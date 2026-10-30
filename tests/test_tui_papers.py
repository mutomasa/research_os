import json
from datetime import datetime

import pytest
from rich.cells import cell_len
from textual.widgets import Static

from research_os.data import profile, venues
from research_os.data.papers import PaperRecord, PaperStore
from research_os.tui.app import ResearchOSApp
from research_os.tui.papers import DismissScreen, PaperList, PapersContext, PapersView
from tui_helpers import run, title_of

BREAKDOWN = {"relevance": 0.9, "venue": 1.0, "gap": 0.5, "velocity": 0.5, "citations_per_year": 12.0,
             "venue_priority": 1, "primary_rq": "RQ2", "relevance_source": "llm",
             "llm_reason": "触覚で滑りを予測する世界モデルで RQ2 に直結する"}


@pytest.fixture
def ctx(root, tmp_path):
    store = PaperStore(tmp_path / "papers.db")
    now = datetime(2026, 10, 26)
    titles = ["Tactile World Models for Slip Prediction", "Contact-Rich Manipulation with Visuo-Tactile JEPA",
              "Failure-Aware Long-Horizon Policies"]
    for i, title in enumerate(titles):
        pid = store.upsert(PaperRecord(title=title, doi=f"10.1/{i}", venue_id="ral", year=2025,
                                       abstract="We propose …", authors=["A. Author", "B. Author"]),
                           "openalex", None, None, now)
        store.db.execute("UPDATE triage SET status='inbox', score=?, primary_rq='RQ2', breakdown=? WHERE paper_id=?",
                         (0.9 - i / 10, json.dumps(BREAKDOWN), pid))
    store.commit()
    yield PapersContext(store, profile.load_profile(root / "research/profile.yaml"),
                        venues.load_venues(root / "registry/venues.yaml"))
    store.close()


def app_with(ctx):
    return ResearchOSApp(research_theme="t", papers=ctx)


def list_text(app) -> str:
    plist = app.query_one(PaperList)
    return "\n".join(str(plist.get_option_at_index(i).prompt) for i in range(plist.option_count))


def test_inbox_lists_papers_with_preview(ctx):
    async def check(app, pilot):
        view = app.query_one(PapersView)
        assert title_of(view.query_one("#inbox-panel")) == "Inbox (3)"
        summary = str(view.query_one("#inbox-summary", Static).render())
        assert "今週 0/10" in summary and "未処理 3" in summary and "読む 0/5" in summary and "RQ1" in summary
        assert app.focused is app.query_one(PaperList)
        lines = list_text(app).split("\n")
        assert lines[0].startswith("▌0.90  Tactile World Models for Slip Prediction  ")
        assert lines[0].endswith("RA-L 2025")  # 掲載先は右寄せ
        assert "RQ2 に強く関連(LLM) · 投稿先 1 位 · 中核 8/15 · 被引用 12/年" in lines[1]
        assert lines[2].startswith(" 0.80")
        preview = str(view.query_one("#preview", Static).render())
        assert "触覚で滑りを予測する" in preview and "doi:10.1/0" in preview
        # 内訳は「項目・根拠・加点」の表（加点 = 重み × 要素の値）
        relevance = next(line for line in preview.splitlines() if line.startswith("RQ2 との関連"))
        assert "LLM 判定 0.90" in relevance and relevance.endswith("+0.45")
        assert "RA-L（優先 1 位）" in preview and "中核 8/15 本" in preview and "+0.20" in preview
        assert "合計" in preview
        await pilot.press("j")
        assert list_text(app).split("\n")[2].startswith("▌0.80")
        assert "Visuo-Tactile" in str(view.query_one("#preview", Static).render())

    run(check, app_with(ctx))


def test_rows_fit_the_list_width_without_key_presses(ctx):
    async def check(app, pilot):
        await pilot.pause()
        width = app.query_one(PaperList).scrollable_content_region.width
        for line in list_text(app).split("\n"):
            assert cell_len(line) <= width
        assert list_text(app).split("\n")[2].rstrip().endswith("RA-L 2025")

    run(check, app_with(ctx))


def test_triage_to_read_and_dismiss_with_reason(ctx):
    async def check(app, pilot):
        await pilot.press("r")
        assert ctx.store.count("to_read") == 1
        assert title_of(app.query_one("#inbox-panel")) == "Inbox (2)"
        await pilot.press("d")
        assert isinstance(app.screen, DismissScreen)
        await pilot.press("1")
        assert not isinstance(app.screen, DismissScreen)
        assert ctx.store.count("dismissed") == 1
        assert title_of(app.query_one("#inbox-panel")) == "Inbox (1)"
        # 取消すと何も変わらない
        await pilot.press("d", "escape")
        assert ctx.store.count("inbox") == 1

    run(check, app_with(ctx))


def test_invalid_transition_and_limit_are_reported(ctx):
    ctx.profile.intake.to_read_max = 0

    async def check(app, pilot):
        await pilot.press("c")  # inbox → core はできない
        await pilot.press("r")  # 読むの上限 0
        messages = [n.message for n in app._notifications]
        assert any("はできません" in m for m in messages)
        assert any("上限" in m for m in messages)
        assert ctx.store.count("inbox") == 3

    run(check, app_with(ctx))


def test_brackets_switch_views(ctx):
    async def check(app, pilot):
        await pilot.press("r", "right_square_bracket")
        assert title_of(app.query_one("#inbox-panel")) == "To read (1)"
        await pilot.press("e")  # to_read → read
        assert title_of(app.query_one("#inbox-panel")) == "To read (0)"
        await pilot.press("left_square_bracket")
        assert title_of(app.query_one("#inbox-panel")) == "Inbox (2)"

    run(check, app_with(ctx))


def test_empty_inbox_and_narrow_terminal(root, tmp_path):
    store = PaperStore(tmp_path / "papers.db")
    ctx = PapersContext(store, profile.load_profile(root / "research/profile.yaml"),
                        venues.load_venues(root / "registry/venues.yaml"))

    async def check(app, pilot):
        assert "Inbox は空です" in str(app.query_one("#empty", Static).render())
        assert not app.query_one("#preview-panel").display  # 100 列未満ではプレビューを隠す

    run(check, app_with(ctx), size=(80, 24))
