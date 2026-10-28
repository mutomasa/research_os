"""全画面共通の部品：ヘッダ・フェーズタブ・ステータスバー・ヘルプ（DESIGN.md §5.1・§5.7・§9）。"""

from datetime import datetime

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Static

from research_os.tui import theme
from research_os.tui.theme import PHASES

# 接続の状態記号（DESIGN.md §5.7）。まだどれも実装していないので既定は unset
CONNECTION_MARKS = {
    "ok": ("✓", theme.SUCCESS),
    "partial": ("⚠", theme.WARNING),
    "down": ("✗", theme.ERROR),
    "checking": ("⠋", theme.MUTED),
    "unset": ("–", theme.NEUTRAL_300),
}
CONNECTIONS = ["Paperpile", "arXiv", "alphaXiv", "GitHub", "Feeds", "MCP"]

GLOBAL_KEYS = [
    ("1–7", "フェーズタブ切替（7 は Intel）"),
    (">  i", "Agent 欄に入力"),
    ("esc", "Agent 欄からメインに戻る"),
    ("↑ ↓", "Agent 欄の入力履歴"),
    ("tab", "Agent 欄で提案を補完"),
    ("?", "このヘルプ"),
    ("q", "終了"),
]


class HeaderLine(Widget):
    """1 行目：アプリ名 · 研究テーマ（左）と時刻（右）。狭い端末では時刻の右に 1 行の Neko を置く。"""

    DEFAULT_CSS = "HeaderLine { height: 1; }"

    now: reactive[datetime] = reactive(datetime.now)
    mascot: reactive[Text | None] = reactive(None)

    def __init__(self, research_theme: str | None, **kwargs):
        super().__init__(**kwargs)
        self.research_theme = research_theme

    def on_mount(self) -> None:
        self.set_interval(30, lambda: setattr(self, "now", datetime.now()))

    def render(self) -> Text:
        clock = Text(self.now.strftime("%Y-%m-%d %H:%M"), style=theme.MUTED)
        if self.mascot is not None:
            clock += Text(" ") + self.mascot
        left = Text(" Research OS", style=f"bold {theme.FOREGROUND}")
        if self.research_theme:
            left.append("  ·  ", style=theme.MUTED)
            left.append(self.research_theme, style=theme.FOREGROUND)
        # 時刻との間に 2 列は空ける。テーマが長ければ表示幅で切って … を付ける（§7.3）
        left.truncate(max(self.size.width - clock.cell_len - 2, 0), overflow="ellipsis")
        gap = max(self.size.width - left.cell_len - clock.cell_len, 1)
        return left + Text(" " * gap) + clock


class PhaseTabs(Widget):
    """2〜3 行目：フェーズタブとアクティブタブ下の ▔ マーカー。"""

    DEFAULT_CSS = "PhaseTabs { height: 2; }"

    active: reactive[str] = reactive("papers")

    def render(self) -> Text:
        tabs = Text(" ")
        start = end = 0
        for i, phase in enumerate(PHASES):
            if i:
                tabs.append("   ")
            if phase.track:
                tabs.append("│   ", style=theme.NEUTRAL_200)
            is_active = phase.id == self.active
            if is_active:
                start = tabs.cell_len
            tabs.append(phase.key, style=theme.MUTED)
            tabs.append(" ")
            tabs.append(phase.label, style=f"bold {phase.color}" if is_active else theme.FOREGROUND)
            if is_active:
                end = tabs.cell_len
        active_color = theme.PHASE_BY_ID[self.active].color
        marker = Text(" " * start) + Text("▔" * (end - start), style=active_color)
        return Text("\n").join([tabs, marker])


class StatusBar(Widget):
    """最下行：外部接続（左）とキーヒント（右）。"""

    DEFAULT_CSS = "StatusBar { height: 1; background: $neutral-50; }"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.states = {name: "unset" for name in CONNECTIONS}

    def render(self) -> Text:
        left = Text(" ")
        for i, name in enumerate(CONNECTIONS):
            mark, color = CONNECTION_MARKS[self.states[name]]
            if i:
                left.append("  ")
            left.append(f"{name} ", style=theme.FOREGROUND)
            left.append(mark, style=color)
        right = Text()
        for key, desc in [("?", "help"), ("q", "quit")]:
            right.append(f"  {key} ", style=theme.ACCENT)
            right.append(desc, style=theme.MUTED)
        right.append(" ")
        gap = max(self.size.width - left.cell_len - right.cell_len, 1)
        return left + Text(" " * gap) + right


class PhasePlaceholder(Static):
    """まだ実装していないフェーズのメイン領域。"""

    def __init__(self, phase: theme.Phase, **kwargs):
        super().__init__(f"{phase.label} 画面は未実装です（docs/todo.md）", id=phase.id, **kwargs)
        self.border_title = phase.label
        self.styles.border_title_color = phase.color


class HelpScreen(ModalScreen):
    """? で開くキー一覧（DESIGN.md §9）。"""

    BINDINGS = [Binding("escape,question_mark,q", "app.pop_screen", "閉じる")]
    DEFAULT_CSS = """
    HelpScreen { align: center middle; }
    HelpScreen > Static {
        width: auto; height: auto; padding: 0 1;
        border: round $primary; background: $surface;
    }
    """

    def compose(self) -> ComposeResult:
        body = Text()
        for i, (key, desc) in enumerate(GLOBAL_KEYS):
            if i:
                body.append("\n")
            body.append(f"{key:<6}", style=theme.ACCENT)
            body.append(desc, style=theme.FOREGROUND)
        help_box = Static(body)
        help_box.border_title = "Keys"
        help_box.border_subtitle = "esc 閉じる"
        yield help_box
