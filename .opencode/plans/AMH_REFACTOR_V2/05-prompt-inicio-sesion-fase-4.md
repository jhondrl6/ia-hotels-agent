# FASE-4: Fix ROI — Eliminar "24X" hardcodeado del template V6
**Proyecto**: Amaziliahotel E2E Refactor v2
**Anterior**: Ninguna (FASE-4 es independiente — NO depende de FASE-3)
**Siguiente**: Cualquiera

---

## Contexto

**G10 (CRÍTICO)**: El ROI mostrado en la propuesta es incorrecto/confuso.

**Hallazgo post-forense (crítico)**:
- NO existe el concepto "Tier A/B/C" en el codebase. El determinador de paquetes usa basic/avanzado/premium.
- `_calculate_roi()` en `v4_proposal_generator.py` (~línea 707) calcula ROI dinámicamente: `roi_ratio = total_gain / total_investment` → `f"{roi_ratio:.1f}X"`
- **PERO**: El template V6 (`propuesta_v6_template.md`, ~línea 105) tiene hardcodeado: `(24X en 6 meses)` junto a la variable `${roi_6m}`
- Resultado: la propuesta muestra algo como `**ROI: 3.9X** (24X en 6 meses)` — DOS números distintos
- El ROI dinámico NO tiene en cuenta GA4 (no hay awareness de GA4 en el cálculo)

**El problema real**: No es "Tier C dice 20X cuando debe ser 3X". Es que el template tiene un número fijo al lado del dinámico.

---

## Tareas de la Fase

### 1. Verificar el template V6

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Ver el hardcoded en el template
grep -n "24X\|20X\|roi\|ROI" modules/commercial_documents/templates/propuesta_v6_template.md
```

### 2. Verificar el cálculo dinámico

```bash
# Ver cómo se calcula el ROI real
grep -n "_calculate_roi\|roi_ratio\|total_gain\|total_investment" \
    modules/commercial_documents/v4_proposal_generator.py | head -15
```

### 3. Implementar Fix

**3a. Template V6**: Eliminar "(24X en 6 meses)" hardcodeado y usar solo la variable dinámica:

```bash
# ANTES (en template):
# **ROI: ${roi_6m}** (24X en 6 meses)

# DESPUÉS:
# **ROI: ${roi_6m}** en 6 meses
```

Buscar todas las instancias de números hardcodeados en el template:

```bash
grep -n "[0-9]\+X" modules/commercial_documents/templates/propuesta_v6_template.md
```

**3b. v4_proposal_generator.py**: Si hay variables `${roi_6m}` y `${roi_12m}`, verificar que se calculan correctamente sin hardcodes:

```bash
grep -n "roi_6m\|roi_12m\|roi_6\|roi_12" modules/commercial_documents/v4_proposal_generator.py
```

### 4. Verificar fix

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# El template NO debe tener "24X" hardcodeado
grep "24X\|20X" modules/commercial_documents/templates/propuesta_v6_template.md || echo "OK: Sin hardcoded ROI"

# Generar propuesta y verificar que muestra un solo ROI consistente
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ 2>&1 | tail -30

# Verificar ROI en propuesta generada
grep -E "ROI|[0-9]+X" outputs/amaziliahotel.com/propuesta.md | head -10
```

**Criterio**: Propuesta debe mostrar un SOLO número de ROI (el dinámico), sin "(24X en 6 meses)".

---

## Post-Ejecución

### Checklist de completitud

- [ ] Template V6 sin "24X" ni otros ROI hardcodeados
- [ ] ROI en propuesta = valor dinámico calculado (un solo número)
- [ ] No hay confusión "3.9X (24X en 6 meses)"
- [ ] Tests pasando: `pytest tests/commercial_documents/ -v -k "roi or ROI or proposal"`
- [ ] Sin regresiones en financial_engine

### Actualizar estado

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-4 \
    --desc "Fix ROI — eliminar 24X hardcodeado de template V6, usar solo cálculo dinámico" \
    --archivos-mod "modules/commercial_documents/templates/propuesta_v6_template.md,modules/commercial_documents/v4_proposal_generator.py" \
    --tests "4" \
    --check-manual-docs
```

---

## Criterios de Aprobación

| Criterio | Estado |
|----------|--------|
| Template V6 sin "24X" hardcodeado | [ ] |
| Propuesta muestra un solo ROI (dinámico) | [ ] |
| No hay números de ROI contradictorios | [ ] |
| Tests pasando | [ ] |
