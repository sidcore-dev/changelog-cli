"""Command-line entry point for changelog-cli."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

from .core import render_changelog


class GitError(RuntimeError):
    """Raised when a git command fails or git/the repo is unavailable."""


def _run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise GitError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def check_git_available() -> None:
    if shutil.which("git") is None:
        raise GitError("git is not installed or not on PATH")


def check_inside_repo() -> None:
    try:
        _run_git(["rev-parse", "--is-inside-work-tree"])
    except GitError as exc:
        raise GitError("not a git repository (or any parent up to the mount point)") from exc


def latest_tag() -> str | None:
    """Return the most recent tag reachable from HEAD, or None if there isn't one."""
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    tag = result.stdout.strip()
    return tag or None


def commit_subjects(from_ref: str | None, to_ref: str) -> list[str]:
    """Fetch commit subject lines between from_ref (exclusive) and to_ref."""
    range_arg = f"{from_ref}..{to_ref}" if from_ref else to_ref
    output = _run_git(["log", range_arg, "--pretty=format:%s"])
    if not output:
        return []
    return output.split("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="changelog-cli",
        description="Generate a Markdown changelog from git commit history between two refs.",
    )
    parser.add_argument("--from", dest="from_ref", default=None, help="Starting ref (default: most recent tag, if any)")
    parser.add_argument("--to", dest="to_ref", default="HEAD", help="Ending ref (default: HEAD)")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        check_git_available()
    except GitError as exc:
        print(f"changelog-cli: error: {exc}", file=sys.stderr)
        return 2

    try:
        check_inside_repo()
    except GitError as exc:
        print(f"changelog-cli: error: {exc}", file=sys.stderr)
        return 1

    from_ref = args.from_ref
    if from_ref is None:
        from_ref = latest_tag()

    try:
        subjects = commit_subjects(from_ref, args.to_ref)
    except GitError as exc:
        print(f"changelog-cli: error: {exc}", file=sys.stderr)
        return 1

    print(render_changelog(subjects, from_ref, args.to_ref), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
