"""
Tests AC-S1 — FASE-P5: sanitización de API keys en errores y logs.

NR7: cada test de detección tiene su mutación que lo pone rojo.
- Verde: sanitización activa → la key nunca aparece en el log.
- Rojo (NR7): sanitización desactivada → la key aparece en el log.

Cubre:
- _sanitize_text: reemplaza valores de keys conocidas.
- _sanitize_error: redacta params key= de URLs en mensajes de error.
- _query_gemini 403: key no viaja en URL (header x-goog-api-key).
- _query_provider: excepción sanitizada antes de logger.warning.
- _query_openrouter: excepción sanitizada en sus dos except internos.
"""

import logging
import pytest
from unittest.mock import patch, MagicMock

from modules.auditors.llm_mention_checker import LLMMentionChecker

SYNTHETIC_GEMINI_KEY = "AIzaSyFAKE_TEST_12345678"
SYNTHETIC_OPENROUTER_KEY = "sk-or-fake-testing-key-v1-abcdef1234567890"
SYNTHETIC_PERPLEXITY_KEY = "pplx-fake-testing-key-abcdef1234567890"


class TestSanitizeText:
    """_sanitize_text: reemplaza valores de keys por ***."""

    def test_replaces_gemini_key(self):
        checker = LLMMentionChecker(gemini_key=SYNTHETIC_GEMINI_KEY)
        result = checker._sanitize_text(f"Error with key {SYNTHETIC_GEMINI_KEY} in msg")
        assert SYNTHETIC_GEMINI_KEY not in result
        assert "***" in result

    def test_replaces_multiple_keys(self):
        checker = LLMMentionChecker(
            openrouter_key=SYNTHETIC_OPENROUTER_KEY,
            gemini_key=SYNTHETIC_GEMINI_KEY,
            perplexity_key=SYNTHETIC_PERPLEXITY_KEY,
        )
        text = f"{SYNTHETIC_OPENROUTER_KEY} {SYNTHETIC_GEMINI_KEY} {SYNTHETIC_PERPLEXITY_KEY}"
        result = checker._sanitize_text(text)
        assert SYNTHETIC_OPENROUTER_KEY not in result
        assert SYNTHETIC_GEMINI_KEY not in result
        assert SYNTHETIC_PERPLEXITY_KEY not in result

    def test_no_keys_is_noop(self):
        checker = LLMMentionChecker(gemini_key=SYNTHETIC_GEMINI_KEY)
        assert checker._sanitize_text("clean message") == "clean message"

    def test_none_keys_is_noop(self):
        checker = LLMMentionChecker()
        assert checker._sanitize_text(f"key={SYNTHETIC_GEMINI_KEY}") == f"key={SYNTHETIC_GEMINI_KEY}"


class TestSanitizeError:
    """_sanitize_error: redacta params key= de URLs."""

    def test_redacts_key_param(self):
        error = Exception(
            "403 Forbidden: https://example.com/api?key=AIzaSySECRET123&other=val"
        )
        result = LLMMentionChecker._sanitize_error(error)
        assert "AIzaSySECRET123" not in result
        assert "key=***" in result

    def test_preserves_other_params(self):
        error = Exception("Error: https://api.com/v1?key=SECRET&format=json")
        result = LLMMentionChecker._sanitize_error(error)
        assert "format=json" in result
        assert "SECRET" not in result

    def test_no_key_param_is_noop(self):
        error = Exception("Connection refused")
        assert LLMMentionChecker._sanitize_error(error) == "Connection refused"


class TestGeminiKeyNotInUrl:
    """AC-S1: Gemini key viaja en header, no en URL."""

    @patch('requests.post')
    def test_gemini_uses_header_not_url(self, mock_post):
        """La URL no contiene la key; el header x-goog-api-key sí."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "ok"}]}}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        checker = LLMMentionChecker(gemini_key=SYNTHETIC_GEMINI_KEY)
        checker._query_gemini("test")

        call_args = mock_post.call_args
        url = call_args[0][0] if call_args[0] else call_args[1].get("url", "")
        assert SYNTHETIC_GEMINI_KEY not in url
        assert "key=" not in url

        headers = call_args[1].get("headers", {})
        assert headers.get("x-goog-api-key") == SYNTHETIC_GEMINI_KEY


class TestGemini403NoKeyLeak:
    """AC-S1: error 403 con token sintético no filtra la key al log."""

    @patch('requests.post')
    def test_gemini_403_does_not_leak_key_in_log(self, mock_post, caplog):
        """Simula 403 con la key en la URL del error (defensa en profundidad)."""
        import requests as real_requests
        http_error = real_requests.HTTPError(
            f"403 Forbidden: https://generativelanguage.googleapis.com/v1beta/"
            f"models/gemini-2.0-flash:generateContent?key={SYNTHETIC_GEMINI_KEY}"
        )
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        checker = LLMMentionChecker(gemini_key=SYNTHETIC_GEMINI_KEY)

        with caplog.at_level(logging.WARNING, logger="modules.auditors.llm_mention_checker"):
            result = checker._query_provider("gemini", "test query")

        assert result is None
        for record in caplog.records:
            assert SYNTHETIC_GEMINI_KEY not in record.getMessage(), (
                f"Key leaked in log: {record.getMessage()}"
            )


class TestOpenRouterErrorNoKeyLeak:
    """AC-S1: error en OpenRouter no filtra la key al log."""

    @patch('requests.post')
    def test_openrouter_500_does_not_leak_key(self, mock_post, caplog):
        """El error del servidor incluye la key; _sanitize_text la redacta."""
        import requests as real_requests
        http_error = real_requests.HTTPError(
            f"500 Server Error — invalid api_key: {SYNTHETIC_OPENROUTER_KEY}"
        )
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        checker = LLMMentionChecker(openrouter_key=SYNTHETIC_OPENROUTER_KEY)

        with caplog.at_level(logging.WARNING, logger="modules.auditors.llm_mention_checker"):
            result = checker._query_provider("openrouter", "test query")

        assert result is None
        for record in caplog.records:
            assert SYNTHETIC_OPENROUTER_KEY not in record.getMessage()


class TestPerplexityErrorNoKeyLeak:
    """AC-S1: error en Perplexity no filtra la key al log."""

    @patch('requests.post')
    def test_perplexity_401_does_not_leak_key(self, mock_post, caplog):
        """El error del servidor incluye la key; _sanitize_text la redacta."""
        import requests as real_requests
        http_error = real_requests.HTTPError(
            f"401 Unauthorized — bad key: {SYNTHETIC_PERPLEXITY_KEY}"
        )
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        checker = LLMMentionChecker(perplexity_key=SYNTHETIC_PERPLEXITY_KEY)

        with caplog.at_level(logging.WARNING, logger="modules.auditors.llm_mention_checker"):
            result = checker._query_provider("perplexity", "test query")

        assert result is None
        for record in caplog.records:
            assert SYNTHETIC_PERPLEXITY_KEY not in record.getMessage()
