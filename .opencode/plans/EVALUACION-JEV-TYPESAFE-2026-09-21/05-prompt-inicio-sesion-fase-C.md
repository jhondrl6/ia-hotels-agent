# FASE-C — Comparación real autorizada

**Estado: BLOQUEADA POR DEPENDENCIA Y AUTORIZACIÓN.** Fase de medición, sin cambios de código. El prompt no autoriza llamadas por sí mismo.

## Lecturas y entrada

Leer maestro §Protocolo, contrato, dependencias, Paso 0, checklist y evidencia A/B. Re-medir HEAD/status, hashes de muestra/protocolo y versiones de instrumentos. Leer las autorizaciones literales del operador con su alcance, no inferirlas del estado habilitado de una cuenta.

Comparación obligatoria: búsqueda fría, DeepSeek y Jev. Anthropic está excluido. Si DeepSeek no responde, no sustituirlo ni presentar dos brazos como comparación completa.

| Lección del Paso 0 | Aplicación en C |
|---|---|
| L-ENT.9 | AC4/AC12: cada solicitud acredita quién respondió realmente |
| L-R.3 | AC4/AC10: población de recuperación y de clasificación, errores y abstenciones visibles |
| L-P6.3 | AC3/AC5: muestra exploratoria no garantiza decisión concluyente |
| DA-C3 | AC5: fallo operativo no produce rechazo semántico |
| L-T4A.5 | AC6: repetir guard con las respuestas efectivamente obtenidas |

## Tareas

1. Ejecutar el checker local usando la CLI entregada. Verificar muestra y protocolo versionados, etiquetas humanas separadas de payloads, saneamiento, valores finitos de presupuesto y criterios acordados. La ausencia de una sola condición detiene la etapa sin inferencias.
2. Con autorización literal específica, ejecutar conectividad sobre inputs de desarrollo previamente congelados. Registrar autenticación por proveedor, cuota/saldo cuando sean comprobables y límites no comprobados; no abrir la consola ni leer datos financieros privados sin permiso. Una prueba de conectividad también cuenta como inferencia y consume presupuesto.
3. Si se autorizó ajuste, usar solo desarrollo, bajo su ledger y criterios pre-registrados. Congelar y versionar configuración final; obtener autorización de evaluación ligada a sus hashes. No usar pares de evaluación para depuración o ajuste.
4. Ejecutar los tres brazos sobre los pares previstos. El runner debe preservar modelo/proveedor efectivos, usage y errores por intento. Validar que el conjunto de IDs observado coincide con el esperado, incluidos fallos; no descartar filas para mejorar métricas.
5. Regenerar el informe desde registros sin red, comprobar denominadores, coste calculado y cargo facturado separado. Medir revisión humana efectivamente realizada, no asumir que toda sugerencia fue revisada. Reportar latencia total de cada etapa, no solo tiempo del servidor.
6. Reproducir el test de aditividad con respuestas reales persistidas y el guard del consumidor. No volver a llamar a APIs para certificar esa propiedad.
7. Emitir `decision.json` y `decision.md` desde la regla pre-registrada, con incertidumbre y límites. Separar recomendación Jev de elegibilidad D6 y dejar transferencia PENDIENTE salvo autorización explícita posterior.

## Artefactos y verificaciones

Bajo `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-C/`: `preflight.json`, `respuestas.jsonl`, `consumo.json`, `informe_comparativa.json`, `aditividad.json`, `decision.json`, `decision.md`. Conectividad, ajuste y evaluación se distinguen en cada registro; nunca sobreescribir una corrida para ocultar un intento.

- AC4: tres brazos y mismo contenido semántico; `provider_effective = deepseek` para el comparador LLM.
- AC5: ACTIVAR/RECHAZAR solo con evidencia evaluable; MUESTRA-INSUFICIENTE con base; COSTE-NO-PAGADO cuando no se autoriza financiar/ejecutar. Error operativo: `run_status = FALLIDO`, `decision = null`.
- AC6: `removed: []` probado sobre guard real con las respuestas de esta corrida.
- AC8/AC12: intento autorizado y con reserva; no credenciales en logs. Un cargo desconocido no vale cero.
- AC7: D6 puede resultar elegible aunque gane DeepSeek. Recomendación no equivale a deuda cerrada ni a default cambiado.

Los comandos se toman del `--help` implementado y se registran exactamente en la evidencia. No hay ejemplo de llamada de pago ejecutable incrustado aquí para evitar confundir un prompt con autorización.

## Post-ejecución y detención

Aplicar post-fase del contrato: README, dependencias, checklist, 09, 10 y 00 con medidas reales. Re-ejecutar tests locales pertinentes y validaciones documentales; registrar iteraciones con unidad/corte. No cambiar código en esta fase ni corregir un fallo del runner a mitad de una medición.

- [ ] Registros completos o ejecución incompleta/fallida declarada; cero datos inventados para completar filas.
- [ ] Ningún ajuste influido por resultados de evaluación se presenta como confirmatorio.
- [ ] Presupuesto y uso desconocido conciliados o límite explícito que impide adoptar.
- [ ] Recomendación y transferencia separadas; no modificar planes hermanos sin instrucción.

Si falta permiso: checkpoint sin llamadas. Si falla autenticación/SDK/contabilidad: detener, conservar evidencia y solicitar remediación con alcance; no repetir automáticamente ni habilitar Anthropic. Sin comparación válida, no certificar AC4 como satisfecho.
