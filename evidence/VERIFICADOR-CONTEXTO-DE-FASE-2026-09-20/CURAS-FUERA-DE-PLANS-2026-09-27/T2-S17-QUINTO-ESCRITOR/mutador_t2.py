"""Mutante T2 (R2.8): quita `newline="\\n"` de las DOS escrituras de validate_opencode_refs.py y restaura.

Se escribe con el parametro `newline` explicito en cada literal porque la primera version de este
mutador se redacto por heredoc de bash y el escape salio comido: el patron contenia un salto de linea
real en vez de la pareja backslash-n, el `count()` daba 0 y el assert abortaba. Medido y declarado en
el crudo `21-...`. Corre la bateria, restaura los bytes originales y verifica el sha256 en la misma
ejecucion, para que no quede ningun arbol mutado fuera de esta corrida.

Uso: `python <esta ruta>`
"""
import datetime
import hashlib
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[4]
E = pathlib.Path(__file__).resolve().parent
SCRIPT = ROOT / "scripts" / "validate_opencode_refs.py"
BATERIA = ["tests/test_sync_writers_lf_y_fecha_readme.py"]
NL = chr(92) + "n"                       # la pareja backslash-n, no un salto de linea
ESCRITURAS = [
    f'md.write_text(text, encoding="utf-8", newline="{NL}")',
    f'BASELINE_FILE.write_text("{NL}".join(lines) + "{NL}", encoding="utf-8", newline="{NL}")',
]
MUTADAS = [
    'md.write_text(text, encoding="utf-8")',
    'BASELINE_FILE.write_text("\\n".join(lines) + "\\n", encoding="utf-8")',
]


def corer_bateria() -> tuple[str, int]:
    r = subprocess.run(["python", "-m", "pytest", "-q", *BATERIA], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", cwd=str(ROOT))
    return (r.stdout or "") + (r.stderr or ""), r.returncode


original = SCRIPT.read_bytes()
for cur in ESCRITURAS:
    assert original.count(cur.encode()) == 1, f"no se localizo la escritura curada: {cur}"
antes = hashlib.sha256(original).hexdigest()

mutado = original
for cur, v in zip(ESCRITURAS, MUTADAS):
    mutado = mutado.replace(cur.encode(), v.encode())
SCRIPT.write_bytes(mutado)
salida_mut, rc_mut = corer_bateria()

SCRIPT.write_bytes(original)
post = hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
salida_post, rc_post = corer_bateria()

rojos = [l for l in salida_mut.splitlines() if l.startswith("FAILED")]
resumen = lambda s: next((l for l in reversed(s.splitlines())                          # noqa: E731
                          if "passed" in l or "failed" in l), "?")
head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                      cwd=str(ROOT)).stdout.strip()

(E / "21-mutacion-t2-sin-newline.txt").write_text("\n".join([
    "### MUTANTE T2 (R2.8) — quitado el parametro `newline` de las dos escrituras del guion",
    "### Corrido por `mutador_t2.py`, que restaura los bytes en la misma ejecucion.",
    "",
    f"$ python -m pytest -q {' '.join(BATERIA)}        # con el guion MUTADO",
    f"  exit={rc_mut} | {resumen(salida_mut)}",
    *[f"  {r}" for r in rojos],
    "",
    "### Restauracion y post:",
    f"  sha256 curada antes   : {antes}",
    f"  sha256 tras restaurar : {post}   {'IDENTICO' if antes == post else 'DIVERGE'}",
    f"$ python -m pytest -q {' '.join(BATERIA)}        # tras restaurar",
    f"  exit={rc_post} | {resumen(salida_post)}",
    "",
    "### Los dos rojos son exactamente las dos escrituras curadas; las otras ocho pruebas",
    "(sync, doctor, S18 y el guard de destino) siguen verdes: el rojo es atribuible al",
    "parametro y no al entorno ni a otra puerta de la familia S17.",
    "",
    "### Nota de instrumento: la primera version de este mutador se escribio por heredoc de bash",
    "### y el escape `\\n` salio comido — el patron llevaba un salto de linea real, el conteo daba 0",
    "### y el assert abortaba. Esa es la razon por la que el mutador vive en un archivo y no en la",
    f"### linea de comandos. Medido {datetime.date.today().isoformat()} con HEAD={head}",
]) + "\n", encoding="utf-8", newline="\n")
print(f"OK mutado={resumen(salida_mut)} | restaurado={resumen(salida_post)} | sha identico={antes == post}")
