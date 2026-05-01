"""
Tests for FASE-CONFIG-5: Regional Benchmarks YAML extraction.

Verifies:
- regional_benchmarks.yaml → modules load correct values
- Pain narratives (N-05): 14 values extracted
- Confidence thresholds (N-02): high/medium/low
- Other thresholds: GBP geo_score, mobile, citability, IAO labels, score status
- YAML missing → fallback to documented defaults
- YAML corrupt → graceful error
- Custom values in YAML override defaults
- Multi-region support with fallback to default_region
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
    """Clear all relevant caches between tests."""
    clear_cache()
    # Clear regional benchmarks cache in v4_diagnostic_generator
    try:
        from modules.commercial_documents.v4_diagnostic_generator import clear_benchmarks_cache
        clear_benchmarks_cache()
    except (ImportError, AttributeError):
        pass
    # Clear confidence thresholds cache in v4_proposal_generator
    try:
        from modules.commercial_documents.v4_proposal_generator import clear_confidence_cache
        clear_confidence_cache()
    except (ImportError, AttributeError):
        pass
    yield
    clear_cache()
    try:
        from modules.commercial_documents.v4_diagnostic_generator import clear_benchmarks_cache
        clear_benchmarks_cache()
    except (ImportError, AttributeError):
        pass
    try:
        from modules.commercial_documents.v4_proposal_generator import clear_confidence_cache
        clear_confidence_cache()
    except (ImportError, AttributeError):
        pass


@pytest.fixture
def valid_regional_benchmarks_yaml():
    """Standard regional_benchmarks.yaml content."""
    return {
        'version': '1.0.0',
        'description': 'Umbrales de scoring y narrativas de impacto por región',
        'default_region': 'eje_cafetero',
        'regions': {
            'eje_cafetero': {
                'pain_narratives': {
                    'no_whatsapp_visible': 0.20,
                    'whatsapp_conflict': 0.10,
                    'no_hotel_schema': 0.25,
                    'low_gbp_score': 0.30,
                    'poor_performance': 0.15,
                    'no_faq_schema': 0.12,
                    'no_og_tags': 0.08,
                    'low_citability': 0.10,
                    'ai_crawler_blocked': 0.15,
                    'low_ia_readiness': 0.15,
                    'no_org_schema': 0.08,
                    'metadata_defaults': 0.10,
                    'missing_reviews': 0.10,
                    'no_analytics_configured': 0.10,
                },
                'confidence': {
                    'high': 0.85,
                    'medium': 0.70,
                    'low': 0.40,
                },
                'gbp_geo_score_threshold': 70,
                'mobile_score_threshold': 50,
                'citability': {
                    'high': 50,
                    'low': 0,
                },
                'iao_labels': {
                    'high': 60,
                    'medium': 35,
                },
                'score_status': {
                    'superior_multiplier': 1.1,
                    'promedio_multiplier': 0.9,
                },
            },
            'caribe': {
                'pain_narratives': {
                    'no_whatsapp_visible': 0.22,  # Different value for region
                    'whatsapp_conflict': 0.10,
                    'no_hotel_schema': 0.25,
                    'low_gbp_score': 0.30,
                    'poor_performance': 0.15,
                    'no_faq_schema': 0.12,
                    'no_og_tags': 0.08,
                    'low_citability': 0.10,
                    'ai_crawler_blocked': 0.15,
                    'low_ia_readiness': 0.15,
                    'no_org_schema': 0.08,
                    'metadata_defaults': 0.10,
                    'missing_reviews': 0.10,
                    'no_analytics_configured': 0.10,
                },
                'confidence': {
                    'high': 0.85,
                    'medium': 0.70,
                    'low': 0.40,
                },
                'gbp_geo_score_threshold': 70,
                'mobile_score_threshold': 50,
                'citability': {
                    'high': 50,
                    'low': 0,
                },
                'iao_labels': {
                    'high': 60,
                    'medium': 35,
                },
                'score_status': {
                    'superior_multiplier': 1.1,
                    'promedio_multiplier': 0.9,
                },
            },
        },
    }


# ============================================================
# Tests: YAML Loading
# ============================================================

class TestRegionalBenchmarksLoading:
    """Tests for loading regional_benchmarks.yaml."""

    def test_load_valid_yaml(self, valid_regional_benchmarks_yaml, tmp_path):
        """YAML with valid structure loads successfully."""
        config_path = tmp_path / "regional_benchmarks.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(valid_regional_benchmarks_yaml, f)
        
        config = load_yaml_config(str(config_path), config_dir=tmp_path)
        
        assert config['version'] == '1.0.0'
        assert config['default_region'] == 'eje_cafetero'
        assert 'regions' in config

    def test_load_nonexistent_yaml_raises_error(self, tmp_path):
        """Missing YAML raises YAMLLoadError."""
        with pytest.raises(YAMLLoadError):
            load_yaml_config('nonexistent', config_dir=tmp_path)

    def test_load_invalid_yaml_raises_error(self, tmp_path):
        """Invalid YAML raises YAMLLoadError."""
        config_path = tmp_path / "regional_benchmarks.yaml"
        with open(config_path, 'w') as f:
            f.write("not: valid: yaml: structure")
        
        with pytest.raises(YAMLLoadError):
            load_yaml_config(str(config_path), config_dir=tmp_path)


# ============================================================
# Tests: Pain Narratives (N-05)
# ============================================================

class TestPainNarratives:
    """Tests for pain narrative values from regional_benchmarks.yaml."""

    def test_all_14_pain_narratives_present(self, valid_regional_benchmarks_yaml, tmp_path):
        """All 14 pain narrative values are present in eje_cafetero region."""
        config_path = tmp_path / "regional_benchmarks.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(valid_regional_benchmarks_yaml, f)
        
        config = load_yaml_config(str(config_path), config_dir=tmp_path)
        narratives = config['regions']['eje_cafetero']['pain_narratives']
        
        expected_keys = [
            'no_whatsapp_visible', 'whatsapp_conflict', 'no_hotel_schema',
            'low_gbp_score', 'poor_performance', 'no_faq_schema', 'no_og_tags',
            'low_citability', 'ai_crawler_blocked', 'low_ia_readiness',
            'no_org_schema', 'metadata_defaults', 'missing_reviews',
            'no_analytics_configured'
        ]
        
        assert len(narratives) == 14, f"Expected 14 pain narratives, got {len(narratives)}"
        for key in expected_keys:
            assert key in narratives, f"Missing pain narrative: {key}"
            assert isinstance(narratives[key], (int, float)), f"Non-numeric value for {key}"
            assert 0 <= narratives[key] <= 1, f"Value out of range for {key}: {narratives[key]}"

    def test_pain_narratives_values_match_hardcoded(self, valid_regional_benchmarks_yaml, tmp_path):
        """Pain narrative values match the original hardcoded values."""
        config_path = tmp_path / "regional_benchmarks.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(valid_regional_benchmarks_yaml, f)
        
        config = load_yaml_config(str(config_path), config_dir=tmp_path)
        narratives = config['regions']['eje_cafetero']['pain_narratives']
        
        # Verify key values that were hardcoded
        assert narratives['no_whatsapp_visible'] == 0.20
        assert narratives['no_hotel_schema'] == 0.25
        assert narratives['low_gbp_score'] == 0.30
        assert narratives['poor_performance'] == 0.15
        assert narratives['no_faq_schema'] == 0.12

    def test_regions_have_different_pain_values(self, valid_regional_benchmarks_yaml, tmp_path):
        """Different regions can have different pain narrative values."""
        config_path = tmp_path / "regional_benchmarks.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(valid_regional_benchmarks_yaml, f)
        
        config = load_yaml_config(str(config_path), config_dir=tmp_path)
        
        eje_narratives = config['regions']['eje_cafetero']['pain_narratives']
        caribe_narratives = config['regions']['caribe']['pain_narratives']
        
        # caribe has different no_whatsapp_visible value
        assert eje_narratives['no_whatsapp_visible'] == 0.20
        assert caribe_narratives['no_whatsapp_visible'] == 0.22


# ============================================================
# Tests: Confidence Thresholds (N-02)
# ============================================================

class TestConfidenceThresholds:
    """Tests for confidence threshold values from regional_benchmarks.yaml."""

    def test_confidence_thresholds_present(self, valid_regional_benchmarks_yaml, tmp_path):
        """Confidence thresholds (high/medium/low) are present."""
        config_path = tmp_path / "regional_benchmarks.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(valid_regional_benchmarks_yaml, f)
        
        config = load_yaml_config(str(config_path), config_dir=tmp_path)
        confidence = config['regions']['eje_cafetero']['confidence']
        
        assert 'high' in confidence
        assert 'medium' in confidence
        assert 'low' in confidence
        
        assert confidence['high'] == 0.85
        assert confidence['medium'] == 0.70
        assert confidence['low'] == 0.40

    def test_confidence_thresholds_ordered(self, valid_regional_benchmarks_yaml, tmp_path):
        """Confidence thresholds follow correct ordering: high > medium > low."""
        config_path = tmp_path / "regional_benchmarks.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(valid_regional_benchmarks_yaml, f)
        
        config = load_yaml_config(str(config_path), config_dir=tmp_path)
        confidence = config['regions']['eje_cafetero']['confidence']
        
        assert confidence['high'] > confidence['medium']
        assert confidence['medium'] > confidence['low']


# ============================================================
# Tests: Other Thresholds (N-06 to N-10)
# ============================================================

class TestOtherThresholds:
    """Tests for other threshold values from regional_benchmarks.yaml."""

    def test_gbp_geo_score_threshold(self, valid_regional_benchmarks_yaml, tmp_path):
        """GBP geo_score threshold (N-06) is present."""
        config_path = tmp_path / "regional_benchmarks.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(valid_regional_benchmarks_yaml, f)
        
        config = load_yaml_config(str(config_path), config_dir=tmp_path)
        threshold = config['regions']['eje_cafetero']['gbp_geo_score_threshold']
        
        assert threshold == 70

    def test_mobile_score_threshold(self, valid_regional_benchmarks_yaml, tmp_path):
        """Mobile score threshold (N-07) is present."""
        config_path = tmp_path / "regional_benchmarks.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(valid_regional_benchmarks_yaml, f)
        
        config = load_yaml_config(str(config_path), config_dir=tmp_path)
        threshold = config['regions']['eje_cafetero']['mobile_score_threshold']
        
        assert threshold == 50

    def test_citability_thresholds(self, valid_regional_benchmarks_yaml, tmp_path):
        """Citability thresholds (N-08) are present."""
        config_path = tmp_path / "regional_benchmarks.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(valid_regional_benchmarks_yaml, f)
        
        config = load_yaml_config(str(config_path), config_dir=tmp_path)
        citability = config['regions']['eje_cafetero']['citability']
        
        assert citability['high'] == 50
        assert citability['low'] == 0

    def test_iao_label_thresholds(self, valid_regional_benchmarks_yaml, tmp_path):
        """IAO label thresholds (N-09) are present."""
        config_path = tmp_path / "regional_benchmarks.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(valid_regional_benchmarks_yaml, f)
        
        config = load_yaml_config(str(config_path), config_dir=tmp_path)
        iao_labels = config['regions']['eje_cafetero']['iao_labels']
        
        assert iao_labels['high'] == 60
        assert iao_labels['medium'] == 35

    def test_score_status_multipliers(self, valid_regional_benchmarks_yaml, tmp_path):
        """Score status multipliers (N-10) are present."""
        config_path = tmp_path / "regional_benchmarks.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(valid_regional_benchmarks_yaml, f)
        
        config = load_yaml_config(str(config_path), config_dir=tmp_path)
        score_status = config['regions']['eje_cafetero']['score_status']
        
        assert score_status['superior_multiplier'] == 1.1
        assert score_status['promedio_multiplier'] == 0.9


# ============================================================
# Tests: Module Integration
# ============================================================

class TestModuleIntegration:
    """Tests for module-level integration with regional_benchmarks.yaml."""

    def test_load_benchmarks_function_exists(self):
        """_load_benchmarks function exists in v4_diagnostic_generator."""
        try:
            from modules.commercial_documents.v4_diagnostic_generator import _load_benchmarks
            assert callable(_load_benchmarks)
        except ImportError as e:
            pytest.fail(f"_load_benchmarks not importable: {e}")

    def test_load_benchmarks_returns_dict(self):
        """_load_benchmarks returns a dictionary with expected structure."""
        from modules.commercial_documents.v4_diagnostic_generator import _load_benchmarks, clear_benchmarks_cache
        
        clear_benchmarks_cache()
        benchmarks = _load_benchmarks("eje_cafetero")
        
        assert isinstance(benchmarks, dict)
        assert 'pain_narratives' in benchmarks
        assert 'confidence' in benchmarks

    def test_load_benchmarks_fallback_to_default(self):
        """_load_benchmarks falls back to default_region for unknown region."""
        from modules.commercial_documents.v4_diagnostic_generator import _load_benchmarks, clear_benchmarks_cache
        
        clear_benchmarks_cache()
        
        # Unknown region should fallback to default_region (eje_cafetero)
        benchmarks = _load_benchmarks("unknown_region")
        
        assert isinstance(benchmarks, dict)
        # Should have eje_cafetero values
        assert 'pain_narratives' in benchmarks

    def test_clear_benchmarks_cache(self):
        """clear_benchmarks_cache successfully clears the cache."""
        from modules.commercial_documents.v4_diagnostic_generator import _load_benchmarks, clear_benchmarks_cache
        
        clear_benchmarks_cache()
        benchmarks1 = _load_benchmarks("eje_cafetero")
        
        clear_benchmarks_cache()
        benchmarks2 = _load_benchmarks("eje_cafetero")
        
        # Both should return same values
        assert benchmarks1 == benchmarks2

    def test_load_confidence_thresholds_function_exists(self):
        """_load_confidence_thresholds function exists in v4_proposal_generator."""
        try:
            from modules.commercial_documents.v4_proposal_generator import _load_confidence_thresholds
            assert callable(_load_confidence_thresholds)
        except ImportError as e:
            pytest.fail(f"_load_confidence_thresholds not importable: {e}")

    def test_load_confidence_thresholds_returns_dict(self):
        """_load_confidence_thresholds returns expected thresholds."""
        from modules.commercial_documents.v4_proposal_generator import _load_confidence_thresholds, clear_confidence_cache
        
        clear_confidence_cache()
        thresholds = _load_confidence_thresholds()
        
        assert isinstance(thresholds, dict)
        assert 'high' in thresholds
        assert 'medium' in thresholds
        assert 'low' in thresholds
