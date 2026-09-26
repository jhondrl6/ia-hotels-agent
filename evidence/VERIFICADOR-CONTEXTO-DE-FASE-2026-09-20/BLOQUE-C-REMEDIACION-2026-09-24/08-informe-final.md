# 08 — Informe final: remediación del bloque C y registro de cierre de la orden 2026-09-22

Sesión documental única, 2026-09-24, sobre `da382b1` con el árbol de B y C sin commitear.
Sin commit, sin push, sin red, sin QMind, sin SDKs, sin piloto y sin reparación de código.

---

## 1. Veredicto de la remediación

**Las tres, REMEDIADAS.** El texto falso se conservó en los tres casos y se anotó con `⟦…⟧` (fecha y
causa), copiando la forma de los dos precedentes del árbol (`06-checklist` ⟦E5⟧ y
`10-analisis` «Contrato de C cerrado el 2026-09-23»), que se leyeron antes de escribir.

| | Archivo | Veredicto | Texto anotado (literal, releído desde disco) |
|---|---|---|---|
| **B1** | `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/README.md`, cabecera | **REMEDIADA** | «el bloque C y el piloto FASE-C no lo están. ⟦**Vencido en parte el 2026-09-24 y rectificado el 2026-09-24 al medirlo**: de esta frase queda en pie solo la segunda mitad — **el piloto FASE-C sí sigue sin autorización**. El **bloque C** … **sí está autorizado y ejecutado desde el 2026-09-24** … **Y eso no es FASE-C** … ⟧» |
| **B2** | `…/06-checklist-implementacion.md`, cabecera | **REMEDIADA** | mismo bloque literal, insertado en la misma frase de la cabecera |
| **B3** | `evidence/…/BLOQUE-C-ENMIENDAS-2026-09-24/02-resultados-bloque-c.md`, renglón JEV de §1 | **REMEDIADA** | «8 de los 11 campos del piloto no están en la costura⟦**Cifra vencida, re-medida el 2026-09-24 y conservada aquí como lo que se dijo, no como estado vigente**: el «8» no reproduce ninguno de los dos métodos … Por **nombre literal** faltan **10 de los 11** … Por **identidad semántica declarada** … faltan **6 de los 11**, y esa es la cifra vigente … Por eso **ese README no se edita**. … ⟧» |

El «8» **no se sobrescribió**. La cifra vigente es **6**, y no la fijó esta sesión: la publicaba desde
antes el consumidor del contrato, `EVALUACION-JEV-TYPESAFE-2026-09-21/README.md`.

---

## 2. Re-emisión del veredicto de C contra el criterio literal de §4.C

Criterio: *«Declarar C CONCLUIDO solo si cada renglón de §4.C queda conciliado y verificado sin
decisiones pendientes necesarias; de lo contrario "C NO CONCLUIDO, con brecha exacta, archivo afectado y
decisión mínima"»*. Cada comprobación es **de esta sesión**, no heredada del expediente de C.

**Re-emisión: en el momento en que C se declaró CONCLUIDO el criterio no estaba cumplido — tres renglones
tenían brecha. Corregidas las tres, la parte documental de C queda CONCLUIDO; la orden no, porque sigue
el piloto.** Lo que sigue no reescribe el veredicto de C: lo anota.

| Renglón | Comprobación propia de esta sesión | Estado al cerrar C (reemitido) | Estado hoy |
|---|---|---|---|
| **CONTEXTO/C** | Leída la costura por AST: `RespuestaNoul.__slots__ = ("pregunta_id","probabilidad_si")`, `CAMPOS_POR_TIPO["noul"] = ("probabilidad_si",)` y su `to_dict` publica `confidence=None` con motivo → E1/E2 reafirmadas contra las formas reales. Y `ls scripts/triage_lesson_relevance.py` → **no existe**, así que ninguna enmienda se implementó | **NO CONCLUIDO.** Brecha: la cabecera del plan y la del checklist afirmaban que el bloque C no estaba autorizado, contradichas por el propio README más abajo y **sin anotación** (decisión mínima: anotar las dos cabeceras, archivo: `README.md` y `06-checklist-implementacion.md`) | **CONCLUIDO (documental)** tras B1/B2. Ejecución: **pendiente propia**, con mandato |
| **CONTEXTO/D** | `grep` de los tres sumandos en `04-contrato-ejecucion.md`: `workflow_obligatorio` 1, `coste_de_generacion` 1, `pack_consumido` 1 | CONCLUIDO (documental) | igual; la medición la hace FASE-D |
| **CONTEXTO/RELEASE** | `grep -c PENDIENTE-AUTORIZACION` en `05-prompt-inicio-sesion-fase-RELEASE.md` = **8**; y la prohibición de reparación de código declarada en el contrato §Dos momentos | CONCLUIDO (documental) | igual; el momento remoto sigue **bloqueado por permiso**, no por contrato |
| **WHATSAPP** | `06-checklist-implementacion.md`: B «CERRADA CON DEUDA REGISTRADA … (AC5 → dueño C-D)» y la fila C con AC5 en su lista; «cinco cortes» presente en contrato (2) y README (1) | CONCLUIDO (documental) | igual; pipeline y `DOMAIN_PRIMER` no ejecutados |
| **JEV** | La tabla existe/falta releída; los once campos extraídos por instrumento de «Contrato requerido para el piloto» y los seis del gap del README verificados uno a uno; protegido `dependencias-fases.md` con sha `b55670d7…` y numstat `18 0` | **NO CONCLUIDO.** Brecha: el resumen único de C decía **8** donde su propio consumidor decía **6** (archivo: `02-resultados-bloque-c.md`, renglón JEV; decisión mínima: anotar con los dos métodos, no editar el README de JEV) | **CONCLUIDO (documental)** tras B3. Sigue **decisión humana** el revisor de la muestra y la salida del gap |
| **ESCRITURA-QMIND** | AC6 partido en **AC6-entrega** / **AC6-aceptación** en maestro §6 y README; el arranque de `05-prompt-inicio-sesion.md` **no** trae operación remota: `fetch_source_titles()` está en la tabla «Re-medir **en el momento B**» con la nota «es una llamada remota y no corre en esta sesión» | CONCLUIDO (documental) | igual; dependencia externa al permiso y presupuesto |

---

## 3. Registro de cierre de la orden

La tabla completa está en `06-registro-cierre-orden.md`, con los seis renglones pedidos (piloto; deudas
D2/D3-parcial/D6/D7/S10/D8-D9/D10; momento remoto; FASE-D+RELEASE, WHATSAPP C y JEV A→B→C separando
dependencia técnica / gobernanza / aceptabilidad semántica; árbol sin commitear; textos centrales) y con
la línea explícita: **ejecutar todo eso tampoco cierra D2, D3 completa, D6, D7 ni S10**.

---

## 4. Hallazgos no remediados

Conforme a §2.2, una cuarta brecha **no se edita: se reporta**.

1. **Un antecedente del mandato está vencido en un símbolo.** §1.2 dice «La costura real es
   `class ResultadoCorrida`». `ResultadoCorrida` **no existe** en el árbol (barrido del repo: 0
   coincidencias, con la de `ResultadoEvaluacion` como control positivo en el mismo grep). La costura es
   `class ResultadoEvaluacion` en `scripts/decision_client.py`; sus `__slots__` sí son los siete que
   enumeraba el mandato, y las dos cifras (10 y 6) se reprodujeron. **Decisión mínima**: corregir el
   símbolo en el mandato; **no se tocó ningún archivo por esto**, porque ningún archivo del repo arrastra
   el nombre equivocado.
2. **El `--check` del índice PRE dio 0, no 1.** §6/§7 esperaban «PRE=1 / POST=0». Medido: estaba fresco,
   y la causa es verificable — el par `LECCIONES-INDEX.md` / `lecciones_index.json` quedó
   **byte-idéntico** PRE y POST (`6197c224…` y `13de1af8…`), porque lo que esta sesión insertó no define
   ni retira ningún ID de lección. **Antecedente vencido, reportado y no ajustado.** El regenerador se
   ejecutó igualmente una vez, como permitía el mandato.
3. **Una fila de tabla con columnas desiguales, preexistente, en `VERIFICADOR-CONTEXTO/README.md`.** El
   bloque de 11 filas, con columnas desiguales, ya medido antes y después de esta sesión: en la línea 189
   **antes** de esta sesión y en la 201 **después** (mismo bloque, desplazado por mis 12 líneas). No la
   introduje y C ya declaró nueve filas así como condición preexistente. **Decisión mínima**: corregirla
   en la fase que posea ese README, no por arrastre documental.
4. **Límite de precisión del propio barrido, declarado.** La etapa 1 es co-ocurrencia, no análisis de
   dependencia: de las 8 coincidencias de la clase (c), **6** (`c-0`) mencionan «bloque C» junto a una
   negación que no le predica nada (p. ej. la fila P2 de `JEV/01-plan-maestro.md`, «no existen
   `scripts/decision_client.py`…»). Solo **2** (`c-1`) son el estado vencido. El instrumento publica los
   dos sub-conteos y su suma; no disfraza la imprecisión con un umbral.

---

## 5. Comprobaciones

| Comando exacto | `EXIT=` | Salida relevante | Instrumento que la sostiene |
|---|---|---|---|
| `build_lesson_index.py --check` (PRE) | **0** | `Índice de lecciones fresco (332 IDs)` | §7 · hallazgo 2 |
| `build_lesson_index.py` (una vez) | 0 | `332 IDs definidos + 51 sin definición (16 análisis, 417 .md citados)` | M9: el escritor autorizado, 1 sola pasada (contado en `07b`) |
| `build_lesson_index.py --check` (POST) | 0 | fresco, 332 IDs | M6: sha del par idéntico PRE/POST |
| `validate_plan_citations.py` | 0 | `743 citas historicas, 0 nuevas y 0 crecimientos (79 archivos)` | umbral de parada: **0 nuevas** ✓ |
| `validate_lesson_capitalization.py` | 0 | forma y trazabilidad; declara que **no** verifica pertinencia | — |
| `validate_document_integration.py` | 0 | comprobaciones cruzadas en verde | — |
| `validate_opencode_refs.py` | 0 | todas las referencias existen | sin `--fix` (`07b`) |
| `validate_plan_closure.py` | 0 | ningún plan vivo declara cierre con filas pendientes | umbral de parada: verde ✓ |
| `validate_governance_numbers.py --report` (sin destino) | 0 | `# no se escribio ningun archivo: pase --report RUTA…` | S12 + M9 |
| `run_all_validations.py --quick --check` | 0 | `TOTAL: 11/11 validations passed`; cableado **183 llamadas / 1326 archivos / 0 violaciones / 30 receptores no resueltos** | umbral 11/11 ✓ y **población 1326** ✓ con los instrumentos ya en `evidence/` |
| `git diff --check` | 0 | sin errores; **5** avisos `CRLF will be replaced by LF` (los esperados y benignos, de archivos que esta sesión no tocó) | — |
| *(aviso declarado)* | — | en `04-validaciones.txt` la línea `CapitalizaciÃ³n del Paso 0 …` sale con **mojibake de consola**: es la salida real del subprocess bajo cp1252, **conservada tal cual** y no «arreglada» (M4). La decisión no se tomó leyendo esa cadena: la sostienen el `EXIT=0` y la línea `TOTAL: 11/11` | M4 |
| `pytest -q` sobre las 6 rutas de C | **1** | `1 failed, 172 passed in 26.68s` | el único rojo es **la misma firma** que declaró C: `tests/test_validate_lesson_capitalization.py::test_medido_contra_el_predecesor_entra_en_alcance_y_su_forma_es_conforme[2026-09-11-TRIBUNAL-ENFORCEMENT-OBS-2026-09-11]`, causa `9c4a001` archivó ese plan y `clasificar_planes` solo mira hijos directos de `.opencode/plans/`. **Se re-declara con dueño, no se arregla ni se tapa. Cero rojos nuevos** |
| `barrido_autorizaciones.py` PRE → POST | 0 → 0 | 15 coincidencias en ambas; `(a) 0 · (b) 7 → 9 · (c) 8 → 6`, con `c-1: 2 → 0` y `b-1: 2 → 4`; **suma 0+7+8 = 15 y 0+9+6 = 15, cierra** | M1 control positivo en cada pasada; M2 normalización NFD sin caracteres de marca (función `norm()` publicada en el instrumento); M3 dos etapas con la ceguera del filtro estilo C declarada (1 casada / 14 no) y las cópulas buscadas aparte |
| `campos_piloto.py` | 0 | exigidos 11; ausentes **10** por literal y **6** por semántico; costura detectada por AST como `ResultadoEvaluacion` | M7: los 6 coinciden con los que nombra `JEV/README.md` |
| `huellas.py compare` 56 rutas | 0 | 3 cambiados, 53 idénticos, 0 altas, 0 bajas | M6 |
| sha256 `JEV/dependencias-fases.md` | 0 | `b55670d7…` idéntico y numstat `18 0`; `Archives/` y los dos expedientes de B: **0 modificados** | M6, comparado por diccionarios en Python |

---

## 6. Qué se tocó y qué no

**Tocado por esta sesión (3 archivos de contenido):** las dos cabeceras del plan CONTEXTO y el renglón JEV
del expediente de C. Numstat contra HEAD: `README.md` `44 23` → **`56 23`** y
`06-checklist-implementacion.md` `54 17` → **`66 17`** — doce líneas añadidas en cada uno y
**cero supresiones nuevas**: las 23 y las 17 que el árbol ya traía sin commitear no se movieron. El
expediente de C está sin trackear, así que su delta lo midió difflib (190 → 190 líneas, 1 hunk).

**Rutas nuevas, justificadas una por una** (todas dentro de `evidence/…/BLOQUE-C-REMEDIACION-2026-09-24/`,
que es mi propio expediente y está excluido del escáner de cableado y del inventario de citas):
`00-arbol-inicial.txt` (§6), `01-huellas-pre.txt` + `01b-m6-pre.txt` (M6),
`02-barrido-reparado.txt` (M1-M3), `03a-aplicacion.txt` + `03b-verificacion-m5.txt` +
`03-rectificaciones.md` (§6), `04-validaciones.txt` (§6), `05-indice-lecciones.txt` (§6),
`06-registro-cierre-orden.md` (§6), `07a-huellas-post-raw.txt` + `07-huellas-post.txt` +
`07b-fronteras.txt` + `07c-huellas-post-cierre.txt` + `07c-compare-cierre.txt` (§6),
`08-informe-final.md` (§6), `antes/` con las tres copias congeladas (el
mecanismo que hace medible «el resto del archivo no se movió» y lo que permitió revertir mi propio error
de EOL), `textos/` con los cuatro fragmentos `b12-viejo` / `b12-nuevo` / `b3-viejo` / `b3-nuevo` que el
aplicador consume (para que la inserción sea reproducible y no quede encerrada en mi cadena de
herramientas), y `instrumentos/` con `huellas.py`, `campos_piloto.py`, `barrido_autorizaciones.py`,
`aplicador.py`, `verifica_edicion.py`, `fronteras.py` y `pasada_siete.sh` (M9: los instrumentos viven
aquí, no en `tmp_test/`, y la población de cableado se re-midió en **1326** con ellos ya sobre el disco).
El `__pycache__` que generó `py_compile` se retiró: es ruido mío, no evidencia.
**Re-medición de cierre**: repetida la comparación M6 tras escribir todo el expediente, el manifiesto de
56 rutas sigue dando **3 cambiados, 53 idénticos, 0 altas, 0 bajas** (`07c-*`), `git diff --check` en 0,
quick **11/11** y cableado en **1326**, y `HEAD` en `da382b1`.

**Trabajo ajeno sin commitear: no se tocó, no se restauró y no se atribuye a esta sesión.** Las 54 rutas
modificadas y las 8 sin trackear que `git status --porcelain` contaba al abrir siguen ahí con su autoría
propia; `00-arbol-inicial.txt` las fotografió antes de mi primera edición y `07-huellas-post.txt` demuestra
por sha que solo 3 rutas cambiaron. Los dos expedientes de B y `.opencode/plans/Archives/` dan **0
modificados**. El archivo protegido `JEV/dependencias-fases.md` sigue en `b55670d7…` con `18 0`.
La única restauración que hubo fue **sobre mis dos propios objetivos**, del estado que yo mismo había
deteriorado con el error de CRLF, y se hizo desde mi snapshot, no desde `HEAD` ni con `stash`/`checkout`.

---

## 7. Fronteras respetadas

Cada una con su comprobación (no con mi palabra): `07b-fronteras.txt`.

- **No commit** → `git rev-parse --short HEAD` = `da382b1` al abrir y al cerrar; `git rev-list --count
  da382b1..HEAD` = **0**. **No push / no red** → 0 comandos ejecutados con URL, `--upload` o
  `fetch_source_titles`; el único hallazgo del patrón son **menciones en prosa** de mi propio registro,
  y el control positivo sobre `JEV/01-plan-maestro.md` demuestra que el patrón casa de verdad.
  **No QMind, no import de SDKs, no piloto FASE-C, ninguna fase de los cuatro planes** → no ejecuté ningún
  prompt de fase; `scripts/triage_lesson_relevance.py` y `scripts/build_phase_briefing.py` siguen sin
  existir (así se declara, no así se arregla).
- **Flags que escriben, prohibidos**: `--fix` **0**, `--update-baseline` **0**, `--write-baseline` **0**
  usos en las líneas de comando ejecutadas; `--report` **sin destino** (la línea termina en `--report`, y
  el propio informe imprime «no se escribio ningun archivo»).
- `run_all_validations.py` solo con `--quick --check` → **0** invocaciones con otros flags.
- `build_lesson_index.py` sin `--check` **exactamente 1 vez**, entre dos `--check`, sobre el árbol ya
  editado.
- Todos los comandos con `./venv/Scripts/python.exe` y `PYTHONIOENCODING=utf-8`.
- **Ningún archivo fuera del alcance cerrado de §2.2**: `huellas.py compare` sobre 56 rutas da 3
  cambiadas y 53 idénticas. No creé IDs de lección, no toqué baselines, prompts de fases cerradas,
  `Archives/`, `DOMAIN_PRIMER.md`, `AGENTS.md`, `.cursorrules`, `.agents/**`, `scripts/**` ni config; no
  añadí citas de plan (`0 nuevas, 0 crecimientos`).

---

## 8. Deudas y decisiones pendientes del operador

1. **Autorizar o no el piloto FASE-C de CONTEXTO** — única `[ ]` de §6, y lo único que separa el estado
   actual del cierre de la orden. Su contrato está reconciliado; `triage_lesson_relevance.py` no existe
   porque es lo que esa fase produce.
2. **Presupuesto y permiso del momento remoto** (D8 consulta Q7, D9 `--upload`, AC6-aceptación de QMind).
   Verificado: AC6 ya está partido y el arranque del prompt de QMind no manda ninguna operación remota.
3. **Decisión sobre el gap de contrato de JEV**, con las dos salidas y sus costes: extender la costura del
   hermano de forma aditiva y compatible, o producir los seis campos en el runner propio de JEV.
   Prohibido por el plan: segunda costura, duplicar `decision_client.py`, recortar AC1/AC2.
4. **Revisor humano y umbrales de la muestra JEV** para pasarla de BORRADOR a congelada.
5. **D2** (abirla o no, y con ella la renumeración 11→12 que toca AC16 y pins de `tests/`), **D3** en su
   parte completa, **D6** (dormida; su disparador es D7), **D7** (proveedor real), **S10** (dónde vivirá
   el `import` del SDK), **D10** (re-leer la interfaz del write-back al cerrar).
6. **Commit y push del árbol** — acción posterior, separada y opcional; no es el quinto corte ni condición
   de ninguno de los cinco.
7. **Alinear o no `AGENTS.md` y la tabla de `docs/CONTRIBUTING.md` sobre `DOMAIN_PRIMER`**, que se
   declaran desincronizados y no se tocan.

**Y la línea que el mandato exige explícita:** ejecutar todo lo anterior **tampoco cierra las deudas
externas**. Aun con piloto, momento remoto y los tres tramos cerrados, **D2, D3 completa, D6, D7 y S10
siguen abiertas**.

No ofrezco abrir la fase siguiente: la línea base que esta sesión acaba de medir —`c-1 = 0`, índice
byte-idéntico, cableado en 1326, 11/11, un rojo ajeno con dueño— es justamente la que esa fase movería.
