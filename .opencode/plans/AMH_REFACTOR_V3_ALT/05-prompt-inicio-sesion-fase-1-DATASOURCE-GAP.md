# FASE-1: DATASOURCE-GAP — Diagnosticar por que datos GBP no llegan a validated_data

**ID**: FASE-1-DATASOURCE-GAP  
**Objetivo**: Rastrear el data flow completo desde la API hasta validated_data["hotel_data"] y fixear los gaps que causan schema vacio  
**Dependencias**: Ninguna (primera fase de V3-alt)  
**Duracion estimada**: 2-3 horas  
**Costo API**: $0.00 (solo lectura de archivos locales y tests)  
**Skill**: iah-cli-phased-execution

---

## Contexto

FASE-0 (HIPOTESIS-VALIDATION de V3) determino que la causa raiz del schema vacio no es GEO-BRIDGE sino que **datos GBP no llegan a `validated_data["hotel_data"]`** en la ejecucion del 20-abr.

El codigo de `_extract_validated_fields()` (v4_asset_orchestrator.py:618-726) es correcto — extrae de `audit_result.schema.properties` y `audit_result.gbp`. El problema es que estas fuentes estan vacias o incompletas cuando:
1. Google Places API retorna 400 → audit_result.gbp tiene datos None
2. El HTML del hotel no tiene schema markup → audit_result.schema.properties esta vacio
3. Ambos fallan simultaneamente → hotel_data queda solo con {name, url, price_range}

**Data flow completo**:
```
Google Places API
  → modules/auditors/v4_comprehensive.py (GBPApiResult)
    → audit_result.gbp (lat, lng, phone, address, rating, reviews, name, website)
      → _extract_validated_fields() (linea 659-693)
        → validated_data["hotel_data"]
          → conditional_generator._generate_hotel_schema(hotel_data)
```

---

## Tareas

### T0: Pre-validar fuentes de fallback (critico antes de implementar)

Antes de agregar fallbacks, verificar que las fuentes de donde sacaremos datos REALMENTE existen para amaziliahotel.com:

```bash
# Verificar si el sitio tiene schema markup en HTML
curl -s https://amaziliahotel.com/ | grep -i "schema.org\|application/ld+json" | head -5

# Verificar si hay telefono visible en HTML
curl -s https://amaziliahotel.com/ | grep -ioE "tel[\s:]*\+?57[\s0-9]{6,}" | head -3

# Verificar si hay direccion visible
curl -s https://amaziliahotel.com/ | grep -ioE "(carrera|calle|avenida|transversal|diagonal|km)[^<]{10,80}" | head -3
```

Documentar resultados. Si las fuentes no existen, los fallbacks seran inutiles → requiere FASE-3 data rescue o FASE-4 inyeccion manual.

### T1: Rastrear GBP data flow en v4_comprehensive.py

```bash
# Verificar como se construye audit_result.gbp
grep -n 'gbp\|GBPApiResult\|places_api\|lat.*lng\|phone.*gbp' /mnt/c/Users/Jhond/Github/iah-cli/modules/auditors/v4_comprehensive.py | head -30
```

Documentar:
1. Donde se crea el objeto GBP (dataclass o dict)?
2. Que pasa si Places API falla? Hay fallback?
3. Los datos de cross_validation (phone_web, phone_gbp) se propagan a gbp?

### T2: Verificar estado de audit_result.gbp en la ejecucion del 20-abr

```bash
# Buscar audit_report.json de la ejecucion del 20-abr
ls -la /mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/amaziliahotel/audit_report.json
```

Leer el JSON y verificar:
1. `gbp.lat`, `gbp.lng` — son null o tienen valores?
2. `gbp.phone` — existe?
3. `gbp.address` — existe?
4. `schema.properties` — tiene datos o esta vacio?
5. `validation.phone_web`, `validation.phone_gbp` — existen?

### T3: Verificar si schema.properties esta vacio cuando no hay schema HTML

```bash
# Verificar como se llena schema en v4_comprehensive
grep -n 'schema.*properties\|schema_analysis\|extract_schema' /mnt/c/Users/Jhond/Github/iah-cli/modules/auditors/v4_comprehensive.py | head -20
```

Documentar:
1. Si el HTML no tiene JSON-LD schema → properties = {} o properties = None?
2. Esto causa que la linea 639 `if audit_result.schema and audit_result.schema.properties` sea False?

### T4: Agregar logging de diagnostico en _extract_validated_fields()

Agregar logs ANTES del return (linea 726) para diagnosticar que datos llegan:

```python
# DIAGNOSTIC: Log what data is available for asset generation
logger.info(f"[V4AssetOrchestrator] validated_data['hotel_data'] completeness:")
hd = validated_data.get("hotel_data", {})
for key in ["name", "telephone", "phone", "address", "latitude", "longitude", "rating", "review_count", "url", "description"]:
    val = hd.get(key)
    has_it = val is not None and val != "" and val != 0
    logger.info(f"  {key}: {'PRESENT' if has_it else 'MISSING'} ({repr(val)[:50]})")
```

### T5: Fix — Agregar fallbacks completos para datos faltantes

Basado en el diagnostico de T0-T3, agregar TODOS los fallbacks en `_extract_validated_fields()`. El contexto identifica 5 gaps; este fix los cubre todos:

**Para telephone** (si gbp.phone y schema.properties.telephone son None):
```python
# Fallback: cross_validation phone_web
if not validated_data["hotel_data"].get("telephone"):
    if audit_result and audit_result.validation:
        phone_web = getattr(audit_result.validation, 'phone_web', None)
        if phone_web:
            validated_data["hotel_data"]["telephone"] = phone_web
            validated_data["hotel_data"]["phone"] = phone_web
```

**Para geo** (si gbp.lat/lng son None):
```python
# Fallback: schema.geo (si existe en el schema original del sitio)
if not validated_data["hotel_data"].get("latitude"):
    if audit_result and audit_result.schema and audit_result.schema.properties:
        geo = audit_result.schema.properties.get("geo", {})
        if isinstance(geo, dict):
            lat = geo.get("latitude")
            lng = geo.get("longitude")
            if lat and lng:
                validated_data["hotel_data"]["latitude"] = lat
                validated_data["hotel_data"]["longitude"] = lng
```

**Para address** (si gbp.address y schema.properties.address son None):
```python
# Fallback: gbp.formatted_address o gbp.address
if not validated_data["hotel_data"].get("address"):
    if audit_result and audit_result.gbp:
        gbp_formatted = getattr(audit_result.gbp, 'formatted_address', None) or getattr(audit_result.gbp, 'address', None)
        if gbp_formatted:
            validated_data["hotel_data"]["address"] = gbp_formatted
```

**Para rating** (si gbp.rating y schema.properties.aggregateRating son None):
```python
# Fallback: gbp.rating
if not validated_data["hotel_data"].get("rating"):
    if audit_result and audit_result.gbp:
        gbp_rating = getattr(audit_result.gbp, 'rating', None)
        if gbp_rating:
            validated_data["hotel_data"]["rating"] = gbp_rating
```

**Para review_count** (si gbp.reviews y schema.properties.aggregateRating.reviewCount son None):
```python
# Fallback: gbp.user_ratings_total o gbp.reviews
if not validated_data["hotel_data"].get("review_count"):
    if audit_result and audit_result.gbp:
        gbp_reviews = getattr(audit_result.gbp, 'user_ratings_total', None) or getattr(audit_result.gbp, 'reviews', None)
        if gbp_reviews:
            validated_data["hotel_data"]["review_count"] = gbp_reviews
```

### T6: Tests >= 8 nuevos

Crear `tests/asset_generation/test_datasource_gap.py`:

1. **test_gbp_empty_fallback_to_cross_validation**: gbp=None, schema=None, pero validation.phone_web existe → telephone se propaga
2. **test_schema_empty_gbp_partial**: schema.properties vacio, gbp tiene solo lat/lng → hotel_data tiene lat/lng pero no telephone
3. **test_both_sources_empty**: Ambos vacios → hotel_data tiene solo name/url (no crashea)
4. **test_gbp_complete**: gbp tiene todos los campos → hotel_data completo
5. **test_schema_geo_fallback**: gbp sin lat/lng pero schema.properties tiene geo → se usa schema.geo
6. **test_address_fallback_gbp_formatted_address**: gbp.address vacio pero gbp.formatted_address existe → address se propaga
7. **test_rating_fallback_gbp**: gbp.rating=4.5, schema vacio → rating=4.5
8. **test_review_count_fallback_gbp**: gbp.user_ratings_total=202, schema vacio → review_count=202
9. **test_all_critical_fields_gbp_fallback**: gbp tiene phone, lat/lng, formatted_address, rating, reviews → hotel_data completo sin schema

---

## Verificacion Pre-Fase

```bash
# Verificar que los archivos a auditar existen
ls -la /mnt/c/Users/Jhond/Github/iah-cli/modules/auditors/v4_comprehensive.py
ls -la /mnt/c/Users/Jhond/Github/iah-cli/modules/asset_generation/v4_asset_orchestrator.py
ls -la /mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/amaziliahotel/audit_report.json
```

---

## Post-Ejecucion

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-1-DATASOURCE-GAP \
    --desc "Diagnosticar y fixear gap de datos GBP en _extract_validated_fields()" \
    --archivos-mod "modules/asset_generation/v4_asset_orchestrator.py,tests/asset_generation/test_datasource_gap.py" \
    --tests "5" \
    --check-manual-docs
```

---

## Criterios de Completitud

- [ ] T0 ejecutado: fuentes de fallback validadas para amaziliahotel.com
- [ ] T1-T3 ejecutados con resultados documentados
- [ ] Logging de diagnostico agregado
- [ ] Fallbacks implementados para telephone, geo, address, rating, review_count
- [ ] Tests >= 8 nuevos pasando
- [ ] Syntax check pasa
- [ ] log_phase_completion.py ejecutado
- [ ] REGISTRY.md actualizado

## Restricciones

- **NO ejecutar v4complete** — solo tests unitarios
- **NO modificar conditional_generator.py** — eso es FASE-3
- **NO modificar geo_enriched_bridge.py** — eso es FASE-2
- **NO modificar hotel_schema_enricher.py** — el enricher no es el problema
