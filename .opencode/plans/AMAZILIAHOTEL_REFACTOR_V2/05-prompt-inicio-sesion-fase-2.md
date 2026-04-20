# FASE-2: Fix hotel_schema con datos reales del audit
**Proyecto**: Amaziliahotel E2E Refactor v2  
**Anterior**: FASE-1 (geo_score necesita ser > 0 — query corregido)  
**Siguiente**: FASE-3 (Content Scrubber)

---

## Contexto

**G2 (CRÍTICO)**: El veredicto forense mostró que `hotel_schema` tiene TODOS los campos vacíos:
- `telephone`: vacío
- `address`: vacío
- `geo`: vacío
- `latitude`/`longitude`: 0.0

**Causa raíz**: `_generate_hotel_schema()` en `conditional_generator.py` no usa los datos del audit (`geo_enriched/`) — usa valores por defecto o hardcodeados.

---

## Tareas de la Fase

### 1. Localizar el código del problema

Revisar `modules/asset_generation/conditional_generator.py`:
```bash
grep -n "_generate_hotel_schema\|hotel_schema\|generate_schema" \
    /mnt/c/Users/Jhond/Github/iah-cli/modules/asset_generation/conditional_generator.py
```

### 2. Implementar Fix

El método `_generate_hotel_schema()` debe:

1. **Leer datos del audit** — `geo_enriched/` tiene los datos reales
2. **Mapear campos**:
   - `geo_enriched.address` → `address`
   - `geo_enriched.telephone` → `telephone`
   - `geo_enriched.latitude` → `latitude`
   - `geo_enriched.longitude` → `longitude`
3. **Fallback graceful**: si no hay datos en `geo_enriched/`, no generar campos vacíos — omitir el campo o marcar como "pending_verification"

### 3. Validación

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Generar assets para Amaziliahotel
./venv/Scripts/python.exe main.py stage --url https://amaziliahotel.com/ --stage outputs 2>&1 | grep -E "hotel_schema|Hotel|telephone|address"

# Verificar que el schema tenga datos reales
cat outputs/amaziliahotel.com/assets/hotel_schema.json 2>/dev/null || echo "No existe"
```

### 4. Ejecutar v4complete para verificar E2E

```bash
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ 2>&1 | grep -E "hotel_schema|Telephone|Address|score"
```

---

## Post-Ejecución

### Checklist de completitud

- [ ] `_generate_hotel_schema()` usa `geo_enriched/` como fuente
- [ ] hotel_schema.json tiene `telephone`, `address`, `geo.lat`, `geo.lng`
- [ ] No hay campos vacíos o con valor "N/A"
- [ ] Tests pasando: `pytest tests/asset_generation/test_conditional_generator.py -v -k "hotel"`
- [ ] Sin regresiones en otros generators

### Actualizar estado

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-2 \
    --desc "Fix hotel_schema — usa datos reales de geo_enriched/" \
    --archivos-mod "modules/asset_generation/conditional_generator.py" \
    --tests "8" \
    --check-manual-docs
```

---

## Criterios de Aprobación

| Criterio | Estado |
|----------|--------|
| hotel_schema.telephone con datos reales | [ ] |
| hotel_schema.address con datos reales | [ ] |
| hotel_schema.geo.lat > 0 | [ ] |
| hotel_schema.geo.lng != 0.0 | [ ] |
| Tests pasando | [ ] |
