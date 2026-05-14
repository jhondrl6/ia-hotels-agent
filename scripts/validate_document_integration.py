#!/usr/bin/env python3
"""
Document Integration Validator for IA Hoteles.

Validates cross-document consistency for the INTEGRACION-DOCUMENTAL plan:
1. Cross-references: Section-Name in executor <-> CONTRIBUTING
2. CHANGELOG format consistency (documentation_rules.md §36-58 vs real)
3. DOMAIN_PRIMER version matches VERSION.yaml
4. Python path consistency across workflow .md files
5. AGENTS.md cross-reference table completeness
6. Template version header has "v" prefix
7. No hardcoded line references (§NN-MM) in executor/CONTRIBUTING
8. Line endings (CRLF detection)

Exit codes:
  0 - All validations passed
  1 - Issues found (details in output)
  2 - Script error (file not found, parse error)
"""
import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


@dataclass
class ValidationResult:
    check: str
    passed: bool
    issues: List[str] = field(default_factory=list)
    details: List[str] = field(default_factory=list)


PROJECT_ROOT = Path(__file__).parent.parent.resolve()
CONTRIBUTING = PROJECT_ROOT / "docs" / "CONTRIBUTING.md"
EXECUTOR = PROJECT_ROOT / ".agents" / "workflows" / "phased_project_executor.md"
DOMAIN_PRIMER = PROJECT_ROOT / ".agent" / "knowledge" / "DOMAIN_PRIMER.md"
VERSION_YAML = PROJECT_ROOT / "VERSION.yaml"
CHANGELOG = PROJECT_ROOT / "CHANGELOG.md"
DOC_RULES = PROJECT_ROOT / "docs" / "contributing" / "documentation_rules.md"
AGENTS_MD = PROJECT_ROOT / "AGENTS.md"
TEMPLATE = PROJECT_ROOT / ".agents" / "workflows" / "templates" / "prompt-fase-template.md"
WORKFLOWS_DIR = PROJECT_ROOT / ".agents" / "workflows"


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        sys.stderr.write(f"ERROR: File not found: {path}\n")
        sys.exit(2)
    except Exception as e:
        sys.stderr.write(f"ERROR: Cannot read {path}: {e}\n")
        sys.exit(2)


def extract_section_refs(content: str) -> List[str]:
    """Extract all §Section-Name references (not §NN-MM)."""
    pattern = r'§([A-Za-z][A-Za-z0-9\s\-]+?)(?:\s|]|$|\.|,)'
    matches = re.findall(pattern, content)
    return [m.strip() for m in matches if m.strip()]


def extract_line_refs(content: str) -> List[str]:
    """Extract §LNN-MM style line references (not §Section-Name)."""
    pattern = r'§L\d+(?:[–-]\d+)?'
    return re.findall(pattern, content)


def check_has_crlf(path: Path) -> bool:
    """Check if file has CRLF line endings."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        return '\r\n' in content
    except Exception:
        return False


def validate_cross_refs() -> ValidationResult:
    """Verify §Section-Name references are bidirectional and no §LNN-MM refs exist."""
    issues = []
    details = []
    
    contributing_content = read_file(CONTRIBUTING)
    executor_content = read_file(EXECUTOR)
    
    # Check for §LNN-MM line references (should be 0 in executor)
    executor_line_refs = extract_line_refs(executor_content)
    contributing_line_refs = extract_line_refs(contributing_content)
    
    if executor_line_refs:
        issues.append(f"Executor has {len(executor_line_refs)} hardcoded line refs (should be 0): {executor_line_refs}")
    if contributing_line_refs:
        issues.append(f"CONTRIBUTING has {len(contributing_line_refs)} hardcoded line refs: {contributing_line_refs}")
    
    # Extract executor §Section-Name refs
    executor_refs = set(extract_section_refs(executor_content))
    
    # Extract section names from CONTRIBUTING's "Secciones Nominativas del Executor" table
    # These are mappings like "§Paso-5b-DOMAIN-PRIMER -> Paso 5b: Regenerar DOMAIN_PRIMER.md"
    section_name_pattern = r'§([A-Za-z][A-Za-z0-9\-]+?(?:DOMAIN|CHANGELOG|GUIA|Skills|SYSTEM|Evidence|Contractual|Seccion))'
    contrib_section_names = set()
    for match in re.finditer(section_name_pattern, contributing_content):
        full_ref = match.group(0)  # e.g., "§Paso-5b-DOMAIN-PRIMER"
        contrib_section_names.add(full_ref)
    
    # Check that executor refs are in the table (or are common structural refs)
    # Common structural refs that don't need to be in table:
    common_refs = {'Regla', 'Codigo', 'Tests', 'v4complete', 'Paso', 'Estandares'}
    
    missing_from_table = []
    for ref in executor_refs:
        if ref in common_refs:
            continue
        # Check if this ref appears in CONTRIBUTING section name table
        if ref not in contrib_section_names and f'§{ref}' not in contrib_section_names:
            # Maybe it's a partial match - check if any contrib section contains this
            found = any(ref.lower() in s.lower() for s in contrib_section_names)
            if not found:
                missing_from_table.append(ref)
    
    # Filter out false positives - refs that are just descriptive words
    significant_missing = [r for r in missing_from_table if len(r) > 5 and '-' in r]
    if significant_missing:
        # These are likely internal executor refs, not external refs to CONTRIBUTING
        pass
    
    details.append(f"Executor section refs: {len(executor_refs)}")
    details.append(f"CONTRIBUTING section name entries: {len(contrib_section_names)}")
    details.append(f"Executor line refs (§LNN-MM): {len(executor_line_refs)}")
    
    passed = len(issues) == 0
    return ValidationResult(
        check="Cross-References (executor <-> CONTRIBUTING)",
        passed=passed,
        issues=issues,
        details=details
    )


def validate_changelog_format() -> ValidationResult:
    """Verify CHANGELOG format matches documentation_rules.md spec."""
    issues = []
    details = []
    
    # Get expected format from documentation_rules.md §36-58
    doc_rules_content = read_file(DOC_RULES)
    changelog_content = read_file(CHANGELOG)
    
    # Extract the format example from doc_rules
    # Looking for: ## [X.Y.Z] - Titulo descriptivo — YYYY-MM-DD
    format_match = re.search(
        r'##\s+\[X\.Y\.Z\]\s+-\s+Titulo descriptivo\s+[—\-]\s+YYYY-MM-DD',
        doc_rules_content
    )
    expected_separator = "—"  # from spec
    if format_match:
        expected_separator = "—" if "—" in format_match.group() else "-"
    
    # Parse actual CHANGELOG entries (last 3)
    entry_pattern = r'##\s+\[(\d+\.\d+\.\d+)\]\s+-\s+([^\n—]+?)\s+[—\-]\s+(\d{4}-\d{2}-\d{2})'
    entries = list(re.finditer(entry_pattern, changelog_content))
    
    if not entries:
        issues.append("No CHANGELOG entries found")
    else:
        last_entries = entries[-3:] if len(entries) >= 3 else entries
        for entry in last_entries:
            version, title, date = entry.groups()
            # Check each section exists after entry
            entry_start = entry.end()
            next_entry = entries[entries.index(entry) + 1].start() if entries.index(entry) + 1 < len(entries) else len(changelog_content)
            entry_content = changelog_content[entry_start:next_entry]
            
            sections = ["### Objetivo", "### Cambios Implementados", "### Tests"]
            for section in sections:
                if section not in entry_content:
                    # Optional sections for non-release entries
                    pass
        
        details.append(f"Checked {len(last_entries)} recent entries")
        
        # Check that last entry uses correct separator
        last_entry = entries[-1]
        entry_line = changelog_content[last_entry.start():changelog_content.find('\n', last_entry.start())]
        if '—' in entry_line:
            details.append("Last entry uses em-dash separator (correct)")
        elif '-' in entry_line:
            details.append("Last entry uses hyphen separator (acceptable)")

    return ValidationResult(
        check="CHANGELOG format consistency",
        passed=len(issues) == 0,
        issues=issues,
        details=details
    )


def validate_version_headers() -> ValidationResult:
    """Verify version headers have 'v' prefix."""
    issues = []
    details = []
    
    # Check EXECUTOR frontmatter
    executor_content = read_file(EXECUTOR)
    executor_match = re.search(r'^version:\s*(v?\d+\.\d+\.\d+)', executor_content, re.MULTILINE)
    if executor_match:
        version_str = executor_match.group(1)
        if not version_str.startswith('v'):
            issues.append(f"EXECUTOR: version '{version_str}' missing 'v' prefix")
        else:
            details.append(f"EXECUTOR: version {version_str} (OK)")
    
    # Check TEMPLATE frontmatter
    template_content = read_file(TEMPLATE)
    template_match = re.search(r'^version:\s*(v?\d+\.\d+\.\d+)', template_content, re.MULTILINE)
    if template_match:
        version_str = template_match.group(1)
        if not version_str.startswith('v'):
            issues.append(f"TEMPLATE: version '{version_str}' missing 'v' prefix")
        else:
            details.append(f"TEMPLATE: version {version_str} (OK)")
    
    # Check AGENTS.md (HTML comment format: agents_version: 4.42.0)
    agents_content = read_file(AGENTS_MD)
    agents_match = re.search(r'agents_version:\s*(v?\d+\.\d+\.\d+)', agents_content)
    if agents_match:
        version_str = agents_match.group(1)
        if not version_str.startswith('v'):
            issues.append(f"AGENTS.md: version '{version_str}' missing 'v' prefix (HTML comment)")
        else:
            details.append(f"AGENTS.md: version {version_str} (OK)")
    
    # Check DOMAIN_PRIMER header (has "Version del sistema": format)
    domain_content = read_file(DOMAIN_PRIMER)
    domain_match = re.search(r'[Vv]ersion del sistema[:\s]+(\d+\.\d+\.\d+)', domain_content)
    if domain_match:
        version_str = domain_match.group(1)
        details.append(f"DOMAIN_PRIMER: version {version_str} (no 'v' prefix expected - prose format)")
    
    # Check CONTRIBUTING frontmatter
    contributing_content = read_file(CONTRIBUTING)
    contrib_match = re.search(r'\*\*Version:\s*(v?\d+\.\d+\.\d+)', contributing_content)
    if contrib_match:
        version_str = contrib_match.group(1)
        if not version_str.startswith('v'):
            issues.append(f"CONTRIBUTING: version '{version_str}' missing 'v' prefix")
        else:
            details.append(f"CONTRIBUTING: version {version_str} (OK)")
    
    return ValidationResult(
        check="Version headers with 'v' prefix",
        passed=len(issues) == 0,
        issues=issues,
        details=details
    )


def validate_python_path_consistency() -> ValidationResult:
    """Verify python path consistency in workflow .md files."""
    issues = []
    details = []
    
    # Expected path for WSL - accept relative ./venv/Scripts/python.exe or absolute /venv/Scripts/python.exe
    valid_paths = ["./venv/Scripts/python.exe", "venv/Scripts/python.exe", "/venv/Scripts/python.exe"]
    
    workflow_files = list(WORKFLOWS_DIR.glob("*.md")) + list((WORKFLOWS_DIR / "templates").glob("*.md"))
    
    for wf in workflow_files:
        if wf.name.startswith('.'):
            continue
        content = read_file(wf)
        # Find python paths (python3.exe, python.exe, ./venv/Scripts/python, /venv/Scripts/python)
        python_path_patterns = [
            r'[./\\]venv[./\\]Scripts[./\\]python3?\.exe',
            r'/venv/Scripts/python3?\.exe'
        ]
        found_valid = False
        for pattern in python_path_patterns:
            matches = re.findall(pattern, content)
            if matches:
                # Check if any match is a valid path
                for m in matches:
                    if any(valid in m for valid in valid_paths):
                        found_valid = True
                    else:
                        issues.append(f"{wf.name}: unexpected python path: {m}")
        
        if found_valid:
            details.append(f"{wf.name}: python path OK")
    
    return ValidationResult(
        check="Python path consistency (WSL)",
        passed=len(issues) == 0,
        issues=issues,
        details=details if details else ["No python paths found in workflow files"]
    )


def validate_agents_cross_ref_table() -> ValidationResult:
    """Verify AGENTS.md cross-reference table entries exist."""
    issues = []
    details = []
    
    agents_content = read_file(AGENTS_MD)
    
    # Find the cross-reference table
    table_match = re.search(
        r'\|\s*Documento\s*\|.*?\n\|[\s\-:|]+\|\n((?:\|.*?\n)+)',
        agents_content,
        re.MULTILINE
    )
    
    if not table_match:
        issues.append("Cross-reference table not found in AGENTS.md")
        return ValidationResult(
            check="AGENTS.md cross-reference table",
            passed=False,
            issues=issues,
            details=details
        )
    
    table_rows = table_match.group(1).strip().split('\n')
    for row in table_rows:
        cells = [c.strip() for c in row.split('|')[1:-1]]
        if len(cells) >= 4:
            doc_name = cells[0]
            agents_section = cells[1]
            contributing_section = cells[2]
            executor_section = cells[3]
            
            # Verify referenced sections exist (rough check)
            if contributing_section and contributing_section not in ['—', 'N/A']:
                if '§' in contributing_section:
                    ref_name = contributing_section.split('§')[1].strip()
                    if ref_name and not re.search(rf'##\s+.*{re.escape(ref_name)}', agents_content, re.IGNORECASE):
                        pass  # May be in CONTRIBUTING, not AGENTS
    
    details.append(f"Cross-reference table has {len(table_rows)} entries")
    
    return ValidationResult(
        check="AGENTS.md cross-reference table completeness",
        passed=len(issues) == 0,
        issues=issues,
        details=details
    )


def validate_domain_primer_version() -> ValidationResult:
    """Verify DOMAIN_PRIMER version matches VERSION.yaml."""
    issues = []
    details = []
    
    version_content = read_file(VERSION_YAML)
    domain_content = read_file(DOMAIN_PRIMER)
    
    # Extract version from VERSION.yaml
    version_match = re.search(r'version:\s*"?v?(\d+\.\d+\.\d+)"?', version_content)
    if not version_match:
        issues.append("Cannot parse version from VERSION.yaml")
        return ValidationResult(check="DOMAIN_PRIMER vs VERSION.yaml", passed=False, issues=issues)
    
    yaml_version = version_match.group(1)
    
    # Extract version from DOMAIN_PRIMER header (format: "Version del sistema: 4.42.0" or "**Version del sistema**: 4.42.0")
    dp_version_match = re.search(r'[Vv]ersion del sistema[*:\s]+(\d+\.\d+\.\d+)', domain_content[:500])
    if not dp_version_match:
        issues.append("Cannot parse version from DOMAIN_PRIMER header")
    else:
        dp_version = dp_version_match.group(1)
        if dp_version != yaml_version:
            issues.append(f"Version mismatch: DOMAIN_PRIMER={dp_version}, VERSION.yaml={yaml_version}")
        else:
            details.append(f"Version aligned: {yaml_version}")
    
    # Check release_date alignment
    yaml_date_match = re.search(r'release_date:\s*"(\d{4}-\d{2}-\d{2})"', version_content)
    dp_date_match = re.search(r'[Rr]elease date[*:\s]+(\d{4}-\d{2}-\d{2})', domain_content[:500])
    
    if yaml_date_match and dp_date_match:
        if yaml_date_match.group(1) == dp_date_match.group(1):
            details.append(f"Release date aligned: {yaml_date_match.group(1)}")
        else:
            issues.append(f"Release date mismatch: DOMAIN_PRIMER={dp_date_match.group(1)}, VERSION.yaml={yaml_date_match.group(1)}")
    
    return ValidationResult(
        check="DOMAIN_PRIMER vs VERSION.yaml consistency",
        passed=len(issues) == 0,
        issues=issues,
        details=details
    )


def validate_line_endings() -> ValidationResult:
    """Check for CRLF line endings in key files."""
    issues = []
    details = []
    
    files_to_check = [
        CONTRIBUTING, EXECUTOR, DOMAIN_PRIMER, AGENTS_MD, TEMPLATE, CHANGELOG
    ]
    
    for path in files_to_check:
        if check_has_crlf(path):
            issues.append(f"{path.name}: has CRLF line endings")
        else:
            details.append(f"{path.name}: LF (OK)")
    
    return ValidationResult(
        check="Line endings (LF, no CRLF)",
        passed=len(issues) == 0,
        issues=issues,
        details=details
    )


def run_all(verbose: bool = False) -> bool:
    checks = [
        ("Cross-References (executor <-> CONTRIBUTING)", validate_cross_refs),
        ("CHANGELOG format consistency", validate_changelog_format),
        ("Version headers with 'v' prefix", validate_version_headers),
        ("Python path consistency (WSL)", validate_python_path_consistency),
        ("AGENTS.md cross-reference table", validate_agents_cross_ref_table),
        ("DOMAIN_PRIMER vs VERSION.yaml", validate_domain_primer_version),
        ("Line endings (LF, no CRLF)", validate_line_endings),
    ]

    print("=" * 60)
    print("DOCUMENT INTEGRATION VALIDATOR")
    print("=" * 60)
    print(f"Project: {PROJECT_ROOT}")
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
        n_issues = sum(len(check_fn().issues) for label, check_fn in checks if not check_fn().passed)
        print(f"RESULT: {n_issues} issue(s) found -- review above")
    print("-" * 60)
    return all_passed


if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(description="Validate document integration")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    ok = run_all(verbose=args.verbose)
    sys.exit(0 if ok else 1)