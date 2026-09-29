"""C5 POST: refresco de stat del indice sobre las rutas que el escritor normalizo, y verificacion.

Medido en esta tanda: tras escribir las 213 rutas, `git status --porcelain -uno` salto de 18 a 231
lineas mientras `git diff --numstat` estaba **vacio** para esas rutas. Eso es cache de stat, no
contenido: git marcaba el archivo como sospechoso porque cambio de tamano y de mtime, y su via de
refresco «segura» no acepta un round-trip de CRLF sin `--really-refresh`.

El refresco se limita a las rutas del informe del escritor (no se toca el indice del resto del
arbol). No se stagea nada: `update-index --really-refresh` actualiza el stat y deja como modificados
los que si tienen contenido nuevo — que son los declarados, y se comprueba aqui.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
S = pathlib.Path(__file__)
INFORME = S.parent / "26b-c5-informe-fix.json"
COMANDO_CANONICO = ("git ls-files --eol .opencode | awk '$1==\"i/lf\" && $2==\"w/crlf\"' | wc -l")


def sh(args, shell=False, stdin=None):
    proc = subprocess.run(args, capture_output=True, cwd=str(ROOT), shell=shell, text=True,
                          encoding="utf-8", input=stdin)
    return proc.returncode, proc.stdout, proc.stderr


def main():
    informe = json.loads(INFORME.read_text(encoding="utf-8"))
    rutas = [n["ruta"] for n in informe["normalizados"]]
    out = [f"rutas_normalizadas_por_el_escritor={len(rutas)}"]

    rc, antes, _err = sh("git status --porcelain -uno", shell=True)
    n_antes = len([l for l in antes.splitlines() if l.strip()])
    rc, diff_antes, _ = sh("git diff --name-only", shell=True)
    out += [f"git_status_uno_ANTES_del_refresco={n_antes}",
            f"git_diff_name_only_ANTES={len([l for l in diff_antes.splitlines() if l.strip()])}"]

    # Refresco solo las rutas del escritor, con -z y stdin: sin toparse a limites de argv ni a
    # comillas de las rutas con acentos.
    rc, stdout, stderr = sh(["git", "update-index", "--really-refresh", "-z", "--stdin"],
                            stdin="\0".join(rutas) + "\0")
    out += [f"update-index_really-refresh_EXIT={rc}",
            f"stdout={stdout.strip()[:400] or '(vacio)'}",
            f"stderr={stderr.strip()[:400] or '(vacio)'}"]

    rc, despues, _ = sh("git status --porcelain -uno", shell=True)
    lineas = [l for l in despues.splitlines() if l.strip()]
    rc, diff2, _ = sh("git diff --name-only", shell=True)
    names = sorted(l[3:] for l in lineas)
    out += [f"git_status_uno_DESPUES_del_refresco={len(lineas)}",
            f"git_diff_name_only_DESPUES={len([l for l in diff2.splitlines() if l.strip()])}",
            "", "=== la poblacion que queda en git status, con su explicacion ==="]
    declaradas = set()
    for l in lineas:
        ruta = l[3:]
        if ruta.startswith("scripts/"):
            banda = "SCRIPT (C1, C2, C3, C4, C7)"
        elif ruta.startswith("tests/"):
            banda = "TEST (baterias de la orden)"
        elif "dependencias-fases" in ruta:
            banda = "FILLA SELLADA (C6)"
        elif ruta == ".opencode/plans/plan_citations_baseline.json":
            banda = "BASELINE DE CITAS (paso 3 del pipeline)"
        elif ruta.startswith(".opencode/plans/Archives/"):
            banda = "ANOTACION O PACK DE LA SESION 1"
        elif ruta in (".opencode/refs_baseline.txt", ".opencode/wiring_report.json"):
            banda = "SALIDA DE ESCRITOR DEL PIPELINE"
        else:
            banda = "FUERA DE POBLACION"
        declaradas.add(ruta)
        out.append(f"  {banda:38s} {ruta}")

    # El conteo canonico lleva `awk`, que en Windows solo existe bajo bash: `shell=True` de Python
    # cae en cmd.exe, el awk falla y deja en stdout el `ls-files --eol` sin filtrar (medido en la
    # primera corrida de este crudo). Se pasa por `bash -c`, como en el PRE.
    rc, residuo, err = sh(["bash", "-c", COMANDO_CANONICO])
    out += ["", "=== C5.3 POST del residuo con el MISMO comando del PRE ===",
            f"comando: {COMANDO_CANONICO}",
            f"rc={rc} stderr={err.strip()[:120] or '(vacio)'}",
            f"residuo_DESPUES={residuo.strip()}",
            f"criterio_3_cumplido={residuo.strip() == '0'}",
            "", "=== C5.4 identidad: ningun contenido de la poblacion difiere de HEAD ===",
            f"rutas_de_la_poblacion_que_aparecen_en_git_status="
            f"{len([r for r in rutas if r in declaradas])}",
            "(cero es el resultado esperado: normalizar EOL no cambia el blob; si alguna aparece, "
            "esa ruta tiene contenido nuevo y habria que declararla aparte)"]

    destino = S.parent / "27-c5-post-y-refresco.txt"
    destino.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(out))
    print("# crudo en", destino.relative_to(ROOT).as_posix())
    return 0 if residuo.strip() == "0" else 1


if __name__ == "__main__":
    sys.exit(main())
