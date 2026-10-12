"""evidence_tier — la única precedencia del tier, compartida por el Juez y Bot 4.

Curación de N6 (AC11): los dos lectores del mismo dato tenían reglas invertidas. El
Juez leía ``financial_scenarios`` → ``MANIFEST`` → ``"C"`` y Bot 4 leía ``MANIFEST`` →
``financial_scenarios`` → ``"UNKNOWN"``. Con los dos artefactos en desacuerdo Bot 4 se
silenciaba (``UNKNOWN`` estaba en la lista que devolvía la lista vacía antes de evaluar)
mientras el Juez aplicaba el primer piso sobre ``C``.

**Precedencia**: la del Juez, por DA-P1.5. ``financial_scenarios_*.json``
(``breakdown.evidence_tier``) es la fuente pre-packaging que ``main.py`` escribe antes del
bloque del tribunal y existe en régimen ZIP-only; ``MANIFEST.json`` es post-packaging y en
ese régimen nunca se descomprime (L-E2E.1), así que priorizarlo era priorizar la fuente
que suele faltar.

**Fallback único**: ``TIER_FALLBACK`` con ``declarado=False``. Se eligió ``"C"`` y no un
sentinel tipo ``UNKNOWN`` porque un tier que nadie declaró no puede certificar la entrega,
y ``"C"`` es justamente el piso que el Juez ya aplicaba; con un sentinel fuera de
``FIRST_FLOOR_TIERS`` el acta diría «sin restricción de primer piso» sobre un veredicto
que solo es condicional por otra razón — texto que describe mal el mecanismo, la familia
de defecto que este plan cura en P6.2. Lo que impide que Bot 4 trate el default como un
tier real es ``declarado``: con ``False`` el check de sobre-presentación **publica su
estado no-evaluable** en vez de callarse, y tampoco emite un CRITICAL fundado en un tier
que ningún artefacto afirmó.

**Rama no certificable**: «MANIFEST y escenarios en desacuerdo» no se certifica con
fixture, porque producción no la genera en régimen ZIP-only y ningún arnés de la casa la
produce (medido 2026-10-12: ``build_dir`` de ``test_honesty_reviewer_fidelidad_salida.py``
nunca pasa ``breakdown=`` y el baseline SalentoReal no trae un MANIFEST descomprimido).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

TIER_FALLBACK = "C"

FUENTE_ESCENARIOS = "escenarios"
FUENTE_MANIFEST = "manifest"
FUENTE_SIN_DECLARACION = "sin-declaracion"

ESCENARIOS_CLAVE_FALSA = "financial_scenarios_*.json"
MANIFEST_CLAVE = "MANIFEST.json → quality_metadata.evidence_tier"


@dataclass(frozen=True)
class EvidenceTierResolution:
    """El tier resuelto, la vía que lo aportó y si un artefacto lo declaró de verdad."""

    tier: str
    fuente: str
    declarado: bool
    descripcion_fuente: str


def _tier_de_escenarios(scenarios: Optional[Mapping]) -> Optional[str]:
    if not isinstance(scenarios, Mapping):
        return None
    breakdown = scenarios.get("breakdown")
    if not isinstance(breakdown, Mapping):
        return None
    tier = breakdown.get("evidence_tier")
    return tier if isinstance(tier, str) and tier else None


def _tier_de_manifest(manifest: Optional[Mapping]) -> Optional[str]:
    if not isinstance(manifest, Mapping):
        return None
    quality = manifest.get("quality_metadata")
    if not isinstance(quality, Mapping):
        return None
    tier = quality.get("evidence_tier")
    return tier if isinstance(tier, str) and tier else None


def resolve_evidence_tier(
    scenarios: Optional[Mapping],
    manifest: Optional[Mapping],
    *,
    scenarios_name: Optional[str] = None,
) -> EvidenceTierResolution:
    """Resuelve ``evidence_tier`` con la precedencia y el fallback de este módulo.

    Recibe los dos dict ya leídos: quien resuelve las rutas sigue siendo cada consumidor
    (el Juez por su glob, Bot 4 por el resolvedor del run), así la unificación es de
    regla de decisión, no de I/O.
    """
    tier = _tier_de_escenarios(scenarios)
    if tier is not None:
        nombre = scenarios_name or ESCENARIOS_CLAVE_FALSA
        return EvidenceTierResolution(
            tier=tier,
            fuente=FUENTE_ESCENARIOS,
            declarado=True,
            descripcion_fuente=f"{nombre} → breakdown.evidence_tier",
        )

    tier = _tier_de_manifest(manifest)
    if tier is not None:
        return EvidenceTierResolution(
            tier=tier,
            fuente=FUENTE_MANIFEST,
            declarado=True,
            descripcion_fuente=MANIFEST_CLAVE,
        )

    return EvidenceTierResolution(
        tier=TIER_FALLBACK,
        fuente=FUENTE_SIN_DECLARACION,
        declarado=False,
        descripcion_fuente=f'sin fuente de tier: fallback declarado "{TIER_FALLBACK}"',
    )
