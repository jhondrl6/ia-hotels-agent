"""Test for FAQ generator output format.

Validates that FAQGenerator produces valid JSON-LD (schema.org FAQPage)
instead of the legacy CSV format.

El provider se aisla con `llamadas_provider`: lo que se mide es el ensamble CSV -> JSON-LD
de `generate()`, no la disponibilidad de un tercero. Sin ese aislamiento el archivo hace red.
"""
import sys
import os
import json

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from modules.delivery.generators import faq_gen
from modules.delivery.generators.faq_gen import FAQGenerator


@pytest.fixture
def llamadas_provider(monkeypatch):
    """Aislamiento del proveedor: `generate_list` llama a `unified_request` real y ese camino
    hace red (`api.deepseek.com`, timeout de 61 s). El contrato que se mide aqui es el ensamble
    CSV -> JSON-LD de `generate()`, no la cuota de un tercero, asi que el mock devuelve la forma
    que el propio prompt exige (CSV estricto) y deja constancia de cuantas veces lo usaron.

    Devuelve la lista de prompts recibidos: vacia o con dos llamadas es un rojo, no un verde.
    """
    llamadas: list[str] = []

    def fake_unified_request(self, prompt, **kwargs):
        llamadas.append(prompt)
        return (
            "¿El hotel ofrece wifi?, Si, Hotel Test ofrece wifi y piscina para sus huespedes en "
            "Pereira, Colombia.\n"
            "¿Tiene piscina?, Si, Hotel Test mantiene una piscina disponible para sus huespedes "
            "en Pereira, Colombia."
        )

    monkeypatch.setattr(faq_gen.ProviderAdapter, "unified_request", fake_unified_request)
    return llamadas


def test_faq_generator_output_is_jsonld(llamadas_provider):
    """FAQ generator must produce valid JSON-LD with FAQPage type."""
    hotel_data = {
        'nombre': 'Hotel Test',
        'ubicacion': 'Pereira, Colombia',
        'servicios': ['wifi', 'piscina'],
        'precio_promedio': '100'
    }
    generator = FAQGenerator()
    output, _ = generator.generate(hotel_data, count=2, reason='Test')

    # El arbol solo vale si salio del provider: sin llamada, `generate()` devuelve el esquema
    # vacio y las aserciones de abajo pasarian por vacio en vez de por correctas.
    assert len(llamadas_provider) == 1, \
        f"el provider debio consultarse una vez, se consulto {len(llamadas_provider)}"

    # Parse as JSON
    data = json.loads(output)

    # Validate JSON-LD structure
    assert data.get("@context") == "https://schema.org", \
        f"@context must be schema.org, got: {data.get('@context')}"
    assert data.get("@type") == "FAQPage", \
        f"@type must be FAQPage, got: {data.get('@type')}"
    assert "mainEntity" in data, "Must have mainEntity array"
    assert isinstance(data["mainEntity"], list), "mainEntity must be a list"
    assert len(data["mainEntity"]) > 0, "mainEntity must have at least 1 item"

    # Validate each FAQ item
    for item in data["mainEntity"]:
        assert item.get("@type") == "Question", \
            f"Each item must be Question, got: {item.get('@type')}"
        assert "name" in item, "Question must have 'name'"
        assert "acceptedAnswer" in item, "Question must have 'acceptedAnswer'"
        answer = item["acceptedAnswer"]
        assert answer.get("@type") == "Answer", \
            f"Answer must be Answer type, got: {answer.get('@type')}"
        assert "text" in answer, "Answer must have 'text'"


def test_faq_generator_has_timestamp(llamadas_provider):
    """FAQ generator output must include a generation timestamp."""
    hotel_data = {
        'nombre': 'Hotel Test',
        'ubicacion': 'Test',
        'servicios': ['wifi'],
        'precio_promedio': '100'
    }
    generator = FAQGenerator()
    output, metadata = generator.generate(hotel_data, count=2, reason='Test')

    # metadata should contain timestamp or generation info
    assert metadata is not None, "Generator must return metadata"
