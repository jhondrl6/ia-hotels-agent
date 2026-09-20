# FASE-B — Promesas realizables y pains coherentes

**Estado:** CERRADA CON DEUDA REGISTRADA (2026-09-20) — la deuda es AC5 y su dueño es **C-D**, no B. **Dependencias:** FASE-0 cerrada con AC20 verde — ya no A directamente: la cadena es A → G → 0 → B — y matriz ratificada por A. **Complejidad técnica:** ALTA: mapper, catálogo, generador, identidad comercial y ledger son consumidores distintos. **Modo:** DIRECTO, no delegate_task para decidir o implementar esta política. **R3:** 4 tareas, 0 comandos largos externos.

> **Checkpoint de la sesión del 2026-09-20 (no borrar al reanudar).** T1, T2 y T3 están
> ejecutados y medidos en `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-B/`
> (`resultados-y-observaciones.md`, `A4-decision.md`, `tests_baseline_pre/post.txt`,
> `run_mutations.py` + `mutation_report.json` 8/8 (M1–M8), `CHECKPOINT-autorizaciones-pendientes.md`).
> AC1 quedó cerrado y verificado por el guard de cableado (21 conformes, 0 omisiones,
> excepciones retiradas). AC2 y AC19a-consumo están implementados. **A1 fue autorizado
> y ejecutado dentro de la misma sesión**: `proposal_asset_alignment.py` separa ahora la
> tabla de resolución del universo contado del gate, sin mover el denominador, y con eso
> cerraron los 7 rojos de matriz (POST-C 83 passed; canónicas 4.285 → 4.299). **A4 quedó
> decidido con la opción O5** (`A4-decision.md`): el fixture de
> `test_get_blocking_issues` se re-ancló a `whatsapp_conflict` —el dolor de WhatsApp que
> sigue prometiendo un servicio contado— y se reforzó con
> `assert "proposal_asset_alignment" in blocking_names`; el punto ciego del gate
> (`counts_in_alignment=False` → "PASS trivial") queda assertionado en
> `test_deuda_ac5_ledger_solo_condicional_pasa_trivial`, que debe ponerse rojo cuando AC5
> lo gobierne. El gate no se tocó. Superficie **AC5, dueño C-D** (maestro §4 y filas C y D
> de la matriz; el "D/E" escrito antes en este archivo era un error de registro). **A2
> ejecutado con autorización del operador: commit `473ed0f`** (42 archivos, +1.907/−266,
> 7/7 checks del pre-commit sin saltar ninguno); **A3 (push) sigue pendiente de
> autorización**. Contador v4complete 0/1.


## Contexto

Leer maestro, contrato de ejecución, decisiones de A, 00 y workflow. Ejecutar solo B. La propuesta original de cambiar una línea de `promised_by` es insuficiente: `PAIN_SOLUTION_MAP` y `PAIN_TO_ASSET` deciden aparte. No conservar un botón solo porque existe un número en conflicto.

### Lecciones capitalizadas aplicables

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-NC6 | El cable perdido se busca en el caller, no creando otra fuente. | AC1 pasa la señal real al detect_pains del orquestador. |
| L-NC10 | La narrativa estática puede contradecir un ledger correcto. | AC2 cruza propuesta, servicio, guía y ledger. |
| L-T4A.5 | Un test verde puede no alcanzar la rama que dice certificar. | AC1 usa el productor de ValidationSummary, incluido centinela, sin combinación imposible. |
| L-PF10 | Una lista vacía válida no equivale a falta de fuente. | Eliminar un pain falso no activa un fallback de catálogo por lista vacía. |
| L-PF6 | Ausencia observada y lector fallido no son equivalentes. | B consume el estado AC19a: el caso medido en vivo es una huella de plugin leída como `exists`, no un lector ciego. Sin alcance verificado no hay dolor de ausencia confirmada —hay `no_verificado_en_sitio` con solicitud de confirmación— y una huella de presencia tampoco se convierte en número utilizable. |

## Tareas

1. **PRE y contrato único.** Capturar baseline. Localizar `PainSolutionMapper.detect_pains/map_to_solutions/get_assets_for_pain`, `PAIN_SOLUTION_MAP`, catálogo, `ConditionalGenerator.PAIN_TO_ASSET`, `V4AssetOrchestrator.generate_assets/_solutions_to_asset_specs`, identidades de servicios y generadores de propuesta/matriz. Inventariar además los productores de promesas que el plan no listaba y que también deciden: `preflight_checks.NEW_HOTEL_THRESHOLDS["whatsapp_button"] = 0.3` (umbral rebajado que autoría botón con confianza 0.3), `ELEMENTO_KB_TO_PAIN_ID["nap_consistente"] → ("whatsapp_conflict", "whatsapp_button", None)` en `v4_diagnostic_generator.py` (un gap de NAP produce assets de WhatsApp), las dos ramas WhatsApp de `V4ProposalGenerator._generate_dynamic_services_table` (override por `whatsapp_conflict` y filtro `whatsapp_sin_brecha`, más el `service_name` derivado de `PROPOSAL_SERVICE_TO_ASSET`) y `ASSET_CATALOG["whatsapp_button"]` (`required_field="whatsapp"`, `required_confidence=0.7`, `block_on_failure=False`). Constatado en el código: `ConditionalGenerator.PAIN_TO_ASSET` **no** tiene hoy la clave `no_whatsapp_visible`, así que pain y asset deciden aparte; y el comentario `FIX-D7` de `run_v4_complete_mode` conserva un texto vencido que todavía presenta `whatsapp_button` como asset `promised_by=always` cuando `ASSET_CATALOG["whatsapp_button"].promised_by` declara ese `"always"` ELIMINADO — B correlige el comentario y no lo hereda como hecho. Inventariar consumidores y estados; no agregar otro mapa paralelo.
2. **Implementar la promesa condicionada.** Derivar una vez la señal HTML desde audit_result.validation en generate_assets y pasarla a detect_pains. Alinear mappers/catálogo/specs para que ausencia o confianza insuficiente no prometan botón operativo; retirar el can_generate incondicional que impone botón para conflicto. Agregar `whatsapp_setup_guide` como asset de solicitud/validación sin número ni enlace provisional, registrado y realmente generado. Reutilizar `whatsapp_conflict_guide` únicamente para conflicto; eliminar su selección automática del número por reseñas y exigir validación humana. Conservar `INVALID_MAPPINGS` que impide presentar una guía de conflicto como resolución de ausencia. Propagar identidad y capacidad del nuevo servicio a propuesta, matriz, ledger y generación; el texto debe distinguir preparación pendiente de instalación realizada. La confianza/número utilizable se deriva de ValidationSummary, no del teléfono web. **AC19a (consumo):** el caso medido en vivo no es un lector ciego — la home devuelve `exists` por huella de plugin—, así que B gobierna los dos sentidos del error. Cuando el reporte declare señal negativa sin alcance verificado, el ledger registra `no_verificado_en_sitio` y la narrativa pide confirmación: prohibido redactar "el hotel no tiene WhatsApp" ni crear un pain de ausencia. Cuando declare presencia por huella de plugin sin número, esa huella tampoco se convierte en número utilizable ni en botón operativo. B define ese estado y su tratamiento; C amplía después, de forma aditiva, lo que el lector puede observar.
3. **POST y mutaciones.** AC1: igualdad de conjuntos main/diagnostic/orquestador y ledger serializado con datos producibles. Mutar señal produce pain incorrecto; tras F-F no exigir bloqueo como consecuencia obligatoria. AC2: ausencia→setup presente en generación; conflicto→guía, nunca botón listo; HTML-only→sin ausencia falsa; vacío real→sin fallback espurio. AC19: una señal negativa sin alcance verificado no genera dolor de ausencia confirmada ni asset de botón, y el ledger conserva la acción pendiente justificada. Mutar individualmente catálogo/mapper/generación y probar que las discordancias son detectadas. Cruzar `coverage_no_silent_drop`, identidad servicio↔asset y narrativa sin dar por resuelto el canal físico.
4. **Cierre incremental.** Guardar pares y reports reales, actualizar AC1/AC2, 00/09/10 y todos los estados. Explicar el delta de assets esperado sin fijar un total histórico de 13. No afirmar que D1 de transporte WhatsApp queda resuelto.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`

## Tests obligatorios

Reusar tests de pain mapper, catálogo, promised-assets-production, semántica, matriz de servicios, generación condicional y regresiones WhatsApp/Visperas. Agregar casos de setup/ausencia/conflicto y tests que lean la salida JSON/MD de writers reales. No modificar tests para permitir un número inventado o silenciar conflicto.

Archivos previstos: `modules/commercial_documents/pain_solution_mapper.py`, `modules/asset_generation/asset_catalog.py`, `v4_asset_orchestrator.py`, `conditional_generator.py`, `whatsapp_conflict_guide.py`, generadores narrativos y registros de identidad efectivamente consumidores; se suman a la allowlist los productores de promesas incluidos en el inventario de la Tarea 1 — `modules/asset_generation/preflight_checks.py`, `modules/commercial_documents/v4_diagnostic_generator.py`, `modules/commercial_documents/v4_proposal_generator.py` — y `main.py` solo para corregir el comentario vencido de `promised_by=always` en el bloque `FIX-D7` de `run_v4_complete_mode`; un generador específico de setup solo si no existe equivalente seguro. No reutilizar `wa_button_gen` legacy, que produce placeholder.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`

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
