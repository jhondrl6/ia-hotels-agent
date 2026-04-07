"""
Financial Factors - Factores financieros centralizados del modelo de pérdidas.

Centraliza todos los valores que antes estaban hardcoded en gap_analyzer.py
y dynamic_impact.py, permitiendo:
- Coherencia entre módulos
- Fácil actualización desde plan_maestro_data.json
- Trazabilidad de valores

Uso:
    from modules.utils.financial_factors import FinancialFactors
    
    factors = FinancialFactors()
    config = factors.get_config('eje_cafetero')
    perdida = (1 - config.factor_captura_aila) * (config.comision_ota_base + config.penalizacion_invisibilidad_ia)
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from modules.utils.benchmarks import BenchmarkLoader


@dataclass
class FinancialFactorsConfig:
    """Configuración de factores financieros para una región."""
    factor_captura_aila: float
    comision_ota_min: float
    comision_ota_base: float
    comision_ota_max: float
    penalizacion_invisibilidad_ia: float
    exclusion_rating_bajo: float
    factor_perdida_base: float
    factor_perdida_min: float
    factor_perdida_max: float
    revpar_cop: int


class FinancialFactors:
    """
    Centraliza todos los factores financieros del modelo.
    
    Los factores se obtienen de plan_maestro_data.json con fallbacks
    a valores por defecto documentados.
    
    SUPERPOSITION_FACTOR: Factor de corrección (0.7) para evitar doble conteo
    de pérdidas superpuestas en marketing attribution. Estándar de industria.
    """
    
    SUPERPOSITION_FACTOR = 0.7
    
    DEFAULTS = {
        'factor_captura_aila': 0.70,  # Renombrar a factor_optimizacion_digital en siguiente versión
        'comision_ota_min': 0.18,     # Actualizado: proxy México/LatAm 2024-2025
        'comision_ota_base': 0.20,    # Actualizado: proxy México/LatAm 2024-2025
        'comision_ota_max': 0.22,     # Actualizado: proxy México/LatAm 2024-2025
        'penalizacion_invisibilidad_ia': 0.05,
        'exclusion_rating_bajo': 0.40,
        'factor_perdida_base': 0.09,
        'factor_perdida_min': 0.077,
        'factor_perdida_max': 0.103,
        'revpar_cop': 197120,
        # Nuevos campos derivados de investigación:
        # Fuente: Skift Research State of Travel 2024 (65% OTA LatAm)
        'reservas_ota_proporcion': 0.65,
        'reservas_directo_proporcion': 0.35,
        # Fuente: Estimado PwC/ITU 2024-2025 (10-20% adopción IA viajeros)
        'uso_ia_proporcion_min': 0.10,
        'uso_ia_proporcion_max': 0.20,
    }
    
    def __init__(self, loader: Optional[BenchmarkLoader] = None):
        self.loader = loader or BenchmarkLoader()
    
    def get_config(self, region: str) -> FinancialFactorsConfig:
        """
        Obtiene configuración de factores para una región.
        
        Args:
            region: Código de región (eje_cafetero, caribe, antioquia, default)
        
        Returns:
            FinancialFactorsConfig con todos los factores
        """
        regional_data = self.loader.get_regional_data(region)
        thresholds = self.loader.get_thresholds()
        
        return FinancialFactorsConfig(
            factor_captura_aila=regional_data.get(
                'factor_captura_aila', 
                self.DEFAULTS['factor_captura_aila']
            ),
            comision_ota_min=thresholds.get(
                'comision_ota_min', 
                self.DEFAULTS['comision_ota_min']
            ),
            comision_ota_base=thresholds.get(
                'comision_ota_base', 
                self.DEFAULTS['comision_ota_base']
            ),
            comision_ota_max=thresholds.get(
                'comision_ota_max', 
                self.DEFAULTS['comision_ota_max']
            ),
            penalizacion_invisibilidad_ia=thresholds.get(
                'penalizacion_invisibilidad_ia', 
                self.DEFAULTS['penalizacion_invisibilidad_ia']
            ),
            exclusion_rating_bajo=thresholds.get(
                'exclusion_rating_bajo', 
                self.DEFAULTS['exclusion_rating_bajo']
            ),
            factor_perdida_base=regional_data.get(
                'factor_perdida_base', 
                self.DEFAULTS['factor_perdida_base']
            ),
            factor_perdida_min=regional_data.get(
                'factor_perdida_min', 
                self.DEFAULTS['factor_perdida_min']
            ),
            factor_perdida_max=regional_data.get(
                'factor_perdida_max', 
                self.DEFAULTS['factor_perdida_max']
            ),
            revpar_cop=regional_data.get(
                'revpar_cop', 
                self.DEFAULTS['revpar_cop']
            ),
        )
    
    def calculate_factor_perdida(self, region: str) -> float:
        """
        Calcula el factor de pérdida base para una región.
        
        Formula: (1 - AILA) × (comisión OTA + penalización IA)
        
        Esto representa el porcentaje de ingresos que se pierden
        por no estar optimizado para reservas directas + IA.
        """
        config = self.get_config(region)
        return (1 - config.factor_captura_aila) * (
            config.comision_ota_base + config.penalizacion_invisibilidad_ia
        )
    
    def get_factor_captura_aila(self, region: str) -> float:
        """Shortcut para obtener factor_captura_aila de una región."""
        return self.get_config(region).factor_captura_aila
    
    def get_source_info(self, region: str) -> Dict[str, Any]:
        """
        Retorna información de fuentes para documentación.
        
        Útil para generar reportes con trazabilidad de datos.
        """
        regional_data = self.loader.get_regional_data(region)
        return {
            'factor_captura_fuente': regional_data.get(
                'factor_captura_fuente', 
                'Indice AILA Colombia (estimado)'
            ),
            'comisiones_fuente': 'Industry benchmark (Booking, Expedia T&Cs)',
            'penalizacion_fuente': 'Observación empírica IAH 2024-2025',
            'revpar_fuente': 'DANE + COTELCO benchmarks 2026',
            'region': region,
        }
    
    def get_all_regions(self) -> list:
        """Retorna lista de regiones disponibles."""
        return list(self.loader._plan_data.get('regiones', {}).keys())
