"""Guard de encoding en `scripts/doctor.py`.

Premisa medida: `VERSION.yaml` lleva emojis en sus notas de release desde `082c9e1`
(v4.75.0). Leido con el codec de plataforma -cp1252 en Windows-, `Path.read_text()`
sin `encoding` lanza `UnicodeDecodeError` y tumba `main.py --doctor`,
`doctor.py --status` y `doctor.py --regenerate-domain-primer`.
"""

import ast
import locale
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCTOR = REPO_ROOT / "scripts" / "doctor.py"
VERSION_YAML = REPO_ROOT / "VERSION.yaml"

TEXT_READS = {"read_text", "read_lines"}


def _reads_without_encoding(tree):
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr not in TEXT_READS:
            continue
        if any(keyword.arg == "encoding" for keyword in node.keywords):
            continue
        hits.append(node.lineno)
    return sorted(hits)


def test_doctor_no_deja_lecturas_de_texto_sin_encoding_explicito():
    tree = ast.parse(DOCTOR.read_text(encoding="utf-8"))
    assert _reads_without_encoding(tree) == []


def test_doctor_resuelve_version_yaml_decodificando_como_utf8():
    text = VERSION_YAML.read_bytes().decode("utf-8")
    version = next(
        line.split('"')[1] for line in text.split("\n") if line.startswith("version:")
    )
    assert re.fullmatch(r"\d+\.\d+\.\d+", version)


def test_codec_de_plataforma_no_cubre_version_yaml():
    """Testigo del bug: falla si alguien vuelve a introducir un caracter que cp1252 no cubre."""
    raw = VERSION_YAML.read_bytes()
    platform_codec = locale.getpreferredencoding(False)
    try:
        raw.decode(platform_codec)
    except UnicodeDecodeError:
        assert platform_codec.lower().replace("-", "") != "utf8"
    else:
        pytest.skip(
            f"el codec de plataforma ({platform_codec}) ya cubre VERSION.yaml; "
            "el guard AST sigue siendo el que impide la regresion"
        )
