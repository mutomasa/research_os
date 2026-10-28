# Research OS

Research OS は、文献検索から実験実行までの研究活動を、ひとつの TUI でつなぐ研究開発 IDE の構想です。

文献データベース、Research Agent、MCP 経由の外部サービスを統合し、研究者が次のサイクルを一貫して進められる環境を目指します。

```text
検索 → 読解 → 比較 → 仮説化 → 実験
```

> Paperpile を文献 DB、Claude Code を Research Agent、MCP を外部世界との I/O、TUI を研究者の Cockpit にする。

## 主な画面

| 画面 | 役割 |
|---|---|
| Papers | Paperpile、arXiv、Semantic Scholar などから文献を検索する |
| Review | 選択した論文を読み、比較・新規性・限界・不足実験を分析する |
| Graph | 論文、手法、データセット、課題などの関係を Knowledge Graph で捉える |
| Hypothesis | Research Gap から Research Question、Hypothesis、Experiment を組み立てて永続化する |
| Run | 実験条件を定義し、実装・学習・評価を実行する |

## Agent 中心の操作

Research OS では、個別の検索画面やツールを人が順番に操作する代わりに、研究上のゴールを自然言語で Agent に伝えます。

```text
Human → Goal → Agent → Plan → Tool / MCP / Skill → Result
```

たとえば `Find recent tactile world model papers` と指示すると、Agent が検索、重複確認、メタデータ取得、要旨評価、PDF 解析、論文比較、文献登録、Knowledge Graph 更新までを連携して進めます。

## アーキテクチャ

```text
Research OS TUI
      │
 User Intent
      │
Research Agent
      │
      ├── Skills ── Search / Review / Gap / Experiment
      ├── MCP ───── Paperpile / arXiv / GitHub / Neo4j
      └── Subagents
              │
         Claude Code
              │
              ├── Code
              ├── Experiment
              └── Docs
```

画面下部のステータスバーでは、Paperpile、arXiv、GitHub、MCP など外部サービスとの接続状態を確認できます。

## 使い方

### 必要なもの

- Python 3.12 以上と [uv](https://docs.astral.sh/uv/)
- （任意）[Claude Code](https://claude.com/claude-code) の `claude` コマンド。論文の関連度を LLM で判定するときに使う。無ければ `--no-llm` を付ける

### セットアップ

```bash
git clone https://github.com/mutomasa/research_os.git
cd research_os
uv sync
uv run research-os --version
```

以降のコマンドはすべてリポジトリの直下で `uv run research-os …` として実行します（`.venv` を activate しておけば `research-os …` だけでも動きます）。

### 1. 研究テーマを書く

設定は 2 つの YAML です。

| ファイル | 内容 |
|---|---|
| `research/profile.yaml` | 研究テーマ、RQ（Research Question）、Venue の上書き、取り込みの上限（`intake:`） |
| `registry/venues.yaml` | 投稿先・論文の取得元となる学術誌・国際会議の一覧 |

まず `research/profile.yaml` の `theme` と `research_questions` を自分の研究に書き換えます。書けたら、適用後の Venue 一覧で確認します。

```bash
uv run research-os venues            # 優先度順に Venue を表示
uv run research-os interests init    # profile.yaml から research/interests.yaml を生成（任意）
```

### 2. 論文を取り込む

```bash
uv run research-os intake run        # Venue から OpenAlex で取得し、スコアを付けて Inbox に出す
uv run research-os intake run --no-llm   # LLM 判定を飛ばす（claude が無いとき）
```

- 前回の取得から `refetch_days`（既定 6 日）以内の Venue は飛ばします。やり直すときは `--force` を付けます。
- Inbox に出す数には上限があります（既定で週 10 本・未処理 10 本・「読む」5 本）。読み切れる量だけを出すための制限で、`research/profile.yaml` の `intake:` で変えられます。
- 取り込んだ論文は `research/papers.db`（SQLite）に入ります。このファイルは git に含めません。
- OpenAlex の API キーや連絡先を使う場合は、環境変数 `OPENALEX_API_KEY` / `OPENALEX_MAILTO` を設定します。

中核論文（core）ができたら、その参考文献と被引用からも候補を集められます。

```bash
uv run research-os intake explore
```

### 3. TUI で Inbox を片付ける

```bash
uv run research-os tui
uv run research-os tui --mascot compact  # 右上の Neko をヘッダ 1 行にする（off で非表示）
```

起動すると Papers 画面に Inbox が出ます。論文を 1 本ずつ見て判断します。

| キー | 操作 |
|---|---|
| `j` / `k`、`g` / `G` | 一覧の移動（先頭 / 末尾） |
| `r` | 読む（To read に入れる） |
| `e` | 読了 |
| `c` | 中核にする（読了の論文のみ） |
| `d` | 捨てる。続けて理由を `1`–`5` で選ぶ（関係ない / 既知 / 古い / 質が低い / その他） |
| `[` / `]` | 一覧の切替：Inbox / To read / Read / Core |
| `1`–`7` | フェーズタブの切替（Papers 以外の画面はまだ未実装） |
| `>` / `i` | Agent 欄に入力（`esc` でメインに戻る） |
| `?` | キー一覧 |
| `q` | 終了 |

判断できる遷移は次のとおりです。できない操作や上限を超える操作は、右上の通知で理由を表示します。

```text
inbox ──→ to_read ──→ read ──→ core
  │          │          │
  └──────────┴──────────┴──→ dismissed（捨てる）
```

- 「既知」を理由に捨てた論文は、Read に入ります（以後の重複除去に使うため）。
- 端末の幅が 100 列未満のときは、プレビュー欄を隠し、Neko をヘッダ 1 行に縮めます。
- Agent 欄は入力と履歴だけが動きます。Agent コアはまだ無いので、送った指示には「未接続」と表示されます。

### CLI だけで回す

TUI を使わずに同じことができます。

```bash
uv run research-os inbox                      # Inbox を表示（--status to_read などで他の一覧）
uv run research-os triage <paper_id> to_read  # 判断：to_read / read / core / dismissed / inbox
uv run research-os triage <paper_id> dismissed --reason irrelevant
uv run research-os intake suggest             # 捨てた理由から設定変更を提案（適用は手で行う）
```

`<paper_id>` は `inbox` の各論文の 2 行目に出ます。

### 設定ファイルの場所を変える

すべてのサブコマンドの前に付けられます。

```bash
uv run research-os --profile path/to/profile.yaml --registry path/to/venues.yaml --db path/to/papers.db tui
```

### テスト

```bash
uv run pytest
```

失敗したテストのログは `logs/pytest/` に自動で書き出されます。

## ドキュメント

- [UI 設計ドキュメント](docs/design.md) — レイアウト、各画面、Agent 操作、外部接続、内部アーキテクチャの詳細
- [TUI デザイン](DESIGN.md) — 配色、画面の描き方、キー操作
- [論文の取り込み](docs/new_features/paper_intake.md) — スコア、上限、Inbox の運用
- [実装計画](docs/todo.md)

## 現在の状態

論文の取り込み（OpenAlex・LLM 判定・Inbox の上限）と、TUI の骨組み（ヘッダ・フェーズタブ・Agent 欄・Neko・Papers の Inbox）までを実装しています。Review 以降の画面と Agent コアは未実装です。進み具合は [docs/todo.md](docs/todo.md) を参照してください。
