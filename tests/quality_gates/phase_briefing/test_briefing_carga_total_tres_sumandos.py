"""AC20 — la carga total se publica con **sus tres sumandos** y la resta comprobada.

El contrato §Carga total y frescura del pack cierra dos trampas que la fila `CONTEXTO/D` de la
orden de calidad nombra:

* **concatenar no es ahorrar**: unir N documentos en uno no baja la suma de sus bytes (suele
  subirla: encabezado, procedencia al pie, `no_incluye[]`). El unico ahorro atribuible al pack
  es lo que **no** entro porque no se declaro, y se publica con su omision.
* **la resta va entre cargas totales**, no entre «fuentes» y «pack». Cada lado trae
  `workflow_obligatorio`, `coste_de_generacion` y `pack_consumido`.

Por eso aqui no se afirme una cifra: se afirme la **identidad** de la resta
(`delta == omitido - andamiaje - coste`) y que los bytes coinciden con `stat -c %s` sobre las
rutas publicadas, recalculados por el test de forma independiente.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PLAN = ROOT / ".opencode" / "plans" / "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
WORKFLOW = ".agents/workflows/phased_project_executor.md"
SUMANDOS = ("workflow_obligatorio", "coste_de_generacion", "pack_consumido")


def _carga(bpb, tmp_path) -> tuple[dict, Path]:
    destinos = tmp_path / "briefing"
    paquetes, _ = bpb.generar(PLAN, destinos, ROOT)
    return bpb.render_carga(paquetes, PLAN, destinos, ROOT), destinos


def _bytes(ruta: str) -> int:
    return os.stat(ROOT / ruta).st_size


def test_por_fase_los_tres_sumandos_en_los_dos_lados(bpb, tmp_path):
    carga, _ = _carga(bpb, tmp_path)
    assert carga["por_fase"], "sin fases medidas no hay delta que publicar"
    for fase in carga["por_fase"]:
        for lado in ("before", "after"):
            assert set(SUMANDOS) <= set(fase[lado]), (
                f"{fase['fase']}/{lado} sin los tres sumandos: {sorted(fase[lado])}")
            assert fase[lado]["total"] == sum(fase[lado][k] for k in SUMANDOS)
        assert fase["delta_bytes"] == fase["before"]["total"] - fase["after"]["total"]
        assert fase["before"]["coste_de_generacion"] == 0, (
            "antes del pack no hay generacion que costear: un numero ahi es inventado")
        assert fase["before"]["pack_consumido"] == 0


def test_el_workflow_sigue_entrando_en_los_dos_lados(bpb, tmp_path):
    """Si el workflow desapareciera del lado `after`, el pack pareceria un ahorro falso."""
    carga, _ = _carga(bpb, tmp_path)
    n_wf = _bytes(WORKFLOW)
    assert n_wf > 0
    for fase in carga["por_fase"]:
        assert fase["after"]["workflow_obligatorio"] >= n_wf, (
            f"{fase['fase']}: el workflow canonico se conto como ahorrado mientras D3 no lo "
            "rebane")
        assert fase["workflow_canonico_bytes"] == n_wf


def test_los_bytes_cuadran_con_stat_sobre_las_rutas_publicadas(bpb, tmp_path):
    """Mismo comando en los dos lados: `stat -c %s`, recalculado aqui de forma independiente.

    El par pre/post no le dice al lector una cifra: le entrega las rutas y la regla para que él
    mismo la saque. Si la suma de `stat` no cuadra con la del JSON, el numero es ret6rico.
    """
    carga, destinos = _carga(bpb, tmp_path)
    assert carga["method"]["comando_bytes"].startswith("stat -c %s")
    antes_esperado = sum(_bytes(r) for r in carga["rutas_stat"]["before"])
    antes_medido = sum(f["before"]["total"] for f in carga["por_fase"])
    assert antes_esperado == antes_medido, (
        f"stat sobre las rutas publicadas da {antes_esperado} y el JSON dice {antes_medido}")
    despues_esperado = sum(_bytes(r) for r in carga["rutas_stat"]["after"])
    despues_medido = sum(f["after"]["workflow_obligatorio"] + f["after"]["pack_consumido"]
                         for f in carga["por_fase"])
    assert despues_esperado == despues_medido, (
        f"stat da {despues_esperado} y el JSON {despues_medido} (el coste de generar no es un "
        "archivo y por eso no entra en esta suma)")
    for fase in carga["por_fase"]:
        pack = destinos / f"{fase['fase']}.md"
        if pack.is_file():
            assert os.stat(pack).st_size == fase["after"]["pack_consumido"], str(pack)
    assert len(carga["rutas_stat"]["before"]) == carga["rutas_stat"]["cuenta"]["before"]


def test_la_resta_cuadra_con_lo_omitido_menos_el_andamiaje(bpb, tmp_path):
    carga, _ = _carga(bpb, tmp_path)
    for fase in carga["por_fase"]:
        assert fase["resta_comprobada"], (
            f"{fase['fase']}: delta {fase['delta_bytes']} != omitido "
            f"{fase['omitido_declarado_bytes']} - andamiaje "
            f"{fase['andamiaje_del_pack_bytes']} - coste "
            f"{fase['after']['coste_de_generacion']}")
        assert fase["delta_bytes"] == (fase["omitido_declarado_bytes"]
                                       - fase["andamiaje_del_pack_bytes"]
                                       - fase["after"]["coste_de_generacion"])
        assert fase["andamiaje_del_pack_bytes"] >= 0, (
            "el pack pesa menos que lo que copia: la resta no esta midiendo lo mismo")


def test_el_andamiaje_del_pack_se_publica_como_coste(bpb, tmp_path):
    """Un pack grande por su procedencia no puede contarse como ahorro de lectura."""
    carga, _ = _carga(bpb, tmp_path)
    andamiaje = sum(f["andamiaje_del_pack_bytes"] for f in carga["por_fase"])
    omitido = sum(f["omitido_declarado_bytes"] for f in carga["por_fase"])
    assert andamiaje > 0 and omitido > andamiaje, (
        f"andamiaje={andamiaje}, omitido={omitido}: el ahorro declarado deberia superar el coste "
        "propio del pack, y si no lo supera el delta es cero o negativo y se explica igual")
    assert carga["total"]["delta_bytes"] == omitido - andamiaje - sum(
        f["after"]["coste_de_generacion"] for f in carga["por_fase"])


def test_un_delta_negativo_es_resultado_valido_y_se_publica(bpb, plantear, tmp_path):
    """Si el pack sale mas grande que la fuente, el numero sale negativo: no se esconde."""
    caso = plantear(lectura="01-doc.md §1 y el workflow canónico")
    (caso["doc1"]).write_text("## 1. S\n\nx\n", encoding="utf-8", newline="\n")
    destinos = tmp_path / "bp"
    paquetes, _ = bpb.generar(caso["plan_dir"], destinos, caso["raiz"])
    carga = bpb.render_carga(paquetes, caso["plan_dir"], destinos, caso["raiz"])
    fase = carga["por_fase"][0]
    assert fase["delta_bytes"] < 0, (
        f"se esperaba un pack mas caro que la fuente minuscula, y dio {fase['delta_bytes']}")
    assert fase["resta_comprobada"], (
        "un delta negativo debe cerrar con la misma identidad que uno positivo")
    assert "negativo" in carga["method"]["regla"] or "cero" in carga["method"]["regla"]


def test_el_metodo_declara_comando_divisor_y_sumandos(bpb, tmp_path):
    carga, destinos = _carga(bpb, tmp_path)
    m = carga["method"]
    assert m["divisor_tokens"] == 4
    assert "build_phase_briefing.py --plan" in m["comando_generacion"]
    assert set(m["sumandos"]) == set(SUMANDOS)
    for k in SUMANDOS:
        assert len(m["sumandos"][k]) > 40, f"sumando {k} sin definicion legible"
    assert "concatenar" in m["regla"].lower()
    invoc = bpb.invocacion_literal(PLAN, ROOT)
    assert m["comando_generacion"] == invoc
    for fase in carga["por_fase"]:
        pack = destinos / f"{fase['fase']}.md"
        linea = bpb.linea_de_estado({"fase": fase["fase"].split("-")[-1],
                                     "estado": fase["estado"]},
                                    pack if pack.is_file() else None)
        esperado = len(invoc.encode("utf-8")) + len(linea.encode("utf-8"))
        assert fase["after"]["coste_de_generacion"] == esperado, (
            f"{fase['fase']}: el coste de generar no es la invocacion + lo que imprime")
