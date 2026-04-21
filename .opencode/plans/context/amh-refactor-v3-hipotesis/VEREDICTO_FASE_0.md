# VEREDICTO FASE-0: Hipotesis V3

## Hipotesis V3 (la cadena de falla propuesta)

El schema del 15-abr era bueno (LodgingBusiness + datos GBP) porque
conditional_generator lo genero asi. El schema del 20-abr es malo (Hotel
sin datos) porque enricher lo genero y GEO-BRIDGE reemplazo el bueno con el malo.

## Evidencia

### T1: geo_enriched/ existia el 15-abr?

- Resultado: **SI EXISTE**
- Todos los archivos en geo_enriched/ tienen timestamp **Apr 20 22:01** (la ejecucion del 20-abr)
- NO hay archivos con timestamp del 15-abr en geo_enriched/
- Interpretacion: geo_enriched/ fue creado DURANTE la ejecucion del 20-abr, no existia durante la ejecucion del 15-abr

### T2: Comparacion schemas 15-abr vs 20-abr

| Aspecto | 15-abr (bueno) | 20-abr (malo) | hotel_schema_rich (enricher) |
|---------|----------------|---------------|------------------------------|
| @type | **LodgingBusiness** | **Hotel** | **Hotel** |
| telephone | +57 310 4019049 | **AUSENTE** | **AUSENTE** |
| address | Completo (calle, ciudad, region, pais) | **AUSENTE** | **AUSENTE** |
| geo (lat/lng) | 4.8133, -75.6961 | **AUSENTE** | **AUSENTE** |
| description | Presente | **AUSENTE** | **AUSENTE** |
| aggregateRating | 4.5 / 202 reviews | **AUSENTE** | **AUSENTE** |
| speakable | Presente | **AUSENTE** | **AUSENTE** |
| confidence | 0.95 (PASSED) | 0.85 (WARNING) | N/A |
| can_use | true | **false** | N/A |
| source_data_hash | amaziliahotel_v2_real_data | 50ed899df51e56b9 | N/A |

**OBSERVACION CRITICA**: El schema del 20-abr y el hotel_schema_rich.json del enricher son **IDENTICOS** en estructura (ambos "@type": "Hotel", ambos sin telephone/address/geo/description/aggregateRating). Solo difieren en formato de salto de linea (\r\n vs \n).

### T3: _extract_validated_fields() en v4_asset_orchestrator.py

- Extrae de `audit_result.schema.properties` (linea 639-656): name, description, telephone, url, address, image, price_range, email, amenities, region, city, rating, review_count
- Extrae de `audit_result.gbp` (linea 659-693): lat/lng (con validacion Colombia), phone, address, rating, reviews, name, website
- Crea keys en validated_data: hotel_data.latitude, hotel_data.longitude, hotel_data.telephone, hotel_data.phone, hotel_data.address, hotel_data.rating, hotel_data.review_count, hotel_data.name
- **USA `setdefault()` para lat/lng** (linea 665-666): solo las pone si NO estan ya en hotel_data. Esto significa que si schema.properties ya puso lat/lng, GBP no las sobreescribe.
- **USA `if not ... .get()` para phone/address/rating/reviews/name**: Solo pone datos GBP si el campo esta vacio o no existe.

### T4: conditional_generator._generate_hotel_schema()

- Recibe `hotel_data` via `validated_data.get("hotel_data", {})` (linea 386/461)
- Genera "@type": **"LodgingBusiness"** (linea 740)
- Lee phone de `hotel_data.get("phone")` o `hotel_data.get("telephone")` (linea 731)
- Lee geo de `hotel_data.get("latitude/longitude")` con validacion Colombia (linea 753-757)
- Lee rating/review_count de hotel_data (linea 764-768)
- Genera speakable, aggregateRating, address completos

### T5: Orden de ejecucion y GEO-BRIDGE

**Pipeline v4complete para hotel_schema**:

1. `_extract_validated_fields()` construye `validated_data["hotel_data"]` con datos de schema.properties + GBP
2. `conditional_generator.generate()` → `_generate_hotel_schema(hotel_data)` → genera schema "LodgingBusiness" con datos
3. Si `confidence_score < 0.7` → `try_enrich_from_geo_enriched()` intenta reemplazar con `hotel_schema_rich.json`
4. Si el geo_enriched tiene mejor score → **SOBREESCRIBE** el archivo en disco

**CRUCE CRUCIAL**: El schema del 20-abr muestra:
- metadata: `confidence_score: 0.85`, `preflight_status: WARNING`, `can_use: false`
- Pero GEO-BRIDGE solo actua si confidence < 0.7 (linea 299)
- 0.85 > 0.7 → GEO-BRIDGE **NO SE EJECUTO** para el schema del 20-abr

**Pero el contenido del 20-abr ES IDENTICO al enricher output**: Esto significa que el schema fue generado por el enricher (Hotel, sin datos), NO por el conditional_generator (LodgingBusiness, con datos).

## ANALISIS: Que paso realmente?

### El 15-abr (schema bueno):
- `_extract_validated_fields()` recibio datos GBP reales → hotel_data tenia telephone, address, lat/lng, rating
- `conditional_generator._generate_hotel_schema()` uso esos datos → LodgingBusiness completo
- metadata dice: `source_data_hash: amaziliahotel_v2_real_data`, `diagnostic_reference: FASE-2A`
- **Esto fue generado en una sesion de hand-seeding o inyeccion manual** (el metadata timestamp es Apr 19 20:31 pero el archivo dice Apr 15)

### El 20-abr (schema malo):
- El schema ES IDENTICO al `hotel_schema_rich.json` del enricher
- El enricher genera "@type": "Hotel" sin datos GBP
- metadata: `confidence_score: 0.85`, `preflight_status: WARNING`, `can_use: false`
- `diagnostic_reference: None` → no vino de una sesion de diagnostico con datos reales
- `source_data_hash: 50ed899df51e56b9` → hash generico

**Hay dos posibles explicaciones**:

**ESCENARIO A**: GEO-BRIDGE reemplazo el schema. Pero 0.85 > 0.7 (threshold)... a menos que:
1. El conditional_generator genero un schema con confidence < 0.7
2. GEO-BRIDGE lo reemplazo con el enricher schema (confidence 0.85)
3. El metadata del 20-abr refleja el score post-enrichment (0.85), no el pre-enrichment

**ESCENARIO B**: El conditional_generator no recibio datos GBP esta vez (API Places fallo), genero un schema basico (sin telefono, sin geo, sin address), que casualmente se parece al enricher output. Y GEO-BRIDGE no se activo porque el score ya era 0.85.

## VEREDICTO

**HIPOTESIS PARCIALMENTE CONFIRMADA con matices criticos**

- [x] El schema del 15-abr era bueno (LodgingBusiness + datos reales) → CONFIRMADO
- [x] El schema del 20-abr es malo (Hotel sin datos reales) → CONFIRMADO
- [x] El enricher genera "@type": "Hotel" sin datos GBP → CONFIRMADO
- [x] El conditional_generator genera "@type": "LodgingBusiness" con datos → CONFIRMADO
- [ ] GEO-BRIDGE fue el causante de la regresion → **NO CONFIRMADO**

**CAUSA RAIZ REAL** (mas probable):

La causa raiz NO es GEO-BRIDGE. Es que **el pipeline no paso datos GBP al conditional_generator** en la ejecucion del 20-abr. Esto puede deberse a:

1. **API Places fallo** (retorno 400) → audit_result.gbp no tuvo datos reales → `_extract_validated_fields()` no puso nada en hotel_data → conditional_generator genero schema vacio
2. **`audit_result.schema.properties` estaba vacio** → la linea 639 `if audit_result and audit_result.schema and audit_result.schema.properties` fue False → no se lleno hotel_data desde schema
3. **El fallback de GBP tampoco funciono** → gbp.lat/lng/phone eran None o 0.0 → no paso la validacion Colombia

Ademas, hay un **BUG en GEO-BRIDGE**: Si el conditional_generator produce un schema con confidence < 0.7, GEO-BRIDGE lo reemplaza con `hotel_schema_rich.json` que es "@type": "Hotel" (enricher) sin datos. Esto DEGRADA el schema si el enricher no tiene datos reales.

## Proximo paso

1. **ABORTAR V3** (el plan de 4 fases para fixear enricher/bridge era incorrecto)
2. Crear plan alternativo (V3-alt) que ataque la causa raiz real:
   - **FASE-1**: Verificar por que `_extract_validated_fields()` no recibe datos GBP (API Places status, audit_result.gbp contenido)
   - **FASE-2**: Fixear GEO-BRIDGE para NO reemplazar schemas LodgingBusiness con Hotel si el enricher no tiene datos reales
   - **FASE-3**: Garantizar que conditional_generator SIEMPRE tenga datos minimos (name, url) aunque falle GBP
3. NO crear fases para el enricher -- el enricher trabaja con datos diferentes y es correcto para su contexto
