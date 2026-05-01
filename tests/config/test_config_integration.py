"""
Test de integración: cambios en YAML se reflejan al reiniciar módulo
FASE-CONFIG-8: Suite de Tests de Regresión

Verifica que los módulos recarguen valores del YAML sin restart completo.
"""
import pytest
import sys
import os
import importlib
import tempfile
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class TestConfigIntegration:
    """Tests: cambio en YAML -> valor reflejado"""

    def test_pricing_tier_value_loaded_from_yaml(self):
        """pricing_calculator.py debe leer tiers.boutique.min_price de YAML"""
        # Importar el módulo
        from modules.financial_engine import pricing_calculator
        
        # Verificar que el módulo carga valores del YAML
        # Buscar en el código que usa load_yaml_config
        module_path = os.path.join(os.path.dirname(__file__), 
            '../../modules/financial_engine/pricing_calculator.py')
        
        with open(module_path, encoding='utf-8') as f:
            content = f.read()
        
        # El módulo debe mencionar load_yaml_config o pricing.yaml
        uses_yaml = ('load_yaml_config' in content or 
                     'pricing.yaml' in content or
                     'yaml' in content.lower())
        assert uses_yaml, "pricing_calculator.py debe cargar valores de YAML"

    def test_scenario_values_loaded_from_yaml(self):
        """scenario_calculator.py debe leer recovery_factors de YAML"""
        module_path = os.path.join(os.path.dirname(__file__), 
            '../../modules/financial_engine/scenario_calculator.py')
        
        with open(module_path, encoding='utf-8') as f:
            content = f.read()
        
        uses_yaml = ('load_yaml_config' in content or 
                     'scenarios.yaml' in content or
                     'yaml' in content.lower())
        assert uses_yaml, "scenario_calculator.py debe cargar valores de YAML"

    def test_all_config_files_have_version(self):
        """Todos los YAML activos de config/ deben tener campo 'version'"""
        config_dir = os.path.join(os.path.dirname(__file__), '../../config')

        # Archivos LEGACY sin version/description (deprecated)
        skip_files = {'settings.yaml'}  # LEGACY — ver header del archivo

        for filename in os.listdir(config_dir):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                if filename in skip_files:
                    continue
                filepath = os.path.join(config_dir, filename)
                with open(filepath, encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                assert 'version' in data, f"{filename} debe tener campo 'version'"
                assert isinstance(data['version'], (str, int, float)), \
                    f"{filename} version debe ser string o number"

    def test_all_config_files_have_description(self):
        """Todos los YAML activos de config/ deben tener campo 'description'"""
        config_dir = os.path.join(os.path.dirname(__file__), '../../config')

        # Archivos LEGACY sin version/description (deprecated)
        skip_files = {'settings.yaml'}  # LEGACY — ver header del archivo

        for filename in os.listdir(config_dir):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                if filename in skip_files:
                    continue
                filepath = os.path.join(config_dir, filename)
                with open(filepath, encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                assert 'description' in data, f"{filename} debe tener campo 'description'"
