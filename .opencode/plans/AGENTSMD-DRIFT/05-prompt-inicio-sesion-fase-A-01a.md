# 05-prompt-inicio-sesion-fase-A-01a

**Fase:** A-01a — Corrección one-shot AGENTS.md (Solución 1)
**Plan:** AGENTSMD-DRIFT
**Sesión:** Nueva (fresh)
**Iteraciones máx:** 60
**Depende de:** —
**Bloquea a:** FASE-A-01b

## Objetivo

Corregir el drift factual en `AGENTS.md` aplicando los 9 pasos de la Solución 1 documentados en `.opencode/context/AGENTSMD-DRIFT-CONTEXT.md`. AGENTS.md tiene 4 secciones con datos stale que deben sincronizarse con la realidad del código vivo y ROADMAP.md.

## Contexto

- **Versión actual:** v4.48.0 (PIPELINE-FIX)
- **AGENTS.md header:** sincronizado (gracias a version-sync)
- **AGENTS.md body:** pre-FASE-0 — omite pain_ledger, delivery_quality_report, human_checklist, data_derivation_layer; dice "9 gates" cuando son 11; referencia evidence_ledger deprecado; estructura data_validation duplicada no reflejada.
- **ROADMAP.md L321-341:** documenta FASE-0 exhaustivamente (paths, entregables, E2E)
- **ROADMAP.md L304-311:** tabla de mapeo 4 grupos → 11 gates
- **ROADMAP.md L377:** FASE A-01 planifica explícitamente "AGENTS.md auditado como contexto primario agente"

## Verificaciones previas (ya hechas en la etapa de planificación)

- ✅ pytest real: **2,743** test functions (AGENTS.md dice 2,491)
- ✅ 211 archivos de test (AGENTS.md dice 192)
- ✅ `modules/quality_gates/publication_gates.py:157-169`: **11 gates** (AGENTS.md dice 9)
- ✅ pain_ledger, delivery_quality_report, human_checklist_generator, data_derivation_layer: existen en código
- ✅ evidence_ledger: solo en `archives/deprecated_modules_20260304/`
- ✅ `data_validation/` (raíz): consistency_checker, contradiction_engine, metadata_validator
- ✅ `modules/data_validation/`: confidence_taxonomy, cross_validator, metadata_validator, schema_validator_v2, external_apis/

## Tareas

### T1: Investigar secciones exactas a editar en AGENTS.md

Cargar AGENTS.md completo y localizar TODAS las líneas que requieren cambio:

1. L123: `2491 funciones, 192 archivos` → actualizar a 2743, 211
2. L168: `evidence_ledger.py` — marcar como DEPRECADO o remover
3. L198: `9 publication gates (6 blocking... 3 advisory...)` → 11 gates con lista correcta
4. L249-255: §Flujo v4 — insertar FASE-5 (DELIVERY QUALITY / FASE-0)
5. L365: `2491 funciones`
6. L380: `2491 funciones totales`
7. L418: `evidence_ledger.py` en árbol data_validation
8. L438-456: árbol modules — falta `modules/data_validation/`
9. L457: `2491 funciones, 192 archivos`
10. Tabla de Módulos Activos (L140-200): falta pain_ledger, delivery_quality_report, human_checklist_generator, data_derivation_layer, confidence_taxonomy, cross_validator

Crear una lista numerada de ediciones con old_text → new_text para cada una.

### T2: Aplicar los 9 pasos de corrección

Ejecutar las ediciones en orden usando `patch` (mode='replace'):

**Paso 1:** Actualizar conteo de tests en 5 ubicaciones (L123, L365, L380, L457, y tabla cobertura):
- 2,491 → **2,743** funciones
- 192 → **211** archivos

**Paso 2:** Actualizar "9 publication gates" → **"11 publication gates"** con lista real (L198):
```
11 publication gates (6 blocking: hard_contradictions, evidence_coverage, financial_validity, coherence, critical_recall, ethics; 3 advisory: content_quality, asset_confidence, proposal_asset_alignment; 2 quality: tier_c_onboarding_required, coverage)
```

**Paso 3:** Insertar en §Flujo v4 (después de FASE 4.7) la FASE 5: DELIVERY QUALITY:
```
FASE 5: DELIVERY QUALITY (FASE-0)
─────────────────────────────────
├─ pain_ledger: trazabilidad pain_id → fuente → severidad → asset
├─ coverage gate (G7): brechas_diagnóstico + brechas_justificadas == brechas_detectadas
├─ tier_c_onboarding_required gate: assessment dict injection
├─ delivery_quality_report: QA post-generación bloqueante (408 líneas, 10 tests)
├─ human_checklist: ≤10 items derivados automáticamente
└─ data_derivation_layer: 5 derivaciones semánticas del audit
```

**Paso 4:** Agregar a §Módulos Activos:
- `pain_ledger` → `modules/asset_generation/pain_ledger.py`
- `delivery_quality_report` → `modules/quality_gates/delivery_quality_report.py`
- `human_checklist_generator` → `modules/quality_gates/human_checklist_generator.py`
- `data_derivation_layer` → `modules/asset_generation/data_derivation_layer.py`
- `confidence_taxonomy` → `modules/data_validation/confidence_taxonomy.py`
- `cross_validator` → `modules/data_validation/cross_validator.py`

**Paso 5:** Marcar `evidence_ledger.py` como **DEPRECADO**:
- L168: cambiar referencia a `[DEPRECADO] archives/deprecated_modules_20260304/evidence_ledger.py`
- L418: remover del árbol `data_validation/`

**Paso 6:** Reorganizar §Estructura de Archivos — árbol `data_validation/`:
- Raíz `data_validation/`: solo consistency_checker.py, contradiction_engine.py, metadata_validator.py
- Agregar `modules/data_validation/` al árbol de modules: confidence_taxonomy.py, cross_validator.py, metadata_validator.py, schema_validator_v2.py, external_apis/

**Paso 7:** Verificar etiquetas FASE-C/FASE-E existentes (L175, L180, L185) — ya correctas, no tocar.

**Paso 8:** Mover `schema_validator_v2.py` de `data_validation/` a `modules/data_validation/` en el árbol de estructura.

**Paso 9:** Sincronizar referencia a FASE-0 y PIPELINE-FIX como completados en §Versión y Estado.

### T3: Verificar correcciones

1. Ejecutar pytest para confirmar conteo real:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   ./venv/Scripts/python.exe -m pytest --collect-only -q 2>/dev/null | tail -1
   ```
   Debe mostrar: `2743 tests collected`

2. Verificar que AGENTS.md ya no contiene datos stale:
   ```bash
   grep -c "2,491\|2491" AGENTS.md  # debe ser 0
   grep -c "9 publication gates" AGENTS.md  # debe ser 0
   grep -c "pain_ledger" AGENTS.md  # debe ser ≥1
   grep -c "delivery_quality_report" AGENTS.md  # debe ser ≥1
   grep -c "DEPRECADO.*evidence_ledger" AGENTS.md  # debe ser ≥1
   ```

3. Verificar que el conteo de gates es correcto:
   ```bash
   grep "publication gates" AGENTS.md | grep "11"
   ```

### T4: Documentación post-fase

Ejecutar log_phase_completion.py:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-A-01a \
    --desc "Corrección one-shot AGENTS.md: 9 pasos editoriales — sync conteo tests (2491→2743), gates (9→11), FASE-0 modules, evidence_ledger deprecado, data_validation tree corregido" \
    --archivos-mod "AGENTS.md" \
    --tests "0" \
    --check-manual-docs
```

Actualizar `09-documentacion-post-proyecto.md`:
- Sección E: `AGENTS.md | Corrección 9 pasos — sincronización con código vivo post-FASE-0 + PIPELINE-FIX | FASE-A-01a`

## Criterios de Completitud

- [ ] AGENTS.md NO contiene "2,491" ni "2491" en ninguna ubicación
- [ ] AGENTS.md NO contiene "9 publication gates"
- [ ] AGENTS.md contiene "11 publication gates" con lista correcta
- [ ] AGENTS.md §Flujo v4 incluye FASE 5: DELIVERY QUALITY
- [ ] AGENTS.md §Módulos Activos incluye pain_ledger, delivery_quality_report, human_checklist_generator, data_derivation_layer
- [ ] AGENTS.md referencia evidence_ledger como DEPRECADO
- [ ] AGENTS.md árbol data_validation refleja la estructura real (2 directorios)
- [ ] AGENTS.md incluye confidence_taxonomy y cross_validator
- [ ] log_phase_completion.py ejecutado exitosamente
- [ ] 09-documentacion-post-proyecto.md actualizado

## Restricciones

- Máximo 60 iteraciones
- **NO modificar ROADMAP.md**
- **NO modificar publication_gates.py ni ningún .py**
- **NO ejecutar v4complete ni v4audit**
- **NO modificar CHANGELOG.md ni GUIA_TECNICA.md** (eso es FASE-RELEASE)
- Solo editar AGENTS.md y 09-documentacion-post-proyecto.md
