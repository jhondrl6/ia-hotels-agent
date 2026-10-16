# CONTEXT — Lecciones de la cura del emisor de fragmentos de credenciales

**Fecha:** 2026-10-11. **Sesión:** fix + diente + barrido de forma en el verificador (`d35cb3d`,
`57bc6d7`, `08f08c9`, `3110792`, todos empujados). **Sin plan dueño:** el trabajo no pertenece al
alcance de `CURA-COSTURA-TRIBUNAL-2026-10-11` (costura del Tribunal), así que las lecciones se
definen aquí, en el corpus de definiciones que el índice reconoce para `.opencode/context/`.

> **Qué es este archivo.** Dos lecciones de proceso sobre credenciales y sobre commits, cada una con
> su evidencia re-midada en el árbol vivo y su contrafactual. No es un plan, no abre fase y no
> declara ACs.
>
> **No autodeclara lección durable.** La entrada a la población de write-back de QMind depende de tres
> grafías al inicio de línea —las dos de forma/durable y la de lecciones capitalizadas—, no del nombre
> del archivo. Este documento no escribe ninguna de las tres, así que
> `scripts/verify_qmind_context_freshness.py` debe publicarlo como `[EXCLUIDO]` con la razón de
> no-declaración: la política del write-back es por aporte declarado, no por existencia.
>
> **Acuña dos IDs nuevos**, `L-SECF.1` y `L-SECF.2`, ambos definidos aquí. Cita IDs ajenos solo cuando
> están definidos en el corpus: `L-CIM.8` (vecino, y no es lo mismo: habla de derivados cuya población
> incluye untracked, no de que el commit los ignore) y `S-E2E-6`. Contadores al escribir: **378 IDs**
> antes de regenerar el par, `citados_sin_definicion` sin cambio.

---

## 0. Veredicto en una línea

Un enmascarado que deja prefijo y sufijo **no oculta nada**, y un verificador que exempta los
directorios donde ese texto vive **no puede fiscalizarlo**: las dos lecciones son la misma enfermedad
vista desde lados distintos — el instrumento declara conformidad sobre un insumo que no está mirando.

---

## 1. `L-SECF.1` — El recorte `prefijo…sufijo` de una credencial no es anónimo, y la exención de cuarentena lo dejaba sin leer

`modules/utils/config_checker.py` reportaba sus claves con un masked de primeros y últimos cuatro
caracteres, comentado «por seguridad». Sumado a dos hechos, eso publicó credenciales en un repo
**público**:

1. Las formas que redactan (`modules/utils/redaction.py`, `SECRET_SHAPES`) exigen **≥16 chars tras
   `sk-`** y **≥25 tras `AIzaSy`**. Un recorte de 4+3+4 es más corto que el patrón que debería
   cazarlo: `redact_secrets` lo devuelve intacto, medido con cadena sintética.
2. El `Secrets Check` del quick exempta en disco `archives/`, `evidence/` y `.opencode/` porque su
   propósito es contener *referencias* a secretos. Con esa exención y patrones de forma completa, el
   check dijo `SIN_HALLAZGOS` teniendo el archivo delante. Lo detectó un barrido humano, no el gate.

**Cómo se midió el daño.** Cuatro líneas con forma de fragmento en todo el árbol versionado. Contra
los valores vivos de `.env` (comparando solo prefijo y sufijo, sin imprimir el valor), **una** casaba
con una clave vigente: el crudo de `evidence/FASE-I/faseI_run.txt`. Las otras tres eran de claves ya
rotadas. La captura del FASE-E2E del REFACTOR-WHATSAPP llevaba cuatro fragmentos vivos y **nunca**
debió entrarse al índice: la tanda del 2026-10-07 ya la había excluido por `S-E2E-6` y publicado una
saneada sin fragmentos; su sha sigue citado entre los 35 de `run_control.json`, así que sacarla del
índice no pierde trazabilidad.

**La cura, en tres capas.** (i) El emisor deja de imprimir contenido: publica nombre, estado y
longitud, con diente que goberna la **forma** (ninguna salida puede casar `xxx…yyy`) y dos controles
ejecutados — el mutante que restaura el recorte, y `git show` de la revisión pre-cura, que sí lo
emitía. (ii) El `Secrets Check` tiene una segunda pata que barre los directorios exemptados con la
forma anclada en **familias de prefijo**, con política propia
(`config/secret_fragment_policy.yaml`): grandfathered **por línea** con dueño y condición de salida,
`NO_CUBIERTO` si la política falta, y violación si la política y el check discrepan sobre qué está
exento. (iii) La ruta cruda queda ignorada por `pathspec` concreto, no por `evidence/**`, para que un
`git add -A` no la devuelva al índice.

**Contrafactual medido, y por eso el patrón es el que es.** Anclar la regla en la **etiqueta**
(`*_API_KEY:` en lugar del prefijo) casaba con los placeholders de guía de `.env.template`, que no son
credenciales. Falso positivo real, y por eso el anclaje se movió al prefijo de familia. Lo que la regla
**no** cubre hoy: fragmentos de familias no listadas en la política.

**Cómo aplicarlo.** Antes de commitear o empujar evidencia de consola, cotejar los valores de `.env`
contra cada línea **por predicado** (longitud, `startswith`, `endswith`) y reportar solo nombre y
número de línea. En repo público, el mensaje de commit también es superficie de filtración: describe
el defecto del emisor sin declarar vigencia ni longitudes de credenciales. Y un enmascarado parcial no
es motivo para dejar de rotar: la rotación es la que deja huérfano lo publicado.

---

## 2. `L-SECF.2` — Un commit por pathspec no toma rutas *untracked*, y la salida filtrada convierte el no-commit en «sin salida»

Se bifurcó una tanda en dos commits con pathspec explícito. El primero (`.gitignore`, ruta ya
versionada) landed. El segundo llevaba cuatro rutas, **dos nunca vistas por Git**, y no landed:
`git commit -- <ruta>` toma el árbol de trabajo solo para rutas que Git ya conoce.

El fallo pasó dos veces inadvertidas:

1. La salida del commit se filtró con un `grep -E` cuyos patrones solo casan con el caso verde
   (`files changed`, `master `), así que excluyó tanto el banner del hook como las líneas de error.
   Resultado: **cero líneas**, que se lee como conformidad.
2. El `rm` del archivo de mensaje iba en la misma cadena, y se llevó el mensaje escrito junto con el
   intento fallido.

Se detectó al verificar `git log` y contra-poner `HEAD^{tree}` con el árbol materializado en el
pre-vuelo. Es decir: **por la verificación, no por la stdout**.

**Regla.** Un commit con pathspec va precedido de `git add` de esas mismas rutas, y su evidencia es el
árbol resultante (`git rev-parse HEAD^{tree}` contra el árbol pre-volado, y el rev que el hook imprimió
en `[8/8]`), nunca lo que el comando mostró. Si la tanda se bifurca, se pre-vuela **por árbol**, no una
vez para los dos.

**Trampa hermana, ya medida esta sesión.** Materializar el árbol de un commit con `GIT_INDEX_FILE` +
`git read-tree HEAD` + `git update-index --add -- <directorio>/` deja el árbol **igual a HEAD**:
`update-index` no desciende por directorios, avisa `Ignoring path …` y sigue. Un verificador de árbol
corrido sobre ese rev aprueba un árbol que no contiene lo del commit. Las dos trampas comparten forma
— el instrumento no ve su insumo y lo reporta como conformidad — y comparten cura: exigir que **el
cambio se demuestre** (`git diff --name-status HEAD <tree>` con el recuento esperado) antes de fiar
cualquier `EXIT=0`.

**Cómo aplicarlo.** Checklist completo en `docs/contributing/leccion-git-pathspec-untracked.md`, que
es la versión procedimental de esta lección. **No aplica** a `git commit -a` (toma lo tracked y deja
fuera lo untracked por la misma razón) ni a `git add -A && git commit` sin pathspec; en este repo el
pathspec explícito sigue siendo obligatorio porque el índice puede contener trabajo ajeno.

---

## 3. Tabla de definiciones

| ID | Enunciado | Definida en | Evidencia |
|---|---|---|---|
| `L-SECF.1` | El recorte `prefijo…sufijo` de una credencial no es anónimo: es más corto que los patrones que redactan, y un escáner que exempta los directorios donde vive no puede fiscalizarlo | este §1 | emisor curado con diente de forma en `tests/utils/test_config_checker_sin_fragmentos.py`; barrido de exentos en `scripts/run_all_validations.py` con `config/secret_fragment_policy.yaml`; 4 líneas fragmentadas en el árbol, 1 casando con clave viva antes de rotar |
| `L-SECF.2` | `git commit -- <ruta>` ignora las rutas untracked y una salida filtrada con `grep` lo borra del radar: la evidencia del commit es el árbol, no la stdout | este §2 | intento fallido del commit `08f08c9` (dos rutas nunca vistas por Git) detectado al cotejar `HEAD^{tree}`; `docs/contributing/leccion-git-pathspec-untracked.md` con el checklist |

---

## 4. Qué no sostiene este documento

- No afirma que el barrido nuevo cubra familias de credencial no listadas en la política: cubre las
  ancladas, y esa es su limitación declarada.
- No demuestra que la rotación de la DeepSeek haya cerrado la exposición histórica: deja el fragmento
  publicado **sin correlato vivo**, que es otra cosa. La purga del historial se descartó con argumento
  (no des-publica y reescribiría shas citados), no se ejecutó.
- No capitaliza lecciones de producto del plan `CURA-COSTURA-TRIBUNAL-2026-10-11`: esas siguen en su
  propio `00-lecciones-capitalizadas.md`, y este archivo no las re-escribe.
- Los contadores de IDs son los del momento de escribir; el par del índice se regenera con el mismo
  commit que publica este documento, y `build_lesson_index.py --check` es quien los estampa.
