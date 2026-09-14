"""FASE-P3-B / AC-F6 — la version del acta sale de VERSION.yaml, no del codigo.

`acta_writer.py` fijaba el footer a mano (``TribunalJudge v4.76.0``). La convencion del
repo es que VERSION.yaml es la fuente unica de version (AGENTS.md: "Fuente unica de
version: VERSION.yaml en raiz. Nunca hardcodear versiones en codigo"), y un acta de
certificacion que declara una version equivocada es exactamente el defecto de
fidelidad que este tribunal viene a cerrar.

El valor de la asercion se lee del YAML, nunca es un literal: si manana VERSION.yaml
dice otra cosa, el test sigue siendo valido.
"""

import re
from datetime import datetime
from pathlib import Path

import yaml

from modules.quality_gates.tribunal.acta_writer import (
    VERSION_NO_DISPONIBLE,
    ActaWriter,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
VERSION_YAML = REPO_ROOT / "VERSION.yaml"

FOOTER = re.compile(r"TribunalJudge v(?P<version>\S+)")


def _acta_minima() -> dict:
    return {
        "verdict": "APROBADO-CONDICIONAL-PENDING-ONBOARDING",
        "evidence_tier": "B+",
        "clauses_evaluated": 6,
        "clauses": {},
        "reviewer_reports": [],
        "first_floor_rule": {},
        "timestamp": datetime(2026, 9, 14).isoformat(),
        "hotel_id": "hotel-prueba",
    }


def _version_del_acta(tmp_path: Path) -> str:
    _, md_path = ActaWriter(tmp_path).write(_acta_minima())
    match = FOOTER.search(md_path.read_text(encoding="utf-8"))
    assert match, "el acta MD perdio el footer TribunalJudge vX.Y.Z (clave de AC-F6)"
    return match.group("version")


class TestVersionDelActa:
    def test_coincide_con_version_yaml(self, tmp_path):
        """Nada de literales: el esperado se lee del disco en el momento del test."""
        esperado = yaml.safe_load(VERSION_YAML.read_text(encoding="utf-8"))["version"]
        assert _version_del_acta(tmp_path) == esperado

    def test_refleja_un_yaml_distinto_sin_tocar_codigo(self, tmp_path, monkeypatch):
        """Mata a la vez el hardcode y una version cacheada al importar el modulo."""
        import modules.quality_gates.tribunal.acta_writer as acta_writer

        otra = tmp_path / "VERSION.yaml"
        otra.write_text('project: "t"\nversion: "9.9.9-test"\n', encoding="utf-8")
        monkeypatch.setattr(acta_writer, "VERSION_FILE", otra)

        assert _version_del_acta(tmp_path / "acta") == "9.9.9-test"

    def test_sin_yaml_legible_lo_declara(self, tmp_path, monkeypatch):
        """Fallback honesto: nunca una version plausible sacada de la manga."""
        import modules.quality_gates.tribunal.acta_writer as acta_writer

        monkeypatch.setattr(
            acta_writer, "VERSION_FILE", tmp_path / "no-existe" / "VERSION.yaml"
        )

        assert _version_del_acta(tmp_path / "acta") == VERSION_NO_DISPONIBLE

    def test_el_writer_no_lleva_un_literal_de_version(self):
        """Candado estructural: el fuente del writer no contiene versiones literales."""
        source = (
            REPO_ROOT / "modules" / "quality_gates" / "tribunal" / "acta_writer.py"
        ).read_text(encoding="utf-8")
        assert not re.search(r"v\d+\.\d+\.\d+", source), (
            "acta_writer.py volvio a llevar una version literal: la fuente unica es "
            "VERSION.yaml (AC-F6)"
        )
