#!/usr/bin/env python3
"""Synchronize VERSION.yaml values across context and docs files."""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
VERSION_FILE = ROOT_DIR / "VERSION.yaml"


def load_version() -> dict:
    if not VERSION_FILE.exists():
        print(f"ERROR: {VERSION_FILE} not found")
        sys.exit(1)

    content = VERSION_FILE.read_text(encoding="utf-8")
    data = {}
    for line in content.strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def _update_file(filepath: Path, content: str, original: str, check_only: bool) -> bool:
    if content != original:
        if check_only:
            print(f"FAIL: {filepath.name} needs update")
            return False
        filepath.write_text(content, encoding="utf-8")
        print(f"OK: {filepath.name} updated")
        return True

    print(f"OK: {filepath.name} in sync")
    return True


def sync_agents_md(version_data: dict, check_only: bool = False) -> bool:
    filepath = ROOT_DIR / "AGENTS.md"
    if not filepath.exists():
        print(f"WARN: {filepath.name} not found")
        return True

    content = filepath.read_text(encoding="utf-8")
    original = content
    version = version_data["version"]
    today = datetime.now().strftime("%Y-%m-%d")

    content = re.sub(r"agents_version:\s*[\d.]+", f"agents_version: {version}", content)
    content = re.sub(r"last_update:\s*[\d-]+", f"last_update: {today}", content)
    content = re.sub(r"\*\*Version\*\*\s*\|\s*v?[\d.]+", f"**Version** | v{version}", content)
    content = re.sub(r">\s*\*\*v[\d.]+", f"> **v{version}", content)

    return _update_file(filepath, content, original, check_only)


def sync_cursorrules(version_data: dict, check_only: bool = False) -> bool:
    filepath = ROOT_DIR / ".cursorrules"
    if not filepath.exists():
        print(f"WARN: {filepath.name} not found")
        return True

    content = filepath.read_text(encoding="utf-8")
    original = content
    version = version_data["version"]
    today = datetime.now().strftime("%Y-%m-%d")

    # Legacy + bridge compatible patterns
    content = re.sub(r"cursorrules_version:\s*[\d.]+", f"cursorrules_version: {version}", content)
    content = re.sub(r"last_update:\s*[\d-]+", f"last_update: {today}", content)
    content = re.sub(r"\*\*Version\*\*\s*\|\s*v?[\d.]+", f"**Version** | v{version}", content)
    content = content.replace(".agent/workflows/", ".agents/workflows/")

    return _update_file(filepath, content, original, check_only)


def sync_gemini_md(version_data: dict, check_only: bool = False) -> bool:
    filepath = ROOT_DIR / "GEMINI.md"
    if not filepath.exists():
        print(f"WARN: {filepath.name} not found")
        return True

    content = filepath.read_text(encoding="utf-8")
    original = content
    version = version_data["version"]

    content = re.sub(r"(IA Hoteles Guardian)\s*v?[\d.]+", rf"\1 v{version}", content)

    return _update_file(filepath, content, original, check_only)


def sync_readme(version_data: dict, check_only: bool = False) -> bool:
    filepath = ROOT_DIR / "README.md"
    if not filepath.exists():
        print(f"WARN: {filepath.name} not found")
        return True

    content = filepath.read_text(encoding="utf-8")
    original = content
    version = version_data["version"]

    content = re.sub(r"\*\*Version:\*\*\s*[\d.]+", f"**Version:** {version}", content)
    content = content.replace("skills/README.md", ".agents/workflows/README.md")
    content = content.replace("`skills/`", "`.agents/workflows/`")

    return _update_file(filepath, content, original, check_only)


def sync_gemini_config(version_data: dict, check_only: bool = False) -> bool:
    filepath = ROOT_DIR / ".gemini" / "config.yaml"
    if not filepath.exists():
        print(f"WARN: {filepath.name} not found")
        return True

    content = filepath.read_text(encoding="utf-8")
    original = content
    version = version_data["version"]
    codename = version_data["codename"]

    pattern = r'IA Hoteles Agent\s*\(v[\d.]+\s*"[^"]*"\)'
    replacement = f'IA Hoteles Agent (v{version} "{codename}")'
    content = re.sub(pattern, replacement, content)

    return _update_file(filepath, content, original, check_only)


def sync_indice_documentacion(version_data: dict, check_only: bool = False) -> bool:
    filepath = ROOT_DIR / "INDICE_DOCUMENTACION.md"
    if not filepath.exists():
        print(f"WARN: {filepath.name} not found")
        return True

    content = filepath.read_text(encoding="utf-8")
    original = content
    version = version_data["version"]

    content = re.sub(r"IA Hoteles Agent\s*v?[\d.]+", f"IA Hoteles Agent v{version}", content)
    content = re.sub(r"\*\*Version:\*\*\s*[\d.]+", f"**Version:** {version}", content)

    return _update_file(filepath, content, original, check_only)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync version across context files")
    parser.add_argument("--check", action="store_true", help="Check only")
    args = parser.parse_args()

    print("=" * 60)
    print("VERSION SYNC" + (" (CHECK)" if args.check else ""))
    print("=" * 60)

    version_data = load_version()
    print("Source: VERSION.yaml")
    print(f"  version: {version_data['version']}")
    print(f"  codename: {version_data['codename']}")
    print()

    all_ok = True
    all_ok &= sync_agents_md(version_data, args.check)
    all_ok &= sync_cursorrules(version_data, args.check)
    all_ok &= sync_gemini_md(version_data, args.check)
    all_ok &= sync_readme(version_data, args.check)
    all_ok &= sync_gemini_config(version_data, args.check)
    all_ok &= sync_indice_documentacion(version_data, args.check)

    print()
    print("=" * 60)
    print("All files in sync" if all_ok else "Some files need update")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
