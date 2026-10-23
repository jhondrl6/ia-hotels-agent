# FASE-E2E — Corrida `v4complete` de Hotel Don Alfonso + análisis post-implementación

**ID**: FASE-E2E · **Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22`
**Objetivo**: probar el pipeline comercial completo con datos reales tras las curas —un hotel tier B+ recibe paquete con veredicto honesto y **ZIP real**— y nutrir el `10-analisis` con los hallazgos de la corrida.
**Dependencias**: FASE-E2E-PRE ✅ y todas las fases de implementación ✅.
**Complejidad técnica**: MEDIA · **Duración estimada**: 2-3 horas (5-10 min solo la corrida)
**Modo de ejecución**: **DIRECTO** o **subagente con `Agent`**; el comando largo se puede lanzar con `Bash` en segundo plano. No usar `delegate_task` ni `notify_on_complete`.

## Contexto

Esta es la **única** corrida `v4complete` del plan (1/1). El baseline congelado es la corrida del 2026-10-12 para el mismo hotel: `evidence_tier` B+, 2 CRITICAL `OVER_PRESENTATION`, `BLOQUEADO`, ZIP suprimido, pérdida realista 3.511.200 COP/mes y 11 brechas de `PainSolutionMapper`. **El 39.600.000 COP/mes del contexto de deudas es un reproductor sintético de `get_detected_issues`, no la cifra del baseline**; esta corrida no lo usa como criterio.

El onboarding del baseline está en `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/hotel_don_alfonso_onboarding.yaml` y debe estar materializado en `output/clientes/` por E2E-PRE. La copia `observations.json` declara `hoteldonalfonso.com`, que no casa por host con `www.donalfonsohotel.com`; el dominio debe estar confirmado antes de la corrida.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A…FASE-H2 | ✅ |
| FASE-E2E-PRE | ✅ `LISTO_PARA_E2E` |

### Base Técnica Disponible
- `main.py` (`v4complete`, `_load_latest_onboarding_data`, `_normalize_url`)
- `data/hotel_observations/observations.json` (fuente declarada; no se edita sin autorización)
- Baseline: `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/` (acta, `revision_*.json`, `financial_scenarios`, `pain_ledger`, recibos, onboarding)
- Salida del ensayo: `evidence/…/FASE-E2E-PRE/`

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| D-T4B-A1 | Una suite verde puede certificar sin ejercitar el contrato real | La corrida es la prueba del paquete renderizado; los tests no la sustituyen |
| L-PF10 | Vacío ≠ ausente | Se distingue “0 brechas porque está curado” de “0 porque el lector falló” |
| L-R.4 | Regla sin verificador solo publicable si lo declara | Si un gate no tiene mutante posible, se declara; no todo se cierra con par rojo/verde |
| L-CIM.12 | Un control verde puede no medir la propiedad | No se certifica “publica” sin el ZIP real y su sha |

## Tareas

### Tarea 1: Preflight de corrida
**Objetivo**: confirmar que E2E-PRE dejó `LISTO_PARA_E2E`, que el onboarding está materializado y que `_load_latest_onboarding_data()` devuelve Don Alfonso con el dominio confirmado. Registrar `pre-vuelo.md` y `preflight.json` antes de gastar la inferencia.
**Criterios de aceptación**:
- [ ] `preflight.json` con `onboarding_source`, `hotel_name`, `rooms`, `adr_cop`, `occupancy_rate`, `direct_channel_pct`, `domain_confirmed`
- [ ] Si falta un requisito, se detiene con `⏳ INCOMPLETA`; no se corre a ciegas
- [ ] No se edita `observations.json` ni el YAML sin autorización

### Tarea 2: Corrida `v4complete`
**Objetivo**: `./venv/Scripts/python.exe main.py v4complete --url https://www.donalfonsohotel.com/` con el onboarding materializado.
**Protocolo**: directo o con `Agent`; si se lanza en segundo plano, usar `Bash` con `run_in_background` y preservar el stdout. **Evidencia proactiva obligatoria inmediatamente después de la corrida**: copiar `01_DIAGNOSTICO_*.md`, `02_PROPUESTA_*.md`, `v4_audit/*.json`, acta, `gate_report`, `revision_honestidad.json`, `pain_ledger.json`, `financial_scenarios_*.json`, ZIP y recibos a `evidence/…/FASE-E2E/`.
**Criterios de aceptación**:
- [ ] Corrida terminada; evidencia a salvo **antes** de verificar
- [ ] `v4_complete_report.json` y `acta_revision.json` presentes
- [ ] ZIP real presente en `deliveries/` (`suppressed:false`) o causa declarada de supresión
- [ ] Recibos de extracción guardados; no se imprime ningún secreto

### Tarea 3: Verificación contra el baseline + `10-analisis`
**Objetivo**: comparar con la corrida 2026-10-12: veredicto (`BLOQUEADO` → no bloqueante), `summary.over_presentations` (2 → 0), pérdida realista (3.511.200 → 3.511.200 o re-medida), 11 brechas de `PainSolutionMapper` re-medidas, `evidence_tier` (sigue B+ — el techo es real y se declara). Inventariar el paquete (`member_count`, sha, tamaño, ZIP real). Actualizar `10-analisis` §Resumen/§Lecciones/§Seguimientos.
**Criterios de aceptación**:
- [ ] Tabla antes/después en evidencia, referenciada desde `10-analisis`, no re-transcrita
- [ ] ZIP real verificado; un “registro” sin ZIP **no** satisface AC7
- [ ] Lecciones de la corrida registradas con formato (qué pasó / por qué / qué lo previene) o “sin lecciones nuevas”

## Tests Obligatorios

| Verificación | Artefacto | Criterio de Éxito |
|--------------|-----------|-------------------|
| AC7 completo | acta + `summary.over_presentations` + `pain_ledger.json` + `v4_complete_report.json` + ZIP | Veredicto no bloqueante; 0 `OVER_PRESENTATION`; pérdida honesta; ZIP real |
| Onboarding | `preflight.json` | Fuente y dominio confirmados |

**Comando de validación**: lectura de artefactos; no `pytest` (la suite ya corrió en cada fase). No `--re-run` para “probar” nada.

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: FASE-E2E ✅ o ⏳ INCOMPLETA.
2. `README.md`: progreso por referencia a `09` §D.
3. `09-documentacion-post-proyecto.md`: D con la métrica de la corrida.
4. `10-analisis-post-implementacion.md`: lecciones de la corrida y seguimientos.
5. `00-lecciones-capitalizadas.md`: anotar las lecciones citadas.
6. `evidence/…/FASE-E2E/`: preflight, corrida, acta, reviews, ZIP, recibos e inventario.

Registro:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-E2E --fecha <fecha-de-cierre-de-esta-fase> \
    --desc "Corrida v4complete Don Alfonso post-curación: ZIP real, 0 OVER_PRESENTATION y veredicto honesto (AC7)" \
    --archivos-nuevos "<rutas nuevas>" --archivos-mod "<rutas modificadas>" --tests "N" --check-manual-docs
```

## Criterios de Completitud (CHECKLIST)

- [ ] E2E-PRE en `LISTO_PARA_E2E`; onboarding materializado y dominio confirmado
- [ ] Corrida terminada; evidencia a salvo antes de verificar
- [ ] AC7 legible en artefactos: veredicto, `summary.over_presentations`, pérdida, 11 brechas, ZIP real
- [ ] Comparación contra baseline publicada; lecciones en `10-analisis`
- [ ] Cinco cortes sin commit; `dependencias-fases.md` actualizado

## Restricciones

- **Una sola corrida (1/1)**: no se re-corre para probar nada. Si falla por red/API, guardar crudo, declarar `⏳ INCOMPLETA` y retomar en sesión nueva; no se parchea en esta fase.
- **No modificar código** en esta fase: si la corrida destapa un defecto, se documenta con dueño y se corrige en una sesión aparte.
- Presupuesto: tope **60 tool-use** (la corrida cuenta 1 llamada + tiempo de pared); corte «listo para revisión»; instrumento legado/no comparable si no aplica.
- No tocar `P6.5`/`D21`, archivos congelados ni `T1_CERTIFIABLE_CLAUSES`. Citas por símbolos (R2.2).

## Prompt de Ejecución

```bash
Actúa como especialista en el repo iah-cli. Ejecuta únicamente FASE-E2E del plan .opencode/plans/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22.
Lee 05-prompt-inicio-sesion-fase-E2E.md, 01-plan-maestro.md §1, §4, §5 y §6, 00-lecciones-capitalizadas.md §2, dependencias-fases.md y workflow canónico.
OBJETIVO: corrida v4complete de Don Alfonso, ZIP real, 0 OVER_PRESENTATION y veredicto honesto.
TAREAS: 1 preflight de onboarding, 2 corrida y evidencia proactiva, 3 verificación contra baseline y 10-analisis.
CRITERIOS: AC7 (ZIP real, 0 OVER_PRESENTATION, pérdida 3.511.200/re-medida, 11 brechas); no sustituir el ZIP por un registro.
VALIDACIONES: artefactos de la corrida; log_phase_completion.py al cierre.
```
