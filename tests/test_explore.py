import json
from datetime import datetime, timedelta

import pytest

from research_os.data import intake, scoring
from research_os.data.papers import PaperRecord, PaperStore
from research_os.data.profile import load_profile
from research_os.data.venues import load_venues
from research_os.sources import openalex

NOW = datetime(2026, 10, 21, 9, 0)


class FakeCitationClient:
    def __init__(self):
        self.calls = []

    def references(self, oa, limit, venue_by_source):
        self.calls.append(("refs", oa, limit))
        return [PaperRecord(title="JEPA world model failure prediction latent dynamics", doi="10.1/ref", year=2024),
                PaperRecord(title="Core paper itself", openalex_id="W1")]

    def citing(self, oa, limit, venue_by_source):
        self.calls.append(("cites", oa, limit))
        return [PaperRecord(title="Citing tactile slip detection", doi="10.1/cite", year=2025)]


@pytest.fixture
def ctx(root):
    store = PaperStore(":memory:")
    registry = load_venues(root / "registry/venues.yaml")
    profile = load_profile(root / "research/profile.yaml")
    core = store.upsert(PaperRecord(title="Core paper itself", openalex_id="W1", doi="10.1/core"),
                        "openalex", None, None, NOW)
    store.db.execute("UPDATE triage SET status = 'core' WHERE paper_id = ?", (core,))
    store.commit()
    yield store, registry, profile, core
    store.close()


def test_explore_adds_refs_and_citing_but_not_core_itself(ctx):
    store, registry, profile, core = ctx
    client = FakeCitationClient()
    report = intake.explore(store, client, registry, profile, NOW)
    assert report.explored == {core: 2}
    assert ("refs", "W1", 50) in client.calls
    assert store.status("doi:10.1/ref") == "candidate"
    assert store.core_links("doi:10.1/ref") == 1


def test_explore_skips_recent_and_reports_missing_ids(ctx):
    store, registry, profile, core = ctx
    intake.explore(store, FakeCitationClient(), registry, profile, NOW)
    other = store.upsert(PaperRecord(title="No OpenAlex", doi="10.1/x"), "alphaxiv", None, None, NOW)
    store.db.execute("UPDATE triage SET status = 'core' WHERE paper_id = ?", (other,))
    client = FakeCitationClient()
    report = intake.explore(store, client, registry, profile, NOW + timedelta(days=1))
    assert client.calls == []
    assert report.skipped_recent == [core] and report.without_openalex_id == [other]


def test_link_is_in_breakdown(ctx):
    store, registry, profile, core = ctx
    intake.explore(store, FakeCitationClient(), registry, profile, NOW)
    intake.rescore(store, registry, profile, NOW)
    row = next(r for r in store.papers("candidate") if r["paper_id"] == "doi:10.1/ref")
    assert json.loads(row["breakdown"])["link"] == pytest.approx(1 / 3, abs=1e-3)


def test_exclude_topics_zero_the_rq(root):
    profile = load_profile(root / "research/profile.yaml")
    profile.research_questions[1].exclude_topics = ["surgical"]
    rel = scoring.relevance_by_rq("Surgical world model for failure prediction", None, profile)
    assert rel["RQ2"] == 0.0


def test_dismiss_as_known_goes_to_library(ctx):
    store, *_ = ctx
    pid = store.upsert(PaperRecord(title="Known", doi="10.1/k"), "openalex", None, None, NOW)
    store.mark_surfaced(pid, NOW)
    store.decide(pid, "dismissed", NOW, 5, reason="known")
    assert store.status(pid) == "read"
    assert [r["dismiss_reason"] for r in store.dismissed()] == ["known"]


def test_citing_url():
    seen = []
    client = openalex.OpenAlexClient(get=lambda url: seen.append(url) or {"results": []})
    client.citing("W1", 20, {})
    assert "cites%3AW1" in seen[0] and "cited_by_count%3Adesc" in seen[0]


def test_references_fetches_work_then_ids():
    pages = [{"referenced_works": ["https://openalex.org/W2", "https://openalex.org/W3"]}, {"results": []}]
    seen = []
    client = openalex.OpenAlexClient(get=lambda url: seen.append(url) or pages.pop(0))
    client.references("W1", 1, {})
    assert "/works/W1" in seen[0] and "openalex%3AW2" in seen[1] and "W3" not in seen[1]
