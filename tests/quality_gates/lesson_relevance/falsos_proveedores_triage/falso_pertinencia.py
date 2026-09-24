"""Proveedor **FALSO** de pertinencia: material de prueba de FASE-C, no toca produccion ni abre socket.

Existe para que la seleccion de C ejercite la **mecanica** del camino (aditividad, estados del suelo,
umbral, destinos de las propuestas) sin conectar un modelo. Sus numeros **no son una opinion**: son
dos ejes deterministas y deliberadamente independientes, y esa independencia es la que permite probar
E1 — que el umbral gobierna `confidence` y no `probabilidad_si`/`por_si`.

* eje A — `por_si`: cuanto se inclina el emisor por la opcion afirmativa, segun `len(id) % 4`.
* eje B — `confidence`: cuan seguro esta de haber leido la pregunta, segun `len(id) % 3`.

Ni `credencial_env` ni red ni SDK. La pregunta de pertinencia es `choice` de **dos** opciones
(`pertinente` / `no-pertinente`), que es la forma que el contrato E1 fija.
"""

from __future__ import annotations

PROVEEDOR = {
    "nombre": "falso-pertinencia",
    "falso": True,
    "credencial_env": None,
    "modelo": "falso-pertinencia-0.1",
    "nota": "determinista por longitud de id; dos ejes independientes a proposito (E1)",
}


def _ejes(id_pregunta: str) -> tuple[float, float]:
    n = len(id_pregunta)
    por_si = 0.90 if n % 4 < 2 else 0.20
    confidence = 0.93 if n % 3 else 0.41
    return por_si, confidence


def evaluar(state, preguntas):
    """Contesta `choice` de dos opciones con sus dos numeros por separado, sin mezclarlos."""
    respuestas = []
    for p in preguntas:
        if p.tipo != "choice":
            raise AssertionError(
                f"falso-pertinencia solo contesta choice de dos opciones; llegaron {p.tipo!r} "
                "(contrato E1: la pregunta de pertinencia no es noul)")
        if len(p.opciones) != 2:
            raise AssertionError(f"se esperaban 2 opciones y llegaron {len(p.opciones)}: {p.opciones}")
        si, no = p.opciones[0], p.opciones[1]
        por_si, confidence = _ejes(p.id)
        respuestas.append({"pregunta_id": p.id, "tipo": "choice",
                           "eleccion": si if por_si >= 0.5 else no,
                           "probabilidades": {si: por_si, no: round(1.0 - por_si, 6)},
                           "confidence": confidence})
    return {"modelo": PROVEEDOR["modelo"], "respuestas": respuestas,
            "usage": {"input_tokens": len(state) // 4, "output_tokens": 12 * len(respuestas)},
            "request_id": "falso-pertinencia-1"}
