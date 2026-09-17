# Research OS — AI-Native Closed-Loop Research Feature

## Status

Proposed

## 1. 概要

Research OS に、研究活動を次の閉ループとして管理・実行する機能を追加する。

```text
研究アイデア
  → 文献調査
  → 比較・Research Gap 抽出
  → 理論化・仮説化
  → 実装
  → 実験
  → 評価
  → 仮説修正
  → 論文化
  → 次の研究アイデア
```

現行仕様の `Papers → Review → Graph → Hypothesis → Run` を維持しつつ、次を拡張する。

- 仮説、実験、証拠、主張を永続化し、追跡可能にする
- 評価結果から仮説・実験・実装へ戻るフィードバックループを作る
- 論文を研究終了後の成果物ではなく、研究中に継続更新するオブジェクトとして扱う
- Claude Code を実装支援だけでなく、研究ループ全体の実行エンジンとして利用する
- Human-in-the-Loop と Research Gate により、AI の提案と人間の科学的判断を分離する

本機能は特定分野専用ではない。SO-101、Vision-Tactile JEPA、Spatial AI、Marble を用いた修士研究を最初のリファレンスユースケースとする。

---

## 2. 背景と課題

現行の Research OS は、文献検索から実験実行までの流れを一つの TUI で扱う設計になっている。一方、研究では実験を一度実行して終わるのではなく、評価結果をもとに仮説、理論、実装、実験条件を繰り返し修正する必要がある。

現在の仕様に不足している主な要素は次のとおりである。

1. 仮説に対する支持証拠・反証証拠・信頼度の管理
2. 仮説と実験、データセット、結果、論文中の主張との追跡可能性
3. Baseline、Ablation、Seed、統計評価を含む実験 Registry
4. 評価結果から適切な研究フェーズへ戻るルーティング
5. 研究の品質を段階的に確認する Research Gate
6. 研究中に Abstract、Method、Experiments などを更新する Paper Workspace
7. 複数の専門 Agent による提案と批判的レビュー

---

## 3. 目的

Research OS を、研究情報を表示するツールから、仮説と証拠を中心に研究を継続的に回す **AI-native Research Engineering Environment** へ拡張する。

### 3.1 成功状態

ユーザーは Research Question を登録した後、次の一連の作業を Research OS 内で行える。

1. 関連文献を検索し、既存研究との差分を確認する
2. Research Gap から検証可能な Hypothesis を作る
3. Hypothesis を検証する最小実験、Baseline、Ablation を設計する
4. Claude Code に実装とテストを依頼する
5. 実験を再現可能な設定で実行する
6. 統計評価により支持・反証・判定保留を記録する
7. 結果に応じて仮説、実装、実験へ戻る
8. Evidence に裏付けられた Claim のみを論文へ反映する

---

## 4. 基本コンセプト

### 4.1 Research Loop

```text
Idea
  ↓
Papers → Review → Graph
  ↓
Hypothesis / Theory
  ↓
Implementation
  ↓
Run / Experiment
  ↓
Evaluation
  ├─ 仮説が弱い → Hypothesis
  ├─ 実装に問題 → Implementation
  ├─ 証拠が不足 → Run
  └─ 証拠が十分 → Paper
                         ↓
                    Reviewer View
                         ↓
                       Idea
```

### 4.2 Traceability Chain

研究成果は次のチェーンで追跡する。

```text
Problem
  → Research Gap
  → Research Question
  → Hypothesis
  → Experiment
  → Run
  → Evidence
  → Claim
  → Paper Section
```

Claim は、対応する Evidence が存在しない限り `supported` にできない。

### 4.3 Agent Orchestration

```text
Human
  → Goal
  → Research Agent
  → Plan
  → Skill / MCP / Subagent / Claude Code
  → Artifact
  → Human Review
```

---

## 5. 画面仕様の拡張

現行の5画面を維持し、`Evaluation` と `Paper` を追加する。

| 画面 | 役割 | 主な成果物 |
|---|---|---|
| Papers | 文献探索 | Paper objects |
| Review | 比較、限界、新規性の分析 | Review reports |
| Graph | 研究領域と証拠関係の構造化 | Knowledge Graph |
| Hypothesis | RQ、仮説、理論、予測の管理 | Hypothesis objects |
| Run | 実装、実験条件、実行管理 | Experiment / Run objects |
| Evaluation | 統計評価、Ablation、反証検討 | Evidence objects |
| Paper | Claim と Evidence に基づく論文更新 | Paper sections |

ナビゲーションは次の構成とする。

```text
Papers │ Review │ Graph │ Hypothesis │ Run │ Evaluation │ Paper
```

### 5.1 Hypothesis 画面

Hypothesis 画面では、仮説を単なる文章ではなく、検証可能な研究オブジェクトとして扱う。

**表示項目**

| 項目 | 内容 |
|---|---|
| ID | `H-001` 形式の一意識別子 |
| Research Question | 仮説が答える問い |
| Statement | 検証可能な仮説文 |
| Prediction | 観測されるべき具体的な結果 |
| Independent Variables | 操作する変数 |
| Dependent Variables | 評価する指標 |
| Baseline | 比較対象 |
| Supporting Evidence | 仮説を支持する文献・実験 |
| Contradicting Evidence | 仮説に反する文献・実験 |
| Confidence | `low / medium / high` |
| Status | `draft / testable / testing / supported / refuted / inconclusive` |

**Agent 指示例**

- `> Convert this research question into testable hypotheses`
- `> Show evidence contradicting H-001`
- `> Find hypotheses without a baseline`
- `> Design the minimum experiment for H-002`

### 5.2 Run 画面

Run 画面を、単一実験の実行画面から Experiment Registry の操作画面へ拡張する。

**必要な機能**

- Hypothesis から Experiment を生成する
- Dataset、Model、Baseline、Ablation、Seed、Metric を固定する
- 実験設定からコードと設定ファイルを生成する
- コード、環境、データ、設定のバージョンを記録する
- 失敗した実行ログも削除せず保存する
- Run 完了後に Evaluation へ結果を引き渡す

### 5.3 Evaluation 画面

Evaluation は結果の可視化だけでなく、科学的主張が成立するかを判定する画面である。

**表示項目**

- Hypothesis と Prediction
- Baseline 比較
- Ablation 結果
- Seed ごとの分散
- 効果量、信頼区間、統計検定
- Failure case と外れ値
- Alternative explanation
- Supporting / Contradicting Evidence
- Reviewer Agent の批判
- 次の推奨アクション

**評価結果によるルーティング**

| 判定 | 戻り先 | アクション |
|---|---|---|
| 仮説が不明確 | Hypothesis | 変数・予測・反証条件を修正 |
| 実装不具合 | Run / Code | テスト追加、実装修正 |
| 実験条件不足 | Run | Baseline、Seed、Ablation を追加 |
| 証拠不足 | Run | 追加データ・追加実験 |
| 仮説を反証 | Hypothesis | 仮説を更新または棄却 |
| 仮説を支持 | Paper | Evidence と Claim を関連付ける |

### 5.4 Paper 画面

論文は最後に一括生成せず、研究開始時から継続更新する。

**セクション**

```text
Abstract
Introduction
Related Work
Method
Experiments
Results
Discussion
Limitations
Conclusion
```

**必須機能**

- Abstract v0.1 を仮説段階で作成する
- Paper Section ごとに Claim を登録する
- Claim から Evidence、Experiment、Hypothesis をたどれる
- 未検証の Claim を警告する
- 結果変更時に影響する文章を検出する
- 引用元を Paper object として関連付ける
- AI 草稿と人間による承認状態を分離する

---

## 6. Research Agent の役割

Agent は独立した判断主体ではなく、専門的な役割と成果物を持つ。

| Agent | 役割 | 成果物 |
|---|---|---|
| Research Scout | 関連論文、データセット、実装を探索 | Literature set |
| Literature Reviewer | 論文の手法・評価・限界を比較 | Review report |
| Novelty Critic | 既存研究との差分と新規性を批判的に検証 | Novelty report |
| Theory Agent | 仮説、変数、数式、予測を整理 | Theory artifact |
| Research Engineer | 数式と仕様を実装へ変換 | Source code / tests |
| Experiment Designer | Baseline、Ablation、Seed、Metric を設計 | Experiment config |
| Evaluation Reviewer | 統計、代替説明、失敗例を検討 | Evaluation report |
| Paper Agent | Evidence に基づいて論文を更新 | Paper draft |

### 6.1 批判的 Agent の要件

`Novelty Critic` と `Evaluation Reviewer` は、少なくとも次を確認する。

- 本当に新規性があるか
- 既存研究の単純な組み合わせではないか
- 実験結果から Claim を導けるか
- Confounder や別の説明がないか
- 都合の悪い結果を無視していないか
- Baseline は十分に強いか
- データリークや評価設計の誤りがないか
- 再現可能な条件が記録されているか

---

## 7. Research Object のデータモデル

### 7.1 Hypothesis Object

```yaml
hypothesis_id: H-001
research_question_id: RQ-001
statement: >
  Vision-Tactile latent prediction improves early manipulation
  failure detection compared with vision-only prediction.
prediction:
  metric: failure_auroc
  direction: greater_than
  baseline: vision_only
status: testable
confidence: medium
supporting_evidence: []
contradicting_evidence: []
experiments:
  - EXP-001
owner: human
created_at: 2026-09-16
updated_at: 2026-09-16
```

### 7.2 Experiment Object

```yaml
experiment_id: EXP-001
hypothesis_id: H-001
question: Does tactile input improve early failure prediction?
dataset: so101_grasp_v1
baseline:
  - vision_only
proposed:
  - vision_tactile_jepa
ablations:
  - without_tactile
  - without_depth
  - without_jepa_loss
seeds:
  - 42
  - 123
  - 456
metrics:
  - success_rate
  - failure_auroc
  - failure_f1
  - slip_detection_rate
status: planned
code_revision: null
environment_lock: null
runs: []
```

### 7.3 Run Object

```yaml
run_id: RUN-001
experiment_id: EXP-001
seed: 42
started_at: null
completed_at: null
status: queued
code_revision: null
config_path: experiments/exp_001/config.yaml
dataset_version: so101_grasp_v1
artifact_path: results/exp_001/run_001
log_path: logs/exp_001/run_001.log
metrics: {}
failure: null
```

### 7.4 Evidence Object

```yaml
evidence_id: EVD-001
hypothesis_id: H-001
experiment_id: EXP-001
run_ids:
  - RUN-001
  - RUN-002
  - RUN-003
type: experimental
direction: supporting
summary: Vision-Tactile JEPA improved failure AUROC over vision-only.
statistics:
  effect_size: null
  confidence_interval: null
  p_value: null
limitations: []
review_status: pending_human_review
```

### 7.5 Claim Object

```yaml
claim_id: CLM-001
text: >
  Multimodal latent prediction improves early failure detection
  under the evaluated grasping conditions.
scope: evaluated_so101_grasp_conditions
hypothesis_id: H-001
evidence_ids:
  - EVD-001
paper_sections:
  - results
  - discussion
status: draft
human_approved: false
```

---

## 8. Knowledge Graph の拡張

現行の Node / Edge に、研究過程を表す型を追加する。

### 8.1 Node

```text
Paper / Method / Dataset / Model / Task / Robot / Metric / Research Problem
Research Gap / Research Question / Hypothesis / Experiment / Run / Evidence / Claim / Paper Section
```

### 8.2 Edge

| From | Relation | To |
|---|---|---|
| Paper | `supports` | Hypothesis |
| Paper | `contradicts` | Hypothesis |
| Research Gap | `motivates` | Research Question |
| Research Question | `has_hypothesis` | Hypothesis |
| Hypothesis | `tested_by` | Experiment |
| Experiment | `has_run` | Run |
| Run | `produces` | Evidence |
| Evidence | `supports` | Claim |
| Evidence | `contradicts` | Claim |
| Claim | `written_in` | Paper Section |
| Failure Mode | `triggers` | Experiment |
| Experiment | `uses` | Dataset / Model / Metric |

これにより、`この Claim の根拠は何か`、`反証された仮説はどれか`、`実験されていない仮説はどれか` を Graph から問い合わせられる。

---

## 9. Research Gate

各 Gate は自動チェックと人間の承認を組み合わせる。

| Gate | 名称 | 通過条件 |
|---|---|---|
| R0 | Idea Gate | Problem、対象者、Research Question が明確 |
| R1 | Novelty Gate | 既存研究、差分、競合仮説を確認済み |
| R2 | Theory Gate | 仮説、変数、予測、反証条件、数式を説明可能 |
| R3 | Implementation Gate | Unit test、データ契約、再現環境が存在 |
| R4 | Experiment Gate | Baseline、Ablation、Seed、Metric、停止条件を定義済み |
| R5 | Evidence Gate | 統計、失敗例、代替説明、限界を評価済み |
| R6 | Paper Gate | Claim と Evidence が一致し、人間が承認済み |

**Agent 指示例**

- `> Review whether EXP-001 passes R4`
- `> List all blockers for R5`
- `> Show claims that fail R6 traceability`

Gate の判定結果は `pass / conditional / fail` とし、理由と未解決項目を保存する。

---

## 10. Human-in-the-Loop

AI が生成・実行できる範囲と、人間が最終判断する範囲を分離する。

| 領域 | AI の役割 | 人間の役割 |
|---|---|---|
| 文献検索 | 検索、重複排除、順位付け | 重要文献の確定 |
| 論文整理 | 比較、要約、構造化 | 解釈の確認 |
| 仮説候補 | 候補生成、反証条件の提示 | 採用、修正、棄却 |
| 新規性 | 既存研究との差分提示 | 最終判断 |
| 数式 | 導出補助、実装との照合 | 妥当性の承認 |
| 実装 | コード、テスト、設定生成 | 仕様と安全性の確認 |
| 実験 | 設計候補、実行、記録 | 実世界操作と条件承認 |
| 統計評価 | 集計、検定、可視化 | 解釈と結論の承認 |
| 論文 | 草稿、引用候補、整合性確認 | Scientific Claim の承認 |

次の操作は必ず人間の承認を要求する。

- Hypothesis を `supported` または `refuted` に確定する
- Claim を `approved` にする
- 実ロボットを動かす実験を開始する
- 外部公開用の論文・データ・コードを出力する

---

## 11. 成果物ディレクトリ

Research OS が対象研究リポジトリへ生成する標準構成を次のようにする。

```text
research-project/
├── CLAUDE.md
├── research/
│   ├── problem.md
│   ├── questions.yaml
│   ├── hypotheses.yaml
│   ├── novelty.md
│   └── contributions.md
├── literature/
│   ├── papers.yaml
│   ├── reviews/
│   └── comparisons/
├── theory/
│   ├── formulation.md
│   ├── losses.md
│   └── architecture.md
├── src/
├── tests/
├── experiments/
│   ├── registry.yaml
│   └── configs/
├── results/
│   ├── evidence.yaml
│   ├── tables/
│   ├── figures/
│   └── statistics/
├── logs/
├── paper/
│   ├── claims.yaml
│   ├── abstract.md
│   ├── introduction.md
│   ├── related_work.md
│   ├── method.md
│   ├── experiments.md
│   ├── results.md
│   ├── discussion.md
│   └── limitations.md
└── gates/
    ├── r0.yaml
    ├── r1.yaml
    ├── r2.yaml
    ├── r3.yaml
    ├── r4.yaml
    ├── r5.yaml
    └── r6.yaml
```

---

## 12. リファレンスユースケース

### 12.1 研究テーマ

**Generative Spatial World Augmentation for Failure-Aware Vision-Tactile Robot Learning**

SO-101 を実世界実験基盤、Vision-Tactile JEPA / Latent World Model を主なアルゴリズム、Spatial AI と Marble を環境生成・評価基盤として扱う。

| 要素 | 役割 |
|---|---|
| SO-101 | 実世界実験と Ground Truth |
| RealSense D435i | RGB-D、空間情報 |
| Tactile / Motor Current | 接触、滑り、失敗の観測 |
| Vision-Tactile JEPA | 将来の multimodal latent state 予測 |
| Failure Head | 操作失敗の早期予測 |
| VLA / Policy | 操作方策 |
| Marble | Digital Cousin の生成 |
| Isaac Sim / MuJoCo | 再現可能なシミュレーション評価 |
| Claude Code | 実装、実験、文書更新 |
| Research OS | 研究ループと証拠の統合管理 |

### 12.2 Research Question

> 視覚・触覚・ロボット状態から将来の latent state を予測することで、SO-101 の操作失敗を早期に検出できるか。また、多様な Digital Cousin で評価することで、単一の実環境では発見しにくい failure mode を発見できるか。

### 12.3 初期 Hypothesis

| ID | Hypothesis |
|---|---|
| H-001 | Vision + Tactile は Vision-only より failure prediction を改善する |
| H-002 | Motor Current は専用触覚センサーがない場合の接触情報 proxy として一定の性能を持つ |
| H-003 | JEPA による将来 latent prediction は reactive fusion より早期失敗予測を改善する |
| H-004 | Digital Cousin 群での評価は単一実環境より多くの failure mode を発見する |
| H-005 | Failure 分析から生成条件を更新すると、hard environment の探索効率が上がる |

### 12.4 理論オブジェクトの例

視覚、触覚、ロボット状態を埋め込み、統合 latent state を作る。

```math
z_t = E_v(I_t) \oplus E_t(T_t) \oplus E_s(s_t)
```

行動系列を条件として将来 latent state を予測する。

```math
\hat{z}_{t+k} = P(z_t, a_{t:t+k})
```

JEPA loss は pixel reconstruction ではなく latent prediction に置く。

```math
\mathcal{L}_{JEPA} = D(\hat{z}_{t+k}, \operatorname{sg}(z_{t+k}))
```

予測状態と現在状態から将来の失敗確率を推定する。

```math
p(f_{t+k}=1) = F(z_t, \hat{z}_{t+k})
```

### 12.5 Ablation Matrix

| Model | RGB | Depth | Tactile | Current | JEPA |
|---|---:|---:|---:|---:|---:|
| Vision Baseline | ✓ |  |  |  |  |
| RGB-D | ✓ | ✓ |  |  |  |
| Vision + Current | ✓ |  |  | ✓ |  |
| Vision + Tactile | ✓ |  | ✓ |  |  |
| VT-JEPA | ✓ |  | ✓ |  | ✓ |
| VT-State-JEPA | ✓ | ✓ | ✓ | ✓ | ✓ |

### 12.6 Metrics

| 評価対象 | 指標 |
|---|---|
| Task performance | Success Rate |
| Failure prediction | AUROC、F1、Precision、Recall |
| Early prediction | Time-to-failure、prediction horizon |
| Slip | Slip detection rate |
| Prediction | Latent prediction error |
| Robustness | Environment shift 下の性能低下 |
| Recovery | Failure recovery rate |
| Generalization | Unseen object / unseen environment |

### 12.7 Failure-Driven World Generation

評価で得た failure mode を次の環境生成条件へ反映する。

```text
Robot Policy
  → Evaluation
  → Failure Detection
  → Failure Analysis
  → World Generation Condition
  → Digital Cousins / Hard Environments
  → Simulation Evaluation or Training
  → Robot Policy
```

例：低照度で失敗率が上がる場合は low-light world を増やし、clutter に弱い場合は段階的に物体密度を上げた環境を生成する。

Marble は研究上の主たる新規性には置かず、交換可能な外部 World Generation Provider として扱う。外部サービスの仕様変更があっても、Hypothesis、Experiment、Evidence の中核データモデルが影響を受けない設計とする。

---

## 13. 最小実装範囲（MVP）

最初のリリースでは、次の範囲に限定する。

1. Hypothesis Registry
2. Experiment Registry
3. Run と Evidence の関連付け
4. R4 Experiment Gate の自動チェック
5. Evaluation 画面での支持・反証・判定保留
6. Claim と Evidence の Traceability
7. Paper の Markdown 更新

### 13.1 MVP の対象外

- 自律的な実ロボット操作
- 完全自動の新規性判定
- 完全自動の論文公開
- 全シミュレータへの共通変換
- Marble 固有 API への強い依存
- 複雑なマルチエージェント間交渉

---

## 14. 受け入れ条件

### 14.1 Hypothesis

- [ ] Research Question から複数の Hypothesis を生成・保存できる
- [ ] 各 Hypothesis に Prediction、Metric、Baseline、反証条件を設定できる
- [ ] Supporting / Contradicting Evidence を表示できる
- [ ] 状態変更履歴を保持できる

### 14.2 Experiment / Run

- [ ] Hypothesis から Experiment を作成できる
- [ ] Baseline、Ablation、Seed、Metric がない場合に R4 が警告する
- [ ] 複数 Run を一つの Experiment に関連付けられる
- [ ] コード revision、設定、データ version、ログを記録できる
- [ ] 失敗した Run も削除せず保持できる

### 14.3 Evaluation

- [ ] Run の結果を集約し、Evidence を生成できる
- [ ] `supporting / contradicting / inconclusive` を記録できる
- [ ] Alternative explanation と Limitation を必須入力にできる
- [ ] Reviewer Agent の指摘を保存できる
- [ ] 次に戻る研究フェーズを提案できる

### 14.4 Paper

- [ ] Claim を Evidence と関連付けられる
- [ ] Evidence のない Claim を検出できる
- [ ] Claim の scope が実験条件を超えている場合に警告できる
- [ ] Human approval 前の Claim を公開対象から除外できる
- [ ] Markdown の論文セクションを差分更新できる

---

## 15. 非機能要件

| 項目 | 要件 |
|---|---|
| Reproducibility | Experiment config、Seed、コード、環境、データ version を保存する |
| Traceability | Problem から Claim まで双方向に追跡できる |
| Auditability | Agent の提案、ツール実行、人間の承認を記録する |
| Recoverability | 中断した研究セッションと Run を復元できる |
| Portability | 外部サービスを Provider interface で交換できる |
| Safety | 実ロボット実験と外部公開は人間の承認を要求する |
| Explainability | Gate 判定と Agent 推奨の理由を表示する |
| Extensibility | 新しい Agent、Metric、Simulator、Data source を追加できる |

---

## 16. 実装フェーズ案

| Phase | 実装内容 |
|---|---|
| Phase 1 | Hypothesis / Experiment / Run / Evidence / Claim のスキーマ |
| Phase 2 | Registry の CRUD と TUI 表示 |
| Phase 3 | R4 Gate と Experiment config 生成 |
| Phase 4 | Run 結果の取り込みと Evaluation |
| Phase 5 | Claim-Evidence Traceability と Paper 更新 |
| Phase 6 | Novelty Critic / Evaluation Reviewer |
| Phase 7 | Knowledge Graph 統合 |
| Phase 8 | Failure-driven experiment / world generation loop |

---

## 17. 設計上の原則

1. **仮説中心**：ツールやモデルではなく、検証する Hypothesis を中心にする
2. **Evidence first**：Claim より先に Evidence を管理する
3. **反証可能性**：支持証拠だけでなく、反証条件と矛盾証拠を保持する
4. **再現可能性**：全 Run にコード、環境、データ、設定を関連付ける
5. **人間が結論を握る**：Novelty、Scientific Claim、Conclusion は人間が承認する
6. **閉ループ**：評価結果を次の研究行動へ必ず接続する
7. **段階的自動化**：最初から完全自律を目指さず、MVP から自動化範囲を広げる
8. **外部サービス非依存**：Marble、Paperpile、alphaXiv、Neo4j などは交換可能にする

---

## 18. 今後の設計判断

次の項目は実装前に ADR で決定する。

- Research Object の永続化方式（YAML / SQLite / Graph DB）
- TUI フレームワーク
- Agent orchestration の実装方式
- Knowledge Graph の永続化先
- Experiment runner と sandbox の境界
- Human approval と audit log のデータモデル
- Paper 差分更新と Citation 管理の方式
- 外部 World Generation Provider の interface

