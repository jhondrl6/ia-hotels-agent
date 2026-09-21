# FASE-B — Proveedores e instrumentos offline

**Estado: BLOQUEADA POR DEPENDENCIA.** Requiere A propia y entrega verificada de B/C offline del hermano. AC15 semántico parcial por NO-EJERCITADO es admisible; no exigir la calidad que el piloto todavía debe medir.

## Lecturas y entrada

Leer maestro, contrato, dependencias, checklist, Paso 0 y evidencia de A. Leer la interfaz y los tests **reales** de `decision_client.py` y `triage_lesson_relevance.py` entregados por el hermano, no solo sus prompts. Verificar que no haya otra sesión escribiendo esas superficies.

No modificar `modules/providers/llm_provider.py`: el comparador es DeepSeek explícito mediante la costura, conservando usage/modelo antes de descartarlos. Anthropic no tiene API habilitada y no se usa como fallback.

| Lección del Paso 0 | Aplicación en B |
|---|---|
| DA-C3 | AC2: ausencia, error y respuesta negativa no se colapsan |
| L-T4A.5 | AC9: SDK real con transporte falso y prueba de que se alcanzó la rama |
| L-V2.1 | AC6/AC8/AC9: mutación del símbolo real y aserción por causa |
| L-ENT.9 | AC4/AC12: proveedor efectivo registrado, sin selección automática |
| L-D5 | AC10: probar instrumentos de consumo y métricas con valores conocidos |

## Tareas

1. Verificar docs actuales de Jev/DeepSeek: paquetes, modelos, payload, usage, errores, tarifas y límites. No hacer una inferencia para «ver si responde». Fijar modelos solicitados y reglas de validación del modelo devuelto; el efectivo real queda NO-EJERCITADO hasta C. Identificar como simulados los valores efectivos de los tests y declarar cualquier alias DeepSeek que impida reproducibilidad estricta.
2. Con autorización de instalación, resolver el SDK en un entorno aislado cuya ubicación y exclusión de git se hayan comprobado. La sonda del 2026-09-21 usó `tmp_test/venv-jev-sdk` (ignorado, 28 MB) y **no** instaló en el `venv` principal: el SDK resuelve `pydantic 2.13.5` contra el pin `pydantic==2.12.5` del proyecto. B elige una ruta duradera, no reutiliza ese entorno de sonda sin verificarlo, no modifica `requirements.txt` y escribe `FASE-B/requirements-pilot.txt` con `entorno.json` de versiones efectivamente resueltas, no solo los mínimos de PyPI.
3. Integrar Jev y DeepSeek en `scripts/decision_client.py`, respetando frontera e interfaz pública. Conservar telemetría sin cambiar lo que consume C. Si hace falta otro archivo de producción para añadir el proveedor o cambiar el consumidor, registrar la incompatibilidad y pedir decisión, no relajar AC1 silenciosamente.
4. Probar Noul sin confidence inventada y la etiqueta/abstención DeepSeek sin presentar score autorreportado como probabilidad calibrada. Resolver compatibilidad con la interfaz real antes de permitir ejecución externa.
5. Completar runner en `scripts/evaluate_jev_pilot.py`: ejecución explícita por proveedor, ledger de intentos, reserva de presupuesto, comparación y generación de decisión. `check`/`report` continúan sin red. Autorización ausente, hashes modificados o presupuesto incompleto impiden construir/enviar peticiones reales.
6. Construir el cliente Jev con `RetryPolicy(max_retries=0)`: los defaults medidos del SDK 0.7.0 son `max_retries=2` (3 intentos ante un 429, cada uno potencialmente facturable). Timeout, 429 y 5xx no producen un intento extra fuera del ledger. Separar tokens observados, coste calculado y cargo facturado, incluido uso desconocido y caché DeepSeek cuando exista.
7. Probar aditividad importando el guard real del consumidor. No modificar la lógica del triaje ajeno para que el piloto parezca compatible. Medir imports con la población completa del piloto y la misma regla de aislamiento de B del hermano.

## Tests y evidencia

Tests previstos bajo `tests/quality_gates/jev_pilot/`; no se declaran existentes antes de esta fase.

| Prueba | Resultado exigido |
|---|---|
| `test_missing_deepseek_does_not_fallback_to_anthropic` | AC2/AC12: falla antes de enviar, aunque una clave sintética Anthropic exista en el test |
| `test_raw_usage_and_effective_model_survive_adapter` | AC4: metadatos preservados junto con la decisión |
| `test_noul_probability_is_not_confidence` | AC2: p_yes bajo no se clasifica como incierto automáticamente |
| `test_sdk_transport_is_exercised_offline` | AC9: el SDK real serializa/parsea, transporte falso invocado, red bloqueada |
| `test_partial_answers_and_invalid_schema_fail` | AC9: IDs ausentes o duplicados no son respuesta negativa; un 200 **sin `usage`** debe lanzar `TypeSafeAPIResponseValidationError` (medido), nunca dar `usage = null` ni coste cero |
| `test_http_failure_cases_remain_distinct` | AC9: 401 → `TypeSafeAuthenticationError`, 429 → `TypeSafeRateLimitError`, timeout → `TypeSafeAPIConnectionError`; aserción por clase y `status`, no por `Exception` genérica |
| `test_budget_reserves_before_each_attempt` | AC8: presupuesto ausente/excedido implica cero envíos |
| `test_sdk_retries_disabled_and_attempts_counted` | AC8: con los defaults el mismo 429 da 3 intentos (medido); con `max_retries=0` da 1 y el ledger coincide |
| `test_timeout_keeps_unknown_cost_reserved` | AC8/AC10: uso desconocido no libera reserva como cero |
| `test_report_replays_without_network` | AC4/AC10: reproducción desde logs, sin clientes |
| `test_real_triage_guard_preserves_anchored_rows` | AC6: removed vacío con respuestas no vacías; mutarlo vuelve rojo el test por la causa prevista |

Guardar `import_scanner.txt`, `integracion.json`, `contract.txt`, `modelos.json`, `sdk_contract.txt`, `budget_tests.txt`, `metrics_tests.txt` y `mutation.json` en `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-B/`. El par de mutación se ejecuta aislado o con monkeypatch, nunca sobre trabajo compartido sin restauración verificada.

```bash
venv/Scripts/python.exe -m pytest tests/quality_gates/jev_pilot -v
```

Si los tests SDK necesitan el entorno aislado, usar su ejecutable real y registrar el comando exacto; no asumir que la instalación existe en `venv`. Re-ejecutar también los tests entregados de costura y triaje del hermano, sin reescribir sus expectativas.

## Post-ejecución y completitud

Aplicar contrato post-fase y actualizar README, dependencias, checklist, 09, 10 y 00. Ejecutar validaciones y conservar delta de archivos, tests e iteraciones con unidad/corte.

- [ ] SDK y adaptadores probados sin red; cero inferencias reales.
- [ ] DeepSeek explícito, sin fallback; `llm_provider.py` intacto.
- [ ] AC1/AC2/AC6/AC8/AC9/AC10 con pruebas causales y artefactos.
- [ ] AC4/AC5 semánticos siguen sin medir; autenticación/saldo también.
- [ ] Muestra/protocolo, modelos solicitados y reglas de validación preparados para congelación; modelo efectivo real pendiente de C.

La existencia de la API y el verde offline no autorizan comenzar C. Si el SDK o la interfaz son incompatibles, detenerse y registrar el cambio requerido; no bajar la aserción.
