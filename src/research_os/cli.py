"""コマンドラインの入口。"""

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

from research_os import __version__
from research_os.data import interests, profile, venues


def _cmd_venues(args: argparse.Namespace) -> int:
    registry = venues.load_venues(args.registry)
    prof = profile.load_profile(args.profile)
    for v in profile.effective_venues(registry, prof):
        priority = "-" if v.priority is None else str(v.priority)
        print(f"{priority:>2}  {v.fit}  {v.label:<20} {v.type:<10} {v.tier or ''}")
    return 0


def _cmd_interests_init(args: argparse.Namespace) -> int:
    prof = profile.load_profile(args.profile)
    path = interests.write_interests(interests.generate_interests(prof), args.out, force=args.force)
    print(f"wrote {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="research-os", description="Research OS")
    parser.add_argument("--version", action="version", version=f"research-os {__version__}")
    parser.add_argument("--registry", type=Path, default=venues.DEFAULT_PATH)
    parser.add_argument("--profile", type=Path, default=profile.DEFAULT_PATH)
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("venues", help="研究プロファイルを適用した Venue 一覧を優先度順に表示")
    p.set_defaults(func=_cmd_venues)

    p = sub.add_parser("interests", help="関心プロファイル interests.yaml の操作")
    isub = p.add_subparsers(dest="interests_command", required=True)
    p = isub.add_parser("init", help="research/profile.yaml から interests.yaml を生成")
    p.add_argument("--out", type=Path, default=interests.DEFAULT_PATH)
    p.add_argument("--force", action="store_true", help="既存ファイルを上書きする")
    p.set_defaults(func=_cmd_interests_init)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not hasattr(args, "func"):
        return 0
    try:
        return args.func(args)
    except (ValidationError, ValueError, FileExistsError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
