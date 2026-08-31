"""
Test de migración: scenarios.yaml -> scenario_calculator.py
FASE-CONFIG-8: Suite de Tests de Regresión

Verifica que los valores de scenarios.yaml se lean del YAML,
no de hardcodes en el código.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import yaml


class TestScenariosYAMLValues:
    """Tests: valores leídos de scenarios.yaml"""

    def test_scenarios_yaml_exists(self):
        """scenarios.yaml debe existir en config/"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/scenarios.yaml')
        assert os.path.exists(config_path), f"scenarios.yaml no encontrado"

    def test_recovery_factors_conservative(self):
        """recovery_factors.conservative == 0.15"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/scenarios.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['recovery_factors']['conservative'] == 0.15

    def test_recovery_factors_realistic(self):
        """recovery_factors.realistic == 0.35 (ROICRII FASE-3: pipeline unificado)"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/scenarios.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['recovery_factors']['realistic'] == 0.35

    def test_ota_shift_minimal(self):
        """ota_shift.minimal == 0.05"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/scenarios.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['ota_shift']['minimal'] == 0.05

    def test_ota_shift_moderate(self):
        """ota_shift.moderate == 0.1"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/scenarios.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['ota_shift']['moderate'] == 0.1

    def test_ota_shift_optimistic(self):
        """ota_shift.optimistic == 0.2"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/scenarios.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['ota_shift']['optimistic'] == 0.2

    def test_scenario_weights(self):
        """scenario_weights: conservative=0.7, realistic=0.2, optimistic=0.1"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/scenarios.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['scenario_weights']['conservative'] == 0.7
        assert data['scenario_weights']['realistic'] == 0.2
        assert data['scenario_weights']['optimistic'] == 0.1

    def test_degradation_rate(self):
        """degradation_rate == 0.02"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/scenarios.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['degradation_rate'] == 0.02


class TestScenariosNoHardcodes:
    """Tests: NO debe haber hardcodes de scenarios en el código"""

    def test_no_minimal_improvement_hardcode(self):
        """scenario_calculator.py NO contiene 'minimal_improvement = 0.05' hardcodeado"""
        import re
        module_path = os.path.join(os.path.dirname(__file__), '../../modules/financial_engine/scenario_calculator.py')
        with open(module_path, encoding='utf-8') as f:
            content = f.read()

        # Buscar asignaciones literales como: minimal_improvement = 0.05
        # NO flaggear: ota_bookings * minimal_improvement (uso de variable)
        pattern = re.compile(r'\bminimal_improvement\s*=\s*0\.0[0-9]+\b')
        for line_num, line in enumerate(content.split('\n'), 1):
            if pattern.search(line) and 'scenario_config' not in line:
                if not line.strip().startswith('#'):
                    assert False, f"L{line_num}: Hardcode sospechoso: {line.strip()}"

    def test_no_moderate_shift_hardcode(self):
        """scenario_calculator.py NO contiene 'moderate_shift = 0.10' hardcodeado"""
        module_path = os.path.join(os.path.dirname(__file__), '../../modules/financial_engine/scenario_calculator.py')
        with open(module_path, encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            # Detectar asignación directa del literal: moderate_shift = 0.10
            if 'moderate_shift' in line and '= 0.10' in line and 'scenario_config' not in line:
                if not stripped.startswith('#'):
                    assert False, f"L{line_num}: Hardcode sospechoso: {stripped}"

    def test_no_conservative_hardcode(self):
        """scenario_calculator.py NO contiene 'conservative = 0.15' hardcodeado"""
        module_path = os.path.join(os.path.dirname(__file__), '../../modules/financial_engine/scenario_calculator.py')
        with open(module_path, encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            # Detectar asignación directa del literal: conservative = 0.15
            if 'conservative' in line and '= 0.15' in line and 'scenario_config' not in line:
                if not stripped.startswith('#'):
                    assert False, f"L{line_num}: Hardcode sospechoso: {stripped}"


class TestScenarioCalculatorUsesYAML:
    """Tests: scenario_calculator.py debe usar load_yaml_config"""

    def test_scenario_calculator_loads_yaml(self):
        """scenario_calculator.py debe cargar scenarios.yaml"""
        module_path = os.path.join(os.path.dirname(__file__), '../../modules/financial_engine/scenario_calculator.py')
        with open(module_path, encoding='utf-8') as f:
            content = f.read()
        assert 'load_yaml_config' in content or 'scenarios.yaml' in content, \
            "scenario_calculator.py debe usar load_yaml_config('scenarios')"
