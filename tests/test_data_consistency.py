from unittest.mock import MagicMock

import pytest

from modules.delivery.manager import DeliveryManager
from modules.utils import data_validator
from modules.utils.data_validator import normalize_hotel_data


@pytest.fixture(autouse=True)
def reset_normalization_cache(tmp_path, monkeypatch):
    cache_path = tmp_path / "hotel_normalization.json"
    monkeypatch.setattr(data_validator, "NORMALIZATION_CACHE_PATH", cache_path)
    monkeypatch.setattr(data_validator, "_NORMALIZATION_CACHE", {})
    yield


def test_normalize_hotel_data_prefers_validated_location():
    sample = {
        "url": "https://example.com",
        "nombre": "Hotel Demo",
        "ubicacion": "Ubicación Errónea",
        "ubicacion_validada": "Ciudad Correcta",
    }

    normalized = normalize_hotel_data(sample, persist=False)

    assert normalized["ubicacion"] == "Ciudad Correcta"
    assert normalized["ubicacion_fuente"] == "gbp_validation"


def test_normalize_hotel_data_applies_hardcoded_overrides():
    sample = {
        "url": "https://hotelvisperas.com",
        "nombre": "Hotel Vísperas",
        "ubicacion": "Salento, Quindío",
    }

    normalized = normalize_hotel_data(sample, persist=False)

    assert normalized["ubicacion"].lower() == "santa rosa de cabal, risaralda"
    assert "hardcoded" in normalized.get("ubicacion_fuente", "")


def test_delivery_manager_passes_normalized_location(tmp_path):
    manager = DeliveryManager(tmp_path)
    manager.schema_gen.generate = MagicMock(return_value="{}")
    manager.faq_gen.generate = MagicMock(return_value="faq")
    manager.seo_fix_gen.generate = MagicMock(return_value="seo")
    manager.report_gen.generate = MagicMock(return_value="ia")
    manager.geo_gen.generate = MagicMock(
        return_value={
            "geo_playbook": "Playbook",
            "directories_csv": "csv",
            "review_playbook": "Review",
        }
    )

    raw_data = {
        "url": "https://example.com",
        "nombre": "Hotel Test",
        "ubicacion": "Ciudad Errónea",
        "ubicacion_validada": "Ciudad Correcta",
    }

    manager.execute("pro_aeo", raw_data)

    called_hotel_data = manager.geo_gen.generate.call_args[0][0]
    assert called_hotel_data["ubicacion"] == "Ciudad Correcta"

    delivery_dir = tmp_path / "delivery_assets"
    assert (delivery_dir / "geo_playbook.md").exists()
