"""
Cross-Validation module for IA Hoteles Agent.

Implements cross-validation between different data sources
(web scraping, user input, GBP API, benchmarks).
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from .confidence_taxonomy import DataPoint, DataSource, ConfidenceLevel


class CrossValidator:
    """
    Cross-validator that aggregates data from multiple sources
    and provides validated results with confidence scoring.
    """

    def __init__(self):
        """Initialize the cross-validator with empty data points storage."""
        self.data_points: Dict[str, DataPoint] = {}

    def add_scraped_data(self, field_name: str, value: Any, metadata: dict = None) -> None:
        """
        Add data from web scraping source.

        Args:
            field_name: Name of the field being validated
            value: The scraped value
            metadata: Optional metadata about the source
        """
        source = DataSource(
            source_type="web_scraping",
            value=value,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )

        if field_name not in self.data_points:
            self.data_points[field_name] = DataPoint(field_name)

        self.data_points[field_name].add_source(source)

    def add_user_input(self, field_name: str, value: Any, metadata: dict = None) -> None:
        """
        Add data from user input source.

        Args:
            field_name: Name of the field being validated
            value: The user-provided value
            metadata: Optional metadata about the input
        """
        source = DataSource(
            source_type="user_input",
            value=value,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )

        if field_name not in self.data_points:
            self.data_points[field_name] = DataPoint(field_name)

        self.data_points[field_name].add_source(source)

    def add_gbp_data(self, field_name: str, value: Any, metadata: dict = None) -> None:
        """
        Add data from Google Business Profile API source.

        Args:
            field_name: Name of the field being validated
            value: The GBP API value
            metadata: Optional metadata about the API response
        """
        source = DataSource(
            source_type="gbp_api",
            value=value,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )

        if field_name not in self.data_points:
            self.data_points[field_name] = DataPoint(field_name)

        self.data_points[field_name].add_source(source)

    def add_benchmark_data(self, field_name: str, value: Any, region: str, metadata: dict = None) -> None:
        """
        Add data from benchmark source.

        Args:
            field_name: Name of the field being validated
            value: The benchmark value
            region: Geographic region for the benchmark data
            metadata: Optional metadata about the benchmark
        """
        meta = metadata or {}
        meta["region"] = region

        source = DataSource(
            source_type="benchmark",
            value=value,
            timestamp=datetime.now().isoformat(),
            metadata=meta
        )

        if field_name not in self.data_points:
            self.data_points[field_name] = DataPoint(field_name)

        self.data_points[field_name].add_source(source)

    def get_validated_field(self, field_name: str) -> Optional[DataPoint]:
        """
        Retrieve a validated field by name.

        Args:
            field_name: Name of the field to retrieve

        Returns:
            DataPoint if exists, None otherwise
        """
        return self.data_points.get(field_name)

    def validate_whatsapp(
        self,
        web_value: str = None,
        gbp_value: str = None,
        user_value: str = None
    ) -> DataPoint:
        """
        Validate WhatsApp number across multiple sources.

        Args:
            web_value: WhatsApp from web scraping
            gbp_value: WhatsApp from GBP API
            user_value: WhatsApp from user input

        Returns:
            Validated DataPoint for "whatsapp"
        """
        field_name = "whatsapp"

        # Clear existing data for this field
        if field_name in self.data_points:
            del self.data_points[field_name]

        # Add all provided values
        if web_value is not None:
            normalized = normalize_phone_number(web_value)
            self.add_scraped_data(field_name, normalized, {"original": web_value})

        if gbp_value is not None:
            normalized = normalize_phone_number(gbp_value)
            self.add_gbp_data(field_name, normalized, {"original": gbp_value})

        if user_value is not None:
            normalized = normalize_phone_number(user_value)
            self.add_user_input(field_name, normalized, {"original": user_value})

        return self.data_points.get(field_name)

    def validate_adr(
        self,
        scraped_price: str = None,
        user_input: float = None,
        benchmark_region: float = None
    ):
        """
        Validate Average Daily Rate (ADR) across multiple sources.

        Args:
            scraped_price: Price from web scraping (as string)
            user_input: Price from user input (as float)
            benchmark_region: Regional benchmark price (as float)

        Returns:
            DataPoint for "adr" or None if no values provided
        """
        field_name = "adr"

        # Clear existing data for this field
        if field_name in self.data_points:
            del self.data_points[field_name]

        # Add all provided values
        if scraped_price is not None:
            try:
                price = float(scraped_price)
                self.add_scraped_data(field_name, price, {"original": scraped_price})
            except (ValueError, TypeError):
                pass

        if user_input is not None:
            self.add_user_input(field_name, user_input, {"original": user_input})

        if benchmark_region is not None:
            self.add_benchmark_data(field_name, benchmark_region, {"region": "default"})

        return self.data_points.get(field_name)

    def get_all_validations(self) -> Dict[str, Dict]:
        """
        Get all validated fields with their full details.

        Returns:
            Dictionary mapping field names to their to_dict() representations
        """
        return {
            field_name: data_point.to_dict()
            for field_name, data_point in self.data_points.items()
        }

    def get_conflict_report(self) -> List[Dict]:
        """
        Generate a report of all fields with conflicts or unknown confidence.

        Returns:
            List of field dictionaries that have CONFLICT or UNKNOWN confidence
        """
        conflicts = []

        for field_name, data_point in self.data_points.items():
            if data_point.confidence in (ConfidenceLevel.CONFLICT, ConfidenceLevel.UNKNOWN):
                conflicts.append(data_point.to_dict())

        return conflicts


def normalize_phone_number(phone: str) -> str:
    """
    Normalize a phone number for consistent comparison.

    Removes all non-numeric characters and handles Colombian
    phone number formats.

    Args:
        phone: Raw phone number string

    Returns:
        Normalized phone number string
    """
    if not phone:
        return ""

    # Remove all non-numeric characters
    digits = ''.join(c for c in phone if c.isdigit())

    # Handle Colombian phone number formats
    # Colombia uses +57 country code
    # Mobile numbers: 3XX XXX XXXX (10 digits)
    # Landlines: 60X XXX XXXX or 60X XXXX XXXX

    if not digits:
        return ""

    # Remove country code if present (57 for Colombia)
    if digits.startswith("57") and len(digits) > 10:
        digits = digits[2:]

    # Handle cases where there's a leading 0 (old format)
    if digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]

    # Handle cases with area code 60X prefix
    if digits.startswith("60") and len(digits) >= 10:
        digits = digits[2:]

    return digits
