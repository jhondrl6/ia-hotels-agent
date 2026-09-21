# Documentación acumulativa — EVALUACION-JEV-TYPESAFE-2026-09-21

Preparación ajustada el 2026-09-21. No es una declaración de implementación ni una orden para sincronizar VERSION. La documentación oficial se actualiza mediante el flujo de contribución cuando se ejecuten fases y exista autorización para su alcance.

## A. Módulos y archivos

| Superficie | Trabajo previsto | Resultado real |
|---|---|---|
| Documentos de este plan y su contexto | Contratos, evidencia de preparación, prompts y checklist | Ajustados en preparación; no código |
| `scripts/evaluate_jev_pilot.py` | A/B: muestra, checker, ejecución y reporte | PENDIENTE |
| `scripts/decision_client.py` | B externa crea; B propia integra proveedores con metadatos | PENDIENTE |
| `tests/quality_gates/jev_pilot/` | Tests deterministas, SDK y presupuesto | PENDIENTE |
| `modules/providers/llm_provider.py` | Ninguna modificación | FUERA DE ALCANCE |

## B. Capacidades

Pendientes: comparación búsqueda fría/DeepSeek/Jev, contabilidad por intento, preflight bloqueante, reproducción del informe y decisión aditiva. Ninguna se anuncia como entregada por haber escrito ACs.

DeepSeek habilitado por defecto y Anthropic sin API son información del operador, no capacidades nuevas implementadas en esta sesión. La selección explícita y la captura de usage todavía se deben construir detrás de la costura.

El SDK `typesafe-sdk==0.7.0` quedó instalado **solo en un entorno aislado** (`tmp_test/venv-jev-sdk`) para una sonda offline documentada en `10-analisis-post-implementacion.md` §Sonda de instalación. No es una capacidad entregada ni un cambio de dependencias del producto: `requirements.txt` y `venv/` no se tocaron, y la instalación principal está prohibida mientras el SDK resuelva pydantic por encima del pin del proyecto.

## C. Límites

No hay inferencias, etiquetas humanas del piloto, muestra congelada, presupuesto aprobado ni decisión de adopción. La autenticación, la cuota y el saldo de la cuenta Jev **no** se comprobaron: la sonda usó una clave sintética con transporte falso. El plan hermano no se modificó y su AC15 semántico parcial será admisible como entrada futura.

## D. Métricas acumulativas

| Magnitud | Preparación | A | B | C |
|---|---|---|---|---|
| Inferencias Jev | 0 | PENDIENTE | PENDIENTE | PENDIENTE |
| Inferencias DeepSeek | 0 | PENDIENTE | PENDIENTE | PENDIENTE |
| Tests nuevos del piloto | 0 | PENDIENTE | PENDIENTE | No código previsto |
| Calidad semántica | NO-EJERCITADA | NO-EJERCITADA | NO-EJERCITADA | PENDIENTE |
| Consumo/coste del piloto | NO-EJERCITADO | NO-EJERCITADO | NO-EJERCITADO | PENDIENTE |

Las validaciones documentales de preparación se registran en el análisis, no se cuentan como tests de rendimiento de proveedores.

## E. Documentos afiliados y permisos

- README, maestro, contrato, dependencias, checklist, prompts y Paso 0: escritos para este plan.
- Contexto de evaluación: actualizado con correcciones y confirmación DeepSeek/Anthropic.
- Índice generado: regenerar con su script y verificar tras la última edición.
- CHANGELOG, GUIA_TECNICA y REGISTRY: no se actualizan para simular una fase ejecutada; en fases futuras seguir CONTRIBUTING y resolver alcance antes de escribir.
- VERSION, AGENTS.md, .cursorrules y .agents: no se modifican.
- Write-back, archivado y push: no autorizados por la preparación. El commit de estos documentos sí se autorizó y ejecutó el 2026-09-21 (`2c966f6`).
