# Robotics Journals & Conferences — IEEE会員資格と論文投稿戦略

## 1. IEEE会員になる必要はあるか？

**結論：IEEEの会員にならなくても、ロボティクス分野の学術誌への論文投稿や国際会議への参加は基本的に可能です。**

IEEE会員資格は論文投稿の必須条件ではありません。IEEE会員になることで、学術情報へのアクセスや国際会議の参加費割引などの特典を受けられます。

JAISTの学生であれば、大学が契約する電子ジャーナルも利用できるため、まずは大学の図書館サービスを活用することを推奨します。

### IEEE会員資格の必要性

| やりたいこと | IEEE会員は必要？ |
|---|---|
| 論文を検索する | 不要 |
| 論文PDFを読む | 不要（OA・大学契約等で閲覧可能） |
| IEEE学術誌へ投稿する | 不要 |
| ICRA・IROS等に論文投稿する | 原則不要 |
| 国際会議で発表する | 不要（参加登録・費用は必要） |
| 国際会議に聴講参加する | 不要 |
| IEEE会員向け割引を受ける | 必要 |
| IEEE RASの会員特典を利用する | RAS会員資格が必要 |

### IEEE RASとは

IEEE Robotics and Automation Society（RAS）は、IEEEに属するロボティクス・自動化分野の専門組織です。

主な対象は以下です。

- Robotics
- Robot Learning
- Robot Manipulation
- Autonomous Systems
- Robot Perception
- Human-Robot Interaction
- Automation

IEEE本体の会員資格とIEEE RASの会員資格は区別されます。

---

## 2. Robotics Journals：ロボティクス学術誌一覧

講義資料で紹介された10誌を整理します。

| No. | 学術誌 | 略称 | 出版元 | 主な研究領域 | 研究との相性 |
|---|---|---|---|---|---|
| 1 | IEEE Transactions on Robotics | T-RO | IEEE | ロボット理論、操作、知覚、制御 | ◎ |
| 2 | IEEE Robotics and Automation Letters | RA-L | IEEE | ロボット研究全般、実験・手法 | ◎ |
| 3 | IEEE Robotics & Automation Magazine | RAM | IEEE | 技術解説、実システム、応用 | ○ |
| 4 | Science Robotics | - | AAAS | 革新的なロボット科学・技術 | ◎ |
| 5 | International Journal of Robotics Research | IJRR | SAGE | Robot Learning、知覚、操作、世界モデル | ◎ |
| 6 | International Journal of Social Robotics | IJSR | Springer | 人間・ロボット相互作用、介護、社会実装 | ○ |
| 7 | Robotics and Computer-Integrated Manufacturing | RCIM | Elsevier | 産業ロボット、製造、協働自動化 | △ |
| 8 | Journal of Field Robotics | JFR | Wiley | SLAM、現場環境認識、移動ロボット | ○ |
| 9 | Robotics and Autonomous Systems | RAS | Elsevier | 自律行動、認識、学習、制御 | ◎ |
| 10 | Autonomous Robots | AURO | Springer | 自律ロボット、知能、計画、操作 | ◎ |

**研究との相性**

- ◎：現在の研究テーマと特に関連が深い
- ○：研究内容次第で適している
- △：現在の研究テーマからはやや離れる

### 現在の研究で優先して調査する学術誌

研究テーマ：

**Vision-Tactile JEPA World Models for Failure-Aware Long-Horizon Robotic Manipulation**

特に優先すべき学術誌は以下の4誌です。

1. **IEEE Robotics and Automation Letters（RA-L）**
   - 視覚・触覚を統合したロボット操作
   - VLAによる行動生成
   - 実機実験による性能評価
   - 比較的コンパクトな研究成果

2. **IEEE Transactions on Robotics（T-RO）**
   - ロボット学習の新しい方法論
   - 潜在世界モデル
   - 長期マニピュレーション
   - 理論と実験を含む成熟した研究

3. **International Journal of Robotics Research（IJRR）**
   - Robot Learning
   - World Models
   - Vision-Tactile Representation
   - Failure Prediction / Recovery

4. **Robotics and Autonomous Systems**
   - 自律ロボット
   - 状態予測
   - 失敗検知と再計画
   - 実ロボットへの適用

---

## 3. Robotics Conferences：国際会議一覧

講義資料で紹介された5つの国際会議を整理します。

| No. | 国際会議 | 正式名称 | IEEE関連 | 主な対象 | 研究との相性 |
|---|---|---|---|---|---|
| 1 | ICRA | IEEE International Conference on Robotics and Automation | あり | ロボット全般、VLA、操作、学習、制御 | ◎ |
| 2 | IROS | IEEE/RSJ International Conference on Intelligent Robots and Systems | あり | 知能ロボット、SLAM、AI、実機システム | ◎ |
| 3 | CASE | IEEE International Conference on Automation Science and Engineering | あり | 自動化、産業ロボット、最適化 | ○ |
| 4 | RSS | Robotics: Science and Systems | なし（独立） | Robot Learning、世界モデル、ロボット基礎研究 | ◎ |
| 5 | RO-MAN | IEEE International Symposium on Robot and Human Interactive Communication | あり | HRI、対話、介護・支援ロボット | ○ |

### ICRA

ロボティクス分野を代表する国際会議の一つです。

主な対象分野：

- Robot Manipulation
- Robot Learning
- Vision-Language-Action
- Reinforcement Learning
- Robot Perception
- World Models
- Sim-to-Real

**研究への適用**

SO-101を使用したVision-Tactile JEPA、VLA、長期操作の失敗検知・復帰実験に適しています。

### IROS

知能ロボットや実環境でのロボットシステムを幅広く対象としています。

主な対象分野：

- Intelligent Robotics
- Autonomous Navigation
- SLAM
- Semantic Mapping
- Robot Learning
- Robot Manipulation
- Multi-Robot Systems

**研究への適用**

SO-101での操作研究だけでなく、TurtleBot3、Livox MID-360を使った空間AI、Semantic Mapping、Scene Graphの研究にも適しています。

### CASE

自動化技術やロボットシステムの工学的応用を対象とします。

主な対象分野：

- Industrial Robotics
- Automation
- Scheduling
- Optimization
- Manufacturing Systems
- Multi-Robot Coordination

**研究への適用**

将来的なロボットフリート管理、協調学習、Agentic Robotics、工場自動化に関連します。

### RSS

ロボットの基礎理論や新規性の高いアルゴリズム研究に適した国際会議です。

主な対象分野：

- Robot Learning
- World Models
- Reinforcement Learning
- Robot Manipulation
- Planning
- Perception
- Embodied AI

**研究への適用**

Vision-Tactile JEPAによる新しい潜在状態表現や、失敗予測・復帰アルゴリズムを提案する場合に有力です。

### RO-MAN

人間とロボットの相互作用を中心とする国際会議です。

主な対象分野：

- Human-Robot Interaction
- Social Robotics
- Assistive Robotics
- Human-Robot Collaboration
- Trust and Explainability

**研究への適用**

将来的に介護ロボット、生活支援ロボット、人間との協調を伴うAgentic Roboticsを研究する場合に候補となります。

---

## 4. IEEEに入会するメリット

IEEE会員になる主なメリットは以下です。

- IEEE主催国際会議の参加費割引
- IEEE RASを通じた専門コミュニティへの参加
- 会員向けの技術情報・教育コンテンツ
- 学術・産業分野の研究者とのネットワーキング
- 一部の学術情報サービスへのアクセス特典

### ICRA 2026の参加費例

早期参加登録料金の例です。

| 登録区分 | 参加費 |
|---|---:|
| 学生・IEEE RAS会員 | €415 |
| 学生・IEEE会員 | €460 |
| 学生・非会員 | €555 |
| 一般・IEEE RAS会員 | €825 |
| 一般・非会員 | €1,100 |

学生・IEEE RAS会員と学生・非会員との差額は€140でした。

ただし、学生会員資格の適用にはIEEEが定める履修要件などを満たす必要があります。

**結論：国際会議に参加する予定が決まった段階で、会費と参加費割引を比較して加入を判断するのが合理的です。**

---

## 5. 修士論文の投稿戦略

### 研究テーマ

**Vision-Tactile JEPA World Models for Failure-Aware Long-Horizon Robotic Manipulation**

日本語：

失敗認識型の長期ロボットマニピュレーションに向けた視覚・触覚統合JEPA世界モデル

### 研究課題

| RQ | 研究課題 | 検証内容 |
|---|---|---|
| RQ1 | Vision-Tactile Representation | 視覚・触覚情報によって接触・滑り・把持状態を正確に表現できるか |
| RQ2 | Predictive World Model | JEPA型世界モデルによって将来の状態や操作失敗を予測できるか |
| RQ3 | Failure-Aware Manipulation | 失敗予測を再計画・回復に利用することで長期タスクの成功率を向上できるか |

### 実験環境

- SO-101ロボットアーム
- RealSense D435i
- XELA uSPa11触覚センサー（導入予定）
- LeRobot
- SmolVLA
- VLA-JEPA
- Vision-Tactile JEPA World Model

### 投稿戦略

#### Step 1：SO-101実機実験

視覚・触覚・関節状態のデータを収集し、以下を検証します。

- 接触状態の推定精度
- 滑り・把持失敗の予測精度
- 世界モデルの予測性能
- 長期操作の成功率
- 失敗からの回復性能

#### Step 2：RA-L / ICRA / IROSを候補に研究成果を投稿

最初の研究成果として、以下をまとめます。

- Vision-Tactile JEPAアーキテクチャ
- 視覚のみと視覚・触覚統合モデルの比較
- 失敗予測の定量評価
- SO-101による実機評価

投稿先は研究成果の完成度、新規性、実験結果、および投稿時期によって選択します。

なお、RA-L採択論文を条件付きでICRA・IROSなどで発表できる制度もあります。既発表内容の扱いや各年度の規定を確認する必要があります。

#### Step 3：T-RO / IJRRへの発展

追加の研究成果として以下を検討します。

- 異なる操作タスクへの汎化
- 長期タスクへの適用
- World Modelを使用した再計画
- Failure Recovery Policyの学習
- 異なる環境・物体での頑健性評価

単なる論文の延長ではなく、新しい技術的貢献と十分な追加検証が必要です。

---

## 6. 今後の研究における優先順位

| 優先度 | 投稿先 | 理由 |
|---|---|---|
| 1 | RA-L | 実機ベースのRobot Learning研究と相性がよい |
| 2 | ICRA | VLA、マニピュレーション、学習の研究成果を発表できる |
| 3 | IROS | 実機研究に加え、空間AI・SLAM研究にも適する |
| 4 | RSS | 世界モデルやロボット学習の新規手法を提案する場合 |
| 5 | T-RO / IJRR | 発展的で十分に成熟した研究成果向け |

### 研究活動の推奨フロー

```text
研究課題の設定
    │
    ▼
関連論文のサーベイ
    │
    ├── RA-L
    ├── T-RO
    ├── IJRR
    ├── ICRA
    ├── IROS
    └── RSS
    │
    ▼
仮説・理論の構築
    │
    ▼
SO-101実機実験
    │
    ▼
定量評価・比較実験
    │
    ▼
論文執筆
    │
    ▼
RA-L / ICRA / IROS
    │
    ▼
研究の発展・追加検証
    │
    ▼
T-RO / IJRR
```

## 7. まとめ

現時点ではIEEEに急いで加入する必要はありません。

まずはJAISTの電子図書館を活用し、RA-L、ICRA、IROS、RSS、T-RO、IJRRなどの主要論文を調査することが重要です。

特に次の3つを研究活動の中心にします。

1. **先行研究調査**：Vision-Tactile Learning、JEPA、World Models、Failure-Aware Manipulation
2. **実機実験**：SO-101によるデータ収集、失敗予測、復帰性能の評価
3. **論文投稿**：まずRA-L・ICRA・IROSを視野に入れ、成果の成熟度に応じてT-RO・IJRRなどを検討

IEEE RASへの加入は、国際会議への参加や研究コミュニティとの交流が具体化した時点で判断します。

---

## 参考リンク

- [IEEE Robotics and Automation Society](https://www.ieee-ras.org/)
- [IEEE Xplore Digital Library](https://ieeexplore.ieee.org/)
- [IEEE Transactions on Robotics](https://www.ieee-ras.org/publications/t-ro)
- [IEEE Robotics and Automation Letters](https://www.ieee-ras.org/publications/ra-l)
- [Robotics: Science and Systems](https://roboticsconference.org/)
- [The International Journal of Robotics Research](https://journals.sagepub.com/home/ijr)
- [Science Robotics](https://www.science.org/journal/scirobotics)