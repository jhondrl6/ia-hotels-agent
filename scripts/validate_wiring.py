#!/usr/bin/env python3
"""Verificador AST de cableado de senales requeridas (FASE-G, AC7 + AC16).

QUE MEDIDA LO ORIGINA (recidiva, no diseno)
    `PainSolutionMapper.detect_pains` y `CoherenceValidator.validate` declaran
    `whatsapp_html_detected: bool = **False**`. Un caller que lo omita no rompe nada:
    recibe el default y **cambia de conducta en silencio**. La divergencia esta en el
    maestro §1 (fila F-A'), ratificada por FASE-A (decicion n.º 3): `run_v4_complete_mode`
    y `V4DiagnosticGenerator._identify_brechas` propagan la senal;
    `V4AssetOrchestrator.generate_assets` no. Con campo UNKNOWN/CONFLICT + HTML presente,
    la ruta del orquestador emite el pain `no_whatsapp_visible` que las otras dos no
    emiten. Es la tercera vez que el repo pierde un cable asi (`L-NC6`, DT4-R2, y ahora
    esta), y las dos anteriores se detectaron **a posteriori**, leyendo un output.

POR QUE UN VERIFICADOR Y NO UN TEST POR CALLER
    El objetivo es estructural: que omitir una senal necesaria sea detectable por un
    verificador, no por un test escrito a mano para cada caller. Un test por caller
    gobierna el caller que su autor recordo; el vacio que produce el defecto es
    justamente el caller que nadie recordo. Por eso la poblacion se **descubre por AST**
    sobre el arbol, sin lista fija de archivos: un archivo nuevo con un caller que omita
    la senal cae en la poblacion sin que nadie la registre.

COMO DECIDE QUIEN ESTA GOBERNADO (gobernar por productor, no por simbolo)
    `validate` es nombre comun en este repo (`PrecisionValidator`, `NoDefaultsValidator`,
    `EnvValidator`, `plan_validator`, `content_validator`). Gobernar por nombre de metodo
    seria un falso verde colectivo. Cada llamada resuelve el **tipo del receptor**
    (constructor en linea, asignacion/anotacion en el ambito, `self.attr` desde su clase,
    parametro anotado) y solo se gobierna si el tipo resuelto esta en `GOBERNADOS`. Lo no
    resoluble **se cuenta y se publica**, no se descarta en silencio.

PROHIBIDO AUTO-ARREGLAR. Este script **reporta**; no reescribe callers. Insertar el kwarg
    que falta le toca a la fase duena de la fila F-A' (FASE-B), no a un verificador.

LIMITE DECLARADO (L-R.4: una regla sin verificador declara su limite)
    El AST no ve dispatch dinamico (`getattr(obj, nombre)(...)`), receptores de tipo no
    deducible estaticamente, ni metaprogramacion. `**kwargs` opacos **si** son violacion
    aqui (impiden probar la presencia), no un limite. Cada caso no visible se publica en
    `poblacion`/`cobertura`/`limites`. **Un ✅ no prueba ausencia de callers no
    gobernados**: prueba que la poblacion descubierta esta conforme o registrada.

Uso:
    python scripts/validate_wiring.py                       # verificar
    python scripts/validate_wiring.py --write-report        # verificar + publicar JSON
    python scripts/validate_wiring.py --ignore-known         # rojo sin excepciones tipadas
    python scripts/validate_wiring.py --root DIR             # verificar otro arbol (tests)

Salida: 0 = conforme; 1 = violaciones; 2 = error de uso o lector fallido.
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT = ROOT / ".opencode" / "wiring_report.json"
SCHEMA_VERSION = "1.0"

# --------------------------------------------------------------------------- politica
#
# Politica centralizada AQUI (una sola fuente de verdad; no repartida por los callers).
# `senales`: argumentos que deben viajar en cada llamada — omitirlos cambia la conducta
# por default silencioso. `prohibidos`: argumentos ya fuera del contrato (F-D');
# reaparecer, en un caller o en la firma, rompe AC16.

GOBERNADOS: dict[tuple[str, str], dict] = {
    ("PainSolutionMapper", "detect_pains"): {
        "senales": ("whatsapp_html_detected",),
        "prohibidos": (),
        "fuente": "maestro §1 fila F-A' · AC7",
        "por_que": (
            "su default False produce el pain `no_whatsapp_visible` que las otras dos "
            "rutas no producen cuando hay HTML y el campo esta UNKNOWN/CONFLICT"
        ),
    },
    ("CoherenceValidator", "validate"): {
        "senales": ("whatsapp_html_detected",),
        "prohibidos": (),
        "fuente": "maestro §1 filas F-A'/CONFLICT · AC7",
        "por_que": (
            "`_check_whatsapp_verified` decide con la senal; omitirla evalua el check "
            "bajo el supuesto de que no hay canal visible"
        ),
    },
    ("AssessmentBuilder", "with_validation"): {
        "senales": ("validation_summary",),
        "prohibidos": ("whatsapp_validation",),
        "fuente": "maestro §2 F-D' · AC16",
        "por_que": (
            "`validation_summary` es el dato upstream que llega al payload; "
            "`whatsapp_validation` era un contrato muerto cuyo dato ya viaja dentro de aquel"
        ),
    },
    # Productor de PROMESAS (no de pains): la tabla de servicios de la propuesta decide
    # que el boton "existe en produccion" leyendo presencia y conflicto. Los dos flags se
    # defaultean, asi que un caller que los omita promete o retira la fila sin avisar.
    # G la goberna hoy porque gobernar solo `detect_pains` dejaria el otro extremo del
    # cable sin guard (F-F ampliada, maestro §1).
    ("V4ProposalGenerator", "_generate_dynamic_services_table"): {
        "senales": ("site_presence_report", "whatsapp_conflict"),
        "prohibidos": (),
        "fuente": "maestro §1 fila F-F ampliada · AC7",
        "por_que": (
            "su default retira la presencia verificada y el conflicto de la tabla de "
            "servicios: la propuesta queda prometedora por omision, no por evidencia"
        ),
    },
}

NOMBRES_GOBERNADOS = {metodo for (_cls, metodo) in GOBERNADOS}

# Exclusion por ROL de directorio (no por archivo conocido); se publica con su motivo.
EXCLUSIONES_POR_ROL: dict[str, str] = {
    ".git": "historial de version-control, no es fuente",
    "venv": "entorno virtual de terceros",
    ".venv": "entorno virtual de terceros",
    ".venv-wsl": "entorno virtual de terceros",
    "__pycache__": "bytecode generado",
    "node_modules": "dependencias de terceros",
    "dist": "artefacto de empaquetado",
    "build": "artefacto de empaquetado",
    ".mypy_cache": "cache de herramienta",
    ".pytest_cache": "cache de herramienta",
    ".tox": "entorno de herramienta",
    ".eggs": "dependencia empaquetada",
    "temp": "scratch y respaldos locales (gitignorado), no fuente versionada",
    "output": "artefactos de corridas: salida, no fuente",
    "evidence": "scripts de medicion historicos; el contrato del plan prohibe reescribirlos",
    "archives": "registro historico cerrado; gobernarlo implicaria reescribir historia",
    "Archives": "registro historico cerrado de .opencode/plans",
}

# Los tests se gobiernan para `prohibidos` (una firma vieja re-introducida en un test es
# la recidiva que AC16 quiere romper) y NO para `senales` (un test que ejerce el default
# lo hace a proposito; gobernarlo obligaria a reescribir la suite).
DIR_TESTS = "tests"

# Homonimos confirmados por G: resuelven a un tipo y ese tipo no es un productor gobernado.
EXCLUSIONES_POR_CLASE: dict[str, str] = {
    "PrecisionValidator": "audita precision numerica, no promesa WhatsApp (AC7: excluir)",
    "NoDefaultsValidator": "audita defaults financieros, no senales de canal",
    "EnvValidator": "valida variables de entorno",
    "PlanValidator": "valida planes de contenido",
    "ContentValidator": "valida contenido generado",
}

# ---------------------------------------------------------------------- excepciones
#
# Tipadas, con dueno y condicion de baja, y **acotables con `--ignore-known`** para que
# cualquiera vea lo que tapan. Una excepcion cuyo hallazgo ya no existe es en si una
# violacion (`EXCEPCION_VAGA`): asi el registro no puede degradarse a allowlist.

EXCEPCIONES: list[dict] = [
    # FASE-B (REFACTOR-WHATSAPP, AC1) retira las tres excepciones que amparaban las
    # omisiones de `whatsapp_html_detected` en v4_asset_orchestrator.py: los tres
    # callers (detect_pains + validate pre-gen + validate post-gen) ya propagan la
    # senal, asi que cada una habria caido en `EXCEPCION_VAGA`. Historial completo
    # en `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-G/wiring_report.json`
    # (dueno FASE-B, ac AC1, `baja_cuando` cumplido el 2026-09-20).
]


# ---------------------------------------------------------------------------- helpers
def _sha_curto(root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=root, capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip() or "SIN_GIT"
    except Exception:
        return "SIN_GIT"


def _relativo(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def archivos_en_alcance(root: Path) -> tuple[list[Path], list[dict]]:
    """Descubre el arbol sin lista fija. Devuelve (fuentes, exclusiones con motivo)."""
    fuentes: list[Path] = []
    exclusiones: list[dict] = []
    for path in sorted(root.rglob("*.py")):
        partes = set(path.relative_to(root).parts[:-1])
        rol = sorted(partes & set(EXCLUSIONES_POR_ROL))
        if rol:
            exclusiones.append(
                {"ruta": _relativo(path, root), "rol": rol[0],
                 "motivo": EXCLUSIONES_POR_ROL[rol[0]]}
            )
            continue
        fuentes.append(path)
    return fuentes, exclusiones


def _cls_de_expresion(node) -> str | None:
    """`Cls(...)` -> 'Cls'; otra cosa -> None."""
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            return node.func.attr
    return None


def _anotacion_nombre(anot) -> str | None:
    if anot is None:
        return None
    if isinstance(anot, ast.Subscript):  # Optional[Cls] / list[Cls] -> mirar el valor
        return _anotacion_nombre(anot.slice)
    return getattr(anot, "id", None) or getattr(anot, "attr", None)


def _clases_de(tree: ast.Module) -> list[ast.ClassDef]:
    return [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]


def _analizar(texto: str) -> ast.Module | None:
    """`ast.parse` silenciando los SyntaxWarning del arbol ajeno a esta medicion.

    El repo tiene cadenas con escape invalido (contrabarra-W, contrabarra-paren); parsear
    610 archivos las reproduciria dos veces por corrida y ensuciaria la salida del quick,
    que es donde este check va a vivir. No oculta un error propio: un `SyntaxError` si
    descarta el archivo y se cuenta abajo.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            return ast.parse(texto)
        except SyntaxError:
            return None


def _encadenar(tree: ast.Module, tipos) -> dict[int, ast.AST]:
    """Mapa `id(nodo)` -> contenedor del tipo pedido (clase o funcion) mas interno.

    `ast.walk` es BFS desde la raiz, asi que los contenedores externos se visitan
    primero y la asignacion deja **el mas interno**, que es el que manda al resolver
    `self.attr` o una variable local.
    """
    cadena: dict[int, ast.AST] = {}
    for contenedor in ast.walk(tree):
        if not isinstance(contenedor, tipos):
            continue
        for hijo in ast.walk(contenedor):
            if hijo is contenedor:
                continue
            cadena[id(hijo)] = contenedor
    return cadena


# --------------------------------------------------------------- bindings y firmas
class _Ambito:
    """Bindings `nombre -> clase` de un archivo: module-level y por funcion.

    Incluye los **aliases de import** (`from x import CoherenceValidator as CV`), porque
    AC7 exige que los aliases queden cubiertos: gobernar solo el nombre canonico dejaria
    evadir el check escribiendo `CV()`.
    """

    def __init__(self, tree: ast.Module):
        self.imports = _imports_de(tree)
        self.module = _bindings_de(tree.body)
        self.funciones: dict[int, dict] = {}
        for func in ast.walk(tree):
            if isinstance(func, ast.FunctionDef | ast.AsyncFunctionDef):
                self.funciones[id(func)] = _bindings_de(func.body, func.args)

    def resolver_nombre(self, nombre: str) -> str | None:
        """`CV` -> `CoherenceValidator` cuando el archivo lo importo con alias."""
        return self.imports.get(nombre, nombre)


def _imports_de(tree: ast.Module) -> dict[str, str]:
    """`alias_local -> nombre_original` de todos los imports del modulo."""
    tabla: dict[str, str] = {}
    for nodo in ast.walk(tree):
        if isinstance(nodo, ast.ImportFrom):
            for alias in nodo.names:
                tabla[alias.asname or alias.name] = alias.name
        elif isinstance(nodo, ast.Import):
            for alias in nodo.names:
                ultima = alias.name.split(".")[-1]
                tabla[alias.asname or ultima] = ultima
    return tabla


def _sentencias_en_ambito(cuerpo: list):
    """Rocia el ambito descendiendo por compuestos (`try`/`if`/`with`/`for`/`while`).

    Mide hacia **gobernar mas**, no menos: `pain_mapper = PainSolutionMapper()` dentro de
    un `try` es el caso real de `V4DiagnosticGenerator._identify_brechas`, y sin descender
    ese caller productivo quedaba como `RECEPTOR_NO_RESUELTO` — un hueco de cobertura del
    propio verificador. Se detiene en `FunctionDef`/`ClassDef`, que son otros ambitos.
    """
    pila = list(cuerpo)
    while pila:
        nodo = pila.pop()
        yield nodo
        if isinstance(nodo, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef | ast.Lambda):
            continue
        for campo in ("body", "orelse", "finalbody", "handlers"):
            hijos = getattr(nodo, campo, None)
            if isinstance(hijos, list):
                pila.extend(h for h in hijos if isinstance(h, ast.stmt | ast.excepthandler))
        manejador = getattr(nodo, "handlers", None)
        if isinstance(manejador, list):
            pila.extend(h for h in manejador if isinstance(h, ast.ExceptHandler))


def _bindings_de(cuerpo: list, args=None) -> dict:
    binds: dict[str, str] = {}
    if args is not None:
        for arg in list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs):
            nombre = _anotacion_nombre(arg.annotation)
            if nombre:
                binds[arg.arg] = nombre
    for nodo in _sentencias_en_ambito(cuerpo):
        if isinstance(nodo, ast.Assign):
            cls = _cls_de_expresion(nodo.value)
            if cls:
                for objetivo in nodo.targets:
                    if isinstance(objetivo, ast.Name):
                        binds[objetivo.id] = cls
        elif isinstance(nodo, ast.AnnAssign) and isinstance(nodo.target, ast.Name):
            nombre = _anotacion_nombre(nodo.annotation)
            if nombre:
                binds[nodo.target.id] = nombre
    return binds


def _self_binding_de_clase(cls: ast.ClassDef, attr: str) -> str | None:
    """`self.<attr>` -> clase, desde `self.<attr> = Cls()` o `= param` con `param: Cls`."""
    for item in cls.body:
        if not isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        anots = {a.arg: _anotacion_nombre(a.annotation)
                 for a in item.args.args + item.args.kwonlyargs}
        for sub in ast.walk(item):
            if isinstance(sub, ast.Assign) and sub.targets and \
                    isinstance(sub.targets[0], ast.Attribute) and \
                    isinstance(sub.targets[0].value, ast.Name) and \
                    sub.targets[0].value.id == "self" and sub.targets[0].attr == attr:
                resuelta = _cls_de_expresion(sub.value)
                if resuelta:
                    return resuelta
                if isinstance(sub.value, ast.Name):
                    return anots.get(sub.value.id)
            if isinstance(sub, ast.AnnAssign) and isinstance(sub.target, ast.Attribute) \
                    and isinstance(sub.target.value, ast.Name) \
                    and sub.target.value.id == "self" and sub.target.attr == attr:
                nombre = _anotacion_nombre(sub.annotation)
                if nombre:
                    return nombre
    return None


def _clase_del_receptor(nodo: ast.Call, tree: ast.Module, env: _Ambito,
                        cont_clase: dict, cont_func: dict) -> tuple[str | None, str]:
    """`(clase_resuelta, estrategia)`. Estrategia con prefijo sin_ cuando no resuelve.

    Cubre los cuatro casos que AC7 nombra expresamente: alias de import, `self.<attr>`,
    `self` a secas (metodo propio) y asignacion local dentro de `try`/`if`/`with`.
    """
    receptor = nodo.func.value  # type: ignore[attr-defined]

    if isinstance(receptor, ast.Call):
        directa = _cls_de_expresion(receptor)
        if directa:
            return env.resolver_nombre(directa) or directa, "constructor_en_linea"
        return None, "receptor_callable_no_resuelto"

    if isinstance(receptor, ast.Attribute) and isinstance(receptor.value, ast.Name) \
            and receptor.value.id == "self":
        cls = cont_clase.get(id(nodo))
        if cls is not None:
            res = _self_binding_de_clase(cls, receptor.attr)
            if res:
                return env.resolver_nombre(res) or res, "self_binding_en_la_clase"
        return None, "self_attr_sin_binding"

    if isinstance(receptor, ast.Name):
        # `self.metodo(...)`: el receptor ES la clase que envuelve la llamada.
        if receptor.id == "self":
            cls = cont_clase.get(id(nodo))
            if cls is not None:
                return cls.name, "self_metodo_propio"
            return None, "self_fuera_de_clase"
        func = cont_func.get(id(nodo))
        if func is not None:
            res = env.funciones.get(id(func), {}).get(receptor.id)
            if res:
                return env.resolver_nombre(res) or res, "asignacion_o_anotacion_local"
        res = env.module.get(receptor.id)
        if res:
            return env.resolver_nombre(res) or res, "asignacion_module_level"
        # Nombre suelto que es una clase importada (incluido alias): `CV()`,
        # `PrecisionValidator.validate(...)`.
        if receptor.id in env.imports:
            return env.resolver_nombre(receptor.id), "clase_importada_o_alias"
        return None, "receptor_sin_binding"

    return None, "expresion_compuesta_o_dinamica"


def _metodo_de(nodo: ast.Call) -> str | None:
    if isinstance(nodo.func, ast.Attribute):
        return nodo.func.attr
    if isinstance(nodo.func, ast.Name):
        return nodo.func.id
    return None


def arboles_de(root: Path) -> tuple[list[dict], list[dict]]:
    """Parsea cada fuente UNA vez.

    Antes el recorrido era doble (una pasada para las firmas, otra para los callers):
    610 archivos leidos y parseados dos veces por cada corrida del quick. Devuelve
    `[{"ruta", "arbol", "es_test"}]` y la lista de exclusiones por rol.
    """
    fuentes, exclusiones = archivos_en_alcance(root)
    analizadas: list[dict] = []
    for path in fuentes:
        try:
            tree = _analizar(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        if tree is None:
            continue
        rel = _relativo(path, root)
        analizadas.append({
            "ruta": rel,
            "arbol": tree,
            "es_test": rel == f"{DIR_TESTS}.py" or rel.startswith(DIR_TESTS + "/"),
        })
    return analizadas, exclusiones


def firmar_simbolos(root: Path) -> dict:
    """Atajo publico: la firma REAL de cada simbolo gobernado sobre `root`."""
    return _firmas_desde(arboles_de(root)[0])


def _firmas_desde(arboles: list[dict]) -> dict:
    """Lee la firma REAL de cada simbolo gobernado (orden de parametros y defaults).

    Se calcula sobre el arbol, no se transcribe: si cambian el orden o re-introducen un
    parametro prohibido en la definicion, el verificador lo ve.
    """
    wanted: dict[str, set] = {}
    for (cls, metodo) in GOBERNADOS:
        wanted.setdefault(cls, set()).add(metodo)

    firmas: dict[str, dict] = {}
    for fuente in arboles:
        tree = fuente["arbol"]
        for cls in _clases_de(tree):
            if cls.name not in wanted:
                continue
            for miembro in cls.body:
                if not isinstance(miembro, ast.FunctionDef | ast.AsyncFunctionDef):
                    continue
                if miembro.name not in wanted[cls.name]:
                    continue
                argumentos = miembro.args
                nombres = [a.arg for a in argumentos.posonlyargs + argumentos.args]
                defaults = [ast.unparse(d) for d in argumentos.defaults]
                cortados = nombres[1:] if nombres and nombres[0] == "self" else nombres
                firmas[f"{cls.name}.{miembro.name}"] = {
                    "parametros": nombres,
                    "parametros_de_llamada": cortados,
                    "kwonly": [a.arg for a in argumentos.kwonlyargs],
                    "defaults": defaults,
                    "archivo": fuente["ruta"],
                }
    faltantes = sorted(f"{c}.{m}" for (c, m) in GOBERNADOS if f"{c}.{m}" not in firmas)
    return {"firmas": firmas, "faltantes": faltantes}


# ------------------------------------------------------------------------- descubrimiento
def poblar(root: Path) -> dict:
    """Descubre y clasifica la poblacion de llamadas a los simbolos gobernados.

    Clasificaciones:
      GOBERNADA_CONFORME            senales presentes
      GOBERNADA_CON_OMISION         senal requerida ausente             -> violacion
      GOBERNADA_CON_KWARGS_OPACOS   `**kwargs` impide probar presencia   -> violacion
      GOBERNADA_CON_ARG_PROHIBIDO   firma vieja re-introducida          -> violacion (AC16)
      TEST_EXENTO_DE_SENAL          en tests/, sin la senal             -> registro, no viola
      EXCLUIDA_POR_CLASE            resuelve a tipo no gobernado        -> registro, no viola
      RECEPTOR_NO_RESUELTO          el AST no deduce el tipo            -> se cuenta y publica
    """
    arboles, exclusiones = arboles_de(root)
    info = _firmas_desde(arboles)
    firmas = info["firmas"]
    poblacion: list[dict] = []
    violaciones: list[dict] = []

    for fuente in arboles:
        tree = fuente["arbol"]

        env = _Ambito(tree)
        cont_clase = _encadenar(tree, ast.ClassDef)
        cont_func = _encadenar(tree, ast.FunctionDef | ast.AsyncFunctionDef)
        rel = fuente["ruta"]
        es_test = fuente["es_test"]

        for nodo in ast.walk(tree):
            if not isinstance(nodo, ast.Call):
                continue
            metodo = _metodo_de(nodo)
            if metodo not in NOMBRES_GOBERNADOS or not isinstance(nodo.func, ast.Attribute):
                continue

            clase, estrategia = _clase_del_receptor(nodo, tree, env, cont_clase, cont_func)
            politica = GOBERNADOS.get((clase, metodo)) if clase else None
            keywords = {k.arg for k in nodo.keywords if k.arg}
            hay_kwargs_opacos = any(k.arg is None for k in nodo.keywords)
            firma = firmas.get(f"{clase}.{metodo}") if clase else None

            cubiertos_pos: set[str] = set()
            if firma:
                for indice in range(len(nodo.args)):
                    parametros = firma["parametros_de_llamada"]
                    if indice < len(parametros):
                        cubiertos_pos.add(parametros[indice])

            registro: dict = {
                "archivo": rel,
                "linea": nodo.lineno,
                "metodo": metodo,
                "receptor": ast.unparse(nodo.func.value)[:60],
                "clase_resuelta": clase,
                "resolucion": estrategia,
                "gobernado": politica is not None,
                "en_tests": es_test,
                "kwargs_presentes": sorted(keywords),
                "posicionales": len(nodo.args),
                "hay_kwargs_opacos": hay_kwargs_opacos,
            }

            if politica is None:
                if clase in EXCLUSIONES_POR_CLASE:
                    registro["clasificacion"] = "EXCLUIDA_POR_CLASE"
                    registro["motivo"] = EXCLUSIONES_POR_CLASE[clase]
                elif clase:
                    registro["clasificacion"] = "EXCLUIDA_POR_CLASE_NO_GOBERNADA"
                    registro["motivo"] = (
                        f"el receptor resuelve a {clase}, que no es un productor gobernado"
                    )
                else:
                    registro["clasificacion"] = "RECEPTOR_NO_RESUELTO"
                    registro["motivo"] = (
                        f"metodo de nombre gobernado ({metodo}) pero el AST no deduce el "
                        f"tipo del receptor ({estrategia}); se publica, no se descarta"
                    )
                if es_test and politica is None:
                    registro["motivo"] += " (llamada bajo tests/)"
                poblacion.append(registro)
                continue

            senales = politica["senales"]
            ausentes = tuple(s for s in senales
                             if s not in keywords and s not in cubiertos_pos)
            prohibidos = politica["prohibidos"]
            vistos = sorted(set(prohibidos) & keywords)
            if firma and prohibidos and len(nodo.args) > len(firma["parametros_de_llamada"]):
                # Aridad imposible contra la firma actual: llego algo de mas (firma vieja).
                vistos = sorted(set(prohibidos))
            registro["senales_requeridas"] = list(senales)
            registro["senales_ausentes"] = list(ausentes)
            registro["prohibidos_presentes"] = vistos

            if vistos:
                registro["clasificacion"] = "GOBERNADA_CON_ARG_PROHIBIDO"
                violaciones.append({
                    "tipo": "ARGUMENTO_PROHIBIDO",
                    "archivo": rel, "linea": nodo.lineno,
                    "simbolo": f"{clase}.{metodo}",
                    "detalle": (f"re-introduce {vistos}; contrato retirado por F-D' "
                                f"({politica['por_que']})"),
                    "fuente_politica": politica["fuente"],
                })
            elif es_test and ausentes:
                registro["clasificacion"] = "TEST_EXENTO_DE_SENAL"
            elif hay_kwargs_opacos and ausentes:
                registro["clasificacion"] = "GOBERNADA_CON_KWARGS_OPACOS"
                violaciones.append({
                    "tipo": "KWARGS_OPACOS",
                    "archivo": rel, "linea": nodo.lineno,
                    "simbolo": f"{clase}.{metodo}",
                    "detalle": (f"`**kwargs` oculta la senal {list(ausentes)}; no puede "
                                f"probarse su presencia"),
                    "fuente_politica": politica["fuente"],
                })
            elif ausentes:
                registro["clasificacion"] = "GOBERNADA_CON_OMISION"
                violaciones.append({
                    "tipo": "SENAL_OMITIDA",
                    "archivo": rel, "linea": nodo.lineno,
                    "simbolo": f"{clase}.{metodo}",
                    "detalle": (f"falta {list(ausentes)}; su default cambia la conducta "
                                f"en silencio ({politica['por_que']})"),
                    "fuente_politica": politica["fuente"],
                })
            else:
                registro["clasificacion"] = "GOBERNADA_CONFORME"
            poblacion.append(registro)

    # El contrato muerto tambien puede reaparecer en la DEFINICION, no solo en el caller.
    for nombre, firma in sorted(firmas.items()):
        cls, _, metodo = nombre.partition(".")
        politica = GOBERNADOS.get((cls, metodo))
        if not politica or not politica["prohibidos"]:
            continue
        vivos = [p for p in politica["prohibidos"] if p in firma["parametros"]]
        if vivos:
            violaciones.append({
                "tipo": "CONTRATO_MUERTO_VIGENTE",
                "archivo": firma["archivo"], "linea": 0,
                "simbolo": nombre,
                "detalle": f"la firma aun declara {vivos}; F-D' lo retiro del contrato",
                "fuente_politica": politica["fuente"],
            })

    for simbolo in info["faltantes"]:
        violaciones.append({
            "tipo": "SIMBOLO_GOBERNADO_AUSENTE",
            "archivo": "(desconocido)", "linea": 0, "simbolo": simbolo,
            "detalle": ("el verificador declara un simbolo que ya no existe en el arbol: "
                        "la politica caduco. Se reporta, no se silencia el check"),
            "fuente_politica": "GOBERNADOS",
        })

    return {
        "poblacion": sorted(poblacion, key=lambda r: (r["archivo"], r["linea"], r["metodo"])),
        "violaciones": sorted(violaciones, key=lambda v: (v["archivo"], v["linea"], v["tipo"])),
        "firmas": firmas,
        "faltantes": info["faltantes"],
        "archivos_analizados": len(arboles),
        "exclusiones": exclusiones,
    }


def _agrupar_exclusiones(exclusiones: list[dict]) -> dict:
    """Resume las exclusiones por rol de directorio: cantidad, motivo y un ejemplo."""
    agrupado: dict[str, dict] = {}
    for item in exclusiones:
        rol = item["rol"]
        entrada = agrupado.setdefault(rol, {
            "cantidad": 0, "motivo": item["motivo"],
            "ejemplo": item["ruta"],
        })
        entrada["cantidad"] += 1
    return dict(sorted(agrupado.items()))


# --------------------------------------------------------------------------- excepciones
def aplicar_excepciones(violaciones: list[dict], excepciones: list[dict]) -> dict:
    """Empareja hallazgos con excepciones tipadas. Ningun lado sobra: ambos se reportan."""
    abiertas = list(violaciones)
    aplicadas: list[dict] = []
    usadas: set[int] = set()

    for hall in abiertas:
        if hall["tipo"] != "SENAL_OMITIDA":
            continue
        for exc in excepciones:
            if id(exc) in usadas:
                continue
            if hall["archivo"] != exc["archivo"]:
                continue
            if hall["simbolo"] != exc["simbolo"]:
                continue
            if exc["senal"] not in hall["detalle"]:
                continue
            usadas.add(id(exc))
            aplicadas.append({"exc": exc, "hall": hall})
            break

    amparadas = {id(a["hall"]) for a in aplicadas}
    restantes = [h for h in abiertas if id(h) not in amparadas]

    for exc in excepciones:
        if id(exc) in usadas:
            continue
        restantes.append({
            "tipo": "EXCEPCION_VAGA",
            "archivo": exc["archivo"], "linea": 0, "simbolo": exc["simbolo"],
            "detalle": ("excepcion tipada que ya no ampara ningun hallazgo: borrarla (el "
                        "hallazgo se corrigio) o corregir su criterio. Si se queda sin "
                        "uso deja de ser excepcion y pasa a ser allowlist"),
            "fuente_politica": f"dueno={exc['dueno']} ac={exc['ac']} "
                               f"baja_cuando={exc['baja_cuando']}",
        })

    return {
        "abiertas": sorted(restantes, key=lambda v: (v["archivo"], v["linea"], v["tipo"])),
        "aplicadas": [
            {
                "tipo_excepcion": a["exc"]["tipo"],
                "archivo": a["exc"]["archivo"],
                "simbolo": a["exc"]["simbolo"],
                "senal": a["exc"]["senal"],
                "motivo": a["exc"]["motivo"],
                "dueno": a["exc"]["dueno"],
                "ac": a["exc"]["ac"],
                "baja_cuando": a["exc"]["baja_cuando"],
                "linea_amparada": a["hall"]["linea"],
            }
            for a in aplicadas
        ],
    }


# -------------------------------------------------------------------------------- reporte
def construir_reporte(root: Path, ignore_known: bool = False) -> dict:
    datos = poblar(root)
    if ignore_known:
        abiertas, aplicadas = list(datos["violaciones"]), []
    else:
        emparejado = aplicar_excepciones(datos["violaciones"], EXCEPCIONES)
        abiertas, aplicadas = emparejado["abiertas"], emparejado["aplicadas"]

    conteo: dict[str, int] = {}
    for registro in datos["poblacion"]:
        conteo[registro["clasificacion"]] = conteo.get(registro["clasificacion"], 0) + 1

    return {
        "schema_version": SCHEMA_VERSION,
        "verificador": "scripts/validate_wiring.py",
        "comando": "python scripts/validate_wiring.py --write-report",
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_sha": _sha_curto(root),
        "modo_excepciones": "IGNORADAS (--ignore-known)" if ignore_known else "APLICADAS",
        "politica": {
            f"{cls}.{metodo}": {
                "senales_requeridas": list(pol["senales"]),
                "argumentos_prohibidos": list(pol["prohibidos"]),
                "fuente": pol["fuente"],
                "por_que": pol["por_que"],
                "firma_real": datos["firmas"].get(f"{cls}.{metodo}"),
            }
            for (cls, metodo), pol in sorted(GOBERNADOS.items())
        },
        "cobertura": {
            "archivos_en_alcance": datos["archivos_analizados"],
            "archivos_excluidos_por_rol": len(datos["exclusiones"]),
            "llamadas_descubiertas": len(datos["poblacion"]),
            "por_clasificacion": dict(sorted(conteo.items())),
            "receptores_no_resueltos": sum(
                1 for r in datos["poblacion"]
                if r["clasificacion"] == "RECEPTOR_NO_RESUELTO"
            ),
            # La cifra que importa: un hueco en produccion si puede esconder una senal;
            # un hueco bajo tests/ solo puede esconder un test, no un caller real.
            "receptores_no_resueltos_en_produccion": sum(
                1 for r in datos["poblacion"]
                if r["clasificacion"] == "RECEPTOR_NO_RESUELTO" and not r["en_tests"]
            ),
            "gobernadas_resueltas": sum(
                1 for r in datos["poblacion"] if r["gobernado"]
            ),
            "exclusiones_por_clase": EXCLUSIONES_POR_CLASE,
        },
        "poblacion": datos["poblacion"],
        "violaciones": abiertas,
        "excepciones_aplicadas": aplicadas,
        # Se agrega por ROL, no por archivo: la lista cruda eran 8.285 rutas (7.589 de
        # `venv/`) inflando el artefacto a 1,4 MB y tapando lo legible. El rol y su
        # motivo siguen publicados, con cantidad y un ejemplo para ir a buscarlos.
        "exclusiones_por_rol": _agrupar_exclusiones(datos["exclusiones"]),
        "limites": [
            "dispatch dinamico (`getattr(obj, nombre)(...)`): el AST no ve que metodo se invoca",
            "receptores cuyo tipo no se deduce estaticamente: se publican en `poblacion` "
            "con clasificacion RECEPTOR_NO_RESUELTO y se cuentan en `cobertura`",
            "metaprogramacion (decoradores que reescriben llamadas, `__getattr__`)",
            "los tests estan exentos de la exigencia de `senales` (ejercitan defaults a "
            "proposito) pero NO de `argumentos_prohibidos`",
            "gobernar `validate` por nombre de metodo seria un falso verde: solo se "
            "gobierna cuando el receptor resuelve a una clase de `GOBERNADOS`",
            "una funcion de MODULO que se llame como un metodo gobernado "
            "(`validate_opencode_refs.validate(...)`) resuelve a su modulo y queda excluida: "
            "gobernar funciones de modulo pediria tabla propia de (modulo, funcion), no la de "
            "clases. Limite medido al inventariar las 74 exclusiones del arbol",
            "un ✅ prueba que la poblacion descubierta esta conforme o registrada; NO "
            "prueba que no existan callers fuera del alcance del AST",
        ],
    }


def publicar(reporte: dict, destino: Path) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(reporte, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destino


def verificar(reporte: dict) -> list:
    return reporte["violaciones"]


def resumen_de(reporte: dict) -> str:
    cobertura = reporte["cobertura"]
    por = cobertura["por_clasificacion"]
    return (
        f"{cobertura['llamadas_descubiertas']} llamadas descubiertas en "
        f"{cobertura['archivos_en_alcance']} archivos | gobernadas "
        f"{cobertura['gobernadas_resueltas']} (conformes {por.get('GOBERNADA_CONFORME', 0)}, "
        f"omisiones {por.get('GOBERNADA_CON_OMISION', 0)}) | amparadas por excepcion "
        f"{len(reporte['excepciones_aplicadas'])} | violaciones {len(reporte['violaciones'])} "
        f"| receptores no resueltos {cobertura['receptores_no_resueltos']}"
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Verificador AST de cableado de senales requeridas (AC7/AC16)")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--write-report", default=None, const=str(DEFAULT_REPORT),
                    nargs="?", help="publicar el JSON del reporte")
    ap.add_argument("--ignore-known", action="store_true",
                    help="no aplicar excepciones tipadas: muestra lo que tapan")
    ap.add_argument("--json", action="store_true", help="salida maquina")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(f"[2] no existe el arbol: {root}")
        return 2

    try:
        reporte = construir_reporte(root, ignore_known=args.ignore_known)
    except Exception as exc:  # LECTOR-FALLIDO con nombre propio, nunca un favorable
        print(f"[2] verificador fallido al medir {root}: {type(exc).__name__}: {exc}")
        return 2

    if args.write_report:
        publicar(reporte, Path(args.write_report))

    viol = verificar(reporte)
    if args.json:
        print(json.dumps({"resumen": resumen_de(reporte), "violaciones": viol},
                         ensure_ascii=False, indent=2))
        return 1 if viol else 0

    if viol:
        if not args.quiet:
            print(f"[FAIL] Wiring: {len(viol)} violacion(es) de cableado | {resumen_de(reporte)}")
        for v in viol:
            print(f"  - {v['tipo']} {v['archivo']}:{v['linea']} {v['simbolo']} :: "
                  f"{v['detalle']}  [politica: {v['fuente_politica']}]")
        if not args.quiet and not args.ignore_known:
            print("  (para ver lo que tapan las excepciones tipadas: --ignore-known)")
        return 1

    if not args.quiet:
        print(f"[OK] Wiring: {resumen_de(reporte)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
