"""Sync Contract - Narrative synchronization between commercial and GEO diagnostics.

This module ensures that the commercial diagnosis (from GapAnalyzer) and the
GEO assessment (from GEODiagnostic) do not contradict each other, and provides
clear tags and recommendations for the proposal.

The 8 combinations are:

| Combination | GEO Score    | Pérdida Comercial | Resultado       | Tag                              |
|-------------|--------------|------------------|-----------------|----------------------------------|
| A1          | EXCELLENT    | Alta             | No contradictorio | "Problema es comercial, no técnico" |
| A2          | EXCELLENT    | Baja             | No contradictorio | "Hotel en buen estado técnico"   |
| B1          | GOOD         | Alta             | No contradictorio | "Brecha técnica contribuye"      |
| B2          | GOOD         | Baja             | No contradictorio | "Hotel en buen estado"           |
| C1          | FOUNDATION   | Alta             | No contradictorio | "Brecha técnica confirma pérdida"|
| C2          | FOUNDATION   | Baja             | Investigar      | "Inconsistencia - investigar"    |
| D1          | CRITICAL     | Alta             | No contradictorio | "Crisis técnica confirma pérdida" |
| D2          | CRITICAL     | Baja             | Error           | "Error - verificar datos"         |

Reference: FASE-4 prompt, README.md
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class GEOBand(Enum):
    """GEO readiness band classification."""
    EXCELLENT = "excellent"      # 86-100
    GOOD = "good"               # 68-85
    FOUNDATION = "foundation"   # 36-67
    CRITICAL = "critical"       # 0-35


class LossLevel(Enum):
    """Commercial loss severity classification."""
    ALTA = "alta"
    BAJA = "baja"
    UNKNOWN = "unknown"


# Threshold for loss classification (in COP)
LOSS_THRESHOLD = 5_000_000  # 5M COP monthly


# =============================================================================
# SYNC RESULT DATA CLASS
# =============================================================================

@dataclass
class SyncResult:
    """Result of synchronization analysis between commercial and GEO diagnostics.
    
    Attributes:
        is_consistent: True if narratives are consistent, False otherwise.
        combination_tag: Short label for the combination (e.g., "Problema es comercial, no técnico").
        recommendation: What to say in the proposal document.
        contradiction_report: Details about inconsistency if is_consistent=False.
        sync_score: 0.0-1.0 indicating how well narratives align.
    """
    is_consistent: bool
    combination_tag: str
    recommendation: str
    contradiction_report: Optional[Dict[str, Any]] = None
    sync_score: float = 1.0


# =============================================================================
# SYNC CONTRACT ANALYZER
# =============================================================================

class SyncContractAnalyzer:
    """Analyzes relationship between commercial diagnosis and GEO assessment.
    
    Ensures narrative consistency and provides clear tags and recommendations
    for the unified proposal.
    
    Usage:
        analyzer = SyncContractAnalyzer()
        result = analyzer.analyze(commercial_diagnosis, geo_assessment)
        
        if result.is_consistent:
            print(f"Tag: {result.combination_tag}")
            print(f"Recommendation: {result.recommendation}")
        else:
            print(f"Contradiction detected: {result.contradiction_report}")
    """

    def __init__(self):
        """Initialize the SyncContractAnalyzer."""
        pass

    def analyze(
        self,
        commercial_diagnosis: Dict[str, Any],
        geo_assessment: Any
    ) -> SyncResult:
        """Analyze synchronization between commercial and GEO diagnostics.
        
        Args:
            commercial_diagnosis: Dict with keys like:
                - perdida_mensual_total (int, COP)
                - brechas_criticas (List[dict])
                - paquete_recomendado (str)
                - metricas_clave (dict)
            geo_assessment: GEOAssessment with:
                - total_score (int, 0-100)
                - band (GEOBand)
                - gaps_blocking (List[str])
                - recommendations (List[str])
                
        Returns:
            SyncResult with consistency analysis and recommendation.
        """
        # Extract loss level
        loss_level = self._classify_loss(commercial_diagnosis)
        
        # Extract GEO band from assessment
        geo_band = self._extract_geo_band(geo_assessment)
        
        # Determine combination
        combination = self._get_combination(geo_band, loss_level)
        
        # Generate result based on combination
        return self._generate_result(combination, geo_band, loss_level, commercial_diagnosis, geo_assessment)

    def _classify_loss(self, commercial_diagnosis: Dict[str, Any]) -> LossLevel:
        """Classify loss level from commercial diagnosis."""
        perdida = commercial_diagnosis.get("perdida_mensual_total", 0)
        
        if perdida == 0:
            return LossLevel.UNKNOWN
        
        if perdida >= LOSS_THRESHOLD:
            return LossLevel.ALTA
        else:
            return LossLevel.BAJA

    def _extract_geo_band(self, geo_assessment: Any) -> GEOBand:
        """Extract GEO band from geo_assessment object."""
        band = getattr(geo_assessment, "band", None)
        
        if band is None:
            logger.warning("[SyncContract] geo_assessment missing 'band', defaulting to GOOD")
            return GEOBand.GOOD
        
        # Handle case where band is stored as string in dict
        if isinstance(band, str):
            band_str = band.lower()
            if "excellent" in band_str or "excelente" in band_str:
                return GEOBand.EXCELLENT
            elif "good" or "buen" in band_str:
                return GEOBand.GOOD
            elif "foundation" or "fundacion" in band_str:
                return GEOBand.FOUNDATION
            elif "critical" or "critico" in band_str:
                return GEOBand.CRITICAL
        
        # Handle Enum
        if hasattr(band, "value"):
            band_value = band.value.lower() if isinstance(band.value, str) else str(band.value).lower()
            if "excellent" in band_value or "excelente" in band_value:
                return GEOBand.EXCELLENT
            elif "good" in band_value:
                return GEOBand.GOOD
            elif "foundation" in band_value:
                return GEOBand.FOUNDATION
            elif "critical" in band_value:
                return GEOBand.CRITICAL
        
        return GEOBand.GOOD

    def _get_combination(self, geo_band: GEOBand, loss_level: LossLevel) -> str:
        """Get combination code based on GEO band and loss level."""
        combination_map = {
            (GEOBand.EXCELLENT, LossLevel.ALTA): "A1",
            (GEOBand.EXCELLENT, LossLevel.BAJA): "A2",
            (GEOBand.EXCELLENT, LossLevel.UNKNOWN): "A2",  # Default to A2 for unknown
            (GEOBand.GOOD, LossLevel.ALTA): "B1",
            (GEOBand.GOOD, LossLevel.BAJA): "B2",
            (GEOBand.GOOD, LossLevel.UNKNOWN): "B2",
            (GEOBand.FOUNDATION, LossLevel.ALTA): "C1",
            (GEOBand.FOUNDATION, LossLevel.BAJA): "C2",
            (GEOBand.FOUNDATION, LossLevel.UNKNOWN): "C2",
            (GEOBand.CRITICAL, LossLevel.ALTA): "D1",
            (GEOBand.CRITICAL, LossLevel.BAJA): "D2",
            (GEOBand.CRITICAL, LossLevel.UNKNOWN): "D1",  # Default to D1 for unknown
        }
        return combination_map.get((geo_band, loss_level), "B2")

    def _generate_result(
        self,
        combination: str,
        geo_band: GEOBand,
        loss_level: LossLevel,
        commercial_diagnosis: Dict[str, Any],
        geo_assessment: Any
    ) -> SyncResult:
        """Generate SyncResult based on combination code."""
        
        # Define results for each combination
        results = {
            "A1": SyncResult(
                is_consistent=True,
                combination_tag="Problema es comercial, no técnico",
                recommendation=(
                    "El diagnóstico GEO muestra un sitio técnicamente sólido, pero el hotel "
                    "tiene pérdida comercial significativa. La propuesta debe enfocarse en "
                    "reducir la dependencia de OTAs y mejorar la captura directa, NO en "
                    "mejoras técnicas GEO. El problema es de distribución, no de visibilidad."
                ),
                sync_score=0.95
            ),
            "A2": SyncResult(
                is_consistent=True,
                combination_tag="Hotel en buen estado técnico",
                recommendation=(
                    "El hotel está en excelente estado tanto técnico como comercial. "
                    "Mantener las buenas prácticas actuales y considerar mejoras incrementales. "
                    "No hay urgencia de intervención técnica."
                ),
                sync_score=1.0
            ),
            "B1": SyncResult(
                is_consistent=True,
                combination_tag="Brecha técnica contribuye",
                recommendation=(
                    "El hotel tiene pérdida comercial Y brechas técnicas GEO moderadas. "
                    "La propuesta debe atacar ambas frentes: mejorar distribución directa "
                    "Y resolver gaps técnicos. Las brechas técnicas contribuyen a la pérdida."
                ),
                sync_score=0.85
            ),
            "B2": SyncResult(
                is_consistent=True,
                combination_tag="Hotel en buen estado",
                recommendation=(
                    "El hotel tiene un desempeño técnico aceptable con pérdidas comerciales "
                    "controlables. Considerar mejoras incrementales en distribución. "
                    "La intervención GEO es opcional."
                ),
                sync_score=0.9
            ),
            "C1": SyncResult(
                is_consistent=True,
                combination_tag="Brecha técnica confirma pérdida",
                recommendation=(
                    "Las brechas técnicas GEO son significativas y confirman/amplifican "
                    "la pérdida comercial. La propuesta debe priorizar la resolución de "
                    "gaps técnicos como el llms.txt, schema.org y robots.txt. "
                    "Urgencia: ALTA para evitar mayor pérdida."
                ),
                sync_score=0.8
            ),
            "C2": SyncResult(
                is_consistent=False,
                combination_tag="Inconsistencia - investigar",
                recommendation=(
                    "ATENCIÓN: El diagnóstico muestra brechas técnicas significativas "
                    "pero pérdida comercial baja. INVESTIGAR: ¿Los datos de pérdida son "
                    "correctos? ¿Hay un error en el scraping? ¿El hotel tiene otra fuente "
                    "de ingresos? No proceder hasta esclarecer esta inconsistencia."
                ),
                contradiction_report={
                    "type": "inconsistency",
                    "detail": "GEO score bajo con pérdida comercial baja",
                    "geo_band": geo_band.value,
                    "loss_level": loss_level.value,
                    "action": "investigar",
                    "geo_score": getattr(geo_assessment, "total_score", "unknown"),
                    "perdida": commercial_diagnosis.get("perdida_mensual_total", 0)
                },
                sync_score=0.4
            ),
            "D1": SyncResult(
                is_consistent=True,
                combination_tag="Crisis técnica confirma pérdida",
                recommendation=(
                    "CRISIS TÉCNICA: El sitio tiene score GEO crítico que contribuye "
                    "directamente a la pérdida comercial. La propuesta debe ser urgente, "
                    "con enfoque técnico prioritario. Resolver gaps críticos (llms.txt, "
                    "robots.txt, schema.org) es condición necesaria para reducir pérdidas."
                ),
                sync_score=0.75
            ),
            "D2": SyncResult(
                is_consistent=False,
                combination_tag="Error - verificar datos",
                recommendation=(
                    "ERROR: El sitio tiene score GEO crítico (0-35) pero pérdida comercial "
                    "baja. Esto es contradictorio. VERIFICAR: (1) ¿El scraping fue exitoso? "
                    "(2) ¿Los datos comerciales son actuales? (3) ¿El hotel realmente tiene "
                    "un sitio web funcional? No generar propuesta hasta validar datos."
                ),
                contradiction_report={
                    "type": "error",
                    "detail": "GEO score crítico con pérdida comercial baja",
                    "geo_band": geo_band.value,
                    "loss_level": loss_level.value,
                    "action": "verificar_datos",
                    "geo_score": getattr(geo_assessment, "total_score", "unknown"),
                    "perdida": commercial_diagnosis.get("perdida_mensual_total", 0)
                },
                sync_score=0.2
            ),
        }
        
        return results.get(combination, results["B2"])

    def get_sync_summary(self, result: SyncResult) -> str:
        """Generate a human-readable summary of the sync result.
        
        Args:
            result: SyncResult from analyze()
            
        Returns:
            Formatted string summary.
        """
        lines = [
            "=" * 60,
            "SYNC CONTRACT SUMMARY",
            "=" * 60,
            f"Consistente: {'✅ Sí' if result.is_consistent else '❌ No'}",
            f"Combinación: {result.combination_tag}",
            f"Sync Score: {result.sync_score:.2f}",
            "",
            "RECOMENDACIÓN:",
            result.recommendation,
        ]
        
        if result.contradiction_report:
            lines.extend([
                "",
                "REPORTE DE CONTRADICCIÓN:",
                f"  Tipo: {result.contradiction_report.get('type', 'N/A')}",
                f"  Detalle: {result.contradiction_report.get('detail', 'N/A')}",
                f"  Acción: {result.contradiction_report.get('action', 'N/A')}",
            ])
        
        lines.append("=" * 60)
        return "\n".join(lines)


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def analyze_sync(
    commercial_diagnosis: Dict[str, Any],
    geo_assessment: Any
) -> SyncResult:
    """Convenience function for quick sync analysis.
    
    Args:
        commercial_diagnosis: Commercial diagnosis dict.
        geo_assessment: GEOAssessment object.
        
    Returns:
        SyncResult with analysis.
    """
    analyzer = SyncContractAnalyzer()
    return analyzer.analyze(commercial_diagnosis, geo_assessment)
