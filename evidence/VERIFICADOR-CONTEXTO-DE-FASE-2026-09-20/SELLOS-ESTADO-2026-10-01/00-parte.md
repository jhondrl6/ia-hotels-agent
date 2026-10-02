# 00-parte — SELLOS-ESTADO-2026-10-01 (plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20)

**Fecha de la tanda:** 2026-10-01 (los sellos se rotulan con la fecha de la tanda; la ejecución y todas las
mediciones de este parte se hicieron el **2026-10-02**, y cada cifra lleva abajo su fecha de medición).

**HEAD inicial:** `21b552f`. Paridad medida tras `git fetch origin --quiet`:
`git rev-list --left-right --count origin/master...HEAD` = **0 0**. Árbol inicial limpio:
`git status --porcelain` = **0 líneas**.

**Frescura PRE de los derivados:** `build_phase_briefing.py --check --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`
→ **exit 0**; `build_lesson_index.py --check` → **exit 0** (`340 IDs`).

---

## 1. Tabla ancla → archivo → estado

| # | Ancla (literal buscado con `grep -nF`) | Archivo | Estado |
|---|---|---|---|
| 3a | `piloto FASE-C no lo están` | `README.md` (línea 34) | **aplicado**, con adaptación declarada en §4 |
| 3a | `piloto FASE-C no lo están` | `06-checklist-implementacion.md` (línea 9) | **aplicado** (texto del mandato tal cual) |
| 3b | `de esta frase queda en pie solo la segunda mitad` | `README.md` (la nota que contiene esa frase cierra en la línea 46; el sello va **tras ese `⟧`** y antes de la «Segunda rectificación») | **aplicado** |
| 3c | `cerrada sin commit ni push` | `dependencias-fases.md` (línea 9) | **aplicado** — el sello va tras el paréntesis `(ver su fila en §Cadena …)` que pertenece a la misma oración, para no partir la frase original |
| 3d | `\| Checks del \`--quick\` \| **11** (delta 0, AC16) \|` | `README.md` (línea 246) | **aplicado** en la celda central, con el pipe del comando escapado (`\| sort -u`) para no romper la tabla: ver §4 |
| 3d | `\| Pasos del hook \| **7** (delta 0, AC16) \|` | `README.md` (línea 247) | **aplicado**, mismo sello y mismo escape |
| 3e | `\| Checks de \`run_all_validations.py --quick\` \| 11 \|` | `09-documentacion-post-proyecto.md` (línea 133) | **aplicado** en la celda `Post`, que es la que publica la cifra |
| 3e | `\| Checks del hook \`scripts/git_hooks/pre-commit\` \| 7 \|` | `09-documentacion-post-proyecto.md` (línea 134) | **aplicado**, misma celda |
| 3f | `13,08 % de la carga total` | `09-documentacion-post-proyecto.md` (línea 139) | **aplicado** tras el cierre del tramo en negrita, para no extender la negrita sobre el sello |
| 3g | `COMPLETO **4**, SECCION-NO-RESUELTA **1** (RELEASE)` | `06-checklist-implementacion.md` | **aplicado con desacuerdo de ubicación**: el mandato la llama «fila AC19» y no está en la fila AC19 (línea 48: esa fila no lleva el recuento). El texto está en el **bullet de §FASE-D**, líneas 218-219, **cruzando un salto de línea** (`COMPLETO **4**,\n SECCION-NO-RESUELTA **1**`), por eso `grep -nF` del literal completo no lo devuelve. El sello se aplicó ahí, junto a la frase. |
| 3g | `Medido sobre el plan: COMPLETO 4, SECCION-NO-RESUELTA 1` | `06-checklist-implementacion.md` (fila **AC22**, línea 51) | **aplicado** dentro de la celda Estado |
| 3h | `generado_por_sha` que afirma «no aplicada» | `10-analisis-post-implementacion.md` | **aplicado con desacuerdo de censo**: el mandato espera **dos** ocurrencias; medido, en este archivo hay **una** (línea 466). La otra coincidencia de `no aplicada` en el archivo (línea 27) es la fila FASE-C y habla de otra cosa (el corpus real de AC13), así que no se selló. |
| 3h | `generado_por_sha` que afirma «no aplicada» | `dependencias-fases.md` §S19 | **aplicado con desacuerdo de censo**: el mandato espera **una**; medido, §S19 tiene **tres** cláusulas que lo afirman (líneas 654-655 «…y no aplicada», 663 «…y no se aplica», 673 «sigue siendo una cuarta opción medida y no aplicada»). Se selló la del libro (654-657, que es la fila contable del estado). Las otras dos **viven anidadas dentro de anotaciones fechadas del 2026-09-26/27 que son antecedente explícito**, y se dejan como están; se declaran aquí en vez de reescribirlas en silencio. Residuo conocido: `⟦Sello 2026-09-28⟧` de esa misma sección (línea ~677) afirma «queda **ABIERTA** por la salida (c)» y «releída así, la clave no está publicada», ambas vencidas por la (d) aplicada; no entraba en el criterio del mandato («ocurrencia que diga que la (d) está no aplicada») y queda sin sello. |
| 4 | fila de deuda nueva | `dependencias-fases.md`, tras §S34 | **aplicado con desacuerdo de número** — ver §3 |
| — | (sin espejo en este plan) | — | El espejo de S37 del plan JEV vive en su propio `10-analisis-post-implementacion.md` |

**Recuento efectivo, medido sobre el commit de la tanda con `git grep -o 'Sello 2026-10-01' HEAD -- … | wc -l`:
17 sellos en los 9 ficheros fuente** — **4** en el plan JEV y **13** aquí (`README.md` 4 = 3a+3b+3d×2;
`06-checklist-implementacion.md` 3 = 3a+3g×2; `09-documentacion-post-proyecto.md` 3 = 3e×2+3f;
`10-analisis-post-implementacion.md` 1 = 3h; `dependencias-fases.md` 2 = 3c+3h). Fuera de los sellos hay dos
escrituras más: la **fila de deuda S37** (PASO 4) y su **línea espejo** en el `10-analisis` del JEV
(`git grep -o 'Espejo 2026-10-01'` = 1). Viaje a los derivados: esos 13 sellos aparecen **13 veces** en los
cinco packs regenerados, porque la prosia del corpus viaja al pack.

El mandato hablaba de «7 puntos, 9 inserciones» para este plan; los puntos medidos son 8 y las inserciones 13,
y la diferencia se justifica por los dos desacuerdos de censo de la tabla (3h) y por el ancla de 3g que cayó en
otro sitio. La primera versión de este parte decía «16 / 12»; quedó refutada por el conteo de arriba, que es el
que se publica.

## 2. Censo del número de deuda (PASO 4), con su comando y su fecha

El censo se ancla a **HEAD** (`21b552f`), no al árbol de trabajo: escribir esta fila añade menciones de su
propio número, y un censo re-corrido después de la escritura ya no mide lo que había antes.

- `git grep -o -E "\bSnn\b" HEAD -- '*.md' | wc -l` (ocurrencias, 2026-10-02): **S33 = 19**, **S34 = 46**,
  **S35 = 7**, **S36 = 7**, **S37 = 0**.
- `git grep -c -E "\bSnn\b" HEAD -- '*.md'` (comando de la casa — **archivos** donde aparece el ID):
  **S33 = 7**, **S34 = 11**, **S35 = 6**, **S36 = 6**, **S37 = 0**.
- El barrido que pedía el mandato, `git grep -nE "\bS3[4-9]\b" HEAD -- '*.md'`, da **30 líneas**; por ID, sobre
  el mismo HEAD: **S34 = 30 líneas en 11 archivos**, **S35 = 7 líneas en 6 archivos**, **S36 = 7 líneas en 6
  archivos**, **S37 = 0**. Las líneas de S35 y S36 son subconjunto de las de S34: las dos claves solo aparecen
  dentro de la prosa del censo de esa fila y de los packs que la reproducen.
- **Decisión:** se toma **S37**. S35 y S36 **no están limpios**: sus únicas menciones son la prosa del censo
  de la fila S34 (línea 1212) y los packs que la copian; darles un número nuevo haría que `git grep -E "\bS35\b"`
  devolviera dos asuntos distintos bajo la misma clave — el defecto que la propia fila S34 documentó con «S33 =
  6 archivos (YA USADO)». El primer ID con **cero** es S37, y ese fue el criterio con el que S34 se tomó a sí
  mismo. El mandato daba por supuesto que el libre siguiente era S35; se declara la deriva.

## 3. Comprobaciones contra disco que sostienen los sellos

- **3a/3b** — el piloto FASE-C se ejecutó y cerró el 2026-09-24: `§Cadena` fila 3 lo declara CERRADA con sus
  commits; el README ya lleva la «Segunda rectificación del mismo 2026-09-24, por cierre de FASE-C» (líneas
  46-52). El checklist **no** lleva esa segunda rectificación, y su §FASE-C existe en la línea 148.
- **3c** — `git rev-parse` de `7f2e9f9`, `5817edd`, `da382b1`: los tres existen; `git merge-base --is-ancestor
  <c> HEAD` → **sí** para `7f2e9f9`, `5817edd` y `84282c1`. La fila 3 de §Cadena publica el rango
  `da382b1..5817edd` y las **37** rutas propias.
- **3d/3e — los denominadores ya se movieron** (medido, no inferido):
  - hook: `grep -oE '^[[:space:]]*# *\[[0-9]+/[0-9]+\]' scripts/git_hooks/pre-commit | sort -u` → **`[1/8]` … `[8/8]`** (8 pasos; la fila decía 7).
  - quick: `grep -coE '^\s*print\(f?"\[[0-9]+/[0-9]+\]' scripts/run_all_validations.py` = 18 literales; las
    etiquetas impresas llegan hasta **`[13/13]`** en modo rápido y **18** en modo completo (la fila decía 11).
  - La AC16 del checklist (línea 45) ya lleva su propia nota: «Cifra vencida el 2026-09-26, verificación
    intacta. El quick pasó a 12 checks y el modo completo a 16 por **D2**»; y §S34 declara el salto **17→18**
    del modo completo por **D-a** y el verificador nuevo. Eso es lo que el sello cita al decir «D2, D-a y S34 lo
    movieron fuera de este plan».
- **3f** — la fila «Carga de lectura A7» del `README.md` de este plan (línea 252) publica **13,15 %** como
  «cifra recalculada el 2026-09-25 … como `216.721 ÷ 1.648.109` sobre `carga.json`», y declara que sustituye a
  `13,08 %`, `12,8 %` y «en el orden del 12 %». La aritmética de la propia fila de §D también lo refuta:
  216.721 ÷ 1.648.109 = **13,149 %**, no 13,08 %.
- **3g** — `grep -H 'estado del pack' .opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/*.md`
  → **los cinco** packs imprimen ``estado del pack`: `COMPLETO``. Y la fuente de la corrida del 2026-09-24,
  `evidence/…/FASE-D/informe.json`: `status` = **`EMITIDO`**, `coverage_basis.packs_por_estado` =
  `{COMPLETO: 4, SECCION-NO-RESUELTA: 1, FUENTE-AUSENTE: 0}`, `packs[].estado` = 4×COMPLETO + 1×SECCION-NO-RESUELTA.
  El recuento sellado describe esa corrida, exactamente como dice el sello.
- **3h** — la (d) está aplicada: `grep -c 'generado_por_sha' scripts/build_phase_briefing.py` = 1 y los packs
  vigentes llevan la clave (6 líneas por pack, 7 en RELEASE); `scripts/verify_packs_in_committed_tree.py:52` la
  normaliza como **quinto patrón** (`NORMALIZAR`); la batería existe con **5** funciones de test
  (`grep -cE '^\s*def test_' tests/test_verify_packs_quinto_patron_generado_por_sha.py` = **5**, medido 2026-10-02).
- **Escape del pipe en 3d** — las filas 246/247 del README tienen **5** caracteres `|` cada una, **1** de ellos
  escapado (`\| sort -u`), así que las celdas efectivas siguen en **3** (4 separadores) como su cabecera. Las
  demás filas tocadas dentro de tablas conservan el número de celdas de su cabecera: `09-doc` 133/134 (5
  separadores, 4 columnas) y 139; `06-checklist` 51 (6 separadores, 5 columnas). Sin el escape, el comando
  `… | sort -u` habría partido la fila en una columna nueva.

## 4. Adaptaciones declaradas sobre el texto del mandato

1. **3a en `README.md`**: el mandato escribe «la sección FASE-C de **este checklist**», y en el README esa
   sección no existe (sus secciones son otras; §FASE-C está en el checklist). Se cambió solo el destino citado,
   ``06-checklist-implementacion.md``, que es donde vive. En el checklist el sello quedó literal.
2. **3d**: el pipe del comando se escapó `\|` por integridad de la tabla (ver §3). El comando sigue siendo el
   que hay que correr, tal cual se publica en este parte.
3. **3h**: al sello se le añadió el valor medido de su propio comando (`= 5, medido 2026-10-02`) para que la
   unidad viaje con la cifra, regla de la casa.
4. **3g**: los identificadores (`coverage_basis.packs_por_estado`, `packs[].estado`, `EMITIDO`, `briefing/`) se
   escribieron en código markdown; el texto del mandato no los marcaba.
5. **Fila S37**: redactada con la letra del mandato; el censo y su comando se añadieron porque el propio
   mandato exige «deja el comando y su fecha en la fila».

## 5. Huellas sha256 PRE / POST (los 9 ficheros de la tanda + el expediente protegido)

Comando: `sha256sum <ruta>` sobre el árbol de trabajo.

| Archivo (plan CONTEXTO) | PRE | POST |
|---|---|---|
| `README.md` | `895d4e82f20d7f2f77d37962c4fa3142a63e20ed764758fa7f8d9c37f1750b43` | `f915ddea6bf52ee787330344f9fd6d2899a84173fd4a882d490e16abbe0fee38` |
| `06-checklist-implementacion.md` | `55fa59754f7430cc8a02857c946b5ddd07d858602a1b15ab5516c4faa6039356` | `d5676872a9b98152c871917368d9f9692f48bce0b45f9ef5e1ec08f9c7df6e12` |
| `09-documentacion-post-proyecto.md` | `f82c11d08387695e8688bc3c4a5991a9faa6807fc1a37593ee522b1e9bc87f0c` | `561d9f0781f9ff733ef6326fbc3d55670ebac1930974ba3ceb5db377085bf23d` |
| `10-analisis-post-implementacion.md` | `56b268c3b422921497118a857bf9f60bc82213a55f61f3fd8ba036491842b3f4` | `0f52237a919f2508b41e6821094dff98992f7079c2e7a0ee146368804febb63c` |
| `dependencias-fases.md` | `e3300ab51712e96098063da4e594c3229c8c9dfecdb0c3f76f6646edd26d5021` | `6b8591568cc148d567ecde55b619ff2c9c76adcfb46b5f407def37081207c2bd` |

Los cuatro ficheros del plan JEV (completan los 9 de la tanda) y sus huellas PRE/POST viven en
`evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/SELLOS-ESTADO-2026-10-01/00-parte.md` §2.

**Expediente protegido — debe quedar idéntico:**
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/mutation/verde_baseline.txt`
PRE = POST = `e29a5574d151505f5e999f747f41942463b717cae2972eb9cc7aec688f104c8e` → **idéntico**.

## 6. Numstat por fichero

`git diff --numstat` contra `21b552f` (2026-10-02, antes del commit):

| Archivo | + | - |
|---|---|---|
| `README.md` | 4 | 4 |
| `06-checklist-implementacion.md` | 3 | 3 |
| `09-documentacion-post-proyecto.md` | 3 | 3 |
| `10-analisis-post-implementacion.md` | 1 | 1 |
| `dependencias-fases.md` | 24 | 2 |
| `briefing/FASE-A.md` | 35 | 13 |
| `briefing/FASE-B.md` | 34 | 12 |
| `briefing/FASE-C.md` | 17 | 17 |
| `briefing/FASE-D.md` | 34 | 12 |
| `briefing/FASE-RELEASE.md` | 48 | 26 |

## 7. Paso 5 — derivados y checks (salidas crudas, orden del mandato)

**7.1 `build_phase_briefing.py --plan .opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` → EXIT=0**

```
[pack] FASE-A: COMPLETO -> FASE-A.md
[pack] FASE-B: COMPLETO -> FASE-B.md
[pack] FASE-C: COMPLETO -> FASE-C.md
[pack] FASE-D: COMPLETO -> FASE-D.md
[pack] FASE-RELEASE: COMPLETO -> FASE-RELEASE.md
[denominador] 5 packs · COMPLETO 5 · SECCION-NO-RESUELTA 0 · FUENTE-AUSENTE 0 · fuentes 37 · secciones pedidas 23, resueltas 23, declaradas no resueltas 0
[OK] FASE-A: 4 fuentes frescas y proyeccion del workflow conforme
[OK] FASE-B: 4 fuentes frescas y proyeccion del workflow conforme
[OK] FASE-C: 4 fuentes frescas y proyeccion del workflow conforme
[OK] FASE-D: 4 fuentes frescas y proyeccion del workflow conforme
[OK] FASE-RELEASE: 10 fuentes frescas y proyeccion del workflow conforme
```

**7.2 `build_lesson_index.py` → EXIT=0**

```
[OK] 340 IDs definidos + 54 sin definición (16 análisis, 422 .md citados)
  -> .opencode/LECCIONES-INDEX.md
  -> .opencode/lecciones_index.json
[fechas] nombre=329 commit=11 sin_fuente=0
```

El par **no cambió de bytes**: `git status --porcelain` no reporta `.opencode/LECCIONES-INDEX.md` ni
`.opencode/lecciones_index.json` como modificados. Los 340 IDs siguen siendo los de HEAD; la fila S37 nueva no
entra en la población del índice (el índice no enumera `### Snn` de `dependencias-fases.md`), y se declara para
que nadie lea eso como un verde vacío: el comando de re-medida es el propio `--check` de 7.4.

**7.3 `build_phase_briefing.py --check --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` → EXIT=0**

```
[OK] FASE-A: 4 fuentes frescas y proyeccion del workflow conforme (procedencia distinta, no vence)
[OK] FASE-B: 4 fuentes frescas y proyeccion del workflow conforme (procedencia distinta, no vence)
[OK] FASE-C: 4 fuentes frescas y proyeccion del workflow conforme (procedencia distinta, no vence)
[OK] FASE-D: 4 fuentes frescas y proyeccion del workflow conforme (procedencia distinta, no vence)
[OK] FASE-RELEASE: 10 fuentes frescas y proyeccion del workflow conforme (procedencia distinta, no vence)
```

**7.4 `build_lesson_index.py --check` → EXIT=0**

```
[OK] Índice de lecciones fresco (340 IDs)
[fechas] nombre=329 commit=11 sin_fuente=0
```

**7.5 `python scripts/run_all_validations.py --quick` → 13/13, EXIT=0** (intérprete: `python` = Python 3.13.3,
el mismo que resuelve el hook; 2026-10-02 11:43)

```
  MODO: rapido - el denominador de las etiquetas impresas es el del modo rapido (13); el modo completo llega a 18 y solo sus 5 exclusivas se etiquetan con ese numero
  [+] Residual Files: No residual files found
  [+] Plan Maestro Sync: Plan Maestro vv2.5.0 loaded correctly
  [+] Version Sync: All versions synchronized
  [+] Secrets Check: SIN_HALLAZGOS: 1370 tracked files + staged (excluidos declarados: 0 binarios conocidos, 1 symlinks)
  [+] Client Material: SIN_HALLAZGOS: 3238 rutas contra 4 marcadores (1 grandfathered con dueño)
  [+] Document Integration: All cross-document checks passed
  [+] Prompts No Release: No --release flag in intermediate prompts
  [+] OpenCode References: All .opencode references exist
  [+] Plan Citations: [OK] Plan citations: 743 citas historicas, 0 nuevas y 0 crecimientos (79 archivos en el inventario)
  [+] Lesson Capitalization: [OK] Capitalización del Paso 0: forma y trazabilidad verificadas | NO verifica pertinencia
  [+] Wiring: 174 llamadas descubiertas en 688 archivos | gobernadas 75 (conformes 21, omisiones 0) | violaciones 0 | 684 excluidos por declaracion de Git | receptores no resueltos 25
  [+] Governance Numbers: [SIN-HALLAZGOS] validate_governance_numbers.py - aserciones de conteo en documentos de gobierno vs etiqueta impresa por el codigo
  [+] Briefing Packs in Commit Tree: [OK] packs en el árbol de HEAD (5/5 reproducidos por el escritor, 0 divergentes, 0 no evaluables)
  TOTAL: 13/13 validations passed
  STATUS: ALL VALIDATIONS PASSED
  [GUARDA] las 13 etiquetas impresas casan con el TOTAL dinamico
```

Nota de instrumento: `[13/13]` valida los packs **del árbol de HEAD**, no los de este árbol de trabajo; su verde
no avala todavía los packs regenerados arriba. El que los avala es `7.3`, que lee las fuentes de este árbol.

## 8. Prohibiciones cumplidas

Sin `pytest` (ni suites ni baterías), sin `--no-verify`, sin push, sin llamadas a APIs, sin tocar baselines.
No se editó `dependencias-fases.md` del plan JEV (protegido), ni `.agents/**`, `scripts/**`, `tests/**`,
`tmp_test/**`, `AGENTS.md`, `.cursorrules`, `VERSION.yaml`, `CHANGELOG.md`, `REGISTRY.md`. El censo del PASO 4
fue de solo lectura.

⟦**Nota de disposición 2026-10-02** — el «sin push» de arriba describe la ventana de ejecución del mandato,
que lo prohibía; esa ventana cerró con el commit. Los dos commits de la tanda —`8a75c03` (los sellos, los packs
y la fila S37) y `9903012` (la corrección del recuento de los partes)— se empujaron a `origin/master` el
2026-10-02 como el rango `21b552f..9903012`, con pre-flight antes de empujar (`git fetch origin --quiet` y
`git rev-list --left-right --count origin/master...HEAD` = **0 2**; `git push --dry-run` mostrando el mismo
rango) y verificación por identidad tras el push (`git ls-remote origin refs/heads/master` devolvió
`99030129a4426938351d2be0e7af9a65bf39e1b8`, igual que `git rev-parse HEAD`, y
`git grep -o 'Sello 2026-10-01' origin/master --` sobre los 9 ficheros fuente dio **17**). L3: **no se corrió**,
por orden escrita del operador («Push sin L3»). Esta nota entra en un commit **posterior** al rango que
declara, así que no publica su propia paridad ni su propio sha: el estado vigente se lee con
`git fetch origin --quiet && git rev-list --left-right --count origin/master...HEAD`.⟧
