#!/bin/bash
# Instrumento m-14: control final de la tanda, sobre el expediente nuevo y sobre el estado publicado del notebook.
# Re-bare el barrido de credenciales (hay mas archivos que cuando corrio 11-) y re-descarga la fuente nueva.
E="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"
NB="01a04d98-b7bd-778c-8441-26fdc7e35f45"
MD="$E/00-expediente.md"
SRC_NEW=$(cat "$E/04a-id-nueva.txt")
SRC_NEW=${SRC_NEW//$'\r'/}
F=".opencode/context/CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21.md"

python "$E/m-11-barrido-final.py" > "$E/16-barrido-final-repetido.txt" 2>&1
B=$?

{
  echo "fecha_cierre=$(date +%F)  hora=$(date -Iseconds)"
  echo "== self-control del expediente nuevo =="
  echo "bytes=$(wc -c < "$MD")"
  echo "lineas=$(wc -l < "$MD")"
  echo "CR=$(tr -dc '\r' < "$MD" | wc -c)"
  echo "backticks=$(tr -dc '`' < "$MD" | wc -c)"
  AP=$(python -c "print(chr(0x27E6).encode().decode())")
  CI=$(python -c "print(chr(0x27E7).encode().decode())")
  echo "apertura_anadida_para_citar_la_forma=$(grep -o "$AP" "$MD" | wc -l)"
  echo "cierre_anadido_para_citar_la_forma=$(grep -o "$CI" "$MD" | wc -l)"
  echo "== secciones =="
  grep -n "^## " "$MD"
  echo "== barrido de credenciales repetido (m-11, ya con todos los archivos) =="
  echo "EXIT_BARRIDO=$B"
  cat "$E/16-barrido-final-repetido.txt"
} > "$E/17-cierre-y-self-control.txt" 2>&1

qmind source download "$SRC_NEW" --nb "$NB" -o "$E/17b-reconfirmacion-$SRC_NEW.md" --overwrite --non-interactive > "$E/17c-reconfirmacion.txt" 2>&1
EXD=$?
{
  echo "== reconfirmacion FINAL de la fuente publicada (descarga + sha256 contra disco) =="
  cat "$E/17c-reconfirmacion.txt"
  echo "EXIT_DESCARGA=$EXD"
  echo "bytes_descarga=$(wc -c < "$E/17b-reconfirmacion-$SRC_NEW.md")"
  echo "sha_descarga=$(sha256sum "$E/17b-reconfirmacion-$SRC_NEW.md" | cut -d' ' -f1)"
  echo "bytes_disco=$(wc -c < "$F")"
  echo "sha_disco=$(sha256sum "$F" | cut -d' ' -f1)"
  diff "$E/17b-reconfirmacion-$SRC_NEW.md" "$F" > /dev/null 2>&1
  echo "DIFF_EXIT=$?  (0 = la fuente publicada casa con el disco: divergence CERRADA)"
} >> "$E/17-cierre-y-self-control.txt" 2>&1
cat "$E/17-cierre-y-self-control.txt"
