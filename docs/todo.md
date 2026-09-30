# Research OS — 実装 TODO

`docs/design.md` から起こした実装チェックリスト。
フェーズ順（検索 → 読解 → 比較 → 仮説化 → 実験）に並べる。

---

## 0. 基盤 / プロジェクト骨格

- [ ] TUI フレームワーク選定（Textual / Bubble Tea など）
- [ ] アプリ骨格：① ヘッダ ② フェーズタブ ③ 研究対象 ④ Agent 欄 ⑤ ステータスバー の4層レイアウト
- [ ] フェーズタブの切り替え（Papers / Review / Graph / Hypothesis / Run ＋ 並走トラックの Intel）
- [ ] グローバル状態管理（現在のテーマ・選択論文・接続状態）
- [ ] 設定ファイル読み込み（API キー、MCP エンドポイント、保存先）
- [ ] ロギング / エラーハンドリング基盤
- [ ] テーマ実装：`DESIGN.md` の配色トークン（Hex / 256 / 16 色フォールバック）・枠線・アイコンの ASCII フォールバック
- [ ] 表示幅ユーティリティ：East Asian Width（全角 = 2、Ambiguous 幅の設定）に基づく切り詰め・パディング
- [ ] キーバインド定義（`DESIGN.md` §9）とヘルプ画面

## 1. Research Agent コア

- [ ] `Human → Goal → Agent → Plan → Tool/MCP/Skill → Result` のループ実装
- [ ] Router：ユーザー発話 → Skill 自動選択
- [ ] Skill レジストリ（literature-review / graph / hypothesis / experiment / intel-watch）
- [ ] Subagent 起動・結果集約
- [ ] Agent 欄 UI（自然言語入力、実行ログ、ステップ表示）

## 2. 外部接続 / MCP

- [x] alphaXiv MCP をプロジェクトに追加（`claude mcp add`）
- [ ] alphaXiv MCP の OAuth 認証を通す（`/mcp`）
- [ ] alphaXiv API キーを発行・設定する（関心フィードの定期取得用）
- [ ] Paperpile 連携（ライブラリ読み取り・重複確認・登録）
- [ ] arXiv 検索クライアント
- [ ] GitHub 連携（リポジトリ・コード検索）
- [ ] Semantic Scholar / OpenAlex（将来）
- [ ] Neo4j 接続（Knowledge Graph 永続化）
- [ ] ステータスバー：各接続のヘルスチェックと表示（`Paperpile ✓ arXiv ✓ alphaXiv ✓ GitHub ✓ Feeds ✓`）
- [ ] Feeds 接続：Intel 監視対象ソースの巡回状態を集計して表示（`Feeds ✓ 8/9`、失敗ソースがあれば警告）

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

### 3.1 alphaXiv 関心フィード（design.md §3.2 / `docs/new_features/alphaXiv.md`）

- [ ] 関心プロファイル `interests.yaml` のスキーマ定義と読み込み（topics / researchers / arxiv_categories / schedule）
- [ ] トピック検索：タグごとに `discover_papers`（`prioritize=recency`）を呼ぶ。検索は 1 メッセージ 2 回までの制限に合わせてまとめる
- [ ] 研究者経由の取得：`get_researcher_papers` で登録研究者の新着を取る
- [ ] （任意）arXiv API でカテゴリ新着を取り、網羅性を補う
- [ ] arXiv ID で重複を除き、複数タグにヒットした論文はタグを統合する
- [ ] 既読キャッシュ（arXiv ID → status: new / seen / saved / dismissed、日本語訳）と新着の抽出
- [ ] 一覧の日本語化：タイトル＋Abstract 冒頭を全件訳す（原タイトル・arXiv ID を併記し、専門用語は原語のまま）
- [ ] 詳細の日本語化：選択した論文だけ `get_paper_content` → 日本語要約（キャッシュして再生成しない）
- [ ] フィード一覧 UI（タグ表示、公開日順／votes 順／タグ別の並べ替え、詳しく・保存・不要の操作）
- [ ] Agent 指示：`今日の新着論文` で手動取得
- [ ] 定期取得を巡回ジョブ基盤に載せる（8.8 と共通）。API キー認証で動かす
- [ ] テスト：重複除去・既読フィルタ・日本語化のキャッシュ（失敗ログは `logs/` に残す）

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
- [ ] Intel 由来の Node / Edge を Graph に統合（詳細は「8. Intel」）：Company / Product / Customer / Event と develops / provides / uses / adopts / announces

## 6. Hypothesis — 仮説を研究オブジェクト化

- [ ] ロジックチェーン管理：Problem → Research Gap → Research Question → Hypothesis → Experiment
- [ ] Research Gap 自動抽出（Graph / Review の結果から）
- [ ] Research Question 生成
- [ ] Hypothesis 生成（検証可能な形式、指標を含む）
- [ ] 仮説の「研究オブジェクト」永続化（ID・履歴・リンク）
- [ ] Experiment への引き渡し
- [ ] Intel の企業間比較・トレンド分析から研究テーマ・事業機会を探索し、Hypothesis の入力にする

## 7. Run — 実験実行

- [ ] 実験定義 UI（Experiment 名 / Dataset / Models / Metrics）
- [ ] `> Implement this experiment`：`experiments/<name>/` に config.yaml / train.py / evaluate.py / README.md を生成
- [ ] `[ Run ]`：Claude Code → Python → PyTorch → Training → Evaluation パイプライン起動
- [ ] 実行ログ・進捗のストリーム表示
- [ ] Metrics 集計（Success Rate / Failure AUC / Slip Rate ...）
- [ ] 結果を Hypothesis オブジェクトへフィードバック

## 8. Intel — 企業・産業の動向監視

`docs/design.md` の 2.6（画面）と 6（監視パイプライン）に対応。元メモは `docs/memo.md`。
Technology Intelligence（技術革新）と Business Intelligence（ビジネスイノベーション）を別々に抽出・比較する。

### 8.1 監視対象レジストリ

- [ ] レジストリのデータモデル（name / category（複数可）/ org_type / origin_country / us_presence / parent + 有効期間 / sources / priority）
- [ ] 5 カテゴリの定義（ロボット基盤モデル・World Model / ヒューマノイド・汎用ロボット / 物流・製造・産業ロボット / 自動運転・自律移動 / AI基盤・シミュレーション）
- [ ] 企業と研究組織・事業部門の区別、創業国と米国拠点の区別（例：Google DeepMind、Intrinsic、1X Technologies、Waabi）
- [ ] 監視設定ファイルの読み込み（companies / check_frequency / summary_language / topics / track_article_updates）
- [ ] 初期監視対象 9 社の登録（Physical Intelligence / Skild AI / Figure AI / World Labs / Generalist AI / Dexterity / Ambi Robotics / NVIDIA / Google DeepMind）と、各社の公式ブログ URL・RSS 有無・記事抽出方法の調査
- [ ] `docs/memo.md` の全企業カテゴリ（重複を除いて 22 社）を段階的にレジストリへ移行

### 8.2 収集（巡回・新着検知）

- [ ] 本文取得方式の決定と実装（RSS/Atom → HTML 抽出のフォールバック → fetch 系 MCP）
- [ ] robots.txt・利用規約・レート制限への対応
- [ ] 新着検知（URL・公開日・本文ハッシュによる既読管理）
- [ ] 論文の新規確認（arXiv / 記事内リンク）と GitHub リポジトリの更新確認
- [ ] 巡回失敗のリトライ・エラー記録（Feeds ステータスへ反映）

### 8.3 要約・構造化抽出

- [ ] 記事本文の抽出と日本語要約（新着検知時のみ実行）
- [ ] Technology Intelligence 抽出スキーマ（技術 / モデル / 学習 / 評価 / 論文 / OSS / 実機）
- [ ] Business Intelligence 抽出スキーマ（商用化 / 顧客 / 経済性 / 実運用 / 事業戦略 / 事業モデル / 根拠）
- [ ] 数値の信頼性ラベル（`company_claimed` / `third_party_verified`）と、指標の種類の明示（ARR ≠ 認識済み売上）
- [ ] 事業化ステージの分類（技術発表 → 実機統合 → 試験導入 → 本番運用 → 継続運用の実績）
- [ ] 記事内の論文・GitHub リンクを Papers の検索・登録パイプラインへ引き渡し

### 8.4 更新追跡

- [ ] 記事スナップショット（ハッシュ）の保存
- [ ] 過去記事の変更検知と Diff 生成（更新・撤回・製品終了）
- [ ] 変更時に `updated_at` / `changes` を記録し、Graph 上の Event も更新
- [ ] Intel 画面の `⟳ Updated` 表示

### 8.5 Knowledge Graph 拡張・来歴管理

- [ ] Node：Company / Product / Customer / Event（`stage` 属性）を追加（技術は既存の Method で表現）
- [ ] Edge：develops / provides / uses / adopts / announces（Company・Product・Model・Customer・Event 間）
- [ ] 時間・根拠・来歴の属性（announced_at / occurred_at / retrieved_at / updated_at / source_url / reliability / changes）
- [ ] 既存の Paper / Method ノードとの接続（Paper `describes` 技術の紐付け）

### 8.6 分析・出力

- [ ] 企業間比較（商用化段階・事業モデル・技術方針）— 週 1 回
- [ ] トレンド分析（VLA→World Action Model / 視覚のみ→Vision-Tactile / 模倣学習と強化学習の統合 / Agentic Robotics）— 週 1 回
- [ ] 週次レポート生成（日本語）
- [ ] 研究テーマ・事業機会の探索（技術と事業化の接点）と Hypothesis への連携
- [ ] 問い「フィジカルAIの技術革新は、どのような新しい顧客価値やビジネスモデルを生み出しているのか？」に答えるクエリ

### 8.7 Intel 画面 UI

- [ ] Intel タブ：Tech / Business / Sources の 3 タブ
- [ ] フィード表示（日付・企業・観点・要約・claim ラベル）とフィルタ（企業 / 期間）
- [ ] Sources タブ：ソース一覧・巡回状態・追加／削除・優先度
- [ ] Agent 指示：`Summarize this week's updates from ...` / `Compare Figure and Skild on their commercialization stage` / `Add ... blog to the watch list` / `Send papers cited in these posts to Papers` / `Generate the weekly intelligence report`

### 8.8 定期実行基盤

- [ ] 巡回ジョブの実行基盤を決定し ADR を起票（cron / systemd timer / 常駐ワーカー / TUI 起動時のキャッチアップ）
- [ ] 毎日（ブログ・論文・GitHub）と週 1 回（比較・トレンド分析）のスケジュール実装
- [ ] alphaXiv 関心フィード（3.1）の定期取得ジョブを同じ基盤に登録
- [ ] 記事本文・スナップショット・抽出結果の保存先の決定（Neo4j と別ストアの切り分け）
- [ ] LLM 呼び出しコストの見積もりと上限管理

### 8.9 テスト

- [ ] 抽出スキーマのフィクスチャテスト（実記事サンプル → Tech / Business 抽出）
- [ ] 新着検知・変更検知（Diff）のテスト
- [ ] 巡回失敗時のログ保存（`logs/<test-name>/` 規約に従う）

## 9. 仕上げ

- [ ] キーバインド / ヘルプ画面
- [ ] セッションの保存・復元
- [ ] README / 使い方ドキュメント
- [ ] テスト（Agent ループ、各 Skill、MCP モック）
