# ROOT CAUSE ANALYSIS — FASE-RELEASE-AMH-V2 (2026-04-20)

## Veredicto: RECHAZADO

| GAP | Criterio | Resultado |
|-----|----------|-----------|
| G2 | hotel_schema: coords, phone, name reales | ❌ FAIL |
| G14 | Cero "COP COP" en propuesta | ✅ PASS |
| G13 | Region = "Eje Cafetero" (Title Case) | ✅ PASS |

---

## G2: hotel_schema Vacío — Causa Raíz

### Síntoma
- audit_report.json → gbp{} tiene lat=None, lng=None
- v4_complete_report.json → hotel_schema = {}
- Schema en delivery ZIP: geo={}, telephone=null, address=null

### Análisis de Data Flow

```
Places API Response
  └── location: {latitude: 4.8133, longitude: -75.6961}  ✅ (FieldMask incluye places.location)
        │
        ▼
_place_data (v4_comprehensive.py:1108-1133)  ✅
  └── PlaceData(lat=4.8133, lng=-75.6961)     ✅
        │
        ▼
_audit_gbp → GBPApiResult (v4_comprehensive.py:777-795)  ✅
  └── GBPApiResult(lat=4.8133, lng=-75.6961)  ✅ (RUNTIME)
        │
        ▼
to_dict() → audit_report.json (v4_comprehensive.py:218-233)  ❌ PROBLEMA
  └── "lat" y "lng" NO ESTÁN en el dict serializado  ❌
        │
        ▼ (en orchestrator: _extract_validated_fields)
validated_data["hotel_data"]["latitude"] = getattr(gbp, 'lat', 0.0)  ❌
  └── gbp.lat = 0.0 (default) porque to_dict() no lo serializó
```

### Causa Raíz Confirmada

**BUG-1: to_dict() en V4AuditResult no serializa lat y lng del GBP**

- Archivo: modules/auditors/v4_comprehensive.py
- Línea: 218-233 (bloque "gbp": {...})
- GBPApiResult tiene campos lat: float = 0.0 y lng: float = 0.0 (líneas 76-77)
- Pero to_dict() solo serializa 13 campos y NO incluye lat ni lng

### Fix Mínimo (PATCH-4)

#### Fix G2-A: Agregar lat/lng a to_dict() gbp block
En v4_comprehensive.py líneas 218-233, agregar:
```python
"lat": self.gbp.lat,
"lng": self.gbp.lng,
```

---

## G13: Region — CORREGIDO ✅
- v4_complete_report.region = "Eje Cafetero" ✅
- No hay eje_cafetero lowercase en propuesta ✅
- PATCH-3 funcionó correctamente

## G14: COP COP — CORREGIDO ✅
- 0 ocurrencias en propuesta ✅
- PATCH-2 (re-scrub post-gen) funcionó correctamente

---

## Siguiente Paso

Ejecutar FASE-PATCH-4 para corregir G2:
1. Agregar lat/lng a to_dict() gbp block (2 líneas)
2. Re-ejecutar v4complete para validar

---

## REGRESIÓN DESCUBIERTA (2026-04-20)

**El schema del 2026-04-15 (ANTES de patches) tiene datos:**
- name: "Amazilia Hotel Campestre" ✅
- telephone: "+57 310 4019049" ✅
- address: {...} ✅
- geo: {latitude: 4.8133, longitude: -75.6961} ✅

**Todos los schemas del 2026-04-20 (DESPUÉS de patches) están vacíos:**
- name: "Amazilia Hotel Campestre" ✅ (nombre del GBP, no del schema)
- telephone: None ❌
- address: None ❌
- geo: None ❌

**Los patches causaron una regresión.** El schema.properties que tenía datos reales fue reemplazado por uno vacío.

### Hipótesis

PATCH-1 agregó/modificó `audit_result.schema.properties` — puede haber cambiado cómo se extraen los datos del schema del website.

### siguiente investigación

Verificar `_extract_validated_fields` en runtime: ¿qué datos recibe cuando hotel_schema se genera?
