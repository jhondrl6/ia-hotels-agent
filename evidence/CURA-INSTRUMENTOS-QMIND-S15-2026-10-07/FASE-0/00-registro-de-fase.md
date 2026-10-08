# Registro de fase — FASE-0 (Preparación) del plan CURA-INSTRUMENTOS-QMIND-S15-2026-10-07

**Cerrada:** 2026-10-08 · **HEAD al cerrar:** `98c190e` (igual a `origin/master`, medido con `git ls-remote origin refs/heads/master`) · **Versión vigente del repo:** `4.79.0` (`VERSION.yaml`, sin cambio en esta sesión)
**Naturaleza:** sesión de orquestación (Etapa 1 del executor). **Cero código, cero tests escritos, cero escrituras remotas.**

## 1. Qué se produjo

| Artefacto | Detalle |
|---|---|
| `.opencode/plans/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/` | 14 documentos: `00-lecciones-capitalizadas.md`, `01-plan-maestro.md`, `04-contrato-ejecucion.md`, `dependencias-fases.md`, `06-checklist-implementacion.md`, `09-documentacion-post-proyecto.md`, `10-analisis-post-implementacion.md`, `README.md` y seis prompts `05-prompt-inicio-sesion-fase-{A1,A2,A3,B,C,RELEASE}.md` |
| `evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-0/` | `quick_apertura.txt`, `quick_cierre.txt`, `pre_seleccion_apertura.txt` y este registro |
| Derivados regenerados con su escritor | `.opencode/LECCIONES-INDEX.md` (58+/50−) y `.opencode/lecciones_index.json` (340+/87−), medidos con `git diff --numstat` |

## 2. Mediciones de la sesión (todas con su comando)

| # | Superficie | Comando | Resultado impreso |
|---|---|---|---|
| M1 | Tip y paridad | `git rev-parse HEAD` / `git rev-parse origin/master` / `git ls-remote origin refs/heads/master` | los tres en `98c190e` — **refuta** las dos filas del mandato (`HEAD = 83a6dc2`, `origin = 649114c`, «2 commits sin empujar»): son cuatro commits y ya están empujados |
| M2 | Árbol | `git status --porcelain -uall` | al abrir: 12 `briefing/FASE-*.md` del plan padre y `evidence/…/FASE-E2E/captura_stdout.txt`, todos **untracked y ajenos** — preservados, no stageados, declarados (maestro S-CIM-7). Al cerrar se suman las 14 rutas propias del plan y los dos derivados modificados |
| M3 | Corpus escaneado por el control S15 | `git diff --name-only 086ce65..HEAD -- .opencode/` | **20 rutas** de diferencia, incluidos los `git mv` que archivaron el plan del padre y la regeneración del par del índice — **refuta** el uso de la medición del mandato como insumo vigente de FASE-B |
| M4 | Quick de apertura | `python scripts/run_all_validations.py --quick > …/quick_apertura.txt 2>&1; echo "EXIT=$?" >> …` | `TOTAL: 13/13 validations passed`, `EXIT=0` (verificado leyendo el archivo con `grep -a`, no de memoria) |
| M5 | Selección de las dos familias | `python -m pytest tests/test_build_lesson_index_s15_fecha_versionada.py tests/test_validate_qmind_writeback_escritura.py -v > …/pre_seleccion_apertura.txt 2>&1; echo "EXIT=$?"` | `1 failed, 26 passed`, `EXIT=1`. El único rojo es `test_el_control_defectuoso_de_la_revision_publicada_si_diverge`, con el mensaje literal `assert ('mtime' == 'mtime' … mtime and 'nombre' == 'mtime' … - mtime + nombre)`. Los 23 dientes del write-back están verdes. **Intérprete usado: Python 3.13.3 del sistema** (el `rootdir` y `configfile: pytest.ini` están impresos en el crudo); la selección no importa módulos del proyecto |
| M6 | Hueco del slug, en disco | `ls -la .opencode/qmind-writeback/instantaneas/` + sha256 por Python | **un** archivo de datos (125.198 B) y su `README.md`, mientras el registro declara **dos** shas distintos: el archivo casa con `1f0ee6e52f008e7413846039e244a8a242b472ba93e59bc933af2bb47e7286e0` (la segunda publicación); `0b02bb5084e3…` no tiene ya con qué casar |
| M7 | Cuerpo crudo del plan padre | sha256 sobre `.opencode/plans/Archives/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/10-analisis-post-implementacion.md` | `3d2184fb2822f38d3b8fe97d55d565d10027373256fd63feb40fa226ee73d28e`, 124.280 B. Comentario de la copia saneada publicada: **+918 B**. Y `git show {83a6dc2,f42c201,98c190e}:<ruta archivada>` dan los **mismos** 124.280 B y el mismo sha: el crudo **no** se editó después de publicar, así que el delta es de las sustituciones del saneado y el VENCIDO de hoy es estructural y estable |
| M8 | Registro | `json.load` sobre `.opencode/qmind-writeback/registro.json` | `schema_version` `1.0`, dos entradas del padre, `fuente_id: ""` en ambas, **sin** `sha_cuerpo` en ninguna |
| M9 | Índice del corpus | `python scripts/build_lesson_index.py --check` (apertura) y `… build_lesson_index.py` (cierre) | apertura: `[OK] fresco (348 IDs)`, `[fechas] nombre=337 commit=11 sin_fuente=0`; cierre: `356 IDs`, `[fechas] nombre=345 commit=11`, `18 análisis`, `449 .md citados`, `79 sin definición` |
| M10 | Paso 0 verificado | `python scripts/validate_lesson_capitalization.py` | `[OK] Capitalización del Paso 0: forma y trazabilidad verificadas` con **8 fuentes capitalizadas** por este plan, y su propio límite declarado impreso («NO verifica pertinencia») |
| M11 | Quick de cierre | mismo comando que M4 sobre el árbol ya curado | `TOTAL: 13/13 validations passed`, `EXIT=0` (`…/quick_cierre.txt`) |

## 3. Hallazgo nuevo de esta sesión, con su medición: el plan se robó IDs del corpus

Al regenerar el índice después de escribir los documentos, `D-1`…`D-3` pasaron a publicarse **con dueño =
CURA-INSTRUMENTOS-QMIND-S15-2026-10-07**, desplazando la atribución que el corpus hacía de esos IDs (citados en
`Archives/DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24`). La causa es de formato, no de intención: `ID_RE` del
generador (`re.compile(r"\b((?:DA|D|L|S)-[A-Z0-9][A-Za-z0-9._-]*)")`) detecta definiciones por convención de
posición, así que **la primera celda de una fila de tabla que empiece con `D-1` es una definición**, aunque la fila
fuera una lista de deudas locales del plan. Dos defectos convivían en el borrador: IDs sin namespace que colisionan
con el corpus, y **numerosidad divergente entre el maestro y el `10-analisis`** (el maestro enumeraba seis
decisiones y el análisis ocho, con los mismos números refiriéndose a cosas distintas).

Curación aplicada y verificada en la misma sesión: la serie de decisiones quedó en `DA-CIM.1`…`DA-CIM.8` (fuente
única en `10-analisis` §Decisiones, enunciada en maestro §2 con los mismos números) y la de deudas en
`S-CIM-1`…`S-CIM-8`. Después de regenerar: `D-1` vuelve a la sección de **citados sin definición** con sus citantes
originales más este plan (mención deliberada y explicada en maestro §2), `DA-CIM.1` y `S-CIM-1` se publican con
dueño = este plan, y `validate_lesson_capitalization.py` sigue en `[OK]`. Queda como registro para FASE-B: el mismo
mecanismo de posicionamiento es el que hace frágil al control S15, así que la lección se aplicó dos veces en la
misma sesión, una de ellas contra el propio documento.

## 4. Rojos y pendientes con dueño

| # | Estado | Dueño | Detalle |
|---|---|---|---|
| R1 | **Rojo conocido, no tocado** | FASE-B | `test_el_control_defectuoso_de_la_revision_publicada_si_diverge` falla determinista contra `98c190e` (M5). No es regresión de esta sesión: es la premisa que el plan viene a curar |
| R2 | **Pendiente por diseño** | FASE-A3 | `[DUPLICADO-VIGENTE]` de la fuente de la era G `01a0bfc9-…`: hoy está tapado por el rojo de vigencia; aparece al curar AC2 y se cierra **declarando con dueño**, no borrando (S-CIM-2) |
| R3 | **Fuera de alcance, nombrado** | operador | `[18/18]` invocado sin `--strict` (deuda S-2 del hermano) — S-CIM-1 |
| R4 | **No certificado** | FASE-RELEASE | AC10: este plan no publicó nada en el notebook. La subida remota requiere autorización literal propia |
| R5 | **No ejecutado** | la fase que lo consuma | Packs de briefing de los prompts nuevos — S-CIM-5 |
| R6 | **No ejecutado, declarado** | — | Modo completo. La preparación no lo corrió; la medición de 15/18 con tres rojos es del cierre del padre y vive en su registro, no se re-transcribe (S-CIM-8) |
| R7 | **No regenerado, con razón medida** | — | `.agent/knowledge/DOMAIN_PRIMER.md`: la preparación no aporta contenido del dominio hotelero y no es fase de implementación; los checks que lo miran salieron verdes (M11). Se regenera al cerrar A1/A2/A3/B/C si la fase trae mandato para escribirlo, y en RELEASE se **verifica** con `doctor.py --context` |

## 5. Registro en REGISTRY: no se ejecutó, y por qué

`log_phase_completion.py` no se invocó para esta sesión. **Medición de la convención, no supuesto:** en
`docs/contributing/REGISTRY.md` no existe entrada de preparación del plan padre (sus entradas son FASE-A…H,
FASE-E2E, FASE-VERIFY, FASE-UNICA del hermano y FASE-RELEASE), y el executor §2.5 reserva el escritor para las
**fases de implementación**, que se registran a sí mismas al cerrar; RELEASE solo verifica. La preparación es la
Etapa 1 de orquestación. Cada fase de código de este plan sí ejecutará su propio registro con `--fecha` real,
`--archivos-mod` medido **después** de los fixers derivados y sin `--release`.

## 6. Derivados: qué se corrió y qué no

| Escritor | Corrido? | Motivo medido |
|---|---|---|
| `build_lesson_index.py` | **sí**, y su `--check` en verde | Esta sesión añadió 14 `.md` que nombran IDs; el índice publica dueño con ruta y conteo de citas (R2.10). Su regeneración es la que destapó §3 |
| `validate_opencode_refs.py --fix` | **no** | El check `[OpenCode References]` salió `[OK]` en M4 y M11: no hay referencias que promover ni corregir |
| `validate_plan_citations.py --update-baseline` | **no** | `[OK] 745 citas historicas, 0 nuevas y 0 crecimientos (81 archivos)`: la fase citó **símbolos**, no `archivo:linea` (R2.2), así que no hay nada que re-baselar. El acto visible no se simula |
| `validate_wiring.py --write-report` | **no** | `[OK]` sin violaciones y **ningún `.py` nuevo** entró al árbol versionado; el reporte no se regenera sin causa |
| `validate_document_integration.py` | sí, por el quick | `[+] Document Integration: All cross-document checks passed` |
| `validate_lesson_capitalization.py` | sí (M10) y por el quick | `[OK]` con límite impreso |
| `doctor.py --regenerate-domain-primer` | **no** | R7 |

## 7. Presupuestos y cortes

**R2.1 — instrumento canónico FUERA DE SERVICIO:** `evidence/FASE-D/measure_iterations.py` pide el transcript del
cliente y su acceso está denegado (medido el 2026-10-07; no reintentado en esta sesión). **Auto-reporte con unidad
declarada:** `tool_use` contados a mano sobre la transcripción propia, **≈62 (banda 60-65)** hasta escribir este
registro, contra la referencia de 60 para una fase. Es la referencia del plan padre en una sesión que además
produjo 14 documentos y 11 mediciones; **no es comparable** con las sesiones que usaron el instrumento, y no se
suma a ningún total. Excedido el número, la consecuencia es checkpoint y **no** ejecutar una segunda fase (R1).

**Cinco cortes:** implementación terminada — *no aplica* (fase documental, declarado) → verificación terminada
(M4-M11) → cierre documental (este registro, sin CHANGELOG/GUIA porque la preparación no cambia el producto y el
mandato prohíbe liberar versión) → **listo para revisión** → espera de autorización. **Commit no ejecutado al cerrar
el documento** (no hubo instrucción literal en el chat hasta ese momento): el árbol quedó con 14 rutas nuevas
propias, dos derivados modificados y las 13 rutas ajenas intactas.

⟦**Sello de la misma sesión (2026-10-08), después del cierre documental:** llegó la instrucción literal «Git Commit +
L3 + Push» y se ejecutó en ese orden. **Commit `b536748`** — 20 rutas, 2.445 inserciones / 137 borrados, con los
ocho checks del hook versionado pasados (incluidos `[6/8]` del índice y `[7/8]` de capitalización). **Revisión
profunda L3** sobre los commits desde su baseline: **0 hallazgos**. **Push:** rango `98c190e..b536748`, paridad
verificada con `git ls-remote origin refs/heads/master` = `b536748…`. Sin tag (opción no solicitada). Las 13 rutas
untracked ajenas siguen intactas y sin stagear. El quick posterior al sello y su crudo van en el commit documental
siguiente, y el sha de ese commit no se estampa aquí.⟧

## 8. Límites de esta fase

El Paso 0 midió el corpus y QMind; **no midió pertinencia** — eso lo decide la certificación de cada fase. Dos
filas del maestro §1 (AC5 por lectura de `main()` y la dependencia dura A1→A3 por lectura de flujo de control) son
afirmaciones leídas **en el código, no ejecutadas**: FASE-A1 y FASE-A3 tienen la obligación de convertirlas en
dientes, y si la corrida las desmiente, el maestro se corrige con la medición delante, no la aserción del test.
Ninguna consulta de esta sesión bajó contenido del notebook: la descarga por CLI no se intentó (antecedente 3/3
fallida el 2026-10-07) y por tanto ninguna verificación por bytes se declara aquí.
