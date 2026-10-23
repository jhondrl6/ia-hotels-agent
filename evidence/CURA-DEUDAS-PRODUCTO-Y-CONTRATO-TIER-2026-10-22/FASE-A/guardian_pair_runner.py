"""Par rojo/verde del guardián de existencia (FASE-A, R2.8 sobre el símbolo real).

Re-ejecutable desde la raíz del repo:
    ./venv/Scripts/python.exe evidence/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22/FASE-A/guardian_pair_runner.py
"""
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / 'tests'))
import test_main_static_guards as g

print("=== VERDE: arbol actual (sitios vigilados) ===")
for site in g.GUARDED_SITES:
    v = g.check_attribute_existence(site.read_text(encoding='utf-8'), filename=site.name)
    estado = 'SIN VIOLACIONES (verde)' if not v else v
    print(f"  {site.name}: {estado}")

print()
print("=== ROJO: mutante con atributo inventado (R2.8) ===")
print("Mutante: _MUTANTE_FASE_A = FinancialFactors.ATTR_INVENTADA_FASE_A")
print("Inyectado en la fuente real de gap_analyzer.py (sitio del defecto original).")
print()
real = g.GUARDED_SITES[1].read_text(encoding='utf-8')
mut = real + "\n# mutante FASE-A (R2.8)\n_MUTANTE_FASE_A = FinancialFactors.ATTR_INVENTADA_FASE_A\n"
v = g.check_attribute_existence(mut, filename='gap_analyzer.py(mutante)')
for line in v:
    print(f"  VIOLACION: {line}")
print()
print(f"RESULTADO MUTANTE: {'ROJO (detectado)' if v else 'VERDE FALSO - el guardian no mide lo que nombra (L-CIM.12)'}")
