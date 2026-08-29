#!/usr/bin/env python3
"""
Instalador de git hooks versionados - IA Hoteles Agent.

Los hooks viven versionados en ``scripts/git_hooks/`` (git no trackea
``.git/hooks/``). Tras clonar el repo, ejecutar:

    python scripts/install_git_hooks.py

Comportamiento:
- Copia cada hook de scripts/git_hooks/ a .git/hooks/
- Si el hook destino existe y difiere, lo respalda como <hook>.bak.<timestamp>
- NO toca post-commit (puede estar gestionado por otras herramientas)

Exit codes:
  0 - hooks instalados o ya vigentes
  2 - el directorio no es un repositorio git
"""
import os
import shutil
import stat
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "scripts" / "git_hooks"
GIT_HOOKS = ROOT / ".git" / "hooks"


def main() -> int:
    if not (ROOT / ".git").exists():
        print(f"[ERROR] {ROOT} no es un repositorio git (falta .git/)")
        return 2

    GIT_HOOKS.mkdir(exist_ok=True)
    installed = 0

    for hook in sorted(SRC_DIR.iterdir()):
        if hook.suffix or hook.name.startswith("."):
            continue
        target = GIT_HOOKS / hook.name

        if target.exists():
            if target.read_bytes() == hook.read_bytes():
                print(f"[OK] {hook.name} ya instalado")
                continue
            backup = target.with_name(f"{hook.name}.bak.{int(time.time())}")
            shutil.copy2(target, backup)
            print(f"[BACKUP] {hook.name} previo -> {backup.name}")

        shutil.copy2(hook, target)
        mode = os.stat(target).st_mode
        os.chmod(target, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"[INSTALL] {hook.name}")
        installed += 1

    print(f"Listo: {installed} hook(s) instalado(s), resto sin cambios.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
