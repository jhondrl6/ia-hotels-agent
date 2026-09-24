"""AC13 — el triaje se prueba contra **planes reales archivados**, no contra fixture propio (R2.6).

**Desviacion declarada por el operador (2026-09-24).** El prompt de la fase decia `Archives/` a secas,
pero el `archives/` de la raiz del repo **no contiene planes**: el corpus real vive en
`.opencode/plans/Archives/`, y de los 27 planes archivados solo dos tienen `00-` que triar
(PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12 y TRIBUNAL-ENFORCEMENT-OBS-2026-09-11). Un `skipif`
sobre una ruta inexistente seria un verde vacio (L-HF1), asi que la condicion de salto mira el corpus
efectivo y `evidence/…/FASE-C/r26.txt` declara si el test **corrio o se salto**, con el porque.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
ARCHIVES = ROOT / ".opencode" / "plans" / "Archives"
SUPPORT_OBSERVADOR = ROOT / "tests" / "support_observador_escrituras.py"

_corpus = sorted(p.parent for p in ARCHIVES.glob("*/00-lecciones-capitalizadas.md"))

skip_sin_corpus = pytest.mark.skipif(
    not ARCHIVES.is_dir() or len(_corpus) < 1,
    reason=("AC13 exige corpus real: no hay planes bajo "
            f"{ARCHIVES.as_posix()} con 00-lecciones-capitalizadas.md "
            f"(medido: {len(_corpus)}; `{ARCHIVES.is_dir()=}`)"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _observador():
    spec = importlib.util.spec_from_file_location("observador_escrituras", SUPPORT_OBSERVADOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@skip_sin_corpus
def test_el_corpus_real_existe_y_es_legible():
    assert _corpus, "el skip dice una cosa y el fixture otra"
    for plan in _corpus:
        texto = (plan / "00-lecciones-capitalizadas.md").read_text(encoding="utf-8")
        assert "## 2." in texto, f"{plan.name} no tiene §2 que triar"


@skip_sin_corpus
@pytest.mark.parametrize("plan_dir", _corpus, ids=lambda p: p.name)
def test_triage_sobre_plan_archivado_real(trl, entorno_falso, plan_dir):
    lecciones = plan_dir / "00-lecciones-capitalizadas.md"
    antes = _sha(lecciones)
    indice, estado = trl.leer_suelo()
    ancladas = trl.filas_ancladas(lecciones)
    assert ancladas, f"{plan_dir.name}: §2 sin filas leidas no es un corpus, es un lector roto"
    pendientes = trl.candidatos_de_pertinencia(indice, plan_dir.name, ancladas)
    obs = _observador()
    with obs.observador_de_escrituras() as registro:
        informe = trl.construir_informe(plan_dir.name, pendientes, ancladas, indice, estado,
                                        entorno=dict(__import__("os").environ))
    s = informe["seccion_dos"]
    assert s["removed"] == [], f"el triaje filtro filas de un plan archivado: {s['removed']}"
    assert s["anchored_after"] == s["anchored_before"] == len(ancladas)
    assert _sha(lecciones) == antes, "un plan archivado se toco: prohibido escribir sobre §2 ajeno"
    assert registro.dentro_de(plan_dir) == [], (
        f"escrituras observadas dentro de un plan archivado: {registro.dentro_de(plan_dir)}")
    assert informe["index_status"] == "FRESCO"
    assert informe["coste"]["emisor"]["falso"] is True
    assert informe["coverage_basis"]["denominador_juicio"]


@skip_sin_corpus
def test_la_salida_por_main_sobre_archivado_es_triado(trl, entorno_falso, tmp_path):
    plan = _corpus[0]
    ruta = tmp_path / "informe.json"
    rc = trl.main(["--plan", plan.name, "--report", "--out", str(ruta)])
    assert rc == 0
    informe = json.loads(ruta.read_text(encoding="utf-8"))
    assert informe["plan"] == plan.name
    assert informe["status"] == "TRIADO"
    assert informe["seccion_dos"]["removed"] == []
