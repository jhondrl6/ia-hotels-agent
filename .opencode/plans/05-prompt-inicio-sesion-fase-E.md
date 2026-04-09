# Prompt de Inicio de Sesion — FASE-E: Integridad de Datos Diagnosticos

## Contexto

### Documento de referencia
`/mnt/c/Users/Jhond/Github/iah-cli/.opencode/plans/context/whatsapp_false_positive.md`
Secciones: WORKSTREAM 1 (WhatsApp) y WORKSTREAM 2 (Regional)

### Estado de Fases Anteriores
- FASE-A (WhatsApp Detection Fix): COMPLETADA — `_detect_whatsapp_from_html()` conectado a v4_diagnostic_generator
- FASE-B (Citability Narrative Fix): COMPLETADA — narrativa diferencia blocks=0 vs score bajo
- FASE-C (Regional Template Fixes): COMPLETADA — typo corregido, eje_cafetero en mapping
- FASE-D (Validacion E2E): COMPLETADA — coherence 0.84, WhatsApp legitimo (hotel no tiene), Region "nacional" persiste

### Problemas Pendientes (detectados en FASE-D)

Patron comun: datos que se detectan correctamente en capas tempranas del pipeline pero NO se propagan a consumidores intermedios/finales.

| Workstream | Dato que existe | Dato que NO llega | Consumidor afectado |
|------------|-----------------|-------------------|---------------------|
| WhatsApp | `whatsapp_html_detected` (HTML scan) | `pain_solution_mapper`, `ValidationSummary`, `coherence_validator` | Pain IDs, coherence gate |
| Regional | `gbp.address` (GBP API) | `_detect_region_from_url()` | `${hotel_region}` en template |

---

## Objetivo

Eliminar 2 persistencias de datos incorrectos en diagnosticos generados:
1. WhatsApp: `whatsapp_html_detected` debe propagarse a ValidationSummary, pain_solution_mapper y coherence_validator
2. Regional: la region debe inferirse desde GBP address cuando la URL no contiene keywords geograficas

---

## Tareas

### ORDEN SUGERIDO (menor a mayor dependencia):

---

### T1: Fix R2 — Sanitizar hotel_region (1 linea, efecto inmediato)

**Archivo:** `modules/commercial_documents/v4_diagnostic_generator.py`
**Linea:** 413

```python
# ANTES:
hotel_region = region or "Colombia"

# DESPUES:
_raw = region or "Colombia"
if _raw.lower() in ("nacional", "general", "default", "unknown"):
    hotel_region = "Colombia"
else:
    hotel_region = _raw.replace("_", " ").title()
```

Efecto: "nacional" NUNCA llega al template como nombre visible. "eje_cafetero" → "Eje Cafetero".

---

### T2: Fix W1 — Agregar rama whatsapp_html_detected en ValidationSummary

**Archivo:** `main.py`
**Linea:** despues de 1766 (despues del bloque `elif whatsapp_web:`)

Agregar nueva rama elif:

```python
elif getattr(audit_result.validation, 'whatsapp_html_detected', False):
    # WhatsApp boton existe en HTML pero no hay telefono en Schema
    validated_fields.append(ValidatedField(
        field_name="whatsapp_number",
        value="detected_via_html",
        confidence=ConfidenceLevel.ESTIMATED,
        sources=["HTML"],
        match_percentage=0.6,
        can_use_in_assets=True
    ))
```

Garantiza que SIEMPRE exista un campo `whatsapp_number` cuando el boton existe en HTML.

---

### T3: Fix R1 — Inferir region desde GBP address post-auditoria

**Archivo:** `main.py`

**3a. Agregar funcion nueva** (despues de `_detect_region_from_url`, ~linea 2700):

```python
def _infer_region_from_address(address: str) -> str | None:
    """Infiere region turistica desde direccion del GBP."""
    if not address:
        return None
    addr_lower = address.lower()
    REGION_PATTERNS = {
        'eje_cafetero': ['armenia', 'quindio', 'quindio', 'pereira', 'risaralda',
                         'manizales', 'caldas', 'salento', 'filandia', 'calarca',
                         'montenegro', 'circasia'],
        'caribe': ['cartagena', 'barranquilla', 'santa marta', 'sincelejo'],
        'antioquia': ['medellin', 'medellin', 'antioquia', 'guatape', 'guatape',
                       'rionegro', 'jardin', 'jardin'],
        'centro': ['bogota', 'bogota', 'cundinamarca', 'chia', 'cajica'],
        'valle': ['cali', 'valle del cauca', 'palmira', 'buga'],
        'llanos': ['villavicencio', 'meta', 'yopal', 'casanare'],
        'san_andres': ['san andres', 'san andres', 'providencia'],
    }
    for region_key, patterns in REGION_PATTERNS.items():
        if any(p in addr_lower for p in patterns):
            return region_key
    return None
```

**3b. Llamar funcion despues del audit** (~linea 1470, despues de que audit_result esta disponible):

```python
# Re-evaluar region si fallback a "nacional" y GBP address disponible
if region == "nacional" and audit_result and hasattr(audit_result, 'gbp') and audit_result.gbp:
    inferred = _infer_region_from_address(audit_result.gbp.address)
    if inferred:
        region = inferred
        print(f"   Region inferida desde GBP: {region}")
```

**IMPORTANTE:** Insertar ANTES de la linea donde se pasa region al generador (~linea 2046).

---

### T4: Fix W2 — pain_solution_mapper consulta whatsapp_html_detected

**Archivo:** `modules/commercial_documents/pain_solution_mapper.py`
**Linea:** 315 (firma) y 330-340 (logica WhatsApp)

**4a. Agregar parametro a `_detect_pains`:**

```python
# ANTES:
def _detect_pains(self, validation_summary):

# DESPUES:
def _detect_pains(self, validation_summary, whatsapp_html_detected=False):
```

**4b. Actualizar condicion WhatsApp (linea 332):**

```python
# ANTES:
if not whatsapp_field or whatsapp_field.confidence in (ConfidenceLevel.UNKNOWN, ConfidenceLevel.CONFLICT):

# DESPUES:
if (not whatsapp_field or whatsapp_field.confidence in (ConfidenceLevel.UNKNOWN, ConfidenceLevel.CONFLICT)) and not whatsapp_html_detected:
```

**4c. Actualizar llamador** (donde se llama `_detect_pains`):
Buscar todos los sitios que llaman `_detect_pains()` y pasar `whatsapp_html_detected`.
El dato viene de `audit_result.validation.whatsapp_html_detected`.

---

### T5: Fix W3 — Capturar tel: del HTML en scraper

**Archivo:** `modules/scrapers/web_scraper.py`
**Linea:** dentro de `_extract_contact()` (~1112-1131)

Agregar despues de la linea que busca telefonos por regex:

```python
# Parsear enlaces tel: que no aparecen como texto visible
tel_links = soup.find_all('a', href=re.compile(r'^tel:', re.I))
for link in tel_links:
    phone = link.get('href', '').replace('tel:', '').strip()
    if phone:
        contact_data['telefono'] = phone
        break
```

---

### T6: Fix W4 — coherence_validator consulta whatsapp_html_detected

**Archivo:** `modules/commercial_documents/coherence_validator.py`
**Linea:** 370-379

Similar a Fix W2: si `whatsapp_html_detected=True` y no hay campo `whatsapp_number` en ValidationSummary,
no deberia dar score 0.0 (deberia dar al menos un score parcial o skip el check).

Agregar logica:

```python
# Antes del check actual (linea 370):
# Si hay WhatsApp en HTML pero no en ValidationSummary, no penalizar
whatsapp_html = getattr(audit_result.validation, 'whatsapp_html_detected', False) if audit_result else False
if not whatsapp_field and whatsapp_html:
    return CoherenceCheck(
        name="whatsapp_verified",
        passed=not is_blocking,
        score=0.5,  # Parcial: boton existe pero sin numero verificado
        message="WhatsApp detectado en HTML (sin verificacion cruzada)",
        severity="warning" if not is_blocking else "info"
    )
```

**NOTA:** Requiere recibir `audit_result` o `whatsapp_html_detected` como parametro.
Verificar la firma de la funcion que hace este check.

---

### T7: Fix R3 — Ampliar keywords URL

**Archivo:** `main.py`
**Linea:** 2691

```python
# ANTES:
if any(x in url_lower for x in ['visperas', 'salento', 'armenia', 'quindio', 'calarca']):

# DESPUES:
if any(x in url_lower for x in ['visperas', 'salento', 'armenia', 'quindio', 'calarca',
      'cafetero', 'finca', 'montenegro', 'filandia', 'circasia', 'termales']):
```

---

## Criterios de Completitud

- [ ] T1: hotel_region nunca muestra "nacional" en template (sanitizado a "Colombia")
- [ ] T2: ValidationSummary siempre tiene campo "whatsapp_number" cuando boton HTML existe
- [ ] T3: Region se infiere desde GBP address cuando URL no tiene keywords
- [ ] T4: pain_solution_mapper NO genera pain "no_whatsapp_visible" cuando boton HTML existe
- [ ] T5: web_scraper captura telefonos de enlaces `tel:`
- [ ] T6: coherence_validator no penaliza whatsapp_verified cuando boton HTML existe
- [ ] T7: Keywords URL ampliadas para Eje Cafetero
- [ ] Tests existentes pasan (sin regresion)
- [ ] v4complete --url https://amaziliahotel.com/ ejecuta sin crashes

---

## Archivos a Modificar

| Archivo | Fixes | Zona |
|---------|-------|------|
| `main.py` | W1 (linea 1766+), R1 (linea 1470+ y funcion nueva), R3 (linea 2691) | 3 zonas separadas |
| `modules/commercial_documents/v4_diagnostic_generator.py` | R2 (linea 413) | 1 zona |
| `modules/commercial_documents/pain_solution_mapper.py` | W2 (lineas 315, 332) | 2 zonas |
| `modules/scrapers/web_scraper.py` | W3 (linea 1112+) | 1 zona |
| `modules/commercial_documents/coherence_validator.py` | W4 (linea 370+) | 1 zona |

**Riesgo de conflictos:** BAJO. Los fixes tocan zonas distintas sin overlap entre workstreams.

---

## Post-Ejecucion

- Marcar checklist en `06-checklist-implementacion.md`
- Ejecutar `log_phase_completion.py --fase FASE-E`
- Actualizar `09-documentacion-post-proyecto.md` Secciones A-D con fixes FASE-E
- Ejecutar prueba E2E: `./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ --debug`

## Evidence

```bash
mkdir -p evidence/fase-e
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/ -v --tb=short -k "whatsapp or region or pain or coherence" 2>&1 | tee evidence/fase-e/regression_pre.log
```
