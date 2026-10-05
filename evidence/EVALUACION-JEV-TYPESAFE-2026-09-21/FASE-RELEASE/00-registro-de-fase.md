# 00 · Registro de fase — FASE-RELEASE (EVALUACION-JEV-TYPESAFE-2026-09-21)

Sesión de **certificación con instrumentos**, no de redacción de un cierre. Mandato ejecutado: el de
FASE-RELEASE emitido el 2026-10-05, que vence al esqueleto `05-prompt-inicio-sesion-fase-RELEASE.md`
sin borrarlo. Rol: auditor-verificador con poder de medir y de rechazar un verde, sin poder de decidir
la adopción ni de escribir sobre el hermano.

**Estado terminal legítimo al que se llega: checkpoint documental con la deuda visible.** No es un plan
cerrado con evidencia plena, porque C cerró `run_status=INCOMPLETO / decision=null` y el operador no ha
emitido etiqueta de adopción en esta sesión. Tampoco es un cierre por prosa, que sería el fallo del
mandato.

---

## 0. Arranque, medido y no copiado (crudo `00-`)

| Aspecto | Comando | Valor medido el 2026-10-05 |
|---|---|---|
| Tip | `git rev-parse HEAD` | `ced8715ae8137a32d9802a2270c790b558ab419f` |
| Árbol | `git status --porcelain` | `?? evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-RELEASE/` — y nada más |
| Paridad | `git rev-list --left-right --count origin/master...HEAD` | **0 0** |
| El servidor | `git ls-remote origin refs/heads/master` | `ced8715…` = HEAD |
| Rango sin L3 | `git rev-list --count 0c79e9c..HEAD` | **15** |
| Rama | `git rev-parse --abbrev-ref HEAD` | `master` |

Contra la §3 del mandato: **sin desviación** en tip, paridad, rango y árbol. Las dos desviaciones que
esta sesión sí produce sobre su propio arranque se declaran aquí y no se corrigen a escondidas:

- **Deriva del instrumento de esta hoja (primera captura de `00-`).** La primera vez que se corrió el
  bloque, la línea de `git status --porcelain` salió **vacía** con la carpeta `FASE-RELEASE/` ya poblada
  por los brutos `02-`, `03-` y `04-`; eso habría publicado un «árbol limpio» falso. Re-ejecutado el
  bloque en stdout y redirigido a archivo, la salida con `??` se reprodujo y la captura vacía no volvió
  a salir. Se re-midió y se reescribió `00-` en lugar de publicar aquella línea.
- **Falso negativo del propio barrido (bruto `16-`).** El primer patrón de rangos pedía
  `0c79e9c\.\.\d{7}`; un sha corto no son siete dígitos, así que la fila 16 del `33-registro` daba «0
  rangos» teniendo dos. Corregido a `[0-9a-f]{7}`, la re-medida está en `16-`. Lección: un conteo con
  patrón mal formado es peor que un conteo ausente (se anota como H16 en §7).

---

## 1. Re-emisión mecánica: `report` y `decide` sobre los registros versionados de C

Banderas del §11 del registro de FASE-B2, cambiando solo `--out` / `--out-dir` hacia esta carpeta y
`--fecha 2026-10-05` (crudos `02-` y `03-`).

| Modo | Comando | EXIT | Artefacto |
|---|---|---|---|
| `report` | `… evaluate_jev_pilot.py report --respuestas …/FASE-C/respuestas.jsonl --etiquetas …/etiquetas.json --muestra …/muestra.json --protocolo …/protocolo.json --out …/FASE-RELEASE/informe_comparativa.json --fecha 2026-10-05` | **0** | `informe_comparativa.json` |
| `decide` | `… evaluate_jev_pilot.py decide --informe …/FASE-RELEASE/informe_comparativa.json --protocolo …/protocolo.json --out-dir …/FASE-RELEASE --fecha 2026-10-05` | **3** (emitido sin decisión) | `decision.json`, `decision.md` |

**Contraste con lo publicado (arnés `04-`, crudo `04-contraste-crudo.txt`).** Se comparan
`sha256_de_los_insumos` y los cocientes, no el archivo entero: el límite declarado en B2 §12 dice que
el bloque `insumos` publica las rutas tal como se pasaron y que `fecha` es la de la invocación.

| Chequeo | Valor medido |
|---|---|
| `sha256_de_los_insumos` B2 vs RELEASE (4 insumos) | **IGUALES** — respuestas `2222023e…`, etiquetas `5da5e8a4…`, muestra `4a8b30c8…`, protocolo `7caed9dc…` |
| Diferencial estructural del informe B2 vs RELEASE, ignorando `fecha` | **0 claves** |
| Diferencial estructural de `decision.json` B2 vs RELEASE, ignorando `fecha` | **0 claves** |
| `decision.md` B2 vs RELEASE | 42 líneas, **1** difiere: `- Fecha:` 2026-10-04 → 2026-10-05 |
| Determinismo (dos corridas `report`, misma invocación) | sha `d980bd97…` en ambas, **idénticas byte a byte** |
| Con otra fecha y rutas absolutas | se mueven **5** claves: `fecha` y las cuatro rutas de `insumos`; `sha256_de_los_insumos` y los cocientes no se mueven |
| `run_status` / `decision` / `transfer_status` vs C | **INCOMPLETO / null / PENDIENTE** en los tres — coincide |
| `cobertura_min` de C vs el emisor de hoy | C: `{capa_fria 0.5, deepseek 0.5, jev 0.5}` · RELEASE: `{capa_fria 0.5, jev 0.5, deepseek 0.5}` — mismos valores |

**Divergencia publicada, no curada:** el informe de C (`FASE-C/informe_comparativa.json`) tiene **otro
schema** — 13 claves con `fase`, `regenerable_desde`, `comando`, `costo_y_cuentas_tres_monedas`,
`hallazgos`, `cambios_requeridos` — y no produce los cuatro cocientes por brazo con denominadores
separados. No es una contradicción: C lo escribió como registro de sesión porque el instrumento no
existía. Su propio `instrumento_de_emision` lo dice literal: «ninguno: `decide` se niega con EXIT 2 … y
`report` ni siquiera está en el parser». **Esa cláusula está vencida desde FASE-B.2 y esta sesión la
re produce por el camino del contrato**: el `decision.json` de esta carpeta imprime
`instrumento_de_emision: scripts/evaluate_jev_pilot.py decide, sobre el informe de … report`.

**Los cuatro cocientes, tal como los emite el instrumento hoy** (brazo por brazo, numerador/denominador):

| Brazo | recuperación | precisión entre propuestas | recall en candidatos | extremo a extremo |
|---|---|---|---|---|
| capa fría | 1/2 = 0.5 | **0/0 = None** (NO-EVALUABLE, no 100 ni 0) | 1/1 = 1.0 | 1/2 = 0.5 |
| jev | 1/2 = 0.5 | 1/1 = 1.0 | 1/1 = 1.0 | 1/2 = 0.5 |
| deepseek | 1/2 = 0.5 | 1/1 = 1.0 | 1/1 = 1.0 | 1/2 = 0.5 |

Latencias publicadas aparte: jev 395.794 ms de respuesta y **48.478 ms de fallo** (`error_kind:
conexion`, `attempts 1`, `estado: no_intentada`, `libera_reserva_como_cero: false`); deepseek 1392.648 y
1133.547 ms. El margen congelado: `diferencia_calculada 0.0` contra umbral 0.25, y
`estado: NO-EVALUABLE` con `denominador_efectivo_de_la_comparacion: 1`.

---

## 2. Cifra por cifra, con su instrumento (AC-R1)

| Magnitud | Comando | Valor | Crudo |
|---|---|---|---|
| Batería del piloto | `./venv/Scripts/python.exe -m pytest tests/quality_gates/jev_pilot -q` | **126 passed**, EXIT 0 | `01-` |
| Batería del protocolo (la de CR-4) | `… -m pytest …/test_jev_pilot_protocolo_check.py -q` | **24 passed**, EXIT 0 | `06-` |
| Dientes del guard real del triaje ajeno | `… -m pytest tests/quality_gates/lesson_relevance -q` | **62 passed**, EXIT 0 | `19-` |
| Funciones `def test_` en `jev_pilot/` | `grep -rE "^[[:space:]]*def test_" tests/quality_gates/jev_pilot --include=*.py \| wc -l` | **111** | `11-` |
| Cifra canónica, árbol de trabajo | `grep -rE "^\s*def test_" tests --include=*.py \| wc -l` | **4835** | `11-` |
| Cifra canónica, commiteada en `ced8715` | `git grep -h -c -E "^\s*def test_" ced8715 -- "tests/*.py"` sumado | **4835** (converge con la del árbol) | `11-` |
| Aislamiento de imports (AC6, pata puerta) | `./venv/Scripts/python.exe scripts/decision_client.py --scan-imports` | **[SIN-HALLAZGOS]** — 0 imports prohibidos fuera de la puerta, población 842/9878 `.py` | `09-` |
| `llm_provider.py` | `git diff -- modules/providers/llm_provider.py` y `git diff --numstat ced8715 -- …` | **vacío** en las dos formas | `10-` |
| Quick gate ANTES de re-publicar derivados | `./venv/Scripts/python.exe scripts/run_all_validations.py --quick` | **12/13, EXIT 1** — el único rojo es `[11/13] Wiring`: el derivado publicado quedó vencido por esta propia hoja (`cobertura.archivos_excluidos_por_rol_versionado: publicado 142 \| fresco 143`; `exclusiones_por_rol.evidence.cantidad_versionada: 130 \| 131`) | `07-` |
| Wiring por separado | `./venv/Scripts/python.exe scripts/validate_wiring.py --check` | **EXIT 3** — «DIVERGE del cálculo en memoria (digest 3141ef38f77c)»; el código 3 no es un rojo de cableado, es falta de publicación | `08-` |
| Write-back QMind (verificación) | `… scripts/validate_qmind_writeback.py --strict` | **[PASS] 13/13 10-analisis archivados ingested**, EXIT 0 | `15-` |
| Frescura QMind | `… scripts/verify_qmind_context_freshness.py --strict` | EXIT **1**, con el detalle de §4 | `12-`, `13-` |

---

## 3. Superficie respetada (AC-R7, control por git y por sha)

`git diff --numstat ced8715` sobre `scripts/`, `tests/`, `config/`, `VERSION.yaml`, `AGENTS.md`,
`.cursorrules`, `muestra.json`, `protocolo.json`, `etiquetas.json` y `FASE-C/`: **vacío en todas**. Lo
único que escribe esta sesión vive en `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-RELEASE/` y, en
el corte documental, lo que producen los writers de la casa (§9). Crudo `05-`.

Shas de disco de los cuatro congelados, que casan con lo publicado por C en su §2 (y no con el blob, que
es otro artefacto por `core.autocrlf=input`):

| Archivo | sha256 disco | sha del blob en `ced8715` |
|---|---|---|
| `muestra.json` | `0107a386ae57…` | `cfda97c919ac…` |
| `etiquetas.json` | `4ffbb120ef94…` | `fc28205933e6…` |
| `protocolo.json` | `140577a06b2315b5…` | `8758e8b20364…` |
| `FASE-C/decision.json` | `0fc9d1e36cbd…` | `cc38fdd167ec…` |

`protocolo.json` disco `140577a06b2315b5…` y blob `8758e8b2…` son **exactamente** las dos formas que FASE-C
publicó en su §2; la re-medición de hoy las reproduce, así que el congelado de C sigue siendo el mismo
archivo byte a byte. Crudos `05-` y `18-`.

---

## 4. QMind: el `[VENCIDO]` no era vencido (deuda B2-4, materializada y medida)

Tres corridas del verificador de frescura, todas `--strict`, en la misma sesión:

| Corrida | `[SIN-DESCARGA]` | Veredicto sobre `CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21.md` | Veredicto sobre `10-analisis-post-implementacion.md` | EXIT |
|---|---|---|---|---|
| 1ª (`12-`) | 4 | **[VENCIDO]** | **[FRESCO]** (`01a10853-6da2…` coincide) | 1 |
| 2ª (`13-`, `--quiet`) | — | (12 problemas, 0 frescos: todas las descargas cayeron) | idem | 1 |
| 3ª (`13-`, completa) | 3 | **[FRESCO]** (`01a0efcc-3297…` coincide) | **[VENCIDO]** | 1 |

Conteo literal que pide el mandato §5.5: en cada corrida el artefacto **con `[SIN-DESCARGA]` salió
`[VENCIDO]`** y el artefacto **descargable salió `[FRESCO]`**. Los dos gobernados tienen fuente que casa
por descarga+sha256 en al menos una corrida. **Conclusión medida: no hay ningún vencido real; hay cuatro
descargas que fallaron con `QMind network request failed` y el instrumento pinta vencido lo fresco que no
pudo bajar** — que es literalmente la deuda B2-4, hoy con su segunda evidencia y no con la de C.

Poblaciones que imprime la corrida: `1 CONTEXT gobernado | 19 excluido(s)`; `1 gobernado (10-analisis) | 0
fuera de alcance`; `notebook iah-cli-lecciones: **57 fuente(s) publicada(s)**`.

`validate_qmind_writeback.py --strict` **[PASS] 13/13, EXIT 0** (`15-`).

**`--upload` no se corrió, y es el punto de este cierre que queda en manos del operador.** Motivos, cada
uno con su fuente: (a) `04-contrato-ejecucion.md` fija que la lectura de QMind «no constituye autorización
para inferencias ni write-back» y el `README` del plan tiene P6 *Write-back a QMind* en **SIN PERMISO**;
(b) el propio `10-analisis` registra el límite del writer: `validate_qmind_writeback.py --upload` fija el
título antiguo e `is_ingested()` decide por nombre del plan, así que **no puede publicar un cierre
actualizado** — por eso el cierre del 2026-09-27 se subió con el CLI de QMind y con título nuevo,
verificado por descarga+sha256 y no por título; (c) QMind no tiene `delete_source`, así que una subida de
más es permanente. Se pide instrucción explícita si se quiere la publicación; sin ella, **AC-R6 queda
PARCIAL con su motivo** y no se presenta el SKIP del writer como publicación.

Y una consecuencia que esta hoja produce y por eso se enuncia: al editar `10-analisis-post-implementacion.md`
en el corte documental, su `sha_disco` va a cambiar y el verificador va a imprimir `VENCIDO` **de verdad**.
§9 publica la corrida posterior a las ediciones para separar el vencido transitorio del vencido real.

---

## 5. Citas vencidas: censo delegado, re-verificación en disco y qué se toca

El único trabajo delegable de la sesión (censo solo-lectura, agente `Explore`) entregó **250 menciones**
en cuatro árboles: 185 en `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/`, 31 en el plan archivado, 18 en
`docs/cobertura-historia.md` y 16 en las filas 16 y 18 del `33-registro-unificado`. El censo entrega
menciones, no veredictos; las que gobiernan decisiones de esta hoja se re-verificaron en disco (`16-`,
`20-`), con el patrón de rango corregido y su deriva declarada en §0.

**Lo que el mandato §2.1 anunciaba y quedó medido:**

1. **El `instrumento_de_emision` de C está vencido** — medido en §1; la re-emisión de RELEASE imprime el
   instrumento. El artefacto de C **no se toca** (AC-R7) y su cláusula se deja como foto de lo que había
   al estampar.
2. **La cláusula «sin commitear» de la fila 16 del `33-registro` venció otra vez** — medido: la fila sigue
   conteniendo `sin commitear` y el rango `0c79e9c..4661b6e`, y hoy `git rev-list --count 0c79e9c..HEAD` =
   **15** (la fila estampó 13 y el sello anterior 14). **No se edita: vive en un documento del hermano y
   AC-R7 veda escribirlo.** Se declara acá con su medición y su dueño (el hermano, con instrucción
   literal), que es el mismo mecanismo que el plan usó el 2026-09-30 para las dos filas de
   `dependencias-fases.md` que no podía tocar.
3. **El rango sin L3 sigue creciendo** — 15 al arrancar, y cada commit de esta sesión lo mueve; §9 y el
   corte 4 publican el re-medido.

**El hallazgo nuevo de este barrido (H13).** `protocolo.json` está **`CONGELADA`**
(`congelado: {revisado_por: jhon, fecha: 2026-10-04}`), medido en disco (`18-`) y confirmado contra las
dos formas de sha que publicó FASE-C. Ocho afirmaciones en presente de los documentos del plan siguen
diciendo que está `BORRADOR`, y **todas son falsas hoy** (medidas y clasificadas por asunto en `20-`):

| Documento | Línea | Frase en presente |
|---|---|---|
| `01-plan-maestro.md` | 146 | «`protocolo.json` en `BORRADOR` porque su congelado es C» |
| `05-prompt-inicio-sesion-fase-B.md` | 3 | «`protocolo.json` conserva `status: BORRADOR`» |
| `05-prompt-inicio-sesion-fase-B.md` | 63 | «mientras `protocolo.json` sigue `BORRADOR`» |
| `06-checklist-implementacion.md` | 11 | «lo que la deja en PARCIAL es `protocolo.json`, que conserva `status: BORRADOR`» |
| `06-checklist-implementacion.md` | 25 | «seguía y sigue `BORRADOR`» |
| `09-documentacion-post-proyecto.md` | 25 | «`protocolo.json` sigue `BORRADOR`» |
| `README.md` | 55 | «`protocolo.json` sigue `BORRADOR`, y eso es FASE-C» |
| `README.md` | 128 | «con `protocolo.json` en `BORRADOR` porque su congelado es C» |

De las 24 menciones totales de `BORRADOR` en el plan: **8 tienen por asunto el protocolo** (las de arriba),
13 la muestra (fotos fechadas, varias ya con sello que las declara vencidas) y 3 son regla condicional o
cita de otro texto (`20-`). La causa de la vencimiento es de secuencia, no de contrato: **B.2 y C cerraron
el 2026-10-04 con sellos que hablan del congelado, pero la matriz `06-checklist` se escribió al cierre de
FASE-B, antes del acto de C.** Lo que esto mueve de verdad es el AC3 (§6): el motivo que declaraba
PARCIAL cayó, y el que queda es otro.

**Alcance de las ediciones:** se re-anclan las cinco que viven en documentos listados por el mandato §5
(README ×2, `06-checklist` ×2, `09` ×1). Las tres restantes (`01-plan-maestro.md`, `05-prompt-B` ×2) no
están en la lista de ediciones del mandato, así que **no se tocan**: se declaran como deuda REL-3 con su
coordenada, siguiendo el precedente de la casa (`10-analisis` §sello 2026-09-30).

---

## 6. Tabla de cierre AC1–AC12 (estado + motivo + artefacto)

Los estados de las filas C/RELEASE son **consumidos de C** o medidos por el instrumento; ninguno lo
inventó esta hoja. Los artefactos citados existen y se leyeron en disco con su sha (censo `18-`).

| AC | Estado al cerrar RELEASE | Motivo medido | Artefacto |
|---|---|---|---|
| AC1 | **HECHA** | Costura intacta como frontera: `[SIN-HALLAZGOS]` con población 842/9878 y 0 imports prohibidos fuera de la puerta; los dos artefactos presentes | `FASE-B/import_scanner.txt` (935 B), `FASE-B/integracion.json` (4355 B), crudo `09-` |
| AC2 | **HECHA** | Brazo DeepSeek explícito sin fallback en `scripts/proveedores/deepseek.py`; `git diff` de `llm_provider.py` **vacío** contra el tip | `FASE-B/contract.txt`, `FASE-B/modelos.json`, crudo `10-` |
| AC3 | **PARCIAL, con el motivo re-anclado** | El motivo que publicaba la matriz (`protocolo.json` en BORRADOR) **cayó**: hoy está `CONGELADA`. Quedan dos motivos medidos: **4 pares contra el objetivo 60–100** de la fila del maestro, y `limites_gasto.usd = null` (fuera de gobernanza). Límite declarado: el orden «versionado antes de la primera inferencia» del protocolo se lee del registro de C y de sus brutos numerados (`01-protocolo-check-pre`, `02-…-post-congelada`, `05/06/07`), no de un instrumento independiente | `muestra.json` (`CONGELADA`, counts 4/2/2/1), `etiquetas.json` (`revisada`), `protocolo.json` (`CONGELADA`, sha disco `140577a0…`), crudo `18-` |
| AC4 | **PARCIAL** | Los cuatro cocientes con denominadores separados ya los produce el instrumento y son reproducibles sin red; lo que no: el brazo jev perdió un par por fallo de transporte (comparación incompleta por diseño, AC12), y **no hay contabilidad de coste separada** en el informe (`cost_calculated`/`cost_billed` ausentes, sin veredicto de exceso contra los techos) → deuda B2-1 | `FASE-C/respuestas.jsonl` (6 filas), `FASE-RELEASE/informe_comparativa.json`, crudos `02-`, `04-`, `17-` |
| AC5 | **CONSUMIDA DE C — no producida por RELEASE** | `run_status=INCOMPLETO`, `decision=null`; la re-emisión reproduce el estado (EXIT 3) y **ningún literal de adopción se emitió en esta sesión**: ACTIVAR EXCLUIDA por medición, RECHAZAR NO EMITIDA, MUESTRA-INSUFICIENTE EXCLUIDA por la regla y ponible por el operador, COSTE-NO-PAGADO BLOQUEADO | `FASE-C/decision.json`, `FASE-RELEASE/decision.json`, `decision.md`, crudos `03-`, `04-` |
| AC6 | **HECHA en sus dos mitades** | Mitad B: mutantes con causa nombrada y restauración por sha. Mitad C: `removed: []`, `anchored_before 25 = anchored_after 25` sobre el **guard real** `scripts/triage_lesson_relevance.py:guardar_filas_ancladas`. Y el hueco que B declaraba NO-EJERCITADO se cerró por otra vía: `tests/quality_gates/lesson_relevance/test_triage_guard_real_aditividad.py` (4 funciones, entre ellas `test_mutar_la_clausula_del_guard_hace_caer_la_afirmacion_de_ac6`) corre en verde dentro de **62 passed** | `FASE-B/mutation.json`, `FASE-C/aditividad.json`, crudo `19-` |
| AC7 | **CERRADA CON TRANSFERENCIA PENDIENTE** (que es su salida legítima) | `jev_recommendation` y `d6_eligibility` separados, `transfer_status=PENDIENTE`. Sin línea literal del operador que nombre archivos y alcance, y con el estado del hermano **re-leído** (`14-`): D7 sigue abierta, D6 dormida con causa. No se declaró deuda ajena cerrada ni se tocó un documento del hermano (`05-`) | `FASE-C/decision.json`, `FASE-RELEASE/decision.json`, `14-` |
| AC8 | **HECHA** | `budget_tests.txt` + preflight + `consumo.json` (`llamadas_usadas 2`, `intentos 2`, `tokens_in_max 1778`, `tokens_out_max 145`); el cliente con `max_retries=0` verificado contando intentos. Desvío de ruta declarado en la matriz (el crudo quedó también en `FASE-B/preflight.json`) | `FASE-B/budget_tests.txt`, `FASE-B/preflight.json`, `FASE-C/consumo.json`, `FASE-C/preflight.json` |
| AC9 | **HECHA** | Cuatro artefactos presentes; SDK real con `MockTransport`, errores asertados por clase, 200 sin `usage` tratado como fallo de validación | `FASE-B/entorno.json`, `requirements-pilot.txt`, `sdk_contract.txt`, `mutation.json` |
| AC10 | **HECHA** | Instrumentos contra valores conocidos en las dos mitades; hoy se re-ve el contrato del denominador cero: la capa fría emite `precision = None (0/0)`, **no** 100 ni 0 | `FASE-A/selftest.txt`, `FASE-B/metrics_tests.txt`, crudo `04-` |
| AC11 | **HECHA en cada fase, y re-validada en este cierre** | Validadores del plan y flujo §4.5 por sus writers (§9). Ninguna cifra se transcribe de una nota sin reproducirla | §9 de este registro y sus brutos |
| AC12 | **HECHA** | Cuatro estados por proveedor, Anthropic excluido, y el brazo sin SDK declarado; la verificación «habilitación ≠ autenticación/cuota» ya tiene denominador: `revisar_preflight` jev → `ok=true`. **Con su hallazgo**: deepseek → `ok=false` porque el guard pide `sdk_instalado=true` y el preflight de C registra `NO-APLICA` (H14, deuda REL-1) | `FASE-C/preflight.json`, `FASE-B/preflight.json`, crudo `19-` |

**Ninguna ejecución fallida cerró un AC de comparación.** AC4 y AC5 siguen PARCIAL y CONSUMIDA
respectivamente por el fallo de transporte de la pata jev, no se ascendieron a verde.

---

## 7. Hallazgos nuevos de esta sesión (con dueño y criterio que los pide)

- **H13 — el congelado de C no se propagó a la matriz.** Ocho frases en presente siguen diciendo que
  `protocolo.json` está `BORRADOR` (§5). Dueño: los documentos del plan; criterio: AC3 y la regla de
  «un resultado, una fuente». Cinco se re-anclan acá; tres quedan como REL-3 porque el mandato no lista
  ese archivo entre las ediciones autorizadas.
- **H14 — el guard del `run` no sabe despachar un brazo sin SDK.** `revisar_preflight(FASE-C/preflight.json,
  'deepseek')` devuelve `ok=false` con el motivo `preflight-sdk_instalado='NO-APLICA: …'`, porque
  `ESTADOS_PREFLIGHT_OBLIGATORIOS` exige `sdk_instalado: True`. Consecuencia medible: un `run` por la vía
  del CLI para el brazo comparador está cortado por su propio preflight, y AC12 dice que DeepSeek es
  obligatorio y que la indisponibilidad **no elimina un brazo de la comparación**. Dueño:
  `scripts/evaluate_jev_pilot.py` (`revisar_preflight` / `ESTADOS_PREFLIGHT_OBLIGATORIOS`); criterio: AC12.
  No es un rojo de esta hoja ni se arregla acá (RELEASE no escribe `scripts/`).
- **H15 — B2-4 dejó de ser una limitación teórica.** Cuatro descargas fallidas en una corrida pintaron
  `VENCIDO` un gobernado fresco (§4). Dueño: `scripts/verify_qmind_context_freshness.py` (instrumento del
  hermano); criterio: ya declarado por C y por B2-4.
- **H16 — un patrón de rango mal formado fabrica verdes vacíos.** `\d{7}` contra shas hex dio «0 rangos»
  en una fila que tiene dos (§0). Dueño: esta hoja; criterio: AC-R9 (nada heredado, todo medido con su
  comando).
- **H17 — el quick gate se pone rojo por escribir evidencia, y el rojo no es de cableado.** `12/13` con
  `[11/13] Wiring` vencido por +1 archivo `.py` en `FASE-RELEASE/` (crudo `07-`/`08-`). Es el mismo caso
  de B2 §10, y la reparación es por su escritor. Dueño: el flujo §4.5 de esta hoja; criterio: AC-R5.
- **H18 — FASE-C y FASE-B.2 no tienen entrada en `REGISTRY.md`.** Medido: las dos únicas entradas del plan
  son `## FASE-A - 2026-09-21` y `## FASE-B - 2026-10-03 (EVALUACION-JEV-TYPESAFE-2026-09-21)`. El Paso
  4.5.1 del executor **verifica, no re-registra**, y el mandato fija `log_phase_completion.py`
  **exactamente una vez** con `--fase FASE-RELEASE` (AC-R5), así que **no se ejecuta por tercera y cuarta
  vez**: se declara como REL-2 con su dueño (el operador, con instrucción explícita por fase y su `--fecha`
  real).
- **H19 — un rojo del piloto aparece solo en la colección completa.** El test
  `test_la_falta_de_deepseek_falla_antes_de_enviar_aunque_haya_clave_anthropic` pasa aislado (1 passed),
  pasa con `decision_client` + `jev_pilot` (221 passed) y pasa en toda la selección `tests/quality_gates`
  (1021 passed, 10 skipped), y cae en la suite entera (1 failed / 4889 passed). El estado que lo provoca vive
  **fuera** de `quality_gates`, medido por descarte. No lo produjo esta hoja: `tests/` y `scripts/` están byte a
  byte como en el tip. Dueño: la selección del piloto con su carga por `importlib`; criterio: AC2/AC12. Se
  registra como REL-5 y no se toca (§9.3).

## 8. Deuda visible: la que viene de atrás, re-medida, y la nueva

| # | Deuda | Estado medido hoy | Dueño / criterio |
|---|---|---|---|
| B2-1 | `report` no compara `usage_normalized` contra los techos ni publica `cost_calculated`/`cost_billed` | **VIVA**: las dos claves no existen en el informe y no hay comparación contra `limites_gasto`; la lectura de control sí puede calcular el exceso (techo `tokens_out 139` contra 145 observado) | `scripts/evaluate_jev_pilot.py` (`report`) / AC4 |
| B2-2 | `metrics()` sin productor | **VIVA**: 1 definición, 0 llamadas desde código (las dos ocurrencias restantes son comentarios); `report` emite cociente por cociente con `score()` | contrato de salida de FASE-A / AC10 |
| B2-3 | El margen apoyado en 1 par utilizable | **VIVA**: `denominador_eval 2`, `denominador_efectivo 1`, `paso 0.5` contra umbral `0.25`, `diferencia_calculada 0.0` y `NO-EVALUABLE` | re-apertura de C con decisión del operador / AC5 |
| B2-4 | Descarga fallida pinta `VENCIDO` un fresco | **MATERIALIZADA y medida** (§4, H15) | `scripts/verify_qmind_context_freshness.py` |
| B2-5 | Transferencia D7/D6 | **PENDIENTE**, con el estado del hermano re-leído y sin un byte movido en su árbol | operador con instrucción literal / AC7 |
| **REL-1** | El preflight del `run` corta el brazo comparador por pedir `sdk_instalado=true` (H14) | nueva, medida | `scripts/evaluate_jev_pilot.py` / AC12 |
| **REL-2** | FASE-C y FASE-B.2 sin entrada en `REGISTRY.md` | nueva, medida | operador, con `--fecha` real de cada cierre / Paso 4.5.1 |
| **REL-3** | Tres frases en presente sobre `protocolo.json` fuera del listado de ediciones del mandato (`01-plan-maestro.md`, `05-prompt-B` ×2) | nueva, medida | documentos del plan / H13 |
| **REL-4** | `05-prompt-inicio-sesion-fase-RELEASE.md` sigue siendo el esqueleto vigente en el índice del README, sin señalar que esta pegada lo venció | nueva | README §Índice / §1 del mandato |
| **REL-5** | Rojo dependiente del orden de colección en la suite completa (H19), invisible en el quick gate | nueva, medida en `28-` y `31-` | `tests/quality_gates/jev_pilot/` con su conftest / AC2 y AC12 |
| **REL-6** | El verificador de frescura decide por descarga cuando el servidor ya publica `metadata.fileSha256`: una descarga que cae sobre la única fuente que casa produce `[VENCIDO]` falso (anclado en §15) | nueva, medida en `40-` | `scripts/verify_qmind_context_freshness.py` (instrumento del hermano) / B2-4 y H15 |

Ninguna de las cinco deudas anteriores se absorbe, y ninguna se presenta como bloqueante si es
aplazamiento con dueño.

---

## 9. Corte 3 — cierre documental, por sus writers y con su EXIT

Cada escritura del cierre pasó por el instrumento que es dueño de ese artefacto. Ningún derivado se editó
a mano. Los códigos de salida se leyeron **sin tubería** (`comando > archivo; echo $?`), que es la forma en
la que un EXIT no se lo roba el `tail`.

### b) El flujo §4.5, en el orden del mandato

| # | Comando | EXIT | Qué imprimió | Crudo |
|---|---|---|---|---|
| b1 | `scripts/sync_versions.py --check` (baseline antes de escribir) | 0 | seis reglas `in sync`; `Result: All files in sync` | `25-` |
| b1 | `scripts/sync_versions.py` (el escritor) | 0 | no movió ninguna de las cinco rutas versionadas: `git status --porcelain` sobre `AGENTS.md`, `.cursorrules`, `README.md`, `docs/CONTRIBUTING.md`, `VERSION.yaml` quedó **vacío** | `25-` |
| b2 | `scripts/version_consistency_checker.py` | 0 | `RESULTADO: TODO SINCRONIZADO` (3/3) | `25-` |
| b3 | CHANGELOG y GUIA_TECNICA (escritura directa de esta hoja, no derivados) | — | entrada bajo `## [Sin publicar]` con sus seis secciones; nota técnica de FASE-RELEASE (la quinta del archivo) | §9.2 |
| b4 | `scripts/run_all_validations.py` (modo completo) | 1 | **16/18**; los dos rojos se atribuyen en §9.3 | `26-` |
| b5 | `scripts/doctor.py --context` | 0 | cinco `[OK]` (`context_file_paths`, `error_catalog_skills`, `domain_primer_methods`, `domain_primer_file_references`, `agents_path_consistency`). **Verificó, no regeneró**: `git diff --numstat` de `DOMAIN_PRIMER.md` vacío | `29-` |
| b6 | `scripts/doctor.py --status` | 0 | `[OK] SYSTEM_STATUS.md regenerado (1 skills, 1270 shadow logs, 10 sesiones)`; su destino regenerable, declarado en `AGENTS.md`, movido **4+/4−** | `32-` |
| b7 | `scripts/validate_qmind_writeback.py --upload EVALUACION-JEV-TYPESAFE-2026-09-21` | **no ejecutado** | checkpoint con solicitud: requiere permiso expreso (publicación externa, sin `delete_source`) y el writer tiene el límite documentado de no poder publicar un cierre actualizado | §4 |
| b8 | `scripts/validate_qmind_writeback.py --strict` | 0 | `[PASS] 13/13 10-analisis archivados ingested` | `15-`, `30-` |
| b9 | `scripts/verify_qmind_context_freshness.py --strict` | 1 | **antes** de las ediciones: 1 fresco + 1 vencido con 4 descargas fallidas. **después**: 0 frescos + 12 problemas con **10 `[SIN-DESCARGA]`** | `12-`, `13-`, `30-` |

### 9.1 QMind después de editar el `10-analisis`: separar el vencido real del transitorio

Medición fuerte, con el sha del archivo como testigo:

| Artefacto | sha de disco antes de editar | sha de disco después | Veredicto del verificador | Lectura correcta |
|---|---|---|---|---|
| `10-analisis-post-implementacion.md` | `424b5828e341…` | `f05d7eab20d2…` | `[VENCIDO]` | **Vencido real** ⟦**cerrado el mismo día por el write-back de §14**: la fuente publicada pasó a ser `01a10e39-1625…` y la cifra final del disco es `d1b8ff00b511…` — el `f05d7eab20d2…` de esta celda era un estado intermedio, ya superado⟧: la fuente publicada del notebook (`01a10853-6da2…`) casa con los bytes **anteriores** a este cierre. Necesita write-back con título nuevo, verificado por descarga+sha256 |
| `CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21.md` | `5587f27ddd5a…` | `5587f27ddd5a…` (sin cambio) | `[VENCIDO]` | **Falso vencido**: su sha no se movió y en la corrida 3 del mismo día casó con la fuente `01a0efcc-3297…`; hoy esa descarga falló |

`validate_qmind_writeback.py --strict` sigue diciendo `[PASS] 13/13` **justo por el límite que se declara**:
decide por título, y el título no cambió aunque el contenido sí. Es la demostración ejecutada de que un
`[PASS]` de ese writer no prueba que la versión publicada esté al día; lo prueba la frescura por descarga.
Consecuencia para el operador: el write-back pendiente no es una formalidad, es la única de las dos casillas
QMind que hoy tiene materia real que publicar.

### 9.2 Ediciones propias de la hoja (no derivados)

| Archivo | Qué entró |
|---|---|
| `README.md` del plan | sello de sesión en la cabecera; filas FASE-C y FASE-RELEASE de la tabla de estados; correcciones datadas en P1, P3, P4, P5, P6 y P7; sello en §Inicio |
| `06-checklist-implementacion.md` | nota de rutas en la cabecera (FASE-C y FASE-RELEASE existen); AC3 y AC4 con motivo re-anclado conservando el viejo; AC5 consumida; AC6, AC7, AC8 y AC12 cerradas con su medición; tres casillas de entrada/salida marcadas con su límite; la corrección datada del «sigue BORRADOR» |
| `09-documentacion-post-proyecto.md` | §A con los seis modos del runner y los cuatro códigos re-medidos; fila de `decision_client.py` con AC6 ya ejercitada; §C con el congelado separada de lo que sigue vigente; **§D con columna RELEASE** (aquí vive el número); §E con el estado de los tres destinos del flujo |
| `10-analisis-post-implementacion.md` | Resumen de ejecución de FASE-C y FASE-RELEASE; §Seguimientos re-escrito con tres estados separados; nueva sección de cierre con las lecciones **L-JEV.R1 a L-JEV.R4** y la tabla de seguimientos B2-1, B2-1c, B2-2, B2-3, B2-4, B2-5, REL-1, REL-2, REL-3, REL-4 |
| `00-lecciones-capitalizadas.md` | sello de §2 con lo que la corrida confirmó (L-D5, L-R.3, L-R.4, L-T4A.5) y lo que no compra (L-P6.3 manda el estado); §4 con las dos cláusulas vencidas |
| `dependencias-fases.md` | **solo** las dos filas de §Decisiones pendientes; la sección «Orden de cierre: hermano primero» intacta, verificada por presencia del título antes y después de escribir |
| `CHANGELOG.md` | entrada `[Sin publicar] - FASE-RELEASE del plan EVALUACION-JEV-TYPESAFE-2026-09-21 - 2026-10-05` con seis secciones |
| `docs/GUIA_TECNICA.md` | `## Nota Técnica — FASE-RELEASE del plan EVALUACION-JEV-TYPESAFE-2026-09-21 (2026-10-05)` |

**Desviación declarada del literal del mandato (§5.2: «CHANGELOG `[X.Y.Z]`, versión leída de
VERSION.yaml»).** `VERSION.yaml` está en **4.78.0**, que es la release **del hermano** fechada el
2026-09-25 y ya tiene su entrada en el archivo. Fechar una segunda entrada `[4.78.0]` el 2026-10-05
inventaría una release nueva con el nombre y la fecha de la anterior, en las cabeceras que sincroniza
`sync_config.yaml`. Como RELEASE tiene prohibido subir VERSION y no hay release que registrar, el contenido
va bajo `## [Sin publicar]`, que es la misma salida que el archivo ya usó para el bloque A. **El mandato no
se editó para acomodar el resultado**: se declara la desviación y se pide instrucción si se prefiere otra.

### 9.3 Los dos rojos del modo completo, atribuidos por causa

El modo rápido (13 checks) no corre ni la suite ni la frescura de CONTEXT; el completo llega a 18 y ahí
aparecen los dos. No son rojos de cableado ni de esta hoja:

1. **`[16/18] Tests`** — el check corre `pytest -q --tb=no` sobre toda la suite y pide EXIT 0. Medido en la
   misma máquina y el mismo tip: **1 failed, 4889 passed, 41 skipped, 4 xfailed en 407.49 s**. El único rojo
   es `tests/quality_gates/jev_pilot/test_jev_pilot_deepseek_brazo.py::test_la_falta_de_deepseek_falla_antes_de_enviar_aunque_haya_clave_anthropic`.
   Caracterizaciones medidas, no inferidas:
   - ese test, solo: **1 passed**;
   - su archivo completo: 15 tests collected, verde;
   - el par `decision_client` + `jev_pilot`: **221 passed**;
   - toda la selección `tests/quality_gates`: **1021 passed, 10 skipped, EXIT 0** (`31-`);
   - o sea es **dependiente del orden de colección** y el estado que lo provoca vive **fuera** de
     `tests/quality_gates`, medido por descarte y no por suposición.
   No lo produjo esta sesión: `tests/`, `scripts/` y `modules/` están **byte a byte** como en `ced8715`
   (`git diff --numstat` vacío, crudo `05-` y `32-`), y RELEASE tiene prohibido escribir ahí. Dueño: la
   selección del piloto con su conftest de carga por `importlib`; criterio que lo pide: AC2/AC12 («sin
   proveedor… error explícito, nunca decisión por defecto»), que es justo la aserción que cae. Se registra
   como **REL-5** y no se toca.
2. **`[18/18] QMind CONTEXT Freshness`** — el mismo instrumento de §9.1, con diez descargas que devolvieron
   `QMind network request failed`. Su rojo mezcla dos materias: un vencido real (el `10-analisis` de esta
   hoja, que quedará publicado cuando el operador autorice el write-back) y un vencido falso por red. La
   deuda de instrumento sigue siendo B2-4/H15.

### 9.4 Índice, derivado y registro oficial

| Escritor | Baseline PRE | Corrida que escribe | POST |
|---|---|---|---|
| `build_lesson_index.py` | `--check` **EXIT 1** («Índice de lecciones vencido: LECCIONES-INDEX.md, lecciones_index.json») | EXIT 0: **344 IDs definidos + 56 sin definición** (16 análisis, 422 `.md` citados) | `--check` **EXIT 0** («fresco (344 IDs)») |
| `validate_wiring.py` | `--check` **EXIT 3** (publicado 142 / fresco 143; evidence 130 → 131) | `--write-report` EXIT 0: 174 llamadas, 699 archivos, **violaciones 0** | `--check` **EXIT 0** (digest `3141ef38f77c` conforme) |
| `log_phase_completion.py` | dry-run primero, para ver lo que escribiría | **una sola corrida real**, `--fase FASE-RELEASE --fecha 2026-10-05 --plan … --tests 0 --check-manual-docs`, EXIT 0 | cabecera `## FASE-RELEASE - 2026-10-05 (EVALUACION-JEV-TYPESAFE-2026-09-21)` presente **1** vez; `Ultima actualizacion` → **2026-10-05**; `REGISTRY.md` **20+/2−**; `docs/contributing/.last_doc_phase.json` **sin cambio** (no se pasó `--archivos-mod`, y pasarla escribe ese subproducto) |

El delta de IDs del índice es exactamente **+4**, y son los cuatro que definió esta hoja
(`L-JEV.R1` a `L-JEV.R4`), todos con el plan dueño `Archives/EVALUACION-JEV-TYPESAFE-2026-09-21` y cero
 citas externas: ninguna fila del hermano se movió. Crudo `22-`.

### 9.5 Validadores del plan, todos en verde antes del cierre

`validate_lesson_capitalization.py`, `validate_plan_citations.py`, `validate_plan_closure.py`,
`validate_opencode_refs.py`, `validate_document_integration.py`, `validate_agents_md.py`,
`validate_governance_numbers.py` y `build_lesson_index.py --check`: **ocho EXIT 0** (crudo `24-`).
Dos lecturas que valen por sí solas: citas del plan **743 históricas, 0 nuevas y 0 crecimientos** —las
ediciones de este cierre citan artefactos y símbolos, no posiciones—, y `validate_plan_closure.py` en
«ningún plan vivo declara cierre con filas pendientes».

### 9.6 Superficie final tocada, medida con `git status`

```
 M .opencode/LECCIONES-INDEX.md            (writer, +13/−9)
 M .opencode/lecciones_index.json          (writer, +64/−8)
 M .opencode/wiring_report.json            (writer, +5/−5)
 M .agent/SYSTEM_STATUS.md                 (writer doctor --status, +4/−4)
 M CHANGELOG.md                            (esta hoja)
 M docs/GUIA_TECNICA.md                    (esta hoja)
 M docs/contributing/REGISTRY.md           (writer, +20/−2)
 M .opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/{README,00-lecciones-capitalizadas,
    06-checklist-implementacion,09-documentacion-post-proyecto,10-analisis-post-implementacion,
    dependencias-fases}.md                  (esta hoja, seis archivos)
?? evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-RELEASE/   (40 entradas: el registro, 35 brutos `.txt` y un arnés, y los tres artefactos
    arnés, y los tres artefactos emitidos por `report`/`decide`)
```

Nada de `scripts/`, `tests/`, `config/`, `VERSION.yaml`, `AGENTS.md`, `.cursorrules`, hooks,
`muestra.json`, `protocolo.json`, `etiquetas.json`, `FASE-C/` ni del hermano. Quick gate final
**13/13, EXIT 0** (`33-`).


**Re-verificación del árbol final (crudo `34-`).** Tras las últimas ediciones del registro y del `10-analisis`, los nueve verificadores volvieron a correr y dieron **EXIT 0** los nueve, el quick gate cerró en **13/13 EXIT 0** y la batería del piloto repitió **126 passed** sobre el árbol de cierre. La prueba de que el derivado no se movió a mano: `build_lesson_index.py --check` y `validate_wiring.py --check` siguen en 0 sin volver a invocar a sus escritores.
---

## 10. Corte 4 — tabla final de estados y petición explícita

### 10.1 Los cinco cortes, cada uno con su evidencia

| Corte | Estado | Evidencia |
|---|---|---|
| 1. Implementación terminada (re-verificación) | **terminado** | re-emisión `report`/`decide` (`02-`, `03-`, artefactos), contraste `04-`, cifra por cifra §2 |
| 2. Verificación terminada | **terminado** | baterías `01-`, `06-`, `19-`; superficie `05-`; AC1–AC12 §6; censo re-verificado `16-`, `20-`; QMind `12-`, `13-`, `15-`, `30-` |
| 3. Cierre documental | **terminado** | §9 con el EXIT de cada writer; brutos `22-` a `33-` |
| 4. Listo para revisión | **esta hoja** | tabla de abajo |
| 5. Espera de autorización | **abierto, aquí termina la sesión** | §11 |

### 10.2 AC del mandato (AC-R1 a AC-R10), con su motivo cuando no es pleno

| AC-R | Estado | Motivo medido |
|---|---|---|
| R1 cifra con instrumento | **HECHA** | toda magnitud del §2 y §9 lleva comando, árbol/tip, fecha y crudo |
| R2 ACs cerrados con motivo | **HECHA** | AC1–AC12 en §6; PARCIAL en AC3/AC4 con motivo re-anclado; AC5 consumida; ningún AC de comparación cerrado por ejecución fallida |
| R3 C consumido, no producido | **HECHA** | `run_status`/`decision`/`transfer_status` coinciden con C; ningún literal de adopción emitido; la re-emisión casa o su divergencia se publica (schema de C ≠ schema del emisor, declarado en §1) |
| R4 transferencia fiel | **HECHA** | `PENDIENTE`, sin línea literal; hermano re-leído (`14-`) y sin un byte (`05-`) |
| R5 flujo §4.5 por sus writers | **HECHA con una desviación declarada** | siete de los ocho comandos del bloque (b) corrieron en orden y con su EXIT publicado; **`--upload` no se ejecutó** por permiso y por límite del writer (§9.b7); CHANGELOG bajo `[Sin publicar]` en vez de `[X.Y.Z]` (§9.2); `log_phase_completion.py` **exactamente una vez** |
| R6 QMind verificado | **PARCIAL con causa** | `--strict` y frescura con EXIT publicado y `[SIN-DESCARGA]` contado (10 en la corrida final); falta `--upload`, que es acto de publicación y le corresponde al operador |
| R7 superficie respetada | **HECHA** | §9.6 y `05-`: cero escrituras en las trece rutas vedadas |
| R8 cinco cortes y permisos | **HECHA** | §10.1; commit, push y L3 solicitados y no ejecutados |
| R9 nada heredado | **HECHA** | tip, paridad, rangos, baterías, shas y conteos medidos en la sesión; las negaciones del CLI se re-corrieron en vez de citar el crudo de B.2 (`21-`) |
| R10 evidencia preservada | **HECHA** | brutos `.txt` numerados en `FASE-RELEASE/` (35 y un arnés al corte documental; **37 y dos arneses al cierre del sello**, recuento en §12); cada hallazgo nuevo con dueño y criterio (§7 y §8) |

### 10.3 Deuda y hallazgos, todos con dueño

B2-1, B2-1c, B2-2, B2-3, B2-4, B2-5 (re-medidos vivos en §8) · REL-1, REL-2, REL-3, REL-4 (§8) · **REL-5**, · **REL-6** (§15)
el rojo dependiente del orden en la suite completa (§9.3) · H13 a H18 (§7).

### 10.4 Petición explícita al operador (cuatro actos, cada uno con su instrucción)

1. **Escaneo L3 del rango sin revisar, re-medido.** Al arrancar de esta sesión era `0c79e9c..ced8715` = **15
   commits**; crece con cada commit que se autorice. Es decisión suya correrlo o no; no se ejecuta por
   inercia.
2. **Autorización escrita de commit.** Si se concede: se stagea **por nombre** las trece rutas modificadas de §9.6, más la
   carpeta `evidence/…/FASE-RELEASE/`, sin `git add -A`, y se deja pasar los hooks activos sin
   `--no-verify`. Advertencia medida en esta casa: el Secrets Check del hook escanea «tracked + staged», así
   que la pasada de pre-commit que ya corró esta hoja **no miró aún** los archivos nuevos; y el `[8/8]` del
   hook lee HEAD, o sea verifica el tip previo y no el commit que se está escribiendo.
3. **Autorización escrita de push** (separada del commit). Si se concede: pre-flight de alcance (objetos,
   `--dry-run`, paridad contra `git ls-remote`) y sello **aditivo** con el rango desde el tip remoto previo;
   un segundo push deja incompleto el sello del primero, y la convención es añadir rango, no reescribir.
4. **Permisos de publicación y gobierno**: write-back del `10-analisis` con título nuevo por el CLI de QMind
   (verificado por descarga + sha256, no por título), la etiqueta de adopción sobre el registro de C, la
   línea literal que nombre archivos y alcance si se quiere mover D7/D6, y decisión sobre REL-2 (registrar
   FASE-C y FASE-B.2 en `REGISTRY.md`, cada uno con su fecha real) y REL-5/REL-1 (dueños de `scripts/` y
   `tests/`).

---

## 11. Lo que esta sesión NO hizo

**Cero envíos de inferencia y cero envíos de conectividad del piloto.** `report` y `decide` no importan la
costura ni instancian clientes: verificado por `--scan-imports` con `[SIN-HALLAZGOS]` y 0 imports prohibidos
fuera de la puerta (`09-`). Las únicas salidas de red de la sesión fueron las **descargas de lectura** del
verificador de frescura de QMind, que el contrato del plan autoriza como preparación y no como inferencia ni
write-back; se declaran porque el §8 del mandato pide cero red y esta hoja leyó esa cláusula por su
contrato: la lectura no gasta el piloto, la publicación sí.

**Sin credenciales en ningún artefacto.** Ni valor, ni máscara, ni longitud, ni prefijo. El único dato de
entorno que se manipuló es `ANTHROPIC_API_KEY` con un centinela sintético ya versionado en la batería, y las
dos cadenas `req_…` citadas son request IDs del antecedente publicado por B, no secretos.

**Sin escribir** `scripts/`, `tests/`, `config/`, `VERSION.yaml`, `AGENTS.md`, `.cursorrules`, hooks, gates,
`muestra.json`, `protocolo.json`, `etiquetas.json`, ningún artefacto de `FASE-C/` ni ningún documento del
hermano o de plans ajenos. **Sin re-congelar** muestra ni protocolo. **Sin re-abrir C**. **Sin emitir la
etiqueta de adopción.** **Sin subir VERSION.** **Sin declarar deuda ajena cerrada.** **Sin ofrecer la fase
siguiente.**

Commit, push, L3 y write-back: **no ejecutados y no ofrecidos como hecho**. Los cinco cortes terminan acá,
en espera de instrucción escrita del operador.

⟦**Vencida en su primera cláusula por §12**: el operador autorizó «Git Commits» y el trabajo se
commiteó en `39717b1` (53 archivos, +3416/−69, hooks en verde, verificado en su propio árbol con un clon
limpio). **Push, L3 y write-back siguen sin ejecutar**, y la frase se conserva porque describe el estado al
estampar el corte documental. La anotación es aditiva: la foto no se reescribe.⟧

---

## 12. Sello del commit `39717b1`

El operador autorizó **«Git Commits»** (acto 2 de §10.4). No autorizó push ni L3, así que esta hoja estampa
el commit y su verificación, y deja el rango sin publicar y sin revisar donde estaba.

### Lo que se ejecutó

| Paso | Comando | Valor medido |
|---|---|---|
| Stage | `git add` **por nombre** de las 13 rutas modificadas + la carpeta `evidence/…/FASE-RELEASE` | **53 rutas** en el índice (`git diff --cached --name-only \| wc -l`); sin `git add -A`; el árbol sin staging quedó vacío |
| Commit | `git commit -F temp/fase-release-2026-10-05/mensaje-commit.txt` | `COMMIT_EXIT=0` · `39717b19a99de8ec87d0c4066a257d06c75a74e7` · **53 archivos, +3416/−69** · hooks activos, **sin `--no-verify`**: «All checks PASSED - Commit allowed» |
| Árbol después del commit | `git status --porcelain` | **vacío** |
| Paridad | `git rev-list --left-right --count origin/master...HEAD` | **0 1** — commiteado, nada empujado |
| El servidor | `git ls-remote origin refs/heads/master` | sigue en `ced8715…`, o sea el commit está **solo local** |
| Rango sin L3 | `git rev-list --count 0c79e9c..HEAD` | **16** (era 15 al arrancar la sesión; este commit lo mueve) |

**El Secrets Check del hook sí miró los archivos nuevos esta vez.** La pasada de pre-commit de §2 corrió con
la carpeta aún sin stagear y reportó «1381 tracked files + staged»; con el stage lleno, el hook volvió a
escanear y pasó. Es la diferencia entre un verde que revisó tu evidencia y un verde que no la vio.

### Verificación en el propio árbol del commit (arnés `35-`, crudo `35-`, procedimiento `36-`)

Clon limpio fuera del workspace (`--no-checkout`, y `core.longpaths` y `core.autocrlf=input` **dentro** del
clon), checkout de `39717b1`, árbol con **0 entradas** de status:

| Chequeo en el clon | Resultado |
|---|---|
| `pytest tests/quality_gates/jev_pilot -q` con el intérprete del venv | **113 passed, 13 skipped**, EXIT 0 — los 13 saltos son el SDK del entorno aislado, ausente en el clon, con su causa nombrada por el fixture `sdk` |
| `report` dentro del clon | EXIT 0 |
| `decide` dentro del clon | **EXIT 3** (emitido sin decisión) |
| `informe_comparativa.json` | sha256 normalizado a LF **igual** al commiteado (`1d6a272cb95f…`); el crudo regenerated es `432a61cc6ba7…`, que es **exactamente** el sha de disco que esta hoja publicó en §1 desde otra raíz |
| `decision.json` | normalizado **igual** (`613da2b719c7…`); crudo `7eccaabecbc6…` = el publicado en §1 |
| `decision.md` | normalizado **igual** (`f329673bf929…`); crudo `571f1fc6ade3…` = el publicado en §1 |
| Cifra canónica commiteada | `git grep -h -c -E "^\s*def test_" 39717b1 -- "tests/*.py"` sumado = **4835**, converge con la del árbol y con la que publica `AGENTS.md` |

Las tres formas del mismo artefacto se publican a propósito y no son tres verdades distintas: el **disco** es
CRLF (`432a61cc…`), el **blob** es LF y su sha256 normalizado es `1d6a272c…`. Con `core.autocrlf=input` la
paridad entre máquinas se prueba por la forma normalizada; citar un sha de disco y exigir que case con el blob
es el error que esta casa ya pagó.

### Lo que este commit vence, medido por asunto y no por literal

- **§11 arriba: «Commit, push, L3 y write-back: no ejecutados y no ofrecidos».** La primera de las cuatro
  quedó ejecutada por instrucción escrita; las tres restantes siguen vigentes. La frase se conserva porque
  describe el estado al estampar el corte documental —que es lo que esta hoja registra— y se anota acá.
- **`10-analisis-post-implementacion.md`, párrafo de permisos del cierre**: mismo acto, misma anotación
  aditiva con su fecha.
- **Ninguna otra mención «sin commit» del expediente se barre**: las de `FASE-B/`, `FASE-B2/`, `FASE-C/`,
  `DEUDA-FASE-B-2026-10-04/`, `PREFLIGHT-FASE-C-2026-10-04/` y `docs/cobertura-historia.md` hablan de **sus
  propias** tandas y sus propios rangos. Contar el literal y barrerlo convertiría prohibiciones ajenas en
  rojos propios, que es el error que la casa ya declaró dos veces.
- **La fila 16 del `33-registro-unificado`** (documento del hermano) sigue diciendo «las ediciones de esta
  fila quedan sin commitear» y estampa `0c79e9c..4661b6e = 13` commits. Con este sello el rango medido es
  `0c79e9c..HEAD` = **16**. **No se toca**: AC-R7 veda escribir en el hermano y no hay línea literal. Queda
  declarado en §5 con su medición.

### Consecuencia que este commit produce para la L3

El commit `39717b1` es un commit **nuevo sobre `ced8715`**, así que cualquier L3 futura tendrá por baseline un
rango que ya lo incluye, no el que estampó la fila 16. El skip anterior no se arrastra a un tip nuevo.

### Conteos del expediente al estampar este sello

La carpeta pasó de 43 a **44 entradas**: **38 brutos `.txt`** (entra `37-verificacion-del-push.txt`), los **dos
arneses `.py`**, el registro y los **tres artefactos** emitidos por `report`/`decide`. El derivado
`.opencode/wiring_report.json` y el índice **no** volvieron a vencerse con los archivos `.txt` nuevos
(`validate_wiring.py --check` y `build_lesson_index.py --check` en **EXIT 0** sin re-invocar a sus escritores),
que es la asimetría con el arnés `.py` del §12. Quick gate con el sello redactado: **13/13, EXIT 0**.

---

### Permisos al cerrar este sello

Commit: **una ejecución** (`39717b1`) más esta hoja de sello. Push: **sin ejecutar** (no autorizado).
L3: **sin ejecutar** (no autorizada; la pedí en §10.4 y la instrucción respondió solo el commit).
Write-back: **sin ejecutar**.

⟦**Vencidas dos de las tres por §13**: la instrucción siguiente autorizó «Git Push + L3». El push se
ejecutó (`ced8715..6a8be5c`, paridad 0 0 contra el servidor) y la L3 se corrió **antes** de empujar, sin
hallazgos. **Write-back: sigue sin ejecutar.** Las frases se conservan porque describen el estado al
estampar.⟧ Sin tocar el hermano, `scripts/`, `tests/`, `config/`, `VERSION.yaml`,
`AGENTS.md`, `muestra.json`, `protocolo.json`, `etiquetas.json` ni `FASE-C/`. Sin ofrecer la fase siguiente ni
re-abrir C.

### Conteos finales del expediente

La carpeta de esta fase pasó de 40 a **43 entradas**: el registro (esta hoja), **37 brutos `.txt`**, **dos
arneses `.py`** (`04-arnes-contraste.py` y `35-arnes-verificacion-del-commit.py`) y los **tres artefactos**
emitidos por `report`/`decide`. Los tres artefactos y el registro viajan en el commit `39717b1`; el arnés y
sus dos brutos (`35-`, `36-`) viajan en este sello. El derivado `.opencode/wiring_report.json` volvió a
quedar vencido con el arnés nuevo (publicado 131 / fresco 132, `EXIT 3`) y se re-publicó por su escritor a
**`EXIT 0`** con digest `2e8f095baf00`; el quick gate cerró en **13/13** y `build_lesson_index.py --check` en
**0** (344 IDs, sin invocar al escritor otra vez).

---

## 13. Sello del push `ced8715..6a8be5c` y de la L3 corrida sobre ese rango

El operador autorizó **«Git Push + L3»** (actos 1 y 3 de §10.4). El write-back, la etiqueta de adopción, la
línea literal de D7/D6 y la decisión sobre REL-1/REL-2/REL-5 **no** estaban en la instrucción: siguen
pendientes.

### Pre-flight de alcance, medido antes de empujar

| Chequeo | Comando | Valor |
|---|---|---|
| Estado del remoto al arrancar | `git fetch origin --quiet` + `git ls-remote origin refs/heads/master` | `ced8715…` — sin nada que reconciliar |
| Ancestria (¿fast-forward?) | `git merge-base --is-ancestor ced8715 HEAD` | **sí** → fast-forward puro, **sin `--force`** |
| Que se mueve | `git log --oneline origin/master..HEAD` | **2 commits**: `39717b1` (trabajo) y `6a8be5c` (sello del commit) |
| Objetos | `git rev-list --objects origin/master..HEAD \| wc -l` | **78** |
| Carga | `git diff --shortstat origin/master..HEAD` | 56 archivos, **+3670/−69** |
| Binarios | `git diff --numstat` con columna de líneas `-` | **ningún binario** según git |
| Blobs grandes | cuatro archivos superan 200 KB: `CHANGELOG.md` 431.356 B, `docs/contributing/REGISTRY.md` 352.567 B, `.opencode/lecciones_index.json` 328.364 B, `docs/GUIA_TECNICA.md` 213.722 B | **los cuatro ya estaban versionados** en `origin/master` y crecieron **+8.110, +1.185, +2.138 y +914 bytes**; la lista los muestra porque `rev-list --objects` reporta el blob nuevo del delta, no un archivo nuevo |

### El push

`git push origin HEAD:master` → `PUSH_EXIT=0`, salida `ced8715..6a8be5c  HEAD -> master`. Verificación
**contra el servidor** y no contra el ref local (crudo `37-`):

| Control | Valor |
|---|---|
| `git ls-remote origin refs/heads/master` | `6a8be5c797613a731c9791f7eb5d3a94a32c8472` |
| `git rev-parse HEAD` | el mismo |
| `git rev-list --left-right --count origin/master...HEAD` | **0 0** |
| `git rev-list --count ced8715..HEAD` | **2** |
| Rango sin L3 | `0c79e9c..HEAD` = **17** |
| Árbol al medir | `?? …/FASE-RELEASE/37-verificacion-del-push.txt` y esta hoja estaban sucios al redactar el sello; la instrucción siguiente («estampa el sello, commitea y envía de nuevo») los estampó. El commit del sello es **posterior** a esta tabla y por eso **no se auto-describe**: su propio rango se verifica con `git log --oneline 6a8be5c..HEAD` y `git rev-list --count 6a8be5c..HEAD`, y su sha vive en `git ls-remote`, no en esta prosa |

### La L3, y qué cubrió exactamente

Se corrió **antes** de empujar, siguiendo el precedente de la casa (`FASE-B` nota de ronda: «L3 deep se corrió
**antes** de empujar, por decisión del operador, y no devolvió hallazgos»), sobre la capa profunda de los
commits aún no revisados desde su baseline. **Resultado: sin hallazgos de seguridad** (`findings_count = 0`),
medido el 2026-10-05. Lo que esa corrida cubrió: `39717b1` y `6a8be5c`.

Lo que **no** cubre, y por eso se enuncia acá y no se esconde bajo el «0 hallazgos»: esta hoja de sello es un
commit **nuevo** y el commit de sello del push que la estampa también, así que cualquier L3 futura tendrá por
baseline un rango que los incluye. El «sin hallazgos» de esta corrida **no** es una garantía sobre el rango
completo `0c79e9c..HEAD` (17 commits), sino sobre los dos que se revisaron. Tampoco reemplaza el escaneo de
dependencias: REL-1 y REL-5 siguen siendo deuda de instrumento con dueño, no hallazgo de seguridad.

### Lo que este push y esta L3 vencen, medido por asunto y no por literal

- **§12, «Permisos al cerrar este sello»**: «Push: **sin ejecutar** (no autorizado). L3: **sin ejecutar**
  (no autorizada; la pedí en §10.4 y la instrucción respondió solo el commit)». Ambas quedaron vencidas por
  la instrucción siguiente. Se conservan como foto del momento de estampar y se anotan acá, que es la
  convención de la casa.
- **§11, cláusula de write-back**: sigue vigente — `--upload` **no** se ejecutó, y el `10-analisis` continúa
  con su vencido real declarado en §9.1.
- **El mensaje publicado de `6a8be5c`** cierra con «Sin push, sin L3, sin write-back». Dos de las tres
  quedaron vencidas por el acto que este párrafo estampa. **No se hace `reword`**: reescribir un commit ya
  empujado exigiría `push --force` sobre una rama compartida, y esa no es la vía de la casa. La errata vive
  aquí y `git log` sigue siendo la autoridad de lo que el mensaje dice.
- **`33-registro-unificado`, fila 16** (documento del hermano): su recuento del rango sin L3 y su cláusula
  «sin commitear» quedan más vencidos todavía. **No se toca** — AC-R7 y cero línea literal.
- Las menciones «sin push» de `FASE-B2/`, `FASE-C/`, `DEUDA-FASE-B-2026-10-04/`,
  `PREFLIGHT-FASE-C-2026-10-04/` y `docs/cobertura-historia.md` hablan de **otros** rangos y de otras tandas:
  **no se barren**, porque contar el literal y barrerlo convierte una prohibición ajena en rojo propio.

### Permisos al cerrar este sello

Push: **ejecutado**, con paridad re-medida contra el servidor. L3: **ejecutada antes del push, sin
hallazgos**, cubriendo `39717b1` y `6a8be5c`. Commit del sello que estampa el push: **esta misma hoja viaja en él**, autorizado por la instrucción
«estampa el sello, commitea y envía de nuevo». El push de ese commit es **posterior a esta línea** y por eso
**no se auto-describe acá**: la promesa que esta página sí puede cumplir es la de dar el comando, no la de
perseguir al puntero. Regla de la casa, enunciada en vez de aplicarse en silencio: **un segundo push deja
incompleto el sello del primero**. Quiera uno el rango exacto del segundo empujón, lo obtiene con
`git log --oneline 6a8be5c..HEAD`, `git rev-list --count 6a8be5c..HEAD`, `git ls-remote origin refs/heads/master`
y `git rev-list --left-right --count origin/master...HEAD`; su autoridad es `git log` y el servidor, no una
nota que se re-escriba cada vez que el ref se mueve. Write-back, etiqueta de adopción, D7/D6 y las decisiones de REL-1/REL-2/REL-5: **sin ejecutar y sin
ofrecer**. Sin tocar el hermano, `scripts/`, `tests/`, `config/`, `VERSION.yaml`, `AGENTS.md`,
`muestra.json`, `protocolo.json`, `etiquetas.json` ni `FASE-C/`. Sin ofrecer la fase siguiente ni re-abrir C.

---

## 14. Write-back del `10-analisis` (2026-10-05, orden expresa)

El operador autorizó «Hacer el write-back del 10-analisis con titulo nuevo». Se ejecutó **por el CLI de QMind**
y se verificó **por descarga + sha256**, no por título — la misma vía del cierre del 2026-09-27, por la misma
razón documentada. Crudos `38-` (frescura) y `39-` (publicación).

| Paso | Valor medido |
|---|---|
| PRE — qué estaba publicado | fuente `01a10853-6da2…`, título «cierre FASE-B, lecciones finales 2026-10-04», **21.249 B, sha256 `424b5828e341…`** — exactamente el `sha_disco` que el verificador imprimió **antes** de las ediciones de este cierre |
| Disco al publicar | **30.655 B, sha256 `d1b8ff00b511…`**, LF puro (CR 0 / LF 256), así que crudo y normalizado coinciden y no hay artefacto CRLF que declarar |
| Deriva declarada | §9.1 publicó `f05d7eab20d2…` como sha del disco; era el estado tras las primeras ediciones y quedó superado por las anotaciones del sello. La cifra que gobierna este acto es la re-medida acá |
| Publicación | `qmind source upload --nb 01a04d98… --file <10-analisis> --title "10-analisis: EVALUACION-JEV-TYPESAFE-2026-09-21 (cierre FASE-RELEASE, checkpoint documental 2026-10-05)" --non-interactive` → EXIT 0 al primer intento; fuente nueva **`01a10e39-1625-71b1-8ca6-73cbdb1c6a94`**, `sourceType: markdown`, `metadata.fileSha256` = `d1b8ff00b511…` y `fileSize` 30.655, ambos iguales al disco. Enlaces firmados (`originUrl`, `uri`, `originalFileUri`) **redactados** del crudo |
| POST — verificación fuerte | descarga de la fuente nueva: **30.655 B, sha256 `d1b8ff00b511…`** → **IGUAL** al disco por crudo y por forma normalizada. La publicación no se creyó por el título |
| Población | **57 → 58 fuentes**. Las dos anteriores (`01a10853-6da2…` y `01a0e4d9-b252…`) quedan **intactas y `ready`**: título nuevo **sin borrar**, que es la convención del 2026-09-27 |
| Frescura después | `verify_qmind_context_freshness.py --strict` → **EXIT 0**, `2 fresco(s), 0 problema(s)`: el `10-analisis` casa con la fuente nueva `01a10e39-1625…` y el `CONTEXT` con `01a0efcc-3297…`. **0 `[SIN-DESCARGA]`** en esta corrida |
| El writer del flujo, re-corrido | `validate_qmind_writeback.py --strict` → `[PASS] 13/13`, EXIT 0 **antes y después** de la publicación. No se movió: su criterio es el título, así que nunca vería el contenido cambiado. Compra de una vez las dos cosas que esta hoja venía declarando |
| Flakiness en números | descarga PRE: 1 er intento EXIT 1 (`QMind network request failed`), 2º EXIT 0; upload: 1er intento EXIT 0; descarga POST: 1 er intento EXIT 1, 2º EXIT 0. La B2-4 también aplica al CLI suelto |

**Qué cierra y qué no cierra este acto.** Cierra el **vencido real** de §9.1: lo publicado ya no son los bytes
posteriores al cierre de FASE-B, sino los del cierre de FASE-RELEASE, probado por descarga. **No** convierte
AC-R6 en pleno: el literal del mandato pedía `validate_qmind_writeback.py --upload`, y ese comando **sigue sin
ejecutarse** — con la razón ya no alegada sino medida: si se corriera, `is_ingested()` decide por nombre del
plan y respondería SKIP, dejando la versión vieja como verdad publicada. AC-R6 queda entonces **PARCIAL en su
literal y CUMPLIDA en su sustancia**, que es lo que hay que leer de la casilla.

**Lo que se abrió y no se verificó (declarado, no curado).** El CLI expone `qmind source delete <source_id>`,
mientras el executor y el contrato afirman que QMind no tiene borrado — premisa sobre la que descansa que el
SKIP del writer sea permanente. **No se invocó**: borrar es irreversible, no estaba autorizado, y la política de
«título nuevo sin eliminar la anterior» sigue siendo la vigente. Queda como premisa a reabrir por su dueño con
evidencia, no por esta hoja.

### Anotaciones que este acto vence

- **§11, cláusula de write-back**: «Write-back: sin ejecutar» quedó vencida por esta sección. Las demás
  cláusulas de ese párrafo (cero inferencias, cero credenciales impresas) siguen vigentes.
- **§9.1**: la fila del `10-analisis` marcada «vencido real» está cerrada; la del `CONTEXT` ya era falsa y sigue
  siendo fresca. Ninguna de las dos casillas gobernadas queda hoy vencida.
- **§13 (permisos)**: «Write-back, etiqueta de adopción, D7/D6 y las decisiones de REL-1/REL-2/REL-5: sin
  ejecutar y sin ofrecer» — la primera parte se cumplió por instrucción separada; las otras tres siguen igual.

---

## 15. La fuente frágil del `CONTEXT`: el verificador baja lo que ya le dicen (2026-10-05)

Orden del operador: «estampa el 15 con la fuente frágil del CONTEXT, commitea y envía». Crudos `40-` (la
caracterización), `38-` (frescura post-write-back) y `12-`/`13-` (las tres corridas del corte 1).

**El fenómeno, en números de esta sesión.** El gobernado `CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21.md`
tiene **una sola** fuente cuyo contenido casa: `01a0efcc-3297-7782-9467-757fe81018fc`. Las otras dos que lo
nombran por título no casan (`01a0e4d9-e442…` publica `fileSha256 04242f497c1b`, 17.263 B contra los
17.272 B del disco). Sobre esa única fuente hay **tres mediciones distintas**: (a) el crudo `40-` registra una racha de 3 descargas directas **0-0-0** (los tres `exit 0`, 17.272 B y sha `5587f27ddd5a…` cada una); (b) su apéndice registra las **dos corridas del verificador en el tip empujado donde esa misma descarga devolvió `salio 1`** y el veredicto salió `[VENCIDO]` (EXIT 1, «1 fresco, 3 problemas», dos `[SIN-DESCARGA]` por corrida); (c) una tercera racha de 3 intentos directos, **no persistida en crudo**, dio **1-1-0** y se declara acá como medida sin evidencia adjunta, que es la forma honesta de contarla. El verificador, mientras tanto, imprimió **`[VENCIDO]` con `[SIN-DESCARGA]`**
en dos corridas del tip empujado (EXIT 1, «1 fresco, 3 problemas») y **`[FRESCO]`** en las otras dos (EXIT 0,
«2 fresco(s), 0 problema(s)» — la del crudo `40-` y la del crudo `38-`) — **con el mismo sha de disco en
cuatro corridas**: `5587f27ddd5a52de…`,
17.272 B, y `git diff` vacío sobre ese archivo, o sea esta sesión no lo tocó ni una vez.

**Lo que el servidor ya publica y el instrumento no mira.** `qmind source list --format json` trae, por
cada fuente, `metadata.fileSha256` y `metadata.fileSize`. Para la que nos importa:

| Fuente | `metadata.fileSha256` | `fileSize` | vs disco (`5587f27ddd5a52de…`, 17.272 B) |
|---|---|---|---|
| `01a0efcc-3297-7782-9467-757fe81018fc` | `5587f27ddd5a52de…ed42d914` | 17.272 | **IGUAL** |
| `01a0e4d9-e442-7d1b-bde5-7e9b669a2701` | `04242f497c1bf086…05df2ea16` | 17.263 | distinto |

Es decir: **la identidad que el verificador persigue descargando hasta 58 fuentes ya viene escrita en la
lista**, sin una sola descarga. Su diseño actual convierte un fallo de red en «no casa», y ahí nace el
`[VENCIDO]` falso. La cura con la evidencia encima de la mesa es de dos pasos, y ninguno es re-bajar la
aserción:

1. decidir la frescura por `metadata.fileSha256` (fuente barata, determinista, cero descargas), y
2. usar la descarga+sha256 solo como **verificación de la promesa del servidor** —y cuando la descarga
   falle sobre la fuente que por metadata sí casa, emitir **`NO-EVALUABLE` con su motivo**, no `VENCIDO`.

**Por qué esto no es un problema de contenido, y por qué no se arregla re-publicando.** El disco del `CONTEXT`
está igual que cuando se publicaron las fuentes; lo único que varía entre una corrida y otra de este día es
si el borde de QMind respondió. Re-publicar el `CONTEXT` «para que vuelva a estar fresco» sería pegar contra
un síntoma: crearía una fuente nueva (58 → 59) con los mismos bytes, y el verificador seguiría dependiendo de
la misma descarga. Tampoco se toca el `10-analisis`: esa publicación **sí** tenía materia (los bytes del
cierre) y ya quedó hecha y verificada por descarga en §14.

**Deuda y su límite.** Se registra como **REL-6**: dueño `scripts/verify_qmind_context_freshness.py`
(instrumento heredado del hermano), criterio la deuda B2-4 / el hallazgo H15 de esta hoja, con la
advertencia de que la cura cambia un **contrato de verificación** — el nombre del artefacto dice
«descarga + sha256» — así que su dueño tiene que decidir si el contrato se re-escribe o si la metadata entra
como primera vía con la descarga de respaldo. **No se abre aquí, y no se anota en el `10-analisis`**:
escribirlo ahí volvería a vencer el archivo que esta sesión acaba de publicar en QMind, y la deuda no vale
ese costo. Vive en el registro de la fase, que no es fuente gobernada.

**Verificación al estampar esta hoja.** `verify_qmind_context_freshness.py --strict` en el árbol del sello:
**EXIT 0**, `2 fresco(s), 0 problema(s)`, **0 `[SIN-DESCARGA]`** — el `CONTEXT` casa con `01a0efcc-3297…` y
el `10-analisis` con `01a10e39-1625…`. El rojo de las dos corridas anteriores del tip no queda «curado» por
esta línea: queda **reproducido y explicado**, con la fuente, los números y la cura propuesta.
