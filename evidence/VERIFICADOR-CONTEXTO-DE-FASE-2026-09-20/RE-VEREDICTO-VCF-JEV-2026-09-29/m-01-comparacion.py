import hashlib
import json
import os
import sys

D = sys.argv[1]
REPO = os.getcwd()
NB = "01a04d98-b7bd-778c-8441-26fdc7e35f45"

PARES = [
    ("VCF 10-analisis", "01a0e464-3331-7684-9742-f64e009fb10b",
     ".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/10-analisis-post-implementacion.md"),
    ("JEV 10-analisis", "01a0e4d9-b252-7ca0-bf4c-9a9ecc7448f5",
     ".opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/10-analisis-post-implementacion.md"),
    ("JEV CONTEXT", "01a0e4d9-e442-7d1b-bde5-7e9b669a2701",
     ".opencode/context/CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21.md"),
    ("Leccion 43 Paso 0", "01a0ef0e-aa1c-7e5d-8486-51d40b8b4f07",
     "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/43-leccion-paso-0-2026-09-28.md"),
]
GEMELO = ("VCF 10-analisis GEMELO", "01a0e0d3-92db-795b-ad7a-48a7c322e8e9")


def medir_bytes(ruta):
    with open(ruta, "rb") as f:
        b = f.read()
    return b


def huellas(b):
    crudo = hashlib.sha256(b).hexdigest()
    norm = hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()
    cr = b.count(b"\r")
    lf = b.count(b"\n")
    crlf = b.count(b"\r\n")
    try:
        chars = len(b.decode("utf-8"))
    except UnicodeDecodeError:
        chars = -1
    return {
        "bytes": len(b),
        "sha_crudo": crudo,
        "sha_norm": norm,
        "CR": cr,
        "LF": lf,
        "CRLF": crlf,
        "chars": chars,
    }


lineas = []
out = os.path.join(D, "03-comparacion-snapshots.txt")

lista = json.load(open(os.path.join(D, "01-source-list.json"), encoding="utf-8"))
fuentes = lista if isinstance(lista, list) else lista.get("sources") or lista.get("data") or []
por_id = {}
for f in fuentes:
    sid = f.get("id") or f.get("sourceId") or f.get("source_id")
    por_id[sid] = f

lineas.append("== Paso 0 - medicion de snapshots del notebook por DESCARGA + sha256 ==")
lineas.append("notebook: %s" % NB)
lineas.append("poblacion del listado JSON: %d fuentes (Total impreso por la tabla: ver 00-source-list.txt)" % len(fuentes))
lineas.append("comando: qmind source list --nb %s --all --format json" % NB)
lineas.append("comando: qmind source download <source_id> --nb %s -o <destino> --overwrite" % NB)
lineas.append("")

for etiqueta, sid, disco in PARES:
    dl = os.path.join(D, "descarga-%s.md" % sid)
    dsk = os.path.join(REPO, disco)
    a = medir_bytes(dl)
    bb = medir_bytes(dsk)
    ha, hb = huellas(a), huellas(bb)
    identico_crudo = ha["sha_crudo"] == hb["sha_crudo"]
    identico_norm = ha["sha_norm"] == hb["sha_norm"]
    veredicto = "FRESCA" if identico_crudo else ("FRESCA-SOLO-NORMALIZANDO-CRLF (artefacto EOL)" if identico_norm else "VENCIDA")
    meta = por_id.get(sid, {})
    lineas.append("--- %s" % etiqueta)
    lineas.append("    source_id        : %s" % sid)
    lineas.append("    titulo publicado : %r" % (meta.get("title") or meta.get("name")))
    lineas.append("    status/updatedAt : %s / %s" % (meta.get("status"), meta.get("updatedAt")))
    lineas.append("    ruta en disco    : %s" % disco)
    lineas.append("    DESCARGA : bytes=%d sha_crudo=%s sha_norm=%s CR=%d LF=%d CRLF=%d chars=%d"
                  % (ha["bytes"], ha["sha_crudo"], ha["sha_norm"], ha["CR"], ha["LF"], ha["CRLF"], ha["chars"]))
    lineas.append("    DISCO    : bytes=%d sha_crudo=%s sha_norm=%s CR=%d LF=%d CRLF=%d chars=%d"
                  % (hb["bytes"], hb["sha_crudo"], hb["sha_norm"], hb["CR"], hb["LF"], hb["CRLF"], hb["chars"]))
    lineas.append("    DELTA    : bytes descarga - disco = %+d ; chars = %+d"
                  % (ha["bytes"] - hb["bytes"], ha["chars"] - hb["chars"]))
    lineas.append("    VEREDICTO: %s" % veredicto)
    lineas.append("")

etiqueta, sid = GEMELO
dl = os.path.join(D, "descarga-%s.md" % sid)
a = medir_bytes(dl)
ha = huellas(a)
dsk = os.path.join(REPO, PARES[0][2])
hb = huellas(medir_bytes(dsk))
meta = por_id.get(sid, {})
lineas.append("--- %s (pendiente de borrado; no tiene counterpart propio en disco)" % etiqueta)
lineas.append("    source_id        : %s" % sid)
lineas.append("    titulo publicado : %r" % (meta.get("title") or meta.get("name")))
lineas.append("    DESCARGA : bytes=%d sha_crudo=%s chars=%d" % (ha["bytes"], ha["sha_crudo"], ha["chars"]))
lineas.append("    contra el 10-analisis EN DISCO (bytes=%d sha=%s): identico_crudo=%s identico_norm=%s"
              % (hb["bytes"], hb["sha_crudo"], ha["sha_crudo"] == hb["sha_crudo"], ha["sha_norm"] == hb["sha_norm"]))
lineas.append("    delta bytes vs disco = %+d ; delta chars vs la otra fuente VCF publicada se lee arriba"
              % (ha["bytes"] - hb["bytes"]))
lineas.append("")

lineas.append("== Titles de las fuentes 10-analisis en el notebook (stem completo, para la re-ingesta) ==")
for f in fuentes:
    t = (f.get("title") or f.get("name") or "")
    if "10-analisis" in t:
        sid = f.get("id") or f.get("sourceId")
        lineas.append("    %s  %r" % (sid, t))

with open(out, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lineas) + "\n")

print("ESCRITO %s" % out)
print("FUENTES_JSON %d" % len(fuentes))
