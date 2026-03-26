"""
Tests for AEO KPIs data models.

Tests cover:
- AEOKPI dataclass
- VoiceReadinessScore dataclass
- AEOKPIs dataclass with composite score calculation
- Serialization to dict
"""
import pytest
from datetime import datetime
from data_models.aeo_kpis import (
    AEOKPI,
    AEOKPIs,
    DataSource,
    VoiceReadinessScore,
)


class TestDataSource:
    """Tests for DataSource enum."""

    @pytest.mark.parametrize("source,expected_value", [
        (DataSource.PROFOUND_API, "profound_api"),
        (DataSource.SEMRUSH_API, "semrush_api"),
        (DataSource.GOOGLE_SEARCH_CONSOLE, "google_search_console"),
        (DataSource.MOCK, "mock"),
    ])
    def test_source_values(self, source, expected_value):
        """Test that enum values are correct."""
        assert source.value == expected_value


class TestAEOKPI:
    """Tests for individual AEOKPI."""

    def test_creation_with_required_fields(self):
        """Test creating an AEOKPI with required fields."""
        kpi = AEOKPI(
            name="AI Visibility Score",
            value=75.5,
            unit="%",
            source=DataSource.MOCK,
        )
        assert kpi.name == "AI Visibility Score"
        assert kpi.value == 75.5
        assert kpi.unit == "%"
        assert kpi.source == DataSource.MOCK

    def test_to_dict(self):
        """Test serialization to dictionary."""
        kpi = AEOKPI(
            name="Share of Voice",
            value=25.0,
            unit="%",
            source=DataSource.PROFOUND_API,
        )
        result = kpi.to_dict()
        assert result["name"] == "Share of Voice"
        assert result["value"] == 25.0
        assert result["unit"] == "%"
        assert result["source"] == "profound_api"


class TestVoiceReadinessScore:
    """Tests for VoiceReadinessScore."""

    def test_creation_with_all_components(self):
        """Test creating a VoiceReadinessScore with all components."""
        vrs = VoiceReadinessScore(
            schema_quality=80.0,
            speakable_coverage=70.0,
            faq_tts_compliance=85.0,
            structured_data_score=75.0,
        )
        assert vrs.schema_quality == 80.0
        assert vrs.speakable_coverage == 70.0
        assert vrs.faq_tts_compliance == 85.0
        assert vrs.structured_data_score == 75.0

    def test_overall_calculation(self):
        """Test that overall score is calculated as weighted average."""
        vrs = VoiceReadinessScore(
            schema_quality=80.0,
            speakable_coverage=70.0,
            faq_tts_compliance=85.0,
            structured_data_score=75.0,
        )
        expected = (80.0 + 70.0 + 85.0 + 75.0) / 4
        assert vrs.overall == expected

    def test_to_dict(self):
        """Test serialization to dictionary."""
        vrs = VoiceReadinessScore(
            schema_quality=80.0,
            speakable_coverage=70.0,
            faq_tts_compliance=85.0,
            structured_data_score=75.0,
        )
        result = vrs.to_dict()
        assert result["schema_quality"] == 80.0
        assert result["speakable_coverage"] == 70.0
        assert result["faq_tts_compliance"] == 85.0
        assert result["structured_data_score"] == 75.0
        assert "overall" in result


class TestAEOKPIs:
    """Tests for the complete AEOKPIs framework."""

    def test_creation_minimal(self):
        """Test creating AEOKPIs with minimal fields."""
        kpis = AEOKPIs(
            hotel_name="Test Hotel",
            url="https://testhotel.com",
        )
        assert kpis.hotel_name == "Test Hotel"
        assert kpis.url == "https://testhotel.com"
        assert kpis.data_source == DataSource.MOCK
        assert kpis.version == "1.0.0"

    def test_creation_full(self):
        """Test creating AEOKPIs with all fields."""
        vrs = VoiceReadinessScore(
            schema_quality=80.0,
            speakable_coverage=70.0,
            faq_tts_compliance=85.0,
            structured_data_score=75.0,
        )
        kpis = AEOKPIs(
            hotel_name="Test Hotel",
            url="https://testhotel.com",
            ai_visibility_score=72.5,
            share_of_voice=28.0,
            citation_rate=65.0,
            voice_search_impressions=1500,
            voice_readiness=vrs,
            competitors_analyzed=5,
            competitor_avg_viscosity=55.0,
            data_source=DataSource.PROFOUND_API,
        )
        assert kpis.ai_visibility_score == 72.5
        assert kpis.share_of_voice == 28.0
        assert kpis.citation_rate == 65.0
        assert kpis.voice_readiness.overall == 77.5

    def test_composite_score_partial_data(self):
        """Test composite score calculation with partial data."""
        kpis = AEOKPIs(
            hotel_name="Test Hotel",
            url="https://testhotel.com",
            ai_visibility_score=80.0,
            share_of_voice=20.0,
            # citation_rate and voice_readiness not set
        )
        # Expected: 80*0.4 + 20*0.2 = 32 + 4 = 36
        assert kpis.calculate_composite_score() == 36.0

    def test_composite_score_full_data(self):
        """Test composite score calculation with all metrics."""
        vrs = VoiceReadinessScore(
            schema_quality=80.0,
            speakable_coverage=80.0,
            faq_tts_compliance=80.0,
            structured_data_score=80.0,
        )
        kpis = AEOKPIs(
            hotel_name="Test Hotel",
            url="https://testhotel.com",
            ai_visibility_score=80.0,
            share_of_voice=20.0,
            citation_rate=60.0,
            voice_readiness=vrs,
        )
        # AI Visibility: 80 * 0.4 = 32
        # SoV: 20 * 0.2 = 4
        # Citation: 60 * 0.2 = 12
        # Voice Readiness: 80 * 0.2 = 16
        # Total = 64
        assert kpis.calculate_composite_score() == 64.0

    def test_composite_score_no_data(self):
        """Test composite score returns -1 when no data available."""
        kpis = AEOKPIs(
            hotel_name="Test Hotel",
            url="https://testhotel.com",
        )
        assert kpis.calculate_composite_score() == -1.0

    def test_to_dict(self):
        """Test full serialization to dictionary."""
        vrs = VoiceReadinessScore(
            schema_quality=80.0,
            speakable_coverage=70.0,
            faq_tts_compliance=85.0,
            structured_data_score=75.0,
        )
        kpis = AEOKPIs(
            hotel_name="Test Hotel",
            url="https://testhotel.com",
            ai_visibility_score=72.5,
            share_of_voice=28.0,
            citation_rate=65.0,
            voice_readiness=vrs,
            data_source=DataSource.PROFOUND_API,
        )
        result = kpis.to_dict()
        assert result["hotel_name"] == "Test Hotel"
        assert result["url"] == "https://testhotel.com"
        assert result["ai_visibility_score"] == 72.5
        assert result["share_of_voice"] == 28.0
        assert result["citation_rate"] == 65.0
        assert result["voice_readiness"]["overall"] == 77.5
        assert result["data_source"] == "profound_api"
        assert "composite_score" in result
        assert "generated_at" in result


class TestAEOKPIsSerialization:
    """Tests for AEOKPIs JSON serialization."""

    def test_serialization_includes_all_fields(self):
        """Test that to_dict includes all relevant fields."""
        vrs = VoiceReadinessScore(
            schema_quality=75.0,
            speakable_coverage=65.0,
            faq_tts_compliance=80.0,
            structured_data_score=70.0,
        )
        kpis = AEOKPIs(
            hotel_name="Hotel Example",
            url="https://example.com",
            ai_visibility_score=70.0,
            share_of_voice=25.0,
            citation_rate=60.0,
            voice_search_impressions=1000,
            voice_readiness=vrs,
            competitors_analyzed=3,
            competitor_avg_viscosity=50.0,
            data_source=DataSource.MOCK,
        )
        result = kpis.to_dict()
        
        required_fields = [
            "hotel_name", "url", "ai_visibility_score", "share_of_voice",
            "citation_rate", "voice_search_impressions", "voice_readiness",
            "competitors_analyzed", "competitor_avg_viscosity", "data_source",
            "composite_score", "generated_at", "version"
        ]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"

    def test_generated_at_is_isoformat(self):
        """Test that generated_at is in ISO format."""
        kpis = AEOKPIs(
            hotel_name="Test Hotel",
            url="https://test.com",
        )
        result = kpis.to_dict()
        # Should not raise and should be parseable
        datetime.fromisoformat(result["generated_at"])
