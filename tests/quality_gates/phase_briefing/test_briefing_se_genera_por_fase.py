"""AC19 — el pack se genera para **todas** las fases del plan y declara lo que no incluye.

Tres cosas se afirman aqui, cada una con su denominador:

* un pack por fase, sin que nadie pase una lista de lecturas a mano: la fuente es el propio
  prompt (bloque «Prompt de ejecucion», cadena `Lee ...`);
* `no_incluye[]` **no vacio** y `lectura_aparte_obligatoria[]` con el workflow canonico a la
  cabeza — mientras D3 no lo rebane, el pack no puede presentarse como sustituto;
* `.agents/` no se escribe ni se copia como sustituto: se observa con el instrumento compartido
  (`tests/support_observador_escrituras.py`) y se compara por contenido, no por `git status`
  (el arbol de trabajo ya trae rutas ajenas a esta fase, y un `git status` lleno no es prueba
  de que la fase escribio).
"""

from __future__ import annotations

import hashlib
import json
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PLAN = ROOT / ".opencode" / "plans" / "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
AGENTS = ROOT / ".agents"
WORKFLOW = AGENTS / "workflows" / "phased_project_executor.md"
SUPPORT_OBSERVADOR = ROOT / "tests" / "support_observador_escrituras.py"
RUTA_WORKFLOW = ".agents/workflows/phased_project_executor.md"


def _observador():
    spec = importlib.util.spec_from_file_location("observador_escrituras", SUPPORT_OBSERVADOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _huellas(directorio: Path) -> dict:
    return {p.relative_to(ROOT).as_posix():
            (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_size)
            for p in sorted(directorio.rglob("*")) if p.is_file()}


def _fases_del_plan() -> list[str]:
    return sorted(p.stem.replace("05-prompt-inicio-sesion-fase-", "")
                  for p in PLAN.glob("05-prompt-inicio-sesion-fase-*.md"))


def test_un_pack_por_cada_fase_del_plan(bpb, tmp_path):
    destinos = tmp_path / "briefing"
    paquetes, rc = bpb.generar(PLAN, destinos, ROOT)
    assert [p["fase"] for p in paquetes] == _fases_del_plan(), (
        "el pack se genero para un subconjunto de las fases del plan")
    assert rc == 0
    for fase in _fases_del_plan():
        assert (destinos / f"FASE-{fase}.md").is_file(), f"falta el pack de FASE-{fase}"


def test_no_incluye_no_es_vacio_y_el_workflow_sigue_aparte(bpb, tmp_path):
    paquetes, _ = bpb.generar(PLAN, tmp_path / "briefing", ROOT)
    for pack in paquetes:
        assert pack["no_incluye"], (
            f"FASE-{pack['fase']}: un pack sin `no_incluye[]` afirma cobertura total sin haberla "
            "medido (L-HF1)")
        assert RUTA_WORKFLOW in pack["lectura_aparte_obligatoria"], (
            "el workflow canonic debe seguir siendo lectura aparte obligatoria")
        assert pack["lectura_aparte_obligatoria"][0] == RUTA_WORKFLOW, (
            "el workflow debe encabezar la lectura aparte mientras D3 no lo rebane")
    texto = (tmp_path / "briefing" / f"FASE-{paquetes[0]['fase']}.md").read_text(encoding="utf-8")
    assert "D3" in texto, "la razon de no rebanar el workflow debe leerse en el pack"


def test_el_pack_no_copia_el_workflow_ni_escribe_agents(bpb, tmp_path):
    obs = _observador()
    antes = _huellas(AGENTS)
    assert antes, f"no hay archivos bajo {AGENTS} para proteger"
    destinos = tmp_path / "briefing"
    with obs.observador_de_escrituras() as registro:
        paquetes, _ = bpb.generar(PLAN, destinos, ROOT)
    assert registro.dentro_de(AGENTS) == [], (
        f"el generador escribio dentro de .agents/: {registro.dentro_de(AGENTS)}")
    assert _huellas(AGENTS) == antes, "un byte de .agents/ se movio (AC17)"

    tajada = WORKFLOW.read_text(encoding="utf-8", errors="replace")
    corte = len(tajada) // 3
    muestra = tajada[corte:corte + 600]
    assert muestra, "el workflow no da una muestra que buscar"
    for pack in paquetes:
        ruta = destinos / f"FASE-{pack['fase']}.md"
        if not ruta.is_file():
            continue
        cuerpo = ruta.read_text(encoding="utf-8")
        assert muestra not in cuerpo, (
            "el pack copia el workflow: eso es rebanar .agents/ por la puerta de atras (AC17/D3)")
        meta = bpb.leer_meta(ruta)
        assert all(s["ruta"] != RUTA_WORKFLOW for s in meta["sources"]), (
            "el workflow no puede gobernar la frescura del pack: es lectura aparte, no fuente")


def test_lo_declado_es_del_prompt_no_de_una_configuracion(bpb, tmp_path):
    """Mover una lectura del prompt mueve el pack: no hay lista paralela que mantener."""
    paquetes, _ = bpb.generar(PLAN, tmp_path / "briefing", ROOT)
    pack_d = next(p for p in paquetes if p["fase"] == "D")
    texto_prompt = (PLAN / "05-prompt-inicio-sesion-fase-D.md").read_text(encoding="utf-8")
    items = bpb.parsear_lista_lectura(texto_prompt)
    assert items, "el prompt de FASE-D no declara lectura: el test quedaria verde vacio"
    assert [i["documento"] for i in items] == [f["documento"] for f in pack_d["fuentes"]]
    assert "01-plan-maestro.md" in {i["documento"] for i in items}


def test_lo_que_vive_fuera_de_opencode_se_declara_aparte_no_se_copia(bpb, tmp_path):
    """Un derivado no puede ampliar la poblacion que escanea otro gate ([8/11] del quick).

    Medido: `docs/CONTRIBUTING.md` declara fases de planes archivados por su ruta vieja. Al
    copiarlo dentro de `.opencode/plans/.../briefing/` esas referencias pasaban a contar como
    nuevas y el quick se ponfa rojo **por el artefacto derivado**. La regla no es un parche al
    sintoma: lo que vive fuera de `.opencode/` se lee aparte y se declara con su ruta.
    """
    destinos = tmp_path / "briefing"
    paquetes, _ = bpb.generar(PLAN, destinos, ROOT)
    release = next(p for p in paquetes if p["fase"] == "RELEASE")
    aparte = release["lectura_aparte_obligatoria"]
    assert ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/docs/CONTRIBUTING.md" not in aparte
    assert any(r == "docs/CONTRIBUTING.md" for r in aparte), aparte
    cuerpo = (destinos / "FASE-RELEASE.md").read_text(encoding="utf-8")
    assert "docs/CONTRIBUTING.md" in cuerpo and "validate_opencode_refs" in cuerpo
    assert all("SR-PIPELINE-FIXES" not in s["ruta"] for s in bpb.leer_meta(
        destinos / "FASE-RELEASE.md")["sources"])


def test_check_del_plan_real_pasa_sobre_el_arbol(bpb, tmp_path, capsys):
    """El comando canonico: generar y verificar contra el mismo arbol."""
    destinos = tmp_path / "briefing"
    bpb.generar(PLAN, destinos, ROOT)
    capsys.readouterr()
    resultados, rc = bpb.verificar(PLAN, destinos, ROOT)
    assert rc == 0, capsys.readouterr().err
    assert sum(r["fuentes"] for r in resultados) >= len(resultados), (
        "un check que no mira ninguna fuente no puede llamarse verde")


def test_sin_ruta_explicita_el_informe_no_se_escribe_en_ninguna_parte(bpb, tmp_path, capsys):
    """S12/L-VCF-12: `--report` a secas no puede tener un destino hardcodeado.

    FASE-B piso evidencia cerrada de FASE-A por ese patron. Aqui el informe y la carga se imprimen
    y **no escriben**, y el aviso se lee en stderr.
    """
    antes = {p: p.stat().st_mtime_ns for p in PLAN.rglob("*") if p.is_file()}
    rc = bpb.main(["--plan", str(PLAN), "--briefing-dir", str(tmp_path / "b"), "--informe", "-"])
    salida = capsys.readouterr()
    assert rc == 0
    assert "no se escribio ningun archivo" in salida.err, salida.err
    assert json.loads(salida.out)["tool"] == "build_phase_briefing.py"
    assert {p: p.stat().st_mtime_ns for p in PLAN.rglob("*") if p.is_file()} == antes, (
        "correr el generador toco documentos del plan")


def test_el_informe_publica_no_incluye_y_proveniencia_por_pack(bpb, tmp_path):
    """AC19/AC21 legibles en el artefacto: un humano debe encontrarlos ahi, no en el codigo."""
    destinos = tmp_path / "briefing"
    paquetes, _ = bpb.generar(PLAN, destinos, ROOT)
    verificacion, _ = bpb.verificar(PLAN, destinos, ROOT)
    informe = bpb.construir_informe(paquetes, verificacion, PLAN, destinos, ROOT)
    assert informe["packs"], "informe sin packs no responde AC19"
    for pack in informe["packs"]:
        assert pack["no_incluye"], pack["fase"]
        assert pack["lectura_aparte_obligatoria"], pack["fase"]
        assert set(["head", "generated_at", "head_fuente"]) <= set(pack["provenance"])
        assert pack["sources"], f"{pack['fase']}: un pack sin fuentes no es gobernable"
    cb = informe["coverage_basis"]
    assert cb["familias_no_cubiertas"], "AC17/AC2: el limite tiene que publicarse, no callarse"
    assert cb["unidad_bytes"].startswith("stat -c %s") and cb["divisor_tokens"] == 4
