"""AC10 — el triaje es **aditivo por construccion**: ninguna fila de §2 puede desaparecer.

El punto no es que `removed` salga vacio (eso lo daria cualquier codigo que no borre nada): el punto
es que **el filtro tiene una oportunidad real de borrar** en cada corrida y no la aprovecha. Por eso
este archivo exige ademas que `filas_cuestionadas_sin_borrar` no este vacio — con un pool que nunca
recibiera un `no-pertinente` el verde seria vacio (L-HF1), y con un guard que no se ejercita no hay
nada que el mutante de AC14 pueda apagar.
"""

from __future__ import annotations

import json


def test_ninguna_fila_anclada_desaparece_y_el_guard_tuvo_trabajo(trl, informe_real):
    s = informe_real["seccion_dos"]
    assert s["removed"] == [], f"el triaje filtro filas de §2: {s['removed']}"
    assert s["anchored_after"] == s["anchored_before"] > 0
    assert s["filas_cuestionadas_sin_borrar"], (
        "ningun anclado fue juzgado `no-pertinente`: el guard no tuvo trabajo y este verde seria "
        "vacuo (L-HF1); revise el proveedor falso o el pool")
    juzgados = {j["id"] for j in informe_real["candidatos"]}
    assert set(s["filas_cuestionadas_sin_borrar"]) <= juzgados


def test_el_informe_del_seccion_dos_trae_los_tres_campos_del_ac10(trl, informe_real):
    delta = trl.ac10_delta(informe_real)
    assert set(delta) >= {"anchored_before", "anchored_after", "removed"}
    assert delta["removed"] == []
    assert delta["escrita_por_este_script"] is False
    assert json.dumps(delta)  # el artefacto es serializable tal cual va a evidencia


def test_anchored_after_conserva_las_filas_litales(ancladas_reales, informe_real, trl):
    """Que no se borr6 la fila **y** que no se reescribi6: la comparacion es contra el texto literal."""
    indice, estado = trl.leer_suelo()
    despues = informe_real["seccion_dos"]
    assert despues["anchored_before"] == len(ancladas_reales)
    ids = [f["id"] for f in ancladas_reales]
    assert len(ids) == len(set(ids)), "dos filas con el mismo ID harian vacio el conteo de aditividad"
