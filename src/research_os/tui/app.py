"""Research OS の TUI アプリ本体（DESIGN.md §6.1・§7.1）。

上から ヘッダ / フェーズタブ / メイン / ステータスバー の順に積む。Agent 欄は feat/tui-agent-pane で入る。
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.widgets import ContentSwitcher

from research_os.tui.theme import LAB_INK, PHASES
from research_os.tui.widgets import HeaderLine, HelpScreen, PhasePlaceholder, PhaseTabs, StatusBar


class ResearchOSApp(App):
    TITLE = "Research OS"
    CSS = """
    Screen { background: $background; }
    /* モーダル（ヘルプ・確認）は後ろの画面を透かす。上の Screen の指定が ModalScreen にも効くため上書きする */
    ModalScreen { background: $background 60%; }
    #main { height: 1fr; }
    #main > * {
        height: 1fr; padding: 0 1;
        border: round $neutral-200; color: $muted;
    }
    """
    BINDINGS = [
        *(Binding(p.key, f"phase('{p.id}')", p.label, show=False) for p in PHASES),
        Binding("question_mark", "help", "help"),
        Binding("q", "quit", "quit"),
    ]

    phase: reactive[str] = reactive("papers", init=False)

    def __init__(self, research_theme: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.research_theme = research_theme
        # CSS の $agent などはテーマの変数なので、CSS を読む前に登録する
        self.register_theme(LAB_INK)
        self.theme = LAB_INK.name

    def compose(self) -> ComposeResult:
        yield HeaderLine(self.research_theme, id="header")
        yield PhaseTabs(id="tabs")
        with ContentSwitcher(initial=self.phase, id="main"):
            for p in PHASES:
                yield PhasePlaceholder(p)
        yield StatusBar(id="status")

    def watch_phase(self, phase: str) -> None:
        self.query_one(PhaseTabs).active = phase
        self.query_one(ContentSwitcher).current = phase

    def action_phase(self, phase: str) -> None:
        self.phase = phase

    def action_help(self) -> None:
        if not isinstance(self.screen, HelpScreen):
            self.push_screen(HelpScreen())
