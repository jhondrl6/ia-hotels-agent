# Contexto: Falsos Positivos en Diagnostico v4 - FASE-E

## Fecha creacion: 2026-04-08
## Fecha actualizacion: 2026-04-09
## Hotel referencia: amaziliahotel.com
## FASE: E - Integridad de Datos Diagnosticos

---

## Naturaleza del Problema

Patron comun: datos que se detectan correctamente en capas tempranas del pipeline
pero NO se propagan a los consumidores intermedios/finales del diagnostico.

| Workstream | Dato que existe | Dato que NO llega | Consumidor afectado |
|------------|-----------------|-------------------|---------------------|
| WhatsApp | `whatsapp_html_detected` (HTML scan) | `pain_solution_mapper`, `ValidationSummary`, `coherence_validator` | Pain IDs, coherence gate |
| Regional | `gbp.address` (GBP API) | `_detect_region_from_url()` | `${hotel_region}` en template |

---

## WORKSTREAM 1: WhatsApp - Propagacion de `whatsapp_html_detected`

### Estado: Fix parcial (FASE-A) -- solo v4_diagnostic_generator corregido

---

### Hallazgo: Falso Positivo WhatsApp

El diagnostico generado reporta "BRECHA 2] Canal Directo Cerrado (Sin WhatsApp)"
indicando que NO hay boton de WhatsApp. El sistema lo detecta como "no existe"
por un problema de propagacion entre capas.

### Flujo actual (problematico):

```
CAPA 1: Scraper's _detectar_whatsapp() [web_scraper.py:394-409]
  -> Escanea HTML en busca de patrones: wa.me, api.whatsapp.com, web.whatsapp.com
  -> Resultado: bool (existe o no) -- NO se expone como campo individual
  -> Solo genera brecha WHATSAPP_AUSENTE en score_visibilidad_ia

CAPA 2: v4_comprehensive.py [linea 444]
  -> _detect_whatsapp_from_html(page_html)
  -> Resultado: whatsapp_html_detected = bool
  -> Se almacena en CrossValidationResult (linea 1122)
  -> SE PROPAGA a: v4_diagnostic_generator (linea 1808) ✅
  -> NO SE PROPAGA a: pain_solution_mapper, ValidationSummary, coherence_validator ❌

CAPA 3: Schema auditor [rich_results_client.py]
  -> Solo extrae 'telephone' del JSON-LD de la pagina
  -> Si telephone no esta en Schema -> phone_web = None

CAPA 4: main.py [linea 1484, 1739-1766]
  -> whatsapp_web = audit_result.validation.phone_web  (= Schema telephone)
  -> Si whatsapp_web = None -> campo "whatsapp_number" NUNCA se agrega a ValidationSummary
  -> Resultado: validation_summary.get_field("whatsapp_number") = None

CAPA 5: pain_solution_mapper.py [linea 331-332]
  -> Consulta validation_summary.get_field("whatsapp_number")
  -> Si no existe -> agrega pain "no_whatsapp_visible"
  -> NUNCA consulta whatsapp_html_detected ❌

CAPA 6: coherence_validator.py [linea 370-379]
  -> Consulta validation_summary.get_field("whatsapp_number")
  -> Si no existe -> whatsapp_verified score = 0.0
  -> NUNCA consulta whatsapp_html_detected ❌
```

### El Gap - 3 Desconexiones

| # | Donde se pierde el dato | Que consume | Efecto |
|---|------------------------|-------------|--------|
| 1 | `main.py:1739-1766` | ValidationSummary | `whatsapp_number` nunca se crea si no hay phone_web del Schema |
| 2 | `pain_solution_mapper.py:331` | Pain ID | Agrega `no_whatsapp_visible` sin consultar HTML |
| 3 | `coherence_validator.py:370` | Coherence gate | `whatsapp_verified = 0.0` sin consultar HTML |

### Confirmacion E2E (FASE-D, amaziliahotel.com):

El fix de FASE-A (`_detect_whatsapp_from_html` en v4_comprehensive.py) funciona correctamente.
El sitio genuinamente NO tiene WhatsApp (no hay wa.me ni whatsapp:// en HTML).
La brecha "Sin WhatsApp" es legitima para este hotel.

El problema es estructural: para un hotel que SI tenga boton WhatsApp en HTML
pero NO telephone en Schema, se generaria un falso positivo en pain_solution_mapper
y coherence_validator aunque v4_diagnostic_generator no lo reporte como brecha.

### Fixes Requeridos

#### Fix W1 (P1): main.py:1766+ - Agregar rama para HTML-detect

Despues del `elif whatsapp_web` (linea 1766), agregar:

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

#### Fix W2 (P1): pain_solution_mapper.py:330-340 - Consultar whatsapp_html_detected

Opcion A (menor impacto) - Pasar `whatsapp_html_detected` como parametro:

```python
def _detect_pains(self, validation_summary, whatsapp_html_detected=False):
    ...
    whatsapp_field = validation_summary.get_field("whatsapp_number")
    has_html_whatsapp = whatsapp_html_detected
    if (not whatsapp_field or whatsapp_field.confidence in (ConfidenceLevel.UNKNOWN, ConfidenceLevel.CONFLICT)) and not has_html_whatsapp:
        pains.append(Pain(...))
```

Opcion B (mas robusta) - Fix W1 ya agrega campo a ValidationSummary,
entonces pain_solution_mapper solo necesita verificar que el campo
con confidence ESTIMATED no dispare el pain. Revisar logica de linea 332.

#### Fix W3 (P2): web_scraper.py:1112+ - Capturar tel: del HTML

`_extract_contact()` solo hace regex sobre texto. No parsea `<a href="tel:...">`.

```python
tel_links = soup.find_all('a', href=re.compile(r'^tel:', re.I))
for link in tel_links:
    phone = link.get('href', '').replace('tel:', '').strip()
    if phone:
        contact_data['telefono'] = phone
        break
```

#### Fix W4 (P3): coherence_validator.py:370 - Same patron que pain_solution_mapper

Consultar `whatsapp_html_detected` antes de asignar score 0.0.

### Archivos a Modificar

| Archivo | Lineas | Cambio |
|---------|--------|--------|
| `main.py` | 1766+ | Agregar rama elif con whatsapp_html_detected |
| `modules/commercial_documents/pain_solution_mapper.py` | 330-340 | Consultar whatsapp_html_detected |
| `modules/scrapers/web_scraper.py` | 1112+ | Parsear href="tel:" en _extract_contact() |
| `modules/commercial_documents/coherence_validator.py` | 370-379 | Consultar whatsapp_html_detected |

---

## WORKSTREAM 2: Regional - Propagacion de `gbp.address`

### Estado: Fix parcial (FASE-C) -- typo yRevisan corregido, fallback persiste

---

### Hallazgo: Region = "nacional" persiste en diagnostico

El diagnostico muestra "Lo que esta pasando en nacional", "Hotel boutique en nacional?",
"zona de nacional" -- texto que deberia mostrar la region real del hotel (ej: "Eje Cafetero").

### Flujo actual (problematico):

```
PASO 1: _detect_region_from_url(url) [main.py:2688-2699]
  -> Keyword-matching contra URL: visperas, salento, cartagena, medellin, bogota...
  -> SOLO 4 regiones mapeadas: eje_cafetero, caribe, antioquia, centro
  -> CUALQUIER URL no mapeada -> return 'nacional'
  -> "amaziliahotel.com" -> no match -> 'nacional'

PASO 2: region = 'nacional' [main.py:1410]
  -> Se pasa al OnboardingController (linea 1421)
  -> Se usa para ADR resolution (linea 1610)
  -> Se pasa a _prepare_template_data (linea 2046)

PASO 3: hotel_region = region or "Colombia" [v4_diagnostic_generator.py:413]
  -> region = 'nacional' (truthy!) -> hotel_region = 'nacional'
  -> NO sanitiza valores genericos
  -> Se propaga sin cambios a:
     - hotel_landmark = "zona de nacional" (linea 417)
     - regional_context = _build_regional_context('nacional') (linea 418)
     - data['hotel_region'] = 'nacional' (linea 541) -> TEMPLATE

PASO 4: _build_regional_context('nacional') [v4_diagnostic_generator.py:1618-1642]
  -> No machea ninguna key del region_contexts dict
  -> Fallback linea 1641: SI detecta "nacional" -> reemplaza con "esta zona"
  -> regional_context = "esta zona en Colombia presenta oportunidades..."
  -> PERO hotel_region ya es "nacional" en el template!

PASO 5: Template diagnostico_v6_template.md
  -> ${hotel_region} = "nacional" en 7+ ubicaciones (L15, L21, L27, etc.)
  -> ${regional_context} = "esta zona..." (OK, pero no compensa hotel_region)
```

### El Gap - 3 Desconexiones

| # | Donde falla | Efecto |
|---|-------------|--------|
| 1 | `_detect_region_from_url()` solo consulta URL, ignora GBP address | Hoteles sin keyword geografica en URL = "nacional" |
| 2 | `hotel_region = region or "Colombia"` no sanitiza "nacional" | Valor generico se propaga al template |
| 3 | No hay normalizacion de formato (guiones bajos, title case) | "eje_cafetero" llegaria como "eje_cafetero" al template |

### Datos Disponibles NO Utilizados

El auditor YA tiene la direccion del GBP (`audit_result.gbp.address`) que contiene
la ciudad/departamento real del hotel. Para amaziliahotel.com:
- GBP address contiene "Armenia" o "Quindio" -> region real = Eje Cafetero
- Pero `_detect_region_from_url()` se ejecuta ANTES del audit y nunca se re-evalua

### Fixes Requeridos

#### Fix R1 (P1): main.py - Inferir region desde GBP address post-auditoria

Agregar funcion `_infer_region_from_address()` y llamarla despues del audit
cuando region = "nacional":

```python
# Despues del audit (~linea 1470):
if region == "nacional" and audit_result and hasattr(audit_result, 'gbp') and audit_result.gbp:
    inferred = _infer_region_from_address(audit_result.gbp.address)
    if inferred:
        region = inferred
        print(f"   Region inferida desde GBP: {region}")

def _infer_region_from_address(address: str) -> str | None:
    if not address:
        return None
    addr_lower = address.lower()
    REGION_PATTERNS = {
        'eje_cafetero': ['armenia', 'quindío', 'quindio', 'pereira', 'risaralda',
                         'manizales', 'caldas', 'salento', 'filandia', 'calarca',
                         'montenegro', 'circasia'],
        'caribe': ['cartagena', 'barranquilla', 'santa marta', 'sincelejo'],
        'antioquia': ['medellín', 'medellin', 'antioquia', 'guatapé', 'guatape',
                       'rionegro', 'jardín', 'jardin'],
        'centro': ['bogotá', 'bogota', 'cundinamarca', 'chia', 'cajica'],
        'valle': ['cali', 'valle del cauca', 'palmira', 'buga'],
        'llanos': ['villavicencio', 'meta', 'yopal', 'casanare'],
        'san_andres': ['san andrés', 'san andres', 'providencia'],
    }
    for region_key, patterns in REGION_PATTERNS.items():
        if any(p in addr_lower for p in patterns):
            return region_key
    return None
```

#### Fix R2 (P1): v4_diagnostic_generator.py:413 - Sanitizar valores genericos

```python
# ANTES:
hotel_region = region or "Colombia"

# DESPUES:
_raw = region or "Colombia"
if _raw.lower() in ("nacional", "general", "default", "unknown"):
    hotel_region = "Colombia"
else:
    hotel_region = _raw.replace("_", " ").title()
    # "eje_cafetero" -> "Eje Cafetero"
    # "caribe" -> "Caribe"
```

Garantiza que "nacional" NUNCA llegue al template como nombre visible.

#### Fix R3 (P2): main.py:2688-2699 - Ampliar keywords URL

Agregar keywords del Eje Cafetero que no estan:

```python
if any(x in url_lower for x in ['visperas', 'salento', 'armenia', 'quindio',
      'calarca', 'cafetero', 'finca', 'amazilia', 'montenegro', 'filandia']):
    return 'eje_cafetero'
```

### Archivos a Modificar

| Archivo | Lineas | Cambio |
|---------|--------|--------|
| `main.py` | 2688-2699 + nueva funcion | Inferir region desde GBP address + ampliar keywords |
| `modules/commercial_documents/v4_diagnostic_generator.py` | 413 | Sanitizar "nacional" y normalizar formato |

---

## BRECHA 5 - Narrativa Citability (FASE-B: COMPLETADO)

**Estado:** Corregido

`blocks_analyzed=0` genera narrativa "Contenido No Discoverable por IA" -- NO "poco estructurado".
El fix diferencia correctamente entre score bajo (blocks>0, score<30) y contenido ausente (blocks=0).

Pain ID: `low_citability` sigue siendo valido como oportunidad.
Narrativa corregida: "contenido no discoverable por IAs"

Archivos relacionados:
- `modules/commercial_documents/v4_diagnostic_generator.py:1850-1860`

---

## Typo yRevisan (FASE-C: COMPLETADO)

**Estado:** Corregido en template

`yRevisan` corregido a `y Revisan` en `templates/diagnostico_v6_template.md:27`.

---

## FASE-D: Validacion E2E (2026-04-09)

**Hotel:** amaziliahotel.com
**Coherence:** 0.84 (umbral 0.80) -- PASS
**Publication:** READY_FOR_PUBLICATION

### Gate Checks

| Check | Score | Pass |
|-------|-------|------|
| problems_have_solutions | 0.818 | OK |
| assets_are_justified | 1.000 | OK |
| financial_data_validated | 0.700 | OK |
| whatsapp_verified | 0.000 | NO-BLOCK (legitimo: hotel no tiene WhatsApp) |
| price_matches_pain | 1.000 | OK |
| promised_assets_exist | 1.000 | OK |

5/6 pasados. `whatsapp_verified=0.000` es resultado correcto para este hotel.

### Hallazgo NO-bloqueante

`phone_web=null` cuando `tel:` link existe en HTML.
El scraper no captura telefono del atributo `tel:` -- solo del JSON-LD Schema.
Ver Fix W3 arriba.

---

## Resumen FASE-E: Alcance Completo

| Workstream | Fixes | Archivos | Complejidad |
|------------|-------|----------|-------------|
| WhatsApp (W1-W4) | 4 fixes propagacion | main.py, pain_solution_mapper, web_scraper, coherence_validator | Media |
| Regional (R1-R3) | 3 fixes deteccion+sanitizacion | main.py, v4_diagnostic_generator | Baja-Media |

**Total:** 7 fixes, 6 archivos, 0 dependencias cruzadas entre workstreams.

### Orden de implementacion sugerido:

1. Fix R2 (sanitizacion hotel_region) -- 1 linea, efecto inmediato
2. Fix W1 (rama elif whatsapp_html) -- ~8 lineas, desbloquea W2/W4
3. Fix R1 (region desde GBP) -- nueva funcion + llamada, elimina causa raiz
4. Fix W2 (pain_solution_mapper) -- 3 lineas, elimina falso positivo pain
5. Fix W3 (web_scraper tel:) -- ~5 lineas, captura telefonos perdidos
6. Fix W4 (coherence_validator) -- 3 lineas, coherence gate realista
7. Fix R3 (ampliar keywords) -- 1 linea, reduce falsos "nacional"
