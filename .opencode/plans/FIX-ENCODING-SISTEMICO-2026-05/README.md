# FIX-ENCODING-SISTEMICO — Prevención de Memory Leak por Encoding

> **Plan ID:** FIX-ENCODING-SISTEMICO-2026-05
> **ROADMAP ref:** N/A (patch operativo post-incidente)
> **Repo baseline:** v4.46.0
> **Created:** 2026-05-14
> **Last validated:** 2026-05-14 (v2 — corregido contra código vivo)
> **Constraint:** 1 fase/sesión. Fase A ya completada (parche inmediato).
> **Contexto forense:** `.opencode/context/INCIDENTE-FORENSE-BLOQUEO-SISTEMA-2026-05-13.md` §8

---

## Contexto del incidente

2026-05-13 22:16: `python.exe` (Windows) consumió 42.5 GB de memoria virtual y congeló el sistema. Causa raíz: `scripts/validate_document_integration.py` imprimió caracteres Unicode en stdout configurado en `cp1252` (default Windows), generando `UnicodeEncodeError`. Hermes re-ejecutó el script 5 veces en 3 minutos sin limpieza de procesos fallidos. Los pipes rotos acumularon excepciones en buffers crecientes → memory leak → DWM crash → apagado forzado.

**Mecanismo completo (3 capas):**
1. Python imprime `↔` en stdout cp1252 → `UnicodeEncodeError`
2. La excepción rompe la pipe Hermes↔Python → `_readerthread` exception
3. Hermes re-ejecuta sin limpiar el proceso zombie → buffers huérfanos se acumulan

Ver documento forense completo: `.opencode/context/INCIDENTE-FORENSE-BLOQUEO-SISTEMA-2026-05-13.md`

---

## Objetivo

Eliminar permanentemente la clase de bug `UnicodeEncodeError` en scripts Python invocados por Hermes en Windows, y prevenir la re-ejecución ciega de comandos fallidos.

Sub-objetivos:
1. Parchear los scripts que REALMENTE carecen de fix de encoding (verificado contra código vivo 2026-05-14).
2. Verificar que los scripts ya parcheados usan un patrón funcional.
3. Documentar la convención UTF-8 obligatoria con patrón estandarizado.
4. Investigar si Hermes puede configurarse para detener reintentos tras N fallos idénticos.

---

## Alcance (CORREGIDO — 2026-05-14)

| ID | Entregable | Estado actual | Acción planificada |
|----|------------|---------------|--------------------|
| B-01 | Auditoría real: 21 scripts en `scripts/` + `main.py` | **Hecha** (ver forense §8.7) | Solo ejecutar parches en los 3 scripts que carecen de fix |
| B-02 | Parche `verify_ga4.py` | Sin fix. `print()` con tildes (ñ, í, ó). Riesgo ALTO. | Aplicar patrón `reconfigure()` |
| B-03 | Parche `validate_structure.py` | Sin fix. `print()` con tildes (ó, é). Riesgo ALTO. | Aplicar patrón `reconfigure()` |
| B-04 | Parche `update_benchmarks.py` | Sin fix. `print()` con `→`. Riesgo MEDIO. | Aplicar patrón `reconfigure()` |
| B-05 | Verificar `main.py` | **YA tiene fix** (`reconfigure` L32-35). 236 líneas Unicode pero protegidas. | Verificar, no modificar |
| B-06 | Verificar `derive_version_from_changelog.py` | **YA tiene fix** (reconfigure + TextIOWrapper L12-17). | Verificar, no modificar |
| B-07 | Verificar `version_consistency_checker.py` | **YA tiene fix** (reconfigure + TextIOWrapper L28-35). | Verificar, no modificar |
| B-08 | Verificar `log_phase_completion.py` | **YA tiene fix** (reconfigure + TextIOWrapper L39-46). | Verificar, no modificar |
| B-09 | Cancelar revisión `doctor.py` | **CERO Unicode** detectado. Falsa alarma del plan original. | Tarea cancelada |
| C-01 | Configuración anti-reintentos Hermes | No investigada | Revisar `repeated_exact_failure_warning` y thresholds. Documentar limitaciones. Incluir investigación del cleanup de procesos tras pipe rota. |
| D-01 | Nota en CONTRIBUTING.md sobre encoding | Inexistente | Agregar sección "Encoding en scripts Python" con patrón estandarizado `reconfigure()` |
| D-02 | Regla en documentation_rules.md | Inexistente | Agregar gate: scripts con `print()` sin fix de encoding = FAIL |

---

## No-Alcance

- No reescribir scripts que ya tienen fix (aunque usen patrón distinto — ambos funcionan).
- No modificar el código fuente de Hermes Agent (fuera de nuestro control).
- No cambiar el default encoding de Windows.
- No ejecutar docs cascade automático salvo en fase RELEASE.
- No parchear scripts con Unicode solo en comentarios (baja prioridad, no bloquean).

---

## Decisiones arquitectónicas (CORREGIDAS)

| # | Decisión | Opciones | Veredicto | Justificación |
|---|----------|----------|-----------|---------------|
| D1 | ¿Parchear script por script o crear wrapper central? | Wrapper `scripts/_encoding_guard.py` / Parche individual | **Parche individual** | Wrapper añade dependencia de import; el patrón son 3-5 líneas auto-documentadas. Tradeoff: duplicación vs simplicidad. |
| D2 | ¿`errors='replace'` o `errors='backslashreplace'`? | replace / backslashreplace / strict / ignore | **`replace`** | `replace` sustituye por `�` — visible para humanos. `backslashreplace` genera `\u2192` que confunde en output terminal. |
| D3 | ¿Auditar solo `scripts/` o también `modules/`? | Solo scripts CLI / Todo / Solo invocados por Hermes | **Todos los scripts CLI en `scripts/` + `main.py`** | `modules/` es librería importada. El riesgo está en scripts ejecutados directamente. El inventario completo son 21 scripts en `scripts/`. |
| D4 | ¿Criterio de riesgo para priorizar parches? | Todos de golpe / Solo Unicode explícito / Solo prints | **Scripts con `print()` que contienen caracteres U+0080+ Y carecen de fix de encoding** | Los prints ASCII-only no fallan en cp1252. Unicode en comentarios no causa crash. Solo los prints con caracteres fuera del rango ASCII son vulnerables. |
| D5 | ¿Forzar UTF-8 en todos los scripts o solo en los que fallan? | Todos / Solo falladores / Todos los CLI scripts | **Solo los 3 scripts sin fix + documentar el patrón para futuros scripts** | 5 scripts ya tienen fix (main.py + 4 en scripts/). Parchear el resto sería redundante. El plan original decía "todos" pero era porque no sabía cuántos ya tenían fix. |
| D6 | ¿Fase C (config Hermes) es implementable o solo investigación? | Implementar / Documentar limitación / Nada | **Investigar y documentar** | Hermes Agent no es código nuestro. Si no hay config expuesta, documentamos workaround. |
| D7 | ¿Patrón de fix estandarizado? | `reconfigure()` / `TextIOWrapper` / Ambos | **`reconfigure()` como primario, `TextIOWrapper` como fallback** | `reconfigure()` es más limpio y ya lo usan main.py y 3 scripts. `TextIOWrapper` solo si `hasattr(sys.stdout, "reconfigure")` es False (Python <3.7). No reescribir scripts ya parcheados. |

---

## Fases

| Fase | Nombre | Tipo | Estado |
|------|--------|------|--------|
| A | Parche inmediato validate_document_integration.py | Código | ✅ Completada 2026-05-14 |
| **B** | **Parche 3 scripts + verificar 4 ya parcheados** | **Código** | **✅ Completada 2026-05-14** |
| C | Configuración anti-reintentos Hermes | Investigación | ✅ Completada 2026-05-14 |
| D | Documentación y reglas | Documentación | ✅ Completada 2026-05-14 |
| RELEASE | Docs cascade | Documentación | ✅ Completada 2026-05-14 |

---

## Criterios de éxito

| Gate | Pregunta | Evidencia esperada |
|------|----------|-------------------|
| G-B1 | ¿Los 3 scripts sin fix (`verify_ga4.py`, `validate_structure.py`, `update_benchmarks.py`) tienen `reconfigure()` activo? | `grep -n "reconfigure\|TextIOWrapper"` devuelve match en cada uno |
| G-B2 | ¿Los 4 scripts ya parcheados (`main.py`, `derive_version_from_changelog.py`, `version_consistency_checker.py`, `log_phase_completion.py`) conservan su fix sin cambios? | `grep` confirma que el fix sigue presente (sin modificar) |
| G-B3 | ¿Los 3 scripts nuevos ejecutan sin `UnicodeEncodeError` en Windows? | `python scripts/verify_ga4.py` etc. completan sin excepciones de encoding |
| G-C | ¿Existe documentación sobre reintentos y cómo mitigarlos? | ✅ Sección en plan con hallazgos completos. Sistema de guardrails nativo de Hermes (`tool_loop_guardrails`) cubre el caso. Incluye análisis de cleanup de procesos tras pipe rota (SIGTERM → SIGKILL). |
| G-D | ¿CONTRIBUTING.md y documentation_rules.md mencionan encoding con el patrón `reconfigure()`? | Match en ambos archivos con la convención UTF-8 obligatoria usando `reconfigure()` como estándar |
| G-VAL | ¿`run_all_validations.py --quick` sigue pasando? | Checks sin regresiones por los parches |

---

## Baseline verificado (2026-05-14) — INVENTARIO REAL

### Scripts que NECESITAN parche (sin fix, Unicode en prints)

| Archivo | Carácter problemático | Tipo | Riesgo |
|---------|----------------------|------|--------|
| `scripts/verify_ga4.py` | `ñ`, `í`, `ó` (tildes español) | print() | **ALTO** |
| `scripts/validate_structure.py` | `ó`, `é` (tildes español) | print() | **ALTO** |
| `scripts/update_benchmarks.py` | `→` (U+2192) | print() | **MEDIO** |

### Scripts YA PROTEGIDOS (verificar, no modificar)

| Archivo | Fix presente | Líneas | Unicode detectado |
|---------|-------------|--------|-------------------|
| `main.py` | `reconfigure()` | L32-35 | 236 líneas (emojis, flechas, tildes) |
| `scripts/derive_version_from_changelog.py` | `reconfigure()` + `TextIOWrapper` fallback | L12-17 | `→` (U+2192) |
| `scripts/version_consistency_checker.py` | `reconfigure()` + `TextIOWrapper` fallback | L28-35 | `✅`, `❌`, `⚠️` |
| `scripts/log_phase_completion.py` | `reconfigure()` + `TextIOWrapper` fallback | L39-46 | Tildes español |
| `scripts/validate_document_integration.py` | `TextIOWrapper` en main block | L461-462 | `§`, `—` (em-dash) |

### Scripts sin Unicode en prints (no requieren acción)

`doctor.py`, `cleanup_sessions.py`, `cleanup_workdirs.py`, `normalize_cache_filenames.py`, `prune_outputs.py`, `structure_guard.py`, `validate.py`, `validate_agent_ecosystem.py`

### Scripts con Unicode solo en comentarios (baja prioridad)

`sync_versions.py`, `fill_upgrade_proposal.py`, `config_checker.py`, `validate_context_integrity.py`, `run_all_validations.py`, `generate_system_status.py`

### Gap documentado (FASE-A)

`validate_document_integration.py` L52, L55: `sys.stderr.write()` dentro de `read_file()` se ejecuta a nivel de módulo, FUERA del bloque `if __name__ == "__main__"` donde está el `TextIOWrapper` (L461). Si hay error de archivo al importar, `stderr.write()` con Unicode podría fallar antes de que el fix se active. **Riesgo: bajo. No requiere parche inmediato.**

---

*Este documento debe cargarse al inicio de cada sesión de este plan para establecer contexto.*
*Validado contra código vivo el 2026-05-14. Ver forense §8 para el análisis completo.*
