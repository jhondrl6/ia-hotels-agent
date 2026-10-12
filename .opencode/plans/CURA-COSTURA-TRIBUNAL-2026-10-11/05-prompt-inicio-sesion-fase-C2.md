# FASE-C2 — El CRITICAL verificado no pierde fuerza por el estado del insumo (AC19)

**ID**: FASE-C2 (plan CURA-COSTURA-TRIBUNAL-2026-10-11; se ejecuta en una sesión NUEVA, entre FASE-C y FASE-E2E)
**Objetivo**: que un hallazgo CRITICAL de un revisor — o su recomendación `BLOQUEAR` — siga bloqueando el ZIP aunque el estado de extracción de ese revisor sea `INPUT_NOT_EVALUABLE` / `FALLIDO` (AC19). Hoy la fuerza de bloqueo exige `status.is_ok`, así que el gate se afloja justo cuando el proveedor falla.
**Dependencias**: FASE-C ✅ (2026-10-12) — `judge.py` y `outcome.py` ya fueron tocados por esa fase; el árbol abre con sus 18 rutas **sin commit**.
**Duración estimada**: 1 sesión.
**Complejidad**: MEDIA — un predicado compartido por dos consumidores (veredicto y acciones correctivas); nada de I/O nuevo.
**Skill**: `.agents/workflows/phased_project_executor.md` (workflow canónico).

## Contexto

FASE-B escaló al Operador y FASE-C re-escaló el 2026-10-12: `INPUT_NOT_EVALUABLE` corta `APROBADO-PARA-ENTREGA` (fila 4 de la matriz, `blocks_approval`) pero **no suprime el ZIP**. El Operador adoptó la decisión el 2026-10-12: curarlo como fase propia antes del run único, con su AC, porque la corrida de FASE-E2E no se repite.

Medición diferencial ejecutada el 2026-10-12 (mismo hallazgo CRITICAL de Bot 4, cambia solo el estado):

| Estado del revisor con `critical_count=1` y `recommendation=BLOQUEAR` | Veredicto | `blocks_delivery_zip` |
|---|---|---|
| `OK_WITH_FINDINGS` (extracción `OK_CON_PROMESAS`) | `BLOQUEADO` | **True** |
| `INPUT_NOT_EVALUABLE` (`NO_EVALUABLE`) | `APROBADO-CONDICIONAL…` | **False — el ZIP se publica** |
| `INPUT_NOT_EVALUABLE` (`FALLIDO`) | `APROBADO-CONDICIONAL…` | **False — el ZIP se publica** |

Mecanismo: los tres predicados de `ReviewerReport` exigen `status.is_ok` (`outcome.py`) y la fila 2 de `TribunalJudge._compute_verdict` decide con ellos. Es incoherente con N5: el escaneo de texto completo que produce ese CRITICAL **no depende del LLM**, así que exigir la salud del insumo para enforcementarlo no protege nada.

**Lo que esta fase NO cura** (declarado, no silencioso):
- Un revisor no-OK con **solo WARNING** sigue en condicional con ZIP publicable. No es la asimetría que se cura: los WARNING nunca bloquearon el ZIP ni con estado OK (fila 5 de la matriz). Queda como comportamiento medido, no como defecto.
- `S-CST-1` (el gate `hard_contradictions` no puede fallar) sigue abierta con dueño Operador; AC19 vive en el tribunal, no en ese cableado.
- La extensión a la fila 3 (`verified_return_for_tests` sin `is_ok`, que haría que cualquier extracción fallida bloquee el ZIP aunque no haya hallazgos) se **rechaza** con motivo: hace la entrega del run único sensible a un fallo transitorio del proveedor. Se re-evalúa con la evidencia del run.

**Nota de registro**: `FASE-C2` lleva dígitos, así que el desempate `(fecha, dígitos)` del checker la corona sobre FASE-A/B/C si comparten fecha (la lección del desempate ya capitalizada).

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| Preparación / 2 / 2b | ✅ |
| FASE-A / FASE-B | ✅ (publicadas y empujadas, tip `4df81d3`) |
| FASE-C | ✅ (2026-10-12, **sin commit**; 18 rutas en el árbol) |

### Base Técnica Disponible

- `modules/quality_gates/tribunal/outcome.py` — `ReviewerReport.verified_critical` / `verified_block` / `verified_return_for_tests` (las tres exigen `is_ok`); `derive_corrective_actions` salta los reportes no-OK con `continue` (un `BLOQUEADO` de esta cura caería al genérico `VEREDICTO_BLOQUEANTE_SIN_HALLAZGO`).
- `modules/quality_gates/tribunal/judge.py` — fila 2 de `_compute_verdict` y su docstring de la matriz §2.1.
- **Blast radius medido el 2026-10-12**: los tres predicados aparecen en **4** líneas de **2** archivos de test (`test_fase_b_consumidores_contrato.py` y `test_fase_0_ac20_evidencia_veredicto.py`); `INPUT_NOT_EVALUABLE` aparece en 4 líneas de un solo archivo, y su diferencial afirma `acta["verdict"] != VERDICT_APPROVED` (sobrevive a la cura: `BLOQUEADO ≠ APPROVED`). Re-anclaje esperado: **0–2 aserciones**, a confirmar en T0 antes de editar.

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección | Qué cambia en ESTA fase |
|----|---------|------------------------|
| L-CST-3 | El coste declarado de un re-anclaje se mide, no se hereda | T0 re-cuenta los consumidores de los predicados antes de editar y publica la cifra con su comando |
| L-CST-5 / mutante de rama indiferente | Afirmar la etiqueta, no solo el valor; declarar qué diente no cubre cada mutante | El par rojo/verde usa el diferencial de estado (mismo hallazgo, dos estados) y la nota declara qué mutante no puede detectar |
| L-CST-1 | Un guard que nadie dispara no existe | T2 se muta en `derive_corrective_actions`, no en un comentario del Juez |
| L-T4A.5 | Datos que atraviesan la rama real | Los tests construyen el report por la vía real: `collect_reviewer_reports` lee un `revision_honestidad.json` escrito en disco con `extraccion` no-OK |

## Tareas

### Tarea 0 — Pre-imagen y blast radius (sin editar)

- [ ] `grep -rn "verified_critical\|verified_block\|verified_return_for_tests" tests/ --include=*.py` y el conteo de `INPUT_NOT_EVALUABLE` en tests; publicar la cifra en `evidence/…/FASE-C2/pre-imagen.md` junto al `git status` de apertura (18 rutas de FASE-C) y la selección de tests que va a correr.
- [ ] Confirmar (o corregir con evidencia) el re-anclaje esperado 0–2 de la base técnica.

### Tarea 1 — AC19: la fila 2 no exige `is_ok`

**Archivos afectados**: `modules/quality_gates/tribunal/outcome.py`, `modules/quality_gates/tribunal/judge.py` (solo su docstring de la matriz).

**Criterios de aceptación**:
- [ ] `ReviewerReport.verified_critical` y `verified_block` dejan de exigir `status.is_ok`: un `critical_count >= 1` o un `recommendation == BLOQUEAR` bloquean desde cualquier estado leído (`OK_*` e `INPUT_NOT_EVALUABLE`). La exigencia `is_ok` **no** se retira de `verified_return_for_tests` (fila 3, alternativa rechazada arriba).
- [ ] Determinismo preservado: `NOT_RUN` / `READER_FAILED` / `ARTIFACT_MISSING` mantienen conteos 0 y `recommendation=None`, así que **no** pueden bloquear por esta vía (control de los tres estados vacíos). Ausencia jamás es PASS, pero tampoco inventa bloqueo.
- [ ] No se tocan `ReviewerStatus` (enum ni `blocks_approval`), `bloque_extraccion`, `_STATUS_LABELS`, ni el knob `GATE_BLOCKING_ENABLED`.
- [ ] Tests por causa + **mutation check** (restaurar la exigencia `is_ok` en los dos predicados → rojo; reactivar → verde; par en `evidence/FASE-C2/`).

### Tarea 2 — La acción correctiva nombra el hallazgo (no un genérico)

**Archivos afectados**: `modules/quality_gates/tribunal/outcome.py` (`derive_corrective_actions`).

**Criterios de aceptación**:
- [ ] Un reporte no-OK con CRITICAL ya no se salta con `continue`: su hallazgo genera la `CorrectiveAction` con las claves del acta (`finding_type`, `severity`, `source_artifact` — AC18), con el dueño que ya tiene el revisor en `_OWNER_BY_REVIEWER`.
- [ ] El `VEREDICTO_BLOQUEANTE_SIN_HALLAZGO` queda reservado para el caso real de veredicto bloqueante sin documentación, no como disfraz de esta cura.
- [ ] **Mutation check** (restaurar el `continue` por `is_ok` → rojo: el BLOQUEADO queda con la acción genérica; reactivar → verde; par en `evidence/FASE-C2/`).

### Tarea 3 — Verificación leyendo un acta generada (no el string del código)

- [ ] Extremo a extremo: `revision_honestidad.json` escrito en disco con `extraccion` no-OK y un CRITICAL → `collect_reviewer_reports` → `judge.evaluate()` + `enrich` → `ActaWriter` → leer JSON **y** MD: `verdict == BLOQUEADO`, `blocks_delivery_zip(acta) is True`, y la acción correctiva nombra el hallazgo de Bot 4.
- [ ] Control diferencial de no-sobre-bloqueo: el mismo insumo con **solo WARNING** y extracción no-OK sigue en condicional (evita el verde vacuo y el exceso de alcance).
- [ ] Control de los tres estados vacíos: sin conteos no hay bloqueo nuevo.

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Diferencial de estado | tests del tribunal (archivo nuevo) | mismo insumo, solo cambia el estado: `OK_WITH_FINDINGS` → `BLOQUEADO`; `INPUT_NOT_EVALUABLE` (y `FALLIDO`) → `BLOQUEADO` con `blocks_delivery_zip` True |
| Rama real por disco | ídem | el report lo lee `collect_reviewer_reports` desde un JSON escrito en `tmp_path`, no un DTO construido a mano |
| Acción correctiva nombrada | ídem | `derive_corrective_actions` emite la acción del hallazgo de Bot 4, no `VEREDICTO_BLOQUEANTE_SIN_HALLAZGO` |
| No-sobre-bloqueo | ídem | WARNING-only bajo no-OK → condicional; los tres estados vacíos → sin bloqueo; `GATE_BLOCKING_ENABLED=0` sigue anulando (kill switch intacto) |
| Mutation checks ×2 | ídem | pares rojo/verde en `evidence/FASE-C2/` |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/tribunal/ -v
PYTHONUTF8=1 ./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Consideración de subagentes (decisión declarada)

**DIRECTO, sin subagente.** Motivos: (1) la cura vive en un símbolo compartido por dos consumidores (`verified_critical` alimenta el veredicto y `derive_corrective_actions`) — la regla del maestro para costuras compartidas es no delegar; (2) el presupuesto (~35 tool calls) no paga el overhead de un spawn ni de su re-verificación; (3) FASE-B/C midieron que la disciplina de mutantes y re-anclas exige el contexto completo de la sesión; (4) el único punto delegable del plan sigue siendo el run de FASE-E2E. Un `Explore` read-only para el grep de T0 sería más caro que el grep mismo.

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: FASE-C2 ✅ con fecha y notas.
2. README del plan: fila de progreso; métricas por referencia a `09` §D.
3. `09-documentacion-post-proyecto.md`: §A (si aplica), §B (feature nueva), §D (tests nuevos FASE-C2), §E (archivos).
4. `10-analisis`: Resumen de Ejecución + fila 17 de la matriz + la decisión arquitectónica (qué alternativa se rechazó y por qué) + **cierre de la escalada** del seguimiento «INPUT_NOT_EVALUABLE no suprime el ZIP».
5. `00-lecciones-capitalizadas.md` §2: filas L-CST-3 y L-CST-5 con su «Real FASE-C2»; lección nueva si la hay.
6. `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-C2/`: pre-imagen, pares rojo/verde de T1 y T2, acta generada, baseline pre/post.
7. Registro de fase: `log_phase_completion.py --fase FASE-C2 --fecha <FECHA_DE_CIERRE> --desc "CRITICAL verificado bloquea sin importar el estado del insumo; accion correctiva nombrada" --tests <N> --check-manual-docs`.
8. DOMAIN_PRIMER regenerado (`doctor.py --regenerate-domain-primer`).
9. Pregunta de aporte durable de cualquier `CONTEXT-*.md` escrito en la sesión.

## Criterios de Completitud (CHECKLIST)

- [ ] AC19 legible en su artefacto (acta generada + par rojo/verde), no en el string del código
- [ ] La fila 3 queda sin tocar y su rechazo está escrito con motivo
- [ ] Delta R2.3 verificado restando; `--quick` verde; `log_phase_completion.py --fase FASE-C2` ejecutado
- [ ] Cinco cortes declarados; sin commit (requiere autorización + pathspec; el árbol abre con las 18 rutas de FASE-C y se declara si un commit cubre ambas fases)

## Restricciones

- **Presupuesto (R2.1)**: ~35 tool calls; corte: hasta listo para revisión.
- **No tocar**: `ReviewerStatus`/`bloque_extraccion`/`_STATUS_LABELS`, `T1_CERTIFIABLE_CLAUSES`, la fila 3 de la matriz, `honesty_reviewer.py` y `alignment_reviewer.py` (sus estados ya son correctos), `publication_gates.py` y `main.py` (`S-CST-1`).
- Citas por símbolo (R2.2). Sin commit sin autorización + pathspec.
- **No delegable a subagente** (ver sección propia arriba).
