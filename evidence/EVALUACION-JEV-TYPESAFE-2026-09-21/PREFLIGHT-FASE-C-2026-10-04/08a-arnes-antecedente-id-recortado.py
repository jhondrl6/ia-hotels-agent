"""Arnes del antecedente y del diente del id recortado (SESION 2.5 / Cierre A).

Carga el brazo desde una revision fija (`git show <rev>:...` volcado a un temporal) o desde el
arbol vigente, y le pasa por su propia costura `transporte` los tres casos que importan:

* `sonda:1` preguntado, `1` devuelto  -> el caso medido en la deuda (fila 2, 3 de 3 envios);
* `pert:L-R.1` preguntado, `L-R.1` devuelto -> la forma del triaje, con prefijo largo;
* `a:1` y `b:1` preguntadas, `1` devuelto -> el recorte ambiguo, donde emparejar seria adivinar.

No imprime credenciales: el transporte es inyectado y la clave es sintetica.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUTA_BRAZO = "scripts/proveedores/deepseek.py"
CLAVE_SINTETICA = "sk-sintetica-de-test-que-no-es-una-credencial"


def _cargar(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def puerta():
    return _cargar("decision_client_sesion25", ROOT / "scripts" / "decision_client.py")


def brazo(rev: str | None) -> Path:
    """El archivo que se va a cargar: el blob de la revision fija o el arbol vigente."""
    destino = ROOT / "temp" / "sesion25-2026-10-04" / ("brazo-%s.py" % (rev or "arbol"))
    if rev is None:
        src = ROOT / RUTA_BRAZO
        destino.write_bytes(src.read_bytes())
        return destino
    crudo = subprocess.run(["git", "show", f"{rev}:{RUTA_BRAZO}"], cwd=ROOT,
                           capture_output=True, check=True).stdout
    destino.write_bytes(crudo)
    return destino


class P:
    """Replica minima de `Pregunta` para no depender de la puerta en el arnes."""

    def __init__(self, id, tipo, enunciado, opciones=(), leyenda=()):
        self.id, self.tipo, self.enunciado = id, tipo, enunciado
        self.opciones, self.leyenda = tuple(opciones), tuple(leyenda)


def _envuelve(respuestas) -> dict:
    """El envelope real de un chat-completion: el JSON vive dentro de choices[0].message.content."""
    return {"id": "cmpl-arnes", "model": "deepseek-flash",
            "usage": {"prompt_tokens": 138, "completion_tokens": 36},
            "choices": [{"finish_reason": "stop",
                         "message": {"content": json.dumps({"respuestas": respuestas})}}]}


def caso(mod, nombre, preguntas, respuestas):
    def transporte(request):
        return _envuelve(respuestas)

    payload = mod.evaluar("estado del plan", preguntas, transporte=transporte,
                          entorno={"DEEPSEEK_API_KEY": CLAVE_SINTETICA})
    dc = puerta()
    salida = {"caso": nombre,
              "preguntas": [p.id for p in preguntas],
              "devuelto_por_el_servicio": [r.get("pregunta_id") for r in respuestas],
              "respuestas": payload["respuestas"],
              "cantidad": len(payload["respuestas"])}
    try:
        dc.validar_payload(payload, preguntas, "deepseek-comparador")
        salida["puerta"] = "VALIDA"
    except dc.RespuestaIlegible as exc:
        salida["puerta"] = "ILEGIBLE"
        salida["motivos"] = exc.motivos
    return salida


def main() -> int:
    rev = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != "-" else None
    mod = _cargar("deepseek_arnes_sesion25", brazo(rev))
    casos = [
        caso(mod, "sonda-recortada", [P("sonda:1", "noul", "Sigues vigente?")],
             [{"pregunta_id": "1", "tipo": "probabilidad_si", "probabilidad_si": 1.0}]),
        caso(mod, "triaje-recortado",
             [P("pert:L-R.1", "choice", "Cual?",
                opciones=("pertinente", "no_pertinente", "insuficiente"))],
             [{"pregunta_id": "L-R.1", "tipo": "choice", "eleccion": "pertinente",
               "probabilidades": {"pertinente": 0.7, "no_pertinente": 0.2, "insuficiente": 0.1},
               "confidence": 0.7}]),
        caso(mod, "recorte-ambiguo",
             [P("a:1", "noul", "Primera?"), P("b:1", "noul", "Segunda?")],
             [{"pregunta_id": "1", "probabilidad_si": 0.5}]),
        caso(mod, "score-recortado",
             [P("triage:L-R.4", "score", "Que nivel?",
                leyenda=("nada", "parcial", "completo"))],
             [{"pregunta_id": "L-R.4", "nivel": 2, "leyenda": "completo", "confidence": 0.6}]),
    ]
    print(json.dumps({"revision": rev or "arbol-de-trabajo",
                      "ruta_cargada": str(brazo(rev)).replace(str(ROOT), ""),
                      "casos": casos}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
