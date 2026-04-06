# CAUSA RAÍZ: WhatsApp Button No Se Genera (FASE-H-01)

## Resumen Ejecutivo

El asset `whatsapp_button` no se genera cuando hay conflicto de números WhatsApp entre web y GBP. El diagnóstico completo de la cadena de flujo revela múltiples puntos de control pero el código de detección de conflicto SÍ funciona correctamente. El problema está en cómo se usa el resultado en el orchestrator de assets.

---

## Flujo Completo de Detección (Verificado)

### Paso 1: CrossValidator Valida WhatsApp
**Archivo**: `modules/data_validation/cross_validator.py` (líneas 123-159)

```
validate_whatsapp(web_value, gbp_value)
    → normaliza números con normalize_phone_number()
    → crea DataPoint con múltiples fuentes
    → DataPoint.recalculate() calcula match_percentage
    → si match < 70% con 2+ fuentes → confidence = CONFLICT
```

**Veredicto**: ✅ FUNCIONA - Detecta CONFLICT correctamente cuando números difieren.

### Paso 2: Auditor Almacena Resultado
**Archivo**: `modules/auditors/v4_comprehensive.py` (líneas 975-987)

```python
return CrossValidationResult(
    whatsapp_status=whatsapp_dp.confidence.value,  # "conflict"
    phone_web=web_phone,
    phone_gbp=gbp_phone,
    validated_fields={
        "whatsapp": whatsapp_dp.to_dict()  # NOTE: key es "whatsapp" NO "whatsapp_number"
    }
)
```

**Veredicto**: ✅ FUNCIONA - Almacena el estado conflict.

### Paso 3: main.py Construye ValidationSummary
**Archivo**: `main.py` (líneas 1695-1722)

```python
# WhatsApp field (verificado cruzando Web + GBP)
if whatsapp_validation and whatsapp_validation.confidence == ConfidenceLevel.VERIFIED:
    validated_fields.append(ValidatedField(
        field_name="whatsapp_number",  # NOTE: usa "whatsapp_number"
        ...
    ))
elif whatsapp_validation and whatsapp_validation.confidence == ConfidenceLevel.CONFLICT:
    validated_fields.append(ValidatedField(
        field_name="whatsapp_number",
        confidence=ConfidenceLevel.CONFLICT,  # ✅ CONFLICT propagado
        ...
    ))
elif whatsapp_web:
    # Solo web, sin GBP
    validated_fields.append(ValidatedField(
        field_name="whatsapp_number",
        confidence=ConfidenceLevel.ESTIMATED,
        ...
    ))
```

**Veredicto**: ✅ FUNCIONA - Crea ValidatedField con "whatsapp_number" y CONFLICT.

### Paso 4: PainSolutionMapper.detect_pains()
**Archivo**: `modules/commercial_documents/pain_solution_mapper.py` (líneas 230-253)

```python
whatsapp_field = validation_summary.get_field("whatsapp_number")
if not whatsapp_field or whatsapp_field.confidence in (ConfidenceLevel.UNKNOWN, ConfidenceLevel.CONFLICT):
    # Agrega pain "no_whatsapp_visible" ⚠️
    pains.append(Pain(id="no_whatsapp_visible", ...))

# Check for WhatsApp conflict (different numbers in web vs GBP)
if whatsapp_field and whatsapp_field.confidence == ConfidenceLevel.CONFLICT:
    pains.append(Pain(
        id="whatsapp_conflict",  # ✅ Este pain SÍ se crea
        name="Conflicto de WhatsApp",
        ...
    ))
```

**Veredicto**: ✅ FUNCIONA - Crea Pain("whatsapp_conflict").

### Paso 5: generate_asset_plan() y Special Case
**Archivo**: `modules/commercial_documents/pain_solution_mapper.py` (líneas 456-521)

```python
# Special case: whatsapp_conflict always generates whatsapp_button
# because the conflict itself justifies the asset as solution
if pain_id == "whatsapp_conflict":
    can_generate = True  # ✅ Special case existe
```

**Veredicto**: ✅ FUNCIONA - Special case existe y fuerza can_generate=True.

---

## HALLAZGO CRÍTICO: Asset Catalog Desconectado

### Problema en asset_catalog.py

**Archivo**: `modules/asset_generation/asset_catalog.py` (línea 54-64)

```python
"whatsapp_button": AssetCatalogEntry(
    asset_type="whatsapp_button",
    required_field="whatsapp",  # ⚠️ Diferente de lo que usa PainSolutionMapper
    required_confidence=0.7,
    promised_by=["no_whatsapp_visible"]  # ⚠️ NO incluye "whatsapp_conflict"
)
```

**Problema 1**: `required_field="whatsapp"` vs PainSolutionMapper usa `"whatsapp_number"`. Esta不一致 no debería afectar porque el special case fuerza can_generate=True.

**Problema 2**: `promised_by=["no_whatsapp_visible"]` NO incluye `"whatsapp_conflict"`. Esto indica que el asset fue diseñado para el dolor "no_whatsapp_visible" pero el special case permite que también se genere para "whatsapp_conflict".

---

## Verificación de Campo "whatsapp_number" vs "whatsapp"

| Módulo | Campo Usado | Ubicación |
|--------|-------------|-----------|
| PainSolutionMapper.detect_pains() | "whatsapp_number" | línea 233 |
| main.py ValidationSummary | "whatsapp_number" | línea 1698 |
| V4ComprehensiveAuditor | "whatsapp" (en validated_fields) | línea 984 |
| Asset Catalog | "whatsapp" (required_field) | línea 58 |
| Tests | "whatsapp" | línea 289, 315, 337 |

**Inconsistencia**: Los tests y el auditor usan `"whatsapp"` pero main.py y PainSolutionMapper usan `"whatsapp_number"`. Esto funciona por ahora porque PainSolutionMapper busca en validation_summary.fields que construye main.py con "whatsapp_number".

---

## Comandos de Verificación

### Verificar que el conflicto se detecta:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python -c "
from modules.data_validation import CrossValidator, ConfidenceLevel
validator = CrossValidator()
# Simular conflicto
validator.add_scraped_data('whatsapp', '3000000000')
validator.add_gbp_data('whatsapp', '3113973744')
dp = validator.get_validated_field('whatsapp')
print(f'Confidence: {dp.confidence}')
print(f'Value: {dp.value}')
print(f'Match: {dp._validation_result.match_percentage}')
"
# Expected: Confidence: ConfidenceLevel.CONFLICT
```

### Verificar que PainSolutionMapper detecta whatsapp_conflict:
```bash
python -c "
from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper
from modules.commercial_documents.data_structures import ValidationSummary, ValidatedField, ConfidenceLevel

mapper = PainSolutionMapper()
validation_summary = ValidationSummary(
    fields=[
        ValidatedField(
            field_name='whatsapp_number',
            value='3000000000',
            confidence=ConfidenceLevel.CONFLICT,
            sources=['Web', 'GBP'],
            match_percentage=0.0
        )
    ],
    overall_confidence=ConfidenceLevel.CONFLICT
)

pains = mapper.detect_pains(None, validation_summary)
print('Pains detectados:')
for p in pains:
    print(f'  - {p.id}: {p.name}')
"
# Expected: Debería listar whatsapp_conflict
```

---

## Causa Raíz Identificada

**Punto donde se corta la cadena**: No se corta - la cadena funciona completa.

**El problema real** está en la **verificación post-generación** o en **cómo el orchestrator procesa el special case**.

### Hipótesis (requiere verificación):
1. El orchestrator puede estar filtrando assets basados en `is_asset_implemented()` antes de verificar `can_generate`
2. El asset puede generarse pero fallar en validación de contenido
3. El special case puede no ejecutarse si `pain_id` no coincide exactamente con "whatsapp_conflict"

---

## Archivos Verificados

| Archivo | Estado |
|---------|--------|
| `modules/data_validation/cross_validator.py` | ✅ Sin problemas |
| `modules/data_validation/confidence_taxonomy.py` | ✅ Sin problemas |
| `modules/auditors/v4_comprehensive.py` | ✅ Sin problemas |
| `modules/commercial_documents/pain_solution_mapper.py` | ✅ Special case existe (línea 491) |
| `modules/asset_generation/asset_catalog.py` | ⚠️ promised_by incompleto |
| `main.py` | ✅ Construcción correcta |

---

## Recomendación

El special case en `get_assets_for_pain()` línea 491-492 debe funcionar. Para confirmar que el asset se planifica:

1. Agregar logging en `generate_asset_plan()` para verificar que whatsapp_conflict produce whatsapp_button
2. Verificar que el orchestrator usa `can_generate=True` del special case
3. Actualizar `promised_by` en asset_catalog para incluir "whatsapp_conflict"

---

*Documento creado: 2026-03-26*
*FASE-H-01: Diagnóstico Causa Raíz WhatsApp*
