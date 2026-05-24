# Contexto: AGENTS.md Desactualizado — Diagnóstico y Soluciones (v4 CORREGIDA)

**Creado:** 2026-05-26
**Revisado:** 2026-05-26 — v4: corrección de inventario data_validation/ (invertido en v3), scripts pendientes confirmados, test files 192→211 confirmado, Solución 1 ampliada a 9 pasos con riesgo Medio
**Proyecto:** iah-cli
**Versión actual:** v4.48.0 (PIPELINE-FIX)
**Archivo evaluado:** `AGENTS.md` (header: v4.48.0, body: pre-FASE-0)
**Ubicación:** `.opencode/context/AGENTSMD-DRIFT-CONTEXT.md`

---

## Resumen ejecutivo

`AGENTS.md` tiene el header sincronizado (v4.48.0) pero el cuerpo tiene **drift factual en 4 secciones**. La causa raíz es confirmada: `version-sync` actualiza headers pero no audita contenido del body. Tres fases delivery se ejecutaron sin que el cuerpo se actualizara.

**Corrección crítica vs versiones anteriores:** La validación exhaustiva (incluyendo `ls` directo en WSL ya que `find` falla silenciosamente en este entorno) confirma que **todos los componentes de FASE-0 existen en código** — `pain_ledger.py`, `delivery_quality_report.py`, `human_checklist_generator.py`, `data_derivation_layer.py`, `validate_document_integration.py`. El problema no es que no existan, sino que **AGENTS.md no los menciona en su flujo ni en su tabla de módulos**, mientras que ROADMAP.md (L321-370) sí los documenta exhaustivamente con paths exactos.

Además, ROADMAP.md §FASE A-01 (L377) ya planifica explícitamente: "`AGENTS.md` auditado como contexto primario agente". Este contexto es el insumo directo para esa fase.

---

## Hallazgos detallados (validados contra código vivo, ROADMAP y CONTRIBUTING)

### 1. Conteo de tests desincronizado

| Campo | AGENTS.md | pytest real (2026-05-26) | Delta |
|-------|-----------|--------------------------|-------|
| Test functions | 2,491 (L123, L365, L380, L457) | 2,743 | +252 |
| Archivos | 192 | 211 | +19 (drift no documentado en AGENTS.md) |
| Bloqueante | "Ninguno" | — | No verificado |

**Severidad:** Baja.

---

### 2. Módulos de FASE-0 existentes pero ausentes en AGENTS.md

AGENTS.md §Flujo de Trabajo v4 (L210-269) cubre FASE 1 a 4.7 pero omite TODOS los componentes entregados en FASE-0 (2026-05-13). **Los componentes SÍ existen en código** y ROADMAP.md (L321-341) los documenta:

| Componente | Path real | Evidencia ROADMAP | ¿En AGENTS.md? |
|------------|-----------|-------------------|----------------|
| `pain_ledger` | `modules/asset_generation/pain_ledger.py` | ROADMAP L329: "100% pains trazables" | **No** (0 menciones) |
| `delivery_quality_report` | `modules/quality_gates/delivery_quality_report.py` (408 líneas) | ROADMAP L332: "QA post-generación; FAIL bloquea ZIP; 10 tests" | **No** (0 menciones) |
| `human_checklist` | `modules/quality_gates/human_checklist_generator.py` (147 líneas) | ROADMAP L333: "≤10 items derivados automáticamente" | **No** (0 menciones) |
| `data_derivation_layer` | `modules/asset_generation/data_derivation_layer.py` (350 líneas) | ROADMAP L334: "5 derivaciones del audit + scoring semántico; 26 tests" | **No** (0 menciones) |

**Severidad:** Alta. El agente que use AGENTS.md no sabrá que FASE-0 existe pese a que ROADMAP lo declara COMPLETADO y el código está desplegado.

---

### 3. Gates de PIPELINE-FIX existentes pero AGENTS.md dice "9 gates"

AGENTS.md L198: `"9 publication gates (6 blocking... 3 advisory...)"`

`publication_gates.py` L157-169 define **11 gates**:
```
hard_contradictions, evidence_coverage, financial_validity, coherence,
critical_recall, ethics, content_quality, asset_confidence,
proposal_asset_alignment, tier_c_onboarding_required, coverage
```

ROADMAP.md L304-311 tiene la **tabla de mapeo** de los 4 grupos conceptuales a los 11 gates reales, confirmando que PIPELINE-FIX subsanó este gap documental en ROADMAP pero AGENTS.md nunca se actualizó.

**Severidad:** Alta — dato numérico objetivamente falso.

---

### 4. Módulos de fases futuras correctamente etiquetados

| Módulo | AGENTS.md | Veredicto |
|--------|-----------|-----------|
| `opportunity_scorer.py` | L175: `"(FASE-C)"` | ✅ Ya etiquetado |
| `local_content_generator.py` | L180: `"(FASE-E)"` | ✅ Ya etiquetado |
| `voice_readiness_proxy.py` | L185: `"(FASE-E)"` | ✅ Ya etiquetado |

**Severidad:** Baja — AGENTS.md ya hace lo correcto aquí.

---

### 5. `evidence_ledger.py` — deprecado pero listado como activo

AGENTS.md L168 y L418 referencian `evidence_ledger.py` en data_validation.

**Realidad:** Solo existe en `archives/deprecated_modules_20260304/evidence_ledger.py`. Fue reemplazado por `pain_ledger.py`. ROADMAP no lo menciona.

**Severidad:** Media — referencia a módulo que ya no está en producción.

---

### 6. Estructura data_validation duplicada

Dos directorios `data_validation/` coexisten:

- `data_validation/` (raíz): `consistency_checker.py`, `contradiction_engine.py`, `metadata_validator.py`
- `modules/data_validation/`: `confidence_taxonomy.py`, `cross_validator.py`, `metadata_validator.py`, `schema_validator_v2.py`, `external_apis/`

Ambos son importados activamente (`main.py:2801` → raíz para `ConsistencyChecker`; `main.py:1444`, `v4_comprehensive.py:23`, `site_presence_checker.py:49` → `modules/data_validation/` para `CrossValidator`, `ConfidenceLevel`, `RichResultsClient`). AGENTS.md §Estructura (L417-422) lista archivos de ambos directorios bajo una sola entrada `data_validation/`, referencia `evidence_ledger.py` (deprecado), y no muestra `modules/data_validation/` en el árbol de modules (L438-456). Adicionalmente, AGENTS.md omite por completo `confidence_taxonomy.py` y `cross_validator.py` (ambos activos e importados), y referencia `schema_validator_v2.py` bajo `data_validation/` cuando realmente está en `modules/data_validation/`.

**Severidad:** Media — riesgo de confusión en rutas de importación para agentes.

---

### 7. Scripts referenciados en AGENTS.md — todos existen

| Script | AGENTS.md ref | Existencia | Tamaño |
|--------|--------------|------------|--------|
| `run_all_validations.py` | L28-29 | ✅ `scripts/run_all_validations.py` | 14,324 bytes |
| `doctor.py` | L30 | ✅ `scripts/doctor.py` | 25,188 bytes |
| `validate_agent_ecosystem.py` | L31 | ✅ `scripts/validate_agent_ecosystem.py` | 9,889 bytes |
| `validate_document_integration.py` | L113 | ✅ `scripts/validate_document_integration.py` | 21,908 bytes |
| `log_phase_completion.py` | L83 | ✅ `scripts/log_phase_completion.py` | 30,295 bytes |
| `sync_versions.py` | L86 | ✅ `scripts/sync_versions.py` | 9,754 bytes |

CONTRIBUTING.md L349 confirma que `validate_document_integration.py` fue parcheado el 2026-05-14 (encoding fix). **Todos los scripts referenciados en AGENTS.md existen.**

**Severidad:** Nula para scripts — todos los verificados existen.

---

### 8. CHANGELOG y VERSION en sinc

CHANGELOG.md: `## [4.48.0] - PIPELINE-FIX — Assessment Dict Bridge + delivery_ready Formula — 2026-05-23`
VERSION.yaml: `version: "4.48.0"`

Sin drift. El sistema `version-sync` funciona para headers.

---

### 9. v4_complete.md timestamp

`v4_complete.md`: Apr 25 11:39 (PRE-FASE-0, que fue 2026-05-13). Los demás workflows: Apr 5 20:59.

---

## Lo que NO es un problema (descartado tras validación)

| Claim original | Veredicto | Evidencia |
|---------------|-----------|-----------|
| "validate_agent_ecosystem.py NO EXISTE" | ❌ Falso — existe | `ls scripts/validate_agent_ecosystem.py` → 9,889 bytes |
| "validate_document_integration.py NO EXISTE" | ❌ Falso — existe | `ls scripts/validate_document_integration.py` → 21,908 bytes; CONTRIBUTING.md L349 confirma parche |
| "delivery_quality_report no encontrado" | ❌ Falso — existe | `modules/quality_gates/delivery_quality_report.py`, 408 líneas |
| "human_checklist no encontrado" | ❌ Falso — existe | `modules/quality_gates/human_checklist_generator.py`, 147 líneas |
| "data_derivation_layer no encontrado" | ❌ Falso — existe | `modules/asset_generation/data_derivation_layer.py`, 350 líneas |
| "data_validation/ solo en raíz" | ❌ Falso — existe en ambos | `ls -d data_validation/ modules/data_validation/` |
| "módulos FASE-C/E presentados como activos" | ❌ Engañoso — ya etiquetados | AGENTS.md L175, L180, L185 |

---

## Causa raíz (confirmada y refinada)

### Gap estructural

```
version-sync hook:
  VERSION.yaml → AGENTS.md header (✓ actualizado)
              → AGENTS.md body (✗ SIN AUDITAR)
```

### El problema real: AGENTS.md desacoplado de ROADMAP

ROADMAP.md documenta exhaustivamente FASE-0 (L321-341) y PIPELINE-FIX (L343-369) con paths, entregables y E2E verificaciones. AGENTS.md no refleja nada de esto. El problema no es que falte código — el código existe y ROADMAP lo referencia. El problema es que **AGENTS.md y ROADMAP.md divergieron**: ROADMAP se actualizó en PIPELINE-FIX (incluyendo la tabla de mapeo 4→11 gates en L304-311), AGENTS.md no.

### 4 secciones con drift en AGENTS.md

| Sección | Dato stale | Valor real |
|---------|-----------|------------|
| §Estado Actual (L123) | 2,491 tests | 2,743 |
| §Estado Actual (L123) | 192 archivos | 211 |
| §Módulos Activos (L198) | "9 publication gates" | 11 |
| §Módulos Activos (L168, L175-180) | Omite pain_ledger, delivery_quality_report, human_checklist, data_derivation_layer | Existen en código |
| §Flujo v4 (L210-269) | Omite FASE-0 completa | ROADMAP L321-341 |
| §Flujo v4 (L249-255) | Omite coverage y tier_c_onboarding gates | publication_gates.py L157-169 |
| §Estructura (L418) | evidence_ledger.py listado | Deprecado en archives/ |
| §Estructura (L438-456) | Omite `modules/data_validation/` y `confidence_taxonomy.py`, `cross_validator.py` | Existen y son activamente importados |
| §Estructura (L417-422) | `schema_validator_v2.py` bajo `data_validation/` | Está en `modules/data_validation/` |

---

## Implicaciones de ROADMAP.md para este contexto

ROADMAP.md §7 (L319-379) revela que:

1. **FASE 0 está COMPLETADA** (2026-05-13) con 8 sub-fases (0A-0H) + RELEASE. Evidencia: `.opencode/plans/FASE-0-DELIVERY-QUALITY/`
2. **FASE A-01** (L377) planifica explícitamente: `"AGENTS.md auditado como contexto primario agente. Zona esencial clara, rutas correctas, sin ruido excesivo"`. Este contexto document es el insumo para ejecutar FASE A-01.
3. **PIPELINE-FIX** subsanó el gap de documentación de gates en ROADMAP (tabla L304-311: 4 grupos → 11 gates) pero AGENTS.md quedó fuera del alcance.
4. **NUEVO-8** (ROADMAP L369): "AssessmentBuilder centralizado — sesión futura dedicada, NO parte de este plan." Pendiente conocido, no relacionado con AGENTS.md drift.
5. **G0 pendiente**: "requiere PASS completo (todos los assets ≥0.8 confidence) para considerar cerrado el primer piso" (ROADMAP L341). Depende de datos de onboarding, no de código.

---

## Implicaciones de CONTRIBUTING.md

1. **AGENTS.md es auto-sync solo para header** (L133, L255): confirmado. El body es manual.
2. **Flujo post-fase obligatorio** (L39-52): ejecuta `log_phase_completion.py` + verifica docs manuales. AGENTS.md NO está en ese flujo — es un vacío contractual.
3. **Tabla de archivos** (L130-144): AGENTS.md está en "Auto-sync desde VERSION.yaml" para header, pero el body no tiene mecanismo.
4. **validate_document_integration.py** fue parcheado para encoding (L349) — existe y es funcional.
5. **ROADMAP.md es MANUAL** (L142): "solo si el usuario dice específicamente que actualizar Roadmap". Esto explica por qué ROADMAP sí se actualizó (fue explícito en PIPELINE-FIX) pero AGENTS.md no.

---

## Soluciones propuestas

### Solución 1: Corrección one-shot (9 pasos)

**Qué:** Editar AGENTS.md manualmente para reflejar el estado actual documentado en ROADMAP.

**Pasos:**
1. Actualizar conteo de tests en 5 ubicaciones (L123, L365, L380, L457, tabla cobertura):
   - 2,491 → **2,743** funciones
   - 192 → **211** archivos
2. Actualizar "9 publication gates" → **"11 publication gates"** con lista actualizada (L198)
3. Insertar en §Flujo v4 (post FASE 4.7):
   ```
   FASE 5: DELIVERY QUALITY (FASE-0)
   ─────────────────────────────────
   ├─ pain_ledger: trazabilidad pain_id → fuente → severidad → asset
   ├─ coverage gate (G7): brechas_diagnóstico + brechas_justificadas == brechas_detectadas
   ├─ tier_c_onboarding_required gate: assessment dict injection
   ├─ delivery_quality_report: QA post-generación bloqueante
   ├─ human_checklist: ≤10 items derivados automáticamente
   └─ data_derivation_layer: 5 derivaciones semánticas del audit
   ```
4. Agregar a §Módulos Activos: `pain_ledger`, `delivery_quality_report`, `human_checklist_generator`, `data_derivation_layer` con paths correctos
5. Marcar `evidence_ledger.py` como **DEPRECADO** → `archives/deprecated_modules_20260304/` (L168, L418). Remover del árbol `data_validation/` en §Estructura.
6. Reorganizar §Estructura de Archivos:
   - Corregir árbol `data_validation/` (raíz): solo `consistency_checker.py`, `contradiction_engine.py`, `metadata_validator.py`
   - Agregar `modules/data_validation/` al árbol de modules (L438-456): `confidence_taxonomy.py`, `cross_validator.py`, `metadata_validator.py`, `schema_validator_v2.py`, `external_apis/`
   - Mover `schema_validator_v2.py` de `data_validation/` a `modules/data_validation/` en el árbol
7. Verificar etiquetas FASE-C/FASE-E existentes — ya correctas
8. Agregar `confidence_taxonomy.py` y `cross_validator.py` a §Módulos Activos (son activamente importados por `main.py` y `v4_comprehensive.py`)
9. Sincronizar versión y fecha con ROADMAP: agregar referencia a FASE-0 y PIPELINE-FIX como completados

**Esfuerzo:** ~60 minutos (9 pasos, +2 vs v3 original)
**Riesgo:** Medio — requiere precisión en rutas de `data_validation/` vs `modules/data_validation/` (validado con `ls` 2026-05-26)
**Efecto:** Inmediato pero temporal

---

### Solución 2: Gate de coherencia automatizado

**Qué:** Crear `scripts/validate_agents_md.py` que audite AGENTS.md contra código vivo + ROADMAP.

**Checks obligatorios:**
1. Módulos citados en AGENTS.md existen en las rutas especificadas (`os.path.exists`)
2. Conteo de tests: `pytest --collect-only -q` vs AGENTS.md (tolerancia ±5%)
3. Conteo de gates: `len(gates)` en publication_gates.py vs AGENTS.md
4. Componentes FASE-0 listados en ROADMAP aparecen en AGENTS.md §Flujo y §Módulos
5. Módulos en `archives/deprecated_*` NO aparecen como activos en AGENTS.md
6. Scripts referenciados en §Validaciones existen en `scripts/`

**Ubicación:** `scripts/validate_agents_md.py`
**Integración:** pre-commit hook `agent-ecosystem`

**Esfuerzo:** ~3 horas
**Riesgo:** Muy bajo

---

### Solución 3: AGENTS.md generativo (largo plazo)

**Qué:** `scripts/generate_agents_md.py` que regenere secciones factuales desde código vivo. Secciones narrativas (Flujo, Criterios de Éxito) permanecen como plantillas mantenidas manualmente.

**Esfuerzo:** ~6-8 horas
**Riesgo:** Medio

---

### Solución 4: Agregar AGENTS.md al flujo post-fase

**Qué:** Incluir `validate_agents_md.py` en el flujo documental obligatorio de CONTRIBUTING.md (entre Paso 5 y Paso 6).

**Dependencia:** Solución 2 implementada.

**Esfuerzo:** ~30 minutos (editar CONTRIBUTING.md)
**Riesgo:** Muy bajo

---

## Interdependencias

```
Solución 1 (one-shot, 8 pasos)
    └── Ejecutable inmediatamente
        │
        ├── Solución 2 (validate_agents_md.py) ← independiente
        │       └── Solución 4 (proceso post-fase)
        │
        └── Solución 3 (generativo) ← excluyente con Solución 2
```

**Recomendación:** Solución 1 + Solución 2 + Solución 4. ROADMAP ya planifica FASE A-01 para esto.

---

## Relación con ROADMAP.md

Este contexto es el **insumo directo para FASE A-01** del ROADMAP (L377):
> "`AGENTS.md` auditado como contexto primario agente. Zona esencial clara, rutas correctas, sin ruido excesivo."

FASE A-01 es parte de "FASE A: Baseline de robustez agente (1-2 semanas)" que ROADMAP prioriza después de completar FASE 0 (primer piso) y PIPELINE-FIX. La secuencia natural es:
1. Ejecutar Solución 1 (corrección one-shot de AGENTS.md) → cierra el drift actual
2. Ejecutar Solución 2 + 4 → previene drift futuro
3. Marcar FASE A-01 como completada en ROADMAP

---

## Archivos del plan

| Archivo | Contenido |
|---------|-----------|
| `AGENTSMD-DRIFT-CONTEXT.md` | Este documento (v3) |

---

## Referencias cruzadas

| Archivo | Sección | Dato clave |
|---------|---------|------------|
| `AGENTS.md` | 4 secciones con drift | Header OK, body pre-FASE-0 |
| `ROADMAP.md` | L321-341 (FASE 0), L343-369 (PIPELINE-FIX), L377 (FASE A-01) | Documenta todo lo que AGENTS.md omite |
| `CONTRIBUTING.md` | L39-52 (flujo post-fase), L130-144 (tabla archivos), L349 (validate_document_integration) | AGENTS.md body es manual, sin mecanismo |
| `VERSION.yaml` | v4.48.0 | En sinc con CHANGELOG |
| `publication_gates.py` | L157-169 (11 gates) | AGENTS.md dice 9 |
| `pain_ledger.py` | `modules/asset_generation/` | 0 menciones en AGENTS.md |
| `delivery_quality_report.py` | `modules/quality_gates/` (408 líneas) | 0 menciones en AGENTS.md |
| `human_checklist_generator.py` | `modules/quality_gates/` (147 líneas) | 0 menciones en AGENTS.md |
| `data_derivation_layer.py` | `modules/asset_generation/` (350 líneas) | 0 menciones en AGENTS.md |
| `validate_document_integration.py` | `scripts/` (21,908 bytes) | Existe. AGENTS.md L113 OK |
| `validate_agent_ecosystem.py` | `scripts/` (9,889 bytes) | Existe. AGENTS.md L31 OK |
| `evidence_ledger.py` | `archives/deprecated_modules_20260304/` | DEPRECADO. AGENTS.md L168, L418 stale |
| `.agents/workflows/phased_project_executor.md` | R3 scope, 60 iteraciones, fases | Marco para el plan de implementación |

---

## Prompt para diseñar el plan de implementación (próxima sesión)

```
Carga .opencode/context/AGENTSMD-DRIFT-CONTEXT.md (v3 definitiva, validada 2026-05-26).
También carga ROADMAP.md §7 (FASE 0, PIPELINE-FIX, FASE A).
Diseña un plan de implementación por fases siguiendo phased_project_executor.md.
Alcance: Solución 1 (8 pasos) + Solución 2 (validate_agents_md.py) + Solución 4 (proceso post-fase).
Este plan ejecuta FASE A-01 del ROADMAP (AGENTS.md auditado como contexto primario agente).
NO implementar aún — solo diseñar fases con R3 scope, dependencias y prompts.
```
