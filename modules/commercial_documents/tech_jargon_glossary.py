"""Glosario único de jerga técnica → lenguaje de negocio (FASE-SR-G, L27).

Fuente ÚNICA compartida por:
- ``modules/quality_gates/commercial_gate.py`` (gate ``CG-TECH-JARGON``:
  DETECTA estos términos en la vista gerencia).
- Generadores de documentos cliente (``v4_proposal_generator``,
  ``v4_diagnostic_generator``): TRADUCEN la jerga vía ``apply_glossary()``
  antes de validar y publicar (el texto validado == texto publicado, L-SR3).

Lecciones aplicadas:
- L27: el texto de negocio se deriva de una única fuente consumida por
  generador Y gate (nunca hardcodeado en dos sitios).
- L30: nunca comparar/presentar strings de presentación; solo valores
  derivados de la fuente canónica.
- H6.4 (CONTEXT-SALENTOREAL): la jerga detectada al cliente fue
  "Schema, AEO, IAO, Open Graph" y el patrón histórico "sin costo
  (fallback)" (SR-B eliminó sus renders; la entrada permanece como guardia).

Created by FASE-SR-G (SR-PIPELINE-FIXES-2026-08-27).
"""

import re
from typing import Dict, List

# ──────────────────────────────────────────────────────────────
# Términos técnicos prohibidos en la vista gerencia (primeras 6 secciones)
# ──────────────────────────────────────────────────────────────
# Migrado VERBATIM desde commercial_gate.py (era la definición duplicada);
# aquí vive como fuente única gate ↔ generadores.

TECH_JARGON_TERMS: List[str] = [
    "Schema", "AEO", "IAO", "Open Graph", "NAP", "Rich Snippets",
    "schema.org", "JSON-LD", "markup estructurado",
    # PROPUESTA-COMERCIAL FASE-D: términos adicionales
    "OpenRouter", "Perplexity", "Gemini", "GA4_PROPERTY_ID",
    "GSC_SITE_URL", "UTM", "iah-cli", "iahotels.co",
    # FASE-SR-G (H6.4): guardia del patrón histórico de jerga al cliente
    "sin costo (fallback)",
]

# ──────────────────────────────────────────────────────────────
# Mapeo jerga → lenguaje de negocio (consumido por los generadores)
# ──────────────────────────────────────────────────────────────
# Claves = términos que los documentos cliente pueden renderizar. Los
# compuestos ("Schema Hotel", "FAQ Schema") van ANTES que el término
# simple ("Schema"): ``apply_glossary`` reemplaza del más largo al más
# corto. Términos de detección que nunca renderizan al cliente
# (GA4_PROPERTY_ID, GSC_SITE_URL, iahotels.co...) no se mapean.

JARGON_BUSINESS_MAP: Dict[str, str] = {
    # Guardia del patrón histórico (H6.4; renders eliminados en FASE-SR-B)
    "sin costo (fallback)": "incluido sin costo adicional",
    # Compuestos de Schema (antes que el término simple)
    "Schema Hotel": "Ficha del Hotel en Google e IA",
    "Schema Organization": "Perfil de Empresa en Google",
    "Schema FAQ": "Preguntas Frecuentes para Google",
    "FAQ Schema": "Preguntas Frecuentes para Google",
    "schema.org": "el estándar de fichas de Google",
    "Schema": "Ficha técnica",
    # Social / vista previa
    "Open Graph": "Vista previa en redes sociales",
    # Pilares de visibilidad (curva 4 pilares, tablas de scores)
    "AEO": "Respuestas con IA",
    "IAO": "Recomendaciones de IA",
    # Datos de negocio local
    "NAP": "nombre, dirección y teléfono",
    # Formatos / resultados de Google
    "Rich Snippets": "resultados enriquecidos en Google",
    "JSON-LD": "el formato estándar de Google",
    "markup estructurado": "estructura de datos para Google",
    # Proveedores/motores de IA (nombres de producto → categoría de negocio)
    "OpenRouter": "proveedores de IA",
    "Perplexity": "buscadores con IA",
    "Gemini": "asistentes de IA",
    # Fuga de marca interna
    "iah-cli": "la plataforma",
}


def jargon_pattern(term: str) -> str:
    """Patron regex de detección para un término de jerga.

    Fuente única de la SEMÁNTICA de matching (gate y glosario comparten el
    mismo patrón — L-NC10: un solo criterio). Los ``\\b`` solo se anclan en
    los bordes que terminan en carácter de palabra: términos como
    "sin costo (fallback)" terminan en ')' y un ``\\b`` final nunca
    matchearía (transición no-palabra → no-palabra).
    """
    escaped = re.escape(term)
    prefix = r"\b" if (term[:1].isalnum() or term[:1] == "_") else ""
    suffix = r"\b" if (term[-1:].isalnum() or term[-1:] == "_") else ""
    return prefix + escaped + suffix


def apply_glossary(text: str) -> str:
    """Traduce jerga técnica a lenguaje de negocio en ``text``.

    Reemplazos case-insensitive con los mismos patrones de detección del
    gate (``jargon_pattern``), del término más largo al más corto (los
    compuestos ganan sobre el término simple). Idempotente: el texto de
    negocio resultante ya no contiene términos mapeados.

    Args:
        text: Texto del documento cliente (propuesta o diagnóstico).

    Returns:
        Texto con la jerga mapeada traducida; el resto queda intacto.
    """
    if not text:
        return text
    result = text
    for term in sorted(JARGON_BUSINESS_MAP, key=len, reverse=True):
        result = re.sub(
            jargon_pattern(term),
            JARGON_BUSINESS_MAP[term],
            result,
            flags=re.IGNORECASE,
        )
    return result


__all__ = [
    "TECH_JARGON_TERMS",
    "JARGON_BUSINESS_MAP",
    "jargon_pattern",
    "apply_glossary",
]
