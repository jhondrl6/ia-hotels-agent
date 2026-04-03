<!-- agents_version: 4.19.0 | last_update: 2026-04-03 -->

# IA Hoteles Agent (iah-cli)

> **v4.19.0 -- Agent Ecosystem Integration COMPLETADO**
> PLAN ANALYTICS-E2E-BRIDGE 100%: Analytics Transparency → Proposal Generator → Asset Bridge via PainSolutionMapper. Coherence score 0.84 (>= 0.8), PainSolutionMapper con 3 pain types analytics, 2 nuevos assets con templates.

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
- Zona Esencial (primeras ~120 líneas): operativo inmediato.
- Zona Referencia (resto): contexto histórico y validaciones.
- Cambios: editar aquí primero, validar después.

**Validaciones**: 
```bash
python scripts/run_all_validations.py --quick
python scripts/run_all_validations.py
```

---

## Gobernanza de Documentacion y Ejecucion

### Conexiones Clave

| Archivo | Proposito | Relacion |
|---------|-----------|----------|
| `docs/CONTRIBUTING.md` | Reglas de documentacion y mantenimiento | Index → fragmentos |
| `docs/contributing/documentation_rules.md` | Checklist docs obligatorias | Referenciado por executor |
| `docs/contributing/REGISTRY.md` | Registro auto de fases completadas | Actualizado por executor |
| `.agents/workflows/phased_project_executor.md` | Motor de ejecucion por fases | Ejecuta → documenta |
| `.agent/CONVENTION.md` | Contrato arquitectura ecosistema agentes | `.agent/` ↔ `.agents/` |
| `.agent/SYSTEM_STATUS.md` | Dashboard auto-regenerable | `main.py --doctor --status` |

### Flujo Post-Fase

Cuando se ejecuta `phased_project_executor.md`:

```
FASE completada
    │
    └── Paso 6: Documentacion Post-Fase
        ├── Lee documentation_rules.md para checklist
        ├── Ejecuta: python scripts/log_phase_completion.py --fase N
        │   ├── Registra en REGISTRY.md (auto)
        │   └── Muestra POR_HACER para docs manuales
        └── Verifica capability contracts
```

### Version y Sincronizacion

Archivos sincronizados automaticamente desde VERSION.yaml (pre-commit):
- `AGENTS.md`, `README.md`, `.cursorrules`
- `docs/CONTRIBUTING.md`, `docs/GUIA_TECNICA.md`, `docs/contributing/REGISTRY.md`

Regenerable (1 comando):
- `.agent/SYSTEM_STATUS.md` → `python main.py --doctor --status`

Documentacion que se actualiza **manualmente** segun CONTRIBUTING.md:
- `CHANGELOG.md`, `GUIA_TECNICA.md`, `ROADMAP.md`
- `INDICE_DOCUMENTACION.md`, `.agents/workflows/README.md`

### Flujo de Actualizacion de Documentacion

**Automatico (pre-commit en cada commit):**
- Version sync VERSION.yaml → 6 archivos
- Agent ecosystem check (8 validaciones)

**Regenerable (1 comando):**
- `.agent/SYSTEM_STATUS.md` → `python main.py --doctor --status`

**Manual (requiere agente):**
- `CHANGELOG.md`, `INDICE_DOCUMENTACION.md`, `documentation_rules.md`

**Prompt:** "Actualizar documentacion oficial del repositorio"

---

## Estado Actual

| Aspecto | Estado |
|---------|--------|
| **Version** | v4.19.0 |
| **Codename** | Agent Ecosystem Integration |
| **Piloto Activo** | Hotel Visperas (testeado) |
| **Tests** | 1700+ test functions, 52/52 regression suite |
| **Bloqueante** | Ninguno |
| **Coherence Score** | ✅ 0.84 (umbral: 0.8) - PASA el gate |
| **Publication Ready** | ✅ true |
| **Mejoras** | TDD Gate, Parallel Execution, FAQGenerator, GA4 Multi-Hotel, **Doctor CLI**, **Pre-commit ecosystem validation**, **v4_quality_validator unificado** |

---

## Comandos CLI

| Comando | Estado | Descripción |
|---------|--------|-------------|
| `v4complete` | ✅ Recomendado | Flujo completo: diagnóstico, propuesta, assets, coherencia |
| `v4audit` | ✅ Funcional | Auditoría con APIs externas (Rich Results, Places, PageSpeed) |
| `spark` | ⚠️ Deprecado | Legacy, usar `v4complete` |
| `execute` | ✅ Funcional | Implementa paquete, recupera análisis v4.0 con coherence ≥ 0.8 |
| `stage` | ✅ Funcional | Ejecuta etapas individuales (geo, ia, seo, outputs) |
| `deploy` | ✅ Funcional | Despliegue remoto via FTP/WP-API |
| `setup` | ✅ Funcional | Configuración interactiva de API keys |
| `onboard` | ✅ Funcional | Captura datos operativos del hotel |
| `--doctor` | ✅ Nuevo v4.19.0 | Diagnóstico del ecosistema de agentes |
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
| `financial_engine/` | Escenarios: conservador/realista/optimista | v4audit, v4complete |
| `financial_engine/calculator_v2.py` | FinancialCalculatorV2 con validación | v4complete |
| `orchestration_v4/` | Flujo dos fases: Hook → Validación | v4complete |
| `asset_generation/` | Generación condicional con gates | v4complete |
| `modules/asset_generation/asset_catalog.py` | Catálogo centralizado de assets con is_asset_implemented | v4complete |
| `auditors/` | APIs externas (Rich Results, Places, PageSpeed) | v4audit, v4complete |
| `modules/auditors/ai_crawler_auditor.py` | Auditoría de robots.txt para IA crawlers | v4audit, v4complete |
| `modules/analytics/google_analytics_client.py` | Cliente GA4 para tráfico indirecto (Método #5 KB) | v4audit (ADVISORY) |
| `modules/asset_generation/llmstxt_generator.py` | Generación de llms.txt estándar | v4complete, execute |
| `modules/auditors/citability_scorer.py` | Score de citabilidad de contenido | v4audit (ADVISORY) |
| `modules/auditors/ia_readiness_calculator.py` | Score compuesto IA-readiness | v4audit (ADVISORY) |
| `commercial_documents/` | Diagnóstico, propuesta, coherencia | v4complete |
| `financial_engine/harness_handlers.py` | Handlers para Agent Harness | v4complete |
| `agent_harness/` | Memoria, auto-corrección, routing | Todos los comandos |
| `observability/dashboard.py` | Métricas y tendencias de calidad | v4.3.0 |
| `observability/calibration.py` | Calibración de umbrales de confianza | v4.3.0 |
| `tests/regression/` | Suite de regresión permanente | CI/CD |
| `data_models/` | Modelos: CanonicalAssessment, Claim, Evidence | v4complete, v4audit |
| `modules/quality_gates/` | Gates técnico, comercial, financiero, coherencia, publicación | v4complete |
| `modules/financial_engine/no_defaults_validator.py` | Validación "No Defaults in Money" | v4complete |
| `commercial_documents/composer.py` | Generación determinística de documentos | v4complete |
| `commercial_documents/coherence_validator.py` | Validador de coherencia con promised_assets_exist | v4complete |
| `enums/` | Enumeraciones: Severity, ConfidenceLevel | Todos |
| `data_validation/evidence_ledger.py` | Almacén centralizado de evidencia | v4complete, v4audit |
| `data_validation/contradiction_engine.py` | Detección de hard/soft conflicts | v4complete |
| `data_validation/schema_validator_v2.py` | Coverage scoring | v4audit |

---

## Flujo de Trabajo v4.1.0

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

<!--
══════════════════════════════════════════════════════════════
ZONA REFERENCIA - Solo si es necesario para contexto profundo
══════════════════════════════════════════════════════════════
-->

## Contexto del Modelo v4.0

### Transformación Fundamental

De "generador de diagnósticos" a "sistema de inteligencia con niveles de certeza explícitos".

### Problemas Resueltos v3.9 → v4.0

| Problema v3.9 | Solución v4.0 |
|---------------|---------------|
| WhatsApp falso en assets | Validación cruzada web+GBP+input |
| 50 FAQs → 18 (inconsistencia) | Preflight check + nombre honesto |
| 3 cifras diferentes | Escenarios únicos con probabilidades |
| Performance Score inventado | PageSpeed API real |
| Sin detección de conflictos | Bloqueo automático con reporte |

---

## Arquitectura v4.3

### Flujo de Datos
```
URL → Validadores → Canonical Assessment → Contradiction Engine → Gates → Document Composer → Publication State
```

### Cambios Breaking v4.2 → v4.3
- Nuevo formato `CanonicalAssessment` (reemplaza assessment v4.2)
- Estados de publicación obligatorios (READY_FOR_CLIENT, DRAFT_INTERNAL, REQUIRES_REVIEW)
- Bloqueo financiero con defaults (No Defaults in Money)
- Coherence < 0.8 bloquea certificado

---

## Pruebas

```bash
# Todas las pruebas (1261 tests)
python -m pytest tests/ -v

# Solo módulos v4.0
python -m pytest tests/data_validation tests/financial_engine \
                  tests/orchestration_v4 tests/asset_generation -v

# Validaciones de coherencia
python scripts/run_all_validations.py --quick  # Rápido
python scripts/run_all_validations.py           # Completo
```

### Cobertura por Módulo

| Módulo | Tests | Directorio |
|--------|-------|------------|
| data_validation | ~20 | `tests/data_validation/` |
| financial_engine | ~15 | `tests/financial_engine/` |
| orchestration_v4 | ~10 | `tests/orchestration_v4/` |
| asset_generation | ~25 | `tests/asset_generation/` |
| commercial_documents | ~8 | `tests/test_commercial_documents*.py` |
| Agent Harness | ~30 | `tests/test_harness_*.py` |
| data_models | ~15 | `tests/test_data_models*.py` |
| quality_gates | ~12 | `tests/test_quality_gates*.py` |
| observability | ~8 | `tests/test_observability*.py` |

---

## Estructura de Archivos v4.3

```
ih-cli/
├── data_models/              # Modelos de datos Pydantic
│   ├── canonical_assessment.py
│   ├── claim.py
│   └── evidence.py
├── data_validation/          # Validación cruzada
│   ├── evidence_ledger.py
│   ├── contradiction_engine.py
│   ├── consistency_checker.py
│   ├── metadata_validator.py
│   └── schema_validator_v2.py
├── modules/quality_gates/    # Quality gates
│   ├── domain_gates.py
│   ├── coherence_gate.py
│   ├── publication_gates.py
│   └── publication_state.py
├── modules/financial_engine/ # Motor financiero
│   ├── no_defaults_validator.py
│   └── calculator_v2.py
├── observability/            # Dashboard y calibración
│   ├── dashboard.py
│   └── calibration.py
├── enums/                    # Enumeraciones
│   ├── severity.py
│   └── confidence_level.py
└── tests/regression/         # Suite de regresión
    └── test_hotel_visperas.py
```
