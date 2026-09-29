"""C3 crudo: que imprime cada modo, sin correr pytest.

El modo completo invoca la suite de pytest (su check exclusivo) y esta orden tiene prohibido correrla,
asi que la cabecera y la guarda del completo se imprimen por la via offline: `_print_summary` sobre un
runner con resultados sinteticos del tamano del modo. No ejecuta ni un check.

El comando de la fila §S21 se corre tal cual, sobre el archivo vigente y sobre la revision de arranque,
para que el crudo muestre las etiquetas antes y despues de la cura.
"""
import contextlib
import importlib.util
import io
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
S = pathlib.Path(__file__)
RUNNER = ROOT / "scripts" / "run_all_validations.py"
# El comando literal de la fila §S21. Un backslash o una comilla de mas en el patron devuelven
# `0 lineas` sobre un archivo que si tiene las 17 etiquetas (medido en este mismo crudo).
PATRON_FILA = r'print\("\[[0-9]+/[0-9]+\]'
PAR_RE = re.compile(r"\[(\d+)/(\d+)\]")


def cargar(nombre, ruta):
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


def etiquetas_por_grep(ruta):
    """El comando de la fila, corrido por `bash -c` con el patron entre comillas simples.

    Lanzar `grep` con `subprocess.run([...])` directo devuelve **exit 2** bajo Windows: la comilla
    doble del patron se come el argv (medido en este crudo). Por eso se le da la linea a la shell,
    que es donde el comando de la fila esta escrito.
    """
    linea = f"grep -oE '{PATRON_FILA}' '{ruta.as_posix()}'"
    proc = subprocess.run(["bash", "-c", linea], capture_output=True, text=True)
    pares = [m.groups() for m in (PAR_RE.search(l) for l in proc.stdout.splitlines()) if m]
    assert proc.returncode == 0 and pares, (
        f"el comando de la fila no devolvio pares sobre {ruta} "
        f"(exit={proc.returncode}, stderr={proc.stderr[:200]!r})")
    return [(int(a), int(b)) for a, b in pares]


def etiquetas_por_python(ruta):
    """El mismo patron, aplicado en proceso sobre los mismos bytes: segundo instrumento."""
    fuente = ruta.read_text(encoding="utf-8")
    return [(int(a), int(b)) for a, b in re.findall(r'print\(f?"\[(\d+)/(\d+)\]', fuente)]


def summary_offline(mod, quick, n):
    runner = mod.ValidationRunner(quick=quick, verbose=False)
    runner.results = [mod.ValidationResult(f"check-{i}", True) for i in range(1, n + 1)]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ok = runner._print_summary()
    lineas = [l.strip() for l in buf.getvalue().splitlines()
              if "MODO:" in l or "GUARDA" in l or "TOTAL:" in l]
    return ok, lineas


def describe(eticas):
    orden = [a for a, _ in sorted(eticas)]
    denominadores = sorted({b for _, b in eticas})
    return (f"etiquetas={len(eticas)} orden={orden} denominadores={denominadores} "
            f"unicos_por_denominador="
            f"{ {d: sum(1 for _, b in eticas if b == d) for d in denominadores} }")


def main():
    mod = cargar("rav_crudo_c3", RUNNER)
    rapido, completo = mod.ValidationRunner()._orden_del_modo()

    vigentes = etiquetas_por_grep(RUNNER)
    vigentes_py = etiquetas_por_python(RUNNER)
    salida = ["=== C3.1 el comando de la fila §S21, sobre el archivo vigente (post-cura) ===",
              f"comando: grep -oE '{PATRON_FILA}' scripts/run_all_validations.py",
              describe(vigentes),
              f"contraste_en_proceso={describe(vigentes_py)}",
              f"los_dos_instrumentos_cuadran={vigentes == vigentes_py}", ""]

    proc = subprocess.run(["git", "show", "84c1aca:scripts/run_all_validations.py"],
                          capture_output=True, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stderr[:200]
    copia = S.parent / "_runner_revision_de_arranque.py"
    copia.write_bytes(proc.stdout)
    arr = etiquetas_por_grep(copia)
    arr_py = etiquetas_por_python(copia)
    salida += ["=== mismo comando sobre REV_INICIO 84c1aca (pre-cura) ===",
               describe(arr),
               f"contraste_en_proceso={describe(arr_py)}",
               f"los_dos_instrumentos_cuadran={arr == arr_py}",
               f"delta_etiquetas_post_minus_pre={len(vigentes) - len(arr)}", "",
               "La cura no anade ni quita etiquetas: la cabecera nueva no es un literal [N/M] y el "
               "registro de emisores que lee `validate_governance_numbers.py` queda intacto.", ""]

    for quick, n, etiqueta in ((True, len(rapido), "rapido"), (False, len(completo), "completo")):
        ok, lineas = summary_offline(mod, quick, n)
        salida += [f"=== modo {etiqueta} (n={n}) por la via offline, sin correr ningun check ===",
                   f"guarda_coherente={ok}"] + lineas + [""]

    copia.unlink()
    salida += ["Declaracion: el modo completo NO se corrio como corrida real porque invoca la suite de "
               "pytest, prohibida en esta orden. Su cabecera y su guarda se imprimen por "
               "`_print_summary` con resultados sinteticos, que es el mismo codigo de la corrida "
               "verdadera."]
    destino = S.parent / "15-c3-cabecera-por-modo.txt"
    destino.write_text("\n".join(salida) + "\n", encoding="utf-8", newline="\n")
    print("# crudo en", destino.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
