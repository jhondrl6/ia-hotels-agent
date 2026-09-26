# FASE-D — Veredicto canónico y causa legible del bloqueo

**Estado:** PENDIENTE. **Dependencias:** A, B y C completas. **Complejidad técnica:** ALTA: el mismo resultado cruza pre-gate, assessment, publication gates y archivos serializados. **Ejecución:** DIRECTA, sin delegate_task para diseño cross-module. **Scope R3:** 4 tareas, 0 comandos largos externos.

## Contexto e inicio

Lee `01-plan-maestro.md`, `04-contrato-ejecucion.md`, `00-lecciones-capitalizadas.md`, checklist y el workflow canónico. Ejecuta únicamente D en esta sesión. Revalida los símbolos antes de editar. La comparación de score por sí sola no consume `is_coherent=False`.

### Lecciones capitalizadas aplicables

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-NC6 | El cable perdido se busca en el caller, no creando otra fuente. | AC4 transporta checks desde el reporte real, sin reconstruirlos por nombre fijo. |
| L-PF10 | Una lista vacía válida no equivale a falta de fuente. | AC9 conserva la distinción entre lista de fallos vacía y reporte ausente. |
| L-T4A.5 | Un test verde puede no alcanzar la rama que dice certificar. | AC8 exige score alto con error real y spy sobre entrada a generación. |

## Tareas

1. **PRE y contrato.** Captura baseline focalizado; localiza `run_v4_complete_mode`, `coherence_verdict_passes`, `AssessmentBuilder.with_coherence`, `_check_coherence` de PublicationGateEngine y writers de gate reports. Identifica las rutas pre/post/fallback y la persistencia del resultado del pre-gate.
2. **Unificación.** Sustituye la decisión por score del pre-gate por `coherence_verdict_passes(score, threshold, report.is_coherent)`. Persiste el reporte y los checks culpables antes de retornar; un error debe impedir entrar a la generación de assets. Conserva el comportamiento documentado de veredicto ausente sin tratarlo como False. Transporta todos los checks fallidos de severidad error al assessment y al reporte de gates; publica `details.failed_check_names` y sus mensajes sin una whitelist WhatsApp. Los caminos post-gen y fallback deben usar el reporte correspondiente, sin un reporte previo obsoleto.
3. **POST, serialización y mutaciones.** AC4: dos checks en error aparecen ambos en JSON real. AC8: score por encima de 0.8 con veredicto False persiste causas y no invoca generación; verde complementario sí entra. Mutantes: restaurar comparación solo-score y omitir propagación de checks deben fallar por las aserciones respectivas. Probar veredicto None, True y False; score insuficiente; ausencia real de reporte y lista vacía. Preservar thresholds de AC5.
4. **Cierre incremental.** Ejecuta el contrato de cierre completo. Actualiza resultados AC4/AC8/AC9, PRE/POST y mutaciones en evidencia de D y análisis. No diagnosticar un error solo por redondeo de score.

## Tests obligatorios

Suites pertinentes bajo `tests/quality_gates/`, `tests/commercial_documents/` y tests de integración de `main.py`. Descubrir y añadir casos en archivos existentes cuando sea viable. La prueba de fail-fast recorre la ruta de producción con APIs externas sustituidas; no llama v4complete real.

Artefactos: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-D/`, JSON emitido por writer real con `details.failed_check_names`, reporte pre-gate con checks y log saneado del test.

## Post-ejecución

Actualizar 00/09/10, checklist, dependencias y estado de este prompt; CHANGELOG y GUIA_TECNICA. Sustituir variables por datos medidos antes de ejecutar:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-D --desc "REFACTOR-WHATSAPP-ENTREGA: veredicto canónico y causas serializadas" --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Completitud y restricciones

- [ ] AC4/AC8/AC9 medidos en disco; mutantes rojos por causa correcta.
- [ ] No se generaron assets tras error del pre-gate.
- [ ] AC5 intacto y PRE/POST conciliado.
- [ ] Cierre incremental completo, sin regresiones ni GAP.
- Presupuesto: referencia 60 tool_use; instrumento `measure_iterations.py`. El corte es el que la sesión tenga autorizado — «hasta el commit» solo si el commit lo está; si no, «hasta listo para revisión», declarando cuál se usó (**los cinco cortes se sostienen sin commit**). Si no puede medirse, FUERA DE SERVICIO conforme al contrato; nunca cumplimiento estimado.
- No ejecutar E2E, cambiar umbrales, relajar Juez ni corregir hallazgos ajenos. Finalizar la sesión; E será otra sesión.
