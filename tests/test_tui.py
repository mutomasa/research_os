import asyncio

from rich.cells import cell_len
from textual.content import Content
from textual.widgets import ContentSwitcher

from research_os.tui.app import ResearchOSApp
from research_os.tui.widgets import HeaderLine, HelpScreen, PhaseTabs, StatusBar


def run(coro_fn, app=None, size=(120, 36)):
    """Textual の run_test を pytest-asyncio なしで回す。"""
    app = app or ResearchOSApp(research_theme="vision tactile world model")

    async def main():
        async with app.run_test(size=size) as pilot:
            await coro_fn(app, pilot)

    asyncio.run(main())


def text_of(widget) -> str:
    return widget.render().plain


def title_of(widget) -> str:
    return Content.from_markup(widget.border_title).plain


def test_starts_on_papers():
    async def check(app, pilot):
        assert app.phase == "papers"
        assert app.query_one(ContentSwitcher).current == "papers"
        tabs, marker = text_of(app.query_one(PhaseTabs)).split("\n")
        # マーカーは「1 Papers」の真下
        assert tabs.index("1 Papers") == marker.index("▔")
        assert marker.count("▔") == len("1 Papers")

    run(check)


def test_number_keys_switch_phase():
    async def check(app, pilot):
        await pilot.press("3")
        assert app.phase == "graph"
        assert app.query_one(ContentSwitcher).current == "graph"
        await pilot.press("7")
        tabs, marker = text_of(app.query_one(PhaseTabs)).split("\n")
        assert tabs.index("7 Intel") == marker.index("▔")

    run(check)


def test_help_opens_and_closes():
    async def check(app, pilot):
        await pilot.press("question_mark")
        assert isinstance(app.screen, HelpScreen)
        await pilot.press("escape")
        assert not isinstance(app.screen, HelpScreen)

    run(check)


def test_header_shows_theme_and_truncates():
    async def check(app, pilot):
        line = text_of(app.query_one(HeaderLine))
        assert line.startswith(" Research OS  ·  ")
        assert line.endswith(app.query_one(HeaderLine).now.strftime("%Y-%m-%d %H:%M"))
        assert "…" in line
        assert cell_len(line) == 80  # 全角 = 2 列で数える（DESIGN.md §7.3）

    run(check, ResearchOSApp(research_theme="失敗認識型の長期ロボットマニピュレーションに向けた視覚・触覚統合JEPA世界モデル"),
        size=(80, 24))


def test_status_bar_lists_connections_as_unset():
    async def check(app, pilot):
        line = text_of(app.query_one(StatusBar))
        for name in ["Paperpile", "arXiv", "alphaXiv", "GitHub", "Feeds", "MCP"]:
            assert f"{name} –" in line
        assert line.rstrip().endswith("q quit")

    run(check)


def test_agent_pane_input_history_and_unconnected_notice():
    from textual.widgets import RichLog

    from research_os.tui.agent import AgentInput, AgentPane

    async def check(app, pilot):
        await pilot.press("greater_than_sign")
        inp = app.query_one(AgentInput)
        assert app.focused is inp
        # フォーカス中の数字や q は入力される（タブ切替・終了にならない）
        await pilot.press(*"q3", "enter")
        assert app.phase == "papers" and app.is_running
        log = "\n".join(line.text for line in app.query_one(RichLog).lines)
        assert "❯ q3" in log and "未接続" in log
        assert inp.value == ""
        await pilot.press("up")
        assert inp.value == "q3"
        await pilot.press("down")
        assert inp.value == ""
        await pilot.press("escape")
        assert app.focused is None
        await pilot.press("4")
        assert "Hypothesis" in title_of(app.query_one(AgentPane))

    run(check)


def test_agent_pane_completes_suggestion_and_shows_state():
    from research_os.tui.agent import AgentInput, AgentPane

    async def check(app, pilot):
        await pilot.press("i", *"今週", "tab")
        assert app.query_one(AgentInput).value == "今週の Inbox"
        pane = app.query_one(AgentPane)
        assert title_of(pane).endswith("idle")
        app.agent_state = "running"
        await pilot.pause()
        assert title_of(pane).endswith("running")
        assert pane.has_class("-busy")
        assert not pane.query_one("#suggestions").display

    run(check)


def test_nothing_is_focused_at_start():
    async def check(app, pilot):
        assert app.focused is None

    run(check)
