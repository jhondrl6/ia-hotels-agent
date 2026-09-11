"""Tests para llm_extractor.py — protocolo de extracción LLM.

Valida el protocolo PromiseExtractor, la implementación LLM (con mock de provider),
y el MockPromiseExtractor para tests sin dependencia de LLM real.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from modules.quality_gates.tribunal.llm_extractor import (
    LLMPromiseExtractor,
    MockPromiseExtractor,
    PromiseExtractor,
    VerbalPromise,
)


class TestVerbalPromise:
    """Tests para la dataclass VerbalPromise."""

    def test_to_dict(self):
        promise = VerbalPromise(
            text="Implementaremos un botón de WhatsApp",
            service_hint="whatsapp_bot",
            location="Alcance del Proyecto",
            confidence=0.95,
        )
        d = promise.to_dict()
        assert d["text"] == "Implementaremos un botón de WhatsApp"
        assert d["service_hint"] == "whatsapp_bot"
        assert d["location"] == "Alcance del Proyecto"
        assert d["confidence"] == 0.95

    def test_from_dict(self):
        data = {
            "text": "FAQ page",
            "service_hint": "faq_page",
            "location": "Entregables",
            "confidence": 0.85,
        }
        promise = VerbalPromise.from_dict(data)
        assert promise.text == "FAQ page"
        assert promise.service_hint == "faq_page"
        assert promise.confidence == 0.85

    def test_roundtrip(self):
        original = VerbalPromise("test", "hint", "loc", 0.9)
        restored = VerbalPromise.from_dict(original.to_dict())
        assert restored.text == original.text
        assert restored.service_hint == original.service_hint
        assert restored.confidence == original.confidence


class TestPromiseExtractorProtocol:
    """Tests para el protocolo PromiseExtractor (runtime_checkable)."""

    def test_extractor_protocol_compliance(self, tmp_path):
        """LLMPromiseExtractor cumple PromiseExtractor protocol."""
        extractor = LLMPromiseExtractor(provider=MagicMock(), cache_dir=tmp_path)
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
            VerbalPromise("WhatsApp", "whatsapp_bot", "Intro", 0.9),
            VerbalPromise("FAQ", "faq_page", "Entregables", 0.85),
        ]
        mock = MockPromiseExtractor(promises)
        result = mock.extract_verbal_promises("cualquier texto")
        assert len(result) == 2
        assert result[0].text == "WhatsApp"
        assert result[1].text == "FAQ"

    def test_mock_extractor_ignores_input(self):
        """MockPromiseExtractor ignora el texto de entrada."""
        promises = [VerbalPromise("test", "hint", "loc", 0.9)]
        mock = MockPromiseExtractor(promises)
        result1 = mock.extract_verbal_promises("texto 1")
        result2 = mock.extract_verbal_promises("texto 2")
        assert result1 == result2

    def test_mock_extractor_empty(self):
        """MockPromiseExtractor con lista vacía retorna []."""
        mock = MockPromiseExtractor([])
        result = mock.extract_verbal_promises("texto")
        assert result == []


class TestLLMPromiseExtractor:
    """Tests para LLMPromiseExtractor con provider mockeado."""

    def test_llm_extractor_with_mock_provider(self, tmp_path):
        """LLMPromiseExtractor usa el provider inyectado."""
        mock_provider = MagicMock()
        mock_provider.chat_completion.return_value = '[{"text": "WhatsApp", "service_hint": "whatsapp_bot", "location": "Intro", "confidence": 0.9}]'

        extractor = LLMPromiseExtractor(provider=mock_provider, cache_dir=tmp_path)
        result = extractor.extract_verbal_promises("texto de propuesta")

        assert len(result) == 1
        assert result[0].text == "WhatsApp"
        mock_provider.chat_completion.assert_called_once()

    def test_llm_extractor_cache_hit(self, tmp_path):
        """LLMPromiseExtractor usa cache para el mismo texto."""
        mock_provider = MagicMock()
        mock_provider.chat_completion.return_value = '[]'

        extractor = LLMPromiseExtractor(provider=mock_provider, cache_dir=tmp_path)
        extractor.extract_verbal_promises("texto")
        extractor.extract_verbal_promises("texto")

        assert mock_provider.chat_completion.call_count == 1

    def test_llm_extractor_cache_miss(self, tmp_path):
        """LLMPromiseExtractor llama al LLM para textos diferentes."""
        mock_provider = MagicMock()
        mock_provider.chat_completion.return_value = '[]'

        extractor = LLMPromiseExtractor(provider=mock_provider, cache_dir=tmp_path)
        extractor.extract_verbal_promises("texto 1")
        extractor.extract_verbal_promises("texto 2")

        assert mock_provider.chat_completion.call_count == 2

    def test_llm_extractor_parses_json_with_markdown(self, tmp_path):
        """LLMPromiseExtractor parsea respuesta con markdown code block."""
        mock_provider = MagicMock()
        mock_provider.chat_completion.return_value = """```json
[{"text": "FAQ", "service_hint": "faq_page", "location": "Entregables", "confidence": 0.85}]
```"""

        extractor = LLMPromiseExtractor(provider=mock_provider, cache_dir=tmp_path)
        result = extractor.extract_verbal_promises("texto")

        assert len(result) == 1
        assert result[0].text == "FAQ"

    def test_llm_extractor_handles_invalid_json(self, tmp_path):
        """LLMPromiseExtractor retorna [] para JSON inválido."""
        mock_provider = MagicMock()
        mock_provider.chat_completion.return_value = "esto no es JSON"

        extractor = LLMPromiseExtractor(provider=mock_provider, cache_dir=tmp_path)
        result = extractor.extract_verbal_promises("texto")

        assert result == []

    def test_llm_extractor_filters_invalid_promises(self, tmp_path):
        """LLMPromiseExtractor filtra promesas sin campos requeridos."""
        mock_provider = MagicMock()
        mock_provider.chat_completion.return_value = """[
            {"text": "Válida", "service_hint": "hint", "location": "loc", "confidence": 0.9},
            {"text": "", "service_hint": "hint", "location": "loc", "confidence": 0.9},
            {"service_hint": "hint", "location": "loc", "confidence": 0.9}
        ]"""

        extractor = LLMPromiseExtractor(provider=mock_provider, cache_dir=tmp_path)
        result = extractor.extract_verbal_promises("texto")

        assert len(result) == 1
        assert result[0].text == "Válida"
