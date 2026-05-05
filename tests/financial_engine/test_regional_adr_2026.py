"""Tests for regional_adr_2026.json integration (FIN-2A).

Verifies that RegionalADRResolver loads the new structured benchmarks
and returns correct epistemic metadata (epistemic_status, can_show_exact, occupancy_rate).
"""

import pytest
import json
import tempfile
import os
from pathlib import Path

from modules.financial_engine.regional_adr_resolver import (
    RegionalADRResolver,
    RegionalADRResult,
    resolve_regional_adr,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def regional_adr_json_content():
    """Minimal but complete regional_adr_2026.json content."""
    return {
        "version": "1.0.0",
        "description": "Benchmarks regionales 2026",
        "last_updated": "2026-05-04",
        "source_document": "data/benchmarks/Benchmarking.md",
        "source_role": "regional_benchmark_not_hotel_specific",
        "valid_for_exact_projection": False,
        "epistemic_status": "regional_benchmark",
        "default_region": "eje_cafetero",
        "regions": {
            "eje_cafetero": {
                "boutique_10_25": {
                    "adr_cop": 420000,
                    "occupancy_rate": 0.512,
                    "rooms_range": [10, 25],
                },
                "standard_26_60": {
                    "adr_cop": 350000,
                    "occupancy_rate": 0.512,
                    "rooms_range": [26, 60],
                },
            },
            "caribe": {
                "boutique_10_25": {
                    "adr_cop": 950000,
                    "occupancy_rate": 0.685,
                    "rooms_range": [10, 25],
                },
                "standard_26_60": {
                    "adr_cop": 750000,
                    "occupancy_rate": 0.685,
                    "rooms_range": [26, 60],
                },
            },
            "antioquia": {
                "boutique_10_25": {
                    "adr_cop": 620000,
                    "occupancy_rate": 0.642,
                    "rooms_range": [10, 25],
                },
                "standard_26_60": {
                    "adr_cop": 480000,
                    "occupancy_rate": 0.642,
                    "rooms_range": [26, 60],
                },
            },
            "default": {
                "any": {
                    "adr_cop": 300000,
                    "occupancy_rate": 0.50,
                    "note": "LEGACY fallback",
                }
            },
        },
    }


@pytest.fixture
def resolver_with_regional_json(tmp_path, regional_adr_json_content):
    """RegionalADRResolver backed by regional_adr_2026.json in a temp dir."""
    # Write regional_adr_2026.json
    benchmark_dir = tmp_path / "data" / "benchmarks"
    benchmark_dir.mkdir(parents=True)
    regional_file = benchmark_dir / "regional_adr_2026.json"
    regional_file.write_text(json.dumps(regional_adr_json_content), encoding="utf-8")

    # Write a minimal plan_maestro_data.json (not used but avoids warnings)
    pm_file = benchmark_dir / "plan_maestro_data.json"
    pm_file.write_text(json.dumps({
        "v25_config": {
            "regiones": {
                "eje_cafetero": {"precio_promedio": 330000, "ocupacion": 0.52},
                "caribe": {"precio_promedio": 410000, "ocupacion": 0.66},
                "antioquia": {"precio_promedio": 280000, "ocupacion": 0.60},
                "default": {"precio_promedio": 280000, "ocupacion": 0.50},
            }
        }
    }), encoding="utf-8")

    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        resolver = RegionalADRResolver()
        yield resolver
    finally:
        os.chdir(original_cwd)


@pytest.fixture
def resolver_without_regional_json(tmp_path):
    """RegionalADRResolver when regional_adr_2026.json does NOT exist."""
    benchmark_dir = tmp_path / "data" / "benchmarks"
    benchmark_dir.mkdir(parents=True)
    pm_file = benchmark_dir / "plan_maestro_data.json"
    pm_file.write_text(
        json.dumps({
            "v25_config": {
                "regiones": {
                    "eje_cafetero": {
                        "precio_promedio": 330000,
                        "ocupacion": 0.52,
                        "habitaciones_promedio": 12,
                    }
                }
            }
        }),
        encoding="utf-8",
    )

    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        resolver = RegionalADRResolver()
        yield resolver
    finally:
        os.chdir(original_cwd)


# ---------------------------------------------------------------------------
# T1: regional_adr_2026.json loading
# ---------------------------------------------------------------------------

def test_load_regional_adr_2026_exists(resolver_with_regional_json):
    """regional_adr_2026.json is loaded and accessible."""
    assert resolver_with_regional_json._regional_benchmarks is not None
    assert resolver_with_regional_json._regional_benchmarks.get("version") == "1.0.0"


def test_load_regional_adr_2026_missing_falls_back_to_empty(resolver_without_regional_json):
    """When regional_adr_2026.json is absent, _regional_benchmarks is empty dict."""
    assert resolver_without_regional_json._regional_benchmarks == {}


# ---------------------------------------------------------------------------
# T2: resolve() with epistemic metadata
# ---------------------------------------------------------------------------

def test_resolve_eje_cafetero_boutique(resolver_with_regional_json):
    """Eje Cafetero boutique (10-25 rooms) returns ADR 420,000 with correct metadata."""
    result = resolver_with_regional_json.resolve(region="eje_cafetero", rooms=15)
    assert result.adr_cop == 420000
    assert result.segment == "boutique"
    assert result.region == "eje_cafetero"
    assert result.epistemic_status == "regional_benchmark"
    assert result.can_show_exact is False
    assert result.occupancy_rate == pytest.approx(0.512)


def test_resolve_caribe_boutique(resolver_with_regional_json):
    """Caribe boutique returns ADR 950,000."""
    result = resolver_with_regional_json.resolve(region="caribe", rooms=20)
    assert result.adr_cop == 950000
    assert result.epistemic_status == "regional_benchmark"
    assert result.can_show_exact is False
    assert result.occupancy_rate == pytest.approx(0.685)


def test_resolve_caribe_standard(resolver_with_regional_json):
    """Caribe standard (26-60 rooms) returns ADR 750,000."""
    result = resolver_with_regional_json.resolve(region="caribe", rooms=40)
    assert result.adr_cop == 750000
    assert result.segment == "standard"


def test_resolve_unknown_region_fallback_default(resolver_with_regional_json):
    """Unknown region falls back to default, epistemic_status=defaulted."""
    result = resolver_with_regional_json.resolve(region="unknown_region", rooms=15)
    assert result.adr_cop == 300000  # default.any.adr_cop
    assert result.epistemic_status == "defaulted"
    assert result.source == "regional_adr_2026"


def test_regional_result_can_show_exact_false(resolver_with_regional_json):
    """can_show_exact is always False for regional_benchmark source."""
    for region in ["eje_cafetero", "caribe", "antioquia"]:
        for rooms in [15, 35]:
            result = resolver_with_regional_json.resolve(region=region, rooms=rooms)
            assert result.can_show_exact is False, f"{region}/{rooms} should have can_show_exact=False"


def test_regional_result_has_occupancy(resolver_with_regional_json):
    """occupancy_rate is populated for all known regions."""
    test_cases = [
        ("eje_cafetero", "boutique", 15, 0.512),
        ("eje_cafetero", "standard", 35, 0.512),
        ("caribe", "boutique", 20, 0.685),
        ("caribe", "standard", 45, 0.685),
        ("antioquia", "boutique", 12, 0.642),
        ("antioquia", "standard", 50, 0.642),
    ]
    for region, expected_segment, rooms, expected_occ in test_cases:
        result = resolver_with_regional_json.resolve(region=region, rooms=rooms)
        assert result.occupancy_rate == pytest.approx(expected_occ), f"{region}/{rooms}"
        assert result.segment == expected_segment


def test_regional_result_epistemic_status(resolver_with_regional_json):
    """epistemic_status is 'regional_benchmark' for known regions, never 'VERIFIED'."""
    for region in ["eje_cafetero", "caribe", "antioquia"]:
        result = resolver_with_regional_json.resolve(region=region, rooms=20)
        assert result.epistemic_status == "regional_benchmark", f"{region} should be regional_benchmark"
        # Verify it's NOT the old-style confidence values
        assert result.confidence in ("ESTIMATED", "VERIFIED", "CONFLICT")


def test_segment_determination_boutique_vs_standard(resolver_with_regional_json):
    """Boutique (10-25) vs Standard (26-60) segmentation is correct."""
    # Eje Cafetero: boutique=420000, standard=350000
    boutique = resolver_with_regional_json.resolve(region="eje_cafetero", rooms=15)
    assert boutique.adr_cop == 420000
    assert boutique.segment == "boutique"

    standard = resolver_with_regional_json.resolve(region="eje_cafetero", rooms=35)
    assert standard.adr_cop == 350000
    assert standard.segment == "standard"


# ---------------------------------------------------------------------------
# T3: resolve_occupancy() with regional benchmarks
# ---------------------------------------------------------------------------

def test_resolve_occupancy_regional_first(resolver_with_regional_json):
    """resolve_occupancy() uses regional_adr_2026.json before plan_maestro_data."""
    occ = resolver_with_regional_json.resolve_occupancy("caribe")
    assert occ == pytest.approx(0.685)


def test_resolve_occupancy_unknown_region(resolver_with_regional_json):
    """Unknown region falls back to default occupancy."""
    occ = resolver_with_regional_json.resolve_occupancy("unknown")
    assert occ == pytest.approx(0.50)


# ---------------------------------------------------------------------------
# T4: Fallback to plan_maestro_data when regional_adr_2026.json is missing
# ---------------------------------------------------------------------------

def test_resolve_fallback_to_plan_maestro(resolver_without_regional_json):
    """When regional_adr_2026.json is absent, falls back to plan_maestro_data."""
    result = resolver_without_regional_json.resolve(region="eje_cafetero", rooms=15)
    # plan_maestro_data eje_cafetero precio_promedio = 330000
    assert result.adr_cop == 330000
    assert result.epistemic_status == "legacy_hardcode"
    assert result.source == "plan_maestro_v2.5"


def test_resolve_occupancy_fallback_plan_maestro(resolver_without_regional_json):
    """resolve_occupancy falls back to plan_maestro_data when regional JSON missing."""
    occ = resolver_without_regional_json.resolve_occupancy("eje_cafetero")
    assert occ == pytest.approx(0.52)  # from plan_maestro_data eje_cafetero.ocupacion


# ---------------------------------------------------------------------------
# T5: Module-level convenience function
# ---------------------------------------------------------------------------

def test_resolve_regional_adr_convenience_function(tmp_path, regional_adr_json_content):
    """Module-level resolve_regional_adr() returns RegionalADRResult with epistemic fields."""
    benchmark_dir = tmp_path / "data" / "benchmarks"
    benchmark_dir.mkdir(parents=True)
    (benchmark_dir / "regional_adr_2026.json").write_text(
        json.dumps(regional_adr_json_content), encoding="utf-8"
    )
    (benchmark_dir / "plan_maestro_data.json").write_text(
        json.dumps({
            "v25_config": {
                "regiones": {
                    "eje_cafetero": {"precio_promedio": 330000, "ocupacion": 0.52},
                    "caribe": {"precio_promedio": 410000, "ocupacion": 0.66},
                    "antioquia": {"precio_promedio": 280000, "ocupacion": 0.60},
                    "default": {"precio_promedio": 280000, "ocupacion": 0.50},
                }
            }
        }), encoding="utf-8"
    )

    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        result = resolve_regional_adr(region="antioquia", rooms=20)
    finally:
        os.chdir(original_cwd)

    assert isinstance(result, RegionalADRResult)
    assert result.adr_cop == 620000
    assert result.epistemic_status == "regional_benchmark"
    assert result.can_show_exact is False
    assert result.occupancy_rate == pytest.approx(0.642)
