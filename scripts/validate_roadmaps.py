#!/usr/bin/env python3
"""Validate roadmap markdown files for required metadata fields.

Checks each H3 roadmap item in `roadmap/*.md` (excluding README and _template)
contains the baseline fields defined in CLAUDE.md.
"""

from __future__ import annotations

import re
from pathlib import Path

REQUIRED_FIELDS = [
    "Status",
    "Owner",
    "Quarter",
    "Priority",
    "Tags",
]

ITEM_HEADING = re.compile(r"^###\s+.+")
FIELD_LINE = re.compile(r"^-\s+\*\*(?P<field>[^*]+):\*\*\s+.+")


def discover_roadmap_files(root: Path) -> list[Path]:
    roadmap_dir = root / "roadmap"
    candidates = sorted(roadmap_dir.glob("*.md"))
    return [
        path
        for path in candidates
        if path.name not in {"README.md", "_template.md"}
    ]


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    current_item: str | None = None
    fields: set[str] = set()

    lines = path.read_text(encoding="utf-8").splitlines()

    def flush_item() -> None:
        nonlocal current_item, fields
        if not current_item:
            return
        missing = [field for field in REQUIRED_FIELDS if field not in fields]
        if missing:
            errors.append(
                f"{path}: item '{current_item}' is missing fields: {', '.join(missing)}"
            )

    for line in lines:
        if ITEM_HEADING.match(line):
            flush_item()
            current_item = line.replace("###", "", 1).strip()
            fields = set()
            continue

        if current_item:
            match = FIELD_LINE.match(line)
            if match:
                fields.add(match.group("field").strip())

    flush_item()
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    files = discover_roadmap_files(root)
    if not files:
        print("No roadmap files found to validate.")
        return 0

    all_errors: list[str] = []
    for file in files:
        all_errors.extend(validate_file(file))

    if all_errors:
        print("Roadmap validation failed:")
        for error in all_errors:
            print(f"- {error}")
        return 1

    print(f"Validated {len(files)} roadmap file(s): all required fields present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
