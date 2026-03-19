"""
Confidence Taxonomy System for IA Hoteles Agent v4.0

Provides a structured approach to data validation and confidence scoring
for hotel data points across multiple sources.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


class ConfidenceLevel(Enum):
    """Confidence levels for data validation results."""
    VERIFIED = "verified"
    ESTIMATED = "estimated"
    CONFLICT = "conflict"
    UNKNOWN = "unknown"


@dataclass
class DataSource:
    """Represents a single source of data for a field."""
    source_type: str  # web_scraping, user_input, gbp_api, benchmark, api_external
    value: Any
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of validating data across multiple sources."""
    confidence_level: ConfidenceLevel
    final_value: Any
    sources_used: List[DataSource]
    match_percentage: float
    discrepancies: List[str] = field(default_factory=list)
    requires_manual_review: bool = False
    can_use_in_assets: bool = False
    disclaimer: Optional[str] = None
    icon: str = ""


class ConfidenceTaxonomy:
    """
    Centralized taxonomy for confidence levels and validation rules.
    """

    TAXONOMY = {
        ConfidenceLevel.VERIFIED: {
            "description": "Data confirmed by multiple independent sources with high consistency",
            "min_sources": 2,
            "min_match_percentage": 90.0,
            "can_use_in_assets": True,
            "requires_review": False,
            "icon": "✓",
            "color": "green",
        },
        ConfidenceLevel.ESTIMATED: {
            "description": "Data from single reliable source or multiple sources with minor discrepancies",
            "min_sources": 1,
            "min_match_percentage": 70.0,
            "can_use_in_assets": True,
            "requires_review": False,
            "icon": "~",
            "color": "yellow",
        },
        ConfidenceLevel.CONFLICT: {
            "description": "Significant discrepancies between sources requiring manual resolution",
            "min_sources": 2,
            "min_match_percentage": 0.0,
            "can_use_in_assets": False,
            "requires_review": True,
            "icon": "⚠",
            "color": "orange",
        },
        ConfidenceLevel.UNKNOWN: {
            "description": "No reliable data sources available",
            "min_sources": 0,
            "min_match_percentage": 0.0,
            "can_use_in_assets": False,
            "requires_review": True,
            "icon": "?",
            "color": "gray",
        },
    }

    @classmethod
    def get_taxonomy_info(cls, level: ConfidenceLevel) -> Dict[str, Any]:
        """Get taxonomy information for a confidence level."""
        return cls.TAXONOMY.get(level, {})

    @classmethod
    def calculate_match_percentage(cls, values: List[Any]) -> float:
        """
        Calculate match percentage between multiple values.
        Returns 100.0 if all values match, lower percentage based on similarity.
        """
        if not values:
            return 0.0
        if len(values) == 1:
            return 100.0

        # Normalize values for comparison
        normalized = []
        for v in values:
            if v is None:
                normalized.append(None)
            elif isinstance(v, str):
                normalized.append(v.lower().strip())
            elif isinstance(v, (int, float)):
                normalized.append(str(v))
            else:
                normalized.append(str(v).lower().strip())

        # Count matches
        matches = 0
        total_pairs = 0
        for i in range(len(normalized)):
            for j in range(i + 1, len(normalized)):
                total_pairs += 1
                if normalized[i] == normalized[j]:
                    matches += 1
                # Phone number special handling
                elif normalized[i] and normalized[j]:
                    norm_i = cls._normalize_phone(str(normalized[i]))
                    norm_j = cls._normalize_phone(str(normalized[j]))
                    if norm_i and norm_j and norm_i == norm_j:
                        matches += 0.9  # Near match for phone formatting differences

        if total_pairs == 0:
            return 100.0
        return (matches / total_pairs) * 100.0

    @staticmethod
    def _normalize_phone(phone: str) -> Optional[str]:
        """Normalize phone number for comparison."""
        if not phone:
            return None
        # Remove all non-digit characters
        digits = ''.join(c for c in phone if c.isdigit())
        # Handle country codes - keep last 10 digits for comparison
        if len(digits) > 10:
            digits = digits[-10:]
        return digits if digits else None

    @classmethod
    def determine_confidence_level(
        cls,
        sources: List[DataSource],
        match_percentage: float
    ) -> ConfidenceLevel:
        """
        Determine confidence level based on sources and match percentage.
        """
        if not sources:
            return ConfidenceLevel.UNKNOWN

        if len(sources) >= 2:
            if match_percentage >= 90.0:
                return ConfidenceLevel.VERIFIED
            elif match_percentage >= 70.0:
                return ConfidenceLevel.ESTIMATED
            else:
                return ConfidenceLevel.CONFLICT
        else:
            # Single source
            if match_percentage >= 70.0:
                return ConfidenceLevel.ESTIMATED
            else:
                return ConfidenceLevel.UNKNOWN

    @classmethod
    def _generate_disclaimer(
        cls,
        level: ConfidenceLevel,
        field_name: str,
        sources: List[DataSource]
    ) -> Optional[str]:
        """Generate appropriate disclaimer based on confidence level."""
        if level == ConfidenceLevel.VERIFIED:
            return None
        elif level == ConfidenceLevel.ESTIMATED:
            source_types = list(set(s.source_type for s in sources))
            return f"Dato estimado basado en: {', '.join(source_types)}"
        elif level == ConfidenceLevel.CONFLICT:
            return f"Conflicto detectado en '{field_name}'. Requiere revisión manual."
        else:
            return f"Sin datos disponibles para '{field_name}'"


class DataPoint:
    """
    Represents a single data field with multiple sources and confidence tracking.
    """

    def __init__(self, field_name: str):
        self.field_name = field_name
        self._sources: List[DataSource] = []
        self._validation_result: Optional[ValidationResult] = None
        self._recalculate()

    def add_source(self, source: DataSource) -> None:
        """Add a data source and recalculate confidence."""
        self._sources.append(source)
        self._recalculate()

    def _recalculate(self) -> None:
        """Recalculate validation result based on current sources."""
        if not self._sources:
            self._validation_result = ValidationResult(
                confidence_level=ConfidenceLevel.UNKNOWN,
                final_value=None,
                sources_used=[],
                match_percentage=0.0,
                discrepancies=["No data sources available"],
                requires_manual_review=True,
                can_use_in_assets=False,
                disclaimer=ConfidenceTaxonomy._generate_disclaimer(
                    ConfidenceLevel.UNKNOWN, self.field_name, []
                ),
                icon="?"
            )
            return

        # Calculate match percentage
        values = [s.value for s in self._sources]
        match_percentage = ConfidenceTaxonomy.calculate_match_percentage(values)

        # Determine confidence level
        confidence_level = ConfidenceTaxonomy.determine_confidence_level(
            self._sources, match_percentage
        )

        # Get taxonomy info
        taxonomy_info = ConfidenceTaxonomy.get_taxonomy_info(confidence_level)

        # Determine final value (use most common or first source)
        final_value = self._determine_final_value(values)

        # Find discrepancies
        discrepancies = self._find_discrepancies()

        # Generate disclaimer
        disclaimer = ConfidenceTaxonomy._generate_disclaimer(
            confidence_level, self.field_name, self._sources
        )

        self._validation_result = ValidationResult(
            confidence_level=confidence_level,
            final_value=final_value,
            sources_used=self._sources.copy(),
            match_percentage=match_percentage,
            discrepancies=discrepancies,
            requires_manual_review=taxonomy_info.get("requires_review", False),
            can_use_in_assets=taxonomy_info.get("can_use_in_assets", False),
            disclaimer=disclaimer,
            icon=taxonomy_info.get("icon", "")
        )

    def _determine_final_value(self, values: List[Any]) -> Any:
        """Determine the final value from multiple sources."""
        if not values:
            return None
        if len(values) == 1:
            return values[0]

        # Return most common non-None value
        from collections import Counter
        non_none = [v for v in values if v is not None]
        if not non_none:
            return None

        # Normalize for comparison
        normalized_map = {}
        for v in non_none:
            if isinstance(v, str):
                norm = v.lower().strip()
            else:
                norm = str(v).lower().strip()
            normalized_map[norm] = v

        counter = Counter(normalized_map.keys())
        most_common = counter.most_common(1)[0][0]
        return normalized_map[most_common]

    def _find_discrepancies(self) -> List[str]:
        """Find discrepancies between sources."""
        if len(self._sources) < 2:
            return []

        discrepancies = []
        values = [(s.source_type, s.value) for s in self._sources]

        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                type_a, val_a = values[i]
                type_b, val_b = values[j]

                # Normalize for comparison
                norm_a = self._normalize_for_comparison(val_a)
                norm_b = self._normalize_for_comparison(val_b)

                if norm_a != norm_b:
                    discrepancies.append(
                        f"{type_a} ({val_a}) != {type_b} ({val_b})"
                    )

        return discrepancies

    def _normalize_for_comparison(self, value: Any) -> Any:
        """Normalize a value for comparison."""
        if value is None:
            return None
        if isinstance(value, str):
            return value.lower().strip()
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value
        return str(value).lower().strip()

    @property
    def value(self) -> Any:
        """Get the final validated value."""
        return self._validation_result.final_value if self._validation_result else None

    @property
    def confidence(self) -> ConfidenceLevel:
        """Get the confidence level."""
        return self._validation_result.confidence_level if self._validation_result else ConfidenceLevel.UNKNOWN

    @property
    def can_use(self) -> bool:
        """Check if this data point can be used in assets."""
        return self._validation_result.can_use_in_assets if self._validation_result else False

    def to_dict(self) -> Dict[str, Any]:
        """Convert data point to dictionary representation."""
        return {
            "field_name": self.field_name,
            "value": self.value,
            "confidence": self.confidence.value,
            "can_use": self.can_use,
            "match_percentage": self._validation_result.match_percentage if self._validation_result else 0.0,
            "sources_count": len(self._sources),
            "sources": [
                {
                    "source_type": s.source_type,
                    "value": s.value,
                    "timestamp": s.timestamp,
                    "metadata": s.metadata
                }
                for s in self._sources
            ],
            "discrepancies": self._validation_result.discrepancies if self._validation_result else [],
            "requires_manual_review": self._validation_result.requires_manual_review if self._validation_result else True,
            "disclaimer": self._validation_result.disclaimer if self._validation_result else None,
            "icon": self._validation_result.icon if self._validation_result else "",
        }
