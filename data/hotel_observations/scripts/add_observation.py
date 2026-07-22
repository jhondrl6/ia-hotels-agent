#!/usr/bin/env python3
"""
add_observation.py — Wizard interactivo para agregar una observacion de hotel.

Uso:
    python3 scripts/add_observation.py
    python3 scripts/add_observation.py --file ruta/al/observations.json

Flujo:
  1. Pregunta los 5 canonicos con validacion de input.
  2. Calcula occupancy_rate y sugiere is_transit_hotel.
  3. Pide is_transit_hotel_basis si la clasificacion es paso.
  4. Calcula campos derivados (occupancy_rate, adr_cop, ratios).
  5. Muestra preview del JSON, pide confirmacion.
  6. Inserta en el array, actualiza last_updated, valida con Draft202012Validator.

Requiere TTY (input interactivo). No se puede ejecutar desde agentes no
interactivos. Ver seccion "Pruebas" abajo para modo no-interactivo.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit(
        "ERROR: jsonschema no instalado.\n"
        "Instalar con: uv pip install --system jsonschema"
    )


# --- Constantes del schema (hardcoded para evitar leer schema en cada prompt) ---

VALID_REGIONS = ("eje_cafetero", "caribe", "antioquia", "default")
VALID_CATEGORIES = ("boutique_10_25", "standard_26_60")
VALID_SOURCES = ("contacto_directo", "formulario_onboarding", "evidencia_verificable")


# --- Helpers de input validados ---

def prompt(msg: str) -> str:
    return input(msg).strip()


def prompt_int(msg: str, min_val: int = 0, max_val: int = 1000) -> int:
    while True:
        raw = prompt(msg)
        try:
            n = int(raw)
            if n < min_val or n > max_val:
                print(f"  ERROR: debe estar entre {min_val} y {max_val}")
                continue
            return n
        except ValueError:
            print(f"  ERROR: '{raw}' no es un entero valido")


def prompt_float(msg: str, min_val: float = 0.0, max_val: float = 1e12) -> float:
    while True:
        raw = prompt(msg)
        # Acepta "200000", "200,000", "200.000" (formato CO)
        cleaned = raw.replace(".", "").replace(",", "") if raw.replace(",", "").replace(".", "").isdigit() else None
        if cleaned is None:
            # fallback: parsear crudo
            try:
                f = float(raw)
            except ValueError:
                print(f"  ERROR: '{raw}' no es un numero valido")
                continue
        else:
            try:
                # Si tenia separadores de miles (puntos/comas), el cleaned es el numero sin sep
                # Si NO tenia separadores, raw ya es el numero
                f = float(cleaned) if cleaned != raw.replace(",", ".") and "," in raw else float(raw)
            except ValueError:
                print(f"  ERROR: '{raw}' no es un numero valido")
                continue
        if f < min_val or f > max_val:
            print(f"  ERROR: debe estar entre {min_val} y {max_val}")
            continue
        return f


def prompt_percentage(msg: str) -> float:
    """Pregunta un porcentaje 0-100. Acepta '60' o '60%' o '60.0'."""
    while True:
        raw = prompt(msg).rstrip("%").strip()
        try:
            f = float(raw)
        except ValueError:
            print(f"  ERROR: '{raw}' no es un numero valido (usa 0-100 o 0%-100%)")
            continue
        if f < 0 or f > 100:
            print(f"  ERROR: debe estar entre 0 y 100")
            continue
        return f


def prompt_bool(msg: str, default: bool | None = None) -> bool:
    while True:
        suffix = ""
        if default is True:
            suffix = " [Y/n]"
        elif default is False:
            suffix = " [y/N]"
        raw = prompt(f"{msg}{suffix}: ").lower()
        if not raw and default is not None:
            return default
        if raw in ("y", "yes", "si", "s", "true", "1"):
            return True
        if raw in ("n", "no", "false", "0"):
            return False
        print("  ERROR: responde y/n")


def prompt_choice(msg: str, choices: tuple[str, ...], default: str | None = None) -> str:
    while True:
        suffix = f" [{'/'.join(choices)}]"
        if default:
            suffix += f" (default: {default})"
        raw = prompt(f"{msg}{suffix}: ").lower()
        if not raw and default:
            return default
        if raw in choices:
            return raw
        print(f"  ERROR: opciones validas: {', '.join(choices)}")


def prompt_nonempty(msg: str, min_len: int = 1) -> str:
    while True:
        raw = prompt(msg)
        if len(raw) < min_len:
            print(f"  ERROR: minimo {min_len} caracteres")
            continue
        return raw


def prompt_optional(msg: str) -> str:
    return prompt(msg)  # puede ser vacio


# --- Calculos derivados ---

def compute_occupancy(rooms: int, monthly_reservations: int) -> float:
    return round(monthly_reservations / (rooms * 30), 4)


def classify_by_occupancy(occ: float) -> str:
    if occ < 0.15:
        return "paso"
    if occ > 0.30:
        return "destino"
    return "ambiguo"


# --- Construccion de la observacion ---

def build_observation() -> dict:
    print("\n=== Wizard: nueva observacion de hotel ===\n")
    print("Los 5 canonicos que pediste al hotel:\n")

    hotel_name = prompt_nonempty("  hotel_name (slug del hotel): ")
    rooms = prompt_int("  rooms (habitaciones en operacion): ", 1, 1000)
    monthly_reservations = prompt_int(
        "  monthly_reservations (reservas/mes promedio): ", 0, 100_000
    )
    avg_reservation_cop = prompt_float(
        "  avg_reservation_cop (valor promedio por reserva, COP): ", 0, 1e10
    )
    direct_channel_percentage = prompt_percentage(
        "  direct_channel_percentage (0-100, %% reservas por canal directo): "
    )

    # Heuristica de occupancy
    occ = compute_occupancy(rooms, monthly_reservations)
    suggestion = classify_by_occupancy(occ)
    print(f"\n  [Heuristica] occupancy_rate = {occ:.4f} ({occ*100:.2f}%)")
    print(f"  [Heuristica] Sugerencia: {suggestion}  "
          f"(<15% paso, >30% destino, 15-30% ambiguo)\n")

    is_transit = prompt_bool("  is_transit_hotel (true=paso, false=destino)", default=(suggestion == "paso"))

    basis = ""
    if is_transit:
        basis = prompt_nonempty(
            "  is_transit_hotel_basis (justificacion, min 20 chars): ", min_len=20
        )
    else:
        # Recomendado pero no obligatorio para destino
        basis = prompt_optional(
            "  is_transit_hotel_basis (opcional para destino, recomendado para trazabilidad): "
        )

    print("\n  Metadata (la llenas tu, no el hotel):\n")
    region = prompt_choice("  region", VALID_REGIONS, default="eje_cafetero")

    # Category auto-derivada de rooms, con opcion de override
    default_cat = "boutique_10_25" if rooms < 26 else "standard_26_60"
    category = prompt_choice("  category", VALID_CATEGORIES, default=default_cat)
    if rooms < 26 and category != "boutique_10_25":
        print("  AVISO: rooms<26 pero category no es boutique_10_25. El schema lo rechazara.")
    if rooms >= 26 and category != "standard_26_60":
        print("  AVISO: rooms>=26 pero category no es standard_26_60. El schema lo rechazara.")

    source = prompt_choice("  source", VALID_SOURCES, default="contacto_directo")
    if source in ("contacto_directo", "formulario_onboarding"):
        default_conf = 0.95
    else:
        default_conf = 0.6
    confidence = prompt_float(
        f"  confidence (0-1, default para {source}): ", 0.0, 1.0
    ) if prompt_bool(f"  usar confidence default {default_conf}?", default=True) else \
        prompt_float("  confidence (0-1): ", 0.0, 1.0)

    epistemic_status = "verified" if source == "contacto_directo" else "estimated"
    if not prompt_bool(f"  epistemic_status = '{epistemic_status}' (auto)", default=True):
        epistemic_status = prompt_choice("  epistemic_status", ("verified", "estimated"))

    collected_at = prompt(f"  collected_at (YYYY-MM-DD, default hoy): ") or str(date.today())

    notes = prompt_optional("  notes (opcional): ")

    # Derivados
    adr_cop = avg_reservation_cop
    direct_channel_ratio = round(direct_channel_percentage / 100, 4)
    ota_percentage = round(1.0 - direct_channel_ratio, 4)

    obs = {
        "hotel_name": hotel_name,
        "is_transit_hotel": is_transit,
        "rooms": rooms,
        "monthly_reservations": monthly_reservations,
        "avg_reservation_cop": avg_reservation_cop,
        "direct_channel_percentage": direct_channel_percentage,
        "occupancy_rate": occ,
        "adr_cop": adr_cop,
        "direct_channel_ratio": direct_channel_ratio,
        "ota_percentage": ota_percentage,
        "region": region,
        "category": category,
        "source": source,
        "confidence": confidence,
        "epistemic_status": epistemic_status,
        "collected_at": collected_at,
    }
    if basis:
        obs["is_transit_hotel_basis"] = basis
    if notes:
        obs["notes"] = notes
    return obs


# --- Validacion y persistencia ---

def validate_observation(obs: dict, schema: dict) -> list[str]:
    """Retorna lista de mensajes de error (vacia si OK).

    Valida contra el subschema de observacion individual ($defs.observation),
    NO contra el schema raiz (que requiere version/last_updated/etc).
    """
    obs_schema = schema.get("$defs", {}).get("observation", schema)
    validator = Draft202012Validator(obs_schema)
    return [f"[{'/'.join(str(p) for p in e.absolute_path) or '<root>'}] {e.message}"
            for e in validator.iter_errors(obs)]


def load_data(obs_path: Path) -> dict:
    if not obs_path.exists():
        return {
            "version": "1.0.0",
            "last_updated": str(date.today()),
            "source_role": "individual_hotel_observations",
            "epistemic_status_default": "verified",
            "description": "Observaciones operacionales reales de hoteles individuales.",
            "observations": [],
        }
    return json.loads(obs_path.read_text(encoding="utf-8"))


def save_data(obs_path: Path, data: dict) -> None:
    obs_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Wizard para agregar observacion de hotel")
    parser.add_argument(
        "--file", type=Path, default=None,
        help="Ruta a observations.json (default: junto al schema)"
    )
    parser.add_argument(
        "--schema", type=Path, default=None,
        help="Ruta al schema (default: junto al archivo de datos)"
    )
    parser.add_argument(
        "--non-interactive", action="store_true",
        help="Lee observacion de stdin como JSON (para testing)"
    )
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    obs_path = args.file or (base / "observations.json")
    schema_path = args.schema or (base / "hotel_observations.schema.json")

    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    if args.non_interactive:
        # Modo test: lee JSON de stdin
        obs = json.loads(sys.stdin.read())
        errors = validate_observation(obs, schema)
        if errors:
            print("FAIL:")
            for e in errors:
                print(f"  - {e}")
            return 1
        print("OK")
        return 0

    obs = build_observation()

    print("\n=== Preview JSON ===\n")
    print(json.dumps(obs, indent=2, ensure_ascii=False))
    print()

    errors = validate_observation(obs, schema)
    if errors:
        print("=== Validacion contra schema: FAIL ===")
        for e in errors:
            print(f"  - {e}")
        if not prompt_bool("\n  A pesar de los errores, intentar guardar de todos modos?", default=False):
            print("Cancelado.")
            return 1

    if not prompt_bool("  Guardar esta observacion en observations.json?", default=True):
        print("Cancelado.")
        return 0

    data = load_data(obs_path)
    data["observations"].append(obs)
    data["last_updated"] = str(date.today())
    save_data(obs_path, data)
    print(f"\n  Guardado en {obs_path}")
    print(f"  Total observaciones: {len(data['observations'])}")
    print(f"  last_updated: {data['last_updated']}")
    print("\n  Sugerencia: corre scripts/validate.py para confirmar.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
