"""
Pillar Maturity Curve v1.0.0 — Curva de Maduración por 4 Pilares.

ROICR FASE-3: Reemplaza el descuento lineal por una curva de maduración
basada en 4 pilares (GEO → SEO → AEO → IAO) que refleja cómo cada pilar
tarda en generar resultados.

La recuperación no es instantánea — sigue una curva de 6 meses:
Mes 1 (GEO): 15% — Google Business Profile, visibilidad local inmediata
Mes 2 (SEO): 35% — Indexación, rich snippets
Mes 3 (SEO): 60% — Autoridad de dominio, backlinks
Mes 4 (AEO): 80% — Answer Engine Optimization, ChatGPT/Perplexity
Mes 5 (IAO): 95% — IA Optimization, maduración completa
Mes 6 (IAO): 100% — Estado estacionario
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


# Curva de maduración por mes (fracción del recovery_factor_max)
CURVA_4_PILARES: List[float] = [0.15, 0.35, 0.60, 0.80, 0.95, 1.00]

# Descripción de cada mes para narrativa comercial
PILARES_POR_MES: Dict[int, str] = {
    1: "GEO — Google Business Profile, visibilidad local inmediata",
    2: "SEO — Indexación, rich snippets, datos estructurados",
    3: "SEO — Autoridad de dominio, backlinks, contenido",
    4: "AEO — Answer Engine Optimization (ChatGPT, Gemini, Perplexity)",
    5: "IAO — IA Optimization, maduración completa del ecosistema",
    6: "IAO — Estado estacionario, mantenimiento y optimización continua",
}


@dataclass
class MaturityProjection:
    """Proyección mensual de recuperación con curva de maduración."""
    mes: int
    factor: float
    recuperacion_mensual: float
    recuperacion_acumulada: float
    pilar: str


@dataclass
class PillarMaturityResult:
    """Resultado completo de la curva de maduración."""
    fuga_mensual: float
    recovery_factor_max: float
    recuperacion_max_mensual: float
    proyecciones: List[MaturityProjection]
    total_recuperacion_6m: float


def aplicar_curva_4_pilares(
    fuga_mensual: float,
    recovery_factor_max: float,
    meses: int = 6,
) -> PillarMaturityResult:
    """Aplica la curva de maduración de 4 pilares a la fuga mensual.

    Args:
        fuga_mensual: Fuga mensual estimada en COP (expected_loss).
        recovery_factor_max: Factor de recuperación máximo (ej. 0.35 = 35%).
        meses: Número de meses a proyectar (default 6, máximo 6).

    Returns:
        PillarMaturityResult con proyección mes a mes y total acumulado.
    """
    if meses > 6:
        meses = 6  # Curva definida para 6 meses

    recuperacion_max_mensual = fuga_mensual * recovery_factor_max
    proyecciones: List[MaturityProjection] = []
    acumulado = 0.0

    for i in range(meses):
        mes = i + 1
        factor = CURVA_4_PILARES[i]
        recuperacion_mes = recuperacion_max_mensual * factor
        acumulado += recuperacion_mes

        proyecciones.append(MaturityProjection(
            mes=mes,
            factor=factor,
            recuperacion_mensual=round(recuperacion_mes, 2),
            recuperacion_acumulada=round(acumulado, 2),
            pilar=PILARES_POR_MES.get(mes, ""),
        ))

    return PillarMaturityResult(
        fuga_mensual=fuga_mensual,
        recovery_factor_max=recovery_factor_max,
        recuperacion_max_mensual=round(recuperacion_max_mensual, 2),
        proyecciones=proyecciones,
        total_recuperacion_6m=round(acumulado, 2),
    )


def calcular_recuperacion_6m(
    fuga_mensual: float,
    recovery_factor_max: float,
) -> float:
    """Fórmula ÚNICA de recuperación proyectada 6m (FASE-B COHERENCIA, N1, DEC-B2).

    Una sola fuente de verdad para el concepto "recuperación proyectada 6m":
    fuga_mensual × recovery_factor_max × Σ(CURVA_4_PILARES) = fuga × recovery × 3.85.

    Diagnóstico y propuesta comercial consumen ESTA función; el pain_ratio es
    una métrica distinta (relación precio/fuga) y NUNCA multiplica aquí.
    """
    result = aplicar_curva_4_pilares(
        fuga_mensual=fuga_mensual,
        recovery_factor_max=recovery_factor_max,
        meses=6,
    )
    return result.total_recuperacion_6m


def formatear_curva_para_propuesta(result: PillarMaturityResult) -> Dict[str, Any]:
    """Formatea la curva de maduración para inclusión en propuesta comercial.

    Retorna un dict con tablas Markdown y datos estructurados para el template.
    """
    # Tabla de proyección mensual
    filas = []
    for p in result.proyecciones:
        recuperacion_fmt = f"${p.recuperacion_mensual:,.0f}".replace(",", ".")
        acumulado_fmt = f"${p.recuperacion_acumulada:,.0f}".replace(",", ".")
        filas.append(
            f"| Mes {p.mes} | {p.factor*100:.0f}% | {recuperacion_fmt} | "
            f"{acumulado_fmt} | {p.pilar} |"
        )

    tabla_mensual = (
        "| Mes | Maduración | Recuperación | Acumulado | Pilar |\n"
        "|-----|-----------|-------------|-----------|-------|\n"
        + "\n".join(filas)
    )

    return {
        "curva_4_pilares_tabla": tabla_mensual,
        "total_recuperacion_6m": f"${result.total_recuperacion_6m:,.0f}".replace(",", "."),
        "recuperacion_max_mensual": f"${result.recuperacion_max_mensual:,.0f}".replace(",", "."),
        "fuga_mensual": f"${result.fuga_mensual:,.0f}".replace(",", "."),
        "recovery_factor_max": f"{result.recovery_factor_max*100:.0f}%",
    }
