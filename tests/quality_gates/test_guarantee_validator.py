"""
Tests for Guarantee Validator — Garantía Día 55 (ROICR FASE-4B).

Tests:
- KPIs mejorados → no trigger
- KPIs sin mejora → trigger + CREDIT_NOTE generada
- Sin baseline → error controlado
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from modules.analytics.guarantee_validator import (
    validar_garantia_dia55,
    load_baseline,
    calculate_improvement,
    BaselineKPIs,
    CurrentKPIs,
    GuaranteeResult,
    DEFAULT_IMPROVEMENT_THRESHOLD,
)


class TestLoadBaseline:
    """Tests para load_baseline."""

    def test_load_baseline_yaml(self):
        """Carga baseline desde YAML de onboarding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            hotel_dir = base / "test_hotel"
            onboarding_dir = hotel_dir / "onboarding"
            onboarding_dir.mkdir(parents=True)
            
            (onboarding_dir / "onboarding_data.yaml").write_text(
                "datos_operativos:\n"
                "  impressions: 10000\n"
                "  clicks: 500\n"
                "  avg_position: 15.0\n"
                "  ctr: 2.5\n"
                "metadatos:\n"
                "  fecha_captura: '2026-01-01'\n",
                encoding="utf-8"
            )
            
            baseline = load_baseline("test_hotel", output_base=base)
            
            assert baseline.impressions == 10000
            assert baseline.clicks == 500
            assert baseline.avg_position == 15.0
            assert baseline.ctr == 2.5
            assert baseline.recorded_at == "2026-01-01"

    def test_load_baseline_not_found_raises(self):
        """Sin archivo de onboarding → FileNotFoundError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            
            with pytest.raises(FileNotFoundError):
                load_baseline("nonexistent_hotel", output_base=base)

    def test_load_baseline_with_data_yaml(self):
        """Carga baseline desde data.yaml alternativo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            hotel_dir = base / "test_hotel"
            onboarding_dir = hotel_dir / "onboarding"
            onboarding_dir.mkdir(parents=True)
            
            (onboarding_dir / "data.yaml").write_text(
                "datos_operativos:\n"
                "  impressions: 20000\n"
                "  clicks: 1000\n"
                "  avg_position: 10.0\n",
                encoding="utf-8"
            )
            
            baseline = load_baseline("test_hotel", output_base=base)
            
            assert baseline.impressions == 20000
            assert baseline.clicks == 1000


class TestCalculateImprovement:
    """Tests para calculate_improvement."""

    def test_positive_improvement(self):
        """KPIs mejoraron → valores positivos."""
        baseline = BaselineKPIs(
            impressions=10000, clicks=500, avg_position=20.0, ctr=2.0
        )
        current = CurrentKPIs(
            impressions=12000, clicks=600, avg_position=15.0, ctr=2.5
        )
        
        improvement = calculate_improvement(baseline, current)
        
        assert improvement["impressions_pct"] == pytest.approx(0.2, rel=0.01)
        assert improvement["clicks_pct"] == pytest.approx(0.2, rel=0.01)
        assert improvement["position_improvement"] == pytest.approx(5.0, abs=0.1)
        assert improvement["ctr_pct"] == pytest.approx(0.25, rel=0.01)

    def test_no_improvement(self):
        """KPIs sin cambio → 0%."""
        baseline = BaselineKPIs(
            impressions=10000, clicks=500, avg_position=15.0, ctr=2.0
        )
        current = CurrentKPIs(
            impressions=10000, clicks=500, avg_position=15.0, ctr=2.0
        )
        
        improvement = calculate_improvement(baseline, current)
        
        assert improvement["impressions_pct"] == 0.0
        assert improvement["clicks_pct"] == 0.0
        assert improvement["position_improvement"] == 0.0

    def test_negative_improvement(self):
        """KPIs empeoraron → valores negativos."""
        baseline = BaselineKPIs(
            impressions=10000, clicks=500, avg_position=10.0, ctr=2.0
        )
        current = CurrentKPIs(
            impressions=8000, clicks=400, avg_position=15.0, ctr=1.5
        )
        
        improvement = calculate_improvement(baseline, current)
        
        assert improvement["impressions_pct"] == pytest.approx(-0.2, rel=0.01)
        assert improvement["clicks_pct"] == pytest.approx(-0.2, rel=0.01)
        assert improvement["position_improvement"] == pytest.approx(-5.0, abs=0.1)


class TestValidarGarantiaDia55:
    """Tests de integración para validar_garantia_dia55."""

    def _make_onboarding(self, base: Path, hotel_id: str, impressions=10000, clicks=500):
        """Helper: crea archivo de onboarding."""
        hotel_dir = base / hotel_id
        onboarding_dir = hotel_dir / "onboarding"
        onboarding_dir.mkdir(parents=True)
        
        (onboarding_dir / "onboarding_data.yaml").write_text(
            f"datos_operativos:\n"
            f"  impressions: {impressions}\n"
            f"  clicks: {clicks}\n"
            f"  avg_position: 20.0\n"
            f"  ctr: 2.0\n"
            f"metadatos:\n"
            f"  fecha_captura: '2026-01-01'\n",
            encoding="utf-8"
        )

    def test_kpis_mejorados_no_trigger(self):
        """KPIs mejoran → garantía NO se activa."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            hotel_id = "test_hotel"
            self._make_onboarding(base, hotel_id)
            
            # Stub GSC con datos mejores
            import modules.analytics.guarantee_validator as gv
            orig_get = gv.get_current_gsc_data
            
            def better_gsc(url, days=55):
                return CurrentKPIs(
                    impressions=13000,  # +30%
                    clicks=700,       # +40%
                    avg_position=12.0,  # mejora de 20→12
                    ctr=3.0,
                    recorded_at=datetime.now().isoformat(),
                    is_simulated=True,
                )
            
            gv.get_current_gsc_data = better_gsc
            
            try:
                result = validar_garantia_dia55(
                    hotel_url="https://test_hotel.com",
                    hotel_id=hotel_id,
                    output_base=base,
                )
            finally:
                gv.get_current_gsc_data = orig_get
            
            assert result.triggered is False
            assert "NO activada" in result.message
            assert result.credit_note_path is None
            assert result.billing_adjustment_path is None

    def test_kpis_sin_mejora_trigger(self):
        """KPIs sin mejora → garantía SÍ se activa + archivos generados."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            hotel_id = "test_hotel2"
            self._make_onboarding(base, hotel_id)
            
            import modules.analytics.guarantee_validator as gv
            orig_get = gv.get_current_gsc_data
            
            def no_improvement_gsc(url, days=55):
                # Mismos datos que baseline
                return CurrentKPIs(
                    impressions=10000,
                    clicks=500,
                    avg_position=20.0,
                    ctr=2.0,
                    recorded_at=datetime.now().isoformat(),
                    is_simulated=True,
                )
            
            gv.get_current_gsc_data = no_improvement_gsc
            
            try:
                result = validar_garantia_dia55(
                    hotel_url="https://test_hotel2.com",
                    hotel_id=hotel_id,
                    output_base=base,
                )
            finally:
                gv.get_current_gsc_data = orig_get
            
            assert result.triggered is True
            assert "ACTIVADA" in result.message
            assert result.credit_note_path is not None
            assert result.billing_adjustment_path is not None
            assert result.credit_note_path.exists()
            assert result.billing_adjustment_path.exists()
            
            # Verifica contenido de CREDIT_NOTE
            content = result.credit_note_path.read_text(encoding="utf-8")
            assert "Garantía Día 55" in content
            assert "CREDIT_NOTE" in content or "Nota de Crédito" in content

    def test_sin_baseline_raises(self):
        """Sin archivo de onboarding → FileNotFoundError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            
            import modules.analytics.guarantee_validator as gv
            orig_get = gv.get_current_gsc_data
            
            def stub_gsc(url, days=55):
                return CurrentKPIs(
                    impressions=10000, clicks=500, avg_position=15.0, ctr=2.0,
                    recorded_at=datetime.now().isoformat(), is_simulated=True,
                )
            
            gv.get_current_gsc_data = stub_gsc
            
            try:
                with pytest.raises(FileNotFoundError):
                    validar_garantia_dia55(
                        hotel_url="https://orphan.com",
                        hotel_id="orphan_hotel",
                        output_base=base,
                    )
            finally:
                gv.get_current_gsc_data = orig_get


class TestGuaranteeResult:
    """Tests para GuaranteeResult.to_dict()."""

    def test_to_dict_complete(self):
        """to_dict()包含所有 campos."""
        baseline = BaselineKPIs(impressions=10000, clicks=500, avg_position=15.0, ctr=2.0, recorded_at="2026-01-01")
        current = CurrentKPIs(impressions=8000, clicks=400, avg_position=18.0, ctr=1.5, recorded_at="2026-03-01", is_simulated=True)
        
        result = GuaranteeResult(
            triggered=True,
            baseline=baseline,
            current=current,
            improvement={"impressions_pct": -0.2, "clicks_pct": -0.2},
            guarantee_dir=Path("/tmp/guarantees"),
            credit_note_path=Path("/tmp/guarantees/CREDIT_NOTE.md"),
            billing_adjustment_path=Path("/tmp/guarantees/billing_adjustment.yaml"),
            message="Garantía activada",
        )
        
        d = result.to_dict()
        
        assert d["triggered"] is True
        assert d["baseline"]["impressions"] == 10000
        assert d["current"]["is_simulated"] is True
        assert d["improvement"]["impressions_pct"] == -0.2
        assert "CREDIT_NOTE.md" in d["credit_note_path"]