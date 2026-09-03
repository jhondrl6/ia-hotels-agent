"""Auditoria del mecanismo N-A1: narratives descarta pain_id en silencio.

Mide (no supone):
  1. Capa 1  = PAIN_SOLUTION_MAP (universo de pain_id)
  2. narratives = las 16 claves del dict en _pain_to_brecha
  3. detect_pains = lo que realmente se emite
  4. El descarte real = emitido por detect_pains Y ausente de narratives
"""
import ast
import re
import sys
from pathlib import Path

_root = Path(__file__).resolve()
while _root.parent != _root and not (_root / "VERSION.yaml").exists():
    _root = _root.parent
sys.path.insert(0, str(_root))

from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper

ROOT = _root
DIAG = ROOT / "modules" / "commercial_documents" / "v4_diagnostic_generator.py"

capa1 = set(PainSolutionMapper.PAIN_SOLUTION_MAP.keys())

# --- narratives: extraer las claves del dict literal por AST ---
tree = ast.parse(DIAG.read_text(encoding="utf-8"))
narratives_keys = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "narratives" and isinstance(node.value, ast.Dict):
                for k in node.value.keys:
                    if isinstance(k, ast.Constant) and isinstance(k.value, str):
                        narratives_keys.add(k.value)

# --- detect_pains: pain_id que el metodo construye ---
src = DIAG.read_text(encoding="utf-8")
psm_src = (ROOT / "modules" / "commercial_documents" / "pain_solution_mapper.py").read_text(encoding="utf-8")
emitidos = set(re.findall(r"""Pain\(\s*id=["']([a-z_0-9]+)["']""", psm_src))
# tambien los que se construyen por variable/helper
emitidos |= set(re.findall(r"""pain_id=["']([a-z_0-9]+)["']""", psm_src))

print("=" * 78)
print("1. CAPA 1  (PAIN_SOLUTION_MAP)          :", len(capa1))
print("2. narratives (_pain_to_brecha)         :", len(narratives_keys))
print("3. pain_id emitidos por detect_pains    :", len(emitidos))

print()
print("=" * 78)
print("A. En Capa 1 pero AUSENTES de narratives  (descarte posible)")
ausentes = sorted(capa1 - narratives_keys)
for p in ausentes:
    marca = "  <-- detect_pains LO EMITE" if p in emitidos else ""
    print(f"   {p:32s}{marca}")
print(f"   total: {len(ausentes)}")

print()
print("=" * 78)
print("B. En narratives pero AUSENTES de Capa 1  (violaria la regla de Capa 1)")
huerfanos = sorted(narratives_keys - capa1)
for p in huerfanos:
    emite = "  <-- detect_pains lo emite" if p in emitidos else "  (no emitido)"
    print(f"   {p:32s}{emite}")
print(f"   total: {len(huerfanos)}")

print()
print("=" * 78)
print("C. DESCARTE REAL = emitido por detect_pains Y ausente de narratives")
real = sorted(emitidos & set(ausentes))
for p in real:
    en_capa1 = "en Capa 1" if p in capa1 else "FUERA de Capa 1"
    print(f"   {p:32s} ({en_capa1})")
print(f"   total: {len(real)}")

print()
print("=" * 78)
print("D. missing_llmstxt - el caso de FASE-B")
print("   en Capa 1                :", "missing_llmstxt" in capa1)
print("   en narratives            :", "missing_llmstxt" in narratives_keys)
print("   emitido por detect_pains :", "missing_llmstxt" in emitidos)
print("   en SERVICE_IDENTITIES    :", end=" ")
from modules.common.service_identity import SERVICE_IDENTITIES
pains_canon = {i.pain_id for i in SERVICE_IDENTITIES}
brechas_canon = {b for i in SERVICE_IDENTITIES for b in i.brecha_candidates}
print("missing_llmstxt" in pains_canon, "(pain_id)")
print("   en brecha_candidates     :", "missing_llmstxt" in brechas_canon)

print()
print("=" * 78)
print("E. Falsos amigos ia_/ai_ (verificar que no se confundieron)")
for s in ("ia_crawler_blocked", "ai_crawler_blocked"):
    print(f"   {s:22s} Capa1={s in capa1!s:5s} narratives={s in narratives_keys!s:5s} emitido={s in emitidos!s}")
