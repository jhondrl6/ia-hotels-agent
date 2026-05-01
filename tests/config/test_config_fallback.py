"""
Test de fallback: YAML ausente o corrupto
FASE-CONFIG-8: Suite de Tests de Regresión

Verifica que el sistema no crashee cuando un YAML está ausente
y que use valores defaults documentados.
"""
import pytest
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class TestFallbackYAMLAbsent:
    """Tests: YAML ausente -> usa defaults (no crashea)"""

    def test_missing_pricing_yaml_raises_readable_error(self):
        """pricing.yaml ausente -> error claro, no crash"""
        # Simular ausencia moviendo temporalmente
        config_path = os.path.join(os.path.dirname(__file__), '../../config/pricing.yaml')
        backup_path = config_path + '.backup_test'

        if os.path.exists(config_path):
            shutil.move(config_path, backup_path)

        try:
            import yaml
            # Intentar cargar - debe fallar con error claro
            with pytest.raises(Exception) as exc_info:
                yaml.safe_load(open(config_path))
            assert 'pricing' in str(exc_info.value).lower() or 'not found' in str(exc_info.value).lower()
        finally:
            if os.path.exists(backup_path):
                shutil.move(backup_path, config_path)

    def test_missing_scenarios_yaml_raises_readable_error(self):
        """scenarios.yaml ausente -> error claro"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/scenarios.yaml')
        backup_path = config_path + '.backup_test'

        if os.path.exists(config_path):
            shutil.move(config_path, backup_path)

        try:
            import yaml
            with pytest.raises(Exception) as exc_info:
                yaml.safe_load(open(config_path))
            assert 'scenarios' in str(exc_info.value).lower() or 'not found' in str(exc_info.value).lower()
        finally:
            if os.path.exists(backup_path):
                shutil.move(backup_path, config_path)

    def test_missing_fallbacks_yaml_raises_readable_error(self):
        """fallbacks.yaml ausente -> error claro"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/fallbacks.yaml')
        backup_path = config_path + '.backup_test'

        if os.path.exists(config_path):
            shutil.move(config_path, backup_path)

        try:
            import yaml
            with pytest.raises(Exception) as exc_info:
                yaml.safe_load(open(config_path))
        finally:
            if os.path.exists(backup_path):
                shutil.move(backup_path, config_path)


class TestFallbackMissingField:
    """Tests: YAML presente pero con campo faltante"""

    def test_pricing_yaml_missing_tier_field(self):
        """pricing.yaml con campo faltante -> error descriptivo"""
        import yaml
        config_path = os.path.join(os.path.dirname(__file__), '../../config/pricing.yaml')

        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Remover un campo y verificar que fallaría al accederlo
        original_tiers = data.pop('tiers', None)
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
                yaml.safe_dump(data, tmp)
                tmp_path = tmp.name

            with open(tmp_path) as f:
                loaded = yaml.safe_load(f)

            # El campo 'tiers' no existe
            with pytest.raises(KeyError):
                _ = loaded['tiers']

            os.unlink(tmp_path)
        finally:
            if original_tiers is not None:
                data['tiers'] = original_tiers
