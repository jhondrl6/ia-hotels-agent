# Índice de Documentación - IA Hoteles Agent CLI

**Versión:** 4.19.0
**Última actualización:** 3 Abril 2026

---

## 📚 Documentación General

| Documento | Descripción | Actualizado |
|-----------|-------------|-------------|
| `README.md` | Guía de uso general | Manual |
| `AGENTS.md` | Contexto global canónico | Manual |
| `CHANGELOG.md` | Historial de cambios | Manual |
| `VERSION.yaml` | Fuente de verdad de versiones | Manual |

---

## 📖 Guías

| Documento | Descripción | Actualizado |
|-----------|-------------|-------------|
| `docs/GUIA_TECNICA.md` | Guía técnica y arquitectura | Manual |
| `docs/CONTRIBUTING.md` | Guía de contribución | Manual |
| `docs/PRECIOS_PAQUETES.md` | Precios y paquetes comerciales | Manual |

---

## 🔧 Módulos del Sistema

### Core

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `main.py` | Punto de entrada CLI | Raíz |
| `orchestration_v4/` | Flujo dos fases | `modules/orchestration_v4/` |
| `agent_harness/` | Memoria, routing, self-healing | Raíz |

### Analytics ( medicion y auditoria )

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `analytics/` | Módulo de analytics | `modules/` |
| `google_analytics_client.py` | Cliente GA4 multi-hotel | `modules/analytics/` |
| `profound_client.py` | Cliente Profound SEO | `modules/analytics/` |
| `semrush_client.py` | Cliente Semrush | `modules/analytics/` |
| `auditors/` |APIs externas de auditoria | `modules/auditors/` |
| `v4_comprehensive_auditor.py` | Auditor comprehensivo V4 | `modules/auditors/` |
| `pagespeed_auditor_v2.py` | PageSpeed Insights | `modules/auditors/` |

### Scanners y Scrapers

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `scrapers/` | Recolectores de datos | `modules/scrapers/` |
| `gbp_auditor.py` | Google Business Profile | `modules/scrapers/` |
| `booking_scraper.py` | Booking.com | `modules/scrapers/` |
| `web_scraper.py` | Scraping general | `modules/scrapers/` |
| `serpapi_client.py` | SERP API | `modules/scrapers/` |
| `google_places_client.py` | Google Places | `modules/scrapers/` |
| `scraper_fallback.py` | Fallback scraping | `modules/scrapers/` |

### Validación

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `data_validation/` | Validación cruzada | `modules/data_validation/` |
| `validation/` | Validación adicional | `modules/validation/` |
| `evidence_ledger.py` | Almacén de evidencia | `modules/data_validation/` |
| `contradiction_engine.py` | Detección de conflictos | `modules/data_validation/` |
| `consistency_checker.py` | Validación inter-documento | `modules/data_validation/` |
| `metadata_validator.py` | Detección CMS defaults | `modules/data_validation/` |
| `schema_validator_v2.py` | Validador de schema | `modules/data_validation/` |

### Geo-Enrichment

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `geo_enrichment/` | Enriquecimiento geográfico | `modules/geo_enrichment/` |
| `geo_diagnostic.py` | Diagnóstico geo | `modules/geo_enrichment/` |
| `geo_enrichment_layer.py` | Capa de enrichment | `modules/geo_enrichment/` |
| `geo_flow.py` | Flujo geo | `modules/geo_enrichment/` |
| `geo_dashboard.py` | Dashboard geo | `modules/geo_enrichment/` |
| `asset_responsibility_contract.py` | Contrato de assets | `modules/geo_enrichment/` |
| `llms_txt_generator.py` | Generador llms.txt | `modules/geo_enrichment/` |
| `sync_contract.py` | Sync de contratos | `modules/geo_enrichment/` |

### Comercial y Documentos

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `commercial_documents/` | Documentos comerciales | `modules/commercial_documents/` |
| `v4_diagnostic_generator.py` | Generador diagnóstico V4 | `modules/commercial_documents/` |
| `v4_proposal_generator.py` | Generador propuesta V4 | `modules/commercial_documents/` |
| `composer.py` | Generación determinística | `modules/commercial_documents/` |
| `coherence_validator.py` | Validador de coherencia | `modules/commercial_documents/` |
| `pain_solution_mapper.py` | Mapeo problemas→assets | `modules/commercial_documents/` |

### Assets

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `asset_generation/` | Generación condicional | `modules/asset_generation/` |
| `asset_catalog.py` | Catálogo centralizado | `modules/asset_generation/` |
| `asset_diagnostic_linker.py` | Link assets a diagnóstico | `modules/asset_generation/` |
| `conditional_generator.py` | Generador condicional | `modules/asset_generation/` |
| `preflight_checks.py` | Gates de calidad | `modules/asset_generation/` |
| `v4_asset_orchestrator.py` | Orchestrator de assets V4 | `modules/asset_generation/` |

### Quality Gates

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `quality_gates/` | Gates de publicación | `modules/quality_gates/` |
| `domain_gates.py` | Gates por dominio | `modules/quality_gates/` |
| `coherence_gate.py` | Gate de coherencia | `modules/quality_gates/` |
| `publication_gates.py` | Gates de publicación | `modules/quality_gates/` |

### Financiera

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `financial_engine/` | Motor financiero | `modules/financial_engine/` |
| `calculator_v2.py` | Calculadora v2 | `modules/financial_engine/` |
| `no_defaults_validator.py` | Validación sin defaults | `modules/financial_engine/` |

### Analyzers y Monitoreo

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `analyzers/` | Analizadores especializados | `modules/analyzers/` |
| `monitoring/` | Monitoreo del sistema | `modules/monitoring/` |

### Deployment y Delivery

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `deployer/` | Despliegue de assets | `modules/deployer/` |
| `delivery/` | Entrega de documentos | `modules/delivery/` |

### Observabilidad

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `observability/` | Dashboard y calibración | `observability/` |
| `dashboard.py` | Métricas | `observability/` |
| `calibration.py` | Calibración de umbrales | `observability/` |

### Data Models

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `data_models/` | Modelos Pydantic | `data_models/` |
| `canonical_assessment.py` | Assessment unificado | `data_models/` |
| `claim.py` | Claims con evidencia | `data_models/` |
| `evidence.py` | Evidencia con hash | `data_models/` |
| `aeo_kpis.py` | KPIs AEO + GA4 | `data_models/` |
| `analytics_status.py` | Status analytics | `data_models/` |
| `assessment.py` | Assessment v4 | `data_models/` |

### Enums

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `enums/` | Enumeraciones | `enums/` |
| `severity.py` | Niveles de severidad | `enums/` |
| `confidence_level.py` | Niveles de confianza | `enums/` |
| `types.py` | Tipos generales | `enums/` |

### Providers y Utils

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `providers/` | Proveedores externos | `modules/providers/` |
| `utils/` | Utilidades | `modules/utils/` |

### Onboarding

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `onboarding/` | Flujo de onboarding | `modules/onboarding/` |

### Agent Ecosystem (Meta-Skills y Workflows)

| Componente | Descripción | Ubicación |
|------------|-------------|-----------|
| `.agents/workflows/` | Skills y workflows del agente | Directorio raiz |
| `.agent/` | Memoria, logs, conocimiento runtime | Directorio raiz |
| `.agent/CONVENTION.md` | Contrato de arquitectura del ecosistema | `.agent/` |
| `.agent/SYSTEM_STATUS.md` | Dashboard auto-regenerable | `.agent/` |
| `.agent/knowledge/DOMAIN_PRIMER.md` | Contexto dominio hotelero | `.agent/knowledge/` |
| `.agent/memory/` | Sesiones, errores, estado actual | `.agent/memory/` |
| `.agent/shadow_logs/` | Logs de comparacion de pricing | `.agent/shadow_logs/` |
| `.agents/workflows/README.md` | Index de skills con triggers | `.agents/workflows/` |
| `.agents/workflows/templates/` | Templates de prompts y configs | `.agents/workflows/templates/` |
| `.agent/workflows` | Symlink -> `.agents/workflows` | `.agent/` |

### Scripts de Diagnostico | Validacion Nuevo en v4.19.0

| Script | Descripción | Ubicación |
|--------|-------------|-----------|
| `scripts/doctor.py` | Punto de entrada diagnostico ecosistema | `scripts/` |
| `scripts/validate_agent_ecosystem.py` | 8 checks automaticos de agents | `scripts/` |

---

## 🧪 Testing

| Directorio | Descripción |
|------------|-------------|
| `tests/` | Suite completa de tests |
| `tests/regression/` | Suite de regresión permanente |
| `tests/data_validation/` | Tests de validación |
| `tests/financial_engine/` | Tests financieros |
| `tests/asset_generation/` | Tests de assets |
| `tests/commercial_documents/` | Tests de documentos |

---

## 📜 Scripts

| Script | Descripción |
|--------|-------------|
| `scripts/doctor.py` | **Diagnostico ecosistema de agentes (v4.19.0)** |
| `scripts/validate_agent_ecosystem.py` | **8 checks automatizados de agentes (v4.19.0)** |
| `scripts/sync_versions.py` | Sincroniza versiones entre archivos |
| `scripts/run_all_validations.py` | Validaciones completas |
| `scripts/validate_context_integrity.py` | Valida referencias |
| `scripts/validate_structure.py` | Valida estructura del proyecto |
| `scripts/validate.py` | Validador general |
| `scripts/structure_guard.py` | Guardia de estructura |
| `scripts/generate_system_status.py` | Genera status del sistema |
| `scripts/cleanup_sessions.py` | Limpia sesiones |
| `scripts/cleanup_workdirs.py` | Limpia directorios de trabajo |
| `scripts/normalize_cache_filenames.py` | Normaliza nombres de cache |
| `scripts/prune_outputs.py` | poda outputs |
| `scripts/fill_upgrade_proposal.py` | Propuesta de upgrade |
| `scripts/sync_conductor_spec.py` | Sincroniza spec del conductor |
| `scripts/audit_check.py` | Check de auditoría |
| `scripts/gen_report.py` | Genera reportes |
| `scripts/log_phase_completion.py` | Log de completitud de fase |
| `scripts/config_checker.py` | Verificador de configuración |
| `scripts/version_consistency_checker.py` | Verifica consistencia de versiones |

---

## 🔗 Referencias

- **Versión actual:** `VERSION.yaml`
- **Contexto global:** `AGENTS.md`
- **Contribución:** `docs/CONTRIBUTING.md`
- **Changelog:** `CHANGELOG.md`
- **Glosario dominio:** `.agent/knowledge/DOMAIN_PRIMER.md`
