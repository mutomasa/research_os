"""Agent 欄（DESIGN.md §5.3）。

入力・履歴・提案・状態表示までを持つ。Agent コア（todo.md §1）はまだ無いので、
送信した指示はログに残し「未接続」と明示するだけにする。
"""

from typing import Literal

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.events import Resize
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Input, RichLog, Static

from research_os.tui import theme

AgentState = Literal["idle", "thinking", "running", "done", "confirm", "error"]

STATE_LABELS: dict[str, tuple[str, str]] = {
    "idle": ("idle", theme.MUTED),
    "thinking": ("thinking…", theme.AGENT),
    "running": ("⠋ running", theme.AGENT),
    "done": ("✓ done", theme.SUCCESS),
    "confirm": ("⚠ confirm", theme.WARNING),
    "error": ("✗ failed", theme.ERROR),
}

# 待機中に出す指示例（design.md §1・§2 の「Agent への指示例」）
SUGGESTIONS = {
    "papers": ["Find papers about …", "Show only papers after 2024", "今週の Inbox"],
    "review": ["Compare these papers", "Find research gaps"],
    "graph": ["Find research gaps", "Show RQ coverage"],
    "hypothesis": ["Find research gaps", "Design experiment"],
    "run": ["Design experiment"],
    "paper": ["Which venue fits PD-001 best right now?", "List missing requirements for RA-L"],
    "intel": ["Summarize this week's updates from …", "Generate the weekly intelligence report"],
}


class AgentInput(Input):
    """❯ の入力行。↑ / ↓ で履歴、tab で提案を補完、esc でメインに戻る（DESIGN.md §9.3）。"""

    BINDINGS = [
        Binding("up", "history(-1)", show=False),
        Binding("down", "history(1)", show=False),
        Binding("tab", "complete", show=False),
        Binding("escape", "leave", show=False),
    ]

    class Leave(Message):
        pass

    def __init__(self, **kwargs):
        super().__init__(placeholder="", **kwargs)
        self.history: list[str] = []
        self._cursor = 0  # len(history) は「まだ履歴に無い新しい入力」
        self.suggestions: list[str] = []

    def remember(self, text: str) -> None:
        self.history.append(text)
        self._cursor = len(self.history)

    def action_history(self, step: int) -> None:
        if not self.history:
            return
        self._cursor = min(max(self._cursor + step, 0), len(self.history))
        self.value = self.history[self._cursor] if self._cursor < len(self.history) else ""
        self.cursor_position = len(self.value)

    def action_complete(self) -> None:
        for s in self.suggestions:
            if s.lower().startswith(self.value.lower()) and s != self.value:
                self.value = s
                self.cursor_position = len(s)
                return

    def action_leave(self) -> None:
        self.post_message(self.Leave())


class AgentPane(Vertical):
    DEFAULT_CSS = """
    AgentPane {
        height: 7; padding: 0 1;
        border: round $agent 60%; border-title-color: $foreground; border-subtitle-color: $muted; border-subtitle-align: left;
        background: $surface;
    }
    AgentPane:focus-within { border: round $agent; }
    AgentPane.-busy { border: heavy $agent; }
    AgentPane RichLog { height: 1fr; background: $surface; scrollbar-size: 0 0; }
    AgentPane #prompt-row { height: 1; }
    AgentPane #prompt { width: 2; color: $agent; }
    AgentPane AgentInput { height: 1; border: none; padding: 0; background: $surface; }
    AgentPane AgentInput:focus { border: none; background: $surface; }
    AgentPane #suggestions { height: 1; color: $muted; text-style: dim; padding-left: 2; }
    """

    phase: reactive[str] = reactive("papers")
    state: reactive[AgentState] = reactive("idle")

    def compose(self) -> ComposeResult:
        log = RichLog(wrap=True, id="agent-log")
        log.can_focus = False  # 起動直後に自動でフォーカスを取らない（入力は > / i で始める）
        yield log
        with Horizontal(id="prompt-row"):
            yield Static("❯", id="prompt")
            yield AgentInput(id="agent-input")
        yield Static(id="suggestions")

    def on_mount(self) -> None:
        self.border_subtitle = "enter 送信  ↑↓ 履歴  tab 補完  esc 戻る"
        self._refresh_chrome()

    def on_resize(self, event: Resize) -> None:
        self._refresh_title()

    def watch_phase(self) -> None:
        if self.is_mounted:
            self._refresh_chrome()

    def watch_state(self, state: AgentState) -> None:
        if self.is_mounted:
            self.set_class(state in ("thinking", "running"), "-busy")
            self._refresh_chrome()

    def _refresh_chrome(self) -> None:
        self._refresh_title()
        suggestions = SUGGESTIONS.get(self.phase, [])
        self.query_one(AgentInput).suggestions = suggestions
        line = self.query_one("#suggestions", Static)
        line.update(" · ".join(suggestions))
        line.display = self.state == "idle"

    def _refresh_title(self) -> None:
        """タイトルは `Agent · <フェーズ>`（左）と状態（右）を同じ枠線上に並べる（§7.3）。"""
        phase = theme.PHASE_BY_ID[self.phase]
        label, color = STATE_LABELS[self.state]
        left = Text("Agent · ") + Text(phase.label, style=phase.color)
        right = Text(label, style=color)
        # 枠の角と左右の ─ の分（各 2〜3 列）を引いた幅で右に寄せる
        gap = max(self.size.width - 8 - left.cell_len - right.cell_len, 1)
        self.border_title = left + Text(" " + "─" * gap + " ", style=f"{theme.AGENT} dim") + right

    def focus_input(self) -> None:
        self.query_one(AgentInput).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        event.input.value = ""
        if not text:
            return
        event.input.remember(text)
        log = self.query_one(RichLog)
        log.write(Text("❯ ", style=theme.AGENT) + Text(text, style=theme.FOREGROUND))
        log.write(Text("  ◯ ", style=theme.MUTED)
                  + Text("Agent コアは未接続です（docs/todo.md §1）", style=theme.MUTED))
