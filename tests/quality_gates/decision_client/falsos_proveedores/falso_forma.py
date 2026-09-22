"""Proveedor **FALSO** que cumple la forma: material de prueba de FASE-B, no toca el arbol de
produccion ni abre un socket.

Existe para que AC8 fije la **forma** de una respuesta sin pinear literales de un proveedor real
(L-V2.3), y para que AC9 pueda medir cuanto cuesta anadir un proveedor sin conectar ninguno.

Que NO hace: no importa SDK ni adapter alguno, no lee credenciales, no llama a la red. Sus numeros
son fijos y derivados de la pregunta, no una opinion.
"""

from __future__ import annotations

PROVEEDOR = {
    "nombre": "falso-forma",
    "falso": True,
    "credencial_env": None,
    "modelo": "falso-forma-0.1",
    "eleccion": "primera",
    "nota": "determinista por indice de opcion; ver `falso-ilegible` para el camino de fallo",
}


def evaluar(state, preguntas):
    """Contesta las tres formas del contrato: choice, score y noul."""
    respuestas = []
    for p in preguntas:
        if p.tipo == "choice":
            e = p.opciones[0]
            n = len(p.opciones)
            resto = round((1.0 - 0.7) / (n - 1), 6) if n > 1 else 0.0
            probs = {o: (0.7 if o == e else resto) for o in p.opciones}
            respuestas.append({"pregunta_id": p.id, "tipo": "choice", "eleccion": e,
                               "probabilidades": probs, "confidence": 0.91})
        elif p.tipo == "score":
            nivel = 1 if len(p.leyenda) > 1 else 0
            respuestas.append({"pregunta_id": p.id, "tipo": "score", "nivel": nivel,
                               "leyenda": p.leyenda[nivel], "confidence": 0.83})
        else:
            respuestas.append({"pregunta_id": p.id, "tipo": "noul", "probabilidad_si": 0.68})
    return {"modelo": PROVEEDOR["modelo"], "respuestas": respuestas,
            "usage": {"input_tokens": 120, "output_tokens": 34}, "request_id": "falso-req-1"}
