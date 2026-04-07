"""
Data Aggregator - Unifica datos de GA4 y GSC en datos unificados.

FASE: FASE-D (GAP-IAO-01-06)
Estado: IMPLEMENTADO

Gracious degradation:
- Sin GSC: funciona solo con GA4
- Sin GA4: funciona solo con GSC
- Sin ambos: funciona con datos vacios
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ConfidenceLevel(str, Enum):
    """Nivel de confianza de los datos agregados."""
    LOW = "LOW"       # Sin fuentes de datos activas
    MEDIUM = "MEDIUM" # Una fuente activa (GA4 o GSC)
    HIGH = "HIGH"     # Ambas fuentes activas (GA4 + GSC)


@dataclass
class UnifiedAnalyticsData:
    """
    Datos unificados de todas las fuentes de analytics.

    Combina datos de GA4 y GSC de forma coherente.
    Cuando una fuente no esta disponible, se degradan graciosamente.
    """
    # Metadata
    confidence_level: ConfidenceLevel = ConfidenceLevel.LOW
    collected_at: str = ""
    date_range_start: str = ""
    date_range_end: str = ""

    # Fuentes activas
    ga4_available: bool = False
    gsc_available: bool = False

    # GA4 data
    ga4_sessions_indirect: int = 0
    ga4_sessions_direct: int = 0
    ga4_sessions_referral: int = 0
    ga4_top_sources: List[Dict[str, Any]] = field(default_factory=list)

    # GSC data
    gsc_total_clicks: int = 0
    gsc_total_impressions: int = 0
    gsc_avg_ctr: float = 0.0
    gsc_avg_position: float = 0.0
    gsc_top_queries: List[Dict[str, Any]] = field(default_factory=list)
    gsc_opportunities: List[Dict[str, Any]] = field(default_factory=list)

    # Derivados
    estimated_ia_visibility: float = 0.0  # Estimacion de visibilidad en IA
    organic_health_score: float = 0.0     # Score de salud organica (0-100)

    def to_dict(self) -> Dict[str, Any]:
        """Serializa a dict."""
        return {
            "confidence_level": self.confidence_level.value,
            "collected_at": self.collected_at,
            "date_range_start": self.date_range_start,
            "date_range_end": self.date_range_end,
            "ga4_available": self.ga4_available,
            "gsc_available": self.gsc_available,
            "ga4_sessions_indirect": self.ga4_sessions_indirect,
            "ga4_sessions_direct": self.ga4_sessions_direct,
            "ga4_sessions_referral": self.ga4_sessions_referral,
            "ga4_top_sources": self.ga4_top_sources,
            "gsc_total_clicks": self.gsc_total_clicks,
            "gsc_total_impressions": self.gsc_total_impressions,
            "gsc_avg_ctr": self.gsc_avg_ctr,
            "gsc_avg_position": self.gsc_avg_position,
            "gsc_top_queries": self.gsc_top_queries,
            "gsc_opportunities": self.gsc_opportunities,
            "estimated_ia_visibility": self.estimated_ia_visibility,
            "organic_health_score": self.organic_health_score,
        }

    def summary_text(self) -> str:
        """Texto resumido para templates del diagnostico."""
        parts = []
        sources = []
        if self.ga4_available:
            sources.append("GA4")
        if self.gsc_available:
            sources.append("GSC")

        sources_str = " + ".join(sources) if sources else "Ninguna"
        parts.append(f"Confianza: {self.confidence_level.value}")
        parts.append(f"Fuentes: {sources_str}")

        if self.gsc_available:
            parts.append(f"GSC: {self.gsc_total_impressions} impresiones, "
                         f"CTR {self.gsc_avg_ctr:.1f}%, "
                         f"Posicion {self.gsc_avg_position:.1f}")

        if self.ga4_available:
            parts.append(f"GA4: {self.ga4_sessions_indirect} sesiones indirectas")

        if self.estimated_ia_visibility > 0:
            parts.append(f"Visibilidad IA: {self.estimated_ia_visibility:.1f}%")

        return " | ".join(parts)


class AnalyticsAggregator:
    """
    Agrega datos de GA4 y GSC en un objeto unificado.

    Usage:
        aggregator = AnalyticsAggregator()
        data = aggregator.collect(start_date, end_date)
        print(data.summary_text())
    """

    def __init__(self, ga4_client=None, gsc_client=None):
        """
        Args:
            ga4_client: Instancia de GoogleAnalyticsClient o None
            gsc_client: Instancia de GoogleSearchConsoleClient o None
        """
        self.ga4_client = ga4_client
        self.gsc_client = gsc_client

    def collect(
        self,
        start_date: str = None,
        end_date: str = None,
    ) -> UnifiedAnalyticsData:
        """
        Recolecta datos de todas las fuentes disponibles.

        Args:
            start_date: Fecha inicio YYYY-MM-DD. Default: 30 dias atras.
            end_date: Fecha fin YYYY-MM-DD. Default: hoy.

        Returns:
            UnifiedAnalyticsData con todos los datos disponibles
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        result = UnifiedAnalyticsData(
            collected_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            date_range_start=start_date,
            date_range_end=end_date,
        )

        # GA4
        result = self._collect_ga4(result)

        # GSC
        result = self._collect_gsc(result)

        # Calcular confianza
        result.confidence_level = self._compute_confidence(
            result.ga4_available, result.gsc_available
        )

        # Calcular metricas derivadas
        result.estimated_ia_visibility = self._estimate_ia_visibility(result)
        result.organic_health_score = self._compute_organic_health_score(result)

        return result

    def _collect_ga4(self, result: UnifiedAnalyticsData) -> UnifiedAnalyticsData:
        """Recolecta datos de GA4 si disponible."""
        try:
            if self.ga4_client and hasattr(self.ga4_client, 'is_available') and self.ga4_client.is_available():
                data = self.ga4_client.get_indirect_traffic("last_30_days")
                result.ga4_available = data.get("data_source") == "GA4"
                result.ga4_sessions_indirect = data.get("sessions_indirect", 0)
                result.ga4_sessions_direct = data.get("sessions_direct", 0)
                result.ga4_sessions_referral = data.get("sessions_referral", 0)
                result.ga4_top_sources = data.get("top_sources", [])[:5]
            elif self.ga4_client:
                # Cliente existe pero no configurado
                result.ga4_available = False
        except Exception as e:
            logger.warning(f"Error recolectando GA4: {e}")
            result.ga4_available = False

        return result

    def _collect_gsc(self, result: UnifiedAnalyticsData) -> UnifiedAnalyticsData:
        """Recolecta datos de GSC si disponible."""
        try:
            if self.gsc_client and hasattr(self.gsc_client, 'is_configured') and self.gsc_client.is_configured():
                report = self.gsc_client.get_search_analytics(
                    start_date=result.date_range_start,
                    end_date=result.date_range_end,
                )
                result.gsc_available = report.is_available
                if report.is_available:
                    result.gsc_total_clicks = report.total_clicks
                    result.gsc_total_impressions = report.total_impressions
                    result.gsc_avg_ctr = report.avg_ctr
                    result.gsc_avg_position = report.avg_position
                    result.gsc_top_queries = [
                        {
                            "query": q.query,
                            "clicks": q.clicks,
                            "impressions": q.impressions,
                            "ctr": q.ctr,
                            "position": q.position,
                        }
                        for q in report.queries[:20]
                    ]

                    # Oportunidades
                    opportunities = self.gsc_client.get_top_opportunities(report, top_n=10)
                    result.gsc_opportunities = [
                        {
                            "query": q.query,
                            "impressions": q.impressions,
                            "ctr": q.ctr,
                            "position": q.position,
                            "opportunity_score": round(q.opportunity_score, 1),
                        }
                        for q in opportunities
                    ]
            elif self.gsc_client:
                result.gsc_available = False
        except Exception as e:
            logger.warning(f"Error recolectando GSC: {e}")
            result.gsc_available = False

        return result

    def _compute_confidence(self, ga4_ok: bool, gsc_ok: bool) -> ConfidenceLevel:
        """Calcula el nivel de confianza basado en fuentes disponibles."""
        if ga4_ok and gsc_ok:
            return ConfidenceLevel.HIGH
        elif ga4_ok or gsc_ok:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def _estimate_ia_visibility(self, data: UnifiedAnalyticsData) -> float:
        """
        Estima visibilidad en IA basado en datos disponibles.

        Heuristica simple:
        - Con GSC: basado en CTR organico y posicion promedio
        - Con GA4: basado en sesiones indirectas
        - Sin datos: 0
        """
        if data.gsc_available and data.gsc_total_impressions > 0:
            # CTR mas alto + mejor posicion = mayor visibilidad
            ctr_factor = min(data.gsc_avg_ctr / 10.0, 1.0)
            position_factor = max(1.0 - (data.gsc_avg_position / 30.0), 0.0)
            visibility = (ctr_factor * 0.6 + position_factor * 0.4) * 100.0
            return max(0.0, min(visibility, 100.0))
        elif data.ga4_available:
            total = (data.ga4_sessions_indirect + data.ga4_sessions_direct +
                     data.ga4_sessions_referral)
            if total > 0:
                return (data.ga4_sessions_indirect / total) * 100.0
        return 0.0

    def _compute_organic_health_score(self, data: UnifiedAnalyticsData) -> float:
        """
        Score de salud organica 0-100.

        Basado en:
        - Impresiones (volumen)
        - CTR (efectividad)
        - Posicion promedio
        """
        if not data.gsc_available:
            # Con solo GA4, estimar
            if data.ga4_available:
                return 40.0  # Baseline si hay GA4
            return 10.0  # Sin datos

        score = 0.0

        # Impresiones (0-30 pts)
        impressions = data.gsc_total_impressions
        if impressions >= 1000:
            score += 30
        elif impressions >= 100:
            score += 20
        elif impressions > 0:
            score += 10

        # CTR (0-35 pts)
        ctr = data.gsc_avg_ctr
        if ctr >= 5.0:
            score += 35
        elif ctr >= 3.0:
            score += 25
        elif ctr >= 1.0:
            score += 15
        elif ctr > 0:
            score += 5

        # Posicion (0-35 pts)
        pos = data.gsc_avg_position
        if pos <= 5.0:
            score += 35
        elif pos <= 10.0:
            score += 25
        elif pos <= 20.0:
            score += 15
        else:
            score += 5

        return round(min(score, 100.0), 1)
