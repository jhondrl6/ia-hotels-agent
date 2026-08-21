"""Tests de contrato para el Benchmark Maestro Único (FASE-P1-A).

Valida los contratos F2 (eje_cafetero ADR consistente) y F4 (Bogotá cubierta),
además del mecanismo de sincronización entre master y plan_maestro_data.
"""
import json
import pytest
from pathlib import Path

from modules.financial_engine.regional_adr_resolver import (
    RegionalADRResolver,
    resolve_regional_adr,
)


ROOT = Path(__file__).resolve().parent.parent.parent
MASTER_PATH = ROOT / "data" / "benchmarks" / "regional_adr_2026.json"
SECONDARY_PATH = ROOT / "data" / "benchmarks" / "plan_maestro_data.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_master() -> dict:
    with open(MASTER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_secondary() -> dict:
    with open(SECONDARY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# F4: Bogotá resuelve a su valor correcto (no default $300K)
# ---------------------------------------------------------------------------

class TestBogotaCoverage:
    """Bogotá debe resolver a su propio benchmark, no al default."""

    def test_bogota_boutique_adr_not_default(self):
        result = resolve_regional_adr("bogota", rooms=15)
        assert result.adr_cop == 350_000, (
            f"Bogotá boutique should resolve to $350K, got ${result.adr_cop:,.0f}"
        )
        assert result.is_default is False

    def test_bogota_standard_adr_not_default(self):
        result = resolve_regional_adr("bogota", rooms=40)
        assert result.adr_cop == 300_000
        assert result.is_default is False

    def test_bogota_with_accent(self):
        """'bogotá' (con tilde) debe resolver igual que 'bogota'."""
        result = resolve_regional_adr("bogotá", rooms=15)
        assert result.adr_cop == 350_000
        assert result.is_default is False

    def test_bogota_epistemic_not_defaulted(self):
        result = resolve_regional_adr("bogota", rooms=15)
        assert result.epistemic_status != "defaulted", (
            "Bogotá should NOT have epistemic_status=defaulted"
        )

    def test_bogota_occupancy_resolved(self):
        resolver = RegionalADRResolver()
        occ = resolver.resolve_occupancy("bogota")
        assert occ == pytest.approx(0.65), (
            f"Bogotá occupancy should be 0.65, got {occ}"
        )


# ---------------------------------------------------------------------------
# F2: eje_cafetero resuelve a un único valor consistente
# ---------------------------------------------------------------------------

class TestEjeCafeteroConsistency:
    """eje_cafetero ADR debe ser consistente entre master y plan_maestro_data."""

    def test_eje_cafetero_boutique_adr(self):
        result = resolve_regional_adr("eje_cafetero", rooms=15)
        assert result.adr_cop == 280_000, (
            f"Eje Cafetero boutique should be $280K, got ${result.adr_cop:,.0f}"
        )
        assert result.source == "regional_adr_2026"

    def test_eje_cafetero_standard_adr(self):
        result = resolve_regional_adr("eje_cafetero", rooms=40)
        assert result.adr_cop == 260_000

    def test_eje_cafetero_alias_coffee_axis(self):
        """Legacy alias 'coffee_axis' debe resolver a eje_cafetero."""
        result = resolve_regional_adr("coffee_axis", rooms=15)
        assert result.adr_cop == 280_000
        assert result.region == "eje_cafetero"

    def test_eje_cafetero_master_secondary_sync(self):
        """ADR del master boutique debe coincidir con plan_maestro_data eje_cafetero."""
        master = _load_master()
        secondary = _load_secondary()

        master_adr = master["regions"]["eje_cafetero"]["boutique_10_25"]["adr_cop"]
        sec_regiones = secondary.get("v25_config", {}).get("regiones", {})
        secondary_adr = sec_regiones["eje_cafetero"]["precio_promedio"]

        assert master_adr == secondary_adr, (
            f"Master ADR ({master_adr:,}) != plan_maestro ADR ({secondary_adr:,})"
        )


# ---------------------------------------------------------------------------
# Cobertura de todas las regiones del master
# ---------------------------------------------------------------------------

class TestAllRegionsCovered:
    """Todas las regiones del master deben existir en plan_maestro_data."""

    def test_all_master_regions_in_secondary(self):
        master = _load_master()
        secondary = _load_secondary()

        master_regions = set(master["regions"].keys()) - {"default"}
        sec_regiones = secondary.get("v25_config", {}).get("regiones", {})
        secondary_regions = set(sec_regiones.keys()) - {"default"}

        missing = master_regions - secondary_regions
        assert not missing, (
            f"Regions in master but missing in plan_maestro_data: {missing}"
        )

    def test_caribe_adr_sync(self):
        master = _load_master()
        secondary = _load_secondary()

        master_adr = master["regions"]["caribe"]["boutique_10_25"]["adr_cop"]
        sec_regiones = secondary.get("v25_config", {}).get("regiones", {})
        secondary_adr = sec_regiones["caribe"]["precio_promedio"]

        assert master_adr == secondary_adr

    def test_antioquia_adr_sync(self):
        master = _load_master()
        secondary = _load_secondary()

        master_adr = master["regions"]["antioquia"]["boutique_10_25"]["adr_cop"]
        sec_regiones = secondary.get("v25_config", {}).get("regiones", {})
        secondary_adr = sec_regiones["antioquia"]["precio_promedio"]

        assert master_adr == secondary_adr


# ---------------------------------------------------------------------------
# Mecanismo de sincronización detecta divergencia
# ---------------------------------------------------------------------------

class TestSyncMechanism:
    """El script de sincronización detecta divergencias."""

    def test_sync_script_passes_current_state(self):
        """Con los archivos sincronizados, validate_benchmark_sync debe pasar."""
        import subprocess
        result = subprocess.run(
            ["python", str(ROOT / "scripts" / "validate_benchmark_sync.py"), "--quiet"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert result.returncode == 0, (
            f"Sync script failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_sync_detects_adr_divergence(self, tmp_path):
        """Si se edita manualmente el archivo no-master, la divergencia se detecta."""
        import shutil
        # Copiar archivos a tmp
        master_copy = tmp_path / "master.json"
        secondary_copy = tmp_path / "secondary.json"

        master = _load_master()
        secondary = _load_secondary()

        # Introducir divergencia en secondary
        sec_regiones = secondary.get("v25_config", {}).get("regiones", {})
        sec_regiones["eje_cafetero"]["precio_promedio"] = 999_999

        master_copy.write_text(json.dumps(master), encoding="utf-8")
        secondary_copy.write_text(json.dumps(secondary), encoding="utf-8")

        # Importar y probar la función de validación directamente
        from scripts.validate_benchmark_sync import (
            get_master_adr_by_region,
            get_secondary_adr_by_region,
        )

        master_adr = get_master_adr_by_region(master)
        secondary_adr = get_secondary_adr_by_region(secondary)

        # Verificar que la divergencia se detecta
        assert master_adr["eje_cafetero"]["adr_cop"] != secondary_adr["eje_cafetero"]["adr_cop"]


# ---------------------------------------------------------------------------
# Resolver occupancy con normalización (P1-A fix)
# ---------------------------------------------------------------------------

class TestOccupancyNormalization:
    """resolve_occupancy debe aplicar la misma normalización que resolve."""

    def test_occupancy_with_capital_region(self):
        resolver = RegionalADRResolver()
        occ = resolver.resolve_occupancy("Eje Cafetero")
        assert occ == pytest.approx(0.512)

    def test_occupancy_bogota_with_accent(self):
        resolver = RegionalADRResolver()
        occ = resolver.resolve_occupancy("Bogotá")
        assert occ == pytest.approx(0.65)

    def test_occupancy_caribe(self):
        resolver = RegionalADRResolver()
        occ = resolver.resolve_occupancy("caribe")
        assert occ == pytest.approx(0.685)


# ---------------------------------------------------------------------------
# Known regions incluye todas las fuentes (P1-A)
# ---------------------------------------------------------------------------

class TestKnownRegions:
    """_get_known_regions debe incluir regiones de ambos archivos."""

    def test_known_regions_includes_bogota(self):
        resolver = RegionalADRResolver()
        known = resolver._get_known_regions()
        assert "bogota" in known

    def test_known_regions_includes_all_master(self):
        resolver = RegionalADRResolver()
        known = resolver._get_known_regions()
        for region in ["eje_cafetero", "caribe", "antioquia", "bogota"]:
            assert region in known, f"{region} not in known regions: {known}"
