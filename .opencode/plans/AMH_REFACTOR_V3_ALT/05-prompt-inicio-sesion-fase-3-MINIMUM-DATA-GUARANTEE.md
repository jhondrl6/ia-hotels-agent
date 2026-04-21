# FASE-3: MINIMUM-DATA-GUARANTEE — Garantizar datos minimos en hotel_schema sin importar fuentes

**ID**: FASE-3-MINIMUM-DATA-GUARANTEE  
**Objetivo**: Garantizar que conditional_generator SIEMPRE produzca un schema con datos minimos criticos, incluso cuando GBP y schema estan vacios  
**Dependencias**: FASE-1-DATASOURCE-GAP + FASE-2-BRIDGE-QUALITY-GUARD completadas  
**Duracion estimada**: 2 horas  
**Costo API**: $0.00 (solo tests)  
**Skill**: iah-cli-phased-execution

---

## Contexto

FASE-1 agrego fallbacks en `_extract_validated_fields()` para cuando GBP o schema estan vacios. Pero estos fallbacks dependen de que OTROS datos existan (cross_validation, schema.geo). Si TODAS las fuentes fallan, hotel_data queda vacio y el schema generado es inutil.

Esta fase agrega una capa final de garantia: el conditional_generator debe poder generar un schema UTIL (con nombre, URL, pais) sin importar que datos reciba, y debe penalizar el confidence score cuando faltan datos criticos.

**Campos criticos para un hotel_schema util**:
- **Obligatorios**: name, url
- **Altamente deseados**: telephone, address (al menos pais), geo
- **Deseables**: rating, review_count, description, amenities

---

## Tareas

### T1: Definir constante CRITICAL_FIELDS en conditional_generator.py

```python
# Campos que hacen un hotel_schema util vs inutil
CRITICAL_FIELDS = {
    "mandatory": ["name", "url"],      # Sin estos, el schema es basura
    "important": ["telephone", "address", "latitude", "longitude"],  # Sin estos, es mediocre
    "nice_to_have": ["rating", "review_count", "description", "amenities"]
}
```

### T2: Agregar _validate_hotel_data_completeness() en conditional_generator.py

```python
def _validate_hotel_data_completeness(self, hotel_data: Dict) -> float:
    """
    Calcula un score de completitud basado en cuantos campos criticos estan presentes.
    
    Returns:
        float: 0.0-1.0 donde 1.0 = todos los campos presentes
    """
    score = 0.0
    total_weight = 0.0
    
    # Mandatory: 40% del score
    for field in CRITICAL_FIELDS["mandatory"]:
        total_weight += 0.2
        val = hotel_data.get(field)
        if val and val != "" and val != "Hotel":
            score += 0.2
    
    # Important: 40% del score
    for field in CRITICAL_FIELDS["important"]:
        total_weight += 0.1
        val = hotel_data.get(field)
        if val is not None and val != "" and val != 0:
            score += 0.1
    
    # Nice to have: 20% del score
    for field in CRITICAL_FIELDS["nice_to_have"]:
        total_weight += 0.05
        val = hotel_data.get(field)
        if val is not None and val != "" and (not isinstance(val, (list, dict)) or len(val) > 0):
            score += 0.05
    
    return score / total_weight if total_weight > 0 else 0.0
```

### T3: Garantizar datos minimos en _generate_hotel_schema() + Data Rescue activo

Al inicio de la funcion (despues de la linea 721), agregar:

```python
# MINIMUM-DATA-GUARANTEE: Ensure basic fields exist
hotel_data.setdefault("name", "Hotel")
hotel_data.setdefault("url", "")
hotel_data.setdefault("country", "CO")
# Si no hay address, crear una minima con pais
if not hotel_data.get("address"):
    hotel_data["address"] = ""
    hotel_data.setdefault("country", "CO")
```

**Data Rescue**: Si despues de todos los fallbacks (FASE-1) hotel_data sigue vacio, intentar rescate basico de la web:

```python
# DATA RESCUE: Si faltan campos criticos, intentar extraer de la URL conocida
# Esto solo se ejecuta si los fallbacks de FASE-1 no proporcionaron datos
if not hotel_data.get("telephone") and not hotel_data.get("address"):
    logger.warning("[DataRescue] All fallbacks failed. Attempting basic web extraction.")
    # Nota: Esto requiere acceso al HTML original. Si no esta disponible,
    # marcar para inyeccion manual (FASE-4 contingency).
    hotel_data["_data_rescue_needed"] = True
```

**Importante**: El Data Rescue no es un scraper completo (costoso), sino un flag que:
1. Marca el asset como "necesita datos manuales"
2. Penaliza confidence a 0.3 (ver T4) para que no pase gates de publicacion
3. Permite que FASE-4 haga inyeccion controlada con datos conocidos

### T4: Penalizar confidence cuando faltan datos criticos

En `_generate_content()` (el metodo principal que llama a _generate_hotel_schema), agregar penalizacion de confidence:

```python
elif asset_type == "hotel_schema":
    content = self._generate_hotel_schema(hotel_data)
    # Penalizar confidence si faltan datos criticos
    completeness = self._validate_hotel_data_completeness(hotel_data)
    
    # Data rescue flag: si todos los fallbacks fallaron, confidence muy bajo
    if hotel_data.get("_data_rescue_needed"):
        confidence_score = 0.3  # Bloquea publication gates
        logger.warning(
            f"[V4Asset] hotel_schema needs data rescue. "
            f"Confidence penalized to {confidence_score}. "
            f"Run FASE-4 manual injection or verify API keys."
        )
    elif completeness < 0.3:
        # Menos del 30% de campos → confidence bajo para activar GEO-BRIDGE (que FASE-2 protege)
        confidence_score = 0.5
    elif completeness < 0.6:
        confidence_score = 0.7
    else:
        confidence_score = 0.9
```

### T5: Agregar fallback de pais Colombia en _extract_validated_fields()

Si no hay address de ninguna fuente, garantizar que al menos exista pais:

```python
# MINIMUM-DATA-GUARANTEE: Ensure country exists
if not validated_data["hotel_data"].get("country"):
    validated_data["hotel_data"]["country"] = "CO"
if not validated_data["hotel_data"].get("region") and audit_result:
    # Intentar inferir region del URL o datos disponibles
    url = getattr(audit_result, 'url', '')
    validated_data["hotel_data"]["region"] = ""  # Empty es mejor que None
```

### T6: Tests >= 4 nuevos

Agregar a `tests/asset_generation/test_conditional_generator.py`:

1. **test_hotel_schema_with_empty_data**: hotel_data={} → schema tiene name="Hotel", country="CO", no crashea
2. **test_completeness_score_full**: Todos los campos presentes → score >= 0.9
3. **test_completeness_score_empty**: Solo name y url → score ~0.3
4. **test_confidence_penalty_low_completeness**: hotel_data con solo name → confidence = 0.5
5. **test_data_rescue_flag_blocks_publication**: hotel_data con _data_rescue_needed=True → confidence = 0.3, can_use = false

---

## Verificacion Pre-Fase

```bash
ls -la /mnt/c/Users/Jhond/Github/iah-cli/modules/asset_generation/conditional_generator.py
ls -la /mnt/c/Users/Jhond/Github/iah-cli/tests/asset_generation/test_conditional_generator.py
ls -la /mnt/c/Users/Jhond/Github/iah-cli/modules/asset_generation/v4_asset_orchestrator.py
```

---

## Post-Ejecucion

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-3-MINIMUM-DATA-GUARANTEE \
    --desc "Garantizar datos minimos en hotel_schema: confidence penaliza datos faltantes" \
    --archivos-mod "modules/asset_generation/conditional_generator.py,modules/asset_generation/v4_asset_orchestrator.py,tests/asset_generation/test_conditional_generator.py" \
    --tests "4" \
    --check-manual-docs
```

---

## Criterios de Completitud

- [ ] CRITICAL_FIELDS definido
- [ ] _validate_hotel_data_completeness() implementada
- [ ] Garantia de datos minimos en _generate_hotel_schema()
- [ ] Data Rescue flag implementado (penaliza a 0.3 si fallbacks fallan)
- [ ] Penalizacion de confidence por datos faltantes
- [ ] Fallback de pais Colombia en _extract_validated_fields()
- [ ] Tests >= 4 nuevos pasando
- [ ] Tests existentes siguen pasando
- [ ] Syntax check pasa
- [ ] log_phase_completion.py ejecutado
- [ ] REGISTRY.md actualizado

## Restricciones

- **NO ejecutar v4complete** — solo tests unitarios
- **NO modificar geo_enriched_bridge.py** — ya fue modificado en FASE-2
- **NO modificar hotel_schema_enricher.py** — el enricher no es el problema
- **CUIDADO con overlap**: Esta fase modifica v4_asset_orchestrator.py que FASE-1 tambien toca. Si FASE-1 ya agrego cambios, esta fase agrega SOLO la seccion de garantia de pais
