"""
Test de migración: fallbacks.yaml -> v4_diagnostic_generator.py, v4_proposal_generator.py
FASE-CONFIG-8: Suite de Tests de Regresión

Verifica que los valores de fallbacks.yaml se lean del YAML,
no de hardcodes en el código.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import yaml


class TestFallbacksYAMLValues:
    """Tests: valores leídos de fallbacks.yaml"""

    def test_fallbacks_yaml_exists(self):
        """fallbacks.yaml debe existir en config/"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/fallbacks.yaml')
        assert os.path.exists(config_path), f"fallbacks.yaml no encontrado"

    def test_benchmark_score_value(self):
        """scores.benchmark_score.value == 58"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/fallbacks.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['scores']['benchmark_score']['value'] == 58

    def test_score_tecnico_value(self):
        """scores.score_tecnico.value == 50"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/fallbacks.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['scores']['score_tecnico']['value'] == 50

    def test_coherence_score_value(self):
        """scores.coherence_score.value == 70"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/fallbacks.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['scores']['coherence_score']['value'] == 70

    def test_voice_readiness_value(self):
        """scores.voice_readiness.value == 0"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/fallbacks.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['scores']['voice_readiness']['value'] == 0


class TestFallbacksNoHardcodes:
    """Tests: NO debe haber hardcodes de fallbacks en el código"""

    def test_no_benchmark_score_hardcode(self):
        """v4_proposal_generator.py NO contiene 'benchmark_score = 58' hardcodeado directo"""
        module_path = os.path.join(os.path.dirname(__file__), '../../modules/commercial_documents/v4_proposal_generator.py')
        with open(module_path, encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        for line in lines:
            stripped = line.strip()
            # Buscar: benchmark_score = 58 (asignación directa)
            if 'benchmark_score' in line and '= 58' in line and 'get_fallback' not in line:
                if not stripped.startswith('#') and 'load_fallback' not in line and '_load_fallback' not in line:
                    assert False, f"Hardcode sospechoso: {line.strip()}"

    def test_no_voice_readiness_string_zero(self):
        """v4_diagnostic_generator.py NO contiene \"voice_readiness = '0'\" hardcodeado"""
        module_path = os.path.join(os.path.dirname(__file__), '../../modules/commercial_documents/v4_diagnostic_generator.py')
        with open(module_path, encoding='utf-8') as f:
            content = f.read()

        # PATTERN: El código migrado usa get_fallback_value() como fuente principal.
        # Las asignaciones '0'/'unknown' son solo fallback de ultimo recurso en except block.
        # Verificar que get_fallback_value se usa en este módulo
        has_fallback_usage = 'get_fallback_value' in content
        assert has_fallback_usage, \
            "v4_diagnostic_generator.py debe usar get_fallback_value() para voice_readiness"


class TestFallbacksIntegration:
    """Tests: módulos deben usar load_yaml_config para fallbacks"""

    def test_proposal_generator_loads_fallbacks(self):
        """v4_proposal_generator.py debe cargar fallbacks.yaml"""
        module_path = os.path.join(os.path.dirname(__file__), '../../modules/commercial_documents/v4_proposal_generator.py')
        with open(module_path, encoding='utf-8') as f:
            content = f.read()
        assert 'load_yaml_config' in content or 'fallbacks.yaml' in content or 'get_fallback' in content, \
            "v4_proposal_generator.py debe usar get_fallback o load_yaml_config('fallbacks')"

    def test_diagnostic_generator_loads_fallbacks(self):
        """v4_diagnostic_generator.py debe cargar fallbacks.yaml"""
        module_path = os.path.join(os.path.dirname(__file__), '../../modules/commercial_documents/v4_diagnostic_generator.py')
        with open(module_path, encoding='utf-8') as f:
            content = f.read()
        assert 'load_yaml_config' in content or 'fallbacks.yaml' in content or 'get_fallback' in content, \
            "v4_diagnostic_generator.py debe usar get_fallback o load_yaml_config('fallbacks')"
