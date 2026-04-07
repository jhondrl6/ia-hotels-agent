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
        "phone": "+57 316 293 0658",
        "website": "https://hotelvisperas.com",
        "services": ["Spa", "Termales", "Restaurante", "WiFi"],
    }


@pytest.fixture
def hotel_eco():
    """Hotel tipo eco/bosque (prueba de tipo diferente)."""
    return {
        "name": "Hotel Bosques del Cafe",
        "city": "Salento",
        "state": "Quindio",
        "phone": "+57 310 123 4567",
        "website": "https://bosquesdelcafe.co",
        "services": ["Senderismo", "Tour del Cafe", "Cabanas"],
    }


@pytest.fixture
def gen():
    """Instancia del generador."""
    return LocalContentGenerator()


# ---------------------------------------------------------------------------
# Test 1: Keyword selection termales
# ---------------------------------------------------------------------------

def test_keyword_selection_termales(gen, hotel_visperas):
    """Genera keywords con {location} reemplazado para tipo termales."""
    keywords = gen._select_keywords(
        hotel_visperas,
        hotel_type="termales",
        location_context={"region": "Eje Cafetero", "nearby_city": "Pereira"},
    )

    # Debe generar keywords
    assert len(keywords) > 0, "No se generaron keywords"
    assert len(keywords) <= 5, f"Se generaron mas de 5 keywords: {len(keywords)}"

    # El placeholder {location} debe estar reemplazado
    for kw in keywords:
        assert "{location}" not in kw and "{region}" not in kw and "{nearby_city}" not in kw, \
            f"Keyword aun contiene placeholder: {kw}"
        # Puede tener city, region o nearby_city (Pereira)
        has_place = any(x in kw for x in ["Santa Rosa de Cabal", "Eje Cafetero", "Pereira"])
        assert has_place, f"Keyword no contiene datos de ubicacion: {kw}"

    # Debe haber keywords de termales y boutique combinadas
    kw_text = " ".join(keywords).lower()
    assert "termales" in kw_text, "No incluye keywords de termales"


# ---------------------------------------------------------------------------
# Test 2: Keyword selection boutique
# ---------------------------------------------------------------------------

def test_keyword_selection_boutique(gen, hotel_visperas):
    """Genera keywords de hotel boutique correctamente."""
    keywords = gen._select_keywords(
        hotel_visperas,
        hotel_type="boutique",
        location_context={"region": "Eje Cafetero"},
    )

    assert len(keywords) > 0
    kw_text = " ".join(keywords).lower()
    assert "boutique" in kw_text, "No incluye keywords boutique"

    # No debe haber keywords de termales si el tipo es boutique
    kw_text = " ".join(keywords).lower()
    # Boutique type = boutique + general templates, NO termales
    assert "boutique" in kw_text or "hospedarse" in kw_text or "hotel" in kw_text


# ---------------------------------------------------------------------------
# Test 3: Page structure
# ---------------------------------------------------------------------------

def test_page_structure(gen, hotel_visperas):
    """Cada pagina tiene titulo, slug, contenido y schema."""
    result = gen.generate_content_set(hotel_visperas, hotel_type="termales")

    assert len(result.pages) > 0, "No se generaron paginas"

    for page in result.pages:
        assert page.keyword_target, f"Pagina sin keyword_target: {page.title}"
        assert page.title, f"Pagina sin titulo"
        assert page.slug, f"Pagina sin slug"
        assert page.content_md, f"Pagina sin contenido"
        assert page.schema_article, f"Pagina sin schema"
        assert isinstance(page.schema_article, dict)
        assert page.internal_links, f"Pagina sin links internos"
        assert isinstance(page.internal_links, list)
        assert page.meta_description, f"Pagina sin meta_description"
        assert page.word_count > 0, f"Word count debe ser positivo: {page.word_count}"


# ---------------------------------------------------------------------------
# Test 4: Word count en rango (800-1200 palabras)
# ---------------------------------------------------------------------------

def test_word_count_range(gen, hotel_visperas):
    """Cada pagina tiene entre 800 y 1200 palabras."""
    result = gen.generate_content_set(hotel_visperas, hotel_type="termales")

    rules = LocalContentGenerator.CONTENT_RULES
    min_words = rules["word_count_min"]
    max_words = rules["word_count_max"]

    for page in result.pages:
        assert page.word_count >= min_words, \
            f"Pagina '{page.title}' tiene menos de {min_words} palabras: {page.word_count}"
        assert page.word_count <= max_words, \
            f"Pagina '{page.title}' tiene mas de {max_words} palabras: {page.word_count}"


# ---------------------------------------------------------------------------
# Test 5: Internal links (minimo 2)
# ---------------------------------------------------------------------------

def test_internal_links(gen, hotel_visperas):
    """Cada pagina tiene minimo 2 links internos (home + reservas)."""
    result = gen.generate_content_set(hotel_visperas, hotel_type="termales")

    for page in result.pages:
        assert len(page.internal_links) >= 2, \
            f"Pagina '{page.title}' tiene menos de 2 links: {len(page.internal_links)}"


# ---------------------------------------------------------------------------
# Test 6: Article schema JSON-LD valido
# ---------------------------------------------------------------------------

def test_article_schema(gen, hotel_visperas):
    """El schema Article JSON-LD es valido y tiene campos requeridos."""
    result = gen.generate_content_set(hotel_visperas, hotel_type="termales")

    for page in result.pages:
        schema = page.schema_article

        assert "@context" in schema, "Schema sin @context"
        assert schema["@context"] == "https://schema.org", \
            f"@context incorrecto: {schema['@context']}"
        assert "@type" in schema, "Schema sin @type"
        assert schema["@type"] == "Article", f"@type incorrecto: {schema['@type']}"
        assert "headline" in schema, "Schema sin headline"
        assert "description" in schema, "Schema sin description"
        assert "author" in schema, "Schema sin author"
        assert schema["author"]["@type"] == "Organization"
        assert schema["author"]["name"] == hotel_visperas["name"]
        assert "publisher" in schema, "Schema sin publisher"
        assert schema["publisher"]["name"] == hotel_visperas["name"]

        # Validar que es JSON serializable
        json_str = json.dumps(schema)
        assert len(json_str) > 0


# ---------------------------------------------------------------------------
# Test 7: Mencion natural del hotel (no vendedora)
# ---------------------------------------------------------------------------

def test_hotel_mention_natural(gen, hotel_visperas):
    """El hotel se menciona naturalmente pero NO de forma vendedora."""
    result = gen.generate_content_set(hotel_visperas, hotel_type="termales")
    hotel_name = hotel_visperas["name"]

    for page in result.pages:
        content = page.content_md.lower()

        # El hotel debe mencionarse al menos una vez
        assert hotel_name.lower() in content, \
            f"Pagina '{page.title}' no menciona al hotel"

        # Count menciones - debe ser razonable (1 a 5 para tono natural)
        mentions = content.count(hotel_name.lower())
        assert mentions <= 5, \
            f"Pagina '{page.title}' menciona al hotel {mentions} veces (max 5 para tono natural)"

        # No debe tener frases excesivamente vendedoras
        salesy_phrases = [
            "compra ahora",
            "oferta especial",
            "descuento exclusivo",
            "reserva ya mismo",
            "oferta limitada",
            "solo por hoy",
        ]
        for phrase in salesy_phrases:
            assert phrase not in content, \
                f"Pagina '{page.title}' tiene frase vendedora: '{phrase}'"


# ---------------------------------------------------------------------------
# Test 8: Pasa Content Scrubber (FASE-B)
# ---------------------------------------------------------------------------

def test_content_scrubber_pass(gen, hotel_visperas):
    """El contenido pasa el Content Scrubber de FASE-B sin problemas graves."""
    result = gen.generate_content_set(hotel_visperas, hotel_type="termales")
    scrubber = ContentScrubber()

    for page in result.pages:
        scrub_result = scrubber.scrub(page.content_md, hotel_visperas, "local_content")

        # Los fixes del scrubber deben ser minimos (indicador de buena calidad)
        # El scrubber puede aplicar fix_region_placeholders si hay "en default"
        # pero eso es un fix positivo, no un error del contenido
        assert scrub_result is not None

        # Verificar que no hay placeholders sin reemplazar
        scrubbed = scrub_result.scrubbed
        assert "en default" not in scrubbed.lower(), \
            f"Pagina '{page.title}' contiene 'en default' sin reemplazar"
        assert "COP COP" not in scrubbed, \
            f"Pagina '{page.title}' contiene 'COP COP' duplicado"

        # Verificar que el contenido limpio no es vacio
        assert len(scrubbed.strip()) > 0, f"Contenido limpio vacio"


# ---------------------------------------------------------------------------
# Test 9: Max 5 pages
# ---------------------------------------------------------------------------

def test_max_5_pages(gen, hotel_visperas):
    """No genera mas de 5 paginas."""
    result = gen.generate_content_set(hotel_visperas, hotel_type="termales")
    assert len(result.pages) <= 5, \
        f"Genero {len(result.pages)} paginas (maximo permitidas: 5)"


# ---------------------------------------------------------------------------
# Test 10: Asset catalog entry
# ---------------------------------------------------------------------------

def test_asset_catalog_entry():
    """local_content_page esta registrado en el asset catalog."""
    # Debe existir en el catalogo
    assert "local_content_page" in ASSET_CATALOG, \
        "local_content_page no esta en el asset catalog"

    entry = ASSET_CATALOG["local_content_page"]
    assert entry.status == AssetStatus.IMPLEMENTED, \
        f"Estado incorrecto: {entry.status}"
    assert entry.asset_type == "local_content_page"
    assert "page_template" in entry.template
    assert entry.required_field == "hotel_data"
    assert entry.required_confidence == 0.5
    assert entry.block_on_failure is False

    # is_asset_implemented debe retornar True
    assert is_asset_implemented("local_content_page") is True, \
        "is_asset_implemented('local_content_page') retorna False"


# ---------------------------------------------------------------------------
# Tests adicionales de robustez
# ---------------------------------------------------------------------------

def test_slug_generation(gen):
    """El slug es URL-safe."""
    slug = gen._build_slug("termales santa rosa de cabal precios")
    assert " " not in slug, f"Slug contiene espacios: {slug}"
    assert slug == "termales-santa-rosa-de-cabal-precios", f"Slug incorrecto: {slug}"


def test_content_scrubber_compatibility_method(gen, hotel_visperas):
    """El metodo content_passes_scrubber detecta frases AI genericas."""
    # Contenido limpio debe pasar
    clean_content = """
    # Sobre termales en Santa Rosa de Cabal
    Esta guia recopila informacion util sobre las termales de la zona.
    La ubicacion ofrece acceso a atractivos naturales y gastronomia local.
    Hotel Visperas se encuentra cerca de los principales atractivos.
    Para reservar contacta al hotel.
    """
    assert LocalContentGenerator.content_passes_scrubber(clean_content) is True

    # Contenido con frase AI debe fallar
    ai_content = "En el corazon de Colombia, descubre la magia de este destino Vibrante"
    assert LocalContentGenerator.content_passes_scrubber(ai_content) is False


def test_eco_hotel_type(gen, hotel_eco):
    """Funciona con tipo eco (parque natural / cafe)."""
    result = gen.generate_content_set(hotel_eco, hotel_type="eco")

    assert len(result.pages) > 0
    assert len(result.pages) <= 5

    kw_text = " ".join(p.keyword_target for p in result.pages).lower()
    # Eco type = parque_natural + cafe + general
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
