# Acta — Cierre documental de la tanda de instrumentos (FASE-A)

**Plan**: `CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15`
**Fecha de cierre**: 2026-10-21 (sesión de ejecución, America/Bogota).
**Autorizaciones escritas del Operador en esta sesión**: (1) commit de los crudos con el mensaje propuesto; (2) commit aparte `docs(plan): FASE-A…` para este acta y la post-ejecución; (3) el trabajo ajeno del 2026-10-21 queda fuera de estos commits; (4) **sin push** — los commits quedan locales.

---

## §0. Re-medición del árbol (T0) — premisas vencidas del prompt

El prompt manda re-medir antes de fiar sus líneas. Medido el 2026-10-21:

1. **«El árbol trae 4 rutas sin commitear» — VENCIDA**: las cuatro rutas del registro `D-QW-1`/`D-QW-2` (`context/CONTEXT-DEUDAS-WRITER-QMIND-2026-10-15.md`, el crudo `14-deuda-writer-context-sin-registro.txt` y el par del índice) quedaron versionadas en `85ab952`. Lo que esta fase debía commitear eran **solo los crudos de `temp/`**.
2. **Trabajo ajeno concurrente**: el árbol traía además `context/CONTEXT-DEUDAS-PRODUCTO-VERIFICADAS-2026-10-21.md` (sin trackear) y el par del índice regenerado, de otra sesión del mismo día. El Operador decidió declararlos fuera de alcance; durante esta sesión, **esa otra sesión los versionó en su propio commit `53fe9ed`** (20:31, mientras el hook de este plan corría). Queda constancia porque la ventana transitoria volvió vencido el par y cortó un intento de commit (§2).
3. **«Población = 2 gobernados» — VENCIDA**: `26bd0f5` archivó `context/CONTEXT-JEV-COSTURA-V4COMPLETE-2026-10-10.md` a `Historico/` (movimiento `R100`, bytes intactos), y la población gobernada del árbol quedó en **1**. No se fuerza la cifra del prompt: se publica la medida (§3).

---

## §1. T1 — Los crudos persistidos (AC2)

Los 12 crudos de la sesión 2026-10-15 (la tanda `2e048e6` + `1f95e84`, escrita por la sesión anterior) se copiaron de `temp/` (gitignored) a `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-RELEASE/` con numeración desde `15-` (sin colisión con el `14-` ya versionado). **`temp/` queda intacto** (780 entradas, sin borrado: FASE-A no lo borra salvo orden del Operador).

**Decisiones declaradas** (el prompt pedía decidir y declarar, no mezclar): `16-indice-antes.txt` y `17-opencode-refs.txt` viajan **como crudos numerados** (`17-`/`18-`), no como cita del acta. `22-quick-plan-nuevo.txt` (el quick tras crear el plan sucesor, del mismo origen de sesión) **se copia además** como `23-` por decisión de esta fase: el inventario del prompt decía «mínimo» y el objetivo es que ningún crudo de la tanda se pierda con el scratch.

**Identidades de cada crudo** — `sha256` del **blob versionado** (el que Git guarda) y del disco (origen en `temp/`). La copia se verificó `origen == destino` **12/12 antes** de tocar `temp/`. Con `core.autocrlf=input`, 9 de 12 blobs quedan normalizados CRLF→LF y **difieren del disco**; los otros 3 son idénticos. Ambas identidades, sin contradicción:

| Ruta versionada (FASE-RELEASE/) | Origen en `temp/` | sha256 disco (= origen) | sha256 blob (Git) |
|---|---|---|---|
| `15-frescura-post-cura.txt` | `14-frescura-post-cura.txt` | `b448936a5040199de549f3d8ab4bc0bf3d44e6db2d5a5ee10273196cc289153c` | `8eb4f906062a4177b8bafb0694ec5d008abbe772f637fea15e28771ce0aa8d3b` |
| `16-frescura-segunda-corrida.txt` | `15-frescura-segunda-corrida.txt` | `70cfba018061607e1123130e0f313b5bcfdbcf85583892681b760b9370b5a460` | `f7f91da0ceaadaf2f242fb10b13a69fa67af7486674a02b84eaf7c38b00e1158` |
| `17-indice-antes.txt` | `16-indice-antes.txt` | `b6d09b056447a2add64eca5d691ed71675252956a9059d1871135748e68659cc` | `b6d09b056447a2add64eca5d691ed71675252956a9059d1871135748e68659cc` (igual) |
| `18-opencode-refs.txt` | `17-opencode-refs.txt` | `3ca52fafb25c2c6196ced54d1e7aa3d75fa81f4df670866f14af2959708a4c52` | `64aa3defca9cb32d77f2514a16167f0679ad4319a4d04a5172cb8da0b381550a` |
| `19-quick-post-cura.txt` | `18-quick-post-cura.txt` | `7555686c8c96de19f9996b51b87e9bd67cb2528a009dca01fb8ae63d8fccd718` | `c075ca5b931ef51e43fd3353e652e415efa920f8aa914237d3935153e63a38de` |
| `20-writeback-post-cura.txt` | `19-writeback-post-cura.txt` | `93044210014f83b4d86e8855f806fe7854577ce85a39e23fc0a0db66d8725efc` | `797de0725e6ac9c7b472d7758a52d37b37fc3dd0f34c162c1929e5d4341e557f` |
| `21-hook-commit-2.txt` | `20-commit2-hook.txt` | `ab3fbd5c9517cc40c5ffa601a974a94b732f11ad9f9c53d7ba70a118a4b8770e` | `d4ebdb56bbb21fe6294516109d66b399a17b7ed858545e8b16dfa4af78190b5c` |
| `22-quick-tras-deuda.txt` | `21-quick-tras-deuda.txt` | `b780ee4bd230d9642362b4116f6b66c1bb2a780b681552bd939af6ff9cb597ea` | `1547e94a061f0b3947909e0686ee85653cedbe0f9cd513a8bac58fec290d430c` |
| `23-quick-plan-nuevo.txt` | `22-quick-plan-nuevo.txt` | `eaa172369da3e567788b30e907ed53df53a5f022d2bae916970f3c8beaa5d4ec` | `4a53ff65175c74ce8ce9ce730e4941fee64da95fbd8277418ae51d038f3f738d` |
| `24-mensaje-commit-1.txt` | `msg-c1.txt` | `b152f3d66279138c2e0326b312ae7b4b572b7970f0a415d99d847fbb6bb059ed` | `b152f3d66279138c2e0326b312ae7b4b572b7970f0a415d99d847fbb6bb059ed` (igual) |
| `25-mensaje-commit-2.txt` | `msg-c2.txt` | `ce23500fde0f4c1275fffa4d28be501a133e80f07b02a8432bc792027812592c` | `ce23500fde0f4c1275fffa4d28be501a133e80f07b02a8432bc792027812592c` (igual) |
| `26-l3-5341e15-a-1f95e84.json` | `l3-out.json` | `a19d77679720612c3ac4e5b789f017a4906b8011b5e13f272a35bb8e13a70bda` | `a19d77679720612c3ac4e5b789f017a4906b8011b5e13f272a35bb8e13a70bda` (igual) |

Copia verificada `origen == destino` en disco: crudo `01` de esta fase no aplica; la verificación se imprimió en sesión y sus pares de bytes son los de la columna «disco». Los shas de blob salen del índice stageado (`git cat-file blob :<ruta>`), crudo `07-shas-blob-vs-disco.txt`.

---

## §2. T2 — El commit (AC1) — con la letra del Operador

**Commit `77dea21`** — `docs(evidencia): los crudos de la tanda 2026-10-15 versionados bajo FASE-RELEASE (15-26)` — **12 rutas exactas** (las de §1), nada más.

Protocolo `L-SECF.2` cumplido: `git status --porcelain` listado antes (crudo `05`), `git add` **nominal por ruta** (prohibido el `add` de directorio padre), `git diff --cached --name-only | wc -l` = **12** contrastado contra el listado esperado (crudo `06`), y `git status` posterior demuestra que **no quedan restos de T1+T2** (solo el directorio de evidencia de esta propia fase, que viaja en el commit de docs).

**El hook pre-commit corrió sus 8 checks, ninguno saltado** — pero hizo falta un tercer intento, y los tres quedan como crudo:

| Intento | Crudo | Resultado | Causa |
|---|---|---|---|
| 1 | `08-hook-pre-commit.txt` | 7/8, cortó en `[8/8]` | El `[8/8]` clona el árbol a `TMPDIR`; con `TMPDIR` en el scratch (ext4) el clon desde `/mnt/c` muere con `Invalid cross-device link`. **Fallo ambiental, no del árbol.** |
| 2 | `08b-hook-pre-commit.txt` | 7/8, cortó en `[6/8]` | Ventana concurrente: la otra sesión revertió/regeneró el par del índice para su commit `53fe9ed` mientras el hook corría → corpus ≠ par por segundos → «índice vencido». **Transitorio, ya cerrado por su commit.** |
| 3 | `08c-hook-pre-commit.txt` | **8/8 PASSED**, `COMMIT-EXIT=0` | Con `TMPDIR` en el mismo FS que el repo (`/mnt/c/Users/Jhond/AppData/Local/Temp`) y el árbol estable. |

El `git show --stat 77dea21` imprime 12 archivos / 346 inserciones: solo T1+T2. El mensaje declara la autoría de la sesión anterior (los crudos se escribieron en la tanda `2e048e6`/`1f95e84`, no en esta).

**Fuera del commit**: el trabajo ajeno (`CONTEXT-DEUDAS-PRODUCTO-VERIFICADAS-2026-10-21` + par), que su propia sesión versionó en `53fe9ed` — decisión del Operador respetada y sin duplicar. **Sin push** (decisión del Operador): no hubo L3 porque no hubo push; la paridad con `origin/master` queda sin medir y AC1 conserva literalmente su parte «empujadas» **pendiente de autorización**.

---

## §3. T3 — Verificación del cierre (AC1, AC2, AC6)

Tres corridas **re-ejecutadas en esta sesión** (nada heredado de la preparación — `L-V.2`):

| Corrida | Resultado | Crudo |
|---|---|---|
| `build_lesson_index.py --check` | `[OK] Índice de lecciones fresco (389 IDs)` | `01-lesson-index-check.txt` |
| `validate_opencode_refs.py` | `[PASS] todas las referencias existen` | `02-opencode-refs.txt` |
| `run_all_validations.py --quick` (venv canónico) | **13/13 — ALL VALIDATIONS PASSED** | `03b-quick-venv-canonico.txt` |

**Advertencia de intérprete (medida, no parecer)**: la primera corrida del quick salió **9/13** (crudo `03-quick.txt`) con `.venv-wsl` (Python 3.11). La causa es contaminación del intérprete, no del árbol: `validate_governance_numbers.py` usa f-strings multi-línea (PEP 701, Python ≥3.12) que 3.11 rechaza como `SyntaxError`, `requests` no está instalado en `.venv-wsl`, y el clon del `[13/13]` muere cross-device bajo ese runtime. Con el **venv canónico** (`venv/Scripts/python.exe`, el mismo par que la tanda documentó en `01-quick-crudo-interprete-venv-wsl-3.11-9-de-13.txt` vs `02-quick-crudo-venv-canónico-13-de-13.txt`): **13/13**. El verde certificado es el canónico; el rojo del 3.11 queda publicado, no borrado.

**Población gobernada en el árbol del commit** (`git archive` de `77dea21` a un temporal + `poblacion_del_context` de `scripts/verify_qmind_context_freshness.py`), crudo `09-poblacion-arbol-commit.txt`:

- **GOBERNADOS: 1** — `context/CONTEXT-CONTRATO-PLANTILLA-TIER-2026-10-12.md`.
- **EXCLUIDOS: 25** — 23 en `Historico/`, y 2 que no autodeclaran lección durable (`CONTEXT-DEUDAS-WRITER-QMIND-2026-10-15`, `CONTEXT-DEUDAS-PRODUCTO-VERIFICADAS-2026-10-21`).

La expectativa «2 gobernados» del prompt está **vencida por `26bd0f5`** (§0.3): los dos CONTEXT publicados ya no son dos gobernados porque uno vive en `Historico/`. Se publica la cifra medida y su causa; no se re-numera nada para cuadrar.

---

## §4. T4 — Este acta, la post-ejecución y el registro de fase

Post-Ejecución 1-7 completa: `dependencias-fases.md`, README del plan, `06-checklist-implementacion.md`, `09-documentacion-post-proyecto.md`, `10-analisis-post-implementacion.md`, `00-lecciones-capitalizadas.md` §2, este acta + crudos, y `log_phase_completion.py --fase FASE-A --tests 0` (la fase se registra a sí misma). `DOMAIN_PRIMER` **no** se regenera (no es fase de implementación). No se escribió ningún `CONTEXT-*.md` nuevo, así que no hay pregunta de aporte durable que formular.

**Cinco cortes declarados**: implementación terminada (T1) → verificación terminada (T3) → cierre documental (este acta) → listo para revisión → espera de autorización (satisfecha en sesión para los dos commits; **no** para el push). Sin push sin L3 y sin autorización: cumplido — no hubo push.

---

## §5. Frontera con FASE-B

- **La deuda era-G queda intacta**: el rojo `[DUPLICADO-VIGENTE]` del writer no se tocó, no se midió el write-back y **no se subió nada al notebook**. El censo y la decisión por fuente son de FASE-B.
- **`D-QW-1`/`D-QW-2` siguen diferidas** con dueño Operador (maestro §5): esta fase solo versionó sus rutas y crudos, no curó nada.
- **`temp/` intacto** (780 entradas): nadie lo borra sin orden del Operador.
- **AC1 deja literalmente pendiente la palabra «empujadas»**: los commits están locales hasta que el Operador autorice push (con L3 entre el último commit y el push).
- **Lección operativa para quien commitee desde WSL**: el `[8/8]` del hook exige `TMPDIR` en el mismo FS que el repo, y el quick se certifica con el venv canónico.

---

## §6. Presupuesto (R2.1 / D-V2.1)

**Auto-reporte, no medido por instrumento**: ~70 `tool calls` en esta sesión (una primera tanda de ~60 agotó el tope de iteraciones y la sesión continuó). El estimado era ~30 y se superó: la causa fue la re-medición del árbol vencido, la contaminación de intérprete del quick y los dos intentos de commit cortados (uno ambiental, uno por concurrencia). Ninguna cifra de este acta proviene de un medidor de transcripción.

## §7. Crudos de esta sesión (todos en `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-A/`)

`01-lesson-index-check.txt`, `02-opencode-refs.txt`, `03-quick.txt` (9/13, venv-wsl 3.11), `03b-quick-venv-canonico.txt` (13/13), `04-poblacion-arbol.txt` (sobre `467de54`), `05-git-status-pre-commit.txt`, `06-staged-listado.txt`, `07-shas-blob-vs-disco.txt`, `08-hook-pre-commit.txt`, `08b-hook-pre-commit.txt`, `08c-hook-pre-commit.txt`, `09-poblacion-arbol-commit.txt` (sobre `77dea21`).
