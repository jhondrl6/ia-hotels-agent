"""AC21 — `--check` vence el pack contra el **arbol**, no contra la memoria del objeto.

La prueba exigida por el contrato es material: se **edita una fuente en disco**, se vuelve a
correr el check contra ese disco, y se revierte. Medir el dictamen sobre el objeto en memoria
dejaria pasar un lector que nunca mira el arbol (L-V2.3, R2.4). Las tres causas tienen que
distinguirse: fuente ausente, sha distinto, fuente ilegible.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _meta(bpb, ruta_pack: Path) -> dict:
    meta = bpb.leer_meta(ruta_pack)
    assert meta is not None, "el pack no lleva bloque de procedencia: no se puede vencer"
    return meta


def _reescribir_meta(bpb, ruta_pack: Path, meta: dict) -> None:
    nuevo = json.dumps(meta, ensure_ascii=False, indent=2)
    texto = ruta_pack.read_text(encoding="utf-8")
    m = bpb.META_RE.search(texto)
    ruta_pack.write_text(
        texto[:m.start()] + bpb.META_INICIO + "\n" + nuevo + "\n" + bpb.META_FIN + texto[m.end():],
        encoding="utf-8", newline="\n")


def test_editar_una_fuente_en_disco_vence_el_check(bpb, plantear, tmp_path):
    caso = plantear(lectura="01-doc.md §1 y el workflow canónico")
    destinos = tmp_path / "briefing"
    paquetes, _ = bpb.generar(caso["plan_dir"], destinos, caso["raiz"])
    pack = destinos / f"FASE-{paquetes[0]['fase']}.md"
    ruta_fuente = caso["doc1"]

    assert _sha(ruta_fuente) == _meta(bpb, pack)["sources"][0]["sha256"]
    antes, rc_antes = bpb.verificar(caso["plan_dir"], destinos, caso["raiz"])
    assert rc_antes == 0 and antes[0]["incidencias"] == []

    original = ruta_fuente.read_text(encoding="utf-8")
    ruta_fuente.write_text(original + "\n## 3. Seccion nueva\n\nalgo que nadie pidio\n",
                           encoding="utf-8", newline="\n")
    try:
        res, rc = bpb.verificar(caso["plan_dir"], destinos, caso["raiz"])
        assert rc == 1, "la fuente cambio en disco y el check no se entero"
        causas = [i["causa"] for r in res for i in r["incidencias"]]
        assert causas == ["SHA-DISTINTO"], causas
        publicados = res[0]["incidencias"][0]
        assert publicados["sha_publicado"] != publicados["sha_arbol"], (
            "el rojo debe decir los dos sha, no solo que algo obro")
    finally:
        ruta_fuente.write_text(original, encoding="utf-8", newline="\n")

    res2, rc2 = bpb.verificar(caso["plan_dir"], destinos, caso["raiz"])
    assert rc2 == 0, "revertida la fuente, el check sigue rojo: verifica otra cosa"
    assert res2[0]["incidencias"] == []


def test_mover_una_fuente_de_lugar_la_vence_por_ausencia(bpb, plantear, tmp_path):
    """Una fuente gobernada que desaparece es FUENTE-AUSENTE, no «nada que decir»."""
    caso = plantear(lectura="01-doc.md §1 y el workflow canónico")
    destinos = tmp_path / "briefing"
    paquetes, _ = bpb.generar(caso["plan_dir"], destinos, caso["raiz"])
    pack = destinos / f"FASE-{paquetes[0]['fase']}.md"
    meta = _meta(bpb, pack)
    # Las rutas del meta son relativas a la RAIZ con la que se genero (aqui, el arbol plantado).
    movida = caso["raiz"] / meta["sources"][0]["ruta"]
    assert movida.is_file(), movida
    movida.rename(movida.parent / "01-doc-movida.md")
    try:
        res, rc = bpb.verificar(caso["plan_dir"], destinos, caso["raiz"])
        assert rc == 1
        assert res[0]["incidencias"][0]["causa"] == "FUENTE-AUSENTE"
    finally:
        (movida.parent / "01-doc-movida.md").rename(movida)
    assert bpb.verificar(caso["plan_dir"], destinos, caso["raiz"])[1] == 0


def test_un_pack_que_no_existe_no_puede_estar_fresco(bpb, plantear, tmp_path):
    caso = plantear(lectura="01-doc.md §1 y el workflow canónico")
    destinos = tmp_path / "briefing"
    bpb.generar(caso["plan_dir"], destinos, caso["raiz"])
    for p in destinos.glob("*.md"):
        p.unlink()
    res, rc = bpb.verificar(caso["plan_dir"], destinos, caso["raiz"])
    assert rc == 1, "ausencia leida como verde (L-PF10)"
    assert res[0]["causa"] == "PACK-AUSENTE"


def test_la_causa_ilegible_no_colapsa_con_las_otras_dos(bpb, plantear, tmp_path):
    """FUENTE-AUSENTE / SHA-DISTINTO / FUENTE-ILEGIBLE: tres causas, tres rojos distintos."""
    caso = plantear(lectura="01-doc.md §1 y el workflow canónico")
    destinos = tmp_path / "briefing"
    paquetes, _ = bpb.generar(caso["plan_dir"], destinos, caso["raiz"])
    assert bpb.CAUSAS_CHECK == ("FUENTE-AUSENTE", "SHA-DISTINTO", "FUENTE-ILEGIBLE",
                                "PACK-AUSENTE")
    pack = destinos / f"FASE-{paquetes[0]['fase']}.md"
    _reescribir_meta(bpb, pack, {**_meta(bpb, pack), "sources": [{
        "ruta": str(caso["doc1"]), "sha256": None, "documento": "01-doc.md",
        "secciones": [], "en_pack": True}]})
    res, rc = bpb.verificar(caso["plan_dir"], destinos, caso["raiz"])
    assert rc == 1, "un sha ausente en el meta debe ser ilegible, no favorable"
    assert res[0]["incidencias"][0]["causa"] == "FUENTE-ILEGIBLE"
