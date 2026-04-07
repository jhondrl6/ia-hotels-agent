"""Document Quality Gate - Validates commercial documents before client delivery.

Detects blocking issues (default placeholders, duplicate currency, zero confidence)
and warnings (mixed language, generic AI phrases, missing contact info) to prevent
low-quality documents from reaching hotelier clients.

Usage:
    from modules.postprocessors.document_quality_gate import DocumentQualityGate
    gate = DocumentQualityGate()
    result = gate.validate_document(content, "diagnostico", hotel_data)
    if not result.passed:
        for issue in result.issues:
            if issue.severity == "blocker":
                print(f"BLOCKER: {issue.message}")
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import re


# Common Portuguese words that appear in Spanish texts due to LLM confusion
PORTUGUESE_WORDS = [
    "passo", "protecao", "proteção", "proxima", "proximo",
    "complicated", "atendimento", "hospede", "hóspede",
    "disponibilidade", "reserva", "servicos", "serviços",
]

# Common English words in hotel context that should be Spanish
ENGLISH_HOTEL_WORDS = [
    "guests", "booking", "checkin", "checkout", "amenities",
    "hospitality", "reservations", "availability", "staff",
]

# Portuguese to Spanish replacements
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
    "reserva": "reserva",  # Same in both but flagged as warning
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

# Generic AI phrases that suggest boilerplate content
GENERIC_AI_PHRASES = [
    "oportunidades de crecimiento en presencia digital",
    "cada vez mas competitivo",
    "en la era digital actual",
    "es fundamental tener una presencia",
    "mundo digital de hoy",
    "entorno altamente competitivo",
    "panorama digital",
    "cabe destacar",
    "es importante senalar",
]


@dataclass
class DocumentQualityIssue:
    """A single quality issue found in a commercial document."""
    check_name: str       # e.g., "placeholder_region", "duplicate_currency"
    severity: str         # "blocker" or "warning"
    line_number: int      # Line where issue was found (1-indexed)
    detected_value: str   # The actual text that triggered the issue
    message: str          # Human-readable description
    auto_fixable: bool    # True if ContentScrubber can fix it


@dataclass
class DocumentQualityResult:
    """Result of validating a commercial document."""
    passed: bool
    score: float          # 0.0 - 1.0 (1.0 = no issues)
    issues: List[DocumentQualityIssue]
    document_type: str    # "diagnostico", "propuesta", "asset"
    blockers_count: int = 0
    warnings_count: int = 0

    def __post_init__(self):
        self.blockers_count = sum(1 for i in self.issues if i.severity == "blocker")
        self.warnings_count = sum(1 for i in self.issues if i.severity == "warning")


class DocumentQualityGate:
    """Validates commercial documents before client delivery.

    Runs blocker checks (fail = document not safe for client)
    and warning checks (degradation noted but document still usable).
    """

    BLOCKER_CHECKS = [
        "placeholder_region",       # "default" where city name should be
        "duplicate_currency",        # "COP COP"
        "zero_confidence",           # "0% confianza" in commercial doc
    ]

    WARNING_CHECKS = [
        "mixed_language",            # Portuguese or English in Spanish doc
        "generic_ai_phrases",        # Typical LLM boilerplate
    ]

    def validate_document(
        self,
        content: str,
        doc_type: str,
        hotel_data: Optional[Dict[str, Any]] = None,
    ) -> DocumentQualityResult:
        """Run all quality checks on a document.

        Args:
            content: The document text to validate.
            doc_type: "diagnostico", "propuesta", or "asset".
            hotel_data: Optional hotel data for context.

        Returns:
            DocumentQualityResult with passed=False if any blocker found.
        """
        issues: List[DocumentQualityIssue] = []

        # Blocker checks
        issues.extend(self._check_placeholder_region(content))
        issues.extend(self._check_duplicate_currency(content))
        issues.extend(self._check_zero_confidence(content, doc_type))

        # Warning checks
        issues.extend(self._check_mixed_language(content))
        issues.extend(self._check_generic_ai_phrases(content))

        has_blockers = any(i.severity == "blocker" for i in issues)

        # Score: deduct points for issues
        score = 1.0
        for issue in issues:
            if issue.severity == "blocker":
                score -= 0.2
            else:
                score -= 0.05
        score = max(0.0, score)

        return DocumentQualityResult(
            passed=not has_blockers,
            score=round(score, 2),
            issues=issues,
            document_type=doc_type,
        )

    # ------------------------------------------------------------------
    # BLOCKER checks
    # ------------------------------------------------------------------
    def _check_placeholder_region(self, content: str) -> List[DocumentQualityIssue]:
        """Detect \"default\" used as a region/city placeholder."""
        issues: List[DocumentQualityIssue] = []
        # Match "en default", "region de default", "de default" in regional context
        pattern = re.compile(r'\b(?:en|region de|de)\s+default\b', re.IGNORECASE)
        for i, line in enumerate(content.split('\n'), 1):
            match = pattern.search(line)
            if match:
                issues.append(DocumentQualityIssue(
                    check_name="placeholder_region",
                    severity="blocker",
                    line_number=i,
                    detected_value=match.group(0),
                    message=f'Línea {i}: "default" usado como región. Debería ser la ciudad real del hotel.',
                    auto_fixable=True,
                ))
        return issues

    def _check_duplicate_currency(self, content: str) -> List[DocumentQualityIssue]:
        """Detect \"COP COP\" or duplicate currency markers."""
        issues: List[DocumentQualityIssue] = []
        pattern = re.compile(r'(COP)\s+\1', re.IGNORECASE)
        for i, line in enumerate(content.split('\n'), 1):
            match = pattern.search(line)
            if match:
                issues.append(DocumentQualityIssue(
                    check_name="duplicate_currency",
                    severity="blocker",
                    line_number=i,
                    detected_value=match.group(0),
                    message=f'Línea {i}: Moneda duplicada "COP COP". Debería ser solo "COP".',
                    auto_fixable=True,
                ))
        return issues

    def _check_zero_confidence(
        self, content: str, doc_type: str
    ) -> List[DocumentQualityIssue]:
        """Detect \"0% confianza\" or equivalent in commercial docs."""
        if doc_type not in ("diagnostico", "propuesta"):
            return []
        issues: List[DocumentQualityIssue] = []
        pattern = re.compile(r'0\s*%\s*(?:de\s+)?confianza', re.IGNORECASE)
        for i, line in enumerate(content.split('\n'), 1):
            match = pattern.search(line)
            if match:
                issues.append(DocumentQualityIssue(
                    check_name="zero_confidence",
                    severity="blocker",
                    line_number=i,
                    detected_value=match.group(0),
                    message=f'Línea {i}: Confianza del 0% destruye credibilidad comercial.',
                    auto_fixable=True,
                ))
        return issues

    # ------------------------------------------------------------------
    # WARNING checks
    # ------------------------------------------------------------------
    def _check_mixed_language(self, content: str) -> List[DocumentQualityIssue]:
        """Detect Portuguese or English words in Spanish document."""
        issues: List[DocumentQualityIssue] = []
        content_lower = content.lower()

        # Check Portuguese
        for word in PORTUGUESE_WORDS:
            if word.lower() in content_lower:
                # Find first occurrence line
                for i, line in enumerate(content.split('\n'), 1):
                    if word.lower() in line.lower():
                        issues.append(DocumentQualityIssue(
                            check_name="mixed_language",
                            severity="warning",
                            line_number=i,
                            detected_value=word,
                            message=f'Reemplazo: {word} -> {PT_TO_ES.get(word, word)}',
                            auto_fixable=True,
                        ))
                        break

        # Check English (hotel context)
        for word in ENGLISH_HOTEL_WORDS:
            # Word boundary check: whole word only
            wb_pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            for i, line in enumerate(content.split('\n'), 1):
                if wb_pattern.search(line):
                    issues.append(DocumentQualityIssue(
                        check_name="mixed_language",
                        severity="warning",
                        line_number=i,
                        detected_value=word,
                        message=f'Palabra inglés: {word} -> {EN_TO_ES.get(word, word)}',
                        auto_fixable=True,
                    ))
                    break

        return issues

    def _check_generic_ai_phrases(self, content: str) -> List[DocumentQualityIssue]:
        """Detect generic AI boilerplate phrases."""
        issues: List[DocumentQualityIssue] = []
        content_lower = content.lower()
        for phrase in GENERIC_AI_PHRASES:
            if phrase.lower() in content_lower:
                for i, line in enumerate(content.split('\n'), 1):
                    if phrase.lower() in line.lower():
                        issues.append(DocumentQualityIssue(
                            check_name="generic_ai_phrases",
                            severity="warning",
                            line_number=i,
                            detected_value=phrase,
                            message=f'frase genérica de AI detectada.',
                            auto_fixable=False,
                        ))
                        break
        return issues
