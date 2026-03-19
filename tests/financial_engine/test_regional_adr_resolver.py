"""
Test module for regional_adr_resolver.py

Comprehensive tests for the RegionalADRResolver class and RegionalADRResult dataclass,
covering ADR resolution based on region and hotel segment, confidence level determination,
and segment ADR table generation.
"""

import pytest
import json
import tempfile
from pathlib import Path
from modules.financial_engine.regional_adr_resolver import (
    RegionalADRResult,
    RegionalADRResolver,
    resolve_regional_adr,
)


class TestRegionalADRResult:
    """Test cases for RegionalADRResult dataclass."""

    def test_regional_adr_result_creation(self):
        """Test RegionalADRResult creation with all required fields."""
        result = RegionalADRResult(
            adr_cop=250000.0,
            region="coffee_axis",
            segment="boutique",
            confidence="VERIFIED",
            source="plan_maestro_v2.5",
        )

        assert result.adr_cop == 250000.0
        assert result.region == "coffee_axis"
        assert result.segment == "boutique"
        assert result.confidence == "VERIFIED"
        assert result.source == "plan_maestro_v2.5"
        assert result.is_default is False
        assert result.metadata is None

    def test_regional_adr_result_with_optional_fields(self):
        """Test RegionalADRResult with optional fields."""
        metadata = {"rooms": 20, "user_provided_adr": 260000.0}
        result = RegionalADRResult(
            adr_cop=250000.0,
            region="coffee_axis",
            segment="boutique",
            confidence="VERIFIED",
            source="plan_maestro_v2.5",
            is_default=False,
            metadata=metadata,
        )

        assert result.is_default is False
        assert result.metadata == metadata


class TestRegionalADRResolverInitialization:
    """Test cases for RegionalADRResolver initialization."""

    def test_resolver_initialization_with_default_path(self):
        """Test RegionalADRResolver initializes with default path."""
        resolver = RegionalADRResolver()

        assert resolver.plan_maestro_path is not None
        assert hasattr(resolver, '_data')

    def test_resolver_initialization_with_custom_path(self):
        """Test RegionalADRResolver initializes with custom path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"regiones": {}}, f)
            temp_path = f.name

        resolver = RegionalADRResolver(temp_path)

        assert resolver.plan_maestro_path == temp_path

        Path(temp_path).unlink()

    def test_resolver_handles_missing_file(self):
        """Test RegionalADRResolver handles missing file gracefully."""
        resolver = RegionalADRResolver("/nonexistent/path.json")

        assert resolver._data == {"regiones": {}}

    def test_resolver_handles_invalid_json(self):
        """Test RegionalADRResolver handles invalid JSON gracefully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json")
            temp_path = f.name

        resolver = RegionalADRResolver(temp_path)

        assert resolver._data == {"regiones": {}}

        Path(temp_path).unlink()


class TestSegmentDetermination:
    """Test cases for segment determination logic."""

    def test_boutique_segment_10_rooms(self):
        """Test 10 rooms returns boutique segment."""
        resolver = RegionalADRResolver()
        segment = resolver._determine_segment(10)
        assert segment == RegionalADRResolver.SEGMENT_BOUTIQUE

    def test_boutique_segment_25_rooms_boundary(self):
        """Test 25 rooms (boundary) returns boutique segment."""
        resolver = RegionalADRResolver()
        segment = resolver._determine_segment(25)
        assert segment == RegionalADRResolver.SEGMENT_BOUTIQUE

    def test_standard_segment_26_rooms_boundary(self):
        """Test 26 rooms (boundary) returns standard segment."""
        resolver = RegionalADRResolver()
        segment = resolver._determine_segment(26)
        assert segment == RegionalADRResolver.SEGMENT_STANDARD

    def test_standard_segment_45_rooms(self):
        """Test 45 rooms returns standard segment."""
        resolver = RegionalADRResolver()
        segment = resolver._determine_segment(45)
        assert segment == RegionalADRResolver.SEGMENT_STANDARD

    def test_standard_segment_60_rooms_boundary(self):
        """Test 60 rooms (boundary) returns standard segment."""
        resolver = RegionalADRResolver()
        segment = resolver._determine_segment(60)
        assert segment == RegionalADRResolver.SEGMENT_STANDARD

    def test_large_segment_61_rooms_boundary(self):
        """Test 61 rooms (boundary) returns large segment."""
        resolver = RegionalADRResolver()
        segment = resolver._determine_segment(61)
        assert segment == RegionalADRResolver.SEGMENT_LARGE

    def test_large_segment_100_rooms(self):
        """Test 100 rooms returns large segment."""
        resolver = RegionalADRResolver()
        segment = resolver._determine_segment(100)
        assert segment == RegionalADRResolver.SEGMENT_LARGE


@pytest.fixture
def sample_plan_maestro_data():
    """Provide sample plan maestro data with multiple regions."""
    return {
        "regiones": {
            "coffee_axis": {
                "name": "Eje Cafetero",
                "adr_cop": 280000.0,
                "segments": {
                    "boutique_10_25": {"adr_cop": 250000.0},
                    "standard_26_60": {"adr_cop": 300000.0},
                }
            },
            "bogota": {
                "name": "Bogotá",
                "adr_cop": 350000.0,
                "segments": {
                    "boutique_10_25": {"adr_cop": 320000.0},
                    "standard_26_60": {"adr_cop": 380000.0},
                }
            },
            "medellin": {
                "name": "Medellín",
                "adr_cop": 320000.0,
                "segments": {
                    "boutique_10_25": {"adr_cop": 290000.0},
                    "standard_26_60": {"adr_cop": 350000.0},
                }
            },
            "default": {
                "name": "Default",
                "adr_cop": 300000.0,
                "segments": {
                    "boutique_10_25": {"adr_cop": 280000.0},
                    "standard_26_60": {"adr_cop": 320000.0},
                }
            }
        }
    }


@pytest.fixture
def resolver_with_data(sample_plan_maestro_data):
    """Provide a RegionalADRResolver with sample data."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_plan_maestro_data, f)
        temp_path = f.name

    resolver = RegionalADRResolver(temp_path)
    yield resolver

    Path(temp_path).unlink()


class TestResolveBoutiqueSegment:
    """Test resolve for boutique segment (10-25 rooms) in each region."""

    def test_boutique_coffee_axis(self, resolver_with_data):
        """Test boutique segment in coffee axis region."""
        result = resolver_with_data.resolve("coffee_axis", 20)

        assert result.adr_cop == 250000.0
        assert result.region == "coffee_axis"
        assert result.segment == "boutique"
        assert result.source == "plan_maestro_v2.5"

    def test_boutique_bogota(self, resolver_with_data):
        """Test boutique segment in bogota region."""
        result = resolver_with_data.resolve("bogota", 15)

        assert result.adr_cop == 320000.0
        assert result.region == "bogota"
        assert result.segment == "boutique"

    def test_boutique_medellin(self, resolver_with_data):
        """Test boutique segment in medellin region."""
        result = resolver_with_data.resolve("medellin", 22)

        assert result.adr_cop == 290000.0
        assert result.region == "medellin"
        assert result.segment == "boutique"

    def test_boutique_boundary_10_rooms(self, resolver_with_data):
        """Test boutique segment with minimum 10 rooms."""
        result = resolver_with_data.resolve("coffee_axis", 10)

        assert result.segment == "boutique"
        assert result.adr_cop == 250000.0

    def test_boutique_boundary_25_rooms(self, resolver_with_data):
        """Test boutique segment with maximum 25 rooms."""
        result = resolver_with_data.resolve("coffee_axis", 25)

        assert result.segment == "boutique"
        assert result.adr_cop == 250000.0


class TestResolveStandardSegment:
    """Test resolve for standard segment (26-60 rooms) in each region."""

    def test_standard_coffee_axis(self, resolver_with_data):
        """Test standard segment in coffee axis region."""
        result = resolver_with_data.resolve("coffee_axis", 45)

        assert result.adr_cop == 300000.0
        assert result.region == "coffee_axis"
        assert result.segment == "standard"

    def test_standard_bogota(self, resolver_with_data):
        """Test standard segment in bogota region."""
        result = resolver_with_data.resolve("bogota", 50)

        assert result.adr_cop == 380000.0
        assert result.region == "bogota"
        assert result.segment == "standard"

    def test_standard_medellin(self, resolver_with_data):
        """Test standard segment in medellin region."""
        result = resolver_with_data.resolve("medellin", 35)

        assert result.adr_cop == 350000.0
        assert result.region == "medellin"
        assert result.segment == "standard"

    def test_standard_boundary_26_rooms(self, resolver_with_data):
        """Test standard segment with minimum 26 rooms."""
        result = resolver_with_data.resolve("coffee_axis", 26)

        assert result.segment == "standard"
        assert result.adr_cop == 300000.0

    def test_standard_boundary_60_rooms(self, resolver_with_data):
        """Test standard segment with maximum 60 rooms."""
        result = resolver_with_data.resolve("coffee_axis", 60)

        assert result.segment == "standard"
        assert result.adr_cop == 300000.0


class TestResolveLargeHotels:
    """Test resolve for large hotels (60+ rooms)."""

    def test_large_hotel_61_rooms(self, resolver_with_data):
        """Test large segment with 61 rooms (boundary)."""
        result = resolver_with_data.resolve("coffee_axis", 61)

        assert result.segment == "large"
        assert result.adr_cop == 280000.0  # Falls back to region adr_cop
        assert result.region == "coffee_axis"

    def test_large_hotel_100_rooms(self, resolver_with_data):
        """Test large segment with 100 rooms."""
        result = resolver_with_data.resolve("bogota", 100)

        assert result.segment == "large"
        assert result.adr_cop == 350000.0  # Falls back to region adr_cop
        assert result.region == "bogota"

    def test_large_hotel_200_rooms(self, resolver_with_data):
        """Test large segment with 200 rooms."""
        result = resolver_with_data.resolve("medellin", 200)

        assert result.segment == "large"
        assert result.adr_cop == 320000.0  # Falls back to region adr_cop
        assert result.region == "medellin"


class TestUnknownRegion:
    """Test with unknown region (should use default)."""

    def test_unknown_region_uses_default(self, resolver_with_data):
        """Test unknown region falls back to default."""
        result = resolver_with_data.resolve("unknown_region", 30)

        assert result.is_default is True
        assert result.region == "default"
        assert result.adr_cop == 320000.0  # default standard segment

    def test_unknown_region_boutique(self, resolver_with_data):
        """Test unknown region with boutique size."""
        result = resolver_with_data.resolve("unknown_region", 20)

        assert result.is_default is True
        assert result.region == "default"
        assert result.segment == "boutique"
        assert result.adr_cop == 280000.0  # default boutique segment

    def test_unknown_region_large(self, resolver_with_data):
        """Test unknown region with large size."""
        result = resolver_with_data.resolve("unknown_region", 80)

        assert result.is_default is True
        assert result.region == "default"
        assert result.segment == "large"
        assert result.adr_cop == 300000.0  # default region adr_cop

    def test_empty_data_returns_default_adr(self):
        """Test with empty data returns default ADR of 300000."""
        resolver = RegionalADRResolver()
        result = resolver.resolve("any_region", 30)

        assert result.adr_cop == 300000.0


class TestConfidenceLevels:
    """Test confidence level determination."""

    @pytest.fixture
    def coffee_resolver(self, sample_plan_maestro_data):
        """Provide resolver with coffee axis data.

        Note: For 30 rooms (standard segment), benchmark ADR is 300000.
        For 20 rooms (boutique segment), benchmark ADR is 250000.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_plan_maestro_data, f)
            temp_path = f.name

        resolver = RegionalADRResolver(temp_path)
        yield resolver

        Path(temp_path).unlink()

    def test_verified_within_20_percent(self, coffee_resolver):
        """Test VERIFIED when user ADR within 20% of benchmark (standard segment)."""
        # For 30 rooms, benchmark is 300000 (standard segment)
        # 20% of 300000 = 60000, range: 240000 to 360000
        result = coffee_resolver.resolve("coffee_axis", 30, user_provided_adr=320000.0)

        assert result.confidence == "VERIFIED"
        expected_deviation = abs(320000 - 300000) / 300000 * 100  # ~6.67%
        assert result.metadata["deviation_pct"] == pytest.approx(expected_deviation, rel=0.01)

    def test_verified_at_exact_boundary(self, coffee_resolver):
        """Test at exact 20% boundary returns ESTIMATED (not < 20)."""
        # For 30 rooms, benchmark is 300000
        # 20% of 300000 = 60000, so 360000 is exactly 20% above
        result = coffee_resolver.resolve("coffee_axis", 30, user_provided_adr=360000.0)

        # 20% is not < 20, so should be ESTIMATED
        assert result.confidence == "ESTIMATED"

    def test_verified_below_benchmark(self, coffee_resolver):
        """Test VERIFIED when user ADR below benchmark but within 20%."""
        result = coffee_resolver.resolve("coffee_axis", 30, user_provided_adr=260000.0)

        deviation = abs(260000 - 300000) / 300000 * 100  # ~13.3%
        assert deviation < 20
        assert result.confidence == "VERIFIED"

    def test_verified_boutique_segment(self, coffee_resolver):
        """Test VERIFIED for boutique segment (different benchmark)."""
        # For 20 rooms, benchmark is 250000 (boutique segment)
        result = coffee_resolver.resolve("coffee_axis", 20, user_provided_adr=270000.0)

        deviation = abs(270000 - 250000) / 250000 * 100  # 8%
        assert deviation < 20
        assert result.confidence == "VERIFIED"

    def test_estimated_within_20_40_percent(self, coffee_resolver):
        """Test ESTIMATED when user ADR within 20-40% of benchmark."""
        # For 30 rooms, benchmark is 300000
        # 20-40% range: 360000 to 420000
        result = coffee_resolver.resolve("coffee_axis", 30, user_provided_adr=380000.0)

        deviation = abs(380000 - 300000) / 300000 * 100  # ~26.7%
        assert 20 <= deviation < 40
        assert result.confidence == "ESTIMATED"

    def test_estimated_at_40_percent_boundary(self, coffee_resolver):
        """Test at exact 40% boundary returns CONFLICT (not < 40)."""
        # For 30 rooms, benchmark is 300000
        # 40% of 300000 = 120000, so 420000 is exactly 40% above
        result = coffee_resolver.resolve("coffee_axis", 30, user_provided_adr=420000.0)

        # 40% is not < 40, so should be CONFLICT
        assert result.confidence == "CONFLICT"

    def test_conflict_above_40_percent(self, coffee_resolver):
        """Test CONFLICT when user ADR >40% different from benchmark."""
        result = coffee_resolver.resolve("coffee_axis", 30, user_provided_adr=500000.0)

        deviation = abs(500000 - 300000) / 300000 * 100  # ~66.7%
        assert deviation > 40
        assert result.confidence == "CONFLICT"

    def test_conflict_below_40_percent(self, coffee_resolver):
        """Test CONFLICT when user ADR >40% below benchmark."""
        result = coffee_resolver.resolve("coffee_axis", 30, user_provided_adr=150000.0)

        deviation = abs(150000 - 300000) / 300000 * 100  # 50%
        assert deviation > 40
        assert result.confidence == "CONFLICT"

    def test_estimated_no_user_adr(self, coffee_resolver):
        """Test ESTIMATED when no user ADR provided."""
        result = coffee_resolver.resolve("coffee_axis", 30, user_provided_adr=None)

        assert result.confidence == "ESTIMATED"
        assert result.metadata["user_provided_adr"] is None
        assert result.metadata["deviation_pct"] is None

    def test_estimated_unknown_region(self, coffee_resolver):
        """Test ESTIMATED when region is unknown."""
        result = coffee_resolver.resolve("unknown_region", 30, user_provided_adr=300000.0)

        assert result.confidence == "ESTIMATED"
        assert result.is_default is True

    def test_metadata_includes_deviation(self, coffee_resolver):
        """Test metadata includes correct deviation percentage."""
        result = coffee_resolver.resolve("coffee_axis", 30, user_provided_adr=330000.0)

        expected_deviation = abs(330000 - 300000) / 300000 * 100  # 10%
        assert result.metadata["deviation_pct"] == pytest.approx(expected_deviation, rel=0.01)


class TestGetSegmentADRTable:
    """Test get_segment_adr_table returns correct structure."""

    def test_returns_dict_structure(self, resolver_with_data):
        """Test method returns dictionary with correct structure."""
        table = resolver_with_data.get_segment_adr_table()

        assert isinstance(table, dict)

    def test_contains_all_regions(self, resolver_with_data):
        """Test table contains all regions from data."""
        table = resolver_with_data.get_segment_adr_table()

        assert "coffee_axis" in table
        assert "bogota" in table
        assert "medellin" in table
        assert "default" in table

    def test_region_has_boutique_key(self, resolver_with_data):
        """Test each region entry has boutique key."""
        table = resolver_with_data.get_segment_adr_table()

        for region_data in table.values():
            assert "boutique" in region_data

    def test_region_has_standard_key(self, resolver_with_data):
        """Test each region entry has standard key."""
        table = resolver_with_data.get_segment_adr_table()

        for region_data in table.values():
            assert "standard" in region_data

    def test_region_has_average_key(self, resolver_with_data):
        """Test each region entry has average key."""
        table = resolver_with_data.get_segment_adr_table()

        for region_data in table.values():
            assert "average" in region_data

    def test_boutique_values_correct(self, resolver_with_data):
        """Test boutique values match segment data."""
        table = resolver_with_data.get_segment_adr_table()

        assert table["coffee_axis"]["boutique"] == 250000.0
        assert table["bogota"]["boutique"] == 320000.0
        assert table["medellin"]["boutique"] == 290000.0

    def test_standard_values_correct(self, resolver_with_data):
        """Test standard values match segment data."""
        table = resolver_with_data.get_segment_adr_table()

        assert table["coffee_axis"]["standard"] == 300000.0
        assert table["bogota"]["standard"] == 380000.0
        assert table["medellin"]["standard"] == 350000.0

    def test_average_values_correct(self, resolver_with_data):
        """Test average values match region adr_cop."""
        table = resolver_with_data.get_segment_adr_table()

        assert table["coffee_axis"]["average"] == 280000.0
        assert table["bogota"]["average"] == 350000.0
        assert table["medellin"]["average"] == 320000.0

    def test_empty_data_returns_empty_dict(self):
        """Test with empty data returns empty dict."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"regiones": {}}, f)
            temp_path = f.name

        resolver = RegionalADRResolver(temp_path)
        table = resolver.get_segment_adr_table()

        assert table == {}

        Path(temp_path).unlink()


class TestResolveRegionalADRFunction:
    """Test the convenience function resolve_regional_adr."""

    def test_function_returns_regional_adr_result(self, sample_plan_maestro_data):
        """Test function returns RegionalADRResult."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_plan_maestro_data, f)
            temp_path = f.name

        result = resolve_regional_adr("coffee_axis", 20, plan_maestro_path=temp_path)

        assert isinstance(result, RegionalADRResult)
        assert result.adr_cop == 250000.0
        assert result.segment == "boutique"

        Path(temp_path).unlink()

    def test_function_with_user_adr(self, sample_plan_maestro_data):
        """Test function with user provided ADR."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_plan_maestro_data, f)
            temp_path = f.name

        result = resolve_regional_adr("bogota", 50, user_provided_adr=370000.0, plan_maestro_path=temp_path)

        assert isinstance(result, RegionalADRResult)
        assert result.confidence == "VERIFIED"

        Path(temp_path).unlink()
