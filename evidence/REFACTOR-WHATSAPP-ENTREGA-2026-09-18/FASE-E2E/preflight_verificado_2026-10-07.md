# FASE-E2E — Tarea 1: preflight verificado en disco (sin spawn)

**Fecha**: 2026-10-07. **Contador v4complete**: **0/1** — ninguna corrida lanzada en esta sesión.
**Estado de la fase**: abierta, detenida antes del `--spawn` por decisión del operador.

## Hallazgo bloqueante medido y su cura

El check libre `run_once.py --preflight` (que no toca la reserva, `run_once.py:767-786`) arrojaba al abrir la sesión:

```
DivergenciaDeHash: divergencia contra el preflight en:
  evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/run_once.py
```

De los 10 archivos congelados (`run_once.py:67-78`), 9 casaban con el disco y uno no: **el propio runner**. El
preflight congeló `ff114aff36da6b59…`, que es el blob de `run_once.py` en `d571277` (b1); el commit `6fd39c2`
(b1-bis) enmendó ese mismo archivo y su blob pasó a `1efa6cd142b70e3e…`. Medido sin filtro (`core.autocrlf=input`):
sha del disco y sha del blob en HEAD coinciden en ambos casos, así que la deriva es contenido real y no artefacto
de línea.

Consecuencia determinista: `lanzar_unico` llama a `verificar_preflight` en `run_once.py:853`, **antes** de
`reservar` en `:855`, por lo que `--spawn` se habría negado sin consumir la reserva. El intento seguía intacto,
pero la fase no podía correr tal como está escrita.

**Cura aplicada (re-emisión, operación libre y ya usada por el plan):** `run_once.py --emitir-preflight`. Respondió
`intentos: 0`, `spawn_autorizado: true`, `requisitos_no_favorables: []`, EXIT 0. Antes de sobrescribir el artefacto
versionado se preservó byte a byte como `preflight_2026-10-07_emision_b1_hash_vencido.json` (precedente:
`preflight_2026-10-06_no_favorable.json`), con sha256 `a0947be1db41e5b7…` idéntico al disco y al blob de HEAD.

**Diferencia entre la emisión preservada y la re-emisión: 2 campos**, medidos campo a campo.

| Campo | Antes | Ahora |
|---|---|---|
| `emitido_el` | `2026-10-07T13:11:10.290075+00:00` | `2026-10-07T14:18:46.435390+00:00` |
| `source_hashes[…/run_once.py]` | `ff114aff36da6b59…` | `1efa6cd142b70e3e…` |

No se movieron: `argv_congelado`, `argv_sha256`, las `identidades`, el `snapshot_memoria`, los otros 9
`source_hashes`, los 12 `requisitos`, `intentos`, `spawn_autorizado` ni `pruebas_de_que_no_se_lanzo_nada`.

Tras la re-emisión: `--preflight` **EXIT 0** y las baterías de H `tests/test_fase_h_intento_unico.py` +
`tests/test_fase_h_onboarding_procedencia.py` **70 passed** (mismo verde que antes, con la misma selección).

⟦**Re-ejecutadas después del spawn: 2 failed / 68 passed.** Los dos rojos son guardas que asertaban que el control
productivo no existía (`test_fase_h_intento_unico.py::test_ningun_test_de_esta_bateria_toco_el_control_productivo` y
`test_fase_h_onboarding_procedencia.py::test_nada_de_esta_fase_creara_el_control_productivo`); el consumo legítimo del
intento venció esa premisa. ⟦**Re-ancladas el 2026-10-07 por autorización del operador:** revisión fija `6fd39c2` +
caracterización del control del runner; **70 passed de nuevo**, dientes medidos contra cinco mutantes con 5/5
atrapados. Crudos en `tests_post_reanclaje.txt` y `dientes_reanclaje_guardas.txt`; detalle en
`resultados-y-observaciones.md` §5b⟧.

## Items de la Tarea 1, verificados

| Item | Resultado | Cómo se midió |
|---|---|---|
| Cierre de H | CERRADA, conmutable y en el remoto | `master == origin/master == 6fd39c2` por `git ls-remote`; árbol de control limpio (`git status --porcelain -uno` vacío) |
| Cierre de FASE-0 con AC20 verde | **VERIFICADO OFFLINE** con par contrafactual medido | `06-checklist-implementacion.md` fila 0 y `dependencias-fases.md` (contrafactual `BLOQUEADO` → `APROBADO-CONDICIONAL-PENDING-ONBOARDING` sobre el acta archivada) |
| `run_control.json` ausente | **ABSENT** | `find` sobre el repo: 0 resultados; `FASE-E2E/` no existía antes de este archivo. La reserva vírgen sigue intacta |
| Hashes de código/runner/input conformes | 10/10 tras la re-emisión (9/10 antes) | `--preflight` y comparación directa de `source_hashes` contra `sha256` de disco |
| YAML derivado vigente | sha `2990d768f0ae75f3…` casa entre `onboarding_provenance.json`, `source_hashes` y el disco | tres lecturas cruzadas |
| Fuente inmutable | `observations.json` `31e70a37…` sin cambio | `fuente_inmutable_intacta` + sha recomputado |
| Tres identidades fijadas | `hotel_donalfonsohotel.com` / `donalfonsohotel.com` / `Hotel Don Alfonso` (más el slug `hotel_don_alfonso`) | bloque `identidades` del preflight |
| Output aislado | `output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/` solo contiene `clientes/hotel_don_alfonso_onboarding.yaml`: no hay artifacts de una corrida previa | listado del árbol |
| Entorno | `./venv/Scripts/python.exe` presente, Python 3.13.3 | verificado en disco |
| Permisos sin imprimir | `--permission-mode auto` efectivo y congelado (default del parser también `auto`); el literal incluye la bandera que el prompt citaba de más | `argv_congelado` + `permisos.modo_efectivo_del_argv_congelado` |
| Consentimiento S-H1 | vigente: edad **77** contra límite 90, emitido 2026-10-07 por `Jhond (operador)`, ventana hasta **2026-10-20** | `consentimiento-corrida.md` + `requisitos.consentimiento_datado_sobre_la_url_viva` |
| Snapshot previo de `.agent/memory` | registrado: 21 archivos, 53.734 bytes, `sha256_del_inventario d65bcf45…` | `snapshot_memoria` |
| Rama de `_load_latest_onboarding_data` | **`YAML_DE_DIR_CLIENTES`**, medida dos veces (derivación y recorrido offline) | `rama_efectiva_del_loader` + `integracion_offline.json` |
| Análisis previo reutilizable | **ENCONTRADO** para el `canonical_url`: `output/TAREA7-2026-09-19/v4_complete` | `aislamiento_de_memoria.analysis_previo` |
| Revocación de claves | **no acreditada** por evidencia operativa; se sostiene la rama "pendiente registrado" que eligió F, con dueño operador | `revocacion_de_claves` |

## Dos consecuencias declaradas que el spawn materializaría

1. **Borrado de 8 sesiones de memoria no versionadas.** `run_v4_complete_mode` pasa por
   `memory.cleanup_old_sessions(days=20)` y hoy alcanza 8 archivos. `.agent/memory/sessions/` está excluido por
   `.gitignore:38`, así que el inventario con sha256 del preflight prueba que existieron pero **no permite
   restaurarlos**. Es la deuda S-H6 que H declaró sin curar.
2. **La corrida es dependiente del análisis previo, no aislada.** El preflight exige "exclusión explícita o
   declaración" y el argv está congelado — añadir una bandera de exclusión está prohibido (L-VUP-9), así que la
   vía es **declararlo** en la evidencia. Medido por AST en H: en `run_v4_complete_mode` la variable solo se
   imprime (`consumos_que_cambian_el_flujo: []`) y la reutilización real vive en `run_execution_mode`; aun así la
   declaración se debe escribir antes del spawn (L-PF11).

## Sonda de conectividad (ejecutada antes del spawn, con autorización escrita del operador)

**La resolución DNS local del host destino es intermitente y esa es la medición que manda.** Dos tandas, ambas
contra `https://www.donalfonsohotel.com/` con `urllib` y sin credenciales:

| Tanda | Medición |
|---|---|
| Sonda previa al spawn | los dos `getaddrinfo`/`gethostbyname` fallaron con `gaierror 11001` y **al menos un fetch devolvió 200** con `final=https://donalfonsohotel.com/` y 142.017 bytes; el recuento exacto de éxitos de esa tanda no es re-verificable porque no se persistió |
| **Re-medición después de lanzar** | **0/5 fetches exitosos**, todos `gaierror 11001`, y `gethostbyname` también cae |

Lo que la sonda **sí** estableció, con host correctos y por fetch (no por DNS cruda):

| Destino | Resultado | Lectura |
|---|---|---|
| `generativelanguage.googleapis.com` | HTTP 403 | Endpoint vivo, la red llega |
| `openrouter.ai` | HTTP 200 | Alcance OK |
| `api.deepseek.com` | HTTP 401 | Endpoint vivo, la red llega |
| `www.googleapis.com/pagespeedonline/v5/runPagespeed` | HTTP 429 | Host real del cliente (`pagespeed_client.py:27`), vivo |

Una primera sonda usó `pagespeed.googleapis.com`, que **no** es el host del producto, y dio `gaierror`; ese rojo era
del instrumento, no de la dependencia.

**Rectificación de lo declarado en chat:** se informó que la URL viva «respondía 200 dos veces» y por tanto que la
red no era riesgo. La frase estaba sobrestimada. El estado medible es: el sitio **está vivo** (se observó un 200 con
la redirección al ápice que midió FASE-A en `decisiones.md` P16), pero la **resolución desde esta máquina es
inestable** y al re-medir cayó 0/5. Aun así se lanzó el intento, porque el spawn ya estaba autorizado, la
alternativa era cerrar la fase sin muestra, y relanzar está prohibido por el contrato.

## Spawn ejecutado

`run_once.py --spawn`, única invocación, en segundo plano. El control productivo quedó:

- `attempts: 1` — el contador del plan pasó de **0/1 a 1/1** desde la creación del proceso, acreditado por
  `run_control.json` y no por la narración (L-R.4).
- `estado: EN_EJECUCION`, `pid: 30576`, `exit_code: null`, `creado_en` y `iniciado_en` del 2026-10-07.
- `argv` literal con el intérprete y las once piezas, incluida `--permission-mode auto`; `argv_sha256 b5748891…`.
- Los 10 `source_hashes` consignados, con el runner ya en `1efa6cd1…`.
- El `snapshot_memoria` de 21 archivos viaja dentro del control, con sha256 por archivo, como exigía AC17.

## Pendiente para poder lanzar

- **Sonda de conectividad a la URL viva**: autorizada por el operador en formulario, pero el clasificador de
  permisos exige la confirmación **escrita en el chat** y rechazó la petición. Medido antes del bloqueo:
  `gethostbyname("www.donalfonsohotel.com")` resuelve a `212.1.212.188`, mientras `getaddrinfo`/`urlopen` fallaban
  con `gaierror 11001` en la misma sesión; openrouter, googleapis, deepseek y perplexity sí conectaban. FASE-A midió
  esta URL devolviendo 200 con redirección a `https://donalfonsohotel.com/` el 2026-09-19 (`decisiones.md` P16), así
  que el síntoma es de resolución inestable. **No se re-intentó la llamada negada.** Un `--spawn` sobre esta duda
  gastaría el único intento en un posible fallo de red, y el plan prohíbe el segundo E2E implícito.
- La revalidación por reloj la hace el propio runner (`revalidar_contra_la_fecha`, `run_once.py:789`), así que no
  hace falta re-emitir el preflight el día del spawn mientras no se edite ninguno de los 10 archivos congelados.
