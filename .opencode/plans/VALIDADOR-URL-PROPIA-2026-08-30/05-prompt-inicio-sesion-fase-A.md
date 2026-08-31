# FASE-A — Contratos TDD + núcleo del guard de URL propia

**ID**: VALIDADOR-URL-PROPIA / FASE-A
**Objetivo**: Implementar el guard de entrada que rechaza URLs no-propias (OTA/red social/buscador) en el choke point `ensure_url()`, con blocklist versionada en `config/`, bypass `--force` documentado y contratos TDD escritos ANTES del fix.
**Dependencias**: Ninguna (primera fase de implementación)
**Duración estimada**: 2-3 horas (~51-60 iteraciones, presupuesto ajustado)
**Skill**: `phased_project_executor.md` v2.17.0

## Modo de ejecución (regla del executor)

**DIRECTO con el agente principal — NO delegar.** Esta fase contiene la decisión arquitectónica del choke point único (dónde y cómo se enforcea el invariante "URL ≡ sitio propio"). Un subagente carece del contexto completo de `main.py` para tomarla correctamente (lección DT-3). Herramientas: terminal + edición de archivos.

## Contexto

El contexto fuente es `.opencode/context/CONTEXT-GAP-URL-NO-PROPIA-SONDA-2026-08-29.md` (leerlo primero). Resumen: `_normalize_url()` (main.py:3604-3615) reduce toda URL a netloc; con URLs de OTA el path ES la identidad del hotel → colisión de `target_id` (GA-1). El scraper no distingue sitio propio de tercero y emite datos con confianza arbitraria: sonda real 29-08 → Instagram produjo `confidence: alta` y `cms: shopify` FALSOS (GA-2). El invariante "URL de entrada ≡ sitio propio" es implícito (RC1): ninguna etapa lo valida.

**Decisión adoptada (contexto §5)**: Opción A — guard de entrada blocklistado con abort fuerte antes de cualquier red/API.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| Preparación | ✅ Completada (2026-08-30) |
| FASE-A | ⏳ En progreso (esta sesión) |

### Base Técnica Disponible
- `main.py`: `ensure_url()` L216-225 (choke point + reinyección `last_url`), `save_state` L1411, `run_v4_complete_mode` L1654, `_normalize_url` L3604-3615.
- Semillas OTA existentes (centralizar, NO crear un tercer sistema): lista `otas` en `modules/scrapers/web_scraper.py:523` y opciones OTA de `modules/orchestration_v4/two_phase_flow.py:716-722`.
- Tests base: 3,631 funciones (conteo `def test_`); `tests/test_target_id_canonicalization.py` (28 tests, congelan semántica netloc-only — N9).
- Línea base sucia conocida: hasta 12 tests rojos preexistentes (test_calculator_v2 ×3, test_pricing_resolution_wrapper ×8, test_site_verification_propagation ×1, al 2026-08-29) + `test_config_pricing::test_tiers_boutique_min_price`. Re-verificar en T1 y registrar el estado real; NO son de este plan.

### Lecciones capitalizadas aplicables a esta fase (Paso 0)
| Lección | Aplicación concreta |
|---------|---------------------|
| TDD contratos ANTES del fix (precedente SR-H2) | `tests/test_url_propia_guard.py` rojo → implementar → verde |
| Fix ORTOGONAL al normalizador (N9) | NO modificar `_normalize_url()` ni `generate_hotel_id()`; los 28 tests deben seguir verdes sin cambios |
| "El gap está en el caller: verificar si el helper ya existe" (L16) | Reusar `_normalize_url()` para extraer el netloc en el guard; no reimplementar parsing |
| Contratos transversales → AST, no regex (L7/SR-A) | Test guardián AST: el guard DEBE ser invocado dentro de `ensure_url` |
| Grep de residuos post-fix (L2) | Al cerrar: grep de las listas OTA duplicadas que fueron centralizadas |
| Pytest seguro (memoria) | Lotes pequeños, `> temp/x.txt 2>&1`, NUNCA suite `tests/commercial_documents` completa |
| Clasificar fallos de validación (L2 vieja) | Version Sync → `sync_versions.py`; NO re-correr la suite esperando que pase |

## Tareas

### T1: Línea base (investigación)
**Objetivo**: Registrar el estado real de la suite antes de tocar código.

**Acciones**:
- Ejecutar `tests/test_target_id_canonicalization.py` (deben ser 28 PASSED) y la selección con fallos conocidos (test_calculator_v2, test_pricing_resolution_wrapper, test_site_verification_propagation, test_config_pricing) con salida a archivo en `temp/fase_a_baseline.txt`.
- Anotar conteo de fallos en `10-analisis-post-implementacion.md` (Seguimientos abiertos) para que las fases siguientes no los atribuyan al plan.

**Criterios de aceptación**:
- [ ] Baseline registrada con fecha y conteos reales.

### T2: Contratos TDD + implementación del núcleo (fix)
**Objetivo**: Guard funcional en `ensure_url()` con blocklist versionada y `--force`.

**Archivos afectados**:
- `tests/test_url_propia_guard.py` (NUEVO — escribir PRIMERO, debe fallar)
- `config/url_blocklist.yaml` (NUEVO — versionado, con categorías `ota` / `red_social` / `buscador` y matching por sufijo de etiquetas de dominio: `*.booking.com`, dominios regionales `booking.com.*`, `google.*`; NUNCA matching por substring — ver contrato 7)
- `modules/data_validation/own_site_guard.py` (NUEVO — API sugerida: `classify_url(url) -> UrlClassification`, `assert_own_site(url, force=False, origen="--url"|"estado_persistente")`, excepción `UrlNoPropiaError` con mensaje en español que nombre la plataforma y pida la URL del sitio propio (si `origen="estado_persistente"`, el mensaje menciona explícitamente el estado persistente — AC6); exit code 2 en CLI)
- `main.py` — SOLO `ensure_url()` (L216-225): **el guard va DESPUÉS de la rama de reinyección de `last_url`** (la reinyección ocurre en L222 dentro de esta misma función; si el guard se pone antes, una `last_url` envenenada preexistente pasaría sin validar). Cubre TODOS los comandos (auditoría: `main()` llama `ensure_url()` en L1406 antes de cualquier routing, incluido execute/onboard/deploy). **`--force` YA EXISTE como flag global (main.py:172, hoy "Sobrescribir PDF si ya existe") — REUTILIZARLO, prohibido `add_argument("--force")` de nuevo (argparse lanzaría ArgumentError); extender su help a la semántica dual.** Con `--force`: no lanza; persiste el evento en `.agent/memory/url_guard_force_events.json` — archivo DEDICADO append-only ({timestamp, url, comando} por línea/entrada). ⚠️ **Auditoría round 2**: NO usar `MemoryManager().save_state` para el evento: `save_state` tiene semántica REPLACE (verificado `memory.py:303-318`) y `main.py:1411` la llama con `{"last_url": ...}` DESPUÉS de `ensure_url`, así que borraría el evento. Nota semántica AC6: con `--force` la URL bloqueada SÍ se persiste como `last_url` en L1411 (bypass explícito del operador); la reinyección posterior será rechazada por el guard con mención del estado persistente — comportamiento correcto y auto-consistente, documentarlo en el test.
- `tests/test_guardian_ast_url_guard.py` (NUEVO — guardián AST: `ensure_url` invoca el guard)

**Contratos mínimos del test (rojos primero)**:
1. `booking.com/hotel/co/x`, `instagram.com/x`, `facebook.com/x`, `google.com/...` → `UrlNoPropiaError` con categoría correcta.
2. `hotelsalentoreal.com` (y variantes con path/query) → pasa el guard.
3. Subdominios (`www.booking.com`, `secure.instagram.com`) y regionales (`booking.com.co`, `google.com.co`) → bloqueados.
4. `--force` → no lanza; retorna clasificación marcada y el evento queda persistido en `.agent/memory/url_guard_force_events.json` (verificable leyendo el archivo).
5. Guard usa `_normalize_url()` para el netloc (no parser propio).
6. Guardián AST: la llamada al guard existe dentro del cuerpo de `ensure_url`.
7. **Anti-falsos-positivos (auditoría F6)**: dominios que CONTIENEN el nombre de plataforma como substring pero no como sufijo de etiqueta PASAN: `bookingbogota.com`, `hotelairbnb.co`, `mytripadvisorhotel.com` → no bloqueados. Matching = netloc exacto O sufijo `.plataforma.tld` entre puntos O patrón regional explícito del yaml.

**Criterios de aceptación**:
- [ ] Contratos escritos y ROJOS antes del fix (evidencia en `temp/fase_a_red.txt`).
- [ ] `config/url_blocklist.yaml` centraliza las semillas existentes (referencia en comentario del yaml a web_scraper.py:523 / two_phase_flow.py:716-722).
- [ ] El rechazo ocurre ANTES de cualquier llamada de red/API (verificable en el orden del código de `main()`: `ensure_url` L1406 precede a routing y a `save_state` L1411).
- [ ] El guard valida TAMBIÉN la URL reinyectada desde `last_url` (colocado después de la rama de reinyección).
- [ ] `--force` reutiliza el flag global existente (main.py:172) y persiste el evento en `.agent/memory/url_guard_force_events.json` (AC4).
- [ ] Mensaje de rechazo en español, claro, con la plataforma nombrada.

### T3: Verificación + regresión dirigida
**Objetivo**: Verde sin regresión.

**Acciones**:
- `pytest tests/test_url_propia_guard.py tests/test_guardian_ast_url_guard.py -v > temp/fase_a_guard.txt 2>&1`
- `pytest tests/test_target_id_canonicalization.py -v > temp/fase_a_canon.txt 2>&1` → 28/28 PASSED (AC3).
- Suites tocadas (si existen): tests de `data_validation/`, tests de main/orquestación que ejerciten `ensure_url`. Lotes pequeños, salida a archivo.
- `python scripts/run_all_validations.py --quick` (si falla Version Sync → `sync_versions.py`; clasificar, no re-correr).

**Criterios de aceptación**:
- [ ] Todos los contratos verdes.
- [ ] 28/28 canonicalización PASSED sin modificar ese test.
- [ ] Sin fallos NUEVOS respecto a la baseline de T1.

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Contratos del guard | `tests/test_url_propia_guard.py` | 100% PASSED |
| Guardián AST | `tests/test_guardian_ast_url_guard.py` | PASSED |
| Regresión canonicalización | `tests/test_target_id_canonicalization.py` | 28/28 PASSED |
| Validaciones | `python scripts/run_all_validations.py --quick` | TOTAL PASS (o solo fallos baseline registrados) |

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️ Antes de cerrar la sesión:

1. `dependencias-fases.md` → FASE-A ✅ con fecha + registro de estado.
2. `README.md` del plan → progreso.
3. `06-checklist-implementacion.md` → fila FASE-A ✅.
4. `09-documentacion-post-proyecto.md` → secciones B (guard), D (+N tests con `git diff tests/ | grep -E '^\+\s*def test_'`), E (archivos).
5. `10-analisis-post-implementacion.md` → fila en Resumen de Ejecución, Métricas, Decisiones Arquitectónicas (D-VUP-A1 choke point, D-VUP-A3 blocklist centralizada), mínimo 3 lecciones nuevas.
6. Evidencia: `evidence/FASE-VUP-A/` (copiar `temp/fase_a_*.txt`).
7. Registro de la fase (SIN `--release`):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-A --desc "Guard de URL propia: blocklist config + own_site_guard + choke point ensure_url + --force (TDD)" \
    --archivos-nuevos "config/url_blocklist.yaml,modules/data_validation/own_site_guard.py,tests/test_url_propia_guard.py,tests/test_guardian_ast_url_guard.py" \
    --archivos-mod "main.py" --tests "N" --check-manual-docs
```
8. `python scripts/doctor.py --regenerate-domain-primer`
9. Commit (pre-commit hook activo: version-sync + ecosystem).

## Criterios de Completitud (CHECKLIST)

- [ ] Contratos TDD rojos→verdes documentados
- [ ] 28/28 canonicalización PASSED (sin tocar el normalizador)
- [ ] `--force` con warning persistido (AC4)
- [ ] Sin fallos nuevos vs baseline
- [ ] `run_all_validations.py --quick` clasificado/pasado
- [ ] Post-ejecución completa (9 puntos)

## Restricciones

- **Máximo 60 iteraciones** (R2). Si se agota: marcar ⏳ INCOMPLETA con checkpoint en `dependencias-fases.md`, guardar evidencia, cerrar.
- **NO modificar** `_normalize_url()`, `_extract_hotel_name_from_url()`, `_detect_region_from_url()` ni `OnboardingController.generate_hotel_id()` (N6/N9).
- **NO tocar** modos execute/onboard/deploy, hook-pdf ni `last_url` — son de FASE-B.
- NO ejecutar `v4complete` (FASE-D).
- NO usar `--release` en `log_phase_completion.py`.
- Fuera de alcance: RC3 (confidence/CMS del scraper), N5 (bug numérico), N7 (higiene main.py), residuos pricing (§7 del contexto).
