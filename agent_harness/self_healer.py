"""Self-Healer Module for Agent Harness.

Provides error matching and recovery strategies for known error patterns.
"""

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from modules.validation import PlanValidator


@dataclass
class RecoveryStrategy:
    """Defines how to recover from a known error.
    
    Attributes:
        strategy: Type of recovery ('retry_with_params', 'retry_with_delay', 'fallback_handler', 'escalate').
        message: Human-readable message about the recovery action.
        retry_allowed: Whether retrying is allowed for this error.
        param_adjustments: Dictionary of parameter adjustments for retry.
        delay_seconds: Delay before retry (for retry_with_delay).
        max_retries: Maximum number of retries allowed.
        fallback_function: Name of fallback function to use.
    """
    strategy: str
    message: str
    retry_allowed: bool = False
    param_adjustments: Dict[str, str] = field(default_factory=dict)
    delay_seconds: int = 0
    max_retries: int = 2
    fallback_function: Optional[str] = None


@dataclass
class ErrorMatch:
    """Result of matching an error against the catalog.
    
    Attributes:
        matched: True if error matched a known pattern.
        error_id: ID from the catalog (e.g., 'ERR-003').
        error_name: Human-readable name.
        category: Error category (e.g., 'network', 'api').
        severity: Error severity ('transient', 'blocking').
        recovery: Recovery strategy to apply.
    """
    matched: bool
    error_id: Optional[str] = None
    error_name: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    recovery: Optional[RecoveryStrategy] = None


class SelfHealer:
    """Matches errors against catalog and suggests recovery actions.
    
    Loads error patterns from error_catalog.json and provides matching
    and recovery capabilities.
    """
    
    DEFAULT_CATALOG_PATH = Path(__file__).parent.parent / ".agent" / "memory" / "error_catalog.json"
    
    def __init__(self, catalog_path: Optional[Path] = None, verbose: bool = True):
        """Initialize SelfHealer.
        
        Args:
            catalog_path: Path to error catalog JSON. Defaults to .agent/memory/error_catalog.json.
            verbose: If True, print healing actions.
        """
        self.catalog_path = catalog_path or self.DEFAULT_CATALOG_PATH
        self.verbose = verbose
        self._catalog: Dict[str, Any] = {}
        self._load_catalog()
    
    def _load_catalog(self) -> None:
        """Load error catalog from JSON file."""
        if not self.catalog_path.exists():
            if self.verbose:
                print(f"[HEALER] [WARN] Catalog not found: {self.catalog_path}")
            self._catalog = {"errors": []}
            return
        
        try:
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                self._catalog = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            if self.verbose:
                print(f"[HEALER] [WARN] Failed to load catalog: {e}")
            self._catalog = {"errors": []}
    
    def match_error(self, exception: Exception) -> ErrorMatch:
        """Match an exception against the error catalog.
        
        Args:
            exception: The exception to match.
            
        Returns:
            ErrorMatch with matched pattern info, or unmatched result.
        """
        error_text = f"{type(exception).__name__}: {str(exception)}"
        
        for error_def in self._catalog.get("errors", []):
            pattern = error_def.get("pattern", "")
            pattern_type = error_def.get("pattern_type", "regex")
            
            matched = False
            if pattern_type == "regex":
                try:
                    matched = bool(re.search(pattern, error_text, re.IGNORECASE))
                except re.error:
                    matched = pattern.lower() in error_text.lower()
            else:
                matched = pattern.lower() in error_text.lower()
            
            if matched:
                recovery_def = error_def.get("recovery", {})
                recovery = RecoveryStrategy(
                    strategy=recovery_def.get("strategy", "escalate"),
                    message=recovery_def.get("message", "Error conocido detectado."),
                    retry_allowed=recovery_def.get("retry_allowed", False),
                    param_adjustments=recovery_def.get("param_adjustments", {}),
                    delay_seconds=recovery_def.get("delay_seconds", 0),
                    max_retries=recovery_def.get("max_retries", 2),
                    fallback_function=recovery_def.get("fallback_function"),
                )
                
                if self.verbose:
                    print(f"[HEALER] [MATCH] Error conocido: {error_def.get('name')} ({error_def.get('id')})")
                    print(f"[HEALER] [INFO] {recovery.message}")
                
                return ErrorMatch(
                    matched=True,
                    error_id=error_def.get("id"),
                    error_name=error_def.get("name"),
                    category=error_def.get("category"),
                    severity=error_def.get("severity"),
                    recovery=recovery,
                )
        
        # No match found
        return ErrorMatch(matched=False)
    
    def apply_param_adjustments(
        self, 
        original_params: Dict[str, Any], 
        adjustments: Dict[str, str]
    ) -> Dict[str, Any]:
        """Apply parameter adjustments for retry.
        
        Args:
            original_params: Original task parameters.
            adjustments: Adjustment rules (e.g., {"timeout": "multiply:2"}).
            
        Returns:
            Modified parameters dictionary.
        """
        modified = dict(original_params)
        
        for param_name, adjustment in adjustments.items():
            if param_name not in modified:
                continue
            
            current_value = modified[param_name]
            if not isinstance(current_value, (int, float)):
                continue
            
            if adjustment.startswith("multiply:"):
                factor = float(adjustment.split(":")[1])
                result = current_value * factor
                modified[param_name] = int(result) if isinstance(current_value, int) else result
            elif adjustment.startswith("add:"):
                addend = float(adjustment.split(":")[1])
                result = current_value + addend
                modified[param_name] = int(result) if isinstance(current_value, int) else result
            elif adjustment.startswith("set:"):
                new_value = adjustment.split(":")[1]
                try:
                    modified[param_name] = float(new_value) if "." in new_value else int(new_value)
                except ValueError:
                    modified[param_name] = new_value
        
        return modified
    
    def should_retry(self, match: ErrorMatch, current_retries: int) -> bool:
        """Check if we should retry based on match and retry count.
        
        Args:
            match: The ErrorMatch from match_error().
            current_retries: Number of retries already attempted.
            
        Returns:
            True if retry is recommended.
        """
        if not match.matched or not match.recovery:
            return False
        
        if not match.recovery.retry_allowed:
            return False
        
        if current_retries >= match.recovery.max_retries:
            if self.verbose:
                print(f"[HEALER] [WARN] Max retries ({match.recovery.max_retries}) reached.")
            return False
        
        return True
    
    def execute_recovery(
        self, 
        match: ErrorMatch, 
        payload: Dict[str, Any],
        retry_count: int
    ) -> Tuple[bool, Dict[str, Any], Optional[float]]:
        """Execute recovery strategy and return modified payload.
        
        Args:
            match: The ErrorMatch with recovery strategy.
            payload: Original task payload.
            retry_count: Current retry attempt number.
            
        Returns:
            Tuple of (should_retry, modified_payload, delay_seconds).
        """
        if not match.recovery:
            return False, payload, None
        
        strategy = match.recovery.strategy
        
        if strategy == "escalate":
            if self.verbose:
                print(f"[HEALER] [ALERT] Escalando a intervencion humana.")
            return False, payload, None
        
        if strategy == "retry_with_params":
            modified = self.apply_param_adjustments(
                payload, 
                match.recovery.param_adjustments
            )
            if self.verbose:
                print(f"[HEALER] [RETRY] Reintento {retry_count + 1} con parametros ajustados.")
            return True, modified, None
        
        if strategy == "retry_with_delay":
            delay = match.recovery.delay_seconds
            if self.verbose:
                print(f"[HEALER] [WAIT] Esperando {delay}s antes de reintentar...")
            time.sleep(delay)
            return True, payload, delay
        
        if strategy == "fallback_handler":
            if self.verbose:
                print(f"[HEALER] [FALLBACK] Usando fallback: {match.recovery.fallback_function}")
            # Fallback handling is done at the Harness level
            return False, payload, None
        
        return False, payload, None

    def run_automated_review(self, target_path: str) -> Dict[str, Any]:
        """Ejecuta validacion local usando PlanValidator.
        
        Args:
            target_path: Ruta al archivo o directorio a revisar (ignorado, usa Plan Maestro).
            
        Returns:
            Dict con el resultado de la revisión (severity_counts, findings).
        """
        if self.verbose:
            print(f"[HEALER] [REVIEW] Iniciando validacion local: {target_path}")
        
        try:
            validator = PlanValidator()
            result = validator.validate()
            
            findings = []
            for error in result.errors:
                findings.append({
                    "id": "VALIDATION-ERROR",
                    "severity": "HIGH",
                    "message": error
                })
            for warning in result.warnings:
                findings.append({
                    "id": "VALIDATION-WARNING",
                    "severity": "MEDIUM",
                    "message": warning
                })
            
            severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for f in findings:
                sev = f.get("severity", "LOW")
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
            
            return {
                "status": "success",
                "passed": result.passed,
                "severity_counts": severity_counts,
                "findings": findings,
                "checks_run": result.checks_run
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def validate_fix(self, target_path: str) -> bool:
        """Valida si una corrección cumple con el Plan Maestro.
        
        Args:
            target_path: Ruta al archivo corregido.
            
        Returns:
            True si no hay problemas de severidad 'HIGH'.
        """
        review_result = self.run_automated_review(target_path)
        
        if review_result.get("status") == "error":
            if self.verbose:
                print(f"[HEALER] [WARN] Error en validacion: {review_result.get('message')}")
            return False

        high_issues = review_result.get("severity_counts", {}).get("HIGH", 0)
        
        if high_issues > 0:
            if self.verbose:
                print(f"[HEALER] [FAIL] Validacion fallida: {high_issues} problemas de severidad ALTA.")
                for finding in review_result.get("findings", []):
                    if finding.get("severity") == "HIGH":
                        print(f"  - [{finding.get('id')}] {finding.get('message')}")
            return False
            
        if self.verbose:
            print("[HEALER] [OK] Validacion exitosa contra Plan Maestro.")
        return True
