# FASE-E2E: Ejecución v4complete Hotel Salento Real + Evidencia

**ID**: TRIBUNAL-OFFLINE-2026-09-09 / FASE-E2E
**Objetivo**: Ejecutar una única corrida `v4complete` para Hotel Salento Real con el tribunal integrado, guardar evidencia proactiva, y verificar que el acta + los 4 reportes de revisión existen en el output. Comparar contra baseline FASE-D (delta, R2.3).
**Dependencias**: FASE-T1 ✅, FASE-T2-A ✅, FASE-T2-B ✅, FASE-T4-A ✅, FASE-T4-B ✅
**Complejidad técnica**: **BAJA** — ejecución + colección de evidencia + verificación de presencia
**Modo de ejecución**: **MIXTO** — v4complete vía subagente (comando largo, timeout=900); verificación directa por el agente principal.
**Skill**: `phased_project_executor.md` v2.20.0

---

## Contexto

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-T1 | ✅ (Juez + acta) |
| FASE-T2-A | ✅ (Bot 1) |
| FASE-T2-B | ✅ (Bot 3) |
| FASE-T4-A | ✅ (Bot 2 + LLM extractor) |
| FASE-T4-B | ✅ (Bot 4) |
| FASE-E2E | ← ESTA FASE |

### Base Técnica Disponible

- **Tribunal completo**: `modules/quality_gates/tribunal/` (judge + 4 revisores + acta_writer + llm_extractor)
- **Integración en main.py**: el Juez se ejecuta junto a `delivery_quality_report`
- **URL objetivo**: `https://www.hotelsalentoreal.com/`
- **Baseline solo-lectura**: `output/FASE-D_salentoreal_post_guard/` (Tier B, 2026-08-31, coherence 0.88)
- **Corrida de referencia**: `evidence/FASE-I/` (coherence 0.8333, post-estabilización)

### Expectativas del output

- `evidence_tier`: B (sin onboarding, datos públicos + benchmark)
- `precision_tier`: C (sin datos operativos reales)
- Veredicto esperado del Juez: `APROBADO-CONDICIONAL-PENDING-ONBOARDING` (regla de primer piso)
- Coherence esperada: ≥ 0.80 (NR5)
- Artefactos nuevos en `v4_audit/`: `acta_revision.json`, `acta_revision.md`, `revision_diagnostico.json`, `revision_assets.json`, `revision_alineacion.json`, `revision_honestidad.json`

---

## Tareas

### Tarea 1: Ejecutar v4complete (COMANDO LARGO)

**Objetivo**: Corrida completa del pipeline con tribunal integrado.

**Comando**:
```bash
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelsalentoreal.com/
```

**Protocolo de subagente** (per executor §Protocolo-de-Subagente-para-v4complete):
```
delegate_task(
    goal="Ejecutar v4complete para Hotel Salento Real con tribunal integrado",
    context="URL: https://www.hotelsalentoreal.com/. Comando: ./venv/Scripts/python.exe main.py v4complete --url https://www.hotelsalentoreal.com/. Expected output: diagnóstico + propuesta + assets + coherence >= 0.80 + acta_revision.json con veredicto APROBADO-CONDICIONAL-PENDING-ONBOARDING (Tier B). El tribunal se ejecuta automáticamente junto a delivery_quality_report.",
    timeout=900,
    notify_on_complete=True,
    toolsets=["terminal"]
)
```

**⚠️ NUNCA ejecutar sin `notify_on_complete=True` o sin subagente** (executor §WARNING).

### Tarea 2: Protocolo de Evidencia Proactiva (OBLIGATORIO)

**Objetivo**: Guardar artefactos críticos INMEDIATAMENTE después de que v4complete genera output, ANTES de cualquier verificación adicional.

**Comando** (ejecutar tal cual, sin esperar):
```bash
mkdir -p evidence/FASE-E2E
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/FASE-E2E/
cp output/v4_complete/02_PROPUESTA_*.md evidence/FASE-E2E/
cp output/v4_complete/hotelsalentoreal/v4_audit/*.json evidence/FASE-E2E/
cp output/v4_complete/hotelsalentoreal/v4_audit/acta_revision.md evidence/FASE-E2E/
cp -r output/v4_complete/deliveries/hotelsalentoreal_*/ evidence/FASE-E2E/deliveries/
```

> La última línea es obligatoria (auditoría 2026-09-09): MANIFEST.json, IMPLEMENTATION_ORDER.md y ASSETS/ viven en `deliveries/` — sin ellas VERIFY no puede re-certificar AC7/AC8 desde `evidence/FASE-E2E/`.

**Esto es OBLIGATORIO sin importar cuánto tiempo quede en el presupuesto** (executor §Protocolo-Evidencia-Proactiva).

### Tarea 3: Verificación + Delta contra baseline

**Objetivo**: Verificar que el tribunal produjo sus artefactos y comparar contra baseline.

**Checklist de verificación**:
- [ ] `acta_revision.json` existe en `v4_audit/` con clave `verdict`
- [ ] `acta_revision.md` existe y es legible (6 cláusulas P6)
- [ ] `revision_diagnostico.json` existe con `findings[]`
- [ ] `revision_assets.json` existe con `coverage_by_service[]`
- [ ] `revision_alineacion.json` existe con `service_matrix[]`
- [ ] `revision_honestidad.json` existe con `findings[]`
- [ ] Veredicto == `APROBADO-CONDICIONAL-PENDING-ONBOARDING` (Tier B → primer piso)
- [ ] Coherence ≥ 0.80 (NR5)
- [ ] `clauses_evaluated` == 6

**Delta contra baseline** (R2.3):
| Métrica | Baseline FASE-D (2026-08-31) | Corrida E2E (post-tribunal) | Delta |
|---------|------------------------------|----------------------------|-------|
| Coherence canónico | 0.88 | — | — |
| `is_coherent` | false | — | — |
| Artefactos en `v4_audit/` | 0 tribunal | 6 tribunal | +6 |
| Veredicto | (no existía) | — | nuevo |
| `no_breach` servicios | 6 (FASE-D es pre-estabilización; referencia post-estabilización FASE-I = 0) | — | 0 esperado |

**Guardar delta en**: `evidence/FASE-E2E/delta_vs_baseline.md`

### Tarea 4: Docs + Post-ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-E2E \
    --desc "Corrida v4complete Hotel Salento Real con tribunal integrado: acta + 4 reportes de revisión" \
    --archivos-nuevos "evidence/FASE-E2E/" \
    --check-manual-docs
```

Actualizar `10-analisis-post-implementacion.md` con:
- Métricas de la corrida (coherence, veredicto, findings por bot)
- Análisis post-implementación: ¿los fixes de estabilización (v4.75.0) se mantienen? ¿El tribunal añade valor?
- Lecciones aprendidas (mínimo 3)

---

## Análisis Post-Implementación (obligatorio en esta fase)

Esta fase incluye el análisis de que los diferentes fixes fueron superados:

| Fix de estabilización (v4.75.0) | ¿Se mantiene en la corrida E2E? | Evidencia |
|----------------------------------|--------------------------------|-----------|
| Punto 8: propuesta dinámica (`no_breach` 6→0) | Verificar en `proposal_asset_matrix.json` | `summary.not_promised` (clave `summary` existe desde post-estabilización; el baseline FASE-D no la trae — delta "no existía") |
| A2: oráculo de presencia persistido | Verificar `site_presence_snapshot.json` en ZIP | archivo existe |
| A6: `asset_path` poblado | Verificar en `proposal_asset_matrix.json` | entradas LINKED con ruta |
| N11/P9: gate respeta `is_coherent` | Verificar en `coherence_validation.json` | `is_coherent` coherente con veredicto |
| H10: severidad 11+2 | Verificar en `gate_report_*.json` | `severity` presente en 13/13 |
| T0.2: oráculo único | Verificar `missing_count` == `alignment.unresolved` | artefacto |
| T0.3: skip silencioso cerrado | Verificar `classify_promised_services()` compartida | builders idénticos |

**Lecciones aprendidas** (formato: qué pasó / por qué / qué lo previene):
1. *(llenar tras la corrida)*
2. *(llenar tras la corrida)*
3. *(llenar tras la corrida)*

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: marcar FASE-E2E ✅
2. **`README.md` del plan**: actualizar progreso
3. **`09-documentacion-post-proyecto.md`**: Sección D (métricas de la corrida)
4. **`10-analisis-post-implementacion.md`**: fila E2E + métricas + lecciones + análisis de fixes
5. **`evidence/FASE-E2E/`**: TODOS los artefactos copiados (Protocolo Proactivo)
6. **`06-checklist-implementacion.md`**: marcar items E2E

---

## Criterios de Completitud (CHECKLIST)

- [ ] **AC13**: `acta_revision.json` con 6 cláusulas en output E2E real
- [ ] **AC14**: 4 reportes de revisión presentes en `v4_audit/`
- [ ] **Veredicto**: `APROBADO-CONDICIONAL-PENDING-ONBOARDING` (Tier B)
- [ ] **NR5**: Coherence ≥ 0.80
- [ ] **Evidencia proactiva**: artefactos en `evidence/FASE-E2E/` ANTES de verificación
- [ ] **Delta documentado**: `evidence/FASE-E2E/delta_vs_baseline.md`
- [ ] **Análisis de fixes**: tabla de 7 fixes de v4.75.0 verificados
- [ ] **Post-ejecución completada**

---

## Restricciones

- **Presupuesto**: 25 iteraciones + 1 comando largo, corte en commit de código (R2.1)
- **NO modificar código fuente** (esta fase solo ejecuta y verifica)
- **NO modificar ROADMAP.md**
- **NO usar números de línea** (R2.2)
- **Única ejecución de v4complete en todo el plan**: si falla, documentar y retomar en nueva sesión (no re-ejecutar en la misma)
- **Baseline FASE-D es SOLO LECTURA**: no modificar `output/FASE-D_salentoreal_post_guard/`
