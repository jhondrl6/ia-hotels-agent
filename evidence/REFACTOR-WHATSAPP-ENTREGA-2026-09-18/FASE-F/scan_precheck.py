"""Medicion FASE-F (scratch, no versionado).

Cuenta los hallazgos de los patrones REALES del verificador sobre output/ y logs/,
que hoy no inspecciona porque estan en .gitignore. Imprime exclusivamente etiqueta,
ruta y conteo: nunca el valor ni la linea coincidente.
"""

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "run_all_validations", ROOT / "scripts" / "run_all_validations.py"
)
rav = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rav)

runner = rav.ValidationRunner(quick=True, repo_root=ROOT)
patterns = [(re.compile(rx), label) for rx, label in runner._secret_patterns()]
BIN_EXTS = rav.ValidationRunner._KNOWN_BINARY_EXTS
MAX_BYTES = rav.ValidationRunner._MAX_SCAN_BYTES

totals = {}
hits_by_file = {}
scanned = 0
skipped_binary = 0
too_big = 0

for base in ("output", "logs"):
    root_dir = ROOT / base
    if not root_dir.is_dir():
        continue
    for path in root_dir.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        if path.suffix.lower() in BIN_EXTS:
            skipped_binary += 1
            continue
        try:
            if path.stat().st_size > MAX_BYTES:
                too_big += 1
                continue
            raw = path.read_bytes()
        except OSError:
            continue
        if b"\x00" in raw[:8192]:
            skipped_binary += 1
            continue
        scanned += 1
        text = raw.decode("utf-8", errors="replace")
        for regex, label in patterns:
            count = len(regex.findall(text))
            if count:
                totals[label] = totals.get(label, 0) + count
                rel = str(path.relative_to(ROOT))
                hits_by_file[rel] = hits_by_file.get(rel, 0) + count

print("archivos_examinados", scanned)
print("no_texto_omitidos", skipped_binary)
print("demasiado_grandes", too_big)
print("archivos_con_hallazgos", len(hits_by_file))
for label, count in sorted(totals.items()):
    print("PATRON", label, count)
for rel, count in sorted(hits_by_file.items(), key=lambda kv: -kv[1])[:20]:
    print("RUTA", rel, count)
