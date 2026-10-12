# Pre-vuelo FASE-E2E — corrida única de `v4complete` (Hotel Don Alfonso)

**Plan**: CURA-COSTURA-TRIBUNAL-2026-10-11 · **Fase**: FASE-E2E · **Fecha de la medición**: 2026-10-12
**Árbol medido**: tip `bce67bc`, `SUCIOS=0` (contado con `git status --porcelain=v1 | wc -l`), paridad `0 0`
(`git fetch` + `git rev-list --left-right --count origin/master...HEAD`), `git ls-remote` casando `bce67bc`.
**Veredicto del preflight**: **`spawn_autorizado: true` — 13/13 requisitos favorables**
(`evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/preflight.json`, sha256
`de570a2712bd9eb6953bd2ff1098cc2e300a22d262863e87ee99bc4c8ee5c4ca`; su crudo impreso
`preflight-sonda-crudo.txt`, sha256 `568baea2baa0c43f9b6995ca13414186aec9b19537949699bc6c3bb8230c5344`).

## 0. Cómo corrió el arnés (opción A del prompt, con su detalle mecánico)

El arnés es **desechable y se ejecutó por stdin**: `PYTHONUTF8=1 ./venv/Scripts/python.exe - < temp/preflight_e2e.py`.
No entró ningún `.py` versionado. Ajuste mecánico declarado: el prompt pedía el arnés por stdin con heredoc inline,
pero el heredoc de ~7 KB resultó **truncado por el tool de shell** (bash devolvió `unexpected EOF while looking for
matching ''`, sin ejecutar nada). La vía fue escribir el cuerpo en `temp/preflight_e2e.py` y pasarlo **por stdin** al
intérprete. `temp/` está gitignorado (`.gitignore:21` `temp/*`) y **excluido por rol** del verificador de cableado
(`EXCLUSIONES_POR_ROL["temp"]`, `scripts/validate_wiring.py:193`), y desde el schema 1.3 ese rol ya no publica
`cantidad` en el artefacto gobernado (su docstring: «un scratch en `temp/` los mueve sin tocar una línea versionada»
es precisamente lo que se retiró del derivado). Verificado después de la corrida: `SUCIOS=0`. El scratch se borra al
cerrar la sesión.

El arnés **reutiliza los predicados** de `run_once.py` / `integracion_offline.py` / `derivar_onboarding.py` (cargados
por ruta de archivo) y **re-mide los cuatro insumos vencidos**: procedencia del derivado (productor re-corrido en esta
fase), rama efectiva del loader sobre el `clientes_dir` efectivo, `edad_dias` contra la fecha del run, e
identidades/argv del comando de **esta** fase. Los doce nombres de requisito son los del vocabulario de REFACTOR, para
que la comparación sea posible; el decimotercero (`el_dominio_responde`) es propio de esta fase (es el checkpoint
T0 e).

## 1. T0(a) — Derivar el onboarding, no editar el warehouse (DEC-A4)

Productor: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/derivar_onboarding.py`, corrido **sin banderas**
(su `main(argv)` ignora cualquier argumento desconocido; `--fecha` no se pasó para no mover `generado_el` y dejar la
salida confrontable con el blob versionado). Salida impresa: `{"rama_efectiva": "YAML_DE_DIR_CLIENTES"}`, EXIT 0.

| Control | Antes | Después | Veredicto |
|---|---|---|---|
| sha256 `data/hotel_observations/observations.json` (fuente inmutable) | `31e70a376894dcb91795246b49d6b2eb464d725996713b818afbf653f26b69bf` | `31e70a376894dcb91795246b49d6b2eb464d725996713b818afbf653f26b69bf` | **IGUAL** (invariante DEC-A4 cumplida) |
| sha256 `evidence/REFACTOR-…/FASE-H/onboarding_provenance.json` (versionado) | `9e5c5f29f6acce9dbb162f2e805c6ffe28c9db05bc71f7364f2a8f5d5a0576f5` | igual | **byte-idéntico al blob de HEAD** (medido con `git show HEAD:… | sha256sum`) |
| sha256 del YAML que escribe el productor en `output/REFACTOR-…/clientes/` | `2990d768f0ae75f3a5dfe6fac098f94c116ddc1b47a27b8727216c371b47c734` | igual | reproducido por la re-corrida |
| `git status --porcelain` tras la re-corrida | — | — | `SUCIOS=0` |

**Errata del prompt, corregida aquí**: la Base Técnica atribuía `9e5c5f29f6acce9d…` al YAML derivado. Medido, ese sha
es el de `onboarding_provenance.json` (disco == blob HEAD); el YAML es `2990d768f0ae75f3…` y **no tiene blob en HEAD**
porque vive bajo `output/` (`git ls-files output/` = 0 archivos; la regla que lo excluye es `.gitignore:54`
`output/*/`). La comprobación «disco contra HEAD» solo aplica al `.json`.

**Colocación en el `clientes_dir` efectivo** (el paso que el productor no hace, hallado el 2026-10-12): default de
`--output` leído del argparse real = `./output` (`main.py:56`), y `run_v4_complete_mode` construye
`clientes_dir = Path(args.output) / "clientes"` (`main.py:1816`) → **el directorio efectivo es `output/clientes`**.
Se copió el YAML ahí y se verificó byte a byte:

- `output/clientes/hotel_don_alfonso_onboarding.yaml` → sha256 `2990d768f0ae75f3a5dfe6fac098f94c116ddc1b47a27b8727216c371b47c734`
  (`cmp` con el origen: idénticos). Es el archivo que ve el loader, no una suposición.
- Copias de procedencia en esta carpeta: `hotel_don_alfonso_onboarding.yaml` (mismo sha) y
  `onboarding_provenance.json` (`9e5c5f29…`, `cmp` idéntico, y el preflight re-afirma `proven == proven_ajena` = `True`).

## 2. T0(b) — Sonda read-only del loader sobre el `clientes_dir` efectivo

`main._load_latest_onboarding_data(hotel_url="https://www.donalfonsohotel.com/", hotel_name="Donalfonsohotel",
output_dir=Path("output/clientes"))`, corrida **dentro del corte de red** con su diente medido.

| Medición | Valor |
|---|---|
| Rama efectiva (predicado `derivar_onboarding.ramas_del_loader`) | **`YAML_DE_DIR_CLIENTES`** (la aceptable; no `OBSERVATIONS_DENTRO_DE_LA_FUNCION`, no `NINGUNA`) |
| `devolvio_datos` | `True` (no `None`: no hay DETENER-CONSULTA por este requisito) |
| `campos_confirmados` | **4** — `habitaciones`, `reservas_mes`, `valor_reserva_cop`, `canal_directo_pct` |
| `metadatos.fecha_captura` leída | `2026-07-22` |
| `metadatos.fuente` declarada | `observations_tier_a` |
| YAMLs observados en el directorio | `hotel_don_alfonso_onboarding.yaml`, `zi-one-luxury_onboarding.yaml` (el de Zione no casa por `_normalize_url`; la sonda devolvió el de Don Alfonso) |
| `ONBOARDING_FRESHNESS_HOURS` | **AUSENTE** — leida del entorno del proceso **después** de `load_dotenv` (`main.py:11-17` carga `.env` en el import) y `.env` no la declara. Con la variable ausente el loader **no** descarta el YAML por edad (`main.py:4085`), así que el riesgo L-VUP-13 de «Using defaults» mudo está cerrado para esta corrida. Si alguien la encendiera antes del spawn, el `fecha_captura` de 2026-07-22 cae fuera de cualquier límite razonable y el fallback del warehouse **tampoco casa** (allí `website` es `https://hoteldonalfonso.com/`) |

## 3. T0(c) — Preflight del único intento (13 requisitos por nombre, con su procedencia)

`P` = predicado reutilizado del arnés de REFACTOR; `M` = medición propia de FASE-E2E.

| Requisito | Cumple | Qué lo sostiene | Procedencia |
|---|---|---|---|
| `entorno_venv` | ✅ | `venv/Scripts/python.exe` existe | `P` (`run_once.preflight`) |
| `fuente_inmutable_intacta` | ✅ | sha256 del warehouse == `sha256_despues` de la procedencia y `sin_cambio: True` | `M`: sha antes/después de re-correr el productor |
| `selector_unico` | ✅ | `hotel_name == "Hotel Don Alfonso"` → 1 coincidencia sobre el total del warehouse | `M`: `derivar_onboarding.seleccionar_unicamente` re-ejecutado |
| `rama_efectiva_del_loader` | ✅ | `YAML_DE_DIR_CLIENTES` sobre `output/clientes` (ver §2) | `M`: sonda propia + `P` el predicado de rama |
| `frescura_fail_closed` | ✅ | `fecha_captura` `2026-07-22`, **edad 82 días** contra el techo `EDAD_MAXIMA_DIAS = 90` → **vence el 2026-10-20** | `M`: `run_once.edad_contra_la_emision` contra la fecha del run |
| `consentimiento_datado_sobre_la_url_viva` | ✅ | `autoriza_entrega: True`; `declarado_por: "Jhond (operador)"`, `fecha: 2026-10-12`, límite 90 | `M`: `run_once.evaluar_consentimiento` con `ruta=` al **consentimiento de CURA** (`consentimiento-corrida.md`, sha256 `dafef45d6171f2ca…`); el bloque de REFACTOR no se usa ni se enmienda |
| `revocacion_de_claves` | ✅ | `cumple: True` **por declaración del operador, no por evidencia operativa**; pendientes releídos: «resto de proveedores configurables (OpenRouter, Perplexity, PageSpeed/Google, DeepSeek)» | insumo de FASE-F (plan ajeno) releído; su semántica es la misma que en H |
| `identidades_fijadas` | ✅ | los tres valores son distintos: `hotel_donalfonsohotel.com` / `Donalfonsohotel` / `donalfonsohotel.com` | `M`: argv de **esta** fase parseado con `main.build_parser` + los tres productores del producto |
| `argv_congelado` | ✅ | `--permission-mode` no se pasa y su **default medido es `auto`**; ninguna bandera prohibida en el argv | `M`: parseo real del argv de esta fase |
| `red_prohibida_y_sin_cli_real` | ✅ | diente del corte medido (`socket.create_connection` levanta `AssertionError`); la sonda corrió dentro del corte; `main.py v4complete` **no** se invocó en el preflight | `M`: `integracion_offline.cortar_red` re-ejecutado |
| `aislamiento_de_memoria` | ✅ | declarado, no satisfecho (igual que en H): ver §5 | `M`: `run_once.inventario_memoria` + `integracion_offline._analysis_previo` sobre el canonical de esta fase |
| `control_productivo_intacto` | ✅ | `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/run_control.json` **no existe** | `M`: anclado a la ruta de CURA — es el chequeo que el arnés de REFACTOR no podía cumplir (sus constantes `RAIZ`/`PLAN`/`DIR_FASE`/`DIR_EVIDENCIA_PRODUCTIVA` son de módulo y no es `--raiz`-aware) |
| `el_dominio_responde` (propio de T0 e) | ✅ | ver §4 | `M`: HEAD/GET real con dos clientes |

**Contador de intentos: 0/1 antes del spawn.** No se creó `run_control.json`: el arnés de H lo escribe en su propio
`lanzar_unico`, y esta fase lanza por subagente con el comando literal del prompt, así que la reserva queda registrada
aquí y en la evidencia post-corrida, no como archivo de control ajeno al flujo.

## 4. T0(e) — El dominio responde (y una inestabilidad del entorno, declarada)

Medición con dos clientes en el mismo proceso:

- **`requests`** (el mecanismo real del pipeline: `modules/utils/http_client.py:223` usa `requests.get`, y lo consumen
  `modules/scrapers/web_scraper.py` y `modules/auditors/v4_comprehensive.py`): **intento 1 → 200 OK**,
  `url_final = https://donalfonsohotel.com/`, **142.017 bytes**, historial `[https://www.donalfonsohotel.com/]`.
- **`urllib` (stdlib), HEAD, 3 intentos con 2 s de espera**: **3/3 fallaron** con
  `URLError: <urlopen error [Errno 11001] getaddrinfo failed>`. En una corrida standalone previa el HEAD de urllib sí
  devolvió 200 y su GET falló: la falla es **intermitente del resolutor de este equipo**, no del sitio. `curl` por
  separado: `HEAD` con cabeceras completas (`platform: hostinger`, `x-hcdn-cache-status`) y `GET -L` → `301` a
  `https://donalfonsohotel.com/` → `200`. `nslookup` resuelve (2 AAAA + 2 A).

**Criterio decidido y por qué**: el requisito se resuelve por el cliente que la corrida va a usar (`requests`), no por
el HEAD de stdlib de mi sonda. Publicar un NO-FAVORABLE por un fallo intermitente del instrumento —con el sitio
respondiendo por tres vías independientes— habría sido el mismo error de verde/prestado pero en sentido inverso. Queda
declarado como **hallazgo de entorno**: la resolución DNS de este host es inestable bajo urllib, y el run puede ver
alguna petición fallando; no es bloqueador y no se compensate.

**Redirección**: `www.donalfonsohotel.com` → `donalfonsohotel.com` (misma dominio registrado, cambia solo la etiqueta
`www`). `_normalize_url` reduce ambos a `donalfonsohotel.com` — su propio docstring: «Reduce
https://www.zione.co/ → zione.co» — así que **no** es «un dominio distinto del del YAML derivado» y el checkpoint no
se dispara. El `hotel.url` del derivado sigue siendo la URL canónica dictada por el operador (2026-10-11).

## 5. T0(d) + efectos secundarios que la corrida va a tocar

**Credenciales por nombre de variable (nunca su valor)**, leídas del entorno del proceso tras `load_dotenv`:

| Variable | Estado |
|---|---|
| `DEEPSEEK_API_KEY` | PRESENTE (valor no impreso) |
| `ANTHROPIC_API_KEY` | AUSENTE |
| `LLM_PROVIDER` | PRESENTE, valor no secreto: `deepseek` |
| `ONBOARDING_FRESHNESS_HOURS` | AUSENTE (ver §2) |

Con `DEEPSEEK_API_KEY` presente no hay riesgo de extracción `FALLIDO` por ausencia de credencial (el riesgo que el
prompt ordenaba detener y consultar). El componente de proveedor de la clave de cache (AC4) se resuelve por
`LLM_PROVIDER` declarada.

**Efectos declarados antes de gastar el intento** (medidos, no inferidos):

- `memory.cleanup_old_sessions(days=20)` (`main.py:1666`) **va a borrar 2 archivos**:
  `.agent/memory/sessions/2026-09-19_3b0f3a94.json` y `.agent/memory/sessions/2026-09-19_dfa27c04.json`.
- `find_latest_analysis(canonical)` **sí encuentra** un análisis previo
  (`output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/v4_complete`): la corrida **no está aislada de la memoria**.
  Según el predicado re-utilizado (`_consumo_del_analysis_previo`, medido por AST en H), en
  `run_v4_complete_mode` esa variable solo se imprime; la reutilización efectiva vive en `run_execution_mode`.
- **`.cache/tribunal/` antes de la corrida: 3 entradas**, todas de formato viejo (las más recientes
  `442e361c…` 2026-10-07, `5c4c2146…` 2026-09-19, `00070f04…` 2026-09-11). Con la clave versionada de FASE-A quedan
  inertes (mandato del maestro: sin migración). Este snapshot es la línea base para identificar **los recibos nuevos**
  de la corrida (T2).
- **`output/v4_complete/` no existía** antes de la corrida (`existe: False`): todo lo que aparezca ahí es de esta
  sesión.
- **`--force-new` es inerte en `v4complete`** (hallazgo de esta fase): el parser la reconoce
  (`main.py:143`, `force_new=True` medido) pero su **único consumidor es `run_execution_mode`** — grep de `force_new`
  en `main.py` da una sola línea con código: `main.py:773`. La frase del prompt «`--force-new` para garantizar
  inyección fresca de onboarding» **no describe el mecanismo**: la inyección la garantiza el YAML colocado en
  `output/clientes` (requisito `rama_efectiva_del_loader`, ✅). Se corrió igualmente el comando literal autorizado; no
  se agregó `--nombre` ni `--output` porque eso cambiaría el argv autorizado por el operador y las identidades del
  paquete.

## 6. Línea base de no-regresión (AC16) y cortes

- Sin código nuevo → sin tests nuevos. Línea base leída del árbol del tip `bce67bc` con el comando canónico commiteado:
  `git grep -c -E "^\s*def test_" HEAD -- tests` = **5321** (la cifra que publicaron FASE-C2 y su sello).
- `run_all_validations.py --quick` **no se corrió durante el spawn** para no medir un árbol con la corrida escribiendo
  `output/` y `evidence/` a la vez; se corre al cierre de T3 y su resultado se publica ahí.
- Cortes declarados: **pre-vuelo terminado y favorable** → (T1 en curso) → verificación → cierre documental → listo
  para revisión → **espera de autorización**. Ningún `git commit` ejecutado ni autorizado en esta fase.
