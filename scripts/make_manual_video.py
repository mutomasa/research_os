"""TUI の操作説明動画を作る（絵コンテ：docs/manual/storyboard.md）。

    uv run python scripts/make_manual_video.py [--out docs/assets/manual.mp4] [--work DIR]

1. サンプルの論文 DB を一時ディレクトリに作り、Textual の Pilot で TUI を実際に操作する
2. 場面ごとに画面を SVG に書き出し、説明するウィジェットの領域（セル単位）を記録する
3. SVG に赤枠（と枠の外を暗くする覆い）を描き足し、画面下に説明を付けた HTML を
   headless Chrome で 1920×1080 の PNG にする
4. ffmpeg で場面をフェードでつないで mp4（H.264・30fps）にする

必要なもの：google-chrome（または chromium）と ffmpeg。
"""

import argparse
import asyncio
import html
import re
import json
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from rich.cells import cell_len
from textual.geometry import Region
from textual.pilot import Pilot

from research_os import __version__
from research_os.data import intake, profile, venues
from research_os.data.papers import PaperRecord, PaperStore
from research_os.tui.app import ResearchOSApp
from research_os.tui.papers import PapersContext

ROOT = Path(__file__).resolve().parents[1]
COLS, ROWS = 120, 36

# Rich の SVG 書き出しの寸法（font-size 20px）。端末の 1 セル = 12.2 × 24.4、
# 画面の左上はウィンドウ枠の分だけずれて <g transform="translate(9, 41)"> の 1 行目（y = 1.5）にある
CELL_W, CELL_H = 12.2, 24.4
ORIGIN_X, ORIGIN_Y = 9.0, 42.5
TEXT_RE = re.compile(r'(<text [^>]*?textLength=")([0-9.]+)("[^>]*>)([^<]*)(</text>)')

WIDTH, HEIGHT, FPS, FADE = 1920, 1080, 30, 0.4
RED = "#ff3b30"

GAP_RQ1 = 1 - 1 / 15  # RQ1 には中核論文が 1 本ある（下の core）。gap = 1 − 中核数 / core_target

# 動画用のサンプル論文（実在の論文ではない。DOI はテスト用の 10.5555 を使う）
SAMPLE = [
    ("Tactile World Models for Predicting Slip in Long-Horizon Manipulation", "ral", 2025, "RQ2",
     dict(relevance=0.92, venue=1.0, gap=1.0, velocity=0.7, citations_per_year=14.0, venue_priority=1,
          relevance_source="llm", llm_reason="触覚から滑りを予測する世界モデルで、RQ2 の失敗予兆の検出に直結する"),
     "inbox"),
    ("Visuo-Tactile JEPA: Self-Supervised Representations for Contact-Rich Tasks", "icra", 2025, "RQ1",
     dict(relevance=0.85, venue=0.9, gap=GAP_RQ1, velocity=0.5, citations_per_year=9.0, venue_priority=2,
          relevance_source="llm", llm_reason="視覚と触覚を JEPA で統合する表現学習で、RQ1 の中心テーマ"),
     "inbox"),
    ("Failure-Aware Recovery Policies with Learned Dynamics", "iros", 2024, "RQ3",
     dict(relevance=0.74, venue=0.8, gap=1.0, velocity=0.4, citations_per_year=6.0, venue_priority=3,
          relevance_source="llm", llm_reason="失敗から回復する方策を学習済みダイナミクスで計画する。RQ3 の比較対象"),
     "inbox"),
    ("Contact-Implicit World Models for In-Hand Reorientation", "tro", 2024, "RQ2",
     dict(relevance=0.58, venue=0.7, gap=1.0, velocity=0.6, citations_per_year=11.0, venue_priority=5,
          relevance_source="keyword"),
     "inbox"),
    ("Benchmarking Long-Horizon Manipulation under Sensor Noise", "rss", 2023, "RQ3",
     dict(relevance=0.46, venue=0.7, gap=1.0, velocity=0.3, citations_per_year=4.0, venue_priority=4,
          relevance_source="keyword"),
     "inbox"),
    ("Slip Detection from High-Resolution Tactile Images", "ral", 2023, "RQ2",
     dict(relevance=0.33, venue=1.0, gap=1.0, velocity=0.2, citations_per_year=3.0, venue_priority=1,
          relevance_source="keyword"),
     "inbox"),
    ("Latent Dynamics for Deformable Object Manipulation", "icra", 2024, "RQ1",
     dict(relevance=0.70, venue=0.9, gap=GAP_RQ1, velocity=0.5, citations_per_year=8.0, venue_priority=2,
          relevance_source="llm", llm_reason="潜在空間でのダイナミクス学習。RQ1 の基礎文献"),
     "core"),
]


def make_context(work: Path, now: datetime) -> PapersContext:
    prof = profile.load_profile(ROOT / "research/profile.yaml")
    registry = venues.load_venues(ROOT / "registry/venues.yaml")
    labels = {v.venue_id: v.label for v in registry.venues}
    store = PaperStore(work / "papers.db")
    for i, (title, venue, year, rq, parts, status) in enumerate(SAMPLE):
        parts = {**parts, "primary_rq": rq}
        score = min(1.0, sum(p for *_, p in intake.score_rows(parts, prof.intake, labels[venue])))
        pid = store.upsert(PaperRecord(title=title, doi=f"10.5555/demo.{i}", venue_id=venue, year=year,
                                       abstract="（サンプルデータ）We propose a method for robotic manipulation …",
                                       authors=["A. Sato", "B. Tanaka", "C. Suzuki", "D. Ito"]),
                           "openalex", None, None, now)
        store.db.execute("UPDATE triage SET status=?, score=?, primary_rq=?, breakdown=?, surfaced_at=? "
                         "WHERE paper_id=?", (status, score, rq, json.dumps(parts), now.isoformat(), pid))
        store.db.execute("INSERT OR REPLACE INTO paper_rq (paper_id, rq_id, relevance) VALUES (?, ?, ?)",
                         (pid, rq, parts["relevance"]))
    store.commit()
    return PapersContext(store, prof, registry)


# ---------------------------------------------------------------- 場面

Action = Callable[[ResearchOSApp, Pilot], Awaitable[None]]
Box = Callable[[ResearchOSApp], Region | None]


@dataclass
class Scene:
    title: str
    body: str
    keys: str = ""  # 説明に添えるキー（表示のみ）
    action: Action | None = None  # 画面を撮る前に行う操作
    box: Box | None = None  # 赤枠で囲む領域（None なら枠なし）
    seconds: float = 5.5
    after: Action | None = None  # 撮った後の後始末（モーダルを閉じるなど）
    svg: str = field(default="", repr=False)
    region: Region | None = None


def widget(selector: str) -> Box:
    return lambda app: app.screen.query_one(selector).region


def toast(app: ResearchOSApp) -> Region | None:
    toasts = app.screen.query("Toast")
    return toasts.last().region if toasts else None


def modal(app: ResearchOSApp) -> Region:
    return app.screen.query_one("Static").region


def keys(*names: str) -> Action:
    async def act(app: ResearchOSApp, pilot: Pilot) -> None:
        await pilot.press(*names)
    return act


async def ask_agent(app: ResearchOSApp, pilot: Pilot) -> None:
    await pilot.press("i")
    app.screen.query_one("#agent-input").value = "今週の Inbox"
    await pilot.press("enter")


def scenes() -> list[Scene]:
    return [
        Scene("画面の構成",
              "research-os tui で起動します。上から ヘッダ・フェーズタブ・メイン画面・Agent 欄・ステータスバー。"
              "（論文はサンプルデータ）",
              keys="research-os tui", box=lambda app: Region(0, 0, COLS, ROWS), seconds=6.5),
        Scene("ヘッダ", "アプリ名・研究テーマ（research/profile.yaml）・バージョン・時刻を表示します。",
              box=widget("#header")),
        Scene("フェーズタブ",
              "研究のフェーズ（Papers → Review → Graph → Hypothesis → Run → Paper）と、並走する Intel。"
              "数字キーで切り替えます。",
              keys="1 – 7", box=widget("#tabs")),
        Scene("Neko", "Agent の状態を顔で表します。考え中・実行中・完了・確認待ち・失敗・居眠り。",
              box=widget("#neko")),
        Scene("Inbox の集計",
              "今週取り込んだ数 / 上限、未処理の数、「読む」の枠、RQ ごとの中核論文の充足（▰▱）。",
              box=widget("#inbox-summary")),
        Scene("Inbox の一覧",
              "OpenAlex から取り込んだ論文をスコア順に並べます。2 行目は、なぜ出てきたか（関連する RQ・投稿先・被引用）。",
              box=widget("#paper-list"), seconds=6.5),
        Scene("Preview",
              "選んだ論文の書誌、スコアの内訳表（項目・根拠・加点）、LLM の判定理由、要旨。",
              box=widget("#preview-panel"), seconds=6.5),
        Scene("カーソルの移動", "j / k で上下に移動すると、Preview が追従します。g / G で先頭 / 末尾。",
              keys="j  k  g  G", action=keys("j"), box=widget("#paper-list")),
        Scene("判断する：読む",
              "r で「読む」へ移します。e は読了、c は中核。結果はトーストで知らせます（v0.1.2 では右下に出ます。#30）。",
              keys="r  e  c", action=keys("r"), box=toast),
        Scene("判断する：捨てる", "d で捨てるときは理由を 1〜5 で選びます（理由は必須）。esc で取り消し。",
              keys="d → 1–5", action=keys("d"), box=modal, after=keys("1")),
        Scene("一覧の切り替え", "[ / ] で Inbox → To read → Read → Core を切り替えます。",
              keys="[  ]", action=keys("right_square_bracket"), box=widget("#inbox-panel"),
              after=keys("left_square_bracket")),
        Scene("Agent 欄",
              "i（または >）で指示を入力します。↑↓ で履歴、tab で提案を補完、esc でメインに戻ります。"
              "v0.1.2 では Agent コアは未接続です。",
              keys="i  enter  esc", action=ask_agent, box=widget("#agent"), seconds=6.5, after=keys("escape")),
        Scene("ステータスバー", "外部との接続の状態（Paperpile・arXiv・alphaXiv・GitHub・Feeds・MCP）を表示します。",
              box=widget("#status")),
        Scene("ヘルプ", "? でキー操作の一覧を開きます。", keys="?", action=keys("question_mark"),
              box=lambda app: app.screen.query("*").first().region, after=keys("escape")),
        Scene("ほかのフェーズ",
              "2 で Review へ。Review 以降の画面は今後実装します（docs/todo.md）。q で終了。",
              keys="2  q", action=keys("2"), box=widget("#main")),
    ]


async def capture(app: ResearchOSApp, plan: list[Scene]) -> None:
    # run_test は既定でトーストを出さない。判断の結果を見せるので有効にする
    async with app.run_test(size=(COLS, ROWS), notifications=True) as pilot:
        await pilot.pause(0.3)
        for scene in plan:
            if scene.action:
                await scene.action(app, pilot)
            await pilot.pause(0.3)
            scene.svg = app.export_screenshot(title=f"Research OS v{__version__}")
            scene.region = scene.box(app) if scene.box else None
            if scene.after:
                await scene.after(app, pilot)
                await pilot.pause(0.2)


# ---------------------------------------------------------------- 描画

def fix_wide_text(svg: str) -> str:
    """書き出しの textLength は文字数 × セル幅なので、全角が半分の幅に詰められて重なる。
    表示幅（全角 = 2 列）× セル幅に直す。x 座標はもともと表示幅で計算されている。"""
    def repl(m: re.Match) -> str:
        width = cell_len(html.unescape(m.group(4))) * CELL_W
        return f"{m.group(1)}{width:.1f}{m.group(3)}{m.group(4)}{m.group(5)}"
    return TEXT_RE.sub(repl, svg)


def annotate(svg: str, region: Region | None) -> str:
    """赤枠と、枠の外を暗くする覆いを SVG に描き足す。"""
    svg = fix_wide_text(svg)
    if region is None:
        return svg
    w, h = COLS * CELL_W, ROWS * CELL_H
    x, y = region.x * CELL_W, region.y * CELL_H
    rw, rh = region.width * CELL_W, region.height * CELL_H
    pad = 3
    overlay = (
        f'<g transform="translate({ORIGIN_X},{ORIGIN_Y})">'
        f'<path fill="#000" fill-opacity="0.62" fill-rule="evenodd" '
        f'd="M0 0H{w}V{h}H0Z M{x} {y}h{rw}v{rh}h{-rw}Z"/>'
        f'<rect x="{x - pad}" y="{y - pad}" width="{rw + 2 * pad}" height="{rh + 2 * pad}" rx="6" '
        f'fill="none" stroke="{RED}" stroke-width="5"/></g>'
    )
    return svg.replace("</svg>", overlay + "</svg>")


PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;background:#0f1117;
  font-family:"Noto Sans CJK JP","Noto Sans JP",sans-serif;color:#e6e8ef}}
.screen{{position:absolute;top:22px;left:0;right:0;height:840px;display:flex;justify-content:center}}
.screen svg{{height:100%;width:auto}}
.cap{{position:absolute;left:0;right:0;bottom:0;height:196px;background:#161925;
  border-top:4px solid {RED};box-sizing:border-box;padding:26px 96px;display:flex;gap:40px;align-items:center}}
.step{{font:700 30px "DejaVu Sans Mono",monospace;color:#8b93b5;min-width:110px}}
.txt{{flex:1}}
.title{{font-size:42px;font-weight:700;margin-bottom:10px}}
.body{{font-size:29px;line-height:1.5;color:#c9cee0}}
.key{{font:600 28px "DejaVu Sans Mono",monospace;color:#fff;background:#2b3046;border:2px solid #4a5175;
  border-radius:10px;padding:10px 20px;white-space:nowrap}}
.card{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;padding:0 160px}}
.card h1{{font-size:88px;margin:0 0 18px}} .card h2{{font-size:40px;color:#8b93b5;font-weight:400;margin:0 0 48px}}
.card p{{font-size:32px;line-height:1.7;color:#c9cee0;margin:0}}
.card code{{font-family:"DejaVu Sans Mono",monospace;color:#9ece6a}}
.bar{{width:160px;height:8px;background:{RED};margin-bottom:40px}}
</style></head><body>{content}</body></html>"""


def scene_page(scene: Scene, index: int, total: int) -> str:
    key = f'<div class="key">{html.escape(scene.keys)}</div>' if scene.keys else ""
    content = (
        f'<div class="screen">{annotate(scene.svg, scene.region)}</div>'
        f'<div class="cap"><div class="step">{index:02d} / {total:02d}</div>'
        f'<div class="txt"><div class="title">{html.escape(scene.title)}</div>'
        f'<div class="body">{html.escape(scene.body)}</div></div>{key}</div>'
    )
    return PAGE.format(W=WIDTH, H=HEIGHT, RED=RED, content=content)


def card_page(title: str, subtitle: str, lines: list[str]) -> str:
    body = "".join(f"<p>{line}</p>" for line in lines)
    content = f'<div class="card"><div class="bar"></div><h1>{title}</h1><h2>{subtitle}</h2>{body}</div>'
    return PAGE.format(W=WIDTH, H=HEIGHT, RED=RED, content=content)


def chrome() -> str:
    for name in ("google-chrome", "chromium", "chromium-browser"):
        if path := shutil.which(name):
            return path
    sys.exit("google-chrome / chromium が見つかりません")


def screenshot(page: str, html_path: Path, png_path: Path) -> None:
    html_path.write_text(page, encoding="utf-8")
    subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size={WIDTH},{HEIGHT}", f"--screenshot={png_path}", html_path.as_uri()],
                   check=True, capture_output=True)


def encode(frames: list[tuple[Path, float]], out: Path) -> None:
    """静止画を場面ごとの長さで並べ、FADE 秒のクロスフェードでつなぐ。"""
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for png, seconds in frames:
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{seconds}", "-i", str(png)]
    chain, last, offset = [], "[0:v]", 0.0
    for i in range(1, len(frames)):
        offset += frames[i - 1][1] - FADE
        label = f"[v{i}]"
        chain.append(f"{last}[{i}:v]xfade=transition=fade:duration={FADE}:offset={offset:.3f}{label}")
        last = label
    total = offset + frames[-1][1]
    chain.append(f"{last}fade=t=in:d=0.5,fade=t=out:st={total - 0.6:.3f}:d=0.6,format=yuv420p[out]")
    cmd += ["-filter_complex", ";".join(chain), "-map", "[out]", "-r", str(FPS),
            "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=ROOT / "docs/assets/manual.mp4")
    parser.add_argument("--work", type=Path, help="中間ファイル（SVG・HTML・PNG）を残す場所")
    args = parser.parse_args()

    work = args.work or Path(tempfile.mkdtemp(prefix="manual-video-"))
    work.mkdir(parents=True, exist_ok=True)
    ctx = make_context(work, datetime.now())
    plan = scenes()
    app = ResearchOSApp(research_theme=ctx.profile.theme, papers=ctx)
    asyncio.run(capture(app, plan))
    ctx.store.close()

    frames: list[tuple[Path, float]] = []

    def add(name: str, page: str, seconds: float) -> None:
        png = work / f"{name}.png"
        screenshot(page, work / f"{name}.html", png)
        frames.append((png, seconds))
        print(f"  {png.name}", file=sys.stderr)

    add("00-title", card_page("Research OS", f"操作ガイド  v{__version__}", [
        "検索 → 読解 → 比較 → 仮説化 → 実験 を 1 つの TUI で回す研究開発 IDE",
        "この動画では Papers の Inbox を中心に、画面の見方とキー操作を説明します"]), 4.0)
    for i, scene in enumerate(plan, 1):
        add(f"{i:02d}-scene", scene_page(scene, i, len(plan)), scene.seconds)
    add("99-cli", card_page("CLI でも使えます", "論文の取り込みと判断", [
        "<code>research-os intake run</code>　Venue × 研究テーマで OpenAlex から取り込み、スコアを付けて Inbox へ",
        "<code>research-os intake explore</code>　中核論文の参考文献・被引用から候補を広げる",
        "<code>research-os inbox</code>　Inbox を一覧（TUI と同じ理由の 1 行）",
        "<code>research-os triage &lt;paper_id&gt; to_read</code>　判断を記録（dismissed は --reason が必須）",
        "<code>research-os tui</code>　この画面を開く"]), 6.0)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    encode(frames, args.out)
    print(f"wrote {args.out} ({sum(s for _, s in frames) - FADE * (len(frames) - 1):.1f}s)", file=sys.stderr)
    if not args.work:
        shutil.rmtree(work)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
