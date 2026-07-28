# Análisis Post-Implementación — DT4-RESIDUAL-FIXES FASE-6 E2E-ZIONE

> **Fecha**: 2026-07-28
> **Versión actual**: v4.65.0
> **Hotel**: Zi One Luxury — https://zione.co/
> **Estado FASE-6**: COMPLETADA (con hallazgos críticos)

---

## 1. Execution Summary Table

| Fase | Sesión | Iteraciones | Status | delegate_task |
|------|--------|-------------|--------|---------------|
| FASE-1 | — | — | ✅ | No (DIRECTA) |
| FASE-2 | — | — | ✅ | No (DIRECTA) |
| FASE-3 | — | — | ✅ | No (DIRECTA) |
| FASE-4 | — | — | ✅ | No (DIRECTA) |
| FASE-5 | — | — | ✅ | No (DIRECTA) |
| FASE-6 | 2026-07-28 | 27 | ⚠️ COMPLETADA CON HALLAZGOS | Sí (v4complete subagente) |
| RELEASE | — | — | 🔒 BLOQUEADA | — |

---

## 2. Findings Verification Matrix (14 criterios)

### C1-C7: Código (verificados en fases anteriores — no requieren re-verificación en FASE-6)

| # | Criterio | Status | Evidencia |
|---|---------|--------|-----------|
| C1 | `pain_ledger_resolved` en contrato AssessmentPayload | ✅ | `AssessmentPayload.pain_ledger_resolved: Optional[List[Dict]]` en `modules/assessment_builder.py:63` |
| C7 | `normalize_site_presence()` existe | ✅ | `modules/asset_generation/site_presence_adapter.py:24` |
| C8 | SitePresenceChecker ≤2 ocurrencias | ✅ | 2 instancias: main.py:2380 + v4_asset_orchestrator.py:240 |
| C11 | Tests de integración existen | ✅ | 3,131 tests; `test_site_presence_adapter.py` (8 tests), varios `*Integration` test classes |

### C2-C14: Output del v4complete generado

| # | Criterio | Archivo | Status | Resultado |
|---|---------|---------|--------|-----------|
| C2 | `justified >= 1` | `gate_report_*.json` | ❌ **FAILED** | `justified=0` (sin cambio vs pre-fix) |
| C3 | `no_whatsapp_visible` not in uncovered | `gate_report_*.json` | ❌ **FAILED** | `uncovered=["no_whatsapp_visible"]` (sin cambio) |
| C4 | `coverage_no_silent_drop.passed == true` | `gate_report_*.json` | ❌ **FAILED** | `passed=false` (sin cambio) |
| C5 | `whatsapp_verified.score > 0.30` | `coherence_validation.json` | ✅ **PASSED** | `score=1.0` (antes 0.30) |
| C6 | `whatsapp_verified.passed or score >= 0.9` | `coherence_validation.json` | ✅ **PASSED** | `passed=true, score=1.0` |
| C9 | Alignment totals consistent | `gate_report` vs `delivery_quality_report` | ❌ **FAILED** | Gate: `5+2=7` ✅, Delivery: `5+0=5` ❌ — INCONSISTENCIA persiste en delivery |
| C10 | Coherence score único y trazable | `coherence_validation_post_gen.json` | ✅ **PASSED** | `pre==post=0.87` (fuente única) |
| C12 | Zi One validado post-fixes | Output files | ❌ **FAILED** | Documentos BLOQUEADOS por `coverage_no_silent_drop` + `CG-ROI-NEGATIVE` |
| C13 | CG-ROI-NEGATIVE documentado | `commercial_gates_report.json` | ⚠️ **PERSISTE** | Sigue BLOCKING. También nuevo: `CG-TECH-JARGON` WARNING |
| C14 | Docs existen | `output/v4_complete/` | ❌ **FAILED** | `01_DIAGNOSTICO_*.md` y `02_PROPUESTA_*.md` NO existen — eliminados por gate blocking |

### Resumen Cuantitativo

| | Count |
|---|-------|
| ✅ PASSED | 7 |
| ❌ FAILED | 5 |
| ⚠️ WARNING | 1 |
| **Total** | 13 |

**De los 5 FAILED, 3 son causados por un solo bug (path del pain_ledger_resolved).**

---

## 3. ROOT CAUSE ANALYSIS — ¿Por qué C2/C3/C4 fallaron?

### El bug: Path incorrecto en main.py:2690

```python
# main.py línea 2690 — BUG:
pain_ledger_resolved_path = output_dir / "v4_audit" / "pain_ledger_resolved.json"
# Resuelve a: output/v4_complete/v4_audit/pain_ledger_resolved.json  ← NO EXISTE

# Path correcto (incluye hotel_id/zione/):
# Debería ser: output/v4_complete/zione/v4_audit/pain_ledger_resolved.json  ← SÍ EXISTE
```

### Cadena causal

1. `pain_ledger_resolved.json` se genera correctamente en `output/v4_complete/zione/v4_audit/` por el post-orchestrator reconciler
2. El archivo contiene `no_whatsapp_visible` con status `MAPPED_TO_SERVICE` ✅
3. main.py:2690 busca en `output/v4_complete/v4_audit/` (sin el subdirectorio `zione/`)
4. El archivo no se encuentra → `pain_ledger_resolved_entries = None`
5. main.py:2783: `if pain_ledger_resolved_entries:` → False → `with_resolved_pain_ledger()` NUNCA se llama
6. El gate `coverage_no_silent_drop` usa `pain_ledger` (sin reconciliar), no `pain_ledger_resolved`
7. `no_whatsapp_visible` aparece como uncovered → gate FAILED
8. Gate FAILED → documentos eliminados → BLOCKED_BY_GATES.md

### Comparación con `pain_ledger` (no reconciliado)

El `pain_ledger.json` que SÍ se carga (línea 2685 usa `_get_pipeline_path(output_dir, hotel_id, "pain_ledger.json")` que SÍ incluye `hotel_id`):

```
pain_ledger.json path: output/v4_complete/zione/v4_audit/pain_ledger.json  ← CORRECTO
pain_ledger_resolved path: output/v4_complete/v4_audit/pain_ledger_resolved.json  ← INCORRECTO
```

Nótese la inconsistencia: una ruta usa `_get_pipeline_path()` (con hotel_id), la otra construye manualmente sin hotel_id.

### Fix requerido (NO implementado — política FASE-6: no modificar código)

```python
# Línea 2690, cambiar de:
pain_ledger_resolved_path = output_dir / "v4_audit" / "pain_ledger_resolved.json"

# A:
pain_ledger_resolved_path = output_dir / hotel_id / "v4_audit" / "pain_ledger_resolved.json"
```

---

## 4. delegate_task Viability Assessment

| Fase | ¿Viable? | ¿Usado? | Outcome |
|------|---------|---------|---------|
| FASE-1 | ❌ WSL venv | No | DIRECTA — implementación de código |
| FASE-2 | ❌ Decisión cross-module | No | DIRECTA — diseño arquitectónico |
| FASE-3 | ❌ WSL venv | No | DIRECTA — refactor |
| FASE-4 | ❌ WSL venv | No | DIRECTA — implementación |
| FASE-5 | ❌ WSL venv | No | DIRECTA — implementación |
| FASE-6 | ✅ v4complete | **Sí** | Subagente exitoso — 3min, exit_code=0 |
| RELEASE | ✅ YAML/MD only | — | Pendiente |

### Evaluación de delegate_task para FASE-6

- **Éxito**: El subagente ejecutó v4complete correctamente, verificó los archivos de output, y reportó resultados en ~3 minutos
- **Problema**: El subagente no pudo detectar que `01_DIAGNOSTICO` y `02_PROPUESTA` no se generaron (por el gate blocking) — los listó como "generados pero eliminados". Esto es un problema de comunicación subagente→principal.
- **Lección**: Los subagentes deben verificar EXISTENCIA de archivos con `ls -la`, no inferir de logs.

---

## 5. Lessons Learned

### Lo que funcionó bien

1. **FASE-2 (SitePresence boost)**: IMPECABLE. `whatsapp_verified` pasó de `score=0.30, passed=false` a `score=1.0, passed=true`. El boost de SitePresence está cableado correctamente a los 3 call sites.

2. **FASE-3 (Coherence single source)**: IMPECABLE. `coherence_validation.json` y `coherence_validation_post_gen.json` son IDÉNTICOS (`score=0.87` ambos). La fuente única de coherencia funciona.

3. **FASE-4 (Alignment DTO)**: PARCIAL. El `gate_report` ahora incluye `alignment` sub-object con `promised_services_total=7, generated_aligned=5, present_in_production=2`. Pero el `delivery_quality_report.json` muestra `present_in_production=0` — el DTO no se propagó al delivery report.

4. **FASE-5 (Gate idempotency)**: Funcionó. Los gates se ejecutaron una sola vez, sin mutaciones al assessment.

5. **delegate_task para v4complete**: Funcionó bien. El subagente completó en ~3 minutos. La arquitectura de subagente+principal es correcta para FASE-6.

### Lo que NO funcionó

1. **FASE-1 (pain_ledger_resolved injection) — BUG DE PATH**: El fix de código está implementado correctamente en el builder y en el gate, pero la carga del archivo en main.py:2690 usa una ruta incorrecta (falta `hotel_id/`). Esto rompe toda la cadena C2→C3→C4→C12→C14.

2. **FASE-4 (Alignment DTO en delivery report)**: El `delivery_quality_report.json` no usa el DTO canónico `AlignmentResult`. Muestra `present_in_production=0` y `passed=false` mientras el `gate_report` muestra `present_in_production=2` y `passed=true`. La inconsistencia pub-vs-delivery NO se resolvió completamente.

3. **Verificación pre-v4complete ausente**: El plan no incluyó un paso de verificación del path de `pain_ledger_resolved` antes de ejecutar v4complete. Si se hubiera validado que el archivo se carga correctamente, este bug se habría detectado en FASE-1.

### Lecciones para el futuro

1. **Validar paths con `_get_pipeline_path()` consistente**: Cualquier path dentro de `output_dir` que incluya `hotel_id` debe usar la misma función helper. La construcción manual de paths (línea 2690) es frágil.

2. **Test de integración end-to-end mínimo antes de FASE-6**: Un test sencillo que cargue `pain_ledger_resolved` desde la ruta correcta y verifique que el gate lo procesa habría detectado este bug en FASE-1.

3. **Verificación de archivos con `ls -la`, no inferencia de logs**: El subagente reportó "archivos generados y eliminados" sin verificar existencia real.

4. **Delivery report debe consumir el mismo DTO que el gate report**: La inconsistencia C9 (7=5+2 vs 5=5+0) muestra que el delivery report tiene su propia lógica de alignment que no se actualizó en FASE-4.

---

## 6. Risk Table

| Riesgo | Probabilidad | Impacto | Mitigación | ¿Ocurrió? |
|--------|-------------|---------|------------|-----------|
| Regresión en consumers de AssessmentPayload | Media | Alto | Tests exhaustivos | ❌ No |
| Shape resolution incorrecto en adapter | Alta | Medio | 5 tests de cobertura | ❌ No |
| Score drift pre/post coherence | Baja | Medio | final_coherence_report | ❌ No |
| CG-ROI-NEGATIVE sigue bloqueando | Alta | Alto | Documentar, no relajar | ✅ **Sí** — sigue BLOCKING |
| v4complete timeout subagente | Media | Alto | timeout=900, notify_on_complete | ❌ No — completó en ~80s |
| **Path de pain_ledger_resolved incorrecto** | — | — | — | ✅ **Sí** — **BUG RAÍZ** |
| Delivery report no usa AlignmentResult DTO | — | — | — | ✅ **Sí** — C9 FAILED |

---

## 7. Acciones Requeridas (para FASE-RELEASE o post-RELEASE)

### Bloqueantes para RELEASE

1. **Fix path en main.py:2690**: Cambiar `output_dir / "v4_audit"` → `output_dir / hotel_id / "v4_audit"`
2. **Re-ejecutar FASE-6** (v4complete Zi One) después del fix de path para validar C2-C4-C12-C14

### Recomendadas para RELEASE

3. **Fix delivery_quality_report**: Unificar con el AlignmentResult DTO del gate report
4. **CG-ROI-NEGATIVE**: Documentar en RELEASE que es una decisión comercial pendiente, no un bug técnico
5. **CG-TECH-JARGON**: Nuevo warning detectado — evaluar si corregir o documentar

---

## 8. Conclusiones

La FASE-6 reveló que **3 de 5 fases de implementación (FASE-2, FASE-3, FASE-5) funcionan correctamente**, mientras que **FASE-1 tiene un bug de path** que rompe la cadena completa del fix más crítico, y **FASE-4 tiene propagación incompleta** al delivery report.

El bug de FASE-1 es trivial de corregir (1 línea), pero su impacto es catastrófico: todos los criterios C2-C4-C12-C14 fallan por esta única causa raíz.

**Recomendación**: NO proceder a FASE-RELEASE sin antes corregir el path y re-ejecutar v4complete para Zi One. El fix es de 1 línea pero requiere re-verificación completa.
