# Research OS — TUI Design System

> 研究者のコックピット。夜のラボで長時間眺めても疲れない、落ち着いた「インク」系のダーク配色。
> 情報は密に、操作は Agent 欄に集め、**いまどのフェーズにいて、Agent が何をしているか** が一目で分かる TUI。

このファイルは Research OS の **見た目と操作感の規約（デザインシステム）** です。
画面の機能・アーキテクチャの正は [`docs/design.md`](docs/design.md)。本書はそれを「どう描くか」に落とし込みます。
形式は [awesome-tui-design](https://github.com/cola-runner/awesome-tui-design) の `TEMPLATE.md` に準拠し、
AI エージェント（Claude Code など）がそのまま読んで TUI 実装に使えることを目的にしています。

> TUI フレームワークは未選定（Textual / Bubble Tea など。`docs/todo.md` §0）。
> 本書はフレームワーク非依存で、色は Hex / ANSI 256 / ANSI 16 の 3 段で定義します。

---

## 目次

1. [Theme Overview](#1-theme-overview)
2. [Color Palette](#2-color-palette)
3. [Typography](#3-typography)
4. [Borders & Box Drawing](#4-borders--box-drawing)
5. [Components](#5-components)
6. [Screens](#6-screens)
7. [Layout & Spacing](#7-layout--spacing)
8. [Icons & Indicators](#8-icons--indicators)
9. [Keybindings](#9-keybindings)
10. [Animation & Motion](#10-animation--motion)
11. [Agent Prompt Guide](#11-agent-prompt-guide)
12. [Do's and Don'ts](#12-dos-and-donts)
13. [Alternate Theme: Mission Control](#13-alternate-theme-mission-control)

---

## 1. Theme Overview

- **Name**: Lab Ink
- **Mood**: 落ち着いた・知的・計器盤的（Tokyo Night 系の青紫インクに、フェーズごとの差し色）
- **Density**: Dense（一覧は 1 論文 2〜3 行、パネル間の余白は 0〜1）
- **Target**: 研究開発 IDE、文献探索、Agent 主導のワークフロー、監視ダッシュボード（Intel）
- **Terminal**: TrueColor 推奨、256 色で完全動作、16 色で機能劣化なし（色は常にアイコン・文字と併用）
- **言語**: UI ラベルは英語（タブ名・ボタン・ステータス）、本文・要約・Agent 応答は日本語
- **Alternate theme**: `Mission Control`（漆黒ネイビー + Agent 役割色。§13）を `:theme mission-control` で切替可能

**デザインの 3 原則**

1. **Agent が主役** — 画面下部の Agent 欄は常に見えていて、`>` 1 キーで入力できる。Agent の実行状態（計画・ツール呼び出し・結果）は隠さず表示する。
2. **フェーズが色で分かる** — Papers / Review / Graph / Hypothesis / Run / Intel はそれぞれ固有色を持ち、タブ・パネルタイトル・Agent の文脈表示に使う。
3. **根拠が見える** — 数値・主張・要約には必ず出典（arXiv ID / URL / `company_claimed` など）を併記する。出典のない情報を強調表示しない。

---

## 2. Color Palette

### 2.1 Semantic Roles

| Role | Hex | ANSI 256 | ANSI 16 | Usage |
|------|-----|----------|---------|-------|
| Background | `#1a1b26` | `234` | `black` | 画面背景（端末既定色を透過してもよい） |
| Foreground | `#c0caf5` | `189` | `white` | 本文・論文タイトル |
| Primary | `#7aa2f7` | `111` | `blue` | フォーカス枠、カーソル行、主要アクション |
| Secondary | `#565f89` | `60` | `bright black` | 非アクティブ枠、補助テキスト |
| Accent | `#7dcfff` | `117` | `bright cyan` | リンク、arXiv ID、キーバインド表示 |
| Agent | `#bb9af7` | `141` | `magenta` | Agent 欄の枠・プロンプト記号・思考中表示 |
| Success | `#9ece6a` | `149` | `green` | 接続 OK、完了、`third_party_verified` |
| Warning | `#e0af68` | `179` | `yellow` | 部分失敗（`Feeds 8/9`）、`company_claimed` |
| Error | `#f7768e` | `204` | `red` | 接続断、ツール失敗、バリデーションエラー |
| Muted | `#737aa2` | `103` | `bright black` | タイムスタンプ、メタ情報、ヒント |
| Surface | `#24283b` | `235` | `black` | パネル背景、Agent 欄背景 |
| Selection | `#2e3c64` | `237` | `blue`（背景） | 選択行の背景 |
| Marked | `#ff9e64` | `215` | `bright yellow` | `★` 付きの選択論文 |

### 2.2 Phase Colors（フェーズ固有色）

各研究フェーズの識別色。**タブのアクティブ表示・パネルタイトル・Agent 欄の文脈バッジにだけ使う**。
状態（成功・失敗）の表現には使わない。

| Phase | Hex | ANSI 256 | ANSI 16 | 意味づけ |
|-------|-----|----------|---------|----------|
| Papers | `#7aa2f7` | `111` | `blue` | 探す（Primary と同色） |
| Review | `#7dcfff` | `117` | `cyan` | 読む |
| Graph | `#73daca` | `79` | `bright cyan` | つなぐ |
| Hypothesis | `#e0af68` | `179` | `yellow` | 閃く |
| Run | `#9ece6a` | `149` | `green` | 試す |
| Intel | `#ff9e64` | `215` | `bright red` | 外を見る（並走トラック） |

> Hypothesis と Warning、Run と Success は同色です。フェーズ色は「タブ／タイトル」、状態色は「アイコン付きの値」に
> 用途を分けているため衝突しません。状態は必ずアイコン（§8）と併用すること。

### 2.3 Neutral Scale

| Step | Hex | ANSI 256 | Usage |
|------|-----|----------|-------|
| 50 | `#16161e` | `233` | ステータスバー背景 |
| 100 | `#24283b` | `235` | Surface |
| 200 | `#3b4261` | `238` | 非アクティブ枠、区切り線 |
| 300 | `#565f89` | `60` | 無効テキスト、プレースホルダ |
| 400 | `#737aa2` | `103` | 補助テキスト（Muted） |
| 500 | `#a9b1d6` | `146` | 二次本文（Abstract、要約） |
| 600 | `#c0caf5` | `189` | 本文（Foreground） |

### 2.4 Domain Colors

**Knowledge Graph ノード種別**（Graph 画面・インライン参照で共通）

| Node | Hex | ANSI 256 | Glyph |
|------|-----|----------|-------|
| Paper | `#c0caf5` | `189` | `▪` |
| Method | `#7aa2f7` | `111` | `●` |
| Dataset | `#73daca` | `79` | `▤` |
| Model | `#bb9af7` | `141` | `◆` |
| Task | `#9ece6a` | `149` | `▸` |
| Robot | `#ff9e64` | `215` | `⚙` |
| Metric | `#e0af68` | `179` | `%` |
| Research Problem | `#f7768e` | `204` | `?` |
| Company | `#ff9e64` | `215` | `■` |
| Product | `#e0af68` | `179` | `▣` |
| Customer | `#9ece6a` | `149` | `◎` |
| Event | `#7dcfff` | `117` | `◷` |

**情報の信頼性**（Intel・数値の併記）

| 値 | 表示 | 色 |
|----|------|----|
| `company_claimed` | `◐ claim` | Warning |
| `third_party_verified` | `● verified` | Success |
| 不明・未確認 | `○ unverified` | Muted |

**論文の既読状態**（関心フィード、design.md §3.2）

| status | 表示 | 色・装飾 |
|--------|------|----------|
| `new` | `NEW` | Primary 背景 + Background 文字（reverse） |
| `seen` | （バッジなし） | 本文を Neutral 500 |
| `saved` | `✓ saved` | Success |
| `dismissed` | 行ごと非表示（`d` で表示切替時は dim + 取消線） | Neutral 300 |

---

## 3. Typography

- **Header font**: figlet は使わない。ヘッダは 1 行のプレーンテキスト（起動スプラッシュのみ小さなロゴ可）
- **Body**: 端末の等幅フォント。日本語は全角（表示幅 2）として扱う
- **Emphasis**: `bold`（見出し・タイトル）、`dim`（メタ情報）、`italic`（Agent の思考・引用。非対応端末では dim で代替）、`underline`（リンク・arXiv ID）
- **原語保持**: 論文タイトル・専門用語・モデル名は原語のまま。日本語訳はその下の行に置く

### Text Hierarchy

| Level | Style | Example Usage |
|-------|-------|---------------|
| App title | BOLD + Primary | `Research OS` |
| Tab (active) | BOLD + Phase color + 下線マーカー `▔▔▔` | `Papers` |
| Tab (inactive) | Muted | `Review` |
| Panel title | BOLD + Phase color（枠に埋め込み） | `╭─ Results (37) ─` |
| Item title | BOLD + Foreground | 論文タイトル（原題） |
| Item subtitle | Neutral 500 | 日本語タイトル・要約 1 行 |
| Meta | Muted | `2025 · arXiv · 2509.01234` |
| Tag | Accent（`#` 前置） | `#VLA #JEPA` |
| Agent prompt | BOLD + Agent | `❯ Compare these papers` |
| Agent output | Foreground | 日本語の回答本文 |
| Caption / hint | dim + Muted | `enter 開く  space 選択` |

---

## 4. Borders & Box Drawing

### 4.1 Primary Border（パネル）

角丸。タイトルは上辺に埋め込み、件数・位置は右端に置く（lazygit 流）。

```
╭─ Results (37) ────────────────── 3 of 37 ─╮
│ content                                   │
╰───────────────────────────────────────────╯
```

| Part | Character | ASCII fallback |
|------|-----------|----------------|
| top_left | `╭` | `+` |
| top_right | `╮` | `+` |
| bottom_left | `╰` | `+` |
| bottom_right | `╯` | `+` |
| horizontal | `─` | `-` |
| vertical | `│` | `\|` |
| cross | `┼` | `+` |
| tee_down | `┬` | `+` |
| tee_up | `┴` | `+` |
| tee_right | `├` | `+` |
| tee_left | `┤` | `+` |

### 4.2 Border States

| 状態 | 枠 | タイトル |
|------|----|----------|
| フォーカス中のパネル | Phase color + bold | Phase color + bold |
| 非フォーカス | Neutral 200 | Muted |
| Agent 欄（待機） | Neutral 200 | Agent |
| Agent 欄（入力中・実行中） | Agent + bold | Agent + bold |
| エラーを含むパネル | Error | Error + `✗` |

### 4.3 Secondary Border（ダイアログ・確認）

外部に書き込む操作（Paperpile 登録、alphaXiv フォルダ保存、実験実行）の確認は **二重線** で目立たせる。

```
╔═ Add 3 papers to Paperpile? ═════════════╗
║                                          ║
║  ★ VLA-JEPA                              ║
║  ★ Tactile World Model                   ║
║  ★ Vision-Tactile Policy                 ║
║                                          ║
║        [ Y  Add ]    [ n  Cancel ]       ║
╚══════════════════════════════════════════╝
```

### 4.4 Dividers

- パネル内のセクション区切り：`─` を Neutral 200 で全幅
- 一覧のアイテム間：区切り線なし（空行 0、アイテムは 2〜3 行のまとまり）
- 見出し付き区切り：`── Similarities ──────────`（見出しは bold）

---

## 5. Components

### 5.1 Header + Phase Tabs

1 行目がヘッダ、2 行目がタブ。アクティブタブは Phase color で表示し、直下に `▔` のマーカー。
Intel は並走トラックなので `│` で区切って右側に置く。

```
 Research OS  ·  vision tactile world model                        2026-10-01 09:12
 1 Papers   2 Review   3 Graph   4 Hypothesis   5 Run   │   6 Intel ●3
 ▔▔▔▔▔▔▔▔
```

- 番号はキーバインド（§9）。番号は Muted、ラベルはアクティブ時 bold + Phase color
- タブ横の `●3` は未読件数（Intel の新着、Papers の関心フィード新着）。Marked 色
- ヘッダ中央は **現在の研究テーマ**（design.md §1 の③）。長い場合は `…` で省略

### 5.2 Paper List Item

1 論文 = 2〜3 行。1 行目は原題、2 行目にメタ、3 行目に日本語訳（関心フィードの場合）またはタグ。

```
 ▌★ VLA-JEPA                                                    NEW
 ▌  2025 · arXiv 2509.01234 · Paperpile ✓
 ▌  視覚・言語・行動を JEPA で統合した世界モデル     #VLA #JEPA
   ★ Tactile World Model
     2026 · Paperpile
     #Tactile #Manipulation
     Vision-Tactile Policy Learning
     2025 · arXiv 2507.04411
```

- カーソル行：左端に `▌`（Primary）＋ Selection 背景
- `★`：選択（Marked 色）。複数選択して Review / Agent に渡す
- 右端バッジ：`NEW` / `✓ saved`（§2.4）
- 既に Paperpile にある論文は `Paperpile ✓` をメタ行に出す（重複登録を防ぐ）

### 5.3 Agent Pane（最重要）

画面下部に常駐。**入力行・実行ログ・提案** の 3 要素で構成する。

```
╭─ Agent · Papers · 3 selected ──────────────────────────── ⠹ running 12s ─╮
│ ❯ Compare these papers                                                   │
│   ✓ get_paper_content  VLA-JEPA                            alphaXiv 2.1s │
│   ✓ get_paper_content  Tactile World Model                 alphaXiv 1.8s │
│   ⠹ get_paper_content  Vision-Tactile Policy               alphaXiv      │
│   ◯ 比較表を生成                                                         │
│ ❯ _                                                                      │
╰─ enter 送信  ↑ 履歴  ctrl+c 中断  ctrl+o ログ展開 ───────────────────────╯
```

- **タイトル**：`Agent · <フェーズ> · <文脈>`。フェーズ名は Phase color、文脈は選択数やテーマ
- **右上**：実行状態（`idle` / `⠹ running 12s` / `✓ done` / `✗ failed`）
- **プロンプト記号**：`❯`（Agent 色）。過去の指示も同じ記号で残す
- **ステップ行**：`状態アイコン  ツール名  対象  …  ソース 所要時間`。ツール名は Accent、ソースは Muted
  - Plan → Tool / MCP / Skill → Result（design.md §4）の流れをそのまま見せる
  - 既定では直近 4 ステップのみ表示、`ctrl+o` で全ログ展開
- **結果**：短い結果は Agent 欄内、表や長文は **メイン領域に新しいパネル** として開き、Agent 欄には `→ Review に比較表を開きました` とだけ出す
- **提案**：待機中は入力行の下に、その画面で使える指示例を dim で 2〜3 個出す（`tab` で補完）

```
│ ❯ _                                                                      │
│   Compare these papers · Find research gaps · Design experiment          │
```

### 5.4 Permission / Confirm Dialog

外部への書き込み・コスト・実行を伴う操作は Agent が勝手に進めず、必ず確認する。

| 操作 | 確認 |
|------|------|
| Paperpile 登録 / alphaXiv フォルダ保存 | 必須（二重線ダイアログ、§4.3） |
| 実験の実行（Run） | 必須。GPU・推定時間を表示 |
| 大量の LLM 呼び出し（詳細の日本語化 10 件以上など） | 必須。件数を表示 |
| 読み取りのみの検索・取得 | 不要 |

キーは `Y`（実行）/ `n` または `Esc`（取消）/ `a`（このセッション中は常に許可）。
`enter` は何も選ばずに押すと取消扱いにし、誤操作で外部に書き込まないようにする。

### 5.5 Tables（比較表・実験結果）

Review の比較表、Run の結果表で共通。ヘッダは bold + 下線、数値は右寄せ、最良値は Success + bold。

```
 Item               VLA-JEPA        Tactile WM      VT Policy
 ────────────────── ─────────────── ─────────────── ───────────────
 Input              RGB             RGB + Touch     RGB + Touch
 World Model        JEPA            Transformer     —
 Policy             VLA             BC              Diffusion
 Future Prediction  ✓               ✓               ✗
 Robot              Franka          UR5             Franka
```

- 欠損は `—`（Muted）。Yes/No は `✓` / `✗` に置換
- 列幅が足りない場合は左端列を固定して横スクロール（`h` / `l`）

### 5.6 Form Controls（Papers 検索・Run 定義）

```
 Query    [ vision tactile world model_                          ]
 Sources  ☑ Paperpile  ☑ arXiv  ☑ Semantic Scholar  ☑ alphaXiv
 Year     [ 2023 ] – [ 2026 ]
                                              [ ⏎ Search ]  [ Reset ]
```

- 入力欄：フォーカス時 `[ ]` を Primary、非フォーカスは Neutral 200
- エラー時：欄を Error、下の行に `✗ 年の範囲が逆です` を Error で表示
- ボタン：フォーカス時 reverse + Primary、それ以外は `[ ]` 囲みのみ

### 5.7 Status Bar

最下行。外部接続を左、フォーカス中のキーヒントを右に置く。背景は Neutral 50。

```
 Paperpile ✓  arXiv ✓  alphaXiv ✓  GitHub ✓  Feeds ⚠ 8/9  MCP ✓       ? help  q quit
```

| 状態 | 表示 |
|------|------|
| 正常 | `名前 ✓`（✓ を Success） |
| 部分失敗 | `名前 ⚠ 8/9`（Warning） |
| 切断・認証切れ | `名前 ✗`（Error。選択すると理由と再接続手順を表示） |
| 確認中 | `名前 ⠋`（Muted） |
| 未設定 | `名前 –`（Neutral 300） |

- 幅が足りないときは右から省略し、`+3` のように残数を表示。異常のある接続は省略しない
- 定期巡回ジョブが動いているときは左端に `⟳`（design.md §6.8）

### 5.8 Toast / Notification

画面右上に 1〜2 行、4 秒で消える。エラーは手動で閉じるまで残す。

```
                                         ╭──────────────────────────────╮
                                         │ ✓ 3 本を Paperpile に登録    │
                                         ╰──────────────────────────────╯
```

---

## 6. Screens

以下はすべて **120 列 × 36 行** を基準にした参考描画。ヘッダ・タブ・Agent 欄・ステータスバーは全画面共通（§7）。

### 6.1 全体フレーム

```
 Research OS  ·  vision tactile world model                                                          2026-10-01 09:12
 1 Papers   2 Review   3 Graph   4 Hypothesis   5 Run   │   6 Intel ●3
 ▔▔▔▔▔▔▔▔
╭─ <メイン領域: フェーズごとの画面> ─────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                    │
│                                                                                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Agent · Papers ──────────────────────────────────────────────────────────────────────────────────────────── idle ─╮
│ ❯ _                                                                                                                │
│   Find papers about … · Show only papers after 2024 · 今日の新着論文                                               │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
 Paperpile ✓  arXiv ✓  alphaXiv ✓  GitHub ✓  Feeds ✓ 9/9  MCP ✓                                         ? help  q quit
```

### 6.2 Papers

一覧（左 60%）＋ プレビュー（右 40%）。100 列未満ではプレビューを隠し、`enter` で全画面表示。

```
╭─ Results (37) ─────────────────────────── 1 of 37 ─╮╭─ Preview ──────────────────────────────────────────╮
│ ▌★ VLA-JEPA                                    NEW ││ VLA-JEPA                                           │
│ ▌  2025 · arXiv 2509.01234                         ││ 2025 · arXiv 2509.01234                            │
│ ▌  #VLA #JEPA #World-Model                         ││                                                    │
│   ★ Tactile World Model                            ││ 視覚・言語・行動を JEPA の潜在空間で統合し、       │
│     2026 · Paperpile ✓                             ││ 将来の潜在状態を予測する VLA を提案。              │
│     #Tactile #Manipulation                         ││                                                    │
│     Vision-Tactile Policy Learning                 ││ Tags   #VLA #JEPA #World-Model                     │
│     2025 · arXiv 2507.04411                        ││ Links  arxiv · alphaxiv · github                   │
╰─ / filter  space ★  enter open  s sort ────────────╯╰────────────────────────────────────────────────────╯
```

- 関心フィード表示時はパネルタイトルが `Feed · 2026-10-01 (12 new)` になり、各アイテムの 3 行目に日本語タイトル
- `v` でソースごとの取得件数（`alphaXiv 10 · arXiv 27`）を表示

### 6.3 Review

選択論文（左の細いリスト）＋ ワークスペース（比較表・分析）。ワークスペースは観点ごとのサブタブ。

```
╭─ Selected (3) ───────╮╭─ Compare ─ [Table] Similarities  Differences  Novelty  Limitations  Missing ─────────╮
│ ★ VLA-JEPA           ││ Item               VLA-JEPA        Tactile WM      VT Policy                         │
│ ★ Tactile World Model││ ────────────────── ─────────────── ─────────────── ───────────────                   │
│ ★ VT Policy          ││ Input              RGB             RGB + Touch     RGB + Touch                       │
│                      ││ Future Prediction  ✓               ✓               ✗                                 │
╰──────────────────────╯╰─ [ ] ]  サブタブ切替   q  引用を表示 ────────────────────────────────────────────────╯
```

- `answer_pdf_queries` の回答は本文中に `[p.4]` のようなページ引用を Accent + underline で付け、選択で該当箇所を表示

### 6.4 Graph

ノードは種別グリフ＋色（§2.4）。エッジはラベルを Muted で線上に置く。フォーカス中ノードは reverse。

```
                        ● World Model
                             │
               ┌─────────────┴─────────────┐
               │ related_to                │ related_to
            ● JEPA                     ● Dreamer
               │ uses                      │
          ▪ VLA-JEPA                  ▪ DreamerV3
               │ extends
       ┌───────┴────────┐
  ▪ Vision-Tactile    ● VLA
       │ solves
       ▼
  ? Failure Prediction
```

- 右側に選択ノードの詳細パネル（種別・関連論文・出典）
- `f` でノード種別フィルタ、`+` / `-` で展開深さ、`c` で断絶領域（disconnected）を Error 色で強調

### 6.5 Hypothesis

研究ロジックのチェーンを縦に並べ、現在編集中の段を強調する。

```
 Problem ─▶ Research Gap ─▶ Research Question ─▶ ▌Hypothesis ─▶ Experiment
                                                  ▔▔▔▔▔▔▔▔▔▔▔
╭─ H-003 · Hypothesis ─────────────────────────────────────── draft ─╮
│ Vision-Tactile JEPA will improve failure prediction AUC            │
│ compared with reactive multimodal fusion.                          │
│                                                                    │
│ 根拠   ▪ VLA-JEPA  ▪ Tactile World Model  ? Failure Prediction     │
│ 検証   → VT-JEPA-001 (Run)                                         │
╰────────────────────────────────────────────────────────────────────╯
```

- 状態バッジ：`draft`（Muted）/ `active`（Hypothesis 色）/ `supported`（Success）/ `rejected`（Error）
- 根拠欄は Graph のノードをグリフ付きで参照（選択で Graph へジャンプ）

### 6.6 Run

実験定義（左）＋ 実行ログ・メトリクス（右）。

```
╭─ VT-JEPA-001 ──────────────────╮╭─ Progress ──────────────────────────────────────────────────╮
│ Dataset  so101_vt_dataset_v3   ││ Vision-only            ████████████████████ 100%  ✓         │
│ Models   ☑ Vision-only         ││ Vision-Tactile Fusion  ████████████░░░░░░░░  61%  epoch 31  │
│          ☑ VT Fusion           ││ Vision-Tactile JEPA    ░░░░░░░░░░░░░░░░░░░░   –   queued    │
│          ☑ VT JEPA             ││                                                             │
│ Metrics  ☑ Success Rate        ││ Failure AUC  ▁▂▃▅▆▇▇█  0.842                                │
│          ☑ Failure AUC         ││                                                             │
│          ☑ Slip Rate           ││                                                             │
│                    [ ▶ Run ]   ││                                                             │
╰────────────────────────────────╯╰─────────────────────────────────────────────────────────────╯
```

- 進捗バー：`█` / `░`、完了は Success、失敗は Error で `✗` と最終ログ 3 行
- メトリクス推移はスパークライン `▁▂▃▄▅▆▇█`

### 6.7 Intel

Tech / Business / Sources のサブタブ。各行に日付・企業・種別・信頼性を必ず出す。

```
╭─ Intel ─ [Tech] Business  Sources ─────────── All companies · Last 7 days ─ updated 06:00 ─╮
│ ★ 09-17  ■ Ambi Robotics   Tech+Biz  Agentic Robotics でロボットプログラムを自動改善       │
│                                      数週間の調整を約10時間で解決            ◐ claim       │
│ ★ 09-10  ■ Skild AI        Biz       商用導入10か月で ARR 1億ドル超 / 有料顧客60社超       │
│                                      ARR は認識済み売上とは異なる            ◐ claim       │
│   09-17  ■ Figure AI       Tech      Helix 2.5：未経験の30家庭環境で汎化を検証             │
│                                                                                            │
│ ⟳ Updated  過去記事 3 件に変更あり（d で Diff）                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────╯
```

- 事業化ステージ（design.md §6.5）は 5 段メーター `▰▰▰▱▱ 試験導入` で表示
- `⟳ Updated` の Diff は `+` 行を Success、`-` 行を Error で表示

---

## 7. Layout & Spacing

### 7.1 基本構造

```
行  1        Header（アプリ名 · テーマ · 時刻）
行  2–3      Phase Tabs + マーカー
行  4–(n-9)  Main（フェーズごとの画面。可変）
行  (n-8)–(n-1) Agent Pane（既定 7 行。3〜全高で可変）
行  n        Status Bar
```

- **Min terminal**: 80 × 24（Agent 欄は 4 行に縮小、2 ペイン画面は 1 ペイン化）
- **Ideal**: 120 × 36 以上
- **Wide（≥ 160 列）**: Main を 3 ペイン化（例：Papers = 一覧 · プレビュー · 関連グラフ）
- **パネル内パディング**: 上下 0 行、左右 1 文字
- **パネル間ギャップ**: 0（枠を隣接させる）
- **インデント**: 2 スペース（アイテムの 2 行目以降）

### 7.2 Agent 欄のサイズ

| モード | 高さ | 切替 |
|--------|------|------|
| Compact | 4 行（入力 + 直近 2 ステップ） | 80×24 時の既定 |
| Normal | 7 行 | 既定 |
| Expanded | 画面の 60% | `ctrl+o` |
| Focus | 全画面（Main を隠す） | `F` |

### 7.3 配置の原則

- テキストは左寄せ、数値・時間・件数は右寄せ
- パネルタイトルは左、件数・位置・状態は右（同じ枠線上）
- 原題 → メタ → 日本語 の順で縦に積む（横に並べない。日本語は幅が読めないため）
- **日本語の表示幅**：全角 = 2 列で計算する。切り詰めは表示幅ベースで行い、`…` を付ける（文字数で切らない）
- **East Asian Ambiguous 幅**：`★ ● ◆ ○ ◎ ▪` などは CJK 環境で 2 列になりうる。設定 `ambiguous_width: 1|2` を持ち、既定は 1。崩れる環境向けに ASCII フォールバック（§8）へ切り替えられるようにする

---

## 8. Icons & Indicators

絵文字は使わない（幅が端末依存のため）。すべて単色グリフで、ASCII フォールバックを持つ。

| Purpose | Icon | ASCII |
|---------|------|-------|
| Success / 接続 OK | `✓` | `+` |
| Error / 失敗 | `✗` | `x` |
| Warning | `⚠` | `!` |
| Info | `ℹ` | `i` |
| Pending | `◯` | `o` |
| Running | `⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏` | `\|/-\` |
| Skipped | `⊘` | `-` |
| Agent prompt | `❯` | `>` |
| Cursor row | `▌` | `>` |
| Marked（選択） | `★` | `*` |
| New | `NEW` | `NEW` |
| Updated | `⟳` | `~` |
| Link / 遷移 | `→` | `->` |
| Graph edge | `─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ▼ ▶` | `- \| + v >` |
| Checkbox on | `☑` | `[x]` |
| Checkbox off | `☐` | `[ ]` |
| Claim | `◐` | `(c)` |
| Verified | `●` | `(v)` |
| Stage meter | `▰ ▱` | `# .` |
| Progress | `█ ░` | `# .` |
| Sparkline | `▁▂▃▄▅▆▇█` | `_.-=^` |

---

## 9. Keybindings

vim 系を基本に、Agent 欄へのアクセスを最短にする。

### 9.1 Global

| Key | Action |
|-----|--------|
| `1`–`6` | フェーズタブ切替（Papers … Intel） |
| `>` / `i` | Agent 欄にフォーカス（入力開始） |
| `Esc` | Agent 欄 → Main に戻る / ダイアログを閉じる |
| `Tab` / `Shift+Tab` | パネル間フォーカス移動 |
| `ctrl+o` | Agent ログ展開 / 縮小 |
| `F` | Focus mode（Agent 欄を全画面） |
| `ctrl+c` | 実行中の Agent を中断（2 回でアプリ終了確認） |
| `:` | コマンドパレット（`:theme`, `:reconnect alphaxiv` など） |
| `?` | ヘルプ（現在の画面のキー一覧） |
| `q` | 終了（実行中ジョブがあれば確認） |

### 9.2 List / Panel

| Key | Action |
|-----|--------|
| `j` / `k`, `↓` / `↑` | 上下移動 |
| `g` / `G` | 先頭 / 末尾 |
| `enter` | 開く（Papers → Review、ノード → 詳細） |
| `space` | `★` 選択トグル |
| `/` | インクリメンタル絞り込み |
| `s` | ソート切替 |
| `d` | dismiss（フィード）/ Diff 表示（Intel） |
| `y` | arXiv ID / URL をコピー |
| `o` | ブラウザで開く |
| `[` / `]` | サブタブ切替 |

### 9.3 Agent Pane

| Key | Action |
|-----|--------|
| `enter` | 送信 |
| `shift+enter` | 改行 |
| `↑` / `↓` | 入力履歴 |
| `tab` | 提案の補完 |
| `@` | 選択中オブジェクトを参照挿入（`@selected`, `@H-003`, `@VT-JEPA-001`） |

キーヒントは各パネル下辺とステータスバー右端に、`キー 説明` の形で Accent（キー）+ Muted（説明）で表示する。

---

## 10. Animation & Motion

動きは **Agent と接続の状態を伝えるときだけ** 使う。装飾的なアニメーションは入れない。

| 対象 | 表現 | 間隔 |
|------|------|------|
| Agent 実行中 | Braille スピナー `⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏`（Agent 色）＋ 経過秒 | 80ms |
| Agent 思考中 | `❯` の直後に `thinking…` を dim italic、ドットのみ循環 | 400ms |
| 接続確認中 | ステータスバーで同スピナー（Muted） | 80ms |
| 新着到着 | タブの `●n` を 1 回だけ reverse で点滅 | 300ms × 2 |
| 画面遷移 | なし（即時切替） | — |
| 進捗 | `█░` バー + パーセント + ETA（Run のみ） | 更新ごと |

- `reduce_motion: true` でスピナーを静止記号 `…` に置換
- ストリーミング出力は 1 行単位で追記（文字単位のタイプライター表現はしない）

---

## 11. Agent Prompt Guide

> AI エージェントに Research OS の TUI コンポーネントを作らせるときに貼る要約。

### Quick Reference

```
Theme:    Lab Ink (dark, Tokyo-Night-like ink blue)
Bg/Fg:    #1a1b26 / #c0caf5      Surface: #24283b   Selection: #2e3c64
Primary:  #7aa2f7 (focus)        Accent:  #7dcfff (links, keys)
Agent:    #bb9af7 (agent pane, ❯, spinner)
Status:   ok #9ece6a / warn #e0af68 / err #f7768e / muted #737aa2
Phases:   Papers #7aa2f7 · Review #7dcfff · Graph #73daca ·
          Hypothesis #e0af68 · Run #9ece6a · Intel #ff9e64
Border:   rounded ╭╮╰╯─│ (panels), double ╔╗╚╝═║ (confirm dialogs)
Glyphs:   ✓ ✗ ⚠ ◯ ⠋ ★ ▌ ❯ ⟳ ◐ ●   (ASCII fallback required)
Layout:   Header / Tabs / Main / Agent(7 rows) / Status bar, min 80x24
Text:     UI labels English, content Japanese; CJK width = 2
```

### Example Prompts

- 「DESIGN.md に従って Papers 画面の結果リストを作って。1 論文 3 行、カーソル行は `▌` + Selection 背景、`space` で `★`、右端に `NEW` バッジ」
- 「Agent 欄を実装して。タイトルは `Agent · <phase> · <context>`、ステップ行は状態アイコン + ツール名（Accent）+ ソースと所要時間（Muted, 右寄せ）、実行中は枠を Agent 色 bold に」
- 「ステータスバーを作って。各接続を `名前 ✓/⚠ n/m/✗/⠋/–` で表示、幅不足時は正常な接続から省略して `+n`」
- 「Paperpile 登録の確認ダイアログを二重線で。`Y` 実行 / `Esc` 取消、対象論文を `★` 付きで列挙」

---

## 12. Do's and Don'ts

### Do

- 状態は **色 + アイコン + 文字** の 3 点で表す（16 色・色覚多様性・スクリーンショットでも読めるように）
- 論文は原題を主、日本語訳を従として縦に並べる
- 数値・主張には出典と信頼性（`◐ claim` / `● verified`）を併記する
- Agent のツール呼び出しは隠さずステップとして見せる。長い結果はメイン領域へ
- 外部への書き込み（Paperpile・alphaXiv・実験実行）は必ず確認ダイアログを出す
- 80 × 24 で全機能が使えることを確認する（ペインは減っても操作は減らさない）
- 表示幅は East Asian Width で計算し、切り詰めは `…` で

### Don't

- フェーズ色を状態（成功・失敗）の意味で使わない
- 絵文字をアイコンに使わない（幅が端末ごとに違う）
- 1 行に 3 色以上の強調色を置かない（Phase / Accent / 状態色のうち 2 つまで）
- TrueColor 前提にしない。256 / 16 色のフォールバックを必ず定義する
- Agent の出力で画面全体を書き換えない（ユーザーが見ていたパネルとカーソルを保持する）
- 装飾目的のアニメーション・スプラッシュの待ち時間を入れない
- 日本語を文字数で切り詰めない（全角で列がずれる）

---

## 13. Alternate Theme: Mission Control

> 参考: [`docs/UI/IMG_8806.jpg`](docs/UI/IMG_8806.jpg)（Agent Tree 型の TUI）。
> 漆黒に近いネイビーの上に、**Agent の役割ごとの 4 色**（Main = 青 / Subagent = 空色 / Routing = 緑 / Advisor = ラベンダー）を
> 細い破線枠で浮かべる、管制室的なテーマ。`:theme mission-control` で Lab Ink（§1〜§12）と切り替える。

レイアウト・コンポーネント・キーバインドは Lab Ink と共通で、**色トークンと枠線スタイルだけ** を差し替える。
加えて、Agent の内部構造（Main / Subagent / Routing / Advisor）を見せる **Agent Tree ビュー**（§13.6）を持つ。

### 13.1 Theme Overview

- **Name**: Mission Control
- **Mood**: 静か・精密・管制室的（黒地に発光する細線と、役割色のラベル）
- **Density**: Dense。枠は破線で軽く、面（背景塗り）はほぼ使わない
- **使いどころ**: Agent 主導で長いタスクを流すとき（Agent Focus `F`、Run 監視、Intel 巡回）
- **原則**: 色は「誰が動いているか（役割）」を表す。状態（成功・失敗）は従来どおり状態色 + アイコン

### 13.2 Semantic Roles

| Role | Hex | ANSI 256 | ANSI 16 | Usage | Lab Ink 対応 |
|------|-----|----------|---------|-------|--------------|
| Background | `#0a0e16` | `233` | `black` | 画面背景（ほぼ黒の紺） | Background |
| Surface | `#0f1522` | `234` | `black` | カード内背景（必要時のみ） | Surface |
| Raised | `#1b2236` | `236` | `bright black`（背景） | 選択行・ハイライト行の背景 | Selection |
| Foreground | `#e6e9f2` | `254` | `bright white` | 本文・カード見出し | Foreground |
| Text 2 | `#aab3c5` | `249` | `white` | 二次本文（値・説明） | Neutral 500 |
| Muted | `#6b7486` | `243` | `bright black` | ラベル（`role:` `state:`）、時刻、ヒント | Muted |
| Border dim | `#263042` | `237` | `bright black` | 非フォーカス枠、区切り `─ ─ ─` | Neutral 200 |
| Primary | `#3d7cf5` | `69` | `blue` | フォーカス枠、Main Agent | Primary |
| Accent | `#6cb6ff` | `75` | `bright blue` | キー表示、リンク、Subagent | Accent |
| Success | `#8ee58c` | `114` | `bright green` | 完了 `[ok returned]`、Routing | Success |
| Warning | `#f2c46d` | `221` | `yellow` | 部分失敗、`company_claimed` | Warning |
| Error | `#ff6b7f` | `204` | `red` | 失敗、接続断 | Error |
| Agent | `#b4a7f5` | `147` | `bright magenta` | Agent 欄の `❯`、Advisor | Agent |
| Marked | `#ff9e64` | `215` | `bright yellow` | `★` 選択 | Marked |

### 13.3 Agent Role Colors（このテーマの主役）

画像の 4 色凡例（`■ argon 4 · high` `■ flash 3.8 · swarm` `■ routing · forks` `■ advisor · on call`）を
Research OS の Agent 構成に対応させる。ヘッダ直下の **凡例行** に常に表示する。

| Role | Hex | ANSI 256 | ANSI 16 | Research OS での対象 | 凡例表記 |
|------|-----|----------|---------|----------------------|----------|
| Main | `#3d7cf5` | `69` | `blue` | Research Agent 本体（計画・統合・ユーザー応答） | `■ main · high` |
| Subagent | `#6cb6ff` | `75` | `bright blue` | 並列ワーカー（paper_searcher / pdf_reader / graph_builder / intel_crawler） | `■ sub · swarm` |
| Routing | `#8ee58c` | `114` | `bright green` | 決定的な分岐（どのソース・どのツール・再試行するか） | `■ routing · forks` |
| Advisor | `#b4a7f5` | `147` | `bright magenta` | 独立コンテキストのレビュアー（計画前・失敗反復時・完了前のチェック） | `■ advisor · on call` |

- 役割色は **枠線・カードタイトル・ログのタグ `[routing]` `[sub:reader]`** にだけ使う。本文は Foreground / Text 2
- Lab Ink では 4 役割とも Agent 色 `#bb9af7` で描き、タグ文字列で区別する（色に頼らない設計を維持）

**Phase Colors（Mission Control 版）**

| Phase | Hex | ANSI 256 |
|-------|-----|----------|
| Papers | `#6cb6ff` | `75` |
| Review | `#3d7cf5` | `69` |
| Graph | `#5fd7c4` | `80` |
| Hypothesis | `#f2c46d` | `221` |
| Run | `#8ee58c` | `114` |
| Intel | `#ff9e64` | `215` |

### 13.4 Borders

角丸ではなく **直角 + 破線** を基本にし、線の細さで「計器盤」感を出す。

```
┌╌ Main Agent · high ╌╌╌╌╌╌╌╌╌╌╌╌╌╌ ████ high ╌┐
╎ role:  plans & applies results               ╎
└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┬╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
                     ▼
```

| Part | Character | ASCII fallback | 用途 |
|------|-----------|----------------|------|
| corner | `┌ ┐ └ ┘` | `+` | カード・パネル |
| dashed horizontal | `╌` | `-` | 既定の枠（役割色） |
| dashed vertical | `╎` | `:` | 既定の枠（役割色） |
| solid horizontal / vertical | `─ │` | `- \|` | フォーカス中のパネル（役割色 + bold） |
| junction | `┬ ┴ ├ ┤` + `·` | `+` | 枠同士の接続点。接続点に `·` を置いて「ノード」に見せる |
| flow arrow | `▼ ◂ ▸` | `v < >` | Agent 間の制御の流れ（Main → Routing → Subagent → Main） |
| inner divider | `- - - - -` | 同左 | カード内の区切り（Border dim） |

- 確認ダイアログは Lab Ink と同じ二重線 `╔═╗`（色は Warning）。破線にしない
- 端末フォントで `╌ ╎` が欠ける場合は `ascii_borders: true` で fallback

### 13.5 Components

**(a) Legend Header**

```
 RESEARCH OS AGENT TREE  ·  MAIN high  ·  SUB ×3 swarm  ·  ADVISOR on call
 ■ main · high      ■ sub · swarm      ■ routing · forks      ■ advisor · on call
```

1 行目はタイトル（大文字・bold、役割名だけ役割色）。2 行目は凡例（`■` を役割色、文字は Muted）。

**(b) Agent Card**（Main / Advisor）

```
┌╌ Research Agent · high / main ╌╌╌╌╌ ████ high ╌┐ ╌ advice ◂ ┌╌ Advisor · on call ╌╌╌╌╌ agent: advisor ╌┐
╎ role:      plans & applies results               ╎            ╎ independent context · reads full session   ╎
╎ state:     Plan: decomposing subtasks…           ╎            ╎▌◆ [1] before a plan: is this right?        ╎
╎ subagents: 3× spawned via /agents                ╎            ╎  · [2] error repeats: am I digging wrong?  ╎
╎ ┌──────────────────────────────────────────┐     ╎            ╎  · [3] before "done": what did I miss?     ╎
╎ │ main: Plan ready · 3 worker tasks        │     ╎            ╎                                            ╎
╎ │ ↳ dispatching forks to routing           │     ╎            ╎ calls: 3   tokens: 368k         [ADVISING] ╎
╎ └──────────────────────────────────────────┘     ╎            └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┬╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
```

- ラベル（`role:` など）は Muted、値は Foreground、強度メーター `████` は役割色
- 内側の小さな実線ボックスは「直近の思考 / 出力」。文字は Text 2
- Advisor のチェック項目は `·` 箇条、現在評価中の項目は `▌◆` + Raised 背景
- 状態バッジは角括弧で右下：`[ADVISING]` `[IDLE]` `[APPLIED]`（役割色）

**(c) Routing Bars**（確信度バー）

```
┌╌ ROUTING · FAST FORK LAYER ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌ forks saved  1,687 ╌┐
╎ which source    ██████████████████████▒▒▒▒▒  0.88 sharp  → runs in code (<16ms)    ╎
╎ which tool      ███████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  0.46 split  → escalates to Main        ╎
╎ retry or stop   █████████████████████▒▒▒▒▒▒  0.85 sharp  → runs in code (<16ms)    ╎
╎ Deterministic forks resolved in <16ms · LLM only sees forks that split              ╎
└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
```

- 塗り `█` は判定先の役割色（`sharp` = Routing 緑、`split` = Main 青）。残りは **ディザ** `▒`（同色の暗色 `#2c4a33` / `#1d3366`）
- `sharp` / `split` の文字は塗りと同色、`→` 以降は Muted
- ASCII fallback: `#` と `.`

**(d) Swarm Cards**（Subagent 並列表示）

```
┌╌ SUBAGENT DISPATCHER (SWARM) ╌╌╌╌╌╌╌ effort: med · 3× swarm · 235 t/s  [ ▁▃▅▇▆▅▃ ] ╌┐
└╌╌╌╌╌·╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌·╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌·╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐ ┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐ ┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐
╎      paper_searcher      ╎ ╎        pdf_reader         ╎ ╎       graph_builder        ╎
╎       sub · med          ╎ ╎        sub · med          ╎ ╎        sub · med           ╎
╎  - - - - - - - - - - -   ╎ ╎  - - - - - - - - - - -    ╎ ╎  - - - - - - - - - - -     ╎
╎   alphaXiv + arXiv 検索   ╎ ╎  本文取得 & PDF 質問     ╎ ╎  ノード / エッジ抽出       ╎
╎      [ ⠹ running ]       ╎ ╎      [ ✓ returned ]       ╎ ╎      [ ◯ queued ]          ╎
└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘ └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘ └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
```

- カード名は bold + Foreground、サブタイトル（`sub · med`）は Subagent 色、本文は中央寄せ
- 状態は `[ アイコン 状態 ]` を中央に。running は Subagent 色スピナー、returned は Success、failed は Error
- スループットのスパークライン `▁▃▅▇` は Routing 緑
- 幅 < 100 列では縦積み、< 80 列ではカードを 1 行サマリ（`⠹ paper_searcher · running`）に畳む

**(e) Return Card + Tagline**

```
              ┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐
              ╎      back to Main session · high               ╎
              ╎  review + verify · Advisor pre-flight stamped   ╎
              └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
       Plan on Main. Delegate to Subagents. Keep Advisor on call.
```

タグラインは bold + Foreground、役割名だけ役割色。1 画面に 1 つまで。

**(f) Session Log**

```
┌╌ session log ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐
╎ 16:04:12  [routing]       which tool    → get_paper_content     split → main     ╎
╎ 16:04:13  [sub:search]    alphaXiv 10 · arXiv 27 件を取得             [ok returned] ╎
╎ 16:04:14  [sub:reader]    VLA-JEPA の本文を取得中                       [/ running] ╎
╎ 16:04:15  [advisor]       同じ検索の反復 → クエリ過剰制約を指摘             applied ╎
╎ 16:04:16  [sub:graph]     Method 12 · Dataset 4 ノードを追加          [ok returned] ╎
└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
```

| 列 | 色 |
|----|----|
| 時刻 | Muted |
| タグ `[routing]` `[sub:*]` `[advisor]` `[main]` | 各役割色 |
| 内容 | Foreground（日本語可） |
| 結果（右寄せ） | `[ok returned]` = Success、`[/ running]` = Subagent、`applied` = Advisor、`split → main` = Main、失敗 = Error + `✗` |

**(g) Prompt + Effort Footer**（Agent 欄・ステータスバーの Mission Control 版）

```
 research ❯ @advisor verify hypothesis before run_

 effort: [main:high/sub:med]   subagents: [3/3 swarm]   advisor: [advising]   routing: [1,687 forks]
```

- `research` は Main 色、`❯` は Agent 色、`@advisor` は Advisor 色 + bold
- フッタはキーを Muted、`[ ]` 内の値を対応する役割色

### 13.6 Screen: Agent Tree（`F` / Focus mode）

Mission Control で Agent Focus（§7.2）を開いたときの全体像。上から **Main ↔ Advisor → Routing → Swarm → Main に戻る** の流れを縦に描く。

```
 RESEARCH OS AGENT TREE  ·  MAIN high  ·  SUB ×3 swarm  ·  ADVISOR on call
 ■ main · high      ■ sub · swarm      ■ routing · forks      ■ advisor · on call

 ┌╌ Main Agent ╌╌╌╌╌╌╌╌╌╌╌ ████ high ╌┐ ╌ advice ◂ ┌╌ Advisor · on call ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐
 ╎ … (13.5 b)                         ╎            ╎ … (13.5 b)                         ╎
 └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┬╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘            └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
                  ▼
 ┌╌ ROUTING · FAST FORK LAYER ╌╌╌╌ (13.5 c) ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐
 └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┬╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
                                          ▼
 ┌╌ SUBAGENT DISPATCHER (SWARM) ╌╌ (13.5 d) ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐
 │ [ paper_searcher ]          [ pdf_reader ]          [ graph_builder ]               │
 └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┬╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
                         ┌╌ back to Main · review + verify ╌┐   (13.5 e)
                         └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
 ┌╌ session log ╌╌ (13.5 f) ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐
 └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
 research ❯ _                                                         (13.5 g)
 effort: [main:high/sub:med]   subagents: [3/3 swarm]   advisor: [idle]   routing: [1,687 forks]
```

- 現在動いている段の枠だけ **実線 + bold**、それ以外は破線（どこで処理が止まっているかが一目で分かる）
- 80 × 24 では Advisor カードを Main カード下の 1 行（`advisor: [advising] · [1] before a plan`）に畳み、Swarm は 1 行サマリ化

### 13.7 Quick Reference（Agent Prompt 用）

```
Theme:    Mission Control (near-black navy, role-colored dashed lines)
Bg/Fg:    #0a0e16 / #e6e9f2     Surface: #0f1522   Raised: #1b2236
Text2:    #aab3c5               Muted:   #6b7486   Border dim: #263042
Roles:    main #3d7cf5 · sub #6cb6ff · routing #8ee58c · advisor #b4a7f5
Status:   ok #8ee58c / warn #f2c46d / err #ff6b7f
Border:   square + dashed ┌╌┐╎└┘ (default), solid │─ for the active stage,
          double ╔═╗ for confirm dialogs; junction dots ·, flow ▼ ◂
Bars:     fill █ in role color + dither ▒ in dark role color
Log tags: [routing] [sub:*] [advisor] [main] in role colors
```

### 13.8 Do's and Don'ts（Mission Control 固有）

- **Do**: 役割色は枠・タイトル・タグに限定し、本文は Foreground / Text 2 で読みやすく保つ
- **Do**: 「いま動いている段」だけを実線にし、静止中の段は破線のまま
- **Do**: 背景の黒は塗りつぶさず端末背景に任せられる（`transparent_bg: true`）。その場合も Raised 行だけは塗る
- **Don't**: Main（青）と Subagent（空色）を隣接する同じ太さの枠で並べない（色差が小さいため、Subagent は必ず破線 + サブタイトル表記で区別）
- **Don't**: 役割色を状態の意味で使わない（Routing の緑 ≠ 成功。成功は必ず `✓` / `[ok …]` と併用）
- **Don't**: ディザ `▒` を装飾目的で使わない。確信度・進捗の「残り」を表すときだけ
