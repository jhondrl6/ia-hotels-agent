"""FASE-E — cierre incremental documental (ediciones por ancla unica).

Cada reemplazo exige el numero exacto de ocurrencias; si no casa, aborta sin escribir.
No toca AGENTS.md ni DOMAIN_PRIMER (configuracion central protegida / sin autorizacion).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PLAN = ROOT / ".opencode/plans/REFACTOR-WHATSAPP-ENTREGA-2026-09-18"
EV = "evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E"

ESTADO_E = (
    "**Estado:** COMPLETADA 2026-10-06, **sin commit ni push** (el mandato no los autorizaba; los cinco "
    "cortes se sostienen sin commit). AC9/AC10/AC11/AC12 **VERIFICADAS OFFLINE** con el writer real y 8/8 "
    "mutantes cayendo por su guard. PRE 290 passed / 9 skipped / EXIT 0 y POST 321 passed / 9 skipped / "
    "EXIT 0 en la misma seleccion; canonicas 4.908 en HEAD y 4.939 en el arbol (+31, todas del archivo "
    "nuevo). Quick 12/13 al abrir el cierre por el derivado de wiring vencido y 13/13 tras regenerarlo con "
    "`validate_wiring.py --write-report`. Contador v4complete 0/1. R2 **FUERA DE SERVICIO (R2.1)**: "
    "auto-reporte ~105 tool_use al corte 'listo para revision', por encima de la referencia de 60, "
    "declarado como checkpoint y sin partir la fase. Detalle: `" + EV + "/resultados-y-observaciones.md`. "
    "**Dependencia inmediata:** FASE-D completa; verificar cierre real de A-D antes de editar."
)

CIERRE_09 = """## Cierre incremental de FASE-E (2026-10-06)

**Que se cerro.** Un resolvedor unico de insumos (`modules/quality_gates/tribunal/review_inputs.py`) con
copia interna **no exportable** antes del borrado del gate, y sus cinco consumidores: los cuatro Bots del
Tribunal y el Juez. El vocabulario `read_status` gano `NO_LEIDO` en `whatsapp_contract.py`, que es donde
FASE-C lo designo; `artifact_paths.resolve_latest` acepta la ruta `explicit` del run y **no** cae al
ascendiente compartido entre hoteles cuando esa ruta esta declarada y no existe.

**Metricas de la fase (medidas, no previstas).**

| Concepto | Valor |
|---|---|
| Funciones de test nuevas | 31 en `tests/quality_gates/tribunal/test_fase_e_snapshot_resolvedor.py` |
| Canonicas | 4.908 en HEAD -> 4.939 en el arbol (+31) |
| PRE / POST (misma seleccion) | 290 passed + 9 skipped / 321 passed + 9 skipped, ambos EXIT 0 |
| Mutantes | 8/8 caen por la asercion de su guard; 8/8 restaurados por sha256 |
| Quick | 12/13 con rojo de derivado (Wiring) y 13/13 tras regenerar con su writer |
| Archivos tocados | 9 modificados + 2 nuevos de producto/tests, mas la evidencia |
| Contador v4complete | 0/1 |

**Deuda que deja E (con dueno, en `resultados-y-observaciones.md` §7):** el resolvedor no ancla todavia los
JSON timestamped (`pain_ledger`, `gate_report_*`, `delivery_quality_report`, `proposal_asset_matrix`,
`financial_scenarios`), que siguen con glob local del directorio del hotel; `REVIEW_INPUT_ABSENT` es INFO
por decision escrita; y el fallback `legacy-ancestor-walk` sigue vivo donde no hay manifiesto, declarado en
el reporte en vez de silencioso.

"""

ANALISIS_10 = """## FASE-E (2026-10-06) — ACs, lo medido y seguimientos

**AC9 VERIFICADO OFFLINE.** El lector nuevo publica READ_OK (con vacio valido), ABSENT, READ_ERROR y
NO_LEIDO siempre con `cause`; un paquete ilegable no devuelve favorable. Sobre baseline real
(`output/TAREA7-2026-09-19/`) con skip visible si falta.

**AC10 VERIFICADO OFFLINE.** `IMPLEMENTATION_ORDER.md` leido del ZIP que escribio `DeliveryPackager.write()`:
tareas con `### N.`, rutas `ASSETS/` que existen como miembros, manifiesto igual al `namelist()` y el asset
nuevo de B (`whatsapp_setup_guide.md`) con su ruta real. Estado de F-P4.1 revalidado con mutacion (M5): la
derivacion por `dest` sigue vigente y **no** es cierto que el writer entregue siempre un stub — pero tampoco
siempre un orden: sin assets planificados el miembro no existe (medido). El rojo extra de F-P4.9 tambien:
despues de `suppress()` el hash y el conteo vuelven None con error declarado.

**AC11 VERIFICADO OFFLINE.** `review_input_manifest.json` con run_id, fuente original, sha256, tamano,
momento, `read_status` y `disposition=retained_by_gate`; Juez y cuatro Bots consumen el resolvedor (AST en
la ruta de produccion); la retencion leida no suma hallazgo; lo nunca generado sigue ABSENT; documento
declarado e inalcanzable es NO_LEIDO, jamas lista vacia. Snapshot y manifiesto fuera del paquete:
comprobado con el writer real y con dos mutantes de guard (M6, M7).

**AC12 VERIFICADO OFFLINE.** Par permitir/bloquear sobre acta real (`ActaWriter` + `publish`/`suppress`):
`enforcement` y `package_evidence` (sha256 + member_count) en las dos ramas. `_compute_verdict` y los
contratos de cuarentena intactos, con prueba de paridad.

**Lecciones aplicadas (efectivas, no declarativas).** L-VUP-5: el writer ya verde se revalido por mutacion y
no se reimplemento. L-V.1: contenido y layout se midieron en el ZIP del writer, no en un MD fabricado.
L-NC10: el orden publicado se cotejo miembro por miembro contra el manifiesto y el `namelist()`. L-PF6:
`NO_LEIDO` existe precisamente porque "no lo alcance" no es "no existe".

**Leccion nueva (L-E-ESC, formulada al medir).** *Un guard de exclusion no se prueba contra la ruta que el
mismo construye.* El primer verde de la no-filtracion cotejaba el nombre del archivo contra la ruta dentro
del ZIP (`ASSETS/v4_audit/review_input_manifest.json`), y pasaba con el guard apagado: la exclusion funciona
por `Path.name`, asi que la asercion debia comparar `Path(miembro).name`. Un mutante lo demostro (M7 paso de
EXIT=0 a EXIT=1 solo al corregir el test, no el producto).

**Seguimientos abiertos por E.** (1) anclar por run_id los JSON timestamped — dueno FASE-H, contraste
VERIFY; (2) decidir si ABSENT de un insumo obligatorio debe subir de INFO — dueno VERIFY; (3) el fallback
`legacy-ancestor-walk` debe retirarse cuando H/E2E garanticen manifiesto en toda corrida — dueno H/E2E.

"""

CHANGELOG_E = """## [Sin publicar] - FASE-E del plan REFACTOR-WHATSAPP-ENTREGA-2026-09-18 - 2026-10-06

### Entrega real revalidada y revision con snapshot interno (AC9-AC12)

**Que cambio.** Nuevo `modules/quality_gates/tribunal/review_inputs.py`: copia interna **no exportable** de
diagnostico y propuesta tomada **antes** de que `run_v4_complete_mode` las borre, manifiesto
`review_input_manifest.json` (run_id, ruta original, ruta interna, sha256, tamano, momento, `read_status`,
`disposition`) y el **resolvedor unico** que ahora consultan el Juez y los cuatro Bots.
`whatsapp_contract.py` sumo `READ_NOT_READ = "NO_LEIDO"` al vocabulario designado.
`artifact_paths.resolve_latest` acepta `explicit=`: si la ruta del run esta declarada y no existe, devuelve
None en vez de elegir el mtime de otro hotel. `delivery_packager.py` excluye `review_input_manifest*` por
nombre y corta `_review_inputs` por nombre de directorio; `write`/`publish`/`suppress` quedan intactos.
`main.py` congela los insumos antes del borrado (gobierno por AST) y pasa el resolvedor al Juez y a los
cuatro Bots; el borrado dejo de resolver rutas por `locals()`.

**Por que.** F-P4.2 medida: el verdadero defecto no era el borrado sino que `DiagnosisReviewer` y
`AssetReviewer` resolvian con globs propios y, ante insumo no alcanzado, `_check_pain_traceability`
devolvia la lista vacia: verde silencioso mientras `artifacts_read` declaraba el patron. Y en regimen
ZIP-only nadie leia `MANIFEST.json` (L-E2E.1), porque se buscaba en un directorio descomprimido que el
flujo ya no produce.

**Evidencia.** `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E/`: `resultados-y-observaciones.md`,
`tests_baseline_pre.txt` (290 passed / 9 skipped / EXIT 0), `tests_baseline_post.txt` (321 passed /
9 skipped / EXIT 0), `mutation_report.json` (8/8 rojos por su guard, arbol intacto por sha256),
`mutaciones_crudo.txt`, `quick_pre.txt` (12/13, rojo de derivado) y `quick_final.txt` (13/13). 31 funciones
nuevas en `tests/quality_gates/tribunal/test_fase_e_snapshot_resolvedor.py`. Ninguna prueba corrio
`main.py v4complete`; contador 0/1.

**Veredicto.** AC9/AC10/AC11/AC12 VERIFICADO OFFLINE. Deuda declarada con dueno: anclar por run_id los
JSON timestamped del resto de insumos (FASE-H), severidad de `REVIEW_INPUT_ABSENT` (VERIFY) y retiro del
fallback `legacy-ancestor-walk` (H/E2E). Sin commit, sin push, sin DOMAIN_PRIMER (checkpoint).

"""

GUIA_E = """## Nota Técnica — FASE-E del plan REFACTOR-WHATSAPP-ENTREGA-2026-09-18 (2026-10-06)

**Capa afectada:** `modules/quality_gates/tribunal/` (nuevo `review_inputs.py`, los cuatro revisores,
`judge.py`, `artifact_paths.py`), `modules/delivery/delivery_packager.py`, `main.py` (rama de gate blocking)
y `modules/data_validation/whatsapp_contract.py`.

**Regla operativa nueva.** Los insumos que el Tribunal necesita leer se congelan **antes** de cualquier
borrado del gate y se referencian por `run_id`. Quien agregue un documento revisable debe:

1. registrarlo en `review_inputs.KIND_PATTERNS` y `KIND_ORDER`, no abrir un glob propio en el revisor;
2. consumir `ReviewInputs.read_document(kind)` y su `read_status` — `READ_OK`/`ABSENT`/`READ_ERROR`/
   `NO_LEIDO`, con `cause` obligatoria;
3. si el pipeline retira el documento del arbol cliente, estampar `disposition=retained_by_gate` y NO
   contarlo como hallazgo nuevo; lo nunca generado queda `ABSENT`.

**Límite interno/cliente.** El snapshot vive en `output/<corrida>/_review_inputs/<run_id>/`, hermano del
directorio del hotel y por tanto fuera del `rglob` que empaqueta `DeliveryPackager`. La exclusion tiene dos
cortes (nombre de archivo `review_input_manifest*` y segmento de directorio `_review_inputs`) y **se prueba
con el writer real**, leyendo `namelist()`; el guard por nombre se coteja contra `Path(miembro).name`, no
contra la ruta dentro del ZIP.

**Lo que no se toco.** `TribunalJudge._compute_verdict`, la tabla de cláusulas, `blocks_delivery_zip` y los
contratos `write`/`publish`/`suppress`. Hay una prueba de paridad que lo verifica.

**Instrumento.** `./venv/Scripts/python.exe -m pytest tests/delivery tests/quality_gates/tribunal
tests/test_p6r_full_flow_matrix.py tests/test_ac_g1_implementation_order.py
tests/quality_gates/test_fase_d_veredicto_canonico.py -q` y
`./venv/Scripts/python.exe evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E/run_mutations.py`.

"""

SELECCION = """# FASE-E — seleccion pertinente de pruebas (misma unidad en PRE y POST)
# Comando canonico:
#   ./venv/Scripts/python.exe -m pytest <estas cinco rutas> -q
# Entorno: Python 3.13 del venv del repo, cwd = raiz del repo, Git Bash bajo Windows.
# Funciones canonicas de la seleccion en el PRE: 293 (299 casos collectados; 6 de parametrizacion).
tests/delivery
tests/quality_gates/tribunal
tests/test_p6r_full_flow_matrix.py
tests/test_ac_g1_implementation_order.py
tests/quality_gates/test_fase_d_veredicto_canonico.py
"""


def reemplazar(ruta: Path, old: str, new: str, esperado: int) -> None:
    texto = ruta.read_text(encoding="utf-8")
    vistos = texto.count(old)
    if vistos != esperado:
        raise SystemExit(f"ANCLA {ruta.name}: {vistos} ocurrencias, se exigian {esperado} :: {old[:70]!r}")
    ruta.write_text(texto.replace(old, new), encoding="utf-8", newline="")
    print(f"[OK] {ruta.relative_to(ROOT)} :: {esperado} reemplazo(s)")


def main() -> None:
    prompt = PLAN / "05-prompt-inicio-sesion-fase-E.md"
    reemplazar(
        prompt,
        "**Estado:** PENDIENTE. **Dependencia inmediata:** FASE-D completa; verificar cierre real de A–D antes de editar.",
        ESTADO_E,
        1,
    )
    reemplazar(prompt, "- [ ] ", "- [x] ", 6)

    checklist = PLAN / "06-checklist-implementacion.md"
    reemplazar(
        checklist,
        "| E | D cerrada | AC9, AC10, AC11, AC12, AC15 | PENDIENTE | PENDIENTE |",
        "| E | D cerrada | AC9, AC10, AC11, AC12, AC15 | **COMPLETADA 2026-10-06, SIN COMMIT** (mandato sin "
        "autorizacion de commit; los cinco cortes se sostienen sin el). AC9/AC10/AC11/AC12 **VERIFICADOS OFFLINE** "
        "con el writer real y 8/8 mutantes cayendo por su guard. Deuda declarada con dueno: anclar por run_id los "
        "JSON timestamped (H), severidad de `REVIEW_INPUT_ABSENT` (VERIFY) y retiro del fallback "
        "`legacy-ancestor-walk` (H/E2E) | `" + EV + "/`: `resultados-y-observaciones.md`, "
        "`tests_baseline_pre.txt`, `tests_baseline_post.txt`, `mutation_report.json`, `mutaciones_crudo.txt`, "
        "`run_mutations.py`, `seleccion_pertinente.txt`, `quick_pre.txt`, `quick_final.txt` |",
        1,
    )
    reemplazar(
        checklist,
        "| AC10 | E; VERIFY contrasta | IMPLEMENTATION_ORDER dentro del ZIP real contiene tareas, rutas ASSETS existentes, setup/guía y manifiesto coherentes | Revalidar regresión P6-R y asset nuevo; desconectar rutas reales o recuperar stub hace rojo, no certificar por tamaño | PENDIENTE |",
        "| AC10 | E; VERIFY contrasta | IMPLEMENTATION_ORDER dentro del ZIP real contiene tareas, rutas ASSETS existentes, setup/guía y manifiesto coherentes | Revalidar regresión P6-R y asset nuevo; desconectar rutas reales o recuperar stub hace rojo, no certificar por tamaño | **VERIFICADO OFFLINE (E 2026-10-06).** Leido del ZIP de `DeliveryPackager.write()`; rutas `ASSETS/` cotejadas miembro por miembro; M5 (basename en vez de ruta real) cae por su asercion; sin assets planificados el miembro no existe, y tras `suppress()` el hash y el conteo vuelven None con error declarado |",
        1,
    )
    reemplazar(
        checklist,
        "| AC11 | E; VERIFY contrasta | `review_input_manifest.json.documents` contiene run_id, fuente original, hash, ruta interna, read_status y disposition=retained_by_gate cuando corresponda; revisores leen snapshot | Borrado sin snapshot o pérdida de ruta hace rojo; nunca generado sigue ausente; snapshot fuera del árbol exportable | PENDIENTE |",
        "| AC11 | E; VERIFY contrasta | `review_input_manifest.json.documents` contiene run_id, fuente original, hash, ruta interna, read_status y disposition=retained_by_gate cuando corresponda; revisores leen snapshot | Borrado sin snapshot o pérdida de ruta hace rojo; nunca generado sigue ausente; snapshot fuera del árbol exportable | **VERIFICADO OFFLINE (E 2026-10-06).** Manifiesto schema 1.0; Juez y los cuatro Bots consumen `ReviewInputs` (AST en la ruta de produccion); NO_LEIDO curado en el vocabulario de FASE-C; M1/M2/M3/M4/M6/M7/M8 caen por su guard; no-filtracion comprobada con `namelist()` del writer real |",
        1,
    )

    deps = PLAN / "dependencias-fases.md"
    reemplazar(
        deps,
        "| E | D cerrada | **Resolvedor único para los cuatro revisores** (\"no leído\" ≠ OK), ZIP real y snapshot interno revisable sin filtración; AC9–AC12 | 0 | PENDIENTE |",
        "| E | D cerrada | **Resolvedor único para los cuatro revisores** (\"no leído\" ≠ OK), ZIP real y snapshot interno revisable sin filtración; AC9–AC12 | 0 | **COMPLETADA 2026-10-06, SIN COMMIT** — AC9/AC10/AC11/AC12 VERIFICADOS OFFLINE con el writer real y 8/8 mutantes por su guard. Deuda con dueño: JSON timestamped sin ancla de run_id (H), severidad de `REVIEW_INPUT_ABSENT` (VERIFY), retiro de `legacy-ancestor-walk` (H/E2E). Evidencia: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E/` |",
        1,
    )

    doc09 = PLAN / "09-documentacion-post-proyecto.md"
    texto = doc09.read_text(encoding="utf-8")
    doc09.write_text(texto.rstrip() + "\n\n" + CIERRE_09, encoding="utf-8", newline="")
    print(f"[OK] {doc09.relative_to(ROOT)} :: seccion de FASE-E agregada")

    doc10 = PLAN / "10-analisis-post-implementacion.md"
    reemplazar(doc10, "## Métricas de ejecución", ANALISIS_10 + "## Métricas de ejecución", 1)

    changelog = ROOT / "CHANGELOG.md"
    reemplazar(
        changelog,
        "## [Sin publicar] - FASE-D del plan REFACTOR-WHATSAPP-ENTREGA-2026-09-18 - 2026-10-06",
        CHANGELOG_E + "## [Sin publicar] - FASE-D del plan REFACTOR-WHATSAPP-ENTREGA-2026-09-18 - 2026-10-06",
        1,
    )

    guia = ROOT / "docs" / "GUIA_TECNICA.md"
    texto = guia.read_text(encoding="utf-8")
    guia.write_text(texto.rstrip() + "\n\n" + GUIA_E, encoding="utf-8", newline="")
    print(f"[OK] {guia.relative_to(ROOT)} :: nota tecnica de FASE-E agregada")

    (ROOT / EV / "seleccion_pertinente.txt").write_text(SELECCION, encoding="utf-8", newline="\n")
    print("[OK] seleccion_pertinente.txt")


if __name__ == "__main__":
    main()
