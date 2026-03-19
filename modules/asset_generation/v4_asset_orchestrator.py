"""
v4 Asset Orchestrator for IA Hoteles Agent.

Orquesta la generación de assets conectando:
- Validación cruzada (v4.0)
- Mapeo problemas → soluciones
- Generación condicional (ConditionalGenerator)
- Validación de coherencia
"""

import json
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


@dataclass
class AssetGenerationResult:
    """Resultado de la generación de assets."""
    hotel_id: str
    hotel_name: str
    generated_assets: List[GeneratedAsset]
    failed_assets: List[FailedAsset]
    coherence_report: CoherenceReport
    output_dir: str
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        generated_count = len(self.generated_assets)
        estimated_count = sum(
            1 for a in self.generated_assets if a.preflight_status.upper() == "WARNING"
        )
        delivery_ready_pct = (
            ((generated_count - estimated_count) / generated_count) * 100
            if generated_count > 0
            else 0.0
        )

        return {
            "hotel_id": self.hotel_id,
            "hotel_name": self.hotel_name,
            "timestamp": self.timestamp,
            "output_dir": self.output_dir,
            "summary": {
                "total_assets": len(self.generated_assets) + len(self.failed_assets),
                "generated": len(self.generated_assets),
                "failed": len(self.failed_assets),
                "can_use": sum(1 for a in self.generated_assets if a.can_use),
                "estimated": estimated_count,
                "delivery_ready_percentage": round(delivery_ready_pct, 2)
            },
            "generated_assets": [
                {
                    "asset_type": a.asset_type,
                    "filename": a.filename,
                    "delivery_filename": a.delivery_filename or a.filename,
                    "path": a.path,
                    "metadata_path": a.metadata_path,
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
            "coherence_report": self.coherence_report.to_dict()
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
    """
    
    def __init__(self, output_base_dir: str = "output"):
        self.output_base_dir = Path(output_base_dir)
        self.conditional_generator = ConditionalGenerator(output_dir=str(output_base_dir))
        self.pain_mapper = PainSolutionMapper()
        self.coherence_validator = CoherenceValidator()
        self.diagnostic_linker = AssetDiagnosticLinker()
        self.content_validator = AssetContentValidator()
    
    def generate_assets(
        self,
        audit_result: V4AuditResult,
        validation_summary: ValidationSummary,
        diagnostic_doc: DiagnosticDocument,
        proposal_doc: ProposalDocument,
        hotel_name: str,
        hotel_url: str
    ) -> AssetGenerationResult:
        """
        Flujo completo de generación de assets v4.0:
        
        1. Detectar problemas del audit
        2. Mapear a soluciones
        3. Validar coherencia con diagnóstico/propuesta
        4. Generar assets condicionalmente
        5. Vincular assets con problemas del diagnóstico
        6. Retornar resultado estructurado
        """
        # 1. Setup
        hotel_id = self._sanitize_hotel_id(hotel_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = self._prepare_output_directory(hotel_id, timestamp)
        
        # 2. Detectar problemas
        pains = self.pain_mapper.detect_pains(audit_result, validation_summary)
        
        # 3. Mapear a soluciones
        solutions = self.pain_mapper.map_to_solutions(pains)
        asset_specs = self._solutions_to_asset_specs(solutions, pains)
        
        # 4. Validar coherencia ANTES de generar
        coherence = self.coherence_validator.validate(
            diagnostic_doc, proposal_doc, asset_specs, validation_summary
        )
        
        if not coherence.is_coherent and coherence.overall_score < 0.5:
            raise CoherenceError(f"Coherencia insuficiente: {coherence.overall_score}")
        
        # 5. Extraer datos validados
        validated_data = self._extract_validated_fields(validation_summary)
        
        # 6. Generar assets condicionalmente
        generated = []
        failed = []
        
        for spec in asset_specs:
            result = self._generate_with_coherence_check(
                spec, validated_data, output_dir, hotel_name, hotel_id
            )
            if isinstance(result, GeneratedAsset):
                generated.append(result)
            else:
                failed.append(result)
        
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
                    coherence_report=coherence
                )
                
                # Save enriched metadata - pass original asset path, not the metadata path
                # save_enriched_metadata will add _metadata.json suffix automatically
                self.diagnostic_linker.save_enriched_metadata(
                    asset.path, metadata
                )
        
        # 8. Guardar reporte de coherencia
        coherence_path = output_dir / "v4_audit" / "coherence_validation.json"
        coherence.save(str(coherence_path.parent))
        
        # 9. Crear y retornar resultado
        result = AssetGenerationResult(
            hotel_id=hotel_id,
            hotel_name=hotel_name,
            generated_assets=generated,
            failed_assets=failed,
            coherence_report=coherence,
            output_dir=str(output_dir),
            timestamp=datetime.now().isoformat()
        )
        
        # 10. Guardar reporte de generación
        self.save_generation_report(result)
        
        return result
    
    def _sanitize_hotel_id(self, hotel_name: str) -> str:
        """Convert hotel name to safe ID."""
        return hotel_name.lower().replace(" ", "_").replace("-", "_").replace(".", "")
    
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
        
        return specs
    
    def _extract_validated_fields(
        self,
        validation_summary: ValidationSummary
    ) -> Dict[str, Any]:
        """
        Extrae campos validados para pasar a ConditionalGenerator.
        Incluye metadata de confianza.
        """
        validated_data = {}
        
        for field in validation_summary.fields:
            validated_data[field.field_name] = field
        
        return validated_data
    
    def _generate_with_coherence_check(
        self,
        asset_spec: AssetSpec,
        validated_data: Dict[str, Any],
        output_dir: Path,
        hotel_name: str,
        hotel_id: str
    ) -> Union[GeneratedAsset, FailedAsset]:
        """
        Genera un asset individual con validación de coherencia previa.
        """
        # Use ConditionalGenerator
        result = self.conditional_generator.generate(
            asset_type=asset_spec.asset_type,
            validated_data=validated_data,
            hotel_name=hotel_name,
            hotel_id=hotel_id
        )
        
        preflight_status = result.get("preflight_status", "BLOCKED").upper()
        
        if preflight_status == "BLOCKED" or result.get("status") == "blocked":
            return FailedAsset(
                asset_type=asset_spec.asset_type,
                reason=result.get("error", "Preflight check failed"),
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
        
        # Determine if asset can be used
        can_use = preflight_status == "PASSED" or (
            preflight_status == "WARNING" and asset_spec.confidence_level != "CONFLICT"
        )

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
