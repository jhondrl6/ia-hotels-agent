# Causa Raiz Real — AMH_REFACTOR_V3_ALT

**Fecha**: 2026-04-21
**Sesion**: FASE-0 HIPOTESIS-VALIDATION (V3)

---

## Hipotesis V3 (RECHAZADA)

V3 decia: GEO-BRIDGE reemplaza schema bueno (LodgingBusiness + datos GBP) con schema malo del enricher (Hotel sin datos).

## Realidad (verificada con codigo)

GEO-BRIDGE **no fue la causa directa** porque el threshold es 0.7 y el schema final tiene 0.85.

La causa raiz es que **datos GBP no llegaron a validated_data["hotel_data"]** en la ejecucion del 20-abr.

---

## Evidencia Forense

### Schema 15-abr (BUENO)
- Archivo: `output/v4_complete/amaziliahotel/hotel_schema/ESTIMATED_hotel_schema_20260415_113915.json`
- @type: "LodgingBusiness"
- Tiene: telephone (+57 310 4019049), address (completo), geo (4.8133, -75.6961), aggregateRating (4.5/202), description, speakable
- Confidence: 0.95, can_use: true
- source_data_hash: "amaziliahotel_v2_real_data"
- diagnostic_reference: "FASE-2A"

### Schema 20-abr (MALO)
- Archivo: `output/v4_complete/amaziliahotel/hotel_schema/ESTIMATED_hotel_schema_20260420_220114.json`
- @type: "Hotel"
- SIN: telephone, address, geo, aggregateRating, description, speakable
- Confidence: 0.85, can_use: false
- source_data_hash: "50ed899df51e56b9" (hash generico)
- diagnostic_reference: "None"

### hotel_schema_rich.json (enricher)
- Archivo: `output/v4_complete/amaziliahotel/geo_enriched/hotel_schema_rich.json`
- IDENTICO al schema 20-abr en contenido (solo difiere en \r\n vs \n)
- @type: "Hotel", SIN datos GBP

### Codigo: _extract_validated_fields() (v4_asset_orchestrator.py:618-726)
- Extrae de audit_result.schema.properties (linea 639-656)
- Extrae de audit_result.gbp (linea 659-693) con getattr() y validacion Colombia
- Usa setdefault() para lat/lng, if-not-get para phone/address/rating
- **El codigo esta correcto** — el problema es que LOS DATOS NO LLEGAN

### Codigo: conditional_generator._generate_hotel_schema() (linea 721-781)
- Genera "@type": "LodgingBusiness" (correcto)
- Lee phone de hotel_data.get("phone") o .get("telephone")
- Lee geo con validacion Colombia
- Lee rating/review_count
- **El codigo esta correcto** — genera buen schema SI recibe buenos datos

### Codigo: GEO-BRIDGE (geo_enriched_bridge.py:47-126)
- Threshold: 0.7 (CONFIDENCE_THRESHOLD)
- Si confidence >= 0.7 → no hace nada
- Si confidence < 0.7 → lee hotel_schema_rich.json del enricher
- **No verifica calidad del reemplazo** — bug latente pero no la causa directa

---

## Data Flow Completo

```
Google Places API
  → v4_comprehensive.py (GBPApiResult)
    → audit_result.gbp (lat, lng, phone, address, rating, reviews, name, website)
      → _extract_validated_fields() → validated_data["hotel_data"]
        → conditional_generator._generate_hotel_schema(hotel_data)
          → ESTIMATED_hotel_schema_*.json
```

**Punto de falla**: Google Places API → v4_comprehensive.py → audit_result.gbp
- Si Places API retorna 400 → gbp.lat = None, gbp.phone = None, etc.
- Si schema.properties vacio (no hay schema en HTML) → segunda fuente tampoco disponible
- Resultado: hotel_data = {name, url, price_range} sin datos criticos

---

## Fuentes de datos y fallbacks

| Campo | Fuente primaria | Fallback actual | Fallback faltante |
|-------|----------------|-----------------|-------------------|
| telephone | schema.properties | gbp.phone | web scraping (tel: links) |
| address | schema.properties | gbp.address | — |
| lat/lng | gbp.lat/lng | — | schema.geo |
| rating | schema.properties | gbp.rating | — |
| review_count | schema.properties | gbp.reviews | — |
| name | schema.properties | gbp.name → hotel_name → metadata.title | — |
| url | schema.properties | gbp.website → audit_result.url | — |

El fix debe completar estos fallbacks faltantes.
