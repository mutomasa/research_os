# Research OS — 開発証跡（Work History）

`git log` のコミットメッセージを開発証跡として転記する記録です。
小さめの単位でコミットしたら、そのつど 1 行〜数行でここに追記してください。

## フォーマット

```markdown
### YYYY-MM-DD `<short-hash>` <コミットメッセージ要約>

- 何を: ...
- なぜ: ...
```

## 履歴

### 2026-09-03 `a157706` docs: add Research OS design and overview

- 何を: `docs/design.md` を作成し、Research OS の UI 設計・アーキテクチャの初版をまとめた。
- なぜ: 実装に入る前に、研究フェーズ（検索 → 読解 → 比較 → 仮説化 → 実験）を1つのTUIで回す構想を明文化するため。

### 2026-09-04 `e5930ae` docs: integrate alphaXiv MCP into Research OS design

- 何を: `docs/design.md` に alphaXiv MCP（文献探索の主力バックエンド）の接続方法・ツール一覧を統合した。
- なぜ: 文献探索を Paperpile / arXiv だけでなく alphaXiv 経由でも行えるようにするため、設計段階で外部接続の仕様を固めておく必要があった。

### 2026-09-04 `b34cbbf` docs: add implementation TODO checklist derived from design.md

- 何を: `docs/design.md` から実装チェックリストを起こし `docs/todo.md` として追加した。
- なぜ: 設計と実装タスクを分離し、フェーズ順（Papers → Review → Graph → Hypothesis → Run）で実装を進められるようにするため。

### 2026-09-16 `4b788f0` docs: propose AI-native closed-loop research feature

- 何を: `docs/new_feature.md`（Status: Proposed）を追加。Hypothesis/Experiment/Run/Evidence/Claim の研究オブジェクトモデル、Evaluation・Paper 画面の追加、Research Gate（R0〜R6）、Human-in-the-Loop 方針、MVP 範囲を定義した。
- なぜ: 現行の `Papers → Review → Graph → Hypothesis → Run` だけでは、評価結果から仮説・実装へ戻るフィードバックループや、Evidence に基づく論文更新を扱えないため、closed-loop な研究エンジンとしての拡張案をまとめる必要があった。

### 2026-09-21 `687ef9e` docs: add Intel screen and monitoring pipeline for US physical-AI companies

- 何を: `docs/design.md` に Intel タブ（2.6）と Intel 監視パイプライン（6 章）を追加。Graph に Company / Product / Customer / Event を拡張し、レイアウト・ステータスバー（Feeds）・Skill 対応表も更新した。
- なぜ: 米国フィジカルAI企業の公式ブログ・論文・ニュースを自動巡回し、技術革新（Technology Intelligence）と事業化動向（Business Intelligence）を別々に抽出・比較して、研究テーマ探索に使うため（元メモ: `docs/memo.md`）。

### 2026-09-21 `cc22bb7` docs: add Intel implementation checklist to todo.md

- 何を: `docs/todo.md` に「8. Intel」セクション（レジストリ・収集・抽出・更新追跡・Graph 拡張・分析出力・UI・定期実行基盤・テスト）を追加し、既存セクションに連動項目を追記した。
- なぜ: design.md の Intel 設計を実装可能なチェックリストに落とし込むため。巡回の実行基盤は未決のため、決定時に ADR を起票する項目として残した。

### 2026-09-25 `25be63b` docs: add alphaXiv interest-feed spec based on MCP verification

- 何を: `docs/new_features/alphaXiv.md` に、関心タグから新着論文を取得して日本語化する「alphaXiv 関心フィード」の仕様を記述した（interests.yaml、取得パイプライン、2段階の日本語化、既読管理、UI、実行方式）。
- なぜ: alphaXiv MCP を実際に呼んで検証した結果、タグ単位のフィードツールが無く `discover_papers` も網羅的でないと分かったため、関心プロファイルを Research OS 側で持つ前提で仕様を固めた。

### 2026-09-25 `01788a6` docs: add alphaXiv interest feed (§3.2) to design.md

- 何を: `docs/design.md` の §3.1 に MCP の利用上の制約を追記し、§3.2 関心フィードを新設した。§2.1・§5・§6.8 から参照を張った。
- なぜ: 新機能の仕様を設計の正である design.md に反映するため。

### 2026-09-25 `fb51c7d` docs: add alphaXiv interest feed tasks to todo.md

- 何を: `docs/todo.md` に §3.1 関心フィードの実装タスク、API キー設定、定期実行基盤へのジョブ登録を追加した。
- なぜ: design.md §3.2 を実装チェックリストに落とし込むため。

### 2026-09-27 `95700f6` docs: add US physical-AI company monitoring memo

- 何を: `docs/memo.md` を追加。米国フィジカルAI企業の公式ブログ・ニュース監視リスト、2026年9月時点の注目ビジネスイノベーション、監視・ナレッジグラフ設計のアイデアをまとめた。
- なぜ: Intel 画面設計（design.md §2.6 / 6 章）の元メモとして参照されていたが未コミットだったため、証跡として残す。

### 2026-10-01 `bd97881` docs: add DESIGN.md TUI design system

- 何を: リポジトリ直下に `DESIGN.md` を追加。TUI デザインシステム「Lab Ink」として、配色トークン（Hex / 256 / 16 色）、フェーズ色、ドメイン色（Graph ノード・信頼性・既読状態）、枠線、コンポーネント（Agent 欄・論文リスト・ステータスバー・確認ダイアログ）、画面ごとの描画例、レイアウト、アイコンと ASCII フォールバック、キーバインド、アニメーション規約を定義した。
- なぜ: `docs/design.md` は各画面の機能を定義しているが描き方の規約が無かったため。awesome-tui-design の `TEMPLATE.md` 形式に揃え、AI エージェントが TUI 実装時にそのまま参照できるようにした。

### 2026-10-01 `217defd` docs: reference DESIGN.md from CLAUDE.md and todo.md

- 何を: `CLAUDE.md` のドキュメント表に `DESIGN.md` を追加し、`docs/todo.md` §0 にテーマ実装・表示幅ユーティリティ・キーバインド定義のタスクを追加した。
- なぜ: デザインシステムを参照先として明示し、実装タスクに落とし込むため。

### 2026-10-02 `2164916` docs: add simple system architecture diagram (draw.io)

- 何を: `docs/architecture.drawio` を追加し、`docs/design.md` §5 の構成（TUI → Research Agent → Skills / Subagents / MCP → Claude Code、バックグラウンド巡回ジョブ）を draw.io 形式で図示した。
- なぜ: ASCII 図よりシステム構成を一目で把握しやすくし、GUI で編集できる形で残すため。

### 2026-10-02 `674554c` docs: remove duplicate docs/new_feature.md

- 何を: 旧パスの `docs/new_feature.md` を削除した。
- なぜ: 同じ提案書が `docs/new_features/new_feature_20260917.md` として既に管理されており（`138afa4`）、重複していたため。新機能の提案書は `docs/new_features/` に集約する。

### 2026-10-02 `6343b89` docs: add C4 model diagram (Level 1-4) of Research OS

- 何を: `docs/c4_model.d2`（d2 ソース）と `docs/c4_model.png`（生成画像）を追加し、Research OS の構成を C4 モデルの Level 1〜4 で図示した。
- なぜ: `docs/design.md` の構成を、システム全体から Research Agent・Hypothesis Skill まで段階的に拡大して把握できるようにするため。

### 2026-10-03 `4351b7c` docs: add Signal Night alternate TUI theme to DESIGN.md

- 何を: `DESIGN.md` に §13「Alternate Theme: Signal Night」を追加。配色トークン（Hex / ANSI 256 / ANSI 16）、Agent 役割色 4 色、破線ボーダー、Routing バー・Swarm カード・Session Log・Agent Tree 画面を定義し、参考画像 `docs/UI/IMG_8806.jpg` を同梱した。
- なぜ: Agent の内部構造（Main / Subagent / Routing / Advisor）が一目で分かる、黒地に役割色を灯す管制室的な見た目を Lab Ink の代替テーマとして選べるようにするため。

### 2026-10-03 `7ff8d54` docs: rename alternate theme Signal Night to Mission Control

- 何を: `DESIGN.md` §13 の代替テーマ名を Signal Night → Mission Control に、`:theme` 引数を `mission-control` に変更した。
- なぜ: 管制室的に Agent を監視するテーマの性格が名前から直接伝わるようにするため。

### 2026-10-25 `b1ec255` docs: propose venue strategy feature based on paper_strategy reference

- 何を: 参照資料 `docs/reference/paper_strategy.md` を追加し、それを基に `docs/new_features/venue_strategy.md`（Status: Proposed）を作成。Venue レジストリ、研究プロファイル（テーマ・RQ カバレッジ）、Paper 画面での投稿パイプライン（R6 統合の投稿準備チェック・投稿先比較・ジャーナル版差分）、締切・投稿規定の巡回監視を定義した。
- なぜ: 現行設計は実験・論文化までで止まっており、どの投稿先にいつ何を揃えて出すかを追跡する仕組みがなかったため。

### 2026-10-25 `235e721` docs: add ADR-0001 for Paper tab and shared Venue registry

- 何を: ADR-0001 を追加。Publish タブを新設せず closed-loop の Paper 画面に投稿戦略を含めること、Venue レジストリを共有データとし Graph に Venue ノードを追加することを決定。
- なぜ: 論文化と投稿先決定の画面・判定（R6 Paper Gate）の二重化を避け、Venue を Papers / Graph / Intel 巡回で共有するため。

### 2026-10-25 `4f3fd27` docs: add Paper tab and Venue registry to design.md

- 何を: `docs/design.md` に 2.7 Paper を追加し、全体レイアウトのタブ・Graph の Node / Edge・ステータスバー（締切表示）・Skill 対応表・巡回基盤を更新した。
- なぜ: ADR-0001 の決定を仕様の正である design.md に反映するため。

### 2026-10-25 `b6c9865` docs: reflect Paper tab and venue strategy in todo.md

- 何を: `docs/todo.md` に 9. Paper（Phase A〜C）を追加し、Papers / Graph / Run / 外部接続 / 基盤の関連タスクを追記。仕上げを 10 に繰り下げた。
- なぜ: design.md §2.7 と venue_strategy.md の仕様を実装タスクに落とし込むため。

### 2026-10-25 `fc46138` docs: add Paper tab to DESIGN.md

- 何を: `DESIGN.md` に Paper のフェーズ色（`#f4b8e4`）、タブバー（`6 Paper │ 7 Intel`）、キーバインド `1`–`7`、Venue / Paper Draft ノード、R6 判定・投稿ステージ・締切の表示規約、6.8 Paper 画面を追加した。
- なぜ: ADR-0001 のフォローアップとして、design.md §2.7 の Paper 画面を描くための規約を揃えるため。

### 2026-10-25 `ce2a318` docs: replace hourglass emoji with ◔ in deadline display

- 何を: design.md・todo.md・venue_strategy.md の締切表示 `⏳` を `◔` に置き換えた。
- なぜ: DESIGN.md の「絵文字をアイコンに使わない」規約に合わせるため。

### 2026-10-25 `bf70cf0` feat: add initial Venue registry (registry/venues.yaml)

- 何を: `registry/venues.yaml` を作成し、学術誌 10・国際会議 5 を venue_strategy.md §3.1 のスキーマで登録した（priority：RA-L 1 / ICRA 2 / IROS 3 / RSS 4 / T-RO・IJRR 5）。
- なぜ: Phase A の起点として、Papers の Venue フィルタ・Graph の Venue ノード・Paper 画面が参照する共有データを用意するため。投稿規定・締切は未確認のため verified: false / 空のままにした。

### 2026-10-25 `b2f6fd1` feat: add research profile (research/profile.yaml)

- 何を: `research/profile.yaml` を作成し、研究テーマ、RQ1〜RQ3（検証内容・サーベイキーワード）、venue_overrides、survey_venues、submission_plan（Step 1〜3）を定義した。venue_strategy.md §4 に追加項目を追記した。
- なぜ: 研究テーマと RQ を Hypothesis チェーンの上位に置き、RQ カバレッジ集計・関心フィードの初期生成・投稿先の優先度判断の基準にするため（Phase A）。

### 2026-10-25 `96e90f8` docs: add ADR-0002 choosing Python + Textual

- 何を: ADR-0002 を追加し、実装言語を Python 3.12+、TUI を Textual、パッケージ管理を uv、検証を pydantic v2、テストを pytest に決定した。DESIGN.md の「未選定」注記と todo.md §0 を更新した。
- なぜ: 実験資産・Paper2Agent・Agent SDK と同じ言語で連携でき、DESIGN.md の描画規約も満たせるため（Go + Bubble Tea / Rust + Ratatui と比較）。

### 2026-10-25 `c4dbeb8` chore: scaffold Python package with uv (src layout, pytest)

- 何を: `pyproject.toml`・`uv.lock`・`src/research_os/`（data パッケージ、最小 CLI）・`tests/`（スモークテスト）・`.gitignore` を追加した。
- なぜ: Phase A のデータ層を実装する土台を用意するため。

### 2026-10-25 `57830e7` feat: load and validate Venue registry

- 何を: `registry/venues.yaml` の読み込み・検証（未知キー・ID 重複・参照切れ）と、テスト失敗時に `logs/pytest/` へ生ログを残す conftest フックを追加した。
- なぜ: Phase A のデータ層の土台として、共有データの書き間違いを読み込み時に検出するため。

### 2026-10-25 `454e03f` feat: load research profile and apply venue overrides

- 何を: `research/profile.yaml` の読み込み・検証と、venue_overrides を適用した優先度順の Venue 一覧（`effective_venues`）を追加した。
- なぜ: 研究テーマ固有の優先度をレジストリを変えずに反映するため。

### 2026-10-25 `72b41ed` feat: generate interests.yaml from research profile and add CLI

- 何を: 研究プロファイルから `interests.yaml` を初期生成する機能と CLI（`research-os venues` / `research-os interests init`）を追加した。
- なぜ: 関心フィードの設定を RQ と対応づけて作り、RQ カバレッジ集計の土台にするため。置き場所は暫定（#5）。

### 2026-10-25 `bd9fe14` test: keep failure log of venue override test

- 何を: override テストの失敗ログを `logs/pytest/` に残した（テスト側の誤りを修正済み）。
- なぜ: CLAUDE.md の失敗ログ保存規約に従うため。同順位の並び順の問題は #3、ログ管理方針は #6。

### 2026-10-25 `ab9cc57` docs: propose paper intake from venues with capped Inbox

- 何を: `docs/new_features/paper_intake.md` を追加。投稿先 × RQ キーワード × 年での取り込み、内訳つきスコア、上限つき Inbox、引用探索と捨てた理由の反映を定義した。
- なぜ: alphaXiv 以外に投稿先からも論文を取り込みつつ、表示量を制御して情報の海に埋もれないようにするため。

### 2026-10-25 `f56ee70` docs: add ADR-0003 for OpenAlex metadata source and SQLite store

- 何を: ADR-0003 を追加。取得元は OpenAlex を主、保存先は SQLite（`research/papers.db`）とした。
- なぜ: 掲載先で絞り込める取得元と、上限の集計に向いた保存先が必要だったため。関心フィードの既読キャッシュの保存先もあわせて決めた。

### 2026-10-25 `90fb64a` docs: add Inbox to design.md §2.1 and paper intake tasks to todo.md

- 何を: `docs/design.md` §2.1 に Inbox を追記し、`docs/todo.md` に §3.2 Paper Intake（PR 2 / PR 3 / UI）を追加した。
- なぜ: 仕様を設計書の正と実装タスクに反映するため。

### 2026-10-25 `d4b4654` feat: add venue identifiers and intake limits to profile

- 何を: `registry/venues.yaml` に identifiers を追加（OpenAlex source ID を学術誌 10・ICRA・IROS で確認、DBLP は未確認で null）し、`research/profile.yaml` に intake（上限・重み）を追加した。
- なぜ: 投稿先から論文を引くための識別子と、表示量の上限を設定として持つため。

### 2026-10-25 `ed017b8` feat: add SQLite paper store with dedupe and triage transitions

- 何を: SQLite の論文ストア（papers / paper_sources / triage / paper_rq / fetch_log）、重複除去、判断の状態遷移を追加した。
- なぜ: ADR-0003 に従い、候補プールと判断の状態を上限の集計ができる形で保存するため。

### 2026-10-25 `0e415b6` feat: add stage-1 paper scoring with breakdown

- 何を: 語の一致による関連度・投稿先・RQ の手薄さ・年あたり被引用のスコアと内訳を追加した。
- なぜ: Inbox で「なぜこの論文か」を示しつつ優先度を付けるため。関連度が粗い問題は #9。

### 2026-10-25 `70fd7b2` feat: add OpenAlex works client

- 何を: RQ ごとに投稿先をまとめて 1 リクエストで検索する OpenAlex クライアントを追加した（API キーは任意）。
- なぜ: 掲載先で絞り込める主な取得元として（ADR-0003）。無料枠の問題は #11。

### 2026-10-25 `8822615` feat: add intake pipeline with weekly and per-RQ caps

- 何を: 取得 → スコアの付け直し → 上限つきで Inbox に出す流れを追加した（週 10・主 RQ ごと 4・未処理 10 で停止・中核で飽和・min_score）。
- なぜ: 情報の海に埋もれないよう、表示量を上限で制御するため。

### 2026-10-25 `21b8e32` test: keep failure log of intake fake client

- 何を: intake テストの失敗ログ（FakeClient のキーワード対応の誤り）を残した。
- なぜ: CLAUDE.md の失敗ログ保存規約に従うため。

### 2026-10-25 `3f0594f` feat: add intake run / inbox / triage CLI

- 何を: `research-os intake run` / `inbox` / `triage` を追加し、実 API で 150 件取得 → Inbox 10 件を確認した。
- なぜ: TUI の前に、取り込みと判断を CLI で回せるようにするため。

### 2026-10-25 `dc83aba` feat: explore references and citations of core papers

- 何を: core 論文の参考文献・被引用を候補に入れる探索、スコアの link 要素、RQ の exclude_topics、捨てる理由 known をライブラリに入れる挙動を追加した。
- なぜ: 広くキーワード検索するより、採用した中核論文の周辺に集中するため（paper_intake.md §6）。

### 2026-10-25 `d8ca43c` feat: suggest profile changes from dismissal reasons

- 何を: 捨てた理由（irrelevant / outdated / low_quality）が 3 本以上たまったら、除外語・year_from・投稿先の優先度の変更を提案する機能を追加した。
- なぜ: 判断の結果を次の取り込みに生かしつつ、設定の変更は人が承認するため（§7）。

### 2026-10-25 `ef967b6` fix: do not suggest generic words as exclude topics

- 何を: 捨てた論文以外の題名に多く出るありふれた語を除外語の候補から外した。
- なぜ: 実データで「learning」が提案されたため。

### 2026-10-25 `ea4fe0f` test: keep failure log of generic-word filter

- 何を: ありふれた語の判定の初版で 2 件失敗したログを残した。
- なぜ: CLAUDE.md の失敗ログ保存規約に従うため。

### 2026-10-25 `68f5523` feat: add intake explore / suggest CLI

- 何を: `research-os intake explore` / `intake suggest` を追加し、実 API で core 1 本から 67 件の候補追加を確認した。
- なぜ: 引用探索と提案を CLI から回せるようにするため。

### 2026-10-25 `cf15c87` docs: align paper intake spec with PR 3 and record commits

- 何を: paper_intake.md §6・§7 を実装（citation_limit 50、参考文献は並べ替えない、link の式、ありふれた語の除外、3 本で提案）に合わせ、todo.md を更新した。
- なぜ: 仕様と実装の食い違いをなくすため。

### 2026-10-25 `1011bad` test: keep second failure log of generic-word filter

- 何を: ありふれた語の判定の初版で、直後の再実行でも 2 件失敗したログを残した。
- なぜ: CLAUDE.md の失敗ログ保存規約に従うため（未追跡のまま残っていた）。

### 2026-10-27 `e638b27` fix: report OpenAlex rate limit instead of crashing

- 何を: OpenAlex の HTTP 429・接続エラーを OpenAlexError にし、CLI で「error: ...」として終了コード 1 を返すようにした。
- なぜ: キーなしで運用すると決めた（#11）ため、無料枠を使い切ってもスタックトレースで落ちないようにする。

### 2026-10-27 `2b27092` docs: specify LLM relevance judge via claude -p

- 何を: paper_intake.md §4.1 に段階 2（claude -p による関連度判定）の仕様を書いた。
- なぜ: 段階 1 の関連度が 1.00 に張り付く（#9）。呼び出し方は利用者が claude -p を選んだ。

### 2026-10-27 `d5a1172` feat: judge relevance of top candidates with claude -p

- 何を: 上位 llm_top_k 件を claude -p で判定し、RQ 定義のハッシュつきで保存して rescore で使うようにした。min_relevance（#15）と判定済みのみを出す制御（#16）を加えた。
- なぜ: 別分野の論文が語の一致だけで上位に来るのを防ぐため。実データで LidarDM 類が 0.1〜0.4 に下がることを確認した。

### 2026-10-27 `8bf0456` feat: run LLM judge in intake run / explore with --no-llm

- 何を: intake run / explore に判定を組み込み、--no-llm と、claude が無いときの段階 1 への切り替えを加えた。Inbox に判定理由を表示する。
- なぜ: CLI から段階 2 を回せるようにするため。

### 2026-10-27 `02ff16e` test: keep failure log of LLM judge test

- 何を: 段階 2 のテストの初版で失敗した 3 件のログを残した。
- なぜ: CLAUDE.md の失敗ログ保存規約に従うため。

### 2026-10-27 `0afa403` docs: align paper intake spec with LLM judge

- 何を: §4.1・§5 に #15・#16 の対応と所要時間を追記し、todo.md を更新した。
- なぜ: 仕様と実装を合わせるため。

### 2026-10-27 `cdc6d82` docs: add Neko mascot at top-right of the TUI

- 何を: `DESIGN.md` §5.9 に右上常駐の ASCII ネコ「Neko」を追加し、ヘッダ図・全体フレーム・レイアウト・アニメーション・Quick Reference を更新。`docs/design.md` §1 と `docs/todo.md` にも反映した。
- なぜ: UI に親しみを持たせつつ、Agent の状態を表情で示すアバターとして機能させるため。絵文字禁止・装飾アニメ禁止の規約に合わせ ASCII のみ・状態遷移時のみ変化とした。

### 2026-10-28 `c34c654` docs: split TUI skeleton into four PRs in todo.md

- 何を: `docs/todo.md` §0.1 に、TUI の骨組みを 4 本の PR（アプリの枠・Agent 欄・Neko・Papers の Inbox）に分けて書き出した。
- なぜ: 機能ごとにブランチと PR を切って小さく積むため。Agent コアは未接続のまま、見た目と操作の器を先に作る。

### 2026-10-28 `39e7c3c` feat: add TUI shell with header, phase tabs and status bar

- 何を: `research-os tui` で Textual アプリを起動できるようにした。ヘッダ・フェーズタブ 1–7・メイン領域（未実装はプレースホルダ）・ステータスバー・`?` ヘルプ・Lab Ink 配色。
- なぜ: Agent 欄・Neko・Papers 画面を載せる器を先に作るため（todo.md §0.1 PR A）。

### 2026-10-28 `336f20e` test: keep failure logs of TUI shell tests

- 何を: テーマの登録順・reactive の初回ウォッチャー・表示幅の測り方の誤りで落ちた 3 回分のログを残した。
- なぜ: CLAUDE.md の失敗ログ保存規約に従うため。

### 2026-10-28 `351dd9f` feat: add Agent pane with input history, suggestions and state

- 何を: 画面下部に Agent 欄を常駐させた。入力（`>` / `i`）・履歴（↑↓）・提案の補完（tab）・状態表示。状態はアプリ全体の `agent_state` として持つ。
- なぜ: 「Agent が主役」（DESIGN.md §1）の入口を先に作るため。Agent コアは未接続なので、送信した指示はログに残して未接続と明示する（todo.md §0.1 PR B）。

### 2026-10-28 `11ded6c` test: keep failure log of Agent pane tests

- 何を: `border_title` がマークアップ文字列を返すことを見落としたテストの失敗ログを残した。
- なぜ: CLAUDE.md の失敗ログ保存規約に従うため。

### 2026-10-28 `3bbcd5f` fix: keep focus off the Agent log and input at startup

- 何を: RichLog をフォーカス不可にし、`AUTO_FOCUS = None` で起動時はどこにもフォーカスを置かないようにした。
- なぜ: 起動直後に Agent ログへ自動フォーカスが当たり背景が明るくなっていた。入力行に当たると `1`–`7` や `q` が効かなくなる。

### 2026-10-28 `46d6131` test: keep failure logs of startup focus fix

- 何を: 修正の途中で入力行が自動フォーカスを取り、5 テストが落ちたログを残した。
- なぜ: CLAUDE.md の失敗ログ保存規約に従うため。
