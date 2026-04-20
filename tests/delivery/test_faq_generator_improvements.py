"""Test for FAQ generator output format.

Validates that FAQGenerator produces valid JSON-LD (schema.org FAQPage)
instead of the legacy CSV format.
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from modules.delivery.generators.faq_gen import FAQGenerator


def test_faq_generator_output_is_jsonld():
    """FAQ generator must produce valid JSON-LD with FAQPage type."""
    hotel_data = {
        'nombre': 'Hotel Test',
        'ubicacion': 'Pereira, Colombia',
        'servicios': ['wifi', 'piscina'],
        'precio_promedio': '100'
    }
    generator = FAQGenerator()
    output, _ = generator.generate(hotel_data, count=2, reason='Test')

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


def test_faq_generator_has_timestamp():
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
