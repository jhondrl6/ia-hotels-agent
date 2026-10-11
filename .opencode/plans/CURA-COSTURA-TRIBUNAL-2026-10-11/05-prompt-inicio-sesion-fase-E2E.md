# FASE-E2E — Run único de v4complete para Hotel Don Alfonso + análisis post-implementación

**ID**: FASE-E2E (plan CURA-COSTURA-TRIBUNAL-2026-10-11)
**Objetivo**: ejecutar **la única corrida de `v4complete` autorizada en todo el plan** para Hotel Don Alfonso (`https://www.donalfonsohotel.com/`, decisión del operador 2026-10-11) con los datos Tier A del warehouse inyectados **por el YAML derivado** (DEC-A4: `observations.json` no se edita), preservar la evidencia proactiva y verificar el output contra AC14, alimentando el análisis post-implementación con lecciones aprendidas.
**Dependencias**: FASE-A ✅, FASE-B ✅, FASE-C ✅ (el run valida la costura curada).
**Duración estimada**: 1 sesión (el run vive en un subagente con timeout 900 s).
**Complejidad**: MEDIA — orquestación y verificación; cero código nuevo.
**Skill**: `.agents/workflows/phased_project_executor.md` (workflow canónico).

## Contexto

Este run es la línea base real sobre la que FASE-VERIFY certifica AC1..18: es el primer output E2E con el contrato de cuatro estados, el recibo y los revisores curados. El onboarding casa **solo por URL normalizada** (`_load_latest_onboarding_data` + `_normalize_url`), y el loader mira **primero** `clientes_dir = Path(args.output)/"clientes"` (con fallback `output/clientes`) y **solo después** cae al warehouse. Por eso el dato entra por el **YAML derivado** (DEC-A4) y no por edición del warehouse: editar `website` era innecesario y falsificaba la procedencia. Medido dos veces más: el registro del warehouse trae `website: https://hoteldonalfonso.com/` — **distinto** de la URL viva del run, así que la rama warehouse no puede casar con esta URL — y el transformador descarta `adr_cop` y `occupancy_rate` porque `_FIELD_MAP` no los propaga. La lección L-VUP-13 («Using defaults (no fresh onboarding data found)») y el precedente de la corrida FASE-E de COHERENCIA-MODULO-ENTREGA (2 runs: 1 sin onboarding por path del loader) mandan la sonda pre-vuelo.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| Preparación | ✅ Completada |
| FASE-A / FASE-B / FASE-C | ✅ Completadas |

### Base Técnica Disponible

- Comando: `./venv/Scripts/python.exe main.py v4complete --url <URL>` (con `PYTHONUTF8=1`; `--force-new` para garantizar inyección fresca de onboarding).
- Inyección de onboarding: `_load_latest_onboarding_data(hotel_url, hotel_name, output_dir=None)` — recorre `*_onboarding.yaml` de `clientes_dir` casando por `_normalize_url`, **descarta** entradas viejas si `ONBOARDING_FRESHNESS_HOURS` está seteada, y solo después cae al warehouse (`data/hotel_observations/observations.json`), donde tampoco casa: su `website` para Don Alfonso es `https://hoteldonalfonso.com/`.
- Productor del derivado (reutilizable): `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/derivar_onboarding.py` — escribe el YAML y `onboarding_provenance.json`, con `--raiz` para no tocar el árbol de la corrida. Su salida vigente del 2026-10-06 vive en `output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/clientes/hotel_don_alfonso_onboarding.yaml` (`url: https://www.donalfonsohotel.com/`, `fecha_captura: 2026-07-22`).
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
- [ ] (a) **Derivar el onboarding**, no editar el warehouse: producir el YAML con el writer versionado `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/derivar_onboarding.py` (usa el transformador real del repo, selecciona por `hotel_name`, cambia **una sola** clave — `hotel.url` a la URL canónica — y declara `campos_no_transportados`: `adr_cop` y `occupancy_rate` no los propaga `_FIELD_MAP`). Colocar el resultado en el `clientes_dir` **real** del run: `Path(args.output)/"clientes"` con fallback `output/clientes` — **leer el default de `--output` del argparse antes de escribir, no suponerlo** (default medido `./output`, así que el directorio efectivo es `output/clientes`); si el run se invoca con un `--output` distinto, derivar también a `<args.output>/clientes/`. Copiar el YAML y su `onboarding_provenance.json` a `evidence/.../FASE-E2E/`.
- [ ] (b) **Sonda read-only del loader**: `_load_latest_onboarding_data("https://www.donalfonsohotel.com/", "Hotel Don Alfonso", output_dir=<el clientes_dir real>)` y publicar en `pre-vuelo.md` el **conteo de `campos_confirmados` y los campos** (medido en el transformador: 4 — habitaciones, reservas_mes, valor_reserva_cop, canal_directo_pct; `adr_cop` y `occupancy_rate` salen `no_disponible`, nunca estimados). Si devuelve `None`, **DETENER y consultar** con la evidencia de la sonda. Declarar en el mismo archivo el estado de `ONBOARDING_FRESHNESS_HOURS`: medido, el loader **descarta** un YAML cuyo `fecha_captura` (2026-07-22) cae fuera del límite cuando la variable está seteada, y el fallback del warehouse **no casa** con la URL del run (allí `website` es `https://hoteldonalfonso.com/`) — o sea, con la variable puesta el run entra en «Using defaults» sin que nada lo avise.
- [ ] (c) **Preflight del único intento**: correr `run_once.preflight()` de `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/run_once.py` y publicar su salida en `pre-vuelo.md` — `spawn_autorizado`, los requisitos por nombre con su causa, el bloque `iah-consentimiento` (contrato de 6 campos: `url_amparada`, `fecha_captura_aceptada`, `limite_de_frescura_dias`, `autoriza`, `declarado_por`, `fecha`) **datado por el operador sobre la URL viva**, y la edad del dato contra su emisión (techo del arnés: `EDAD_MAXIMA_DIAS = 90` sobre el dato de 2026-07-22; medido el 2026-10-11: **81 días**, así que el techo se cumple el **2026-10-20** — si esta fase corre después de esa fecha, el requisito sale NO-FAVORABLE y se para y consulta, nunca se re-fecha el dato a mano). El arnés está anclado a las rutas del plan REFACTOR-WHATSAPP (`DIR_FASE`, `consentimiento-corrida.md`, `evidence/.../FASE-F/credential_status.json`): reutilizarlo exige o correrlo con `--raiz` sobre un árbol que traiga esos artefactos, o reproducir sus requisitos con los de **esta** fase y declararlo. Si ninguna de las dos sale, el pre-vuelo se publica **NO-FAVORABLE** y la fase se detiene — el run no se gasta.
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
- [ ] Si un elemento falta, se registra como hallazgo con causa en el acta de la fase — no se «arregla» corriendo otra vez (el run es único).

### Tarea 3 — Documentación y análisis post-implementación con lecciones aprendidas

**Archivos afectados**:
- `09-documentacion-post-proyecto.md` (§D: métricas del run — aquí vive el número)
- `10-analisis-post-implementacion.md` (Resumen de Ejecución; **Matriz de Verificación de Hallazgos**: defectos 1-6 + N1-N9 con Expected/Real/Status leídos del output real; **Lecciones Aprendidas** del run, formato qué pasó/por qué/qué lo previene + pertinencia; Seguimientos)
- `00-lecciones-capitalizadas.md` §2 y `dependencias-fases.md`

**Criterios de aceptación**:
- [ ] Métricas del run (coherence, duration, tokens si el recibo las trae) registradas UNA vez en `09` §D y referenciadas.
- [ ] Lecciones del run escritas en `10-analisis` (puede declararse «sin lecciones nuevas» sin cuota).
- [ ] Registro de fase — **esta fase no modifica ningún archivo versionado**: el YAML derivado vive bajo `output/`, que `.gitignore` excluye con la regla `output/*/`, y el warehouse queda intacto (sha256 igual antes y después). Se registran como nuevos los artefactos de evidencia:
  ```bash
  ./venv/Scripts/python.exe scripts/log_phase_completion.py \
      --fase FASE-E2E --fecha <FECHA_DE_CIERRE_DE_ESTA_FASE> \
      --desc "Run unico v4complete Don Alfonso post-cura; onboarding por YAML derivado; evidencia y verificacion AC14" \
      --archivos-nuevos "evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/pre-vuelo.md" \
      --tests "0" --check-manual-docs --force-skip-docs --skip-reason "no-aplica: fase de ejecucion sin cambios de codigo"
  ```
- [ ] Pregunta de aporte durable de cualquier `CONTEXT-*.md` escrito en la sesión.

## Tests Obligatorios

Sin código nuevo → sin tests unitarios nuevos. La «prueba» de esta fase es AC14 leído en los artefactos de la corrida, y los pares de evidencia en `evidence/.../FASE-E2E/`.

**Comando de validación**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Criterios de Completitud (CHECKLIST)

⚠️ Ver template §6. Resumen:

- [ ] Pre-vuelo completo: YAML derivado en el `clientes_dir` real, sonda con su conteo de `campos_confirmados` y el estado de `ONBOARDING_FRESHNESS_HOURS`, `run_once.preflight()` publicado con `spawn_autorizado`, sha256 del warehouse **igual** antes y después, credencial por nombre de variable y dominio respondiendo (o consulta al operador documentada)
- [ ] Run único ejecutado vía subagente con timeout 900 y notify_on_complete
- [ ] Evidencia proactiva guardada ANTES de la verificación
- [ ] AC14 leído en gate report + acta + recibo + stdout (no inferido)
- [ ] `09` §D con las métricas del run; `10-analisis` con matriz y lecciones
- [ ] `--quick` verde; `log_phase_completion.py` ejecutado; cinco cortes declarados; sin commit

## Restricciones

- **Presupuesto (R2.1)**: ~35 tool calls del parent (el run vive en el subagente y no cuenta contra este presupuesto declarado — se declara así porque es de pared, no de iteraciones); corte: hasta listo para revisión.
- **UNA corrida de v4complete en todo el plan** (mandato del operador). Prohibido ejecutar v4complete desde el parent sin subagente y sin notify_on_complete.
- **No modificar código** en esta fase, y **no tocar `data/hotel_observations/observations.json`** (DEC-A4: fuente inmutable, con su sha256 antes y después publicado en `pre-vuelo.md`). Lo que se escribe es el YAML derivado bajo `output/…/clientes/` (no versionado) y la evidencia de la fase.
- No imprimir valores de credenciales (solo presencia por nombre de variable).
- Cualquier bloqueo de clasificador o de permisos durante el run se documenta en el acta de la fase; no se «resuelve» cambiando el alcance.

## Prompt de Ejecución

```
Actúa como agente orquestador de la fase E2E del plan CURA-COSTURA-TRIBUNAL-2026-10-11.

Ejecuta únicamente FASE-E2E del plan .opencode/plans/CURA-COSTURA-TRIBUNAL-2026-10-11/
Lee 01-plan-maestro.md (§1 ACs y §4 restricciones), 00-lecciones-capitalizadas.md (§2 y §4), dependencias-fases.md (conflictos y riesgos) y el workflow canónico.

OBJETIVO: Una única corrida de v4complete para Hotel Don Alfonso (https://www.donalfonsohotel.com/) con onboarding Tier A inyectado por el YAML derivado (el warehouse de observaciones no se toca); evidencia preservada; verificación de AC14 leyendo artefactos, incluido el estado de la extracción del recibo; análisis post-implementación con lecciones aprendidas en 10-analisis.

CONTEXTO:
- Fases previas completadas: Preparación, FASE-A, FASE-B, FASE-C
- El run vive en un subagente (delegate_task, timeout=900, notify_on_complete=True, toolsets terminal)
- El run es ÚNICO: una segunda corrida requiere consulta al operador

TAREAS:
1. T0 Pre-vuelo: derivar el YAML de onboarding (productor: evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/derivar_onboarding.py) en el clientes_dir real del run; sonda read-only del loader con su conteo de campos_confirmados; run_once.preflight() publicado; credencial por nombre de variable; dominio responde. sha256 de observations.json antes y despues: debe ser el mismo
2. T1 Run único vía subagente con el comando exacto (PYTHONUTF8=1, --force-new)
3. T2 Evidencia proactiva ANTES de verificar; AC14 leído en artefactos
4. T3 Docs: 09 §D, 10-analisis (matriz + lecciones), log_phase_completion

CRITERIOS:
- AC14 legible en gate report + acta + recibos + stdout; run único respetado; evidencia en evidence/.../FASE-E2E/

VALIDACIONES:
- run_all_validations.py --quick
- log_phase_completion.py --fase FASE-E2E --fecha <fecha de cierre>
```
