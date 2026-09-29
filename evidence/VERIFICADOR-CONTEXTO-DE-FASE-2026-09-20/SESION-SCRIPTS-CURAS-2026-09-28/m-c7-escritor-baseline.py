"""C7 crudo: el escritor del baseline sobre ruta EXTERNA, vigente contra la revision de arranque.

La orden prohibe probar el escritor contra el baseline real, asi que se corre con `--baseline` fuera
del repositorio y `--plans-dir` sobre el arbol de planes vigente (el escritor solo lee de ahi). El
control es el escritor de `REV_INICIO` (84c1aca), materializado con `git show` y ejecutado sobre la
misma copia: sin ancla fija el control caduca en cuanto la cura entra en el commit.

Se reproducen las tres magnitudes con las que la sesion 1 tas6 D-H (CR, LF, CRLF), la identidad salvo
CR y la identidad salvo CR y marca de tiempo.
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = pathlib.Path(__file__).resolve().parents[3]
S = pathlib.Path(__file__)
REV_INICIO = "84c1aca"
ESCRITOR_REL = "scripts/validate_plan_citations.py"
PLANS = ROOT / ".opencode" / "plans"


def correr(script: Path, destino: Path) -> dict:
    proc = subprocess.run([sys.executable, str(script), "--plans-dir", str(PLANS),
                           "--baseline", str(destino), "--update-baseline"],
                          capture_output=True, text=True)
    assert proc.returncode == 0, f"{proc.returncode}: {proc.stdout}{proc.stderr}"
    b = destino.read_bytes()
    datos = json.loads(b.decode("utf-8"))
    return {"stdout": proc.stdout.strip(), "bytes": len(b),
            "CR": b.count(b"\r"), "LF": b.count(b"\n"), "CRLF": b.count(b"\r\n"),
            "sha16": hashlib.sha256(b).hexdigest()[:16],
            "sin_marca": {k: v for k, v in datos.items() if k != "created_at"},
            "bruto": b}


def main():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="c7_baseline_"))
    viejo_ruta = tmp / "escritor_viejo.py"
    proc = subprocess.run(["git", "show", f"{REV_INICIO}:{ESCRITOR_REL}"],
                          capture_output=True, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stderr[:200]
    viejo_ruta.write_bytes(proc.stdout)
    assert b"newline=" not in proc.stdout, (
        f"la revision {REV_INICIO} ya trae la cura: el control no tendria rojo que mostrar")

    nuevo = correr(ROOT / ESCRITOR_REL, tmp / "nuevo" / "baseline.json")
    viejo = correr(viejo_ruta, tmp / "viejo" / "baseline.json")

    identidad_cr = nuevo["bruto"].replace(b"\n", b"\r\n") == viejo["bruto"]
    # La marca de tiempo se normaliza POR BYTES, no con el dict parseado: la identidad byte a byte es
    # la que prueba que el unico cambio entre los dos escritores es el parametro.
    sin_marca = lambda b: re.sub(rb'"created_at": "[^"]*"', b'"created_at": "N"', b)
    marca = lambda b: re.search(rb'"created_at": "([^"]*)"', b).group(1)
    crudo_igual = nuevo["bruto"] == viejo["bruto"]
    identidad_cr = sin_marca(nuevo["bruto"]).replace(b"\n", b"\r\n") == sin_marca(viejo["bruto"])
    identidad_dict = nuevo["sin_marca"] == viejo["sin_marca"]
    lineas = [
        "=== C7.1 escritor VIGENTE (con la cura) sobre ruta externa ===",
        nuevo["stdout"],
        f"bytes={nuevo['bytes']}  CR={nuevo['CR']}  LF={nuevo['LF']}  CRLF={nuevo['CRLF']}  "
        f"sha={nuevo['sha16']}",
        "comando de la casa para el conteo de CR: tr -cd '\\r' | wc -c",
        "",
        f"=== C7.2 control ANCLADO a {REV_INICIO}: escritor viejo sobre la MISMA copia ===",
        viejo["stdout"],
        f"bytes={viejo['bytes']}  CR={viejo['CR']}  LF={viejo['LF']}  CRLF={viejo['CRLF']}  "
        f"sha={viejo['sha16']}",
        "",
        "=== C7.3 identidades ===",
        f"created_at_vigente={marca(nuevo['bruto']).decode()}  "
        f"created_at_control={marca(viejo['bruto']).decode()}",
        f"identico_salvo_CR_y_marca_por_bytes: {identidad_cr}",
        f"identico_bruto_crudo: {crudo_igual}   (False esperado: uno emite LF puro y el otro CRLF "
        "puro, y sus marcas de tiempo pueden no coincidir)",
        f"identico_por_dict_sin_created_at: {identidad_dict}",
        f"crlf_puro_en_el_control: "
        f"{viejo['CR'] == viejo['LF'] == viejo['CRLF'] and viejo['CR'] > 0}",
        f"lf_puro_en_la_cura: {nuevo['CR'] == 0 and nuevo['LF'] > 0}",
        "",
        "Lectura: la unica diferencia entre los dos escritores es el parametro `newline`; la marca",
        "`created_at` si cambia entre corridas (segundos de diferencia), por eso la identidad se",
        "afirma normalizandola por bytes. Con `lf_puro_en_la_cura` y `crlf_puro_en_el_control` en",
        "True, el rojo del control y el verde de la cura son atribuibles al cambio de C7 y no a la",
        "maquina.",
    ]
    destino = S.parent / "23-c7-escritor-baseline.txt"
    destino.write_text("\n".join(lineas) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lineas))
    print("# crudo en", destino.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
