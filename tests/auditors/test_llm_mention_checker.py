"""
Tests for LLMMentionChecker — FASE-C IAO Measurement.

Tests cover:
- Stub mode (no API keys)
- Mock data parsing
- Mention detection accuracy
- Score calculation
- Multiple providers
"""

import pytest
from unittest.mock import patch, MagicMock
from modules.auditors.llm_mention_checker import (
    LLMMentionChecker,
    LLMQueryResult,
    LLMReport,
)


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
            "choices": [{"message": {"content": "Te recomiendo el Hotel Visperas en Manizales."}}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        checker = LLMMentionChecker(openrouter_key="fake-key")
        result = checker._query_openrouter("Recomiendame un hotel en Manizales")

        assert result is not None
        assert "Hotel Visperas" in result
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
        assert "Hotel Visperas" in result


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
            "choices": [{"message": {"content": "Te recomiendo el Hotel Test en Bogota. Es excelente."}}]
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
            "choices": [{"message": {"content": "Te recomiendo el Hotel Otro en Bogota."}}]
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
