"""Lanzador del Config Checker desde scripts."""

from pathlib import Path
import sys


def _ensure_project_root() -> Path:
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root


def main() -> None:
    _ensure_project_root()
    from modules.utils.config_checker import main as checker_main

    checker_main()


if __name__ == "__main__":
    main()
