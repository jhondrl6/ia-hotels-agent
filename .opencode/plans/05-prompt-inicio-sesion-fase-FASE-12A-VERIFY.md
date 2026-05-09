# Verificación FASE-12A + Preparación FASE-12B

## Instrucciones de la sesión

> **REGLA**: Esta sesión ejecuta v4complete (comando de larga duración) y verifica resultados.

### Contexto
- FASE-12A completada: fix aplicado en `site_presence_checker.py`, tests creados.
- Ahora se debe verificar que el fix funciona en un escenario real.

### Tareas

- [ ] **1. Guardar evidencia previa** — Crear `evidence/FASE-12A/` y copiar cualquier output previo.
- [ ] **2. Ejecutar v4complete** — `venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co/`
  - Esperar finalización (~5-10 min).
- [ ] **3. Copiar evidencia** — `cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/FASE-12A/`
  - `cp output/v4_complete/02_PROPUESTA_*.md evidence/FASE-12A/`
  - `cp output/v4_complete/termales/v4_audit/*.json evidence/FASE-12A/`
- [ ] **4. Verificar `asset_generation_report.json`**:
  - `hotel_schema` ya NO debe aparecer como SKIPPED.
  - Debe aparecer como generado o al menos como intentado.
- [ ] **5. Verificar diagnóstico**:
  - `01_DIAGNOSTICO_*.md` debería reportar `hotel_schema` como presente o al menos no skippeado.
- [ ] **6. Ejecutar `run_all_validations.py --quick`** — Verificar no-regresión.

### Criterios de completitud
- v4complete ejecutado exitosamente.
- `hotel_schema` generado (no SKIPPED).
- Evidencia guardada en `evidence/FASE-12A/`.
- `run_all_validations.py --quick` no reporta regresiones.

### Próxima sesión
FASE-12B: Implementar coherence check en `proposal_asset_alignment.py`.