#!/usr/bin/env python3
"""Normalize cache filenames by removing accents and special characters."""

import argparse
import os
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple


def remove_accents(text: str) -> str:
    """Remove accents from text."""
    nfkd_form = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd_form if not unicodedata.combining(c))


def normalize_filename(filename: str) -> str:
    """Normalize filename according to rules."""
    name, ext = os.path.splitext(filename)
    
    name = remove_accents(name)
    name = name.lower()
    name = name.replace(' ', '_')
    name = re.sub(r'[^a-z0-9_.]', '', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    
    return f"{name}{ext.lower()}"


def scan_cache_directory(cache_dir: Path) -> List[Path]:
    """Scan cache directory for JSON files."""
    if not cache_dir.exists():
        return []
    return list(cache_dir.glob('*.json'))


def find_duplicates(files: List[Path]) -> Dict[str, List[Tuple[Path, float]]]:
    """Group files by normalized name with their modification times."""
    groups: Dict[str, List[Tuple[Path, float]]] = {}
    
    for file_path in files:
        normalized = normalize_filename(file_path.name)
        mtime = file_path.stat().st_mtime
        
        if normalized not in groups:
            groups[normalized] = []
        groups[normalized].append((file_path, mtime))
    
    return {k: v for k, v in groups.items() if len(v) > 1 or k != v[0][0].name}


def process_cache(cache_dir: Path, dry_run: bool = False) -> Tuple[int, int, int]:
    """Process cache files and normalize/deduplicate.
    
    Returns:
        Tuple of (files_renamed, files_deleted, files_kept)
    """
    files = scan_cache_directory(cache_dir)
    print(f"Found {len(files)} JSON files in {cache_dir}")
    
    if not files:
        print("No files to process.")
        return 0, 0, 0
    
    groups = find_duplicates(files)
    
    files_renamed = 0
    files_deleted = 0
    files_kept = 0
    
    for normalized_name, file_list in groups.items():
        file_list.sort(key=lambda x: x[1], reverse=True)
        most_recent, most_recent_mtime = file_list[0]
        
        print(f"\nProcessing group for normalized name: {normalized_name}")
        
        for file_path, mtime in file_list:
            print(f"  - {file_path.name} (mtime: {mtime})")
        
        print(f"\n  Keeping: {most_recent.name} (most recent)")
        
        if most_recent.name != normalized_name:
            new_path = most_recent.parent / normalized_name
            print(f"  Renaming: {most_recent.name} -> {normalized_name}")
            if not dry_run:
                most_recent.rename(new_path)
            files_renamed += 1
        else:
            print(f"  No rename needed (already normalized)")
        
        files_kept += 1
        
        for file_path, mtime in file_list[1:]:
            print(f"  Deleting duplicate: {file_path.name}")
            if not dry_run:
                file_path.unlink()
            files_deleted += 1
    
    return files_renamed, files_deleted, files_kept


def main():
    parser = argparse.ArgumentParser(
        description='Normalize cache filenames and remove duplicates'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without making them'
    )
    parser.add_argument(
        '--cache-dir',
        type=Path,
        default=None,
        help='Path to cache directory (default: data/cache/)'
    )
    
    args = parser.parse_args()
    
    if args.cache_dir:
        cache_dir = args.cache_dir
    else:
        script_dir = Path(__file__).parent
        cache_dir = script_dir.parent / 'data' / 'cache'
    
    print(f"Cache directory: {cache_dir}")
    print(f"Dry run: {args.dry_run}")
    print("-" * 50)
    
    renamed, deleted, kept = process_cache(cache_dir, dry_run=args.dry_run)
    
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  Files renamed: {renamed}")
    print(f"  Files deleted: {deleted}")
    print(f"  Files kept: {kept}")
    
    if args.dry_run:
        print("\n(Dry run - no changes were made)")


if __name__ == '__main__':
    main()
