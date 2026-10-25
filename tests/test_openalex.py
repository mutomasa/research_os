import urllib.parse

from research_os.sources import openalex

WORK = {
    "id": "https://openalex.org/W123",
    "doi": "https://doi.org/10.1109/LRA.2025.ABC",
    "title": "TactileAloha: Learning Bimanual Manipulation With Tactile Sensing",
    "publication_year": 2025,
    "cited_by_count": 14,
    "primary_location": {"source": {"id": "https://openalex.org/S4210169774",
                                    "display_name": "IEEE Robotics and Automation Letters"}},
    "locations": [{"landing_page_url": "https://arxiv.org/abs/2503.01234"}],
    "authorships": [{"author": {"display_name": "Ningquan Gu"}}],
    "abstract_inverted_index": {"We": [0], "learn": [1], "tactile": [2], "policies": [3]},
}


def test_parse_work():
    rec = openalex.parse_work(WORK, {"S4210169774": "ral"})
    assert rec.doi == "10.1109/lra.2025.abc"
    assert rec.arxiv_id == "2503.01234"
    assert rec.openalex_id == "W123"
    assert rec.venue_id == "ral"
    assert rec.abstract == "We learn tactile policies"
    assert rec.authors == ["Ningquan Gu"]


def test_unknown_source_has_no_venue_id():
    assert openalex.parse_work(WORK, {}).venue_id is None


def test_build_url_combines_venues_and_keywords(monkeypatch):
    monkeypatch.delenv("OPENALEX_API_KEY", raising=False)
    monkeypatch.setenv("OPENALEX_MAILTO", "me@example.com")
    url = openalex.build_url(["Tactile Sensing", "Slip Detection"], ["S1", "S2"], 2023, 50)
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    assert q["filter"] == ["primary_location.source.id:S1|S2,publication_year:>2022"]
    assert q["search"] == ["(Tactile Sensing) OR (Slip Detection)"]
    assert q["mailto"] == ["me@example.com"]
    assert "api_key" not in q


def test_api_key_is_sent_when_set(monkeypatch):
    monkeypatch.setenv("OPENALEX_API_KEY", "k")
    url = openalex.build_url(["x"], ["S1"], 2023, 10)
    assert "api_key=k" in url


def test_client_uses_injected_get():
    seen = []
    client = openalex.OpenAlexClient(get=lambda url: seen.append(url) or {"results": [WORK, {"title": None}]})
    recs = client.search(["x"], ["S4210169774"], 2023, 10, {"S4210169774": "ral"})
    assert len(recs) == 1 and len(seen) == 1
