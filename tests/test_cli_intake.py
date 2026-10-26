from datetime import datetime

from research_os.cli import main
from research_os.data.papers import PaperRecord, PaperStore


def _args(root, db, *rest):
    return ["--registry", str(root / "registry/venues.yaml"), "--profile", str(root / "research/profile.yaml"),
            "--db", str(db), *rest]


def test_inbox_and_triage(root, tmp_path, capsys):
    db = tmp_path / "papers.db"
    store = PaperStore(db)
    pid = store.upsert(PaperRecord(title="JEPA world models for failure prediction", doi="10.1/a",
                                   venue_id="ral", year=2025, cited_by_count=10), "openalex", None, None,
                       datetime(2026, 10, 25))
    store.db.execute("UPDATE triage SET status='inbox', score=0.8, primary_rq='RQ2',"
                     " breakdown='{\"relevance\":1.0,\"venue\":1.0,\"gap\":1.0,\"velocity\":0.5,"
                     "\"citations_per_year\":5.0,\"venue_priority\":1,\"primary_rq\":\"RQ2\"}' WHERE paper_id=?", (pid,))
    store.commit()
    store.close()

    assert main(_args(root, db, "inbox")) == 0
    out = capsys.readouterr().out
    assert "未処理 1" in out and "RA-L 2025" in out and "RQ2 関連 1.00" in out

    assert main(_args(root, db, "triage", pid, "dismissed")) == 1
    assert "理由" in capsys.readouterr().err
    assert main(_args(root, db, "triage", pid, "to_read")) == 0
    assert main(_args(root, db, "triage", "doi:nope", "to_read")) == 1


def test_suggest_and_explore_without_core(root, tmp_path, capsys):
    db = tmp_path / "papers.db"
    assert main(_args(root, db, "intake", "suggest")) == 0
    assert "提案はありません" in capsys.readouterr().out


def test_explore_without_core_makes_no_requests(root, tmp_path, capsys, monkeypatch):
    import research_os.cli as cli

    class NoNetwork:
        def references(self, *a):
            raise AssertionError("network")

        citing = references

    monkeypatch.setattr(cli, "OpenAlexClient", NoNetwork)
    assert main(_args(root, tmp_path / "papers.db", "intake", "explore")) == 0
    assert "中核論文（core）がまだありません" in capsys.readouterr().out


def test_rate_limit_is_reported_and_partial_results_kept(root, tmp_path, capsys, monkeypatch):
    import io
    import urllib.error

    import research_os.sources.openalex as oa

    calls = []

    def fake_urlopen(req, timeout):
        calls.append(req.full_url)
        if len(calls) == 1:
            body = {"results": [{"id": "https://openalex.org/W1", "title": "Tactile sensing for slip detection",
                                 "publication_year": 2025, "cited_by_count": 3, "locations": [],
                                 "primary_location": None, "authorships": []}]}
            return io.BytesIO(__import__("json").dumps(body).encode())
        raise urllib.error.HTTPError(req.full_url, 429, "Too Many Requests", {}, None)

    monkeypatch.setattr(oa.urllib.request, "urlopen", fake_urlopen)
    db = tmp_path / "papers.db"
    assert main(_args(root, db, "intake", "run")) == 1
    assert "無料枠を使い切りました" in capsys.readouterr().err
    assert len(PaperStore(db).papers()) == 1  # 枠を使い切る前に取得した分は残る
