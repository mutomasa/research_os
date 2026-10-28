import asyncio

from rich.cells import cell_len
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


def test_help_keeps_the_screen_behind_visible():
    async def check(app, pilot):
        await pilot.press("question_mark")
        assert app.screen.styles.background.a < 1

    run(check)
