#!/bin/sh
# F4 - los totales del git grep sobre HEAD, sumados con awk (el crudo 31 imprime file:count y se
# queda sin suma; contar lineas de un grep -c no es el total). Ancla con backtick, como nombra la fila.
D="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29"
{
  echo "### F4 totales por ancla, sobre revisiones fijas (LINEAS sumadas con awk)"
  echo "### comando: git grep -c -F '<ancla>' <rev> -- '*.md' | awk -F: '{t+=\$NF} END {print t+0}'"
  for rev in HEAD 3c2e6a3 e5a654b; do
    echo "-- revision $rev"
    for pat in '`.opencode/plans/Archives' '`/.opencode/plans/Archives' '`.opencode' '`/.opencode'; do
      s=$(git grep -c -F "$pat" "$rev" -- '*.md' | awk -F: '{t+=$NF} END {print t+0}')
      printf "   %-32s -> %s lineas\n" "$pat" "$s"
    done
  done
  echo
  echo "### contraste con lo que midio la sesion del 2026-09-28 (crudo 05, sobre HEAD de entonces)"
  echo "   ancla del mandato: 166 lineas   ancla ancha: 564 lineas   (HEAD = 84c1aca mas la tanda)"
  echo "   par declarado en la fila S17: 518 contra 66"
  echo
  echo "### poblacion del corpus marcado"
  echo "-- .md versionados en HEAD: $(git ls-files '*.md' | wc -l)"
  echo "-- .md en el arbol de 3c2e6a3: $(git ls-tree -r --name-only 3c2e6a3 | grep -c '\.md$')"
  echo "-- git rev-parse --short HEAD: $(git rev-parse --short HEAD)"
  echo "-- git grep -c cuenta LINEAS; str.count cuenta OCURRENCIAS (crudo 30b)"
} > "$D/35-f4-totales-por-revision.txt" 2>&1
echo "EXIT_F4_TOTALES=$?" >> "$D/35-f4-totales-por-revision.txt"
