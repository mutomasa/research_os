import pytest

from research_os.data import scoring
from research_os.data.profile import IntakeConfig, effective_venues, load_profile
from research_os.data.venues import load_venues


@pytest.fixture
def profile(root):
    return load_profile(root / "research/profile.yaml")


@pytest.fixture
def venues(root, profile):
    return {v.venue_id: v for v in effective_venues(load_venues(root / "registry/venues.yaml"), profile)}


def test_tokens_handle_hyphen_and_plural():
    assert scoring.tokens("Vision-Tactile World Models") == {"vision", "tactile", "world", "model"}


def test_relevance_picks_matching_rq(profile):
    rel = scoring.relevance_by_rq(
        "JEPA world models for failure prediction", "We learn latent dynamics.", profile
    )
    assert max(rel, key=rel.get) == "RQ2"
    assert rel["RQ2"] == 1.0


def test_unrelated_paper_scores_low(profile):
    rel = scoring.relevance_by_rq("Protein folding with transformers", None, profile)
    assert max(rel.values()) < 0.3


def test_venue_weight_follows_priority(venues):
    assert scoring.venue_weight(venues["ral"]) == 1.0
    assert scoring.venue_weight(venues["tro"]) == pytest.approx(0.2)
    assert scoring.venue_weight(venues["jfr"]) == 0.1  # 登録済みで priority なし
    assert scoring.venue_weight(None) == 0.0


def test_velocity_uses_per_year_not_total():
    old = scoring.citations_per_year(100, 2016, 2026)  # 11 年で 100
    new = scoring.citations_per_year(30, 2025, 2026)   # 2 年で 30
    assert new > old


def test_gap_shrinks_as_core_fills():
    cfg = IntakeConfig()
    assert scoring.gap(0, cfg) == 1.0
    assert scoring.gap(15, cfg) == 0.0


def test_score_breakdown_and_weights(venues):
    total, parts = scoring.score(1.0, venues["ral"], 0, 50, IntakeConfig())
    assert total == pytest.approx(1.0)
    assert parts["venue_priority"] == 1
    assert set(parts) >= {"relevance", "venue", "gap", "velocity", "citations_per_year"}
