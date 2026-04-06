"""
Modelos de datos para métricas y KPIs de AEO (Answer Engine Optimization).

Este módulo define la estructura de datos para medir el rendimiento de AEO,
incluyendo AI Visibility Score, Share of Voice, y Voice Readiness Index.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class DataSource(Enum):
    """Fuente de datos para las métricas."""
    PROFOUND_API = "profound_api"
    SEMRUSH_API = "semrush_api"
    GOOGLE_SEARCH_CONSOLE = "google_search_console"
    MOCK = "mock"


@dataclass
class AEOKPI:
    """Un KPI individual de AEO."""
    name: str
    value: float
    unit: str  # e.g., "%", "points", "ratio"
    source: DataSource
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "source": self.source.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class VoiceReadinessScore:
    """Desglose del Voice Readiness Index."""
    schema_quality: float  # 0-100
    speakable_coverage: float  # 0-100
    faq_tts_compliance: float  # 0-100
    structured_data_score: float  # 0-100
    overall: float = 0.0  # Calculado

    def __post_init__(self):
        self.overall = (
            self.schema_quality * 0.25 +
            self.speakable_coverage * 0.25 +
            self.faq_tts_compliance * 0.25 +
            self.structured_data_score * 0.25
        )

    def to_dict(self) -> dict:
        return {
            "schema_quality": self.schema_quality,
            "speakable_coverage": self.speakable_coverage,
            "faq_tts_compliance": self.faq_tts_compliance,
            "structured_data_score": self.structured_data_score,
            "overall": round(self.overall, 2),
        }


@dataclass
class IndirectTrafficMetrics:
    """Métricas de tráfico indirecto de GA4 (Método #5 KB)."""
    sessions_indirect: int = 0
    sessions_direct: int = 0
    sessions_referral: int = 0
    data_source: str = "N/A"
    top_sources: list = field(default_factory=list)
    date_range: Optional[str] = None
    note: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "sessions_indirect": self.sessions_indirect,
            "sessions_direct": self.sessions_direct,
            "sessions_referral": self.sessions_referral,
            "data_source": self.data_source,
            "top_sources": self.top_sources,
            "date_range": self.date_range,
            "note": self.note,
        }

    @classmethod
    def from_ga4_response(cls, response: dict) -> "IndirectTrafficMetrics":
        """Factory method para crear desde respuesta de GA4."""
        return cls(
            sessions_indirect=response.get("sessions_indirect", 0),
            sessions_direct=response.get("sessions_direct", 0),
            sessions_referral=response.get("sessions_referral", 0),
            data_source=response.get("data_source", "N/A"),
            top_sources=response.get("top_sources", []),
            date_range=response.get("date_range"),
            note=response.get("note"),
        )


@dataclass
class AEOKPIs:
    """
    Framework completo de KPIs para AEO.
    
    Incluye AI Visibility Score, Share of Voice, Tasa de Citación,
    y Voice Readiness Index composite.
    
    GAP-IAO-01-05: Agregado indirect_traffic (GA4) como método #5.
    """
    hotel_name: str
    url: str
    
    # Core AEO Metrics
    ai_visibility_score: Optional[float] = None  # 0-100
    share_of_voice: Optional[float] = None  # 0-100%
    citation_rate: Optional[float] = None  # 0-100%
    voice_search_impressions: Optional[int] = None
    
    # Voice Readiness (internal assessment)
    voice_readiness: Optional[VoiceReadinessScore] = None
    
    # Competitor benchmarks
    competitors_analyzed: int = 0
    competitor_avg_viscosity: Optional[float] = None
    
    # GAP-IAO-01-05: GA4 indirect traffic (Método #5)
    indirect_traffic: Optional[IndirectTrafficMetrics] = None
    
    # Metadata
    data_source: DataSource = DataSource.MOCK
    generated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"

    def calculate_composite_score(self) -> float:
        """
        Calcula un AI Visibility Score composite combinando métricas disponibles.
        
        GAP-IAO-01-05: Incluye GA4 (indirect_traffic) como método #5 cuando disponible.
        
        Returns:
            float: Score 0-100, o -1 si no hay datos suficientes.
        """
        scores = []
        
        if self.ai_visibility_score is not None:
            scores.append(self.ai_visibility_score * 0.35)  # Reducido de 0.40
        
        if self.share_of_voice is not None:
            scores.append(self.share_of_voice * 0.20)
        
        if self.citation_rate is not None:
            scores.append(self.citation_rate * 0.20)
        
        if self.voice_readiness is not None:
            scores.append(self.voice_readiness.overall * 0.15)  # Reducido de 0.20
        
        # GAP-IAO-01-05: GA4 como método #5 (25% cuando disponible)
        if (self.indirect_traffic is not None and 
            self.indirect_traffic.data_source == "GA4"):
            # Normalizar: 100 sesiones = 10 puntos, máximo 100 sesiones = 10 pts
            indirect_normalized = min(10, self.indirect_traffic.sessions_indirect / 10)
            scores.append(indirect_normalized * 0.10)  # 10% del score total
        
        if not scores:
            return -1.0
        
        return round(sum(scores), 2)

    def to_dict(self) -> dict:
        """Serializa el framework de KPIs a diccionario."""
        return {
            "hotel_name": self.hotel_name,
            "url": self.url,
            "ai_visibility_score": self.ai_visibility_score,
            "share_of_voice": self.share_of_voice,
            "citation_rate": self.citation_rate,
            "voice_search_impressions": self.voice_search_impressions,
            "voice_readiness": self.voice_readiness.to_dict() if self.voice_readiness else None,
            "competitors_analyzed": self.competitors_analyzed,
            "competitor_avg_viscosity": self.competitor_avg_viscosity,
            # GAP-IAO-01-05: GA4 indirect traffic
            "indirect_traffic": self.indirect_traffic.to_dict() if self.indirect_traffic else None,
            "data_source": self.data_source.value,
            "composite_score": self.calculate_composite_score(),
            "generated_at": self.generated_at.isoformat(),
            "version": self.version,
        }
