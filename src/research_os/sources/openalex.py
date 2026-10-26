"""OpenAlex の works 検索（ADR-0003）。

キーなしでは同じ IP の利用全体で 1 日の無料枠を共有するため、OPENALEX_API_KEY があれば付ける。
OPENALEX_MAILTO は連絡先として付ける（枠は増えない）。
"""

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable

from research_os.data.papers import PaperRecord

BASE_URL = "https://api.openalex.org/works"
SELECT = "id,doi,title,publication_year,cited_by_count,primary_location,locations,authorships,abstract_inverted_index"
ARXIV_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})")

HttpGet = Callable[[str], dict]


class OpenAlexError(RuntimeError):
    pass


def _urllib_get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "research-os"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            # キーなしの無料枠（IP 全体で 1 日分）を使い切った。取得済みの分は保存されている（#11）
            raise OpenAlexError("OpenAlex の 1 日の無料枠を使い切りました。翌日に再実行してください") from e
        raise OpenAlexError(f"OpenAlex が HTTP {e.code} を返しました") from e
    except urllib.error.URLError as e:
        raise OpenAlexError(f"OpenAlex に接続できません: {e.reason}") from e


def search_query(keywords: list[str]) -> str:
    return " OR ".join(f"({k})" for k in keywords)


def build_url(keywords: list[str], source_ids: list[str], year_from: int, per_page: int) -> str:
    params = {
        "filter": f"primary_location.source.id:{'|'.join(source_ids)},publication_year:>{year_from - 1}",
        "search": search_query(keywords),
        "select": SELECT,
        "per-page": str(per_page),
    }
    return _url(BASE_URL, params)


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


def _auth_params() -> dict[str, str]:
    params = {}
    if key := os.environ.get("OPENALEX_API_KEY"):
        params["api_key"] = key
    if mailto := os.environ.get("OPENALEX_MAILTO"):
        params["mailto"] = mailto
    return params


def _url(path: str, params: dict[str, str]) -> str:
    return f"{path}?{urllib.parse.urlencode({**params, **_auth_params()})}"


class OpenAlexClient:
    def __init__(self, get: HttpGet = _urllib_get):
        self.get = get

    def references(self, openalex_id: str, limit: int, venue_by_source: dict[str, str]) -> list[PaperRecord]:
        """参考文献。被引用数で並べると分野をまたぐ古典ばかりになるため、並べ替えずに上限まで取る。"""
        work = self.get(_url(f"{BASE_URL}/{openalex_id}", {"select": "id,referenced_works"}))
        ids = [_short_id(u) for u in work.get("referenced_works") or []][:limit]
        if not ids:
            return []
        data = self.get(_url(BASE_URL, {"filter": f"openalex:{'|'.join(ids)}", "select": SELECT,
                                        "per-page": str(len(ids))}))
        return [parse_work(w, venue_by_source) for w in data.get("results", []) if w.get("title")]

    def citing(self, openalex_id: str, limit: int, venue_by_source: dict[str, str]) -> list[PaperRecord]:
        """被引用（この論文を引用している論文）。被引用数の多い順に上限まで取る。"""
        data = self.get(_url(BASE_URL, {"filter": f"cites:{openalex_id}", "sort": "cited_by_count:desc",
                                        "select": SELECT, "per-page": str(limit)}))
        return [parse_work(w, venue_by_source) for w in data.get("results", []) if w.get("title")]

    def search(self, keywords: list[str], source_ids: list[str], year_from: int,
               per_page: int, venue_by_source: dict[str, str]) -> list[PaperRecord]:
        data = self.get(build_url(keywords, source_ids, year_from, per_page))
        return [parse_work(w, venue_by_source) for w in data.get("results", []) if w.get("title")]
