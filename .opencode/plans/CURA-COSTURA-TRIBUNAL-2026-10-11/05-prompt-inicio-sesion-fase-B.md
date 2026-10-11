# FASE-B — Consumidores del contrato: Bot 2 y Bot 4 dejan de verse sanas con extracción no-OK

**ID**: FASE-B (plan CURA-COSTURA-TRIBUNAL-2026-10-11)
**Objetivo**: migrar los dos revisores LLM del Tribunal a la API checked de FASE-A, eliminar el wrapper transicional DEC-A1, propagar el estado de extracción al acta (fin del `OK_NO_FINDINGS` con cara de «sin promesas»), llevar el regex de lenguaje de verificación al texto completo (N5) y medir/ajustar la superficie de falso positivo del patrón de CRITICAL (N7).
**Dependencias**: FASE-A ✅ (la API checked y el recibo deben existir).
**Duración estimada**: 1 sesión.
**Complejidad**: ALTA — dos revisores que gatean la entrega del ZIP; lectores de artefactos (R2.6 aplica).
**Skill**: `.agents/workflows/phased_project_executor.md` (workflow canónico).

## Contexto

FASE-A curó el productor. Hoy los consumidores leen `extract_verbal_promises → list` y una extracción `NO_EVALUABLE`/`FALLIDO` llega como `[]`: Bot 2 queda `OK_NO_FINDINGS` con recomendación APROBADO y Bot 4 `OK_NO_FINDINGS` (§10.3 del contexto) — el envenenamiento persistente es indistinguible de una propuesta sin promesas. Además, el regex de sobre-presentación corre solo sobre las citas que el LLM eligió (N5) y el patrón `total/absoluto/definitivo` puede suprimir un ZIP por una palabra común en prosa hotelera (N7).

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| Preparación | ✅ Completada (2026-10-11) |
| FASE-A | ✅ Completada (contrato 4 estados + cache versionada + recibo; wrapper transicional DEC-A1 vivo) |

### Base Técnica Disponible

- `modules/quality_gates/tribunal/alignment_reviewer.py` (símbolos: `AlignmentReviewer`, el consumo de la extracción en su camino promesa→matriz, `_cover_unmatched_entries`, `_find_matrix_entry`).
- `modules/quality_gates/tribunal/honesty_reviewer.py` (símbolos: `HonestyReviewer`, el consumo de claims, el regex de lenguaje de verificación, la lectura de `evidence_tier` con fallback `UNKNOWN`).
- `modules/quality_gates/tribunal/outcome.py` — medido: `collect_reviewer_reports` computa el estado del revisor **solo desde `findings_count`** (ternario `OK_NO_FINDINGS` / `OK_WITH_FINDINGS`), `ReviewerStatus` lleva la propiedad que el Juez consulta, y `_compute_verdict` decide con `status.blocks_approval`; `derive_corrective_actions` lee `finding_type` y `source_artifact` de cada finding.
- `modules/quality_gates/tribunal/acta_writer.py` — `_STATUS_LABELS` tiene 5 etiquetas y su reserva es `.get(status, status)` (un miembro nuevo se mostraría crudo); `ACTA_FINDING_KEYS` proyecta `finding_type`, `severity`, `clause`, `description`.
- API checked de FASE-A en `llm_extractor.py` (cuatro estados + recibo).
- Baseline real para R2.6: usar el acta JSON y la propuesta reales más recientes disponibles en el repo (output/ o evidence/ de planes anteriores); si no hay, `pytestmark = pytest.mark.skipif(...)` **explícito y visible**.

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar; el cruce cubre ambas direcciones | T1/T2: los tests de AC8/9 exigen datos que alcancen la rama de estado no-OK y el cruce cubre promesa→matriz y matriz→promesa |
| DA-T4A | PromiseExtractor es la interfaz; el llamador no cambia de implementación | T1/T2: los revisores consumen el estado, no la implementación; el mock inyectado por tests toma la forma del contrato nuevo |
| L-VERIFY.4 | El acta mostró P6.2 NOT_EVALUABLE con revisores corriendo | T1/T2: el report de cada revisor declara su estado de extracción en el acta, para que el humano vea «no evaluado» y no «sano» |

## Tareas

> **Orden de ejecución obligatorio: T3 → T2 → T1 → T4.** La razón, medida sobre la propuesta real del 2026-10-07: encender el texto completo (T2) **antes** de ajustar el patrón (T3) mete ≥1 CRITICAL espurio sobre esa propuesta — de las 5 coincidencias del patrón de cuantificadores, 3 son totales financieros o de tabla — y `verified_critical` **suprime el ZIP** en la corrida única de FASE-E2E, que no se puede repetir. Las tareas conservan su numeración y sus ACs: solo se declara el orden.

### Tarea 1 — Bot 2 consume el estado (AC8)

**Archivos afectados**:
- `modules/quality_gates/tribunal/alignment_reviewer.py`
- `modules/quality_gates/tribunal/outcome.py` — **EDITA obligatorio** (no condicional): `collect_reviewer_reports` es quien computa `OK_NO_FINDINGS` **solo desde `findings_count`**, y el Juez decide con `status.blocks_approval`; sin tocarlo, el acta diría «sana» aunque el report declare `NO_EVALUABLE` (AC17)
- `modules/quality_gates/tribunal/acta_writer.py` — **EDITA obligatorio**: `_STATUS_LABELS` tiene 5 etiquetas y su reserva `.get(status, status)` mostraría crudo el miembro nuevo de AC17
- `tests/quality_gates/tribunal/` (tests del revisor)

**Criterios de aceptación**:
- [ ] El revisor consume la API checked de FASE-A.
- [ ] Extracción `NO_EVALUABLE`/`FALLIDO` → el report publica el estado con su motivo (tri-estado R2.9: sin hallazgos vs no evaluado vs lector fallido); **nunca** `OK_NO_FINDINGS` ante un no-OK.
- [ ] **AC17 (el acta, no solo el report)**: el estado no-OK del revisor se propaga a un `ReviewerStatus` con `blocks_approval=True` (miembro nuevo, p. ej. `INPUT_NOT_EVALUABLE`), con su etiqueta en `acta_writer._STATUS_LABELS`. Test que atravesaba `collect_reviewer_reports` + `_compute_verdict`: con `extraccion: NO_EVALUABLE` y `findings: []` el acta **no** dice `OK_NO_FINDINGS` y el veredicto **no** es `APROBADO-PARA-ENTREGA`; par rojo/verde en `evidence/FASE-B/`.
- [ ] **Quitar el default `extractor=None → LLMPromiseExtractor()` de `alignment_reviewer.review`**: Bot 4 ya exige el extractor obligatorio (`honesty_reviewer.review` lo documenta: «no existe un default que instancie el LLM real»); el default de Bot 2 permite que un llamador offline dispare una llamada real al proveedor.
- [ ] El cruce matriz→promesa (`_cover_unmatched_entries`) queda intacto y sigue disparando `SIN_BRECHA_ASOCIADA` — el no-OK no apaga la mitad del revisor que hoy sobrevive.
- [ ] ≥1 test contra baseline real (R2.6) con skipif explícito y visible.

### Tarea 2 — Bot 4 consume el estado + texto completo (AC9)

**Archivos afectados**:
- `modules/quality_gates/tribunal/honesty_reviewer.py`
- `tests/quality_gates/tribunal/` (tests del revisor)

**Criterios de aceptación**:
- [ ] Extracción `NO_EVALUABLE`/`FALLIDO` → estado explícito en el report; `TIER_MISMATCH` y los hallazgos que dependen de claims dejan de silenciarse por un no-OK (hoy con `[]` ni siquiera se emiten).
- [ ] El regex de lenguaje de verificación corre sobre el **texto completo** de la propuesta, no solo sobre las citas elegidas por el LLM (N5). Test: una cita omitida por el extractor sigue siendo detectada en texto completo. **Se ejecuta después de T3** por la razón del orden declarado arriba: con el patrón sin ajustar, esta misma decisión produce CRITICAL espurio y suprime el ZIP.
- [ ] **AC18 (contrato de claves del finding)**: los findings de Bot 4 dejan de escribir `"type"` y pasan a `finding_type` (con `clause` y `source_artifact` donde aplique), para que `ACTA_FINDING_KEYS` y `derive_corrective_actions` los nombren. Medido en el acta del 2026-10-07: su único finding se proyecta `finding_type: None`. Coste: re-anclar **8** lecturas de la clave (4 en `test_honesty_reviewer.py`, 1 en `test_honesty_reviewer_fidelidad_salida.py`, 3 en `test_honesty_reviewer_retro_reales.py`). La evidencia se lee en **un acta generada**, no en el string.
- [ ] ≥1 test contra baseline real (R2.6) con skipif explícito y visible.

### Tarea 3 — Superficie de falso positivo del patrón CRITICAL (AC10, cura N7)

**Archivos afectados**:
- `modules/quality_gates/tribunal/honesty_reviewer.py`
- `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-B/medicion-falso-positivo.md`

**Criterios de aceptación**:
- [ ] Medición sobre corpus real de propuestas (propuestas de `output/` y `evidence/` del repo) **con el patrón del código**: la medición importa `verification_patterns` de `honesty_reviewer.py` y lo invoca, en lugar de re-escribir a mano un regex equivalente. Publica **dos cifras** por patrón: ocurrencias literales en el texto vs coincidencias matcheadas. Cifra publicada con su comando.
- [ ] Baseline ya medido el 2026-10-11 sobre la propuesta real del 2026-10-07 (`02_PROPUESTA_COMERCIAL` del run, 14.690 caracteres): el grupo de cuantificadores (100 por ciento, total, absoluto, definitivo) da **5 coincidencias** con **5 literales `total`** (case-insensitive) — «fuga total estimada», «Total recuperación proyectada», «Total CAPEX», «Protección total para usted», «Transparencia total»; 3 son totales financieros o de tabla y 2 son absolutos de prosa — y **0 de sus 5 literales `100%`** están matcheados. El grupo de verificación (`verificad[oa]s?…`) da **1** («Verificado», dentro de «Día 1 (Verificado)»). La auditoría caracterizaba 4 de 5 como financieros o de tabla: re-medido, son 3.
- [ ] **Frontera curada**: `\b` después de `%` exige un carácter de palabra y por eso ningún `100%` matchea — la cura lleva su par rojo/verde (un `100%` en prosa de garantía debe poder volverse CRITICAL si la AC lo pide, y un `total` de tabla debe dejar de serlo).
- [ ] Patrón ajustado con criterio documentado (p. ej., exigir forma de cuantificador porcentual o contexto de garantía) — o decisión de mantenerlo con el riesgo medido y dueño. Ninguna de las dos salidas es «no medido».
- [ ] **Mutation check** del guard CRITICAL: revertir → test rojo; reactivar → verde; ambas salidas en `evidence/FASE-B/`.
- [ ] El comportamiento de bloqueo (`BLOQUEAR` → `verified_critical` → ZIP en cuarentena) queda cubierto por tests que atraviesen la rama real.

### Tarea 4 — Eliminar el wrapper transicional DEC-A1 (AC15)

**Archivos afectados**:
- `modules/quality_gates/tribunal/llm_extractor.py` (solo borrado del wrapper)
- `tests/quality_gates/tribunal/`

**Criterios de aceptación**:
- [ ] `extract_verbal_promises` (wrapper) eliminado; consumidores ya no lo llaman.
- [ ] `grep -c` = 0 del símbolo del wrapper en `modules/` (sin comentarios que lo recuerden).
- [ ] La suite del tribunal queda verde con la API checked como única vía.

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Bot 2 estados no-OK por causa (R2.9) | tests del revisor | NO_EVALUABLE y FALLIDO producen report con estado; OK_SIN_PROMESAS produce sin-hallazgos legítimo |
| Bot 4 ídem + cita omitida detectada | ídem | texto completo cubre la cita que el LLM no eligió |
| Baseline real (R2.6) | ídem | ≥1 test contra artefacto real; skipif visible si no hay |
| Mutation check patrón CRITICAL | ídem | par rojo/verde en evidence/FASE-B/ |
| AC17 — el acta ante extracción no-OK | tests del tribunal | `collect_reviewer_reports` + `_compute_verdict` atravesados: con estado no-OK y `findings: []` el acta JSON no publica `OK_NO_FINDINGS` y el veredicto no es `APROBADO-PARA-ENTREGA`; la etiqueta nueva aparece en el acta MD; par rojo/verde |
| AC18 — finding de Bot 4 nombrado | tests del tribunal | un acta generada proyecta `finding_type` (y `clause` / `source_artifact` cuando apliquen) del hallazgo de Bot 4, no `None` |
| Bot 2 sin default de extractor | ídem | `alignment_reviewer.review` exige el extractor; un llamador offline no puede disparar una llamada real |
| Wrapper eliminado | ídem | grep 0 + suite verde |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/tribunal/ -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** — ver template §5:

1. `dependencias-fases.md`: FASE-B ✅ con fecha y notas.
2. README del plan: progreso; métricas por referencia a `09` §D.
3. `09-documentacion-post-proyecto.md`: secciones A/B/D/E.
4. `10-analisis-post-implementacion.md`: Resumen de Ejecución + lecciones + seguimientos (la medición N7 con su cifra si queda decisión abierta).
5. `00-lecciones-capitalizadas.md` §2: qué pasó realmente.
6. `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-B/`: pares pre/post (R2.3), mutantes, par rojo/verde N7, `medicion-falso-positivo.md`.
7. Registro de fase:
   ```bash
   ./venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-B --fecha <FECHA_DE_CIERRE_DE_ESTA_FASE> \
       --desc "Bot 2/Bot 4 consumen contrato 4 estados; N5 texto completo; N7 medido y ajustado; wrapper DEC-A1 eliminado" \
       --archivos-mod "modules/quality_gates/tribunal/alignment_reviewer.py,modules/quality_gates/tribunal/honesty_reviewer.py,modules/quality_gates/tribunal/llm_extractor.py,modules/quality_gates/tribunal/outcome.py,modules/quality_gates/tribunal/acta_writer.py" \
       --tests <TESTS_NUEVOS_DE_ESTA_FASE> --check-manual-docs
   ```
8. DOMAIN_PRIMER regenerado (`--regenerate-domain-primer`).
9. Pregunta de aporte durable de cualquier `CONTEXT-*.md` escrito en la sesión.

## Criterios de Completitud (CHECKLIST)

⚠️ Ver template §6. Resumen:

- [ ] AC8/9/10/15/17/18 legibles en sus artefactos, **y AC1 cerrado aquí** junto con AC15 (la API checked queda como única vía: su cierre no se certificaba en FASE-A porque DEC-A1 dejaba el wrapper devolviendo `[]`)
- [ ] Tests por estado (R2.9), cruce bidireccional (L-T4A.5), baseline real (R2.6) con skip visible
- [ ] Mutation check N7 con par rojo/verde en evidence/
- [ ] Delta R2.3 verificado restando
- [ ] `--quick` verde; `log_phase_completion.py` ejecutado
- [ ] Cinco cortes declarados; sin commit (requiere autorización + pathspec)

## Restricciones

- **Presupuesto (R2.1)**: ~55 tool calls; unidad `tool calls`; corte: hasta listo para revisión (sin autorización de commit).
- **No tocar** `judge.py` (FASE-C) ni `main.py`. `llm_extractor.py` solo para el borrado del wrapper (T4).
- **No re-activar** el modo de fallo silencioso: el `except` que devuelve el default de «no encontrado» está prohibido (R2.9).
- Citas por símbolo (R2.2). Sin commit sin autorización + pathspec.
- **No delegable a subagente**: la costura compartida de ambos reviewers exige el contexto completo de los dos (regla de decisión del executor); la medición N7 es la única pieza read-only delegable si el presupuesto lo pide, integrada y verificada por el parent.

## Prompt de Ejecución

```
Actúa como agente de implementación del plan CURA-COSTURA-TRIBUNAL-2026-10-11.

Ejecuta únicamente FASE-B del plan .opencode/plans/CURA-COSTURA-TRIBUNAL-2026-10-11/
Lee 01-plan-maestro.md (§1 ACs y §4 restricciones), 00-lecciones-capitalizadas.md (§2 y §4), dependencias-fases.md, 05-prompt-inicio-sesion-fase-A.md (estado heredado de DEC-A1) y el workflow canónico.

OBJETIVO: Bot 2 y Bot 4 consumen el contrato de cuatro estados y dejan de verse sanas ante extracción no-OK; detección de sobre-presentación sobre texto completo; superficie de falso positivo del patrón CRITICAL medida y ajustada; wrapper transicional eliminado.

CONTEXTO:
- Fases previas completadas: Preparación, FASE-A
- Base técnica: alignment_reviewer.py, honesty_reviewer.py, outcome.py, API checked de llm_extractor.py
- No delegates a subagente (costura compartida; excepción read-only: la medición N7 si el presupuesto lo pide)

TAREAS (orden de ejecución obligatorio, la numeración no cambia):
1. T3 Medición y ajuste del patrón CRITICAL con el patrón del código, dos cifras y frontera curada (AC10, mutation check)
2. T2 Bot 4 consume estado + texto completo (AC9) + contrato de claves del finding (AC18)
3. T1 Bot 2 consume estado (AC8) + acta con estado no-OK aprobable no (AC17) + cruce matriz→promesa intacto + quitar el default de extractor
4. T4 Eliminar wrapper DEC-A1 (AC15, cierra AC1)

CRITERIOS:
- AC8/9/10/15/17/18 legibles en artefactos y AC1 cerrado con AC15; tests por causa; baseline real R2.6; delta R2.3; outcome.py y acta_writer.py son edición obligatoria

VALIDACIONES:
- pytest tests/quality_gates/tribunal/ -v
- run_all_validations.py --quick
- log_phase_completion.py --fase FASE-B --fecha <fecha de cierre>
```
