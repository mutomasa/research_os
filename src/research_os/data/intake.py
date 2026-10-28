"""論文の取り込み → スコア付け → 上限つきで Inbox に出す。

仕様: docs/new_features/paper_intake.md §2・§4・§5
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from research_os.data import scoring
from research_os.data.papers import PaperStore
from research_os.data.profile import ResearchProfile, effective_venues
from research_os.data.venues import VenueRegistry
from research_os.llm.relevance import profile_hash
from research_os.sources.openalex import OpenAlexClient


@dataclass
class FetchReport:
    fetched: dict[str, int] = field(default_factory=dict)  # rq_id → 取得件数
    skipped_recent: list[str] = field(default_factory=list)  # refetch_days 以内のため取得しなかった RQ
    venues_without_source: list[str] = field(default_factory=list)  # OpenAlex ID が無い survey_venues


@dataclass
class ExploreReport:
    explored: dict[str, int] = field(default_factory=dict)  # 中核論文の paper_id → 取得件数
    skipped_recent: list[str] = field(default_factory=list)
    without_openalex_id: list[str] = field(default_factory=list)


@dataclass
class SurfaceReport:
    surfaced: list[str] = field(default_factory=list)
    blocked_by_backlog: bool = False
    weekly_remaining: int = 0


def week_start(now: datetime) -> datetime:
    monday = now - timedelta(days=now.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def year_from(profile: ResearchProfile, now: datetime) -> int:
    return profile.intake.year_from or now.year - 3


def fetch(store: PaperStore, client: OpenAlexClient, registry: VenueRegistry,
          profile: ResearchProfile, now: datetime, force: bool = False) -> FetchReport:
    """RQ ごとに、survey_venues × survey_topics × 年の範囲で OpenAlex を 1 回ずつ検索する。"""
    report = FetchReport()
    sources = []
    for venue_id in profile.survey_venues:
        source_id = registry.get(venue_id).identifiers.openalex
        if source_id:
            sources.append(source_id)
        else:
            report.venues_without_source.append(venue_id)
    if not sources:
        return report
    venue_by_source = registry.by_openalex_id()
    since = year_from(profile, now)
    for rq in profile.research_questions:
        if not rq.survey_topics:
            continue
        key = f"openalex|{rq.id}|{'|'.join(sorted(sources))}|{since}|{'|'.join(rq.survey_topics)}"
        last = store.last_fetched(key)
        if not force and last and now - last < timedelta(days=profile.intake.refetch_days):
            report.skipped_recent.append(rq.id)
            continue
        records = client.search(rq.survey_topics, sources, since, profile.intake.per_query, venue_by_source)
        for rec in records:
            store.upsert(rec, "openalex", rec.openalex_id, key, now)
        store.log_fetch(key, len(records), now)
        report.fetched[rq.id] = len(records)
    return report


def explore(store: PaperStore, client: OpenAlexClient, registry: VenueRegistry,
            profile: ResearchProfile, now: datetime, force: bool = False) -> ExploreReport:
    """中核論文の参考文献と被引用を候補プールに入れる（paper_intake.md §6）。"""
    report = ExploreReport()
    venue_by_source = registry.by_openalex_id()
    limit = profile.intake.citation_limit
    for row in store.papers("core"):
        pid, oa = row["paper_id"], row["openalex_id"]
        if not oa:
            report.without_openalex_id.append(pid)
            continue
        key = f"citation|{pid}"
        last = store.last_fetched(key)
        if not force and last and now - last < timedelta(days=profile.intake.refetch_days):
            report.skipped_recent.append(pid)
            continue
        records = client.references(oa, limit, venue_by_source) + client.citing(oa, limit, venue_by_source)
        added = 0
        for rec in records:
            if store.find(rec) == pid:
                continue
            store.upsert(rec, "citation", pid, key, now)
            added += 1
        store.log_fetch(key, added, now)
        report.explored[pid] = added
    return report


def rescore(store: PaperStore, registry: VenueRegistry, profile: ResearchProfile, now: datetime) -> int:
    """candidate と inbox の論文のスコアを付け直す（RQ の手薄さは毎回変わるため）。

    LLM 判定（段階 2）があればその関連度を使い、無ければ段階 1（語の一致）を使う。除外語は両方に効かせる。
    """
    venues = {v.venue_id: v for v in effective_venues(registry, profile)}
    core = {rq.id: store.count("core", rq.id) for rq in profile.research_questions}
    h = profile_hash(profile)
    rows = store.papers("candidate") + store.papers("inbox")
    for row in rows:
        judged = store.llm_relevance(row["paper_id"], h)
        if judged:
            text = f"{row['title']} {row['abstract'] or ''}"
            llm, reason = judged
            relevance = {rq.id: 0.0 if scoring.excluded(text, rq.exclude_topics) else llm.get(rq.id, 0.0)
                         for rq in profile.research_questions}
        else:
            relevance = scoring.relevance_by_rq(row["title"], row["abstract"], profile)
        primary = max(relevance, key=relevance.get) if relevance else None
        cpy = scoring.citations_per_year(row["cited_by_count"], row["year"], now.year)
        total, parts = scoring.score(
            relevance.get(primary, 0.0), venues.get(row["venue_id"]), core.get(primary, 0), cpy, profile.intake,
            core_links=store.core_links(row["paper_id"]),
        )
        parts["primary_rq"] = primary
        parts["relevance_source"] = "llm" if judged else "keyword"
        if judged:
            parts["llm_reason"] = reason
        store.set_relevance(row["paper_id"], relevance)
        store.set_score(row["paper_id"], total, parts, primary)
    store.commit()
    return len(rows)


def surface(store: PaperStore, profile: ResearchProfile, now: datetime, judged_only: bool = False) -> SurfaceReport:
    """上限（paper_intake.md §5）の範囲で、スコアの高い candidate を inbox に出す。

    judged_only なら LLM 判定済みの候補だけを出す（未判定の段階 1 の 1.00 が判定済みを追い越さないように）。
    """
    cfg = profile.intake
    report = SurfaceReport()
    if store.count("inbox") >= cfg.inbox_backlog_max:
        report.blocked_by_backlog = True
        return report
    start = week_start(now)
    remaining = cfg.inbox_weekly_total - store.surfaced_since(start)
    per_rq = {}
    for rq in profile.research_questions:
        cap = 1 if store.count("core", rq.id) >= cfg.core_target else cfg.inbox_per_rq
        per_rq[rq.id] = cap - store.surfaced_since(start, rq.id)
    backlog_room = cfg.inbox_backlog_max - store.count("inbox")
    for row in store.papers("candidate"):
        if remaining <= 0 or backlog_room <= 0:
            break
        if row["score"] is None or row["score"] < cfg.min_score:
            break  # スコア順なので以降も下回る
        parts = json.loads(row["breakdown"])
        if parts["relevance"] < cfg.min_relevance:
            continue  # 関連の薄い論文が投稿先・手薄さの加点だけで空き枠を埋めないようにする
        if judged_only and parts.get("relevance_source") != "llm":
            continue
        rq = row["primary_rq"]
        if per_rq.get(rq, 0) <= 0:
            continue
        store.mark_surfaced(row["paper_id"], now)
        report.surfaced.append(row["paper_id"])
        remaining -= 1
        backlog_room -= 1
        per_rq[rq] -= 1
    store.commit()
    report.weekly_remaining = max(0, remaining)
    return report


def format_reason(parts: dict) -> str:
    """スコアの内訳を 1 行で表す（CLI の inbox と TUI の Papers 画面で共有）。"""
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
