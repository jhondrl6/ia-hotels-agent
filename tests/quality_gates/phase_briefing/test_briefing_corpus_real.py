"""R2.6 / AC19 — el generador se corre contra **planes reales archivados**, no contra fixture.

Precedente del defecto (L-HF1, medido en FASE-C): un `skipif` sobre una ruta inexistente es un
verde vacio. Aqui la condicion de salto mira el corpus efectivo y la prueba **publica el
denominador de la convencion**: de los planes archivados que tienen prompts de fase, cuantos
declaran su lectura en el formato que el generador parsea (una linea `Lee ...` dentro de un
bloque fenced de «Prompt de ejecucion»).

Lo medido en esta corrida: **0 de 121** prompts archivados, sobre **16** planes bajo `Archives/`
que tienen prompts de fase (los dos denominadores los imprime el propio test; esta linea es un
antecedente, no la fuente). La convencion la usan los planes nuevos, no los
archivados. Por eso un pack de un archivado sale `SIN-DECLARACION` y su check se publica
`SIN-FUENTES` en lugar de `OK`. Convertir eso en verde seria el defecto que L-PF10 nombra:
llamar «no habia nada» a «no encontre donde estaba la declaracion».
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PLANS = ROOT / ".opencode" / "plans"
ARCHIVES = PLANS / "Archives"


def _archivados_con_prompts() -> list[Path]:
    if not ARCHIVES.is_dir():
        return []
    return sorted(d for d in ARCHIVES.iterdir()
                  if d.is_dir() and list(d.glob("05-prompt-inicio-sesion-fase-*.md")))


CORPUS = _archivados_con_prompts()

skip_sin_corpus = pytest.mark.skipif(
    not ARCHIVES.is_dir() or len(CORPUS) < 1,
    reason=(f"R2.6 exige corpus real: no hay planes con 05-prompt-inicio-sesion-fase-*.md bajo "
            f"{ARCHIVES.as_posix()} (medido: {len(CORPUS)}; `{ARCHIVES.is_dir()=}`)"))


def _denominador(bpb) -> dict:
    """Cuantos prompts archivados declaran lectura, medido sobre el corpus real."""
    total = declarados = 0
    for plan in CORPUS:
        for p in sorted(plan.glob("05-prompt-inicio-sesion-fase-*.md")):
            total += 1
            if bpb.parsear_lista_lectura(p.read_text(encoding="utf-8", errors="replace")):
                declarados += 1
    return {"prompts_archivados": total, "con_declaracion_lee": declarados,
            "planes": len(CORPUS)}


@skip_sin_corpus
def test_el_corpus_real_existe_y_es_legible():
    assert CORPUS, "el skip dice una cosa y el fixture otra"
    for plan in CORPUS[:3]:
        assert list(plan.glob("05-prompt-inicio-sesion-fase-*.md"))


@skip_sin_corpus
def test_genera_el_pack_de_una_fase_de_un_plan_archivado_real(bpb, tmp_path):
    plan = CORPUS[0]
    destinos = tmp_path / "briefing"
    paquetes, rc = bpb.generar(plan, destinos, ROOT)
    assert rc == 0
    assert paquetes, f"{plan.name}: ni un prompt recorrido, el verde seria vacio"
    for pack in paquetes:
        archivo = destinos / f"FASE-{pack['fase']}.md"
        assert archivo.is_file(), f"falta el pack de FASE-{pack['fase']} de {plan.name}"
        meta = bpb.leer_meta(archivo)
        assert meta["plan"] == plan.name
        assert meta["no_incluye"], (
            "un pack de un archivado sin `no_incluye[]` afirmaria cobertura total")


@skip_sin_corpus
def test_un_archivado_sin_declara_lectura_no_se_informa_como_verde(bpb, tmp_path, capsys):
    """El hallazgo medido, assertionado: 0 de los archivados usan la convencion `Lee ...`."""
    d = _denominador(bpb)
    assert d["prompts_archivados"] > 0
    plan = CORPUS[0]
    destinos = tmp_path / "briefing"
    paquetes, _ = bpb.generar(plan, destinos, ROOT)
    sin_declaracion = [p for p in paquetes if p["declaracion"] == "SIN-DECLARACION"]
    if d["con_declaracion_lee"] == 0:
        assert len(sin_declaracion) == len(paquetes), (
            f"el corpus real no declara lectura ({d}) y aun asi un pack salio DECLARADA: "
            "el parser esta inventando")
    capsys.readouterr()
    res, rc = bpb.verificar(plan, destinos, ROOT)
    salida = capsys.readouterr()
    assert rc == 0
    if all(r["sin_fuentes"] for r in res):
        assert "SIN-FUENTES" in salida.err and "OK" not in salida.err, (
            "el check llamo OK a cero fuentes: verde vacio (L-HF1)")


@skip_sin_corpus
def test_el_denominador_del_corpus_se_publica_con_su_medicion(bpb):
    """La prueba no relata: imprime el denominador que va a `evidence/…/FASE-D/r26.txt`."""
    d = _denominador(bpb)
    assert set(d) == {"prompts_archivados", "con_declaracion_lee", "planes"}
    assert d["planes"] == len(CORPUS)
    print(f"[r26] corpus={d} skipif={'NO salto' if CORPUS else 'Salto'}")


@skip_sin_corpus
def test_generar_un_archivado_no_escribe_dentro_del_corpus(bpb, tmp_path):
    plan = CORPUS[0]

    def huellas() -> dict:
        return {str(p): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_size)
                for p in sorted(plan.rglob("*")) if p.is_file()}

    antes = huellas()
    bpb.generar(plan, tmp_path / "briefing", ROOT)
    assert huellas() == antes, "el generador escribio dentro de un plan archivado"
