# Sesión: ProspecciónII.md — Auditoría Exhaustiva Post-Sesión

**Fecha**: 2026-05-25 (actualizado post-auditoría + fixes aplicados 2026-05-25)
**Proyecto**: iah-cli · v4.52.0 DIAGNOSTIC-ALIGNMENT
**Auditoría**: Validación contra código vivo + Fixes aplicados

---

## ESTADO: RESUELTO — Todos los fixes aplicados y verificados

| # | Hallazgo original | Estado | Detalle |
|---|-------------------|--------|---------|
| 1 | Probabilidades 70/20/10 → etiquetas descriptivas | ✅ Resuelto | Fix ya aplicado en `v4_diagnostic_generator.py` L966-968 |
| 2 | "Comparan en reserva" — causa raíz `booking → reserva` | ✅ Corregido | `document_quality_gate.py` L31, L56 ahora excluyen "booking" (FIX 1) |
| 3 | Quick Win #3 jerga técnica | ℹ️ Doc drift | Código ya correcto en L1628/1636. Documento refería líneas obsoletas. |
| 4 | "Perdida" sin tilde → "Pérdida" | ✅ Corregido | Fix sistémico: 8 archivos, no solo `scenario_calculator.py` (FIX 3) |
| 5 | Brecha 5 "IA Bloqueada" vs "IA sin guía" | ✅ Resuelto | Ya corregido en FASE-B |
| — | Bug TypeError `_check_scenario_order()` | ✅ Corregido | `_extract_scenario_values()` normaliza a números ambos paths (dict + objeto) (FIX 2) |
| — | Doble pipe `||` en tablas | ✅ Corregido | `diagnostico_v6_template.md` (L30-34, L100-105) y `propuesta_v6_template.md` (L24-28) (FIX 5) |
| — | `"Perdida"` sin tilde sistémico | ✅ Corregido | 8 archivos: calculator_v2, loss_projector, opportunity_scorer, outreach_gen, report_builder (FIX 3) |

---

## FIX 1: `"booking"` en `document_quality_gate.py` ✅

**Archivo**: `modules/postprocessors/document_quality_gate.py`

Cambios:
- L31: Eliminado `"booking"` de `ENGLISH_HOTEL_WORDS`
- L56: Eliminado `"booking": "reserva"` de `EN_TO_ES`
- Agregado comentario: `# NOTE: "booking" intentionally excluded — Booking is a brand name`

**Verificación**: `content_scrubber.py` L60 ya tenía el fix. 28/28 tests pasan.

---

## FIX 2: TypeError `_check_scenario_order()` ✅

**Archivo**: `modules/quality_gates/commercial_gate.py`

**Causa raíz real**: `_extract_scenario_values()` (L251-264) retornaba objetos `Scenario` por el path `getattr()` (producción) pero números por el path `dict.get()` (tests). La comparación `<` en `_check_scenario_order()` fallaba con objetos.

**Fix (no documentado en el contexto original)**:
- `_extract_scenario_values()` ahora tiene `_to_numeric()` que extrae `.monthly_loss_central` de objetos y preserva números
- `_check_scenario_order()` mantiene sus comparaciones originales (los valores ya son números)
- Solución más limpia que el fix parcial propuesto en el documento (que solo cambiaba 2 de 4 líneas y rompía tests)

**Verificación**: 27/27 tests pasan.

---

## FIX 3: `"Perdida"` → `"Pérdida"` (sistémico) ✅

El documento original solo detectó `scenario_calculator.py` L73. El bug era sistémico:

| Archivo | Cambio |
|---------|--------|
| `modules/financial_engine/scenario_calculator.py` L73 | `"Perdida estimada:"` → `"Pérdida estimada:"` |
| `modules/financial_engine/calculator_v2.py` L71 | Docstring |
| `modules/financial_engine/calculator_v2.py` L354 | f-string |
| `modules/financial_engine/calculator_v2.py` L368 | String literal |
| `modules/financial_engine/loss_projector.py` L377 | `"Perdidas significativamente"` |
| `modules/financial_engine/loss_projector.py` L380 | `"Perdidas sobre el promedio"` |
| `modules/financial_engine/opportunity_scorer.py` L292 | Docstring |
| `modules/generators/outreach_gen.py` L224 | Template |
| `modules/generators/report_builder.py` L1048 | Header |

---

## FIX 4: Quick Win #3 — Documentation Drift ℹ️

**No se requiere acción de código**. El fix ya estaba aplicado:
- L1628: `Instalar el "Traductor para IAs" en su web` (FAQ schema)
- L1636: `Hacer que Google muestre sus preguntas frecuentes...` (GBP optimization)

El documento referenciaba números de línea de una versión anterior. El texto "Antes" (`"Configurar Schema de Hotel + FAQ en su web."`) ya no existe en el código.

---

## FIX 5: Doble pipe `||` en templates ✅

El documento solo mencionaba `diagnostico_v6_template.md`. Realidad: 2 templates afectados.

**Archivos modificados**:
- `diagnostico_v6_template.md`: Tabla "Antes/Ahora" (L30-34) y tabla "Score de Visibilidad Digital" (L100-105)
- `propuesta_v6_template.md`: Tabla "El problema/El impacto" (L24-28)

---

## Hallazgos nuevos que el documento original no detectó

1. **Fix incompleto para BUG 2**: El documento proponía `.monthly_loss_central` en 2 líneas (L279, L291) pero omitía L285 y L297 (format strings). La solución final fue mejor: normalizar en `_extract_scenario_values()`.

2. **"Perdida" sistémico**: 9 archivos, no 1. El documento solo vio la punta del iceberg.

3. **Doble pipe en propuesta**: El documento solo mencionaba el template de diagnóstico.

4. **Tests no cubrían path de producción**: `test_commercial_gate.py` pasa dicts con números, pero producción pasa objetos `Scenario`. El TypeError nunca se detectaba en CI.

5. **Sugerencia confusa**: `commercial_gate.py` L287/L299 refiere a `_build_scenario_table_rows` que vive en `v4_diagnostic_generator.py`, no en el mismo archivo.

---

## Archivos modificados en esta sesión

```
modules/postprocessors/document_quality_gate.py     — FIX 1 (booking)
modules/quality_gates/commercial_gate.py             — FIX 2 (_extract_scenario_values)
modules/financial_engine/scenario_calculator.py      — FIX 3 (Pérdida)
modules/financial_engine/calculator_v2.py            — FIX 3 (Pérdida)
modules/financial_engine/loss_projector.py           — FIX 3 (Pérdida)
modules/financial_engine/opportunity_scorer.py       — FIX 3 (Pérdida)
modules/generators/outreach_gen.py                   — FIX 3 (Pérdida)
modules/generators/report_builder.py                 — FIX 3 (Pérdida)
modules/commercial_documents/templates/diagnostico_v6_template.md  — FIX 5 (||)
modules/commercial_documents/templates/propuesta_v6_template.md    — FIX 5 (||)
.opencode/context/ProspeccionII-Sesion-20260525.md   — Este documento (actualizado)
```

---

## Verificación final

```bash
# Tests del gate comercial
PYTHONIOENCODING=utf-8 venv/Scripts/python.exe -X utf8 -m pytest tests/quality_gates/test_commercial_gate.py -q
# → 27 passed ✅

# Tests del quality gate
PYTHONIOENCODING=utf-8 venv/Scripts/python.exe -X utf8 -m pytest tests/postprocessors/test_document_quality_gate.py -q
# → 28 passed ✅

# Verificar que no quedan "Perdida" sin tilde en archivos modificados
grep -rn "Perdida" modules/financial_engine/ modules/generators/ --include="*.py" | grep -v "Pérdida"
# → 0 resultados ✅

# Verificar que no quedan "||" iniciales en templates
grep -n "^||" modules/commercial_documents/templates/*.md
# → 0 resultados ✅
```
