<!-- agents_version: v4.74.1 | last_update: 2026-09-02 -->

# IA Hoteles Agent (iah-cli)

> **v4.74.1 -- Blocklist-v2 COMPLETADO**

---

## Politica de Contexto Global

### WHY
- Reducir ambiguedad operativa con una sola fuente primaria.
- Optimizar carga cognitiva del agente: señal/ruido ≥ 90%.
- Garantizar confiabilidad mediante validación cruzada de datos.

### WHAT
- `AGENTS.md` = contexto global esencial (estructura de dos zonas).
- `.cursorrules` = puente de compatibilidad legacy.
- `docs/` = detalles de bajo nivel (progressive disclosure).

### HOW
- Zona Esencial (lineas 1-294): operativo inmediato, modulos, workflows, comandos.
- Zona Referencia (linea 295+): contexto historico, arquitectura y estructura.
- Cambios: editar aqui primero, validar despues.

**Validaciones**:
```bash
python scripts/run_all_validations.py --quick
python scripts/run_all_validations.py
python scripts/doctor.py --status        # Regenerar SYSTEM_STATUS.md
python scripts/validate_agent_ecosystem.py  # Verificar integridad de skills
```

**Pre-commit hooks activos:**
- `agent-ecosystem`: valida skills, refs, symlink, shadow logs, memoria antes de cada commit
- `version-sync`: sincroniza VERSION.yaml con README, AGENTS, CONTRIBUTING, etc.

---

## Workflows Disponibles (.agents/workflows/)

| Workflow | Trigger | Descripcion |
|----------|---------|-------------|
| `phased_project_executor.md` | "por fases", "una fase" | Executor de proyectos por fases (1 fase/sesion) |

> **Nota (limpieza 2026-08-24)**: Los 16 skills restantes fueron archivados en
> `archives/deprecated_workflows_20260824/`. La funcionalidad de la familia v4_* ya vive
> en codigo (`python main.py v4complete`, `tests/regression/`); los stubs nunca se usaron.
> Para "diagnostico"/"analiza este hotel" usar el comando CLI `v4complete`.

---

## Vinculo con la Documentacion del Repositorio

Para actualizar cualquier documento del repositorio (CHANGELOG, VERSION, docs):

→ `docs/CONTRIBUTING.md` — Indice y procedimientos oficiales
→ `docs/contributing/documentation_rules.md` — Checklist de documentacion obligatoria
→ `docs/contributing/validation.md` — Pre-commit hooks y validaciones

**Prompt para el agente:** "Actualizar documentacion oficial:VERSION sync + CHANGELOG + REGISTRY via scripts/log_phase_completion.py"

### Flujo Documental Obligatorio (Resumen)

> [!IMPORTANT]
> **DOMAIN_PRIMER se regenera en FASE-RELEASE** (no manualmente). Ver `.opencode/plans/INTEGRACION-DOCUMENTAL-PLAN.md` para el plan de integración documental completo.
>
> Los vínculos abaixo son **verificables por script** (ver FASE-C del plan de integración).

Cuando se ejecuta un plan de documentación (ej: `09-documentacion-post-proyecto.md`):

```
1. log_phase_completion.py --fase FASE-X --desc "..." --check-manual-docs
   → Registra en REGISTRY.md automáticamente

2. sync_versions.py
   → Sincroniza VERSION.yaml → 6 archivos (AGENTS, README, .cursorrules, CONTRIBUTING, GUIA_TECNICA, REGISTRY)

3. Verificar CHANGELOG.md formato CONTRIBUTING.md:
   ### Objetivo / ### Cambios / ### Archivos Nuevos / ### Archivos Modificados / ### Tests

4. Verificar GUIA_TECNICA.md tiene nota técnica por fase

5. run_all_validations.py --quick
   → Validación final (4/4 checks)

5b. validate_agents_md.py
   → Gate de coherencia AGENTS.md (gate count, module refs, etc.)
```

**Regla**: NO ejecutar planes de documentación directamente. SIEMPRE seguir el flujo anterior.

**Detalle completo**: `.agents/workflows/phased_project_executor.md` §4.5

### Tabla de Cross-References Documentales

|| Documento | Seccion en AGENTS.md | Seccion en CONTRIBUTING | Seccion en Executor |
|-----------|----------------------|-------------------------|---------------------|
| `AGENTS.md` | (este archivo) | `§Contrato-con-phased_project_executor` | — |
| `CONTRIBUTING.md` | `§Vinculo-con-la-Documentacion` | — | `§Paso-2` |
| `phased_project_executor.md` | `§Flujo-Documental-Obligatorio` | `§Flujo-Post-Fase` | — |
| `DOMAIN_PRIMER.md` | (auto-regenerado) | `§Paso-5b` | `§E7` |
| `prompt-fase-template.md` | — | — | `§2-Crear-Prompts` |
| `validate_document_integration.py` | (script de validacion) | `validation.md §13` | — |

**Gate de No-Regresion Documental**: Ejecutar `python scripts/validate_document_integration.py`
antes de cada commit para prevenir desincronizacion entre los 4 documentos clave.

**Regenerable (comandos directos):**
- `.agent/SYSTEM_STATUS.md` → `python scripts/doctor.py --status`

## Estado Actual

| Aspecto | Estado |
|---------|--------|
| **Tests** | 3,689 funciones, 284 archivos, 0 regresion |
| **Bloqueante** | Ninguno |
| **Coherence Score** | ✅ ≥0.8 (varía por ejecución; umbral: 0.8) - PASA el gate |
| **Publication Ready** | ✅ true |
| **Mejoras** | TDD Gate, Parallel Execution, FAQGenerator, GA4 Multi-Hotel, **Doctor CLI**, **Pre-commit ecosystem validation**, **v4_quality_validator unificado**, **4 Pilares Alignment**, **Voice Readiness Proxy**, **DT-4 Residual Fixes (pain_ledger + SitePresence + coherence/alignment unify + gate idempotency)** |

---

## Comandos CLI

| Comando | Estado | Descripción |
|---------|--------|-------------|
| `v4complete` | ✅ Recomendado | Flujo completo: diagnóstico, propuesta, assets, coherencia |
| `v4audit` | ✅ Funcional | Auditoría con APIs externas (Rich Results, Places, PageSpeed) |
| `spark` | ⚠️ Deprecado | Legacy, usar `v4complete` |
| `execute` | ✅ Funcional | Implementa paquete, recupera análisis previo |
| `stage` | ✅ Funcional | Ejecuta etapas individuales (geo, ia, seo, outputs) |
| `deploy` | ✅ Funcional | Despliegue remoto via FTP/WP-API |
| `setup` | ✅ Funcional | Configuración interactiva de API keys |
| `onboard` | ✅ Funcional | Captura datos operativos del hotel |
| `--doctor` | ✅ Funcional | Diagnóstico del ecosistema de agentes |
| `audit` | ⚠️ Deprecado | Legacy v3.x, usar `v4complete` |
| `hook-pdf` | ✅ Funcional | PDF gancho 2 páginas desde output v4complete |
| `validate-guarantee` | ✅ Funcional | Valida garantía Día 55 sobre output v4complete |

### Uso Recomendado

```bash
# Análisis completo nuevo
python main.py v4complete --url https://hotel.com

# Diagnóstico del ecosistema de agentes
python main.py --doctor

# Implementar paquete (usa análisis previo si existe)
python main.py execute --url https://hotel.com --package starter_geo

# Generar PDF gancho desde output v4complete
python main.py hook-pdf --output-dir output/v4_complete/
```

---

## Módulos Activos

| Módulo | Función | Usado por |
|--------|---------|-----------|
| `data_validation/` | Validación cruzada web+GBP+input | v4audit, v4complete |
| `data_validation/metadata_validator.py` | Detección de CMS defaults | v4complete |
| `data_validation/consistency_checker.py` | Validación inter-documento | v4complete |
| `data_validation/evidence_ledger.py` | [DEPRECADO] reemplazado por pain_ledger en `modules/asset_generation/` | v4complete, v4audit |
| `data_validation/contradiction_engine.py` | Detección de hard/soft conflicts | v4complete |
| `modules/data_validation/schema_validator_v2.py` | Coverage scoring | v4audit |
| `modules/financial_engine/` | Escenarios: conservador/realista/optimista | v4audit, v4complete |
| `modules/financial_engine/calculator_v2.py` | FinancialCalculatorV2 con validación | v4complete |
| `modules/financial_engine/no_defaults_validator.py` | Validación "No Defaults in Money" | v4complete |
| `modules/financial_engine/harness_handlers.py` | Handlers para Agent Harness | v4complete |
| `modules/asset_generation/pain_ledger.py` | Trazabilidad pain_id → fuente → severidad → asset | v4complete |
| `modules/quality_gates/delivery_quality_report.py` | QA post-generación bloqueante (408 líneas, 10 tests) | v4complete |
| `modules/quality_gates/human_checklist_generator.py` | ≤10 items derivados automáticamente | v4complete |
| `modules/asset_generation/data_derivation_layer.py` | 5 derivaciones semánticas del audit (350 líneas, 26 tests) | v4complete |
| `modules/data_validation/confidence_taxonomy.py` | Taxonomía de niveles de confianza | v4complete, v4audit |
| `modules/data_validation/cross_validator.py` | Validación cruzada multi-fuente | v4audit, v4complete |
| `modules/financial_engine/opportunity_scorer.py` | Scoring ponderado 3 factores (severidad+esfuerzo+impacto) para priorizar brechas (FASE-C) | v4complete |
| `modules/orchestration_v4/` | Flujo dos fases: Hook → Validación | v4complete |
| `modules/asset_generation/` | Generación condicional con gates | v4complete |
| `modules/asset_generation/asset_catalog.py` | Catálogo centralizado de assets con is_asset_implemented | v4complete |
| `modules/asset_generation/llmstxt_generator.py` | Generación de llms.txt estándar | v4complete, execute |
| `modules/asset_generation/local_content_generator.py` | Generación de contenido local 3-5 paginas boutique (FASE-E) | v4complete |
| `modules/auditors/` | APIs externas (Rich Results, Places, PageSpeed) | v4audit, v4complete |
| `modules/auditors/ai_crawler_auditor.py` | Auditoría de robots.txt para IA crawlers | v4audit, v4complete |
| `modules/auditors/citability_scorer.py` | Score de citabilidad de contenido | v4audit (ADVISORY) |
| `modules/auditors/ia_readiness_calculator.py` | Score compuesto IA-readiness | v4audit (ADVISORY) |
| `modules/auditors/voice_readiness_proxy.py` | Voice Readiness Proxy (GBP 30%, Schema 25%, Snippets 25%, Factual 20%) | v4complete (FASE-E) |
| `modules/analytics/` | GA4, GSC, Profound, Semrush clients | v4audit |
| `modules/analytics/google_analytics_client.py` | Cliente GA4 para tráfico indirecto | v4audit (ADVISORY) |
| `modules/analytics/google_search_console_client.py` | Cliente GSC para keywords, posiciones, CTR | v4audit, v4complete (ADVISORY) |
| `modules/analytics/data_aggregator.py` | Unifica GA4 + GSC en datos consolidados | v4complete (ADVISORY) |
| `modules/commercial_documents/` | Diagnóstico, propuesta, coherencia | v4complete |
| `modules/commercial_documents/hook_pdf_generator.py` | PDF gancho 2 páginas (hook-pdf) | hook-pdf |
| `modules/commercial_documents/coherence_validator.py` | Validador de coherencia con promised_assets_exist | v4complete |
| `agent_harness/` | Memoria, auto-corrección, routing, MCP | Todos los comandos |
| `agent_harness/memory.py` | Persistencia de estado y vigencia de análisis | Todos |
| `modules/quality_gates/` | 13 publication gates — blocking (10): evidence_coverage, coherence, hard_contradictions, coverage_no_silent_drop, financial_validity, critical_recall, ethics, tier_c_onboarding_required, doc_audit_consistency, pricing_compliance; advisory (3): content_quality, asset_confidence, proposal_asset_alignment | v4complete |
| `data_models/` | Modelos: CanonicalAssessment, Claim, AnalyticsStatus, AEOKPIs | v4complete, v4audit |
| `enums/` | Enumeraciones: Severity, ConfidenceLevel | Todos |
| `modules/geo_enrichment/` | Enriquecimiento geográfico (GEO) | v4complete |
| `modules/scrapers/` | Scrapers externos (Booking, TripAdvisor, etc.) | v4audit |
| `modules/delivery/` | Packaging y entrega de resultados | execute |
| `modules/commercial_documents/pain_solution_mapper.py` | Mapeo problemas→assets con pain types analytics | v4complete |
| `modules/utils/` | Utilidades transversales (config_checker, benchmarks, http_client) | Todos los comandos |
| `modules/common/` | Loaders compartidos YAML/fallback | financial_engine, commercial_documents |
| `modules/providers/` | LLM providers, benchmark resolver, disclaimers | scrapers, analyzers |
| `modules/deployer/` | Despliegue FTP/WP-API | deploy |
| `modules/onboarding/` | Formularios, validadores y carga de datos | onboard |
| `modules/generators/` | Generadores auxiliares (report_builder, spark, outreach) | spark |
| `modules/analyzers/` | Analizadores de gaps, competencia y ROI | v4audit, config_checker |
| `modules/monitoring/` | Health dashboard y métricas | main.py |
| `modules/postprocessors/` | Quality gate y scrubber de contenido | publication_gates |
| `modules/quality/` | Validadores semánticos y de coherencia financiera | publication_gates, pain_solution_mapper |
| `modules/orchestration/` | Reconciliador post-orquestación | tests |
| `modules/validation/` | Validación de contenido, plan y seguridad | interno |
| `modules/assessment_builder.py` | Construcción del assessment canónico | v4complete |
| `modules/data_validation/own_site_guard.py` | Guard URL propia (v4.74.0) | v4complete, hook-pdf |
| `modules/analytics/guarantee_validator.py` | Validación Garantía Día 55 | validate-guarantee |

---

## Flujo de Trabajo v4

```
FASE 1: HOOK (Automático)
─────────────────────────
URL → Benchmark Regional → Rango Estimado
Output: Hook con disclaimer, Progreso: 30%

FASE 2: VALIDACIÓN CRUZADA
──────────────────────────
Datos web + GBP + input usuario
├─ WhatsApp: web vs GBP vs input
├─ ADR: benchmark vs input vs scraping
└─ Conflictos → Reporte o Continuar

FASE 3: ESCENARIOS FINANCIEROS
──────────────────────────────
| Escenario    | Prob | Base              |
|--------------|------|-------------------|
| Conservador  | 70%  | Peor caso plausible |
| Realista     | 20%  | Meta esperada     |
| Optimista    | 10%  | Mejor caso        |

FASE 3.5: DOCUMENTOS COMERCIALES
──────────────────────────────
- 01_DIAGNOSTICO_Y_OPORTUNIDAD.md
- 02_PROPUESTA_COMERCIAL.md
- Gate de coherencia: score ≥ 0.8

FASE 4: ASSETS CONDICIONALES
───────────────────────────
Preflight checks:
├─ WhatsApp: confidence ≥ 0.9
├─ FAQ Page: confidence ≥ 0.7
└─ Hotel Schema: confidence ≥ 0.8

Nomenclatura:
├─ PASSED: boton_whatsapp.html
├─ WARNING: ESTIMATED_boton_whatsapp.html
└─ BLOCKED: No generar

FASE 4.5: PUBLICATION GATES
────────────────────────────
├─ hard_contradictions: count = 0
├─ evidence_coverage: ≥ 95%
├─ financial_validity: sin defaults
├─ coherence: ≥ 0.8
├─ critical_recall: ≥ 90%
├─ ethics: sin violaciones
├─ content_quality: sin errores
├─ asset_confidence: ≥ threshold
├─ proposal_asset_alignment: sin divergencias
├─ tier_c_onboarding_required: assessment dict injection
├─ pricing_compliance: pain_ratio ≤ tier gate_max (floor-aware D1)
└─ coverage_no_silent_drop: brechas_diagnostico + brechas_justificadas == brechas_detectadas

FASE 4.6: CONSISTENCY CHECKER
─────────────────────────────
Validación cruzada de claims:
├─ whatsapp_consistency
├─ gbp_consistency
├─ schema_consistency
└─ adr_validation

FASE 4.7: PROMISE vs IMPLEMENTATION
──────────────────────────────
├─ promised_assets_exist: valida que assets prometidos existen en el generador de assets
└─ severity: error (blocking)

FASE 5: DELIVERY QUALITY (FASE-0)
─────────────────────────────────
├─ pain_ledger: trazabilidad pain_id → fuente → severidad → asset
├─ coverage gate (G7): brechas_diagnóstico + brechas_justificadas == brechas_detectadas
├─ tier_c_onboarding_required gate: assessment dict injection
├─ delivery_quality_report: QA post-generación bloqueante (408 líneas, 10 tests)
├─ human_checklist: ≤10 items derivados automáticamente
└─ data_derivation_layer: 5 derivaciones semánticas del audit (350 líneas, 26 tests)
```

---

## Criterios de Éxito

| Check | Umbral | Configurable en |
|-------|--------|-----------------|
| Coherence Score | ≥ 0.8 | `modules/quality_gates/publication_gates.py` |
| WhatsApp Verificado | ≥ 0.9 | `modules/quality_gates/domain_gates.py` |
| Datos Financieros | ≥ 0.7 | `modules/quality_gates/coherence_gate.py` |
| Price/Loss Ratio | 3x-6x | `config/pricing.yaml` |
| Vigencia análisis | < 20 días | `agent_harness/memory.py` |

---

## Taxonomía de Confianza

| Nivel | Confidence | Criterio | Uso en Assets |
|-------|------------|----------|---------------|
| 🟢 VERIFIED | ≥ 0.9 | 2+ fuentes coinciden | Directo |
| 🟡 ESTIMATED | 0.5-0.9 | 1 fuente o benchmark | Con disclaimer |
| 🔴 CONFLICT | < 0.5 | Fuentes contradicen | Bloqueado |

---

## KPIs y Métricas

| KPI | Umbral | Medición |
|-----|--------|----------|
| Evidence Coverage | >= 95% | Claims con evidencia / Total |
| Hard Contradictions | = 0 | Bloquean export |
| Financial Validity | = 100% | Sin defaults |
| Critical Issue Recall | >= 90% | Detectados / Reales |
| Coherence Score | >= 0.8 | Para certificar |
| Execution Trace | Completo | Validadores ejecutados/saltados |

## Métricas Advisory (No Bloqueantes)

| Métrica | Descripción | Rango | Uso |
|---------|-------------|-------|-----|
| Citability Score | Calidad de contenido para citación IA | 0-100 | Diagnóstico |
| IA-Readiness | Preparación general para IA | 0-100 | Diagnóstico |
| AI Crawler Score | Accesibilidad para crawlers IA | 0-100 | Diagnóstico |

Estas métricas son **ADVISORY** - se reportan pero NO afectan:
- Publication gates
- Coherence score
- Overall confidence

Se incluyen para orientar mejoras pero nunca bloquean publicación.

---

## Diagnostico Rapido de Fallos

| Sintoma | Causa Probable | Solucion |
|---------|---------------|----------|
| Symlink roto en `.agent/workflows` | Windows requiere permisos admin | Ejecutar terminal como admin o recrear con `mklink /D` |
| Coherence < 0.8 | Claims sin evidencia o contradicciones | `python scripts/doctor.py --context` para ver detalles |
| Version mismatch en docs | Docs no sincronizadas con VERSION.yaml | Pre-commit `version-sync` hook o ejecutar `python scripts/version_consistency_checker.py` |
| Error de API key ausente | .env no configurado o key invalida | `python main.py setup` o editar `.env` manualmente |
| Test failures | Regresion o cambio breaking | `python scripts/doctor.py --agent` para diagnosticar |
| Skill no encuentra workflow | Ruta `.agents/workflows/` inexistente | Verificar symlink `.agent/workflows` -> `.agents/workflows` |
| Agent Harness no responde | MCP client o skill router bloqueado | `python scripts/doctor.py --json` para diagnostico estructurado |

**Fuente unica de version**: `VERSION.yaml` en raiz. Nunca hardcodear versiones en codigo.

**Convencion de arquitectura**: `.agent/CONVENTION.md` - contrato para cualquier futuro agente o modificacion.

---

<!--
ZONA REFERENCIA - Solo si es necesario para contexto profundo
Actualizada: 2026-08-31 | v4.74.0
-->

## Transformación v3 → v4

De "generador de diagnósticos" a "sistema de inteligencia con niveles de certeza explicitos".
Los problemas resueltos historicos (WhatsApp falso, FAQs inconsistentes, cifras multiples, etc.) estan documentados en CHANGELOG.md.

---

## Arquitectura

### Flujo de Datos
```
URL → Validadores → Canonical Assessment → Contradiction Engine → Gates → Document Composer → Publication State
```

---

## Pruebas

```bash
# Todas las pruebas (3,689 funciones, 284 archivos)
python -m pytest tests/ -v

# Suite de regresión (26 tests)
python -m pytest tests/regression/ -v

# Solo modulos v4 core
python -m pytest tests/data_validation tests/financial_engine \
                  tests/orchestration_v4 tests/asset_generation -v

# Validaciones de coherencia
python scripts/run_all_validations.py --quick  # Rapido
python scripts/run_all_validations.py           # Completo
```

### Cobertura por Modulo (3,689 funciones totales)

| Modulo | Funciones test | Directorio |
|--------|---------------|------------|
| financial_engine | 549 | `tests/financial_engine/` |
| asset_generation | 418 | `tests/asset_generation/` |
| quality_gates | 294 | `tests/quality_gates/` |
| commercial_documents | 279 | `tests/commercial_documents/` |
| auditors | 149 | `tests/auditors/` |
| geo_enrichment | 140 | `tests/geo_enrichment/` |
| test_never_block_architecture | 122 | `tests/test_never_block_architecture/` |
| data_validation | 111 | `tests/data_validation/` |
| orchestration_v4 | 66 | `tests/orchestration_v4/` |
| config | 61 | `tests/config/` |
| utils | 57 | `tests/utils/` |
| delivery | 54 | `tests/delivery/` |
| postprocessors | 52 | `tests/postprocessors/` |
| scrapers | 38 | `tests/scrapers/` |
| analytics | 33 | `tests/analytics/` |
| regression | 26 | `tests/regression/` |
| e2e | 21 | `tests/e2e/` |
| providers | 18 | `tests/providers/` |
| common | 16 | `tests/common/` |
| monitoring | 14 | `tests/monitoring/` |
| root test files | 611 | `tests/test_*.py` (integration, harness, data models) |

---

## Estructura de Archivos

```
iah-cli/
├── main.py                     # Punto de entrada CLI
├── AGENTS.md                   # Contexto global para agentes
├── VERSION.yaml                # Fuente unica de version
├── data_models/                # Modelos de datos Pydantic
│   ├── canonical_assessment.py
│   ├── claim.py
│   ├── aeo_kpis.py
│   └── analytics_status.py
├── data_validation/            # Validación cruzada
│   ├── contradiction_engine.py
│   ├── consistency_checker.py
│   └── metadata_validator.py
├── agent_harness/              # Core del agente
│   ├── core.py
│   ├── memory.py
│   ├── mcp_client.py
│   ├── observer.py
│   ├── self_healer.py
│   ├── skill_executor.py
│   ├── skill_router.py
│   └── types.py
├── enums/                      # Enumeraciones
│   ├── severity.py
│   └── confidence_level.py
├── modules/                    # Modulos funcionales
│   ├── analytics/              # GA4, Profound, Semrush
│   ├── asset_generation/       # Generacion condicional + templates
│   ├── auditors/               # APIs externas (Rich Results, Places...)
│   ├── commercial_documents/   # Diagnostico, propuesta, coherencia
│   ├── financial_engine/       # Escenarios + no_defaults_validator
│   ├── geo_enrichment/         # Enriquecimiento geografico (GEO)
│   ├── quality_gates/          # Gates de publicacion
│   │   ├── publication_gates.py
│   │   ├── domain_gates.py
│   │   ├── coherence_gate.py
│   │   ├── delivery_quality_report.py
│   │   └── human_checklist_generator.py
│   ├── data_validation/        # Validacion avanzada
│   │   ├── confidence_taxonomy.py
│   │   ├── cross_validator.py
│   │   ├── metadata_validator.py
│   │   ├── own_site_guard.py
│   │   ├── schema_validator_v2.py
│   │   └── external_apis/
│   ├── orchestration_v4/       # Flujo dos fases Hook → Validacion
│   ├── orchestration/          # Reconciliador post-orquestacion
│   ├── scrapers/               # Scrapers externos (Booking, TripAdvisor)
│   ├── delivery/               # Packaging y entrega
│   ├── generators/             # Generadores auxiliares
│   ├── analyzers/              # Analizadores de contenido
│   ├── deployer/               # Despliegue FTP/WP-API
│   ├── monitoring/             # Health dashboard
│   ├── onboarding/             # Captura datos hotel
│   ├── providers/              # LLM providers
│   ├── utils/                  # Utilidades
│   ├── validation/             # Validaciones adicionales
│   ├── common/                 # Loaders YAML/fallback compartidos
│   ├── postprocessors/         # Quality gate + scrubber de contenido
│   └── quality/                # Validadores semanticos y de coherencia financiera
├── tests/                      # Suite de pruebas (3,689 funciones, 284 archivos)
│   ├── regression/             # Regresion permanente (26 tests)
│   ├── data_validation/
│   ├── financial_engine/
│   ├── orchestration_v4/
│   ├── asset_generation/
│   ├── auditors/
│   ├── geo_enrichment/
│   ├── quality_gates/
│   ├── commercial_documents/
│   ├── scrapers/
│   ├── providers/
│   ├── delivery/
│   ├── e2e/
│   ├── monitoring/
│   └── test_never_block_architecture/
├── templates/                  # Templates de documentos y assets
├── scripts/                    # Scripts de validacion y utilidades
├── config/                     # Archivos de configuracion (GA4, etc.)
├── docs/                       # Documentacion detallada
├── data/                       # Datos de referencia
└── logs/                       # Logs de ejecucion
```
