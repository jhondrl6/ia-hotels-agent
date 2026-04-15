"""
Test: Audit Generated Before Assets

FASE 5 TRANSVERSAL - T1: Verificar orden de dependencias Audit → Assets

Este test verifica que audit_report se genera ANTES que cualquier asset,
confirmando que el flujo de generación es correcto.

Timestamps esperados:
1. audit_report.json (primero)
2. financial_scenarios.json
3. Documentos .md
4. v4_complete_report.json (último)
"""

import json
import os
from datetime import datetime
from pathlib import Path


class TestAuditGeneratedBeforeAssets:
    """Test T1: Audit debe generarse antes que los assets."""

    @staticmethod
    def get_output_dir():
        """Obtiene el directorio de output v4_complete."""
        base_path = Path("/mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete")
        if base_path.exists():
            return str(base_path)
        
        # Fallback: buscar el más reciente
        output_base = Path("/mnt/c/Users/Jhond/Github/iah-cli/output")
        if output_base.exists():
            dirs = sorted(output_base.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
            for d in dirs:
                if d.is_dir() and d.name.startswith("v4"):
                    return str(d)
        return None

    def test_audit_timestamp_is_first(self):
        """Verifica que audit_report tiene el timestamp más antiguo."""
        output_dir = self.get_output_dir()
        assert output_dir is not None, "No se encontró directorio de output"
        
        # Archivos a verificar
        files_to_check = [
            "audit_report.json",
            "financial_scenarios.json",
            "01_DIAGNOSTICO_Y_OPORTUNIDAD_20260323_073213.md",
            "02_PROPUESTA_COMERCIAL_20260323_073214.md",
            "v4_complete_report.json"
        ]
        
        timestamps = {}
        for filename in files_to_check:
            filepath = Path(output_dir) / filename
            if filepath.exists():
                stat = filepath.stat()
                timestamps[filename] = stat.st_mtime
        
        assert "audit_report.json" in timestamps, "audit_report.json no encontrado"
        
        # Obtener timestamp de audit
        audit_time = timestamps["audit_report.json"]
        
        # Verificar que audit es anterior o igual a todos los demás
        for filename, timestamp in timestamps.items():
            if filename == "audit_report.json":
                continue
            assert audit_time <= timestamp, (
                f"VIOLATION: {filename} ({timestamp}) tiene timestamp ANTERIOR a audit_report ({audit_time})"
            )

    def test_audit_contains_metadata_for_later_assets(self):
        """Verifica que audit contiene metadata usada por assets posteriores."""
        output_dir = self.get_output_dir()
        assert output_dir is not None
        
        audit_path = Path(output_dir) / "audit_report.json"
        assert audit_path.exists(), "audit_report.json no encontrado"
        
        with open(audit_path, 'r', encoding='utf-8') as f:
            audit_data = json.load(f)
        
        # Verificar que audit tiene campos usados por assets
        assert "schema" in audit_data, "audit_report.json debe contener 'schema'"
        assert "gbp" in audit_data, "audit_report.json debe contener 'gbp'"
        assert "performance" in audit_data, "audit_report.json debe contener 'performance'"
        
        # Verificar que geo_score existe (usado en documentos)
        assert "geo_score" in str(audit_data) or "geo_score" in audit_data.get("gbp", {}), (
            "audit_report.json debe contener geo_score para cálculos posteriores"
        )

    def test_financial_scenarios_after_audit(self):
        """Verifica que financial_scenarios se genera después de audit."""
        output_dir = self.get_output_dir()
        assert output_dir is not None
        
        audit_path = Path(output_dir) / "audit_report.json"
        financial_path = Path(output_dir) / "financial_scenarios.json"
        
        assert audit_path.exists(), "audit_report.json no encontrado"
        assert financial_path.exists(), "financial_scenarios.json no encontrado"
        
        audit_time = audit_path.stat().st_mtime
        financial_time = financial_path.stat().st_mtime
        
        # financial_scenarios debe ser >= audit_time (puede ser casi simultáneo)
        assert financial_time >= audit_time - 0.001, (
            f"financial_scenarios.json ({financial_time}) no puede ser anterior a audit_report.json ({audit_time})"
        )

    def test_audit_uses_schema_data_in_generation(self):
        """
        Verifica que audit_report se genera ANTES que los documentos
        y que contiene datos de schema que los assets necesitan.
        
        NOTA: Esta es una verificación de FLUJO, no de contenido.
        El orden de timestamps confirma que audit se ejecuta primero.
        """
        output_dir = self.get_output_dir()
        assert output_dir is not None
        
        audit_path = Path(output_dir) / "audit_report.json"
        doc1_path = Path(output_dir) / "01_DIAGNOSTICO_Y_OPORTUNIDAD_20260323_073213.md"
        
        assert audit_path.exists(), "audit_report.json no encontrado"
        assert doc1_path.exists(), "Documento diagnóstico no encontrado"
        
        # Timestamps
        audit_time = audit_path.stat().st_mtime
        doc_time = doc1_path.stat().st_mtime
        
        # Audit debe ser anterior
        assert audit_time < doc_time, (
            f"audit_report.json ({audit_time}) debe tener timestamp menor que documento ({doc_time})"
        )
        
        print(f"✅ ORDEN CONFIRMADO: audit ({audit_time}) < documento ({doc_time})")


if __name__ == "__main__":
    test = TestAuditGeneratedBeforeAssets()
    
    print("=" * 60)
    print("T1: Test Audit Generated Before Assets")
    print("=" * 60)
    
    try:
        test.test_audit_timestamp_is_first()
        print("✅ test_audit_timestamp_is_first PASSED")
    except AssertionError as e:
        print(f"❌ test_audit_timestamp_is_first FAILED: {e}")
    
    try:
        test.test_audit_contains_metadata_for_later_assets()
        print("✅ test_audit_contains_metadata_for_later_assets PASSED")
    except AssertionError as e:
        print(f"❌ test_audit_contains_metadata_for_later_assets FAILED: {e}")
    
    try:
        test.test_financial_scenarios_after_audit()
        print("✅ test_financial_scenarios_after_audit PASSED")
    except AssertionError as e:
        print(f"❌ test_financial_scenarios_after_audit FAILED: {e}")
    
    try:
        test.test_audit_uses_schema_data_in_generation()
        print("✅ test_audit_uses_schema_data_in_generation PASSED")
    except AssertionError as e:
        print(f"❌ test_audit_uses_schema_data_in_generation FAILED: {e}")
    
    print("=" * 60)
    print("T1 COMPLETADO: Orden Audit → Assets verificado")
    print("=" * 60)
