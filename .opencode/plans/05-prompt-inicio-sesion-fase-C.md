# Prompt de Inicio de Sesion — FASE-C: Regional Template Fixes

## Contexto

### Documento de referencia
`/mnt/c/Users/Jhond/Github/iah-cli/.opencode/plans/context/whatsapp_false_positive.md` (seccion "Errores de Consistencia Regional")

### Estado de Fases Anteriores
- FASE-A (WhatsApp Detection Fix): Completada en sesion previa
- FASE-B (Citability Narrative Fix): Completada en sesion previa

### Problema
Dos errores en el template y generador:

1. **Typo `yRevisan`** en `diagnostico_v6_template.md:27` — falta espacio: "Entran a Google yRevisan 5 webs"
2. **Fallback regional generico** en `v4_diagnostic_generator.py:1627` — "La region de Nacional en Colombia" cuando la region no esta en el mapping
3. **Region "Eje Cafetero" no esta en el mapping** (solo: cartagena, medellin, bogota, cali, barranquilla, santa marta)

---

## Objetivo

Corregir los 3 errores para que futuras generaciones del diagnostico no tengan:
- Typo "yRevisan"
- "La region de Nacional en Colombia" para regiones no mapeadas

---

## Tareas

### T1: Corregir typo yRevisan

**Archivo:** `modules/commercial_documents/templates/diagnostico_v6_template.md` (linea 27)

```markdown
# ANTES:
| Entran a Google yRevisan 5 webs | Le preguntan a ChatGPT: "¿Hotel boutique en ${hotel_region}?" |

# DESPUES:
| Entran a Google y revisan 5 webs | Le preguntan a ChatGPT: "¿Hotel boutique en ${hotel_region}?" |
```

### T2: Agregar Eje Cafetero al mapping regional

**Archivo:** `modules/commercial_documents/v4_diagnostic_generator.py` (lineas 1613-1620)

Agregar al diccionario `region_contexts`:
```python
"eje cafetero": "El Eje Cafetero (Caldas, Quindío, Risaralda) es una de las principales regiones cafeteras del mundo y un destino turístico en crecimiento. Los viajeros buscan experiencias auténticas de naturaleza, café y cultura. La presencia digital hotelera es clave para captar tanto turismo nacional como internacional.",
```

Tambien considerar agregar otras regiones comunes faltantes:
- "san andres"
- "llanos orientales"
- "costa atlantica" (alias para barranquilla area)

### T3: Corregir fallback regional generico

**Archivo:** `modules/commercial_documents/v4_diagnostic_generator.py` (linea 1627)

Cambiar el fallback para que no diga "La region de {region}" cuando region es un nombre generico:

```python
# ANTES:
return f"La región de {region} en Colombia presenta oportunidades de crecimiento en presencia digital hotelera."

# DESPUES:
region_display = region if region and region.lower() not in ("nacional", "colombia", "general", "") else "esta zona"
return f"{region_display} en Colombia presenta oportunidades de crecimiento en presencia digital hotelera."
```

### T4: Verificar hotel_region fallback en linea 413

**Archivo:** `modules/commercial_documents/v4_diagnostic_generator.py` (linea 413)

```python
hotel_region = region or "Colombia"
```

Esto esta correcto — "Colombia" es fallback razonable. Solo verificar que el flujo downstream (T3) lo maneja bien.

---

## Criterios de Completitud

- [ ] Typo `yRevisan` corregido en template
- [ ] "Eje Cafetero" en el mapping de `region_contexts`
- [ ] Fallback no genera "La region de Nacional" para valores genericos
- [ ] Template sin placeholders rotos
- [ ] Tests existentes pasan

---

## Archivos a Modificar

| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Typo linea 27 |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Lines 1613-1620 (mapping), 1627 (fallback) |

## Post-Ejecucion

- Marcar checklist en `06-checklist-implementacion.md`
- Ejecutar `log_phase_completion.py --fase FASE-C`
- Actualizar `09-documentacion-post-proyecto.md`

## Evidence

```bash
mkdir -p evidence/fase-c
./venv/Scripts/python.exe -m pytest tests/commercial_documents/ tests/asset_generation/ -v --tb=short 2>&1 | tee evidence/fase-c/regression_pre.log
```
