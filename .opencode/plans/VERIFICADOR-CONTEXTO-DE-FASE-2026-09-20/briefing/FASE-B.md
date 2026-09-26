# Briefing pack — FASE-B

> **Artefacto generado. NO editar a mano.** Regenerar con:
> `python scripts/build_phase_briefing.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`
> La frescura la gobierna el sha256 de `sources[]` contra el arbol vigente:
> `python scripts/build_phase_briefing.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 --check`.

- **plan**: `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`
- **fuente de lo declarado**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-B.md` (bloque «Prompt de ejecucion»)
- **estado del pack**: `COMPLETO`
- **declaracion de lectura en el prompt**: `DECLARADA`
- **procedencia**: HEAD `a81da09` · generado `2026-09-26T03:06:52Z`
- **tokens**: estimados por divisor 4, no recuento de tokenizer

## Lectura aparte obligatoria (el pack **no** la sustituye)

- `.agents/workflows/phased_project_executor.md` — 108017 bytes (~27004 tokens). se lee aparte mientras la deuda **D3** no rebane el workflow por fase; copiarlo aqui seria rebanar `.agents/` por la puerta de atras (AC17).

## Que **no** incluye este pack

- 01-plan-maestro.md — 19097 bytes fuera de lo declarado (2, 4)
- 00-lecciones-capitalizadas.md — 38226 bytes fuera de lo declarado (2)

---

# Contenido declarado, copiado de su fuente

## Fuente: `05-prompt-inicio-sesion-fase-B.md` (documento completo)

# FASE-B — Costura de proveedor de decisiones, neutra y extensible

**ID**: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 / FASE-B
**Objetivo**: escribir `scripts/decision_client.py`, la única puerta del repo a un proveedor de
decisiones estructuradas, con contract test de forma y con **la extensión a un segundo proveedor
probada**. Cubre AC6–AC9.
**Dependencias**: FASE-A ✅ (reutiliza sus tres estados y su convención de `coverage_basis`).
**Duración / scope**: 1 sesión; **3 tareas** de código + **0** comandos de larga duración (R3).
**Skill**: `phased_project_executor`.

## Contexto

**Ningún proveedor de pago se activa en este plan.** El acceso existe y está habilitado desde
2026-09-20; el operador decidió posponerlo. Eso no vuelve innecesaria esta fase: la vuelve más barata
y más segura. Lo que se construye aquí es la **costura**, y lo que se certifica es que añadir el
proveedor pospuesto cuesta **un archivo** (AC9). Su activación real es la deuda **D7**, y el primer
consumidor natural es la deuda **D6**, el lint de contradicciones semánticas.

La razón de aislar el proveedor no es estética: el SDK del proveedor rompió compatibilidad dos veces en
sus primeros nueve días público (redefinió los criterios de una primitiva; migró de serializador). Si
el repo se acopla al nombre del proveedor, cada subida rompe fases.

### Estado de fases anteriores

| Fase | Estado |
|---|---|
| FASE-A | ✅ — reutilizar `status` de tres estados y `coverage_basis`; no reinventarlos |

### Base técnica disponible

- La costura resuelve el proveedor por variable de entorno. Los dos candidatos que pueden quedar
  detrás, cuando se active D7, son el SDK oficial del proveedor y el **adapter** que el propio
  proveedor publica como reemplazo respaldado por APIs de LLM — el adapter existe precisamente para
  comparar proveedor contra proveedor en costo, velocidad e inteligencia.
- Forma esperada de una respuesta: elección con probabilidades y confianza; nivel ordenado con
  leyenda; binario con probabilidad de sí. La confianza es lo que permite separar «actué» de «no estoy
  seguro», y es el eje que FASE-C usa en AC12.
- Límites que condicionan el diseño y que hay que dejar escritos en el módulo: solo acepta texto; su
  techo de contexto por solicitud es **menor** que la suma de los documentos de gobierno de este repo
  (de ahí que FASE-C chunkee, y que el lint de conteos de FASE-A sea determinista y no pase por aquí);
  y sus modos de fallo documentados son lectura literal, conteo y comparación de fechas.
- Credencial: solo por variable de entorno. **Nunca** se imprime, se pega en el chat ni se escribe en
  evidencia — una clave que aparece en un transcript obliga a rotarla. La evidencia registra
  `provider_status`, jamás el valor. En esta fase no hay credencial en absoluto.

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-V2.3 | Renumerar sin medir quién afirma el conteo deja contrato huérfano | Tarea 2 / **AC8**: el contract test afirma la **forma**, no los literales del proveedor ni de su versión |
| L-PF6 | Lector roto leído como ausencia | Tarea 1 / **AC7**: proveedor no configurado **no** puede producir una decisión por defecto |
| L-PF10 | Vacío ≠ ausente | Tarea 1 / **AC7**: `RESUELTO` / `NO-CONFIGURADO` / `ILEGIBLE`, tres estados, tres tests |
| L-D3 | Baseline absoluto hace que cumplir cuente como violación | **AC6**: el escaneo de imports se publica con su población, no como «0 coincidencias» a secas |
| L-R.3 | Un `[OK]` sin denominador no informa | **AC6/AC9**: todo conteo lleva la población que lo sostiene |
| L-R.4 | Regla sin verificador es publicable solo si lo declara | **AC9 y D7**: la comparación de proveedores se declara **fuera de alcance**, no se omite |
| L-VUP-5 | Una fase que no produce ni un rojo es un falso verde potencial | Criterios de completitud: el verde sin rojo previo se reporta sospechoso |

## Tareas

### Tarea 1: La costura y sus tres estados

**Objetivo**: `decision_client.py` con contrato propio (`evaluar(state, preguntas) → respuestas
tipadas`), resolución de proveedor por entorno, y fallo explícito cuando no hay proveedor o la
respuesta es ilegible.

**Archivos afectados**: `scripts/decision_client.py` (nuevo),
`tests/quality_gates/decision_client/` (nuevo).

**Criterios de aceptación**: **AC6** (ningún archivo fuera del script importa SDK o adapter alguno;
artefacto `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/import_scanner.txt` con conteo **y** población escaneada) y **AC7** (clave
`provider_status`, tres tests nombrados por su causa; prohibido el `except` que devuelve un valor que
pueda leerse como decisión). Sin proveedor configurado, `evaluar()` **falla**; no devuelve una
heurística.

### Tarea 2: Contract test de forma

**Objetivo**: fijar la forma de la respuesta para que una subida de SDK rompa **este** test y no a una
fase de otro plan.

**Criterios de aceptación**: **AC8** — artefacto `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/contract.txt` con el nombre del test
y su salida; versión de modelo pineada y declarada; se prueba que **alterar la forma del proveedor
falso lo pone rojo**. Prohibido pinear el número de checks ni literales del proveedor (L-V2.3).

### Tarea 3: Extensibilidad probada, no prometida

**Objetivo**: registrar un **segundo proveedor falso** a través de la costura y demostrar cuánto cuesta.
No se conecta ningún servicio real.

**Criterios de aceptación**: **AC9** — artefacto `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/costura.json` con la clave
`files_changed_to_add_provider` (valor esperado `1`; si es mayor, se explica cuál y por qué) y
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/extensibilidad.txt` con la salida del test que añade el segundo proveedor sin tocar
ningún otro módulo. **No hay comparación de proveedores en este plan**: con uno solo no hay elección
que medir, y exigirla produciría un `NO-EJERCITADO` que certifica humo. La comparación es deuda D7.

## Tests obligatorios

| Test | Criterio de éxito |
|------|-------------------|
| `test_decision_client_provider_no_configurado.py` | `NO-CONFIGURADO`, sin decisión por defecto |
| `test_decision_client_respuesta_ilegible.py` | `ILEGIBLE` con el motivo; nunca un favorable |
| `test_decision_client_contract_forma.py` | La forma fijada; alterarla rompe el test (**rojo**) |
| `test_decision_client_aislamiento_imports.py` | AC6 sobre el árbol real, con población |
| `test_decision_client_segundo_proveedor_un_archivo.py` | AC9; `files_changed_to_add_provider == 1` |

```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/decision_client -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-ejecución (OBLIGATORIO)

1. `dependencias-fases.md` — FASE-B ✅ con fecha y notas.
2. `README.md` — progreso y estado real de AC6–AC9.
3. `06-checklist-implementacion.md` — casillas correspondientes.
4. `09-documentacion-post-proyecto.md` — Secciones A, B, D, E.
5. `10-analisis-post-implementacion.md` — fila de la fase, lecciones nuevas con pertinencia, métricas
   reales, seguimientos y decisiones: **qué se pospuso (D7) y qué coste tiene posponerlo**.
6. `00-lecciones-capitalizadas.md` — «Qué cambia» con lo que realmente pasó; §4 al estado del cierre.

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-B \
  --desc "decision_client.py: costura neutra, contract test de forma y extensibilidad a un segundo proveedor probada (AC6-AC9)" \
  --archivos-mod "scripts/decision_client.py,tests/quality_gates/decision_client" \
  --tests "N" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
```

## Criterios de completitud

- [ ] Los cinco tests pasan; ninguno cubre dos estados.
- [ ] `contract.txt` demuestra el rojo al alterar la forma y el verde con la forma actual (AC8).
- [ ] `costura.json` reporta `files_changed_to_add_provider`, con su valor o su explicación (AC9).
- [ ] Cero llamadas de red en toda la fase: verificable, no afirmado.
- [ ] Ninguna evidencia ni log contiene credencial alguna, ni parcial ni enmascarada.
- [ ] `--quick` verde sin haber tocado su composición (AC16).
- [ ] Post-ejecución completa, incluido el índice regenerado en el mismo commit.

## Restricciones

- **No se activa ningún proveedor real ni se hace una sola llamada de red.** Lo certificado aquí es la
  forma y el aislamiento.
- No importar el SDK ni el adapter en ningún otro archivo (es AC6, no estilo).
- No modificar `.agents/**`, `run_all_validations.py`, el hook, `build_lesson_index.py` ni
  `validate_governance_numbers.py` (es de FASE-A: consúmalo, no lo reescriba).
- No enviar a ningún proveedor contenido del plan `REFACTOR-WHATSAPP` ni material del cliente.
- No ejecutar la pipeline. No commitear ni empujar sin instrucción literal.
- Presupuesto con instrumento y corte declarados (R2.1); nunca estimado.

## Prompt de ejecución

```text
Ejecuta unicamente FASE-B del plan
C:/Users/Jhond/Github/iah-cli/.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/.
Lee 05-prompt-inicio-sesion-fase-B.md, 01-plan-maestro.md §2 (las filas del proveedor y D7) y §4
(AC6-AC9, AC16, AC17), 04-contrato-ejecucion.md (permisos y la regla de cero red),
00-lecciones-capitalizadas.md §2, dependencias-fases.md y el workflow canónico.
Heredas de FASE-A los tres estados y la convencion coverage_basis: reutilizalos.
Escribe scripts/decision_client.py como unica puerta del repo a un proveedor de decisiones: contrato
propio, proveedor resuelto por variable de entorno, fallo explicito cuando no hay proveedor o la
respuesta es ilegible, y nunca una decision por defecto.
Cero llamadas de red: por decision del operador no entra Jev en este plan. AC6: ningun otro archivo
importa el SDK ni el adapter, con el conteo y su poblacion. AC8: contract test que se pone ROJO si
altera la forma del proveedor falso, sin pinear literales del proveedor. AC9: registra un segundo
proveedor falso a traves de la costura y publica files_changed_to_add_provider; si es mayor que 1, lo
explicas. La comparacion de proveedores NO es de este plan: es la deuda D7.
La credencial no se imprime, no se pega ni entra en evidencia: se registra provider_status.
No toques .agents/, run_all_validations.py, el hook, validate_governance_numbers.py ni ningun plan
vivo. Registra la fase con log_phase_completion.py y regenera el indice en el mismo commit. Deja
checkpoint si falta autorizacion.
```

---

## Nota de cierre de esta fase (2026-09-23) — no reconstruye las instrucciones de arriba

**Esta fase ya se ejecutó: FASE-B cerró VERIFICADO OFFLINE el 2026-09-21 y se commiteó el 2026-09-22
en `647f436`. Este prompt queda como histórico de esa sesión y no debe volver a ejecutarse.** Tres
rectificaciones que el texto de arriba no contenía cuando se escribió, y que la fase produjo al
commitearse:

- **S11 y S12** nacieron del propio commit de la fase y fueron corregidas **fuera de este plan** por el
  bloque A de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` (`fdd397f`); su **aceptación** por el plan
  propietario está en `dependencias-fases.md` §Conciliación. La guarda que esta fase publicó en el
  README sobre `validate_governance_numbers.py --report` sin destino **ya no aplica**.
- **AC9 se declaró con alcance local**: certifica añadir un proveedor **falso** del repo
  (`files_changed_to_add_provider = 1`, medido por sha256, sin red ni credenciales), **no** el coste de
  integrar un SDK real con sus dependencias y su autenticación. Su texto original («añadir el segundo
  cuesta un archivo») se leía como lo segundo.
- La instrucción de arriba sobre **`log_phase_completion.py` ya está cumplida y no se repite**: la fase
  tiene su entrada en `REGISTRY.md`. Volver a registrarla duplicaría la entrada, y ningún cierre de
  esta fase mueve `VERSION.yaml` (el bump pertenece a RELEASE).

Dónde quedó cerrado y qué quedó abierto (S10, D6, D7): `10-analisis-post-implementacion.md` y
`06-checklist-implementacion.md`.


> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-B.md` · sha256 `0f4e51282983f59cc79bb13d7536bf7bf0a732e38a275464a632757f1ef90006` · 12245 bytes copiados de 12245 del documento · HEAD `a81da09` · generado `2026-09-26T03:06:52Z`

## Fuente: `01-plan-maestro.md` §2

## 2. Matriz de decisión

| Decisión | Resuelto | Base |
|---|---|---|
| **¿Se toca `run_all_validations.py` o el hook para añadir checks?** | **NO.** Ninguna fase de este plan altera el número de checks | `REFACTOR-WHATSAPP` está en vuelo y pinea la cifra. **Sitios medidos el 2026-09-20** (no es el prompt de FASE-C, como decía la primera versión de esta fila): el bloque de arranque de FASE-B de su `README.md` («El quick son 11 checks.»), `06-checklist-implementacion.md` («el modo rápido pasó de 10 a **11 checks** y da 11/11»), `09-documentacion-post-proyecto.md` y `10-analisis-post-implementacion.md`. Promover algo al set de 11 invalida la medición de fases ajenas. **⟦Re-medido el 2026-09-24 por el bloque C de la orden de calidad⟧**: el bloque de arranque de su `README.md` **ya no está en esa lista** —sus enmiendas lo sustituyeron por el comando que imprime la cifra—, y quienes la conservan (`06-`, `09-`, `10-`, su `dependencias-fases.md`, su prompt de FASE-G) son registros de fases cerradas. Eso **no debilita esta fila**: la razón de fondo sigue en pie, porque las mediciones ya publicadas son precisamente esas. Y **`run_all_validations.py` no está libre**: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` lo declara dentro de su alcance (ver D10). Queda como deuda con disparador (§Deuda) |
| **¿Se edita `.agents/` para corregir A1–A4 a mano?** | **NO.** El verificador **reporta**, no reescribe | Quien corrige la frase a mano produce la fosilización siguiente (Q6: la cura es un writer o un verificador, no el edit). Precedente: `validate_plan_citations.py` reporta sin reescribir, decisión DA-HF3 |
| **¿Arquitectura de los nuevos verificadores?** | Script **standalone** en `scripts/`, invocable suelto; el set de 11 queda intacto | Es el patrón de la casa: `[9/11]` y `[10/11]` son wrappers de 4 líneas que delegan a `validate_plan_citations.py` y `validate_lesson_capitalization.py` |
| **¿Se construye un cliente HTTP propio del proveedor?** | **NO.** Costura neutra `decision_client.py` que resuelve al proveedor configurado; el SDK oficial o el adapter quedan detrás | **Origen declarado del dato:** el operador reportó el 2026-09-20 que el SDK del proveedor rompió compatibilidad dos veces en sus primeros nueve días de público (redefinió los criterios de una primitiva; migró de serializador). **No verificable desde este repo** — no hay registro ni changelog del SDK versionado aquí—, así que se cita como dato externo y la decisión no depende de él: nombrar la costura, no el proveedor, es la cura estructural tanto si el historial es de dos rupturas como de ninguna, y así añadir un proveedor nuevo después es **un** archivo |
| **¿El triaje de pertinencia puede filtrar?** | **NO. Solo propone.** La fila ya anclada en §2 nunca desaparece | El riesgo de un filtro que descarta en silencio una premisa carga-estructura ya cobró un plan: `VACUOUS_RECALL` obligó a crear FASE-0 y AC20 en la revisión 2 de `REFACTOR-WHATSAPP` |
| **¿Se activa FASE-VERIFY?** | **NO.** Etapas = 3 (Preparación → Implementación → RELEASE) | §4.6 exige **los tres** criterios. Se cumplen «≥3 fases de implementación» y «ACs que cruzan fases»; **no** existe fase con ejecución E2E (`v4complete`/`v4audit` prohibidos por este plan). Criterio 2 cae → no aplica |
| **¿Entra Jev en este plan?** | **NO, por decisión del operador del 2026-09-20.** El acceso existe y la API está habilitada; posponerlo es distinto de no poder usarlo | FASE-B deja la costura lista y AC9 verifica que **añadir** un segundo proveedor sea un cambio de un archivo. La activación queda como deuda **D7** con su disparador |
| **¿Se compara proveedores dentro de este plan?** | **NO.** Con un único proveedor configurable no hay elección que medir | Reformular AC9 era obligatorio: un AC que exige medir una comparación inexistente se cierra declarando `NO-EJERCITADO` y certifica humo. Es la familia de verde vacuo que AC20 cerró en el otro plan |
| **¿Dónde vive el pack generado por FASE-D?** | En `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/`, **dentro del plan** | `.agents/workflows/` tiene contadores de skills con `glob("*.md")` no recursivo: un `.md` ahí altera lo que reporta `validate_agent_ecosystem.py` y exige seguimiento en su `README.md`. Y AC17 prohíbe escribir en `.agents/` |
| **¿`confidence` es lo mismo que la probabilidad de sí? (⟦decidido el 2026-09-23, orden §4.C⟧)** | **NO.** La pregunta de pertinencia es `choice` de dos opciones, y el umbral de AC12 se aplica a `confidence` **nombrando el campo** en `basis` | Confirmado contra `scripts/decision_client.py`, no contra su docstring: `RespuestaEleccion` exige `confidence` y `RespuestaNoul` la trae en `None` con `confidence_motivo` —la primitiva no la expone—. Un umbral sobre `probabilidad_si` mediría otra cosa y cerraría AC12 con una métrica que el AC no describe |
| **¿El JSON del índice puede leerse confiando en que `[6/7]` lo regeneró? (⟦decidido el 2026-09-23⟧)** | **NO. AC11 toma la ruta (b):** C consume el JSON **tras ejecutar ella misma** la comprobación de frescura | L-V2.2 (`PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`): un verificador no apoya su conclusión en el artefacto de otro gate. La ruta (a) (`build()` en memoria) habría **borrado** el estado `VENCIDO`; elegirla aquí sin decirlo dejaría un AC que pide tres estados sobre un diseño que solo produce dos. Coste aceptado: C es responsable de su suelo y mide dos lecturas por corrida |
| **¿Una lección propuesta por el proveedor falso entra en §2 del `00-`? (⟦decidido el 2026-09-23⟧)** | **NO, no en automático.** Propuesta ≠ pertinente: exige **revisión humana explícita** y su aceptación o rechazo **registrada** con quién decidió | Lo que prueba el falso es la mecánica del camino, no la pertinencia. Auto-triarse con respuestas sintéticas y escribir el resultado en §2 fabricaría la evidencia que AC15 declara `NO-EJERCITADO`, y rechazar en silencio es la familia del filtro que la matriz ya descartó arriba (`VACUOUS_RECALL`). El rechazo también se publica: una fila no desaparece |
| **¿La futura FASE-C aplica las mejoras generales de la orden de calidad? (⟦declarado el 2026-09-23⟧)** | **NO.** C conserva el **workflow canónico** y el **proceso común** vigentes: lee `.agents/workflows/phased_project_executor.md`, cierra con los seis pasos del contrato y no renumera nada (AC16 delta 0) | La orden `2026-09-22` autorizó y ejecutó su bloque A (conciliado, §5-ter) y su **bloque B, concluido contractualmente por su matriz §13, que es la única fuente de su estado**; el **bloque C** —estas enmiendas prospectivas— quedó autorizado el **2026-09-24** solo sobre los documentos de los cuatro planes, y el **piloto FASE-C sigue sin autorización**. Ejecutar una mejora de proceso dentro de la fase sería colar un cambio de gobierno por arrastre de una fase, y dejaría la medición de D3/A7 comparada contra dos reglas distintas. De C **sí** entra lo que este plan ya resolvió para sí: las cuatro enmiendas de AC11/AC12/AC15/propuestas |

> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/01-plan-maestro.md` · sha256 `1872761743009e43998c568717282545ac7a106cc86acfd1285078e995a0b3b7` · 7144 bytes copiados de 51507 del documento · HEAD `a81da09` · generado `2026-09-26T03:06:52Z`

## Fuente: `01-plan-maestro.md` §4

## 4. Criterios de aceptación

**Tabla de ACs** (forma que lee `validate_lesson_capitalization.py` en C4). Cada AC declara
**el artefacto y la clave donde un humano lo leería** (R2.4); el detalle sigue debajo.

| AC | Criterio | Artefacto e instrumento esperado |
|---|---|---|
| AC1 | `validate_governance_numbers.py` reproduce **las aserciones normativas vivas** —las cuatro de §1— y **ninguna otra** sobre árbol vigente, con la regla de población de A8 aplicada; A5, A6 y A7 quedan fuera de su alcance y son la motivación de FASE-C y FASE-D | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/informe.json` → `findings[]` con `assertion_id`, `document`, `claimed`, `observed`, `occurrences[]` |
| AC2 | Publica denominador: población mirada, **regla de población y su exclusión histórica aplicada**, exenciones y familias no cubiertas | ídem → `coverage_basis` |
| AC3 | Expresa `SIN-HALLAZGOS` / `AUSENTE` / `LECTOR-FALLIDO` sin colapsar ninguno | ídem → `status` + tres tests por causa |
| AC4 | Mutation check **por aserción** sobre el símbolo real del guard | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/mutation/` con rojo y verde |
| AC5 | El conteo del quick y del hook se preserva como **delta 0** con par pre/post | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/baseline-pre-post.md` |
| AC6 | Ningún archivo fuera de la costura importa SDK ni adapter alguno | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/import_scanner.txt` (conteo + población) |
| AC7 | Proveedor no configurado o respuesta ilegible fallan explícitos, nunca con decisión por defecto | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/informe.json` → `provider_status` |
| AC8 | Contract test de forma con proveedor falso y versión pineada | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/contract.txt` |
| AC9 | **Añadir un segundo proveedor es un cambio de un archivo**, demostrado con un proveedor falso adicional; ningún proveedor de pago se activa en este plan | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/extensibilidad.txt` + `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/costura.json` → `files_changed_to_add_provider` |
| AC10 | El triaje **no elimina** ninguna fila anclada de §2 | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/ac10_delta.json` → `removed: []` |
| AC11 | Índice ausente o vencido no se lee como «sin candidatos»; **`AUSENTE`, `VENCIDO` y `LECTOR-FALLIDO` son tres causas distinguibles y la frescura la comprueba el propio C** (⟦ruta (b) decidida 2026-09-23⟧) | ídem → `index_status` |
| AC12 | Umbral publicado con valor, base y acción por debajo, **aplicado a `confidence` de un `choice` de dos opciones** — no a `probabilidad_si` — y las propuestas van a **revisión humana**, no a §2 en automático (⟦decidido 2026-09-23⟧) | ídem → `threshold` |
| AC13 | ≥1 test contra corpus real archivado, con skip visible y declarado | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/r26.txt` |
| AC14 | Mutation check sobre el guard real de no-filtrado | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/` |
| AC15 | Denominador del triaje con términos usados, ceros incluidos y familias no juzgadas, **más la aceptabilidad que dispara D6** | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/coverage.json` |
| AC16 | El quick sigue en 11 checks y el hook en 7, en **todo** el plan | los cuatro `baseline-pre-post.md`, delta 0 |
| AC17 | `.agents/` intocado en escritura y límites de cobertura declarados | `coverage.json` → `families_not_covered[]` + `git status` sobre `.agents/` |
| AC18 | Capitalización, citas e índice verdes sobre los artefactos de este plan | salida de los tres verificadores sobre el mismo árbol final verificado (commit opcional posterior autorizado) |
| **AC19** | `build_phase_briefing.py` emite un pack por fase, **sin tocar `.agents/`**, declarando `no_incluye[]` y la lectura aparte obligatoria; **resuelve un plan también en su ruta archivada** (⟦bloque C 2026-09-24⟧: sin eso, el `--check` posterior al `git mv` del RELEASE no es ejecutable) | `…/briefing/FASE-X.md` + `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/informe.json` → `packs[]` |
| AC20 | El **delta de carga total** de lectura se mide con el **mismo comando** antes y después, bytes exactos y tokens con el divisor declarado, contando **workflow obligatorio + coste de generar el pack + pack leído** (⟦bloque C 2026-09-24⟧ concatenar no es ahorrar) | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json` → `before`, `after`, `method` + par pre/post con la resta |
| AC21 | Cada pack declara HEAD, fecha y sha por fuente; **la frescura la gobierna el sha de las fuentes relevantes, y HEAD es procedencia, no clave de caducidad** (⟦bloque C 2026-09-24⟧, para que el commit del propio generado no lo venza) | ídem → `provenance` ; prueba re-editando una fuente y re-midiendo en disco |
| AC22 | Sección declarada y no resuelta es un estado propio: **prohibido emitir un pack más corto en silencio** | ídem → `status ∈ {COMPLETO, SECCION-NO-RESUELTA, FUENTE-AUSENTE}` + tres tests |
| AC23 | Mutation check sobre el guard que impide el truncamiento silencioso | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/mutation/` con rojo y verde |

Un AC cuya clave no existe en el artefacto está incompleto **antes** de ejecutarse (R2.4).

### FASE-A — `validate_governance_numbers.py` (determinista, sin modelo)

- **AC1** — El script, invocado suelto, reproduce sobre el árbol vigente **exactamente** las
  cuatro aserciones de §1 y ninguna otra. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/informe.json`, clave
  `findings[]` con `assertion_id ∈ {A1,A2,A3,A4}`, `document`, `claimed`, `observed` y
  `occurrences[]` (sitios donde esa aserción está escrita).
  **Regla de población (A8 — sin esto AC1 es innavegable):** la familia de aserción es **la
  atribución resoluble**, una afirmación que liga un conteo a un check o documento **nombrado**,
  con el `claimed` que el texto sostiene. El escaneo encuentra **22 instancias `[N/M]` y 2 formas
  «check N»** en los documentos de gobierno; de esas, cada una cae en una de tres clases y la clase
  decide si es hallazgo:
  - **VIVA (normativa):** sostiene una regla vigente del propio documento. Debe cuadrar con la
    etiqueta que imprime el código; si no cuadra → **finding** (esto son A1, A2, A3 y el `[10/10]`
    de A4).
  - **CONGELADA (histórica):** mención de medición fechada, o dentro de una entrada de changelog.
    El **propio objeto auditado** declara esta clase: la entrada `v2.24.0` del workflow dice que
    «las 4 menciones históricas de medición (dos en R2.10, dos en el changelog) se conservan
    literales». No es hallazgo, **pero tampoco silencio**: se publica en `historical_excluded[]`
    con su conteo y la frase que la ampara (L-HF1: un candado que excluye sin decirlo es peor que
    un candado que falla).
  - **VIGENTE Y CORRECTA:**cuadra con la fuente (p. ej. `[7/7]` del hook, los `[6/7]` del índice).
    Entra en `assertions_checked` con su `observed`; no genera hallazgo.
  Un verde de AC1 sin las tres clases publicadas no informa: diría «el árbol está limpio» sobre una
  población que el script recortó a mano.
- **AC2** — El mismo artefacto publica denominador (L-R.3): clave `coverage_basis` con
  `documents_scanned`, `assertions_checked`, `families_not_covered[]`, y `excluded[]` con cuántos
  planes quedaron exentos y por qué. Ninguna salida `SIN-HALLAZGOS` puede emitirse sin esta clave.
  **Familias que NO cubre, declaradas y medidas el 2026-09-20** (la lista no es un «etcétera»):
  (i) prose de conteo sin patrón `[N/M]` ni «check N» («11 checks», «once validaciones» en prosa);
  (ii) aserciones de conteo **fuera de los documentos de gobierno**, que este plan no toca y que hoy
  también están vencidas — `AGENTS.md` («Validación final (10/10 checks en modo rápido; 14 en el
  completo)», que mide 11 y 15), `docs/GUIA_TECNICA.md` y `docs/contributing/REGISTRY.md` con sus
  «check 8»/`[9/9]`/`[10/10]` históricos; (iii) **los pins de conteo en `tests/`** (hay al menos
  `tests/test_validate_plan_closure.py`, que assertiona `[5/7]` dentro del hook); (iv) cualquier
  otra fuente dinámica que no sea una etiqueta impresa (umbrales, tamaños, conteos de tests).
  Las cuatro familias se listan con su medición de AC2 y **D1** decide sobre (i)–(iii); AC5/AC16
  barre (iii) al medir quién afirma el 11 y el 7 (L-V2.3).
- **AC3** — Los tres estados de R2.9 son legibles y **no colapsan**: `sin hallazgos` dice sobre
  qué midió; `ausente` dice la ruta buscada; `lector fallido` dice el motivo y **nunca** sale
  como favorable ni como 0. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/informe.json` clave `status`, más tres
  tests nombrados por su causa, uno por estado.
- **AC4** — Mutation check (R2.8) sobre el símbolo real que guarda la detección, **por aserción**
  y no una vez por fase. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/mutation/` con el rojo (guard desactivado) y
  el verde (guard activo). Sin el lado rojo, AC4 queda ⚠️ (R2.4). Un verde obtenido a la primera
  sin rojo previo se declara sospechoso (L-VUP-5). **Anclaje de la aserción (L-V2.1, medida en
  `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`):** mutar la guarda de A2 y obtener «un hallazgo»
  no prueba nada si otro guard produjo ese hallazgo; cada mutante se afirma sobre **el `assertion_id`
  y el mensaje de esa detección**, y el rojo debe nombrar la aserción mutada.
- **AC5** — El plan no altera ningún conteo: `run_all_validations.py --quick` sigue en 11 checks
  y el hook en 7, formulado como **delta** con par `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/*_baseline_pre.txt` /
  `*_baseline_post.txt` y la resta comprobada (R2.3, R2.7, L-D3, L-V2.3). Artefacto:
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/baseline-pre-post.md`, delta esperado **0**; una resta 0 con tests nuevos
  declarados = baseline contaminado y la fase no cierra en ✅.

### FASE-B — `decision_client.py` (costura de proveedor neutro)

- **AC6** — Ningún archivo fuera de `decision_client.py` importa el SDK del proveedor ni el
  adapter. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/import_scanner.txt` con el conteo de coincidencias y la
  población escaneada (AC2 aplica: 0 sin denominador no es prueba).
- **AC7** — Proveedor no configurado **falla abierto a error explícito**, nunca a un resultado
  por defecto que pudiera leerse como decisión. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/informe.json` clave
  `provider_status ∈ {RESUELTO, NO-CONFIGURADO, ILEGIBLE}`, con un test por estado (R2.9).
- **AC8** — Un contract test con proveedor falso fija la **forma** de la respuesta (elección,
  score, binario, confianza, probabilidades) y la versión de modelo pineada. Subir el SDK sin
  tocar la costura debe romper este test, no a las fases. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/contract.txt`
  con el nombre del test y su salida. Prohibido pinear literales del conteo (L-V2.3).
- **AC9** — Con un solo proveedor en este plan, lo certificable no es «cuál gana» sino que **añadir
  el segundo sea un cambio de un archivo**. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/costura.json` clave
  `files_changed_to_add_provider` (debe ser `1`, o explicarse) y `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/extensibilidad.txt`
  con el test que registra un **proveedor falso adicional** a través de la costura sin tocar ningún
  otro archivo. La comparación real entre proveedores queda como deuda **D7**: un AC que exigiera
  medirla ahora se cerraría declarando `NO-EJERCITADO` y certificaría humo.

### FASE-C — `triage_lesson_relevance.py` (capa de pertinencia, aditiva)

- **AC10** — El triaje es **aditivo por construcción**: ningún ID ya presente en §2 de un plan
  puede desaparecer. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/ac10_delta.json` con `anchored_before`,
  `anchored_after`, `removed` que **debe** ser `[]`; y un test que lo afirma.
- **AC11** — El suelo determinista es `lecciones_index.json`. Si falta, está vencido o no se puede
  leer, el script **no** emite «no hay candidatos»: emite `AUSENTE`, `VENCIDO` o `LECTOR-FALLIDO` con la
  ruta buscada y el comando de regeneración (L-PF6, L-PF10). Artefacto: clave `index_status` + tres
  tests, uno por causa.
  **Fuente de la decisión (Knowledge Center, `L-V2.2` de
  `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`):** «un verificador no debe apoyar su conclusión en
  el artefacto que genera otro gate» — ese plan lo capitalizó porque leer el JSON era lo obvio y el
  JSON lo produce `[6/7]`; la cura que implementó fue **calcular el índice en memoria** con
  `build_lesson_index.build()` (0,30 s medidos) y fallar con nombre propio si el cálculo cae.
  - **⟦ENMENDADA el 2026-09-23 por la orden de calidad §4.C — la elección queda CERRADA, no abierta para C⟧**
  **FASE-C elige la ruta (b): consumir el JSON con su propia comprobación de frescura.** Ya no hay
  elección que la sesión de C tenga que tomar; lo que tiene que implementar es esto, con su costo
  declarado:
  - C **ejecuta ella misma** la comprobación de frescura contra el árbol y a partir de ahí emite su
    estado. **`VENCIDO` es producto del check propio de C**, no de un `--check` ajeno, y por eso el
    estado sigue vivo (a diferencia de la ruta (a), que lo habría borrado).
  - **Prohibida la tercera vía**: leer el JSON confiando en que otro gate (el `[6/7]` del hook o la
    sesión anterior) lo regeneró. Que el archivo exista no es que esté fresco.
  - **Coste aceptado:** C es responsable de su suelo —si el árbol se movió después de la última
    regeneración, C lo dice aunque el hook esté verde— y mide dos lecturas del mismo JSON por corrida
    (la suya y la del check) en lugar de heredar un verde.
  - **Tres causas distinguibles, ninguna colapsable** (R2.9, y aquí con nombres propios porque el
    prompt las pide separadas): **`AUSENTE`** = no hay archivo en la ruta buscada → imprime la ruta y
    el comando de regeneración; **`VENCIDO`** = el archivo existe y se lee, pero **el check de frescura
    propio de C** no lo aprueba → imprime qué diff lo venció y el comando; **`LECTOR-FALLIDO`** = el
    archivo existe pero revienta al parsear o no es legible → imprime el motivo. **Un JSON roto jamás
    produce «sin candidatos» y `VENCIDO` no es `AUSENTE`.**
- **AC12** — El umbral de confianza se publica **con su valor y su efecto**, y los candidatos se
  separan en `propuesto` y `a-revisar-humano`. Ningún camino del código auto-filtra una lección.
  Artefacto: clave `threshold` con `value`, `basis`, `action_below`.
  - **⟦ENMENDADA el 2026-09-23 por la orden de calidad §4.C — forma de la pregunta binaria⟧**
  **La pregunta de pertinencia se formula como `choice` de dos opciones, no como `noul`.** Forma
  confirmada contra `scripts/decision_client.py` (no contra su documentación): `RespuestaEleccion`
  trae `eleccion` + `probabilidades` sobre **todas** las opciones + **`confidence` obligatoria**,
  mientras `RespuestaNoul` trae solo `probabilidad_si` y **`confidence = None` con su
  `confidence_motivo`** — la primitiva no la expone, y la puerta la **prohíbe** ahí.
  **Consecuencia operativa, que es el punto de la enmienda: la probabilidad de sí no es confianza y
  no pueden usarse indistintamente.** El `threshold` de AC12 se aplica a **`confidence`** (cuán seguro
  está el proveedor de haber leído bien la pregunta), y **`basis` debe nombrar el campo**; un umbral
  declarado sobre `probabilidad_si` sería otra cosa — cuánto se inclina por «sí» — y cerraría AC12 con
  una métrica que no es la que el AC describe. Publicar los dos números separados es válido y
  recomendado; **equipararlos, no**.
  - **⟦ENMENDADA el 2026-09-23 — qué se hace con las propuestas⟧**
  **Las propuestas del proveedor falso prueban mecánica y no entran en §2 en automático.** Con `D7`
  sin activar, quien contesta es un proveedor **falso determinista**: lo que su respuesta demuestra es
  que el camino funciona (aditividad, estados, umbral), **no** que la lección propuesta sea pertinente.
  Por eso ninguna fila propuesta puede escribirse en `00-lecciones-capitalizadas.md` §2 por el propio
  script ni por el cierre de la fase: **cada propuesta exige revisión humana explícita, y su
  aceptación o rechazo queda registrada con quién la decidió** (aceptada → entra con dueño y «qué
  cambia» reales; rechazada → se publica el rechazo con su motivo, no se borra). Esto es AC12 en su
  parte de `a-revisar-humano`, es AC10 (aditividad) del lado del documento, y es la familia de
  `VACUOUS_RECALL` que la matriz §2 ya descartó: **un verde con proveedor falso no es evidencia de
  pertinencia.**
- **AC13** — ≥1 test contra **corpus real archivado**, no contra fixture propio (R2.6). El skip
  por baseline ausente es `pytest.mark.skipif` explícito y la evidencia declara **si el test
  corrió o se saltó**. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/r26.txt` con el nombre del test y su marcador.
- **AC14** — Mutation check (R2.8) sobre el guard real de AC10 y AC11, con las dos salidas en
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/`.
- **AC15** — Denominador propio y **términos usados**: el artefacto imprime a cuántos de los 320
  IDs aplicó juicio, sobre qué población, con qué términos de búsqueda, y el conteo que arrojó la
  capa fría con esos términos (incluidos los ceros como en A5). Sin esto, el triaje repite el
  defecto que pretende curar. Publica además **aceptabilidad**: `acceptance` = candidatos propuestos
  que resultaron pertinentes sobre el total propuesto, con su muestra y su método. Ese número es el
  **disparador de la deuda D6** y lo único que decide si el lint de contradicciones se abre en este
  directorio o en uno nuevo. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/coverage.json`.
  - **⟦DECLARADO el 2026-09-23 (orden §4.C): el tramo semántico de AC15 permanece NO-EJERCITADO, con
    motivo⟧** — y no es un descuido ni un ⚠️ prestado: con `D7` sin activar el único emisor de juicio es
    un proveedor **falso**, así que `acceptance` se publica como `NO-EJERCITADO` con el motivo literal y
    **D6 sigue dormida**. No se abre un lint de contradicciones semánticas sobre una base que nunca juzgó
    nada, y **no** se reemplaza el número por una aceptabilidad simulada con el falso para poder cerrar
    el AC: eso convertiría el disparador de una deuda en una cifra fabricada. Lo que C **sí** cierra con
    el falso es la mecánica —aditividad (AC10), estados del índice (AC11), umbral publicado (AC12),
    mutation check (AC14) y denominador con términos y ceros (AC15, su parte no semántica)— y lo que no,
    se declara con su nombre. **Re-evaluar D6 toca cuando exista un proveedor real, no antes.**

### FASE-D — `build_phase_briefing.py` (pack derivado y delta de lectura)

- **AC19** — El generador recorre los prompts de fase del plan, extrae la lista de lectura que cada
  uno **declara**, resuelve cada sección nombrada y emite un pack por fase. `.agents/` no se escribe
  ni se copia como sustituto. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/informe.json` clave `packs[]` con
  `no_incluye[]` y `lectura_aparte_obligatoria[]` — el workflow canónico figura ahí, porque este plan
  no lo rebaná (D3).
- **AC20** — El delta de carga de lectura se mide con el **mismo comando** en los dos lados (`stat
  -c %s` por documento declarado; la estimación de tokens declara su divisor). Artefacto:
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json` con `before`, `after`, `method` por fase y total, más el par
  `*_baseline_pre.txt` / `*_baseline_post.txt` con la resta comprobada (R2.3, R2.7). El delta se
  reporta sobre las fases de **este** plan; la fila de `REFACTOR-WHATSAPP` se publica como
  referencia, no como objetivo. **Un delta cero o negativo es un resultado válido y se explica**: lo
  prohibido es afirmarlo sin medir.
  - **⟦Carga total, añadida el 2026-09-24 por el bloque C de la orden §4.C, fila `CONTEXTO/D`⟧**
  La resta de AC20 se saca entre **cargas totales**, no entre «bytes de las fuentes» y «bytes del
  pack». Cada lado publica los tres sumandos definidos en el contrato (§Carga total y frescura del
  pack): `workflow_obligatorio` (lo que la fase sigue leyendo aparte, con el workflow canónico a la
  cabeza mientras D3 no lo rebane), `coste_de_generacion` (la corrida del generador que la sesión
  ejecuta para obtener el pack) y `pack_consumido`. **Prohibido describir la concatenación como
  ahorro**: unir N documentos no reduce la suma de sus bytes y puede subirla. Lo que AC20 puede
  acreditar es cuánto deja de leerse porque **no** entró al pack, y eso solo se ve si se publica
  también lo omitido (`no_incluye[]`). Si la carga total sube, el resultado es ese y se explica.
- **AC21** — Cada pack declara `provenance` con `head`, `generated_at` y `sha256` por fuente;
  `--check` falla contra un árbol modificado. La prueba se hace **editando una fuente y re-midiendo
  en disco**, no leyendo el objeto en memoria (L-V2.3, R2.4).
  - **⟦Frescura por entradas relevantes, añadida el 2026-09-24 (orden §4.C, fila `CONTEXTO/D`)⟧**
  El predicado de caducidad es **el sha256 de cada fuente listada en `sources[]` contra el árbol
  vigente**, con sus tres causas distinguibles (`FUENTE-AUSENTE` / sha distinto / fuente ilegible).
  `head` identifica de qué árbol salió el pack; **no** es la llave de caducidad. Razón: el pack es un
  generado versionado, de modo que si HEAD gobernara, el commit que lo guarda lo dejaría vencido en
  el mismo commit — invalidación circular. Consecuencias probables y con test: HEAD distinto con
  fuentes idénticas **no** produce `VENCIDO` (se informa como procedencia distinta); el pack no está
  en su propio conjunto de fuentes; y mover una fuente sí lo vence.
  - **⟦Traslado del plan, mismo bloque⟧** AC19 obliga al generador a resolver un plan **también bajo
    `Archives/`**, porque el cierre del RELEASE regenera y verifica el pack **después** del `git mv`.
    El rojo de un `--check` llamado sobre rutas ya movidas no se repara editando código: se repara
    regenerando con la ruta vigente (§Orden del cierre del contrato).
- **AC22** — Tres estados, ninguno colapsado: `COMPLETO`, `SECCION-NO-RESUELTA` (nombra la sección
  pedida y las rutas intentadas) y `FUENTE-AUSENTE` (ruta buscada). **Prohibido emitir un pack más
  corto en silencio**: el recorte no resuelto es un estado, no una reducción. Un `except` que devuelva
  el pack parcial está prohibido (L-PF6, L-PF10).
- **AC23** — Mutation check sobre el símbolo real que niega el truncamiento, con rojo y verde en
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/mutation/`. Sin el lado rojo, AC23 queda ⚠️ (R2.4).

### Transversales

- **AC16** — El conteo de checks del `--quick` y del hook queda inalterado en **todo** el plan
  (delta 0, par pre/post por fase, resta comprobada). Es la AC que abre la puerta a que este plan
  corra mientras otro está en vuelo. **La medición de «quién afirma el 11 y el 7» barre también
  `tests/`**, no solo los documentos: L-V2.3 se capitalizó justamente porque el rojo vivo estaba en
  un contract test. Medido el 2026-09-20: `tests/test_validate_plan_closure.py` assertiona `[5/7]`
  dentro del hook, y `tests/test_validate_lesson_capitalization.py` ya quedó re-atado a coherencia
  estructural (grupo derivado de `run_all`, ordinales exactos `1..D`) en lugar del literal.
- **AC17** — Este plan **no** modifica `.agents/`. Declara además, en su propia salida, las
  familias de aserción que no cubre (L-HF1, L-R.4). Artefacto: `coverage.json` clave
  `families_not_covered[]`, con **las cuatro familias de AC2 nombradas una por una** (prosa sin
  patrón; conteos fuera de los documentos de gobierno —`AGENTS.md`, `docs/GUIA_TECNICA.md`,
  `docs/contributing/REGISTRY.md` con «check 8»/`[9/9]`/`[10/10]`/`10/10…14`—; pins de conteo en
  `tests/`; y toda fuente dinámica que no sea etiqueta impresa) y, para cada una, si queda como
  límite permanente o como trabajo de **D1**. Un `families_not_covered[]` genérico no cierra AC17.
- **AC18** — Los artefactos del plan pasan, sobre el mismo árbol final verificado,
  `validate_lesson_capitalization.py` (C1–C8), `validate_plan_citations.py` y
  `build_lesson_index.py --check`. El commit es opcional, posterior y requiere autorización explícita:
  no condiciona ninguno de los cinco cortes. Ningún AC ni prompt cita `archivo:número` (R2.2).

> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/01-plan-maestro.md` · sha256 `1872761743009e43998c568717282545ac7a106cc86acfd1285078e995a0b3b7` · 25266 bytes copiados de 51507 del documento · HEAD `a81da09` · generado `2026-09-26T03:06:52Z`

## Fuente: `04-contrato-ejecucion.md` (documento completo)

# Contrato de ejecución — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

Cada prompt es ejecutable en una sesión nueva leyendo este contrato, el maestro y las filas
pertinentes de `00-lecciones-capitalizadas.md`. Este archivo **no reemplaza**
`.agents/workflows/phased_project_executor.md`; concreta su aplicación a este plan.

**Estado de B: consultar §13 de la fuente única enlazada abajo.** El bloque B está concluido
contractualmente por su propia matriz. **El bloque C de esa orden quedó autorizado el 2026-09-24
solo como enmiendas prospectivas sobre los documentos de los cuatro planes; el piloto FASE-C de este
plan sigue sin autorizar y no se ejecutó al redactarlas.** Los permisos de este plan no amplían ese
mandato.
Fuente única de resultados y estados D1/S13:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
**§13, única matriz vigente**; §1–§12 son antecedentes rectificados, no aceptación actual.
Evidencia de las enmiendas del bloque C:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/`.

## Permisos de la sesión

| Acción | ¿Autorizada? | Base |
|---|---|---|
| Escribir en `scripts/` (cuatro archivos nuevos) y `tests/` | **Sí** | Alcance §3 del maestro |
| Escribir en `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/` | **Sí, solo FASE-D y solo como generado** | AC19; el directorio vive dentro del plan, no en `.agents/workflows/` |
| Leer `.agents/`, `output/`, `evidence/` de otros planes, `Archives/` | **Sí, lectura** | Necesaria para AC13, AC19 y para el denominador |
| Modificar cualquier archivo bajo `.agents/` | **No** | AC17. Configuración central, y es la fuente que el verificador auditó y que FASE-D lee |
| Reescribir un prompt de fase de otro plan | **No** | FASE-D los parsea. Reescribirlos es lo que D2/D3 postergan |
| Modificar `scripts/run_all_validations.py` o `scripts/git_hooks/pre-commit` | **No** (este plan los lee como fuente de verdad) | AC16: alteraría el conteo que otros planes publican. **Lectura actualizada el 2026-09-24 (bloque C de la orden §4.C):** en `REFACTOR-WHATSAPP` quedan pineados en sus **registros de fases cerradas** (`06-`, `09-`, `10-`, su `dependencias-fases.md` y su prompt de FASE-G, medidos el 2026-09-24 con `grep -rl` sobre las dos formas de la cifra), que son evidencia histórica y no se reescribe; lo que las enmiendas de ese bloque convirtieron en «el valor lo imprime la corrida, con su comando» fueron las **instrucciones prospectivas** (su bloque de arranque y sus prompts pendientes). Eso **no** satisface el disparador de **D2**: D2 pide que deje de haber *fases en vuelo* que pineen el número, y esa decisión sigue con su dueño. **Y no es un archivo libre**: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` lo declara dentro de su alcance, así que este plan no lo escribe pero **sí** debe re-leer su etiqueta `[15/15]` y la invocación del write-back en el cierre (deuda **D10**) |
| Ejecutar `v4complete`, `v4audit`, la pipeline o cualquier API de pago | **No** | §5 del maestro. Este plan no tiene corrida ni llamadas de red |
| **Llamadas reales a un proveedor de decisiones** | **No, en ninguna fase** | Decisión del operador del 2026-09-20: Jev no entra. AC9 certifica la **costura**, no al proveedor; activarlo es deuda **D7** |
| `git commit` / `git push` | **No implícito** | Cada fase deja el checkpoint; el commit requiere instrucción literal |
| **Escribir configuración central en el cierre** — lo que `sync_versions.py` (sin `--check`) reescribe según `scripts/sync_config.yaml`: `README.md` de raíz, `AGENTS.md`, `.cursorrules`, `docs/CONTRIBUTING.md`, `docs/GUIA_TECNICA.md`; `VERSION.yaml` (entrada, no salida); y `docs/contributing/REGISTRY.md` con su tracker `.last_doc_phase.json` cuando se pasa `--archivos-mod` | **No implícito.** Requiere autorización literal **por destino**, comprobada antes de escribir | **Rectificación 2026-09-25:** «cierre offline» y el mandato de RELEASE **no** otorgan este permiso. `--check` y `--help` leen, no escriben. Rige **C0** del `05-prompt-inicio-sesion-fase-RELEASE.md`. Alinear la política de `DOMAIN_PRIMER` es decisión aparte; tampoco la cubre un sync de cabeceras |
| Write-back a QMind | **No en fases de implementación.** En RELEASE **solo con autorización literal propia** | Orden R2.5/R2.10 lo sitúa antes del `git mv`; eso fija su *posición*, no su *permiso*. Es operación remota: ver §Dos momentos del cierre |
| Consulta a QMind (deuda D8 / consulta Q7) | **No por defecto.** Requiere la misma autorización literal | La regla «la consulta no concede permiso de subida» vale al revés: tampoco una subida autorizada concede lectura libre |

**Regla de cero red.** FASE-B y FASE-C se prueban contra proveedores **falsos**. Si una sesión
necesita llamar a un servicio real para avanzar, para y deja checkpoint: la llamada no se autoriza
por conveniencia. Consecuencia aceptada y escrita en el maestro: ningún AC de este plan mide calidad
de decisiones de un modelo real.

**Alcance de la regla (precisión del bloque C, 2026-09-24).** «Cero red» gobierna las **pruebas** de
proveedor de decisiones en las cuatro fases de implementación; no describe el cierre de FASE-RELEASE,
que por su orden R2.5/R2.10 contiene dos operaciones remotas (la consulta Q7 y el `--upload`). Decir
que RELEASE «no hace ninguna llamada de red» y a la vez ordenar esas dos era la contradicción que la
fila `CONTEXTO/RELEASE` de la orden de calidad §4.C pedía resolver. Se resuelve separando momentos, no
borcando ninguna de las dos mitades: ver §Dos momentos del cierre.

## Dos momentos del cierre (añadido por el bloque C de la orden de calidad §4.C)

| Momento | Qué contiene | Red | Autorización | Qué se publica si falta |
|---|---|---|---|---|
| **Cierre offline** | Lecturas y verificadores sin escritura; sync, documentos, registro y derivados únicamente sobre destinos autorizados | **No** | Mandato de RELEASE más autorización literal de los archivos escribibles, comprobada en C0 del prompt RELEASE | Detenerse antes de escribir si falta un destino necesario: `PENDIENTE-AUTORIZACION`, no cierre cumplido |
| **Aceptación remota** | re-corrida de la consulta Q7 (D8) y `--upload` del `10-analisis` antes del `git mv` (D9) | **Sí** | **Literal y propia para cada una**, con presupuesto escrito | Estado `PENDIENTE-AUTORIZACION` con su causa, **no** un PASS ni un `[OK]` por omisión |

**Rectificación 2026-09-25:** «cierre propio de la fase» no otorgaba permiso sobre configuración central.
Rige **C0 del `05-prompt-inicio-sesion-fase-RELEASE.md`**: releer los destinos reales antes de escribir.
`sync_versions.py --check` no escribe; el sync en escritura requiere autorización literal para sus
consumidores de `scripts/sync_config.yaml`. `VERSION.yaml` es entrada, con permiso propio para cambiarla.
La alineación de política de DOMAIN_PRIMER no se autoriza mediante el sync de cabeceras. Tampoco se
actualizan baselines para absorber errores. Sin permiso suficiente, checkpoint previo, no cierre completo.

El archivado (`git mv`) es un **tercer** momento y conserva su autorización separada: no la concede el
cierre offline ni la sustituye una subida pendiente. Con la aceptación remota pendiente, el plan
**puede** archivar solo si el operador lo autoriza expresamente sabiendo que la fuente no se publicó;
si no, deja checkpoint. Nunca se promueve un resultado parcial a éxito del cierre (§Orden del cierre).

## Enmiendas prospectivas ya resueltas para FASE-C (registradas el 2026-09-23)

Fuente: `.opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` §4.C, fila `CONTEXTO/C`, con
autorización local del operador sobre **este** plan y solo sobre **estas** cinco decisiones. **Ninguna
se implementó todavía**: son contrato para la sesión de C, no trabajo hecho. No acompañan cambio de
versión, de `REGISTRY.md` ni de configuración central.

| # | Regla que C debe cumplir | Qué deroga o precisa |
|---|---|---|
| **E1** | La pregunta de pertinencia es **`choice` de dos opciones**, con `confidence` leída como campo **independiente** del umbral. **Prohibido equiparar `probabilidad_si` con confianza.** | Precisa AC12 y su `basis`; la forma está en `scripts/decision_client.py` (`RespuestaEleccion` / `RespuestaNoul.confidence = None`) |
| **E2** | C consume `.opencode/lecciones_index.json` **después de ejecutar ella misma** la comprobación de frescura. Prohibido apoyarse en que `[6/7]` del hook u otra sesión lo regeneró. `AUSENTE` / `VENCIDO` / `LECTOR-FALLIDO` son tres causas con su test cada una | **Cierra la elección abierta de AC11** en la ruta (b); con la ruta (a) `VENCIDO` habría dejado de existir y el AC pediría tres estados a un diseño de dos |
| **E3** | Una propuesta del proveedor falso **no** entra en §2 de `00-lecciones-capitalizadas.md` por sí sola: pasa a `a-revisar-humano` y solo entra con **revisión humana explícita**, dejando la **aceptación o el rechazo registrado** con quién lo decidió. Un rechazo se publica, no se borra | Corrige el paso 6 de post-ejecución del prompt de C, que mandaba «aplicar lo que proponga» sin filtro humano |
| **E4** | El tramo **semántico** de AC15 se publica `NO-EJERCITADO` con su motivo y **D6 queda dormida**. No se simula una aceptabilidad con el falso para cerrar el AC | Refuerza lo ya escrito en el prompt de C; queda elevado a contrato para que no dependa de leer un párrafo |
| **E5** | C **conserva el workflow canónico y el proceso común vigentes**: lee `.agents/workflows/phased_project_executor.md`, cierra con los seis pasos de este contrato, y no renumera checks (AC16 delta 0 sobre los valores que imprime la corrida, no pineados) | Lo que C conserva es el proceso común **tal como lo deja el bloque B**, cuyo estado vigente es la matriz §13 de la fuente única indicada al inicio; los dictámenes anteriores se conservan retirados. Ejecutar dentro de C una mejora de proceso sería colar un cambio de gobierno por arrastre de una fase |

**Reconfirmación de E1 y E2 contra el cliente real (2026-09-24, bloque C de la orden de calidad).**
No es una renegociación: es el contraste que la fila pedía, hecho sobre el código que ejecuta C y no
sobre su documentación ni sobre la transcripción de este contrato. `scripts/decision_client.py` sigue
dando la forma que E1 asume — `RespuestaEleccion` declara `__slots__` con `confidence` y su validación
**exige** el número (`confidence ausente o fuera de [0,1] - sin ella no se puede…`), mientras
`RespuestaNoul` fija `confidence = None` en la propiedad de clase y **la puerta rechaza** que un `noul`
la reporte (`noul no debe reportar confidence`), con `a _en_rango` gobernando `probabilidad_si` por
separado. **Conclusión: E1 y E2 quedan coherentes con el cliente vigente y no se mueven.** La lectura
completa con sus anclas simbólicas está en la evidencia del bloque C.

**Invariante que ninguna enmienda mueve:** el triaje es **aditivo** (AC10, `removed: []` con su test),
todo conteo lleva su **denominador** (AC15/AC2), todo verificador de detección se cierra con su
**mutation check** sobre el símbolo real del guard (AC14), al menos un test corre sobre **corpus real**
archivado con su skip declarado (AC13), y **la red sigue prohibida** en las cuatro fases (§Regla de
cero red). Lo enmendado es la **forma de la pregunta, la fuente de la frescura y el destino de las
propuestas**; no el nivel de garantía.

**Antecedente de las enmiendas, no estado actual de D1/S13.** Los dos párrafos siguientes conservan
las declaraciones de la conciliación y de los dictámenes retirados de B; **no certifican** D1/S13:
su estado solo lo determina la matriz vigente §13 de la fuente única. La obligación de no pisar
históricos en AC14 se mantiene, sin trasladar a C la validación pendiente del arnés de B.

**Lo que NO se tocó al enmendar** (antecedente de aquella sesión): las deudas **S10** (dónde vivirá el
`import` del SDK) y **D7** (activar el proveedor) siguen pendientes y **no son bloqueantes artificiales
de una C offline** — C se cierra con proveedor falso por diseño; **D6** sigue dormida; y el **rojo
contractual** de A1–A4 (`validate_governance_numbers.py`, `exit 1`) sigue vivo porque es **D1** y pide
instrucción literal sobre `.agents/`. **⟦Rectificado el 2026-09-23 por el bloque B de la orden de
calidad, con instrucción literal del operador:⟧ D1 se ejecutó desde su fuente y el árbol real de
`.agents/` ya sale `SIN-HALLAZGOS` (`exit 0`); las cuatro aserciones quedaron como contraejemplo
congelado en `tests/quality_gates/governance_numbers/fixtures/` con sus mutantes. Este contrato de C ya
no puede dar por vivo ese rojo. La conciliación de FASE-B con la remediación del bloque A está en
`dependencias-fases.md` §Conciliación y §Ejecución del bloque B.**

**S13 — dictamen anterior retirado; estado vigente solo en §13.** ⟦El dictamen del
2026-09-23 decía **«S13 resuelta por el bloque B y completada en su remediación el mismo día»**: el arnés
`test_governance_numbers_mutation_por_asercion.py` ya no escribe en
`evidence/…/FASE-A/mutation/`; su evidencia va a destino temporal explícito y **se observan las
operaciones de escritura** del escritor real (`tests/support_observador_escrituras.py`, alcance
declarado: proceso de pytest, no procesos hijos), con ancla positiva y con los tres controles
negativos del mandato sobre un expediente desechable (a escritor redirigido a destino protegido,
b bytes idénticos, c mtime restaurado). La comparación de contenido **y** metadatos del expediente
protegido se conserva además. El
párrafo siguiente sigue vigente como **regla para el mutation check propio de C (AC14)**, salvo su
última frase, que la remediación dejó corta: se reemplaza «por hash de objeto» por «por operaciones
de escritura observadas, más contenido y metadatos» — un `utime` restaurado deja el estado final
idéntico y solo el observador lo ve.⟧ **Antecedente del defecto original:** el arnés de mutación de FASE-A
(`test_governance_numbers_mutation_por_asercion.py`, por su constante `EVIDENCE` junto a `SCRIPT`) tenía el
**destino de escritura hardcodeado dentro de `evidence/…/FASE-A/mutation/`**: al re-evidenciar R2.8 el
2026-09-23 re-escribió 7 archivos cerrados de otra fase — sin daño, porque los 7 `git hash-object --path`
casaron con HEAD, pero con los `mtime` movidos, que es lo que hace invisible este patrón. Es la misma familia
que **S12 / L-VCF-12**, y aquella cura alcanzó a los dos verificadores, no al arnés. **Cuando C escriba su
mutation check de AC14 no puede heredar ese patrón**: su evidencia va a
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/`, el destino se declara con la ruta del
propio cierre (no como constante apuntando al directorio de otra fase), y la prueba de que no pisó pasado
exige **operaciones de escritura observadas, más contenido y metadatos**, con el alcance del observador
declarado. La redacción anterior «por hash de objeto, no por `git status`» queda como antecedente
insuficiente: una reescritura de bytes idénticos puede no cambiar ninguno de los dos.

## Dónde se escribe la evidencia (corregido en la auditoría del 2026-09-20)

Toda la evidencia de este plan va a **`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-X/`**.
La primera versión del plan escribía en `evidence/FASE-A/` … `evidence/FASE-D/` a secas, y eso **no
estaba libre**: esas cuatro rutas raíz existen desde `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` y guardan
su evidencia con exactamente los nombres que produciría este plan (`faseA_baseline_pre.txt`,
`faseA_baseline_post.txt`, `faseB_baseline.txt`, …). Escribir ahí mezclará procedencia de dos planes y
podrá **sobrescribir evidencia de un plan archivado sin que salte ninguna validación** (`validate_opencode_refs.py`
solo mira rutas bajo `.opencode/`, y `evidence/` no entra). El convenio vigente es el subdirectorio por
plan, que ya usa `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`.

**Excepción de lectura, no de escritura**: `evidence/FASE-D/measure_iterations.py` conserva su ruta
legada porque es el instrumento canónico que publica el executor; no es destino de nueva evidencia.

**Discrepancia de la plantilla, rectificada dentro del proceso B:** al concebir el plan,
`.agents/workflows/templates/prompt-fase-template.md` prescribía `evidence/fase-{N}/` sin namespace;
AC17 impedía corregirla desde estas fases y se registró bajo D1. La escritura documental acotada de B
corrige ahora sus destinos y su ejemplo a **`evidence/{NOMBRE-PLAN}/FASE-{N}/`**, alineados con los de
este contrato. Es corrección del proceso B **sujeta a validación en la matriz vigente §13** de la
fuente única, no certificación de D1/S13 ni trabajo trasladado a C/D2.

## Corte de presupuesto (R2.1)

Instrumento canónico: `evidence/FASE-D/measure_iterations.py` (ruta legado, ver arriba), corte **hasta
el commit de código** cuando el commit está autorizado; cuando no lo está, el corte utilizable es
**«hasta listo para revisión»** y se declara cuál de los dos se usó — el commit es una acción posterior
y separada del cierre documental, no un corte ni condición de ninguno (executor, *Cinco cortes*).
Este plan declara presupuesto y **declara además si el instrumento corrió**. Si no corre bajo la
política de permisos de la sesión, el auto-reporte se publica en la unidad usada (`tool_use`,
`ids únicos`) y se declara que **no es comparable** con las demás. Prohibido reportar cumplimiento
estimado o mezclar unidades. Sin instrumento, la métrica se retira y se declara fuera de servicio,
no se estima. **Precondición medida el 2026-09-20**: `find . -name "*.jsonl"` devuelve **0** dentro del
workspace — es la misma condición que documentó `D-V2.1` (`PASO0-…`/`TRIBUNAL-ENFORCEMENT-OBS`,
reproducida en cuatro fases seguidas), así que esta sesión **espera** caer en el auto-reporte con unidad
declarada y lo declara, en lugar de prometer una medición que no puede hacer.

## Cierres incrementales obligatorios por fase

1. **Par pre/post del conteo de checks** en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-X/`
   (`*_baseline_pre.txt`,
   `*_baseline_post.txt`) y `baseline-pre-post.md` con la **resta** comprobada. Delta esperado: **0**
   en las cuatro fases de implementación (AC5, AC16). FASE-D añade además su propio par de **carga de
   lectura** (AC20), que sí espera un delta distinto de cero y que se reporta aunque sea cero.
2. **Selección de tests de la fase** ejecutada, publicada con su resultado, y los rojos preexistentes
   ajenos a la fase declarados como tales con dueño y causa, sin arrastrarlos ni maquillarlos.
3. `run_all_validations.py --quick` en verde, **sin** que la fase haya tocado su composición.
4. **Registro de la fase por sí misma**: `scripts/log_phase_completion.py` al terminar. FASE-RELEASE
   **no** registra fases ajenas.
5. `build_lesson_index.py` regenerado y comprobado **sobre el mismo árbol final verificado** tras las
   ediciones de `.md` bajo `plans/` que nombren un ID (R2.10). Aplica también a FASE-D. El commit es
   opcional, posterior y autorizado por separado; no condiciona los cinco cortes. Si se autoriza,
   incluye fuentes y par generado coherentes, como exige `[6/7]` del hook.
6. Actualización de `00-lecciones-capitalizadas.md` §2 (lo que **realmente** pasó), §4 (cobertura al
   estado real), `06-checklist-implementacion.md`, `dependencias-fases.md` y `README.md` del plan.
7. **FASE-D únicamente**: `build_phase_briefing.py --check` en verde contra el árbol final, y ningún
   pack emitido con `SECCION-NO-RESUELTA` sin decirlo (AC22).
8. **FASE-D únicamente — hereda el resultado NO medido de C y lo acepta.** D no reabre C ni lo
   renegocia: registra que el tramo semántico de AC15 salió `NO-EJERCITADO`, que **D6 sigue dormida**,
   y que su disparador solo se evalúa cuando exista proveedor real (D7). Lo que D **sí** hereda medido
   de C es su parte mecánica: los tres estados del índice, el umbral sobre `confidence`, la aditividad
   y el denominador con sus ceros. El pack puede exhibir los candidatos de pertinencia, pero no puede
   presentar esa exhibición como aceptabilidad obtenida (§E4).

## Reglas sobre el pack generado (FASE-D)

- El pack es **derivado, no autoritativo**. Ninguna lectura canónica desaparece: lo que el pack no
  incluye se declara en `no_incluye[]` y en `lectura_aparte_obligatoria[]`, donde figura el workflow
  canónico porque este plan **no** lo rebaná (D3).
- Un pack no puede achicarse en silencio: sección pedida y no resuelta es un estado propio con la
  ruta intentada (AC22, L-PF6, L-PF10).
- Lleva `provenance` con HEAD, fecha y sha por fuente, y `--check` lo vence contra el árbol (AC21).
  Un pack vencido se regenera; no se edita a mano.

## Carga total y frescura del pack (añadido por el bloque C de la orden de calidad §4.C)

Las tres reglas anteriores dejan abiertos dos puntos que la fila `CONTEXTO/D` cerró: **qué se cuenta
como carga** y **qué mueve la frescura**.

**Carga total (AC20), no «bytes del pack».** El pack unifica lecturas; no las elimina. La medición de
`carga.json` publica por fase los tres sumandos y la resta se saca entre los dos totales, no entre el
pack y la lista de documentos:

| Sumando | Qué entra | Por qué no puede faltar |
|---|---|---|
| `workflow_obligatorio` | Los bytes de lo que la fase **sigue** leyendo aparte (`lectura_aparte_obligatoria[]`): el workflow canónico mientras D3 no lo rebane, y toda fuente declarada y no incluida | Si no se cuenta, el pack aparece como ahorro cuando la fase lee lo mismo más el pack |
| `coste_de_generacion` | La corrida del generador que la sesión ejecuta para obtener el pack (invocación publicada y, si el instrumento corre, su coste) | Un artefacto que hay que producir no es gratis para quien lo consume |
| `pack_consumido` | Los bytes del pack que la fase efectivamente lee | Es el único sumando que el pack reemplaza |

**Prohibido presentar la concatenación como ahorro.** Juntar N documentos en un archivo no baja la
suma de sus bytes; puede subirla (encabezados, procedencia al pie, `no_incluye[]`). El ahorro real
solo puede venir de lo que **no** se copia al pack, y eso se mide declarando qué se omitió. Un delta
cero o negativo sigue siendo resultado válido y se publica igual (AC20). La fila D3 del maestro conserva
su dueño: el recorte de la fuente **no** es lo que mide esta resta.

**Frescura por entradas relevantes; HEAD es procedencia.** AC21 fija el criterio: `--check` vence el
pack comparando **el sha256 de cada fuente listada en `sources[]` contra el árbol vigente**, y fallando
por una de tres causas distinguibles (`FUENTE-AUSENTE` / fuente con sha distinto / fuente ilegible).
`provenance.head` se publica para identificar **de qué árbol salió** el pack, no para invalidarlo: si
el sha de HEAD gobernara la caducidad, el propio commit que guarda el pack generado lo dejaría vencido
en el instante de publicarse — circularidad que la orden §4.C nombró expresamente. Consecuencias
operativas:
- el pack **no** está en su propio conjunto `sources[]`, ni tampoco el commit que lo transporta;
- un HEAD distinto con las fuentes idénticas **no** vencifica el pack: se informa el desfase como
  procedencia distinta, no como `VENCIDO`;
- la invalidación la produce un cambio en una fuente gobernada, nunca el acto de versionar el generado.

**Regeneración y verificación tras el traslado.** El `git mv` del RELEASE cambia las rutas que el pack
declara como fuentes, así que **`--check` después del traslado sin regenerar tiene que fallar**: ese
rojo es un paso del cierre, no una reparación. El orden queda fijado en §Orden del cierre: regenerar
el pack con la ruta ya trasladada y **después** verificarlo. Regenerar un artefacto derivado con su
propio generador es operación de cierre autorizada a RELEASE; **modificar `build_phase_briefing.py`
para que el check pase no lo es** (§Restricciones del prompt de RELEASE: RELEASE no modifica código).

## Reglas de forma aplicadas a los artefactos de este plan

- **Símbolos, nunca `archivo:número`** en ACs, prompts y evidencia (R2.2). Antes de citar una región,
  confirmarla con `grep`/lectura; si difiere, corregir la cita y avisar.
- **Conteos como delta** con par de archivos, no números absolutos (R2.3, R2.7).
- **Todo AC de detección se cierra con mutation check** sobre el símbolo real del guard, con las dos
  salidas en evidencia (R2.8). Verde a la primera = sospechoso y explicado.
- **Todo lector expresa tres estados** y los publica (R2.9): `sin hallazgos` / `ausente` /
  `lector fallido`. Prohibido el `except` que devuelve el valor por defecto de «no encontrado».
- **AC no legible en el artefacto = ⚠️, nunca ✅** (R2.4). Prueba práctica: si el AC no responde
  *«¿dónde lo vería un humano que solo tiene el artefacto?»*, no está listo.
- El **reporte no reescribe**: ningún script de este plan edita `.agents/` ni los planes ajenos.
- Toda cifra copiada de una fuente dinámica se publica **con su comando y su fecha**, y se re-mide al
  cerrar la fase (medición A6 del maestro: las cifras de este plan vencieron al crearse el plan).

## Orden del cierre (R2.5 / R2.10, no permutable)

**Paso 0 (D10, añadido en la auditoría del 2026-09-20):** antes de correr el bloque, verificar la
interfaz del writer contra el árbol vigente — `./venv/Scripts/python.exe scripts/validate_qmind_writeback.py --help`
— porque `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` puede haber añadido `--title`/`--file` o quitado la
degradación a PASS. Si cambió, se re-escribe este bloque **con su nota datada** antes de ejecutarlo.
Este paso es **de lectura**: corre aunque la aceptación remota siga sin autorizar.

**Cada línea lleva su momento (§Dos momentos del cierre).** Las marcadas `⟦remoto⟧` no se ejecutan con
el permiso del cierre documental: necesitan su autorización literal y su presupuesto, y si faltan se
declaran `PENDIENTE-AUTORIZACION` sin promover el cierre a éxito. La marcadas `⟦traslado⟧` requieren la
autorización propia del archivado.

```bash
# ⟦remoto⟧ — aceptación remota, autorización y presupuesto propios
./venv/Scripts/python.exe scripts/validate_qmind_writeback.py --upload VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20
./venv/Scripts/python.exe scripts/build_lesson_index.py
# ⟦traslado⟧ — el archivado es un tercer momento, con autorización expresa
git mv .opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 .opencode/plans/Archives/
# Cola final tras todas las escrituras autorizadas: no modificar baselines para absorber errores.
./venv/Scripts/python.exe scripts/validate_opencode_refs.py
./venv/Scripts/python.exe scripts/validate_plan_citations.py
# Resolver cualquier corrección de corpus autorizada antes de regenerar los derivados.
./venv/Scripts/python.exe scripts/build_phase_briefing.py --plan <ruta-vigente-del-plan>
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/build_phase_briefing.py --plan <ruta-vigente-del-plan> --check
./venv/Scripts/python.exe scripts/build_lesson_index.py --check
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

El `--check` del pack **no** se corrige editando `build_phase_briefing.py` ni su `provenance`: se
corrige regenerando. Si tras regenerar el pack sigue rojo, eso es un defecto del generador y su dueño
es FASE-D, no RELEASE — RELEASE lo declara y deja el checkpoint, porque tiene prohibido modificar código
fuente (§Restricciones de su prompt).

*(Forma unificada el 2026-09-20: los prompts de fase ya usaban el intérprete del `venv`; este bloque
canónico decía `python`, que bajo Git Bash resuelve al intérprete sin dependencias del proyecto. El
orden y sus argumentos no cambiaron en aquella intervención.)*

**Rectificación 2026-09-25:** retiradas las escrituras automáticas `--fix` y `--update-baseline` de la
secuencia; requieren alcance propio y nunca absorben errores. La cola del prompt y del contrato queda
alineada: últimas escrituras autorizadas → packs → índice → checks, sin sustituir C0 ni los permisos
remotos y de traslado. Si no hubo archivado autorizado, verificar en la ruta actual y declararlo pendiente.

## FASE-VERIFY: no aplica, con la razón medida

§4.6 exige **los tres** criterios de activación. Se cumplen «≥3 fases de implementación» (ahora
cuatro: A, B, C, D) y «ACs que cruzan múltiples fases» (AC15, AC16 y AC17 cruzan fases). **No** se
cumple «existe al menos una fase con ejecución E2E (`v4complete`, `v4audit`, etc.)»: este plan tiene
prohibida la pipeline y prohibida la red. Criterio 2 cae → **3 etapas**, sin sesión de certificación.

Consecuencia declarada: ningún AC de este plan puede llegar a `SUPERADO EN E2E`. Su techo es
`VERIFICADO OFFLINE` con su mutation check, o `NO-EJERCITADO` cuando algo no se ejercitó — y
`NO-EJERCITADO` **no** es una salida disponible para AC9, porque AC9 ya no pide medir una
comparación.


> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/04-contrato-ejecucion.md` · sha256 `c4d18dc91998a0086c93fef0182f8f82a48367b7afcd8aa799bed43577fe06e5` · 29211 bytes copiados de 29211 del documento · HEAD `a81da09` · generado `2026-09-26T03:06:52Z`

## Fuente: `00-lecciones-capitalizadas.md` §2

## 2. Lecciones capitalizadas

| ID | Enunciado (una línea) | Definida en (ruta) | Qué cambia en ESTE plan | Dónde se aplica |
|----|----------------------|--------------------|-------------------------|-----------------|
| L-R.1 | Una regla que vive solo en el workflow y no en el artefacto que la fase rellena, se cumple por coincidencia | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | El plan existe porque las aserciones numéricas del workflow y de su template **no las sostiene ningún check**: se cumplen por coincidencia y hoy están vencidas | AC1 · FASE-A Tarea 1  · **aplicada el 2026-09-21 en FASE-A:** el verificador ahora contrasta contra la etiqueta impresa por el `def _check_*` que la ejecuta; las cuatro aserciones siguen vencidas sin que ningún gate las sostenga, y el guard existe (reporta, no reescribe) |
| L-R.3 | Un `[OK]` sin denominador no informa: el verificador publica la población que miró | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | Ninguna salida del lint o del triaje puede decir «sin hallazgos» sin imprimir cuántas aserciones/IDs miró y quiénes quedaron exentos | AC2 · AC15  · **aplicada el 2026-09-21 en FASE-A:** `coverage_basis` es obligatoria y el favorable está bloqueado sin ella (prueba `test_la_salida_favorable_no_existe_sin_denominador`); con denominador impreso: 24 miradas / 11 correctas / 8 congeladas / 0 no resueltas · **aplicada el 2026-09-21 en FASE-B (AC6/AC9):** el `0` de imports se publica con **dos** poblaciones (678 rastreados por `git grep` / 692 del árbol que ve el AST), los 4.379 nodos de import vistos, las 21 menciones-no-import aparte y los excluidos por directorio con su conteo; y el `1` de `files_changed_to_add_provider` sale de sha256 sobre la frontera copiada, no de una afirmación (L-VCF-8) · **aplicada el 2026-09-24 en FASE-D:** `coverage_basis` del informe imprime 5 packs por estado, 34 fuentes, 23 secciones pedidas / 23 resueltas y las cinco familias no cubiertas; y el corpus real se publica con su denominador de convencion (**0 de 121** prompts archivados declaran lectura) en lugar de un `[OK]` a secas |
| L-R.4 | Una regla de proceso sin verificador es publicable solo si la regla lo declara | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | Las tres reglas que este plan no cierra (promoción al quick, rebanado del workflow, arreglo de `.agents/`) se publican con dueño y disparador, no se callan | AC17 · `dependencias-fases.md` §Deuda  · **aplicada el 2026-09-21 en FASE-B:** la comparación de proveedores se declaró **fuera de alcance** en `extensibilidad.txt` con su porqué (D7) y la decisión de geometría que este plan **no** tomó salió con dueño y disparador nuevos: **S10** (L-VCF-9) |
| L-NC10 | Fosilización narrativa como clase de bug: templates con texto estático que ignoran la fuente dinámica de verdad | `Archives/REFACTOR-COHERENCIA-NARRATIVA-2026-08-22` | Mismo defecto, otro artefacto: el template fija «`[10/10]` de `--quick»` cuando el código emite `[10/11]`. La cura es comparar contra la fuente, no reescribir la frase | AC1 · AC4  · **aplicada el 2026-09-21 en FASE-A:** la lista de aserciones se **descubrió** escaneando los dos documentos (24 instancias: 22 con corchete + 2 formas «check N»), no hardcodeada; A1 apareció en dos sitios que el patrón nunca había visto juntos · **aplicada el 2026-09-24 en FASE-D:** el generador no recibe ninguna lista de lecturas por configuracion: parsea la que el propio prompt declara. El test confronta `parsear_lista_lectura(prompt)` contra las fuentes del pack emitido, y `no_incluye[]` publica los bytes que quedaron fuera de lo declarado |
| L-PF6 | Un lector roto leído como ausencia real produjo un pain falso HIGH con cifra económica | `Archives/SR-PIPELINE-FIXES-2026-08-27` | El triaje lee `lecciones_index.json` y el lint lee `.agents/`: ambos publican los tres estados, y un parser que revienta jamás devuelve «sin candidatos» | AC3 · AC11  · **aplicada el 2026-09-21 en FASE-A:** cuatro caminos de `LECTOR-FALLIDO` con motivo propio (fuente sin etiquetas, hook sin pasos, documento sin patrones, sujeto ambiguo por alias); ninguno devuelve «sin hallazgos» · **aplicada el 2026-09-21 en FASE-B (AC7):** la prohibición del default es el eje del módulo — `evaluar()` sin proveedor **falla** con 5 `motivo_clase` que no colapsan, y el mutante `M-AC7-proveedor-por-defecto` muestra que ceder un default sí fabricaría una decisión. Coste propio descubierto al medir: la regla «nadie más importa el SDK» aplicada sin graduar producía **16 hallazgos ajenos** (L-VCF-7) · **aplicada el 2026-09-24 en FASE-D:** el lector de la lista declarada falla ruidoso y por causas separadas — `--plan` inexistente = exit 2 con sus tres rutas intentadas; fuente ausente = el pack **no se emite** (exit 1) con la ruta buscada; meta sin sha = `FUENTE-ILEGIBLE`, que no colapsa con `FUENTE-AUSENTE` ni con `SHA-DISTINTO` |
| L-PF10 | Vacío ≠ ausente: la lista quedó vacía **porque el fix funcionó**, y el extractor devolvía `None` igual que cuando el dato no existe | `Archives/SR-PIPELINE-FIXES-2026-08-27` | El estado `SIN-HALLAZGOS` del lint es un resultado positivo y debe decir sobre qué midió; `AUSENTE` debe imprimir la ruta buscada y el comando de regeneración | AC3 · AC11 · AC15  · **aplicada el 2026-09-21 en FASE-A:** `SIN-HALLAZGOS` imprime sobre qué midió y `AUSENTE` la ruta buscada; un documento no vacío con 0 instancias es fallo de lectura, no «limpio» · **aplicada el 2026-09-21 en FASE-B:** `respuestas: []` es `ILEGIBLE` con causa `respuesta-vacia:list` (no «cero decisiones favorables»), `usage=None` **no** es consumo cero, y `noul.confidence` es `None` **con su motivo escrito**, no un 0.0 que FASE-C leería como certeza · **aplicada el 2026-09-24 en FASE-D:** al trío de AC22 hubo que sumarle un cuarto estado, `SIN-DECLARACION` (pack emitido con cero fuentes gobernadas), y el `--check` lo imprime como `SIN-FUENTES` en lugar de `OK` — con test que prohíbe la palabra OK en esa salida. Motivo medido: 121 prompts archivados no declaran lectura, y llamarlos «completos» era el verde vacio de L-HF1 |
| L-D3 | Un baseline numérico hace que cumplir el plan cuente como violación | `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` | El invariante «el quick sigue en 11 checks» se formula como **delta** con par `*_baseline_pre/post.txt`, no como número absoluto | AC5 · AC16 · AC20  · **aplicada el 2026-09-21 en FASE-A:** los conteos se publicaron como delta con par pre/post y la resta (quick 0, hook 0, población A8 0); la métrica que sí se movió (tests, +23) se declaró aparte en lugar de maquillarla · **aplicada el 2026-09-21 en FASE-B:** quick 11→11, completo 4→4, hook 7→7, `.agents/` 98.694/6.123 idénticos y población AC6 678 sin mover y 690→**692** en el árbol (+2 por los instrumentos de la propia fase: nota 3 en `FASE-B/baseline-pre-post.md`) — con **+48 funciones / 53 casos** de tests publicados por separado. Y una elección de unidad: no se publicó un `tool_use` aproximado, porque no era medible (R2.1) · **aplicada el 2026-09-24 en FASE-D:** la carga de lectura se goberno como delta con par `faseD_carga_pre/post.txt` (`stat -c %s`) y resta **entre cargas totales**; cinco identidades comprobadas por `instrumentos/comprobar_resta_carga.py` (exit 0) y quick 11→11 / hook 7→7. Y un test planta una fuente diminuta para exigir que un delta **negativo** se publique con la misma identidad, no que se esconda |
| L-V2.3 | Renumerar el hook sin medir quién afirma el número de checks deja contrato huérfano | `Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` | Este plan **no renumera** nada: su AC5 y AC16 exigen medir la población que afirma los conteos antes de tocarla, y no pinear literales | AC5 · AC16 · AC8  · **aplicada el 2026-09-21 en FASE-A:** el barrido de `tests/` mostró que **esta fase añadió 4 pins del denominador 11** al fijar el contrato AC1 (L-VCF-5), declarados con dueño D1/D2 en vez de limar la aserción · **aplicada el 2026-09-21 en FASE-B (AC8):** el contract test afirma la **forma** y compara el modelo contra lo que el proveedor falso **declara**, nunca contra una cadena; el pin `jev-1.13.0` vive en `PIN_MODELO_DECLARADO` con `usado_por_el_codigo: false` y un test lo comprueba por AST (aparece una sola vez: su definición). FASE-B **no añadió** pins del 11 ni del 7 (4→4, medido) · **aplicada el 2026-09-24 en FASE-D:** AC21 se prueba **escribiendo la fuente en disco** y re-midiendo contra ese disco (y al revertir, verde); y AC23 se anclo con una cadena exclusiva del generador, porque «rutas intentadas» y «seccion pedida» ya vivian dentro de los documentos que el pack copia — un mutante anclado ahi daba rojo sin serlo |
| L-V2.1 | Un test que solo mira **qué check** disparó puede quedar verde por una rama distinta de la que pretendía observar | `Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` | Cada mutante de AC4 y AC14 se afirma sobre el `assertion_id`/la detección que dice atacar, no sobre «el script devolvió un hallazgo»: el rojo tiene que nombrar la aserción mutada | AC4 · AC14 |
| L-V2.2 | Un verificador no debe apoyar su conclusión en el artefacto generado por **otro** gate | `Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` | FASE-C lee `lecciones_index.json`, que produce `[6/7]`; la cura ya implementada por ese plan es **calcular el índice en memoria** con `build_lesson_index.build()` (0,30 s medidos). ⟦**Ruta CERRADA el 2026-09-23, contrato E2**: FASE-C consume el JSON **tras ejecutar él mismo** la comprobación de frescura, de modo que `VENCIDO` sea estado producido por su propio check y no por un `--check` ajeno; la ruta (a) queda descartada porque **borraría** el estado que AC11 exige, y sigue prohibida la tercera vía (leer el JSON confiando en que otro paso lo regeneró). Coste publicado: C es responsable de su suelo y hace dos lecturas del JSON por corrida⟧ | AC11 · AC15 |
| D-V2.1 | El instrumento canónico de R2.1 no alcanza el transcript de sesión bajo el cliente actual; la medición se publica como auto-reporte con **unidad declarada** | `Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` (definida allí; **reproducida en cuatro fases seguidas** por `Archives/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`) | El `04-contrato-ejecucion.md` de este plan ya aplica el patrón (instrumento, corte, y si no corre: unidad declarada, «no comparable», o métrica retirada — nunca estimada). Verificado el 2026-09-20: `find . -name "*.jsonl"` devuelve **0** dentro del workspace, la misma precondición del incidente | **AC5** · **AC16** (par pre/post por fase) · `04-contrato-ejecucion.md` §Corte de presupuesto |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | Todo AC de detección del plan se cierra con mutation check sobre el símbolo real del guard, con las dos salidas en evidencia | AC4 · AC14  · **aplicada el 2026-09-21 en FASE-A:** seis mutantes sobre los símbolos reales del guard, con verde y rojo en disco — y el primer intento de anclaje (id posicional) **no** observaba la rama que decía certificar: ver L-VCF-1 · **aplicada el 2026-09-24 en FASE-D:** mutation check con las dos salidas en disco — apagado `GUARD_NO_TRUNCAMIENTO_ACTIVO` el pack conserva el estado `SECCION-NO-RESUELTA` pero **pierde la declaracion del recorte** y se achica en silencio (los dos tamaños y su diferencia viven en `FASE-D/mutation/resumen.txt`; **no se transcriben aquí**: este `.md` entra en el pack que lo mide → **L-VCF-19**). Un test aparte exige que el mutante NO cambie el estado: si lo cambiara, el rojo vendria de otra rama (L-V2.1) |
| L-VUP-5 | Una fase de extensión que no produce ni un rojo es un falso verde potencial | `Archives/VALIDADOR-URL-PROPIA-2026-08-30` | El verde de la primera corrida del lint se reporta **sospechoso** y se explica, nunca como éxito | AC4 · AC14  · **aplicada el 2026-09-21 en FASE-A:** el verde de la primera corrida **fue sospechoso y lo era**: la regla de población se rectificó dos veces y el mutation check nombraba a la aserción equivocada · **aplicada el 2026-09-21 en FASE-B:** la primera corrida de la selección dio **30 fallos** (f-string mal cerrado, `score` cayendo en `opciones` por argumento posicional, 8 aserciones mal apuntadas) y el primer mutante de forma apagaba la lista **entera**, que no aislaba a ningún guard (L-VCF-6). Rojos propios además de los buscados: AC8 guarda su `exit 1` en `contract.txt` |
| L-HF1 | Un candado con la cobertura equivocada pasa en verde mientras el artefacto miente | `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` | El lint declara las familias de aserción que **no** cubre, una por una y medidas: prosa de conteo sin patrón, conteos fuera de los documentos de gobierno (`AGENTS.md`, `docs/GUIA_TECNICA.md`, `docs/contributing/REGISTRY.md`), pins de conteo en `tests/` y toda fuente dinámica que no sea etiqueta impresa. Ese límite es AC, no nota al pie | AC2 · AC17  · **aplicada el 2026-09-21 en FASE-A:** `families_not_covered[]` salió de la AC y del script: las cuatro familias medidas en el informe (3 / 245 / 4 archivos / 4.330 funciones en disk), y `git status --porcelain .agents/` quedó vacío · **aplicada el 2026-09-21 en FASE-B:** el escáner publica sus cuatro límites medidos (carga no literal → 16 sitios contados y no callados; dependencias declaradas → no miradas, es D7; menciones en prosa → aparte; exclusiones → con su conteo) y `git status --porcelain .agents/` volvió a quedar vacío con 98.694/6.123 bytes idénticos · **aplicada el 2026-09-24 en FASE-D:** `no_incluye[]` no vacio es exigido por test fase por fase, y del medir salio una regla nueva: lo que vive **fuera** de `.opencode/` se declara lectura aparte y no se copia, porque copiarlo dentro del plan ampliaba la poblacion que escanea `validate_opencode_refs.py` y un artefacto derivado le devolvio rojo al quick ([8/11]) por referencias ajenas |

Dueños distintos representados: **6** — TRIBUNAL-OFFLINE, REFACTOR-COHERENCIA-NARRATIVA, SR-PIPELINE-FIXES, ESTABILIZACION-PRE-TRIBUNAL, PASO0-VERIFICADOR-CAPITALIZACION y VALIDADOR-URL-PROPIA. Satisface C8 (≥2) con holgura y no repite solo al predecesor. **Doble corrección del 2026-09-20**: la fila decía **7** cuando las once originales ya tenían **6** dueños nombrables (L-R.3 aplicado a este propio archivo: el conteo se re-mide, no se copia), y las tres lecciones nuevas de la capa tibia **no suman dueño** — `D-V2.1` está definida en `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`, no en `TRIBUNAL-ENFORCEMENT-OBS`, que es donde la **reproducen** cuatro fases seguidas. Lo detectó `validate_lesson_capitalization.py` con su checks `C7` (atribución contra el índice), no una lectura humana: es el verificador de forma de este mismo plan funcionando sobre su propio `00-`.

> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/00-lecciones-capitalizadas.md` · sha256 `f6c1a005848008424dfe9128d48500a0fdff0fa5ba3a967c73b8b5c6eb0b8ec0` · 14966 bytes copiados de 53192 del documento · HEAD `a81da09` · generado `2026-09-26T03:06:52Z`

## Fuente: `dependencias-fases.md` (documento completo)

# Dependencias y bloqueantes — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

**Estado de B: consultar §13 de la fuente única enlazada abajo.** El bloque B está **concluido
contractualmente** por su propia matriz. El **bloque C** de esa orden quedó autorizado el 2026-09-24
solo como enmiendas prospectivas sobre los documentos de los cuatro planes; **el piloto FASE-C de este
plan no lo estaba** y ninguna de sus fases se ejecutó ni se diseñó al conciliar.
**⟦Rectificado el 2026-09-24 al cerrar FASE-C⟧**: esa frase sigue siendo cierta sobre el **bloque C**
(enmiendas documentales) y ya no lo es sobre el **piloto**: el operador autorizó esa tarde, con mandato
propio y corte **«hasta listo para revisión»**, ejecutar FASE-C, que quedó **cerrada sin commit ni push**
(ver su fila en §Cadena y su evidencia en `evidence/…/FASE-C/`). Fuente única de
resultados y estados D1/S13:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
**§13, única matriz vigente**; §1–§12 son antecedentes rectificados, no aceptación actual.
D3 permanece parcial, con dueño **«Plan propio, posterior»**. Los cierres de FASE-A/B y la
conciliación del bloque A se conservan como históricos, distintos de la remediación del bloque B.
Evidencia de las enmiendas del bloque C:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/`.

## Cadena

```
FASE-A ──► FASE-B ──► FASE-C ──► FASE-D ──► FASE-RELEASE-4.xx.0
 (lint      (costura   (triaje    (pack       (docs, sync, REGISTRY,
  determ.)   proveedor) pertin.)   briefing +  write-back, archivar)
                                    delta de
                                    lectura)   └─ VERIFY no aplica (§4.6 cae en criterio 2)

A y B son técnicamente independientes; C consume a ambas y D consume a las tres.
Se mantienen secuenciales por la Regla de Sesión Única del executor.
```

**No ejecutar fases en paralelo ni encadenarlas dentro de una sesión.** Un checkpoint no
habilita la fase siguiente.

| Orden / prompt | Objetivo | Complejidad | Estado |
|---|---|---|---|
| 1 · [FASE-A](05-prompt-inicio-sesion-fase-A.md) | `validate_governance_numbers.py`: aserción contra fuente dinámica, con denominador y tres estados | MEDIA técnica / ALTA consecuencia: es el guard de las ediciones futuras sobre `.agents/` | **✅ CERRADA 2026-09-21 — VERIFICADO OFFLINE (AC1–AC5)** |
| 2 · [FASE-B](05-prompt-inicio-sesion-fase-B.md) | `decision_client.py`: costura neutra, contract test con proveedor falso y **un solo** proveedor configurable; AC9 certifica que añadir el segundo cuesta un archivo | MEDIA-ALTA: la superficie que cambia de proveedor sin que nadie más se entere | **✅ CERRADA 2026-09-21 — VERIFICADO OFFLINE (AC6–AC9; AC16/AC17/AC18 en su parte)**. **Conciliada el 2026-09-23** con la remediación del bloque A de la orden de calidad: **S11 y S12 aceptadas** (corrección técnica en `fdd397f`, no de esta sesión); AC9 declarado con su alcance local. Ver §Conciliación |
| 3 · [FASE-C](05-prompt-inicio-sesion-fase-C.md) | `triage_lesson_relevance.py`: capa de pertinencia **aditiva** sobre `lecciones_index.json`, nunca filtro | ALTA: es la mitad que el verificador de capitalización declara fuera de alcance | **✅ CERRADA 2026-09-24 — VERIFICADO OFFLINE su mecánica (AC10–AC14 y AC15 en su parte no semántica; AC16/AC17/AC18 en su parte de C). AC15 queda ⚠️ PARCIAL con `acceptance = NO-EJERCITADO` (contrato E4), que es el techo alcanzable con D7 sin activar.** Cortes: la fase llegó **hasta listo para revisión** y se paró ahí. **Push hecho el 2026-09-24** por instrucción literal del operador: publicó `da382b1..5817edd`. ⟦**La paridad no se publica como cifra (2026-09-25)**: cualquier commit posterior la mueve, así que se lee con `git fetch origin --quiet && git rev-list --left-right --count origin/master...HEAD` — es la regla que este plan ya aplica a HEAD en su README⟧. **Commit hecho el 2026-09-24 con autorización explícita del operador y en dos tiempos**: `7f2e9f9` (el helper `tests/support_observador_escrituras.py`, creación de BLOQUE-B, viaja aparte por dependencia técnica: 3 tests de esta fase lo cargan en 8 puntos) y `5817edd` (las **37** rutas propias de FASE-C, +3.774 líneas, con los **7** checks del hook en verde). Quedan **fuera** por decisión del operador: los documentos del plan, el par de índice y `REGISTRY.md` — a nivel de hunk no se separa el cierre de C del trabajo de BLOQUE-B/C sobre esos archivos (164 hunks, **59** nombran FASE-C, 22 otro bloque, 83 sin marca). Consecuencia medida en un árbol extraído de HEAD con `git archive`: la suite de esta fase da **14 failed / 16 passed / 26 errors** (`SueloNoLeible: VENCIDO`, que es el guard de frescura haciendo su trabajo) y pasa a **56 passed** al regenerar el par con `build_lesson_index.py` en ese árbol; el `[6/7] --check` del hook valida contra el árbol de trabajo y **no** afirma coherencia interna del commit. Evidencia: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/` (`informe.json`, `ac10_delta.json`, `coverage.json`, `r26.txt`, `mutation/` con su verde y su rojo, `run_tests.txt`, `regression_calidad.txt`, `cero-red.txt`, `no-piso-pasado_ANTES/DESPUES.txt`, par pre/post de AC16). Métricas por fase: `09-documentacion-post-proyecto.md` §D, no este archivo. **D6 sigue dormida con causa medida** (ver su fila en §Deuda): `acceptance` no se ejercitó y no se simuló |
| 4 · [FASE-D](05-prompt-inicio-sesion-fase-D.md) | `build_phase_briefing.py`: pack derivado por fase, proveniencia con sha, negativa a truncar y **delta de carga de lectura medido** (AC19–AC23) | MEDIA: es determinista, pero gobierna lo que todas las sesiones futuras van a leer | **✅ CERRADA 2026-09-24 — VERIFICADO OFFLINE (AC19–AC23; y AC16/AC17/AC18 en su parte).** Mandato propio del operador, corte **«hasta listo para revisión»**, **sin commit ni push** (instrucción separada como siempre). **Lo que produjo**: `scripts/build_phase_briefing.py` (determinista, cero proveedor, cero red) + **5 packs** en `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/`, uno por fase del plan — COMPLETO **4**, SECCION-NO-RESUELTA **1** (RELEASE: el prompt nombra «los cuatro prompts de fase» en prosa y **no se adivina**), FUENTE-AUSENTE **0** — sobre **34** fuentes declaradas y **23** secciones pedidas, todas resueltas. ⟦**Re-medido el 2026-09-25 por la conciliación final de la orden de calidad**: ese `SECCION-NO-RESUELTA` era **conducta correcta del generador** (AC22: nombra la sección, las rutas intentadas y no adivina), y su causa —la prosa del prompt de RELEASE— se corrigió **en el prompt**, no en el generador. La corrida de hoy da **5 COMPLETO / 0 SECCION-NO-RESUELTA / 37 fuentes** (sus bytes y su porcentaje viven en la salida completa de `evidence/…/CONCILIACION-FINAL-ORDEN-2026-09-25/11-carga-corrida-3.txt`, no en esta fila). **`carga.json` NO se re-escribió** (evidencia cerrada de FASE-D, **S12**): lo que esta fila describía sigue siendo el estado que D certificó⟧. **AC20**: carga total medida en los dos lados con el mismo comando (divisor 4 declarado), con los tres sumandos por fase y la resta **entre cargas totales**; los dos totales y el delta **no se copian en este archivo**: viven en `carga.json` y `carga-pre-post.md` porque este `.md` está dentro del pack que ese `stat` mide (**L-VCF-19**); `instrumentos/comprobar_resta_carga.py` verifica cinco identidades y sale `exit 0`; el workflow canónico entra en los dos lados mientras **D3** no lo rebane, y por eso el ahorro real queda **muy por debajo de un tercio** (concatenar no es ahorrar). **AC21**: frescura por **sha256 de `sources[]`** contra el árbol, cuatro causas sin colapsar (`FUENTE-AUSENTE` / `SHA-DISTINTO` / `FUENTE-ILEGIBLE` / `PACK-AUSENTE`), HEAD publicado como procedencia y **con test que prohíbe que venza**; el pack no está en su propio `sources[]`; y el generador resuelve un plan **también bajo `Archives/`** (demostrado sobre archivados reales: es la llamada del RELEASE tras el `git mv`). **AC22**: a los tres estados del contrato se añadió una cuarta salida medida, `SIN-DECLARACION`, con su `--check` imprimiendo `SIN-FUENTES` en lugar de `OK`. **AC23**: `mutation/` con verde (declara) y rojo (no declara, y el pack se achica en silencio conservando el estado) del símbolo real `GUARD_NO_TRUNCAMIENTO_ACTIVO` — los dos tamaños, en `mutation/resumen.txt` y tampoco se copian aquí (**L-VCF-19**) —, destino por argumento obligatorio y expediente de FASE-A protegido por observador de escrituras + `huellas` (S13). **Tests**: 49 casos en `tests/quality_gates/phase_briefing/` (un estado por test, guard de cero red autouse). **AC17**: `.agents/` con **cero bytes aportados** — la casilla literal «`git status .agents/` vacío» **no era verificable** porque el árbol llegó con 3 rutas sucias ajenas del bloque B, y se afirmó como lo que goberna AC17: observador de escrituras + sha256/tamaño de los 4 archivos, iguales antes y después. **AC16**: delta 0 (quick 11/11 `exit 0`, hook 7→7) con los 49 casos declarados aparte. **Herencia de C aceptada sin reabrirla**: el pack exhibe la parte mecánica medida de C y su `acceptance = NO-EJERCITADO` **como lo que es**; E1–E5 no se renegociaron y **D6 sigue dormida** (ver su fila en §Deuda). **Deuda nueva con dueño y disparador: S16** — la convención `Lee …` que parsea el generador no está escrita en `prompt-fase-template.md`: medido, **0 de 121** prompts archivados la usan. Evidencia: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/` (`informe.json`, `carga.json`, `carga-pre-post.md`, par `faseD_carga_pre/post.txt`, par `faseD_baseline/quick_pre/post.txt`, `baseline-pre-post.md`, `r26.txt`, `cero-red.txt`, `mutation/`, `instrumentos/`) |
| 5 · [FASE-RELEASE](05-prompt-inicio-sesion-fase-RELEASE.md) | Cierre documental, sync, write-back y archivado en orden R2.5/R2.10 | MEDIA | **✅ CERRADA EN SU PARTE OFFLINE el 2026-09-25 — VERIFICADO sin red.** C0 ejercido (mandato con destinos literales, luego writers): release **4.78.0** `Gobernanza, costura, pertinencia y carga medida`, `release_date`/`date` 2026-09-25; cinco cabeceras por `sync_versions.py`; `DOMAIN_PRIMER.md` regenerado con su writer; `CHANGELOG.md` +90/0; `REGISTRY.md` por `log_phase_completion.py` (cabecera 2026-09-25). **Dos defectos de instrumento declarados con su cura pendiente en `scripts/`**: los writers reescriben sin `newline="\n"` (CRLF sobre archivos `i/lf`) y `readme_version_header` no goberna la fecha legible del README. **Sin autorización siguen**: Q7/D8 (premissa no comprobada), `--upload`/D9, `git mv`, `--fix`/`--update-baseline`, commit, push. Evidencia: `evidence/…/FASE-RELEASE/` (12 archivos) |

## Qué debe heredar cada fase

| Fase | Hereda de | Pieza concreta |
|---|---|---|
| A | — | **Estado medido del árbol, no asumido**: al publicarse la auditoría (`2c9d0c1`, 2026-09-20, paridad 0/0 con `origin/master` verificada con `git ls-remote`) el árbol está **limpio** y el índice viene regenerado y fresco; A re-mide HEAD/status al abrir porque la pareja del índice se comparte con las fases vivas de `REFACTOR-WHATSAPP`. Las cuatro aserciones vencidas A1–A4 medidas y copiadas en el maestro §1 (con **A3 rectificada: el write-back imprime `[15/15]`**), la medición A7 de carga de lectura re-medida (263.973 bytes) y la población A8 que obliga a la regla de clases de AC1 |
| A — **notas de ejecución (2026-09-21)** | lo que A encontró al medir de verdad: HEAD ya no era `2c9d0c1` sino `2deddee` (11 commits de `EVALUACION-JEV` encima) con paridad 0/0 conservada y árbol limpio; **A1–A4 siguen vencidas y A7 no se movió** (263.973 re-medidos); la población A8 se reprodujo exacta (22 + 17 líneas + 2). Dos hallazgos nuevos de la fase, con dueño: **(N1)** el disparador de **D1** era circular — «verificador verde» solo se cumple *después* de corregir `.agents/`, así que se reformuló a «verificador operativo con mutation check + decisión escrita del operador»; **(N2)** la propia prueba de AC1 **añadió 4 pins del denominador 11 en `tests/`** (familia iii de AC2), declarados en `baseline-pre-post.md` en vez de limar la aserción |
| B — **reutilizado, no reinventado** | A | `coverage_basis` con el mismo esqueleto de AC2 (`archivos_escaneados`, `poblacion`, `excluidos_por_directorio`, `limites`, `comando`, `medido_el`) y el tri-estado de AC3, que aquí se llama `provider_status` con sus `motivo_clase`. **Una adicción propia declarada**: el `status` de la puerta es binario en el escaneo (`SIN-HALLAZGOS`/`HALLAZGOS`) porque su tercer y cuarto camino (`AUSENTE`, `LECTOR-FALLIDO`) viven en la resolución del proveedor, no en el conteo — y ahí el tercero se llama `estado_lector`, no se colapsa con `NO-CONFIGURADO`. |
| B — **notas de ejecución (2026-09-21)** | lo que B encontró al medir | HEAD ya no era `e3c4573` sino `74d8ff5` (dos commits de barrido documental de FASE-A encima); `find . -name "*.jsonl"` sigue en **0** (D-V2.1 reproducida por quinta vez, métrica retirada y unidad contable declarada); **0** imports del SDK en el árbol y el SDK **no instalado** en el venv del producto (sí en `tmp_test/venv-jev-sdk`, excluido y publicado); la poblacion que `git grep` ve (678 `.py`) y la que ve el árbol de trabajo (692 en el árbol de trabajo; 690 en el primer escaneo de la fase) **difieren** y las dos se publican |
| C | A y B | La costura de B como única puerta al proveedor; los estados `AUSENTE`/`VENCIDO` de A aplicados al índice de lecciones. **Enmienda prospectiva aceptada el 2026-09-23 (orden de calidad §4.C, solo para CONTEXTO/C):** la pregunta binaria se formula como `choice` de dos opciones con `confidence` **independiente** (no con `noul`: su probabilidad de sí **no** es confianza — ver `decision_client.py`, que prohíbe `confidence` en `noul`); **AC11 elige la ruta (b)** (leer `lecciones_index.json` tras ejecutar C **ella misma** la comprobación de frescura, sin confiar en que otro gate lo regeneró), con `AUSENTE` / `VENCIDO` / `LECTOR-FALLIDO` como tres causas distinguibles; y las propuestas del proveedor falso **no** entran a §2 del `00-` en automático: exigen **revisión humana explícita con aceptación o rechazo registrado**. Detalle en `05-prompt-inicio-sesion-fase-C.md` y en el maestro §4 |
| D | A, B y C | Los tres estados y `coverage_basis`; el informe de candidatos de C, que el pack exhibe como sección propia; y **el resultado no medido de C, que D acepta sin reabrirlo** (⟦bloque C, 2026-09-24⟧: con D7 inactiva el `acceptance` de AC15 solo puede ser `NO-EJERCITADO`, así que **no** es un disparador de D6 que D pueda encontrar «cumplido»). D hereda medido lo mecánico de C y **no** lo no medido. Reglas de carga total y frescura del pack: contrato §Carga total y frescura del pack |
| RELEASE | A, B, C y D | Los cuatro `coverage.json`/`informe.json`, los pares pre/post de las cuatro fases, el delta de carga **total** medido y el registro de deuda §6 del maestro. **Tres momentos con tres permisos** (contrato §Dos momentos del cierre): el cierre offline es de la fase; la consulta Q7 (D8) y el `--upload` (D9) son remotos y cada uno necesita autorización literal y presupuesto propios; el `git mv` es un tercer momento con autorización expresa. Y el pack se **regenera con la ruta trasladada antes** de verificarlo |

## Conflictos de archivo

| Archivo / ruta | Lo toca | Riesgo y regla |
|---|---|---|
| `.opencode/LECCIONES-INDEX.md`, `.opencode/lecciones_index.json` | **Este plan y las fases vivas de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`** | **Conflicto real, ya latente.** `[6/7]` del hook bloquea el commit con el índice vencido contra el árbol, así que **ambos planes lo regeneran**. Regla: regenerar en el mismo commit, nunca `--check` contra un índice ajeno; si aparece un diff que no proviene de tu edición, re-generar y volver a medir, no `git checkout` |
| `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/` | Solo FASE-D, y solo como **generado** (**existe desde el 2026-09-24: 5 packs**) | **Efecto colateral medido por D**: los packs son `.md` dentro del corpus que escanea `build_lesson_index.py`, así que **generarlos vuelve a vencer el par del índice** (A6 sobre un artefacto derivado). La cura no es editar el generado ni el JSON: es el paso 5 del contrato — regenerar el índice sobre el árbol final. Vive dentro del plan a propósito. En `.agents/workflows/` alteraría los contadores de skills (`validate_agent_ecosystem.py`, `sync_data.py`, `doctor.py` usan `glob("*.md")`) y exigiría seguimiento en su `README.md` — y AC17 prohíbe escribir en `.agents/` |
| `scripts/run_all_validations.py` | **Este plan: solo lectura** (AC16). **Pero no está libre**: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` lo declara dentro de su alcance («su connection en `scripts/run_all_validations.py`») | Corregido el 2026-09-20: la cifra de 11 checks **no la pinea el prompt de FASE-C** de `REFACTOR-WHATSAPP` sino cuatro documentos suyos (arranque de FASE-B en su `README.md`, `06-`, `09-`, `10-`). **⟦Re-contado el 2026-09-24 por el bloque C de la orden de calidad: esa fila quedó vencida⟧** — su bloque de arranque ya no pinea la cifra, que fue sustituida por el comando que la imprime. Lo que hoy la contiene (`06-`, `09-`, `10-`, su `dependencias-fases.md` y su prompt de FASE-G, medido el 2026-09-24 con `grep -rl` sobre las dos formas de la cifra) son **registros de fases cerradas**: evidencia histórica que no se reescribe. Consecuencia para AC16: el delta 0 se contrasta contra la corrida propia, no contra esas filas. Y ese tercer plan en vuelo puede cambiar **la etiqueta y la invocación** del write-back `[15/15]` — que es justamente la fuente de verdad de A3 y del fix de AC1. Regla: AC16 (delta 0) obliga a re-medir aquí; **D10** obliga a re-leer la interfaz del write-back antes del `--upload` de este RELEASE |
| `evidence/` (raíz) | **Nadie escribe en las rutas legadas** | Corregido el 2026-09-20: `evidence/FASE-A/` … `evidence/FASE-D/` **ya existen y son de `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03`** (guardan `faseA_baseline_pre.txt`, `faseA_baseline_post.txt`, `faseB_baseline.txt`…), que son exactamente los nombres que produciría este plan si escribiera en la raíz: colisión y procedencia mezclada con un plan **archivado**. Toda la evidencia de este plan va a `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-X/`, como hace `REFACTOR-WHATSAPP` con su subdirectorio. **Se conserva la cita de lectura** a `evidence/FASE-D/measure_iterations.py`, que es el instrumento canónico del executor y vive en esa ruta legado |
| `scripts/git_hooks/pre-commit` | **Nadie** | Sus 7 checks son la otra mitad de AC16 |
| `.agents/**` | **Nadie en escritura** | AC17. Es el objeto auditado y, desde FASE-D, también la fuente que se lee para componer el pack. Copiar una sección al pack **no** es editar la fuente |
| `scripts/build_lesson_index.py` | **Nadie** (solo ejecutar) | FASE-C lo consume como suelo determinista; modificarlo cambiaría la población que publican AC11 y AC15 |
| Los `05-prompt-inicio-sesion-fase-*.md` de **cualquier** plan | FASE-D solo **lectura** | El generador parsea la lista de lectura que cada prompt declara. Reescribir prompts ajenos es justamente lo que D2/D3 postergan hasta el RELEASE del otro plan |
| `00-lecciones-capitalizadas.md`, `06-checklist-implementacion.md`, `09-…`, `10-…`, `README.md`, `dependencias-fases.md` | Todas las fases, incremental | Cierre obligatorio del contrato §Cierres. Escritos por la fase que cierra, no diferidos a RELEASE |
| `scripts/validate_governance_numbers.py` · `decision_client.py` · `triage_lesson_relevance.py` · `build_phase_briefing.py` y sus tests | Una fase cada uno | Propiedad exclusiva; ninguna fase posterior reescribe sobre lo que la anterior serializó |

## Prerrequisitos y límites visibles

- **Ningún prerrequisito de autorización central, y ninguna credencial necesaria.** Por decisión del
  operador del 2026-09-20 **no entra Jev en este plan**: FASE-B prueba la costura contra proveedores
  **falsos** y AC9 certifica que añadir uno real es un cambio de un archivo. Activar el proveedor
  habilitado es la deuda **D7**, con su disparador. Consecuencia aceptada y escrita: ningún AC de
  este plan mide calidad de decisiones de un modelo real; miden forma, aislamiento y no-regresión.
- **La capa tibia del Paso 0 no se consultó al concebir; sí en la auditoría del 2026-09-20.** QMind
  `iah-cli-lecciones` no estaba accesible en la sesión de concepción (consulta Q7, declarada NO
  EJECUTADA en `00-lecciones-capitalizadas.md` §1 y §4) y se aplicó el fallback: memoria de proyecto +
  índice generado. En la auditoría el CLI estuvo disponible y la consulta se corrió cuatro veces; sus
  lecciones ya están en §2 (L-V2.1, L-V2.2, D-V2.1) y sus efectos en AC4, AC11 y el corte de
  presupuesto. **Lo que queda es D8 como re-correr, no como descubrir.** Límite que sigue en pie: el
  triaje de FASE-C calibra contra 320 IDs definidos y 50 citados sin definición (re-medido al
  regenerar el índice por la entrada de este plan, maestro §1 A6); si el notebook aporta lecciones
  fuera del repo, ese conjunto está incompleto y así se declara en el denominador de AC15.
- **FASE-D no reduce por sí sola la lectura de las fases del otro plan.** Sus nueve prompts siguen
  citando el workflow canónico; el recorte real de esa fuente es la deuda D3. Lo que AC20 puede
  cerrar es el delta sobre las fases de **este** plan, y un delta cero o negativo es resultado
  válido si se explica.
- **Este plan convive con otros dos en vuelo.** No comparte ACs, no comparte contador de corrida, no
  consume el intento `v4complete: 0/1` de `REFACTOR-WHATSAPP`. Pero las superficies compartidas **no
  son una, son tres** (medidas el 2026-09-20): la pareja del índice de lecciones con
  `REFACTOR-WHATSAPP`; la cifra de 11 checks que ese plan pinea en cuatro de sus documentos (hoy
  **cinco, todos ellos registros de fases cerradas** tras el arranque de su `README.md` pasar a mandar
  el comando — medido el 2026-09-24, §Conflictos de archivo); y
  `scripts/run_all_validations.py` + `scripts/validate_qmind_writeback.py`, que
  `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` declara **dentro de su alcance**. Este plan no los escribe;
  los lee como fuente de verdad, y de ahí salen AC16 (delta 0) y **D10**.
- **No hay FASE-VERIFY** y por tanto ningún AC puede certificarse contra output E2E. Techo
  alcanzable: `VERIFICADO OFFLINE` con mutation check, o `NO-EJERCITADO`.

## Deuda registrada (dueño y disparador, no silencio)

| # | Deuda | Dueño | Disparador |
|---|---|---|---|
| D1 | Corregir o eliminar las aserciones A1–A4 en `.agents/` | Este plan, FASE-RELEASE, con instrucción literal del operador; ejecución adelantada por mandato de B | **Estado vigente: matriz §13 de la fuente única, no certificado aquí.** Antecedente: **Disparador reformulado el 2026-09-21 (FASE-A):** era circular («verificador verde» no puede darse antes de la corrección que el verificador pide); pasa a *verificador operativo con su mutation check en disco* — cumplido el 2026-09-21 — **y** decisión escrita del operador sobre la forma de la corrección |
| D2 | Promover `validate_governance_numbers.py` a check del `--quick` con renumeración (11 → 12) | Plan propio posterior | Sesión previa a `FASE-RELEASE` de `REFACTOR-WHATSAPP`: ya no hay fases que pineen «11 checks». **⟦Aclaración del bloque C, 2026-09-24: las enmiendas de ese bloque sobre `REFACTOR-WHATSAPP` NO satisfacen este disparador⟧** — convirtieron en «el valor lo imprime la corrida» las **instrucciones prospectivas**, y dejaron intactos los registros de sus fases cerradas (`06-`, `09-`, `10-`, su `dependencias-fases.md` y su prompt de FASE-G), que son evidencia histórica. D2 sigue necesitando su propia sesión y su propia decisión |
| D3 | Rebanar el workflow canónico por fase (bajar la carga de lectura de A7: **263.973 bytes ≈ 65.993 tokens** re-medidos el 2026-09-20 sobre la sesión de FASE-B del plan en vuelo; los 254.010 de la concepción vencieron ese mismo día) | Plan propio, posterior | Mismo disparador para el rebanado completo; **D3 parcial**, no cerrada. La simplificación encargada a B no se difiere. **No** es FASE-D: el pack unifica lecturas declaradas, no recorta la fuente |
| D4 | Verificador de la resta del par pre/post (R2.7 sigue sin instrumento mecánico) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda de proceso | Ya asignado antes que este plan; no se reasigna |
| D5 | Instrumento que compruebe que `evidence/FASE-X/` contiene el par verde/rojo (R2.8) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda de proceso | Mismo tramo que D4 |
| **D6** | **Lint de contradicciones semánticas** (`validate_plan_semantics.py`): prompts de fase contra estado real del plan, con falsos positivos medidos contra los archivados | Plan propio posterior; **entra en este mismo directorio** si el disparador se cumple mientras está vigente | **Condicionado al resultado de FASE-C**: que el triaje entregue candidatos que el Paso 0 no ancló, con su aceptabilidad medida publicada en el informe. Si FASE-C sale inaceptable, **no se activa**: no se apila un segundo consumidor sobre una base que no funcionó. ⟦Precisión del bloque C, 2026-09-24⟧: mientras **D7** esté inactiva, la rama «salió aceptable» **no es alcanzable** — con proveedor falso `acceptance` solo puede publicarse `NO-EJERCITADO` (contrato **E4**), así que D6 queda **dormida con causa**, no «pendiente de que alguien consulte el número». Se re-evalúa al activar D7, no antes. **⟦Medido al cerrar FASE-C el 2026-09-24: la condición se cumplió literalmente — `coverage.json` publica `acceptance = NO-EJERCITADO` con su motivo y `valor: null`, sin cifra simulada (contrato E4). D6 queda DORMIDA y este plan no abre el lint semántico sobre una base que no juzgó nada; su re-evaluación sigue atada a D7⟧** **⟦Re-declarada al cerrar FASE-D el 2026-09-24 — no re-abierta ni re-asignada por interpretación: D leyó el `coverage.json` de C y encontró exactamente lo mismo que publicó C (`NO-EJERCITADO`, `valor: null`), así que la rama «el triaje salió aceptable» sigue sin ser alcanzable mientras D7 esté inactiva. D no reabrió C, no renegoció E1–E5 y no presentó la exhibición de candidatos en el pack como aceptabilidad obtenida. Lo único que activaría D6 es un proveedor real mediante (D7), y ese no es el estado de este plan⟧** |
| **D7** | **Activar el proveedor de decisiones ya habilitado** (Jev) como segundo proveedor detrás de `decision_client.py`; correr la comparación de proveedores y restituir «elegir midiendo» como AC | Plan propio posterior | Acceso existente desde 2026-09-20, pospuesto por decisión del operador. El consumidor natural es D6, el único trabajo genuinamente semántico del lote |
| D8 | Re-ejecutar la consulta Q7 de QMind. **Premisa vencida: el 2026-09-20 el CLI sí estaba disponible y la consulta se corrió en la auditoría de la concepción** (cuatro `retrieve`, resultados capitalizados como L-V2.1, L-V2.2 y D-V2.1). **Y su forma publicada es incorrecta**: `--nb iah-cli-lecciones` devuelve `error: Bad request`; hay que pasar el ID `01a04d98-b7bd-778c-8441-26fdc7e35f45` | Este plan, sesión previa a FASE-RELEASE (re-corrida, no primera vez) | Que el notebook haya cambiado desde la auditoría, o que se quiera verificar el comando corregido con las citas que ya devolvió |
| D9 | Write-back de `10-analisis-post-implementacion.md` a QMind | Este plan, FASE-RELEASE | Orden R2.5/R2.10: `--upload` **antes** del `git mv`, y segunda regeneración del índice después |
| **D10** | **Re-leer la interfaz del write-back antes de correr el cierre.** `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` (commiteado, PENDIENTE, con disparador anterior al RELEASE de `REFACTOR-WHATSAPP`) piensa añadir `--title`/`--file` a `validate_qmind_writeback.py`, verificar contenido en vez de título, quitar la degradación a PASS y tocar su conexión en `run_all_validations.py` | Este plan, FASE-RELEASE | **CUMPLIDA en su lectura el 2026-09-25** (FASE-RELEASE): `validate_qmind_writeback.py --help` contra el árbol vigente → `--nb`, `--strict`, `--upload`; **sin** `--title` ni `--file`, decide por título y degrada a `exit 0` sin CLI. La firma **no** cambió (el mini-plan no se ejecutó), así que `04-contrato-ejecucion.md` **no** se re-escribió; lectura con su evidencia en `evidence/…/FASE-RELEASE/02-tarea1-firma-writer.txt`. Queda vigente la advertencia para quien sí corra la subida: verificar por contenido, no por título |

### Ejecución del bloque B de la orden de calidad (2026-09-23) — coordinación, no nuevo propietario

**Estado vigente: matriz §13 de la fuente única citada al inicio.** Las declaraciones de resolución
y suficiencia de pruebas que siguen son antecedentes retirados de §1–§12; no aceptación actual.

El operador autorizó el bloque B de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` y, dentro de él,
**adelantar D1 y la parte de D3 que B necesita** respecto de sus disparadores originales. Se registra
aquí sin crear un propietario paralelo: los dueños son los que fija el maestro §6 (D1 = «Este plan,
FASE-RELEASE»; D2/D3 = «Plan propio, posterior»); B ejecutó contenido bajo mandato, no reclamó la
propiedad. **Ampliación de alcance registrada:** el mandato B listaba el executor y
`prompt-fase-template.md`, pero retirar A4 (D1) exigía tocar su fuente,
`.agents/workflows/templates/lecciones-capitalizadas-template.md`; el operador autorizó expresamente
esa ampliación el 2026-09-23 y confirmó mantener los campos `version:` de frontmatter del executor
(v2.25.0) y de la plantilla (v1.6.0) como metadato documental, no bump de release (`VERSION.yaml`
intacto).

- **D1 — estado vigente en la matriz §13; no certificada aquí.** **Antecedente retirado** del
  2026-09-23: el dictamen decía «RESUELTA y revalidada». Las cuatro aserciones A1–A4 se corrigieron/retiraron **desde su
  fuente** (`.agents/`): el árbol vigente ya sale `SIN-HALLAZGOS` (`validate_governance_numbers.py`
  exit 0, vuelto a medir en la remediación). La decisión de forma fue retirar el denominador volátil
  en lugar de copiar la cifra vigente (la opción que el propio plan ya recomendaba: «dejar que el
  verificador la imprima es la que no se desfasa»). La detección no se debilitó: las cuatro
  aserciones quedaron reancladas a un **contraejemplo congelado** en
  `tests/quality_gates/governance_numbers/fixtures/` con sus mutantes, más una regresión del árbol
  honesto. Sin renumerar checks (**D2** sigue fuera).
- **S13 — estado vigente en la matriz §13; no certificada aquí.** **Antecedente retirado:** el
  dictamen del 2026-09-23 decía «RESUELTA, con la parte que faltaba hecha en la remediación del mismo día». El arnés
  `test_governance_numbers_mutation_por_asercion.py` ya no escribe en `evidence/…/FASE-A/mutation/`.
  El primer retiro **movió el destino pero seguía midiendo estado final** (instantáneas
  antes/después), y su control negativo definía una función de huellas propia dentro del test y
  provocaba el rojo con `os.utime`: no observaba escrituras. Ahora se observan las **operaciones de
  escritura** del escritor real con `tests/support_observador_escrituras.py` (alcance declarado:
  proceso de pytest, no procesos hijos), con ancla positiva, y los tres controles negativos del
  mandato (a escritor redirigido a destino protegido, b bytes idénticos, c mtime restaurado) sobre un
  **expediente desechable**. Se conserva la comparación de contenido y metadatos del expediente
  protegido. Cierre de la deuda que el bloque A dejó viva.
- **Controles negativos sobre el instrumento real (remediación, mismo día).** Ningún rojo por causa se
  produce ya reimplementando el defecto dentro del test:
  `test_control_negativo_el_escritor_permisivo_vuelve_a_afirmar_de_mas` corre el **escritor commiteado
  en `da382b1`** (leído con `git show`, materializado en un temporal —sin `checkout` ni `stash`—) y su
  `- [x] Tests passing` rompe la misma exigencia;
  `test_control_negativo_el_instrumento_versionado_re_llamaba_y_el_de_hoy_no` mide los **cálculos de
  verificador** en ese módulo versionado contra el del árbol, con la misma inyección y la misma conta
  (cifras PRE/POST y procedencia: resumen del bloque B, §4.1 y §4.3). Con eso
  el PRE queda anclado a una revisión, no a «el árbol que había cuando corri». ⟦Nombre rectificado el
  2026-09-23: la fila anterior citaba `…_recalcula_y_el_actual_no`, nombre que no existe en disco.⟧
- **D3 — ADELANTADA EN PARTE, NO CERRADA.** Se ejecutó lo que B requería: principio de
  proporcionalidad/reuso, retiro de cuotas «mínimo 3 lecciones», y **cortes utilizables sin commit**
  (los **cinco** terminan en espera de autorización; el commit es una acción posterior y separada,
  opcional, no el quinto corte). La remediación añadió lo que el
  primer pase dejó contradicho: la resolución de «RELEASE no registra» vs «registrar cada fase», y la
  sustitución de métricas copiadas en README/`09`/`10` por referencia a su fuente. Nada de eso se
  difiere a D2, al bloque C ni al piloto. El rebanado completo del workflow canónico (bajar la carga
  de lectura por fase) **sigue diferido** a su disparador (sesión previa a FASE-RELEASE de
  `REFACTOR-WHATSAPP`) y conserva su dueño del maestro §6: **«Plan propio, posterior»**, no se
  reasigna. No se declara D3 cumplida ni se midió reducción de carga (no hay ahorro D3 que afirmar).
- **Pendientes que B dejó y cómo están ahora.** ⟦Re-lectura el 2026-09-24 por el bloque C⟧ La fila
  original decía «el árbol de B está **sin commitear** (mandato: cero commit/push); el bloque C (enmiendas
  prospectivas a los cuatro planes) y el piloto FASE-C siguen pendientes de su autorización». De esas tres
  cosas, **dos cambiaron y una queda igual**:
  - **sin commitear**: sigue vigente y **no** lo mueve este bloque. El mandato del bloque C también
    prohíbe commit y push; su árbol —el de B y el de estas enmiendas— se entrega sin commitear y el
    commit es decisión separada del operador.
  - **bloque C**: **autorizado el 2026-09-24**, y ejecutado como enmiendas documentales sobre los cuatro
    planes (§Bloque C abajo). No es el piloto.
  - **piloto FASE-C**: **sigue sin autorización** y no se ejecutó. Su contrato está conciliado y su
    prompt listo; eso habilita pedir el mandato, no ejecutarlo.
  **Frontera de red:** la corrida `--check` **completa** que hizo la primera sesión de B
  incluye el check QMind y en esta máquina el CLI `qmind` está instalado, así que «cero red» **no puede
  afirmarse** y queda **NO DETERMINADO** (no se preservó su stdout; no se repite la llamada). El bloque C
  **tampoco** determinó esa fila: no corrió el `--check` completo ni hizo llamada alguna. Las citas
  «mandato §1…§8» tampoco apuntaban a nada versionado: el mandato llegó como adjunto del operador y se
  archivó como copia byte a byte en
  `evidence/…/BLOQUE-B-REMEDIACION-2026-09-23/99-mandato-de-remediacion-B-2026-09-23.txt`
  (sha256 `5a12e90f04a1ab3e4536bbe451c62d6dab1deac268706fbef02b1e12a9c31394`, procedencia y límites en
  `99-procedencia-del-mandato.md`).
  Fuente única de resultados de B:
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
  (el resumen de la primera sesión, `…/BLOQUE-B-ORDEN-CALIDAD-2026-09-23/00-resumen-bloque-B.md`,
  queda como antecedente con su cierre retirado).

## Bloque C de la orden de calidad (2026-09-24) — qué se concilió en este plan

Autorización: **solo enmiendas prospectivas sobre los documentos de los cuatro planes**, más el par del
índice de lecciones regenerado por su generador y la evidencia del bloque. Prohibido: código, tests,
`VERSION.yaml`, `AGENTS.md`, `.cursorrules`, `.agents/**`, hooks, configuración, `sync_versions.py`,
`build_lesson_index.py`, REGISTRY, red, QMind, pipeline, archivado, commit y push. Evidencia:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/`.

| Fila §4.C | Qué quedó resuelto | Dónde |
|---|---|---|
| `CONTEXTO/C` | **Nada que renegociar.** E1–E5 se conservan y su forma se reconfirmó contra `scripts/decision_client.py` (la validación de `RespuestaEleccion` exige `confidence`; `RespuestaNoul` la fija en `None` y la puerta rechaza que un `noul` la reporte). **AC15 semántico `NO-EJERCITADO` y D6 dormida** quedan admitidos explícitamente en la fila D6 de arriba | contrato §Enmiendas + este archivo |
| `CONTEXTO/D` | **Carga total** con tres sumandos (`workflow_obligatorio`, `coste_de_generacion`, `pack_consumido`) y resta entre totales: concatenar no es ahorrar. **Frescura por sha de las fuentes relevantes; HEAD es procedencia, no llave de caducidad** (corta la invalidación circular por el commit del generado). **Regeneración del pack tras el traslado antes de verificarlo** y AC19 obliga a resolver rutas archivadas. **D acepta el resultado no medido de C** | contrato §Carga total y frescura del pack, §Cierres item 8, maestro AC19/AC20/AC21, prompt FASE-D |
| `CONTEXTO/RELEASE` | **Cuatro permisos, no tres** ⟦rectificado 2026-09-25; la etiqueta «tres momentos» sigue siendo el título-history del bloque por sus cinco referencias vivas⟧: **C0 destinos escribibles** (offline = sin red, **no** permiso de escritura: `sync_versions.py` sin `--check` puede reescribir `README.md` de raíz, `AGENTS.md`, `.cursorrules`, `docs/CONTRIBUTING.md` y `docs/GUIA_TECNICA.md` según `sync_config.yaml`; `VERSION.yaml` es entrada y REGISTRY + `.last_doc_phase.json` salen del escritor del registro) · **cierre offline verificado** · **remoto** (D8 y D9, cada uno con autorización literal y presupuesto) · **traslado**. Se separa el mandato de la fase de esos permisos, con `PENDIENTE-AUTORIZACION` en vez de omisión. **Leer el estado ≠ reparar**: correr `validate_governance_numbers.py` es verificación y la reparación de `.agents/` no vuelve a hacerse aquí. **Sin writers automáticos**: `--fix` y `--update-baseline` salieron de la secuencia; los checks no escriben y ningún baseline se actualiza para absorber errores. **El `--check` posterior al traslado se apoya en una regeneración prevista**, y un rojo de un derivado no autoriza editar código. **D2 no se da por satisfecho** por las enmiendas de `REFACTOR-WHATSAPP` | contrato §Dos momentos del cierre y §Orden del cierre, prompt FASE-RELEASE |

**Qué este bloque NO tocó y por qué.** No ejecutó el piloto FASE-C ni ninguna fase; no activó D6 ni D7;
no movió `VERSION.yaml` ni las versiones documentales de `04-`/`06-`; no escribió en `AGENTS.md`,
`.agents/**`, hooks, `REGISTRY.md` ni su tracker auxiliar; no regeneró DOMAIN_PRIMER; no tocó la
evidencia histórica de FASE-A/B ni los prompts de fases cerradas. La **incompatibilidad declarada** que
queda fuera de su alcance: `AGENTS.md` (§Vinculo con la Documentación) sigue condensando DOMAIN_PRIMER
en «se regenera en FASE-RELEASE» y `docs/CONTRIBUTING.md` titula «Regenerar» a su Paso 5b mientras la
fila de su tabla dice «Se VERIFICA»; son documentos centrales que la fila `WHATSAPP` resuelve **para el
plan** (regenerar al cerrar cada fase, verificar en RELEASE), pero alinearlos a ellos exige instrucción
expresa aparte y no se hizo por arrastre.

## Rutas ajenas en el árbol al commitear FASE-B (medido, no supuesto)

Al cerrar FASE-B (2026-09-21) había **tres rutas ajenas** en el árbol. Al abrir su tramo de commit
quedaba **una**: `.opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/dependencias-fases.md`, que el
commit de esta fase **deja fuera** y sobre la que no se hace `git checkout` (es trabajo en curso de otra
sesión, no basura que limpiar; precedente: FASE-A excluyó a propósito sus dos rutas ajenas).

Las otras dos —`ROADMAP.md` y `.opencode/context/Refuerzo.md`— se las llevó la otra sesión en `eecf246`,
que ese día era el HEAD del repo y estaba **sin empujar** (`git rev-list --left-right --count
origin/master...HEAD` → `0/1`). Consecuencia declarada: **el commit de FASE-B se apoyaba sobre un commit
ajeno todavía no publicado** — y el push del mismo 2026-09-22 lo publicó con los cuatro de esta fase,
como queda escrito debajo, y el HEAD sobre el que esta fase midió su par pre/post (`74d8ff5`) ya no es
el HEAD. Las restas no se mueven —los cuatro archivos gobernados por AC16/AC17 no están en ninguno de los
dos commits y su `git diff --numstat` sigue vacío—, pero la premisa «el árbol de partida es solo mío»
queda refutada y así queda escrita (medición A6 del maestro, cumplida sobre esta propia fase). Detalle con
comandos y mtimes en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/baseline-pre-post.md`
§Rutas ajenas.

**Cerrado el 2026-09-22.** El commit de FASE-B está hecho — **`647f436`** (46 archivos, +4.412/−97), con
instrucción literal del operador y con el par del índice de lecciones dentro, así que `[6/7]` del hook no
lo cortó y los **7** checks pasaron. Dos consecuencias re-medidas para quien abra FASE-C: la paridad con
`origin/master` era **`0/2`** al cerrarlo, **`0/3`** tras su propio barrido de citas (`612efd0`) y
**`0/5`** tras el micro-barrido (`cf64faf`) — cada commit documental suma uno, así que la cifra se re-mide
y no se copia—; y **el push se hizo el 2026-09-22 con instrucción literal del operador**, que publicó
`74d8ff5..b764e8d` —los cinco commits, incluido el ajeno `eecf246` que era su ancestro obligado— y dejó
paridad **`0/0`** medida tras `git fetch`; y el propio commit movió el denominador que la fase había publicado — **678 → 691** `.py`
rastreados —, con lo que la resta de AC6 quedó rectificada con su nota y su residuo de un archivo
(`.venv-wsl/bin/activate_this.py`, exclusión no declarada) registrado como **S11** con su lección
**L-VCF-11**. Y el re-muestreo que hizo falta para medir esa rectificación **pisó la evidencia cerrada de
FASE-A**: `validate_governance_numbers.py --report` tiene su destino hardcodeado en
`evidence/…/FASE-A/informe.json`, así que el comando canónico del plan re-escribe el registro de otra
fase en cada corrida. Se revirtió (`git checkout --` sobre ese archivo) y se re-muestreó con destino
explícito, que da el mismo `HALLAZGOS` (A1–A4, 24 instancias, `exit 1`) sin tocarlo → **S12** /
**L-VCF-12**, con su guarda publicada en el README para quien abra FASE-C.

## Conciliación con la remediación del bloque A — aceptación de S11 y S12 (2026-09-23)

**Qué se acepta y de dónde viene (procedencia, no atribución a esta sesión).** Las dos deudas
nacidas del commit de FASE-B fueron corregidas **fuera de este plan**, por las cuatro sesiones
autorizadas del **bloque A** de `.opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`, y el
código corregido entró al repo en **`fdd397f`** sobre la superficie
`scripts/decision_client.py`, `scripts/validate_governance_numbers.py`,
`tests/quality_gates/decision_client/` y `tests/quality_gates/governance_numbers/`. El resumen de esa
remediación (`evidence/…/REMEDIACION-BLOQUE-A-2026-09-22/00-resumen-bloque-A.md` §4) dice de sí misma,
y se cita literal por ser el límite que esta fila respeta: **«lo aplicado es CORRECCIÓN TÉCNICA, no
cierre contractual»**, porque el traslado de S11/S12 a ese bloque exigía la enmienda registrada **en
este plan**, que era el pendiente. **Ese pendiente es lo que esta sección cierra**: el plan propietario
CONTEXTO acepta la remediación y registra el traslado. El mérito técnico es de esas sesiones y de `fdd397f`;
esta sesión **no** editó código ni tests.

**Alcance de lo aceptado** — solo S11 y S12, y solo en lo que el bloque A hizo:

| Deuda | Cura aceptada (en `fdd397f`) | Re-validación offline medida el 2026-09-23 |
|---|---|---|
| **S11** — `.venv-wsl` faltaba en `ARCHIVOS_EXCLUIDOS_DE_LA_POBLACION` y las exclusiones se solapan | La exclusión entra en la lista **y su conteo se publica**; dos pruebas de población sobre árbol plantado; el escaneo se comparte entre aserciones del mismo árbol | `python scripts/decision_client.py --scan-imports` → `SIN-HALLAZGOS`, **0** imports prohibidos, `exit 0`; población escaneada **696** vs `git ls-files '*.py'` = **696** → **residuo 0** (la resta que en B cerró en 692−691 ya no existe); `.venv-wsl` figura en `excluidos_por_directorio` con **582** archivos |
| **S12** — `--report` sin destino re-escribía `evidence/…/FASE-A/informe.json` | El destino por defecto desaparece de los dos verificadores: `--report` a secas **imprime y no escribe**; el aviso va a stderr y el stdout queda JSON puro; **seis** tests nuevos en `tests/quality_gates/governance_numbers/` ⟦rectificado el 2026-09-23: esta fila decía «cinco»; corridos por nombre dan **6 funciones / 6 casos** en `test_governance_numbers_s12_report_no_escribe.py`, y el directorio completo **35 funciones / 40 casos**, `40 passed` con `EXIT=0`⟧ | `python scripts/validate_governance_numbers.py --report` sin destino → **`exit 1`** con `status: HALLAZGOS` y `assertion_ids = [A1,A2,A3,A4]`; `sha256` de `evidence/…/FASE-A/informe.json` **idéntico** antes y después de la corrida; `git status --porcelain evidence/` **vacío** |

**Los tres momentos van separados, y así quedan:** (1) **cierre original de FASE-B** — `647f436`
(2026-09-22), que cerró AC6–AC9 y **produjo** S11/S12 al mover el denominador y al re-muestrear;
(2) **corrección posterior** — `fdd397f` (2026-09-22), bloque A de la orden, técnica y probada por su
dueño; (3) **aceptación** — esta sección, 2026-09-23, que además re-mide offline. Ninguna de las tres
se atribuye a las otras dos.

**Qué NO cerró aquella aceptación (antecedente fechado).** El rojo contractual A1–A4 seguía vivo:
`validate_governance_numbers.py` salía `exit 1` porque aquella sesión no editaba `.agents/` (AC17,
D1/S1); la remediación del bloque A no lo tocó. Después B recibió autorización de corrección, pero
su estado vigente remite a la **matriz §13** de la fuente única, no a ese rojo ni a verdes retirados.
Y siguen abiertas, con dueño, **sin** convertirse en bloqueantes artificiales de una
FASE-C offline: **S10** (dónde vivirá el `import` del SDK cuando D7 se active), **D7** (activar el
proveedor) y **D6** (lint semántico, **dormida** porque su disparador es el `acceptance` de AC15).

**AC9 queda declarado con su alcance real** (no solo su cifra): certifica **extensión local** —
registrar un proveedor **falso** del repo a través de la costura, sin red ni credenciales, medido por
sha256 (`files_changed_to_add_provider = 1`, re-medido el 2026-09-23 con `--costura`, `exit 0`). **No**
certifica el coste total de integrar un **SDK real** en un archivo: dependencias y autenticación no se
midieron ni pueden medirse bajo la regla de cero red. El propio `--costura` ya imprime esa acotación
en su clave `alcance_de_ac9`, y la ubicación futura de ese SDK es **S10**/D7, coordinada con el plan
hermano `EVALUACION-JEV-TYPESAFE-2026-09-21`.

**Instrumentos reutilizados, no nuevos.** Esta conciliación no añadió instrumentación: corrieron los
existentes de B (`--scan-imports`, `--costura`, `--provider-status`) y de A (`--report`), más la
selección `tests/quality_gates/decision_client` (**87 passed**, `exit 0`). **No se repitió la suite
completa por rutina**: su estado vigente es el que publicó la sesión 4 del bloque A, y lo que aquí se
ejecutó es la selección pertinente, distinguible de los resultados históricos de B. Crudos, comandos y
códigos en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/CONCILIACION-B-Y-CONTRATO-C-2026-09-23/`.

### S16 — la convención que parsea el generador no está escrita en ninguna fuente (nueva, 2026-09-24)

**Hecho medido al cerrar FASE-D**: `build_phase_briefing.py` extrae la lista de lectura del prompt
desde la cadena `Lee …` dentro de un bloque fenced de «Prompt de ejecución». Sobre el corpus
completo: **121** prompts de fase bajo `.opencode/plans/Archives/` y **0** la usan; **5** prompts la
usan en todo el repo y son los cinco de este plan. Consecuencia directa y probada: el pack de un
plan archivado sale `SIN-DECLARACION` y su `--check` imprime `SIN-FUENTES` — el corte del
generador, no su defecto.

- **Dueño**: `.agents/workflows/templates/prompt-fase-template.md`, sección 8 (Prompt de Ejecución),
  y por arrastre los prompts de los planes vivos. **No es de FASE-D**: escribir en `.agents/` es
  AC17 y esa superficie es D1/con instrucción literal del operador.
- **Disparador**: la próxima vez que un mandato autorice tocar el template (precedente: el bloque B
  de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22` autorizó `lecciones-capitalizadas-template.md` para
  retirar A4). Ahí se añade la forma canónica de la lista de lectura, y FASE-RELEASE de este plan
  **no** la reescribe.
- **Por qué se registra y no se calla**: sin esta fila, un lector de 2026-12 verá packs vacíos para
  los planes archivados y concluirá que el generador está roto. L-R.4: una regla de proceso sin
  verificador es publicable solo si la regla lo declara — y aquí lo declara el propio pack.
- **Alternativa descartada**: hacer que el generador adivine la lectura por heurística de rutas
  (`*.md` citados en el prompt). Convertiría `SECCION-NO-RESUELTA` en una invención silenciosa, que
  es la familia de defecto que L-PF6/L-PF10 trajeron a este plan.

### S17 — los writers de texto reescriben en CRLF archivos que git almacena en LF (nueva, 2026-09-25)

**Hecho medido al cerrar FASE-RELEASE**: la escritura final de `SyncEngine.sync_rule` en
`scripts/sync_versions.py` y la de `run_regenerate_domain_primer` en `scripts/doctor.py` cierran con
`write_text(..., encoding="utf-8")` **sin** `newline="\n"`. En Windows eso re-escribe en CRLF un
archivo que git almacena en `i/lf`. Medido en la corrida: **6** archivos quedaron
`[FAIL] Line endings` tras el sync y la regeneración (lo cortó el detector de finales de línea que el
bloque B de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22` añadió a `validate_document_integration.py`), y
el expediente `FASE-RELEASE/12-normalizacion-lf.txt` registra la normalización byte a byte con
`git diff -U0` comprobando que el delta seguía siendo solo tokens de versión/fecha/codename. El
antecedente de la cura correcta vive en el propio repo: `scripts/log_phase_completion.py` pasa
`newline="\n"` y lo documenta junto a la escritura.

- **Dueño**: `scripts/sync_versions.py` y `scripts/doctor.py`. Es edición de `scripts/`, **no** de este
  plan ni de la orden: FASE-RELEASE tiene prohibido modificar código, y ese fue el motivo exacto por el
  que aquí se declaró el defecto en lugar de curarlo.
- **Disparador**: el próximo mandato que autorice literalmente editar esos dos writers. La cura es el
  parámetro en la escritura, no la normalización posterior del árbol.
- **Remedio vigente (provisional y declarado)**: normalizar por bytes al cerrar. No es la cura — deja el
  defecto en el escritor, que es la regla que este plan ya aplica a los datos: *un dato con escritor se
  arregla en el escritor o con un verificador, no con un tercero que lo reescriba a mano*.
- **Alternativa descartada**: fixedear los finales de línea en cada llamada desde los dos cierres del
  RELEASE sin tocar el writer (sería el mismo remiendo en dos sitios más) y reconfigurar `text`/`eol`
  de git: eso cambiaría el árbol de trabajo de archivos ajenos a este plan para tapar un defecto local.

**⟦CURADA el 2026-09-25 en una sesión aparte, con mandato de código del operador⟧.** El disparador de
arriba se cumplió ese mismo día: se autorizó editar `scripts/sync_versions.py` y `scripts/doctor.py` más
sus tests. Estado de la cura:

- **Tres escrituras**, no dos. Al curar apareció una tercera de la misma familia en el mismo archivo:
  `run_status` escribe `.agent/SYSTEM_STATUS.md`, y estaba dejando el árbol en `w/crlf` contra su propio
  `i/lf` (medido con `git ls-files --eol` antes de tocar nada). Las tres llevan ahora `newline="\n"`:
  `SyncEngine.sync_rule`, `run_regenerate_domain_primer` y `run_status`.
- **Prueba por comportamiento, no por parámetro**: `tests/test_sync_writers_lf_y_fecha_readme.py` corre
  los **escritores reales** sobre repositorios temporales y afirma sobre los bytes emitidos. Su control
  negativo ejecuta la versión **commiteada** de cada script (`git show HEAD:…`, sin `checkout` ni
  `stash`): el viejo escribe CRLF y el nuevo LF en el mismo entorno, así que la diferencia es
  atribuible al parámetro y no a la máquina.
- **Límite declarado**: la traducción `\n` → `\r\n` es propiedad del SO. La prueba **mide** si este SO
  traduce (`_traduce_a_crlf()`) y, donde no traduzca, las tres comprobaciones de bytes se saltan con
  motivo en vez de dar un verde que no observó nada. Las de S18 son portables.
- Con la cura hecha, el `--check` del sync volvió a `All files in sync` y la normalización manual por
  bytes del cierre de RELEASE (`12-normalizacion-lf.txt`) queda como antecedente: el próximo cierre no
  la necesita. No se re-escribió ese expediente cerrado (**S12**).

### S18 — `readme_version_header` no goberna la fecha legible de `README.md` (nueva, 2026-09-25)

**Hecho medido al cerrar FASE-RELEASE**: después del sync de cinco cabeceras, la línea de estado de
`README.md` seguía diciendo `Actualizado 11 Septiembre 2026` con `release_date: 2026-09-25` ya en la
fuente única. La regla `readme_version_header` de `scripts/sync_config.yaml` tiene patrón para el token
de versión pero no para esa etiqueta de fecha; la regla hermana `guia_tecnica_header` sí la goberna, y
`docs/GUIA_TECNICA.md` movió su fecha en la misma corrida.

- **Corte de cobertura declarado, no deducido**: el quick `[3/11] Version Sync` dio **PASS** con el
  README desfasado, así que la comprobación vigente no mira esa etiqueta. El rojo solo lo ve un lector
  humano — que es lo que lo encontró — y por eso se registra con deuda en vez de con un verde.
- **Dueño**: `scripts/sync_config.yaml` y el lector de esa regla en `scripts/sync_versions.py`.
- **Disparador**: el próximo mandato que autorice editar el config de sync o sus patrones de header; o
  la próxima release, si se quiere que la fecha del README salga por su escritor.
- **Alternativa descartada**: editar esa línea del README a mano. Crearía un segundo escritor sobre un
  dato que ya tiene uno — la familia exacta de la que `scripts/sync_config.yaml` retiró la regla
  `registry_last_update` el 2026-09-23.

**⟦CURADA el 2026-09-25, en la misma sesión que S17 y con el mismo mandato de código⟧.**

- El patrón llega ahora hasta la fecha (`… | Actualizado[^\n|]*`) y el template emite `{date_text}`, la
  forma larga que `_interpolate` ya sabía producir: «25 Septiembre 2026». **No** entra un ISO en la
  cabecera — hay prueba que lo prohíbe, porque cambiar el formato que el documento mostraba no era lo
  que pedía la deuda. `[^\n|]*` no cruza la línea ni el separador, así que no alcanza otras menciones
  de «Actualizado» (hay una línea de contexto con esa palabra como señuelo en la prueba).
- El corte de cobertura quedó cerrado en el árbol real, y se midió antes de celebrarlo: con la regla
  vigente, el `--check` del sync pasó de `IN_SYNC` a **`FAIL: README.md (readme_version_header) - needs
  update`** sobre el README que dejó la release. Ese rojo es la detección funcionando, no una regresión.
- Escribir `README.md` es destino central y no estaba en el mandato de código: se pidió y se autorizó
  aparte (`python scripts/sync_versions.py --rule readme_version_header`, 2026-09-25). Delta real: la
  **línea 5** (fecha). `git diff --numstat` contra `HEAD` marca 2/2 porque la cabecera de versión ya
  la movió la release; la separación se comprobó con `git diff -U0` y con huellas antes/después en
  `evidence/…/CIERRE-ORDEN-2026-09-25/07-guard-idempotencia-sync.txt`, donde una segunda corrida del
  mismo comando no mueve **ninguna** de las diez rutas vigiladas.
- El espejo de prueba allana **las dos** líneas que goberna la regla: con solo la cabecera allanada, el
  `FAIL` llegaba por la segunda sustitución y no por la fecha. Medido, y por eso está escrito.


> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md` · sha256 `a38da8ea12a6a54ef5598925e54e6132881306439236419c6b597d2dd4696723` · 56768 bytes copiados de 56768 del documento · HEAD `a81da09` · generado `2026-09-26T03:06:52Z`

---

<!-- BEGIN BRIEFING-META
{
  "generado_por": "scripts/build_phase_briefing.py",
  "plan": "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20",
  "fase": "B",
  "estado": "COMPLETO",
  "declaracion": "DECLARADA",
  "provenance": {
    "head": "a81da09",
    "generated_at": "2026-09-26T03:06:52Z"
  },
  "no_incluye": [
    "01-plan-maestro.md — 19097 bytes fuera de lo declarado (2, 4)",
    "00-lecciones-capitalizadas.md — 38226 bytes fuera de lo declarado (2)"
  ],
  "lectura_aparte_obligatoria": [
    ".agents/workflows/phased_project_executor.md"
  ],
  "sources": [
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/01-plan-maestro.md",
      "sha256": "1872761743009e43998c568717282545ac7a106cc86acfd1285078e995a0b3b7",
      "documento": "01-plan-maestro.md",
      "secciones": [
        "2",
        "4"
      ],
      "en_pack": true
    },
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/04-contrato-ejecucion.md",
      "sha256": "c4d18dc91998a0086c93fef0182f8f82a48367b7afcd8aa799bed43577fe06e5",
      "documento": "04-contrato-ejecucion.md",
      "secciones": [],
      "en_pack": true
    },
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/00-lecciones-capitalizadas.md",
      "sha256": "f6c1a005848008424dfe9128d48500a0fdff0fa5ba3a967c73b8b5c6eb0b8ec0",
      "documento": "00-lecciones-capitalizadas.md",
      "secciones": [
        "2"
      ],
      "en_pack": true
    },
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md",
      "sha256": "a38da8ea12a6a54ef5598925e54e6132881306439236419c6b597d2dd4696723",
      "documento": "dependencias-fases.md",
      "secciones": [],
      "en_pack": true
    }
  ],
  "divisor_tokens": 4
}
END BRIEFING-META -->
