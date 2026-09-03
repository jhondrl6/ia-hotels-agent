import sys, yaml
from pathlib import Path
_root = Path(__file__).resolve()
while _root.parent != _root and not (_root / "VERSION.yaml").exists():
    _root = _root.parent
sys.path.insert(0, str(_root))
from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper

data = yaml.safe_load((_root / "config" / "regional_benchmarks.yaml").read_text(encoding="utf-8"))
capa1 = set(PainSolutionMapper.PAIN_SOLUTION_MAP.keys())
print(f"Capa 1 (PAIN_SOLUTION_MAP): {len(capa1)}")
print()
regions = data.get("regions", data)
allkeys = set()
for rname, rval in regions.items():
    if not isinstance(rval, dict):
        continue
    pn = rval.get("pain_narratives")
    if pn is None:
        continue
    keys = set(pn.keys())
    allkeys |= keys
    print(f"region {rname!r}: {len(keys)} pain_narratives")
    print(f"   huérfanos (no están en Capa 1): {sorted(keys - capa1)}")
print()
print(f"UNIÓN de todas las regiones: {len(allkeys)}")
print(f"   huérfanos vs Capa 1: {sorted(allkeys - capa1)}")
print(f"   Capa 1 sin narrativa YAML en NINGUNA región: {len(capa1 - allkeys)}")
print(f"   Capa 1 presente en ALGUNA región: {len(capa1 & allkeys)}")
