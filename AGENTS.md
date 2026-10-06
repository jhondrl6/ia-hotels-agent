<!-- agents_version: v4.78.0 | last_update: 2026-09-25 -->

# IA Hoteles Agent (iah-cli)

> **v4.78.0 -- Gobernanza, costura, pertinencia y carga medida COMPLETADO**

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

**Prompt para el agente:** "Actualizar documentacion oficial segun `docs/CONTRIBUTING.md` (flujo post-fase y gate de release)"

### Flujo Documental Obligatorio (Principios y referencias canonicas)

> [!IMPORTANT]
> **DOMAIN_PRIMER se regenera al cerrar cada fase de implementación**, con `python scripts/doctor.py --regenerate-domain-primer`, y **se verifica** (no se regenera) en FASE-RELEASE con `python scripts/doctor.py --context`. Es un comando que alguien invoca: no hay automatismo que lo corra, y el archivo **no se edita a mano**. Ver `.opencode/plans/INTEGRACION-DOCUMENTAL-PLAN.md` para el plan de integración documental completo.
>
> Los vínculos abaixo son **verificables por script** (ver FASE-C del plan de integración).
>
> **Este apartado ya no duplica el procedimiento paso a paso**: la secuencia ejecutable vive en
> `.agents/workflows/phased_project_executor.md` §4.5 y en `docs/CONTRIBUTING.md` (Paso 1-6). Copiarla
> aqui era lo que hacía divergir tres textos del mismo dato. Quedan los principios que gobiernan ese
> procedimiento y su referencia canónica:

- **Un resultado, una fuente.** Cada cifra o estado se registra en su artefacto (`09-documentacion-post-proyecto.md` §D para las métricas por fase, el informe o el test para una medición, `REGISTRY.md` para el registro de fases) y se **referencia** desde los demás documentos. No se re-transcribe a mano.
- **El registro de fases lo escribe la fase al cerrar**, con `scripts/log_phase_completion.py`. Ese script es el **único** escritor de la cabecera `> **Ultima actualizacion:**` de `REGISTRY.md` (fecha de la última *entrada documental*, no la de release). `sync_versions.py` no toca REGISTRY: la regla `registry_last_update` fue retirada de `scripts/sync_config.yaml`.
- **El cierre documental verifica, no re-registra.** `log_phase_completion.py` es aditivo: volver a ejecutarlo sobre una fase ya cerrada apila una entrada duplicada (§4.5 del executor, Paso 4.5.1).
- **El registro declara, no aprueba.** El escritor no ejecuta tests ni verifica contratos, así que ya no publica esas garantías como cumplidas.
- **Cinco cortes, utilizables sin commit.** Implementación terminada → verificación terminada → cierre documental → listo para revisión → espera de autorización: **los cinco** terminan en espera de autorización y se declaran y verifican sin commitear. El `git commit` NO es el quinto corte ni condición de ninguno: es una acción posterior y separada, opcional, y requiere autorización explícita.
- **Conteos que imprime la corrida.** Ni el número de checks de `run_all_validations.py --quick` ni ningún denominador se fija en un documento; lo publican la corrida y `scripts/validate_governance_numbers.py`.
- **Gate de coherencia de este archivo**: `python scripts/validate_agents_md.py`.
- **Regla**: NO ejecutar planes de documentación directamente. SIEMPRE el flujo canónico del
  executor §4.5 / `docs/CONTRIBUTING.md`.

### Tabla de Cross-References Documentales

|| Documento | Seccion en AGENTS.md | Seccion en CONTRIBUTING | Seccion en Executor |
|-----------|----------------------|-------------------------|---------------------|
| `AGENTS.md` | (este archivo) | `§Contrato-con-phased_project_executor` | — |
| `CONTRIBUTING.md` | `§Vinculo-con-la-Documentacion` | — | `§Paso-2` |
| `phased_project_executor.md` | `§Flujo-Documental-Obligatorio` | `§Flujo-Post-Fase` | — |
| `DOMAIN_PRIMER.md` | (arriba: se regenera al cerrar cada fase de implementación, con su comando) | `§Paso-5b` | `§E7` |
| `prompt-fase-template.md` | — | — | `§2-Crear-Prompts` |
| `validate_document_integration.py` | (script de validacion) | `validation.md §13` | — |

**Gate de No-Regresion Documental**: Ejecutar `python scripts/validate_document_integration.py`
antes de cada commit para prevenir desincronizacion entre los 4 documentos clave.

**Regenerable (comandos directos):**
- `.agent/SYSTEM_STATUS.md` → `python scripts/doctor.py --status`

## Estado Actual

| Aspecto | Estado |
|---------|--------|
| **Tests** | La cifra la imprime el metodo canonico (`grep -rE "^\s*def test_" tests --include=*.py`); el retrato fechado por modulo, la corrida de referencia y su evidencia viven en `§Cobertura por Modulo` (corrida POST-P6-R en `evidence/FASE-P6/`). Aqui no se re-transcribe: re-copiarla es lo que la dejaba desfasada |
| **Bloqueante** | Ninguno |
| **Coherence Score** | ✅ ≥0.8 (varía por ejecución; umbral: 0.8) - PASA el gate |
| **Publication Ready** | ✅ true |
| **Mejoras** | TDD Gate, Parallel Execution, FAQGenerator, GA4 Multi-Hotel, **Doctor CLI**, **Pre-commit ecosystem validation**, **v4_quality_validator unificado**, **4 Pilares Alignment**, **Voice Readiness Proxy**, **DT-4 Residual Fixes (pain_ledger + SitePresence + coherence/alignment unify + gate idempotency)**, **Tribunal certificador P6+P7 (Juez determinista + acta dual + 4 revisores sobre artefactos)**, **Tribunal con dientes: enforcement O1-cuarentena (el veredicto gatea rename/suppresion del ZIP) + generacion multi-hotel + certificacion 25 ACs (FASE-VERIFY)** |

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
| `modules/quality_gates/` | 13 publication gates — blocking (11): evidence_coverage, coherence, hard_contradictions, coverage_no_silent_drop, financial_validity, critical_recall, ethics, tier_c_onboarding_required, doc_audit_consistency, pricing_compliance, asset_confidence; advisory (2): content_quality, proposal_asset_alignment (degraden a blocking bajo su piso — `publication_gates.py`) | v4complete |
| `modules/quality_gates/tribunal/` | Tribunal certificador P6 con enforcement (v4.77.0): `judge.py` (veredicto determinista sobre 6 cláusulas, regla del primer piso, `_compute_verdict` consume `reviewer_reports`) + `outcome.py` (DTOs del contrato: `ReviewerReport`/`CorrectiveAction`/`TribunalOutcome`/`EnforcementState`, `blocks_publish = blocks ∧ GATE_BLOCKING_ENABLED`) + `acta_writer.py` (acta dual JSON+MD, secciones de revisores siempre visibles, `enforcement`, `corrective_actions`, `package_evidence`) + 4 revisores que **leen el ZIP en cuarentena** (`.zip.tmp`) + `artifact_paths.py` y `llm_extractor.py` (protocolo `PromiseExtractor`: el LLM propone, el Juez decide) | v4complete |
| `data_models/` | Modelos: CanonicalAssessment, Claim, AnalyticsStatus, AEOKPIs | v4complete, v4audit |
| `enums/` | Enumeraciones: Severity, ConfidenceLevel | Todos |
| `modules/geo_enrichment/` | Enriquecimiento geográfico (GEO) | v4complete |
| `modules/scrapers/` | Scrapers externos (Booking, TripAdvisor, etc.) | v4audit |
| `modules/delivery/` | Packaging y entrega de resultados — O1-cuarentena: `write()` deja `<hotel>_<fecha>.zip.tmp`, `publish()` renombra solo si el veredicto lo permite, `suppress()` borra la cuarentena | execute, v4complete |
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
blocking (11) — cualquiera fallido impide ready:
├─ hard_contradictions: count = 0
├─ evidence_coverage: ≥ 95%
├─ financial_validity: sin defaults
├─ coherence: ≥ 0.8
├─ critical_recall: ≥ 90%
├─ ethics: sin violaciones
├─ asset_confidence: blocking si 100% de assets son ESTIMATED
├─ tier_c_onboarding_required: assessment dict injection
├─ doc_audit_consistency: sin contradicciones doc↔audit
├─ pricing_compliance: pain_ratio ≤ tier gate_max (floor-aware D1)
└─ coverage_no_silent_drop: brechas_diagnostico + brechas_justificadas == brechas_detectadas

advisory (2) — se divulgan en human_checklist.md, solo degradan a blocking bajo su piso:
├─ content_quality: sin blockers ("COP COP", región "default", "0% confianza")
└─ proposal_asset_alignment: coverage ≥ 0.8

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
# Todas las pruebas (la cifra canonica la imprime el metodo grep; ver §Cobertura por Modulo)
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

### Cobertura por Modulo (4,850 funciones totales)

> **Aqui vive la cifra**: `Estado Actual`, `§Pruebas` y el arbol de estructuras la **referencian**, no la
> re-transcriben. Es un retrato del **arbol de trabajo**, que es lo que mide el comando canonico. La cifra
> **commiteada** se mide sin tocar el arbol, con `git grep -c -E "^\s*def test_" HEAD -- tests`.

> **El historial de rondas** vive en `docs/cobertura-historia.md`: las notas aparcadas alli, en orden
> cronologico descendente, con sus atribuciones por bateria, sus notas de instrumento y sus antecedentes. Cada
> ronda aparca su nota **alli**; en este archivo solo cambian la cifra de la cabecera y la fila de la tabla que le
> corresponde.

| Modulo | Funciones test | Directorio |
|--------|---------------|------------|
| financial_engine | 552 | `tests/financial_engine/` (+3 en la ronda del 2026-10-01: el diente de tres piezas del aislamiento de flags, `test_pricing_resolution_wrapper.py` 36 → 39) |
| asset_generation | 472 | `tests/asset_generation/` |
| quality_gates | 993 | `tests/quality_gates/` (incl. `tribunal/` con los tests del enforcement P2/P3 y la matriz P6-R; +los arneses `decision_client/`, `lesson_relevance/` y `phase_briefing/` de la orden de calidad; +2 en la ronda S31 del 2026-09-27: el control de resolucion del plan anclado a la revision fija `44f53c2` y el control anti-literal de los seis arneses; **+9 en la ronda del 2026-09-28**: 6 en `phase_briefing/test_briefing_proyeccion_workflow_gobernada.py` — la cura de S32, que gobierna por `--check` la proyeccion del workflow y pierde su verde cuando se la apaga — y 3 en `governance_numbers/test_governance_numbers_estados_sin_puntero_d1.py` — la cura de D-A sobre los estados que se delegaban en D1; **+11 en la ronda del 2026-10-03**: los 11 de `jev_pilot/test_jev_pilot_ledger_fase_b.py`, la pata (b) del ledger del piloto JEV — `attempts`, `error_kind` y `usage_normalized` — con su control negativo ejecutado sobre el guard versionado en HEAD, que reproduce el hueco del nombre `typesafe_sdk`; **+54 en la OLA 2 del 2026-10-03**: 14 en `jev_pilot/test_jev_pilot_sdk_ac9.py` (AC9 con el SDK real y `MockTransport`, red bloqueada), 15 en `test_jev_pilot_run_guards.py` (los seis cortes de cero envios del `run`), 10 en `test_jev_pilot_deepseek_brazo.py` (el comparador explicito sin fallback) y 14 en `test_jev_pilot_protocolo_check.py` (los ocho umbrales y la politica de nulos del protocolo), mas 1 en `decision_client/test_decision_client_aislamiento_imports.py` (el contrafactual de la excepcion de cero red); **+4 en la ronda del 2026-10-04 (deuda declarada al cierre de FASE-B)**: 4 en el nuevo `lesson_relevance/test_triage_guard_real_aditividad.py`, el diente de AC6 sobre la **clausula** del guard de `scripts/triage_lesson_relevance.py` (no sobre el simbolo que ya apagan los dientes de AC14), con su mutante en `tmp_path` y su contraste del modulo cargado contra el blob de HEAD; **+5 en la ronda del 2026-10-04 (SESION 2.5, preflight de FASE-C)**: 5 en `jev_pilot/test_jev_pilot_deepseek_brazo.py` (10 → 15), los dientes del id recortado que cura `scripts/proveedores/deepseek.py` — noul, choice del triaje y score con el prefijo perdido, el recorte ambiguo que no se adivina, la prioridad de la coincidencia exacta y el no-relleno por la via nueva — cada uno con su mutante de ocurrencia unica y su restauracion verificada por sha; las diez pruebas previas del archivo quedaron verdes **sin re-anclar ninguna** (medido: ninguna asercion dependia del descarte); **+35 en la ronda del 2026-10-04 (SESION 3.5, FASE-B.2 del piloto JEV)**: 35 en el nuevo `jev_pilot/test_jev_pilot_report_decide_fase_b2.py`, los dientes de CR-1/CR-2/CR-3 — los cuatro cocientes con denominadores separados sobre valores calculados a mano, el denominador cero como NO-EVALUABLE, la abstencion en su columna propia, el fallo del camino dentro del extremo a extremo y fuera de precision, las cuatro etiquetas de `decide` provocadas con protocolos sinteticos, los literales de `run_status` del maestro (:101) y la credencial del SDK por el camino del contrato sin imprimir valor ni longitud — con sus cinco mutantes en `FASE-B2/mutation.json` (M1 a M5, todos caen por la causa nombrada y el arbol intacto por sha). Ademas: `test_jev_pilot_offline.py` conservo sus 7 funciones y **re-ancla** la negacion de `decide` (sin insumos sigue EXIT 2; con insumos offline emite, dentro del mismo guard de imports), y `test_jev_pilot_protocolo_check.py` cerro CR-4 re-anclando el aviso `:43` a `CONGELADA` con diente contrario — 24 verdes donde antes habia 1 failed / 23 passed; **+7 en la ronda del 2026-10-05 (CIERRE-DE-ABANICO, REL-1 del piloto JEV)**: los 7 de `jev_pilot/test_jev_pilot_run_guards.py` (16 a 23), el par verde/rojo del dictado D4 sobre el guard del preflight — la excusa `NO-APLICA` del brazo, que se publica en `no_aplica_declarados`, el diente anclado al `FASE-C/preflight.json` versionado y la comparacion de tipo que deja de tragar un `1` — con sus cuatro mutantes en `FASE-RELEASE/44-mutantes-guard-preflight-crudo.txt` y el arbol intacto por sha. La nota de la ronda, en `docs/cobertura-historia.md`) |
| commercial_documents | 363 | `tests/commercial_documents/` |
| auditors | 226 | `tests/auditors/` (incl. +11 de AC-S1 en P5, +7 de TestGeminiModelFromRegistry en v4.77.1, +5 de TestGeminiCostAccounting en v4.77.2, +1 del contrato no-medible en v4.77.3) |
| geo_enrichment | 140 | `tests/geo_enrichment/` |
| data_validation | 133 | `tests/data_validation/` |
| test_never_block_architecture | 122 | `tests/test_never_block_architecture/` |
| orchestration_v4 | 93 | `tests/orchestration_v4/` |
| delivery | 78 | `tests/delivery/` (+9 de cuarentena O1 en P2) |
| config | 61 | `tests/config/` |
| utils | 60 | `tests/utils/` |
| postprocessors | 52 | `tests/postprocessors/` |
| scrapers | 49 | `tests/scrapers/` |
| common | 38 | `tests/common/` |
| analytics | 33 | `tests/analytics/` |
| regression | 26 | `tests/regression/` |
| e2e | 21 | `tests/e2e/` |
| providers | 18 | `tests/providers/` |
| monitoring | 14 | `tests/monitoring/` |
| archived (no coleccionables) | 220 | `tests/_archived_broken_tests/` |
| root test files | 1086 | `tests/*.py` (integration, harness, data models, multi-hotel P6/P6-R, `functional_test_*`, los validadores de gobernanza, la cura S17/S18 y las cuatro baterias de la orden 2026-09-26: S15, el verificador del arbol del commit, su cura S20 y la cura (b) de S19; mas los dos controles de 2026-09-27 que atan la resolucion del plan archivado a `resolver_plan()` del escritor, el control de la ronda S29 anclado a la **revision fija** `9c4a001` con `git archive`, y los **+3** de la ronda S17 del mismo dia: el quinto escritor `validate_opencode_refs.py` con su `--fix`, su `--write-baseline` y su guard de destino por operaciones observadas — un verde aditivo que sin arbol versionado no tendria oportunidad de perder; **+12 en la ronda del 2026-09-28**: 7 en `test_sync_writers_lf_y_fecha_readme.py` (10 → 17: la forma que promueve `--fix`, el delta EOL contra la forma citada, la cuenta de escritores LF y el ancla del control C7) y 5 nuevas en `test_run_all_validations_denominador_por_modo.py`, la cura de S21 con su [GUARDA] tambien fuera del rapido; **+40 en la ronda del 2026-09-30**: 6 en `test_registry_fecha_documental.py` (14 → 20, la cura de D-F5 con sus rechazos y su forma ISO), 5 en el nuevo `test_verify_packs_quinto_patron_generado_por_sha.py` (S19(d) salida (c)), 17 en el nuevo `test_verify_qmind_context_freshness.py` (S34, con su control negativo contra el hermano versionado) y 12 en el nuevo `test_validate_lesson_capitalization_c9_descripcion_alcance.py` (el sub-punto de S29: gobernar la descripcion del alcance, no solo el alcance); **+31 en la segunda ronda del 2026-09-30**, las tres baterias del wiring: 12 en `test_validate_wiring_alcance_por_declaracion_git.py` (el paso 1, alcance por declaracion de Git, llegado de la tanda anterior), 8 en el nuevo `test_validate_wiring_criterio_en_el_exit.py` (el paso 2: la clausula de produccion en el EXIT, con su control negativo anclado a `abd181c`) y 11 en el nuevo `test_validate_wiring_check_derivado_versionado.py` (el paso 3: `--check` sobre `.opencode/wiring_report.json`, con los tres estados del lector y dos mutantes; **+6 en la ronda del 2026-10-01**: 6 nuevas en `tests/test_hook_precommit_packs_check.py` (0 → 6), la bateria del `[8/8]` del hook pre-commit que entró en `0ff9f25`; **+7 en la segunda ronda del 2026-10-01 (CIERRE-DEUDA)**: +5 en `test_registry_fecha_documental.py` (20 → 25, los dientes de la guarda `--plan` de la fila 15 con su control negativo sobre el escritor versionado en `bb1be59`) y +2 en `test_diagnostic_geo_metrics.py` (3 → 5, el diente de perdida de seccion de la fila 14, que ubica la tabla por el dato y sobrevive un renombre del titulo). Los tres archivos de la ronda, con su instrumento y su contrafactual, en `docs/cobertura-historia.md`; **+1 en la tanda ADOPCION-Y-CIERRE-DEUDA del 2026-10-01**: el diente de delimitadores de la fila 17 del registro 33- en `test_diagnostic_geo_metrics.py` (5 → 6, paridad de pipes y columnas entre cabecera y separador ubicando la tabla por el dato; mutante con ancla unica y `ast.parse`, control de renombre VERDE y control negativo con `git show 7fa8d5c` ejecutado; **+5 en la OLA 2 del 2026-10-03**: 5 en el nuevo `test_validate_wiring_diente_mudanza_1_3.py` (la mudanza (a) de la fila 18: schema 1.3, las dos mitades del diente en una sola corrida). El contrafactual de la excepcion de cero red vive en `tests/quality_gates/decision_client/` y se conto en la fila de quality_gates, no aqui; **+15 en la ronda del 2026-10-04 (deuda declarada al cierre de FASE-B, dos baterias)**: +11 en `test_verify_qmind_context_freshness.py` (17 → 28: la poblacion **declarada** del `10-analisis` del piloto JEV, el recorte de la bajada por prefijo, el NO-EVALUABLE cuando el archivo del plan se mueve y el control negativo **ejecutado** sobre el diente versionado en `6cdb430`, que dava `[OK]` con el cuerpo vencido) y +4 en `test_validate_wiring_alcance_por_declaracion_git.py` (12 → 16: la premisa de disco de la fila 230, su predicado en los dos estados y el control anclado a `4c113de`, que afirma por AST que no se movio ninguna asercion). Nota de ronda en `docs/cobertura-historia.md`; **+8 en la ronda del 2026-10-05 (CIERRE-DE-ABANICO, REL-6 del piloto JEV)**: 28 a 36 en `test_verify_qmind_context_freshness.py`, los dientes del contrato que D2 re-escribe — `metadata.fileSha256`/`fileSize` como primera via, la descarga+sha256 quedando como verificacion de la promesa del servidor, `NO-EVALUABLE` cuando la fuente que casa no baja, `PROMESA-ROTA` cuando el indice desmiente a lo que baja y el rojo mandando sobre la abstencion — con sus seis mutantes en `FASE-RELEASE/47-mutantes-contrato-frescura-crudo.txt` y **dos aserciones re-ancladas** por el contrato nuevo: `descargas` de 2 a 1 en `test_la_forma_original_mas_cierre_es_legal` y la ruta en `test_un_titulo_sin_prefijo_tambien_se_examina_por_bytes`, ambas con su justificacion escrita dentro del test y la ruta de barrido cubierta por la nueva `test_sin_metadata_publicada_el_camino_de_descarga_sigue_vivo`) |

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
│   │   ├── human_checklist_generator.py
│   │   └── tribunal/           # Juez P6 + acta dual + 4 revisores
│   │       ├── judge.py
│   │       ├── acta_writer.py
│   │       ├── artifact_paths.py
│   │       ├── llm_extractor.py
│   │       ├── diagnosis_reviewer.py   # Bot 1 — P6.1
│   │       ├── alignment_reviewer.py   # Bot 2 — P6.2
│   │       ├── asset_reviewer.py       # Bot 3 — P6.3/P6.4
│   │       └── honesty_reviewer.py     # Bot 4 — P6.5
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
├── tests/                      # Suite de pruebas (su cifra vive en §Cobertura por Modulo)
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
