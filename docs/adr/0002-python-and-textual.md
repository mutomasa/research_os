# ADR-0002: 実装言語と TUI フレームワーク — Python + Textual

## Status
Accepted

## Context
設計フェーズを終え、Phase A（Venue レジストリ・研究プロファイルのデータ層）から実装に入る。
実装言語と TUI フレームワークは `docs/todo.md` §0 の先頭タスクで未決のままだった（`DESIGN.md` 冒頭の注記）。

制約と要件：

- 実験側の資産は Python（PyTorch / LeRobot / SmolVLA / VLA-JEPA）。Run 画面から学習・評価を直接呼びたい。
- Paper2Agent 統合構想（`docs/new_features/paper2agent.md`）は Python からの呼び出しを前提にしている。
- Claude Agent SDK・MCP クライアントを Research Agent コアで使う。
- `DESIGN.md` の描画規約（配色トークンと 256 / 16 色フォールバック、角丸・二重線の枠、East Asian Width による全角幅、サブタブ、確認ダイアログ）を満たせること。

検討した選択肢：

1. **Python + Textual** — CSS 風のスタイル定義、ウィジェット、非同期ワーカーを持つ。研究資産と同じ言語で書ける。
2. **Go + Bubble Tea** — 起動が速く単一バイナリで配布できる。Python 資産の呼び出しは別プロセスとの IPC が必要になる。
3. **Rust + Ratatui** — 高速で堅牢だが、描画以外（状態管理・ウィジェット）を自前で組む量が多く、Python 資産との境界も残る。

## Decision
- 実装言語は **Python（3.12 以上）**、TUI フレームワークは **Textual** とする。
- パッケージ管理は **uv**、レイアウトは `src/research_os/`（src レイアウト）と `tests/`。
- YAML の読み込みは PyYAML、スキーマ検証は pydantic v2、テストは pytest を使う。
- 画面に依存しないデータ層（`research_os.data`）と TUI（`research_os.tui`）を分け、データ層は TUI なしでテストできるようにする。

## Consequences
- **メリット**
  - Run 画面・Paper2Agent・Agent SDK と同じプロセス・同じ言語で連携できる。
  - データ層を先に実装・テストでき、TUI の作り込みと並行して進められる。
- **デメリット・トレードオフ**
  - Go / Rust に比べて起動が遅く、配布には Python 環境（uv）が必要。
  - 全角文字の表示幅は Textual 任せにせず、`DESIGN.md` の規約（Ambiguous 幅の設定を含む）に沿った自前のユーティリティで扱う必要がある。
- **フォローアップ**
  - `DESIGN.md` 冒頭の「TUI フレームワークは未選定」の注記を更新する。
  - 配色トークンを Textual のテーマ・CSS 変数に落とし込む方法は、TUI 骨格の実装時に決める。
