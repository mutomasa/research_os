"""Venue レジストリ（registry/venues.yaml）の読み込みと検証。

仕様: docs/new_features/venue_strategy.md §3 / ADR-0001
"""

from datetime import date
from pathlib import Path
from typing import Literal

import yaml
from pydantic import model_validator

from research_os.data.base import StrictModel

Fit = Literal["◎", "○", "△"]
Tier = Literal["first_result", "foundational", "mature_journal"]
VenueType = Literal["journal", "conference", "magazine"]

DEFAULT_PATH = Path("registry/venues.yaml")


class Links(StrictModel):
    official: str | None = None
    cfp: str | None = None
    author_guide: str | None = None


class Identifiers(StrictModel):
    issn: list[str] = []
    openalex: str | None = None  # OpenAlex source ID（例: S4210169774）
    dblp: str | None = None


class Policies(StrictModel):
    co_presents_with: list[str] = []
    notes: list[str] = []
    verified: bool = False


class Deadline(StrictModel):
    year: int
    kind: str  # 例: paper_submission / ral_with_conference_option
    due: date
    source_url: str
    retrieved_at: date
    verified: bool = False


class Venue(StrictModel):
    venue_id: str
    name: str
    abbrev: str | None
    type: VenueType
    publisher: str
    ieee_related: bool
    scope: list[str]
    fit: Fit
    priority: int | None
    tier: Tier | None
    links: Links
    identifiers: Identifiers = Identifiers()
    policies: Policies
    deadlines: list[Deadline] = []
    source_url: str
    retrieved_at: date
    updated_at: date

    @property
    def label(self) -> str:
        """一覧表示用の短い名前（略称がなければ正式名称）。"""
        return self.abbrev or self.name


class VenueRegistry(StrictModel):
    schema_version: Literal[1]
    venues: list[Venue]

    @model_validator(mode="after")
    def _check_ids(self) -> "VenueRegistry":
        ids = [v.venue_id for v in self.venues]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(f"venue_id が重複しています: {duplicates}")
        known = set(ids)
        for v in self.venues:
            unknown = [c for c in v.policies.co_presents_with if c not in known]
            if unknown:
                raise ValueError(f"{v.venue_id}.policies.co_presents_with に未登録の venue_id: {unknown}")
        return self

    def ids(self) -> set[str]:
        return {v.venue_id for v in self.venues}

    def by_openalex_id(self) -> dict[str, str]:
        """OpenAlex source ID → venue_id。"""
        return {v.identifiers.openalex: v.venue_id for v in self.venues if v.identifiers.openalex}

    def get(self, venue_id: str) -> Venue:
        for v in self.venues:
            if v.venue_id == venue_id:
                return v
        raise KeyError(venue_id)


def load_venues(path: Path = DEFAULT_PATH) -> VenueRegistry:
    with Path(path).open(encoding="utf-8") as f:
        return VenueRegistry.model_validate(yaml.safe_load(f))
