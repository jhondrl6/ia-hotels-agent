"""
Canonical Metrics -- Normalizacion de nombres de metricas entre fuentes externas.

Patron inspirado en Goose (canonical models para LLM providers).
Cada fuente de datos usa su propio vocabulario. Este modulo mapea
todos los nombres a un vocabulario unico interno.
"""

from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class CanonicalMetric:
    """Definicion de una metrica canonica y sus aliases."""
    canonical_name: str       # nombre interno unico
    description: str          # que mide esta metrica
    unit: str                 # unidad (clicks, score, rate, cop, etc.)
    aliases: Dict[str, str] = field(default_factory=dict)  # {fuente: nombre_en_fuente}


# Registro central de metricas canonicas
CANONICAL_METRICS: Dict[str, CanonicalMetric] = {
    "organic_traffic": CanonicalMetric(
        canonical_name="organic_traffic",
        description="Visitas organicas desde motores de busqueda",
        unit="clicks",
        aliases={
            "ga4": "organic_total",
            "ga4_new": "organic_new",
            "profound": "organic_clicks",
            "serpapi": "organicClicks",
            "semrush": "Organic Traffic",
        }
    ),
    "geo_score": CanonicalMetric(
        canonical_name="geo_score",
        description="Completitud del perfil de Google Business",
        unit="score_0_100",
        aliases={
            "places_api": "geo_score",
            "gbp_auditor": "geo_score",
        }
    ),
    "review_rating": CanonicalMetric(
        canonical_name="review_rating",
        description="Calificacion promedio en Google Maps",
        unit="rating_1_5",
        aliases={
            "places_api": "rating",
            "gbp_auditor": "rating",
            "serpapi": "rating",
        }
    ),
    "review_count": CanonicalMetric(
        canonical_name="review_count",
        description="Numero total de reviews en Google Maps",
        unit="count",
        aliases={
            "places_api": "user_rating_count",
            "gbp_auditor": "reviews",
            "serpapi": "reviewsCount",
        }
    ),
    "photo_count": CanonicalMetric(
        canonical_name="photo_count",
        description="Numero de fotos en el perfil GBP",
        unit="count",
        aliases={
            "places_api": "photo_count",
            "gbp_auditor": "photos",
        }
    ),
    "adr": CanonicalMetric(
        canonical_name="adr",
        description="Average Daily Rate (tarifa promedio diaria)",
        unit="cop",
        aliases={
            "manual": "adr",
            "pms": "ADR",
            "benchmark": "adr_avg",
        }
    ),
    "occupancy_rate": CanonicalMetric(
        canonical_name="occupancy_rate",
        description="Tasa de ocupacion del hotel",
        unit="percentage",
        aliases={
            "manual": "occupancy_rate",
            "pms": "occupancy",
        }
    ),
}


def resolve_metric(source: str, source_name: str) -> Optional[str]:
    """
    Resuelve un nombre de metrica de una fuente externa a su nombre canonico.

    Args:
        source: identificador de la fuente (ga4, serpapi, places_api, etc.)
        source_name: nombre de la metrica en esa fuente

    Returns:
        canonical_name si existe, None si no se encuentra
    """
    for canonical, metric in CANONICAL_METRICS.items():
        if source in metric.aliases and metric.aliases[source] == source_name:
            return canonical
    return None


def get_all_names(canonical_name: str) -> Optional[Dict[str, str]]:
    """Devuelve {fuente: nombre_en_fuente} para una metrica canonica."""
    metric = CANONICAL_METRICS.get(canonical_name)
    return metric.aliases if metric else None


def metric_exists(canonical_name: str) -> bool:
    """Verifica si una metrica canonica existe en el registro."""
    return canonical_name in CANONICAL_METRICS


def list_sources() -> list:
    """Lista todas las fuentes registradas."""
    sources = set()
    for metric in CANONICAL_METRICS.values():
        sources.update(metric.aliases.keys())
    return sorted(sources)
