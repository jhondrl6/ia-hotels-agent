#!/bin/bash
# Instrumento m-01: re-medicion HOY de la divergencia del CONTEXT de JEV, por DESCARGA + sha256 contra disco.
# La descarga es la fuente del criterio; metadata.fileSha256 del servidor es corroboracion aparte.
E="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"
NB="01a04d98-b7bd-778c-8441-26fdc7e35f45"
SRC="01a0e4d9-e442-7d1b-bde5-7e9b669a2701"
F=".opencode/context/CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21.md"
D="$E/descarga-$SRC.md"
O="$E/01-re-medicion-divergencia-hoy.txt"

qmind source download "$SRC" --nb "$NB" -o "$D" --overwrite --non-interactive > "$E/01b-descarga.txt" 2>&1
EXDL=$?
{
  echo "fecha_medicion=$(date +%F)  hora=$(date -Iseconds)"
  echo "fuente=$SRC"
  echo "notebook=$NB"
  echo "salida_descarga (01b-descarga.txt):"
  cat "$E/01b-descarga.txt"
  echo "EXIT_DESCARGA=$EXDL"
  echo
  echo "== DESCARGA =="
  ls -l "$D"
  echo "bytes_descarga=$(wc -c < "$D")"
  sha256sum "$D"
  echo "CR_descarga=$(tr -dc '\r' < "$D" | wc -c)"
  echo "LF_descarga=$(tr -dc '\n' < "$D" | wc -c)"
  echo
  echo "== DISCO =="
  ls -l "$F"
  echo "bytes_disco=$(wc -c < "$F")"
  sha256sum "$F"
  echo "CR_disco=$(tr -dc '\r' < "$F" | wc -c)"
  echo "LF_disco=$(tr -dc '\n' < "$F" | wc -c)"
  echo
  echo "== CONTRASTE =="
  B_DESC=$(wc -c < "$D")
  B_DISC=$(wc -c < "$F")
  echo "delta_bytes_disco_menos_descarga=$((B_DISC - B_DESC))"
  S1=$(sha256sum "$D" | cut -d' ' -f1)
  S2=$(sha256sum "$F" | cut -d' ' -f1)
  if [ "$S1" = "$S2" ]; then echo "shas_iguales=SI (la divergencia DESAPARECIO: PARAR)"; else echo "shas_iguales=NO (sigue VENCIDA)"; fi
  echo "sha_descarga=$S1"
  echo "sha_disco=$S2"
  echo
  echo "== DIFF (numero de linea y contenido) =="
  diff "$D" "$F"
  echo "DIFF_EXIT=$?"
} > "$O" 2>&1
echo "EXIT_BLOQUE=$?"
echo "salida=$O"
