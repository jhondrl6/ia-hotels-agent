# FASE-B — Promesas realizables y pains coherentes

**Estado:** PENDIENTE. **Dependencias:** A completa y matriz ratificada. **Complejidad técnica:** ALTA: mapper, catálogo, generador, identidad comercial y ledger son consumidores distintos. **Modo:** DIRECTO, no delegate_task para decidir o implementar esta política. **R3:** 4 tareas, 0 comandos largos externos.

## Contexto

Leer maestro, contrato de ejecución, decisiones de A, 00 y workflow. Ejecutar solo B. La propuesta original de cambiar una línea de `promised_by` es insuficiente: `PAIN_SOLUTION_MAP` y `PAIN_TO_ASSET` deciden aparte. No conservar un botón solo porque existe un número en conflicto.

### Lecciones capitalizadas aplicables

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-NC6 | El cable perdido se busca en el caller, no creando otra fuente. | AC1 pasa la señal real al detect_pains del orquestador. |
| L-NC10 | La narrativa estática puede contradecir un ledger correcto. | AC2 cruza propuesta, servicio, guía y ledger. |
| L-T4A.5 | Un test verde puede no alcanzar la rama que dice certificar. | AC1 usa el productor de ValidationSummary, incluido centinela, sin combinación imposible. |
| L-PF10 | Una lista vacía válida no equivale a falta de fuente. | Eliminar un pain falso no activa un fallback de catálogo por lista vacía. |
| L-PF6 | Ausencia observada y lector fallido no son equivalentes. | B consume el estado AC19: sin alcance verificado no hay dolor de ausencia confirmada, hay `no_verificado_en_sitio` con solicitud de confirmación. |

## Tareas

1. **PRE y contrato único.** Capturar baseline. Localizar `PainSolutionMapper.detect_pains/map_to_solutions/get_assets_for_pain`, `PAIN_SOLUTION_MAP`, catálogo, `ConditionalGenerator.PAIN_TO_ASSET`, `V4AssetOrchestrator.generate_assets/_solutions_to_asset_specs`, identidades de servicios y generadores de propuesta/matriz. Inventariar consumidores y estados; no agregar otro mapa paralelo.
2. **Implementar la promesa condicionada.** Derivar una vez la señal HTML desde audit_result.validation en generate_assets y pasarla a detect_pains. Alinear mappers/catálogo/specs para que ausencia o confianza insuficiente no prometan botón operativo; retirar el can_generate incondicional que impone botón para conflicto. Agregar `whatsapp_setup_guide` como asset de solicitud/validación sin número ni enlace provisional, registrado y realmente generado. Reutilizar `whatsapp_conflict_guide` únicamente para conflicto; eliminar su selección automática del número por reseñas y exigir validación humana. Conservar `INVALID_MAPPINGS` que impide presentar una guía de conflicto como resolución de ausencia. Propagar identidad y capacidad del nuevo servicio a propuesta, matriz, ledger y generación; el texto debe distinguir preparación pendiente de instalación realizada. La confianza/número utilizable se deriva de ValidationSummary, no del teléfono web. **AC19 (consumo):** cuando el reporte de presencia declare señal negativa sin alcance verificado, el ledger registra `no_verificado_en_sitio` y la narrativa pide confirmación; prohibido redactar "el hotel no tiene WhatsApp". B define ese estado y su tratamiento; C amplía después lo que el lector puede observar.
3. **POST y mutaciones.** AC1: igualdad de conjuntos main/diagnostic/orquestador y ledger serializado con datos producibles. Mutar señal produce pain incorrecto; tras F-F no exigir bloqueo como consecuencia obligatoria. AC2: ausencia→setup presente en generación; conflicto→guía, nunca botón listo; HTML-only→sin ausencia falsa; vacío real→sin fallback espurio. AC19: una señal negativa sin alcance verificado no genera dolor de ausencia confirmada ni asset de botón, y el ledger conserva la acción pendiente justificada. Mutar individualmente catálogo/mapper/generación y probar que las discordancias son detectadas. Cruzar `coverage_no_silent_drop`, identidad servicio↔asset y narrativa sin dar por resuelto el canal físico.
4. **Cierre incremental.** Guardar pares y reports reales, actualizar AC1/AC2, 00/09/10 y todos los estados. Explicar el delta de assets esperado sin fijar un total histórico de 13. No afirmar que D1 de transporte WhatsApp queda resuelto.

## Tests obligatorios

Reusar tests de pain mapper, catálogo, promised-assets-production, semántica, matriz de servicios, generación condicional y regresiones WhatsApp/Visperas. Agregar casos de setup/ausencia/conflicto y tests que lean la salida JSON/MD de writers reales. No modificar tests para permitir un número inventado o silenciar conflicto.

Archivos previstos: `modules/commercial_documents/pain_solution_mapper.py`, `modules/asset_generation/asset_catalog.py`, `v4_asset_orchestrator.py`, `conditional_generator.py`, `whatsapp_conflict_guide.py`, generadores narrativos y registros de identidad efectivamente consumidores; un generador específico de setup solo si no existe equivalente seguro. No reutilizar `wa_button_gen` legacy, que produce placeholder.

## Post-ejecución

Ejecutar cierre del contrato y registrar esta fase, no fases futuras:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-B --desc "REFACTOR-WHATSAPP-ENTREGA: promesas realizables y setup" --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --archivos-nuevos "$ARCHIVOS_NUEVOS_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Completitud y restricciones

- [ ] AC1/AC2 y pruebas de contrato/regresión verdes con mutantes rojos pertinentes.
- [ ] Setup existe como entregable, no solo como catálogo/promesa.
- [ ] Pains y conflictos siguen divulgados; cobertura no equivale a instalación confirmada.
- [ ] PRE/POST y cierre incremental completos.
- Presupuesto referencia 60 tool_use, instrumento `measure_iterations.py`, corte commit de código; retirar métrica si no medible.
- No modificar umbrales, privacidad, warehouse, Juez ni ejecutar v4complete. El endurecimiento de href/gate corresponde a C en otra sesión.
