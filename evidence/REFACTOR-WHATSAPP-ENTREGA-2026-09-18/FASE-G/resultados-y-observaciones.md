# FASE-G — Resultados, delta PRE/POST y observaciones medidas

**Sesión:** G (implementación) · **Fecha:** 2026-09-20 · **HEAD de partida:** `d7ff932`
**AC que cierra:** AC7 (verificador AST de cableado) y AC16 (retiro del contrato muerto),
con AC15 (par PRE/POST + mutaciones) como contrato de evidencia.

## 1. Qué se construyó

| Artefacto | Rol | Medida |
|---|---|---|
| `scripts/validate_wiring.py` | Verificador AST: descubre población sin lista fija, exige señales por productor, publica límites | 905 líneas; ~10,8 s por corrida completa |
| `.opencode/wiring_report.json` | Artefacto legible por humano/VERIFY (AC7) | 3.421 líneas JSON; `git_sha` anotado |
| `tests/test_validate_wiring.py` | Suite propia: rojos por guard, no por sintaxis | 464 líneas; **18 funciones canónicas** |
| `scripts/run_all_validations.py` | Check 11 registrado **dentro del modo rápido** | +90/−21 líneas (renumeración + `_check_wiring`) |
| `modules/assessment_builder.py` + `main.py` + 2 tests | F-D': contrato muerto retirado | verbatim en `inventario-callers.md` §3 |

## 2. Cobertura real medida por el propio verificador

```
611 archivos en alcance · 169 llamadas descubiertas · 70 gobernadas
  GOBERNADA_CONFORME          14   (6 de ellas productivas)
  GOBERNADA_CON_OMISION        3   (las tres del orquestador, con dueño FASE-B/AC1)
  EXCLUIDA_POR_CLASE          43   (13 productivas: homónimos de `validate`)
  EXCLUIDA_POR_CLASE_NO_GOB.  31
  TEST_EXENTO_DE_SENAL        53
  RECEPTOR_NO_RESUELTO        25   ·  de las cuales en PRODUCCION: 0
```

El número que importa es el último: **cero receptores sin resolver fuera de `tests/`**. Es la
única forma honesta de decir «no se me escapó ningún caller productivo», y es una cuenta que
publica el instrumento, no esta prosa. Aun así, el verde **no** prueba ausencia de callers
invisible para el AST (dispatch dinámico, metaprogramación): ver `limites` en el JSON.

## 3. Delta PRE → POST (R2.3, mismo entorno y selección)

| Concepto | PRE (antes de editar) | POST-A (selección **idéntica**) | POST-B (+suite nuevo) |
|---|---|---|---|
| passed | 1.313 | 1.313 | **1.331** |
| failed | 1 | 1 | 1 |
| skipped | 2 | 2 | 2 |
| xfailed / xpassed | 0 / 0 | 0 / 0 | 0 / 0 |
| exit code | 1 | 1 | 1 |
| tiempo | 20,6 s | 14,5 s | 57,5 s |

**Delta explicado:** `passed_post = 1.313 + 18 = 1.331` en POST-B y **+0** en POST-A. Las 18
son las funciones canónicas del único archivo de test añadido por G
(`tests/test_validate_wiring.py`). `skipped` idéntico. **0 regresiones causadas por la fase.**

Nota de unidad (R2.3: decir qué mide cada cifra): **función canónica** =
`grep -cE "^\s*def test_"` sobre el fuente; **caso recolectado** = lo que cuenta pytest. En
este archivo ambas coinciden en 18 (sin parametrizaciones). El par 4.246 → **4.264** del repo
se midió con el método canónico del repo sobre `tests/` entero.

Corrección medida durante el cierre: el primer POST-B se tomó con 17 funciones y reportó
1.330; se re-midió con el archivo completo (1.331) en lugar de ajustar la prosa. La
diferencia de 1 no era parametrización ni recolección: **la función 18
(`test_una_politica_que_declara_un_simbolo_inexistente_hace_rojo`) se escribió después de
ese POST**, al descubrir con el propio instrumento que la política había declarado un símbolo
que los fixtures no definían.

**El fallo preexistente, con par medido (no con la cifra histórica de AGENTS.md):**

```
FAILED tests/test_validate_lesson_capitalization.py::
  test_medido_contra_el_predecesor_entra_en_alcance_y_su_forma_es_conforme[2026-09-11-TRIBUNAL-ENFORCEMENT-OBS-2026-09-11]
```

Causa raíz medida: `clasificar_planes()` toma los hijos directos de `.opencode/plans/`, y
`TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` fue movido a `Archives/` en el commit `9c4a001`
(RELEASE v4.77.0) — por tanto ya no está en `alcance`, mientras el test exige estarlo.
**No es de G** (está rojo en PRE, con el árbol intacto) y **G no lo toca**: es un contract test
del verificador de capitalización cuyo dueño es el mismo tramo de deuda que R2.5/R2.10. Queda
registrado con dueño en `10-analisis-post-implementacion.md`. G no añadió exclusiones ni cambió
expectativas para ocultarlo: figura igual en PRE y en los dos POST.

## 4. Mutaciones (R2.8 / AC15) — 7 de 7 con rojo por el guard

Instrumento: `temp/mutaciones_fase_g.py` (fuente archivada en `mutation_report.json`). Cada
mutación debilita **el guard real** sobre el archivo vivo, restaura byte a byte y verifica
sha256; un rojo por `SyntaxError`/`ImportError` se marca inválido, no cuenta.

| ID | Guard debilitado | Resultado |
|---|---|---|
| M1 | vaciar la política `GOBERNADOS` | rojo por `assert 0 == 1` en el test del caller nuevo ✓ |
| M2 | aceptar `**kwargs` opacos | rojo: `KWARGS_OPACOS` deja de dispararse ✓ |
| M3 | gobernar por **nombre** de método en vez de clase | rojo: denuncia el homónimo `PrecisionValidator.validate` del fixture ✓ |
| M4 | quitar el diente a `EXCEPCION_VAGA` | rojo: la excepción huérfana pasa a ser ruido inofensivo ✓ |
| M5 | re-introducir `whatsapp_validation` en la firma | rojo por AC16 en el árbol vivo ✓ |
| M6 | desactivar la detección de argumento prohibido | rojo: `AssertionError: []` (la violación desaparece) ✓ |
| M7 | des-regular el check del modo rápido | rojo por coherencia de ordinales (`1..11` vs `[1..10]`) ✓ |

`con_rojo_del_guard = 7`, `asercion_esperada_en_el_rojo = 7`, `worktree_restaurado = true`.

## 5. Cinco observaciones medidas (ninguna inferida de la prosa del plan)

1. **La divergencia F-A' no es una línea, son tres.** El AST encontró
   `v4_asset_orchestrator.py` omitiendo `whatsapp_html_detected` en `:286` (`detect_pains`),
   `:309` y `:447` (dos `CoherenceValidator.validate`). El maestro §1 describe solo la primera.
   Consecuencia para B: arreglar solo la 286 deja dos rojos y convierte dos excepciones en
   `EXCEPCION_VAGA`. El verificador ya lo impide.

2. **Gobernar `validate` por nombre habría sido un falso verde colectivo: 71 de las 74
   llamadas excluidas se llaman `validate`.** Medido sobre el reporte:
   `EXCLUIDA_POR_CLASE` + `EXCLUIDA_POR_CLASE_NO_GOBERNADA` = **74** registros, de los cuales
   **71** invocan a un método llamado `validate` cuyo receptor resuelve a una clase que no es
   `CoherenceValidator` (`NoDefaultsValidator` 29, `FinancialInputsContract` 18,
   `PrecisionValidator` 6, `PlanValidator` 4, `ContentValidator` 3, `EnvValidator` 1, y
   funciones de módulo como `validate_opencode_refs` 7). En producción son **15** las
   exclusiones por homónimo. Sin resolución del tipo del receptor, esas 71 habrían entrado a
   la población gobernada y el check habría sido inusable — o lo habrían vaciado a fuerza de
   excepciones. La mutación M3 lo demostró por el camino inverso.
3. **El verificador tuvo un hueco de cobertura propio, y tuvo que medirlo contra sí mismo.**
   La primera versión del resolutor de receptores solo miraba sentencias directas del cuerpo de
   una función. Reconstruido ese "antes" (sustituyendo el recorrido por uno de un solo nivel,
   en memoria, sobre el árbol real): **8 receptores productivos sin resolver**,
   entre ellos `v4_diagnostic_generator.py:3300` (`pain_mapper = PainSolutionMapper()` dentro
   de un `try`) — un caller que **sí** propaga la señal y que habría quedado fuera de la
   población gobernada sin que ningún verde lo advirtiera. Tras descender por
   `try`/`if`/`with`: **0 en producción**, gobernadas 67 → 70, conformes 11 → 14. Lo que lo
   convirtió en test y no en anécdota es `cobertura.receptores_no_resueltos_en_produccion`,
   que hoy está asertado en 0: un ✅ general no habría probado nada de esto.
4. **El contrato muerto estaba tan muerto que sus propios tests le pasaban `None`.** Los dos
   consumidores de `with_validation` en `tests/test_assessment_builder.py` pasan `None` como
   segundo argumento, y el cuerpo del método nunca lo leyó. Y su dato upstream sí está vivo:
   ocho líneas de `main.py` consumen `whatsapp_validation` para construir los
   `ValidatedField` que alimentan `validation_summary`. G retiró el parámetro, no la variable.

5. **AÑADIDO durante el cierre (no estaba en el diseño inicial):** el registro de excepciones
   sin diente sería un allowlist. Medido: una excepción que ya no ampara nada produce
   `EXCEPCION_VAGA` y **rompe** el check (M4 lo demuestra), y `--ignore-known` deja ver los 4
   hallazgos completos del árbol. Sin estos dos mecanismos, la única salida de un hallazgo
   molesto habría sido «anadir una excepción y olvidarse», que es la forma en que un verificador
   se convierte en decorative.

## 5bis. Sexta observación, nacida del propio cierre (medida, no prevista)

**Los dos escritores de `REGISTRY.md` divergen desde que `VERSION.yaml` se ancló.** Al registrar la
fase, `log_phase_completion.py` estampó `> **Ultima actualizacion:** 2026-09-20` (hoy) y el quick
volvió a rojo: `Version Sync` — ahora **10/11**, no 9/10 — porque `sync_versions.py`, tras el ancla
que FASE-A puso en `d7ff932`, compara esa cabecera contra `date: 2026-09-19` y no contra el reloj.
Medido leyéndolos, no infiriéndolo del rojo: `sync_versions.py --check` dio **6 OK y 1 FAIL**
(`registry_last_update`), y el único archivo con diferencia real era `REGISTRY.md`.

Es `L-ENT.4` otra vez, con mecanismo distinto: el arreglo de A cerró la caducidad a medianoche y
abrió una **fricción entre escritores** — `log_phase_completion` escribe «cuándo se registró»,
`sync_versions` exige «qué fecha de release está anclada». Cada fase intermedia de este plan va a
re-abrir ese rojo, y las tres soluciones son distintas en coste:

1. **Lo que hizo G**: `sync_versions.py --rule registry_last_update`, es decir **el escritor
   oficial**, acotado a la regla que estaba roja. Resultado medido: 7/7 in sync y `git diff --stat`
   sobre `REGISTRY.md` = 30 inserciones / 1 borrado — las 30 son la entrada de FASE-G; la 1
   borrada es esa línea de fecha. **Sin edición manual y sin tocar `AGENTS.md` ni `.cursorrules`**
   (configuración central, prohibida sin instrucción expresa).
2. Lo que **no** hizo G: editar la fecha a mano (curaría el síntoma hasta la próxima fase) ni
   modificar `_check_version_sync` para absorber el rojo (prohibido por el contrato).
3. Lo que **no** le toca a G: arreglar el escritor. `log_phase_completion.py` debería, o bien
   escribir el valor que `sync_versions` valida, o dejar constancia de la fecha real de registro en
   otro campo. **Dueño: FASE-RELEASE / operador**, con la nota de que la fecha real de la fase ya
   está publicada donde importa — el encabezado `## FASE-G - 2026-09-20` de la propia entrada.

Queda como deuda registrada con dueño y con el comando de reproducción exacto, no como
anecdota: `python scripts/log_phase_completion.py … && python scripts/run_all_validations.py --quick`
→ rojo esperable; `python scripts/sync_versions.py --rule registry_last_update` → 7/7.

## 6. AC7 y AC16: estado declarado con su artefacto

| AC | Verde | Rojo | Artefacto y clave |
|---|---|---|---|
| AC7 | ✅ check 11 del quick en verde por cobertura (14 conformes, 3 amparadas con dueño, 0 huecos productivos) | ✅ caller nuevo en archivo nuevo; ✅ `**kwargs` opacos; ✅ alias y `self`; ✅ homónimos excluidos; **y ✅ sobre la divergencia actual tal como estaba antes de corregirla** | `.opencode/wiring_report.json`: `poblacion`, `cobertura`, `politica`, `excepciones_aplicadas`, `limites` |
| AC16 | ✅ firma leída por el verificador: `with_validation(self, validation_summary)`; 3 callers actualizados; dato upstream intacto | ✅ caller con la firma vieja (`ARGUMENTO_PROHIBIDO`); ✅ re-introducirlo en la firma (`CONTRATO_MUERTO_VIGENTE`) | mismo reporte, clave `politica["AssessmentBuilder.with_validation"].firma_real` + `inventario-callers.md` §3 |
| AC15 | ✅ par PRE/POST misma selección y entorno, exit codes y conteos | ✅ 7 mutaciones con causa nombrada | `tests_baseline_pre.txt`, `tests_baseline_post.txt`, `mutation_report.json` |

**Verde que no se declara alcanzado:** AC7 no certifica que no existan callers invisibles para
el AST, y AC16 no certifica el cierre de AC20 (propiedad de FASE-0, no tocada) ni goberna las
tablas de promesas (F-F/B). Ambos límites están en `limites` del JSON, no solo en esta prosa.

## 7. Límites de esta fase, dichos en claro

- El check vive en `run_all_validations.py --quick`. **No** está en el hook de pre-commit
  (`scripts/git_hooks/pre-commit`, 7 checks, que además no invoca `run_all_validations.py` —
  fila `L-V3.1`). G no tocó hooks: prohibido por el contrato de fases intermedias.
- Tres hallazgos quedan **abiertos con dueño** (FASE-B, AC1). G no corrigió el producto:
  gobernar sin ability de corregir es el diseño, y la corrección es de la fase dueña.
- No se tocaron `TribunalJudge._compute_verdict`, flags de bloqueo, umbrales 0.8/0.9,
  `write/publish/suppress`, `domain_gates.py`, ni la serialización del acta (AC20).
- No se ejecutó `main.py v4complete`, ni red, ni scraping. Contador **0/1**.
- FASE-0, B y H son otras sesiones (R1).
