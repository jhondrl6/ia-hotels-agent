"""Re-derivacion del gap de contrato del piloto JEV (B3), medida, no heredada.

Metodos publicados los dos, porque el numero del expediente no reproduce ninguno:
  - literal:    el nombre exacto de los 11 campos aparece como token en decision_client.py
  - semantico:  identidad semantica declarada (mapeo explicito, no inferencia implicita)

La costura se localiza por AST, no por un nombre de clase copiado de un prompt: se toman las
clases con `__slots__` y la que figura como tipo de retorno de alguna funcion del propio archivo.

M1: incluye control positivo en la misma corrida y con el mismo instrumento.
"""
import ast
import re
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[4]
SEAM = ROOT / "scripts" / "decision_client.py"
MAESTRO = ROOT / ".opencode" / "plans" / "EVALUACION-JEV-TYPESAFE-2026-09-21" / "01-plan-maestro.md"
README_JEV = ROOT / ".opencode" / "plans" / "EVALUACION-JEV-TYPESAFE-2026-09-21" / "README.md"

# Identidad semantica declarada: slot de la costura -> campo del contrato del piloto
SEMANTICO = {
    "proveedor": "provider_effective",
    "modelo": "model_effective",
    "respuestas": "answers",
    "usage": "usage_raw",
    "request_id": "request_id",
}


def norm(s):
    d = unicodedata.normalize("NFD", s)
    return "".join(c for c in d if not unicodedata.combining(c)).lower()


def campos_requeridos():
    txt = MAESTRO.read_text(encoding="utf-8")
    m = re.search(r"Contrato requerido para el piloto:(.+)", txt)
    if not m:
        raise SystemExit("no se encontro la linea del contrato requerido en 01-plan-maestro.md")
    return re.findall(r"`([a-z_]+)`", m.group(1))


def costura():
    src = SEAM.read_text(encoding="utf-8")
    tree = ast.parse(src)
    clases = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.ClassDef):
            for st in n.body:
                if isinstance(st, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "__slots__" for t in st.targets
                ):
                    clases[n.name] = [
                        e.value for e in ast.iter_child_nodes(st.value) if isinstance(e, ast.Constant)
                    ]
    rets = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.returns is not None:
            for c in ast.walk(n.returns):
                if isinstance(c, ast.Name):
                    rets.add(c.id)
    return clases, rets & set(clases), src


def tokens(src):
    return set(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", src))


def main():
    requeridos = campos_requeridos()
    clases, retornos, src = costura()
    toks = tokens(src)

    print("== 1. contrato del piloto: campos exigidos ==")
    print(f"fuente: {MAESTRO.relative_to(ROOT).as_posix()} :: 'Contrato requerido para el piloto:'")
    print(f"exigidos: {len(requeridos)} -> {requeridos}")

    print()
    print("== 2. costura real por AST ==")
    for c in sorted(clases):
        mark = "  <-- COSTURA (tipo de retorno de una funcion del archivo)" if c in retornos else ""
        print(f"  class {c}: __slots__ = {list(clases[c])}{mark}")
    if len(retornos) != 1:
        print(f"  AVISO: {len(retornos)} clases con slots devueltas por funciones: {sorted(retornos)}")
    seam_name = sorted(retornos)[0] if retornos else None
    slots = clases.get(seam_name, [])

    print()
    print("== 3. metodo LITERAL (nombre exacto presente en decision_client.py) ==")
    lit_faltan = [c for c in requeridos if c not in toks]
    for c in requeridos:
        print(f"  {'PRESENTE' if c in toks else 'AUSENTE  '}  {c}")
    print(f"  ausentes por literal: {len(lit_faltan)} -> {lit_faltan}")

    print()
    print("== 4. metodo SEMANTICO (identidad declarada slot->campo) ==")
    cubiertos = sorted(SEMANTICO.values())
    for c in requeridos:
        if c in cubiertos:
            slot = [k for k, v in SEMANTICO.items() if v == c][0]
            print(f"  CUBIERTO   {c}  <- slot '{slot}' (en la costura: {slot in slots})")
        else:
            print(f"  AUSENTE    {c}")
    sem_faltan = [c for c in requeridos if c not in cubiertos]
    print(f"  ausentes por semantico: {len(sem_faltan)} -> {sem_faltan}")

    print()
    print("== 5. lo que publica el consumidor (README de JEV, linea del gap) ==")
    rd = README_JEV.read_text(encoding="utf-8")
    for ln in rd.splitlines():
        if "Gap de contrato medido" in ln or ("no** expone" in norm(ln)) or "no expone" in norm(ln):
            m = re.findall(r"`([a-z_]+)`", ln)
            print(f"  backticks en la linea del gap: {m}")
    gap_line = [ln for ln in rd.splitlines() if "Gap de contrato medido" in ln]
    print(f"  lineas que nombran el gap: {len(gap_line)}")

    print()
    print("== 6. CONTROL POSITIVO (M1) ==")
    # el mismo instrumento, la misma normalizacion: debe encontrar lo que se sabe presente
    probes = [
        ("el bloque C y el piloto FASE-C no lo están", str(ROOT / ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/README.md"), True),
        ("provider_requested", str(SEAM), False),
        ("request_id", str(SEAM), True),
    ]
    for needle, path, esperado in probes:
        hay = norm(needle) in norm(Path(path).read_text(encoding="utf-8"))
        ok = "OK" if hay == esperado else "FALLO"
        print(f"  [{ok}] {Path(path).name}: {needle!r} -> encontrado={hay} esperado={esperado}")

    print()
    print("== 7. SUMA ==")
    print(f"  literal {len(lit_faltan)} + semantico {len(sem_faltan)} sobre {len(requeridos)} exigidos")


if __name__ == "__main__":
    main()
