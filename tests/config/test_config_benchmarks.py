"""
Test de migración: regional_benchmarks.yaml -> v4_diagnostic_generator.py
FASE-CONFIG-8: Suite de Tests de Regresión

Verifica que los valores de regional_benchmarks.yaml se lean del YAML,
no de hardcodes en el código.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import yaml


class TestBenchmarksYAMLValues:
    """Tests: valores leídos de regional_benchmarks.yaml"""

    def test_benchmarks_yaml_exists(self):
        """regional_benchmarks.yaml debe existir en config/"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/regional_benchmarks.yaml')
        assert os.path.exists(config_path), f"regional_benchmarks.yaml no encontrado"

    def test_eje_cafetero_no_whatsapp_visible(self):
        """regions.eje_cafetero.pain_narratives.no_whatsapp_visible == 0.20"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/regional_benchmarks.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['regions']['eje_cafetero']['pain_narratives']['no_whatsapp_visible'] == 0.20

    def test_eje_cafetero_no_hotel_schema(self):
        """regions.eje_cafetero.pain_narratives.no_hotel_schema == 0.25"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/regional_benchmarks.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['regions']['eje_cafetero']['pain_narratives']['no_hotel_schema'] == 0.25

    def test_eje_cafotero_low_gbp_score(self):
        """regions.eje_cafetero.pain_narratives.low_gbp_score == 0.30"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/regional_benchmarks.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['regions']['eje_cafetero']['pain_narratives']['low_gbp_score'] == 0.30

    def test_eje_cafetero_confidence_thresholds(self):
        """confidence.high == 0.85, medium == 0.70, low == 0.40"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/regional_benchmarks.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        c = data['regions']['eje_cafetero']['confidence']
        assert c['high'] == 0.85
        assert c['medium'] == 0.70
        assert c['low'] == 0.40

    def test_eje_cafetero_gbp_geo_score_threshold(self):
        """gbp_geo_score_threshold == 70"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/regional_benchmarks.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['regions']['eje_cafetero']['gbp_geo_score_threshold'] == 70

    def test_eje_cafetero_mobile_score_threshold(self):
        """mobile_score_threshold == 50"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/regional_benchmarks.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['regions']['eje_cafetero']['mobile_score_threshold'] == 50


class TestBenchmarksNoHardcodes:
    """Tests: NO debe haber hardcodes de benchmarks en el código"""

    def test_no_no_whatsapp_visible_hardcode(self):
        """v4_diagnostic_generator.py NO contiene 'no_whatsapp_visible': 0.20 hardcodeado"""
        module_path = os.path.join(os.path.dirname(__file__), '../../modules/commercial_documents/v4_diagnostic_generator.py')
        with open(module_path, encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        for line in lines:
            stripped = line.strip()
            # Buscar: 'no_whatsapp_visible': 0.20 (hardcodeado, no de YAML)
            if 'no_whatsapp_visible' in line and '0.20' in line and 'get(' not in line and '.get(' not in line:
                if not stripped.startswith('#') and 'pain_narratives' not in line:
                    assert False, f"Hardcode sospechoso: {line.strip()}"


class TestBenchmarksIntegration:
    """Tests: módulos deben usar load_yaml_config para benchmarks"""

    def test_diagnostic_generator_loads_benchmarks(self):
        """v4_diagnostic_generator.py debe cargar regional_benchmarks.yaml"""
        module_path = os.path.join(os.path.dirname(__file__), '../../modules/commercial_documents/v4_diagnostic_generator.py')
        with open(module_path, encoding='utf-8') as f:
            content = f.read()
        assert 'load_yaml_config' in content or 'regional_benchmarks.yaml' in content, \
            "v4_diagnostic_generator.py debe usar load_yaml_config('regional_benchmarks')"
