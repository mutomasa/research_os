Paper2Agentを内部にコピーして作り直すのではなく、「Paper Agent生成バックエンド」として組み込むのが一番きれいです。

Paper2Agent自体がClaude Code / CodexなどのCoding Agent上で動くSkillとして設計されており、論文とRepositoryから Paper Skill + 検証済みMCP Server を生成できます。
一方、Research OSは「検索 → 読解 → 比較 → 仮説化 → 実験」をTUIから一貫して扱う研究IDEなので、役割がほぼ補完関係です。

推奨アーキテクチャ

こうします。

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

要するに、

Research OSがPaper2Agentを呼び出して論文をAgent化し、その成果物をResearch OS側で管理する

という構成です。

1. Research OSに「Agentify Paper」を追加する

今のResearch OSには、

Papers
Review
Graph
Hypothesis
Run

があります。

ここにまず、

Papers / Review

VLA-JEPA
────────────────────────
PDF       ✓
GitHub    ✓
Code      ✓

[ Review ]
[ Compare ]
[ Agentify ]

という操作を追加します。

Agentifyすると、

Paper
+
GitHub Repository
       ↓
Paper2Agent
       ↓
Paper Skill
+
Paper MCP

を生成します。

Research OSから見るとPaper2Agentは、

Paper Compiler

です。

2. Paper2AgentそのものはCoding Agentに実行させる

ここは重要です。

Research OS PythonコードからPaper2Agent内部APIを直接呼ぶより、

Research OS
    ↓
Agent Runtime
    ↓
Claude Code / Codex
    ↓
Paper2Agent Skill

の方がPaper2Agent本来の設計に合っています。

Paper2Agent公式READMEでも、Claude CodeやCodexにSkillをインストールし、

Use the paper2agent skill to agentify this paper...

と指示する方式になっています。Claude Codeでは/paper2agent、Codexでは$paper2agentとして利用できます。

したがってResearch OSには、

class AgentRuntime:
    def run(self, task): ...

class ClaudeCodeRuntime(AgentRuntime):
    ...

class CodexRuntime(AgentRuntime):
    ...

のような抽象化を置くとよいです。

そうすれば将来、

Claude Code
Codex
Gemini CLI
OpenHands

を交換できます。

3. Research OSのディレクトリ

例えばこうします。

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
│
├── evidence/
│
└── docs/

Paper2Agent自身の出力形式も、

dist/<project>-agent/
├── skill/<paper-name>/
└── mcp/<repository-name>-mcp/

というSkill + MCP構成になっています。

そのためResearch OS側では、成果物をほぼそのまま取り込めます。

4. Paper Agent Registryを作る

これがResearch OS側では重要です。

例えば、

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

Research OSはPaper2Agent内部を理解する必要はありません。

見るのは、

READY
VALIDATED
AVAILABLE TOOLS
VERSION
SOURCE PAPER
SOURCE COMMIT

だけです。

5. Paper2AgentのValidation結果をResearch OSに取り込む

これは必ず取り込んだ方がいいです。

Paper2MCPは単純なwrapper generatorではなく、

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

という段階を踏みます。

さらに、各MCP Toolは既存Repositoryコードに紐付いていなければならず、Implementerとは別のVerifier Agentによる検証も要求されています。

これはResearch OSのExperiment管理と非常に相性がいいです。

Research OSの画面では、

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

くらい表示できるとよいです。

6. Paper Agentを実験のBaselineとして選択できるようにする

ここからResearch OSらしくなります。

今のRun画面を、

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

とします。

すると裏では、

Hypothesis

「Tactile latent prediction improves
 failure prediction」

        ↓

VLA-JEPA Paper MCP

        ↓

取得
- preprocessing
- model
- training
- evaluation

        ↓

Claude Code / Codex

        ↓

新規実装

        ↓

Experiment Harness

という流れになります。

ここがPaper2Agent単体にはないResearch OSの価値です。

7. Knowledge Graphにも追加する

Research OSはKnowledge Graphを構想しています。

Paper AgentをNodeとして追加すると面白いです。

Paper
  │
  ├── implements ──→ Method
  │
  ├── provides ────→ Tool
  │
  └── agentified_as → PaperAgent

PaperAgent
  │
  ├── exposes → MCPTool
  │
  └── used_by → Experiment

Experiment
  │
  ├── tests → Hypothesis
  └── produces → Result

例えば、

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

になります。

これなら、

「このExperimentはどの論文のどのコードを元にしたのか？」

が追跡できます。

これは研究のProvenance / Lineageとしてかなり価値があります。

8. CLIはこうしたい

TUIだけでなくCLIを持たせます。

# 論文登録
research paper add <paper-url>

# GitHub repositoryを紐付け
research paper repo <paper-id> <github-url>

# Paper2Agent実行
research paper agentify <paper-id>

Agent Runtimeも指定できます。

research paper agentify <paper-id> \
  --runtime claude

または、

research paper agentify <paper-id> \
  --runtime codex

確認：

research agent list
NAME            STATUS      TOOLS
VLA-JEPA        READY       7
SAM2            READY       12
Marigold-V2     READY       5
Tactile-WM      BUILDING    -

詳細：

research agent inspect vla-jepa

そして、

research experiment create \
  --baseline paper-agent:vla-jepa

までつながればかなり良いです。

9. Research OSから投げるプロンプト

MVPならAPI連携すら必要ありません。

Research OSからClaude Code/Codexをsubprocessで起動し、

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

くらいで十分です。

そしてstdoutのJSONだけResearch OSが受け取ります。

つまり最初は、

Research OS
 ↓ subprocess
Claude Code
 ↓
Paper2Agent Skill
 ↓
filesystem
 ↓
Research OS Registry

でいいです。

無理にLangGraphを挟む必要もありません。

10. 3段階で実装するのがおすすめ
v0.1 — Paper2Agent Launcher

まずこれだけ。

Paper selection
      ↓
[Agentify]
      ↓
Claude Code / Codex
      ↓
Paper2Agent
      ↓
MCP生成

追加するもの：

agents/runtimes/
paper_agents/

これならかなり小さい変更です。

v0.2 — Paper Agent Registry

次に、

Paper
  ↓
Paper Agent
  ↓
MCP Tools

を永続化。

TUIから、

Papers
Review
Agents ← NEW
Graph
Hypothesis
Run

またはPaper詳細にAgent statusを表示します。

v0.3 — Experiment Integration

最後に、

Paper Agent
      ↓
Hypothesis
      ↓
Experiment
      ↓
Coding Agent
      ↓
Harness
      ↓
Evidence

を作ります。

ここまで来れば、

Research OS = Paper Agentを利用して研究を回すControl Plane

になります。

重要：Paper2Agentをforkして中に埋め込まない方がいい

私はここは強く分離します。

× Research OS
   └── Paper2Agent source codeを大量コピー

ではなく、

○ Research OS
     │
     ├── AgentRuntime
     │
     └── PaperAgentBackend
                │
                ▼
           Paper2Agent Skill

とします。

例えばInterfaceだけ決めます。

class PaperAgentBackend:
    def agentify(
        self,
        paper,
        repository=None,
    ) -> PaperAgentArtifact:
        ...

最初の実装：

Paper2AgentBackend

将来、

Paper2AgentBackend
Paper2CodeBackend
CustomBackend

を追加できます。

最終的なResearch OS像

一番きれいなのはこれだと思います。

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

Research OSがすでに持っている「研究オブジェクトを永続化する」「ADRや実験ログなど証跡を残す」という思想とも非常に相性がいいです。現在のCLAUDE.mdでも、テスト失敗ログを残してAgentが原因を追跡できることや、設計判断をADRとして保存する方針が明示されています。

なので、最初に実装するなら research paper agentify + Paper Agent Registryまでをおすすめします。ここなら既存のResearch OS思想を壊さず、Paper2Agentの強みをそのまま取り込めます。