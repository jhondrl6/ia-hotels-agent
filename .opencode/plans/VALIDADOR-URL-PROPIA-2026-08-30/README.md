# VALIDADOR-URL-PROPIA-2026-08-30

> **Versión objetivo**: 4.74.0 | **Estado**: FASE-A ✅ → FASE-B ✅ → FASE-C ✅ 2026-08-31 (11/11 probes PASS, regresión 101 passed) — siguiente: FASE-D
> **Workflow**: `phased_project_executor.md` v2.17.0 (R1: una fase/sesión, R2: ≤60 iteraciones, R3: scope por fase)
> **Contexto fuente**: `.opencode/context/CONTEXT-GAP-URL-NO-PROPIA-SONDA-2026-08-29.md` (verificado contra código vivo v4.73.0)
> **Auditoría de estrategia (2026-08-30)**: re-verificado contra código vivo HEAD (todos los claims de líneas/funciones confirmados; 28/28 canonicalización y 13 rojos baseline reproducidos). Corregidos 6 fallos de causa raíz: F1 `--force` YA existe en argparse (reutilizar, no re-crear); F2 ensure_url SÍ cubre execute/onboard/deploy → eliminados los guards redundantes por modo; F3 probe P5 requiere sembrar el estado (la URL bloqueada nunca se persiste sola); F4 mecanismo concreto para el warning de `--force` (`.agent/memory/url_guard_force_events.json`); F5 el baseline H2 corrió CON DEFAULTS → FASE-D NO puebla clientes; F6 contrato anti-falsos-positivos de matching ( dominios parecidos). Detalle en §Auditoría.

## Problema (2 gaps empíricos, Opción A recomendada)

| # | Gap | Consecuencia probada |
|---|-----|----------------------|
| GA-1 | `_normalize_url()` reduce todo a netloc; en URLs de OTA el path ES la identidad | `booking.com/hotel/co/finca-don-julio` → target_id `booking.com` → colisión de identidad entre hoteles, análisis cruzados vía memoria |
| GA-2 | El scraper no distingue sitio propio de página de tercero | Sonda real: Instagram → `confidence: alta` + `cms: shopify` FALSOS; la basura entra silenciosa hasta gates y hook PDF |

**Fix**: guard de entrada blocklistado (abort fuerte antes de red/API) + `--force` explícito + saneamiento de `last_url` + guard en hook-pdf + defensa opcional en capa de datos. **Ortogonal** al normalizador (28 tests congelan la semántica netloc-only).

## Fases (7 sesiones: 4 implementación + VERIFY + RELEASE)

| Fase | Sesión | Objetivo | Complejidad | Modo de ejecución | Comando largo |
|------|--------|----------|-------------|-------------------|---------------|
| FASE-A | 1 | Núcleo del guard: contratos TDD + `config/url_blocklist.yaml` + `own_site_guard` + choke point `ensure_url()` + `--force` | Media | **DIRECTO** (decisión arquitectónica, no delegable) | No |
| FASE-B | 2 | ✅ **Completada 2026-08-31**. Superficies secundarias: saneamiento `last_url` (AC6), hook-pdf (AC7), defensa capa datos (`assert_own_site` en scraper/auditor). **Nota auditoría F2**: `ensure_url()` se llama para TODOS los comandos en `main()`; el tuple de L217 solo excluye la REINYECCIÓN, no la validación → no existen "modos sin ensure_url" y NO se agregaron guards por modo (contra-condición congelada en el guardián AST). **Hallazgo de ejecución D-VUP-B1**: la defensa de capa de datos habría anulado `--force` (esas superficies no reciben `args.force`) → registro por netloc `FORZADAS_PROCESO` consultado solo por `ORIGEN_CAPA_DATOS`; FASE-C debe considerarlo en P5/P9 | Baja-Media | **DELEGADO** — subagente 1 (main.py: `last_url` + contratos ensure_url por comando) ‖ subagente 2 (hook_pdf_generator + capa datos), parent integra | No |
| FASE-C | 3 | Verificación empírica con URLs de **Finca Hotel Don Julio** (Booking/Instagram) + regresión 28 tests canonicalización | Baja | **DELEGADO** (probes CLI cortos + pytest, sin decisión) | No |
| FASE-D | 4 | E2E: **única corrida `v4complete` Hotel Salento Real** + evidencia proactiva + comparación vs baseline H2 | Baja (impl) | **MIXTO** — v4complete vía subagente (timeout 900, notify), parent verifica | Sí (1) |
| FASE-VERIFY | 5 | Certificación formal AC1-AC8 contra evidencia real, sin código | Baja-Media | **DIRECTO** (no delegable, §4.6) | No |
| FASE-RELEASE-4.74.0 | 6 | Version bump, CHANGELOG, GUIA_TECNICA, validaciones finales | Baja | **DELEGABLE** (solo YAML/MD + scripts) | No |

**FASE-VERIFY activada** (§4.6): ≥3 fases impl ✓ (A-D), E2E ✓ (FASE-D), ACs cross-fase ✓ (AC1-AC8 cruzan A→D).

## Criterios de aceptación (fuente única para todo el plan)

| AC | Descripción | Fase dueña | Verificación |
|----|-------------|-----------|--------------|
| AC1 | `v4complete --url booking.com/hotel/...` → exit ≠ 0, mensaje claro en español, sin scrapeo ni llamadas API de costo | A | FASE-C P1 |
| AC2 | Instagram/Facebook/Google → mismo comportamiento | A | FASE-C P2 |
| AC3 | URL propia (`hotelsalentoreal.com`) → comportamiento inalterado; `tests/test_target_id_canonicalization.py` (28 tests) verde | A | FASE-C P10 |
| AC4 | `--force` (flag global reutilizado, main.py:173): bypass con evento persistido en el archivo dedicado `.agent/memory/url_guard_force_events.json` | A | FASE-C P9 + VERIFY |
| AC5 | Guard activo en TODOS los comandos con URL (onboard, execute, deploy, v4audit, audit legacy, validate-guarantee); guardián AST | B | FASE-C P1-P4 + test guardián |
| AC6 | `last_url` blocklistada no se persiste; reinyección persistente bloqueada → rechazo con mención del estado persistente | B | FASE-C P5 |
| AC7 | `hook-pdf` rechaza `v4_complete_report.json.url` de plataforma bloqueada (sin `--url`) | B | FASE-C P6 |
| AC8 | v4complete tradicional sin regresión: E2E Salento Real coherence ≥ 0.8, gates y plan de assets equivalentes al baseline H2 | D | FASE-D + VERIFY |

## Complejidad técnica (detalle → `01-plan-maestro.md`)

Escala: Baja → Baja-Media → Media → Alta → MÁXIMA.
Riesgo concentrado en **FASE-A** (choke point + TDD); FASE-B/C/RELEASE delegables; FASE-D comando largo delegado; VERIFY directo.

## Delegación (delegate_task)

| Fase | Delegable | Justificación (regla del executor) |
|------|-----------|------------------------------------|
| FASE-A | NO | Decisión arquitectónica cross-module (choke point único) — subagente carece de contexto completo |
| FASE-B | SÍ | 2 tracks de ediciones localizadas que replican el patrón de FASE-A; sin decisión de diseño |
| FASE-C | SÍ | Probes CLI deterministas + pytest por lotes; sin decisión |
| FASE-D | MIXTO | Comando largo (v4complete) delegado; verificación/comparación en parent (L30 RC1-RC2) |
| FASE-VERIFY | NO | Requiere juicio y contexto completo del plan (§4.6) |
| FASE-RELEASE | SÍ | Solo YAML/MD + scripts, sin imports del proyecto |

## Medios de comprobación de efectividad

1. **Caso positivo del guard (Don Julio)**: 11 sondas P1-P11 en FASE-C (Booking/Instagram rechazadas sin costo API, reinyección `last_url`, hook-pdf, capa librería).
2. **No-regresión tradicional (Salento Real)**: 28 tests de canonicalización + corrida E2E única en FASE-D comparada contra `output/salentoreal_final_v4c_h2/` (smoke 7/7, coherence 0.88).
3. **Certificación formal**: FASE-VERIFY completa la matriz AC1-AC8 contra evidencia real.

## Reglas transversales (lecciones capitalizadas, Paso 0)

- TDD: contratos ANTES del fix (precedente SR-H2); fix ORTOGONAL a `_normalize_url`/`generate_hotel_id` (N9).
- Guardián AST para contratos transversales (SR-A), no regex.
- No crear un tercer sistema: centralizar semillas OTA existentes (`web_scraper.py:523`, `two_phase_flow.py:716-722`) en `config/url_blocklist.yaml`.
- Pytest seguro: lotes pequeños, salida a archivo (`> temp/x.txt 2>&1`), NUNCA suite `tests/commercial_documents` completa (fuga ~8GB).
- Línea base sucia: re-verificar los tests rojos preexistentes al inicio de FASE-A y NO atribuirlos al plan; residuo `test_config_pricing` fuera de alcance (§7.1 del contexto). **Verificado en FASE-A T1 (2026-08-30): 14 fallos** (3 calculator_v2 + 9 pricing_resolution_wrapper + 1 site_verification_propagation + 1 config_pricing); `test_function_default_flags` es orden-dependiente (pasa aislado). Las fases comparan contra la MISMA combinación de archivos.
- **`--force` YA EXISTE** (auditoría F1): `main.py:173` lo define global ("Sobrescribir PDF si ya existe", usado por hook-pdf). FASE-A lo REUTILIZA (prohibido `add_argument("--force")` de nuevo → argparse ArgumentError); se extiende el help a la semántica dual "bypass del guard / sobrescribir". `hook-pdf --force` omite ambos (documentado y testeado: FASE-B propaga `force` desde `generate()` hasta `extract_data()` y el guard de AC7).
- **FASE-D SIN poblar clientes** (auditoría F5): el baseline H2 corrió CON DEFAULTS (verificado en `output/salentoreal_final_v4c_h2/v4_complete/v4_complete_report.json`: "uses default/legacy values — Tier B evidence", `direct_channel_percentage: "default"`), y no existe YAML de onboarding de Salento Real en el repo (verificado 2026-08-30). La equivalencia AC8 exige correr con defaults; NO fabricar datos de onboarding. La lección L13 aplica a runs que necesiten Tier B, no a esta corrida de equivalencia.
- E2E con `--output` alternativo: grep de símbolos no definidos en ramas nuevas antes del run.
- `log_phase_completion.py` SIN `--release` en fases intermedias; bump/CHANGELOG solo en RELEASE.
- Clasificar fallos de `run_all_validations.py`: Version Sync → `sync_versions.py`; Document Integration → README; NO re-correr la suite.

## Archivo índice

| Archivo | Propósito |
|---------|-----------|
| `01-plan-maestro.md` | Fases, complejidad, tareas, presupuesto de iteraciones |
| `05-prompt-inicio-sesion-fase-A.md` … `fase-D.md` | Prompts de implementación (1 por sesión) |
| `05-prompt-inicio-sesion-fase-VERIFY.md` | Certificación formal de ACs |
| `05-prompt-inicio-sesion-fase-RELEASE.md` | Cierre documental v4.74.0 |
| `06-checklist-implementacion.md` | Estado maestro de fases |
| `09-documentacion-post-proyecto.md` | Datos acumulativos para RELEASE |
| `10-analisis-post-implementacion.md` | Lecciones, matriz de verificación, decisiones |
| `dependencias-fases.md` | Grafo de dependencias y conflictos de archivo |

## Auditoría de estrategia (2026-08-30, contra código vivo HEAD)

Claims del plan/contexto re-verificados y CONFIRMADOS: `ensure_url()` main.py:216-225 con reinyección de `last_url`; `save_state` main.py:1411; `_normalize_url` main.py:3604-3615 (netloc-only); fallback ADR N2 main.py:1954-1972; semillas OTA `web_scraper.py:523` y `two_phase_flow.py:716-722`; hook-pdf lee `report_json["url"]` (`hook_pdf_generator.py:179-213`); N1 matching por netloc en `_load_latest_onboarding_data` (main.py:3674+); 28/28 canonicalización PASSED; baseline 13 rojos exacta (3+8+1+1); parser plano sin subparsers; entrada única `main()` → `ensure_url` en L1406 ANTES de todo routing; `doctor.py --regenerate-domain-primer` existe.

| # | Fallo (causa raíz) | Evidencia viva | Corrección aplicada |
|---|--------------------|----------------|---------------------|
| F1 | El plan manda "parsear `--force`" como si no existiera; `add_argument` duplicado lanzaría `ArgumentError` al arrancar | `main.py:172`: `--force` global ya existe ("Sobrescribir PDF"), consumido en hook-pdf L1565/1575 | Reutilizar el flag; extender help; contrato TDD de semántica dual; documentar que `hook-pdf --force` también omite el guard AC7 |
| F2 | Premisa falsa: "modos sin `ensure_url` (execute/onboard/deploy)". En realidad `main()` llama `ensure_url()` para TODOS los comandos (L1406); el tuple L217 solo excluye la reinyección de `last_url`. Los guards por modo duplican el enforcement y el guardián AST fosilizaría la duplicación (anti-lección L-PF2/L-NC10) | `main.py:1401-1460`: ensure_url precede a todos los `if args.command`; grep de call sites (1 sola llamada) | Choke point único (como ya decía el contexto §5.1): guard en `ensure_url` + capa de datos (`extract_hotel_data`, `audit`) + hook-pdf. FASE-B track 1 se reduce a `last_url`; guardián AST apunta a las 4 superficies reales |
| F3 | P5 ("reinyección de last_url bloqueada") es inejecutable tal como está: el rechazo del guard ocurre en L1406, ANTES de `save_state` L1411 → la URL bloqueada nunca se persiste; el `last_url` actual es `hotelsalentoreal.com` (verificado en vivo). Sin sembrar el estado, el 2º comando sin `--url` arrancaría un v4complete COMPLETO sobre Salento Real — violando las restricciones de FASE-C | `agent_harness/memory.py` state: `last_url=https://www.hotelsalentoreal.com/`; orden L1406 < L1411 en main() | P5 reescrito: sembrar el estado con URL de Booking vía `MemoryManager().save_state(...)` (simula estado legacy envenenado) → comando sin `--url` → rechazo con mención del estado → verificar no-re-persistencia → restaurar `last_url` |
| F4 | AC4 exige "warning persistido en trace" sin definir el mecanismo; el implementador de A inventaría uno y el verificador de P9/VERIFY no sabría dónde buscar | No existe "trace" definido en el plan | Mecanismo concreto: archivo DEDICADO append-only `.agent/memory/url_guard_force_events.json` ({timestamp, url, comando}). Round 2: prohibido `MemoryManager().save_state` — tiene semántica REPLACE (`memory.py:303-318`) y `main.py:1411` la llama después de `ensure_url`, así que borraría el evento; P9 y VERIFY inspeccionan el archivo dedicado |
| F5 | FASE-D manda poblar `clientes/` con onboarding de Salento Real (L13), pero (a) no existe tal YAML en el repo y (b) el baseline H2 corrió CON DEFAULTS. Fabricar onboarding rompería la equivalencia AC8 (tier de evidencia, pricing, gates) | `output/clientes/` solo contiene zi-one-luxury; reporte H2: "uses default/legacy values — Tier B evidence", `direct_channel_percentage: "default"` | FASE-D corre SIN poblar clientes (defaults ≡ baseline); lección L13 reescrita en el prompt D |
| F6 | Contratos de matching sin cobertura de falsos positivos: matching por substring bloquearía dominios de hoteles legítimos (`bookingbogota.com`, `hotelairbnb.co`) | Contratos TDD del plan solo cubrían subdominios/regionales a bloquear | Contrato nuevo: dominios que CONTIENEN el nombre de plataforma como substring pero no son sufijo por etiqueta de dominio PASAN; matching = coincidencia exacta de netloc O sufijo `.plataforma.tld` entre puntos O patrones regionales explícitos |
| F7 | P1-P4: "sin llamadas API" sin criterio observable para el subagente | — | Criterio observable: exit 2 + duración < 30 s + sin artefactos nuevos en `output/` + ausencia de marcadores de scraping/auditoría en stdout |
| F8 | P9 "abortar manualmente" ambiguo para un subagente | — | Captura con timeout corto (45 s) + inspección de `url_guard_force_events` con Python; no se exige exit code al proceso matado |
| F9 | `cp output/.../**/...` de FASE-D no funciona en Git Bash sin globstar; la estructura real es anidada (`v4_complete/...`) | Estructura verificada en `output/salentoreal_final_v4c_h2/v4_complete/` | Rutas explícitas en el prompt D |
| F10 | Grep residual "superficie con URL sin guard" indefinible operacionalmente | — | Reemplazado por checks concretos: 1 definición de `ensure_url`; guardián AST 4 superficies; grep de usos de `args.url` posteriores al guard estructuralmente garantizados por el orden en `main()` |
