# FASE-B — Estabilizar el control S15 del índice de lecciones (AC7, AC8)

**ID:** CURA-INSTRUMENTOS-QMIND-S15 / FASE-B
**Estado:** ✅ **CERRADA 2026-10-09** contra HEAD `77e64ca` (== `origin/master`), árbol **sin commitear** (no hubo
instrucción literal de commit). AC7 landed con la causa medida y sus dos hipótesis descartadas; AC8 landed con el
reloj derivado del corpus, el clon fiel por patrón S20 y sus 2 mutantes. **FASE-C declarada «no aplica»**. Acta:
`evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-B/00-registro-de-fase.md`; diagnóstico: `…/diagnostico.md`.
**Objetivo:** que `tests/test_build_lesson_index_s15_fecha_versionada.py` deje de fallar según el entorno **sin
perder el diente**: el control tiene que seguir perdiendo cuando el generador está en su revisión defectuosa, y
seguir ganando cuando está curado, con la divergencia esperada gobernada.
**Dependencias:** ninguna de código con FASE-A (otra superficie, mismo repo). Se ejecuta **después** de A3 para no
pelear con ella el par regenerado del índice.
**Complejidad:** ALTA — es un control anti-regresión cuya premisa de entorno ya cayó una vez, y su fracaso actual
afecta a **cada commit** (`[6/8]` del hook).
**Skill:** `.agents/workflows/phased_project_executor.md`.
**Modo:** DIRECTO; delegable solo un inventario `read-only` de dueños del corpus. **R3:** 4 tareas, 0 comandos largos.

## Contexto medido

- `test_el_control_defectuoso_de_la_revision_publicada_si_diverge` **falla hoy**, reproducido en la preparación
  contra `98c190e` (`E/FASE-0/pre_seleccion_apertura.txt`: 1 failed / 26 passed, EXIT=1). El mensaje impreso es
  exactamente `assert ('mtime' == 'mtime' … mtime and 'nombre' == 'mtime' … - mtime + nombre)`.
- El archivo tiene **4** funciones `def test_` y las otras tres están verdes, incluida
  `test_dos_checkouts_con_mtimos_distintos_publican_bytes_identicos` — o sea el **corte positivo** de la cura del
  2026-09-26 sigue funcionando; lo que pierde es el **control negativo**.
- Mecanismo que hay que **reproducir midiendo**, no dar por cierto: el control ejecuta el generador de la revisión
  fija `REV_CONTROL_DEFECTUOSO = 6b02532` (cuyo `_plan_date` caía a `f.stat().st_mtime`) sobre **dos clones del
  mismo commit** con mtimes declarados distintos (`MTO_A = 2020-01-02`, `MTO_B = 2031-06-06`, aplicados con
  `os.utime` a los dos documentos de `DOC_SIN_FECHA` bajo `context/Historico/`). En el clon A el dueño que gana por
  fecha-temprana es el documento fechado por `mtime`; en el clon B ese mismo `mtime` (2031) es **más tarde** que
  cualquier fecha del tier `nombre`, así que gana un plan dueño con fecha en el nombre y la clasificación sale
  `nombre`. La aserción exige `mtime` en **ambos** árboles.
- Por eso el síntoma depende del corpus y no solo del entorno: **el corpus cambió desde la medición del mandato.**
  Entre `086ce65` y `98c190e` hay 20 rutas de diferencia bajo `.opencode/`, incluidos los `git mv` que archivaron
  el plan padre y la regeneración del par del índice (maestro §1 fila 2). FASE-B reproduce contra su HEAD y publica
  su propia banda; la medición del 2026-10-07 es antecedente, no resultado de esta fase.
- Antecedente de la cura original, recuperado del corpus (Q7 de `00-lecciones-capitalizadas.md`, fila S15 del
  `10-analisis` de `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`): `mtime` fue **retirado** de la lista de fuentes y
  `_plan_date` quedó en tres cortes — `nombre`, `commit` (`%aI` del último commit que tocó el documento, recortado
  a 10 caracteres) y `SIN-FUENTE` con `0000-00-00`. Su **límite declarado y no curado allí**: «un futuro `git mv`
  masivo de `Historico/` colapsaría esas dos fechas a una sola y el desempate pasaría al nombre del plan». Y su
  segundo disparador vivo: «un `[FAIL]` en un clon con CRLF no es S15 sino el otro corte — hay que clonar con
  `-c core.autocrlf=input`».
- Forma del clon en el test: `_pareja_de_checkouts` pasa `-c core.autocrlf=input -c core.longpaths=true` **como
  flags del `git clone`**, y materializa solo `.opencode/plans` y `.opencode/context` con
  `git checkout HEAD -- …`. El patrón S20 (config escrita **dentro** del clon y verificada con `--get`) vive en
  `scripts/verify_index_in_committed_tree.py::clon_fiel`. Medir si la flags-del-clon bastan o si el árbol del clon
  hereda el `core.autocrlf` del sistema.

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-VCF-15 | Un verde del árbol de trabajo no sustituye la prueba en el árbol del commit | El control se ejecuta sobre el generador **commiteado en `6b02532`** (`git show`), y la fecha esperada se re-deriva del corpus en vez de pinearse |
| L-T4A.5 | Un verde puede no alcanzar la rama que dice certificar | Prohibido concluir «el fixture está mal» sin reproducir la clasificación; el diente de AC8 tiene que perder cuando se apaga la gobernanza nueva |
| L-V2.1 | Un test que solo mira qué check disparó queda verde por la rama equivocada | AC7 nombra por cada `i` divergente **qué dueño** produce la fecha y por qué tier; no basta el par `mtime`/`nombre` |
| L-QW.3 | Un verde por ausencia del instrumento es un rojo disfrazado | Si un clon no materializa la ruta, el resultado es NO-EVALUABLE con la ruta buscada, no «divergencia hallada» ni verde |
| L-ENT.14 | Una prueba de NO-existencia recortada por un `head` no prueba nada | El inventario de dueños y el censo de tiers (`[fechas]`) se publican completos |
| L-VUP-5 | Un contrato verde exige mutación | AC8 cierra apagando la gobernanza nueva y mostrando el rojo, con restauración por sha |

## Tareas

### Tarea 1 — AC7: diagnóstico con medición (sin tocar nada)

Correr el archivo de control capturando, **por cada `i` divergente**, la tupla `fuente_fecha` de A y de B, el
documento dueño que la produce y el tier que la ganó en cada árbol. Medir las tres hipótesis candidatas y publicar
cuál cae:

1. **Dependencia del reloj del corpus:** con `MTO_B` en 2031 el documento `mtime` queda **después** de todo dueño
   con fecha en el nombre, así que el desempate cambia de bando. Prueba: reproducir con un par de mtimes ambos
   anteriores al plan fechado más antiguo del corpus y medir si la divergencia sigue siendo `mtime` en los dos
   árboles. **Si esta hipótesis se cumple, la cura pertenece al test (gobernar el fixture), no al generador** →
   AC8 sin FASE-C.
2. **Dependencia del entorno del clon:** CRLF/`autocrlf` o `longpaths` sin fijar **dentro** del clon; ruta que no
   materializa. Prueba: comparar bytes de los `.md` del corpus entre árbol y clon, y leer `git config --get` dentro
   del clon. **Si cae aquí, se declara con su receta de clonado y se comprueba si el mismo corte afecta a
   `scripts/verify_index_in_committed_tree.py`** (hermanos que ya fijan la config dentro del clon).
3. **Cambio de población del corpus** (archivado del padre, regeneración del índice). Prueba: correr el control
   contra `98c190e` y contra `086ce65` materializados por `git archive`/clon, y publicar la banda de IDs divergentes
   en cada uno. **Refuta** el uso de la medición del mandato como resultado propio.

Prohibido en AC7: editar código o tests, re-ancorar el control, declarar «el fixture está mal» sin haber
reproducido la clasificación. **Salida esperable:** una de las tres hipótesis se confirma y las otras dos quedan
medidas como descartadas; las tres quedan escritas con su medición.

### Tarea 2 — AC8: cura con el diente intacto

Gobernar la clasificación para que la divergencia **esperada** sea solo la fecha de `mtime`, sin debilitar la
aserción ni el control negativo. Lo que se puede tocar: el fixture, la forma en que deriva su población esperada,
la construcción del clon. Lo que **no** se puede tocar: la aserción `la[i]["fuente_fecha"] == "mtime" and
lb[i]["fuente_fecha"] == "mtime"` reducida a un `in {...}` que traga la mala clasificación; `REV_CONTROL_DEFECTUOSO`
re-ancorado a HEAD; un baseline re-fijado.

### Tarea 3 — Dientes del control y no-regresión

1. El control **pierde** con el generador de `6b02532` puesto (hoy ya pierde: hay que probar que pierde **por la
   razón nombrada**, no por el entorno).
2. El control **gana** con el generador curado, y el corte positivo (`…_publican_bytes_identicos`) sigue verde sin
   tocar su aserción.
3. Apagar la gobernanza nueva (mutante sobre el símbolo del test o del generador, según dónde cayó la cura) **vuelve
   el rojo**, con restauración por sha256.
4. Un caso de entorno declarado NO-EVALUABLE: forzar que la ruta no materialice en un clon y comprobar que el
   mensaje nombra la ruta buscada en vez de afirmar divergencia.

### Tarea 4 — Cierre con las hermanas re-corridas

Si AC8 tocó `scripts/build_lesson_index.py` (código de producto), **esta fase no cierra esa parte**: se declara,
se escribe la fila de `dependencias-fases.md` y continúa FASE-C con AC9. Re-correr las hermanas:
`tests/test_build_lesson_index.py` (16 funciones) y `tests/test_verify_qmind_context_freshness.py` (36 funciones),
más `build_lesson_index.py --check` y el quick. El par regenerado del índice viaja con la fase (R2.10).

## Tests Obligatorios

| Superficie | Criterio |
|---|---|
| `tests/test_build_lesson_index_s15_fecha_versionada.py` | 4 funciones, **cero** aserciones rebajadas; los dientes nuevos se suman |
| `tests/test_build_lesson_index.py` + `tests/test_verify_qmind_context_freshness.py` | 16 y 36 funciones, re-corridas con su selección literal |
| `scripts/build_lesson_index.py --check` | imprime la línea `[fechas]` con sus tres tiers **en verde y en rojo** |
| `run_all_validations.py --quick` | todos sus checks |

## Post-ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-B --fecha 2026-10-08 \
    --desc "CURA-INSTRUMENTOS-QMIND-S15: diagnostico medido del control S15 y cura con diente intacto" \
    --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
```

Resto conforme al contrato §cierre: checklist, 09, 10, 00, CHANGELOG bajo `## [Sin publicar]`, GUIA_TECNICA,
derivados con su escritor, quick, auto-reporte.

## Criterios de Completitud (CHECKLIST)

- [x] AC7 publicado con medición: la causa confirmada (reloj del fixture contra el piso de fechas-en-nombre del corpus, 2026-07-06), las dos descartadas (entorno del clon —pero su premisa de árbol fiel sí estaba rota—, cambio de población —misma banda en `98c190e` y `086ce65`—), y la banda de IDs divergentes medida contra el HEAD de esta sesión (`77e64ca`: 11, con 7 inversiones de dueño)
- [x] AC8 sin aserción rebajada: la cita literal del control antes/después aparece en la evidencia (`E/FASE-B/baseline-pre-post.md`: la aserción `mtime`/`mtime` intacta; 2 `assert` eliminadas, ambas re-emitidas y nombradas; 22 agregadas)
- [x] El mutante de gobernanza devuelve el rojo y su restauración está verificada por sha256 (M1 clamp apagado y M2 clon sin config, ambos `EXIT=1` con la firma nombrada; sha256 del test vivo idéntico antes y después)
- [x] Ningún verde de esta fase depende de `.opencode/` ajeno: las 13 rutas staged del hermano REFACTOR-WHATSAPP (S-CIM-7) no se tocaron ni entraron en conteo; el `--check` en las dos vías se corrió con `--out-dir temp/s15_check`
- [x] Las dos hermanas re-corridas con par pre/post y resta comprobada (R2.7): 18 casos (16 funciones) y 36, `EXIT=0`, ambas intactas por `git diff --stat`; la resta de la fase (4) se comprueba sobre su propia selección
- [x] Si la cura exige el generador, FASE-B **no** lo edita: cierra con la fila de FASE-C abierta y su razón → **no lo exigió**; FASE-C cierra en «no aplica» con la frase contraria escrita y su medición (`diagnostico.md` §5)
- [x] Post-ejecución completo; quick verde; derivados regenerados (`log_phase_completion.py`, `build_lesson_index.py`, `validate_opencode_refs.py --fix`, `doctor.py --regenerate-domain-primer`, `validate_document_integration.py`, quick)

## Restricciones

- No editar `scripts/build_lesson_index.py` en esta fase (pertenece a AC9/FASE-C).
- No re-ancorar `REV_CONTROL_DEFECTUOSO` a HEAD, no re-fijar baselines, no convertir la aserción en pertenencia.
- No tocar `AGENTS.md`, `.cursorrules`, `VERSION.yaml`, el workflow ni los hooks; no liberar versión.
- No iniciar FASE-C ni FASE-RELEASE. Presupuesto **90 `tool_use`** al corte autorizado (la referencia por fase y su
  base medida viven en `04-contrato-ejecucion.md` §R2); auto-reporte con unidad declarada.

## Prompt de ejecución

```
Actua como ejecutor de fases del repo C:\Users\Jhond\Github\iah-cli (rama master), en espanol y sin acentos en
el mensaje de commit.

Lee 01-plan-maestro.md §1 y §4, 04-contrato-ejecucion.md, 00-lecciones-capitalizadas.md §2 y §4, dependencias-fases.md, 05-prompt-inicio-sesion-fase-B.md y el workflow canónico.

Ejecuta SOLO FASE-B del plan .opencode/plans/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07.

OBJETIVO: estabilizar el control S15 sin perder su diente, publicando la causa con su medicion y no con su hipotesis.

TAREAS: 1) AC7 diagnostico midiendo las tres hipotesis candidatas sin tocar codigo. 2) AC8 cura gobernando la
divergencia esperada. 3) dientes con mutante y restauracion por sha. 4) cierre con las hermanas de 16 y 36 funciones.

CRITERIOS: el control pierde con el generador de 6b02532 por la razon nombrada, gana con el curado, la asercion
vieja queda intacta y la banda de IDs divergentes se mide contra el HEAD de esta sesion.

RESTRICCIONES: sin editar build_lesson_index.py en esta fase, sin re-ancorar el control a HEAD, sin AGENTS ni
VERSION, sin commit salvo instruccion literal, sin iniciar C.

```
