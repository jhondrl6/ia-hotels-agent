"""Mutante T1 (R2.8): devuelve el parrafo «Alcance hacia delante» del workflow a la frase vencida
que estaba en HEAD, sin tocar el resto del archivo ni el fixture del contraejemplo congelado."""
import subprocess, pathlib

W = pathlib.Path(".agents/workflows/phased_project_executor.md")
MARK = "- **Alcance hacia delante**".encode()
LARGO_CURADO = 12       # medido: lineas 728..739 del archivo curado
LARGO_VENCIDO = 5       # medido: el parrafo tal como estaba en HEAD

head = subprocess.run(["git", "show", f"HEAD:{W.as_posix()}"], capture_output=True, check=True).stdout
hlines = head.split(b"\n")
hi = next(i for i, l in enumerate(hlines) if l.startswith(MARK))
vencido = hlines[hi:hi + LARGO_VENCIDO]
assert vencido[0].endswith(": solo".encode()), vencido[0]
assert vencido[4].rstrip().endswith("quedaron exentos.".encode()), vencido[4]
assert b"no est\xc3\xa9n en `Archives/`" in b"\n".join(vencido)

lines = W.read_bytes().split(b"\n")
idx = [i for i, l in enumerate(lines) if l.startswith(MARK)]
assert len(idx) == 1, idx
i = idx[0]
assert lines[i + LARGO_CURADO - 1].rstrip().endswith("validate_lesson_capitalization.py`.".encode()), lines[i + LARGO_CURADO - 1]
W.write_bytes(b"\n".join(lines[:i] + vencido + lines[i + LARGO_CURADO:]))
print(f"MUTADO: parrafo curado de {LARGO_CURADO} lineas -> frase vencida de {LARGO_VENCIDO} (HEAD)")
