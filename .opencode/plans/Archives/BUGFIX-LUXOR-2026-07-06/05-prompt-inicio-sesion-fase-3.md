# FASE-3: BUG-5 — Higiene Content Scrubber (Eliminar FASE 3.6 Dead Code)

**ID**: FASE-3
**Objetivo**: Eliminar o reordenar el bloque FASE 3.6 del content scrubber que es dead code efectivo, generando warnings `[SKIP]` innecesarios.
**Dependencias**: Ninguna (independiente de FASE-1 y FASE-2)
**Duración estimada**: 1-2 horas
**Skill**: `phased-project-executor`

---

## Contexto

Plan: BUGFIX-LUXOR-2026-07-06 v4.60.1
Contexto origen: `/.opencode/context/Historico/bugs_no_onboarding_luxor_2026-07-06.md`

El content scrubber en FASE 3.6 corre antes de que los documentos existan, produciendo warnings `[SKIP]`. Los scrubs reales ocurren post-T4FIX y post-gen. FASE 3.6 es dead code efectivo.

### Estado de Fases Anteriores
- FASE-1: NO INICIADA (independiente)
- FASE-2: NO INICIADA (independiente)

### Base Técnica Disponible
- `main.py` — pipeline principal (FASE 3.6 en ~L2372-2473, scrubs post-T4FIX en ~L2551, post-gen en ~L2719)
- `tests/postprocessors/test_content_scrubber.py` — tests del scrubber

---

## Tareas

### T1: Investigar FASE 3.6 del content scrubber

**Objetivo**: Entender el flujo completo del scrubber: FASE 3.6, post-T4FIX, y post-gen.

**Archivos afectados:**
- `main.py` (investigación: ~L2372-2473, ~L2551, ~L2719)

**Causa raíz (verificada contra código vivo):**
- `main.py:2372` (FASE 3.6) — el scrubber corre, pero `diagnostic_path`/`proposal_path` no existen aún (los documentos se generan después). Imprime `[SKIP]`.
- `main.py:2422/2441` — imprime `[SKIP] Diagnostic/Proposal document not available for scrubbing`.
- `main.py:2551` — post-T4FIX scrub: SÍ scrubbea (L2579-2585). "COP COP" → "COP".
- `main.py:2719` — post-gen proposal scrub: SÍ scrubbea (L2728-2732).
- El resultado final es correcto, pero FASE 3.6 es dead code efectivo.
- **Skill ref:** `iah-cli-phantom-gate-debug` — patrón "Content Scrubber Never Runs".

**Acción de investigación:**
1. grep para `[SKIP]` en `main.py` (NO confiar en line numbers — stale).
2. Leer el bloque FASE 3.6 completo.
3. Identificar el quality gate (L2444) que depende de `diag_text`/`prop_text` producidos en el bloque.
4. Determinar si el quality gate necesita moverse junto con el scrub o si puede eliminarse.

**Criterios de aceptación:**
- [ ] Flujo del scrubber documentado: FASE 3.6 (dead) vs post-T4FIX (vivo) vs post-gen (vivo)
- [ ] Quality gate identificado y se sabe qué hacer con él

---

### T2: Eliminar o reordenar bloque FASE 3.6

**Objetivo**: Remover el dead code del scrubber en FASE 3.6, manteniendo los scrubs post-T4FIX y post-gen que ya funcionan.

**Archivos afectados:**
- `main.py` (~L2372-2473)

**Decisión de implementación:**

**Opción A (mínima — preferida si el quality gate no depende del bloque):**
- Eliminar el bloque FASE 3.6 (L2372-2473) y dejar solo los scrubs post-T4FIX y post-gen que ya funcionan.
- Si el quality gate (L2444) depende de `diag_text`/`prop_text` producidos en el bloque, moverlo a después de la generación de documentos.

**Opción B (correcta — si el quality gate SÍ depende del bloque):**
- Mover el scrub de FASE 3.6 a después de la generación de documentos.
- Unificarlo con los scrubs post-T4FIX/post-gen para evitar duplicación.
- Requiere cuidar el quality gate (L2444) que depende del `diag_text`/`prop_text` producidos en el bloque.

**Pre-requisito:** La decisión A vs B se toma en T1 basándose en la investigación del quality gate.

**Verificación inmediata:**
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
grep -n '\[SKIP\]' main.py
# Post-fix: NO debe mostrar "Diagnostic document not available for scrubbing" ni "Proposal document not available for scrubbing"
```

**Criterios de aceptación:**
- [ ] Bloque FASE 3.6 eliminado o movido a posición correcta
- [ ] Quality gate preservado (si aplica) — corre sobre texto scrubbeado, no vacío
- [ ] `[SKIP] Diagnostic/Proposal document not available for scrubbing` no aparece en código

---

### T3: Verificar que los scrubs post-T4FIX y post-gen siguen funcionando

**Objetivo**: Confirmar que la eliminación de FASE 3.6 no rompe los scrubs que sí funcionan.

**Archivos afectados:**
- `tests/postprocessors/test_content_scrubber.py`

**Tests:**
- Test existente: verificar que los scrubs post-T4FIX y post-gen siguen funcionando.
- Test nuevo: ejecutar v4complete end-to-end → no debe aparecer `[SKIP]` en log. (Este test E2E se ejecuta en FASE-5, aquí solo el test unitario.)
- Test nuevo: quality gate debe correr sobre texto scrubbeado, no vacío.

**Comando:**
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/postprocessors/test_content_scrubber.py -v
```

**Criterios de aceptación:**
- [ ] Tests existentes del scrubber pasan
- [ ] Scrubs post-T4FIX y post-gen verificados como intactos
- [ ] No hay warnings `[SKIP]` en el flujo

---

## Post-Ejecución: log_phase_completion.py

**Comando (ejecutar SOLO si T1-T3 completan exitosamente):**
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py --fase FASE-3 --desc BUG5_content_scrubber_fase_36_dead_code_removed --archivos-mod main.py --tests 1 --check-manual-docs"
```

---

## Actualizar Documentación

**Después de log_phase_completion.py:**

1. **CHANGELOG.md** (agregar entrada):
```markdown
### FASE-3 BUG-5
- Eliminado FASE 3.6 del content scrubber (dead code que producía warnings `[SKIP]` innecesarios)
```

2. **GUIA_TECNICA.md** (agregar nota técnica):
```markdown
### Notas de Cambios v4.60.1 - FASE-3

**Problema:** FASE 3.6 del content scrubber corría antes de que los documentos existieran, produciendo warnings `[SKIP]`. Los scrubs reales ocurrían post-T4FIX y post-gen.
**Solución:** Eliminado el bloque FASE 3.6 (dead code). Los scrubs post-T4FIX y post-gen siguen funcionando.
**Módulos afectados:** `main.py`
**Backwards compatibility:** ✅ Sin breaking changes — los scrubs funcionales se preservaron
**Tests:** 1 test de regresión nuevo
```

3. **09-documentacion-post-proyecto.md** (acumular datos)

---

## Criterios de Completitud (CHECKLIST)

- [ ] **T1**: Flujo del scrubber documentado, quality gate identificado
- [ ] **T2**: Bloque FASE 3.6 eliminado o reordenado
- [ ] **T2**: Quality gate preservado (si aplica)
- [ ] **T3**: Tests del scrubber pasan
- [ ] **T3**: Scrubs post-T4FIX y post-gen verificados como intactos
- [ ] **log_phase_completion.py**: Ejecutado exitosamente
- [ ] **Docs cascade**: CHANGELOG, GUIA_TECNICA, 09-documentacion actualizados

---

## Restricciones

- **NO ejecutar v4complete** (eso es FASE-5)
- **NO modificar `llm_mention_checker.py`** (eso es FASE-2)
- **NO modificar `v4_comprehensive.py`** (eso es FASE-1 y FASE-4)
- **NO modificar `seo_elements_detector.py`** (eso es FASE-4)
- **NO modificar L1942 de main.py** (eso es FASE-1 — solo tocar L2372-2473)
- **Máximo 60 iteraciones** del agente
- **Verificar contra código vivo** antes de aplicar patch
- **Cuidar el quality gate** — no romper el flujo post-T4FIX

---

## Budget de Iteraciones Estimado

```
Fijos:
  - Leer plan + verificar estado: ~3 iters
  - Investigar código/archivos: ~5-10 iters
  - log_phase_completion.py + docs cascade: ~10 iters
  Total fijo: ~18-23 iters

Específico:
  - T1 (investigar FASE 3.6): ~8-12 iters
  - T2 (eliminar/reordenar bloque): ~8-12 iters
  - T3 (verificar scrubs + tests): ~5-8 iters
  Total específico: ~21-32 iters

Total estimado: 39-55 iters (dentro del límite de 60)
```

**Modo de ejecución:** Agente principal DIRECTO (código puro)

---

## Recuperación en Caso de Agotamiento

Si el agente alcanza 60 iteraciones:
1. Guardar estado actual del fix (si ya se aplicó)
2. Marcar fase como `⏳ INCOMPLETA` en `dependencias-fases.md`
3. Documentar checkpoint
4. Retomar en nueva sesión

---

## Checklist Final

- [ ] FASE 3.6 del scrubber eliminada o reordenada
- [ ] `[SKIP] Diagnostic/Proposal document not available` no aparece en código
- [ ] Quality gate preservado y funcional
- [ ] Scrubs post-T4FIX y post-gen intactos
- [ ] Tests del scrubber pasan
- [ ] log_phase_completion.py ejecutado
- [ ] CHANGELOG.md actualizado
- [ ] GUIA_TECNICA.md actualizado
- [ ] 09-documentacion-post-proyecto.md actualizado
