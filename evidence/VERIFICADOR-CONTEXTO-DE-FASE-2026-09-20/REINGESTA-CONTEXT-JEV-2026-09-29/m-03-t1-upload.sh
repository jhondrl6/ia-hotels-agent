#!/bin/bash
# Instrumento m-03: T1, la UNICA escritura del notebook prevista por la orden.
# Re-ingesta del CONTEXT de JEV con titulo NUEVO que conserva el stem (repetir el titulo responderia [SKIP]).
# Todo por shell: qmind no resuelve desde subprocess de Python en Windows.
E="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"
NB="01a04d98-b7bd-778c-8441-26fdc7e35f45"
F=".opencode/context/CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21.md"
T="CONTEXT: CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21 (cierre 2026-09-29, plan archivado en Archives)"

{
  echo "fecha_upload=$(date +%F)  hora=$(date -Iseconds)"
  echo "archivo=$F"
  echo "bytes_local=$(wc -c < "$F")"
  echo "sha_local=$(sha256sum "$F" | cut -d' ' -f1)"
  echo "titulo_nuevo=$T"
} > "$E/03a-upload-pre.txt" 2>&1
echo "EXIT_PRE=$?"
cat "$E/03a-upload-pre.txt"

qmind source upload --non-interactive --format json --nb "$NB" --file "$F" --title "$T" > "$E/03-t1-upload.json" 2>"$E/03b-t1-upload-stderr.txt"
EXU=$?
echo "EXIT_UPLOAD=$EXU" | tee -a "$E/03a-upload-pre.txt"
echo "bytes_stdout_upload=$(wc -c < "$E/03-t1-upload.json")"
echo "-- stderr upload --"
cat "$E/03b-t1-upload-stderr.txt"
