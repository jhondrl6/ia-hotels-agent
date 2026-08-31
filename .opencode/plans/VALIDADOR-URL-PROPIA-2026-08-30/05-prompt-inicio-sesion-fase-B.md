# FASE-B — Superficies secundarias del guard (last_url, hook-pdf, capa datos)

**ID**: VALIDADOR-URL-PROPIA / FASE-B
**Objetivo**: Extender el guard de FASE-A a todas las superficies restantes: saneamiento de `last_url` (AC6), guard de hook-pdf sobre `report_json["url"]` (AC7) y defensa en capa de datos (`assert_own_site` en scraper/auditor). **Corrección de auditoría (F2)**: el objetivo original decía "modos que no pasan por ensure_url (execute/onboard/deploy)" — premisa FALSA verificada contra código vivo: `main()` llama `ensure_url()` para TODOS los comandos en L1406 (el tuple de L217 solo excluye la reinyección de `last_url`, no la validación). Por tanto NO se agregan guards al arranque de los modos (duplicarían el enforcement y fosilizarían la duplicación — anti-lección L-PF2/L-NC10); el choke point único de FASE-A ya cubre execute/onboard/deploy.
**Dependencias**: FASE-A ✅ (guard núcleo + contratos verdes + commit hecho)
**Duración estimada**: 2 horas (~41-50 iteraciones)
**Skill**: `phased_project_executor.md` v2.17.0

## Modo de ejecución (regla del executor)

**DELEGADO — 2 subagentes en tracks localizadas + agente principal integra.**
Justificación: ediciones localizadas que REPLICAN el patrón establecido en FASE-A; no hay decisión de diseño nueva (DT-3: delegate_task para ediciones localizadas <~20 líneas con patrón conocido).

```
Subagente 1 (delegate_task) → Track main.py:
    last_url: garantía de orden (rechazo en ensure_url precede save_state L1411),
    aviso con mención del estado persistente al reinyectar URL bloqueada (AC6),
    no re-persistir bloqueadas + contratos ensure_url por comando (execute/onboard/deploy)
Subagente 2 (delegate_task) → Track librería/hook-pdf:
    hook_pdf_generator.extract_data() valida report_json["url"]
    + assert_own_site() al inicio de WebScraper.extract_hotel_data()
      y V4ComprehensiveAuditor.audit()
Parent (agente principal):
    revisar diffs, extender guardián AST a las 4 superficies reales, unificar
    mensajes/exit code con FASE-A, tests nuevos, regresión dirigida
```

Ambas tracks pueden correr en paralelo (no comparten archivos). Si una track creciera hacia decisión de diseño, el parent la retoma directamente (regla prevalente).

**Contexto obligatorio para CADA subagente** (incluir en el prompt de delegación): leer `modules/data_validation/own_site_guard.py` + `config/url_blocklist.yaml` + los tests de FASE-A (`tests/test_url_propia_guard.py`) para replicar exactamente la API, el mensaje en español y el exit code (2). Sin decisión de diseño: si algo no está definido por FASE-A, reportar al parent en vez de inventar.

## Contexto

FASE-A implementó el guard en el choke point `ensure_url()`, que `main()` invoca para TODOS los comandos (main.py:1406, verificado en auditoría) — incluidos execute/onboard/deploy. Quedan estas superficies reales: `last_url` persiste URLs envenenadas pre-fix (N3: main.py:1411 guarda, ensure_url reinyecta L216-225 — el rechazo del guard en L1406 precede a `save_state`, así que URLs nuevas bloqueadas nunca se persisten; el caso a cubrir es el estado legacy ya envenenado), hook-pdf no recibe `--url` (N8: valida `report_json["url"]`), y la capa de datos queda desprotegida para llamadores de librería (sondas, futuros módulos, handlers del harness como `_spark_handler` que llaman `V4ComprehensiveAuditor.audit(url)` directamente) → `assert_own_site()` defensivo.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| Preparación | ✅ Completada (2026-08-30) |
| FASE-A | ✅ Completada (ver `dependencias-fases.md`) |
| FASE-B | ⏳ En progreso (esta sesión) |

### Base Técnica Disponible
- `modules/data_validation/own_site_guard.py` (API de FASE-A: `assert_own_site`, `classify_url`, `UrlNoPropiaError`)
- `config/url_blocklist.yaml`, `tests/test_url_propia_guard.py`, `tests/test_guardian_ast_url_guard.py`
- Tests base: 3,631 + N de FASE-A (ver `09-documentacion-post-proyecto.md` sección D)

### Lecciones capitalizadas aplicables a esta fase
| Lección | Aplicación concreta |
|---------|---------------------|
| Si se toca un contrato, verificar TODOS los consumidores con grep (DT-3 §7.2) | `grep -n "ensure_url\|last_url\|_normalize_url(" main.py` antes de cerrar: ninguna superficie con URL sin guard |
| Integrar tracks delegados cuando tocan los mismos archivos; el criterio es overlap (L12) | Solo subagente 1 toca main.py; el parent integra ambas tracks y corre la regresión |
| Contratos transversales → AST (L7/SR-A) | Extender el guardián AST: la llamada al guard debe existir en las 4 superficies reales (`ensure_url`, `WebScraper.extract_hotel_data`, `V4ComprehensiveAuditor.audit`, `HookPDFGenerator.extract_data`) |
| TDD también para extensiones (SR-H2) | Tests de cada superficie en rojo ANTES del fix de esa superficie |
| Pytest seguro (memoria) | Lotes pequeños, salida a archivo; NUNCA `tests/commercial_documents` completa |

## Tareas

### T1: Track 1 — saneamiento last_url + contratos por comando (subagente 1 → integra parent)
**Archivos afectados**: `main.py` (solo `ensure_url`/`save_state` si hiciera falta), `tests/test_url_propia_guard.py` (extensión)

**Contratos (rojo primero)**:
1. `ensure_url` con `args.command` ∈ {execute, onboard, deploy} y `args.url` bloqueada → mismo rechazo que v4complete (exit 2, mensaje en español). Estos comandos YA pasan por `ensure_url` (main.py:1406) — este contrato LO DOCUMENTA, no requiere guard adicional en los modos.
2. Rechazo con URL bloqueada → `save_state` NO es llamado con esa URL (test con spy/monkeypatch sobre `MemoryManager.save_state`; garantía de orden: `ensure_url` L1406 precede a `save_state` L1411).
3. Estado persistente con `last_url` bloqueada (estado legacy envenenado, sembrado con monkeypatch de `load_state`) + comando sin `--url` → rechazo con mención explícita de que proviene del estado persistente (AC6), y la URL bloqueada NO se re-persiste.

**Criterios de aceptación**:
- [ ] AC6 cubierto por test (contratos 2 y 3).
- [ ] NO se agregaron guards al arranque de run_execution_mode/run_onboard_mode/run_deploy_mode (auditoría F2); el grep de `assert_own_site` en main.py muestra UNA sola llamada (en `ensure_url`).

### T2: Track 2 — hook-pdf + capa de datos (subagente 2 → integra parent)
**Archivos afectados**: `modules/commercial_documents/hook_pdf_generator.py`, `modules/scrapers/web_scraper.py`, `modules/auditors/v4_comprehensive.py`, tests

**Contratos (rojo primero)**:
1. `hook-pdf` con `v4_complete_report.json` cuya `url` es de plataforma bloqueada → rechazo claro (AC7), sin generar PDF.
2. `WebScraper().extract_hotel_data(url_booking)` → `UrlNoPropiaError` antes de cualquier petición HTTP.
3. `V4ComprehensiveAuditor` con URL OTA → excepción antes de cualquier llamada Places.
4. Sitio propio → comportamiento inalterado (fixture hotelsalentoreal.com).

**Criterios de aceptación**:
- [ ] AC7 cubierto por test.
- [ ] Llamadores de librería protegidos (defensa opcional #6 del contexto, adoptada).
- [ ] Nota de regresión (auditoría 2026-08-30): existen 5 fixtures con dominios bloqueados (`test_seo_elements_detector.py:87`, `test_autonomous_research_fase8.py:33/133/164`, `test_publication_gates.py:1351`) pero NINGUNO llama a `extract_hotel_data()` ni a `audit()` (son HTML inline, provider scraper distinto y claims de gate) → no deberían romperse; confirmarlo en la regresión de T3.

### T3: Integración + guardián AST completo + regresión (parent, directo)
**Acciones**:
- Revisar diff de ambas tracks; unificar mensajes/exit code con FASE-A.
- Extender `tests/test_guardian_ast_url_guard.py`: el guard debe aparecer en las 4 superficies reales: `ensure_url` (main.py) + `WebScraper.extract_hotel_data` + `V4ComprehensiveAuditor.audit` + `extract_data` del hook-pdf (patrón SR-A). Y verificar que NO aparezca al arranque de los modos run_execution_mode/run_onboard_mode/run_deploy_mode (auditoría F2: redundancia fosilizada).
- Regresión dirigida: `test_url_propia_guard.py`, guardián AST, `test_target_id_canonicalization.py` (28), suites de hook-pdf/scrapers/auditors tocadas → salida a archivo.
- Grep de residuos (L2): `grep -rn "def ensure_url" main.py` (1 definición); verificar que ninguna superficie con URL quedó sin guard.
- `python scripts/run_all_validations.py --quick` (clasificar fallos documentales vs de código).

**Criterios de aceptación**:
- [ ] Guardián AST extendido PASSED.
- [ ] 28/28 canonicalización PASSED.
- [ ] Sin fallos nuevos vs baseline registrada en FASE-A.

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Contratos extendidos | `tests/test_url_propia_guard.py` | 100% PASSED |
| Guardián AST completo | `tests/test_guardian_ast_url_guard.py` | PASSED (4 superficies: ensure_url, extract_hotel_data, audit, extract_data) |
| Regresión canonicalización | `tests/test_target_id_canonicalization.py` | 28/28 PASSED |
| Suites tocadas (hook-pdf, scrapers, auditors) | según toque | Sin fallos nuevos |

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️ Antes de cerrar la sesión:

1. `dependencias-fases.md` → FASE-B ✅ con fecha.
2. `README.md` del plan → progreso.
3. `06-checklist-implementacion.md` → fila FASE-B ✅.
4. `09-documentacion-post-proyecto.md` → B/D/E.
5. `10-analisis-post-implementacion.md` → Resumen de Ejecución (columna delegate_task: 2 subagentes), Métricas, mínimo 3 lecciones (incluir evaluación de la delegación: qué funcionó/qué no).
6. Evidencia: `evidence/FASE-VUP-B/` (copiar salidas pytest de `temp/`).
7. Registro (SIN `--release`):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-B --desc "Guard extendido: saneamiento last_url (AC6) + hook-pdf (AC7) + capa datos assert_own_site (scraper/auditor)" \
    --archivos-mod "main.py,modules/commercial_documents/hook_pdf_generator.py,modules/scrapers/web_scraper.py,modules/auditors/v4_comprehensive.py,tests/test_url_propia_guard.py,tests/test_guardian_ast_url_guard.py" \
    --tests "N" --check-manual-docs
```
8. `python scripts/doctor.py --regenerate-domain-primer`
9. Commit.

## Criterios de Completitud (CHECKLIST)

- [ ] AC5: guard en TODOS los comandos con URL (guardián AST verde)
- [ ] AC6: last_url saneada (test verde)
- [ ] AC7: hook-pdf rechaza url bloqueada (test verde)
- [ ] 28/28 canonicalización PASSED
- [ ] Post-ejecución completa (9 puntos)

## Restricciones

- **Máximo 60 iteraciones** (R2); subagentes con timeout adecuado y reporte acotado.
- NO modificar la API/mensajes/exit code definidos en FASE-A (replicar, no rediseñar).
- NO tocar `_normalize_url` ni los normalizadores (N6/N9).
- NO ejecutar `v4complete` (FASE-D).
- Subagentes NO toman decisiones de diseño: ante ambigüedad, reportan al parent.
- NO usar `--release` en `log_phase_completion.py`.
