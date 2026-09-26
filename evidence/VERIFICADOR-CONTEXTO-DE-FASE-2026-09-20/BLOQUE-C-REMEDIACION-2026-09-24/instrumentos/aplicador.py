"""Edicion a nivel de bytes respetando la terminacion de linea que YA tiene el archivo.

Los tres objetivos estan en LF puro (medido con `tr -dc`, no con `grep -c '\r'`: ese patron degenera
a vacio y cuenta lineas, no retornos de carro). Un `Edit` que injertara CRLF en un archivo LF mixteria
las terminaciones y reescribiria el archivo de cara a `git diff`; aqui se busca y se sustituye sobre
bytes, con la unica coincidencia exigida por asercion y el EOL heredado del propio archivo.

Uso: aplicador.py RUTA VIEJO.txt NUEVO.txt
"""
import hashlib
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def unirse(lineas, eol):
    return eol.join(lineas).encode("utf-8")


def leer_fragmento(p: Path, eol: str) -> bytes:
    txt = p.read_text(encoding="utf-8").replace("\r\n", "\n")
    if txt.endswith("\n"):
        txt = txt[:-1]
    return unirse(txt.split("\n"), eol)


def main():
    ruta = Path(sys.argv[1])
    data = ruta.read_bytes()
    cr, lf = data.count(b"\r"), data.count(b"\n")
    eol_str = "\r\n" if (cr == lf and cr > 0) else "\n"
    eol = eol_str.encode()
    viejo = leer_fragmento(Path(sys.argv[2]), eol_str)
    nuevo = leer_fragmento(Path(sys.argv[3]), eol_str)

    print(f"objetivo            : {ruta}")
    print(f"EOL heredado        : {'CRLF' if eol == bytes([13,10]) else 'LF'}  (CR={cr} LF={lf})")
    print(f"sha256 antes        : {hashlib.sha256(data).hexdigest()}")
    print(f"tamano antes (bytes): {len(data)}  lineas={lf}")
    print(f"coincidencias de viejo: {data.count(viejo)}")
    if data.count(viejo) != 1:
        raise SystemExit(f"ABORTADO: se exigia exactamente 1 coincidencia, hay {data.count(viejo)}")
    out = data.replace(viejo, nuevo, 1)
    ruta.write_bytes(out)
    print(f"sha256 despues      : {hashlib.sha256(out).hexdigest()}")
    print(f"tamano despues      : {len(out)}  (delta {len(out)-len(data)} bytes)")
    print(f"CR antes/despues    : {cr} / {out.count(bytes([13]))}")
    print(f"LF antes/despues    : {lf} / {out.count(bytes([10]))}")
    print(f"lineas anadidas     : {out.count(bytes([10])) - lf}")
    print(f"nuevo presente      : {out.count(nuevo)}   viejo restante: {out.count(viejo)}")


if __name__ == "__main__":
    main()
