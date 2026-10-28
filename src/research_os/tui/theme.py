"""Lab Ink の配色トークンとフェーズ定義（DESIGN.md §2）。"""

from dataclasses import dataclass

from textual.theme import Theme

FOREGROUND = "#c0caf5"
PRIMARY = "#7aa2f7"
SECONDARY = "#565f89"
ACCENT = "#7dcfff"
AGENT = "#bb9af7"
SUCCESS = "#9ece6a"
WARNING = "#e0af68"
ERROR = "#f7768e"
MUTED = "#737aa2"
SURFACE = "#24283b"
SELECTION = "#2e3c64"
MARKED = "#ff9e64"
BACKGROUND = "#1a1b26"
NEUTRAL_50 = "#16161e"
NEUTRAL_200 = "#3b4261"
NEUTRAL_300 = "#565f89"


@dataclass(frozen=True)
class Phase:
    key: str  # タブ切替のキー（DESIGN.md §9.1）
    id: str
    label: str
    color: str
    track: bool = False  # 直列フローの外にある並走トラック（Intel）


PHASES = [
    Phase("1", "papers", "Papers", "#7aa2f7"),
    Phase("2", "review", "Review", "#7dcfff"),
    Phase("3", "graph", "Graph", "#73daca"),
    Phase("4", "hypothesis", "Hypothesis", "#e0af68"),
    Phase("5", "run", "Run", "#9ece6a"),
    Phase("6", "paper", "Paper", "#f4b8e4"),
    Phase("7", "intel", "Intel", "#ff9e64", track=True),
]
PHASE_BY_ID = {p.id: p for p in PHASES}

LAB_INK = Theme(
    name="lab-ink",
    primary=PRIMARY,
    secondary=SECONDARY,
    accent=ACCENT,
    foreground=FOREGROUND,
    background=BACKGROUND,
    surface=SURFACE,
    panel=SURFACE,
    success=SUCCESS,
    warning=WARNING,
    error=ERROR,
    dark=True,
    variables={
        "agent": AGENT,
        "muted": MUTED,
        "selection": SELECTION,
        "marked": MARKED,
        "neutral-50": NEUTRAL_50,
        "neutral-200": NEUTRAL_200,
        "footer-key-foreground": ACCENT,
    },
)
