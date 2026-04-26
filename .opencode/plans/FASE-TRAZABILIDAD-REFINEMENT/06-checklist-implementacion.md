# Checklist de Implementacion — FASE-TRAZABILIDAD-REFINEMENT

> **Regla**: Una fase por sesion. Marcar [x] al completar. Si algo falla, cancelar y crear item de recuperacion.

---

## T0: Pre-flight

| # | Verificacion | Comando | Estado |
|---|-------------|---------|--------|
| 0.1 | venv existe | `ls venv/Scripts/python.exe` | [x] |
| 0.2 | Skills cargados | `skill_view iah-cli-plan-vs-reality-check` | [x] |
| 0.3 | geo_flow_result.json existe | `ls output/v4_complete/amazilia_hotel/v4_audit/geo_flow_result.json` | [x] |
| 0.4 | geo_assessment.total_score = 23 | `python -c "import json;..."` | [x] |

---

## T1: Corregir lectura Salud Tecnica GEO (D3)

| # | Accion | Archivo | Lineas | Estado |
|---|--------|---------|--------|--------|
| 1.1 | Cambiar `geo_flow_data.get('geo_score')` → `geo_assessment.get('total_score')` | `v4_diagnostic_generator.py` | 1273-1275 | [x] |
| 1.2 | Cambiar `geo_flow_data.get('status')` → `geo_assessment.get('band')` | `v4_diagnostic_generator.py` | 1273-1275 | [x] |
| 1.3 | Verificar con script de prueba | `python -c "..."` (ver T1 en prompt) | — | [x] |

---

## T2: WARNING en summary de readiness (D1)

| # | Accion | Archivo | Lineas | Estado |
|---|--------|---------|--------|--------|
| 2.1 | Agregar `"warnings"` key al dict `summary` | `publication_gates.py` | 1013-1019 | [x] |
| 2.2 | Verificar que `GateStatus.WARNING` se usa correctamente | `publication_gates.py` | grep WARNING | [x] |
| 2.3 | `git diff` muestra solo adicion de `"warnings"` key | — | — | [x] |

---

## T3: Visibilidad Tier C en encabezado (D2)

| # | Accion | Archivo | Lineas | Estado |
|---|--------|---------|--------|--------|
| 3.1 | Agregar `financial_tier_suffix` y `financial_tier_banner` en `_build_financial_placeholders()` | `v4_diagnostic_generator.py` | 767-795 | [x] |
| 3.2 | Agregar variables al diccionario de retorno | `v4_diagnostic_generator.py` | 793-795 | [x] |
| 3.3 | Agregar `${financial_tier_banner}` y `${financial_tier_suffix}` al template | `diagnostico_v6_template.md` | 70-73 | [x] |
| 3.4 | Verificar que el template compila sin variables faltantes | `grep '${' templates/diagnostico_v6_template.md` | — | [x] |

---

## T4: Nota asset_confidence en diagnostico (D4)

| # | Accion | Archivo | Lineas | Estado |
|---|--------|---------|--------|--------|
| 4.1 | Leer `asset_generation_report.json` en `generate()` | `v4_diagnostic_generator.py` | 464 | [x] |
| 4.2 | Construir `asset_confidence_note` si hay assets < 0.7 | `v4_diagnostic_generator.py` | 1877-1899 | [x] |
| 4.3 | Agregar `${asset_confidence_note}` al template (antes de `${manual_attention_table}`) | `diagnostico_v6_template.md` | 85 | [x] |
| 4.4 | Agregar `asset_confidence_note` al template_data | `v4_diagnostic_generator.py` | 464 | [x] |

---

## T5: Ejecucion v4complete Amazilia Hotel

| # | Accion | Comando | Estado |
|---|--------|---------|--------|
| 5.1 | Ejecutar v4complete | `venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/` | [x] |
| 5.2 | Verificar exit code = 0 | — | [x] |
| 5.3 | Verificar Pilar GEO != "0/100" | `grep "GEO" output/v4_complete/01_DIAGNOSTICO_*.md` | [x] |
| 5.4 | Verificar Salud Tecnica GEO muestra score > 0 | `grep "Salud" output/v4_complete/01_DIAGNOSTICO_*.md` | [x] |
| 5.5 | Verificar gate_report.json tiene `summary.warnings` | `python -c "import json;..."` | [x] |
| 5.6 | Si Tier C: verificar banner + sufijo en diagnostico | `grep "Tier C" output/v4_complete/01_DIAGNOSTICO_*.md` | [x] |
| 5.7 | Si assets baja confianza: verificar nota de transparencia | `grep "confianza baja" output/v4_complete/01_DIAGNOSTICO_*.md` | [x] |

---

## Post-Ejecucion

| # | Accion | Comando | Estado |
|---|--------|---------|--------|
| P.1 | Registrar fase en REGISTRY.md | `log_phase_completion.py --fase FASE-TRAZABILIDAD-REFINEMENT ...` | [x] |
| P.2 | Commit cambios | `git add -A && git commit -m "fix: FASE-TRAZABILIDAD-REFINEMENT ..."` | [x] |

---

## Documentacion Post-Fase (verificacion contra CONTRIBUTING.md)

| # | Documento | Verificado | Estado |
|---|-----------|-----------|--------|
| D.1 | CHANGELOG.md — seccion REFINEMENT bajo 4.35.1 | D1-D4 documentados como RESUELTOS | [x] |
| D.2 | GUIA_TECNICA.md — header version | v4.35.1 / 2026-04-25 | [x] |
| D.3 | GUIA_TECNICA.md — nota tecnica REFINEMENT | D1-D4 + decision GEO | [x] |
| D.4 | CONTRIBUTING.md — header version | v4.35.1 | [x] |
| D.5 | sync_versions.py —check | All files in sync | [x] |
| D.6 | Checklist plan actualizado | 27/27 items [x] | [x] |

---

## Resumen

- **Total items codigo**: 20
- **Total items documentacion**: 6
- **Total general**: 26
- **Completados**: 26
- **Tiempo**: Fase completada en sesion 2026-04-25
- **Commit**: `a46f831`
