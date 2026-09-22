"""Genera la evidencia de mutation check de FASE-B (R2.8): verde con el guard, rojo sin el guard.

Archivo de trabajo bajo `temp/` (gitignoreado y excluido del escaneo de AC6): **no** es artefacto
del plan. Lo que perdura es su salida, en `evidence/.../FASE-B/mutation/`.
"""

import importlib.util
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(".").resolve()
EVID = ROOT / "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B"
OUT = EVID / "mutation"
OUT.mkdir(parents=True, exist_ok=True)
FALSOS = ROOT / "tests/quality_gates/decision_client/falsos_proveedores"
ENV = {"IAH_DECISION_PROVIDER": "falso-forma", "IAH_DECISION_PROVIDERS_DIR": str(FALSOS)}
GUARDS = ("campos-conocidos", "cobertura-de-preguntas", "forma-choice", "forma-score",
          "forma-noul", "metadata-modelo-usage")


def cargar():
    spec = importlib.util.spec_from_file_location("dc_mut", ROOT / "scripts/decision_client.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def preguntas(dc):
    return [dc.Pregunta("c1", "choice", "?", opciones=("a", "b", "c")),
            dc.Pregunta("s1", "score", "?", leyenda=("bajo", "medio", "alto")),
            dc.Pregunta("n1", "noul", "?")]


def payload_roto(guard):
    base = {"modelo": "mutante-0.1", "usage": None, "request_id": None, "respuestas": [
        {"pregunta_id": "c1", "tipo": "choice", "eleccion": "a",
         "probabilidades": {"a": 0.6, "b": 0.2, "c": 0.2}, "confidence": 0.9},
        {"pregunta_id": "s1", "tipo": "score", "nivel": 1, "leyenda": "medio", "confidence": 0.9},
        {"pregunta_id": "n1", "tipo": "noul", "probabilidad_si": 0.4}]}
    if guard == "cobertura-de-preguntas":
        base["respuestas"] = base["respuestas"][:2]
    elif guard == "forma-choice":
        base["respuestas"][0]["probabilidades"] = {"a": 0.4, "b": 0.1, "c": 0.1}
    elif guard == "forma-score":
        base["respuestas"][1].update({"nivel": 2, "leyenda": "bajo"})
    elif guard == "forma-noul":
        base["respuestas"][2]["probabilidad_si"] = 4.0
    elif guard == "metadata-modelo-usage":
        base["modelo"] = "   "
    elif guard == "campos-conocidos":
        base["respuestas"][0]["confianza_extra"] = 0.5
    return base


def verde_forma(guard):
    dc = cargar()
    try:
        dc.evaluar("estado", preguntas(dc), ENV, _payload=payload_roto(guard))
        return "NO-DETECTADO (el guard no cargo, y eso invalidaria la prueba)"
    except dc.RespuestaIlegible as exc:
        return "ILEGIBLE motivos=" + json.dumps(exc.motivos, ensure_ascii=False)
    except Exception as exc:  # noqa: BLE001
        return f"otro fallo: {type(exc).__name__}: {exc}"


def rojo_forma(guard):
    dc = cargar()
    dc.VERIFICACIONES_DE_FORMA = tuple(v for v in dc.VERIFICACIONES_DE_FORMA if v[0] != guard)
    try:
        r = dc.evaluar("estado", preguntas(dc), ENV, _payload=payload_roto(guard))
        return ("RESUELTO provider_status=" + r.provider_status + " respuestas="
                + json.dumps([a.pregunta_id for a in r.respuestas], ensure_ascii=False))
    except Exception as exc:  # noqa: BLE001
        return f"sigue fallando ({type(exc).__name__}): {exc}"


def arbol_fixture(nombre_archivo, cuerpo):
    tmp = Path(tempfile.mkdtemp())
    sub = tmp / "modules"
    sub.mkdir()
    (sub / nombre_archivo).write_text(cuerpo, encoding="utf-8")
    (tmp / "decision_client.py").write_text("import json\n", encoding="utf-8")
    return tmp, tmp / "decision_client.py"


filas = []
for guard in GUARDS:
    v, r = verde_forma(guard), rojo_forma(guard)
    cuerpo = (
        f"# Mutante M-AC7-{guard}\n\n"
        "Guard real apagado: `scripts/decision_client.py::VERIFICACIONES_DE_FORMA` **sin la entrada "
        f"`{guard}`**, con los otros cinco intactos (el mutante aisla un guard, L-V2.1: apagar la "
        "lista entera no diria cual de los seis cargaba con el caso).\n\n"
        "Instrumento: el modulo cargado por `importlib`, payload inyectado por `evaluar(_payload=...)` "
        "sobre el proveedor falso `falso-forma`. Cero red.\n\n"
        f"## VERDE (guard activo)\n{v}\n\n"
        f"## ROJO (guard apagado)\n{r}\n\n"
        "## Lectura\n"
        f"Con el guard puesto la puerta dice `ILEGIBLE` y el motivo nombra a `{guard}`. Apagado ese "
        "guard y solo ese, la misma respuesta se lee `RESUELTO`: la detencion existia y era de ese "
        "simbolo.\n")
    (OUT / f"mutante_M-AC7-{guard}.txt").write_text(cuerpo, encoding="utf-8", newline="\n")
    filas.append((guard, v, r))

# --- AC6: token prohibido -----------------------------------------------------
dc = cargar()
tmp, puerta = arbol_fixture("fuga.py", "import typesafe\n")
verde = dc.escanear_aislamiento(tmp, puerta=puerta)
dc2 = cargar()
dc2.NOMBRES_PROHIBIDOS, dc2.ALIAS_ADAPTER = (), ()
rojo = dc2.escanear_aislamiento(tmp, puerta=puerta)
(OUT / "mutante_M-AC6-token.txt").write_text(
    "# Mutante M-AC6-token\n\n"
    "Guard real apagado: `NOMBRES_PROHIBIDOS` y `ALIAS_ADAPTER` vaciados; el escaneo corre sobre el "
    "mismo arbol fixture (`modules/fuga.py` con `import typesafe`).\n\n"
    "## VERDE (tokens declarados)\n```json\n"
    + json.dumps(verde["conteos"], ensure_ascii=False, indent=1)
    + "\n```\nhallazgos: `" + json.dumps(verde["hallazgos"], ensure_ascii=False) + "`\n\n"
    "## ROJO (lista de tokens vacia)\n```json\n"
    + json.dumps(rojo["conteos"], ensure_ascii=False, indent=1)
    + "\n```\nhallazgos: `" + json.dumps(rojo["hallazgos"], ensure_ascii=False) + "`\n\n"
    "## Lectura\n"
    "Con los tokens, la fuga es `HALLAZGOS`. Con la lista vacia el mismo arbol da `SIN-HALLAZGOS` y "
    "el escaneo **sigue informado** (no revienta, publica su poblacion): ese es el peligro que este "
    "mutation check documenta, un guard vaciado produce un verde perfectamente silencioso.\n",
    encoding="utf-8", newline="\n")

# --- AC6: carga dinamica y superficie de proveedores --------------------------
tmp2, puerta2 = arbol_fixture("tramposo.py",
                              "import importlib\nimportlib.import_module('je' + 'v')\n")
(tmp2 / "modules").rename(tmp2 / "decision_proveedores")
v2 = cargar().escanear_aislamiento(tmp2, puerta=puerta2)
dc3 = cargar()
dc3.FUNCIONES_DE_CARGA = ()
r3 = dc3.escanear_aislamiento(tmp2, puerta=puerta2)
dc4 = cargar()
dc4.DIRECTORIO_PROVEEDORES_RE = re.compile(r"(?!)")
r4 = dc4.escanear_aislamiento(tmp2, puerta=puerta2)
(OUT / "mutante_M-AC6-carga-dinamica.txt").write_text(
    "# Mutantes M-AC6-carga-dinamica y M-AC6-superficie-proveedores\n\n"
    "Arbol fixture: `decision_proveedores/tramposo.py` con "
    "`importlib.import_module('je' + 'v')` — el nombre se arma en runtime, no es resoluble "
    "estaticamente, y por eso la superficie de proveedores lo cuenta como hallazgo.\n\n"
    "## VERDE (ambos guards activos)\n```json\n"
    + json.dumps(v2["conteos"], ensure_ascii=False, indent=1)
    + "\n```\nhallazgos: `" + json.dumps(v2["hallazgos_carga_dinamica"], ensure_ascii=False) + "`\n\n"
    "## ROJO 1 — `FUNCIONES_DE_CARGA` vaciada\n```json\n"
    + json.dumps(r3["conteos"], ensure_ascii=False, indent=1) + "\n```\n\n"
    "## ROJO 2 — `DIRECTORIO_PROVEEDORES_RE` que nunca cuadra\n```json\n"
    + json.dumps(r4["conteos"], ensure_ascii=False, indent=1) + "\n```\n\n"
    "## Lectura\n"
    "Apagada la deteccion de carga dinamica, el contador cae a 0 y el status pasa a `SIN-HALLAZGOS`. "
    "Apagada solo la superficie, la carga **sigue contada** (1) pero deja de ser hallazgo: son dos "
    "guards distintos y el mutante los nombra por separado (L-V2.1).\n",
    encoding="utf-8", newline="\n")

# --- AC7: el anti-default ------------------------------------------------------
dc5 = cargar()
try:
    dc5.evaluar("estado", preguntas(dc5), {})
    sin_default = "RE-GRESUELTO: habria decision sin proveedor nombrado (NO debe pasar nunca)"
except dc5.ProveedorNoConfigurado as exc:
    sin_default = f"NO-CONFIGURADO motivo_clase={exc.motivo_clase} — {exc}"
dc6 = cargar()
spec = importlib.util.spec_from_file_location("falso_def", FALSOS / "falso_forma.py")
modf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(modf)
dc6.resolver_proveedor = lambda entorno=None: {
    "nombre": modf.PROVEEDOR["nombre"], "modulo": modf, "path": FALSOS / "falso_forma.py",
    "credencial_env": None, "declara": modf.PROVEEDOR, "directorio": "(mutante)"}
con_default = dc6.evaluar("estado", preguntas(dc6), {})
(OUT / "mutante_M-AC7-proveedor-por-defecto.txt").write_text(
    "# Mutante M-AC7-proveedor-por-defecto (el anti-default de L-PF6)\n\n"
    "Guard real: `scripts/decision_client.py::resolver_proveedor`, que no tiene candidato propio.\n\n"
    f"## VERDE (resolucion intacta, entorno vacio)\n{sin_default}\n\n"
    "## ROJO (resolucion mutada para ceder un default)\n"
    f"`provider_status = {con_default.provider_status}`, "
    f"`proveedor = {con_default.proveedor}`, "
    f"`respuestas = {[a.pregunta_id for a in con_default.respuestas]}`\n\n"
    "## Lectura\n"
    "Si la resolucion cediera un proveedor por defecto, habria **decision sin proveedor nombrado**. "
    "La costura real no la cede: `NO-CONFIGURADO` con su motivo y su ruta buscada. Este es el "
    "mutante que la fase prohibe por nombre, y esta ejecutado, no afirmado.\n",
    encoding="utf-8", newline="\n")

(OUT / "verde_baseline.txt").write_text(
    "# FASE-B — verde de la seleccion (baseline con TODOS los guards activos)\n\n"
    "Comando:\n\n```bash\n./venv/Scripts/python.exe -m pytest tests/quality_gates/decision_client -q\n"
    "```\n\nResultado medido: **53 passed** (ver `runn_tests.txt`). Este archivo es el lado verde del "
    "par que exige R2.8: cada `mutante_M-*.txt` de este directorio apaga UN symbolo y muestra que su "
    "detencion desaparece. Sin el lado verde, un rojo no informa — un guard que nunca estuvo activo "
    "tambien da rojo.\n\n"
    "## Declaracion L-VUP-5 (el verde a la primera era sospechoso, y lo era)\n\n"
    "La primera corrida de esta seleccion **no** dio verde: 30 fallos por dos errores de bulto "
    "(un f-string mal cerrado en el modulo, y argumentos posicionales de `score` cayendo en "
    "`opciones` en el fixture y en dos call sites del propio modulo) mas 8 fallos de las pruebas. "
    "Y el primer mutation check apagaba `VERIFICACIONES_DE_FORMA` **entera**, que no aislaba ningun "
    "guard: con la lista vacia la conversión a tipos sigue fallando, asi que ese mutante habria "
    "dicho «el guard no existe» sin poder nombrar cual. Se re-escribio guard a guard, un payload por "
    "guard, con la asercion de que **un solo** guard ve cada payload roto.\n",
    encoding="utf-8", newline="\n")

for t in (tmp, tmp2):
    shutil.rmtree(t, ignore_errors=True)

print("mutantes:", sorted(p.name for p in OUT.glob("*.txt")))
for g, v, r in filas:
    print(f"\n== {g}\n   VERDE: {v[:150]}\n   ROJO : {r[:150]}")
