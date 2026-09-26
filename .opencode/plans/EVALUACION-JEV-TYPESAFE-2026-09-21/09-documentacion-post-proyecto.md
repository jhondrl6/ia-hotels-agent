# Documentación acumulativa — EVALUACION-JEV-TYPESAFE-2026-09-21

Preparación ajustada el 2026-09-21. No es una declaración de implementación ni una orden para sincronizar VERSION. La documentación oficial se actualiza mediante el flujo de contribución cuando se ejecuten fases y exista autorización para su alcance.

## A. Módulos y archivos

| Superficie | Trabajo previsto | Resultado real |
|---|---|---|
| Documentos de este plan y su contexto | Contratos, evidencia de preparación, prompts y checklist | Ajustados en preparación; no código |
| `scripts/evaluate_jev_pilot.py` | A/B: muestra, checker, ejecución y reporte | **PARCIAL (A 2026-09-21)**: modos offline `prepare`/`check` + métricas creados y auto-verificados; `run`/`decide` se niegan (B/C) |
| `scripts/decision_client.py` | B externa crea; B propia integra proveedores con metadatos | PENDIENTE |
| `tests/quality_gates/jev_pilot/` | Tests deterministas, SDK y presupuesto | **PARCIAL (A)**: `test_jev_pilot_offline.py` 7/7 verde (guards con par causal); tests de SDK/presupuesto en B |
| `modules/providers/llm_provider.py` | Ninguna modificación | FUERA DE ALCANCE |

## B. Capacidades

Pendientes: comparación búsqueda fría/DeepSeek/Jev, contabilidad por intento, preflight bloqueante, reproducción del informe y decisión aditiva. Ninguna se anuncia como entregada por haber escrito ACs.

DeepSeek habilitado por defecto y Anthropic sin API son información del operador, no capacidades nuevas implementadas en esta sesión. La selección explícita y la captura de usage todavía se deben construir detrás de la costura.

El SDK `typesafe-sdk==0.7.0` quedó instalado **solo en un entorno aislado** (`tmp_test/venv-jev-sdk`) para una sonda offline documentada en `10-analisis-post-implementacion.md` §Sonda de instalación. No es una capacidad entregada ni un cambio de dependencias del producto: `requirements.txt` no se tocó y el SDK sigue fuera de `venv/`, con la instalación principal prohibida mientras el SDK resuelva pydantic por encima del pin del proyecto. **Corrección posterior del mismo día:** `venv/` sí cambió, pero no por el SDK — se alineó su pydantic al pin (`2.12.3`→`2.12.5`, core `2.41.4`→`2.41.5`, +`pydantic-settings 2.10.1`) para cerrar un desajuste preexistente; ver `10-analisis-post-implementacion.md` §Alineación de pydantic en el venv.

## C. Límites

No hay inferencias, etiquetas humanas del piloto, muestra congelada, presupuesto aprobado ni decisión de adopción. La autenticación, la cuota y el saldo de la cuenta Jev **no** se comprobaron: la sonda usó una clave sintética con transporte falso. El plan hermano no se modificó y su AC15 semántico parcial será admisible como entrada futura.

## D. Métricas acumulativas

| Magnitud | Preparación | A | B | C |
|---|---|---|---|---|
| Inferencias Jev | 0 | PENDIENTE | PENDIENTE | PENDIENTE |
| Inferencias DeepSeek | 0 | PENDIENTE | PENDIENTE | PENDIENTE |
| Tests nuevos del piloto | 0 | **Entregados por A**: `tests/quality_gates/jev_pilot/test_jev_pilot_offline.py` (7 funciones `def test_`, corrida «7 passed» en `10-analisis-post-implementacion.md`), más `scripts/evaluate_jev_pilot.py` con sus modos `prepare`/`check` y `run`/`decide` negados explícitamente. ⟦Rectificado el 2026-09-24 por el bloque C de la orden de calidad: esta celda decía «PENDIENTE»⟧ | PENDIENTE | No código previsto |
| Calidad semántica | NO-EJERCITADA | NO-EJERCITADA | NO-EJERCITADA | PENDIENTE |
| Consumo/coste del piloto | NO-EJERCITADO | NO-EJERCITADO | NO-EJERCITADO | PENDIENTE |

Las validaciones documentales de preparación se registran en el análisis, no se cuentan como tests de rendimiento de proveedores.

## E. Documentos afiliados y permisos

- README, maestro, contrato, dependencias, checklist, prompts y Paso 0: escritos para este plan.
- Contexto de evaluación: actualizado con correcciones y confirmación DeepSeek/Anthropic.
- Índice generado: regenerar con su script y verificar tras la última edición.
- CHANGELOG, GUIA_TECNICA y REGISTRY: no se actualizan para simular una fase ejecutada; en fases futuras seguir CONTRIBUTING y resolver alcance antes de escribir.
- VERSION, AGENTS.md, .cursorrules y .agents: no se modifican.
- Write-back y archivado: no autorizados por la preparación. El commit de estos documentos (`2c966f6`) y su push a `origin/master` (rango hasta `99ac860`) sí se autorizaron y ejecutaron el 2026-09-21.
