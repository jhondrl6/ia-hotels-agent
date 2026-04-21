# CONTEXTO DE HANDOFF — AMH_REFACTOR_V2
**Fecha**: 2026-04-20 22:15
**Proyecto**: iah-cli — Release AMH (Amazilia Hotel)
**Estado**: RECHAZADO — Requiere investigación de causa raíz adicional
**Versión actual**: 4.32.0

---

## SITUACIÓN ACTUAL

### Veredicto Final: RECHAZADO

| GAP | Criterio | Estado |
|-----|----------|--------|
| G2 | hotel_schema con coords/tel/addr reales | ❌ FAIL — REVERSIÓN |
| G14 | Cero "COP COP" en propuesta | ✅ PASS |
| G13 | Region = "Eje Cafetero" (Title Case) | ✅ PASS |

**Problema central**: El schema del 2026-04-15 (ANTES de cualquier patch) tenía datos reales.
Todos los schemas del 2026-04-20 (DESPUÉS de patches) están vacíos. Los patches causaron regresión.

---

## DATOS CONFIRMADOS

### audit_report.json (post-PATCH-4) — LÍNEAS 37-38
```json
"lat": 4.8068995,
"lng": -75.8291505,
```
**PATCH-4 está aplicado** (v4_comprehensive.py líneas 231-232). Lat/lng ahora se serializan correctamente.

### hotel_schema generado (2026-04-20 22:01)
```json
{
  "@type": "Hotel",
  "name": "Amazilia Hotel Campestre",
  "url": "https://amaziliahotel.com/",
  "priceRange": "$$",
  "amenityFeature": [...],
  "starRating": "4",
  "numberOfRooms": "10",
  "checkinTime": "15:00",
  "checkoutTime": "12:00"
  // ❌ NO telephone
  // ❌ NO address
  // ❌ NO geo coordinates
}
```

### hotel_schema del 2026-04-15 (ANTES de patches) —Datos reales
```json
{
  "@type": "Hotel",
  "name": "Amazilia Hotel Campestre",
  "telephone": "+57 310 4019049",
  "address": {完整的地址},
  "geo": {latitude: 4.8133, longitude: -75.6961}
}
```

### GBPApiResult — Runtime tiene datos, JSON no los usa
- `gbp.phone`: "310 4019049" ✅
- `gbp.address`: "mts a la derecha, Via Pereira a #Entrada 8 Cafelia..." ✅
- `gbp.lat`: 4.8068995 ✅ (PATCH-4 aplicada)
- `gbp.lng`: -75.8291505 ✅ (PATCH-4 aplicada)
- `audit_report.json` tiene lat/lng ahora ✅

**PERO**: el `hotel_schema` que se genera NO incluye estos datos del GBP. Solo tiene los amenities detectados del website.

---

## FLOW DE DATOS (PROBLEMA IDENTIFICADO)

```
Places API → _search_places_new() → PlaceData(lat/lng) ✅
                                        ↓
                              _audit_gbp() → GBPApiResult(lat/lng/phone/addr) ✅
                                        ↓
                              to_dict() → audit_report.json (lat/lng serializados) ✅
                                        ↓
                    v4_asset_orchestrator._extract_validated_fields()
                              ↓
              ¿usa audit_result.gbp para poblar validated_data?
              ¿o solo usa audit_result.schema.properties?
                                        ↓
                              conditional_generator
                                        ↓
                              hotel_schema SIN datos de GBP ❌
```

**HIPÓTESIS PRINCIPAL**: `_extract_validated_fields()` extrae datos de `audit_result.schema.properties` (website extraído) pero NO inyecta los datos del GBP (`audit_result.gbp.lat/lng/phone/address`). El GBP tiene datos reales, pero no se usan para el schema.

---

## FIXES APLICADOS

| Patch | Descripción | Estado |
|-------|-------------|--------|
| PATCH-1 | FieldMask con `places.location` en _search_places_new | ✅ Aplicado |
| PATCH-2 | (Nombre wiring lat/lng → hotel_schema) | ¿? No verificado |
| PATCH-3 | `.title()` en region en proposal | ✅ Aplicado |
| PATCH-4 | Agregar lat/lng a `to_dict()` gbp block | ✅ Aplicado |

---

## EVIDENCIA

- **Logs E2E release-1**: `evidence/amh-release-validation-patches/v4complete_release.log`
- **Logs E2E release-2**: `evidence/amh-release-validation-patches-v2/v4complete_release2.log`
- **ROOT_CAUSE_ANALYSIS**: `evidence/amh-release-validation-patches/ROOT_CAUSE_ANALYSIS.md`
- **Plan siguiente fase**: `.opencode/plans/AMH_REFACTOR_V2/05-prompt-inicio-sesion-fase-PATCH-4.md`
- **audit_report.json**: `output/v4_complete/audit_report.json`
- **v4_complete_report.json**: `output/v4_complete/v4_complete_report.json` (region: "Eje Cafetero", coherence: 0.89)
- **hotel_schema vacío**: `output/v4_complete/amaziliahotel/hotel_schema/ESTIMATED_hotel_schema_20260420_220114.json`
- **Propuesta PASS (G14)**: `output/v4_complete/02_PROPUESTA_COMERCIAL_20260420_220114.md`

---

## PRÓXIMO PASO OBLIGATORIO

**Investigar `_extract_validated_fields()` en `v4_asset_orchestrator.py` (~línea 618+)**

1. ¿Extrae datos de `audit_result.gbp` o solo de `audit_result.schema.properties`?
2. Si solo usa `schema.properties`: agregar fallback a `audit_result.gbp.phone/lat/lng/address`
3. El schema del 15 de abril tenía datos reales de alguna fuente — identificar cuál cambió

**NO ejecutar nueva E2E hasta que se identifique la causa raíz del schema vacío.**

---

## ARCHIVOS CLAVE A REVISAR

| Archivo | Relevancia |
|---------|-----------|
| `modules/asset_generation/v4_asset_orchestrator.py` | `_extract_validated_fields()` — punto de falla |
| `modules/asset_generation/conditional_generator.py` | `_generate_hotel_schema()` — genera schema final |
| `modules/auditors/v4_comprehensive.py` | `to_dict()` — PATCH-4 ok, pero no resuelve el schema |
| `.opencode/plans/AMH_REFACTOR_V2/05-prompt-inicio-sesion-fase-PATCH-4.md` | Plan de siguiente fase |

---

## MÉTRICAS DE COSTO

- **E2E release-1**: ~$0.05 USD (1 ejecución completa)
- **E2E release-2**: ~$0.05 USD (post-PATCH-4)
- **Total AMH_REFACTOR_V2**: ~$0.10 USD en validaciones
