"""AC21 (segundaclause) — HEAD es **procedencia**, no la llave de caducidad del pack.

Si el sha de HEAD gobernara, el commit que guarda el pack generado lo dejaria vencido dentro de
ese mismo commit: invalidacion circular, prohibida por el contrato §Carga total y frescura del
pack. Como una sesion de test no puede avanzar el HEAD del repo, la condicion se fabrica sobre
el arbol plantado: se reescribe `provenance.head` del pack **sin tocar ninguna fuente**. Eso es
exactamente el estado «el pack salio de otro arbol». Que el check no lo lea como VENCIDO es lo
que se prueba; y que lo **publique** como procedencia distinta, para que no se pierda el dato.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _reescribir_head_del_meta(bpb, ruta_pack: Path, head_falso: str) -> dict:
    texto = ruta_pack.read_text(encoding="utf-8")
    m = bpb.META_RE.search(texto)
    meta = json.loads(m.group(1))
    meta = {**meta, "provenance": {**meta["provenance"], "head": head_falso}}
    nuevo = json.dumps(meta, ensure_ascii=False, indent=2)
    ruta_pack.write_text(
        texto[:m.start()] + bpb.META_INICIO + "\n" + nuevo + "\n" + bpb.META_FIN + texto[m.end():],
        encoding="utf-8", newline="\n")
    return meta


def test_head_distinto_con_fuentes_identicas_no_vence_el_pack(bpb, plantear, tmp_path):
    caso = plantear(lectura="01-doc.md §1 y el workflow canónico")
    destinos = tmp_path / "briefing"
    paquetes, _ = bpb.generar(caso["plan_dir"], destinos, caso["raiz"])
    pack = destinos / f"FASE-{paquetes[0]['fase']}.md"
    meta = _reescribir_head_del_meta(bpb, pack, "0123456")

    res, rc = bpb.verificar(caso["plan_dir"], destinos, caso["raiz"])
    assert meta["provenance"]["head"] != res[0]["head_arbol"], (
        "el caso no estaba planteado: HEAD del pack igual al del arbol, el test no mira nada")
    assert rc == 0, (
        f"HEAD avanzo y el pack se vencio: HEAD goberna la caducidad ({res[0]['incidencias']})")
    assert res[0]["procedencia_distinta"] is True, (
        "no vence, pero tiene que decirlo: la procedencia distinta es dato publicable")
    assert res[0]["incidencias"] == []


def test_el_pack_no_esta_en_su_propio_conjunto_de_fuentes(bpb, plantear, tmp_path):
    caso = plantear(lectura="01-doc.md §1 y el workflow canónico")
    destinos = tmp_path / "briefing"
    paquetes, _ = bpb.generar(caso["plan_dir"], destinos, caso["raiz"])
    pack = destinos / f"FASE-{paquetes[0]['fase']}.md"
    meta = json.loads(bpb.META_RE.search(pack.read_text(encoding="utf-8")).group(1))
    rutas = {Path(s["ruta"]).name for s in meta["sources"]}
    assert pack.name not in rutas, (
        "el pack se goberna a si mismo: al versionarlo se venceria dentro de su propio commit")
    assert "01-doc.md" in rutas


def test_avanzar_el_head_reales_no_cambia_el_dictamen_sobre_fuentes_iguales(
        bpb, plantear, tmp_path):
    """El mismo arbol de fuentes, dos cabeceras distintas declaradas: mismo dictamen."""
    caso = plantear(lectura="01-doc.md §1 y el workflow canónico")
    destinos = tmp_path / "briefing"
    paquetes, _ = bpb.generar(caso["plan_dir"], destinos, caso["raiz"])
    pack = destinos / f"FASE-{paquetes[0]['fase']}.md"
    dictamenes = []
    for cabeza in ("0123456", "abcdef9"):
        _reescribir_head_del_meta(bpb, pack, cabeza)
        res, rc = bpb.verificar(caso["plan_dir"], destinos, caso["raiz"])
        dictamenes.append((rc, res[0]["causa"], res[0]["procedencia_distinta"]))
    assert dictamenes[0][0] == dictamenes[1][0] == 0
    assert dictamenes[0][2] is True and dictamenes[1][2] is True
    assert len({d[0] for d in dictamenes}) == 1, (
        f"la caducidad dependio de la cabecera declarada: {dictamenes}")
