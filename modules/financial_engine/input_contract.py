"""Financial Inputs Contract v4.1.0.

Validates and normalizes financial inputs with strict type checking
and range validation. Guarantees data integrity before calculations.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
import re


class ValidationSeverity(Enum):
    """Severity levels for validation errors."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationError:
    """Single validation error."""
    field: str
    message: str
    severity: ValidationSeverity
    value: Any = None


@dataclass
class ValidationResult:
    """Result of input validation."""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    normalized_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def has_critical_errors(self) -> bool:
        """Check if there are critical errors."""
        return any(
            e.severity == ValidationSeverity.CRITICAL 
            for e in self.errors
        )
    
    def get_errors_by_severity(self, severity: ValidationSeverity) -> List[ValidationError]:
        """Get errors filtered by severity."""
        return [e for e in self.errors if e.severity == severity]


@dataclass
class FinancialInputsContract:
    """Contract for financial input validation.
    
    Strict validation rules:
    - rooms: int > 0 and <= 500
    - adr_cop: float > 0
    - occupancy_rate: float in [0, 1] (auto-normalizes 0-100)
    - direct_channel_percentage: float in [0, 1] (auto-normalizes)
    - ota_commission_rate: float in [0, 1], default 0.15
    - ota_presence: List[str], default ["booking", "expedia"]
    - region: str, one of known regions
    - whatsapp_number: Optional[str], validated format
    
    All percentage inputs are normalized to 0-1 range.
    """
    
    # Required fields
    rooms: int
    adr_cop: float
    
    # Optional fields with defaults
    occupancy_rate: float = 0.50
    direct_channel_percentage: float = 0.0
    ota_commission_rate: float = 0.15
    ota_presence: List[str] = field(default_factory=lambda: ["booking", "expedia"])
    region: str = "default"
    whatsapp_number: Optional[str] = None
    hotel_name: Optional[str] = None
    hotel_url: Optional[str] = None
    
    # Known regions from plan_maestro
    KNOWN_REGIONS = {"eje_cafetero", "caribe", "antioquia", "default", "bogota"}
    
    # Validation constants
    MAX_ROOMS = 500
    MIN_ROOMS = 1
    MAX_ADR_COP = 5_000_000  # 5M COP max
    MIN_ADR_COP = 10_000     # 10K COP min
    
    def validate(self) -> ValidationResult:
        """Validate all inputs and return result."""
        errors = []
        warnings = []
        normalized = {}
        
        # Validate rooms
        rooms_result = self._validate_rooms()
        if rooms_result[0]:  # is error
            errors.append(rooms_result[1])
        else:
            normalized["rooms"] = rooms_result[2]
        
        # Validate ADR
        adr_result = self._validate_adr()
        if adr_result[0]:
            errors.append(adr_result[1])
        else:
            normalized["adr_cop"] = adr_result[2]
        
        # Validate occupancy (with normalization)
        occ_result = self._validate_occupancy()
        if occ_result[0]:
            errors.append(occ_result[1])
        else:
            normalized["occupancy_rate"] = occ_result[2]
        
        # Validate direct channel percentage
        dcp_result = self._validate_direct_channel()
        if dcp_result[0]:
            errors.append(dcp_result[1])
        else:
            normalized["direct_channel_percentage"] = dcp_result[2]
        
        # Validate OTA commission
        comm_result = self._validate_commission()
        if comm_result[0]:
            errors.append(comm_result[1])
        else:
            normalized["ota_commission_rate"] = comm_result[2]
        
        # Validate region
        region_result = self._validate_region()
        if region_result[0]:
            warnings.append(region_result[1])
        normalized["region"] = region_result[2] if not region_result[0] else "default"
        
        # Validate WhatsApp (optional)
        if self.whatsapp_number:
            wa_result = self._validate_whatsapp()
            if wa_result[0]:
                warnings.append(wa_result[1])
            else:
                normalized["whatsapp_number"] = wa_result[2]
        
        # Copy other fields
        normalized["ota_presence"] = self.ota_presence
        normalized["hotel_name"] = self.hotel_name
        normalized["hotel_url"] = self.hotel_url
        
        is_valid = not any(e.severity == ValidationSeverity.CRITICAL for e in errors)
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            normalized_data=normalized
        )
    
    def _validate_rooms(self) -> Tuple[bool, Optional[ValidationError], Optional[int]]:
        """Validate rooms field."""
        if not isinstance(self.rooms, int):
            return True, ValidationError(
                field="rooms",
                message=f"rooms must be integer, got {type(self.rooms).__name__}",
                severity=ValidationSeverity.CRITICAL,
                value=self.rooms
            ), None
        
        if self.rooms < self.MIN_ROOMS:
            return True, ValidationError(
                field="rooms",
                message=f"rooms must be >= {self.MIN_ROOMS}, got {self.rooms}",
                severity=ValidationSeverity.CRITICAL,
                value=self.rooms
            ), None
        
        if self.rooms > self.MAX_ROOMS:
            return True, ValidationError(
                field="rooms",
                message=f"rooms exceeds maximum {self.MAX_ROOMS}, got {self.rooms}",
                severity=ValidationSeverity.ERROR,
                value=self.rooms
            ), None
        
        return False, None, self.rooms
    
    def _validate_adr(self) -> Tuple[bool, Optional[ValidationError], Optional[float]]:
        """Validate ADR field."""
        try:
            adr = float(self.adr_cop)
        except (TypeError, ValueError):
            return True, ValidationError(
                field="adr_cop",
                message=f"adr_cop must be numeric, got {type(self.adr_cop).__name__}",
                severity=ValidationSeverity.CRITICAL,
                value=self.adr_cop
            ), None
        
        if adr <= 0:
            return True, ValidationError(
                field="adr_cop",
                message=f"adr_cop must be positive, got {adr}",
                severity=ValidationSeverity.CRITICAL,
                value=adr
            ), None
        
        if adr < self.MIN_ADR_COP:
            return True, ValidationError(
                field="adr_cop",
                message=f"adr_cop below minimum {self.MIN_ADR_COP}, got {adr}",
                severity=ValidationSeverity.ERROR,
                value=adr
            ), None
        
        if adr > self.MAX_ADR_COP:
            return True, ValidationError(
                field="adr_cop",
                message=f"adr_cop exceeds maximum {self.MAX_ADR_COP}, got {adr}",
                severity=ValidationSeverity.ERROR,
                value=adr
            ), None
        
        return False, None, round(adr, 2)
    
    def _validate_occupancy(self) -> Tuple[bool, Optional[ValidationError], Optional[float]]:
        """Validate occupancy rate (normalizes 0-100 to 0-1)."""
        try:
            occ = float(self.occupancy_rate)
        except (TypeError, ValueError):
            return True, ValidationError(
                field="occupancy_rate",
                message=f"occupancy_rate must be numeric",
                severity=ValidationSeverity.CRITICAL,
                value=self.occupancy_rate
            ), None
        
        # Normalize if > 1 (user entered percentage)
        if occ > 1.0
