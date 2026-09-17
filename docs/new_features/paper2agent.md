# Paper2Agent 統合構想

## 概要

Paper2Agent を内部にコピーして作り直すのではなく、**「Paper Agent 生成バックエンド」として組み込む** のが最もきれいな統合方法である。

- Paper2Agent は、Claude Code / Codex などの Coding Agent 上で動く Skill として設計されており、論文と Repository から **Paper Skill + 検証済み MCP Server** を生成できる。
- 一方 Research OS は、「検索 → 読解 → 比較 → 仮説化 → 実験」を TUI から一貫して扱う研究 IDE である。

両者の役割はほぼ補完関係にあり、Research OS が Paper2Agent を呼び出して論文をエージェント化し、その成果物を Research OS 側で管理する構成が自然である。

## 推奨アーキテクチャ

```text
                         Research OS
                             │
                 ┌───────────┴───────────┐
                 │                       │
           Research State            Research Agent
                 │                       │
    Paper / Hypothesis / Experiment      │
                 │                       │
                 │               Claude Code / Codex
                 │                       │
                 │                 Paper2Agent Skill
                 │                       │
                 │           Paper + Repository
                 │                       │
                 │                       ▼
                 │              ┌─────────────────┐
                 │              │ Paper Agent     │
                 │              │                 │
                 │              │ Skill           │
                 │              │ Validated MCP   │
                 │              └────────┬────────┘
                 │                       │
                 └─────────────── Register
                                         │
                                         ▼
                               Paper Agent Registry
                                         │
                         ┌───────────────┼──────────────┐
                         ▼               ▼              ▼
                       Review        Hypothesis       Experiment
```

要するに **「Research OS が Paper2Agent を呼び出して論文をエージェント化し、その成果物を Research OS 側で管理する」** という構成である。

---

## 1. Research OS に「Agentify Paper」を追加する

現在の Research OS には次の画面がある。

- Papers
- Review
- Graph
- Hypothesis
- Run

ここに、Papers / Review 画面から次の操作を追加する。

```text
VLA-JEPA
────────────────────────
PDF       ✓
GitHub    ✓
Code      ✓

[ Review ]
[ Compare ]
[ Agentify ]
```

`Agentify` を実行すると、次の変換が行われる。

```text
Paper
  +
GitHub Repository
       ↓
   Paper2Agent
       ↓
  Paper Skill
  +
  Paper MCP
```

Research OS から見ると、Paper2Agent は **「Paper Compiler」** に相当する。

---

## 2. Paper2Agent 本体は Coding Agent に実行させる

ここは設計上重要な判断である。Research OS の Python コードから Paper2Agent の内部 API を直接呼ぶのではなく、次の経路を採る方が Paper2Agent 本来の設計に合っている。

```text
Research OS
    ↓
Agent Runtime
    ↓
Claude Code / Codex
    ↓
Paper2Agent Skill
```

Paper2Agent の公式 README でも、Claude Code や Codex に Skill をインストールし、

```text
Use the paper2agent skill to agentify this paper...
```

と指示する方式が採られている（Claude Code では `/paper2agent`、Codex では `$paper2agent` として利用できる）。

したがって Research OS 側には、次のような Runtime 抽象化を置くとよい。

```python
class AgentRuntime:
    def run(self, task): ...

class ClaudeCodeRuntime(AgentRuntime):
    ...

class CodexRuntime(AgentRuntime):
    ...
```

こうしておけば、将来的に次のような Runtime を交換できる。

- Claude Code
- Codex
- Gemini CLI
- OpenHands

---

## 3. Research OS のディレクトリ構成

例えば次のような構成にする。

```text
research_os/
├── research/
│   ├── papers/
│   ├── hypotheses/
│   └── experiments/
│
├── agents/
│   ├── runtimes/
│   │   ├── claude_code.py
│   │   └── codex.py
│   │
│   └── paper_agent/
│       ├── manager.py
│       ├── registry.py
│       └── models.py
│
├── paper_agents/
│   ├── registry.yaml
│   │
│   └── vla-jepa/
│       ├── metadata.yaml
│       ├── skill/
│       └── mcp/
│
├── experiments/
├── evidence/
└── docs/
```

Paper2Agent 自身の出力形式も、次のような Skill + MCP 構成になっている。

```text
dist/<project>-agent/
├── skill/<paper-name>/
└── mcp/<repository-name>-mcp/
```

そのため Research OS 側では、この成果物をほぼそのまま取り込める。

---

## 4. Paper Agent Registry を作る

Research OS 側にとって、これが最も重要なコンポーネントになる。

```yaml
id: paper-agent-vla-jepa

paper:
  id: arxiv-2602.10098
  title: VLA-JEPA

repository:
  url: https://github.com/...
  commit: abc1234

agentification:
  backend: paper2agent
  runtime: claude-code

skill:
  path: paper_agents/vla-jepa/skill

mcp:
  path: paper_agents/vla-jepa/mcp
  status: ready

validation:
  status: passed
  tools:
    total: 8
    passed: 7
    failed: 1

created_at: 2026-09-17
```

Research OS は Paper2Agent の内部実装を理解する必要はなく、次の項目だけを見ればよい。

- `READY`
- `VALIDATED`
- `AVAILABLE TOOLS`
- `VERSION`
- `SOURCE PAPER`
- `SOURCE COMMIT`

---

## 5. Paper2Agent の Validation 結果を Research OS に取り込む

これは必ず取り込むべきである。Paper2MCP は単純な wrapper generator ではなく、次の段階を踏んでツールを生成する。

```text
Environment setup
       ↓
Tool discovery
       ↓
Reference execution
       ↓
Tool implementation
       ↓
Independent verification
       ↓
MCP integration
       ↓
Runtime validation
       ↓
Delivery
```

さらに、各 MCP Tool は既存 Repository のコードに紐付いていなければならず、Implementer とは別の Verifier Agent による検証も要求される。これは Research OS の Experiment 管理と非常に相性がよい。

Research OS の画面では、例えば次のように表示できるとよい。

```text
Paper Agent: VLA-JEPA

Status        READY
MCP           CONNECTED
Tools         7 / 8 validated
Repository    abc1234
Environment   Python 3.x / CUDA xx

Tools
✓ preprocess_dataset
✓ train_model
✓ evaluate
✓ inference
✓ visualize
✓ reproduce_table
✓ reproduce_figure
✗ export_model
```

---

## 6. Paper Agent を実験の Baseline として選択できるようにする

ここから Research OS らしい価値が生まれる。今の Run 画面を、次のように拡張する。

```text
Experiment: VT-JEPA-001

Baseline
[ VLA-JEPA Paper Agent ▼ ]

Extension
[ Add tactile encoder ]

Dataset
[ so101_dataset_v3 ]

Metrics
[ Success Rate ]
[ Failure AUC ]

[Create Experiment]
```

この操作の裏側では、次の流れが実行される。

```text
Hypothesis
「Tactile latent prediction improves failure prediction」
        ↓
VLA-JEPA Paper MCP
        ↓
取得（preprocessing / model / training / evaluation）
        ↓
Claude Code / Codex
        ↓
新規実装
        ↓
Experiment Harness
```

これは Paper2Agent 単体にはない、Research OS ならではの価値である。

---

## 7. Knowledge Graph にも追加する

Research OS は Knowledge Graph を構想している。Paper Agent を Node として追加すると、次のような関係が表現できる。

```text
Paper
  ├── implements ──→ Method
  ├── provides ────→ Tool
  └── agentified_as → PaperAgent

PaperAgent
  ├── exposes → MCPTool
  └── used_by → Experiment

Experiment
  ├── tests → Hypothesis
  └── produces → Result
```

例えば VLA-JEPA の場合、次のような系譜になる。

```text
VLA-JEPA Paper
       │
       ▼
VLA-JEPA Agent
       │
       ├─ train()
       ├─ evaluate()
       └─ inference()
              │
              ▼
        EXP-VT-001
              │
              ▼
        Hypothesis H-003
```

これにより、**「この Experiment はどの論文のどのコードを元にしたのか」** が追跡できる。これは研究の Provenance / Lineage として大きな価値を持つ。

---

## 8. CLI 設計

TUI だけでなく CLI も持たせる。

```bash
# 論文登録
research paper add <paper-url>

# GitHub repository を紐付け
research paper repo <paper-id> <github-url>

# Paper2Agent 実行
research paper agentify <paper-id>
```

Agent Runtime も指定できるようにする。

```bash
research paper agentify <paper-id> --runtime claude
# または
research paper agentify <paper-id> --runtime codex
```

登録状況の確認:

```bash
$ research agent list
NAME            STATUS      TOOLS
VLA-JEPA        READY       7
SAM2            READY       12
Marigold-V2     READY       5
Tactile-WM      BUILDING    -
```

詳細確認:

```bash
research agent inspect vla-jepa
```

最終的には、次のように Experiment 作成までつながると理想的である。

```bash
research experiment create --baseline paper-agent:vla-jepa
```

---

## 9. Research OS から投げるプロンプト

MVP であれば API 連携すら不要である。Research OS から Claude Code / Codex を subprocess で起動し、次のようなプロンプトを渡すだけで十分である。

```text
Use the installed paper2agent skill.

Paper:
<PAPER_PATH>

Repository:
<GITHUB_URL>

Create a reviewed paper skill and tested MCP server.

Output:
<RESEARCH_OS_PROJECT>/paper_agents/<PAPER_ID>/

Run all verification required by Paper2Agent.

Return a JSON summary containing:
- generated_skill
- generated_mcp
- available_tools
- validation_status
- runtime_requirements
- excluded_tools
- limitations
```

Research OS は stdout に出力された JSON だけを受け取ればよい。つまり最初の実装は、次の経路で十分である。

```text
Research OS
 ↓ subprocess
Claude Code
 ↓
Paper2Agent Skill
 ↓
filesystem
 ↓
Research OS Registry
```

無理に LangGraph などのオーケストレーションを挟む必要はない。

---

## 10. 実装は 3 段階で進める

### v0.1 — Paper2Agent Launcher

まずはここだけを実装する。

```text
Paper selection
      ↓
  [Agentify]
      ↓
Claude Code / Codex
      ↓
   Paper2Agent
      ↓
   MCP 生成
```

追加するもの:

- `agents/runtimes/`
- `paper_agents/`

これなら既存コードへの変更はかなり小さく済む。

### v0.2 — Paper Agent Registry

次に、次の関係を永続化する。

```text
Paper → Paper Agent → MCP Tools
```

TUI 側では、次のいずれかの形で表示する。

- ナビゲーションに `Agents` 画面を新設する（`Papers / Review / Agents / Graph / Hypothesis / Run`）
- あるいは Paper 詳細画面に Agent Status を表示する

### v0.3 — Experiment Integration

最後に、次の流れを実装する。

```text
Paper Agent → Hypothesis → Experiment → Coding Agent → Harness → Evidence
```

ここまで来れば、**Research OS = Paper Agent を利用して研究を回す Control Plane** になる。

---

## 重要: Paper2Agent を fork して埋め込まない

ここは強く分離すべき部分である。

**避けるべき構成:**

```text
Research OS
   └── Paper2Agent のソースコードを大量コピー
```

**採用すべき構成:**

```text
Research OS
     ├── AgentRuntime
     └── PaperAgentBackend
                │
                ▼
           Paper2Agent Skill
```

Interface だけを決めておく。

```python
class PaperAgentBackend:
    def agentify(
        self,
        paper,
        repository=None,
    ) -> PaperAgentArtifact:
        ...
```

最初の実装は `Paper2AgentBackend` のみとし、将来的には次のような Backend を追加できるようにする。

- `Paper2AgentBackend`
- `Paper2CodeBackend`
- `CustomBackend`

---

## 最終的な Research OS 像

最終形としては、次の構成が最もきれいだと考えられる。

```text
                  Research OS
              Research Control Plane

                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
    Papers       Hypotheses    Experiments
       │             │             │
       ▼             │             │
 Paper2Agent         │             │
       │             │             │
       ▼             │             │
 Paper Agent ────────┼─────────────┘
       │             │
       ▼             ▼
      MCP       AI Coding Agent
       │        Claude / Codex
       └──────┬──────┘
              ▼
       Experiment Harness
              │
              ▼
            Result
              │
              ▼
        Evidence Graph
              │
              ▼
        Next Hypothesis
```

Research OS がすでに持っている「研究オブジェクトを永続化する」「ADR や実験ログなどの証跡を残す」という思想とも非常に相性がよい。現在の `CLAUDE.md` でも、テスト失敗ログを残して Agent が原因を追跡できるようにすることや、設計判断を ADR として保存する方針が明示されている。

したがって、最初に実装するなら `research paper agentify` + Paper Agent Registry までをおすすめする。ここまでであれば、既存の Research OS の思想を壊さず、Paper2Agent の強みをそのまま取り込むことができる。
