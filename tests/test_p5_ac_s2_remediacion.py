"""Remediacion FASE-P5 AC-S2 — audit 2026-09-15.

Cubre los tres huecos que la auditoria forense encontro en el commit b25b63a:
1. El escaneo staged estaba muerto: `re` solo se importaba dentro de
   _check_no_secrets y el NameError de _check_staged_content lo tragaba un
   `except Exception` — verde vacio (L-PF6). Estos tests prueban la divergencia
   staged-vs-worktree sobre un repo git real: el indice contiene el secreto,
   el arbol de trabajo NO, y el checker debe bloquear igualmente.
2. Estado NO_CUBIERTO real: el whitelist de extensiones se reemplazo por sniff
   NUL; un tracked no clasificable como texto bloquea en lugar de saltarse.
3. Politica de material de cliente separada de la deteccion de claves
   (config/client_material_policy.yaml).

NR7: cada deteccion (rojo) tiene su par sin-mutacion (verde).
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "run_all_validations", ROOT / "scripts" / "run_all_validations.py"
)
rav = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rav)

SYNTHETIC_KEY_VALUE = "AIzaSy" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7R"
_GOOGLE_PATTERN = (r"AIzaSy[A-Za-z0-9_\-]{30,}", "Google API key (AIzaSy...)")

_GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "p5-test",
    "GIT_AUTHOR_EMAIL": "p5-test@local",
    "GIT_COMMITTER_NAME": "p5-test",
    "GIT_COMMITTER_EMAIL": "p5-test@local",
    "GPGPROGRAM": "",
}


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args], cwd=repo, env=_GIT_ENV, check=True,
        capture_output=True, text=True,
    )


@pytest.fixture
def tmp_repo(tmp_path):
    _git(tmp_path, "init", "-q", "--initial-branch=main", ".")
    (tmp_path / "notas.md").write_text("documento limpio\n", encoding="utf-8")
    _git(tmp_path, "add", "notas.md")
    _git(tmp_path, "commit", "-q", "-m", "base")
    return tmp_path


class TestStagedVsWorktreeDivergence:
    """El secreto vive solo en el indice; el worktree esta limpio."""

    def test_red_staged_secret_blocks_even_with_clean_worktree(self, tmp_repo):
        # indice con el secreto...
        (tmp_repo / "notas.md").write_text(
            f"clave: {SYNTHETIC_KEY_VALUE}\n", encoding="utf-8"
        )
        _git(tmp_repo, "add", "notas.md")
        # ...y worktree restaurado limpio: la divergencia es exactamente esa.
        (tmp_repo / "notas.md").write_text("documento limpio\n", encoding="utf-8")

        runner = rav.ValidationRunner(quick=True, repo_root=tmp_repo)
        runner._check_no_secrets()
        result = runner.results[-1]
        assert result.name == "Secrets Check"
        assert not result.passed, (
            "b25b63a pasaba aqui: el NameError de `re` se tragaba y devolvia []"
        )
        assert "BLOCKING" in result.message
        assert any("STAGED" in d for d in result.details)
        assert SYNTHETIC_KEY_VALUE not in " ".join(result.details), (
            "la salida debe estar redactada"
        )

    def test_green_staged_and_worktree_clean(self, tmp_repo):
        runner = rav.ValidationRunner(quick=True, repo_root=tmp_repo)
        runner._check_no_secrets()
        result = runner.results[-1]
        assert result.passed
        assert "SIN_HALLAZGOS" in result.message


class TestNoCubiertoState:
    """LO-PF6: un archivo que el checker no puede leer como texto no puede dar verde."""

    @staticmethod
    def _runner_with_tracked(tmp_path, monkeypatch, tracked_names, content: bytes):
        runner = rav.ValidationRunner(quick=True, repo_root=tmp_path)
        paths = []
        for name in tracked_names:
            f = tmp_path / name
            f.write_bytes(content)
            paths.append(f)
        monkeypatch.setattr(runner, "_git_tracked_files", lambda: paths)
        monkeypatch.setattr(runner, "_check_staged_content", lambda patterns: [])
        return runner

    def test_red_unknown_binary_is_no_cubierto_and_blocks(self, tmp_path, monkeypatch):
        runner = self._runner_with_tracked(
            tmp_path, monkeypatch, ["blob.dat"], b"\x00\x01\x02data"
        )
        runner._check_no_secrets()
        result = runner.results[-1]
        assert not result.passed
        assert "NO_CUBIERTO" in result.message

    def test_green_same_file_without_nul_is_scanned(self, tmp_path, monkeypatch):
        runner = self._runner_with_tracked(
            tmp_path, monkeypatch, ["blob.dat"], b"texto sin nulos"
        )
        runner._check_no_secrets()
        assert runner.results[-1].passed
        assert "SIN_HALLAZGOS" in runner.results[-1].message

    def test_green_known_binary_excluded_but_declared(self, tmp_path, monkeypatch):
        runner = self._runner_with_tracked(
            tmp_path, monkeypatch, ["paquete.zip"], b"PK\x00\x01\x02\x03"
        )
        runner._check_no_secrets()
        result = runner.results[-1]
        assert result.passed
        assert "1 binarios conocidos" in result.message, (
            "la exclusion debe ser declarada, no silenciosa"
        )

    def test_red_secret_in_extensionless_tracked_file(self, tmp_path, monkeypatch):
        # .cursorrules/pre-commit: sin extension textual lista; el sniff NUL los
        # cubren, el whitelist de b25b63a los saltaba en silencio.
        runner = self._runner_with_tracked(
            tmp_path, monkeypatch, ["config_sin_sufijo"],
            f"key = {SYNTHETIC_KEY_VALUE}".encode(),
        )
        runner._check_no_secrets()
        assert not runner.results[-1].passed
        assert "BLOCKING" in runner.results[-1].message


class TestClientMaterialPolicy:
    """AC-S2 remendada: la politica anti-material-de-cliente va separada del detector."""

    @staticmethod
    def _runner_with_paths(tmp_path, monkeypatch, tracked=(), staged=()):
        runner = rav.ValidationRunner(quick=True, repo_root=tmp_path)
        monkeypatch.setattr(
            runner, "_git_tracked_files",
            lambda: [tmp_path / p for p in tracked],
        )
        monkeypatch.setattr(runner, "_git_staged_paths", lambda: list(staged))
        return runner

    def test_red_client_marker_outside_quarantine_blocks(self, tmp_path, monkeypatch):
        runner = self._runner_with_paths(
            tmp_path, monkeypatch, tracked=["site/promos_donalfonso.html"]
        )
        runner._check_client_material()
        result = runner.results[-1]
        assert result.name == "Client Material"
        assert not result.passed
        assert "BLOCKING" in result.message
        assert any("donalfonso" in d for d in result.details)

    def test_red_client_marker_in_staged_blocks(self, tmp_path, monkeypatch):
        runner = self._runner_with_paths(
            tmp_path, monkeypatch, staged=["entregables/gbp_profiles_export.json"]
        )
        runner._check_client_material()
        assert not runner.results[-1].passed

    def test_green_quarantine_and_grandfathered_pass(self, tmp_path, monkeypatch):
        runner = self._runner_with_paths(
            tmp_path, monkeypatch,
            tracked=[
                "evidence/FASE-P4/corrida/hotelsalentoreal/blob.md",
                "archives/gbp_profiles.json",
                ".opencode/context/Historico/CONTEXT-SALENTOREAL.md",
                # grandfathered en config/client_material_policy.yaml:
                "tests/fixtures/donalfonsohotel_onboarding.yaml",
            ],
        )
        runner._check_client_material()
        result = runner.results[-1]
        assert result.passed, result.message
        assert "SIN_HALLAZGOS" in result.message

    def test_red_missing_policy_fails_closed(self, tmp_path, monkeypatch):
        runner = rav.ValidationRunner(quick=True, repo_root=tmp_path)
        monkeypatch.setattr(rav, "ROOT_DIR", tmp_path)
        runner._check_client_material()
        result = runner.results[-1]
        assert not result.passed
        assert "POLICY_MISSING" in result.message
