# Documentación Post-Proyecto — AGENTSMD-DRIFT

**Versión target:** v4.49.0  
**Proyecto:** iah-cli  
**Release date:** 2026-05-26

---

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| validate_agents_md | scripts/validate_agents_md.py | Script de 6 checks que audita AGENTS.md contra codigo vivo | FASE-A-01b |

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| AGENTS.md editorial fix | AGENTS.md | Corrección 9 pasos — test count 2743, gates 11, FASE-0 modules, evidence_ledger → DEPRECADO | FASE-A-01a |
| validate_agents_md gate | scripts/validate_agents_md.py | 6 checks automáticos integrados en flujo post-fase CONTRIBUTING.md §Paso 5.5 | FASE-A-01b |
| E2E Castilla Real verification | v4complete | Coherence 0.83, 9/11 gates, 11 pain entries, 12 assets | FASE-A-01c |

## Sección C: RELEASE — Cierre Documental v4.49.0

| Paso | Resultado |
|------|-----------|
| VERSION.yaml | 4.48.0 → 4.49.0 / AGENTSMD-DRIFT / 2026-05-26 |
| sync_versions.py | 6/7 OK (README.md WARN pre-existente — formato no coincide con sync_config.yaml) |
| version_consistency_checker.py | ✅ SINCRONIZADO |
| CHANGELOG.md | Entrada [4.49.0] con formato CONTRIBUTING.md |
| GUIA_TECNICA.md | Nota técnica v4.49.0 agregada |
| DOMAIN_PRIMER.md | Header actualizado (`.agent/knowledge/DOMAIN_PRIMER.md`) |
| README.md | Header manual actualizado (v4.49.0, 26 Mayo 2026, 2,743 tests) |
| AGENTS.md | agents_version corregido + paths 4 módulos corregidos (schema_validator_v2, pain_ledger, dashboard, calibration deprecados eliminados) |
| validate_agents_md.py | 6/6 PASS ✅ |
| run_all_validations.py | 4/5 PASS (Version Sync WARN por README pre-existente) |
| Pre-commit hooks | Version consistency ✅ / File sync OK |
| Git commit | `release: v4.49.0 AGENTSMD-DRIFT` — 23 files, 1800 insertions |
| log_phase_completion.py | FASE-RELEASE-4.49.0 registrada en REGISTRY.md |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Coherence Hotel Castilla Real | 0.83 | FASE-A-01c |
| Publication Gates PASS rate | 9/11 | FASE-A-01c |
| Pain Ledger entries | 11 | FASE-A-01c |
| Assets generados | 12 | FASE-A-01c |
| Human checklist items | 5 | FASE-A-01c |
| validate_agents_md checks | 6/6 PASS | FASE-RELEASE |
| Test suite | 2,743 tests, 0 regresiones | Todas |
| Files changed in release | 8 modificados + 1 nuevo | FASE-RELEASE |
| Git commit delta | +1800 −26 lines, 23 files | FASE-RELEASE |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| AGENTS.md | 9 pasos editoriales — conteo tests, gates, módulos FASE-0, evidence_ledger | FASE-A-01a |
| docs/CONTRIBUTING.md | Agregado Paso 5.5: validate_agents_md.py en flujo post-fase | FASE-A-01b |
| evidence/FASE-A-01c/ | Evidencia v4complete preservada (13 archivos) | FASE-A-01c |
| VERSION.yaml | 4.48.0 → 4.49.0 (AGENTSMD-DRIFT) | FASE-RELEASE |
| CHANGELOG.md | Entrada [4.49.0] completa | FASE-RELEASE |
| docs/GUIA_TECNICA.md | Nota técnica v4.49.0 | FASE-RELEASE |
| .agent/knowledge/DOMAIN_PRIMER.md | Header v4.49.0 | FASE-RELEASE |
| README.md | Header v4.49.0 manual | FASE-RELEASE |
| docs/contributing/REGISTRY.md | FASE-RELEASE-4.49.0 registrada | FASE-RELEASE |
| AGENTS.md | 4 paths modulares corregidos + agents_version actualizado | FASE-RELEASE |

## Sección F: WARN Conocidos (no bloqueantes)

| WARN | Causa | Estado |
|------|-------|--------|
| README.md sync pattern mismatch | sync_config.yaml espera formato `**Version:**` pero README.md usa `**v4.49.0** —` | Pre-existente (v4.48.0). No bloquea. |
| G8 asset_confidence (2 assets) | whatsapp_conflict_guide + hotel_schema bajo umbral | Advisory, no bloquea delivery |
