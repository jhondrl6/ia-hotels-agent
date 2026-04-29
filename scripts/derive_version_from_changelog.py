#!/usr/bin/env python3
"""Derive VERSION.yaml from CHANGELOG.md latest entry."""
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
CHANGELOG = ROOT_DIR / "CHANGELOG.md"
VERSION = ROOT_DIR / "VERSION.yaml"

# Fix Windows encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def extract_latest_version(path: Path) -> str | None:
    """Extract latest version from CHANGELOG.md (first entry)."""
    content = path.read_text(encoding="utf-8")
    match = re.search(r'^##\s+\[v?(\d+\.\d+\.\d+)\]', content, re.MULTILINE)
    return match.group(1) if match else None


def update_version_yaml(yaml_path: Path, new_version: str) -> None:
    """Update version field in VERSION.yaml, preserving rest of YAML."""
    lines = yaml_path.read_text(encoding="utf-8").splitlines()
    new_lines = []
    for line in lines:
        if line.strip().startswith("version:"):
            new_lines.append(f'version: "{new_version}"')
        else:
            new_lines.append(line)
    yaml_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def main() -> int:
    ver = extract_latest_version(CHANGELOG)
    if not ver:
        print("ERROR: No version found in CHANGELOG.md")
        return 1
    update_version_yaml(VERSION, ver)
    print(f"VERSION.yaml → {ver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
