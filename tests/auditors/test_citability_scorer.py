"""Tests para CitabilityScorer.

Valida análisis de citabilidad de contenido HTML.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest

from modules.auditors.citability_scorer import (
    CitabilityScorer,
    CitabilityScore,
    ContentBlock,
)


@pytest.fixture
def scorer():
    """Fixture que proporciona una instancia de CitabilityScorer."""
    return CitabilityScorer()


@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return """
    <html>
    <body>
        <p>¿Cuáles son los servicios incluidos en la tarifa?</p>
        <p>Nuestra tarifa incluye desayuno buffet, acceso a la piscina y wifi gratuito.</p>
        <p>Este es un párrafo de prueba que contiene información sobre las instalaciones del hotel. 
        Cuenta con健身房, restaurante y servicio de habitaciones las 24 horas. 
        Los huéspedes pueden disfrutar de actividades recreativas y entretenimiento.</p>
        <p>Otro párrafo más corto.</p>
    </body>
    </html>
    """


class TestCitabilityScorer:
    """Tests for CitabilityScorer class."""

    def test_citability_scorer_basic(self, scorer, sample_html):
        """Test that score is within 0-100 range."""
        result = scorer.score_content(sample_html, "https://example.com")
        
        assert isinstance(result, CitabilityScore)
        assert 0 <= result.overall_score <= 100
        assert result.blocks_analyzed > 0
        assert isinstance(result.block_scores, list)

    def test_citability_scorer_recommendations(self, scorer, sample_html):
        """Test that recommendations are generated."""
        result = scorer.score_content(sample_html, "https://example.com")
        
        assert isinstance(result.recommendations, list)
        assert len(result.recommendations) > 0
        assert all(isinstance(r, str) for r in result.recommendations)

    def test_citability_scorer_optimal_range(self, scorer):
        """Test bonus for optimal word range (134-167 words)."""
        optimal_html = """
        <html>
        <body>
            <p>""" + " ".join(["palabra"] * 150) + """</p>
        </body>
        </html>
        """
        
        result = scorer.score_content(optimal_html, "https://example.com")
        
        assert result.blocks_analyzed == 1
        block_score = result.block_scores[0]["score"]
        assert block_score >= 70

    def test_content_block_creation(self):
        """Test ContentBlock dataclass creation."""
        block = ContentBlock(
            text="Sample text content",
            word_count=3,
            has_question=False,
            has_answer=False,
            is_self_contained=True,
            factual_density=0.5,
        )
        
        assert block.text == "Sample text content"
        assert block.word_count == 3
        assert block.is_self_contained is True

    def test_score_block_method(self, scorer):
        """Test _score_block calculates correctly."""
        block = ContentBlock(
            text="¿Qué servicios ofrece el hotel? El hotel ofrece piscina y restaurante.",
            word_count=140,
            has_question=True,
            has_answer=True,
            is_self_contained=True,
            factual_density=0.3,
        )
        
        score = scorer._score_block(block)
        
        assert 0 <= score <= 100
        assert score >= 50

    def test_extract_content_blocks(self, scorer, sample_html):
        """Test _extract_content_blocks extracts paragraphs."""
        blocks = scorer._extract_content_blocks(sample_html)
        
        assert len(blocks) > 0
        assert all(isinstance(b, ContentBlock) for b in blocks)

    def test_empty_html(self, scorer):
        """Test handling of empty HTML."""
        result = scorer.score_content("<html><body></body></html>", "https://example.com")
        
        assert result.overall_score == 0
        assert result.blocks_analyzed == 0

    def test_short_block_detection(self, scorer):
        """Test detection of short blocks under 100 words."""
        short_html = """
        <html>
        <body>
            <p>Este es un párrafo corto con algunas palabras.</p>
            <p>Otro párrafo también corto con contenido limitado.</p>
        </body>
        </html>
        """
        
        result = scorer.score_content(short_html, "https://example.com")
        
        assert any("under 100 words" in r for r in result.recommendations)
