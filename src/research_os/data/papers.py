"""論文ライブラリと Inbox の SQLite ストア。

仕様: docs/new_features/paper_intake.md §3 / ADR-0003
"""

import json
import re
import sqlite3
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

DEFAULT_PATH = Path("research/papers.db")

STATUSES = ("candidate", "inbox", "to_read", "read", "core", "dismissed")
LIBRARY = ("to_read", "read", "core")
DISMISS_REASONS = ("irrelevant", "known", "outdated", "low_quality", "other")

# 人が行う判断の遷移（candidate → inbox は surface() だけが行う）
TRANSITIONS = {
    "inbox": {"to_read", "read", "dismissed"},
    "to_read": {"read", "dismissed"},
    "read": {"core", "dismissed"},
    "core": {"read"},
    "dismissed": {"inbox"},
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS papers (
    paper_id TEXT PRIMARY KEY,
    doi TEXT UNIQUE,
    arxiv_id TEXT UNIQUE,
    openalex_id TEXT UNIQUE,
    title TEXT NOT NULL,
    title_norm TEXT NOT NULL,
    abstract TEXT,
    year INTEGER,
    authors TEXT NOT NULL DEFAULT '[]',
    venue_id TEXT,
    venue_name TEXT,
    cited_by_count INTEGER NOT NULL DEFAULT 0,
    first_seen TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS papers_title_norm ON papers (title_norm);
CREATE TABLE IF NOT EXISTS paper_sources (
    paper_id TEXT NOT NULL REFERENCES papers (paper_id),
    source TEXT NOT NULL,
    source_ref TEXT,
    query TEXT,
    retrieved_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS triage (
    paper_id TEXT PRIMARY KEY REFERENCES papers (paper_id),
    status TEXT NOT NULL,
    score REAL,
    breakdown TEXT,
    primary_rq TEXT,
    surfaced_at TEXT,
    decided_at TEXT,
    dismiss_reason TEXT
);
CREATE TABLE IF NOT EXISTS paper_rq (
    paper_id TEXT NOT NULL REFERENCES papers (paper_id),
    rq_id TEXT NOT NULL,
    relevance REAL NOT NULL,
    PRIMARY KEY (paper_id, rq_id)
);
CREATE TABLE IF NOT EXISTS fetch_log (
    query_key TEXT PRIMARY KEY,
    fetched_at TEXT NOT NULL,
    result_count INTEGER NOT NULL
);
"""


def normalize_title(title: str) -> str:
    t = unicodedata.normalize("NFKC", title).lower()
    t = re.sub(r"[^0-9a-z]+", " ", t)
    return " ".join(t.split())


@dataclass
class PaperRecord:
    """取得元から得た 1 本の論文。"""

    title: str
    doi: str | None = None
    arxiv_id: str | None = None
    openalex_id: str | None = None
    abstract: str | None = None
    year: int | None = None
    authors: list[str] = field(default_factory=list)
    venue_id: str | None = None
    venue_name: str | None = None
    cited_by_count: int = 0

    def preferred_id(self) -> str:
        if self.doi:
            return f"doi:{self.doi}"
        if self.arxiv_id:
            return f"arxiv:{self.arxiv_id}"
        if self.openalex_id:
            return f"openalex:{self.openalex_id}"
        return f"title:{normalize_title(self.title)}"


class InvalidTransition(ValueError):
    pass


class LimitReached(ValueError):
    pass


class PaperStore:
    def __init__(self, path: Path | str = DEFAULT_PATH):
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)

    def close(self) -> None:
        self.db.close()

    # ── 取り込み ──────────────────────────────────────────────

    def find(self, rec: PaperRecord) -> str | None:
        """外部 ID・正規化題名のどれかが一致する既存の paper_id を返す。"""
        for column, value in (
            ("doi", rec.doi),
            ("arxiv_id", rec.arxiv_id),
            ("openalex_id", rec.openalex_id),
            ("title_norm", normalize_title(rec.title)),
        ):
            if value:
                row = self.db.execute(f"SELECT paper_id FROM papers WHERE {column} = ?", (value,)).fetchone()
                if row:
                    return row["paper_id"]
        return None

    def upsert(self, rec: PaperRecord, source: str, source_ref: str | None, query: str | None, now: datetime) -> str:
        """論文を追加し、既にあれば欠けている項目だけ埋める（プレプリントと出版版を 1 本にまとめる）。"""
        ts = now.isoformat()
        paper_id = self.find(rec)
        if paper_id is None:
            paper_id = rec.preferred_id()
            self.db.execute(
                "INSERT INTO papers (paper_id, doi, arxiv_id, openalex_id, title, title_norm, abstract, year,"
                " authors, venue_id, venue_name, cited_by_count, first_seen, updated_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (paper_id, rec.doi, rec.arxiv_id, rec.openalex_id, rec.title, normalize_title(rec.title),
                 rec.abstract, rec.year, json.dumps(rec.authors, ensure_ascii=False), rec.venue_id,
                 rec.venue_name, rec.cited_by_count, ts, ts),
            )
            self.db.execute("INSERT INTO triage (paper_id, status) VALUES (?, 'candidate')", (paper_id,))
        else:
            # 出版版（venue あり）の情報を優先し、被引用数は大きいほうを残す
            self.db.execute(
                "UPDATE papers SET doi = COALESCE(doi, ?), arxiv_id = COALESCE(arxiv_id, ?),"
                " openalex_id = COALESCE(openalex_id, ?), abstract = COALESCE(abstract, ?),"
                " year = COALESCE(year, ?), venue_id = COALESCE(?, venue_id),"
                " venue_name = COALESCE(?, venue_name), cited_by_count = MAX(cited_by_count, ?),"
                " updated_at = ? WHERE paper_id = ?",
                (rec.doi, rec.arxiv_id, rec.openalex_id, rec.abstract, rec.year, rec.venue_id,
                 rec.venue_name, rec.cited_by_count, ts, paper_id),
            )
        self.db.execute(
            "INSERT INTO paper_sources (paper_id, source, source_ref, query, retrieved_at) VALUES (?, ?, ?, ?, ?)",
            (paper_id, source, source_ref, query, ts),
        )
        self.db.commit()
        return paper_id

    def last_fetched(self, query_key: str) -> datetime | None:
        row = self.db.execute("SELECT fetched_at FROM fetch_log WHERE query_key = ?", (query_key,)).fetchone()
        return datetime.fromisoformat(row["fetched_at"]) if row else None

    def log_fetch(self, query_key: str, count: int, now: datetime) -> None:
        self.db.execute(
            "INSERT INTO fetch_log (query_key, fetched_at, result_count) VALUES (?, ?, ?)"
            " ON CONFLICT (query_key) DO UPDATE SET fetched_at = excluded.fetched_at,"
            " result_count = excluded.result_count",
            (query_key, now.isoformat(), count),
        )
        self.db.commit()

    # ── スコア ────────────────────────────────────────────────

    def papers(self, status: str | None = None) -> list[sqlite3.Row]:
        sql = "SELECT p.*, t.status, t.score, t.breakdown, t.primary_rq, t.surfaced_at FROM papers p JOIN triage t USING (paper_id)"
        if status:
            return self.db.execute(sql + " WHERE t.status = ? ORDER BY t.score DESC", (status,)).fetchall()
        return self.db.execute(sql).fetchall()

    def set_relevance(self, paper_id: str, relevance: dict[str, float]) -> None:
        self.db.execute("DELETE FROM paper_rq WHERE paper_id = ?", (paper_id,))
        self.db.executemany(
            "INSERT INTO paper_rq (paper_id, rq_id, relevance) VALUES (?, ?, ?)",
            [(paper_id, rq, r) for rq, r in relevance.items()],
        )

    def set_score(self, paper_id: str, score: float, breakdown: dict, primary_rq: str | None) -> None:
        self.db.execute(
            "UPDATE triage SET score = ?, breakdown = ?, primary_rq = ? WHERE paper_id = ?",
            (score, json.dumps(breakdown, ensure_ascii=False), primary_rq, paper_id),
        )

    def commit(self) -> None:
        self.db.commit()

    # ── 集計（上限の計算） ────────────────────────────────────

    def count(self, status: str | tuple[str, ...], primary_rq: str | None = None) -> int:
        statuses = (status,) if isinstance(status, str) else status
        sql = f"SELECT COUNT(*) FROM triage WHERE status IN ({','.join('?' * len(statuses))})"
        args: list = list(statuses)
        if primary_rq:
            sql += " AND primary_rq = ?"
            args.append(primary_rq)
        return self.db.execute(sql, args).fetchone()[0]

    def surfaced_since(self, since: datetime, primary_rq: str | None = None) -> int:
        sql = "SELECT COUNT(*) FROM triage WHERE surfaced_at >= ?"
        args: list = [since.isoformat()]
        if primary_rq:
            sql += " AND primary_rq = ?"
            args.append(primary_rq)
        return self.db.execute(sql, args).fetchone()[0]

    def mark_surfaced(self, paper_id: str, now: datetime) -> None:
        self.db.execute(
            "UPDATE triage SET status = 'inbox', surfaced_at = ? WHERE paper_id = ? AND status = 'candidate'",
            (now.isoformat(), paper_id),
        )

    # ── 人の判断 ──────────────────────────────────────────────

    def status(self, paper_id: str) -> str:
        row = self.db.execute("SELECT status FROM triage WHERE paper_id = ?", (paper_id,)).fetchone()
        if row is None:
            raise KeyError(paper_id)
        return row["status"]

    def decide(self, paper_id: str, new_status: str, now: datetime, to_read_max: int,
               reason: str | None = None) -> None:
        current = self.status(paper_id)
        if new_status not in TRANSITIONS.get(current, set()):
            raise InvalidTransition(f"{paper_id}: {current} → {new_status} はできません")
        if new_status == "dismissed" and reason not in DISMISS_REASONS:
            raise ValueError(f"捨てる理由を {DISMISS_REASONS} から選んでください")
        if new_status == "to_read" and self.count("to_read") >= to_read_max:
            raise LimitReached(f"「読む」が上限 {to_read_max} 本に達しています。読み終えるか捨ててから追加してください")
        self.db.execute(
            "UPDATE triage SET status = ?, decided_at = ?, dismiss_reason = ? WHERE paper_id = ?",
            (new_status, now.isoformat(), reason if new_status == "dismissed" else None, paper_id),
        )
        self.db.commit()
