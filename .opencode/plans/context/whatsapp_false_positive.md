# Contexto: Falso Positivo WhatsApp en Diagnóstico v4

## Fecha: 2026-04-08
## Hotel: amaziliahotel.com

---

## Hallazgo: Contradicción visual vs. diagnóstico

El diagnóstico generado (01_DIAGNOSTICO_Y_OPORTUNIDAD_20260408_213710.md, línea 78)
reporta "BRECHA 2] Canal Directo Cerrado (Sin WhatsApp)" indicando que NO hay botón
de WhatsApp. SIN EMBARGO, visualmente el botón SÍ existe en amaziliahotel.com.

---

## Causa Raíz Identificada

El diagnóstico genera un FALSO POSITIVO. El botón de WhatsApp SÍ existe visualmente,
pero el sistema lo detecta como "no existe" por un problema de detección en capas:

### Flujo actual (problemático):

```
CAPA 1: Scraper's _detectar_whatsapp() [web_scraper.py:394-409]
  → Escanea HTML en busca de patrones: wa.me, api.whatsapp.com, web.whatsapp.com
  → ¿Resultado? WhatsApp VISIBLE (si existe visualmente)
  → Este dato se PIERDE — no llega al diagnóstico

CAPA 2: Schema auditor [rich_results_client.py:391-407]
  → Solo extrae 'telephone' del JSON-LD de la página
  → NO escanea HTML visual
  → Si telephone no está en Schema → phone_web = None

CAPA 3: Diagnostic generator [v4_diagnostic_generator.py:1788]
  → Condition: if not audit_result.validation.phone_web:
  → → phone_web viene del Schema, no del scraper
  → → Si telephone no está en JSON-LD → reporta "Sin WhatsApp" ❌
```

---

## El Gap

| Qué ve el usuario en amaziliahotel.com | Qué reporta el diagnóstico |
|----------------------------------------|--------------------------|
| Botón flotante de WhatsApp (visible) | "Sin botón WhatsApp" |
| WhatsApp real funcionando | `phone_web = None` (no detectado) |

El botón de WhatsApp existe como **elemento HTML visual**, pero NO está declarado
en el **JSON-LD Schema** como propiedad `telephone`. El diagnosticador solo consulta
la capa Schema.

---

## Confirmación en código

- `_detectar_whatsapp()` (web_scraper.py:394-409): búsqueda visual/patrones → **NO usada en diagnóstico**
- `_extract_properties()` (rich_results_client.py:395): solo extrae `telephone` del JSON-LD → **USA esta**
- `v4_diagnostic_generator.py:1788`: `if not audit_result.validation.phone_web:` → teléfono del Schema, no del scraper

### Módulos involucrados:

| Archivo | Función | Rol |
|---------|---------|-----|
| modules/scrapers/web_scraper.py | `_detectar_whatsapp()` | Detecta WhatsApp en HTML (NO se usa en diagnóstico) |
| modules/data_validation/external_apis/rich_results_client.py | `_extract_properties()` | Extrae `telephone` solo de JSON-LD |
| modules/auditors/v4_comprehensive.py | `_run_cross_validation()` | Asigna `phone_web = schema.properties.get("telephone")` |
| modules/commercial_documents/v4_diagnostic_generator.py:1788 | Detección de brecha | Condición: `if not phone_web` → fals positivo |

---

## Veredicto

La brecha ["BRECHA 2] Canal Directo Cerrado (Sin WhatsApp)" es un **falso positivo**.

El botón de WhatsApp existe visualmente, pero el sistema de auditoría no lo detecta porque:

1. El Schema auditor solo lee `telephone` de JSON-LD
2. El botón flotante de WhatsApp en WordPress typically no se declara en Schema.org
3. El diagnóstico mezcla "botón visual" con "teléfono en Schema" — son cosas distintas

---

## Recomendación

El scraper's `_detectar_whatsapp()` debería alimentar la detección de `no_whatsapp_visible`,
no solo el Schema `telephone`. O el diagnóstico debería distinguir entre:

- "WhatsApp visual" (existe botón en HTML) → diferente de
- "teléfono en Schema" (telephone en JSON-LD)

El `pain_id no_whatsapp_visible` debería basarse en `_detectar_whatsapp()` del scraper,
no en `phone_web` del Schema.

---

## Archivos clave relacionados

- `/mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260408_213710.md`
- `/mnt/c/Users/Jhond/Github/iah-cli/modules/scrapers/web_scraper.py` → `_detectar_whatsapp()`
- `/mnt/c/Users/Jhond/Github/iah-cli/modules/data_validation/external_apis/rich_results_client.py` → `_extract_properties()`
- `/mnt/c/Users/Jhond/Github/iah-cli/modules/auditors/v4_comprehensive.py` → `_run_cross_validation()`
- `/mnt/c/Users/Jhond/Github/iah-cli/modules/commercial_documents/v4_diagnostic_generator.py` → línea 1788
- `/mnt/c/Users/Jhond/Github/iah-cli/modules/commercial_documents/pain_solution_mapper.py` → `no_whatsapp_visible`
- `/mnt/c/Users/Jhond/Github/iah-cli/modules/asset_generation/asset_catalog.py` → `whatsapp_button` (promised_by)

---

## BRECHA 5 - Narrativa Imprecisa (Citabilidad)

**Fecha:** 2026-04-09
**Hotel:** amaziliahotel.com
**Estado:** Narrativa imprecisa, oportunidad válida

---

### Hallazgo: Narrativa incorrecta en diagnóstico

El diagnóstico (línea 93-96) reporta:
> "ChatGPT y Perplexity no recomiendan su hotel porque **el contenido es insuficiente o poco estructurado**"

Sin embargo, del audit_report.json:161-168:
```
citability.overall_score: 0
blocks_analyzed: 0          ← La clave
high_citability_blocks: 0
```

El auditor **no pudo analizar contenido** (blocks_analyzed: 0). El score de 0 es un **default por ausencia de dato**, no una evaluación real de calidad de contenido.

La recomendación del propio audit lo confirma:
> *"Content structure is good. Maintain current paragraph lengths."*

Esto contradice directamente la narrativa "contenido poco estructurado".

---

### Causa Raíz

| Dato del audit | Significado |
|----------------|-------------|
| `blocks_analyzed: 0` | No hay contenido que el crawler haya podido capturar |
| `overall_score: 0` | Score por default, no evaluación real |
| `high_citability_blocks: 0` | Sin bloques evaluados |

El score 0 no dice "contenido malo". Dice "no hay contenido para analizar".

---

### El Gap

| Narrativa del diagnóstico | Realidad del audit |
|--------------------------|--------------------|
| Contenido "poco estructurado" | blocks_analyzed = 0 → no hay contenido |
| Contenido "insuficiente" | ✅ CORRECTO (pero no se usa esta narrativa) |
| ChatGPT no puede recomendar | No hay datos para citar |

---

### Veredicto

**Narrativa imprecisa, oportunidad válida.**

La oportunidad **sigue siendo real**: que el hotel sea recomendable por IA. Lo que cambia es la explicación:

| Narrativa original (errónea) | Narrativa corregida |
|---------------------------|-------------------|
| "contenido es insuficiente o poco estructurado" | "sitio no tiene contenido estructurado para que AI lo descubra y cite" |

---

### Asset Consecuente

**CONSECUENTE:** `llms.txt` o `local_content_page` (generación de contenido local FASE-E)
- Le da a AI contenido explícito para descubrir
- Resuelve el problema real: contenido inexistente o no discoverable

**INCONSECUENTE:** `citability_guide` o `content_restructure`
- Sería redundante; la narrativa de "no citable" ya no aplica
- El problema no es contenido "malo", es contenido "ausente"

**Pain ID:** `low_citability` sigue siendo válido como oportunidad.
**Narrativa sugerida:** " contenido no discoverable por IAs"

---

### Archivos relacionados

- `/mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/audit_report.json` → lines 161-168
- `/mnt/c/Users/Jhond/Github/iah-cli/modules/commercial_documents/v4_diagnostic_generator.py:1850-1860` → pain_id `low_citability`
- `/mnt/c/Users/Jhond/Github/iah-cli/modules/commercial_documents/v4_diagnostic_generator.py:1851-1854` → score evaluation logic

---

## Errores de Consistencia Regional (Plantilla diagnostico_v6)

**Fecha:** 2026-04-09
**Hotel:** amaziliahotel.com
**Estado:** Corregido en archivo generado, pendiente en template fuente

---

### Hallazgo: Inconsistencias regionales en contexto regional

El documento generado `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260408_213710.md` contenía errores de consistencia:

1. Línea 21: "Lo que está pasando en **nacional**" → deberia ser "el Eje Cafetero"
2. Línea 27: typo "**yRevisan**" (sin espacio) + mención "**nacional**"
3. Línea 35: "La región de **nacional** en Colombia" → deberia ser "del Eje Cafetero"
4. Línea 37: pregunta clave mencionaba "zona de **nacional**"
5. Líneas 55-57: fuentes de benchmarks decia "**Nacional**" x3

**Todos los errores:** El texto de región dice "nacional" cuando el contexto dice "Eje Cafetero".

---

### Causa Raíz

El texto "nacional" viene de la variable `${hotel_region}` cuando el hotel no tiene una región específica en el mapping de `_build_regional_context()`.

El typo `yRevisan` es texto **hardcodeado directamente** en el template `diagnostico_v6_template.md:27`, no es una variable.

---

### Fuentes en template

| Archivo | Línea | Contenido |
|---------|-------|-----------|
| `templates/diagnostico_v6_template.md` | 21 | `### Lo que está pasando en ${hotel_region}` |
| `templates/diagnostico_v6_template.md` | 27 | `\| Entran a Google yRevisan 5 webs \| ... ${hotel_region}? \|` |
| `templates/diagnostico_v6_template.md` | 35 | `${regional_context}` (línea 35 del template inyecta línea 1627) |
| `modules/commercial_documents/v4_diagnostic_generator.py` | 1627 | `return f"La región de {region} en Colombia..."` |
| `modules/commercial_documents/v4_diagnostic_generator.py` | 413 | `hotel_region = region or "Colombia"` |

---

### Fallback en _build_regional_context()

Cuando la región NO está en el mapping de `region_contexts` (líneas 1613-1620), se usa:

```python
return f"La región de {region} en Colombia presenta oportunidades..."
```

El problema: cuando region = "Nacional" o valor genérico, dice "La región de Nacional" — que es redundante/incorrecto.

---

### Typo yRevisan

Error en `diagnostico_v6_template.md:27`:
```
| Entran a Google yRevisan 5 webs | ...
```
**Corrección necesaria:** `yRevisan` → `y Revisan` (falta espacio)

---

### Veredicto

**Errores de plantilla, no de generación.**
Los errores ocurren porque:
1. `${hotel_region}` se resuelve dinámicamente — si el hotel tiene region = "Nacional" (genérico), despliega "Nacional"
2. El typo `yRevisan` es texto hardcodeado estático en el template

**Las correcciones aplicadas al archivo generado NO persisten en futuras regeneraciones.**
El template debe ser corregido para que las próximas generaciones salgan bien.

---

### Acciones recomendadas

1. **Corregir typo en template:**
   - `templates/diagnostico_v6_template.md:27` → `yRevisan` → `y Revisan`

2. **Corregir fallback regional en generador:**
   - `v4_diagnostic_generator.py:1627` → cambiar "La región de {region}" por algo contextual
   - O agregar "Eje Cafetero" al mapping de `region_contexts` (líneas 1613-1620)

3. **Verificar región del hotel en onboarding:**
   - Si region = "Nacional" para hoteles del Eje Cafetero, es un error de captura
   - Revisar cómo se mapea la region en el flujo de onboarding

---

### Archivos a modificar

- `/mnt/c/Users/Jhond/Github/iah-cli/modules/commercial_documents/templates/diagnostico_v6_template.md` → corregir typo yRevisan
- `/mnt/c/Users/Jhond/Github/iah-cli/modules/commercial_documents/v4_diagnostic_generator.py:1627` → corregir texto fallback regional
