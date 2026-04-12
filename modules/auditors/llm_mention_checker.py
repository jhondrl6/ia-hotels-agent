"""
LLM Mention Checker — IAO Measurement Module.

Consults LLMs (OpenRouter, Gemini, Perplexity) to detect if a hotel
is mentioned in AI-generated recommendations.

REGLA CRITICA: OpenAI SIEMPRE via OpenRouter. NUNCA import openai SDK directo.

Parte de FASE-C: IAO Restoration + LLM Mention Checker.
"""

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class LLMQueryResult:
    """Resultado de una query individual a un LLM provider."""
    provider: str           # "openrouter" | "gemini" | "perplexity"
    query: str              # Query ejecutada
    response_text: str      # Respuesta completa del LLM
    hotel_mentioned: bool   # Si el hotel fue mencionado
    mention_context: str    # Contexto de la mención
    ranking_position: Optional[int] = None  # Posición en lista (1=primero)
    competitors_mentioned: List[str] = field(default_factory=list)
    error: Optional[str] = None  # Error si la query falló


@dataclass
class LLMReport:
    """Reporte consolidado de menciones en LLMs."""
    hotel_name: str
    hotel_url: str
    location: str
    queries_tested: int
    total_mentions: int           # Veces mencionado en todas las queries
    avg_ranking: Optional[float]  # Ranking promedio cuando es mencionado
    mention_rate: float           # mentions / queries_tested (0.0-1.0)
    providers_used: List[str]
    query_results: List[LLMQueryResult] = field(default_factory=list)
    mention_score: int = 0        # 0-100
    source: str = "stub"          # "llm_check" | "stub"

    @property
    def share_of_voice(self) -> float:
        """Porcentaje de menciones vs competencia."""
        if not self.query_results:
            return 0.0
        total_competitor_mentions = sum(
            len(r.competitors_mentioned) for r in self.query_results
        )
        total = self.total_mentions + total_competitor_mentions
        if total == 0:
            return 0.0
        return round(self.total_mentions / total, 2)


class LLMMentionChecker:
    """
    Consulta LLMs para detectar menciones del hotel en recomendaciones.

    REGLA: OpenAI SIEMPRE via OpenRouter. NUNCA usar openai SDK directo.

    Providers (orden de prioridad):
    1. OpenRouter (principal, ~$0.01-0.03/query)
    2. Gemini (gratis, free tier generoso)
    3. Perplexity (mejor para IAO porque cita fuentes, ~$0.02-0.05/query)
    """

    PROBING_QUERIES = [
        "Recomiéndame un hotel boutique en {location}",
        "¿Cuál es el mejor hotel para parejas en {location}?",
        "Hoteles con encanto cerca de {landmark}",
        "¿Dónde hospedarse en {location} que tenga buena vista?",
        "Hotel tranquilo para trabajar en {location}",
    ]

    def __init__(self, openrouter_key: Optional[str] = None,
                 gemini_key: Optional[str] = None,
                 perplexity_key: Optional[str] = None):
        """
        Al menos una key requerida. Si todas son None, retorna stub.

        Costo estimado por hotel:
        - OpenRouter: ~$0.01-0.03/query (5 queries = $0.05-0.15)
        - Gemini: GRATIS (free tier generoso)
        - Perplexity: ~$0.02-0.05/query
        """
        self._openrouter_key = openrouter_key or os.environ.get("OPENROUTER_API_KEY")
        self._gemini_key = gemini_key or os.environ.get("GEMINI_API_KEY")
        self._perplexity_key = perplexity_key or os.environ.get("PERPLEXITY_API_KEY")

        self._available_providers = []
        if self._openrouter_key:
            self._available_providers.append("openrouter")
        if self._gemini_key:
            self._available_providers.append("gemini")
        if self._perplexity_key:
            self._available_providers.append("perplexity")

    @property
    def is_available(self) -> bool:
        """True si al menos un provider tiene API key."""
        return len(self._available_providers) > 0

    def check_mentions(self, hotel_name: str, hotel_url: str,
                       location: str, landmark: str = "") -> LLMReport:
        """
        Ejecuta queries de recomendación y analiza menciones.

        Si no hay API keys, retorna stub con source="stub".
        """
        if not self.is_available:
            return self._build_stub_report(hotel_name, hotel_url, location)

        query_results: List[LLMQueryResult] = []
        providers_used = []

        for template in self.PROBING_QUERIES:
            query = template.format(
                location=location or "Colombia",
                landmark=landmark or location or "Colombia"
            )

            # Try each available provider
            for provider in self._available_providers:
                response = self._query_provider(provider, query)
                if response is None:
                    continue

                parsed = self._parse_mentions(response, hotel_name)
                result = LLMQueryResult(
                    provider=provider,
                    query=query,
                    response_text=response,
                    hotel_mentioned=parsed["mentioned"],
                    mention_context=parsed["context"],
                    ranking_position=parsed["ranking_position"],
                    competitors_mentioned=parsed["competitors"],
                )
                query_results.append(result)

                if provider not in providers_used:
                    providers_used.append(provider)

                # One provider per query is enough
                break

            # Rate limiting: small delay between queries
            time.sleep(0.5)

        # Calculate aggregate metrics
        mentions = [r for r in query_results if r.hotel_mentioned]
        total_mentions = len(mentions)
        queries_tested = len(query_results)
        mention_rate = total_mentions / queries_tested if queries_tested > 0 else 0.0

        rankings = [r.ranking_position for r in mentions if r.ranking_position is not None]
        avg_ranking = sum(rankings) / len(rankings) if rankings else None

        # Calculate mention_score (0-100)
        mention_score = self._calculate_mention_score(
            mention_rate, avg_ranking, total_mentions, queries_tested
        )

        return LLMReport(
            hotel_name=hotel_name,
            hotel_url=hotel_url,
            location=location,
            queries_tested=queries_tested,
            total_mentions=total_mentions,
            avg_ranking=avg_ranking,
            mention_rate=mention_rate,
            providers_used=providers_used,
            query_results=query_results,
            mention_score=mention_score,
            source="llm_check",
        )

    def _query_provider(self, provider: str, query: str) -> Optional[str]:
        """Dispatch query to the appropriate provider."""
        try:
            if provider == "openrouter":
                return self._query_openrouter(query)
            elif provider == "gemini":
                return self._query_gemini(query)
            elif provider == "perplexity":
                return self._query_perplexity(query)
        except Exception as e:
            logger.warning(f"LLM query failed for {provider}: {e}")
            return None

    def _query_openrouter(self, query: str) -> Optional[str]:
        """
        Llama OpenRouter API. NUNCA usar openai SDK directo.
        Usa google/gemini-2.0-flash-001 como modelo barato.
        """
        import requests

        headers = {
            "Authorization": f"Bearer {self._openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://iah-cli.dev",
            "X-Title": "IAH-CLI IAO Checker",
        }
        payload = {
            "model": "google/gemini-2.0-flash-001",
            "messages": [{"role": "user", "content": query}],
            "max_tokens": 1024,
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _query_gemini(self, query: str) -> Optional[str]:
        """Llama Gemini API directo (no via OpenRouter)."""
        import requests

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/gemini-2.0-flash:generateContent?key={self._gemini_key}"
        )
        payload = {
            "contents": [{"parts": [{"text": query}]}],
            "generationConfig": {"maxOutputTokens": 1024},
        }

        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def _query_perplexity(self, query: str) -> Optional[str]:
        """Llama Perplexity API. Mejor para IAO porque cita fuentes."""
        import requests

        headers = {
            "Authorization": f"Bearer {self._perplexity_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "sonar",
            "messages": [{"role": "user", "content": query}],
            "max_tokens": 1024,
        }

        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _parse_mentions(self, response: str, hotel_name: str) -> dict:
        """
        Detecta si el hotel fue mencionado y en qué contexto.

        Estrategia:
        1. Buscar hotel_name (case-insensitive) en la respuesta
        2. Extraer contexto (50 chars alrededor de la mención)
        3. Detectar posición en listas numeradas
        4. Identificar competidores mencionados
        """
        response_lower = response.lower()
        hotel_lower = hotel_name.lower()

        # Check if hotel is mentioned
        mentioned = hotel_lower in response_lower

        # Extract mention context
        context = ""
        if mentioned:
            idx = response_lower.find(hotel_lower)
            start = max(0, idx - 50)
            end = min(len(response), idx + len(hotel_name) + 50)
            context = response[start:end].strip()

        # Detect ranking position (numbered lists like "1. Hotel X")
        ranking_position = None
        if mentioned:
            # Pattern: "N. " or "N) " followed by hotel name
            patterns = [
                rf'(\d+)\.\s*.*?{re.escape(hotel_name)}',
                rf'(\d+)\)\s*.*?{re.escape(hotel_name)}',
            ]
            for pattern in patterns:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    ranking_position = int(match.group(1))
                    break

        # Detect competitors (other hotel names mentioned)
        competitors = []
        # Simple heuristic: look for capitalized names near "hotel" keyword
        hotel_pattern = r'(?:Hotel|hotel|HOTEL)\s+([A-Z][a-zA-ZáéíóúñÁÉÍÓÚÑ]+(?:\s+[A-Z][a-zA-ZáéíóúñÁÉÍÓÚÑ]+)?)'
        for match in re.finditer(hotel_pattern, response):
            name = match.group(1).strip()
            if name.lower() != hotel_lower and len(name) > 2:
                competitors.append(name)

        return {
            "mentioned": mentioned,
            "context": context,
            "ranking_position": ranking_position,
            "competitors": list(set(competitors)),  # deduplicate
        }

    def _calculate_mention_score(self, mention_rate: float,
                                  avg_ranking: Optional[float],
                                  total_mentions: int,
                                  queries_tested: int) -> int:
        """
        Calcula score 0-100 basado en menciones LLM.

        Componentes:
        - mention_rate (50pts): % de queries donde fue mencionado
        - ranking_bonus (30pts): bonus por posición alta en listas
        - consistency_bonus (20pts): bonus por ser mencionado en múltiples queries
        """
        if queries_tested == 0:
            return 0

        # Base: mention rate (0-50pts)
        rate_score = int(mention_rate * 50)

        # Ranking bonus (0-30pts): mejor ranking = más puntos
        ranking_score = 0
        if avg_ranking is not None:
            if avg_ranking <= 1:
                ranking_score = 30
            elif avg_ranking <= 2:
                ranking_score = 25
            elif avg_ranking <= 3:
                ranking_score = 20
            elif avg_ranking <= 5:
                ranking_score = 15
            else:
                ranking_score = 10

        # Consistency bonus (0-20pts)
        consistency_score = 0
        if total_mentions >= 4:
            consistency_score = 20
        elif total_mentions >= 3:
            consistency_score = 15
        elif total_mentions >= 2:
            consistency_score = 10
        elif total_mentions >= 1:
            consistency_score = 5

        return min(100, rate_score + ranking_score + consistency_score)

    def _build_stub_report(self, hotel_name: str, hotel_url: str,
                            location: str) -> LLMReport:
        """Retorna reporte stub cuando no hay API keys."""
        return LLMReport(
            hotel_name=hotel_name,
            hotel_url=hotel_url,
            location=location,
            queries_tested=0,
            total_mentions=0,
            avg_ranking=None,
            mention_rate=0.0,
            providers_used=[],
            mention_score=0,
            source="stub",
        )
