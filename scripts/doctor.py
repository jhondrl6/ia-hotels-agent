#!/usr/bin/env python3
"""
Doctor - Agente Ecosystem Health Check.

Integrates all validation scripts into a single CLI entry point:
- `python scripts/doctor.py` -- full ecosystem + context check
- `python scripts/doctor.py --agent` -- only agent ecosystem
- `python scripts/doctor.py --context` -- only context integrity
- `python scripts/doctor.py --status` -- regenerate SYSTEM_STATUS.md
- `python scripts/doctor.py --regenerate-domain-primer` -- regenerate DOMAIN_PRIMER.md
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


def run_regenerate_domain_primer() -> bool:
    """Regenerate DOMAIN_PRIMER.md from live module data and VERSION.yaml.

    Scans both:
    - modules/ (application modules)
    - Top-level packages: agent_harness/, data_models/, enums/
    """
    from collections import defaultdict

    DOMAIN_PRIMER_PATH = AGENT_ROOT / "knowledge" / "DOMAIN_PRIMER.md"
    FALLBACK_PATH = PROJECT_ROOT / ".agents" / "knowledge" / "DOMAIN_PRIMER.md"
    target_path = DOMAIN_PRIMER_PATH if DOMAIN_PRIMER_PATH.exists() else FALLBACK_PATH

    # Get version info
    version = "unknown"
    codename = "unknown"
    plan_maestro = "unknown"
    version_file = PROJECT_ROOT / "VERSION.yaml"
    if version_file.exists():
        for line in version_file.read_text().split("\n"):
            if line.startswith("version:"):
                version = line.split('"')[1].strip('"') if '"' in line else line.split(":")[1].strip()
            elif line.startswith("codename:"):
                codename = line.split('"')[1].strip('"') if '"' in line else line.split(":")[1].strip()
            elif line.startswith("plan_maestro_version:"):
                plan_maestro = line.split('"')[1].strip('"') if '"' in line else line.split(":")[1].strip()

    # Helper: scan a package directory for modules
    def scan_package(pkg_path: Path) -> dict:
        pkg_info = {}
        for d in sorted(pkg_path.iterdir()):
            if not d.is_dir() or d.name.startswith("_") or d.name == "__pycache__":
                continue
            py_files = [f for f in d.rglob("*.py") if f.name != "__init__.py" and "__pycache__" not in str(f)]
            classes = defaultdict(list)
            for pyf in py_files:
                try:
                    text = pyf.read_text(encoding="utf-8", errors="ignore")
                    for ln in text.split("\n"):
                        stripped = ln.strip()
                        if stripped.startswith("class "):
                            cls_name = stripped.split("class ", 1)[1].split("(")[0].split(":")[0].strip()
                            if cls_name:
                                classes[pyf.name].append(cls_name)
                except Exception:
                    pass
            key_classes = {}
            for fname in sorted(classes.keys()):
                for cls in classes[fname][:4]:
                    key_classes.setdefault(fname, []).append(cls)
            pkg_info[d.name] = {"file_count": len(py_files), "classes": key_classes}
        return pkg_info

    def scan_agent_harness(pkg_path: Path) -> dict:
        """Scan agent_harness/ as a root-level package."""
        info = {}
        py_files = [f for f in pkg_path.rglob("*.py") if "__pycache__" not in str(f)]
        info["agent_harness"] = {"file_count": len(py_files), "classes": {}}
        # Also scan submodules individually
        for d in sorted(pkg_path.iterdir()):
            if d.is_dir() and d.name != "__pycache__":
                sub_files = [f for f in d.glob("*.py")]
                classes = defaultdict(list)
                for pyf in sub_files:
                    try:
                        text = pyf.read_text(encoding="utf-8", errors="ignore")
                        for ln in text.split("\n"):
                            stripped = ln.strip()
                            if stripped.startswith("class "):
                                cls_name = stripped.split("class ", 1)[1].split("(")[0].split(":")[0].strip()
                                if cls_name:
                                    classes[pyf.name].append(cls_name)
                    except Exception:
                        pass
                key_classes = {}
                for fname in sorted(classes.keys()):
                    for cls in classes[fname][:4]:
                        key_classes.setdefault(fname, []).append(cls)
                sub_name = f"agent_harness/{d.name}"
                info[sub_name] = {
                    "file_count": len([f for f in sub_files if f.name != "__init__.py"]),
                    "classes": key_classes,
                }
        # Scan root-level files
        root_files = [f for f in pkg_path.glob("*.py") if f.name != "__init__.py"]
        root_classes = defaultdict(list)
        for pyf in root_files:
            try:
                text = pyf.read_text(encoding="utf-8", errors="ignore")
                for ln in text.split("\n"):
                    stripped = ln.strip()
                    if stripped.startswith("class "):
                        cls_name = stripped.split("class ", 1)[1].split("(")[0].split(":")[0].strip()
                        if cls_name:
                            root_classes[pyf.name].append(cls_name)
            except Exception:
                pass
        root_key = {}
        for fname in sorted(root_classes.keys()):
            for cls in root_classes[fname][:4]:
                root_key.setdefault(fname, []).append(cls)
        info["agent_harness/root"] = {"file_count": len(root_files), "classes": root_key}
        return info

    mod_info = {}
    # 1. modules/
    if (PROJECT_ROOT / "modules").exists():
        mod_info.update(scan_package(PROJECT_ROOT / "modules"))
    # 2. agent_harness/ (top-level orchestration)
    if (PROJECT_ROOT / "agent_harness").exists():
        mod_info.update(scan_agent_harness(PROJECT_ROOT / "agent_harness"))
    # 3. data_models/
    if (PROJECT_ROOT / "data_models").exists():
        mod_info.update(scan_package(PROJECT_ROOT / "data_models"))
    # 4. enums/
    if (PROJECT_ROOT / "enums").exists():
        mod_info.update(scan_package(PROJECT_ROOT / "enums"))

    mod = mod_info
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def mod_table_rows(mod_keys):
        rows = []
        for key in mod_keys:
            if key not in mod:
                continue
            info = mod[key]
            classes_str = ""
            for fname, cls_list in sorted(info["classes"].items()):
                classes_str += ", ".join(cls_list) + "; "
            classes_str = classes_str.rstrip("; ")
            if classes_str:
                rows.append(f"| **{key}/** | {info['file_count']} | {classes_str[:200]} |")
            else:
                rows.append(f"| **{key}/** | {info['file_count']} | (util/constantes) |")
        return "\n".join(rows)

    core_mods = ["scrapers", "data_validation", "financial_engine", "orchestration_v4", "onboarding"]
    analysis_mods = ["auditors", "analyzers", "providers"]
    generation_mods = ["commercial_documents", "asset_generation", "delivery", "generators", "geo_enrichment"]
    data_mods = ["analytics", "deployer"]
    quality_mods = ["quality_gates"]
    util_mods = ["utils", "monitoring", "validation"]
    top_level_mods = ["agent_harness/root", "agent_harness/core", "agent_harness/memory",
                      "agent_harness/observer", "agent_harness/self_healer", "agent_harness/skill_router",
                      "agent_harness/skill_executor", "agent_harness/types", "agent_harness/mcp_client"]

    modules_count = sum(1 for k in mod if k not in top_level_mods)
    top_level_count = sum(1 for k in mod if k in top_level_mods)
    total_files = sum(i['file_count'] for i in mod.values())

    tables = mod_table_rows(core_mods)
    tables2 = mod_table_rows(analysis_mods)
    tables3 = mod_table_rows(generation_mods)
    tables4 = mod_table_rows(data_mods)
    tables5 = mod_table_rows(quality_mods)
    tables6 = mod_table_rows(util_mods)
    tables7 = mod_table_rows(top_level_mods)

    # Get agent_harness version from __init__.py
    harness_version = "unknown"
    harness_init = PROJECT_ROOT / "agent_harness" / "__init__.py"
    if harness_init.exists():
        try:
            text = harness_init.read_text()
            for line in text.split("\n"):
                if line.startswith("__version__"):
                    harness_version = line.split("=")[1].strip().strip('"').strip("'")
                    break
        except Exception:
            pass

    all_mods = sorted(mod.keys())
    pipeline_stages = " -> ".join([m for m in all_mods if m not in ("utils", "validation")])

    content = f"""# Domain Primer - IA Hoteles Agent CLI

> **Proposito**: Base de conocimiento comprimida del dominio "hoteleria digital".
> Consultar para entender conceptos de negocio y su mapeo a codigo.
>
> **Version del sistema**: {version} | **Codename**: {codename}
> **Release date**: {now} | **Plan Maestro**: {plan_maestro}
> **Agent Harness**: v{harness_version}

---

## Modulos del Repositorio (auto-generado)

> {modules_count} modulos detectados en `modules/` + {top_level_count} paquetes de nivel root. {total_files} archivos Python en total.

### CORE - Pipeline de diagnostico

| Modulo | Archivos | Clases/Funciones Clave |
|--------|----------|------------------------|
{tables}

### ANALISIS Y AUDITORIA

| Modulo | Archivos | Clases/Funciones Clave |
|--------|----------|------------------------|
{tables2}

### GENERACION DE CONTENIDO Y ASSETS

| Modulo | Archivos | Clases/Funciones Clave |
|--------|----------|------------------------|
{tables3}

### DATOS EXTERNOS Y DEPLOY

| Modulo | Archivos | Clases/Funciones Clave |
|--------|----------|------------------------|
{tables4}

### QUALITY GATES

| Modulo | Archivos | Clases/Funciones Clave |
|--------|----------|------------------------|
{tables5}

### UTILIDADES Y VALIDACION

| Modulo | Archivos | Clases/Funciones Clave |
|--------|----------|------------------------|
{tables6}

### ORQUESTACION: AGENT HARNESS & PAQUETES ROOT

> Paquetes de primer nivel fuera de `modules/`. Agent Harness es el orquestador de tareas.

| Paquete | Archivos | Clases Clave |
|---------|----------|-------------|
{tables7}

---

## Referencias

- `docs/GUIA_TECNICA.md` - Notas tecnicas y arquitectura
- `docs/contributing/` - Procedimientos de contribucion
- `README.md` - Navegacion rapida del proyecto
- `AGENTS.md` - Contexto global del agente

---

*Auto-generado: {now} | v{version} {codename}*
*Regenerar con: `python scripts/doctor.py --regenerate-domain-primer`*
*NO EDITAR MANUALMENTE - Este archivo se regenera automaticamente desde los modulos del proyecto*
"""

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(content, encoding="utf-8")
    total_classes = sum(
        sum(len(cls_list) for cls_list in info["classes"].values())
        for info in mod.values()
    )
    print(f"[OK] DOMAIN_PRIMER.md regenerado en {target_path.relative_to(PROJECT_ROOT)}")
    print(f"     {total_files} archivos Python, {total_classes} clases en {len(mod)} modulos ({modules_count} en modules/, {top_level_count} root)")
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
    parser.add_argument("--regenerate-domain-primer", action="store_true", help="Regenerate DOMAIN_PRIMER.md from live module data")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.status:
        ok = run_status()
        sys.exit(0 if ok else 1)

    if args.regenerate_domain_primer:
        ok = run_regenerate_domain_primer()
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
