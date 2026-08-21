#!/usr/bin/env python3
"""Validate benchmark synchronization between master (regional_adr_2026.json) and
plan_maestro_data.json.

FASE-P1-A: ensures ADR/occupancy values in plan_maestro_data.json match the
master file for all shared regions. Reports divergences and exits non-zero
if any are found.

Usage:
    python scripts/validate_benchmark_sync.py          # normal run
    python scripts/validate_benchmark_sync.py --quiet   # only print errors
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASTER_PATH = ROOT / "data" / "benchmarks" / "regional_adr_2026.json"
SECONDARY_PATH = ROOT / "data" / "benchmarks" / "plan_maestro_data.json"


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_master_adr_by_region(master: dict) -> dict:
    """Extract boutique ADR per region from the master."""
    result = {}
    for region, data in master.get("regions", {}).items():
        if region == "default":
            any_data = data.get("any", {})
            result[region] = {
                "adr_cop": any_data.get("adr_cop"),
                "occupancy_rate": any_data.get("occupancy_rate"),
            }
            continue
        boutique = data.get("boutique_10_25", {})
        result[region] = {
            "adr_cop": boutique.get("adr_cop"),
            "occupancy_rate": boutique.get("occupancy_rate"),
        }
    return result


def get_secondary_adr_by_region(secondary: dict) -> dict:
    """Extract ADR/occupancy from plan_maestro_data.json v25_config.regiones."""
    result = {}
    regiones = secondary.get("v25_config", {}).get("regiones", {})
    if not regiones:
        regiones = secondary.get("regiones", {})
    for region, data in regiones.items():
        result[region] = {
            "adr_cop": data.get("precio_promedio", data.get("adr_cop")),
            "occupancy_rate": data.get("ocupacion", data.get("occupancy_rate")),
        }
    return result


def validate(quiet: bool = False) -> list:
    """Return list of divergence messages. Empty = all synced."""
    master = load_json(MASTER_PATH)
    secondary = load_json(SECONDARY_PATH)

    master_adr = get_master_adr_by_region(master)
    secondary_adr = get_secondary_adr_by_region(secondary)

    divergences = []

    # Check master regions exist in secondary
    for region, mdata in master_adr.items():
        if region == "default":
            continue  # default has different structure
        if region not in secondary_adr:
            divergences.append(
                f"MISSING: region '{region}' in master but absent in plan_maestro_data.json"
            )
            continue

        sdata = secondary_adr[region]

        # ADR check
        if mdata["adr_cop"] is not None and sdata["adr_cop"] is not None:
            if mdata["adr_cop"] != sdata["adr_cop"]:
                divergences.append(
                    f"ADR DIVERGENCE [{region}]: master={mdata['adr_cop']:,} "
                    f"vs plan_maestro={sdata['adr_cop']:,}"
                )

        # Occupancy check
        if mdata["occupancy_rate"] is not None and sdata["occupancy_rate"] is not None:
            if abs(mdata["occupancy_rate"] - sdata["occupancy_rate"]) > 0.001:
                divergences.append(
                    f"OCCUPANCY DIVERGENCE [{region}]: master={mdata['occupancy_rate']} "
                    f"vs plan_maestro={sdata['occupancy_rate']}"
                )

    # Check secondary doesn't have extra regions absent from master
    master_regions = set(master_adr.keys()) - {"default"}
    secondary_regions = set(secondary_adr.keys()) - {"default"}
    extra = secondary_regions - master_regions
    if extra:
        divergences.append(
            f"EXTRA REGIONS in plan_maestro_data.json not in master: {extra}"
        )

    if not quiet:
        if divergences:
            print("BENCHMARK SYNC FAIL:")
            for d in divergences:
                print(f"  - {d}")
        else:
            print(f"BENCHMARK SYNC OK: {len(master_regions)} regions verified "
                  f"(master: {sorted(master_regions)})")

    return divergences


if __name__ == "__main__":
    quiet = "--quiet" in sys.argv
    divergences = validate(quiet=quiet)
    sys.exit(1 if divergences else 0)
