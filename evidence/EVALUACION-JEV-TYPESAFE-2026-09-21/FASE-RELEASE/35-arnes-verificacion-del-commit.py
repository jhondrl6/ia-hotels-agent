# -*- coding: utf-8 -*-
"""Sello del commit de FASE-RELEASE: verificar el commiteado en SU PROPIO arbol, fuera del repo.

La regla de la casa es que un verde lleva la etiqueta del árbol donde corrió. Este arnés clona el
commit en un directorio temporal fuera del workspace (con `--no-checkout`, y `core.longpaths` y
`core.autocrlf=input` DENTRO del clon), y allí adentro:

  1. corre la batería del piloto (el SDK del entorno aislado no existe en el clon: los saltos llevan
     su causa nombrada por el fixture `sdk`, y se cuentan en vez de esconderse);
  2. reproduce `report` y `decide` y compara por sha256 **normalizado a LF** contra los artefactos
     commiteados — el disco del repo es CRLF y el blob es LF, así que la identidad de bytes crudos
     entre máquinas no es el contrato; la identidad normalizada sí;
  3. cuenta las funciones `def test_` commiteadas sin tocar ningún árbol.

No muta el repositorio: escribe el clon bajo la carpeta temporal del sistema y la borra al final.
"""
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COMMIT = sys.argv[1] if len(sys.argv) > 1 else None
PYEXE = sys.executable
EXP = "evidence/EVALUACION-JEV-TYPESAFE-2026-09-21"


def correr(args, cwd, captura=True):
    r = subprocess.run(args, cwd=str(cwd), capture_output=captura, text=True,
                       encoding='utf-8', errors='replace')
    return r.returncode, (r.stdout or '') + (r.stderr or '')


def norm(b: bytes) -> str:
    return hashlib.sha256(b.replace(b'\r\n', b'\n')).hexdigest()


def main():
    if not COMMIT:
        print("uso: 35-arnes-verificacion-del-commit.py <revision>   (EXIT 2)")
        return 2
    destino = Path(tempfile.gettempdir()) / f"clone-jev-{COMMIT[:7]}"
    if destino.exists():
        shutil.rmtree(destino, ignore_errors=True)

    print("=" * 78)
    print(f"== verificacion del commit {COMMIT} en su propio arbol")
    print("=" * 78)

    rc, out = correr(["git", "clone", "--no-checkout", f"file:///{ROOT}", str(destino)], ROOT)
    print(f"-- clone EXIT={rc}")
    if rc != 0:
        print(out[-800:])
        return 1
    for cfg, val in (("core.longpaths", "true"), ("core.autocrlf", "input")):
        rc, _ = correr(["git", "config", cfg, val], destino)
        print(f"-- git config {cfg}={val} EXIT={rc}")
    rc, out = correr(["git", "checkout", "-q", COMMIT], destino)
    rc_head, head = correr(["git", "rev-parse", "HEAD"], destino)
    rc_st, st = correr(["git", "status", "--porcelain"], destino)
    lineas = [l for l in st.split('\n') if l.strip()]
    print(f"-- checkout EXIT={rc} | HEAD={head.strip()} | entradas del status={len(lineas)}")
    for l in lineas[:10]:
        print("     ", l)

    print()
    print("== 1. bateria del piloto en el clon")
    rc, out = correr([PYEXE, "-m", "pytest", "tests/quality_gates/jev_pilot", "-q"], destino)
    resumen = [l for l in out.split('\n') if ' passed' in l or ' failed' in l or 'error' in l]
    print(f"   EXIT={rc} | {' | '.join(resumen[-2:])}")
    print("   (los skipped son el SDK del entorno aislado, ausente en el clon, con su causa por fixture)")

    print()
    print("== 2. reproduccion de report y decide dentro del clon, contra lo commiteado")
    (destino / "scratch").mkdir(exist_ok=True)
    rc, _ = correr([PYEXE, "scripts/evaluate_jev_pilot.py", "report",
                    "--respuestas", f"{EXP}/FASE-C/respuestas.jsonl",
                    "--etiquetas", f"{EXP}/etiquetas.json",
                    "--muestra", f"{EXP}/muestra.json",
                    "--protocolo", f"{EXP}/protocolo.json",
                    "--out", "scratch/informe_comparativa.json", "--fecha", "2026-10-05"], destino)
    print(f"   report en el clon: EXIT={rc}  (0 = emitido)")
    rc2, _ = correr([PYEXE, "scripts/evaluate_jev_pilot.py", "decide",
                     "--informe", "scratch/informe_comparativa.json",
                     "--protocolo", f"{EXP}/protocolo.json",
                     "--out-dir", "scratch", "--fecha", "2026-10-05"], destino)
    print(f"   decide en el clon: EXIT={rc2}  (3 = emitido sin decision)")
    for n in ("informe_comparativa.json", "decision.json", "decision.md"):
        a = (destino / "scratch" / n).read_bytes()
        b = (destino / EXP / "FASE-RELEASE" / n).read_bytes()
        print(f"   {n:26s} normalizado clon={norm(a)[:16]} normalizado commiteado={norm(b)[:16]} "
              f"{'IGUAL' if norm(a) == norm(b) else 'DIVERGE'}")
        print(f"       crudo clon={hashlib.sha256(a).hexdigest()[:12]} (CRLF del disco) "
              f"crudo clon-checkout={hashlib.sha256((destino / EXP / 'FASE-RELEASE' / n).read_bytes()).hexdigest()[:12]}")

    print()
    print("== 3. cifra canonica commiteada, medida sin tocar el arbol de trabajo")
    rc, out = correr(["git", "grep", "-h", "-c", "-E", r"^\s*def test_", COMMIT, "--", "tests/*.py"], ROOT)
    total = sum(int(l) for l in out.split('\n') if l.strip().isdigit())
    print(f"   git grep -h -c -E ... {COMMIT[:7]} -- tests/*.py  sumado = {total}")

    shutil.rmtree(destino, ignore_errors=True)
    print()
    print(f"-- clon eliminado: {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
