"""Copia saneada del 10-analisis para el write-back de cierre.

Metodo heredado de FASE-G: sustitucion a nivel de bytes con conteo declarado por token y
PRUEBA DE FIDELIDAD invirtiendo las sustituciones sobre la copia y cotejando el sha256 contra el
original. No es el documento canonico: es la instantanea que se sube.
"""
import hashlib
import io
import os
import sys

SRC = ".opencode/plans/Archives/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/10-analisis-post-implementacion.md"
DST_DIR = "evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-RELEASE"
DST = os.path.join(DST_DIR, "qmind-upload-10-analisis-cierre-4.79.0-saneado.md")
SENTINELA = "<!-- COPIA-SANEADA-QMIND-INI -->\n"
FIN = "<!-- COPIA-SANEADA-QMIND-FIN -->\n"

# (token_original, token_saneado) en orden: de mas largo a mas corto para que la biyeccion valga.
PARES = [
    ("Hotel Don Alfonso", "[HOTEL-CLIENTE-OMITIDO]"),
    ("Don Alfonso", "[CLIENTE]"),
    ("https://www.donalfonsohotel.com/", "[URL-DEL-CLIENTE-OMITIDA]"),
    ("donalfonsohotel.com", "[DOMINIO-DEL-CLIENTE-OMITIDO]"),
    ("consentimiento-donalfonso.md", "consentimiento-[CLIENTE].md"),
    ("don_alfonso_20261007", "[ARCHIVO-DEL-CLIENTE-OMITIDO]"),
    ("donalfonso", "[CLIENTE-RUTA]"),
    ("6063146139", "[TELEFONO-DEL-CLIENTE-OMITIDO]"),
    ("Alfonso", "[CLIENTE-RESTO]"),
]

CABECERA = SENTINELA + (
    "> **Esta NO es el documento canónico.** Es la **copia saneada** del `10-analisis` del plan\n"
    "> `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` producida por su FASE-RELEASE el 2026-10-07 para el write-back a\n"
    "> QMind con `scripts/validate_qmind_writeback.py --upload --file --title`. El documento canónico es\n"
    "> `.opencode/plans/Archives/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/10-analisis-post-implementacion.md` (la ruta\n"
    "> estaba en raíz de planes al momento de la primera ingesta de cierre; el `git mv` de archivado la movió). Se sustituyeron\n"
    "> identidades del cliente (nombre comercial, URL, dominio, teléfono y rutas que las nombran) con conteo\n"
    "> declarado por token; la fidelidad se probó invirtiendo las sustituciones sobre esta copia y cotejando el\n"
    "> sha256 contra el original. Prueba y conteos: `qmind-writeback-RELEASE.md` en esta carpeta.\n"
    + FIN
)


def main():
    crudo = io.open(SRC, "rb").read()
    sha_original = hashlib.sha256(crudo).hexdigest()
    texto = crudo.decode("utf-8")

    conteos = []
    for viejo, nuevo in PARES:
        n = texto.count(viejo)
        conteos.append((viejo, nuevo, n))
        if n:
            texto = texto.replace(viejo, nuevo)
        assert nuevo not in io.open(SRC, "rb").read().decode("utf-8"), "colision de token: " + nuevo

    for viejo, nuevo, n in conteos:
        print("%-38s -> %-28s : %d" % (viejo, nuevo, n))

    cuerpo_saneado = texto
    for token in ("Don Alfonso", "donalfonso", "Alfonso", "6063146139", "donalfonsohotel"):
        assert token not in cuerpo_saneado, "residuo de identidad: " + token

    copia = CABECERA + cuerpo_saneado
    if not os.path.isdir(DST_DIR):
        os.makedirs(DST_DIR)
        print("[OK] carpeta creada: " + DST_DIR)
    with io.open(DST, "wb") as f:
        f.write(copia.encode("utf-8"))

    # Prueba de fidelidad: retirar la cabecera, invertir las sustituciones en orden inverso y cotejar sha.
    leido = io.open(DST, "rb").read().decode("utf-8")
    fin = leido.index(FIN) + len(FIN)
    revertido = leido[fin:]
    # Se invierte empezando por el token mas largo: "[CLIENTE]" es subcadena de
    # "[HOTEL-CLIENTE-OMITIDO]" y, en otro orden, la inversion corromperia el token compuesto.
    for viejo, nuevo, n in sorted([c for c in conteos if c[2]], key=lambda c: -len(c[1])):
        revertido = revertido.replace(nuevo, viejo)
    sha_revertido = hashlib.sha256(revertido.encode("utf-8")).hexdigest()
    coincide = sha_revertido == sha_original
    print("\noriginal : %s  %d B" % (sha_original, len(crudo)))
    print("revertido: %s  %d B" % (sha_revertido, len(revertido.encode("utf-8"))))
    print("[FIDELIDAD] %s" % ("OK - la copia invierte al original byte a byte" if coincide else "FALLO"))
    if not coincide:
        sys.exit(1)


if __name__ == "__main__":
    main()
