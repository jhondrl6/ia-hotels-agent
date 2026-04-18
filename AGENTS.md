<!-- agents_version: 4.31.1 | last_update: 2026-04-18 -->

# IA Hoteles Agent (iah-cli)

> **v4.31.1 -- AMAZILIA-BUGFIX Release Complete COMPLETADO**

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
| `v4_complete.md` | "diagnostico", "analiza este hotel" | Flujo v4 completo: onboarding, validacion, assets |
| `v4_quality_validator.md` | "valida calidad", "QA", "verifica" | Validador integral pre-generacion y post-entrega |
| `v4_financial_scenarios.md` | "calcula escenarios", "financiero" | Escenarios conservador/realista/optimista v4 |
| `v4_regional_resolver.md` | "benchmark regional", "resuelve region" | resuelve ADR y benchmarks regionales |
| `v4_asset_conditional.md` | "genera assets", "assets condicionales" | Genera assets con preflight checks y gates |
| `v4_regression_guardian.md` | "regresion", "post-implementacion" | Validacion post-implementacion flujo v4complete |
| `truth_protocol.md` | "verifica datos", "certifica veracidad" | Certificar veracidad datos financieros |
| `delivery_wizard.md` | "entrega", "kit de entrega" | Generar kit de entrega completo |
| `deployment_assistant.md` | "despliega", "deploy" | Desplegar kits AEO en WordPress |
| `seo_technical.md` | "SEO tecnico", "auditoria tecnica" | Auditoria tecnica y credibilidad web |
| `env_rerun.md` | "fallo entorno", "API key" | Solucionar fallos de entorno y API Keys |
| `maintenance_autopilot.md` | "mantenimiento skills" | Auto-mantenimiento arquitectura de skills |
| `meta_skill_creator.md` | "crear skill", "nuevo workflow" | Fabrica para crear nuevas Meta-Skills |
| `watchdog_check.md` | "vigilancia", "anomalias" | Escaner de vigilancia y alertas |
| `monitor_bg.md` | "monitorea", "segundo plano" | Monitoreo de tareas en segundo plano |
| `phased_project_executor.md` | "por fases", "una fase" | Executor de proyectos por fases (1 fase/sesion) |

---

## Vinculo con la Documentacion del Repositorio

Para actualizar cualquier documento del repositorio (CHANGELOG, VERSION, docs):

→ `docs/CONTRIBUTING.md` — Indice y procedimientos oficiales
→ `docs/contributing/documentation_rules.md` — Checklist de documentacion obligatoria
→ `docs/contributing/validation.md` — Pre-commit hooks y validaciones

**Prompt para el agente:** "Actualizar documentacion oficial:VERSION sync + CHANGELOG + REGISTRY via scripts/log_phase_completion.py"

### Flujo Documental Obligatorio (Resumen)

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
```

**Regla**: NO ejecutar planes de documentación directamente. SIEMPRE seguir el flujo anterior.

**Detalle completo**: `.agents/workflows/phased_project_executor.md` §4.5

**Regenerable (1 comando):**
- `.agent/SYSTEM_STATUS.md` → `python main.py --doctor --status`

## Estado Actual

| Aspecto | Estado |
|---------|--------|
| **Tests** | 2224 funciones, 140 archivos, 0 regresion |
| **Bloqueante** | Ninguno |
| **Coherence Score** | ✅ 0.84 (umbral: 0.8) - PASA el gate |
| **Publication Ready** | ✅ true |
| **Mejoras** | TDD Gate, Parallel Execution, FAQGenerator, GA4 Multi-Hotel, **Doctor CLI**, **Pre-commit ecosystem validation**, **v4_quality_validator unificado**, **4 Pilares Alignment**, **Voice Readiness Proxy** |

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

### Uso Recomendado

```bash
# Análisis completo nuevo
python main.py v4complete --url https://hotel.com

# Diagnóstico del ecosistema de agentes
python main.py --doctor

# Implementar paquete (usa análisis previo si existe)
python main.py execute --url https://hotel.com --package starter_geo
```

---

## Módulos Activos

| Módulo | Función | Usado por |
|--------|---------|-----------|
| `data_validation/` | Validación cruzada web+GBP+input | v4audit, v4complete |
| `data_validation/metadata_validator.py` | Detección de CMS defaults | v4complete |
| `data_validation/consistency_checker.py` | Validación inter-documento | v4complete |
| `data_validation/evidence_ledger.py` | Almacén centralizado de evidencia | v4complete, v4audit |
| `data_validation/contradiction_engine.py` | Detección de hard/soft conflicts | v4complete |
| `data_validation/schema_validator_v2.py` | Coverage scoring | v4audit |
| `modules/financial_engine/` | Escenarios: conservador/realista/optimista | v4audit, v4complete |
| `modules/financial_engine/calculator_v2.py` | FinancialCalculatorV2 con validación | v4complete |
| `modules/financial_engine/no_defaults_validator.py` | Validación "No Defaults in Money" | v4complete |
| `modules/financial_engine/harness_handlers.py` | Handlers para Agent Harness | v4complete |
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

| `modules/commercial_documents/coherence_validator.py` | Validador de coherencia con promised_assets_exist | v4complete |
| `agent_harness/` | Memoria, auto-corrección, routing, MCP | Todos los comandos |
| `agent_harness/memory.py` | Persistencia de estado y vigencia de análisis | Todos |
| `observability/` | Métricas y calibración | Todos |
| `observability/dashboard.py` | Dashboard de calidad | Todos |
| `observability/calibration.py` | Calibración de umbrales de confianza | Todos |
| `modules/quality_gates/` | Gates: técnico, comercial, financiero, coherencia, publicación | v4complete |
| `data_models/` | Modelos: CanonicalAssessment, Claim, Evidence, AnalyticsStatus, AEOKPIs | v4complete, v4audit |
| `enums/` | Enumeraciones: Severity, ConfidenceLevel | Todos |
| `modules/geo_enrichment/` | Enriquecimiento geográfico (GEO) | v4complete |
| `modules/scrapers/` | Scrapers externos (Booking, TripAdvisor, etc.) | v4audit |
| `modules/delivery/` | Packaging y entrega de resultados | execute |
| `modules/commercial_documents/pain_solution_mapper.py` | Mapeo problemas→assets con pain types analytics | v4complete |

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
└─ critical_recall: ≥ 90%

FASE 4.6: CONSISTENCY CHECKER
─────────────────────────────
Validación cruzada de claims:
├─ whatsapp_consistency
├─ gbp_consistency
├─ schema_consistency
└─ adr_validation

FASE 4.7: PROMISE vs IMPLEMENTATION
──────────────────────────────
├─ promised_assets_exist: valida que assets prometidos existen en генератор
└─ severity: error (blocking)
```

---

## Criterios de Éxito

| Check | Umbral | Configurable en |
|-------|--------|-----------------|
| Coherence Score | ≥ 0.8 | `.conductor/guidelines.yaml` |
| WhatsApp Verificado | ≥ 0.9 | `.conductor/guidelines.yaml` |
| Datos Financieros | ≥ 0.7 | `.conductor/guidelines.yaml` |
| Price/Loss Ratio | 3x-6x | `.conductor/guidelines.yaml` |
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
| Test failures | Regresion o cambio breaking | `python main.py --doctor --agent` para diagnosticar |
| Skill no encuentra workflow | Ruta `.agents/workflows/` inexistente | Verificar symlink `.agent/workflows` -> `.agents/workflows` |
| Agent Harness no responde | MCP client o skill router bloqueado | `python scripts/doctor.py --json` para diagnostico estructurado |

**Fuente unica de version**: `VERSION.yaml` en raiz. Nunca hardcodear versiones en codigo.

**Convencion de arquitectura**: `.agent/CONVENTION.md` - contrato para cualquier futuro agente o modificacion.

---

<!--
ZONA REFERENCIA - Solo si es necesario para contexto profundo
Actualizada: 2026-04-03 | v4.19.0
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
# Todas las pruebas (1782 funciones, 140 archivos)
python -m pytest tests/ -v

# Suite de regresión (52 tests)
python -m pytest tests/regression/ -v

# Solo modulos v4 core
python -m pytest tests/data_validation tests/financial_engine \
                  tests/orchestration_v4 tests/asset_generation -v

# Validaciones de coherencia
python scripts/run_all_validations.py --quick  # Rapido
python scripts/run_all_validations.py           # Completo
```

### Cobertura por Modulo (1782 funciones totales)

| Modulo | Funciones test | Directorio |
|--------|---------------|------------|
| financial_engine | 339 | `tests/financial_engine/` |
| test_never_block_architecture | 159 | `tests/test_never_block_architecture/` |
| data_validation | 126 | `tests/data_validation/` |
| asset_generation | 150 | `tests/asset_generation/` |
| geo_enrichment | 140 | `tests/geo_enrichment/` |
| quality_gates | 87 | `tests/quality_gates/` |
| auditors | 75 | `tests/auditors/` |
| orchestration_v4 | 66 | `tests/orchestration_v4/` |
| scrapers | 29 | `tests/scrapers/` |
| providers | 18 | `tests/providers/` |
| e2e | 13 | `tests/e2e/` |
| delivery | 11 | `tests/delivery/` |
| monitoring | 14 | `tests/monitoring/` |
| observability | 9 | `tests/observability/` |
| regression | 52 | `tests/regression/` |
| commercial_documents | 9 | `tests/commercial_documents/` |
| root test files | ~482 | `tests/test_*.py` (integration, harness, data models) |

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
│   ├── evidence.py
│   ├── aeo_kpis.py
│   └── analytics_status.py
├── data_validation/            # Validación cruzada
│   ├── evidence_ledger.py
│   ├── contradiction_engine.py
│   ├── consistency_checker.py
│   ├── metadata_validator.py
│   └── schema_validator_v2.py
├── agent_harness/              # Core del agente
│   ├── core.py
│   ├── memory.py
│   ├── mcp_client.py
│   ├── observer.py
│   ├── self_healer.py
│   ├── skill_executor.py
│   └── skill_router.py
├── observability/              # Dashboard y calibracion
│   ├── dashboard.py
│   └── calibration.py
├── enums/                      # Enumeraciones
│   ├── severity.py
│   ├── confidence_level.py
│   └── types.py
├── modules/                    # Modulos funcionales
│   ├── analytics/              # GA4, Profound, Semrush
│   ├── asset_generation/       # Generacion condicional + templates
│   ├── auditors/               # APIs externas (Rich Results, Places...)
│   ├── commercial_documents/   # Diagnostico, propuesta, coherencia
│   ├── financial_engine/       # Escenarios + no_defaults_validator
│   ├── geo_enrichment/         # Enriquecimiento geografico (GEO)
│   ├── quality_gates/          # Gates de publicacion
│   ├── orchestration_v4/       # Flujo dos fases Hook → Validacion
│   ├── scrapers/               # Scrapers externos (Booking, TripAdvisor)
│   ├── delivery/               # Packaging y entrega
│   ├── generators/             # Generadores auxiliares
│   ├── analyzers/              # Analizadores de contenido
│   ├── deployer/               # Despliegue FTP/WP-API
│   ├── monitoring/             # Health dashboard
│   ├── onboarding/             # Captura datos hotel
│   ├── providers/              # LLM providers
│   ├── utils/                  # Utilidades
│   └── validation/             # Validaciones adicionales
├── tests/                      # Suite de pruebas (1782 funciones)
│   ├── regression/             # Regresion permanente (52 tests)
│   ├── data_validation/
│   ├── financial_engine/
│   ├── orchestration_v4/
│   ├── asset_generation/
│   ├── auditors/
│   ├── geo_enrichment/
│   ├── quality_gates/
│   ├── commercial_documents/
│   ├── observability/
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
