from datetime import datetime
from itertools import count

import pytest

from research_os.data import feedback
from research_os.data.papers import PaperRecord, PaperStore
from research_os.data.profile import load_profile
from research_os.data.venues import load_venues

NOW = datetime(2026, 10, 21)
_ids = count()


@pytest.fixture
def ctx(root):
    store = PaperStore(":memory:")
    yield store, load_venues(root / "registry/venues.yaml"), load_profile(root / "research/profile.yaml")
    store.close()


def _dismiss(store, title, reason, rq="RQ2", year=2025, venue_id=None):
    pid = store.upsert(PaperRecord(title=title, doi=f"10.1/{next(_ids)}", year=year, venue_id=venue_id),
                       "openalex", None, None, NOW)
    store.db.execute("UPDATE triage SET primary_rq = ? WHERE paper_id = ?", (rq, pid))
    store.mark_surfaced(pid, NOW)
    store.decide(pid, "dismissed", NOW, 5, reason=reason)
    return pid


def test_no_suggestion_below_threshold(ctx):
    store, registry, profile = ctx
    _dismiss(store, "Surgical robot world model", "irrelevant")
    _dismiss(store, "Surgical policy evaluation", "irrelevant")
    assert feedback.suggest(store, registry, profile) == []


def test_exclude_terms_from_irrelevant(ctx):
    store, registry, profile = ctx
    for t in ["Surgical robot world model", "Surgical policy evaluation", "LiDAR surgical simulation"]:
        _dismiss(store, t, "irrelevant")
    [s] = feedback.suggest(store, registry, profile)
    assert s.kind == "exclude_topics" and s.target == "RQ2"
    assert "surgical" in s.message
    assert "world" not in s.message.split("：")[1].split("。")[0]  # RQ 自身の語は提案しない


def test_year_from_from_outdated(ctx):
    store, registry, profile = ctx
    for y in (2018, 2019, 2020):
        _dismiss(store, f"Old paper {y}", "outdated", year=y)
    [s] = feedback.suggest(store, registry, profile)
    assert s.kind == "year_from" and "2020" in s.message


def test_venue_priority_from_low_quality(ctx):
    store, registry, profile = ctx
    for k in range(3):
        _dismiss(store, f"Weak result {k}", "low_quality", venue_id="ral")
    [s] = feedback.suggest(store, registry, profile)
    assert s.kind == "venue_priority" and s.target == "ral" and "現在 1" in s.message


def test_generic_words_are_not_suggested(ctx):
    store, registry, profile = ctx
    for k in range(20):
        store.upsert(PaperRecord(title=f"Learning manipulation {k}", doi=f"10.2/{k}"), "openalex", None, None, NOW)
    for t in ["Surgical learning A", "Surgical learning B", "Surgical learning C"]:
        _dismiss(store, t, "irrelevant")
    [s] = feedback.suggest(store, registry, profile)
    assert "surgical" in s.message and "learning" not in s.message
