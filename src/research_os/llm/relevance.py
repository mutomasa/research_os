"""関連度の段階 2：Claude Code（claude -p）による判定。

仕様: docs/new_features/paper_intake.md §4.1
段階 1（語の一致）の上位だけを判定し、結果は llm_relevance に RQ 定義のハッシュつきで保存する。
"""

import hashlib
import json
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from research_os.data.papers import PaperStore
from research_os.data.profile import ResearchProfile

ABSTRACT_CHARS = 1500
TIMEOUT = 300

SYSTEM_PROMPT = (
    "あなたはロボティクス分野の研究者で、先行研究の候補を研究課題（RQ）ごとに仕分ける。"
    "与えられた題名と要旨だけで判断し、推測で関連度を上げない。"
)

GUIDE = """各論文について、各 RQ の先行研究としての関連度を 0〜1 で付けてください。
- 1.0: その RQ の問いそのものを、ロボットの操作（マニピュレーション）の文脈で扱っている
- 0.7: 手法か対象のどちらかが RQ と直接重なり、比較対象や引用候補になる
- 0.4: 関連する手法を別の対象（自動運転・ナビゲーションなど）で扱っている
- 0.1: "world model" や "learning" のような一般的な語が共通するだけ
- 0.0: 無関係
reason は最も関連の高い RQ について、なぜその値かを日本語 1 文で書いてください。"""

# (prompt, json_schema, model) → structured_output
Runner = Callable[[str, dict, str], dict]


class JudgeError(RuntimeError):
    pass


@dataclass
class JudgeReport:
    judged: int = 0
    calls: int = 0
    error: str | None = None


def profile_hash(profile: ResearchProfile) -> str:
    """RQ の定義が変わったら判定し直すためのハッシュ。"""
    spec = [profile.theme] + [
        [rq.id, rq.title, rq.question, rq.survey_topics, rq.exclude_topics] for rq in profile.research_questions
    ]
    return hashlib.sha256(json.dumps(spec, ensure_ascii=False).encode()).hexdigest()[:12]


def schema(profile: ResearchProfile) -> dict:
    rq_ids = [rq.id for rq in profile.research_questions]
    score = {"type": "number", "minimum": 0, "maximum": 1}
    return {
        "type": "object",
        "properties": {
            "papers": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                        "relevance": {
                            "type": "object",
                            "properties": {rq: score for rq in rq_ids},
                            "required": rq_ids,
                        },
                        "reason": {"type": "string"},
                    },
                    "required": ["key", "relevance", "reason"],
                },
            }
        },
        "required": ["papers"],
    }


def build_prompt(profile: ResearchProfile, papers: dict[str, dict]) -> str:
    lines = [f"研究テーマ: {profile.theme}", "", "RQ:"]
    for rq in profile.research_questions:
        lines.append(f"- {rq.id} {rq.title}: {rq.question}（キーワード: {', '.join(rq.survey_topics)}）")
    lines += ["", "論文:"]
    for key, row in papers.items():
        meta = ", ".join(str(x) for x in (row["year"], row["venue_name"]) if x)
        lines.append(f"[{key}] {row['title']}" + (f" ({meta})" if meta else ""))
        lines.append((row["abstract"] or "（要旨なし）")[:ABSTRACT_CHARS])
        lines.append("")
    lines.append(GUIDE)
    return "\n".join(lines)


def claude_cli_run(prompt: str, json_schema: dict, model: str) -> dict:
    """claude -p をツールなし・MCP なし・セッション保存なしで呼び、構造化出力を返す。"""
    exe = shutil.which("claude")
    if not exe:
        raise JudgeError("claude コマンドが見つかりません")
    cmd = [exe, "-p", "--output-format", "json", "--tools", "", "--strict-mcp-config",
           "--no-session-persistence", "--model", model, "--system-prompt", SYSTEM_PROMPT,
           "--json-schema", json.dumps(json_schema)]
    try:
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired as e:
        raise JudgeError(f"claude -p が {TIMEOUT} 秒で終わりませんでした") from e
    if proc.returncode != 0:
        raise JudgeError(f"claude -p が終了コード {proc.returncode} で失敗しました: {proc.stderr.strip()[:300]}")
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise JudgeError(f"claude -p の出力が JSON ではありません: {proc.stdout[:300]}") from e
    if out.get("is_error") or not isinstance(out.get("structured_output"), dict):
        raise JudgeError(f"claude -p が構造化出力を返しませんでした: {str(out.get('result'))[:300]}")
    return out["structured_output"]


def judge(store: PaperStore, profile: ResearchProfile, now: datetime, runner: Runner | None = None) -> JudgeReport:
    """まだ判定のない candidate を段階 1 のスコア順に llm_top_k 件まで判定する。"""
    runner = runner or claude_cli_run
    cfg = profile.intake
    h = profile_hash(profile)
    report = JudgeReport()
    rows = [r for r in store.papers("candidate") if store.llm_relevance(r["paper_id"], h) is None][:cfg.llm_top_k]
    for i in range(0, len(rows), cfg.llm_batch):
        batch = {f"P{j + 1}": row for j, row in enumerate(rows[i:i + cfg.llm_batch])}
        try:
            out = runner(build_prompt(profile, batch), schema(profile), cfg.llm_model)
        except JudgeError as e:
            report.error = str(e)
            break
        report.calls += 1
        for item in out.get("papers", []):
            row = batch.get(item.get("key"))
            if row is None:
                continue
            rel = {rq.id: min(1.0, max(0.0, float(item["relevance"].get(rq.id, 0.0))))
                   for rq in profile.research_questions}
            store.set_llm_relevance(row["paper_id"], rel, item.get("reason", ""), h, now)
            report.judged += 1
        store.commit()
    return report
