"""Cierre de la tanda: LF en los crudos propios y las cifras que viajan con el commit.

1. Los artefactos que ESTA sesion escribio pasan a LF puro (regla de la casa). El barrido se limita al
   directorio de evidencia de la sesion: la poblacion de C5 ya la normalizo su propio escritor, y los
   archivos del arbol versionado no se tocan aqui.
2. Las cifras del reporte: funciones de test con el metodo canonico (arbol de trabajo) y con el del
   arbol versionado (`git grep -c ... HEAD`), y el desglose por archivo que explica la deriva.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
S = pathlib.Path(__file__)
DIR = S.parent
BATERIAS = ["tests/test_sync_writers_lf_y_fecha_readme.py",
            "tests/test_run_all_validations_denominador_por_modo.py",
            "tests/quality_gates/governance_numbers/test_governance_numbers_estados_sin_puntero_d1.py",
            "tests/quality_gates/phase_briefing/test_briefing_proyeccion_workflow_gobernada.py"]


def sh(args, shell=False):
    """`shell=True` de Python bajo Windows es cmd.exe, y cmd.exe NO trata 'como comilla: el patron
    `'^\\s*def test_'` llega con las comillas puestas y da 0 coincidencias (medido: la columna HEAD
    salio 0 sobre archivos que si tienen funciones). Toda linea de shell se pasa por `bash -c`."""
    if shell is True:
        args = ["bash", "-c", args]
        shell = False
    proc = subprocess.run(args, capture_output=True, cwd=str(ROOT), shell=shell, text=True,
                          encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def main():
    salida = ["=== 1. LF en los artefactos propios de la sesion ==="]
    normalizados, ya_lf, cr_altos = 0, 0, []
    for p in sorted(DIR.rglob("*")):
        if not p.is_file() or p == S or p.suffix == ".bak":
            continue
        b = p.read_bytes()
        if bytes([13]) not in b:
            ya_lf += 1
            continue
        nuevo = b.replace(b"\r\n", b"\n")
        restantes = nuevo.count(bytes([13]))
        if restantes:
            cr_altos.append((p.name, restantes))
        p.write_bytes(nuevo)
        normalizados += 1
    salida += [f"archivos_mirados={ya_lf + normalizados}",
               f"ya_estaban_en_LF={ya_lf}",
               f"normalizados_por_este_cierre={normalizados}",
               f"CR_sueltos_conservados={cr_altos or '(ninguno)'}", ""]

    salida += ["=== 2. las cifras de test, con los dos instrumentos ==="]
    rc1, disco, _ = sh("grep -rE '^\\s*def test_' tests --include=*.py | wc -l", shell=True)
    rc2, head, _ = sh("git grep -c -E '^\\s*def test_' HEAD -- tests | "
                      "awk -F: '{s+=$NF} END {print s}'", shell=True)
    n_disco, n_head = int(disco or 0), int(head or 0)
    salida += [f"metodo_canonico_arbol_de_trabajo={n_disco} (rc={rc1})",
               f"arbol_versionado_HEAD={n_head} (rc={rc2})",
               f"deriva_de_la_tanda={n_disco - n_head}",
               "cifra publicada en AGENTS.md (seccion Cobertura por Modulo): 4.590",
               f"la cabecera de AGENTS.md NO se toco en esta sesion (prohibido; es instruccion aparte)",
               "", "-- las cuatro baterias que explican la deriva --"]
    for rel in BATERIAS:
        p = ROOT / rel
        rc, n, _ = sh(f"grep -cE '^\\s*def test_' '{rel}'", shell=True)
        rc2, h, _ = sh(f"git show HEAD:'{rel}' 2>/dev/null | grep -cE '^\\s*def test_'", shell=True)
        salida.append(f"  {p.name:58s} disco={n or 0:>3}  HEAD={h or 0:>3}")
    salida.append(f"  suma de la columna disco debe casar con la deriva + {n_head}")

    rc, crudos, _ = sh(f"bash -c 'ls -1 {DIR.relative_to(ROOT).as_posix()} | wc -l'", shell=True)
    rc, est, _ = sh("git status --porcelain -uno | wc -l", shell=True)
    rc, sinv, _ = sh("git ls-files --others --exclude-standard | wc -l", shell=True)
    salida += ["", "=== 3. inventario del cierre ===",
               f"entradas_del_directorio_de_evidencia={crudos}",
               f"lineas_git_status_uno={est}",
               f"archivos_sin_versionar_en_el_repo={sinv}",
               f"HEAD_sigue_en=$(git rev-parse --short HEAD)".replace("$(git rev-parse --short HEAD)",
                                                                     sh("git rev-parse --short HEAD",
                                                                        shell=True)[1])]

    destino = DIR / "35-cierre-lf-y-cifras.txt"
    destino.write_text("\n".join(salida) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(salida))
    print("# crudo en", destino.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
