#!/usr/bin/env python3
"""
validate.py — Valida observations.json contra hotel_observations.schema.json.

Uso:
    python3 scripts/validate.py
    python3 scripts/validate.py ruta/al/observations.json

Portable: usa Path(__file__).parent.parent para resolver rutas relativas
al archivo schema y al archivo observations.json por defecto. No depende
del cwd ni de rutas absolutas de maquina.
"""

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit(
        "ERROR: jsonschema no instalado.\n"
        "Instalar con: uv pip install --system jsonschema\n"
        "O dentro de un venv del proyecto: .venv/bin/pip install jsonschema"
    )


def resolve_paths(argv: list[str]) -> tuple[Path, Path]:
    """Resuelve (observations.json, schema.json) a partir de argv o defaults."""
    base = Path(__file__).resolve().parent.parent  # data/hotel_observations/
    schema_path = base / "hotel_observations.schema.json"

    if len(argv) > 1:
        obs_path = Path(argv[1]).resolve()
    else:
        obs_path = base / "observations.json"

    return obs_path, schema_path


def validate(obs_path: Path, schema_path: Path) -> tuple[bool, list[str]]:
    """Valida y retorna (ok, mensajes). Mensajes lista vacia si ok."""
    if not obs_path.exists():
        return False, [f"Archivo no encontrado: {obs_path}"]
    if not schema_path.exists():
        return False, [f"Schema no encontrado: {schema_path}"]

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"Schema invalido (no es JSON): {e}"]

    try:
        data = json.loads(obs_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"observations.json invalido (no es JSON): {e}"]

    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(data))

    if not errors:
        n = len(data.get("observations", []))
        last = data.get("last_updated", "?")
        return True, [f"OK: {n} observacion(es) validadas (last_updated={last})"]

    msgs = [f"FAIL: {len(errors)} error(es)"]
    for e in errors[:10]:  # mostrar maximo 10
        loc = "/".join(str(p) for p in e.absolute_path) or "<root>"
        msgs.append(f"  - [{loc}] {e.message}")
    if len(errors) > 10:
        msgs.append(f"  ... y {len(errors) - 10} error(es) mas")
    return False, msgs


def main() -> int:
    obs_path, schema_path = resolve_paths(sys.argv)
    ok, messages = validate(obs_path, schema_path)
    for m in messages:
        print(m)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
