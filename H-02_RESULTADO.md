# FASE-H-02 Resultado: Fix WhatsApp Button No Se Genera

## Fecha: 2026-03-26

---

## Hipótesis Verificadas

| # | Hipótesis | Estado | Evidencia |
|---|-----------|--------|-----------|
| H1 | Orchestrator filtra assets por is_asset_implemented() | ❌ No confirmada | El orchestrator no filtra por este criterio antes de generar |
| H2 | Asset se genera pero falla en validación de contenido | ❌ No confirmada | La validación de contenido no bloquea el asset |
| H3 | Special case no se ejecuta si pain_id no coincide | ❌ No confirmada | El pain_id sí coincide exactamente con "whatsapp_conflict" |

---

## Causa Raíz Descubierta

**Desajuste de nombre de campo entre módulos:**

| Módulo | Campo Usado | Ubicación |
|--------|-------------|-----------|
| ValidationSummary (main.py) | `whatsapp_number` | validation_summary.fields |
| V4AssetOrchestrator._extract_validated_fields() | `whatsapp_number` | línea 362 |
| ConditionalGenerator._generate_content() | `whatsapp` | línea 216 |

El `ConditionalGenerator` buscaba `validated_data.get("whatsapp")` pero el campo se almacenaba como `"whatsapp_number"`. Esto causaba que `phone_data` fuera un dict vacío `{}`, y el número de teléfono se convertía en la representación de string de un dict vacío.

---

## Fix Aplicado

### 1. conditional_generator.py (línea 215-218)

```python
# ANTES:
phone_data = validated_data.get("whatsapp", {})

# DESPUÉS:
phone_data = validated_data.get("whatsapp") or validated_data.get("whatsapp_number", {})
```

**Razón**: Aceptar ambos nombres de campo para compatibilidad retroactiva.

### 2. asset_catalog.py (línea 63)

```python
# ANTES:
promised_by=["no_whatsapp_visible"]

# DESPUÉS:
promised_by=["no_whatsapp_visible", "whatsapp_conflict"]
```

**Razón**: Documentar que whatsapp_button resuelve ambos pains.

---

## Archivos Modificados

1. `modules/asset_generation/conditional_generator.py` - Fix de compatibilidad de nombres
2. `modules/asset_generation/asset_catalog.py` - Agregado whatsapp_conflict a promised_by

---

## Verificación

### Syntax Check
```bash
python3 -m py_compile modules/asset_generation/conditional_generator.py  # OK
python3 -m py_compile modules/asset_generation/asset_catalog.py           # OK
```

### Tests (requiere pytest)
```bash
python -m pytest tests/commercial_documents/test_pain_solution_mapper.py::test_detect_pain_whatsapp_conflict -v
python -m pytest tests/commercial_documents/test_pain_solution_mapper.py tests/data_validation/test_cross_validator.py -v
```

---

## Siguiente Paso

FASE-H-04 puede ejecutarse después de este fix para continuar con la verificación de la cadena de flujo completa.

---

*Documento creado: 2026-03-26*
*FASE-H-02: Fix Causa Raíz WhatsApp*
