"""
Data structures for commercial document generation.

These dataclasses define the input structures required for generating
diagnostic and proposal documents in the v4.0 system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from datetime import datetime

# Use the unified ConfidenceLevel from confidence_taxonomy
from modules.data_validation.confidence_taxonomy import ConfidenceLevel

if TYPE_CHECKING:
    pass


def adapt_validation_confidence(dv_confidence) -> "ConfidenceLevel":
    """
    Adapta de data_validation.ConfidenceLevel a commercial_documents.ConfidenceLevel.
    
    data_validation usa lowercase: "verified", "estimated", "conflict", "unknown"
    commercial_documents usa UPPERCASE: "VERIFIED", "ESTIMATED", "CONFLICT", "UNKNOWN"
    """
    # Handle both enum and string inputs
    if hasattr(dv_confidence, 'value'):
        value = dv_confidence.value
    else:
        value = str(dv_confidence).lower()
    
    mapping = {
        "verified": ConfidenceLevel.VERIFIED,
        "estimated": ConfidenceLevel.ESTIMATED,
        "conflict": ConfidenceLevel.CONFLICT,
        "unknown": ConfidenceLevel.UNKNOWN,
    }
    return mapping.get(value, ConfidenceLevel.UNKNOWN)


@dataclass
class ValidatedField:
    """A single validated field with confidence information."""
    field_name: str
    value: Any
    confidence: ConfidenceLevel
    sources: List[str] = field(default_factory=list)
    match_percentage: float = 0.0
    can_use_in_assets: bool = False


@dataclass
class Conflict:
    """Represents a conflict between data sources."""
    field_name: str
    source_a: str
    value_a: Any
    source_b: str
    value_b: Any
    description: str = ""


@dataclass
class ValidationSummary:
    """Summary of all validation results."""
    fields: List[ValidatedField]
    overall_confidence: ConfidenceLevel
    conflicts: List[Conflict] = field(default_factory=list)
    
    def get_field(self, name: str) -> Optional[ValidatedField]:
        """Get a specific field by name."""
        for field in self.fields:
            if field.field_name == name:
                return field
        return None
    
    def has_conflicts(self) -> bool:
        """Check if there are any conflicts."""
        return len(self.conflicts) > 0


@dataclass
class Scenario:
    """Financial scenario with loss projections."""
    monthly_loss_min: int
    monthly_loss_max: int
    probability: float
    description: str
    assumptions: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    monthly_opportunity_cop: int = 0  # Valor absoluto cuando loss <= 0 (ganancia/equilibrio)
    monthly_loss_central: Optional[int] = None  # NUEVO — valor central de presentación
    
    def format_loss_cop(self) -> str:
        """Format loss amount with semantic handling for negative values."""
        amount = self.monthly_loss_central if self.monthly_loss_central is not None else self.monthly_loss_max
        if amount <= 0:
            return f"Equilibrio (ahorro: {format_cop(abs(amount))})"
        return format_cop(amount)
    
    def is_equilibrium_or_gain(self) -> bool:
        """Check if this scenario represents equilibrium or gain."""
        amount = self.monthly_loss_central if self.monthly_loss_central is not None else self.monthly_loss_max
        return amount <= 0


@dataclass
class FinancialScenarios:
    """Container for all three financial scenarios."""
    conservative: Scenario  # 70% probability
    realistic: Scenario     # 20% probability - MAIN
    optimistic: Scenario    # 10% probability
    
    def get_main_scenario(self) -> Scenario:
        """Get the main (realistic) scenario for display."""
        return self.realistic
    
    def format_range_cop(self) -> str:
        """Format the loss range for display in COP."""
        min_val = f"{self.conservative.monthly_loss_min:,.0f}".replace(",", ".")
        max_val = f"{self.optimistic.monthly_loss_max:,.0f}".replace(",", ".")
        return f"${min_val} - ${max_val} COP/mes"


class EvidenceTier(Enum):
    """Clasificación de calidad de evidencia financiera."""
    A = "A"  # GA4 + GSC conectados — datos verificables
    B = "B"  # Benchmarks regionales + scraping — estimado con base
    C = "C"  # Solo scraping básico — estimado con baja confianza
    
    @property
    def disclaimer(self) -> str:
        if self == EvidenceTier.A:
            return "Basado en datos de Google Analytics y Search Console verificados."
        elif self == EvidenceTier.B:
            return "Estimación basada en benchmarks regionales y datos de su web. Para mayor precisión, conecte Google Analytics 4."
        else:
            return "Estimación basada en datos limitados de su web. Conecte Google Analytics 4 para un diagnóstico más preciso."


@dataclass
class FinancialBreakdown:
    """Desglose financiero por capas: verificable vs estimado."""
    
    # CAPA 1: Datos verificables (hechos del hotel + comisión OTA)
    monthly_ota_commission_cop: float      # Ej: $5,400,000
    ota_commission_basis: str              # Ej: "120 noches OTA × $300K ADR × 15%"
    ota_commission_source: str             # Ej: "onboarding" | "scraping" | "benchmark"
    
    # CAPA 2A: Ahorro por migración OTA→directo (hipótesis)
    shift_savings_cop: float               # Ej: $540,000
    shift_percentage: float                # Ej: 0.10
    shift_source: str                      # Ej: "benchmark: hoteles con presencia digital mejorada"
    
    # CAPA 2B: Ingresos nuevos por visibilidad IA (hipótesis)
    ia_revenue_cop: float                  # Ej: $2,250,000
    ia_boost_percentage: float             # Ej: 0.05
    ia_source: str                         # Ej: "estimado: sin datos GA4"
    
    # META
    evidence_tier: str                     # "A" | "B" | "C"
    disclaimer: str                        # Texto honesto sobre confianza del dato
    hotel_data_sources: Dict[str, str] = field(default_factory=dict)
    # Dict de fuente por dato: {"adr": "onboarding", "rooms": "onboarding", "occupancy": "benchmark"}


@dataclass
class SchemaValidation:
    """Schema validation results."""
    hotel_schema_detected: bool
    hotel_schema_valid: bool
    hotel_confidence: str
    faq_schema_detected: bool
    faq_schema_valid: bool
    faq_confidence: str
    org_schema_detected: bool
    total_schemas: int
    errors: List[Dict] = field(default_factory=list)
    warnings: List[Dict] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GBPData:
    """Google Business Profile data."""
    place_found: bool
    place_id: Optional[str]
    name: str
    rating: float
    reviews: int
    photos: int
    phone: Optional[str]
    website: Optional[str]
    address: str
    geo_score: int
    geo_score_breakdown: Dict[str, float]
    confidence: str


@dataclass
class PerformanceData:
    """Performance metrics from PageSpeed."""
    has_field_data: bool
    mobile_score: Optional[int]
    desktop_score: Optional[int]
    lcp: Optional[float]
    fid: Optional[int]
    cls: Optional[float]
    status: str
    message: str


@dataclass
class CrossValidationResult:
    """Cross-validation results between sources."""
    whatsapp_status: str
    phone_web: Optional[str]
    phone_gbp: Optional[str]
    adr_status: str
    adr_web: Optional[float]
    adr_benchmark: Optional[float]
    conflicts: List[Dict] = field(default_factory=list)
    validated_fields: Dict[str, Any] = field(default_factory=dict)
    whatsapp_html_detected: bool = False  # True si scraper detecto boton WhatsApp en HTML


@dataclass
class V4AuditResult:
    """Complete v4.0 audit result."""
    url: str
    hotel_name: str
    timestamp: str
    schema: SchemaValidation
    gbp: GBPData
    performance: PerformanceData
    validation: CrossValidationResult
    overall_confidence: str
    critical_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Optional[Any] = None


@dataclass
class AssetSpec:
    """Specification for an asset to be generated."""
    asset_type: str
    problem_solved: str = ""
    description: str = ""
    confidence_level: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    priority: int = 5  # 1 = highest
    has_automatic_solution: bool = True
    # New fields for Phase 2
    pain_ids: List[str] = field(default_factory=list)  # Problems it solves
    confidence_required: float = 0.7
    can_generate: bool = False
    reason: str = ""
    requires_manual_action: bool = False  # True if asset is MANUAL_ONLY


@dataclass
class DiagnosticDocument:
    """Represents a diagnostic document generated."""
    path: str
    problems: List[Any]  # List[Pain] - forward reference
    financial_impact: Scenario
    generated_at: str


@dataclass
class ProposalDocument:
    """Represents a proposal document generated."""
    path: str
    price_monthly: int
    assets_proposed: List[AssetSpec]
    roi_projected: float
    generated_at: str


@dataclass
class DiagnosticSummary:
    """Summary of diagnostic for proposal generation.
    
    Atributos KB (GAP-IAO-01-02):
        score_tecnico: Score 0-100 del CHECKLIST_IAO (calcular_cumplimiento)
        score_ia: None=sin datos, -1=error, >=0=score real de IATester
        paquete: "basico" (<40), "avanzado" (40-69), "premium" (>=70)
        faltantes: Lista de elementos KB que fallan
        pain_ids: Lista de pain_ids desde brechas[] (conecta con PainSolutionMapper)
        faltantes_monetizables: Elementos KB que fallan y tienen asset IMPLEMENTED
        faltantes_no_monetizables: Elementos KB que fallan y tienen asset MISSING/None
    """
    hotel_name: str
    critical_problems_count: int
    quick_wins_count: int
    overall_confidence: ConfidenceLevel
    top_problems: List[str] = field(default_factory=list)
    validated_data_summary: Dict[str, Any] = field(default_factory=dict)
    coherence_score: Optional[float] = None
    # === CAMPOS KB (GAP-IAO-01-02) ===
    score_tecnico: Optional[int] = None   # 0-100, None si sin datos
    score_ia: Optional[int] = None        # None=sin intentarlo, -1=error, >=0=score
    paquete: Optional[str] = None          # "basico" | "avanzado" | "premium" | None
    faltantes: Optional[List[str]] = None  # Elementos KB que fallan (e.g. ["ssl", "open_graph"])
    pain_ids: Optional[List[str]] = None  # Pain IDs de brechas[] para PainSolutionMapper
    faltantes_monetizables: List[str] = field(default_factory=list)  # Con asset IMPLEMENTED
    faltantes_no_monetizables: List[str] = field(default_factory=list)  # Con asset MISSING/None
    data_source: Optional[str] = None     # "IATester+BingProxy" | "KB" | "N/A" | None
    brechas_reales: Optional[List[Dict[str, Any]]] = None  # FASE-G: desde _identify_brechas con impacto real

    # === NUEVOS CAMPOS 4 PILARES (FASE-A) ===
    score_seo: Optional[int] = None       # 0-100
    score_geo: Optional[int] = None       # 0-100
    score_aeo: Optional[int] = None       # 0-100
    score_iao: Optional[int] = None       # 0-100
    score_global: Optional[int] = None    # Promedio ponderado 4 pilares
    elementos_seo: Optional[Dict[str, bool]] = None
    elementos_geo: Optional[Dict[str, bool]] = None
    elementos_aeo: Optional[Dict[str, bool]] = None
    elementos_iao: Optional[Dict[str, bool]] = None
    # === CAMPOS IAO ADICIONALES (FASE-C) ===
    iao_status: Optional[str] = None           # "Excelente" | "Bueno" | "Regular" | "Bajo"
    iao_regional_avg: Optional[int] = None     # Benchmark regional IAO
    llm_report_summary: Optional[Dict] = None  # Resumen del LLM report (source, mention_score, etc.)
    # === CAMPOS VOICE READINESS (TAREA-2) ===
    voice_readiness_score: Optional[int] = None  # 0-100 score from VoiceReadinessProxy
    voice_readiness_level: Optional[str] = None   # critical | basic | good | excellent


def confidence_to_icon(confidence) -> str:
    """Convert confidence level to display icon."""
    # Handle string confidence levels
    if isinstance(confidence, str):
        confidence_str = confidence.upper()
    else:
        # Handle enum (could be from different module)
        confidence_str = str(confidence).split('.')[-1].upper()
    
    icons = {
        "VERIFIED": "🟢",
        "ESTIMATED": "🟡",
        "CONFLICT": "🔴",
        "UNKNOWN": "⚪",
    }
    return icons.get(confidence_str, "⚪")


def confidence_to_label(confidence) -> str:
    """Convert confidence level to display label."""
    # Handle string confidence levels
    if isinstance(confidence, str):
        confidence_str = confidence.upper()
    else:
        # Handle enum (could be from different module)
        confidence_str = str(confidence).split('.')[-1].upper()
    
    labels = {
        "VERIFIED": "VERIFIED",
        "ESTIMATED": "ESTIMATED",
        "CONFLICT": "CONFLICT",
        "UNKNOWN": "UNKNOWN",
    }
    return labels.get(confidence_str, "UNKNOWN")


def format_cop(amount: int) -> str:
    """Format amount in Colombian Pesos."""
    formatted = f"{amount:,.0f}".replace(",", ".")
    return f"${formatted} COP"






def calculate_quick_wins(audit_result: V4AuditResult, validation_summary: Optional[ValidationSummary] = None) -> int:
    """Calcula quick wins dinámicamente basado en audit_result.
    
    Un quick win es un problema fácilmente solucionable que tiene alto impacto.
    Basado en: schema detection, WhatsApp visibility, FAQ schema.
    """
    quick_wins = 0
    
    # Guard against None audit_result
    if not audit_result:
        return quick_wins
    
    # Guard against None schema
    if not audit_result.schema:
        return quick_wins
    
    # Guard against None validation
    if not audit_result.validation:
        return quick_wins
    
    # Guard against None performance
    if not audit_result.performance:
        return quick_wins
    
    # Guard against None gbp
    if not audit_result.gbp:
        return quick_wins
    
    if not audit_result.schema.hotel_schema_detected:
        quick_wins += 1
    if not audit_result.validation.phone_web:
        quick_wins += 1
    if not audit_result.schema.faq_schema_detected:
        quick_wins += 1
    if audit_result.performance.mobile_score is not None and audit_result.performance.mobile_score < 70:
        quick_wins += 1
    if audit_result.gbp.photos < 20:
        quick_wins += 1
    
    return quick_wins


def extract_top_problems(audit_result: V4AuditResult, limit: int = 5) -> List[str]:
    """Extrae top problems desde audit_result de forma consistente.
    
    Prioriza:
    1. Critical issues del audit
    2. Conflictos de validación
    3. Problemas de schema críticos
    4. Recomendaciones restantes
    
    Args:
        audit_result: Resultado completo del audit
        limit: Máximo número de problemas a retornar
        
    Returns:
        Lista de problemas como strings
    """
    problems = []
    
    # Guard against None audit_result
    if audit_result is None:
        return problems
    
    # 1. Add critical issues from audit
    if audit_result.critical_issues:
        for issue in audit_result.critical_issues[:limit]:
            problems.append(issue)
    
    # 2. Add validation conflicts if any
    remaining = limit - len(problems)
    if remaining > 0 and audit_result.validation and audit_result.validation.conflicts:
        for conflict in audit_result.validation.conflicts[:remaining]:
            field_name = conflict.get('field_name', 'Dato')
            problems.append(f"Conflicto de {field_name}: discrepancia entre fuentes")
    
    # 3. Add schema issues
    remaining = limit - len(problems)
    if remaining > 0 and audit_result.schema and not audit_result.schema.hotel_schema_detected:
        problems.append("Sin Schema de Hotel (invisible para IA)")
        remaining -= 1
    
    if remaining > 0 and audit_result.validation and audit_result.validation.whatsapp_status and audit_result.validation.whatsapp_status.lower() == ConfidenceLevel.CONFLICT.value:
        problems.append("WhatsApp inconsistente entre Web y Google Business Profile")
        remaining -= 1
    
    if remaining > 0 and audit_result.schema and not audit_result.schema.faq_schema_detected:
        problems.append("Sin Schema FAQ (pierde rich snippets)")
        remaining -= 1
    
    # 4. Fill with recommendations if needed
    remaining = limit - len(problems)
    if remaining > 0 and audit_result.recommendations:
        for rec in audit_result.recommendations[:remaining]:
            problems.append(rec)
    
    return problems[:limit]
