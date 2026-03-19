"""Dynamic financial impact calculator.

Replaces hardcoded IMPACTOS_FINANCIEROS in gbp_auditor.py with dynamic
calculations based on hotel data or regional benchmarks.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from modules.utils.benchmarks import BenchmarkLoader
from modules.utils.confidence_tracker import ConfidenceTracker, DataSource


IMPACT_TYPES = [
    'PERFIL_NO_RECLAMADO',
    'FOTOS_INSUFICIENTES',
    'RESENAS_CRITICAS',
    'SIN_WHATSAPP',
    'PERFIL_ABANDONADO',
    'SIN_FAQ',
    'RATING_BAJO',
    'SIN_HORARIOS',
    'SIN_WEBSITE',
    'CERO_ACTIVIDAD_RECIENTE',
]


@dataclass
class ImpactResult:
    """Result of impact calculation for one issue type."""
    issue_type: str
    factor: float
    monthly_loss_cop: int
    description: str
    confidence_source: str


@dataclass 
class DynamicImpactReport:
    """Complete financial impact analysis."""
    impacts: List[ImpactResult]
    total_monthly_loss_cop: int
    data_sources: Dict[str, Any]
    base_metrics: Dict[str, Any]


class DynamicImpactCalculator:
    """
    Calculate financial impacts dynamically based on available data.
    
    Priority order:
    1. Hotel provides data (reservas_mes, valor_reserva, canal_directo)
    2. Fall back to plan_maestro_data.json regional benchmarks
    3. Use Benchmarking.md for contextual data (RevPAR, ADR)
    """

    PERDIDA_MENSUAL_BASE = 2_100_000  # COP - Base loss for PERFIL_NO_RECLAMADO scenario

    def __init__(self, benchmark_loader: Optional[BenchmarkLoader] = None):
        self.benchmark_loader = benchmark_loader or BenchmarkLoader()
        self.tracker = ConfidenceTracker()

    def calculate_impacts(
        self,
        region: str,
        detected_issues: List[str],
        hotel_data: Optional[Dict[str, Any]] = None,
    ) -> DynamicImpactReport:
        """
        Calculate monthly loss for each detected issue.
        
        Args:
            region: Region code (e.g., 'eje_cafetero', 'caribe')
            detected_issues: List of issue types present (from IMPACT_TYPES)
            hotel_data: Optional hotel-provided data with:
                - reservas_mes: int
                - valor_reserva: int  
                - canal_directo: float (0-1)
        
        Returns:
            DynamicImpactReport with calculated impacts
        """
        regional_data = self.benchmark_loader.get_regional_data(region)
        
        reservas_mes, reservas_source = self._get_reservas_mensuales(
            hotel_data, regional_data
        )
        valor_reserva, valor_source = self._get_valor_reserva(
            hotel_data, regional_data
        )
        canal_directo, canal_source = self._get_canal_directo(
            hotel_data, regional_data
        )
        
        base_revenue_mes = reservas_mes * valor_reserva
        self.tracker.add_field(
            "reservas_mes", reservas_mes, reservas_source[0], reservas_source[1],
            is_estimated=reservas_source[2]
        )
        self.tracker.add_field(
            "valor_reserva", valor_reserva, valor_source[0], valor_source[1],
            is_estimated=valor_source[2]
        )
        self.tracker.add_field(
            "canal_directo", canal_directo, canal_source[0], canal_source[1],
            is_estimated=canal_source[2]
        )
        self.tracker.add_field(
            "ingreso_mensual_base", base_revenue_mes, DataSource.CALCULATED,
            "reservas_mes * valor_reserva"
        )
        
        revpar_regional = regional_data.get('revpar_cop', 197120)
        self.tracker.add_field(
            "revpar_regional", revpar_regional, DataSource.PLAN_MAESTRO_JSON,
            f"{region} benchmark", is_estimated=True
        )
        
        impacts = []
        total_loss = 0
        
        for issue_type in detected_issues:
            factor = self._get_factor_for_issue(issue_type)
            description = self._get_description_for_issue(issue_type)
            
            monthly_loss = self._calculate_loss(
                factor=factor,
                reservas_mes=reservas_mes,
                valor_reserva=valor_reserva,
                canal_directo=canal_directo,
                revpar=revpar_regional,
            )
            
            impacts.append(ImpactResult(
                issue_type=issue_type,
                factor=factor,
                monthly_loss_cop=monthly_loss,
                description=description,
                confidence_source="calculated" if hotel_data else "benchmark",
            ))
            total_loss += monthly_loss
        
        data_sources = self.tracker.generate_report().to_dict()
        
        return DynamicImpactReport(
            impacts=impacts,
            total_monthly_loss_cop=total_loss,
            data_sources=data_sources,
            base_metrics={
                "reservas_mes": reservas_mes,
                "valor_reserva": valor_reserva,
                "canal_directo": canal_directo,
                "base_revenue_mes": base_revenue_mes,
                "region": region,
            }
        )

    def _get_reservas_mensuales(
        self,
        hotel_data: Optional[Dict[str, Any]],
        regional_data: Dict[str, Any],
    ) -> tuple:
        """Get reservas_mensuales with source tracking."""
        if hotel_data and 'reservas_mes' in hotel_data:
            return (
                hotel_data['reservas_mes'],
                (DataSource.HOTEL_INPUT, "Hotel questionnaire input", False),
            )
        
        benchmark_value = regional_data.get('reservas_mensuales_promedio', 200)
        return (
            benchmark_value,
            (DataSource.PLAN_MAESTRO_JSON, 
             f"{regional_data.get('factor_captura_fuente', 'regional benchmark')}",
             True),
        )

    def _get_valor_reserva(
        self,
        hotel_data: Optional[Dict[str, Any]],
        regional_data: Dict[str, Any],
    ) -> tuple:
        """Get valor_reserva with source tracking."""
        if hotel_data and 'valor_reserva' in hotel_data:
            return (
                hotel_data['valor_reserva'],
                (DataSource.HOTEL_INPUT, "Hotel questionnaire input", False),
            )
        
        benchmark_value = regional_data.get('valor_reserva_promedio', 300000)
        return (
            benchmark_value,
            (DataSource.PLAN_MAESTRO_JSON,
             f"{regional_data.get('factor_captura_fuente', 'regional benchmark')}",
             True),
        )

    def _get_canal_directo(
        self,
        hotel_data: Optional[Dict[str, Any]],
        regional_data: Dict[str, Any],
    ) -> tuple:
        """Get canal_directo percentage with source tracking."""
        if hotel_data and 'canal_directo' in hotel_data:
            return (
                hotel_data['canal_directo'],
                (DataSource.HOTEL_INPUT, "Hotel questionnaire input", False),
            )
        
        benchmark_value = regional_data.get('canal_directo_porcentaje', 0.50)
        return (
            benchmark_value,
            (DataSource.PLAN_MAESTRO_JSON,
             "Default regional average (50%)",
             True),
        )

    def _calculate_loss(
        self,
        factor: float,
        reservas_mes: int,
        valor_reserva: int,
        canal_directo: float,
        revpar: int,
    ) -> int:
        """
        Calculate monthly loss for a specific issue.
        
        For PERFIL_NO_RECLAMADO (factor=1.0), use the base loss value.
        For other issues, use dynamic calculation based on hotel metrics.
        """
        if factor >= 1.0:
            return self.PERDIDA_MENSUAL_BASE
        
        indirect_channel_share = 1 - canal_directo
        base_loss = factor * indirect_channel_share * reservas_mes * valor_reserva
        return int(base_loss)

    def _get_factor_for_issue(self, issue_type: str) -> float:
        """Get impact factor for issue type."""
        factors = {
            'PERFIL_NO_RECLAMADO': 1.0,
            'FOTOS_INSUFICIENTES': 0.35,
            'RESENAS_CRITICAS': 0.40,
            'SIN_WHATSAPP': 0.30,
            'PERFIL_ABANDONADO': 0.25,
            'SIN_FAQ': 0.20,
            'RATING_BAJO': 0.45,
            'SIN_HORARIOS': 0.15,
            'SIN_WEBSITE': 0.25,
            'CERO_ACTIVIDAD_RECIENTE': 0.30,
        }
        return factors.get(issue_type, 0.20)

    def _get_description_for_issue(self, issue_type: str) -> str:
        """Get description for issue type."""
        descriptions = {
            'PERFIL_NO_RECLAMADO': 'Invisible total en búsquedas locales',
            'FOTOS_INSUFICIENTES': 'Google penaliza relevancia local vs competencia',
            'RESENAS_CRITICAS': 'Descalificado del shortlist de Google Maps',
            'SIN_WHATSAPP': '30% de consultas inmediatas nunca llegan',
            'PERFIL_ABANDONADO': 'Google aplica degradación algorítmica',
            'SIN_FAQ': 'No responde al modelo conversacional de Google',
            'RATING_BAJO': 'Excluido automáticamente de recomendaciones',
            'SIN_HORARIOS': 'Señal de negocio informal o cerrado',
            'SIN_WEBSITE': 'Fuerza dependencia 100% de OTAs',
            'CERO_ACTIVIDAD_RECIENTE': 'Google interpreta como negocio inactivo',
        }
        return descriptions.get(issue_type, 'Impacto en visibilidad')


def get_detected_issues(gbp_data: Dict[str, Any], schema_data: Dict[str, Any]) -> List[str]:
    """Detect which issues are present based on GBP/Schema audit data."""
    issues = []
    
    if not gbp_data.get('claimed', False):
        issues.append('PERFIL_NO_RECLAMADO')
    
    photos = gbp_data.get('photos', 0)
    if photos < 5:
        issues.append('FOTOS_INSUFICIENTES')
    
    rating = gbp_data.get('rating', 5)
    if rating < 3.5:
        issues.append('RESENAS_CRITICAS')
    elif rating < 4.0:
        issues.append('RATING_BAJO')
    
    if not gbp_data.get('has_whatsapp', False):
        issues.append('SIN_WHATSAPP')
    
    if not gbp_data.get('has_hours', False):
        issues.append('SIN_HORARIOS')
    
    if not gbp_data.get('website'):
        issues.append('SIN_WEBSITE')
    
    if not gbp_data.get('posts', 0) > 0:
        issues.append('CERO_ACTIVIDAD_RECIENTE')
    
    if not schema_data.get('tiene_hotel_schema', False):
        issues.append('PERFIL_ABANDONADO')
    
    if not schema_data.get('has_faq', False):
        issues.append('SIN_FAQ')
    
    return issues
