# Research OS — Venue Strategy（投稿先戦略）機能

## Status

Proposed（画面構成と Graph の変更は [ADR-0001](../adr/0001-paper-tab-and-venue-registry.md) で決定）

## 1. 概要

現行の Research OS は「検索 → 読解 → 比較 → 仮説化 → 実験」までを扱い、
closed-loop 構想（`docs/new_features/new_feature_20260917.md`）は Claim と Evidence による論文化までを扱う。
しかし **「どの学術誌・国際会議に、いつ、何を揃えて投稿するか」** を扱う仕組みがない。

本機能は、`docs/reference/paper_strategy.md`（ロボティクス分野の学術誌・国際会議の整理と修士論文の投稿戦略）を
Research OS のデータと画面に落とし込む。

```text
研究課題の設定 → 関連論文のサーベイ → 仮説・理論の構築 → 実機実験
  → 定量評価・比較実験 → 論文執筆 → RA-L / ICRA / IROS
  → 研究の発展・追加検証 → T-RO / IJRR
```

この流れのうち、次を Research OS 上で追跡可能にする。

- 投稿先（Venue）を研究オブジェクトとして管理し、文献探索・Graph・論文化で共有する
- 研究テーマと RQ を最上位オブジェクトとして持ち、文献・仮説・実験のカバレッジを見る
- 投稿準備の充足度を Evidence / Claim から判定し、投稿先の選択を Agent が支援する
- 締切・投稿規定を巡回して変化を検知する

## 2. 方針

| 方針 | 内容 |
|---|---|
| Publish タブは作らない | closed-loop の **Paper 画面** に投稿戦略を含める。論文を書く場所と投稿先を決める場所を分けない |
| Venue は共有データ | Venue レジストリは画面に属さず、Papers・Graph・Paper・Intel 巡回のすべてから参照する（Intel の監視対象レジストリと同じ位置付け） |
| 判定の一本化 | 投稿準備チェックは closed-loop の Research Gate R6（Paper Gate）に統合する。別のゲートを作らない |
| 人間が決める | 投稿先の決定・投稿の実行は人間が行う。Agent は比較と根拠の提示まで |

## 3. Venue レジストリ

### 3.1 属性

| 属性 | 内容 | 例 |
|---|---|---|
| `venue_id` | 一意な ID | `ral` |
| `name` / `abbrev` | 正式名称・略称 | IEEE Robotics and Automation Letters / RA-L |
| `type` | `journal` ／ `conference` ／ `magazine` | `journal` |
| `publisher` | 出版元・主催 | IEEE |
| `ieee_related` | IEEE 関連か | `true` |
| `scope` | 主な研究領域（タグ） | Robot Learning, Manipulation, Perception |
| `fit` | 現在の研究テーマとの相性（`◎` ／ `○` ／ `△`） | `◎` |
| `priority` | 投稿優先度（1 が最優先。未設定可） | `1` |
| `tier` | 投稿戦略上の位置付け（`first_result` ／ `foundational` ／ `mature_journal`） | `first_result` |
| `links` | 公式サイト・CFP・投稿規定の URL | — |
| `policies` | 投稿規定の要点（ページ数、二重投稿、既発表の扱い、連携制度） | RA-L 採択論文を ICRA / IROS で発表できる制度 |
| `deadlines` | 年度ごとの締切（[6](#6-締切投稿規定の監視) で巡回して更新） | — |
| `retrieved_at` / `updated_at` / `source_url` | 来歴（Intel の来歴属性と共通） | — |

`fit` と `priority` は研究テーマに依存するため、レジストリ本体ではなく **研究プロファイル側（[4](#4-研究プロファイル)）で上書き可能** にする。
レジストリには既定値だけを置く。

### 3.2 初期登録

`docs/reference/paper_strategy.md` §2・§3 の 15 件（学術誌 10、国際会議 5）を初期登録する。

| priority | Venue | type | fit | tier |
|---|---|---|---|---|
| 1 | RA-L | journal | ◎ | first_result |
| 2 | ICRA | conference | ◎ | first_result |
| 3 | IROS | conference | ◎ | first_result |
| 4 | RSS | conference | ◎ | foundational |
| 5 | T-RO | journal | ◎ | mature_journal |
| 5 | IJRR | journal | ◎ | mature_journal |
| — | Robotics and Autonomous Systems | journal | ◎ | — |
| — | Autonomous Robots | journal | ◎ | — |
| — | Science Robotics | journal | ◎ | — |
| — | RAM / IJSR / JFR / CASE / RO-MAN | — | ○ | — |
| — | RCIM | journal | △ | — |

### 3.3 データ配置

Venue レジストリは研究プロジェクトをまたいで使うため、Research OS 側の共有データとして持つ。

```text
registry/
├── venues.yaml        # Venue レジストリ（本機能）
└── companies.yaml     # Intel 監視対象レジストリ（design.md §6.2）
```

### 3.4 Knowledge Graph

| From | 関係 | To | 用途 |
|---|---|---|---|
| Paper | `published_in` | Venue | 掲載先での絞り込み・集計 |
| Paper Draft | `targets` | Venue | 自分の論文の投稿先（候補を含む） |
| Venue | `co_presents_with` | Venue | RA-L → ICRA / IROS のような連携制度 |

- `Venue` ノードを追加する。`Paper Draft` は closed-loop の `Paper Section` 群をまとめる上位オブジェクトとして扱う。
- 掲載先情報は arXiv / alphaXiv だけでは不足するため、Semantic Scholar / OpenAlex の venue メタデータで補う（todo の「将来」から優先度を上げる）。

### 3.5 Papers 画面での利用

- Venue フィルタ：`> RA-L・T-RO・IJRR に載った tactile 論文だけ`
- 優先 Venue での重み付け：関心フィードと検索結果のランキングに `priority` を反映できる（既定はオフ）
- サーベイの網羅度：優先 Venue ごとに、読了・レビュー済みの論文数を表示する

## 4. 研究プロファイル

研究テーマと RQ を、Hypothesis チェーン（Problem → Research Gap → Research Question → Hypothesis → Experiment）の **上位** に置く。

```yaml
# research/profile.yaml
theme: Vision-Tactile JEPA World Models for Failure-Aware Long-Horizon Robotic Manipulation
theme_ja: 失敗認識型の長期ロボットマニピュレーションに向けた視覚・触覚統合JEPA世界モデル
research_questions:
  - id: RQ1
    title: Vision-Tactile Representation
    question: 視覚・触覚情報によって接触・滑り・把持状態を正確に表現できるか
  - id: RQ2
    title: Predictive World Model
    question: JEPA型世界モデルによって将来の状態や操作失敗を予測できるか
  - id: RQ3
    title: Failure-Aware Manipulation
    question: 失敗予測を再計画・回復に利用することで長期タスクの成功率を向上できるか
venue_overrides:
  ral:  { fit: "◎", priority: 1 }
  icra: { fit: "◎", priority: 2 }
survey_venues: [ral, tro, ijrr, icra, iros, rss]
```

- closed-loop の成果物ディレクトリ（`research/questions.yaml`）とは、`research_questions` の ID で対応づける。
- 関心プロファイル `interests.yaml`（design.md §3.2）のトピックは、ここから初期生成できる。

**RQ カバレッジ**

| RQ | 関連論文 | 仮説 | 実験 | Evidence |
|---|---|---|---|---|
| RQ1 | 12 | 2 | 1 | 1 |
| RQ2 | 8 | 1 | 0 | 0 |
| RQ3 | 3 | 0 | 0 | 0 |

（数値は表示イメージ）。「RQ3 の先行研究が薄い」「RQ2 は実験が未着手」を Agent が指摘できるようにする。

## 5. 投稿パイプライン（Paper 画面）

### 5.1 投稿ステージ

```text
planning → drafting → ready → submitted → under_review → accepted / rejected
                                              └─ revision ─┘
```

```yaml
# paper/submission.yaml
draft_id: PD-001
title: Vision-Tactile JEPA for Failure Prediction on SO-101
target_venue: ral
candidate_venues: [ral, icra, iros]
stage: drafting
requirements:          # 5.2 の投稿準備チェックリスト
  - id: REQ-arch
    text: Vision-Tactile JEPA アーキテクチャの記述
    claim_ids: [CLM-001]
  - id: REQ-ablation
    text: 視覚のみと視覚・触覚統合モデルの比較
    evidence_ids: []
  - id: REQ-failure-eval
    text: 失敗予測の定量評価
    evidence_ids: [EVD-001]
  - id: REQ-real-robot
    text: SO-101 による実機評価
    evidence_ids: []
decided_by: null       # 人間が投稿先を確定したら記録
```

### 5.2 投稿準備チェックリスト

`paper_strategy.md` §5 Step 2 の要件を、必須 Evidence / Claim として定義する。

| 要件 | 判定に使うもの |
|---|---|
| Vision-Tactile JEPA アーキテクチャ | Claim（Method セクション）が存在し承認済み |
| 視覚のみ vs 視覚・触覚統合の比較 | Ablation の Evidence |
| 失敗予測の定量評価 | Failure AUC 等の Evidence |
| SO-101 による実機評価 | 実機 Run 由来の Evidence |

- 判定は Research Gate **R6（Paper Gate）** に統合し、結果は `pass / conditional / fail` と未充足項目で表示する。
- 要件テンプレートは Venue の `tier` ごとに持つ（`first_result` と `mature_journal` で要求水準を変える）。

### 5.3 投稿先の比較

Agent が、成果の成熟度・新規性・実験結果・投稿時期（締切）を並べて候補を比較する。

```
> Compare RA-L, ICRA and IROS for PD-001

          RA-L          ICRA          IROS
締切      通年          (CFP 参照)     (CFP 参照)
要件充足  3/4           3/4            3/4
不足      実機評価      実機評価       実機評価
備考      ICRA/IROS 発表制度あり
```

- 締切は [6](#6-締切投稿規定の監視) の巡回結果を参照する。未取得なら「未確認」と明示し、推測で埋めない。
- 投稿先の確定は人間が行い、`decided_by` に記録する。

### 5.4 ジャーナル版への発展チェック

`paper_strategy.md` §5 Step 3 の「単なる論文の延長ではなく、新しい技術的貢献と十分な追加検証が必要」を仕組みで担保する。

- 会議版 Paper Draft と、ジャーナル版 Paper Draft の Claim 集合を比較し、**新規 Claim** と **追加 Evidence** を一覧にする。
- 追加の検討観点（異なるタスクへの汎化、長期タスク、World Model による再計画、Failure Recovery Policy、環境・物体の頑健性）を要件テンプレートとして持つ。
- `> What is new in PD-002 compared to PD-001?`

### 5.5 Agent 指示例

- `> Which venue fits PD-001 best right now?`
- `> List missing requirements for RA-L`
- `> Show RQ coverage`
- `> What is new in the journal version?`

## 6. 締切・投稿規定の監視

Intel の巡回ジョブ基盤（design.md §6、実行基盤は ADR で決定予定）に、Venue の CFP ページを監視対象として載せる。

| 処理 | 頻度 |
|---|---|
| CFP・締切の確認 | 週 1 回（締切 30 日前からは毎日） |
| 投稿規定ページの変更確認 | 週 1 回 |

- 締切を抽出して `deadlines` を更新し、ステータスバーにカウントダウンを出す（例：`ICRA ◔ 21d`）。
- 投稿規定（二重投稿、既発表の扱い、RA-L と会議の連携制度など）は年度で変わるため、Intel の Diff 機能で変更を検知する。
- 抽出した締切は `source_url` と `retrieved_at` を必ず保持し、公式ページで確認するまで「未確認」扱いにする。

## 7. 関連する拡張（別項目として扱う）

| 項目 | 内容 | 扱い |
|---|---|---|
| 実験環境アセット | SO-101 / RealSense D435i / XELA uSPa11（`status: planned`）/ LeRobot / SmolVLA を登録し、Run の実験定義と Review 比較表の Robot・Sensor 軸で使う | Run の拡張として todo に記載 |
| 論文 PDF の入手経路 | JAIST 電子図書館・IEEE Xplore など、どの経路で PDF を読めるか | 未決（将来） |
| IEEE / RAS 会員の損益判断 | 参加する会議が決まった時点で、会費と参加費割引を比較 | 保留 |

## 8. 段階的な実装

| Phase | 内容 | 画面への影響 |
|---|---|---|
| A | Venue レジストリ・研究プロファイルのスキーマ、初期登録、Graph の `Venue` ノード、Papers の Venue フィルタ | 小 |
| B | Paper 画面：投稿ステージ、投稿準備チェックリスト（R6 統合）、投稿先比較、ジャーナル版の差分チェック | Paper タブ追加 |
| C | 締切・投稿規定の巡回、ステータスバーの締切表示 | ステータスバー |

## 9. 未決事項

- Venue の掲載先メタデータの取得元（Semantic Scholar / OpenAlex / DBLP）
- 締切抽出の方法（CFP ページの HTML 抽出か、手動登録を既定にするか）
- 要件テンプレートを Venue ごとに持つか、`tier` ごとに持つか
- `Paper Draft` オブジェクトを closed-loop のスキーマへ正式に追加するか
