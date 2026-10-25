"""コマンドラインの入口。"""

import argparse

from research_os import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="research-os", description="Research OS")
    parser.add_argument("--version", action="version", version=f"research-os {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)
    return 0
