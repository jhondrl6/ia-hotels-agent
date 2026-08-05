"""Tests FASE-D: Política de entrega ZIP (N16 + N21).

Verifica:
- N16: commercial_gates_report* excluido del ZIP de cliente
- N21: filtrado por run más reciente (no 24h fijo)
"""

import json
import time
import zipfile
import pytest
import tempfile
from pathlib import Path
from os import utime

from modules.delivery.delivery_packager import DeliveryPackager


class TestGateReportExclusion:
    """N16: commercial_gates_report* no viaja al cliente."""

    def test_is_excluded_matches_plain_report(self):
        """_is_excluded_from_zip detecta commercial_gates_report.json."""
        assert DeliveryPackager._is_excluded_from_zip("commercial_gates_report.json") is True

    def test_is_excluded_matches_diagnostic_report(self):
        """_is_excluded_from_zip detecta commercial_gates_report_diagnostic_*.json."""
        assert DeliveryPackager._is_excluded_from_zip(
            "commercial_gates_report_diagnostic_20260804_123637.json"
        ) is True

    def test_is_excluded_ignores_asset_generation_report(self):
        """_is_excluded_from_zip NO excluye asset_generation_report.json."""
        assert DeliveryPackager._is_excluded_from_zip("asset_generation_report.json") is False

    def test_is_excluded_ignores_other_files(self):
        """_is_excluded_from_zip NO excluye archivos normales."""
        assert DeliveryPackager._is_excluded_from_zip("hotel-schema.json") is False
        assert DeliveryPackager._is_excluded_from_zip("geo_playbook.md") is False
        assert DeliveryPackager._is_excluded_from_zip("financial_scenarios.json") is False

    def test_zip_excludes_gate_reports(self, tmp_path):
        """ZIP de cliente no contiene commercial_gates_report*."""
        # Setup: crear estructura de hotel con gate reports
        hotel_dir = tmp_path / "output" / "hotel_test"
        hotel_dir.mkdir(parents=True)
        v4_audit = hotel_dir / "v4_audit"
        v4_audit.mkdir()

        # Archivo normal (debe ir)
        (v4_audit / "asset_generation_report.json").write_text(
            '{"status": "ok"}', encoding="utf-8"
        )
        # Gate report del diagnóstico (NO debe ir)
        (v4_audit / "commercial_gates_report_diagnostic_20260804.json").write_text(
            '{"all_passed": false}', encoding="utf-8"
        )
        # Gate report de propuesta (NO debe ir)
        (v4_audit / "commercial_gates_report.json").write_text(
            '{"blocking_passed": false}', encoding="utf-8"
        )
        # Asset normal en raíz
        (hotel_dir / "hotel-schema.json").write_text('{"@type": "Hotel"}', encoding="utf-8")

        deliveries_dir = tmp_path / "deliveries"
        deliveries_dir.mkdir()

        packager = DeliveryPackager(
            base_output_dir=str(tmp_path / "output"),
            deliveries_dir=str(deliveries_dir),
        )
        zip_path = packager.package(
            hotel_id="hotel_test",
            output_dir=str(hotel_dir),
        )

        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            gate_files = [n for n in names if "commercial_gates_report" in n]
            assert gate_files == [], f"ZIP should not contain gate reports, found: {gate_files}"
            # Verificar que asset_generation_report SÍ está
            asset_reports = [n for n in names if "asset_generation_report" in n]
            assert len(asset_reports) == 1, "asset_generation_report should be in ZIP"


class TestRunBasedFiltering:
    """N21: filtrado por timestamp del run más reciente."""

    def test_get_latest_run_timestamp_finds_latest(self, tmp_path):
        """_get_latest_run_timestamp retorna el mtime más reciente."""
        v4_audit = tmp_path / "v4_audit"
        v4_audit.mkdir()

        # Crear archivos con mtimes distintos
        old_file = v4_audit / "old_report.json"
        new_file = v4_audit / "new_report.json"
        old_file.write_text("{}", encoding="utf-8")
        new_file.write_text("{}", encoding="utf-8")

        # Set mtimes: old = 1000s ago, new = now
        now = time.time()
        utime(str(old_file), (now - 1000, now - 1000))
        utime(str(new_file), (now - 10, now - 10))

        result = DeliveryPackager._get_latest_run_timestamp(v4_audit)
        assert result is not None
        # Should be close to now - 10 (within 1s tolerance)
        assert abs(result - (now - 10)) < 1.0

    def test_get_latest_run_timestamp_excludes_gate_reports(self, tmp_path):
        """_get_latest_run_timestamp ignora commercial_gates_report*."""
        v4_audit = tmp_path / "v4_audit"
        v4_audit.mkdir()

        # Gate report con mtime más reciente (debe ignorarse)
        gate_file = v4_audit / "commercial_gates_report.json"
        gate_file.write_text("{}", encoding="utf-8")
        now = time.time()
        utime(str(gate_file), (now, now))

        # Archivo normal con mtime más antiguo
        normal_file = v4_audit / "asset_generation_report.json"
        normal_file.write_text("{}", encoding="utf-8")
        utime(str(normal_file), (now - 500, now - 500))

        result = DeliveryPackager._get_latest_run_timestamp(v4_audit)
        assert result is not None
        # Should match normal_file mtime, NOT gate_file
        assert abs(result - (now - 500)) < 1.0

    def test_get_latest_run_timestamp_empty_dir(self, tmp_path):
        """_get_latest_run_timestamp retorna None si v4_audit vacío."""
        v4_audit = tmp_path / "v4_audit"
        v4_audit.mkdir()
        assert DeliveryPackager._get_latest_run_timestamp(v4_audit) is None

    def test_get_latest_run_timestamp_missing_dir(self, tmp_path):
        """_get_latest_run_timestamp retorna None si directorio no existe."""
        assert DeliveryPackager._get_latest_run_timestamp(tmp_path / "nonexistent") is None

    def test_zip_filters_stale_v4_audit_artifacts(self, tmp_path):
        """ZIP filtra artefactos de runs anteriores en v4_audit."""
        hotel_dir = tmp_path / "output" / "hotel_test"
        hotel_dir.mkdir(parents=True)
        v4_audit = hotel_dir / "v4_audit"
        v4_audit.mkdir()

        now = time.time()
        # Artefacto del run actual (debe ir)
        current_file = v4_audit / "financial_scenarios.json"
        current_file.write_text('{"scenarios": {}}', encoding="utf-8")
        utime(str(current_file), (now - 5, now - 5))

        # Artefacto de un run anterior (NO debe ir — 2 horas antes)
        stale_file = v4_audit / "financial_scenarios_old.json"
        stale_file.write_text('{"scenarios": "stale"}', encoding="utf-8")
        utime(str(stale_file), (now - 7200, now - 7200))

        # Asset en raíz (siempre va)
        (hotel_dir / "hotel-schema.json").write_text('{"@type": "Hotel"}', encoding="utf-8")

        deliveries_dir = tmp_path / "deliveries"
        deliveries_dir.mkdir()

        packager = DeliveryPackager(
            base_output_dir=str(tmp_path / "output"),
            deliveries_dir=str(deliveries_dir),
        )
        zip_path = packager.package(
            hotel_id="hotel_test",
            output_dir=str(hotel_dir),
        )

        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            current_in_zip = any("financial_scenarios.json" in n for n in names)
            stale_in_zip = any("financial_scenarios_old.json" in n for n in names)
            assert current_in_zip, "Current run artifact should be in ZIP"
            assert not stale_in_zip, "Stale run artifact should NOT be in ZIP"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
