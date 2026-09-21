# FASE-RELEASE — Cierre documental, write-back y archivado

**ID**: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 / FASE-RELEASE
**Objetivo**: sincronizar versiones, publicar CHANGELOG y `GUIA_TECNICA`, cerrar `REGISTRY.md` con los
**cuatro** módulos nuevos, re-evaluar la deuda D1–D10 con los números que dejó la ejecución, y archivar
el plan en el orden fijo de R2.5/R2.10.
**Dependencias**: FASE-A, FASE-B, FASE-C y FASE-D ✅. Si alguna quedó con un AC en ⚠️ o
`NO-EJERCITADO`, **ese estado viaja al cierre**: no se promociona a ✅ en RELEASE.
**Duración / scope**: 1 sesión; **4 tareas** documentales + **0** comandos de larga duración.
**Regla**: RELEASE **NO modifica código fuente** y **NO** registra fases ajenas.

## Contexto

Entran al repo cuatro scripts nuevos y un directorio de artefactos generados (`briefing/` dentro de
este plan). El índice de lecciones gana las lecciones de este plan para que el Paso 0 del siguiente las
consulte. El único momento en que el write-back a QMind funciona es con el plan todavía en `plans/`
raíz (R2.10), y la segunda regeneración del índice es obligatoria porque el `git mv` cambia rutas que el
índice publica con su dueño.

### Estado de fases anteriores (a confirmar en disco al abrir la sesión)

| Fase | Estado esperado | Qué trae |
|---|---|---|
| FASE-A | ✅ | `validate_governance_numbers.py`, AC1–AC5, informe con `coverage_basis` |
| FASE-B | ✅ | `decision_client.py`, contract test de forma, `files_changed_to_add_provider` |
| FASE-C | ✅ con AC15 en ⚠️ si no hubo proveedor | `triage_lesson_relevance.py`, AC10–AC14, y `acceptance = NO-EJERCITADO` |
| FASE-D | ✅ | `build_phase_briefing.py`, los packs, y `carga.json` con el delta **medido** |

## Tareas

### Tarea 1: Verificar la capa tibia (ya consultada en la auditoría del 2026-09-20)

La consulta Q7 de `00-lecciones-capitalizadas.md` **ya no está pendiente como descubrimiento**: se
ejecutó en la auditoría de la concepción el 2026-09-20 con el CLI disponible y autenticado, y sus
resultados están capitalizados en §2 (L-V2.1, L-V2.2, D-V2.1). Quedan dos cosas por hacer aquí:

1. **Re-correr solo si el notebook cambió** desde esa fecha (nuevas fuentes ingeridas por otros
   planes), y publicar el resultado con la forma **correcta** del comando: `--nb` exige el ID
   `01a04d98-b7bd-778c-8441-26fdc7e35f45` — la forma con el nombre (`--nb iah-cli-lecciones`), que es
   la que publica el workflow canónico, devuelve `error: Bad request` (medido el 2026-09-20).
2. **Re-leer la interfaz del write-back antes del orden de cierre (deuda D10)**:
   `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` declara dentro de su alcance
   `scripts/validate_qmind_writeback.py` y su conexión en `scripts/run_all_validations.py`. Correr
   `validate_qmind_writeback.py --help` contra el árbol vigente y **re-escribir el bloque de cierre de
   este prompt si la firma cambió** (`--title`/`--file`, o el fin de la degradación a PASS). Si sigue
   igual, se publica esa verificación con su fecha. Criterio: **AC18** (y **AC16**: que la composición
   del `--quick` siga en 11 pese a cualquier cambio del hermano).

### Tarea 2: Sincronizar versiones y publicar documentación

`sync_versions` → CHANGELOG → `GUIA_TECNICA` → `docs/contributing/REGISTRY.md` (los cuatro módulos y
su check), y las Secciones A/B/D/E de `09-documentacion-post-proyecto.md`. Verificar con
`version_consistency_checker.py` y `sync_versions.py --check`, que son `[1/7]` y `[2/7]` del hook: si el
sync queda pendiente, el propio commit no pasa.

### Tarea 3: Cerrar la deuda con números, no con opinión

Presentar **sin ejecutar** las decisiones que este plan abrió. Cada una sale con su coste medido y su
dueño nombrado:

- **D1** — las aserciones A1–A4 de `.agents/`: ¿corregirlas a mano, o eliminar la aserción del documento
  y dejar que el verificador la imprima en su salida? La segunda es la que no se desfasa. `.agents/` es
  configuración central: necesita instrucción literal del operador.
- **D2 / D3** — promover el verificador al `--quick` (renumerando 11 → 12) y rebanar el workflow
  canónico: **ambas siguen debidas**, con el disparador que ya está escrito. No se reinterpretan aquí.
- **D6** — el lint de contradicciones semánticas: **solo puede activarse si AC15 publicó una
  aceptabilidad real**. Con `acceptance = NO-EJERCITADO`, D6 queda **dormida** y se registra así, con la
  causa. Un lint de pertinencia sobre una base que nunca juzgó nada es deuda apilada sobre humo.
- **D7** — activar el proveedor: confirmar que la costura quedó probada (`files_changed_to_add_provider`)
  y que el coste de entrada es **un archivo**. No activarlo en el cierre.
- **D4 / D5** — siguen con dueño en `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`; no se reasignan.

### Tarea 4: Cierre en orden y verificación final

```bash
./venv/Scripts/python.exe scripts/validate_qmind_writeback.py --upload VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20
./venv/Scripts/python.exe scripts/build_lesson_index.py
git mv .opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 .opencode/plans/Archives/
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/validate_opencode_refs.py --fix
./venv/Scripts/python.exe scripts/validate_plan_citations.py --update-baseline
./venv/Scripts/python.exe scripts/build_phase_briefing.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 --check
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Tests y validaciones obligatorias

| Verificación | Criterio de éxito |
|---|---|
| `validate_lesson_capitalization.py` | C1–C8 verdes sobre el `00-…` final, tras la consulta Q7 |
| `validate_governance_numbers.py` (el de FASE-A) | Verde sobre el árbol final, con su denominador |
| `build_phase_briefing.py --check` (el de FASE-D) | Verde contra el árbol **después** del archivado |
| `validate_plan_closure.py` (`[5/7]` del hook) | Sin filas pendientes en `10-analisis-post-implementacion.md` |
| `build_lesson_index.py --check` (`[6/7]`) | Índice reflejando el árbol después del `git mv` |
| `run_all_validations.py --quick` | 11 checks verdes, composición intacta (AC16) |

## Post-ejecución (OBLIGATORIO)

1. `dependencias-fases.md` — FASE-RELEASE ✅ y la tabla de deuda **D1–D10** con su estado real tras la
   Tarea 3 (D6 dormida o activada, con la cifra que lo decide).
2. `README.md` — estado final, ruta nueva en `Archives/`, ACs con el nivel alcanzado.
3. `06-checklist-implementacion.md` — casillas de cierre.
4. `10-analisis-post-implementacion.md` — matriz final, métricas reales (incluida la carga de lectura
   antes/después), límites y seguimientos S1–S7.
5. `00-lecciones-capitalizadas.md` — §4 al estado del cierre y Q7 resuelta o limitación re-fechada.
6. `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-RELEASE/` — salidas de las validaciones de la tabla anterior.

RELEASE **no** invoca `log_phase_completion.py` sobre fases ajenas: solo sincroniza y valida.

## Criterios de completitud

- [ ] Write-back ejecutado **con el plan aún en raíz** (es el único paso que deja de funcionar tarde).
- [ ] Índice regenerado **dos** veces, con la segunda después del `git mv`.
- [ ] `--check` del pack verde contra el árbol final, no contra el de mitad de cierre.
- [ ] Ningún AC promocionado a ✅ sin su mutation check o su clave en el artefacto (R2.4).
- [ ] `--quick` verde y con 11 checks (AC16); `validate_governance_numbers.py` verde.
- [ ] D1 y D2/D3 con decisión escrita o dueño y disparador vigentes; **D6 con su causa declarada**.
- [ ] Delta de carga de lectura publicado **aunque sea cero** (AC20), con su comando.
- [ ] CHANGELOG, `GUIA_TECNICA` y `REGISTRY.md` sync; `[1/7]` y `[2/7]` en verde.
- [ ] Plan archivado y las referencias vivas apuntando a la ruta nueva.

## Restricciones

- No modifica código fuente. No abre ni cierra deuda de `REFACTOR-WHATSAPP`. No ejecuta la pipeline.
- **No activa el proveedor de decisiones** (D7) ni hace una sola llamada de red en el cierre.
- No toca `.agents/**` salvo instrucción literal del operador resultante de la Tarea 3.
- No commitea ni empuja sin instrucción literal; un único commit cierra RELEASE + archivado (R2.5).

## Prompt de ejecución

```text
Ejecuta unicamente FASE-RELEASE del plan
C:/Users/Jhond/Github/iah-cli/.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/.
Lee 05-prompt-inicio-sesion-fase-RELEASE.md, 01-plan-maestro.md §4 y §6, 04-contrato-ejecucion.md
(orden del cierre y regla de cero red), 00-lecciones-capitalizadas.md completo,
06-checklist-implementacion.md, dependencias-fases.md, 10-analisis-post-implementacion.md,
los cuatro prompts de fase, docs/CONTRIBUTING.md y el workflow canonical (FASE-RELEASE).
Primero re-mide en disco el estado real de A, B, C y D: un AC en ⚠️ o NO-EJERCITADO viaja al cierre con
ese estado, no se promociona.
Tarea 1: ejecuta la consulta Q7 de QMind que la concepcion no pudo correr; si sigue inaccesible,
re-fecha la limitacion en §4 y en dependencias, no la borres.
Tarea 3: cierra la deuda con numeros. D1 (aserciones A1-A4 de .agents/) se presenta con coste y no se
ejecuta sin instruccion literal. D2/D3 siguen debidas con su disparador. D6 queda DORMIDA si AC15 no
publico una aceptabilidad real: escribelo con la causa. D7 se confirma con files_changed_to_add_provider
y no se activa aqui.
Tarea 4: cierra en el orden write-back -> indice -> git mv -> indice -> refs -> citas -> check del pack
-> quick. Publica el delta de carga de lectura aunque sea cero.
No modifiques codigo fuente, no registres fases ajenas, no ejecutes la pipeline, no hagas llamadas de
red, no commitees ni empujes sin instruccion literal.
```
