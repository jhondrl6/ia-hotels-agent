# FASE-G — Premisas re-medidas antes de la primera edición

**Sesión:** G (implementación) · **Fecha:** 2026-09-20
**HEAD al abrir:** `d7ff932` · rama `master` · árbol limpio · `git rev-list --left-right --count origin/master...HEAD` = **0 / 0**

Ningún número de esta sesión se heredó del contexto: cada fila se midió con comando sobre el
árbol o sobre el archivo heredado de FASE-A.

## 1. Estado heredado y delta real desde el cierre de A

| Premisa | Cómo se re-midió | Resultado |
|---|---|---|
| HEAD y paridad con origin | `git rev-parse HEAD`, `git status --short`, `git rev-list --left-right --count origin/master...HEAD` | `d7ff932`, árbol limpio, **0/0**. Coincide con el estado anunciado por A |
| «A cerró y publicó» sin tocar código de producto | `git log --oneline d4dacb4..HEAD` y `git diff --stat d4dacb4..HEAD` | 4 commits (`3e97d95`, `60b0b7a`, `f015ed7`, `d7ff932`), 20 archivos: **todos** docs del plan, índice de lecciones, CHANGELOG, REGISTRY, GUIA_TECNICA, `VERSION.yaml` y evidencia. **Cero `.py` de producto** → las mediciones por símbolo de A siguen vigentes (se comprobó de todas formas en §2) |
| Quick 10/10 al abrir | `./venv/Scripts/python.exe scripts/run_all_validations.py --quick` | **10/10, exit 0**, a las 08:54 del 2026-09-20. No hubo que leer `_check_version_sync` porque no había rojo que atribuir: A ancló `date: "2026-09-19"` en `VERSION.yaml` (`d7ff932`) y el check dejó de depender del reloj. **La advertencia del mandato sobre el reloj quedó sin efecto medido, no supuesta** |
| Baseline de A preservado | Lectura de `FASE-A/baseline_inventory.json` y `decisiones.md` (sin modificar) | Leídos. **A no registró la selección literal de su corrida de 133 tests** (el `txt` empieza a mitad de la salida y el JSON guarda el recuento pero no los caminos). G deja la suya escrita literal en `tests_baseline_pre.txt`, porque la lección aplica: un baseline sin selección no es re-medible |

## 2. Comparación por símbolo de lo que A midió (mandato explícito de esta sesión)

| Símbolo | Medición heredada de A | Re-medición de G | Veredicto |
|---|---|---|---|
| `LLMMentionChecker._sanitize_text` | P10: enmascara **solo** las 3 keys de `__init__`, por igualdad literal | `llm_mention_checker.py`: `for key_value in (self._gemini_key, self._openrouter_key, self._perplexity_key)` en el cuerpo de `_sanitize_text`; las tres keys se asignan en `__init__` (líneas 118-120) | **Confirmada sin delta.** Sigue siendo F, no G |
| `ValidationRunner._check_no_secrets` | P10: recorre `git ls-files` + staged | `_git_tracked_files` hace `git ls-files -z` y `git diff --cached --name-only -z --diff-filter=ACM`; el escaneo los consume en dos sitios | **Confirmada.** `output/` y `logs/` siguen fuera por `.gitignore`, no por el código |
| Writer P6-R (`asset_zip_paths`) | P11: derivado de los `dest` reales y consumido por la plantilla | `delivery_packager.py` deriva el mapping de `["dest"]` y se lo pasa al contrato; `asset_responsibility_contract.py` lo consume en dos ramas con fallback al propio filename | **Confirmada.** E sigue sin motivo para reconstruir el writer |
| `CrossValidator._reconcile_whatsapp_multisede` | Decisión 11 de A: existe, con suite propia | `cross_validator.py` lo define y se auto-invoca en el flujo; `tests/data_validation/test_whatsapp_multisede.py` existe | **Confirmada.** G **no** lo reimplementó, **no** lo eludió y **no** lo tocó |

## 3. La premisa que el plan traía mal medida, y que G corrigió

| Premisa del plan | Lo que midió el AST de G |
|---|---|
| Fila F-A' del maestro §1: la divergencia es que `generate_assets` llama a `detect_pains` sin `whatsapp_html_detected` (una invocación) | **Son tres invocaciones del mismo archivo**: `v4_asset_orchestrator.py:286` (`detect_pains`), `:309` y `:447` (dos llamadas a `CoherenceValidator.validate`, pre-gen y post-gen), que omiten la misma señal por el mismo mecanismo (default `False`) |

Consecuencia operativa registrada para FASE-B en `inventario-callers.md` §1.2: corregir solo la
286 deja dos rojos y convierte sus excepciones en `EXCEPCION_VAGA`. Es exactamente el caso que
AC7 fue a buscar, y es la primera observación medida de la fase.

## 4. R2 — presupuesto, instrumento y corte

| Concepto | Estado |
|---|---|
| Instrumento | `evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>` |
| Transcript de esta sesión | **No disponible** para el instrumento (no hay ruta a un transcript que esta sesión pueda leer; el precedente está registrado en `project-medicion-de-iteraciones-fuera-del-workspace.md`) |
| Declaración | **Métrica FUERA DE SERVICIO (R2.1 / D-V2.1)** desde el primer momento, conforme al mandato: no se intentó evadir la denegación |
| Auto-reporte con unidad propia | Unidad = **intervenciones sobre el árbol y corridas medibles en disco**, no `tool_use` (contar tool_use exige el transcript; sin él cualquier cifra sería inventada). Medido con `git status --porcelain` y `git diff --stat`: **9 rutas tocadas** — 5 archivos modificados (+125 / −21 líneas) y 4 de nueva creación (`scripts/validate_wiring.py` 905 líneas, `tests/test_validate_wiring.py` 464, `.opencode/wiring_report.json`, el directorio de evidencia) — sobre **2 corridas pytest de baseline** (PRE, POST-A), **2 corridas POST-B** (la primera con el suite aun incompleto y su re-medición con las 18 funciones), **7 mutaciones de guard** con restauración verificada por sha256, **1 quick de apertura** y **3 quicks de cierre** (uno de ellos rojo por Version Sync, con causa medida en §5bis de `resultados-y-observaciones.md`). Corte = última edición de código antes de las validaciones de cierre || Comparación con la referencia de 60 tool_use | **No procede**: la referencia está expresada en una unidad que sin transcript no es medible. Declarar aquí «78 tool_use» sería exactamente lo que R2.1 prohíbe |
| Duración de pared (se registra aparte) | PRE 20,6 s · POST-A 14,5 s · POST-B 57,5 s · suite nuevo 45,8 s · cada corrida del verificador ~10,8 s · batería de mutaciones ~3 min |
| Corte documental posterior al código | Sí, separado: el cierre documental (docs de plan + CHANGELOG + REGISTRY + DOMAIN_PRIMER) se midió aparte del corte de código, como exige R2.1 |

**Nunca se estimó cumplimiento del presupuesto: se retiró la métrica por no ser
medible y se declaró en su lugar una unidad contable, sin compararla con la referencia.**

## 5. Contador v4complete

**0 / 1.** Esta fase no lanzó `main.py v4complete`, no ejecutó red ni scraping, y ninguna
lectura de artefactos ajenos consumió el intento. La evidencia leída de
`output/TAREA7-2026-09-19/` no se tocó.
