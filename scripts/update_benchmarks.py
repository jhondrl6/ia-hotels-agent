#!/usr/bin/env python3
"""
Update Benchmarks - Calcula promedios regionales desde research y actualiza plan_maestro_data.json

Uso:
    # Paso 1: Guardar output de deep research en data/benchmarks/research_output.json
    # Paso 2: Ejecutar este script
    python scripts/update_benchmarks.py

    # Modo seco (solo calcula, no escribe):
    python scripts/update_benchmarks.py --dry-run

    # Usar archivo de entrada diferente:
    python scripts/update_benchmarks.py --input data/benchmarks/research_2026Q2.json

Fórmulas:
    GEO:  Misma fórmula que google_places_client.calculate_geo_score()
          (rating/5*30) + (reviews/100*2 capped 20) + (fotos*0.5 capped 20) +
          (10 if has_hours) + (10 if has_website) → normalizado a 0-100

    AEO:  schema_hotel(30) + schema_faq(25) + open_graph(25) + robots_ai(20)
          Proxy basado en datos que deep research puede verificar.

    SEO:  has_own_website(35) + schema_hotel(20) + schema_faq(15) + mobile_speed(30)
          Proxy basado en datos que deep research puede verificar.
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


# ─── Rutas ───────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
BENCHMARKS_DIR = BASE_DIR / "data" / "benchmarks"
PLAN_MAESTRO_PATH = BENCHMARKS_DIR / "plan_maestro_data.json"
DEFAULT_INPUT = BENCHMARKS_DIR / "research_output.json"


# ─── Fórmulas (replican la lógica del sistema) ────────────────────────────

def calculate_geo_score(hotel: Dict[str, Any]) -> int:
    """Fórmula idéntica a google_places_client.calculate_geo_score()."""
    rating = hotel.get("rating", 0) or 0
    reviews = hotel.get("reviews", 0) or 0
    photos = hotel.get("fotos", 0) or 0
    has_hours = hotel.get("has_hours", False)
    has_website = hotel.get("has_website", False)

    rating_score = (rating / 5.0) * 30.0
    reviews_score = min((reviews / 100.0) * 2.0, 20.0)
    photos_score = min(photos * 0.5, 20.0)
    hours_score = 10.0 if has_hours else 0.0
    website_score = 10.0 if has_website else 0.0

    raw_total = rating_score + reviews_score + photos_score + hours_score + website_score
    return int(min(raw_total * (100.0 / 90.0), 100.0))


def calculate_aeo_score(hotel: Dict[str, Any]) -> int:
    """Proxy AEO basado en datos verificables por deep research.

    Peso: schema_hotel(30) + schema_faq(25) + open_graph(25) + robots_ai(20) = 100
    """
    score = 0
    if hotel.get("schema_hotel"):
        score += 30
    if hotel.get("schema_faq"):
        score += 25
    if hotel.get("open_graph"):
        score += 25
    if hotel.get("robots_ai_friendly"):
        score += 20
    return score


def calculate_seo_score(hotel: Dict[str, Any]) -> int:
    """Proxy SEO basado en datos verificables por deep research.

    Peso: has_own_website(35) + schema_hotel(20) + schema_faq(15) + mobile_speed(30) = 100
    """
    score = 0
    if hotel.get("has_own_website"):
        score += 35
    if hotel.get("schema_hotel"):
        score += 20
    if hotel.get("schema_faq"):
        score += 15

    mobile = hotel.get("mobile_speed", "").lower() if hotel.get("mobile_speed") else ""
    if mobile == "buena":
        score += 30
    elif mobile == "regular":
        score += 18
    # "mala" o ausente = 0

    return score


# ─── Cálculo de promedios ────────────────────────────────────────────────

def compute_region_averages(hotels: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcula promedios de GEO, AEO, SEO para una lista de hoteles."""
    if not hotels:
        return {"geo_avg": 0, "aeo_avg": 0, "seo_avg": 0, "count": 0}

    geo_scores = [calculate_geo_score(h) for h in hotels]
    aeo_scores = [calculate_aeo_score(h) for h in hotels]
    seo_scores = [calculate_seo_score(h) for h in hotels]

    return {
        "geo_avg": round(sum(geo_scores) / len(geo_scores)),
        "aeo_avg": round(sum(aeo_scores) / len(aeo_scores)),
        "seo_avg": round(sum(seo_scores) / len(seo_scores)),
        "count": len(hotels),
    }


def compute_all_regions(research_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Calcula promedios por región + default (promedio nacional)."""
    results = {}
    all_hotels = []

    regiones = research_data.get("regiones", {})
    for region_name, region_data in regiones.items():
        hotels = region_data.get("hotels", [])
        all_hotels.extend(hotels)
        avg = compute_region_averages(hotels)
        results[region_name] = avg

    # Default = promedio de todas las regiones combinadas
    if all_hotels:
        results["default"] = compute_region_averages(all_hotels)
    else:
        results["default"] = {"geo_avg": 55, "aeo_avg": 20, "seo_avg": 50, "count": 0}

    return results


# ─── Actualización del plan_maestro ──────────────────────────────────────

def update_plan_maestro(
    averages: Dict[str, Dict[str, Any]],
    plan_maestro_path: Path,
    dry_run: bool = False,
) -> None:
    """Actualiza solo los campos *_score_ref en plan_maestro_data.json."""
    with open(plan_maestro_path, "r", encoding="utf-8") as f:
        plan_maestro = json.load(f)

    regiones = plan_maestro.get("v25_config", {}).get("regiones", {})

    if not regiones:
        print("[ERROR] No se encontró 'v25_config.regiones' en plan_maestro_data.json")
        sys.exit(1)

    updated = []
    for region_name, avg in averages.items():
        if region_name in regiones:
            old_geo = str(regiones[region_name].get("geo_score_ref", "?"))
            old_aeo = str(regiones[region_name].get("aeo_score_ref", "?"))
            old_seo = str(regiones[region_name].get("seo_score_ref", "?"))

            regiones[region_name]["geo_score_ref"] = avg["geo_avg"]
            regiones[region_name]["aeo_score_ref"] = avg["aeo_avg"]
            regiones[region_name]["seo_score_ref"] = avg["seo_avg"]

            updated.append(
                f"  {region_name:15s}  GEO {old_geo:>2s} -> {avg['geo_avg']:>2d}  "
                f"AEO {old_aeo:>2s} -> {avg['aeo_avg']:>2d}  "
                f"SEO {old_seo:>2s} -> {avg['seo_avg']:>2d}  "
                f"(n={avg['count']})"
            )
        else:
            print(f"  [WARN] Región '{region_name}' no existe en plan_maestro_data.json, saltando")

    # Actualizar fecha
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    plan_maestro["fecha_actualizacion"] = now

    if not dry_run:
        with open(plan_maestro_path, "w", encoding="utf-8") as f:
            json.dump(plan_maestro, f, indent=2, ensure_ascii=False)

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Cambios en plan_maestro_data.json:")
    for line in updated:
        print(line)
    print(f"\n  Fecha actualizada: {now}")
    print(f"  Archivo: {plan_maestro_path}")


# ─── Validación del input ────────────────────────────────────────────────

def validate_research_data(data: Dict[str, Any]) -> List[str]:
    """Valida estructura del JSON de research. Retorna lista de warnings."""
    warnings = []

    regiones = data.get("regiones", {})
    if not regiones:
        warnings.append("No se encontró 'regiones' en el JSON")

    for region_name, region_data in regiones.items():
        hotels = region_data.get("hotels", [])
        if not hotels:
            warnings.append(f"Región '{region_name}' sin hoteles")
            continue

        if len(hotels) < 5:
            warnings.append(
                f"Región '{region_name}' tiene solo {len(hotels)} hoteles (mínimo recomendado: 10)"
            )

        # Verificar campos requeridos por hotel
        required = ["nombre", "rating"]
        for i, hotel in enumerate(hotels):
            missing = [f for f in required if f not in hotel or hotel[f] is None]
            if missing:
                warnings.append(
                    f"Región '{region_name}', hotel #{i+1} '{hotel.get('nombre', '?')}': "
                    f"faltan campos {missing}"
                )

    return warnings


# ─── Main ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Calcula promedios regionales desde research y actualiza plan_maestro_data.json"
    )
    parser.add_argument(
        "--input", "-i",
        default=str(DEFAULT_INPUT),
        help=f"Ruta al JSON de research (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Solo muestra los cambios, no escribe",
    )
    args = parser.parse_args()

    input_path = Path(args.input)

    # Verificar que existe
    if not input_path.exists():
        print(f"[ERROR] No se encontró el archivo de research: {input_path}")
        print(f"\nUso: Guarda el output del deep research en {DEFAULT_INPUT}")
        print(f"      y ejecuta: python scripts/update_benchmarks.py")
        sys.exit(1)

    # Cargar research
    with open(input_path, "r", encoding="utf-8") as f:
        research_data = json.load(f)

    # Validar
    warnings = validate_research_data(research_data)
    if warnings:
        print("[WARNINGS]")
        for w in warnings:
            print(f"  - {w}")
        print()

    # Calcular promedios
    print("Calculando promedios regionales...")
    averages = compute_all_regions(research_data)

    for region_name, avg in averages.items():
        label = region_name.replace("_", " ").title()
        print(
            f"  {label:20s}  GEO {avg['geo_avg']:>2d}/100  "
            f"AEO {avg['aeo_avg']:>2d}/100  SEO {avg['seo_avg']:>2d}/100  (n={avg['count']})"
        )

    # Actualizar plan_maestro
    print()
    update_plan_maestro(averages, PLAN_MAESTRO_PATH, dry_run=args.dry_run)

    if not args.dry_run:
        print("\n[Listo] Benchmarks actualizados correctamente.")
    else:
        print("\n[DRY RUN] Ningún archivo fue modificado.")


if __name__ == "__main__":
    main()
