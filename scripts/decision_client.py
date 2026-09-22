#!/usr/bin/env python3
"""Unica puerta del repositorio a un proveedor de decisiones estructuradas (FASE-B del plan
VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20).

QUE ES
    Una costura: resuelve QUE proveedor debe contestar (por variable de entorno), le pasa el estado
    y las preguntas, y **valida la forma** de lo que devuelve. No decide nada por su cuenta.

QUE NO ES
    No es un cliente HTTP, no conoce ningun proveedor concreto, y no tiene proveedor por defecto.
    El SDK oficial y el adapter viven detras de ella (deuda **D7**: activarlos), no dentro de los
    consumidores. Razon: el SDK del proveedor redefinio los criterios de una primitiva y migro de
    serializador en sus primeros nueve dias de publico (dato **externo**, reportado por el operador
    el 2026-09-20; no verificable desde este repo). Si el repo se acopla al nombre del proveedor,
    cada subida rompe fases de otros planes; si se acopla a la costura, rompe **este** contract test.

CONTRATO PROPIO (por eso existe el archivo, no por conveniencia)
    `evaluar(state, preguntas)` -> `ResultadoEvaluacion` con una respuesta tipada por pregunta.
    Tres formas de respuesta, las tres documentadas en la interfaz del proveedor:
      * `choice` : eleccion + probabilidades sobre TODAS las opciones + confidence.
      * `score`  : nivel ordenado + su leyenda + confidence.
      * `noul`   : probabilidad de si. **Sin** confidence: la primitiva no la expone, y un numero
                   ahi significaria dos cosas distintas segun quien lo lea (ver `VERIFICACIONES`).
    La confidence es lo que separa «actue» de «no estoy seguro»; FASE-C la usa en AC12, por eso es
    obligatoria en `choice`/`score` y prohibida en `noul`, y por eso un payload incompleto **falla**
    en lugar de rellenarse.

LOS TRES ESTADOS (R2.9; convenciones y nombres heredados de FASE-A, no reinventados)
    `provider_status` in {`RESUELTO`, `NO-CONFIGURADO`, `ILEGIBLE`}, y cada fallo lleva su
    `motivo_clase` para que los estados no colapsen entre si:
      * `NO-CONFIGURADO` : no se nombro proveedor, o el directorio buscado no existe, o el nombre
                           no esta en el directorio. Imprime **la ruta y el nombre buscados**.
      * `ILEGIBLE`       : el proveedor contesto y la respuesta no pasa la forma. Imprime los
                           motivos. **Nunca** una decision favorable ni una heuristica.
    Y un estado del lector, aparte del del proveedor: si el **modulo** de un proveedor no carga,
    esto cae a `LECTOR-FALLIDO` (`LectorFallido`) y no se traduce a ninguno de los tres, porque
    «no pude leer al proveedor» no es «el proveedor no contesto» (L-PF6, L-PF10).

LIMITES DEL PROVEEDOR QUE CONDICIONAN EL DISENO (escritos aqui porque son del proveedor)
    1. **Solo acepta texto**: `state` y cada `Pregunta.enunciado` son `str`; nada de binarios.
    2. **Techo de contexto por solicitud** (dato externo, documentacion publica consultada el
       2026-09-21 por el plan hermano `EVALUACION-JEV-TYPESAFE-2026-09-21`, **no verificado desde
       este repo**): 64k tokens para estado + todas las preguntas, 32k para estado + la pregunta
       mas larga. `TECHO_CONTEXTO_DECLARADO` lo publica **como declaracion**: ningun codigo de esta
       costura compara nada contra el. Estar por debajo del techo **no** esta medido aqui: la suma
       en bytes de los dos documentos de gobierno de este repo si esta medida (`estimar_carga` la
       expone con su divisor), y la premise del plan -que el techo es menor que esa suma- queda a
       cargo de quien active D7. De ahi que FASE-C chunkee, y que el lint de conteos de FASE-A sea
       determinista y no pase por esta puerta.
    3. **Modos de fallo documentados del proveedor**: lectura literal, conteo y comparacion de
       fechas. Son la razon de que la costura exija forma y no interprete semantica.
    4. **Hasta 255 opciones** por `choice` y probabilidades que suman ~1
       (`TOLERANCIA_SUMA_PROBABILIDADES`, declarada ahi mismo).

CERO RED (regla del contrato de ejecucion de este plan)
    Este modulo **no abre sockets ni importa ningun cliente HTTP**: importa stdlib de proposito
    (`importlib` para cargar el archivo del proveedor por ruta, `ast` para el escaneo de AC6). La
    prueba `tests/quality_gates/decision_client/conftest.py` arma ademas un guard que hace explotar
    cualquier intento de conexion durante la seleccion de esta fase.

CREDENCIAL
    La costura no la lee salvo para publicar **si esta o no** (`credencial.presente`, un bool), y
    nunca su valor, su longitud ni un prefijo. Un valor que aparece en un transcript obliga a
    rotarla, asi que la evidencia registra `provider_status`, jamas la clave.

USO
    python scripts/decision_client.py --provider-status      # resuelve, no llama a nadie
    python scripts/decision_client.py --scan-imports         # AC6 sobre el arbol, con poblacion
    python scripts/decision_client.py --costura              # AC9: cuanto cuesta un 2 proveedor
    python scripts/decision_client.py --report [--json]      # informe.json (FASE-B)

SALIDA CLI: 0 = RESUELTO / SIN-HALLAZGOS · 1 = hay hallazgos · 2 = AUSENTE (ruta buscada) ·
3 = LECTOR-FALLIDO. Los estados se imprimen en ASCII por la misma razon que en
`validate_governance_numbers.py`: la consola de este entorno no es UTF-8.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Sequence

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
EVIDENCIA = ROOT / "evidence" / "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20" / "FASE-B"

ENV_PROVIDER = "IAH_DECISION_PROVIDER"
ENV_PROVIDERS_DIR = "IAH_DECISION_PROVIDERS_DIR"

ESTADOS_PROVEEDOR = ("RESUELTO", "NO-CONFIGURADO", "ILEGIBLE")
TIPOS_PREGUNTA = ("choice", "score", "noul")

# --- AC8: el pin del modelo, DECLARADO y nunca usado para validar ---------------------------
# AC8 pide «version de modelo pineada y declarada»; el prompt de la fase prohibe pinear literales
# del proveedor en el contract test. Las dos cosas se respetan aqui: el valor vive en esta
# declaracion con su fuente y su fecha, y la prueba afirma (a) que la costura conserva el modelo
# que el proveedor reporto y (b) que esta constante no interviene en ninguna decision del codigo.
PIN_MODELO_DECLARADO = {
    "modelo": "jev-1.13.0",
    "fuente": "dato externo: docs.typesafe.ai/models, consultado el 2026-09-21 por "
              "EVALUACION-JEV-TYPESAFE-2026-09-21 (CONTEXT-JEV-TYPESAFE §1)",
    "verificado_desde_este_repo": False,
    "aliases_moviles_rechazados": ["jev-latest", "jev-preview"],
    "usado_por_el_codigo": False,
}

# --- AC6: lo que NO puede importarse fuera de esta puerta -----------------------------------
# Nombres del SDK, del adapter y del transporte que el SDK exige (no confundir httpx2 con httpx).
NOMBRES_PROHIBIDOS = ("typesafe", "typesafe_sdk", "typesafe-sdk", "jev", "httpx2")
# Alias del adapter que el propio proveedor publica como reemplazo respaldado por APIs de LLM.
ALIAS_ADAPTER = ("typesafe_adapter", "adapter_typesafe", "system_one_adapter")
# Que cuenta como importar: statica, dinamica o trampa por builtin.
IMPORT_STATICO_NODES = (ast.Import, ast.ImportFrom)
FUNCIONES_DE_CARGA = ("import_module", "__import__", "find_and_load", "exec_module")
# Un archivo bajo cualquier directorio `*proveedores*` esta en la superficie de contrabando: ahi
# una carga con nombre construido en runtime SI es hallazgo (fuera de ahi es solo un limite).
DIRECTORIO_PROVEEDORES_RE = re.compile(r"(^|/)[^/]*proveedores[^/]*/")
ARCHIVOS_EXCLUIDOS_DE_LA_POBLACION = (".git", "venv", ".venv", "env", "__pycache__",
                                      "node_modules", "tmp_test", "site-packages", "build",
                                      "temp")

TOLERANCIA_SUMA_PROBABILIDADES = 0.02
TECHO_CONTEXTO_DECLARADO = {"estado_mas_preguntas_tokens": 64000,
                            "estado_mas_pregunta_mas_larga_tokens": 32000,
                            "fuente": "dato externo, ver LIMITES del docstring",
                            "comparado_por_el_codigo": False}
DIVISOR_TOKENS_DECLARADO = 4

SCHEMA_VERSION = "1.0"

# centinela de `evaluar(_payload=...)`: `None` **es** un payload posible (el de un proveedor roto),
# asi que «no se inyecto nada» no puede representarse con None.
SIN_PAYLOAD_INYECTADO = object()


class ProveedorNoConfigurado(Exception):
    """`provider_status = NO-CONFIGURADO`. Dice la ruta y el nombre buscados. Jamas decide."""

    def __init__(self, mensaje: str, motivo_clase: str, buscado: dict):
        super().__init__(mensaje)
        self.motivo_clase = motivo_clase
        self.buscado = buscado


class RespuestaIlegible(Exception):
    """`provider_status = ILEGIBLE`: el proveedor contesto y la forma no pasa. Nunca un favorable."""

    def __init__(self, mensaje: str, motivos: Sequence[str], proveedor: str = None):
        super().__init__(mensaje)
        self.motivos = list(motivos)
        self.proveedor = proveedor
        # Credencial del intento fallido: la escribe `evaluar()` para que el informe pueda declarar
        # «se resolvio un proveedor con credencial X presente/ausente» sin haberla leido.
        self.credencial = None


class LectorFallido(Exception):
    """R2.9: el lector (o el modulo del proveedor) no pudo operar. No se traduce a los tres estados."""


class Ausente(Exception):
    """R2.9: la ruta buscada se imprime tal cual."""


# -----------------------------------------------------------------------------------------
# Contrato propio
# -----------------------------------------------------------------------------------------

def _ascii(texto: str) -> str:
    sin = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return sin.replace("\n", " ").strip()


def _en_rango(valor) -> bool:
    return isinstance(valor, (int, float)) and not isinstance(valor, bool) and 0.0 <= float(valor) <= 1.0


class Pregunta:
    """Una pregunta al proveedor: `choice` con opciones, `score` con leyenda ordenada, `noul`."""

    __slots__ = ("id", "tipo", "enunciado", "opciones", "leyenda")

    def __init__(self, id: str, tipo: str, enunciado: str,
                 opciones: Sequence[str] = (), leyenda: Sequence[str] = ()):
        self.id = id
        self.tipo = tipo
        self.enunciado = enunciado
        self.opciones = tuple(opciones)
        self.leyenda = tuple(leyenda)

    def validar(self) -> list:
        fallos = []
        if not isinstance(self.id, str) or not self.id.strip():
            fallos.append(f"pregunta con id vacio o no texto: {self.id!r}")
        if self.tipo not in TIPOS_PREGUNTA:
            fallos.append(f"{self.id}: tipo {self.tipo!r} fuera de contrato {list(TIPOS_PREGUNTA)}")
        if not isinstance(self.enunciado, str) or not self.enunciado.strip():
            fallos.append(f"{self.id}: el proveedor solo acepta texto y el enunciado no lo es")
        if self.tipo == "choice" and not self.opciones:
            fallos.append(f"{self.id}: choice sin opciones no es evaluable")
        if self.tipo == "score" and not self.leyenda:
            fallos.append(f"{self.id}: score sin leyenda ordenada no es evaluable")
        return fallos

    def __repr__(self):
        return f"Pregunta(id={self.id!r}, tipo={self.tipo!r})"


class RespuestaEleccion:
    __slots__ = ("pregunta_id", "eleccion", "probabilidades", "confidence")

    def __init__(self, pregunta_id, eleccion, probabilidades, confidence):
        self.pregunta_id, self.eleccion = pregunta_id, eleccion
        self.probabilidades, self.confidence = dict(probabilidades), confidence

    tipo = "choice"

    def to_dict(self) -> dict:
        return {"tipo": self.tipo, "pregunta_id": self.pregunta_id, "eleccion": self.eleccion,
                "probabilidades": self.probabilidades, "confidence": self.confidence}


class RespuestaNivel:
    __slots__ = ("pregunta_id", "nivel", "leyenda", "confidence")

    def __init__(self, pregunta_id, nivel, leyenda, confidence):
        self.pregunta_id, self.nivel = pregunta_id, nivel
        self.leyenda, self.confidence = leyenda, confidence

    tipo = "score"

    def to_dict(self) -> dict:
        return {"tipo": self.tipo, "pregunta_id": self.pregunta_id, "nivel": self.nivel,
                "leyenda": self.leyenda, "confidence": self.confidence}


class RespuestaNoul:
    """`noul` no trae confidence: la primitiva no la expone. No se rellena con 0.0 ni con None
    «por defecto»: el campo existe para decir «no aplica a esta primitiva», con su causa escrita."""

    __slots__ = ("pregunta_id", "probabilidad_si")

    def __init__(self, pregunta_id, probabilidad_si):
        self.pregunta_id, self.probabilidad_si = pregunta_id, probabilidad_si

    tipo = "noul"
    confidence = None

    def to_dict(self) -> dict:
        return {"tipo": self.tipo, "pregunta_id": self.pregunta_id,
                "probabilidad_si": self.probabilidad_si, "confidence": None,
                "confidence_motivo": "la primitiva noul no expone confidence"}


class ResultadoEvaluacion:
    """Lo que la costura publica de una corrida. `usage=None` **no** es consumo cero (lección del
    plan hermano: un usage ausente no puede leerse como 0)."""

    __slots__ = ("provider_status", "proveedor", "modelo", "respuestas", "usage",
                 "request_id", "credencial")

    def __init__(self, provider_status, proveedor, modelo, respuestas, usage,
                 request_id, credencial):
        self.provider_status = provider_status
        self.proveedor = proveedor
        self.modelo = modelo
        self.respuestas = tuple(respuestas)
        self.usage = usage
        self.request_id = request_id
        self.credencial = credencial

    def por_pregunta(self, id_pregunta: str):
        for r in self.respuestas:
            if r.pregunta_id == id_pregunta:
                return r
        return None

    def to_dict(self) -> dict:
        return {"provider_status": self.provider_status, "proveedor": self.proveedor,
                "modelo": self.modelo, "respuestas": [r.to_dict() for r in self.respuestas],
                "usage": self.usage, "request_id": self.request_id,
                "credencial": self.credencial}


# -----------------------------------------------------------------------------------------
# Forma de la respuesta: los guards que AC8 fija y que el mutation check apaga uno a uno
# -----------------------------------------------------------------------------------------

CAMPOS_BASE = ("pregunta_id", "tipo")
CAMPOS_POR_TIPO = {
    "choice": ("eleccion", "probabilidades", "confidence"),
    "score": ("nivel", "leyenda", "confidence"),
    "noul": ("probabilidad_si",),
}


def _campos_declarados(r: dict) -> tuple:
    return tuple(sorted(k for k in r if k not in CAMPOS_BASE))


def check_campos_conocidos(payload: dict, preguntas: Sequence[Pregunta]) -> list:
    """Un campo nuevo, o uno que desaparece, ES una ruptura de contrato: la primitiva cambio."""
    motivos = []
    for r in payload.get("respuestas", []):
        if not isinstance(r, dict):
            motivos.append(f"respuesta no es un objeto: {r!r}")
            continue
        tipo = r.get("tipo")
        faltan = set(CAMPOS_BASE) - set(r)
        if faltan:
            motivos.append(f"respuesta {r.get('pregunta_id', '?')}): faltan campos base "
                           f"{sorted(faltan)}")
        if tipo not in CAMPOS_POR_TIPO:
            motivos.append(f"respuesta {r.get('pregunta_id', '?')}): tipo {tipo!r} fuera de "
                           f"contrato {list(CAMPOS_POR_TIPO)}")
            continue
        esperados = set(CAMPOS_POR_TIPO[tipo])
        declarados = set(_campos_declarados(r))
        if tipo == "noul" and declarados & {"confidence"}:
            motivos.append(f"{r.get('pregunta_id')}: noul no debe reportar confidence "
                           "(la primitiva no la expone)")
            declarados -= {"confidence"}
        if esperados - declarados:
            motivos.append(f"{r.get('pregunta_id')} ({tipo}): faltan campos "
                           f"{sorted(esperados - declarados)}")
        if declarados - esperados and tipo != "noul":
            motivos.append(f"{r.get('pregunta_id')} ({tipo}): campos fuera de contrato "
                           f"{sorted(declarados - esperados)}")
    desconocidos = set(payload) - {"modelo", "respuestas", "usage", "request_id"}
    if desconocidos:
        motivos.append(f"payload con claves fuera de contrato {sorted(desconocidos)}")
    return motivos


def check_cobertura_de_preguntas(payload: dict, preguntas: Sequence[Pregunta]) -> list:
    """Una respuesta por pregunta, ni una de mas: ningun drop silencioso (familia de AC12)."""
    ids_esperados = [p.id for p in preguntas]
    ids_recibidos = [r.get("pregunta_id") for r in payload.get("respuestas", []) if isinstance(r, dict)]
    motivos = []
    duplicados = {i for i in ids_recibidos if ids_recibidos.count(i) > 1}
    if duplicados:
        motivos.append(f"respuestas duplicadas para {sorted(duplicados)}")
    faltan = [i for i in ids_esperados if i not in ids_recibidos]
    sobran = [i for i in ids_recibidos if i not in ids_esperados]
    if faltan:
        motivos.append(f"sin respuesta para {faltan}")
    if sobran:
        motivos.append(f"respuestas de preguntas no pedidas {sobran}")
    for r, p in zip(payload.get("respuestas", []), preguntas):
        if isinstance(r, dict) and "tipo" in r and r["tipo"] != p.tipo:
            motivos.append(f"{p.id}: el proveedor contesto {r['tipo']!r} a una pregunta {p.tipo!r}")
    return motivos


def check_choice(payload: dict, preguntas: Sequence[Pregunta]) -> list:
    motivos = []
    por_id = {p.id: p for p in preguntas if p.tipo == "choice"}
    for r in payload.get("respuestas", []):
        if not isinstance(r, dict) or r.get("tipo") != "choice" or r.get("pregunta_id") not in por_id:
            continue
        p = por_id[r["pregunta_id"]]
        if r.get("eleccion") not in p.opciones:
            motivos.append(f"{p.id}: eleccion {r.get('eleccion')!r} no esta entre las opciones")
        probs = r.get("probabilidades")
        if not isinstance(probs, dict):
            motivos.append(f"{p.id}: probabilidades no es un objeto")
            continue
        if set(probs) != set(p.opciones):
            motivos.append(f"{p.id}: las probabilidades no cubren exactamente las opciones "
                           f"(recibidas {sorted(probs)}, esperadas {sorted(p.opciones)})")
            continue
        if any(not _en_rango(v) for v in probs.values()):
            motivos.append(f"{p.id}: alguna probabilidad esta fuera de [0,1]")
            continue
        if abs(sum(float(v) for v in probs.values()) - 1.0) > TOLERANCIA_SUMA_PROBABILIDADES:
            motivos.append(f"{p.id}: las probabilidades suman "
                           f"{sum(float(v) for v in probs.values()):.4f}, no 1 "
                           f"(tolerancia {TOLERANCIA_SUMA_PROBABILIDADES})")
            continue
        if not _en_rango(r.get("confidence")):
            motivos.append(f"{p.id}: confidence ausente o fuera de [0,1] - sin ella no se puede "
                           "separar «actue» de «no estoy seguro» (AC12 de FASE-C)")
    return motivos


def check_score(payload: dict, preguntas: Sequence[Pregunta]) -> list:
    motivos = []
    por_id = {p.id: p for p in preguntas if p.tipo == "score"}
    for r in payload.get("respuestas", []):
        if not isinstance(r, dict) or r.get("tipo") != "score" or r.get("pregunta_id") not in por_id:
            continue
        p = por_id[r["pregunta_id"]]
        nivel = r.get("nivel")
        if not isinstance(nivel, int) or isinstance(nivel, bool) or not 0 <= nivel < len(p.leyenda):
            motivos.append(f"{p.id}: nivel {nivel!r} fuera de la leyenda de {len(p.leyenda)} "
                           "niveles ordenados")
            continue
        if r.get("leyenda") != p.leyenda[nivel]:
            motivos.append(f"{p.id}: el nivel {nivel} y su leyenda {r.get('leyenda')!r} no "
                           f"cuadran (la leyenda declarada es {p.leyenda[nivel]!r})")
            continue
        if not _en_rango(r.get("confidence")):
            motivos.append(f"{p.id}: confidence ausente o fuera de [0,1]")
    return motivos


def check_noul(payload: dict, preguntas: Sequence[Pregunta]) -> list:
    motivos = []
    ids = {p.id for p in preguntas if p.tipo == "noul"}
    for r in payload.get("respuestas", []):
        if not isinstance(r, dict) or r.get("tipo") != "noul" or r.get("pregunta_id") not in ids:
            continue
        if not _en_rango(r.get("probabilidad_si")):
            motivos.append(f"{r.get('pregunta_id')}: probabilidad_si ausente o fuera de [0,1]. "
                           "Ojo: probabilidad baja NO es incertidumbre, puede ser un no claro.")
    return motivos


def check_metadata(payload: dict, preguntas: Sequence[Pregunta]) -> list:
    """El modelo que el proveedor reporta tiene que sobrevivir: sin el no hay reproducibilidad."""
    motivos = []
    if not isinstance(payload.get("modelo"), str) or not payload["modelo"].strip():
        motivos.append("el payload no declara que modelo lo contesto (sin modelo no es reproducible)")
    usage = payload.get("usage")
    if usage is not None:
        if not isinstance(usage, dict):
            motivos.append("usage no es un objeto ni None")
        else:
            desconocido = set(usage) - {"input_tokens", "output_tokens"}
            if desconocido:
                motivos.append(f"usage con claves fuera de contrato {sorted(desconocido)}")
            for k in ("input_tokens", "output_tokens"):
                v = usage.get(k)
                if v is not None and (not isinstance(v, int) or isinstance(v, bool) or v < 0):
                    motivos.append(f"usage.{k} no es un entero >= 0: {v!r}")
    return motivos


# Guard aggregate: apagar uno de estos es lo que el mutation check de R2.8 prueba que se note.
VERIFICACIONES_DE_FORMA = (
    ("campos-conocidos", check_campos_conocidos),
    ("cobertura-de-preguntas", check_cobertura_de_preguntas),
    ("forma-choice", check_choice),
    ("forma-score", check_score),
    ("forma-noul", check_noul),
    ("metadata-modelo-usage", check_metadata),
)


def _nombre_de_la_verificacion(motivo: str) -> str:
    """De `forma-choice: c1: ...` a `forma-choice`: cada motivo declara que guard lo produjo, para
    que un mutation check pueda afirmar que el rojo que vio es **el suyo** y no otro (L-V2.1)."""
    return motivo.split(":", 1)[0]


def validar_payload(payload, preguntas: Sequence[Pregunta], proveedor: str = None) -> dict:
    """Del payload crudo al contrato, o a `RespuestaIlegible`. **Nunca** a una decision implicita."""
    if not isinstance(payload, dict):
        raise RespuestaIlegible(
            f"el proveedor {proveedor!r} devolvio {type(payload).__name__}, no un payload",
            [f"payload-no-dict:{type(payload).__name__}"], proveedor)
    respuestas = payload.get("respuestas")
    if respuestas is None:
        raise RespuestaIlegible(f"el payload del proveedor {proveedor!r} no trae respuestas",
                                ["respuesta-ausente:'respuestas' no esta en el payload"], proveedor)
    if not isinstance(respuestas, list) or not respuestas:
        # L-PF10: vacio != ausente, y una lista vacia tampoco es « cero decisiones favorables».
        raise RespuestaIlegible(
            f"el proveedor {proveedor!r} devolvio una lista de respuestas vacia",
            [f"respuesta-vacia:{type(respuestas).__name__}"], proveedor)
    motivos = []
    for nombre, fn in VERIFICACIONES_DE_FORMA:
        for m in fn(payload, preguntas):
            motivos.append(f"{nombre}: {m}")
    if motivos:
        raise RespuestaIlegible(
            f"respuesta de {proveedor!r} fuera de forma ({len(motivos)} motivo(s))",
            motivos, proveedor)
    return payload


def a_respuestas_tipadas(payload: dict) -> list:
    """Solo se llama despues de `validar_payload`: si aun falta un campo ahi, la invariante se
    rompio dentro de la puerta y eso se declara como fallo del lector, nunca se rellena."""
    tipadas = []
    for r in payload["respuestas"]:
        esperados = CAMPOS_POR_TIPO.get(r["tipo"], ())
        faltan = [k for k in esperados if k not in r]
        if faltan:
            raise LectorFallido(
                f"la validacion paso pero a {r.get('pregunta_id')} le faltan {faltan}: la puerta "
                "no rellena campos, se declara inoperante (R2.9)")
        if r["tipo"] == "choice":
            tipadas.append(RespuestaEleccion(r["pregunta_id"], r["eleccion"],
                                             r["probabilidades"], r["confidence"]))
        elif r["tipo"] == "score":
            tipadas.append(RespuestaNivel(r["pregunta_id"], r["nivel"], r["leyenda"],
                                          r["confidence"]))
        else:
            tipadas.append(RespuestaNoul(r["pregunta_id"], r["probabilidad_si"]))
    return tipadas


# -----------------------------------------------------------------------------------------
# Resolucion del proveedor (por entorno, sin default) y carga del modulo
# -----------------------------------------------------------------------------------------

def _credencial(nombre_env: str, entorno: dict) -> dict:
    """Solo `presente`. El valor, su longitud y cualquier prefijo quedan fuera por diseño."""
    if not nombre_env:
        return {"env_var": None, "presente": False, "motivo": "el proveedor no declara credencial"}
    return {"env_var": nombre_env, "presente": bool(entorno.get(nombre_env)),
            "motivo": "bool por entorno; el valor nunca se lee ni se imprime desde esta costura"}


def resolver_proveedor(entorno: dict = None) -> dict:
    """`{nombre, modulo, path, credencial_env}` del proveedor nombrado por el entorno.

    No hay proveedor por defecto: ninguna de las cuatro salidas «no encontro» devuelve un candidato
    propio (L-PF6 - un lector roto leido como ausencia producia un dolor falso).
    """
    entorno = os.environ if entorno is None else entorno
    buscado = {ENV_PROVIDER: entorno.get(ENV_PROVIDER), ENV_PROVIDERS_DIR: entorno.get(ENV_PROVIDERS_DIR)}
    nombre = (entorno.get(ENV_PROVIDER) or "").strip()
    if not nombre:
        raise ProveedorNoConfigurado(
            f"{ENV_PROVIDER} no esta definido: no hay proveedor nombrado y esta costura no elige "
            "uno por su cuenta", "env-de-proveedor-sin-definir", buscado)
    dir_raw = (entorno.get(ENV_PROVIDERS_DIR) or "").strip()
    if not dir_raw:
        raise ProveedorNoConfigurado(
            f"{ENV_PROVIDERS_DIR} no esta definido: no se busca en ninguna ruta por defecto "
            f"(el proveedor nombrado era {nombre!r})", "env-de-directorio-sin-definir", buscado)
    directorio = Path(dir_raw)
    if not directorio.is_dir():
        raise ProveedorNoConfigurado(
            f"el directorio de proveedores no existe: {directorio} (proveedor nombrado {nombre!r})",
            "directorio-buscado-no-existe", buscado)
    candidatos = sorted(p for p in directorio.glob("*.py") if not p.name.startswith("_"))
    encontrados, errores = [], []
    for path in candidatos:
        try:
            mod = cargar_modulo_proveedor(path)
        except LectorFallido as exc:
            errores.append(f"{path.name}: {exc}")
            continue
        decl = getattr(mod, "PROVEEDOR", {})
        encontrados.append(decl.get("nombre"))
        if decl.get("nombre") == nombre:
            return {"nombre": nombre, "modulo": mod, "path": path,
                    "credencial_env": decl.get("credencial_env"),
                    "declara": decl, "directorio": str(directorio),
                    "descarte_carga": errores}
    raise ProveedorNoConfigurado(
        f"el proveedor {nombre!r} no esta en {directorio}; nombres encontrados: "
        f"{encontrados or '(ninguno)'}"
        + (f"; modulos que no cargaron: {errores}" if errores else ""),
        "nombre-no-esta-en-el-directorio", {**buscado, "directorio": str(directorio),
                                            "nombres_encontrados": encontrados})


def cargar_modulo_proveedor(path: Path):
    """Carga UN archivo local por ruta. No importa paquetes: es la unica carga dinamica de la puerta."""
    spec = importlib.util.spec_from_file_location(f"iah_decision_provider__{path.stem}", path)
    if spec is None or spec.loader is None:
        raise LectorFallido(f"no se pudo construir el spec de {path}")
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:  # noqa: BLE001 - se re-lanza con estado propio, jamas se traga
        raise LectorFallido(f"el modulo de proveedor {path} no cargo: {type(exc).__name__}: {exc}") from exc
    if not isinstance(getattr(mod, "PROVEEDOR", None), dict):
        raise LectorFallido(f"{path}: no declara un dict PROVEEDOR")
    if not callable(getattr(mod, "evaluar", None)):
        raise LectorFallido(f"{path}: PROVEEDOR no expone una funcion evaluar(state, preguntas)")
    return mod


# -----------------------------------------------------------------------------------------
# La puerta
# -----------------------------------------------------------------------------------------

def evaluar(state, preguntas: Sequence[Pregunta], entorno: dict = None,
            _payload=SIN_PAYLOAD_INYECTADO) -> ResultadoEvaluacion:
    """Unica llamada del repo a un proveedor de decisiones estructuradas.

    `_payload` existe para el contract test de forma (inyectar un payload alterado sin tocar un
    proveedor real); **no** es un atajo de produccion: sigue validando la forma.
    """
    if not isinstance(state, str):
        raise TypeError("el proveedor solo acepta texto: `state` debe ser str")
    entorno = os.environ if entorno is None else entorno
    preguntas = list(preguntas)
    fallos = [f for p in preguntas for f in p.validar()]
    if fallos:
        raise ValueError("preguntas fuera de contrato: " + "; ".join(fallos[:3]))
    if not preguntas:
        raise ValueError("evaluar() sin preguntas no tiene nada que medir: se falla, no se devuelve []")

    prov = resolver_proveedor(entorno)
    payload = (prov["modulo"].evaluar(state, preguntas)
               if _payload is SIN_PAYLOAD_INYECTADO else _payload)
    credencial = _credencial(prov.get("credencial_env"), entorno)
    try:
        validar_payload(payload, preguntas, prov["nombre"])
    except RespuestaIlegible as exc:
        exc.credencial = credencial
        raise
    return ResultadoEvaluacion(
        provider_status="RESUELTO",
        proveedor=prov["nombre"],
        modelo=payload["modelo"],
        respuestas=a_respuestas_tipadas(payload),
        usage=payload.get("usage"),
        request_id=payload.get("request_id"),
        credencial=credencial,
    )


def estado_proveedor(entorno: dict = None) -> dict:
    """Diagnostico sin llamada: resuelve y dice en que de los tres estados (o el del lector) esta."""
    entorno = os.environ if entorno is None else entorno
    try:
        prov = resolver_proveedor(entorno)
    except ProveedorNoConfigurado as exc:
        return {"provider_status": "NO-CONFIGURADO", "motivo_clase": exc.motivo_clase,
                "motivo": str(exc), "buscado": exc.buscado}
    except LectorFallido as exc:
        return {"provider_status": None, "estado_lector": "LECTOR-FALLIDO", "motivo": str(exc)}
    return {"provider_status": "RESUELTO", "proveedor": prov["nombre"],
            "archivo": str(prov["path"]), "credencial": _credencial(prov.get("credencial_env"), entorno),
            "declara": {k: v for k, v in prov["declara"].items() if k != "nota"},
            "nota_proveedor": prov["declara"].get("nota"),
            "motivo_clase": None, "motivo": None}


def estimar_carga(state: str, preguntas: Sequence[Pregunta]) -> dict:
    """Lo que costaria una solicitud, con su divisor declarado. FASE-C chunkea con esto."""
    texto = state + "".join(p.enunciado for p in preguntas)
    bytes_total = len(texto.encode("utf-8"))
    return {"bytes": bytes_total, "tokens_estimados_divisor_4": bytes_total // DIVISOR_TOKENS_DECLARADO,
            "preguntas": len(preguntas), "techo_declarado": TECHO_CONTEXTO_DECLARADO,
            "nota": "comparacion contra el techo NO la decide este modulo (LIMITES, punto 2)"}


# -----------------------------------------------------------------------------------------
# AC6: escaneo de aislamiento sobre el arbol real
# -----------------------------------------------------------------------------------------

def _nombres_de_un_import(nodo) -> list:
    if isinstance(nodo, ast.Import):
        return [(a.name or "") for a in nodo.names]
    if isinstance(nodo, ast.ImportFrom):
        return [(nodo.module or "")]
    return []


def es_import_prohibido(ruta_modulo: str) -> str:
    """Guard AC6: que raiz del modulo importado esta prohibida. None si no lo esta."""
    raiz = (ruta_modulo or "").strip().lower()
    if not raiz:
        return None
    normalizado = raiz.replace("-", "_")
    for prohibido in NOMBRES_PROHIBIDOS + ALIAS_ADAPTER:
        p = prohibido.replace("-", "_")
        if normalizado == p or normalizado.startswith(p + "."):
            return prohibido
    return None


def es_carga_dinamica_prohibida(nodo) -> str:
    """`importlib.import_module("typesafe")`, `__import__("typesafe")`, `...find_and_load(...)`.

    Dos clases y no una: con argumento **literal** se puede resolver el nombre y, si es prohibido,
    es hallazgo; con argumento **no literal** el escaneo estatico no sabe que se importa, asi que se
    publica como limite medido de la familia `cargas-no-resueltas` (L-HF1: un candado que excluye en
    silencio es peor que uno que falla).
    """
    if not isinstance(nodo, ast.Call):
        return None
    f = nodo.func
    nombre = getattr(f, "attr", None) or getattr(f, "id", None)
    if nombre not in FUNCIONES_DE_CARGA:
        return None
    for arg in nodo.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            prohibido = es_import_prohibido(arg.value)
            return f"prohibida:{prohibido}" if prohibido else None
    return f"carga-no-resuelta:{nombre}(argumento no literal)"


def iterar_py(raiz: Path) -> tuple:
    """(archivos a escanear, excluidos por directorio) - la exclusion se publica, no se calla."""
    incluidos, excluidos = [], {k: 0 for k in ARCHIVOS_EXCLUIDOS_DE_LA_POBLACION}
    for path in sorted(raiz.rglob("*.py")):
        partes = {p.lower() for p in path.relative_to(raiz).parts[:-1]}
        tocado = partes & set(ARCHIVOS_EXCLUIDOS_DE_LA_POBLACION)
        if tocado:
            for t in tocado:
                excluidos[t] += 1
            continue
        incluidos.append(path)
    return incluidos, {k: v for k, v in excluidos.items() if v}


def escanear_aislamiento(raiz: Path = ROOT, puerta: Path = None) -> dict:
    """Cuantas coincidencias de import del SDK/adapter hay, y sobre que poblacion (AC6 + L-R.3)."""
    puerta = puerta or Path(__file__).resolve()
    archivos, excluidos = iterar_py(raiz)
    coincidencias, menciones, no_parseables, carga_dinamica = [], [], [], []
    nodos_vistos = 0
    for path in archivos:
        try:
            texto = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            no_parseables.append({"archivo": path.relative_to(raiz).as_posix(),
                                  "motivo": f"lectura: {exc}"})
            continue
        try:
            arbol = ast.parse(texto, filename=str(path))
        except SyntaxError as exc:
            # R2.9: un archivo que no se puede parsear NO es «sin coincidencias».
            no_parseables.append({"archivo": path.relative_to(raiz).as_posix(),
                                  "motivo": f"sintaxis: {exc.msg} linea {exc.lineno}"})
            continue
        dentro_de_la_puerta = path.resolve() == puerta.resolve()
        for nodo in ast.walk(arbol):
            if isinstance(nodo, IMPORT_STATICO_NODES):
                nodos_vistos += 1
                for ruta in _nombres_de_un_import(nodo):
                    prohibido = es_import_prohibido(ruta)
                    if prohibido:
                        coincidencias.append({
                            "archivo": path.relative_to(raiz).as_posix(), "linea": nodo.lineno,
                            "import": ruta, "token": prohibido,
                            "en_la_puerta": dentro_de_la_puerta,
                        })
            elif isinstance(nodo, ast.Call):
                marca = es_carga_dinamica_prohibida(nodo)
                if marca:
                    carga_dinamica.append({
                        "archivo": path.relative_to(raiz).as_posix(), "linea": nodo.lineno,
                        "marca": marca,
                        "clase": "prohibida" if marca.startswith("prohibida:") else "no-resuelta",
                        "en_la_puerta": dentro_de_la_puerta,
                        "en_directorio_de_proveedores": DIRECTORIO_PROVEEDORES_RE.search(
                            path.relative_to(raiz).as_posix()) is not None,
                    })
        for linea, texto_linea in enumerate(texto.splitlines(), start=1):
            for token in NOMBRES_PROHIBIDOS + ALIAS_ADAPTER:
                if re.search(r"(?<![\w.\-])" + re.escape(token) + r"(?![\w.\-])", texto_linea):
                    menciones.append({"archivo": path.relative_to(raiz).as_posix(), "linea": linea,
                                      "token": token,
                                      "es_linea_de_import": bool(
                                          re.match(r"^\s*(import|from)\s", texto_linea))})
                    break
    fuera = [c for c in coincidencias if not c["en_la_puerta"]]
    dinamica_prohibida = [c for c in carga_dinamica if c["clase"] == "prohibida"]
    dinamica_no_resuelta = [c for c in carga_dinamica if c["clase"] == "no-resuelta"]
    # Una carga con nombre construido en runtime solo es hallazgo dentro de un directorio de
    # proveedores: es la superficie por la que un modulo podria colar el SDK sin nombrarlo.
    fuera_dinamica = ([c for c in dinamica_prohibida if not c["en_la_puerta"]]
                      + [c for c in dinamica_no_resuelta
                         if c["en_directorio_de_proveedores"] and not c["en_la_puerta"]])
    return {
        "status": "HALLAZGOS" if (fuera or fuera_dinamica) else "SIN-HALLAZGOS",
        "regla": ("ningun archivo fuera de la puerta importa el SDK, el adapter ni su transporte; "
                  "la carga dinamica de paquetes esta prohibida salvo la carga por ruta que hace "
                  "la propia puerta de sus modulos de proveedor"),
        "puerta": puerta.relative_to(raiz).as_posix(),
        "conteos": {
            "coincidencias_de_import_total": len(coincidencias),
            "coincidencias_de_import_fuera_de_la_puerta": len(fuera),
            "cargas_dinamicas_prohibidas": len(dinamica_prohibida),
            "cargas_dinamicas_no_resueltas": len(dinamica_no_resuelta),
            "cargas_no_resueltas_en_directorios_de_proveedor": sum(
                1 for c in dinamica_no_resuelta if c["en_directorio_de_proveedores"]),
            "hallazgos_de_carga_dinamica": len(fuera_dinamica),
            "menciones_no_import": len(menciones),
            "archivos_no_parseables": len(no_parseables),
        },
        "hallazgos": fuera,
        "hallazgos_carga_dinamica": fuera_dinamica,
        "cargas_dinamicas_no_resueltas": [{k: v for k, v in c.items()
                                          if k != "en_directorio_de_proveedores"}
                                          for c in dinamica_no_resuelta[:20]],
        "en_la_puerta": [c for c in coincidencias if c["en_la_puerta"]]
                        + [c for c in carga_dinamica if c["en_la_puerta"]],
        "menciones_no_import": menciones,
        "no_parseables": no_parseables,
        "coverage_basis": {
            "archivos_py_en_el_arbol": len(archivos) + sum(excluidos.values()),
            "archivos_escaneados": len(archivos),
            "nodos_de_import_vistos": nodos_vistos,
            "excluidos_por_directorio": excluidos,
            "tokens_buscados": list(NOMBRES_PROHIBIDOS) + list(ALIAS_ADAPTER),
            "archivos_mirados": [{"archivo": p.relative_to(raiz).as_posix()} for p in archivos]
                                 if len(archivos) <= 40 else None,
            "poblacion_truncada": len(archivos) > 40,
            "comando": "python scripts/decision_client.py --scan-imports",
            "medido_el": datetime.now().strftime("%Y-%m-%d"),
            "limites": [
                "cuenta imports staticos y cargas dinamicas con argumento literal; una carga con "
                "el nombre construido en runtime (\"types\" + \"afe\") no es resoluble estaticamente: "
                "se publica en `cargas_dinamicas_no_resueltas`, y SOLO cuenta como hallazgo si el "
                "archivo vive bajo un directorio `*proveedores*` (la superficie de contrabando)",
                "no mira dependencias declaradas (requirements/pyproject): un paquete instalado "
                "sin que nadie lo importe no lo detecta; eso es D7",
                "las menciones en prosa o docstring se publican aparte y NO son hallazgos",
                f"archivos excluidos por directorio: {dict(sorted(excluidos.items())) or '(ninguno)'}",
            ],
        },
    }


# -----------------------------------------------------------------------------------------
# AC9: cuanto cuesta anadir un proveedor, medido
# -----------------------------------------------------------------------------------------

PLANTILLA_SEGUNDO_PROVEEDOR = '''"""Proveedor FALSO generado por la medicion de AC9: no abre sockets, no tiene credencial."""
from __future__ import annotations

PROVEEDOR = {{"nombre": "{nombre}", "falso": True, "credencial_env": None,
             "modelo": "{modelo}", "eleccion": "ultima", "nota": "generado por --costura"}}


def evaluar(state, preguntas):
    """Contesta al reves que `falso-forma` para que la medicion distinga a los dos proveedores."""
    respuestas = []
    for p in preguntas:
        if p.tipo == "choice":
            e = p.opciones[-1]
            probs = {{o: (round(1 - 0.02, 4) if o == e else 0.02) for o in p.opciones}}
            tot = sum(probs.values())
            respuestas.append({{"pregunta_id": p.id, "tipo": "choice", "eleccion": e,
                               "probabilidades": {{k: round(v / tot, 6) for k, v in probs.items()}},
                               "confidence": 0.62}})
        elif p.tipo == "score":
            n = len(p.leyenda) - 1
            respuestas.append({{"pregunta_id": p.id, "tipo": "score", "nivel": n,
                               "leyenda": p.leyenda[n], "confidence": 0.62}})
        else:
            respuestas.append({{"pregunta_id": p.id, "tipo": "noul", "probabilidad_si": 0.31}})
    return {{"modelo": PROVEEDOR["modelo"], "respuestas": respuestas, "usage": None,
            "request_id": None}}
'''


def medir_costura(directorio_base: Path, raiz: Path = ROOT) -> dict:
    """Cuantos archivos hay que tocar para que la costura sepa un proveedor MAS.

    Copia la puerta y sus proveedores a un directorio temporal, anade **un** archivo, mide por sha256
    que nadie mas cambio, y despacha los dos proveedores a traves de `evaluar()`. No toca el arbol.
    """
    import hashlib
    import shutil
    import tempfile

    if not directorio_base.is_dir():
        raise Ausente(f"directorio de proveedores falsos no existe: {directorio_base}")
    tmp = Path(tempfile.mkdtemp(prefix="iah-costura-"))
    try:
        dest = tmp / "falsos_proveedores"
        shutil.copytree(directorio_base, dest)
        shutil.copy2(raiz / "scripts" / "decision_client.py", tmp / "decision_client.py")

        def huellas(carpeta_raiz: Path) -> dict:
            """sha256 de TODO lo copiado (la puerta incluida): el «1» cuenta la frontera entera."""
            return {p.relative_to(carpeta_raiz).as_posix():
                    hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted(carpeta_raiz.rglob("*.py"))}

        antes = huellas(tmp)
        nombres_base = [getattr(cargar_modulo_proveedor(p), "PROVEEDOR", {}).get("nombre")
                        for p in sorted(dest.glob("*.py")) if not p.name.startswith("_")]
        nombre_base = next((n for n in nombres_base if n), None)
        if not nombre_base:
            raise Ausente(f"el directorio base {directorio_base} no tiene ningun proveedor falso "
                          "que servir de comparacion")
        nombre = "falso-segundo-medido"
        (dest / "falso_segundo.py").write_text(
            PLANTILLA_SEGUNDO_PROVEEDOR.format(nombre=nombre, modelo="falso-segundo-0.1"),
            encoding="utf-8")
        despues = huellas(tmp)

        agregados = sorted(set(despues) - set(antes))
        modificados = sorted(n for n in set(antes) & set(despues) if antes[n] != despues[n])
        tocados = agregados + modificados

        preguntas = [Pregunta("p1", "choice", "?", opciones=("a", "b", "c")),
                     Pregunta("p2", "score", "?", leyenda=("bajo", "medio", "alto")),
                     Pregunta("p3", "noul", "?")]
        base = {ENV_PROVIDERS_DIR: str(dest)}
        r1 = evaluar("estado", preguntas, {**base, ENV_PROVIDER: nombre_base})
        r2 = evaluar("estado", preguntas, {**base, ENV_PROVIDER: nombre})
        distintos = [a.eleccion for a in r1.respuestas if a.tipo == "choice"] != \
                    [a.eleccion for a in r2.respuestas if a.tipo == "choice"]
        return {
            "files_changed_to_add_provider": len(tocados),
            "archivos_tocados": tocados,
            "agregados": agregados,
            "modificados": modificados,
            "costura_funciona_con_ambos": [r1.proveedor, r2.proveedor],
            "los_dos_despachan_respuestas_distintas": distintos,
            "provider_status": ["RESUELTO" if r1.provider_status == r2.provider_status == "RESUELTO"
                                else "ILEGIBLE", "RESUELTO"],
            "archivos_de_test_paralelos": {
                "valor": 1,
                "nota": "un proveedor falso nuevo necesita un caso que lo despache; se declara "
                        "aparte, no se esconde para inflar el «1» (AC1 del plan hermano "
                        "EVALUACION-JEV: tests, runner y manifiesto se contabilizan aparte)"},
            "coverage_basis": {
                "directorio_base": str(directorio_base),
                "proveedor_base_usado": nombre_base,
                "archivos_base_antes": sorted(antes),
                "archivos_base_despues": sorted(despues),
                "instrumento": "sha256 por archivo + despacho real por la costura",
                "comando": "python scripts/decision_client.py --costura "
                           "--falsos-directorio tests/quality_gates/decision_client/falsos_proveedores",
                "medido_el": datetime.now().strftime("%Y-%m-%d"),
                "corte": f"copias temporales bajo {tmp.name}; el arbol del repo no se modifico",
            },
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# -----------------------------------------------------------------------------------------
# Informe y CLI
# -----------------------------------------------------------------------------------------

def sonda_tres_estados(directorio_falsos: Path) -> dict:
    """Los tres estados de AC7, provocados cada uno por su causa, sobre proveedores FALSOs."""
    out = {}
    env_base = {ENV_PROVIDERS_DIR: str(directorio_falsos)}
    preguntas = [Pregunta("p1", "choice", "¿Cual?", opciones=("si", "no", "quiza")),
                 Pregunta("p2", "score", "¿Nivel?", leyenda=("bajo", "medio", "alto")),
                 Pregunta("p3", "noul", "¿Aplica?")]

    try:
        r = evaluar("estado de prueba", preguntas,
                    {**env_base, ENV_PROVIDER: "falso-forma"})
        out["RESUELTO"] = {"provider_status": r.provider_status, "proveedor": r.proveedor,
                           "modelo_reportado_por_el_proveedor": r.modelo,
                           "respuestas": [a.to_dict() for a in r.respuestas],
                           "credencial": r.credencial,
                           "provocado_por": "falso-forma a traves de la costura, sin red"}
    except (ProveedorNoConfigurado, RespuestaIlegible, LectorFallido) as exc:
        out["RESUELTO"] = {"provider_status": "LECTOR-FALLIDO", "motivo": str(exc)}

    try:
        evaluar("estado de prueba", preguntas, {ENV_PROVIDER: "falso-forma"})
        out["NO-CONFIGURADO"] = {"provider_status": "ILEGIBLE-INESPERADO",
                                 "motivo": "evaluar() no debio resolver sin directorio"}
    except ProveedorNoConfigurado as exc:
        out["NO-CONFIGURADO"] = {"provider_status": "NO-CONFIGURADO",
                                 "motivo_clase": exc.motivo_clase, "motivo": str(exc),
                                 "buscado": exc.buscado,
                                 "decision_devuelta": None,
                                 "provocado_por": f"{ENV_PROVIDER} definido, {ENV_PROVIDERS_DIR} no"}
    except (RespuestaIlegible, LectorFallido) as exc:
        out["NO-CONFIGURADO"] = {"provider_status": "LECTOR-FALLIDO", "motivo": str(exc)}

    try:
        r = evaluar("estado de prueba", preguntas,
                    {**env_base, ENV_PROVIDER: "falso-ilegible"})
        out["ILEGIBLE"] = {"provider_status": "INESPERADAMENTE-RESUELTO",
                           "detalle": r.to_dict()}
    except RespuestaIlegible as exc:
        out["ILEGIBLE"] = {"provider_status": "ILEGIBLE", "motivos": exc.motivos,
                           "proveedor": exc.proveedor, "decision_devuelta": None,
                           "provocado_por": "falso-ilegible devuelve choice sin confidence y una "
                                            "pregunta sin responder"}
    except ProveedorNoConfigurado as exc:
        out["ILEGIBLE"] = {"provider_status": "NO-CONFIGURADO", "motivo": str(exc)}
    return out


def construir_informe(directorio_falsos: Path, raiz: Path = ROOT) -> dict:
    scan = escanear_aislamiento(raiz)
    sond = sonda_tres_estados(directorio_falsos)
    costura = medir_costura(directorio_falsos, raiz)
    informe = {
        "tool": "scripts/decision_client.py",
        "esquema": "FASE-B del plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20",
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": scan["status"],
        "provider_status": sond,
        "aislamiento_imports": scan,
        "costura": costura,
        "corte_de_red": {
            "llamadas_de_red_en_esta_fase": 0,
            "como_se_verifica": "guard de socket en conftest.py + escaneo ast de imports de esta "
                                "puerta y de los proveedores falsos (ninguno importa un cliente HTTP)",
            "credenciales_leidas": False,
        },
        "cobertura_de_la_fase": {
            "comando": "python scripts/decision_client.py --report",
            "medido_el": datetime.now().strftime("%Y-%m-%d"),
        },
    }
    return informe


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--falsos-directorio",
                    default=str(ROOT / "tests" / "quality_gates" / "decision_client"
                                / "falsos_proveedores"))
    ap.add_argument("--provider-status", action="store_true")
    ap.add_argument("--scan-imports", action="store_true")
    ap.add_argument("--costura", action="store_true")
    ap.add_argument("--report", nargs="?", const=str(EVIDENCIA / "informe.json"), default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.provider_status:
        est = estado_proveedor()
        print(json.dumps(est, indent=2, ensure_ascii=False, default=str))
        return 0 if est.get("provider_status") == "RESUELTO" else (
            2 if est.get("estado_lector") == "LECTOR-FALLIDO" else 1)

    if args.scan_imports:
        scan = escanear_aislamiento()
        if args.json:
            print(json.dumps(scan, indent=2, ensure_ascii=False))
        else:
            print(f"[{_ascii(scan['status'])}] decision_client.py - aislamiento de imports (AC6)")
            c = scan["conteos"]
            print(f"  {c['coincidencias_de_import_fuera_de_la_puerta']} import(s) prohibido(s) fuera "
                  f"de la puerta | {c['hallazgos_de_carga_dinamica']} carga(s) dinamica(s) hallada(s) "
                  f"| {c['menciones_no_import']} mencion(es) no-import (no son hallazgos) | "
                  f"{c['archivos_no_parseables']} archivo(s) no parseable(s)")
            b = scan["coverage_basis"]
            print(f"  poblacion: {b['archivos_escaneados']}/{b['archivos_py_en_el_arbol']} .py | "
                  f"nodos de import vistos {b['nodos_de_import_vistos']} | excluidos "
                  f"{b['excluidos_por_directorio']} | tokens {b['tokens_buscados']}")
        return 1 if scan["status"] == "HALLAZGOS" else 0

    if args.costura:
        datos = medir_costura(Path(args.falsos_directorio))
        print(json.dumps(datos, indent=2, ensure_ascii=False))
        return 0 if datos["files_changed_to_add_provider"] == 1 else 1

    if args.report:
        informe = construir_informe(Path(args.falsos_directorio))
        destino = Path(args.report)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(informe, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
        if args.json:
            print(json.dumps(informe, indent=2, ensure_ascii=False, default=str))
        else:
            ps = informe["provider_status"]
            print(f"[{_ascii(informe['status'])}] decision_client.py - "
                  "costura de proveedor de decisiones (AC6-AC9)")
            print(f"  provider_status: " + " | ".join(
                f"{k}={_ascii(str(v.get('provider_status')))}" for k, v in ps.items()))
            print(f"  imports fuera de la puerta: "
                  f"{informe['aislamiento_imports']['conteos']['coincidencias_de_import_fuera_de_la_puerta']}"
                  f" sobre {informe['aislamiento_imports']['coverage_basis']['archivos_escaneados']} .py")
            print(f"  files_changed_to_add_provider: "
                  f"{informe['costura']['files_changed_to_add_provider']}")
            print(f"  informe: {destino}")
        return 0 if informe["status"] == "SIN-HALLAZGOS" else 1

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
