"""Proveedor **FALSO** que contesta fuera de forma: provocador del estado `ILEGIBLE` (AC7).

Rompe dos cosas a la vez, cada una con su motivo publicable:
  * una `choice` sin `confidence` - sin ella no se puede separar «actue» de «no estoy seguro»;
  * una pregunta que se queda sin respuesta - el drop silencioso que la familia de AC12 prohíbe.

Tampoco este abre red ni lee credenciales.
"""

from __future__ import annotations

PROVEEDOR = {
    "nombre": "falso-ilegible",
    "falso": True,
    "credencial_env": None,
    "modelo": "falso-ilegible-0.1",
    "nota": "devuelve choice sin confidence y deja la ultima pregunta sin responder",
}


def evaluar(state, preguntas):
    respuestas = []
    for p in preguntas[:-1]:
        if p.tipo == "choice":
            e = p.opciones[0]
            respuestas.append({"pregunta_id": p.id, "tipo": "choice", "eleccion": e,
                               "probabilidades": {o: (1.0 if o == e else 0.0) for o in p.opciones}})
        elif p.tipo == "score":
            respuestas.append({"pregunta_id": p.id, "tipo": "score", "nivel": 0,
                               "leyenda": p.leyenda[0], "confidence": 0.5})
        else:
            respuestas.append({"pregunta_id": p.id, "tipo": "noul", "probabilidad_si": 0.5})
    return {"modelo": PROVEEDOR["modelo"], "respuestas": respuestas,
            "usage": None, "request_id": None}
