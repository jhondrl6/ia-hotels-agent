# FASE-E2E — Corrida `v4complete` de Hotel Don Alfonso + análisis post-implementación

**ID**: FASE-E2E · **Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22`
**Objetivo**: probar el pipeline comercial completo con datos reales tras las curas —un hotel tier B+ recibe paquete con veredicto honesto y **ZIP real**— y nutrir el `10-analisis` con los hallazgos de la corrida.
**Dependencias**: FASE-E2E-PRE ✅ y todas las fases de implementación ✅.
**Complejidad técnica**: MEDIA · **Duración estimada**: 2-3 horas (5-10 min solo la corrida)
**Modo de ejecución**: **DIRECTO**, con la corrida lanzada en `Bash` en segundo plano desde el hilo principal (preferido). `Agent` queda acotado a ejecutar el comando: nunca la verificación ni el cierre documental. No usar `delegate_task` ni `notify_on_complete`.

## Contexto

Esta es la **única** corrida `v4complete` del plan (1/1). El baseline congelado es la corrida del 2026-10-12 para el mismo hotel: `evidence_tier` B+, 2 CRITICAL `OVER_PRESENTATION`, `BLOQUEADO`, ZIP suprimido, pérdida realista 3.511.200 COP/mes y 11 brechas de `PainSolutionMapper`. **El 39.600.000 COP/mes del contexto de deudas es un reproductor sintético de `get_detected_issues`, no la cifra del baseline**; esta corrida no lo usa como criterio.

El onboarding del baseline vive en `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/hotel_don_alfonso_onboarding.yaml` y **ya está materializado** en `output/clientes/`: es byte-idéntico a la copia versionada, verificado por E2E-PRE, que **no lo creó** —ya estaba allí desde el 2026-10-12—. La copia `observations.json` declara `hoteldonalfonso.com`, que no casa por host con `www.donalfonsohotel.com`; **el dominio quedó confirmado por letra del Operador el 2026-10-24** (web canónica `https://donalfonsohotel.com/`, ápice; asiento en `01-plan-maestro.md` §5) y esa grafía del warehouse **no** se usa en el run: carga al hotel por el fallback y hace que el paquete imprima una web que no es la del hotel (`evidence/…/FASE-E2E-PRE/confirmacion-dominio.txt`).

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
- [ ] `domain_confirmed: true` con la letra del Operador del 2026-10-24 como asiento: la web canónica es `https://donalfonsohotel.com/` (ápice; `www` normaliza al mismo host). La URL del run es `https://www.donalfonsohotel.com/` o su ápice — **nunca** `https://hoteldonalfonso.com/`, que carga al hotel por el fallback de `observations.json`, no dispara ninguna alerta e imprime en el documento del cliente una web que no es la del hotel (`evidence/…/FASE-E2E-PRE/confirmacion-dominio.txt`)
- [ ] `frescura_declarada_vencida: true` con la edad medida del dato y esta letra: `fecha_captura: 2026-07-22` excede el techo de 90 días que publicó el baseline. Es la **decisión (b) del Operador (2026-10-24)**: se corre con la captura vigente y se declara la edad en el pre-vuelo, sin re-capturar. No se fija `ONBOARDING_FRESHNESS_HOURS`: con el dato vencido eso pone el loader en fail-closed, el tribunal pasa de `ANALYTICS_CEILING` a `ONBOARDING_INCOMPLETE` y AC7 deja de ser alcanzable (`evidence/…/FASE-E2E-PRE/condicion-frescura-decision-b.txt`)
- [ ] `consentimiento-corrida.md` de **esta** corrida en `evidence/…/FASE-E2E/`, con la letra datada del Operador, `url_amparada`, `fecha_captura_aceptada: 2026-07-22`, su límite de frescura y la aceptación expresa de la edad declarada en el criterio anterior; su ruta, fecha y sha256 se publican en `preflight.json`. **No se reutiliza el acto de `CURA-COSTURA-TRIBUNAL-2026-10-11`**: ese documento ampara su propia corrida y lo declara por escrito. Sin este asiento no se gasta la inferencia: es condición de entrada, no una nota de chat (el ensayo E2E-PRE no la cubrió porque no hizo red ni inferencia)
- [ ] Si falta un requisito, se detiene con `⏳ INCOMPLETA`; no se corre a ciegas
- [ ] No se edita `observations.json` ni el YAML sin autorización

### Tarea 2: Corrida `v4complete`
**Objetivo**: `./venv/Scripts/python.exe main.py v4complete --url https://www.donalfonsohotel.com/ --force-new` con el onboarding materializado. `--force-new` **no** garantiza la inyección fresca: su único consumidor vivo es `run_execution_mode` y `run_v4_complete_mode` no lo consulta (re-medido el 2026-10-24); la inyección la da el YAML del `clientes_dir` efectivo. **Aislamiento del análisis previo**: `output/v4_complete/` conserva los artefactos del 2026-10-12; si la corrida los reutiliza, el pre-vuelo lo declara y la evidencia se lee con esa marca (`L-PF11`), sin heredar la premisa en silencio.
**Protocolo**: `Bash` con `run_in_background` desde el hilo principal y stdout preservado. Si se delega en `Agent`, el encargo cubre **solo el comando** y lleva verbatim las prohibiciones de esta fase —un intento, sin reintento ni `--re-run`, sin modificar código, sin declarar la fase ni ejecutar `log_phase_completion.py`— porque un subagente que reintenta quema la única inferencia pagada. El término de la corrida se afirma por exit code y presencia de artefactos, no por la notificación de la herramienta. **Evidencia proactiva obligatoria inmediatamente después de la corrida**: copiar `01_DIAGNOSTICO_*.md`, `02_PROPUESTA_*.md`, `v4_audit/*.json`, acta, `gate_report`, `revision_honestidad.json`, `pain_ledger.json`, `financial_scenarios_*.json`, ZIP y recibos a `evidence/…/FASE-E2E/`.
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
7. **Derivados al día, como último paso del cierre** (herencia medida de FASE-A y FASE-B): re-publicar el artefacto de Wiring con `validate_wiring.py --write-report` si la fase añadió archivos versionados —un `.py` nuevo en `tests/` **o** en `evidence/` mueve contadores—, y re-publicar el par del índice con `build_lesson_index.py` si la fase anotó lecciones **citando IDs del vocabulario** en `00-lecciones` o `10-analisis` (la prosa que no cita ninguno no lo vence). Verificar los dos con `--check` y leer el exit **sin tubería**: `run_all_validations.py --quick` no goberna la frescura del índice, pero el hook `[6/8]` del pre-commit la corta y bloquea el commit.

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
- [ ] Derivados re-publicados y verificados con `--check` como último paso (Wiring si la fase añadió archivos versionados; índice de lecciones si se citaron IDs del vocabulario), con el exit leído sin tubería

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
