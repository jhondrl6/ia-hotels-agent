"""Self-Healer Module for Agent Harness.

Provides error matching and recovery strategies for known error patterns.
v3.1: Added learning mode for unknown errors + lazy PlanValidator import.
"""

import json
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


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


class ErrorLearner:
    """Tracks unknown errors and suggests catalog entries.
    
    Groups errors by type/message pattern and provides a summary at
    session end with suggested catalog entries for user review.
    """
    
    DEFAULT_LEARN_PATH = Path(__file__).parent.parent / ".agent" / "memory" / "unknown_errors.json"
    
    def __init__(self, learn_path: Optional[Path] = None):
        self.learn_path = learn_path or self.DEFAULT_LEARN_PATH
        self.session_errors: Dict[str, int] = defaultdict(int)
        self.session_examples: Dict[str, str] = {}
        self._load_history()
        self._ensure_dir()
    
    def _ensure_dir(self):
        self.learn_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_history(self):
        """Load previous unknown error history."""
        if self.learn_path.exists():
            try:
                data = json.loads(self.learn_path.read_text(encoding="utf-8"))
                for key, count in data.get("counts", {}).items():
                    self.session_errors[key] += count
                self.session_examples.update(data.get("examples", {}))
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_history(self):
        """Persist unknown error accumulation."""
        try:
            data = {
                "counts": dict(self.session_errors),
                "examples": self.session_examples,
            }
            self.learn_path.with_suffix(".tmp").write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            self.learn_path.with_suffix(".tmp").replace(self.learn_path)
        except IOError:
            pass
    
    def record_unknown(self, exception: Exception) -> str:
        """Record an unmatched error and return its grouping key.
        
        Args:
            exception: The exception that was not matched.
            
        Returns:
            A grouping key (error_type: short_message) for this error.
        """
        error_type = type(exception).__name__
        # Use first 100 chars of message for grouping
        short_msg = str(exception)[:100].strip()
        key = f"{error_type}: {short_msg}"
        
        self.session_errors[key] += 1
        if key not in self.session_examples:
            self.session_examples[key] = str(exception)[:500]
        
        return key
    
    def get_suggestions(self) -> List[Dict[str, Any]]:
        """Get suggested catalog entries for recurring unknown errors.
        
        Only returns errors that occurred >= 2 times (to avoid noise).
        
        Returns:
            List of suggested error catalog entries.
        """
        suggestions = []
        for key, count in self.session_errors.items():
            if count < 2:
                continue
            
            # Parse key back to components
            if ":" in key:
                error_type = key.split(":")[0].strip()
            else:
                error_type = "RuntimeError"
            
            example = self.session_examples.get(key, "")
            
            # Suggest a retry_allowed=False entry (escalate) by default
            suggestions.append({
                "id": f"AUTO-{len(suggestions)+1:03d}",
                "name": f"Unknown {error_type}",
                "category": "unknown",
                "pattern_type": "contains",
                "pattern": error_type,
                "severity": "blocking",
                "recovery": {
                    "strategy": "escalate",
                    "message": f"Error no catalogado: {error_type}. Revisar manualmente.",
                    "retry_allowed": False,
                },
                "occurrences": count,
                "example": example,
                "note": "Generated by ErrorLearner. Review and adjust before adding to error_catalog.json",
            })
        
        return suggestions
    
    def flush(self):
        """Save accumulated errors to disk."""
        self._save_history()


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
        
        # Error learning for unknown errors
        self.learner = ErrorLearner()
    
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
            elif pattern_type == "contains":
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
        
        # No match found -- record for learning
        group_key = self.learner.record_unknown(exception)
        if self.verbose:
            print(f"[HEALER] [UNKNOWN] Error no catalogado registrado: {group_key}")
        
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
        """Ejecuta validacion local usando PlanValidator (lazy import).
        
        Args:
            target_path: Ruta al archivo o directorio a revisar (ignorado, usa Plan Maestro).
            
        Returns:
            Dict con el resultado de la validacion (severity_counts, findings).
        """
        if self.verbose:
            print(f"[HEALER] [REVIEW] Iniciando validacion local: {target_path}")
        
        try:
            # Lazy import to avoid module dependency at startup
            from modules.validation import PlanValidator
        except ImportError:
            if self.verbose:
                print(f"[HEALER] [WARN] PlanValidator no disponible. Omitiendo validacion.")
            return {
                "status": "skipped",
                "message": "PlanValidator module not available",
                "passed": True,
                "severity_counts": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
                "findings": [],
                "checks_run": [],
            }
        
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
            if self.verbose:
                print(f"[HEALER] [ERROR] Validacion fallo: {e}")
            return {"status": "error", "message": str(e)}

    def validate_fix(self, target_path: str) -> bool:
        """Valida si una correccion cumple con el Plan Maestro.
        
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
        
        if review_result.get("status") == "skipped":
            return True  # If PlanValidator is not available, don't block
        
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
    
    def get_learning_report(self) -> Dict[str, Any]:
        """Get a report of unknown errors learned this session.
        
        Returns:
            Dictionary with suggestions for new catalog entries.
        """
        suggestions = self.learner.get_suggestions()
        unknown_errors_count = len(self.learner.session_errors)
        
        return {
            "unknown_errors_tracked": unknown_errors_count,
            "suggestions_for_catalog": suggestions,
            "total_suggestions": len(suggestions),
        }
    
    def _flush_learner(self):
        """Persist learned errors to disk."""
        self.learner.flush()
