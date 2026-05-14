# Checklist de Implementación — FIX-ENCODING-SISTEMICO (v2 corregida)

> **Regla:** Máximo 1 fase/sesión. Cada item se marca ✅ al completar en su sesión.
> **Corregido:** 2026-05-14 contra código vivo. Ver forense §8.
> **Cambios vs v1:** 4 scripts ya tenían fix (se verifican, no se parchean). 1 script era falsa alarma (doctor.py). 3 scripts reales necesitan parche.

---

## FASE-A: Parche inmediato (COMPLETADA 2026-05-14)

| # | Tarea | Estado | Criterio PASS |
|---|-------|--------|---------------|
| A-1 | Parchear `scripts/validate_document_integration.py` con UTF-8 en stdout/stderr | ✅ | `io.TextIOWrapper` presente en L461-462 dentro de `if __name__ == "__main__"` |
| A-2 | Verificar que el script ejecuta sin `UnicodeEncodeError` en Windows | ✅ | Sin excepciones de encoding |

**Caveat documentado:** `sys.stderr.write()` en L52, L55 (función `read_file()`) está fuera del bloque main. Si hay error de archivo al importar, stderr podría fallar con Unicode antes de activarse el fix. Riesgo bajo — no requiere acción.

---

## FASE-B: Parche 3 scripts + Verificar 4 ya parcheados + Validar

> **Estrategia corregida:** El análisis contra código vivo (2026-05-14) reveló que 5 scripts ya tienen fix de encoding (main.py + 4 en scripts/). Solo 3 scripts necesitan parche real. El resto son verificaciones.

### BLOQUE 1 — Parches reales (3 scripts sin fix)

| # | Tarea | Estado | Criterio PASS |
|---|-------|--------|---------------|
| B-1 | **Parchear `scripts/verify_ga4.py`** — agregar `reconfigure()` para UTF-8 | ✅ | `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` presente en L6-8; script ejecuta sin `UnicodeEncodeError` (solo falla por dotenv ausente en WSL) |
| B-2 | **Parchear `scripts/validate_structure.py`** — agregar `reconfigure()` para UTF-8 | ✅ | `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` presente en L23-25; script ejecuta sin `UnicodeEncodeError` |
| B-3 | **Parchear `scripts/update_benchmarks.py`** — agregar `reconfigure()` para UTF-8 | ✅ | `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` presente en L36-38; script ejecuta sin `UnicodeEncodeError` (DRY RUN exit 0) |

**Patrón estándar a aplicar (3 líneas al inicio del script, antes de cualquier print):**
```python
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
```

### BLOQUE 2 — Verificaciones (4 scripts ya parcheados, NO modificar)

| # | Tarea | Estado | Criterio PASS |
|---|-------|--------|---------------|
| B-4 | **Verificar `main.py`** — fix `reconfigure()` ya presente en L32-35 | ✅ | `grep -n "reconfigure.*utf-8" main.py` devuelve match L32-35. No modificar. |
| B-5 | **Verificar `scripts/derive_version_from_changelog.py`** — fix ya presente en L12-17 | ✅ | `grep -n "reconfigure\|TextIOWrapper"` devuelve match L14, L17. No modificar. |
| B-6 | **Verificar `scripts/version_consistency_checker.py`** — fix ya presente en L28-35 | ✅ | `grep -n "reconfigure\|TextIOWrapper"` devuelve match L31, L35. No modificar. |
| B-7 | **Verificar `scripts/log_phase_completion.py`** — fix ya presente en L39-46 | ✅ | `grep -n "reconfigure\|TextIOWrapper"` devuelve match L42, L46. No modificar. |

### BLOQUE 3 — Validación final

| # | Tarea | Estado | Criterio PASS |
|---|-------|--------|---------------|
| B-8 | Ejecutar `python scripts/verify_ga4.py` en Windows (o WSL con python.exe) | ✅ | Sin `UnicodeEncodeError` (falla por dotenv ausente en WSL, no por encoding) |
| B-9 | Ejecutar `python scripts/validate_structure.py` en Windows | ✅ | Sin `UnicodeEncodeError`. Reporta 2 errores preexistentes de estructura. |
| B-10 | Ejecutar `python scripts/update_benchmarks.py` en Windows | ✅ | Sin `UnicodeEncodeError`. DRY RUN exit 0, output con Unicode correcto. |
| B-11 | Ejecutar `python scripts/run_all_validations.py --quick` | ✅ | 5/5 validations passed. Sin regresiones. |

### Tareas canceladas (falsas alarmas del plan v1)

| # | Tarea original | Motivo cancelación |
|---|---------------|-------------------|
| ~~B-1 (v1)~~ | ~~Crear script audit_encoding_risk.py~~ | Auditoría ya realizada en sesión 2026-05-14. Resultados en forense §8.7. |
| ~~B-6 (v1)~~ | ~~Revisar doctor.py~~ | **CERO Unicode detectado.** Falsa alarma. |
| ~~B-7 (v1)~~ | ~~Evaluar competitor_analyzer.py~~ | `logger.info` con Unicode = bajo riesgo. Logging handlers tienen su propio encoding. |

**Veredicto FASE-B:** 3 parches + 4 verificaciones + validación.

---

## FASE-C: Configuración anti-reintentos Hermes ✅ COMPLETADA 2026-05-14

| # | Tarea | Estado | Criterio PASS |
|---|-------|--------|---------------|
| C-1 | Investigar `repeated_exact_failure_warning` en documentación/config de Hermes | ✅ | Encontrado en `agent/tool_guardrails.py` (PR #1321). Configurable via `tool_loop_guardrails` en `~/.hermes/config.yaml`. |
| C-2 | Determinar si existe configuración para detener ejecución tras N fallos idénticos | ✅ | **SÍ EXISTE.** `hard_stop_enabled` (bool) + `hard_stop_after.exact_failure` (int). Por defecto estaba desactivado. |
| C-3 | Si configurable: aplicar threshold (max 2 reintentos para mismo comando+mismo error) | ✅ | `hard_stop_enabled: true` + `hard_stop_after.exact_failure: 3`. Aplicado con `hermes config set`. Requiere nueva sesión. |
| C-4 | Si no configurable: documentar workaround en AGENTS.md o en este plan | ✅ | No necesario. La solución nativa de Hermes cubre el caso. El plan original asumía que no existía esta feature. |
| C-5 | **Investigar cleanup de procesos tras pipe rota** — ¿Hermes hace SIGKILL si SIGTERM no responde? | ✅ | `ProcessRegistry.kill_process()`: SIGTERM → SIGKILL (local), `terminate()` (Windows). Background cleanup cada 60s para environments inactivos >300s. |
| C-6 | Verificar si existe issue/feature request en repositorio Hermes sobre esto | ✅ | PR #1321 (@alireza78a) merged — implementó exactamente esta feature. GitHub API bloqueada, no se verificaron issues adicionales. |

### Hallazgos detallados FASE-C

#### Sistema de guardrails de Hermes (`agent/tool_guardrails.py`)

Hermes v0.13.0 incluye un controlador de guardrails para el loop de tool-calling que detecta 3 tipos de bucles:

| Tipo | Detecta | Warning (default) | Hard stop (default) |
|------|---------|-------------------|---------------------|
| `exact_failure` | Mismo tool + mismos args falla repetidamente | 2 | 5 |
| `same_tool_failure` | Misma tool falla (args pueden variar) | 3 | 8 |
| `idempotent_no_progress` | Tool read-only devuelve mismo resultado | 2 | 5 |

#### Cambios aplicados a `~/.hermes/config.yaml`:
```yaml
tool_loop_guardrails:
  warnings_enabled: true        # sin cambios
  hard_stop_enabled: true       # ANTES: false → AHORA: true
  warn_after:
    exact_failure: 2            # sin cambios
    same_tool_failure: 3        # sin cambios
    idempotent_no_progress: 2   # sin cambios
  hard_stop_after:
    exact_failure: 3            # ANTES: 5 → AHORA: 3
    same_tool_failure: 8        # sin cambios
    idempotent_no_progress: 5   # sin cambios
```

**Efecto:** Si un mismo comando de terminal falla con idénticos argumentos 2 veces → warning al LLM. Si falla 3 veces → hard stop (el agente debe cambiar de estrategia o detenerse).

#### Cleanup de procesos
- `ProcessRegistry.kill_process()` usa SIGTERM → si no responde, `process.kill()` (efectivamente SIGKILL en Unix)
- Background thread limpia environments inactivos cada 60s (ventana de inactividad: 300s)
- **Para el incidente:** 5 ejecuciones en 3 min no habrían activado el cleanup (ventana de 5 min). Pero el guardrail con `exact_failure_warn_after: 2` habría alertado al LLM tras el 2º fallo, previniendo las ejecuciones 3-5.

#### Nota: requiere nueva sesión
Los cambios en `tool_loop_guardrails` requieren `/reset` (nueva sesión) para aplicarse porque la config se carga al inicio de cada sesión.

---

## FASE-D: Documentación y reglas

|| # | Tarea | Estado | Criterio PASS |
||---|-------|--------|---------------|
|| D-1 | Agregar sección "Encoding en scripts Python" a `docs/CONTRIBUTING.md` | ✅ | Sección con: (a) por qué UTF-8, (b) patrón `reconfigure()` como estándar, (c) `TextIOWrapper` como fallback, (d) cómo verificar en Windows |
|| D-2 | Agregar regla a `docs/contributing/documentation_rules.md` — gate de validación encoding | ✅ | Regla: "Todo script CLI con `print()` debe tener fix de encoding (`reconfigure` o `TextIOWrapper`) o usar ASCII-only" |
|| D-3 | Actualizar `AGENTS.md` §Vinculo-con-la-Documentacion si es necesario | ✅ | No requiere cambios. AGENTS.md ya referencia ambos archivos modificados (L67-69). Cross-reference consistente. |
|| D-4 | Verificar que no hay CRLF introducidos en archivos editados | ✅ | `git diff --check` exit 0. Sin errores de whitespace. Warnings CRLF preexistentes (Windows core.autocrlf). |

---

## FASE-RELEASE: Docs cascade (si se modificó CONTRIBUTING o documentation_rules)

| # | Tarea | Estado | Criterio PASS |
|---|-------|--------|---------------|
| REL-1 | Ejecutar `scripts/log_phase_completion.py` para fases B, C, D | ✅ | REGISTRY.md actualizado con FASE-B, FASE-C, FASE-D |
| REL-2 | Ejecutar `scripts/sync_versions.py` | ✅ | 7 archivos sincronizados a v4.46.1 (README, AGENTS, .cursorrules, CONTRIBUTING, GUIA_TECNICA, REGISTRY) |
| REL-3 | Actualizar `CHANGELOG.md` con formato CONTRIBUTING.md | ✅ | Secciones: Objetivo, Cambios, Archivos Modificados, Tests |
| REL-4 | Actualizar `docs/GUIA_TECNICA.md` con nota técnica | ✅ | Nota técnica v4.46.1: prevención de memory leak por encoding, patrón estándar |
| REL-5 | Ejecutar `scripts/run_all_validations.py --quick` | ✅ | 5/5 validations passed sin regresiones |

---

*Checklist corregido 2026-05-14 contra código vivo. No modificar filas ya completadas.*
