"""
Tests de regresion para el pipeline de inyeccion onboarding.

FASE-3: ONBOARDING-INJECTION-GAP-2026-07-29

Cubre:
- _normalize_url(): normalizacion canonica de URLs
- _load_latest_onboarding_data(): matching por URL en YAMLs + fallback observations.json
- _observation_to_onboarding_format(): conversion observation → formato onboarding
"""

import sys
from pathlib import Path

# Add project root to path for importing main.py functions
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import yaml

from main import _normalize_url, _observation_to_onboarding_format, _load_latest_onboarding_data


# ============================================================================
# T1: Tests para _normalize_url() — ≥10 casos
# ============================================================================

class TestNormalizeUrl:
    """Tests para _normalize_url() — normalizacion canonica de URLs."""

    @pytest.mark.parametrize("input_url,expected", [
        # Caso base
        ("https://zione.co/", "zione.co"),
        # www removido
        ("https://www.zione.co/", "zione.co"),
        # Sin trailing slash
        ("http://zione.co", "zione.co"),
        # Path ignorado
        ("https://www.hotel.com/es/", "hotel.com"),
        # Query string ignorado
        ("https://hotel.co?lang=es", "hotel.co"),
        # Case insensitive
        ("https://ZIONE.CO/", "zione.co"),
        # Subdominio preservado (www removido, sub si)
        ("https://www.sub.domain.co/", "sub.domain.co"),
        # HTTP sin www
        ("http://simple-hotel.co", "simple-hotel.co"),
        # Sin protocolo (requiere fix: añadir // antes de urlparse)
        ("zione.co", "zione.co"),
        # URL completa con path, query, fragment
        ("https://www.hotel.com.co/path?q=1#frag", "hotel.com.co"),
        # Caso extra: solo dominio con www y sin protocolo
        ("www.hotel.co", "hotel.co"),
        # Caso extra: https con path largo
        ("https://www.mi-hotel.com.co/habitaciones/suite-presidencial/", "mi-hotel.com.co"),
        # Caso extra: HTTP con www y query params
        ("http://www.hotelboutique.com?utm_source=google&lang=es", "hotelboutique.com"),
    ])
    def test_normalize_url(self, input_url, expected):
        assert _normalize_url(input_url) == expected

    def test_normalize_url_empty_returns_empty(self):
        """URL vacía retorna string vacío."""
        result = _normalize_url("")
        assert isinstance(result, str)
        # urlparse('//') tiene netloc vacío
        assert result == ""

    def test_normalize_url_idempotent(self):
        """Doble normalización produce el mismo resultado."""
        url = "https://www.Zione.Co/path?q=1"
        first = _normalize_url(url)
        second = _normalize_url(first)
        assert first == second == "zione.co"


# ============================================================================
# T2: Tests para _load_latest_onboarding_data() — matching por URL
# ============================================================================

class TestLoadLatestOnboardingData:
    """Tests para _load_latest_onboarding_data() con matching por URL normalizada."""

    # --- Helper ---

    @staticmethod
    def _make_yaml(tmp_path: Path, filename: str, hotel_url: str,
                   hotel_name: str = "Test Hotel", rooms: int = 20,
                   fecha_captura: str = "2026-07-29T10:00:00+00:00",
                   extra: dict | None = None) -> Path:
        """Crea un YAML de onboarding temporal."""
        data = {
            "hotel": {
                "nombre": hotel_name,
                "url": hotel_url,
            },
            "datos_operativos": {
                "habitaciones": rooms,
                "reservas_mes": 180,
                "valor_reserva_cop": 350000,
                "canal_directo_pct": 45.0,
            },
            "metadatos": {
                "fecha_captura": fecha_captura,
                "fuente": "test",
            },
        }
        if extra:
            data.update(extra)
        filepath = tmp_path / filename
        filepath.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        return filepath

    # --- Tests ---

    def test_match_by_url_normalized(self, tmp_path):
        """Un YAML con hotel.url debe matchear por URL normalizada."""
        self._make_yaml(
            tmp_path, "test-hotel_onboarding.yaml",
            hotel_url="https://www.testhotel.com/",
            rooms=20,
        )

        result = _load_latest_onboarding_data(
            hotel_url="https://testhotel.com/",
            hotel_name="Test Hotel",
            output_dir=tmp_path,
        )
        assert result is not None
        assert result["datos_operativos"]["habitaciones"] == 20
        assert result["hotel"]["nombre"] == "Test Hotel"

    def test_no_match_different_url(self, tmp_path):
        """URLs diferentes no deben matchear."""
        self._make_yaml(
            tmp_path, "hotel-a_onboarding.yaml",
            hotel_url="https://hotel-a.com/",
        )

        result = _load_latest_onboarding_data(
            hotel_url="https://hotel-b.com/",
            hotel_name="Hotel B",
            output_dir=tmp_path,
        )
        assert result is None

    def test_no_url_field_returns_none(self, tmp_path):
        """YAML sin hotel.url no matchea (sin fallback)."""
        yaml_content = """hotel:
  nombre: Old Hotel
datos_operativos:
  habitaciones: 10
metadatos:
  fecha_captura: '2026-07-29T10:00:00+00:00'
"""
        (tmp_path / "old-hotel_onboarding.yaml").write_text(yaml_content, encoding="utf-8")

        result = _load_latest_onboarding_data(
            hotel_url="https://oldhotel.com/",
            hotel_name="Old Hotel",
            output_dir=tmp_path,
        )
        # Sin hotel.url, sin observations.json en tmp_path → None
        assert result is None

    def test_empty_output_dir_returns_none(self, tmp_path):
        """Directorio sin YAMLs retorna None."""
        result = _load_latest_onboarding_data(
            hotel_url="https://anyhotel.com/",
            hotel_name="Any Hotel",
            output_dir=tmp_path,
        )
        assert result is None

    def test_multiple_yamls_picks_correct_url(self, tmp_path):
        """Con múltiples YAMLs, solo matchea el de URL correcta."""
        self._make_yaml(tmp_path, "hotel-a_onboarding.yaml",
                        hotel_url="https://hotel-a.com/", rooms=15)
        self._make_yaml(tmp_path, "hotel-b_onboarding.yaml",
                        hotel_url="https://hotel-b.com/", rooms=25)
        self._make_yaml(tmp_path, "hotel-c_onboarding.yaml",
                        hotel_url="https://hotel-c.com/", rooms=35)

        result = _load_latest_onboarding_data(
            hotel_url="https://www.hotel-b.com/",
            hotel_name="Hotel B",
            output_dir=tmp_path,
        )
        assert result is not None
        assert result["datos_operativos"]["habitaciones"] == 25

    def test_corrupt_yaml_skipped(self, tmp_path):
        """YAML corrupto se salta sin romper."""
        # YAML válido con URL correcta
        self._make_yaml(tmp_path, "valid_onboarding.yaml",
                        hotel_url="https://target.com/", rooms=42)
        # YAML corrupto
        (tmp_path / "corrupt_onboarding.yaml").write_text(
            "invalid: yaml: [\n  - broken", encoding="utf-8"
        )

        result = _load_latest_onboarding_data(
            hotel_url="https://target.com/",
            hotel_name="Target",
            output_dir=tmp_path,
        )
        assert result is not None
        assert result["datos_operativos"]["habitaciones"] == 42

    def test_yaml_without_metadatos_skipped(self, tmp_path):
        """YAML sin metadatos se salta."""
        (tmp_path / "no-meta_onboarding.yaml").write_text(
            yaml.dump({"hotel": {"nombre": "No Meta", "url": "https://target.com/"}}),
            encoding="utf-8",
        )
        # Otro YAML válido
        self._make_yaml(tmp_path, "valid_onboarding.yaml",
                        hotel_url="https://target.com/", rooms=99)

        result = _load_latest_onboarding_data(
            hotel_url="https://target.com/",
            hotel_name="Target",
            output_dir=tmp_path,
        )
        assert result is not None
        assert result["datos_operativos"]["habitaciones"] == 99


# ============================================================================
# T3: Tests para _observation_to_onboarding_format()
# ============================================================================

class TestObservationToOnboardingFormat:
    """Tests para _observation_to_onboarding_format()."""

    def test_maps_all_fields(self):
        """Todos los campos del observation se mapean correctamente."""
        obs = {
            "hotel_name": "Zi One Luxury",
            "website": "https://zione.co/",
            "region": "eje_cafetero",
            "rooms": 34,
            "monthly_reservations": 800,
            "avg_reservation_cop": 290000,
            "direct_channel_percentage": 40.0,
            "collected_at": "2026-07-22",
            "confidence": 0.95,
            "epistemic_status": "verified",
        }

        result = _observation_to_onboarding_format(obs)

        assert result["hotel"]["nombre"] == "Zi One Luxury"
        assert result["hotel"]["url"] == "https://zione.co/"
        assert result["hotel"]["ubicacion"] == "eje_cafetero"
        assert result["datos_operativos"]["habitaciones"] == 34
        assert result["datos_operativos"]["reservas_mes"] == 800
        assert result["datos_operativos"]["valor_reserva_cop"] == 290000
        assert result["datos_operativos"]["canal_directo_pct"] == 40.0
        assert result["metadatos"]["confidence"] == 0.95
        assert result["metadatos"]["epistemic_status"] == "verified"
        assert "campos_confirmados" in result["metadatos"]
        assert "habitaciones" in result["metadatos"]["campos_confirmados"]

    def test_missing_fields_use_defaults(self):
        """Campos faltantes usan defaults seguros."""
        obs = {"hotel_name": "Minimal Hotel"}

        result = _observation_to_onboarding_format(obs)

        assert result["hotel"]["nombre"] == "Minimal Hotel"
        assert result["hotel"]["url"] == ""
        assert result["hotel"]["ubicacion"] == ""
        assert result["datos_operativos"]["habitaciones"] == 10
        assert result["datos_operativos"]["reservas_mes"] == 0
        assert result["datos_operativos"]["valor_reserva_cop"] == 0
        assert result["datos_operativos"]["canal_directo_pct"] == 20.0
        assert result["metadatos"]["confidence"] == 0.0
        assert result["metadatos"]["epistemic_status"] == "verified"

    def test_source_note_includes_confidence(self):
        """El campo source_note incluye el nivel de confidence."""
        obs = {
            "hotel_name": "Test",
            "confidence": 0.88,
        }
        result = _observation_to_onboarding_format(obs)
        assert "0.88" in result["metadatos"]["source_note"]
        assert "Tier A" in result["metadatos"]["source_note"]
        assert "observations.json" in result["metadatos"]["source_note"]

    def test_fuente_is_observations_tier_a(self):
        """La fuente del metadata siempre es observations_tier_a."""
        result = _observation_to_onboarding_format({"hotel_name": "X"})
        assert result["metadatos"]["fuente"] == "observations_tier_a"

    def test_fecha_captura_from_collected_at(self):
        """Usa collected_at si está presente."""
        obs = {
            "hotel_name": "Test",
            "collected_at": "2026-07-15",
        }
        result = _observation_to_onboarding_format(obs)
        assert result["metadatos"]["fecha_captura"] == "2026-07-15"
