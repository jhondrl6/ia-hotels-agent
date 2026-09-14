# Análisis Post-Implementación — TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Estado**: 🔄 en curso (0 fases cerradas)
> **Plan**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 · **Versión objetivo**: 4.77.0 (confirmar en P1)
> **Creado**: 2026-09-14 en la sesión de ajuste — el executor lo exige **desde la concepción** del plan (v1.4.0+ del template); este plan lo debió desde el 2026-09-11 y la deuda queda aquí registrada, no retrodatada. Se actualiza al cierre de **cada** fase.

---

## Resumen de Ejecución (llenar al cierre de cada fase)

| Fase | Sesión | Estado | Iteraciones (ids + tool_use, corte = commit) | delegate_task | Notas |
|------|--------|--------|----------------------------------------------|---------------|-------|
| Ajuste de preparación *(orquestación, fuera de presupuesto de fase)* | 2026-09-14 | ✅ | auto-reporte (D-V2.1: el instrumento no alcanza el transcript bajo el cliente actual; unidad declarada) | No | Etapa 1 completada: prompts P3-A/P3-B/P4/RELEASE + 09/10 creados; P2 diferido a Q1 con declaración; P3 dividida por R3; FASE-VERIFY condicionada; cierre sin P4 fijado; citas `3bdc14e`/origin/tag `v4.76.0` corregidas |
| FASE-P1 | 2026-09-14 | ✅ | **≈30 `ids` / ≈58 `tool_use`** (auto-reporte, **unidad declarada** — D-V2.1: `measure_iterations.py` no alcanza el transcript bajo el cliente actual), corte = commit de cierre | No | Q1=sí · Q1b=escalar · Q2=O1-cuarentena · Q2b=2 capas · Q3=P3→P2 · Q4=el hotel · Q5=a · Q6=4 estados · Q7=knob heredado · VERIFY no activa · prompt P2 creado. **Presupuesto de 30 superado** → causa y cura en L-P1.4 |
| FASE-P3-A | — | ⬜ **(primera de ejecución — DA-P1.3)** | — | No | AC-F1 (dos capas, ZIP-aware) + AC-F2 (fuente del tier) + AC-F4 |
| FASE-P3-B | — | ⬜ | — | No | AC-F5 **disparado** (Q5=a, toca `main.py`) + AC-F3 + AC-F6 · presupuesto 25 |
| FASE-P2 | — | ⬜ **(se ejecuta: Q1=sí; depende de P3-A y P3-B)** | — | No | O1-cuarentena; prompt creado por P1 |
| FASE-P4 | — | ⬜ (opcional: §Cierre válido sin P4) | — | Sí (corrida) | T3a = el hotel, por contacto del operador (DA-P1.9) |
| FASE-VERIFY | 2026-09-14 | ❌ **No activa** (cerrado en P1) | n/a | No | Criterio §4.6-2 no garantizable desde la ingeniería; AC-V1 en RELEASE |
| FASE-RELEASE-4.77.0 | — | ⬜ | — | Sí | Cierre + tag + **AC-V1** (patrón VERIFY embebido) + archivado R2.5 |

**Regla L-R.1 (vigente para este archivo)**: una fila en `⬜` con celda de iteraciones en `—` **no bloquea**; lo que bloquea el ✅ de fase cerrada es `—` **después** de cerrada. Una fase diferida (P2 por Q1=no, P4 por cierre sin P4) se marca `Diferida` con la decisión como causa, nunca `—`.

---

## Decisiones Arquitectónicas / de Proceso

### D-AJUST.1 — División de FASE-P3 en P3-A / P3-B (2026-09-14)
- **Decisión**: P3 empaquetaba 6 fixes (AC8, tier del acta, AC-F4, AC-F5, barreda, versión) y excedía el máximo de R3 (≤4 tareas). Se divide: **P3-A** = AC-F1 (AC8) + AC-F2 (tier acta) + AC-F4 (primer piso `B_PLUS`) sobre `judge.py`/`asset_reviewer.py`; **P3-B** = AC-F3 (barreda, test-only) + versión del acta + AC-F5 solo condicional a Q5=(a), sobre tests/`acta_writer.py`/`main.py`.
- **Rationale**: la división es por naturaleza de cambio (detección/fidelidad del acta vs cableado/test), no por tamaño: P3-A no toca `main.py` ni `acta_writer.py`; P3-B solo toca `main.py` bajo Q5=a. Cada fase nace dentro de R3 y con baseline NR1 propio.
- **Alternativas rechazadas**: (i) agrupar "tier acta + versión acta" en una sola tarea para caber en 4 — rechaza medir R3 con agrupaciones convenientes, que es como la regla muere; (ii) dejar P3 inteira "porque son fixes chicos" — R3 existe precisamente contra el agotamiento por acumulación (la regla lo dice: el orquestador que crea fases grandes es responsable del agotamiento de las sesiones siguientes).

### D-AJUST.2 — FASE-VERIFY condicionada, no decidida en la preparación (2026-09-14)
- **Decisión**: los 3 criterios de §4.6 no son evaluables hoy porque el conteo de fases de implementación depende de Q1 (P2), Q5 (AC-F5 en P3-B) y Q4/T3a (P4). Se registra la evaluación condicional en `dependencias-fases.md` y **FASE-P1 la cierra**.
- **Rationale**: activar o excluir VERIFY con una decisión no tomada sería el gesto que L-V.4 prohíbe (decidir en la fase equivocada); el plan ya tenía el patrón embebido en RELEASE (AC-V1) sin declararlo sustituto.
- **Alternativas rechazadas**: (i) fijar "no activa" (conteo P2+P3=2) — omitía que P4 es fase con ejecución E2E y que el conteo cambia con Q1; (ii) crear ya el prompt VERIFY — prompt condicional a una decisión pendiente es un entregable falso.

### D-AJUST.3 — Escenario de cierre sin P4 (2026-09-14)
- **Decisión**: si T3a no se cierra (con Q5≠c), P4 se difiere con la misma mecánica que Q5=(c) — §Cierre válido sin P4 en `dependencias-fases.md`. El fallo de T3b no difiere: AC-O0 (`B_PLUS` con límite). Si P1 eligió Q1=(c) y T3a falla después, la resolución por defecto es O4 documentada.
- **Rationale**: sin esto, RELEASE quedaba bloqueada por una precondición externa que quizá nunca llega; con esto, el diferimiento es una decisión con rastro, no un `—`.

### FASE-P1 (2026-09-14) — decisiones DA-P1.1 … DA-P1.10

Desarrollo completo con alternativas rechazadas: `evidence/FASE-P1/decision-enforcement.md` §1.

| ID | Decisión | Rationale (una línea) | Alternativa rechazada |
|----|----------|-----------------------|------------------------|
| DA-P1.1 | **Enforcement sí** | G0 (`ROADMAP.md` §9) exige acta `APROBADO-PARA-ENTREGA`, y esa rama está cerrada por un guard que hoy no puede recibir los hallazgos: auditoría-only = **G0 incerrable por diseño** | (b) O4 documentado · (c) decidir tras P4 (inobservable con el cableado actual) |
| DA-P1.2 | **Escalar, no ciclar** | Los defectos que bloquean son estructurales (stub, asset ausente): regenerar produce el mismo stub. El `suggestion` de L-PF3 no tiene forma de restricción aquí | reintento con guard anti-bucle · entrega parcial (contradice el acta) |
| DA-P1.3 | **Orden P3-A → P3-B → P2 → P4** | Cablear dientes sobre detecciones rotas produce bloqueos inevaluables y invita a apagar el tribunal | P2 primero |
| DA-P1.4 | **O1-cuarentena** | El packager ya escribe `.zip.tmp` y renombra de forma atómica con los bytes finalizados: la decisión se mueve del *write* al **publish** sin duplicar serialización ni cambiar el contrato ZIP-only | O1-staging (layout fantasma) · O2 (memoria) · O3 (abandona single-write) · O4 |
| DA-P1.5 | **AC8 en dos capas** | Arreglar solo la lectura deja pasar el stub; arreglar solo el heurístico no sirve porque el archivo nunca se lee. **AC8 y AC-F2 son el mismo bug con dos víctimas** | (a) sola · (b) sola · dejarlo caer con el reordenamiento |
| DA-P1.6 | **Cuatro estados, no tres** | El tri-estado omitía `NOT_RUN`, que es el estado que la corrida real ya exhibe; diseñar los estados alrededor del bug dejaría P2 sin palabra para nombrar su propio fallo | tri-estado del plan · colapsar `NOT_RUN` con `READER_FAILED` |
| DA-P1.7 | **Heredar `GATE_BLOCKING_ENABLED`** + `enforcement.suppressed_by_operator` en el acta | Medido: el tribunal **no** heredaba el knob. Un solo botón para todo lo que suprime entrega, y el escape queda declarado en el artefacto en vez de ser silencio | knob sin escape · knob propio `TRIBUNAL_BLOCKING_ENABLED` (dos switches confundibles) |
| DA-P1.8 | **Q5=(a) como par con AC-F2** | Propagar banderas sin arreglar la fuente del tier es invisible: `_read_evidence_tier` seguiría leyendo `"C"` | (b) `B_PLUS` como decisión de producto (deja `APROBADO-PARA-ENTREGA` como código muerto) · (c) diferir |
| DA-P1.9 | **T3a la da el hotel, por contacto del operador** | Es la única decisión del plan que no es de diseño sino comercial; sus líneas rojas (el agente jamás llena el YAML, nada de datos plausibles para destrabar, consentimiento y frescura) son la garantía de que el tier no vuelve a mentir | que el agente o el plan "estimen" el dato · correr con defaults |
| DA-P1.10 | **FASE-VERIFY no activa** | El criterio §4.6-2 depende de que un hotel responda: atar la certificación a eso deja el cierre en `—` indefinido. La certificación se ancla al par NR7 por fase, que sí depende de este plan | crear el prompt VERIFY con una condición abierta · dejarla "condicionada" otra sesión |

**Tensión registrada, no resuelta en P1** (para que P2 no la descubra tarde): la decisión Q2b asume que los revisores leen el ZIP, y la decisión Q2 los pone a leer el `.zip.tmp`. Son el mismo archivo en regímenes distintos del mismo nombre; el contrato lo cierra fijando que **el resolutor de entrega lee un ZIP sea `.tmp` o publicado**, y P2 debe verificar además **si el acta viaja dentro del ZIP** (Tarea 1 de su prompt).

---

## Lecciones Aprendidas (mínimo 3 por fase con aprendizaje; al cerrar cada fase)

| ID | Pasó / Qué | Por qué | Cura (y si es regla sin verificador, declarada — L-R.4) | Pertinencia |
|----|-----------|---------|----------------------------------------------------------|-------------|
| L-AJUST.1 | Un plan citaba como viva (`bd2bf57`, "local sin push", "sin tag") una verdad que un rebase y un push posteriores invalidaron | Las citas de commit se escribieron en presente en la concepción y ningún check las contra-verifica al re-verificar el plan | Higiene aplicada 2026-09-14: citar el commit **vivo en origin** y distinguir en el texto lo histórico ("existen desde v2.21.0") de lo presente. Sin verificador mecánico → límite declarado (L-R.4) | INCLUIR — aplicable a todo plan largo con predecesor |
| L-P1.1 | La opción barata de Q2 estaba **fuera de la lista**: O1/O2/O3/O4 se concibieron como alternativas mutuamente excluyentes y ninguna aprovechaba que `_create_zip_single_write` ya recibe `manifest_bytes`/`implementation_order_bytes` **finalizados** y que `package()` escribe `.zip.tmp` antes del rename atómico | El menú se escribió desde el diseño concepción ("¿dónde corren los revisores?") y no desde la medición del artefacto ("¿qué costura ya existe?"); la pregunta bien hecha — *¿dónde cae la decisión?* — no estaba en la tabla | Toda pregunta de arquitectura de este plan se formula después de re-leer el artefacto y **nombra la costura existente** si la hay. Sin verificador mecánico: lo disciplina la Tarea 1 del prompt de fase → límite declarado (L-R.4) | **INCLUIR** — la clase de error que produce refactor más caro del necesario |
| L-P1.2 | El docstring de `_compute_verdict` prometía "Finding CRITICAL de revisores → DEVOLVER-CORRECCIONES" y el cuerpo de la función no tenía ni el parámetro: contrato documentado y código divergían | Un docstring escrito en T1 describió la intención del plan, no lo que se implementó, y ningún check compara el texto con la firma | En P2, la matriz del contrato se refleja en la **firma** de `_compute_verdict` y su test; un docstring no es evidencia. La lectura del texto para juzgar el comportamiento es la misma falla que L-V.2 prohíbe sobre las notas | **INCLUIR** — leer el cuerpo, no el comentario |
| L-P1.3 | La pregunta Q2b estaba formulada como "(a) **o** (b)" y la medición mostró que eran **las dos mitades de un mismo fix**; además AC8 y AC-F2 resultaron ser el mismo defecto (un lector escrito contra un layout descomprimido) con dos víctimas | El plan ereditó la disyuntiva de la concepción sin medirla; al medir las dos capas, la disyunción se autodestruyó | Antes de fijar una pregunta de decisión, **verificar que las opciones son excluyentes**. Si la medición muestra que un "o" es un "y", se re-enuncia la pregunta, no se elige una rama | **INCLUIR** — aplicable a cualquier tanda de decisiones |
| L-P1.4 | **Presupuesto superado**: 30 iteraciones declaradas ≈ 30 `ids` / 58 `tool_use` (unidad auto-reportada, D-V2.1) | Causa medida: (i) el Paso 0 de fuentes obligatorias de esta fase son **11 documentos** y hubo que leerlos; (ii) la Tarea 1 exige re-leer 14 símbolos por evidencia propia (L-V.2) y no heredar; (iii) 8 preguntas de decisión con su tanda, dos de ellas corregidas en vivo | Un presupuesto de fase debe declararse **junto con su instrumento de medición**, y D-V2.1 (el instrumento no alcanza el transcript) debería forzar a revisar el presupuesto de las fases de decisión: 30 era un número de fase de código. Propuesta para el sucesor: fase de decisión con ≥6 preguntas → presupuesto en función de `fuentes obligatorias × símbolos a re-leer`, no del tamaño del entregable. Regla sin verificador → declarada (L-R.4) | **INCLUIR** — el nº va en la celda, no en la memoria |
| L-P1.5 | Un `except Exception` que solo imprime un warning envuelve **las tres** cadenas que este plan decide (FASE-K, el bloque del Juez y el de cada revisor): en las tres, el fallo se manifiesta como **ausencia silenciosa**, no como error | No es un defecto de la fase: es el patrón never-block del repo aplicado a código que además **declara valores por defecto** (`"C"`, `[]`, `financial_breakdown = None`) | NR8/Q6 extiende su regla a los gates: ningún camino puede producir "sin hallazgos" desde "no leí". En AC-F5 el test "sin `NameError` con `generate_proposal=False`" es obligatorio por esto mismo | **INCLUIR** — patrón transversal de `main.py` (familia L-T2C.2) |

---

## Métricas de Ejecución (al cerrar cada fase)

- Tests canonónicos: pre-plan 4.063 / 293 archivos (medido 2026-09-11, v4.76.0) — actualizar con delta R2.7 por fase. **P1: 4.063 / 293 sin cambio** (fase de decisión, cero código, cero tests nuevos ni tocados; verificado por `git status` en el commit de cierre).
- `--quick`: 9 checks desde `4ac139a` (eran 8 al cierre del predecesor). **P1: resultado en la evidencia del commit de cierre.**
- Coherence / publicación: sin cambio en P1 (no hay corrida).
- Archivos tocados por P1: `evidence/FASE-P1/` (2 nuevos), `05-prompt-inicio-sesion-fase-P2.md` (nuevo), y los **7** documentos de plan actualizados (`00`, `01`, `06`, `README`, `dependencias`, este `10`, más `09`).

---

## Seguimientos Abiertos

- ~~Empujar el tag `v4.76.0`~~ — **hecho 2026-09-14**: master `8cbcb05..3f026d2` y tag `v4.76.0` (`2df9dbc`→`3bdc14e`) en origin, tras L3 sin hallazgos. La convención sigue para los futuros: los tags no se empujan solos, se preguntan.
- La rama local `backup/pre-sanidad-evidence-20260912` conserva el objeto `bd2bf57`: candidata a podar cuando el usuario confirme que nada la referencia (no borrar desde un agente sin pedirlo).
- **T3a sin cerrar (Q4/DA-P1.9)** — dueño: **el operador**, con la jerarquía Salento Real → Don Alfonso/Luxor → Zi-One. Tres líneas rojas: el agente **jamás** llena el YAML de onboarding; **nada** de datos plausibles "para destrabar"; consentimiento y frescura registrados. Si al iniciar P4 no hay dato con fuente → §Cierre válido sin P4 **sin reabrir decisión**. No es una precondición "en espera": es un diferimiento con disparador y dueño escritos.
- **`test_barreda_un_solo_emisor_de_la_clave` en rojo** → dueño **FASE-P3-B (AC-F3)**. Causa exacta medida en P1: `asset_reviewer.py` es un segundo emisor de `"asset_path":`. §5.1 del contrato fija **qué emite Bot 3** para que la whitelist sea un acto documentado y no una rendición.
- **Cola de 78 adyacentes sin evaluar (Q7 del Paso 0)** → **declarada fuera de alcance en P1**, con razón escrita (§6.1 de `decision-enforcement.md`): ninguno toca los símbolos del plan y la pasada se hace por síntoma, no por volumen. Si una fase de código descubre un candidato que sí nombra uno de sus símbolos, se capitaliza **ahí** y se anota en el `00-`.
- **"Verificador de conteos declarados en §4"** (llegó del plan PASO0 con la premisa ya corregida) → **RETIRADO en P1 con medición**: el §4 de `00-lecciones-capitalizadas.md` declara 19 lecciones y el §2 tiene 19 filas. No se hereda el ítem ni se abre AC.
- **Tensión que hereda P2** (registrada arriba, en DA-P1.4/§final): Q2b asume ZIP publicado y Q2 pone los revisores sobre el `.zip.tmp`. El contrato lo resuelve con un resolutor que lee un ZIP en cualquiera de los dos estados — P2 no puede resolverlo improvisando.
- **`acta_writer.py` con la versión hardcodeada** → pasó de nota de fase a **AC-F6** con artefacto y mutation check.

---

## Lecciones capitalizadas de planes anteriores

Fuente canónica: `00-lecciones-capitalizadas.md` (Paso 0 horizontal del 2026-09-12 + capa fría del índice). Su tabla §2 (19 lecciones con dueño y efecto) **es** esta sección; no se duplica. Lo que aquí se registra es el contraste promesa↔realidad al cerrar cada fase:

| Fase | Lecciones que la gobernavan | Se aplicó de verdad (evidencia) | No aplicó / parcial (causa) |
|------|-----------------------------|----------------------------------|------------------------------|
| FASE-P1 | L-V.2 (re-leer, no heredar), L-V.1 (fixture ≠ régimen), L-SR5/L-PF3 (bloqueo con consecuencia), L-PF6/L-PF10 + DA-C3 (ausencia ≠ hallazgo), L-T2C.2 (`except` anchos), L-VUP-6 (delegar solo lo decidido), R2.2 (símbolos), R2.4 (AC en artefacto), §15.4.1 (contrato antes que implementadores) | **L-V.2**: los 14 símbolos se re-leyeron y **§2.1 quedó confirmado con evidencia propia**, no heredada — y de esa re-lectura salieron tres hechos que el plan no tenía (`research-estado.md` §3). **L-VUP-6**: Q1b/Q5/Q6/Q7 se cerraron **aquí**; el brief de P4 y el prompt de P2 reciben decisiones, no preguntas. **R2.4**: los 17 ACs del §6 llevan artefacto + clave. **§15.4.1**: el contrato se fijó antes de que exista una línea de P2 | **L-PF3 en su letra**: la cura "regenerar con el `suggestion` + 1 reintento" **no** se aplicó porque los defectos bloqueantes son estructurales (DA-P1.2 la rechaza con causa) — se conserva el espíritu (bloqueo con camino de reparación), no el mecanismo. **R2.1**: la medición no la hizo el instrumento sino auto-reporte con unidad declarada (D-V2.1). **NR7**: P1 no produce mutation check (fase sin código); queda escrito AC por AC para P2/P3-A/P3-B |
| ⟨P3-A, P3-B, P2, P4…⟩ | | | |

Capa fría y consultas literales: §1 de `00-lecciones-capitalizadas.md`. Límite declarado (L-R.4): la **forma** del Paso 0 la verifica `scripts/validate_lesson_capitalization.py` desde `e02a688`; su **pertinencia** sigue disciplinada por lectura humana — este plan no debe dar por verificado lo que ningún check mira. **Estado al cerrar P1**: el §2 del `00-` sigue en 19 filas (ninguna lección nueva de P1: lo producido son **decisiones**, que viven en §1 de este archivo) y sus **4 hallazgos de §3.b quedaron resueltos** (ver §6.1 de `decision-enforcement.md`).
