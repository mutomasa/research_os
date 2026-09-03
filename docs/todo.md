# Research OS — 実装 TODO

`docs/design.md` から起こした実装チェックリスト。
フェーズ順（検索 → 読解 → 比較 → 仮説化 → 実験）に並べる。

---

## 0. 基盤 / プロジェクト骨格

- [ ] TUI フレームワーク選定（Textual / Bubble Tea など）
- [ ] アプリ骨格：① ヘッダ ② フェーズタブ ③ 研究対象 ④ Agent 欄 ⑤ ステータスバー の4層レイアウト
- [ ] フェーズタブの切り替え（Papers / Review / Graph / Hypothesis / Run）
- [ ] グローバル状態管理（現在のテーマ・選択論文・接続状態）
- [ ] 設定ファイル読み込み（API キー、MCP エンドポイント、保存先）
- [ ] ロギング / エラーハンドリング基盤

## 1. Research Agent コア

- [ ] `Human → Goal → Agent → Plan → Tool/MCP/Skill → Result` のループ実装
- [ ] Router：ユーザー発話 → Skill 自動選択
- [ ] Skill レジストリ（literature-review / graph / hypothesis / experiment）
- [ ] Subagent 起動・結果集約
- [ ] Agent 欄 UI（自然言語入力、実行ログ、ステップ表示）

## 2. 外部接続 / MCP

- [x] alphaXiv MCP をプロジェクトに追加（`claude mcp add`）
- [ ] alphaXiv MCP の OAuth 認証を通す（`/mcp`）
- [ ] Paperpile 連携（ライブラリ読み取り・重複確認・登録）
- [ ] arXiv 検索クライアント
- [ ] GitHub 連携（リポジトリ・コード検索）
- [ ] Semantic Scholar / OpenAlex（将来）
- [ ] Neo4j 接続（Knowledge Graph 永続化）
- [ ] ステータスバー：各接続のヘルスチェックと表示（`Paperpile ✓ arXiv ✓ alphaXiv ✓ GitHub ✓`）

### alphaXiv MCP ツール割り当て

- [ ] `discover_papers` → Papers 検索
- [ ] `get_paper_content` → Review 全文 / AI 要約取得
- [ ] `answer_pdf_queries` → Review 質問ベース読解（引用付き）
- [ ] `read_files_from_github_repository` → Run / 実装調査
- [ ] `find_researchers` / `get_researcher_papers` → 著者からの探索
- [ ] `list_library` / `save_papers_to_folder` / `create_folder` → ライブラリ整理

## 3. Papers — 文献を探す

- [ ] クエリ入力 UI
- [ ] Sources 選択（☑ Paperpile / ☑ arXiv / ☑ Semantic Scholar / ☑ alphaXiv）
- [ ] Year フィルタ
- [ ] 複数ソース横断検索とマージ・重複排除
- [ ] 検索結果リスト（タイトル / 年 / ソース / タグ、★ で選択）
- [ ] Abstract 評価によるランキング
- [ ] Agent 指示：`Find papers about ...` / `Show only papers after 2024` / `Add selected papers to Paperpile` / `Discover related papers on alphaXiv`
- [ ] 選択論文を Paperpile / alphaXiv ライブラリへ登録

## 4. Review — 論文を深く読む

- [ ] 選択論文リスト表示（Selected Papers: N）
- [ ] 3本選択で比較表を自動生成
- [ ] 比較表の軸抽出（Input / World Model / Policy / Future Prediction / Robot ...）
- [ ] `> Compare these papers`：Similarities / Differences / Novelty / Limitations / Missing experiments
- [ ] PDF 解析（`answer_pdf_queries` によるページ単位・引用付き抽出）
- [ ] 論文理解ワークスペース UI（メモ・ハイライト保持）

## 5. Graph — 研究領域の構造理解

- [ ] Knowledge Graph データモデル
  - [ ] Node 種別：Paper / Method / Dataset / Model / Task / Robot / Metric / Research Problem
  - [ ] Edge 種別：uses / evaluates_on / extends / solves / related_to
- [ ] 論文メタデータ → Node/Edge 抽出パイプライン
- [ ] グラフの TUI 描画（ツリー / ネットワーク表示）
- [ ] Agent 問い合わせ：`Show papers connecting JEPA and tactile sensing` / `What research areas are disconnected?`
- [ ] Neo4j への永続化と再読み込み

## 6. Hypothesis — 仮説を研究オブジェクト化

- [ ] ロジックチェーン管理：Problem → Research Gap → Research Question → Hypothesis → Experiment
- [ ] Research Gap 自動抽出（Graph / Review の結果から）
- [ ] Research Question 生成
- [ ] Hypothesis 生成（検証可能な形式、指標を含む）
- [ ] 仮説の「研究オブジェクト」永続化（ID・履歴・リンク）
- [ ] Experiment への引き渡し

## 7. Run — 実験実行

- [ ] 実験定義 UI（Experiment 名 / Dataset / Models / Metrics）
- [ ] `> Implement this experiment`：`experiments/<name>/` に config.yaml / train.py / evaluate.py / README.md を生成
- [ ] `[ Run ]`：Claude Code → Python → PyTorch → Training → Evaluation パイプライン起動
- [ ] 実行ログ・進捗のストリーム表示
- [ ] Metrics 集計（Success Rate / Failure AUC / Slip Rate ...）
- [ ] 結果を Hypothesis オブジェクトへフィードバック

## 8. 仕上げ

- [ ] キーバインド / ヘルプ画面
- [ ] セッションの保存・復元
- [ ] README / 使い方ドキュメント
- [ ] テスト（Agent ループ、各 Skill、MCP モック）
