"""OpenAlex の works 検索（ADR-0003）。

キーなしでは同じ IP の利用全体で 1 日の無料枠を共有するため、OPENALEX_API_KEY があれば付ける。
OPENALEX_MAILTO は連絡先として付ける（枠は増えない）。
"""

import json
import os
import re
import urllib.parse
import urllib.request
from collections.abc import Callable

from research_os.data.papers import PaperRecord

BASE_URL = "https://api.openalex.org/works"
SELECT = "id,doi,title,publication_year,cited_by_count,primary_location,locations,authorships,abstract_inverted_index"
ARXIV_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})")

HttpGet = Callable[[str], dict]


def _urllib_get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "research-os"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def search_query(keywords: list[str]) -> str:
    return " OR ".join(f"({k})" for k in keywords)


def build_url(keywords: list[str], source_ids: list[str], year_from: int, per_page: int) -> str:
    params = {
        "filter": f"primary_location.source.id:{'|'.join(source_ids)},publication_year:>{year_from - 1}",
        "search": search_query(keywords),
        "select": SELECT,
        "per-page": str(per_page),
    }
    if key := os.environ.get("OPENALEX_API_KEY"):
        params["api_key"] = key
    if mailto := os.environ.get("OPENALEX_MAILTO"):
        params["mailto"] = mailto
    return f"{BASE_URL}?{urllib.parse.urlencode(params)}"


def abstract_from_index(index: dict[str, list[int]] | None) -> str | None:
    if not index:
        return None
    words = sorted((pos, word) for word, positions in index.items() for pos in positions)
    return " ".join(w for _, w in words)


def _short_id(url: str | None) -> str | None:
    return url.rsplit("/", 1)[-1] if url else None


def parse_work(work: dict, venue_by_source: dict[str, str]) -> PaperRecord:
    source = (work.get("primary_location") or {}).get("source") or {}
    source_id = _short_id(source.get("id"))
    doi = work.get("doi")
    arxiv_id = None
    for loc in work.get("locations") or []:
        if m := ARXIV_RE.search(loc.get("landing_page_url") or ""):
            arxiv_id = m.group(1)
            break
    return PaperRecord(
        title=work.get("title") or "",
        doi=doi.removeprefix("https://doi.org/").lower() if doi else None,
        arxiv_id=arxiv_id,
        openalex_id=_short_id(work.get("id")),
        abstract=abstract_from_index(work.get("abstract_inverted_index")),
        year=work.get("publication_year"),
        authors=[a["author"]["display_name"] for a in work.get("authorships") or [] if a.get("author")],
        venue_id=venue_by_source.get(source_id or ""),
        venue_name=source.get("display_name"),
        cited_by_count=work.get("cited_by_count") or 0,
    )


class OpenAlexClient:
    def __init__(self, get: HttpGet = _urllib_get):
        self.get = get

    def search(self, keywords: list[str], source_ids: list[str], year_from: int,
               per_page: int, venue_by_source: dict[str, str]) -> list[PaperRecord]:
        data = self.get(build_url(keywords, source_ids, year_from, per_page))
        return [parse_work(w, venue_by_source) for w in data.get("results", []) if w.get("title")]
