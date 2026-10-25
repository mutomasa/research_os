# Research OS — Paper Intake（投稿先からの論文取り込みと Inbox）

## Status

Proposed（取得元と保存先は [ADR-0003](../adr/0003-paper-metadata-sources-and-sqlite.md) で決定）

## 1. 概要

alphaXiv の関心フィード（design.md §3.2）に加えて、`registry/venues.yaml` の投稿先（RA-L / ICRA / IROS / RSS / T-RO / IJRR など）に
**掲載された論文** を拾い、研究プロファイルの RQ に照らして優先度を付けて取り込む。

ただし目的は「たくさん集めること」ではなく **読むべき論文を少しだけ前に出すこと** である。
そのため本機能の中心は、スコア付けよりも **表に出す量の上限（§5）** にある。

```
OpenAlex / Semantic Scholar / DBLP（掲載先 × RQ キーワード × 年）─┐
alphaXiv 関心フィード / 引用関係からの探索 ──────────────────┤
                                                              ▼
       重複除去（DOI / arXiv ID / 題名の正規化。プレプリントと出版版を 1 本にまとめる）
                                                              ▼
       候補プール（非表示）── スコア付け（§4）
                                                              ▼
       Inbox（上限つき。§5）── 人が判断：読む / 捨てる（理由つき）
                                                              ▼
       論文ライブラリ（RQ にひも付け）→ RQ カバレッジ → 手薄さの加点へ戻る
```

## 2. 取得元

| 取得元 | 使うもの | 役割 |
|---|---|---|
| **OpenAlex**（無料・キー不要） | 掲載先 ID・年・キーワードでの絞り込み、要旨（inverted index）、被引用数、引用関係（`referenced_works` / `cites:`） | 主力 |
| Semantic Scholar | TLDR、被引用の推移、プレプリントと出版版のひも付け | 補助（スコアの材料） |
| DBLP | ICRA / IROS / RSS の会議録の収録確認（要旨なし） | 取りこぼしの確認 |
| alphaXiv | 関心フィード（既存。design.md §3.2） | 新着プレプリント |

- `registry/venues.yaml` の各 Venue に、取得元ごとの識別子を持たせる。

  ```yaml
  identifiers:
    issn: [2377-3766]
    openalex: null     # OpenAlex の source ID（例: S...）。ISSN から解決し、確認したら記入
    dblp: null         # 例: journals/ral, conf/icra
  ```

- 検索の範囲は **RQ ごとの `survey_topics` × `survey_venues` × 年の範囲** に限る（全体検索はしない）。
  年の範囲の既定は直近 4 年（`intake.year_from` で変更可）。
- 利用条件を守る：OpenAlex は `mailto` を付けた polite pool で呼ぶ、Semantic Scholar はキーなしの速度制限に合わせる、取得結果はキャッシュして再取得しない。

## 3. データモデル

候補は数千件規模になり得るため、論文と判断の状態は SQLite（`research/papers.db`、git 管理外）に置く（ADR-0003）。

### 3.1 論文（papers）

| 列 | 内容 |
|---|---|
| `paper_id` | 内部 ID。`doi:` → `arxiv:` → `openalex:` の順で最初に得られたものを使う |
| `doi` / `arxiv_id` / `openalex_id` | 外部 ID（重複除去のキー） |
| `title` / `title_norm` | 題名と正規化した題名（小文字化・記号除去・空白の正規化） |
| `abstract` / `year` / `authors` | 要旨・出版年・著者 |
| `venue_id` | `registry/venues.yaml` の venue_id（該当なしは null） |
| `venue_name` | 取得元が返した掲載先名（そのまま保存） |
| `cited_by_count` / `citations_per_year` | 被引用数と、出版からの年数で割った値 |
| `first_seen` / `updated_at` | 来歴 |

### 3.2 取得の来歴（paper_sources）

`paper_id` / `source`（`openalex` / `s2` / `dblp` / `alphaxiv` / `citation`）/ `source_ref` / `query` / `retrieved_at`。
同じ論文が複数経路で見つかった場合は 1 行の論文に対して来歴を複数持つ。

### 3.3 判断の状態（triage）

```
candidate（非表示）→ inbox → to_read → read → core
                       └──→ dismissed（理由つき）
```

| 状態 | 意味 |
|---|---|
| `candidate` | 候補プール。表には出さない |
| `inbox` | 今週表に出した論文。人の判断待ち |
| `to_read` | 読むと決めた論文（上限あり） |
| `read` | 読了。ライブラリに入る |
| `core` | 中核論文。RQ の飽和判定と引用探索の起点になる |
| `dismissed` | 捨てた論文。理由（`irrelevant` / `known` / `outdated` / `low_quality` / `other`）を必須にする |

- 状態遷移ごとに日時を記録する（`surfaced_at` / `decided_at`）。
- `to_read` / `read` / `core` を **ライブラリ** と呼び、RQ カバレッジの「関連論文」はライブラリを数える。

### 3.4 RQ とのひも付け（paper_rq）

`paper_id` / `rq_id` / `relevance`（0〜1）。最も関連度の高い RQ を **主 RQ** として、RQ ごとの上限の計算に使う。

## 4. スコア

各論文に 0〜1 のスコアを付け、**内訳を必ず保存して表示する**（なぜこの論文が出てきたかを説明できるようにする）。

```
score = 0.50 × relevance + 0.20 × venue + 0.15 × gap + 0.15 × velocity − penalty
```

| 要素 | 計算 | 備考 |
|---|---|---|
| `relevance` | 主 RQ との関連度 | 段階 1：RQ の `survey_topics` と題名・要旨の語の一致（安価）。段階 2：段階 1 の上位だけを LLM で判定 |
| `venue` | profile の priority p（1〜5）から `(6 − p) / 5`。priority なしの登録 Venue は 0.1、未登録は 0 | RA-L = 1.0 … T-RO / IJRR = 0.2 |
| `gap` | `max(0, 1 − 主 RQ の core 数 / core_target)` | 手薄な RQ ほど加点 |
| `velocity` | `min(1, log(1 + citations_per_year) / log(1 + 50))` | 総数ではなく年あたりで見る |
| `penalty` | ライブラリ内の論文と題名がほぼ同じ（正規化題名が一致、または類似度 0.9 以上）なら候補から外す | 重複は減点ではなく統合する |

- 重みは `intake.weights` で変更できる。
- LLM 判定（段階 2）は 1 回の取り込みで上位 `intake.llm_top_k`（既定 30）件までに限る。

**表示イメージ**

```
0.82  Tactile World Models for Slip Prediction        RA-L 2025
      RQ2 関連 0.91 · RA-L(1) · RQ2 手薄 +0.10 · 被引用 18/年
```

## 5. 埋もれないための上限

| 設定 | 既定値（仮） | 挙動 |
|---|---|---|
| `inbox_weekly_total` | 10 | 1 週間（ISO 週）に Inbox に出す論文の総数。**alphaXiv 関心フィードと共有** し、取り込み経路が増えても表示量は増えない |
| `inbox_per_rq` | 4 | 主 RQ ごとの週あたりの上限 |
| `inbox_backlog_max` | 10 | 未処理の Inbox がこの数以上残っていたら、新しい論文を出さない |
| `to_read_max` | 5 | `to_read` の上限。満杯なら「読む」を選べない（読み終えるか捨てるまで） |
| `core_target` | 15 | RQ ごとの中核論文の目標数。達した RQ は `inbox_per_rq` を 1 に絞る |
| `min_score` | 0.30 | これ未満は出さない（枠を埋めるために質の低い論文を出さない） |
| `schedule` | weekly | 投稿先経由の取り込みは週 1 回まとめて行う。毎日流れるのは関心フィードの新着だけ |

**Inbox に出す手順**

1. 未処理の Inbox が `inbox_backlog_max` 以上なら何もしない。
2. 今週の残り枠 = `inbox_weekly_total` − 今週すでに出した数。
3. 候補をスコア順に見て、`min_score` 以上で、主 RQ の今週の残り枠（飽和 RQ は 1）がある論文を、残り枠が尽きるまで `inbox` にする。

設定は `research/profile.yaml` の `intake` に置く（研究テーマごとに変えられるように）。

## 6. 引用関係からの探索（PR 3）

広くキーワード検索するより、採用した中核論文の周辺に集中する。

- `core` の論文について、OpenAlex の参照文献（`referenced_works`）と被引用（`cites:`）を取得し、`source: citation` として候補プールに入れる。
- スコアに `link` 要素（その論文とつながる core 論文の数を正規化した値）を加える。
- 1 回の探索で取得する件数に上限を設ける（core 1 本あたり参照・被引用それぞれ上位 20 件）。

## 7. 捨てた理由の反映（PR 3）

| 理由 | 反映 |
|---|---|
| `irrelevant` | 捨てた論文の題名に多く出る語を、その RQ の除外語の候補として提示する（自動では追加せず、人が承認する） |
| `known` | 既知の論文としてライブラリに `read` で入れる（以後の重複除去に使う） |
| `outdated` | 同じ RQ で続くなら `year_from` の引き上げを提案する |
| `low_quality` | 同じ掲載先で続くなら、その Venue の `venue` 重みを下げる提案をする |

反映は **提案まで** とし、設定の変更は人が承認する。

## 8. 段階的な実装

| PR | 内容 |
|---|---|
| 1 | 本仕様、design.md §2.1 の Inbox、todo.md、ADR-0003 |
| 2 | 論文ライブラリと Inbox のデータ層（SQLite）、Venue の識別子、OpenAlex からの取得、スコア（段階 1）、上限の制御、CLI |
| 3 | 引用関係からの探索、捨てた理由の反映、LLM 判定（段階 2） |

## 9. 未決事項

- 段階 1 の関連度を語の一致のままにするか、埋め込みに置き換えるか
- Semantic Scholar・DBLP をどの段階で取り込むか（PR 2 では OpenAlex のみ）
- Paperpile のライブラリとの同期（既に持っている論文を `read` として取り込むか）
