# CURA B2-1 / B2-1c — contabilidad de coste en `report` (2026-10-09)

Sesión de curación con mandato del operador sobre la deuda que FASE-RELEASE dejó con dueño.
Criterio aplicado: **AC4** del maestro (`Comparación ... tokens y contabilidad de coste separada`).
Nada de esta hoja toca `FASE-C/`: sus artefactos se re-emiten a esta carpeta y los originales se
dejan intactos (medido con `git status --porcelain evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-C/`
→ vacío).

## Las dos filas que se cierran

| Fila | Lo que decía la deuda | Lo que hace el instrumento hoy |
|---|---|---|
| B2-1 | `report` no compara `usage_normalized` contra `limites_gasto.tokens_in/tokens_out` ni publica `cost_calculated`/`cost_billed` | `contabilidad_de_coste()` produce, por brazo, `tokens` (suma / máximo / n observaciones / filas sin medida por estado), `contra_techos` (techo, medido, exceso o margen restante, filas fuera, veredicto) y las dos columnas `cost_calculated` y `cost_billed`. Entra en `por_brazo[brazo]["contabilidad"]["coste"]` |
| B2-1c | el exceso de 145 observado por C contra el techo congelado de 139 no lo publica ningún instrumento | veredicto `EXCESO` con `exceso_sobre_el_techo` y las `filas_fuera_del_techo` nombradas, más la señal mecánica `S6` por brazo excedido. `decide` no cambia de estado por el exceso (AC5): el diente está escrito |

## Hallazgo medido en esta sesión: la deuda estaba sub-contada

No es un arreglo cosmético, es un número que no estaba publicado. Crudo: `05-cuenta-publicada-vs-cuenta-al-cerrar.txt`.

- La deuda citaba **un** exceso (jev 145 sobre 139, +6). Medido hoy sobre los registros versionados de
  C: **dos brazos** rebasaron el techo de salida — jev 145 (+6) y **deepseek 158 (+19)**. El brazo
  comparador pasó el techo en dos filas, la mayor con +19, y ningún instrumento lo decía.
- La causa por la que no estaba: el brazo comparador **no pasó por `run`**. Lo corrió
  `FASE-C/12-arnes-correr-deepseek-eval.py`, que lee `_estado_cuenta(OUT)`, aplica
  `reservar_presupuesto` por envío y suma con la misma aritmética del runner, pero **no persiste**
  `consumo.json`. Medido en disco: `consumo.json` quedó en `llamadas_usadas: 2 / tokens_out_max: 145`
  (la foto de jev), mientras `registro_deepseek.json` estampa `cuenta_al_salir` con
  `llamadas_usadas: 4 / tokens_out_max: 158`. O sea: la cuenta publicada se quedó en la mitad de los
  envíos reales.

Las dos filas **capa_fria** (cero envíos, cero medida) salen `NO-EVALUABLE` con su motivo, no `DENTRO`
ni cero: es el diente que la casa exige (AC10, "ausencias y fallos no se computan como ceros favorables").

## Decisiones de diseño, con su causa

- **`cost_calculated` sin tarifa es `NO-EVALUABLE`, no un cero.** Medido el 2026-10-09:
  `config/provider_registry.yaml` no tiene ninguna entrada para `jev-1.13.0` ni para DeepSeek
  (`grep -iE "deepseek|jev|typesafe"` sobre ese archivo devuelve 0 líneas; las tarifas por 1M que hay
  son de Gemini). La columna se calcula sola el día que el protocolo congele
  `limites_gasto.precios_por_mtok.{input,output}`; el diente `test_cost_calculated_con_tarifa_casa_con_el_calculo_a_mano`
  fija la aritmética (1788/1e6×0.30 + 150/1e6×2.50 = 0.0009114) para que ese camino no se escriba sin test.
- **`cost_billed` no se inventa.** El cargo lo dice el proveedor; sin fila que lo traiga persistido la
  columna es `NO-OBSERVADO` con `usd: null`. Con filas que lo traen, suma (`0.001 + 0.002 = 0.003`, diente propio).
- **El exceso no es un veredicto del modelo.** `S6` publica y `decide` sigue negándose: sobre los
  registros de C la re-emisión da `run_status=INCOMPLETO` / `decision=null`, idéntico a lo versionado
  (`02-decide-re-emitido-C.json`). Convertir el exceso en `FALLIDO` o en `RECHAZAR` sería un cambio de
  la regla congelada, y la regla la mueve el operador con protocolo nuevo, no esta sesión.
- **`margen_restante_bajo_el_techo` existe para que DENTRO no se exprese como exceso negativo.**
  La primera versión publicaba `-56`; ese número mentía. Ahora: EXCESO → exceso 6 y margen None;
  DENTRO → exceso None y margen 780/9/0.

## Deuda nueva que esta sesión produce: una curada aquí, una abierta con dueño

| Fila | Hecho medido | Dueño | Criterio | Estado |
|---|---|---|---|---|
| B2-1d | la cuenta de etapa la persiste solo `run`; los arneses de brazo (`11-`, `12-`) reimplementan la aritmética y no escriben `consumo.json`, así que la cuenta publicada diverge de la cuenta real (2 vs 4 llamadas, 145 vs 158) | que los brazos pasen por `run`, o que el arnés use el persistidor de la casa — `scripts/evaluate_jev_pilot.py` (`run` / `_estado_cuenta` / `_persistir`) | AC8 | **ABIERTA con dueño** |
| B2-1e | `reservar_presupuesto` cortaba por llamadas agotadas, reintentos, timeout y techos en null sin autorización, pero **nunca** comparaba los tokens observados contra `tokens_in`/`tokens_out` antes del siguiente envío: un exceso descubierto en el envío N no impedía el N+1. Cobertura medida **antes** de la cura: `tests/quality_gates/jev_pilot/test_jev_pilot_run_guards.py` tenía 23 funciones y ningún corte por tokens observados | `scripts/evaluate_jev_pilot.py` (`reservar_presupuesto`) | AC8 y maestro §115 ("falta o agotamiento impide la siguiente llamada") | **CURADA aquí** (decisión del operador) |

### La cura de B2-1e y su consecuencia sobre el expediente de C

`reservar_presupuesto` recorre ahora los dos techos contra la cuenta (`tokens_in_max` /
`tokens_out_max`) y, si lo observado pasa el techo, agrega
`techo_rebasado_de_<campo>:<observado>><techo>` y publica `exceso_observado` con sus números. La
comparación es de **tipo y valor**: un `True` en la cuenta no es un token de 1 (el mismo error que ya
se curó en el guard del preflight), y un techo `null` no tiene con qué comparar, así que no inventa
corte. La frontera es `>` y no `>=`: 139 contra 139 reserva.

Dientes en `test_jev_pilot_run_guards.py` (23 → **31** funciones): la reserva suelta, la frontera, el
techo null, el booleano, los dos campos a la vez, **el par 2 negado dentro de `run`** con el transporte
inyectado (`envios == 1`, cero llamadas al segundo, la fila negada con su motivo en el ledger) y la
cuenta persistida que niega la corrida entera. Contrafactual M3 (crudo `06-`): si
`limites_desde_protocolo` no traslada los techos, el guard es letra muerta y se envían los dos pares;
la restauración se verifica dentro del mismo test.

**Lo que hay que saber antes de la corrida de 60 pares**: el `consumo.json` versionado de FASE-C trae
`tokens_out_max: 145` contra el techo congelado 139, así que cualquier `run` del brazo jev que **entre**
en ese `out_dir` se niega entero antes de construir cliente. Es el comportamiento correcto (esa cuenta
ya rebasó su techo) y no un obstáculo: la corrida nueva abre su propio `out_dir`.

## Instrumento y prueba

Batería nueva: `tests/quality_gates/jev_pilot/test_jev_pilot_report_coste_b2_1.py` — **24 funciones test**
(método canónico `grep -rE "^\s*def test_" tests/quality_gates/jev_pilot/test_jev_pilot_report_coste_b2_1.py | wc -l`).

| Comando | Salida |
|---|---|
| `./venv/Scripts/python.exe -m pytest tests/quality_gates/jev_pilot/test_jev_pilot_report_coste_b2_1.py -q` | 24 passed |
| `./venv/Scripts/python.exe -m pytest tests/quality_gates/jev_pilot/test_jev_pilot_run_guards.py -q` | 42 passed (31 funciones: 23 en HEAD + 8 de B2-1e; el parametrizado rinde 4 casos) |
| `./venv/Scripts/python.exe -m pytest tests/quality_gates/jev_pilot -q` | **173 passed** (141 antes de la cura + 24 de B2-1 + 8 de B2-1e) |

Contrafactuales ejecutados (crudo `04-crudo-controfactuales-y-anclas.txt`):

- **M1** `runner_fresco._entero_o_none = lambda v: None` → el veredicto pasa a `NO-EVALUABLE` y `S6`
  desaparece; el diente del exceso pierde. Restauración verificada en el mismo test (revierte a EXCESO).
- **M2** `ESTADOS_USAGE_OBSERVADOS` tragándose `sin_usage` y `no_intentada` → la ausencia deja de
  publicarse (`filas_sin_medida_por_estado == {}`) y una fila sin medida cuenta como fila con envio;
  cae el diente `test_las_filas_sin_medida_se_cuentan_por_estado_no_como_cero`. Restauración verificada.
- **Frontera** 139 contra 139 es `DENTRO` con margen 0: un `>=` en lugar de `>` pierde ese verde.
- **M3** (crudo `06-`) `limites_desde_protocolo` sustituido por una versión ciega que no traslada los
  techos: el guard de B2-1e deja de cortar y `run` envía los dos pares. Prueba que el corte depende del
  traslado protocolo→límites, no del fixture. Restauración verificada en el mismo test.

## Artefactos de esta hoja

| Archivo | Qué es |
|---|---|
| `01-informe-con-coste-C.json` | re-emisión de `report` sobre los insumos versionados de C, con el bloque `coste` (fecha 2026-10-09) |
| `02-decide-re-emitido-C.json` | re-emisión de `decide` sobre ese informe: `INCOMPLETO` / `decision=null` |
| `03-crudo-pytest-seleccion-jev.txt` | la selección completa del piloto, 173 passed (re-capturada tras B2-1e) |
| `04-crudo-controfactuales-y-anclas.txt` | los dos mutantes y las dos anclas al árbol versionado, con su selección |
| `05-cuenta-publicada-vs-cuenta-al-cerrar.txt` | el hallazgo: 145 publicado contra 158 real, y 2 llamadas contra 4 |
| `06-crudo-cura-b2-1e-y-gates.txt` | los dientes del corte nuevo, su contrafactual M3, el conteo canónico y los dos gates |
| `07-crudo-atribucion-de-los-dos-rojos.txt` | los dos rojos de la suite grande: el de packs (preexistente, dueño `5249aed`) y el de colección, con su disparador nombrado y su mecanismo medido |
| `08-crudo-sello-commit-y-gate.txt` | el commit `ec69570`, el gate re-apuntado visto desde HEAD, el quick gate en 13/13 y la paridad antes del push |
| `09-crudo-sello-push.txt` | el rango empujado, la paridad `0 0`, el tip del servidor y el pre-flight que prueba que las rutas ajenas no entraron |

Comando con el que se re-emiten `01-` y `02-` (una línea, ejecutado en esta sesión; la segunda corrida
dio el mismo sha256 en los dos archivos, o sea la re-emisión es byte a byte):

```text
./venv/Scripts/python.exe -c "import importlib.util as u,json;from pathlib import Path as P;s=u.spec_from_file_location('e','scripts/evaluate_jev_pilot.py');m=u.module_from_spec(s);s.loader.exec_module(m);E=P('evidence/EVALUACION-JEV-TYPESAFE-2026-09-21');o=E/'CURA-B2-1-2026-10-09';p=json.loads((E/'protocolo.json').read_text(encoding='utf-8'));i=m.report(respuestas=E/'FASE-C'/'respuestas.jsonl',etiquetas=E/'etiquetas.json',muestra=E/'muestra.json',protocolo=E/'protocolo.json',fecha='2026-10-09');m._persistir(o,'01-informe-con-coste-C.json',i);m._persistir(o,'02-decide-re-emitido-C.json',m.decide(informe=i,protocolo=p,fecha='2026-10-09'));print('veredicto jev:',i['por_brazo']['jev']['contabilidad']['coste']['veredicto_exceso'])"
```

| sha256 (16 primeros) | antes | despues |
|---|---|---|
| `01-informe-con-coste-C.json` | `849a5d2a8540ce49` | `849a5d2a8540ce49` |
| `02-decide-re-emitido-C.json` | `4442d51c5fad5b28` | `4442d51c5fad5b28` |

El comando persiste con `_persistir` de la casa, asi que los dos JSON formatean igual que los
artefactos versionados de FASE-C. Nota de instrumento: esta hoja **no añade ningun `.py` bajo
`evidence/`**, a proposito -- los arneses `.py` mueven los contadores del `wiring_report` y obligan a
re-publicarlo (cobrado en la ronda del 2026-10-05: 132 a 137 y EXIT 3).


## Lo que esta sesión NO hizo (límites declarados)

- No editó ningún documento del plan (`01-plan-maestro.md`, `06-checklist`, `10-analisis`, README). Las
  filas B2-1/B2-1c del `10-analisis` quedan **sin estampar** aunque el código ya las cumple: esa hoja ya
  está publicada en QMind (59 fuentes) y cada edición de contenido obliga a re-verificar por descarga +
  sha256 y a sumar una fuente. Es decisión del operador, con su mando y su coste publicado.
- No escribió en `REGISTRY.md`. El registro de fases lo escribe `scripts/log_phase_completion.py` al
  cerrar, y esta hoja aún no está cerrada documentalmente.
- No corrió `build_lesson_index.py` ni `sync_versions.py`: no hay lección nueva ni versión que mover.
- No llamó a ninguna API: toda la sesión es offline y el guard de sockets del `conftest.py` estuvo armado. ⟦Sello del commit `ec69570` (2026-10-09): el «No commiteó» de esta viñeta quedó vencido por autorización escrita del operador; el push, acto aparte, ya esta estampado abajo con su paridad medida.⟧
- No tocó `modules/providers/llm_provider.py`, `requirements.txt` ni `VERSION.yaml`.

## Los cinco cortes, medidos

| Corte | Estado | Medición |
|---|---|---|
| Implementación terminada | **HECHO** | `contabilidad_de_coste` + `columna_de_tokens` en `scripts/evaluate_jev_pilot.py`, cableadas en `report()` y en `senales_mecanicas()` (S6); bateria nueva de 24 funciones en `tests/quality_gates/jev_pilot/test_jev_pilot_report_coste_b2_1.py` |
| Verificacion terminada | **HECHA** | seleccion del piloto **173 passed** (141 al abrir + 24 de B2-1 + 8 de B2-1e); `validate_wiring.py --check` **EXIT 0** tras re-publicar con el writer (`cobertura.archivos_en_alcance` 713 → 714 por el `.py` nuevo); `run_all_validations.py --quick` **12/13** |
| El unico rojo del gate no es de esta sesion | **ATRIBUIDO** | `[13/13] Briefing Packs` DIVERGE por `04-contrato-ejecucion.md` del hermano VERIFICADOR-CONTEXTO: el pack versionado espera `39c8b094489b3703ddd707d3` y el arbol del commit trae `1065b1c744b65d54`. Medido con `git show HEAD~4:<ruta>` (39c8b094) contra `git show HEAD:<ruta>` (1065b1c7); la movio `5249aed` (chore de archivado del 07-08) sin re-corrida de packs. Dueño: la tanda que archivo, no esta cura |
| Cierre documental | **NO HECHO, a proposito** | no se estampan las filas B2-1/B2-1c del `10-analisis` (esa hoja vive publicada en QMind: cada edicion obliga a re-verificar por descarga + sha256 y suma una fuente, 59 → 60), no se escribio leccion nueva, no se toco `REGISTRY.md`, no se movio `AGENTS.md`. Nota de instrumento: `validate_governance_numbers.py` dio **[SIN-HALLAZGOS]** con los 24 tests ya en el arbol, asi que ninguna cifra publicada quedo desfasada por esta sesion |
| Listo para revision / espera de autorizacion | **AQUI** | el `git commit` no es condicion de ninguno de los cortes anteriores; queda en manos del operador |
| Commiteado | **HECHO tras destrabar el gate** | `ec69570`, 19 rutas, los 8 checks del hook verdes; el push queda como acto aparte |
| Commiteado y empujado | **HECHO tras destrabar el gate** | `ec69570` + sello `923979b`, 20 rutas en el rango, los 8 checks del hook verdes; push `5249aed..923979b` con paridad `0 0` y tip del servidor `923979be0273` (crudo `09-`) |

### Hallazgo sobre REL-5 (no curado aquí, con dueño)

El rojo que la suite grande imprime en `test_jev_pilot_deepseek_brazo.py` estaba registrado como
«dependiente del orden de colección» (REL-5 / D5). Medido hoy tiene **nombre y mecanismo**: el
disparador es `tests/quality_gates/test_fase_d_veredicto_canonico.py`, que importa `main`, y
`main.py:17` ejecuta `load_dotenv()` al importarse y mete `DEEPSEEK_API_KEY` en `os.environ`
(comprobado por presencia, sin imprimir el valor: `False` antes de importar `main`, `True` después).
El test del brazo está escrito sobre la premisa «no hay credencial», así que pasa en su archivo y en
la selección del piloto, y cae cuando otro módulo cargó `.env` en el mismo proceso. **No depende del
orden**: con los dos archivos en orden invertido también cae. La cura hermética cabe en una línea, pero
REL-5 está declarada terminal por decisión del operador y abrir aquí su sesión excedía este mandato.
Crudo: `07-`.

## Sello del commit ec69570 (2026-10-09)

Lleva 19 rutas: el runner curado, las dos baterías, los 8 artefactos de esta hoja, `wiring_report.json`
re-publicado, los 5 packs regenerados del hermano, el hook versionado y sus dos dientes nuevos.
2089/80 líneas. `git show --stat` en crudo `08-`.

**Lo que hubo que destrabar para poder commitear.** El gate `[8/8]` corría
`verify_packs_in_committed_tree.py` con su default `--rev HEAD`, y en un pre-commit HEAD es el **padre**
del commit que se intenta. Como `5249aed` movió la fuente proyectada sin sus derivados, HEAD estaba
divergente: el gate cortaba **todo** commit del repo, y el commit que repara esa divergencia no podía
aprobarse a sí mismo. Medido en el árbol staged: `--rev HEAD` → DIVERGE/EXIT 1, y el mismo verificador
sobre el índice → **5/5 reproducidos, 0 divergentes, EXIT 0**. El hook ahora materializa el árbol del
índice (`git write-tree` + `git commit-tree -p HEAD`) y, si eso falla, cae a HEAD **con aviso impreso**;
no se apaga ningún corte. Dos dientes nuevos en `tests/test_hook_precommit_packs_check.py` (8 passed en
total) con su mutante, y el hook reinstalado con `install_git_hooks.py` (el test de identidad instalado≡
versionado es el que obliga a reinstalar).

Consecuencia verificada después del commit: `verify_packs_in_committed_tree.py` en su default da
**5/5 reproducidos en HEAD** y `run_all_validations.py --quick` vuelve a **13/13**. El repo queda
commiteable para cualquier tanda, que es lo que este gate no podía hacer desde `5249aed`.

## Sello del push (2026-10-09)

Rango empujado `5249aed..923979b` (2 commits, 41 objetos, 20 archivos, 2142/80 lineas). Paridad
re-midida despues del push: `git rev-list --count --left-right master...origin/master` = **0 0** y
`git ls-remote origin refs/heads/master` = `923979be0273`, igual al tip local. Pre-flight antes de
empujar: `git diff --name-only origin/master..HEAD | grep -c REFACTOR-WHATSAPP` = **0**, o sea las 13
rutas ajenas que siguen staged en esta maquina no entraron en el rango. Crudo: `09-`.

**Lo que publica este rango y lo que no.** Publica la cura del runner, las dos baterias, el expediente y
el gate `[8/8]` re-apuntado. **No** publica el estampado de las filas B2-1/B2-1c/B2-1e en el `10-analisis`
(sigue pendiente su edicion y el write-back con la fuente 60), ni REGISTRY de esta tanda, ni leccion
capitalizada: los tres quedan en la cola de la sesion 2 por decision del operador. **L3 (revision de
seguridad profunda): NO corrida**; dueno el operador, rango medido para ese escaneo `5249aed..923979b`.

Esta hoja se commitea y se empuja **despues** de medir esa paridad, asi que el commit que estampa el sello queda deliberadamente fuera de su propia cobertura: se re-mide con `git rev-list --count --left-right master...origin/master` y con `git ls-remote origin refs/heads/master`, no con un sello nuevo que vuelva a quedar atras (leccion cobrada en la tanda del 2026-10-05).

## Cola de autorizaciones (cada una con su puerta, no se infieren entre si)

1. **Commitear la tanda** — **HECHO en `ec69570`** (19 rutas: `scripts/evaluate_jev_pilot.py`, la bateria nueva de B2-1,
   `test_jev_pilot_run_guards.py` con los dientes de B2-1e, los 7 artefactos de esta carpeta y
   `.opencode/wiring_report.json` re-publicado). Ojo: el indice tiene ademas 13 rutas ajenas stageadas
   por un tercero a las 10:43:35 de hoy (`briefing/` del REFACTOR-WHATSAPP y un `captura_stdout.txt`);
   por decision del operador se dejan como estan, asi que el commiteado va **por nombre**, no con `git commit` a secas.
2. **Regenerar los briefing packs del hermano** para cerrar el rojo `[13/13]`, o dejarlo con su dueño.
3. **Estampar B2-1/B2-1c en el `10-analisis`** con la medicion nueva (dos brazos, no uno) y pagar su
   re-publicacion en QMind.
4. **Curar B2-1d** (que la cuenta de etapa la escriba `run` tambien cuando el brazo lo despacha un
   arnes), o decidir que la corrida nueva de los brazos pasa por `run` y la fila cierra sola.
5. **Leccion + REGISTRY** al cerrar documentalmente la fase (`scripts/log_phase_completion.py`), si esta
   hoja cierra como fase y no como curación suelta.


Muestra objetivo **60 pares, mitad eval**; `limites_gasto.usd` **sigue null declarado**. Cadena:
(b) generar candidatos desde los 324 pares citados del índice → **(a) esta cura, hecha, y B2-1e
también curada** (el techo ya rebasado corta el siguiente envío) → (c) protocolo v2 con techos de
llamadas/tokens y splits, congelado antes de evaluar → tu etiquetado de los 60 pares → corrida C nueva
con mandato y presupuesto → `decide` emite `ACTIVAR`/`RECHAZAR` → firma del operador.
Sigue abierto B2-1d (la cuenta de etapa) y el estampado documental de las filas B2-1/B2-1c/B2-1e.

---

## Addendum de la SESIÓN 2 (2026-10-09): la hoja cierra documentalmente

Esta sección es aditiva. Lo que la sesión 1 dejo abierto en esta hoja quedó cerrado hoy, y se re-mide
antes de afirmarlo: el tip de arranque era `fb13108` (paridad `0 0` con `origin/master`), la selección del
piloto abrio en **173 passed** y el quick gate en **13/13**.

| lo que la sesión 1 dejó dicho | estado medido hoy | dónde queda la prueba |
|---|---|---|
| «Sigue abierto B2-1d (la cuenta de etapa)» | **CURADO.** `registrar_envio_en_cuenta()` en `scripts/evaluate_jev_pilot.py` suma y publica la cuenta de etapa en el mismo acto, y por envío. Decisión por costo: la alternativa («que el brazo pase por `run`») duplicaba la costura que el mandato de FASE-B prohíbe, así que se cerró por el persistidor de la casa. No se tocó `modules/providers/llm_provider.py`. | `tests/quality_gates/jev_pilot/test_jev_pilot_cuenta_etapa_b2_1d.py`, **9 funciones**; crudo `10-`; contrafactual a nivel de archivo: la batería contra el runner versionado en `fb13108` da **7 rojos / 2 verdes** y la restauración se verifica por sha256 (`4a26552237be9c84`) |
| «no se estampan las filas B2-1/B2-1c/B2-1e del `10-analisis`» | **ESTAMPADO**, en modo anotación aditiva (la tabla de seguimientos queda intacta: `git diff --numstat` = 53/0). sha256 de disco antes `ee40f5ee52ff…` (coincide con el blob de HEAD), después `b88e3e08a70d…`. | `10-analisis-post-implementacion.md` (anotación 2026-10-09) y crudo `11-` |
| «cada edición obliga a re-verificar por descarga + sha256 y a sumar una fuente» | **HECHO.** Write-back por el writer de la casa con título nuevo que conserva el stem; verificación por **descarga + sha256 contra el disco**, no por título. | crudo `13-` |
| la población `59 → 60` que traía el mandato | **RE-ANCLADA POR MEDICIÓN.** El notebook `iah-cli-lecciones` tenía **61** fuentes publicadas antes de la subida y **62** después; las cuatro publicaciones previas del stem siguen `ready` con su título intacto (verificado por `id`, no por título). El 59 es el dato de la tanda del 2026-10-08. | crudo `13-` §2 y §3 |

**Hallazgo nuevo de la sesión 2, con número.** El estampado se escribió **tres veces**: tres ediciones
reportadas como bloqueadas por el clasificador escribieron igualmente, y una anotación hermana perdió su
`⟧`. Se midió por conteo de copias y balance de delimitadores, y se curó en la misma sesión (crudo `11-` §3).
La regla que sale —un bloqueo notificado no prueba que la herramienta no escribió; se cuenta el resultado en
disco— queda enunciada en `§2` del contexto de lecciones **sin ID**, porque aún no tiene instrumento que la
haga cumplir.

**Lo que esta sesión NO hizo.** No corrió inferencias ni autenticó credenciales (el guard de sockets del
`conftest.py` estuvo armado y la selección lo ejerce); no escribió en `FASE-C/` (el arnés que fundo el
hallazgo se lee, no se re-escribe: su ancla está en el test `T7` de la batería nueva); no abrió la corrida de
60 pares ni FASE-C; no movió `VERSION.yaml`, `AGENTS.md` ni `modules/`; no tocó las 13 rutas ajenas que siguen
staged en esta máquina. `REL-5` (hermeticidad del brazo por el `dotenv`) sigue **terminal por decisión del
operador**: su cura cabe en un fixture autouse y está descripta, no ejecutada.

**Cierre documental de esta hoja (medido, no prometido).** Selección del piloto **182 passed** (173 + 9) y
**190 passed** con los 8 dientes del hook; `validate_wiring.py --check` **EXIT 0** con
`cobertura.archivos_en_alcance` **714 → 715** re-publicado por el writer; `build_lesson_index.py --check`
**EXIT 0** con **368 IDs** (365 → 368 por `L-JEV.C1/C2/C3`, definidos en
`.opencode/context/CONTEXT-JEV-CURA-B2-1-2026-10-09.md`); `run_all_validations.py --quick` **13/13**;
`REGISTRY.md` escrito con `scripts/log_phase_completion.py` (primero `--dry-run`), 7 rutas nuevas y 7
modificadas declaradas como rutas, no como conteos.

**Frescura, dicha como se midió.** `verify_qmind_context_freshness.py --strict` sobre `10-analisis` dio
**`[FRESCO]` / EXIT 0 en cuatro de cinco corridas de la serie limpia** (`2-0-0-0-0`) y
**`NO-EVALUABLE` / EXIT 2 en la restante**, siempre por una descarga que no bajó (`QMind network
request failed`). **Nunca dio `VENCIDO` después del write-back**: el rojo real que sí dio, antes
de publicar, quedó cerrado por la publicación. Lo que sostiene la afirmación de que la fuente publicada es este cuerpo
**no es la etiqueta del verificador** sino la medición propia: la descarga de `13-` dio
`b88e3e08a70da45f…` con 37874 bytes, idénticos a los del disco, con su racha `0-0-0-1` de reintentos. Un
`NO-EVALUABLE` del instrumento no desdice esa observación, y tampoco la borra.

Queda **vencido y sin curar**, con dueño: `CHANGELOG.md:764-765` (afirma en presente la deuda y el exceso de
un solo brazo; lo cierra quien mueva el próximo release, no esta sesión).

**Hallazgo del censo que esta hoja no tenía: dos celdas de `09-documentacion` dicen `PENDIENTE` donde los
ledger prueban envíos.** `09-documentacion-post-proyecto.md:31` y `:32`, en la celda de la columna C, afirman
que el brazo jev y el comparador no ejercitaron inferencias en FASE-C. Medido contra los artefactos
versionados: `ledger.jsonl` tiene 2 filas jev (1 `EJERCITADO` + 1 `FALLO`, 2 attempts) y
`ledger-deepseek.jsonl` 2 filas `EJERCITADO`; el `registro_deepseek.json` entra con 2 llamadas y sale con 4.
O sea que C sí envió en los dos brazos. **Está vencido desde el cierre de C, no desde esta firma** — la firma
solo lo hace visible, y es la misma forma de `L-JEV.R1`: una fase que mutó el artefacto y no escribió la fila
que lo declara. No se curó aquí (el mandato estampa el `10-analisis`, no el `09`) y queda con dueño: quien
reabra el `09` al cerrar la corrida nueva. Crudo `12-` §6.

**Límite del instrumento, y por eso van DOS conteos en el censo.** Un barrido por patrones de *síntoma* sobre
*líneas* no ve una celda cuyo contenido literal es `PENDIENTE`, y además confunde el sello de una celda con el
de la vecina en la misma fila. El censo se rehízo en tres pasadas (semántica, línea, celda con cabecera de
columna) y reporta 29 líneas / 51 celdas declarando que **las unidades no son comparables**. Lección de
método: en una tabla, el sello y el veredicto son de celda.

**Los cinco cortes, re-medidos al cerrar la hoja.** Implementación terminada (la función y su cableado en
`run`) · verificación terminada (9 funciones, contrafactual a nivel de archivo, gates) · cierre documental
(estampado + lección + índice + `REGISTRY.md` con `log_phase_completion.py`) · listo para revisión (este
addendum y los crudos `10-` a `13-`) · **espera de autorización escrita**: el `git commit` no es condición de
ninguno de los anteriores y queda en manos del operador, con su pathspec nombrado. El push y el escaneo L3 son
actos aparte, cada uno con su línea escrita.
