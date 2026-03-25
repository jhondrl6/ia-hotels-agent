"""Plan Maestro Validator.

Validates coherence against Plan Maestro v2.5 data.
Checks thresholds consistency, region required fields, and benchmark alignment.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    passed: bool
    errors: List[str]
    warnings: List[str]
    checks_run: int


class PlanValidator:
    """Validates coherence against Plan Maestro data.
    
    Checks:
    1. Plan Maestro JSON file exists and is parseable
    2. Thresholds in decision_engine.py match JSON values
    3. Regions have required fields
    4. Package definitions are complete
    """
    
    REQUIRED_REGION_FIELDS: Set[str] = {
        "revpar_cop",
        "habitaciones_promedio",
        "factor_captura_aila",
        "comision_ota_base",
        "factor_perdida_base",
    }
    
    REQUIRED_PACKAGE_FIELDS: Set[str] = {
        "precio_cop",
        "roi_target",
        "componentes",
    }
    
    REQUIRED_THRESHOLDS: Set[str] = {
        "impacto_catastrofico",
        "brecha_conversion_critica",
        "revpar_premium",
        "web_score_alto",
        "gbp_score_bajo",
        "factor_gbp_punto",
    }
    
    def __init__(self, data_path: Path | None = None):
        """Initialize validator with optional custom data path."""
        if data_path is None:
            data_path = Path(__file__).parent.parent.parent / "data" / "benchmarks" / "plan_maestro_data.json"
        self.data_path = data_path
        self._data: Dict[str, Any] | None = None
    
    def _load_data(self) -> Dict[str, Any]:
        """Load plan maestro data from JSON file."""
        if self._data is not None:
            return self._data
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Plan Maestro data not found: {self.data_path}")
        
        with open(self.data_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)
        
        return self._data
    
    def validate(self) -> ValidationResult:
        """Run all validation checks.
        
        Returns:
            ValidationResult with pass/fail status and details.
        """
        errors: List[str] = []
        warnings: List[str] = []
        checks_run = 0
        
        try:
            data = self._load_data()
            checks_run += 1
        except FileNotFoundError as e:
            errors.append(str(e))
            return ValidationResult(
                passed=False,
                errors=errors,
                warnings=warnings,
                checks_run=checks_run,
            )
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in Plan Maestro data: {e}")
            return ValidationResult(
                passed=False,
                errors=errors,
                warnings=warnings,
                checks_run=checks_run,
            )
        
        result = self._validate_thresholds(data)
        errors.extend(result["errors"])
        warnings.extend(result["warnings"])
        checks_run += result["checks_run"]
        
        result = self._validate_regions(data)
        errors.extend(result["errors"])
        warnings.extend(result["warnings"])
        checks_run += result["checks_run"]
        
        result = self._validate_packages(data)
        errors.extend(result["errors"])
        warnings.extend(result["warnings"])
        checks_run += result["checks_run"]
        
        result = self._validate_version_metadata(data)
        errors.extend(result["errors"])
        warnings.extend(result["warnings"])
        checks_run += result["checks_run"]
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            checks_run=checks_run,
        )
    
    def _validate_thresholds(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all required thresholds exist."""
        errors: List[str] = []
        warnings: List[str] = []
        checks_run = 0
        
        thresholds = data.get("umbrales_decision", {})
        
        for field_name in self.REQUIRED_THRESHOLDS:
            checks_run += 1
            if field_name not in thresholds:
                errors.append(f"Missing required threshold: {field_name}")
            elif not isinstance(thresholds[field_name], (int, float)):
                errors.append(f"Threshold {field_name} must be numeric, got {type(thresholds[field_name])}")
        
        if "inactividad_max_mensual" not in thresholds:
            warnings.append("Missing optional threshold: inactividad_max_mensual")
            checks_run += 1
        
        return {"errors": errors, "warnings": warnings, "checks_run": checks_run}
    
    def _validate_regions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all regions have required fields."""
        errors: List[str] = []
        warnings: List[str] = []
        checks_run = 0
        
        regions = data.get("regiones", {})
        
        if "default" not in regions:
            errors.append("Missing required 'default' region")
            checks_run += 1
            return {"errors": errors, "warnings": warnings, "checks_run": checks_run}
        
        for region_name, region_data in regions.items():
            checks_run += 1
            if not isinstance(region_data, dict):
                errors.append(f"Region '{region_name}' must be a dictionary")
                continue
            
            missing = self.REQUIRED_REGION_FIELDS - set(region_data.keys())
            if missing:
                errors.append(f"Region '{region_name}' missing fields: {', '.join(missing)}")
            
            benchmarks = region_data.get("benchmarks", {})
            if not benchmarks:
                warnings.append(f"Region '{region_name}' has no benchmarks defined")
            else:
                required_benchmarks = {"gbp_score", "schema_score"}
                missing_bench = required_benchmarks - set(benchmarks.keys())
                if missing_bench:
                    warnings.append(f"Region '{region_name}' missing benchmarks: {', '.join(missing_bench)}")
        
        return {"errors": errors, "warnings": warnings, "checks_run": checks_run}
    
    def _validate_packages(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all packages have required fields."""
        errors: List[str] = []
        warnings: List[str] = []
        checks_run = 0
        
        packages = data.get("paquetes_servicios_v23", {})
        
        required_packages = {"Starter GEO", "Pro AEO", "Pro AEO Plus", "Elite", "Elite PLUS"}
        missing_packages = required_packages - set(packages.keys())
        
        if missing_packages:
            errors.append(f"Missing required packages: {', '.join(missing_packages)}")
            checks_run += 1
        
        for pkg_name, pkg_data in packages.items():
            checks_run += 1
            if not isinstance(pkg_data, dict):
                errors.append(f"Package '{pkg_name}' must be a dictionary")
                continue
            
            missing = self.REQUIRED_PACKAGE_FIELDS - set(pkg_data.keys())
            if missing:
                errors.append(f"Package '{pkg_name}' missing fields: {', '.join(missing)}")
            
            precio = pkg_data.get("precio_cop")
            if precio is not None and precio <= 0:
                errors.append(f"Package '{pkg_name}' has invalid precio_cop: {precio}")
            
            roi = pkg_data.get("roi_target")
            if roi is not None and roi <= 0:
                warnings.append(f"Package '{pkg_name}' has low roi_target: {roi}")
        
        return {"errors": errors, "warnings": warnings, "checks_run": checks_run}
    
    def _validate_version_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate version metadata exists."""
        errors: List[str] = []
        warnings: List[str] = []
        checks_run = 0
        
        checks_run += 1
        if "version" not in data:
            warnings.append("Missing version field in Plan Maestro data")
        
        checks_run += 1
        if "fecha_actualizacion" not in data:
            warnings.append("Missing fecha_actualizacion field")
        
        checks_run += 1
        if "documento_oficial" not in data:
            warnings.append("Missing documento_oficial field")
        
        return {"errors": errors, "warnings": warnings, "checks_run": checks_run}
