# Indice de Documentacion - IA Hoteles Agent v4.8.0

**Ultima actualizacion:** 23 Marzo 2026

Guia rapida para encontrar la informacion que necesitas tras la actualizacion Financial Centralization & ChatGPT Alternatives.

---

## Busco Por Tipo de Usuario

### Consultor / Agencia (Venta)

**Quiero...**

| Necesidad                                      | Documento                                                                             |
|------------------------------------------------|---------------------------------------------------------------------------------------|
| Entender flujo de venta (Spark->Piloto->Pro AEO) | [README.md](README.md) - Secciones principales                                        |
| Ver precios y ROI de cada paquete (v2.6)       | [docs/PRECIOS_PAQUETES.md](docs/PRECIOS_PAQUETES.md)                                  |
| Validar Veracidad de un Diagnostico            | [docs/GUIA_TECNICA.md](docs/GUIA_TECNICA.md) - Protocolo de Verdad 4.0               |
| Aprender con caso real (Hotel Visperas)        | [output/clientes_no_borrar/hotel_visperas/CASO_ESTUDIO.md](output/clientes_no_borrar/hotel_visperas/CASO_ESTUDIO.md) |

### Desarrollador / Tecnico

**Quiero...**

| Necesidad                                            | Documento                                                               |
|------------------------------------------------------|-------------------------------------------------------------------------|
| Entender arquitectura del proyecto                   | [docs/GUIA_TECNICA.md](docs/GUIA_TECNICA.md)                           |
| Protocolo de Verdad 4.0 (Triangulacion)              | [docs/GUIA_TECNICA.md](docs/GUIA_TECNICA.md)                           |
| Nuevos modulos v3.6 (confidence_tracker, dynamic_impact) | [docs/GUIA_TECNICA.md](docs/GUIA_TECNICA.md)                           |
| Orquestacion Agentica (Task-Based)                   | [docs/GUIA_TECNICA.md](docs/GUIA_TECNICA.md)                           |
| Meta-Skills y Enrutamiento Semantico                 | [.agents/workflows/README.md](.agents/workflows/README.md)             |
| Stage Handlers (v4)                                   | [modules/orchestration_v4/two_phase_flow.py](modules/orchestration_v4/two_phase_flow.py) |
| Agent Harness (Core Execution 3.3)                   | [agent_harness/core.py](agent_harness/core.py)                         |
| Knowledge Graph (Verified Profiles)                  | [data/knowledge/hotels/](data/knowledge/hotels/)                       |
| Ver estado de features (implementado vs planificado) | [ROADMAP.md](ROADMAP.md)                                               |

---

## Sistema de Contexto y Mantenimiento (NUEVO v3.6)

### Gobernanza de Contexto y Fuentes Primarias

| Archivo | Proposito |
|---------|-----------|
| [VERSION.yaml](VERSION.yaml) | Version oficial del proyecto (unica fuente de verdad) |
| [AGENTS.md](AGENTS.md) | Contexto global canónico humano-curado |
| [.cursorrules](.cursorrules) | Puente de compatibilidad para tooling legacy |
| [SYSTEM_STATUS.md](.agent/SYSTEM_STATUS.md) | Dashboard de estado del sistema (auto-generado) |
| [DOMAIN_PRIMER.md](.agent/knowledge/DOMAIN_PRIMER.md) | Base de conocimiento del dominio (auto-generado desde codigo) |

### Scripts de Mantenimiento

| Script | Uso |
|--------|-----|
| scripts/sync_versions.py | Sincroniza versiones desde VERSION.yaml |
| scripts/generate_domain_primer.py | Regenera DOMAIN_PRIMER desde módulos activos |
| scripts/validate_context_integrity.py | Valida referencias cruzadas del sistema |
| scripts/cleanup_sessions.py | Limpia sesiones antiguas de memoria |
| scripts/normalize_cache_filenames.py | Normaliza nombres de archivos de cache |
| scripts/generate_system_status.py | Genera dashboard de estado |
| scripts/run_all_validations.py | Orquestador de validaciones (sin Gemini CLI) |
| scripts/validate.py | CLI para validaciones nativas |

### Guia de Contribucion

| Documento | Proposito |
|-----------|-----------|
| [CONTRIBUTING.md](docs/CONTRIBUTING.md) | Reglas obligatorias para mantenimiento de documentacion contextual |
| [AGENTS.md](AGENTS.md) | Politica y contexto global del agente (fuente primaria) |
| [error_catalog.json](.agent/memory/error_catalog.json) | Catalogo de errores para self-healing |

---

## Busco Por Tema

### Plan Maestro y Benchmarking (Core) - v2.6.0

| Tema | Ubicacion |
|------|-----------|
| Benchmarking Nacional 2026 | [data/benchmarks/Benchmarking.md](data/benchmarks/Benchmarking.md) |
| Plan Maestro v2.6.0 (Reglas 2026) | [data/benchmarks/Plan_maestro_v2_5.md](data/benchmarks/Plan_maestro_v2_5.md) |
| JSON Canonico (Umbrales v2.6) | [data/benchmarks/plan_maestro_data.json](data/benchmarks/plan_maestro_data.json) |

### Nuevos Modulos v3.6 (Dynamic Impact)

| Modulo | Funcion |
|--------|---------|
| modules/utils/confidence_tracker.py | Tracking de provenance de datos (hotel vs benchmark) |
| modules/utils/dynamic_impact.py | Calculo dinamico de impacto financiero |

### Nuevos Módulos v3.7 (Estimation Elimination)

| Modulo | Funcion |
|--------|---------|
| modules/onboarding/forms.py | Formulario interactivo de captura de datos operativos |
| modules/onboarding/validators.py | Validadores de campos (habitaciones, reservas, etc.) |
| modules/onboarding/data_loader.py | Carga de datos desde YAML/JSON |
| modules/scrapers/gbp_auditor_playwright.py | Auditor GBP con Playwright (fallback automático) |
| modules/scrapers/gbp_photo_auditor_playwright.py | Auditor de fotos con Playwright |
| modules/scrapers/gbp_factory.py | Factory con fallback Selenium→Playwright |
| modules/scrapers/google_places_client.py | Cliente de Places API con geo_score real |
| modules/analyzers/competitor_analyzer.py | Analyzer integrado con Places API |
| modules/utils/horarios_detector_playwright.py | Detector de horarios con Playwright (módulo independiente) |

### Nuevos Módulos v3.8 (Validation & Multi-Driver)

| Modulo | Funcion |
|--------|---------|
| modules/validation/plan_validator.py | Validador de coherencia contra Plan Maestro |
| modules/validation/content_validator.py | Validador de estándares de contenido GEO/AEO |
| modules/validation/security_validator.py | Detector de secrets hardcoded |
| modules/scrapers/drivers/driver_interface.py | Interfaz abstracta para drivers |
| modules/scrapers/drivers/selenium_driver.py | Wrapper Selenium con anti-detección |
| modules/scrapers/drivers/playwright_driver.py | Wrapper Playwright con stealth |
| modules/scrapers/drivers/humanized.py | Delays y comportamiento humanizado |

### Nuevos Módulos v3.9 (Financial Centralization & ChatGPT Alternatives)

| Modulo | Funcion |
|--------|---------|
| modules/utils/financial_factors.py | Centralización de factores financieros desde plan_maestro_data.json |
| modules/analyzers/bing_proxy_tester.py | Alternativa a ChatGPT API usando Bing como proxy |

### Nuevos Módulos v3.9.1 (execute Integration)

| Modulo | Funcion |
|--------|---------|
| agent_harness/memory.py (find_latest_analysis) | Auto-descubrimiento de analisis_completo.json previo |
| agent_harness/memory.py (save_analysis_reference) | Guarda referencia de análisis en historial |
| agent_harness/memory.py (cleanup_old_sessions) | TTL de 20 días para sesiones |

### Nuevos Módulos v4.5.6 (NEVER_BLOCK Architecture)

|| Modulo | Funcion |
|--------|---------|
|| modules/providers/benchmark_resolver.py | Fallback con benchmark regional (Pereira/Santa Rosa de Cabal) |
|| modules/providers/autonomous_researcher.py | Investigacion en fuentes publicas (GBP, Booking, TripAdvisor, Instagram) |
|| modules/providers/disclaimer_generator.py | Disclaimers honestos por nivel de confidence |
|| modules/asset_generation/asset_metadata.py | Campo `disclaimers` para assets |

### Nuevos Módulos v4.6.0 (HEALTH DASHBOARD - FASE 10)

|| Modulo | Funcion |
|--------|---------|
|| modules/monitoring/__init__.py | Módulo de monitoring con exports |
|| modules/monitoring/health_metrics_collector.py | ExecutionMetrics dataclass + HealthMetricsCollector |
|| modules/monitoring/health_dashboard_generator.py | HealthDashboardGenerator con Chart.js |
|| tests/monitoring/test_health_dashboard.py | 14 tests para FASE 10 |

### Nuevos Módulos v4.8.0 (FASE-CAUSAL-01 - SITE PRESENCE CHECKER)

| Modulo | Funcion |
|--------|---------|
| modules/asset_generation/site_presence_checker.py | Verificacion sitio real ANTES de generar assets |

### Módulos Modificados v4.8.0 (FASE-CAUSAL-01)

| Modulo | Cambio |
|--------|--------|
| modules/asset_generation/conditional_generator.py | Integración site_url + gate SitePresenceChecker |
| modules/asset_generation/asset_metadata.py | Estados SKIPPED, REDUNDANT en AssetStatus |
| modules/asset_generation/v4_asset_orchestrator.py | SkippedAsset dataclass + reporting mejorado |
| tests/asset_generation/test_site_presence_checker.py | 10 tests para SitePresenceChecker |

### Módulos Modificados v3.9

| Modulo | Cambio |
|--------|--------|
| modules/generators/report_builder_fixed.py | Bug competitors_data + precio con metadatos |
| modules/scrapers/web_scraper.py | _extract_price retorna metadatos de fuente |
| modules/analyzers/gap_analyzer.py | Usa FinancialFactors en lugar de hardcoded |
| modules/analyzers/ia_tester.py | Bing Proxy como fallback de ChatGPT |

### Documentación Técnica de Referencia (NUEVO v3.7)

| Tema | Ubicacion |
|------|-----------|
| Fórmulas de Cálculo GBP (geo_score, pérdidas) | [docs/FORMULAS_CALCULO_GBP.md](docs/FORMULAS_CALCULO_GBP.md) |
| Migración Selenium → Playwright | [docs/MIGRACION_PLAYWRIGHT.md](docs/MIGRACION_PLAYWRIGHT.md) |

### Documentación de Automatización v3.8

| Tema | Ubicacion |
|------|-----------|
| Pre-commit Configuration | [.pre-commit-config.yaml](.pre-commit-config.yaml) |
| Validation Engine | [modules/validation/](modules/validation/) |
| Multi-Driver Architecture | [modules/scrapers/drivers/](modules/scrapers/drivers/) |

### Generadores de Entrega (v3.6)

| Modulo | Funcion |
|--------|---------|
| modules/delivery/delivery_context.py | Contexto inteligente: mapea brechas a assets a generar |
| modules/delivery/generators/schema_gen.py | Generador de Schema LodgingBusiness jerarquico |
| modules/delivery/generators/faq_gen.py | Generador de bloques FAQPage con justificacion |
| modules/delivery/generators/seo_fix_gen.py | Fixes especificos para issues SEO detectados |
| modules/delivery/generators/wa_button_gen.py | Boton WhatsApp solo si hay fuga detectada |
| modules/delivery/generators/booking_bar_gen.py | Barra de reserva si motor no es prominente |
| modules/generators/outreach_gen.py | Logica de poda regional (LinkedIn) |

### Skills Principales (Official Framework)

| Skill | Ubicacion |
|-------|-----------|
| Truth Protocol | [.agents/workflows/truth_protocol.md](.agents/workflows/truth_protocol.md) |
| Audit Guardian | [.agents/workflows/audit_guardian.md](.agents/workflows/audit_guardian.md) |
| Delivery Wizard | [.agents/workflows/delivery_wizard.md](.agents/workflows/delivery_wizard.md) |
| QA Guardian | [.agents/workflows/qa_guardian.md](.agents/workflows/qa_guardian.md) |
| Deployment Assistant | [.agents/workflows/deployment_assistant.md](.agents/workflows/deployment_assistant.md) |
| Meta Skill Creator | [.agents/workflows/meta_skill_creator.md](.agents/workflows/meta_skill_creator.md) |

### Historial de Cambios

| Documento | Contenido |
|-----------|-----------|
| [CHANGELOG.md](CHANGELOG.md) | Ultimas 5 versiones (v3.6.0 - v3.1.0) |
| [CHANGELOG_ARCHIVE.md](docs/archive/CHANGELOG_ARCHIVE.md) | Versiones historicas (v3.0.0 y anteriores) |

---

**Version:** 4.8.0
**Ultima actualizacion:** 23 Marzo 2026
**IA Hoteles Agent v4.8.0**

---

## Nuevos Módulos v4.5.1 (GEO Integration Fixed)

| Modulo | Funcion |
|--------|---------|
| modules/commercial_documents/pain_solution_mapper.py | Detección de problemas GEO (ai_crawler_blocked, low_citability, low_ia_readiness) |
| modules/commercial_documents/v4_diagnostic_generator.py | Sección de métricas GEO en diagnóstico |
| modules/commercial_documents/v4_proposal_generator.py | Assets GEO en propuesta comercial |
| modules/asset_generation/conditional_generator.py | Gate de contenido vacío y placeholders |
| tests/asset_generation/test_content_gates.py | 19 tests para validación de contenido |

### Módulos v4.5.0 (GEO Integration) - Anteriores

| Modulo | Funcion |
|--------|---------|
| modules/auditors/ai_crawler_auditor.py | Auditoría de robots.txt para IA crawlers |
| modules/asset_generation/llmstxt_generator.py | Generación de llms.txt estándar |
| modules/auditors/citability_scorer.py | Score de citabilidad de contenido |
| modules/auditors/ia_readiness_calculator.py | Score compuesto IA-readiness |
