# AMH_REFACTOR_V3_ALT — Plan Maestro

**Fecha**: 2026-04-21
**Proyecto**: iah-cli — Amazilia Hotel Release
**Anterior**: AMH_REFACTOR_V3 (ABORTADO — hipotesis de causa raiz parcialmente incorrecta)
**Version actual**: 4.32.0
**Veredicto FASE-0**: RECHAZADA → abortar V3, redirigir a causa raiz real

---

## CAUSA RAIZ REAL (verificada con codigo)

### Diagnostico

V3 decia que GEO-BRIDGE reemplazaba el schema bueno (LodgingBusiness + datos GBP) con el schema malo del enricher (Hotel sin datos). FASE-0 demostro que esta cadena es **parcialmente incorrecta**:

**Evidencia clave**:
1. Schema 15-abr: `@type: "LodgingBusiness"`, tiene telephone, address, geo, aggregateRating, description, speakable. Confidence 0.95. `can_use: true`.
2. Schema 20-abr: `@type: "Hotel"`, SIN telephone, SIN address, SIN geo, SIN description, SIN aggregateRating. Confidence 0.85. `can_use: false`.
3. `hotel_schema_rich.json` (enricher): IDENTICO al schema del 20-abr — mismo `@type: "Hotel"`, mismos datos vacios.
4. GEO-BRIDGE threshold es 0.7. El schema 20-abr tiene confidence 0.85 > 0.7 → GEO-BRIDGE **no se ejecuto** para ese asset.
5. `_extract_validated_fields()` (linea 618-726) SI extrae datos de `audit_result.gbp` y `audit_result.schema.properties` — el codigo esta correcto.

### Cadena de falla REAL

```
1. API Places fallo (400) o schema.properties estaba vacio
       |
2. _extract_validated_fields() no encontro datos GBP
   - gbp.lat/lng = None/0.0 → no pasa validacion Colombia
   - gbp.phone = None → no hay telefono
   - schema.properties vacio → no hay address, description, rating
   - hotel_data queda practicamente vacio: {name, url, price_range, amenities}
       |
3. conditional_generator._generate_hotel_schema() recibe hotel_data vacio
   - Genera schema con: name="Amazilia Hotel", url, priceRange="$$"
   - SIN telephone, SIN address, SIN geo, SIN rating
   - @type = "LodgingBusiness" (correcto)
   - Confidence alta (0.85) porque el generador no penaliza datos faltantes
       |
4. GEO-BRIDGE: confidence 0.85 > threshold 0.7 → NO se ejecuta
   - Pero si SE EJECUTARA, reemplazaria con hotel_schema_rich.json (enricher)
     que es IDENTICO en contenido (sin datos) pero con @type: "Hotel"
       |
5. Resultado: ESTIMATED_hotel_schema con datos vacios
```

### Bug adicional: GEO-BRIDGE degradation

Aunque GEO-BRIDGE no fue la causa directa en esta ejecucion, tiene un bug latente:
- Si confidence < 0.7 → reemplaza con enricher output
- El enricher NO tiene datos GBP (trabaja con CanonicalAssessment, no V4AuditResult)
- Resultado: reemplaza LodgingBusiness (potencialmente con algunos datos) con Hotel (sin datos)
- **Esto empeora el resultado en vez de mejorarlo**

### Por que el 15-abr funciono

El schema del 15-abr tiene metadata: `source_data_hash: amaziliahotel_v2_real_data`, `diagnostic_reference: FASE-2A`. Esto indica que fue generado en una sesion donde los datos GBP SI estaban disponibles (API Places respondio correctamente, o los datos fueron inyectados manualmente desde una sesion de diagnostico previa).

---

## FASES DEL REFACTORING

| Fase | ID | Objetivo | Archivos principales | Costo API |
|------|----|----------|---------------------|-----------|
| FASE-1 | DATASOURCE-GAP | Diagnosticar y fixear por que datos GBP no llegan a validated_data. **Incluye pre-validacion T0 de fuentes de fallback.** | v4_asset_orchestrator.py, main.py | $0 (solo codigo) |
| FASE-2 | BRIDGE-QUALITY-GUARD | GEO-BRIDGE solo reemplaza si el reemplazo es objetivamente mejor | geo_enriched_bridge.py | $0 |
| FASE-3 | MINIMUM-DATA-GUARANTEE | Garantizar datos minimos en conditional_generator. **Incluye Data Rescue flag que bloquea publicacion si fallbacks fallan.** | conditional_generator.py, v4_asset_orchestrator.py | $0 |
| FASE-RELEASE | RELEASE-4.33.0 | E2E validation con validacion de fallback activation + plan de contingencia FASE-4 si schema sigue vacio | Todos | ~$0.15 (o ~$0.30 si FASE-4) |

### Dependencias

```
FASE-1 (DATASOURCE-GAP) — Diagnostico sin API
  |
  +---> FASE-2 (BRIDGE-QUALITY-GUARD) — Fix GEO-BRIDGE
  |       |
  |       +---> FASE-3 (MINIMUM-DATA-GUARANTEE) — Garantia de datos minimos
  |               |
  |               +---> FASE-RELEASE (E2E + Release 4.33.0)
  |
  [FASE-2 y FASE-3 pueden ser paralelas si no comparten archivos]
```

### Conflict Matrix

| Fase | Archivos que modifica |
|------|----------------------|
| FASE-1 | modules/asset_generation/v4_asset_orchestrator.py, tests/asset_generation/test_v4_asset_orchestrator.py |
| FASE-2 | modules/asset_generation/geo_enriched_bridge.py, tests/asset_generation/test_geo_enriched_bridge.py |
| FASE-3 | modules/asset_generation/conditional_generator.py, modules/asset_generation/v4_asset_orchestrator.py |
| FASE-RELEASE | VERSION.yaml, CHANGELOG.md, GUIA_TECNICA.md, REGISTRY.md |

**Overlap**: FASE-1 y FASE-3 comparten `v4_asset_orchestrator.py` → secuenciales
**Overlap**: FASE-2 NO comparte archivos con FASE-1 → podria ser paralela, pero logicamente depende del diagnostico de FASE-1

---

## RESTRICCIONES

1. **1 fase por sesion** — Sin excepciones
2. **v4complete SOLO en FASE-RELEASE** — No gastar API en fases intermedias
3. **Windows venv**: `./venv/Scripts/python.exe` para TODO
4. **No bump de version** hasta FASE-RELEASE
5. **Tests de regresion** antes de cada fase
6. **No tocar hotel_schema_enricher.py** — el enricher trabaja con datos diferentes (CanonicalAssessment) y es correcto para su contexto (geo_flow). El problema no esta ahi.
7. **NO hacer release si T7 (plan de contingencia) se activa** — Abortar release y crear FASE-4: INYECCION-MANUAL
