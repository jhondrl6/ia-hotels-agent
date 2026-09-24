"""AC11, primera causa — `AUSENTE`: no hay archivo en la ruta buscada.

`AUSENTE` tiene que decir **la ruta** y **el comando de regeneracion**, y no puede degenerar en «sin
candidatos» ni en `LECTOR-FALLIDO` (R2.9: tres causas, ninguna colapsable).
"""

from __future__ import annotations

import pytest


def test_ausente_imprime_ruta_y_comando(trl, tmp_path):
    ruta = tmp_path / "no-esta" / "lecciones_index.json"
    assert not ruta.exists()
    estado = trl.comprobar_frescura(ruta)
    assert estado["index_status"] == "AUSENTE"
    assert str(ruta) in estado["ruta_buscada"]
    assert "build_lesson_index.py" in estado["comando_regeneracion"]
    assert estado["index_status"] != "LECTOR-FALLIDO"


def test_ausente_no_es_sin_candidatos(trl, tmp_path):
    ruta = tmp_path / "lecciones_index.json"
    with pytest.raises(trl.SueloNoLeible) as exc:
        trl.leer_suelo(ruta)
    informe = trl.informe_suelo_no_leible("PLAN-CUALQUIERA", exc.value.estado, exc.value.payload)
    texto = repr(informe).lower()
    assert informe["index_status"] == "AUSENTE"
    assert informe["candidatos"] is None, "una ausencia no se publica como lista vacia de candidatos"
    assert "sin candidatos" not in texto.replace("«sin candidatos»", "")
    assert "NO es" in informe["nota"] and "sin candidatos" in informe["nota"]


def test_salida_del_main_es_distinta_para_ausente(trl, tmp_path, capsys):
    rc = trl.main(["--plan", "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20",
                   "--index-json", str(tmp_path / "ausente.json")])
    salida = capsys.readouterr().out
    assert rc == 2, f"AUSENTE debe salir con exit 2, salio {rc}"
    assert "[AUSENTE]" in salida and "regenerar" in salida
