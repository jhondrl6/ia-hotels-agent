# FASE-2: Cerrar gaps Pain→Asset — PainSolutionMapper + clave duplicada (MAYOR COMPLEJIDAD)

**ID**: ASSET-ALIGNMENT-FASE-2
**Objetivo**: Cerrar los gaps que impiden que `optimization_guide` y `open_graph` se planifiquen y generen, eliminando también la clave duplicada en conditional_generator.py.
**Dependencias**: FASE-1 completada
**Duración estimada**: 2-3 horas
**Skill**: `iah-cli-phased-execution` + `iah-cli-execution-conventions`
**delegate_task**: ✅ SUBAGENTE — spec completa con código ANTES/DESPUÉS del contexto (§3.1, §3.2, §9.5).

---

## Contexto

Esta es la **fase de mayor complejidad técnica** del plan. Cierra la desconexión entre la propuesta
comercial (que promete servicios) y el pipeline Pain→Asset (que planifica y genera los assets).

### Problema 3.1: optimization_guide nunca se planifica

El asset `optimization_guide` (para SEO Local) SÍ existe en el catálogo y SÍ tiene generador,
pero el PainSolutionMapper no lo planifica porque ningún pain detectado lo mapea.

Los pains que SÍ lo mapean no se activaron en la ejecución de Zi One Luxury:
- `poor_performance` → requiere `core_web_vitals`, `mobile_score` → performance API devolvió ERROR
- `metadata_defaults` → requiere `default_title`, `default_description` → hotel no tiene metadatos por defecto
- `low_citability` → requiere `citability_score < 50` → citability = 56.13 (> 50)

**El score SEO Local del hotel es 25/100** (promedio regional: 59/100) — el diagnóstico SÍ detecta
que está bajo, pero no hay un pain type `low_seo_score` en PainSolutionMapper.

### Problema 3.2: open_graph no se activa con OG tags existentes

El pain `no_og_tags` SÍ existe en PAIN_SOLUTION_MAP (L245-253), pero `detect_pains()` (L523-533)
solo lo activa cuando `seo_elements.open_graph == False`. Zi One Luxury ya tiene 8 OG tags
(og:locale, og:type, og:title, og:description, og:url, og:site_name, og:image), así que
`open_graph: True` y el pain nunca entra al ledger.

La propuesta SIEMPRE promete "Meta Tags Sociales (Open Graph)" como servicio, pero el pipeline
solo lo genera cuando NO hay OG tags. Necesita un modo "enhance_existing".

### Problema 9.5: Clave duplicada en PAIN_TO_ASSET

`conditional_generator.py:250-251`:
```python
"whatsapp_conflict": "whatsapp_button",                        # L250 — SOBREESCRITO
"whatsapp_conflict": ["whatsapp_button", "whatsapp_conflict_guide"],  # L251 — sobrevive
```
Solo la segunda entrada sobrevive. No rompe la generación actual pero es fragil.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-1 | ✅ Completada |

### Base Técnica Disponible

- Archivos a modificar:
  - `modules/commercial_documents/pain_solution_mapper.py` (PAIN_SOLUTION_MAP + detect_pains)
  - `modules/asset_generation/conditional_generator.py` (L250-251)
  - `modules/asset_generation/asset_catalog.py` (verificar promised_by consistency)
- Tests base: `tests/test_pain_solution_mapper.py` (si existe), `tests/asset_generation/`

---

## Tareas

### Tarea 1: Agregar pain `low_seo_score` → optimization_guide

**Objetivo**: Crear un nuevo pain type en PainSolutionMapper que se active cuando el score SEO Local
del hotel esté significativamente bajo, mapeando a `optimization_guide`.

**Archivos afectados**:
- `modules/commercial_documents/pain_solution_mapper.py`

**Especificación del nuevo pain**:

```python
"low_seo_score": {
    "assets": ["optimization_guide"],
    "confidence_required": 0.0,
    "priority": 2,
    "validation_fields": ["seo_local_score"],
    "estimated_impact": "high",
    "name": "SEO Local Bajo",
    "description": "El score de SEO Local está significativamente por debajo del promedio regional"
},
```

**Trigger en detect_pains()**: Activar cuando `seo_local_score < 40` (configurable).
En la ejecución de Zi One Luxury: SEO Local = 25/100 → SÍ se activaría.

**Verificar**: Que `seo_local_score` esté disponible como validation_field en el audit_report.
Si el campo se llama diferente en el audit (ej: `seo_score`, `local_seo_score`), usar el nombre correcto.

**Criterios de aceptación**:
- [ ] Pain `low_seo_score` existe en PAIN_SOLUTION_MAP
- [ ] `detect_pains()` activa el pain cuando `seo_local_score < 40`
- [ ] El pain mapea a `["optimization_guide"]`
- [ ] `asset_catalog.py` entry para `optimization_guide` incluye `low_seo_score` en `promised_by`
- [ ] Test: mock audit con seo_local_score=25 → pain se activa → asset se planifica

### Tarea 2: Modificar detección de `no_og_tags` — modo enhance_existing

**Objetivo**: Hacer que el pain `no_og_tags` se active también cuando el sitio YA tiene OG tags
pero estos son mejorables, no solo cuando están ausentes.

**Archivos afectados**:
- `modules/commercial_documents/pain_solution_mapper.py`

**Lógica actual** (L523-533):
```python
if not seo_elements.open_graph:
    ledger.append(PainLedgerEntry(
        pain_id="no_og_tags",
        ...
    ))
```

**Fix requerido**: Cambiar la condición para evaluar si los OG tags son completos/mejorables.
Una heurística simple: si `open_graph == True` pero faltan tags importantes (og:image:alt,
og:locale:alternate, twitter:card), activar el pain con `confidence` reducida.

**Opción simple (recomendada para esta fase)**: Activar el pain siempre que la propuesta prometa
"Meta Tags Sociales (Open Graph)" Y el asset no esté ya generado. La lógica sería:
```python
# Si no hay OG tags → pain con confidence alta
if not seo_elements.open_graph:
    ledger.append(PainLedgerEntry(pain_id="no_og_tags", confidence=0.9, ...))
# Si hay OG tags pero el servicio se promete → pain con confidence media (enhance_existing)
elif seo_elements.open_graph and self._og_tags_incomplete(seo_elements):
    ledger.append(PainLedgerEntry(pain_id="no_og_tags", confidence=0.5, ...))
```

**`_og_tags_incomplete`**: Método helper que verifica si faltan tags importantes.
Por ahora, retornar True siempre que haya menos de 10 OG tags (Zi One tiene 8 < 10 → True).
El umbral puede refinarse después.

**Criterios de aceptación**:
- [ ] `no_og_tags` se activa cuando `open_graph == False` (comportamiento existente)
- [ ] `no_og_tags` se activa cuando `open_graph == True` pero tags incompletos (nuevo)
- [ ] El pain tiene `confidence` diferenciada (alta sin OG, media con OG incompletos)
- [ ] `open_graph` asset se planifica en ambos casos
- [ ] Test: mock audit con open_graph=True y 8 tags → pain se activa con confidence=0.5

### Tarea 3: Eliminar clave duplicada en conditional_generator.py

**Objetivo**: Eliminar la entrada duplicada en PAIN_TO_ASSET (L250-251), manteniendo la versión
que mapea a lista (que es la que sobrevive y la que usa `generate_for_faltantes`).

**Archivos afectados**:
- `modules/asset_generation/conditional_generator.py`

**Código actual** (L250-251):
```python
"whatsapp_conflict": "whatsapp_button",                        # L250 — SOBREESCRITO
"whatsapp_conflict": ["whatsapp_button", "whatsapp_conflict_guide"],  # L251 — sobrevive
```

**Fix**: Eliminar L250 (la entrada string). Mantener L251 (la entrada lista).

**Verificar**: Que ningún consumidor de PAIN_TO_ASSET espere un string para `whatsapp_conflict`.
Si hay consumidores que hacen `isinstance(value, str)`, ajustarlos para manejar listas.

**Criterios de aceptación**:
- [ ] Solo una entrada `whatsapp_conflict` en PAIN_TO_ASSET (mapea a lista)
- [ ] No hay consumidores que rompan con el cambio (grep de `whatsapp_conflict` en el código)
- [ ] Tests de asset generation pasan

### Tarea 4: Extender OpenGraphGenerator con modo enhance_existing (Gap 3.2b)

**Objetivo**: Modificar el generador OpenGraphGenerator para que, cuando el sitio ya tenga OG
tags, genere solo los tags FALTANTES (no duplique los existentes). Esto cierra el gap detectado
en la revisión del plan: el detector de pains (Tarea 2) activa el pain, pero el generador
producía tags desde cero sin conocer los existentes.

**Archivos afectados**:
- `modules/asset_generation/open_graph_generator.py`
- `modules/asset_generation/conditional_generator.py` (pasar existing_tags al generador)

**Estado actual del generador** (open_graph_generator.py:231-338):
```python
def _generate_html(self, og_data: HotelOGData) -> str:
    lines = [
        f'<meta property="og:type" content="hotel" />',
        f'<meta property="og:title" content="{og_data.hotel_name}" />',
        f'<meta property="og:description" content="{description}" />',
        # ... todos los tags desde cero
    ]
```

**Fix requerido**:

1. `OpenGraphGenerator.generate_content()` aceptar parámetro opcional `existing_og_tags: list[str]`
   (lista de propiedades OG ya presentes en el sitio, ej: `["og:locale", "og:type", "og:title", ...]`)

2. `_generate_html()` filtrar: si `og:type` ya está en `existing_og_tags`, NO generarlo.
   Si `og:image:alt` NO está, generarlo. Si `twitter:card` NO está, generarlo.

3. Si todos los tags importantes ya están presentes, retornar un HTML con nota explicativa:
   ```html
   <!-- Open Graph Tags ya presentes en el sitio (8 tags detectados) -->
   <!-- Tags adicionales recomendados: og:image:alt, twitter:card -->
   <!-- Generated by IA Hoteles Agent - enhance_existing mode -->
   ```

4. En `conditional_generator.py` L528-534: pasar los tags existentes del audit report
   al generador:
   ```python
   elif asset_type == "open_graph":
       from .open_graph_generator import OpenGraphGenerator
       generator = OpenGraphGenerator()
       hotel_data = validated_data.get("hotel_data", validated_data)
       hotel_dict = getattr(hotel_data, 'value', hotel_data) if not isinstance(hotel_data, dict) else hotel_data
       # NUEVO: pasar OG tags existentes del audit
       existing_og_tags = validated_data.get("existing_og_tags", [])
       content = generator.generate_content(
           hotel_dict if isinstance(hotel_dict, dict) else {},
           existing_og_tags=existing_og_tags if isinstance(existing_og_tags, list) else []
       )
   ```

5. Verificar que el audit report incluye la lista de OG tags detectados.
   Si el campo se llama `seo_elements.og_tags_list` o similar, usar ese nombre.
   Si no existe el campo, hacer fallback a lista vacía (comportamiento actual: genera desde cero).

**Criterios de aceptación**:
- [ ] `generate_content()` acepta `existing_og_tags` parámetro opcional (default=[])
- [ ] Tags en `existing_og_tags` NO se duplican en el HTML output
- [ ] Tags faltantes (que no están en `existing_og_tags`) SÍ se generan
- [ ] Si todos los tags importantes están presentes, genera nota HTML explicativa (no archivo vacío)
- [ ] `conditional_generator.py` L528-534 pasa `existing_og_tags` del audit al generador
- [ ] Test: mock con existing_og_tags=["og:type","og:title","og:url"] → HTML no incluye esos 3 tags
- [ ] Test: mock sin existing_og_tags (default) → HTML incluye todos los tags (regresión: comportamiento original)

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_pain_solution_mapper.py` | `tests/commercial_documents/test_pain_solution_mapper.py` | Todos pasan + N nuevos |
| `test_conditional_generator.py` | `tests/asset_generation/test_conditional_generator.py` | Todos pasan |
| `test_open_graph_generator.py` | `tests/asset_generation/test_open_graph_generator.py` | Todos pasan + 2 nuevos (enhance_existing) |
| `test_proposal_asset_alignment.py` | `tests/quality_gates/test_proposal_asset_alignment.py` | 24/24 pasan |
| `test_asset_catalog.py` | `tests/asset_generation/test_asset_catalog.py` | Si existe, pasa |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_pain_solution_mapper.py tests/asset_generation/test_conditional_generator.py tests/asset_generation/test_open_graph_generator.py tests/quality_gates/test_proposal_asset_alignment.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: Marcar FASE-2 como ✅ Completada.
2. **`README.md` del plan**: Actualizar tabla de progreso.
3. **`09-documentacion-post-proyecto.md`**:
   - **Sección B**: Agregar funcionalidad nueva (low_seo_score pain, enhance_existing OG mode, clave duplicada fix)
   - **Sección D**: Métricas (tests count, files modified)
   - **Sección E**: Archivos afiliados (pain_solution_mapper.py, conditional_generator.py, asset_catalog.py)
4. **`evidence/fase-2/`**: Guardar diffs.
5. **log_phase_completion.py**:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   ./venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-2-ASSET-ALIGNMENT \
       --desc "Gaps Pain→Asset: low_seo_score pain + no_og_tags enhance_existing + OpenGraphGenerator enhance_existing mode + clave duplicada fix" \
       --archivos-mod "modules/commercial_documents/pain_solution_mapper.py,modules/asset_generation/conditional_generator.py,modules/asset_generation/asset_catalog.py,modules/asset_generation/open_graph_generator.py" \
       --tests "5" \
       --check-manual-docs
   ```
6. **CHANGELOG.md y GUIA_TECNICA.md**: Editar con cambios.

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] Pain `low_seo_score` existe en PAIN_SOLUTION_MAP con trigger `seo_local_score < 40`
- [ ] `detect_pains()` activa `low_seo_score` cuando aplica
- [ ] `optimization_guide` en `assets` de `low_seo_score`
- [ ] `asset_catalog.py` entry `optimization_guide` incluye `low_seo_score` en `promised_by`
- [ ] `no_og_tags` se activa con `open_graph=True` e tags incompletos (confidence=0.5)
- [ ] `no_og_tags` sigue activándose con `open_graph=False` (regresión: confidence=0.9)
- [ ] `open_graph` asset se planifica en ambos casos
- [ ] `_og_tags_incomplete()` helper implementado
- [ ] OpenGraphGenerator.generate_content() acepta `existing_og_tags` (default=[])
- [ ] Tags en `existing_og_tags` NO se duplican en el HTML output
- [ ] Tags faltantes SÍ se generan
- [ ] `conditional_generator.py` L528 pasa `existing_og_tags` del audit al generador
- [ ] Test: enhance_existing con 3 tags existentes → HTML no los duplica
- [ ] Test: sin existing_og_tags → HTML incluye todos (regresión)
- [ ] Clave duplicada en conditional_generator.py:250 eliminada
- [ ] Tests nuevos pasan (5+)
- [ ] Tests existentes sin regresión
- [ ] `run_all_validations.py --quick` pasa
- [ ] `dependencias-fases.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado
- [ ] CHANGELOG.md + GUIA_TECNICA.md editados
- [ ] `evidence/fase-2/` con diffs

---

## Restricciones

- **Máximo 60 iteraciones del agente por fase**
- **No ejecutar v4complete** (reservado para FASE-5)
- **No modificar** `publication_gates.py` (Gate 9 funciona correctamente)
- **No modificar** `v4_proposal_generator.py` (eso es FASE-3)
- **No modificar ROADMAP.md**
- **No cambiar el umbral de citability** (50) — eso es un cambio de calibración, no de este plan
- **No cambiar la lógica de `poor_performance`** — el problema es API key, no lógica

---

## Prompt de Ejecución (delegate_task subagente)

```
Actúa como especialista en Python con conocimiento del proyecto iah-cli.

OBJETIVO: Cerrar los gaps Pain→Asset en PainSolutionMapper + eliminar clave duplicada en conditional_generator.py. Esta es la fase de mayor complejidad técnica del plan.

CONTEXTO:
- Proyecto: /mnt/c/Users/Jhond/Github/iah-cli
- Python: ./venv/Scripts/python.exe (Windows venv desde WSL)
- Versión actual: 4.62.0 (post-FASE-1)
- Problema 1: PainSolutionMapper no tiene pain `low_seo_score` → optimization_guide nunca se planifica. El hotel Zi One Luxury tiene SEO Local = 25/100 (promedio regional 59/100).
- Problema 2: Pain `no_og_tags` (pain_solution_mapper.py:245-253) solo se activa cuando seo_elements.open_graph == False. El sitio YA tiene 8 OG tags → pain nunca se activa → open_graph nunca se planifica. Necesita modo "enhance_existing".
- Problema 3: conditional_generator.py:250-251 tiene clave duplicada "whatsapp_conflict" — la primera entrada (string) se sobrescribe por la segunda (lista).

TAREAS:
1. En pain_solution_mapper.py: agregar pain "low_seo_score" a PAIN_SOLUTION_MAP:
   - assets: ["optimization_guide"]
   - validation_fields: ["seo_local_score"]
   - trigger: seo_local_score < 40
   - priority: 2, estimated_impact: "high"
   - confidence_required: 0.0
2. En pain_solution_mapper.py detect_pains(): activar "low_seo_score" cuando seo_local_score < 40
3. En pain_solution_mapper.py: modificar detección de "no_og_tags":
   - Si open_graph == False: activar pain con confidence=0.9 (comportamiento existente)
   - Si open_graph == True pero tags incompletos (< 10): activar pain con confidence=0.5 (NUEVO)
   - Implementar helper _og_tags_incomplete(seo_elements) que retorne True si < 10 OG tags
4. En asset_catalog.py: verificar que optimization_guide.promised_by incluye "low_seo_score"
5. En conditional_generator.py:250-251: eliminar L250 (string), mantener L251 (lista)
6. Verificar que ningún consumidor de PAIN_TO_ASSET espere string para whatsapp_conflict
7. En open_graph_generator.py: modificar generate_content() para aceptar parámetro opcional existing_og_tags: list[str] (default=[])
   - _generate_html(): filtrar tags que ya están en existing_og_tags (no duplicarlos)
   - Si todos los tags importantes están presentes, generar nota HTML explicativa
8. En conditional_generator.py L528-534: pasar existing_og_tags del audit report al generador
   - Verificar qué campo del audit report contiene la lista de OG tags detectados
   - Si no existe el campo, fallback a lista vacía (comportamiento actual)
9. Escribir 5 tests nuevos:
   - test_low_seo_score: mock audit con seo_local_score=25 → pain se activa → optimization_guide se planifica
   - test_no_og_tags_enhance: mock audit con open_graph=True y 8 tags → pain se activa con confidence=0.5
   - test_no_duplicate_key: PAIN_TO_ASSET["whatsapp_conflict"] es lista, no string
   - test_og_enhance_existing: generate_content con existing_og_tags=["og:type","og:title","og:url"] → HTML no incluye esos 3
   - test_og_no_existing: generate_content sin existing_og_tags → HTML incluye todos (regresión)
10. Ejecutar tests: ./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_pain_solution_mapper.py tests/asset_generation/test_conditional_generator.py tests/asset_generation/test_open_graph_generator.py tests/quality_gates/test_proposal_asset_alignment.py -v
11. Ejecutar: ./venv/Scripts/python.exe scripts/run_all_validations.py --quick

CRITERIOS:
- Pain low_seo_score existe y se activa con seo_local_score < 40
- Pain no_og_tags se activa en modo enhance_existing (open_graph=True, tags < 10)
- OpenGraphGenerator NO duplica tags existentes, genera solo los faltantes
- Clave duplicada eliminada; PAIN_TO_ASSET["whatsapp_conflict"] es lista
- asset_catalog optimization_guide.promised_by incluye low_seo_score
- Tests nuevos pasan (5), existentes sin regresión
- run_all_validations.py --quick pasa

VALIDACIONES:
- grep "low_seo_score" modules/commercial_documents/pain_solution_mapper.py (debe existir)
- grep "_og_tags_incomplete" modules/commercial_documents/pain_solution_mapper.py (debe existir)
- grep "existing_og_tags" modules/asset_generation/open_graph_generator.py (debe existir)
- grep -c "whatsapp_conflict" modules/asset_generation/conditional_generator.py (debe ser 1, no 2)
- pytest tests/commercial_documents/ tests/asset_generation/ tests/quality_gates/test_proposal_asset_alignment.py -v
```
