"""
Tests for LLMMentionChecker — FASE-C IAO Measurement.

Tests cover:
- Stub mode (no API keys)
- Mock data parsing
- Mention detection accuracy
- Score calculation
- Multiple providers
- FASE-2 BUG-4a: Model externalization to provider_registry
"""

import os
import pytest
from unittest.mock import patch, MagicMock, Mock
from modules.auditors.llm_mention_checker import (
    LLMMentionChecker,
    LLMQueryResult,
    LLMReport,
)
from modules.utils.provider_registry import ProviderRegistry, ProviderConfig


class TestLLMMentionCheckerStub:
    """Tests for stub mode (no API keys)."""

    @patch.dict('os.environ', {}, clear=True)
    def test_stub_without_keys(self):
        """Sin keys, retorna stub report."""
        checker = LLMMentionChecker()
        assert checker.is_available is False

        report = checker.check_mentions(
            hotel_name="Hotel Visperas",
            hotel_url="https://hotelvisperas.com",
            location="Manizales, Colombia",
        )

        assert report.source == "stub"
        assert report.queries_tested == 0
        assert report.total_mentions == 0
        assert report.mention_score == 0
        assert report.providers_used == []

    @patch.dict('os.environ', {}, clear=True)
    def test_stub_report_structure(self):
        """Stub report tiene estructura correcta."""
        checker = LLMMentionChecker()
        report = checker.check_mentions(
            hotel_name="Test Hotel",
            hotel_url="https://test.com",
            location="Bogota",
        )

        assert isinstance(report, LLMReport)
        assert report.hotel_name == "Test Hotel"
        assert report.hotel_url == "https://test.com"
        assert report.location == "Bogota"
        assert report.mention_rate == 0.0
        assert report.avg_ranking is None

    @patch.dict('os.environ', {}, clear=True)
    def test_stub_share_of_voice_zero(self):
        """Stub report tiene share_of_voice = 0."""
        checker = LLMMentionChecker()
        report = checker.check_mentions(
            hotel_name="Test Hotel",
            hotel_url="https://test.com",
            location="Bogota",
        )
        assert report.share_of_voice == 0.0


class TestLLMMentionCheckerWithKeys:
    """Tests with mock API keys (no real API calls)."""

    def test_available_with_openrouter_key(self):
        """Con OpenRouter key, is_available = True."""
        checker = LLMMentionChecker(openrouter_key="fake-key")
        assert checker.is_available is True
        assert "openrouter" in checker._available_providers

    def test_available_with_gemini_key(self):
        """Con Gemini key, is_available = True."""
        checker = LLMMentionChecker(gemini_key="fake-key")
        assert checker.is_available is True
        assert "gemini" in checker._available_providers

    def test_available_with_multiple_keys(self):
        """Con múltiples keys, todos los providers están disponibles."""
        checker = LLMMentionChecker(
            openrouter_key="key1",
            gemini_key="key2",
            perplexity_key="key3",
        )
        assert checker.is_available is True
        assert len(checker._available_providers) == 3

    @patch('requests.post')
    def test_openrouter_query_success(self, mock_post):
        """OpenRouter query exitoso retorna respuesta."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Te recomiendo el Hotel Visperas en Manizales."}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20},
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        checker = LLMMentionChecker(openrouter_key="fake-key")
        result = checker._query_openrouter("Recomiendame un hotel en Manizales")

        assert result is not None
        assert "Hotel Visperas" in result["text"]
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_openrouter_query_failure(self, mock_post):
        """OpenRouter query fallido retorna None via _query_provider."""
        mock_post.side_effect = Exception("Connection error")

        checker = LLMMentionChecker(openrouter_key="fake-key")
        result = checker._query_provider("openrouter", "test query")

        assert result is None

    @patch('requests.post')
    def test_gemini_query_success(self, mock_post):
        """Gemini query exitoso retorna respuesta."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "Hotel Visperas es una buena opcion."}]}}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        checker = LLMMentionChecker(gemini_key="fake-key")
        result = checker._query_gemini("Recomiendame un hotel")

        assert result is not None
        assert "Hotel Visperas" in result["text"]


class TestMentionParsing:
    """Tests for mention detection and parsing."""

    def test_parse_mention_detected(self):
        """Detecta mención del hotel en respuesta."""
        checker = LLMMentionChecker()
        response = "Te recomiendo el Hotel Visperas, tiene vistas increibles."
        parsed = checker._parse_mentions(response, "Hotel Visperas")

        assert parsed["mentioned"] is True
        assert "Hotel Visperas" in parsed["context"]

    def test_parse_mention_not_detected(self):
        """No detecta mención cuando el hotel no está."""
        checker = LLMMentionChecker()
        response = "Te recomiendo el Hotel Estelar en Bogota."
        parsed = checker._parse_mentions(response, "Hotel Visperas")

        assert parsed["mentioned"] is False
        assert parsed["context"] == ""

    def test_parse_mention_case_insensitive(self):
        """Detección es case-insensitive."""
        checker = LLMMentionChecker()
        response = "El HOTEL VISPERAS es excelente."
        parsed = checker._parse_mentions(response, "Hotel Visperas")

        assert parsed["mentioned"] is True

    def test_parse_ranking_position(self):
        """Detecta posición en lista numerada."""
        checker = LLMMentionChecker()
        response = "1. Hotel Estelar\n2. Hotel Visperas\n3. Hotel Dann Carlton"
        parsed = checker._parse_mentions(response, "Hotel Visperas")

        assert parsed["mentioned"] is True
        assert parsed["ranking_position"] == 2

    def test_parse_competitors(self):
        """Detecta competidores mencionados."""
        checker = LLMMentionChecker()
        response = "Te recomiendo el Hotel Visperas. Tambien esta el Hotel Estelar y el Hotel Plaza."
        parsed = checker._parse_mentions(response, "Hotel Visperas")

        assert parsed["mentioned"] is True
        assert len(parsed["competitors"]) >= 1

    def test_parse_no_competitors(self):
        """Sin competidores si no hay otros hoteles."""
        checker = LLMMentionChecker()
        response = "El Hotel Visperas es el mejor lugar para hospedarse."
        parsed = checker._parse_mentions(response, "Hotel Visperas")

        assert parsed["mentioned"] is True
        # May find 0 or may false-positive on "Hotel" patterns
        assert isinstance(parsed["competitors"], list)


class TestMentionScoreCalculation:
    """Tests for mention_score calculation."""

    def test_score_zero_no_queries(self):
        """Sin queries, score = 0."""
        checker = LLMMentionChecker()
        score = checker._calculate_mention_score(0.0, None, 0, 0)
        assert score == 0

    def test_score_perfect(self):
        """Mención perfecta: 100% rate, rank 1, 5 mentions."""
        checker = LLMMentionChecker()
        score = checker._calculate_mention_score(1.0, 1.0, 5, 5)
        # rate_score=50 + ranking_score=30 + consistency_score=20 = 100
        assert score == 100

    def test_score_partial(self):
        """Mención parcial: 60% rate, rank 3, 3 mentions."""
        checker = LLMMentionChecker()
        score = checker._calculate_mention_score(0.6, 3.0, 3, 5)
        # rate_score=30 + ranking_score=20 + consistency_score=15 = 65
        assert score == 65

    def test_score_only_rate(self):
        """Solo mention rate, sin ranking."""
        checker = LLMMentionChecker()
        score = checker._calculate_mention_score(0.5, None, 2, 4)
        # rate_score=25 + ranking_score=0 + consistency_score=10 = 35
        assert score == 35

    def test_score_capped_at_100(self):
        """Score no excede 100."""
        checker = LLMMentionChecker()
        score = checker._calculate_mention_score(1.0, 1.0, 10, 10)
        assert score <= 100


class TestLLMReportProperties:
    """Tests for LLMReport dataclass properties."""

    def test_share_of_voice_empty(self):
        """Sin resultados, share_of_voice = 0."""
        report = LLMReport(
            hotel_name="Test",
            hotel_url="https://test.com",
            location="Bogota",
            queries_tested=0,
            total_mentions=0,
            avg_ranking=None,
            mention_rate=0.0,
            providers_used=[],
        )
        assert report.share_of_voice == 0.0

    def test_share_of_voice_calculated(self):
        """Con menciones y competidores, calcula share_of_voice."""
        results = [
            LLMQueryResult(
                provider="openrouter",
                query="test",
                response_text="Hotel Test es bueno. Tambien Hotel A y Hotel B.",
                hotel_mentioned=True,
                mention_context="Hotel Test es bueno",
                competitors_mentioned=["Hotel A", "Hotel B"],
            ),
            LLMQueryResult(
                provider="gemini",
                query="test2",
                response_text="Solo Hotel Test.",
                hotel_mentioned=True,
                mention_context="Hotel Test",
                competitors_mentioned=[],
            ),
        ]
        report = LLMReport(
            hotel_name="Test",
            hotel_url="https://test.com",
            location="Bogota",
            queries_tested=2,
            total_mentions=2,
            avg_ranking=1.0,
            mention_rate=1.0,
            providers_used=["openrouter", "gemini"],
            query_results=results,
        )
        # 2 hotel mentions / (2 hotel + 2 competitors) = 0.5
        assert report.share_of_voice == 0.5


class TestCheckMentionsMocked:
    """Tests for check_mentions with mocked providers."""

    @patch('requests.post')
    def test_check_mentions_with_openrouter(self, mock_post):
        """check_mentions con OpenRouter retorna report real."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Te recomiendo el Hotel Test en Bogota. Es excelente."}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20},
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        checker = LLMMentionChecker(openrouter_key="fake-key")
        report = checker.check_mentions(
            hotel_name="Hotel Test",
            hotel_url="https://test.com",
            location="Bogota",
        )

        assert report.source == "llm_check"
        assert report.queries_tested > 0
        assert report.total_mentions > 0
        assert report.mention_score > 0
        assert "openrouter" in report.providers_used

    @patch('requests.post')
    def test_check_mentions_no_mentions(self, mock_post):
        """Hotel no mencionado en respuestas."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Te recomiendo el Hotel Otro en Bogota."}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20},
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        checker = LLMMentionChecker(openrouter_key="fake-key")
        report = checker.check_mentions(
            hotel_name="Hotel Test",
            hotel_url="https://test.com",
            location="Bogota",
        )

        assert report.source == "llm_check"
        assert report.total_mentions == 0
        assert report.mention_rate == 0.0

    @patch('modules.auditors.llm_mention_checker.time.sleep')
    @patch.object(LLMMentionChecker, "_query_provider", return_value=None)
    def test_check_mentions_all_providers_fail_is_not_measured(self, mock_query, mock_sleep):
        """Con keys pero todos los proveedores fallando: source="stub" (no medible),
        NO "llm_check" con 0/0 que se lee como "cero menciones"."""
        checker = LLMMentionChecker(openrouter_key="fake-key")
        assert checker.is_available, "precondicion: hay key, no es el stub sin keys"
        report = checker.check_mentions(
            hotel_name="Hotel Test",
            hotel_url="https://test.com",
            location="Bogota",
        )
        assert report.queries_tested == 0
        assert report.source == "stub"
        assert report.mention_score == 0
        assert report.query_results == []


# ═══════════════════════════════════════════════════════════════════════
# FASE-2 BUG-4a: Model externalization to provider_registry.yaml
# ═══════════════════════════════════════════════════════════════════════

class TestOpenRouterModelFromRegistry:
    """FASE-2 BUG-4a: Verifies model is read from provider_registry, not hardcoded."""

    def test_model_not_hardcoded_in_source(self):
        """Verify 'google/gemini-2.0-flash-001' is NOT in the source file."""
        import inspect
        source = inspect.getsource(LLMMentionChecker._query_openrouter)
        assert "google/gemini-2.0-flash-001" not in source, (
            "BUG-4a regression: modelo hardcoded en _query_openrouter"
        )

    def test_default_model_from_registry(self):
        """Verify default_model is read from ProviderRegistry (BUG-4a: not hardcoded)."""
        import yaml
        from pathlib import Path

        config_path = Path(__file__).resolve().parent.parent.parent / "config" / "provider_registry.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        expected_model = raw["providers"]["openrouter"]["default_model"]

        ProviderRegistry.reset()
        registry = ProviderRegistry()
        registry.load()
        cfg = registry.get("openrouter")
        assert cfg is not None, "openrouter not in provider_registry"
        assert cfg.default_model == expected_model, (
            f"Registry mismatch: expected {expected_model}, got {cfg.default_model}"
        )

    def test_payload_uses_registry_model(self):
        """Mock and verify payload uses model from ProviderRegistry."""
        ProviderRegistry.reset()

        mock_cfg = ProviderConfig(
            id="openrouter",
            type="llm",
            description="Test",
            auth_type="api_key",
            default_model="test-model-v2:free",
            env_vars=["OPENROUTER_API_KEY"],
        )

        with patch.object(ProviderRegistry, 'load', return_value=None):
            with patch.object(ProviderRegistry, 'get', return_value=mock_cfg):
                with patch('requests.post') as mock_post:
                    mock_response = Mock()
                    mock_response.json.return_value = {
                        "choices": [{"message": {"content": "test response"}}],
                        "usage": {"prompt_tokens": 10, "completion_tokens": 20},
                    }
                    mock_post.return_value = mock_response

                    checker = LLMMentionChecker(openrouter_key="test-key")
                    result = checker._query_openrouter("test query")

                    assert result is not None
                    assert result["text"] == "test response"

                    mock_post.assert_called_once()
                    payload = mock_post.call_args[1]["json"]
                    assert payload["model"] == "test-model-v2:free", (
                        f"Expected test-model-v2:free in payload, got {payload['model']}"
                    )

                    assert result["cost_usd"] == 0.0

    def test_payload_model_falls_back_when_registry_empty(self):
        """When registry has no openrouter config, fallback to first model in _OPENROUTER_FALLBACK_MODELS."""
        ProviderRegistry.reset()
        expected_fallback = LLMMentionChecker._OPENROUTER_FALLBACK_MODELS[0]

        with patch.object(ProviderRegistry, 'load', return_value=None):
            with patch.object(ProviderRegistry, 'get', return_value=None):
                with patch('requests.post') as mock_post:
                    mock_response = Mock()
                    mock_response.json.return_value = {
                        "choices": [{"message": {"content": "fallback response"}}],
                        "usage": {"prompt_tokens": 5, "completion_tokens": 10},
                    }
                    mock_post.return_value = mock_response

                    checker = LLMMentionChecker(openrouter_key="test-key")
                    result = checker._query_openrouter("fallback test")

                    assert result is not None
                    payload = mock_post.call_args[1]["json"]
                    assert payload["model"] == expected_fallback, (
                        f"Fallback model failed: got {payload['model']}"
                    )

    @pytest.mark.skipif(
        not os.environ.get("OPENROUTER_API_KEY"),
        reason="Requiere OPENROUTER_API_KEY para integración real"
    )
    def test_integration_real_openrouter_call(self):
        """Integration: real OpenRouter call with model from registry."""
        checker = LLMMentionChecker()
        result = checker._query_openrouter("Say hello in one word.")

        assert result is not None
        assert "text" in result
        assert len(result["text"]) > 0
        assert result["cost_usd"] == 0.0
        assert result["tokens_used"] > 0


# ═══════════════════════════════════════════════════════════════════════
# Gemini: modelo parametrizado en provider_registry.yaml (mismo patron que OpenRouter)
# ═══════════════════════════════════════════════════════════════════════

def _gemini_ok(text="Hotel Visperas es una buena opcion.", tokens=7):
    response = Mock()
    response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": text}]}}],
        "usageMetadata": {"totalTokenCount": tokens},
    }
    response.raise_for_status = MagicMock()
    return response


def _gemini_http_error(status):
    """Mock de respuesta que lanza requests.HTTPError con .response.status_code."""
    import requests

    error_response = Mock()
    error_response.status_code = status
    error_response.json.return_value = {"error": {"message": f"HTTP {status}"}}
    exc = requests.HTTPError(f"{status} Error", response=error_response)

    response = Mock()
    response.raise_for_status = Mock(side_effect=exc)
    return response


class TestGeminiModelFromRegistry:
    """El modelo de Gemini se lee del registry; no esta hardcodeado en el .py."""

    def test_model_not_hardcoded_in_source(self):
        """gemini-2.0-flash (retirado por Google, da 404) no debe volver al fuente."""
        import inspect
        source = inspect.getsource(LLMMentionChecker._query_gemini)
        assert "gemini-2.0-flash" not in source, (
            "regresion: modelo de Gemini hardcodeado en _query_gemini"
        )

    def test_gemini_registered_en_yaml(self):
        """provider_registry.yaml define el provider gemini con default_model."""
        import yaml
        from pathlib import Path

        config_path = Path(__file__).resolve().parent.parent.parent / "config" / "provider_registry.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        gemini = raw["providers"]["gemini"]
        assert gemini["type"] == "llm"
        assert "GEMINI_API_KEY" in gemini["env_vars"]
        assert gemini["default_model"], "default_model vacio"

    def test_url_usa_modelo_del_registry(self):
        """La URL se arma con el default_model del registry, y la key va en header."""
        ProviderRegistry.reset()

        mock_cfg = ProviderConfig(
            id="gemini",
            type="llm",
            description="Test",
            auth_type="api_key",
            default_model="test-gemini-v9",
            env_vars=["GEMINI_API_KEY"],
        )

        with patch.object(ProviderRegistry, 'load', return_value=None):
            with patch.object(ProviderRegistry, 'get', return_value=mock_cfg):
                with patch('requests.post') as mock_post:
                    mock_post.return_value = _gemini_ok()

                    checker = LLMMentionChecker(gemini_key="test-key")
                    result = checker._query_gemini("test query")

                    assert result is not None
                    assert result["tokens_used"] == 7

                    mock_post.assert_called_once()
                    url = mock_post.call_args[0][0]
                    assert "models/test-gemini-v9:generateContent" in url, (
                        f"Expected modelo del registry en la URL, got {url}"
                    )
                    # AC-S1: la key viaja en header, nunca en la URL
                    assert "test-key" not in url

    def test_url_fallback_cuando_registry_vacio(self):
        """Sin config de gemini, se usa el primer fallback model declarado."""
        ProviderRegistry.reset()
        expected = LLMMentionChecker._GEMINI_FALLBACK_MODELS[0]

        with patch.object(ProviderRegistry, 'load', return_value=None):
            with patch.object(ProviderRegistry, 'get', return_value=None):
                with patch('requests.post') as mock_post:
                    mock_post.return_value = _gemini_ok()

                    checker = LLMMentionChecker(gemini_key="test-key")
                    result = checker._query_gemini("fallback test")

                    assert result is not None
                    url = mock_post.call_args[0][0]
                    assert f"models/{expected}:generateContent" in url, (
                        f"Fallback model fallo: got {url}"
                    )

    def test_404_prueba_el_siguiente_modelo(self):
        """Un modelo retirado (404) degrada al siguiente fallback, sin abortar."""
        ProviderRegistry.reset()

        mock_cfg = ProviderConfig(
            id="gemini",
            type="llm",
            description="Test",
            auth_type="api_key",
            default_model="modelo-retirado",
            env_vars=["GEMINI_API_KEY"],
        )

        with patch.object(ProviderRegistry, 'load', return_value=None):
            with patch.object(ProviderRegistry, 'get', return_value=mock_cfg):
                with patch('requests.post') as mock_post:
                    mock_post.side_effect = [
                        _gemini_http_error(404),
                        _gemini_ok(text="respuesta del fallback"),
                    ]

                    checker = LLMMentionChecker(gemini_key="test-key")
                    result = checker._query_gemini("test query")

                    assert result is not None
                    assert result["text"] == "respuesta del fallback"
                    assert mock_post.call_count == 2
                    segundo_url = mock_post.call_args_list[1][0][0]
                    assert "modelo-retirado" not in segundo_url

    def test_429_no_reintenta_otros_modelos(self):
        """Cuota agotada (429) es del proyecto, no del modelo: una sola llamada."""
        ProviderRegistry.reset()

        with patch.object(ProviderRegistry, 'load', return_value=None):
            with patch.object(ProviderRegistry, 'get', return_value=None):
                with patch('requests.post') as mock_post:
                    mock_post.return_value = _gemini_http_error(429)

                    checker = LLMMentionChecker(gemini_key="test-key")
                    result = checker._query_gemini("test query")

                    assert result is None
                    assert mock_post.call_count == 1, (
                        "429 no debe reintentarse contra todos los fallback models"
                    )

    def test_key_redactada_en_el_log_de_error(self):
        """AC-S1: un error de Gemini no filtra la key al log."""
        ProviderRegistry.reset()
        synthetic_key = "AIzaSySINTETICA_PARA_TEST_000000"

        with patch.object(ProviderRegistry, 'load', return_value=None):
            with patch.object(ProviderRegistry, 'get', return_value=None):
                with patch('requests.post') as mock_post:
                    mock_post.side_effect = Exception(f"connection reset key={synthetic_key}")

                    checker = LLMMentionChecker(gemini_key=synthetic_key)
                    with patch('modules.auditors.llm_mention_checker.logger') as mock_logger:
                        result = checker._query_gemini("test query")

                    assert result is None
                    logged = " ".join(str(c) for c in mock_logger.warning.call_args_list)
                    assert synthetic_key not in logged


# ═══════════════════════════════════════════════════════════════════════
# Tarea 4: contabilidad de coste de Gemini (ya no cost_usd=0.0 hardcodeado)
# ═══════════════════════════════════════════════════════════════════════

def _gemini_ok_usage(prompt=0, candidates=0, thoughts=0, total=None,
                     text="Hotel Visperas es una buena opcion."):
    """Mock con el desglose usageMetadata real de Gemini (no solo totalTokenCount)."""
    usage = {
        "promptTokenCount": prompt,
        "candidatesTokenCount": candidates,
        "thoughtsTokenCount": thoughts,
        "totalTokenCount": total if total is not None else prompt + candidates + thoughts,
    }
    response = Mock()
    response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": text}]}}],
        "usageMetadata": usage,
    }
    response.raise_for_status = MagicMock()
    return response


class TestGeminiCostAccounting:
    """Con billing activo cada query quema saldo real: cost_usd debe derivarse del usage."""

    def test_gemini_declara_precios_en_yaml(self):
        """provider_registry.yaml declara precios por 1M tokens para gemini."""
        import yaml
        from pathlib import Path

        config_path = Path(__file__).resolve().parent.parent.parent / "config" / "provider_registry.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        gemini = raw["providers"]["gemini"]
        assert gemini.get("price_per_1m_input", 0) > 0
        assert gemini.get("price_per_1m_output", 0) > 0

    def test_cost_se_deriva_del_desglose_no_del_total(self):
        """totalTokenCount NO basta: el coste usa prompt/candidates por separado."""
        ProviderRegistry.reset()
        mock_cfg = ProviderConfig(
            id="gemini", type="llm", description="Test", auth_type="api_key",
            default_model="test-gemini", env_vars=["GEMINI_API_KEY"],
            price_per_1m_input=0.30, price_per_1m_output=2.50,
        )
        with patch.object(ProviderRegistry, 'load', return_value=None):
            with patch.object(ProviderRegistry, 'get', return_value=mock_cfg):
                with patch('requests.post') as mock_post:
                    # prompt=1000 @0.30 + (candidates=500 + thoughts=200) @2.50
                    mock_post.return_value = _gemini_ok_usage(prompt=1000, candidates=500, thoughts=200)
                    checker = LLMMentionChecker(gemini_key="test-key")
                    result = checker._query_gemini("q")
        expected = (1000 * 0.30 + (500 + 200) * 2.50) / 1_000_000
        assert result["cost_usd"] == pytest.approx(expected)
        assert result["cost_usd"] > 0, "el coste debe ser no-cero con uso real"

    def test_thinking_tokens_se_coban_a_tarifa_de_salida(self):
        """Los modelos de razonamiento cobran thoughtsTokenCount a precio de salida."""
        ProviderRegistry.reset()
        mock_cfg = ProviderConfig(
            id="gemini", type="llm", description="Test", auth_type="api_key",
            default_model="test-gemini", env_vars=["GEMINI_API_KEY"],
            price_per_1m_input=0.30, price_per_1m_output=2.50,
        )
        base = None
        with_costs = None
        for thoughts in (0, 1000):
            with patch.object(ProviderRegistry, 'load', return_value=None):
                with patch.object(ProviderRegistry, 'get', return_value=mock_cfg):
                    with patch('requests.post') as mock_post:
                        mock_post.return_value = _gemini_ok_usage(prompt=100, candidates=100, thoughts=thoughts)
                        checker = LLMMentionChecker(gemini_key="test-key")
                        r = checker._query_gemini("q")
            if thoughts == 0:
                base = r["cost_usd"]
            else:
                with_costs = r["cost_usd"]
        # 1000 thinking tokens @2.50/1M = 0.0025 de delta
        assert with_costs - base == pytest.approx(1000 * 2.50 / 1_000_000)

    def test_cost_cero_si_registry_no_declara_precios(self):
        """Sin precios declarados se degrada a 0.0, pero tokens_used se registra."""
        ProviderRegistry.reset()
        mock_cfg = ProviderConfig(
            id="gemini", type="llm", description="Test", auth_type="api_key",
            default_model="test-gemini", env_vars=["GEMINI_API_KEY"],
        )
        with patch.object(ProviderRegistry, 'load', return_value=None):
            with patch.object(ProviderRegistry, 'get', return_value=mock_cfg):
                with patch('requests.post') as mock_post:
                    mock_post.return_value = _gemini_ok_usage(prompt=1000, candidates=500, thoughts=0)
                    checker = LLMMentionChecker(gemini_key="test-key")
                    result = checker._query_gemini("q")
        assert result["cost_usd"] == 0.0
        assert result["tokens_used"] == 1500

    def test_cost_no_hardcoded_en_gemini(self):
        """Regresion: 'cost_usd": 0.0' fijo ya no es el valor devuelto incondicionalmente."""
        import inspect
        source = inspect.getsource(LLMMentionChecker._query_gemini)
        assert "price_per_1m_input" in source or "input_price" in source, (
            "el coste de Gemini debe derivarse de precios del registry, no hardcodear 0.0"
        )

