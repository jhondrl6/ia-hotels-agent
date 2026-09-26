#!/usr/bin/env python3
"""Delta PRE/POST del bloque B medido sobre el MISMO trabajo, no sobre cifras ajenas.

PRE = el arbol commiteado `da382b1` (antes de TODO B), recuperado con `git show` sin tocar el
arbol de trabajo: sin stash, sin checkout, sin escribir en destinos historicos.
POST = el arbol actual de la remediacion.

**Limite declarado:** la primera pasada de B nunca se commiteo, asi que su estado intermedio
no es recuperable por git y por eso no se reclama como PRE (es exactamente el error del
«24 passed / 16 errors» que el mandato retiro). La pareja comparable es HEAD vs ahora.

Terminales medidos:
  T1  afirmaciones `- [x]` que publica UNA entrada del registro (mismos args de entrada)
  T2  calculos de verificador dentro de `validate_document_integration.run_all()` con un fallo
  T3  instrucciones que mandan transcribir metricas a un documento secundario (plantilla)
  T4  instrucciones que mandan re-registrar fases en el cierre documental (executor)
  T5  duracion de la seleccion de pruebas afectada (se publica aunque empeore)

Uso:
    python "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/instrumentos/medir_deltas_b.py"
"""
import importlib.util
import io
import re
import subprocess
import sys
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = "da382b1"
PLANTILLA = ".agents/workflows/templates/prompt-fase-template.md"
EJECUTOR = ".agents/workflows/phased_project_executor.md"
LPC = "scripts/log_phase_completion.py"
VDI = "scripts/validate_document_integration.py"

# Los mismos argumentos de entrada para las dos versiones del escritor: es lo que hace
# comparable T1 (no es «la entrada que toco en cada fase», es la misma corrida).
ARGS = dict(fase="FASE-MEDICION", desc="medicion comparable PRE/POST",
            archivos_nuevos="modules/nuevo.py", archivos_mod="modules/viejo.py",
            tests="13", coherence=0.5)


def _mostrar(rel: str) -> str:
    r = subprocess.run(["git", "show", f"{BASE}:{rel}"], capture_output=True, cwd=str(ROOT))
    if r.returncode != 0:
        raise SystemExit(f"git show {BASE}:{rel} fallo: {r.stderr.decode('utf-8', 'replace')}")
    return r.stdout.decode("utf-8", errors="replace")


def _cargar_texto(nombre: str, codigo: str, path_virtual: Path):
    src = Path(path_virtual)
    spec = importlib.util.spec_from_loader(
        nombre, loader=None, origin=str(src))
    mod = importlib.util.module_from_spec(spec)
    mod.__file__ = str(src)
    exec(compile(codigo, str(src), "exec"), mod.__dict__)   # noqa: S102 - carga del PRE versionado
    return mod


def _args(mod):
    ns = type("NS", (), {})()
    for k, v in ARGS.items():
        setattr(ns, k, v)
    ns.fase = ARGS["fase"]
    return ns


def t1_entradas():
    from types import SimpleNamespace
    args = SimpleNamespace(**ARGS)
    salida = {}
    for etiqueta, codigo, virtual in (
            ("PRE", _mostrar(LPC), ROOT / "scripts" / "log_phase_completion.py"),
            ("POST", (ROOT / "scripts" / "log_phase_completion.py").read_text(encoding="utf-8"),
             ROOT / "scripts" / "log_phase_completion.py")):
        mod = _cargar_texto(f"lpc_{etiqueta.lower()}", codigo, virtual)
        entrada = mod.generar_entrada_registry(args)
        salida[etiqueta] = {
            "lineas_x": re.findall(r"(?m)^- \[x\].*$", entrada),
            "casillas_vacias": len(re.findall(r"(?m)^- \[ \]", entrada)),
            "dice_declarado": bool(re.search(r"declarad", entrada, re.IGNORECASE)),
            "longitud": len(entrada),
        }
    return salida


def t2_calculos():
    """Corre el mismo instrumento de medicion sobre el PRE (HEAD) y sobre el POST."""
    script = (ROOT / "evidence" / "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
              / "BLOQUE-B-REMEDIACION-2026-09-23" / "instrumentos"
              / "medir_recalculo_doc_integration.py")
    r = subprocess.run([sys.executable, str(script), "--forzar-fallo", "validate_line_endings"],
                       capture_output=True, text=True, cwd=str(ROOT))
    total = re.search(r"TOTAL de calculos de verificadores", r.stdout)
    cifra = re.findall(r"^\s*(\d+)\s+TOTAL", r.stdout, re.MULTILINE)
    return {"exit": r.returncode, "calculos_post": int(cifra[0]) if cifra else None,
            "hubo_total": bool(total), "stdout_last": r.stdout.strip().splitlines()[-1:]}


def t3_y_t4(texto_pre: str, texto_post: str, patron: str):
    f = lambda t: len(re.findall(patron, t, re.MULTILINE))
    return {"PRE": f(texto_pre), "POST": f(texto_post)}


def main() -> int:
    print(f"# MEDIDO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} por medir_deltas_b.py")
    print(f"# PRE = git show {BASE}:… (arbol commiteado antes de TODO B; sin stash ni checkout)")
    print("# POST = arbol de trabajo actual de la remediacion")
    print("# Limite: la primera pasada de B no esta en git (no se commiteo), asi que no es PRE\n")

    entradas = t1_entradas()
    print("T1 — una entrada de REGISTRY con los MISMOS args "
          f"(--tests {ARGS['tests']!r}, --coherence {ARGS['coherence']}):")
    for etiqueta in ("PRE", "POST"):
        d = entradas[etiqueta]
        print(f"   {etiqueta}: casillas `- [x]` = {len(d['lineas_x'])} | "
              f"`- [ ]` = {d['casillas_vacias']} | declara «declarado» = {d['dice_declarado']} | "
              f"{d['longitud']} chars")
        for linea in d["lineas_x"]:
            print(f"      - {linea}")

    print("\nT2 — calculos de verificador en `validate_document_integration.run_all()` "
          "con un fallo inyectado (POST; el PRE esta preservado en PRE_recalculo_doc_integration.txt):")
    t2 = t2_calculos()
    print(f"   POST: {t2['calculos_post']} calculos para 8 verificadores, exit {t2['exit']} "
          f"({t2['stdout_last']})")

    pl_pre, pl_post = _mostrar(PLANTILLA), (ROOT / PLANTILLA).read_text(encoding="utf-8")
    ej_pre, ej_post = _mostrar(EJECUTOR), (ROOT / EJECUTOR).read_text(encoding="utf-8")

    # T3: ordenes de transcribir metricas a un documento secundario (README / 10-analisis).
    t3 = t3_y_t4(pl_pre, pl_post,
                 r"(?m)^\s*-\s+\*\*(?:Seccion D|Métricas de Ejecución)\*\*?:?\s*"
                 r"(?:Actualizar con datos reales|Actualizar metricas acumulativas)"
                 r"|Actualizar métricas \(tests, validaciones\)")
    print("\nT3 — plantilla: instrucciones que mandaban transcribir la metrica a un segundo "
          f"documento: PRE {t3['PRE']} → POST {t3['POST']} (ahora: referencia a 09 §D)")

    # T4: en el cierre documental, ejecuciones del escritor ordenadas "por cada fase".
    t4 = t3_y_t4(ej_pre, ej_post,
                 r"por cada fase|Registrar cada fase del plan|UNA vez por cada fase documentada")
    print(f"T4 — executor: frases que ordenaban (re)registrar por cada fase en el cierre "
          f"documental: PRE {t4['PRE']} → POST {t4['POST']}")
    for etiqueta, texto in (("PRE", ej_pre), ("POST", ej_post)):
        hits = [l.strip() for l in texto.splitlines()
                if re.search(r"por cada fase|Registrar cada fase del plan|"
                             r"UNA vez por cada fase documentada", l)]
        print(f"   {etiqueta}: {hits if hits else '—'}")

    print("\nT5 — ver tiempos de la seleccion afectada: leer "
          "PRE_suite_governance_registry.txt y POST_suite_b_remediacion.txt "
          "(se publican funcion y duracion aunque el cambio sea adverso).")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
