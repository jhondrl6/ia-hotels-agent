#!/usr/bin/env python3
"""Instrumento de medicion: cuantas veces se calcula cada resultado dentro del
`run_all()` REAL de `scripts/validate_document_integration.py`.

Metodo: se envuelven las funciones verificadoras de nivel de modulo con un contador y
se llama al `run_all()` sin tocar (asi se mide el camino real, incluido su resumen de
errores). El instrumento no escribe en el repo: solo lee.

Salida: 0 si cada verificador se calculo exactamente una vez; 1 si alguno se calculo
mas de una vez (recalculo), con el conteo por verificador.

Modos:
    (sin flags)                     ejecucion normal del arbol vigente
    --rev <rev>                     mide la version **commiteada** del script (`git show <rev>:…`),
                                    materializada en un directorio temporal: el PRE queda anclado a
                                    una fuente versionada, no a «el arbol que estaba cuando corri»
    --forzar-fallo <verificador>   el verificador nombrado se hace fallar con un
                                    ValidationResult sintetico **sin tocar ningun
                                    archivo del repo**, para ejercitar el camino del
                                    resumen de errores (es el unico camino que
                                    re-llama a los validadores)

Uso:
    python "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/instrumentos/medir_recalculo_doc_integration.py" [--forzar-fallo validate_line_endings]
    python "…/medir_recalculo_doc_integration.py" --rev da382b1 --forzar-fallo validate_line_endings
"""
import argparse
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / "scripts" / "validate_document_integration.py"
REL_EN_GIT = "scripts/validate_document_integration.py"

VERIFICADORES = [
    "validate_cross_refs",
    "validate_changelog_format",
    "validate_version_headers",
    "validate_python_path_consistency",
    "validate_agents_cross_ref_table",
    "validate_domain_primer_version",
    "validate_readme_counts",
    "validate_line_endings",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forzar-fallo", metavar="VERIFICADOR", default=None,
                    help="nombra el verificador al que se le inyecta un fallo sintetico")
    ap.add_argument("--rev", default=None,
                    help="commit del que se lee el script con `git show` (fuente versionada)")
    opts = ap.parse_args()
    if opts.forzar_fallo and opts.forzar_fallo not in VERIFICADORES:
        print(f"[ERROR] verificador desconocido: {opts.forzar_fallo} "
              f"(validos: {', '.join(VERIFICADORES)})")
        return 2

    ruta_script = SCRIPT
    tmpdir = None
    if opts.rev:
        proc = subprocess.run(["git", "show", f"{opts.rev}:{REL_EN_GIT}"], capture_output=True,
                              text=True, encoding="utf-8", cwd=str(ROOT))
        if proc.returncode != 0:
            print(f"[ERROR] git salio {proc.returncode}: {proc.stderr.strip()}")
            return 2
        tmpdir = tempfile.TemporaryDirectory(prefix="medir_recalculo_")
        ruta_script = Path(tmpdir.name) / "scripts" / Path(REL_EN_GIT).name
        ruta_script.parent.mkdir(parents=True, exist_ok=True)
        ruta_script.write_text(proc.stdout, encoding="utf-8")

    spec = importlib.util.spec_from_file_location("vdi_medicion", ruta_script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Con `--rev` el modulo carga con PROJECT_ROOT apuntando al temporal, asi que sus validadores
    # reales no verian el repo: se sustituyen por stubs puros. Lo que se mide es cuantas veces
    # `run_all()` pide cada resultado, que es justo la propiedad en juego.
    llamar_original = opts.rev is None

    contador = {}
    for nombre in VERIFICADORES:
        original = getattr(mod, nombre)

        def envuelto(original=original, nombre=nombre):
            contador[nombre] = contador.get(nombre, 0) + 1
            if not llamar_original:
                resultado = mod.ValidationResult(check=nombre, passed=True)
            else:
                resultado = original()
            if nombre == opts.forzar_fallo:
                # Fallo sintetico sobre el resultado ya calculado: no se toca ningun
                # archivo del repo para provocar el rojo.
                resultado = mod.ValidationResult(
                    check=resultado.check, passed=False,
                    issues=[f"FUERZA-DE-MEDICION: {nombre} marcado como fallido por el instrumento"])
            return resultado

        setattr(mod, nombre, envuelto)

    buf = io.StringIO()
    with redirect_stdout(buf):
        pasado = mod.run_all(verbose=False)
    stdout_real = buf.getvalue()

    fuente = (f"git show {opts.rev}:{REL_EN_GIT}" if opts.rev
              else SCRIPT.relative_to(ROOT).as_posix())
    print(f"# COMANDO: python scripts/validate_document_integration.py  (misma ruta de codigo: run_all())")
    print(f"# FUENTE MEDIDA: {fuente}")
    print(f"# VERIFICADORES: {'stubs puros (medicion estructural)' if not llamar_original else 'los reales del modulo'}")
    if opts.forzar_fallo:
        print(f"# MODO: --forzar-fallo {opts.forzar_fallo} (fallo sintetico, sin editar archivos)")
    print(f"# MEDIDO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} por medir_recalculo_doc_integration.py")
    print(f"RESULTADO run_all: {'PASS' if pasado else 'FAIL (hay al menos un check con hallazgos)'}")
    print()
    print(f"{'llamadas':>8}  verificador")
    total = 0
    for nombre in VERIFICADORES:
        veces = contador.get(nombre, 0)
        total += veces
        print(f"{veces:>8}  {nombre}")
    print(f"{total:>8}  TOTAL de calculos de verificadores")
    print()
    exceso = {k: v for k, v in contador.items() if v > 1}
    if exceso:
        print("[HALLAZGO] verificadores calculados mas de una vez por ejecucion:")
        for k, v in sorted(exceso.items()):
            print(f"   - {k}: {v} calculos")
        recalculados = total - len(contador)
        print(f"   recalculo total: {recalculados} calculos extra sobre {len(contador)} verificadores")
        print("EXIT=1")
        return 1
    print("[SIN-HALLAZGOS] cada verificador se calculo exactamente una vez por ejecucion")
    print("EXIT=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
