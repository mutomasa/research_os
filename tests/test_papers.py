from datetime import datetime

import pytest

from research_os.data.papers import (
    InvalidTransition,
    LimitReached,
    PaperRecord,
    PaperStore,
    normalize_title,
)

NOW = datetime(2026, 10, 25, 9, 0)


@pytest.fixture
def store():
    s = PaperStore(":memory:")
    yield s
    s.close()


def test_normalize_title():
    assert normalize_title("  Vision–Tactile JEPA: A World-Model! ") == "vision tactile jepa a world model"


def test_new_paper_starts_as_hidden_candidate(store):
    pid = store.upsert(PaperRecord(title="A", doi="10.1/a"), "openalex", "W1", "q", NOW)
    assert pid == "doi:10.1/a"
    assert store.status(pid) == "candidate"


def test_preprint_and_published_version_merge(store):
    pre = store.upsert(PaperRecord(title="Tactile World Models", arxiv_id="2501.00001"), "alphaxiv", None, None, NOW)
    pub = store.upsert(
        PaperRecord(title="Tactile World-Models", doi="10.1/b", venue_id="ral", cited_by_count=7),
        "openalex", "W2", "q", NOW,
    )
    assert pre == pub
    row = store.papers()[0]
    assert (row["doi"], row["venue_id"], row["cited_by_count"]) == ("10.1/b", "ral", 7)
    assert len(store.papers()) == 1


def test_human_cannot_skip_inbox(store):
    pid = store.upsert(PaperRecord(title="A", doi="10.1/a"), "openalex", None, None, NOW)
    with pytest.raises(InvalidTransition):
        store.decide(pid, "to_read", NOW, to_read_max=5)


def test_dismiss_requires_reason(store):
    pid = store.upsert(PaperRecord(title="A", doi="10.1/a"), "openalex", None, None, NOW)
    store.mark_surfaced(pid, NOW)
    with pytest.raises(ValueError, match="理由"):
        store.decide(pid, "dismissed", NOW, to_read_max=5)
    store.decide(pid, "dismissed", NOW, to_read_max=5, reason="irrelevant")
    assert store.status(pid) == "dismissed"


def test_to_read_limit(store):
    ids = []
    for i in range(3):
        pid = store.upsert(PaperRecord(title=f"P{i}", doi=f"10.1/{i}"), "openalex", None, None, NOW)
        store.mark_surfaced(pid, NOW)
        ids.append(pid)
    store.decide(ids[0], "to_read", NOW, to_read_max=2)
    store.decide(ids[1], "to_read", NOW, to_read_max=2)
    with pytest.raises(LimitReached):
        store.decide(ids[2], "to_read", NOW, to_read_max=2)
    store.decide(ids[0], "read", NOW, to_read_max=2)
    store.decide(ids[2], "to_read", NOW, to_read_max=2)
