import sys, re, yaml, ast
from pathlib import Path
_root = Path(__file__).resolve()
while _root.parent != _root and not (_root / "VERSION.yaml").exists():
    _root = _root.parent
sys.path.insert(0, str(_root))

src = (_root / "modules" / "commercial_documents" / "v4_diagnostic_generator.py").read_text(encoding="utf-8")
pat = re.compile(r"pain_narratives\.get\('([a-z_]+)',\s*([0-9.]+)\)")
py_defaults = {m.group(1): float(m.group(2)) for m in pat.finditer(src)}

data = yaml.safe_load((_root / "config" / "regional_benchmarks.yaml").read_text(encoding="utf-8"))
regions = {r: v["pain_narratives"] for r, v in data["regions"].items()
           if isinstance(v, dict) and isinstance(v.get("pain_narratives"), dict)}

print(f"Python fallbacks hardcoded en `narratives`: {len(py_defaults)}")
print(f"Regiones con pain_narratives en YAML: {list(regions)}")
print()
base = regions["eje_cafetero"]
print("¿Los fallbacks de Python == eje_cafetero?")
diffs = {k: (py_defaults[k], base.get(k)) for k in py_defaults if py_defaults[k] != base.get(k)}
print(f"   coincidencias: {len(py_defaults)-len(diffs)}/{len(py_defaults)}   divergencias: {diffs}")
print()
print("Regiones cuyo valor difiere de eje_cafetero (es decir, donde el fallback Python seria INCORRECTO):")
for r, vals in regions.items():
    if r == "eje_cafetero":
        continue
    d = {k: (base[k], vals[k]) for k in vals if k in base and base[k] != vals[k]}
    print(f"   {r}: {len(d)} de {len(vals)} difieren -> {d}")
