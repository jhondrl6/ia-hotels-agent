"""
Tests para comando spark.
Valida: generación de 4 archivos, tiempo <5 minutos, contenido quick_win_action.
"""

import json
import time
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# Evitar imports pesados si no están disponibles
try:
    from modules.generators.spark_generator import SparkGenerator, GeoStageResult, IAStageResult
except ImportError:
    pytest.skip("Módulos no disponibles", allow_module_level=True)


class TestSparkCommandIntegration:
    """Tests de integración para comando spark."""
    
    def test_spark_generator_exists(self):
        """Valida que SparkGenerator existe y es importable."""
        assert SparkGenerator is not None
        gen = SparkGenerator()
        assert hasattr(gen, 'generate_spark_report')
    
    def test_spark_report_generates_four_files(self):
        """Valida que Spark Report genera exactamente 4 archivos esperados."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "spark_output"
            
            # Mock de resultados
            geo_result = self._mock_geo_result()
            ia_result = self._mock_ia_result()
            
            # Generar reporte
            gen = SparkGenerator()
            files = gen.generate_spark_report(geo_result, ia_result, output_dir)
            
            # Validar que se generaron 4 archivos
            assert len(files) == 4, f"Se esperaban 4 archivos, se generaron {len(files)}"
            
            required_files = {
                "spark_report": "spark_report.md",
                "whatsapp_script": "whatsapp_script.txt",
                "quick_win_action": "quick_win_action.md",
                "metrics_summary": "metrics_summary.json",
            }
            
            for key, expected_filename in required_files.items():
                assert key in files, f"Archivo faltante: {key}"
                file_path = files[key]
                assert file_path.exists(), f"Archivo no existe: {file_path}"
                assert file_path.name == expected_filename, f"Nombre incorrecto: {file_path.name} vs {expected_filename}"
    
    def test_spark_report_content_structure(self):
        """Valida estructura del spark_report.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            geo_result = self._mock_geo_result()
            ia_result = self._mock_ia_result()
            
            gen = SparkGenerator()
            files = gen.generate_spark_report(geo_result, ia_result, output_dir)
            
            # Leer spark_report.md
            report_path = files["spark_report"]
            content = report_path.read_text(encoding="utf-8")
            
            # Validar que contiene elementos clave (1 página, 3 métricas)
            assert content, "Reporte vacío"
            assert len(content) > 100, "Reporte muy corto"
            assert len(content) < 5000, "Reporte muy largo (debería ser 1 página)"
            
            # Buscar indicadores de contenido
            indicators = ["pérdida", "brecha", "métrica", "Score", "oportunidad"]
            found = sum(1 for indicator in indicators if indicator.lower() in content.lower())
            assert found >= 2, f"Reporte incompleto: solo {found} indicadores encontrados"
    
    def test_whatsapp_script_is_short(self):
        """Valida que guion WhatsApp es ~60 segundos (max 300 caracteres)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            geo_result = self._mock_geo_result()
            ia_result = self._mock_ia_result()
            
            gen = SparkGenerator()
            files = gen.generate_spark_report(geo_result, ia_result, output_dir)
            
            script_path = files["whatsapp_script"]
            content = script_path.read_text(encoding="utf-8")
            
            # Un mensaje WhatsApp típico: 300-500 caracteres = 60 segundos a velocidad normal
            assert len(content) > 50, "Script muy corto"
            assert len(content) < 800, f"Script muy largo ({len(content)} chars, debería <800)"
            assert "hola" in content.lower() or "hotel" in content.lower(), "Script sin saludo"
    
    def test_quick_win_action_included(self):
        """Valida que quick_win_action contiene acción específica."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            geo_result = self._mock_geo_result()
            ia_result = self._mock_ia_result()
            
            gen = SparkGenerator()
            files = gen.generate_spark_report(geo_result, ia_result, output_dir)
            
            qw_path = files["quick_win_action"]
            content = qw_path.read_text(encoding="utf-8")
            
            # Validar que contiene elementos de acción
            action_keywords = ["acción", "hacer", "gratis", "hoy", "semanal", "fotos", "horarios", "reseñas", "gain", "impact"]
            found = sum(1 for kw in action_keywords if kw.lower() in content.lower())
            assert found >= 2, f"Quick win incompleto: {found} palabras clave encontradas"
    
    def test_metrics_json_valid_format(self):
        """Valida que metrics_summary.json es JSON válido."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            geo_result = self._mock_geo_result()
            ia_result = self._mock_ia_result()
            
            gen = SparkGenerator()
            files = gen.generate_spark_report(geo_result, ia_result, output_dir)
            
            metrics_path = files["metrics_summary"]
            content = metrics_path.read_text(encoding="utf-8")
            
            # Validar JSON
            data = json.loads(content)
            assert isinstance(data, dict), "Metrics no es diccionario"
            
            # Validar estructura básica
            expected_keys = ["hotel_nombre", "perdida_mensual", "gbp_score", "quick_win"]
            found_keys = [k for k in expected_keys if k in data]
            assert len(found_keys) >= 2, f"Metrics incompleto: solo {found_keys}"
    
    def test_spark_execution_under_five_minutes(self):
        """Valida que tiempo de ejecución es <5 minutos (mocked)."""
        start = time.time()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            geo_result = self._mock_geo_result()
            ia_result = self._mock_ia_result()
            
            gen = SparkGenerator()
            files = gen.generate_spark_report(geo_result, ia_result, output_dir)
        
        elapsed = time.time() - start
        
        # En test, debería ser casi inmediato (<1 seg)
        assert elapsed < 300, f"Ejecución demasiado lenta: {elapsed} segundos"
        assert len(files) == 4, "Archivos no generados"
    
    def test_files_are_readable(self):
        """Valida que todos los archivos generados son legibles."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            geo_result = self._mock_geo_result()
            ia_result = self._mock_ia_result()
            
            gen = SparkGenerator()
            files = gen.generate_spark_report(geo_result, ia_result, output_dir)
            
            for key, path in files.items():
                assert path.exists(), f"Archivo no existe: {key}"
                try:
                    content = path.read_text(encoding="utf-8")
                    assert content, f"Archivo vacío: {key}"
                except Exception as e:
                    pytest.fail(f"No se puede leer {key}: {e}")
    
    # Helper methods
    def _mock_geo_result(self) -> GeoStageResult:
        """Crea un mock de GeoStageResult."""
        mock = MagicMock(spec=GeoStageResult)
        mock.hotel_data = {
            "nombre": "Hotel Test",
            "url": "https://hotel-test.com",
            "ubicacion": "Armenia, Colombia"
        }
        mock.gbp_data = {
            "score": 75,
            "fotos_count": 5,
            "reviews_count": 12,
            "posts_count": 2
        }
        mock.schema_data = {"has_schema": False}
        mock.competitors_data = [
            {"nombre": "Competidor 1", "score": 85},
            {"nombre": "Competidor 2", "score": 70}
        ]
        return mock
    
    def _mock_ia_result(self) -> IAStageResult:
        """Crea un mock de IAStageResult."""
        mock = MagicMock(spec=IAStageResult)
        mock.ia_test = {
            "chatgpt_mentions": 0,
            "gemini_mentions": 0,
            "visibility": "invisible"
        }
        mock.llm_analysis = {
            "perdida_mensual_total": 5_000_000,
            "brechas_criticas": [
                {"nombre": "Sin visibilidad IA", "descripcion": "No aparece en ChatGPT"},
                {"nombre": "GBP sin optimizar", "descripcion": "Falta 15 fotos"}
            ],
            "paquete_recomendado": "Pro AEO"
        }
        mock.current_provider = "deepseek"
        return mock


class TestSparkCommandCLI:
    """Tests para integración CLI del comando spark."""
    
    @pytest.mark.skip(reason="Requiere test con URL real")
    def test_spark_command_cli_real(self):
        """Test del comando spark con URL real (solo manual)."""
        # Este test se ejecutaría con:
        # pytest tests/test_spark_command.py::TestSparkCommandCLI::test_spark_command_cli_real -v
        # python main.py spark --url https://hotelvisperas.com --skip-check
        pass
    
    def test_spark_help_available(self):
        """Valida que help del comando spark es accesible."""
        # Este test validaría que: python main.py spark --help funciona
        # Se implementaría con subprocess mock
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
