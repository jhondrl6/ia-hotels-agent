#!/usr/bin/env python3
"""
Pre-carga GBP Batch de Prospectos
=================================
FASE-P2-B / F9: Script reutilizable que toma una lista de prospectos
(nombre + ciudad), ejecuta la pre-carga GBP/Places, y produce un reporte
con gate de completitud (telefono + direccion + categoria verificadas).

Uso:
    python scripts/preload_prospects_gbp.py --input prospectos.yaml
    python scripts/preload_prospects_gbp.py --input prospectos.yaml --dry-run
    python scripts/preload_prospects_gbp.py --input prospectos.yaml --output reporte.md
    python scripts/preload_prospects_gbp.py --builtin   # usa lista embebida del Eje Cafetero

Formato de entrada (YAML):
    prospects:
      - name: "Hotel Condina Pereira"
        city: "Pereira"
      - name: "Hotel Salento Real"
        city: "Salento"

Formato de salida (Markdown):
    Tabla con estado de completitud por prospecto:
    - VERIFIED: telefono + direccion + categoria encontrados
    - PARTIAL: algunos campos faltantes
    - MISSING: no encontrado o sin datos de contacto
"""

import argparse
import csv
import io
import json
import logging
import os
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Agregar project root al path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Estructuras
# ---------------------------------------------------------------------------

COMPLETENESS_VERIFIED = "VERIFIED"
COMPLETENESS_PARTIAL = "PARTIAL"
COMPLETENESS_MISSING = "MISSING"
COMPLETENESS_DRY_RUN = "DRY_RUN"


@dataclass
class ProspectInput:
    """Prospecto desde la lista de entrada."""
    name: str
    city: str
    source_index: int = 0


@dataclass
class ProspectResult:
    """Resultado de pre-carga de un prospecto."""
    name: str
    city: str
    source_index: int
    # Datos GBP
    place_id: str = ""
    found_name: str = ""
    phone: Optional[str] = None
    address: str = ""
    website: Optional[str] = None
    rating: float = 0.0
    reviews: int = 0
    category: str = ""
    # Gate de completitud
    has_phone: bool = False
    has_address: bool = False
    has_category: bool = False
    has_website: bool = False
    completeness: str = COMPLETENESS_MISSING
    error: Optional[str] = None
    # Meta
    fetched_at: str = ""
    search_query: str = ""

    def ready_to_contact(self) -> bool:
        """Marca 'listo para contactar' solo si telefono + direccion + categoria."""
        return self.has_phone and self.has_address and self.has_category


# ---------------------------------------------------------------------------
# Parser de entrada
# ---------------------------------------------------------------------------

def parse_yaml_input(filepath: Path) -> List[ProspectInput]:
    """Parsea archivo YAML de prospectos."""
    try:
        import yaml
    except ImportError:
        logger.error("PyYAML no instalado. Instalar con: pip install pyyaml")
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    prospects = []
    raw_list = data.get('prospects', data if isinstance(data, list) else [])
    for i, item in enumerate(raw_list, 1):
        name = item.get('name', '').strip()
        city = item.get('city', '').strip()
        if name:
            prospects.append(ProspectInput(name=name, city=city, source_index=i))
    return prospects


def parse_csv_input(filepath: Path) -> List[ProspectInput]:
    """Parsea archivo CSV de prospectos (columnas: name, city)."""
    prospects = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            name = row.get('name', row.get('hotel', '')).strip()
            city = row.get('city', row.get('municipio', row.get('ciudad', ''))).strip()
            if name:
                prospects.append(ProspectInput(name=name, city=city, source_index=i))
    return prospects


def parse_input(filepath: Path) -> List[ProspectInput]:
    """Parsea archivo de entrada (YAML o CSV segun extension)."""
    ext = filepath.suffix.lower()
    if ext in ('.yaml', '.yml'):
        return parse_yaml_input(filepath)
    elif ext == '.csv':
        return parse_csv_input(filepath)
    else:
        logger.warning(f"Extension {ext} no reconocida, intentando YAML")
        return parse_yaml_input(filepath)


# ---------------------------------------------------------------------------
# Lista embebida del Eje Cafetero (fallback si no hay --input)
# ---------------------------------------------------------------------------

BUILTIN_PROSPECTS = [
    {"name": "Hotel Condina Pereira", "city": "Pereira"},
    {"name": "Hotel Catalonia Pereira", "city": "Pereira"},
    {"name": "Hostal Ciudad de Segorbe", "city": "Salento"},
    {"name": "Hotel Salento Real Eje Cafetero", "city": "Salento"},
    {"name": "Hotel Guadalupe Plaza", "city": "Dosquebradas"},
    {"name": "Hotel Platino Plaza", "city": "Dosquebradas"},
    {"name": "Hotel Tangara", "city": "Dosquebradas"},
    {"name": "Finca Hotel Villa Ilusion", "city": "Dosquebradas"},
    {"name": "Hotel Visperas", "city": "Santa Rosa de Cabal"},
    {"name": "Hotel Recreacional Marcelandia", "city": "Santa Rosa de Cabal"},
    {"name": "Hotel El Mirador del Cocora", "city": "Salento"},
    {"name": "Mahalo Hostal Boutique", "city": "Salento"},
    {"name": "Colina del Sol Hotel Hacienda", "city": "Quimbaya"},
    {"name": "Finca Hotel Los Girasoles", "city": "Quimbaya"},
    {"name": "Finca Hotel Casa Nostra", "city": "Quimbaya"},
    {"name": "Hotel Campestre Nogal de Cafetal", "city": "Quimbaya"},
    {"name": "Finca Hotel Jardin Cafetero del Quindio", "city": "Quimbaya"},
    {"name": "Origen Finca Hotel", "city": "Quimbaya"},
    {"name": "Pausa Hospedaje Filandia", "city": "Filandia"},
    {"name": "Hostal la Luz de la Colina", "city": "Filandia"},
    {"name": "Hostal Amelia Filandia", "city": "Filandia"},
    {"name": "Hospedaje Mandarinos Filandia", "city": "Filandia"},
    {"name": "La Casita Filandia", "city": "Filandia"},
    {"name": "Mot Mot Glamping", "city": "Filandia"},
    {"name": "Alua Glamping", "city": "Filandia"},
    {"name": "Hotel Cafe Bernal", "city": "Armenia"},
    {"name": "Hosteria Mi Monaco", "city": "Armenia"},
    {"name": "Finca Hotel Nuestro Sueno", "city": "Montenegro"},
    {"name": "Casa Azul Boutique Hostel", "city": "Pereira"},
    {"name": "La Iguana Cafe y Hostal", "city": "Pereira"},
]


def get_builtin_prospects() -> List[ProspectInput]:
    """Retorna la lista embebida de 30 prospectos del Eje Cafetero."""
    return [
        ProspectInput(name=p["name"], city=p["city"], source_index=i)
        for i, p in enumerate(BUILTIN_PROSPECTS, 1)
    ]


# ---------------------------------------------------------------------------
# Pre-carga GBP
# ---------------------------------------------------------------------------

def preload_prospect(
    prospect: ProspectInput,
    places_client: Any,
    dry_run: bool = False
) -> ProspectResult:
    """
    Ejecuta pre-carga GBP/Places para un prospecto.

    Args:
        prospect: Datos del prospecto
        places_client: Instancia de GooglePlacesClient
        dry_run: Si True, no ejecuta llamadas a API

    Returns:
        ProspectResult con datos y estado de completitud
    """
    result = ProspectResult(
        name=prospect.name,
        city=prospect.city,
        source_index=prospect.source_index,
        fetched_at=datetime.now().isoformat()
    )

    if dry_run:
        result.completeness = COMPLETENESS_DRY_RUN
        result.search_query = f"text:{prospect.name} {prospect.city}"
        return result

    # Buscar en Places API
    place = places_client.search_by_name(
        name=prospect.name,
        city=prospect.city,
        category="lodging"
    )

    if place is None or not place.place_found:
        result.error = place.error_message if place else "No response"
        result.completeness = COMPLETENESS_MISSING
        return result

    # Llenar datos
    result.place_id = place.place_id
    result.found_name = place.name
    result.phone = place.phone
    result.address = place.address
    result.website = place.website_url
    result.rating = place.rating
    result.reviews = place.reviews
    result.search_query = place.search_query or f"text:{prospect.name} {prospect.city}"

    # Evaluar completitud
    result.has_phone = bool(place.phone and place.phone.strip())
    result.has_address = bool(place.address and place.address.strip())
    result.has_website = bool(place.website_url and place.website_url.strip())
    # Categoria: verificar si es lodging (el search ya filtra por includedType)
    result.has_category = place.place_found
    result.category = "lodging" if place.place_found else ""

    # Gate de completitud
    if result.ready_to_contact():
        result.completeness = COMPLETENESS_VERIFIED
    elif result.has_phone or result.has_address:
        result.completeness = COMPLETENESS_PARTIAL
    else:
        result.completeness = COMPLETENESS_MISSING

    return result


# ---------------------------------------------------------------------------
# Reporte
# ---------------------------------------------------------------------------

def generate_report(results: List[ProspectResult], dry_run: bool = False) -> str:
    """Genera reporte Markdown con estado de completitud."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    mode = "DRY-RUN" if dry_run else "LIVE"

    lines = []
    lines.append(f"# Reporte Pre-carga GBP de Prospectos ({mode})")
    lines.append(f"")
    lines.append(f"**Fecha:** {now}")
    lines.append(f"**Total prospectos:** {len(results)}")

    # Resumen
    verified = sum(1 for r in results if r.completeness == COMPLETENESS_VERIFIED)
    partial = sum(1 for r in results if r.completeness == COMPLETENESS_PARTIAL)
    missing = sum(1 for r in results if r.completeness == COMPLETENESS_MISSING)

    if not dry_run:
        lines.append(f"")
        lines.append(f"## Resumen de Completitud")
        lines.append(f"")
        lines.append(f"| Estado | Cantidad | % |")
        lines.append(f"|--------|----------|---|")
        pct_v = f"{verified * 100 // len(results)}%" if results else "0%"
        pct_p = f"{partial * 100 // len(results)}%" if results else "0%"
        pct_m = f"{missing * 100 // len(results)}%" if results else "0%"
        lines.append(f"| VERIFIED (listo para contactar) | {verified} | {pct_v} |")
        lines.append(f"| PARTIAL (datos incompletos) | {partial} | {pct_p} |")
        lines.append(f"| MISSING (no encontrado) | {missing} | {pct_m} |")
    else:
        lines.append(f"")
        lines.append(f"**Modo:** DRY-RUN -- no se ejecutaron llamadas a API")

    lines.append(f"")
    lines.append(f"## Detalle por Prospecto")
    lines.append(f"")

    if dry_run:
        lines.append(f"| # | Hotel | Ciudad | Query prevista | Estado |")
        lines.append(f"|---|-------|--------|----------------|--------|")
        for r in results:
            lines.append(
                f"| {r.source_index} | {r.name} | {r.city} "
                f"| `{r.search_query}` | DRY_RUN |"
            )
    else:
        lines.append(
            f"| # | Hotel | Ciudad | Telefono | Direccion | "
            f"Web | Rating | Resenas | Estado |"
        )
        lines.append(
            f"|---|-------|--------|----------|-----------|"
            f"-----|--------|---------|--------|"
        )
        for r in results:
            phone_str = r.phone if r.has_phone else "**Pendiente verificar**"
            addr_short = (r.address[:30] + "...") if len(r.address) > 30 else r.address
            addr_str = addr_short if r.has_address else "**Pendiente verificar**"
            web_str = "Si" if r.has_website else "No"
            rating_str = f"{r.rating}/5" if r.rating > 0 else "N/A"
            reviews_str = str(r.reviews) if r.reviews > 0 else "N/A"
            status_icon = {
                COMPLETENESS_VERIFIED: "VERIFIED",
                COMPLETENESS_PARTIAL: "PARTIAL",
                COMPLETENESS_MISSING: "MISSING",
            }.get(r.completeness, r.completeness)
            lines.append(
                f"| {r.source_index} | {r.name} | {r.city} "
                f"| {phone_str} | {addr_str} "
                f"| {web_str} | {rating_str} | {reviews_str} | {status_icon} |"
            )

    # Seccion de errores
    errors = [r for r in results if r.error]
    if errors:
        lines.append(f"")
        lines.append(f"## Errores")
        lines.append(f"")
        for r in errors:
            lines.append(f"- **{r.name}** ({r.city}): {r.error}")

    lines.append(f"")
    lines.append(f"---")
    lines.append(f"*Generado por preload_prospects_gbp.py*")
    return "\n".join(lines)


def save_json_results(results: List[ProspectResult], filepath: Path) -> None:
    """Guarda resultados en formato JSON para procesamiento posterior."""
    data = {
        "generated_at": datetime.now().isoformat(),
        "total": len(results),
        "summary": {
            "verified": sum(1 for r in results if r.completeness == COMPLETENESS_VERIFIED),
            "partial": sum(1 for r in results if r.completeness == COMPLETENESS_PARTIAL),
            "missing": sum(1 for r in results if r.completeness == COMPLETENESS_MISSING),
        },
        "results": [asdict(r) for r in results]
    }
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"JSON results saved to {filepath}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Pre-carga GBP batch de prospectos con gate de completitud"
    )
    parser.add_argument(
        '--input', '-i',
        type=str,
        help='Ruta al archivo YAML/CSV con prospectos (columnas: name, city)'
    )
    parser.add_argument(
        '--builtin',
        action='store_true',
        help='Usar lista embebida de 30 prospectos del Eje Cafetero'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Ruta del archivo de salida Markdown (default: stdout)'
    )
    parser.add_argument(
        '--json-output',
        type=str,
        default=None,
        help='Ruta del archivo de salida JSON (opcional)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Modo prueba: no ejecuta llamadas a API'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Log detallado'
    )

    args = parser.parse_args()

    # Configurar logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    # Cargar prospectos
    if args.builtin:
        prospects = get_builtin_prospects()
        logger.info(f"Cargados {len(prospects)} prospectos (lista embebida Eje Cafetero)")
    elif args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            logger.error(f"Archivo no encontrado: {input_path}")
            sys.exit(1)
        prospects = parse_input(input_path)
        logger.info(f"Cargados {len(prospects)} prospectos desde {input_path}")
    else:
        parser.print_help()
        print("\nError: especificar --input <archivo> o --builtin")
        sys.exit(1)

    if not prospects:
        logger.error("No se encontraron prospectos en la entrada")
        sys.exit(1)

    # Inicializar Places client (solo si no es dry-run)
    places_client = None
    if not args.dry_run:
        from modules.scrapers.google_places_client import GooglePlacesClient
        places_client = GooglePlacesClient()
        if not places_client.is_available:
            logger.error(
                "GOOGLE_MAPS_API_KEY no configurada. "
                "Configurar en .env o exportar como variable de entorno."
            )
            sys.exit(1)

    # Ejecutar pre-carga
    results = []
    for prospect in prospects:
        logger.info(
            f"[{prospect.source_index}/{len(prospects)}] "
            f"Pre-cargando: {prospect.name} ({prospect.city})"
        )
        result = preload_prospect(prospect, places_client, dry_run=args.dry_run)
        results.append(result)

    # Generar reporte
    report = generate_report(results, dry_run=args.dry_run)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Reporte guardado en {output_path}")
    else:
        print(report)

    # Guardar JSON si se solicita
    if args.json_output:
        save_json_results(results, Path(args.json_output))

    # Resumen en stderr
    if not args.dry_run:
        v = sum(1 for r in results if r.completeness == COMPLETENESS_VERIFIED)
        p = sum(1 for r in results if r.completeness == COMPLETENESS_PARTIAL)
        m = sum(1 for r in results if r.completeness == COMPLETENESS_MISSING)
        print(
            f"\nCompletitud: {v} VERIFIED / {p} PARTIAL / {m} MISSING "
            f"de {len(results)} prospectos",
            file=sys.stderr
        )
    else:
        print(
            f"\nDRY-RUN completado: {len(results)} prospectos listados "
            f"(sin llamadas a API)",
            file=sys.stderr
        )


if __name__ == '__main__':
    main()
