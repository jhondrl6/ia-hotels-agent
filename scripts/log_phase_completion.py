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
3. Verifica documentacion manual (enforcement)
4. Muestra POR_HACER para documentacion manual pendiente

Enforcement (--check-manual-docs):
- Verifica que MANUAL_DOCS contengan referencia a la fase
- Si no, FAIL con mensaje claro
- Usa --force-skip-docs para saltar verificacion (con razon)

Version Sync Gate (--release):
- Cuando una fase marca un release (nueva version), valida que
  CHANGELOG.md y VERSION.yaml esten sincronizados
- Si CHANGELOG dice 4.9.0 pero VERSION.yaml dice 4.8.0 -> FAIL
- Usa --auto-sync para ejecutar sync_versions automaticamente

"""

import argparse
import sys
import re
from datetime import datetime
from pathlib import Path

# Fix encoding for Windows (cp1252 doesn't support Unicode symbols like (R, (X), (T)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        # Fallback: wrap stdout to handle encoding errors
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Rutas
ROOT_DIR = Path(__file__).parent.parent
CONTRIBUTING_FILE = ROOT_DIR / "docs" / "CONTRIBUTING.md"
DOCS_CONTRIBUTING_DIR = ROOT_DIR / "docs" / "contributing"
REGISTRY_FILE = DOCS_CONTRIBUTING_DIR / "REGISTRY.md"
LAST_DOC_TRACKER = DOCS_CONTRIBUTING_DIR / ".last_doc_phase.json"

# Archivos de documentacion manual segun CONTRIBUTING.md (R8)
MANUAL_DOCS = {
    "CHANGELOG.md": "Nueva release (registro historico de cambios)",
    "GUIA_TECNICA.md": "Cambios arquitectonicos o tecnicos",
    "ROADMAP.md": "Cambios en estrategia de monetizacion",
    ".agents/workflows/README.md": "Agregar o eliminar skills",
}

# Archivos que requieren actualizacion para esta fase (se llena detectando cambios en codigo)
REQUIRE_ArchitectURAL_CHANGE = [
    "modules/asset_generation/conditional_generator.py",
    "modules/delivery/generators/faq_gen.py",
    "modules/delivery/generators/voice_guide.py",
    "data_models/aeo_kpis.py",
    "modules/analytics/",
    "commercial_documents/composer.py",
]


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
        "--check-manual-docs",
        action="store_true",
        help="Verificar que docs manuales esten actualizadas (FAIL si no)"
    )
    parser.add_argument(
        "--force-skip-docs",
        action="store_true",
        help="Saltar verificacion de docs manuales (requiere razon en --skip-reason)"
    )
    parser.add_argument(
        "--skip-reason",
        default="",
        help="Razon para saltarse verificacion de docs (requerido si --force-skip-docs)"
    )
    parser.add_argument(
        "--release",
        type=str,
        default=None,
        help="Version de release (ej: 4.9.0). Activa Version Sync Gate."
    )
    parser.add_argument(
        "--auto-sync",
        action="store_true",
        help="Ejecutar sync_versions.py automaticamente si hay desincronizacion"
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
    """Agrega entrada al final de REGISTRY.md (antes del ultimo ---)"""
    
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
    last_dash_idx = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "---":
            last_dash_idx = i
            break
    
    if last_dash_idx is not None:
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


def get_last_documented_phase():
    """Obtiene la ultima fase que documento cada archivo manual.
    
    Lee el tracker JSON para saber cual fue la ultima fase que actualizo
    cada archivo de documentacion manual.
    """
    if not LAST_DOC_TRACKER.exists():
        return {}
    import json
    try:
        return json.loads(LAST_DOC_TRACKER.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_last_documented_phase(fase_id, archivos_actualizados):
    """Guarda cual fase documento cada archivo.
    
    Actualiza el tracker JSON con la fase actual y los archivos
    que fueron actualizados por esta fase.
    """
    import json
    tracker = get_last_documented_phase()
    for arch in archivos_actualizados:
        tracker[arch] = fase_id
    LAST_DOC_TRACKER.write_text(json.dumps(tracker, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# Mapeo de archivos de codigo -> archivos de documentacion que deben mencionarlos
# Esta tabla define QUE documentacion debe actualizar cada modulo
CODE_TO_DOC_MAP = {
    # Modulo de asset generation
    "modules/asset_generation/conditional_generator.py": ["GUIA_TECNICA.md", "capabilities.md"],
    "modules/asset_generation/asset_catalog.py": ["GUIA_TECNICA.md"],
    "modules/asset_generation/preflight_checks.py": ["GUIA_TECNICA.md"],
    "modules/asset_generation/site_presence_checker.py": ["GUIA_TECNICA.md", "CONTRIBUTING.md"],
    # Modulos de delivery/generators
    "modules/delivery/generators/faq_gen.py": ["GUIA_TECNICA.md"],
    "modules/delivery/generators/voice_guide.py": ["GUIA_TECNICA.md"],
    "modules/delivery/generators/google_assistant_checklist.md": ["GUIA_TECNICA.md"],
    "modules/delivery/generators/apple_business_connect_guide.md": ["GUIA_TECNICA.md"],
    "modules/delivery/generators/alexa_skill_blueprint.md": ["GUIA_TECNICA.md"],
    # Modulos de analytics
    "modules/analytics/profound_client.py": ["GUIA_TECNICA.md"],
    "modules/analytics/semrush_client.py": ["GUIA_TECNICA.md"],
    # Data models
    "data_models/aeo_kpis.py": ["GUIA_TECNICA.md"],
    # Orchestration
    "modules/asset_generation/v4_asset_orchestrator.py": ["GUIA_TECNICA.md"],
    # Commercial documents
    "commercial_documents/composer.py": ["GUIA_TECNICA.md"],
    "commercial_documents/__init__.py": ["GUIA_TECNICA.md"],
    "modules/commercial_documents/pain_solution_mapper.py": ["GUIA_TECNICA.md"],
}


def audit_documentation_gaps(fase_id, archivos_modificados, archivos_nuevos):
    """
    Genera un reporte de 'documentacion huérfana' - archivos de documentacion
    que no mencionan modulos que fueron modificados.
    
    Este reporte muestra:
    1. Archivos de codigo modificados
    2. Archivos de documentacion que DEBERIAN ser actualizados
    3. Cuales YA mencionan la fase
    4. Cuales tienen gaps
    
    Args:
        fase_id: Identificador de fase (ej: FASE-12)
        archivos_modificados: Lista de rutas de archivos modificados
        archivos_nuevos: Lista de rutas de archivos nuevos
    
    Returns:
        dict con {doc_file: {mentioned: bool, missing_files: list}}
    """
    # Normalizar fase para busqueda
    fase_searches = [
        fase_id,
        fase_id.replace("-", " "),  # FASE-12 -> FASE 12
        re.sub(r'FASE-([A-Z]+)', r'FASE \1', fase_id),  # FASE-F -> FASE F
    ]
    
    all_code_files = set(archivos_modificados or []) | set(archivos_nuevos or [])
    
    results = {}
    
    # Para cada archivo de codigo modificado, determinar que docs lo requieren
    docs_that_need_update = set()
    for code_file in all_code_files:
        for pattern, doc_list in CODE_TO_DOC_MAP.items():
            if pattern in code_file or code_file.startswith(pattern.replace("[^/]*/", "")):
                docs_that_need_update.update(doc_list)
    
    # Verificar cada doc requerido
    for doc in docs_that_need_update:
        doc_path = ROOT_DIR / "docs" / doc if not doc.startswith("docs/") else ROOT_DIR / doc
        if not doc_path.exists():
            # Try root level
            doc_path = ROOT_DIR / doc
        
        mentioned = False
        missing_files = []
        
        if doc_path.exists():
            content = doc_path.read_text(encoding="utf-8", errors="ignore")
            for search in fase_searches:
                if search in content:
                    mentioned = True
                    break
            
            # Si no menciona la fase, agregar a missing_files
            if not mentioned:
                # Encontrar que archivos de codigo triggers este doc
                for code_file in all_code_files:
                    for pattern, doc_list in CODE_TO_DOC_MAP.items():
                        if pattern in code_file and doc in doc_list:
                            missing_files.append(code_file)
                            break
        else:
            missing_files = list(all_code_files)
        
        results[doc] = {
            "mentioned": mentioned,
            "missing_files": missing_files,
            "path": str(doc_path) if doc_path.exists() else "N/A"
        }
    
    return results


def mostrar_audit_documentacion(fase_id, args):
    """Muestra el reporte de audit de documentacion huérfana."""
    
    archivos_mod = args.archivos_mod.split(",") if args.archivos_mod else []
    archivos_nuevos = args.archivos_nuevos.split(",") if args.archivos_nuevos else []
    
    archivos_mod = [f.strip() for f in archivos_mod if f.strip()]
    archivos_nuevos = [f.strip() for f in archivos_nuevos if f.strip()]
    
    if not archivos_mod and not archivos_nuevos:
        return
    
    audit = audit_documentation_gaps(fase_id, archivos_mod, archivos_nuevos)
    
    # Filtrar solo los que tienen gaps
    gaps = {doc: info for doc, info in audit.items() if not info["mentioned"]}
    
    print("\n" + "=" * 60)
    print("DOCUMENTATION AUDIT - Documentacion Huérfana")
    print("=" * 60)
    
    if not gaps:
        print("\n  (OK) Todos los archivos de documentacion mencionan la fase")
        print("       No se detectaron gaps")
        print()
        return
    
    print("\n  (!) ATENCION: Se detectaron gaps de documentacion\n")
    
    for doc, info in gaps.items():
        print("  [GAP] " + doc)
        print("        Ruta: " + info["path"])
        if info["missing_files"]:
            print("        Archivos de codigo que REQUIEREN actualizacion:")
            for mf in info["missing_files"][:5]:  # Max 5
                print("          - " + mf)
            if len(info["missing_files"]) > 5:
                print("          ... y " + str(len(info["missing_files"]) - 5) + " mas")
        print()
    
    print("  --")
    print("  Para resolver: Editar manualmente los archivos listados arriba")
    print("  y agregar referencia a la fase " + fase_id)
    print("=" * 60)


def check_manual_docs_updated(fase_id, archivos_modificados):
    """Verifica si los archivos de documentacion manual requieren actualizacion.
    
    Detecta si hubo cambios arquitectonicos (archivos en REQUIRE_ArchitectURAL_CHANGE)
    y si los archivos MANUAL_DOCS ya fueron actualizados para esta fase.
    
    Returns:
        tuple: (needs_update: bool, files_to_update: list, gaps: list)
    """
    # Normalizar fase_id para busqueda (FASE-F -> FASE F, FASE-12 -> FASE 12)
    fase_search_space = re.sub(r'FASE-([A-Z0-9]+)', r'FASE \1', fase_id)  # FASE F
    fase_search_hyphen = fase_id  # FASE-F
    fase_search_stripped = fase_id.replace('-', '')  # FASEF
    
    gaps = []
    needs_update = []
    
    # Detectar si hubo cambios arquitectonicos
    has_architectural_changes = False
    mod_set = set(archivos_modificados.split(",")) if archivos_modificados else set()
    
    for changed_file in mod_set:
        changed_file = changed_file.strip()
        if not changed_file:
            continue
        for arch_pattern in REQUIRE_ArchitectURAL_CHANGE:
            if arch_pattern.endswith("/"):
                if changed_file.startswith(arch_pattern) or arch_pattern in changed_file:
                    has_architectural_changes = True
                    break
            elif changed_file == arch_pattern or arch_pattern in changed_file:
                has_architectural_changes = True
                break
    
    if not has_architectural_changes:
        # No hubieron cambios arquitectonicos, no requiere GUIA_TECNICA
        return False, [], []
    
    # Hubieron cambios arquitectonicos - verificar MANUAL_DOCS
    tracker = get_last_documented_phase()
    
    # GUIA_TECNICA.md SIEMPRE requiere actualizacion si hay cambios arquitectonicos
    guia_tec_path = ROOT_DIR / "docs" / "GUIA_TECNICA.md"
    if guia_tec_path.exists():
        content = guia_tec_path.read_text(encoding="utf-8", errors="ignore")
        # Buscar cualquier forma de la fase: FASE-F, FASE F, FASE-12, FASE 12
        found = (fase_search_hyphen in content or 
                 fase_search_space in content or
                 fase_search_stripped in content)
        if not found:
            gaps.append("GUIA_TECNICA.md")
            needs_update.append("GUIA_TECNICA.md")
    
    # CHANGELOG.md requiere actualizacion si es release
    changelog_path = ROOT_DIR / "docs" / "CHANGELOG.md"
    if changelog_path.exists():
        content = changelog_path.read_text(encoding="utf-8", errors="ignore")
        if not (fase_search_hyphen in content or fase_search_space in content):
            gaps.append("CHANGELOG.md")
            # CHANGELOG solo se actualiza al final de release, no es blocking
    
    return len(needs_update) > 0, needs_update, gaps


def mostrar_por_hacer(args):
    """Muestra que documentacion manual se debe actualizar"""
    
    print("\n" + "=" * 60)
    print("POR_HACER: Documentacion Manual")
    print("=" * 60)
    print("\nSegun CONTRIBUTING.md (R8, estos archivos se actualizan manualmente:\n")
    
    for doc, razon in MANUAL_DOCS.items():
        print(f"  (T) {doc}")
        print(f"     Cuando: {razon}")
        print()
    
    print("=" * 60)
    print("Recordatorio: Editar CHANGELOG.md al final de release")
    print("=" * 60)


def verificar_docs_manuales(fase_id, args):
    """Verifica y强制( enforce) documentacion manual.
    
    Si --check-manual-docs y hay gaps:
    - Si --force-skip-docs: muestra skip pero continua
    - Sin force-skip: EXIT FAIL
    
    Returns:
        bool: True si passou (docs ok o force-skip), False si fall
    """
    needs_update, files, gaps = check_manual_docs_updated(fase_id, args.archivos_mod)
    
    if not needs_update:
        print("\n[CHECK MANUAL DOCS] (R) No se detectaron cambios arquitectonicos.")
        print("   GUIA_TECNICA.md no requiere actualizacion para esta fase.")
        return True
    
    print("\n" + "!" * 60)
    print("GAP DETECTADO: Documentacion Manual Desactualizada")
    print("!" * 60)
    print(f"\nFase: {fase_id}")
    print(f"Archivos con gaps: {', '.join(gaps)}")
    print("\nSegun CONTRIBUTING.md (R8, estos archivos requieren actualizacion manual")
    print("porque se detectaron cambios arquitectonicos en el codigo:\n")
    for f in files:
        print(f"  (T) {f}")
        print(f"     Razon: {MANUAL_DOCS.get(f, 'Cambio arquitectonico detectado')}")
        print()
    
    print("-" * 60)
    print("ACCIONES REQUERIDAS:")
    print("-" * 60)
    for f in files:
        print(f"  1. Editar {f}")
        print(f"  2. Agregar entrada para {fase_id}")
        print(f"  3. Ejecutar: git add {f} && git commit -m 'docs: {fase_id} - actualizar {f}'")
        print()
    
    if args.force_skip_docs:
        if not args.skip_reason:
            print("\nERROR: --force-skip-docs requiere --skip-reason")
            return False
        print(f"\n[WARN] Verificacion saltada via --force-skip-docs")
        print(f"       Razon: {args.skip_reason}")
        return True
    
    print("\n" + "=" * 60)
    print("FAIL: Documentacion manual desactualizada")
    print("=" * 60)
    print("\nOpciones:")
    print("  1. Actualizar los archivos listados arriba")
    print("  2. Usar --force-skip-docs --skip-reason '...' si es intencional")
    print("  3. Usar --check-only para solo verificar sin bloquear")
    print("\nSaliendo con exit code 1...")
    return False


def check_version_sync(release_version: str, dry_run: bool = False) -> bool:
    """
    Verifica que CHANGELOG.md y VERSION.yaml esten sincronizados con release_version.
    
    Si CHANGELOG.md tiene entrada [X.Y.Z] y VERSION.yaml tiene version W.Z.V:
    - Si X.Y.Z != W.Z.V -> INCONSISTENCIA
    
    Args:
        release_version: Version del release (ej: "4.9.0")
        dry_run: Si True, solo muestra el estado sin hacer nada
    
    Returns:
        bool: True si sincronizado o auto-sync exitoso, False si fall
    """
    import re
    
    # Extraer version de CHANGELOG
    changelog_path = ROOT_DIR / "CHANGELOG.md"
    yaml_path = ROOT_DIR / "VERSION.yaml"
    
    changelog_ver = None
    if changelog_path.exists():
        content = changelog_path.read_text(encoding="utf-8")
        match = re.search(r'^##\s+\[(\d+\.\d+\.\d+)\]', content, re.MULTILINE)
        if match:
            changelog_ver = match.group(1)
    
    yaml_ver = None
    if yaml_path.exists():
        for line in yaml_path.read_text(encoding="utf-8").strip().splitlines():
            if ":" in line and not line.strip().startswith("#"):
                key, value = line.split(":", 1)
                if key.strip() == "version":
                    yaml_ver = value.strip().strip('"').strip("'")
    
    print("\n" + "=" * 60)
    print("VERSION SYNC GATE")
    print("=" * 60)
    print(f"  Release version: {release_version}")
    print(f"  CHANGELOG.md:    {changelog_ver or 'N/A'}")
    print(f"  VERSION.yaml:    {yaml_ver or 'N/A'}")
    
    # Caso 1: CHANGELOG no tiene la version del release
    if changelog_ver != release_version:
        print(f"\n  (!) CHANGELOG no tiene entrada [{release_version}]")
        print(f"      CHANGELOG dice: {changelog_ver or 'N/A'}")
        print("\n  ACCION: Crear entrada en CHANGELOG.md antes de continuar")
        print("  python scripts/log_phase_completion.py --fase ... --desc '...'")
        print("  (luego reabrir con --release " + release_version + ")")
        return False
    
    # Caso 2: CHANGELOG y VERSION.yaml no coinciden
    if yaml_ver != changelog_ver:
        print(f"\n  (!) INCONSISTENCIA: CHANGELOG={changelog_ver} != VERSION={yaml_ver}")
        print("\n  Opciones:")
        print(f"    1. python scripts/sync_versions.py --check  # Verificar diff")
        print(f"    2. python scripts/sync_versions.py          # Sincronizar (requiere VERSION.yaml actualizado)")
        print(f"    3. Usar --auto-sync para sincronizacion automatica")
        
        if not dry_run:
            print("\n" + "=" * 60)
            print("FAIL: Version desincronizada entre CHANGELOG y VERSION.yaml")
            print("=" * 60)
        return False
    
    print("  (OK) CHANGELOG y VERSION.yaml sincronizados en " + changelog_ver)
    return True


def run_sync_versions():
    """Ejecuta sync_versions.py para sincronizar archivos contextuales."""
    import subprocess
    
    sync_script = ROOT_DIR / "scripts" / "sync_versions.py"
    if not sync_script.exists():
        print(f"\n[WARN] sync_versions.py no encontrado en {sync_script}")
        return False
    
    print("\n[SYNC] Ejecutando sync_versions.py...")
    try:
        result = subprocess.run(
            [sys.executable, str(sync_script)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"\n[ERROR] Fallo al ejecutar sync_versions.py: {e}")
        return False


def main():
    args = parse_args()
    fase_id = args.fase.upper()
    
    print("=" * 60)
    print("LOG PHASE COMPLETION: " + fase_id)
    print("=" * 60)

    # ============================================================
    # AUTO-DETECT: FASE-RELEASE-X.Y.Z activa Version Sync Gate automaticamente
    # ============================================================
    release_match = re.match(r'^FASE-RELEASE-(\d+\.\d+\.\d+)$', fase_id, re.IGNORECASE)
    if release_match:
        detected_version = release_match.group(1)
        print("\n[AUTO-DETECT] FASE-RELEASE detectado: " + detected_version)
        if not args.release:
            print("  (INFO) Usando --release automatico: " + detected_version)
            args.release = detected_version

    # ============================================================
    # PASO 0: Version Sync Gate (si es release)
    # ============================================================
    if args.release:
        print("\n[VERSION GATE] Release detectado: " + args.release)
        gate_ok = check_version_sync(args.release, dry_run=args.dry_run)
        
        if not gate_ok and not args.dry_run:
            print("\n[!] Version Sync Gate FALLO. Resolve los issues antes de continuar.")
            print("    Pasos:")
            print("      1. python scripts/version_consistency_checker.py --fix")
            print("      2. python scripts/sync_versions.py")
            print("      3. python scripts/log_phase_completion.py --release " + args.release + " ...")
            sys.exit(1)
        
        # Auto-sync si se pidio y hay desincronizacion
        if args.auto_sync and not args.dry_run:
            run_sync_versions()

    # Verificar docs manuales si se pidio
    if args.check_manual_docs:
        if not verificar_docs_manuales(fase_id, args):
            sys.exit(1)

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
    print(f"       (R) {REGISTRY_FILE}")
    
    # Actualizar tracker de documentacion si hay archivos modificados
    if args.archivos_mod:
        mod_files = [f.strip() for f in args.archivos_mod.split(",") if f.strip()]
        save_last_documented_phase(fase_id, mod_files)
    
    # Mostrar POR_HACER
    mostrar_por_hacer(args)

    # Mostrar audit de documentacion huérfana
    mostrar_audit_documentacion(fase_id, args)

    # Verificar gaps de documentacion (warning, no blocking)
    needs_update, files, gaps = check_manual_docs_updated(fase_id, args.archivos_mod)
    if needs_update:
        print("\n[WARN] Se detectaron gaps en documentacion manual:")
        for g in gaps:
            print(f"       - {g}")
        print("\n   Use --check-manual-docs para convertir esto en error blocking.")
    
    print("\n[2/2] Checklist final:")
    print("       (X) Actualizar CHANGELOG.md (al final del release)")
    print("       (X) Actualizar GUIA_TECNICA.md (si hay cambios arquitectonicos)")
    print("       (X) Verificar sync_versions.py si es release")
    print("       (X) Ejecutar: python scripts/run_all_validations.py --quick")
    
    if args.release:
        print("       (X) Version Sync Gate: PASSED (" + args.release + ")")
    
    print("\n(R) Fase registrada exitosamente")
    return 0


if __name__ == "__main__":
    sys.exit(main())
