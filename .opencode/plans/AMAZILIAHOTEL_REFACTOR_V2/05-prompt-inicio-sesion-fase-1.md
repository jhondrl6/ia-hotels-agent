# FASE-1: Fix Google Maps Query — Nombre derivado del dominio
**Proyecto**: Amaziliahotel E2E Refactor v2
**Anterior**: Ninguna (FASE-1 es independiente)
**Siguiente**: FASE-2 (depende de geo_score válido)

---

## Contexto

**NG4 (CRÍTICO)**: El veredicto forense asume "API key inválida". **Esta hipótesis es incorrecta.**

**Hipótesis corregida (post-forense)**: Google Maps Places API retorna `ZERO_RESULTS` porque `_build_search_queries()` en `v4_comprehensive.py` extrae el nombre del hotel del dominio: `domain.split('.')[0]` → `"amaziliahotel"` → `.title()` → `"Amaziliahotel"`. Google Maps no asocia este string como nombre de hotel.

**Evidencia**:
- El archivo `modules/auditors/places_auditor.py` NO EXISTE. La funcionalidad está en `modules/auditors/v4_comprehensive.py`.
- Método `_build_search_queries()` (~línea 917) construye queries incluyendo el domain-derived name como fallback.
- Línea 979: `domain_name = domain.split('.')[0]`
- Línea 982: `readable = domain_name.replace('-', ' ').replace('_', ' ').title()` → produce "Amaziliahotel"
- El método también intenta variaciones con espacios (~línea 964-969) pero el core query sigue siendo deficiente.

**Resultado cascada**:
- `geo_score=0`
- `lat/lng=0.0`
- `hotel_schema` con campos vacíos (tel, addr, geo) → arrastra a FASE-2

---

## Tareas de la Fase

### 1. Verificar la hipótesis en el código real

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Archivo correcto (NO places_auditor.py que NO existe)
grep -n "_build_search_queries\|domain_name\|\.split.*\..*\[0\]\|textQuery\|search_place" \
    modules/auditors/v4_comprehensive.py | head -30

# Ver cómo se construye el query
grep -n "readable\|domain_name\|hotel_name.*query\|query.*hotel" \
    modules/auditors/v4_comprehensive.py | head -20
```

### 2. Identificar el query malformado

Google Maps Places API (New) acepta:
- `textQuery` — búsqueda libre (ej: "Amazilia Hotel Armenia Colombia")
- `locationBias` — sesgo geográfico
- `includedType` — tipo de lugar (lodging/hotel)

**Error actual**: `domain.split('.')[0].title()` → `"Amaziliahotel"` → Google no lo asocia.

**Fix correcto**: Construir query con nombre legible + ubicación conocida:
- Si hay datos del schema scraping: usar `schema_org_data.name` + ciudad/país
- Fallback: parsear dominio inteligentemente ("amaziliahotel" → "Amazilia Hotel") + "Armenia Quindío Colombia"

### 3. Implementar Fix

En `modules/auditors/v4_comprehensive.py`, método `_build_search_queries()`:

```python
# ANTES (MAL) — línea ~979-982
domain_name = domain.split('.')[0]
readable = domain_name.replace('-', ' ').replace('_', ' ').title()
# Resultado: "Amaziliahotel" — Google no lo encuentra

# DESPUÉS (CORRECTO)
# 1. Intentar nombre del schema primero
hotel_name = schema_data.get("name", "") if schema_data else ""

# 2. Si no hay schema, parsear dominio separando palabras
if not hotel_name:
    domain_name = domain.split('.')[0]
    # Separar camelCase o palabras conocidas
    import re
    readable = re.sub(r'([a-z])([A-Z])', r'\1 \2', domain_name)
    readable = readable.replace('-', ' ').replace('_', ' ').strip()
    # Heurística: si "hotel" no está, agregarlo
    if "hotel" not in readable.lower():
        readable = readable + " Hotel"

# 3. Agregar ubicación conocida
location = ""
if city:
    location = f"{city}"
if region:
    location = f"{location} {region}".strip()
query = f"{readable} {location} Colombia".strip()
# Resultado: "Amazilia Hotel Armenia Quindío Colombia"
```

### 4. Verificar fix

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Test con query corregido (verificar que el método existe)
grep -n "_search_places_new\|_build_search_queries" modules/auditors/v4_comprehensive.py

# Test unitario del query builder
./venv/Scripts/python.exe -c "
from modules.auditors.v4_comprehensive import V4ComprehensiveAuditor
a = V4ComprehensiveAuditor()
# Verificar que el query builder produce algo usable
queries = a._build_search_queries('amaziliahotel.com', schema_data={}, city='Armenia', region='Quindío')
print('Queries generados:', queries)
"
```

**Criterio de éxito**: Los queries NO contienen "amaziliahotel" sin espacios. Deben incluir "Amazilia Hotel" + ubicación.

### 5. Validar con v4audit completo

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4audit --url https://amaziliahotel.com/ --check-places 2>&1 | grep -E "geo_score|lat|lng|score|ZERO_RESULTS"
```

---

## Post-Ejecución

### Checklist de completitud

- [ ] Query corregido: no usa domain.split()[0] directamente como nombre
- [ ] Queries incluyen nombre parseado + ubicación
- [ ] Places API retorna resultado (no ZERO_RESULTS)
- [ ] geo_score > 0
- [ ] lat/lng != 0.0
- [ ] Tests pasando: `pytest tests/auditors/ -v -k "places or search or geo"`
- [ ] No hay regresiones en otros audits que sí encuentren su hotel

### Actualizar estado

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-1 \
    --desc "Fix Google Maps query — _build_search_queries usa nombre parseado + ubicación, NO domain.split()[0]" \
    --archivos-mod "modules/auditors/v4_comprehensive.py" \
    --tests "5" \
    --check-manual-docs
```

---

## Criterios de Aprobación

| Criterio | Estado |
|----------|--------|
| Archivo correcto: `v4_comprehensive.py` (NO places_auditor.py) | [ ] |
| Query NO usa "amaziliahotel" como string sin espacios | [ ] |
| geo_score > 0 (no 0.0) | [ ] |
| lat/lng != 0.0 | [ ] |
| Places API no retorna ZERO_RESULTS | [ ] |
| Tests pasando | [ ] |
