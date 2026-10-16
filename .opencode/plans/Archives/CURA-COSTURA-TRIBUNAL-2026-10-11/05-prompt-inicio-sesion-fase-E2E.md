# FASE-E2E — Run único de v4complete para Hotel Don Alfonso + análisis post-implementación

**ID**: FASE-E2E (plan CURA-COSTURA-TRIBUNAL-2026-10-11)
**Objetivo**: ejecutar **la única corrida de `v4complete` autorizada en todo el plan** para Hotel Don Alfonso (`https://www.donalfonsohotel.com/`, decisión del operador 2026-10-11) con los datos Tier A del warehouse inyectados **por el YAML derivado** (DEC-A4: `observations.json` no se edita), preservar la evidencia proactiva y verificar el output contra AC14, alimentando el análisis post-implementación con lecciones aprendidas.
**Dependencias**: FASE-A ✅, FASE-B ✅, FASE-C ✅, **FASE-C2 ✅ (2026-10-12, publicada en `fa4c93e` + sello `c787422`, empujada con paridad `0 0`)** — el run valida la costura curada **incluida AC19**: bajo extracción no-OK un CRITICAL del escaneo determinista también suprime el ZIP y su acción correctiva nombra el hallazgo.
**Duración estimada**: 1 sesión (el run vive en un subagente con timeout 900 s).
**Complejidad**: MEDIA — orquestación y verificación; cero código nuevo.
**Skill**: `.agents/workflows/phased_project_executor.md` (workflow canónico).

## Contexto

Este run es la línea base real sobre la que FASE-VERIFY certifica AC1..18: es el primer output E2E con el contrato de cuatro estados, el recibo y los revisores curados. El onboarding casa **solo por URL normalizada** (`_load_latest_onboarding_data` + `_normalize_url`), y el loader mira **primero** `clientes_dir = Path(args.output)/"clientes"` (con fallback `output/clientes`) y **solo después** cae al warehouse. Por eso el dato entra por el **YAML derivado** (DEC-A4) y no por edición del warehouse: editar `website` era innecesario y falsificaba la procedencia. Medido dos veces más: el registro del warehouse trae `website: https://hoteldonalfonso.com/` — **distinto** de la URL viva del run, así que la rama warehouse no puede casar con esta URL — y el transformador descarta `adr_cop` y `occupancy_rate` porque `_FIELD_MAP` no los propaga. La lección L-VUP-13 («Using defaults (no fresh onboarding data found)») y el precedente de la corrida FASE-E de COHERENCIA-MODULO-ENTREGA (2 runs: 1 sin onboarding por path del loader) mandan la sonda pre-vuelo.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| Preparación | ✅ Completada |
| FASE-A / FASE-B / FASE-C | ✅ Completadas y publicadas |
| FASE-C2 | ✅ Completada y publicada el 2026-10-12 (`fa4c93e` + sello `c787422`): AC19 — la fila 2 de la matriz §2.1 ya no exige `status.is_ok` |

### Base Técnica Disponible

- Comando: `./venv/Scripts/python.exe main.py v4complete --url <URL>` (con `PYTHONUTF8=1`; `--force-new` para garantizar inyección fresca de onboarding).
- Inyección de onboarding: `_load_latest_onboarding_data(hotel_url, hotel_name, output_dir=None)` — recorre `*_onboarding.yaml` de `clientes_dir` casando por `_normalize_url`, **descarta** entradas viejas si `ONBOARDING_FRESHNESS_HOURS` está seteada, y solo después cae al warehouse (`data/hotel_observations/observations.json`), donde tampoco casa: su `website` para Don Alfonso es `https://hoteldonalfonso.com/`.
- Productor del derivado (reutilizable): `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/derivar_onboarding.py` — escribe el YAML y `onboarding_provenance.json`. **Ojo medido el 2026-10-12: el destino está hardcodeado al plan ajeno.** El productor escribe en `<raiz>/output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/clientes/…` y su procedencia en `<raiz>/evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/onboarding_provenance.json` — por las constantes de módulo `PLAN`, `dir_clientes` y `destino` de `derivar_onboarding.py`; `--raiz` cambia la raíz pero **no** el componente de plan, así que **nunca** deposita el YAML en `output/clientes/`, que es el `clientes_dir` que lee una corrida con el `--output` por defecto. Si se invoca el run sin `--output`, el loader mira `output/clientes/` (hoy solo contiene `zi-one-luxury_onboarding.yaml`) y cae al warehouse, que no casa: **T0(a) tiene que colocar el YAML en el `clientes_dir` real y la sonda de T0(b) correr contra ese directorio**, no contra el de REFACTOR.
  Su salida vigente (re-derivada el 2026-10-12 por accidente de esta consulta y medida **byte-idéntica**: sha256 `9e5c5f29f6acce9d` en disco == el blob en HEAD) vive en `output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/clientes/hotel_don_alfonso_onboarding.yaml` (`url: https://www.donalfonsohotel.com/`, `fecha_captura: 2026-07-22`, `campos_confirmados` = 4). El productor **no tiene `--help`**: se ejecuta con cualquier argumento, así que llamarlo «para leer sus banderas» escribe; invoke it solo como paso real de T0(a).
- Control de la fuente inmutable: sha256 de `data/hotel_observations/observations.json` antes y después, publicado en `pre-vuelo.md`. El precedente de tests es `tests/test_fase_h_onboarding_procedencia.py` (rama favorable declarada `YAML_DE_DIR_CLIENTES`; `OBSERVATIONS_DENTRO_DE_LA_FUNCION` y las demás ramas del loader declaradas **silenciosas**, no favorables).
- Preflight reutilizable: `run_once.preflight()` del mismo FASE-H (12 requisitos por nombre, `spawn_autorizado`, bloque `iah-consentimiento`, edad contra la emisión con techo de 90 días).
- Valores esperados del derivado: Hotel Don Alfonso, 11 habitaciones, 140 reservas/mes, valor reserva $330.000 COP, 30% canal directo, `boutique_10_25`, eje_cafetero, Tier A confidence 0.95, `source: contacto_directo`, `epistemic_status: verified`. `adr_cop` y `occupancy_rate` **no** viajan: se declaran `no_disponible` (nunca se estiman).
- Salida esperada: `output/v4_complete/` (diagnóstico, propuesta, assets, gate report con coherence, acta del tribunal en `v4_audit/`, ZIP con cuarentena O1).

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-VUP-13 | «Using defaults» confirmado empíricamente en el log | T0: derivar el YAML de onboarding (DEC-A4, el warehouse no se toca) y sonda read-only del loader ANTES del run, publicando `campos_confirmados` y el estado de `ONBOARDING_FRESHNESS_HOURS`; AC14 exige «Onboarding data loaded» en el stdout; decisión del operador 2026-10-11: URL canónica `https://www.donalfonsohotel.com/` — la diferencia con el `website` del warehouse se resuelve por el derivado, no por el warehouse |
| L-T4A.3 | Cache de producción `.cache/tribunal/` es decisión declarada | T3: los recibos de la corrida viven bajo el `cache_dir` de producción; se copian a evidence como artefacto, no se borra la cache |
| L-V.2 | Re-leer artefactos, no heredar conclusiones | T3: la verificación lee gate report/acta/recibos reales de ESTA corrida |

## Tareas (R3: 3 tareas + 1 comando largo)

### Tarea 0 — Pre-vuelo (sin gastar el run)

**Archivos afectados**:
- `output/clientes/hotel_don_alfonso_onboarding.yaml` (derivado; `output/*/` está en `.gitignore`, así que **no es un archivo versionado** — su copia va a `evidence/.../FASE-E2E/` como procedencia)
- `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/pre-vuelo.md`

**Invariante**: `data/hotel_observations/observations.json` **NO se toca** (DEC-A4 del maestro). Su sha256 **antes y después** se publica en `pre-vuelo.md` y tiene que casar; `tests/test_fase_h_onboarding_procedencia.py` ya declara esa fuente como inmutable y su test `test_la_fuente_inmutable_sale_igual_antes_y_despues_de_derivar` es el precedente del control.

**Criterios de aceptación**:
- [ ] (a) **Derivar el onboarding**, no editar el warehouse: producir el YAML con el writer versionado `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/derivar_onboarding.py` (usa el transformador real del repo, selecciona por `hotel_name`, cambia **una sola** clave — `hotel.url` a la URL canónica — y declara `campos_no_transportados`: `adr_cop` y `occupancy_rate` no los propaga `_FIELD_MAP`). Colocar el resultado en el `clientes_dir` **real** del run: `Path(args.output)/"clientes"` con fallback `output/clientes` — **leer el default de `--output` del argparse antes de escribir, no suponerlo** (default medido `./output`, así que el directorio efectivo es `output/clientes`); si el run se invoca con un `--output` distinto, derivar también a `<args.output>/clientes/`. **Como el productor no escribe ahí (ver Base Técnica), el paso es: correr el productor → copiar el YAML y su `onboarding_provenance.json` al `clientes_dir` efectivo → publicar el sha256 de la copia** para que «el archivo que ve el loader» sea verificable y no una suposición. Copiar el YAML y su `onboarding_provenance.json` a `evidence/.../FASE-E2E/`.
- [ ] (b) **Sonda read-only del loader**: `_load_latest_onboarding_data("https://www.donalfonsohotel.com/", "Hotel Don Alfonso", output_dir=<el clientes_dir real>)` y publicar en `pre-vuelo.md` el **conteo de `campos_confirmados` y los campos** (medido en el transformador: 4 — habitaciones, reservas_mes, valor_reserva_cop, canal_directo_pct; `adr_cop` y `occupancy_rate` salen `no_disponible`, nunca estimados). Si devuelve `None`, **DETENER y consultar** con la evidencia de la sonda. Declarar en el mismo archivo el estado de `ONBOARDING_FRESHNESS_HOURS`: medido, el loader **descarta** un YAML cuyo `fecha_captura` (2026-07-22) cae fuera del límite cuando la variable está seteada, y el fallback del warehouse **no casa** con la URL del run (allí `website` es `https://hoteldonalfonso.com/`) — o sea, con la variable puesta el run entra en «Using defaults» sin que nada lo avise.
- [ ] (c) **Preflight del único intento**: correr `run_once.preflight()` de `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/run_once.py` y publicar su salida en `pre-vuelo.md` — `spawn_autorizado`, los requisitos por nombre con su causa, el bloque `iah-consentimiento` (contrato de 6 campos: `url_amparada`, `fecha_captura_aceptada`, `limite_de_frescura_dias`, `autoriza`, `declarado_por`, `fecha`) **datado por el operador sobre la URL viva**, y la edad del dato contra su emisión (techo del arnés: `EDAD_MAXIMA_DIAS = 90` sobre el dato de 2026-07-22; medido el 2026-10-12: **82 días**, así que el techo se cumple el **2026-10-20** — si esta fase corre después de esa fecha, el requisito sale NO-FAVORABLE y se para y consulta, nunca se re-fecha el dato a mano).

  **Decisión del Operador (2026-10-12): el arnés NO se reutiliza tal cual — opción A.** Medido ese día corriendo `preflight()` en modo lectura sobre el árbol actual: `spawn_autorizado: False`, **11 de 12 requisitos favorables**, y el único no favorable es `control_productivo_intacto`, que falla **por el run de otro plan** (existe `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E2E/run_control.json` del 2026-10-07, aquel plan ya gastó su corrida única en `b05e620`). Las constantes del arnés son de módulo (`RAIZ`, `PLAN`, `DIR_FASE` y `DIR_EVIDENCIA_PRODUCTIVA` en `run_once.py`) y ese chequeo **no** es `--raiz`-aware, así que «correrlo apuntando a CURA» no lo arregla.

  La vía ejecutada es un **arnés desechable por stdin** (sin `.py` versionado, precedente: la medición de AC10 en FASE-B) que:
  1. **importa** `run_once` y reutiliza sus predicados puros — `leer_consentimiento`/`evaluar_consentimiento` (pasando `ruta=` al consentimiento de esta fase), `EDAD_MAXIMA_DIAS`, y los **12 nombres** de requisito, para que el vocabulario siga siendo comparable con el de REFACTOR;
  2. **re-mide los cuatro insumos que hoy vienen del árbol de H** y que estarían vencidos: la procedencia del derivado (productor re-corrido en esta fase), la rama efectiva del loader **sobre el `clientes_dir` efectivo de esta corrida** (T0 b), `edad_dias` recalculado contra la fecha del run, y `identidades`/`argv` del comando de **esta** fase;
  3. ancla `control_productivo_intacto` a `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/run_control.json` (ausente hoy → favorable), que es lo que el arnés de REFACTOR no puede comprobar;
  4. publica en `pre-vuelo.md` una **columna de procedencia por requisito** («predicado de `run_once.preflight()`» vs «medición propia de FASE-E2E») y deja el JSON del preflight en `evidence/…/FASE-E2E/`.

  **Alternativas y su estado:** (B) versionar un `preflight_cura.py` bajo `evidence/` queda como **respaldo** si se quiere un instrumento re-ejecutable en otra sesión — su coste declarado es +1 archivo en alcance (724→725) y republicar `wiring_report.json` en el mismo commit, más la divergencia de ~200 líneas de lógica duplicada. (C) «excepción documentada corriendo el arnés tal cual» se **rechaza con motivo**: publicaría 11 requisitos certificados sobre artefactos de H del 2026-10-06/07, es decir un verde prestado, en contradicción directa con L-V.2 («las notas de fases upstream pueden ser inexactas; VERIFY debe re-leer los artefactos»), que este prompt ya declara aplicable.

  **Consentimiento (pendiente del Operador, dueño nombrado):** medido el 2026-10-12, el requisito `consentimiento_datado_sobre_la_url_viva` **sale favorable** con el bloque vigente (`evidence/REFACTOR-…/FASE-H/consentimiento-corrida.md`: ampara `https://www.donalfonsohotel.com/`, `fecha_captura_aceptada: 2026-07-22`, límite 90, `autoriza` contiene «entrega», `fecha: 2026-10-07` ≥ captura), porque el predicado no mira qué plan corrió. Ese bloque autoriza **la corrida de REFACTOR**, así que la vía limpia es un bloque propio de CURA en `evidence/…/FASE-E2E/consentimiento-corrida.md`, fechado por el operador (un acto suyo: `declarado_por` y `fecha` no los escribe el agente). El arnés por stdin le pasa `ruta=`, así que ninguna de las dos opciones exige editar el archivo ajeno. Sin bloque datado ni decisión escrita del Operador, T0 sale **NO-FAVORABLE** y el run no se gasta.
- [ ] (d) **Credencial por nombre de variable** (nunca su valor): presencia de `DEEPSEEK_API_KEY` / `ANTHROPIC_API_KEY` / `LLM_PROVIDER` declarada en `pre-vuelo.md` con `grep` de nombres. Sin credencial la extracción terminará `FALLIDO` (estado honesto tras FASE-A): **detener y consultar** antes de gastar la corrida única.
- [ ] (e) **El dominio responde**: HEAD a `https://www.donalfonsohotel.com/`; si no responde, o si redirige a un dominio distinto del del YAML derivado, **detener y consultar**.

### Tarea 1 — El run (comando largo, vía subagente)

**Criterios de aceptación**:
- [ ] Spawn de subagente con `delegate_task`: goal «Ejecutar v4complete para Hotel Don Alfonso», toolsets `terminal`, `timeout=900`, `notify_on_complete=True`.
- [ ] Comando exacto en el contexto del subagente:
  ```bash
  PYTHONUTF8=1 ./venv/Scripts/python.exe main.py v4complete --url https://www.donalfonsohotel.com/ --force-new
  ```
- [ ] **El run es ÚNICO.** Si el subagente expira (timeout 900 s), re-spawn solo si la corrida previa no produjo output; un escenario que exija una SEGUNDA corrida (output válido ya generado) se consulta con el operador antes.
- [ ] El parent conserva sus iteraciones para T2/T3 (no espera bloqueado).

### Tarea 2 — Evidencia proactiva + verificación del output (AC14)

**Archivos afectados**:
- `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/`

**Criterios de aceptación**:
- [ ] **Protocolo de Evidencia Proactiva, ANTES de cualquier otra verificación**: copiar a `evidence/.../FASE-E2E/` el stdout completo, `01_DIAGNOSTICO_*.md`, `02_PROPUESTA_*.md`, los JSON de `v4_audit/` (incluidos gate report y acta del tribunal), los recibos de extracción del `cache_dir` de esta corrida, el acta escrita por `ActaWriter`, **y el YAML de onboarding derivado con su `onboarding_provenance.json`** (viven bajo `output/`, que no se versiona: la copia en `evidence/` es su única procedencia).
- [ ] Verificación contra AC14, leyendo los artefactos: «Onboarding data loaded» en stdout con los 4 campos confirmados; coherence ≥ 0.8 en el gate report; acta emitida con los 4 revisores y su report; recibo presente con proveedor servido, modelo **pedido** y modelo **firmado** (si difieren), versión de prompt y usage; **el estado de la extracción leído del recibo** (`OK_CON_PROMESAS` / `OK_SIN_PROMESAS` / `NO_EVALUABLE` / `FALLIDO`) con su motivo — si es no-OK se registra como hallazgo de la fase, y si el veredicto es `BLOQUEADO` el acta nombra el hallazgo bloqueante mientras la medición de AC10 dice si es verdadero o falso positivo; estado del ZIP (publicado o cuarentena con veredicto honesto — un `BLOQUEAR` legítimo es un resultado válido del sistema curado, no un fallo del run; se documenta).
- [ ] **Diente nuevo de AC19 (FASE-C2), leerlo en el acta y no inferirlo del veredicto**: si el estado de extracción de algún revisor es no-OK (`NO-EVALUABLE`/`FALLIDO`) y ese revisor trae `critical_count >= 1` o `recommendation: BLOQUEAR`, el acta tiene que salir `BLOQUEADO`, `blocks_delivery_zip` True y **`corrective_actions` nombrando el hallazgo** (`finding_type`, `severity`, `artifact`, `owner` de `_OWNER_BY_REVIEWER`) en lugar de `VEREDICTO_BLOQUEANTE_SIN_HALLAZGO`. Antes de FASE-C2 ese caso publicaba el ZIP; la prueba de la cura en flujo real es que aquí ya no. Se registra en la matriz de `10-analisis` con el valor leído del JSON y del MD del `ActaWriter`. **Salida esperada de este run** (precedente medido en FASE-B sobre la propuesta de Don Alfonso: dos absolutos de prosa de garantía y la celda «(Verificado)» de la tabla → CRITICAL verdaderos): `BLOQUEADO` con ZIP en cuarentena, sea cual sea el estado de la extracción.
- [ ] Si un elemento falta, se registra como hallazgo con causa en el acta de la fase — no se «arregla» corriendo otra vez (el run es único).

### Tarea 3 — Documentación y análisis post-implementación con lecciones aprendidas

**Archivos afectados**:
- `09-documentacion-post-proyecto.md` (§D: métricas del run — aquí vive el número)
- `10-analisis-post-implementacion.md` (Resumen de Ejecución; **Matriz de Verificación de Hallazgos**: defectos 1-6 + N1-N9 con Expected/Real/Status leídos del output real; **Lecciones Aprendidas** del run, formato qué pasó/por qué/qué lo previene + pertinencia; Seguimientos)
- `00-lecciones-capitalizadas.md` §2 y `dependencias-fases.md`

**Criterios de aceptación**:
- [ ] Métricas del run (coherence, duration, tokens si el recibo las trae) registradas UNA vez en `09` §D y referenciadas.
- [ ] Lecciones del run escritas en `10-analisis` (puede declararse «sin lecciones nuevas» sin cuota).
- [ ] Registro de fase — **corregido el 2026-10-12**: esta fase **sí** modifica archivos versionados, y no son de código. T3 edita cuatro documentos del plan (`09-documentacion-post-proyecto.md`, `10-analisis-post-implementacion.md`, `00-lecciones-capitalizadas.md`, `dependencias-fases.md`) y estampa `REGISTRY.md` + `.last_doc_phase.json` al registrarse; lo que **no** se toca es el warehouse (`observations.json`, sha256 igual antes y después) y el YAML derivado, que vive bajo `output/` (excluido por `.gitignore` con la regla `output/*/`) — su procedencia es la copia en `evidence/`. Por eso el comando lleva `--archivos-mod` con las cuatro rutas del plan:
  ```bash
  ./venv/Scripts/python.exe scripts/log_phase_completion.py \
      --fase FASE-E2E --fecha <FECHA_DE_CIERRE_DE_ESTA_FASE> \
      --desc "Run unico v4complete Don Alfonso post-cura; onboarding por YAML derivado; evidencia y verificacion AC14" \
      --archivos-nuevos "evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/pre-vuelo.md" \
      --archivos-mod ".opencode/plans/Archives/CURA-COSTURA-TRIBUNAL-2026-10-11/09-documentacion-post-proyecto.md,.opencode/plans/Archives/CURA-COSTURA-TRIBUNAL-2026-10-11/10-analisis-post-implementacion.md,.opencode/plans/Archives/CURA-COSTURA-TRIBUNAL-2026-10-11/00-lecciones-capitalizadas.md,.opencode/plans/Archives/CURA-COSTURA-TRIBUNAL-2026-10-11/dependencias-fases.md" \
      --tests "0" --check-manual-docs --force-skip-docs --skip-reason "no-aplica: fase de ejecucion sin cambios de codigo" \
      --plan CURA-COSTURA-TRIBUNAL-2026-10-11
  ```
  (`--force-skip-docs` sigue siendo la bandera correcta —su alcance son CHANGELOG/GUIA_TECNICA/ROADMAP/DOMAIN_PRIMER, que esta fase no toca—, pero ya no puede ir acompañada de la afirmación «no modifica ningún archivo versionado». El escritor es **aditivo**: no volver a correrlo sobre la fase ya cerrada. `--plan` solo hace falta si la cabecera `## FASE-E2E - <fecha>` ya existiera en `REGISTRY.md` por otro plan el mismo día; se declara aquí por si acaso.)
- [ ] Pregunta de aporte durable de cualquier `CONTEXT-*.md` escrito en la sesión.

## Tests Obligatorios

Sin código nuevo → sin tests unitarios nuevos. La «prueba» de esta fase es AC14 leído en los artefactos de la corrida, y los pares de evidencia en `evidence/.../FASE-E2E/`.

**Comando de validación**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Criterios de Completitud (CHECKLIST)

⚠️ Ver template §6. Resumen:

- [ ] Pre-vuelo completo: YAML derivado **colocado en el `clientes_dir` efectivo** con su sha256 publicado, sonda con su conteo de `campos_confirmados` y el estado de `ONBOARDING_FRESHNESS_HOURS`, preflight de **12 requisitos por nombre con su columna de procedencia** (opción A: predicados de `run_once` + medición propia de los cuatro insumos vencidos) y `spawn_autorizado`, sha256 del warehouse **igual** antes y después, consentimiento datado por el Operador (propio de CURA o su declaración escrita de que el vigente lo ampara), credencial por nombre de variable y dominio respondiendo (o consulta al operador documentada)
- [ ] Run único ejecutado vía subagente con timeout 900 y notify_on_complete
- [ ] Evidencia proactiva guardada ANTES de la verificación
- [ ] AC14 leído en gate report + acta + recibo + stdout (no inferido)
- [ ] `09` §D con las métricas del run; `10-analisis` con matriz y lecciones
- [ ] `--quick` verde; `log_phase_completion.py` ejecutado; cinco cortes declarados; sin commit

## Restricciones

- **Presupuesto (R2.1)**: ~35 tool calls del parent (el run vive en el subagente y no cuenta contra este presupuesto declarado — se declara así porque es de pared, no de iteraciones); corte: hasta listo para revisión. **Ajuste declarado el 2026-10-12**: la opción A del preflight añade al parent la re-medición de los cuatro insumos vencidos y su columna de procedencia (~8-12 llamadas), así que el techo realista de esta fase es **~45**, no ~35. Se recalibra **antes** de correr, no excedido el presupuesto en silencio (el patrón de FASE-A/B/C fue excederlo y declararlo después).
- **UNA corrida de v4complete en todo el plan** (mandato del operador). Prohibido ejecutar v4complete desde el parent sin subagente y sin notify_on_complete.
- **No modificar código** en esta fase, y **no tocar `data/hotel_observations/observations.json`** (DEC-A4: fuente inmutable, con su sha256 antes y después publicado en `pre-vuelo.md`). Lo que se escribe es el YAML derivado bajo `output/…/clientes/` (no versionado) y la evidencia de la fase.
- No imprimir valores de credenciales (solo presencia por nombre de variable).
- Cualquier bloqueo de clasificador o de permisos durante el run se documenta en el acta de la fase; no se «resuelve» cambiando el alcance.

## Prompt de Ejecución

```
Actúa como agente orquestador de la fase E2E del plan CURA-COSTURA-TRIBUNAL-2026-10-11.

Ejecuta únicamente FASE-E2E del plan .opencode/plans/Archives/CURA-COSTURA-TRIBUNAL-2026-10-11/
Lee 01-plan-maestro.md (§1 ACs y §4 restricciones), 00-lecciones-capitalizadas.md (§2 y §4), dependencias-fases.md (conflictos y riesgos) y el workflow canónico.

OBJETIVO: Una única corrida de v4complete para Hotel Don Alfonso (https://www.donalfonsohotel.com/) con onboarding Tier A inyectado por el YAML derivado (el warehouse de observaciones no se toca); evidencia preservada; verificación de AC14 leyendo artefactos, incluido el estado de la extracción del recibo; análisis post-implementación con lecciones aprendidas en 10-analisis.

CONTEXTO:
- Fases previas completadas y publicadas: Preparación, FASE-A, FASE-B, FASE-C y FASE-C2 (AC19, `fa4c93e`)
- El run vive en un subagente (delegate_task, timeout=900, notify_on_complete=True, toolsets terminal)
- El run es ÚNICO: una segunda corrida requiere consulta al operador
- El preflight del arnés de REFACTOR sale NO-FAVORABLE tal cual (11/12, falla control_productivo_intacto por el run de otro plan): usar la opcion A del prompt (arnes por stdin, predicados reutilizados, cuatro insumos re-medidos, procedencia por requisito). No aceptar un verde prestado de los artefactos de H

TAREAS:
1. T0 Pre-vuelo: derivar el YAML de onboarding (productor: evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/derivar_onboarding.py) y **colcarlo en el clientes_dir efectivo del run** con su sha256; sonda read-only del loader contra ese directorio con su conteo de campos_confirmados; preflight de 12 requisitos con su columna de procedencia; consentimiento datado por el operador; credencial por nombre de variable; dominio responde. sha256 de observations.json antes y despues: debe ser el mismo
2. T1 Run único vía subagente con el comando exacto (PYTHONUTF8=1, --force-new)
3. T2 Evidencia proactiva ANTES de verificar; AC14 leído en artefactos
4. T3 Docs: 09 §D, 10-analisis (matriz + lecciones), log_phase_completion

CRITERIOS:
- AC14 legible en gate report + acta + recibos + stdout; run único respetado; evidencia en evidence/.../FASE-E2E/

VALIDACIONES:
- run_all_validations.py --quick
- log_phase_completion.py --fase FASE-E2E --fecha <fecha de cierre>
```
