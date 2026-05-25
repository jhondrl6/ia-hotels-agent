# 09-documentacion-post-proyecto.md — COPYWRITING REFACTOR

> **Plan**: COPYWRITING-REFACTOR
> **Actualizado**: 2026-05-25

---

## Sección E — Documentación Post-Fase (OBLIGATORIO tras cada fase)

Cada fase DEBE ejecutar `log_phase_completion.py` al finalizar y marcar esta checklist.

### FASE-COPY-A: Template Restructuring + Generator Fixes

- [x] Ejecutar: `./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-COPY-A --desc "Template restructuring: owner-first view (diagnostico_v6), OTA narrative + honest finances (propuesta_v6), scenario clamp fix (_build_scenario_table_rows), tier consistency (evidence_tier passed to scenario table)" --check-manual-docs`
- [x] Verificar que REGISTRY.md tiene entrada FASE-COPY-A

### FASE-COPY-B: Commercial Gates + Content Validation

- [x] Ejecutar: `./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-COPY-B --desc "Commercial gates: scenario_order, roi_positive, ia_blocked_claim, whatsapp_lead, ota_narrative" --check-manual-docs`
- [x] Verificar que REGISTRY.md tiene entrada FASE-COPY-B

### FASE-COPY-C: E2E v4complete Validation

- [ ] Ejecutar: `./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-COPY-C --desc "E2E v4complete Hotel Castilla Real: validation against Copywriting.jsonl commercial gates" --check-manual-docs`
- [ ] Verificar que REGISTRY.md tiene entrada FASE-COPY-C

### FASE-COPY-RELEASE: Documentación y Cierre

- [ ] Ejecutar: `./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-COPY-RELEASE --desc "COPYWRITING-REFACTOR release: docs cascade, version bump, final validation" --check-manual-docs`
- [ ] Ejecutar: `./venv/Scripts/python.exe scripts/sync_versions.py`
- [ ] Verificar CHANGELOG.md actualizado
- [ ] Verificar GUIA_TECNICA.md con nota técnica
- [ ] Ejecutar: `./venv/Scripts/python.exe scripts/run_all_validations.py --quick` → 4/4
- [ ] Ejecutar: `./venv/Scripts/python.exe scripts/validate_document_integration.py`
- [ ] Ejecutar: `./venv/Scripts/python.exe scripts/doctor.py --status` → regenerar SYSTEM_STATUS.md
- [ ] Ejecutar: `./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer`

---

## Flujo Documental Obligatorio (RELEASE)

```
1. log_phase_completion.py --fase FASE-COPY-RELEASE --desc "..." --check-manual-docs
   → Registra en REGISTRY.md automáticamente

2. sync_versions.py
   → Sincroniza VERSION.yaml → 6 archivos (AGENTS, README, .cursorrules, CONTRIBUTING, GUIA_TECNICA, REGISTRY)

3. Verificar CHANGELOG.md formato CONTRIBUTING.md:
   ### Objetivo / ### Cambios / ### Archivos Nuevos / ### Archivos Modificados / ### Tests

4. Verificar GUIA_TECNICA.md tiene nota técnica por fase

5. run_all_validations.py --quick
   → Validación final (4/4 checks)

6. validate_document_integration.py
   → Gate de No-Regresión Documental
```
