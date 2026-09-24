"""AC11, tercera causa — `LECTOR-FALLIDO`: existe, pero revienta al parsear.

Es la causa que la version original del prompt no cubria y la que mas se confunde con las otras dos:
un JSON roto **no** es `AUSENTE` (el archivo esta) ni `VENCIDO` (no se leyo para compararlo) ni, sobre
todo, «sin candidatos». Un lector roto leido como ausencia es L-PF6, y aqui produce un triaje verde
sobre nada.
"""

from __future__ import annotations

import pytest

PLAN = "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"

ROTOS = {
    "no-es-json": '{"lecciones": [',
    "bytes-que-noSon-texto": "\x00\x01\x02 binario",
    "dict-con-lista": '{"lecciones": {"no": "es lista"}, "cobertura": []}',
}


@pytest.mark.parametrize("nombre,contenido", sorted(ROTOS.items()))
def test_json_ilegible_es_lector_fallido_con_su_motivo(trl, tmp_path, nombre, contenido):
    ruta = tmp_path / "lecciones_index.json"
    ruta.write_text(contenido, encoding="utf-8")
    estado = trl.comprobar_frescura(ruta)
    assert estado["index_status"] == "LECTOR-FALLIDO", (
        f"{nombre}: salio {estado['index_status']}; las tres causas no se colapsan (R2.9)")
    assert estado["motivo"], "LECTOR-FALLIDO sin motivo no informa"


def test_lector_fallido_no_es_ausente_ni_vencido_ni_vacio(trl, tmp_path):
    ruta = tmp_path / "lecciones_index.json"
    ruta.write_text("esto no es json en absoluto", encoding="utf-8")
    with pytest.raises(trl.SueloNoLeible) as exc:
        trl.leer_suelo(ruta)
    assert exc.value.estado == "LECTOR-FALLIDO"
    informe = trl.informe_suelo_no_leible(PLAN, exc.value.estado, exc.value.payload)
    assert informe["candidatos"] is None
    assert informe["status"] == "SUELO-LECTOR-FALLIDO"
    assert "sin candidatos" not in repr(informe).replace("«sin candidatos»", "").lower()


def test_el_main_responde_exit_3_y_dice_el_motivo(trl, tmp_path, capsys):
    ruta = tmp_path / "lecciones_index.json"
    ruta.write_text('{"lecciones": [', encoding="utf-8")
    rc = trl.main(["--plan", PLAN, "--index-json", str(ruta)])
    salida = capsys.readouterr().out
    assert rc == 3, f"LECTOR-FALLIDO debe salir con exit 3, salio {rc}"
    assert "[LECTOR-FALLIDO]" in salida
    assert "no es JSON legible" in salida


def test_el_calculo_propio_roto_tambien_es_lector_fallido(trl, indice_real, monkeypatch):
    """Si el generador de la casa no puede calcular, no hay base ni para decir «fresco» ni «vencido»."""
    def explosivo(*a, **kw):
        raise RuntimeError("corpus ilegible")
    mod = trl._generador()
    monkeypatch.setattr(trl, "_generador", lambda: mod)
    monkeypatch.setattr(mod, "build", explosivo)
    estado = trl.comprobar_frescura(indice_real)
    assert estado["index_status"] == "LECTOR-FALLIDO"
    assert estado["subcausa"] == "calculo-en-memoria"
    assert "no hay base" in estado["motivo"]
