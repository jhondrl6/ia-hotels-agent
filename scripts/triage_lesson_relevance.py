#!/usr/bin/env python
"""triaje de pertinencia sobre el indice de lecciones — FASE-C de VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20.

`validate_lesson_capitalization.py` dice de si mismo que su `[OK]` significa «la forma exigida
esta», nunca «capitalice bien». Este script escribe la otra mitad: **si la leccion anclada en §2 era
la pertinente y cuales quedaron fuera**, y lo hace **proponiendo**, jamas filtrando (AC10).

UNICA PUERTA AL PROVEEDOR: `scripts/decision_client.py` (AC6/AC7 heredados de FASE-B). Este archivo
no importa SDK ni adapter alguno y no abre sockets.

ESTADOS DEL SUELO (R2.9 — tres causas, ninguna colapsable, AC11)
    `AUSENTE`          no hay archivo en la ruta buscada -> imprime la ruta y el comando de regeneracion
    `VENCIDO`          existe y se lee, pero **el check de frescura propio de C** no lo aprueba ->
                       imprime que diff lo vencio, el comando, y que el `[6/7]` de
                       `scripts/git_hooks/pre-commit` es el check del hook que lo detecta
    `LECTOR-FALLIDO`   existe pero revienta al parsear, o el calculo propio no pudo correr -> motivo

    Que el archivo exista no es que este fresco: la tercera via (leer el JSON confiando en que otro
    paso lo regenero) la prohibe el contrato E2, asi que C calcula el indice en memoria con el
    generador de la casa y compara contra lo que hay en disco. Coste aceptado: **dos lecturas del
    mismo JSON por corrida** (la del check y la del consumo), publicada en `lecturas_del_json_por_corrida`.

FORMA DE LA PREGUNTA (contrato E1): `choice` de **dos** opciones. El umbral de AC12 gobierna
`confidence`, que en `decision_client.RespuestaEleccion` es un campo distinto de `probabilidades`;
`RespuestaNoul` fija `confidence = None` con su motivo y la puerta la rechaza ahi, de modo que una
pregunta `noul` no podria gobernar el umbral. `por_si` se publica en cada candidato y **no** decide.

SALIDA: 0 = TRIADO · 2 = AUSENTE · 3 = LECTOR-FALLIDO · 4 = VENCIDO ·
        5 = TOPE-EXCEDIDO (el tope de coste no se resuelve recortando candidatos) ·
        6 = REVISION-INCOMPLETA (una decision humana sin quien/fecha/motivo no se aplica) ·
        7 = EMISOR-NO-CONFIGURADO (suelo fresco y puerta sin proveedor: NO es «sin candidatos»)
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
DEFAULT_PLANS = ROOT / ".opencode" / "plans"
DEFAULT_CONTEXT = ROOT / ".opencode" / "context"
INDICE_JSON = ROOT / ".opencode" / "lecciones_index.json"
INDICE_MD = ROOT / ".opencode" / "LECCIONES-INDEX.md"
REGEN_COMMANDO = "python scripts/build_lesson_index.py"
CHECK_HOOK = "[6/7] de scripts/git_hooks/pre-commit (build_lesson_index.py --check)"

ESCRIBE_SECCION_DOS = False      # E3: el triaje propone; ningun camino de este script edita §2.
GUARD_ADITIVIDAD_ACTIVO = True   # AC10; el mutation check de AC14 apaga ESTE simbolo.
TECHO_LLAMADAS = 200             # techo del --report contra el proveedor FALSO; no es licencia de red.
LOTE = 20

ESTADOS_INDICE = ("FRESCO", "AUSENTE", "VENCIDO", "LECTOR-FALLIDO")
OPCIONES_PERTINENCIA = ("pertinente", "no-pertinente")
ID_LECCION_RE = re.compile(r"^(?:DA|D|L|S)-[A-Za-z0-9._-]+$")

UMBRAL = {
    "campo": "confidence",
    "value": 0.80,
    "basis": ("`confidence` de la respuesta `choice` de dos opciones que devuelve la primitiva "
              "decision_client.RespuestaEleccion: cuan seguro esta el emisor de haber leido bien la "
              "pregunta. NO es `probabilidad_si` (no existe en `choice`) ni "
              "`probabilidades['pertinente']`, que aqui se publica como `por_si` y mide cuanto se "
              "inclina por la opcion afirmativa. Son dos numeros distintos y no se equiparan."),
    "action_below": ("el candidato pasa a `a-revisar-humano` con su pregunta, su eleccion y sus dos "
                     "numeros publicados. NO se descarta, NO se borra de §2, NO se re-pregunta."),
    "fuente": "AC12 del maestro §4 + contrato E1 (orden de calidad §4.C, 2026-09-23)",
}

# Capa fria: los terminos con los que el Paso 0 buscaba en el indice. A5 y §3-D5 midieron que
# `grep -icE "verificador mec"` devuelve 0 sobre un corpus que si contiene verificadores nombrados
# con otras palabras, y un cero de grep no distingue «no existe» de «termine equivocado». Se publican
# con su conteo, ceros incluidos (AC15): son la evidencia del limite, no un filtro.
TERMINOS_CAPA_FRIA = (
    "verificador mec", "pertinencia", "denominador", "cobertura medida",
    "falso verde", "fosiliz", "renumer", "capa fria", "triaje", "lecciones capitalizadas",
)

_CARGAS = 0


def _cargar_por_ruta(path: Path):
    """Carga un modulo del repo por ruta, con nombre unico por carga (los mutantes no heredan sys.modules)."""
    global _CARGAS
    _CARGAS += 1
    spec = importlib.util.spec_from_file_location(f"trl_dep_{_CARGAS}_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"no se pudo construir el spec de {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _decision_client():
    return _cargar_por_ruta(SCRIPTS / "decision_client.py")


def _generador():
    return _cargar_por_ruta(SCRIPTS / "build_lesson_index.py")


class SueloNoLeible(Exception):
    """El suelo determinista no esta en condiciones de sostener ninguna conclusion (AC11)."""

    def __init__(self, estado: str, payload: dict):
        super().__init__(f"{estado}: {payload.get('motivo')}")
        self.estado = estado
        self.payload = payload


class TopeExcedido(RuntimeError):
    """Se alcanzo el techo de llamadas sin triar el pool: el recorte silencioso esta prohibido."""


class EmisorNoConfigurado(Exception):
    """`decision_client` no resuelve ningun emisor: se publica NO-CONFIGURADO, jamas «sin candidatos»."""

    def __init__(self, motivo_clase: str, motivo: str, buscado: dict | None = None):
        super().__init__(motivo)
        self.motivo_clase = motivo_clase
        self.motivo = motivo
        self.buscado = buscado or {}


# --------------------------------------------------------------------------------------------
# AC11 — el suelo, con el check de frescura propio de C (E2, ruta b)
# --------------------------------------------------------------------------------------------

def _motivo(exc: Exception) -> str:
    return f"{type(exc).__name__}: {exc}"


def comprobar_frescura(ruta_json: Path = INDICE_JSON,
                       plans_dir: Path = DEFAULT_PLANS,
                       context_dir: Path | None = DEFAULT_CONTEXT) -> dict:
    """El check de C: calcula el indice en memoria con el generador de la casa y compara con el disco.

    No invoca `build_lesson_index.py --check` ni confia en que `[6/7]` del hook lo regenero: ejecuta
    la misma comprobacion por su cuenta, y su coste es la segunda lectura del JSON.
    """
    base = {"ruta_buscada": str(ruta_json), "comando_regeneracion": REGEN_COMMANDO,
            "check_del_hook_que_lo_detecta": CHECK_HOOK, "ejecutado_por": "triage_lesson_relevance"}
    if not ruta_json.exists():
        return {**base, "index_status": "AUSENTE",
                "motivo": f"no hay archivo en {ruta_json}",
                "nota": "AUSENTE no es «sin candidatos» ni «fresco» (L-PF10)"}
    try:
        disco_texto = ruta_json.read_text(encoding="utf-8")
    except Exception as exc:
        return {**base, "index_status": "LECTOR-FALLIDO",
                "motivo": f"el archivo existe pero no se pudo leer: {_motivo(exc)}"}
    try:
        disco = json.loads(disco_texto)
    except Exception as exc:
        return {**base, "index_status": "LECTOR-FALLIDO",
                "motivo": f"el archivo existe pero no es JSON legible: {_motivo(exc)}"}
    if not isinstance(disco, dict) or not isinstance(disco.get("lecciones"), list):
        return {**base, "index_status": "LECTOR-FALLIDO",
                "motivo": ("el JSON se parseo pero no tiene la forma del indice (dict con `lecciones` "
                           f"en lista): {type(disco).__name__} — no se lee como ausencia")}
    try:
        generador = _generador()
        index, coverage = generador.build(plans_dir, context_dir)
        esperado = generador.render_json(index, coverage)
    except Exception as exc:
        return {**base, "index_status": "LECTOR-FALLIDO", "subcausa": "calculo-en-memoria",
                "motivo": ("el calculo propio del indice no pudo correr, asi que no hay base ni para "
                           f"afirmar frescura ni para afirmar vencimiento: {_motivo(exc)}")}
    if esperado == disco_texto:
        return {**base, "index_status": "FRESCO", "motivo": None,
                "ids_con_definicion": coverage["ids_con_definicion"]}
    try:
        esperado_dict = json.loads(esperado)
    except Exception as exc:
        return {**base, "index_status": "LECTOR-FALLIDO",
                "motivo": f"el calculo propio no produjo JSON legible: {_motivo(exc)}"}
    ids_disco = {l.get("id") for l in disco.get("lecciones", [])}
    ids_calculo = {l.get("id") for l in esperado_dict.get("lecciones", [])}
    cob_disco = disco.get("cobertura", {})
    cob_calculo = esperado_dict.get("cobertura", {})
    return {**base, "index_status": "VENCIDO", "motivo": "el disco y el calculo propio difieren",
            "diff": {"solo_en_disco": sorted(ids_disco - ids_calculo),
                     "solo_en_el_calculo": sorted(ids_calculo - ids_disco),
                     "cobertura_distinta": {
                         k: {"disco": cob_disco.get(k), "calculo": cob_calculo.get(k)}
                         for k in sorted(set(cob_disco) | set(cob_calculo))
                         if cob_disco.get(k) != cob_calculo.get(k)},
                     "sha256_disco": hashlib.sha256(disco_texto.encode("utf-8")).hexdigest()[:16],
                     "sha256_calculo": hashlib.sha256(esperado.encode("utf-8")).hexdigest()[:16]}}


def leer_suelo(ruta_json: Path = INDICE_JSON, **kw) -> tuple[dict, dict]:
    """Devuelve (indice, estado). Un lector roto jamas devuelve «sin candidatos» (L-PF6)."""
    estado = comprobar_frescura(ruta_json, **kw)
    if estado["index_status"] != "FRESCO":
        raise SueloNoLeible(estado["index_status"], estado)
    with ruta_json.open(encoding="utf-8") as fh:      # segunda lectura: el coste declarado de (b)
        return json.load(fh), estado


# --------------------------------------------------------------------------------------------
# §2 del plan: las filas que no pueden desaparecer (AC10)
# --------------------------------------------------------------------------------------------

def _celdas(linea: str) -> list[str]:
    texto = linea.strip()
    if not texto.startswith("|"):
        return []
    partes = [c.strip() for c in re.split(r"(?<!\\)\|", texto)]
    return [p for p in partes[1:-1]] if len(partes) > 2 else []


def _limpiar(texto: str) -> str:
    return re.sub(r"\s+", " ", (texto or "").replace("**", "").replace("`", "")).strip()


def seccion_dos(texto: str) -> str | None:
    lineas = texto.splitlines()
    inicio = None
    for i, linea in enumerate(lineas):
        if re.match(r"^##\s+2[\s.]", linea):
            inicio = i
        elif inicio is not None and re.match(r"^##\s+\d", linea):
            return "\n".join(lineas[inicio:i])
    return "\n".join(lineas[inicio:]) if inicio is not None else None


def filas_ancladas(ruta_lecciones: Path) -> list[dict]:
    """Las filas de §2 del plan: id, enunciado y fila literal. Se leen; nunca se reescriben."""
    try:
        texto = ruta_lecciones.read_text(encoding="utf-8")
    except Exception as exc:
        raise SueloNoLeible("AUSENTE", {"ruta_buscada": str(ruta_lecciones),
                                        "motivo": f"el documento de lecciones no se pudo leer: {_motivo(exc)}"})
    seccion = seccion_dos(texto)
    if seccion is None:
        raise SueloNoLeible("LECTOR-FALLIDO", {
            "ruta_buscada": str(ruta_lecciones),
            "motivo": "el documento no tiene una seccion «## 2.» legible: no se puede afirmar que "
                      "no haya filas ancladas"})
    filas = []
    for linea in seccion.splitlines():
        celdas = _celdas(linea)
        if len(celdas) < 2:
            continue
        id_celda = _limpiar(celdas[0])
        if not ID_LECCION_RE.match(id_celda) or id_celda in ("ID",):
            continue
        filas.append({"id": id_celda, "enunciado": _limpiar(celdas[1]), "fila": linea})
    if not filas:
        raise SueloNoLeible("LECTOR-FALLIDO", {
            "ruta_buscada": str(ruta_lecciones),
            "motivo": "§2 existe pero no se leyo ninguna fila con ID de leccion: un vacio leido por "
                      "un lector que no coincide no es una ausencia (L-PF10)"})
    return filas


# --------------------------------------------------------------------------------------------
# AC10 — la aditividad, y el unico simbolo que la sostiene
# --------------------------------------------------------------------------------------------

def guardar_filas_ancladas(anteriores: list[dict], propuesta: list[dict]) -> tuple[list[dict], list[str]]:
    """Guard de no-filtrado. Apagado, devuelve `propuesta` tal cual: ahi es donde la fila desaparece.

    Con el guard activo la seccion vuelve **intacta** y la intencion de filtro queda publicada como
    `intentos_filtrados`: cuestionar una fila y borrarla son dos cosas distintas, y la segunda es la
    que este plan prohibe (maestria §2, `VACUOUS_RECALL`).
    """
    intentos = [f["id"] for f in anteriores if f not in propuesta]
    if not GUARD_ADITIVIDAD_ACTIVO:
        return list(propuesta), intentos
    if intentos:
        return list(anteriores) + [f for f in propuesta if f not in anteriores], intentos
    return list(propuesta), []


# --------------------------------------------------------------------------------------------
# candidatos: lo que el Paso 0 toco y no anclo
# --------------------------------------------------------------------------------------------

def nombres_del_plan(plan: str) -> list[str]:
    base = Path(plan).name
    return [base, f"Archives/{base}"]


def resolver_plan(plan: str, plans_dir: Path = DEFAULT_PLANS) -> Path:
    buscadas = [plans_dir / plan, plans_dir / "Archives" / Path(plan).name, Path(plan)]
    for c in buscadas:
        if c.is_dir() and (c / "00-lecciones-capitalizadas.md").is_file():
            return c
    raise SueloNoLeible("AUSENTE", {
        "ruta_buscada": " | ".join(str(c) for c in buscadas),
        "motivo": f"el plan {plan!r} no esta en ninguna de las rutas buscadas",
        "comando_regeneracion": REGEN_COMMANDO})


def candidatos_de_pertinencia(indice: dict, plan: str, ancladas: list[dict]) -> list[dict]:
    """IDs que el plan define o cita y que §2 no anclo: el pool que el Paso 0 dejo fuera."""
    nombres = nombres_del_plan(plan)
    anclados = {f["id"] for f in ancladas}
    pool: dict[str, dict] = {}
    for leccion in indice.get("lecciones", []):
        citado = any(n in (leccion.get("planes_que_lo_citan") or []) for n in nombres)
        definido = leccion.get("plan") in nombres
        if not (citado or definido) or leccion["id"] in anclados:
            continue
        pool[leccion["id"]] = {
            "id": leccion["id"], "familia": leccion.get("familia"),
            "enunciado": leccion.get("enunciado"), "plan_dueno": leccion.get("plan"),
            "archivo": leccion.get("archivo"), "total_citas": leccion.get("total_citas"),
            "definido_por_el_plan": definido, "citado_por_el_plan": citado,
            "tipo_fila": "pendiente"}
    for cit in indice.get("citados_sin_definicion", []):
        cid = cit.get("id")
        if cid in anclados or cid in pool:
            continue
        if not any(n in (cit.get("planes_que_lo_citan") or []) for n in nombres):
            continue
        pool[cid] = {"id": cid, "familia": cit.get("familia"), "enunciado": None,
                     "plan_dueno": None, "archivo": None, "total_citas": cit.get("total_citas"),
                     "definido_por_el_plan": False, "citado_por_el_plan": True,
                     "tipo_fila": "pendiente",
                     "nota": "citado sin definicion en el corpus: no hay enunciado que triar"}
    return [pool[k] for k in sorted(pool)]


def anclados_para_revision(ancladas: list[dict]) -> list[dict]:
    """Re-preguntar por las filas ya ancladas: «era esta la pertinente?» tambien es triaje (AC10)."""
    return [{"id": f["id"], "familia": f["id"].split("-")[0], "enunciado": f["enunciado"],
             "plan_dueno": "§2 del plan triado", "archivo": "00-lecciones-capitalizadas.md",
             "total_citas": None, "definido_por_el_plan": None, "citado_por_el_plan": True,
             "tipo_fila": "anclada"} for f in ancladas]


# --------------------------------------------------------------------------------------------
# AC12 — la pregunta binaria y el umbral, a traves de la unica puerta
# --------------------------------------------------------------------------------------------

def construir_preguntas(dc, fuentes: list[dict]) -> tuple[list, str]:
    """Un `state` con los dossiers y una `choice` de dos opciones por candidato (E1)."""
    lineas = [
        "Triaje de pertinencia del Paso 0. Para cada pregunta elija una de dos opciones:",
        f"  {OPCIONES_PERTINENCIA[0]}: la leccion debio capitalizarse en §2 del plan que se tria.",
        f"  {OPCIONES_PERTINENCIA[1]}: no debio.",
        "Publique `confidence` por pregunta: es cuan seguro esta de haber leido la pregunta, no",
        "cuanto se inclina por la opcion afirmativa."]
    preguntas = []
    for f in fuentes:
        pid = f"pert:{f['id']}"
        enunciado = (f"¿Debio capitalizarse en §2 la leccion {f['id']} "
                     f"({f.get('enunciado') or 'sin definicion en el corpus'}) "
                     f"definida por {f.get('plan_dueno') or 'fuente desconocida'}?")
        lineas.append(f"- {pid}: {enunciado}")
        preguntas.append(dc.Pregunta(pid, "choice", enunciado, opciones=OPCIONES_PERTINENCIA))
    return preguntas, "\n".join(lineas)


def declaracion_del_emisor(entorno: dict) -> dict:
    """Que declara el modulo que contesta: `falso` es una propiedad del proveedor, no de este script."""
    dc = _decision_client()
    try:
        return dict(dc.resolver_proveedor(entorno).get("declara") or {})
    except Exception as exc:
        return {"nombre": None, "falso": None, "motivo": f"no se pudo resolver: {_motivo(exc)}"}


def triar(fuentes: list[dict], entorno: dict | None = None,
          lote: int = LOTE, tope: int = TECHO_LLAMADAS) -> tuple[list[dict], dict]:
    """Pasa por `decision_client.evaluar()` por lotes. Nada se descarta: todo candidato sale con bucket."""
    entorno = dict(os.environ if entorno is None else entorno)
    dc = _decision_client()
    emisor = declaracion_del_emisor(entorno)
    juicios: list[dict] = []
    llamadas = 0
    for i in range(0, len(fuentes), lote):
        bloque = fuentes[i:i + lote]
        if llamadas and llamadas >= tope:
            raise TopeExcedido(f"se alcanzo el tope de {tope} llamadas con {len(fuentes) - i} "
                               "candidatos sin triar; el recorte silencioso esta prohibido")
        preguntas, state = construir_preguntas(dc, bloque)
        try:
            resultado = dc.evaluar(state, preguntas, entorno)
        except dc.ProveedorNoConfigurado as exc:
            raise EmisorNoConfigurado(exc.motivo_clase, str(exc),
                                      getattr(exc, "buscado", None)) from exc
        except dc.RespuestaIlegible as exc:
            raise EmisorNoConfigurado("respuesta-ilegible", str(exc)) from exc
        llamadas += 1
        for f in bloque:
            r = resultado.por_pregunta(f"pert:{f['id']}")
            if r is None:
                juicios.append({**f, "estado": "SIN-RESPUESTA", "bucket": "a-revisar-humano",
                                "motivo": f"el emisor no contesto pert:{f['id']}"})
                continue
            probabilidades = dict(getattr(r, "probabilidades", {}) or {})
            confidence = getattr(r, "confidence", None)
            if confidence is None:
                bucket, motivo_bucket = "a-revisar-humano", (
                    "el emisor no publico `confidence`: sin el campo gobernado no hay umbral que "
                    "aplicar, y la ausencia se revisa, no se descarta")
            elif confidence < UMBRAL["value"]:
                bucket, motivo_bucket = "a-revisar-humano", (
                    f"`confidence` {confidence} bajo el umbral {UMBRAL['value']}")
            elif r.eleccion != OPCIONES_PERTINENCIA[0]:
                bucket, motivo_bucket = "a-revisar-humano", (
                    f"el emisor confidently eligio {r.eleccion!r}: el rechazo del emisor se publica "
                    "y lo decide un humano, nunca se borra la fila")
            else:
                bucket, motivo_bucket = "propuesto", "`confidence` sobre el umbral y eleccion afirmativa"
            juicios.append({
                **f, "estado": "TRIADO", "eleccion": r.eleccion,
                "por_si": probabilidades.get(OPCIONES_PERTINENCIA[0]),
                "por_no": probabilidades.get(OPCIONES_PERTINENCIA[1]),
                "confidence": confidence, "bucket": bucket, "motivo_bucket": motivo_bucket,
                "campo_gobernado": "confidence", "umbral": UMBRAL["value"],
                "provider_status": resultado.provider_status,
                "proveedor": resultado.proveedor, "modelo": resultado.modelo})
    return juicios, {"llamadas_al_proveedor": llamadas, "lote": lote, "tope": tope,
                     "preguntas": len(fuentes),
                     "emisor": {"nombre": emisor.get("nombre"), "falso": emisor.get("falso"),
                                "credencial_env": emisor.get("credencial_env"),
                                "declarado_por": "el propio modulo proveedor, via decision_client"}}


# --------------------------------------------------------------------------------------------
# E3 — la revision humana se registra; §2 no se escribe
# --------------------------------------------------------------------------------------------

CAMPOS_DECISION = ("decidio", "fecha", "motivo")


def revisar_humano(juicios: list[dict], decisiones: list[dict] | None) -> dict:
    """Una propuesta del proveedor falso no es evidencia de pertinencia: necesita quien decida."""
    pendientes = [j["id"] for j in juicios if j.get("bucket") == "propuesto"]
    registros, incompletas = [], []
    for d in decisiones or []:
        faltan = [c for c in CAMPOS_DECISION if not str(d.get(c) or "").strip()]
        registro = {"id": d.get("id"), "aceptada": d.get("aceptada"), "decidio": d.get("decidio"),
                    "fecha": d.get("fecha"), "motivo": d.get("motivo")}
        if d.get("id") not in pendientes:
            registro["estado"] = "FUERA-DE-LISTA"
            registro["nota"] = "la decision no corresponde a ninguna propuesta de esta corrida"
        elif faltan:
            registro["estado"] = "REVISION-INCOMPLETA"
            registro["faltan"] = faltan
            incompletas.append(registro["id"])
        elif d.get("aceptada"):
            registro["estado"] = "ACEPTADA-PARA-QUE-ESCRIBA-UN-HUMANO"
            registro["nota"] = ("este script no edita §2 (E3): se publica la fila para que una mano la "
                                "aplique con dueno y «que cambia» reales, citando la revision que la avala")
            registro["fila_para_seccion_dos"] = f"| `{d['id']}` | (aplicada por revision humana) |"
        else:
            registro["estado"] = "RECHAZADA-PUBLICADA"
            registro["fila_no_se_borra"] = True
        registros.append(registro)
    return {"propuestas_pendientes": pendientes, "n_pendientes": len(pendientes),
            "registros": registros, "incompletas": incompletas,
            "seccion_dos_editada_por_este_script": False,
            "nota": ("una fila citada y no aplicada se marca como tal, no se borra (AC10); con "
                     "proveedor falso una propuesta prueba la mecanica del camino, no la pertinencia (E3)")}


# --------------------------------------------------------------------------------------------
# AC15 — denominador, terminos con sus ceros, familias no juzgadas, acceptance
# --------------------------------------------------------------------------------------------

def contar_terminos(ruta: Path) -> dict:
    """La capa fria sobre el indice generado, con sus ceros publicados (A5 / §3-D5)."""
    if not ruta.exists():
        return {"archivo": str(ruta), "estado_archivo": "AUSENTE", "conteos": None}
    texto = ruta.read_text(encoding="utf-8", errors="replace").lower()
    return {"archivo": str(ruta), "bytes": len(texto.encode("utf-8")),
            "metodo": ("conteo de coincidencias de la cadena literal, case-insensitive, sobre el "
                       "indice generado — el mismo atajo que el Paso 0 ya usaba, publicado con sus ceros"),
            "ceros": None,
            "conteos": [{"termino": t, "coincidencias": texto.count(t.lower())}
                        for t in TERMINOS_CAPA_FRIA]}


def denominador(indice: dict, juicios: list[dict], ancladas: list[dict]) -> dict:
    cobertura = indice.get("cobertura", {})
    lecciones = indice.get("lecciones", [])
    familias = sorted({l.get("familia") for l in lecciones if l.get("familia")})
    juzgadas = sorted({j.get("familia") for j in juicios if j.get("familia")})
    numericos = [l["id"] for l in lecciones if re.fullmatch(r"[0-9][0-9.]*", str(l.get("id")))]
    terminos = contar_terminos(INDICE_MD)
    if terminos.get("conteos"):
        terminos["ceros"] = [t["termino"] for t in terminos["conteos"] if t["coincidencias"] == 0]
    return {
        "poblacion_leida_del_indice": {
            "ids_con_definicion": cobertura.get("ids_con_definicion"),
            "ids_citados_sin_definicion": cobertura.get("ids_citados_sin_definicion"),
            "archivos_md_escaneados": cobertura.get("archivos_md_escaneados"),
            "archivos_analysis_escaneados": cobertura.get("archivos_analysis_escaneados"),
            "archivos_contexto_escaneados": cobertura.get("archivos_contexto_escaneados"),
            "fuente": "bloque `cobertura` del JSON leido en esta corrida (cifra no pineada: L-V2.3)",
        },
        "ids_que_recibieron_juicio": len(juicios),
        "denominador_juicio": f"{len(juicios)} de {cobertura.get('ids_con_definicion')}",
        "ancladas_en_seccion_dos": len(ancladas),
        "familias_del_indice": familias,
        "familias_juzgadas": juzgadas,
        "familias_no_juzgadas": sorted(set(familias) - set(juzgadas)),
        "familias_excluidas_por_el_generador": cobertura.get("familias_excluidas", []),
        "ids_numericos": {"no_juzgados": len(numericos), "ejemplos": numericos[:5],
                          "metodo": "regex ^[0-9][0-9.]*$ sobre el `id` del indice"},
        "terminos_capa_fria": terminos,
        "pool_no_sometido_a_juicio": {
            "nota": ("se juzgo el pool «el plan lo define o lo cita, y §2 no lo ancla» mas las filas "
                     "ancladas re-preguntadas. El resto del indice NO se juzgo: los IDs definidos por "
                     "otros planes y ni citados ni anclados por este son otro corte. Decirlo es el "
                     "denominador (AC15), no un descarte."),
        },
    }


def aceptacion() -> dict:
    """E4: el tramo semantico de AC15 NO se ejercita y no se simula."""
    return {
        "estado": "NO-EJERCITADO", "valor": None, "muestra": None, "metodo": None,
        "motivo": ("no hay proveedor de decisiones activo en este plan (deuda D7): el emisor del "
                   "juicio es un proveedor FALSO determinista, asi que `propuesto / a-revisar-humano` "
                   "mide la mecanica del camino y no la pertinencia. Publicar aqui una aceptabilidad "
                   "seria fabricar el disparador de la deuda D6 (contrato E4)"),
        "deuda_afectada": {"D6": "dormida — se re-evalua al existir proveedor real, no antes",
                           "D7": "activar el proveedor; no bloquea una FASE-C offline"},
        "prohibido": "simular la aceptabilidad con el proveedor falso para cerrar AC15 en verde (E4)",
    }


# --------------------------------------------------------------------------------------------
# informe
# --------------------------------------------------------------------------------------------

def _head() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(ROOT),
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or "DESCONOCIDO"
    except Exception as exc:
        return f"DESCONOCIDO ({type(exc).__name__})"


def construir_informe(plan: str, pendientes: list[dict], ancladas: list[dict], indice: dict,
                      estado_suelo: dict, entorno: dict | None = None,
                      decisiones: list[dict] | None = None,
                      revisar_anclados: bool = True, lote: int = LOTE,
                      tope: int = TECHO_LLAMADAS) -> dict:
    fuentes = list(pendientes)
    if revisar_anclados:
        fuentes += anclados_para_revision(ancladas)
    juicios, coste = triar(fuentes, entorno, lote, tope)
    propuestas = [j for j in juicios if j.get("bucket") == "propuesto"
                  and j.get("tipo_fila") != "anclada"]
    cuestionadas = sorted({j["id"] for j in juicios
                           if j.get("tipo_fila") == "anclada"
                           and j.get("eleccion") == OPCIONES_PERTINENCIA[1]})
    lo_que_el_filtro_daria = [f for f in ancladas if f["id"] not in cuestionadas]
    despues, intentos = guardar_filas_ancladas(ancladas, lo_que_el_filtro_daria)
    denom = denominador(indice, juicios, ancladas)
    denom["lecturas_del_json_por_corrida"] = 2
    return {
        "tool": "triage_lesson_relevance.py", "schema_version": "1.0",
        "generated_at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "head": _head(), "plan": plan,
        "status": "TRIADO" if juicios else "SIN-CANDIDATOS",
        "index_status": estado_suelo["index_status"], "frescura": estado_suelo,
        "lecturas_del_json_por_corrida": 2,
        "coste_declarado_ruta_b": ("C ejecuta su propio check de frescura y mide el JSON dos veces "
                                   "(check + consumo) en lugar de heredar el verde de [6/7] del hook"),
        "forma_pregunta": {
            "tipo": "choice", "opciones": list(OPCIONES_PERTINENCIA),
            "campo_gobernado": "confidence",
            "campo_publicado_y_no_gobernado": "por_si = probabilidades['pertinente']",
            "por_que_no_noul": UMBRAL["basis"]},
        "umbral": UMBRAL,
        "seccion_dos": {"anchored_before": len(ancladas), "anchored_after": len(despues),
                        "removed": [f["id"] for f in ancladas if f not in despues],
                        "filas_cuestionadas_sin_borrar": cuestionadas,
                        "intentos_filtrados": intentos,
                        "propuestas_que_entraron_sin_revision": len(
                            [r for r in (decisiones or []) if r.get("estado") == "aplicada"]),
                        "escrita_por_este_script": False},
        "candidatos": juicios,
        "buckets": {"propuesto": [j["id"] for j in propuestas],
                    "a_revisar_humano": [j["id"] for j in juicios
                                         if j.get("bucket") == "a-revisar-humano"
                                         and j.get("tipo_fila") != "anclada"],
                    "ancladas_confirmadas": sorted(
                        {j["id"] for j in juicios if j.get("tipo_fila") == "anclada"
                         and j.get("eleccion") == OPCIONES_PERTINENCIA[0]}),
                    "ancladas_cuestionadas_sin_borrar": cuestionadas},
        "revision_humana": revisar_humano([j for j in juicios if j.get("tipo_fila") != "anclada"],
                                         decisiones),
        "aceptacion": aceptacion(), "coverage_basis": denom, "coste": coste,
        "prohibiciones": ["no filtra (AC10)", "no escribe §2 (E3)", "no importa el SDK (AC6)",
                          "no sale a la red (regla de cero red del contrato)"],
    }


def informe_suelo_no_leible(plan: str, estado: str, payload: dict) -> dict:
    return {"tool": "triage_lesson_relevance.py", "schema_version": "1.0", "plan": plan,
            "status": f"SUELO-{estado}", "index_status": estado, "suelo": payload,
            "candidatos": None,
            "nota": ("el suelo determinista no sostiene ninguna conclusion; esto NO es «sin "
                     "candidatos» (L-PF6, L-PF10) y no se emite denominador favorable (L-R.3)"),
            "aceptacion": aceptacion()}


def informe_emisor_no_configurado(plan: str, estado: dict, exc: EmisorNoConfigurado) -> dict:
    """Suelo FRESCO y ningun emisor resuelto: se publica el estado, no un triaje vacio."""
    return {"tool": "triage_lesson_relevance.py", "schema_version": "1.0", "plan": plan,
            "status": "EMISOR-NO-CONFIGURADO", "index_status": estado.get("index_status"),
            "provider_status": "NO-CONFIGURADO", "motivo_clase": exc.motivo_clase,
            "motivo": exc.motivo, "buscado": exc.buscado,
            "poblacion_que_habria_triado": {"ancladas_en_seccion_dos": estado.get("ancladas"),
                                            "pool_pendiente": estado.get("pool_pendiente"),
                                            "ruta_del_suelo": estado.get("ruta_buscada")},
            "candidatos": None, "umbral": UMBRAL,
            "nota": ("el suelo se leyo fresco pero la puerta no resolvio emisor: esto NO es «sin "
                     "candidatos» ni un verde (AC7); sin emisor no hay juicio que publicar"),
            "aceptacion": aceptacion()}


def coverage_json(informe: dict) -> dict:
    return {"tool": informe["tool"], "plan": informe["plan"], "head": informe.get("head"),
            "generated_at": informe.get("generated_at"), "index_status": informe["index_status"],
            "coverage_basis": informe["coverage_basis"], "aceptacion": informe["aceptacion"],
            "denominador_juicio": informe["coverage_basis"]["denominador_juicio"]}


def ac10_delta(informe: dict) -> dict:
    s = informe["seccion_dos"]
    return {"tool": informe["tool"], "plan": informe["plan"], "head": informe.get("head"),
            "generated_at": informe.get("generated_at"),
            **{k: s[k] for k in ("anchored_before", "anchored_after", "removed",
                                 "filas_cuestionadas_sin_borrar", "intentos_filtrados",
                                 "escrita_por_este_script")},
            "guard": "triage_lesson_relevance.GUARD_ADITIVIDAD_ACTIVO"}


def _escribir(ruta: str | None, payload: dict, etiqueta: str) -> None:
    if not ruta:
        return
    destino = Path(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  {etiqueta} escrito en: {ruta}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Triaje aditivo de pertinencia sobre el indice de lecciones (proponer, no filtrar)")
    ap.add_argument("--plan", required=True, help="nombre o ruta del plan que se tria")
    ap.add_argument("--report", action="store_true",
                    help="emitir el informe; sin --out solo imprime y NO escribe (L-VCF-12)")
    ap.add_argument("--out", default=None, help="destino explicito del informe JSON")
    ap.add_argument("--coverage-out", default=None, help="destino explicito de coverage.json (AC15)")
    ap.add_argument("--ac10-out", default=None, help="destino explicito de ac10_delta.json (AC10)")
    ap.add_argument("--decisiones", default=None, help="JSON con las revisiones humanas registradas")
    ap.add_argument("--solo-pendientes", action="store_true",
                    help="no re-preguntar por las filas ya ancladas en §2")
    ap.add_argument("--index-json", default=str(INDICE_JSON))
    ap.add_argument("--plans-dir", default=str(DEFAULT_PLANS))
    ap.add_argument("--lote", type=int, default=LOTE)
    ap.add_argument("--tope", type=int, default=TECHO_LLAMADAS)
    ap.add_argument("--json", action="store_true", help="volcar el informe por stdout")
    args = ap.parse_args(argv)
    ruta_json = Path(args.index_json)
    plans_dir = Path(args.plans_dir)
    nombre = Path(args.plan).name
    exit_por_estado = {"AUSENTE": 2, "LECTOR-FALLIDO": 3, "VENCIDO": 4}
    try:
        ruta_plan = resolver_plan(args.plan, plans_dir)
        indice, estado = leer_suelo(ruta_json, plans_dir=plans_dir, context_dir=DEFAULT_CONTEXT)
        ancladas = filas_ancladas(ruta_plan / "00-lecciones-capitalizadas.md")
        pendientes = candidatos_de_pertinencia(indice, nombre, ancladas)
        decisiones = None
        if args.decisiones:
            decisiones = json.loads(Path(args.decisiones).read_text(encoding="utf-8"))
            if isinstance(decisiones, dict):
                decisiones = decisiones.get("decisiones", [])
        informe = construir_informe(nombre, pendientes, ancladas, indice, estado, None, decisiones,
                                    revisar_anclados=not args.solo_pendientes, lote=args.lote,
                                    tope=args.tope)
    except EmisorNoConfigurado as exc:
        estado_emisor = {"index_status": "FRESCO", "ruta_buscada": str(ruta_json),
                         "pool_pendiente": len(pendientes), "ancladas": len(ancladas)}
        informe = informe_emisor_no_configurado(nombre, estado_emisor, exc)
        print(f"[EMISOR-NO-CONFIGURADO] el suelo esta FRESCO pero nadie contesta: {exc.motivo}")
        print(f"  clase de motivo: {exc.motivo_clase}")
        print(f"  buscado por la puerta: {exc.buscado}")
        print("  esto NO es «sin candidatos» ni un triaje verde: sin emisor no hay juicio (AC7)")
        if args.json:
            print(json.dumps(informe, ensure_ascii=False, indent=2))
        _escribir(args.out, informe, "informe")
        return 7
    except SueloNoLeible as exc:
        informe = informe_suelo_no_leible(nombre, exc.estado, exc.payload)
        _informar_suelo(exc)
        if args.json:
            print(json.dumps(informe, ensure_ascii=False, indent=2))
        _escribir(args.out, informe, "informe")
        return exit_por_estado.get(exc.estado, 3)
    except TopeExcedido as exc:
        print(f"[TOPE-EXCEDIDO] {exc}")
        return 5

    s = informe["seccion_dos"]
    cb = informe["coverage_basis"]
    print(f"[{informe['status']}] plan {informe['plan']} | suelo {informe['index_status']} "
          f"(2 lecturas del JSON por el check propio de C)")
    print(f"  §2 antes={s['anchored_before']} despues={s['anchored_after']} "
          f"removed={s['removed'] or '[]'} cuestionadas={s['filas_cuestionadas_sin_borrar'] or 'ninguna'}")
    print(f"  candidatos triados: {len(informe['candidatos'])} "
          f"(propuesto={len(informe['buckets']['propuesto'])}, "
          f"a-revisar-humano={len(informe['buckets']['a_revisar_humano'])})")
    print(f"  umbral: {informe['umbral']['campo']} >= {informe['umbral']['value']} "
          f"(`por_si` se publica y NO gobierna) | emisor: {informe['coste']['emisor']['nombre']} "
          f"falso={informe['coste']['emisor']['falso']}")
    print(f"  aceptacion: {informe['aceptacion']['estado']} — D6 dormida")
    print(f"  denominador: {cb['denominador_juicio']} IDs juzgados, familias juzgadas "
          f"{cb['familias_juzgadas']}, no juzgadas {cb['familias_no_juzgadas'] or 'ninguna'}")
    if cb["terminos_capa_fria"].get("conteos"):
        print("  terminos de la capa fria: " + ", ".join(
            f"{t['termino']}={t['coincidencias']}" for t in cb["terminos_capa_fria"]["conteos"]))
    print(f"  §2 escrita por este script: {s['escrita_por_este_script']} "
          f"(propuestas sin revision humana: {informe['revision_humana']['n_pendientes']})")
    if args.out and not args.report:
        print("[AVISO] --out sin --report no escribe: el destino se declara con el informe",
              file=sys.stderr)
    if args.report:
        if args.out:
            print("  [DESTINO DECLARADO] el informe se escribe solo donde --out lo nombra; no hay "
                  "ruta por defecto dentro de la evidencia de otra fase (L-VCF-12)")
        else:
            print("  [NO-ESCRITURA] --report sin --out imprime y no escribe")
        _escribir(args.out, informe, "informe")
        _escribir(args.coverage_out, coverage_json(informe), "coverage")
        _escribir(args.ac10_out, ac10_delta(informe), "ac10_delta")
    if args.json:
        print(json.dumps(informe, ensure_ascii=False, indent=2))
    if informe["revision_humana"]["incompletas"]:
        print(f"[REVISION-INCOMPLETA] sin quien/fecha/motivo no se aplica: "
              f"{informe['revision_humana']['incompletas']}")
        return 6
    return 0


def _informar_suelo(exc: SueloNoLeible) -> None:
    p = exc.payload
    print(f"[{exc.estado}] el suelo del triaje no es leible: {p.get('motivo')}")
    print(f"  ruta buscada: {p.get('ruta_buscada')}")
    if p.get("comando_regeneracion"):
        print(f"  regenerar: {p['comando_regeneracion']}")
    if exc.estado == "VENCIDO":
        print(f"  lo detecta el hook en: {p.get('check_del_hook_que_lo_detecta')}")
        d = p.get("diff") or {}
        print(f"  que lo vencio: {len(d.get('solo_en_disco', []))} IDs solo en disco, "
              f"{len(d.get('solo_en_el_calculo', []))} solo en el calculo, "
              f"{len(d.get('cobertura_distinta', {}))} claves de cobertura distintas")


if __name__ == "__main__":
    sys.exit(main())
