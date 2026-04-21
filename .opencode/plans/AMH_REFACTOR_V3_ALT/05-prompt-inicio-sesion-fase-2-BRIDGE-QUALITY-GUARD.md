# FASE-2: BRIDGE-QUALITY-GUARD — GEO-BRIDGE solo reemplaza si el reemplazo es mejor

**ID**: FASE-2-BRIDGE-QUALITY-GUARD  
**Objetivo**: Agregar verificacion de calidad en GEO-BRIDGE para que nunca reemplace un schema con uno peor  
**Dependencias**: FASE-1-DATASOURCE-GAP completada  
**Duracion estimada**: 1.5-2 horas  
**Costo API**: $0.00 (solo tests)  
**Skill**: iah-cli-phased-execution

---

## Contexto

FASE-0 demostro que GEO-BRIDGE tiene un bug latente: si el conditional_generator produce un schema con confidence < 0.7, GEO-BRIDGE lo reemplaza con `hotel_schema_rich.json` del enricher. Pero el enricher genera `@type: "Hotel"` sin datos GBP, mientras que el conditional_generator genera `@type: "LodgingBusiness"` que es mas correcto para Google Rich Results.

**Bug actual en geo_enriched_bridge.py**:
```python
# Linea 72-78: Solo verifica confidence, NO verifica calidad del contenido
if current_confidence >= CONFIDENCE_THRESHOLD:
    return current_content, current_confidence

# Linea 87-126: Lee el archivo y lo retorna sin comparar campos
geo_filename, boosted_confidence = ASSET_ENRICHMENT_MAP[asset_type]
# ... lee enriched_content ...
return enriched_content, boosted_confidence  # ← RETORNA SIN VALIDAR
```

**Resultado**: Si el enricher schema tiene MENOS campos que el original, GEO-BRIDGE lo reemplaza de todos modos. Esto degrada activamente el resultado.

---

## Tareas

### T1: Definir _is_better_schema() en geo_enriched_bridge.py

Agregar funcion auxiliar que compara dos schemas JSON campo por campo:

```python
def _is_better_schema(replacement_content: str, current_content: str) -> bool:
    """
    Verifica si el schema de reemplazo es objetivamente mejor que el actual.
    
    Retorna True solo si el reemplazo tiene:
    1. Al menos la misma cantidad de campos con datos reales
    2. No pierde campos criticos (telephone, address, geo)
    3. No cambia @type de LodgingBusiness a Hotel (LodgingBusiness es preferido)
    """
    try:
        replacement = json.loads(replacement_content)
        current = json.loads(current_content)
    except (json.JSONDecodeError, TypeError):
        return False
    
    # Obtener el objeto principal del @graph
    rep_obj = replacement.get("@graph", [replacement])[0] if isinstance(replacement.get("@graph"), list) else replacement
    cur_obj = current.get("@graph", [current])[0] if isinstance(current.get("@graph"), list) else current
    
    # Verificar: NO cambiar de LodgingBusiness a Hotel
    cur_type = cur_obj.get("@type", "")
    rep_type = rep_obj.get("@type", "")
    if cur_type == "LodgingBusiness" and rep_type == "Hotel":
        logger.info("[GEO-Bridge] Rejecting: LodgingBusiness -> Hotel is a degradation")
        return False
    
    # Contar campos con datos reales
    critical_fields = ["telephone", "address", "geo", "aggregateRating", "description"]
    cur_count = sum(1 for f in critical_fields if cur_obj.get(f) is not None and cur_obj.get(f) != "")
    rep_count = sum(1 for f in critical_fields if rep_obj.get(f) is not None and rep_obj.get(f) != "")
    
    if rep_count < cur_count:
        logger.info(f"[GEO-Bridge] Rejecting: {rep_count} fields vs {cur_count} fields current")
        return False
    
    return True
```

### T2: Integrar quality check en try_enrich_from_geo_enriched()

Modificar la funcion principal para verificar calidad antes de retornar:

Despues de leer el enriched_content (linea ~108), agregar:
```python
# Quality gate: solo reemplazar si es objetivamente mejor
if asset_type == "hotel_schema" and current_content:
    if not _is_better_schema(enriched_content, current_content):
        logger.info(
            f"[GEO-Bridge] Quality gate REJECTED enrichment for {asset_type}: "
            f"replacement is not better than current"
        )
        return current_content, current_confidence
```

### T3: Agregar verificacion de campos faltantes

Si el reemplazo pierde campos criticos que el original tenia, loguear advertencia detallada:

```python
# Log detallado de campos perdidos
lost_fields = []
for field in critical_fields:
    if cur_obj.get(field) and not rep_obj.get(field):
        lost_fields.append(field)
if lost_fields:
    logger.warning(f"[GEO-Bridge] Would lose fields: {lost_fields}")
```

### T4: Agregar metrica de enriquecimiento

Agregar logging del resultado del quality gate para trazabilidad:

```python
logger.info(
    f"[GEO-Bridge] Quality gate result for {asset_type}: "
    f"{'ACCEPTED' if is_better else 'REJECTED'} "
    f"(current: {cur_count} fields, replacement: {rep_count} fields)"
)
```

### T5: Tests >= 5 nuevos

Agregar a `tests/asset_generation/test_geo_enriched_bridge.py`:

1. **test_bridge_rejects_hotel_replacing_lodgingbusiness**: Current=LodgingBusiness con datos, replacement=Hotel sin datos → NO reemplaza
2. **test_bridge_accepts_better_schema**: Current=Hotel sin datos, replacement=LodgingBusiness con datos → SI reemplaza
3. **test_bridge_rejects_fewer_fields**: Current tiene 4 campos criticos, replacement tiene 2 → NO reemplaza
4. **test_bridge_accepts_equal_fields**: Ambos tienen 4 campos → SI reemplaza
5. **test_bridge_handles_invalid_json**: JSON invalido → retorna original sin crashear

---

## Verificacion Pre-Fase

```bash
ls -la /mnt/c/Users/Jhond/Github/iah-cli/modules/asset_generation/geo_enriched_bridge.py
ls -la /mnt/c/Users/Jhond/Github/iah-cli/tests/asset_generation/test_geo_enriched_bridge.py
```

---

## Post-Ejecucion

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-2-BRIDGE-QUALITY-GUARD \
    --desc "Quality gate en GEO-BRIDGE: solo reemplaza si el schema es objetivamente mejor" \
    --archivos-mod "modules/asset_generation/geo_enriched_bridge.py,tests/asset_generation/test_geo_enriched_bridge.py" \
    --tests "5" \
    --check-manual-docs
```

---

## Criterios de Completitud

- [ ] _is_better_schema() implementada
- [ ] Quality gate integrado en try_enrich_from_geo_enriched()
- [ ] Logging detallado de aceptacion/rechazo
- [ ] Tests >= 5 nuevos pasando
- [ ] Tests existentes siguen pasando
- [ ] Syntax check pasa
- [ ] log_phase_completion.py ejecutado
- [ ] REGISTRY.md actualizado

## Restricciones

- **NO ejecutar v4complete** — solo tests unitarios
- **NO modificar conditional_generator.py** — eso es FASE-3
- **NO modificar v4_asset_orchestrator.py** — ya fue modificado en FASE-1
- **NO modificar hotel_schema_enricher.py** — el enricher no es el problema
