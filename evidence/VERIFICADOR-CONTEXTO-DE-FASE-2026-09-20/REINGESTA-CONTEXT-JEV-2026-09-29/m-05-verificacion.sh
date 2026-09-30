#!/bin/bash
# Instrumento m-05: espera a status=ready y VERIFICACION POR DESCARGA + sha256 contra el archivo local.
# El criterio es la descarga; metadata.fileSha256 del servidor es corroboracion aparte, no el criterio.
E="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"
NB="01a04d98-b7bd-778c-8441-26fdc7e35f45"
F=".opencode/context/CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21.md"
SRC_NEW=$(cat "$E/04a-id-nueva.txt")
SRC_NEW=${SRC_NEW//$'\r'/}
D="$E/descarga-$SRC_NEW.md"
GJ="$E/05-get-$SRC_NEW.json"

{
  echo "fecha_verificacion=$(date +%F)  hora=$(date -Iseconds)"
  echo "fuente_nueva=$SRC_NEW"
} > "$E/05a-espera-status.txt" 2>&1

for i in 1 2 3 4 5 6 7 8 9 10; do
  qmind source get "$SRC_NEW" --nb "$NB" --format json --non-interactive > "$GJ" 2>/dev/null
  EXG=$?
  ST=$(python -c "
import json,sys
d=json.load(open(sys.argv[1],encoding='utf-8'))
n=d.get('data',d) if isinstance(d,dict) else d
print(n.get('status',''))
" "$GJ" 2>/dev/null)
  echo "intento=$i EXIT_GET=$EXG status=$ST" >> "$E/05a-espera-status.txt"
  if [ "$ST" = "ready" ]; then break; fi
  sleep 5
done
cat "$E/05a-espera-status.txt"

qmind source download "$SRC_NEW" --nb "$NB" -o "$D" --overwrite --non-interactive > "$E/05b-descarga-nueva.txt" 2>&1
EXD=$?
{
  echo
  echo "== DESCARGA DE LA FUENTE NUEVA =="
  cat "$E/05b-descarga-nueva.txt"
  echo "EXIT_DESCARGA=$EXD"
  ls -l "$D"
  echo "bytes_descarga=$(wc -c < "$D")"
  echo "sha_descarga=$(sha256sum "$D" | cut -d' ' -f1)"
  echo "CR_descarga=$(tr -dc '\r' < "$D" | wc -c)"
  echo "LF_descarga=$(tr -dc '\n' < "$D" | wc -c)"
  echo
  echo "== ARCHIVO LOCAL =="
  echo "bytes_local=$(wc -c < "$F")"
  echo "sha_local=$(sha256sum "$F" | cut -d' ' -f1)"
  echo "CR_local=$(tr -dc '\r' < "$F" | wc -c)"
  echo "LF_local=$(tr -dc '\n' < "$F" | wc -c)"
  echo
  echo "== CRITERIO =="
  B1=$(wc -c < "$D"); B2=$(wc -c < "$F")
  S1=$(sha256sum "$D" | cut -d' ' -f1); S2=$(sha256sum "$F" | cut -d' ' -f1)
  echo "delta_bytes=$((B1 - B2))"
  if [ "$S1" = "$S2" ]; then echo "identico_crudo=True"; else echo "identico_crudo=False  (PARAR y diagnosticar en aislado)"; fi
  echo
  echo "== DIFF (debe estar vacio) =="
  diff "$D" "$F"
  echo "DIFF_EXIT=$?"
  echo
  echo "== CORROBORACION DEL SERVIDOR (aparte, no el criterio) =="
  python -c "
import json,sys
d=json.load(open(sys.argv[1],encoding='utf-8'))
n=d.get('data',d) if isinstance(d,dict) else d
md=n.get('metadata') or {}
print('status=%s' % n.get('status'))
print('title=%s' % n.get('title'))
print('metadata.fileSha256=%s' % md.get('fileSha256'))
print('metadata.fileSize=%s' % md.get('fileSize'))
" "$GJ"
} >> "$E/05a-espera-status.txt" 2>&1
echo "EXIT_BLOQUE=$?"
cat "$E/05a-espera-status.txt"
