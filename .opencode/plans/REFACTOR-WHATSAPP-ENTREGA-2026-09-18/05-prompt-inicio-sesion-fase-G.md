# FASE-G — Verificador de cableado y retiro del contrato muerto

**Estado:** PENDIENTE. **Dependencia inmediata:** FASE-A completa (matriz ratificada). G es ahora la **segunda sesión** del plan — cadena `A → G → 0 → B → C → D → E → F → H → E2E → VERIFY → RELEASE`—: adelanta porque su verificador es el guard de las ediciones de B–F y, por tanto, corre **antes** de FASE-0, de B y de F; no depende de F ni de su acreditación operativa.
**Complejidad técnica:** ALTA: descubrimiento de población sin lista fija, riesgo de falsos verdes y limpieza de firma cross-module.
**Scope R3:** 4 tareas, 0 comandos largos externos. Una sesión exclusivamente para G.

## Contexto e inicio

Ejecución futura con mandato propio. Lee `01-plan-maestro.md` §1 (filas F-A', F-D'), §2 y §4 (AC7, AC16); `04-contrato-ejecucion.md`; `00-lecciones-capitalizadas.md`; checklist; dependencias y el workflow canónico.
Revalida en disco antes de editar: `CoherenceValidator.validate`, `PainSolutionMapper.detect_pains`, `AssessmentBuilder.with_validation`, `V4DiagnosticGenerator._identify_brechas`, `V4AssetOrchestrator.generate_assets`, `run_v4_complete_mode` y el check legacy `CommercialGate._check_whatsapp_verified` en `domain_gates.py`.
El objetivo es estructural: que la omisión de una señal necesaria sea **detectable por un verificador**, no por un test escrito a mano para cada caller. No se añade una segunda fuente de verdad ni se reintroduce el parámetro muerto como dato paralelo.
Evidencia propia: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-G/`.

### Lecciones capitalizadas aplicables

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-NC6 | El cable perdido se busca en el caller, no creando otra fuente. | AC7 descubre la población de callers; AC16 retira el argumento muerto sin inventar datos en el builder. |
| L-R.4 | Una regla sin verificador declara expresamente su límite. | `wiring_report.json` publica cobertura real, excepciones tipadas y lo que el AST **no** puede ver (kwargs opacos, dispatch dinámico). |
| L-T4A.5 | Un test verde puede no alcanzar la rama que dice certificar. | El verificador se prueba con un caller nuevo en archivo nuevo; no con el caller ya corregido en B/D. |

## Tareas

1. **PRE e inventario de firmas.** Captura baseline focalizado antes de editar. Construye el inventario completo de callers de `validate`, `detect_pains` y `with_validation` (incluidos aliases, instancias asignadas a `self.*` y wrappers), clasificando cada uno: señal requerida presente, ausente, no aplicable, y clase homónima ajena que debe excluirse. La matriz de cableado debe cubrir también los **productores de promesas** del inventario actualizado de B (`preflight_checks.NEW_HOTEL_THRESHOLDS`, `ELEMENTO_KB_TO_PAIN_ID` y sus llamadas a `detect_pains`, las ramas WhatsApp de `V4ProposalGenerator._generate_dynamic_services_table`, `ASSET_CATALOG["whatsapp_button"]` y el `PAIN_TO_ASSET` de `ConditionalGenerator`, que hoy no tiene clave `no_whatsapp_visible`): el verificador gobierna señales por productor, no solo por símbolo. Documenta el rol test/legacy de `CommercialGate._check_whatsapp_verified` sin modificarlo. **Caso rojo contra la divergencia vigente:** la divergencia real que hoy mide el repo está en `modules/asset_generation/v4_asset_orchestrator.py`, donde `V4AssetOrchestrator.generate_assets` invoca `detect_pains(audit_result, validation_summary, analytics_data)` **sin** `whatsapp_html_detected` —parámetro que sí existe en la firma de `PainSolutionMapper.detect_pains` y que `V4DiagnosticGenerator._identify_brechas` sí propaga—. El verificador debe demostrar su rojo **sobre esa invocación tal como está hoy, antes de corregirla**: si en el código actual sale verde, la cobertura del verificador está mal, no el producto.
2. **Verificador AST (V-1).** Implementa un verificador que descubra la población por AST —sin lista fija de archivos— y exija los kwargs declarados como obligatorios para cada símbolo gobernado, con excepciones tipadas y justificadas. Emite `wiring_report.json` con población descubierta, kwargs exigidos, fuentes, excepciones y límites declarados, y se conecta a `run_all_validations.py --quick` sin debilitar checks existentes ni modificar baselines de validadores.
3. **Retiro del contrato muerto (F-D').** Elimina el parámetro descartado `whatsapp_validation` de `AssessmentBuilder.with_validation` y de sus callers, conservando el dato upstream que alimenta `ValidationSummary`. Inventario de firma antes y después; no borrar variables todavía consumidas ni crear una verdad paralela dentro del builder.
4. **POST, mutaciones y cierre.** AC7: agregar un caller nuevo en un archivo nuevo que omita la señal, u ocultarla tras kwargs opacos, rompe el verificador; los aliases/`self` quedan cubiertos y las clases `validate` no relacionadas excluidas. AC16: inyectar un caller con la firma vieja rompe el contrato; los tests pertinentes pasan. Ejecuta el contrato de cierre completo y actualiza AC7/AC16, PRE/POST, delta y `mutation_report.json`.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`

## Reglas y límites

- El verificador declara su cobertura medida: qué ve, qué no ve y por qué. Un ✅ no prueba ausencia de callers no gobernados.
- Prohibido convertir el verificador en un allowlist de archivos conocidos, o silenciar un hallazgo con una excepción sin justificación tipada.
- No tocar `TribunalJudge._compute_verdict`, flags de bloqueo, umbrales (0.8 / 0.9) ni `write/publish/suppress`.
- **AC20 no es de G:** la serialización de la evidencia del veredicto (acta, `reviewer_reports[].findings`, `package_evidence`, `details` del gate `critical_recall`) es propiedad de FASE-0. G corre antes y no la toca ni la declara cubierta.
- El módulo legacy de `domain_gates.py` se conserva sin cambios; no archivarlo en esta fase ni usar sus tests como certificación del check productivo.
- Ninguna prueba ejecuta `main.py v4complete`; no hay red ni scraping.

## Tests obligatorios

Suites descubiertas de `tests/commercial_documents/`, `tests/asset_generation/`, `tests/data_validation/` y tests de validadores/scripts, con `./venv/Scripts/python.exe`. El verificador se prueba sobre fixtures de código en archivos temporales y sobre el repo real; el caso rojo usa un caller **nuevo**, no el ya corregido.
`tests_baseline_pre.txt` / `tests_baseline_post.txt` con misma selección y entorno, exit codes y passed/failed/skipped/xfailed/xpassed; delta explicado.
`mutation_report.json`: desactivar el verificador, permitir kwargs opacos o reintroducir la firma vieja deben fallar por la aserción correspondiente, no por syntax/import.

## Delegación viable

DIRECTA para el diseño del verificador y la limpieza de firma. `delegate_task` (o `Agent` equivalente) solo para inventarios read-only independientes de símbolos y callers, sin edición ni imports pesados. Brief con objetivo, allowlist, prohibiciones, contrato decidido y formato de salida. El principal decide exclusiones, verifica diff y ejecuta los tests; si el delegado no accede al venv, no reinstalar dependencias.

## Post-ejecución

Actualizar estado de este prompt, checklist, dependencias, índice del plan, 00/09/10 con al menos tres observaciones medidas; subsección G en CHANGELOG bajo versión vigente y nota en `docs/GUIA_TECNICA.md`. Sustituir variables por datos medidos; registro propio sin `--release`:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-G --desc "REFACTOR-WHATSAPP-ENTREGA: verificador AST de cableado y retiro de parámetro muerto" --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/build_lesson_index.py --check
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/validate_document_integration.py
```

Confirmar REGISTRY sin GAP y TOTAL PASS dinámico; el nuevo check debe quedar verde por cobertura real, no por excepción amplia. DOMAIN_PRIMER solo por writer según resolución de A. Write-back solo autorizado y saneado. No commit, push ni release implícitos.

## Presupuesto y checklist

Referencia **60 tool_use hasta el commit de código**; instrumento `evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>`, duración de pared aparte. Sin transcript o con acceso denegado: **FUERA DE SERVICIO (R2.1)** con auto-reporte separado por unidad; nunca estimar cumplimiento.

- [ ] A cerrada con la matriz ratificada; PRE tomado antes de editar y POST conciliado.
- [ ] Inventario de callers completo y clasificado, con exclusiones justificadas.
- [ ] `wiring_report.json` publicado, conectado al quick y con límites declarados.
- [ ] AC7 rojo con caller nuevo en archivo nuevo y rojo ya demostrado sobre la divergencia actual de `V4AssetOrchestrator.generate_assets`; AC16 rojo con firma vieja.
- [ ] Parámetro muerto retirado sin verdad paralela ni variable upstream eliminada indebidamente.
- [ ] Legacy `domain_gates` intacto y clasificado; umbrales, Juez y O1 sin cambios; serialización del acta (AC20) sin tocar, es de FASE-0.
- [ ] Cierre incremental completo y R2 medido o retirado; FASE-0, B y H serán otras sesiones.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`
