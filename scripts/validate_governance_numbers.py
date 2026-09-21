#!/usr/bin/env python3
"""Verificador de aserciones sobre conteos en los documentos de gobierno (FASE-A del plan
VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20).

QUE HACE
    Cada vez que un documento de gobierno (`phased_project_executor.md` y su template de
    `00-lecciones-capitalizadas.md`) afirma «este verificador es el check N de M» o «el hook
    corre K pasos», este script contrasta esa afirmacion contra la **fuente dinamica de verdad**:
    la etiqueta `[N/M]` que el codigo imprime dentro de su propio `def _check_*` en
    `scripts/run_all_validations.py`, y los pasos que declara `scripts/git_hooks/pre-commit`.

POR QUE EXISTE (medido, no supuesto)
    Cuatro asunciones del workflow estaban vencidas contra el codigo que las ejecuta y **ningun
    check las sostenia**: se cumplian por coincidencia (L-R.1). El texto que pide el verificador
    vivia en el mismo documento cuyos numeros estaban vencidos (maestro §1, medicion A8).

POLITICA: REPORTA, NO REESCRIBE (decision DA-HF3, misma que `validate_plan_citations.py`)
    Corregir la frase a mano produce la fosilizacion siguiente: la cura es un verificador o un
    writer, no el edit.

REGLA DE POBLACION (A8 — sin ella AC1 es inalcanzable)
    El escaneo de los dos documentos no devuelve cuatro coincidencias sino 22 instancias `[N/M]`
    en 17 lineas mas 2 formas «check N». Cada instancia cae en una de tres clases, y la clase
    decide si es hallazgo:
      * **VIVA (normativa)**: sostiene una regla vigente -> se contrasta; si no cuadra -> hallazgo.
      * **CONGELADA (historica)**: mencion de medicion fechada o dentro de una entrada del
        changelog `## Versiones` con un denominador de otra epoca. El propio objeto auditado
        ampara esta clase (entrada v2.24.0 del changelog; ver
        `historical_excluded[].authorized_by`).
        No es hallazgo, **pero se publica** con su conteo y la frase que la ampara (L-HF1).
      * **VIGENTE Y CORRECTA**: cuadra con la fuente -> entra en `assertions_checked`.
    Un hallazgo es **una asercion con sus `occurrences[]`**, no una linea.

TRI-ESTADO (R2.9, aplicado a si mismo como `validate_lesson_capitalization.py`)
    `SIN-HALLAZGOS` (y solo con `coverage_basis` completa) / `AUSENTE` (dice la ruta buscada) /
    `LECTOR-FALLIDO` (dice el motivo y **nunca** un favorable ni un 0). Prohibido el `except` que
    devuelve «no habia nada».

USO
    python scripts/validate_governance_numbers.py --report
    python scripts/validate_governance_numbers.py --json
    python scripts/validate_governance_numbers.py --governance-doc D [--governance-doc D2] \\
        --source S --hook H          # (tests: fixtures en tmp_path)

SALIDA: 0 = SIN-HALLAZGOS · 1 = HALLAZGOS · 2 = AUSENTE · 3 = LECTOR-FALLIDO.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    # Misma solucion de la casa que `validate_lesson_capitalization.py`: la consola
    # de este entorno no es UTF-8 y el texto citado de los documentos lleva acentos.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent

SOURCE_DEFAULT = ROOT / "scripts" / "run_all_validations.py"
HOOK_DEFAULT = ROOT / "scripts" / "git_hooks" / "pre-commit"
GOVERNANCE_DEFAULTS = (
    ROOT / ".agents" / "workflows" / "phased_project_executor.md",
    ROOT / ".agents" / "workflows" / "templates" / "lecciones-capitalizadas-template.md",
)
REPORT_DEFAULT = (
    ROOT / "evidence" / "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20" / "FASE-A" / "informe.json"
)

# Los archivos que SON la fuente de verdad nunca pueden ser el sujeto de una asercion.
SOURCE_FILE_NAMES = {"run_all_validations.py", "pre-commit"}

BRACKET_RE = re.compile(r"\[(\d+)/(\d+)\]")
CHECK_N_RE = re.compile(r"\bcheck (\d+)\b")
# Prosa de conteo: «11 checks», «7 pasos», «10/10 en modo rápido». NO entra en la poblacion
# auditada (esa es la de A8: `[N/M]` y «check N»); se mide solo para publicar la familia (i).
PROSA_RE = re.compile(r"\b\d{1,3}\s*(?:/\s*\d{1,3})?\s*(?:checks?|validaciones|pasos)\b|"
                      r"\b\d{1,3}/\d{1,3}\b")
METHOD_RE = re.compile(r"^    def (_check_[A-Za-z0-9_]+)\s*\(")
PRINT_LABEL_RE = re.compile(r"""print\(f?["']\[(\d+)/(\d+)\]([^"']*)""")
SCRIPT_REF_RE = re.compile(r"([A-Za-z0-9_]+\.py)")
HOOK_STEP_RE = re.compile(r"^#\s*\[(\d+)/(\d+)\]\s+(.*)$")
CHANGELOG_HEADER_RE = re.compile(r"^##\s+Versiones\b")
CHANGELOG_ENTRY_RE = re.compile(r"^- \*\*v\d+\.\d+\.\d+\*\*")

# --- Simbolos de la regla de poblacion (publicados: son auditables y mutables) ------------
# H2: la clausula de la propia instancia narra un evento pasado de medicion.
HISTORICAL_EVENT_MARKERS = ("bloqueó", "ese commit", "el mismo día", "el mismo dia",
                            "pasó el commit")
# Marcadores de fuente. `hook` ignora el sujeto: una afirmacion «[6/7] del hook» afirma la
# forma del hook (sus 7 pasos), no la identidad de un check.
KIND_MARKERS = {
    "hook": ("pre-commit", "hook"),
    "quick": ("--quick",),
    "full": ("fuera de `--quick`", "completo", "modo completo", " full "),
}
ALIAS_STOPWORDS = {
    "checking", "check", "checks", "files", "file", "with", "from", "that", "this", "all",
    "being", "running", "quick", "full", "completo", "hook", "commit", "version",
    "versions", "planes", "plan", "indice", "índice", "arbol", "árbol", "paso", "pasos",
    "total", "modo", "archivados", "executor", "corrida", "validations", "validacion",
    "against", "propio", "misma", "otro", "otra", "solo", "linea", "lineas", "numeros",
    "simbolos", "simbolo", "symbols", "ejemplo", "prohibido", "nuevas", "anterior",
    "siguiente", "unica", "unico", "marca", "bandera", "corre", "imprime", "tests",
}

# Familias que este verificador NO cubre (AC2/AC17). No son un «etcetera»: cada una se mide
# en `cobertura_de_familias()` y se publica con su conteo, su comando y su dueno.
FAMILIES_NOT_COVERED = (
    "prosa-de-conteo-sin-patron",
    "conteos-fuera-de-los-documentos-de-gobierno",
    "pins-de-conteo-en-tests",
    "fuentes-dinamicas-que-no-sean-etiqueta-impresa",
)

SCHEMA_VERSION = "1.0"


class LectorFallido(Exception):
    """R2.9: el lector caído se declara; nunca se lee como ausencia."""


class Ausente(Exception):
    """R2.9: la ruta buscada se imprime tal cual."""


def _ascii(texto: str) -> str:
    """La consola bajo cp1252 no admite acentos: solo se máscara la IMPRESION."""
    sin = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return sin.replace("\n", " ").strip()


def _leer(path: Path, que: str) -> str:
    if not path.exists():
        raise Ausente(f"{que} no existe: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:  # R2.9: jamas «no habia nada»
        raise LectorFallido(f"no se pudo leer {que} ({path}): {exc}") from exc


# -----------------------------------------------------------------------------------------
# Fuente dinamica de verdad 1: run_all_validations.py — etiqueta emparejada con su def _check_*
# -----------------------------------------------------------------------------------------

def _sin_docstring(cuerpo: list) -> list:
    """El cuerpo del metodo sin su docstring: los ejemplos del docstring no son el codigo."""
    fuera, dentro = [], False
    for linea in cuerpo:
        if not linea.strip() and not fuera:
            continue                       # lineas en blanco antes del docstring
        if not dentro and not fuera and '"""' in linea:
            if linea.count('"""') == 2 and linea.strip() != '"""':
                continue                   # docstring cerrado en una sola linea
            dentro = True
            continue
        if dentro:
            if '"""' in linea:
                dentro = False
            continue
        fuera.append(linea)
    return fuera


def _stem(nombre: str) -> str:
    base = nombre[:-3] if nombre.endswith(".py") else nombre
    for prefijo in ("validate_", "check_", "build_"):
        if base.startswith(prefijo):
            return base[len(prefijo):]
    return base


def _aliases(nombre_script: str, etiqueta: str) -> set:
    tokens = set()
    base = nombre_script[:-3] if nombre_script.endswith(".py") else nombre_script
    if base:
        tokens.add(base.lower())
        tokens.add(_stem(nombre_script).lower().replace("_", "-"))
        tokens.add(_stem(nombre_script).lower())
    for palabra in re.findall(r"[A-Za-záéíóúñ][A-Za-záéíóúñ0-9_\-]{4,}", etiqueta or ""):
        bajo = palabra.lower()
        if bajo not in ALIAS_STOPWORDS:
            tokens.add(bajo)
    return tokens


def cargar_fuente_validations(path: Path) -> list:
    """`[{script, ordinal, total, mode, etiqueta, emisor, aliases}]`, leido del codigo.

    El modo (quick / full) NO se deduce del denominador: se lee de donde `run_all` invoca el
    check — antes o despues de la linea `if not self.quick`. Confundir la etiqueta del check de
    dependencias con la del write-back de QMind fue exactamente el error de medicion de A3.
    """
    lineas = _leer(path, "fuente de checks").splitlines()
    bloques = {}
    actual = None
    for linea in lineas:
        m = METHOD_RE.match(linea)
        if m:
            actual = m.group(1)
            bloques.setdefault(actual, [])
            continue
        if actual and re.match(r"^(class |def )\w", linea):
            actual = None
        if actual:
            bloques[actual].append(linea)

    registros = []
    for metodo, cuerpo in bloques.items():
        texto = "\n".join(cuerpo)
        etiqueta = PRINT_LABEL_RE.search(texto)
        if not etiqueta:
            continue
        # El script invocado se lee del CODIGO, no del docstring: el docstring de
        # `_check_plan_citations` menciona `file.py:123` como ejemplo de lo prohibido, y
        # atribuir ese token al check dejaba A1 sin sujeto.
        scripts = [
            s for s in SCRIPT_REF_RE.findall("\n".join(_sin_docstring(cuerpo)))
            if s not in SOURCE_FILE_NAMES and s != "measure_iterations.py"
        ]
        registros.append({
            "emisor": metodo,
            "ordinal": int(etiqueta.group(1)),
            "total": int(etiqueta.group(2)),
            "etiqueta": etiqueta.group(3).strip(),
            "script": scripts[0] if scripts else None,
            "mode": None,
            "aliases": _aliases(scripts[0] if scripts else "", etiqueta.group(3)),
        })
    if not registros:
        raise LectorFallido(
            f"{path}: 0 etiquetas `[N/M]` emparejadas con un `def _check_*`; "
            "la fuente de verdad no se puede leer (no es 'sin hallazgos')"
        )

    # Modo segun el sitio de la invocacion dentro de run_all.
    quick, completo = set(), set()
    en_run_all = False
    despues_del_guard = False
    for linea in lineas:
        if re.match(r"^\s*def run_all\b", linea):
            en_run_all, despues_del_guard = True, False
            continue
        if en_run_all and re.match(r"^    def \w", linea):
            en_run_all = False
            continue
        if en_run_all:
            if re.search(r"if not self\.quick", linea):
                despues_del_guard = True
            for m in re.finditer(r"self\.(_check_[A-Za-z0-9_]+)\(\)", linea):
                (completo if despues_del_guard else quick).add(m.group(1))
    if not quick and not completo:
        raise LectorFallido(
            f"{path}: no se encontro el cuerpo de `def run_all` con sus llamadas "
            "`self._check_*()`; el modo (quick/full) no se puede derivar de la fuente"
        )
    for r in registros:
        r["mode"] = "quick" if r["emisor"] in quick else "full"
    return registros


def cargar_fuente_hook(path: Path) -> list:
    """`[{script, ordinal, total, etiqueta, emisor, aliases}]` desde la cabecera del hook."""
    lineas = _leer(path, "fuente del hook").splitlines()
    registros = []
    for i, linea in enumerate(lineas):
        m = HOOK_STEP_RE.match(linea)
        if not m:
            continue
        scripts = [s for s in SCRIPT_REF_RE.findall(m.group(3)) if s not in SOURCE_FILE_NAMES]
        registros.append({
            "emisor": f"hook:{i + 1}",
            "ordinal": int(m.group(1)),
            "total": int(m.group(2)),
            "etiqueta": m.group(3).strip(),
            "script": scripts[0] if scripts else None,
            "mode": "hook",
            "aliases": _aliases(scripts[0] if scripts else "", m.group(3)),
        })
    if not registros:
        raise LectorFallido(
            f"{path}: 0 pasos `[i/n]` en la cabecera del hook; no hay fuente contra la que medir"
        )
    # El hook repite el ordinal en el comentario de seccion y en el `echo`: una sola entrada por
    # paso, y la que nombra el script gana (si no, el pool del hook quedaria aguado).
    por_ordinal = {}
    for r in registros:
        previo = por_ordinal.get(r["ordinal"])
        if previo is None or (not previo["script"] and r["script"]):
            por_ordinal[r["ordinal"]] = r
    return [por_ordinal[k] for k in sorted(por_ordinal)]


def totales_vigentes(validations: list, hook: list) -> dict:
    totales = {"hook": hook[0]["total"], "quick": None, "full": None}
    por_total = {}
    for r in validations:
        por_total.setdefault(r["total"], set()).add(r["mode"])
    if totales["hook"] is None:
        raise LectorFallido("el hook no declara su total")
    quick_t = [t for t, modos in por_total.items() if "quick" in modos]
    full_t = [t for t, modos in por_total.items() if "full" in modos]
    totales["quick"] = max(quick_t) if quick_t else None
    totales["full"] = max(full_t) if full_t else None
    if totales["quick"] is None:
        raise LectorFallido("ningun check de run_all_validations.py corre en modo quick")
    return totales


# -----------------------------------------------------------------------------------------
# Poblacion: instancias de los documentos de gobierno, con su clausula y su bloque
# -----------------------------------------------------------------------------------------

def _bloques(texto: str):
    """(linea, columna, bloque) por instancia `[N/M]` y por forma «check N».

    Un bloque es el run de lineas consecutivas no vacias: asi la ventana de sujeto no salta
    de un parrafo a otro (saltarla fue como el changelog casi fabrica un hallazgo falso).
    """
    lineas = texto.splitlines()
    id_bloque, bloques = [], []
    actual = None
    for i, linea in enumerate(lineas):
        if linea.strip() == "":
            actual = None
            id_bloque.append(None)
            continue
        if actual is None:
            actual = len(bloques)
            bloques.append([])
        bloques[actual].append((i + 1, linea))
        id_bloque.append(actual)
    out = []
    for i, linea in enumerate(lineas):
        b = id_bloque[i]
        if b is None:
            continue
        for m in BRACKET_RE.finditer(linea):
            out.append({
                "forma": "bracket", "ordinal": int(m.group(1)), "total": int(m.group(2)),
                "linea": i + 1, "col": m.start(), "raw": m.group(0), "bloque": b,
            })
        for m in CHECK_N_RE.finditer(linea):
            out.append({
                "forma": "check_n", "ordinal": int(m.group(1)), "total": None,
                "linea": i + 1, "col": m.start(), "raw": m.group(0), "bloque": b,
            })
    return bloques, out


def _plano(bloque: list, inst: dict) -> tuple:
    """(texto del bloque, offset plano de la instancia) — todo ventana se mide aqui."""
    texto = "\n".join(l for _, l in bloque)
    for n, (ln, _) in enumerate(bloque):
        if ln == inst["linea"]:
            return texto, sum(len(l) + 1 for _, l in bloque[:n]) + inst["col"]
    return texto, None


def _segmento(texto: str, cursor, len_raw: int) -> str:
    """Clausula propia de la instancia: el tramo entre separadores `. ; :` mas cercanos."""
    if cursor is None:
        return texto[:400]
    inicio = max((texto.rfind(s, 0, cursor) for s in ".;:"), default=-1)
    fines = [f for f in (texto.find(s, cursor + len_raw) for s in ".;:") if f != -1]
    fin = min(fines) if fines else len(texto)
    return texto[inicio + 1:fin]


def _ventana(texto: str, cursor, len_raw: int, atras: int, adelante: int) -> tuple:
    """(recorte, posicion de la instancia dentro del recorte)."""
    if cursor is None:
        return "", 0
    inicio = max(0, cursor - atras)
    fin = min(len(texto), cursor + adelante + len_raw)
    return texto[inicio:fin], cursor - inicio


def _linea_de_versiones(texto: str) -> int:
    for i, linea in enumerate(texto.splitlines()):
        if CHANGELOG_HEADER_RE.match(linea):
            return i + 1
    return len(texto.splitlines()) + 1


def _frase_de_amparo(texto: str) -> str:
    """La frase del propio objeto auditado que declara las menciones historicas literales."""
    for m in re.finditer(r"[^.]*menciones[^.]{0,20}hist.{0,2}ricas[^.]*\.[^.]*\.", texto):
        return m.group(0).strip()
    return ""


# -----------------------------------------------------------------------------------------
# Guards (cada mutante de AC4 se afirma sobre uno de estos simbolos reales)
# -----------------------------------------------------------------------------------------

def es_mencion_historica(inst: dict, segmento: str, dentro_changelog: bool,
                         totales: dict) -> tuple:
    """Clase CONGELADA. Dos rutas, ambas publicadas con la marca que la disparo."""
    vigentes = {t for t in totales.values() if t is not None}
    if dentro_changelog and inst["total"] is not None and inst["total"] not in vigentes:
        return True, ("H1-denominador-de-otra-epoca-dentro-de-##-Versiones",
                      f"total afirmado {inst['total']} no esta entre {sorted(vigentes)}")
    for marca in HISTORICAL_EVENT_MARKERS:
        if marca in segmento:
            return True, ("H2-clausula-propia-narra-un-evento-pasado", marca)
    return False, (None, None)


def marcador_mas_cercano(texto: str, lado: str):
    """`lado` = 'after' busca el marcador mas cercano despues; 'before' el mas cercano antes."""
    mejor, mejor_d = None, None
    for kind, patrones in KIND_MARKERS.items():
        for p in patrones:
            if lado == "after":
                d = texto.find(p)
                if d == -1:
                    continue
            else:
                if p not in texto:
                    continue
                d = len(texto) - (texto.rfind(p) + len(p))
            if mejor_d is None or d < mejor_d:
                mejor, mejor_d = kind, d
    return mejor


def modo_de_la_instancia(texto: str, cursor, len_raw: int) -> str:
    """`hook` / `quick` / `full` / ''.

    Primero el marcador mas cercano DESPUES de la instancia; si no hay ninguno antes del fin del
    bloque, el mas cercano ANTES. Sin este orden, el `[10/10]` del template se leia como
    afirmacion del hook porque «del hook» cae 33 caracteres antes y «--quick» 38 despues — y A4
    es justamente una afirmacion sobre el quick.
    """
    if cursor is None:
        return ""
    return (marcador_mas_cercano(texto[cursor + len_raw:], "after")
            or marcador_mas_cercano(texto[:cursor], "before") or "")


def ordinal_discrepa(claimed: int, record: dict) -> bool:
    """Guard de ordinal (A2, y A3 por esta via): el ordinal afirmado no es el que imprime el codigo."""
    return claimed != record["ordinal"]


def total_discrepa(claimed: int, record_total: int) -> bool:
    """Guard de denominador (A4): el total afirmado no es el que imprime el codigo."""
    return claimed != record_total


def check_n_discrepa(claimed: int, record: dict) -> bool:
    """Guard de la forma «check N» (sin denominador): A1 y su segunda ocurrencia."""
    return claimed != record["ordinal"]


def forma_de_hook_ok(ordinal: int, total, hook_total: int) -> bool:
    """«[6/7] del hook» afirma la forma del hook (sus N pasos), no la identidad de un check.

    Sin denominador afirmado (forma «check N») solo se puede exigir que el ordinal caiga dentro
    del hook: exigirle mas seria inventar una fuente que el texto no declara.
    """
    if total is not None and total != hook_total:
        return False
    return 1 <= ordinal <= hook_total


def sujeto_de_la_instancia(ventana: str, ancla: int, pool: list) -> dict:
    """El verificador nombrado en la ventana, o —solo si no hay nombre explicito— un alias unico.

    Se ignoran los nombres de archivo que son la fuente de verdad (`run_all_validations.py`), y
    los scripts que no pertenecen al pool de la fuente resuelta: `install_git_hooks.py` aparece
    a 95 caracteres de un `[6/7]` y no es un check de nadie.
    """
    candidatas = []
    for r in pool:
        if not r["script"]:
            continue
        for m in re.finditer(re.escape(r["script"]), ventana):
            candidatas.append((abs(m.start() - ancla), r))
            break
    if candidatas:
        return min(candidatas)[1]
    por_alias = {}
    for r in pool:
        for a in r["aliases"]:
            if len(a) >= 5 and re.search(
                r"(?<![A-Za-z0-9_\-])" + re.escape(a) + r"(?![A-Za-z0-9_\-])", ventana.lower()
            ):
                por_alias[id(r)] = r
                break
    unicos = {r["ordinal"]: r for r in por_alias.values()}
    if len(unicos) == 1:
        return list(unicos.values())[0]
    if len(unicos) > 1:
        raise LectorFallido(
            "dos verificadores de la misma fuente reivindican la misma asercion por alias "
            f"({sorted(r['script'] or r['emisor'] for r in unicos.values())}): adivinar cual es "
            "el sujeto daria un hallazgo falso; se declara el fallo de lectura (R2.9)"
        )
    return None


# -----------------------------------------------------------------------------------------
# Analisis
# -----------------------------------------------------------------------------------------

def analizar(governance: list, source: Path, hook_path: Path) -> dict:
    validations = cargar_fuente_validations(source)
    hook = cargar_fuente_hook(hook_path)
    totales = totales_vigentes(validations, hook)
    pool_quick = [r for r in validations if r["mode"] == "quick"]
    pool_full = validations

    findings_by_key = {}
    checked, historical, unresolved = [], [], []
    docs_scan = []

    for idx, doc in enumerate(governance):
        texto = _leer(doc["path"], f"documento de gobierno {doc['name']}")
        bloques, instancias = _bloques(texto)
        linea_changelog = _linea_de_versiones(texto)
        amparo = _frase_de_amparo(texto)
        docs_scan.append({
            "document": doc["path"].as_posix(),
            "nombre": doc["name"],
            "bytes": doc["path"].stat().st_size,
            "instancias_bracket": sum(1 for i in instancias if i["forma"] == "bracket"),
            "instancias_check_n": sum(1 for i in instancias if i["forma"] == "check_n"),
            "lineas_con_instancias": len({i["linea"] for i in instancias}),
            "orden_de_escaneo": idx,
        })
        if not instancias and texto.strip():
            raise LectorFallido(
                f"{doc['path']}: documento no vacio con 0 instancias de conteo; o el patron "
                "no aplica o la lectura es parcial (R2.9: vacio != ausente)"
            )

        for inst in sorted(instancias, key=lambda i: (i["linea"], i["col"])):
            bloque = bloques[inst["bloque"]]
            bloque_texto, cursor = _plano(bloque, inst)
            len_raw = len(inst["raw"])
            segmento = _segmento(bloque_texto, cursor, len_raw)
            ventana, ancla = _ventana(bloque_texto, cursor, len_raw, 300, 200)
            dentro_cl = (
                inst["linea"] >= linea_changelog
                and any(CHANGELOG_ENTRY_RE.match(l) for _, l in bloque)
            )
            congelada, regla = es_mencion_historica(inst, segmento, dentro_cl, totales)
            ubicacion = {
                "document": doc["path"].as_posix(),
                "linea": inst["linea"],
                "columna": inst["col"] + 1,
                "texto_afirmado": inst["raw"],
                "segmento": segmento.strip(),
            }
            if congelada:
                historical.append({
                    **ubicacion,
                    "clase": "CONGELADA-historica",
                    "regla": regla[0],
                    "marca": regla[1],
                    "authorized_by": amparo or "sin frase de amparo encontrada en el documento",
                })
                continue

            modo = modo_de_la_instancia(bloque_texto, cursor, len_raw)
            if modo == "hook":
                ok = forma_de_hook_ok(inst["ordinal"], inst["total"], totales["hook"])
                registro = {"ordinal": inst["ordinal"], "total": totales["hook"],
                            "script": None, "emisor": "hook (forma)", "mode": "hook"}
                razones = [] if ok else ["forma-del-hook"]
                fuente = f"hook de {totales['hook']} pasos"
                observado = f"hook:[{inst['ordinal']}/{totales['hook']}]"
            else:
                pool = pool_quick if modo == "quick" else pool_full
                record = sujeto_de_la_instancia(ventana, ancla, pool) if modo else None
                if record is None:
                    unresolved.append({
                        **ubicacion, "clase": "NO-RESUELTA",
                        "motivo": ("la instancia no declara fuente (--quick/hook/completo)"
                                   if not modo else
                                   f"fuente {modo} pero ningun verificador nombrado ni alias unico "
                                   "aparece en la ventana"),
                    })
                    continue
                fuente = (f"{record['script']} imprime [{record['ordinal']}/{record['total']}]"
                          f" ({record['mode']}) via {record['emisor']}")
                razones = []
                if inst["forma"] == "check_n":
                    if check_n_discrepa(inst["ordinal"], record):
                        razones.append("ordinal")
                else:
                    if ordinal_discrepa(inst["ordinal"], record):
                        razones.append("ordinal")
                    if total_discrepa(inst["total"], record["total"]):
                        razones.append("denominador")
                registro = record
                observado = f"[{record['ordinal']}/{record['total']}]"

            claimed = (f"[{inst['ordinal']}/{inst['total']}]" if inst["forma"] == "bracket"
                       else f"check {inst['ordinal']}")
            entrada = {
                "document": doc["path"].as_posix(),
                "nombre_documento": doc["name"],
                "orden_documento": idx,
                "observed_ordinal": registro["ordinal"] if registro["script"] else None,
                "claimed": claimed,
                "observed": observado,
                "subject": registro["script"] or "(forma del hook)",
                "source_kind": modo or "(hook)",
                "fuente": fuente,
                "emisor_del_codigo": registro["emisor"],
                "razones": razones,
                "ocurrencia": ubicacion,
            }
            if razones:
                clave = (entrada["document"], entrada["claimed"], entrada["subject"], modo)
                findings_by_key.setdefault(clave, entrada)
                findings_by_key[clave]["ocurrencia_line"] = ubicacion["linea"]
                findings_by_key[clave].setdefault("occurrences", []).append(ubicacion)
                findings_by_key[clave]["reasons"] = sorted(
                    set(findings_by_key[clave].get("reasons", [])) | set(razones))
            else:
                checked.append({**entrada, "clase": "VIGENTE-CORRECTA"})

    ordenados = sorted(findings_by_key.values(),
                       key=lambda f: (f["orden_documento"], f["observed_ordinal"] or 0,
                                      f["ocurrencia_line"], f["claimed"]))
    hallazgos = []
    for n, f in enumerate(ordenados, start=1):
        hallazgos.append({
            "assertion_id": f"A{n}",
            # `assertion_id` es POSICIONAL (reproduce la numeracion A1-A4 del maestro §1) y por
            # tanto se re-numera si un hallazgo desaparece. Todo anclaje de mutante o de contract
            # test tiene que mirar esta clave de contenido, que no se mueve (L-V2.1, medida en
            # el mutation check de esta misma fase).
            "assertion_key": (f"{f['subject']}|{f['claimed']}|{f['nombre_documento']}"),
            "document": f["document"],
            "claimed": f["claimed"],
            "observed": f["observed"],
            "subject": f["subject"],
            "source_kind": f["source_kind"],
            "fuente": f["fuente"],
            "emisor_del_codigo": f["emisor_del_codigo"],
            "class": "VIVA-normativa",
            "reasons": f.get("reasons", []),
            "occurrences": f["occurrences"],
        })

    informe = {
        "tool": "scripts/validate_governance_numbers.py",
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": "HALLAZGOS" if hallazgos else "SIN-HALLAZGOS",
        "findings": hallazgos,
        "assertions_checked": [
            {"assertion": c["claimed"], "observed": c["observed"], "document": c["document"],
             "subject": c["subject"], "source_kind": c["source_kind"], "fuente": c["fuente"]}
            for c in checked
        ],
        "historical_excluded": historical,
        "unresolved": unresolved,
        "coverage_basis": {
            "documents_scanned": docs_scan,
            "fuentes": {
                "quick": {"path": source.as_posix(), "total": totales["quick"],
                          "checks": [f"{r['script'] or r['emisor']}=[{r['ordinal']}/{r['total']}]"
                                     for r in validations if r["mode"] == "quick"]},
                "solo_completo": {"total": totales["full"],
                                  "checks": [f"{r['script'] or r['emisor']}=[{r['ordinal']}/{r['total']}]"
                                             for r in validations if r["mode"] != "quick"]},
                "hook": {"path": hook_path.as_posix(), "total": totales["hook"],
                         "steps": [f"{r['script'] or r['etiqueta']}=[{r['ordinal']}/{r['total']}]"
                                   for r in hook]},
            },
            "poblacion": {
                "instancias_totales": sum(d["instancias_bracket"] + d["instancias_check_n"]
                                          for d in docs_scan),
                "clase_viva_con_hallazgo": sum(len(h["occurrences"]) for h in hallazgos),
                "aserciones_de_hallazgo": len(hallazgos),
                "clase_viva_correcta": len(checked),
                "clase_historica_congelada": len(historical),
                "clase_no_resuelta": len(unresolved),
            },
            "regla_de_poblacion": {
                "fuente": "maestro §1 medicion A8 del plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20",
                "clases": ["VIVA-normativa", "CONGELADA-historica", "VIGENTE-CORRECTA"],
                "historica_H1": "instancia dentro de una entrada `- **vX.Y.Z**` de `## Versiones` "
                                "cuyo denominador no es ninguno de los totales vigentes",
                "historica_H2": "la clausula propia narra un evento pasado de medicion "
                                f"(marcadores: {list(HISTORICAL_EVENT_MARKERS)})",
                "historical_authorizing_phrase": next((h["authorized_by"] for h in historical), ""),
                "hallazgo_por_asercion_no_por_linea": True,
                "assertion_id_derivation": "hallazgos ordenados por (orden de documento escaneado, "
                                           "ordinal observado del check, linea): reproduce la "
                                           "numeracion A1-A4 del maestro §1 sin pinearla",
            },
            "families_not_covered": [],
            "excluded": [],
            "comando": "python scripts/validate_governance_numbers.py --report",
            "medido_el": datetime.now().strftime("%Y-%m-%d"),
        },
    }
    informe["coverage_basis"]["families_not_covered"] = cobertura_de_familias(
        ROOT, informe["coverage_basis"]["poblacion"])
    informe["coverage_basis"]["excluded"] = documentos_excluidos(ROOT)
    if informe["status"] == "SIN-HALLAZGOS" and not denominador_completo(informe["coverage_basis"]):
        raise LectorFallido("no se puede emitir SIN-HALLAZGOS sin coverage_basis completa (L-R.3)")
    return informe


def denominador_completo(basis: dict) -> bool:
    needed = ("documents_scanned", "fuentes", "poblacion", "regla_de_poblacion",
              "families_not_covered", "excluded", "comando", "medido_el")
    return all(basis.get(k) for k in needed)


def cobertura_de_familias(root: Path, poblacion: dict) -> list:
    """Las cuatro familias de AC2, medidas en runtime (no enumeradas «de oido»)."""
    gov = [root / ".agents" / "workflows" / "phased_project_executor.md",
           root / ".agents" / "workflows" / "templates" / "lecciones-capitalizadas-template.md"]
    fuera = [root / "AGENTS.md", root / "docs" / "GUIA_TECNICA.md",
             root / "docs" / "contributing" / "REGISTRY.md"]
    prose, fuera_hits = [], []
    for d in gov:
        if not d.exists():
            continue
        # Familia (i): lo que queda DESPUES de quitar los patrones ya auditados — si no, cada
        # `[7/7]` contaria dos veces y el denominador mentiria.
        sin_brackets = BRACKET_RE.sub(" ", _leer(d, "documento de gobierno"))
        for m in PROSA_RE.finditer(sin_brackets):
            prose.append({"document": d.name, "texto": m.group(0).strip()})
    for d in fuera:
        if not d.exists():
            continue
        t = _leer(d, "documento fuera de alcance")
        hits = [m.group(0).strip() for m in PROSA_RE.finditer(BRACKET_RE.sub(" ", t))]
        hits += [f"[{a}/{b}]" for a, b in BRACKET_RE.findall(t)]
        hits += ["check " + c for c in re.findall(r"\bcheck (\d+)\b", t)]
        if hits:
            fuera_hits.append({"document": d.as_posix(), "instancias": len(hits),
                               "ejemplos": hits[:4]})
    tests_dir = root / "tests"
    pins = []
    if tests_dir.is_dir():
        for py in sorted(tests_dir.rglob("*.py")):
            try:
                t = py.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            n = len(BRACKET_RE.findall(t))
            if n:
                pins.append({"archivo": py.as_posix(), "instancias": n,
                             "etiquetas": sorted({f"{a}/{b}" for a, b in BRACKET_RE.findall(t)})})
    funcs = 0
    if tests_dir.is_dir():
        for py in tests_dir.rglob("*.py"):
            funcs += len(re.findall(r"^\s*def test_", py.read_text(
                encoding="utf-8", errors="replace"), flags=re.M))
    return [
        {
            "familia": FAMILIES_NOT_COVERED[0],
            "que_es": "prosa de conteo sin patron `[N/M]` ni «check N» (p. ej. «11 checks», "
                      "«once validaciones», «pasa 4/4» en texto corrido)",
            "medicion": {"archivos_mirados": [d.name for d in gov], "coincidencias": len(prose),
                         "ejemplos": prose[:4]},
            "comando": "grep -roE '[0-9]+ (checks|validaciones|pasos)' .agents/workflows/"
                       "phased_project_executor.md",
            "estado": "trabajo D1 (lint de prosa) — limite declarado de FASE-A",
        },
        {
            "familia": FAMILIES_NOT_COVERED[1],
            "que_es": "aserciones de conteo FUERA de los documentos de gobierno: AGENTS.md, "
                      "docs/GUIA_TECNICA.md, docs/contributing/REGISTRY.md",
            "medicion": {"archivos_mirados": [h["document"] for h in fuera_hits],
                         "instancias": sum(h["instancias"] for h in fuera_hits),
                         "por_archivo": fuera_hits},
            "comando": "grep -rcE '\\[[0-9]+/[0-9]+\\]|check [0-9]+' AGENTS.md "
                       "docs/GUIA_TECNICA.md docs/contributing/REGISTRY.md",
            "estado": "fuera del alcance de este plan (maestro §3); D1 decide",
        },
        {
            "familia": FAMILIES_NOT_COVERED[2],
            "que_es": "pins de conteo en tests/ (un test que assertiona un ordinal del hook o "
                      "del quick se rompe al renumerar, y hoy no lo mira ningun verificador)",
            "medicion": {"archivos_con_pines": len(pins), "poblacion": pins},
            "comando": "grep -rnE '\\[[0-9]+/[0-9]+\\]' tests/ --include=*.py",
            "estado": "barrido por AC5/AC16 de esta fase (quien afirma el 11 y el 7); "
                     "cubrirlo con el verificador es D1",
        },
        {
            "familia": FAMILIES_NOT_COVERED[3],
            "que_es": "toda fuente dinamica que no sea una etiqueta impresa: umbrales, tamano "
                      "de corpus, conteo de funciones de test",
            "medicion": {"funciones_test_en_disk": funcs,
                         "ejemplo_vencido": "AGENTS.md publica 4.246 funciones canonicas; "
                                            "la resta en disk da otra cifra"},
            "comando": "grep -rE '^\\s*def test_' tests --include=*.py | wc -l",
            "estado": "limite permanente de este verificador (solo contrasta conteos de checks)",
        },
    ]


def documentos_excluidos(root: Path) -> list:
    """Que quedo fuera de la poblacion mirada y por que (AC2: exenciones, no silencio)."""
    excluidos = []
    for nombre in ("prompt-fase-template.md",):
        p = root / ".agents" / "workflows" / "templates" / nombre
        if not p.exists():
            continue
        texto = _leer(p, "template excluido")
        excluidos.append({
            "documento": p.as_posix(),
            "instancias_detectadas": len(BRACKET_RE.findall(texto)) + len(CHECK_N_RE.findall(texto)),
            "motivo": "el maestro §1 declara objetos auditados solo dos: el workflow canonico y "
                      "su template de lecciones; este template vive en el mismo directorio y se "
                      "mide aqui para que la exclusion no sea silencio",
            "evidencia_prosa": [m.group(0) for m in
                                re.finditer(r"pasa \d+/\d+", texto)][:3],
        })
    excluidos.append({
        "documento": ".agents/workflows/** (restante)",
        "instancias_detectadas": None,
        "motivo": "el plan fija como poblacion los dos documentos de gobierno; el resto de "
                  ".agents/ no se escribe ni se audita en FASE-A (AC17)",
    })
    return excluidos


# -----------------------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------------------

def _linea_cobertura(informe: dict) -> str:
    p = informe["coverage_basis"]["poblacion"]
    f = informe["coverage_basis"]["fuentes"]
    return (
        f"poblacion: {p['instancias_totales']} instancia(s) | viva-hallazgo "
        f"{p['clase_viva_con_hallazgo']} en {p['aserciones_de_hallazgo']} asercion(es) | "
        f"viva-correcta {p['clase_viva_correcta']} | historica-congelada "
        f"{p['clase_historica_congelada']} | no-resuelta {p['clase_no_resuelta']} || "
        f"fuentes: quick {f['quick']['total']} checks | solo-completo "
        f"{len(f['solo_completo']['checks'])} (total {f['solo_completo']['total']}) | "
        f"hook {f['hook']['total']} pasos || familias no cubiertas: "
        f"{len(informe['coverage_basis']['families_not_covered'])}"
    )


def _estado_a_imprimir(informe: dict) -> str:
    """La marca de estado que ve un consumidor: ASCII estable, sin depender del resto de la linea.

    No es un defecto arreglado sobre la marcha: es el contrato que fija la prueba
    `test_marca_de_estado_en_ascii`, para que quien lea la consola o
    un log pueda buscar el estado sin acertar con los acentos del texto que lo sigue.
    """
    return "SIN-HALLAZGOS" if informe["status"] == "SIN-HALLAZGOS" else "HALLAZGOS"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--governance-doc", action="append", default=None,
                    help="documento de gobierno a auditar (repetible); default: los dos del maestro")
    ap.add_argument("--source", default=str(SOURCE_DEFAULT))
    ap.add_argument("--hook", default=str(HOOK_DEFAULT))
    ap.add_argument("--report", nargs="?", const=str(REPORT_DEFAULT), default=None,
                    help="escribir el informe JSON (default: ruta de evidencia del plan)")
    ap.add_argument("--json", action="store_true", help="volcar el informe por stdout")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    if args.governance_doc:
        docs = [{"path": Path(p), "name": Path(p).stem} for p in args.governance_doc]
    else:
        docs = [{"path": p, "name": p.stem} for p in GOVERNANCE_DEFAULTS]

    try:
        faltan = [d["path"] for d in docs if not d["path"].exists()]
        for otro in (Path(args.source), Path(args.hook)):
            if not otro.exists():
                faltan.append(otro)
        if faltan:
            print("[AUSENTE] validate_governance_numbers: no se encontro la ruta buscada")
            for f in faltan:
                print(f"  - {f}")
            print("  (R2.9: AUSENTE no es 'sin hallazgos'; no se emite denominador favorable)")
            return 2
        informe = analizar(docs, Path(args.source), Path(args.hook))
    except LectorFallido as exc:
        print("[LECTOR-FALLIDO] validate_governance_numbers no pudo operar:")
        print(f"  motivo: {exc}")
        print("  (R2.9: nunca se imprime un favorable ni un 0 desde aqui)")
        return 3

    if args.report:
        destino = Path(args.report)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(informe, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    if args.json:
        print(json.dumps(informe, indent=2, ensure_ascii=False))
        return 1 if informe["findings"] else 0

    if not args.quiet:
        # La marca del estado se imprime SIN acentos: un lector (o un test) que busca
        # `SIN-HALLAZGOS` no puede encontrarla dentro de un texto acentuado.
        marca = _ascii(_estado_a_imprimir(informe))
        print(f"[{marca}] validate_governance_numbers.py - "
              "aserciones de conteo en documentos de gobierno vs etiqueta impresa por el codigo")
        print(f"  {_ascii(_linea_cobertura(informe))}")
        print(f"  {_ascii('medido ' + informe['coverage_basis']['medido_el'] + ' con: '
                          + informe['coverage_basis']['comando'])}")
        for h in informe["findings"]:
            print(f"  - {h['assertion_id']} {h['document']}:{h['occurrences'][0]['linea']} "
                  f"claimed={h['claimed']} observed={h['observed']} "
                  f"sujeto={h['subject']} razones={','.join(h['reasons'])} "
                  f"occurrences={len(h['occurrences'])}")
        if informe["unresolved"]:
            print(f"  [NO-RESUELTAS] {len(informe['unresolved'])} instancia(s) sin fuente "
                  "resoluble (publicadas, no recortadas):")
            for u in informe["unresolved"][:5]:
                print(f"    - {u['document']}:{u['linea']} {u['texto_afirmado']} — {u['motivo']}")
    return 1 if informe["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
