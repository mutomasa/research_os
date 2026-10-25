"""捨てた理由の集計と、設定変更の提案（paper_intake.md §7）。

提案するだけで、research/profile.yaml の変更は人が行う。
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from statistics import median

from research_os.data.papers import PaperStore
from research_os.data.profile import ResearchProfile, effective_venues
from research_os.data.scoring import tokens
from research_os.data.venues import VenueRegistry

MIN_EVIDENCE = 3  # 同じ理由がこの本数以上たまったら提案する
GENERIC_RATIO = 0.10  # 捨てた論文以外の題名のこの割合を超えて出る語（learning など）は除外語にしない


@dataclass
class Suggestion:
    kind: str  # exclude_topics / year_from / venue_priority
    target: str  # RQ id または venue_id
    message: str
    evidence: list[str]  # 根拠になった paper_id


def suggest(store: PaperStore, registry: VenueRegistry, profile: ResearchProfile) -> list[Suggestion]:
    by_reason: dict[tuple[str, str | None], list] = defaultdict(list)
    for row in store.dismissed():
        by_reason[(row["dismiss_reason"], row["primary_rq"])].append(row)
    out: list[Suggestion] = []
    out += _exclude_terms(by_reason, store, profile)
    out += _year_from(by_reason, profile)
    out += _venue_priority(store, registry, profile)
    return out


def _exclude_terms(by_reason, store: PaperStore, profile: ResearchProfile) -> list[Suggestion]:
    library = [tokens(r["title"]) for status in ("to_read", "read", "core") for r in store.papers(status)]
    out = []
    for rq in profile.research_questions:
        rows = by_reason.get(("irrelevant", rq.id), [])
        if len(rows) < MIN_EVIDENCE:
            continue
        dismissed_ids = {r["paper_id"] for r in rows}
        others = [tokens(r["title"]) for r in store.papers() if r["paper_id"] not in dismissed_ids]
        df = Counter(w for t in others for w in t)
        generic = {w for w, n in df.items() if n > GENERIC_RATIO * len(others)}
        own = set().union(*(tokens(t) for t in rq.survey_topics)) if rq.survey_topics else set()
        counts = Counter(w for r in rows for w in tokens(r["title"]))
        terms = [
            w for w, n in counts.most_common()
            if n >= max(2, len(rows) // 2) and w not in own and w not in generic
            and sum(w in t for t in library) == 0
        ][:5]
        if terms:
            out.append(Suggestion(
                "exclude_topics", rq.id,
                f"{rq.id} で「関係ない」と捨てた {len(rows)} 本の題名に多い語：{', '.join(terms)}。"
                f"research/profile.yaml の {rq.id}.exclude_topics への追加を検討してください",
                [r["paper_id"] for r in rows],
            ))
    return out


def _year_from(by_reason, profile: ResearchProfile) -> list[Suggestion]:
    out = []
    for rq in profile.research_questions:
        rows = [r for r in by_reason.get(("outdated", rq.id), []) if r["year"]]
        if len(rows) < MIN_EVIDENCE:
            continue
        proposed = int(median(r["year"] for r in rows)) + 1
        current = profile.intake.year_from
        if current is None or proposed > current:
            out.append(Suggestion(
                "year_from", rq.id,
                f"{rq.id} で「古い」と捨てた論文が {len(rows)} 本（出版年の中央値 {proposed - 1}）。"
                f"intake.year_from を {proposed} に上げることを検討してください",
                [r["paper_id"] for r in rows],
            ))
    return out


def _venue_priority(store: PaperStore, registry: VenueRegistry, profile: ResearchProfile) -> list[Suggestion]:
    venues = {v.venue_id: v for v in effective_venues(registry, profile)}
    by_venue: dict[str, list] = defaultdict(list)
    for row in store.dismissed():
        if row["dismiss_reason"] == "low_quality" and row["venue_id"]:
            by_venue[row["venue_id"]].append(row)
    out = []
    for venue_id, rows in by_venue.items():
        if len(rows) < MIN_EVIDENCE or venue_id not in venues:
            continue
        v = venues[venue_id]
        now = "なし" if v.priority is None else str(v.priority)
        out.append(Suggestion(
            "venue_priority", venue_id,
            f"{v.label} の論文を「質が低い」と {len(rows)} 本捨てています。"
            f"venue_overrides で priority（現在 {now}）を下げることを検討してください",
            [r["paper_id"] for r in rows],
        ))
    return out
