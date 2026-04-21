# Root Cause Analysis — 3 Persistencias AMH_REFACTOR_V2

## PERSISTENCIA 1 — SCRUBBER BYPASS EN PROPUESTA (G14)

### Síntoma
5x "COP COP" en proposal, log muestra "[SKIP] Proposal document not available for scrubbing"

### Código involucrado

**main.py:2271-2274** — proposal_path se inicializa como None:
```python
# FIX-D7: Proposal generation moved to AFTER assets (see L2361+)
proposal_path = None
proposal_doc = None
```

**main.py:2277-2346** — FASE 3.6 ejecuta ContentScrubber, pero proposal_path sigue siendo None:
```python
# FASE 3.6: Content Scrubber + Document Quality Gate (FASE-B)
scrubber = ContentScrubber()

# Scrub diagnostic document  ← SÍ funciona, diagnostic_path ya existe
if diagnostic_path and Path(diagnostic_path).exists():
    ...

# Scrub proposal document  ← FALLA porque proposal_path = None
if proposal_path and Path(proposal_path).exists():  # FALSE → SKIPPED
    ...
else:
    print("   [SKIP] Proposal document not available for scrubbing")  # ESTO SE EJECUTA
```

**main.py:2463-2476** — La propuesta se genera DESPUÉS del scrubber (FASE 5):
```python
# Esto ocurre ~150 líneas después del scrubber
proposal_gen = V4ProposalGenerator()
proposal_path = proposal_gen.generate(...)  # Aquí se crea el archivo
```

**modules/postprocessors/content_scrubber.py:161-169** — La regla COP COP funciona correctamente:
```python
def _fix_duplicate_currency(self, content: str, fixes: List[str]) -> str:
    def replace_currency(m):
        fixes.append('Moneda: "COP COP" -> "COP"')
        return "COP"
    content = re.sub(r'\bCOP\s+COP\b', replace_currency, content, flags=re.IGNORECASE)
    return content
```

### Flujo de datos real vs esperado

**Esperado**: Generar propuesta → Scrub propuesta → Entregar
**Real**: Scrub propuesta (path=None, SKIP) → Generar propuesta (con COP COP) → Entregar

La causa raíz es un "chicken-and-egg" creado por FIX-D7 que movió la generación de propuesta DESPUÉS de los assets, pero FASE 3.6 (scrubber) se quedó ANTES de la generación.

### Fix propuesto

**Opción A (mínimo, recomendado)**: Re-scrub la propuesta después de generarla.

Agregar después de main.py:2476 (donde se asigna proposal_path):
```python
# Re-scrub proposal now that it exists
if proposal_path and Path(proposal_path).exists():
    try:
        with open(proposal_path, 'r', encoding='utf-8') as f:
            prop_content = f.read()
        prop_scrub = scrubber.scrub(prop_content, hotel_data, "propuesta")
        if prop_scrub.fix_count > 0:
            print(f"   [SCRUB] Proposal (post-gen): {prop_scrub.fix_count} fix(es) applied")
            with open(proposal_path, 'w', encoding='utf-8') as f:
                f.write(prop_scrub.scrubbed)
    except Exception as e:
        print(f"   [WARN] Post-gen scrub failed: {e}")
```

**Opción B**: Mover FASE 3.6 (scrub de propuesta) a después de la generación. Separar scrub de diagnóstico (que sí funciona) del scrub de propuesta.

---

## PERSISTENCIA 2 — HOTEL_SCHEMA CON LAT:0.0 (G2)

### Síntoma
hotel_schema genera con campos vacíos, log "No places found for lat:0.0, lng:0.0"
GBP data real: place_id ChIJY8v6vep7OI4RdD22tR3SLRk, name "Amazilia Hotel Campestre", geo_score=62

### Código involucrado

**modules/auditors/v4_comprehensive.py:1061** — FieldMask NO incluye places.location:
```python
headers = {
    'Content-Type': 'application/json',
    'X-Goog-Api-Key': api_key,
    'X-Goog-FieldMask': 'places.id,places.displayName,places.rating,places.userRatingCount,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.photos'
    # FALTA: places.location
}
```

**modules/auditors/v4_comprehensive.py:1103-1116** — PlaceData se crea con lat/lng HARDCODEADOS a 0.0:
```python
place_data = PlaceData(
    place_id=place_id,
    name=name,
    ...
    lat=0.0,   # ← HARDCODED, nunca extrae del API response
    lng=0.0,   # ← HARDCODED
    ...
)
```

**modules/auditors/v4_comprehensive.py:777-795** — GBPApiResult hereda lat=0.0 de PlaceData:
```python
return GBPApiResult(
    ...
    lat=places_result.lat,   # ← 0.0 desde PlaceData
    lng=places_result.lng,   # ← 0.0 desde PlaceData
    ...
)
```

**modules/asset_generation/v4_asset_orchestrator.py:661-666** — _extract_validated_fields rechaza coords 0,0:
```python
gbp_lat = getattr(gbp, 'lat', 0.0) or 0.0  # → 0.0
gbp_lng = getattr(gbp, 'lng', 0.0) or 0.0  # → 0.0
if 0 <= gbp_lat <= 13 and -82 <= gbp_lng <= -66:
    # 0.0 está en rango [0,13] PERO el problema es que 0.0 es un valor inválido
    # NOTA: setdefault solo setea si la key no existe
    validated_data["hotel_data"].setdefault("latitude", gbp_lat)  # setea 0.0
    validated_data["hotel_data"].setdefault("longitude", gbp_lng) # setea 0.0
```

Wait — 0.0 SÍ pasa la validación `0 <= 0.0 <= 13`. El problema real es que 0.0 es un valor sin sentido (está en el océano Atlántico, no en Colombia).

**modules/asset_generation/conditional_generator.py:709-716** — _is_valid_colombia_coords acepta 0.0:
```python
def _is_valid_colombia_coords(self, lat, lng) -> bool:
    lat_f = float(lat) if lat else 0.0
    lng_f = float(lng) if lng else 0.0
    return 0 <= lat_f <= 13 and -82 <= lng_f <= -66  # 0.0 pasa!
```

**modules/asset_generation/conditional_generator.py:750-754** — Schema genera geo con coords 0.0:
```python
"geo": {
    "@type": "GeoCoordinates",
    "latitude": str(hotel_data.get("latitude")),    # "0.0"
    "longitude": str(hotel_data.get("longitude"))    # "0.0"
} if self._is_valid_colombia_coords(hotel_data.get("latitude"), hotel_data.get("longitude")) else None,
```

### Flujo de datos real vs esperado

**Esperado**: Places API → lat/lng reales → hotel_schema con geo válido
**Real**: Places API (sin places.location en FieldMask) → lat=0.0, lng=0.0 → hotel_schema con geo "0.0"/"0.0" (válido pero inútil)

### Fix propuesto

**Fix en modules/auditors/v4_comprehensive.py** — 2 cambios:

1. Línea 1061: Agregar `places.location` al FieldMask:
```python
'X-Goog-FieldMask': 'places.id,places.displayName,places.rating,places.userRatingCount,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.photos,places.location'
```

2. Líneas 1115-1116: Extraer lat/lng del API response en vez de hardcodear:
```python
# Parse location from API response
location_data = place.get('location', {})
api_lat = location_data.get('latitude', 0.0) or 0.0
api_lng = location_data.get('longitude', 0.0) or 0.0

place_data = PlaceData(
    ...
    lat=api_lat,   # ← del API
    lng=api_lng,   # ← del API
    ...
)
```

**Fix adicional en conditional_generator.py** — Rechazar 0.0 como coordenada válida:
```python
def _is_valid_colombia_coords(self, lat, lng) -> bool:
    try:
        lat_f = float(lat) if lat else 0.0
        lng_f = float(lng) if lng else 0.0
        if lat_f == 0.0 and lng_f == 0.0:
            return False  # 0,0 no es coordenada válida
        return 0 < lat_f <= 13 and -82 <= lng_f <= -66
    except (ValueError, TypeError):
        return False
```

---

## PERSISTENCIA 3 — REGION LOWERCASE EN AUDIT_REPORT (G13)

### Síntoma
audit_report.json muestra region "eje_cafetero" en lowercase

### Código involucrado

**main.py:2929-2942** — _detect_region_from_url retorna lowercase snake_case:
```python
def _detect_region_from_url(url: str) -> str:
    url_lower = url.lower()
    if any(x in url_lower for x in ['visperas', 'salento', 'armenia', 'quindio', ...
          'pereira', 'risaralda', 'manizales', 'caldas', 'amazilia']):
        return 'eje_cafetero'  # ← LOWERCASE
    ...
    return 'nacional'
```

**main.py:1494** — Region se usa como variable interna:
```python
region = _detect_region_from_url(args.url)  # "eje_cafetero"
```

**main.py:2734-2738** — v4_complete_report.json recibe region lowercase directamente:
```python
report = {
    'v4_complete': True,
    'hotel_name': hotel_name,
    'url': args.url,
    'region': region,  # ← "eje_cafetero" SIN capitalizar
    ...
}
```

**main.py:2538** — assessment dict también recibe region lowercase:
```python
assessment["hotel_data"] = {"region": region} if region else {}  # "eje_cafetero"
```

**modules/commercial_documents/v4_proposal_generator.py:456** — El fix .title() existe SOLO para proposal:
```python
hotel_region = (region or "Colombia").replace("_", " ").title()  # "Eje Cafetero"
```

**⚠️ IMPORTANTE**: NO cambiar el valor interno de `region` porque `feature_flags.py:48` tiene:
```python
validated_regions: tuple = ("eje_cafetero", "antioquia")
```
Y `should_use_regional_for(region)` en línea 128 hace `region in self.validated_regions` — un match exacto de string. Cambiar a "Eje Cafetero" rompería la regional ADR resolution.

### Flujo de datos real vs esperado

**Esperado**: region = "Eje Cafetero" (Title Case) en todos los outputs
**Real**: region = "eje_cafetero" (snake_case lowercase) en audit_report y como variable interna; solo se capitaliza en proposal_generator

### Fix propuesto

**Fix mínimo en main.py:2738** — Aplicar .title() solo en el punto de serialización del reporte:
```python
'region': region.replace("_", " ").title() if region else region,
```

**Fix adicional en main.py:2538** — Aplicar .title() en el assessment dict (publication gates):
```python
assessment["hotel_data"] = {"region": region.replace("_", " ").title()} if region else {}
```

**Fix adicional en main.py:2289** — Aplicar .title() en hotel_data para ContentScrubber:
```python
if region:
    hotel_data["region"] = region.replace("_", " ").title()
```

**NO cambiar**: `_detect_region_from_url`, `_infer_region_from_address`, `validated_regions`, `should_use_regional_for` — estos DEBEN permanecer en lowercase snake_case para que los lookup keys internos funcionen.

**Impacto**: Cambios mínimos (3 líneas), solo afectan output de usuario. Toda la lógica interna sigue usando lowercase.
