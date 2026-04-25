# Contexto de Evaluación — FASE-TRAZABILIDAD-PATCH + FASE-SEO-SCORE

**Última actualización**: 2026-04-25
**Proyecto**: iah-cli v4.35.1
**Fase actual**: 06-fase-trazabilidad-patch+seo (por ejecutar, 1 sola ejecución v4complete)
**Fase siguiente**: 09-documentacion-post-proyecto

---

## Objetivo del contexto

Documentar el estado ANTES (baseline) y el estado DESPUÉS de la implementación
de los planes 06 y 07, para evaluar efectividad de cada fix.

---

## BASELINE — Estado tras FASE-TRAZABILIDAD-VALIDATE

**Fecha del baseline**: 2026-04-25
**Hotel de prueba**: Amazilia Hotel (https://amaziliahotel.com/)
**Comando baseline**: `./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ --nombre "Amazilia Hotel"`

### T1: BUG-02 — financial_validity gate false positive

| Atributo | Valor (ANTES) | Fuente |
|----------|--------------|--------|
| Gate status | PASSED | ✅ confirmado |
| Gate message | "All financial data validated - no default values detected" | ✅ confirmado |
| gate_report.json financial_sources | `{adr_cop: "legacy_hardcode", occupancy_rate: "default", direct_channel_percentage: "default"}` | ✅ confirmado L190-194 |
| Gate blocks publication | No (FALSE POSITIVE — Tier C con defaults dice PASSED) | ✅ confirmado |
| Gate details.default_sources | No presente | ✅ confirmado |

**Archivo evidencia**: `output/v4_complete/gate_report.json` líneas 24-30 + 190-194

### T2: Secciones faltantes en diagnóstico

| Atributo | Valor (ANTES) |
|----------|--------------|
| "Validación de Calidad" como encabezado | NO existe |
| "Trazabilidad Brechas" como encabezado | NO existe |
| Sección brechas real | "Brechas detectadas que afectan su presencia digital..." (párrafo, no sección nombrada) |
| `_build_manual_attention_table()` contenido | No verificado |

**Archivo evidencia**: `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260425_133242.md`

### T4: geo_flow_result — Timing

| Atributo | Valor (ANTES) |
|----------|--------------|
| geo_flow_result.json existe | SÍ |
| Ruta | `output/v4_complete/amazilia_hotel/v4_audit/geo_flow_result.json` |
| Fila "Salud Técnica GEO" en diagnóstico | NO (generado después del diagnóstico) |
| Causa raíz | Flujo: Diagnóstico → Propuesta → Gates → Assets (geo_flow al final) |

**Archivo evidencia**: `ls output/v4_complete/amazilia_hotel/v4_audit/` confirma existencia

### D2: seo_score ausente del JSON

| Atributo | Valor (ANTES) | Fuente |
|----------|--------------|--------|
| SEO Local en diagnóstico markdown | 25/100 ✅ | ✅ confirmado `01_DIAGNOSTICO_*.md` L52 |
| `_calculate_web_score()` existe | SÍ (L1444, usa `calcular_score_seo()`) | ✅ confirmado en código |
| `seo_score` en v4_complete_report.json | NO ❌ | ✅ confirmado grep vacío |
| `web_score` en v4_complete_report.json | NO ❌ | ✅ confirmado grep vacío |
| Template V6 resuelve `${seo_score}` | SÍ (funciona en markdown) | ✅ confirmado |

**Comando evidencia**: `grep -i "seo_score\|web_score" output/v4_complete/v4_complete_report.json` → vacío

### Estado general del readiness

| Atributo | Valor |
|----------|-------|
| Publication Readiness | READY_FOR_PUBLICATION |
| Blocking issues | 0 |
| Gates con WARNING | 2 (asset_confidence, proposal_asset_alignment) |

---

## CRITERIOS DE ÉXITO — DESPUÉS de implementación

### T1: BUG-02 — financial_validity gate

| Criterio | Esperado (DESPUÉS) |
|----------|-------------------|
| Gate status | WARNING |
| Gate passed | True |
| Gate message | Contiene "Tier C" o "default/legacy values" |
| gate_report.json details.default_sources | Presente con campos affected |
| Readiness | READY_FOR_PUBLICATION (WARNING no bloquea) |

**Test unitario**:
```bash
./venv/Scripts/python.exe -c "
from modules.quality_gates.publication_gates import PublicationGatesOrchestrator
assessment = {
    'financial_sources': {
        'adr_cop': 'legacy_hardcode',
        'occupancy_rate': 'default',
        'direct_channel_percentage': 'default'
    },
    'financial_data': {'occupancy_rate': 0.5, 'direct_channel_percentage': 0.2, 'adr_cop': 300000}
}
orch = PublicationGatesOrchestrator()
result = orch._financial_validity_gate(assessment)
print(f'Status: {result.status.value}, Passed: {result.passed}')
print(f'Message: {result.message}')
print(f'Details: {result.details}')
"
```
**Esperado**: `Status: WARNING, Passed: True, Message: contiene "Tier C" o "default"`

**Test de integración**:
```bash
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ --nombre "Amazilia Hotel"
grep -A5 '"gate_name": "financial_validity"' output/v4_complete/gate_report.json
```
**Esperado**: `status: WARNING, message: contiene "Tier C"`

---

### T2: Secciones del diagnóstico

| Criterio | Esperado (DESPUÉS) |
|----------|-------------------|
| Encabezado de brechas visible | "## 🔍 Trazabilidad de Brechas" o equivalente en markdown |
| "Validación de Calidad" | Solo si `_build_manual_attention_table()` retorna contenido |

**Test de verificación**:
```bash
grep -E "## .*[Tt]razabilidad|## .*[Bb]rechas|## .*[Vv]alid" output/v4_complete/01_DIAGNOSTICO_*.md
```
**Esperado**: Al menos un encabezado de sección relacionado con brechas/trazabilidad

---

### T4: geo_flow_result timing

| Criterio | Esperado (DESPUÉS) |
|----------|-------------------|
| Fila "Salud Técnica GEO" en diagnóstico | Verificable tras post-assets |
| geo_flow_result.json existe | SÍ (confirmado) |

**Test de verificación**:
```bash
grep "Salud Técnica GEO" output/v4_complete/01_DIAGNOSTICO_*.md
ls output/v4_complete/amazilia_hotel/v4_audit/geo_flow_result.json
```
**Nota**: El archivo ya existe. La fila en diagnóstico aparece solo si se regenera post-assets.

---

### D2: seo_score en JSON

| Criterio | Esperado (DESPUÉS) |
|----------|-------------------|
| `seo_score` o `web_score` en v4_complete_report.json | SÍ, presente |
| Valor | Numérico 0-100 |

**Test de verificación**:
```bash
grep -i "seo_score\|web_score" output/v4_complete/v4_complete_report.json
```
**Esperado**: Línea con score (ej. `"seo_score": 25` o `"web_score": "25"`)

---

## REGISTRO DE IMPLEMENTACIÓN

| Fecha | Fase | Tarea | Archivo modificado | Cambio realizado | Verificado |
|-------|------|-------|-------------------|-----------------|------------|
| 2026-04-25 | PRE-FIX | Bug output_dir | `v4_diagnostic_generator.py` | `_prepare_template_data()` ahora recibe `output_dir` | ✅ |
| 2026-04-25 | 06-PATCH+SEO | T1-BUG02 | `publication_gates.py` | PENDIENTE |
| 2026-04-25 | 06-PATCH+SEO | T2-Secciones | `v4_diagnostic_generator.py` + template V6 | PENDIENTE |
| 2026-04-25 | 06-PATCH+SEO | T3-seo_score | `main.py` | PENDIENTE (absorbido de FASE-07) |
| 2026-04-25 | 06-PATCH+SEO | T4-geo_flow | N/A (timing) | PENDIENTE |

---

## ESTADO DE EVALUACIÓN

| Tarea | Estado evaluación | Resultado |
|-------|-----------------|-----------|
| T1-BUG02 | PENDIENTE | — |
| T2-Secciones | PENDIENTE | — |
| T3-seo_score (D2) | PENDIENTE | absorbido de FASE-07 |
| T4-geo_flow | PENDIENTE | — |

**Verificación**: 1 sola ejecución v4complete al final verifica los 4 issues simultáneamente.

---

## NOTAS

- **D1 (WARNING en readiness)**: Diferida a sesión dedicada. No cambia en 06-PATCH.
- **geo_flow_result.json**: Ya se genera correctamente — solo matter de timing.
- **SEO en markdown**: Ya funciona (25/100). El fix es solo para el JSON.
- **Fix pre-ejecución**: El bug de `output_dir` ya fue corregido antes de esta evaluación.

---

## VALIDACIÓN CRUZADA vs CÓDIGO REAL (2026-04-25)

**Método**: Inspección directa de publication_gates.py, v4_diagnostic_generator.py, main.py, template V6.

### Resultado del baseline: CONFIRMADO ✓

Todos los valores del baseline coinciden con el código actual.

### Hallazgos que afectan los planes 06 y 07

#### H1: T1.1 FASE-RAIZ NO implementado (CRÍTICO)

El checklist `06-checklist-implementacion.md` marca T1.1 como `[x]` completado:
```
- [x] Modificar `_financial_validity_gate()` para pasar `sources` a NoDefaultsValidator
- [x] WARNING si mayoría (>50%) default/hardcode
- [x] BLOCKED si TODOS son default
```

Pero `grep` confirma **CERO** ocurrencias de `financial_sources`, `GateStatus.WARNING`, `DEFAULT_SOURCES`
o `Tier C` en `publication_gates.py`. El gate sigue siendo binario PASSED/BLOCKED.

**Impacto en FASE-06**: T1-BUG02 no es un "check secundario" como describe el plan.
Es la implementación COMPLETA del path WARNING + financial_sources que T1.1 debió hacer.

#### H2: `_build_manual_attention_table()` siempre retorna contenido

El plan 06 condiciona la sección "Validación de Calidad" a si `_build_manual_attention_table()`
tiene contenido. Pero SIEMPRE retorna al menos una fila (mensaje "No se detectaron problemas...").
**La sección es viable siempre.**

#### H3: Template V6 L125 ya tiene "RESUMEN DE BRECHAS"

Existe `## 📋 RESUMEN DE BRECHAS → OPORTUNIDADES` con `${brechas_resumen_section}`.
El encabezado `## 🔍 Trazabilidad` debe ir en L82 como reemplazo o antes de `${brechas_section}`.

#### H4: seo_score retorna `str`, JSON necesita `int`

`_calculate_web_score()` retorna `str(score)` (ej: "25"). Para el JSON se necesita `int()`.
El campo debe agregarse en main.py ~L2792 donde se construye el dict `report`.

### Estado actualizado del registro

| Fecha | Fase | Tarea | Hallazgo | Acción |
|-------|------|-------|----------|--------|
| 2026-04-25 | VALIDACIÓN | T1.1 RAIZ | Checklist dice [x] pero código sin cambios | Corregir checklist a [ ] |
| 2026-04-25 | VALIDACIÓN | T1-BUG02 | Scope ampliado: implementación completa, no parche | Actualizar plan 06 |
| 2026-04-25 | VALIDACIÓN | T2-Secciones | `_build_manual_attention_table()` siempre retorna contenido | Aclarar en plan 06 |
