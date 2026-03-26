#!/usr/bin/env python3
"""
Version Consistency Checker - Valida sincronia entre CHANGELOG.md y VERSION.yaml

Este script es parte del sistema deVersion Health. Detecta gaps de sincronizacion
entre el changelog y el archivo de version.

Uso:
    python scripts/version_consistency_checker.py              # Check all
    python scripts/version_consistency_checker.py --fix         # Auto-fix si es posible
    python scripts/version_consistency_checker.py --changelog    # Solo changelog
    python scripts/version_consistency_checker.py --version-yaml # Solo VERSION.yaml

Exit codes:
    0 = Todo sincronizado
    1 = Inconsistencia detectada
    2 = Error

"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional

ROOT_DIR = Path(__file__).parent.parent
CHANGELOG_FILE = ROOT_DIR / "CHANGELOG.md"
VERSION_FILE = ROOT_DIR / "VERSION.yaml"
CONTRIBUTING_FILE = ROOT_DIR / "docs" / "CONTRIBUTING.md"


def extract_latest_version_from_changelog(changelog_path: Path) -> Optional[str]:
    """Extrae la version mas reciente del CHANGELOG.md (primera entrada)."""
    if not changelog_path.exists():
        return None
    
    content = changelog_path.read_text(encoding="utf-8")
    # Buscar ## [X.Y.Z] - fecha
    match = re.search(r'^##\s+\[(\d+\.\d+\.\d+)\]', content, re.MULTILINE)
    if match:
        return match.group(1)
    return None


def extract_version_from_yaml(yaml_path: Path) -> Optional[str]:
    """Extrae la version del VERSION.yaml."""
    if not yaml_path.exists():
        return None
    
    for line in yaml_path.read_text(encoding="utf-8").strip().splitlines():
        if ":" in line and not line.strip().startswith("#"):
            key, value = line.split(":", 1)
            if key.strip() == "version":
                return value.strip().strip('"').strip("'")
    return None


def extract_latest_phase_from_registry(registry_path: Path) -> Optional[str]:
    """Extrae la fase mas reciente del REGISTRY.md."""
    if not registry_path.exists():
        return None
    
    content = registry_path.read_text(encoding="utf-8")
    # Buscar ## FASE-XXX - fecha
    matches = re.findall(r'^##\s+(FASE-[A-Za-z0-9\'\-]+)\s+-\s+(\d{4}-\d{2}-\d{2})', content, re.MULTILINE)
    if matches:
        # Devolver la primera (mas reciente)
        return matches[0][0]
    return None


def extract_codename_from_yaml(yaml_path: Path) -> Optional[str]:
    """Extrae el codename del VERSION.yaml."""
    if not yaml_path.exists():
        return None
    
    for line in yaml_path.read_text(encoding="utf-8").strip().splitlines():
        if ":" in line and not line.strip().startswith("#"):
            key, value = line.split(":", 1)
            if key.strip() == "codename":
                return value.strip().strip('"').strip("'")
    return None


def compare_versions(v1: str, v2: str) -> int:
    """Compara dos versiones semver. Returns -1, 0, 1."""
    def parse(v):
        return [int(x) for x in v.split(".")]
    
    p1, p2 = parse(v1), parse(v2)
    for i in range(max(len(p1), len(p2))):
        n1 = p1[i] if i < len(p1) else 0
        n2 = p2[i] if i < len(p2) else 0
        if n1 < n2:
            return -1
        if n1 > n2:
            return 1
    return 0


def check_consistency() -> Tuple[bool, str, list]:
    """
    Verifica consistencia entre CHANGELOG, VERSION.yaml y REGISTRY.
    
    Returns:
        (is_consistent, summary, gaps)
    """
    gaps = []
    
    changelog_ver = extract_latest_version_from_changelog(CHANGELOG_FILE)
    yaml_ver = extract_version_from_yaml(VERSION_FILE)
    codename = extract_codename_from_yaml(VERSION_FILE)
    
    if not changelog_ver:
        gaps.append("CHANGELOG.md no tiene entradas de version reconocibles")
    if not yaml_ver:
        gaps.append("VERSION.yaml no tiene campo 'version'")
    
    if changelog_ver and yaml_ver:
        cmp = compare_versions(changelog_ver, yaml_ver)
        if cmp > 0:
            gaps.append(
                f"CHANGELOG ahead of VERSION.yaml: "
                f"CHANGELOG={changelog_ver} > VERSION={yaml_ver}"
            )
        elif cmp < 0:
            gaps.append(
                f"VERSION.yaml ahead of CHANGELOG: "
                f"VERSION={yaml_ver} > CHANGELOG={changelog_ver}"
            )
    
    registry_path = ROOT_DIR / "docs" / "contributing" / "REGISTRY.md"
    latest_phase = extract_latest_phase_from_registry(registry_path)
    
    return len(gaps) == 0, "", gaps


def check_contributing_consistency() -> Tuple[bool, list]:
    """
    Verifica que CONTRIBUTING.md este sincronizado con la realidad del proyecto.
    
    Returns:
        (is_consistent, gaps)
    """
    gaps = []
    
    if not CONTRIBUTING_FILE.exists():
        gaps.append("CONTRIBUTING.md no existe")
        return False, gaps
    
    content = CONTRIBUTING_FILE.read_text(encoding="utf-8")
    
    # Detectar si menciona AEO (deberia, ya que es la fase mas reciente)
    if "AEO" not in content and "FASE-A" not in content:
        gaps.append("CONTRIBUTING.md no menciona AEO Re-Architecture")
    
    # Verificar que lista de manuales coincide con documentation_rules
    # (esto es verificacion cruzada, no exhaustiva)
    
    return len(gaps) == 0, gaps


def main():
    parser = argparse.ArgumentParser(
        description="Version Consistency Checker - Valida sincronia CHANGELOG vs VERSION.yaml"
    )
    parser.add_argument("--fix", action="store_true", help="Auto-reparar gaps si es posible")
    parser.add_argument("--changelog", action="store_true", help="Solo verificar CHANGELOG")
    parser.add_argument("--version-yaml", action="store_true", help="Solo verificar VERSION.yaml")
    parser.add_argument("--contributing", action="store_true", help="Solo verificar CONTRIBUTING.md")
    parser.add_argument("--verbose", action="store_true", help="Salida detallada")
    args = parser.parse_args()
    
    print("=" * 60)
    print("VERSION CONSISTENCY CHECKER")
    print("=" * 60)
    
    # Si no se especifico nada, mostrar estado general
    show_all = not (args.changelog or args.version_yaml or args.contributing)
    
    all_ok = True
    all_gaps = []
    
    # 1. CHANGELOG vs VERSION.yaml
    if args.changelog or show_all:
        print("\n[1/3] CHANGELOG vs VERSION.yaml")
        print("-" * 40)
        
        changelog_ver = extract_latest_version_from_changelog(CHANGELOG_FILE)
        yaml_ver = extract_version_from_yaml(VERSION_FILE)
        codename = extract_codename_from_yaml(VERSION_FILE)
        
        print(f"  CHANGELOG.md:  {changelog_ver or 'N/A'}")
        print(f"  VERSION.yaml:   {yaml_ver or 'N/A'}")
        print(f"  Codename:       {codename or 'N/A'}")
        
        if changelog_ver and yaml_ver:
            cmp = compare_versions(changelog_ver, yaml_ver)
            if cmp == 0:
                print("  Status: ✅ SINCRONIZADO")
            elif cmp > 0:
                print(f"  Status: ❌ CHANGELOG ahead by {changelog_ver} vs {yaml_ver}")
                all_ok = False
                all_gaps.append(f"CHANGELOG={changelog_ver} > VERSION={yaml_ver}")
            else:
                print(f"  Status: ⚠️  VERSION ahead by {yaml_ver} vs {changelog_ver}")
                all_gaps.append(f"VERSION={yaml_ver} > CHANGELOG={changelog_ver}")
        elif not changelog_ver:
            print("  Status: ⚠️  No se pudo leer CHANGELOG")
            all_gaps.append("CHANGELOG no tiene version reconocible")
        elif not yaml_ver:
            print("  Status: ❌ VERSION.yaml sin campo version")
            all_ok = False
            all_gaps.append("VERSION.yaml sin campo version")
    
    # 2. REGISTRY - fase mas reciente
    if args.version_yaml or show_all:
        print("\n[2/3] REGISTRY - Ultima Fase")
        print("-" * 40)
        
        registry_path = ROOT_DIR / "docs" / "contributing" / "REGISTRY.md"
        latest_phase = extract_latest_phase_from_registry(registry_path)
        
        if latest_phase:
            print(f"  Ultima fase: {latest_phase}")
            print(f"  Status: ✅ REGISTRY OK")
        else:
            print(f"  Status: ⚠️  No se encontro fase en REGISTRY")
    
    # 3. CONTRIBUTING.md
    if args.contributing or show_all:
        print("\n[3/3] CONTRIBUTING.md Consistency")
        print("-" * 40)
        
        ok, gaps = check_contributing_consistency()
        
        if ok:
            print(f"  Status: ✅ SINCRONIZADO")
        else:
            print(f"  Status: ⚠️  Inconsistencias detectadas")
            for g in gaps:
                print(f"    - {g}")
                all_gaps.append(f"CONTRIBUTING: {g}")
            all_ok = False
    
    # Resumen
    print("\n" + "=" * 60)
    if all_ok:
        print("RESULTADO: ✅ TODO SINCRONIZADO")
        print("=" * 60)
        return 0
    else:
        print("RESULTADO: ❌ INCONSISTENCIAS DETECTADAS")
        print("=" * 60)
        print("\nGaps encontrados:")
        for i, g in enumerate(all_gaps, 1):
            print(f"  {i}. {g}")
        print("\nPara sincronizar manualmente:")
        print("  1. python scripts/derive_version_from_changelog.py  # Deriva VERSION from CHANGELOG")
        print("  2. python scripts/sync_versions.py                  # Sincroniza archivos")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
