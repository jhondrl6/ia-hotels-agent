import json
import os
import re
import sys

D = sys.argv[1]
REDACTADO = "REDACTADA-URL-DE-OBJETO-FIRMADA-ver-11-redaccion-url-firmadas.txt"

OBJETOS = ["01-source-list.json", "08-t1-upload.json", "09-source-list-post-t1.json"]
TOKEN = re.compile(r"x-oss-credential|x-oss-signature|x-oss-date|x-oss-expires")

R = []
R.append("== Redaccion de URLs firmadas en la evidencia de QMind ==")
R.append("Motivo: la salida del CLI trae en originUrl y metadata.originalFileUri una URL de objeto con")
R.append("credencial y firma (x-oss-credential / x-oss-signature / x-oss-date / x-oss-expires). La regla")
R.append("de la casa es no persistir esos enlaces en evidencia. Los campos se sustituyen por")
R.append("REDACTADA-URL-DE-OBJETO-FIRMADA; id, title, status, uri y metadata.fileSha256 se conservan,")
R.append("que es lo que sostiene la medicion.")
R.append("Re-ejecucion: la PRIMERA pasada (2026-09-29) conto ANTES=275 / 5 / 280 (TOTAL 560) con un")
R.append("marcador que contenia los propios tokens, asi que su DESPUES (448) estaba contaminado por el")
R.append("marcador: 4 ocurrencias por fuente sustituida. Esta pasada cambia el marcador y re-mide.")
R.append("")
total_antes = 0
total_despues = 0
for nombre in OBJETOS:
    p = os.path.join(D, nombre)
    if not os.path.exists(p):
        R.append("%s : AUSENTE" % nombre)
        continue
    con = open(p, encoding="utf-8").read()
    antes = len(TOKEN.findall(con))
    d = json.load(open(p, encoding="utf-8"))

    def toca(o):
        if isinstance(o, dict):
            for k in list(o.keys()):
                if k in ("originUrl", "downloadUrl", "url", "signedUrl", "originalFileUri"):
                    if isinstance(o[k], str) and o[k]:
                        o[k] = REDACTADO
                    elif isinstance(o.get(k), dict) and "url" in o[k]:
                        o[k]["url"] = REDACTADO
                else:
                    toca(o[k])
        elif isinstance(o, list):
            for e in o:
                toca(e)

    toca(d)
    nuevo = json.dumps(d, ensure_ascii=False, indent=2)
    despues = len(TOKEN.findall(nuevo))
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(nuevo + "\n")
    total_antes += antes
    total_despues += despues
    R.append("%s : ocurrencias de tokens de firma ANTES=%d DESPUES=%d" % (nombre, antes, despues))

R.append("")
R.append("TOTAL ocurrencias antes=%d despues=%d en %d archivos" % (total_antes, total_despues, len(OBJETOS)))

# Barrido de supervivientes en TODO el expediente, no solo los tres objetos
raiz = D
sup = []
for dp, _, fns in os.walk(raiz):
    for fn in fns:
        fp = os.path.join(dp, fn)
        try:
            c = open(fp, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        n = len(TOKEN.findall(c))
        if n:
            sup.append("%s : %d" % (os.path.relpath(fp, raiz), n))
# El propio instrumento define el patron en su regex: se excluye del barrido y se declara.
sup = [s for s in sup if not os.path.basename(s.split(" : ")[0]).startswith("m-")
       and os.path.basename(s.split(" : ")[0]) != "11-redaccion-url-firmadas.txt"]
R.append("")
R.append("== Barrido de supervivientes en el expediente completo ==")
R.append("comando logico: recorrer el directorio y contar x-oss-credential|x-oss-signature|x-oss-date|x-oss-expires")
R.append("exclusion declarada: quedan fuera los instrumentos m-* que DEFINEN el patron y este propio")
R.append("informe, que nombra los tokens al describir el comando (autocontagio del contador)")
R.append("control aparte, solo en los tres objetos JSON: ocurrencias de la raiz del objeto firmado "
         "(%s) = %d" % ("qoder-mind.oss",
                        sum(len(re.findall(r"qoder-mind\.oss", open(os.path.join(D, n2), encoding="utf-8").read()))
                            for n2 in OBJETOS if os.path.exists(os.path.join(D, n2)))))
if sup:
    for s in sup:
        R.append("    %s" % s)
else:
    R.append("    0 supervivientes")

with open(os.path.join(D, "11-redaccion-url-firmadas.txt"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(R) + "\n")
print("ESCRITO 11-redaccion-url-firmadas.txt")
print("ANTES=%d DESPUES=%d SUPERVIVIENTES=%d" % (total_antes, total_despues, len(sup)))
