# ADR-0001: Paper タブの追加と Venue レジストリの共有データ化

## Status
Accepted

## Context
`docs/reference/paper_strategy.md` で、修士研究の投稿戦略（RA-L / ICRA / IROS → T-RO / IJRR）と、
ロボティクス分野の学術誌・国際会議の整理が追加された。
Research OS は「検索 → 読解 → 比較 → 仮説化 → 実験」までを扱っているが、
**どの投稿先に、いつ、何を揃えて投稿するか** を扱う仕組みがない。

検討した選択肢：

1. **Publish タブを新設する** — 投稿戦略専用の画面を作る。
   ただし closed-loop 構想（`docs/new_features/new_feature_20260917.md`）にはすでに論文化を担う Paper 画面があり、
   「論文を書く場所」と「投稿先を決める場所」が分かれる。投稿準備チェックと Research Gate R6（Paper Gate）の判定も二重化する。
2. **closed-loop の Paper 画面に投稿戦略を含める** — 研究フェーズとして Run の後ろに 1 タブだけ伸ばす。
3. **画面を追加せず Agent 指示だけで扱う** — 投稿状態や要件の充足度を一覧できず、追跡性が弱い。

また、投稿先（Venue）の情報は Paper 画面だけでなく、Papers の掲載先フィルタ、Graph の掲載関係、
Intel 巡回基盤による締切監視からも参照される。

## Decision
- フェーズタブに **Paper** を追加し、ナビゲーションを `Papers │ Review │ Graph │ Hypothesis │ Run │ Paper │ Intel` とする。
  Paper は closed-loop 構想の Paper 画面（Claim / Evidence に基づく論文更新）を基礎とし、投稿戦略（投稿ステージ・投稿準備チェック・投稿先比較・ジャーナル版の差分チェック）を含める。Publish タブは作らない。
- 投稿準備チェックは Research Gate R6（Paper Gate）に統合し、別のゲートは設けない。
- **Venue レジストリ** を画面に属さない共有データ（`registry/venues.yaml`）とし、Intel の監視対象レジストリと同じ位置付けにする。
- Knowledge Graph に `Venue` ノードと、`Paper published_in Venue` ／ `Paper Draft targets Venue` ／ `Venue co_presents_with Venue` エッジを追加する。
- closed-loop 構想の Evaluation 画面は本 ADR の対象外とし、Proposed のまま残す。

詳細仕様は `docs/new_features/venue_strategy.md`。

## Consequences
- **メリット**
  - 研究フローが `… → Run → Paper` と一直線になり、`paper_strategy.md` §6 の推奨フローと対応する。
  - 投稿可否の判定が R6 に一本化され、Claim / Evidence との追跡性を保てる。
  - Venue を Papers・Graph・Intel 巡回で共有でき、掲載先での絞り込みや締切監視を同じデータで扱える。
- **デメリット・トレードオフ**
  - Paper 画面の責務が大きくなる（論文更新＋投稿管理）。肥大化した場合は画面内サブタブ（Draft / Submission）に分ける。
  - タブ番号が変わる（Intel が `6` → `7`）。
  - 掲載先メタデータは arXiv / alphaXiv だけでは不足し、Semantic Scholar / OpenAlex 連携の優先度が上がる。
- **フォローアップ**
  - `DESIGN.md` に Paper タブのフェーズ色・タブバー・キーバインド（`1`–`7`）・画面レイアウトを追加する。
  - 締切監視は Intel の巡回実行基盤の ADR（未起票）に依存する。
  - closed-loop 構想の Evaluation 画面を採用するかは別 ADR で決定する。
