# Prompt de Inicio de Sesion — FASE-PATCH-1
## Fix Places API FieldMask + lat/lng Extraction (Persistencia G2)

**Fecha**: 2026-04-20
**Tipo**: PATCH (fix de persistencia, NO re-escribir FASE-1/2)
**Depende de**: FASE-1 a FASE-8 completadas
**Bloquea**: FASE-RELEASE

---

## Contexto

FASE-1 y FASE-2 se marcaron como completadas pero el v4complete E2E sigue mostrando:
- `hotel_schema` con latitude "0.0", longitude "0.0"
- Log: `No places found for lat:0.0, lng:0.0`
- GBP data REAL está disponible (geo_score=62 verified) pero las coordenadas nunca llegan al schema

**Causa raíz confirmada** (ROOT_CAUSE_ANALYSIS.md):
1. `v4_comprehensive.py:1061` — X-Goog-FieldMask NO incluye `places.location`
2. `v4_comprehensive.py:1115-1116` — PlaceData se crea con `lat=0.0, lng=0.0` HARDCODEADOS

El API de Places SÍ devuelve datos, pero el código nunca pide ni extrae las coordenadas.

---

## Objetivo

Que `hotel_schema` genere con coordenadas reales del Places API, no 0.0.

---

## Tareas

### T1: Agregar `places.location` al FieldMask

**Archivo**: `modules/auditors/v4_comprehensive.py`
**Línea**: ~1061

```python
# ACTUAL:
'X-Goog-FieldMask': 'places.id,places.displayName,places.rating,places.userRatingCount,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.photos'

# CAMBIO: Agregar ',places.location' al final
'X-Goog-FieldMask': 'places.id,places.displayName,places.rating,places.userRatingCount,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.photos,places.location'
```

### T2: Extraer lat/lng del API response en PlaceData

**Archivo**: `modules/auditors/v4_comprehensive.py`
**Líneas**: ~1103-1116

```python
# ANTES de crear PlaceData, extraer del response:
location_data = place.get('location', {})
api_lat = location_data.get('latitude', 0.0) or 0.0
api_lng = location_data.get('longitude', 0.0) or 0.0

# En PlaceData:
lat=api_lat,  # NO hardcodear 0.0
lng=api_lng,  # NO hardcodear 0.0
```

### T3: Harden _is_valid_colombia_coords para rechazar 0.0

**Archivo**: `modules/asset_generation/conditional_generator.py`
**Línea**: ~709-716

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

Nota: cambiar `0 <=` a `0 <` para excluir 0.0 del rango válido.

---

## Verificación

### V1: Tests de regresión
```bash
./venv/Scripts/python.exe -m pytest tests/auditors/ tests/asset_generation/ -v --tb=short
```

### V2: Grep verification
```bash
# FieldMask debe incluir places.location
grep 'places.location' modules/auditors/v4_comprehensive.py

# No debe haber lat=0.0 hardcodeado en PlaceData
grep 'lat=0.0' modules/auditors/v4_comprehensive.py  # debe dar 0 matches

# _is_valid_colombia_coords debe rechazar 0.0
grep 'lat_f == 0.0' modules/asset_generation/conditional_generator.py
```

### V3: Syntax check
```bash
./venv/Scripts/python.exe -m py_compile modules/auditors/v4_comprehensive.py
./venv/Scripts/python.exe -m py_compile modules/asset_generation/conditional_generator.py
```

---

## Restricciones

- NO ejecutar v4complete (eso es FASE-RELEASE)
- NO modificar main.py (eso es FASE-PATCH-2)
- NO modificar v4_proposal_generator.py (eso es FASE-PATCH-3)
- SOLO tocar: `v4_comprehensive.py` y `conditional_generator.py`

---

## Criterios de Completitud

- [ ] FieldMask incluye `places.location`
- [ ] PlaceData usa lat/lng del API response (no hardcodeado)
- [ ] `_is_valid_colombia_coords` rechaza (0,0)
- [ ] Tests de regresión pasan
- [ ] Syntax checks pasan
- [ ] Grep verification confirma cambios
