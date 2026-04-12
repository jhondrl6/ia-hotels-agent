"""AEO Snippet Tracker for featured snippet measurement.

Measures real AEO outcomes: featured snippets captured and People Also Ask presence.
Uses SerpAPI as data source (free tier: 100 queries/month).

Usage:
    from modules.auditors.aeo_snippet_tracker import AEOSnippetTracker, AEOSnippetReport

    tracker = AEOSnippetTracker(serpapi_key=os.getenv("SERPAPI_KEY"))
    report = tracker.check_snippets(
        hotel_name="Hotel Casa de la Paz",
        hotel_url="https://hotel.com",
        location="Armenia, Quindio",
        landmark="Parque de la Vida",
    )
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import os
import re

import httpx


@dataclass
class SnippetResult:
    """Result of testing a single factual query."""
    query: str                      # Query factual ejecutada
    has_snippet: bool               # Si hay featured snippet
    snippet_source: Optional[str]    # URL del sitio que captura el snippet
    is_our_hotel: bool               # Si el snippet es de nuestro hotel
    snippet_type: Optional[str]      # "paragraph" | "list" | "table"
    people_also_ask: List[str]      # Preguntas relacionadas


@dataclass
class AEOSnippetReport:
    """Complete AEO snippet audit report."""
    hotel_url: str
    queries_tested: int
    snippets_captured: int          # Cuántos snippets captura el hotel
    snippets_competitor: int         # Cuántos captura la competencia
    paa_presence: int               # Veces que aparece en People Also Ask
    snippet_score: int              # 0-100
    queries: List[SnippetResult]
    source: str                     # "serpapi" | "stub"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class AEOSnippetTracker:
    """Tracks featured snippet capture for AEO measurement.

    Queries factual queries via SerpAPI to detect:
    - Featured snippets (position zero)
    - People Also Ask (PAA) presence
    - Competitor snippet capture

    Costo API:
    - Free tier: 100 queries/month
    - Paid: $50/month for 1,000 queries

    Sin API key: retorna stub con source="stub".
    """

    QUERIES_FACTUALES = [
        "hotel {nombre} horario",
        "hotel {nombre} telefono",
        "hotel {nombre} direccion",
        "hoteles boutique en {ciudad}",
        "mejor hotel cerca de {landmark}",
    ]

    def __init__(self, serpapi_key: Optional[str] = None, timeout: float = 15.0):
        """Initialize tracker.

        Args:
            serpapi_key: SerpAPI key. If None, reads from SERPAPI_KEY env var.
                        If still None, operates in stub mode.
            timeout: Request timeout in seconds.
        """
        self.serpapi_key = serpapi_key or os.getenv("SERPAPI_KEY")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout) if self.serpapi_key else None

    def __del__(self):
        """Cleanup HTTP client."""
        if hasattr(self, 'client') and self.client:
            self.client.close()

    def _is_stub(self) -> bool:
        """Check if running in stub mode (no API key)."""
        return self.serpapi_key is None

    def check_snippets(
        self,
        hotel_name: str,
        hotel_url: str,
        location: str = "",
        landmark: str = "",
    ) -> AEOSnippetReport:
        """Execute factual queries and verify snippet capture.

        Args:
            hotel_name: Nombre del hotel a auditar.
            hotel_url: URL del hotel para comparar con fuentes de snippets.
            location: Ciudad/region para queries geolocalizadas.
            landmark: Landmark cercano para queries de proximidad.

        Returns:
            AEOSnippetReport con resultados de snippets.
            Si no hay API key: retorna stub con source="stub".
        """
        if self._is_stub():
            return self._stub_report(hotel_url)

        # Generar queries concretas
        queries = self._generar_queries(hotel_name, location, landmark)

        results: List[SnippetResult] = []
        snippets_our_hotel = 0
        snippets_competitor = 0
        paa_count = 0

        for query in queries:
            try:
                result = self._query_serpapi(query, hotel_url)
                results.append(result)
                if result.is_our_hotel:
                    snippets_our_hotel += 1
                elif result.has_snippet:
                    snippets_competitor += 1
                paa_count += len(result.people_also_ask)
            except Exception:
                # Graceful degradation: si falla una query, continuar con las demas
                results.append(SnippetResult(
                    query=query,
                    has_snippet=False,
                    snippet_source=None,
                    is_our_hotel=False,
                    snippet_type=None,
                    people_also_ask=[],
                ))

        # Calcular score
        total = len(queries) if queries else 1
        snippet_score = int((snippets_our_hotel / total) * 100)

        return AEOSnippetReport(
            hotel_url=hotel_url,
            queries_tested=len(queries),
            snippets_captured=snippets_our_hotel,
            snippets_competitor=snippets_competitor,
            paa_presence=paa_count,
            snippet_score=snippet_score,
            queries=results,
            source="serpapi",
        )

    def _generar_queries(self, hotel_name: str, location: str, landmark: str) -> List[str]:
        """Genera queries factuales concretas."""
        queries = []
        for template in self.QUERIES_FACTUALES:
            query = template.format(
                nombre=hotel_name,
                ciudad=location,
                landmark=landmark,
            )
            queries.append(query)
        return queries

    def _query_serpapi(self, query: str, hotel_url: str) -> SnippetResult:
        """Execute a single SerpAPI query and parse results.

        Args:
            query: Query string to search.
            hotel_url: Hotel URL to compare against snippet sources.

        Returns:
            SnippetResult con datos parseados.
        """
        # Extraer dominio base para comparacion
        hotel_domain = self._extract_domain(hotel_url)

        # SerpAPI endpoint
        params = {
            "q": query,
            "api_key": self.serpapi_key,
            "engine": "google",
            "google_domain": "google.com",
            "gl": "co",  # Colombia
            "hl": "es",  # Espanol
        }

        response = self.client.get(
            "https://serpapi.com/search",
            params=params,
        )
        response.raise_for_status()
        data = response.json()

        # Parse featured snippet
        has_snippet = False
        snippet_source = None
        snippet_type = None
        is_our_hotel = False

        if "answer_box" in data and data["answer_box"]:
            answer = data["answer_box"]
            has_snippet = True
            snippet_type = answer.get("type", "paragraph")

            # Intentar extraer fuente del snippet
            if "source" in answer:
                snippet_source = answer["source"].get("link", "")
            elif "domain" in answer:
                snippet_source = answer["domain"]

            # Verificar si la fuente es nuestro hotel
            if snippet_source and hotel_domain in snippet_source:
                is_our_hotel = True

        # Parse People Also Ask
        paa: List[str] = []
        if "people_also_ask" in data:
            for item in data["people_also_ask"]:
                if "question" in item:
                    paa.append(item["question"])
                # Verificar si nuestro hotel aparece en alguna respuesta PAA
                if "snippet" in item and hotel_domain in str(item.get("snippet", "")):
                    is_our_hotel = True

        return SnippetResult(
            query=query,
            has_snippet=has_snippet,
            snippet_source=snippet_source,
            is_our_hotel=is_our_hotel,
            snippet_type=snippet_type,
            people_also_ask=paa,
        )

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL for comparison."""
        # Simple extraction: "https://hotel.com" -> "hotel.com"
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        return domain.lower()

    def _stub_report(self, hotel_url: str) -> AEOSnippetReport:
        """Generate stub report when no API key is available.

        Returns a stub report with source="stub" so callers know
        the data is not real.
        """
        stub_queries = [
            SnippetResult(
                query=q.format(nombre="[STUB]", ciudad="[STUB]", landmark="[STUB]"),
                has_snippet=False,
                snippet_source=None,
                is_our_hotel=False,
                snippet_type=None,
                people_also_ask=[],
            )
            for q in self.QUERIES_FACTUALES
        ]

        return AEOSnippetReport(
            hotel_url=hotel_url,
            queries_tested=len(stub_queries),
            snippets_captured=0,
            snippets_competitor=0,
            paa_presence=0,
            snippet_score=0,
            queries=stub_queries,
            source="stub",
        )


def get_aeo_snippet_tracker() -> AEOSnippetTracker:
    """Factory function to get AEOSnippetTracker instance.

    Returns:
        AEOSnippetTracker instance (stub if no API key).
    """
    return AEOSnippetTracker(serpapi_key=os.getenv("SERPAPI_KEY"))
