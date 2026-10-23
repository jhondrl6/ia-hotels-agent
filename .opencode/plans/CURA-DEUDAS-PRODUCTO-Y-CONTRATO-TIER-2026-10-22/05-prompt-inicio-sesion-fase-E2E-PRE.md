# FASE-E2E-PRE — Ensayo determinista del baseline (sin inferencia pagada)

**ID**: FASE-E2E-PRE · **Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22`
**Objetivo**: probar el ensamblaje completo del paquete de Don Alfonso con los artefactos del baseline y el código corregido —onboarding, render B+, revisor real, juez real y publicación en un directorio temporal— **antes** de gastar la única corrida pagada.
**Dependencias**: FASE-A…FASE-H2 ✅.
**Complejidad técnica**: MEDIA · **Duración estimada**: 2-3 horas
**Modo de ejecución**: **DIRECTO** (sin `v4complete`; no usa el LLM).

## Contexto

La corrida E2E es única y no se parchea en esa fase. El baseline del 2026-10-12 dejó todos los insumos para un ensayo determinista: `financial_scenarios_20261012_165654.json`, `audit_report_20261012_165654.json`, `gate_report`, `commercial_gates_report`, `revision_*.json`, `01_DIAGNOSTICO`, `02_PROPUESTA` y `hotel_don_alfonso_onboarding.yaml`. El ensayo no repite la extracción ni la generación LLM: reutiliza esos artefactos, renderiza con los generadores corregidos, invoca el `HonestyReviewer` real y el `TribunalJudge` real, y prueba `DeliveryPackager.write/publish` en un directorio temporal.

**Hallazgo que este paso debe cerrar**: el onboarding del baseline vive en `output/clientes/hotel_don_alfonso_onboarding.yaml`, que está gitignorado; la copia versionada está en la evidencia. `data/hotel_observations/observations.json` declara Don Alfonso con `hoteldonalfonso.com`, que no casa por host con `www.donalfonsohotel.com`. El preflight materializa el YAML versionado y **afirma** que `_load_latest_onboarding_data()` lo devuelve; el Operador confirma el dominio antes de la corrida.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A…FASE-H2 | ✅ |

### Base Técnica Disponible
- Baseline: `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/` (incluye `corrida/`, `recibos/`, `hotel_don_alfonso_onboarding.yaml`)
- `main.py` (`_load_latest_onboarding_data`, `_normalize_url`, `v4complete`)
- `modules/commercial_documents/v4_proposal_generator.py` y `v4_diagnostic_generator.py`
- `modules/quality_gates/tribunal/honesty_reviewer.py`, `judge.py`, `outcome.py`, `review_inputs.py`
- `modules/delivery/` (`DeliveryPackager.write/publish/suppress`)
- `modules/quality_gates/tribunal/llm_extractor.py` (`MockPromiseExtractor` para no llamar al LLM)

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| D-T4B-A1 | Una suite verde puede certificar sin ejercitar el contrato real | El ensayo usa los artefactos reales del baseline, no fixtures inventados |
| L-PF10 | Vacío ≠ ausente | Distinguir “0 findings porque está curado” de “0 porque el revisor no leyó” |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | El juez se ejecuta con el código nuevo y los reports reales; no se simula el veredicto |
| L-R.4 | Regla sin verificador solo publicable si lo declara | El ensayo no sustituye la corrida; si un insumo falta, se detiene y se declara |

## Tareas

### Tarea 1: Preflight de onboarding y dominio
**Objetivo**: materializar el YAML versionado en `output/clientes/` (si no existe), afirmar que `_load_latest_onboarding_data("https://www.donalfonsohotel.com/")` lo devuelve y registrar la fuente (`observations_tier_a`), `rooms`, `adr_cop`, `occupancy_rate` y `direct_channel_percentage`. Documentar la discrepancia `hoteldonalfonso.com` vs `www.donalfonsohotel.com`; el Operador confirma el dominio antes de E2E.
**Criterios de aceptación**:
- [ ] `preflight.json` con `onboarding_source`, `hotel_name`, `rooms`, `adr_cop`, `occupancy_rate`, `direct_channel_pct` y `domain_confirmed`
- [ ] Si el YAML no está o no casa, el ensayo se detiene con `⏳ INCOMPLETA`; no se sigue a ciegas
- [ ] No se edita `observations.json` sin autorización del Operador

### Tarea 2: Render con los generadores corregidos
**Objetivo**: reconstruir la propuesta y el diagnóstico con los insumos del baseline y los generadores corregidos, sin llamar al LLM. Si un generador exige un objeto que no se puede reconstruir sin inferencia, se documenta el hueco y se usa la ruta de render de plantilla con los datos del baseline; no se inventan cifras.
**Criterios de aceptación**:
- [ ] Propuesta y diagnóstico renderizados en `evidence/…/FASE-E2E-PRE/render/`
- [ ] El texto conserva “Fuga total”/“Total recuperación” y no contiene “Protección total”/“Transparencia total” con tier B+
- [ ] La fuente de cada cifra es un artefacto del baseline, no un valor inventado

### Tarea 3: Revisor real y juez real
**Objetivo**: ejecutar `HonestyReviewer` sobre los documentos renderizados y `TribunalJudge` sobre el `v4_audit` del baseline con el código nuevo; usar `MockPromiseExtractor` o los reports existentes para no llamar al LLM.
**Criterios de aceptación**:
- [ ] `revision_honestidad.json` del ensayo → `summary.over_presentations == 0` en propuesta y diagnóstico
- [ ] Acta del ensayo → `verdict` no bloqueante y `conditional_reason` legible
- [ ] `P6.5` permanece `NOT_EVALUABLE` con su dueño; no se toca
- [ ] Mutante: desactivar la condición del render → `summary.over_presentations > 0` (rojo)

### Tarea 4: Ensamblaje y publicación en temporal
**Objetivo**: probar `DeliveryPackager.write()` y `publish()` con un mini-paquete o con los artefactos del baseline en un directorio temporal; afirmar que el ZIP existe, no está suprimido y tiene sha/tamaño. No tocar `deliveries/` real.
**Criterios de aceptación**:
- [ ] ZIP temporal con `suppressed:false`, `member_count > 0`, sha y tamaño registrados
- [ ] El flujo de supresión se prueba con un veredicto bloqueante en otro caso, sin borrar el paquete bueno
- [ ] El ensayo no escribe en `deliveries/` real ni en el `output/` de la corrida

### Tarea 5: Veredicto del ensayo
**Objetivo**: si las cuatro tareas pasan, declarar `LISTO_PARA_E2E`; si alguna falla, detener y abrir seguimiento con dueño. No se autoriza la corrida pagada con un fallo abierto de este ensayo.
**Criterios de aceptación**:
- [ ] `pre-vuelo.md` con la tabla de checks y el estado final
- [ ] `LISTO_PARA_E2E` o `⏳ INCOMPLETA` con la causa y el dueño
- [ ] `10-analisis` §Seguimientos actualizado

## Tests Obligatorios

| Verificación | Artefacto | Criterio de Éxito |
|--------------|-----------|-------------------|
| onboarding | `preflight.json` | Fuente y datos reales; dominio declarado |
| render B+ | `render/02_PROPUESTA`, `render/01_DIAGNOSTICO` | Sin claims absolutos; labels financieros intactos |
| revisor real | `review/revision_honestidad.json` | `summary.over_presentations == 0` |
| juez real | `judge/acta_revision.json` | Veredicto no bloqueante + `conditional_reason` |
| paquete | `package/` | ZIP real, `suppressed:false`, sha/tamaño |

**Comando de validación**: lectura de artefactos del ensayo + `./venv/Scripts/python.exe -m pytest <tests-de-render-y-paquete> -q` (si la fase añade tests). **No** ejecutar `main.py v4complete`.

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: FASE-E2E-PRE ✅ o ⏳ INCOMPLETA.
2. `README.md`: progreso por referencia a `09` §D.
3. `09-documentacion-post-proyecto.md`: B/D/E de la fase.
4. `10-analisis-post-implementacion.md`: fila, lecciones y seguimientos.
5. `00-lecciones-capitalizadas.md`: anotar las lecciones citadas.
6. `evidence/…/FASE-E2E-PRE/`: preflight, render, reviews, judge, package y `pre-vuelo.md`.

Registro:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-E2E-PRE --fecha <fecha-de-cierre-de-esta-fase> \
    --desc "Ensayo determinista del baseline: onboarding, render B+, revisor y juez reales, paquete temporal (sin inferencia)" \
    --archivos-nuevos "<rutas nuevas>" --archivos-mod "<rutas modificadas>" --tests "N" --check-manual-docs
```

## Criterios de Completitud (CHECKLIST)

- [ ] Onboarding materializado y dominio declarado; si no, detenido
- [ ] Propuesta y diagnóstico B+ sin los 2 claims; labels financieros intactos
- [ ] `summary.over_presentations == 0`; acta con `conditional_reason`
- [ ] ZIP temporal real; `deliveries/` intacto
- [ ] `LISTO_PARA_E2E` o `INCOMPLETA` con dueño; evidencia completa
- [ ] Cinco cortes sin commit; lecciones registradas

## Restricciones

- **No** ejecutar `v4complete` ni llamar al LLM pagado. **No** modificar código de producto en esta fase: si el ensayo falla, se documenta y se corrige en la fase dueña, no aquí.
- No tocar `deliveries/` real, archivos congelados, `P6.5`/`D21` ni `T1_CERTIFIABLE_CLAUSES`.
- Presupuesto: tope **60 tool-use**; instrumento legado/no comparable si no aplica. Citas por símbolos (R2.2).

## Prompt de Ejecución

```bash
Actúa como especialista en el repo iah-cli. Ejecuta únicamente FASE-E2E-PRE del plan .opencode/plans/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22.
Lee 05-prompt-inicio-sesion-fase-E2E-PRE.md, 01-plan-maestro.md §1, §2, §4, §5 y §6, 00-lecciones-capitalizadas.md §2, dependencias-fases.md y workflow canónico.
OBJETIVO: ensayo determinista del baseline (onboarding, render B+, revisor/juez reales, paquete temporal) sin inferencia.
TAREAS: 1 preflight de onboarding, 2 render, 3 revisor y juez reales, 4 paquete temporal, 5 veredicto LISTO/INCOMPLETA.
CRITERIOS: summary.over_presentations == 0; acta con conditional_reason; ZIP temporal real; no tocar deliveries real.
VALIDACIONES: artefactos del ensayo; log_phase_completion.py al cierre.
```
