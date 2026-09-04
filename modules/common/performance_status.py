"""Vocabulario canónico de ``performance.status`` (FASE-H / V11).

El audit (``modules/auditors/v4_comprehensive.py``) produce estos estados, y con
ellos deciden tanto el diagnóstico comercial
(``modules/commercial_documents/v4_diagnostic_generator.py``) como las
recomendaciones del propio audit qué es legítimo afirmar ante el cliente. Dos
dueños para el mismo criterio es la deriva que denuncia el dossier (H10/A1), así
que el criterio vive aquí una sola vez.
"""

from typing import Optional

#: Estados que significan "la API respondió bien" — sólo ellos autorizan afirmar
#: que la ausencia de datos de campo es del sitio (nuevo o con poco tráfico).
#: ``VERIFIED`` y ``LAB_DATA_ONLY`` los entrega ``PageSpeedClient``; ``OK`` y
#: ``SUCCESS`` vienen de mocks y fixtures históricos del repo.
PERFORMANCE_OK_STATUSES = frozenset({"OK", "SUCCESS", "VERIFIED", "LAB_DATA_ONLY"})


def is_performance_api_unavailable(status: Optional[str]) -> bool:
    """True cuando el eje PageSpeed no quedó medido por una causa nuestra.

    Lista blanca, no lista negra: vacío, ``None`` y cualquier valor desconocido
    caen del lado de "no evaluable" (vacío ≠ ausente, lección SR-H2), que es
    justo el error que cometía el texto hardcodeado de D6 al asumir "sitio nuevo".
    """
    return (status or "").strip().upper() not in PERFORMANCE_OK_STATUSES
