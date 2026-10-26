"""テスト失敗時に logs/pytest/<日時>-failures.log へ生のログを残す（CLAUDE.md「テストとログ」）。"""

import os
import platform
import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_failures: list[pytest.TestReport] = []


@pytest.fixture
def root() -> Path:
    return ROOT


@pytest.fixture(autouse=True)
def no_real_claude(monkeypatch):
    """テストから本物の claude -p を呼ばない（契約の利用枠を使うため）。必要なテストは上書きする。"""
    import research_os.llm.relevance as rel

    def refuse(*a, **k):
        raise AssertionError("test tried to run the real claude -p")

    monkeypatch.setattr(rel.subprocess, "run", refuse)


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.failed:
        _failures.append(report)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    if not _failures:
        return
    log_dir = ROOT / "logs" / "pytest"
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = log_dir / f"{stamp}-{len(_failures)}-failures.log"
    lines = [
        f"command: {' '.join(sys.argv)}",
        f"cwd: {os.getcwd()}",
        f"python: {sys.version}",
        f"platform: {platform.platform()}",
        f"exitstatus: {exitstatus}",
        "",
    ]
    for r in _failures:
        lines += [f"=== {r.nodeid} ({r.when}) ===", r.longreprtext]
        for name, content in r.sections:
            lines += [f"--- {name} ---", content]
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
