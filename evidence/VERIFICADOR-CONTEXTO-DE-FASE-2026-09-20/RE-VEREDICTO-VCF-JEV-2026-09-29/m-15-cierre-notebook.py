import json
import os
import re
import sys

D = sys.argv[1]
ID_BORRADO = sys.argv[2]
STEM = "10-analisis: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
REDACTADO = "REDACTADA-URL-DE-OBJETO-FIRMADA-ver-11-redaccion-url-firmadas.txt"
URL_FIRMADA = re.compile(r"https://\S*x-oss-signature\S*")
TOKEN = re.compile(r"x-oss-credential|x-oss-signature|x-oss-date|x-oss-expires")


def cargar(nombre):
    d = json.load(open(os.path.join(D, nombre), encoding="utf-8"))
    return d if isinstance(d, list) else (d.get("sources") or d.get("data") or [])


R = []
R.append("== T2 - cierre del notebook despues del borrado del gemelo ==")
R.append("comando : qmind source delete %s --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 --force" % ID_BORRADO)
R.append("salida y exit: en 14-t2-delete.txt; pre-estado de la fuente: 13-pre-borrado-get.txt")
R.append("")

# 1) Redaccion del listado POST-T2 (estructural) y de los crudos de texto (por regex)
p16 = os.path.join(D, "16-source-list-post-t2.json")
doc = json.load(open(p16, encoding="utf-8"))


def toca(o):
    if isinstance(o, dict):
        for k, v in list(o.items()):
            if k in ("originUrl", "downloadUrl", "url", "signedUrl", "originalFileUri") and isinstance(v, str) and v:
                o[k] = REDACTADO
            else:
                toca(v)
    elif isinstance(o, list):
        for e in o:
            toca(e)


toca(doc)
with open(p16, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")

txt_redactados = []
for nombre in ["13-pre-borrado-get.txt", "14-t2-delete.txt", "15-post-borrado-tabla.txt"]:
    p = os.path.join(D, nombre)
    if not os.path.exists(p):
        continue
    c = open(p, encoding="utf-8", errors="replace").read()
    n = len(URL_FIRMADA.findall(c))
    if n:
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(URL_FIRMADA.sub(REDACTADO, c))
    txt_redactados.append("%s : %d URLs firmadas sustituidas" % (nombre, n))

post = cargar("16-source-list-post-t2.json")
pre = cargar("01-source-list.json")
p1 = cargar("09-source-list-post-t1.json")
R.append("== Poblacion del notebook ==")
R.append("PRE  (01)            : %d fuentes" % len(pre))
R.append("POST T1 (09)         : %d fuentes" % len(p1))
R.append("POST T2 (16)         : %d fuentes" % len(post))
R.append("delta T1 = %+d ; delta T2 = %+d ; neto contra el PRE = %+d"
         % (len(p1) - len(pre), len(post) - len(p1), len(post) - len(pre)))
R.append("")

R.append("== Ausencia del id borrado ==")
ids = [f.get("id") for f in post]
R.append("id presente en el POST-T2 (json)      : %s" % (ID_BORRADO in ids))
tabla = open(os.path.join(D, "15-post-borrado-tabla.txt"), encoding="utf-8", errors="replace").read()
R.append("id presente en el POST-T2 (tabla)     : %s" % (ID_BORRADO in tabla))
R.append("Total impreso por la tabla            : %s" % [l for l in tabla.splitlines() if l.startswith("Total")])
R.append("menciones del id en TODO el dir menos sus propios crudos de T2: %d"
         % sum(len(re.findall(ID_BORRADO, open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read()))
               for dp, _, fns in os.walk(D) for fn in fns
               if not fn.startswith("m-") and fn not in ("13-pre-borrado-get.txt", "14-t2-delete.txt",
                                                          "12-t1-verificacion-por-descarga.txt",
                                                          "03-comparacion-snapshots.txt",
                                                          "17-cierre-notebook-post-t2.txt",
                                                          "11-redaccion-url-firmadas.txt")))
R.append("")

R.append("== Fuentes del plan VCF que quedan en el notebook ==")
for f in post:
    t = f.get("title") or ""
    if STEM in t:
        md = f.get("metadata") or {}
        R.append("    id=%s status=%s bytes=%s sha=%s" % (f.get("id"), f.get("status"), md.get("fileSize"), md.get("fileSha256")))
        R.append("      title=%r" % t)
R.append("")
R.append("== Titulos duplicados en el notebook (control de que no queda un segundo gemelo) ==")
veces = {}
for f in post:
    veces[f.get("title")] = veces.get(f.get("title"), 0) + 1
dup = {k: v for k, v in veces.items() if v > 1}
if dup:
    for k, v in sorted(dup.items()):
        R.append("    %d x  %r" % (v, k))
else:
    R.append("    0 titulos repetidos")
R.append("")
R.append("== Redaccion de URLs firmadas en los crudos de esta tanda ==")
for s in txt_redactados:
    R.append("    " + s)
sup = []
for dp, _, fns in os.walk(D):
    for fn in fns:
        if fn.startswith("m-") or fn in ("11-redaccion-url-firmadas.txt", "17-cierre-notebook-post-t2.txt"):
            continue
        c = open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read()
        n = len(TOKEN.findall(c))
        if n:
            sup.append("%s : %d" % (fn, n))
R.append("    supervivientes del barrido (excluidos instrumentos y el propio informe): %d" % len(sup))
for s in sup:
    R.append("      " + s)

with open(os.path.join(D, "17-cierre-notebook-post-t2.txt"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(R) + "\n")
print("ESCRITO 17-cierre-notebook-post-t2.txt")
print("POST_T2=%d" % len(post))
