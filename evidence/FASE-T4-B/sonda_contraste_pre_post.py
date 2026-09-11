"""Contraste pre/post de la auditoria D-T4B-A1 (sonda de sola lectura).

Compara la version commiteada en HEAD del revisor con la del arbol de trabajo sobre los
mismos artefactos reales. Mientras el fix este sin commitear, imprime el delta que
documento la auditoria (0 CG leidos y veredicto espurio vs 12 entradas y veredicto
determinado por hallazgos reales). Despues del commit de la remediacion ambas lineas
coinciden: la sonda pasa a servir como reproduccion del contrato de lectura.

Uso:  python evidence/FASE-T4-B/sonda_contraste_pre_post.py
Requiere el baseline de sola lectura output/FASE-D_salentoreal_post_guard/.
No escribe en el baseline ni toca el arbol de trabajo.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from modules.quality_gates.tribunal import HonestyReviewer as WorktreeReviewer
from modules.quality_gates.tribunal.llm_extractor import MockPromiseExtractor

AUDIT = REPO_ROOT / "output/FASE-D_salentoreal_post_guard/v4_complete/hotelsalentoreal/v4_audit"
MODULE_PATH = "modules/quality_gates/tribunal/honesty_reviewer.py"


def load_head_reviewer():
    """Carga el revisor tal como esta en HEAD, sin tocar el arbol de trabajo."""
    source = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "show", f"HEAD:{MODULE_PATH}"],
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "head_honesty_reviewer.py"
        path.write_text(source, encoding="utf-8")
        spec = importlib.util.spec_from_file_location("head_honesty_reviewer", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.HonestyReviewer


def probe(reviewer_cls):
    reviewer = reviewer_cls(AUDIT)
    report = reviewer.review(extractor=MockPromiseExtractor([]))
    gates = report["commercial_gates_read"]
    return {
        "propuesta": reviewer._load_proposal() is not None,
        "total_cg_count": gates.get("total_cg_count"),
        "distinct_cg_count": gates.get("distinct_cg_count"),
        "canonical_file": gates.get("canonical_file"),
        "diagnostic_file": gates.get("diagnostic_file"),
        "veredicto": report["verdict_recommendation"],
        "cg_refs": [f.get("cg_reference") for f in report["findings"]],
        "tiers": [f.get("evidence_tier_declared") for f in report["findings"]],
    }


def main():
    if not AUDIT.is_dir():
        print(f"baseline no disponible: {AUDIT}")
        return 0
    print("HEAD  :", json.dumps(probe(load_head_reviewer()), ensure_ascii=False))
    print("WORK  :", json.dumps(probe(WorktreeReviewer), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
