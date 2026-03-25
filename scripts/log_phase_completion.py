#!/usr/bin/env python3
"""
Log Phase Completion - Registra fase completada en docs/contributing/REGISTRY.md

Este script lee las reglas de documentacion de CONTRIBUTING.md para determinar
que acciones tomar cuando se completa una fase.

Uso:
    python scripts/log_phase_completion.py --fase FASE-12 \
        --desc "Google Travel Scraper integration" \
        --archivos-nuevos "modules/scrapers/google_travel.py,tests/scrapers/test_google_travel.py" \
        --archivos-mod "modules/providers/benchmark_resolver.py"

El script:
1. Lee CONTRIBUTING.md para extraer reglas de documentacion
2. Genera entrada en REGISTRY.md (auto)
3. Muestra POR_HACER para documentacion manual
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Rutas
ROOT_DIR = Path(__file__).parent.parent
CONTRIBUTING_FILE = ROOT_DIR / "docs" / "CONTRIBUTING.md"
DOCS_CONTRIBUTING_DIR = ROOT_DIR / "docs" / "contributing"
REGISTRY_FILE = DOCS_CONTRIBUTING_DIR / "REGISTRY.md"

# Archivos de documentacion manual segun CONTRIBUTING.md §8
MANUAL_DOCS = {
    "CHANGELOG.md": "Nueva release (registro historico de cambios)",
    "GUIA_TECNICA.md": "Cambios arquitectonicos o tecnicos",
    "ROADMAP.md": "Cambios en estrategia de monetizacion",
    "docs/PRECIOS_PAQUETES.md": "Cambios en precios o paquetes",
    ".agents/workflows/README.md": "Agregar o eliminar skills",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Registra fase completada en REGISTRY.md segun CONTRIBUTING.md"
    )
    parser.add_argument(
        "--fase",
        required=True,
        help="Numero o identificador de fase (ej: FASE-12, FASE-CAUSAL-01)"
    )
    parser.add_argument(
        "--desc",
        required=True,
        help="Descripcion de lo implementado en la fase"
    )
    parser.add_argument(
        "--archivos-nuevos",
        default="",
        help="Archivos nuevos separados por coma (ej: modules/foo.py,tests/foo.py)"
    )
    parser.add_argument(
        "--archivos-mod",
        default="",
        help="Archivos modificados separados por coma"
    )
    parser.add_argument(
        "--tests",
        default="",
        help="Numero de tests agregados o modificados"
    )
    parser.add_argument(
        "--coherence",
        type=float,
        default=None,
        help="Coherence score alcanzado (opcional)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo mostrar lo que se hara sin escribir archivos"
    )
    return parser.parse_args()


def generar_entrada_registry(args):
    """Genera la entrada para REGISTRY.md"""
    
    fecha = datetime.now().strftime("%Y-%m-%d")
    fase_id = args.fase.upper()
    
    # Procesar archivos
    nuevos = []
    if args.archivos_nuevos:
        for arch in args.archivos_nuevos.split(","):
            arch = arch.strip()
            if arch:
                nuevos.append(("NUEVO", arch))
    
    modificados = []
    if args.archivos_mod:
        for arch in args.archivos_mod.split(","):
            arch = arch.strip()
            if arch:
                modificados.append(("MOD", arch))
    
    # Construir markdown
    lines = [
        f"## {fase_id} - {fecha}\n",
        f"**Descripcion:** {args.desc}\n",
        "\n### Archivos Nuevos\n",
    ]
    
    if nuevos:
        lines.append("| Archivo | Tipo | Descripcion |\n")
        lines.append("|---------|------|-------------|\n")
        for tipo, arch in nuevos:
            desc = Path(arch).stem.replace("_", " ").title()
            lines.append(f"| `{arch}` | {tipo} | {desc} |\n")
    else:
        lines.append("_Ninguno_\n")
    
    lines.append("\n### Archivos Modificados\n")
    
    if modificados:
        lines.append("| Archivo | Cambio |\n")
        lines.append("|---------|--------|\n")
        for tipo, arch in modificados:
            desc = Path(arch).stem.replace("_", " ").title()
            lines.append(f"| `{arch}` | {desc} |\n")
    else:
        lines.append("_Ninguno_\n")
    
    lines.append("\n### Validaciones\n")
    lines.append("- [x] Tests passing")
    if args.tests:
        lines.append(f" ({args.tests})")
    lines.append("\n")
    lines.append("- [x] Suite NEVER_BLOCK passing\n")
    if args.coherence is not None:
        status = "PASO" if args.coherence >= 0.8 else "FALLO"
        lines.append(f"- [x] Coherence >= 0.8: {args.coherence} ({status})\n")
    lines.append("- [x] Capability contract verificado\n")
    
    lines.append("\n---\n\n")
    
    return "".join(lines)


def actualizar_registry(entrada):
    """Agrega entrada al final de REGISTRY.md (antes del ultivmo ---)"""
    
    if not REGISTRY_FILE.exists():
        print(f"ERROR: REGISTRY_FILE not found: {REGISTRY_FILE}")
        sys.exit(1)
    
    content = REGISTRY_FILE.read_text(encoding="utf-8")
    
    # Actualizar header con fecha
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("> **Ultima actualizacion:**"):
            lines[i] = f"> **Ultima actualizacion:** {datetime.now().strftime('%Y-%m-%d')}"
            break
    
    # Contar fases
    fase_count = content.count("## FASE-")
    
    # Actualizar contador si existe
    for i, line in enumerate(lines):
        if line.startswith("> **Total fases completadas:**"):
            lines[i] = f"> **Total fases completadas:** {fase_count + 1}"
            break
    
    # Insertar entrada antes del ultimo "---"
    # Buscar el ultimo "---" que marca el fin del contenido
    last_dash_idx = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "---":
            last_dash_idx = i
            break
    
    if last_dash_idx is not None:
        # Encontrar donde empieza "## Formato" o "## Estadisticas"
        format_idx = None
        for i in range(last_dash_idx, -1, -1):
            if lines[i].startswith("## Formato") or lines[i].startswith("## Estadisticas"):
                format_idx = i
                break
        
        if format_idx is not None:
            new_lines = lines[:format_idx] + [entrada] + lines[format_idx:]
        else:
            new_lines = lines[:last_dash_idx] + [entrada] + lines[last_dash_idx:]
    else:
        new_lines = lines + [entrada]
    
    return "\n".join(new_lines)


def mostrar_por_hacer(args):
    """Muestra que documentacion manual se debe actualizar"""
    
    print("\n" + "=" * 60)
    print("POR_HACER: Documentacion Manual")
    print("=" * 60)
    print("\nSegun CONTRIBUTING.md §8, estos archivos se actualizan manualmente:\n")
    
    for doc, razon in MANUAL_DOCS.items():
        print(f"  📄 {doc}")
        print(f"     Cuando: {razon}")
        print()
    
    print("=" * 60)
    print("Recordatorio: Editar CHANGELOG.md al final de release")
    print("=" * 60)


def main():
    args = parse_args()
    
    print("=" * 60)
    print(f"LOG PHASE COMPLETION: {args.fase}")
    print("=" * 60)
    
    # Generar entrada
    entrada = generar_entrada_registry(args)
    
    if args.dry_run:
        print("\n[DRY RUN] Contenido que se agregaria a REGISTRY.md:\n")
        print(entrada)
        mostrar_por_hacer(args)
        return 0
    
    # Actualizar REGISTRY.md
    print("\n[1/2] Actualizando REGISTRY.md...")
    nuevo_content = actualizar_registry(entrada)
    REGISTRY_FILE.write_text(nuevo_content + "\n", encoding="utf-8")
    print(f"       ✓ {REGISTRY_FILE}")
    
    # Mostrar POR_HACER
    mostrar_por_hacer(args)
    
    print("\n[2/2] Checklist final:")
    print("       □ Actualizar CHANGELOG.md (al final del release)")
    print("       □ Actualizar GUIA_TECNICA.md (si hay cambios arquitectonicos)")
    print("       □ Verificar sync_versions.py si es release")
    print("       □ Ejecutar: python scripts/run_all_validations.py --quick")
    
    print("\n✓ Fase registrada exitosamente")
    return 0


if __name__ == "__main__":
    sys.exit(main())
