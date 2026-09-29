import re, sys, io, os

ROOT = ".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
NEGS = ["no lo esta", "sigue sin autorizar", "sin autorizacion", "no se ejecuto",
        "no esta autorizada", "no estan autorizados", "pendientes de su autorizacion",
        "no esta autorizado", "sigue pendiente de su autorizacion"]

def norm(s):
    for a, b in [("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u"),("ñ","n"),
                 ("«",'"'),("»",'"'),("’","'")]:
        s = s.replace(a, b)
    return s.lower()

def paragraphs(text):
    """(linea_inicial, linea_final, bloque) separados por una linea en blanco."""
    parts = re.split(r"\n[ \t]*\n", text)
    out, off = [], 0
    for p in parts:
        start_line = text.count("\n", 0, off) + 1
        end_line = text.count("\n", 0, off + len(p)) + 1
        if p.strip():
            out.append((start_line, end_line, p))
        off += len(p) + 2
    return out

def main():
    scope = sys.argv[1]
    dest = sys.argv[2]
    if scope == "fuentes":
        files = sorted(os.path.join(ROOT, f).replace("\\", "/")
                       for f in os.listdir(ROOT) if f.endswith(".md"))
    elif scope == "corpus-completo":
        files = []
        for dirpath, dirnames, filenames in os.walk(".opencode/plans"):
            for f in sorted(filenames):
                if f.endswith(".md"):
                    files.append(os.path.join(dirpath, f).replace("\\", "/"))
        files.sort()
    else:
        raise SystemExit("alcance desconocido")
    con_nota = sin_nota = fuerte = 0
    rows = []
    for path in files:
        with io.open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        for a, b, block in paragraphs(text):
            if "piloto FASE-C" not in block:
                continue
            low = norm(block)
            if not any(norm(g) in low for g in NEGS):
                continue
            has_note = "⟦" in block
            # criterio fuerte: la apertura de nota cae DESPUES de la ultima negacion del parrafo
            positions = [low.find(norm(g)) for g in NEGS if norm(g) in low]
            last_neg = max(positions)
            note_after = has_note and block.find("⟦") > last_neg
            if has_note:
                con_nota += 1
            else:
                sin_nota += 1
            if note_after:
                fuerte += 1
            first = " ".join(block.split())[:110]
            rows.append((path, a, b, "CON-NOTA" if has_note else "SIN-NOTA",
                         "NOTA-DETAS-DE-LA-FRASE" if note_after else "SIN-NOTA-DETAS", first))
    out = io.open(dest, "w", encoding="utf-8", newline="\n")
    out.write("== F3 barrido por parrafo. Alcance: %s (%d archivos .md)\n" % (scope, len(files)))
    out.write("== Lista de archivos del alcance:\n")
    for f in files:
        out.write("   %s\n" % f)
    out.write("== Predicado: un parrafo (separado por linea en blanco) contiene la cadena literal\n")
    out.write("   'piloto FASE-C' Y alguna de estas negaciones normalizadas (minusculas, sin acentos):\n")
    out.write("   %s\n" % ", ".join(NEGS))
    out.write("== Clasificacion A (criterio debil): el caracter '⟦' aparece en el MISMO parrafo => CON-NOTA\n")
    out.write("== Clasificacion B (criterio fuerte): ademas, el '⟦' cae DESPUES de la ultima negacion del\n")
    out.write("   parrafo, o sea que la nota sigue a la frase en lugar de referir a otra cosa del bloque\n")
    out.write("== Limites: las tablas markdown sin linea en blanco forman UN parrafo (una fila anotada\n")
    out.write("   anota el bloque entero bajo el criterio debil); y '⟦' es la marca de nota datada de la casa.\n\n")
    for r in rows:
        out.write("%s:%d-%d [%s] [%s] %s...\n" % (r[0], r[1], r[2], r[3], r[4], r[5]))
    out.write("\nTOTAL parrafos que afirman la clausula: %d\n" % len(rows))
    out.write("CON-NOTA (criterio debil): %d\n" % con_nota)
    out.write("SIN-NOTA (criterio debil): %d\n" % sin_nota)
    out.write("CON NOTA-DETAS-DE-LA-FRASE (criterio fuerte): %d\n" % fuerte)
    out.close()
    sys.stdout.write("ALCANCE=%s ARCHIVOS=%d TOTAL=%d CON-NOTA=%d SIN-NOTA=%d FUERTE=%d\n"
                     % (scope, len(files), len(rows), con_nota, sin_nota, fuerte))

main()
