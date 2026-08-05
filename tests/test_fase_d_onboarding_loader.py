"""Tests FASE-D (S7): Fallback del loader de onboarding.

Verifica que _load_latest_onboarding_data:
1. Encuentra YAML en output_dir especificado
2. Retorna None si el directorio no existe
3. Funciona con el default output/clientes
"""

import pytest
import tempfile
from pathlib import Path

# _load_latest_onboarding_data y _normalize_url están en main.py
from main import _load_latest_onboarding_data, _normalize_url


class TestOnboardingLoaderFallback:
    """S7: loader encuentra YAML aunque --output sea alternativo."""

    @pytest.fixture
    def sample_onboarding_yaml(self, tmp_path):
        """Crea un YAML de onboarding de ejemplo."""
        clientes_dir = tmp_path / "clientes"
        clientes_dir.mkdir()
        yaml_content = (
            "hotel:\n"
            "  url: https://hotel-test.example.com/\n"
            "  nombre: Hotel Test\n"
            "metadatos:\n"
            "  campos_confirmados:\n"
            "    - habitaciones\n"
            "    - tarifa_promedio\n"
            "    - ocupacion\n"
            "  fecha_captura: '2026-08-05T10:00:00'\n"
            "datos_operativos:\n"
            "  habitaciones: 20\n"
            "  valor_reserva_cop: 250000\n"
        )
        yaml_file = clientes_dir / "hotel-test_onboarding.yaml"
        yaml_file.write_text(yaml_content, encoding="utf-8")
        return clientes_dir

    def test_loader_finds_yaml_in_custom_dir(self, sample_onboarding_yaml):
        """Loader encuentra YAML en directorio custom."""
        result = _load_latest_onboarding_data(
            hotel_url="https://hotel-test.example.com/",
            hotel_name="Hotel Test",
            output_dir=sample_onboarding_yaml,
        )
        assert result is not None, "Should find onboarding data"
        assert result["hotel"]["url"] == "https://hotel-test.example.com/"
        assert result["datos_operativos"]["habitaciones"] == 20

    def test_loader_returns_none_for_nonexistent_dir(self, tmp_path):
        """Loader retorna None si directorio no existe."""
        result = _load_latest_onboarding_data(
            hotel_url="https://hotel-test.example.com/",
            hotel_name="Hotel Test",
            output_dir=tmp_path / "nonexistent",
        )
        assert result is None

    def test_loader_returns_none_for_empty_dir(self, tmp_path):
        """Loader retorna None si directorio existe pero no tiene YAMLs."""
        empty_dir = tmp_path / "empty_clientes"
        empty_dir.mkdir()
        result = _load_latest_onboarding_data(
            hotel_url="https://hotel-test.example.com/",
            hotel_name="Hotel Test",
            output_dir=empty_dir,
        )
        assert result is None

    def test_loader_matches_by_normalized_url(self, sample_onboarding_yaml):
        """Loader matchea por URL normalizada (con/sin trailing slash)."""
        result = _load_latest_onboarding_data(
            hotel_url="https://hotel-test.example.com",  # sin trailing slash
            hotel_name="Hotel Test",
            output_dir=sample_onboarding_yaml,
        )
        assert result is not None, "Should match regardless of trailing slash"

    def test_loader_returns_none_for_wrong_url(self, sample_onboarding_yaml):
        """Loader retorna None si URL no coincide."""
        result = _load_latest_onboarding_data(
            hotel_url="https://otro-hotel.example.com/",
            hotel_name="Otro Hotel",
            output_dir=sample_onboarding_yaml,
        )
        assert result is None

    def test_normalize_url_strips_protocol_and_www(self):
        """_normalize_url elimina protocolo y www."""
        assert _normalize_url("https://www.hotel.com/") == "hotel.com"
        assert _normalize_url("http://hotel.com") == "hotel.com"
        assert _normalize_url("https://hotel.com/") == "hotel.com"

    def test_fallback_pattern_in_main_flow(self, tmp_path):
        """Verifica el patrón de fallback: si custom dir falla → default dir."""
        # Setup: crear YAML solo en output/clientes (default), no en custom
        default_dir = tmp_path / "default_output" / "clientes"
        default_dir.mkdir(parents=True)
        yaml_content = (
            "hotel:\n"
            "  url: https://fallback-test.example.com/\n"
            "metadatos:\n"
            "  campos_confirmados: [hab]\n"
        )
        (default_dir / "fallback_onboarding.yaml").write_text(
            yaml_content, encoding="utf-8"
        )

        # Custom dir sin YAML
        custom_dir = tmp_path / "custom_output" / "clientes"
        custom_dir.mkdir(parents=True)

        # Paso 1: intentar con custom → None
        result = _load_latest_onboarding_data(
            hotel_url="https://fallback-test.example.com/",
            hotel_name="Fallback Hotel",
            output_dir=custom_dir,
        )
        assert result is None, "Custom dir has no YAML"

        # Paso 2: fallback a default → encuentra
        result = _load_latest_onboarding_data(
            hotel_url="https://fallback-test.example.com/",
            hotel_name="Fallback Hotel",
            output_dir=default_dir,
        )
        assert result is not None, "Default dir has the YAML"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
