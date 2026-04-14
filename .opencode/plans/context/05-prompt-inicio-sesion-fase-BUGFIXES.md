# FASE-BUGFIXES — Corrección Bugs Específicos (WhatsApp, Review, Org_schema, Propuesta)

**ID**: FASE-BUGFIXES
**Objetivo**: Corregir 4 bugs específicos que generan assets rotos/falsos
**Dependencias**: FASE-DATASOURCE ✅ (completada 2026-04-14)
**Duración estimada**: 1-2 horas
**Skill**: systematic-debugging
**Paralela con**: FASE-PERSONALIZATION (NO compartir archivos — ver Restricciones)

---

## Contexto

4 bugs en assets individuales. NO aborda causa raíz (eso es PERSONALIZATION).

| ID | Problema | Archivo |
|----|----------|---------|
| D4 | WhatsApp href="detected_via_html" (roto) | whatsapp_button_generator.py |
| D5 | Review widget ★★★★★ falso (0 reviews reales) | review_widget_generator.py |
| D6 | org_schema url="example.com" (placeholder) | org_schema_generator.py |
| D7 | Propuesta dice "No generado" para assets que SÍ existen | main.py |

## Estado Post-FASE-DATASOURCE

Los datos del audit YA están disponibles en `validated_data`:
- `validated_data["hotel_data"]["telephone"]` — teléfono del sitio
- `validated_data["phone_web"]` — teléfono de web scraping
- `validated_data["gbp_rating"]` — rating real del GBP
- `validated_data["gbp_review_count"]` — reviews reales

---

## ⚠️ RESTRICCIONES CRÍTICAS (paralelización)

**NO modificar estos archivos** (pertenece a FASE-PERSONALIZATION que corre en paralelo):
- `modules/asset_generation/v4_asset_orchestrator.py`
- `modules/asset_generation/conditional_generator.py`
- `modules/asset_generation/llmstxt_generator.py` (si es archivo separado)
- `modules/asset_generation/geo_playbook_generator.py` (si es archivo separado)
- `modules/asset_generation/monthly_report_generator.py` (si es archivo separado)
- `modules/asset_generation/optimization_guide_generator.py` (si es archivo separado)

**Archivos SÍ permitidos para esta fase:**
- `modules/asset_generation/whatsapp_button_generator.py`
- `modules/asset_generation/review_widget_generator.py`
- `modules/asset_generation/org_schema_generator.py`
- `main.py` (solo sección propuesta ~líneas 2063-2098)

---

## Tarea 1: D4 — Fix WhatsApp Button

### Problema
`href="https://wa.me/detected_via_html?text=..."` — "detected_via_html" no es un número.

### Pasos
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
grep -rn "detected_via_html" modules/asset_generation/ --include="*.py"
```

### Fix
En `whatsapp_button_generator.py`:
- Si `validated_data["phone_web"]` existe → usar ese número (normalizar: quitar +57, espacios)
- Si no hay teléfono → generar botón con marcador claro `[PENDIENTE: número de WhatsApp]`
- NUNCA pasar "detected_via_html" como número

### Criterio
```bash
grep "detected_via_html" modules/asset_generation/whatsapp_button_generator.py
# Esperado: 0 matches
```

---

## Tarea 2: D5 — Fix Review Widget

### Problema
Muestra ★★★★★ "Excelente servicio" cuando `gbp_rating=0.0` y `gbp_review_count=0`.

### Pasos
```bash
grep -rn "Excelente servicio\|★★★★★\|5 estrellas" modules/asset_generation/ --include="*.py"
```

### Fix
En `review_widget_generator.py`:
- Si `rating == 0.0` o `review_count == 0` → mostrar "Aún no hay reseñas disponibles" o widget vacío
- Si hay datos reales → mostrarlos con rating exacto
- NUNCA inventar reviews

### Criterio
```bash
grep "Excelente servicio" modules/asset_generation/review_widget_generator.py
# Esperado: 0 matches (o solo en condicional con rating > 0)
```

---

## Tarea 3: D6 — Fix Org Schema

### Problema
`url="https://example.com"` (placeholder), `telephone=""`, `logo=""`.

### Pasos
```bash
grep -rn "example.com" modules/asset_generation/ --include="*.py"
```

### Fix
En `org_schema_generator.py`:
- Usar `validated_data["hotel_data"]["url"]` si existe
- Usar `validated_data["hotel_data"]["telephone"]` si existe
- Si falta dato → omitir el campo del JSON (no incluir placeholder)
- NUNCA usar "example.com"

### Criterio
```bash
grep "example.com" modules/asset_generation/org_schema_generator.py
# Esperado: 0 matches
```

---

## Tarea 4: D7 — Fix Propuesta "No generado"

### Problema
La propuesta muestra ❌ para assets que SÍ se generaron.

### Pasos
```bash
grep -n "No generado\|voice_assistant\|whatsapp_button\|monthly_report" main.py | head -20
```

### Fix
En `main.py` (~sección propuesta, líneas 2063-2098):
- Verificar si el archivo físico existe en `output/v4_complete/{hotel}/asset_dir/`
- Marcar ✅ si existe, ❌ si no
- No depender solo de flags internos

### Criterio
Verificar que la propuesta refleje el estado real de los archivos generados.

---

## Validación

### Tests
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/ -v -k "whatsapp or review or org_schema" --tb=short
```

### Verificación código (sin v4complete)
```bash
# D4: No más detected_via_html en código
grep -c "detected_via_html" modules/asset_generation/whatsapp_button_generator.py
# Esperado: 0

# D5: No más Excelente servicio hardcodeado
grep -c "Excelente servicio" modules/asset_generation/review_widget_generator.py
# Esperado: 0 (o condicional)

# D6: No más example.com
grep -c "example.com" modules/asset_generation/org_schema_generator.py
# Esperado: 0
```

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md` → FASE-BUGFIXES ✅
2. `06-checklist-implementacion.md` → tareas [x]
3. `09-documentacion-post-proyecto.md` → Sección A/D
4. `log_phase_completion.py --fase FASE-BUGFIXES`
5. `./venv/Scripts/python.exe scripts/doctor.py --status`

## Criterios de Completitud

- [ ] D4: "detected_via_html" eliminado del código
- [ ] D5: "Excelente servicio" no hardcodeado
- [ ] D6: "example.com" eliminado
- [ ] D7: Propuesta verifica existencia de archivos
- [ ] No modifica archivos de FASE-PERSONALIZATION
- [ ] Tests pasan
- [ ] Documentación actualizada
