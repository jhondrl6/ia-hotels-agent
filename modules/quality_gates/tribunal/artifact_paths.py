"""artifact_paths — resolución compartida de rutas de artefactos del tribunal.

El pipeline escribe la propuesta comercial en ``v4_complete/`` mientras el resto de
artefactos vive en ``v4_complete/<hotel>/v4_audit/``: dos niveles de distancia y un
nombre timestamped. Un lector que solo mire ``v4_audit_dir`` y su padre declara la
propuesta ausente de forma espuria, así que la búsqueda ascendente vive aquí en una
sola fuente para todos los revisores.
"""

import json
from pathlib import Path
from typing import Iterable, Optional

PROPOSAL_PATTERN = "02_PROPUESTA_COMERCIAL*.md"
CG_CANONICAL_PATTERN = "commercial_gates_report.json"
CG_DIAGNOSTIC_PATTERN = "commercial_gates_report_diagnostic_*.json"
FINANCIAL_SCENARIOS_PATTERN = "financial_scenarios_*.json"

ANCESTOR_LEVELS = 3


def pick_most_recent(paths: Iterable[Path]) -> Optional[Path]:
    """Retorna el Path más reciente por mtime, ignorando rutas ilegibles."""
    def mtime(path: Path) -> float:
        try:
            return path.stat().st_mtime
        except OSError:
            return 0.0

    files = [path for path in paths if path.is_file()]
    return max(files, key=mtime) if files else None


def resolve_latest(pattern: str, v4_audit_dir: Path, deliveries_dir: Optional[Path] = None,
                   ancestor_levels: int = ANCESTOR_LEVELS) -> Optional[Path]:
    """Resuelve el artefacto timestamped más reciente buscándose en ``v4_audit_dir``
    y en sus ascendientes, y recursivamente en ``deliveries_dir`` si se informa.

    El candidato se elige por mtime entre todos los directorios recorridos, no por el
    primer glob que dé un golpe.
    """
    candidates: list[Path] = []
    current = Path(v4_audit_dir)
    for _ in range(ancestor_levels + 1):
        if current.is_dir():
            candidates.extend(current.glob(pattern))
        if current.parent == current:
            break
        current = current.parent

    if deliveries_dir is not None and Path(deliveries_dir).is_dir():
        candidates.extend(Path(deliveries_dir).rglob(pattern))

    return pick_most_recent(candidates)


def read_text(path: Optional[Path]) -> Optional[str]:
    """Lee texto de forma segura (never-block)."""
    if path is None:
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def load_json(path: Optional[Path]) -> Optional[dict]:
    """Carga JSON de forma segura (never-block)."""
    if path is None:
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
