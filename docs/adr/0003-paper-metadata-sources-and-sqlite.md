# ADR-0003: 論文メタデータの取得元（OpenAlex を主）と保存先（SQLite）

## Status
Accepted

## Context
`registry/venues.yaml` の投稿先に掲載された論文を拾い、RQ に照らして優先度を付けて取り込みたい
（`docs/new_features/paper_intake.md`）。

- arXiv / alphaXiv は掲載先（venue）の情報をほとんど持たないため、掲載先で絞り込める取得元が別に必要。
- 候補は数千件規模になり得る。判断の状態（候補・Inbox・読む・捨てた理由）を、上限の計算のために集計しながら更新する。
- alphaXiv 関心フィードの既読キャッシュの保存先も未決だった（`docs/new_features/alphaXiv.md` 未決事項）。

検討した取得元：

| 取得元 | 掲載先での絞り込み | 要旨 | 引用関係 | 利用条件 |
|---|---|---|---|---|
| OpenAlex | ○（source ID / ISSN） | ○ | ○ | 無料・キー不要（`mailto` 推奨） |
| Semantic Scholar | △（venue 名の文字列） | ○（TLDR あり） | ○ | キーなしは速度制限が厳しい |
| DBLP | ○（会議録のキー） | × | × | 無料 |
| IEEE Xplore API | ○（IEEE のみ） | ○ | △ | キーが必要 |

検討した保存先：YAML ファイル / SQLite / Neo4j。

## Decision
- 論文メタデータの **主な取得元は OpenAlex** とする。Semantic Scholar（TLDR・被引用の推移）と DBLP（会議録の収録確認）は補助とし、PR 2 では OpenAlex のみ実装する。
- 論文・取得の来歴・判断の状態・RQ とのひも付けは **SQLite**（`research/papers.db`、git 管理外）に保存する。
  alphaXiv 関心フィードの既読キャッシュも同じ DB に置く。
- 人が編集する設定（`registry/venues.yaml`・`research/profile.yaml`・`interests.yaml`）は YAML のまま残す。
- Knowledge Graph（Neo4j）への反映は、ライブラリ（`to_read` / `read` / `core`）に入った論文に限る。候補プールは Graph に入れない。

## Consequences
- **メリット**
  - 掲載先・年・キーワードでの絞り込みと引用関係の取得を、キー不要の 1 つの API でまかなえる。
  - 上限の計算（今週出した数、RQ ごとの数、未処理数）を SQL で素直に書ける。
  - 候補プールを Graph から分けることで、Graph が「読むべき論文」の構造だけを表す。
- **デメリット・トレードオフ**
  - OpenAlex の掲載先名や会議録の収録は揺れることがあり、Venue ごとに source ID を確認して `venues.yaml` に記録する手間がある。
  - `papers.db` は git 管理外のため、マシン間での共有やバックアップは別途必要。
- **フォローアップ**
  - `registry/venues.yaml` に `identifiers`（ISSN / OpenAlex source ID / DBLP キー）を追加する（PR 2）。
  - `papers.db` のバックアップ・エクスポート（YAML / BibTeX）の方法を決める。
