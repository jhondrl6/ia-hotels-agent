"""
Test de migración: pricing.yaml -> pricing_calculator.py
FASE-CONFIG-8: Suite de Tests de Regresión

Verifica que los valores de pricing.yaml se lean del YAML,
no de hardcodes en el código.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import yaml


class TestPricingYAMLValues:
    """Tests: valores leídos de pricing.yaml"""

    def test_pricing_yaml_exists(self):
        """pricing.yaml debe existir en config/"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/pricing.yaml')
        assert os.path.exists(config_path), f"pricing.yaml no encontrado en {config_path}"

    def test_tiers_boutique_min_price(self):
        """tiers.boutique.min_price == 1200000"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/pricing.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['tiers']['boutique']['min_price'] == 1200000

    def test_tiers_standard_min_price(self):
        """tiers.standard.min_price == 1800000"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/pricing.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['tiers']['standard']['min_price'] == 1800000

    def test_tiers_large_min_price(self):
        """tiers.large.min_price == 3500000"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/pricing.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['tiers']['large']['min_price'] == 3500000

    def test_gates_min_ratio(self):
        """gates.min_ratio == 0.03"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/pricing.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['gates']['min_ratio'] == 0.03

    def test_gates_max_ratio(self):
        """gates.max_ratio == 0.06"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/pricing.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['gates']['max_ratio'] == 0.06


class TestPricingNoHardcodes:
    """Tests: NO debe haber hardcodes de pricing en el código"""

    def test_no_tier_config_hardcode(self):
        """pricing_calculator.py NO contiene TIER_CONFIG = { (dict hardcodeado)"""
        module_path = os.path.join(os.path.dirname(__file__), '../../modules/financial_engine/pricing_calculator.py')
        with open(module_path, encoding='utf-8') as f:
            content = f.read()
        # Buscar patrón TIER_CONFIG = { ... } en formato hardcodeado
        assert 'TIER_CONFIG = {' not in content, \
            "pricing_calculator.py contiene 'TIER_CONFIG = {' (hardcodeado)"

    def test_no_gate_min_ratio_hardcode(self):
        """pricing_calculator.py NO contiene GATE_MIN_RATIO = 0.03 hardcodeado"""
        module_path = os.path.join(os.path.dirname(__file__), '../../modules/financial_engine/pricing_calculator.py')
        with open(module_path, encoding='utf-8') as f:
            content = f.read()
        # Buscar línea como GATE_MIN_RATIO = 0.03 (asignación directa, no de config)
        lines = content.split('\n')
        for line in lines:
            stripped = line.strip()
            if 'GATE_MIN_RATIO' in line and '=' in line:
                # Es OK si viene de cfg[...] o self.cfg
                if 'cfg[' not in line and 'self.cfg' not in line and 'self.GATE' not in line:
                    assert False, f"Línea sospechosa de hardcode: {line.strip()}"


class TestPricingCalculatorUsesYAML:
    """Tests: pricing_calculator.py debe usar load_yaml_config o equivalente"""

    def test_pricing_calculator_loads_yaml(self):
        """pricing_calculator.py debe cargar pricing.yaml via load_yaml_config"""
        module_path = os.path.join(os.path.dirname(__file__), '../../modules/financial_engine/pricing_calculator.py')
        with open(module_path, encoding='utf-8') as f:
            content = f.read()
        assert 'load_yaml_config' in content or 'pricing.yaml' in content, \
            "pricing_calculator.py debe usar load_yaml_config('pricing') o similar"
