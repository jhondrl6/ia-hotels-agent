# Checklist de Implementacion — FASE-TRAZABILIDAD-REFINEMENT

> **Regla**: Una fase por sesion. Marcar [x] al completar. Si algo falla, cancelar y crear item de recuperacion.

---

## T0: Pre-flight

| # | Verificacion | Comando | Estado |
|---|-------------|---------|--------|
| 0.1 | venv existe | `ls venv/Scripts/python.exe` | [ ] |
| 0.2 | Skills cargados | `skill_view iah-cli-plan-vs-reality-check` | [ ] |
| 0.3 | geo_flow_result.json existe | `ls output/v4_complete/amazilia_hotel/v4_audit/geo_flow_result.json` | [ ] |
| 0.4 | geo_assessment.total_score = 23 | `python -c "import json;..."` | [ ] |

---

## T1: Corregir lectura Salud Tecnica GEO (D3)

| # | Accion | Archivo | Lineas | Estado |
|---|--------|---------|--------|--------|
| 1.1 | Cambiar `geo_flow_data.get('geo_score')` → `geo_assessment.get('total_score')` | `v4_diagnostic_generator.py` | 1258-1261 | [ ] |
| 1.2 | Cambiar `geo_flow_data.get('status')` → `geo_assessment.get('band')` | `v4_diagnostic_generator.py` | 1258-1261 | [ ] |
| 1.3 | Verificar con script de prueba | `python -c "..."` (ver T1 en prompt) | — | [ ] |

---

## T2: WARNING en summary de readiness (D1)

| # | Accion | Archivo | Lineas | Estado |
|---|--------|---------|--------|--------|
| 2.1 | Agregar `"warnings"` key al dict `summary` | `publication_gates.py` | 1008-1014 | [ ] |
| 2.2 | Verificar que `GateStatus.WARNING` se usa correctamente | `publication_gates.py` | grep WARNING | [ ] |
| 2.3 | `git diff` muestra solo adicion de `"warnings"` key | — | — | [ ] |

---

## T3: Visibilidad Tier C en encabezado (D2)

| # | Accion | Archivo | Lineas | Estado |
|---|--------|---------|--------|--------|
| 3.1 | Modificar `_build_financial_title_label()` para retornar dict con `tier_suffix` | `v4_diagnostic_generator.py` | 703-715 | [ ] |
| 3.2 | Agregar `financial_tier_suffix` y `financial_tier_banner` al template_data | `v4_diagnostic_generator.py` | ~462 | [ ] |
| 3.3 | Agregar `${financial_tier_banner}` y `${financial_tier_suffix}` al template | `diagnostico_v6_template.md` | 68-76 | [ ] |
| 3.4 | Verificar que el template compila sin variables faltantes | `grep '${' templates/diagnostico_v6_template.md` | — | [ ] |

---

## T4: Nota asset_confidence en diagnostico (D4)

| # | Accion | Archivo | Lineas | Estado |
|---|--------|---------|--------|--------|
| 4.1 | Leer `asset_generation_report.json` en `generate()` | `v4_diagnostic_generator.py` | ~462 | [ ] |
| 4.2 | Construir `asset_confidence_note` si hay assets < 0.7 | `v4_diagnostic_generator.py` | — | [ ] |
| 4.3 | Agregar `${asset_confidence_note}` al template (antes de `${manual_attention_table}`) | `diagnostico_v6_template.md` | 82 | [ ] |
| 4.4 | Agregar `asset_confidence_note` al template_data | `v4_diagnostic_generator.py` | ~462 | [ ] |

---

## T5: Ejecucion v4complete Amazilia Hotel

| # | Accion | Comando | Estado |
|---|--------|---------|--------|
| 5.1 | Ejecutar v4complete | `venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/` | [ ] |
| 5.2 | Verificar exit code = 0 | — | [ ] |
| 5.3 | Verificar Pilar GEO != "0/100" | `grep "GEO" output/v4_complete/01_DIAGNOSTICO_*.md` | [ ] |
| 5.4 | Verificar Salud Tecnica GEO muestra score > 0 | `grep "Salud" output/v4_complete/01_DIAGNOSTICO_*.md` | [ ] |
| 5.5 | Verificar gate_report.json tiene `summary.warnings` | `python -c "import json;..."` | [ ] |
| 5.6 | Si Tier C: verificar banner + sufijo en diagnostico | `grep "Tier C" output/v4_complete/01_DIAGNOSTICO_*.md` | [ ] |
| 5.7 | Si assets baja confianza: verificar nota de transparencia | `grep "confianza baja" output/v4_complete/01_DIAGNOSTICO_*.md` | [ ] |

---

## Post-Ejecucion

| # | Accion | Comando | Estado |
|---|--------|---------|--------|
| P.1 | Registrar fase en REGISTRY.md | `log_phase_completion.py --fase FASE-TRAZABILIDAD-REFINEMENT ...` | [ ] |
| P.2 | Commit cambios | `git add -A && git commit -m "fix: FASE-TRAZABILIDAD-REFINEMENT ..."` | [ ] |

---

## Resumen

- **Total items**: 20
- **Tiempo estimado**: 45-60 min (incluye ejecucion v4complete ~3-5 min)
- **Costo API**: Solo 1 ejecucion v4complete (~$0.50-1.50 USD estimado)
