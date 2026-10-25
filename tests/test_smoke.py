import research_os
from research_os.cli import main


def test_version():
    assert research_os.__version__ == "0.1.0"


def test_cli_without_args_exits_cleanly():
    assert main([]) == 0
