# Censo de citas vencidas por el estampado del `10-analisis` (SESIÓN 2 del piloto JEV, 2026-10-09)

Qué se pregunta: qué textos del plan, de sus índices y del CHANGELOG contradice la anotación aditiva que se
estampó hoy en `10-analisis-post-implementacion.md` (sha en disco `b88e3e08a70d…`, íntegro en `11-`). Las
cuatro afirmaciones de la firma son: (1) B2-1/B2-1c/B2-1e/B2-1d curadas; (2) el rebase del techo 139 era de
**dos** brazos (jev 145 +6 y deepseek 158 +19); (3) la cuenta publicada decía **2 llamadas** y la real al
cerrar era **4**; (4) la población del notebook es **61**, no la `59 → 60` que traía el mandato.

## 1. Método: tres pasadas, ninguna suficiente sola

- **Pasada A — subagente `Explore`, solo lectura.** Barrido semántico con 38 patrones sobre 16 archivos;
  devolvió 38 filas clasificadas a mano. **Es la pasada que encontró lo que la B no podía ver** (§4).
- **Pasada B — regla mecánica a nivel de LÍNEA.** Una línea lleva sello propio si cae dentro de un bloque
  `⟦ … ⟧` abierto antes **o** si ella misma contiene `⟦`/`⟧`. La versión ingenua (solo el bloque abierto)
  clasificó mal 12 líneas: una anotación de una sola línea no deja el estado «dentro» al cerrarse. Corregida,
  las tres filas de `06-checklist` y la celda de `09-documentacion:35` pasaron a CON-SELLO.
  **Totales: 29 coincidencias — 20 con sello, 9 sin sello.**
- **Pasada C — regla mecánica a nivel de CELDA, con cabecera de tabla.** Divide cada fila por `|`, resuelve la
  cabecera de columna (`Preparación | A | B | C | RELEASE (2026-10-05)`) y mira el sello **de esa celda**.
  Añade patrones de **cuenta** (`Inferencias Jev/DeepSeek`, `2 llamadas`, `0 envíos`, `llamadas_usadas`,
  `cuenta_al_entrar/salir`, `registro_deepseek`, `sin red(?![a-z])`) a los de **deuda**.
  **Totales: 51 celdas que casan — 24 con sello, 27 sin sello.** La cuenta sube porque una fila de tabla son
  varias celdas: **la unidad de B y de C no es comparable y se declara tal cual**.

Patrones de deuda (12): `B2-1(?![\w-])`, `viva al medir`, `ningún instrumento`, `cuenta publicada`,
`consumo\.json`, `tokens_out_max`, `(?<!\d)145(?!\d)`, `(?<!\d)158(?!\d)`, `cost_calculated`, `cost_billed`,
`dos brazos`, `solo la primera pata`. Patrones de cuenta (7): los de arriba en §1. Ningún barrido con tope de
salida; los ceros se declaran con su patrón.

Archivos barridos: los 12 `.md` del plan archive, `CHANGELOG.md`, `docs/contributing/REGISTRY.md`,
`.opencode/LECCIONES-INDEX.md` y `.opencode/lecciones_index.json`. Excluidos por mandato: `evidence/**`,
`scripts/**`, `tests/**`, `Archives/Historico/` y los briefing del hermano (que sí contienen `5249aed`).

## 2. Clasificación por asunto

| categoría | celdas/líneas | cuáles |
|---|---|---|
| **VENCIDA POR ESTA FIRMA** | 4 | `10-analisis:237` y `:238` (las dos filas de la tabla de seguimientos, redactadas en presente: «no compara… ni publica», «no lo publica ningún instrumento», y la 238 fija el exceso en UN brazo). `CHANGELOG.md:764` y `:765` — una sola viñeta cortada por salto de línea, que dice «el informe no publica contabilidad de coste ni veredicto de exceso» con el 145 solo. |
| **VENCIDA POR EL HECHO QUE LA FIRMA DECLARA, PERO PREEXISTENTE** | 2 | `09-documentacion-post-proyecto.md:31` y `:32`, **celda de la columna C** (las dos leen `PENDIENTE`). Medido contra los artefactos versionados de FASE-C: `ledger.jsonl` tiene 2 filas jev (1 `EJERCITADO` + 1 `FALLO`, 2 attempts) y `ledger-deepseek.jsonl` 2 filas `EJERCITADO`; el `registro_deepseek.json` entra con 2 llamadas y sale con **4**. O sea C **sí** envió en los dos brazos. La celda está vencida **desde el cierre de C (2026-10-04)**, no desde hoy: la firma solo la hace visible. §4 explica por qué la pasada B no la encontró. |
| **HISTÓRICA CON SELLO PROPIO** | 24 celdas / 20 líneas | las tres de `06-checklist` (:12, :16, :27, sellos 2026-10-04 y 2026-10-05), la celda RELEASE de `09-documentacion:35` (cabecera de columna `RELEASE (2026-10-05)` y `⟦Sello 2026-10-04⟧` en la celda de al lado), `README:25`, `10-analisis:266` y el cuerpo de la anotación nueva (`:283-334`) |
| **CITA DE SHA PUBLICADO** | 2 | `10-analisis:289` (`ec69570`) y `:290` (`5249aed..fb13108`), ambas dentro de la anotación: son referencia a lo ya empujado, no estado del instrumento |
| **OTRO ASUNTO** | el resto | `01-plan-maestro:41` (enunciado de AC8), `:110`/`:111` (definiciones de `cost_calculated`/`cost_billed` del contrato), `:172` (interfaces previstas), `04-contrato-ejecucion:18`, `05-prompt-…-B:25` y `…-C:25` (tareas de fase), `…-C:9` («no presentar dos brazos como comparación completa», otro sentido), `…-C:31` (lista de artefactos previstos), `06-checklist:17` («SDK real sin red», contrato de AC9), `README:23`/`:55`, `10-analisis:30`, y las cuatro apariciones de `sin red` en CHANGELOG (`:845`, `:847` y otras dos) que el patrón de cuenta caza y no significan nada de esta familia |

## 3. Las 9 líneas sin sello según la pasada B, y su lectura

| archivo:línea | de qué habla | veredicto |
|---|---|---|
| `01-plan-maestro.md:41` | enunciado de AC8 (presupuesto finito, reserva antes de cada intento) | OTRO ASUNTO — define el criterio, no afirma deuda |
| `01-plan-maestro.md:110` / `:111` | definiciones contractuales de `cost_calculated` y `cost_billed` | OTRO ASUNTO — hoy el informe las publica, pero la línea no dice que falten |
| `05-prompt-…-fase-C.md:9` | «no sustituirlo ni presentar dos brazos como comparación completa» | OTRO ASUNTO — «dos brazos» ahí es otra cosa |
| `05-prompt-…-fase-C.md:31` | lista de artefactos previstos, con `consumo.json` | OTRO ASUNTO |
| `10-analisis:237` / `:238` | las dos filas de la tabla de seguimientos | **VENCIDA POR ESTA FIRMA** (redacción en presente y exceso en un brazo); se conservan: convención de anotar sin reescribir. Tienen sello **de sección** — caen bajo `## Cierre FASE-RELEASE (2026-10-05)` (línea 188) — y la regla de `⟦…⟧` no ve los sellos de sección |
| `CHANGELOG.md:764` / `:765` | «Deuda visible re-medida, no absorbida: B2-1 y B2-1c…» | **VENCIDA POR ESTA FIRMA**, mismo caso: sello de sección (`## [Sin publicar] - … 2026-10-05`, línea 724) y redacción en presente |

## 4. El hallazgo metodológico del censo: dos unidades de barrido, dos ciegas

La pasada B buscaba **deuda** (`B2-1…`, `consumo.json`, `145/158`) a nivel de **línea**. Con eso:

- **No veía la columna C** de `09-documentacion`: su contenido literal es `PENDIENTE`, una palabra que no está
  en ningún patrón de deuda. La encontró la pasada A leyendo la fila completa y la cerró la pasada C midiendo la
  **celda** contra los ledger.
- **Marcaría como «sin sello» una celda vencida y como «con sello» la vecina de la misma fila**: la línea 31
  tiene `⟦Sello 2026-10-04⟧` en la celda de la columna B y `PENDIENTE` sin sello en la de la columna C. A nivel
  de línea, el sello de B contamina el juicio de C. Eso es exactamente lo que la regla nueva dice: **en una
  tabla el sello es de celda, no de línea**.
- Y los **sellos de sección** (`## … (2026-10-05)`) son invisibles para un rastreo de `⟦⟧`: las cuatro filas
  vencidas (`10-analisis:237/238`, `CHANGELOG:764/765`) están bajo cabecera fechada.

Consecuencia para la casa: un censo hecho con patrones de síntoma sobre líneas no cuenta las celdas de cuenta.
Es `L-JEV.C1` vista desde el otro lado (la deuda se ramifica por quién produce cada número) y se anota en el
crudo `14-` como límite del instrumento, no como defecto del plan.

## 5. Segunda pasada sobre los índices (el «su índice» del mandato)

| índice | líneas que mencionan el plan | líneas con una deuda B2-1* o sus cifras |
|---|---|---|
| `.opencode/LECCIONES-INDEX.md` | 14 (71, 87, 110-116, 149, 169, 174, 183, 202, 262, 444, 470) | 0 |
| `.opencode/lecciones_index.json` | 17 (645, 1796, 2034, 2372-2461…) | 0 |
| `docs/contributing/REGISTRY.md` | 5 filas de fase (11696, 11713, 11745, 11763, 11781) + la entrada de hoy (12078) | 0 |

Los índices no afirman nada sobre la familia B2-1 ni sobre el exceso: son contadores de citas que produce el
escritor. Si el estampado movió alguno, lo decide `build_lesson_index.py --check`, no la lectura — medido antes
y después del estampado: **fresco, 365 IDs, EXIT 0** en las dos medias; regenerado luego a 368 por las
lecciones nuevas (§5 de `14-`).

Archivos con **cero** coincidencias de deuda, por barrido completo y sin tope: `00-lecciones-capitalizadas.md`,
`04-contrato-ejecucion.md`, `05-prompt-…-A.md`, `05-prompt-…-B.md`, `05-prompt-…-RELEASE.md`,
`dependencias-fases.md`, `REGISTRY.md`, `LECCIONES-INDEX.md`.

## 6. Qué queda vencido y sin curar, con dueño

- **`09-documentacion-post-proyecto.md:31` y `:32`, celda de la columna C (`PENDIENTE`).** La cura real es
  escribir en esa celda lo que miden los ledger (jev: 1 ejercitado + 1 fallo, 2 attempts; deepseek: 2
  ejercitados; cuenta al salir 4 y `tokens_out_max` 158), con su sello datado. **No se hizo aquí**: el mandato
  estampa el `10-analisis`, no el `09`, y editar otro documento del plan habría abierto otro ciclo de
  frescura. Dueño: quien reabra el `09` con el cierre de la corrida nueva. Es además un caso exacto de
  `L-JEV.R1` (una fase que muta un artefacto sin escribir las filas que lo declaran): la columna C quedó
  `PENDIENTE` cuando C ya había enviado.
- **`CHANGELOG.md:764-765`**: vencido y sin tocar; mover el CHANGELOG es asunto de versión y del pre-commit
  `version-sync`. Dueño: quien cierre el próximo release.
- **Las filas `B2-2`, `B2-3`, `B2-5` y `REL-1…REL-5`** de la misma tabla siguen abiertas: se listan para que
  nadie lea «familia B2-1 cerrada» como «deuda del plan cerrada`.
- `B2-4` no la vence esta firma: es el `NO-EVALUABLE` por descarga fallida, ya curado el 2026-10-05.

## 7. NO-EVALUABLE del censo

- Celdas de `06-checklist` y `09-documentacion` de miles de caracteres: se clasificó por el fragmento con la
  afirmación, no por la celda completa.
- La existencia de `contabilidad_de_coste()` / `registrar_envio_en_cuenta()` en el árbol no la verificó el
  censo (barrido restringido a documentación): la verificaron las baterías de `10-`.
- El contenido de `.opencode/qmind-writeback/registro.json` y de las instantáneas no entró en el censo: su
  evidencia vive en `13-`.
- Los conteos de citas del índice (líneas 71, 87, 149, 169, 444, 470…) no son afirmaciones de estado y no se
  recatalogaron.
