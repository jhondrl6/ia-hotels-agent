"""§S32 (a) — el `--check` del escritor goberna también la proyección de bytes del workflow.

El pack de cada fase imprime `N bytes (~M tokens)` de `.agents/workflows/phased_project_executor.md`,
pero el workflow **no** está en `sources[]` y no puede estarlo: `test_briefing_se_genera_por_fase`
afirma que copiarlo sería rebanar `.agents/` por la puerta de atrás (AC17/D3). Hasta esta cura el
`--check` miraba solo las shas de esas fuentes, así que un workflow editado dejaba la proyección
vencida con verde y el rojo lo cortaba `[13/13]` del árbol commiteado — después del commit de quien
editó. Los cuatro criterios de la fila se prueban aquí sobre un plan plantado en `tmp_path`, con el
escritor **real** cargado por ruta.

Lo que se goberna es el número publicado, no un sha nuevo del workflow: el tamaño no deja de
publicarse (salida (b) rechazada por tocar lo que AC17/D3 decidió a propósito), y
`docs/CONTRIBUTING.md` queda fuera del contraste — su cifra en el pack es un reclamo de tamaño
publicado como texto, no una proyección de este generador.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

WF_REL = ".agents/workflows/phased_project_executor.md"
PROYECCION_RE = re.compile(
    r"^-\s+`(?P<ruta>[^`]+)`\s+—\s+(?P<bytes>\d+)\s+bytes\s+\(~(?P<tokens>\d+)\s+tokens\)",
    re.M)


def _generar_y_comprobar(bpb, caso, destinos):
    bpb.generar(caso["plan_dir"], destinos, caso["raiz"])
    return bpb.verificar(caso["plan_dir"], destinos, caso["raiz"])


def _lineas_proyectadas(pack: Path) -> dict:
    texto = pack.read_text(encoding="utf-8", errors="replace")
    return {m["ruta"]: (int(m["bytes"]), int(m["tokens"]))
            for m in PROYECCION_RE.finditer(texto)}


def test_la_proyeccion_fresca_verde_pero_declara_que_se_goberno(bpb, plantear, tmp_path):
    """Un verde que no nombra lo que miró es el defecto L-PF10: aqui se publica `proyeccion_gobernada`."""
    caso = plantear(nombre="S32-FRESCA")
    destinos = tmp_path / "b-fresca"
    resultados, rc = _generar_y_comprobar(bpb, caso, destinos)
    assert rc == 0, "un pack recien generado no puede estar vencido"
    assert resultados[0]["proyeccion_gobernada"] is True, (
        "el check dio verde sin declarar que contrastó la proyeccion del workflow")
    assert resultados[0]["incidencias_de_proyeccion"] == 0
    pack = destinos / "FASE-X.md"
    publicados = _lineas_proyectadas(pack)[WF_REL]
    reales = len((caso["raiz"] / WF_REL).read_bytes())
    assert publicados == (reales, bpb.tokens_estimados(reales)), (
        f"la proyeccion del pack no casa con el disco: {publicados} contra {reales}")


def test_unos_bytes_de_mas_en_el_workflow_cortan_el_check(bpb, plantear, tmp_path, capsys):
    """Criterio 1 de C2: el rojo sale en el instrumento de quien edita, no solo en [13/13]."""
    caso = plantear(nombre="S32-ROJO")
    destinos = tmp_path / "b-rojo"
    bpb.generar(caso["plan_dir"], destinos, caso["raiz"])
    wf = caso["raiz"] / WF_REL
    wf.write_bytes(wf.read_bytes() + b"\n# linea nueva que nadie regenero\n")

    capsys.readouterr()
    resultados, rc = bpb.verificar(caso["plan_dir"], destinos, caso["raiz"])
    salida = capsys.readouterr()

    assert rc == 1, (
        "el --check siguio dando verde con la proyeccion vencida: §S32 no esta curado")
    incidencias = resultados[0]["incidencias"]
    assert [i["causa"] for i in incidencias] == ["PROYECCION-VENCIDA"], (
        f"la incidencia no es la proyeccion vencida: {incidencias}")
    i = incidencias[0]
    reales = len(wf.read_bytes())
    assert i["fuente"] == WF_REL
    assert i["bytes_arbol"] == reales and i["bytes_publicados"] < reales, (
        f"el rojo no publica los dos numeros: {i}")
    assert i["tokens_arbol"] == bpb.tokens_estimados(reales), (
        "los tokens derivados de los bytes no se contrastan")
    assert WF_REL in salida.err and "PROYECCION-VENCIDA" in salida.err, (
        f"la consola del check no nombra la proyeccion vencida: {salida.err}")
    assert resultados[0]["incidencias_de_proyeccion"] == 1


def test_el_workflow_sigue_fuera_de_sources_con_la_proyeccion_gobernada(bpb, plantear, tmp_path):
    """AC17/D3 intacto: gobernar el numero no mete el workflow entre las fuentes gobernadas."""
    caso = plantear(nombre="S32-SOURCES")
    destinos = tmp_path / "b-sources"
    _generar_y_comprobar(bpb, caso, destinos)
    meta = bpb.leer_meta(destinos / "FASE-X.md")
    assert meta is not None, "el pack plantado no publico su bloque de procedencia"
    assert all(s["ruta"] != WF_REL for s in meta["sources"]), (
        f"el workflow entro en sources[]: {meta['sources']}")
    assert WF_REL in meta["lectura_aparte_obligatoria"], (
        "la lectura aparte desaparecio: la proyeccion se goberna porque se declara")


def test_quitar_la_comparacion_devuelve_el_verde_falso(bpb, plantear, tmp_path, monkeypatch):
    """Criterio 4 de C2: sin la comparacion nueva el mismo escenario verdece — el control tiene dientes."""
    caso = plantear(nombre="S32-ARNES")
    destinos = tmp_path / "b-arnes"
    bpb.generar(caso["plan_dir"], destinos, caso["raiz"])
    wf = caso["raiz"] / WF_REL
    wf.write_bytes(wf.read_bytes() + b"\n# mutante sin regenerar\n")

    resultados, rc_con_cura = bpb.verificar(caso["plan_dir"], destinos, caso["raiz"])
    assert rc_con_cura == 1, "el escenario base dejo de cortar: el arnes no tendria nada que apagar"
    assert resultados[0]["incidencias_de_proyeccion"] == 1

    real = bpb.proyecciones_de_lectura_aparte
    monkeypatch.setattr(bpb, "proyecciones_de_lectura_aparte", lambda *a, **k: [])
    _sin_comparacion, rc_sin_cura = bpb.verificar(caso["plan_dir"], destinos, caso["raiz"])
    assert rc_sin_cura == 0, (
        "el rojo no venia de la comparacion nueva: habria otra puerta que ya cortaba, y el verde de "
        "arriba no seria atribuible a C2")
    monkeypatch.setattr(bpb, "proyecciones_de_lectura_aparte", real)
    _, rc_restaurado = bpb.verificar(caso["plan_dir"], destinos, caso["raiz"])
    assert rc_restaurado == 1, "apagado y vuelto a encender el arnes no deja el mismo veredicto"


def test_una_proyeccion_ausente_es_un_silent_drop_no_un_verde(bpb, plantear, tmp_path):
    """La lectura aparte se declara pero su tamano dejo de imprimirse: eso se corta, no se ignora."""
    caso = plantear(nombre="S32-DROP")
    destinos = tmp_path / "b-drop"
    _generar_y_comprobar(bpb, caso, destinos)
    pack = destinos / "FASE-X.md"
    texto = pack.read_text(encoding="utf-8")
    assert WF_REL in _lineas_proyectadas(pack), "el pack plantado no proyecto el tamano del workflow"
    sin_linea = "\n".join(l for l in texto.splitlines()
                          if not PROYECCION_RE.match(l) or WF_REL not in l)
    pack.write_text(sin_linea + "\n", encoding="utf-8", newline="\n")
    assert WF_REL not in _lineas_proyectadas(pack), (
        "la supresion del renglon no se materializo: el control quedaria verde vacio")

    resultados, rc = bpb.verificar(caso["plan_dir"], destinos, caso["raiz"])
    assert rc == 1, "dejar de publicar el tamano gobernado no puede ser verde"
    assert [i["causa"] for i in resultados[0]["incidencias"]] == ["PROYECCION-AUSENTE"]


def test_contributing_no_entra_en_el_contraste_por_bytes(bpb, plantear, tmp_path):
    """Criterio 5 de C2: el gobierno por bytes cubre solo el workflow; CONTRIBUTING es un reclamo de texto.

    En el espejo plantado `docs/CONTRIBUTING.md` ni siquiera existe: si entrara en el contraste, la
    linea nueva daria `PROYECCION-FUENTE-AUSENTE` y el check cortaria. Que quede verde con esa linea
    presente y ese archivo ausente es justo lo que afirma el criterio.
    """
    caso = plantear(nombre="S32-CONTRIB")
    destinos = tmp_path / "b-contrib"
    _generar_y_comprobar(bpb, caso, destinos)
    pack = destinos / "FASE-X.md"
    texto = pack.read_text(encoding="utf-8")
    linea_ajena = ("- `docs/CONTRIBUTING.md` — 19763 bytes (~4940 tokens). el prompt la declara "
                   "pero vive fuera de `.opencode/`.")
    assert "## Que **no** incluye este pack" in texto, (
        "el pack plantado perdio la seccion donde se inserta la linea de control")
    pack.write_text(texto.replace("## Que **no** incluye este pack",
                                  f"{linea_ajena}\n\n## Que **no** incluye este pack"),
                    encoding="utf-8", newline="\n")

    proyectadas = _lineas_proyectadas(pack)
    assert proyectadas.get("docs/CONTRIBUTING.md") == (19763, 4940), (
        f"la linea de control no quedo plantada como proyeccion: {proyectadas}")
    assert not (caso["raiz"] / "docs" / "CONTRIBUTING.md").exists(), (
        "el espejo perdio su condicion de control: el archivo citado debe estar ausente")

    resultados, rc = bpb.verificar(caso["plan_dir"], destinos, caso["raiz"])
    assert rc == 0, (
        f"el check corto una proyeccion que no es del workflow: {resultados[0]['incidencias']}")
    assert resultados[0]["proyeccion_gobernada"] is True, (
        "sin el workflow gobernado la ausencia de rojo de arriba no habria observado nada")
