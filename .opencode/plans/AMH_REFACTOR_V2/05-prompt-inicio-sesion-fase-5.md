# FASE-5: Fix faq_page → JSON-LD + Fix monthly_report Blanks
**Proyecto**: Amaziliahotel E2E Refactor v2  
**Anterior**: FASE-3 (Content Scrubber)  
**Siguiente**: FASE-6 (WhatsApp/Voice en propuesta)

---

## Contexto

**G4 (CRÍTICO)**: `faq_page` genera `.csv` en vez de JSON-LD.
- El handler en `conditional_generator.py` sigue usando formato antiguo
- El veredicto: "faq_page extensión | .csv | STILL .csv | ❌ NO"

**G7 (CRÍTICO)**: `monthly_report` tiene 27 "_____" blanks.
- Template con placeholders sin rellenar
- Esto bloquea delivery del asset

---

## Tareas de la Fase

### 1. Fix faq_page → JSON-LD

```bash
# Localizar handler de faq_page
grep -n "faq_page\|FAQ\|faq" \
    /mnt/c/Users/Jhond/Github/iah-cli/modules/asset_generation/conditional_generator.py \
    | head -20
```

**Implementar**:
- Generar `faq_page.json` (JSON-LD con `@type: FAQPage`)
- Usar datos reales del audit (`audit_data.faq_questions`)
- Eliminar generación `.csv` antigua

**Formato JSON-LD esperado**:
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "¿Pregunta?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Respuesta"
      }
    }
  ]
}
```

### 2. Fix monthly_report blanks

```bash
# Localizar template
find /mnt/c/Users/Jhond/Github/iah-cli -name "*monthly_report*" -o -name "*report*template*" 2>/dev/null | grep -v __pycache__
```

**Implementar**:
- Reemplazar todos los "_____" con valores reales del audit
- Si el dato no existe, usar "Por confirmar" en lugar de blank

### 3. Verificar ambos fixes

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Verificar faq_page
ls -la outputs/amaziliahotel.com/assets/faq_page.* 2>/dev/null
cat outputs/amaziliahotel.com/assets/faq_page.json 2>/dev/null | head -20

# Verificar monthly_report sin blanks
grep -c "_____" outputs/amaziliahotel.com/assets/monthly_report.md 2>/dev/null || echo "0 blanks"
```

---

## Post-Ejecución

### Checklist de completitud

- [ ] `faq_page.json` existe (JSON-LD)
- [ ] `faq_page.csv` NO existe
- [ ] `monthly_report.md` tiene 0 blanks "_____"
- [ ] Tests pasando: `pytest tests/asset_generation/test_conditional_generator.py -v`
- [ ] Sin regresiones en faq_generator

### Actualizar estado

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-5 \
    --desc "Fix faq_page → JSON-LD + monthly_report sin blanks" \
    --archivos-mod "modules/asset_generation/conditional_generator.py,modules/asset_generation/faq_generator.py" \
    --tests "7" \
    --check-manual-docs
```

---

## Criterios de Aprobación

| Criterio | Estado |
|----------|--------|
| faq_page.json existe (JSON-LD) | [ ] |
| faq_page.csv NO existe | [ ] |
| monthly_report con 0 blanks | [ ] |
| Tests pasando | [ ] |
