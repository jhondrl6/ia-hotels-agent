"""C5 — escritor de normalizacion CRLF→LF de la poblacion residuo de `.opencode` (deuda D-C).

Reglas que coderan este archivo (no son adornos, son los criterios de la orden):

* **Poblacion calculada, nunca lista a mano.** La unica fuente de la poblacion es el comando canonico
  de la casa (`git ls-files --eol .opencode` con `i/lf` y `w/crlf`), leida con `-z` y
  `core.quotePath=false` para que las dos rutas con escapes octales no se pierdan.
* **Identidad contra el blob antes de escribir.** Un archivo solo se normaliza si su contenido, ya sin
  CRLF, es byte a byte el blob de `HEAD:<ruta>`. Si no lo es, se RECHAZA: la normalizacion no puede
  llevarse por delante contenido ajeno (criterio 2 de C5).
* **Fuera de la poblacion se niega.** Toda ruta pedida por `--rutas-extra` que no este en la poblacion
  se rechaza con codigo propio (criterio 5, el mutante).
* **Sin traduccion del SO.** Se escribe por bytes: `write_bytes` no traduce finales de linea, y con
  `write_text` este mismo escritor reproduciria el defecto que cura.
* **`--dry-run` no escribe nada** y lo afirma por huella, no por intencion.

Uso:
    python m-c5-normalizador-residuo.py --dry-run
    python m-c5-normalizador-residuo.py --fix --informe <ruta.json>
    python m-c5-normalizador-residuo.py --rutas-extra <archivo-fuera-de-poblacion>   # mutante
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
POBLACION_PATHSPEC = ".opencode"
COMANDO_CANONICO = ("git ls-files --eol .opencode | awk '$1==\"i/lf\" && $2==\"w/crlf\"' | wc -l")
EXIT_ACEPTADO = 0
EXIT_RECHAZO = 4
EXIT_IDENTIDAD = 5


def sh(args, shell=False):
    """Con `shell=True` la linea va como cadena: pasarla como lista le da a cmd.exe un argumento
    `['...']` que no puede resolver y devuelve 1 con «nombre de archivo no válido» (medido aqui)."""
    proc = subprocess.run(args, capture_output=True, cwd=str(ROOT), shell=shell, text=True,
                          encoding="utf-8")
    if proc.returncode != 0:
        raise SystemExit(f"[ERROR] {args if isinstance(args, str) else ' '.join(args)} -> "
                         f"{proc.returncode}: {proc.stderr.strip()[:300]}")
    return proc.stdout


def blob_de_head(ruta: str) -> bytes:
    proc = subprocess.run(["git", "cat-file", "blob", f"HEAD:{ruta}"], capture_output=True,
                          cwd=str(ROOT))
    if proc.returncode != 0:
        raise ValueError(f"no hay blob de HEAD para {ruta}")
    return proc.stdout


def poblacion_residuo() -> list[str]:
    """La poblacion: registros `i/lf  w/crlf` bajo `.opencode`, con la ruta cruda (sin comillas)."""
    salida = sh(["git", "-c", "core.quotePath=false", "ls-files", "--eol", "-z",
                 POBLACION_PATHSPEC])
    rutas = []
    for registro in salida.split("\0"):
        if not registro.strip():
            continue
        cabecera, _, ruta = registro.partition("\t")
        campos = cabecera.split()
        if len(campos) >= 2 and campos[0] == "i/lf" and campos[1] == "w/crlf" and ruta.strip():
            rutas.append(ruta.strip())
    return sorted(set(rutas))


def conteo_canonico() -> int:
    """El mismo predicado del comando de la casa (`$1==\"i/lf\" && $2==\"w/crlf\"`), sin awk.

    `shell=True` cae en cmd.exe bajo Git Bash y `awk` no existe ahi (medido: 255 con
    «"$2" no se reconoce como comando»). El conteo se hace en Python sobre la salida de
    `git ls-files --eol` con el quoting por defecto, que es lo que la linea del crudo imprime; la
    seleccion de rutas se lee aparte con `-z` y `core.quotePath=false`, y el escritor exige que las
    dos lecturas den el mismo numero antes de tocar nada.
    """
    salida = sh(["git", "ls-files", "--eol", POBLACION_PATHSPEC])
    n = 0
    for registro in salida.splitlines():
        if not registro.strip():
            continue
        cabecera = registro.split("\t", 1)[0]
        campos = cabecera.split()
        if len(campos) >= 2 and campos[0] == "i/lf" and campos[1] == "w/crlf":
            n += 1
    return n


def sin_crlf(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n")


def normalizar(rutas: list[str], dry_run: bool) -> dict:
    informe = {"poblacion_calculada": len(rutas), "normalizados": [], "rechazados_identidad": [],
               "ya_lf": [], "dry_run": dry_run}
    for r in rutas:
        disco = (ROOT / r).read_bytes()
        if b"\r" not in disco:
            informe["ya_lf"].append(r)
            continue
        nuevo = sin_crlf(disco)
        try:
            blob = blob_de_head(r)
        except ValueError as e:
            informe["rechazados_identidad"].append({"ruta": r, "motivo": str(e)})
            continue
        if nuevo != blob:
            d = _primera_diferencia(nuevo, blob)
            informe["rechazados_identidad"].append({
                "ruta": r, "motivo": "el contenido normalizado no es el blob de HEAD",
                "linea": d[0], "esperado": d[1], "obtenido": d[2],
                "sha_antes": hashlib.sha256(disco).hexdigest()[:16],
                "sha_normalizado": hashlib.sha256(nuevo).hexdigest()[:16],
                "sha_blob": hashlib.sha256(blob).hexdigest()[:16]})
            continue
        if not dry_run:
            (ROOT / r).write_bytes(nuevo)
        informe["normalizados"].append({
            "ruta": r, "bytes_antes": len(disco), "bytes_despues": len(nuevo),
            "cr_antes": disco.count(b"\r"), "cr_despues": nuevo.count(b"\r"),
            "sha_blob": hashlib.sha256(blob).hexdigest()[:16]})
    return informe


def _primera_diferencia(antes: bytes, despues: bytes) -> tuple[int, str, str]:
    a = sin_crlf(antes).splitlines()
    b = despues.splitlines()
    for i in range(max(len(a), len(b))):
        x = a[i].decode("utf-8", "replace") if i < len(a) else "(ausente)"
        y = b[i].decode("utf-8", "replace") if i < len(b) else "(ausente)"
        if x != y:
            return i + 1, x[:160], y[:160]
    return 0, "(misma linea a linea, distinto ensamblado)", ""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fix", action="store_true", help="escribir (por defecto no se escribe)")
    ap.add_argument("--dry-run", action="store_true", help="no escribe nada; informa")
    ap.add_argument("--rutas-extra", action="append", default=[], metavar="RUTA",
                    help="ruta pedida fuera de la poblacion: se rechaza (control negativo)")
    ap.add_argument("--informe", default=None)
    args = ap.parse_args(argv)

    poblacion = poblacion_residuo()
    canonico = conteo_canonico()
    if len(poblacion) != canonico:
        print(f"[ERROR] la lectura con -z ({len(poblacion)}) no casa con el comando canonico "
              f"({canonico}): poblacion dudosa, no se escribe nada")
        return EXIT_RECHAZO

    fuera = [r for r in args.rutas_extra if r not in poblacion]
    if fuera:
        print(f"[RECHAZADO-FUERA-DE-POBLACION] {len(fuera)} ruta(s) no estan en la poblacion "
              "residuo; el escritor no normaliza archivo fuera de ella:")
        for r in fuera:
            print(f"    - {r}")
        return EXIT_RECHAZO

    pedidas = sorted(set(poblacion))
    informe = normalizar(pedidas, dry_run=not args.fix)
    informe["comando_canonico"] = COMANDO_CANONICO
    informe["conteo_canonico_antes"] = canonico

    resumen = (f"[{'DRY-RUN' if not args.fix else 'ESCRITO'}] poblacion={canonico} · "
               f"normalizados={len(informe['normalizados'])} · "
               f"rechazados_identidad={len(informe['rechazados_identidad'])} · "
               f"ya_lf={len(informe['ya_lf'])} · rechazados_fuera_de_poblacion={len(fuera)}")
    print(resumen)
    for i in informe["rechazados_identidad"][:5]:
        print(f"    - IDENTIDAD {i['ruta']}: {i['motivo']} (linea {i.get('linea')})")
    if args.informe:
        pathlib.Path(args.informe).write_text(
            json.dumps(informe, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8", newline="\n")
        print(f"[informe] {args.informe}")
    if informe["rechazados_identidad"]:
        return EXIT_IDENTIDAD
    return EXIT_ACEPTADO


if __name__ == "__main__":
    sys.exit(main())
