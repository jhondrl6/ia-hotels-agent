"""C4 crudo: espejo con ruta minoritaria, antes/despues del --fix vigente y del commiteado.

No toca el arbol del proyecto: los dos escritores corren sobre espejos temporales (el PROJECT_ROOT
sale del __file__ de la copia). Escribe su salida con newline="\n" y UTF-8, por la regla de la casa.
"""
import importlib.util
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
S = pathlib.Path(__file__)
VIGENTE = ROOT / "scripts" / "validate_opencode_refs.py"


def _cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    anterior = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = anterior
    return mod


def commiteado(rev, tmp):
    proc = subprocess.run(["git", "show", f"{rev}:scripts/validate_opencode_refs.py"],
                          capture_output=True, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stderr[:400]
    destino = tmp / f"commiteado_{rev}.py"
    destino.write_bytes(proc.stdout)
    return destino


def espejo(raiz, script_src):
    (raiz / "scripts").mkdir(parents=True, exist_ok=True)
    destino = raiz / ".opencode" / "plans" / "Archives" / "HUESO"
    destino.mkdir(parents=True)
    shutil.copyfile(script_src, raiz / "scripts" / "validate_opencode_refs.py")
    (destino / "nota.md").write_bytes(b"# destino del espejo\n")
    nota = "# Nota del espejo\n\nLeer `.opencode/plans/HUESO/nota.md` antes de cerrar.\n"
    archivo = raiz / ".opencode" / "plans" / "registro.md"
    archivo.write_bytes(nota.encode("utf-8"))
    return archivo


def ruta_citada(texto):
    return [l for l in texto.splitlines() if ".opencode" in l]


# Patron de la forma minoritaria: backtick + barra + .opencode/plans/Archives. Se compone fuera del
# f-string y SIN doble escape: con r'`/\\.opencode' el regex pide un backslash literal y da 0 falso
# sobre el control (medido en esta misma corrida).
BARRA = "`" + "/.opencode/plans/Archives"


def correr(etiqueta, src, tmp, nombre):
    raiz = tmp / nombre
    archivo = espejo(raiz, src)
    antes = archivo.read_text(encoding="utf-8")
    mod = _cargar(f"refs_crudo_{nombre}", raiz / "scripts" / "validate_opencode_refs.py")
    primera = mod.main(["--fix"])
    despues = archivo.read_text(encoding="utf-8")
    bytes_tras_primera = archivo.read_bytes()
    segunda = mod.main(["--fix"])
    bytes_tras_segunda = archivo.read_bytes()
    salida = [f"=== {etiqueta} ===",
              f"exit_primera_corrida={primera}  exit_segunda_corrida={segunda}",
              f"ANTES  : {ruta_citada(antes)}",
              f"DESPUES: {ruta_citada(despues)}",
              f"forma_minoritaria_con_barra={BARRA in despues}",
              f"idempotente_en_bytes={bytes_tras_primera == bytes_tras_segunda} "
              f"(bytes_tras_primera={len(bytes_tras_primera)} "
              f"bytes_tras_segunda={len(bytes_tras_segunda)})",
              ""]
    return salida


def main():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="refs_forma_crudo_"))
    lineas = []
    lineas += correr("VIGENTE (cura C4)", VIGENTE, tmp, "vigente")
    lineas += correr("CONTROL 5817edd (antes de la cura)",
                     commiteado("5817edd", tmp), tmp, "control")
    destino = S.parent / "09-c4-espejo-forma.txt"
    destino.write_text("\n".join(lineas) + "\n", encoding="utf-8", newline="\n")
    print("# crudo en", destino.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
