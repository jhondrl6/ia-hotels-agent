# Prompt: FASE-H-06 - Fix WhatsApp Phone Validation

## Proyecto: iah-cli | hotelvisperas.com
## Fecha: 2026-03-26

---

## Pre-requisito

**FASE-H-05 DEBE estar completada y documentada.**

---

## Contexto

El validador `AssetContentValidator` tiene un regex `\+57\d{10}` que detecta números de teléfono reales de Colombia (ej: `+573005551234`) como placeholders. Esto causa que `whatsapp_button` sea bloqueado aunque el número sea válido y el asset se genere correctamente.

**Error observado:**
```
Asset failure (whatsapp_button): Content validation failed: placeholder: Placeholder detected: \+57\\d{10}
```

---

## Tareas de FASE-H-06

### 1. Analizar el problema

Revisar `modules/asset_generation/asset_content_validator.py` líneas 48-66:

```python
PLACEHOLDER_PATTERNS = [
    # Phone placeholders
    r'\+57XXX',  # +57XXX literally
    r'\+57\d{10}',  # +57 followed by exactly 10 digits (not masked)
    ...
]
```

El regex `\+57\d{10}` coincide con cualquier número que empiece en +57 seguido de exactamente 10 dígitos - incluyendo números reales como `+573005551234`.

### 2. Determinar la solución

Opciones:
1. **Modificar el regex** para solo detectar placeholders obvios como `+57XXX` o `+57 XXX XXX XXXX`
2. **Agregar excepción** para contenido que proviene de `whatsapp_button` (verificar contexto)
3. **Cambiar el approach** - el HTML del botón WhatsApp se genera en `_generate_whatsapp_button()` - NO debe ser validado como contenido de usuario

### 3. Implementar el fix

Opción recomendada: Modificar el regex para detectar solo placeholders obvios:

```python
r'\+57XXX',  # +57XXX literally (placeholder)
r'\+57\s*XXX\s*XXX\s*XXX',  # +57 XXX XXX XXX (placeholder with spaces)
# ELIMINAR: r'\+57\d{10}'  # Esto rechaza números reales
```

### 4. Verificar

Después del fix, ejecutar:
```bash
python main.py v4complete --url https://www.hotelvisperas.com/es --nombre "Hotel Vísperas" --debug
```

Verificar que:
- `whatsapp_button` ya NO aparece en "Fallidos"
- El asset está en `ASSETS/whatsapp_button/` del delivery

### 5. Ejecutar pytest

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/asset_generation/ -v
```

---

## Criterio de Completitud

- [ ] Regex modificado en `asset_content_validator.py`
- [ ] Tests de regresión pasando
- [ ] `whatsapp_button` pasa validación y se incluye en delivery
- [ ] Documentación del fix en `FIXES_APPLIED.md`

---

## Post-Ejecución

### 1. Documentar en `FIXES_APPLIED.md`
### 2. Actualizar `06-checklist-GAPS-V4COMPLETE.md`
### 3. Proceder a FASE-H-07

---

*Prompt creado: 2026-03-26*
*Depende de: FASE-H-05*
