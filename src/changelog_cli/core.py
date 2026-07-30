"""Core changelog grouping and rendering logic for changelog-cli.

Pure text processing only — no subprocess calls or filesystem access.
The CLI layer is responsible for gathering commit subjects via `git
log` and handing them to `render_changelog`.
"""
from __future__ import annotations

import re

CONVENTIONAL_TYPES = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "perf": "Performance Improvements",
    "refactor": "Code Refactoring",
    "docs": "Documentation",
    "style": "Styles",
    "test": "Tests",
    "build": "Build System",
    "ci": "Continuous Integration",
    "chore": "Chores",
    "revert": "Reverts",
}

CATEGORY_ORDER = [
    "Features",
    "Bug Fixes",
    "Performance Improvements",
    "Code Refactoring",
    "Documentation",
    "Styles",
    "Tests",
    "Build System",
    "Continuous Integration",
    "Chores",
    "Reverts",
    "Other",
]

_SUBJECT_RE = re.compile(r"^([a-zA-Z]+)(\([^)]*\))?!?:\s*(.+)$")


def parse_subject(subject: str) -> tuple[str, str]:
    """Split a commit subject into (category label, description).

    Recognizes Conventional Commits prefixes like `feat:`, `fix(scope):`,
    or `feat!:`. Anything that doesn't match a known type falls under
    "Other" with the original subject preserved as the description.
    """
    match = _SUBJECT_RE.match(subject.strip())
    if match:
        type_key = match.group(1).lower()
        description = match.group(3).strip()
        if type_key in CONVENTIONAL_TYPES and description:
            return CONVENTIONAL_TYPES[type_key], description
    return "Other", subject.strip()


def group_commits(subjects: list[str]) -> dict[str, list[str]]:
    """Group commit subjects by their Conventional Commits category."""
    groups: dict[str, list[str]] = {}
    for subject in subjects:
        if not subject.strip():
            continue
        label, description = parse_subject(subject)
        groups.setdefault(label, []).append(description)
    return groups


def render_changelog(subjects: list[str], from_ref: str | None, to_ref: str) -> str:
    """Render a Markdown changelog section for the given commit subjects."""
    groups = group_commits(subjects)

    if from_ref:
        header = f"## Changes from {from_ref} to {to_ref}"
    else:
        header = f"## Changes through {to_ref}"

    lines = [header, ""]

    if not groups:
        lines.append("No commits found.")
        return "\n".join(lines).rstrip("\n") + "\n"

    for label in CATEGORY_ORDER:
        if label not in groups:
            continue
        lines.append(f"### {label}")
        lines.append("")
        for description in groups[label]:
            lines.append(f"- {description}")
        lines.append("")

    return "\n".join(lines).rstrip("\n") + "\n"
