#!/bin/bash
# F4 v2 — reproduccion del par 518/66 de la fila S17, con prueba de arbol limpio correcta
cd /c/Users/Jhond/Github/iah-cli || exit 1
D="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28"

echo "### 0. Estado del arbol al medir"
echo "-- git rev-parse --short HEAD"; git rev-parse --short HEAD
echo "-- git status --porcelain -uno | wc -l   (0 = el arbol versionado esta intacto; ignora no versionados)"
git status --porcelain -uno | wc -l
echo "-- git status --porcelain | wc -l   (incluye no versionados: esta propia carpeta de evidencia aparece como 1 linea colapsada)"
git status --porcelain | wc -l
echo "-- git status --porcelain (sin -uno, para ver que esa unica linea es la evidencia de esta sesion)"
git status --porcelain
echo "-- git config --get core.autocrlf"; git config --get core.autocrlf

echo
echo "### 1. Instrumento que nombra la fila: git grep -c sobre una revision, patron con backtick (LINEAS, no ocurrencias)"
for rev in HEAD 3c2e6a3; do
  echo "-- revision $rev"
  for pat in '`.opencode/plans/Archives' '`/.opencode/plans/Archives' '`.opencode' '`/.opencode'; do
    s=$(git grep -c -F "$pat" "$rev" -- '*.md' | awk -F: '{t+=$NF} END {print t+0}')
    printf "   git grep -c  %-30s -> %s lineas\n" "$pat" "$s"
  done
done

echo
echo "### 2. Contraste: el 0 falso documentado (patron que empieza por '/' sin el backtick)"
echo "-- git grep -c -F '/.opencode/plans/Archives' HEAD -> $(git grep -c -F '/.opencode/plans/Archives' HEAD -- '*.md' | awk -F: '{t+=$NF} END {print t+0}') lineas"

echo
echo "### 3. Ocurrencias por str.count sobre el arbol de trabajo (poblacion: .md versionados)"
python "$D/conteo_formas.py" "$D/06-f4-par-de-formas.txt"

echo
echo "### 4. Revision que introdujo la cifra y su par en su propio momento"
git log -S '518 contra 66' --oneline -- .opencode/plans | cat
echo "-- la linea hoy:"
grep -n '518 contra 66' .opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md
echo "-- .md versionados en HEAD: $(git ls-files '*.md' | wc -l)"
echo "-- .md en el arbol de 3c2e6a3: $(git ls-tree -r --name-only 3c2e6a3 | grep -c '\.md$')"
