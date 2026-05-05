# FASE-SCORING-B: Extensión del breakdown a los 4 pilares

**ID**: FASE-SCORING-B
**Objetivo**: Agregar breakdowns de SEO, AEO, IAO al diagnóstico generado (además del GEO existente), usando el mismo Hotel Castilla Real para validación
**Dependencias**: SCORING-A ✅ Completada (el fix del filtrado es prerequisito para que los 4 breakdowns muestren todos los factores)
**Duración estimada**: 45-60 min
**Skill**: `iah-cli-phased-execution`

---

## Contexto

SCORING-A corrigió `_build_scoring_breakdown()` para mostrar TODOS los factores. Ahora la función es genérica y soporta `seo`, `geo`, `aeo`, `iao` como parámetro `pilar`. Pero el generator solo la invoca para GEO.

Los 4 pilares tienen checklists, calculadores y extractores implementados:
- CHECKLIST_SEO: 7 items = 100pts (ssl, schema_hotel, LCP_ok, CLS_ok, imagenes_alt, blog_activo, schema_reviews)
- CHECKLIST_GEO: 6 items = 100pts (nap_consistente, redes_activas, geo_score_gbp, fotos_gbp, horario_gbp, schema_reviews_geo)
- CHECKLIST_AEO: 6 items = 100pts (schema_faq, open_graph, schema_hotel_aeo, contenido_factual, speakable_schema, imagenes_alt_aeo)
- CHECKLIST_IAO: 7 items = 100pts (citability_score, contenido_extenso, llms_txt_exists, crawler_access, brand_signals, ga4_indirect, schema_advanced)

**Solo falta cablear** las 3 invocaciones faltantes en el generator y los 3 placeholders en el template. ~10 líneas de código total.

**Contexto validado:** `.opencode/context/scoring-transparency-context.md` (2026-05-05)

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| SCORING-A | ✅ Completada |

### Base Técnica Disponible

- `_build_scoring_breakdown(pilar, elementos)` — ya corregida en SCORING-A, genérica para 4 pilares
- `_extraer_elementos_seo(audit_result)` — L2280
- `_extraer_elementos_aeo(audit_result)` — L2345
- `_extraer_elementos_iao(audit_result)` — L2375
- `calcular_score_seo()`, `calcular_score_aeo()`, `calcular_score_iao()` — implementados
- Template `diagnostico_v6_template.md` — tiene `${geo_score_breakdown}` L60
- Test: v4complete con Hotel Castilla Real (https://www.hotelcastillareal.com/, region=eje_cafetero)

---

## Tareas

### Tarea 1: Agregar 3 asignaciones en el generator

**Objetivo**: Cablear las invocaciones de `_build_scoring_breakdown()` para SEO, AEO, IAO

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` ~L697

**Cambio exacto**:

Buscar la línea existente:
```python
'geo_score_breakdown': _build_scoring_breakdown('geo', self._extraer_elementos_geo(audit_result)),
```

Agregar debajo (manteniendo indentación):
```python
'seo_score_breakdown': _build_scoring_breakdown('seo', self._extraer_elementos_seo(audit_result)),
'aeo_score_breakdown': _build_scoring_breakdown('aeo', self._extraer_elementos_aeo(audit_result)),
'iao_score_breakdown': _build_scoring_breakdown('iao', self._extraer_elementos_iao(audit_result)),
```

**Criterios de aceptación**:
- [ ] Las 3 líneas existen en el diccionario de template data
- [ ] Cada una usa el pilar correcto y el extractor correspondiente
- [ ] Sin errores de sintaxis

### Tarea 2: Agregar 3 placeholders en el template v6

**Objetivo**: Agregar los placeholders para que el template renderice los breakdowns

**Archivos afectados**:
- `modules/commercial_documents/templates/diagnostico_v6_template.md` ~L60

**Cambio**: Después de `${geo_score_breakdown}` (o en sección de desglose), agregar:
```markdown
${seo_score_breakdown}
${aeo_score_breakdown}
${iao_score_breakdown}
```

**Nota**: Evaluar si conviene una tabla compacta de 4 pilares o líneas individuales. El contexto sugiere formato compacto para evitar ruido visual. Si el formato en línea es muy largo, usar estructura:
```markdown
| Pilar | Score | Desglose |
|-------|-------|----------|
| SEO   | XX/100 | ${seo_score_breakdown} |
| GEO   | XX/100 | ${geo_score_breakdown} |
| AEO   | XX/100 | ${aeo_score_breakdown} |
| IAO   | XX/100 | ${iao_score_breakdown} |
```

**Criterios de aceptación**:
- [ ] Los 3 placeholders existen en el template
- [ ] La ubicación es lógica (cerca de GEO, o en tabla unificada)
- [ ] Sin errores de sintaxis Jinja2

### Tarea 3: Validar con v4complete (Hotel Castilla Real)

**Objetivo**: Ejecutar v4complete y verificar los 4 breakdowns en el diagnóstico generado

**Comando**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe main.py v4complete \
    --url https://www.hotelcastillareal.com/ \
    --output output/test-scoring-transparency
```

**⚠️ CORRECCIÓN (2026-05-05):** El flag `--region` no existe en v4complete. La región se detecta automáticamente.

**Ejecutar con**: `terminal(background=true, notify_on_complete=true, timeout=600)`

**Criterios de aceptación**:
- [ ] v4complete termina sin errores
- [ ] El diagnóstico muestra breakdown de SEO (7 factores)
- [ ] El diagnóstico muestra breakdown de GEO (6 factores, con fix de SCORING-A)
- [ ] El diagnóstico muestra breakdown de AEO (6 factores)
- [ ] El diagnóstico muestra breakdown de IAO (7 factores)
- [ ] Factores TRUE con ✅, FALSE con ~~tachado~~ (herencia SCORING-A)
- [ ] Coherence score ≥ 0.80

**Verificación del output**:
```bash
grep -E "(SEO|GEO|AEO|IAO)" output/test-scoring-transparency/01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md | head -20
```

---

## Tests Obligatorios

| Test | Criterio de Éxito |
|------|-------------------|
| v4complete Hotel Castilla Real | 4 pilares con breakdown visible |
| `run_all_validations.py --quick` | 4/4 checks |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase:

1. **`dependencias-fases.md`**
   - Marcar SCORING-B como ✅ Completada

2. **`README.md` del plan**
   - Actualizar tabla de progreso

3. **`06-checklist-implementacion.md`**
   - Marcar items B1-B7

4. **`09-documentacion-post-proyecto.md`**
   - Marcar Sección E: Post-Fase SCORING-B

5. **Ejecutar log_phase_completion.py**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-SCORING-B \
    --desc "Extension del scoring breakdown a los 4 pilares (SEO, GEO, AEO, IAO)" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/templates/diagnostico_v6_template.md" \
    --tests "0" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] Generator tiene 4 asignaciones de breakdown (GEO + SEO + AEO + IAO)
- [ ] Template v6 tiene 4 placeholders
- [ ] v4complete Hotel Castilla Real: 4 breakdowns visibles en diagnóstico
- [ ] Factores TRUE/FALSE marcados correctamente (✅/~~tachado~~)
- [ ] `scoring_methodology.md` y el output alineados (4 pilares)
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `log_phase_completion.py` ejecutado
- [ ] `dependencias-fases.md` actualizado

---

## Restricciones

- NO modificar `_build_scoring_breakdown()` (ya fue corregida en SCORING-A)
- NO modificar checklists, calculadores, ni extractores
- NO agregar nuevos pilares (solo los 4 existentes)
- NO modificar `scoring_methodology.md` (ya está correcto)
- NO crear tests unitarios nuevos
- Máximo 60 iteraciones del agente
- Si agotamiento: guardar evidencia en `evidence/SCORING-B/`, actualizar checkpoint
