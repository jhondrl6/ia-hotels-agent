"""Regional ADR Resolver v4.1.0.

Resolves ADR (Average Daily Rate) based on hotel region and size segment.
Uses plan_maestro_data.json as the source of truth for regional benchmarks.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Any
from pathlib import Path
import json


@dataclass
class RegionalADRResult:
    """Result of regional ADR resolution."""
    adr_cop: float
    region: str
    segment: str
    confidence: str  # "VERIFIED", "ESTIMATED", "CONFLICT"
    source: str
    is_default: bool = False
    metadata: Dict[str, Any] = None


class RegionalADRResolver:
    """Resolves ADR from regional benchmarks."""
    
    SEGMENT_BOUTIQUE = "boutique"
    SEGMENT_STANDARD = "standard"
    SEGMENT_LARGE = "large"
    
    BOUTIQUE_MAX = 25
    STANDARD_MAX = 60
    
    def __init__(self, plan_maestro_path: Optional[str] = None):
        self.plan_maestro_path = plan_maestro_path or self._default_plan_path()
        self._data = None
        self._load_data()
    
    def _default_plan_path(self) -> str:
        paths = [
            "data/benchmarks/plan_maestro_data.json",
            "../data/benchmarks/plan_maestro_data.json",
        ]
        for path in paths:
            if Path(path).exists():
                return path
        return "data/benchmarks/plan_maestro_data.json"
    
    def _load_data(self) -> None:
        try:
            with open(self.plan_maestro_path, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self._data = {"regiones": {}}
            print(f"[ADR Resolver] Warning: Could not load plan maestro: {e}")
    
    def resolve(self, region: str, rooms: int, user_provided_adr: Optional[float] = None) -> RegionalADRResult:
        segment = self._determine_segment(rooms)
        region_data = self._get_region_data(region)
        adr = self._get_adr_for_segment(region_data, segment)
        
        confidence = self._determine_confidence(region, user_provided_adr, adr)
        
        return RegionalADRResult(
            adr_cop=adr,
            region=region if region in self._get_known_regions() else "default",
            segment=segment,
            confidence=confidence,
            source="plan_maestro_v2.5",
            is_default=(region not in self._get_known_regions()),
            metadata={
                "rooms": rooms,
                "user_provided_adr": user_provided_adr,
                "deviation_pct": self._calculate_deviation(user_provided_adr, adr) if user_provided_adr else None,
            }
        )
    
    def _determine_segment(self, rooms: int) -> str:
        if rooms <= self.BOUTIQUE_MAX:
            return self.SEGMENT_BOUTIQUE
        elif rooms <= self.STANDARD_MAX:
            return self.SEGMENT_STANDARD
        else:
            return self.SEGMENT_LARGE
    
    def _get_region_data(self, region: str) -> Dict[str, Any]:
        if not self._data:
            return {}
        # Try v25_config.regiones first (actual structure), then legacy regiones
        regiones = self._data.get("v25_config", {}).get("regiones", {})
        if not regiones:
            regiones = self._data.get("regiones", {})
        return regiones.get(region, regiones.get("default", {}))
    
    def _get_adr_for_segment(self, region_data: Dict, segment: str) -> float:
        if not region_data:
            return 300000.0
        
        segments = region_data.get("segments", {})
        
        if segment == self.SEGMENT_BOUTIQUE and "boutique_10_25" in segments:
            return segments["boutique_10_25"].get("adr_cop", region_data.get("adr_cop", region_data.get("precio_promedio", 300000.0)))
        
        if segment == self.SEGMENT_STANDARD and "standard_26_60" in segments:
            return segments["standard_26_60"].get("adr_cop", region_data.get("adr_cop", region_data.get("precio_promedio", 300000.0)))
        
        # Support both adr_cop (new) and precio_promedio (plan_maestro_data.json)
        return region_data.get("adr_cop", region_data.get("precio_promedio", 300000.0))
    
    def _determine_confidence(self, region: str, user_provided_adr: Optional[float], benchmark_adr: float) -> str:
        if region not in self._get_known_regions():
            return "ESTIMATED"
        if user_provided_adr is None:
            return "ESTIMATED"
        
        deviation = self._calculate_deviation(user_provided_adr, benchmark_adr)
        if deviation is None:
            return "ESTIMATED"
        if deviation < 20:
            return "VERIFIED"
        if deviation < 40:
            return "ESTIMATED"
        return "CONFLICT"
    
    def _calculate_deviation(self, user_adr: Optional[float], benchmark_adr: float) -> Optional[float]:
        if user_adr is None or benchmark_adr == 0:
            return None
        return abs(user_adr - benchmark_adr) / benchmark_adr * 100
    
    def _get_known_regions(self) -> set:
        if not self._data:
            return {"default"}
        regiones = self._data.get("v25_config", {}).get("regiones", {})
        if not regiones:
            regiones = self._data.get("regiones", {})
        return set(regiones.keys())
    
    def resolve_occupancy(self, region: str) -> float:
        """Resolve occupancy rate for a region from plan_maestro_data.
        
        Returns the calibrated occupancy or 0.50 as default.
        """
        region_data = self._get_region_data(region)
        return region_data.get("ocupacion", 0.50)
    
    def get_segment_adr_table(self) -> Dict[str, Dict[str, float]]:
        table = {}
        regiones = self._data.get("v25_config", {}).get("regiones", {})
        if not regiones:
            regiones = self._data.get("regiones", {})
        for region_code, region_data in regiones.items():
            # Support both adr_cop (legacy/test) and precio_promedio (plan_maestro_data.json)
            avg = region_data.get("precio_promedio", region_data.get("adr_cop"))
            table[region_code] = {
                "boutique": region_data.get("segments", {}).get("boutique_10_25", {}).get("adr_cop", avg),
                "standard": region_data.get("segments", {}).get("standard_26_60", {}).get("adr_cop", avg),
                "average": avg,
            }
        return table


def resolve_regional_adr(region: str, rooms: int, user_provided_adr: Optional[float] = None, plan_maestro_path: Optional[str] = None) -> RegionalADRResult:
    resolver = RegionalADRResolver(plan_maestro_path)
    return resolver.resolve(region, rooms, user_provided_adr)
