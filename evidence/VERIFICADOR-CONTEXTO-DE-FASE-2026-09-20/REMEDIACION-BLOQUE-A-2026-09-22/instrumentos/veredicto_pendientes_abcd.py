"""Veredicto de los pendientes técnicos a-d del bloque A (sesión 2, 2026-09-22).

Compara la revisión HEAD (extraída con `git show`, sin stash sobre trabajo sin commitear) contra el
árbol de trabajo en los seis comportamientos que esta sesión añadió. Rojo en HEAD por SU causa y
verde en el árbol es la demostración que pide el §4 de la autorización; cada criterio imprime la
causa de su rojo, no solo la etiqueta.

Uso:
    python instrumentos/veredicto_pendientes_abcd.py            # HEAD vs arbol de trabajo
Salida: un bloque por criterio; exit 0 solo si TODOS pasan en el árbol de trabajo.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
PUERTA = RAIZ / "scripts" / "decision_client.py"
GN = RAIZ / "scripts" / "validate_governance_numbers.py"


def _cargar(ruta: Path, nombre: str):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _version_head(ruta_repo: Path, ruta_archivo: str, destino: Path) -> Path:
    texto = subprocess.run(["git", "show", f"HEAD:{ruta_archivo}"], cwd=str(ruta_repo),
                           capture_output=True, text=True, check=True).stdout
    destino.write_text(texto, encoding="utf-8")
    return destino


FUENTE = '''#!/usr/bin/env python3
class Runner:
    def run_all(self) -> None:
        self._check_alpha()
        self._check_beta()

    def _check_alpha(self) -> None:
        """Chequea alpha."""
        print("[1/2] Checking alpha...")
        script_path = ROOT_DIR / "scripts" / "validate_alpha.py"

    def _check_beta(self) -> None:
        print("[2/2] Checking beta...")
        script_path = ROOT_DIR / "scripts" / "validate_beta.py"
'''

HOOK = '''#!/bin/sh
# Pasos:
#   [1/2] Alpha check (validate_alpha.py)
#   [2/2] Beta check (validate_beta.py)
echo "[1/2] Checking alpha..."
echo "[2/2] Checking beta..."
'''

DOC_OK = (
    "**Verificador**: `scripts/validate_alpha.py` es check 1 de `run_all_validations.py --quick`.\n"
    "Beta corre como `[2/2]` de `run_all_validations.py --quick` (`scripts/validate_beta.py`).\n"
)


def _fixture_gn(tmp: Path) -> dict:
    source = tmp / "run_all_validations.py"
    source.write_text(FUENTE, encoding="utf-8")
    hook = tmp / "pre-commit"
    hook.write_text(HOOK, encoding="utf-8")
    doc = tmp / "workflow.md"
    doc.write_text(DOC_OK, encoding="utf-8")
    return {"source": source, "hook": hook, "doc": doc}


def _criterios(mod, mod_gn, tmp: Path) -> list:
    criterios = []

    # C1 (a): poblacion vacia no cierra favorable
    vacio = tmp / "arbol-vacio"
    vacio.mkdir(parents=True, exist_ok=True)
    scan = mod.escanear_aislamiento(vacio, puerta=vacio / "decision_client.py")
    criterios.append((
        "C1 SIN-POBLACION",
        scan["status"] == "SIN-POBLACION",
        f"arbol sin archivos devolvio status {scan['status']!r} (favorable sobre poblacion 0)",
    ))

    # C2 (a): lectura incompleta no cierra favorable
    roto_raiz = tmp / "repo-roto"
    (roto_raiz / "modules").mkdir(parents=True, exist_ok=True)
    (roto_raiz / "modules" / "roto.py").write_text("def x(\n", encoding="utf-8")
    puerta = roto_raiz / "decision_client.py"
    puerta.write_text("import json\n", encoding="utf-8")
    scan2 = mod.escanear_aislamiento(roto_raiz, puerta=puerta)
    criterios.append((
        "C2 LECTURA-INCOMPLETA",
        scan2["status"] == "LECTURA-INCOMPLETA" and scan2["no_parseables"],
        f"1 archivo no parseable devolvio status {scan2['status']!r} (se lee como «sin hallazgos»)",
    ))

    # C3 (b): exclusiones solapadas no inflan el denominador. El caso es el de L-VCF-11: dos
    # nombres de exclusion que YA estan en la lista de HEAD anidando el mismo archivo
    # (venv/lib/site-packages/x.py suma en los dos marcadores).
    solapado = tmp / "repo-solapado"
    (solapado / "venv" / "lib" / "site-packages").mkdir(parents=True, exist_ok=True)
    (solapado / "modules").mkdir(parents=True, exist_ok=True)
    (solapado / "venv" / "lib" / "site-packages" / "x.py").write_text(
        "import typesafe\n", encoding="utf-8")
    (solapado / "modules" / "limpio.py").write_text("import json\n", encoding="utf-8")
    puerta_s = solapado / "decision_client.py"
    puerta_s.write_text("import json\n", encoding="utf-8")
    b = mod.escanear_aislamiento(solapado, puerta=puerta_s)["coverage_basis"]
    criterios.append((
        "C3 denominador-unico",
        b["archivos_py_en_el_arbol"] == 3 and b["archivos_escaneados"] == 2,
        f"1 archivo bajo 2 exclusiones solapadas dio arbol={b['archivos_py_en_el_arbol']} "
        f"(2 escaneados + 1 unico esperado): la suma de la atribucion infla el total",
    ))

    # C4 (c): el informe refleja sonda y costura; una sonda caida no deja favorable
    scan_limpio = {"status": "SIN-HALLAZGOS", "hallazgos": [], "hallazgos_carga_dinamica": [],
                   "no_parseables": [],
                   "coverage_basis": {"archivos_escaneados": 10, "archivos_py_en_el_arbol": 10}}
    sonda_caida = {"RESUELTO": {"provider_status": "LECTOR-FALLIDO", "motivo": "roto"},
                   "NO-CONFIGURADO": {"provider_status": "NO-CONFIGURADO"},
                   "ILEGIBLE": {"provider_status": "ILEGIBLE"}}
    costura_ok = {"files_changed_to_add_provider": 1}
    try:
        mod.escanear_aislamiento = lambda *a, **kw: dict(scan_limpio)
        mod.sonda_tres_estados = lambda *a, **kw: {k: dict(v) for k, v in sonda_caida.items()}
        mod.medir_costura = lambda *a, **kw: dict(costura_ok)
        informe = mod.construir_informe(tmp)
        componentes = informe.get("componentes") or {}
        criterios.append((
            "C4 informe-refleja-sonda",
            informe["status"] != "SIN-HALLAZGOS"
            and componentes.get("sonda_tres_estados") == "SONDA-FALLIDA",
            f"sonda caida (RESUELTO->LECTOR-FALLIDO) dejo informe status "
            f"{informe['status']!r} sin 'componentes' que lo expliquen: el informe hereda el "
            f"status del escaneo a secas",
        ))
    finally:
        pass

    # C5 (a, gobernanza): documento vacio no produce favorable ni exit 0
    script_gn = mod_gn.__file__ if getattr(mod_gn, "__file__", None) else str(GN)
    doc_blanco = tmp / "gobierno-en-blanco.md"
    doc_blanco.write_text("", encoding="utf-8")
    fx = _fixture_gn(tmp)
    r = subprocess.run([sys.executable, str(script_gn),
                        "--governance-doc", str(doc_blanco),
                        "--source", str(fx["source"]), "--hook", str(fx["hook"])],
                       capture_output=True, text=True)
    criterios.append((
        "C5 gov-doc-vacio",
        r.returncode == 3 and "LECTOR-FALLIDO" in r.stdout,
        f"documento de gobierno de 0 bytes salio exit {r.returncode} con salida "
        f"{(r.stdout.strip().splitlines() or ['<vacia>'])[0][:80]!r}: poblacion vacia certificada "
        "como favorable",
    ))

    # C6: stdout de --report sin destino es JSON parseable (el aviso va a stderr)
    r2 = subprocess.run([sys.executable, str(script_gn), "--report",
                         "--governance-doc", str(fx["doc"]),
                         "--source", str(fx["source"]), "--hook", str(fx["hook"])],
                        capture_output=True, text=True)
    try:
        datos = json.loads(r2.stdout)
        c6_ok = isinstance(datos, dict) and "no se escribio ningun archivo" in r2.stderr
        c6_causa = "" if c6_ok else "el aviso o la marca de estado contamina stdout, o el JSON no parsea"
    except json.JSONDecodeError as exc:
        c6_ok = False
        c6_causa = f"stdout no es JSON parseable ({exc}): la salida mezcla JSON con relatos"
    criterios.append(("C6 stdout-json-parseable", c6_ok, c6_causa))
    return criterios


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="veredicto-abcd-") as nombre:
        tmp = Path(nombre)
        pre = _version_head(RAIZ, "scripts/decision_client.py", tmp / "decision_client_PRE.py")
        pre_gn = _version_head(RAIZ, "scripts/validate_governance_numbers.py",
                               tmp / "validate_governance_numbers_PRE.py")
        mod_pre = _cargar(pre, "dc_pre_abcd")
        mod_pre_gn = _cargar(pre_gn, "gn_pre_abcd")
        mod_post = _cargar(PUERTA, "dc_post_abcd")
        mod_post_gn = _cargar(GN, "gn_post_abcd")

        print("PRE (HEAD) — criterios del cierre a-d:")
        pre_resultados = _criterios(mod_pre, mod_pre_gn, tmp / "pre")
        for nombre_c, ok, causa in pre_resultados:
            print(f"  {'OK  ' if ok else 'FALLA'} {nombre_c}"
                  + ("" if ok else f" — causa: {causa}"))
        pre_rotos = [n for n, ok, _ in pre_resultados if not ok]
        print(f"PRE: {len(pre_resultados) - len(pre_rotos)}/{len(pre_resultados)} "
              f"(rotos: {', '.join(pre_rotos) or 'ninguno'})")

        print("POST (arbol de trabajo):")
        post_resultados = _criterios(mod_post, mod_post_gn, tmp / "post")
        for nombre_c, ok, causa in post_resultados:
            print(f"  {'OK  ' if ok else 'FALLA'} {nombre_c}"
                  + ("" if ok else f" — causa: {causa}"))
        post_rotos = [n for n, ok, _ in post_resultados if not ok]
        print(f"POST: {len(post_resultados) - len(post_rotos)}/{len(post_resultados)} "
              f"(rotos: {', '.join(post_rotos) or 'ninguno'})")

        faltan_verde = [n for n, ok, _ in post_resultados if not ok]
        if faltan_verde:
            print(f"VEREDICTO: SIN CERRAR — faltan verde en: {', '.join(faltan_verde)}")
            return 1
        print("VEREDICTO: los seis criterios pasan en el arbol de trabajo.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
