# Plan de Refactorización — Auditoría M6 Hotel Schema (Termales Santa Rosa de Cabal)

> **Proyecto**: iah-cli — Divergencia `hotel_schema` entre audit path y SitePresenceChecker  
> **Sitio**: http://www.termales.com.co/  
> **Fecha**: 2026-05-09  
> **Versionamiento**: Sin cambio de versión (fix interno)

---

## FASE-12A: Fix causa raíz — Eliminar expansión Hotel→{LocalBusiness, Organization}

### Objetivo
Eliminar el falso positivo que hace que `SitePresenceChecker._check_schema_exists("Hotel", …)`
detecte `Organization` y `LocalBusiness` como si fueran `Hotel`, causando que el asset
`hotel_schema` se marque como SKIPPED cuando en realidad **no existe** schema Hotel en el sitio.

### Tareas

- [ ] **1. Investigar código vivo** — Leer `modules/asset_generation/site_presence_checker.py` L353-376 y confirmar la línea exacta de expansión (L364-365).
- [ ] **2. Aplicar fix SOL-1** — Cambiar L365: eliminar `"LocalBusiness"` y `"Organization"` de la expansión. Dejar solo `["LodgingBusiness"]`.
- [ ] **3. Crear tests unitarios** — Crear `tests/test_site_presence_checker.py` con cobertura mínima:
  - Hotel presente → found
  - Solo Organization → NOT_FOUND (post-fix)
  - Solo LocalBusiness → NOT_FOUND (post-fix)
  - LodgingBusiness presente → found
  - Hotel + Organization mix → found (Hotel match priorizado)
  - Schema vacío → NOT_FOUND
- [ ] **4. Ejecutar tests** — `venv/Scripts/python.exe -m pytest tests/test_site_presence_checker.py -v`
- [ ] **5. Ejecutar v4complete** — `venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co/`
- [ ] **6. Verificar output** — Confirmar que `asset_generation_report.json` ya NO marca `hotel_schema` como SKIPPED; el asset debe generarse.

### Restricciones
- Solo se modifica `site_presence_checker.py` y se crea el archivo de tests.
- No tocar `proposal_asset_alignment.py`, `coherence_validator.py`, ni `pain_solution_mapper.py` en esta fase.
- Máximo 60 iteraciones.

### Criterios de completitud
- `site_presence_checker.py` L365 contiene **solo** `["LodgingBusiness"]`.
- `tests/test_site_presence_checker.py` existe con ≥ 5 casos de test, todos pasando.
- `v4complete` genera `hotel_schema` asset (no SKIPPED).
- `run_all_validations.py --quick` no reporta regresiones.

---

## FASE-12B: Coherence gate — Detección de divergencia audit↔presence

### Objetivo
Agregar un chequeo de consistencia para que, cuando el audit diga `hotel_schema_detected=false`
pero `SitePresenceChecker` reporte `EXISTS`, el gate marque `DIVERGENT` en vez de `is_coherent: true`.

### Tareas

- [ ] **1. Investigar flujo de coherencia** — Leer `proposal_asset_alignment.py` desde `verify_proposal_asset_alignment()` (L146) hasta el final, y `coherence_validator.py` si existe.
- [ ] **2. Implementar check de divergencia** — En `proposal_asset_alignment.py`, dentro de `verify_proposal_asset_alignment()`, antes de marcar `present_in_production`, agregar lógica SOL-2:
  ```python
  if expected_asset_type == "hotel_schema" and presence_status == "exists":
      audit_report = assessment.get("audit_report", {})
      schema_data = audit_report.get("schema", {})
      if not schema_data.get("hotel_schema_detected", False):
          report.missing.append(ServiceAlignment(
              service_name=service_name,
              asset_type=expected_asset_type,
              is_aligned=False,
              status="missing",
              message="DIVERGENCIA: SitePresenceChecker reporta EXISTS pero audit dice hotel_schema_detected=false.",
              presence_verified=True,
              presence_status="divergent"
          ))
          continue
  ```
- [ ] **3. Agregar estado `divergent`** — Asegurar que `ServiceAlignment.presence_status` acepte `"divergent"` como valor válido.
- [ ] **4. Tests** — Agregar tests unitarios para el caso de divergencia en un nuevo archivo `tests/test_proposal_asset_alignment.py` o en uno existente.
- [ ] **5. Ejecutar v4complete** — Re-ejecutar sobre termales.com.co y verificar que `coherence_report` ya NO muestra `is_coherent: true` cuando hay divergencia.

### Restricciones
- No modificar el fix de FASE-12A.
- Máximo 60 iteraciones.

### Criterios de completitud
- La divergencia hotel_schema se detecta explícitamente como `"divergent"`.
- `is_coherent` es `false` cuando audit y presence discrepan.
- Tests pasando.

---

## FASE-12C: Separación de servicios en propuesta (OPCIONAL)

### Objetivo
Separar `Schema Hotel` y `Schema Organization` en `PROPOSAL_SERVICE_TO_ASSET` para transparencia
comercial: el cliente ve que ya tiene Organization y necesita Hotel schema.

### Tareas

- [ ] **1. Modificar `PROPOSAL_SERVICE_TO_ASSET`** — Agregar `"Schema Organization": "org_schema"` si no existe.
- [ ] **2. Actualizar `pain_solution_mapper.py`** — Verificar que `no_org_schema` se activa/desactiva correctamente.
- [ ] **3. Actualizar templates de propuesta** — Documentar los cambios en templates.
- [ ] **4. Tests** — Agregar cobertura para la separación.

### Restricciones
- Opcional — solo si FASE-12A y 12-B están completadas.
- Máximo 60 iteraciones.

### Criterios de completitud
- `PROPOSAL_SERVICE_TO_ASSET` tiene entradas separadas para Hotel y Organization.
- Propuesta comercial refleja el estado real de cada schema.
- Tests pasando.

---

## FASE-RELEASE: Documentación y validación final

### Objetivo
Cerrar el ciclo con documentación, changelog, y ejecución final de v4complete sobre termales.com.co.

### Tareas

- [ ] **1. Actualizar `09-documentacion-post-proyecto.md`** — Sección E: listar todos los archivos modificados.
- [ ] **2. Actualizar `CHANGELOG.md`** — Entrada con formato correcto.
- [ ] **3. Actualizar `GUIA_TECNICA.md`** — Notas técnicas por fase.
- [ ] **4. Ejecutar `log_phase_completion.py`** — Una vez por cada fase completada (12-A, 12-B, 12-C si aplica).
- [ ] **5. Ejecutar `sync_versions.py`** — Sincronizar VERSION.yaml.
- [ ] **6. Ejecutar `version_consistency_checker.py`**.
- [ ] **7. Ejecutar final de v4complete** — `venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co/` y verificar:
  - `hotel_schema` generado (no SKIPPED).
  - `coherence_report.is_coherent` = `false` si hay divergencia (correcto).
  - Diagnóstico y propuesta coherentes.
- [ ] **8. Ejecutar `run_all_validations.py --quick`** — Pasar 4/4.
- [ ] **9. Ejecutar `doctor.py --status`** — Sin errores.
- [ ] **10. Guardar evidencia** — Copiar output a `evidence/FASE-12/`.

### Criterios de completitud
- CHANGELOG.md con formato correcto.
- GUIA_TECNICA.md con notas de cada fase.
- v4complete ejecutado y documentado.
- 09-documentacion-post-proyecto.md completo.
- `run_all_validations.py --quick` 4/4.

---

## Estado actual

| Fase      | Estado     |
|-----------|------------|
| FASE-12A  | ⏳ Pendiente |
| FASE-12B  | ⏳ Pendiente |
| FASE-12C  | ⏳ Pendiente (opcional) |
| FASE-RELEASE | ⏳ Pendiente |