"""
v4 Asset Orchestrator for IA Hoteles Agent.

Orquesta la generación de assets conectando:
- Validación cruzada (v4.0)
- Mapeo problemas → soluciones
- Generación condicional (ConditionalGenerator)
- Validación de coherencia
"""

import json
import logging

logger = logging.getLogger(__name__)
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from ..commercial_documents.data_structures import (
    V4AuditResult,
    ValidationSummary,
    DiagnosticDocument,
    ProposalDocument,
    AssetSpec,
    ValidatedField
)
from ..commercial_documents.pain_solution_mapper import PainSolutionMapper, Pain
from ..commercial_documents.coherence_validator import CoherenceValidator, CoherenceReport
from .conditional_generator import ConditionalGenerator
from .asset_diagnostic_linker import AssetDiagnosticLinker, AssetMetadata
from .asset_content_validator import AssetContentValidator, ContentStatus
from .site_presence_checker import SitePresenceChecker  # FASE-CAUSAL-01
from .data_assessment import DataAssessment, DataClassification  # FASE-I-01
from .geo_enriched_bridge import try_enrich_from_geo_enriched  # FASE-GEO-BRIDGE
from .pain_ledger import PainLedger  # FASE-0B: PainLedger facade
from ..geo_enrichment.geo_flow import GeoFlow  # FASE-6: GEO Flow
from ..orchestration.post_orchestrator_reconciler import PostOrchestratorReconciler  # FASE-0: DT-4 reconciliador
from data_models.canonical_assessment import (  # FASE-6: Canonical Assessment
    CanonicalAssessment,
    SiteMetadata,
    SchemaAnalysis,
    PerformanceAnalysis,
    PerformanceMetrics
)


@dataclass
class GeneratedAsset:
    """Represents a successfully generated asset."""
    asset_type: str
    filename: str
    path: str
    metadata_path: str
    preflight_status: str  # PASSED, WARNING
    confidence_score: float
    pain_ids_resolved: List[str]
    can_use: bool
    delivery_filename: str = ""


@dataclass
class FailedAsset:
    """Represents an asset that failed generation."""
    asset_type: str
    reason: str
    pain_ids_affected: List[str]
    preflight_status: str  # BLOCKED


# FASE-CAUSAL-01: Nuevo tipo para assets skippeados
@dataclass
class SkippedAsset:
    """Represents an asset that was skipped due to already existing in production."""
    asset_type: str
    reason: str  # skip_reason del SitePresenceChecker
    presence_status: str  # EXISTS, REDUNDANT, etc
    site_verified: bool
    recommendations: List[str] = field(default_factory=list)
    pain_ids_affected: List[str] = field(default_factory=list)


@dataclass
class AssetGenerationResult:
    """Resultado de la generación de assets."""
    hotel_id: str
    hotel_name: str
    generated_assets: List[GeneratedAsset]
    failed_assets: List[FailedAsset]
    coherence_report: CoherenceReport  # No default - va antes
    post_coherence_score: Optional[float] = None  # H6 FIX: score after real asset generation
    skipped_assets: List[SkippedAsset] = field(default_factory=list)  # FASE-CAUSAL-01
    output_dir: str = ""
    timestamp: str = ""
    
    @staticmethod
    def _to_relative_path(path_str: str) -> str:
        """Convert absolute path to relative path for portability.
        
        H12 FIX: Avoid hardcoded Windows paths (C:\) in output.
        M4 FIX: Normalize all paths to forward slashes for cross-platform JSON output.
        Returns relative path when possible, always with forward slashes.
        """
        if not path_str:
            return path_str
        try:
            path = Path(path_str)
            if path.is_absolute():
                # Try to make relative to current working directory
                try:
                    return str(path.relative_to(Path.cwd())).replace("\\", "/")
                except ValueError:
                    # If can't make relative to cwd, return just the last 3 parts
                    parts = path.parts
                    if len(parts) > 3:
                        return str(Path(*parts[-3:])).replace("\\", "/")
                    return path_str.replace("\\", "/")
            return path_str.replace("\\", "/")
        except Exception:
            return path_str.replace("\\", "/")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        generated_count = len(self.generated_assets)
        # Mantener estimated_count para backward compat del campo "estimated"
        estimated_count = sum(
            1 for a in self.generated_assets if a.preflight_status.upper() == "WARNING"
        )
        # PIPELINE-FIX: delivery_ready usa confidence_score, no preflight_status
        CONFIDENCE_THRESHOLD = 0.65
        ready_count = sum(
            1 for a in self.generated_assets
            if a.confidence_score >= CONFIDENCE_THRESHOLD
        )
        delivery_ready_pct = (
            (ready_count / generated_count) * 100
            if generated_count > 0
            else 0.0
        )

        return {
            "hotel_id": self.hotel_id,
            "hotel_name": self.hotel_name,
            "timestamp": self.timestamp,
            "output_dir": self._to_relative_path(self.output_dir),
            "summary": {
                "total_assets": len(self.generated_assets) + len(self.failed_assets) + len(self.skipped_assets),
                "generated": len(self.generated_assets),
                "failed": len(self.failed_assets),
                "skipped": len(self.skipped_assets),  # FASE-CAUSAL-01
                "can_use": sum(1 for a in self.generated_assets if a.can_use),
                "estimated": estimated_count,
                "delivery_ready_percentage": round(delivery_ready_pct, 2),
                # SOL-3 NOTE: site_verification_applied reflects skips at orchestrator level,
                # not checks at gate level. The gate sees the skip list but cannot re-verify
                # site presence. This is a known timing gap — see SOL-2-D3.
                "site_verification_applied": len(self.skipped_assets) > 0  # FASE-CAUSAL-01
            },
            "generated_assets": [
                {
                    "asset_type": a.asset_type,
                    "filename": a.filename,
                    "delivery_filename": a.delivery_filename or a.filename,
                    "path": self._to_relative_path(a.path),
                    "metadata_path": self._to_relative_path(a.metadata_path),
                    "preflight_status": a.preflight_status,
                    "confidence_score": round(a.confidence_score, 2),
                    "pain_ids_resolved": a.pain_ids_resolved,
                    "can_use": a.can_use
                }
                for a in self.generated_assets
            ],
            "failed_assets": [
                {
                    "asset_type": a.asset_type,
                    "reason": a.reason,
                    "pain_ids_affected": a.pain_ids_affected,
                    "preflight_status": a.preflight_status
                }
                for a in self.failed_assets
            ],
            # FASE-CAUSAL-01: Sección de assets skippeados
            "skipped_assets": [
                {
                    "asset_type": a.asset_type,
                    "reason": a.reason,
                    "presence_status": a.presence_status,
                    "site_verified": a.site_verified,
                    "recommendations": a.recommendations,
                    "pain_ids_affected": a.pain_ids_affected
                }
                for a in self.skipped_assets
            ],
            "coherence_report": self.coherence_report.to_dict(),
            # H6 FIX: both scores for transparency
            "coherence_score_pre": round(self.coherence_report.overall_score, 2),
            "coherence_score_post": round(self.post_coherence_score, 2) if self.post_coherence_score is not None else None,
            "coherence_score_final": (
                round(self.post_coherence_score, 2)
                if self.post_coherence_score is not None
                else round(self.coherence_report.overall_score, 2)
            )
        }


class CoherenceError(Exception):
    """Raised when coherence validation fails."""
    pass


class V4AssetOrchestrator:
    """
    Orquesta la generación de assets conectando:
    - Validación cruzada (v4.0)
    - Mapeo problemas → soluciones
    - Generación condicional (ConditionalGenerator)
    - Validación de coherencia
    
    FASE-CAUSAL-01: Integración de SitePresenceChecker para verificar
    sitio real ANTES de generar, evitando assets redundantes.
    """
    
    def __init__(self, output_base_dir: str = "output"):
        self.output_base_dir = Path(output_base_dir)
        self.conditional_generator = ConditionalGenerator(output_dir=str(output_base_dir))
        self.pain_mapper = PainSolutionMapper()
        self.coherence_validator = CoherenceValidator()
        self.diagnostic_linker = AssetDiagnosticLinker()
        self.content_validator = AssetContentValidator()
        self.site_checker = SitePresenceChecker()  # FASE-CAUSAL-01
        self.data_assessor = DataAssessment()  # FASE-I-01
        self.geo_flow = GeoFlow()  # FASE-6: GEO Flow
        self.pain_ledger = PainLedger()  # FASE-0B: PainLedger facade
    
    def generate_assets(
        self,
        audit_result: V4AuditResult,
        validation_summary: ValidationSummary,
        diagnostic_doc: DiagnosticDocument,
        proposal_doc: ProposalDocument,
        hotel_name: str,
        hotel_url: str,  # FASE-CAUSAL-01: Ahora se requiere URL
        site_url: Optional[str] = None,  # Alias para backward compatibility
        analytics_data: Optional[Dict[str, Any]] = None,  # ANALYTICS-FIX-01: analytics pains
        audit_report_raw: Optional[Dict[str, Any]] = None,  # FASE-0H-G8: raw audit dict for derivation
    ) -> AssetGenerationResult:
        """
        Flujo completo de generación de assets v4.0:
        
        1. Detectar problemas del audit
        2. Mapear a soluciones
        3. Validar coherencia con diagnóstico/propuesta
        4. Generar assets condicionalmente
        5. Vincular assets con problemas del diagnóstico
        6. Retornar resultado estructurado
        
        FASE-CAUSAL-01: Si site_url está disponible, se verifica el sitio real
        ANTES de generar para evitar assets redundantes.
        """
        # FASE-CAUSAL-01: Normalizar site_url
        actual_site_url = site_url or hotel_url
        
        # 1. Setup
        hotel_id = self._sanitize_hotel_id(hotel_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = self._prepare_output_directory(hotel_id, timestamp)
        
        # 2. Detectar problemas
        pains = self.pain_mapper.detect_pains(audit_result, validation_summary, analytics_data)

        # FASE-0B: Crear PainLedger y guardar como fuente de verdad de brechas
        pain_ledger_path = output_dir / "v4_audit" / "pain_ledger.json"
        pain_ledger_entries = self.pain_ledger.from_pains(pains, source_module="pain_solution_mapper")
        self.pain_ledger.save(pain_ledger_entries, pain_ledger_path)
        logger.info(f"[V4AssetOrchestrator] PainLedger saved: {len(pain_ledger_entries)} entries")

        # 3. Mapear a soluciones
        solutions = self.pain_mapper.map_to_solutions(pains)
        asset_specs = self._solutions_to_asset_specs(solutions, pains)
        
        # 4. Validar coherencia ANTES de generar
        coherence = self.coherence_validator.validate(
            diagnostic_doc, proposal_doc, asset_specs, validation_summary
        )
        
        if not coherence.is_coherent and coherence.overall_score < 0.5:
            raise CoherenceError(f"Coherencia insuficiente: {coherence.overall_score}")
        
        # 5. Extraer datos validados (FASE 12: ahora incluye hotel_data del audit)
        # FASE-0H-G8: pasa audit_report_raw para derivación de campos faltantes
        validated_data = self._extract_validated_fields(
            validation_summary, audit_result, audit_report_raw
        )

        # PATCH-3: Inyectar output_dir para que MonthlyReportGenerator encuentre asset_generation_report.json
        validated_data["hotel_data"]["output_dir"] = str(output_dir)

        # ═══════════════════════════════════════════════════════════════════
        # FASE-I-01: ENRICHMENT CON AUTONOMOUS RESEARCHER
        # Si los datos son LOW, ejecutar investigación para enriquecer
        # ═══════════════════════════════════════════════════════════════════
        assessment_result = self.data_assessor.assess(
            hotel_data=validated_data.get("hotel_data", {}),
            gbp_data=validated_data.get("gbp_data", {}),
            seo_data=validated_data.get("seo_data", {}),
            scraping_success=validated_data.get("scraping_success", False)
        )

        # Si classification es LOW, ejecutar AutonomousResearcher para enrichment
        if assessment_result.classification == DataClassification.LOW:
            logger.info(
                f"[V4AssetOrchestrator] LOW data detected - "
                f"executing AutonomousResearcher enrichment"
            )
            assessment_result = self.data_assessor.research_if_low_data(
                hotel_name=hotel_name,
                hotel_url=actual_site_url,
                assessment_result=assessment_result,
                output_dir=str(output_dir)
            )
        # ═══════════════════════════════════════════════════════════════════

        # 6. Generar assets condicionalmente
        generated = []
        failed = []
        skipped = []  # FASE-CAUSAL-01
        
        for spec in asset_specs:
            result = self._generate_with_coherence_check(
                spec, validated_data, output_dir, hotel_name, hotel_id, actual_site_url
            )
            if isinstance(result, GeneratedAsset):
                # FASE-GEO-BRIDGE: Attempt to enrich from geo_enriched/
                # FASE-A: Para hotel_schema, SIEMPRE aplicar bridge si existe schema rico
                # (incluso si confidence >= 0.7, porque conditional_generator puede haber
                # encontrado y usado el schema rico, o el basic tiene confidence alta
                # pero no tiene los 16+ campos del rico)
                geo_enriched_dir = output_dir / "geo_enriched"
                rich_schema_exists = (
                    result.asset_type == "hotel_schema" and
                    (geo_enriched_dir / "hotel_schema_rich.json").exists()
                )
                should_bridge = (
                    result.path and (
                        rich_schema_exists or
                        result.confidence_score < 0.7
                    )
                )
                if should_bridge:
                    # Read current content from disk
                    current_content = ""
                    if Path(result.path).exists():
                        try:
                            with open(result.path, 'r', encoding='utf-8') as f:
                                current_content = f.read()
                        except Exception:
                            current_content = ""

                    enriched_content, new_score = try_enrich_from_geo_enriched(
                        asset_type=result.asset_type,
                        current_content=current_content,
                        current_confidence=result.confidence_score,
                        geo_enriched_dir=geo_enriched_dir,
                        hotel_id=hotel_id
                    )

                    if new_score > result.confidence_score:
                        # Write enriched content back to disk
                        try:
                            with open(result.path, 'w', encoding='utf-8') as f:
                                f.write(enriched_content)
                            # Update metadata to reflect enrichment
                            result = GeneratedAsset(
                                asset_type=result.asset_type,
                                filename=result.filename,
                                path=result.path,
                                metadata_path=result.metadata_path,
                                preflight_status="PASSED",
                                confidence_score=new_score,
                                pain_ids_resolved=result.pain_ids_resolved,
                                can_use=True,
                                delivery_filename=result.delivery_filename
                            )
                            logger.info(
                                f"[V4AssetOrchestrator] GEO-Bridge enriched "
                                f"{result.asset_type}: {new_score:.2f}"
                            )
                        except Exception as e:
                            logger.warning(
                                f"[V4AssetOrchestrator] Failed to write enriched "
                                f"content for {result.asset_type}: {e}"
                            )

                generated.append(result)
            elif isinstance(result, SkippedAsset):  # FASE-CAUSAL-01
                skipped.append(result)
            else:
                failed.append(result)
        
        # ═══════════════════════════════════════════════════════════════════
        # H6 FIX: Post-generation coherence validation
        # Run coherence check AGAIN with real generated assets to detect
        # missing/skipped assets that the pre-generation check couldn't see.
        # This score replaces the pre-generation score in the final report.
        # ═══════════════════════════════════════════════════════════════════
        post_coherence_score = None
        post_coherence_report = None
        try:
            # Build generated_assets dict for coherence validator
            generated_assets_dict = {}
            for asset in generated:
                generated_assets_dict[asset.asset_type] = {
                    'can_use': asset.can_use,
                    'confidence_score': asset.confidence_score,
                    'filename': asset.filename
                }
            
            # Re-run coherence validation with real assets
            post_coherence_report = self.coherence_validator.validate(
                diagnostic_doc, proposal_doc, asset_specs, validation_summary,
                generated_assets=generated_assets_dict
            )
            post_coherence_score = post_coherence_report.overall_score
            logger.info(
                f"[V4AssetOrchestrator] Post-gen coherence: {post_coherence_score:.2f} "
                f"(pre-gen was {coherence.overall_score:.2f})"
            )
        except Exception as e:
            logger.warning(f"[V4AssetOrchestrator] Post-gen coherence check failed: {e}")
        
        # 7. Vincular con diagnóstico y enriquecer metadata
        links = self.diagnostic_linker.create_links(generated, diagnostic_doc)
        
        for asset in generated:
            # Get pain descriptions for this asset
            pain_descriptions = []
            for pain in pains:
                if pain.id in asset.pain_ids_resolved:
                    pain_descriptions.append(pain.description)
            
            # Get spec for this asset type
            spec = next((s for s in asset_specs if s.asset_type == asset.asset_type), None)
            
            if spec:
                metadata = self.diagnostic_linker.enrich_asset_metadata(
                    base_metadata={},
                    asset_spec=spec,
                    diagnostic_doc=diagnostic_doc,
                    coherence_report=coherence,
                    original_confidence_score=asset.confidence_score  # BUG B FIX: Pass original score
                )
                
                # Save enriched metadata - pass original asset path, not the metadata path
                # save_enriched_metadata will add _metadata.json suffix automatically
                self.diagnostic_linker.save_enriched_metadata(
                    asset.path, metadata
                )
        
        # 8. Guardar reporte de coherencia (ambos scores)
        coherence_path = output_dir / "v4_audit" / "coherence_validation.json"
        coherence.save(str(coherence_path.parent))
        
        # H6 FIX: Also save post-coherence report if available
        if post_coherence_report:
            post_coherence_path = output_dir / "v4_audit" / "coherence_validation_post_gen.json"
            # FASE-6-HOTFIX G1: pass full file path so save() writes to the correct filename
            post_coherence_report.save(str(post_coherence_path))
        
        # 9. Crear y retornar resultado
        result = AssetGenerationResult(
            hotel_id=hotel_id,
            hotel_name=hotel_name,
            generated_assets=generated,
            failed_assets=failed,
            skipped_assets=skipped,  # FASE-CAUSAL-01
            coherence_report=coherence,
            post_coherence_score=post_coherence_score,  # H6 FIX: post-gen score
            output_dir=str(output_dir),
            timestamp=datetime.now().isoformat()
        )

        # ═══════════════════════════════════════════════════════════════════
        # FASE-6: GEO FLOW - POST-PIPELINE ENRICHMENT
        # ═══════════════════════════════════════════════════════════════════
        try:
            # Build CanonicalAssessment from validated_data
            canonical_data = self._build_canonical_assessment(
                hotel_name=hotel_name,
                hotel_url=actual_site_url,
                validated_data=validated_data,
                diagnostic_doc=diagnostic_doc
            )

            commercial_diagnosis = self._build_commercial_diagnosis(
                diagnostic_doc=diagnostic_doc,
                proposal_doc=proposal_doc
            )

            logger.info("[V4AssetOrchestrator] FASE-6: Running GEO Flow...")
            geo_result = self.geo_flow.execute(
                hotel_data=canonical_data,
                commercial_diagnosis=commercial_diagnosis,
                output_dir=str(output_dir)
            )

            # Save GEO Flow result
            if geo_result:
                geo_result_path = output_dir / "v4_audit" / "geo_flow_result.json"
                import json as json_module
                with open(geo_result_path, 'w', encoding='utf-8') as f:
                    json_module.dump(geo_result.to_dict(), f, indent=2, ensure_ascii=False)
                logger.info(f"[V4AssetOrchestrator]   GEO Flow complete: {len(geo_result.assets_generated)} assets, case={geo_result.case.value}")

        except Exception as e:
            logger.warning(f"[V4AssetOrchestrator]   GEO Flow skipped due to error: {e}")

        # 10. Guardar reporte de generación
        self.save_generation_report(result)

        # FASE-0 (DT-4): Post-orchestration reconciliation
        # Unifies pain_ledger + asset_generation_report → pain_ledger_resolved.json
        reconciler = PostOrchestratorReconciler()
        pain_ledger_path = output_dir / "v4_audit" / "pain_ledger.json"
        pain_ledger_resolved_path = output_dir / "v4_audit" / "pain_ledger_resolved.json"
        asset_gen_report_path = Path(result.output_dir) / "v4_audit" / "asset_generation_report.json"

        if pain_ledger_path.exists() and asset_gen_report_path.exists():
            reconciler.reconcile(
                asset_generation_report_path=asset_gen_report_path,
                pain_ledger_path=pain_ledger_path,
                output_path=pain_ledger_resolved_path,
            )

        return result
    
    def _sanitize_hotel_id(self, hotel_name: str) -> str:
        """Convert hotel name to safe ID."""
        return hotel_name.lower().replace(" ", "_").replace("-", "_").replace(".", "")

    # ═══════════════════════════════════════════════════════════════════════
    # FASE-6: GEO FLOW HELPER METHODS
    # ═══════════════════════════════════════════════════════════════════════

    def _build_canonical_assessment(
        self,
        hotel_name: str,
        hotel_url: str,
        validated_data: Dict[str, Any],
        diagnostic_doc: DiagnosticDocument
    ) -> CanonicalAssessment:
        """
        Construye un CanonicalAssessment desde validated_data para GEO Flow.

        FASE-6: Provee los datos canónicos que geo_flow necesita para
        ejecutar diagnóstico y enrichment.
        """
        hotel_data = validated_data.get("hotel_data", {})

        # SiteMetadata
        site_metadata = SiteMetadata(
            title=hotel_data.get("name", hotel_name),
            description=hotel_data.get("description", "")
        )

        # SchemaAnalysis - extraer del audit si disponible
        schema_props = validated_data.get("schema_properties", {})
        coverage_score = 0.5  # Default
        present_fields = []
        missing_critical = []

        if schema_props:
            # Calcular coverage basado en campos presentes
            critical_fields = ["name", "description", "url", "address", "telephone"]
            present_fields = [f for f in critical_fields if schema_props.get(f)]
            coverage_score = len(present_fields) / len(critical_fields) if critical_fields else 0.5
            missing_critical = [f for f in critical_fields if not schema_props.get(f)]

        schema_analysis = SchemaAnalysis(
            schema_type="Hotel",
            coverage_score=coverage_score,
            missing_critical_fields=missing_critical,
            present_fields=present_fields
        )

        # PerformanceAnalysis - score default de 70
        performance_analysis = PerformanceAnalysis(
            performance_score=70.0,
            metrics=PerformanceMetrics()
        )

        # Construir y retornar CanonicalAssessment
        return CanonicalAssessment(
            url=hotel_url,
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis
        )

    def _build_commercial_diagnosis(
        self,
        diagnostic_doc: DiagnosticDocument,
        proposal_doc: ProposalDocument
    ) -> Dict[str, Any]:
        """
        Construye el dict de commercial_diagnosis para GEO Flow.

        FASE-6: Extrae loss_amount y problemas del DiagnosticDocument
        para sync contract analysis.
        """
        # Extraer loss_amount del financial_impact (Scenario)
        loss_amount = 0
        if diagnostic_doc and diagnostic_doc.financial_impact:
            # Scenario tiene monthly_loss_min/max
            scenario = diagnostic_doc.financial_impact
            loss_amount = scenario.monthly_loss_min  # Usar min como baseline

        # Extraer problemas detectados
        problems = []
        if diagnostic_doc and diagnostic_doc.problems:
            problems = [
                {
                    "id": getattr(p, "id", str(i)),
                    "description": getattr(p, "description", str(p)),
                    "severity": getattr(p, "severity", "UNKNOWN").value if hasattr(getattr(p, "severity", None), 'value') else "UNKNOWN"
                }
                for i, p in enumerate(diagnostic_doc.problems)
            ]

        return {
            "loss_amount": loss_amount,
            "problems": problems
        }
    
    def _prepare_output_directory(
        self, 
        hotel_id: str, 
        timestamp: str
    ) -> Path:
        """
        Crea estructura de carpetas unificada con ConditionalGenerator:
        output/{hotel_id}/
        ├── v4_audit/
        │   └── coherence_validation.json
        ├── whatsapp_button/
        ├── faq_page/
        ├── hotel_schema/
        └── financial_projection/
        
        Nota: Los assets se guardan directamente en output/{hotel_id}/{asset_type}/
        por ConditionalGenerator, no en delivery_assets/
        """
        # Usar estructura unificada: output/{hotel_id}/ (sin timestamp)
        base_dir = self.output_base_dir / hotel_id
        
        # Crear directorio v4_audit para coherencia
        (base_dir / "v4_audit").mkdir(parents=True, exist_ok=True)
        
        return base_dir
    
    def _solutions_to_asset_specs(
        self,
        solutions: List,
        pains: List[Pain]
    ) -> List[AssetSpec]:
        """Convert solutions to AssetSpec objects."""
        specs = []
        seen_types = set()
        
        for solution in solutions:
            if solution.asset_type in seen_types:
                continue
            seen_types.add(solution.asset_type)
            
            # Find the pain this solution solves
            pain = next((p for p in pains if p.id == solution.pain_id), None)
            
            specs.append(AssetSpec(
                asset_type=solution.asset_type,
                problem_solved=solution.pain_id,
                description=solution.description,
                confidence_level=pain.confidence if pain else "UNKNOWN",
                priority=solution.priority,  # FASE 2: Usar priority del mapping
                has_automatic_solution=True,
                pain_ids=[solution.pain_id],
                confidence_required=solution.confidence_required,
                can_generate=True
            ))
        
        # D4-FIX: Include assets with promised_by=["always"] or ["always_aeo"]
        from modules.asset_generation.asset_catalog import ASSET_CATALOG
        
        for asset_type, entry in ASSET_CATALOG.items():
            # Skip if already in specs
            if any(s.asset_type == asset_type for s in specs):
                continue
            
            # Check promised_by for "always" or "always_aeo"
            promised = getattr(entry, 'promised_by', []) or []
            if not any(p in promised for p in ['always', 'always_aeo']):
                continue
            
            # Get priority from entry or default
            priority = getattr(entry, 'priority', 5)
            
            specs.append(AssetSpec(
                asset_type=asset_type,
                problem_solved=f"promised_by_catalog_{asset_type}",
                description=f"Asset prometido: {asset_type}",
                confidence_level="ESTIMATED",
                priority=priority,
                has_automatic_solution=True,
                pain_ids=[],
                confidence_required=getattr(entry, 'required_confidence', 0.5),
                can_generate=True
            ))
        
        return specs
    
    def _extract_validated_fields(
        self,
        validation_summary: ValidationSummary,
        audit_result: V4AuditResult = None,  # FASE 12: audit_data_pipeline
        audit_report_raw: Optional[Dict[str, Any]] = None,  # FASE-0H-G8: raw dict for derivation
    ) -> Dict[str, Any]:
        """
        Extrae campos validados para pasar a ConditionalGenerator.
        Incluye metadata de confianza.
        
        FASE 12: Ahora incluye hotel_data del audit_result.schema.properties
        para que los assets usen datos reales del hotel.
        
        FASE-0H-G8: Si audit_report_raw está disponible, deriva campos
        faltantes (og_tags_detected, org_data, metadata) del audit.
        
        G6 WON'T FIX (FASE-6-HOTFIX): Los siguientes campos del hotel_schema
        requieren datos de onboarding real y no pueden poblarse solo con
        web scraping + GBP + benchmark:
          - amenities detallados (checkInTime, checkOutTime, roomTypes,
            starRating verificado, ADR real, ocupación real)
        El sistema funciona correctamente: genera el schema con los datos
        disponibles. El gate FASE-4 bloquea correctamente cuando el 100%
        de assets son ESTIMATED. La solución real es onboard al hotel.
        """
        validated_data = {}
        
        for field in validation_summary.fields:
            validated_data[field.field_name] = field
        
        # FIX-A3: SIEMPRE crear hotel_data (antes estaba dentro del if schema.properties)
        validated_data["hotel_data"] = {}
        
        # FASE 12: Agregar hotel_data del audit schema si properties existe
        if audit_result and audit_result.schema and audit_result.schema.properties:
            props = audit_result.schema.properties
            validated_data["hotel_data"].update({
                "name": props.get("name"),
                "description": props.get("description"),
                "telephone": props.get("telephone"),
                "url": props.get("url"),
                "address": props.get("address"),
                "image": props.get("image"),
                "price_range": props.get("price_range"),
                # GAP-3: Pass real hotel data fields from schema for llms.txt
                "email": props.get("email", ""),
                "amenities": props.get("amenityFeature", []) or props.get("amenities", []),
                "region": props.get("addressRegion", ""),
                "city": props.get("addressLocality", ""),
                "rating": props.get("rating", None),
                "review_count": props.get("reviewCount", None),
            })
        
        # FASE-2 FIX: Inyectar datos del GBP SIEMPRE (schema.properties puede estar vacío)
        if audit_result and audit_result.gbp:
            gbp = audit_result.gbp
            # Coordenadas GPS
            gbp_lat = getattr(gbp, 'lat', 0.0) or 0.0
            gbp_lng = getattr(gbp, 'lng', 0.0) or 0.0
            if 0 <= gbp_lat <= 13 and -82 <= gbp_lng <= -66:
                validated_data["hotel_data"].setdefault("latitude", gbp_lat)
                validated_data["hotel_data"].setdefault("longitude", gbp_lng)
            # Phone del GBP (clave "phone" para _generate_hotel_schema)
            gbp_phone = getattr(gbp, 'phone', None)
            if gbp_phone and not validated_data["hotel_data"].get("telephone"):
                validated_data["hotel_data"]["telephone"] = gbp_phone
                validated_data["hotel_data"]["phone"] = gbp_phone
            # Address del GBP
            gbp_address = getattr(gbp, 'address', None)
            if gbp_address and not validated_data["hotel_data"].get("address"):
                validated_data["hotel_data"]["address"] = gbp_address
            # Rating/reviews del GBP
            if not validated_data["hotel_data"].get("rating"):
                gbp_rating = getattr(gbp, 'rating', None)
                if gbp_rating:
                    validated_data["hotel_data"]["rating"] = gbp_rating
            if not validated_data["hotel_data"].get("review_count"):
                gbp_reviews = getattr(gbp, 'reviews', None)
                if gbp_reviews:
                    validated_data["hotel_data"]["review_count"] = gbp_reviews
            # Name del GBP como fallback
            if not validated_data["hotel_data"].get("name"):
                gbp_name = getattr(gbp, 'name', None)
                if gbp_name:
                    validated_data["hotel_data"]["name"] = gbp_name
            # Website del GBP
            gbp_website = getattr(gbp, 'website', None)
            if gbp_website and not validated_data["hotel_data"].get("url"):
                validated_data["hotel_data"]["url"] = gbp_website
        
        # FIX-A3: Fallback name priority: hotel_name > gbp.name > metadata.title
        # (El bloque original solo usaba metadata.title, que era vacío en amaziliahotel)
        if not validated_data["hotel_data"].get("name"):
            # Fuente 1: hotel_name del audit (siempre disponible)
            if audit_result and getattr(audit_result, 'hotel_name', None):
                validated_data["hotel_data"]["name"] = audit_result.hotel_name
            # Fuente 2: GBP name
            elif audit_result and audit_result.gbp:
                gbp_name = getattr(audit_result.gbp, 'name', None)
                if gbp_name:
                    validated_data["hotel_data"]["name"] = gbp_name
            # Fuente 3: metadata title (último recurso, puede ser vacío)
            elif audit_result and audit_result.metadata:
                title_name = getattr(audit_result.metadata, 'title', None)
                if title_name:
                    validated_data["hotel_data"]["name"] = title_name
        
        # Asegurar URL mínima en hotel_data siempre
        if not validated_data["hotel_data"].get("url") and audit_result:
            validated_data["hotel_data"]["url"] = getattr(audit_result, 'url', '')
        
        # WhatsApp conflict data for whatsapp_conflict_guide asset
        if audit_result and audit_result.validation:
            validated_data["phone_web"] = getattr(audit_result.validation, 'phone_web', None)
            validated_data["phone_gbp"] = getattr(audit_result.validation, 'phone_gbp', None)
            validated_data["whatsapp_href_number"] = getattr(audit_result.validation, 'whatsapp_href_number', None)
            # FIX-A2: Propagate phone_web to whatsapp key for whatsapp_button handler
            validated_data["whatsapp"] = validated_data.get("phone_web", "")
            # FASE-1-DATASOURCE-GAP FIX: Propagar phone_web a hotel_data si gbp.phone fue None
            if not validated_data["hotel_data"].get("telephone"):
                phone_web = validated_data.get("phone_web")
                if phone_web:
                    validated_data["hotel_data"]["telephone"] = phone_web
                    validated_data["hotel_data"]["phone"] = phone_web
        if audit_result and audit_result.gbp:
            validated_data["gbp_rating"] = getattr(audit_result.gbp, 'rating', 0.0)
            validated_data["gbp_review_count"] = getattr(audit_result.gbp, 'reviews', 0)

        # MINIMUM-DATA-GUARANTEE: Ensure country exists
        if not validated_data["hotel_data"].get("country"):
            validated_data["hotel_data"]["country"] = "CO"
        if not validated_data["hotel_data"].get("region") and audit_result:
            url = getattr(audit_result, 'url', '')
            validated_data["hotel_data"]["region"] = ""

        # DIAGNOSTIC: Log what data is available for asset generation
        logger.info(f"[V4AssetOrchestrator] validated_data['hotel_data'] completeness:")
        hd = validated_data.get("hotel_data", {})
        for key in ["name", "telephone", "phone", "address", "latitude", "longitude", "rating", "review_count", "url", "description"]:
            val = hd.get(key)
            has_it = val is not None and val != "" and val != 0
            logger.info(f"  {key}: {'PRESENT' if has_it else 'MISSING'} ({repr(val)[:50]})")

        # FASE-0H-G8: Derive missing fields from raw audit_report
        if audit_report_raw:
            try:
                from .data_derivation_layer import DataDerivationLayer, merge_derived_into_validated
                layer = DataDerivationLayer()
                derived = layer.derive(audit_report_raw)
                if derived:
                    merge_derived_into_validated(validated_data, derived)
                    logger.info(
                        f"[V4AssetOrchestrator] FASE-0H-G8: Derived {len(derived)} fields "
                        f"from audit_report: {list(derived.keys())}"
                    )
            except Exception as e:
                logger.warning(
                    f"[V4AssetOrchestrator] FASE-0H-G8: derivation skipped — {e}"
                )

        return validated_data
    
    def _generate_with_coherence_check(
        self,
        asset_spec: AssetSpec,
        validated_data: Dict[str, Any],
        output_dir: Path,
        hotel_name: str,
        hotel_id: str,
        site_url: str  # FASE-CAUSAL-01: URL para verificar sitio real
    ) -> Union[GeneratedAsset, FailedAsset, SkippedAsset]:  # FASE-CAUSAL-01: Added SkippedAsset
        """
        Genera un asset individual con validación de coherencia previa.
        
        FASE-CAUSAL-01: Ahora pasa site_url a ConditionalGenerator para verificar
        si el asset ya existe en el sitio real.
        """
        # Use ConditionalGenerator - FASE-CAUSAL-01: now passes site_url
        result = self.conditional_generator.generate(
            asset_type=asset_spec.asset_type,
            validated_data=validated_data,
            hotel_name=hotel_name,
            hotel_id=hotel_id,
            site_url=site_url  # FASE-CAUSAL-01: Verificación de sitio real
        )
        
        preflight_status = result.get("preflight_status", "BLOCKED").upper()
        result_status = result.get("status", "")
        
        # FASE-CAUSAL-01: Handle SKIPPED status from site presence check
        if result_status == "skipped":
            return SkippedAsset(
                asset_type=asset_spec.asset_type,
                reason=result.get("skip_reason", "Asset ya existe en sitio de producción"),
                presence_status=result.get("presence_status", "exists"),
                site_verified=result.get("site_verified", True),
                recommendations=result.get("recommendations", []),
                pain_ids_affected=asset_spec.pain_ids
            )
        
        if preflight_status == "BLOCKED" or result_status == "blocked":
            return FailedAsset(
                asset_type=asset_spec.asset_type,
                reason=result.get("error", "Preflight check failed"),
                pain_ids_affected=asset_spec.pain_ids,
                preflight_status="BLOCKED"
            )
        
        # FIX-B1: Handle generation errors that return status "error" without file_path
        if result_status == "error" or not result.get("success", True):
            return FailedAsset(
                asset_type=asset_spec.asset_type,
                reason=result.get("error", "Generation failed"),
                pain_ids_affected=asset_spec.pain_ids,
                preflight_status="BLOCKED"
            )
        
        # Get file paths
        file_path = result.get("file_path", "")
        metadata = result.get("metadata", {})
        
        # Validate content quality
        content_issues = []
        if file_path and Path(file_path).exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                content_result = self.content_validator.validate_file(file_path, content)
                
                if content_result.issues:
                    content_issues = [
                        f"{i.issue_type}: {i.message}" 
                        for i in content_result.issues
                    ]
                    
                    # If content is INVALID (has placeholders or critical issues), block the asset
                    if content_result.status == ContentStatus.INVALID:
                        metadata['content_validation_status'] = 'invalid'
                        metadata['content_issues'] = content_issues
                        
                        # BUG A FIX: Delete the already-written file since validation failed
                        # The file was saved by conditional_generator.generate() before we could validate
                        if file_path and Path(file_path).exists():
                            try:
                                Path(file_path).unlink()
                                # Also delete the metadata file
                                metadata_path = Path(file_path).parent / f"{Path(file_path).stem}_metadata.json"
                                if metadata_path.exists():
                                    metadata_path.unlink()
                            except Exception as delete_err:
                                metadata['cleanup_error'] = str(delete_err)
                        
                        return FailedAsset(
                            asset_type=asset_spec.asset_type,
                            reason=f"Content validation failed: {'; '.join(content_issues[:3])}",
                            pain_ids_affected=asset_spec.pain_ids,
                            preflight_status="BLOCKED"
                        )
                    
                    # If content has warnings, add to metadata
                    if content_result.status == ContentStatus.WARNING:
                        metadata['content_validation_status'] = 'warning'
                        metadata['content_issues'] = content_issues
            except Exception as e:
                metadata['content_validation_error'] = str(e)
        
        # M3 FIX: Unify can_use logic with asset_metadata.py
        # Rule: can_use = true if preflight_status != "BLOCKED"
        can_use = preflight_status != "BLOCKED"

        generated_filename = Path(file_path).name if file_path else f"{asset_spec.asset_type}_failed.html"
        delivery_filename = self._compute_delivery_filename(generated_filename)
        
        return GeneratedAsset(
            asset_type=asset_spec.asset_type,
            filename=generated_filename,
            path=file_path,
            metadata_path=str(Path(file_path).parent / f"{Path(file_path).stem}_metadata.json") if file_path else "",
            preflight_status=preflight_status,
            confidence_score=metadata.get("confidence_score", 0.0),
            pain_ids_resolved=asset_spec.pain_ids,
            can_use=can_use,
            delivery_filename=delivery_filename
        )

    @staticmethod
    def _compute_delivery_filename(filename: str) -> str:
        """Normalize generated filename for delivery-facing reports.

        Keeps traceability in metadata while removing internal warning prefixes
        from presentation fields.
        """
        for prefix in ("ESTIMATED_", "FAILED_"):
            if filename.startswith(prefix):
                return filename[len(prefix):]
        return filename
    
    def save_generation_report(
        self,
        result: AssetGenerationResult
    ) -> str:
        """
        Guarda asset_generation_report.json con el resumen completo.
        """
        report_path = Path(result.output_dir) / "v4_audit" / "asset_generation_report.json"
        
        report_data = result.to_dict()
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return str(report_path)


# Exportar clases principales
__all__ = [
    'V4AssetOrchestrator',
    'AssetGenerationResult',
    'GeneratedAsset',
    'FailedAsset',
    'CoherenceError'
]
