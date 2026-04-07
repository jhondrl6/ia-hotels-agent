"""Opportunity Scorer — Priorizacion ponderada de brechas.

Reemplaza los porcentajes fijos (15%, 10%) de las brechas criticas
por un modelo ponderado de 3 factores:

  FACTOR 1 — Severidad del Gap (0-40 pts)
  FACTOR 2 — Esfuerzo de Implementacion (0-30 pts)
  FACTOR 3 — Impacto en Conversion Directa (0-30 pts)

Total: 0-100 pts, rankeado descendente.

Uso:
    scorer = OpportunityScorer()
    scores = scorer.score_brechas(brechas, assessment, competitor_data)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class OpportunityScore:
    """Resultado de scoring para una brecha individual."""

    brecha_id: str
    brecha_name: str
    severity_score: float       # 0-40
    effort_score: float         # 0-30
    impact_score: float         # 0-30
    total_score: float          # 0-100
    estimated_monthly_cop: float
    justification: str          # Explicacion legible para el hotelero
    rank: int = 0               # 1 = prioridad mas alta


class OpportunityScorer:
    """Scores and ranks brechas by weighted 3-factor model."""

    # Mapas de severidad por tipo de brecha
    # base: puntuacion base (0-40)
    # competitor_factor: si ajusta por datos de competencia
    BRECHA_SEVERITY_MAP: Dict[str, Dict[str, Any]] = {
        "faq_schema_missing": {
            "base": 35,
            "competitor_factor": True,
            "label": "Sin Schema FAQ",
        },
        "gbp_incomplete": {
            "base": 30,
            "competitor_factor": True,
            "label": "GBP incompleta",
        },
        "whatsapp_conflict": {
            "base": 40,
            "competitor_factor": False,
            "label": "WhatsApp inconsistente",
        },
        "data_inconsistent": {
            "base": 35,
            "competitor_factor": False,
            "label": "Datos inconsistentes",
        },
        "cms_defaults": {
            "base": 20,
            "competitor_factor": True,
            "label": "Metadatos CMS por defecto",
        },
        "no_hotel_schema": {
            "base": 30,
            "competitor_factor": True,
            "label": "Sin Schema Hotel",
        },
        "poor_performance": {
            "base": 25,
            "competitor_factor": False,
            "label": "Rendimiento web bajo",
        },
    }

    # Esfuerzo por tipo de brecha (0-30)
    BRECHA_EFFORT_MAP: Dict[str, float] = {
        "faq_schema_missing": 30,    # Ya generamos el asset JSON-LD
        "gbp_incomplete": 25,        # Hotelero sube fotos desde celular
        "whatsapp_conflict": 20,     # Unificar numero en web y GBP
        "data_inconsistent": 20,     # Corregir datos en fuentes
        "cms_defaults": 15,          # Modificar metadatos CMS
        "no_hotel_schema": 30,       # Ya generamos el asset
        "poor_performance": 10,      # Requiere trabajo tecnico avanzado
    }

    # Impacto en conversion directa (0-30)
    BRECHA_IMPACT_MAP: Dict[str, float] = {
        "faq_schema_missing": 20,    # Rich snippets, mediano plazo
        "gbp_incomplete": 25,        # Visibilidad local inmediata
        "whatsapp_conflict": 30,     # Reserva directa perdida
        "data_inconsistent": 30,     # Reserva directa perdida
        "cms_defaults": 20,          # SEO mediano plazo
        "no_hotel_schema": 25,       # Visibilidad en asistentes IA
        "poor_performance": 25,      # Abandono mobile inmediato
    }

    # Justificaciones template
    _JUSTIFICATION_TEMPLATES: Dict[str, str] = {
        "faq_schema_missing": (
            "Google no puede mostrar sus preguntas frecuentes en los resultados {competitor_note}. "
            "Solucion: instalar schema JSON-LD generado automaticamente. "
            "Impacto: mayor visibilidad en busquedas informativas."
        ),
        "gbp_incomplete": (
            "Su perfil de Google Business Profile tiene informacion incompleta {competitor_note}. "
            "Solucion: completar fotos, horarios y servicios desde su celular. "
            "Impacto: mas clics y llamadas desde Google Maps."
        ),
        "whatsapp_conflict": (
            "El numero de WhatsApp es diferente en Google vs web. "
            "Clientes confundidos no completan la reserva. "
            "Solucion: unificar el numero en todas las fuentes. "
            "Impacto: reservas directas recuperadas inmediatamente."
        ),
        "data_inconsistent": (
            "Hay informacion contradictoria entre fuentes sobre su hotel. "
            "Los motores de IA no saben cual dato es correcto. "
            "Solucion: corregir y unificar datos. "
            "Impacto: confianza del cliente y consistencia en busquedas."
        ),
        "cms_defaults": (
            "Su sitio usa titulos y descripciones por defecto del CMS {competitor_note}. "
            "Solucion: personalizar metadatos con nombre, descripcion y ubicacion del hotel. "
            "Impacto: mejor presencia en resultados de busqueda."
        ),
        "no_hotel_schema": (
            "Su sitio no tiene datos estructurados para hoteles {competitor_note}. "
            "Solucion: instalar markup Schema.org generado automaticamente. "
            "Impacto: Google y asistentes de IA entienden mejor su hotel."
        ),
        "poor_performance": (
            "Su sitio web carga lento en dispositivos mobiles. "
            "53% de los usuarios abandonan si tarda mas de 3 segundos. "
            "Solucion: optimizar imagenes y caching. "
            "Impacto: menos abandonos, mas reservas."
        ),
    }

    def score_brechas(
        self,
        brechas: List[Dict[str, Any]],
        assessment: Any = None,
        competitor_data: Optional[Dict[str, Any]] = None,
        total_monthly_loss: Optional[float] = None,
    ) -> List[OpportunityScore]:
        """Score and rank all brechas.

        Args:
            brechas: Lista de dict con al menos 'id' y 'type' (brecha type key).
            assessment: CanonicalAssessment opcional para contexto extra.
            competitor_data: Datos de competencia para ajustar severidad.
                Ej: {"competitors_with_faq": 3, "total_competitors": 5}
            total_monthly_loss: Perdida mensual total estimada del financiero.
                Se usa para distribuir el COP proporcionalmente al score.

        Returns:
            Lista de OpportunityScore ordenada por total_score descendente.
        """
        scores: List[OpportunityScore] = []

        for brecha in brechas:
            brecha_type = brecha.get("type", brecha.get("id", "unknown"))
            brecha_id = brecha.get("id", brecha_type)
            brecha_name = brecha.get(
                "name",
                self.BRECHA_SEVERITY_MAP.get(brecha_type, {}).get(
                    "label", brecha_type.replace("_", " ").title()
                ),
            )

            severity = self._calc_severity(brecha_type, competitor_data, brecha)
            effort = self._calc_effort(brecha_type, brecha)
            impact = self._calc_impact(brecha_type, brecha)
            total = severity + effort + impact

            monthly_cop = self._estimate_monthly_impact(
                total, assessment, total_monthly_loss, len(brechas)
            )
            justification = self._generate_justification(
                brecha_type, severity, effort, impact, competitor_data
            )

            scores.append(
                OpportunityScore(
                    brecha_id=brecha_id,
                    brecha_name=brecha_name,
                    severity_score=severity,
                    effort_score=effort,
                    impact_score=impact,
                    total_score=total,
                    estimated_monthly_cop=monthly_cop,
                    justification=justification,
                )
            )

        # Sort descending by total_score, assign ranks
        scores.sort(key=lambda s: s.total_score, reverse=True)
        for i, s in enumerate(scores, 1):
            s.rank = i

        return scores

    def score_from_assessment(self, assessment: Any) -> List[OpportunityScore]:
        """Deriva brechas desde un CanonicalAssessment y las scorea.

        Metodo conveniente que extrae brechas directamente del assessment
        sin requerir lista previa de brechas.

        Args:
            assessment: CanonicalAssessment con claims y analisis.

        Returns:
            Lista de OpportunityScore.
        """
        brechas = self._extract_brechas_from_assessment(assessment)
        if not brechas:
            return []
        return self.score_brechas(brechas, assessment=assessment)

    def _extract_brechas_from_assessment(self, assessment: Any) -> List[Dict[str, Any]]:
        """Extrae brechas candidatas desde un CanonicalAssessment."""
        brechas = []
        seen: set = set()

        if assessment is None:
            return brechas

        # Schema: sin FAQ schema
        schema = getattr(assessment, "schema_analysis", None)
        if schema and not schema.has_hotel_schema:
            bid = "no_hotel_schema"
            if bid not in seen:
                brechas.append({"id": bid, "type": bid, "name": "Sin Schema Hotel"})
                seen.add(bid)
            # FAQ viene de missing fields o coverage low
            missing = getattr(schema, "missing_critical_fields", [])
            if any("faq" in f.lower() for f in missing) or schema.coverage_score < 0.5:
                bid = "faq_schema_missing"
                if bid not in seen:
                    brechas.append(
                        {"id": bid, "type": bid, "name": "Sin Schema FAQ"}
                    )
                    seen.add(bid)

        # GBP: incompleta
        gbp = getattr(assessment, "gbp_analysis", None)
        if gbp:
            photo_count = getattr(gbp, "photo_count", None)
            is_claimed = getattr(gbp, "is_claimed", None)
            if (photo_count is not None and photo_count < 10) or (
                is_claimed is not None and not is_claimed
            ):
                bid = "gbp_incomplete"
                if bid not in seen:
                    brechas.append(
                        {"id": bid, "type": bid, "name": "GBP incompleta"}
                    )
                    seen.add(bid)

        # Claims: buscar conflictos de WhatsApp, datos inconsistentes
        claims = getattr(assessment, "claims", [])
        for claim in claims:
            cat = getattr(claim, "category", "").lower()
            msg = getattr(claim, "message", "").lower()

            if "whatsapp" in cat or "whatsapp" in msg:
                bid = "whatsapp_conflict"
                if bid not in seen:
                    brechas.append(
                        {
                            "id": bid,
                            "type": bid,
                            "name": "WhatsApp inconsistente",
                            "claim": claim,
                        }
                    )
                    seen.add(bid)

            if "inconsistent" in msg or "conflict" in msg or "dif" in msg:
                bid = "data_inconsistent"
                if bid not in seen:
                    brechas.append(
                        {
                            "id": bid,
                            "type": bid,
                            "name": "Datos inconsistentes",
                            "claim": claim,
                        }
                    )
                    seen.add(bid)

        # Metadata: CMS defaults
        metadata = getattr(assessment, "site_metadata", None)
        if metadata and getattr(metadata, "has_default_title", False):
            bid = "cms_defaults"
            if bid not in seen:
                brechas.append(
                    {"id": bid, "type": bid, "name": "Metadatos CMS por defecto"}
                )
                seen.add(bid)

        # Performance
        perf = getattr(assessment, "performance_analysis", None)
        if perf and getattr(perf, "performance_score", 100) < 70:
            bid = "poor_performance"
            if bid not in seen:
                brechas.append(
                    {"id": bid, "type": bid, "name": "Rendimiento web bajo"}
                )
                seen.add(bid)

        return brechas

    def _calc_severity(
        self,
        brecha_type: str,
        competitor_data: Optional[Dict[str, Any]] = None,
        brecha: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Calcula severidad 0-40.

        Si hay datos de competencia y competitor_factor es True:
        - Si muchos competidores lo tienen resuelto -> maximo (40)
        - Si nadie lo tiene -> 25 (mitad del maximo)
        """
        severity_info = self.BRECHA_SEVERITY_MAP.get(
            brecha_type, {"base": 20, "competitor_factor": False}
        )
        base = severity_info["base"]
        use_competitor = severity_info["competitor_factor"]

        if not use_competitor or not competitor_data:
            return float(base)

        # Competitor adjustment
        competitors_with = competitor_data.get("competitors_with_feature", 0)
        total_competitors = competitor_data.get("total_competitors", 0)

        if total_competitors > 0:
            ratio = competitors_with / total_competitors
            if ratio > 0.5:
                # La mayoria de competidores lo tiene: urgencia alta
                return 40.0
            elif ratio > 0.0:
                # Algunos lo tienen: urgencia media-alta
                return 30.0
            else:
                # Nadie lo tiene: urgencia media
                return 25.0

        return float(base)

    def _calc_effort(
        self, brecha_type: str, brecha: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calcula esfuerzo 0-30 (mas alto = mas facil de implementar)."""
        effort = self.BRECHA_EFFORT_MAP.get(brecha_type, 15)
        # Override si la brecha tiene un effort explicito
        if brecha and "effort_override" in brecha:
            effort = brecha["effort_override"]
        return float(effort)

    def _calc_impact(
        self, brecha_type: str, brecha: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calcula impacto en conversion directa 0-30."""
        impact = self.BRECHA_IMPACT_MAP.get(brecha_type, 15)
        if brecha and "impact_override" in brecha:
            impact = brecha["impact_override"]
        return float(impact)

    def _estimate_monthly_impact(
        self,
        score: float,
        assessment: Any = None,
        total_monthly_loss: Optional[float] = None,
        num_brechas: int = 4,
    ) -> float:
        """Estima impacto mensual en COP basado en el score.

        Si hay total_monthly_loss disponible, distribuye proporcionalmente.
        Si no, usa estimacion desde benchmark.
        """
        if total_monthly_loss and total_monthly_loss > 0:
            # Distribuir proporcionalmente segun score relativo
            # score/100 * total_monthly_loss * (1/num_brechas) como base,
            # ajustado por el factor de score
            weight = score / 100.0
            # Normalizar: si todas las brechas tuvieran score 100,
            # compartirian equitativamente. Como tienen scores distintos,
            # la proporcion es directamente weight.
            return round(total_monthly_loss * weight / max(num_brechas, 1) * (100 / 50), 0)

        # Fallback: estimacion desde assessment o base
        if assessment:
            # Intentar.extraer datos financieros
            # No hay campo financiero directo en CanonicalAssessment base,
            # usar estimacion conservadora
            base_monthly = 3000000  # 3M COP base estimado

        else:
            base_monthly = 3000000  # 3M COP base estimado

        # Score/100 * base_monthly * factor_brecha
        factor = 0.15 if score >= 80 else (0.10 if score >= 60 else 0.05)
        return round(base_monthly * factor, 0)

    def _generate_justification(
        self,
        brecha_type: str,
        severity: float,
        effort: float,
        impact: float,
        competitor_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Genera justificacion legible para hotelero no tecnico."""
        template = self._JUSTIFICATION_TEMPLATES.get(
            brecha_type,
            "Se detecto una oportunidad de mejora en su presencia digital. "
            "Solucion: revisar e implementar recomendaciones tecnicas. "
            "Impacto: mejora en visibilidad online.",
        )

        # Competitor note
        competitor_note = ""
        if competitor_data and self.BRECHA_SEVERITY_MAP.get(
            brecha_type, {}
        ).get("competitor_factor"):
            comp_with = competitor_data.get("competitors_with_feature", 0)
            comp_total = competitor_data.get("total_competitors", 0)
            if comp_total > 0:
                competitor_note = (
                    f"(su competidor {comp_with} de {comp_total} ya lo tiene resuelto)"
                )

        return template.format(competitor_note=competitor_note)

    def get_weights_summary(self) -> Dict[str, Any]:
        """Retorna los pesos del modelo para documentacion."""
        return {
            "severidad": {"max": 40, "descripcion": "Gravedad de la brecha vs competencia"},
            "esfuerzo": {
                "max": 30,
                "descripcion": "Facilidad de implementacion (alto = facil)",
            },
            "impacto": {
                "max": 30,
                "descripcion": "Impacto directo en conversion/reservas",
            },
            "total": 100,
        }
