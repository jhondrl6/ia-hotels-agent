# FASE-0 — resultados y observaciones medidas

Plan `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`. Sesión del 2026-09-20 sobre HEAD
`ad0cc84` (árbol limpio al abrir; `66e17bd`, el código de G, ya empujado y en
paridad con `origin/master`). Modo DIRECTO, 4 tareas, 0 comandos largos externos,
**contador v4complete 0/1** (no se ejecutó `v4complete`, ni red, ni scraping).

## 1. Tarea 1 — PRE antes de editar

| Medición | Instrumento | Resultado |
|---|---|---|
| HEAD y estado del árbol | `git rev-parse --short HEAD` / `git status --porcelain` | `ad0cc84`, 0 entradas: nada pendiente ajeno a la fase |
| Quick del repo | `run_all_validations.py --quick` | **11/11** (el guard `Wiring` de G sigue en 169 llamadas / 70 gobernadas / 0 violaciones / 3 omisiones amparadas con dueño FASE-B) |
| Baseline de la corrida | `output/TAREA7-2026-09-19/` | 60 archivos; `gate_report_20260919_150131.json` → `critical_recall` con `value: 1.0, details: {}`; `acta_revision.json` → `BLOQUEADO`, tier B, `package_evidence.suppressed: true` (sha `4847cc…`, 52 entradas) |
| Pytest PRE (selección literal de 12 archivos) | `tests_baseline_pre.txt` | **189 passed, 1 skipped**, 3.67 s |
| Suite nueva contra el árbol HEAD sin el fix | `git archive HEAD` extraído en temporal + `pytest` | **16 failed, 3 passed, 2 skipped** (bloque PRE-c del mismo archivo). 13 rojos por aserción y 3 por `ImportError` del helper nuevo — los 3 no cuentan como prueba de guard |

**Camino real del `1.0`, identificado por el símbolo que lo produce (R2.2), no por
número de línea** (`pre_camino_gate.json`):

`PublicationGatesOrchestrator._extract_critical_recall` → rama
`if critical_issues:` → `return 1.0  # All critical issues were detected`, es decir
**recall FUNDADO**. Descartados por medición los otros dos candidatos: el campo
directo `assessment["critical_recall"]` no existe en el payload del builder, y el
camino derivado SR-H2 exige `critical_issues` vacío con audit presente.

Reconstruido con el `AssessmentBuilder` real sobre el `audit_report_20260919_150111.json`
archivado, el gate reproduce **exactamente** lo serializado aquel día:
`value: 1.0, details: {}` (`coincide_con_el_archivo: true`). Y el writer del
reporte **ya** serializa `details` sin filtrar: `"details": r.details` dentro de
`main._build_gate_report_payload`, verificado leyendo la fuente de la función.
**El writer del reporte no se tocó**, como sospechaba el prompt.

## 2. Tarea 2 — los tres cambios aditivos

| # | Símbolo | Qué se agregó | Qué NO se tocó |
|---|---|---|---|
| i | `PublicationGatesOrchestrator._critical_recall_details` (nuevo, llamado solo desde la rama PASSED de `_critical_recall_gate`) | `critical_issues_count` + `recall_basis` en el camino fundado (`all_critical_issues_detected`) y en el de críticos evidentes no cubiertos (`evident_critical_issues_missed`, con `evident_critical_missed`). SR-H2 conserva su base `audit_present_no_critical_issues`; los casos no fundamentados siguen con `details: {}` | `_extract_critical_recall`, el umbral, `passed`, `status`, `message`, `value` |
| ii | `ReviewerReport.to_dict` | `findings` proyectado con lista blanca `ACTA_FINDING_KEYS` (`finding_type`, `severity`, `clause`, `description`), truncado a `ACTA_FINDING_TEXT_LIMIT = 240` y tope `ACTA_FINDING_CAP = 20` con `findings_omitted` cuando se supera | `verified_critical`, `verified_block`, `verified_return_for_tests`, `report_from_payload`, `_compute_verdict` |
| iii | `main._record_published_package_evidence` (nuevo) + su llamada tras cada `packager.publish(` | `package_evidence` con `suppressed: False`, `path` de la ruta publicada, `sha256` y `member_count` del **ZIP entregado**, en **las dos** ramas de publicación: la normal y el `except` never-block del enriquecimiento | `write`/`publish`/`suppress`, la decisión `_outcome.blocks_publish`, el orden decisión→rename |

## 3. Tarea 3 — POST, contrafactual y mutaciones

**Contrafactual (`baseline_vs_contrafactual.json`, copia temporal, `output/` intacto):**

| Caso | Hallazgos `VACUOUS_RECALL` | Recomendación del Bot 1 | Veredicto de `TribunalJudge._compute_verdict` | ¿En `BLOCKING_VERDICTS`? |
|---|---|---|---|---|
| A baseline archivado | 1 | `BLOQUEAR` | `BLOQUEADO` | sí |
| B con la anotación del productor | 0 | `APROBADO` (`status OK_NO_FINDINGS`) | `APROBADO-CONDICIONAL-PENDING-ONBOARDING` | **no** → publicable |
| C mutante engañoso: `critical_count = 0` sin recalcular la recomendación | — | `BLOQUEAR` | `BLOQUEADO` | sí |

C confirma la advertencia del prompt: el par exige **eliminar el hallazgo y
recalcular la recomendación**; cero-del-conteo por sí solo deja el contrafactual
falsamente negativo, porque `ReviewerReport.verified_block` decide por la
recomendación.

**Crecimiento del acta, medido sobre el acta real de la corrida:** JSON
1.362 → 2.513 bytes (**+1.151, +84 %**), MD **0 bytes** de delta
(`ActaWriter._render_reviewer_reports` renderiza una tabla y no consume
`findings`). Los cuatro `revision_*.json` de esa corrida suman 9.155 bytes, así
que la proyección añade ~12 % de ese material y no lo duplica: son cuatro claves
por hallazgo, con descripción acotada.

**Mutaciones (`run_mutations.py` → `mutation_report.json`): 6/6 rompieron, todas
por el guard, y `todo_restaurado: true` verificado por sha256.**

| ID | Mutación | Rojo | Prueba |
|---|---|---|---|
| M1 | apagar la anotación del camino fundado | 5 failed | `TestAnotacionDelCaminoFundado`, `TestCaminoFundadoSobreBaselineReal` |
| M2 | quitar `findings` de `to_dict` | 7 failed | `TestToDictPublicaHallazgos`, `TestActaPublicaLaCausa`, AC-E1 (forma del acta) |
| M3 | quitar la llamada de evidencia junto al `publish` de la rama normal | 1 failed | `TestCableadoPublishPublicaEvidencia` (regla AST propia) |
| M4 | el helper sigue llamado pero ya no anota | 2 failed | `TestPackageEvidenceEnRamaPublish` |
| M5 | **prohibida por el plan**: relajar `_check_vacuous_recall` | 3 failed | `test_recall_declarado_sin_lista_sin_audit_sigue_vacio` + suite del revisor |
| M6 | **prohibida por el plan**: sustituir (no sumar) la serie SR-H2 | 3 failed | `TestCriticalRecallGate::test_empty_critical_issues_with_audit_passes` |

M5 y M6 no compran verde: se aplicaron para demostrar que los tests que vigilan
esos dos límites están vivos. Todas se ejecutaron sobre copia temporal de los
archivos mutados con respaldo byte-a-byte, restauración y verificación sha256;
el acta y los `revision_*.json` del baseline nunca se escribieron (60 archivos y
`details: {}` re-verificados al cerrar).

**POST de la selección (misma selección y entorno que PRE):**

| corrida | selección | resultado |
|---|---|---|
| PRE | 12 archivos literales | 189 passed, 1 skipped, exit 0 |
| POST-B | los mismos 12 archivos, código de la fase ya aplicado | **189 passed, 1 skipped** — delta 0 |
| POST-A | selección + `tests/test_fase_0_ac20_evidencia_veredicto.py` (21 funciones) | **210 passed, 1 skipped**, exit 0 |
| funciones canónicas (`grep -rE "^\s*def test_" tests --include=*.py`) | HEAD `ad0cc84` → árbol de la fase | 4.264 → **4.285** (+21, todas de esta fase) |

El delta 0 no fue gratis: ver observación O4.

## 4. Observaciones medidas (no rumoreadas)

**O1 — el conteo que ahora publica el acta es 4, no 3.** El `audit_report`
archivado lista 3 `critical_issues`, pero `AssessmentBuilder.with_geo_flow`
(FASE-G) anexa el de banda GEO antes de correr los gates: 4 al momento del gate.
La medición M2 del plan decía "un único CRITICAL `VACUOUS_RECALL`" y seguía
siendo cierta para el acta; el número que publicará `details` en una corrida de
hoy es el de la lista efectiva del assessment. Ninguna cifra del plan se
propaga como hecho presente.

**O2 — aliasing entre el auditor y el assessment.** `with_audit` asigna la misma
lista de `audit_result.critical_issues` y `with_geo_flow` hace `.append` sobre
ella, así que el geo-flow muta el objeto del auditor. Lo detecté porque mi propia
medición del delta salía 0. Fuera del alcance de FASE-0: se registra con dueño
implícito (B/C tocan esa superficie) y no se cambia.

**O3 — el writer del reporte no era el problema.** `"details": r.details` ya
viajaba completo; el hueco estaba exclusivamente en el productor. El prompt lo
planteaba como hipótesis a re-medir (L-V.3) y aquí se confirmó con la fuente leída.

**O4 — un test pineaba la forma exacta del bloque `reviewer_reports`.**
`test_reviewer_reports_refleja_los_cuatro_revisores` asertaba
`set(entry) == {6 claves}`. Cualquier clave nueva del acta lo rompe por
re-numeración y no por el contrato: el mismo mecanismo que en G dejó rojo
`test_registrado_como_check_5_en_el_hook` (`L-V2.3`). Se re-ató a la regla
declarada (superconjunto de las seis heredadas + `findings`,
`findings_omitted` opcional, y coherencia interna `len(findings) <= findings_count`).
La aserción de que hay cuatro entradas, una por Bot, sigue intacta.

**O5 — el fixture de recall fundado se auto-invalidaba.** `audit_with_founded_recall`
emparejaba `critical_issues_count: 3` con
`recall_basis: "audit_present_no_critical_issues"`, que es la base del camino de
cero críticos. Pasaba porque el revisor solo mira la presencia de la clave. Se
corrigió el fixture hacia `all_critical_issues_detected` — el revisor no se tocó
y la aserción no se debilitó: ahora el fixture describe lo que el productor
produce, y sirve de evidencia de compatibilidad (count > 0 aceptado).

**O6 — `publish()` es un `rename`, así que la evidencia se calcula sobre la ruta
publicada.** Mismos bytes que la cuarentena y, además, el archivo que recibe el
cliente. En la rama de supresión se calcula antes del `unlink`, como ya hacía
AC-G3. Las dos ramas quedaron cubiertas, que es lo que la rectificación de A
exigía (no una sino dos ramas de `main.py`).

**O7 — el rojo heredado de G sigue rojo y no se arrastró a la selección.**
`test_medido_contra_el_predecesor_entra_en_alcance_y_su_forma_es_conforme[2026-09-11-TRIBUNAL-ENFORCEMENT-OBS-2026-09-11]`:
1 failed, 1 skipped, 4.293 deselected. Causa ya medida en G (`9c4a001` archivó el
plan y `clasificar_planes` solo mira hijos directos de `.opencode/plans/`). Dueño
distinto; no se excluyó ni se maquilló.

**O8 — accidente registrado: una `git stash --include-untracked` sobre el worktree
en curso.** La usé para medir el conteo canónico de HEAD y era un riesgo
innecesario sobre trabajo sin commitear. Se revirtió con `git stash pop` en la
misma sesión y se verificó la restauración (5 archivos modificados + 2 nuevos, y
`main.py`/`publication_gates.py`/`outcome.py` con sus símbolos de la fase
presentes). La medición de HEAD se rehízo sin tocar el árbol, con
`git grep -h -E "^[[:space:]]*def test_" HEAD -- tests`. Lección de proceso: para
medir el estado anterior existe `git grep <rev>` y `git archive`, no `stash`.

## 5. Límites declarados de esta fase

- P6.2 y P6.5 siguen `NOT_EVALUABLE` por diseño y `T1_CERTIFIABLE_CLAUSES` son
  4 (`P6.1, P6.3, P6.4, P6.6`). **Esta fase no las activó**: el acta no puede
  afirmar seis cláusulas certificadas.
- `BLOCKING_VERDICTS` medido hoy: `{BLOQUEADO, DEVOLVER-CORRECCIONES}` — intacto.
- El hash del paquete publicado depende de que el archivo exista al anotar: si
  `publish()` renombra y algo borra el ZIP antes de la anotación,
  `package_evidence` viaja con `sha256: null` y su `error` (caso cubierto por
  `test_paquete_inexistente_viaja_con_error_declarado`).
- El tope de 20 hallazgos por revisor es un techo declarado, no una garantía de
  que el acta liste todas las causas de un revisor ruidoso; `findings_omitted`
  dice cuántas faltan.
- Nada de esto certifica la rama E2E: FASE-0 corre offline sobre artefactos
  archivados. AC20 queda VERIFICADO OFFLINE hasta que E2E lo ejercite en la
  corrida única, y `APROBADO-CONDICIONAL-PENDING-ONBOARDING` es el techo real con
  tier B.

## 6. Cierre incremental y R2

| Paso del contrato | Comando | Resultado medido |
|---|---|---|
| Registro de fase | `log_phase_completion.py --fase FASE-0 --desc "REFACTOR-WHATSAPP-ENTREGA: evidencia del veredicto serializada" --archivos-mod (5 rutas) --archivos-nuevos (1) --tests 21 --check-manual-docs` | **Registrado en `REGISTRY.md`; auditoría de documentación huérfana: 0 gaps** |
| Índice de lecciones | `build_lesson_index.py` y `--check` | **320 IDs** (319 → 320: nace `L-ENT.15`), «citados sin definición» sigue en **48** — ninguna cita huérfana nueva |
| Validación rápida | `run_all_validations.py --quick` | **10/11** al primer intento y **11/11** al resolver con su escritor (O9). `Plan Citations`: 743 citas históricas, **0 nuevas y 0 crecimientos** |
| Integración documental | `validate_document_integration.py` | All checks passed |
| Cierre de planes | `validate_plan_closure.py` | OK: ningún plan vivo declara cierre con filas pendientes (el bloque «Inicio de la siguiente sesión» del README quedó reescrito para FASE-B) |
| DOMAIN_PRIMER | `doctor.py --regenerate-domain-primer` | Writer ejecutado (mandato resuelto por A: regenerar al cerrar fase de implementación). **Salida idéntica: el archivo no aparece modificado en `git status`** — 206 archivos Python, 390 clases en 25 módulos; la fase no añadió módulo ni clase gobernable |
| QMind | — | **Sin subir.** La consulta no autoriza ingesta y el título de esta fase no está pre-acordado; el de G ya existe y `--upload` respondería SKIP. RELEASE necesita autorización propia y el disparador del mini-plan `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` (sesión previa a RELEASE) |
| Commit / push | — | **No ejecutados: no pedidos.** El árbol queda con 3 archivos de producto, 2 tests re-atados, 1 suite nueva y 11 archivos de evidencia/documentación como checkpoint |

**O9 — el rojo de los dos escritores de `REGISTRY.md` se volvió a encontrar, y se resolvió con su escritor.** Tras `log_phase_completion.py`, el quick dio **10/11** con `FAIL: docs/contributing/REGISTRY.md (registry_last_update)`: la entrada estampa la fecha del día y `sync_versions.py` valida contra el ancla `date` fijada en `VERSION.yaml`. Ya medido y documentado en G; la cura registrada es el escritor oficial acotado — `sync_versions.py --rule registry_last_update` → 7/7 in sync → quick **11/11** — y no un edit manual de la fecha ni tocar configuración central. Esta fase lo re-confirma como recaída prevista del diseño, no como defecto nuevo.

**O10 — el DOMAIN_PRIMER se regenera por su writer y esta fase no le añade nada.** Ejecutado el mandato de A, el contenido quedó idéntico. Eso no es un paso omitido: es la comprobación de que el plan no cambió módulos ni clases gobernaria, dicha con el conteo del propio writer.

**R2 (presupuesto e instrumento): métrica FUERA DE SERVICIO (R2.1).** `evidence/FASE-D/measure_iterations.py` exige el transcript de la sesión y su acceso no estuvo disponible; no se reintentó ni se evadió. **Auto-reporte en unidad propia, no comparable con la referencia de 60 tool_use**: ~45 intervenciones de herramienta contadas a mano, de las cuales ~28 hasta el último estado de código y el resto en cierre documental. **Corte de código = NO CONSUMADO**: no hay commit de la fase, así que el corte del instrumento tampoco existe (no se declara consumado sin autorización, contrato §"Inicio de cada fase" 5). Duración de pared registrada aparte: suite focalizada ~4 s por corrida, regresión completa 232 s, batería de mutaciones ~12 s.

**Postura final de la fase.** AC20 **VERIFICADO OFFLINE** con su par medido; AC12 **PARCIAL** (rama publish cubierta offline, par de flujo real pendiente de E2E); AC15 verificado con PRE/POST de la misma selección y delta explicado; regla de decisión, umbrales y contratos de cuarentena **intactos y verificados**. Lo que la fase **no** afirma: que una corrida real publique — eso solo lo dice la corrida única con su acta.

