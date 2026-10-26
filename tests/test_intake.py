from datetime import datetime, timedelta

import pytest

from research_os.data import intake
from research_os.data.papers import PaperRecord, PaperStore
from research_os.data.profile import load_profile
from research_os.data.venues import load_venues

NOW = datetime(2026, 10, 21, 9, 0)  # 水曜

TITLES = {
    "RQ1": "Vision tactile learning and tactile sensing for slip detection",
    "RQ2": "JEPA world models for failure prediction with latent dynamics",
    "RQ3": "Failure-aware manipulation with failure recovery and replanning",
}

# research/profile.yaml の各 RQ の survey_topics の先頭
FIRST_KEYWORD = {"Vision-Tactile Learning": "RQ1", "JEPA": "RQ2", "Failure-Aware Manipulation": "RQ3"}


class FakeClient:
    def __init__(self, per_rq: int = 8):
        self.calls = []
        self.per_rq = per_rq

    def search(self, keywords, source_ids, year_from, per_page, venue_by_source):
        self.calls.append((tuple(keywords), tuple(source_ids), year_from))
        rq = FIRST_KEYWORD[keywords[0]]
        return [
            PaperRecord(title=f"{TITLES[rq]} {i}", doi=f"10.1/{rq}-{i}", year=2025,
                        venue_id="ral", cited_by_count=20)
            for i in range(self.per_rq)
        ]


@pytest.fixture
def ctx(root):
    store = PaperStore(":memory:")
    yield store, load_venues(root / "registry/venues.yaml"), load_profile(root / "research/profile.yaml")
    store.close()


def _run(store, registry, profile, now=NOW, client=None):
    client = client or FakeClient()
    intake.fetch(store, client, registry, profile, now)
    intake.rescore(store, registry, profile, now)
    return intake.surface(store, profile, now)


def test_fetch_one_request_per_rq_and_reports_missing_sources(ctx):
    store, registry, profile = ctx
    client = FakeClient()
    report = intake.fetch(store, client, registry, profile, NOW)
    assert len(client.calls) == 3
    assert report.venues_without_source == ["rss"]
    assert client.calls[0][2] == 2023  # 直近 4 年


def test_refetch_is_skipped_within_refetch_days(ctx):
    store, registry, profile = ctx
    intake.fetch(store, FakeClient(), registry, profile, NOW)
    client = FakeClient()
    report = intake.fetch(store, client, registry, profile, NOW + timedelta(days=2))
    assert client.calls == [] and len(report.skipped_recent) == 3


def test_weekly_total_and_per_rq_caps(ctx):
    store, registry, profile = ctx
    report = _run(store, registry, profile)  # 3 RQ × 8 本の候補
    assert len(report.surfaced) == 10
    per_rq = {rq: store.count("inbox", rq) for rq in TITLES}
    assert max(per_rq.values()) <= 4
    assert store.count("candidate") == 14  # 残りは非表示のまま


def test_nothing_more_this_week_after_cap(ctx):
    store, registry, profile = ctx
    _run(store, registry, profile)
    for row in store.papers("inbox"):
        store.decide(row["paper_id"], "dismissed", NOW, 5, reason="irrelevant")
    report = intake.surface(store, profile, NOW + timedelta(days=1))
    assert report.surfaced == []
    report = intake.surface(store, profile, NOW + timedelta(days=7))  # 翌週
    assert len(report.surfaced) > 0


def test_backlog_blocks_new_papers(ctx):
    store, registry, profile = ctx
    _run(store, registry, profile)  # 未処理 10
    report = intake.surface(store, profile, NOW + timedelta(days=7))
    assert report.blocked_by_backlog and report.surfaced == []


def test_min_score_leaves_slots_empty(ctx):
    store, registry, profile = ctx
    store.upsert(PaperRecord(title="Protein folding with transformers", doi="10.1/x"), "openalex", None, None, NOW)
    intake.rescore(store, registry, profile, NOW)
    assert intake.surface(store, profile, NOW).surfaced == []


def test_saturated_rq_is_throttled(ctx):
    store, registry, profile = ctx
    profile.intake.core_target = 1
    pid = store.upsert(PaperRecord(title=TITLES["RQ2"] + " core", doi="10.1/core"), "openalex", None, None, NOW)
    store.db.execute("UPDATE triage SET status = 'core', primary_rq = 'RQ2' WHERE paper_id = ?", (pid,))
    _run(store, registry, profile)
    assert store.count("inbox", "RQ2") == 1


def test_breakdown_is_saved(ctx):
    store, registry, profile = ctx
    _run(store, registry, profile)
    import json
    parts = json.loads(store.papers("inbox")[0]["breakdown"])
    assert parts["venue_priority"] == 1 and parts["primary_rq"] in TITLES
