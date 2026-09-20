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
  - [2.6 Intel — 企業・産業の動向を監視する](#26-intel--企業産業の動向を監視する)
- [3. ステータスバー（外部接続）](#3-ステータスバー外部接続)
  - [3.1 alphaXiv MCP](#31-alphaxiv-mcp)
- [4. Agent 欄がこのUIの中心](#4-agent-欄がこのuiの中心)
- [5. 裏側のアーキテクチャ](#5-裏側のアーキテクチャ)
- [6. Intel 監視パイプライン（フィジカルAI企業の動向監視）](#6-intel-監視パイプラインフィジカルai企業の動向監視)

---

## 1. 全体レイアウト

画面は上から **① ナビゲーション → ② 研究対象 → ③ Agent操作 → ④ 接続状態** の4層です。

```
┌────────────────────────────────────────────────────┐
│ Research OS                                        │  ① アプリ名
├────────────────────────────────────────────────────┤
│ Papers │ Review │ Graph │ Hypothesis │ Run │ Intel │  ② 研究フェーズ
├────────────────────────────────────────────────────┤
│                                                    │
│  vision tactile world model                        │  ③ 現在の研究テーマ
│                                                    │
│  Found: 37 papers                                  │
│                                                    │
│  ★ VLA-JEPA                                        │
│  ★ Tactile World Model                             │  ④ 文献・成果物
│  ★ Vision-Tactile Policy                           │
│                                                    │
├────────────────────────────────────────────────────┤
│ Agent                                              │
│                                                    │
│ > Compare these papers                             │
│ > Find research gaps                               │  ⑤ AI Agent操作
│ > Design experiment                                │
│                                                    │
├────────────────────────────────────────────────────┤
│ Paperpile ✓ arXiv ✓ alphaXiv ✓ GitHub ✓ Feeds ✓    │  ⑥ 外部接続
└────────────────────────────────────────────────────┘
```

| # | 要素 | 役割 |
|---|------|------|
| ① | アプリ名 | Research OS のヘッダ |
| ② | 研究フェーズ | Papers / Review / Graph / Hypothesis / Run のタブ切り替え。加えて、フェーズ横断で企業・産業動向を監視する **Intel** タブ（[2.6](#26-intel--企業産業の動向を監視する)） |
| ③ | 現在の研究テーマ | いま扱っているクエリ／テーマ |
| ④ | 文献・成果物 | ヒットした論文やアウトプット一覧 |
| ⑤ | Agent 操作 | 自然言語で Agent に指示する欄（**最重要**） |
| ⑥ | 外部接続 | Paperpile / arXiv / alphaXiv / GitHub / Feeds / MCP の接続ステータス |

> Intel は「検索 → 読解 → 比較 → 仮説化 → 実験」の直列フローには入らない **並走トラック** です。
> 毎日の巡回で得た論文・技術動向を Papers へ、事業化の動向を Hypothesis（研究テーマ探索）へ流し込みます。

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

Intel（[2.6](#26-intel--企業産業の動向を監視する)）が追加する Node：
`Company`（企業・研究組織）／ `Product` ／ `Customer` ／ `Event`（事業イベント）

**Edge の種類**

| From | 関係 | To |
|------|------|-----|
| Paper | `uses` | Method |
| Paper | `evaluates_on` | Dataset |
| Paper | `extends` | Paper |
| Paper | `solves` | Problem |
| Method | `related_to` | Method |
| Company | `develops` | Model |
| Company | `provides` | Product |
| Product | `uses` | Model |
| Customer | `adopts` | Product |
| Company | `announces` | Event |

Intel 由来の Edge / Node の詳細（時間・根拠・来歴の管理を含む）は [6.6](#66-ナレッジグラフ拡張と来歴管理) を参照。

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

### 2.6 Intel — 企業・産業の動向を監視する

米国のフィジカルAI企業（ロボット基盤モデル、ヒューマノイド、物流・製造ロボット、自動運転、AI基盤・シミュレーション）の
**公式ブログ・研究論文・ニュース** を自動巡回し、次の 2 つの観点で動向を把握する画面です。

| 観点 | 見るもの |
|------|----------|
| **Technology Intelligence**（技術革新） | VLA / World Model・World Action Model / ロボット強化学習・模倣学習 / Vision-Tactile Learning / Agentic Robotics / ロボット基盤モデル |
| **Business Intelligence**（ビジネスイノベーション） | 新製品・新サービス / PoC から商用導入への移行 / ビジネスモデルの変化 / 新規顧客・提携 / 売上・ARR・ROI / 新市場への参入 |

単なる新着要約ではなく、**技術的な研究成果が顧客価値や新規事業にどうつながっているか** を追跡するのが目的です。

**画面イメージ**

```
Intel — updated 2026-09-21 06:00          Feeds ✓ 9/9
[ Tech ] [ Business ] [ Sources ]     Filter: All companies / Last 7 days

  ★ 2026-09-17  Ambi Robotics    Tech + Biz
      Agentic Robotics でロボットプログラムを自動改善
      claim: 数週間かかった調整を約10時間で解決（企業発表）
  ★ 2026-09-10  Skild AI         Biz
      商用導入から10か月で ARR 1億ドル超 / 有料顧客60社超
      claim: 企業発表（ARR は認識済み売上と異なる）
    2026-09-17  Figure AI        Tech
      Helix 2.5：未経験の30家庭環境での汎化を検証

  ⟳ Updated: 過去記事 3 件に変更あり（Diff を表示）
```

**タブ**

| タブ | 内容 |
|------|------|
| Tech | Technology Intelligence の抽出結果（モデル名・アーキテクチャ・評価・論文・OSS・実機） |
| Business | Business Intelligence の抽出結果（商用化段階・顧客・経済性・事業モデル）とイベントの時系列 |
| Sources | 監視対象ソースの一覧・巡回状態・追加／削除・優先度 |

**Agent への指示例**

- `> Summarize this week's updates from Physical Intelligence and Skild AI`
- `> Compare Figure and Skild on their commercialization stage`
- `> Which companies moved from PoC to production deployment recently?`
- `> Add Dexterity's blog to the watch list`
- `> Send papers cited in these posts to Papers`
- `> Generate the weekly intelligence report`

> Intel は「論文の外側」にある、企業の研究成果と事業化の動きを Research OS に取り込む入口です。
> 収集した情報は Knowledge Graph（Graph 画面）に統合され、企業間比較・トレンド分析・研究テーマ探索に使われます。

---

## 3. ステータスバー（外部接続）

画面下部 `Paperpile ✓  arXiv ✓  alphaXiv ✓  GitHub ✓  MCP ✓` はステータスバーです。

| 表示 | 意味 |
|------|------|
| Paperpile ✓ | Paperpile ライブラリへアクセス可能 |
| arXiv ✓ | 新規論文検索が可能 |
| alphaXiv ✓ | alphaXiv MCP 経由で論文探索・全文解析・研究者検索が可能 |
| GitHub ✓ | コード・OSS・実装の検索が可能 |
| Feeds ✓ | Intel の監視対象ソース（企業ブログ・ニュース等）を巡回できている。`Feeds ✓ 8/9` のように取得成功数を併記し、失敗ソースがあれば警告表示にする |
| MCP ✓ | MCP Server 群が正常 |

**将来の拡張イメージ**

```
Paperpile ✓   arXiv ✓   alphaXiv ✓   GitHub ✓   Feeds ✓   Semantic Scholar ✓   OpenAlex ✓
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
| Intel | Intel Watch Skill（巡回・要約・抽出・比較・週次レポート。[6](#6-intel-監視パイプラインフィジカルai企業の動向監視)） |

Intel は定期実行（毎日・週次）を伴うため、対話中の Agent ループとは別に **バックグラウンドの巡回ジョブ** を持ちます
（実行基盤は未決。ADR で決定する。[6.8](#68-未決事項)）。

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

---

## 6. Intel 監視パイプライン（フィジカルAI企業の動向監視）

[2.6 Intel](#26-intel--企業産業の動向を監視する) の裏側の仕様です。
元メモ: `docs/memo.md`（企業ごとの公式ブログ URL 一覧・具体的な注目トピックを含む）。

### 6.1 全体パイプライン

```
企業ブログ・研究論文・ニュース
        │
        ▼
定期巡回・新着検知（Feeds）
        │
        ▼
本文抽出 → LLM 要約（日本語）
        │
        ├──────────────┐
        ▼              ▼
Technology         Business
Intelligence       Intelligence
        │              │
        └──────┬───────┘
               ▼
    企業間比較・トレンド分析
               │
               ▼
        Knowledge Graph
               │
               ▼
   週次レポート・研究テーマ探索
```

要点は、**技術動向と事業化動向を別々に抽出** し、後段で突き合わせることです。

### 6.2 監視対象レジストリ

監視対象は企業単位の **レジストリ** として管理します。カテゴリは次の 5 つです。

| # | カテゴリ | 例 | 見る目的 |
|---|----------|-----|----------|
| 1 | ロボット基盤モデル・World Model | Physical Intelligence / Skild AI / Figure AI / World Labs / 1X Technologies / Generalist AI | VLA・World Model の技術動向。研究テーマ「Vision-Tactile JEPA World Model for Long-Horizon VLA」との関連が高い。モデル提供・ライセンス・提携などのビジネスモデル |
| 2 | ヒューマノイド・汎用ロボット | Boston Dynamics / Agility Robotics / Apptronik / Sunday Robotics / Tesla | 工場・物流への実導入、量産体制、RaaS。**技術デモと顧客現場での継続運用を区別** して分析 |
| 3 | 物流・製造・産業ロボット | Amazon Robotics / Dexterity / Ambi Robotics / Intrinsic / FieldAI | 実顧客現場での AI の経済的価値の検証（導入・保守・改善コストなど） |
| 4 | 自動運転・自律移動 | Waymo / Nuro / Waabi / Zoox | World Model・Sim2Real・安全性・継続学習の知見、商用運行・Fleet Management |
| 5 | AI基盤・シミュレーション | NVIDIA / Google DeepMind / World Labs / Intrinsic | 開発環境・学習基盤（Isaac / GR00T / Cosmos / Gemini Robotics など） |

**レジストリの主な属性**

| 属性 | 内容 |
|------|------|
| `name` / `category` | 企業名、所属カテゴリ（複数可。例：Intrinsic はカテゴリ 3 と 5） |
| `org_type` | `company`（独立企業）／ `research_org`（研究組織）／ `business_unit`（事業部門） |
| `origin_country` / `us_presence` | 創業国と米国拠点の有無 |
| `parent` | 親組織と有効期間（`valid_from` / `valid_to`） |
| `sources` | 公式ブログ・ニュース・GitHub・論文などの URL、RSS の有無、記事抽出方法 |
| `priority` | 巡回優先度（初期監視対象は最優先） |

**企業と研究組織・出自を区別する理由**：技術の開発主体を誤らないためです。例：

- Google DeepMind は Google の研究組織であり、独立した米国企業ではない。
- Intrinsic は 2026 年 2 月に Alphabet 傘下の独立事業から Google 内の事業へ移行した（親組織の変遷は `valid_from` で保持する）。
- 1X Technologies（ノルウェー創業）と Waabi（カナダ発）は米国にも拠点を持つ。厳密な米国発企業とは区別して管理する。

**初期監視対象（9 社・組織）**

| 企業・組織 | 主な監視目的 |
|------------|--------------|
| Physical Intelligence | VLA、ロボット基盤モデル |
| Skild AI | 汎用ロボット基盤モデルの商用化 |
| Figure AI | ヒューマノイド、VLA、量産 |
| World Labs | World Model、空間知能 |
| Generalist AI | 汎用ロボット学習 |
| Dexterity | World Model、触覚、物流自動化 |
| Ambi Robotics | Agentic Robotics、商用運用 |
| NVIDIA | GR00T、Cosmos、Isaac |
| Google DeepMind | Gemini Robotics、VLA |

**監視設定（例）**

```json
{
  "companies": [
    "Physical Intelligence", "Skild AI", "Figure AI", "World Labs",
    "Generalist AI", "Dexterity", "Ambi Robotics", "NVIDIA", "Google DeepMind"
  ],
  "check_frequency": "daily",
  "summary_language": "ja",
  "topics": [
    "VLA", "World Model", "Robot Learning", "Agentic Robotics",
    "Commercial Deployment", "Business Model"
  ],
  "track_article_updates": true
}
```

実装時は、企業ごとの `sources`（公式ブログ URL・RSS の有無・記事抽出方法）、`org_type`、`parent` を追加する。

### 6.3 抽出スキーマ

LLM 要約時に、1 記事から Technology / Business を別々の構造化データとして抽出します。

**Technology Intelligence**

| 分類 | 抽出項目 |
|------|----------|
| 技術 | VLA、World Model、RL、触覚、Agentic Robotics |
| モデル | モデル名、アーキテクチャ、入力モダリティ |
| 学習 | 模倣学習、強化学習、自己教師あり学習 |
| 評価 | 成功率、汎化性能、ベンチマーク |
| 論文 | arXiv、学会論文、研究記事 |
| OSS | GitHub、学習済みモデル、データセット |
| 実機 | 対象ロボット、センサー、計算基盤 |

記事中の論文・GitHub リンクは **Papers（2.1）の検索・登録パイプラインへ引き渡す**。

**Business Intelligence**

| 分類 | 抽出項目 |
|------|----------|
| 商用化 | PoC、試験導入、正式導入、量産、サービス開始 |
| 顧客 | 導入企業、対象業界、対象業務 |
| 経済性 | 価格、売上、ARR、ROI、導入・運用コスト |
| 実運用 | 稼働時間、成功率、スループット、人間の介入率 |
| 事業戦略 | 提携、M&A、資金調達、新規事業 |
| 事業モデル | API、SaaS、RaaS、ライセンス、ハードウェア販売 |
| 根拠 | 情報源 URL、発表日、実施日、第三者検証の有無 |

**数値の扱い**：売上・ARR・導入数などの数値は、既定で「企業発表（`company_claimed`）」として保存する。
ARR は認識済み売上高とは異なるため、指標の種類を明示する。第三者検証があれば `third_party_verified` に更新する。

### 6.4 監視頻度と更新追跡

| 処理 | 頻度 |
|------|------|
| 企業ブログの新着確認 | 毎日 |
| 新規論文の確認 | 毎日 |
| GitHub リポジトリの更新確認 | 毎日 |
| 新着記事の要約 | 新着検知時 |
| 企業間の比較分析 | 週 1 回 |
| 技術・ビジネスのトレンド分析 | 週 1 回 |
| 過去記事の変更確認 | 定期的 |

**過去記事の変更追跡**：新着記事だけでなく、既存記事の更新・撤回・製品の終了などを検知する。
取得時に本文のスナップショット（ハッシュ）を保存し、変化があれば Diff と `updated_at` を記録して Intel 画面の
`⟳ Updated` に表示する。過去の発表内容が後に変更・終了された場合、Graph 上の Event も更新対象にする。

### 6.5 事業化ステージの区別

技術発表から事業化までの経緯を追跡するため、同じ企業の発表でも **段階の異なるイベント** として区別して保存する。

| # | イベント段階 | 例 |
|---|--------------|-----|
| 1 | 技術発表 | 新しい VLA を発表した |
| 2 | 実機統合 | VLA を実機に統合した |
| 3 | 試験導入 | 顧客企業がロボットの試験導入を開始した |
| 4 | 本番運用 | 顧客企業が本番運用を開始した |
| 5 | 継続運用の実績 | 継続運用の実績が公開された |

技術デモ（1〜2）と顧客現場での継続運用（4〜5）を混同しないことが、Business Intelligence の分析品質の要になる。

### 6.6 ナレッジグラフ拡張と来歴管理

企業・技術・製品・顧客・論文を Knowledge Graph（[2.3](#23-graph--研究領域の構造理解)）で一元管理する。

```
Company ──develops──▶ Model ──uses──▶ Method（技術）
   │                    ▲                 ▲
   │ provides           │ uses            │ describes
   ▼                    │                 │
Product ────────────────┘               Paper
   ▲
   │ adopts
Customer

Company ──announces──▶ Event
```

- 「技術（Technology）」は既存の `Method` Node で表現し、新規 Node は追加しない。
- 追加する Node：`Company` ／ `Product` ／ `Customer` ／ `Event`。`Event` は 6.5 の段階（`stage`）を持つ。

**時間・根拠・来歴（すべての Event / 関係に付与）**

| 属性 | 内容 |
|------|------|
| `announced_at` | 発表日 |
| `occurred_at` | 実施日（発表日と異なる場合） |
| `retrieved_at` | 情報取得日 |
| `updated_at` | 更新日 |
| `source_url` | 情報源 URL |
| `reliability` | 情報の信頼性（`company_claimed` ／ `third_party_verified`） |
| `changes` | 過去の発表からの変更点（6.4 の Diff への参照） |

### 6.7 出力

| 出力 | 内容 | 頻度 |
|------|------|------|
| Intel フィード | Tech / Business 別の新着・更新の一覧（2.6） | 新着検知時 |
| 企業間比較 | 商用化段階・事業モデル・技術方針の比較 | 週 1 回 |
| トレンド分析 | VLA→World Action Model、視覚のみ→Vision-Tactile、模倣学習と強化学習の統合、Agentic Robotics による自己改善 など | 週 1 回 |
| 週次レポート | 上記をまとめた日本語レポート | 週 1 回 |
| 研究テーマ・事業機会の探索 | 企業・技術・顧客・市場の関係から、異なる領域の接点を探索し Hypothesis（2.4）の入力にする | 随時 |

最終的に、次の問いに答えられる Research OS を目指す。

> **「フィジカルAIの技術革新は、どのような新しい顧客価値やビジネスモデルを生み出しているのか？」**

### 6.8 未決事項

- **巡回の実行基盤**：TUI プロセス外のスケジューラ／常駐ワーカーが必要。方式（cron・systemd timer・常駐デーモン・TUI 起動時のキャッチアップなど）は ADR で決定する。
- **本文取得の方法**：RSS/Atom、HTML 抽出、MCP（fetch 系）のどれを既定にするか。robots.txt・利用規約・レート制限の扱い。
- **要約・抽出のコスト**：毎日の LLM 呼び出し量と、新着のみ要約する運用の徹底。
- **Feeds の保存先**：記事本文・スナップショット・抽出結果を Neo4j と別ストアのどちらに持つか。
- **論文との突き合わせ**：記事内の論文言及を Papers の重複排除（2.1）とどう統合するか。
