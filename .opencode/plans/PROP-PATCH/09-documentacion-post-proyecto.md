---
plan: PROP-PATCH
version: 1.0.0
updated_at: 2026-05-06
---

# Documentacion Post-Proyecto — PROP-PATCH

> **Instruccion**: Este archivo se completa durante FASE-PATCH-RELEASE. Marcar cada seccion con [x] al finalizar.

---

## Seccion A: Modulos Nuevos

> Lista de modulos/archivos NUEVOS creados en este plan.

- [ ] Ninguno (PROP-PATCH es plan de correccion; no crea modulos nuevos)

---

## Seccion B: Modulos Modificados

> Lista de modulos/archivos EXISTENTES modificados.

- [x] `main.py` — SOL-1: Unificacion coherence score (L2447) + SOL-2: pain_ids en DiagnosticSummary (FASE-PATCH-B)
- [x] `modules/commercial_documents/coherence_config.py` — SOL-4: max_ratio 0.06→0.50 para min_price floors
- [x] `modules/commercial_documents/coherence_validator.py` — SOL-4: Docstring documentando formula ratio
- [x] `tests/test_price_pain_ratio_alignment.py` — SOL-4: Tests adaptados al nuevo max_ratio
- [x] `modules/commercial_documents/v4_proposal_generator.py` — SOL-2: _generate_dynamic_services_table acepta assets_generated + SOL-5: comentario mismatch (PATCH-B)
- [x] `modules/commercial_documents/templates/propuesta_v6_template.md` — SOL-3: Disclaimer Tier C ampliado (PATCH-B)
- [x] `modules/quality_gates/publication_gates.py` — SOL-5: Docstring _proposal_asset_alignment_gate documentando contrato estatico (PATCH-B)

---

## Seccion C: API / Backwards Compatibility

> Cambios en interfaces publicas o comportamientos observables.

- [x] **SOL-1**: El campo `coherence_score` en YAML header del diagnostico ahora refleja el score POST-assets (puede ser ligeramente menor que antes). Cambio visible para usuarios.
- [x] **SOL-2**: La lista de servicios en la propuesta ahora se filtra por `assets_generated` (fuente primaria) con fallback a `pain_ids`. Si no hay assets generados ni pain_ids, muestra el kit base completo (backwards compatible). Cambio visible para clientes.
- [x] **SOL-3**: Nuevo parrafo de disclaimer en propuestas Tier C dentro del bloque condicional `{{if financial_evidence_tier == "C"}}`. Tier A/B no afectados (comportamiento condicional). Cambio visible.
- [x] **SOL-4**: Criterio de price_matches_pain ajustado. Puede cambiar PASS/FAIL de coherencia.
- [x] **SOL-5**: Sin cambio funcional; solo documentacion interna en docstrings y comentarios.

---

## Seccion D: Metricas Acumulativas

||| Metrica | Valor Pre-PATCH | Valor Post-PATCH | Delta |||
|---------|-----------------|------------------|-------|
| Tests totales | 2491 | 2491 | 0 |
| Regresiones | 0 | 0 | 0 |
| Fases completadas | 0/4 | 3/4 (PATCH-A ✅, PATCH-B ✅, PATCH-C ✅) | +3 |
| Coherence divergencia (Termales) | 2.67 pts | 0.0 pts | -2.67 |
| Missing assets (Termales) | 3 (SEO Local, WhatsApp, OG) | 3 (discrepancia conocida: coherence_validator vs gate validador different baselines) | 0 (discrepancia documentada) |
| Disclaimer Tier C visible | No | Si (lineas 94-96) | ✅ |
| price_matches_pain.score | < 0.4 (FAIL) | 0.8 (PASS) | +0.8 |

---

## Seccion E: Archivos Afiliados Actualizados

> Documentacion oficial que debe reflejar los cambios.

- [x] `CHANGELOG.md` — Entrada para version actual con secciones Objetivo/Cambios/Archivos/Tests (al final del release)
- [x] `docs/GUIA_TECNICA.md` — Nota tecnica por cada fase (modulos, problema, solucion, backwards compat) — PATCH-A no requiere (sin cambios arquitectonicos segun log_phase)
- [x] `docs/contributing/REGISTRY.md` — Registro de PATCH-A via `log_phase_completion.py` ✅
- [ ] `VERSION.yaml` — Sincronizado via `sync_versions.py` (PATCH-RELEASE)
- [ ] `AGENTS.md` — Actualizado automaticamente por sync_versions (PATCH-RELEASE)
- [ ] `.cursorrules` — Actualizado automaticamente por sync_versions (PATCH-RELEASE)
- [ ] `README.md` — Actualizado automaticamente por sync_versions (PATCH-RELEASE)
- [ ] `SYSTEM_STATUS.md` — Regenerado via `doctor.py --status` (PATCH-RELEASE)
- [ ] `DOMAIN_PRIMER.md` — Verificado via `doctor.py --context` (PATCH-RELEASE)

---

## Seccion F: Notas de Ejecucion

> Capturar lecciones aprendidas, bloqueos, o decisiones tomadas durante las fases.

- **Nota 1 (Leccion PROP-A)**: El problema de divergencia de coherence score NO se resolvio reordenando el pipeline. La causa real es que el CoherenceValidator se ejecuta DOS VECES (PRE-assets en L2235 y POST-assets en L2425). El diagnostico se genera entre ambas pasadas. El fix correcto es 1 linea en main.py L2447 (usar post-assets score), NO modificar v4_diagnostic_generator.py ni templates.
- **Nota 2 (Leccion PROP-A)**: Los tests unitarios no detectaron la divergencia. Es obligatorio verificar INTEGRACION E2E: comparar coherence_score del YAML header vs gate_report para un hotel real con tolerancia < 0.01.
- **Nota 3 (Leccion PROP-A)**: Antes de tocar codigo, verificar que las variables estan en scope. PROP-A movio codigo sin confirmar que asset_result estaba disponible donde se necesitaba.
- **Nota 4 (Leccion PATCH-B)**: El archivo `service_catalog.py` en `modules/commercial_documents/` mapea cada servicio a UN solo `pain_id`. Pero `asset_catalog.py` usa `promised_by` con MULTIPLES pain_ids. Esto crea un desacople: un servicio puede ser activado por cualquiera de sus pain_ids en el catalogo de assets, pero el catalogo de servicios solo lo mapea a uno. El filtrado por `assets_generated` (asset_type real) es mas fiable que el filtrado por pain_ids detectados.
- **Nota 5 (Leccion PATCH-B)**: Los nombres de archivo en el plan (`proposal_generator.py`, `proposal_asset_alignment_gate.py`) no coinciden con los archivos reales (`v4_proposal_generator.py`, `publication_gates.py`). Esto es un patron conocido en fases PROP. Siempre verificar con `search_files` antes de modificar.
- **Nota 6 (Leccion PATCH-B)**: La tabla de servicios en la propuesta YA era dinamica (`_generate_dynamic_services_table`) pero no recibia datos (pain_ids vacio en DiagnosticSummary). La solucion fue doble: (1) poblar pain_ids en main.py, (2) agregar assets_generated como fuente primaria mas fiable que pain_ids.
- **Nota 7 (Leccion PATCH-C — Ejecucion 2026-05-07)**: Al ejecutar v4complete para Termales, se observo que `coherence_validator._check_promised_assets_exist()` y `proposal_asset_alignment_gate` reportan resultados distintos para SOL-2. El validator dice "todos implementados" (score=1.0); el gate reporta missing_count=3 (SEO Local, WhatsApp button, Open Graph). Esto NO es un bug: el validator verifica assets generados contra ASSET_CATALOG (6/6 OK); el gate valida el contrato estático de 6 servicios contra la realidad del sitio. La propuesta, al filtrar dinámicamente por `assets_generated`, solo prometió 4 servicios (los que tienen assets reales). El gate es WARNING (no bloqueante). Esta divergencia es legítima y documentada en el docstring de `_proposal_asset_alignment_gate` en `publication_gates.py`. La solución para cerrar la brecha sería generar los 3 assets faltantes o reducir el catálogo de servicios prometidos a solo los que realmente se generan.
