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
