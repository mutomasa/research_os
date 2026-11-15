import tomllib
from pathlib import Path

import research_os
from research_os.cli import main


def test_version_matches_pyproject():
    # ヘッダ右上に出す版（DESIGN.md §5.1）が pyproject.toml とずれないようにする
    pyproject = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text())
    assert research_os.__version__ == pyproject["project"]["version"]


def test_cli_without_args_exits_cleanly():
    assert main([]) == 0
