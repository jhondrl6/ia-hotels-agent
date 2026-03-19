"""Chequea archivos residuales o duplicados en el repo."""

import argparse
import json
import re
from pathlib import Path

IGNORED_EXTENSIONS = {".pyc"}
RESIDUAL_SUFFIXES = {".bak", ".backup", ".tmp"}

UMBRALES_ESPERADOS = {
    "impacto_catastrofico": 6000000,
    "brecha_conversion_critica": 2500000,
    "revpar_premium": 180000,
    "web_score_alto": 75,
    "gbp_score_bajo": 60,
}

CAMPOS_REGION_REQUERIDOS = [
    "revpar_cop",
    "reservas_mensuales_promedio",
    "valor_reserva_promedio",
    "canal_directo_porcentaje",
    "habitaciones_promedio",
    "factor_captura_aila",
    "comision_ota_base",
    "factor_perdida_base",
]


def find_residuals(base_path: Path) -> list[Path]:
    residuals: list[Path] = []
    for path in base_path.rglob("*"):
        if path.is_dir():
            continue
        if path.suffix in IGNORED_EXTENSIONS:
            continue
        if path.suffix in RESIDUAL_SUFFIXES or ".backup" in path.name:
            residuals.append(path)
    return residuals


def main() -> None:
    parser = argparse.ArgumentParser(description="Verifica archivos residuales")
    parser.add_argument("--root", default=".", help="Directorio raiz a inspeccionar")
    args = parser.parse_args()

    base_path = Path(args.root).resolve()
    residuals = find_residuals(base_path)
    if not residuals:
        print("Sin archivos residuales detectados.")
        return

    print("Archivos residuales detectados:")
    for path in residuals:
        print(f" - {path.relative_to(base_path)}")


def _load_json(json_path: Path) -> dict | None:
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[GUARD] Error cargando {json_path}: {e}")
        return None


def _extract_thresholds_from_engine(engine_path: Path) -> dict:
    thresholds = {}
    try:
        content = engine_path.read_text(encoding="utf-8")
        for key in UMBRALES_ESPERADOS:
            pattern = rf't\.get\("{key}",\s*([\d_]+)\)'
            match = re.search(pattern, content)
            if match:
                value_str = match.group(1).replace("_", "")
                thresholds[key] = int(value_str)
    except Exception as e:
        print(f"[GUARD] Error leyendo decision_engine.py: {e}")
    return thresholds


def _verify_thresholds_consistency(json_data: dict, engine_thresholds: dict) -> list[str]:
    errors = []
    json_umbrales = json_data.get("umbrales_decision", {})
    for key, expected in UMBRALES_ESPERADOS.items():
        json_value = json_umbrales.get(key)
        engine_value = engine_thresholds.get(key)
        if json_value != expected:
            errors.append(f"  - {key}: JSON={json_value}, esperado={expected}")
        if engine_value and engine_value != expected:
            errors.append(f"  - {key}: decision_engine.py={engine_value}, esperado={expected}")
    return errors


def _verify_regions(json_data: dict) -> list[str]:
    errors = []
    regiones = json_data.get("regiones", {})
    for region_name, region_data in regiones.items():
        if not isinstance(region_data, dict):
            errors.append(f"  - Region '{region_name}' no es un objeto valido")
            continue
        missing = [c for c in CAMPOS_REGION_REQUERIDOS if c not in region_data]
        if missing:
            errors.append(f"  - Region '{region_name}' falta campos: {', '.join(missing)}")
    return errors


def _verify_version(json_data: dict) -> list[str]:
    errors = []
    version = json_data.get("version", "")
    if not version:
        errors.append("  - Version no especificada en JSON")
    elif not version.startswith("v2."):
        errors.append(f"  - Version desactualizada: {version} (se espera v2.x)")
    return errors


def run_plan_maestro_check() -> None:
    """Valida coherencia local entre plan_maestro_data.json y decision_engine.py."""
    print("\n[GUARD] Ejecutando validacion de Plan Maestro (sin conexion externa)...")

    repo_root = Path(__file__).resolve().parent.parent
    json_path = repo_root / "data" / "benchmarks" / "plan_maestro_data.json"
    engine_path = repo_root / "modules" / "decision_engine.py"

    if not json_path.exists():
        print(f"[GUARD] ERROR: No existe {json_path}")
        return

    if not engine_path.exists():
        print(f"[GUARD] ERROR: No existe {engine_path}")
        return

    json_data = _load_json(json_path)
    if not json_data:
        return

    engine_thresholds = _extract_thresholds_from_engine(engine_path)

    all_errors = []
    all_errors.extend(_verify_thresholds_consistency(json_data, engine_thresholds))
    all_errors.extend(_verify_regions(json_data))
    all_errors.extend(_verify_version(json_data))

    if all_errors:
        print("[GUARD] ALERTA: Se detectaron inconsistencias:")
        for error in all_errors:
            print(error)
        print(f"[GUARD] Total: {len(all_errors)} problemas encontrados.")
    else:
        print("[GUARD] Coherencia tecnica validada correctamente.")
        print(f"[GUARD] Version JSON: {json_data.get('version', 'N/A')}")
        print(f"[GUARD] Umbrales verificados: {len(UMBRALES_ESPERADOS)} OK")
        print(f"[GUARD] Regiones validadas: {len(json_data.get('regiones', {}))}")


if __name__ == "__main__":
    main()
    run_plan_maestro_check()
