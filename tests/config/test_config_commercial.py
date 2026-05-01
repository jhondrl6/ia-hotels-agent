"""
Test de migración: commercial.yaml -> v4_proposal_generator.py
FASE-CONFIG-8: Suite de Tests de Regresión

Verifica que los valores de commercial.yaml se lean del YAML,
no de hardcodes en el código.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import yaml


class TestCommercialYAMLValues:
    """Tests: valores leídos de commercial.yaml"""

    def test_commercial_yaml_exists(self):
        """commercial.yaml debe existir en config/"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/commercial.yaml')
        assert os.path.exists(config_path), f"commercial.yaml no encontrado"

    def test_roi_cap(self):
        """roi.cap == 5.0"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/commercial.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['roi']['cap'] == 5.0

    def test_guarantees_satisfaction_days(self):
        """guarantees.satisfaction_days == 90"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/commercial.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['guarantees']['satisfaction_days'] == 90

    def test_guarantees_improvement_percent(self):
        """guarantees.improvement_percent == 10"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/commercial.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['guarantees']['improvement_percent'] == 10

    def test_guarantees_delivery_days(self):
        """guarantees.delivery_days == 15"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/commercial.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['guarantees']['delivery_days'] == 15

    def test_payment_single_discount(self):
        """payment_options.single_payment_discount == 0.9"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/commercial.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['payment_options']['single_payment_discount'] == 0.9

    def test_break_even_months(self):
        """break_even.default_months == 6"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/commercial.yaml')
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['break_even']['default_months'] == 6


class TestCommercialNoHardcodes:
    """Tests: NO debe haber hardcodes de commercial en el código"""

    def test_no_build_guarantees_section_hardcode(self):
        """v4_proposal_generator.py NO contiene 'def _build_guarantees_section' hardcodeado"""
        module_path = os.path.join(os.path.dirname(__file__), '../../modules/commercial_documents/v4_proposal_generator.py')
        with open(module_path, encoding='utf-8') as f:
            content = f.read()
        # Si existe la función, debe usar commercial.yaml, no strings hardcodeados
        assert 'def _build_guarantees_section' not in content, \
            "v4_proposal_generator.py no debe tener _build_guarantees_section hardcodeado"

    def test_no_90_days_literal_hardcode(self):
        """propuesta_v6_template.md NO debe tener '90 días' literal hardcodeado"""
        template_path = os.path.join(os.path.dirname(__file__), '../../templates/comerciales/propuesta_v6_template.md')
        if not os.path.exists(template_path):
            pytest.skip(f"Template no encontrado: {template_path}")
        with open(template_path, encoding='utf-8') as f:
            content = f.read()
        # El template puede mencionar 90 días SI viene de un placeholder
        # Buscar hardcoded static "90 días" que no sea placeholder
        lines = content.split('\n')
        for line in lines:
            if '90 días' in line or '90 dias' in line or '90 d' in line:
                # Aceptable si es placeholder tipo {satisfaction_days}
                if '{satisfaction_days}' not in line and 'garantia' not in line.lower():
                    continue  # Podría ser en contexto no-problemático
                # Si tiene "90 días" estático (sin placeholder), marcar
                import re
                if re.search(r'90\s*d[ií]as(?!.*\{)', line):
                    assert False, f"Template con '90 días' hardcodeado (debe usar placeholder): {line[:80]}"


class TestCommercialIntegration:
    """Tests: módulos deben usar load_yaml_config para commercial"""

    def test_proposal_generator_loads_commercial(self):
        """v4_proposal_generator.py debe cargar commercial.yaml"""
        module_path = os.path.join(os.path.dirname(__file__), '../../modules/commercial_documents/v4_proposal_generator.py')
        with open(module_path, encoding='utf-8') as f:
            content = f.read()
        assert 'load_yaml_config' in content or 'commercial.yaml' in content or 'get_commercial' in content, \
            "v4_proposal_generator.py debe usar load_yaml_config('commercial')"
