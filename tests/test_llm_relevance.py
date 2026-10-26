import json
import subprocess
from datetime import datetime

import pytest

import research_os.llm.relevance as rel
from research_os.data import intake
from research_os.data.papers import PaperRecord, PaperStore
from research_os.data.profile import load_profile
from research_os.data.venues import load_venues

NOW = datetime(2026, 10, 27, 9, 0)

# 要旨に RQ2 の語句が 2 つ出るので、段階 1 ではどれも RQ2 の関連度が 1.00 に張り付く（#9 の再現）
ABSTRACT = "We learn latent dynamics with world models."
TITLES = [
    "JEPA world models for robotic grasp failure prediction",
    "LidarDM: generative LiDAR world models for driving",
    "Latent dynamics world models for urban traffic",
]


class FakeRunner:
    def __init__(self, scores=None, fail_on=None):
        self.calls = []
        self.scores = scores or {}
        self.fail_on = fail_on

    def __call__(self, prompt, json_schema, model):
        self.calls.append((prompt, json_schema, model))
        if self.fail_on is not None and len(self.calls) == self.fail_on:
            raise rel.JudgeError("boom")
        papers = []
        for line in prompt.splitlines():
            if line.startswith("[P"):
                key, title = line[1:].split("] ", 1)
                r2 = self.scores.get(title.split(" (")[0], 0.1)
                papers.append({"key": key, "relevance": {"RQ1": 0.0, "RQ2": r2, "RQ3": 0.0}, "reason": f"理由 {title}"})
        return {"papers": papers}


@pytest.fixture
def ctx(root):
    store = PaperStore(":memory:")
    registry = load_venues(root / "registry/venues.yaml")
    profile = load_profile(root / "research/profile.yaml")
    for i, t in enumerate(TITLES):
        store.upsert(PaperRecord(title=t, doi=f"10.9/{i}", abstract=ABSTRACT, year=2025, venue_id="ral", cited_by_count=10),
                     "openalex", None, None, NOW)
    intake.rescore(store, registry, profile, NOW)
    yield store, registry, profile
    store.close()


def _score(store, title):
    row = next(r for r in store.papers() if r["title"] == title)
    return row["score"], json.loads(row["breakdown"])


def test_llm_relevance_replaces_keyword_relevance(ctx):
    store, registry, profile = ctx
    _, before = _score(store, TITLES[1])
    assert before["relevance"] == 1.0 and before["relevance_source"] == "keyword"

    runner = FakeRunner({TITLES[0]: 0.95, TITLES[1]: 0.05, TITLES[2]: 0.05})
    report = rel.judge(store, profile, NOW, runner)
    assert (report.judged, report.calls, report.error) == (3, 1, None)
    assert runner.calls[0][2] == "sonnet"

    intake.rescore(store, registry, profile, NOW)
    good, good_parts = _score(store, TITLES[0])
    bad, bad_parts = _score(store, TITLES[1])
    assert bad_parts["relevance"] == 0.05 and bad_parts["relevance_source"] == "llm"
    assert bad_parts["llm_reason"].startswith("理由 LidarDM")
    assert good > bad
    # 投稿先・手薄さの加点だけで min_score は超えるが、関連度の下限で Inbox には出ない
    assert bad > profile.intake.min_score
    surfaced = intake.surface(store, profile, NOW).surfaced
    assert [p for p in surfaced if "10.9/1" in p] == []


def test_judgment_is_cached_until_rqs_change(ctx):
    store, _, profile = ctx
    rel.judge(store, profile, NOW, FakeRunner())
    again = FakeRunner()
    assert rel.judge(store, profile, NOW, again).calls == 0

    changed = profile.model_copy(deep=True)
    changed.research_questions[1].question += "（改訂）"
    assert rel.profile_hash(changed) != rel.profile_hash(profile)
    assert rel.judge(store, changed, NOW, again).judged == 3


def test_top_k_and_batches(ctx):
    store, _, profile = ctx
    cfg = profile.model_copy(deep=True)
    cfg.intake.llm_top_k, cfg.intake.llm_batch = 3, 2
    runner = FakeRunner()
    assert rel.judge(store, cfg, NOW, runner).calls == 2

    store2 = PaperStore(":memory:")
    for i in range(5):
        store2.upsert(PaperRecord(title=f"JEPA world models {i}", doi=f"10.8/{i}"), "openalex", None, None, NOW)
    cfg.intake.llm_top_k = 2
    assert rel.judge(store2, cfg, NOW, FakeRunner()).judged == 2


def test_runner_failure_keeps_keyword_scores(ctx):
    store, registry, profile = ctx
    cfg = profile.model_copy(deep=True)
    cfg.intake.llm_batch = 1
    report = rel.judge(store, cfg, NOW, FakeRunner(fail_on=2))
    assert (report.judged, report.error) == (1, "boom")
    intake.rescore(store, registry, cfg, NOW)
    sources = {json.loads(r["breakdown"])["relevance_source"] for r in store.papers()}
    assert sources == {"llm", "keyword"}


def test_exclude_topics_still_apply_after_llm(ctx):
    store, registry, profile = ctx
    cfg = profile.model_copy(deep=True)
    cfg.research_questions[1].exclude_topics = ["LiDAR"]
    rel.judge(store, cfg, NOW, FakeRunner({TITLES[1]: 0.9}))
    intake.rescore(store, registry, cfg, NOW)
    assert _score(store, TITLES[1])[1]["relevance"] < 0.9


def test_claude_cli_run_flags_and_parsing(monkeypatch):
    seen = {}

    def fake_run(cmd, input, capture_output, text, timeout):
        seen["cmd"], seen["input"] = cmd, input
        out = {"type": "result", "is_error": False, "result": "", "structured_output": {"papers": []}}
        return subprocess.CompletedProcess(cmd, 0, json.dumps(out), "")

    monkeypatch.setattr(rel.shutil, "which", lambda name: "/usr/bin/claude")
    monkeypatch.setattr(rel.subprocess, "run", fake_run)
    assert rel.claude_cli_run("PROMPT", {"type": "object"}, "sonnet") == {"papers": []}
    cmd = seen["cmd"]
    assert cmd[:2] == ["/usr/bin/claude", "-p"] and seen["input"] == "PROMPT"
    assert cmd[cmd.index("--tools") + 1] == ""  # ツールは使わせない
    assert "--strict-mcp-config" in cmd and "--no-session-persistence" in cmd
    assert json.loads(cmd[cmd.index("--json-schema") + 1]) == {"type": "object"}


@pytest.mark.parametrize("returncode, stdout, message", [
    (1, "", "終了コード 1"),
    (0, "not json", "JSON ではありません"),
    (0, json.dumps({"is_error": True, "result": "limit"}), "構造化出力"),
])
def test_claude_cli_run_errors(monkeypatch, returncode, stdout, message):
    monkeypatch.setattr(rel.shutil, "which", lambda name: "/usr/bin/claude")
    monkeypatch.setattr(rel.subprocess, "run",
                        lambda cmd, **k: subprocess.CompletedProcess(cmd, returncode, stdout, "err"))
    with pytest.raises(rel.JudgeError, match=message):
        rel.claude_cli_run("p", {}, "sonnet")


def test_missing_claude_command(monkeypatch):
    monkeypatch.setattr(rel.shutil, "which", lambda name: None)
    with pytest.raises(rel.JudgeError, match="見つかりません"):
        rel.claude_cli_run("p", {}, "sonnet")


def test_judged_only_skips_unjudged_candidates(ctx):
    store, registry, profile = ctx
    cfg = profile.model_copy(deep=True)
    cfg.intake.llm_top_k = 1
    rel.judge(store, cfg, NOW, FakeRunner({TITLES[0]: 0.7}))
    intake.rescore(store, registry, cfg, NOW)
    # 未判定の 2 本は段階 1 の 1.00 のままスコアが上だが、judged_only では出ない
    assert intake.surface(store, cfg, NOW, judged_only=True).surfaced == ["doi:10.9/0"]
