---
description: FASE-GEO-BRIDGE — Bridge geo_enriched → delivery pipeline
version: 1.0.0
---

# FASE-GEO-BRIDGE: geo_enriched → Asset Enrichment Bridge

**ID**: FASE-GEO-BRIDGE  
**Objetivo**: Crear el bridge que conecta `geo_enriched/` (datos reales) con el pipeline de delivery de assets  
**Dependencias**: Ninguna (root cause fix)  
**Duración estimada**: 2-3 horas  
**Skill**: `iah-cli-phased-execution` + `code-review`

---

## Contexto

### Problema Central (D2 + D3 + D8 del AUDIT)

El pipeline de iah-cli tiene DOS flujos que nunca se intersectan:

1. **GEO Flow** → genera `geo_enriched/` con datos REALES (hotel_schema_rich.json, llms.txt, faq_schema.json)
2. **V4AssetOrchestrator** → genera los 10 assets de delivery con confidence_score=0.5 (PLACEHOLDERS)

**El cliente recibe**:
- `hotel_schema/ESTIMATED_hotel_schema_*.json` con `name: "Hotel"` (vacío) ❌
- `llms_txt/ESTIMATED_llms_*.txt` con `# Hotel` (placeholder) ❌

**Cuando geo_enriched/ tiene**:
- `hotel_schema_rich.json` con `name: "Amaziliahotel"` ✅
- `llms.txt` con `# Amaziliahotel` + URL real + amenities reales ✅

### Archivos Clave a Investigar

```
modules/geo_enrichment/geo_enrichment_layer.py   — genera geo_enriched/ (FOUNDATION band)
modules/asset_generation/conditional_generator.py — genera assets delivery
modules/asset_generation/v4_asset_orchestrator.py — orchestra todo
modules/asset_generation/llmstxt_generator.py     — generador llms.txt (IGNORA geo_enriched)
```

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| (ninguna - este es el primer fix) | — |

---

## Tareas

### Tarea 1: Mapear el flujo actual de generación de assets

**Objetivo**: Entender exactamente dónde y cómo se generan `hotel_schema` y `llms_txt`

**Pasos**:
1. Leer `modules/asset_generation/conditional_generator.py` líneas 100-400 (FASE-CAUSAL-01 gate + generación)
2. Leer `modules/asset_generation/v4_asset_orchestrator.py` líneas 234-350 (enrichment flow)
3. Leer `modules/geo_enrichment/geo_enrichment_layer.py` líneas 70-250 (generate method)
4. Identificar: ¿en qué momento se decide el contenido del hotel_schema? ¿de dónde viene `validated_data`?

**Entregable**: Captura del flujo con puntos exactos donde los datos se pierden

---

### Tarea 2: Crear función de enrichment bridge

**Objetivo**: Crear una función que dado un asset con confidence < 0.7, intente poblarlo desde geo_enriched/

**Ubicación nueva**: `modules/asset_generation/geo_enriched_bridge.py`

**API propuesta**:
```python
def try_enrich_from_geo_enriched(
    asset_type: str,
    current_content: str,
    geo_enriched_dir: Path,
    hotel_id: str
) -> Tuple[str, float]:
    """
    Si geo_enriched/ tiene versión enriquecida de este asset,
    usarla Y retornar confidence_score mejorado.
    
    Returns:
        (content, new_confidence_score)
    """
```

**Mapeo de assets**:
| Delivery Asset | geo_enriched Source | Confidence boost |
|---------------|---------------------|------------------|
| hotel_schema | hotel_schema_rich.json | 0.5 → 0.85 |
| llms_txt | llms.txt | 0.5 → 0.85 |
| faq_schema | faq_schema.json | 0.5 → 0.85 |

---

### Tarea 3: Integrar bridge en V4AssetOrchestrator

**Objetivo**: Ejecutar el enrichment DESPUÉS de generar y ANTES de guardar

**Punto de inyección**: `modules/asset_generation/v4_asset_orchestrator.py` línea ~270, después de `_generate_with_coherence_check` pero antes de guardar el asset

**Lógica**:
```python
# Después de generar asset
if generated_asset.confidence_score < 0.7:
    enriched_content, new_score = try_enrich_from_geo_enriched(
        generated_asset.asset_type,
        generated_asset.content,
        output_dir / "geo_enriched",
        hotel_id
    )
    if new_score > generated_asset.confidence_score:
        generated_asset.content = enriched_content
        generated_asset.confidence_score = new_score
        generated_asset.preflight_status = "PASSED"
```

---

### Tarea 4: Tests para el bridge

**Objetivo**: Tests que verifican el enrichment funciona

**Archivo**: `tests/asset_generation/test_geo_enriched_bridge.py`

**Casos de prueba**:
1. `test_bridge_enriches_hotel_schema_from_geo_enriched` — dado geo_enriched con hotel_schema_rich.json, el bridge mejora el confidence
2. `test_bridge_skips_if_no_geo_enriched_dir` — si no existe geo_enriched/, retorna contenido original
3. `test_bridge_preserves_high_confidence_assets` — si confidence >= 0.7, no modifica
4. `test_bridge_handles_missing_files_gracefully` — si falta archivo específico, usa original

---

## Restricciones

- NO modificar `modules/geo_enrichment/` — solo leer
- NO alterar la cadena financiera (cálculos de scenarios)
- Mantener backward compatibility: si geo_enriched/ no existe, el pipeline debe funcionar igual
- Tests existentes deben seguir pasando

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_bridge_enriches_hotel_schema_from_geo_enriched` | `tests/asset_generation/test_geo_enriched_bridge.py` | PASA |
| `test_bridge_skips_if_no_geo_enriched_dir` | `tests/asset_generation/test_geo_enriched_bridge.py` | PASA |
| `test_bridge_preserves_high_confidence_assets` | `tests/asset_generation/test_geo_enriched_bridge.py` | PASA |
| `test_bridge_handles_missing_files_gracefully` | `tests/asset_generation/test_geo_enriched_bridge.py` | PASA |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_geo_enriched_bridge.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Tests nuevos pasan**: Los 4 tests del bridge ejecutan exitosamente
- [ ] **Validaciones del proyecto**: `python scripts/run_all_validations.py --quick` pasa 4/4
- [ ] **`dependencias-fases.md` actualizado**: FASE-GEO-BRIDGE marcada como ✅ Completada
- [ ] **Bridge funcional**: `hotel_schema` y `llms_txt` usan datos de geo_enriched/ cuando disponible
- [ ] **Confidence mejorado**: Assets enriquecidos tienen confidence > 0.7
- [ ] **No hay regresión**: Tests existentes siguen pasando

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**: Marcar FASE-GEO-BRIDGE como ✅ Completada con fecha
2. **`06-checklist-implementacion.md`**: Marcar Tareas 1-4 como completadas
3. **`09-documentacion-post-proyecto.md`**:
   - Sección A: Agregar `modules/asset_generation/geo_enriched_bridge.py` (nuevo módulo)
   - Sección D: Actualizar métricas de confidence de assets
4. **证据/fase-geo-bridge/**: Crear directorio con evidencia (logs de tests, output del bridge)

**NO esperar a la siguiente sesión para documentar.**
