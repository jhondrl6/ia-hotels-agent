"""Lector latente de ``GapAnalyzer._basic_analysis`` — FASE-A (Tarea 2, L-V2).

El refactor ``1501dd8`` convirtió ``FinancialFactors.SUPERPOSITION_FACTOR``
(atributo) en ``get_superposition_factor()`` (método). ``gap_analyzer`` conservó
un lector latente del atributo muerto en la rama fallback de
``analyze_with_llm``; al recorrer la rama revienta con ``AttributeError``.

Decisión (10-analisis §Decisiones): REPARAR, no retirar — la rama es código
vivo (fallback cuando el LLM no está disponible o falla), y ``GapAnalyzer`` lo
consumen ``config_checker`` y ``spark_generator``.

Mutation check (R2.8): si se reintroduce el lector del atributo muerto,
``_basic_analysis`` revienta y estos tests fallan en rojo.
"""

from modules.analyzers.gap_analyzer import GapAnalyzer
from modules.utils.financial_factors import FinancialFactors


def _correr_rama_fallback():
    """Recorre ``_basic_analysis`` con la forma real de sus entradas (dicts)."""
    # __new__ evita instanciar ProviderAdapter: la rama bajo prueba no usa self.
    analyzer = GapAnalyzer.__new__(GapAnalyzer)
    return analyzer._basic_analysis({}, {}, {}, {})


def test_basic_analysis_recorre_modelo_perdidas_sin_attribute_error():
    """La rama fallback no revienta y publica `factor_superposicion` (AC5)."""
    resultado = _correr_rama_fallback()
    assert "modelo_perdidas" in resultado
    modelo = resultado["modelo_perdidas"]
    assert "factor_superposicion" in modelo
    assert isinstance(modelo["factor_superposicion"], float)


def test_factor_superposicion_viene_del_contrato_metodo():
    """El valor del lector casa con el contrato vivo `get_superposition_factor()`."""
    resultado = _correr_rama_fallback()
    assert (
        resultado["modelo_perdidas"]["factor_superposicion"]
        == FinancialFactors.get_superposition_factor()
    )
