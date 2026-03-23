#!/usr/bin/env python3
"""
Synchronize VERSION.yaml values across context and docs files.

This script is CONFIG-DRIVEN - sync rules are defined in sync_config.yaml.
To add/modify sync behavior, edit the config file, not this script.

Usage:
    python sync_versions.py              # Sync all files
    python sync_versions.py --check       # Check if sync needed
    python sync_versions.py --list        # List all sync rules
    python sync_versions.py --rule <id>   # Sync specific rule only
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import yaml

ROOT_DIR = Path(__file__).parent.parent
VERSION_FILE = ROOT_DIR / "VERSION.yaml"
CONFIG_FILE = ROOT_DIR / "scripts" / "sync_config.yaml"


class SyncEngine:
    """Config-driven synchronization engine."""
    
    def __init__(self, config_path: Path):
        self.config = self._load_config(config_path)
        self.version_data = self._load_version()
        self.results: Dict[str, str] = {}  # rule_id -> status
    
    def _load_config(self, path: Path) -> dict:
        """Load sync configuration from YAML."""
        if not path.exists():
            print(f"ERROR: Config file not found: {path}")
            sys.exit(1)
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    
    def _load_version(self) -> dict:
        """Load version data from VERSION.yaml."""
        if not VERSION_FILE.exists():
            print(f"ERROR: Version file not found: {VERSION_FILE}")
            sys.exit(1)
        
        data = {}
        for line in VERSION_FILE.read_text(encoding="utf-8").strip().splitlines():
            if ":" in line and not line.strip().startswith("#"):
                key, value = line.split(":", 1)
                data[key.strip()] = value.strip().strip('"').strip("'")
        
        # Add today's date if not present
        if "date" not in data:
            data["date"] = datetime.now().strftime("%Y-%m-%d")
        elif data.get("date") == "today":
            data["date"] = datetime.now().strftime("%Y-%m-%d")
        
        return data
    
    def _interpolate(self, template: str) -> str:
        """Interpolate template with version data."""
        result = template
        
        # Handle date transformations if {date_text} is in template
        if "{date_text}" in template:
            date_val = self.version_data.get("date", "")
            try:
                dt = datetime.strptime(date_val, "%Y-%m-%d")
                meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                date_text = f"{dt.day} {meses[dt.month]} {dt.year}"
                result = result.replace("{date_text}", date_text)
            except ValueError:
                result = result.replace("{date_text}", date_val)
        
        # Interpolate other variables
        for key, value in self.version_data.items():
            if key != "date":  # date already processed
                result = result.replace(f"{{{key}}}", str(value))
        
        return result
    
    def _apply_replacements(self, content: str, replacements: List[dict]) -> tuple:
        """Apply all replacements to content. Returns (new_content, changed)."""
        original = content
        for repl in replacements:
            pattern = repl.get("pattern")
            template = repl.get("template", "")
            multiline = repl.get("multiline", False)
            
            if multiline:
                flags = re.MULTILINE | re.DOTALL
            else:
                flags = re.MULTILINE
            
            interpolated = self._interpolate(template)
            content = re.sub(pattern, interpolated, content, flags=flags)
        
        return content, content != original
    
    def sync_rule(self, rule_id: str, check_only: bool = False) -> bool:
        """Sync a specific rule by ID."""
        rule = None
        for r in self.config.get("rules", []):
            if r.get("id") == rule_id:
                rule = r
                break
        
        if not rule:
            print(f"WARN: Rule '{rule_id}' not found")
            return False
        
        filepath = ROOT_DIR / rule["file"]
        if not filepath.exists():
            print(f"WARN: File not found: {filepath}")
            self.results[rule_id] = "SKIP"
            return True
        
        content = filepath.read_text(encoding="utf-8")
        original = content
        
        content, changed = self._apply_replacements(content, rule.get("replacements", []))
        
        if not changed:
            self.results[rule_id] = "SYNC"
            print(f"OK: {rule['file']} ({rule_id}) - in sync")
            return True
        
        if check_only:
            self.results[rule_id] = "FAIL"
            print(f"FAIL: {rule['file']} ({rule_id}) - needs update")
            return False
        
        filepath.write_text(content, encoding="utf-8")
        self.results[rule_id] = "UPDATED"
        print(f"OK: {rule['file']} ({rule_id}) - updated")
        return True
    
    def sync_all(self, check_only: bool = False) -> bool:
        """Sync all rules defined in config."""
        all_ok = True
        for rule in self.config.get("rules", []):
            ok = self.sync_rule(rule["id"], check_only)
            all_ok = all_ok and ok
        return all_ok
    
    def list_rules(self):
        """List all sync rules."""
        print(f"\nSync Rules (config version {self.config.get('version')}):")
        print("=" * 60)
        for rule in self.config.get("rules", []):
            print(f"\n  [{rule['id']}]")
            print(f"    File: {rule['file']}")
            print(f"    Desc: {rule.get('description', 'N/A')}")
            print(f"    Replacements: {len(rule.get('replacements', []))}")
    
    def validate_config(self) -> bool:
        """Validate sync config structure."""
        errors = []
        
        if "rules" not in self.config:
            errors.append("Missing 'rules' key in config")
        
        for i, rule in enumerate(self.config.get("rules", [])):
            if "id" not in rule:
                errors.append(f"Rule {i}: missing 'id'")
            if "file" not in rule:
                errors.append(f"Rule {i}: missing 'file'")
            if "replacements" not in rule:
                errors.append(f"Rule {rule.get('id', i)}: missing 'replacements'")
            else:
                for j, repl in enumerate(rule.get("replacements", [])):
                    if "pattern" not in repl:
                        errors.append(f"Rule {rule.get('id', i)}: replacement {j} missing 'pattern'")
        
        if errors:
            print("Config validation errors:")
            for err in errors:
                print(f"  - {err}")
            return False
        
        print("Config validation: OK")
        return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync version across context files (config-driven)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--check", action="store_true", help="Check only, don't write")
    parser.add_argument("--list", action="store_true", help="List all sync rules")
    parser.add_argument("--validate", action="store_true", help="Validate config only")
    parser.add_argument("--rule", type=str, help="Sync specific rule ID only")
    args = parser.parse_args()
    
    engine = SyncEngine(CONFIG_FILE)
    
    if args.validate:
        return 0 if engine.validate_config() else 1
    
    if args.list:
        engine.list_rules()
        return 0
    
    print("=" * 60)
    print("VERSION SYNC" + (" (CHECK)" if args.check else ""))
    print("=" * 60)
    print(f"\nSource: {VERSION_FILE}")
    print(f"  version: {engine.version_data.get('version', 'N/A')}")
    print(f"  codename: {engine.version_data.get('codename', 'N/A')}")
    print(f"  date: {engine.version_data.get('date', 'N/A')}")
    print()
    
    if args.rule:
        all_ok = engine.sync_rule(args.rule, args.check)
    else:
        all_ok = engine.sync_all(args.check)
    
    print()
    print("=" * 60)
    statuses = set(engine.results.values())
    summary = ", ".join(f"{k}:{v}" for k, v in engine.results.items()) if hasattr(engine, 'results') else ""
    print(f"Result: {'All files in sync' if all_ok else 'Some files need update'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
