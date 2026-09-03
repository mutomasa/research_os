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

## ドキュメント

- [UI 設計ドキュメント](docs/design.md) — レイアウト、各画面、Agent 操作、外部接続、内部アーキテクチャの詳細

## 現在の状態

現在は UI とアーキテクチャの設計段階です。実装方針と画面仕様の詳細は設計ドキュメントを参照してください。
