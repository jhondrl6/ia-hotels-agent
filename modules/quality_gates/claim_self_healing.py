"""Self-Healing Loop para CG-CLAIM-VS-EVIDENCE — FASE-SR-C (D-PF2, L-SR5).

Cierra el ciclo "detecta, loggea y publica igual" (L-SR5): cuando el gate
comercial ``CG-CLAIM-VS-EVIDENCE`` detecta un claim factualmente falso
(p.ej. "no aparece" cuando GBP confirma place_found=True, rating >= 4.0),
este módulo REGENERA el documento usando el ``suggestion`` del gate como
restricción obligatoria, RE-VALIDA los gates comerciales sobre el documento
regenerado y, si el claim persiste tras 1 reintento, ESCALA a BLOCKED real
(el pipeline en main.py retiene los documentos cliente y aborta el ZIP).

Guard anti-bucle: máximo 1 regeneración por instancia (``MAX_REGENERATIONS``).
La segunda llamada a ``heal()`` no reescribe ni re-valida: retorna
``escalated_to_blocked`` directamente.

Trazabilidad (criterio T2): ``ClaimHealingResult.status`` distingue
``resolved_by_regeneration`` (2ª evaluación sin bloqueo del claim) de
``escalated_to_blocked`` (persistencia tras el reintento).

Estrategias de regeneración (restricción = ``suggestion`` del gate):
- ``traceable_claim``: la oración factual de invisibilidad del hotel se
  reemplaza por el claim trazable textual del ``suggestion`` del gate
  (preservando prefijos de lista/etiqueta/tabla y puntuación final).
- ``instruction_neutralized``: oraciones de autochequeo/instrucción al lector
  ("busque su hotel y anote qué información no aparece") no son claims sobre
  el hotel; se neutraliza la frase con un sinónimo sin patrón de claim
  ("falta") preservando la instrucción.

La re-validación es el árbitro: el documento regenerado se considera corregido
solo si la 2ª evaluación no produce bloqueos de CG-CLAIM-VS-EVIDENCE.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import re

from modules.quality_gates.commercial_gate import (
    CLAIM_VS_EVIDENCE_RE,
    CONDITIONAL_MARKERS_RE,
    CommercialGateReport,
)

# ──────────────────────────────────────────────────────────────
# Estados de trazabilidad del loop
# ──────────────────────────────────────────────────────────────

STATUS_NO_NEEDED = "no_needed"
STATUS_RESOLVED = "resolved_by_regeneration"
STATUS_ESCALATED = "escalated_to_blocked"

GATE_ID_CLAIM_VS_EVIDENCE = "CG-CLAIM-VS-EVIDENCE"

# ──────────────────────────────────────────────────────────────
# Patrones de regeneración
# ──────────────────────────────────────────────────────────────

# Extrae la frase del claim desde el ``message`` del gate:
# 'El documento dice "no aparece" (factual) pero place_found=True...'
_CLAIM_PHRASE_FROM_MESSAGE = re.compile(r'"([^"]+)"\s*\(factual\)')

# Extrae el claim trazable desde el ``suggestion`` del gate:
# 'Cambiar absolutos por claims trazables: "Google sí lo encuentra, ..."'
_TRACEABLE_CLAIM_FROM_SUGGESTION = re.compile(r'claims trazables:\s*"([^"]+)"')

# Fallback trazable si el suggestion no provee el texto entrecomillado.
# Contrato probado en tests: el suggestion real del gate SÍ lo provee.
_FALLBACK_TRACEABLE_CLAIM = (
    "Google sí lo encuentra, pero su ficha/web tienen fricciones "
    "que desvían reservas directas."
)

# Oraciones de autochequeo/instrucción al lector (no son claims sobre el
# hotel): "busque su hotel y anote qué información no aparece".
_INSTRUCTION_MARKERS = re.compile(
    r'usted\s+mismo|anote|busque\s+su\s+hotel|verifique|pruebe|'
    r'haga\s+la\s+prueba|revise\s+su',
    re.IGNORECASE,
)

# Sujetos cuya visibilidad queda contrastada por la evidencia GBP: la
# oración factual de invisibilidad sobre estos sujetos contradice
# place_found=True/rating>=4.0 y se reemplaza por el claim trazable.
_GBP_SUBJECT_MARKERS = re.compile(
    r'google|gbp|b[uú]squeda|ficha|perfil|maps',
    re.IGNORECASE,
)

# Sinónimos neutrales (sin patrón de claim) para frases que NO son claims
# de visibilidad del hotel contrastable con GBP: instrucciones al lector y
# claims sobre otros sujetos (p.ej. un elemento del sitio). Clave en
# minúsculas; el reemplazo preserva la capitalización inicial de la frase.
_NEUTRAL_SYNONYMS = {
    "no aparece": "falta",
    "no figura": "falta",
    "no está en google": "falta en google",
    "no esta en google": "falta en google",
    "invisible en búsquedas": "difícil de hallar en búsquedas",
    "invisible en busquedas": "difícil de hallar en búsquedas",
}

# Split de oraciones conservando separadores (misma frontera que el gate:
# [.!?\n]). Cada match es "oración + puntuación/salto final".
_SENTENCE_RE = re.compile(r'[^.!?\n]+[.!?\n]*')

# Prefijos estructurales a preservar en el reemplazo trazable:
# viñetas/numeración de lista (requieren espacio tras el marcador para no
# consumir énfasis markdown como "*texto"), etiquetas en negritas/backticks
# y celdas de tabla previas a la oración ofensiva.
_LIST_PREFIX = re.compile(r'^\s*(?:[-*+]|\d+[.)])\s+')
_LABEL_PREFIX = re.compile(r'^\s*(?:\*\*[^*\n]{1,80}\*\*|`[^`\n]{1,80}`):?\s*')
_TABLE_PREFIX = re.compile(r'^(?:\s*\|[^|\n]*)+\|\s*')

# Puntuación/cierre final a preservar en el reemplazo trazable
# (incluye celda de tabla cerrada "|").
_TRAILING_PUNCT = re.compile(r'[\s|.!?\n]+$')


# ──────────────────────────────────────────────────────────────
# Data Classes
# ──────────────────────────────────────────────────────────────

@dataclass
class ClaimHealingAction:
    """Acción de regeneración aplicada a una oración ofensiva."""
    strategy: str  # "traceable_claim" | "instruction_neutralized"
    original_sentence: str
    healed_sentence: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy,
            "original_sentence": self.original_sentence[:200],
            "healed_sentence": self.healed_sentence[:200],
        }


@dataclass
class ClaimHealingResult:
    """Resultado del self-healing loop para trazabilidad del run."""
    status: str
    attempts: int = 0
    max_attempts: int = 1
    resolved_gates: List[str] = field(default_factory=list)
    escalated_gates: List[str] = field(default_factory=list)
    actions: List[ClaimHealingAction] = field(default_factory=list)
    healed_text: str = ""
    revalidated_report: Optional[CommercialGateReport] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "resolved_gates": list(self.resolved_gates),
            "escalated_gates": list(self.escalated_gates),
            "actions": [a.to_dict() for a in self.actions],
        }


# ──────────────────────────────────────────────────────────────
# Self-Healer
# ──────────────────────────────────────────────────────────────

class ClaimSelfHealer:
    """Loop self-healing D-PF2 para CG-CLAIM-VS-EVIDENCE (máx 1 regeneración).

    Uso:
        healer = ClaimSelfHealer()
        healing = healer.heal(
            document_text=doc,
            report=commercial_report,
            revalidate_fn=lambda text: validator.validate_diagnostic(...),
        )
        if healing.status == STATUS_RESOLVED:
            doc = healing.healed_text
        elif healing.status == STATUS_ESCALATED:
            ...  # escalar a BLOCKED real (main.py retiene docs y aborta ZIP)
    """

    GATE_ID = GATE_ID_CLAIM_VS_EVIDENCE
    MAX_REGENERATIONS = 1

    def __init__(self, max_regenerations: int = MAX_REGENERATIONS):
        self._max_attempts = max_regenerations
        self._attempts = 0

    @property
    def attempts(self) -> int:
        return self._attempts

    def heal(
        self,
        document_text: str,
        report: CommercialGateReport,
        revalidate_fn: Callable[[str], CommercialGateReport],
    ) -> ClaimHealingResult:
        """Ejecuta el ciclo regenerar → re-validar (máx 1 regeneración).

        Args:
            document_text: Texto del documento con el claim ofensivo.
            report: Reporte comercial de la 1ª evaluación (debe contener el
                fallo BLOCKING de CG-CLAIM-VS-EVIDENCE).
            revalidate_fn: Función de re-validación de gates comerciales sobre
                un texto candidato (mismos parámetros que la 1ª evaluación).
        """
        claim_failures = [
            r for r in report.blocking_failures if r.gate_id == self.GATE_ID
        ]
        if not claim_failures:
            return ClaimHealingResult(
                status=STATUS_NO_NEEDED,
                attempts=self._attempts,
                max_attempts=self._max_attempts,
            )

        # Guard anti-bucle: nunca más de MAX_REGENERATIONS regeneraciones.
        if self._attempts >= self._max_attempts:
            return ClaimHealingResult(
                status=STATUS_ESCALATED,
                attempts=self._attempts,
                max_attempts=self._max_attempts,
                escalated_gates=[r.gate_id for r in claim_failures],
                healed_text=document_text,
            )

        traceable_claim = self._extract_traceable_claim(
            claim_failures[0].suggestion
        )
        healed_text, actions = self._rewrite_document(
            document_text, traceable_claim
        )

        self._attempts += 1
        revalidated = revalidate_fn(healed_text)

        still_failing = [
            r for r in revalidated.blocking_failures if r.gate_id == self.GATE_ID
        ]
        if still_failing:
            # Persistencia tras el reintento → escalar a BLOCKED real.
            return ClaimHealingResult(
                status=STATUS_ESCALATED,
                attempts=self._attempts,
                max_attempts=self._max_attempts,
                escalated_gates=[r.gate_id for r in still_failing],
                actions=actions,
                healed_text=healed_text,
                revalidated_report=revalidated,
            )

        return ClaimHealingResult(
            status=STATUS_RESOLVED,
            attempts=self._attempts,
            max_attempts=self._max_attempts,
            resolved_gates=[self.GATE_ID],
            actions=actions,
            healed_text=healed_text,
            revalidated_report=revalidated,
        )

    # ── Extracción de la restricción (suggestion del gate) ───

    def _extract_traceable_claim(self, suggestion: str) -> str:
        """Extrae el claim trazable del ``suggestion`` del gate."""
        m = _TRACEABLE_CLAIM_FROM_SUGGESTION.search(suggestion or "")
        if m:
            return m.group(1).strip()
        return _FALLBACK_TRACEABLE_CLAIM

    def extract_claim_phrase(self, message: str) -> Optional[str]:
        """Extrae la frase ofensiva del ``message`` del gate (trazabilidad)."""
        m = _CLAIM_PHRASE_FROM_MESSAGE.search(message or "")
        return m.group(1) if m else None

    # ── Regeneración del documento ───────────────────────────

    def _rewrite_document(
        self, document_text: str, traceable_claim: str
    ) -> tuple:
        """Reescribe TODAS las oraciones factuales ofensivas del documento.

        A diferencia del gate (que se detiene en el primer match), el healer
        debe corregir todas las ocurrencias para que la re-validación pase.
        """
        actions: List[ClaimHealingAction] = []
        healed_lines = []
        for line in document_text.split("\n"):
            healed_lines.append(
                self._rewrite_line(line, traceable_claim, actions)
            )
        return "\n".join(healed_lines), actions

    def _rewrite_line(
        self,
        line: str,
        traceable_claim: str,
        actions: List[ClaimHealingAction],
    ) -> str:
        if not CLAIM_VS_EVIDENCE_RE.search(line):
            return line
        parts = []
        for m in _SENTENCE_RE.finditer(line):
            parts.append(
                self._rewrite_sentence(
                    m.group(0), traceable_claim, actions
                )
            )
        return "".join(parts)

    def _rewrite_sentence(
        self,
        sentence: str,
        traceable_claim: str,
        actions: List[ClaimHealingAction],
    ) -> str:
        claim_match = CLAIM_VS_EVIDENCE_RE.search(sentence)
        if not claim_match:
            return sentence
        # Oración condicional → el gate no la marca (FASE-C N11): intacta.
        if CONDITIONAL_MARKERS_RE.search(sentence):
            return sentence
        # Instrucción al lector → sinónimo neutral (preserva la instrucción).
        if _INSTRUCTION_MARKERS.search(sentence):
            healed = self._neutralize_claim_phrase(sentence)
            if healed != sentence:
                actions.append(ClaimHealingAction(
                    strategy="instruction_neutralized",
                    original_sentence=sentence.strip(),
                    healed_sentence=healed.strip(),
                ))
            return healed
        # Claim de visibilidad del hotel contrastable con GBP → claim
        # trazable textual del suggestion del gate (restricción obligatoria).
        if _GBP_SUBJECT_MARKERS.search(sentence):
            healed = self._replace_with_traceable_claim(
                sentence, traceable_claim
            )
            actions.append(ClaimHealingAction(
                strategy="traceable_claim",
                original_sentence=sentence.strip(),
                healed_sentence=healed.strip(),
            ))
            return healed
        # Claim sobre otro sujeto (p.ej. elemento del sitio) → sinónimo
        # neutral: elimina el patrón de claim sin inventar visibilidad.
        healed = self._neutralize_claim_phrase(sentence)
        if healed != sentence:
            actions.append(ClaimHealingAction(
                strategy="instruction_neutralized",
                original_sentence=sentence.strip(),
                healed_sentence=healed.strip(),
            ))
        return healed

    def _replace_with_traceable_claim(
        self, sentence: str, traceable_claim: str
    ) -> str:
        """Reemplaza la oración por el claim trazable preservando estructura.

        Conserva: prefijo de lista ("- "), etiqueta ("**X**: "), celdas de
        tabla previas ("| a | b |") y puntuación/cierre final (".", "|").
        """
        prefix = ""
        m = _TABLE_PREFIX.match(sentence)
        if m:
            prefix += m.group(0)
        else:
            m = _LIST_PREFIX.match(sentence)
            if m:
                prefix += m.group(0)
            m = _LABEL_PREFIX.match(sentence[len(prefix):])
            if m:
                prefix += m.group(0)

        tail = ""
        m = _TRAILING_PUNCT.search(sentence)
        if m:
            tail = m.group(0)

        core_end = len(sentence) - len(tail)
        core_start = len(prefix)
        if core_end <= core_start:
            # Oración degenerada: solo prefijo/puntuación → sinónimo neutral.
            return self._neutralize_claim_phrase(sentence)
        return prefix + traceable_claim + tail

    def _neutralize_claim_phrase(self, sentence: str) -> str:
        """Reemplaza frases de claim por sinónimos sin patrón de claim.

        Preserva la capitalización inicial de la frase reemplazada.
        """
        lowered = sentence.lower()
        for phrase, synonym in _NEUTRAL_SYNONYMS.items():
            idx = lowered.find(phrase)
            while idx != -1:
                original = sentence[idx: idx + len(phrase)]
                replacement = synonym
                if original[:1].isupper():
                    replacement = synonym[:1].upper() + synonym[1:]
                sentence = (
                    sentence[:idx] + replacement + sentence[idx + len(phrase):]
                )
                lowered = sentence.lower()
                idx = lowered.find(phrase, idx + len(replacement))
        return sentence
