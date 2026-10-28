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
        # 100 列未満なので Neko は時刻の右に 1 行で座る（DESIGN.md §5.9）
        assert line.endswith(app.query_one(HeaderLine).now.strftime("%Y-%m-%d %H:%M") + " (o.o)")
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


def neko_text(app) -> str:
    from research_os.tui.neko import Neko

    return text_of(app.query_one(Neko))


def test_neko_sits_top_right_and_follows_agent_state():
    from research_os.tui.neko import Neko

    async def check(app, pilot):
        cat = app.query_one(Neko)
        assert cat.display
        # ヘッダ〜マーカーの 3 行の右端 7 列
        assert (cat.region.x, cat.region.y, cat.region.width, cat.region.height) == (113, 0, 7, 3)
        assert neko_text(app) == " /\\_/\\ \n( o.o )\n > ^ < "
        for state, face in [("thinking", "( -.- )"), ("running", "( O.O )"), ("error", "( x.x )")]:
            app.agent_state = state
            await pilot.pause()
            assert neko_text(app).split("\n")[1] == face
        app.agent_state = "confirm"
        await pilot.pause()
        assert neko_text(app).split("\n")[1:] == ["( o.O )", " > ? < "]

    run(check)


def test_neko_done_returns_to_idle_and_sleeps_when_untouched():
    app = ResearchOSApp()
    app.done_seconds = 0.05
    app.sleep_seconds = 0.1

    async def check(app, pilot):
        app.agent_state = "done"
        await pilot.pause()
        assert neko_text(app).split("\n")[1] == "( ^.^ )"
        await pilot.pause(0.3)
        assert app.agent_state == "idle"
        assert app.sleeping
        assert neko_text(app).split("\n")[0].endswith("z")
        await pilot.press("3")
        assert not app.sleeping
        assert neko_text(app).split("\n")[1] == "( o.o )"

    run(check, app)


def test_neko_modes():
    from research_os.tui.neko import Neko

    async def compact(app, pilot):
        assert not app.query_one(Neko).display
        assert text_of(app.query_one(HeaderLine)).endswith(" (o.o)")

    async def off(app, pilot):
        assert not app.query_one(Neko).display
        assert not text_of(app.query_one(HeaderLine)).endswith(")")

    run(compact, ResearchOSApp(mascot="compact"))
    run(off, ResearchOSApp(mascot="off"))


def test_help_keeps_the_screen_behind_visible():
    async def check(app, pilot):
        await pilot.press("question_mark")
        assert app.screen.styles.background.a < 1

    run(check)
