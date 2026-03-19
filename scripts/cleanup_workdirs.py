"""Limpia carpetas temporales sin borrar entregables recientes."""

import argparse
import shutil
from pathlib import Path


TARGET_DIRS = ["logs", "temp", "tests/results"]


def cleanup(base_dir: Path, dry_run: bool) -> None:
    for relative in TARGET_DIRS:
        path = base_dir / relative
        if not path.exists():
            continue
        if dry_run:
            print(f"   - Se limpiaria: {path}")
            continue
        if path.is_dir():
            shutil.rmtree(path)
            path.mkdir(parents=True, exist_ok=True)
            print(f"   - Reiniciado: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Limpia directorios de trabajo temporales")
    parser.add_argument("--root", default=".", help="Raiz del proyecto")
    parser.add_argument("--dry-run", action="store_true", help="Simula la limpieza")
    args = parser.parse_args()

    base_dir = Path(args.root).resolve()
    cleanup(base_dir, args.dry_run)


if __name__ == "__main__":
    main()
