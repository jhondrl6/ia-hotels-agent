"""
Financial Evidence — Epistemic Metadata Model.

Proporciona trazabilidad campo-por-campo de donde viene cada numero
y con que confianza se puede mostrar.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional, Any


class EpistemicStatus(Enum):
    """Estado epistemico de un campo financiero."""
    MEASURED = "measured"           # Dato real del hotel (onboarding)
    OBSERVED = "observed"           # Extraido de la web (scraping)
    REGIONAL_BENCHMARK = "regional_benchmark"  # Benchmark regional
    DEFAULTED = "defaulted"         # Valor por defecto/fallback
    SIMULATED = "simulated"         # Simulacion/hipotesis
    CONFLICT = "conflict"           # Conflicto entre fuentes


class PrecisionTier(Enum):
    """Tier de precision financiera basado en fuentes de datos."""
    A = "A"  # Todos los campos measured → cifra exacta
    B = "B"  # Mayoria measured/observed, al menos 1 regional_benchmark
    C = "C"  # Al menos 1 defaulted o simulated


# Mapeo de source strings legacy → EpistemicStatus
SOURCE_TO_EPISTEMIC: Dict[str, EpistemicStatus] = {
    "user_provided": EpistemicStatus.MEASURED,
    "web_scraping": EpistemicStatus.OBSERVED,
    "regional_v410": EpistemicStatus.REGIONAL_BENCHMARK,
    "legacy_hardcode": EpistemicStatus.DEFAULTED,
    "unknown": EpistemicStatus.DEFAULTED,
}


@dataclass
class FieldEvidence:
    """Evidencia epistemica de un campo individual."""
    value: float
    source: str  # ej: "benchmarking_2026:eje_cafetero:boutique_10_25"
    epistemic_status: EpistemicStatus
    precision: str = "range"  # "exact" o "range"
    can_show_exact: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "source": self.source,
            "epistemic_status": self.epistemic_status.value,
            "precision": self.precision,
            "can_show_exact": self.can_show_exact,
        }


@dataclass
class FinancialEvidence:
    """Evidencia epistemica completa para datos financieros de un hotel."""
    adr_cop: FieldEvidence
    occupancy_rate: FieldEvidence
    direct_channel_percentage: FieldEvidence
    ota_commission_rate: FieldEvidence = field(default_factory=lambda: FieldEvidence(
        value=0.15,
        source="industry_standard",
        epistemic_status=EpistemicStatus.DEFAULTED,
        precision="range",
        can_show_exact=False,
    ))

    @property
    def precision_tier(self) -> PrecisionTier:
        """Determina tier por peor fuente."""
        statuses = {
            self.adr_cop.epistemic_status,
            self.occupancy_rate.epistemic_status,
            self.direct_channel_percentage.epistemic_status,
        }
        if statuses == {EpistemicStatus.MEASURED}:
            return PrecisionTier.A
        if EpistemicStatus.DEFAULTED in statuses or EpistemicStatus.SIMULATED in statuses:
            return PrecisionTier.C
        return PrecisionTier.B

    @property
    def can_show_exact_money(self) -> bool:
        return all(
            f.epistemic_status in {EpistemicStatus.MEASURED, EpistemicStatus.OBSERVED}
            for f in [self.adr_cop, self.occupancy_rate, self.direct_channel_percentage]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializacion para financial_scenarios.json."""
        return {
            "adr_cop": self.adr_cop.to_dict(),
            "occupancy_rate": self.occupancy_rate.to_dict(),
            "direct_channel_percentage": self.direct_channel_percentage.to_dict(),
            "ota_commission_rate": self.ota_commission_rate.to_dict(),
            "financial_precision_tier": self.precision_tier.value,
            "can_show_exact_money": self.can_show_exact_money,
        }


def build_financial_evidence(
    adr_cop: float,
    adr_source: str,
    occupancy_rate: float,
    occupancy_source: str,
    direct_channel_pct: float,
    channel_source: str,
    ota_commission_rate: float = 0.15,
    ota_source: str = "industry_standard",
) -> FinancialEvidence:
    """Factory: construye FinancialEvidence desde fuentes dispersas.

    Args:
        adr_cop: Valor del ADR en COP.
        adr_source: Fuente del ADR ("user_provided", "web_scraping", "regional_v410", "legacy_hardcode").
        occupancy_rate: Tasa de ocupacion (0.0-1.0).
        occupancy_source: Fuente de occupancy ("user_provided", "web_scraping", "regional_v410", "legacy_hardcode").
        direct_channel_pct: Porcentaje de canal directo (0.0-1.0).
        channel_source: Fuente del canal directo.
        ota_commission_rate: Tasa de comision OTA (default 0.15).
        ota_source: Fuente de comision OTA (default "industry_standard").

    Returns:
        FinancialEvidence con status epistemico resuelto.
    """
    def _resolve(source: str, value: float) -> tuple[EpistemicStatus, bool]:
        """Resuelve status y can_show_exact desde source string."""
        status = SOURCE_TO_EPISTEMIC.get(source, EpistemicStatus.DEFAULTED)
        can_show = status in {EpistemicStatus.MEASURED, EpistemicStatus.OBSERVED}
        return status, can_show

    adr_status, adr_can_show = _resolve(adr_source, adr_cop)
    occ_status, occ_can_show = _resolve(occupancy_source, occupancy_rate)
    ch_status, ch_can_show = _resolve(channel_source, direct_channel_pct)
    ota_status, ota_can_show = _resolve(ota_source, ota_commission_rate)

    return FinancialEvidence(
        adr_cop=FieldEvidence(
            value=adr_cop,
            source=adr_source,
            epistemic_status=adr_status,
            precision="exact" if adr_can_show else "range",
            can_show_exact=adr_can_show,
        ),
        occupancy_rate=FieldEvidence(
            value=occupancy_rate,
            source=occupancy_source,
            epistemic_status=occ_status,
            precision="exact" if occ_can_show else "range",
            can_show_exact=occ_can_show,
        ),
        direct_channel_percentage=FieldEvidence(
            value=direct_channel_pct,
            source=channel_source,
            epistemic_status=ch_status,
            precision="exact" if ch_can_show else "range",
            can_show_exact=ch_can_show,
        ),
        ota_commission_rate=FieldEvidence(
            value=ota_commission_rate,
            source=ota_source,
            epistemic_status=ota_status,
            precision="range",
            can_show_exact=ota_can_show,
        ),
    )
