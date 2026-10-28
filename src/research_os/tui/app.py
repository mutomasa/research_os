"""Research OS の TUI アプリ本体（DESIGN.md §6.1・§7.1）。

上から ヘッダ / フェーズタブ / メイン / Agent 欄 / ステータスバー の順に積む。
ヘッダとタブの 3 行の右端には Neko（DESIGN.md §5.9）が座る。
"""

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import ContentSwitcher

from research_os.tui.agent import AgentInput, AgentPane, AgentState
from research_os.tui import neko
from research_os.tui.neko import MascotMode, Neko
from research_os.tui.theme import LAB_INK, PHASES
from research_os.tui.widgets import HeaderLine, HelpScreen, PhasePlaceholder, PhaseTabs, StatusBar


class ResearchOSApp(App):
    TITLE = "Research OS"
    # 起動直後はどこにもフォーカスを置かない。1–7 や q をそのままグローバルキーとして効かせるため
    AUTO_FOCUS = None
    CSS = """
    Screen { background: $background; }
    /* モーダル（ヘルプ・確認）は後ろの画面を透かす。上の Screen の指定が ModalScreen にも効くため上書きする */
    ModalScreen { background: $background 60%; }
    #top { height: 3; }
    #neko { margin-left: 2; }
    #main { height: 1fr; }
    #main > * {
        height: 1fr; padding: 0 1;
        border: round $neutral-200; color: $muted;
    }
    """
    BINDINGS = [
        *(Binding(p.key, f"phase('{p.id}')", p.label, show=False) for p in PHASES),
        Binding("greater_than_sign,i", "focus_agent", "agent", show=False),
        Binding("question_mark", "help", "help"),
        Binding("q", "quit", "quit"),
    ]

    phase: reactive[str] = reactive("papers", init=False)
    # Agent の状態はアプリ全体で 1 つ。Agent 欄と Neko（DESIGN.md §5.9）が購読する
    agent_state: reactive[AgentState] = reactive("idle", init=False)
    sleeping: reactive[bool] = reactive(False, init=False)

    done_seconds = 5.0  # done の顔を見せてから idle に戻すまで
    sleep_seconds = 600.0  # 操作がないまま経つと Neko が眠る

    def __init__(self, research_theme: str | None = None, mascot: MascotMode = "full", **kwargs):
        super().__init__(**kwargs)
        self.research_theme = research_theme
        self.mascot = mascot
        # CSS の $agent などはテーマの変数なので、CSS を読む前に登録する
        self.register_theme(LAB_INK)
        self.theme = LAB_INK.name

    def compose(self) -> ComposeResult:
        with Horizontal(id="top"):
            with Vertical():
                yield HeaderLine(self.research_theme, id="header")
                yield PhaseTabs(id="tabs")
            yield Neko(id="neko")
        with ContentSwitcher(initial=self.phase, id="main"):
            for p in PHASES:
                yield PhasePlaceholder(p)
        yield AgentPane(id="agent")
        yield StatusBar(id="status")

    def watch_phase(self, phase: str) -> None:
        self.query_one(PhaseTabs).active = phase
        self.query_one(ContentSwitcher).current = phase
        self.query_one(AgentPane).phase = phase

    def on_mount(self) -> None:
        self._sleep_timer = self.set_timer(self.sleep_seconds, self._fall_asleep)
        self._update_mascot()

    def on_resize(self, event: events.Resize) -> None:
        self._update_mascot()

    async def on_event(self, event: events.Event) -> None:
        if isinstance(event, (events.Key, events.MouseDown)) and hasattr(self, "_sleep_timer"):
            self.sleeping = False
            self._sleep_timer.reset()
        await super().on_event(event)

    def _fall_asleep(self) -> None:
        if self.agent_state == "idle":
            self.sleeping = True

    def watch_agent_state(self, state: AgentState) -> None:
        self.query_one(AgentPane).state = state
        if state == "done":
            self.set_timer(self.done_seconds, self._done_to_idle)
        self._update_mascot()

    def _done_to_idle(self) -> None:
        if self.agent_state == "done":
            self.agent_state = "idle"

    def watch_sleeping(self) -> None:
        self._update_mascot()

    def _update_mascot(self) -> None:
        """mascot 設定と端末の幅で、右上の 3 行版・ヘッダの 1 行版・非表示を切り替える。"""
        state = "sleep" if self.sleeping and self.agent_state == "idle" else self.agent_state
        mode = self.mascot
        if mode == "full" and self.size.width < neko.COMPACT_BELOW:
            mode = "compact"
        cat = self.query_one(Neko)
        cat.display = mode == "full"
        cat.state = state
        self.query_one(HeaderLine).mascot = neko.compact(state) if mode == "compact" else None

    def action_phase(self, phase: str) -> None:
        self.phase = phase

    def action_focus_agent(self) -> None:
        self.query_one(AgentPane).focus_input()

    def on_agent_input_leave(self, event: AgentInput.Leave) -> None:
        self.set_focus(None)

    def action_help(self) -> None:
        if not isinstance(self.screen, HelpScreen):
            self.push_screen(HelpScreen())
