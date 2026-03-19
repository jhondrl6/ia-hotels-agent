"""Consolidate and archive session files."""

import argparse
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict


SESSIONS_DIR = Path(".agent/memory/sessions")
ARCHIVES_DIR = Path(".agent/memory/archives/sessions")
LEGACY_FILE = Path(".agent/memory/execution_history.jsonl")
MAX_ACTIVE_SESSIONS = 5
ARCHIVE_AFTER_DAYS = 30


def parse_session_date(filename: str) -> str | None:
    if len(filename) >= 10:
        return filename[:10]
    return None


def load_session_file(filepath: Path) -> dict | None:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_session_file(filepath: Path, data: dict, dry_run: bool) -> None:
    if dry_run:
        print(f"   - Would write: {filepath}")
        return
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"   - Written: {filepath}")


def consolidate_sessions(sessions_dir: Path, dry_run: bool) -> tuple[list[Path], list[Path]]:
    session_files = sorted(sessions_dir.glob("*.json"))
    by_date: dict[str, list[tuple[Path, dict]]] = defaultdict(list)

    for filepath in session_files:
        date = parse_session_date(filepath.stem)
        if not date:
            continue
        data = load_session_file(filepath)
        if data:
            by_date[date].append((filepath, data))

    created: list[Path] = []
    deleted: list[Path] = []

    for date, files in by_date.items():
        if len(files) <= 1:
            continue

        print(f"Consolidating {len(files)} sessions for {date}")

        all_entries = []
        most_recent_updated = ""
        for filepath, data in files:
            entries = data.get("entries", [])
            all_entries.extend(entries)
            updated = data.get("updated_at", "")
            if updated > most_recent_updated:
                most_recent_updated = updated
            deleted.append(filepath)
            if not dry_run:
                print(f"   - Merging: {filepath.name}")

        consolidated = {
            "session_id": f"{date}_consolidated",
            "entries": all_entries,
            "updated_at": most_recent_updated
        }

        new_path = sessions_dir / f"{date}_consolidated.json"
        save_session_file(new_path, consolidated, dry_run)
        created.append(new_path)

    return created, deleted


def archive_old_sessions(sessions_dir: Path, archives_dir: Path, dry_run: bool) -> list[Path]:
    cutoff = datetime.now() - timedelta(days=ARCHIVE_AFTER_DAYS)
    session_files = sorted(sessions_dir.glob("*.json"))
    archived: list[Path] = []

    for filepath in session_files:
        date_str = parse_session_date(filepath.stem)
        if not date_str:
            continue
        try:
            session_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue

        if session_date < cutoff:
            print(f"Archiving old session: {filepath.name}")
            dest = archives_dir / filepath.name
            if dry_run:
                print(f"   - Would move to: {dest}")
            else:
                archives_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(filepath), str(dest))
                print(f"   - Moved to: {dest}")
            archived.append(filepath)

    return archived


def enforce_max_sessions(sessions_dir: Path, archives_dir: Path, dry_run: bool) -> list[Path]:
    session_files = sorted(sessions_dir.glob("*.json"), key=lambda p: p.stem[:10], reverse=True)
    archived: list[Path] = []

    if len(session_files) <= MAX_ACTIVE_SESSIONS:
        return archived

    to_archive = session_files[MAX_ACTIVE_SESSIONS:]
    print(f"Enforcing max {MAX_ACTIVE_SESSIONS} active sessions")

    for filepath in to_archive:
        print(f"Archiving excess session: {filepath.name}")
        dest = archives_dir / filepath.name
        if dry_run:
            print(f"   - Would move to: {dest}")
        else:
            archives_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(filepath), str(dest))
            print(f"   - Moved to: {dest}")
        archived.append(filepath)

    return archived


def delete_legacy_file(base_dir: Path, dry_run: bool) -> bool:
    legacy_path = base_dir / LEGACY_FILE
    if not legacy_path.exists():
        return False

    print(f"Deleting legacy file: {legacy_path}")
    if dry_run:
        print("   - Would delete")
    else:
        legacy_path.unlink()
        print("   - Deleted")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Cleanup and consolidate session files")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without making them")
    args = parser.parse_args()

    base_dir = Path(args.root).resolve()
    sessions_dir = base_dir / SESSIONS_DIR
    archives_dir = base_dir / ARCHIVES_DIR
    dry_run = args.dry_run

    if dry_run:
        print("=== DRY RUN MODE - No changes will be made ===\n")

    stats = {
        "consolidated_created": 0,
        "consolidated_deleted": 0,
        "archived": 0,
        "legacy_deleted": False
    }

    if sessions_dir.exists():
        print("Step 1: Consolidating sessions by date...")
        created, deleted = consolidate_sessions(sessions_dir, dry_run)
        stats["consolidated_created"] = len(created)
        stats["consolidated_deleted"] = len(deleted)

        print("\nStep 2: Archiving sessions older than 30 days...")
        archived = archive_old_sessions(sessions_dir, archives_dir, dry_run)
        stats["archived"] += len(archived)

        print("\nStep 3: Enforcing max active sessions...")
        archived = enforce_max_sessions(sessions_dir, archives_dir, dry_run)
        stats["archived"] += len(archived)
    else:
        print(f"Sessions directory not found: {sessions_dir}")

    print("\nStep 4: Deleting legacy file...")
    stats["legacy_deleted"] = delete_legacy_file(base_dir, dry_run)

    print("\n=== SUMMARY ===")
    print(f"Consolidated files created: {stats['consolidated_created']}")
    print(f"Session files merged/deleted: {stats['consolidated_deleted']}")
    print(f"Sessions archived: {stats['archived']}")
    print(f"Legacy file deleted: {stats['legacy_deleted']}")

    if dry_run:
        print("\n(Dry run - no actual changes made)")


if __name__ == "__main__":
    main()
