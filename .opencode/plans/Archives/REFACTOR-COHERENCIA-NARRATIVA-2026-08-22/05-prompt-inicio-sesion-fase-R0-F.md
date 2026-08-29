# FASE-R0-F — Verificación profunda AC1-AC12 + Análisis Post-Implementación

**ID**: FASE-R0-F
**Objetivo**: Certificar formalmente que los 7 fixes (B1-B7) fueron superados mediante la matriz de verificación AC1-AC12 sobre el output E2E post-fix, comparar antes/después contra el baseline anómalo, y completar el análisis post-implementación (lecciones aprendidas, métricas, seguimientos).
**Dependencias**: FASE-R0-E ✅ (hard — verifica contra su output y evidencia).
**Duración estimada**: 45 minutos
**Skill**: phased_project_executor v2.15.0
**Lectura previa obligatoria**: `.opencode/context/Historico/CONTEXT-REFACTOR-COHERENCIA-NARRATIVA-FUGAS-WHATSAPP-2026-08-22.md` — §8 (AC1-AC12), §3 (lecciones aplicables), §11 (validación factual)

---

## Contexto

FASE-R0-E generó el output post-fix y la evidencia (`evidence/FASE-R0-E/` con baseline/ y output nuevo). Esta fase NO ejecuta comandos largos NI modifica código: es la certificación formal de que la refactorización cumplió su objetivo, usando el diff antes/después y los 12 criterios de aceptación del plan. El resultado alimenta directamente el análisis post-implementación que el usuario exige ("análisis post implementación de que los diferentes fixes fueron superados y lecciones aprendidas").

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-R0-A | ✅ Completada (B2) |
| FASE-R0-B | ✅ Completada (B1+B4) |
| FASE-R0-C | ✅ Completada (B3+B5) |
| FASE-R0-D | ✅ Completada (B6+B7) |
| FASE-R0-E | ✅ Completada (E2E + evidencia + smoke 7/7) |

> Si FASE-R0-E está `⏳ INCOMPLETA`: ABORTAR — no hay output post-fix verificable.

### Base Técnica

- **Evidencia post-fix**: `evidence/FASE-R0-E/` (diagnóstico, propuesta, v4_complete_report.json, pain_ledger, proposal_asset_matrix).
- **Baseline anómalo**: `evidence/FASE-R0-E/baseline/` (corrida 20260821_175706).
- **Referencias del baseline** (CONTEXT §9): "Fuga 1 — Contacto perdido por WhatsApp incorrecto" en Sección 4 (L110-117 del output); Quick Win WhatsApp (L123, L260); título "WHATSAPP…" (L29, L39); "3 FUGAS" vs contadores "7" (L105); "3 fugas digitales" (L130); propuesta: WhatsApp como adicional (L60), "(WhatsApp + datos para IA)" (L203).
- **Archivo a llenar**: `10-analisis-post-implementacion.md` (ya pre-estructurado con la matriz B1-B7 y ACs).
- **Tests base**: 3,372 funciones tras A-D (sin cambios en esta fase).

---

## Modo de Ejecución: DIRECTO (agente principal) + delegate_task OPCIONAL para el track de greps

**Justificación** (executor): la matriz de verificación y las lecciones requieren juicio y contexto completo del plan → directo. El **track de greps residuales + comparativa de pain_ledger** (Tarea 2) es trabajo independiente sin imports del proyecto NI decisiones arquitectónicas → **delegable vía `delegate_task`** como trabajo paralelo (regla de trabajo paralelo del executor). Si el presupuesto de iteraciones es holgado, puede ejecutarse directo.

**Presupuesto de iteraciones** (R2, máx. 60): ~5 setup + ~12 verificación narrativa + ~5 delegate/greps + ~10 matriz+lecciones + ~10 docs + margen.

---

## Tareas

### Tarea 1: Verificación narrativa AC1-AC6, AC8-AC11 (diff antes/después)

Leer el diagnóstico y propuesta POST-fix (`evidence/FASE-R0-E/`) y comparar contra el baseline (`evidence/FASE-R0-E/baseline/`). Completar la columna "Real" de la Matriz de Verificación en `10-analisis-post-implementacion.md`:

| AC | Verificación manual (lectura del output post-fix) |
|----|--------------------------------------------------|
| AC1 | Sección 4 del diagnóstico NUEVO: NO existe "Fuga 1 — Contacto perdido por WhatsApp incorrecto"; las fugas listadas derivan de los 7 pains reales |
| AC2 | Quick Wins (Sección 5 y 8): el Quick Win de Schema menciona datos/Google, NO WhatsApp |
| AC3 | Cada "### Fuga {n} —" corresponde a un pain_id real del pain_ledger nuevo (cruzar sección ↔ `evidence/FASE-R0-E/` pain_ledger) |
| AC4 | *(Verificación por test unitario de R0-B — confirmar que el test `test_fugas_principales_con_whatsapp_conflict` pasó en R0-B y anotarlo)* |
| AC5 | Gates reportados en la corrida: 13/13 en el mismo estado que baseline (12 PASSED + 1 WARNING pricing_compliance) |
| AC6 | Coherence score ≥ 0.8 (comparar con baseline 0.9485 y documentar delta) |
| AC8 | Pain_ledger nuevo: mismos 7 pain_ids que baseline, sin pain de WhatsApp (comparación JSON) |
| AC9 | Título Sección 4: "LAS {N} FUGAS PRINCIPALES" con N = fugas listadas = `${brechas_destacadas_count}` |
| AC10 | Sección 6: "Detecta las {N} fugas digitales" con N = 7 (brechas reales) |
| AC11 | Propuesta nueva, plan 30 días: "Implementación Fase 1 (datos para IA)" — SIN "WhatsApp + " (caso Zione sin conflicto) |

**Diff narrativo antes/después** (agregar como evidencia textual en la matriz):
- Sección 1 título: baseline "…POR WHATSAPP, GOOGLE MAPS E IA" → post-fix "…POR GOOGLE MAPS E IA" (o equivalente dinámico).
- Sección 4: baseline 3 fugas hardcoded con WhatsApp → post-fix N fugas derivadas de pains.
- Sección 5/8 Quick Wins: baseline Quick Win WhatsApp → post-fix Quick Win Schema/datos.
- Propuesta L60/L203 equivalentes: sin WhatsApp como adicional/fuga.

### Tarea 2 (DELEGABLE vía delegate_task): Greps residuales + comparativa formal

**Opción A — delegate_task** (trabajo paralelo sin imports del proyecto):

```
delegate_task(
  goal="Verificación de residuos narrativos post-refactor (AC7, AC12, AC8)",
  context="""Ejecutar desde la raíz del repo y retornar una tabla patrón|matches|veredicto:
1. grep -rn "WhatsApp incorrecto" modules/ → esperado: 0 resultados (con el diseño D-NC6 la narrativa es dinámica y el string literal ya no existe en modules/) (AC7)
2. grep -rn "Corregir el número de WhatsApp" modules/ → esperado: 0 resultados (AC12)
3. grep -rn "Fuga 1 — Contacto perdido" modules/commercial_documents/templates/ → esperado: 0 resultados
4. grep -rn "LAS 3 FUGAS\|Detecta las 3 fugas" modules/commercial_documents/ → esperado: 0 resultados
5. Comparar pain_ledger: evidence/FASE-R0-E/baseline/ vs evidence/FASE-R0-E/ → mismos 7 pain_ids, sin WhatsApp (AC8)
Retornar SOLO la tabla de resultados con veredicto PASA/FALLA por patrón.""",
  timeout=300,
  notify_on_complete=True,
  toolsets=["terminal"]
)
```

**Opción B — directo** (si el presupuesto es holgado): ejecutar los mismos greps y comparativa en la sesión.

**Resultado esperado**: AC7 ✅, AC12 ✅, residuos de template ✅, AC8 ✅ (7 pain_ids idénticos).

### Tarea 3: Completar el análisis post-implementación (`10-analisis-post-implementacion.md`)

1. **Matriz de Verificación de Hallazgos**: completar columnas Real/Status para B1-B7 y AC1-AC12 (todas las filas pre-creadas).
2. **Lecciones Aprendidas** (mínimo 3 nuevas, numeración L-NC1+): formato qué pasó / por qué / qué lo previene + pertinencia INCLUIR/EXCLUIR. Temas sugeridos: fosilización narrativa como clase de bug (datos dinámicos + texto estático), tests de contrato contra fuente dinámica (no valores fijos), el hallazgo de que el test estático de template es el guardián contra re-fosilización.
3. **Métricas de Ejecución**: tests totales (3,372), coherence pre/post, gates pre/post, pain_ids pre/post.
4. **Seguimientos abiertos**: cualquier AC con FALLA o advertencia (p. ej., B7 si quedó como auto-resuelto sin Opción B), pendientes para FASE-RELEASE.
5. **Checklist de Cierre**: dejar preparado (se completa en RELEASE).

### Tarea 4: Post-ejecución documental

Ver sección **Post-Ejecución**.

---

## Tests Obligatorios

Esta fase NO crea tests ni modifica código. Si algún AC FALLA:
1. NO marcar la fase completada.
2. Documentar el fallo en `10-analisis-post-implementacion.md` (Seguimientos abiertos) y en `dependencias-fases.md`.
3. El fix puntual del AC fallido se ejecuta en una **sesión de recuperación nueva** (fase `FASE-R0-G` si aplica), y luego FASE-R0-E bis solo si el fallo afecta el output E2E (decisión documentada — recordar la regla de única ejecución y que una re-ejecución requiere justificación explícita).

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: FASE-R0-F ✅ + resumen del veredicto (ACs PASA/FALLA).
2. **`README.md` del plan**: tabla de progreso actualizada.
3. **`06-checklist-implementacion.md`**: fila FASE-R0-F ✅.
4. **`09-documentacion-post-proyecto.md`**: Notas de Ejecución de la fase + Sección D (veredicto ACs).
5. **`10-analisis-post-implementacion.md`**: COMPLETADO en Tarea 3 (matriz, lecciones, métricas, seguimientos).
6. **Registrar la fase**:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-R0-F \
    --desc "Verificacion AC1-AC12 post-implementacion: 12/12 PASA (o detalle de fallas) + analisis post-implementacion completo" \
    --archivos-mod "" \
    --check-manual-docs
```

> **SIN flag `--release`**.

7. **Validación final**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```
> Fallos "Version Sync"/"Document Integration" → `sync_versions.py` + re-validar.

---

## Criterios de Completitud (CHECKLIST)

⚠️ Verificar ANTES de marcar como ✅ COMPLETADA ⚠️

- [ ] AC1-AC12 verificados formalmente (columnas Real/Status completas en la matriz)
- [ ] 12/12 ACs en estado PASA (o fallas documentadas con plan de recuperación — en tal caso NO completar)
- [ ] Diff narrativo antes/después documentado (baseline vs post-fix)
- [ ] Greps residuales: AC7 y AC12 con 0 matches no condicionados
- [ ] Pain_ledger pre/post: mismos 7 pain_ids (AC8)
- [ ] Mínimo 3 lecciones aprendidas nuevas registradas
- [ ] Métricas de ejecución actualizadas (tests, coherence, gates)
- [ ] `log_phase_completion.py` ejecutado (SIN `--release`)
- [ ] `dependencias-fases.md`, `README.md`, `06-checklist`, `09`, `10` actualizados
- [ ] `run_all_validations.py --quick` TOTAL PASS

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- Máximo 60 iteraciones (R2).
- **NO ejecutar `v4complete`** (la única ejecución ya ocurrió en R0-E; una re-ejecución requiere sesión de recuperación justificada).
- NO modificar código fuente ni templates (si un AC falla por código, va a sesión de recuperación — no se arregla aquí).
- NO bump de versión ni CHANGELOG (FASE-RELEASE-4.72.1 — siguiente y última fase).
- `log_phase_completion.py` SIN `--release`.
