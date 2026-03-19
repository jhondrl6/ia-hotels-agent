"""Coherence Gate - Gate de Coherencia Global.

Bloquea documentos con baja coherencia entre fuentes de evidencia.
Umbral configurable, por defecto 0.8.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
from datetime import datetime, timezone


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
        return {
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
    
    def execute(
        self, 
        coherence_score: float,
        assessment_data: Optional[Dict[str, Any]] = None
    ) -> CoherenceGateResult:
        """Ejecuta el gate de coherencia.
        
        Args:
            coherence_score: Score de coherencia actual (0-1)
            assessment_data: Datos adicionales del assessment
            
        Returns:
            CoherenceGateResult con resultado de validación
        """
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
    def from_guidelines(guidelines_path: str = ".conductor/guidelines.yaml") -> "CoherenceGate":
        """Crea gate desde archivo de guidelines.
        
        Args:
            guidelines_path: Ruta al archivo YAML
            
        Returns:
            CoherenceGate configurado
        """
        import yaml
        
        try:
            with open(guidelines_path, 'r') as f:
                guidelines = yaml.safe_load(f)
            
            v4_rules = guidelines.get("v4_coherence_rules", {})
            overall = v4_rules.get("overall_coherence", {})
            threshold = overall.get("confidence_threshold", 0.8)
            
            return CoherenceGate(config={"threshold": threshold})
        except Exception:
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
