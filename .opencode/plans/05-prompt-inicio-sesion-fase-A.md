# Prompt de Inicio de Sesion — FASE-A: WhatsApp Detection Fix

## Contexto

### Documento de referencia
`/mnt/c/Users/Jhond/Github/iah-cli/.opencode/plans/context/whatsapp_false_positive.md`

### Estado de Fases Anteriores
Ninguna — esta es la primera fase del proyecto.

### Problema
El sistema reporta "Sin WhatsApp" para hoteles que SÍ tienen boton de WhatsApp visible en su web. El falso positivo ocurre porque:

1. El scraper (`web_scraper.py:394-409`) tiene `_detectar_whatsapp()` que SI detecta el boton HTML
2. El resultado del scraper (`WHATSAPP_AUSENTE`) NO se consume en ningun otro modulo (confirmado: grep retorna 0 fuera de web_scraper.py)
3. El diagnostico usa `phone_web` que viene SOLO del Schema JSON-LD `telephone` property (v4_comprehensive.py:1029)
4. Si el hotel tiene boton WhatsApp pero no declara `telephone` en Schema → falso positivo

---

## Objetivo

Eliminar el falso positivo de WhatsApp haciendo que el diagnosticador distinga entre:
- "WhatsApp visual" (boton en HTML detectado por scraper) → NO es brecha
- "Telefono en Schema" (telephone en JSON-LD) → info complementaria

---

## Tareas

### T1: Conectar scraper detection al pipeline

**Archivo:** `modules/auditors/v4_comprehensive.py`

El metodo `_run_cross_validation()` (linea 1021) actualmente solo usa `schema.properties.get("telephone")` para `phone_web`. Necesita TAMBIEN recibir el resultado del scraper.

**Accion:**
1. Verificar como `v4_comprehensive.py` obtiene los datos del scraper (buscar donde se llama `web_scraper` o `scraper`)
2. Si `_detectar_whatsapp()` ya se ejecuta durante el scrape, capturar su resultado y pasarlo al cross_validator
3. Agregar campo `whatsapp_html_detected: bool` al `CrossValidationResult` (data_structures.py:184)

### T2: Agregar campo al data structure

**Archivo:** `modules/commercial_documents/data_structures.py`

Agregar a `ValidationSummary` (linea ~184):
```python
whatsapp_html_detected: bool = False  # True si scraper detecto boton WhatsApp en HTML
```

### T3: Actualizar brecha WhatsApp en diagnostic_generator

**Archivo:** `modules/commercial_documents/v4_diagnostic_generator.py`

Cambiar la condicion en linea 1788:
```python
# ANTES:
if not audit_result.validation or not audit_result.validation.phone_web:

# DESPUES (distinguir WhatsApp visual vs Schema telephone):
if not audit_result.validation:
    # Sin datos de validacion → saltar
    pass
elif not audit_result.validation.phone_web and not getattr(audit_result.validation, 'whatsapp_html_detected', False):
    # Ni Schema telephone ni boton HTML → brecha real
    brechas.append({...})
elif not audit_result.validation.phone_web and getattr(audit_result.validation, 'whatsapp_html_detected', False):
    # Boton HTML existe pero sin Schema telephone → brecha menor (solo Schema)
    # NO reportar como "Sin WhatsApp" — el boton esta ahi
    pass  # O agregar brecha menor "Schema incompleto"
```

### T4: Actualizar quick wins (linea 1005-1009)

Misma logica: NO sugerir "Agregar Boton WhatsApp" si `whatsapp_html_detected=True`.

### T5: Actualizar tabla brechas (linea 941-944)

Si `whatsapp_html_detected=True` pero `phone_web=None`, NO mostrar "Sin Boton WhatsApp". En su lugar mostrar nota informativa.

---

## Criterios de Completitud

- [ ] `_detectar_whatsapp()` del scraper alimenta el pipeline de validacion
- [ ] `CrossValidationResult` tiene campo `whatsapp_html_detected`
- [ ] Brecha "Sin WhatsApp" NO se genera cuando boton HTML existe
- [ ] Quick wins NO sugiere "Agregar WhatsApp" cuando boton existe
- [ ] Tests existentes pasan (sin regresion)
- [ ] `search_files('WHATSAPP_AUSENTE')` en v4_comprehensive sigue vacio (no es necesario propagar, solo usar el nuevo campo)

---

## Archivos a Modificar

| Archivo | Cambio |
|---------|--------|
| `modules/auditors/v4_comprehensive.py` | Recibir whatsapp del scraper, agregar a CrossValidationResult |
| `modules/commercial_documents/data_structures.py` | Campo `whatsapp_html_detected` en ValidationSummary |
| `modules/commercial_documents/v4_diagnostic_generator.py` | 4 zonas: brecha, tabla, quick wins, condicion |

## Post-Ejecucion

- Marcar checklist en `06-checklist-implementacion.md`
- Ejecutar `log_phase_completion.py --fase FASE-A`
- Actualizar `09-documentacion-post-proyecto.md` Seccion A (modulos) y Seccion E (archivos)

## Evidence

```bash
mkdir -p evidence/fase-a
./venv/Scripts/python.exe -m pytest tests/commercial_documents/ tests/asset_generation/ -v --tb=short 2>&1 | tee evidence/fase-a/regression_pre.log
```
