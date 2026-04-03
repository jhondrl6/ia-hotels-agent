#!/usr/bin/env python3
"""
Agent Ecosystem Validator for IA Hoteles.

Validates the health and consistency of the agent ecosystem:
1. .agent/ (runtime data: memory, logs, knowledge)
2. .agents/workflows/ (agent skills and workflows)
3. Cross-references between them (symlink integrity, dead URLs)
4. Shadow log health
5. Memory/session integrity

Exit codes:
  0 - All validations passed
  1 - Issues found (details in output)
"""
import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class ValidationResult:
    check: str
    passed: bool
    issues: List[str] = field(default_factory=list)
    details: List[str] = field(default_factory=list)


PROJECT_ROOT = Path(__file__).parent.parent.resolve()
AGENT_DATA = PROJECT_ROOT / ".agent"
AGENT_SKILLS = PROJECT_ROOT / ".agents" / "workflows"


def validate_symlink() -> ValidationResult:
    """Check that .agent/workflows is a symlink (or accessible dir) pointing to .agents/workflows."""
    link = AGENT_DATA / "workflows"
    issues = []
    details = []
    target_dir = PROJECT_ROOT / ".agents" / "workflows"

    try:
        if link.is_symlink():
            target = link.resolve()
            details.append(f"workflows (symlink) -> {target}")
            if not target.exists():
                issues.append(f"Symlink target does not exist: {link}")
        elif link.is_dir():
            details.append(f"workflows (directory, resolved to {link})")
            if not (link / "README.md").exists():
                issues.append("workflows directory has no README.md (may be empty or wrong target)")
        else:
            issues.append("workflows is missing (neither symlink nor directory)")
    except OSError as e:
        # Windows symlink permission error -- fallback: check the target directly
        details.append(f"workflows (symlink exists, stat needs elevated access: {e})")

    # Verify the expected target has content regardless of symlink access
    if target_dir.exists():
        md_count = len(list(target_dir.glob("*.md")))
        details.append(f"Target (.agents/workflows) exists: {md_count} skills")
    else:
        issues.append("Target .agents/workflows/ not found")
    return ValidationResult(check="symlink", passed=len(issues) == 0, issues=issues, details=details)


def validate_readme_refs() -> ValidationResult:
    """Check that README.md in workflows does not reference missing files."""
    readme = AGENT_SKILLS / "README.md"
    issues = []
    details = []
    if not readme.exists():
        return ValidationResult(check="README_refs", passed=False, issues=["README.md not found"])
    content = readme.read_text(encoding="utf-8")
    import re
    refs = set(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content))
    for title, target in sorted(refs):
        if target.startswith('#'):
            continue  # anchor
        path = AGENT_SKILLS / target
        if not path.exists():
            issues.append(f"README references {target} ({title}) -- file not found")
        else:
            details.append(f"OK: {target}")
    return ValidationResult(check="README_refs", passed=len(issues) == 0, issues=issues, details=details)


def validate_skills_exist() -> ValidationResult:
    """Check that every .md in workflows/ is tracked in README.md."""
    issues = []
    details = []
    readme = (AGENT_SKILLS / "README.md").read_text(encoding="utf-8")
    for f in sorted(AGENT_SKILLS.iterdir()):
        if not f.name.startswith('.') and f.name not in ('README.md',) and f.suffix in ('.md', '.py'):
            if f.name not in readme:
                issues.append(f"File exists but not in README.md: {f.name}")
            else:
                details.append(f"Tracked: {f.name}")
    return ValidationResult(check="skills_in_readme", passed=len(issues) == 0, issues=issues, details=details)


def validate_shadow_logs() -> ValidationResult:
    """Validate a sample of shadow log files are parseable JSON."""
    log_dir = AGENT_DATA / "shadow_logs"
    issues = []
    details = []
    if not log_dir.exists():
        return ValidationResult(check="shadow_logs", passed=False, issues=["shadow_logs/ missing"])
    files = sorted(log_dir.glob("*.json"))
    details.append(f"Total shadow logs: {len(files)}")
    # Sample first 5 and last 5
    to_check = (files[:5] + files[-5:]) if len(files) > 10 else files
    corrupt = 0
    for f in to_check:
        try:
            data = json.loads(f.read_text())
            # Check required keys
            required = ["comparison_id", "timestamp", "hotel_id"]
            missing = [k for k in required if k not in data]
            if missing:
                issues.append(f"Missing keys in {f.name}: {missing}")
        except json.JSONDecodeError:
            corrupt += 1
            issues.append(f"Corrupt JSON: {f.name}")
    if corrupt:
        details.append(f"Corrupt files (sample): {corrupt}")
    details.append("Sample OK" if not corrupt else f"{corrupt} corrupt in sample")
    return ValidationResult(check="shadow_logs", passed=len(issues) == 0, issues=issues, details=details)


def validate_memory() -> ValidationResult:
    """Check memory/ structure and key files."""
    mem = AGENT_DATA / "memory"
    issues = []
    details = []
    required_files = ["current_state.json", "error_catalog.json", "COMMON_ERRORS.md"]
    for rf in required_files:
        p = mem / rf
        if p.exists():
            details.append(f"OK: {rf}")
        else:
            issues.append(f"Missing: {rf}")
    # Validate current_state is valid JSON
    cs = mem / "current_state.json"
    if cs.exists():
        try:
            json.loads(cs.read_text())
            details.append("current_state.json: valid JSON")
        except json.JSONDecodeError:
            issues.append("current_state.json: corrupt JSON")
    # Count session files
    sessions = list((mem / "sessions").glob("*.json")) if (mem / "sessions").exists() else []
    archives = list((mem / "archives/sessions").glob("*.json")) if (mem / "archives/sessions").exists() else []
    details.append(f"Active sessions: {len(sessions)}")
    details.append(f"Archived sessions: {len(archives)}")
    return ValidationResult(check="memory", passed=len(issues) == 0, issues=issues, details=details)


def validate_gitignore() -> ValidationResult:
    """Check that runtime data dirs are gitignored."""
    gitignore = PROJECT_ROOT / ".gitignore"
    issues = []
    details = []
    if not gitignore.exists():
        return ValidationResult(check="gitignore", passed=False, issues=[".gitignore not found"])
    content = gitignore.read_text(encoding="utf-8", errors="replace")
    required_patterns = [
        ".agent/memory/sessions/",
        ".agent/shadow_logs/",
        ".agent/memory/current_state.json"
    ]
    for p in required_patterns:
        if p in content:
            details.append(f"Tracked: {p}")
        else:
            issues.append(f"Not in .gitignore: {p}")
    return ValidationResult(check="gitignore", passed=len(issues) == 0, issues=issues, details=details)


def validate_knowledge() -> ValidationResult:
    """Check DOMAIN_PRIMER.md exists."""
    kp = AGENT_DATA / "knowledge" / "DOMAIN_PRIMER.md"
    if kp.exists():
        size = kp.stat().st_size
        return ValidationResult(check="knowledge", passed=True,
                                details=[f"DOMAIN_PRIMER.md: {size} bytes"])
    return ValidationResult(check="knowledge", passed=False,
                            issues=["knowledge/DOMAIN_PRIMER.md missing"])


def validate_agents_dir() -> ValidationResult:
    """Check that .agents/workflows/ has expected structure."""
    issues = []
    details = []
    if not AGENT_SKILLS.exists():
        return ValidationResult(check="agents_dir", passed=False, issues=[".agents/workflows/ missing"])
    md_files = list(AGENT_SKILLS.glob("*.md"))
    py_files = list(AGENT_SKILLS.glob("*.py"))
    details.append(f"Skills (Markdown): {len(md_files)}")
    details.append(f"Scripts (Python): {len(py_files)}")
    return ValidationResult(check="agents_dir", passed=True, details=details)


def run_all(verbose: bool = False) -> bool:
    checks = [
        ("Symlink integrity", validate_symlink),
        ("README dead references", validate_readme_refs),
        ("Skills tracked in README", validate_skills_exist),
        ("Shadow logs health", validate_shadow_logs),
        ("Memory structure", validate_memory),
        ("Gitignore patterns", validate_gitignore),
        ("Knowledge base", validate_knowledge),
        ("Agents directory", validate_agents_dir),
    ]

    print("=" * 60)
    print("AGENT ECOSYSTEM VALIDATOR")
    print("=" * 60)
    print(f"Project: {PROJECT_ROOT}")
    print(f"Data dir: {AGENT_DATA}")
    print(f"Skills dir: {AGENT_SKILLS}")
    print()

    all_passed = True
    for label, check_fn in checks:
        result = check_fn()
        status = "PASS" if result.passed else "FAIL"
        if not result.passed:
            all_passed = False
        print(f"[{status}] {label}")
        for d in result.details:
            print(f"      {d}")
        for i in result.issues:
            print(f"   [!] {i}")
        print()

    print("-" * 60)
    if all_passed:
        print("RESULT: All checks passed")
    else:
        n_issues = sum(
            len(check_fn().issues)
            for _, check_fn in checks
            if not check_fn().passed
        )
        print(f"RESULT: {n_issues} issue(s) found -- review above")
    print("-" * 60)
    return all_passed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate agent ecosystem integrity")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    ok = run_all(verbose=args.json)
    sys.exit(0 if ok else 1)
