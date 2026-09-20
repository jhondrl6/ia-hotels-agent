# FASE-VERIFY — Certificación transversal sobre evidencia existente

**Estado:** PENDIENTE. **Dependencia inmediata:** FASE-E2E cerrada con evidencia preservada (o checkpoint explícito de corrida no consumida).
**Complejidad técnica:** ALTA: juicio transversal sobre 18 ACs, límites causales y una sola muestra.
**Scope R3:** 4 tareas, 0 comandos largos externos. **Ejecución DIRECTA obligatoria: VERIFY no se delega.** Sin código nuevo, sin tests, sin v4complete, sin remediación.

## Contexto e inicio

Ejecución futura con mandato propio. Lee `01-plan-maestro.md` §4 y §5; `04-contrato-ejecucion.md` §"Corrida única y límites de certificación"; `00-lecciones-capitalizadas.md`; checklist; dependencias; los análisis de B–H y E2E; y el workflow canónico (FASE-VERIFY).
VERIFY **lee y dictamina**, no repara: ningún cambio de código, de umbrales, de datos ni de evidencia. Un hallazgo se registra con dueño y disparador, no se cierra aquí. Documentar un resultado fallido es un resultado válido de esta fase; no lo convierte en certificación favorable ni habilita reparación dentro de RELEASE.
Entrada: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-*/`, `output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/` y los artefactos preservados por el runner.

### Lecciones capitalizadas aplicables

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-V.4 | VERIFY registra fallos con dueño; no los remedia. | Cada FALLA sale con causa, dueño y disparador de sesión de recuperación autorizada; no se abre un fix en esta sesión. |
| L-VUP-17 | Los tests locales no certifican integración renderizada. | Se separa régimen offline (B–H) de lo realmente ejercitado en la única corrida; nada pasa a SUPERADO EN E2E por tests verdes. |
| L-T4A.5 | Un test verde puede no alcanzar la rama que dice certificar. | Se verifica que cada AC cite artefacto real (writer/ZIP/acta/JSON), no presencia de un string en código ni tamaño de archivo. |
| L-R.4 | Una regla sin verificador declara expresamente su límite. | `certificacion.json` publica cobertura y límites: qué no se puede afirmar con un hotel y una corrida. |
| L-PF6 | Ausencia observada y lector fallido no son equivalentes. | Ausencias, retenciones deliberadas y errores de lectura se dictaminan por separado; un fallo de red no prueba ausencia de canal. |

## Tareas

1. **Integridad e inventario de evidencia.** Comprobar hashes de código/runner/input y `run_control.json` (`attempts=1`, PID, argv, timestamps, exit code) contra lo preservado; inventariar artefactos por fase con `read_status` (READ_OK incluido vacío, ABSENT, READ_ERROR) y disposición (publicado / retenido / suprimido). Registrar faltantes y errores de lectura como tales, sin rellenar con supuestos. Verificar que el ZIP público no contiene snapshot interno ni documentos retenidos.
2. **Dictamen por AC y certificación.** Recorrer AC1–AC20 contra artefactos reales y clasificar cada uno: **SUPERADO** (offline y/o E2E, indicando el régimen), **FALLA** o **NO EJERCITADO**. Emitir `certificacion.json` con matriz, evidencia citada por símbolo/ruta, límites y diff estructural del cambio (superficies tocadas por fase frente a lo planificado). READY_FOR_PUBLICATION exige gates y acta favorables y ZIP válido: `exit_code == 0` no lo acredita. Si la meta de entrega no se demuestra, declararla parcial/FALLA para esa meta. **Tres obligaciones de la revisión 2:** (i) certificar `AC20` y verificar si `readiness` volvió a convivir con un veredicto bloqueante, porque ese par ya se observó; (ii) anotar que AC1/AC2/AC3/AC6 no los ejercita la ruta viva de este hotel (medido el 2026-09-19: sin pain, sin botón en el plan, check en verde vacuo), así que su régimen propio es OFFLINE y declararlo NO EJERCITADO en E2E no es un fracaso sino un límite; (iii) comparar contra el baseline `output/TAREA7-2026-09-19/`, no contra la expectativa del plan.
3. **Triaje, deudas y límites.** Reabrir y enlazar **F-P4.3** por su mismo ID (no duplicar ni reescribir su informe original); registrar hallazgos nuevos con dueño y disparador; recalificar F-P4.1 según lo medido en E; confirmar estado de F-P4.2 y F-P4.5; mantener F-B y F-E como deudas diferidas con su condición escrita. Declarar el alcance de la muestra: un hotel y una corrida no certifican todos los hoteles ni todas las ramas. No convertir un resultado de la corrida en implementación automática.
4. **Lecciones y cierre.** Extraer lecciones reales con el template vigente (sin fabricar), actualizar `00-lecciones-capitalizadas.md` (aplicación efectiva por fila), `09-documentacion-post-proyecto.md`, `10-analisis-post-implementacion.md` (matriz final, comparación histórico/post, seguimientos), checklist, dependencias e índice del plan. Ejecutar el cierre documental del contrato y las validaciones autorizadas. Corte R2 **documental** declarado por separado.

## Reglas

- Prohibido ejecutar `main.py v4complete`, relanzar el runner, correr pytest, mutar símbolos o editar código/configuración/datos/evidencia.
- Lectura con máscara o por número de línea si un artefacto pudiera contener un secreto; nunca imprimirlo ni propagarlo a un artefacto nuevo.
- No modificar `evidence/FASE-P4/` ni históricos archivados; no usar el resultado de VERIFY para relajar gates, umbrales o enforcement.
- La certificación es del estado observado: si un AC quedó sin evidencia, se dictamina NO EJERCITADO con dueño, no se asume superado.

## Post-ejecución

Actualizar documentos de cierre con datos medidos y al menos tres observaciones; subsección VERIFY en CHANGELOG bajo versión vigente y nota en `docs/GUIA_TECNICA.md`. Sustituir variables por datos reales; registro propio sin `--release`:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-VERIFY --desc "REFACTOR-WHATSAPP-ENTREGA: certificación AC1-AC18, triaje y límites de muestra" --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/build_lesson_index.py --check
./venv/Scripts/python.exe scripts/validate_lesson_capitalization.py
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/validate_document_integration.py
```

Confirmar REGISTRY sin GAP. No commit, push, tag ni write-back sin autorización expresa; VERSION y release pertenecen a RELEASE.

## Presupuesto y checklist

Referencia **60 tool_use**; fase sin código, corte **documental** declarado aparte. Instrumento `evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>`; sin transcript o con acceso denegado, **FUERA DE SERVICIO (R2.1)** con auto-reporte por unidad separado.

- [ ] E2E cerrada (o checkpoint de corrida no consumida) y evidencia íntegra verificada por hash.
- [ ] Matriz AC1–AC20 dictaminada con régimen offline/E2E explícito y artefacto citado por AC.
- [ ] `certificacion.json` con límites de muestra; READY no deducido de exit code.
- [ ] F-P4.3 reabierto y enlazado, sin duplicación; deudas F-B/F-E vigentes con condición escrita.
- [ ] Lecciones reales extraídas; 00/09/10, checklist, dependencias e índice actualizados.
- [ ] Ninguna remediación, ejecución ni delegación; RELEASE queda para otra sesión.
