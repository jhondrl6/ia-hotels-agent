#!/bin/bash
# Instrumento m-20: normalizacion de los crudos a LF, sin tocar las descargas (su sha ES la evidencia).
# Causa medida: el stdout de Python bajo Windows traduce \n a \r\n, y el redirect del shell lo guarda tal cual.
E="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"
# O es relativo A LA CARPETA: el script hace cd antes de abrir el redirect, y una ruta de repo raiz
# ya no resuelve desde aqui (fallo medido: el block ni se ejecuto).
O="30-normalizacion-eol-de-crudos.txt"
cd "$E" || exit 1

{
  echo "fecha=$(date +%F)  hora=$(date -Iseconds)"
  echo "== antes =="
  con=0; sin=0
  for f in *; do [ -f "$f" ] || continue; n=$(tr -dc '\r' < "$f" | wc -c)
    if [ "$n" -gt 0 ]; then con=$((con+1)); else sin=$((sin+1)); fi; done
  echo "con_CR=$con  sin_CR=$sin"
  echo "descargas_y_reconfirmacion (intocables, ya en LF):"
  for f in descarga-01a0e4d9-e442-7d1b-bde5-7e9b669a2701.md descarga-01a0efcc-3297-7782-9467-757fe81018fc.md 17b-reconfirmacion-01a0efcc-3297-7782-9467-757fe81018fc.md; do
    echo "  $f CR=$(tr -dc '\r' < "$f" | wc -c) bytes=$(wc -c < "$f") sha=$(sha256sum "$f" | cut -d' ' -f1)"
  done

  echo "== normalizando (excluidas las tres descargas) =="
  tocados=0
  for f in *; do
    [ -f "$f" ] || continue
    case "$f" in
      descarga-*.md|17b-*.md) continue ;;
    esac
    # el archivo de salida de ESTE bloque esta abierto por el shell: sed -i sobre el huerfana el
    # descriptor y se pierde toda la medida. Se excluye por nombre.
    if [ "$f" = "30-normalizacion-eol-de-crudos.txt" ]; then continue; fi
    antes=$(wc -c < "$f")
    sed -i 's/\r$//' "$f"
    despues=$(wc -c < "$f")
    if [ "$antes" != "$despues" ]; then tocados=$((tocados+1)); fi
  done
  echo "archivos_reducidos=$tocados"

  con2=0; sin2=0
  for f in *; do [ -f "$f" ] || continue; n=$(tr -dc '\r' < "$f" | wc -c)
    if [ "$n" -gt 0 ]; then con2=$((con2+1)); else sin2=$((sin2+1)); fi; done
  echo "con_CR_despues=$con2  sin_CR_despues=$sin2"

  echo "== las descargas siguen intactas (sha por identidad, no por confianza) =="
  for f in descarga-01a0e4d9-e442-7d1b-bde5-7e9b669a2701.md descarga-01a0efcc-3297-7782-9467-757fe81018fc.md 17b-reconfirmacion-01a0efcc-3297-7782-9467-757fe81018fc.md; do
    echo "  $f CR=$(tr -dc '\r' < "$f" | wc -c) bytes=$(wc -c < "$f") sha=$(sha256sum "$f" | cut -d' ' -f1)"
  done
} > "$O" 2>&1
echo "EXIT_BLOQUE=$?"
cat "$O"
