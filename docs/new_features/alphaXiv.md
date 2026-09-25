# alphaXivから自分の専門のタグや関心から論文の一覧を取得する。

## 概要

自分の専門分野・関心タグをもとに alphaXiv MCP から新着論文を定期的に取得し、
**日本語化した一覧（関心フィード）** として Papers 画面に表示する。
一覧から選んだ論文だけを AI レポート経由で日本語要約し、ライブラリ（alphaXiv / Paperpile）へ登録する。

- alphaXiv は MCP で論文を取得して日本語にする
- MCP のドキュメント：https://www.alphaxiv.org/docs/mcp
- 設計書の該当箇所：`docs/design.md` §3.2 alphaXiv 関心フィード

## 検証結果（2026-09-25）

実際に MCP を呼び出して確認した結果。

| 検証 | 結果 |
|---|---|
| `discover_papers`（keywords: `VLA` / `Vision-Language-Action` / `reinforcement learning`, `prioritize=recency`） | 11件取得。ID・タイトル・公開日・所属機関・votes・views・Abstract 冒頭が返る。最新は 2026-09-23 公開 |
| `get_paper_content`（2609.18207） | 構造化された英語の AI レポート（著者・位置づけ・目的・手法・結果・意義と限界、約2,000語） |
| `list_library` | 取得可。デフォルト 4 フォルダ（Want to read / Reading / Completed / My publications）のみで中身は空 |
| 公式ドキュメント | 全19ツール。フィード／トレンド／カテゴリ閲覧のツールは無い |

### 判明した制約

1. **タグ・カテゴリで新着を取るツールが無い**。ユーザーの関心・タグを検索に使う仕組みも無い
   → 関心プロファイルは Research OS 側で持つ。
2. **`discover_papers` は関連度で並べた上位候補を返す検索で、網羅的ではない**（1回あたり 10 件前後）。
   「今日の cs.RO を全件」はできない → 必要なら arXiv API で補完する。
3. **1メッセージあたり検索2回まで**。関心トピックが多い場合は、1回の呼び出しにまとめるか複数回に分けて呼ぶ。
4. **結果に重複が混ざる**（検証時も同一論文が2回出現）→ arXiv ID で重複を除く。
5. **キーワードはユーザーが書いた語をそのまま使う前提**。略語を勝手に展開すると精度が落ちる
   → タグには検索語そのもの（`VLA` など）を登録する。
6. **認証**：対話利用は OAuth で可。無人の定期実行には API キー（`Authorization: Bearer <key>`）が必要。

## 仕様

### 1. 関心プロファイル（`interests.yaml`）

Research OS 側で管理する設定ファイル。タグごとに検索キーワードを持つ。

```yaml
topics:
  - tag: VLA-RL
    keywords: [VLA, Vision-Language-Action, reinforcement learning]
    prioritize: recency        # recency / default / popular / historical
  - tag: World Model
    keywords: [world model, robot manipulation]
    prioritize: recency
researchers:                   # alphaXiv の SLUG か氏名
  - Chelsea Finn
  - Sergey Levine
arxiv_categories: [cs.RO]      # 任意：網羅性の補完用
schedule: daily                # daily / weekly / manual
```

- `keywords` には検索語をそのまま書く（略語を展開しない）。
- タグは一覧の表示・フィルタ・Knowledge Graph のノード付与にも使う。

### 2. 取得パイプライン

```
interests.yaml
   ├─ ① トピック検索：tag ごとに discover_papers（prioritize=recency）
   ├─ ② 研究者経由  ：get_researcher_papers（researchers の新着）
   └─ ③ 補完（任意）：arXiv API で arxiv_categories の新着
        ▼
   arXiv ID で重複除去（複数タグにヒットした論文はタグを統合）
        ▼
   既読キャッシュと突き合わせて新着のみ抽出
        ▼
   一覧の日本語化（タイトル＋Abstract 冒頭）
        ▼  ユーザーが選択
   詳細の日本語化：get_paper_content → 日本語要約
        ▼
   save_papers_to_folder / Paperpile 登録 / Knowledge Graph 更新
```

### 3. 日本語化は 2 段階

| 段階 | 入力 | 出力 | タイミング |
|---|---|---|---|
| 一覧 | タイトル、Abstract 冒頭、所属、公開日 | 日本語タイトル＋1〜2行の日本語概要 | 取得時に全件 |
| 詳細 | `get_paper_content` の AI レポート（不足時は `fullText`） | 日本語要約（目的／手法／結果／限界／自分の研究との関連） | 選択した論文のみ |

- レポートは約2,000語あるため、全件に対して取得しない（コストを抑える）。
- 英語の原タイトルと arXiv ID は常に併記する（検索や引用に使うため）。
- 専門用語（VLA、GRPO、flow matching など）は訳さずに原語のまま残す。

### 4. 既読管理・キャッシュ

- arXiv ID をキーにローカルへ保存する：`first_seen` / `tags` / `status`（new / seen / saved / dismissed）/ 日本語一覧文 / 日本語要約。
- 次回取得時は `status != new` の論文を一覧から除き、新着だけ出す。
- 日本語要約はキャッシュし、同じ論文で再生成しない。

### 5. 一覧の表示（Papers 画面）

```
Feed: VLA-RL ・ World Model        2026-09-25  新着 7件

● [VLA-RL] リアルタイム VLA 方策のための強化学習
  Reinforcement Learning for Real-Time Vision-Language-Action Policies
  2609.18207 | 2026-09-16 | Stanford | ▲207
  大規模 VLA の推論遅延を、軽量な編集方策と chunk 単位の critic で補正し RL 微調整する。

● [VLA-RL] BEE：VLA による介入適応型の実世界強化学習
  ...
```

- 並び順：公開日の新しい順（既定）／votes 順／タグ別。
- 操作：`> 詳しく` で詳細要約、`> 保存` でライブラリ登録、`> 不要` で dismissed。

### 6. 実行方式

- **手動**：Agent 欄で `> 今日の新着論文` などと指示すると、その場で取得する。
- **定期**：Intel と同じバックグラウンド巡回ジョブ基盤に載せる（方式は Intel と共通の ADR で決定。`design.md` §6.8）。
- 定期実行では API キー認証を使う。

## 未決事項

- `interests.yaml` の置き場所（リポジトリ内／ユーザー設定ディレクトリ）
- 既読キャッシュのストア（SQLite / Neo4j / JSON）
- arXiv API による補完を初期スコープに含めるか
- 関心プロファイルを alphaXiv ライブラリや Paperpile の保存履歴から自動で推薦するか
