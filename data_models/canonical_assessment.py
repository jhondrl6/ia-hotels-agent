"""Canonical Assessment - Modelo unificado de análisis de hotel.

Sprint 1, Fase 0: Estructura canónica que agrupa todo el análisis
realizado sobre un sitio web de hotel.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

from enums.confidence_level import ConfidenceLevel
from enums.severity import Severity


class SiteMetadata(BaseModel):
    """Metadatos del sitio web analizado.

    Attributes:
        title: Título del sitio (tag <title>).
        description: Meta description del sitio.
        cms_detected: CMS detectado (WordPress, etc.) o None.
        has_default_title: True si el título parece ser el default del CMS.
        detected_language: Idioma detectado del sitio (ej: "es", "en").
        viewport_meta: True si tiene meta viewport (responsive).
    """

    title: str = Field(..., description="Título del sitio web")
    description: Optional[str] = Field(None, description="Meta description")
    cms_detected: Optional[str] = Field(None, description="CMS detectado")
    has_default_title: bool = Field(
        default=False, description="True si usa título por defecto del CMS"
    )
    detected_language: Optional[str] = Field(None, description="Idioma detectado (ISO 639-1)")
    viewport_meta: Optional[bool] = Field(None, description="Tiene meta viewport")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Hotel Visperas - Oaxaca",
                "description": "Hotel boutique en el centro histórico de Oaxaca",
                "cms_detected": "WordPress",
                "has_default_title": False,
                "detected_language": "es",
                "viewport_meta": True,
            }
        }


class SchemaAnalysis(BaseModel):
    """Análisis de Schema.org implementado en el sitio.

    Attributes:
        schema_type: Tipo principal de schema (Hotel, Organization, etc.).
        coverage_score: Score de cobertura de campos Schema.org (0.0-1.0).
        missing_critical_fields: Lista de campos críticos faltantes.
        present_fields: Lista de campos Schema.org presentes.
        raw_schema: Schema.org completo como dict.
        has_hotel_schema: True si tiene schema Hotel específico.
        has_local_business: True si tiene schema LocalBusiness.
    """

    schema_type: Optional[str] = Field(None, description="Tipo de schema principal")
    coverage_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Score de cobertura 0.0-1.0"
    )
    missing_critical_fields: List[str] = Field(
        default_factory=list, description="Campos críticos faltantes"
    )
    present_fields: List[str] = Field(
        default_factory=list, description="Campos presentes"
    )
    raw_schema: Optional[Dict[str, Any]] = Field(None, description="Schema raw completo")
    has_hotel_schema: bool = Field(default=False, description="Tiene schema Hotel")
    has_local_business: bool = Field(default=False, description="Tiene LocalBusiness")

    @field_validator("coverage_score")
    @classmethod
    def validate_coverage(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("coverage_score must be between 0.0 and 1.0")
        return round(v, 4)


class PerformanceMetrics(BaseModel):
    """Métricas de performance web (Core Web Vitals).

    Attributes:
        lcp: Largest Contentful Paint en segundos.
        fcp: First Contentful Paint en segundos.
        cls: Cumulative Layout Shift (unitless).
        ttfb: Time to First Byte en milisegundos.
        inp: Interaction to Next Paint en milisegundos (si disponible).
        tbt: Total Blocking Time en milisegundos.
    """

    lcp: Optional[float] = Field(None, ge=0, description="Largest Contentful Paint (s)")
    fcp: Optional[float] = Field(None, ge=0, description="First Contentful Paint (s)")
    cls: Optional[float] = Field(None, ge=0, description="Cumulative Layout Shift")
    ttfb: Optional[float] = Field(None, ge=0, description="Time to First Byte (ms)")
    inp: Optional[float] = Field(None, ge=0, description="Interaction to Next Paint (ms)")
    tbt: Optional[float] = Field(None, ge=0, description="Total Blocking Time (ms)")


class PerformanceAnalysis(BaseModel):
    """Análisis completo de performance del sitio.

    Attributes:
        performance_score: Score general de performance (0-100).
        accessibility_score: Score de accesibilidad (0-100).
        metrics: Métricas Core Web Vitals detalladas.
        severity: Nivel de severidad basado en scores.
        has_critical_issues: True si hay problemas críticos de performance.
    """

    performance_score: float = Field(..., ge=0, le=100, description="Score performance 0-100")
    accessibility_score: Optional[float] = Field(
        None, ge=0, le=100, description="Score accesibilidad 0-100"
    )
    metrics: PerformanceMetrics = Field(
        default_factory=PerformanceMetrics, description="Métricas detalladas"
    )
    severity: Severity = Field(default=Severity.LOW, description="Severidad de issues")
    has_critical_issues: bool = Field(default=False, description="Tiene issues críticos")

    @model_validator(mode="after")
    def set_severity(self) -> "PerformanceAnalysis":
        """Determina severidad basada en performance_score y Core Web Vitals."""
        score = self.performance_score
        metrics = self.metrics

        # Umbrales de severidad para métricas
        # CRITICAL: performance < 50 o lcp > 4s o fcp > 3s o cls > 0.25
        if (score < 50 or
            (metrics.lcp and metrics.lcp > 4.0) or
            (metrics.fcp and metrics.fcp > 3.0) or
            (metrics.cls and metrics.cls > 0.25)):
            self.severity = Severity.CRITICAL
            self.has_critical_issues = True
        # HIGH: performance < 70 o lcp > 2.5s o fcp > 1.8s o cls > 0.1
        elif (score < 70 or
              (metrics.lcp and metrics.lcp > 2.5) or
              (metrics.fcp and metrics.fcp > 1.8) or
              (metrics.cls and metrics.cls > 0.1)):
            self.severity = Severity.HIGH
            self.has_critical_issues = True
        # MEDIUM: performance < 90 o lcp > 1.8s o fcp > 1.0s o cls > 0.05
        elif (score < 90 or
              (metrics.lcp and metrics.lcp > 1.8) or
              (metrics.fcp and metrics.fcp > 1.0) or
              (metrics.cls and metrics.cls > 0.05)):
            self.severity = Severity.MEDIUM
        else:
            self.severity = Severity.LOW
        return self


class GBPAnalysis(BaseModel):
    """Análisis del perfil de Google Business Profile.

    Attributes:
        profile_url: URL del perfil GBP.
        rating: Rating promedio (0-5).
        review_count: Número total de reseñas.
        photo_count: Número de fotos en el perfil.
        is_claimed: True si el perfil está verificado/claimed.
        categories: Categorías del negocio.
        hours_available: True si tiene horarios configurados.
        phone_matches: True si el teléfono coincide con el sitio web.
    """

    profile_url: Optional[str] = Field(None, description="URL del perfil GBP")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Rating 0-5")
    review_count: Optional[int] = Field(None, ge=0, description="Cantidad de reseñas")
    photo_count: Optional[int] = Field(None, ge=0, description="Cantidad de fotos")
    is_claimed: Optional[bool] = Field(None, description="Perfil verificado")
    categories: List[str] = Field(default_factory=list, description="Categorías")
    hours_available: Optional[bool] = Field(None, description="Tiene horarios")
    phone_matches: Optional[bool] = Field(None, description="Teléfono coincide con web")

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not 0.0 <= v <= 5.0:
            raise ValueError("rating must be between 0.0 and 5.0")
        return v


class Claim(BaseModel):
    """Claim de validación - afirmación verificable sobre el hotel.

    Attributes:
        claim_id: UUID único del claim.
        source_id: Identificador de la fuente de evidencia.
        timestamp: Fecha/hora de creación.
        confidence: Score de confianza (0.0-1.0).
        confidence_level: Nivel de confianza calculado.
        evidence_excerpt: Extracto verificable de la evidencia.
        severity: Nivel de severidad del claim.
        category: Categoría del claim (metadata, schema, performance, gbp).
        message: Descripción legible del claim.
        field_path: Ruta del campo afectado (opcional).
        raw_evidence: Datos crudos de evidencia (opcional).
        is_actionable: True si requiere acción.
        is_verified: True si está verificado (confianza ≥ 0.9).
        blocks_deployment: True si bloquea publicación.
    """

    # Campos obligatorios
    source_id: str = Field(..., min_length=1, description="Fuente de evidencia")
    evidence_excerpt: str = Field(..., min_length=1, description="Extracto de evidencia")
    severity: Severity = Field(..., description="Nivel de severidad")
    category: str = Field(..., min_length=1, description="Categoría del claim")
    message: str = Field(..., min_length=1, description="Mensaje descriptivo")

    # Campos con defaults
    claim_id: UUID = Field(default_factory=uuid4, description="UUID único")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confianza 0.0-1.0")

    # Campos opcionales
    field_path: Optional[str] = Field(None, description="Ruta del campo")
    raw_evidence: Optional[Dict[str, Any]] = Field(None, description="Evidencia cruda")

    # Propiedades calculadas
    @property
    def confidence_level(self) -> ConfidenceLevel:
        """Determina el nivel de confianza basado en el score."""
        return ConfidenceLevel.from_score(self.confidence)

    @property
    def is_actionable(self) -> bool:
        """True si el claim requiere acción (CRITICAL o HIGH)."""
        return self.severity in (Severity.CRITICAL, Severity.HIGH)

    @property
    def is_verified(self) -> bool:
        """True si está verificado (confianza ≥ 0.9)."""
        return self.confidence >= 0.9

    @property
    def blocks_deployment(self) -> bool:
        """True si bloquea publicación (CRITICAL)."""
        return self.severity == Severity.CRITICAL

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Severity: lambda v: v.value,
        }


class CanonicalAssessment(BaseModel):
    """Evaluación canónica consolidada de un hotel.

    Esta es la estructura unificada que agrupa todo el análisis
    realizado sobre un sitio web de hotel, incluyendo metadatos,
    Schema.org, performance, Google Business Profile y claims
    de validación generados.

    Attributes:
        assessment_id: UUID único del assessment.
        url: URL del sitio web analizado.
        analyzed_at: Fecha/hora del análisis.
        version: Versión del esquema de assessment.
        site_metadata: Metadatos del sitio web.
        schema_analysis: Análisis de Schema.org.
        performance_analysis: Análisis de performance.
        gbp_analysis: Análisis de Google Business Profile (opcional).
        claims: Lista de claims generados.
        coherence_score: Score de coherencia entre fuentes (0.0-1.0).
        evidence_coverage: Porcentaje de claims con evidencia (0.0-1.0).
        hard_contradictions: Número de contradicciones duras detectadas.
    """

    # Identificación
    assessment_id: UUID = Field(default_factory=uuid4, description="UUID único")
    url: str = Field(..., description="URL del sitio analizado")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha análisis")
    version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$", description="Versión")

    # Metadatos del sitio
    site_metadata: SiteMetadata = Field(..., description="Metadatos del sitio")

    # Análisis específicos
    schema_analysis: SchemaAnalysis = Field(..., description="Análisis Schema.org")
    performance_analysis: PerformanceAnalysis = Field(..., description="Análisis performance")
    gbp_analysis: Optional[GBPAnalysis] = Field(None, description="Análisis GBP")

    # Claims y validación
    claims: List[Claim] = Field(default_factory=list, description="Claims generados")
    coherence_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Score coherencia 0.0-1.0"
    )
    evidence_coverage: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Cobertura evidencia 0.0-1.0"
    )
    hard_contradictions: int = Field(default=0, ge=0, description="Contradicciones duras")

    # Opportunity scores (FASE-C: priorizacion ponderada de brechas)
    opportunity_scores: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Lista de brechas con score ponderado (severidad, esfuerzo, impacto, COP)",
    )

    @field_validator("coherence_score", "evidence_coverage")
    @classmethod
    def validate_score_range(cls, v: float) -> float:
        """Valida que los scores estén entre 0.0 y 1.0."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")
        return round(v, 4)

    def get_critical_claims(self) -> List[Claim]:
        """Retorna claims con severidad CRITICAL o HIGH.

        Returns:
            Lista de claims que requieren atención prioritaria.
        """
        return [c for c in self.claims if c.severity in (Severity.CRITICAL, Severity.HIGH)]

    def get_claims_by_category(self, category: str) -> List[Claim]:
        """Filtra claims por categoría.

        Args:
            category: Categoría a filtrar (metadata, schema, performance, gbp).

        Returns:
            Lista de claims de la categoría especificada.
        """
        return [c for c in self.claims if c.category.lower() == category.lower()]

    def get_claims_by_severity(self, severity: Severity) -> List[Claim]:
        """Filtra claims por nivel de severidad.

        Args:
            severity: Nivel de severidad a filtrar.

        Returns:
            Lista de claims con la severidad especificada.
        """
        return [c for c in self.claims if c.severity == severity]

    def get_verified_claims(self) -> List[Claim]:
        """Retorna claims con confianza ≥ 0.9 (VERIFIED).

        Returns:
            Lista de claims verificados.
        """
        return [c for c in self.claims if c.is_verified]

    def get_deployment_blockers(self) -> List[Claim]:
        """Retorna claims que bloquean publicación.

        Returns:
            Lista de claims con severidad CRITICAL.
        """
        return [c for c in self.claims if c.blocks_deployment]

    def get_categories(self) -> Set[str]:
        """Retorna todas las categorías únicas de claims.

        Returns:
            Conjunto de categorías presentes.
        """
        return set(c.category for c in self.claims)

    def add_claim(self, claim: Claim) -> None:
        """Agrega un claim al assessment.

        Args:
            claim: Claim a agregar.
        """
        self.claims.append(claim)
        self._recalculate_metrics()

    def _recalculate_metrics(self) -> None:
        """Recalcula métricas de cobertura después de modificar claims."""
        if not self.claims:
            self.evidence_coverage = 0.0
            return

        with_evidence = sum(1 for c in self.claims if c.source_id)
        self.evidence_coverage = round(with_evidence / len(self.claims), 4)

    def to_dict(self, include_raw: bool = True) -> Dict[str, Any]:
        """Serializa el assessment a diccionario.

        Args:
            include_raw: Si incluir datos raw (schemas, evidencia).

        Returns:
            Diccionario con todos los datos del assessment.
        """
        data = self.model_dump()
        if not include_raw:
            # Remover datos crudos pesados
            data.get("schema_analysis", {}).pop("raw_schema", None)
            for claim in data.get("claims", []):
                claim.pop("raw_evidence", None)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CanonicalAssessment":
        """Crea un CanonicalAssessment desde un diccionario.

        Args:
            data: Diccionario con los datos del assessment.

        Returns:
            Nueva instancia de CanonicalAssessment.
        """
        return cls.model_validate(data)

    def get_summary(self) -> Dict[str, Any]:
        """Genera un resumen ejecutivo del assessment.

        Returns:
            Diccionario con métricas clave del análisis.
        """
        total_claims = len(self.claims)
        critical = len(self.get_claims_by_severity(Severity.CRITICAL))
        high = len(self.get_claims_by_severity(Severity.HIGH))
        medium = len(self.get_claims_by_severity(Severity.MEDIUM))
        low = len(self.get_claims_by_severity(Severity.LOW))
        verified = len(self.get_verified_claims())

        return {
            "url": self.url,
            "analyzed_at": self.analyzed_at.isoformat(),
            "version": self.version,
            "total_claims": total_claims,
            "severity_breakdown": {
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low,
            },
            "coherence_score": self.coherence_score,
            "evidence_coverage": self.evidence_coverage,
            "hard_contradictions": self.hard_contradictions,
            "verified_claims": verified,
            "deployment_blockers": len(self.get_deployment_blockers()),
            "has_gbp_data": self.gbp_analysis is not None,
            "performance_score": self.performance_analysis.performance_score,
            "schema_coverage": self.schema_analysis.coverage_score,
        }

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Severity: lambda v: v.value,
            ConfidenceLevel: lambda v: v.value,
        }
        populate_by_name = True
