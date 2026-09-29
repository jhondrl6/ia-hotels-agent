"""C5 criterio 2: identidad POST == `git cat-file blob HEAD:<ruta>` sobre las 213 rutas.

La fila y la orden citan una muestra de tres archivos; aqui se verifica la poblacion entera, porque el
escritor ya exigio la identidad ANTES de escribir y el refresco de stat del indice no cambia contenido.
Se reportan tambien las tres rutas de la muestra citada, para que el crudo hable el mismo idioma que
el criterio.
"""
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
S = pathlib.Path(__file__)
INFORME = S.parent / "26b-c5-informe-fix.json"
MUESTRA = [".opencode/context/Historico/Pendiente.md",
           ".opencode/plans/Archives/VALIDADOR-URL-PROPIA-2026-08-30/README.md",
           ".opencode/refs_baseline.txt"]


def blob(rev: str, ruta: str):
    proc = subprocess.run(["git", "cat-file", "blob", f"{rev}:{ruta}"], capture_output=True,
                          cwd=str(ROOT))
    return proc.stdout if proc.returncode == 0 else None


def main():
    rutas = [n["ruta"] for n in json.loads(INFORME.read_text(encoding="utf-8"))["normalizados"]]
    iguales, distintos, sin_blob = [], [], []
    for r in rutas:
        disco = (ROOT / r).read_bytes()
        b = blob("HEAD", r)
        if b is None:
            sin_blob.append(r)
        elif disco == b:
            iguales.append(r)
        else:
            distintos.append(r)

    salida = [f"rutas_normalizadas={len(rutas)}",
              f"POST_igual_al_blob_HEAD={len(iguales)}",
              f"POST_distinto_al_blob={len(distintos)}",
              f"sin_blob_en_HEAD={len(sin_blob)}",
              f"criterio_2_cumplido_en_toda_la_poblacion={not distintos and not sin_blob}",
              "", "=== muestra de tres citada por la orden, medida aparte ==="]
    for r in MUESTRA:
        disco = (ROOT / r).read_bytes() if (ROOT / r).is_file() else b""
        b = blob("HEAD", r)
        salida.append(f"  {r}: disco_igual_a_blob={disco == b}  "
                      f"CR_disco={disco.count(bytes([13]))}  tamano_disco={len(disco)}  "
                      f"tamano_blob={len(b) if b is not None else None}")
    if distintos:
        salida += ["", "DISTINTOS:"] + [f"  {r}" for r in distintos[:20]]
    destino = S.parent / "28-c5-identidad-post.txt"
    destino.write_text("\n".join(salida) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(salida))
    print("# crudo en", destino.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
