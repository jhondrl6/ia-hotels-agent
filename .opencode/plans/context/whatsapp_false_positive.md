# Contexto: Falsos Positivos en Diagnostico v4 - FASE-E

## Fecha creacion: 2026-04-08
## Fecha actualizacion: 2026-04-09 (micro-sesion W0)
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

### Estado: Fix W0 aplicado (patrones), BRECHA 2 persiste -- debug pendiente

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

### Confirmacion E2E (FASE-D, amaziliahotel.com) -- CORREGIDO 2026-04-09:

**CONCLUSION ANTERIOR (ERRONEA):** "El sitio genuinamente NO tiene WhatsApp."
**CONCLUSION CORRECTA:** El sitio SI tiene WhatsApp. La deteccion falla por gaps en los patrones de busqueda.

#### Investigacion con browser real (2026-04-09, post-FASE-E):

El hotel amaziliahotel.com SI tiene boton WhatsApp funcional, implementado via plugin
WordPress "Joinchat" (creame-whatsapp-me) v5.2.1:
- Numero: +57 310 401 9049
- Ubicacion: esquina inferior derecha
- Tooltip: "Bienvenido al Hotel Amazilia, ¿En qué te podemos ayudar?"
- Config: WhatsApp Web, button_delay=3s, message_delay=5s

#### Causa raiz del falso negativo -- Patrones insuficientes:

El HTML crudo (sin ejecutar JS) contiene:
- `class="joinchat"` (21 ocurrencias) -- NO contiene la palabra "whatsapp"
- `data-settings='{"telephone":"573104019049"}'`
- Script: `creame-whatsapp-me/public/js/joinchat.min.js`
- SVG con titulo "WhatsApp" dentro del widget

Pero `_detect_whatsapp_from_html()` busca SOLO estos 7 patrones:
```
1. r'wa\.me/'                          -> 0 matches (Joinchat construye el link via JS)
2. r'api\.whatsapp\.com'               -> 0 matches
3. r'web\.whatsapp\.com'               -> 0 matches
4. r'whatsapp://'                      -> 0 matches
5. r'whatsapp\.com/send'               -> 0 matches
6. r'class="[^"]*whatsapp[^"]*"'       -> 0 matches (la clase es "joinchat", no "whatsapp")
7. r'id="[^"]*whatsapp[^"]*"'          -> 0 matches
```

**Ninguno de los 7 patrones matchea.** El patron `class="*whatsapp*"` falla porque
Joinchat usa `class="joinchat"` sin la palabra whatsapp en el nombre de clase.
El link `wa.me/573104019049` se genera dinamicamente via JavaScript al hacer click,
NO existe como href en el HTML estatico.

#### Patrones que SI existen en el HTML crudo y deberian detectarse:
- `joinchat` (clase CSS del plugin, 21 matches)
- `creame-whatsapp-me` (path del plugin en script src)
- `data-settings` con JSON conteniendo `"telephone"`
- `<title>WhatsApp</title>` dentro de SVG del widget

#### Implicacion:

Esta no es solo una "desconexion entre capas" (como se creia en FASE-A/D).
El problema es mas fundamental: `_detect_whatsapp_from_html()` no puede detectar
el plugin de WhatsApp mas popular de WordPress (Joinchat/creame-whatsapp-me).

BRECHA 2 "Sin WhatsApp" en el diagnostico de amaziliahotel.com es FALSA.
El hotel pierde la oportunidad reportada ($626.400 COP/mes) solo en el papel,
no en la realidad.

### Fixes Requeridos

**NOTA:** Los fixes W1-W4 originales siguen siendo validos para propagacion entre capas,
pero el fix W0 (nuevo) es el PREREQUISITO -- sin el, ninguna capa recibe el dato correcto.

#### Fix W0 (P0 - CRITICO): v4_comprehensive.py:1040-1048 - Ampliar patrones de deteccion

Los 7 patrones actuales fallan para Joinchat, el plugin de WhatsApp mas usado en WordPress (500K+ installs).
El link `wa.me/` se construye via JavaScript, NO existe en el HTML estatico.

```python
whatsapp_patterns = [
    # --- Patrones originales (links directos) ---
    r'wa\.me/',
    r'api\.whatsapp\.com',
    r'web\.whatsapp\.com',
    r'whatsapp://',
    r'whatsapp\.com/send',
    r'class="[^"]*whatsapp[^"]*"',
    r'id="[^"]*whatsapp[^"]*"',
    # --- NUEVOS: Plugins WordPress comunes ---
    r'class="[^"]*joinchat[^"]*"',          # Joinchat/creame-whatsapp-me (500K+ installs)
    r'creame-whatsapp-me',                   # Path del plugin Joinchat
    r'whatsapp-me',                          # Variacion del plugin
    r'class="[^"]*wa-chat[^"]*"',           # WA Chat widgets
    r'class="[^"]*click-to-chat[^"]*"',     # Click to Chat (another popular WP plugin)
    r'class="[^"]*ht-ctc[^"]*"',            # Click to Chat for WhatsApp (200K+ installs)
    r'data-phone.*whatsapp',                 # Generic data attributes
    r'data-settings.*telephone',            # Joinchat stores number in data-settings JSON
    r'joinchat',                             # Joinchat class name (catch-all)
]
```

Con estos patrones adicionales, amaziliahotel.com pasaria de 0/7 a 3+ matches.

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
|| whatsapp_verified | 0.000 | NO-BLOCK (FALSO NEGATIVO: hotel SI tiene WhatsApp via Joinchat) |
| price_matches_pain | 1.000 | OK |
| promised_assets_exist | 1.000 | OK |

5/6 pasados. `whatsapp_verified=0.000` es FALSO NEGATIVO -- el hotel SI tiene WhatsApp
via plugin Joinchat, pero `_detect_whatsapp_from_html()` no lo detecta porque los patrones
no cubren la clase CSS "joinchat" ni el plugin "creame-whatsapp-me".
Ver "Causa raiz del falso negativo" arriba.

### Hallazgo NO-bloqueante

`phone_web=null` cuando `tel:` link existe en HTML.
El scraper no captura telefono del atributo `tel:` -- solo del JSON-LD Schema.
Ver Fix W3 arriba.

---

## Resumen FASE-E: Alcance Completo

| Workstream | Fixes | Archivos | Complejidad | Estado |
|------------|-------|----------|-------------|--------|
| WhatsApp (W0-W4) | 5 fixes (W0 deteccion + W1-W4 propagacion) | v4_comprehensive.py, main.py, pain_solution_mapper, web_scraper, coherence_validator | Media-Alta | W0 aplicado, BRECHA 2 persiste (ver abajo) |
| Regional (R1-R3) | 3 fixes deteccion+sanitizacion | main.py, v4_diagnostic_generator | Baja-Media | PENDIENTE |

**Total:** 8 fixes, 6 archivos, 0 dependencias cruzadas entre workstreams.

---

## SESION 2026-04-09 (post-FASE-E): Micro-sesion W0

### Que se hizo:

**Fix W0 APLICADO en 2 archivos:**

1. `modules/auditors/v4_comprehensive.py:1040-1055` -- Se agregaron 6 patrones nuevos:
   - `joinchat`, `creame-whatsapp-me`, `ht-ctc`, `click-to-chat`, `wa-chat`, `data-settings.*telephone`

2. `modules/scrapers/web_scraper.py:394-410` -- Mismos 6 patrones en `_detectar_whatsapp()`.

**Verificacion unitaria PASA:**
```python
# Test directo de la funcion con HTML simulado de Joinchat:
html_test = '<div class="joinchat" data-settings="telephone..."></div>'
auditor._detect_whatsapp_from_html(html_test)  # → True ✅

# HTML sin WA:
auditor._detect_whatsapp_from_html('<p>Sin whatsapp</p>')  # → False ✅
```

### Resultado de v4complete post-fix:

**BRECHA 2 "Sin WhatsApp" PERSISTE en el diagnostico generado.**

Evidencia del reporte:
```
audit_report.json:
  validation.whatsapp_status = "estimated"     (detecto algo via GBP phone)
  validation.phone_web = None                  (Schema no tiene telephone)
  validation.phone_gbp = "310 4019049"         (GBP SI tiene telefono)
  # whatsapp_html_detected: NO APARECE en el JSON
```

Output del v4complete:
```
WhatsApp: estimated
Sin WhatsApp Visible: high
whatsapp_verified: score=0.000, passed=False
```

### Diagnostico del problema restante:

El fix W0 de patrones funciona correctamente en la funcion `_detect_whatsapp_from_html()`,
pero el valor `whatsapp_html_detected=True` NO llega al `_identify_brechas()` del
diagnostic generator. Hay un eslabon roto entre la deteccion y el consumo.

**Flujo que deberia funcionar pero no lo hace:**
```
v4_comprehensive.py:444  whatsapp_html_detected = _detect_whatsapp_from_html(page_html)
                          ↓ (ahora retorna True)
v4_comprehensive.py:447  validation_result = _run_cross_validation(..., whatsapp_html_detected=True)
                          ↓
v4_comprehensive.py:1130 CrossValidationResult(whatsapp_html_detected=True)
                          ↓
main.py:1463             audit_result = auditor.audit(url)
                          ↓
main.py:2058             diagnostic_gen.generate(audit_result=audit_result)
                          ↓
v4_diagnostic_generator.py:1810  getattr(audit_result.validation, 'whatsapp_html_detected', None)
                          ↓
                          DEBERIA ser True, pero probablemente llega None o False
```

**Hipotesis principal (VERIFICAR en proxima sesion):**

El parametro `page_html` que recibe `_detect_whatsapp_from_html()` en la linea 444
podria ser None, vacio, o texto sin clases CSS en la ejecucion real del `audit()`.

El metodo `audit()` en v4_comprehensive.py obtiene `page_html` de alguna fuente
interna (scraping, HTTP request, etc.) que podria:
- No ejecutarse correctamente
- Retornar solo texto plano (sin HTML tags/clases)
- Ser filtrado antes de llegar a la funcion de deteccion

### ACCIONES PENDIENTES para proxima sesion:

#### PASO 1 (DEBUG): Verificar page_html en audit()

Agregar log temporal en `v4_comprehensive.py:444-446`:

```python
whatsapp_html_detected = self._detect_whatsapp_from_html(page_html)
print(f"[DEBUG-W0] page_html length: {len(page_html) if page_html else 0}")
print(f"[DEBUG-W0] whatsapp_html_detected: {whatsapp_html_detected}")
if page_html and 'joinchat' in page_html.lower():
    print(f"[DEBUG-W0] joinchat FOUND in page_html")
elif page_html:
    print(f"[DEBUG-W0] joinchat NOT in page_html (first 200 chars: {page_html[:200]})")
```

Ejecutar: `venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/`
Ver si page_html tiene contenido y si contiene "joinchat".

#### PASO 2 (SEgun resultado del debug):

**SI page_html esta vacio/None:**
- Rastrear como `audit()` obtiene page_html. Buscar en v4_comprehensive.py
  donde se hace el HTTP request o scraping.
- Puede que el scraper de v4_comprehensive use un metodo diferente al WebScraper.

**SI page_html tiene contenido pero sin "joinchat":**
- El scraper puede estar parseando solo texto (BeautifulSoup.get_text())
  en vez de HTML crudo. Verificar que pasa el HTML original.

**SI page_html tiene "joinchat" pero whatsapp_html_detected=False:**
- Los nuevos patrones no compilaron correctamente. Limpiar __pycache__
  y re-ejecutar.

#### PASO 3: Fixes W1-W4 y R1-R3 (solo despues de que W0 funcione E2E)

Una vez que `whatsapp_html_detected=True` llegue al diagnostic generator y
BRECHA 2 desaparezca del diagnostico, proceder con:

1. Fix W1 (main.py:1766+ -- rama elif para HTML-detect en ValidationSummary)
2. Fix R2 (v4_diagnostic_generator.py:413 -- sanitizar "nacional")
3. Fix R1 (main.py -- _infer_region_from_address post-audit)
4. Fix W2 (pain_solution_mapper.py -- consultar whatsapp_html_detected)
5. Fix W3 (web_scraper.py -- capturar tel: del HTML)
6. Fix W4 (coherence_validator.py -- consultar whatsapp_html_detected)
7. Fix R3 (main.py -- ampliar keywords URL)

### Orden de implementacion sugerido (ACTUALIZADO):

1. ~~Fix W0 (patrones deteccion)~~ -- APLICADO, pendiente debug E2E
2. **DEBUG: Verificar page_html en audit()** -- PROXIMO PASO INMEDIATO
3. Fix R2 (sanitizacion hotel_region) -- 1 linea, efecto inmediato
4. Fix W1 (rama elif whatsapp_html) -- ~8 lineas, desbloquea W2/W4
5. Fix R1 (region desde GBP) -- nueva funcion + llamada, elimina causa raiz
6. Fix W2 (pain_solution_mapper) -- 3 lineas, elimina falso positivo pain
7. Fix W3 (web_scraper tel:) -- ~5 lineas, captura telefonos perdidos
8. Fix W4 (coherence_validator) -- 3 lineas, coherence gate realista
9. Fix R3 (ampliar keywords) -- 1 linea, reduce falsos "nacional"

### Validacion final:

Despues de todos los fixes, regenerar:
```bash
venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/
```

Verificar:
- BRECHA 2 "Sin WhatsApp" NO aparece en `01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md`
- `whatsapp_verified` score > 0 en output
- `region` = "eje_cafetero" (no "nacional")
- Coherence >= 0.80
