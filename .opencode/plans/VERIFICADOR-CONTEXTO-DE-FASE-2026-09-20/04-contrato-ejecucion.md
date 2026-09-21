# Contrato de ejecución — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

Cada prompt es ejecutable en una sesión nueva leyendo este contrato, el maestro y las filas
pertinentes de `00-lecciones-capitalizadas.md`. Este archivo **no reemplaza**
`.agents/workflows/phased_project_executor.md`; concreta su aplicación a este plan.

## Permisos de la sesión

| Acción | ¿Autorizada? | Base |
|---|---|---|
| Escribir en `scripts/` (cuatro archivos nuevos) y `tests/` | **Sí** | Alcance §3 del maestro |
| Escribir en `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/` | **Sí, solo FASE-D y solo como generado** | AC19; el directorio vive dentro del plan, no en `.agents/workflows/` |
| Leer `.agents/`, `output/`, `evidence/` de otros planes, `Archives/` | **Sí, lectura** | Necesaria para AC13, AC19 y para el denominador |
| Modificar cualquier archivo bajo `.agents/` | **No** | AC17. Configuración central, y es la fuente que el verificador auditó y que FASE-D lee |
| Reescribir un prompt de fase de otro plan | **No** | FASE-D los parsea. Reescribirlos es lo que D2/D3 postergan |
| Modificar `scripts/run_all_validations.py` o `scripts/git_hooks/pre-commit` | **No** (este plan los lee como fuente de verdad) | AC16: alteraría el conteo que otros planes publican —los 11 checks del quick están pineados en cuatro documentos de `REFACTOR-WHATSAPP` (arranque de FASE-B en su `README.md`, `06-`, `09-`, `10-`), no en su prompt de FASE—. **Y no es un archivo libre**: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` lo declara dentro de su alcance, así que este plan no lo escribe pero **sí** debe re-leer su etiqueta `[15/15]` y la invocación del write-back en el cierre (deuda **D10**) |
| Ejecutar `v4complete`, `v4audit`, la pipeline o cualquier API de pago | **No** | §5 del maestro. Este plan no tiene corrida ni llamadas de red |
| **Llamadas reales a un proveedor de decisiones** | **No, en ninguna fase** | Decisión del operador del 2026-09-20: Jev no entra. AC9 certifica la **costura**, no al proveedor; activarlo es deuda **D7** |
| `git commit` / `git push` | **No implícito** | Cada fase deja el checkpoint; el commit requiere instrucción literal |
| Write-back a QMind | **No en fases de implementación** | Orden R2.5/R2.10, solo en RELEASE y antes del `git mv` |

**Regla de cero red.** FASE-B y FASE-C se prueban contra proveedores **falsos**. Si una sesión
necesita llamar a un servicio real para avanzar, para y deja checkpoint: la llamada no se autoriza
por conveniencia. Consecuencia aceptada y escrita en el maestro: ningún AC de este plan mide calidad
de decisiones de un modelo real.

## Dónde se escribe la evidencia (corregido en la auditoría del 2026-09-20)

Toda la evidencia de este plan va a **`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-X/`**.
La primera versión del plan escribía en `evidence/FASE-A/` … `evidence/FASE-D/` a secas, y eso **no
estaba libre**: esas cuatro rutas raíz existen desde `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` y guardan
su evidencia con exactamente los nombres que produciría este plan (`faseA_baseline_pre.txt`,
`faseA_baseline_post.txt`, `faseB_baseline.txt`, …). Escribir ahí mezclará procedencia de dos planes y
podrá **sobrescribir evidencia de un plan archivado sin que salte ninguna validación** (`validate_opencode_refs.py`
solo mira rutas bajo `.opencode/`, y `evidence/` no entra). El convenio vigente es el subdirectorio por
plan, que ya usa `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`.

**Dos excepciones declaradas, no olvidos**: (i) `evidence/FASE-D/measure_iterations.py` se cita **como
ruta legado de lectura** porque es el instrumento canónico que publica el executor; (ii) la plantilla
`.agents/workflows/templates/prompt-fase-template.md` sigue prescribiendo `evidence/fase-{N}/` en la
raíz — este plan **no** puede corregirla (AC17 prohíbe escribir en `.agents/`), así que la discrepancia
queda aquí escrita y viaja con **D1** cuando el operador decida sobre los documentos de gobierno.

## Corte de presupuesto (R2.1)

Instrumento canónico: `evidence/FASE-D/measure_iterations.py` (ruta legado, ver arriba), corte **hasta
el commit de código**.
Este plan declara presupuesto y **declara además si el instrumento corrió**. Si no corre bajo la
política de permisos de la sesión, el auto-reporte se publica en la unidad usada (`tool_use`,
`ids únicos`) y se declara que **no es comparable** con las demás. Prohibido reportar cumplimiento
estimado o mezclar unidades. Sin instrumento, la métrica se retira y se declara fuera de servicio,
no se estima. **Precondición medida el 2026-09-20**: `find . -name "*.jsonl"` devuelve **0** dentro del
workspace — es la misma condición que documentó `D-V2.1` (`PASO0-…`/`TRIBUNAL-ENFORCEMENT-OBS`,
reproducida en cuatro fases seguidas), así que esta sesión **espera** caer en el auto-reporte con unidad
declarada y lo declara, en lugar de prometer una medición que no puede hacer.

## Cierres incrementales obligatorios por fase

1. **Par pre/post del conteo de checks** en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-X/`
   (`*_baseline_pre.txt`,
   `*_baseline_post.txt`) y `baseline-pre-post.md` con la **resta** comprobada. Delta esperado: **0**
   en las cuatro fases de implementación (AC5, AC16). FASE-D añade además su propio par de **carga de
   lectura** (AC20), que sí espera un delta distinto de cero y que se reporta aunque sea cero.
2. **Selección de tests de la fase** ejecutada, publicada con su resultado, y los rojos preexistentes
   ajenos a la fase declarados como tales con dueño y causa, sin arrastrarlos ni maquillarlos.
3. `run_all_validations.py --quick` en verde, **sin** que la fase haya tocado su composición.
4. **Registro de la fase por sí misma**: `scripts/log_phase_completion.py` al terminar. FASE-RELEASE
   **no** registra fases ajenas.
5. `build_lesson_index.py` regenerado **en el mismo commit** que escribe cualquier `.md` bajo `plans/`
   que nombre un ID (R2.10; lo corta `[6/7]` del hook). Aplica a las cuatro fases: FASE-D también
   escribe `.md` de plan.
6. Actualización de `00-lecciones-capitalizadas.md` §2 (lo que **realmente** pasó), §4 (cobertura al
   estado real), `06-checklist-implementacion.md`, `dependencias-fases.md` y `README.md` del plan.
7. **FASE-D únicamente**: `build_phase_briefing.py --check` en verde contra el árbol final, y ningún
   pack emitido con `SECCION-NO-RESUELTA` sin decirlo (AC22).

## Reglas sobre el pack generado (FASE-D)

- El pack es **derivado, no autoritativo**. Ninguna lectura canónica desaparece: lo que el pack no
  incluye se declara en `no_incluye[]` y en `lectura_aparte_obligatoria[]`, donde figura el workflow
  canónico porque este plan **no** lo rebaná (D3).
- Un pack no puede achicarse en silencio: sección pedida y no resuelta es un estado propio con la
  ruta intentada (AC22, L-PF6, L-PF10).
- Lleva `provenance` con HEAD, fecha y sha por fuente, y `--check` lo vence contra el árbol (AC21).
  Un pack vencido se regenera; no se edita a mano.

## Reglas de forma aplicadas a los artefactos de este plan

- **Símbolos, nunca `archivo:número`** en ACs, prompts y evidencia (R2.2). Antes de citar una región,
  confirmarla con `grep`/lectura; si difiere, corregir la cita y avisar.
- **Conteos como delta** con par de archivos, no números absolutos (R2.3, R2.7).
- **Todo AC de detección se cierra con mutation check** sobre el símbolo real del guard, con las dos
  salidas en evidencia (R2.8). Verde a la primera = sospechoso y explicado.
- **Todo lector expresa tres estados** y los publica (R2.9): `sin hallazgos` / `ausente` /
  `lector fallido`. Prohibido el `except` que devuelve el valor por defecto de «no encontrado».
- **AC no legible en el artefacto = ⚠️, nunca ✅** (R2.4). Prueba práctica: si el AC no responde
  *«¿dónde lo vería un humano que solo tiene el artefacto?»*, no está listo.
- El **reporte no reescribe**: ningún script de este plan edita `.agents/` ni los planes ajenos.
- Toda cifra copiada de una fuente dinámica se publica **con su comando y su fecha**, y se re-mide al
  cerrar la fase (medición A6 del maestro: las cifras de este plan vencieron al crearse el plan).

## Orden del cierre (R2.5 / R2.10, no permutable)

**Paso 0 (D10, añadido en la auditoría del 2026-09-20):** antes de correr el bloque, verificar la
interfaz del writer contra el árbol vigente — `./venv/Scripts/python.exe scripts/validate_qmind_writeback.py --help`
— porque `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` puede haber añadido `--title`/`--file` o quitado la
degradación a PASS. Si cambió, se re-escribe este bloque **con su nota datada** antes de ejecutarlo.

```bash
./venv/Scripts/python.exe scripts/validate_qmind_writeback.py --upload VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20
./venv/Scripts/python.exe scripts/build_lesson_index.py
git mv .opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 .opencode/plans/Archives/
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/validate_opencode_refs.py --fix
./venv/Scripts/python.exe scripts/validate_plan_citations.py --update-baseline
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

*(Forma unificada el 2026-09-20: los prompts de fase ya usaban el intérprete del `venv`; este bloque
canónico decía `python`, que bajo Git Bash resuelve al intérprete sin dependencias del proyecto. El
orden y sus argumentos no cambian.)*

## FASE-VERIFY: no aplica, con la razón medida

§4.6 exige **los tres** criterios de activación. Se cumplen «≥3 fases de implementación» (ahora
cuatro: A, B, C, D) y «ACs que cruzan múltiples fases» (AC15, AC16 y AC17 cruzan fases). **No** se
cumple «existe al menos una fase con ejecución E2E (`v4complete`, `v4audit`, etc.)»: este plan tiene
prohibida la pipeline y prohibida la red. Criterio 2 cae → **3 etapas**, sin sesión de certificación.

Consecuencia declarada: ningún AC de este plan puede llegar a `SUPERADO EN E2E`. Su techo es
`VERIFICADO OFFLINE` con su mutation check, o `NO-EJERCITADO` cuando algo no se ejercitó — y
`NO-EJERCITADO` **no** es una salida disponible para AC9, porque AC9 ya no pide medir una
comparación.
