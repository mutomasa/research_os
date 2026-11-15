"""Papers 画面の Inbox（design.md §2.1「Inbox」・DESIGN.md §6.2）。

一覧（左）とプレビュー（右）。一覧の論文を 読む / 読了 / 中核 / 捨てる＋理由 で判断する。
判断は data 層の PaperStore.decide に任せ、上限や遷移の誤りはトーストで伝える。
"""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.events import Resize
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option

from research_os.data import intake
from research_os.data.papers import DISMISS_REASONS, InvalidTransition, LimitReached, PaperStore
from research_os.data.profile import IntakeConfig, ResearchProfile
from research_os.data.venues import VenueRegistry
from research_os.tui import theme


@dataclass
class PapersContext:
    store: PaperStore
    profile: ResearchProfile
    registry: VenueRegistry


# [ / ] で切り替える一覧（UI ラベルは英語、DESIGN.md §1）
VIEWS = [("inbox", "Inbox"), ("to_read", "To read"), ("read", "Read"), ("core", "Core")]
DECISIONS = {"to_read": "読む", "read": "読了", "core": "中核", "dismissed": "捨てる"}
DISMISS_LABELS = {
    "irrelevant": "関係ない",
    "known": "既知（ライブラリに入れる）",
    "outdated": "古い",
    "low_quality": "質が低い",
    "other": "その他",
}
PREVIEW_BELOW = 100  # これより狭い端末ではプレビューを隠す（DESIGN.md §6.2）
METER_CELLS = 4
SCORE_TABLE_WIDTH = 40  # プレビュー（120 列で約 42 列）に収まる幅


def meter(n: int, target: int) -> Text:
    """中核論文の数を ▰▱ の 4 マスで表す（RQ の飽和メーター）。"""
    filled = min(METER_CELLS, round(METER_CELLS * n / target)) if target else 0
    return Text("▰" * filled, style=theme.SUCCESS) + Text("▱" * (METER_CELLS - filled), style=theme.NEUTRAL_200)


def summary(ctx: PapersContext, now: datetime) -> Text:
    """Inbox  今週 7/10 · 未処理 4 · 読む 3/5    RQ1 ▰▰▱▱ …"""
    cfg, store = ctx.profile.intake, ctx.store
    week = store.surfaced_since(intake.week_start(now))
    line = Text()
    line.append(f"今週 {week}/{cfg.inbox_weekly_total}", style=theme.FOREGROUND)
    line.append(" · ", style=theme.MUTED)
    line.append(f"未処理 {store.count('inbox')}", style=theme.FOREGROUND)
    line.append(" · ", style=theme.MUTED)
    to_read = store.count("to_read")
    line.append(f"読む {to_read}/{cfg.to_read_max}", style=theme.WARNING if to_read >= cfg.to_read_max else theme.FOREGROUND)
    line.append("    ")
    for rq in ctx.profile.research_questions:
        line.append(f" {rq.id} ", style=theme.MUTED)
        line += meter(store.count("core", rq.id), cfg.core_target)
    return line


def item(row: sqlite3.Row, venue: str, cursor: bool, width: int, config: IntakeConfig) -> Text:
    """1 論文 = 2 行。1 行目はスコア・原題・掲載先（右寄せ）、2 行目はスコアの内訳（DESIGN.md §5.2）。

    行は折り返さず、表示幅で切って … を付ける（§7.3）。
    """
    bar = Text("▌", style=theme.PRIMARY) if cursor else Text(" ")
    score = Text(f"{row['score'] or 0:.2f}  ", style=theme.ACCENT)
    where = Text(f"  {venue} {row['year'] or ''}".rstrip(), style=theme.MUTED)
    title = Text(row["title"], style=f"bold {theme.FOREGROUND}" if cursor else theme.FOREGROUND)
    title.truncate(max(width - bar.cell_len - score.cell_len - where.cell_len, 1), overflow="ellipsis")
    gap = Text(" " * max(width - bar.cell_len - score.cell_len - title.cell_len - where.cell_len, 0))
    reason = row["breakdown"] and intake.format_reason(json.loads(row["breakdown"]), config)
    sub = bar + Text("      " + (reason or row["paper_id"]), style=theme.MUTED)
    sub.truncate(width, overflow="ellipsis")
    return Text("\n").join([bar + score + title + gap + where, sub])


def preview(row: sqlite3.Row | None, venue: str, config: IntakeConfig) -> Text:
    if row is None:
        return Text("論文を選ぶとここに詳細を表示します", style=theme.MUTED)
    body = Text(row["title"], style=f"bold {theme.FOREGROUND}")
    body.append(f"\n{venue} {row['year'] or ''} · ", style=theme.MUTED)
    body.append(row["paper_id"], style=theme.ACCENT)
    authors = json.loads(row["authors"] or "[]")
    if authors:
        more = f" ほか {len(authors) - 3} 名" if len(authors) > 3 else ""
        body.append("\n" + ", ".join(authors[:3]) + more, style=theme.MUTED)
    if row["breakdown"]:
        parts = json.loads(row["breakdown"])
        body.append("\n\n")
        body += score_table(parts, row["score"] or 0, venue, config)
        if parts.get("llm_reason"):
            body.append("\n" + parts["llm_reason"], style="#a9b1d6")
    if row["abstract"]:
        body.append("\n\n" + row["abstract"], style="#a9b1d6")
    return body


def cell(text: str, width: int, justify: str = "left", style: str = theme.MUTED) -> Text:
    """表示幅 width に切り詰め・埋める（全角は 2 列、DESIGN.md §7.3）。"""
    t = Text(text, style=style)
    t.truncate(width, overflow="ellipsis")
    t.align(justify, width)
    return t


def score_table(parts: dict, score: float, venue: str, config: IntakeConfig) -> Text:
    """スコアの内訳を「項目・根拠・加点」の表にし、加点の合計がスコアになることを示す。"""
    rule = Text("─" * SCORE_TABLE_WIDTH, style=theme.NEUTRAL_200)
    rows = intake.score_rows(parts, config, venue)
    lines = [cell(f"スコア {score:.2f}", SCORE_TABLE_WIDTH, style=f"bold {theme.FOREGROUND}"), rule]
    for label, detail, points in rows:
        lines.append(cell(label, 16, style=theme.FOREGROUND) + cell(detail, 18)
                     + cell(f"+{points:.2f}", SCORE_TABLE_WIDTH - 34, "right", theme.ACCENT))
    capped = "（上限）" if sum(p for *_, p in rows) > 1 else ""
    lines += [rule, cell("合計" + capped, 34, style=theme.FOREGROUND)
              + cell(f"{score:.2f}", SCORE_TABLE_WIDTH - 34, "right", theme.ACCENT)]
    return Text("\n").join(lines)


class DismissScreen(ModalScreen[str | None]):
    """捨てる理由を選ぶ（paper_intake.md §3.3。理由は必須）。"""

    BINDINGS = [
        *(Binding(str(i), f"choose('{r}')", show=False) for i, r in enumerate(DISMISS_REASONS, 1)),
        Binding("escape,q", "choose(None)", show=False),
    ]
    DEFAULT_CSS = """
    DismissScreen { align: center middle; }
    DismissScreen > Static {
        width: auto; height: auto; padding: 0 1;
        border: double $warning; background: $surface;
    }
    """

    def __init__(self, title: str):
        super().__init__()
        self.paper_title = title

    def compose(self) -> ComposeResult:
        body = Text(self.paper_title + "\n\n", style=f"bold {theme.FOREGROUND}")
        for i, r in enumerate(DISMISS_REASONS, 1):
            body.append(f"{i} ", style=theme.ACCENT)
            body.append(DISMISS_LABELS[r] + "\n", style=theme.FOREGROUND)
        box = Static(body)
        box.border_title = "捨てる理由"
        box.border_subtitle = "1–5 選ぶ  esc 取消"
        yield box

    def action_choose(self, reason: str | None) -> None:
        self.dismiss(reason)


class PaperList(OptionList):
    BINDINGS = [
        Binding("j", "cursor_down", show=False),
        Binding("k", "cursor_up", show=False),
        Binding("g", "first", show=False),
        Binding("G", "last", show=False),
        Binding("r", "decide('to_read')", "読む"),
        Binding("e", "decide('read')", "読了"),
        Binding("c", "decide('core')", "中核"),
        Binding("d", "decide('dismissed')", "捨てる"),
        Binding("left_square_bracket", "view(-1)", show=False),
        Binding("right_square_bracket", "view(1)", show=False),
    ]

    class Decide(Message):
        def __init__(self, status: str):
            super().__init__()
            self.status = status

    class View(Message):
        def __init__(self, step: int):
            super().__init__()
            self.step = step

    class Resized(Message):
        pass

    def on_resize(self, event: Resize) -> None:
        # 行は一覧の幅に合わせて切るので、幅が決まる・変わるたびに描き直してもらう
        self.post_message(self.Resized())

    def action_decide(self, status: str) -> None:
        self.post_message(self.Decide(status))

    def action_view(self, step: int) -> None:
        self.post_message(self.View(step))


class PapersView(Horizontal):
    DEFAULT_CSS = """
    PapersView > Vertical, PapersView > VerticalScroll {
        border: round $neutral-200; border-title-color: $primary; padding: 0 1;
    }
    PapersView > Vertical { width: 3fr; }
    PapersView > Vertical:focus-within { border: round $primary; }
    PapersView > VerticalScroll { width: 2fr; }
    PapersView #inbox-summary { height: 1; margin-bottom: 1; }
    PapersView PaperList { height: 1fr; border: none; padding: 0; background: $background; }
    PapersView PaperList:focus { border: none; background-tint: $foreground 0%; }
    PapersView PaperList > .option-list--option-highlighted { background: $selection; }
    PapersView PaperList:focus > .option-list--option-highlighted { background: $selection; }
    PapersView #empty { color: $muted; }
    """

    view: reactive[str] = reactive("inbox", init=False)

    def __init__(self, ctx: PapersContext, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.rows: list[sqlite3.Row] = []
        self.labels = {v.venue_id: v.label for v in ctx.registry.venues}
        self._cursor: int | None = None

    def compose(self) -> ComposeResult:
        with Vertical(id="inbox-panel"):
            yield Static(id="inbox-summary")
            yield PaperList(id="paper-list")
            yield Static(id="empty")
        with VerticalScroll(id="preview-panel"):
            yield Static(id="preview")

    def on_mount(self) -> None:
        self.query_one("#inbox-panel").border_subtitle = "j/k 移動  r 読む  e 読了  c 中核  d 捨てる  [ ] 一覧"
        self.query_one("#preview-panel").border_title = "Preview"
        self.reload()

    def on_resize(self, event: Resize) -> None:
        self.query_one("#preview-panel").display = self.app.size.width >= PREVIEW_BELOW

    def on_paper_list_resized(self, event: PaperList.Resized) -> None:
        self._redraw_items()

    def _item(self, index: int) -> Text:
        row = self.rows[index]
        width = self.query_one(PaperList).scrollable_content_region.width
        return item(row, self._venue(row), index == self._cursor, width or 80, self.ctx.profile.intake)

    def _redraw_items(self) -> None:
        """一覧の幅が決まって（変わって）から、行を幅に合わせて描き直す。"""
        plist = self.query_one(PaperList)
        for i in range(len(self.rows)):
            plist.replace_option_prompt_at_index(i, self._item(i))

    def watch_view(self) -> None:
        self.reload()

    def _venue(self, row: sqlite3.Row) -> str:
        return self.labels.get(row["venue_id"], row["venue_name"] or "-")

    def reload(self, keep: int = 0) -> None:
        self.rows = self.ctx.store.papers(self.view)
        label = dict(VIEWS)[self.view]
        panel = self.query_one("#inbox-panel")
        panel.border_title = f"{label} ({len(self.rows)})"
        self.query_one("#inbox-summary", Static).update(summary(self.ctx, datetime.now()))
        plist = self.query_one(PaperList)
        self._cursor = None
        plist.set_options(Option(self._item(i), id=r["paper_id"]) for i, r in enumerate(self.rows))
        empty = self.query_one("#empty", Static)
        empty.display = not self.rows
        if self.view == "inbox":
            empty.update("Inbox は空です。research-os intake run で取り込みます")
        else:
            empty.update(f"{label} の論文はまだありません")
        if self.rows:
            plist.highlighted = min(keep, len(self.rows) - 1)
        else:
            self.query_one("#preview", Static).update(preview(None, "", self.ctx.profile.intake))

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        plist = self.query_one(PaperList)
        # カーソル行だけ左端に ▌ を出す（§5.2）。前の行は元に戻す
        previous, self._cursor = self._cursor, event.option_index
        if previous is not None and previous < len(self.rows):
            plist.replace_option_prompt_at_index(previous, self._item(previous))
        plist.replace_option_prompt_at_index(self._cursor, self._item(self._cursor))
        row = self.rows[self._cursor]
        self.query_one("#preview", Static).update(preview(row, self._venue(row), self.ctx.profile.intake))

    def on_paper_list_view(self, event: PaperList.View) -> None:
        keys = [k for k, _ in VIEWS]
        self.view = keys[(keys.index(self.view) + event.step) % len(keys)]

    def on_paper_list_decide(self, event: PaperList.Decide) -> None:
        index = self.query_one(PaperList).highlighted
        if index is None or not self.rows:
            return
        row = self.rows[index]
        if event.status == "dismissed":
            def chosen(reason: str | None) -> None:
                if reason:
                    self._decide(index, row, "dismissed", reason)

            self.app.push_screen(DismissScreen(row["title"]), chosen)
        else:
            self._decide(index, row, event.status)

    def _decide(self, index: int, row: sqlite3.Row, status: str, reason: str | None = None) -> None:
        try:
            self.ctx.store.decide(row["paper_id"], status, datetime.now(), self.ctx.profile.intake.to_read_max,
                                  reason=reason)
        except (InvalidTransition, LimitReached) as e:
            # エラーは手動で閉じるまで残す（DESIGN.md §5.8。トーストはクリックで閉じる）
            self.app.notify(str(e), severity="error", timeout=600)
            return
        action = DECISIONS[status] + (f"（{DISMISS_LABELS[reason]}）" if reason else "")
        self.app.notify(f"✓ {row['title']} → {action}", timeout=4)
        self.reload(keep=index)

    def focus_list(self) -> None:
        self.query_one(PaperList).focus()
