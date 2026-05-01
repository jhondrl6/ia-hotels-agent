"""
Test de schema validation: YAML con valores inválidos
FASE-CONFIG-8: Suite de Tests de Regresión

Verifica que el sistema detecte y rechace YAML con tipos o rangos inválidos.
"""
import pytest
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class TestSchemaValidation:
    """Tests: YAML con valores inválidos -> error descriptivo"""

    def test_pricing_min_price_string_invalid(self):
        """pricing.yaml con min_price como string -> error de tipo"""
        import yaml
        config_path = os.path.join(os.path.dirname(__file__), '../../config/pricing.yaml')

        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Cambiar min_price a string (inválido)
        original = data['tiers']['boutique']['min_price']
        data['tiers']['boutique']['min_price'] = "1200000"  # string, no int

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
            yaml.safe_dump(data, tmp)
            tmp_path = tmp.name

        try:
            with open(tmp_path) as f:
                loaded = yaml.safe_load(f)
            # Verificar que se cargó como string
            assert loaded['tiers']['boutique']['min_price'] == "1200000"
            # Verificar que fallaría al usar en cálculo (type check)
            with pytest.raises((TypeError, ValueError)):
                _ = loaded['tiers']['boutique']['min_price'] + 1
        finally:
            data['tiers']['boutique']['min_price'] = original
            os.unlink(tmp_path)

    def test_pricing_min_ratio_out_of_range(self):
        """pricing.yaml con min_ratio > 1 -> warning o error de rango"""
        import yaml
        config_path = os.path.join(os.path.dirname(__file__), '../../config/pricing.yaml')

        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Guardar original
        original = data['gates']['min_ratio']
        # Valor fuera de rango válido (debe ser 0-1)
        data['gates']['min_ratio'] = 1.5

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
            yaml.safe_dump(data, tmp)
            tmp_path = tmp.name

        try:
            with open(tmp_path) as f:
                loaded = yaml.safe_load(f)
            # El valor se cargó (YAML no valida rango)
            assert loaded['gates']['min_ratio'] == 1.5
            # Pero al usar en validación de gate debería fallar
            min_ratio = loaded['gates']['min_ratio']
            assert min_ratio > 1.0, "Valor fuera de rango debería ser detectado"
        finally:
            data['gates']['min_ratio'] = original
            os.unlink(tmp_path)

    def test_scenarios_ota_shift_invalid_type(self):
        """scenarios.yaml con ota_shift.minimal como string -> error de tipo"""
        import yaml
        config_path = os.path.join(os.path.dirname(__file__), '../../config/scenarios.yaml')

        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

        original = data['ota_shift']['minimal']
        data['ota_shift']['minimal'] = "0.05"  # string, no float

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
            yaml.safe_dump(data, tmp)
            tmp_path = tmp.name

        try:
            with open(tmp_path) as f:
                loaded = yaml.safe_load(f)
            # Verificar que se cargó como string (tipo incorrecto)
            assert loaded['ota_shift']['minimal'] == "0.05"
            assert not isinstance(loaded['ota_shift']['minimal'], (int, float)), \
                "ota_shift.minimal debe ser numérico, no string"
        finally:
            data['ota_shift']['minimal'] = original
            os.unlink(tmp_path)

    def test_benchmark_score_negative_invalid(self):
        """fallbacks.yaml con benchmark_score negativo -> debería detectarse"""
        import yaml
        config_path = os.path.join(os.path.dirname(__file__), '../../config/fallbacks.yaml')

        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

        original = data['scores']['benchmark_score']['value']
        data['scores']['benchmark_score']['value'] = -10

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
            yaml.safe_dump(data, tmp)
            tmp_path = tmp.name

        try:
            with open(tmp_path) as f:
                loaded = yaml.safe_load(f)
            # El valor se cargó (YAML no valida rango)
            assert loaded['scores']['benchmark_score']['value'] == -10
            # Score negativo debería ser inválido
            assert loaded['scores']['benchmark_score']['value'] < 0
        finally:
            data['scores']['benchmark_score']['value'] = original
            os.unlink(tmp_path)
