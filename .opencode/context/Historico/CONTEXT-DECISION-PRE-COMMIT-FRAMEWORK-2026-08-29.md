# CONTEXT — Decisión: migrar al framework pre-commit (Opción 2) vs mantener hook custom (Opción 1+)

> **Fecha**: 2026-08-29
> **Tipo**: Contexto de decisión (evaluación, no implementación)
> **Estado del repo al escribir**: v4.73.0, commit `23dfe27` (hook custom versionado activo)
> **Decisión pendiente**: activar el stack completo de `.pre-commit-config.yaml` (framework pre-commit 4.3.0, hoy instalado pero desconectado de `.git/hooks`) o evolucionar el hook custom actual.

---

## Decisiones registradas (usuario, 2026-08-29)

1. **Triaje de los 12 tests fallando (§4.2): DIFERIDO a la siguiente fase.** Se aplaza
   explícitamente la investigación de causa raíz de los 12 fallos de la selección pytest-v4.
   Es el prerequisito R1 — ninguna activación del framework puede ocurrir antes de resolverlo.
2. **Mientras tanto, la Opción 1 queda vigente**: hook custom versionado (`scripts/git_hooks/`)
   como único gate activo en cada commit.
3. La migración al framework (2a/2b) se tomará cuando se cumpla alguno de los disparadores
   del §10; no se hará como cambio incidental.

**Primera acción de la siguiente fase**: triaje de los 12 fallos (3 en
`test_calculator_v2.py`, 8 en `test_pricing_resolution_wrapper.py`, 1 en
`test_site_verification_propagation.py`) — ver §4.2 y §11 pregunta 2.

---

## 1. Propósito

Este documento reúne los elementos necesarios para decidir si el repo adopta el framework
pre-commit como gate de cada commit (formato, lint, tests, higiene, validaciones), o mantiene
y extiende el hook custom actual. Incluye implicaciones, requisitos, ventajas, desventajas,
el comportamiento esperado de los commits frecuentes y los **bloqueantes reales medidos hoy**.

---

## 2. Línea base (situación actual, 2026-08-29)

| Elemento | Estado |
|---|---|
| Hook activo en `.git/hooks/pre-commit` | Custom, versionado en `scripts/git_hooks/pre-commit`, instalado vía `scripts/install_git_hooks.py` |
| Checks activos por commit | [1/3] version consistency, [2/3] sync check, [3/3] referencias `.opencode` con auto-fix |
| Costo medido por commit | ~2-4 s |
| Framework pre-commit | Instalado (v4.3.0) pero **desconectado**: `pre-commit install` fue reemplazado en algún momento por el hook custom (existe `pre-commit.legacy`) |
| `.pre-commit-config.yaml` | Declarado completo (13 hooks) pero sin enforcement real |
| Flujo de commits | Directos a `master`, frecuentes (cierre de fase, evidencias, docs); ejecutados por humanos y agentes |
| post-commit | Pertenece al tracker de Qoder — no debe tocarse |

Bug corregido en esta sesión: el hook previo elegía `python3` de Git Bash (sin dependencias del
proyecto) y sus checks pasaban en silencio por un bug del pipe (`$?` capturaba el estado de
`head`, no del script). El enforcement de versión nunca estuvo realmente activo hasta hoy.

---

## 3. Inventario del stack declarado (`.pre-commit-config.yaml`)

| # | Hook | Qué hace | Impacto al activar |
|---|---|---|---|
| 1 | black 26.3.1 | Formatea .py a línea 100 | Modifica archivos; primer commit falla con "files modified" |
| 2 | ruff v0.15.7 (--fix) | Lint + auto-fix | Igual que black |
| 3 | trailing-whitespace | Quita espacios finales | Modifica archivos legacy al tocarlos |
| 4 | end-of-file-fixer | Nueva línea final | Idem (repo con CRLF abundante) |
| 5 | check-yaml / check-json | Sintaxis | Bajo |
| 6 | check-added-large-files (500KB) | Bloquea archivos grandes | Riesgo con artefactos de `evidence/` |
| 7 | check-case-conflict / check-merge-conflict / detect-private-key | Higiene | Bajo, alto valor (secrets) |
| 8 | **no-commit-to-branch (main, master)** | Bloquea commits a esas ramas | **BLOQUEANTE con el flujo actual** |
| 9 | pytest-v4 | 4 suites core (1,276 tests) | **12 tests fallando hoy** (ver §4.2) |
| 10 | structure-guard | Archivos residuales | Bajo |
| 11 | validate-plan | `run_all_validations.py --check` | ~3 s, ya verde |
| 12 | 4 import-smokes + check-v4-structure | Smoke de módulos | ~1-2 s |
| 13 | agent-ecosystem / version-sync / opencode-refs | Ecosistema agente, sync, refs auto-fix | Ya equivalen a checks activos |

---

## 4. Bloqueantes reales medidos hoy (evidencia 2026-08-29)

### 4.1 `no-commit-to-branch` vs flujo directo a master
Los commits recientes (incluidos los de esta sesión: `50c817c`, `33023cc`, `23dfe27`) son 100%
directos a `master`. Activar el framework sin tocar este hook bloquearía **todos** los commits.
Opciones: eliminar el hook, acotarlo, o migrar a flujo de ramas+PR (cambio de proceso mayor).

### 4.2 `pytest-v4` tiene 12 tests fallando AHORA
Medición directa (2026-08-29): `12 failed, 1263 passed, 1 skipped` en 8.7 s.

```
tests/financial_engine/test_calculator_v2.py            3 fallos (scenario order, recovery factor ROI)
tests/financial_engine/test_pricing_resolution_wrapper.py  8 fallos (modo activo/canary/edge/integración)
tests/asset_generation/test_site_verification_propagation.py 1 fallo (exists_with_issues_keeps_detected)
```

Con el framework activo, **cada commit sería bloqueado** por estos fallos hasta resolverlos.
Requiere triaje previo: ¿regresión real (posible relación con cambios de pricing $400K o SR-E/H2)
o tests desactualizados? Nota: la suite de regresión (26) y el quick de validaciones sí pasan;
el README afirma "0 regresiones", así que estos 12 merecen investigación propia con independencia
de la decisión del framework.

### 4.3 black no puede correr en este entorno hoy
`black --check` crashea con `UnicodeDecodeError` (byte 0xe1) al leer `.gitignore` — el archivo
tiene caracteres no UTF-8. Hasta corregir la codificación de `.gitignore`, el hook de black
fallaría en cada commit. Fix trivial (re-codificar el archivo), pero es prerequisito.

### 4.4 Costo por commit (medido, corrige estimaciones previas)
- Selección pytest-v4: **8.7-11.6 s** (1,276 tests).
- Validaciones + smokes + sync: ~3-5 s.
- **Total estimado por commit con framework: 20-40 s** (no "varios minutos" como se estimó
  antes de medir). Aceptable en commits de cierre de fase; fricción real en micro-commits
  iterativos (si se hicieran varios por sesión).

### 4.5 Ruido de normalización sobre código legacy
black/end-of-file-fixer/trailing-whitespace solo tocan archivos staged, pero el repo tiene
formato heredado (CRLF frecuente, líneas largas en módulos antiguos). Cada archivo legacy que
se toque recibirá un diff de limpieza mezclado con el cambio funcional. Alternativa: commit de
normalización masiva único (miles de líneas, alto ruido en `git blame`) o aceptarlo incremental.

### 4.6 Artefactos grandes
`check-added-large-files` (500KB) puede bloquear JSON/ZIP de `evidence/` u `output/`. Históricamente
se han commiteado evidencias; habría que verificar tamaños o ajustar el límite/exclusiones.

---

## 5. Requisitos para habilitar la Opción 2 (checklist ordenado)

| # | Requisito | Bloqueante | Esfuerzo |
|---|---|---|---|
| R1 | Triar y resolver los 12 tests fallando de la selección pytest-v4 — **diferido a la siguiente fase por decisión del usuario (2026-08-29)** | Sí | Medio (investigación de causa raíz) |
| R2 | Decidir política de ramas: quitar `no-commit-to-branch` o migrar a PRs | Sí | Decisión de proceso |
| R3 | Corregir codificación de `.gitignore` (UTF-8) | Sí (para black) | Trivial |
| R4 | Decidir política de formato legacy (incremental vs normalización masiva) | No | Decisión |
| R5 | Auditar tamaños de artefactos vs límite 500KB | No | Bajo |
| R6 | Migrar el chequeo [2/2] del hook custom (file synchronization) al framework o conservarlo | Sí | Bajo |
| R7 | `pre-commit install` + verificación end-to-end (incluye commits de agente) | Sí | Bajo |

---

## 6. Ventajas de la Opción 2

1. **Enforcement del stack completo**: formato, lint, tests core, higiene, secrets — no solo versión+referencias.
2. **Fuente única declarativa y versionada** (`.pre-commit-config.yaml`): cualquier clon obtiene el mismo gate con `pre-commit install`; el hook custom requiere instalador manual.
3. **Detección adelantada**: regresiones y problemas de formato en el commit, no al cierre de fase.
4. **Estándar portable**: `pre-commit.ci` ya configurado para CI; alineado con prácticas de la industria.
5. **detect-private-key + check-added-large-files**: protecciones que hoy no existen.

## 7. Desventajas y riesgos

1. **R1 sin resolver bloquea todo commit** — el framework amplifica cualquier deuda de tests.
2. **Cambio de proceso** (R2): perder commits directos a master o aceptarlos quitando el hook (en cuyo caso una protección declarada desaparece).
3. **20-40 s por commit**: fricción acumulada en sesiones con muchos commits; riesgo de hábito de `--no-verify` que anula todo el sistema.
4. **Ruido de diffs** por normalización de archivos legacy (blame, revisiones).
5. **Más piezas móviles**: entornos de hook por repo (black/ruff descargados), diagnósticos más complejos cuando algo falla.
6. **El post-commit de Qoder no se toca**, pero el pre-commit del framework reemplaza al custom actual — hay que conservar los 3 checks activos (ya declarados como hooks del framework: version-sync y opencode-refs; falta file-sync).

---

## 8. Comportamiento de los commits frecuentes: hoy vs futuro

| Aspecto | Hoy (Opción 1 activa) | Futuro con Opción 2 |
|---|---|---|
| Commit típico de cierre de fase | 2-4 s, verde | 20-40 s, verde si R1 resuelto |
| Commit con referencia .opencode rota | Auto-fix + re-stage (1 intento extra) | Igual (hook opencode-refs declarado) |
| Commit con test roto | **Pasa** (no se corren tests al commit) | **Bloqueado** |
| Commit con formato/lint sucio | Pasa | Bloqueado/auto-corregido + re-stage |
| Commits del agente (Qoder) | Transparente | Igual transparente + 20-40 s |
| Micro-commits iterativos | Sin fricción | Fricción (considerar `--no-verify` puntual o commits atómicos más grandes) |
| Commit directo a master | Permitido | Bloqueado salvo decisión R2 |

**Proyección**: con el ritmo actual (~1-3 commits por sesión de fase), el costo agregado es
despreciable (minutos/mes). El riesgo de fricción solo aparece si se adopta un estilo de
micro-commits frecuentes.

---

## 9. Alternativas de decisión

| Opción | Descripción | Cuándo elegirla |
|---|---|---|
| **1+ (status quo evolutivo)** | Mantener hook custom; añadir black/ruff/pytest al script cuando se necesiten | Si el flujo actual es suficiente y no hay presión de formato/calidad en commit |
| **2b (framework curado)** | Activar el framework **sin** `no-commit-to-branch` y con selección de hooks priorizada (tests, refs, hygiene, secrets; formato opcional) | Mejor relación valor/disrupción; camino intermedio recomendado si se decide migrar |
| **2a (framework completo)** | Todo lo declarado, incluida protección de ramas | Solo con migración a flujo de ramas/PR |

## 10. Criterios de recomendación (disparadores)

Activar la migración cuando se cumpla **alguno**:
- Se incorpora un segundo colaborador humano (consistencia de gate entre máquinas).
- Se introduce flujo de ramas/PR (R2 deja de ser bloqueo).
- Un bug de formato/lint/test llega a master que el gate habría atrapado.
- El triaje de R1 ya se hizo por otra razón (los 12 fallos resueltos).

**No activar** como cambio incidental dentro de otra fase: merece fase propia (estimación:
1 sesión para R1 + 1 sesión corta para R3-R7 si R2 está decidido).

## 11. Preguntas abiertas para el usuario

1. ¿Se mantiene el flujo de commits directos a master, o se planea migrar a ramas/PR? (define R2)
2. ¿Los 12 tests fallando deben investigarse ya (independiente del framework) o se toleran?
3. ¿Se acepta normalización de formato incremental (diffs mixtos) o se prefiere un commit de limpieza masiva?
4. ¿Hay micro-commits en el horizonte (varios por sesión) que harían sentir los 20-40 s?

## 12. Plan de migración propuesto (si se decide)

| Paso | Acción | Salida |
|---|---|---|
| T0 | Triaje de los 12 fallos pytest-v4 (causa raíz, no síntoma) | Suite verde o exclusión justificada |
| T1 | Fix `.gitignore` UTF-8 + auditoría de tamaños evidence/ | black operativo |
| T2 | Curar `.pre-commit-config.yaml` según decisión R2/R4 | Config final |
| T3 | Añadir hook de file-synchronization al framework (equivalencia del [2/3] custom) | Paridad funcional |
| T4 | `pre-commit install`, prueba E2E (commit limpio, commit con fix, commit bloqueado), actualización validation.md/README | Gate activo |
| T5 | Retirar `scripts/git_hooks/` o dejarlo como fallback documentado | Cierre |

## 13. Métricas a verificar antes/después

- `pytest tests/data_validation tests/financial_engine tests/orchestration_v4 tests/asset_generation` → 0 failed (hoy: 12).
- `black --check scripts/` sin crash de .gitignore.
- Tiempo wall-clock del hook completo < 60 s.
- Cero commits con `--no-verify` en las primeras 2 semanas post-activación.

---

## Fuentes

- `.pre-commit-config.yaml` (config declarada)
- `scripts/git_hooks/pre-commit`, `scripts/install_git_hooks.py` (estado activo, commit `23dfe27`)
- Medición pytest-v4 2026-08-29: 12 failed / 1263 passed / 8.7 s
- `.git/hooks/pre-commit.legacy` (evidencia del reemplazo histórico del framework)
- Crash de black sobre `.gitignore` reproducido el 2026-08-29 (UnicodeDecodeError byte 0xe1)
