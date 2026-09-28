"""Crudo T3 (R2.8, control negativo de S31): muta el puente, mide el rojo, restaura y re-mide.

Se corre como script y no como `echo` + `pytest` encadenados porque el texto lleva backticks: bash
convertia la llamada `ruta_plan()` en una sustitucion de comando y el crudo salia mutilado (medido
en la primera version de este archivo). El script muta, mide, **restaura en la misma corrida** y
verifica la huella, asi que no queda ninguna ventana con el arbol mutado.

Uso: `python <esta ruta>`
"""
import datetime
import hashlib
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[4]
E = pathlib.Path(__file__).resolve().parent
PUENTE = ROOT / "tests" / "support_resolucion_plan.py"
BATERIA = ["tests/quality_gates/lesson_relevance", "tests/quality_gates/phase_briefing"]
CURADA = b"    resuelto = bpb.resolver_plan(nombre, plans_dir)"
MUTADA = b"    resuelto = Path(plans_dir) / nombre   # MUTANTE: raiz a pelo, como antes de S31"


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def bateria() -> tuple[str, int]:
    r = subprocess.run(["python", "-m", "pytest", "-q", *BATERIA], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", cwd=str(ROOT))
    return (r.stdout or "") + (r.stderr or ""), r.returncode


def resumen(s: str) -> str:
    return next((l for l in reversed(s.splitlines()) if "passed" in l or "failed" in l), "?")


original = PUENTE.read_bytes()
assert original.count(CURADA) == 1, "el puente no esta en la forma curada esperada"
antes = sha(PUENTE)

PUENTE.write_bytes(original.replace(CURADA, MUTADA))
mut_sha = sha(PUENTE)
salida_mut, rc_mut = bateria()

PUENTE.write_bytes(original)
post_sha = sha(PUENTE)
salida_post, rc_post = bateria()

firmas = sorted({l.strip()[:220] for l in salida_mut.splitlines() if "FileNotFoundError" in l})
head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                      cwd=str(ROOT)).stdout.strip()
cmd = f"python -m pytest -q {' '.join(BATERIA)}"

lineas = [
    "### MUTANTE T3 (R2.8) — el puente de resolucion deja de preguntar al escritor",
    "### Mutacion: `ruta_plan()` resuelve `plans_dir / nombre` a pelo, o sea la ruta de RAIZ que los",
    "### seis arneses pineaban antes del `git mv` de D-c (`3c2e6a3`, 2026-09-26). No es una",
    "### simulacion del defecto: es el defecto, con el nombre de la ruta vieja.",
    "### Corrido por `crudo_t3.py` (este mismo directorio), que restaura los bytes en la misma corrida.",
    "",
    f"$ {cmd}          # con el puente MUTADO",
    f"  exit={rc_mut} | {resumen(salida_mut)}",
    f"  FAILED={sum(1 for l in salida_mut.splitlines() if l.startswith('FAILED'))}"
    f"  ERROR={sum(1 for l in salida_mut.splitlines() if l.startswith('ERROR'))}",
    "",
    "### Firma del rojo (FileNotFoundError, deduplicada):",
    *([f"  {f}" for f in firmas[:3]] or ["  (no aparecio la firma esperada)"]),
    "",
    "### Nota de fidelidad: revertir los arneses al literal ACTUAL (`plans/Archives/<PLAN>`) NO da",
    "### rojo, porque hoy el plan si esta ahi. El rojo sale contra la ruta donde el plan ya no vive,",
    "### y ahi esta la leccion: el literal no es fragil el dia que se escribe, es fragil contra el",
    "### proximo traslado. Por eso el control se corre sobre la ruta de raiz.",
    "",
    "### RESTAURACION",
    f"  sha256 curada antes   : {antes}",
    f"  sha256 del mutante    : {mut_sha}",
    f"  sha256 tras restaurar : {post_sha}   {'IDENTICO' if antes == post_sha else 'DIVERGE'}",
    f"$ {cmd}          # tras restaurar",
    f"  exit={rc_post} | {resumen(salida_post)}",
    "",
    f"### Medido {datetime.date.today().isoformat()} sobre el arbol de trabajo con HEAD={head}",
]
(E / "31-mutante-y-restauracion-t3.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8",
                                                    newline="\n")
print(f"CRUDO 31 escrito | mutado: {resumen(salida_mut)} | restaurado: {resumen(salida_post)} | "
      f"sha identico={antes == post_sha}")
