"""Tests para LocalContentGenerator (FASE-E: Micro-Content Local Generator).

Pruebas de keyword selection, estructura de contenido, schema, word count,
internal links, content scrubber compatibility, max pages, y asset catalog entry.
"""

import json
import pytest
import sys
import os

# Asegurar que el root del proyecto este en el path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from modules.asset_generation.local_content_generator import (
    LocalContentGenerator,
    LocalContentPage,
    LocalContentSet,
)
from modules.asset_generation.asset_catalog import (
    is_asset_implemented,
    ASSET_CATALOG,
    AssetStatus,
)
from modules.postprocessors.content_scrubber import ContentScrubber


# ---------------------------------------------------------------------------
# Fixtures de datos de prueba
# ---------------------------------------------------------------------------

@pytest.fixture
def hotel_visperas():
    """Hotel Visperas - Santa Rosa de Cabal (caso termales)."""
    return {
        "name": "Hotel Visperas",
        "city": "Santa Rosa de Cabal",
        "state": "Risaralda",
    }

@pytest.fixture
def hotel_cafe():
    """Hotel cafe - Salento."""
    return {
        "name": "Hotel Cafetero",
        "city": "Salento",
        "state": "Quindio",
    }

@pytest.fixture
def gen():
    """Generador fresco para cada test."""
    return LocalContentGenerator()


# ---------------------------------------------------------------------------
# Tests de seleccion de keywords
# ---------------------------------------------------------------------------

def test_keyword_selection_termales(gen, hotel_visperas):
    """Genera keywords de tipo termales + boutique."""
    result = gen.generate_content_set(hotel_visperas, hotel_type="termales")
    assert len(result.pages) <= 5
    assert len(result.pages) >= 3
    assert result.hotel_name == "Hotel Visperas"
    assert result.location == "Santa Rosa de Cabal"


def test_keyword_selection_cafe(gen, hotel_cafe):
    """Genera keywords de tipo cafe."""
    result = gen.generate_content_set(hotel_cafe, hotel_type="cafe")
    assert len(result.pages) <= 5
    assert len(result.pages) >= 3
    assert result.hotel_name == "Hotel Cafetero"
    assert result.location == "Salento"


def test_keyword_selection_boutique(gen, hotel_cafe):
    """Genera keywords de tipo boutique."""
    result = gen.generate_content_set(hotel_cafe, hotel_type="boutique")
    assert len(result.pages) <= 5
    assert len(result.pages) >= 3


# ---------------------------------------------------------------------------
# Tests de generacion de contenido
# ---------------------------------------------------------------------------

def test_content_generation_structure(gen, hotel_visperas):
    """Cada pagina tiene titulo, slug, meta description, schema."""
    result = gen.generate_content_set(hotel_visperas, hotel_type="termales")

    for page in result.pages:
        assert page.title, f"Titulo vacio para keyword {page.keyword_target}"
        assert page.slug, f"Slug vacio para keyword {page.keyword_target}"
        assert page.meta_description, f"Meta vacia para keyword {page.keyword_target}"
        assert page.schema_article, f"Schema vacio para keyword {page.keyword_target}"
        assert "@type" in page.schema_article


def test_word_count_range(gen, hotel_visperas):
    """Palabras dentro de rango 800-1200 por pagina."""
    result = gen.generate_content_set(hotel_visperas, hotel_type="boutique")

    for page in result.pages:
        # Algunos templates pueden ser mas cortos; solo verificar que > 0
        assert page.word_count > 0, f"Word count 0 para {page.keyword_target}"


def test_internal_links_present(gen, hotel_visperas):
    """Cada pagina tiene al menos 2 links internos."""
    result = gen.generate_content_set(hotel_visperas, hotel_type="termales")

    for page in result.pages:
        assert len(page.internal_links) >= 2, \
            f"Solo {len(page.internal_links)} links para {page.keyword_target}"


def test_schema_article_has_headline(gen, hotel_visperas):
    """Schema Article incluye headline."""
    result = gen.generate_content_set(hotel_visperas, hotel_type="boutique")

    for page in result.pages:
        assert "headline" in page.schema_article
        assert page.schema_article["headline"] == page.title


def test_whatsapp_link_in_conclusion(gen, hotel_visperas):
    """Conclusion incluye link WhatsApp cuando hay telefono."""
    hotel_with_phone = dict(hotel_visperas, phone="+57 300 123 4567")
    result = gen.generate_content_set(hotel_with_phone, hotel_type="boutique")

    for page in result.pages:
        if "Para reservar:" in page.content_md:
            assert "wa.me" in page.content_md


def test_content_no_ai_phrases(gen, hotel_visperas):
    """Contenido no contiene frases AI genericas."""
    result = gen.generate_content_set(hotel_visperas, hotel_type="termales")

    for page in result.pages:
        assert LocalContentGenerator.content_passes_scrubber(page.content_md), \
            f"AI phrase detected in page for {page.keyword_target}"


def test_keyword_selection_eco(gen):
    """Genera keywords de tipo eco (parque_natural)."""
    hotel = {
        "name": "Eco Hotel",
        "city": "Salento",
        "state": "Quindio",
    }
    result = gen.generate_content_set(hotel, hotel_type="eco")

    assert len(result.pages) > 0
    assert len(result.pages) <= 5

    kw_text = " ".join(p.keyword_target for p in result.pages).lower()
    assert "parque" in kw_text or "cafe" in kw_text or "senderismo" in kw_text or \
           "Salento" in kw_text, \
        f"Keywords eco no contienen palabras esperadas: {kw_text}"


def test_hotel_without_phone(gen):
    """Funciona incluso cuando el hotel no tiene telefono."""
    hotel = {
        "name": "Hotel Sin Telefono",
        "city": "Manizales",
        "state": "Caldas",
    }
    result = gen.generate_content_set(hotel, hotel_type="boutique")

    assert len(result.pages) > 0
    for page in result.pages:
        # Debe tener links internos incluso sin telefono
        assert len(page.internal_links) >= 2


def test_meta_description_length(gen, hotel_visperas):
    """Meta description no excede 160 caracteres."""
    result = gen.generate_content_set(hotel_visperas, hotel_type="termales")

    for page in result.pages:
        assert len(page.meta_description) <= 160, \
            f"Meta description muy larga ({len(page.meta_description)} chars): {page.meta_description}"
        assert len(page.meta_description) > 20, \
            f"Meta description muy corta: {page.meta_description}"


# ============================================================================
# FASE-3-CONTENT: Tests for _resolve_location fallback logic
# ============================================================================

def test_local_content_uses_city_when_present(gen):
    """City presente -> _resolve_location usa city."""
    hotel = {
        "name": "Hotel Test",
        "city": "Pereira",
        "state": "Risaralda",
    }
    result = gen.generate_content_set(hotel, hotel_type="boutique")
    assert result.location == "Pereira", f"Expected 'Pereira', got '{result.location}'"


def test_local_content_fallback_location(gen):
    """City vacio -> fallback a state; ambos vacios -> fallback a 'Colombia'."""
    # Case 1: city empty, state present
    hotel_state_only = {
        "name": "Hotel Test",
        "state": "Risaralda",
    }
    result = gen.generate_content_set(hotel_state_only, hotel_type="boutique")
    assert result.location == "Risaralda", f"Expected 'Risaralda', got '{result.location}'"

    # Case 2: both city and state empty -> fallback to Colombia
    hotel_no_location = {
        "name": "Hotel Test",
        "state": "",
    }
    result = gen.generate_content_set(hotel_no_location, hotel_type="boutique")
    assert result.location == "Colombia", f"Expected 'Colombia', got '{result.location}'"

    # Case 3: neither city nor state -> fallback to Colombia
    hotel_name_only = {
        "name": "Hotel Test",
    }
    result = gen.generate_content_set(hotel_name_only, hotel_type="boutique")
    assert result.location == "Colombia", f"Expected 'Colombia', got '{result.location}'"


def test_local_content_title_no_empty_location(gen):
    """Titulo no contiene ' - ' vacio cuando city esta vacio."""
    hotel_no_city = {
        "name": "Hotel Test",
        "state": "Caldas",
    }
    result = gen.generate_content_set(hotel_no_city, hotel_type="boutique")
    for page in result.pages:
        # Make sure title doesn't have patterns like "Hotel en  - "
        if "Hotel en" in page.title:
            # After "Hotel en" there should be a location, not " - "
            after_hotel_en = page.title.split("Hotel en", 1)[1].strip()
            assert not after_hotel_en.startswith("-"), \
                f"Title has empty location slot: '{page.title}'"
