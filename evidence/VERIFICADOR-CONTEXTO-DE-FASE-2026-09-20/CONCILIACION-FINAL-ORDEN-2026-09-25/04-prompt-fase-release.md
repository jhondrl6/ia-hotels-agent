# Prompt FASE-RELEASE — listo para pegar en una sesión posterior

**No ejecutado en esta sesión.** La conciliación final del 2026-09-25 **no** autoriza FASE-RELEASE, no la
empieza y no la encadena. Este bloque es su entregable 4.

Fuente canónica: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-RELEASE.md`
(conciliado el 2026-09-25 y **rectificado el mismo día**: cuatro prompts nombrados en la lista de lectura,
cola de regeneración fija **después** de las últimas escrituras, `--fix`/`--update-baseline` **fuera** de la
secuencia, trampa de `--carga` declarada y **C0** como permiso previo sobre los destinos escribibles).
Este archivo es una **copia pegable**, no una segunda fuente de estados: si el prompt canónico cambia,
manda el canónico. Antecedente de las dos versiones anteriores: `22-prompt-canonico-antes.txt` y
`23-prompt-pegable-antes.txt`; delta en `28-diff-permisos.txt`.

## C0 — Autorizar destinos antes de escribir

**Rectificación 2026-09-25:** la versión inicial de este entregable confundía «offline» con permiso de
escritura y agrupaba `sync_versions.py` con su modo `--check`. Se retira esa lectura; el antecedente se
conserva en `23-prompt-pegable-antes.txt`. Rige C0 del prompt canónico y de su contrato.

Antes de cualquier escritura de RELEASE, contrastar los destinos reales de los writers con una
instrucción literal del operador. Iniciar RELEASE no autoriza por sí solo `AGENTS.md`, `.cursorrules`,
`VERSION.yaml`, `REGISTRY`, sus trackers ni otros archivos centrales. Si falta un destino necesario,
detenerse y pedirlo; solo continuar lecturas autorizadas. No declarar cierre offline completo con C0
incompleto. La alineación de política de DOMAIN_PRIMER se decide aparte del sync de cabeceras.

## Operaciones offline previstas (sujetas a C0; no son permisos concedidos)

| Operación | Comando / destino | Naturaleza |
|---|---|---|
| Confirmar estado de A/B/C/D **en disco** | `git ls-files scripts/decision_client.py scripts/triage_lesson_relevance.py scripts/build_phase_briefing.py`, `git status --short`, tablas de `dependencias-fases.md` | lectura |
| Leer la firma del writer sin llamarlo (D10) | `./venv/Scripts/python.exe scripts/validate_qmind_writeback.py --help` | lectura local, **no** es remota |
| Verificar sincronización | `sync_versions.py --check` | solo lectura; un rojo no autoriza escribir |
| Sincronizar versiones | `sync_versions.py` **sin `--check`** puede escribir `README.md` de raíz, `AGENTS.md`, `.cursorrules`, `docs/CONTRIBUTING.md` y `docs/GUIA_TECNICA.md`, según `scripts/sync_config.yaml` | requiere permiso literal de esos destinos para versión/fecha/codename; no concede edición de política |
| Publicar documentación de cierre | `CHANGELOG.md`, contenido de `docs/GUIA_TECNICA.md`, documentos del plan y `09` §A/B/D/E | escritura solo con destinos autorizados en C0 |
| Registrar la fase | `scripts/log_phase_completion.py` sobre `docs/contributing/REGISTRY.md`; también `docs/contributing/.last_doc_phase.json` si se pasa `--archivos-mod` | permiso explícito sobre todas sus salidas; sin duplicar fases |
| Verificar sin escribir | `validate_governance_numbers.py --report` (**sin destino**), `validate_document_integration.py`, `validate_lesson_capitalization.py`, `validate_plan_citations.py`, `validate_opencode_refs.py` (**sin `--fix`**), `run_all_validations.py **--quick**` | lectura |
| Cierre de derivados (cola fija, **después** de la última escritura de documentos) | `build_phase_briefing.py --plan <ruta>` → `build_lesson_index.py` → `build_phase_briefing.py --plan <ruta> --check` → `build_lesson_index.py --check` → `run_all_validations.py --quick` | escritura en `briefing/` y en el par `.opencode/LECCIONES-INDEX.md` + `lecciones_index.json` |

**Prohibiciones de la fase** (viajan del contrato y de la orden de calidad): no modifica código fuente ni
`scripts/*.py` (un defecto del generador se **declara** con su dueño y deja checkpoint); no repara
`.agents/` (D1 ya se resolvió desde su fuente — correr el verificador es **leer**, no arreglar); no
promociona ningún `⚠️`/`NO-EJERCITADO` a verde; no re-registra fases ajenas; no re-escribe `carga.json` ni
ningún expediente cerrado; el modo completo de `run_all_validations.py` **no** se corre (su `[15/15]`
invoca el write-back de QMind).

## Destinos de sincronización (qué archivo es de quién)

- `VERSION.yaml` → entrada del sync, no salida. Su cambio exige autorización propia con versión y fecha
  aprobadas; ni el nombre RELEASE ni un hook autorizan un incremento. El permiso para sincronizar
  cabeceras no autoriza editar su política ni cambiar código/configuración del writer.
- `docs/contributing/REGISTRY.md` → **solo** por `log_phase_completion.py`; su regla de fecha
  (`registry_last_update`) **fue retirada** de `sync_config.yaml` a propósito — no reintroducirla.
- `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` → **solo** por `build_lesson_index.py`,
  y **después** de los packs.
- `.opencode/plans/<PLAN>/briefing/FASE-*.md` → **solo** por `build_phase_briefing.py` (cada corrida
  reescribe los **5** packs del plan: no hay bandera por fase).
- `docs/CONTRIBUTING.md`, `docs/contributing/*.md`, `AGENTS.md`, `.cursorrules`, `.agents/**` → **configuración
  central**: cualquier edición suya exige instrucción literal **separada** del mandato de RELEASE.

## Checkpoints separados. C0 precede las escrituras; cada permiso se pide y se reporta aparte

| # | Checkpoint | Operación | Qué lo habilita | Si falta el permiso, se publica como |
|---|---|---|---|---|
| C0 | **Destinos offline** | Contrastar salidas reales de sync, registro y demás writers con los archivos permitidos | Mandato literal con destinos y campos de sincronización; permiso propio para cambiar VERSION y para alinear política | Preflight incompleto: no escribir ni declarar cierre offline completo |
| C1 | **Consulta** QMind (D8) | re-corrida de Q7 con `--nb 01a04d98-b7bd-778c-8441-26fdc7e35f45` (la forma con el nombre da `Bad request`) | autorización literal + presupuesto de lectura | `PENDIENTE-AUTORIZACION` con la causa, **no** «verificada» ni omitida |
| C2 | **Subida** QMind (D9) | `validate_qmind_writeback.py --upload <plan>` con el plan **aún en raíz** (R2.10) | autorización literal + presupuesto; re-leer la firma (writer decide **por título**, degrada a `exit 0` sin CLI) | `PENDIENTE-AUTORIZACION`, y la ingesta final por `qmind source upload` directo **dicho explícitamente** |
| C3 | **Archivado** | `git mv .opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 .opencode/plans/Archives/` + re-regeneración de packs e índice con la ruta trasladada | autorización propia del traslado, separada del cierre documental | no se mueve nada; el plan queda en raíz y se declara |
| C4 | **Correcciones de corpus** | Comprobar refs y citas sin `--fix` ni `--update-baseline`; presentar cualquier corrección necesaria | Permiso aparte por archivo antes de escribir; no actualizar baselines para absorber errores | El rojo se declara con su lista, sin reescrituras automáticas |
| C5 | **Commit** | `git commit` del árbol (o del subconjunto que se nombre) | instrucción literal; el hook `[1/7]…[7/7]` puede reescribir `AGENTS.md`/`VERSION.yaml`/`.cursorrules` — por eso se decide **antes** qué viaja | árbol sin commitear, con la **frontera declarada** (qué rutas propias vs. ajenas, como hizo FASE-C con sus 37 rutas y 164 hunks) |
| C6 | **Push** | `git push` | instrucción literal separada del commit | `PENDIENTE-AUTORIZACION`; el estado del remoto **se mide**, no se infiere |

**Un checkpoint no habilita el siguiente.** El `git commit` **no** es condición de ninguno de los cinco
cortes del cierre: implementación → verificación → cierre documental → listo para revisión → espera de
autorización, y los cinco terminan en espera.

## Prompt pegable

```text
Ejecuta unicamente FASE-RELEASE del plan
C:/Users/Jhond/Github/iah-cli/.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/
empezando por su Tarea 1 y sin encadenar ningun checkpoint remoto.
Lee 05-prompt-inicio-sesion-fase-RELEASE.md, 01-plan-maestro.md §4 y §6, 04-contrato-ejecucion.md
(§Dos momentos del cierre, §Carga total y frescura del pack, §Orden del cierre),
00-lecciones-capitalizadas.md completo, 06-checklist-implementacion.md, dependencias-fases.md,
10-analisis-post-implementacion.md, los cuatro prompts de fase uno por uno
(05-prompt-inicio-sesion-fase-A.md, 05-prompt-inicio-sesion-fase-B.md,
05-prompt-inicio-sesion-fase-C.md, 05-prompt-inicio-sesion-fase-D.md), docs/CONTRIBUTING.md y el
workflow canonical (FASE-RELEASE).
Re-mide en disco el estado de A, B, C y D antes de tocar nada: AC15 sigue NO-EJERCITADO y D6 dormida,
y ese estado viaja al cierre tal cual. La dependencia tecnica de JEV ya se entrego; eso no autoriza nada.
Primero C0, antes de escribir: este prompt no concede permisos sobre los destinos de los writers.
Relee scripts/sync_config.yaml: sync_versions.py SIN --check puede modificar README.md de raiz,
AGENTS.md, .cursorrules, docs/CONTRIBUTING.md y docs/GUIA_TECNICA.md. Exige autorizacion literal para
esos archivos y sus campos de version/fecha/codename; --check solo lee. VERSION.yaml es entrada, no
salida del sync: cambiarla exige version y fecha aprobadas. Exige tambien destinos autorizados para
CHANGELOG, contenido de GUIA_TECNICA, REGISTRY y trackers, documentos del plan, packs, indice y expediente.
Si falta alguno necesario, detente antes de escribir: checkpoint C0, no cierre offline completo.
Solo pueden continuar lecturas autorizadas: sync_versions.py --check, validate_qmind_writeback.py --help
y verificadores sin escritura. Alinear la politica de DOMAIN_PRIMER exige otra decision literal:
el permiso de sincronizar cabeceras no autoriza esa alineacion ni regenerar el primer.
validate_governance_numbers.py es LEER el estado, no reparar .agents/.
No corras run_all_validations.py sin --quick: el modo completo invoca el write-back de QMind.
Checkpoints que NO estan autorizados por este prompt y se piden uno a uno: C1 consulta Q7 (D8), C2 subida
--upload (D9), C3 git mv a Archives, C4 correcciones de corpus, C5 commit, C6 push.
Sin su permiso literal se declaran PENDIENTE-AUTORIZACION con causa y dueno, nunca
se omiten en silencio ni se promociona el cierre parcial a exito. No actualizar baselines para absorber
errores. Refs y citas se verifican sin --fix ni --update-baseline; cualquier correccion requiere permiso.
Cola final despues de la ultima escritura autorizada: regenerar
packs -> regenerar el par del indice -> check del pack -> check del indice -> quick. Nunca al reves: los
packs son .md dentro del corpus del indice (L-VCF-17).
No uses --carga ni --informe apuntando a evidence/.../FASE-D/: esa evidencia esta cerrada (S12). Usa - o
una ruta nueva dentro de evidence/.../FASE-RELEASE/.
El delta de CARGA TOTAL se referencia desde FASE-D/carga.json y desde la fila «Carga de lectura A7» del
README; no se transcribe en 10- ni en 09 ni en esta copia. Su recalculo sobre el expediente cerrado es
13,15 % (216.721 / 1.648.109). La re-medicion del 2026-09-25 esta en
evidence/.../CONCILIACION-FINAL-ORDEN-2026-09-25/11-carga-corrida-3.txt y describe otro arbol que la
medicion cerrada de D (5 packs COMPLETO y 37 fuentes frente a 4+1 y 34): si el cierre re-mide, abre
expediente propio y no pisa el anterior.
S15 declarada, no absorbida: un verde local de [6/7] no certifica otro checkout, y reparar
build_lesson_index.py es alcance tecnico separado que RELEASE no tiene autorizado.
Las cinco propuestas pendientes de revision humana (E3) no se aceptan ni se rechazan desde el cierre:
viajan como pendientes con su dueno.
Termina en «listo para revision» con la matriz requisito -> evidencia -> estado -> remanente, la frontera
del arbol (que es de esta fase, que es ajeno, que esta sin commitear) y los checkpoints C0-C6 listados.
```

## Qué se espera como salida legítima

Con C0 incompleto, **checkpoint previo sin escritura**, no cierre completo. Con permisos suficientes y
las tareas offline verificadas, un **cierre documental offline** con deuda D1–D10 leída desde sus fuentes
(§13 de B para D1/S13), D6 dormida con causa, D2 y D7 sin tocar; C0–C6 declarados con su estado real; `09`/`10` cerrados por
referencia a sus artefactos; packs e índice regenerados sobre el árbol final y verificados con sus dos
`--check` + `--quick`; y la evidencia nueva en `evidence/…/FASE-RELEASE/` sin sobrescribir ningún
expediente anterior. Un resultado así **no** dice «calidad semántica medida» ni «los cuatro planes
terminados».
