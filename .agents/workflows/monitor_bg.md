---
description: Monitoreo y control de tareas ejecutadas en segundo plano.
---

# Skill: Background Monitor (Gestor de Tareas)

> [!NOTE]
> **Trigger**: "monitorea tareas", "procesos en background", "qué está haciendo el agente".

## Pre-requisitos (Contexto)
- [ ] Tareas activas registradas en el AgentHarness.

## Fronteras (Scope)
- **Hará**: Listado de tareas activas (PID, Nombre, Duración), Chequeo de estado (Running/Failed/Finished), Captura de logs en tiempo real.
- **NO Hará**: No ejecuta nuevas tareas, solo gestiona la visibilidad de las existentes.

## Pasos de Ejecución

### 1. Listado de Procesos Activos
Consultar el estado de las tareas mediante el `AgentHarness.get_active_background_tasks()`.

*Validación*: Se muestra tabla con tareas y sus estados.

### 2. Inspección de Logs (Watch)
Verificar las últimas 10 líneas de logs de una tarea específica si está en estado 'running'.

*Validación*: Se muestra el progreso actual de la tarea.

### 3. Reaprovechamiento de Resultados
Integrar los datos de las tareas finalizadas en el contexto de memoria del hotel.

*Validación*: El `hotel_data` se actualiza con los resultados del scraping en background.

## Criterios de Éxito
- [ ] Tareas monitoreadas en tiempo real.
- [ ] No se pierden procesos por falta de visibilidad.
- [ ] Logs disponibles para debugging.

## Plan de Recuperación (Fallback)
- Si la tarea se congela, marcar como 'zombie' y sugerir reinicio.
- Si el monitor no carga, consultar el archivo `logs/execution_history.jsonl` directamente.
