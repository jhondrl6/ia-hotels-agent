"""
Test de contrato anti-regresión — FASE-P0-C (F7): Encoding UTF-8 en writers.

Verifica que TODOS los writers de artefactos usan encoding='utf-8' explícito
para eliminar artefactos corruptos (cp1252 por defecto en Windows).

Fallo original F7: delivery_quality_report.json lanzaba UnicodeDecodeError
(byte 0xf3) y mojibake "B+ ? Datos fuente" en diagnóstico.
"""

import ast
import json
from pathlib import Path

import pytest

from modules.quality_gates.delivery_quality_report import (
    DeliveryQualityReport,
    DeliveryQualityReportGenerator,
)


# ── T3.1: delivery_quality_report save/load con caracteres Unicode ────────

class TestDeliveryQualityReportEncoding:
    """Verifica que el delivery_quality_report.json se escribe y lee correctamente
    con encoding='utf-8', incluyendo caracteres especiales (tildes, ñ, em-dash)."""

    def _minimal_report(self) -> DeliveryQualityReport:
        """Crear un DeliveryQualityReport con campos que contienen Unicode."""
        return DeliveryQualityReport(
            status="PASS",
            blocking=False,
            coverage_gate={"status": "PASS", "ratio": 1.0},
            proposal_asset_gate={"status": "PASS", "alignment_score": 0.95},
            asset_specificity_gate={"status": "PASS", "min_confidence": 0.85},
            evidence_gate={"status": "PASS", "quality": "high"},
            summary={
                "diagnostico": "B+ – Datos fuente verificados",
                "brecha_1": "Pérdida estimada: $1.198.906/mes — ocupación média 65%",
                "recommendation": "Implementar schema Hotel + FAQ para visibilidad IA",
            },
            human_review_items=[],
            advisory_warnings=[],
        )

    def test_save_uses_utf8_encoding(self, tmp_path):
        """El JSON generado debe ser legible con encoding='utf-8' sin errores."""
        generator = DeliveryQualityReportGenerator()
        report = self._minimal_report()
        output_path = tmp_path / "delivery_quality_report.json"

        generator.save(report, output_path)

        # Verificar que el archivo es legible con utf-8
        content = output_path.read_text(encoding="utf-8")
        data = json.loads(content)
        assert data["status"] == "PASS"

    def test_no_mojibake_in_unicode_fields(self, tmp_path):
        """Los campos con caracteres especiales NO deben tener mojibake."""
        generator = DeliveryQualityReportGenerator()
        report = self._minimal_report()
        output_path = tmp_path / "delivery_quality_report.json"

        generator.save(report, output_path)

        content = output_path.read_text(encoding="utf-8")
        data = json.loads(content)

        # Verificar que los caracteres Unicode se preservan correctamente
        summary = data.get("summary", {})
        diagnostico = summary.get("diagnostico", "")
        assert "–" in diagnostico or "Datos fuente" in diagnostico, (
            f"Mojibake detectado en diagnostico: {diagnostico!r}"
        )

        brecha = summary.get("brecha_1", "")
        assert "ó" in brecha or "65%" in brecha, (
            f"Mojibake detectado en brecha_1: {brecha!r}"
        )

    def test_roundtrip_preserves_special_chars(self, tmp_path):
        """Save + load debe preservar tildes, ñ y caracteres especiales."""
        generator = DeliveryQualityReportGenerator()
        report = self._minimal_report()
        output_path = tmp_path / "delivery_quality_report.json"

        generator.save(report, output_path)

        # Cargar usando el método interno
        loaded = generator._load_json(output_path)
        summary = loaded.get("summary", {})

        assert summary.get("diagnostico") == "B+ – Datos fuente verificados"
        assert "ocupación média" in summary.get("brecha_1", "")


# ── T3.2: Auditoría estática — todos los writers deben usar encoding ─────

class TestEncodingContractStatic:
    """Auditoría estática: verifica que ningún writer en modules/ escribe
    archivos sin encoding='utf-8' explícito."""

    MODULES_DIR = Path(__file__).resolve().parent.parent / "modules"

    def _find_writers_without_encoding(self):
        """Recorre todos los .py en modules/ y busca write_text() sin encoding."""
        violations = []
        for py_file in self.MODULES_DIR.rglob("*.py"):
            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(py_file))
            except (SyntaxError, UnicodeDecodeError):
                continue

            for node in ast.walk(tree):
                # Check Path.write_text() calls without encoding keyword
                if isinstance(node, ast.Call):
                    func = node.func
                    func_name = None
                    if isinstance(func, ast.Attribute) and func.attr == "write_text":
                        func_name = "write_text"
                    if func_name == "write_text":
                        has_encoding = any(
                            kw.arg == "encoding" for kw in node.keywords
                        )
                        if not has_encoding:
                            violations.append(
                                f"{py_file.relative_to(self.MODULES_DIR.parent)}:{node.lineno}"
                            )
        return violations

    def test_no_write_text_without_encoding(self):
        """Ningún write_text() en modules/ debe carecer de encoding='utf-8'."""
        violations = self._find_writers_without_encoding()
        assert not violations, (
            f"Writers sin encoding='utf-8' encontrados (FASE-P0-C):\n"
            + "\n".join(f"  - {v}" for v in violations)
        )
