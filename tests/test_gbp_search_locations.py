import pytest

from modules.scrapers.gbp_auditor import GBPAuditor
from modules.utils.geo_validator import ValidationResult


class DummyElement:
    def __init__(self, aria_label: str):
        self._aria_label = aria_label

    def get_attribute(self, name: str):
        if name == 'aria-label':
            return self._aria_label
        return None

    @property
    def text(self) -> str:
        return self._aria_label


class DummyDriver:
    def __init__(self, rating_labels: list[str], photo_labels: list[str]):
        self._rating_elements = [DummyElement(lbl) for lbl in rating_labels]
        self._photo_elements = [DummyElement(lbl) for lbl in photo_labels]

    def find_elements(self, by: str, value: str):
        value_lower = value.lower()
        if 'estrellas' in value_lower:
            return self._rating_elements
        if 'foto' in value_lower:
            return self._photo_elements
        return []

    def find_element(self, by: str, value: str):
        raise TimeoutError("DummyDriver does not support single element lookup")


def _validation_result(resolved: str | None, actual_city: str | None = None, actual_state: str | None = None) -> ValidationResult:
    return ValidationResult(
        is_valid=False,
        distance_km=12.5,
        threshold_km=5.0,
        expected_location=(4.6376, -75.5737),
        actual_location=(4.8553, -75.5834),
        hotel_name="Hotel Vísperas",
        expected_city="Salento",
        confidence=0.4,
        resolved_location=resolved,
        actual_city=actual_city,
        actual_state=actual_state,
    )


def test_prepare_search_locations_prefers_geo_override():
    validation = _validation_result(
        resolved="Santa Rosa de Cabal, Risaralda",
        actual_city="Santa Rosa de Cabal",
        actual_state="Risaralda",
    )
    candidates = GBPAuditor._prepare_search_locations("Salento, Quindío", validation)
    assert candidates[0] == "Santa Rosa de Cabal, Risaralda"
    assert "Salento, Quindío" in candidates


def test_prepare_search_locations_returns_input_when_same():
    validation = _validation_result(resolved="Salento, Quindío")
    candidates = GBPAuditor._prepare_search_locations("Salento, Quindío", validation)
    assert candidates == ["Salento, Quindío"]


def test_build_resolved_location_falls_back_to_input():
    fallback = "Salento, Quindío"
    result = GBPAuditor._build_resolved_location(None, fallback)
    assert result == fallback


def test_extract_metrics_sets_confidence_flags():
    auditor = GBPAuditor()
    auditor.driver = DummyDriver(
        rating_labels=["4,7 estrellas en 599 reseñas"],
        photo_labels=["Ver 120 fotos"]
    )
    profile = auditor._base_profile()
    html = "<div>4,7 estrellas en 599 reseñas · Ver 120 fotos</div>"

    auditor._extract_metrics(html, profile)

    assert profile['rating'] == pytest.approx(4.7)
    assert profile['reviews'] == 599
    assert profile['fotos'] == 120

    confidence = profile['meta']['data_confidence']
    assert confidence['rating'] is True
    assert confidence['reviews'] is True
    assert confidence['photos'] is True


def test_parse_int_handles_mil_abbreviation():
    assert GBPAuditor._parse_int("1,2 mil") == 1200
    assert GBPAuditor._parse_int("3.5k") == 3500
    assert GBPAuditor._parse_int("750") == 750
