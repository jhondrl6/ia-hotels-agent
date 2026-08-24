# FASE-R0-E — E2E: Única ejecución de v4complete (Zi One Luxury) + evidencia + smoke

**ID**: FASE-R0-E
**Objetivo**: Ejecutar **la única corrida `v4complete` del plan** sobre Zi One Luxury (https://zione.co/) con onboarding real, preservar evidencia (baseline anómalo + output post-fix) y realizar la verificación smoke que habilita la verificación profunda de FASE-R0-F.
**Dependencias**: FASE-R0-A ✅ + FASE-R0-B ✅ + FASE-R0-C ✅ + FASE-R0-D ✅ (hard — la corrida debe reflejar TODOS los fixes).
**Duración estimada**: ~30 minutos de agente + 5-10 minutos de corrida v4complete.
**Skill**: phased_project_executor v2.15.0 (§Protocolo-de-Subagente-para-v4complete + §Protocolo-de-Evidencia-Proactiva)
**Lectura previa obligatoria**: `.opencode/context/CONTEXT-REFACTOR-COHERENCIA-NARRATIVA-FUGAS-WHATSAPP-2026-08-22.md` — §1 (mapa de artefactos), §8 (AC5, AC6, AC8), §9 (datos del sistema)

---

## Contexto

Con los 4 fixes narrativos implementados (B2, B1+B4, B3+B5, B6+B7), se genera el output E2E de Zione para verificar en producción simulada que la anomalía desapareció. La corrida previa (20260821_175706) reportaba: "Fuga 1 — Contacto perdido por WhatsApp incorrecto" pese a `whatsapp_status=VERIFIED`, coherence 0.9485, 7 pain_ids, gates 13/13 (12 PASSED + 1 WARNING pricing_compliance). El baseline anómalo DEBE preservarse ANTES de la corrida para el diff antes/después de FASE-R0-F.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-R0-A | ✅ Completada (B2) |
| FASE-R0-B | ✅ Completada (B1+B4) |
| FASE-R0-C | ✅ Completada (B3+B5) |
| FASE-R0-D | ✅ Completada (B6+B7) |

> Si alguna fase NO está ✅ en `06-checklist-implementacion.md`: ABORTAR esta fase (la corrida no reflejaría todos los fixes).

### Base Técnica

- **Comando** (el onboarding real se auto-carga — mecanismo FASE-D S7, `main.py` L1759-1781):

```bash
./venv/Scripts/python.exe main.py v4complete --url https://zione.co/
```

- **Onboarding real**: `output/clientes/zi-one-luxury_onboarding.yaml` (Tier A, 4 campos confirmados: habitaciones=34, reservas_mes=800, valor_reserva_cop=290000, canal_directo_pct=40.0). En el log de la corrida debe aparecer `Onboarding data loaded: 4 campos confirmados`.
- **Baseline anómalo a preservar** (ANTES de correr):
  - `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260821_175706.md`
  - `output/v4_complete/02_PROPUESTA_COMERCIAL_20260821_175706.md`
  - `output/v4_complete/v4_complete_report.json` (correspondiente a esa corrida)
  - `pain_ledger` del baseline: los archivos ya existen SUELTOS (verificado) en `output/v4_complete/zione/v4_audit/pain_ledger.json` y `pain_ledger_resolved.json` — copiarlos directamente (NO se necesita descomprimir el ZIP de deliveries)
- **Expected output**: nuevos `01_DIAGNOSTICO_*.md`, `02_PROPUESTA_*.md`, `v4_complete_report.json`, deliveries ZIP (pain_ledger, proposal_asset_matrix), coherence ≥ 0.80.

---

## Modo de Ejecución: DELEGATE_TASK para v4complete (subagente) + parent para el resto

**Justificación** (executor §Protocolo-de-Subagente-para-v4complete + decisión del plan maestro §6): `v4complete` consume 5-10 minutos de tiempo real. Delegarlo a un subagente con `notify_on_complete=True` permite que el agente parent concentre sus iteraciones en preservación de evidencia, verificación smoke y docs cascade — exactamente el perfil de esta fase. El subagente SOLO ejecuta el comando con toolset de terminal (sin imports del proyecto, sin riesgo venv WSL).

**Presupuesto de iteraciones** (R2, máx. 60): ~5 pre-checks + ~3 baseline + ~3 delegate + ~10 evidencia/smoke + ~10 docs + margen amplio.

---

## Tareas

### Tarea 1: Pre-checks + preservación del baseline anómalo + ejecución de v4complete vía subagente

**1a. Pre-checks** (~3 iteraciones):
- [ ] Verificar en `06-checklist-implementacion.md` que A+B+C+D están ✅.
- [ ] Verificar que `output/clientes/zi-one-luxury_onboarding.yaml` existe y contiene los 4 campos confirmados.
- [ ] Snapshot rápido del estado git (`git status --short`) para trazabilidad.

**1b. Preservar baseline ANTES de la corrida** (~2 iteraciones) — comandos PowerShell 7 (shell del entorno; NO usar sintaxis bash `mkdir -p`/`cp`/`unzip`):

```powershell
New-Item -ItemType Directory -Force -Path evidence/FASE-R0-E/baseline | Out-Null
Copy-Item output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260821_175706.md evidence/FASE-R0-E/baseline/
Copy-Item output/v4_complete/02_PROPUESTA_COMERCIAL_20260821_175706.md evidence/FASE-R0-E/baseline/
Copy-Item output/v4_complete/v4_complete_report.json evidence/FASE-R0-E/baseline/v4_complete_report_baseline.json
# pain_ledger del baseline (ya existen sueltos — verificado):
Copy-Item output/v4_complete/zione/v4_audit/pain_ledger.json evidence/FASE-R0-E/baseline/
Copy-Item output/v4_complete/zione/v4_audit/pain_ledger_resolved.json evidence/FASE-R0-E/baseline/
```

> Si algún archivo del baseline no existe con ese nombre exacto, localizar los archivos de la corrida 20260821 por patrón (`Get-ChildItem output/v4_complete/*20260821*`) y copiar los equivalentes. Documentar en `dependencias-fases.md` qué se preservó.

**1c. Ejecutar v4complete vía `delegate_task`** (protocolo del executor):

```
delegate_task(
  goal="Ejecutar v4complete para Zi One Luxury y confirmar la generación completa del output",
  context="""Comando EXACTO (ejecutar UNA sola vez, desde la raíz del repo):
./venv/Scripts/python.exe main.py v4complete --url https://zione.co/

El onboarding real se auto-carga desde output/clientes/zi-one-luxury_onboarding.yaml (NO requiere flags).

Expected output en output/v4_complete/:
- 01_DIAGNOSTICO_Y_OPORTUNIDAD_<timestamp>.md
- 02_PROPUESTA_COMERCIAL_<timestamp>.md
- v4_complete_report.json (whatsapp_status: VERIFIED)
- deliveries/ ZIP (pain_ledger.json, proposal_asset_matrix.json)
- coherence >= 0.80
- En el log: 'Onboarding data loaded: 4 campos confirmados'

REGLAS:
- NO modificar código fuente ni configuración.
- NO re-ejecutar si falla: capturar el error completo y retornarlo.
- Retornar en el reporte: exit status, lista de archivos generados, coherence score, estado de gates.""",
  timeout=900,
  notify_on_complete=True,
  toolsets=["terminal"]
)
```

> **FALLO DELEGATION NO DISPONIBLE**: si `delegate_task` no está disponible en el entorno, ejecutar directamente con `terminal(./venv/Scripts/python.exe main.py v4complete --url https://zione.co/, timeout=600, notify_on_complete=True)` — nunca bloquear sin notificación (regla del executor).
>
> **SI v4complete FALLA**: NO re-ejecutar (única ejecución del plan). Aplicar el Protocolo de Recuperación: guardar lo que exista en `evidence/FASE-R0-E/`, marcar la fase `⏳ INCOMPLETA` con el error documentado, y cerrar sesión. El diagnóstico del fallo y la re-ejecución autorizada ocurren en una sesión de recuperación NUEVA (documentar la decisión en `dependencias-fases.md`).

### Tarea 2: Protocolo de Evidencia Proactiva + verificación smoke

**2a. Evidencia Proactiva (OBLIGATORIA inmediatamente después del output, antes de cualquier otra verificación)** — PowerShell 7:

```powershell
New-Item -ItemType Directory -Force -Path evidence/FASE-R0-E | Out-Null
# Copiar SOLO el timestamp más reciente (post-fix) — no el del baseline:
$diag = Get-ChildItem output/v4_complete/01_DIAGNOSTICO_*.md | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$prop = Get-ChildItem output/v4_complete/02_PROPUESTA_*.md | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Copy-Item $diag.FullName evidence/FASE-R0-E/
Copy-Item $prop.FullName evidence/FASE-R0-E/
Copy-Item output/v4_complete/v4_complete_report.json evidence/FASE-R0-E/
Get-ChildItem output/v4_complete/deliveries/*.zip -ErrorAction SilentlyContinue | ForEach-Object { Copy-Item $_.FullName evidence/FASE-R0-E/ }
# pain_ledger nuevo: copiar los JSON sueltos del output de la corrida
# (ruta típica: output/v4_complete/zione/v4_audit/pain_ledger*.json — verificar la ruta real del run y copiarlos a evidence/FASE-R0-E/)
```

> Cuidado: NO sobrescribir `evidence/FASE-R0-E/baseline/`. Los archivos nuevos van en la raíz de `evidence/FASE-R0-E/`.

**2b. Verificación smoke** (rápida — la verificación profunda de ACs es FASE-R0-F, NO esta fase):

| # | Check | Umbral | Estado esperado |
|---|-------|--------|-----------------|
| S1 | Archivos nuevos existen (diagnóstico, propuesta, report, deliveries) | Todos | ✅ |
| S2 | `v4_complete_report.json`: `whatsapp_status` | `VERIFIED` | ✅ (capa de datos intacta — AC8 parcial) |
| S3 | Coherence score reportado | ≥ 0.8 (AC6; referencia baseline: 0.9485) | ✅ |
| S4 | Gates de publicación | 13/13 en el mismo estado que baseline (12 PASSED + 1 WARNING pricing_compliance) — AC5 | ✅ |
| S5 | Log/manifest: onboarding cargado | "4 campos confirmados" | ✅ |
| S6 | Pain_ledger nuevo: 7 pain_ids, SIN pain de WhatsApp | 7 ids (schema, seo, faq, analytics, visibility, crawlers, og) | ✅ (AC8) |
| S7 | Smoke narrativo rápido (grep, no análisis): el diagnóstico nuevo NO contiene "Contacto perdido por WhatsApp incorrecto" | 0 matches | ✅ (anticipo AC1) |

### Tarea 3: Post-ejecución documental

Ver sección **Post-Ejecución**.

---

## Tests Obligatorios

Esta fase NO crea tests ni ejecuta suites (sin cambios de código). La verificación es la tabla smoke de Tarea 2.

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: FASE-R0-E ✅ + notas (timestamp de la corrida, coherence, estado gates, archivos preservados).
2. **`README.md` del plan**: tabla de progreso actualizada.
3. **`06-checklist-implementacion.md`**: fila FASE-R0-E ✅.
4. **`09-documentacion-post-proyecto.md`**:
   - Sección D (Métricas): coherence de la corrida, gates, pain_ids.
   - Notas de Ejecución de la fase (comando delegado, duración, resultado del subagente).
5. **`10-analisis-post-implementacion.md`**:
   - Resumen de Ejecución: fila FASE-R0-E (iteraciones, delegate_task usado: sí/no, notas).
   - Métricas de Ejecución: coherence pre/post (0.9485 → nuevo), gates pre/post.
6. **Evidencia**: `evidence/FASE-R0-E/` (baseline/ + output post-fix) — YA guardada en Tarea 2a.
7. **Registrar la fase**:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-R0-E \
    --desc "E2E v4complete Zione post-fixes narrativos: evidencia baseline+nueva, smoke 7/7" \
    --archivos-mod "" \
    --coherence <valor_real_de_la_corrida> \
    --check-manual-docs
```

> **SIN flag `--release`**. Sustituir `<valor_real_de_la_corrida>` por el coherence reportado.

8. **Validación final**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```
> Fallos "Version Sync"/"Document Integration" → `sync_versions.py` + re-validar.

---

## Criterios de Completitud (CHECKLIST)

⚠️ Verificar ANTES de marcar como ✅ COMPLETADA ⚠️

- [ ] Pre-checks A+B+C+D ✅ verificados antes de la corrida
- [ ] Baseline anómalo (20260821) preservado en `evidence/FASE-R0-E/baseline/`
- [ ] v4complete ejecutado UNA sola vez (vía delegate_task o terminal con notify_on_complete)
- [ ] Evidencia proactiva guardada en `evidence/FASE-R0-E/` ANTES de cualquier verificación
- [ ] Smoke S1-S7: todos ✅ (si S3/S4 desvían del baseline, documentar y NO marcar completada sin análisis)
- [ ] `log_phase_completion.py` ejecutado (SIN `--release`)
- [ ] `dependencias-fases.md`, `README.md`, `06-checklist`, `09`, `10` actualizados
- [ ] `run_all_validations.py --quick` TOTAL PASS

**NO marcar la fase como completada si algún criterio falla.** Si v4complete falló: `⏳ INCOMPLETA` + error documentado + sesión de recuperación nueva.

---

## Restricciones

- Máximo 60 iteraciones (R2).
- **UNA sola ejecución de v4complete** en toda la fase (y en todo el plan). Sin re-intentos.
- NO modificar código fuente ni configuración en esta fase (los fixes ya están en A-D).
- NO ejecutar la verificación profunda de AC1-AC12 (es FASE-R0-F) — solo smoke.
- NO bump de versión ni CHANGELOG (FASE-RELEASE-4.72.1).
- `log_phase_completion.py` SIN `--release`.
- NUNCA ejecutar v4complete sin `notify_on_complete=True` o sin subagente (regla del executor).
