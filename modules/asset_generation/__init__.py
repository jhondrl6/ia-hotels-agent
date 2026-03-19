"""Asset Generation for IA Hoteles Agent v4.0.

Generates assets conditionally with quality gates and metadata.
"""

from .preflight_checks import (
    PreflightStatus,
    PreflightCheck,
    PreflightReport,
    PreflightChecker,
)

from .asset_metadata import (
    AssetMetadata,
    AssetMetadataEnforcer,
    AssetStatus,
)

from .conditional_generator import (
    ConditionalGenerator,
)

from .v4_asset_orchestrator import (
    V4AssetOrchestrator,
    AssetGenerationResult,
    GeneratedAsset,
    FailedAsset,
    CoherenceError,
)

from .asset_diagnostic_linker import (
    AssetDiagnosticLinker,
    AssetDiagnosticLink,
    AssetMetadata,
)

__all__ = [
    # Preflight Checks
    "PreflightStatus",
    "PreflightCheck",
    "PreflightReport",
    "PreflightChecker",
    # Asset Metadata
    "AssetMetadata",
    "AssetMetadataEnforcer",
    "AssetStatus",
    # Conditional Generator
    "ConditionalGenerator",
    # v4 Asset Orchestrator
    "V4AssetOrchestrator",
    "AssetGenerationResult",
    "GeneratedAsset",
    "FailedAsset",
    "CoherenceError",
    # Asset Diagnostic Linker
    "AssetDiagnosticLinker",
    "AssetDiagnosticLink",
]
