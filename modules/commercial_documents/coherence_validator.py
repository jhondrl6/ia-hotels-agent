"""
Coherence Validator for Commercial Documents v4.2.0.

Validates that diagnostic, proposal, and assets are aligned
and coherent with each other.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .data_structures import (
    DiagnosticDocument,
    ProposalDocument,
    AssetSpec,
    ValidationSummary,
    ConfidenceLevel
)
from .coherence_config import CoherenceConfig, CoherenceRule, get_coherence_config


@dataclass
class CoherenceCheck:
    """Result of a single coherence check."""
    name: str
    passed: bool
    score: float  # 0.0 - 1.0
    message: str
    severity: str  # "error", "warning", "info"


@dataclass
class CoherenceReport:
    """Complete coherence validation report."""
    is_coherent: bool
    overall_score: float  # Promedio de scores
    checks: List[CoherenceCheck]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "4.2.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "is_coherent": self.is_coherent,
            "overall_score": round(self.overall_score, 2),
            "checks": [
                {
                    "name": c.name,
                    "passed": c.passed,
                    "score": round(c.score, 2),
                    "message": c.message,
                    "severity": c.severity
                }
                for c in self.checks
            ],
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": self.timestamp,
            "version": self.version
        }
    
    def save(self, output_path: str) -> str:
        """Save report to JSON file."""
        path = Path(output_path) / "coherence_validation.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        return str(path)


class CoherenceValidator:
    """
    Validates that diagnostic, proposal and assets are aligned.
    
    Ensures:
    - Every problem has at least one solution
    - Every asset is justified by a problem
    - Financial data comes from validated sources
    - WhatsApp numbers are verified before use
    - Price is proportional to financial pain (Sesión 5: usa decimal interno, notación x en mensajes)
    """
    
    # Pesos para cada check (checks críticos tienen mayor peso)
    CHECK_WEIGHTS = {
        "problems_have_solutions": 1.5,    # Crítico: problemas sin solución = propuesta vacía
        "assets_are_justified": 1.0,       # Normal
        "financial_data_validated": 1.5,   # Crítico: datos financieros base del ROI
        "whatsapp_verified": 0.5,          # Menor: solo relevante si hay WA button
        "price_matches_pain": 1.0,         # Normal
        "promised_assets_exist": 2.0        # Peso alto: crítico
    }
    
    def __init__(self, config: Optional[CoherenceConfig] = None, confidence_threshold: Optional[float] = None):
        self.config = config or get_coherence_config()
        # Backwards compatibility: if confidence_threshold is passed, create a custom config
        if confidence_threshold is not None and config is None:
            self.config = CoherenceConfig()
            # Override the financial_data_validated threshold
            if 'financial_data_validated' in self.config._rules:
                rule = self.config._rules['financial_data_validated']
                self.config._rules['financial_data_validated'] = CoherenceRule(
                    name=rule.name,
                    confidence_threshold=confidence_threshold,
                    blocking=rule.blocking,
                    description=rule.description
                )
        self.checks: List[CoherenceCheck] = []
    
    def validate(
        self,
        diagnostic: DiagnosticDocument,
        proposal: ProposalDocument,
        assets: List[AssetSpec],
        validation_summary: ValidationSummary
    ) -> CoherenceReport:
        """
        Execute all coherence validations.
        
        Args:
            diagnostic: The diagnostic document
            proposal: The proposal document
            assets: List of proposed assets
            validation_summary: Validation summary with confidence data
            
        Returns:
            CoherenceReport with all validation results
        """
        self.checks = []
        
        # Run all checks
        self.checks.append(self._check_problems_have_solutions(diagnostic, assets))
        self.checks.append(self._check_assets_are_justified(assets, diagnostic))
        self.checks.append(self._check_financial_data_validated(proposal, validation_summary))
        self.checks.append(self._check_whatsapp_verified(assets, validation_summary))
        self.checks.append(self._check_price_matches_pain(proposal, diagnostic))
        self.checks.append(self._check_promised_assets_exist(assets, diagnostic))
        
        # Calculate weighted overall score
        total_weight = sum(self.CHECK_WEIGHTS.get(c.name, 1.0) for c in self.checks)
        weighted_score = sum(
            c.score * self.CHECK_WEIGHTS.get(c.name, 1.0) 
            for c in self.checks
        )
        overall_score = weighted_score / total_weight if total_weight > 0 else 0.0
        
        # Collect errors and warnings
        errors = []
        warnings = []
        
        for check in self.checks:
            if check.severity == "error" and not check.passed:
                errors.append(f"[{check.name}] {check.message}")
            elif check.severity == "warning" and not check.passed:
                warnings.append(f"[{check.name}] {check.message}")
        
        # Determine if coherent
        # Coherent if: no errors AND overall_score >= threshold (default 0.8)
        threshold = self.config.get_threshold('overall_coherence')
        is_coherent = len(errors) == 0 and overall_score >= threshold
        
        return CoherenceReport(
            is_coherent=is_coherent,
            overall_score=overall_score,
            checks=self.checks,
            errors=errors,
            warnings=warnings
        )
    
    def _check_problems_have_solutions(
        self, 
        diagnostic: DiagnosticDocument, 
        assets: List[AssetSpec]
    ) -> CoherenceCheck:
        """
        Validate that each problem in the diagnostic has at least one asset that solves it.
        
        Score: % of problems with solution
        Failure: If < 50% of problems have solution
        """
        problems = diagnostic.problems
        if not problems:
            return CoherenceCheck(
                name="problems_have_solutions",
                passed=True,
                score=1.0,
                message="No problems detected in diagnostic",
                severity="info"
            )
        
        # Get all pain_ids covered by assets
        covered_pain_ids = set()
        for asset in assets:
            covered_pain_ids.update(asset.pain_ids)
        
        # Count problems with solutions
        # Handle both Pain objects (with id attribute) and dicts
        problems_with_solution = 0
        for problem in problems:
            if hasattr(problem, 'id'):
                if problem.id in covered_pain_ids:
                    problems_with_solution += 1
            elif isinstance(problem, dict) and problem.get('id') in covered_pain_ids:
                problems_with_solution += 1
        
        total_problems = len(problems)
        score = problems_with_solution / total_problems if total_problems > 0 else 1.0
        
        if score >= 0.8:
            passed = True
            severity = "info"
            message = f"{int(score * 100)}% de problemas tienen solución automática"
        elif score >= 0.5:
            passed = True
            severity = "warning"
            message = f"Solo {int(score * 100)}% de problemas tienen solución ({problems_with_solution}/{total_problems})"
        else:
            passed = False
            severity = "error"
            message = f"Solo {int(score * 100)}% de problemas tienen solución - propuesta incompleta"
        
        return CoherenceCheck(
            name="problems_have_solutions",
            passed=passed,
            score=score,
            message=message,
            severity=severity
        )
    
    def _check_assets_are_justified(
        self,
        assets: List[AssetSpec],
        diagnostic: DiagnosticDocument
    ) -> CoherenceCheck:
        """
        Validate that each asset is justified by at least one problem in diagnostic.
        
        Score: % of assets with justification
        Failure: If > 20% of assets have no justification
        """
        if not assets:
            return CoherenceCheck(
                name="assets_are_justified",
                passed=True,
                score=1.0,
                message="No assets to validate",
                severity="info"
            )
        
        problem_ids = set()
        for problem in diagnostic.problems:
            if hasattr(problem, 'id'):
                problem_ids.add(problem.id)
            elif isinstance(problem, dict):
                problem_ids.add(problem.get('id'))
        
        justified_assets = 0
        for asset in assets:
            if any(pid in problem_ids for pid in asset.pain_ids):
                justified_assets += 1
        
        total_assets = len(assets)
        score = justified_assets / total_assets if total_assets > 0 else 1.0
        
        if score >= 0.9:
            passed = True
            severity = "info"
            message = f"{int(score * 100)}% de assets justificados"
        elif score >= 0.8:
            passed = True
            severity = "warning"
            message = f"{int(score * 100)}% de assets justificados ({justified_assets}/{total_assets})"
        else:
            passed = False
            severity = "error"
            message = f"Solo {int(score * 100)}% de assets tienen justificación"
        
        return CoherenceCheck(
            name="assets_are_justified",
            passed=passed,
            score=score,
            message=message,
            severity=severity
        )
    
    def _check_financial_data_validated(
        self,
        proposal: ProposalDocument,
        validation_summary: ValidationSummary
    ) -> CoherenceCheck:
        """
        Validate that financial data comes from fields with sufficient confidence.
        
        Score: Average confidence of financial fields
        Warning: If any field < threshold (configurable)
        """
        # Financial fields to check
        financial_fields = ['adr_cop', 'rooms', 'occupancy_rate', 'direct_channel_percentage']
        
        confidences = []
        low_confidence_fields = []
        threshold = self.config.get_threshold('financial_data_validated')
        is_blocking = self.config.is_blocking('financial_data_validated')
        
        for field_name in financial_fields:
            field = validation_summary.get_field(field_name)
            if field:
                # Convert confidence level to numeric score
                confidence_score = self._confidence_level_to_score(field.confidence)
                confidences.append(confidence_score)
                
                if confidence_score < threshold:
                    low_confidence_fields.append(field_name)
        
        score = sum(confidences) / len(confidences) if confidences else 0.0
        
        if not low_confidence_fields:
            passed = True
            severity = "info"
            message = f"Datos financieros validados (confidence promedio: {score:.2f})"
        elif score >= threshold:
            passed = True
            severity = "warning"
            message = f"Algunos campos financieros con baja confianza: {', '.join(low_confidence_fields)}"
        else:
            passed = not is_blocking  # Si es blocking, falla; si no, pasa con warning
            severity = "error" if is_blocking else "warning"
            message = f"Datos financieros insuficientemente validados: {', '.join(low_confidence_fields)}"
        
        return CoherenceCheck(
            name="financial_data_validated",
            passed=passed,
            score=score,
            message=message,
            severity=severity
        )
    
    def _check_whatsapp_verified(
        self,
        assets: List[AssetSpec],
        validation_summary: ValidationSummary
    ) -> CoherenceCheck:
        """
        If there's a whatsapp_button asset, validate that the number has sufficient confidence.
        
        Score: 1.0 if passes, 0.0 if fails
        Failure (blocking): If confidence < threshold (configurable, default 0.9)
        """
        threshold = self.config.get_threshold('whatsapp_verified')
        is_blocking = self.config.is_blocking('whatsapp_verified')
        
        # Check if whatsapp_button is in assets
        has_whatsapp_button = any(
            asset.asset_type == "whatsapp_button" for asset in assets
        )
        
        if not has_whatsapp_button:
            return CoherenceCheck(
                name="whatsapp_verified",
                passed=True,
                score=1.0,
                message="No hay asset de WhatsApp button",
                severity="info"
            )
        
        # Check WhatsApp field confidence
        whatsapp_field = validation_summary.get_field("whatsapp_number")
        
        if not whatsapp_field:
            return CoherenceCheck(
                name="whatsapp_verified",
                passed=not is_blocking,
                score=0.0,
                message="WhatsApp button requiere validación pero no hay campo 'whatsapp_number'",
                severity="error" if is_blocking else "warning"
            )
        
        confidence_score = self._confidence_level_to_score(whatsapp_field.confidence)
        
        if confidence_score >= threshold:
            return CoherenceCheck(
                name="whatsapp_verified",
                passed=True,
                score=1.0,
                message=f"WhatsApp verificado con confidence {confidence_score:.2f}",
                severity="info"
            )
        elif confidence_score >= threshold - 0.2:  # 0.2 margin for warning
            return CoherenceCheck(
                name="whatsapp_verified",
                passed=not is_blocking,
                score=confidence_score,
                message=f"WhatsApp con confidence {confidence_score:.2f} - requiere >= {threshold}",
                severity="error" if is_blocking else "warning"
            )
        else:
            return CoherenceCheck(
                name="whatsapp_verified",
                passed=not is_blocking,
                score=confidence_score,
                message=f"WhatsApp con confidence insuficiente ({confidence_score:.2f}) - requiere >= {threshold}",
                severity="error" if is_blocking else "warning"
            )
    
    def _check_price_matches_pain(
        self,
        proposal: ProposalDocument,
        diagnostic: DiagnosticDocument
    ) -> CoherenceCheck:
        """
        Validate that proposal price is coherent with financial pain.
        
        NOTA (Sesión 5 - M-001):
        - Usa unidades DECIMAL internamente (0.03 = 3%, 0.06 = 6%)
        - Muestra notación x en mensajes para legibilidad (3.0x = 3%)
        """
        price = proposal.price_monthly
        pain = diagnostic.financial_impact.monthly_loss_max
        
        if pain <= 0:
            return CoherenceCheck(
                name="price_matches_pain",
                passed=True,
                score=1.0,
                message="No hay dolor financiero calculado",
                severity="info"
            )
        
        price_rule = self.config.get_price_rule()
        ratio = price / pain  # Decimal (ej: 0.05 = 5%)
        
        # Convertir a notación x para mensajes legibles
        ratio_x = price_rule.to_x_notation(ratio)
        min_x = price_rule.to_x_notation(price_rule.min_ratio)
        max_x = price_rule.to_x_notation(price_rule.max_ratio)
        ideal_x = price_rule.to_x_notation(price_rule.ideal_ratio)
        
        # Rangos de tolerancia en decimal
        ideal_range_margin = 0.005  # +/- 0.5%
        ideal_range_min = price_rule.ideal_ratio - ideal_range_margin
        ideal_range_max = price_rule.ideal_ratio + ideal_range_margin
        
        # Validación usando DECIMAL (0.03-0.06)
        if ideal_range_min <= ratio <= ideal_range_max:
            score = 1.0
            passed = True
            severity = "info"
            message = f"Precio ({ratio_x:.1f}x del dolor) en rango ideal ({ideal_x:.1f}x)"
        elif price_rule.min_ratio <= ratio < ideal_range_min or ideal_range_max < ratio <= price_rule.max_ratio:
            score = 0.8
            passed = True
            severity = "warning"
            if ratio < ideal_range_min:
                message = f"Precio en límite inferior ({ratio_x:.1f}x) - rango ideal {min_x:.1f}x-{max_x:.1f}x"
            else:
                message = f"Precio en límite superior ({ratio_x:.1f}x) - rango ideal {min_x:.1f}x-{max_x:.1f}x"
        elif ratio < price_rule.min_ratio:
            score = max(0.0, ratio / price_rule.min_ratio)
            passed = False
            severity = "warning"
            message = f"Precio muy bajo ({ratio_x:.1f}x del dolor) - mínimo recomendado {min_x:.1f}x"
        else:  # ratio > price_rule.max_ratio
            score = max(0.0, 1 - (ratio - price_rule.max_ratio) / price_rule.max_ratio)
            passed = False
            severity = "warning"
            message = f"Precio muy alto ({ratio_x:.1f}x del dolor) - máximo recomendado {max_x:.1f}x"
        
        return CoherenceCheck(
            name="price_matches_pain",
            passed=passed,
            score=score,
            message=message,
            severity=severity
        )
    
    def _check_promised_assets_exist(
        self,
        assets: List[AssetSpec],
        diagnostic: DiagnosticDocument
    ) -> CoherenceCheck:
        """Valida que todos los assets prometidos existen en el generador."""
        from ..asset_generation.asset_catalog import is_asset_implemented
        
        promised_types = {a.asset_type for a in assets}
        missing_types = [
            t for t in promised_types 
            if not is_asset_implemented(t)
        ]
        
        if not missing_types:
            return CoherenceCheck(
                name="promised_assets_exist",
                passed=True,
                score=1.0,
                message="Todos los assets prometidos están implementados",
                severity="info"
            )
        
        # Calcular score basado en % de assets disponibles
        score = (len(promised_types) - len(missing_types)) / len(promised_types) if promised_types else 1.0
        
        return CoherenceCheck(
            name="promised_assets_exist",
            passed=False,
            score=score,
            message=f"Assets prometidos no implementados: {', '.join(missing_types)}",
            severity="error"  # BLOCKING: no prometer lo que no se puede entregar
        )
    
    def _confidence_level_to_score(self, confidence: ConfidenceLevel) -> float:
        """Convert ConfidenceLevel to numeric score."""
        mapping = {
            ConfidenceLevel.VERIFIED: 0.95,
            ConfidenceLevel.ESTIMATED: 0.7,
            ConfidenceLevel.CONFLICT: 0.3,
            ConfidenceLevel.UNKNOWN: 0.0
        }
        return mapping.get(confidence, 0.0)
