"""Tests para scripts/validate_opencode_refs.py.

Cubren: extracción de referencias (con descarte de plantillas/globs),
detección de referencias rotas, --fix por promoción a Archives/Historico,
--fix por basename único, negativa a adivinar en casos ambiguos, el
baseline congelado y los exit codes del CLI.
"""

import pytest

from scripts import validate_opencode_refs as vor


@pytest.fixture
def tree(tmp_path, monkeypatch):
    """Monta un mini-repo .opencode y redirige las constantes del módulo."""
    opencode = tmp_path / ".opencode"
    (opencode / "plans" / "PLAN-A").mkdir(parents=True)
    (opencode / "plans" / "Archives" / "PLAN-B").mkdir(parents=True)
    (opencode / "context" / "Historico").mkdir(parents=True)
    (opencode / "plans" / "PLAN-A" / "doc.md").write_text("x", encoding="utf-8")
    (opencode / "plans" / "Archives" / "PLAN-B" / "10-analisis.md").write_text(
        "x", encoding="utf-8")
    (opencode / "context" / "activo.md").write_text("x", encoding="utf-8")
    (opencode / "context" / "Historico" / "movido.md").write_text("x", encoding="utf-8")
    monkeypatch.setattr(vor, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(vor, "OPENCODE_DIR", opencode)
    monkeypatch.setattr(vor, "BASELINE_FILE", opencode / "refs_baseline.txt")
    return tmp_path


def plans_dir(tree):
    return tree / ".opencode" / "plans"


def test_extract_refs_forward_and_backslash():
    text = "Ver `.opencode/plans/PLAN-A/doc.md` y .opencode\\context\\activo.md fin."
    refs = vor.extract_refs(text)
    assert refs == [".opencode/plans/PLAN-A/doc.md", ".opencode\\context\\activo.md"]


def test_extract_refs_strips_trailing_punctuation():
    text = "Ruta: .opencode/plans/PLAN-A/doc.md."
    assert vor.extract_refs(text) == [".opencode/plans/PLAN-A/doc.md"]


def test_extract_refs_discards_templates_and_globs():
    text = (
        "plantilla .opencode/plans/<nombre-del-plan>/ "
        "truncada .opencode/plans/X/0{2,3}-prompt.md "
        "wildcard .opencode/plans/X/*.md "
        "elipsis .opencode/context/...CONTEXT-....md"
    )
    assert vor.extract_refs(text) == []


def test_validate_detects_broken_and_ignores_valid(tree):
    scan = plans_dir(tree) / "PLAN-A" / "scan.md"
    scan.write_text(
        "ok: .opencode/plans/PLAN-A/doc.md\n"
        "rota: .opencode/context/no_existe.md\n",
        encoding="utf-8",
    )
    broken = vor.validate([plans_dir(tree)])
    assert [ref for _md, _ln, ref in broken] == [".opencode/context/no_existe.md"]


def test_validate_all_valid_returns_empty(tree):
    scan = plans_dir(tree) / "PLAN-A" / "scan.md"
    scan.write_text("ok: .opencode/context/activo.md\n", encoding="utf-8")
    assert vor.validate([plans_dir(tree)]) == []


def test_fix_promotes_to_archives(tree):
    """El patrón de archivado se resuelve sin ambigüedad vía promoción."""
    scan = plans_dir(tree) / "PLAN-A" / "scan.md"
    scan.write_text("ref: .opencode/plans/PLAN-B/10-analisis.md\n", encoding="utf-8")
    broken = vor.validate([plans_dir(tree)])
    fixed, unfixable = vor.fix_broken(broken)
    assert fixed == 1
    assert unfixable == []
    content = scan.read_text(encoding="utf-8")
    assert ".opencode/plans/Archives/PLAN-B/10-analisis.md" in content


def test_fix_unique_basename(tree):
    """Sin promoción posible, un basename único basta para reparar."""
    (plans_dir(tree) / "PLAN-A" / "unico.md").write_text("x", encoding="utf-8")
    scan = plans_dir(tree) / "PLAN-A" / "scan.md"
    scan.write_text("ref: .opencode/context/unico.md\n", encoding="utf-8")
    broken = vor.validate([plans_dir(tree)])
    fixed, unfixable = vor.fix_broken(broken)
    assert fixed == 1
    assert unfixable == []
    assert ".opencode/plans/PLAN-A/unico.md" in scan.read_text(encoding="utf-8")


def test_fix_ambiguous_refuses_and_leaves_file(tree):
    """Con varios candidatos y sin promoción, no se adivina."""
    (plans_dir(tree) / "PLAN-A" / "dup.md").write_text("x", encoding="utf-8")
    (plans_dir(tree) / "Archives" / "PLAN-B" / "dup.md").write_text("x", encoding="utf-8")
    scan = plans_dir(tree) / "PLAN-A" / "scan.md"
    original = "ref: .opencode/context/dup.md\n"
    scan.write_text(original, encoding="utf-8")
    broken = vor.validate([plans_dir(tree)])
    fixed, unfixable = vor.fix_broken(broken)
    assert fixed == 0
    assert len(unfixable) == 1
    assert scan.read_text(encoding="utf-8") == original


def test_baseline_skips_frozen_refs(tree):
    scan = plans_dir(tree) / "PLAN-A" / "scan.md"
    scan.write_text("rota: .opencode/context/no_existe.md\n", encoding="utf-8")
    key = vor.file_key(scan)
    vor.BASELINE_FILE.write_text(
        f"{key}|.opencode/context/no_existe.md\n", encoding="utf-8")
    assert vor.validate([plans_dir(tree)]) == []
    # Sin filtro de baseline (modo --write-baseline) la referencia reaparece.
    assert len(vor.validate([plans_dir(tree)], apply_baseline=False)) == 1


def test_main_exit_codes(tree, capsys):
    scan = plans_dir(tree) / "PLAN-A" / "scan.md"
    scan.write_text("ref: .opencode/plans/PLAN-B/10-analisis.md\n", encoding="utf-8")
    assert vor.main([]) == 1
    assert vor.main(["--fix"]) == 0
    assert vor.main([]) == 0
