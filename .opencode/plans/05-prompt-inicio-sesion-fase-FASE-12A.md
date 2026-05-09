# FASE-12A: Fix causa raíz — Eliminar expansión Hotel→{LocalBusiness, Organization}

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.

### Contexto previo
- Auditoría M6 detectó divergencia entre `hotel_schema_detected` (audit) y `hotel_schema` (gate/SitePresenceChecker).
- Causa raíz: `site_presence_checker.py:365` expande Hotel a `[LodgingBusiness, LocalBusiness, Organization]`.
- El audit path (`rich_results_client.py:537`) solo acepta Hotel y LodgingBusiness.
- Resultado: sitios con solo Organization reportan `hotel_schema=EXISTS` → asset SKIPPED → falso positivo.

### Objetivo de esta fase
1. Fix línea 365 en `site_presence_checker.py` — eliminar `LocalBusiness` y `Organization`.
2. Crear `tests/test_site_presence_checker.py` con cobertura mínima.
3. Ejecutar tests y verificar que el fix es correcto.

### Tareas

- [x] Leer y confirmar la línea exacta a modificar en `modules/asset_generation/site_presence_checker.py` L364-365.
- [x] Aplicar fix: cambiar `target_types.extend(["LodgingBusiness", "LocalBusiness", "Organization"])` → `target_types.extend(["LodgingBusiness"])`.
- [x] Crear `tests/test_site_presence_checker.py` con al menos 5 casos:
  - Hotel presente → found ✅
  - Solo Organization → NOT_FOUND ✅
  - Solo LocalBusiness → NOT_FOUND ✅
  - LodgingBusiness presente → found ✅
  - Schema vacío → NOT_FOUND ✅
- [x] Ejecutar tests: `venv/Scripts/python.exe -m pytest tests/test_site_presence_checker.py -v`
  - Resultado: **5/5 passed**
- [x] Verificar que todos los tests pasan.
- [x] Verificar regresion en asset_generation: 328 passed, 1 pre-existing failure (test_generate_geo_playbook — no relacionada con el fix).

### Restricciones
- NO ejecutar v4complete en esta sesión (será en la siguiente sub-fase de verificación).
- NO modificar otros módulos.
- Máximo 60 iteraciones.

### Entregable
- `site_presence_checker.py` modificado (línea 365).
- `tests/test_site_presence_checker.py` creado y pasando.

### Próxima sesión
Ejecutar v4complete para termales.com.co y verificar que `hotel_schema` se genera correctamente.