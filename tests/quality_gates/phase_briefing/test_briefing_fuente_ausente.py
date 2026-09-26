"""AC22 (causa FUENTE-AUSENTE) — si la fuente no existe, el pack **no se emite**.

Es la otra mitad de L-PF6: un lector roto no puede leerse como «no habia nada que incluir».
Aquí la distincion que se prueba es emision: `SECCION-NO-RESUELTA` emite y declara;
`FUENTE-AUSENTE` se niega a emitir, y la prueba de esa negativa es un archivo que **no** esta.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_fuente_ausente_no_emite_el_pack_y_nombre_la_ruta_buscada(bpb, plantear, tmp_path):
    caso = plantear(lectura="01-doc.md §1 y no-hay-nada.md y el workflow canónico")
    destinos = tmp_path / "briefing"
    paquetes, rc = bpb.generar(caso["plan_dir"], destinos, caso["raiz"])
    pack = paquetes[0]
    assert pack["estado"] == "FUENTE-AUSENTE"
    assert rc == 1, "una fuente ausente no puede ser un exito de generacion"
    assert not (destinos / f"FASE-{pack['fase']}.md").exists(), (
        "se emitio un pack a pesar de la fuente ausente: el recorte quedaba silencioso")
    assert not destinos.exists() or list(destinos.iterdir()) == [], (
        "un pack parcial no se escribe ni como subproducto")

    ausente = [f for f in pack["fuentes"] if not f["existe"]]
    assert len(ausente) == 1 and ausente[0]["documento"] == "no-hay-nada.md"
    rutas = " ".join(ausente[0]["rutas_intentadas"])
    assert "no-hay-nada.md" in rutas, (
        f"la causa tiene que imprimir la ruta buscada, no solo 'no existe': {rutas}")


PROMPT_SIN_DECLARAR = "# FASE-X — plantado sin bloque de ejecucion\n\nNada que leer aqui.\n"


def test_la_ausencia_se_distingue_del_vacio(bpb, plantear, tmp_path):
    """Cero lecturas declaradas no es «no hay fuentes»: es un prompt que no declara."""
    caso = plantear(nombre="VACIO", prompt_texto=PROMPT_SIN_DECLARAR)
    paquetes, _ = bpb.generar(caso["plan_dir"], tmp_path / "v", caso["raiz"])
    assert paquetes[0]["declaracion"] == "SIN-DECLARACION"
    assert paquetes[0]["estado"] == "COMPLETO"
    assert paquetes[0]["no_incluye"], "un pack sin contenido debe decir que no incluye nada"
    caso2 = plantear(nombre="AUSENTE", lectura="no-hay-nada.md y el workflow canónico")
    paquetes2, _ = bpb.generar(caso2["plan_dir"], tmp_path / "a", caso2["raiz"])
    assert paquetes2[0]["estado"] == "FUENTE-AUSENTE"
    assert paquetes[0]["estado"] != paquetes2[0]["estado"], (
        "vacio y ausente colapsaron en un mismo estado (L-PF10)")


def test_el_check_no_dice_ok_sobre_cero_fuentes(bpb, plantear, tmp_path, capsys):
    """Un verde sin denominador no informa: 0 fuentes gobernadas se publica como SIN-FUENTES."""
    caso = plantear(nombre="CERO", prompt_texto=PROMPT_SIN_DECLARAR)
    destinos = tmp_path / "c"
    bpb.generar(caso["plan_dir"], destinos, caso["raiz"])
    capsys.readouterr()
    resultados, rc = bpb.verificar(caso["plan_dir"], destinos, caso["raiz"])
    salida = capsys.readouterr()
    assert rc == 0
    assert resultados[0]["sin_fuentes"] is True
    assert "SIN-FUENTES" in salida.err, (
        f"el check llamo OK a una comprobacion que no miro nada: {salida.err}")
    assert "[OK]" not in salida.err
