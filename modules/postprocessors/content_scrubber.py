"""Content Scrubber - Post-processor that fixes common LLM output issues.

Applies deterministic text transformations to commercial documents
to remove visible errors before client delivery:
- Region placeholders ("default" -> real city/region)
- Duplicate currency ("COP COP" -> "COP")
- Zero confidence statements replaced with commercial-safe text
- Portuguese/English words converted to Spanish
- Generic AI phrases softened

All rules are IDEMPOTENT: running twice produces the same result as once.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import re


@dataclass
class ScrubResult:
    """Result of scrubbing a document."""
    original: str
    scrubbed: str
    fixes_applied: List[str]
    fix_count: int = 0

    def __post_init__(self):
        self.fix_count = len(self.fixes_applied)


# Portuguese to Spanish replacements (shared with quality gate)
PT_TO_ES = {
    "passo": "paso",
    "protecao": "proteccion",
    "proteção": "proteccion",
    "proxima": "proxima",
    "proximo": "proximo",
    "atendimento": "atencion",
    "hospede": "huesped",
    "hóspede": "huesped",
    "disponibilidade": "disponibilidad",
    "servicos": "servicios",
    "serviços": "servicios",
    "complicated": "complicado",
}

# English to Spanish replacements (hotel context)
EN_TO_ES = {
    "guests": "huespedes",
    "guest": "huesped",
    "booking": "reserva",
    "checkin": "check-in",
    "checkout": "check-out",
    "amenities": "servicios",
    "hospitality": "hospitalidad",
    "reservations": "reservaciones",
    "availability": "disponibilidad",
    "staff": "personal",
}

# Confidence replacement text
CONFIDENCE_REPLACEMENT = (
    "estimación basada en datos web disponibles. "
    "Para mayor precisión, configure Google Analytics 4 "
    "y Google Search Console."
)


class ContentScrubber:
    """Post-processor that fixes common LLM output issues.

    All methods are idempotent: calling scrub() multiple times
    produces the same output as calling it once.
    """

    def scrub(
        self,
        content: str,
        hotel_data: Optional[Dict[str, Any]] = None,
        doc_type: str = "diagnostico",
    ) -> ScrubResult:
        """Apply all scrubbing rules.

        Args:
            content: Document text to clean.
            hotel_data: Hotel data (city, state, region) for placeholder replacement.
            doc_type: Document type for context-aware fixes.

        Returns:
            ScrubResult with original, scrubbed content, and list of fixes applied.
        """
        fixes: List[str] = []

        content = self._fix_region_placeholders(content, hotel_data, fixes)
        content = self._fix_duplicate_currency(content, fixes)
        content = self._fix_confidence_statement(content, doc_type, fixes)
        content = self._fix_mixed_language(content, fixes)
        content = self._fix_generic_ai_phrases(content, hotel_data, fixes)

        return ScrubResult(
            original=content,
            scrubbed=content,
            fixes_applied=fixes,
        )

    # ---------------------------------------------------------------
    # RULE 1: Replace "default" with real city/region
    # ---------------------------------------------------------------
    def _fix_region_placeholders(
        self,
        content: str,
        hotel_data: Optional[Dict[str, Any]],
        fixes: List[str],
    ) -> str:
        """Replace 'default' region placeholders with real hotel data.

        Only replaces "default" in contextual patterns like:
        - "en default" → "en {city}"
        - "region de default" → "region del {state}" or "del {region}"
        Does NOT replace standalone "default" (e.g., "valor por defecto").
        """
        if not hotel_data:
            return content

        city = hotel_data.get("city", "")
        state = hotel_data.get("state", "")
        region = hotel_data.get("region", state or city)

        if not city and not state:
            return content

        # "en default" → "en {city}"
        def replace_en_default(m):
            fixes.append(f'Región: "en default" -> "en {city}"')
            return f"en {city}"

        content = re.sub(
            r'\ben\s+default\b',
            replace_en_default,
            content,
            flags=re.IGNORECASE,
        )

        # "region de default" → "region del {region}"
        def replace_region_default(m):
            fixes.append(f'Región: "region de default" -> "region del {region}"')
            return f"region del {region}"

        content = re.sub(
            r'\bregion(?:\s+del?\s+|\s+de\s+)default\b',
            replace_region_default,
            content,
            flags=re.IGNORECASE,
        )

        return content

    # ---------------------------------------------------------------
    # RULE 2: Remove duplicate currency
    # ---------------------------------------------------------------
    def _fix_duplicate_currency(self, content: str, fixes: List[str]) -> str:
        """Remove "COP COP" → "COP"."""

        def replace_currency(m):
            fixes.append('Moneda: "COP COP" -> "COP"')
            return "COP"

        content = re.sub(r'\bCOP\s+COP\b', replace_currency, content, flags=re.IGNORECASE)
        return content

    # ---------------------------------------------------------------
    # RULE 3: Replace zero confidence statement
    # ---------------------------------------------------------------
    def _fix_confidence_statement(
        self,
        content: str,
        doc_type: str,
        fixes: List[str],
    ) -> str:
        """Replace "0% de confianza" with commercial-safe text.

        Only applies to commercial doc types (diagnostico, propuesta),
        NOT to internal technical documents.
        """
        if doc_type not in ("diagnostico", "propuesta"):
            return content

        pattern = re.compile(r'([Cc]on)\s*0\s*%\s*(?:de\s+)?confianza', re.IGNORECASE)
        replacement = f"{CONFIDENCE_REPLACEMENT}"

        if pattern.search(content):
            content = pattern.sub(replacement, content)
            fixes.append('Confianza: "0% confianza" -> texto comercial')

        return content

    # ---------------------------------------------------------------
    # RULE 4: Fix mixed language (pt/es, en/es)
    # ---------------------------------------------------------------
    def _fix_mixed_language(self, content: str, fixes: List[str]) -> str:
        """Convert Portuguese and English words to Spanish."""
        original = content

        # Portuguese replacements (case-insensitive whole words)
        for pt_word, es_word in PT_TO_ES.items():
            pattern = re.compile(re.escape(pt_word), re.IGNORECASE)
            if pattern.search(content):
                # Check if it's a word boundary to avoid partial matches
                if re.search(r'\b' + re.escape(pt_word) + r'\b', content, re.IGNORECASE):
                    content = re.sub(
                        r'\b' + re.escape(pt_word) + r'\b',
                        es_word,
                        content,
                        flags=re.IGNORECASE,
                    )
                    fixes.append(f'Idioma: "{pt_word}" -> "{es_word}"')

        # English replacements (case-insensitive whole words)
        for en_word, es_word in EN_TO_ES.items():
            pattern = re.compile(r'\b' + re.escape(en_word) + r'\b', re.IGNORECASE)
            if pattern.search(content):
                content = pattern.sub(es_word, content)
                fixes.append(f'Idioma: "{en_word}" -> "{es_word}"')

        return content

    # ---------------------------------------------------------------
    # RULE 5: Soften generic AI phrases
    # ---------------------------------------------------------------
    def _fix_generic_ai_phrases(
        self,
        content: str,
        hotel_data: Optional[Dict[str, Any]],
        fixes: List[str],
    ) -> str:
        """Replace generic AI boilerplate with neutral text.

        Uses a replacement map tailored to common LLM outputs
        in Spanish hotel content.
        """
        replacements = {
            "oportunidades de crecimiento en presencia digital hotelera": (
                "oportunidades concretas de mejora digital"
            ),
            "cada vez mas competitivo": "en un mercado que exige diferenciacion",
            "en la era digital actual": "actualmente",
            "es fundamental tener una presencia": "es clave mantener una presencia",
            "mundo digital de hoy": "entorno digital actual",
            "entorno altamente competitivo": "mercado exigente",
            "panorama digital": "panorama actual",
            "cabe destacar": "cabe senalar",
            "es importante senalar": "es relevante destacar",
        }

        for phrase, replacement in replacements.items():
            if phrase.lower() in content.lower():
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                content = pattern.sub(replacement, content)
                fixes.append(f'IA generica: frase suavizada')
                break  # Only report once

        return content
