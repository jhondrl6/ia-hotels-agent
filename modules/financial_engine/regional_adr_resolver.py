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
    # NUEVOS campos epistémicos (FIN-2A)
    epistemic_status: str = "regional_benchmark"
    can_show_exact: bool = False
    occupancy_rate: Optional[float] = None


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
        self._regional_benchmarks = None
        self._load_data()
        # FIN-2A: Only auto-load regional_adr_2026.json when using the default
        # plan_maestro_path. When caller provides a custom path (e.g. test fixtures
        # or explicit override), they control the data source — the custom path
        # means "I am providing my own data".
        if plan_maestro_path is None:
            self._load_regional_benchmarks()
        else:
            self._regional_benchmarks = {}

    def _load_regional_benchmarks(self) -> None:
        """Load regional benchmarks from regional_adr_2026.json (FIN-2A).

        Search order:
        1. Same directory as custom plan_maestro_path (for test isolation)
        2. data/benchmarks/ relative to current working directory (repo root)
        3. ../data/benchmarks/ (for tests run from subdirs)
        """
        # Determine the search paths
        custom_dir = None
        if self.plan_maestro_path:
            custom_dir = str(Path(self.plan_maestro_path).parent)

        paths_to_try = []
        if custom_dir:
            paths_to_try.append(Path(custom_dir) / "regional_adr_2026.json")
        paths_to_try.extend([
            Path("data/benchmarks/regional_adr_2026.json"),
            Path("../data/benchmarks/regional_adr_2026.json"),
        ])

        for path in paths_to_try:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self._regional_benchmarks = json.load(f)
                    return
                except (json.JSONDecodeError, IOError) as e:
                    print(f"[ADR Resolver] Warning: Could not load regional_adr_2026.json ({path}): {e}")
        self._regional_benchmarks = {}

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

        # FIN-2A: Try regional_adr_2026.json first
        adr, occupancy, epistemic_status, source = self._resolve_from_regional_benchmarks(region, segment)

        # Fallback to plan_maestro_data if regional benchmarks not available
        if adr is None:
            region_data = self._get_region_data(region)
            adr = self._get_adr_for_segment(region_data, segment)
            occupancy = region_data.get("ocupacion", 0.50)
            epistemic_status = "legacy_hardcode"
            source = "plan_maestro_v2.5"

        confidence = self._determine_confidence(region, user_provided_adr, adr)
        is_default = region not in self._get_known_regions()

        return RegionalADRResult(
            adr_cop=adr,
            region=region if region in self._get_known_regions() else "default",
            segment=segment,
            confidence=confidence,
            source=source,
            is_default=is_default,
            metadata={
                "rooms": rooms,
                "user_provided_adr": user_provided_adr,
                "deviation_pct": self._calculate_deviation(user_provided_adr, adr) if user_provided_adr else None,
            },
            epistemic_status=epistemic_status,
            can_show_exact=False,
            occupancy_rate=occupancy,
        )

    # Legacy region name aliases (plan_maestro_data.json → regional_adr_2026.json)
    REGION_ALIASES = {
        "coffee_axis": "eje_cafetero",
        "medellin": "antioquia",
        # bogota not mapped — no coverage in regional_adr_2026.json, use default
    }

    def _resolve_from_regional_benchmarks(self, region: str, segment: str):
        """Try to resolve ADR from regional_adr_2026.json. Returns (adr, occupancy, epistemic_status, source)."""
        if not self._regional_benchmarks:
            return None, None, None, None

        # Apply legacy region alias if present
        resolved_region = self.REGION_ALIASES.get(region, region)
        regions = self._regional_benchmarks.get("regions", {})
        region_data = regions.get(resolved_region)

        # Fall back to default region
        if region_data is None:
            region_data = regions.get("default", {})
            if not region_data:
                return None, None, None, None
            resolved_region = "default"

        # Map segment to key
        segment_key = "boutique_10_25" if segment == self.SEGMENT_BOUTIQUE else "standard_26_60"

        # Try specific segment
        segment_data = region_data.get(segment_key) or region_data.get("any")
        if segment_data is None:
            return None, None, None, None

        adr = segment_data.get("adr_cop")
        occupancy = segment_data.get("occupancy_rate")
        epistemic_status = "regional_benchmark" if resolved_region != "default" else "defaulted"
        source = "regional_adr_2026"

        return adr, occupancy, epistemic_status, source
    
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
        """Resolve occupancy rate for a region.

        FIN-2A: First tries regional_adr_2026.json, then falls back to plan_maestro_data.
        Returns the calibrated occupancy or 0.50 as default.
        """
        # FIN-2A: Try regional benchmarks first
        if self._regional_benchmarks:
            regions = self._regional_benchmarks.get("regions", {})
            region_data = regions.get(region)
            if region_data is None:
                region_data = regions.get("default", {})
            if region_data:
                # Try both segment keys and "any"
                for key in ["boutique_10_25", "standard_26_60", "any"]:
                    if key in region_data:
                        occ = region_data[key].get("occupancy_rate")
                        if occ is not None:
                            return occ

        # Fallback to plan_maestro_data
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
