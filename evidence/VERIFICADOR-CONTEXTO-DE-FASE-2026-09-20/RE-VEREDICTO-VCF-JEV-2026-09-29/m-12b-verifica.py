import hashlib
import json
import os
import sys

D, TITULO = sys.argv[1], sys.argv[2]
DISCO = os.path.join(os.getcwd(), ".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/10-analisis-post-implementacion.md")
STEM = "10-analisis: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
PRE = "01-source-list.json"
POST = "09-source-list-post-t1.json"


def fuentes_de(nombre):
    d = json.load(open(os.path.join(D, nombre), encoding="utf-8"))
    return d if isinstance(d, list) else (d.get("sources") or d.get("data") or [])


def sha(b):
    return hashlib.sha256(b).hexdigest()


a = fuentes_de(PRE)
b = fuentes_de(POST)
R = []
R.append("== T1 - verificacion de la re-ingesta por DESCARGA + sha256 ==")
R.append("comando de subida : qmind source upload --non-interactive --format json --nb %s --file <10-analisis VCF> --title \"%s\"" % (b and "01a04d98-b7bd-778c-8441-26fdc7e35f45", TITULO))
R.append("comando de lista  : qmind source list --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 --all --format json")
R.append("poblacion PRE  (01-source-list.json)        : %d fuentes" % len(a))
R.append("poblacion POST (09-source-list-post-t1.json): %d fuentes" % len(b))
R.append("delta de poblacion: %+d" % (len(b) - len(a)))
R.append("")
R.append("== Fuentes del plan VCF en el POST (stem %r) ==" % STEM)
nueva = None
for f in b:
    t = f.get("title") or ""
    if STEM in t:
        md = f.get("metadata") or {}
        marca = ""
        if t == TITULO:
            nueva = f
            marca = "   <== la nueva"
        R.append("    id=%s" % f.get("id"))
        R.append("      status=%s  title=%r" % (f.get("status"), t))
        R.append("      metadata.fileSha256=%s  fileSize=%s  originalFileSize=%s%s"
                 % (md.get("fileSha256"), md.get("fileSize"), md.get("originalFileSize"), marca))
R.append("")

if nueva is None:
    R.append("FALLO: el titulo exacto pedido no aparece en el listado POST.")
else:
    sid = nueva.get("id")
    dest = os.path.join(D, "descarga-%s.md" % sid)
    if not os.path.exists(dest):
        R.append("FALLO: no hay descarga en %s (ver 12b-descarga-nueva.log)" % dest)
    else:
        bd = open(dest, "rb").read()
        bk = open(DISCO, "rb").read()
        R.append("== Descarga de la fuente nueva vs el archivo en disco ==")
        R.append("comando : qmind source download %s --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 -o descarga-%s.md --overwrite" % (sid, sid))
        R.append("DESCARGA : bytes=%d sha256=%s CR=%d LF=%d" % (len(bd), sha(bd), bd.count(b"\r"), bd.count(b"\n")))
        R.append("DISCO    : bytes=%d sha256=%s CR=%d LF=%d" % (len(bk), sha(bk), bk.count(b"\r"), bk.count(b"\n")))
        R.append("identico_crudo=%s   delta bytes descarga-disco = %+d" % (sha(bd) == sha(bk), len(bd) - len(bk)))
        md = nueva.get("metadata") or {}
        R.append("corroboracion aparte: metadata.fileSha256 del servidor == sha del disco: %s"
                 % (md.get("fileSha256") == sha(bk)))
        R.append("VEREDICTO: %s" % ("FRESCA - la re-ingesta publico el contenido de disco" if sha(bd) == sha(bk) else "NO CASA"))
        R.append("")
        R.append("La fuente anterior del mismo plan (%s) sigue en el notebook con su titulo original" % "01a0e464-3331-7684-9742-f64e009fb10b")
        R.append("y el gemelo pendiente de borrado (%s) tambien. Forma precedente en la casa:" % "01a0e0d3-92db-795b-ad7a-48a7c322e8e9")
        R.append("TRIBUNAL-OFFLINE-2026-09-09 publica version original + version de cierre con titulos distintos.")
        R.append("El caso a borrar por T2 es el que repite TITULO exacto, no la version de cierre anterior.")

with open(os.path.join(D, "12-t1-verificacion-por-descarga.txt"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(R) + "\n")
print("ESCRITO 12-t1-verificacion-por-descarga.txt")
