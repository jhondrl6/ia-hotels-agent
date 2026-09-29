#!/bin/bash
# F1 — archivado del plan EVALUACION-JEV-TYPESAFE-2026-09-21
cd /c/Users/Jhond/Github/iah-cli || exit 1

echo "== git rev-parse --short HEAD"
git rev-parse --short HEAD

echo "== git log --find-renames --stat -1 84282c1 -- .opencode/plans"
git log --find-renames --stat -1 84282c1 -- .opencode/plans

echo "== git ls-files .opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/ (rutas)"
git ls-files .opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/

echo "== conteo git ls-files bajo Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/"
git ls-files .opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/ | grep -c '/'

echo "== conteo git ls-files bajo .opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/ (sin Archives)"
git ls-files .opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/ | grep -c '/' ; echo "EXIT_GREP=$?"

echo "== conteo en disco bajo Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/ (find -type f)"
find .opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/ -type f | wc -l

echo "== existencia del directorio no-archivado en el arbol de trabajo"
ls -d .opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/ 2>&1 ; echo "EXIT_LS=$?"

echo "== planes vivos hoy en .opencode/plans/ (solo primeros niveles)"
ls .opencode/plans/

echo "== scores de renombre (raw) en 84282c1 bajo .opencode/plans"
git log --find-renames --raw -1 84282c1 -- .opencode/plans

echo "== renombres R### de 84282c1 sobre el plan JEV (git show --name-status -M)"
git show --name-status -M --format='' 84282c1 | grep -E '^R[0-9]+' | grep 'EVALUACION-JEV-TYPESAFE-2026-09-21'

echo "== conteo de renombres R100 / R089 / R099 sobre el plan JEV"
for score in R100 R089 R099; do
  n=$(git show --name-status -M --format='' 84282c1 | grep -E "^$score" | grep -c 'EVALUACION-JEV-TYPESAFE-2026-09-21')
  echo "$score=$n"
done

echo "== commit que archiva el plan: git log --diff-filter=R --oneline -- .opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/"
git log --diff-filter=R --oneline -- .opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/

echo "== 84282c1 es ancestro de HEAD?"
git merge-base --is-ancestor 84282c1 HEAD && echo "SI-ANCESTRO" || echo "NO-ANCESTRO"
