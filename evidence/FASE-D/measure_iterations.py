r"""Cuenta iteraciones reales de una sesion a partir de su transcript .jsonl.

Existe porque el presupuesto de iteraciones del workflow (R2 <=60, y el que fija cada
prompt de fase) no tiene contador instrumentado: cada fase se auto-reporta y la cifra no
es auditable ni comparable entre fases. Ese hallazgo lo registraron FASE-B y FASE-D por
separado; este script es la respuesta automatizada.

Unidad de conteo: **ids de mensaje de asistente unicos** (`message.id`, un id por
peticion al modelo) y total de bloques `tool_use`. Es la misma unidad con la que B y D
publicaron sus cifras, asi que son comparables entre fases.

Uso:
    python evidence/FASE-D/measure_iterations.py <transcript.jsonl> [corte-ISO-8601]

El segundo argumento es opcional y corta el conteo en ese timestamp -- por ejemplo el
momento del commit de codigo -- para separar «iteraciones de implementacion» de
«iteraciones de cierre documental».
"""
from __future__ import annotations

import json
import sys


def _to_utc_seconds(value: object) -> float | None:
    """Normaliza el timestamp de un record: el transcript mezcla epoch-ms e ISO-8601 UTC.

    Compararlas como cadenas descarta en silencio los records epoch y subcuenta el corte.
    """
    from datetime import datetime, timezone

    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value) / 1000.0
    text = str(value).strip()
    if not text:
        return None
    if text.isdigit():
        return float(text) / 1000.0
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def measure(path: str, cutoff: str | None = None) -> tuple[int, int, int]:
    cutoff_seconds = _to_utc_seconds(cutoff) if cutoff else None
    turn_ids: set[str] = set()
    tool_uses = 0
    records = 0
    skipped_no_ts = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            records += 1
            if rec.get("type") != "assistant":
                continue
            if cutoff_seconds is not None:
                ts = _to_utc_seconds(rec.get("timestamp"))
                if ts is None:
                    skipped_no_ts += 1
                    continue
                if ts > cutoff_seconds:
                    continue
            msg = rec.get("message") or {}
            mid = msg.get("id")
            if mid:
                turn_ids.add(str(mid))
            content = msg.get("content")
            if isinstance(content, list):
                tool_uses += sum(
                    1 for c in content if isinstance(c, dict) and c.get("type") == "tool_use"
                )
    if cutoff_seconds is not None and skipped_no_ts:
        print(
            f"aviso: {skipped_no_ts} records de asistente sin timestamp utilizable quedaron fuera del corte",
            file=sys.stderr,
        )
    return len(turn_ids), tool_uses, records


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cutoff = argv[1] if len(argv) > 1 else None
    ids, tools, records = measure(argv[0], cutoff)
    scope = f" (timestamp <= {cutoff})" if cutoff else " (transcript completo)"
    print(f"iteraciones{scope}: {ids} ids de mensaje unicos, {tools} tool_use, {records} records")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
