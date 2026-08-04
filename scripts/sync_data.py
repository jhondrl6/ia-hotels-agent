#!/usr/bin/env python3
"""
sync_data.py — Sincroniza datos numéricos entre documentos.

Similar a sync_versions.py pero para métricas que cambian frecuentemente:
test_count, module_count, skill_count. Inyecta los valores reales en
AGENTS.md y README.md, eliminando el reproceso manual de corrección.

Uso:
    python scripts/sync_data.py
    python scripts/sync_data.py --dry-run   # Muestra cambios sin aplicar
"""

import sys
import re
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent


def get_test_count() -> int:
    """Obtiene el test count real via pytest --collect-only."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", str(ROOT / "tests")],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    match = re.search(r"(\d+) tests? collected", result.stdout)
    if match:
        return int(match.group(1))
    # Fallback: buscar en stderr (pytest puede escribir warnings ahí)
    match = re.search(r"(\d+) tests? collected", result.stderr)
    if match:
        return int(match.group(1))
    raise RuntimeError(f"No se pudo obtener test_count. stdout={result.stdout[:200]}")


def get_module_count() -> int:
    """Cuenta archivos .py en modules/ (excluyendo __pycache__)."""
    modules_dir = ROOT / "modules"
    if not modules_dir.exists():
        return 0
    return len([
        f for f in modules_dir.rglob("*.py")
        if "__pycache__" not in str(f)
    ])


def get_skill_count() -> int:
    """Cuenta skills .md en .agents/workflows/ (excluyendo README.md)."""
    workflows_dir = ROOT / ".agents" / "workflows"
    if not workflows_dir.exists():
        return 0
    return len([
        f for f in workflows_dir.glob("*.md")
        if f.name != "README.md"
    ])


def format_number(n: int) -> str:
    """Formatea número con coma: 3215 → '3,215'."""
    return f"{n:,}"


def sync_agents_md(test_count: int, module_count: int, skill_count: int, dry_run: bool) -> list:
    """Sincroniza datos en AGENTS.md. Retorna lista de cambios aplicados."""
    path = ROOT / "AGENTS.md"
    content = path.read_text(encoding="utf-8")
    original = content
    changes = []

    # Pattern: "3,215 funciones" (test count total)
    new_text = format_number(test_count)
    content = re.sub(
        r"\d{1,3},\d{3}\s+funciones",
        f"{new_text} funciones",
        content,
    )
    
    if content != original:
        changes.append(f"AGENTS.md: test_count → {new_text}")
        if not dry_run:
            path.write_text(content, encoding="utf-8")

    return changes


def sync_readme_md(test_count: int, module_count: int, skill_count: int, dry_run: bool) -> list:
    """Sincroniza datos en README.md. Retorna lista de cambios aplicados."""
    path = ROOT / "README.md"
    content = path.read_text(encoding="utf-8")
    original = content
    changes = []
    new_text = format_number(test_count)

    # Pattern: "3,215 test functions" (mantener formato)
    content = re.sub(
        r"\d{1,3},\d{3}\s+test\s+functions",
        f"{new_text} test functions",
        content,
    )

    # Pattern: "3,215 pruebas automatizadas" (mantener formato)
    content = re.sub(
        r"\d{1,3},\d{3}\s+pruebas\s+automatizadas",
        f"{new_text} pruebas automatizadas",
        content,
    )

    # Pattern: "205 archivos Python en modules/"
    content = re.sub(
        r"\d+\s+archivos\s+Python\s+en\s+modules/",
        f"{module_count} archivos Python en modules/",
        content,
    )

    # Pattern: "16 agent skills"
    content = re.sub(
        r"\d+\s+agent\s+skills",
        f"{skill_count} agent skills",
        content,
    )

    if content != original:
        changes.append(f"README.md: test={new_text}, modules={module_count}, skills={skill_count}")
        if not dry_run:
            path.write_text(content, encoding="utf-8")

    return changes


def main():
    dry_run = "--dry-run" in sys.argv

    print("=" * 60)
    print("SYNC DATA — Sincronización de datos numéricos")
    print("=" * 60)
    if dry_run:
        print("[DRY-RUN] No se aplicarán cambios.\n")

    # Colectar datos reales
    print("[1/3] Colectando datos reales...")
    test_count = get_test_count()
    module_count = get_module_count()
    skill_count = get_skill_count()
    print(f"  test_count:   {test_count:,}")
    print(f"  module_count: {module_count}")
    print(f"  skill_count:  {skill_count}")

    # Inyectar en documentos
    print("\n[2/3] Sincronizando AGENTS.md...")
    agents_changes = sync_agents_md(test_count, module_count, skill_count, dry_run)
    for c in agents_changes:
        print(f"  ✓ {c}")
    if not agents_changes:
        print("  → Sin cambios (ya sincronizado)")

    print("\n[3/3] Sincronizando README.md...")
    readme_changes = sync_readme_md(test_count, module_count, skill_count, dry_run)
    for c in readme_changes:
        print(f"  ✓ {c}")
    if not readme_changes:
        print("  → Sin cambios (ya sincronizado)")

    # Resumen
    print("\n" + "=" * 60)
    total = len(agents_changes) + len(readme_changes)
    if total == 0:
        print("RESULTADO: ✅ Todo sincronizado (sin cambios necesarios)")
    else:
        print(f"RESULTADO: ✅ {total} cambio(s) aplicado(s)")
    print("=" * 60)


if __name__ == "__main__":
    main()
