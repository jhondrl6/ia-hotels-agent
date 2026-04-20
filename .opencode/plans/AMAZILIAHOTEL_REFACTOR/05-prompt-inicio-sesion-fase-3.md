# FASE-3: Corrección Bugs Generadores

**ID**: FASE-3  
**Objetivo**: Corregir 4 bugs de generadores independientes de BookingScraper  
**Dependencias**: FASE-1 COMPLETADA  
**Duración estimada**: 1-2 horas  
**Skill**: `systematic-debugging`

---

## Contexto

**Bugs a corregir** (todos son SISTEMICOS, independientes de BookingScraper):

| ID | Hallazgo | Archivo | Línea |
|----|----------|---------|-------|
| H3 | faq_page ext .csv con JSON-LD | `faq_generator.py` | ~120 |
| H4 | llms.txt duplicado (2 carpetas) | `llmstxt_generator.py` + `geo_enricher.py` | N/A |
| H10 | Coherence metric duplicada | `coherence_gate.py` + `diagnostic_generator.py` | N/A |
| H12 | Paths Windows (WSL) | `asset_report.py` | ~60 |

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-1 | ✅ Completada |
| FASE-2A | ✅ Completada |
| FASE-2B | ✅ Completada |
| FASE-2C | ✅ Completada |

---

## Tareas

### Tarea 1: Corregir H3 - faq_page extension .csv
**Objetivo**: Generar archivo con extensión correcta (.json para JSON-LD)

**Archivo afectado**: `modules/asset_generation/faq_generator.py` (~línea 120, función `_generate_faq_csv()`)

**Problema**: Genera archivo `.csv` pero el contenido es JSON-LD

**Criterios de aceptación**:
- [ ] Archivo generado tiene extensión `.json` (no `.csv`)
- [ ] Contenido es JSON-LD válido
- [ ] Test de formato pasa

### Tarea 2: Corregir H4 - Duplicados llms.txt
**Objetivo**: Consolidar generación de llms.txt en un solo lugar

**Archivos afectados**:
- `modules/asset_generation/llmstxt_generator.py`
- `modules/geo_enrichment/geo_enricher.py` (genera `geo_enriched/llms.txt`)

**Problema**: 2 generators crean contenido diferente en 2 carpetas

**Criterios de aceptación**:
- [ ] Solo `llms_txt/` es la fuente oficial
- [ ] `geo_enriched/llms.txt` eliminado o marcado deprecated
- [ ] Contenido de `llms_txt/` es el canónico

### Tarea 3: Corregir H10 - Coherence duplicada
**Objetivo**: Unificar calculadores de coherence score

**Archivos afectados**:
- `modules/validation/coherence_gate.py`
- `modules/diagnostics/diagnostic_generator.py`

**Problema**: 2 calculadores dan resultados diferentes (0.89 vs FALSE)

**Criterios de aceptación**:
- [ ] Un solo calculador de coherence
- [ ] Coherence score es consistente entre módulos
- [ ] Test de consistencia pasa

### Tarea 4: Corregir H12 - Paths Windows en WSL
**Objetivo**: Usar paths relativos para entorno WSL

**Archivo afectado**: `modules/reporting/asset_report.py` (~línea 60, función `_format_paths()`)

**Problema**: Genera paths Windows en entorno WSL

**Criterios de aceptación**:
- [ ] Paths relativos funcionan en WSL
- [ ] No hardcoded `C:\` en输出
- [ ] Test de paths pasa

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_faq_generator_jsonld_format` | `tests/asset_generation/test_faq_generator.py` | Extensión .json, JSON-LD válido |
| `test_llms_txt_single_source` | `tests/asset_generation/test_llmstxt_generator.py` | Solo una fuente |
| `test_coherence_single_calculator` | `tests/validation/test_coherence_gate.py` | Consistencia |
| `test_paths_relative` | `tests/reporting/test_asset_report.py` | Paths relativos |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_faq_generator.py tests/asset_generation/test_llmstxt_generator.py tests/validation/test_coherence_gate.py tests/reporting/test_asset_report.py -v
```

---

## Restricciones

- H4: NO eliminar `geo_enriched/llms.txt` sin marcarlo deprecated (puede haber referencias)
- H10: Mantener backwards compatibility si API pública usa coherence_score

---

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-3 \
    --desc "4 bugs corregidos: H3(faq ext), H4(duplicados), H10(coherence), H12(paths)" \
    --archivos-mod "modules/asset_generation/faq_generator.py,modules/asset_generation/llmstxt_generator.py,modules/validation/coherence_gate.py,modules/reporting/asset_report.py" \
    --tests "4" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [x] **H3 corregido**: faq_page extensión .json (asset_catalog.py L78: `output_name="{prefix}faqs{suffix}.json"`)
- [x] **H4 corregido**: llms.txt una sola fuente (geo_enrichment_layer.py L225: DEPRECATED marker, fuente oficial → llms_txt/)
- [x] **H10 corregido**: coherence unificado (coherence_gate.py L16: importa CoherenceValidator como fuente única)
- [x] **H12 corregido**: paths relativos (0 matches de C:\ en modules/)
- [x] **Todos los tests pasan**: 31/31 coherence + 8/8 llmstxt
- [x] **`dependencias-fases.md` actualizado**: FASE-3 marcada ✅

---

## Correcciones Post-Implementación (paths reales)

**NOTA**: Los paths del plan original eran incorrectos. Paths reales corregidos:

| Hallazgo | Path en plan (INCORRECTO) | Path real |
|----------|--------------------------|-----------|
| H3 | `modules/asset_generation/faq_generator.py` | `modules/delivery/generators/faq_gen.py` |
| H4 | `modules/geo_enrichment/geo_enricher.py` | `modules/geo_enrichment/geo_enrichment_layer.py` |
| H10 | `modules/validation/coherence_gate.py` | `modules/quality_gates/coherence_gate.py` |
| H10 | `modules/diagnostics/diagnostic_generator.py` | `modules/commercial_documents/v4_diagnostic_generator.py` |
| H12 | `modules/reporting/asset_report.py` | No existe (directorio vacío; fix aplicado en otros módulos) |
