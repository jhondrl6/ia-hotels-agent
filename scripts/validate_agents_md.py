#!/usr/bin/env python3
"""validate_agents_md.py — Audit AGENTS.md contra código vivo + ROADMAP.md

Uso: python scripts/validate_agents_md.py
Salida: JSON con resultados + exit code (0=PASS, 1=FAIL)
"""

import os
import re
import json
import sys
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
AGENTS_MD = BASE / "AGENTS.md"
ROADMAP_MD = BASE / "ROADMAP.md"
PUBLICATION_GATES = BASE / "modules" / "quality_gates" / "publication_gates.py"


def read_agents_md():
    return AGENTS_MD.read_text(encoding="utf-8")


def _is_deprecated_line(line: str) -> bool:
    """Check if a line marks content as deprecated."""
    return "[DEPRECADO]" in line.upper() or "[DEPRECATED]" in line.upper()


def check_1_modules_exist():
    """Checks que módulos citados en AGENTS.md existen en las rutas especificadas.
    Escanea AGENTS.md en busca de paths tipo `modules/...` y verifica existencia.
    Ignora paths que aparecen en líneas marcadas [DEPRECADO]."""
    content = read_agents_md()
    lines = content.splitlines()

    path_pattern = re.compile(
        r'`((?:modules|data_validation|agent_harness|observability|enums|scripts)/[\w_/]+\.py)`'
    )
    
    found = []
    missing = []
    
    for i, line in enumerate(lines):
        if _is_deprecated_line(line):
            continue
        
        matches = path_pattern.findall(line)
        for path in matches:
            full_path = BASE / path
            if full_path.exists():
                found.append(path)
            else:
                missing.append({"path": path, "line": i + 1, "text": line.strip()[:120]})

    status = "PASS" if len(missing) == 0 else "FAIL"
    return {
        "status": status,
        "total": len(found) + len(missing),
        "found": len(found),
        "missing": missing,
    }


def check_2_test_count():
    """Conteo de tests: pytest --collect-only -q vs AGENTS.md (tolerancia ±5%)."""
    content = read_agents_md()

    # Handles both "2,743" and "2743"
    test_pattern = re.compile(r'(\d{1,3}(?:,\d{3})*|\d{4,})\s+funciones')
    matches = test_pattern.findall(content)
    if not matches:
        return {"status": "SKIP", "error": "No test count found in AGENTS.md"}
    
    agents_count_str = matches[0].replace(",", "")
    agents_count = int(agents_count_str)

    result = run_collect_tests()
    if result["status"] != "OK":
        return {
            "status": "SKIP",
            "error": f"pytest collection failed: {result.get('error', 'unknown')}",
        }

    pytest_count = result["count"]
    denominator = max(agents_count, pytest_count, 1)
    pct_diff = abs(pytest_count - agents_count) / denominator * 100

    status = "PASS" if pct_diff <= 5 else "FAIL"
    return {
        "status": status,
        "agents_md_count": agents_count,
        "pytest_count": pytest_count,
        "pct_diff": round(pct_diff, 1),
        "tolerance": "±5%",
    }


def run_collect_tests():
    """Run pytest --collect-only and parse test count."""
    venv_python = BASE / "venv" / "Scripts" / "python.exe"
    python_exe = str(venv_python) if venv_python.exists() else sys.executable

    try:
        proc = subprocess.run(
            [python_exe, "-m", "pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            cwd=str(BASE),
            timeout=120,
        )
        output = (proc.stdout or "") + "\n" + (proc.stderr or "")

        match = re.search(r'(\d+)\s+(?:tests?\s+collected|items?)', output)
        if match:
            return {"status": "OK", "count": int(match.group(1))}
        
        test_lines = [l for l in output.splitlines() if "::" in l and "test_" in l]
        if test_lines:
            return {"status": "OK", "count": len(test_lines)}

        return {"status": "ERROR", "error": "Could not parse pytest output", "raw": output[:500]}
    except subprocess.TimeoutExpired:
        return {"status": "ERROR", "error": "pytest timed out"}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}


def check_3_gate_count():
    """Conteo de gates: len(self.gates) en publication_gates.py vs AGENTS.md."""
    content = read_agents_md()

    if not PUBLICATION_GATES.exists():
        return {"status": "SKIP", "error": "publication_gates.py not found"}

    gates_content = PUBLICATION_GATES.read_text(encoding="utf-8")

    gates_match = re.search(
        r'self\.gates\s*:\s*Dict\[\w+,\s*\w+\]\s*=\s*\{(.*?)\}',
        gates_content,
        re.DOTALL,
    )
    if not gates_match:
        return {"status": "SKIP", "error": "Could not find self.gates dict"}

    gates_block = gates_match.group(1)
    gate_entries = re.findall(r'"(\w+)"\s*:', gates_block)
    code_gate_count = len(gate_entries)

    gate_pattern = re.compile(r'(\d+)\s+publication\s+gates?', re.IGNORECASE)
    gate_matches = gate_pattern.findall(content)
    if not gate_matches:
        return {"status": "SKIP", "error": "No gate count found in AGENTS.md"}

    agents_gate_count = int(gate_matches[0])

    status = "PASS" if code_gate_count == agents_gate_count else "FAIL"
    return {
        "status": status,
        "code_gate_count": code_gate_count,
        "agents_md_count": agents_gate_count,
        "gate_names": gate_entries,
    }


def check_4_fase0_modules():
    """Componentes FASE-0 listados en ROADMAP.md aparecen en AGENTS.md §Módulos."""
    content = read_agents_md()

    fase0_modules = [
        "pain_ledger",
        "delivery_quality_report",
        "human_checklist",
        "data_derivation_layer",
    ]

    missing_from_agents = []
    for mod in fase0_modules:
        if mod.lower() not in content.lower():
            missing_from_agents.append(mod)

    roadmap_missing = []
    if ROADMAP_MD.exists():
        roadmap_content = ROADMAP_MD.read_text(encoding="utf-8")
        for mod in fase0_modules:
            if mod.lower() not in roadmap_content.lower():
                roadmap_missing.append(mod)

    all_missing = list(set(missing_from_agents + roadmap_missing))
    status = "PASS" if len(all_missing) == 0 else "FAIL"

    return {
        "status": status,
        "modules_checked": fase0_modules,
        "missing_agents_md": missing_from_agents,
        "missing_roadmap": roadmap_missing,
    }


def check_5_no_deprecated_active():
    """Módulos en archives/deprecated_* NO aparecen como activos en AGENTS.md.
    Solo flaggea módulos que existen EXCLUSIVAMENTE en archives."""
    content = read_agents_md()
    lines = content.splitlines()
    archives_dir = BASE / "archives"

    if not archives_dir.exists():
        return {
            "status": "PASS",
            "note": "No archives/ directory — nothing to check",
            "deprecated_found": [],
        }

    # Collect .py basenames from deprecated_modules_* subdirs
    deprecated_basenames = set()
    for subdir in archives_dir.iterdir():
        if subdir.is_dir() and subdir.name.startswith("deprecated_modules"):
            for py_file in subdir.rglob("*.py"):
                if py_file.name != "__init__.py":
                    deprecated_basenames.add(py_file.name)

    # A module is "exclusively deprecated" if NO copy exists outside archives
    exclusively_deprecated = set()
    for basename in deprecated_basenames:
        # Search for this file outside archives/
        found_outside = False
        for root, dirs, files in os.walk(str(BASE)):
            # Skip archives directory
            if "archives" in root.split(os.sep):
                continue
            if basename in files:
                found_outside = True
                break
        if not found_outside:
            exclusively_deprecated.add(basename)

    # Now check AGENTS.md for active references to exclusively-deprecated modules
    active_references = []
    for i, line in enumerate(lines):
        if _is_deprecated_line(line):
            continue
        
        backtick_paths = re.findall(r'`([^`]+)`', line)
        for bt_path in backtick_paths:
            basename = bt_path.split("/")[-1]
            if basename in exclusively_deprecated:
                active_references.append({
                    "module": basename,
                    "path": bt_path,
                    "line": i + 1,
                    "text": line.strip()[:120],
                })

    status = "PASS" if len(active_references) == 0 else "FAIL"
    return {
        "status": status,
        "exclusively_deprecated": sorted(exclusively_deprecated),
        "active_references": active_references,
    }


def check_6_scripts_exist():
    """Scripts referenciados en AGENTS.md existen en scripts/."""
    content = read_agents_md()
    lines = content.splitlines()

    # Match scripts/foo.py anywhere inside backtick content
    script_pattern = re.compile(r'`[^`]*\b(scripts/[\w_]+\.py)\b[^`]*`')

    found = []
    missing = []
    for i, line in enumerate(lines):
        matches = script_pattern.findall(line)
        for path in matches:
            full_path = BASE / path
            if full_path.exists():
                found.append(path)
            else:
                missing.append({"path": path, "line": i + 1, "text": line.strip()[:120]})

    status = "PASS" if len(missing) == 0 else "FAIL"
    return {
        "status": status,
        "total": len(found) + len(missing),
        "found": len(found),
        "missing": missing,
    }


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    results = {
        "modules_exist": check_1_modules_exist(),
        "test_count": check_2_test_count(),
        "gate_count": check_3_gate_count(),
        "fase0_modules": check_4_fase0_modules(),
        "no_deprecated_active": check_5_no_deprecated_active(),
        "scripts_exist": check_6_scripts_exist(),
    }

    passed = all(
        r.get("status") == "PASS"
        for r in results.values()
    )

    print(json.dumps(results, indent=2, ensure_ascii=False))

    if not passed:
        failed = [k for k, v in results.items() if v.get("status") == "FAIL"]
        print(f"\n[{len(failed)}/{len(results)} FAILED]: {', '.join(failed)}", file=sys.stderr)

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
