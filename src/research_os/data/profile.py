"""研究プロファイル（research/profile.yaml）の読み込みと、Venue 既定値への上書き。

仕様: docs/new_features/venue_strategy.md §4
"""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import model_validator

from research_os.data.base import StrictModel
from research_os.data.venues import Fit, Tier, Venue, VenueRegistry

DEFAULT_PATH = Path("research/profile.yaml")


class ResearchQuestion(StrictModel):
    id: str
    title: str
    question: str
    verification: list[str] = []
    survey_topics: list[str] = []


class VenueOverride(StrictModel):
    fit: Fit | None = None
    priority: int | None = None
    tier: Tier | None = None


class SubmissionStep(StrictModel):
    step: int
    title: str
    goal: str | None = None
    research_questions: list[str] = []
    candidate_venues: list[str] = []
    contributions: list[str] = []
    note: str | None = None


class IntakeWeights(StrictModel):
    relevance: float = 0.50
    venue: float = 0.20
    gap: float = 0.15
    velocity: float = 0.15


class IntakeConfig(StrictModel):
    """論文取り込みと Inbox の上限（docs/new_features/paper_intake.md §5）。"""

    inbox_weekly_total: int = 10
    inbox_per_rq: int = 4
    inbox_backlog_max: int = 10
    to_read_max: int = 5
    core_target: int = 15
    min_score: float = 0.30
    year_from: int | None = None  # None なら直近 4 年
    per_query: int = 50
    refetch_days: int = 6
    weights: IntakeWeights = IntakeWeights()


class ResearchProfile(StrictModel):
    schema_version: Literal[1]
    theme: str
    theme_ja: str
    research_questions: list[ResearchQuestion]
    survey_topics: list[str] = []
    venue_overrides: dict[str, VenueOverride] = {}
    survey_venues: list[str] = []
    submission_plan: list[SubmissionStep] = []
    intake: IntakeConfig = IntakeConfig()

    @model_validator(mode="after")
    def _check_rq_refs(self) -> "ResearchProfile":
        ids = [rq.id for rq in self.research_questions]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(f"research_questions の id が重複しています: {duplicates}")
        for s in self.submission_plan:
            unknown = [r for r in s.research_questions if r not in ids]
            if unknown:
                raise ValueError(f"submission_plan step {s.step} に未定義の RQ: {unknown}")
        return self

    def referenced_venue_ids(self) -> set[str]:
        refs = set(self.venue_overrides) | set(self.survey_venues)
        for s in self.submission_plan:
            refs |= set(s.candidate_venues)
        return refs

    def check_venues(self, registry: VenueRegistry) -> None:
        """プロファイルが参照する venue_id がすべてレジストリにあるか確認する。"""
        unknown = sorted(self.referenced_venue_ids() - registry.ids())
        if unknown:
            raise ValueError(f"profile が registry/venues.yaml に無い venue_id を参照しています: {unknown}")


def load_profile(path: Path = DEFAULT_PATH) -> ResearchProfile:
    with Path(path).open(encoding="utf-8") as f:
        return ResearchProfile.model_validate(yaml.safe_load(f))


def effective_venues(registry: VenueRegistry, profile: ResearchProfile) -> list[Venue]:
    """venue_overrides を適用した Venue 一覧を、priority 順（未設定は後ろ）で返す。"""
    profile.check_venues(registry)
    venues = []
    for v in registry.venues:
        override = profile.venue_overrides.get(v.venue_id)
        if override:
            v = v.model_copy(update=override.model_dump(exclude_none=True))
        venues.append(v)
    return sorted(venues, key=lambda v: (v.priority is None, v.priority or 0))
