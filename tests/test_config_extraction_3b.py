"""
Tests for FASE-CONFIG-3B: YAML config extraction for financial scenarios.

Verifies:
- scenarios.yaml → modules load correct values
- financial_defaults.yaml → DEFAULTS from YAML
- YAML missing → fallback to documented defaults
- YAML corrupt → graceful error
- Custom values in YAML override defaults
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch

from modules.common.yaml_loader import load_yaml_config, YAMLLoadError, clear_cache


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(autouse=True)
def _clear_caches():
    """Clear all YAML caches between tests."""
    clear_cache()
    from modules.common.fallback_loader import clear_cache as clear_fallback_cache
    clear_fallback_cache()
    yield
    clear_cache()
    clear_fallback_cache()


@pytest.fixture
def valid_scenarios_yaml():
    """Standard scenarios.yaml content."""
    return {
        'version': '1.0.0',
        'recovery_factors': {'conservative': 0.15, 'realistic': 0.20, 'optimistic': 0.25},
        'scenario_weights': {'conservative': 0.70, 'realistic': 0.20, 'optimistic': 0.10},
        'degradation_rate': 0.02,
        'ota_shift': {'minimal': 0.05, 'moderate': 0.10, 'optimistic': 0.20},
        'ia_boost': 0.05,
        'pain_ratio_default': 0.20,
    }


@pytest.fixture
def valid_financial_defaults_yaml():
    """Standard financial_defaults.yaml content."""
    return {
        'version': '1.0.0',
        'superposition_factor': 0.7,
        'factor_captura_aila': 0.70,
        'comision_ota': {'min': 0.18, 'base': 0.20, 'max': 0.22},
        'penalizacion_invisibilidad_ia': 0.05,
        'exclusion_rating_bajo': 0.40,
        'factor_perdida_base': 0.09,
        'factor_perdida_min': 0.077,
        'factor_perdida_max': 0.103,
        'revpar_cop': 197120,
        'reservas_ota_proporcion': 0.65,
        'reservas_directo_proporcion': 0.35,
        'uso_ia_proporcion_min': 0.10,
        'uso_ia_proporcion_max': 0.20,
    }


@pytest.fixture
def temp_yaml_dir(valid_scenarios_yaml, valid_financial_defaults_yaml, monkeypatch):
    """Create temporary YAML config files and redirect config/ reads."""

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Write scenarios.yaml
        with open(tmp / 'scenarios.yaml', 'w') as f:
            yaml.dump(valid_scenarios_yaml, f)

        # Write financial_defaults.yaml
        with open(tmp / 'financial_defaults.yaml', 'w') as f:
            yaml.dump(valid_financial_defaults_yaml, f)

        # Monkeypatch yaml_loader config_dir
        original_resolve = Path('config').resolve

        def _mock_resolve():
            return tmp.resolve()

        monkeypatch.setattr('modules.common.yaml_loader.Path', type('MockPath', (), {
            '__new__': lambda cls, *a: Path(tmp / Path(*a).name),
            'resolve': lambda self: self,
        }))

        yield tmp


# ============================================================
# yaml_loader tests
# ============================================================

class TestYAMLLoader:
    """Test the shared yaml_loader module."""

    def test_load_valid_scenarios_yaml(self, _clear_caches, tmp_path):
        """scenarios.yaml presente → carga correcta."""
        config_dir = tmp_path / 'config'
        config_dir.mkdir()
        real_config = Path('config')
        if real_config.exists():
            import shutil
            shutil.copy(real_config / 'scenarios.yaml', config_dir / 'scenarios.yaml')
        else:
            # Fallback: write from scratch
            import yaml
            with open(config_dir / 'scenarios.yaml', 'w') as f:
                yaml.dump({
                    'recovery_factors': {'conservative': 0.15, 'realistic': 0.20, 'optimistic': 0.25},
                    'degradation_rate': 0.02,
                    'ia_boost': 0.05,
                }, f)
        
        from modules.common.yaml_loader import load_yaml_config
        config = load_yaml_config('scenarios', config_dir=config_dir)
        assert config['recovery_factors']['conservative'] == 0.15
        assert config['ia_boost'] == 0.05

    def test_load_valid_financial_defaults_yaml(self, _clear_caches, tmp_path):
        """financial_defaults.yaml presente → carga correcta."""
        config_dir = tmp_path / 'config'
        config_dir.mkdir()
        real_config = Path('config')
        if real_config.exists():
            import shutil
            shutil.copy(real_config / 'financial_defaults.yaml', config_dir / 'financial_defaults.yaml')
        else:
            import yaml
            with open(config_dir / 'financial_defaults.yaml', 'w') as f:
                yaml.dump({
                    'superposition_factor': 0.7,
                    'comision_ota': {'base': 0.20},
                    'revpar_cop': 197120,
                }, f)
        
        from modules.common.yaml_loader import load_yaml_config
        config = load_yaml_config('financial_defaults', config_dir=config_dir)
        assert config['superposition_factor'] == 0.7
        assert config['revpar_cop'] == 197120

    def test_yaml_missing_raises_error(self, _clear_caches):
        """YAML ausente → YAMLLoadError."""
        with patch('modules.common.yaml_loader.Path.exists', return_value=False):
            with pytest.raises(YAMLLoadError, match="not found"):
                load_yaml_config('nonexistent')

    def test_yaml_corrupt_raises_error(self, _clear_caches, tmp_path):
        """YAML corrupto → YAMLLoadError (via yaml parser or dict check)."""
        bad_file = tmp_path / 'corrupt.yaml'
        bad_file.write_text("not: valid: yaml: [unclosed")

        with pytest.raises((YAMLLoadError, yaml.YAMLError)):
            load_yaml_config('corrupt', config_dir=tmp_path)


# ============================================================
# scenario_calculator tests
# ============================================================

class TestScenarioCalculatorYAML:
    """Verify ScenarioCalculator uses YAML values."""

    def test_loads_ota_shifts_from_yaml(self, temp_yaml_dir):
        """scenario_calculator usa ota_shift de YAML."""
        from modules.financial_engine.scenario_calculator import ScenarioCalculator

        calc = ScenarioCalculator()
        config = calc._load_scenario_config()

        assert config['ota_shift']['minimal'] == 0.05
        assert config['ota_shift']['moderate'] == 0.10
        assert config['ota_shift']['optimistic'] == 0.20

    def test_ia_boost_from_yaml(self, temp_yaml_dir):
        """scenario_calculator usa ia_boost de YAML."""
        from modules.financial_engine.scenario_calculator import ScenarioCalculator

        calc = ScenarioCalculator()
        config = calc._load_scenario_config()

        assert config['ia_boost'] == 0.05

    def test_fallback_when_yaml_missing(self, _clear_caches):
        """YAML ausente → fallback a defaults documentados."""
        from modules.financial_engine.scenario_calculator import ScenarioCalculator

        with patch('modules.financial_engine.scenario_calculator.load_yaml_config',
                   side_effect=YAMLLoadError("not found")):
            calc = ScenarioCalculator()
            config = calc._load_scenario_config()
            assert config['ota_shift']['minimal'] == 0.05  # fallback
            assert config['ia_boost'] == 0.05  # fallback

    def test_custom_ota_shift_in_yaml(self, _clear_caches, tmp_path):
        """Valores personalizados en YAML → sobreescriben defaults."""
        custom_yaml = tmp_path / 'scenarios.yaml'
        data = {
            'ota_shift': {'minimal': 0.08, 'moderate': 0.15, 'optimistic': 0.30},
            'ia_boost': 0.07,
        }
        with open(custom_yaml, 'w') as f:
            yaml.dump(data, f)

        from modules.financial_engine.scenario_calculator import ScenarioCalculator
        from modules.common.yaml_loader import load_yaml_config

        with patch('modules.financial_engine.scenario_calculator.load_yaml_config',
                   return_value=data):
            calc = ScenarioCalculator()
            config = calc._load_scenario_config()
            assert config['ota_shift']['minimal'] == 0.08
            assert config['ota_shift']['moderate'] == 0.15
            assert config['ia_boost'] == 0.07


# ============================================================
# loss_projector tests
# ============================================================

class TestLossProjectorYAML:
    """Verify LossProjector uses YAML degradation_rate."""

    def test_degradation_rate_from_yaml(self):
        """loss_projector carga degradation_rate de YAML."""
        with patch('modules.financial_engine.loss_projector.load_yaml_config',
                   return_value={'degradation_rate': 0.03}):
            from modules.financial_engine.loss_projector import LossProjector
            lp = LossProjector("Test Hotel")
            assert lp._degradation_rate == 0.03

    def test_degradation_rate_fallback(self):
        """YAML ausente → degradation_rate fallback 0.02."""
        with patch('modules.financial_engine.loss_projector.load_yaml_config',
                   side_effect=YAMLLoadError("not found")):
            from modules.financial_engine.loss_projector import LossProjector
            lp = LossProjector("Test Hotel")
            assert lp._degradation_rate == 0.02


# ============================================================
# financial_factors tests
# ============================================================

class TestFinancialFactorsYAML:
    """Verify FinancialFactors uses YAML defaults."""

    def test_defaults_from_yaml(self):
        """financial_factors carga DEFAULTS de YAML."""
        from modules.utils.financial_factors import FinancialFactors

        yaml_data = {
            'factor_captura_aila': 0.75,
            'comision_ota': {'min': 0.15, 'base': 0.18, 'max': 0.25},
            'penalizacion_invisibilidad_ia': 0.06,
            'revpar_cop': 200000,
        }
        with patch('modules.utils.financial_factors.load_yaml_config', return_value=yaml_data):
            defaults = FinancialFactors._load_defaults()
            assert defaults['factor_captura_aila'] == 0.75
            assert defaults['comision_ota_base'] == 0.18  # flattened
            assert defaults['comision_ota_min'] == 0.15
            assert defaults['comision_ota_max'] == 0.25
            assert defaults['revpar_cop'] == 200000

    def test_defaults_fallback(self):
        """YAML ausente → DEFAULTS fallback."""
        from modules.utils.financial_factors import FinancialFactors

        with patch('modules.utils.financial_factors.load_yaml_config',
                   side_effect=YAMLLoadError("not found")):
            defaults = FinancialFactors._load_defaults()
            assert defaults['factor_captura_aila'] == 0.70
            assert defaults['comision_ota_base'] == 0.20
            assert defaults['revpar_cop'] == 197120

    def test_superposition_factor_from_yaml(self):
        """SUPERPOSITION_FACTOR carga de YAML."""
        from modules.utils.financial_factors import FinancialFactors

        with patch('modules.utils.financial_factors.load_yaml_config',
                   return_value={'superposition_factor': 0.85}):
            assert FinancialFactors.get_superposition_factor() == 0.85

    def test_superposition_factor_fallback(self):
        """YAML ausente → SUPERPOSITION_FACTOR fallback 0.7."""
        from modules.utils.financial_factors import FinancialFactors

        with patch('modules.utils.financial_factors.load_yaml_config',
                   side_effect=YAMLLoadError("not found")):
            assert FinancialFactors.get_superposition_factor() == 0.7


# ============================================================
# v4_proposal_generator tests
# ============================================================

class TestV4ProposalGeneratorYAML:
    """Verify V4ProposalGenerator uses YAML recovery_factors, weights, pain_ratio."""

    def test_recovery_factors_from_yaml(self):
        """v4_proposal_generator usa recovery_factors de YAML."""
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator

        yaml_data = {
            'recovery_factors': {'conservative': 0.10, 'realistic': 0.15, 'optimistic': 0.30},
            'scenario_weights': {'conservative': 0.70, 'realistic': 0.20, 'optimistic': 0.10},
            'pain_ratio_default': 0.25,
        }
        with patch('modules.commercial_documents.v4_proposal_generator.load_yaml_config',
                   return_value=yaml_data):
            gen = V4ProposalGenerator()
            config = gen._load_scenario_config()
            assert config['recovery_factors']['conservative'] == 0.10
            assert config['recovery_factors']['realistic'] == 0.15
            assert config['recovery_factors']['optimistic'] == 0.30
            assert config['pain_ratio_default'] == 0.25

    def test_scenario_weights_from_yaml(self):
        """v4_proposal_generator usa scenario_weights de YAML."""
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator

        yaml_data = {
            'recovery_factors': {'conservative': 0.15, 'realistic': 0.20, 'optimistic': 0.25},
            'scenario_weights': {'conservative': 0.50, 'realistic': 0.30, 'optimistic': 0.20},
            'pain_ratio_default': 0.20,
        }
        with patch('modules.commercial_documents.v4_proposal_generator.load_yaml_config',
                   return_value=yaml_data):
            gen = V4ProposalGenerator()
            config = gen._load_scenario_config()
            assert config['scenario_weights']['conservative'] == 0.50
            assert config['scenario_weights']['realistic'] == 0.30
            assert config['scenario_weights']['optimistic'] == 0.20

    def test_fallback_when_yaml_missing(self):
        """YAML ausente → fallback a hardcoded defaults."""
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator

        with patch('modules.commercial_documents.v4_proposal_generator.load_yaml_config',
                   side_effect=YAMLLoadError("not found")):
            gen = V4ProposalGenerator()
            config = gen._load_scenario_config()
            assert config['recovery_factors']['conservative'] == 0.15
            assert config['scenario_weights']['realistic'] == 0.20
            assert config['pain_ratio_default'] == 0.20

    def test_custom_recovery_factors_override(self):
        """Valores YAML personalizados → sobreescriben defaults."""
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator

        yaml_data = {
            'recovery_factors': {'conservative': 0.05, 'realistic': 0.12, 'optimistic': 0.18},
            'scenario_weights': {'conservative': 0.60, 'realistic': 0.25, 'optimistic': 0.15},
            'pain_ratio_default': 0.30,
        }
        with patch('modules.commercial_documents.v4_proposal_generator.load_yaml_config',
                   return_value=yaml_data):
            gen = V4ProposalGenerator()
            config = gen._load_scenario_config()
            assert config['recovery_factors']['optimistic'] == 0.18
            assert config['pain_ratio_default'] == 0.30
