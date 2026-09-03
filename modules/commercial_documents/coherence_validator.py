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
    
    def save(self, output_path: str, filename: str = "coherence_validation.json") -> str:
        """Save report to JSON file.
        
        Args:
            output_path: Directory path or full file path. 
                         If it ends with .json, uses it as the target file.
                         Otherwise, treats it as a directory and creates {filename} inside.
            filename: Default filename when output_path is a directory (default: coherence_validation.json)
        """
        path = Path(output_path)
        if path.suffix == '.json':
            # Full file path — use as-is
            pass
        else:
            # Directory — create filename inside
            path = path / filename
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
        validation_summary: ValidationSummary,
        whatsapp_html_detected: bool = False,
        generated_assets: Optional[Dict[str, Any]] = None,  # FASE-2-PATCH-A
        site_presence_report: Optional[Dict[str, Any]] = None,  # FASE-0 (DT-4): SitePresence boost
    ) -> CoherenceReport:
        """
        Execute all coherence validations.

        Args:
            diagnostic: The diagnostic document
            proposal: The proposal document
            assets: List of proposed assets
            validation_summary: Validation summary with confidence data
            whatsapp_html_detected: Whether WhatsApp was detected in HTML
            generated_assets: Dict of generated assets with confidence scores (post-gen only)
            site_presence_report: Canonical dict from normalize_site_presence() —
                carries site_verified and confidence per asset type. Used by
                _check_whatsapp_verified() to boost confidence when
                SitePresenceChecker confirmed WhatsApp exists on the real site.

        Returns:
            CoherenceReport with all validation results
        """
        self.checks = []
        
        # Run all checks
        self.checks.append(self._check_problems_have_solutions(diagnostic, assets))
        self.checks.append(self._check_assets_are_justified(assets, diagnostic))
        self.checks.append(self._check_financial_data_validated(proposal, validation_summary))
        self.checks.append(self._check_whatsapp_verified(assets, validation_summary, whatsapp_html_detected, site_presence_report))
        self.checks.append(self._check_price_matches_pain(proposal, diagnostic))
        self.checks.append(self._check_promised_assets_exist(assets, diagnostic, generated_assets, site_presence_report))
        
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

        # FASE-C (Punto 8, AC6): el complemento siempre-activo se GENERA pero no
        # se PROMETE por pain (counts_in_alignment=False en el registro canónico),
        # así que nunca puede tener un pain_id que lo justifique. Dejarlo en el
        # denominador condena este check a < 0.8 en toda corrida y vuelve
        # is_coherent=False estructural, no por el hotel analizado. Fuera del
        # denominador; los dientes quedan para cualquier otro asset sin pain.
        from modules.asset_generation.proposal_asset_alignment import (
            ALWAYS_ACTIVE_COMPLEMENT_ASSETS,
        )
        promised_assets = [
            a for a in assets
            if getattr(a, "asset_type", "") not in ALWAYS_ACTIVE_COMPLEMENT_ASSETS
        ]
        complementos = len(assets) - len(promised_assets)

        if not promised_assets:
            return CoherenceCheck(
                name="assets_are_justified",
                passed=True,
                score=1.0,
                message=(
                    "Ningún asset prometido por brecha que validar "
                    f"({complementos} complemento(s) siempre-activo(s) fuera del denominador)"
                    if complementos
                    else "No assets to validate"
                ),
                severity="info"
            )

        justified_assets = 0
        for asset in promised_assets:
            if any(pid in problem_ids for pid in asset.pain_ids):
                justified_assets += 1
        
        total_assets = len(promised_assets)
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
        validation_summary: ValidationSummary,
        whatsapp_html_detected: bool = False,
        site_presence_report: Optional[Dict[str, Any]] = None,  # FASE-0 (DT-4): SitePresence boost
    ) -> CoherenceCheck:
        """
        If there's a whatsapp_button asset, validate that the number has sufficient confidence.
        
        FASE-0 (DT-4): If site_presence_report confirms WhatsApp exists on the site,
        boost confidence to 0.95+ to avoid false-negative coherence failures.

        Score: 1.0 if passes, 0.0 if fails
        Failure (blocking): If confidence < threshold (configurable, default 0.9)
        """
        # FASE-0 (DT-4): Boost confidence if SitePresenceChecker confirmed WhatsApp exists
        site_whatsapp_exists = False
        if site_presence_report:
            whatsapp_presence = site_presence_report.get("whatsapp_button", {})
            if isinstance(whatsapp_presence, dict):
                presence_status = whatsapp_presence.get("presence_status") or whatsapp_presence.get("status", "")
                site_whatsapp_exists = presence_status == "exists"

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
        
        # Si hay WhatsApp en HTML pero no en ValidationSummary, no penalizar
        if not whatsapp_field and whatsapp_html_detected:
            return CoherenceCheck(
                name="whatsapp_verified",
                passed=not is_blocking,
                score=0.5,
                message="WhatsApp detectado en HTML (sin verificacion cruzada)",
                severity="warning" if not is_blocking else "info"
            )
        
        if not whatsapp_field:
            return CoherenceCheck(
                name="whatsapp_verified",
                passed=not is_blocking,
                score=0.0,
                message="WhatsApp button requiere validación pero no hay campo 'whatsapp_number'",
                severity="error" if is_blocking else "warning"
            )
        
        confidence_score = self._confidence_level_to_score(whatsapp_field.confidence)

        # FASE-0 (DT-4): If site confirms WhatsApp exists, boost confidence
        if site_whatsapp_exists:
            confidence_score = max(confidence_score, 0.95)

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

        Formula: ratio = price_monthly / pain_monthly (ambos en COP/mes)
        - ratio < 0.03 (3%): precio muy bajo
        - 0.03 <= ratio <= 0.50: rango aceptable (PATCH-A: max_ratio 0.50 para min_price floors)
        - ratio > 0.50: precio muy alto (score penalizado)
        - NOTA: usa notación x internamente para legibilidad (0.03 = 3.0x)
        """
        price = proposal.price_monthly
        main = diagnostic.financial_impact
        pain = getattr(main, 'monthly_loss_central', None) or main.monthly_loss_max
        
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
    
    def _extract_verified_in_production_types(
        self,
        site_presence_report: Optional[Dict[str, Any]]
    ) -> set:
        """FASE-P2-A (F14): extrae asset_types verificados en producción.

        Un asset se considera "verificado en producción" cuando el
        site_presence_report (dict canónico de normalize_site_presence)
        confirma status "exists" o "redundant" con site_verified=True.

        Estos assets NO deben contarse como "missing" en promised_assets_exist
        aunque no tengan archivo físico generado, porque el sitio vivo ya los
        tiene implementados — coherente con el gate proposal_asset_alignment
        que los marca como "present_in_production".

        Args:
            site_presence_report: Dict canónico con resultados de SitePresenceChecker.

        Returns:
            Set de asset_type verificados en producción.
        """
        if not site_presence_report:
            return set()

        verified_types: set = set()
        # El dict canónico tiene "results" + keys de asset_type en top-level
        results = site_presence_report.get("results", {}) or {}

        # Iterar sobre ambos: top-level keys y "results" (pueden diferir)
        all_keys = set(results.keys())
        for key in site_presence_report:
            if key not in ("results", "site_url", "checked_at",
                           "site_reachable", "verification_errors",
                           "presence_status"):
                all_keys.add(key)

        for asset_type in all_keys:
            presence = results.get(asset_type) or site_presence_report.get(asset_type)
            if not isinstance(presence, dict):
                continue

            status = str(presence.get("status", "")).lower()
            site_verified = presence.get("site_verified", False)

            # Normalizar enum value si viene como PresenceStatus.value
            if hasattr(status, 'value'):
                status = str(status.value).lower()

            # FASE-SR-E (H7, L-SR3): criterio canónico — exists_with_issues
            # también cuenta como verificado en producción (el asset existe;
            # sus campos faltantes son mejora sugerida, no asset ausente).
            from ..asset_generation.site_presence_checker import (
                is_present_in_production,
            )
            if (
                status in ("redundant",) or is_present_in_production(status)
            ) and site_verified:
                verified_types.add(asset_type)

        return verified_types

    def _check_promised_assets_exist(
        self,
        assets: List[AssetSpec],
        diagnostic: DiagnosticDocument,
        generated_assets: Optional[Dict[str, Any]] = None,
        site_presence_report: Optional[Dict[str, Any]] = None
    ) -> CoherenceCheck:
        """Valida que todos los assets prometidos existen en el generador.

        SOURCE OF TRUTH (FASE-1-A): 
        - Si generated_assets viene del pipeline: verificar contra assets realmente generados
          (asset_generation_report.json: generated_assets[asset_type]['can_use'])
        - Si generated_assets=None: fallback al catalogo estatico is_asset_implemented()
          (comportamiento legacy preservado para backward compatibility)

        FASE-SOL2-B (Option C1): Also cross-references PROPOSAL_SERVICE_TO_ASSET
        to ensure all 7 promised services have implemented assets. This unifies
        the baseline with proposal_asset_alignment_gate (Gate 9).

        FASE-P2-A (F14): If site_presence_report confirms an asset exists in
        production (status "exists"/"redundant" + site_verified=True), it is
        treated as "present" even without a generated file. This aligns
        coherence with proposal_asset_alignment_gate, which already accepts
        "present_in_production" status.

        Both validators now agree on "what was promised":
        - coherence_validator: checks asset types from diagnostic + PROPOSAL_SERVICE_TO_ASSET
        - proposal_asset_alignment_gate: checks services from PROPOSAL_SERVICE_TO_ASSET
        """
        from ..asset_generation.asset_catalog import is_asset_implemented
        from ..asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET

        # FASE-P2-A (F14): asset_types verificados en el sitio vivo
        verified_in_production = self._extract_verified_in_production_types(
            site_presence_report
        )

        promised_types = {a.asset_type for a in assets}
        missing_types = []
        production_only_types = []  # F14: track for message clarity
        
        # H6 FIX: Use generated_assets as source of truth when available
        # For pre-gen, generated_assets=None -> use static catalog (legacy)
        # For post-gen, generated_assets dict -> trust it over static catalog.
        # IMPORTANT: empty dict {} means "no assets generated" (truthy, so use it)
        # but an asset missing from the dict means it was never scheduled, not failed.
        # We check: asset_type exists in dict AND can_use=True to consider it present.
        if generated_assets is not None:
            # Post-generation: each promised asset type must be in generated_assets with can_use=True
            # FASE-P2-A (F14): OR verified in production via site_presence_report
            for asset_type in promised_types:
                gen_info = generated_assets.get(asset_type, {})
                # can_use must be explicitly True (not just dict existing)
                if gen_info.get('can_use', False):
                    continue
                # F14: asset verificado en producción no es "missing"
                if asset_type in verified_in_production:
                    production_only_types.append(asset_type)
                    continue
                missing_types.append(asset_type)
        else:
            # Pre-generation fallback: use static catalog
            # F14: still accept site presence as valid
            for t in promised_types:
                if is_asset_implemented(t):
                    continue
                if t in verified_in_production:
                    production_only_types.append(t)
                    continue
                missing_types.append(t)

        # FASE-SOL2-B: Cross-check all PROPOSAL_SERVICE_TO_ASSET entries
        # Ensure every promised service maps to an implemented asset.
        # H6 FIX: When generated_assets is provided (post-gen), we already know
        # which asset types were actually generated. The PROPOSAL_SERVICE_TO_ASSET
        # cross-check is only meaningful when generated_assets=None (pre-gen).
        # With real generated_assets, we trust the orchestrator's actual output.
        missing_service_assets = []
        if not generated_assets:
            # Legacy pre-generation check: use static catalog for PROPOSAL_SERVICE_TO_ASSET
            for service_name, asset_type in PROPOSAL_SERVICE_TO_ASSET.items():
                if not is_asset_implemented(asset_type):
                    # F14: accept production-verified assets here too
                    if asset_type in verified_in_production:
                        continue
                    missing_service_assets.append(f"{service_name}→{asset_type}")

        # SOL-1: Deduplicate — if an asset_type appears in both lists,
        # prefer the service→asset format (more informative). Extract asset_type
        # from "service→asset" entries to avoid false duplicates.
        service_asset_types = set()
        for entry in missing_service_assets:
            if "\u2192" in entry:
                service_asset_types.add(entry.split("\u2192")[1])
        # Only include from missing_types if not also in missing_service_assets
        deduped_missing_types = [t for t in missing_types if t not in service_asset_types]
        all_missing = deduped_missing_types + missing_service_assets
        if not all_missing:
            # F14: enrich message with production-verified info
            prod_note = ""
            if production_only_types:
                prod_note = f" (incluye {len(production_only_types)} verificado(s) en producción: {', '.join(sorted(production_only_types))})"
            return CoherenceCheck(
                name="promised_assets_exist",
                passed=True,
                score=1.0,
                message=f"Todos los assets prometidos están implementados ({len(PROPOSAL_SERVICE_TO_ASSET)} servicios verificados via PROPOSAL_SERVICE_TO_ASSET){prod_note}",
                severity="info"
            )

        # Calcular score basado en % de assets disponibles
        total_checked = len(promised_types | set(PROPOSAL_SERVICE_TO_ASSET.values()))
        # F14: production-verified assets count as present for scoring
        effective_present = total_checked - len(set(all_missing))
        score = effective_present / total_checked if total_checked else 1.0

        msg_parts = []
        if missing_types:
            msg_parts.append(f"Assets no implementados: {', '.join(missing_types)}")
        if missing_service_assets:
            msg_parts.append(f"Servicios sin asset implementado: {', '.join(missing_service_assets)}")
        if production_only_types:
            msg_parts.append(f"Verificados en producción (sin archivo): {', '.join(sorted(production_only_types))}")

        return CoherenceCheck(
            name="promised_assets_exist",
            passed=False,
            score=score,
            message="; ".join(msg_parts),
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
