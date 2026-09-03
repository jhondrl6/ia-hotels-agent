# CONTEXT-GAP-URL-NO-PROPIA-SONDA-2026-08-29

> **Tipo**: Contexto de decisión con evidencia medida (insumo para sesión de orquestación → plan).
> **Disparador comercial**: exclusión de #1 Condina (in situ 29-08) y reemplazo por Finca Hotel Don Julio, sin web propia → pregunta "¿puede v4complete correr sobre URL de OTA/Instagram?".
> **Veredicto de la evaluación preliminar**: NO viable — el pipeline no rechaza entradas no-propias y produce auditorías inválidas de forma silenciosa.
> **Verificación (2026-08-31)**: validado exhaustivamente contra código vivo (v4.73.0, HEAD). GA-1 y GA-2 **CONFIRMADOS** línea por línea (§2b). Corregidas 2 imprecisiones factuales (superficie de colisión en §1; ruta del test en §7.1). Amplificado con 10 hallazgos nuevos (§2c), síntesis de causas raíz (§2d) y refuerzos del plan (§5-§7). Sigue sin implementarse.
> **Uso previsto**: esta sesión NO implementa. Una nueva sesión con `phased_project_executor` v2.17.0 formula el micro-plan (1 fase) a partir de los §5-§7.

---

## 1. Resumen ejecutivo — dos gaps comprobados empíricamente

| # | Gap | Ubicación | Consecuencia probada |
|---|-----|-----------|----------------------|
| **GA-1** | Colapso de identidad: `_normalize_url()` reduce TODO a `netloc`; en URLs de OTA el path ES la identidad del hotel | `main.py:3604-3615` (docstring confirma: "Ignora: protocolo, www, trailing slash, **path**, query string") | `booking.com/hotel/co/finca-don-julio.es.html` → canónica `"booking.com"`. Dos hoteles distintos de Booking comparten `target_id`; `memory.find_latest_analysis(canonical_url)` (`main.py:1704`) puede devolver **el análisis de otro hotel**. Ventana 20 días = `cleanup_old_sessions(days=20)` (`main.py:1634`); el escaneo por substring de `output/` en `find_latest_analysis` (`memory.py:364-380`) **no tiene límite de antigüedad**. Superficies reales de colisión (corregido 31-08 — no existe ningún writer de `hotels/` en el código): `output/clientes/{slug}_onboarding.yaml` (slug del nombre → `booking_onboarding.yaml` compartido), `output/v4_complete/{hotel_id}/v4_audit/` (`hotel_id` derivado del nombre, `main.py:1674`) y el `target_id` de memoria |
| **GA-2** | El scraper no distingue "sitio del hotel" de "página de tercero" y emite datos con confianza arbitraria | `modules/scrapers/web_scraper.py:39-147` (`extract_hotel_data`); detección de OTA/agregador = **0 coincidencias en todo el repo** (grep exhaustivo `booking|agoda|trivago|expedia|es un OTA|agregador` solo devuelve playbooks/comisiones/tests) | Sonda real 29-08: página de Instagram → `confidence: "alta"`, `cms: "shopify"` (FALSO), nombre = título de la pestaña de IG. Página de Booking → 7 brechas que describen **la página de Booking**, `schema_data: 0`, visibilidad IA 0. Ninguno aborta: el basura-entrada se propaga como dato válido hacia audit → pain_ledger → docs → gates → hook PDF |

**Riesgo de producto**: entregar un diagnóstico `READY_FOR_PUBLICATION` que audita la presencia digital de Meta/Booking, no del hotel. Es la violación exacta del contrato de credibilidad numérica (plan CREDIBILIDAD-NUMÉRICA + SR-PIPELINE-FIXES, v4.73.0).

**Contexto SR-D**: la canonicalización (FASE-SR-D, `2026-08-28`) canonicó el invariante implícito "URL ≡ sitio propio del hotel". El guard propuesto hace ese invariante **explícito y bloqueante**.

## 2. Evidencia cruda de las sondas (ejecutadas 2026-08-29)

### Sonda 1 — canonicalización + sondas de origen (`temp/probe_donjulio_viability.py`)
```json
{
 "booking":   { "original": "https://www.booking.com/hotel/co/finca-don-julio.es.html", "canonical": "booking.com" },
 "instagram": { "original": "https://www.instagram.com/fincahoteldonjulio",              "canonical": "instagram.com" },
 "sondas": {
  "https://www.booking.com/robots.txt":  { "status": 200, "len": 33384 },
  "https://www.booking.com/llms.txt":    { "status": 404 },
  "https://www.instagram.com/robots.txt":{ "status": 200, "len": 6256 }
 }
}
```
Nota: robots.txt/llms.txt 200/404 son **las políticas de Booking/Meta**. Con el anclaje al origen introducido en SR-F (D-PF6), el auditor de crawlers atribuiría la política de Booking al hotel.

### Sonda 2 — scrapeo real con URL original completa (`temp/probe2_donjulio.py`)
```json
{
 "booking": {
  "region": "eje_cafetero", "hotel_name": "Booking",
  "scrape": { "error": null, "metodo": "web_scraping_avanzado", "confidence": "baja",
              "n_brechas": 7, "precio_promedio": null, "whatsapp": null, "n_schema": 0,
              "cms_detected": {"cms": "unknown"}, "score_visibilidad_ia": 0 }
 },
 "instagram": {
  "region": "eje_cafetero", "hotel_name": "Instagram",
  "scrape": { "error": null, "metodo": "web_scraping_avanzado", "confidence": "alta",
              "n_brechas": 6, "precio_promedio": null, "whatsapp": null, "n_schema": 0,
              "cms_detected": {"cms": "shopify", "signals": ["Shopify resources"]},
              "nombre_extraido": "Finca Hotel Don Julio (@fincahoteldonjulio) • Fotos y vídeos de Instagram",
              "score_visibilidad_ia": 4 }
 }
}
```
Puntos de observación: (a) "éxito" sin error en ambos; (b) `hotel_name` = nombre de la plataforma; (c) Instagram produce **falsa confianza alta + falso CMS**; (d) `region` sale "eje_cafetero" por defecto/datos del path, no por el hotel.

### Reproducibilidad
Scripts: `temp/probe_donjulio_viability.py` y `temp/probe2_donjulio.py` (referencia a `os.getcwd()` en `sys.path`, salida UTF-8 por cp1252 de consola). Si `temp/` se limpia: el Apéndice A conserva el código. Salidas completas: `temp/probe_donjulio_result.json`, `temp/probe2_result.json`.

## 2b. Verificación contra código vivo (2026-08-31, v4.73.0 HEAD)

| Claim del doc | Veredicto | Evidencia |
|---|---|---|
| `_normalize_url` reduce a netloc (path/query descartados) | CONFIRMADO | `main.py:3604-3615`; probe `temp/probe_donjulio_result.json` |
| Búsqueda de análisis previo por URL canónica | CONFIRMADO | `main.py:1654` (canonical_url), `main.py:1704` (find_latest_analysis), `agent_harness/memory.py:334-382` |
| Scraper sin distinguir sitio propio de tercero | CONFIRMADO | `modules/scrapers/web_scraper.py:39-147`; grep exhaustivo: 0 detección de OTA en código activo (solo archives/, tests, texto comercial y modelo `ota_presence`) |
| `confidence: "alta"` en IG | CONFIRMADO + mecanismo | `_calculate_confidence` (`web_scraper.py:1173-1192`) puntúa JSON-LD/og:title/`@`/`$` — mide estructura de página, no identidad de fuente |
| `cms: "shopify"` falso en IG | CONFIRMADO + mecanismo | `_detectar_cms` (`web_scraper.py:845`): `if 'shopify' in html_lower` — substring sobre todo el HTML |
| nombre = título de la pestaña IG | CONFIRMADO | `_extract_name` (`web_scraper.py:959-982`) vía og:title/title; coincide verbatim con `temp/probe2_result.json` |
| `hotel_name` = "Booking"/"Instagram" | CONFIRMADO | `_extract_hotel_name_from_url` (`main.py:3725-3729`) toma primera etiqueta del netloc |
| `region` = eje_cafetero espurio | CONFIRMADO + mecanismo | `_detect_region_from_url` (`main.py:3568-3570`) contiene keyword `'finca'` — matchea el path del OTA |
| Sondas ancladas al origen (nota Sonda 1) | CONFIRMADO en código | `ai_crawler_auditor.py:89-97` (FASE-SR-F H5): robots.txt se pide al origen → con URL OTA se atribuye la política de Booking al hotel |
| Evidencia bajo `hotels/booking_com/` | IMPRECISO | No existe writer de `hotels/` en el código → corregido en §1 (superficies reales) |
| §4 estado comercial (Condina/Don Julio/Segorbe) | CONFIRMADO | `evidence/Ingresos/05_Pipeline_PostSismo.md` líneas 17, 19, 42, 56 |
| §8 referencias | EXISTEN | `/.opencode/plans/Archives/SR-PIPELINE-FIXES-2026-08-27/`, `VERSION.yaml` 4.73.0, sondas en `temp/` |

## 2c. Hallazgos nuevos de la verificación (amplificación)

| # | Hallazgo | Evidencia | Severidad |
|---|---|---|---|
| N1 | **Contaminación cruzada de datos operativos**: `_load_latest_onboarding_data()` matchea por `_normalize_url` (netloc) → el YAML de onboarding del hotel A de Booking alimenta los escenarios financieros del hotel B (habitaciones, ADR, % canal directo) | `main.py:3674-3690` | Alta |
| N2 | **ADR de OTA entra al motor financiero**: el fallback de ADR scrapea `args.url` y pasa `web_scraping_adr` a `resolve_adr_with_shadow()`. La página de Booking tiene precios reales y plausibles → el fallo es silencioso, no ruidoso | `main.py:1954-1972` | Alta |
| N3 | **`last_url` persistente propaga URLs envenenadas**: se guarda tras cada run (`main.py:1411`) y `ensure_url()` (`main.py:216-225`) la reinyecta silenciosamente en comandos posteriores sin `--url` | `main.py:216-225, 1411` | Alta |
| N4 | **Coste API en nombre basura**: la auditoría llama Places API con queries construidas desde `hotel_name` ("Instagram", "Booking") | `modules/auditors/v4_comprehensive.py:433-482, 800-829` | Media |
| N5 | **Bug numérico en `generar_reporte_ejecutivo()`**: `'m' in impacto_str` es True por "COP/mes" → los impactos en K se suman como M (×1000); `.replace('.', '')` convierte "2.1" → "21" (×10). Latente: sin llamadores hoy, pero es API pública del scraper | `web_scraper.py:893-899` | Media (latente) |
| N6 | **Identidad duplicada entre módulos**: `OnboardingController.generate_hotel_id()` reimplementa el colapso a netloc (copia no importable por dependencia inversa con main) → cualquier fix debe cubrir ambas copias o ser ortogonal a ellas | `modules/orchestration_v4/onboarding_controller.py:339-351` | Media |
| N7 | **Higiene main.py**: `def _audit_handler` aparece **5 veces** (definiciones duplicadas que se pisan); tres esquemas de identidad conviven (netloc canónico, slug del nombre, URL completa como `hotel_id` en handlers financieros) | `main.py:228-239+`, `main.py:1877, 1968` | Baja-Media |
| N8 | **hook-pdf no tiene superficie para un guard por `--url`**: no recibe URL; consume por glob el último `01_DIAGNOSTICO_*.md`/`v4_complete_report.json` del directorio (`sorted(...)[-1]`). El guard ahí solo puede validar `report_json["url"]` | `modules/commercial_documents/hook_pdf_generator.py:179-213` | Media |
| N9 | **Suite de regresión congela la semántica netloc-only**: `tests/test_target_id_canonicalization.py` (28 tests, verdes 31-08) fija p. ej. `"…/habitaciones" → hotelsalentoreal.com` e inspecciona el source de main.py y del controller. El fix debe ser ORTOGONAL (guard de entrada, no cambio del normalizador) o romperá 28 tests. Esta suite no estaba listada en los ACs del doc | `tests/test_target_id_canonicalization.py` | Alta (para el plan) |
| N10 | **`config/pricing.yaml` internamente inconsistente**: `floor_price: 1.200.000` > `boutique.min_price: 800.000` (el piso viola el mínimo de su propio tier); el rango boutique 800K–2.5M contradice la escalera canónica $1,5M–3,5M | `config/pricing.yaml:8, 33` | Residuo (§7.1/§7.2) |

## 2d. Síntesis de causas raíz

- **RC1 (primaria)**: el invariante "URL de entrada ≡ sitio web propio del hotel" es *implícito* — ningún componente lo valida. Todo el pipeline confía en él sin enforcement. GA-2, N1-N4 y N8 son consecuencias directas.
- **RC2**: la identidad se deriva del netloc (path descartado) — correcto para sitios propios, inválido para terceros donde el path ES la identidad. De aquí nacen GA-1, N1 y N6.
- **RC3**: el modelo de confianza del scraper mide *calidad de extracción*, no *identidad de la fuente* — por eso Instagram produce "alta". El guard mitiga la superficie conocida pero deja RC3 viva para terceros no blocklisted.
- **RC4**: ausencia de validación en el límite de entrada del dominio: basura entra y ninguna etapa (audit → pain → financiero → docs → gates → hook PDF) la detiene.

## 3. Por qué es inviable también en el plano comercial (kit Ingresos)

1. **Escalera rota**: los assets prometidos (Schema Hotel, llms.txt, robots fix, FAQ, botón WhatsApp) se materializan/depiegan sobre **sitio propio** (`modules/asset_generation/*`, `deploy` FTP/WP-API). Sin web no hay Implementación ($1,5M–3,5M) ni Seguimiento ($400K/mes recurrente).
2. **Precedentes en el propio funnel**: #3 Segorbe (SIN WEB 27-08 → "inviable v4complete/PDF gancho") y ahora #1 Don Julio (sin web detectada en Booking/Agoda/Trivago/Google Hotels/Instagram/gremios; `donjulio.com.co` es otro negocio). La regla del kit quedó **validada por código**: sin web propia no hay producto.
3. **No es un gap del kit** — el kit opera bien; es un gap de defensa del repositorio que impide el workaround tentador ("correrlo sobre la URL de Booking").

## 4. Estado comercial asociado (para no perder el hilo al retomar)

- `evidence/Ingresos/05_Pipeline_PostSismo.md`: #1 Condina CERRADO in situ (NO OPERATIVO, re-evaluar 2026-11-29); slot #1 = Don Julio OPERANDO* con próxima acción "confirmar con pregunta directa si tiene web propia + teléfono". LOG 29-08 registrado.
- Si Don Julio confirma que NO tiene web → pasa a caso igual que Segorbe: **definir reemplazo con web propia** (vivero: lista v1 — Mahalo, Natura Cocora, Mirador del Cocora, Vista Hermosa en Salento; regla §6.5 aplica).
- Regla de prudencia intacta: ≥5 OPERANDO se mantiene (7 con teléfono verificado + Don Julio por verificar).

## 5. Opciones para el plan (evaluación de decisión)

| Opción | Descripción | Pros | Contras |
|--------|-------------|------|---------|
| **A — Guard de entrada (RECOMENDADA)** | Rechazo temprano y fuerte en `v4complete`/`onboard`/`execute`/`hook-pdf`: si el `netloc` canónico está en blocklist de plataformas (booking.com, agoda.com, expedia.com, hotels.com, tripadvisor.com, instagram.com, facebook.com, google.*, airbnb.com, despegar.com, Kayak/momondo/… como lista versionada en `config/`), **abortar con mensaje claro** ("necesito la URL del sitio web propio del hotel; esta URL es de un agregador/red social") antes de scrapeo/coste API | 1 fase, complejidad Baja-Media; "fallar duro antes que disciplina manual" (preferencia del usuario); superficie mínima; no toca gates ni financiera; testable con fixtures sin red | Blocklist requiere mantenimiento; un hotel con subdominio propio en plataforma (raro) sería falsamente rechazado — mitigar con `--force` explícito documentado |
| B — Marcaje de "tercero" en scraper | `extract_hotel_data` detecta agregador y etiqueta los datos como no-propios, degradando el run | Más "suave" | Propaga basura marcada; exige changes en gates/docs para respetar la marca; complejidad mayor; tentación de vender igual el diagnóstico |
| C — Modo "sin web" (GBP-only + onboarding) | Producto nuevo: runner que auditiona GBP + datos del hotel sin sitio | Habría que construirlo (el `tier_c_onboarding_required` gate pide onboarding, no sustituye el sitio) | Fuera de alcance del fix; **merece su propio contexto de decisión comercial** (¿existe oferta para hoteles sin web?) |

**Recomendación**: Opción A sola. C queda como pregunta de negocio separada (no mezclar con el guard).

**Refuerzos de la Opción A (post-verificación 31-08)**:
1. **Un solo choke point de enforcement**, no guards por comando: validar en `ensure_url()` (`main.py:216-225`) + al arranque de los modos que no pasan por ella (`execute`, `onboard`, `deploy`), **antes** de cualquier llamada de red/API. Cubre de una vez v4complete, v4audit, audit (legacy), validate-guarantee, onboard, execute y deploy.
2. `hook-pdf` no recibe `--url` (N8): su guard valida `report_json["url"]` en `extract_data()`.
3. Blocklist versionada (`config/url_blocklist.yaml`) con matching de subdominios y dominios regionales (`*.booking.com`, `booking.com.*`, `google.*`), clasificando OTA / red social / buscador. **Semillas ya existentes en el repo**: lista `otas` de `web_scraper.py:523` y opciones OTA de `two_phase_flow.py:716-722` — centralizarlas en el config.
4. **Sanear `last_url`** (N3, ~2 líneas, misma RC1): no persistir URLs bloqueadas y avisar al reinyectar una URL persistente blocklistada.
5. **No cambiar la semántica de `_normalize_url` ni `generate_hotel_id`** (N9): el guard es ortogonal; mantiene verdes los 28 tests de `tests/test_target_id_canonicalization.py` y evita tocar las dos copias de la normalización (N6).
6. Opcional (decidir en orquestación): defensa en capa de datos — `assert_own_site()` al inicio de `WebScraper.extract_hotel_data()` y `V4ComprehensiveAuditor.audit()` para proteger llamadores de librería (sondas, futuros módulos).
7. Falsos positivos del scraper (confidence/CMS, RC3): **sin fix en este plan** — el guard bloquea la superficie conocida; RC3 queda registrada en §7 como watchlist.

## 6. Insumos de alcance para la sesión de orquestación

- **Nombre sugerido de plan**: `VALIDADOR-URL-PROPIA-2026-08-XX` (micro-plan, **1 fase de implementación** + cierre documental; VERIFY puede fundirse con la fase dada la escala, decidirlo en orquestación).
- **Archivos candidatos** (verificados 31-08): `main.py` — `ensure_url()` L216-225 (choke point + reinyección de `last_url`), L1411 (`save_state last_url`), `run_v4_complete_mode` L1654 (canonicalización existente, NO tocar semántica); modos sin `ensure_url`: `run_execution_mode` (scrapeo L597/L818), `run_onboard_mode` L1046+, `run_deploy_mode` L967; `modules/commercial_documents/hook_pdf_generator.py` `extract_data()` L179-213 (validar `report_json["url"]`); `config/` (blocklist nueva — hoy no existe ningún archivo análogo); tests nuevos (`tests/` — p. ej. `test_url_propia_guard.py`).
- **ACs de borrador** (ajustados 31-08):
  - AC1: `v4complete --url <booking/hotel/...>` → exit ≠ 0, mensaje claro en español, **sin scrapeo previo ni llamadas API de costo** (el auditor gasta Places API con queries tipo "Instagram"/"Booking" — N4).
  - AC2: `instagram.com/...`, `facebook.com/...`, `google.com/...` → mismo comportamiento.
  - AC3: URL de sitio propio (fixture `hotelsalentoreal.com`) → comportamiento inalterado (no regresión; corrida E2E NO requerida — usar tests unitarios + `find_latest_analysis` spy). **Regresión obligatoria explícita**: `tests/test_target_id_canonicalization.py` (28 tests, verdes 31-08) debe seguir verde — el fix es ortogonal al normalizador (N9).
  - AC4: `--force` documentado (bypass explícito con warning persistido en trace).
  - AC5: guard activo en **todos** los comandos con URL: `onboard`, `execute`, `v4audit`, `audit` (legacy), `validate-guarantee`, `deploy` (mismos mensajes); contrato anti-regresión tipo guardián AST si aplica (patrón SR-A).
  - AC6 (nuevo, N3): `last_url` blocklistada no se persiste; si `ensure_url()` reinyecta una URL persistente bloqueada → mismo rechazo, con mención explícita de que proviene del estado persistente.
  - AC7 (nuevo, N8): `hook-pdf` rechaza cuando `v4_complete_report.json.url` es de plataforma bloqueada (sin necesidad de `--url`).
- **Requisitos del workflow**: executor v2.17.0 (R1 una fase/sesión, R2 ≤60 iteraciones, R3 presupuesto de tareas), prompt de sesión propio, checklist, `10-analisis` desde concepción, TDD (contratos ANTES del fix — precedente SR-H2), `log_phase_completion.py` SIN `--release`, suites pytest **aisladas con salida a archivo** (memoria: `test_proposal_generator.py` ~8GB), pre-commit hooks.
- **Lecciones capitalizables a vincular**: SR-D (canonicalización/UTM), SR-F D-PF6 (anclaje de sondas al origen — aquí el origen es el equivocado cuando la URL no es propia), L-PF (vacío≠ausente), "un log de rechazo no es la causa".

## 7. Residuos conocidos relacionados (para registrar en el 10-analisis, no para este plan)

1. `tests/config/test_config_pricing.py::TestPricingYAMLValues::test_tiers_boutique_min_price` — **falla en HEAD, verificado ejecutándolo 31-08**: el test espera 1.200.000 (`test_config_pricing.py:30`), `config/pricing.yaml:8` tiene 800.000. Ampliado con N10: el propio yaml es inconsistente — `floor_price: 1.200.000` (línea 33) supera el `min_price` de su tier boutique, y 800K–2.5M contradice la escalera canónica $1,5M–3,5M (`CONTEXTO MAESTRO v3.0`). Decidir: ¿se corrige el test, el yaml, o ambos contra la escalera canónica?
2. `monthly_default` plano (hook) vs derivado del calculador (propuesta) — fix durable pendiente. **Estructura confirmada 31-08**: `config/pricing.yaml:31` = 400K; fallbacks hardcoded 1.2M en `hook_pdf_generator.py:159`, `v4_proposal_generator.py:501` y `pricing_calculator.py:156` (tres fuentes, dos valores). El LOG 27-08 del pipeline ya registró la dualidad ($1,2M hook vs $400K floor propuesta).
3. GOOGLE_PAGESPEED_API_KEY inválida/sin habilitar — rotación = decisión del usuario (OPS, registrado en FASE-SR-F). No verificable sin consumo de API.
4. En el run de `hook-pdf` de 28-08 persisten WARN `aeo_score/iao_score` vacíos en la validación del hook (advisory, no bloqueante) — vigilar.
5. (nuevo 31-08, N5) `WebScraper.generar_reporte_ejecutivo()` (`web_scraper.py:893-899`): los impactos K se suman como M porque `'m' in impacto_str` matchea "COP/mes" (×1000), y `.replace('.', '')` convierte "2.1" en "21" (×10). Latente — sin llamadores hoy. Fix aparte del guard, pero de la misma familia de credibilidad numérica.
6. (nuevo 31-08, RC3) El `confidence`/`cms` del scraper mide estructura de página, no identidad de fuente: el guard no lo arregla para terceros no blocklisted (subdominios Wix, marketplaces nuevos). Watchlist con la blocklist versionada.
7. (nuevo 31-08, N7) Higiene `main.py`: `def _audit_handler` definido 5 veces (definiciones duplicadas que se pisan); conviven tres esquemas de identidad (netloc canónico, slug del nombre, URL completa como `hotel_id` en `main.py:1877, 1968`). Candidato a limpieza en un plan de refactor, no en este.

## 8. Referencias

- Plan madre de los fixes previos: `/.opencode/plans/Archives/SR-PIPELINE-FIXES-2026-08-27/` (README 11 fases ✅, v4.73.0, VERIFY 13/13).
- Precedente de contexto→plan: `.opencode/context/Historico/CONTEXT-SALENTOREAL-V4COMPLETE-EJECUCION-2026-08-27.md` (si archive movió la ruta, localizar por nombre).
- Pipeline comercial: `evidence/Ingresos/05_Pipeline_PostSismo.md` (LOG 2026-08-28/29) + `01_Lista_Prospectos_v2_post_sismo.md` (tabla top 10, recuento).
- E2E de referencia con sitio propio: `output/salentoreal_final_v4c_h2/` + `evidence/FASE-SR-H2/smoke_result_h2.json` (smoke 7/7).

## Apéndice A — Sondas (reproductoras)

Guardar como `temp/probe_donjulio_viability.py` y `temp/probe2_donjulio.py` y ejecutar desde la raíz del repo. Esenciales:

```python
# Sonda 1 (canonicalización): importa de main
from main import _normalize_url, _detect_region_from_url, _extract_hotel_name_from_url
# _normalize_url("https://www.booking.com/hotel/co/finca-don-julio.es.html") → "booking.com"

# Sonda 2 (scrapeo real):
from modules.scrapers.web_scraper import WebScraper
d = WebScraper().extract_hotel_data("https://www.instagram.com/fincahoteldonjulio")
# d["confidence"] == "alta"; d["cms_detected"]["cms"] == "shopify"  ← falsos positivos
```
Requisitos: `sys.path.insert(0, os.getcwd())`; envolver stdout con UTF-8 (consola cp1252); 1 sola petición por URL (timeout 15 s).
