"""Verificacion POST del write-back: la fuente ya esta subida, aqui se prueba que baj6 y casa.

Re-corre el `50-` NO: volver a subir crearia una fuente duplicada (la leccion de idempotencia por clave).
Este arnes solo lee el servidor.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
HOJA = (RAIZ / ".opencode" / "plans" / "Archives" / "EVALUACION-JEV-TYPESAFE-2026-09-21" /
        "10-analisis-post-implementacion.md")
NB = "01a04d98-b7bd-778c-8441-26fdc7e35f45"
NUEVA = "01a10ec9-8113-7875-a806-2eec6521d37a"
STEM = "10-analisis: EVALUACION-JEV-TYPESAFE-2026-09-21"
PREVIAS = ("01a10e39-1625", "01a10853-6da2", "01a0e4d9-b252", "01a0efcc-3297")
URL = re.compile(r"https?://\S+")
CAMPOS = re.compile(r'"(originUrl|originalFileUri|downloadUrl|signedUrl)"\s*:\s*"[^"]*"')


def red(t):
    return URL.sub("[URL-REDACTADA]", CAMPOS.sub(r'"\1": "[REDACTADA]"', t or ""))


def qmind(args):
    exe = shutil.which("qmind")
    proc = subprocess.run([exe, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=300)
    return proc.returncode, red((proc.stdout or "") + (proc.stderr or ""))


def sha(b):
    return hashlib.sha256(b).hexdigest()


disco = HOJA.read_bytes()
print("== disco que se publico: %d B | sha256 %s" % (len(disco), sha(disco)))

print("== 1. estado de la fuente nueva en el listado")
rc, out = qmind(["source", "list", "--nb", NB, "--all", "--format", "json"])
fuentes = json.loads(out[out.find("{"):]).get("sources") or []
por = {f.get("id"): f for f in fuentes}
print("   rc=%d | fuentes = %d" % (rc, len(fuentes)))
n = por.get(NUEVA)
if not n:
    print("   [NO-EVALUABLE] la fuente nueva no aparece todavia en el listado")
else:
    m = n.get("metadata") or {}
    print("   status=%s | fileSha256=%s | fileSize=%s | title=%r"
          % (n.get("status"), m.get("fileSha256"), m.get("fileSize"), (n.get("title") or "")[:80]))
    print("   casa_con_disco: sha=%s size=%s" % (m.get("fileSha256") == sha(disco),
                                                 m.get("fileSize") == len(disco)))

print("== 2. verificacion fuerte: descargar la fuente nueva y comparar por sha")
scratch = Path(tempfile.mkdtemp(prefix="post-"))
racha = []
bajado = None
try:
    for i in range(1, 6):
        destino = scratch / ("post-%d.bin" % i)
        rc_d, sal_d = qmind(["source", "download", "--nb", NB, NUEVA, "-o", str(destino)])
        if rc_d == 0 and destino.is_file():
            racha.append(0)
            bajado = destino.read_bytes()
            print("   intento %d: exit=0 | %d B" % (i, len(bajado)))
            break
        racha.append(1)
        print("   intento %d: exit=%d | %s" % (i, rc_d, (sal_d.strip().splitlines() or [""])[0][:70]))
        time.sleep(3)
finally:
    shutil.rmtree(scratch, ignore_errors=True)
print("   RACHA POST = %s (intentos declarados, AC-4)" % "-".join(str(x) for x in racha))
if bajado is None:
    print("   [NO-EVALUABLE] no bajo: NO se declara publicada la fuente")
    sys.exit(1)
print("   bajado %d B | sha256 %s" % (len(bajado), sha(bajado)))
print("   IGUAL AL DISCO = %s" % (bajado == disco))

print("== 3. las fuentes previas, intactas")
for p in PREVIAS:
    for k in [x for x in por if (x or "").startswith(p)]:
        print("   %s… status=%s title=%r" % (k[:22], por[k].get("status"),
                                             (por[k].get("title") or "")[:62]))
stem = [f for f in fuentes if STEM in (f.get("title") or "")]
print("   fuentes que conservan el stem: %d | todas ready: %s"
      % (len(stem), all(f.get("status") == "ready" for f in stem)))

print("== 4. el verificador curado, sobre el arbol ya publicado")
proc = subprocess.run([sys.executable, str(RAIZ / "scripts" / "verify_qmind_context_freshness.py"),
                       "--strict"], cwd=str(RAIZ), capture_output=True, text=True,
                      encoding="utf-8", errors="replace", timeout=600)
lineas = (proc.stdout or "").splitlines()
for l in lineas:
    if l.startswith("  [FRESCO]") or l.startswith("  [VENCIDO]") or l.startswith("  [NO-EVALUABLE]") \
       or l.startswith("  [SIN-DESCARGA]") or l.startswith("  [PROMESA-ROTA]") or l.startswith("[") \
       or l.startswith("notebook "):
        print("   " + red(l)[:170])
print("   FRESHNESS_EXIT=%d" % proc.returncode)

print("== 5. el hermano que decide por titulo")
p2 = subprocess.run([sys.executable, str(RAIZ / "scripts" / "validate_qmind_writeback.py"),
                     "--strict"], cwd=str(RAIZ), capture_output=True, text=True,
                    encoding="utf-8", errors="replace", timeout=600)
for l in (p2.stdout or "").splitlines():
    if l.startswith("[") or "PASS" in l or "FAIL" in l:
        print("   " + red(l)[:170])
print("   WRITEBACK_STRICT_EXIT=%d" % p2.returncode)
