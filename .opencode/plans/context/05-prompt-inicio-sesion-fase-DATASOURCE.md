# FASE-DATASOURCE — Corrección de Datos Fuente (coords, región, teléfono, GBP)

**ID**: FASE-DATASOURCE  
**Objetivo**: Corregir extracción de datos fuente — coordenadas GPS, región, teléfono, validación GBP  
**Dependencias**: Ninguna (raíz)  
**Duración estimada**: 2-3 horas  
**Skill**: systematic-debugging  

---

## Contexto del Problema

La ejecución v4complete para **Amazilia Hotel** (https://amaziliahotel.com/) generó assets CON DATOS FALSOS:
- Coordenadas GPS: "40.7128", "-74.0060" (New York City) — el hotel está en Pereira, Colombia (~4.81°N, -75.69°W)
- Región: "nacional" — debe ser "Pereira" o "Eje Cafetero"
- Teléfono: null en audit_report — el sitio tiene tel:3104019049
- GBP: "Amaziliahotel, Colombia: búsqueda de hoteles de Google" — esto es resultado de búsqueda, NO perfil real

### Evidencia en Archivos
```
Directorio base: /mnt/c/Users/Jhond/Github/iah-cli
Contexto: .opencode/plans/context/AUDIT-AMAZILIA-2026-04-14.md
Assets generados: output/v4_complete/amaziliahotel/
```

### Hallazgos a Corregir
| ID | Problema | Evidencia |
|----|----------|-----------|
| D1 | Coordenadas GPS falsas | `grep "40.7128" output/v4_complete/amaziliahotel/hotel_schema/*.json` → 5 matches |
| D3 | Región "nacional" | grep "nacional" en diagnostico y propuesta |
| D9 | Teléfono no capturado | audit_report.json: phone_web = null |
| D12 | GBP inválido | name = "Amaziliahotel, Colombia: búsqueda..." (resultado búsqueda, no perfil) |

---

## Tarea 1: D1 — Corrección de Coordenadas GPS

### Problema
hotel_schema_generator usa coordenadas hardcodeadas de NYC (40.7128, -74.0060) en lugar de extraerlas del sitio o标记为pendiente.

### Archivos a Modificar
- `modules/asset_generation/hotel_schema_generator.py`
- `modules/geo_enrichment/geo_enrichment_layer.py` (si aplica)

### Pasos
1. Buscar dónde están las coordenadas hardcodeadas:
   ```bash
   grep -rn "40.7128\|-74.0060" modules/ --include="*.py"
   ```
2. Modificar para:
   - Si GBP/geo data tiene coordenadas válidas de Colombia → usar esas
   - Si region = "Pereira" o similar → usar coordenadas aproximadas de Pereira (~4.81°N, -75.69°W)
   - Si no hay datos → marcar como PENDIENTE_ONBOARDING con null
3. NO hardcodear NYC nunca

### Criterio de Éxito
```bash
# Después del fix, verificar:
grep "40.7128\|-74.0060" output/v4_complete/amaziliahotel/hotel_schema/*.json
# Debe devolver: no matches
```

---

## Tarea 2: D3 — Corrección de Detección de Región

### Problema
El detector de región devuelve "nacional" cuando el sitio tiene "Pereira" 10 veces, "Eje Cafetero" 2 veces, "Risaralda" 2 veces.

### Archivos a Modificar
- `modules/orchestration_v4/` (region detector)
- `main.py` (~línea 1511)

### Pasos
1. Buscar el region detector:
   ```bash
   grep -rn "nacional" modules/ --include="*.py" -l
   ```
2. Modificar para priorizar regiones pequeñas (ciudad > departamento > país)
3. Pereira, Risaralda, Eje Cafetero = región LOCAL, no "nacional"

### Criterio de Éxito
- audit_report.json muestra region = "Pereira" o "Eje Cafetero"
- No "nacional"

---

## Tarea 3: D9 — Captura de Teléfono

### Problema
audit_report.json muestra phone_web = null. El sitio HTML tiene `tel:3104019049` en 2 lugares.

### Archivos a Modificar
- `modules/auditors/web_auditor.py`
- `modules/auditors/seo_elements_auditor.py`

### Pasos
1. Buscar parser de teléfonos:
   ```bash
   grep -rn "tel:" modules/auditors/ --include="*.py" -l
   ```
2. Agregar soporte para formato `tel:+XXXXXXXXXXX` y `tel:XXXXXXXXXX`
3. Extraer +57 3104019049 del HTML

### Criterio de Éxito
```bash
# Después del fix:
# audit_report.json: phone_web = "+57 3104019049" (no null)
```

---

### D12 — Validación GBP

### Problema
GBP auditor busca "amaziliahotel" pero el nombre real en Google Maps es **"Amazilia Hotel"**. El resultado "Amaziliahotel, Colombia: búsqueda de hoteles de Google" es un resultado de búsqueda, no un perfil real.

### Query Correcta para Google Maps
```
"Amazilia Hotel" Pereira, Colombia
```

### Archivos a Modificar
- `modules/auditors/gbp_auditor.py` o similar
- `modules/providers/benchmark_resolver.py`

### Pasos
1. Buscar dónde se hace la query GBP:
   ```bash
   grep -rn "amaziliahotel\|Amazilia" modules/auditors/ --include="*.py" -l
   ```
2. Modificar la query de búsqueda para usar "Amazilia Hotel" en lugar de "amaziliahotel"
3. Validar que el resultado es un perfil real (contiene dirección, horas, fotos) y no un resultado de búsqueda
4. Si el resultado contiene "búsqueda de" o "search results" → rechazar como inválido

### Criterio de Éxito
```python
# GBP query usa "Amazilia Hotel" (no "amaziliahotel")
# GBP result con "búsqueda" → status = "unavailable"
# geo_score refleja datos reales o "unavailable"
```

---

## Validación

### Tests Obligatorios
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe -m pytest tests/ -v -k "coords or region or phone or gbp" --tb=short
```

### Verificación Manual
```bash
# D1: Coordenadas
grep -c "40.7128" output/v4_complete/amaziliahotel/hotel_schema/*.json
# Esperado: 0

# D3: Región
grep -n "nacional" output/v4_complete/01_DIAGNOSTICO*.md
grep -n "nacional" output/v4_complete/02_PROPUESTA*.md
# Esperado: 0 matches (o solo "Eje Cafetero" que NO es "nacional")

# D9: Teléfono
# Verificar en audit_report.json: phone_web no es null

# D12: GBP
# GBP status = "unavailable" o similar (no "verified" con rating 0.0)
```

---

## Post-Ejecución (OBLIGATORIO)

1. **Actualizar `.opencode/plans/context/dependencias-fases.md`**:
   - FASE-DATASOURCE = ✅ Completada
   - Fecha de finalización

2. **Actualizar `.opencode/plans/context/06-checklist-implementacion.md`**:
   - Todas las tareas de FASE-DATASOURCE marcadas [x]

3. **Actualizar `.opencode/plans/context/09-documentacion-post-proyecto.md`**:
   - Sección A: módulos nuevos
   - Sección D: métricas
   - Sección E: archivos modificados

4. **Registrar en REGISTRY.md**:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-DATASOURCE \
       --desc "Corrección datos fuente: coords, región, teléfono, GBP" \
       --archivos-mod "modules/asset_generation/hotel_schema_generator.py,modules/auditors/web_auditor.py,modules/auditors/gbp_auditor.py" \
       --check-manual-docs
   ```

---

## Criterios de Completitud

- [ ] D1: `grep "40.7128" modules/` → 0 matches
- [ ] D3: Región = "Pereira" o "Eje Cafetero" (no "nacional")
- [ ] D9: phone_web no es null
- [ ] D12: GBP inválido rechazado
- [ ] Tests pasan
- [ ] dependencias-fases.md actualizado
- [ ] 06-checklist-implementacion.md actualizado
- [ ] 09-documentacion-post-proyecto.md actualizado
- [ ] REGISTRY.md actualizado con log_phase_completion.py
