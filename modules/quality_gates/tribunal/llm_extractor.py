"""Interfaz de extracción LLM para el tribunal de certificación.

Protocolo de extracción de promesas verbales desde texto de propuesta.
El extractor SOLO propone; nunca emite veredicto. El veredicto lo aplica
la capa determinista del revisor, y el Juez lo certifica.

Patrón que T4-B replica para extracción de claims de honestidad.
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable


@dataclass
class VerbalPromise:
    """Una promesa encontrada en lenguaje natural."""
    text: str
    service_hint: str
    location: str
    confidence: float

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "service_hint": self.service_hint,
            "location": self.location,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VerbalPromise":
        return cls(
            text=data["text"],
            service_hint=data["service_hint"],
            location=data["location"],
            confidence=data["confidence"],
        )


@runtime_checkable
class PromiseExtractor(Protocol):
    """Protocolo de extracción de promesas verbales desde texto de propuesta."""

    def extract_verbal_promises(self, proposal_text: str) -> list[VerbalPromise]:
        """Extrae promesas verbales del texto de propuesta.

        Args:
            proposal_text: Texto completo de la propuesta comercial.

        Returns:
            Lista de VerbalPromise encontradas.
        """
        ...


class LLMPromiseExtractor:
    """Implementación default: usa el LLM del pipeline con cache.

    El cache evita re-llamar al LLM para el mismo texto. La clave del cache
    es el hash SHA256 del texto de entrada.
    """

    EXTRACTION_PROMPT = """Eres un extractor de promesas verbales de una propuesta comercial para hoteles.

Tu tarea: identificar cada promesa verbal de servicio o entregable que aparezca en el texto.

Para cada promesa, extrae:
1. text: texto literal de la promesa (cita textual)
2. service_hint: servicio al que parece referirse (ej: "whatsapp_bot", "faq_page", "schema_hotel", "local_content")
3. location: sección de la propuesta donde aparece (ej: "Introducción", "Alcance del Proyecto", "Entregables")
4. confidence: confianza de la extracción (0.0-1.0)

Responde SOLO con JSON válido, sin markdown, sin explicación adicional:
[
  {
    "text": "...",
    "service_hint": "...",
    "location": "...",
    "confidence": 0.9
  }
]

Si no hay promesas, responde: []

Texto de propuesta:
"""

    def __init__(self, provider=None, cache_dir: Path | None = None):
        """Inicializa el extractor.

        Args:
            provider: Instancia de LLMProvider (si es None, usa ProviderAdapter).
            cache_dir: Directorio de cache (si es None, usa .cache/tribunal/).
        """
        self.provider = provider
        self.cache_dir = cache_dir or Path(".cache/tribunal")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def extract_verbal_promises(self, proposal_text: str) -> list[VerbalPromise]:
        """Extrae promesas verbales del texto de propuesta.

        Usa cache para evitar re-llamar al LLM con el mismo texto.
        """
        cache_key = self._compute_cache_key(proposal_text)
        cached = self._load_from_cache(cache_key)
        if cached is not None:
            return cached

        if self.provider is None:
            from modules.providers.llm_provider import ProviderAdapter
            adapter = ProviderAdapter()
            self.provider = adapter.provider

        prompt = self.EXTRACTION_PROMPT + proposal_text
        response_text = self.provider.chat_completion(
            prompt,
            max_tokens=2000,
            temperature=0.1,
        )

        promises = self._parse_response(response_text)
        self._save_to_cache(cache_key, promises)
        return promises

    def _compute_cache_key(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _cache_path(self, cache_key: str) -> Path:
        return self.cache_dir / f"{cache_key}.json"

    def _load_from_cache(self, cache_key: str) -> list[VerbalPromise] | None:
        path = self._cache_path(cache_key)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [VerbalPromise.from_dict(d) for d in data]
        except (json.JSONDecodeError, OSError, KeyError):
            return None

    def _save_to_cache(self, cache_key: str, promises: list[VerbalPromise]) -> None:
        path = self._cache_path(cache_key)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in promises], f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def _parse_response(self, response_text: str) -> list[VerbalPromise]:
        """Parsea la respuesta del LLM como JSON de promesas."""
        response_text = response_text.strip()
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            start_idx = 1 if lines[0].strip().startswith("```") else 0
            end_idx = -1 if lines[-1].strip() == "```" else len(lines)
            response_text = "\n".join(lines[start_idx:end_idx]).strip()

        try:
            data = json.loads(response_text)
            if not isinstance(data, list):
                return []
            return [VerbalPromise.from_dict(item) for item in data if self._is_valid_promise(item)]
        except json.JSONDecodeError:
            return []

    def _is_valid_promise(self, item: dict) -> bool:
        """Valida que un dict tenga la estructura de VerbalPromise."""
        required = {"text", "service_hint", "location", "confidence"}
        if not required.issubset(item.keys()):
            return False
        if not isinstance(item["text"], str) or not item["text"].strip():
            return False
        if not isinstance(item["confidence"], (int, float)):
            return False
        return True


class MockPromiseExtractor:
    """Para tests: retorna promesas fijas sin llamar LLM.

    Útil para probar la lógica determinista del revisor sin dependencia
    de LLM real.
    """

    def __init__(self, promises: list[VerbalPromise]):
        """Inicializa con promesas fijas.

        Args:
            promises: Lista de VerbalPromise a retornar.
        """
        self.promises = promises

    def extract_verbal_promises(self, proposal_text: str) -> list[VerbalPromise]:
        """Retorna las promesas fijas (ignora proposal_text)."""
        return self.promises
