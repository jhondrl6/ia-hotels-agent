---
description: FASE-CONTENT-SCRUBBER — Fix self-replacement + spacing errors
version: 1.0.0
---

# FASE-CONTENT-SCRUBBER: Fix Content Scrubber — Self-Replacement y Spacing

**ID**: FASE-CONTENT-SCRUBBER  
**Objetivo**: Fix content scrubber para evitar warnings de self-replacement y detectar errores de espaciado  
**Dependencias**: Ninguna (paralela, independiente)  
**Duración estimada**: 1 hora  
**Skill**: `iah-cli-phased-execution`

---

## Contexto

### Problema (R6 + R7 del AUDIT)

```
R6: Content scrubber — evitar self-replacement warnings

"reserva" → "reserva" y "proxima" → "proxima" generan warnings innecesarios.
Agregar check: si old == new, skip.

(NOTA: D7 del AUDIT es "SEO score 10 con datos nulos" — deuda de documentación
del _calculate_web_score, NO es un problema del content scrubber. D7 queda fuera
de esta fase.)

---

R7: Content scrubber — detectar errores de espaciado

"debeproveer" no es error de idioma → content scrubber no lo detecta.
Agregar regex para palabras pegadas (ej: debeproveer → debe prover).
```

### Warnings Actuales del Content Scrubber

```
"Reemplazo: proxima -> proxima"
"Reemplazo: reserva -> reserva"
"Reemplazo: reserva -> reserva"
```

Estos 3 warnings son self-replacement: la palabra se reemplaza por sí misma.

---

## Tareas

### Tarea 1: Fix self-replacement — skip if old == new

**Ubicación**: `modules/postprocessors/document_quality_gate.py`

**Buscar** dónde se ejecutan los reemplazos y agregar check:

```python
# ANTES:
for old, new in replacements:
    content = content.replace(old, new)

# DESPUÉS:
for old, new in replacements:
    if old == new:
        continue  # Skip self-replacement
    if old in content:
        content = content.replace(old, new)
        fixes_applied.append(f"Reemplazo: {old} -> {new}")
    else:
        warnings.append(f"Patrón no encontrado: {old}")
```

---

### Tarea 2: Agregar regex para palabras pegadas

**Problema**: `debeproveer` → el espacio se perdió entre "debe" y "proveer"

**Regex a detectar**:
```python
import re

# Detectar palabras pegadas: dos palabras conocidas unidas sin espacio
# Ej: "debeproveer" → "debe prover"
SPACING_ERRORS = [
    (r'debeproveer', 'debe prover'),
    (r'debeen', 'deben'),  # "debeen" → "deben"
    (r'\bdel(\w{4,})', r'de \1'),  # palabras cortas pegadas
]

# Detectar pero NO auto-corregir (son pocos casos específicos)
```

**Implementación**:
```python
def detect_spacing_errors(content: str) -> List[Dict[str, str]]:
    """Detecta errores de espaciado común sin auto-corregir."""
    errors = []
    
    spacing_patterns = [
        (r'debeproveer', 'debe prover'),
        (r'paramas', 'para más'),
        (r'estees', 'este es'),
    ]
    
    for pattern, correction in spacing_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            for match in matches:
                errors.append({
                    "found": match,
                    "suggested": correction,
                    "type": "spacing_error"
                })
    
    return errors
```

---

### Tarea 3: Integrar en content_quality gate

**Ubicación**: `modules/postprocessors/document_quality_gate.py`

**Agregar** la verificación de spacing errors en el gate de content_quality:

```python
# Detectar errores de espaciado
spacing_errors = detect_spacing_errors(content)

if spacing_errors:
    warnings.append(f"Errores de espaciado detectados: {len(spacing_errors)}")
    for error in spacing_errors:
        details.append(f"  - '{error['found']}' → '{error['suggested']}'")
```

---

### Tarea 4: Tests

**Archivo**: `tests/postprocessors/test_document_quality_gate.py` (o crear si no existe)

**Casos**:
1. `test_skip_self_replacement` — "reserva" → "reserva" no genera warning
2. `test_detect_spacing_errors` — "debeproveer" es detectado
3. `test_content_quality_gate_with_spacing` — gate incluye spacing errors en warnings

---

## Restricciones

- NO modificar lógica de replacement de idioma (español → español)
- Solo fix self-replacement y spacing, no reescribir el scrubber completo
- Los spacing errors se detectan pero NO se auto-corregen (son peligrosos)

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_skip_self_replacement` | `tests/postprocessors/test_document_quality_gate.py` | PASA — sin warning |
| `test_detect_spacing_errors` | `tests/postprocessors/test_document_quality_gate.py` | PASA — detecta |
| `test_content_quality_gate_with_spacing` | `tests/postprocessors/test_document_quality_gate.py` | PASA — incluye en warnings |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/postprocessors/test_document_quality_gate.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Self-replacement fixed**: "proxima" → "proxima" y "reserva" → "reserva" no generan warnings
- [ ] **Spacing errors detected**: "debeproveer" detectado con sugerencia
- [ ] **Tests pasan**: Los 3 tests ejecutan exitosamente
- [ ] **`dependencias-fases.md` actualizado**: FASE-CONTENT-SCRUBBER ✅ Completada

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: Marcar FASE-CONTENT-SCRUBBER como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar Tareas 1-4 como completadas
3. **`09-documentacion-post-proyecto.md`**:
   - Sección E: `modules/postprocessors/document_quality_gate.py` modificado
   - Sección D: Métrica "Self-replacement warnings: 3 → 0"
