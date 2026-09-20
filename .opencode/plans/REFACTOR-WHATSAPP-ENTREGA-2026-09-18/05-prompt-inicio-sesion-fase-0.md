# FASE-0 — Evidencia del veredicto serializada (entrega publicable)

**Estado:** PENDIENTE. **Dependencia inmediata:** FASE-A completa y FASE-G cerrada (G es la segunda sesión del orden revisado). **Complejidad técnica:** MEDIA técnica / ALTA consecuencia: no cambia decisiones, pero sin ella la entrega publicable es inalcanzable para cualquier hotel con issues críticos. **Modo:** DIRECTO. **R3:** 4 tareas, 0 comandos largos externos.

## Contexto

Lee `01-plan-maestro.md` §1 (fila FASE-0), §4 (AC10, AC12, AC18, AC20), `04-contrato-ejecucion.md`, `00-lecciones-capitalizadas.md` (filas L-E2E.2, L-V.3, L-T2A.2), `dependencias-fases.md` y el workflow canónico. Revalida en disco antes de editar: `_check_vacuous_recall`, `ReviewerReport.to_dict`, `_compute_package_evidence` y el payload del gate report. Evidencia propia: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-0/`.

**Objetivo:** que la evidencia del veredicto sea completa y legible en **las dos ramas** de la decisión (publish y supresión), para que el ZIP pueda publicarse cuando el producto lo merece y para que AC10/AC12/AC18 tengan de dónde leer.

**Causa raíz medida (HEAD `938f59f`, corrida real `output/TAREA7-2026-09-19/`):** `v4_audit/revision_diagnostico.json` contiene un único hallazgo CRITICAL, `VACUOUS_RECALL`, y ese hallazgo basta para suprimir un paquete con producto correcto. El gate viaja con `value: 1.0` y `details: {}` (`gate_report_20260919_150131.json`). En `modules/quality_gates/publication_gates.py` la rama PASSED de `PublicationGatesOrchestrator._critical_recall_gate` construye `details: Dict[str, Any] = {}` y solo lo anota con `critical_issues_count: 0` y `recall_basis: "audit_present_no_critical_issues"` en el camino derivado "cero issues críticos con audit presente". El otro camino a `1.0` es `PublicationGatesOrchestrator._extract_critical_recall`: `critical_issues` NO vacío y `_evident_critical_missed == 0` → `return 1.0`, un recall **fundado** que viaja con `details` vacío. `DiagnosisReviewer._check_vacuous_recall` (`if recall_value == 1.0 and not has_critical_count`) lo interpreta como vacuidad → CRITICAL → `TribunalJudge._compute_verdict` (`if any(r.verified_critical or r.verified_block for r in reviewer_reports)`) → `BLOQUEADO`, y `run_v4_complete_mode` suprime el `.zip.tmp`. Resultado observable en esa corrida: readiness `READY_FOR_PUBLICATION` con 13/13 gates verdes y aun así ZIP suprimido. Cualquier hotel con ≥1 issue crítico y recall 100 % queda bloqueado de fábrica.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`

### Lecciones capitalizadas aplicables

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-E2E.2 | La predicción "el gate ya declara `details`, no dispara" resultó falsa en la corrida real. | Esta fase cierra ese hueco; por eso su verde es el contrafactual, no la ausencia de rojos. |
| L-V.3 | Las predicciones del plan son hipótesis, no hechos. | La hipótesis sobre la serialización se re-mide **antes** de implementar, contra el artefacto producido. |
| L-T2A.2 | Fundado vs vacuo se certificaba solo con fixture. | Aquí se certifica contra el `gate_report` real del 2026-09-19 y su acta. |
| L-VUP-5 | Un contrato ya verde exige mutación para demostrar sensibilidad. | Mutar la anotación del gate debe apagar el contrafactual; si no lo hace, el test no alcanza la rama. |
| DA-P1.4 | La decisión O1 vive en publish, no en write. | Se agrega evidencia en la rama publish sin mover la decisión ni el contrato del packager. |
| L-R.4 | Una regla sin verificador declara expresamente su límite. | Se declara: dos cláusulas siguen `NOT_EVALUABLE` y el hash del publicado depende de que exista cuarentena. |

## Tareas

1. **PRE.** Baseline focalizado antes de editar. Reproduce en memoria el camino del gate con el assessment real de la corrida y confirma cuál de los dos caminos a `1.0` produjo el valor. Verifica que `_build_gate_report_payload` —con su clave `"details": r.details`— ya serializa el diccionario sin filtrar: si se confirma, no se toca el writer del reporte.
2. **Evidencia en el productor y en el acta.** Tres cambios aditivos y nada más. (i) `modules/quality_gates/publication_gates.py`: anotar `critical_issues_count` y un `recall_basis` distinguido (p. ej. `all_critical_issues_detected`) también en el camino fundado de `_critical_recall_gate`, preservando la serialización legacy donde no aplica. (ii) `modules/quality_gates/tribunal/outcome.py`: `ReviewerReport.to_dict()` omite `findings`; serializarlos o una proyección con `finding_type`, `severity`, `clause`, `description` para que el acta muestre causas y no solo conteos. Ojo medido: `to_dict()` alimenta el bloque `reviewer_reports` del acta en JSON y en MD (`ActaWriter._write_md`, vía `ActaWriter._render_reviewer_reports`), así que hay que medir el crecimiento del acta y no duplicar lo que ya escriben los `revision_*.json`. (iii) `main.py`: la rama publish de `run_v4_complete_mode` (`packager.publish`) no registra `package_evidence`; hoy solo se inyecta en la rama de supresión vía `_compute_package_evidence` (`sha256`/`member_count`). Añadirlo en publish para que AC12 pueda certificar hash y conteo del paquete **entregado**.
3. **POST, contrafactual y mutaciones.** Contrafactual obligatorio: reproducir en memoria, **sin escribir en disco**, `TribunalJudge._compute_verdict` sobre `output/TAREA7-2026-09-19/v4_complete/hotel_don_alfonso/v4_audit/acta_revision.json` con y sin el hallazgo `VACUOUS_RECALL`, y registrar el par observado en `baseline_vs_contrafactual.json`. Resultado ya medido el 2026-09-19: con el hallazgo → `BLOQUEADO`; con `details` fundado (y por tanto `findings: []`, `status OK_NO_FINDINGS` y `verdict_recommendation` recalculada a `APROBADO` por `diagnosis_reviewer._compute_verdict`) → `APROBADO-CONDICIONAL-PENDING-ONBOARDING`, no incluido en `BLOCKING_VERDICTS` → publicable. **Advertencia:** hacer cero el `critical_count` sin recalcular la `recommendation` **no basta**, porque `ReviewerReport.verified_block` también bloquea por `recommendation == "BLOQUEAR"`; el mutante debe eliminar el hallazgo y recalcular la recomendación, o el contrafactual sale falsamente negativo. Mutaciones: suprimir la anotación del camino fundado, quitar `findings` de `to_dict()`, quitar `package_evidence` en publish — cada una debe romper una expectativa distinta. Prohibido mutar el árbol `output/TAREA7-2026-09-19/` ni `evidence/FASE-P4/`: acta y `revision_*.json` son solo lectura.
4. **Cierre incremental.** Actualiza AC20/AC12 con par medido, `thresholds.json`, `mutation_report.json` por AC y el estado de este prompt. Registra las observaciones de compatibilidad halladas (ver Tests) como hechos, no como ruido.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`

## Reglas y límites

- Prohibido cambiar `_compute_verdict` del Juez, la tabla de cláusulas, `BLOCKING_VERDICTS`, la regla de primer piso (`_apply_first_floor_rule`), los flags de bloqueo, los umbrales (0.8 / 0.9 / 0.7 / 0.5 / 0.3) ni los contratos `write`/`publish`/`suppress`.
- Prohibido conseguir el verde reduciendo severidades, modificando `DiagnosisReviewer._check_vacuous_recall` para que deje de denunciar, o desactivando `GATE_BLOCKING_ENABLED`.
- El proxy del revisor **también** es imperfecto: trata "recall porque se detectaron todos los críticos" como vacuo. La corrección elegida es en el **productor del dato** (el gate), no aflojar el detector, porque el detector cumple su contrato (un `details` sin conteo es efectivamente inequívoco) y aflojarlo dejaría sin defensa el caso genuinamente vacuo de SR-H2; anotar en el productor hace el dato autoportante y conserva intacta la detección.
- Límite declarado: P6.2 y P6.5 siguen `NOT_EVALUABLE` por diseño (`TribunalJudge._evaluate_p6_2` y la entrada P6.5 de `TribunalJudge._evaluate_clauses`) y `T1_CERTIFIABLE_CLAUSES` son 4. Esta fase **no** las activa; el acta no puede afirmar seis cláusulas certificadas.
- Un bloqueo legítimo conserva su veredicto. Ninguna prueba ejecuta `main.py v4complete`; no hay red ni scraping.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`

## Tests obligatorios

`tests/quality_gates/test_publication_gates.py` (`TestCriticalRecallGate.test_empty_critical_issues_with_audit_passes` aserta `result.details.get("critical_issues_count") == 0` en el camino de cero issues: debe seguir verde, el cambio es aditivo y no una sustitución), `tests/quality_gates/tribunal/test_diagnosis_reviewer.py` (el fixture `audit_with_founded_recall` monta un recall fundado con `critical_issues_count: 3`: ya demuestra que el revisor acepta un conteo >0, reutilizarlo como evidencia de compatibilidad), `tests/delivery/test_p2_cuarentena_zip.py` (su helper `_informe_bloqueante` construye un `VACUOUS_RECALL`), `tests/test_p6r_full_flow_matrix.py`, y cualquier test que aserte la forma exacta del acta o de `reviewer_reports` — descubrirlos por grep, no por lista fija.

Observación medida que la fase debe resolver sin tocar el revisor: el fixture de recall fundado (`audit_with_founded_recall`) empareja `critical_issues_count: 3` con `recall_basis: "audit_present_no_critical_issues"`, una combinación internamente contradictoria que hoy pasa porque el revisor solo mira la presencia de la clave. `tests_baseline_pre.txt` / `tests_baseline_post.txt` con la MISMA selección y entorno, exit codes y sumas; `mutation_report.json` por AC con guard/test/exit codes; `baseline_vs_contrafactual.json` en `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-0/`.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`

## Delegación viable

DIRECTA: la causa raíz y el par contrafactual son decisiones de arquitectura con evidencia en el worktree. `delegate_task` (o `Agent` equivalente) solo para grep read-only de tests que aserten la forma del acta o de `reviewer_reports`, y para inventariar el crecimiento del MD del acta. Brief con objetivo, allowlist, prohibiciones (umbrales, Juez, O1, `output/TAREA7-2026-09-19/`), contrato ya decidido y formato de salida. El principal integra, verifica diff y corre los tests; sin acceso al venv, no reinstalar dependencias.

## Post-ejecución

Cierre según `04-contrato-ejecucion.md` §"Cierre incremental obligatorio" (no se repiten aquí sus 7 puntos), añadiendo: actualizar `06-checklist-implementacion.md`, `dependencias-fases.md`, `README.md`, `09-documentacion-post-proyecto.md`, `10-analisis-post-implementacion.md` y `00-lecciones-capitalizadas.md` con los estados y observaciones realmente medidos. Registro propio sin `--release`:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-0 --desc "REFACTOR-WHATSAPP-ENTREGA: evidencia del veredicto serializada" --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/build_lesson_index.py --check
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/validate_document_integration.py
```

Confirmar REGISTRY sin GAP y TOTAL PASS dinámico. Sin commit, push ni release implícitos; la siguiente fase (B) es otra sesión.

## Presupuesto y checklist

Referencia **60 tool_use hasta el commit de código**; instrumento `evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>`, duración de pared aparte, corte en el commit de código. Sin transcript o con acceso denegado: **FUERA DE SERVICIO (R2.1)** con auto-reporte separado por unidad; nunca estimar cumplimiento.

- [ ] PRE tomado antes de editar y POST conciliado con la misma selección y entorno.
- [ ] Camino real del `1.0` de la corrida identificado y documentado por el símbolo que lo produce (rama de `_critical_recall_gate` o `return 1.0` de `_extract_critical_recall`), no por número de línea (R2.2).
- [ ] Anotación del camino fundado añadida; `test_empty_critical_issues_with_audit_passes` de `test_publication_gates.py` sigue verde.
- [ ] `to_dict()` publica hallazgos (o proyección) con crecimiento del acta medido y sin duplicar los `revision_*.json`.
- [ ] `package_evidence` presente en la rama publish; `write`/`publish`/`suppress` intactos.
- [ ] Contrafactual reproducido en memoria y registrado; mutante con solo cero del conteo verificado como falsamente negativo.
- [ ] Juez, cláusulas, umbrales, `BLOCKING_VERDICTS` y `GATE_BLOCKING_ENABLED` sin cambios; P6.2 y P6.5 declarados no activados.
- [ ] Cierre incremental completo y R2 medido o retirado.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`
