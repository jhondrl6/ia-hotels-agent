# FASE-G — Verificador de cableado y retiro del contrato muerto

**Estado:** PENDIENTE. **Dependencia inmediata:** FASE-F completa (incluida acreditación operativa o pendiente explícito de AC13).
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

1. **PRE e inventario de firmas.** Captura baseline focalizado antes de editar. Construye el inventario completo de callers de `validate`, `detect_pains` y `with_validation` (incluidos aliases, instancias asignadas a `self.*` y wrappers), clasificando cada uno: señal requerida presente, ausente, no aplicable, y clase homónima ajena que debe excluirse. Documenta el rol test/legacy de `CommercialGate._check_whatsapp_verified` sin modificarlo.
2. **Verificador AST (V-1).** Implementa un verificador que descubra la población por AST —sin lista fija de archivos— y exija los kwargs declarados como obligatorios para cada símbolo gobernado, con excepciones tipadas y justificadas. Emite `wiring_report.json` con población descubierta, kwargs exigidos, fuentes, excepciones y límites declarados, y se conecta a `run_all_validations.py --quick` sin debilitar checks existentes ni modificar baselines de validadores.
3. **Retiro del contrato muerto (F-D').** Elimina el parámetro descartado `whatsapp_validation` de `AssessmentBuilder.with_validation` y de sus callers, conservando el dato upstream que alimenta `ValidationSummary`. Inventario de firma antes y después; no borrar variables todavía consumidas ni crear una verdad paralela dentro del builder.
4. **POST, mutaciones y cierre.** AC7: agregar un caller nuevo en un archivo nuevo que omita la señal, u ocultarla tras kwargs opacos, rompe el verificador; los aliases/`self` quedan cubiertos y las clases `validate` no relacionadas excluidas. AC16: inyectar un caller con la firma vieja rompe el contrato; los tests pertinentes pasan. Ejecuta el contrato de cierre completo y actualiza AC7/AC16, PRE/POST, delta y `mutation_report.json`.

## Reglas y límites

- El verificador declara su cobertura medida: qué ve, qué no ve y por qué. Un ✅ no prueba ausencia de callers no gobernados.
- Prohibido convertir el verificador en un allowlist de archivos conocidos, o silenciar un hallazgo con una excepción sin justificación tipada.
- No tocar `TribunalJudge._compute_verdict`, flags de bloqueo, umbrales (0.8 / 0.9) ni `write/publish/suppress`.
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

- [ ] F cerrada; PRE tomado antes de editar y POST conciliado.
- [ ] Inventario de callers completo y clasificado, con exclusiones justificadas.
- [ ] `wiring_report.json` publicado, conectado al quick y con límites declarados.
- [ ] AC7 rojo con caller nuevo en archivo nuevo; AC16 rojo con firma vieja.
- [ ] Parámetro muerto retirado sin verdad paralela ni variable upstream eliminada indebidamente.
- [ ] Legacy `domain_gates` intacto y clasificado; umbrales, Juez y O1 sin cambios.
- [ ] Cierre incremental completo y R2 medido o retirado; H será otra sesión.
