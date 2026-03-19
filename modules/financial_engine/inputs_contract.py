"""Financial Inputs Contract - Strict Validation for Financial Data."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
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
    normalized: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_critical_errors(self) -> bool:
        return any(e.severity == ValidationSeverity.CRITICAL for e in self.errors)


@dataclass
class FinancialInputsContract:
    """Contract for financial input validation."""

    rooms: int
    adr_cop: float
    occupancy_rate: float = 0.50
    direct_channel_percentage: float = 0.0
    ota_commission_rate: float = 0.15
    ota_presence: List[str] = field(default_factory=lambda: ["booking", "expedia"])
    region: str = "default"
    whatsapp_number: Optional[str] = None
    hotel_name: Optional[str] = None
    hotel_url: Optional[str] = None

    KNOWN_REGIONS = {"eje_cafetero", "caribe", "antioquia", "default"}
    MAX_ROOMS = 500
    MIN_ROOMS = 1
    MAX_ADR_COP = 5_000_000
    MIN_ADR_COP = 10_000

    def validate(self) -> ValidationResult:
        errors = []
        warnings = []
        normalized = {}

        # Validate rooms
        if not isinstance(self.rooms, int) or self.rooms < self.MIN_ROOMS:
            errors.append(ValidationError("rooms", f"rooms must be integer >= {self.MIN_ROOMS}", ValidationSeverity.CRITICAL, self.rooms))
        elif self.rooms > self.MAX_ROOMS:
            errors.append(ValidationError("rooms", f"rooms exceeds {self.MAX_ROOMS}", ValidationSeverity.ERROR, self.rooms))
        else:
            normalized["rooms"] = self.rooms

        # Validate ADR
        try:
            adr = float(self.adr_cop)
            if adr <= 0:
                errors.append(ValidationError("adr_cop", "adr_cop must be positive", ValidationSeverity.CRITICAL, adr))
            elif adr < self.MIN_ADR_COP:
                errors.append(ValidationError("adr_cop", f"adr_cop below {self.MIN_ADR_COP}", ValidationSeverity.ERROR, adr))
            elif adr > self.MAX_ADR_COP:
                errors.append(ValidationError("adr_cop", f"adr_cop exceeds {self.MAX_ADR_COP}", ValidationSeverity.ERROR, adr))
            else:
                normalized["adr_cop"] = round(adr, 2)
        except (TypeError, ValueError):
            errors.append(ValidationError("adr_cop", "adr_cop must be numeric", ValidationSeverity.CRITICAL, self.adr_cop))

        # Validate occupancy (normalize 0-100 to 0-1)
        try:
            occ = float(self.occupancy_rate)
            if occ > 1.0:
                occ = occ / 100.0
            if 0 <= occ <= 1.0:
                normalized["occupancy_rate"] = round(occ, 4)
            else:
                errors.append(ValidationError("occupancy_rate", "must be in [0,1] or [0,100]", ValidationSeverity.ERROR, self.occupancy_rate))
        except (TypeError, ValueError):
            errors.append(ValidationError("occupancy_rate", "must be numeric", ValidationSeverity.CRITICAL, self.occupancy_rate))

        # Validate direct channel
        try:
            dcp = float(self.direct_channel_percentage)
            if dcp > 1.0:
                dcp = dcp / 100.0
            if 0 <= dcp <= 1.0:
                normalized["direct_channel_percentage"] = round(dcp, 4)
            else:
                errors.append(ValidationError("direct_channel_percentage", "must be in [0,1] or [0,100]", ValidationSeverity.ERROR, self.direct_channel_percentage))
        except (TypeError, ValueError):
            errors.append(ValidationError("direct_channel_percentage", "must be numeric", ValidationSeverity.ERROR, self.direct_channel_percentage))

        # Validate commission
        try:
            comm = float(self.ota_commission_rate)
            if 0 <= comm <= 1.0:
                normalized["ota_commission_rate"] = round(comm, 4)
            else:
                warnings.append(ValidationError("ota_commission_rate", "out of range, using default", ValidationSeverity.WARNING, comm))
                normalized["ota_commission_rate"] = 0.15
        except (TypeError, ValueError):
            warnings.append(ValidationError("ota_commission_rate", "not numeric, using default", ValidationSeverity.WARNING, self.ota_commission_rate))
            normalized["ota_commission_rate"] = 0.15

        # Validate region
        if self.region not in self.KNOWN_REGIONS:
            warnings.append(ValidationError("region", f"Unknown region {self.region}, using default", ValidationSeverity.WARNING, self.region))
            normalized["region"] = "default"
        else:
            normalized["region"] = self.region

        # Copy other fields
        normalized["ota_presence"] = self.ota_presence
        normalized["hotel_name"] = self.hotel_name
        normalized["hotel_url"] = self.hotel_url

        is_valid = not any(e.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL) for e in errors)

        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings, normalized=normalized)

    @classmethod
    def from_dict(cls, data):
        return cls(
            rooms=data.get("rooms", 0),
            adr_cop=data.get("adr_cop", data.get("adr", 0)),
            occupancy_rate=data.get("occupancy_rate", data.get("occupancy", 0.50)),
            direct_channel_percentage=data.get("direct_channel_percentage", 0.0),
            ota_commission_rate=data.get("ota_commission_rate", 0.15),
            ota_presence=data.get("ota_presence", ["booking", "expedia"]),
            region=data.get("region", "default"),
            whatsapp_number=data.get("whatsapp_number"),
            hotel_name=data.get("hotel_name"),
            hotel_url=data.get("hotel_url"),
        )

    def to_hotel_financial_data(self):
        result = self.validate()
        if not result.is_valid:
            raise ValueError(f"Validation failed: {result.errors}")
        return result.normalized