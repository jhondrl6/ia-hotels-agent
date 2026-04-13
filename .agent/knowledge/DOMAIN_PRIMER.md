# Domain Primer - IA Hoteles Agent CLI

> **Proposito**: Base de conocimiento comprimida del dominio "hoteleria digital".
> Consultar para entender conceptos de negocio y su mapeo a codigo.
>
> **Version del sistema**: 4.28.0 | **Codename**: 4 Pilares Alignment + Voice Readiness Proxy
> **Release date**: 2026-04-13 | **Plan Maestro**: v2.6.0
> **Agent Harness**: v3.2.0

---

## Modulos del Repositorio (auto-generado)

> 21 modulos detectados en `modules/` + 1 paquetes de nivel root. 171 archivos Python en total.

### CORE - Pipeline de diagnostico

| Modulo | Archivos | Clases/Funciones Clave |
|--------|----------|------------------------|
| **scrapers/** | 16 | BookingScraper; DriverInterface; GBPAuditor; GBPAuditorAuto; GBPRevenueLeakDetector; DriverAdapterProtocol, DriverAdapterBase, SeleniumAdapter, PlaywrightAdapter; PostsAuditResult, GBPPostsAuditor; Pl |
| **data_validation/** | 6 | ConfidenceLevel, DataSource, ValidationResult, ConfidenceTaxonomy; CrossValidator; MetadataValidator; PageSpeedResult, PageSpeedClient; SchemaType, SchemaValidationResult, RichResultsTestResult, RichR |
| **financial_engine/** | 14 | ADRSource, ADRResolutionResult, ADRResolutionWrapper; CalculationStatus, FinancialCalculationResult, FinancialCalculatorV2; RolloutMode, FinancialFeatureFlags; CalculationStep, TransparentCalculation, |
| **orchestration_v4/** | 2 | OnboardingPhase, OnboardingStatus, OnboardingState, OnboardingController; Phase1Result, Phase2Result, HotelInputs, TwoPhaseOrchestrator |
| **onboarding/** | 4 | OnboardingForm |

### ANALISIS Y AUDITORIA

| Modulo | Archivos | Clases/Funciones Clave |
|--------|----------|------------------------|
| **auditors/** | 9 | SnippetResult, AEOSnippetReport, AEOSnippetTracker; CrawlerAccessResult, AICrawlerAuditReport, AICrawlerAuditor; ContentBlock, CitabilityScore, CitabilityScorer; IAReadinessReport, IAReadinessCalculat |
| **analyzers/** | 5 | BingResult, BingProxyTester; CompetitorAnalyzer; GapAnalyzer; IATester; ROICalculator |
| **providers/** | 5 | ResearchOutput, ResearchResult, BookingScraper, AutonomousResearcher; BenchmarkDeviation, BenchmarkCrossValidator; BenchmarkResult, BenchmarkResolver; DisclaimerGenerator, IntelligentDisclaimerGenerat |

### GENERACION DE CONTENIDO Y ASSETS

| Modulo | Archivos | Clases/Funciones Clave |
|--------|----------|------------------------|
| **commercial_documents/** | 6 | CoherenceRule, PriceValidationRule, CoherenceConfig; CoherenceCheck, CoherenceReport, CoherenceValidator; ValidatedField, Conflict, ValidationSummary, Scenario; Pain, Solution, PainSolutionMapper; V4D |
| **asset_generation/** | 15 | AssetStatus, AssetCatalogEntry; ContentStatus, ContentIssue, ContentValidationResult, AssetContentValidator; AssetDiagnosticLink, AssetMetadata, AssetDiagnosticLinker; AssetStatus, AssetMetadata, Asse |
| **delivery/** | 23 | AltTextGuideGenerator; AnalyticsSetupGuideGenerator; BlogStrategyGuideGenerator; BookingBarGenerator; CertificateGenerator; ContentGenerator; DeliveryContext; DeliveryPackager; DeployInstructionsGener |
| **generators/** | 3 | OutreachGenerator; ReportDataBundle, ReportIntegrationAudit, ReportIntegrationAdapter, ReportBuilder; GeoStageResult, IAStageResult, SparkGenerator |
| **geo_enrichment/** | 8 | AssetType, AssetResponsibility, AssetResponsibilityContract; GEODashboard; GEOBand, ScoreBreakdown, GEOAssessment, GEODiagnostic; GEOEnrichmentLayer; GeoFlowResult, GeoFlow; HotelSchemaEnricher; LLMsT |

### DATOS EXTERNOS Y DEPLOY

| Modulo | Archivos | Clases/Funciones Clave |
|--------|----------|------------------------|
| **analytics/** | 5 | ConfidenceLevel, UnifiedAnalyticsData, AnalyticsAggregator; GoogleAnalyticsClient; GSCQueryData, GSCPageData, GSCReport, GoogleSearchConsoleClient; ProfoundClient; SemrushClient |
| **deployer/** | 4 | ConnectionResult, BaseConnector; FTPConnector; DeployAction, DeployPlan, DeployManager; WordPressConnector |

### QUALITY GATES

| Modulo | Archivos | Clases/Funciones Clave |
|--------|----------|------------------------|
| **quality_gates/** | 5 | CoherenceStatus, PublicationStatus, CoherenceGap, CoherenceGateResult; GateType, GateStatus, GateCheck, DomainGateResult; EthicsStatus, EthicsIssue, EthicsValidationResult, EthicsGate; GateStatus, Pub |

### UTILIDADES Y VALIDACION

| Modulo | Archivos | Clases/Funciones Clave |
|--------|----------|------------------------|
| **utils/** | 17 | BenchmarkLoader; CanonicalMetric; DataSource, DataConfidence, ConfidenceReport, ConfidenceTracker; ConfigChecker; ImpactResult, DynamicImpactReport, DynamicImpactCalculator; EnvValidator; FinancialFac |
| **monitoring/** | 2 | HealthDashboardGenerator; ExecutionMetrics, HealthMetricsCollector |
| **validation/** | 3 | ValidationResult, ContentValidator; ValidationResult, PlanValidator; ValidationResult, SecurityIssue, SecurityValidator |

### ORQUESTACION: AGENT HARNESS & PAQUETES ROOT

> Paquetes de primer nivel fuera de `modules/`. Agent Harness es el orquestador de tareas.

| Paquete | Archivos | Clases Clave |
|---------|----------|-------------|
| **agent_harness/root/** | 8 | AgentHarness, _NoColors; IA_Hoteles_MCP_Client; MemoryManager; ExecutionMetrics, Observer; RecoveryStrategy, ErrorMatch, ErrorLearner, SelfHealer; StepType, WorkflowStep, ExecutionResult, SkillMetrics |

---

## Referencias

- `docs/GUIA_TECNICA.md` - Notas tecnicas y arquitectura
- `docs/contributing/` - Procedimientos de contribucion
- `README.md` - Navegacion rapida del proyecto
- `AGENTS.md` - Contexto global del agente

---

*Auto-generado: 2026-04-13 | v4.28.0 4 Pilares Alignment + Voice Readiness Proxy*
*Regenerar con: `python scripts/doctor.py --regenerate-domain-primer`*
*NO EDITAR MANUALMENTE - Este archivo se regenera automaticamente desde los modulos del proyecto*
