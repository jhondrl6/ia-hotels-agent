#!/bin/bash
# 10 — veredictos por AC leidos de sus fuentes (no de la orden)
cd /c/Users/Jhond/Github/iah-cli || exit 1
V=".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
J=".opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21"
export PYTHONIOENCODING=utf-8

echo "### A. Filas AC12/AC13/AC14/AC15 del checklist del plan VCF (texto integro)"
python - "$V/06-checklist-implementacion.md" <<'PY'
import io, sys
lines = io.open(sys.argv[1], encoding="utf-8").read().split("\n")
for i, ln in enumerate(lines, 1):
    if ln.startswith("| AC12") or ln.startswith("| AC13") or ln.startswith("| AC14") or ln.startswith("| AC15"):
        print("LINEA %d: %s" % (i, ln))
        print()
PY

echo "### B. coverage.json de FASE-C: aceptabilidad y su motivo"
python - <<'PY'
import io, json
d = json.load(io.open("evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/coverage.json", encoding="utf-8"))
print("aceptacion =", json.dumps(d.get("aceptacion"), ensure_ascii=False))
print("umbral     =", json.dumps(d.get("umbral"), ensure_ascii=False))
print("claves     =", sorted(d.keys()))
PY

echo "### C. mutation/ de FASE-C: verde y rojos del guard (AC14)"
ls evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/
echo "-- resumen.txt"
cat evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/resumen.txt

echo
echo "### D. AC3 del plan JEV: su clausula y su estado declarado"
grep -n '^| AC3' "$J/01-plan-maestro.md"
echo "-- estado en el README del plan (fila FASE-A)"
grep -n 'BORRADOR' "$J/README.md" | head -4
echo "-- AC3 en el checklist de JEV"
grep -n 'AC3' "$J/06-checklist-implementacion.md" | head -6

echo
echo "### E. rastro de original_sha256 en la muestra de JEV (lo que AC3 exige)"
echo "-- busqueda del token en todo el plan JEV"
grep -rn 'original_sha256\|sha256' "$J" | cut -c1-200 | head -20
echo "-- busqueda en la evidencia de FASE-A de JEV"
ls evidence/ | head -3
find evidence -ipath '*JEV*' -type f 2>/dev/null | head -20

echo
echo "### F. estados B/C/RELEASE del plan JEV (para el corolario PENDIENTE-POR-DISENO)"
grep -n 'FASE-B\|FASE-C\|FASE-RELEASE' "$J/README.md" | grep -i 'bloquead\|pendiente\|sin autoriza' | cut -c1-220
