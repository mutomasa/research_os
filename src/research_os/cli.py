"""コマンドラインの入口。"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from pydantic import ValidationError

from research_os import __version__
from research_os.data import feedback, intake, interests, papers, profile, venues
from research_os.llm import relevance as llm_relevance
from research_os.sources.openalex import OpenAlexClient, OpenAlexError


def _cmd_venues(args: argparse.Namespace) -> int:
    registry = venues.load_venues(args.registry)
    prof = profile.load_profile(args.profile)
    for v in profile.effective_venues(registry, prof):
        priority = "-" if v.priority is None else str(v.priority)
        print(f"{priority:>2}  {v.fit}  {v.label:<20} {v.type:<10} {v.tier or ''}")
    return 0


def _cmd_interests_init(args: argparse.Namespace) -> int:
    prof = profile.load_profile(args.profile)
    path = interests.write_interests(interests.generate_interests(prof), args.out, force=args.force)
    print(f"wrote {path}")
    return 0


def _load(args: argparse.Namespace):
    registry = venues.load_venues(args.registry)
    prof = profile.load_profile(args.profile)
    prof.check_venues(registry)
    return registry, prof, papers.PaperStore(args.db)


def _score_and_surface(args: argparse.Namespace, registry, prof, store, now: datetime) -> intake.SurfaceReport:
    """段階 1 でスコアを付け、上位を LLM で判定し直してから Inbox に出す（paper_intake.md §4.1）。"""
    intake.rescore(store, registry, prof, now)
    if args.no_llm:
        return intake.surface(store, prof, now)
    report = llm_relevance.judge(store, prof, now)
    if report.calls:
        print(f"llm judged: {report.judged} ({report.calls} calls)")
    if report.judged:
        intake.rescore(store, registry, prof, now)
    if report.error:
        print(f"warning: LLM 判定を中断しました。段階 1 の関連度で続けます: {report.error}", file=sys.stderr)
        return intake.surface(store, prof, now)
    return intake.surface(store, prof, now, judged_only=True)


def _cmd_intake_run(args: argparse.Namespace) -> int:
    registry, prof, store = _load(args)
    now = datetime.now()
    report = intake.fetch(store, OpenAlexClient(), registry, prof, now, force=args.force)
    for rq, n in report.fetched.items():
        print(f"fetched {rq}: {n}")
    if report.skipped_recent:
        print(f"skipped (fetched within {prof.intake.refetch_days} days): {', '.join(report.skipped_recent)}")
    if report.venues_without_source:
        print(f"no OpenAlex source: {', '.join(report.venues_without_source)}")
    result = _score_and_surface(args, registry, prof, store, now)
    if result.blocked_by_backlog:
        print(f"Inbox に未処理が {prof.intake.inbox_backlog_max} 本以上あるため、新しい論文は出しません")
    print(f"surfaced: {len(result.surfaced)} (今週の残り {result.weekly_remaining})")
    return 0


def _cmd_intake_explore(args: argparse.Namespace) -> int:
    registry, prof, store = _load(args)
    now = datetime.now()
    report = intake.explore(store, OpenAlexClient(), registry, prof, now, force=args.force)
    for pid, n in report.explored.items():
        print(f"explored {pid}: {n}")
    if report.skipped_recent:
        print(f"skipped (fetched within {prof.intake.refetch_days} days): {len(report.skipped_recent)}")
    if report.without_openalex_id:
        print(f"no OpenAlex ID: {', '.join(report.without_openalex_id)}")
    if not (report.explored or report.skipped_recent or report.without_openalex_id):
        print("中核論文（core）がまだありません。research-os triage <paper_id> core で指定してください")
    result = _score_and_surface(args, registry, prof, store, now)
    print(f"surfaced: {len(result.surfaced)} (今週の残り {result.weekly_remaining})")
    return 0


def _cmd_intake_suggest(args: argparse.Namespace) -> int:
    registry, prof, store = _load(args)
    suggestions = feedback.suggest(store, registry, prof)
    if not suggestions:
        print(f"提案はありません（同じ理由が {feedback.MIN_EVIDENCE} 本以上たまると提案します）")
    for s in suggestions:
        print(f"[{s.kind}] {s.message}")
    return 0


def _format_reason(parts: dict) -> str:
    source = "（LLM）" if parts.get("relevance_source") == "llm" else ""
    items = [f"{parts.get('primary_rq')} 関連 {parts['relevance']:.2f}{source}"]
    if parts.get("venue_priority"):
        items.append(f"投稿先({parts['venue_priority']})")
    if parts["gap"] > 0:
        items.append(f"手薄 {parts['gap']:.2f}")
    if parts.get("link"):
        items.append(f"中核とつながり {parts['link']:.2f}")
    items.append(f"被引用 {parts['citations_per_year']:g}/年")
    return " · ".join(items)


def _cmd_inbox(args: argparse.Namespace) -> int:
    registry, prof, store = _load(args)
    cfg = prof.intake
    now = datetime.now()
    week = store.surfaced_since(intake.week_start(now))
    core = " ".join(f"{rq.id} core {store.count('core', rq.id)}/{cfg.core_target}" for rq in prof.research_questions)
    print(f"Inbox  今週 {week}/{cfg.inbox_weekly_total} · 未処理 {store.count('inbox')} · "
          f"読む {store.count('to_read')}/{cfg.to_read_max}    {core}")
    labels = {v.venue_id: v.label for v in registry.venues}
    for row in store.papers(args.status):
        venue = labels.get(row["venue_id"], row["venue_name"] or "-")
        print(f"\n{row['score'] or 0:.2f}  {row['title']}  [{venue} {row['year'] or ''}]")
        print(f"      {row['paper_id']}")
        if row["breakdown"]:
            parts = json.loads(row["breakdown"])
            print(f"      {_format_reason(parts)}")
            if parts.get("llm_reason"):
                print(f"      {parts['llm_reason']}")
    return 0


def _cmd_triage(args: argparse.Namespace) -> int:
    _, prof, store = _load(args)
    store.decide(args.paper_id, args.status, datetime.now(), prof.intake.to_read_max, reason=args.reason)
    print(f"{args.paper_id} → {args.status}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="research-os", description="Research OS")
    parser.add_argument("--version", action="version", version=f"research-os {__version__}")
    parser.add_argument("--registry", type=Path, default=venues.DEFAULT_PATH)
    parser.add_argument("--profile", type=Path, default=profile.DEFAULT_PATH)
    parser.add_argument("--db", type=Path, default=papers.DEFAULT_PATH)
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("venues", help="研究プロファイルを適用した Venue 一覧を優先度順に表示")
    p.set_defaults(func=_cmd_venues)

    p = sub.add_parser("interests", help="関心プロファイル interests.yaml の操作")
    isub = p.add_subparsers(dest="interests_command", required=True)
    p = isub.add_parser("init", help="research/profile.yaml から interests.yaml を生成")
    p.add_argument("--out", type=Path, default=interests.DEFAULT_PATH)
    p.add_argument("--force", action="store_true", help="既存ファイルを上書きする")
    p.set_defaults(func=_cmd_interests_init)

    p = sub.add_parser("intake", help="投稿先からの論文取り込み")
    isub = p.add_subparsers(dest="intake_command", required=True)
    p = isub.add_parser("run", help="OpenAlex から取得し、スコアを付けて上限の範囲で Inbox に出す")
    p.add_argument("--force", action="store_true", help="refetch_days 以内でも再取得する")
    p.add_argument("--no-llm", action="store_true", help="LLM（claude -p）による関連度の判定を飛ばす")
    p.set_defaults(func=_cmd_intake_run)
    p = isub.add_parser("explore", help="中核論文の参考文献・被引用を候補に入れ、上限の範囲で Inbox に出す")
    p.add_argument("--force", action="store_true", help="refetch_days 以内でも再取得する")
    p.add_argument("--no-llm", action="store_true", help="LLM（claude -p）による関連度の判定を飛ばす")
    p.set_defaults(func=_cmd_intake_explore)
    p = isub.add_parser("suggest", help="捨てた理由から設定変更を提案する（適用は手で行う）")
    p.set_defaults(func=_cmd_intake_suggest)

    p = sub.add_parser("inbox", help="Inbox（または指定した状態）の論文を表示")
    p.add_argument("--status", default="inbox", choices=papers.STATUSES)
    p.set_defaults(func=_cmd_inbox)

    p = sub.add_parser("triage", help="論文の判断（読む / 読了 / 中核 / 捨てる）")
    p.add_argument("paper_id")
    p.add_argument("status", choices=sorted({s for t in papers.TRANSITIONS.values() for s in t}))
    p.add_argument("--reason", choices=papers.DISMISS_REASONS, help="捨てる理由（dismissed のとき必須）")
    p.set_defaults(func=_cmd_triage)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not hasattr(args, "func"):
        return 0
    try:
        return args.func(args)
    except (ValidationError, ValueError, KeyError, FileExistsError, FileNotFoundError, OpenAlexError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
