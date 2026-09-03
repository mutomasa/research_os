# Research OS — UI 設計ドキュメント

このUIは、研究活動を **「検索 → 読解 → 比較 → 仮説化 → 実験」** まで
ひとつのTUIで回す **Research OS** を想定しています。

一言でいうと、このUIの思想は次の構成です。

> **Paperpile を文献DB、Claude Code を Research Agent、
> MCP を外部世界との I/O、TUI を研究者の Cockpit にする。**

---

## 目次

- [1. 全体レイアウト](#1-全体レイアウト)
- [2. 各画面の詳細](#2-各画面の詳細)
  - [2.1 Papers — 文献を探す](#21-papers--文献を探す)
  - [2.2 Review — 論文を深く読む](#22-review--論文を深く読む)
  - [2.3 Graph — 研究領域の構造理解](#23-graph--研究領域の構造理解)
  - [2.4 Hypothesis — 仮説を研究オブジェクト化](#24-hypothesis--仮説を研究オブジェクト化)
  - [2.5 Run — 実験実行](#25-run--実験実行)
- [3. ステータスバー（外部接続）](#3-ステータスバー外部接続)
  - [3.1 alphaXiv MCP](#31-alphaxiv-mcp)
- [4. Agent 欄がこのUIの中心](#4-agent-欄がこのuiの中心)
- [5. 裏側のアーキテクチャ](#5-裏側のアーキテクチャ)

---

## 1. 全体レイアウト

画面は上から **① ナビゲーション → ② 研究対象 → ③ Agent操作 → ④ 接続状態** の4層です。

```
┌────────────────────────────────────────────┐
│ Research OS                                 │  ① アプリ名
├────────────────────────────────────────────┤
│ Papers │ Review │ Graph │ Hypothesis │ Run  │  ② 研究フェーズ
├────────────────────────────────────────────┤
│                                            │
│  vision tactile world model                │  ③ 現在の研究テーマ
│                                            │
│  Found: 37 papers                          │
│                                            │
│  ★ VLA-JEPA                                │
│  ★ Tactile World Model                     │  ④ 文献・成果物
│  ★ Vision-Tactile Policy                   │
│                                            │
├────────────────────────────────────────────┤
│ Agent                                      │
│                                            │
│ > Compare these papers                     │
│ > Find research gaps                       │  ⑤ AI Agent操作
│ > Design experiment                        │
│                                            │
├────────────────────────────────────────────┤
│ Paperpile ✓ arXiv ✓ alphaXiv ✓ GitHub ✓    │  ⑥ 外部接続
└────────────────────────────────────────────┘
```

| # | 要素 | 役割 |
|---|------|------|
| ① | アプリ名 | Research OS のヘッダ |
| ② | 研究フェーズ | Papers / Review / Graph / Hypothesis / Run のタブ切り替え |
| ③ | 現在の研究テーマ | いま扱っているクエリ／テーマ |
| ④ | 文献・成果物 | ヒットした論文やアウトプット一覧 |
| ⑤ | Agent 操作 | 自然言語で Agent に指示する欄（**最重要**） |
| ⑥ | 外部接続 | Paperpile / arXiv / alphaXiv / GitHub / MCP の接続ステータス |

---

## 2. 各画面の詳細

### 2.1 Papers — 文献を探す

文献を探す画面です。

**入力例**

| 項目 | 値 |
|------|-----|
| Query | `vision tactile world model` |
| Sources | ☑ Paperpile ／ ☑ arXiv ／ ☑ Semantic Scholar ／ ☑ alphaXiv |
| Year | 2023–2026 |

**出力例**

```
37 papers found

★ VLA-JEPA
  2025 | arXiv
  tags: VLA, JEPA, World Model

★ Tactile World Model
  2026 | Paperpile
  tags: Tactile, Manipulation

  Vision-Tactile Policy Learning
  2025 | arXiv
```

**Agent への指示例**

- `> Find papers about tactile failure prediction`
- `> Show only papers after 2024`
- `> Add selected papers to Paperpile`
- `> Discover related papers on alphaXiv and pull their AI summaries`

---

### 2.2 Review — 論文を深く読む

選択した論文を深く読むための画面です。3本選択すると Agent が比較表を作ります。

```
Selected Papers: 3
  - VLA-JEPA
  - Tactile World Model
  - Vision-Tactile Policy
```

**Agent が生成する比較表**

| 項目 | VLA-JEPA | Tactile WM | VT Policy |
|------|----------|------------|-----------|
| Input | RGB | RGB + Touch | RGB + Touch |
| World Model | JEPA | Transformer | — |
| Policy | VLA | BC | Diffusion |
| Future Prediction | Yes | Yes | No |
| Robot | Franka | UR5 | Franka |

さらに `> Compare these papers` から、次の観点まで分析します。

- Similarities（共通点）
- Differences（相違点）
- Novelty（新規性）
- Limitations（限界）
- Missing experiments（不足している実験）

> Review は単なる PDF Viewer ではなく、**LLM による論文理解ワークスペース** です。

---

### 2.3 Graph — 研究領域の構造理解

論文同士の関係を **Knowledge Graph** として見る、Research OS の中核画面です。

```
                   World Model
                       │
           ┌───────────┼───────────┐
           │                       │
          JEPA                   Dreamer
           │                       │
       VLA-JEPA                DreamerV3
           │
           ├──────────────┐
           │              │
      Vision-Tactile     VLA
           │
           ▼
    Failure Prediction
```

**Node の種類**

`Paper` ／ `Method` ／ `Dataset` ／ `Model` ／ `Task` ／ `Robot` ／ `Metric` ／ `Research Problem`

**Edge の種類**

| From | 関係 | To |
|------|------|-----|
| Paper | `uses` | Method |
| Paper | `evaluates_on` | Dataset |
| Paper | `extends` | Paper |
| Paper | `solves` | Problem |
| Method | `related_to` | Method |

**Agent への問い合わせ例**

- `> Show papers connecting JEPA and tactile sensing`
- `> What research areas are disconnected?`

> Graph は「論文一覧」から「研究領域の構造理解」へ進む場所です。

---

### 2.4 Hypothesis — 仮説を研究オブジェクト化

Research Gap から研究仮説を作る画面です。研究ロジックを次のチェーンで管理します。

```
Problem → Research Gap → Research Question → Hypothesis → Experiment
```

**生成の流れ（例）**

1. **Research Gap**
   > Most visual-tactile systems perform reactive fusion.
   > Few approaches explicitly predict future multimodal latent states.

2. **Research Question**
   > Can future visual-tactile latent prediction improve
   > early manipulation failure detection?

3. **Hypothesis**
   > Vision-Tactile JEPA will improve failure prediction AUC
   > compared with reactive multimodal fusion.

> ChatGPT との会話と違い、仮説を **「研究オブジェクト」として永続化** するのが要点です。

---

### 2.5 Run — 実験実行

実験を定義して実行する画面です。

**実験定義（例）**

| 項目 | 内容 |
|------|------|
| Experiment | `VT-JEPA-001` |
| Dataset | `so101_vt_dataset_v3` |
| Models | ☑ Vision-only ／ ☑ Vision-Tactile Fusion ／ ☑ Vision-Tactile JEPA |
| Metrics | ☑ Success Rate ／ ☑ Failure AUC ／ ☑ Slip Rate |

`[ Run ]` を押すと、次のパイプラインが走ります。

```
Claude Code → Python → PyTorch → Training → Evaluation
```

**`> Implement this experiment` の結果**

```
experiments/
└── vt_jepa_001/
    ├── config.yaml
    ├── train.py
    ├── evaluate.py
    └── README.md
```

> ここまで来ると Research OS は文献管理ツールではなく **研究開発 IDE** になります。

---

## 3. ステータスバー（外部接続）

画面下部 `Paperpile ✓  arXiv ✓  alphaXiv ✓  GitHub ✓  MCP ✓` はステータスバーです。

| 表示 | 意味 |
|------|------|
| Paperpile ✓ | Paperpile ライブラリへアクセス可能 |
| arXiv ✓ | 新規論文検索が可能 |
| alphaXiv ✓ | alphaXiv MCP 経由で論文探索・全文解析・研究者検索が可能 |
| GitHub ✓ | コード・OSS・実装の検索が可能 |
| MCP ✓ | MCP Server 群が正常 |

**将来の拡張イメージ**

```
Paperpile ✓   arXiv ✓   alphaXiv ✓   GitHub ✓   Semantic Scholar ✓   OpenAlex ✓
Notion ✓   Overleaf ✓   Neo4j ✓   Claude ✓
```

### 3.1 alphaXiv MCP

文献探索の主力バックエンドとして [alphaXiv MCP](https://www.alphaxiv.org/docs/mcp) を接続します。

| 項目 | 値 |
|------|-----|
| Endpoint | `https://api.alphaxiv.org/mcp/v1` |
| Transport | Streamable HTTP |
| 認証 | OAuth 2.1（デフォルト）／ API キー（`Authorization: Bearer <key>`） |

**導入コマンド（Claude Code）**

```bash
# OAuth（対話ログイン）
claude mcp add --transport http alphaxiv https://api.alphaxiv.org/mcp/v1

# API キー（非対話・Settings > API Keys で発行）
claude mcp add --transport http alphaxiv https://api.alphaxiv.org/mcp/v1 \
  --header "Authorization: Bearer <key>"
```

追加後、Claude Code で `/mcp` を開き `alphaxiv` を選んで認証すると有効化されます。

**主なツール（全19種）**

| 分類 | ツール | 用途 |
|------|--------|------|
| Research | `discover_papers` | トピックからランク付き候補論文をエージェント検索 |
| Research | `get_paper_content` | AI 生成レポート／抽出全文の取得 |
| Research | `answer_pdf_queries` | PDF をページ単位・引用付き（XML）で質問検索 |
| Research | `read_files_from_github_repository` | 論文付随リポジトリの並列探索 |
| Researcher | `find_researchers` / `get_researcher` / `get_researcher_papers` | 研究者・著者から論文をたどる |
| Library | `list_library` / `save_papers_to_folder` / `create_folder` ほか | alphaXiv ライブラリの整理 |

---

## 4. Agent 欄がこのUIの中心

```
│ Agent                                      │
│                                            │
│ > Compare these papers                     │
│ > Find research gaps                       │
│ > Design experiment                        │
```

従来の研究ツールは、検索ボタン・フィルタ・PDF Viewer・タグ・フォルダを
**ユーザー自身が操作** します。

Research OS では、操作の主語が Agent に移ります。

```
Human → Goal → Agent → Plan → Tool / MCP / Skill → Result
```

たとえば `> Find recent tactile world model papers` の一言で、Agent が次を実行します。

1. arXiv 検索 ＋ alphaXiv `discover_papers`
2. Paperpile 重複確認
3. Metadata 取得
4. Abstract 評価
5. 上位論文の選択
6. PDF 解析（alphaXiv `answer_pdf_queries` / `get_paper_content`）
7. 比較
8. Paperpile 登録
9. Knowledge Graph 更新

---

## 5. 裏側のアーキテクチャ

```
                         Research OS TUI
                               │
                          User Intent
                               │
                               ▼
                         Research Agent
                               │
                   ┌───────────┼────────────┐
                   ▼           ▼            ▼
                 Skills       MCP        Subagents
                   │           │
        ┌──────────┼───────┐   ├─ Paperpile
        ▼          ▼       ▼   ├─ arXiv
      Search     Review   Gap  ├─ alphaXiv
                             │ ├─ GitHub
                             │ └─ Neo4j
                             ▼
                         Claude Code
                             │
                   ┌─────────┼─────────┐
                   ▼         ▼         ▼
                 Code    Experiment   Docs
```

**画面と Skill の対応**

| 画面 | 主に使う Skill |
|------|---------------|
| Papers / Review | Paperpile Skill（literature-review） |
| Graph | Graph 用 Skill |
| Hypothesis | Research Gap / Hypothesis Skill |
| Run | Experiment / Coding Skill |

ユーザーは Skill そのものをほぼ意識しません。裏側で自動選択されます。

```
ユーザー
  ↓  「この論文3本比較して」
Router
  ↓
literature-review Skill
  ↓
Paperpile MCP
  ↓
結果
```
