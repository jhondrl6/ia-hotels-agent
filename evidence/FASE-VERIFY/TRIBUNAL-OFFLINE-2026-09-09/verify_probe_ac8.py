# Sonda read-only FASE-VERIFY — TRIBUNAL-OFFLINE-2026-09-09
# Reproduce el régimen real de Bot 3 (AssetReviewer) contra el output vivo
# y el desempaquetado de evidencia, para fijar la causa raíz de AC8.
# NO modifica código ni artefactos: solo lee e imprime.
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from modules.quality_gates.tribunal.asset_reviewer import AssetReviewer

LIVE_AUDIT = ROOT / "output/v4_complete/hotelsalentoreal/v4_audit"
LIVE_DELIVERIES = ROOT / "output/v4_complete/deliveries"
UNPACKED = (
    ROOT / "evidence/FASE-E2E/deliveries/hotelsalentoreal_20260911_unpacked"
)
REAL_IMPL_ORDER = UNPACKED / "IMPLEMENTATION_ORDER.md"

print("=" * 70)
print("SONDA AC8 — AssetReviewer contra régimen real")
print("=" * 70)

# 1. Live acta (AC1/AC13 sobre output vivo, no solo copia de evidencia)
acta = json.loads((LIVE_AUDIT / "acta_revision.json").read_text(encoding="utf-8"))
print(f"\n[1] acta_revision.json VIVA: verdict={acta['verdict']!r} "
      f"evidence_tier={acta['evidence_tier']!r} clauses_evaluated={acta['clauses_evaluated']}")

# 2. Resolución de delivery_dir con el layout vivo (ZIP-only)
reviewer = AssetReviewer(LIVE_AUDIT, LIVE_DELIVERIES)
resolved = reviewer._resolve_delivery_dir()
print(f"\n[2] _resolve_delivery_dir() sobre deliveries/ vivo -> {resolved!r}")
print(f"    is_dir={resolved.is_dir() if resolved else None}")
print(f"    entradas en deliveries/: {sorted(p.name for p in LIVE_DELIVERIES.glob('*'))}")

# 3. Capa 1: check con el dir resuelto vivo (el ZIP)
findings_live = reviewer._check_implementation_order(resolved)
print(f"\n[3] _check_implementation_order(resolved_vivo) -> {len(findings_live)} findings")

# 4. Capa 2: heurística _is_template_stub contra el stub REAL (468 B)
content = REAL_IMPL_ORDER.read_text(encoding="utf-8")
size = REAL_IMPL_ORDER.stat().st_size
is_stub = reviewer._is_template_stub(content)
lines = content.strip().splitlines()
non_empty = sum(1 for l in lines if l.strip() and not l.strip().startswith("#"))
print(f"\n[4] IMPLEMENTATION_ORDER.md real: {size} bytes")
print(f"    _is_template_stub(content_real) -> {is_stub}")
print(f"    non_empty_lines (no '#') = {non_empty}  (umbral del heurístico: <= 3)")
separators = sum(1 for l in lines if l.strip() == "---")
print(f"    líneas '---' contadas como contenido: {separators}")

# 5. Check completo apuntando al desempaquetado de evidencia
findings_unpacked = reviewer._check_implementation_order(UNPACKED)
print(f"\n[5] _check_implementation_order(unpacked_evidencia) -> {len(findings_unpacked)} findings")
for f in findings_unpacked:
    print(f"    {f['finding_type']}: {f['description']}")

# 6. Conclusión
print("\n" + "=" * 70)
print("CONCLUSIÓN AC8:")
print("  Capa 1: deliveries/ vivo es ZIP-only -> _resolve_delivery_dir cae al")
print("          .zip; '<zip>/IMPLEMENTATION_ORDER.md' no existe -> 0 findings.")
print(f"  Capa 2: aun con el archivo disponible, _is_template_stub -> {is_stub}")
print(f"          (non_empty_lines={non_empty} > 3: los '---' y boilerplate cuentan).")
print("=" * 70)
