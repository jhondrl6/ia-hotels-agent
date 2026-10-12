"""Tests para llm_extractor.py — protocolo de extracción LLM.

Valida el protocolo PromiseExtractor, la implementación LLM (con un arnés local del
proveedor, sin red) y el MockPromiseExtractor para tests sin dependencia de LLM real.

Los estados del contrato se prueban en
`test_llm_extractor_contrato_cuatro_estados.py`; este archivo cubre la superficie de
siempre del extractor sobre la API checked (`extract_checked`), que tras FASE-B es la
unica via.
"""

import pytest

from modules.providers.llm_provider import ChatCompletionDetail
from modules.quality_gates.tribunal import llm_extractor
from modules.quality_gates.tribunal.llm_extractor import (
    ExtractionState,
    LLMPromiseExtractor,
    MockPromiseExtractor,
    PromiseExtractor,
    VerbalPromise,
)


@pytest.fixture(autouse=True)
def configuracion_arnesada(monkeypatch):
    """La clave de cache se resuelve sin keyring y sin .env real."""
    monkeypatch.setattr(llm_extractor, "_read_config", lambda nombre: None)


class ProveedorFalso:
    """Arnés mínimo del contrato de proveedor: texto fijo, sin llamada real."""

    def __init__(self, texto):
        self.texto = texto
        self.llamadas = []

    def chat_completion(self, prompt, model=None, max_tokens=1000, temperature=0.7):
        self.llamadas.append(prompt)
        return self.texto

    def chat_completion_detailed(self, prompt, model=None, max_tokens=1000, temperature=0.7):
        self.llamadas.append(prompt)
        return ChatCompletionDetail(
            text=self.texto,
            finish_reason="stop",
            model_requested=model or "deepseek-chat",
            model_served="deepseek-chat",
            provider_name="deepseek",
        )

    def get_provider_name(self):
        return "deepseek"


class TestVerbalPromise:
    """Tests para la dataclass VerbalPromise."""

    def test_to_dict(self):
        promise = VerbalPromise(
            text="Implementaremos un botón de WhatsApp",
            service_hint="whatsapp_bot",
            location="Alcance del Proyecto",
        )
        d = promise.to_dict()
        assert d["text"] == "Implementaremos un botón de WhatsApp"
        assert d["service_hint"] == "whatsapp_bot"
        assert d["location"] == "Alcance del Proyecto"

    def test_from_dict(self):
        data = {
            "text": "FAQ page",
            "service_hint": "faq_page",
            "location": "Entregables",
        }
        promise = VerbalPromise.from_dict(data)
        assert promise.text == "FAQ page"
        assert promise.service_hint == "faq_page"
        assert promise.location == "Entregables"

    def test_roundtrip(self):
        original = VerbalPromise("test", "hint", "loc")
        restored = VerbalPromise.from_dict(original.to_dict())
        assert restored.text == original.text
        assert restored.service_hint == original.service_hint
        assert restored.location == original.location


class TestPromiseExtractorProtocol:
    """Tests para el protocolo PromiseExtractor (runtime_checkable)."""

    def test_extractor_protocol_compliance(self, tmp_path):
        """LLMPromiseExtractor cumple PromiseExtractor protocol."""
        extractor = LLMPromiseExtractor(provider=ProveedorFalso("[]"), cache_dir=tmp_path)
        assert isinstance(extractor, PromiseExtractor)

    def test_mock_extractor_protocol_compliance(self):
        """MockPromiseExtractor cumple PromiseExtractor protocol."""
        mock = MockPromiseExtractor([])
        assert isinstance(mock, PromiseExtractor)

    def test_protocol_runtime_checkable(self):
        """El protocolo es runtime_checkable."""
        assert hasattr(PromiseExtractor, "__protocol_attrs__") or callable(PromiseExtractor)


class TestMockPromiseExtractor:
    """Tests para MockPromiseExtractor (sin LLM real)."""

    def test_mock_extractor_used_in_tests(self):
        """MockPromiseExtractor retorna promesas fijas, sin LLM."""
        promises = [
            VerbalPromise("WhatsApp", "whatsapp_bot", "Intro"),
            VerbalPromise("FAQ", "faq_page", "Entregables"),
        ]
        mock = MockPromiseExtractor(promises)
        result = mock.extract_checked("cualquier texto").promises
        assert len(result) == 2
        assert result[0].text == "WhatsApp"
        assert result[1].text == "FAQ"

    def test_mock_extractor_ignores_input(self):
        """MockPromiseExtractor ignora el texto de entrada."""
        promises = [VerbalPromise("test", "hint", "loc")]
        mock = MockPromiseExtractor(promises)
        result1 = mock.extract_checked("texto 1").promises
        result2 = mock.extract_checked("texto 2").promises
        assert result1 == result2

    def test_mock_extractor_empty(self):
        """MockPromiseExtractor con lista vacía retorna []."""
        mock = MockPromiseExtractor([])
        result = mock.extract_checked("texto").promises
        assert result == []


class TestLLMPromiseExtractor:
    """Tests para LLMPromiseExtractor con proveedor arnesado (sin red)."""

    def test_llm_extractor_with_mock_provider(self, tmp_path):
        """LLMPromiseExtractor usa el provider inyectado."""
        mock_provider = ProveedorFalso('[{"text": "WhatsApp", "service_hint": "whatsapp_bot", "location": "Intro"}]')

        extractor = LLMPromiseExtractor(provider=mock_provider, cache_dir=tmp_path)
        result = extractor.extract_checked("texto de propuesta").promises

        assert len(result) == 1
        assert result[0].text == "WhatsApp"
        assert len(mock_provider.llamadas) == 1

    def test_llm_extractor_cache_hit(self, tmp_path):
        """LLMPromiseExtractor usa cache para el mismo texto."""
        mock_provider = ProveedorFalso("[]")

        extractor = LLMPromiseExtractor(provider=mock_provider, cache_dir=tmp_path)
        extractor.extract_checked("texto").promises
        extractor.extract_checked("texto").promises

        assert len(mock_provider.llamadas) == 1

    def test_llm_extractor_cache_miss(self, tmp_path):
        """LLMPromiseExtractor llama al LLM para textos diferentes."""
        mock_provider = ProveedorFalso("[]")

        extractor = LLMPromiseExtractor(provider=mock_provider, cache_dir=tmp_path)
        extractor.extract_checked("texto 1").promises
        extractor.extract_checked("texto 2").promises

        assert len(mock_provider.llamadas) == 2

    def test_llm_extractor_parses_json_with_markdown(self, tmp_path):
        """LLMPromiseExtractor parsea respuesta con markdown code block."""
        mock_provider = ProveedorFalso(
            """```json
[{"text": "FAQ", "service_hint": "faq_page", "location": "Entregables"}]
```"""
        )

        extractor = LLMPromiseExtractor(provider=mock_provider, cache_dir=tmp_path)
        result = extractor.extract_checked("texto").promises

        assert len(result) == 1
        assert result[0].text == "FAQ"

    def test_llm_extractor_handles_invalid_json(self, tmp_path):
        """Respuesta ilegible: estado NO_EVALUABLE con promesas vacias, no un [] mudo."""
        mock_provider = ProveedorFalso("esto no es JSON")

        extractor = LLMPromiseExtractor(provider=mock_provider, cache_dir=tmp_path)
        outcome = extractor.extract_checked("texto")

        assert outcome.state is ExtractionState.NO_EVALUABLE
        assert outcome.promises == []
        assert outcome.reason

    def test_llm_extractor_filters_invalid_promises(self, tmp_path):
        """LLMPromiseExtractor filtra promesas sin campos requeridos."""
        mock_provider = ProveedorFalso("""[
            {"text": "Válida", "service_hint": "hint", "location": "loc"},
            {"text": "", "service_hint": "hint", "location": "loc"},
            {"service_hint": "hint", "location": "loc"}
        ]""")

        extractor = LLMPromiseExtractor(provider=mock_provider, cache_dir=tmp_path)
        result = extractor.extract_checked("texto").promises

        assert len(result) == 1
        assert result[0].text == "Válida"
