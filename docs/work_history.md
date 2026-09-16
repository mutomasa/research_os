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

### 2026-09-16 `<pending>` docs: add AI-native closed-loop research feature proposal

- 何を: `docs/new_feature.md`（Status: Proposed）を追加。Hypothesis/Experiment/Run/Evidence/Claim の研究オブジェクトモデル、Evaluation・Paper 画面の追加、Research Gate（R0〜R6）、Human-in-the-Loop 方針、MVP 範囲を定義した。
- なぜ: 現行の `Papers → Review → Graph → Hypothesis → Run` だけでは、評価結果から仮説・実装へ戻るフィードバックループや、Evidence に基づく論文更新を扱えないため、closed-loop な研究エンジンとしての拡張案をまとめる必要があった。
