# FASE-12C: Separación de servicios Schema Hotel / Schema Organization (OPCIONAL)

## Instrucciones de la sesión

> **REGLA**: Ejecutar solo si FASE-12A y 12B están completadas.

### Contexto
- Actualmente `PROPOSAL_SERVICE_TO_ASSET` mapea "Datos Estructurados" → "hotel_schema".
- `org_schema` existe como asset y tiene su propio pain_id (`no_org_schema`), pero no está separado en la propuesta.
- El cliente no sabe que ya tiene Organization y que le falta Hotel.

### Objetivo
Separar los servicios de schema para transparencia comercial.

### Tareas

- [ ] **1. Modificar `PROPOSAL_SERVICE_TO_ASSET`** — Agregar:
  ```python
  "Schema Hotel": "hotel_schema",
  "Schema Organization": "org_schema",
  ```
- [ ] **2. Actualizar `pain_solution_mapper.py`** — Verificar que `no_hotel_schema` y `no_org_schema` se activan/desactivan correctamente con los nuevos nombres.
- [ ] **3. Actualizar templates** — Si hay templates de propuesta que referencian "Datos Estructurados", actualizar.
- [ ] **4. Tests** — Agregar cobertura para la separación de servicios.
- [ ] **5. Ejecutar v4complete** — Verificar que la propuesta ahora muestra dos servicios separados.

### Restricciones
- Opcional — priorizar si hay tiempo.
- Máximo 60 iteraciones.

### Próxima sesión
FASE-RELEASE: Documentación final y validación.