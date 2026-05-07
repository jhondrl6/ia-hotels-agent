"""[DEPRECATED] Wrapper para config_checker de modules/utils.

Este script existe solo por compatibilidad hacia atrás.
Usa directamente: python -m modules.utils.config_checker

O desde la raíz del proyecto:
    python modules/utils/config_checker.py

Fue deprecado el 2026-05-05 -襄山
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Re-dirigir al módulo principal
from modules.utils.config_checker import main as checker_main

if __name__ == "__main__":
    checker_main()
