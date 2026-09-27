# Checklist — EVALUACION-JEV-TYPESAFE-2026-09-21

Estado de preparación: AJUSTADA el 2026-09-21. Ninguna casilla de implementación se completa con la redacción de este archivo. Rutas de evidencia bajo `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/`; son destinos previstos, no artefactos existentes.

## Matriz de aceptación

| AC | Fase | Evidencia que debe leerse | Estado |
|---|---|---|---|
| AC1 | B | `FASE-B/import_scanner.txt`, `integracion.json`: población, imports y archivos realmente cambiados | PENDIENTE |
| AC2 | B | `FASE-B/contract.txt`, `modelos.json`: fallos explícitos, DeepSeek sin fallback, Noul sin confianza inventada | PENDIENTE |
| AC3 | A/B | `muestra.json`, `etiquetas.json`, `protocolo.json`: sha, revisión humana, splits y commit anterior a inferencias | **PARCIAL (FASE-A 2026-09-21)**: artefactos creados; muestra **BORRADOR** (4 pares, 2 dev/2 eval, 1 excluido), sha+splits verificados por checker; revisión humana `sin_revisar`, umbrales nulos y commit pendientes |
| AC4 | C | `FASE-C/respuestas.jsonl`, `informe_comparativa.json`: tres brazos, metadatos, denominadores y costes | PENDIENTE |
| AC5 | C | `FASE-C/decision.json`, `decision.md`: regla pre-registrada y ejecución válida, o impedimento explícito | PENDIENTE |
| AC6 | B/C | `FASE-B/mutation.json`, `FASE-C/aditividad.json`: guard real, causa del rojo y removed vacío | PENDIENTE |
| AC7 | C/RELEASE | `FASE-C/decision.json`: Jev y D6 independientes; transferencia autorizada o pendiente explícita | PENDIENTE |
| AC8 | B/C | `FASE-B/budget_tests.txt`, `FASE-C/preflight.json`, `consumo.json`: ninguna llamada sin reserva y permiso; cliente con `RetryPolicy(max_retries=0)` verificado contando intentos | PENDIENTE |
| AC9 | B | `FASE-B/entorno.json`, `requirements-pilot.txt`, `sdk_contract.txt`, `mutation.json`: SDK real sin red; errores asertados por clase y 200 sin `usage` tratado como fallo de validación, no como consumo cero | PENDIENTE |
| AC10 | A/B | `FASE-A/selftest.txt`, `FASE-B/metrics_tests.txt`: instrumentos contra valores conocidos | **FASE-A HECHA 2026-09-21**: `selftest.txt` con 7 tests en verde (score conocido; denominador cero → `None`, no 100 %); `metrics_tests.txt` corresponde a B |
| AC11 | Preparación / cada fase | Paso 0, documentación cruzada y validadores; ver registro de preparación en `10-analisis-post-implementacion.md` | PREPARACIÓN VALIDADA el 2026-09-21; se revalida en cada fase, no certifica el piloto |
| AC12 | B/C | `FASE-C/preflight.json`: habilitación declarada distinta de autenticación/cuota; Anthropic excluido | PENDIENTE |

## Entrada por fase

- [ ] A: instrucción de ejecución; corpus y revisión humana accesibles. No requiere B/C del hermano para preparar.
- [ ] B: A con muestra/protocolo y estado real; B externa y C externa verificadas offline; AC15 semántico parcial admitido.
- [ ] B: entorno aislado e instalación expresamente autorizados; no modificar `llm_provider.py` ni defaults globales.
- [ ] C: SDK y runner offline verificados; muestra y protocolo versionados; valores y permisos completos.
- [ ] C: conectividad/ajuste separados de evaluación; congelación final antes de ver evaluación.
- [ ] RELEASE: evidencias re-leídas, decisión evaluable o cierre administrativo explícito sin falsear ACs.

## Salida por fase

- [ ] Tests y par verde/rojo por guard, con causa y símbolo nombrados.
- [ ] No se confunde error, ausencia, abstención ni resultado negativo.
- [ ] Cada petición declara proveedor/modelo efectivos; no fallback a Anthropic.
- [ ] Tokens observados, coste calculado y cargo facturado separados.
- [ ] Matriz de AC y estados reales actualizados; no se marcan parciales como verdes.
- [ ] Iteraciones: valor, unidad y corte, o no medible con motivo; nunca estimación presentada como medición.
- [ ] Post-fase y validaciones según contrato; índice generado fresco.
- [ ] Ninguna modificación de planes hermanos ni gobierno central sin autorización delimitada.
- [ ] Commit, push, write-back y archivado no se infieren de la orden de implementar.
