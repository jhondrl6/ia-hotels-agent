"""Fixtures compartidos de la seleccion FASE-A / `validate_governance_numbers.py`.

Dos poblaciones, y no se mezclan:
  * `arbol_real` — el repo vigente: es contra el que AC1 afirma A1-A4 (un fixture propio no
    prueba que el verificador reproduzca la medicion del maestro §1).
  * `fixture_gobierno` — un arbol minimo en tmp_path con su `run_all_validations.py`, su hook y
    sus documentos de gobierno, para poder provocar cada estado de R2.9 sin depender del arbol.
"""

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "validate_governance_numbers.py"

SOURCE_RAPIDA = '''#!/usr/bin/env python3
class Runner:
    def run_all(self) -> None:
        self._check_alpha()
        self._check_beta()
        if not self.quick:
            self._check_gamma()

    def _check_alpha(self) -> None:
        """Chequea alpha."""
        print("[1/2] Checking alpha...")
        script_path = ROOT_DIR / "scripts" / "validate_alpha.py"

    def _check_beta(self) -> None:
        print("[2/2] Checking beta...")
        script_path = ROOT_DIR / "scripts" / "validate_beta.py"

    def _check_gamma(self) -> None:
        print("[3/3] Checking gamma write-back...")
        script_path = ROOT_DIR / "scripts" / "validate_gamma_writeback.py"
'''

HOOK_RAPIDO = '''#!/bin/sh
# Pasos:
#   [1/2] Alpha check (validate_alpha.py)
#   [2/2] Beta check (validate_beta.py)
echo "[1/2] Checking alpha..."
echo "[2/2] Checking beta..."
'''

DOC_OK = (
    "# Gobierno de prueba\n\n"
    "**Verificador**: `scripts/validate_alpha.py` es check 1 de `run_all_validations.py --quick`.\n"
    "Beta corre como `[2/2]` de `run_all_validations.py --quick` "
    "(`scripts/validate_beta.py`).\n"
    "El cierre lo bloquea el paso `[1/2]` del hook `scripts/git_hooks/pre-commit`.\n"
)

DOC_VENCIDO = (
    "# Gobierno de prueba\n\n"
    "**Verificador**: `scripts/validate_alpha.py` es check 7 de `run_all_validations.py --quick`.\n"
    "Beta corre como `[9/9]` de `run_all_validations.py --quick` "
    "(`scripts/validate_beta.py`).\n"
)

DOC_HISTORICA = (
    DOC_VENCIDO
    + "\n## Versiones\n\n"
    "- **v1.1.0** (2026-01-01): Gamma paso a correr siempre (check `[3/3]`); despues se "
    "renumero y `[2/2]` bloqueó ese commit, y el write-back se documentó como `[7/7]`.\n"
)


@pytest.fixture(scope="session")
def raiz_repo() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def script_ruta() -> Path:
    return SCRIPT


@pytest.fixture
def gobierno(tmp_path: Path) -> dict:
    """Arbol minimo gobernable: fuente de checks, hook y dos documentos de gobierno."""
    source = tmp_path / "run_all_validations.py"
    source.write_text(SOURCE_RAPIDA, encoding="utf-8")
    hook = tmp_path / "pre-commit"
    hook.write_text(HOOK_RAPIDO, encoding="utf-8")
    doc = tmp_path / "workflow.md"
    doc.write_text(DOC_OK, encoding="utf-8")
    return {"source": source, "hook": hook, "doc": doc, "tmp": tmp_path}


@pytest.fixture
def modulo_gn():
    """El modulo real, cargado por ruta: los mutantes de AC4 lo patchean a el."""
    spec = importlib.util.spec_from_file_location("validate_governance_numbers", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
