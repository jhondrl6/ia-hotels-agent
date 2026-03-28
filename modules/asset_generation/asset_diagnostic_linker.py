"""
Asset-Diagnostic Linker for v4.0.

Vincula los assets generados con los problemas del diagnóstico.
Enriquece la metadata de los assets con justificación.
"""

import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..commercial_documents.data_structures import (
    DiagnosticDocument,
    AssetSpec,
    ConfidenceLevel
)
from ..commercial_documents.coherence_validator import CoherenceReport
from ..commercial_documents.pain_solution_mapper import PainSolutionMapper
from .asset_catalog import ASSET_CATALOG, is_asset_implemented


@dataclass
class AssetDiagnosticLink:
    """Vínculo entre un asset y los problemas que resuelve."""
    asset_type: str
    asset_path: str
    pain_ids: List[str]
    pain_descriptions: List[str]
    justification: str
    confidence_score: float
    expected_impact: str


@dataclass
class AssetMetadata:
    """Metadata enriquecida para cada asset."""
    asset_type: str
    generated_at: str
    confidence_level: str  # VERIFIED, ESTIMATED
    validation_sources: List[str]
    preflight_status: str
    can_use: bool
    disclaimer: str
    source_data_hash: str
    diagnostic_reference: str  # Path al diagnóstico
    problems_solved: List[str]
    coherence_score: float
    confidence_score: float = 0.0  # BUG B FIX: Added missing field (with default at end)
    # Campos de conexión con narrativa de diagnóstico
    problem_solved: str = ""
    impact_cop: int = 0
    priority: str = ""
    timing: str = ""
    why_this_asset: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "asset_type": self.asset_type,
            "generated_at": self.generated_at,
            "confidence_level": self.confidence_level,
            "confidence_score": self.confidence_score,  # BUG B FIX: Include score
            "validation_sources": self.validation_sources,
            "preflight_status": self.preflight_status,
            "can_use": self.can_use,
            "disclaimer": self.disclaimer,
            "source_data_hash": self.source_data_hash,
            "diagnostic_reference": self.diagnostic_reference,
            "problems_solved": self.problems_solved,
            "coherence_score": round(self.coherence_score, 2),
            # Nueva metadata de conexión narrativa
            "problem_solved": self.problem_solved,
            "impact_cop": self.impact_cop,
            "priority": self.priority,
            "timing": self.timing,
            "why_this_asset": self.why_this_asset
        }


class AssetDiagnosticLinker:
    """
    Vincula los assets generados con los problemas del diagnóstico.
    Enriquece la metadata de los assets con justificación.
    """
    
    def __init__(self):
        self.pain_mapper = PainSolutionMapper()
    
    def create_links(
        self,
        generated_assets: List,
        diagnostic_doc: DiagnosticDocument
    ) -> List[AssetDiagnosticLink]:
        """
        Crea vínculos entre assets y problemas del diagnóstico.
        """
        links = []
        
        for asset in generated_assets:
            pain_descriptions = []
            
            # Find problem descriptions
            for problem in diagnostic_doc.problems:
                problem_id = getattr(problem, 'id', problem.get('id') if isinstance(problem, dict) else '')
                if problem_id in asset.pain_ids_resolved:
                    desc = getattr(problem, 'description', problem.get('description', '') if isinstance(problem, dict) else '')
                    pain_descriptions.append(desc)
            
            # Get expected impact
            expected_impact = self._get_expected_impact(asset.asset_type)
            
            # Generate justification
            justification = self.generate_justification(
                asset.asset_type,
                asset.pain_ids_resolved,
                diagnostic_doc
            )
            
            links.append(AssetDiagnosticLink(
                asset_type=asset.asset_type,
                asset_path=asset.path,
                pain_ids=asset.pain_ids_resolved,
                pain_descriptions=pain_descriptions,
                justification=justification,
                confidence_score=asset.confidence_score,
                expected_impact=expected_impact
            ))
        
        return links
    
    def enrich_asset_metadata(
        self,
        base_metadata: Dict[str, Any],
        asset_spec: AssetSpec,
        diagnostic_doc: DiagnosticDocument,
        coherence_report: CoherenceReport,
        original_confidence_score: float = 0.0  # BUG B FIX: Added parameter
    ) -> AssetMetadata:
        """
        Enriquece la metadata base del asset con:
        - Referencia al diagnóstico
        - Problemas que resuelve
        - Score de coherencia
        - Justificación de la recomendación
        
        Args:
            base_metadata: Metadata original del asset
            asset_spec: Especificación del asset
            diagnostic_doc: Documento de diagnóstico
            coherence_report: Reporte de coherencia
            original_confidence_score: Score de confianza original del asset (BUG B FIX)
        """
        # Determine confidence level string
        if isinstance(asset_spec.confidence_level, ConfidenceLevel):
            conf_level = asset_spec.confidence_level.value
        else:
            conf_level = str(asset_spec.confidence_level)
        
        # Build list of problems solved
        problems_solved = []
        for problem in diagnostic_doc.problems:
            problem_id = getattr(problem, 'id', problem.get('id') if isinstance(problem, dict) else '')
            if problem_id in asset_spec.pain_ids:
                name = getattr(problem, 'name', problem.get('name', problem_id) if isinstance(problem, dict) else problem_id)
                problems_solved.append(name)
        
        # Generate disclaimer based on confidence
        disclaimer = self._generate_disclaimer(conf_level, asset_spec.asset_type)
        
        # Map asset type to narrative fields (pass financial_impact for dynamic impact_cop)
        narrative_fields = self._get_narrative_fields(
            asset_spec.asset_type, 
            diagnostic_doc,
            financial_scenario=diagnostic_doc.financial_impact if hasattr(diagnostic_doc, 'financial_impact') else None
        )
        
        # BUG B FIX: Use original confidence_score if available, otherwise derive from confidence_level
        if original_confidence_score > 0:
            final_confidence_score = original_confidence_score
        else:
            # Derive score from confidence_level if not provided
            # Normalize to uppercase for comparison (confidence_level may come as string or enum)
            conf_level_upper = conf_level.upper() if conf_level else ""
            if conf_level_upper == "VERIFIED":
                final_confidence_score = 0.9
            elif conf_level_upper == "ESTIMATED":
                final_confidence_score = 0.6
            elif conf_level_upper == "CONFLICT":
                final_confidence_score = 0.3
            else:
                final_confidence_score = 0.5
        
        return AssetMetadata(
            asset_type=asset_spec.asset_type,
            generated_at=datetime.now().isoformat(),
            confidence_level=conf_level,
            confidence_score=final_confidence_score,  # BUG B FIX: Use proper score
            validation_sources=["web_scraping", "google_business_profile", "user_input"],
            preflight_status="PASSED" if conf_level == "VERIFIED" else "WARNING",
            can_use=conf_level in ["VERIFIED", "ESTIMATED"],
            disclaimer=disclaimer,
            source_data_hash=self._hash_data({
                "asset_type": asset_spec.asset_type,
                "problems": problems_solved,
                "timestamp": datetime.now().isoformat()
            }),
            diagnostic_reference=diagnostic_doc.path,
            problems_solved=problems_solved,
            coherence_score=coherence_report.overall_score,
            problem_solved=narrative_fields.get("problem_solved", ""),
            impact_cop=narrative_fields.get("impact_cop", 0),
            priority=narrative_fields.get("priority", ""),
            timing=narrative_fields.get("timing", ""),
            why_this_asset=narrative_fields.get("why_this_asset", "")
        )
    
    def generate_justification(
        self,
        asset_type: str,
        pain_ids: List[str],
        diagnostic_doc: DiagnosticDocument
    ) -> str:
        """
        Genera texto justificando por qué este asset resuelve estos problemas.
        """
        # Check if asset is implemented
        if not is_asset_implemented(asset_type):
            return (
                f"Este asset ({asset_type}) actualmente no está implementado en el sistema. "
                f"Fue prometido para resolver: {', '.join(pain_ids) if pain_ids else 'problemas identificados'}. "
                "Por favor contacte al equipo de desarrollo para más información."
            )
        
        # Use hardcoded justifications for implemented assets
        justifications = {
            "whatsapp_button": (
                "El botón WhatsApp resuelve el problema de falta de canal directo de "
                "comunicación permitiendo a los huéspedes contactar directamente al hotel "
                "desde cualquier página. Esto reduce la fricción en el proceso de reserva "
                "y aumenta las conversiones del canal directo."
            ),
            "faq_page": (
                "La página de FAQ mejora la experiencia del usuario respondiendo preguntas "
                "comunes de forma inmediata, reduciendo la carga del equipo de atención "
                "y mejorando el SEO mediante schema markup estructurado."
            ),
            "hotel_schema": (
                "El schema de Hotel mejora la visibilidad en resultados de búsqueda de Google, "
                "permitiendo mostrar información enriquecida como precios, disponibilidad "
                "y reseñas directamente en los resultados de búsqueda."
            ),
            "financial_projection": (
                "La proyección financiera cuantifica el impacto potencial de las mejoras, "
                "proporcionando una base objetiva para la toma de decisiones y demostrando "
                "el ROI esperado de la implementación."
            ),
            "geo_playbook": (
                "El Playbook de Geolocalización optimiza la presencia en Google Business "
                "Profile, mejorando la visibilidad local y atrayendo más tráfico cualificado "
                "desde búsquedas con intención de reserva."
            ),
            "review_plan": (
                "El Plan de Gestión de Reviews establece un sistema para aumentar y gestionar "
                "las reseñas, mejorando la reputación online y aumentando la confianza de "
                "potenciales huéspedes."
            ),
            "optimization_guide": (
                "La Guía de Optimización SEO aborda problemas de metadatos por defecto del CMS, "
                "mejorando el SEO on-page y la visibilidad en búsquedas orgánicas. "
                "Incluye recomendaciones específicas para títulos, descripciones y schema markup."
            ),
            "performance_audit": (
                "La Auditoría de Performance analiza Core Web Vitals (LCP, FID, CLS) y "
                "proporciona recomendaciones concretas para mejorar los tiempos de carga, "
                "lo cual impacta directamente en la experiencia del usuario y el ranking de Google."
            ),
            "direct_booking_campaign": (
                "La Campaña de Reserva Directa requiere implementación manual ya que involucra "
                "estrategia de email/SMS personalizada. Esta acción debe coordinarse con el "
                "equipo de marketing del hotel."
            )
        }
        
        default_justification = (
            f"Este asset ({asset_type}) resuelve problemas identificados en el diagnóstico "
            f"relacionados con: {', '.join(pain_ids)}."
        )
        
        return justifications.get(asset_type, default_justification)
    
    def save_enriched_metadata(
        self,
        asset_path: str,
        metadata: AssetMetadata
    ) -> str:
        """
        Guarda la metadata enriquecida junto al asset.
        {asset_name}_metadata.json
        """
        if not asset_path:
            return ""
        
        path = Path(asset_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        metadata_path = path.parent / f"{path.stem}_metadata.json"
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata.to_dict(), f, indent=2, ensure_ascii=False)
        
        return str(metadata_path)
    
    def _get_expected_impact(self, asset_type: str) -> str:
        """Get expected impact level for an asset type."""
        impact_map = {
            "whatsapp_button": "high",
            "hotel_schema": "high",
            "geo_playbook": "high",
            "barra_reserva_movil": "high",
            "direct_booking_campaign": "high",
            "faq_page": "medium",
            "performance_audit": "medium",
            "optimization_guide": "medium",
            "review_plan": "medium",
            "review_widget": "low",
            "org_schema": "low"
        }
        return impact_map.get(asset_type, "medium")
    
    def _generate_disclaimer(self, confidence_level: str, asset_type: str) -> str:
        """Generate appropriate disclaimer based on confidence."""
        disclaimers = {
            "VERIFIED": (
                "Este asset fue generado con datos verificados de múltiples fuentes. "
                "Puede usarse con confianza en producción."
            ),
            "ESTIMATED": (
                "Este asset fue generado con datos estimados o de una sola fuente. "
                "Se recomienda verificar antes de usar en producción."
            ),
            "CONFLICT": (
                "Este asset fue generado con datos en conflicto entre fuentes. "
                "NO usar en producción hasta resolver las inconsistencias."
            )
        }
        
        base_disclaimer = disclaimers.get(confidence_level, disclaimers["ESTIMATED"])
        
        # Add asset-specific notes
        if asset_type == "whatsapp_button":
            base_disclaimer += " Verifique que el número de WhatsApp es correcto."
        elif asset_type == "hotel_schema":
            base_disclaimer += " Verifique que todos los datos del hotel son correctos."
        elif asset_type == "optimization_guide":
            base_disclaimer += " Verifique que los metadatos recomendados sean relevantes para su propiedad."
        elif asset_type == "performance_audit":
            base_disclaimer += " Los valores de Core Web Vitals dependen de la configuración técnica del servidor y CDN."
        
        return base_disclaimer
    
    def _get_narrative_fields(
        self, 
        asset_type: str, 
        diagnostic_doc: DiagnosticDocument,
        financial_scenario: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Get narrative fields for an asset type based on the diagnostic.
        
        Args:
            asset_type: Type of asset
            diagnostic_doc: Diagnostic document
            financial_scenario: Optional financial scenario (Scenario object) for dynamic impact_cop calculation.
                               If not provided, uses default hardcoded values.
        
        Returns:
            Dict with problem_solved, impact_cop, priority, timing, why_this_asset
        """
        # Asset weight mapping based on estimated_impact
        ASSET_WEIGHTS = {
            "high": 0.40,
            "medium": 0.25,
            "low": 0.15
        }
        
        def _get_asset_estimated_impact(asset_type: str) -> Optional[str]:
            """Look up estimated_impact for an asset type from PAIN_SOLUTION_MAP."""
            for pain_data in self.pain_mapper.PAIN_SOLUTION_MAP.values():
                if asset_type in pain_data.get("assets", []):
                    return pain_data.get("estimated_impact")
            return None
        
        # Default values
        narrative_fields = {
            "problem_solved": "Problema identificado en el diagnóstico",
            "impact_cop": 0,
            "priority": "P3",
            "timing": "Semana 1",
            "why_this_asset": "Mejora la presencia online del hotel"
        }
        
        # Map asset types to specific narrative fields (problem_solved, priority, timing, why_this_asset)
        # impact_cop is calculated dynamically from financial_scenario when available
        asset_narratives = {
            "whatsapp_button": {
                "problem_solved": "Falta de canal directo de comunicación",
                "priority": "P1",
                "timing": "30 minutos",
                "why_this_asset": "Permite contacto instantáneo con huéspedes, aumentando reservas directas"
            },
            "faq_page": {
                "problem_solved": "Ausencia de Schema FAQ que pierde rich snippets",
                "priority": "P1",
                "timing": "30 minutos",
                "why_this_asset": "Activa rich snippets en Google y mejora citación en ChatGPT"
            },
            "hotel_schema": {
                "problem_solved": "Falta de schema de hotel estructurado",
                "priority": "P1",
                "timing": "1 hora",
                "why_this_asset": "Muestra información enriquecida en Google (precios, disponibilidad, reseñas)"
            },
            "geo_playbook": {
                "problem_solved": "Baja puntuación en Google Business Profile",
                "priority": "P1",
                "timing": "Día 2",
                "why_this_asset": "Optimiza perfil de Google Maps para atraer búsquedas locales con intención de reserva"
            },
            "review_plan": {
                "problem_solved": "Gestión ineficiente de reseñas online",
                "priority": "P2",
                "timing": "Día 3",
                "why_this_asset": "Establece sistema para aumentar y gestionar reseñas, mejorando reputación online"
            },
            "review_widget": {
                "problem_solved": "Falta de widget de reseñas visible en sitio web",
                "priority": "P2",
                "timing": "Día 2",
                "why_this_asset": "Muestra reseñas recientes para generar confianza en potenciales huéspedes"
            },
            "org_schema": {
                "problem_solved": "Ausencia de schema de organización",
                "priority": "P3",
                "timing": "Semana 2",
                "why_this_asset": "Ayuda a Google a entender mejor la estructura del negocio hotelero"
            },
            "barra_reserva_movil": {
                "problem_solved": "Falta de motor de reservas visible en móvil",
                "priority": "P1",
                "timing": "Semana 1",
                "why_this_asset": "Facilita reservas directas desde dispositivos móviles, reduciendo dependencia de OTAs"
            },
            "financial_projection": {
                "problem_solved": "Falta de proyección financiera cuantificada",
                "priority": "P2",
                "timing": "Día 1",
                "why_this_asset": "Proporciona base objetiva para toma de decisiones y demuestra ROI esperado"
            },
            "performance_audit": {
                "problem_solved": "Problemas de rendimiento web que afectan experiencia de usuario",
                "priority": "P2",
                "timing": "Día 2",
                "why_this_asset": "Analiza Core Web Vitals y ofrece recomendaciones para mejorar velocidad de carga"
            },
            "optimization_guide": {
                "problem_solved": "Metadatos por defecto del CMS que dañan SEO",
                "priority": "P2",
                "timing": "Día 3",
                "why_this_asset": "Aborda problemas de títulos, descripciones y schema markup para mejorar visibilidad orgánica"
            },
            "direct_booking_campaign": {
                "problem_solved": "Dependencia excesiva de OTAs con altas comisiones",
                "priority": "P1",
                "timing": "Semana 2",
                "why_this_asset": "Campaña de email/SMS personalizada para aumentar reservas directas"
            },
            "llms_txt": {
                "problem_solved": "Falta de archivo llms.txt para orientación de crawlers de IA",
                "priority": "P3",
                "timing": "30 minutos",
                "why_this_asset": "Facilita que los modelos de lenguaje entiendan y representen correctamente el hotel"
            }
        }
        
        # Start with defaults
        result = narrative_fields.copy()
        
        # Override with asset-specific narrative if available
        if asset_type in asset_narratives:
            result.update(asset_narratives[asset_type])
        
        # Calculate impact_cop dynamically if financial_scenario is available
        # and has valid numeric monthly_loss_max
        if financial_scenario is not None:
            monthly_loss_max = getattr(financial_scenario, 'monthly_loss_max', None)
            # Only calculate if monthly_loss_max is a valid number
            if monthly_loss_max is not None and isinstance(monthly_loss_max, (int, float)) and monthly_loss_max > 0:
                estimated_impact = _get_asset_estimated_impact(asset_type)
                if estimated_impact and estimated_impact in ASSET_WEIGHTS:
                    weight = ASSET_WEIGHTS[estimated_impact]
                    result["impact_cop"] = int(monthly_loss_max * weight)
                else:
                    # Fallback for assets not in PAIN_SOLUTION_MAP - use medium weight
                    result["impact_cop"] = int(monthly_loss_max * 0.25)
        
        return result

    def _hash_data(self, data: Dict) -> str:
        """Create hash of data for tracking."""
        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(data_str.encode()).hexdigest()[:16]
        except Exception:
            return "unknown"


__all__ = [
    'AssetDiagnosticLinker',
    'AssetDiagnosticLink',
    'AssetMetadata'
]
