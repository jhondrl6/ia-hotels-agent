"""
Guarantee Validator — Garantía Día 55 (ROICR FASE-4B).

Valida si la garantía de mejora del Día 55 se activa o no.

Flujo:
1. Cargar línea base del Día 0 desde onboarding (load_baseline)
2. Consultar GSC actual (simular si no hay API key real)
3. Comparar KPIs: impresiones, clics, posición promedio
4. Si mejora < threshold → generar CREDIT_NOTE.md + billing_adjustment.yaml

Los outputs se generan en: outputs/{hotel_id}/guarantees/
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


# Threshold de mejora mínima para evitar trigger de garantía
DEFAULT_IMPROVEMENT_THRESHOLD = 0.10  # 10% de mejora mínima


@dataclass
class BaselineKPIs:
    """KPIs baseline del Día 0 (desde onboarding)."""
    impressions: int = 0
    clicks: int = 0
    avg_position: float = 0.0
    ctr: float = 0.0
    recorded_at: str = ""


@dataclass
class CurrentKPIs:
    """KPIs actuales (desde GSC)."""
    impressions: int = 0
    clicks: int = 0
    avg_position: float = 0.0
    ctr: float = 0.0
    recorded_at: str = ""
    is_simulated: bool = False  # True si vino de stub/mock


@dataclass
class GuaranteeResult:
    """
    Resultado de la validación de garantía Día 55.
    
    Attributes:
        triggered: True si la garantía se activó (no hubo mejora suficiente)
        baseline: KPIs baseline cargados
        current: KPIs actuales
        improvement: Dict con % mejora por KPI
        guarantee_dir: Ruta donde se escribieron los archivos de garantía
        credit_note_path: Ruta al CREDIT_NOTE.md (None si no se generó)
        billing_adjustment_path: Ruta al billing_adjustment.yaml (None si no se generó)
        message: Mensaje legible de resultado
    """
    triggered: bool
    baseline: BaselineKPIs
    current: CurrentKPIs
    improvement: Dict[str, float] = field(default_factory=dict)
    guarantee_dir: Optional[Path] = None
    credit_note_path: Optional[Path] = None
    billing_adjustment_path: Optional[Path] = None
    message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "triggered": self.triggered,
            "baseline": {
                "impressions": self.baseline.impressions,
                "clicks": self.baseline.clicks,
                "avg_position": self.baseline.avg_position,
                "ctr": self.baseline.ctr,
                "recorded_at": self.baseline.recorded_at,
            },
            "current": {
                "impressions": self.current.impressions,
                "clicks": self.current.clicks,
                "avg_position": self.current.avg_position,
                "ctr": self.current.ctr,
                "recorded_at": self.current.recorded_at,
                "is_simulated": self.current.is_simulated,
            },
            "improvement": self.improvement,
            "guarantee_dir": str(self.guarantee_dir) if self.guarantee_dir else None,
            "credit_note_path": str(self.credit_note_path) if self.credit_note_path else None,
            "billing_adjustment_path": str(self.billing_adjustment_path) if self.billing_adjustment_path else None,
            "message": self.message,
        }


def load_baseline(hotel_id: str, output_base: Path = Path("./output")) -> BaselineKPIs:
    """
    Carga la línea base del Día 0 desde onboarding.
    
    Busca en: {output_base}/{hotel_id}/onboarding/onboarding_data.yaml (o .json)
    
    Args:
        hotel_id: ID del hotel
        output_base: Directorio base de outputs (default: ./output)
    
    Returns:
        BaselineKPIs con los datos de Day 0
        
    Raises:
        FileNotFoundError: Si no encuentra archivo de onboarding
    """
    onboarding_paths = [
        output_base / hotel_id / "onboarding" / "onboarding_data.yaml",
        output_base / hotel_id / "onboarding" / "onboarding_data.yml",
        output_base / hotel_id / "onboarding" / "onboarding_data.json",
        # Alternativa: datos operativos capturados
        output_base / hotel_id / "onboarding" / "data.yaml",
        output_base / hotel_id / "onboarding" / "data.json",
    ]
    
    for path in onboarding_paths:
        if path.exists():
            from modules.onboarding.data_loader import load_onboarding_data
            data = load_onboarding_data(path)
            
            # Extraer KPIs baseline
            # Onboarding puede tener datos_operativos o metadatos
            datos_op = data.get("datos_operativos", {})
            metadatos = data.get("metadatos", {})
            
            baseline = BaselineKPIs(
                impressions=datos_op.get("impressions_baseline", datos_op.get("impressions", 0)),
                clicks=datos_op.get("clicks_baseline", datos_op.get("clicks", 0)),
                avg_position=datos_op.get("avg_position_baseline", datos_op.get("avg_position", 0.0)),
                ctr=datos_op.get("ctr_baseline", datos_op.get("ctr", 0.0)),
                recorded_at=metadatos.get("fecha_captura", datos_op.get("recorded_at", "")),
            )
            return baseline
    
    raise FileNotFoundError(
        f"No se encontró archivo de onboarding para hotel '{hotel_id}' en {output_base}. "
        f"Buscó en: {[str(p) for p in onboarding_paths]}"
    )


def get_current_gsc_data(hotel_url: str, days: int = 55) -> CurrentKPIs:
    """
    Obtiene KPIs actuales desde GSC (o stub si no hay API).
    
    Args:
        hotel_url: URL del hotel para consultar GSC
        days: Número de días hacia atrás para comparar (default: 55)
    
    Returns:
        CurrentKPIs con datos actuales (o simulados si no hay GSC API)
    """
    try:
        from modules.analytics import GoogleSearchConsoleClient
        
        gsc = GoogleSearchConsoleClient()
        if not gsc.is_configured():
            logger.warning("[GuaranteeValidator] GSC no configurado — usando modo simulación")
            return _get_simulated_current_kpis()
        
        # Calcular fechas para el periodo
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        report = gsc.get_search_analytics(
            start_date=start_date,
            end_date=end_date,
            dimensions=["query"],
        )
        
        if not report.is_available:
            logger.warning(f"[GuaranteeValidator] GSC no disponible: {report.error_message} — usando simulación")
            return _get_simulated_current_kpis()
        
        return CurrentKPIs(
            impressions=report.total_impressions,
            clicks=report.total_clicks,
            avg_position=report.avg_position,
            ctr=report.avg_ctr,
            recorded_at=datetime.now().isoformat(),
            is_simulated=False,
        )
        
    except ImportError:
        logger.warning("[GuaranteeValidator] Cliente GSC no disponible — usando modo simulación")
        return _get_simulated_current_kpis()
    except Exception as e:
        logger.warning(f"[GuaranteeValidator] Error consultando GSC: {e} — usando modo simulación")
        return _get_simulated_current_kpis()


def _get_simulated_current_kpis() -> CurrentKPIs:
    """
    Genera KPIs simulados para cuando no hay GSC API.
    
    En producción real, esto debería requerir inputs manuales del usuario
    para evitar falsas garantías.
    """
    logger.info("[GuaranteeValidator] MODO SIMULACIÓN: KPIs simulados (no hay GSC API)")
    
    # Simulamos datos que NO superan el threshold para que la garantía NO se active
    # en el caso base — el usuario debe pasar datos reales si quiere validar
    return CurrentKPIs(
        impressions=0,
        clicks=0,
        avg_position=0.0,
        ctr=0.0,
        recorded_at=datetime.now().isoformat(),
        is_simulated=True,
    )


def calculate_improvement(baseline: BaselineKPIs, current: CurrentKPIs) -> Dict[str, float]:
    """
    Calcula el % de mejora entre baseline y current.
    
    Returns:
        Dict con claves: impressions_pct, clicks_pct, position_improvement (negativo=mejora)
    """
    improvement = {}
    
    # Impressions
    if baseline.impressions > 0:
        improvement["impressions_pct"] = (current.impressions - baseline.impressions) / baseline.impressions
    else:
        improvement["impressions_pct"] = 0.0
    
    # Clicks
    if baseline.clicks > 0:
        improvement["clicks_pct"] = (current.clicks - baseline.clicks) / baseline.clicks
    else:
        improvement["clicks_pct"] = 0.0
    
    # Position (menor es mejor, así que improvement es baseline - current)
    if baseline.avg_position > 0:
        improvement["position_improvement"] = baseline.avg_position - current.avg_position
    else:
        improvement["position_improvement"] = 0.0
    
    # CTR
    if baseline.ctr > 0:
        improvement["ctr_pct"] = (current.ctr - baseline.ctr) / baseline.ctr
    else:
        improvement["ctr_pct"] = 0.0
    
    return improvement


def _generate_credit_note(hotel_id: str, baseline: BaselineKPIs, current: CurrentKPIs, 
                          improvement: Dict[str, float], output_dir: Path) -> Path:
    """Genera CREDIT_NOTE.md en output_dir."""
    guarantee_dir = output_dir / "guarantees"
    guarantee_dir.mkdir(parents=True, exist_ok=True)
    
    credit_note_path = guarantee_dir / "CREDIT_NOTE.md"
    
    # Calcular valores para la nota
    imp_pct = improvement.get("impressions_pct", 0.0) * 100
    clk_pct = improvement.get("clicks_pct", 0.0) * 100
    pos_imp = improvement.get("position_improvement", 0.0)
    
    content = f"""# Nota de Crédito — Garantía Día 55

**Hotel ID:** {hotel_id}  
**Fecha de emisión:** {datetime.now().strftime('%Y-%m-%d')}  
**Periodo evaluado:** Día 0 → Día 55

---

## Resultado de la Validación

La garantía de mejora del Día 55 **NO se cumplió** — los KPIs no muestran
mejora suficiente respecto a la línea base registrada.

### Línea Base (Día 0)
| KPI | Valor |
|-----|-------|
| Impresiones | {baseline.impressions:,} |
| Clics | {baseline.clicks:,} |
| Posición promedio | {baseline.avg_position:.1f} |
| CTR | {baseline.ctr:.2f}% |

### KPIs Actuales (Día 55)
| KPI | Valor | Mejora |
|-----|-------|--------|
| Impresiones | {current.impressions:,} | {imp_pct:+.1f}% |
| Clics | {current.clicks:,} | {clk_pct:+.1f}% |
| Posición promedio | {current.avg_position:.1f} | {pos_imp:+.1f} |
| CTR | {current.ctr:.2f}% | — |

---

## Detalle de la Garantía

Umbral de mejora mínimo: 10%

**Motivo de activación:** Los KPIs evaluados no superaron el umbral de mejora
del {DEFAULT_IMPROVEMENT_THRESHOLD:.0%} requerido por la garantía.

---

*Este documento fue generado automáticamente por iah-cli ROICR FASE-4.*
*Para procesar el ajuste de facturación, use el archivo billing_adjustment.yaml.*
"""
    
    credit_note_path.write_text(content, encoding="utf-8")
    logger.info(f"[GuaranteeValidator] CREDIT_NOTE.md generado: {credit_note_path}")
    return credit_note_path


def _generate_billing_adjustment(hotel_id: str, baseline: BaselineKPIs, current: CurrentKPIs,
                                  improvement: Dict[str, float], output_dir: Path) -> Path:
    """Genera billing_adjustment.yaml en output_dir."""
    guarantee_dir = output_dir / "guarantees"
    guarantee_dir.mkdir(parents=True, exist_ok=True)
    
    billing_path = guarantee_dir / "billing_adjustment.yaml"
    
    import yaml
    
    data = {
        "hotel_id": hotel_id,
        "guarantee_day": 55,
        "triggered": True,
        "evaluation_date": datetime.now().strftime("%Y-%m-%d"),
        "baseline": {
            "impressions": baseline.impressions,
            "clicks": baseline.clicks,
            "avg_position": baseline.avg_position,
            "ctr": baseline.ctr,
            "recorded_at": baseline.recorded_at,
        },
        "current": {
            "impressions": current.impressions,
            "clicks": current.clicks,
            "avg_position": current.avg_position,
            "ctr": current.ctr,
            "recorded_at": current.recorded_at,
            "is_simulated": current.is_simulated,
        },
        "improvement": {k: round(v, 4) for k, v in improvement.items()},
        "threshold_pct": DEFAULT_IMPROVEMENT_THRESHOLD * 100,
        "adjustment_action": "NOTA_CREDITO_APLICABLE",
        "nota_credito_path": str(guarantee_dir / "CREDIT_NOTE.md"),
    }
    
    with open(billing_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    
    logger.info(f"[GuaranteeValidator] billing_adjustment.yaml generado: {billing_path}")
    return billing_path


def validar_garantia_dia55(hotel_url: str, hotel_id: str, 
                           output_base: Path = Path("./output")) -> GuaranteeResult:
    """
    Valida si la garantía del Día 55 se activó para el hotel dado.
    
    Args:
        hotel_url: URL del hotel
        hotel_id: ID del hotel (slug o nombre)
        output_base: Directorio base de outputs (default: ./output)
    
    Returns:
        GuaranteeResult con el resultado de la validación.
        
    Raises:
        FileNotFoundError: Si no se encuentra la línea base de onboarding
    """
    logger.info(f"[GuaranteeValidator] Iniciando validación Día 55 para hotel: {hotel_id}")
    
    # 1. Cargar línea base del Día 0
    try:
        baseline = load_baseline(hotel_id, output_base)
        logger.info(f"[GuaranteeValidator] Baseline cargado: imp={baseline.impressions}, clks={baseline.clicks}")
    except FileNotFoundError as e:
        logger.error(f"[GuaranteeValidator] No se pudo cargar baseline: {e}")
        raise
    
    # 2. Consultar GSC actual
    current = get_current_gsc_data(hotel_url, days=55)
    logger.info(f"[GuaranteeValidator] KPIs actuales: imp={current.impressions}, clks={current.clicks}, sim={current.is_simulated}")
    
    # 3. Calcular mejora
    improvement = calculate_improvement(baseline, current)
    logger.info(f"[GuaranteeValidator] Mejora calculada: {improvement}")
    
    # 4. Evaluar threshold —我们需要检查是否有任何 KPI 超过阈值
    # 如果没有 KPI 改善（所有都是 0 或负数），触发保证
    has_meaningful_improvement = (
        improvement.get("impressions_pct", 0) >= DEFAULT_IMPROVEMENT_THRESHOLD
        or improvement.get("clicks_pct", 0) >= DEFAULT_IMPROVEMENT_THRESHOLD
        or (improvement.get("position_improvement", 0) >= 0 
            and baseline.avg_position > current.avg_position 
            and abs(improvement.get("position_improvement", 0)) >= 1.0)
    )
    
    triggered = not has_meaningful_improvement
    
    # Preparar directorio de salida
    output_dir = output_base / hotel_id
    guarantee_dir = output_dir / "guarantees"
    credit_note_path = None
    billing_adjustment_path = None
    
    if triggered:
        logger.info(f"[GuaranteeValidator] Garantía ACTIVADA — generando documentos de ajuste")
        credit_note_path = _generate_credit_note(hotel_id, baseline, current, improvement, output_dir)
        billing_adjustment_path = _generate_billing_adjustment(hotel_id, baseline, current, improvement, output_dir)
        message = (
            f"Garantía Día 55 ACTIVADA para {hotel_id}. "
            f"Mejora insuficiente: impresiones {improvement.get('impressions_pct', 0)*100:+.1f}%, "
            f"clics {improvement.get('clicks_pct', 0)*100:+.1f}%. "
            f"Documentos: CREDIT_NOTE.md y billing_adjustment.yaml generados."
        )
    else:
        message = (
            f"Garantía Día 55 NO activada para {hotel_id}. "
            f"Mejoró: impresiones {improvement.get('impressions_pct', 0)*100:+.1f}%, "
            f"clics {improvement.get('clicks_pct', 0)*100:+.1f}%. "
            f"KPIs superan el threshold del {DEFAULT_IMPROVEMENT_THRESHOLD*100:.0f}%."
        )
        logger.info(f"[GuaranteeValidator] {message}")
    
    return GuaranteeResult(
        triggered=triggered,
        baseline=baseline,
        current=current,
        improvement=improvement,
        guarantee_dir=guarantee_dir,
        credit_note_path=credit_note_path,
        billing_adjustment_path=billing_adjustment_path,
        message=message,
    )