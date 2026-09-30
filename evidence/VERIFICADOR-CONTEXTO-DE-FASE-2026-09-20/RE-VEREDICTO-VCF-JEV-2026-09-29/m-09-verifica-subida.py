import hashlib
import json
import os
import subprocess
import sys

D = sys.argv[1]
NB = sys.argv[2]
TITULO = sys.argv[3]
DISCO = os.path.join(os.getcwd(), ".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/10-analisis-post-implementacion.md")
STEM = "10-analisis: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"

R = []


def huellas(b):
    return {
        "bytes": len(b),
        "sha": hashlib.sha256(b).hexdigest(),
        "sha_norm": hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest(),
        "CR": b.count(b"\r"),
        "LF": b.count(b"\n"),
    }


with open(os.path.join(D, "09-source-list-post-t1.json"), encoding="utf-8") as f:
    lista = json.load(f)
fuentes = lista if isinstance(lista, list) else (lista.get("sources") or lista.get("data") or [])
with open(os.path.join(D, "01-source-list.json"), encoding="utf-8") as f:
    pre = json.load(f)
fuentes_pre = pre if isinstance(pre, list) else (pre.get("sources") or pre.get("data") or [])

R.append("== T1 - verificacion de la re-ingesta por DESCARGA + sha256 ==")
R.append("poblacion PRE  : %d fuentes" % len(fuentes_pre))
R.append("poblacion POST : %d fuentes" % len(fuentes))
R.append("delta poblacion: %+d" % (len(fuentes) - len(fuentes_pre)))
R.append("")
R.append("fuentes que llevan el stem %r:" % STEM)
nueva = None
for f in fuentes:
    t = f.get("title") or f.get("name") or ""
    sid = f.get("id") or f.get("sourceId")
    if STEM in t:
        marcado = ""
        if t == TITULO:
            marcado = "   <== LA NUEVA (titulo exacto pedido)"
            nueva = sid
        R.append("    %s  status=%s  %r%s" % (sid, f.get("status"), t, marcado))
R.append("")

if nueva is None:
    R.append("FALLO: ninguna fuente lleva el titulo exacto pedido.")
else:
    destino = os.path.join(D, "descarga-%s.md" % nueva)
    p = subprocess.run(["qmind", "source", "download", nueva, "--nb", NB, "-o", destino, "--overwrite"],
                       capture_output=True, text=True)
    R.append("comando : qmind source download %s --nb %s -o descarga-%s.md --overwrite" % (nueva, NB, nueva))
    R.append("exit    : %d" % p.returncode)
    if p.stdout.strip():
        R.append("stdout  : %s" % p.stdout.strip()[:400])
    if p.stderr.strip():
        R.append("stderr  : %s" % p.stderr.strip()[:400])
    with open(destino, "rb") as fh:
        bdl = fh.read()
    with open(DISCO, "rb") as fh:
        bdis = fh.read()
    ha, hb = huellas(bdl), huellas(bdis)
    R.append("DESCARGA : bytes=%d sha=%s sha_norm=%s CR=%d LF=%d" % (ha["bytes"], ha["sha"], ha["sha_norm"], ha["CR"], ha["LF"]))
    R.append("DISCO    : bytes=%d sha=%s sha_norm=%s CR=%d LF=%d" % (hb["bytes"], hb["sha"], hb["sha_norm"], hb["CR"], hb["LF"]))
    R.append("identico_crudo=%s  identico_normalizando_CRLF=%s" % (ha["sha"] == hb["sha"], ha["sha_norm"] == hb["sha_norm"]))
    R.append("delta bytes descarga-disco = %+d" % (ha["bytes"] - hb["bytes"]))
    R.append("VEREDICTO: %s" % ("FRESCA (la re-ingesta publico el contenido de disco)" if ha["sha"] == hb["sha"] else "NO CASA"))
    R.append("")
    R.append("La fuente anterior del mismo plan sigue en el notebook con su titulo original:")
    for f in fuentes:
        t = f.get("title") or f.get("name") or ""
        sid = f.get("id") or f.get("sourceId")
        if STEM in t and sid != nueva:
            R.append("    %s  %r" % (sid, t))
    R.append("Esa es la forma que ya publica el plan TRIBUNAL-OFFLINE (version original + version de cierre),")
    R.append("no un gemelo por repeticion de titulo.")

with open(os.path.join(D, "10-t1-verificacion.txt"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(R) + "\n")
print("ESCRITO 10-t1-verificacion.txt")
print("NUEVA_ID %s" % nueva)
