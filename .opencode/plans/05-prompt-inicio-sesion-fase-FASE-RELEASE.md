# FASE-RELEASE: Documentación y validación final

## Instrucciones de la sesión

> **REGLA**: Solo se ejecuta cuando TODAS las fases de implementación (12-A, 12-B, 12-C) tienen ✅.

### Contexto
- Todos los fixes implementados y probados.
- Ahora se cierra con documentación oficial, version bump y validación completa.

### Tareas

- [ ] **1. Registrar fases** — Ejecutar `log_phase_completion.py` por cada fase completada:
  ```bash
  ./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-12A --desc "Fix expansion Hotel→LodgingBusiness en SitePresenceChecker (eliminada Organization y LocalBusiness)" --archivos-nuevos "tests/test_site_presence_checker.py" --archivos-mod "modules/asset_generation/site_presence_checker.py" --tests "5" --check-manual-docs
  ```
  ```bash
  ./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-12B --desc "Agregar coherence check audit↔presence en proposal_asset_alignment.py" --archivos-nuevos "tests/test_proposal_asset_alignment.py" --archivos-mod "modules/asset_generation/proposal_asset_alignment.py" --tests "2" --check-manual-docs
  ```
  (Si FASE-12C fue ejecutada, registrarla también.)
- [ ] **2. Sincronizar versiones** — `./venv/Scripts/python.exe scripts/sync_versions.py`
- [ ] **3. Verificar consistencia** — `./venv/Scripts/python.exe scripts/version_consistency_checker.py`
- [ ] **4. Validar CHANGELOG.md** — Verificar formato según CONTRIBUTING.md.
- [ ] **5. Validar GUIA_TECNICA.md** — Verificar que cada fase tiene su sección.
- [ ] **6. Actualizar `09-documentacion-post-proyecto.md`** — Secciones A, B, D, E.
- [ ] **7. Ejecutar v4complete FINAL** — `venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co/`
- [ ] **8. Guardar evidencia final** — `evidence/FASE-RELEASE/`
- [ ] **9. Ejecutar `run_all_validations.py --quick`** — 4/4.
- [ ] **10. Ejecutar `doctor.py --status`** — Sin errores.

### Entregables finales
- CHANGELOG.md actualizado.
- GUIA_TECNICA.md con notas técnicas.
- 09-documentacion-post-proyecto.md completo.
- Evidencia en `evidence/FASE-*/`.
- v4complete ejecutado con éxito para termales.com.co.
- Todos los tests pasando.
- `run_all_validations.py --quick` 4/4.