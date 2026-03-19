"""Herramienta para mantener la carpeta de outputs bajo control."""

import argparse
import shutil
from pathlib import Path


def prune_outputs(base_dir: Path, keep: int) -> None:
    if not base_dir.exists():
        print(f"Directorio no encontrado: {base_dir}")
        return

    runs = sorted(
        (p for p in base_dir.iterdir() if p.is_dir()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    archive_dir = base_dir.parent / "archives" / "outputs"
    archive_dir.mkdir(parents=True, exist_ok=True)

    for index, path in enumerate(runs):
        if index < keep:
            continue
        target = archive_dir / path.name
        print(f"Archivando: {path.name} -> {target}")
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(path), str(target))


def main() -> None:
    parser = argparse.ArgumentParser(description="Prune manual de salidas del pipeline")
    parser.add_argument("--output", default="./output", help="Directorio con resultados recientes")
    parser.add_argument("--keep", type=int, default=2, help="Cantidad de corridas a preservar")
    args = parser.parse_args()

    prune_outputs(Path(args.output).resolve(), args.keep)


if __name__ == "__main__":
    main()
