"""Decision Engine v2.4.2 (Reglas Puras, sin LLM).

Deterministic package selection using Plan Maestro v2.4.2 benchmarks.
Orden de reglas según §5.2: Impacto Catastrófico → Conversión → IA → GEO

v2.4.2 Changes:
- Modelo logarítmico para inactividad GBP (calibrado $1.6M)
- Separación motor: inexistente (45%) vs no prominente (18%)
- Activity score compuesto: posts + fotos + reviews
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict

from modules.utils.benchmarks import BenchmarkLoader


@dataclass
class Diagnostico:
    """Estructura de datos de diagnóstico para motor de decisión v2.4.2."""
    sin_motor_reservas: int = 0
    schema_ausente: int = 0
    gbp_score: int = 0
    web_score: int = 50
    revpar: int = 0
    region: str = "default"
    menciones_ia: int = 0
    # v2.4.2: Campos de actividad GBP
    gbp_activity_score: int = 100      # 0-100 compuesto (posts+fotos+reviews)
    gbp_motor_existe: bool = True       # True si existe motor en GBP
    gbp_motor_prominente: bool = False  # True si motor visible/1-clic

    @property
    def impacto_total(self) -> int:
        """Suma de brechas de conversión y schema."""
        return int(self.sin_motor_reservas + self.schema_ausente)


class DecisionEngine:
    """
    Motor de decisión basado en brecha dominante (Plan Maestro v2.4.2 §5.2).
    
    ORDEN DE EVALUACIÓN:
    1. Impacto catastrófico (≥$8M) → Elite PLUS
    2. Brecha conversión crítica (≥$3M) → Evaluar por RevPAR
    3. Brecha IA dominante → Evaluar por web_score
    4. Brecha GEO dominante → Evaluar por gbp_score + inactividad
    
    v2.4.2: Modelo logarítmico de inactividad + descuentos motor GBP
    """
    
    def __init__(self, loader: BenchmarkLoader | None = None) -> None:
        self.loader = loader or BenchmarkLoader()
        self.thresholds = self.loader.get_thresholds()
        # Metadatos de versión (no rompe contrato anterior)
        plan_meta = self.loader.get_decision_plan_meta()
        self.plan_version = plan_meta.get("version", "v2.4.2")
        self.plan_document = plan_meta.get("documento_oficial", "Plan_maestro_v2_5.md")

    def _identificar_brecha_dominante(self, diag: Diagnostico) -> str:
        brechas, _ = self._calcular_brechas(diag)
        return max(brechas, key=brechas.get)

    def _calcular_brechas(self, diag: Diagnostico) -> tuple[Dict[str, int], Dict[str, Any]]:
        """Calcula brechas ajustadas + trazas (penalización log y descuentos)."""
        t = self.thresholds
        factor_gbp = t.get("factor_gbp_punto", 50_000)
        max_inactividad = t.get("inactividad_max_mensual", 1_600_000)

        # Ajuste brecha conversión por estado de motor GBP
        brecha_conversion = diag.sin_motor_reservas
        motor_ajuste = 0.0
        if not diag.gbp_motor_existe:
            motor_ajuste = t.get("descuento_motor_inexistente", 0.45)
            brecha_conversion = int(brecha_conversion * (1 - motor_ajuste))
        elif diag.gbp_motor_existe and not diag.gbp_motor_prominente:
            motor_ajuste = t.get("descuento_motor_no_prominente", 0.18)
            brecha_conversion = int(brecha_conversion * (1 - motor_ajuste))

        # Penalización logarítmica por inactividad GBP
        if diag.gbp_activity_score >= 100:
            penalizacion_inactividad = 0
        else:
            penalizacion = math.log(101 - diag.gbp_activity_score) / math.log(101)
            penalizacion_inactividad = int(penalizacion * max_inactividad)

        brechas = {
            "conversion": brecha_conversion,
            "ia_visibility": diag.schema_ausente,
            "geo": (100 - diag.gbp_score) * factor_gbp + penalizacion_inactividad,
        }

        extra = {
            "brecha_conversion_ajustada": brecha_conversion,
            "penalizacion_inactividad": penalizacion_inactividad,
            "motor_ajuste": motor_ajuste,
        }
        return brechas, extra

    def recomendar(self, diag: Diagnostico) -> Dict[str, Any]:
        """Aplica reglas de decisión en orden según Plan Maestro v2.3 §5.2."""
        region_data = self.loader.get_regional_data(diag.region)
        t = self.thresholds

        brechas, brechas_extra = self._calcular_brechas(diag)
        impacto_total = brechas_extra.get("brecha_conversion_ajustada", diag.sin_motor_reservas) + diag.schema_ausente
        revpar = diag.revpar or region_data.get("revpar_cop", 0)
        brecha_dominante = max(brechas, key=brechas.get)

        # Valores por defecto
        paquete = "Pro AEO"
        paquete_id = "pro_aeo"
        razon = "Perfil balanceado; Pro AEO optimiza relación costo-beneficio."

        # ═══════════════════════════════════════════════════════════════════
        # REGLA 1: IMPACTO CATASTRÓFICO (Máxima prioridad)
        # ═══════════════════════════════════════════════════════════════════
        if impacto_total >= t.get("impacto_catastrofico", 8_000_000):
            paquete = "Elite PLUS"
            paquete_id = "elite_plus"
            razon = (
                f"Pérdidas totales ≥${t.get('impacto_catastrofico', 8_000_000):,}/mes "
                "requieren monitoring completo y stack Elite PLUS."
            )
        
        # ═══════════════════════════════════════════════════════════════════
        # REGLA 2: RevPAR PREMIUM (Sin importar brecha)
        # ═══════════════════════════════════════════════════════════════════
        elif revpar >= t.get("revpar_premium", 250_000):
            if diag.web_score >= t.get("web_score_alto", 75) or diag.gbp_score >= 80:
                paquete = "Elite PLUS"
                razon = (
                    f"RevPAR premium (${revpar:,}) con señales fuertes (web {diag.web_score}/GBP {diag.gbp_score}) "
                    "justifica máximo blindaje de margen."
                )
            else:
                paquete = "Elite"
                paquete_id = "elite"
                razon = (
                    f"RevPAR premium (${revpar:,}) justifica sistema Elite completo."
                )
        
        # ═══════════════════════════════════════════════════════════════════
        # REGLA 3: BRECHA CONVERSIÓN CRÍTICA
        # ═══════════════════════════════════════════════════════════════════
        elif brecha_dominante == "conversion" and brechas_extra.get("brecha_conversion_ajustada", diag.sin_motor_reservas) >= t.get("brecha_conversion_critica", 3_000_000):
            paquete = "Pro AEO Plus"
            paquete_id = "pro_aeo_plus"
            razon = (
                f"Brecha conversión crítica (${diag.sin_motor_reservas:,}) + "
                f"RevPAR medio (${revpar:,}). Activar wa.me + fix web."
            )
        
        # ═══════════════════════════════════════════════════════════════════
        # REGLA 9: GBP OPTIMIZADO PERO INACTIVO (precede a IA)
        # ═══════════════════════════════════════════════════════════════════
        elif diag.gbp_score >= t.get("gbp_score_bajo", 60) and diag.gbp_activity_score < t.get("gbp_activity_score_bajo", 30):
            paquete = "Starter GEO + GBP Activation"
            paquete_id = "starter_geo_gbp_activation"
            razon = (
                f"GBP Score adecuado ({diag.gbp_score}) pero inactividad crítica "
                f"(activity {diag.gbp_activity_score}/100). Addon de activación recupera $1.5M/mes."
            )
            brecha_dominante = "geo"

        # ═══════════════════════════════════════════════════════════════════
        # REGLA 4: BRECHA IA DOMINANTE
        # ═══════════════════════════════════════════════════════════════════
        elif brecha_dominante == "ia_visibility":
            if diag.web_score >= t.get("web_score_alto", 75):
                paquete = "Pro AEO"
                paquete_id = "pro_aeo"
                razon = (
                    f"Web score alto ({diag.web_score}≥{t.get('web_score_alto', 75)}) "
                    "ya convierte; falta robustecer visibilidad IA con JSON-LD."
                )
            else:
                paquete = "Pro AEO Plus"
                paquete_id = "pro_aeo_plus"
                razon = (
                    f"Web score bajo ({diag.web_score}<{t.get('web_score_alto', 75)}) "
                    "necesita fix web crítico + esquema IA completo."
                )
        
        # ═══════════════════════════════════════════════════════════════════
        # REGLA 5: BRECHA GEO DOMINANTE
        # ═══════════════════════════════════════════════════════════════════
        elif brecha_dominante == "geo":
            if diag.gbp_score < t.get("gbp_score_bajo", 60):
                paquete = "Starter GEO"
                paquete_id = "starter_geo"
                razon = (
                    f"Prioridad absoluta: visibilidad local (GBP {diag.gbp_score}<{t.get('gbp_score_bajo', 60)}). "
                    "Optimizar GBP antes de escalar a IA."
                )
            # ═══════════════════════════════════════════════════════════════
            # REGLA 9: GBP OPTIMIZADO PERO INACTIVO (v2.4.2)
            # ═══════════════════════════════════════════════════════════════
            elif diag.gbp_activity_score < t.get("gbp_activity_score_bajo", 30):
                paquete = "Starter GEO + GBP Activation"
                paquete_id = "starter_geo_gbp_activation"
                razon = (
                    f"GBP Score adecuado ({diag.gbp_score}) pero inactividad crítica "
                    f"(activity {diag.gbp_activity_score}/100). Addon de activación recupera $1.5M/mes."
                )
            else:
                paquete = "Pro AEO"
                paquete_id = "pro_aeo"
                razon = (
                    "GBP adecuado pero múltiples brechas moderadas; "
                    "Pro AEO cubre GEO+IA sin sobrecosto."
                )

        confianza = self._compute_confianza(diag)

        # ═══════════════════════════════════════════════════════════════════
        # NOTA: Eliminada lógica de degradación por ROI (v3.9.2)
        # El paquete recomendado debe ser consistente con el diagnóstico.
        # La decisión comercial (ajustar por presupuesto) es responsabilidad
        # del consultor, no del sistema automático.
        # ═══════════════════════════════════════════════════════════════════
        # PRECIO_PAQUETES queda disponible para referencia futura
        precios_paquetes = {
            "elite_plus": 9_800_000,
            "elite": 7_500_000,
            "pro_aeo_plus": 4_800_000,
            "pro_aeo": 3_200_000,
            "starter_geo": 1_800_000,
            "starter_geo_gbp_activation": 2_600_000
        }

        return {
            "paquete": paquete,
            "package_id": paquete_id,
            "razon": razon,
            "confianza": confianza,
            "brecha_dominante": brecha_dominante,
            "region": diag.region,
            "version": self.loader.load().get("version", "v2.4.2"),
            "plan_version": self.plan_version,
            "plan_document": self.plan_document,
            "gbp_activity_penalty": brechas_extra.get("penalizacion_inactividad", 0),
            "brecha_conversion_ajustada": brechas_extra.get("brecha_conversion_ajustada", diag.sin_motor_reservas),
            "motor_ajuste": brechas_extra.get("motor_ajuste", 0),
            "schema_ausente": diag.schema_ausente,
            "inputs": {
                "impacto_total": impacto_total,
                "gbp_score": diag.gbp_score,
                "web_score": diag.web_score,
                "revpar": revpar,
                "menciones_ia": diag.menciones_ia,
            },
            "firma_marca": "IAH · Reglas puras v2.4.2",
        }

    def _compute_confianza(self, diag: Diagnostico) -> float:
        """Calcula confianza de la recomendación basada en calidad de datos."""
        t = self.thresholds
        impacto_norm = min(diag.impacto_total / max(t.get("impacto_catastrofico", 8_000_000), 1), 1.2)
        gbp_gap = max(0.0, (t.get("gbp_score_bajo", 60) - diag.gbp_score) / 100)
        web_gap = max(0.0, (t.get("web_score_alto", 75) - diag.web_score) / 100)

        confianza = 0.78 + (0.10 * impacto_norm) - (0.05 * gbp_gap) - (0.03 * web_gap)
        confianza = max(0.60, min(confianza, 0.96))
        return round(confianza, 2)
