# CAUSA RAIZ: optimization_guide - Content Validation Failed

## Proyecto: iah-cli | hotelvisperas.com
## Fecha: 2026-03-26
## Diagnostico: FASE-H-03

---

## Error Reportado

```
Content validation failed: placeholder: Placeholder detected: \.\.\.; generic_phrase: Generic phrase detected: 'no configurado'
```

---

## Archivos Involucrados

| Archivo | Rol |
|---------|-----|
| `modules/asset_generation/conditional_generator.py` | Genera el asset optimization_guide |
| `modules/asset_generation/asset_content_validator.py` | Valida el contenido y rechaza placeholders |

---

## Ubicacion Exacta del Problema

**Archivo**: `conditional_generator.py`
**Metodo**: `_generate_optimization_guide()` (lineas 782-975)

### Placeholder "... " (Ellipsis)
- **Patron**: `\.{3}` en `PLACEHOLDER_PATTERNS` (asset_content_validator.py linea 53)
- **Detectado en**: Archivos generados contienen "No configurado..." con ellipsis

### Generic Phrase "no configurado"
- **Lista negra**: `GENERIC_PHRASES` en asset_content_validator.py (lineas 68-74)
- **Terminos rechazados**:
  - 'no configurado'
  - 'por definir'
  - 'pendiente'
  - 'sin especificar'
  - 'sin configurar'

---

## Evidence de Archivos Generados

### Archivo: `ESTIMATED_guia_optimizacion_20260318_190641.md` (lineas 13, 25)
```
|| Valor actual | No configurado |
|| Valor actual | No configurado... |
```

### Archivo: `ESTIMATED_guia_optimizacion_20260321_201334.md` (linea 27)
```
|| Valor actual | No configurado... |
```

---

## Fix BUG-02 de FASE-G (Verificacion)

**Verificado presente** en `conditional_generator.py`:

1. **Linea 854** (fix para meta_description):
```python
{(meta_description[:80] + " (resumen de 80 caracteres)") if meta_description else "⚠️ Sin meta description"}
```

2. **Linea 830** (title tag):
```python
{title_tag if title_tag else "⚠️ Sin title tag configurado"}
```

**PROBLEMA**: El fix esta en el codigo PERO los archivos generados (20260321) todavia contienen "No configurado...". Esto indica que:

1. O el fix no se aplico en el momento de la generacion
2. O hay otra fuente de "No configurado" que no es `meta_description[:80]` ni `title_tag`

---

## Causa Raiz Identificada

El texto "No configurado..." aparece en la tabla de "Valor actual" cuando:

1. `meta_description` es `None` o vacio → genera "⚠️ Sin meta description" (correcto)
2. `title_tag` es `None` o vacio → genera "⚠️ Sin title tag configurado" (correcto)

**Hipotesis**: Los archivos generados con "No configurado..." fueron creados ANTES del fix BUG-02 de FASE-G, o hay datos en `metadata_data` que contienen "no configurado" como string literal.

---

## Proximo Paso (FASE-H-04)

1. Buscar en `conditional_generator.py` donde se origina exactamente el texto "No configurado"
2. Si el fix actual es insuficiente, reemplazar con texto descriptivo que NO este en la lista negra
3. Alternativa: Agregar "No configurado" a una lista de excepciones si es contexto valido

---

## Criterio de Completitud FASE-H-03

- [x] Placeholders localizados: `\.{3}` y lista `GENERIC_PHRASES`
- [x] Lista negra del validator documentada (5 terminos)
- [x] Causa raiz clara: texto "No configurado..." en archivos generados
- [x] Fix BUG-02 verificado presente
- [ ] Checklist actualizado

---

*Documento generado: 2026-03-26*
*Proyecto: iah-cli | hotelvisperas.com*
