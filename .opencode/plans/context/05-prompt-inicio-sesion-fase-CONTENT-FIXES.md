# FASE-CONTENT-FIXES — Corrección de Contenido Específico en Assets

**ID**: FASE-CONTENT-FIXES  
**Objetivo**: Corregir contenido incorrecto en optimization_guide, monthly_report, y llms_txt  
**Dependencias**: FASE-PERSONALIZATION  
**Duración estimada**: 1-2 horas  
**Skill**: systematic-debugging  

---

## Contexto del Problema

Esta fase corrige contenido específico que contradice o no representa la realidad del sitio.

### Hallazgos a Corregir
| ID | Problema | Evidencia |
|----|----------|-----------|
| D8 | optimization_guide se contradice | "Sin title tag configurado" → luego "Title tag personalizado detectado" |
| GAP-2 | monthly_report usa "Hotel" genérico | ASSET_monthly_report.md línea 4: `**Hotel**: Hotel` |
| GAP-3 | llms_txt genérico sin datos reales | Solo dice "hotel boutique ubicado en Colombia" sin mencionar spa, Pereira, Eje Cafetero |

---

## Tarea 1: D8 — Fix optimization_guide Contradiciones

### Problema
optimization_guide_generator produce documento que dice:
- Línea A: "Sin title tag configurado"
- Línea B: "Title tag personalizado detectado"

Estas contradicciones indican que el generator no está procesando correctamente los datos del audit.

### Archivo a Modificar
- `modules/asset_generation/optimization_guide_generator.py`

### Pasos
1. Buscar el generator y las contradicciones:
   ```bash
   grep -n "title tag\|meta description" modules/asset_generation/optimization_guide_generator.py
   ```

2. Examinar cómo obtiene los datos de SEO:
   ```bash
   grep -n "has_default_title\|has_default_description\|audit" modules/asset_generation/optimization_guide_generator.py
   ```

3. El problema: probablemente usa `has_default_title = false` (el sitio NO tiene title por defecto) y luego `has_default_title = true` (detecta title en algún lugar). Unificar lógica.

4. Fix: Si `has_default_title = false` significa "NO hay title tag personalizado", usar ese estado consistentemente. No cambiar arbitrariamente.

### Criterio de Éxito
```bash
# Verificar que el documento generado NO se contradice
grep -A2 -B2 "title tag\|meta description" output/v4_complete/amaziliahotel/optimization_guide/*.md
# Esperado: CONSISTENCIA (si dice "Sin title", no debe luego decir "Title configurado")
```

---

## Tarea 2: GAP-2 — Fix monthly_report "Hotel" Genérico

### Problema
monthly_report_generator produce:
```markdown
**Hotel**: Hotel
```

Cuando debería usar "Amazilia" o "Amaziliahotel" del audit_report.

### Archivo a Modificar
- `modules/asset_generation/monthly_report_generator.py`

### Pasos
1. Buscar el generator:
   ```bash
   grep -n "Hotel\|hotel_name\|name" modules/asset_generation/monthly_report_generator.py
   ```

2. Modificar para usar `audit_report["name"]` si está disponible:
   ```python
   hotel_name = "Hotel"  # Antes: hardcodeado
   if audit_report and audit_report.get("name"):
       hotel_name = audit_report["name"]  # Ahora: del audit
   ```

3. Si no hay audit_report → usar "Hotel" como fallback (aceptable para plantillas genéricas).

### Criterio de Éxito
```bash
grep "Hotel:" output/v4_complete/amaziliahotel/monthly_report/*.md
# Esperado: "Hotel: Amazilia" o similar (NO solo "Hotel")

# Verificar que NO dice literalmente solo "Hotel" como nombre
grep -E "\*\*Hotel\*\*: Hotel$" output/v4_complete/amaziliahotel/monthly_report/*.md
# Esperado: 0 matches
```

---

## Tarea 3: GAP-3 — Fix llms_txt Genérico

### Problema
llms_txt dice solo "hotel boutique ubicado en Colombia" sin usar los datos reales del sitio:
- spa (300 referencias en HTML)
- Pereira (10 referencias)
- Eje Cafetero (2 referencias)
- habitaciones (5)
- piscina (2)
- restaurante (2)
- campestre (4)

### Archivo a Modificar
- `modules/asset_generation/llmstxt_generator.py`

### Pasos
1. Buscar el generator:
   ```bash
   grep -n "Colombia\|boutique\|hotel" modules/asset_generation/llmstxt_generator.py
   ```

2. Modificar para incluir contenido del sitio:
   ```python
   # Agregar servicios destacados del hotel
   services = []
   if audit_report and audit_report.get("content_highlights"):
       services = audit_report["content_highlights"]
   
   # Incluir en llms.txt:
   # "Amazilia Hotel Campestre..."
   # "Servicios: {', '.join(services) if services else 'habitaciones, restaurante...'}"
   ```

3. Incluir también región:
   ```python
   region = audit_report.get("region", "Colombia")
   # "...ubicado en {region}..."
   ```

### Criterio de Éxito
```bash
# Verificar contenido real en llms_txt
grep -i "pereira\|spa\|eje cafetero\|habitaciones\|piscina" output/v4_complete/amaziliahotel/llms_txt/*.txt
# Esperado: al menos 2-3 de estos términos mencionados

# Verificar que NO es solo "hotel boutique ubicado en Colombia"
wc -l output/v4_complete/amaziliahotel/llms_txt/*.txt
# Esperado: más de 3 líneas (contenido sustancial)
```

---

## Validación

### Tests Obligatorios
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe -m pytest tests/ -v -k "optimization_guide or monthly_report or llms_txt" --tb=short
```

### Verificación Manual
```bash
# D8: optimization_guide sin contradicciones
# (Inspección visual del contenido)

# GAP-2: monthly_report
grep "Hotel:" output/v4_complete/amaziliahotel/monthly_report/*.md
# Esperado: "Amazilia" no solo "Hotel"

# GAP-3: llms_txt
grep -c "Pereira\|spa\|Eje Cafetero" output/v4_complete/amaziliahotel/llms_txt/*.txt
# Esperado: > 0
```

---

## Post-Ejecución (OBLIGATORIO)

1. **Actualizar `.opencode/plans/context/dependencias-fases.md`**:
   - FASE-CONTENT-FIXES = ✅ Completada
   - Fecha de finalización

2. **Actualizar `.opencode/plans/context/06-checklist-implementacion.md`**:
   - Todas las tareas de FASE-CONTENT-FIXES marcadas [x]

3. **Actualizar `.opencode/plans/context/09-documentacion-post-proyecto.md`**:
   - Sección A: módulos nuevos
   - Sección D: métricas
   - Sección E: archivos modificados

4. **Registrar en REGISTRY.md**:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-CONTENT-FIXES \
       --desc "Fix contenido: optimization_guide, monthly_report, llms_txt" \
       --archivos-mod "modules/asset_generation/optimization_guide_generator.py,modules/asset_generation/monthly_report_generator.py,modules/asset_generation/llmstxt_generator.py" \
       --check-manual-docs
   ```

---

## Criterios de Completitud

- [ ] D8: optimization_guide sin contradicciones
- [ ] GAP-2: monthly_report con nombre real (no solo "Hotel")
- [ ] GAP-3: llms_txt con contenido real del sitio (Pereira, spa, Eje Cafetero)
- [ ] Tests pasan
- [ ] dependencias-fases.md actualizado
- [ ] 06-checklist-implementacion.md actualizado
- [ ] 09-documentacion-post-proyecto.md actualizado
- [ ] REGISTRY.md actualizado
