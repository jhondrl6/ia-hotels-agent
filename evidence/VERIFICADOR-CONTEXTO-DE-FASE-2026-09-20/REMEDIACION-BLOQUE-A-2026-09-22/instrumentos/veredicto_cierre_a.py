"""Veredicto de cierre del bloque A — criterios a-d completos (sesión 3, 2026-09-22).

Reemplaza a `veredicto_pendientes_abcd.py` (sesión 2), que queda como antecedente con su log. Este
instrumento corrige las tres debilidades que la auditoría le encontró:

  1. **El PRE gatea el exit**: si HEAD sigue en la línea de partida (`a3ab8f9`), TODOS los criterios
     deben ser rojos en PRE; un PRE verde delata un fixture rojo-muerto y el instrumento sale 2.
     Si HEAD ya se movió (commiteado el trabajo), la matriz PRE queda como advertencia y el exit
     responde solo por POST.
  2. **Cada rojo nombra su causa y la causa se COMPRUEBA con un predicado** (sesion 4): cada
     criterio es un predicado que en la revision de partida solo puede romper el defecto que el
     criterio nombra (p. ej. C3 falla porque la suma de la atribucion infla el total), y lleva un
     segundo predicado de **causa esperada** sobre los valores observados. Un rojo en PRE cuya
     firma no coincide con la causa esperada (p. ej. un fixture roto que apaga el escenario del
     criterio) hace el veredicto INSTRUMENTO SOSPECHOSO: contado a mano bastaba para "12/12
     rojos", pero la causa se imprimia sin comprobarse — reproducido en sesion 4 sabotajeando el
     fixture de C9: el instrumento debil certificado "rojo-por-causa" con un escenario que ya no
     existia. Un criterio que cae por una excepcion del propio instrumento se registra como tal,
     no como verde.
  3. **Cubre lo que sesión 2 no tocó**: exits del CLI (no solo estados de función), veredicto de
     costura sin despacho real, informe parcial que conserva hallazgos, conservación parcial en
     gobernanza, y el criterio d (invariantes del mutante sin partición fijada). C11 (sesion 4)
     cubre la poblacion mixta con un documento AUSENTE: analizar los legibles, publicar la causa
     y conservar los hallazgos (exit 3), en lugar de la puerta exit 2 que descartaba hallazgos y
     rompia el JSON por stdout.
  4. **Los predicados de causa se auto-prueban** (sesion 4, tras una auto-auditoria): los 13
     criterios tienen su predicado como **funcion pura de la observacion**, y
     `_auto_test_predicados()` pasa observaciones sinteticas por cada uno: la firma baseline del
     defecto (contra sobre-tightening) y las firmas vecinas — la solucion ya aplicada, el estado
     intermedio y la precondicion del fixture apagada (contra el permiso de sintoma compartido, que
     fue la brecha medida: un `JSONDecodeError` no distingue veredicto mezclado, puerta `AUSENTE`,
     lector caido ni salida vacia). Si un predicado acepta lo que no debe, el veredicto es
     INSTRUMENTO SOSPECHOSO con exit 2: la discriminacion no se deja a la lectura del codigo.

Uso:
    python instrumentos/veredicto_cierre_a.py
Salida: matriz PRE/POST por criterio con causa y comprobacion de causa, mas el auto-test de
predicados; exit 0 = POST verde, PRE rojo-por-causa-comprobada y auto-test OK (o baseline vencida
declarada); 1 = hay rojo en POST; 2 = INSTRUMENTO SOSPECHOSO: PRE no rojo con la baseline intacta,
rojo en PRE por causa no esperada, o un predicado que acepta una observacion de otra causa.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
BASELINE = "a3ab8f9"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
HEAD = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(RAIZ),
                      capture_output=True, text=True).stdout.strip()


def _cargar(ruta: Path, nombre: str):
    spec = importlib.util.spec_from_file_location(nombre, str(ruta))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _extraer_head(rel: str, destino: Path) -> Path:
    texto = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=str(RAIZ),
                           capture_output=True, text=True, check=True,
                           encoding="utf-8", errors="replace").stdout
    destino.write_text(texto, encoding="utf-8", newline="\n")
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

# Las lineas `#   [N/M]` son obligatorias: sin ellas el hook del fixture es ilegitimo para el
# verificador y TODOS los criterios de gobernanza caen por la razon equivocada (error de la
# sesion 2, documentado en 00-resumen-bloque-A.md).
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
DOC_VENCIDO = (
    "**Verificador**: `scripts/validate_alpha.py` es check 7 de `run_all_validations.py --quick`.\n"
    "Beta corre como `[9/9]` de `run_all_validations.py --quick` (`scripts/validate_beta.py`).\n"
)


def _fixture(tmp: Path) -> dict:
    fx = {"tmp": tmp}
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "src.py").write_text(FUENTE, encoding="utf-8")
    (tmp / "hook").write_text(HOOK, encoding="utf-8")
    (tmp / "doc_ok.md").write_text(DOC_OK, encoding="utf-8")
    (tmp / "doc_vencido.md").write_text(DOC_VENCIDO, encoding="utf-8")
    (tmp / "doc_blanco.md").write_text("", encoding="utf-8")
    return fx


def _correr(script: Path, *args: str) -> subprocess.CompletedProcess:
    # utf-8 explicito: los hijos reconfiguran su consola a utf-8 y el default de la plataforma
    # (cp1252) rompe la captura en los guiones largos del informe (medido en esta corrida).
    return subprocess.run([sys.executable, str(script), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def _scan_fake(status: str, **extra) -> dict:
    base = {"status": status, "hallazgos": [], "hallazgos_carga_dinamica": [], "no_parseables": [],
            "conteos": {"coincidencias_de_import_fuera_de_la_puerta": 0,
                        "hallazgos_de_carga_dinamica": 0, "menciones_no_import": 0,
                        "archivos_no_parseables": 0},
            "coverage_basis": {"archivos_escaneados": 0 if status == "SIN-POBLACION" else 700,
                               "nodos_de_import_vistos": 5, "tokens_buscados": ["t"],
                               "excluidos_por_directorio": {},
                               "archivos_py_en_el_arbol": 0}}
    base.update(extra)
    return base


SONDA_OK = {"RESUELTO": {"provider_status": "RESUELTO"},
            "NO-CONFIGURADO": {"provider_status": "NO-CONFIGURADO"},
            "ILEGIBLE": {"provider_status": "ILEGIBLE"}}
COSTURA_CONtrato = {"files_changed_to_add_provider": 1,
                    "provider_status": ["RESUELTO", "RESUELTO"],
                    "costura_funciona_con_ambos": ["falso-forma", "falso-segundo-medido"],
                    "los_dos_despachan_respuestas_distintas": True}


def _criterios_dc(mod, fx: dict, revision: str) -> list:
    """Criterios sobre decision_client. Cada tupla: (id, ok, causa-del-rojo-esperada-en-PRE,
    causa-esperada) — el 4to elemento es un predicado sobre los valores observados que verifica
    que el rojo cayo por la firma del defecto nombrado (solo se evalua en PRE; None en POST)."""
    out = []
    tmp = fx["tmp"] / revision
    tmp.mkdir(parents=True, exist_ok=True)
    orig = {n: getattr(mod, n) for n in ("escanear_aislamiento", "sonda_tres_estados",
                                         "medir_costura", "construir_informe")}

    def restaurar():
        for n, v in orig.items():
            setattr(mod, n, v)

    try:
        # C1 (a): poblacion vacia — estado propio Y exit del CLI no favorable.
        # El estado de la FUNCION se prueba sobre un arbol real vacio; el exit del CLI no puede
        # probarse contra ese arbol (main escanea la raiz del repo, que no esta vacia), asi que se
        # le inyecta el mismo estado: lo que se demonstra aqui es el ALAMBRE status->exit, y el
        # estado por poblacion vacia lo demuestra C1a.
        vacio = tmp / "arbol-vacio"
        vacio.mkdir(exist_ok=True)
        scan = mod.escanear_aislamiento(vacio, puerta=vacio / "decision_client.py")
        out.append(("C1a SIN-POBLACION", scan["status"] == "SIN-POBLACION",
                    "arbol vacio devolvio " + repr(scan["status"]),
                    _causa_esperada_c1a(scan)))
        scan_fake = _scan_fake("SIN-POBLACION")
        mod.escanear_aislamiento = lambda *a, **kw: dict(scan_fake)
        capturado = io.StringIO()
        with contextlib.redirect_stdout(capturado), contextlib.redirect_stderr(io.StringIO()):
            code = mod.main(["--scan-imports"])
        out.append(("C1b wiring-exit-vacía", scan["status"] != "SIN-HALLAZGOS" and code != 0,
                    f"CLI salio {code} con estado {scan['status']!r}",
                    _causa_esperada_c1b(code, scan)))
        mod.escanear_aislamiento = orig["escanear_aislamiento"]

        # C2 (a): lectura incompleta — estado propio Y exit no favorable.
        roto = tmp / "repo-roto"
        (roto / "modules").mkdir(parents=True, exist_ok=True)
        (roto / "modules" / "roto.py").write_text("def x(\n", encoding="utf-8")
        (roto / "decision_client.py").write_text("import json\n", encoding="utf-8")
        scan2 = mod.escanear_aislamiento(roto, puerta=roto / "decision_client.py")
        out.append(("C2 LECTURA-INCOMPLETA",
                    scan2["status"] == "LECTURA-INCOMPLETA" and bool(scan2["no_parseables"]),
                    f"1 no parseable dio status {scan2['status']!r} "
                    f"(causas conservadas: {len(scan2['no_parseables'])})",
                    _causa_esperada_c2(scan2)))
        mod.escanear_aislamiento = lambda *a, **kw: _scan_fake("LECTURA-INCOMPLETA",
                                                               no_parseables=[{"archivo": "x"}])
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code2 = mod.main(["--scan-imports"])
        out.append(("C2b wiring-exit-incompleta", code2 != 0,
                    f"CLI salio {code2} con lectura incompleta declarada",
                    _causa_esperada_c2b(code2)))
        mod.escanear_aislamiento = orig["escanear_aislamiento"]

        # C3 (b): solape de exclusiones no infla; se publica el conteo unico.
        sol = tmp / "repo-solapado"
        (sol / "venv" / "lib" / "site-packages").mkdir(parents=True, exist_ok=True)
        (sol / "modules").mkdir(parents=True, exist_ok=True)
        (sol / "venv" / "lib" / "site-packages" / "x.py").write_text("pass\n", encoding="utf-8")
        (sol / "modules" / "a.py").write_text("import json\n", encoding="utf-8")
        (sol / "decision_client.py").write_text("import json\n", encoding="utf-8")
        b = mod.escanear_aislamiento(sol, puerta=sol / "decision_client.py")["coverage_basis"]
        out.append(("C3 denominador-unico",
                    b["archivos_py_en_el_arbol"] == 3 and b.get("excluidos_archivos_unicos") == 1,
                    f"arbol={b['archivos_py_en_el_arbol']} unicos={b.get('excluidos_archivos_unicos')}"
                    " (esperado 3 y 1; la suma de la atribucion infla)",
                    _causa_esperada_c3(b)))

        # C4 (c): sonda caida degrada el informe y se nombra en componentes.
        mod.escanear_aislamiento = lambda *a, **kw: _scan_fake("SIN-HALLAZGOS")
        mod.sonda_tres_estados = lambda *a, **kw: {**{k: dict(v) for k, v in SONDA_OK.items()},
                                                   "RESUELTO": {"provider_status":
                                                                "LECTOR-FALLIDO"}}
        mod.medir_costura = lambda *a, **kw: dict(COSTURA_CONtrato)
        inf = mod.construir_informe(tmp)
        ok4 = (inf.get("status") != "SIN-HALLAZGOS"
               and (inf.get("componentes") or {}).get("sonda_tres_estados") == "SONDA-FALLIDA")
        out.append(("C4 sonda-caida-degrada", ok4,
                    f"informe {inf.get('status')!r} componentes={inf.get('componentes')!r} "
                    "(sonda LECTOR-FALLIDO donde se esperaba RESUELTO)",
                    _causa_esperada_c4(inf)))

        # C5 (c): el «1» de costura sin despacho real no es OK, ni en el informe ni en el CLI.
        mod.sonda_tres_estados = lambda *a, **kw: {k: dict(v) for k, v in SONDA_OK.items()}
        mod.medir_costura = lambda *a, **kw: {**COSTURA_CONtrato,
                                              "provider_status": ["ILEGIBLE", "RESUELTO"]}
        inf = mod.construir_informe(tmp)
        ok5 = (inf.get("status") != "SIN-HALLAZGOS"
               and (inf.get("componentes") or {}).get("costura") == "FALLIDA")
        capturado = io.StringIO()
        with contextlib.redirect_stdout(capturado), contextlib.redirect_stderr(io.StringIO()):
            code5 = mod.main(["--costura"])
        out.append(("C5 costura-1-sin-despacho", ok5 and code5 != 0,
                    f"informe {inf.get('status')!r}, --costura exit {code5}: el 1 de archivos "
                    "contaba una frontera que no resolvio a los dos proveedores",
                    _causa_esperada_c5(inf, code5)))

        # C6 (a/c): informe PARCIAL — la ruta ausente no borra el hallazgo del escaneo.
        mod.escanear_aislamiento = lambda *a, **kw: _scan_fake(
            "HALLAZGOS", hallazgos=[{"archivo": "modules/fuga.py", "import": "typesafe"}],
            coverage_basis={"archivos_escaneados": 1, "archivos_py_en_el_arbol": 1,
                            "nodos_de_import_vistos": 1, "tokens_buscados": ["t"]})
        mod.sonda_tres_estados = lambda *a, **kw: {k: dict(v) for k, v in SONDA_OK.items()}

        def costura_ausente(*a, **kw):
            raise mod.Ausente("directorio de proveedores falsos no existe: Z")

        mod.medir_costura = costura_ausente
        destino = tmp / "informe-parcial.json"
        exc6 = None
        try:
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                code6 = mod.main(["--report", str(destino),
                                  "--falsos-directorio", str(tmp / "no-existe")])
            datos = json.loads(destino.read_text(encoding="utf-8")) if destino.exists() else {}
            conservado = any("fuga.py" in h.get("archivo", "")
                             for h in (datos.get("aislamiento_imports") or {}).get("hallazgos", []))
            fallos = {f.get("componente"): f.get("estado")
                      for f in datos.get("fallos_de_componentes", [])}
            ok6 = code6 == 2 and conservado and datos.get("status") != "SIN-HALLAZGOS" \
                and fallos.get("costura") == "AUSENTE"
            causa6 = (f"exit {code6}, hallazgo conservado={conservado}, status="
                      f"{datos.get('status')!r}, fallos={fallos!r}")
            # el informe NO murio: en PRE eso significaria que la causa ya no es la nombrada
            causa_pre6 = _causa_esperada_c6(None, getattr(mod, "Ausente", None))
        except Exception as e6:
            exc6 = e6
            ok6 = False
            causa6 = f"el informe murio con la componente ausente: {type(exc6).__name__}: {exc6} " \
                     "(stdout sin informe parcial)"
            causa_pre6 = _causa_esperada_c6(exc6, getattr(mod, "Ausente", None))
        out.append(("C6 parcial-conserva-hallazgos", ok6, causa6, causa_pre6))
    finally:
        restaurar()
    return out


# Predicados de causa esperada, UNO POR CRITERIO, como funciones puras de la observacion.
# Cada uno describe la firma POSITIVA del defecto que el criterio nombra (no la ausencia de la
# solucion) y rechaza las firmas vecinas: las causas con las que el rojo podria confundirse.
# `_auto_test_predicados()` pasa observaciones sinteticas por los 13 y gatea el veredicto, de modo
# que "cada rojo comprueba su causa" es medicion del instrumento, no lectura confiable del codigo.
def _causa_esperada_c1a(scan) -> bool:
    """Defecto nombrado: poblacion vacia saldaba favorable. Otra firma (estados intermedios de la
    solucion, lectura incompleta) no es el defecto de C1a."""
    return scan["status"] == "SIN-HALLAZGOS"


def _causa_esperada_c1b(code: int, scan) -> bool:
    """Defecto: el alambre estado->exit no respondia (exit 0) con estado favorable por defecto."""
    return code == 0 and scan["status"] == "SIN-HALLAZGOS"


def _causa_esperada_c2(scan2) -> bool:
    """Defecto: 1 archivo no parseable saldaba favorable CON las causas ya colectadas."""
    return scan2["status"] == "SIN-HALLAZGOS" and len(scan2["no_parseables"]) == 1


def _causa_esperada_c2b(code2: int) -> bool:
    return code2 == 0


def _causa_esperada_c3(b: dict) -> bool:
    """Defecto: la suma de la atribucion inflaba el denominador (3 + 1 = 4) y no habia conteo
    unico. Un denominador correcto sin atribucion es OTRA falla, no la que nombra C3."""
    return b["archivos_py_en_el_arbol"] == 4 and b.get("excluidos_archivos_unicos") is None


def _causa_esperada_c4(inf: dict) -> bool:
    """Defecto: sonda caida no degradaba el informe y el componente ni se publicaba."""
    return (inf.get("status") == "SIN-HALLAZGOS"
            and "sonda_tres_estados" not in (inf.get("componentes") or {}))


def _causa_esperada_c5(inf: dict, code5: int) -> bool:
    """Defecto: la costura saldaba favorable Y el CLI salia 0 contando archivos, no despachos."""
    return inf.get("status") == "SIN-HALLAZGOS" and code5 == 0


def _causa_esperada_c6(exc, Ausente) -> bool:
    """Defecto: la componente ausente mataba el informe con `Ausente` (sin informe parcial).
    Otra excepcion es un instrumento caido por otra via, no la causa de C6."""
    return exc is not None and Ausente is not None and isinstance(exc, Ausente)


def _causa_esperada_c8(precond_vacio: bool, r) -> bool:
    """Defecto: documento VACIO (precondicion del fixture) saldaba favorable con exit 0.
    Sin documento en blanco el criterio no prueba su escenario: rojo del instrumento."""
    return bool(precond_vacio) and r.returncode == 0 and "SIN-HALLAZGOS" in r.stdout


def _causa_esperada_c9(precond_blanco: bool, r, destino_existe: bool, datos) -> bool:
    """Firma PRE medida: sin concepto de lectura parcial, los dos documentos legibles daban 1,
    destino escrito y status HALLAZGOS con los hallazgos del vencido."""
    return (bool(precond_blanco) and r.returncode == 1 and destino_existe
            and isinstance(datos, dict) and datos.get("status") == "HALLAZGOS"
            and len(datos.get("findings") or []) >= 1)


def _causa_esperada_c10(invariantes_ok: bool, forcing: bool) -> bool:
    """Defecto: el test de invariantes se enteraba de la particion. Vale solo si ademas el guard
    extra exigia su payload propio; sin eso el rojo diria que el guard es un duplicado roto."""
    return (not invariantes_ok) and forcing


# Predicados de causa para los caminos `except`. Un `JSONDecodeError` es un SINTOMA comun a varias
# causas (el veredicto mezclado con el informe, la puerta AUSENTE, el lector caido, la salida
# vacia), asi que ninguno de estos predicados puede aceptar la excepcion como prueba: cada uno
# exige la firma POSITIVA del defecto nombrado y rechaza las firmas de las otras causas.
# Brecha medida en la auditoria de la sesion 4: el predicado C7 de la primera version aceptaba
# cualquier JSONDecodeError, y una observacion sintetica con exit 2 + `[AUSENTE]` (puerta del
# verificador, otra causa) pasaba como "su causa". El auto-test `_auto_test_predicados()` fija
# esa discriminacion con observaciones sinteticas y gatea el veredicto.
def _causa_esperada_c7(r) -> bool:
    """PRE esperado de C7: el verificador OPERO (exit 0/1 del veredicto) y stdout trajo el
    resumen humano mezclado, no JSON puro. `--report` sin destino en la baseline imprimio
    `[SIN-HALLAZGOS] ...` (medido: JSONDecodeError en la columna 2 de esa linea). Exit 2/3 con
    puerta `[AUSENTE]`/`[LECTOR-FALLIDO]` o stdout vacio son otras causas, no la de C7.
    Frontera del accept-set: basta con la palabra SIN-HALLAZGOS/HALLAZGOS sin corchetes porque la
    familia «palabra suelta sin marca bracketeada» es inalcanzable en la revision congelada — el
    codigo de PRE imprime la marca bracketeada en TODOS los caminos que producen stdout
    (`if not args.quiet`, verificado leyendo `git show a3ab8f9:...`)."""
    if r.returncode not in (0, 1):
        return False
    if "[AUSENTE]" in r.stdout or "[LECTOR-FALLIDO]" in r.stdout:
        return False
    return ("SIN-HALLAZGOS" in r.stdout or "HALLAZGOS" in r.stdout)


def _causa_esperada_c11(r, fx: dict) -> bool:
    """PRE esperado de C11: con la fuente, el hook y el documento legible PRESENTES, el exit 2
    menciona como ausente la ruta del documento (la puerta previa), no otra. Si falta una fuente,
    el mismo exit 2 es causa distinta (verificador sin reglas) y el predicado rechaza."""
    if r.returncode != 2 or "AUSENTE" not in r.stdout:
        return False
    for nombre in ("src.py", "hook", "doc_vencido.md"):
        if not (fx["tmp"] / nombre).exists():
            return False
    return str(fx["tmp"] / "no-existe-en-fixture.md") in r.stdout


def _auto_test_predicados(fx: dict, Ausente=None) -> tuple:
    """Discriminacion de los 13 predicados de causa, probada con observaciones sinteticas.
    Por cada predicado se mide la ACEPTACION de la firma baseline (contra sobre-tightening) y el
    RECHAZO de las firmas vecinas: la solucion ya aplicada, el estado intermedio, y la precondicion
    del fixture apagada. Un solo caso fallido hace el veredicto INSTRUMENTO SOSPECHOSO."""
    import subprocess

    def rp(code, out=""):
        return subprocess.CompletedProcess([], code, out, "")

    fav = {"status": "SIN-HALLAZGOS", "no_parseables": []}
    fix_vac = {"status": "SIN-POBLACION", "no_parseables": []}
    li = {"status": "LECTURA-INCOMPLETA", "no_parseables": [{"archivo": "x"}]}
    s1 = {"status": "SIN-HALLAZGOS", "no_parseables": [{"archivo": "x"}]}
    sol_aplicada = {"status": "LECTURA-INCOMPLETA", "no_parseables": [{"a": 1}]}
    b_bad = {"archivos_py_en_el_arbol": 4, "excluidos_archivos_unicos": None}
    b_ok = {"archivos_py_en_el_arbol": 3, "excluidos_archivos_unicos": 1}
    b_sin_atrib = {"archivos_py_en_el_arbol": 3, "excluidos_archivos_unicos": None}
    b_otros = {"archivos_py_en_el_arbol": 4, "excluidos_archivos_unicos": 2}
    i_bad = {"status": "SIN-HALLAZGOS"}
    i_fix = {"status": "SIN-HALLAZGOS", "componentes": {"sonda_tres_estados": "SONDA-FALLIDA"}}
    i_hall = {"status": "HALLAZGOS"}
    hall = {"status": "HALLAZGOS", "findings": [{"a": 1}]}
    lf = {"status": "LECTOR-FALLIDO", "findings": [{"a": 1}]}

    # --- caminos `except` (C7, C11): sintomas compartidos entre varias causas ------------------
    puerta = rp(2, "[AUSENTE] no se encontro la ruta buscada:\n  - C:\\otra-ruta\n")
    caido = rp(3, "[LECTOR-FALLIDO] no pudo operar:\n  motivo: lectura\n")
    firma_c7 = rp(0, "[SIN-HALLAZGOS] validate_governance_numbers.py - aserciones de conteo\n")
    hall_c7 = rp(1, "[HALLAZGOS] validate_governance_numbers.py\n")
    doc_ausente = str(fx["tmp"] / "no-existe-en-fixture.md")
    c11_ok = rp(2, f"[AUSENTE] no se encontro la ruta buscada:\n  - {doc_ausente}\n")
    fx_sin = {"tmp": Path(str(fx["tmp"]) + "-sin-fuentes")}
    c11_sin_fuentes = rp(2, "[AUSENTE] no se encontro la ruta buscada:\n  - "
                            f"{str(fx_sin['tmp'] / 'no-existe-en-fixture.md')}\n")

    casos = [
        # C7
        ("C7 acepta la firma baseline favorable", _causa_esperada_c7(firma_c7)),
        ("C7 acepta la firma baseline con hallazgos", _causa_esperada_c7(hall_c7)),
        ("C7 rechaza la puerta AUSENTE", not _causa_esperada_c7(puerta)),
        ("C7 rechaza el lector caido", not _causa_esperada_c7(caido)),
        ("C7 rechaza stdout vacio", not _causa_esperada_c7(rp(0, ""))),
        # C11
        ("C11 acepta exit 2 que nombra el doc con fuentes intactas",
         _causa_esperada_c11(c11_ok, fx)),
        ("C11 rechaza la misma firma sin la precondicion de fuentes",
         not _causa_esperada_c11(c11_sin_fuentes, fx_sin)),
        ("C11 rechaza exit 3 (verificador ya operando en parcial)",
         not _causa_esperada_c11(rp(3, "{}"), fx)),
        # C1a / C1b
        ("C1a acepta el favorable baseline", _causa_esperada_c1a(fav)),
        ("C1a rechaza la solucion ya aplicada", not _causa_esperada_c1a(fix_vac)),
        ("C1a rechaza lectura incompleta (otro defecto)", not _causa_esperada_c1a(li)),
        ("C1b acepta exit 0 con estado favorable", _causa_esperada_c1b(0, fav)),
        ("C1b rechaza exit 1 (el alambre si respondio)", not _causa_esperada_c1b(1, fav)),
        ("C1b rechaza exit 0 con estado no favorable", not _causa_esperada_c1b(0, li)),
        # C2 / C2b
        ("C2 acepta favorable con 1 causa conservada", _causa_esperada_c2(s1)),
        ("C2 rechaza la solucion ya aplicada", not _causa_esperada_c2(sol_aplicada)),
        ("C2 rechaza favorable sin causas", not _causa_esperada_c2({"status": "SIN-HALLAZGOS",
                                                                    "no_parseables": []})),
        ("C2b acepta exit 0", _causa_esperada_c2b(0)),
        ("C2b rechaza exit 1", not _causa_esperada_c2b(1)),
        # C3
        ("C3 acepta denominador inflado sin atribucion", _causa_esperada_c3(b_bad)),
        ("C3 rechaza la solucion ya aplicada", not _causa_esperada_c3(b_ok)),
        ("C3 rechaza denominador correcto sin atribucion", not _causa_esperada_c3(b_sin_atrib)),
        ("C3 rechaza inflado CON atribucion", not _causa_esperada_c3(b_otros)),
        # C4 / C5
        ("C4 acepta informe favorable sin el componente", _causa_esperada_c4(i_bad)),
        ("C4 rechaza el componente ya publicado", not _causa_esperada_c4(i_fix)),
        ("C4 rechaza informe con hallazgos", not _causa_esperada_c4(i_hall)),
        ("C5 acepta favorable con exit 0", _causa_esperada_c5(i_bad, 0)),
        ("C5 rechaza exit 1 (el CLI ya respondio)", not _causa_esperada_c5(i_bad, 1)),
        ("C5 rechaza otro estado de informe", not _causa_esperada_c5(i_hall, 0)),
        # C6
        ("C6 acepta la componente ausente que mata el informe",
         _causa_esperada_c6(Ausente("z") if Ausente else None, Ausente)),
        ("C6 rechaza otra excepcion", not _causa_esperada_c6(TypeError("z"), Ausente)),
        ("C6 rechaza ausencia de excepcion", not _causa_esperada_c6(None, Ausente)),
        # C8 / C9
        ("C8 acepta favorable sobre doc en blanco",
         _causa_esperada_c8(True, rp(0, "[SIN-HALLAZGOS] ...\n"))),
        ("C8 rechaza sin la precondicion de blancura",
         not _causa_esperada_c8(False, rp(0, "[SIN-HALLAZGOS] ...\n"))),
        ("C8 rechaza la solucion ya aplicada",
         not _causa_esperada_c8(True, rp(3, "[LECTOR-FALLIDO] ...\n"))),
        ("C8 rechaza exit 1 con hallazgos",
         not _causa_esperada_c8(True, rp(1, "[HALLAZGOS] ...\n"))),
        ("C9 acepta exit 1 con destino y HALLAZGOS", _causa_esperada_c9(True, rp(1), True, hall)),
        ("C9 rechaza sin la precondicion de blancura",
         not _causa_esperada_c9(False, rp(1), True, hall)),
        ("C9 rechaza la solucion ya aplicada (exit 3, sin destino)",
         not _causa_esperada_c9(True, rp(3), False, lf)),
        ("C9 rechaza exit 1 con informe parcial", not _causa_esperada_c9(True, rp(1), True, lf)),
        # C10
        ("C10 acepta invariantes enterados y guard legitimo", _causa_esperada_c10(False, True)),
        ("C10 rechaza invariantes ajenos a la particion", not _causa_esperada_c10(True, True)),
        ("C10 rechaza guard sin payload propio", not _causa_esperada_c10(False, False)),
    ]
    if Ausente is None:
        casos = [c for c in casos if not c[0].startswith("C6")]
    fallidos = [nombre for nombre, ok in casos if not ok]
    return not fallidos, f"{len(casos)} casos; fallidos: " + ("; ".join(fallidos) or "ninguno")


def _criterios_gn(script: Path, fx: dict) -> list:
    """Criterios sobre validate_governance_numbers, todos por subprocess con salidas reales.
    Tuplas de 4: (id, ok, causa, causa-esperada) — el 4to verifica la firma POSITIVA del defecto
    nombrado sobre lo observado (incluida la precondicion del fixture) y solo gobierna en PRE."""
    src, hook = str(fx["tmp"] / "src.py"), str(fx["tmp"] / "hook")
    out = []

    # C7: `--report` sin destino = stdout JSON puro + aviso a stderr + exit del veredicto.
    r = _correr(script, "--report", "--governance-doc", str(fx["tmp"] / "doc_ok.md"),
                "--source", src, "--hook", hook)
    try:
        datos = json.loads(r.stdout)
        ok7 = (isinstance(datos, dict) and "no se escribio ningun archivo" in r.stderr
               and r.returncode == (1 if datos.get("findings") else 0))
        causa7 = f"returncode {r.returncode}, JSON={isinstance(datos, dict)}"
        causa_pre7 = False  # un stdout parseable en PRE ya no seria la causa esperada
    except json.JSONDecodeError as exc:
        ok7 = False
        causa7 = f"stdout no es JSON puro ({exc}): el veredicto/aviso se mezcla con el informe"
        causa_pre7 = _causa_esperada_c7(r)
    out.append(("C7 stdout-json-puro", ok7, causa7, causa_pre7))

    # C8 (a): documento de gobierno vacio -> LECTOR-FALLIDO exit 3 con la causa nombrada.
    # La causa esperada incluye la precondicion del fixture (el doc DEBE estar en blanco): con un
    # fixture que ya no instancia el escenario, el rojo seria del instrumento, no del defecto.
    precond_vacio = not (fx["tmp"] / "doc_blanco.md").read_text(encoding="utf-8").strip()
    r = _correr(script, "--governance-doc", str(fx["tmp"] / "doc_blanco.md"),
                "--source", src, "--hook", hook)
    ok8 = r.returncode == 3 and "LECTOR-FALLIDO" in r.stdout and "vacio" in r.stdout \
        and "SIN-HALLAZGOS" not in r.stdout
    out.append(("C8 gov-doc-vacio", ok8,
                f"exit {r.returncode} primera-linea "
                f"{(r.stdout.strip().splitlines() or ['<vacia>'])[0][:90]!r}",
                _causa_esperada_c8(precond_vacio, r)))

    # C9: lectura incompleta NO borra los hallazgos del otro documento; destino no escrito.
    destino = fx["tmp"] / "no-debe-existir.json"
    precond_blanco = not (fx["tmp"] / "doc_blanco.md").read_text(encoding="utf-8").strip()
    r = _correr(script, "--governance-doc", str(fx["tmp"] / "doc_vencido.md"),
                "--governance-doc", str(fx["tmp"] / "doc_blanco.md"),
                "--source", src, "--hook", hook, "--report", str(destino))
    try:
        j = _correr(script, "--governance-doc", str(fx["tmp"] / "doc_vencido.md"),
                    "--governance-doc", str(fx["tmp"] / "doc_blanco.md"),
                    "--source", src, "--hook", hook, "--json")
        datos = json.loads(j.stdout)
        ok9 = (r.returncode == 3 and not destino.exists()
               and j.returncode == 3 and datos.get("status") == "LECTOR-FALLIDO"
               and len(datos.get("findings") or []) >= 1
               and any("vacio" in f.get("motivo", "")
                       for f in datos.get("fallos_de_lectura", [])))
        causa9 = (f"exit {r.returncode}, destino-escrito={destino.exists()}, "
                  f"status={datos.get('status')!r}, hallazgos-conservados="
                  f"{len(datos.get('findings') or [])}")
        # Firma PRE medida (cierre-a-antes-despues.txt): sin concepto de lectura parcial, el
        # script viejo respondio 1/HALLAZGOS con destino escrito, ignorando el doc en blanco.
        causa_pre9 = _causa_esperada_c9(precond_blanco, r, destino.exists(), datos)
    except json.JSONDecodeError as exc:
        ok9 = False
        causa9 = f"stdout --json no parseable ({exc}): el fallo parcial perdio los hallazgos"
        causa_pre9 = False
    out.append(("C9 gov-parcial-conserva", ok9, causa9, causa_pre9))

    # C11 (sesion 4): el AUSENTE de un documento en poblacion mixta deja de ser una puerta previa
    # que descartaba los hallazgos del legible y rompia el JSON (exit 2, stdout en prosa); ahora
    # analizar() trata la ausencia como incompletitud (§4.A-a): exit 3, hallazgos conservados y
    # la causa publicada en fallos_de_lectura.
    r = _correr(script, "--governance-doc", str(fx["tmp"] / "doc_vencido.md"),
                "--governance-doc", str(fx["tmp"] / "no-existe-en-fixture.md"),
                "--source", src, "--hook", hook, "--json")
    try:
        datos = json.loads(r.stdout)
        ok11 = (r.returncode == 3 and datos.get("status") == "LECTOR-FALLIDO"
                and len(datos.get("findings") or []) >= 1
                and any("no existe" in f.get("motivo", "")
                        for f in datos.get("fallos_de_lectura", [])))
        causa11 = (f"exit {r.returncode}, status={datos.get('status')!r}, hallazgos-conservados="
                   f"{len(datos.get('findings') or [])}")
        causa_pre11 = False
    except json.JSONDecodeError:
        ok11 = False
        causa11 = (f"exit {r.returncode} con stdout no parseable: la ruta ausente descarto "
                   "los hallazgos del documento legible")
        causa_pre11 = _causa_esperada_c11(r, fx)
    out.append(("C11 ausente-mixto-conserva", ok11, causa11, causa_pre11))
    return out


def _criterio_d(path_tests: Path, mod_dc, fx: dict) -> tuple:
    """d: las invariantes del mutante no fijan la particion; el guard extra cae por la funcion de
    payloads (precio contractual), no por una conta."""
    mod_t = _cargar(path_tests, f"mutantes_{fx['tag']}")
    original = tuple(mod_dc.VERIFICACIONES_DE_FORMA)
    mod_dc.VERIFICACIONES_DE_FORMA = original + (("forma-extra", original[0][1]),)
    try:
        try:
            mod_t.test_cada_mutante_apunta_a_un_simbolo_distinto_y_vigente(mod_dc)
            invariantes_ok = True
            causa = ""
        except AssertionError as exc:
            invariantes_ok = False
            causa = f"el test de invariantes se entero de la particion: {exc}"
        try:
            mod_t._payload_que_solo_ve("forma-extra")
            forcing = False
            causa = (causa or "") + " | el guard extra no exigio payload propio (particion libre)"
        except AssertionError:
            forcing = True
        # PRE esperado: el test de invariantes detecta al guard extra (rojo por su causa) Y el
        # guard extra exige su propio payload (es un guard legitimo, no un duplicado roto).
        return invariantes_ok and forcing, causa, _causa_esperada_c10(invariantes_ok, forcing)
    finally:
        mod_dc.VERIFICACIONES_DE_FORMA = original


def main() -> int:
    lineas = [f"instrumento: veredicto_cierre_a.py | HEAD={HEAD} baseline={BASELINE} | "
              f"python={sys.version.split()[0]}"]
    with tempfile.TemporaryDirectory(prefix="veredicto-cierre-a-") as nombre:
        tmp = Path(nombre)
        pre_dc = _extraer_head("scripts/decision_client.py", tmp / "decision_client_PRE.py")
        pre_gn = _extraer_head("scripts/validate_governance_numbers.py",
                               tmp / "validate_governance_numbers_PRE.py")
        pre_tests = _extraer_head("tests/quality_gates/decision_client/"
                                  "test_decision_client_mutation_guards.py",
                                  tmp / "mutation_guards_PRE.py")
        fx_pre = _fixture(tmp / "pre")
        fx_pre["tag"] = "pre"
        fx_post = _fixture(tmp / "post")
        fx_post["tag"] = "post"

        mod_pre = _cargar(pre_dc, "dc_pre")
        mod_post = _cargar(RAIZ / "scripts/decision_client.py", "dc_post")

        res_pre = (_criterios_dc(mod_pre, fx_pre, "pre")
                   + _criterios_gn(pre_gn, fx_pre)
                   + [("C10 mutantes-sin-particion", *_criterio_d(pre_tests, mod_pre, fx_pre))])
        res_post = (_criterios_dc(mod_post, fx_post, "post")
                    + _criterios_gn(RAIZ / "scripts/validate_governance_numbers.py", fx_post)
                    + [("C10 mutantes-sin-particion",
                        *_criterio_d(RAIZ / "tests/quality_gates/decision_client/"
                                           "test_decision_client_mutation_guards.py",
                                     mod_post, fx_post))])
        auto_ok, auto_detalle = _auto_test_predicados(fx_post, getattr(mod_post, "Ausente", None))

    baseline_intacta = HEAD == BASELINE
    rojos_pre = [n for n, ok, _, _ in res_pre if not ok]
    verdes_post = [n for n, ok, _, _ in res_post if ok]
    rojos_post = [(n, c) for n, ok, c, _ in res_post if not ok]
    causas_equivocadas = [(n, c) for n, ok, c, cp in res_pre if not ok and cp is not True]
    lineas.append("PRE (revision de la linea de partida):")
    for n, ok, causa, cp in res_pre:
        if ok:
            lineas.append(f"  OK   {n}")
            continue
        marca = "?" if cp is None else ("OK" if cp else "NO")
        lineas.append(f"  FALLA {n}" + (f" — causa: {causa}" if causa else "")
                      + f" | causa-esperada: {marca}")
    lineas.append("POST (arbol de trabajo):")
    for n, ok, causa, _ in res_post:
        lineas.append(f"  {'OK  ' if ok else 'FALLA'} {n}" + ("" if ok else f" — causa: {causa}"))
    n_total = len(res_post)
    lineas.append(f"PRE rojos: {len(rojos_pre)}/{n_total} | POST verdes: {len(verdes_post)}/"
                  f"{n_total} | rojos-PRE-con-causa-comprobada: "
                  f"{sum(1 for _, ok, _, cp in res_pre if not ok and cp is True)}/{len(rojos_pre)}")
    lineas.append(f"auto-test de predicados (observaciones sinteticas de otras causas): "
                  + ("OK" if auto_ok else f"FALLA — {auto_detalle}"))
    if not auto_ok:
        lineas.append("VEREDICTO: INSTRUMENTO SOSPECHOSO — un predicado de causa acepto una "
                      "observacion de otra causa; la matriz PRE/POST no es fiable hasta "
                      "corregirlo (la discriminacion se prueba con el auto-test, no con la "
                      "confianza en el lectura-del-codigo).")
        print("\n".join(lineas))
        return 2
    if rojos_post:
        lineas.append("VEREDICTO: SIN CERRAR — rojos en POST: "
                      + ", ".join(n for n, _ in rojos_post))
        print("\n".join(lineas))
        return 1
    if baseline_intacta and len(rojos_pre) != n_total:
        lineas.append("VEREDICTO: INSTRUMENTO SOSPECHOSO — con la baseline intacta todo PRE deberia "
                      "estar rojo; hay verdes en PRE que no se explican (fixture o criterio roto).")
        print("\n".join(lineas))
        return 2
    if baseline_intacta and causas_equivocadas:
        lineas.append("VEREDICTO: INSTRUMENTO SOSPECHOSO — criterios rojos en PRE por una causa "
                      "distinta de la esperada (el criterio ya no prueba el defecto que nombra, o "
                      "el fixture dejo de instanciar su escenario): "
                      + ", ".join(n for n, _ in causas_equivocadas))
        print("\n".join(lineas))
        return 2
    if not baseline_intacta:
        lineas.append(f"ADVERTENCIA: HEAD={HEAD} ya no es la baseline {BASELINE}; la matriz PRE es "
                      "informativa (el log de la corrida original es el registro), el exit "
                      "responde por POST.")
        if causas_equivocadas:
            lineas.append("NOTA: con la baseline movida hay rojos en PRE por causa no esperada: "
                          + ", ".join(n for n, _ in causas_equivocadas))
    lineas.append(f"VEREDICTO: los {n_total} criterios pasan en el arbol de trabajo"
                  + (" y todos cayeron en PRE por la causa esperada, comprobada con predicado."
                     if baseline_intacta else "."))
    print("\n".join(lineas))
    return 0


if __name__ == "__main__":
    sys.exit(main())
