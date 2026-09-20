# FASE-A — Contratos, baseline y prerrequisitos

**Estado:** EJECUTADA 2026-09-19 con **checkpoint documental pendiente de autorización de commit** (HEAD `d4dacb4`, contador **0/1**). Evidencia: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-A/` (`decisiones.md`, `baseline_inventory.json`, `qmind-consulta-reintentada.md`, `tests_pertinentes_pre.txt`). Las cuatro ratificaciones (§3 de `decisiones.md`) se cerraron sin reinterpretar; los textos de "13/13 gates verdes" quedan rectificados a **10 PASSED + 3 WARNING, 0 fallidos** y AC20 (iii) incorpora la tercera ruta de publicación (el `except` never-block de `main.py`). **Dependencias:** preparación leída y mandato de ejecutar A. **Complejidad técnica:** ALTA por decisiones cross-module, datos reales y seguridad. **Modo:** principal DIRECTO; delegate_task solo para recuperaciones independientes read-only, nunca para decidir arquitectura. **R3:** 4 tareas, 0 comandos largos externos.

## Contexto

Lee `01-plan-maestro.md`, `04-contrato-ejecucion.md`, `00-lecciones-capitalizadas.md`, 09/10 y el workflow `.agents/workflows/phased_project_executor.md`. Esta sesión ejecuta solo A: contratos y baseline, no los fixes ni la corrida.

### Lecciones capitalizadas aplicables

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-NC6 | El cable perdido se busca en el caller, no creando otra fuente. | Congelar productores de AC1/AC7, incluido detect_pains y no solo validate. |
| L-V.1 | Contenido y layout reales son dos ejes distintos del contrato. | AC10 parte del writer ya corregido P6-R; no del stub histórico. |
| L-VUP-9 | Los comandos delegados deben usar flags comprobados. | Ratificar parser/loader para AC14/AC17 sin ejecutar el comando largo. |
| L-R.4 | Una regla sin verificador declara expresamente su límite. | Registrar límites del futuro AST, contador y baseline. |
| L-E2E.2 | La predicción de que "el gate ya declara `details` y el recall vacuo no dispara" la refutó una corrida real. | A ratifica FASE-0/AC20 y deja de tratar las predicciones del plan como hechos. |

## Tareas

1. **Baseline y mapa de fuentes.** Registrar HEAD, status, quick PRE y pares de tests pertinentes antes de crear nuevos tests. Leer síntomas en artefactos P4 permitidos sin abrir logs crudos; inventariar hash/ruta, no modificar esa evidencia. Contrastar writer P6-R y sanitización vigente. Producir `baseline_inventory.json` y `decisiones.md` bajo evidencia de A.
2. **Ratificar contrato de fixes.** Validar la matriz del maestro: ausencia→setup; conflicto→guía sin número elegido; presencia no es confianza; botón solo con dato utilizable. Registrar aprobación/rectificación de F-F ampliada + F-A' + V-1, F-D', conservación del módulo legacy y F-B/F-E diferidas con dueño/AC. No codificar F-B sin decisión de privacidad escrita. Confirmar campos propuestos de reportes y la frontera snapshot privado/ZIP exportable. Ratificar además los cuatro puntos de la revisión 2 del maestro, sin reinterpretarlos: (a) la **FASE-0** nueva y su **AC20** (serialización de la evidencia del veredicto en las dos direcciones de la decisión); (b) la división de AC19 en **AC19a** (aditiva, dentro de C) y **AC19b** (migración al tri-estado: deuda diferida con dueño, no es fase); (c) la meta de E2E **re-anclada**: el objetivo certificable es un ZIP publicado con veredicto no bloqueante (`APROBADO-CONDICIONAL-PENDING-ONBOARDING`), no `READY`, porque el tier A exige GA4+GSC conectados y hoy el tier sale **B por defecto**; (d) el nuevo orden de sesiones **A → G → 0 → B**. Si el operador cambia la decisión, actualizar prompts afectados antes de B; no reinterpretar restricciones.
3. **Resolver prerrequisitos operativos.** Primer sub-paso obligatorio: releer `output/TAREA7-2026-09-19/` (corrida real de `v4complete` del 2026-09-19 15:01 sobre el mismo hotel y la misma URL) y registrarla como **baseline medido del plan**, sin modificar sus artefactos; el §7 del maestro fue corregido precisamente porque esa corrida ya refutaba varias premisas del §1. Reintentar además la consulta al notebook QMind `iah-cli-lecciones` (nb `01a04d98-b7bd-778c-8441-26fdc7e35f45`) que esta sesión no pudo ejecutar porque el clasificador de permisos la denegó, y registrar el resultado en cualquiera de los dos casos: recuperado o vuelve a estar denegado. Seleccionar exactamente la observación Hotel Don Alfonso, conservar valores y 2026-07-22; registrar el vínculo de URL indicado por el usuario, no una redirección supuesta. Evaluar necesidad de reconfirmación de vigencia y estado de `ONBOARDING_FRESHNESS_HOURS` sin imprimir secretos. ~~Pedir al operador evidencia de revocación de la key expuesta, no su valor.~~ **RESUELTO (2026-09-19): el operador confirmó la rotación de la key Gemini-local (AIzaSyDq…) el 2026-09-18, con ocasión de la intervención previa; registrado en `evidence/FASE-P5/AC-S3-S4-inventario-superficie.md` (§2, rotación; §5, criterios de cierre). A no la vuelve a pedir: referencia el registro y lo pasa a F/H como acreditación por afirmación del operador (no inferible del repo). La revocación de la key en `archives/gbp_profiles.json` no aplica: es el key estático firmado de Google en HTML scrapeado, no credencial del operador.** Re-medir el quick al inicio: el 9/10 del 2026-09-18 era cuatro documentos sucios en el árbol y hoy da 10/10 con esos archivos idénticos a HEAD, así que no se pide autorización central por ese concepto. Si el rojo reaparece, leer `_check_version_sync` completa antes de atribuirle una causa y solo entonces escalar al operador. Resolver también la divergencia de instrucciones sobre regeneración DOMAIN_PRIMER (cada fase frente a solo RELEASE) sin editar workflow ni AGENTS por cuenta propia.
4. **Cierre.** Registrar decisiones cerradas y las que siguen bloqueadas; actualizar checklist/dependencias/00/09/10 y docs incrementales conforme al contrato. A no está completa si queda abierta una decisión necesaria para B o para el cierre verde. No esperar al intento E2E para descubrir identidad o privacidad.

## Tests y evidencia obligatorios

Verificar sin red las superficies actuales de `tests/regression/test_whatsapp_conflicts.py`, `tests/commercial_documents/test_promised_assets_production.py`, `tests/asset_generation/test_site_presence_adapter.py`, `tests/test_p6r_full_flow_matrix.py`, `tests/quality_gates/test_publication_gates.py`, `tests/quality_gates/tribunal/test_diagnosis_reviewer.py` y `tests/auditors/test_p5_ac_s1_secret_sanitization.py`; las dos del gate y del revisor se inspeccionan solo en lectura porque son la superficie que FASE-0/AC20 gobernará. Ajustar la selección si el inventario real lo requiere y registrar la selección exacta. No declarar que pruebas no ejecutadas pasaron. Un test con imports/red involuntaria se aísla o se reporta, no consume v4complete.

Evidencia: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-A/`. AC14 queda preparado, no certificado E2E. Guardar respuestas de producto sin datos secretos.

## Post-ejecución

Aplicar cierre incremental del contrato, incluida nota de fase en CHANGELOG/GUIA_TECNICA y registro propio; variables se sustituyen por medidas reales:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-A --desc "REFACTOR-WHATSAPP-ENTREGA: contratos y prerrequisitos" --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Completitud y restricciones

- [x] Decisiones de matriz, diferidos, legado y evidencia cerradas por escrito. (`decisiones.md` §2: 8 ratificaciones + 3 precisiones; F-B/F-E diferidas conservadas)
- [x] Baseline real preservado y F-P4.1 clasificado correctamente. (60 archivos leídos, **0 escrituras**, hashes en `baseline_inventory.json`; `asset_zip_paths` verificado en el writer)
- [x] Identidad, fecha, frescura, revocación y permiso documental con estado explícito. (`decisiones.md` §4; la **reconfirmación de vigencia queda abierta con dueño: operador**, necesaria para H/E2E y no para B)
- [ ] Cierre incremental y validaciones completos o checkpoint INCOMPLETA. **CHECKPOINT**: validaciones, índice y registro ejecutados; **falta la autorización de commit**, por lo que el corte de R2 no se declara consumado.
- Presupuesto 60 tool_use de referencia; instrumento `measure_iterations.py`. **A es documental: se declara corte documental, no commit de código simulado. El instrumento quedó FUERA DE SERVICIO (R2.1): el transcript no está disponible; se conserva el auto-reporte con su unidad sin sumarlo.**
- No implementar B–H, ejecutar v4complete, leer secretos, modificar observations ni evidence P4, subir datos o hacer push. **Cumplido: 0 corridas, 0 escrituras fuera de `evidence/…/FASE-A/` y los documentos del plan; `.env` leído solo por nombres de clave; la lectura denegada de `evidence/FASE-P5/…` no se evadió. G no iniciada.**
