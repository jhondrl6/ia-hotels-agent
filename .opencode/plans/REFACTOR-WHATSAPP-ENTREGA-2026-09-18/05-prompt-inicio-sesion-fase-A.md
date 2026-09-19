# FASE-A — Contratos, baseline y prerrequisitos

**Estado:** PENDIENTE. **Dependencias:** preparación leída y mandato de ejecutar A. **Complejidad técnica:** ALTA por decisiones cross-module, datos reales y seguridad. **Modo:** principal DIRECTO; delegate_task solo para recuperaciones independientes read-only, nunca para decidir arquitectura. **R3:** 4 tareas, 0 comandos largos externos.

## Contexto

Lee `01-plan-maestro.md`, `04-contrato-ejecucion.md`, `00-lecciones-capitalizadas.md`, 09/10 y el workflow `.agents/workflows/phased_project_executor.md`. Esta sesión ejecuta solo A: contratos y baseline, no los fixes ni la corrida.

### Lecciones capitalizadas aplicables

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-NC6 | El cable perdido se busca en el caller, no creando otra fuente. | Congelar productores de AC1/AC7, incluido detect_pains y no solo validate. |
| L-V.1 | Contenido y layout reales son dos ejes distintos del contrato. | AC10 parte del writer ya corregido P6-R; no del stub histórico. |
| L-VUP-9 | Los comandos delegados deben usar flags comprobados. | Ratificar parser/loader para AC14/AC17 sin ejecutar el comando largo. |
| L-R.4 | Una regla sin verificador declara expresamente su límite. | Registrar límites del futuro AST, contador y baseline. |

## Tareas

1. **Baseline y mapa de fuentes.** Registrar HEAD, status, quick PRE y pares de tests pertinentes antes de crear nuevos tests. Leer síntomas en artefactos P4 permitidos sin abrir logs crudos; inventariar hash/ruta, no modificar esa evidencia. Contrastar writer P6-R y sanitización vigente. Producir `baseline_inventory.json` y `decisiones.md` bajo evidencia de A.
2. **Ratificar contrato de fixes.** Validar la matriz del maestro: ausencia→setup; conflicto→guía sin número elegido; presencia no es confianza; botón solo con dato utilizable. Registrar aprobación/rectificación de F-F ampliada + F-A' + V-1, F-D', conservación del módulo legacy y F-B/F-E diferidas con dueño/AC. No codificar F-B sin decisión de privacidad escrita. Confirmar campos propuestos de reportes y la frontera snapshot privado/ZIP exportable. Si el operador cambia la decisión, actualizar prompts afectados antes de B; no reinterpretar restricciones.
3. **Resolver prerrequisitos operativos.** Seleccionar exactamente la observación Hotel Don Alfonso, conservar valores y 2026-07-22; registrar el vínculo de URL indicado por el usuario, no una redirección supuesta. Evaluar necesidad de reconfirmación de vigencia y estado de `ONBOARDING_FRESHNESS_HOURS` sin imprimir secretos. Pedir al operador evidencia de revocación de la key expuesta, no su valor. Re-medir el quick al inicio: el 9/10 del 2026-09-18 era cuatro documentos sucios en el árbol y hoy da 10/10 con esos archivos idénticos a HEAD, así que no se pide autorización central por ese concepto. Si el rojo reaparece, leer `_check_version_sync` completa antes de atribuirle una causa y solo entonces escalar al operador. Resolver también la divergencia de instrucciones sobre regeneración DOMAIN_PRIMER (cada fase frente a solo RELEASE) sin editar workflow ni AGENTS por cuenta propia.
4. **Cierre.** Registrar decisiones cerradas y las que siguen bloqueadas; actualizar checklist/dependencias/00/09/10 y docs incrementales conforme al contrato. A no está completa si queda abierta una decisión necesaria para B o para el cierre verde. No esperar al intento E2E para descubrir identidad o privacidad.

## Tests y evidencia obligatorios

Verificar sin red las superficies actuales de `tests/regression/test_whatsapp_conflicts.py`, `tests/commercial_documents/test_promised_assets_production.py`, `tests/asset_generation/test_site_presence_adapter.py`, `tests/test_p6r_full_flow_matrix.py` y `tests/auditors/test_p5_ac_s1_secret_sanitization.py`. Ajustar la selección si el inventario real lo requiere y registrar la selección exacta. No declarar que pruebas no ejecutadas pasaron. Un test con imports/red involuntaria se aísla o se reporta, no consume v4complete.

Evidencia: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-A/`. AC14 queda preparado, no certificado E2E. Guardar respuestas de producto sin datos secretos.

## Post-ejecución

Aplicar cierre incremental del contrato, incluida nota de fase en CHANGELOG/GUIA_TECNICA y registro propio; variables se sustituyen por medidas reales:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-A --desc "REFACTOR-WHATSAPP-ENTREGA: contratos y prerrequisitos" --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Completitud y restricciones

- [ ] Decisiones de matriz, diferidos, legado y evidencia cerradas por escrito.
- [ ] Baseline real preservado y F-P4.1 clasificado correctamente.
- [ ] Identidad, fecha, frescura, revocación y permiso documental con estado explícito.
- [ ] Cierre incremental y validaciones completos o checkpoint INCOMPLETA.
- Presupuesto 60 tool_use de referencia; instrumento `measure_iterations.py`. A es documental: declarar corte documental, no simular commit de código. Si acceso no disponible, métrica FUERA DE SERVICIO.
- No implementar B–H, ejecutar v4complete, leer secretos, modificar observations ni evidence P4, subir datos o hacer push. Nueva sesión para B.
