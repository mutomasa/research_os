"""右上のマスコット Neko（DESIGN.md §5.9）。

Agent の状態を表情で示す。状態が変わったときに顔を差し替えるだけで、常時アニメーションはしない。
"""

from typing import Literal

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from research_os.tui import theme

MascotMode = Literal["full", "compact", "off"]

EARS = " /\\_/\\ "
MOUTH = " > ^ < "
# 状態 → (顔の行, 顔の行の色)。耳と口の行は Agent 色
FACES = {
    "idle": ("( o.o )", theme.AGENT),
    "thinking": ("( -.- )", theme.AGENT),
    "running": ("( O.O )", theme.AGENT),
    "done": ("( ^.^ )", theme.SUCCESS),
    "confirm": ("( o.O )", theme.WARNING),
    "error": ("( x.x )", theme.ERROR),
    "sleep": ("( -.- )", theme.MUTED),
}
COMPACT_BELOW = 100  # これより狭い端末では 1 行に縮める（タブ行の幅を確保するため）


def lines(state: str) -> list[tuple[str, str]]:
    """3 行の Neko を (文字列, 色) で返す。sleep は全体を Muted、耳の横に z。"""
    face, color = FACES[state]
    if state == "sleep":
        return [(EARS[:-1] + "z", theme.MUTED), (face, theme.MUTED), (MOUTH, theme.MUTED)]
    mouth = " > ? < " if state == "confirm" else MOUTH
    return [(EARS, theme.AGENT), (face, color), (mouth, theme.AGENT)]


def compact(state: str) -> Text:
    """1 行版：`( o.o )` の内側の空白を詰めた `(o.o)`。"""
    face, color = FACES[state]
    return Text(face.replace(" ", ""), style=theme.MUTED if state == "sleep" else color)


class Neko(Widget):
    DEFAULT_CSS = "Neko { width: 7; height: 3; }"

    state: reactive[str] = reactive("idle")

    def render(self) -> Text:
        return Text("\n").join(Text(s, style=c) for s, c in lines(self.state))
