#!/usr/bin/env python3
"""
Doctor - Agente Ecosystem Health Check.

Integrates all validation scripts into a single CLI entry point:
- `python scripts/doctor.py` -- full ecosystem + context check
- `python scripts/doctor.py --agent` -- only agent ecosystem
- `python scripts/doctor.py --context` -- only context integrity
- `python scripts/doctor.py --status` -- regenerate SYSTEM_STATUS.md
- `python scripts/doctor.py --json` -- machine-readable output

Also callable from main.py as `python main.py --doctor`
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
AGENT_ROOT = PROJECT_ROOT / ".agent"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


def run_validator(script: str, label: str, capture_output: bool = False) -> tuple:
    """Run a validation script and return (passed, stdout, stderr)."""
    script_path = SCRIPTS_DIR / script
    if not script_path.exists():
        return False, "", f"Script not found: {script}"
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(PROJECT_ROOT)
        )
        passed = result.returncode == 0
        stdout = result.stdout
        stderr = result.stderr
        return passed, stdout, stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Timeout after 120s"
    except Exception as e:
        return False, "", str(e)


def print_header(title: str, char: str = "="):
    print(f"\n{char * 60}")
    print(f"  {title}")
    print(f"{char * 60}")


def print_check(status: str, label: str, detail: str = ""):
    icon = "[OK]" if status == "PASS" else "[!!]"
    line = f"  {icon}  {label}"
    if detail:
        line += f" -- {detail}"
    print(line)


def run_full() -> bool:
    """Run all checks and return True if everything passed."""
    print_header("AGENT ECOSYSTEM -- DOCTOR")
    print(f"  Project:  {PROJECT_ROOT}")
    print(f"  Timestamp: {datetime.now(timezone.utc).isoformat()}")

    # 1. Run agent ecosystem validator
    print_header("1. Agent Ecosystem Check", "-")
    agent_passed, agent_out, agent_err = run_validator("validate_agent_ecosystem.py", "Agent Ecosystem")

    if agent_out:
        # Print the validator output
        for line in agent_out.strip().split("\n"):
            print(f"  {line}")
    if agent_err:
        print(f"  [STDERR] {agent_err}")

    # 2. Run context integrity validator
    print_header("2. Context Integrity Check", "-")
    ctx_passed, ctx_out, ctx_err = run_validator("validate_context_integrity.py", "Context Integrity")

    if ctx_out:
        for line in ctx_out.strip().split("\n"):
            print(f"  {line}")
    if ctx_err:
        print(f"  [STDERR] {ctx_err}")

    # 3. Check version consistency
    print_header("3. Version Consistency", "-")
    version_file = PROJECT_ROOT / "VERSION.yaml"
    sys_status = AGENT_ROOT / "SYSTEM_STATUS.md"
    readme = PROJECT_ROOT / "CHANGELOG.md"

    if version_file.exists():
        content = version_file.read_text()
        for line in content.split("\n"):
            if line.startswith("version:"):
                version = line.split('"')[1].strip('"') if '"' in line else line.split(":")[1].strip()
                print_check("PASS", "VERSION.yaml", version)
                break
    else:
        print_check("FAIL", "VERSION.yaml", "not found")

    # 4. Quick file counts
    print_header("4. Ecosystem Stats", "-")

    # Skill count
    workflows = PROJECT_ROOT / ".agents" / "workflows"
    if workflows.exists():
        md_count = len(list(workflows.glob("*.md")))
        py_count = len(list(workflows.glob("*.py")))
        print_check("PASS", f"Skills in .agents/workflows/", f"{md_count} markdown, {py_count} python")

    # Shadow logs
    shadow_dir = AGENT_ROOT / "shadow_logs"
    if shadow_dir.exists():
        sl_count = len(list(shadow_dir.glob("*.json")))
        print_check("PASS", f"Shadow logs", f"{sl_count} files")

    # Sessions
    session_dir = AGENT_ROOT / "memory" / "sessions"
    if session_dir.exists():
        sess_count = len(list(session_dir.glob("*.json")))
        print_check("PASS", f"Active sessions", f"{sess_count} files")

    # 5. Summary
    print_header("SUMMARY")
    all_passed = agent_passed and ctx_passed

    if all_passed:
        print("  Doctor: ALL CHECKS PASSED")
    else:
        issues = []
        if not agent_passed:
            issues.append("agent ecosystem")
        if not ctx_passed:
            issues.append("context integrity")
        print(f"  Doctor: ISSUES FOUND in {', '.join(issues)}")
        print("  Run `python scripts/doctor.py --json` for details")

    print("=" * 60)
    return all_passed


def run_status() -> bool:
    """Regenerate SYSTEM_STATUS.md from live data."""
    sys_status = AGENT_ROOT / "SYSTEM_STATUS.md"

    # Get project version
    version = "unknown"
    version_file = PROJECT_ROOT / "VERSION.yaml"
    if version_file.exists():
        for line in version_file.read_text().split("\n"):
            if line.startswith("version:"):
                version = line.split('"')[1].strip('"') if '"' in line else line.split(":")[1].strip()
                break

    # Get workflow stats
    workflows = PROJECT_ROOT / ".agents" / "workflows"
    skills = []
    if workflows.exists():
        for f in sorted(workflows.glob("*.md")):
            if f.name == "README.md":
                continue
            # Read description from frontmatter
            desc = ""
            try:
                content = f.read_text(encoding="utf-8")
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 2:
                        fm = parts[1].strip()
                        for line in fm.split("\n"):
                            if line.startswith("description:"):
                                desc = line.split(":", 1)[1].strip()
                                break
            except Exception:
                pass
            skills.append((f.name, desc))

    # Shadow logs count
    shadow_count = 0
    shadow_dir = AGENT_ROOT / "shadow_logs"
    if shadow_dir.exists():
        shadow_count = len(list(shadow_dir.glob("*.json")))

    # Session count
    session_count = 0
    session_dir = AGENT_ROOT / "memory" / "sessions"
    if session_dir.exists():
        session_count = len(list(session_dir.glob("*.json")))

    # Archive count
    archive_count = 0
    archive_dir = AGENT_ROOT / "memory" / "archives" / "sessions"
    if archive_dir.exists():
        archive_count = len(list(archive_dir.glob("*.json")))

    # Current state
    cs_file = AGENT_ROOT / "memory" / "current_state.json"
    last_url = "N/A"
    last_updated = "N/A"
    if cs_file.exists():
        try:
            cs = json.loads(cs_file.read_text())
            last_url = cs.get("last_url", "N/A")
            last_updated = cs.get("last_updated", "N/A")
        except Exception:
            pass

    # Last shadow log
    last_shadow = "N/A"
    if shadow_dir.exists():
        shadow_files = sorted(shadow_dir.glob("*.json"))
        if shadow_files:
            last_shadow = shadow_files[-1].name

    # Last session
    last_session = "N/A"
    if session_dir.exists():
        session_files = sorted(session_dir.glob("*.json"))
        if session_files:
            last_session = session_files[-1].name

    # Build markdown
    skills_md = "| Skill | Descripcion |\n"
    skills_md += "|-------|-------------|\n"
    for name, desc in skills:
        skills_md += f"| {name} | {desc or '-'} |\n"

    content = f"""# System Status Dashboard

> Auto-generado: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
> Fuente de verdad para version: VERSION.yaml en raiz del proyecto
> REGENERAR CON: python scripts/doctor.py --status
> NO EDITAR MANUALMENTE - Este archivo se regenera automaticamente

## Versiones

| Componente | Version | Fuente |
|------------|---------|--------|
| Proyecto | {version} | VERSION.yaml |
| Ecosystem Convention | 1.0.0 | .agent/CONVENTION.md |

## Skills Activas ({len(skills)})

{skills_md}

## Estado de Datos

| Metrica | Valor |
|---------|-------|
| Shadow logs | {shadow_count} archivos JSON |
| Sesiones activas | {session_count} |
| Sesiones archivadas | {archive_count} |
| Ultimo shadow log | {last_shadow} |
| Ultima sesion activa | {last_session} |
| Ultimo contexto actualizado | {last_updated} |
| Ultima URL procesada | {last_url} |

## Validaciones

Ejecuta `python main.py --doctor` para verificar el estado completo del ecosistema.

Scripts de validacion:
- `python scripts/validate_agent_ecosystem.py` -- Ecosistema de agentes
- `python scripts/validate_context_integrity.py` -- Integridad de contexto
- `python scripts/doctor.py --status` -- Regenerar este archivo
"""

    sys_status.write_text(content, encoding="utf-8")
    print(f"[OK] SYSTEM_STATUS.md regenerado ({len(skills)} skills, {shadow_count} shadow logs, {session_count} sesiones)")
    return True


def run_json() -> bool:
    """Run all checks and output JSON."""
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "version": "unknown",
        "checks": {}
    }

    # Version
    version_file = PROJECT_ROOT / "VERSION.yaml"
    if version_file.exists():
        for line in version_file.read_text().split("\n"):
            if line.startswith("version:"):
                result["version"] = line.split('"')[1].strip('"') if '"' in line else line.split(":")[1].strip()
                break

    # Agent ecosystem
    agent_passed, agent_out, agent_err = run_validator("validate_agent_ecosystem.py", "Agent")
    result["checks"]["agent_ecosystem"] = {"passed": agent_passed, "stderr": agent_err}

    # Context integrity
    ctx_passed, ctx_out, ctx_err = run_validator("validate_context_integrity.py", "Context")
    result["checks"]["context_integrity"] = {"passed": ctx_passed, "stderr": ctx_err}

    # Stats
    workflows = PROJECT_ROOT / ".agents" / "workflows"
    result["stats"] = {}
    if workflows.exists():
        result["stats"]["skills"] = len(list(workflows.glob("*.md")))
    shadow_dir = AGENT_ROOT / "shadow_logs"
    if shadow_dir.exists():
        result["stats"]["shadow_logs"] = len(list(shadow_dir.glob("*.json")))

    result["overall"] = agent_passed and ctx_passed
    print(json.dumps(result, indent=2))
    return result["overall"]


def main():
    parser = argparse.ArgumentParser(description="Agent ecosystem health check")
    parser.add_argument("--agent", action="store_true", help="Only run agent ecosystem check")
    parser.add_argument("--context", action="store_true", help="Only run context integrity check")
    parser.add_argument("--status", action="store_true", help="Regenerate SYSTEM_STATUS.md")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.status:
        ok = run_status()
        sys.exit(0 if ok else 1)

    if args.json:
        ok = run_json()
        sys.exit(0 if ok else 1)

    if args.agent:
        agent_passed, agent_out, agent_err = run_validator("validate_agent_ecosystem.py", "Agent")
        print(agent_out)
        if agent_err:
            print(agent_err, file=sys.stderr)
        sys.exit(0 if agent_passed else 1)

    if args.context:
        ctx_passed, ctx_out, ctx_err = run_validator("validate_context_integrity.py", "Context")
        print(ctx_out)
        if ctx_err:
            print(ctx_err, file=sys.stderr)
        sys.exit(0 if ctx_passed else 1)

    # Default: full check
    ok = run_full()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
