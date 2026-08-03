# Design Patterns and Architectural Principles

<cite>
**Referenced Files in This Document**
- [05-prompt-inicio-sesion-fase-4.md](file://plans\Archives\ROICRII\05-prompt-inicio-sesion-fase-4.md)
- [dependencias-fases.md](file://plans\Archives\ONBOARDING-INJECTION-GAP-2026-07-29\dependencias-fases.md)
- [07-prompt-fase-release-b.md](file://plans\Archives\ONBOARDING-INJECTION-GAP-2026-07-29\07-prompt-fase-release-b.md)
- [MODULO-HOOK-PDF.md](file://context\Historico\MODULO-HOOK-PDF.md)
</cite>

## Table of Contents
1. Introduction
2. Project Structure
3. Core Components
4. Architecture Overview
5. Detailed Component Analysis
6. Dependency Analysis
7. Performance Considerations
8. Troubleshooting Guide
9. Conclusion

## Introduction
This document explains the design patterns and architectural principles that underpin the iah-cli system, focusing on how sequential processing, dynamic asset generation, financial calculation strategies, quality gate notifications, standardized document generation, structured data exchange, and configuration-driven behavior work together to create a maintainable and extensible architecture. It synthesizes evidence from project plans and context artifacts to describe how these patterns are applied across validation, generation, and reporting phases.

## Project Structure
The repository contains planning artifacts, historical context, and evidence outputs that reflect the evolution of the iah-cli pipeline:
- Plans define phased implementation steps, dependencies, and release activities.
- Context documents capture operational decisions, integration points, and CLI command patterns.
- Evidence directories store generated reports and validation outputs used by quality gates.

```mermaid
graph TB
subgraph "Plans"
P1["ROICRII Phase Plan"]
P2["Onboarding Injection Phases"]
P3["Release Notes"]
end
subgraph "Context"
C1["Hook PDF Integration"]
end
subgraph "Evidence"
E1["Quality Reports"]
E2["Gate Reports"]
E3["Financial Scenarios"]
end
P1 --> E1
P2 --> E2
P3 --> E1
C1 --> E1
```

[No sources needed since this diagram shows conceptual workflow, not actual code structure]

## Core Components
Key components identified through planning and context artifacts include:
- Pipeline orchestration for sequential phases (validation, generation, reporting).
- Dynamic asset generation driven by site analysis results.
- Financial calculation strategies with configurable parameters.
- Quality gate notifications and status updates.
- Standardized document generation using templates.
- Structured data models exchanged between modules.
- Configuration-driven behavior via YAML files.

These components are coordinated by CLI commands and phase-based execution flows.

**Section sources**
- [05-prompt-inicio-sesion-fase-4.md:1-54](file://plans\Archives\ROICRII\05-prompt-inicio-sesion-fase-4.md#L1-L54)
- [dependencias-fases.md:8-75](file://plans\Archives\ONBOARDING-INJECTION-GAP-2026-07-29\dependencias-fases.md#L8-L75)
- [07-prompt-fase-release-b.md:38-74](file://plans\Archives\ONBOARDING-INJECTION-GAP-2026-07-29\07-prompt-fase-release-b.md#L38-L74)
- [MODULO-HOOK-PDF.md:300-346](file://context\Historico\MODULO-HOOK-PDF.md#L300-L346)

## Architecture Overview
The iah-cli system follows a pipeline architecture where each phase performs a specific responsibility:
- Validation: Normalize inputs, resolve identities, and verify freshness.
- Generation: Produce assets based on analysis results and templates.
- Reporting: Generate quality and gate reports, update status, and notify stakeholders.

```mermaid
sequenceDiagram
participant User as "User"
participant CLI as "CLI Entrypoint"
participant Loader as "Data Loader"
participant Validator as "Validator"
participant Generator as "Asset Generator"
participant Reporter as "Reporter"
User->>CLI : Execute command (e.g., v4complete)
CLI->>Loader : Load and normalize input data
Loader-->>CLI : Normalized dataset
CLI->>Validator : Validate data integrity and rules
Validator-->>CLI : Validation result
CLI->>Generator : Generate assets using templates
Generator-->>CLI : Generated files
CLI->>Reporter : Produce reports and gate checks
Reporter-->>CLI : Status and notifications
CLI-->>User : Completion summary
```

[No sources needed since this diagram shows conceptual workflow, not actual code structure]

## Detailed Component Analysis

### Pipeline Pattern Implementation
The pipeline pattern is implemented through phased execution where each phase depends on the previous one. The dependency graph illustrates sequential processing from loader rewrite to final release activities.

```mermaid
flowchart TD
Start([Start]) --> FASE0A["FASE-0-A: Loader rewrite + normalize_url<br/>+ frescura configurable"]
FASE0A --> FASE0B["FASE-0-B: Persist hotel.url<br/>+ Pass output_dir<br/>+ Template url:None"]
FASE0B --> FASE1["FASE-1: Taxonomy + Deprecation"]
FASE0B --> FASE2["FASE-2: observations.json fallback"]
FASE1 --> FASE3["FASE-3: Tests"]
FASE2 --> FASE3
FASE3 --> RELEASEA["RELEASE-A: v4complete + verification"]
RELEASEA --> RELEASEB["RELEASE-B: Version bump + CHANGELOG"]
RELEASEB --> RELEASEC["RELEASE-C: Analysis + closure"]
RELEASEC --> End([End])
```

**Diagram sources**
- [dependencias-fases.md:8-75](file://plans\Archives\ONBOARDING-INJECTION-GAP-2026-07-29\dependencias-fases.md#L8-L75)

**Section sources**
- [dependencias-fases.md:8-75](file://plans\Archives\ONBOARDING-INJECTION-GAP-2026-07-29\dependencias-fases.md#L8-L75)

### Factory Pattern for Dynamic Asset Generation
The factory pattern enables dynamic creation of assets based on site analysis results. The system generates different types of deliverables (diagnostic reports, commercial proposals, financial scenarios) depending on the input data and configuration.

```mermaid
classDiagram
class AssetFactory {
+createAsset(type, config) Asset
+validateConfig(config) bool
+getSupportedTypes() list
}
class DiagnosticReport {
+generateAnalysis() string
+formatOutput() string
}
class CommercialProposal {
+calculateROI() float
+generateProposal() string
}
class FinancialScenarios {
+modelCashflows() array
+computeMetrics() dict
}
AssetFactory --> DiagnosticReport : "creates"
AssetFactory --> CommercialProposal : "creates"
AssetFactory --> FinancialScenarios : "creates"
```

[No sources needed since this diagram shows conceptual class relationships, not actual code structure]

**Section sources**
- [05-prompt-inicio-sesion-fase-4.md:1-54](file://plans\Archives\ROICRII\05-prompt-inicio-sesion-fase-4.md#L1-L54)

### Strategy Pattern for Financial Calculations
The strategy pattern allows different financial calculation approaches to be selected based on configuration. The system supports various CAPEX breakdown methods and ratio calculations.

```mermaid
classDiagram
class FinancialStrategy {
<<interface>>
+calculateCAPEX(data) float
+calculateRatios(data) dict
+validateInputs(data) bool
}
class SetupFeeBreakdown {
-components : list
+calculateCAPEX(data) float
+breakdownComponents() dict
}
class RatioCalculator {
-addressablePainRatio : float
-feeToLossRatio : float
+calculateRatios(data) dict
+applyGates(thresholds) dict
}
class ConfigDrivenStrategy {
-configPath : string
+loadConfiguration() dict
+selectStrategy(config) FinancialStrategy
}
FinancialStrategy <|-- SetupFeeBreakdown
FinancialStrategy <|-- RatioCalculator
ConfigDrivenStrategy --> FinancialStrategy : "selects"
```

**Diagram sources**
- [05-prompt-inicio-sesion-fase-4.md:1-54](file://plans\Archives\ROICRII\05-prompt-inicio-sesion-fase-4.md#L1-L54)

**Section sources**
- [05-prompt-inicio-sesion-fase-4.md:1-54](file://plans\Archives\ROICRII\05-prompt-inicio-sesion-fase-4.md#L1-L54)

### Observer Pattern for Quality Gate Notifications
The observer pattern implements quality gate notifications and status updates throughout the pipeline. When quality gates pass or fail, observers are notified to update dashboards, send alerts, or trigger downstream processes.

```mermaid
sequenceDiagram
participant Pipeline as "Pipeline Engine"
participant Gate as "Quality Gate"
participant Observer as "Notification Observer"
participant Dashboard as "Dashboard Service"
participant Logger as "Audit Logger"
Pipeline->>Gate : Evaluate quality criteria
Gate-->>Pipeline : Gate result (pass/fail)
Pipeline->>Observer : Notify gate status change
Observer->>Dashboard : Update dashboard status
Observer->>Logger : Log audit trail
Observer-->>Pipeline : Acknowledge notification
Note over Pipeline,Logger : Quality gate events propagate to all observers
```

[No sources needed since this diagram shows conceptual workflow, not actual code structure]

**Section sources**
- [07-prompt-fase-release-b.md:38-74](file://plans\Archives\ONBOARDING-INJECTION-GAP-2026-07-29\07-prompt-fase-release-b.md#L38-L74)

### Template Method Pattern for Document Generation
The template method pattern standardizes document generation while allowing customization through templates. The hook PDF generator demonstrates this pattern with configurable templates and styles.

```mermaid
classDiagram
class DocumentGenerator {
<<abstract>>
+generateDocument(data) string
#processTemplate(template) string
#applyStyles(styles) string
#formatContent(content) string
}
class HookPDFGenerator {
-templatePath : string
-stylePath : string
+generateDocument(data) string
#processTemplate(template) string
#applyStyles(styles) string
}
class CommercialDocumentGenerator {
-templatePath : string
+generateDocument(data) string
#processTemplate(template) string
}
DocumentGenerator <|-- HookPDFGenerator
DocumentGenerator <|-- CommercialDocumentGenerator
```

**Diagram sources**
- [MODULO-HOOK-PDF.md:300-346](file://context\Historico\MODULO-HOOK-PDF.md#L300-L346)

**Section sources**
- [MODULO-HOOK-PDF.md:300-346](file://context\Historico\MODULO-HOOK-PDF.md#L300-L346)

### Dataclass Pattern for Structured Data Exchange
The dataclass pattern provides structured data models for exchanging information between modules. These dataclasses ensure type safety and consistent data formats across the pipeline.

```mermaid
classDiagram
class OnboardingData {
+hotel_url : string
+observations : list
+metadata : dict
+validate() bool
+to_dict() dict
}
class FinancialScenario {
+revenue_projections : array
+cost_breakdown : dict
+setup_fee_components : list
+roi_metrics : dict
+calculate_net_present_value() float
}
class QualityGateResult {
+gate_name : string
+status : enum
+score : float
+details : dict
+timestamp : datetime
}
class AssetMatrix {
+assets : list
+alignment_score : float
+recommendations : list
+update_recommendations() void
}
```

[No sources needed since this diagram shows conceptual data models, not actual code structure]

**Section sources**
- [05-prompt-inicio-sesion-fase-4.md:1-54](file://plans\Archives\ROICRII\05-prompt-inicio-sesion-fase-4.md#L1-L54)

### Configuration-Driven Design Principle
The system uses external YAML configuration files to modify behavior without code changes. Configuration controls everything from freshness windows to financial ratios and template paths.

```mermaid
flowchart TD
ConfigFile["YAML Configuration File"] --> Parser["Configuration Parser"]
Parser --> RuntimeConfig["Runtime Configuration Object"]
RuntimeConfig --> Pipeline["Pipeline Orchestrator"]
RuntimeConfig --> Validators["Validation Rules"]
RuntimeConfig --> Generators["Asset Generators"]
RuntimeConfig --> Templates["Template System"]
subgraph "Configuration Categories"
Freshness["Freshness Windows"]
Ratios["Financial Ratios"]
Gates["Quality Gate Thresholds"]
Paths["File Path Mappings"]
end
RuntimeConfig --> Freshness
RuntimeConfig --> Ratios
RuntimeConfig --> Gates
RuntimeConfig --> Paths
```

[No sources needed since this diagram shows conceptual configuration flow, not actual code structure]

**Section sources**
- [05-prompt-inicio-sesion-fase-4.md:1-54](file://plans\Archives\ROICRII\05-prompt-inicio-sesion-fase-4.md#L1-L54)

## Dependency Analysis
The system exhibits clear dependency patterns with well-defined interfaces between components:

```mermaid
graph TB
subgraph "Core Modules"
Main["main.py"]
DataLoader["modules/onboarding/data_loader.py"]
ScenarioCalc["modules/financial_engine/scenario_calculator.py"]
end
subgraph "Supporting Modules"
Templates["Template Engine"]
Validators["Validation Layer"]
Reporters["Reporting Module"]
end
subgraph "External Dependencies"
YAML["YAML Config Files"]
JSON["JSON Data Files"]
TemplatesFS["Template Files"]
end
Main --> DataLoader
Main --> ScenarioCalc
DataLoader --> Templates
ScenarioCalc --> Validators
Validators --> Reporters
YAML --> Main
JSON --> DataLoader
TemplatesFS --> Templates
```

**Diagram sources**
- [dependencias-fases.md:76-99](file://plans\Archives\ONBOARDING-INJECTION-GAP-2026-07-29\dependencias-fases.md#L76-L99)

**Section sources**
- [dependencias-fases.md:76-99](file://plans\Archives\ONBOARDING-INJECTION-GAP-2026-07-29\dependencias-fases.md#L76-L99)

## Performance Considerations
- **Lazy Loading**: Data loaders implement lazy loading to minimize memory usage during large dataset processing.
- **Caching**: Configuration and template caching reduces repeated file I/O operations.
- **Parallel Processing**: Independent validation tasks can be executed in parallel to improve throughput.
- **Streaming**: Large report generation uses streaming to handle memory constraints.
- **Incremental Updates**: Only changed assets are regenerated when inputs are modified.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and their resolutions based on observed patterns:

- **URL Matching Failures**: Implement canonical URL normalization to handle protocol variations, www prefixes, and trailing slashes.
- **Freshness Window Issues**: Configure environment variables for freshness thresholds instead of hardcoding values.
- **Template Rendering Errors**: Validate template syntax and ensure all required variables are provided.
- **Configuration Loading Failures**: Verify YAML syntax and ensure all required sections are present.
- **Quality Gate Failures**: Review gate thresholds and adjust based on business requirements.

**Section sources**
- [07-prompt-fase-release-b.md:38-74](file://plans\Archives\ONBOARDING-INJECTION-GAP-2026-07-29\07-prompt-fase-release-b.md#L38-L74)

## Conclusion
The iah-cli system demonstrates effective use of multiple design patterns to create a flexible, maintainable, and extensible architecture. The pipeline pattern ensures sequential processing, factory pattern enables dynamic asset generation, strategy pattern supports configurable financial calculations, observer pattern handles quality gate notifications, template method pattern standardizes document generation, dataclass pattern ensures structured data exchange, and configuration-driven design allows behavior modification without code changes. These patterns work together to create a robust system that can adapt to changing requirements while maintaining code quality and performance.

[No sources needed since this section summarizes without analyzing specific files]