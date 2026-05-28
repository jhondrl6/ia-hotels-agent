"""
ROI Formatter v1.0.0 — Métricas CAPEX/OPEX Desacopladas.

ROICR FASE-3: Separa CAPEX (inversión única, activo digital del cliente)
de OPEX (fee mensual de servicio). PROHIBIDO: Recuperación / (OPEX + CAPEX)
— esto produce ROI falso de 0.80X.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class ROIMetrics:
    """Métricas de ROI con CAPEX/OPEX desacoplados."""
    roi_saas: float
    capex_total: float
    opex_mensual: float
    recuperacion_total: float
    meses_proyeccion: int
    nota_metodologica: str
    activos_digitales: List[str]


def calcular_metricas_roi(
    recuperacion_total: float,
    inversion_opex: float,
    inversion_capex: float,
    meses_proyeccion: int = 6,
    activos_digitales: Optional[List[str]] = None,
    roi_cap: Optional[float] = None,
) -> ROIMetrics:
    """Calcula métricas de ROI con CAPEX/OPEX desacoplados.

    PROHIBIDO: recuperacion_total / (inversion_opex + inversion_capex)
    — esto mezcla activo del cliente con fee de servicio y produce ROI falso.

    Args:
        recuperacion_total: Recuperación total proyectada en COP
                            (suma de recuperación mensual × meses).
        inversion_opex: Inversión operativa (fee mensual × meses, servicio).
        inversion_capex: Inversión en activo digital (setup fee, propiedad del cliente).
        meses_proyeccion: Meses de proyección (default 6).
        activos_digitales: Lista de activos digitales que quedan en propiedad
                           del cliente (ej. ["Hotel Schema", "FAQ Page", ...]).

    Returns:
        ROIMetrics con roi_saas independiente y nota metodológica.
    """
    if activos_digitales is None:
        activos_digitales = []

    # ROI SaaS: retorno sobre inversión operativa (servicio)
    # NUNCA dividir por OPEX+CAPEX
    roi_saas = recuperacion_total / inversion_opex if inversion_opex > 0 else 0.0

    # Apply optional cap (e.g., 5.0X from commercial.yaml)
    if roi_cap is not None and roi_saas > roi_cap:
        roi_saas = roi_cap

    nota = (
        f"ROI calculado sobre inversión operativa ({meses_proyeccion} meses de servicio). "
        f"La inversión CAPEX (${inversion_capex:,.0f} COP) representa activos digitales "
        f"que quedan en propiedad del cliente y no se deprecian en este cálculo. "
        f"Metodología: Recuperación Total / OPEX (fee de servicio), "
        f"NO Recuperación / (OPEX + CAPEX)."
    )

    return ROIMetrics(
        roi_saas=round(roi_saas, 2),
        capex_total=inversion_capex,
        opex_mensual=inversion_opex / meses_proyeccion if meses_proyeccion > 0 else 0,
        recuperacion_total=recuperacion_total,
        meses_proyeccion=meses_proyeccion,
        nota_metodologica=nota,
        activos_digitales=activos_digitales,
    )


def formatear_roi_para_propuesta(metrics: ROIMetrics) -> Dict[str, Any]:
    """Formatea métricas ROI para inclusión en propuesta comercial.

    Retorna un dict listo para ser usado como placeholders en el template.
    """
    return {
        "roi_saas": f"{metrics.roi_saas:.2f}X",
        "capex_total": f"${metrics.capex_total:,.0f}".replace(",", "."),
        "opex_mensual": f"${metrics.opex_mensual:,.0f}".replace(",", "."),
        "recuperacion_total": f"${metrics.recuperacion_total:,.0f}".replace(",", "."),
        "activos_digitales_lista": "\n".join(
            f"- {a}" for a in metrics.activos_digitales
        ),
        "nota_metodologica": metrics.nota_metodologica,
    }
