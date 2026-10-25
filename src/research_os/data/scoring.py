"""論文のスコア（段階 1：語の一致）。

仕様: docs/new_features/paper_intake.md §4
score = w.relevance × relevance + w.venue × venue + w.gap × gap + w.velocity × velocity
"""

import math
import re

from research_os.data.profile import IntakeConfig, ResearchProfile
from research_os.data.venues import Venue

STOPWORDS = {"a", "an", "and", "for", "in", "of", "on", "the", "to", "with", "via", "using", "based"}
VELOCITY_CAP = 50  # 年あたり被引用がこの値で velocity = 1


def tokens(text: str) -> set[str]:
    words = re.findall(r"[0-9a-z]+", text.lower())
    # 複数形の s だけ落とす簡易な正規化（"models" と "model" を同一視する）
    return {w[:-1] if len(w) > 3 and w.endswith("s") else w for w in words if w not in STOPWORDS and len(w) > 1}


def rq_relevance(text: str, survey_topics: list[str]) -> float:
    """RQ の survey_topics の各語句が本文にどれだけ含まれるか。上位 2 語句の被覆率の平均（0〜1）。"""
    if not survey_topics:
        return 0.0
    body = tokens(text)
    covers = sorted(
        (len(t & body) / len(t) for t in (tokens(topic) for topic in survey_topics) if t),
        reverse=True,
    )
    top = covers[:2]
    return sum(top) / len(top) if top else 0.0


def relevance_by_rq(title: str, abstract: str | None, profile: ResearchProfile) -> dict[str, float]:
    text = f"{title} {abstract or ''}"
    return {rq.id: round(rq_relevance(text, rq.survey_topics), 3) for rq in profile.research_questions}


def venue_weight(venue: Venue | None) -> float:
    if venue is None:
        return 0.0
    if venue.priority is None:
        return 0.1
    return max(0.0, (6 - venue.priority) / 5)


def citations_per_year(cited_by_count: int, year: int | None, current_year: int) -> float:
    if not year:
        return 0.0
    return cited_by_count / max(1, current_year - year + 1)


def velocity(cpy: float) -> float:
    return min(1.0, math.log1p(cpy) / math.log1p(VELOCITY_CAP))


def gap(core_count: int, config: IntakeConfig) -> float:
    return max(0.0, 1 - core_count / config.core_target)


def score(relevance: float, venue: Venue | None, core_count: int, cpy: float,
          config: IntakeConfig) -> tuple[float, dict]:
    """スコアと内訳を返す。内訳は Inbox で「なぜこの論文か」を示すために保存する。"""
    w = config.weights
    parts = {
        "relevance": round(relevance, 3),
        "venue": round(venue_weight(venue), 3),
        "gap": round(gap(core_count, config), 3),
        "velocity": round(velocity(cpy), 3),
    }
    total = (w.relevance * parts["relevance"] + w.venue * parts["venue"]
             + w.gap * parts["gap"] + w.velocity * parts["velocity"])
    parts["citations_per_year"] = round(cpy, 1)
    parts["venue_priority"] = venue.priority if venue else None
    return round(total, 3), parts
