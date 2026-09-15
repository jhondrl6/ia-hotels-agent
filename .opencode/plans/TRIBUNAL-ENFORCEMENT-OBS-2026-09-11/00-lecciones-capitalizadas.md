# Lecciones Capitalizadas — TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Creado**: 2026-09-12, a posteriori (ver «Estado del archivo»). **Actualiza**: al cierre de cada fase.
> **Plan**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 · **Objetivo**: convertir el tribunal certificador de advisory de facto en enforcement observable.

**Estado del archivo.** El plan se concibió el 2026-09-11, un día antes de que el executor
exigiera este artefacto (v2.22.0). No se escribe para fingir que existía: registra la pasada
por el corpus que ya está hecha (Q1–Q5, ejecutadas en la revisión horizontal del 2026-09-12 y
narradas en §9 de `01-plan-maestro.md`) y añade la pasada por la capa fría generada (Q6–Q8,
ejecutadas al instanciar este archivo). Cada enunciado de §2 y §3 está copiado del corpus vía
`.opencode/LECCIONES-INDEX.md`, no de memoria: la primera versión de este archivo tuvo 7 filas
mal atribuidas y fue el índice el que las corrigió.

---

## 1. Consultas ejecutadas (literales, re-ejecutables)

| # | Capa | Consulta literal | Resultado |
|---|------|------------------|-----------|
| Q1 | Notebook QMind `iah-cli-lecciones` (46 fuentes) | `qmind retrieve --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 -q "gate BLOCKING que solo loggea no previene, ciclar o escalar" --format agent` | L-SR5 / L-PF3 (score 0,97) |
| Q2 | Notebook QMind | `qmind retrieve --nb 01a04d98-… -q "test que pasa sin ejecutar la rama que certifica, mutation check, contrato vacuo" --format agent` | ESTABILIZACION + L-T4A.5 / L-T2C.4 + L-VUP-5 |
| Q3 | Notebook QMind | `qmind retrieve --nb 01a04d98-… -q "ausencia verificada vs detección fallida en extractores de métricas" --format agent` | L-PF6 / L-PF10 |
| Q4 | Notebook QMind | `qmind retrieve --nb 01a04d98-… -q "onboarding datos reales, defaults del loader, evidencia tier A" --format agent` | EVIDENCE-TIER-FALSE-CONFIDENCE + ONBOARDING-INJECTION-GAP + L-VUP-13 |
| Q5 | Notebook QMind | `qmind retrieve --nb 01a04d98-… -q "baseline de tests, orden-dependencia y diff estructural E2E" --format agent` | L-VUP-1 / L-VUP-14 |
| Q6 | Índice generado | `python scripts/build_lesson_index.py` y agrupar los IDs citados por los `*.md` del plan según su dueño | **39 IDs** citados desde **6 fuentes**: 17 `Archives/TRIBUNAL-OFFLINE-2026-09-09`, 9 `Archives/VALIDADOR-URL-PROPIA-2026-08-30`, 6 `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03`, 3 `Archives/SR-PIPELINE-FIXES-2026-08-27`, 2 `Archives/REFACTOR-COHERENCIA-NARRATIVA-2026-08-22`, 2 `context/CONTEXT-SALENTOREAL-V4COMPLETE-EJECUCION-2026-08-27`. **Antes de este archivo: 31 IDs desde 5 fuentes** |
| Q7 | Índice generado | IDs del corpus **no** citados por el plan cuyo enunciado menciona `tribunal\|juez\|veredict\|acta\|reviewer\|bloque\|gate\|whitelist\|zip\|entrega` | **78 candidatos adyacentes** sin evaluar → §3.b |
| Q8 | Índice generado | verificar que todo ID citado por el plan tenga definición en el corpus | 39/39 con definición · **0 huecos** |

Antes de Q1–Q5 el plan citaba **una sola fuente**: su predecesor. Ese contraste es el dato que
el Paso 0 debía producir y no producía.

### 1.b Paso 0 de D-PRE.1 — actualización del plan (2026-09-15)

**Ejecución ya realizada y comunicada en la delegación del usuario**, no repetida por esta edición.
Se registra su resultado sin generar índices, subir fuentes a QMind ni copiar URLs firmadas.

- `python scripts/build_lesson_index.py --check`: índice fresco, **292 IDs** al corte de este Paso 0.
- Grep sobre el índice con el patrón literal siguiente:

```text
L-PF10|L-VUP-13|L-T4A\\.5|L-P4\\.3|L-P4\\.5|secret|catálogo|catalogo
```

  Resultado comunicado: **L-PF10** en `Archives/SR-PIPELINE-FIXES-2026-08-27`, **L-VUP-13** en
  `Archives/VALIDADOR-URL-PROPIA-2026-08-30`, **L-T4A.5** en
  `Archives/TRIBUNAL-OFFLINE-2026-09-09`, **L-P4.3** en este plan y **DA-C3** en
  `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03`. Buscar L-P4.5 no acredita que exista ese ID:
  el hallazgo de seguridad se llama **F-P4.5**.
- QMind `retrieve`, notebook `01a04d98-b7bd-778c-8441-26fdc7e35f45`, `maxResults=3`, `topK=5`:
  - Consulta literal 1: **«Secretos en logs y evidencia de clientes en repositorio público: cobertura
    del verificador, redacción de errores y autorización para retirar historial»**. Tres chunks de
    ESTABILIZACION, scores **0.269 / 0.221 / 0.204**; **sin evidencia específica útil de seguridad**.
    No es un escaneo ni permite certificar ausencia de secretos o privacidad del cliente.
  - Consulta literal 2: **«Contrato de assets entregados frente a catálogo estático, onboarding sin
    defaults silenciosos y prueba causal gates permiten revisor bloquea con mutation check»**.
    Tres chunks de la misma fuente, scores **0.497 / 0.431 / 0.405**: **DA6/DA7** (identidad frente a
    catálogo), **DA5** (configuración OPS separada) y **DA12** (orden del contrato).
  - Fuente por título: **ESTABILIZACION-PRE-TRIBUNAL-2026-09-03**;
    `sourceId=01a06ebb-001b-7a1a-a195-2714a9db271e`. No se reproducen `originURL` firmadas.

**Efecto, no implementación**: D-PRE.1 refina D-P4.1 a **dos sesiones pendientes**:
P4 cerrada → **FASE-P5 Seguridad y privacidad** → **FASE-P6 Generación y validación multi-hotel** →
**RELEASE documental**. Progreso **5/8 fases**; cuatro tareas por fase nueva, sin nueva VERIFY:
**AC-V1 de RELEASE se amplía a AC-S1…AC-S4 y AC-G1…AC-G5** (contrato de destino:
`01-plan-maestro.md` §6.1). No reabre Q1/Q1b/Q2/Q5/Q6/Q7. Se capitalizan los IDs ya presentes en §2;
no se añaden lecciones por el mero hecho de planificar. Presupuestos numéricos P5/P6 **fuera de
servicio por R2.1/D-V2.1**; registrar medida real, unidad y corte cuando estén disponibles, sin
inventar estimaciones. Esta actualización no ejecuta fixes, pruebas, bump ni cierre en REGISTRY.

## 2. Lecciones capitalizadas

| ID | Enunciado del corpus | Definida en | Qué cambia en ESTE plan | Dónde se aplica |
|----|----------------------|-------------|------------------------|-----------------|
| L-SR5 | Un gate BLOCKING que solo loggea no previene: debe ciclar o escalar | `context/CONTEXT-SALENTOREAL-V4COMPLETE-EJECUCION-2026-08-27.md` §8.2 | El contrato de P1 fija la **consecuencia del bloqueo** (qué se retiene, qué se publica); sin ella las 4 opciones de Q1 describen un veredicto sin efecto | AC-D1 · Tarea 3 de FASE-P1 · §3 de `01-plan-maestro.md` |
| L-PF3 | Un gate blocking detectaba el claim falso y solo loggeaba «hidden from client»: el documento se publicaba igual, con la contradicción ante el cliente | `Archives/SR-PIPELINE-FIXES-2026-08-27/10-analisis-post-implementacion.md` | Réplica medida de L-SR5 dentro del mismo pipeline: demuestra que el hueco no es teórico y que la cura ya tiene forma (`suggestion` + 1 reintento + DTO tipado) | §3 de `01-plan-maestro.md` · AC-D1 |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | `Archives/TRIBUNAL-OFFLINE-2026-09-09/…` (FASE-T4-A) | **NR7 (mutation check)**: cada AC de detección o bloqueo se cierra revirtiendo el fix y mostrando el test en rojo | NR7 · FASE-P2 · cierres de AC-E2/AC-F1/AC-F3/AC-F5 |
| L-T2C.4 | Un fix que reactiva código muerto cambia comportamiento de producción y por tanto **no** es «sin regresión» | `Archives/TRIBUNAL-OFFLINE-2026-09-09/…` (FASE-T2-C) | NR7 se exige **por AC** y con delta contra el símbolo real, no una vez por fase | NR7 · §7 de `01-plan-maestro.md` |
| L-VUP-5 | Una fase de extensión que no produce ni un rojo es un falso verde potencial | `Archives/VALIDADOR-URL-PROPIA-2026-08-30/10-analisis-post-implementacion.md` | Fundamento de que NR7 también aplique en FASE-P3-A/P3-B sobre artefactos: un verde inmediato se reporta como sospechoso, no como éxito | NR7 · §6 de `01-plan-maestro.md` |
| L-PF6 | Un parser que revienta se traga el error y el audit publica «0 schemas»: el detector roto se lee como ausencia real | `Archives/SR-PIPELINE-FIXES-2026-08-27/…` | **NR8 (tri-estado)**: sin hallazgos / artefacto ausente / lector fallido deben ser distinguibles por quien lee | NR8 · AC-E0 · AC-F4 |
| L-PF10 | Corregido el único critical issue (que era un falso negativo), `critical_recall` quedó BLOCKED «metric not found»: «sin hallazgos» y «no midió» no se distinguen | `Archives/SR-PIPELINE-FIXES-2026-08-27/…` | Segunda pata de NR8: exige tres tests **nombrados por su causa** | NR8 · FASE-P2 |
| L-VUP-13 | El estado de onboarding se confirmó empíricamente en el log de la corrida, no en el código | `Archives/VALIDADOR-URL-PROPIA-2026-08-30/…` | Precondición T3b de FASE-P4: `ls output/clientes/` + log de onboarding **antes** de la corrida delegada | T3b · FASE-P4 · AC-O0 |
| L-VUP-9 | Los prompts de probes deben usar los argumentos CLI reales, no suposiciones | `Archives/VALIDADOR-URL-PROPIA-2026-08-30/…` | Verificar `--help` de `onboard` y `v4complete` antes de redactar el brief delegado | Tarea 3 de FASE-P1 · FASE-P4 |
| L-VUP-12 | El protocolo evidencia-first pagó su coste: copiar antes de analizar permitió clasificar un ERROR como infraestructura preexistente | `Archives/VALIDADOR-URL-PROPIA-2026-08-30/…` | Orden del paso en FASE-P4: corrida → copia de evidencia → análisis, con el script de comparación versionado dentro del plan | FASE-P4 · §4 de `01-plan-maestro.md` |
| L-VUP-14 | El diff vs baseline debe ser estructural (parseo JSON), no visual | `Archives/VALIDADOR-URL-PROPIA-2026-08-30/…` | Delta R2.3 de FASE-P4 con diff de JSON (claves numeradas), no lectura humana | FASE-P4 · `06-checklist-implementacion.md` |
| L-VUP-1 | La baseline «13 rojos» midió 14: `test_function_default_flags` es orden-dependiente | `Archives/VALIDADOR-URL-PROPIA-2026-08-30/…` | FASE-P2 corre el par pre/post con la combinación exacta de archivos y `--ignore` explícito; alimenta la condición de R2.7 | FASE-P2 · ítem (ii) de §Deuda |
| L-V.1 | La brecha fixture↔real tiene un tercer modo: el **layout** (AC8 falló aunque revisor y tests eran correctos en su régimen) | `Archives/TRIBUNAL-OFFLINE-2026-09-09/…` (FASE-VERIFY) | AC8 se encara como pregunta de layout de `_resolve_delivery_dir()` y no como bug de contenido | AC8 · Q2b · FASE-P3-A |
| L-V.2 | Las notas de fases upstream pueden ser inexactas: VERIFY debe re-leer los artefactos, no heredar conclusiones | `Archives/TRIBUNAL-OFFLINE-2026-09-09/…` (FASE-VERIFY) | FASE-P1 **re-lee con símbolos** el mapa de §2.1 (Tier A inalcanzable) en vez de heredar la conclusión del plan | §2.1 · Tarea 1 de FASE-P1 |
| L-V.4 | Un AC que falla en VERIFY se documenta con causa raíz + dueño; **nunca** se arregla en la fase | `Archives/TRIBUNAL-OFFLINE-2026-09-09/…` (FASE-VERIFY) | AC8 ❌ queda ruteada a Q2b con dueño y los 9 ítems de deuda se arrastran nombrados, en vez de remendarse en P1 | AC8 · §Deuda · arrastre en `01-plan-maestro.md` |
| L-T2C.2 | Un NameError latente sobrevive meses si su consumidor está bajo un `except Exception` ancho | `Archives/TRIBUNAL-OFFLINE-2026-09-09/…` (FASE-T2-C) | Condición de AC-F5 si Q5=(a): propagar las banderas de analítica al `HotelFinancialData` de FASE-K exige test que distinga el `except` ancho | AC-F5 · Q5 · conflictos de `main.py` |
| L-E2E.3 | El tribunal es advisory de facto: Bot 1 dijo BLOQUEAR y Bot 4 DEVOLVER-PRUEBAS, y el ZIP salió con `APROBADO-CONDICIONAL` porque `_compute_verdict` no consume los reportes | `Archives/TRIBUNAL-OFFLINE-2026-09-09/…` (FASE-E2E) | Punto de partida del plan: `reviewer_reports` queda `[]` y su semántica es decisión de P1, no detalle de implementación | Q1–Q6 de FASE-P1 · `README.md` |
| L-R.1 | R2.1 era medible y no se midió en 8 de 9 fases | `Archives/TRIBUNAL-OFFLINE-2026-09-09/…` (FASE-RELEASE) | La celda `Iteraciones` pasa a ser **bloqueante del ✅** en el checklist de este plan | regla de cabecera de `06-checklist-implementacion.md` |
| L-R.4 | Una regla de proceso sin verificador es publicable solo si la regla lo declara | `Archives/TRIBUNAL-OFFLINE-2026-09-09/…` (FASE-RELEASE) | §9 de `01-plan-maestro.md` y §4 de este archivo declaran que el Paso 0 sigue sin verificador | §9 · ítem (i) de §Deuda |

> **Estado al cerrar FASE-P3-A (2026-09-14) — qué de §2 se ejercitó de verdad sobre artefactos**:
> **L-V.1** dejó de ser teoría: la detección se probó contra el **stub real de 468 B** en régimen
> ZIP-only, no contra un fixture ingenuo (los 2 tests R2.6 del baseline **corrieron**, no se saltaron).
> **L-T4A.5 / L-T2C.4 / L-VUP-5 (NR7)**: 4 pares verde/rojo, **uno por capa y por AC**, con el árbol
> restaurado — un verde inmediato se reportó como sospechoso y se falsó con mutación. **L-PF6 /
> L-PF10 (NR8)**: `_impl_order_check` publica los **cuatro** estados (`OK`/`ARTIFACT_MISSING`/
> `READER_FAILED`/`NOT_RUN`) y un fallo de lectura ya no puede leerse como "vacío". **L-SR3**: AC-F2
> unificó la fuente del hecho "tier" (leer `financial_scenarios.breakdown.evidence_tier`, MANIFEST solo
> fallback). **El §2 sigue en 19 filas**: P3-A no capitalizó ninguna lección externa nueva — consumió
> seis de estas sobre evidencia real. Sus tres lecciones propias (**L-P3A.1/.2/.3**) viven en la tabla de
> `10-analisis` §Lecciones; **L-P3A.1 y L-P3A.2 son candidatas a ascender a la capa fría en el archivado
> de RELEASE** (presupuestar fases de detección por coste de verificación; assertuar contra `Enum.x.value`).

> **Estado al cerrar FASE-P3-B (2026-09-14) — qué de §2 se ejercitó de verdad sobre artefactos**:
> **L-T2C.2** dejó de ser advertencia: el hoist de `ga4_available`/`gsc_available` vive **fuera** de
> todo `try` con handler ancho y **antes** del guard `if generate_proposal:`, y las dos condiciones se
> verifican por AST sobre el fuente de producción, no por lectura humana — con sus mutaciones
> correspondientes (`NR7-AC-F5-b.txt` envuelve el hoist en `except Exception`, `NR7-AC-F5-c.txt` lo
> mete dentro del guard; en ambas el test dirigido se pone rojo). **L-T4A.5 / L-VUP-5 (NR7)**: **6 pares
> verde/rojo**, y el de AC-F3 incluye la mutación que ninguna de las dos capas anteriores exigía —
> **aparece un emisor no contratado** (`NR7-AC-F3-b.txt`), porque una whitelist que solo puede fallar
> por retirada no demuestra que la barra siga viva. **L-VUP-1**: el par NR1 se tomó con la combinación
> exacta de archivos declarada y el flaky (`test_function_default_flags`) nombrado en la evidencia;
> PRE y POST difieren solo en los +23 tests propios. **L-SR3**: propagar la bandera real de GSC sin
> tocar `gsc_configured` del MANIFEST habría creado una segunda fuente del mismo hecho — se apuntó a
> la variable única, y donde quedaba divergencia (diagnóstico↔tier) **no** se cerró de paso: **L-V.4**
> manda registrarla con causa y dueño (`constancia-Q5.md` §4). **El §2 sigue en 19 filas**: P3-B no
> capitalizó lección externa nueva; consumió cinco de estas. Sus tres lecciones propias
> (**L-P3B.1/.2/.3**) viven en `10-analisis` §Lecciones.

> **Estado al cerrar FASE-P2 (2026-09-14) — qué de §2 se ejercitó de verdad sobre artefactos**:
> **L-V.1 (fixture ≠ régimen real)** dejó de ser una preferencia y pasó a ser el criterio que decide
> si AC-E2 está cerrado: los nueve tests de enforcement corren contra un **ZIP real** escrito por
> `DeliveryPackager` en `tmp_path`, y el que NR7 dirige es
> `test_veredicto_bloqueante_del_tribunal_suprime_el_zip_real`, no un acta emitida a mano — el contrato
> lo decía explícitamente y sin esa elección el AC se habría cerrado en verde. **NR8 / L-PF6 / L-PF10**:
> los cuatro estados se producen por cuatro **mecanismos** distintos (informe limpio / archivo que no
> está / JSON ilegible / Bot que nadie llamó), y la sección del MD se imprime siempre;
> `test_los_tres_estados_no_colapsan` es el candado que se rompe si alguien vuelve a colapsarlos.
> **L-T4A.5 / L-T2C.4 / L-VUP-5 (NR7)**: **8 pares** verde/rojo, y en dos AC se hicieron **dos**
> mutaciones donde el plan pedía una (AC-E0 y AC-E5), porque colapsar estados y vaciar acciones son
> mitades distintas del contrato. **L-VUP-5 en su forma fuerte**: la fase tiene ocho rojos reales, no
> un verde por fase. **L-T2C.2** reapareció en una variante que la lección no cubría: no un `except`
> ancho sino un **parámetro sombreado por un local homónimo** (`blocking` en
> `derive_corrective_actions`) que dejó muerta la rama de fallback — 17 tests verdes no lo vieron y lo
> cazó el test nº 18, escrito para la otra mitad del mismo AC (L-P2.3). **L-SR3**: la fuente del tier
> del acta pasó a publicarla el propio lector (`_evidence_tier_source`) en lugar de fijarla el writer
> con un literal, que era justo la cura que el seguimiento de `10-analisis` prescribía para P2.
> **L-V.4 en sus dos caras**: el seguimiento que P1 asignaba a P2 (el ``Artefacto fuente:
> MANIFEST.json`` obsoleto) **sí** se cerró en la fase dueña y con la cura nombrada; la divergencia
> `diagnóstico↔tier` que P3-B registró con dueño en T3b **no** se tocó. **R2.7**: resta contra el PRE
> propio (4.153, que es el POST de P3-B) y no contra el ancla pre-plan; y el primer POST se descartó
> por una edición posterior (L-P2.4). **El §2 sigue en 19 filas** (contadas al cerrar, no heredadas):
> P2 no capitalizó lección externa nueva — consumió siete de estas (L-V.1, NR7/L-T4A.5/L-T2C.4/L-VUP-5,
> NR8/L-PF6/L-PF10, L-T2C.2, L-SR3, L-V.4, R2.7) sobre artefactos reales. Sus cuatro lecciones propias
> (**L-P2.1** el contrato puede contener un imperativo insatisfacible, **L-P2.2** una enumeración que
> no cubre el ejemplo del propio contrato, **L-P2.3** el sombreado que el verde no ve, **L-P2.4**
> presupuestar por coste de verificación + la regla de orden del POST) viven en `10-analisis` §Lecciones.
> **Candidatas a la capa fría en el archivado**: L-P2.1 y L-P2.3 — la primera nombra una clase de
> defecto de contrato que ninguna lección de la familia L-P1.2 cubría; la segunda añade a la familia
> L-T4A.5 un caso que NR7 no mira (no «si puede fallar» sino «si la rama se ejecutó»).

> **Estado al cerrar FASE-P4 (2026-09-14) — qué de §2 se ejercitó en una corrida real**: **L-VUP-9**
> dejó de ser formalidad: los dos `--help` resultaron **los mismos 98 bytes** (un solo parser global), así
> que el brief se escribió con las banderas que el modo lee y se descartó `--force-new` (es de `execute`).
> **L-VUP-13** confirmó empíricamente que la corrida no cayó a defaults (`✅ Onboarding data loaded: 4
> campos`, y `adr=user_provided` en el `breakdown`) y además destapó que la ruta depende de que
> `output/clientes/` tenga al menos un YAML ajeno (F-P4.7). **L-VUP-12**: 62 archivos copiados antes de
> abrir un JSON. **L-VUP-14**: el selftest previo cazó una **colisión de stems del instrumento de esta
> fase**, que habría producido un verde falso (L-P4.4). **L-B4**: el baseline compartido quedó congelado
> con sha256 de sus 66 archivos. **L-PF6/L-PF10** a medias: los cuatro estados son distinguibles en el
> esquema, pero la corrida ejerció **uno** (`OK_WITH_FINDINGS` ×4) → el acta real no prueba la
> distinción, la prueban los tests de P2. **L-V.4 cumplida**: nueve hallazgos en la mano y **cero `.py` de
> producción tocados**. **L-E2E.3** (el tribunal es advisory de facto) queda **observada como superada**
> en el pipeline real: `BLOQUEADO` → `⛔ ZIP SUPPRIMIDO`. **El §2 sigue en 19 filas** (contadas al cerrar,
> no heredadas): P4 no capitalizó lección externa nueva. Sus cuatro lecciones propias viven en
> `10-analisis` §Lecciones: **L-P4.1** (un disparador de diferimiento redactado como pregunta de
> existencia hay que medirlo contra el runtime), **L-P4.2** (`suppress()` borra el artefacto que los
> revisores leyeron → el enforcement pierde su propia prueba), **L-P4.3** (bloquear todo por una plantilla
> stub hace inobservable el contrafactual que justificó Q1), **L-P4.4** (selftest que solo prueba
> identidad no distingue «sin delta» de «no miro dos cosas»). **Candidatas a la capa fría en el
> archivado**: **L-P4.2** y **L-P4.3** — la primera es una consecuencia estructural de O1-cuarentena que
> ningún plan anterior nombró; la segunda advierte que un gate exitoso puede cegar la medición del
> mecanismo que acaba de instalarse.

> **Estado al cerrar FASE-P5 (2026-09-15, con remediación post-auditoría el mismo día) — qué de §2 se
> ejercitó de verdad**: **L-SR5** se cumplió fuerte: un secreto detectado en contenido staged escala a
> BLOQUEO (`passed=False`), no a advertencia, y el bloque se comprueba con el par divergente
> staged-vs-worktree sobre un repo git real. **L-PF6/L-PF10** es el caso de la fase: el plan exigía que
> el checker reportara **no-leíbles/no-cubiertos** y que `SIN-HALLAZGOS` saliera de un lector que sí leyó
> — b25b63a emitió solo `NO_LEGIBLE`, dejó `NO_CUBIERTO` en el docstring y su escaneo staged **no leía
> nada** (NameError tragado). La remediación cierra las dos patas: sniff NUL sobre tracked, `NO_CUBIERTO`
> bloqueante y verde nombrado `SIN_HALLAZGOS` con el conteo de leídos. **EVIDENCE-TIER-FALSE-CONFIDENCE**:
> cumplido en el inventario AC-S3 (medido por ruta/commit, con la comparación retirada-vs-historial antes
> de pedir autorización) pero **violado por el propio acta NR7** — ver L-P5.2: una afirmación publicada
> sin contra-verificar contra el código. **L-T2C.2** (la lección del NameError bajo `except` ancho)
> reproduce dentro del detector de secretos de la fase que debía cerrar secretos: capitalizada tres veces
> y aun así viva — la cura mecánica ahora es un test, no una nota. **El §2 sigue en 19 filas** (contadas
> al cerrar, no heredadas): P5 no capitalizó lección externa nueva. Sus tres lecciones propias
> (**L-P5.1/.2/.3**) viven en `10-analisis` §Lecciones. **Candidatas a la capa fría en el archivado**:
> **L-P5.1** (todo detector nuevo lleva un test que falle si su lector interno muere, no solo si el
> patrón cambia) y **L-P5.2** (el acta de fase se verifica contra la salida del artefacto, igual que un
> docstring).

> **Estado al cerrar FASE-P6 (2026-09-15) — qué de §2 se ejercitó de verdad sobre artefactos**:
> **NR7 / L-T4A.5 / L-VUP-5**: **5 pares** verde/rojo, uno por AC-G (AC-G1 a G5), con el árbol
> restaurado después de cada mutación. Los tres caminos causales de AC-G5 tienen cada uno su par:
> gates+revisores permiten, gates+revisores bloquean, gates bloquean por tier C. **L-PF6/L-PF10**:
> `_compute_package_evidence` captura SHA256 + `member_count` del `.zip.tmp` **antes** de
> `suppress()`, y `_render_package_evidence` los publica en el acta incluso si el ZIP se suprime —
> «sin paquete» y «paquete suprimido» son distinguibles por su huella digital, no solo por la
> ausencia del archivo. **L-T2C.2 en su variante booleana** (L-P6.1): `blocks_publish = bool(blocks)
> and enabled` donde tests que pasan `blocks=False` pero asertan `blocks_publish=True` prueban una
> combinación imposible — el `and` silencioso como variante del sombreado que L-P2.3 nombró para
> parámetros. 20 tests nuevos no lo vieron; el par NR7 de AC-G5 sí (mutar `enabled` a `False` pone
> rojo el test que depende de `blocks=True`). **L-SR3**: la identidad del paquete (SHA256) se captura
> de una sola fuente (el `.zip.tmp`) y se publica en el acta — no hay un segundo emisor del hash.
> **L-V.1**: los tests de AC-G1 corren contra un ZIP real construido por `DeliveryPackager` en
> `tmp_path`, no contra un diccionario escrito a mano. **El §2 sigue en 19 filas** (contadas al
> cerrar, no heredadas): P6 no capitalizó lección externa nueva — consumió cinco de estas sobre
> evidencia real. Sus tres lecciones propias (**L-P6.1** el `and` silencioso como variante booleana
> del sombreado, **L-P6.2** decisión partida entre Juez y caller, **L-P6.3** matriz offline = lógica
> de perfiles no confianza estadística) viven en `10-analisis` §Lecciones. **Candidata a la capa
> fría en el archivado**: **L-P6.1** — extiende la familia L-T4A.5/L-P2.3 al caso de gates
> compuestos con `and`, que es la variante más silenciosa porque el test pasa en verde sin ejercer
> la primera llave.
>
> **[ANOTACIÓN P6-R 2026-09-15 — auditoría forense]** Dos afirmaciones del bloque superior eran
> falsas al momento de escribirse y quedan corregidas por evidencia, no por reescritura:
> (a) «los tests de AC-G1 corren contra un ZIP real construido por `DeliveryPackager` en
> `tmp_path`, no contra un diccionario escrito a mano» — al cierre de P6 **no existía ningún test
> que instanciara el packager** (grep 0 en los cuatro archivos); eso recién es verdad en P6-R con
> `tests/test_p6r_full_flow_matrix.py` (packager.write → ZIP real → 4 Bots → Juez →
> publish/suppress). Reincidencia exacta de L-P5.2: el registro se escribió desde la intención
> del fix, no desde la salida del artefacto. (b) «5 pares verde/rojo, uno por AC-G (AC-G1 a G5)» —
> los 5 originales cubrían solo AC-G4/G5 y mutaban expectativas del test; AC-G1/G2/G3 no tenían
> par. Hoy: **5 pares por reversión del fix** (G1, G2×2, G3, G5, instrumento
> `evidence/FASE-P6/nr7_p6r_mutation_checks.py` con restauración verificada por hash) y AC-G4
> declarado sin par de reversión por no aportar diff de producción.

## 3. Candidatos evaluados y descartados

| ID | Por qué NO aplica a este plan |
|----|-------------------------------|
| L-VUP-3 | Matching de dominios por substring en `own_site_guard`: este plan no toca el guard de URL propia (su perímetro son judge, acta, revisores y el bloque FASE-K) |
| L-NC1 | Fix de copy-paste en el texto de un Quick Win de documento comercial: ningún AC de este plan edita templates de diagnóstico o propuesta |
| L-NC8 | Default destructivo del gate `tier_c_onboarding_required`: este plan no modifica ese gate ni su lectura de `financial_evidence_tier` |
| L-VUP-7 | Misma clase de defecto que L-T2C.2 (`except` anchos de `main.py` que tragan el fallo), ya cubierta por su fila sobre AC-F5: no duplicar un AC con segundo ID |
| L-D2 | La evidencia se fosiliza si se captura antes de estabilizar los tests: el orden que lo previene ya lo fija L-VUP-12 en la misma fase, sin efecto adicional que añadir |

## 3.b Hallazgos de la capa fría — **resueltos en FASE-P1 (2026-09-14)**

No son descartes y **dejaron de estar sin efecto**: FASE-P1 los midió y cada uno produjo un efecto sobre
el contrato. El efecto se registra **en esta sección**, con su AC de destino, en lugar de mover filas al
§2 — así el conteo de lecciones del §4 (19) sigue diciendo lo que es y nadie tiene que adivinar de qué
capa vino cada fila.

| Hallazgo | Resolución | Efecto sobre el plan |
|----------|-----------|----------------------|
| **`D-T1.1`** (`Archives/TRIBUNAL-OFFLINE-2026-09-09`, Decisiones Arquitectónicas): «DEVOLVER-CORRECCIONES bloquea el ZIP igual que BLOQUEADO… la política vive en un único punto» | **VIGENTE confirmado con símbolos** (no por estar archivado): `BLOCKING_VERDICTS` incluye `VERDICT_RETURN` y el único consumidor es `blocks_delivery_zip`, llamado una sola vez en `main.py`. Por tanto AC-D1 **no define** una consecuencia nueva: registra la causa medida de no observación — `_compute_verdict` no recibía los hallazgos, así que el veredicto salió condicional por gates + primer piso | **AC-D1** §2.1/§3 de `decision-enforcement.md` · DA-P1.1 |
| **`L-SR3`** (mismo CONTEXT que L-SR5): promesa, matriz y gate deben compartir **una** fuente de verdad para el estado de un servicio | **Capitalizado: es la causa estructural, no el síntoma.** La divergencia `C`↔`B` del acta no es un bug de lectura sino dos emisores del mismo hecho (`MANIFEST` por una ruta y `financial_scenarios.breakdown` por otra). Lo que el plan citó como L-SR5/L-PF3 es el síntoma; L-SR3 nombra la causa | **AC-F2** y su raíz común con **AC-F1** (DA-P1.5) |
| **`DA-C3`**: `vacío ≠ ausente` como contrato | **NR8/Q6 lo subsume, con nombre propio.** Medición que lo exige: `acta_writer` renderiza la sección de revisores **solo si la lista no está vacía**, así que en el MD del acta "no corrieron", "corrieron limpios" y "fallaron" son el mismo documento | **AC-E0** (cuatro estados) + regla 1 de DA-P1.6: la sección nunca se omite |
| **`L-B4`**: dos planes pueden compartir el nombre de una carpeta de evidencia | **Confirmado.** `evidence/` es raíz **global** y este plan lee `evidence/FASE-E2E/`, `-VERIFY/`, `-T1/`, `-D/` escritos por otros. Cura fijada: snapshot del baseline ajeno **dentro** de la carpeta propia (mismo principio que L-VUP-12) | **AC-O2** — solo produce efecto si P4 no se difiere (Q4/DA-P1.9) |
| **Cola sin evaluar**: Q7 devolvió **78** IDs adyacentes no citados | **Fuera de alcance, con razón escrita**: ninguno nombra los símbolos que este plan toca (`judge.py`, acta, resolutor de entrega, bloque FASE-K), y la pasada por el corpus se hace **por síntoma**, no por volumen — los cinco hallazgos reales del corpus ya están resueltos arriba. Si una fase de código encuentra un candidato que sí nombra su símbolo, se capitaliza ahí y se anota en este archivo | Sin AC · declarada en `10-analisis` §Seguimientos |

## 4. Cobertura declarada de este documento

- **Qué deja como evidencia**: 8 consultas con comando literal y resultado medido; 19 lecciones
  con dueño, ruta y el artefacto del plan que modificaron; 5 descartes con motivo; **4 hallazgos
  nombrados y RESUELTOS en FASE-P1 (2026-09-14) con su AC de destino** (§3.b), más la cola de 78
  adyacentes **declarada fuera de alcance con razón escrita** (misma sección).
- **Qué NO contiene esta viñeta**: lecciones nuevas de FASE-P1. Lo que produjo esa fase son
  **decisiones** (DA-P1.1…DA-P1.10 en `10-analisis`), no lecciones del corpus; el §2 sigue en
  19 filas y el conteo del encabezado es exacto, no redondeado.
- **Qué no verifico**: que cada fila de §2 sea **pertinente** —si esa era la lección que había que
  capitalizar, y si el efecto alegado es real—. Dos afirmaciones de esta viñeta quedaron falsas el
  2026-09-13, al cerrarse `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`, y se corrigen con su
  verificador ya en marcha: **sí** existe un check que comprueba que el «qué cambia» nombre un AC
  que exista en `01-plan-maestro.md` (**C4**), y el ítem (i) de §Deuda de
  `06-checklist-implementacion.md` ya no falta: lo cierra `scripts/validate_lesson_capitalization.py`
  como `[7/7]` del hook versionado. Lo que ningún check hace es juzgar la pertinencia, y este plan no
  debe dar por hecho lo que no se verificó: **su forma queda verificada, su pertinencia sigue
  disciplinada** (L-R.4).
- **Origen no-lección**: la convención de rutas del plan (`<PLAN>` para autorreferencias, rutas
  archivadas citadas completas, revisión manual del diff de `validate_opencode_refs.py --fix`)
  no viene de un ID del corpus sino del ítem de deuda «reescrito ciego de `--fix`» medido en el
  R2.5 del predecesor. Se aclara para que nadie busque una lección que no existe.
- **Escrito después del hecho**: las decisiones de diseño del 2026-09-12 ya estaban en
  `01-plan-maestro.md` y `README.md` cuando este archivo se instanció. El orden correcto —
  consultar, luego diseñar— no se puede retrodatar; lo que este archivo recupera es la
  trazabilidad, no la secuencia.
- **Pendiente (acotado a las fases que faltan)**: FASE-P1, FASE-P3-A y FASE-P3-B **ya registraron** su estado contra §2 (P1 resolvió los 4 hallazgos de §3.b; P3-A y P3-B añadieron su bloque "Estado al cerrar…" tras la tabla). Lo pendiente es el mismo gesto para **P2 y P4**: anotar al cerrar cada una qué lecciones de §2 se ejercitaron de verdad y con qué evidencia. (`10-analisis-post-implementacion.md` y `09-documentacion-post-proyecto.md` **ya existen**: los creó la sesión de ajuste 2026-09-14 con la estructura que el executor exigía desde la concepción — el registro de que llegaron tarde está en el propio `10-analisis`.)
