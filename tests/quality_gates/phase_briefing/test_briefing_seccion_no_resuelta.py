"""AC22 — seccion declarada y no resuelta es **un estado propio**, no un pack mas corto.

El defecto que esta prueba persigue es el del `except` que devuelve el pack parcial: la fase
leyo un archivo mas corto que lo que pidio y nadie se entero (L-PF6, L-PF10). Aqui el pack
conserva lo que si se resolvio, **nombra la seccion pedida y las rutas intentadas**, y declara
que no esta completo.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MARCA = "[SECCION-NO-RESUELTA]"


def test_la_seccion_no_resuelta_se_declara_con_su_ruta_intentada(bpb, plantear, tmp_path):
    caso = plantear(lectura="01-doc.md §1 y §99 y el workflow canónico")
    destinos = tmp_path / "bp"
    paquetes, rc = bpb.generar(caso["plan_dir"], destinos, caso["raiz"])
    pack = paquetes[0]
    assert pack["estado"] == "SECCION-NO-RESUELTA"
    no_resueltas = [r for f in pack["fuentes"] for r in f["secciones_no_resueltas"]]
    assert no_resueltas == ["99"], (
        f"la seccion pedida y no resuelta debe quedar registrada como referencia, no como "
        f"nombre de seccion inventado: {no_resueltas}")

    ruta_pack = destinos / f"FASE-{pack['fase']}.md"
    assert ruta_pack.is_file(), (
        "una seccion no resuelta no impide emitir el pack: lo que impide es emitirlo en silencio")
    cuerpo = ruta_pack.read_text(encoding="utf-8")
    assert MARCA in cuerpo, "el pack no declara su recorte: se achico sin decirlo"
    assert "99" in cuerpo, "la seccion pedida debe nombrarse en el pack"
    assert "01-doc.md" in cuerpo, "la ruta intentada debe nombrarse en el pack"
    assert "contenido 1" in cuerpo, (
        "lo que si se resolvio no puede perderse por culpa de lo que no: eso seria truncar")
    assert rc == 0, "SECCION-NO-RESUELTA se emite y se declara; no es un fallo de emision"


def test_los_tres_estados_no_colapsan(bpb, plantear, tmp_path):
    """COMPLETO / SECCION-NO-RESUELTA / FUENTE-AUSENTE son tres causas distinguibles (R2.9)."""
    estados = {}
    for nombre, lectura in [
        ("P1", "01-doc.md §1 y el workflow canónico"),
        ("P2", "01-doc.md §1 y §99 y el workflow canónico"),
        ("P3", "01-doc.md §1 y no-hay-nada.md y el workflow canónico"),
    ]:
        caso = plantear(nombre=nombre, lectura=lectura)
        paquetes, _ = bpb.generar(caso["plan_dir"], tmp_path / nombre, caso["raiz"])
        estados[nombre] = paquetes[0]["estado"]
    assert estados == {"P1": "COMPLETO", "P2": "SECCION-NO-RESUELTA", "P3": "FUENTE-AUSENTE"}, (
        f"los estados colapsaron o se nombraron mal: {estados}")


def test_un_item_en_prosa_no_se_adivina_se_declara(bpb, plantear, tmp_path):
    """«los cuatro prompts de fase» nombra un conjunto, no una ruta: no se resuelve a mano."""
    caso = plantear(lectura="01-doc.md §1, los cuatro prompts de fase y el workflow canónico")
    destinos = tmp_path / "bp"
    paquetes, _ = bpb.generar(caso["plan_dir"], destinos, caso["raiz"])
    fuentes = paquetes[0]["fuentes"]
    prosa = [f for f in fuentes if f["clase"] == "prosa"]
    assert len(prosa) == 1 and prosa[0]["documento"] == "los cuatro prompts de fase"
    assert paquetes[0]["estado"] == "SECCION-NO-RESUELTA"
    cuerpo = (destinos / f"FASE-{paquetes[0]['fase']}.md").read_text(encoding="utf-8")
    assert "los cuatro prompts de fase" in cuerpo
