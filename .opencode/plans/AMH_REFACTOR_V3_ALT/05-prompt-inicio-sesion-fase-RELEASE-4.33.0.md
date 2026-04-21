# FASE-RELEASE: E2E Validation + Release 4.33.0

**ID**: FASE-RELEASE-4.33.0  
**Objetivo**: Ejecutar v4complete E2E con Amazilia Hotel y validar que hotel_schema tiene datos reales  
**Dependencias**: FASE-1 + FASE-2 + FASE-3 completadas  
**Duracion estimada**: 1-2 horas  
**Costo API**: ~$0.15 (una ejecucion v4complete)  
**Skill**: iah-cli-phased-execution

---

## Contexto

Todas las fases de implementacion estan completas. Esta es la unica ejecucion de v4complete del plan. El objetivo es validar que el hotel_schema resultante tiene datos reales (telephone, address, geo) y que GEO-BRIDGE no degrada el resultado.

---

## Tareas

### T1: Verificacion pre-release

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Syntax check de todos los archivos modificados
./venv/Scripts/python.exe -m py_compile modules/asset_generation/v4_asset_orchestrator.py
./venv/Scripts/python.exe -m py_compile modules/asset_generation/conditional_generator.py
./venv/Scripts/python.exe -m py_compile modules/asset_generation/geo_enriched_bridge.py

# Tests de regresion
./venv/Scripts/python.exe -m pytest tests/asset_generation/ -x --tb=short -q
```

### T2: Ejecutar v4complete E2E

```bash
mkdir -p evidence/amh-refactor-v3-alt

./venv/Scripts/python.exe main.py v4complete \
    --url https://amaziliahotel.com/ \
    --debug 2>&1 | tee evidence/amh-refactor-v3-alt/ejecucion_release.log
```

### T3: Validar hotel_schema resultante + fallback activation

```bash
# Encontrar el schema generado mas reciente
ls -lt output/v4_complete/amaziliahotel/hotel_schema/ESTIMATED_hotel_schema_*.json | head -1
```

Verificar en el schema:
1. `@type`: Debe ser "LodgingBusiness" (NO "Hotel")
2. `telephone`: Debe tener un numero real (NO vacio)
3. `address`: Debe tener al menos streetAddress y addressCountry
4. `geo`: Debe tener lat/lng en rango Colombia (0-13, -82 a -66)
5. Confidence: >= 0.7

**CRITICO — Validar que fallbacks se activaron**:
```bash
# Verificar logs de diagnostico (FASE-1 T4)
grep "MISSING\|PRESENT" evidence/amh-refactor-v3-alt/ejecucion_release.log | grep -E "telephone|address|geo|rating|review_count"

# Verificar que NO hay Data Rescue flag
grep "DataRescue\|data_rescue_needed" evidence/amh-refactor-v3-alt/ejecucion_release.log
```

Si aparece `[DataRescue] All fallbacks failed` o confidence = 0.3:
→ NO continuar con release. Ejecutar plan de contingencia (T7).

### T4: Validar GEO-BRIDGE comportamiento

```bash
# Verificar logs del GEO-BRIDGE
grep "GEO-Bridge" evidence/amh-refactor-v3-alt/ejecucion_release.log
```

Verificar:
1. Si GEO-BRIDGE se activo: solo lo hizo para mejorar, no para degradar
2. Si GEO-BRIDGE rechazo un reemplazo: log dice "Quality gate REJECTED"
3. Si no se activo: confidence >= 0.7 (correcto)

### T5: Validar publication gates

```bash
grep "gate\|PASSED\|FAILED\|BLOCKED" evidence/amh-refactor-v3-alt/ejecucion_release.log | tail -20
```

Todos los gates deben pasar.

### T6: Release documentation

1. Actualizar VERSION.yaml:
   - version: 4.33.0
   - codename: "AMH V3-Alt Datasource Gap Fix"
   - release_date: fecha actual

2. sync_versions.py:
   ```bash
   ./venv/Scripts/python.exe scripts/sync_versions.py
   ```

3. CHANGELOG.md — agregar entrada:
   ```markdown
   ## [4.33.0] - 2026-04-21
   
   ### Objetivo
   Fix hotel_schema vacio: causa raiz = datos GBP no llegaban a validated_data
   
   ### Cambios
   - _extract_validated_fields(): fallbacks completos para telephone (cross_validation), geo (schema.geo), address (gbp.formatted_address), rating (gbp.rating), review_count (gbp.user_ratings_total)
   - GEO-BRIDGE: quality gate que rechaza reemplazos peores (LodgingBusiness -> Hotel sin datos)
   - conditional_generator: garantia de datos minimos + Data Rescue flag (penaliza a 0.3 si fallbacks fallan) + penalizacion de confidence por datos faltantes
   
   ### Archivos Nuevos
   - tests/asset_generation/test_datasource_gap.py
   
   ### Archivos Modificados
   - modules/asset_generation/v4_asset_orchestrator.py
   - modules/asset_generation/geo_enriched_bridge.py
   - modules/asset_generation/conditional_generator.py
   - tests/asset_generation/test_geo_enriched_bridge.py
   - tests/asset_generation/test_conditional_generator.py
   
   ### Tests
   - >= 17 tests nuevos (8 + 5 + 4 por fase)
   ```

4. GUIA_TECNICA.md — agregar nota tecnica

5. REGISTRY.md — verificar todas las fases registradas

### T7: Plan de contingencia (ejecutar SOLO si T3 detecta schema vacio o confidence 0.3)

Si la ejecucion E2E produce schema sin datos (telephone vacio, address vacio, confidence < 0.7):

1. **NO hacer release 4.33.0**
2. **Documentar en evidence/**:
   ```bash
   echo "FASE-RELEASE RECHAZADA: Schema vacio despues de fixes" >> evidence/amh-refactor-v3-alt/contingencia_triggered.md
   echo "Fecha: $(date)" >> evidence/amh-refactor-v3-alt/contingencia_triggered.md
   echo "Confidence: $(grep confidence evidence/amh-refactor-v3-alt/ejecucion_release.log | tail -1)" >> evidence/amh-refactor-v3-alt/contingencia_triggered.md
   ```
3. **Crear FASE-4: INYECCION-MANUAL** en el plan:
   - Usar datos del schema 15-abr conocido (source_data_hash: amaziliahotel_v2_real_data)
   - Inyectar telephone (+57 310 4019049), geo (4.8133, -75.6961), rating (4.5), review_count (202)
   - Modificar `_extract_validated_fields()` para leer de `evidence/known_good_data/amaziliahotel.json`
   - Re-ejecutar v4complete (costo API: ~$0.15)
4. **Abortar release** hasta que FASE-4 valide exito

### T8: Commit y tag (solo si T3 paso y T7 NO se activo)

```bash
git add .
git commit -m "release: v4.33.0 AMH V3-Alt — fix hotel_schema datasource gap"
git tag v4.33.0
```

---

## Criterios de Completitud

- [ ] v4complete ejecuta sin crash
- [ ] hotel_schema tiene @type "LodgingBusiness"
- [ ] hotel_schema tiene telephone con datos reales
- [ ] hotel_schema tiene address con datos reales
- [ ] hotel_schema tiene geo con coordenadas Colombia
- [ ] Fallbacks se activaron (logs confirman PRESENT en telephone, address, geo, rating, review_count)
- [ ] NO aparece `[DataRescue] All fallbacks failed` en logs
- [ ] Confidence >= 0.7 (NO 0.3 que indica data rescue)
- [ ] GEO-BRIDGE quality gate funciona correctamente
- [ ] Todos los publication gates pasan
- [ ] VERSION.yaml = 4.33.0 (solo si T7 NO se activo)
- [ ] CHANGELOG.md actualizado
- [ ] GUIA_TECNICA.md actualizado
- [ ] REGISTRY.md actualizado
- [ ] log_phase_completion.py ejecutado con --release 4.33.0 (solo si exito)
- [ ] git commit + tag v4.33.0 (solo si exito)
- [ ] O: Plan de contingencia T7 ejecutado si schema vacio
