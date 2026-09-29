"""C5 PRE: la poblacion residuo re-medida HOY, con el comando del crudo de la sesion 1.

Dos notas de instrumento, ambas medidas escribiendo este crudo:

* El comando canonico imprime las rutas no-ASCII entre comillas y con escapes octales (`git ls-files`
  respeta `core.quotePath` por defecto). Contar lineas funciona, pero resolver la ruta no: una de esas
  rutas devolvio `OSError [Errno 22]`. Para el escritor se re-leen con `-c core.quotePath=false` y `-z`,
  y el crudo afirma que las dos lecturas dan EL MISMO conteo.
* La identidad contra el blob (`POST == git cat-file blob HEAD:<ruta>`) solo puede exigirse en los
  archivos cuyo contenido no cambio: los doce declarados de la sesion 1 difieren de HEAD por
  contenido, y normalizarlos por EOL no los deja identicos al blob. Se reportan aparte.
"""
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
S = pathlib.Path(__file__)
AWK = '$1=="i/lf" && $2=="w/crlf"'
COMANDO_CANONICO = f"git ls-files --eol .opencode | awk '{AWK}' | wc -l"


def bash(linea: str) -> str:
    proc = subprocess.run(["bash", "-c", linea], capture_output=True, text=True,
                          encoding="utf-8", cwd=str(ROOT))
    assert proc.returncode == 0, f"{linea} -> {proc.returncode}: {proc.stderr[:300]}"
    return proc.stdout


def rutas_poblacion():
    """La poblacion con las rutas crudas: `-z` y `core.quotePath=false`, sin comillas ni octales.

    El registro de `ls-files --eol` es `i/lf  w/crlf  attr/\\t<ruta>`: el primer campo es **una**
    cadena separada por espacios, no el literal `i/lf`. Partirla por el tab y luego por espacios es lo
    que hace que la seleccion funcione (la primera version de esta funcion filtraba por `cols[0]` y
    devolvia cero rutas, el mismo 0 falso que la casa ya documento cinco veces).
    """
    salida = bash("git -c core.quotePath=false ls-files --eol -z .opencode")
    rutas = []
    for registro in salida.split("\0"):
        if not registro.strip():
            continue
        # Un registro es `i/lf  w/crlf  attr/\t<ruta>`: la cabecera es UN campo con tres columnas
        # separadas por espacios. Partirla por el tab y comparar el primer token es lo que hace que
        # la seleccion funcione; la primera version de esta funcion pedian `cols[0] == "i/lf"` sobre
        # la cabecera entera y devolvia cero rutas (el 0 falso de la casa, sexta vez).
        if "\t" in registro:
            cabecera, ruta = registro.split("\t", 1)
        else:
            cabecera, _, ruta = registro.partition(" ")
        campos = cabecera.split()
        if len(campos) >= 2 and campos[0] == "i/lf" and campos[1] == "w/crlf":
            rutas.append(ruta.strip())
    return rutas


def main():
    conteo_canonico = int(bash(COMANDO_CANONICO).strip())
    rutas = rutas_poblacion()
    extensiones = {}
    for r in rutas:
        extensiones[r.rsplit(".", 1)[-1]] = extensiones.get(r.rsplit(".", 1)[-1], 0) + 1

    status = [l[3:] for l in bash("git status --porcelain -uno").splitlines()]
    sucias_en_poblacion = [r for r in rutas if r in status]

    distintos = []
    for r in rutas:
        disco = (ROOT / r).read_bytes()
        blob = subprocess.run(["git", "cat-file", "blob", f"HEAD:{r}"], capture_output=True,
                              cwd=str(ROOT)).stdout
        if disco.replace(b"\r\n", b"\n") != blob:
            distintos.append(r)

    lineas = [
        "=== C5.1 PRE con el comando canonico de la casa (crudos 27- y 28- de la sesion 1) ===",
        f"comando: {COMANDO_CANONICO}",
        f"residuo_hoy={conteo_canonico}",
        f"residuo_leido_con_quotePath_false_y_z={len(rutas)}   "
        f"(mismo conteo: {conteo_canonico == len(rutas)})",
        f"desglose_por_extension={extensiones}",
        "cifra de la orden: 213 (34 json + 176 md + 2 `md\"` + 1 txt), medida 2026-09-28 en el "
        "crudo 28-",
        f"deriva_contra_213={conteo_canonico - 213}",
        "",
        "=== C5.2 cruce con las doce rutas declaradas de la sesion 1 ===",
        f"lineas_git_status_uno={len(status)}",
        f"de_la_poblacion_que_tambien_esta_sucia={len(sucias_en_poblacion)}",
    ]
    for r in sucias_en_poblacion:
        lineas.append(f"  POBLACION-Y-DECLARADA {r}")
    lineas += ["", "=== C5.3 identidad contra el blob de HEAD, archivo por archivo (criterio 2) ===",
               f"total_poblacion={len(rutas)}",
               f"identicos_al_blob_salvo_EOL={len(rutas) - len(distintos)}",
               f"distintos_por_contenido={len(distintos)}"]
    for r in distintos:
        lineas.append(f"  DISTINTO {r}")
    lineas += ["", "El escritor de C5 solo normaliza los identicos al blob salvo EOL: para esos, la",
               "normalizacion deja el POST byte a byte igual al blob, que es el criterio 2. Los",
               "distintos por contenido quedan declarados y fuera (son trabajo de otra sesion)."]

    destino = S.parent / "24-c5-pre-poblacion.txt"
    destino.write_text("\n".join(lineas) + "\n", encoding="utf-8", newline="\n")
    (S.parent / "_c5_rutas_poblacion.txt").write_text("\n".join(rutas) + "\n",
                                                      encoding="utf-8", newline="\n")
    print("\n".join(lineas))
    print("# crudo en", destino.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
