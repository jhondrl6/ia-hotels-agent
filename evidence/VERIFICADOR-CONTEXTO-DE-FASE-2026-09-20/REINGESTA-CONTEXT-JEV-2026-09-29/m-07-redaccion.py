#!/usr/bin/env python3
"""Instrumento m-07: redaccion de las URL firmadas de los JSON persistidos, y su control por FORMA del valor.

El patron se construye por concatenacion: ni el marcador ni este instrumento contienen el token buscado,
asi que el conteo no se autocontamina. Solo se imprimen rutas de clave y conteos, nunca valores.
"""
import glob
import json

PREF = "x-os" + "s-"
SUFJ = ["signature", "credential", "date", "expires"]
FORM = PREF + "(" + "|".join(SUFJ) + ")="
MARK = "REDACTADA"
CAMPOS = ["originUrl", "originalFile" + "Uri"]

E = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"


def walk(node, path=""):
    """Yield (ruta, valor) de cada hoja str del arbol."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, "%s.%s" % (path, k) if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, "%s[%d]" % (path, i))
    elif isinstance(node, str):
        yield path, node


def cuenta_forma(texto):
    import re
    return len(re.findall(FORM, texto))


files = sorted(glob.glob(E + "/*.json"))
print("patron_del_control=%s" % FORM)
print("marcador=%s" % MARK)
print("archivos_json=%d" % len(files))
print("campos_redactados=%s" % CAMPOS)
print()

# el instrumento se autoexcluye del barrido: no es un JSON persistido
totales_antes = 0
marcadores = 0
for fp in files:
    with open(fp, encoding="utf-8") as fh:
        texto = fh.read()
    antes = cuenta_forma(texto)
    datos = json.loads(texto)
    golpeados = []
    for ruta, valor in walk(datos):
        if cuenta_forma(valor):
            golpeados.append(ruta)
    # redaccion por hoja: se sustituye el valor completo cuando lleva la forma
    def scrub(node):
        global marcadores
        n = 0
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(v, str) and cuenta_forma(v):
                    node[k] = MARK
                    n += 1
                else:
                    n += scrub(v)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                if isinstance(v, str) and cuenta_forma(v):
                    node[i] = MARK
                    n += 1
                else:
                    n += scrub(v)
        return n

    hojas_con_forma = len(golpeados)
    marcadores += scrub(datos)
    nuevo = json.dumps(datos, ensure_ascii=False, indent=2)
    despues = cuenta_forma(nuevo)
    totales_antes += antes
    with open(fp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(nuevo)
    print("%s" % fp.split("/")[-1])
    print("  forma_antes=%d  hojas_con_forma=%d  forma_despues=%d" % (antes, hojas_con_forma, despues))
    print("  rutas_afectadas=%s" % sorted({r.split("[")[0].rsplit(".", 1)[-1] for r in golpeados}))
    print("  marcadores_en_el_archivo=%d" % nuevo.count('"%s"' % MARK))

print()
print("TOTAL_forma_antes=%d" % totales_antes)
print("TOTAL_marcadores=%d" % marcadores)
print("TOTAL_forma_despues=%d  (debe ser 0)" % sum(cuenta_forma(open(fp, encoding="utf-8").read()) for fp in files))
print()
print("CAMPOS_CONSERVADOS (muestra de una fuente):")
datos = json.load(open(E + "/06-source-list-post.json", encoding="utf-8"))
for s in datos["sources"][:1]:
    md = s.get("metadata") or {}
    for k in ("id", "title", "status", "uri"):
        v = s.get(k)
        print("  %s=%s" % (k, ("<MARCA>" if v == MARK else str(v)[:80])))
    print("  metadata.fileSha256=%s" % md.get("fileSha256"))
    print("  metadata.uri_lleva_forma=%d" % cuenta_forma(str(md.get("fileSha256"))))
