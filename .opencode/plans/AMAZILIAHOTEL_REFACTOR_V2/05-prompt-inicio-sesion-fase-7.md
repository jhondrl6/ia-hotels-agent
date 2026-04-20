# FASE-7: Fix Capitalización de Region en Proposal Generator
**Proyecto**: Amaziliahotel E2E Refactor v2
**Anterior**: Ninguna (FASE-7 es independiente)
**Siguiente**: FASE-8

---

## Contexto

**G13 (MEDIO)**: "eje_cafetero" aparece en lowercase en la propuesta.

**Hallazgo post-forense (crítico)**:
- La string "eje_cafetero" NO está hardcodeada en `v4_proposal_generator.py`
- El origen: `_infer_region_from_address()` en `main.py` produce regiones en lowercase (ej: "eje_cafetero")
- El `v4_diagnostic_generator.py` SÍ convierte a Title Case (ya corregido)
- El `v4_proposal_generator.py` NO sanitiza — pasa la región tal como llega
- "COP COP" ya debe estar resuelto por FASE-3 (scrubber activado). Si persiste, es bug en FASE-3.

**NOTA**: Si FASE-3 se ejecutó correctamente, G14 ("COP COP") ya está resuelto. Esta fase SOLO trata G13 (capitalización).

---

## Tareas de la Fase

### 1. Verificar el data flow de la región

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Origen: cómo se infiere la región
grep -n "_infer_region_from_address\|region.*lower\|eje_cafetero" main.py | head -10

# Cómo llega al proposal generator
grep -n "region\|hotel_region\|eje" modules/commercial_documents/v4_proposal_generator.py | head -15

# Verificar que el diagnostic generator SÍ sanitiza (referencia)
grep -n "title()\|\.title\|capitalize\|Eje Cafetero" modules/commercial_documents/v4_diagnostic_generator.py | head -10
```

### 2. Implementar Fix

**Enfoque**: Agregar sanitización `.title()` en el proposal generator donde se usa la región:

```python
# En v4_proposal_generator.py, donde se inserta la región en el template:
# ANTES (MAL)
region = audit_data.get("region", "")  # "eje_cafetero"

# DESPUÉS (CORRECTO)
region_raw = audit_data.get("region", "")
region = region_raw.replace("_", " ").title()  # "eje_cafetero" → "Eje Cafetero"
```

**Alternativa más robusta** (si hay múltiples sitios donde se usa):
- Sanitizar al inicio del método `generate()` o `_populate_template()`
- Aplicar `.replace("_", " ").title()` una sola vez
- Usar esa variable sanitizada en todo el template

### 3. Verificar COP COP (confirmar FASE-3)

```bash
# Si FASE-3 se ejecutó, esto debe dar 0
grep -c "COP COP" outputs/amaziliahotel.com/propuesta.md 2>/dev/null || echo "0"

# Si es > 0, FASE-3 falló — NO intentar parchear aquí
# (reportar como bug en FASE-3)
```

### 4. Verificar fix

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Verificar que no hay "eje_cafetero" en propuesta generada
grep -c "eje_cafetero" outputs/amaziliahotel.com/propuesta.md 2>/dev/null || echo "0"

# Verificar que "Eje Cafetero" SÍ aparece con mayúsculas
grep "Eje Cafetero" outputs/amaziliahotel.com/propuesta.md | head -5
```

---

## Post-Ejecución

### Checklist de completitud

- [ ] Region sanitizada con `.title()` en proposal generator
- [ ] "eje_cafetero" = 0 en propuesta (reemplazado por "Eje Cafetero")
- [ ] "COP COP" = 0 en propuesta (confirmar FASE-3)
- [ ] Propuesta legible con capitalización correcta
- [ ] Tests pasando: `pytest tests/commercial_documents/ -v -k "proposal or region"`

### Actualizar estado

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-7 \
    --desc "Fix capitalización región — .title() en proposal generator para eje_cafetero → Eje Cafetero" \
    --archivos-mod "modules/commercial_documents/v4_proposal_generator.py" \
    --tests "2" \
    --check-manual-docs
```

---

## Criterios de Aprobación

| Criterio | Estado |
|----------|--------|
| "eje_cafetero" = 0 en propuesta | [ ] |
| "Eje Cafetero" con mayúsculas correctas | [ ] |
| "COP COP" = 0 (confirmar FASE-3) | [ ] |
| Tests pasando | [ ] |
