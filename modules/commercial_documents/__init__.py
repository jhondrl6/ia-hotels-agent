"""Commercial Documents Generator v4.0 for IA Hoteles.

This module provides document generation for commercial proposals and diagnostics
using the v4.0 confidence-based validation system.

Usage:
    from modules.commercial_documents import V4DiagnosticGenerator, V4ProposalGenerator
    
    # Generate diagnostic
    diag_gen = V4DiagnosticGenerator()
    diagnostic_path = diag_gen.generate(
        audit_result=audit_result,
        validation_summary=validation_summary,
        financial_scenarios=scenarios,
        hotel_name="Hotel Visperas",
        hotel_url="https://hotelvisperas.com",
        output_dir="output/"
    )
    
    # Generate proposal
    prop_gen = V4ProposalGenerator()
    proposal_path = prop_gen.generate(
        diagnostic_summary=diagnostic_summary,
        financial_scenarios=scenarios,
        asset_plan=asset_plan,
        hotel_name="Hotel Visperas",
        output_dir="output/"
    )
"""

from .v4_diagnostic_generator import V4DiagnosticGenerator
from .v4_proposal_generator import V4ProposalGenerator
from .coherence_validator import CoherenceValidator, CoherenceReport, CoherenceCheck
from .coherence_config import CoherenceConfig, CoherenceRule, PriceValidationRule, get_coherence_config
from .pain_solution_mapper import PainSolutionMapper, Pain, Solution
from .data_structures import (
    V4AuditResult,
    ValidationSummary,
    FinancialScenarios,
    Scenario,
    DiagnosticDocument,
    ProposalDocument,
    AssetSpec,
    ValidatedField,
    ConfidenceLevel,
)

__all__ = [
    'V4DiagnosticGenerator',
    'V4ProposalGenerator',
    'CoherenceValidator',
    'CoherenceReport',
    'CoherenceCheck',
    'CoherenceConfig',
    'CoherenceRule',
    'PriceValidationRule',
    'get_coherence_config',
    'PainSolutionMapper',
    'Pain',
    'Solution',
    # Data Structures
    'V4AuditResult',
    'ValidationSummary',
    'FinancialScenarios',
    'Scenario',
    'DiagnosticDocument',
    'ProposalDocument',
    'AssetSpec',
    'ValidatedField',
    'ConfidenceLevel',
]
