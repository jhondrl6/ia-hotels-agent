#!/bin/bash
# F2 — piloto FASE-C del plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20
cd /c/Users/Jhond/Github/iah-cli || exit 1
E="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C"

echo "== git ls-files bajo $E (rutas)"
git ls-files "$E/"

echo "== conteo git ls-files bajo $E/"
git ls-files "$E/" | grep -c '/'

echo "== conteo en disco bajo $E/ (find -type f)"
find "$E" -type f | wc -l

echo "== git log --oneline -- $E/"
git log --oneline -- "$E/"

echo "== 7f2e9f9 es ancestro de HEAD?"
git merge-base --is-ancestor 7f2e9f9 HEAD && echo "SI-ANCESTRO" || echo "NO-ANCESTRO"

echo "== 5817edd es ancestro de HEAD?"
git merge-base --is-ancestor 5817edd HEAD && echo "SI-ANCESTRO" || echo "NO-ANCESTRO"

echo "== oneline de 7f2e9f9 y 5817edd"
git log --oneline -1 7f2e9f9
git log --oneline -1 5817edd

echo "== scripts/triage_lesson_relevance.py versionado?"
git ls-files scripts/triage_lesson_relevance.py

echo "== donde vive la rectificacion: grep -n 'Rectificado el 2026-09-24' de los cuatro documentos del plan"
P=".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
for f in 01-plan-maestro.md 04-contrato-ejecucion.md 10-analisis-post-implementacion.md dependencias-fases.md; do
  echo "-- $f"
  grep -n 'Rectificado el 2026-09-24' "$P/$f" || echo "   (sin coincidencia)"
done

echo "== frase vencida en presente, por documento (linea exacta)"
for f in 01-plan-maestro.md 04-contrato-ejecucion.md 10-analisis-post-implementacion.md dependencias-fases.md; do
  echo "-- $f"
  grep -n 'no se ejecut\|no lo esta\|no lo está\|sigue sin autorizar\|sigue sin autorización' "$P/$f" || echo "   (sin coincidencia)"
done
