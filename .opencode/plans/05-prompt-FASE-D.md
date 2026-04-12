# FASE-D: Package & Template Alignment — 4 Pilares en Diagnóstico, Propuesta, Gap Analyzer y Report Builder

**ID**: FASE-D
**Objetivo**: Alinear toda la cadena de generación (diagnóstico → propuesta → assets → reportes) para que use el modelo de 4 pilares de forma consistente. Actualizar paquetes comerciales, gap analyzer, opportunity scorer, templates y report builder.
**Dependencias**: FASE-C completada (4 scores funcionando)
**Duración estimada**: 3-4 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

### Estado post-FASE-A/B/C
- 4 scores funcionando: SEO, GEO, AEO, IAO (cada uno 0-100)
- score_global calculado como promedio ponderado
- AEOSnippetTracker y LLMMentionChecker integrados en v4audit
- Templates reciben variables iao_score, aeo_score, etc.

### La cadena que necesita alineación

```
V4AuditResult (4 scores)
    │
    ├──→ v4_diagnostic_generator.py → _prepare_template_data()
    │         │
    │         ├──→ diagnostico_v6_template.md (Score de Visibilidad)
    │         ├──→ report_builder.py (ANALISIS 4-PILARES)
    │         └──→ DiagnosticSummary → v4_proposal_generator.py
    │                                      │
    │                                      ├──→ propuesta_v6_template.md
    │                                      └──→ score_tecnico → sugerir_paquete()
    │
    ├──→ gap_analyzer.py → 2 gaps (geo + aeo) → NECESITA 4 gaps
    │
    ├──→ opportunity_scorer.py → brechas → NECESITA alinear con 4 pilares
    │
    └──→ benchmarks.py / update_benchmarks.py → 3 scores → NECESITA 4 scores
```

### Archivos comerciales actuales

**Paquetes en benchmarks.py** (`paquetes_servicios_v23`):
- Starter GEO, Pro AEO, Pro AEO Plus, Elite, Elite PLUS
- "Pro AEO" → centrado en schema/FAQ
- "Elite" → incluye IAO (nombre legacy)

**Gap analyzer** (gap_analyzer.py L283-335):
- Solo calcula `gap_geo` y `gap_aeo` (2 gaps)
- Usa `geo_score_ref` y `aeo_score_ref` (solo 2 benchmarks)

**Report builder** (report_builder.py L962):
- Dice "ANALISIS 4-PILARES" pero solo muestra GEO y AEO (no SEO/IAO como scores)

**Template diagnóstico** (diagnostico_v6_template.md L52-55):
- Muestra 4 filas: GEO, Competitive, AEO, SEO
- NO muestra IAO → necesita fila IAO

**Template propuesta** (propuesta_v6_template.md L47-50):
- YA muestra 4 servicios correctos (GEO, IAO, AEO, SEO)
- NO necesita cambios en contenido

---

## Tareas

### Tarea 1: Actualizar gap_analyzer.py a 4 gaps

**Objetivo**: Expandir de 2 gaps (geo + aeo) a 4 gaps (seo + geo + aeo + iao).

**Archivos afectados**:
- `modules/analyzers/gap_analyzer.py`

**Cambios**:
```python
# ANTES (L283-335):
geo_benchmark = region_data.get('geo_score_ref', 42)
aeo_benchmark = region_data.get('aeo_score_ref', 18)
gap_geo = max(0, geo_benchmark - gbp_score)
gap_aeo = max(0, aeo_benchmark - aeo_score)
suma_gaps = gap_geo + gap_aeo

# DESPUÉS:
seo_benchmark = region_data.get('seo_score_ref', 50)
geo_benchmark = region_data.get('geo_score_ref', 42)
aeo_benchmark = region_data.get('aeo_score_ref', 18)
iao_benchmark = region_data.get('iao_score_ref', 15)  # NUEVO

gap_seo = max(0, seo_benchmark - seo_score)
gap_geo = max(0, geo_benchmark - gbp_score)
gap_aeo = max(0, aeo_benchmark - aeo_score)
gap_iao = max(0, iao_benchmark - iao_score)  # NUEVO
suma_gaps = gap_seo + gap_geo + gap_aeo + gap_iao

# Ponderación proporcional por pilar
if suma_gaps > 0:
    peso_seo = gap_seo / suma_gaps
    peso_geo = gap_geo / suma_gaps
    peso_aeo = gap_aeo / suma_gaps
    peso_iao = gap_iao / suma_gaps
```

**Criterios de aceptación**:
- [ ] 4 gaps calculados (seo, geo, aeo, iao)
- [ ] Ponderación proporcional actualizada
- [ ] `_map_brecha_to_paquete()` actualizado para mapear a 4 pilares
- [ ] Tests existentes pasan

### Tarea 2: Actualizar opportunity_scorer.py

**Objetivo**: Añadir nuevas brechas específicas de IAO y SEO al scorer.

**Archivos afectados**:
- `modules/financial_engine/opportunity_scorer.py`

**Nuevas brechas a añadir**:
```python
# IAO brechas
"no_llms_txt": {
    "description": "Sin archivo llms.txt para crawlers de IA",
    ...
},
"ia_crawler_blocked": {
    "description": "robots.txt bloquea crawlers de IA",
    ...
},
"weak_brand_signals": {
    "description": "Sin identidad digital consolidada (SameAs, social links)",
    ...
},

# SEO brechas  
"no_meta_descriptions": {
    "description": "Meta descriptions faltantes o genéricas",
    ...
},
"poor_heading_structure": {
    "description": "Estructura de headings no optimizada",
    ...
},
```

**Criterios de aceptación**:
- [ ] Nuevas brechas IAO añadidas con severity/effort/impact scores
- [ ] `score_from_assessment()` detecta las nuevas brechas
- [ ] Tests existentes pasan

### Tarea 3: Actualizar benchmarks.py y update_benchmarks.py

**Objetivo**: Expandir de 3 scores a 4 scores en benchmarks regionales.

**Archivos afectados**:
- `modules/utils/benchmarks.py`
- `scripts/update_benchmarks.py`

**Cambios en update_benchmarks.py**:
```python
# ANTES (L110-117):
geo_scores = [calculate_geo_score(h) for h in hotels]
aeo_scores = [calculate_aeo_score(h) for h in hotels]
seo_scores = [calculate_seo_score(h) for h in hotels]

# DESPUÉS:
geo_scores = [calculate_geo_score(h) for h in hotels]
aeo_scores = [calculate_aeo_score(h) for h in hotels]
seo_scores = [calculate_seo_score(h) for h in hotels]
iao_scores = [calculate_iao_score(h) for h in hotels]  # NUEVO

return {
    "geo_avg": round(sum(geo_scores) / len(geo_scores)),
    "aeo_avg": round(sum(aeo_scores) / len(aeo_scores)),
    "seo_avg": round(sum(seo_scores) / len(seo_scores)),
    "iao_avg": round(sum(iao_scores) / len(iao_scores)),  # NUEVO
}

# ANTES (L163-169): 
regiones[region_name]["geo_score_ref"] = avg["geo_avg"]
regiones[region_name]["aeo_score_ref"] = avg["aeo_avg"]
regiones[region_name]["seo_score_ref"] = avg["seo_avg"]

# DESPUÉS:
regiones[region_name]["geo_score_ref"] = avg["geo_avg"]
regiones[region_name]["aeo_score_ref"] = avg["aeo_avg"]
regiones[region_name]["seo_score_ref"] = avg["seo_avg"]
regiones[region_name]["iao_score_ref"] = avg["iao_avg"]  # NUEVO
```

**Nueva función**:
```python
def calculate_iao_score(hotel: Dict[str, Any]) -> int:
    """IAO score basado en proxies disponibles."""
    score = 0
    if hotel.get("has_llms_txt"): score += 20
    if hotel.get("has_schema_entity"): score += 20
    if hotel.get("citability_score", 0) > 50: score += 20
    if hotel.get("allows_ai_crawlers"): score += 20
    if hotel.get("has_sames_as_links"): score += 20
    return min(100, score)
```

**Cambios en benchmarks.py**:
- Añadir `iao_score_ref` a los defaults regionales
- Actualizar `get_regional_data()` para incluir IAO

**Criterios de aceptación**:
- [ ] `calculate_iao_score()` implementada en update_benchmarks.py
- [ ] Benchmarks regionales incluyen `iao_score_ref`
- [ ] `get_regional_data()` retorna 4 benchmarks

### Tarea 4: Actualizar report_builder.py — Sección 4-Pilares (LEGADO, mínimo)

**NOTA IMPORTANTE**: `report_builder.py` es código legado del comando `spark` (DEPRECADO).
El pipeline activo `v4complete` usa `V4DiagnosticGenerator` + `V4ProposalGenerator`.
Este archivo NO afecta la salida real de v4complete.

**Objetivo**: Añadir comentario DEPRECATED al inicio y actualizar la sección 4-Pilares para consistencia
(si alguien lee este archivo, no debe ver una estructura contradictoria con el pipeline activo).

**Archivos afectados**:
- `modules/generators/report_builder.py`

**Cambios**:
1. Añadir al inicio del archivo (después de imports):
```python
# ⚠️ DEPRECATED: Este módulo pertenece al comando 'spark' (deprecado).
# El pipeline activo 'v4complete' usa V4DiagnosticGenerator + V4ProposalGenerator
# en modules/commercial_documents/. No modificar este archivo para cambios funcionales.
```

2. En la sección "ANALISIS 4-PILARES" (L962), actualizar para incluir IAO:
```python
# ANTES: Solo muestra PILAR 1 (GEO) y PILAR 2 (AEO)
# DESPUÉS: Mostrar los 4 pilares

## [TARGET] ANALISIS 4-PILARES (SEO + GEO + AEO + IAO)

### [MAP] PILAR 1: SEO (Para que te ENCUENTREN)
**Score SEO: {seo_score}/100**
[tabla con métricas SEO]

### [MAP] PILAR 2: GEO (Para que te UBICQUEN)
**Score GEO: {gbp_data.get('score', 0)}/100**
[tabla existente con métricas GEO]

### [DOC] PILAR 3: AEO (Para que te CITEN)
**Score AEO: {schema_data.get('score_schema', 0)}/100**
[tabla existente con métricas AEO]

### [IA] PILAR 4: IAO (Para que te RECOMIENDEN)
**Score IAO: {iao_score}/100**
[tabla con métricas IAO: citability, llms.txt, crawler access, menciones LLM]

---
**Score Global de Visibilidad Digital: {score_global}/100**
```

**Criterios de aceptación**:
- [ ] 4 pilares mostrados con score y métricas
- [ ] Score global visible
- [ ] Paquete sugerido usa score_global
- [ ] Progresión SEO→AEO→IAO con advertencia si scores están invertidos

### Tarea 5: Actualizar diagnostico_v6_template.md

**Objetivo**: Añadir fila IAO a la tabla de Score de Visibilidad Digital.

**Archivos afectados**:
- `modules/commercial_documents/templates/diagnostico_v6_template.md`

**Cambios**:
```markdown
<!-- ANTES (L52-55): -->
| **Google Maps** (GEO) | ${geo_score}/100 | ${geo_regional_avg}/100 | ${geo_status} |
| **Posición Competitiva Local** (vs cercanos) | ${competitive_score}/100 | ... |
| **AEO** - Infraestructura para IAs | ${aeo_score}/100 | ... |
| **SEO Local** (Web) | ${seo_score}/100 | ... |

<!-- DESPUÉS: -->
| **SEO Local** (Para que te ENCUENTREN) | ${seo_score}/100 | ${seo_regional_avg}/100 | ${seo_status} |
| **Google Maps** (Para que te UBICQUEN) | ${geo_score}/100 | ${geo_regional_avg}/100 | ${geo_status} |
| **AEO** (Para que te CITEN) | ${aeo_score}/100 | ${aeo_regional_avg}/100 | ${aeo_status} |
| **IAO** (Para que te RECOMIENDEN) | ${iao_score}/100 | ${iao_regional_avg}/100 | ${iao_status} |
| **Visibilidad Digital** (Global) | ${score_global}/100 | — | ${score_global_status} |
```

**Criterios de aceptación**:
- [ ] Fila IAO añadida con etiquetas correctas
- [ ] Score global añadido como resumen
- [ ] Labels alineados con la narrativa comercial ("Para que te ENCUENTREN/CITEN/UBICQUEN/RECOMIENDEN")
- [ ] Fila "Posición Competitiva Local" se mantiene como métrica adicional (no es un pilar, es un sub-score de GEO)

### Tarea 6: Actualizar v4_diagnostic_generator.py — _get_regional_benchmarks()

**Objetivo**: Añadir IAO benchmark al retorno.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (L1249-1263)

**Cambios**:
```python
# ANTES:
return {
    'geo_score_ref': region_data.get('geo_score_ref', 55),
    'aeo_score_ref': region_data.get('aeo_score_ref', 20),
    'seo_score_ref': region_data.get('seo_score_ref', 50),
}

# DESPUÉS:
return {
    'geo_score_ref': region_data.get('geo_score_ref', 55),
    'aeo_score_ref': region_data.get('aeo_score_ref', 20),
    'seo_score_ref': region_data.get('seo_score_ref', 50),
    'iao_score_ref': region_data.get('iao_score_ref', 15),
}
```

Y añadir cálculo de `iao_regional` en `_prepare_template_data()`.

**Criterios de aceptación**:
- [ ] `_get_regional_benchmarks()` retorna 4 benchmarks
- [ ] `iao_regional_avg` inyectado en template data
- [ ] Default IAO benchmark = 15 (realista: la mayoría de hoteles no tienen IAO)

### Tarea 7: Actualizar v4_proposal_generator.py — score_tecnico → score_global

**Objetivo**: Migrar la propuesta de usar `score_tecnico` (CHECKLIST_IAO) a `score_global` (4 pilares).

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py` (L697-778)

**Cambios**:
```python
# ANTES (L700):
score = diagnostic_summary.score_tecnico if diagnostic_summary.score_tecnico is not None else 50

# DESPUÉS:
score = diagnostic_summary.score_global if diagnostic_summary.score_global is not None else (
    diagnostic_summary.score_tecnico if diagnostic_summary.score_tecnico is not None else 50
)

# ANTES (L748):
score_tecnico = diagnostic_summary.score_tecnico if diagnostic_summary.score_tecnico is not None else "N/A"

# DESPUÉS:
score_global = diagnostic_summary.score_global if diagnostic_summary.score_global is not None else (
    diagnostic_summary.score_tecnico if diagnostic_summary.score_tecnico is not None else "N/A"
)
```

**Criterios de aceptación**:
- [ ] `score_global` es la métrica principal (fallback a score_tecnico)
- [ ] Template variable `score_tecnico` se mantiene como alias por compatibilidad
- [ ] `sugerir_paquete()` usa score_global

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Gap analyzer 4 gaps | `tests/test_audit_alignment.py` | Calcula 4 gaps correctamente |
| Opportunity scorer IAO | `tests/financial_engine/test_opportunity_scorer.py` | Nuevas brechas detectadas |
| Benchmarks 4 scores | `tests/test_benchmarks.py` | 4 scores calculados |
| Report builder 4 pilares | `tests/generators/test_report_builder.py` | Muestra 4 pilares |
| Proposal score global | `tests/commercial_documents/test_proposal.py` | Usa score_global |
| Suite completa | — | 390+ tests, 0 regresiones |

**Comandos de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/ -x --tb=short
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** → Marcar FASE-D como completada
2. **`06-checklist-implementacion.md`** → Marcar items de FASE-D
3. **Ejecutar**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-D \
    --desc "Package & Template Alignment: 4 pilares en diagnóstico, propuesta, gap analyzer, report builder" \
    --archivos-mod "modules/analyzers/gap_analyzer.py,modules/financial_engine/opportunity_scorer.py,modules/utils/benchmarks.py,modules/generators/report_builder.py,modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/v4_proposal_generator.py,scripts/update_benchmarks.py" \
    --archivos-nuevos "modules/commercial_documents/templates/diagnostico_v6_template.md" \
    --tests "395" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] gap_analyzer.py calcula 4 gaps (seo, geo, aeo, iao)
- [ ] opportunity_scorer.py tiene brechas IAO/SEO nuevas
- [ ] benchmarks.py / update_benchmarks.py manejan 4 scores
- [ ] report_builder.py muestra 4 pilares completos + score global
- [ ] diagnostico_v6_template.md tiene fila IAO + score global
- [ ] v4_proposal_generator.py usa score_global como métrica principal
- [ ] _get_regional_benchmarks() retorna 4 benchmarks con IAO
- [ ] Suite completa pasa (0 regresiones)
- [ ] log_phase_completion.py ejecutado

---

## Restricciones

- propuesta_v6_template.md NO se modifica (ya correcto con 4 servicios)
- NO cambiar precios de paquetes (solo nombres y alineación)
- NO crear nuevos assets (solo alinear existentes)
- NO eliminar score_tecnico (mantener como alias backward compat)
- Los paquetes existentes (Starter GEO, Pro AEO, etc.) se mantienen por ahora — solo se actualiza su composición interna
- Python: `./venv/Scripts/python.exe`
- Working directory: `/mnt/c/Users/Jhond/Github/iah-cli`
