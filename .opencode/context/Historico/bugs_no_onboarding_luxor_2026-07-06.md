# Bugs NO relacionados con onboarding — v4complete Luxorhotel

> **Fecha detección:** 2026-07-06
> **Fecha evaluación:** 2026-07-06
> **Ejecución:** `main.py v4complete --url http://www.luxorhotel.com.co/`
> **Motor:** v4.60.0
> **Propósito:** Evaluar viabilidad de intervención (fix) para cada bug
> **Doctrina:** Validate-against-live-code — cada bug verificado contra código vivo del repo

---

## BUG-1: lat:0.0, lng:0.0 — Places API no resuelve coordenadas

- **Línea log:** 1 (`ejecucion.log`)
- **Mensaje:** `No places found for lat:0.0, lng:0.0`
- **Causa raíz (VERIFICADA en código):** `modules/auditors/v4_comprehensive.py:1159-1160` — `_audit_competitors()` pasa `lat=0.0, lng=0.0` hardcoded con comentario `# TODO: Get from geocoding`. Pero `gbp_result` SÍ tiene coords reales: `v4_comprehensive.py:799-800` asigna `lat=places_result.lat, lng=places_result.lng` desde Places API. La skill `iah-cli-data-source-debug` confirma que el fix D1 ya añadió `lat`/`lng` a `GBPApiResult`. El campo existe, simplemente no se usa en `_audit_competitors`.
- **Impacto:**
  - Competidores: solo 1 encontrado (debería ser más)
  - Geo Score: 61/100 (potencialmente degradado)
  - `geo_flow_result.json` con datos incompletos
  - Afecta score competitivo y AEO (competitiva local) de forma silenciosa
- **Skill ref:** `iah-cli-data-source-debug` — fix D1 (lat/lng ya en GBPApiResult)
- **No resolvible con onboarding** porque onboarding no entrega lat/lng.

### Alcance del fix

- **Archivos:** 1 — `modules/auditors/v4_comprehensive.py`
- **Cambio:** L1159-1160 → `lat=gbp_result.lat, lng=gbp_result.lng`
- **Validación adicional:** si lat/lng son 0.0 o fuera de rango Colombia (lat 0-13, lng -82 a -66), `return []` sin llamar a `search_nearby_lodging` con coords nulas.
- **Complejidad:** Baja — 2 líneas + validación de rango.

### Pruebas

- `tests/test_google_places_client.py` ya existe.
- Test de regresión: `_audit_competitors` con `gbp_result.lat=4.8, lng=-75.7` debe llamar `search_nearby_lodging` con esos valores (mock `CompetitorAnalyzer`).
- Test edge: `gbp_result` con `lat=0.0` → retorna `[]` sin llamar API.

### Prioridad: P1 (Alta)

Afecta datos de salida y scores de forma silenciosa. El dato ya existe en `gbp_result`, solo no se usa.

### Viabilidad: ALTA — entra en la planificación.

---

## BUG-2: calc_result UnboundLocalError en FinancialBreakdown

- **Línea log:** 185 (`ejecucion.log`)
- **Mensaje:** `cannot access local variable 'calc_result' where it is not associated with a value`
- **Módulo:** FASE-K en `main.py` (NO es FinancialBreakdown handler — el handler en `harness_handlers.py` está correcto)
- **Causa raíz (VERIFICADA en código):** `main.py:1942` — dentro del try (L1927-1944) se ejecuta:
  ```python
  print(f"   Source reliability: {calc_result.metadata.get('source_reliability', 'unknown')}")
  ```
  `calc_result` NO existe en este scope. Es una variable del handler de harness (`harness_handlers.py:120`), no de `main.py`. El error se atrapa en L1943 except e imprime "FinancialBreakdown fallo".
- **Impacto REAL (MENOR al descrito originalmente):**
  - `financial_breakdown` YA fue asignado en L1939 (`_sc.calculate_breakdown`) ANTES del error en L1942.
  - El objeto `financial_breakdown` sobrevive y se usa correctamente en L1948-1962.
  - El "fallback hardcoded" que menciona el doc original NO es causado por este bug: `scenario_calculator.py:471-474` usa sources `'hardcoded: sin GA4'` por diseño (CAPA 2A/2B son hipótesis sin GA4, no por el UnboundLocalError).
  - `ota_commission_cop` ($7.741.440) se calcula OK.
  - El evidence tier/disclaimer son los que corresponden por las fuentes de datos reales.
  - **Impacto real: ruido en log (warning falso), sin impacto en output.**
- **No resolvible con onboarding** — es bug de código Python puro.

### Alcance del fix

- **Archivos:** 1 — `main.py`
- **Cambio:** L1942 → remover la línea entera (no aporta nada: `financial_breakdown` ya tiene su propio `evidence_tier` y `disclaimer`), o reemplazar `calc_result.metadata` por una referencia válida del scope (ej. `financial_breakdown.evidence_tier`).
- **Complejidad:** Muy baja — 1 línea.

### Pruebas

- `tests/test_financial_breakdown.py` ya existe.
- Test: ejecutar FASE-K con datos reales → no debe imprimir warning.
- Test: `financial_breakdown` debe tener `evidence_tier` y `disclaimer` no nulos.

### Prioridad: P3 (Baja)

Cosmético, no afecta output ni scores.

### Viabilidad: ALTA — entra en la planificación.

---

## BUG-4: LLM providers caídos (openrouter 404, gemini 403)

- **Líneas log:** 3-12 (`ejecucion.log`)
- **Mensajes:**
  - `LLM query failed for openrouter: 404 Client Error: Not Found`
  - `LLM query failed for gemini: 403 Client Error: Forbidden`
- **Causa raíz (VERIFICADA en código) — DOS sub-problemas con naturaleza distinta:**

  **openrouter 404 (FIX DE CÓDIGO):** `modules/auditors/llm_mention_checker.py:239` hardcodea `"model": "google/gemini-2.0-flash-001"`. El 404 indica que ese modelo fue removido/renombrado en OpenRouter. El `provider_registry.yaml` declara `default_model: qwen/qwen3.6-plus:free` pero NO se usa — el modelo está hardcoded en el `.py`.

  **gemini 403 (CONFIG/INFRA — fuera de planificación):** `llm_mention_checker.py:100` lee `GEMINI_API_KEY`. NO existe en `.env`. El log muestra `key=AIzaSy...KJB8` que es `GOOGLE_MAPS_API_KEY` (no tiene permisos de Generative Language API). Hay un env_loader que mapea `GOOGLE_MAPS_API_KEY` → `GOOGLE_API_KEY` (el log imprime `[OK] GOOGLE_API_KEY: AIza...KJB8`) pero eso NO es `GEMINI_API_KEY`.

- **Impacto:**
  - Solo DeepSeek funcionó como LLM provider
  - Si DeepSeek cae, el pipeline completo falla — sin redundancia real
  - Los LLM calls que fallaron son: generación de contenido, análisis semántico, validación
- **Config relevante:** `.env` → `DEEPSEEK_API_KEY`, `OPENROUTER_API_KEY`, `OPENAI_API_KEY`. Falta `GEMINI_API_KEY`.
- **No resolvible con onboarding** — es infraestructura/API keys.

### Alcance del fix

**Parte CÓDIGO (openrouter — planificable):**
- **Archivos:** 1-2 — `modules/auditors/llm_mention_checker.py` + `config/provider_registry.yaml`
- **Cambio:** Externalizar el modelo al `provider_registry.yaml` (el campo `default_model` ya existe). `llm_mention_checker.py:239` debe leer del registry, no hardcodear.
- **Pre-requisito:** verificar catálogo OpenRouter actual para confirmar qué modelo vigente reemplaza a `google/gemini-2.0-flash-001` (consulta a https://openrouter.ai/models — no al código).
- **Complejidad:** Baja de código, media de integración.

**Parte CONFIG (gemini — fuera de planificación):**
- Requiere: crear `GEMINI_API_KEY` en Google AI Studio (https://aistudio.google.com/apikey) y añadirla a `.env`.
- Es infraestructura/credenciales, no fix de código. El código ya lee `GEMINI_API_KEY` correctamente (L100).
- **Acción del usuario:** generar la key y añadirla manualmente a `.env`.

### Pruebas

- No hay tests de LLM providers vivos (requieren API keys reales).
- Test unitario (automatizable): mock `_query_openrouter` verificando que el payload usa el modelo del `registry` (no hardcoded).
- Test de integración: requiere `OPENROUTER_API_KEY` real — marcar `@pytest.mark.skipif`.
- Prueba manual post-config (gemini): ejecutar `python main.py v4complete --url http://www.luxorhotel.com.co/` y verificar que el log NO muestre `LLM query failed for gemini: 403`.

### Prioridad: P2 (Media)

Afecta resiliencia del pipeline, pero DeepSeek funciona.

### Viabilidad: PARCIAL

- openrouter (externalizar modelo): **SÍ** entra en la planificación.
- gemini (configurar API key): **NO** entra en la planificación — es acción manual del usuario sobre `.env`.

---

## BUG-5: Content Scrubber bypass inicial en FASE 3.6

- **Líneas log:** 249-250 (`ejecucion.log`)
- **Mensajes:**
  - `[SKIP] Diagnostic document not available for scrubbing`
  - `[SKIP] Proposal document not available for scrubbing`
- **Recuperación post-T4FIX (líneas 274, 279):**
  - `[SCRUB] Diagnostic (post-T4FIX): 1 fix(es) applied` → "COP COP" → "COP"
  - `[SCRUB] Proposal (post-gen): 2 fix(es) applied`
- **Causa raíz (VERIFICADA en código):** En `main.py:2372` (FASE 3.6) el scrubber corre, pero `diagnostic_path`/`proposal_path` no existen aún (los documentos se generan después). El scrubber en `main.py:2422/2441` imprime `[SKIP]`. Posteriormente:
  - `main.py:2551` — post-T4FIX scrub: SÍ scrubbea (L2579-2585).
  - `main.py:2719` — post-gen proposal scrub: SÍ scrubbea (L2728-2732).
  - El resultado final es correcto, pero FASE 3.6 es dead code efectivo.
- **Impacto funcional:** BAJO — los fixes se aplican eventualmente. Pero el warning `[SKIP]` genera ruido y FASE 3.6 como gate es inefectiva.
- **Skill ref:** `iah-cli-phantom-gate-debug` — patrón "Content Scrubber Never Runs"
- **No resolvible con onboarding** — es orden de ejecución del pipeline.

### Alcance del fix

- **Archivos:** 1 — `main.py`
- **Opción A (mínima):** eliminar el bloque FASE 3.6 (L2372-2473) y dejar solo los scrubs post-T4FIX y post-gen que ya funcionan.
- **Opción B (correcta):** mover el scrub de FASE 3.6 a después de la generación de documentos, unificándolo con los scrubs post-T4FIX/post-gen para evitar duplicación. Requiere cuidar el quality gate (L2444) que depende del `diag_text`/`prop_text` producidos en el bloque.
- **Complejidad:** Media — requiere cuidar el orden del quality gate (no romper el flujo post-T4FIX).

### Pruebas

- `tests/postprocessors/test_content_scrubber.py` existe.
- Test: ejecutar v4complete end-to-end → no debe aparecer `[SKIP]` en log.
- Test: quality gate debe correr sobre texto scrubbeado, no vacío.
- Verificar que los scrubs post-T4FIX y post-gen siguen funcionando.

### Prioridad: P3 (Baja)

Higiene de código, no afecta output.

### Viabilidad: ALTA — entra en la planificación.

---

## BUG-6: OG no detectado — sitio es SPA (JavaScript app shell)

- **Línea log (implícita):** `OG not detected for http://www.luxorhotel.com.co/`
- **Snippet HTML (verificado en log):** `<!doctype html><html lang=en translate=no>...<script type="text/javascript">` — es un SPA, no HTML estático.
- **Causa raíz (VERIFICADA en código):** El fetcher HTTP obtiene el app shell vacío. `modules/auditors/seo_elements_detector.py:41-87` — `detect(html, url)` parsea con BeautifulSoup. Funciona correctamente con HTML real, pero recibe HTML vacío del app shell. `modules/auditors/v4_comprehensive.py:505` — `_run_seo_elements_audit(page_html)` recibe `page_html` del fetch HTTP inicial (app shell, no renderizado). Los OG tags se renderizan client-side vía JavaScript.
- **Dependencias:** Playwright SÍ está instalado (`venv/Lib/site-packages/playwright`, v==1.58.0). Selenium también (v==4.38.0). NO se usan para renderizar SPAs antes del SEO audit.
- **Impacto:**
  - `seo_elements.open_graph: False` (falso negativo)
  - AEO score incorrecto: 25 pts del componente Open Graph se pierden
  - Brecha "Sin OG Tags" puede no ser real
  - Diagnóstico sobrestima la gravedad del problema
- **No resolvible con onboarding** — es tecnología del sitio web del hotel.

### Alcance del fix

- **Archivos:** 1-2 — `modules/auditors/v4_comprehensive.py` o `modules/auditors/seo_elements_detector.py` + posiblemente `modules/utils/http_client.py`
- **Cambio:** Detectar SPA (HTML con `<script>` pero sin og tags Y pocos meta tags) y renderizar con Playwright como fallback antes de parsear.
- **Pre-requisito:** confirmar que `playwright install chromium` ya está hecho o documentarlo.
- **Caveats:** manejar timeouts, fallback graceful si Playwright falla (no crashear, retornar BeautifulSoup result sobre HTML estático).
- **Complejidad:** Media-Alta — añade dependencia de runtime, manejar timeouts, fallback.

### Pruebas

- `tests/auditors/test_seo_elements_detector.py` existe.
- Test: `detect()` con HTML de SPA vacío + Playwright mock → debe encontrar og tags del HTML renderizado.
- Test: si Playwright no disponible, fallback a BeautifulSoup (no crashear).
- Verificar: `playwright install chromium` en CI/entorno.

### Prioridad: P2 (Media)

Afecta precisión del AEO score y diagnóstico.

### Viabilidad: ALTA (con caveats) — entra en la planificación.

---

## Resumen de viabilidad

| Bug   | Categoría         | ¿Fix viable? | Complejidad | Prioridad | ¿En plan? |
|-------|--------------------|-------------|-------------|-----------|-----------|
| BUG-1 | Datos / API        | Sí          | Baja        | P1 Alta   | SÍ        |
| BUG-2 | Código Python      | Sí          | Muy baja    | P3 Baja   | SÍ        |
| BUG-4 | Infra + Código     | Parcial     | Baja cód / N/A cfg | P2 Media | PARCIAL (openrouter sí, gemini no) |
| BUG-5 | Orden pipeline     | Sí          | Media       | P3 Baja   | SÍ        |
| BUG-6 | Fetcher / SPA      | Sí          | Media-Alta  | P2 Media  | SÍ        |

---

## Bugs que quedan fuera de la planificación

### BUG-4 (parte gemini 403) — Configuración de credenciales

- **Acción del usuario:** crear `GEMINI_API_KEY` en Google AI Studio (https://aistudio.google.com/apikey) y añadirla a `.env`.
- No es fix de código, es setup de infraestructura. El código ya lee `GEMINI_API_KEY` correctamente (`llm_mention_checker.py:100`).

### BUG-4 (parte openrouter 404) — Requiere verificación externa antes de planificar

- Antes de planificar el fix, hay que confirmar qué modelo vigente reemplaza a `google/gemini-2.0-flash-001` en OpenRouter. Eso es una consulta al catálogo de OpenRouter (https://openrouter.ai/models), no al código.
- El fix de código (externalizar modelo al registry) sí es planificable.

---

## Pruebas necesarias para los bugs fuera de planificación

### BUG-4 gemini (config, fuera de plan)

- Prueba manual post-config: ejecutar `python main.py v4complete --url http://www.luxorhotel.com.co/` y verificar que el log NO muestre `LLM query failed for gemini: 403`.
- Prueba de la key: curl directo a la API de Gemini con la nueva key.
- No hay test automatizable (requiere key real).

### BUG-4 openrouter (modelo vigente)

- Prueba manual: curl al endpoint de OpenRouter con el modelo candidato para confirmar que existe antes de actualizar el código/registry.
- Test automatizable post-fix: mock del payload verificando que usa el modelo del registry (no hardcoded).

---

## Orden de ejecución sugerido para la planificación

### Fase 1 — Quick wins (bajo riesgo)

- **BUG-2:** 1 línea en `main.py`. Cero riesgo de regresión.
- **BUG-1:** 2 líneas en `v4_comprehensive.py`. Test de regresión simple.

### Fase 2 — Resiliencia LLM

- **BUG-4 openrouter:** externalizar modelo al `provider_registry.yaml`. Requiere verificar catálogo OpenRouter antes. Bajo riesgo de código, medio de integración.

### Fase 3 — Higiene de pipeline

- **BUG-5:** eliminar/reordenar FASE 3.6. Requiere cuidar el quality gate.
- Test E2E para confirmar que los scrubs post-T4FIX/post-gen siguen OK.

### Fase 4 — SPA rendering (mayor complejidad)

- **BUG-6:** integrar Playwright como fallback. Requiere instalar browser, manejar timeouts, fallback graceful.
- Mayor riesgo de regresión (añade dependencia de runtime).

La ejecución por fases permite entregar valor incremental: BUG-1 y BUG-2 se resuelven en minutos, BUG-4 openrouter en una sesión corta, BUG-5 y BUG-6 requieren sesiones dedicadas con pruebas E2E.

---

## Datos de la ejecución (evidencia)

- Log completo: `evidence/luxor-v4complete/ejecucion.log`
- Audit report: `output/v4_complete/luxorhotel/v4_audit/audit_report_20260706_110424.json`
- Financial scenarios: `output/v4_complete/luxorhotel/v4_audit/financial_scenarios_20260706_110425.json`
- Diagnostic: `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260706_110427.md`
- Proposal: `output/v4_complete/02_PROPUESTA_COMERCIAL_20260706_110433.md`
- Delivery ZIP: `output/v4_complete/deliveries/luxorhotel_20260706.zip`
- Pain ledger: `output/v4_complete/luxorhotel/v4_audit/pain_ledger.json`

---

## Evidencia de validación contra código vivo

| Bug   | Archivo verificado | Línea(s) | Confirmación |
|-------|-------------------|----------|--------------|
| BUG-1 | `modules/auditors/v4_comprehensive.py` | 1159-1160, 799-800 | `lat=0.0` hardcoded; `gbp_result.lat` disponible |
| BUG-2 | `main.py` | 1927-1944 | `calc_result` no existe en scope; `financial_breakdown` sí sobrevive |
| BUG-4 | `modules/auditors/llm_mention_checker.py` | 239, 100 | modelo hardcoded; `GEMINI_API_KEY` ausente en `.env` |
| BUG-5 | `main.py` | 2372-2473, 2551, 2719 | FASE 3.6 SKIP; post-T4FIX y post-gen sí scrubbean |
| BUG-6 | `modules/auditors/seo_elements_detector.py` | 41-87 | `detect()` correcto pero recibe HTML vacío del app shell |
