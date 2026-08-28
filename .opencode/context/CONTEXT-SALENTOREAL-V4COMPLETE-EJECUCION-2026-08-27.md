# CONTEXT — Ejecución E2E v4complete Hotel Salento Real: NameError latente en main.py + bloqueo estructural proposal_asset_alignment (SALENTOREAL-2026-08-27)

> **Fecha**: 2026-08-27
> **Alcance**: Ejecución de prueba E2E de `v4complete` para `https://www.hotelsalentoreal.com/` (con y sin query string UTM), análisis de comportamiento del pipeline completo, corrección de un bug blocker detectado en vivo, y caracterización del bloqueo estructural recurrente del gate `proposal_asset_alignment`.
> **Origen**: Solicitud de prueba v4complete para Hotel Salento Real (Eje Cafetero) con informe de comportamiento. La corrida reveló un crash (NameError) en FASE 3 que solo se manifiesta con `--output` alternativo, y confirmó un bloqueo estructural ya visto en Zione (2026-07-23).
> **Método**: Corridas E2E reales (3: una con output por defecto pre-existente, dos con output aislado), lectura de artefactos (gate_report, delivery_quality_report, proposal_asset_matrix, pain_ledger, coherence_validation, commercial_gates_report ×2), diff corrida-a-corrida, y cruce con lecciones L-NC1–L-NC12 del plan REFACTOR-COHERENCIA-NARRATIVA-2026-08-22.
> **Versión actual del sistema**: v4.72.2
> **Estado de validación**: ✅ Todos los hallazgos verificados contra artefactos reales de las corridas + código vivo (`main.py`, `output/test_salentoreal_v4c/`, `output/v4_complete/`). **Re-validación exhaustiva 2026-08-27**: 6/6 hallazgos CONFIRMADOS contra código vivo + disco; 1 corrección de hecho (nombre del helper); 4 hallazgos nuevos (N1–N4, ver §9.5).

---

## Veredicto Ejecutivo

La prueba E2E cumplió su función: **encontró 1 bug blocker real que ninguna prueba unitaria cubría** (NameError por `logger` inexistente en `main.py`, corregido en vivo) y **confirmó que el bloqueo de `proposal_asset_alignment` es estructural y recurrente** (3ª manifestación: Zione jul-2026, Salento 18:03, Salento 18:30), con una causa raíz nueva identificada: **tres capas contabilizan distinto el mismo hecho** (7 servicios prometidos).

**Estado final del hotel**: `NOT_READY` — 12/13 publication gates PASSED, coherencia 0.86 (≥ 0.8 ✅), WhatsApp VERIFIED (100%), pero alineación propuesta-assets 43% (3/7) < 80%.

**Hallazgos** (6):

1. **[CORREGIDO] NameError `logger` en main.py** — crash duro en FASE 3; solo se activa con `--output` alternativo (rama FASE-D S7). Hermano directo de L-NC8/L-NC9 pero variante más severa: sin `except` que lo enmascare, mata el flujo con exit 1.
2. **Contaminación de `target_id` por query string** — los parámetros UTM de la URL llegan íntegros al ID de memoria (`hotel_hotelsalentoreal.com__utm_source_google_...`), rompiendo la reutilización de análisis previos (< 20 días).
3. **Bloqueo estructural `proposal_asset_alignment`** — la propuesta promete 7 servicios; 4 quedan "sin costo (fallback)" vía RC1 en el texto y `NO_BREACH` en la matriz, pero el gate los cuenta como `missing`. Los 4 servicios son 3 capas con 3 contabilizaciones distintas del mismo hecho.
4. **Paradoja del preflight `hotel_schema`** — el pain #1 (score 85) no puede generar su asset correctivo porque la evidencia del problema (0 schemas detectados) degrada la confianza del asset a 0.00 < 0.8.
5. **Varianza entre corridas** — misma URL, 3 horas de diferencia: 7→5 brechas detectadas, 7→5 assets generados, `llms_txt` pasó de "generado" a "already in production" (SitePresence).
6. **Gate comercial detecta claim falso y el flujo continúa** — `CG-CLAIM-VS-EVIDENCE` BLOCKING (el diagnóstico dice "no aparece" cuando GBP confirma `place_found=True`, 4.5★) se registra como "hidden from client" y la regeneración no corrige el claim.

---

## 1. Contexto de la Ejecución

### 1.1 Corridas

| # | Hora | URL | Output | Resultado |
|---|------|-----|--------|-----------|
| A (pre-existente) | 18:03 | Limpia (sin UTM) | `output/v4_complete/` (default) | NOT_READY 43% (1 gate), 7 assets, coherencia 0.8438 |
| B | 18:25–18:26 | Con UTM completo | `output/test_salentoreal_v4c/` | ❌ **CRASH** NameError FASE 3, exit 1 |
| C | 18:29–18:30 | Con UTM completo | `output/test_salentoreal_v4c/` | ✅ Completa (exit 0), NOT_READY 43%, 5 assets, coherencia 0.86 |

Comando (B y C):
```bash
python main.py v4complete --url "https://www.hotelsalentoreal.com/?utm_source=google&utm_medium=organic&utm_campaign=GoogleMyBusiness&partner=5792" --output output/test_salentoreal_v4c
```

### 1.2 Salud del entorno (pre-ejecución)

- `python main.py --doctor`: ALL CHECKS PASSED (validaciones, version sync 4.72.2, config 9/9, ecosistema 2 skills).
- API keys activas: DeepSeek ✅, Google/Maps ✅ (misma key), OpenAI ✅. PageSpeed ❌ (ver §6).
- Advertencias no bloqueantes: `ANTHROPIC_API_KEY` y `WEBDRIVER_PATH` ausentes.

### 1.3 Comportamiento de la URL con query string

| Componente | ¿Afectado por UTM? | Detalle |
|-----------|-------------------|---------|
| Detección de región | NO | `_detect_region_from_url` hace substring sobre URL completa → 'salento' → `eje_cafetero` ✅ |
| Nombre del hotel | NO | Derivado de `netloc` → "Hotelsalentoreal" ✅ |
| Scrapers / audit | NO | La URL con query funciona normalmente en audit ✅ |
| **`target_id` de memoria** | **SÍ** | `hotel_hotelsalentoreal.com__utm_source_google_utm_medium_organic_utm_campaign_googlemybusiness_partner_5792` ❌ (ver §3) |

---

## 2. Hallazgo 1 — NameError `logger` en main.py (CORREGIDO)

### 2.1 Síntoma

Corrida B murió al entrar a FASE 3 con:

```
File "main.py", line 1777, in run_v4_complete_mode
    logger.info(
NameError: name 'logger' is not defined
```

Exit code 1. El flujo completo (escenarios financieros, documentos, assets, gates) no se ejecutó.

### 2.2 Causa raíz

`main.py` **nunca define `logger`** (0 coincidencias para `import logging` / `getLogger` / `logger =` en todo el archivo). El bloque de fallback FASE-D (S7) en `run_v4_complete_mode` invocaba `logger.info()`:

```python
# main.py (pre-fix), dentro de run_v4_complete_mode
if onboarding_data is None and clientes_dir != Path("output/clientes"):
    _fallback_dir = Path("output/clientes")
    if _fallback_dir.exists() and any(_fallback_dir.glob("*_onboarding.yaml")):
        logger.info(  # ← NameError
```

La rama requiere las 3 condiciones simultáneas: (1) sin onboarding en el dir de salida custom, (2) `--output` ≠ default, (3) `output/clientes/*_onboarding.yaml` existe (hay uno de zi-one-luxury del 04-08). **La corrida estándar (output default) nunca entra en esta rama** — por eso A no crasheó y el bug pasó desapercibido hasta esta prueba.

### 2.3 Corrección aplicada (2026-08-27, +9/−4 en main.py)

| Sitio | Línea | Uso | Riesgo |
|-------|-------|-----|--------|
| Fallback onboarding FASE-D S7 | ~1777 | `logger.info(...)` | **Crash activo** — detonado por corrida B |
| Aviso staleness en BLOCKED_BY_GATES | ~2976 | `logger.warning(...)` | **Latente** — se activaría con `commercial_gates_report.json` más viejo que la propuesta (DT-4 D11b) |

Fix: reemplazo por `print(f"[INFO] ...")` / `print(f"[WARN] ...")`, idioma dominante del archivo. Verificación: `py_compile` OK; `grep "logger\."` en main.py = **0 coincidencias** (lección L2: sin residuos); la corrida C ejecutó la rama corregida (`[INFO] Onboarding not found in output\test_salentoreal_v4c\clientes, falling back to output\clientes` en log L155).

### 2.4 Relación con L-NC8/L-NC9 (clase de bug)

L-NC8/L-NC9 documentaron: `FinancialFactors` sin import + `except Exception` amplio → NameError **silencioso** degradado a gate BLOCKED falso (tier "C"). Este hallazgo es de la **misma clase con variante más severa**: aquí no hay `except` que enmascare, el NameError es un **crash duro**. La generalización correcta de la clase no es "except amplio" sino:

> **Símbolo no definido en una rama condicional no ejercitada por la corrida estándar.**

Dos instancias, dos síntomas distintos (gate falso / crash), misma raíz: código añadido en fases que referencia símbolos inexistentes y solo se ejecuta bajo condiciones particulares.

---

## 3. Hallazgo 2 — Contaminación de `target_id` por query string

**Log corrida C (L67)**:
```
[OK] Phase 1 iniciada: hotel_hotelsalentoreal.com__utm_source_google_utm_medium_organic_utm_campaign_googlemybusiness_partner_5792
```

El `target_id` de memoria se construye desde la URL **raw**, sin canonicalizar. Consecuencias:

1. La memoria de análisis (`agent_harness/memory.py`, vigencia < 20 días) registra la sesión bajo un ID distinto al de la URL limpia → `find_latest_analysis` / `_find_recent_v4_analysis` **no reutilizarán** el análisis de la corrida A para la URL con UTM, ni viceversa.
2. Los IDs polucionan listados y logs (legibilidad, debugging).
3. El helper correcto **ya existe**: `_normalize_url()` en `main.py:3542` (ignora protocolo, www, path y **query string**) — el gap está en el caller, no en la fuente (patrón L-NC6/L16). ⚠️ **CORRECCIÓN DE VALIDACIÓN**: el contexto original citó `_normalize_url_for_matching()`; ese símbolo **no existe** en el repo (grep = 0 en main.py y modules/). El helper real es `_normalize_url`. Cualquier fix futuro debe usar el nombre real.

Impacto: medio (no rompe la corrida; rompe la reutilización y encarece re-ejecuciones con cuota de APIs).

---

## 4. Hallazgo 3 — Bloqueo estructural `proposal_asset_alignment` (3ª manifestación)

### 4.1 Historial del bloqueo

| Fecha | Hotel | Alineación | Faltantes |
|-------|-------|-----------|-----------|
| 2026-07-23 | Zi One Luxury (zione.co) | 75% | SEO Local, Meta Tags OG |
| 2026-08-27 18:03 | Salento Real | 43% (3/7) | SEO Local, WhatsApp, Schema Hotel, Meta Tags OG |
| 2026-08-27 18:30 | Salento Real | 43% (3/7) | SEO Local, WhatsApp, Schema Hotel, Meta Tags OG |

**SEO Local (`optimization_guide`) y Meta Tags OG (`open_graph`) faltan en las 3 corridas** — son promesas estructuralmente vacías del catálogo de servicios desde al menos julio.

### 4.2 Causa raíz nueva: tres capas, tres contabilizaciones del mismo hecho

Estado de los 7 servicios prometidos en la corrida C:

| Servicio | Asset | Propuesta (RC1) | proposal_asset_matrix | Delivery G9 | Publication gate |
|----------|-------|-----------------|----------------------|-------------|------------------|
| SEO Local | optimization_guide | "sin costo (fallback)" | NO_BREACH | missing | **missing** ❌ |
| Botón de WhatsApp | whatsapp_button | "sin costo (fallback)" | NO_BREACH | missing | **missing** ❌ |
| Schema Hotel | hotel_schema | prometido (conf 1.0, pain `no_hotel_schema`) | **MISSING_ASSET** | missing | **missing** ❌ |
| Schema Organization | org_schema | LINKED | LINKED (0.8) | generado ✅ | generado ✅ |
| Página de FAQ | faq_page | LINKED | LINKED (0.8) | generado ✅ | generado ✅ |
| Meta Tags OG | open_graph | "sin costo (fallback)" | NO_BREACH | missing | **missing** ❌ |
| Optimización IA | llms_txt | "sin costo (fallback)" | NO_BREACH | **present_in_production** ✅ | **present_in_production** ✅ |

Observaciones verificadas:

1. **RC1 (`v4_proposal_generator.py`) declara "sin costo"** para 4 servicios porque sus brechas candidatas (`low_seo_score`, `whatsapp_conflict`, `no_og_tags`, `missing_llmstxt`…) no están en `opportunity_scores` — warning por log, el texto de la propuesta los trata como adicionales sin compromiso.
2. **La matriz** respeta esa decisión (`NO_BREACH`, `pain_ids: []`).
3. **El publication gate ignora el estado NO_BREACH** y los cuenta como `missing` en `coverage_ratio` (3/7 = 0.4286 < 0.80 → BLOCKED).
4. La fuente de la promesa (catálogo de servicios del tier) **no se deriva del pain_ledger** (5 pains → 4 assets), mientras que el plan de assets sí. Promesa y plan provienen de fuentes distintas que nadie reconcilia — la versión de gating de la "fosilización narrativa" (L-NC10): la capa de promesa no consume la fuente dinámica de verdad.

### 4.3 Efecto en cascada (funcionamiento correcto del never-block)

La corrida C completó y los mecanismos de protección operaron como diseñados: `BLOCKED_BY_GATES.md` generado, documentos cliente (01/02) eliminados, Delivery Quality FAIL 4/5 (G9), **ZIP abortado**, human checklist de 3 items emitido. El bloqueo es "correcto" dada la promesa; el defecto está aguas arriba, en la composición de la promesa.

Dato menor verificado: el mensaje interno de G9 dice "3/7 servicios cubiertos … — **1 sin cubrir**" mientras su propio `unresolved: 1` y `coverage_ratio: 0.4286` indican 4 sin cubrir (2+1+1=4 de 7). Redacción del mensaje desalineada con sus propios datos.

---

## 5. Hallazgo 4 — Paradoja del preflight `hotel_schema`

- Pain #1 del hotel: `no_hotel_schema` (score 85, severity HIGH, $1.06M COP/mes estimados). El audit confirma: **0 schemas encontrados**.
- Preflight FASE 4: `hotel_schema: Insufficient confidence (0.00 < 0.8)` → **asset no generado**.
- `coherence_validation.json`: check `promised_assets_exist` **FAILED** (severity error): "Assets no implementados: hotel_schema", score 0.9 — pero el gate de coherencia publica 0.86 (usa score agregado, no el flag `is_coherent: false` del mismo archivo).
- `pain_ledger_resolved.json`: `no_hotel_schema` queda `DETECTED` (no `ASSET_GENERATED`); `mapped_to_service: 0`, `justified_skip: 0`.

**La paradoja**: la evidencia del problema (ausencia total de schemas) es lo que reduce a 0.00 la confianza del asset que lo corrige. El pain más severo del hotel es estructuralmente irresoluble por el pipeline autónomo. Nota: `geo_enriched/hotel_schema_rich.json` y `faq_schema.json` sí se generan en la rama GEO, pero no cuentan como asset `hotel_schema` para ningún gate.

---

## 6. Hallazgo 5 — Varianza entre corridas (A 18:03 vs C 18:30)

| Métrica | Corrida A | Corrida C | Delta |
|---------|-----------|-----------|-------|
| Brechas detectadas (plan de assets) | 7 (incl. `low_ia_readiness`, `ai_crawler_blocked`) | 5 | −2 |
| Assets generados | 7 (incl. `llms_txt`, `local_content_page`) | 5 | −2 |
| `llms_txt` | Generado (conf 1.0) | present_in_production (SitePresence) | cambia de categoría |
| Coherencia final | 0.8438 | 0.8644 | +0.02 |
| Gate bloqueante | proposal_asset_alignment | proposal_asset_alignment (idéntico) | 0 |
| Escenarios financieros | $6.57M / $4.04M / $1.26M | idénticos | 0 (determinista) |

La capa financiera es determinista; la capa de brechas/assets **no lo es** entre corridas separadas por horas, con la misma URL efectiva (verificado en disco: pain_ledger A=7 pain_ids, C=5 pain_ids; asset_generation_report A=7 assets, C=5 assets). **CORRECCIÓN DE VALIDACIÓN sobre la hipótesis**: el contexto original conjeturó que `ai_crawler_blocked` "desaparece si el audit mide robots 1.00/1.00". La verificación directa (grep en AMBOS `audit_report`) muestra que `ai_crawler_blocked` **no aparece en ninguno de los dos** ledger (grep = 0 en A y en C). Lo que cambia entre corridas no es "que desaparezca una brecha por robots accesibles", sino que el pain_id simplemente no está presente en el ledger de C (filtro estable por hotel, no condicional a robots). `low_ia_readiness` es el otro pain_id ausente en C. Hipótesis de investigación revisada: `pain_solution_mapper` (o cache de audit/SitePresence) aplica un filtro distinto entre corridas que excluye estos dos pain_ids de forma determinista, no por score de robots. Requiere investigación en `pain_solution_mapper.py`.

---

## 7. Hallazgo 6 — PageSpeed API key inválida + claim falso no ciclado

1. **PageSpeed**: `[3/5] Status: ERROR — API key not valid. Please pass a valid API key.` La misma `GOOGLE_API_KEY` funciona para Places (GBP 4.5★/984 reseñas/5 competidores). La performance del sitio entra sin datos (no bloquea, degrada evidencia).
2. **`CG-CLAIM-VS-EVIDENCE` (BLOCKING) sin ciclo de corrección**: el gate comercial del diagnóstico detectó "El documento dice 'no aparece' (factual) pero place_found=True y rating=4.5/5.0". El flujo lo registró como `WARNING:root:Diagnostic commercial gates BLOCKING (hidden from client)` y **continuó** — el diagnóstico regenerado post-FASE 4 no corrigió el claim. Detectar el claim falso sin forzar su corrección deja pasar exactamente la erosión de credibilidad que el gate existe para prevenir (misma familia que L-NC10/L30: la narrativa no se sincroniza con los datos).
3. **`CG-TIER-CONSISTENCY`**: frontmatter dice tier 'B', el texto dice tier 'D' (WARNING). Igual familia: display string desincronizado de la fuente financiera (L30).
4. `CG-TECH-JARGON` (WARNING en ambas evaluaciones): jerga (Schema, AEO, IAO, Open Graph) en vista gerencia — inconsistente con la decisión comercial de lenguaje de negocio.

---

## 8. Aplicación de Lecciones Aprendidas (REFACTOR-COHERENCIA-NARRATIVA-2026-08-22)

### 8.1 Lecciones capitalizadas en esta ejecución

| Lección | Aplicación en esta ejecución |
|---------|------------------------------|
| **L-NC8/L-NC9** (NameError por símbolo faltante, except amplio) | El crash de FASE 3 es la 2ª instancia de la clase en 4 días. Confirmó la generalización: la clase es "símbolo no definido en rama no ejercitada", con o sin except que enmascare. El fix siguió la prevención de L-NC9 punto 1: "ejecutar el bloque una vez" (la corrida C ejecutó exactamente la rama corregida). |
| **L-NC10** (fosilización narrativa) | 2 manifestaciones nuevas en capa de datos/gating: (a) propuesta promete servicios sin derivarlos del pain_ledger (§4.2); (b) claim "no aparece" contradicho por GBP propio (§7.2). La clase "capa narrativa/decisoria que no consume la fuente de verdad" sigue produciendo hallazgos. |
| **L-NC11** (verificación E2E > unit tests) | **Validación empírica**: el NameError no estaba cubierto por ninguna de las 3,379 tests unitarios; solo una corrida E2E con condiciones no estándar (`--output` custom) lo detonó. Refuerza: los E2E deben cubrir variaciones de parámetros, no solo la ruta feliz. |
| **L-NC12** (diff antes/después como evidencia) | El diff A-vs-C (7→5 assets, llms_txt generado→producción, gates idénticos) fue la herramienta que reveló la varianza (§6) y descartó regresión financiera. |
| **L30** (tras parametrizar, verificar strings de display) | CG-TIER-CONSISTENCY 'B' vs 'D': la fuente financiera dice B, el texto muestra D. Instancia viva de la lección. |
| **L27** (citar fuente de verdad, no hardcodear) | El diagnóstico cita pain_ledger correctamente (coverage_no_silent_drop 5/5 ✅) pero la PROPUESTA promete del catálogo estático de servicios — mitad del sistema cumple L27, mitad no. |
| **L2** (grep de residuos post-fix) | Aplicado: `grep "logger\."` en main.py = 0 tras el fix. |
| **L16** (el gap está en el caller) | Caso target_id: `_normalize_url()` ya existe (main.py:3542); falta invocarla al construir el target_id (§3). ⚠️ El contexto original escribió `_normalize_url_for_matching` (inexistente). |

### 8.2 Lecciones nuevas (formato qué pasó / por qué / qué lo previene)

| ID | Lección | Fuente |
|----|---------|--------|
| L-SR1 | **Las ramas no ejercitadas por la corrida estándar acumulan defectos latentes.** / Qué pasó: el fallback FASE-D S7 con `logger` inexistente convivió con el código desde su fase sin detonar hasta una prueba con `--output` alternativo. / Por qué: la corrida estándar (output default) nunca evalúa la condición `clientes_dir != Path("output/clientes")`, así que el código muerto-en-práctica no se ejecuta en ninguna validación regular. / Qué lo previene: (1) smoke E2E periódico con `--output` alternativo como variación de parámetros; (2) tras cada fase, grep de símbolos sospechosos en ramas nuevas (`logger\.`, imports no usados); (3) test estático que compile main.py y verifique ausencia de referencias a símbolos no definidos. INCLUIR (memoria ya registrada 2026-08-27). | Corrida B |
| L-SR2 | **La identidad de memoria debe derivarse de la URL canónica, no de la raw.** / Qué pasó: los UTM params llegaron íntegros al `target_id`, fragmentando la memoria del mismo hotel en N identidades según cómo se pegue el link. / Por qué: el caller construye el ID antes de canonicalizar, pese a existir `_normalize_url()` (main.py:3542; el contexto lo nombró mal como `_normalize_url_for_matching`, símbolo inexistente). / Qué lo previene: pasar toda URL por el normalizador canónico como primer paso de `run_v4_complete_mode` (y `onboard`, `execute`, `validate-guarantee`), usando la versión normalizada para target_id y la original solo para scraping. INCLUIR. | Log L67 |
| L-SR3 | **Promesa, matriz y gate deben compartir UNA fuente de verdad para el estado de un servicio.** / Qué pasó: RC1 declara "sin costo", la matriz registra NO_BREACH, y el gate cuenta missing — el mismo servicio está "no comprometido" y "faltante" según el artefacto que se lea, y el bloqueo resultante (43%) sorprende porque el propio generador de propuesta "sabía" que esos 4 servicios no tenían costo/compromiso. / Por qué: la composición de la propuesta viene del catálogo de servicios del tier (estático), no del pain_ledger (dinámico); el gate evalúa contra la promesa estática. / Qué lo previene: (1) que el catálogo de servicios prometidos se derive del pain_ledger + assets disponibles (present_in_production cuenta); (2) que el gate respete el estado NO_BREACH o que RC1 deje de emitirlo; nunca ambos criterios en paralelo (extensión de L-NC10 a la capa de gating). INCLUIR. | §4.2 |
| L-SR4 | **La confianza de un asset no debe degradarse por la evidencia del problema que resuelve.** / Qué pasó: `hotel_schema` (pain #1, score 85) quedó bloqueado por preflight 0.00 < 0.8 precisamente porque el sitio tiene 0 schemas — más evidencia del problema = menos confianza del correctivo. / Por qué: el preflight confunde "confianza en los datos de entrada" con "confianza en la implementación del asset"; con 0 schemas no hay qué verificar, pero el asset correctivo es precisamente más necesario y su contenido derivable del GBP (nombre, dirección, rating — todos presentes). / Qué lo previene: separar ambas confianzas; cuando la brecha es "ausencia de X", la confianza del asset debe calcularse desde las fuentes disponibles para construir X (GBP/web), no desde la presencia de X. INCLUIR. | §5 |
| L-SR5 | **Un gate BLOCKING que solo loggea no previene: debe ciclar o escalar.** / Qué pasó: `CG-CLAIM-VS-EVIDENCE` detectó un claim factualmente falso en el diagnóstico ("no aparece" vs GBP 4.5★), se marcó BLOCKING y "hidden from client", y el flujo siguió publicando el mismo claim en la versión final. / Por qué: el resultado del gate no se inyecta de vuelta en la regeneración del documento (no hay self-healing loop para claims), solo se archiva. / Qué lo previene: al detectar claims vs evidencia, regenerar la sección con el `suggestion` del gate como restricción (el gate ya provee el texto trazable correcto) y re-validar; si persiste, escalar a BLOCKED real. INCLUIR. | §7.2 |

---

## 9. Recomendaciones Priorizadas (semilla de plan futuro)

| # | Prioridad | Recomendación | Hallazgo | Lección |
|---|-----------|---------------|----------|---------|
| 1 | **P0** | Unificar contabilidad promesa/matriz/gate: derivar servicios prometidos del pain_ledger + present_in_production, o hacer que el gate respete NO_BREACH. Resuelve el bloqueo estructural recurrente (Zione jul + Salento ago). | §4 | L-SR3, L-NC10 |
| 2 | **P0** | Self-healing loop para `CG-CLAIM-VS-EVIDENCE`: regenerar sección con el suggestion del gate y re-validar. | §7.2 | L-SR5 |
| 3 | **P1** | Canonicalizar URL antes de construir `target_id` (usar `_normalize_url` en `main.py:3248/3394/3460` y todos los comandos con `--url`). ⚠️ El helper real es `_normalize_url` (no `_normalize_url_for_matching`). | §3, N3 | L-SR2, L16 |
| 4 | **P1** | Rediseñar preflight de `hotel_schema`: confianza desde fuentes disponibles (GBP/web), no desde presencia de la brecha. | §5 | L-SR4 |
| 5 | **P2** | Investigar varianza del plan de assets entre corridas (7→5 brechas; `ai_crawler_blocked` desaparece con robots 1.00 en ambas). | §6 | L-NC12 |
| 6 | **P2** | Corregir/rotar la API key de PageSpeed (la de Maps funciona; verificar si son keys distintas en settings.yaml). | §7.1 | — |
| 7 | **P3** | Alinear mensaje interno de G9 con sus propios contadores ("1 sin cubrir" vs unresolved 4). | §4.3 | L30 |
| 8 | **P3** | CG-TIER-CONSISTENCY ('B' vs 'D') y CG-TECH-JARGON: strings de display contra fuente financiera / lenguaje de negocio en vista gerencia. | §7.3-7.4 | L30, L27 |
| 9 | **P0** | Unificar conteo `unresolved` de G9 en UN helper `AlignmentResult.compute_unresolved()` usado por `gate_report` y `delivery_quality_report` (elimina la divergencia 4-vs-1 del mismo run). | N1 | — |
| 10 | **P1** | Canonicalizar `target_id` con `_normalize_url()` en `main.py:3248/3394/3460` (y onboard/execute/validate-guarantee) para evitar fragmentación de memoria y costo de API repetido. | N3, §3 | L-SR2 |
| 11 | **P1** | Hacer que el preflight de `hotel_schema` respete `fallback`+`block_on_failure=False` del catálogo (o eliminar el fallback si realmente no debe generarse). | N4, §5 | L-SR4 |

Criterio de éxito sugerido para un plan sobre #1+#2: una corrida v4complete de Salento Real con `readiness: READY_FOR_PUBLICATION` y 0 falsos claim-fact gates, sin tocar la capa financiera (determinista, intacta).

---

## 9.5 Re-validación contra código vivo y hallazgos amplificados (2026-08-27, post-escritura)

Veredicto de re-auditoría: los 6 hallazgos originales fueron verificados contra código vivo y artefactos en disco (24 comprobaciones: grep, ls directo, read_file, json en disco, run logs, git log). Resultado: **6/6 CONFIRMADOS**. 1 corrección de hecho (nombre del helper, ver §9.5.1). 4 hallazgos nuevos (N1–N4).

### 9.5.1 Corrección de hecho
- **Nombre del helper** (afecta §3, §8.2 L-SR2, §9 #3): el contexto cita `_normalize_url_for_matching()` como existente en main.py. Verificación: ese símbolo **NO existe** en todo el repo (grep = 0 en main.py y modules/). El helper real es `_normalize_url()` en `main.py:3542`, que sí ignora protocolo/www/path/query string. Toda recomendación/fix debe usar `_normalize_url`.

### 9.5.2 Hallazgos nuevos (amplificación)

| ID | Hallazgo | Evidencia (código vivo / disco) | Causa raíz | Recomendación causa raíz |
|----|----------|--------------------------------|-----------|--------------------------|
| N1 | **G9 divergente entre dos reportes del MISMO run** | `gate_report` (gate_results[8]): unresolved=4, mensaje "4 sin cubrir". `delivery_quality_report`: unresolved=1, mensaje "1 sin cubrir". coverage_ratio idéntico (0.4286). | Dos caminos de código computan `unresolved` distinto: `gate_report`→`verify_proposal_asset_alignment`→`AlignmentResult.from_alignment_report` (publication_gates.py:903); `delivery_quality_report`→reconstruye desde `proposal_asset_matrix.json`+SitePresence (delivery_quality_report.py:235). | Unificar el conteo en UN helper `AlignmentResult.compute_unresolved()` llamado por AMBOS reportes. No parchear el texto del mensaje. |
| N2 | **Nombre del helper incorrecto** (ver §9.5.1) | grep `_normalize_url_for_matching` = 0 en repo; `_normalize_url` en main.py:3542. | El contexto transcribió mal el nombre del símbolo. | Usar `_normalize_url` en todo fix/recomendación. |
| N3 | **target_id crudo rompe reutilización de memoria** (impacto de H2 subestimado) | `main.py:3248/3394/3460` graban `target_id=args.url` crudo vía `memory.append_log`/`save_analysis_reference`; `find_latest_v4_analysis` (665) busca por ese ID. A (URL limpia) y C (URL con UTM) = mismo hotel, 2 identidades distintas en `agent_harness/memory.py`. | El ID de memoria se construye antes de canonicalizar; cada variación de link de campaña fragmenta la memoria y fuerza re-ejecución del audit (costo de API repetido: PageSpeed cae, GBP se reconsulta). | Impacto MEDIO-ALTO (no medio): canonicalizar con `_normalize_url` antes de `main.py:3248/3394/3460`. |
| N4 | **Fallback de hotel_schema no se invoca** (raíz de H4 más profunda) | `asset_catalog.py:92` hotel_schema: `fallback="generate_basic_schema"`, `block_on_failure=False` → debería generarse desde GBP. Pero `coherence_validator._check_promised_assets_exist` (543/611) marca MISSING_ASSET porque no se generó; el preflight de confianza 0.00 (linker/orchestrator) mata la generación antes. | Dos contratos contradictorios para el mismo asset: el catálogo DICE "puedo generar con fallback" pero el preflight lo bloquea. | El preflight debe respetar `fallback`+`block_on_failure=False` del catálogo, o eliminar el fallback si realmente no debe generarse. Nunca ambos. |

### 9.5.3 Estado de compromiso del fix H1
El contexto (§2.3, §11) marcó el fix `logger` como "pendiente de commit del usuario". Verificación: **YA ESTÁ COMITEADO** en `d8e509d` (2026-08-27 18:59, "fix(v4complete): NameError logger en main.py + contexto E2E Salento Real"). `grep "logger\." main.py` = 0 (sin residuos). No requiere acción de commit adicional.

## 10. Evidencia y Artefactos

| Artefacto | Ruta |
|-----------|------|
| Log corrida B (crash) | `temp/test_salentoreal_v4c_run.log` |
| Log corrida C (completa) | `temp/test_salentoreal_v4c_run2.log` |
| Reporte integral corrida C | `output/test_salentoreal_v4c/v4_complete/v4_complete_report.json` |
| Gate report (13 gates) | `output/test_salentoreal_v4c/v4_complete/hotelsalentoreal/v4_audit/gate_report_20260827_183051.json` |
| Delivery quality (G7-G9) | `.../v4_audit/delivery_quality_report.json` |
| Matriz propuesta-assets | `.../v4_audit/proposal_asset_matrix.json` |
| Pain ledger resuelto | `.../v4_audit/pain_ledger_resolved.json` |
| Coherencia (post-gen) | `.../v4_audit/coherence_validation.json` |
| Gates comerciales diagnóstico / propuesta | `.../v4_audit/commercial_gates_report_diagnostic_20260827_183051.json` / `commercial_gates_report.json` |
| BLOCKED_BY_GATES | `output/test_salentoreal_v4c/v4_complete/BLOCKED_BY_GATES.md` |
| Corrida A (output default, 18:03) | `output/v4_complete/{BLOCKED_BY_GATES.md, v4_complete_report.json, hotelsalentoreal/}` |
| Fix aplicado | `main.py` (+9/−4, sitios ~1777 y ~2976; sin commit — pendiente de decisión del usuario) |
| Precedente histórico | `.opencode/context/Historico/ZIONE-PROPOSAL-ASSET-ALIGNMENT-BLOCK-2026-07-23.md` |
| Lecciones fuente | `.opencode/plans/REFACTOR-COHERENCIA-NARRATIVA-2026-08-22/10-analisis-post-implementacion.md` (L-NC1–L-NC12) |

---

## 11. Seguimientos Abiertos

| Tema | Estado | Acción |
|------|--------|--------|
| Fix `logger` en main.py (2 sitios) | ✅ CORREGIDO + **YA COMITEADO** (d8e509d, 2026-08-27) | `grep "logger\." main.py` = 0; considerar test estático anti-`logger.` como guardián |
| Gate `proposal_asset_alignment` estructural | 🔴 ABIERTO (3ª manifestación) | Recomendación #1 — candidato a plan dedicado |
| Self-healing para CG-CLAIM-VS-EVIDENCE | 🔴 ABIERTO | Recomendación #2 |
| target_id con query string | 🔴 ABIERTO | Recomendación #3 (gap en caller, helper existente) |
| Preflight hotel_schema paradoja | 🔴 ABIERTO | Recomendación #4 |
| Varianza plan de assets entre corridas | 💡 INVESTIGAR | Recomendación #5 |
| PageSpeed API key | 💡 OPS | Recomendación #6 |
| G9 divergente 4-vs-1 (gate_report vs delivery_quality) | 🔴 ABIERTO (no detectado en corrida original) | Recomendación #9 (N1) |
| target_id fragmenta memoria (costo API repetido) | 🔴 ABIERTO | Recomendación #10 (N3) |
| Preflight hotel_schema ignora fallback del catálogo | 🔴 ABIERTO | Recomendación #11 (N4) |
| Nombre helper `_normalize_url_for_matching` (inexistente) | ✅ CORREGIDO (es `_normalize_url`) | Actualizar toda referencia futura |
