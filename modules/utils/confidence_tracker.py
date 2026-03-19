"""Confidence tracker for data source transparency.

Tracks the origin of all financial data (hotel-provided vs benchmark fallback)
to generate transparent diagnostics.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class DataSource(Enum):
    HOTEL_INPUT = "hotel_input"
    PLAN_MAESTRO_JSON = "plan_maestro_json"
    BENCHMARKING_MD = "benchmarking_md"
    CALCULATED = "calculated"
    UNKNOWN = "unknown"


@dataclass
class DataConfidence:
    """Single data point with source tracking."""
    field_name: str
    value: Any
    source: DataSource
    source_detail: str = ""
    is_estimated: bool = False
    confidence_score: float = 1.0  # 0.0 to 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field_name,
            "value": self.value,
            "source": self.source.value,
            "source_detail": self.source_detail,
            "estimated": self.is_estimated,
            "confidence": self.confidence_score,
        }


@dataclass
class ConfidenceReport:
    """Complete report of all data sources used in diagnostic."""
    data_points: List[DataConfidence] = field(default_factory=list)

    def add(
        self,
        field_name: str,
        value: Any,
        source: DataSource,
        source_detail: str = "",
        is_estimated: bool = False,
        confidence: float = 1.0,
    ) -> None:
        self.data_points.append(DataConfidence(
            field_name=field_name,
            value=value,
            source=source,
            source_detail=source_detail,
            is_estimated=is_estimated,
            confidence_score=confidence,
        ))

    def get_field(self, field_name: str) -> Optional[DataConfidence]:
        for dp in self.data_points:
            if dp.field_name == field_name:
                return dp
        return None

    def has_hotel_data(self) -> bool:
        return any(dp.source == DataSource.HOTEL_INPUT for dp in self.data_points)

    def get_sources_summary(self) -> Dict[str, int]:
        summary = {}
        for dp in self.data_points:
            key = dp.source.value
            summary[key] = summary.get(key, 0) + 1
        return summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data_points": [dp.to_dict() for dp in self.data_points],
            "sources_summary": self.get_sources_summary(),
            "has_hotel_input": self.has_hotel_data(),
        }


class ConfidenceTracker:
    """
    Tracks data provenance throughout the diagnostic pipeline.
    
    Usage:
        tracker = ConfidenceTracker()
        
        # When hotel provides data
        tracker.add_field("reservas_mes", 250, DataSource.HOTEL_INPUT, 
                         "Direct input from hotel questionnaire")
        
        # When using benchmark fallback
        tracker.add_field("reservas_mes", 200, DataSource.PLAN_MAESTRO_JSON,
                         "Eje Cafetero regional average", is_estimated=True)
        
        # Generate transparent report
        report = tracker.generate_report()
    """

    def __init__(self) -> None:
        self.report = ConfidenceReport()

    def add_field(
        self,
        field_name: str,
        value: Any,
        source: DataSource,
        source_detail: str = "",
        is_estimated: bool = False,
        confidence: Optional[float] = None,
    ) -> None:
        """Add a data point with its source."""
        if confidence is None:
            confidence = self._default_confidence(source, is_estimated)
        
        self.report.add(
            field_name=field_name,
            value=value,
            source=source,
            source_detail=source_detail,
            is_estimated=is_estimated,
            confidence=confidence,
        )

    def _default_confidence(self, source: DataSource, is_estimated: bool) -> float:
        """Get default confidence score based on source."""
        base_confidence = {
            DataSource.HOTEL_INPUT: 1.0,
            DataSource.PLAN_MAESTRO_JSON: 0.85,
            DataSource.BENCHMARKING_MD: 0.70,
            DataSource.CALCULATED: 0.90,
            DataSource.UNKNOWN: 0.50,
        }.get(source, 0.50)
        
        return base_confidence * 0.9 if is_estimated else base_confidence

    def generate_report(self) -> ConfidenceReport:
        """Return the confidence report."""
        return self.report
