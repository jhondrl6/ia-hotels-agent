"""Coherence Gate - Gate de Coherencia Global.

Bloquea documentos con baja coherencia entre fuentes de evidencia.
Umbral configurable, por defecto 0.8.

H10 FIX: Unificado con CoherenceValidator para evitar métricas duplicadas.
Usa CoherenceValidator internamente como fuente única de verdad.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
from datetime import datetime, timezone

# H10 FIX: Importar CoherenceValidator como fuente única de verdad
from ..commercial_documents.coherence_validator import CoherenceValidator, CoherenceReport


class CoherenceStatus(Enum):
    """Estados de coherencia del assessment."""
    CERTIFIED = "certified"  # Coherence >= 0.8
    REVIEW = "review"        # Coherence 0.5-0.8
    DRAFT_INTERNAL = "draft_internal"  # Coherence < 0.5
    INSUFFICIENT = "insufficient"  # Sin datos suficientes


class PublicationStatus(Enum):
    """Estados de publicación posibles."""
    READY_FOR_CLIENT = "ready_for_client"
    REQUIRES_REVIEW = "requires_review"
    DRAFT_INTERNAL = "draft_internal"
    BLOCKED = "blocked"


@dataclass
class CoherenceGap:
    """Un gap de coherencia identificado."""
    category: str
    description: str
    severity: str  # high, medium, low
    suggestion: str


@dataclass
class CoherenceGateResult:
    """Resultado del gate de coherencia."""
    coherence_score: float
    threshold: float
    passed: bool
    status: CoherenceStatus
    publication_status: PublicationStatus
    gaps: List[CoherenceGap] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    # FASE-1-COH: campos del validator integration
    checks: Optional[List[Dict[str, Any]]] = None
    validator_errors: Optional[List[str]] = None
    validator_warnings: Optional[List[str]] = None
    
    @property
    def can_certify(self) -> bool:
        """True si puede ser certificado."""
        return self.status == CoherenceStatus.CERTIFIED
    
    @property
    def can_publish(self) -> bool:
        """True si puede publicarse al cliente."""
        return self.publication_status == PublicationStatus.READY_FOR_CLIENT
    
    @property
    def requires_review(self) -> bool:
        """True si requiere revisión manual."""
        return self.publication_status == PublicationStatus.REQUIRES_REVIEW
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa resultado a diccionario."""
        result = {
            "coherence_score": round(self.coherence_score, 4),
            "threshold": self.threshold,
            "passed": self.passed,
            "status": self.status.value,
            "publication_status": self.publication_status.value,
            "can_certify": self.can_certify,
            "can_publish": self.can_publish,
            "requires_review": self.requires_review,
            "gaps": [
                {
                    "category": g.category,
                    "description": g.description,
                    "severity": g.severity,
                    "suggestion": g.suggestion,
                }
                for g in self.gaps
            ],
            "suggestions": self.suggestions,
            "timestamp": self.timestamp.isoformat(),
        }
        # FASE-1-COH: incluir datos del validator si disponibles
        if self.checks is not None:
            result["checks"] = self.checks
        if self.validator_errors is not None:
            result["validator_errors"] = self.validator_errors
        if self.validator_warnings is not None:
            result["validator_warnings"] = self.validator_warnings
        return result
    
    def to_user_message(self) -> str:
        """Genera mensaje para el usuario."""
        if self.passed:
            return (
                f"✅ Coherencia validada: {self.coherence_score:.1%} "
                f"(umbral: {self.threshold:.1%})"
            )
        
        messages = [
            f"⚠️ Coherencia insuficiente: {self.coherence_score:.1%}",
            f"   Umbral requerido: {self.threshold:.1%}",
            "",
            f"Estado: {self.status.value}",
            f"Publicación: {self.publication_status.value}",
        ]
        
        if self.gaps:
            messages.extend(["", "Gaps identificados:"])
            for gap in self.gaps:
                messages.append(f"  • [{gap.severity.upper()}] {gap.description}")
        
        if self.suggestions:
            messages.extend(["", "Sugerencias de mejora:"])
            for suggestion in self.suggestions:
                messages.append(f"  → {suggestion}")
        
        return "\n".join(messages)


class CoherenceGate:
    """Gate de coherencia global del assessment.
    
    Valida que el coherence_score cumpla con el umbral mínimo
    requerido para certificar documentos.
    
    H10 FIX: Ahora usa CoherenceValidator internamente como fuente única
    de verdad, evitando métricas duplicadas. Mantiene API pública compatible.
    
    Umbrales configurables en .conductor/guidelines.yaml:
    - overall_coherence: 0.8 (por defecto)
    
    Estados resultantes:
    - coherence >= 0.8: CERTIFIED → READY_FOR_CLIENT
    - coherence 0.5-0.8: REVIEW → REQUIRES_REVIEW
    - coherence < 0.5: DRAFT_INTERNAL
    """
    
    DEFAULT_THRESHOLD = 0.8
    REVIEW_THRESHOLD = 0.5
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Inicializa el gate con configuración.
        
        Args:
            config: Configuración opcional con 'threshold'
        """
        self.config = config or {}
        self.threshold = self.config.get(
            "threshold", 
            self.DEFAULT_THRESHOLD
        )
        # H10 FIX: Usar CoherenceValidator como fuente única
        self._validator = CoherenceValidator()
    
    def execute(
        self, 
        coherence_score: Optional[float] = None,
        assessment_data: Optional[Dict[str, Any]] = None,
        # FASE-1-COH: params para integración con validator
        diagnostic: Optional[Any] = None,
        proposal: Optional[Any] = None,
        assets: Optional[List[Any]] = None,
        validation_summary: Optional[Any] = None,
        generated_assets: Optional[Dict[str, Any]] = None,
        whatsapp_html_detected: bool = False,
    ) -> CoherenceGateResult:
        """Ejecuta el gate de coherencia.
        
        FASE-1-COH: Si se proporcionan diagnostic/proposal/assets/validation_summary,
        usa CoherenceValidator internamente como fuente única de verdad.
        Si solo se proporciona coherence_score, mantiene backward compatibility.
        
        Args:
            coherence_score: Score de coherencia actual (0-1) — backward compat
            assessment_data: Datos adicionales del assessment — backward compat
            diagnostic: DiagnosticDocument para validator (FASE-1-COH)
            proposal: ProposalDocument para validator (FASE-1-COH)
            assets: Lista de AssetSpec para validator (FASE-1-COH)
            validation_summary: ValidationSummary para validator (FASE-1-COH)
            generated_assets: Assets generados para validator (FASE-1-COH)
            whatsapp_html_detected: Flag para validator (FASE-1-COH)
            
        Returns:
            CoherenceGateResult con resultado de validación
        """
        # FASE-1-COH: Si hay datos completos, usar validator como fuente única
        if diagnostic is not None and proposal is not None and assets is not None and validation_summary is not None:
            return self.execute_from_validator(
                diagnostic=diagnostic,
                proposal=proposal,
                assets=assets,
                validation_summary=validation_summary,
                generated_assets=generated_assets,
                whatsapp_html_detected=whatsapp_html_detected,
                assessment_data=assessment_data,
            )
        
        # --- COMPORTAMIENTO LEGACY (backward compatible) ---
        # Si no hay coherence_score explícito, intentar extraer de assessment_data
        if coherence_score is None:
            coherence_score = (assessment_data or {}).get("coherence_score", 0.0)
        
        # 1. Validar que coherence_score está en rango válido
        if not isinstance(coherence_score, (int, float)):
            coherence_score = 0.0
        
        coherence_score = max(0.0, min(1.0, float(coherence_score)))
        
        # 2. Determinar si pasa el umbral
        passed = coherence_score >= self.threshold
        
        # 3. Identificar gaps si los hay
        assessment_data = assessment_data or {}
        gaps = self._identify_gaps(coherence_score, assessment_data)
        
        # 4. Generar sugerencias de mejora
        suggestions = self._generate_suggestions(coherence_score, gaps)
        
        # 5. Determinar estado de publicación
        status, pub_status = self._determine_status(coherence_score)
        
        return CoherenceGateResult(
            coherence_score=coherence_score,
            threshold=self.threshold,
            passed=passed,
            status=status,
            publication_status=pub_status,
            gaps=gaps,
            suggestions=suggestions,
        )
    
    def execute_from_validator(
        self,
        diagnostic: Any,
        proposal: Any,
        assets: List[Any],
        validation_summary: Any,
        generated_assets: Optional[Dict[str, Any]] = None,
        whatsapp_html_detected: bool = False,
        assessment_data: Optional[Dict[str, Any]] = None,
    ) -> CoherenceGateResult:
        """FASE-1-COH: Ejecuta el gate usando CoherenceValidator como fuente única.
        
        Llama a self._validator.validate() y produce un CoherenceGateResult
        basado en el CoherenceReport completo, no solo en un float.
        
        Args:
            diagnostic: DiagnosticDocument
            proposal: ProposalDocument
            assets: Lista de AssetSpec
            validation_summary: ValidationSummary
            generated_assets: Assets generados (opcional)
            whatsapp_html_detected: Flag de WhatsApp detectado en HTML
            assessment_data: Datos adicionales del assessment para gaps legacy
            
        Returns:
            CoherenceGateResult con datos completos del validator
        """
        # 1. Ejecutar validator como fuente única de verdad
        report = self._validator.validate(
            diagnostic=diagnostic,
            proposal=proposal,
            assets=assets,
            validation_summary=validation_summary,
            whatsapp_html_detected=whatsapp_html_detected,
            generated_assets=generated_assets,
        )
        
        coherence_score = report.overall_score
        
        # 2. Determinar si pasa el umbral
        passed = report.is_coherent
        
        # 3. Convertir errores/warnings del validator a gaps del gate
        gaps = self._validator_errors_to_gaps(report)
        
        # 4. Generar sugerencias (del validator + gaps legacy)
        suggestions = self._generate_suggestions(coherence_score, gaps)
        # Agregar warnings del validator como sugerencias adicionales
        for warning in report.warnings:
            if warning not in suggestions:
                suggestions.append(warning)
        
        # 5. Determinar estado de publicación
        status, pub_status = self._determine_status(coherence_score)
        
        # 6. Convertir checks del validator a dicts serializables
        checks_dicts = [
            {
                "name": c.name,
                "passed": c.passed,
                "score": round(c.score, 4),
                "message": c.message,
                "severity": c.severity,
            }
            for c in report.checks
        ]
        
        # 7. Gaps adicionales del assessment_data legacy (si existen)
        assessment_data = assessment_data or {}
        legacy_gaps = self._identify_gaps(coherence_score, assessment_data)
        # Solo agregar gaps legacy que no estén ya cubiertos por el validator
        existing_categories = {g.category for g in gaps}
        for legacy_gap in legacy_gaps:
            if legacy_gap.category not in existing_categories:
                gaps.append(legacy_gap)
        
        return CoherenceGateResult(
            coherence_score=coherence_score,
            threshold=self.threshold,
            passed=passed,
            status=status,
            publication_status=pub_status,
            gaps=gaps,
            suggestions=suggestions,
            checks=checks_dicts,
            validator_errors=report.errors if report.errors else None,
            validator_warnings=report.warnings if report.warnings else None,
        )
    
    def _validator_errors_to_gaps(self, report: Any) -> List[CoherenceGap]:
        """FASE-1-COH: Convierte errores/warnings del CoherenceReport a CoherenceGaps.
        
        Args:
            report: CoherenceReport del validator
            
        Returns:
            Lista de CoherenceGap
        """
        gaps = []
        
        for check in report.checks:
            if not check.passed and check.severity in ("error", "warning"):
                gaps.append(CoherenceGap(
                    category=check.name,
                    description=check.message,
                    severity=check.severity,
                    suggestion=f"Revisar check '{check.name}': {check.message}",
                ))
        
        return gaps
    
    def check(
        self, 
        assessment: Dict[str, Any]
    ) -> CoherenceGateResult:
        """Check convenience que extrae coherence_score del assessment.
        
        Args:
            assessment: Assessment canónico con coherence_score
            
        Returns:
            CoherenceGateResult con resultado
        """
        coherence_score = assessment.get("coherence_score", 0.0)
        return self.execute(coherence_score, assessment)
    
    def _identify_gaps(
        self, 
        coherence_score: float,
        assessment_data: Dict[str, Any]
    ) -> List[CoherenceGap]:
        """Identifica gaps específicos de coherencia.
        
        Args:
            coherence_score: Score actual
            assessment_data: Datos del assessment
            
        Returns:
            Lista de gaps identificados
        """
        gaps = []
        
        # Evidencia insuficiente
        if coherence_score < 0.5:
            gaps.append(CoherenceGap(
                category="evidence",
                description="Evidencia insuficiente para certificar",
                severity="high",
                suggestion="Agregue más fuentes de evidencia (GBP, PageSpeed, datos del hotel)"
            ))
        
        # Claims sin verificar
        unverified_claims = assessment_data.get("unverified_claims", [])
        if unverified_claims:
            gaps.append(CoherenceGap(
                category="claims",
                description=f"{len(unverified_claims)} claims sin verificar",
                severity="medium",
                suggestion="Verifique los claims con fuentes externas"
            ))
        
        # Contradicciones no resueltas
        contradictions = assessment_data.get("contradictions", [])
        if contradictions:
            gaps.append(CoherenceGap(
                category="contradictions",
                description=f"{len(contradictions)} contradicciones sin resolver",
                severity="high",
                suggestion="Resuelva las contradicciones entre fuentes de datos"
            ))
        
        # Datos GBP faltantes
        gbp_data = assessment_data.get("gbp_data", {})
        if not gbp_data:
            gaps.append(CoherenceGap(
                category="gbp",
                description="Datos de Google Business Profile no disponibles",
                severity="medium",
                suggestion="Conecte y valide el perfil de GBP"
            ))
        
        # Datos financieros incompletos
        financial = assessment_data.get("financial_assessment", {})
        if not financial or financial.get("confidence", 0) < 0.7:
            gaps.append(CoherenceGap(
                category="financial",
                description="Datos financieros incompletos o de baja confianza",
                severity="medium",
                suggestion="Complete los datos financieros del hotel"
            ))
        
        return gaps
    
    def _generate_suggestions(
        self, 
        coherence_score: float,
        gaps: List[CoherenceGap]
    ) -> List[str]:
        """Genera sugerencias para mejorar coherencia.
        
        Args:
            coherence_score: Score actual
            gaps: Gaps identificados
            
        Returns:
            Lista de sugerencias
        """
        suggestions = []
        
        # Sugerencias basadas en score
        if coherence_score < 0.3:
            suggestions.append(
                "Complete el onboarding con todos los datos del hotel"
            )
            suggestions.append(
                "Verifique la URL del sitio web y el perfil de GBP"
            )
        elif coherence_score < 0.5:
            suggestions.append(
                "Agregue más fuentes de evidencia (GBP, PageSpeed)"
            )
        elif coherence_score < 0.8:
            suggestions.append(
                "Resuelva las contradicciones suaves identificadas"
            )
            suggestions.append(
                "Verifique claims con baja confianza"
            )
        
        # Sugerencias específicas por gap
        for gap in gaps:
            if gap.severity == "high":
                suggestions.append(f"Priorice: {gap.suggestion}")
        
        return suggestions
    
    def _determine_status(
        self, 
        coherence_score: float
    ) -> Tuple[CoherenceStatus, PublicationStatus]:
        """Determina estados basado en score.
        
        Args:
            coherence_score: Score de coherencia
            
        Returns:
            Tuple de (CoherenceStatus, PublicationStatus)
        """
        if coherence_score >= self.DEFAULT_THRESHOLD:
            return (CoherenceStatus.CERTIFIED, PublicationStatus.READY_FOR_CLIENT)
        elif coherence_score >= self.REVIEW_THRESHOLD:
            return (CoherenceStatus.REVIEW, PublicationStatus.REQUIRES_REVIEW)
        else:
            return (CoherenceStatus.DRAFT_INTERNAL, PublicationStatus.DRAFT_INTERNAL)
    
    @staticmethod
    def from_guidelines(guidelines_path: str | None = None) -> "CoherenceGate":
        """Crea gate desde configuracion centralizada.
        
        Nota: .conductor/guidelines.yaml fue eliminado. Este metodo ahora
        delega en CoherenceConfig (fuente unica de verdad en defaults).
        El parametro guidelines_path se ignora por compatibilidad.
        
        Returns:
            CoherenceGate con umbrales canonicos
        """
        return CoherenceGate()


def check_coherence(
    coherence_score: float,
    threshold: float = 0.8
) -> CoherenceGateResult:
    """Función helper para validar coherencia rápidamente.
    
    Args:
        coherence_score: Score a validar
        threshold: Umbral mínimo
        
    Returns:
        CoherenceGateResult con resultado
    """
    gate = CoherenceGate(config={"threshold": threshold})
    return gate.execute(coherence_score)
