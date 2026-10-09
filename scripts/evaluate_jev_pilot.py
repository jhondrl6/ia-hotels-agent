#!/usr/bin/env python3
"""Instrumento del piloto Jev (EVALUACION-JEV-TYPESAFE-2026-09-21).

`prepare`, `check`, `report` y `decide` son LOCALES y deterministas: NO importan clientes de
inferencia, NO abren red y NO leen credenciales, y esa regla la goberna `FORBIDDEN_MODULES` con su
test. `run` llego en FASE-B (2026-10-03) y no cambia el contrato offline: se construye solo con
preflight de AC12 y presupuesto de AC8 reservados, y el SDK lo carga la puerta
(`scripts/decision_client.py`), que es el unico sitio donde AC6 admite ese import. `report` y
`decide` llegaron en FASE-B.2 (2026-10-04) cerrando CR-1..CR-4: reproducen la comparacion y aplican
la regla congelada desde los registros persistidos, con cero llamadas. `report`/`decide` sin insumos
se niegan con EXIT 2 y su causa escrita, y `decide` emite pero no elige cuando un criterio queda
NO-EVALUABLE (EXIT 3). Un par de triaje es (target_plan, lesson_id) con una etiqueta humana
{pertinente|no_pertinente|insuficiente} e importancia.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

MUESTRA_SCHEMA = "jev-pilot-muestra/v1"
ETIQUETAS_SCHEMA = "jev-pilot-etiquetas/v1"
PROTOCOLO_SCHEMA = "jev-pilot-protocolo/v1"

# Claves que jamas pueden viajar en el payload que veran los modelos.
LABEL_KEYS = {"label", "etiqueta", "importance", "importancia", "reviewer",
              "reviewed_at", "human_reviewed", "revisado", "aceptado"}
# Modulos de proveedor/red que el modo offline tiene prohibido importar.
# FASE-B (2026-10-03): el nombre REAL del paquete medido es `typesafe_sdk` (distribucion
# `typesafe-sdk`); `import typesafe` da ModuleNotFoundError, o sea la lista vieja bloqueaba un
# nombre que no existe y dejaba pasar el que si. Se anaden las dos grafias del nombre real.
FORBIDDEN_MODULES = {"typesafe", "typesafe_sdk", "typesafe-sdk", "httpx", "httpx2",
                     "httpcore", "httpcore2", "tenacity", "anthropic", "openai",
                     "requests", "urllib.request"}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _split_for_plan(target_plan: str) -> str:
    """Split determinista por plan: todas las parejas de un mismo plan caen en
    el mismo set, lo que hace imposible que un plan se filtre a ambos."""
    digest = hashlib.sha256(target_plan.encode("utf-8")).digest()
    return "eval" if digest[0] % 2 == 0 else "dev"


def payload_for_models(muestra: dict) -> list[dict]:
    """Proyeccion del input que veran los modelos: solo id y fragmento."""
    return [
        {"pair_id": p["pair_id"], "input_fragment": p["input_fragment"]}
        for p in muestra.get("pairs", [])
    ]


def prepare(candidates: list[dict], temporal_cut: str, corpus_source: str) -> tuple[dict, dict]:
    """Construye muestra (inputs saneados) y etiquetas (separadas) desde
    candidatos. Las etiquetas quedan sin revisar: el agente prepara, no
    etiqueta. El resultado es BORRADOR, nunca CONGELADA."""
    seen: set[tuple[str, str]] = set()
    pairs: list[dict] = []
    exclusions: list[dict] = []
    labels: list[dict] = []
    for cand in candidates:
        plan = cand["target_plan"]
        lesson = cand["lesson_id"]
        key = (plan, lesson)
        if key in seen:
            continue
        seen.add(key)
        if cand.get("excluded"):
            exclusions.append({"pair_id": f"{plan}::{lesson}",
                               "motivo": cand.get("exclude_reason", "sin_motivo")})
            continue
        sanitized = cand["sanitized_text"]
        pair_id = f"{plan}::{lesson}"
        pairs.append({
            "pair_id": pair_id,
            "target_plan": plan,
            "target_phase": cand.get("target_phase", ""),
            "lesson_id": lesson,
            "input_fragment": sanitized,
            "original_sha256": sha256_text(cand["original_text"]),
            "sanitized_sha256": sha256_text(sanitized),
            "split": _split_for_plan(plan),
        })
        labels.append({
            "pair_id": pair_id,
            "label": None,               # pertinente|no_pertinente|insuficiente: lo fija un humano
            "importance": None,          # alta|media|baja
            "reviewer": None,
            "reviewed_at": None,
        })

    dev = sum(1 for p in pairs if p["split"] == "dev")
    evaln = sum(1 for p in pairs if p["split"] == "eval")
    muestra = {
        "schema": MUESTRA_SCHEMA,
        "status": "BORRADOR",
        "corpus_source": corpus_source,
        "temporal_cut": temporal_cut,
        "review": {"human_reviewed": False, "reviewer": None, "reviewed_at": None},
        "pairs": pairs,
        "exclusions": exclusions,
        "counts": {"total": len(pairs), "dev": dev, "eval": evaln,
                   "excluidos": len(exclusions)},
    }
    etiquetas = {"schema": ETIQUETAS_SCHEMA, "review_status": "sin_revisar",
                 "labels": labels}
    return muestra, etiquetas


def _load_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def check(muestra_path: Path, etiquetas_path: Path) -> dict:
    """Verifica los controles mecanicos. Su exito solo acredita esquema, hashes,
    splits, fuga de etiquetas y congelacion honesta: no juicio humano ni gasto."""
    muestra = _load_json(muestra_path)
    etiquetas = _load_json(etiquetas_path) if Path(etiquetas_path).exists() else {"labels": []}
    findings: list[dict] = []

    if muestra.get("schema") != MUESTRA_SCHEMA:
        findings.append({"guard": "schema", "ok": False, "motivo": "schema muestra invalido"})
    else:
        findings.append({"guard": "schema", "ok": True, "motivo": ""})

    # Guard: integridad de contenido por SHA.
    for p in muestra.get("pairs", []):
        if sha256_text(p["input_fragment"]) != p.get("sanitized_sha256"):
            findings.append({"guard": "content_sha", "ok": False, "pair_id": p["pair_id"],
                             "motivo": "el fragmento no casa con sanitized_sha256"})
    if not any(f["guard"] == "content_sha" and not f["ok"] for f in findings):
        findings.append({"guard": "content_sha", "ok": True, "motivo": ""})

    # Guard: fuga de plan entre splits.
    plans_by_split: dict[str, set[str]] = {"dev": set(), "eval": set()}
    for p in muestra.get("pairs", []):
        plans_by_split.setdefault(p["split"], set()).add(p["target_plan"])
    leak = plans_by_split.get("dev", set()) & plans_by_split.get("eval", set())
    if leak:
        findings.append({"guard": "split_disjoint", "ok": False,
                         "motivo": f"planes en ambos splits: {sorted(leak)}"})
    else:
        findings.append({"guard": "split_disjoint", "ok": True, "motivo": ""})

    # Guard: las etiquetas no entran a los inputs que veran los modelos.
    leaked = [p["pair_id"] for p in muestra.get("pairs", []) if LABEL_KEYS & set(p.keys())]
    leaked += [pair for pair in payload_for_models(muestra)
               if LABEL_KEYS & set(pair.keys())]
    if leaked:
        findings.append({"guard": "labels_not_in_payload", "ok": False,
                         "motivo": f"etiquetas filtradas a inputs: {sorted(set(leaked))}"})
    else:
        findings.append({"guard": "labels_not_in_payload", "ok": True, "motivo": ""})

    # Guard: muestra sin revision humana no puede declararse CONGELADA.
    review = muestra.get("review", {})
    frozen = muestra.get("status") == "CONGELADA"
    if frozen and not (review.get("human_reviewed") and review.get("reviewer")
                       and review.get("reviewed_at")):
        findings.append({"guard": "unreviewed_not_frozen", "ok": False,
                         "motivo": "status CONGELADA sin revision humana con dueno y fecha"})
    else:
        findings.append({"guard": "unreviewed_not_frozen", "ok": True, "motivo": ""})

    ok = all(f["ok"] for f in findings)
    return {"check_status": "OK" if ok else "FALLO",
            "muestra_status": muestra.get("status"),
            "counts": muestra.get("counts"),
            "findings": findings}


def score(numerator: int, denominator: int) -> dict:
    """Cociente con numerador/denominador publicados. Denominador cero NO es
    100 % ni 0 %: se reporta None con motivo."""
    if denominator == 0:
        return {"value": None, "numerator": numerator, "denominator": denominator,
                "motivo": "denominador_cero"}
    return {"value": round(numerator / denominator, 4), "numerator": numerator,
            "denominator": denominator, "motivo": ""}


def metrics(recovery: dict, classification: dict, e2e: dict) -> dict:
    """Envuelve los cuatro cocientes definidos en el maestro (recuperacion,
    clasificacion, extremo a extremo) manteniendo denominadores separados."""
    return {
        "recuperacion": score(recovery["num"], recovery["den"]),
        "precision_entre_propuestas": score(classification["prec_num"], classification["den"]),
        "recall_importante_candidatos": score(classification["rec_num"], classification["den"]),
        "extremo_a_extremo": score(e2e["num"], e2e["den"]),
    }


# --- FASE-B, pata (b): attempts, error_kind y usage_normalized ------------------------------
# La costura (scripts/decision_client.py) conserva pedido/modelo/tiempo --la pata (a), ejecutada
# en 4621049-- y declara que estas tres NO le pertenecen: nacen en el ledger del runner.
# El SDK vive fuera del sys.path del producto; estas funciones NO lo importan: reciben objetos y
# clasifican por nombre de clase, o sea son probables sin red y sin el paquete instalado.

CLASES_DE_ERROR = {
    "TypeSafeAuthenticationError": "auth",
    "TypeSafePermissionDeniedError": "auth",
    "TypeSafeRateLimitError": "cuota",
    "TypeSafeAPIConnectionError": "conexion",
    "TypeSafeAPITimeoutError": "timeout",
    "TypeSafeAPIResponseValidationError": "respuesta_ilegible",
    "TypeSafeBadRequestError": "peticion",
    "TypeSafeUnprocessableEntityError": "peticion",
    "TypeSafeNotFoundError": "peticion",
    "TypeSafeInternalServerError": "servidor",
}


def error_kind_de(exc: BaseException) -> dict:
    """Clase del fallo por el nombre real de la excepcion y su `status` (AC9).

    Camina el MRO: una subclase del SDK se clasifica por su antecesor conocido, no por `Exception`.
    DA-C3/AC2: un fallo y una respuesta negativa no colapsan, y `desconocido` no es `ausente`.
    """
    for cls in type(exc).__mro__:
        clase = CLASES_DE_ERROR.get(cls.__name__)
        if clase:
            return {"error_kind": clase, "clase": type(exc).__name__,
                    "status": getattr(exc, "status", None)}
    return {"error_kind": "desconocido", "clase": type(exc).__name__,
            "status": getattr(exc, "status", None)}


def normalizar_usage(usage) -> dict:
    """Tokens observados, separados del coste calculado y del cargo facturado (AC8/AC10).

    Medido en el SDK 0.7.0: `Usage()` resuelve `(None, None)`, o sea «uso desconocido» es un estado
    del tipo y no un cero. Un timeout sin `usage` tampoco es cero: `sin_usage` conserva la reserva.
    Acepta el objeto del SDK y el dict ya normalizado que devuelve la puerta, porque el ledger se
    rellena con las dos formas y un dict no puede degenerar en `desconocido` por no saber leerlo.
    """
    def _entero(valor):
        return valor if isinstance(valor, int) and not isinstance(valor, bool) else None

    def _campo(nombre):
        return usage.get(nombre) if isinstance(usage, dict) else getattr(usage, nombre, None)

    if usage is None:
        return {"input_tokens": None, "output_tokens": None, "total": None,
                "estado": "sin_usage", "libera_reserva_como_cero": False}
    entrada = _entero(_campo("input_tokens"))
    salida = _entero(_campo("output_tokens"))
    if entrada is not None and salida is not None:
        estado = "observado"
    elif entrada is not None or salida is not None:
        estado = "parcial"
    else:
        estado = "desconocido"
    total = None if (entrada is None or salida is None) else entrada + salida
    return {"input_tokens": entrada, "output_tokens": salida, "total": total,
            "estado": estado, "libera_reserva_como_cero": False}


def nuevo_ledger(proveedor: str, modelo_solicitado: str) -> dict:
    """Fila del ledger antes de cualquier intento: `attempts` en 0 y nada observado."""
    return {"proveedor": proveedor, "modelo_solicitado": modelo_solicitado,
            "modelo_efectivo": None, "attempts": 0, "intentos": [], "error_kind": None,
            "usage_normalized": {"input_tokens": None, "output_tokens": None, "total": None,
                                 "estado": "no_intentada", "libera_reserva_como_cero": False},
            "coste_calculado": None, "cargo_facturado": None, "estado": "NO-EJERCITADO"}


def reservar_presupuesto(cuenta: dict, limites: dict) -> dict:
    """AC8: la reserva se comprueba ANTES de cada intento; falta o agotamiento implican cero envios.

    `max_reintentos` distinto de 0 se niega: el default medido del SDK (2) hace 3 intentos por
    llamada ante un 429 y esos intentos no estan en el ledger. Un techo de tokens en null solo se
    admite con su autorizacion declarada, porque la corrida que mide el techo no puede exigir el
    techo que todavia no existe.

    B2-1e: un techo por llamada **ya rebasado** en la cuenta corta el siguiente envio. El exceso del
    intento N no se pudo predecir antes de N (los tokens se conocen despues), pero maestro §115 manda
    detener cuando la contabilidad ya no acota: seguir enviando con el techo roto acumularia gasto
    contra un presupuesto que el protocolo declara agotado.
    """
    motivos: list[str] = []
    llamadas = limites.get("llamadas")
    if not isinstance(llamadas, int) or isinstance(llamadas, bool) or llamadas <= 0:
        motivos.append("presupuesto_de_llamadas_ausente")
    usadas = cuenta.get("llamadas_usadas")
    if not isinstance(usadas, int) or isinstance(usadas, bool):
        motivos.append("cuenta_de_llamadas_ausente")
    elif isinstance(llamadas, int) and usadas >= llamadas:
        motivos.append("llamadas_agotadas")
    if limites.get("max_reintentos") != 0:
        motivos.append("reintentos_sin_ledger")
    timeout = limites.get("timeout_s")
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout <= 0:
        motivos.append("timeout_ausente")
    autorizacion = limites.get("autorizacion_de_null") or {}
    exceso_observado = []
    for clave, campo in (("tokens_in", "tokens_in_max"), ("tokens_out", "tokens_out_max")):
        techo = limites.get(clave)
        if techo is None and not autorizacion.get("declarada"):
            motivos.append(f"techo_de_{clave}_sin_declarar")
        observado = cuenta.get(campo)
        # comparacion de tipo y valor: un `True` en la cuenta no es un token de 1 (el guard viejo
        # tragaba `1 == True`), y un techo null no tiene con que comparar.
        if (isinstance(techo, int) and not isinstance(techo, bool)
                and isinstance(observado, int) and not isinstance(observado, bool)
                and observado > techo):
            motivos.append(f"techo_rebasado_de_{clave}:{observado}>{techo}")
            exceso_observado.append({"campo": clave, "techo": techo, "observado": observado})
    restantes = (llamadas - usadas) if (isinstance(llamadas, int)
                                         and isinstance(usadas, int)) else None
    return {"reservado": not motivos, "motivos": motivos, "llamadas_restantes": restantes,
            "exceso_observado": exceso_observado}


def registrar_intento(ledger: dict, *, resultado: str, excepcion=None, usage=None,
                      modelo_efectivo=None, duracion_ms=None) -> dict:
    """Suma un intento al ledger con su clase de error y su usage normalizado."""
    ledger["attempts"] += 1
    fila = {"n": ledger["attempts"], "resultado": resultado, "duracion_ms": duracion_ms}
    if excepcion is not None:
        clasificado = error_kind_de(excepcion)
        ledger["error_kind"] = clasificado["error_kind"]
        fila.update(clasificado)
    if usage is not None:
        ledger["usage_normalized"] = normalizar_usage(usage)
    if modelo_efectivo is not None:
        ledger["modelo_efectivo"] = modelo_efectivo
    ledger["intentos"].append(fila)
    ledger["estado"] = "FALLO" if excepcion is not None else "EJERCITADO"
    return ledger


def _refuse(name: str, faltan: list) -> int:
    """Negacion con causa escrita y EXIT nombrado: sin insumos no se emite nada (AC10).

    FASE-B.2 reemplaza la negacion historica de `decide` (que se negaba siempre) por esta: el modo
    ya existe, y lo que sigue negado es emitir sin los registros que lo sustentan. El numero 2 se
    conserva porque es el que el contrato de FASE-A prometio (`main(["decide"]) == 2`) y porque
    `run` ya lo usa por la misma razon.
    """
    sys.stderr.write(
        f"{name} exige {', '.join(faltan)}: sin ellos no hay registros que reproducir, y publicar "
        f"un cociente sin insumo seria rellenarlo a mano (AC10). Este modo no abre red ni "
        f"instancia clientes.\n")
    return 2


# --- FASE-B, paso 1a (2026-10-03): el modo `run`, con preflight y presupuesto antes de enviar ---
# El runner NO importa el SDK: lo carga la puerta (`scripts/decision_client.py`), que es el unico
# sitio donde AC6 admite ese import. Aqui se goberna CUANDO se construye: sin preflight de AC12 y
# sin reserva de AC8 no hay ni un intento, y eso se publica con su causa en vez de callarse.

PREFLIGHT_SCHEMA = "jev-pilot-preflight/v1"
ESTADOS_PREFLIGHT_OBLIGATORIOS = {"habilitacion_declarada": True, "sdk_instalado": True,
                                  "autenticacion_real": "AUTENTICADA"}
# REL-1 (H14 de FASE-C, dictado D4 del 2026-10-05): un brazo puede declarar que un estado material no
# le aplica, pero solo se lo excusa si el motivo viene escrito en el mismo valor. Un `NO-APLICA` a secas
# no es una declaracion, es la ausencia del estado con mejor cara.
PREFLIGHT_NO_APLICA = "NO-APLICA"
_SEPARADORES_NO_APLICA = ":\u00a0 \t-–—"
PROVEEDOR_JEV = "jev"
CAMPOS_CANDIDATO_PERMITIDOS = ("id", "enunciado")
# `planes_que_lo_citan` y las fechas de aceptacion quedan fuera por el maestro §Corpus: metadatos
# que revelan la etiqueta no entran al contexto que ven los modelos.
ETIQUETA_DE_NINGUNA = "ninguna-aplica"


def _puerta():
    """Carga la costura por ruta. Es la unica puerta de acceso al SDK (AC6)."""
    script = Path(__file__).resolve().parent / "decision_client.py"
    spec = importlib.util.spec_from_file_location("decision_client_del_piloto", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _casado(valor, esperado) -> bool:
    """El estado casa con lo que se exige, por tipo y por valor.

    `1 == True` en Python, asi que el guard historico aceptaba un `1` en el preflight como si
    declarara el SDK instalado. D4 (2026-10-05) manda cortar con cualquier otro literal, y un entero
    —o un `"True"` escrito como texto— es otro literal, no la declaracion pedida.
    """
    return type(valor) is type(esperado) and valor == esperado


def _no_aplica_con_motivo(valor) -> str:
    """El motivo que el brazo escribio junto a su `NO-APLICA`, o cadena vacia si no excusa nada.

    Medido en `FASE-C/preflight.json` (deepseek, `sdk_instalado`): el valor real es
    `"NO-APLICA: el comparador es un API HTTP, no un SDK; el contrato del brazo es ..."`. Se excusa
    solo esa forma. Un `NO-APLICA` pelado, uno sin texto despues del separador, `NO-APLICABLE` (que
    es otra palabra), las minusculas o un valor que no sea texto cortan igual que antes.
    """
    if not isinstance(valor, str):
        return ""
    texto = valor.strip()
    if not texto.startswith(PREFLIGHT_NO_APLICA):
        return ""
    resto = texto[len(PREFLIGHT_NO_APLICA):]
    if resto and resto[0] not in _SEPARADORES_NO_APLICA:
        return ""
    return resto.strip(_SEPARADORES_NO_APLICA).strip()


def revisar_preflight(ruta_preflight: Path, proveedor: str) -> dict:
    """AC12 como precondicion de AC8: los cuatro estados por proveedor, y tres se exigen.

    `cuota_o_saldo` se **declara** pero no se exige: medido el 2026-10-03, `typesafe_sdk` 0.7.0 no
    expone superficie de saldo, asi que exigirla forzaria a fingirla. Lo que no esta se estampa con
    su motivo, no con un valor que parezca favorable.

    REL-1: un estado exigido tambien se satisface cuando el propio preflight del brazo declara
    `NO-APLICA` con su motivo. La excusa nunca es silenciosa: sale en `no_aplica_declarados`.
    """
    ruta = Path(ruta_preflight)
    if not ruta.exists():
        return {"ok": False, "motivos": [f"preflight-ausente:{ruta.as_posix()}"]}
    datos = _load_json(ruta)
    if datos.get("schema") != PREFLIGHT_SCHEMA:
        return {"ok": False, "motivos": [f"preflight-schema:{datos.get('schema')!r}"]}
    registro = (datos.get("proveedores") or {}).get(proveedor)
    if not isinstance(registro, dict):
        return {"ok": False, "motivos": [f"preflight-sin-proveedor:{proveedor}"]}
    motivos = []
    no_aplica = {}
    for clave, esperado in ESTADOS_PREFLIGHT_OBLIGATORIOS.items():
        valor = registro.get(clave)
        if _casado(valor, esperado):
            continue
        motivo = _no_aplica_con_motivo(valor)
        if motivo:
            no_aplica[clave] = motivo
            continue
        motivos.append(f"preflight-{clave}={valor!r}")
    return {"ok": not motivos, "motivos": motivos, "registro": registro,
            "no_aplica_declarados": no_aplica,
            "cuota_o_saldo": registro.get("cuota_o_saldo"),
            "modelo_efectivo_preflight": registro.get("modelo_efectivo_preflight")}


def limites_desde_protocolo(protocolo: dict, *, autorizacion_de_null: dict = None) -> dict:
    """Del `limites_gasto` y `parametros` del protocolo a los limites que exige `reservar_presupuesto`.

    La autorizacion de los dos null NO se infiere del protocolo: la pasa quien corre, porque el acto
    de medir el techo no puede exigir el techo que todavia no existe.
    """
    gastos = protocolo.get("limites_gasto") or {}
    parametros = protocolo.get("parametros") or {}
    retry = parametros.get("retry_policy") or {}
    return {"llamadas": gastos.get("llamadas"), "tokens_in": gastos.get("tokens_in"),
            "tokens_out": gastos.get("tokens_out"), "usd": gastos.get("usd"),
            "max_reintentos": retry.get("max_retries"),
            "timeout_s": parametros.get("timeout_s"),
            "autorizacion_de_null": autorizacion_de_null or {}}


def _tokens(texto: str) -> set:
    return {t for t in re.findall(r"[a-z0-9]+", (texto or "").lower()) if len(t) > 3}


def recuperacion_fria(consulta: str, lecciones: list, k: int = 8) -> dict:
    """La capa fria congelada: overlap lexico determinista, desempate por id, solo id + enunciado.

    No mira etiquetas ni metadatos del plan, y no se afina mirando el conjunto de evaluacion: por eso
    el orden es estable por id y no por el puntaje del dia.
    """
    consulta_tokens = _tokens(consulta)
    puntuadas = []
    for leccion in lecciones:
        if not isinstance(leccion, dict) or not leccion.get("id"):
            continue
        similitud = len(consulta_tokens & _tokens(leccion.get("enunciado", "")))
        puntuadas.append((similitud, leccion["id"], leccion))
    puntuadas.sort(key=lambda t: (-t[0], t[1]))
    candidatos = [{"id": l["id"],
                   "enunciado": (l.get("enunciado") or "")[:300]}
                  for _, _, l in puntuadas[:k]]
    return {"candidatos": candidatos, "poblacion": len(lecciones), "k": k,
            "desempate": "similitud desc, id asc", "empates_en_el_corte": None}


def preguntas_para_par(pair_id: str, candidatos: list, rubrica: dict) -> dict:
    """Una pregunta `choice` por consulta fria: los k candidatos + la salida «no aplica».

    La rubrica del protocolo fija `pertinente|no_pertinente|insuficiente`; la opcion de ninguna es la
    que la skill del fabricante pide cuando nada casa, y evita que elegir siempre sea gratis.
    """
    criterios = {c["id"]: c["enunciado"] for c in candidatos}
    criterios[ETIQUETA_DE_NINGUNA] = "Ninguna de las lecciones propuestas es pertinente para esta consulta."
    return {pair_id: {"type": "choice",
                      "instructions": ("Decide cual de estas lecciones capitalizadas es PERTINENTE para la "
                                       "consulta fria. Rubrica: "
                                       f"{rubrica.get('valores')}; importancia: {rubrica.get('importancia')}."),
                      "criteria": criterios}}


def _estado_cuenta(out_dir: Path) -> dict:
    ruta = Path(out_dir) / "consumo.json"
    if not ruta.exists():
        return {"llamadas_usadas": 0, "intentos": 0, "usage_estados": [],
                 "tokens_in_max": None, "tokens_out_max": None}
    return _load_json(ruta)


def _persistir(out_dir: Path, nombre: str, datos) -> Path:
    destino = Path(out_dir) / nombre
    destino.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(datos, str):
        destino.write_text(datos, encoding="utf-8")
    else:
        destino.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destino


def registrar_envio_en_cuenta(out_dir: Path, cuenta: dict, fila: dict,
                             *, nombre: str = "consumo.json") -> dict:
    """B2-1d/AC8: sumar un envio a la cuenta de etapa y dejarla persistida en el mismo acto.

    La funcion existe porque el defecto era de separacion, no de aritmetica: `run` era el unico que
    escribia `consumo.json`, mientras que un brazo despachado por un arnes sumaba la misma aritmetica
    en su propia memoria y no publicaba nada. Medido en FASE-C: la cuenta publicada se quedo en 2
    llamadas con `tokens_out_max` 145 (la foto del brazo jev) mientras la cuenta real al cerrar era 4
    llamadas y 158. Aqui quien suma publica, asi que contar sin quedarse en disco ya no es un camino.

    Se persiste por envio y no solo al cerrar la corrida: si el proceso muere a mitad, la cuenta que
    lee el siguiente `run` es la que ya se gasto, que es lo que AC8 pide entre sesiones.
    """
    cuenta["llamadas_usadas"] += 1
    cuenta["intentos"] += fila["attempts"]
    uso = fila["usage_normalized"]
    if uso.get("input_tokens") is not None:
        cuenta["tokens_in_max"] = max(cuenta.get("tokens_in_max") or 0, uso["input_tokens"])
    if uso.get("output_tokens") is not None:
        cuenta["tokens_out_max"] = max(cuenta.get("tokens_out_max") or 0, uso["output_tokens"])
    if uso.get("estado") not in ("observado",):
        cuenta.setdefault("usage_estados", []).append(uso.get("estado"))
    _persistir(Path(out_dir), nombre, cuenta)
    return cuenta


def _nulos_de(objeto, ruta="") -> list:
    """Rutas punteadas cuyo valor es `null`, para gobernar cuales se admiten."""
    nulos: list[str] = []
    if isinstance(objeto, dict):
        for clave, valor in objeto.items():
            nulos += _nulos_de(valor, f"{ruta}.{clave}" if ruta else str(clave))
    elif isinstance(objeto, list):
        for i, valor in enumerate(objeto):
            nulos += _nulos_de(valor, f"{ruta}[{i}]")
    elif objeto is None:
        nulos.append(ruta)
    return nulos


# Los ocho umbrales gobernables del protocolo. Viven aqui como datos, no repartidos en ifs: una
# cifra que se valida en dos sitios distintos caduca en uno de ellos.
PROTOCOLO_UMBRALES = (
    ("parametros.retry_policy.max_retries", "entero"),
    ("parametros.timeout_s", "numero"),
    ("limites_gasto.llamadas", "entero"),
    ("criterios_adopcion.cobertura_min", "fraccion"),
    ("criterios_adopcion.suficiencia_minima", "fraccion"),
    ("criterios_adopcion.margen_vs_deepseek", "fraccion"),
    ("criterios_adopcion.latencia_max", "numero"),
    ("reglas_recuperacion.k", "entero"),
)
# Los unicos null que el protocolo admite en su forma actual, con la condicion que los habilita.
# `usd` no es un pendiente disfrazado: el operador lo declaro FUERA DE GOBERNANZA el 2026-10-03, y
# esa declaracion tiene que estar escrita en el `motivo` para que el null valga.
NULOS_ADMITIDOS = {"limites_gasto.tokens_in", "limites_gasto.tokens_out", "limites_gasto.usd"}


def _en(dct: dict, ruta: str):
    actual = dct
    for parte in ruta.split("."):
        if not isinstance(actual, dict) or parte not in actual:
            return False, None
        actual = actual[parte]
    return True, actual


def validar_protocolo(protocolo: dict) -> dict:
    """Lector/validador de `protocolo.json` contra `PROTOCOLO_SCHEMA`, sus ocho umbrales y su nulidad.

    No decide nada sobre el piloto: verifica forma, coherencia entre umbrales y que los unicos null
    sean los declarados. Un `OK` aqui tampoco congela el protocolo: el congelado es FASE-C.
    """
    hallazgos: list[dict] = []

    def falla(guard: str, motivo: str) -> None:
        hallazgos.append({"guard": guard, "motivo": motivo})

    if protocolo.get("schema") != PROTOCOLO_SCHEMA:
        falla("schema", f"se leyo {protocolo.get('schema')!r}, se esperaba {PROTOCOLO_SCHEMA!r}")

    status = protocolo.get("status")
    if status not in ("BORRADOR", "CONGELADA"):
        falla("status", f"status {status!r} fuera de {{BORRADOR, CONGELADA}}")

    k = None
    for i, (ruta, tipo) in enumerate(PROTOCOLO_UMBRALES):
        if ruta == "reglas_recuperacion.k":
            texto = protocolo.get("reglas_recuperacion") or ""
            encontrado = re.search(r"top-(\d+)", texto)
            if not encontrado:
                falla("umbral-k", f"`reglas_recuperacion` no declara un top-k: {texto[:80]!r}")
                continue
            k = int(encontrado.group(1))
            continue
        presente, valor = _en(protocolo, ruta)
        if not presente:
            falla("umbral-ausente", f"{ruta} no esta en el protocolo")
            continue
        if valor is None:
            falla("umbral-null", f"{ruta} sigue null: bloquea FASE-C y no es un umbral")
        elif tipo == "entero" and (not isinstance(valor, int) or isinstance(valor, bool)):
            falla("umbral-forma", f"{ruta} no es entero: {valor!r}")
        elif tipo == "numero" and (not isinstance(valor, (int, float)) or isinstance(valor, bool)):
            falla("umbral-forma", f"{ruta} no es numero: {valor!r}")
        elif tipo == "fraccion" and (not isinstance(valor, (int, float)) or isinstance(valor, bool)
                                     or not (0 < valor <= 1)):
            falla("umbral-rango", f"{ruta} fuera de (0, 1]: {valor!r}")

    # Coherencia entre umbrales, que es lo que un numero suelto no puede decir.
    ok_timeout, timeout_s = _en(protocolo, "parametros.timeout_s")
    ok_lat, latencia = _en(protocolo, "criterios_adopcion.latencia_max")
    if ok_timeout and ok_lat and isinstance(timeout_s, (int, float)) \
            and isinstance(latencia, (int, float)) and latencia != timeout_s * 1000:
        falla("umbral-coherencia",
              f"latencia_max {latencia} no es timeout_s {timeout_s} en milisegundos")
    ok_retries, retries = _en(protocolo, "parametros.retry_policy.max_retries")
    if ok_retries and retries != 0:
        falla("umbral-reintentos",
              f"max_retries {retries!r}: el piloto autoriza 0, los demas gastan fuera del ledger")
    if k is not None and k < 1:
        falla("umbral-k", f"k={k} no define una capa fria")

    nulos = _nulos_de(protocolo)
    motivo = str((protocolo.get("limites_gasto") or {}).get("motivo") or "")
    for ruta in nulos:
        if ruta not in NULOS_ADMITIDOS:
            falla("nulo-no-admitido", f"{ruta} esta null y no esta entre los admitidos")
            continue
    for clave in ("tokens_in", "tokens_out"):
        presente, valor = _en(protocolo, f"limites_gasto.{clave}")
        if presente and valor is None and not motivo.strip():
            falla("nulo-sin-motivo", f"limites_gasto.{clave} es null y `motivo` esta vacio")
    presente, usd = _en(protocolo, "limites_gasto.usd")
    if presente and usd is None and "fuera de gobernanza" not in motivo:
        falla("usd-sin-declaracion",
              "limites_gasto.usd es null sin la declaracion «fuera de gobernanza» en `motivo`")

    rubrica = protocolo.get("rubrica") or {}
    if not rubrica.get("valores") or not rubrica.get("importancia"):
        falla("rubrica", "la rubrica o su escala de importancia vienen vacias")

    modelos = protocolo.get("modelos") or {}
    if not modelos.get("jev_pin"):
        falla("modelo-pedido", "el protocolo no fija el modelo solicitado de Jev")
    if not modelos.get("comparador"):
        falla("comparador", "el protocolo no fija el brazo comparador")
    if modelos.get("excluido") != "Anthropic":
        falla("excluido", f"el brazo excluido declarado es {modelos.get('excluido')!r}")

    revision = str((protocolo.get("criterios_adopcion") or {}).get("revision_humana") or "")
    if not revision.strip() or "a-decidir" in revision or "pendiente" in revision:
        falla("revision-humana", f"la revision humana no tiene designado con fecha: {revision[:80]!r}")

    return {"check_status": "OK" if not hallazgos else "FALLO",
            "protocolo_status": status, "k": k, "umbrales_gobernados": len(PROTOCOLO_UMBRALES),
            "nulos": nulos, "hallazgos": hallazgos}


def run(*, muestra: Path, protocolo: Path, indice: Path, preflight: Path, out_dir: Path,
        proveedor: str = None, k: int = 8, splits: str = "dev",
        autorizacion_de_null: dict = None, enviar=None, etiquetas: Path = None,
        hora=None) -> dict:
    """Corrida explicita por proveedor, con reserva de presupuesto ANTES de cada intento (AC8).

    `enviar` existe para que el transporte falso de AC9 pueda ejercitar toda la mecanica del runner
    sin red; en produccion es `decision_client.system_one_jev`. Nada de aqui elige proveedor solo.
    """
    import time as _time
    hora = hora or _time.monotonic
    out_dir = Path(out_dir)
    if proveedor not in (PROVEEDOR_JEV, "deepseek"):
        return {"status": "NEGADO", "motivos": [f"proveedor-no-autorizado:{proveedor!r}"],
                "envios": 0}
    if proveedor == "deepseek":
        # El comparador no es un camino de este runner: se despacha por la costura con
        # IAH_DECISION_PROVIDER, que es donde vive su contrato de proveedor. Dejarlo aqui duplicaria
        # la puerta, que el prompt de FASE-B prohibe expresamente.
        return {"status": "NEGADO", "envios": 0,
                "motivos": ["el brazo deepseek se despacha por la costura: el runner no lo instancia, "
                            "y esta tanda no autoriza llamadas DeepSeek"]}
    muestra_datos = _load_json(Path(muestra))
    if muestra_datos.get("status") != "CONGELADA":
        return {"status": "NEGADO", "motivos": ["muestra-no-congelada"], "envios": 0}
    protocolo_datos = _load_json(Path(protocolo))
    modelo_solicitado = (protocolo_datos.get("modelos") or {}).get("jev_pin")
    limites = limites_desde_protocolo(protocolo_datos, autorizacion_de_null=autorizacion_de_null)
    cuenta = _estado_cuenta(out_dir)
    pre = revisar_preflight(preflight, proveedor)
    if not pre["ok"]:
        return {"status": "NEGADO", "motivos": pre["motivos"], "envios": 0,
                "preflight": str(preflight)}
    reserva = reservar_presupuesto(cuenta, limites)
    if not reserva["reservado"]:
        return {"status": "NEGADO", "motivos": reserva["motivos"], "envios": 0,
                "preflight": "OK", "cuenta": cuenta}

    puerta = None
    resolucion_sdk = None
    credencial = None
    if enviar is None:
        # La construccion del cliente y el envio van juntos detras de la inyeccion: un test con
        # transporte falso tiene que poder ejercitar el guard, el ledger y la contabilidad sin
        # necesitar la credencial real que `TypeSafeClient` resuelve por entorno.
        # CR-3: la credencial se resuelve ANTES de abrir la puerta y solo por su nombre de entorno.
        # Con `enviar` inyectado este bloque no existe, o sea la via offline jamas toca `.env`.
        credencial = credencial_del_sdk(Path(__file__).resolve().parents[1])
        puerta = _puerta()
        cargado = puerta.cargar_sdk()
        resolucion_sdk = cargado["resolucion"]
        cliente = puerta.cliente_jev(cargado["modulo"], modelo=modelo_solicitado,
                                     timeout=limites["timeout_s"])
        enviar = lambda state, questions, modelo: puerta.system_one_jev(
            cliente, state=state, questions=questions, modelo=modelo)

    lecciones = _load_json(Path(indice)).get("lecciones") or []
    pares = [p for p in muestra_datos.get("pairs", [])
             if p.get("split") in ([s.strip() for s in str(splits).split(",")] or ["dev"])]
    rubrica = protocolo_datos.get("rubrica") or {}
    ledger_ruta = out_dir / "ledger.jsonl"
    ledger_ruta.parent.mkdir(parents=True, exist_ok=True)
    enviados = 0
    for par in pares:
        fria = recuperacion_fria(par["input_fragment"], lecciones, k)
        questions = preguntas_para_par(par["pair_id"], fria["candidatos"], rubrica)
        estado = nuevo_ledger(proveedor, modelo_solicitado)
        estado["pair_id"] = par["pair_id"]
        estado["split"] = par.get("split")
        estado["candidatos_frios"] = [c["id"] for c in fria["candidatos"]]
        estado["leccion_target_en_candidatos"] = par["lesson_id"] in estado["candidatos_frios"]
        reserva = reservar_presupuesto(cuenta, limites)
        if not reserva["reservado"]:
            estado["estado"] = "NO-EJERCITADO"
            estado["motivos"] = reserva["motivos"]
            with ledger_ruta.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(estado, ensure_ascii=False) + "\n")
            continue
        inicio = hora()
        try:
            payload = enviar({"consulta": par["input_fragment"], "candidatos": fria["candidatos"]},
                             questions, modelo_solicitado)
        except Exception as exc:
            registrar_intento(estado, resultado="fallo", excepcion=exc,
                              duracion_ms=round((hora() - inicio) * 1000.0, 3))
        else:
            registrar_intento(estado, resultado="exito",
                              usage=payload.get("usage"),
                              modelo_efectivo=payload.get("modelo"),
                              duracion_ms=round((hora() - inicio) * 1000.0, 3))
            estado["answers"] = payload.get("answers")
            estado["request_id"] = payload.get("request_id")
        # `attempts` es lo que el SDK hizo, no lo que el runner pidio: con max_retries=0 debe ser 1.
        # B2-1d: la suma y la publicacion van juntas por `registrar_envio_en_cuenta`, la misma funcion
        # que le toca usar a un brazo despachado fuera de `run`.
        cuenta = registrar_envio_en_cuenta(out_dir, cuenta, estado)
        enviados += 1
        with ledger_ruta.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(estado, ensure_ascii=False) + "\n")
    _persistir(out_dir, "consumo.json", cuenta)
    fila_ledger = [json.loads(l) for l in ledger_ruta.read_text(encoding="utf-8").splitlines() if l]
    recuperacion = None
    if etiquetas and Path(etiquetas).exists():
        recuperacion = recuperacion_medida(muestra_datos, _load_json(Path(etiquetas)), fila_ledger)
    resultado = {"status": "OK" if enviados else "SIN-ENVIO", "envios": enviados,
                 "cuenta": cuenta, "preflight": "OK",
                 "ledger": ledger_ruta.as_posix(), "pares": len(pares), "split": splits,
                 "modelo_solicitado": modelo_solicitado, "k": k,
                 "resolucion_sdk": resolucion_sdk, "credencial": credencial,
                 "recuperacion": recuperacion,
                 "modelos_efectivos": sorted({f.get("modelo_efectivo") for f in fila_ledger
                                              if f.get("modelo_efectivo")})}
    _persistir(out_dir, "run_resumen.json", resultado)
    return resultado


def recuperacion_medida(muestra: dict, etiquetas: dict, filas_ledger: list) -> dict:
    """Metrica 1 del maestro: pertinentes importantes presentes entre candidatos / elegibles.

    El denominador es humano y del conjunto elegible, no de lo que la capa fria quiso: si vale cero
    el cociente es NO-EVALUABLE (`score` lo publica con su motivo), nunca 100 % ni 0 %.

    Y hay un segundo cero que tampoco puede leerse como medida: un elegible **sin fila en el ledger**
    no es un fallo de recuperacion, es un no-medido (pasa cuando el elegible vive en un split que esta
    corrida no despacho). Esos se publican aparte en `sin_medir` y salen del numerador y del
    denominador; si no queda ningun elegible con fila, el cociente es NO-EVALUABLE con su motivo, no
    un 0.0 que acusaria a la capa fria de algo que nunca consulto.
    """
    por_par = {f.get("pair_id"): f for f in filas_ledger if f.get("pair_id")}
    importantes = [p for p in muestra.get("pairs", [])
                   if any(l["pair_id"] == p["pair_id"] and l.get("label") == "pertinente"
                          and l.get("importance") in ("alta", "media")
                          for l in etiquetas.get("labels", []))]
    medidos = [p for p in importantes if p["pair_id"] in por_par]
    sin_medir = [p["pair_id"] for p in importantes if p["pair_id"] not in por_par]
    presentes = [p for p in medidos if por_par[p["pair_id"]].get("leccion_target_en_candidatos")]
    cociente = score(len(presentes), len(medidos))
    if sin_medir:
        cociente["motivo"] = (cociente["motivo"] + "; " if cociente["motivo"] else "") + \
            f"{len(sin_medir)} elegible(s) sin fila en el ledger: no medidos, no fallados"
    cociente["presentes"] = [p["pair_id"] for p in presentes]
    cociente["elegibles"] = [p["pair_id"] for p in importantes]
    cociente["medidos"] = [p["pair_id"] for p in medidos]
    cociente["sin_medir"] = sin_medir
    return cociente


# --- FASE-B.2 (2026-10-04): CR-1 y CR-2, los modos que faltaban del contrato del runner -------
# El maestro fija cuatro cocientes (01-plan-maestro.md:88-91) y exige que cada uno publique su
# numerador y su denominador (93). `metrics()` envuelve la forma de FASE-A, pero comparte un solo
# `den` para precision y recall (`:191-192`), o sea NO puede expresar los cuatro denominadores
# separados que pide AC10. Por eso `report` produce cada cociente con `score()` --el emisor de
# cocientes probado en FASE-A-- sobre sus propios conteos, y `metrics()` queda intacto y sin usar:
# re-implementarlo tampoco estaba en el mandato.
#
# Ningun numero de aqui nace de una lectura nueva del protocolo: los umbrales se LEEN del
# `criterios_adopcion` congelado y se aplican, y un cociente sin insumo sale NO-EVALUABLE con su
# motivo (AC10) en vez de un 0 o un 100.

INFORME_SCHEMA = "jev-pilot-informe-comparativa/v1"
DECISION_SCHEMA = "jev-pilot-decision/v1"
COCIENTES_INFORME = ("recuperacion", "precision_entre_propuestas",
                     "recall_importante_candidatos", "extremo_a_extremo")
# `run_status` usa los cuatro literales del maestro (:101). Donde la fila trae un error, el literal
# depende de QUE clase de error es: autenticacion, esquema, peticion o un fallo no clasificable son
# impedimento operativo del camino (FALLIDO); conexion, timeout, cuota o servidor son
# indisponibilidad, que segun AC12 detiene o aplaza pero NO elimina el brazo (INCOMPLETO).
ERRORES_DE_IMPEDIMENTO = {"auth", "respuesta_ilegible", "peticion", "desconocido"}
ERRORES_DE_INDISPONIBILIDAD = {"conexion", "timeout", "cuota", "servidor"}


def leer_respuestas(ruta: Path) -> list:
    """`respuestas.jsonl` tal como quedo en disco: una fila por (par, brazo), sin re-etiquetar."""
    filas = []
    for linea in Path(ruta).read_text(encoding="utf-8").splitlines():
        if linea.strip():
            filas.append(json.loads(linea))
    return filas


def estado_de_propuesta(fila) -> str:
    """Como leida la fila del brazo, no cuantas clases de no-eleccion hay.

    `sin_fila` y `sin_eleccion_por_fallo` se separan a proposito: la primera es un par que este
    despacho nunca consulto (no medido), la segunda es un envio que salio y volvio vacio (fallo del
    camino, que si cuenta contra el extremo a extremo). Colapsarlas es la forma facil de mejorar el
    score excluyendo fallos, y el maestro lo prohibe en :93.
    """
    if fila is None:
        return "sin_fila"
    propuesta = fila.get("propuesta")
    if propuesta is None:
        return "sin_eleccion_por_fallo" if fila.get("error_kind") else "sin_eleccion"
    if isinstance(propuesta, list):
        return "ranking"
    if propuesta == ETIQUETA_DE_NINGUNA:
        return "abstencion"
    return "eleccion"


def poblacion_de_comparacion(muestra: dict, etiquetas: dict) -> dict:
    """El conjunto humano elegible: pertinentes de importancia alta o media, con su target."""
    importantes = []
    for par in muestra.get("pairs", []):
        for l in etiquetas.get("labels", []):
            if (l["pair_id"] == par["pair_id"] and l.get("label") == "pertinente"
                    and l.get("importance") in ("alta", "media")):
                importantes.append({"pair_id": par["pair_id"], "lesson_id": par["lesson_id"],
                                    "importancia": l.get("importance")})
    pertinentes = sum(1 for l in etiquetas.get("labels", []) if l.get("label") == "pertinente")
    return {"importantes": importantes,
            "por_par": {p["pair_id"]: p for p in importantes},
            "pertinentes": pertinentes,
            "total_pares": (muestra.get("counts") or {}).get("total")}


def es_acierto(par: dict) -> bool:
    """El brazo acerto en ese par, con la MISMA regla en recall y en extremo a extremo.

    Para un brazo que elige, acertar es proponer el target. Para la capa fria, cuya propuesta es el
    conjunto de candidatos, acertar es que el target este dentro: la convencion tiene que ser una
    sola, o el mismo brazo diria 1/2 en un cociente y 0/1 en el otro sobre la misma fila.
    """
    if par["estado_propuesta"] == "eleccion":
        return par["propuesta"] == par["target"]
    if par["estado_propuesta"] == "ranking":
        return bool(par["target_en_candidatos"])
    return False


def conteos_por_brazo(filas_brazo: list, poblacion: dict) -> dict:
    """CR-1: el contador de clasificacion y del extremo a extremo, desde filas persistidas.

    Cuatro denominadores distintos sobre la misma poblacion, cada uno con su regla:
      * precision  -> entre las elecciones que el brazo DE VERDAD hizo (una abstencion o un fallo
        no son una propuesta, son su denominador aparte).
      * recall     -> entre los pares importantes cuyo target SI estaba entre los candidatos,
        porque fuera de ese conjunto acertar no era una opcion del clasificador.
      * e2e        -> sobre todo el conjunto importante elegible, incluyendo las omisiones de
        recuperacion (maestro :90) y los envios que volvieron con fallo (:93).
      * recuperacion -> la que ya produce `recuperacion_medida`, no se recalcula aqui.
    """
    por_par = {f.get("pair_id"): f for f in filas_brazo if f.get("pair_id")}
    importantes = [p["pair_id"] for p in poblacion["importantes"]]
    sin_fila = [pid for pid in importantes if pid not in por_par]
    # Una fila cuyo par no esta en el conjunto elegible NO se descarta en silencio: se cuenta y se
    # publica. Perderla sin decirlo es la forma barata de que el denominador parezca mas chico.
    fuera = [f.get("pair_id") for f in filas_brazo if f.get("pair_id") not in set(importantes)]
    detalle = []
    for pid in importantes:
        fila = por_par.get(pid)
        par = poblacion["por_par"][pid]
        estado = estado_de_propuesta(fila)
        recuperable = bool(fila.get("leccion_target_en_candidatos")) if fila else False
        detalle.append({
            "pair_id": pid, "estado_propuesta": estado,
            "propuesta": fila.get("propuesta") if fila else None,
            "target": par["lesson_id"],
            "target_en_candidatos": recuperable if fila else None,
            "error_kind": fila.get("error_kind") if fila else None,
            "acierto": es_acierto({"estado_propuesta": estado,
                                   "propuesta": fila.get("propuesta") if fila else None,
                                   "target": par["lesson_id"], "target_en_candidatos": recuperable}),
        })
    recuperables = [d for d in detalle if d["estado_propuesta"] != "sin_fila"
                    and d["target_en_candidatos"]]
    enviadas = [d for d in detalle if d["estado_propuesta"] != "sin_fila"]
    propuestas = [d for d in detalle if d["estado_propuesta"] == "eleccion"]
    return {
        "detalle": detalle,
        "sin_fila": sin_fila,
        "fuera_del_conjunto": fuera,
        "poblacion": len(importantes),
        "prec_num": sum(1 for d in propuestas if d["acierto"]),
        "den_propuestas": len(propuestas),
        "rec_num": sum(1 for d in recuperables if d["acierto"]),
        "den_recuperables": len(recuperables),
        "e2e_num": sum(1 for d in enviadas if d["acierto"]),
        "den_elegible": len(enviadas),
        "abstenciones": sum(1 for d in detalle if d["estado_propuesta"] == "abstencion"),
        "fallos": sum(1 for d in detalle if d["estado_propuesta"] == "sin_eleccion_por_fallo"),
        "sin_eleccion": sum(1 for d in detalle if d["estado_propuesta"] == "sin_eleccion"),
        "rankings": sum(1 for d in detalle if d["estado_propuesta"] == "ranking"),
    }


def cocientes_por_brazo(conteos: dict) -> dict:
    """Los cuatro cocientes, cada uno con el denominador que le corresponde por definicion."""
    detalle = conteos["detalle"]
    eleccion_de_recuperable = [d for d in detalle if d["estado_propuesta"] == "eleccion"
                               and d["target_en_candidatos"]]
    return {
        "recuperacion": None,  # la pone `recuperacion_medida`, no se recalcula aqui
        "precision_entre_propuestas": score(conteos["prec_num"], conteos["den_propuestas"]),
        "recall_importante_candidatos": score(conteos["rec_num"], conteos["den_recuperables"]),
        "extremo_a_extremo": score(conteos["e2e_num"], conteos["den_elegible"]),
        "lectura": {
            "capa_fria_es_un_ranking": all(d["estado_propuesta"] in ("ranking", "sin_fila")
                                           for d in detalle),
            "elecciones_sobre_recuperables": len(eleccion_de_recuperable),
            "poblacion_elegible": conteos["poblacion"],
        },
    }


def conteo_de_abstenciones(conteos: dict) -> dict:
    """Las abstenciones en denominador propio, como fija el criterio congelado.

    El conteo crudo es un hecho del registro; el cociente que se saca de el es abstenciones entre las
    decisiones efectivamente tomadas (eleccion + abstencion), y con denominador cero es NO-EVALUABLE.
    """
    tomadas = conteos["den_propuestas"] + conteos["abstenciones"]
    return {"con_eleccion": conteos["den_propuestas"], "abstenciones": conteos["abstenciones"],
            "sin_eleccion_por_fallo": conteos["fallos"], "sin_fila": len(conteos["sin_fila"]),
            "cociente_de_abstencion": score(conteos["abstenciones"], tomadas)}


def latencias_por_brazo(filas_brazo: list) -> dict:
    """Latencia solo de los intentos que respondieron: la duracion de un fallo no es una latencia."""
    de_exito, de_fallo = [], []
    for fila in filas_brazo:
        for intento in fila.get("intentos") or []:
            duracion = intento.get("duracion_ms")
            if duracion is None:
                continue
            (de_fallo if intento.get("resultado") != "exito" else de_exito).append(duracion)
    return {"latencias_ms_de_respuesta": de_exito, "duracion_ms_de_fallos": de_fallo,
            "max_latencia_ms": max(de_exito) if de_exito else None,
            "nota": "la duracion de un intento que fallo por el camino no se cuenta como latencia "
                    "de respuesta; se publica aparte con esa etiqueta"}


ESTADOS_USAGE_OBSERVADOS = ("observado", "parcial")
CAMPOS_DE_USAGE = (("input", "input_tokens", "tokens_in"),
                   ("output", "output_tokens", "tokens_out"))


def _entero_o_none(valor):
    return valor if isinstance(valor, int) and not isinstance(valor, bool) else None


def _numero_o_none(valor):
    return valor if (isinstance(valor, (int, float)) and not isinstance(valor, bool)) else None


def columna_de_tokens(filas_brazo: list, campo: str) -> dict:
    """Una columna de tokens observados, por campo, sin convertir la ausencia en cero.

    `n_observaciones` es el denominador de la columna: una fila con `estado` sin_usage o desconocido
    hizo un envio y no dejo medida, asi que se cuenta aparte y no se suma como cero.
    """
    valores, observadas, sin_medida = [], 0, {}
    for fila in filas_brazo:
        uso = fila.get("usage_normalized") or {}
        entero = _entero_o_none(uso.get(campo))
        estado = str(uso.get("estado") or "sin_estado")
        if estado not in ESTADOS_USAGE_OBSERVADOS:
            sin_medida[estado] = sin_medida.get(estado, 0) + 1
            continue
        observadas += 1
        if entero is not None:
            valores.append({"pair_id": fila.get("pair_id"), "valor": entero})
    return {"suma": sum(v["valor"] for v in valores) if valores else None,
            "maximo_por_llamada": max((v["valor"] for v in valores), default=None),
            "n_observaciones": len(valores), "n_filas_con_envio": observadas,
            "filas_sin_medida_por_estado": dict(sorted(sin_medida.items())),
            "valores_por_fila": valores}


def contabilidad_de_coste(filas_brazo: list, protocolo: dict) -> dict:
    """AC4 en tres columnas separadas y el veredicto de exceso contra los techos (deuda B2-1/B2-1c).

    Tokens observados, coste calculado y cargo facturado son preguntas distintas: ninguna se deriva
    de las otras y ninguna se rellena con un cero favorable. Medido el 2026-10-09,
    `config/provider_registry.yaml` no registra tarifa para `jev-1.13.0` ni para el brazo DeepSeek,
    asi que `cost_calculated` sale NO-EVALUABLE con la tarifa nombrada en vez de un dolar inventado;
    el dia que el protocolo congele `precios_por_mtok` la misma funcion lo calcula.
    """
    gastos = protocolo.get("limites_gasto") or {}
    precios = gastos.get("precios_por_mtok") or {}
    columnas = {alias: columna_de_tokens(filas_brazo, campo)
                for alias, campo, _techo in CAMPOS_DE_USAGE}

    techo_de = {"input": gastos.get("tokens_in"), "output": gastos.get("tokens_out")}
    contra_techos, excedidos, no_evaluables = {}, [], []
    for alias, _campo, nombre_techo in CAMPOS_DE_USAGE:
        techo = _entero_o_none(techo_de.get(alias))
        maximo = columnas[alias]["maximo_por_llamada"]
        fuera = [v for v in columnas[alias]["valores_por_fila"]
                 if techo is not None and v["valor"] > techo]
        if techo is None:
            veredicto, motivo = "NO-EVALUABLE", (f"`limites_gasto.{nombre_techo}` es null en el "
                                                 "protocolo: no hay techo que rebasar")
            no_evaluables.append(alias)
        elif maximo is None:
            veredicto, motivo = "NO-EVALUABLE", ("ningun envio dejo medida de este campo: la "
                                                 "comparacion no se puede hacer con ceros")
            no_evaluables.append(alias)
        else:
            veredicto, motivo = ("EXCESO" if fuera else "DENTRO"), ""
            if fuera:
                excedidos.append({"campo": alias, "techo": techo,
                                  "filas": [f"{v['pair_id']}={v['valor']}" for v in fuera]})
        contra_techos[alias] = {
            "techo_congelado": techo, "clave_del_techo": nombre_techo,
            "medido_maximo_por_llamada": maximo,
            "exceso_sobre_el_techo": ((maximo - techo) if fuera else None),
            "margen_restante_bajo_el_techo": ((techo - maximo) if (techo is not None and maximo
                                                                    is not None and not fuera)
                                              else None),
            "filas_fuera_del_techo": [v["pair_id"] for v in fuera],
            "veredicto": veredicto, "motivo": motivo,
        }
    if excedidos:
        veredicto_global = "EXCESO"
    elif no_evaluables:
        veredicto_global = "NO-EVALUABLE"
    else:
        veredicto_global = "DENTRO"

    precio_in = _numero_o_none(precios.get("input"))
    precio_out = _numero_o_none(precios.get("output"))
    if precio_in is None or precio_out is None:
        cost_calculated = {
            "usd": None, "estado": "NO-EVALUABLE",
            "tarifa_por_mtok": {"input": precio_in, "output": precio_out},
            "motivo": ("el protocolo congelado no declara `limites_gasto.precios_por_mtok` y "
                       "config/provider_registry.yaml no tiene entrada para estos dos modelos "
                       "(medido 2026-10-09): sin tarifa no hay coste calculable, y un cero no es "
                       "un calculo")}
    elif not columnas["input"]["n_observaciones"] and not columnas["output"]["n_observaciones"]:
        cost_calculated = {
            "usd": None, "estado": "NO-EVALUABLE",
            "tarifa_por_mtok": {"input": precio_in, "output": precio_out},
            "motivo": ("hay tarifa pero ningun envio dejo tokens observados: calcular sobre una suma "
                       "vacia daria un cero que no es un coste")}
    else:
        cost_calculated = {
            "usd": round((columnas["input"]["suma"] or 0) / 1e6 * precio_in
                         + (columnas["output"]["suma"] or 0) / 1e6 * precio_out, 8),
            "estado": "CALCULADO",
            "tarifa_por_mtok": {"input": precio_in, "output": precio_out},
            "base": {"suma_input": columnas["input"]["suma"],
                     "suma_output": columnas["output"]["suma"]},
            "motivo": ("calculado sobre las sumas observadas; las filas sin medida no entran en la "
                       "suma y se ven en `tokens.*.filas_sin_medida_por_estado`")}
    cobrados = [f.get("cargo_facturado") for f in filas_brazo
                if _numero_o_none(f.get("cargo_facturado")) is not None]
    cost_billed = {
        "usd": (round(sum(cobrados), 6) if cobrados else None),
        "estado": "OBSERVADO" if cobrados else "NO-OBSERVADO",
        "n_filas_con_cargo": len(cobrados),
        "motivo": ("" if cobrados else "ningun registro persistido trae `cargo_facturado`: el cargo "
                                      "lo dice el proveedor, no el ledger del piloto, y sin "
                                      "observacion la columna se declara no observada en vez de 0"),
    }
    return {"unidad_de_comparacion": ("maximo observado por llamada contra el techo congelado, que es "
                                      "la unidad con la que se escribieron los techos (ver "
                                      "`limites_gasto.motivo` del protocolo)"),
            "filas": len(filas_brazo),
            "tokens": {alias: columnas[alias] for alias, _c, _t in CAMPOS_DE_USAGE},
            "contra_techos": contra_techos, "veredicto_exceso": veredicto_global,
            "cost_calculated": cost_calculated, "cost_billed": cost_billed}


def fallos_de_contabilidad(filas: list, protocolo: dict) -> list:
    """FALLIDO por contabilidad: filas que contradicen el presupuesto congelado del protocolo.

    Con `max_retries=0` congelado, un envio con `attempts` distinto de 1 hizo intentos que no estan
    en el ledger (AC8). Es un fallo de datos del experimento, no del modelo, y por eso manda
    `run_status=FALLIDO` con `decision=null` en vez de colarse como un brazo que perdio.
    """
    retry = ((protocolo.get("parametros") or {}).get("retry_policy") or {}).get("max_retries")
    motivos = []
    for fila in filas:
        attempts = fila.get("attempts")
        if fila.get("error_kind") == "auth":
            motivos.append(f"auth:{fila.get('pair_id')}:{fila.get('brazo')}")
        if retry == 0 and isinstance(attempts, int) and attempts > 1:
            motivos.append(f"intentos-fuera-de-ledger:{fila.get('pair_id')}"
                           f":{fila.get('brazo')}={attempts}")
    return motivos


def senales_mecanicas(informe: dict) -> list:
    """Hechos numericos que el informe puede decir sin interpretar el protocolo."""
    senales = []
    por_brazo = informe["por_brazo"]
    brazos = list(por_brazo)
    rec = {b: por_brazo[b]["recuperacion"].get("value") for b in brazos}
    valores = {v for v in rec.values() if v is not None}
    if len(brazos) > 1 and len(valores) == 1:
        senales.append({"id": "S1", "senal": "la recuperacion es el mismo numero en todos los brazos",
                        "base": {"valor": rec},
                        "consecuencia": "la metrica de recuperacion mide la capa fria, que es comun: "
                                        "por si sola no decide entre brazos"})
    for b in brazos:
        fila = por_brazo[b]
        if fila["precision_entre_propuestas"]["motivo"] == "denominador_cero":
            senales.append({"id": "S2", "senal": f"{b}: precision sin propuestas que contar",
                            "base": {"den_propuestas": 0},
                            "consecuencia": "NO-EVALUABLE, no 0.0: el brazo no hizo ninguna eleccion "
                                            "contable en esta corrida"})
    margen = informe.get("criterios", {}).get("margen_vs_deepseek", {})
    if margen.get("denominador_eval"):
        senales.append({"id": "S3", "senal": "resolucion del extremo a extremo sobre el conjunto "
                                             "elegible medido",
                        "base": {"denominador": margen["denominador_eval"],
                                 "paso_de_la_resolucion": margen["paso_de_resolucion"]},
                        "consecuencia": "un margen congelado mas fino que el paso del cociente no "
                                        "discrimina en este denominador; se publica, no se re-lee"})
    for b in brazos:
        if por_brazo[b]["contabilidad"]["fallos_operativos"]:
            senales.append({"id": "S4", "senal": f"{b}: envios que volvieron con fallo del camino",
                            "base": por_brazo[b]["contabilidad"]["fallos_operativos"],
                            "consecuencia": "AC12: la indisponibilidad detiene o aplaza y no elimina "
                                            "el brazo; la comparacion queda incompleta y declarada"})
    for b in brazos:
        if por_brazo[b]["lectura"]["capa_fria_es_un_ranking"] and \
                por_brazo[b]["recall_importante_candidatos"]["value"] is not None:
            senales.append({"id": "S5", "senal": f"{b}: es un ranking, no un clasificador",
                            "base": {"recall": por_brazo[b]["recall_importante_candidatos"]["value"],
                                     "recuperacion": por_brazo[b]["recuperacion"]["value"]},
                            "consecuencia": "su propuesta es el conjunto de candidatos, asi que el "
                                            "recall dentro de candidatos vale 1.0 por construccion y "
                                            "no es una comparacion de calidad entre brazos"})
    for b in brazos:
        coste = por_brazo[b]["contabilidad"].get("coste") or {}
        if coste.get("veredicto_exceso") == "EXCESO":
            senales.append({"id": "S6", "senal": f"{b}: un techo de tokens congelado se rebaso",
                            "base": {"excedido_por": [
                                {"campo": c, "techo": coste["contra_techos"][c]["techo_congelado"],
                                 "medido": coste["contra_techos"][c]["medido_maximo_por_llamada"],
                                 "exceso": coste["contra_techos"][c]["exceso_sobre_el_techo"],
                                 "filas": coste["contra_techos"][c]["filas_fuera_del_techo"]}
                                for c, v in sorted(coste["contra_techos"].items())
                                if v["veredicto"] == "EXCESO"]},
                            "consecuencia": "AC4 y AC8: el techo se paso y la corrida no lo publicaba; "
                                            "se publica aqui y la decision de detener o seguir es del "
                                            "operador, no del informe"})
    return senales


def report(*, respuestas: Path, etiquetas: Path, muestra: Path, protocolo: Path,
           fecha: str = None) -> dict:
    """CR-2: la comparacion reproducida desde registros persistidos, sin red y sin clientes.

    Cero llamadas, cero credenciales: solo lee `respuestas.jsonl` + `etiquetas.json` +
    `muestra.json` + `protocolo.json`. Dos corridas con los mismos insumos dan los mismos bytes
    salvo `fecha`, que es lo que hace al artefacto regenerable (AC4).
    """
    from datetime import date
    muestra_datos = _load_json(Path(muestra))
    etiquetas_datos = _load_json(Path(etiquetas))
    protocolo_datos = _load_json(Path(protocolo))
    filas = leer_respuestas(Path(respuestas))
    poblacion = poblacion_de_comparacion(muestra_datos, etiquetas_datos)
    k = validar_protocolo(protocolo_datos)["k"]
    brazos: list[str] = []
    for fila in filas:
        if fila.get("brazo") and fila["brazo"] not in brazos:
            brazos.append(fila["brazo"])

    por_brazo = {}
    for brazo in brazos:
        filas_brazo = [f for f in filas if f.get("brazo") == brazo]
        conteos = conteos_por_brazo(filas_brazo, poblacion)
        cocientes = cocientes_por_brazo(conteos)
        cocientes["recuperacion"] = recuperacion_medida(muestra_datos, etiquetas_datos, filas_brazo)
        por_brazo[brazo] = {
            **cocientes,
            "abstenciones": conteo_de_abstenciones(conteos),
            "latencia": latencias_por_brazo(filas_brazo),
            "contabilidad": {
                "filas": len(filas_brazo),
                "fuera_del_conjunto_elegible": conteos["fuera_del_conjunto"],
                "fallos_operativos": [
                    {"pair_id": f.get("pair_id"), "error_kind": f.get("error_kind"),
                     "attempts": f.get("attempts")}
                    for f in filas_brazo if f.get("error_kind")],
                "modelos_pedidos": sorted({f.get("modelo_pedido") for f in filas_brazo
                                           if f.get("modelo_pedido")}),
                "modelos_efectivos": sorted({f.get("modelo_efectivo") for f in filas_brazo
                                             if f.get("modelo_efectivo")}),
                "usage_por_fila": [f.get("usage_normalized") for f in filas_brazo],
                "coste": contabilidad_de_coste(filas_brazo, protocolo_datos),
                "request_ids": sorted({f.get("request_id") for f in filas_brazo
                                       if f.get("request_id")}),
                "fallos_de_contabilidad": fallos_de_contabilidad(filas_brazo, protocolo_datos),
            },
            "por_par": conteos["detalle"],
        }

    criterios = evaluar_criterios(por_brazo, poblacion, protocolo_datos, brazos)
    informe = {
        "schema": INFORME_SCHEMA,
        "plan": "EVALUACION-JEV-TYPESAFE-2026-09-21",
        "generado_sin_red": True,
        "instrumento": "scripts/evaluate_jev_pilot.py report",
        "fecha": fecha or date.today().isoformat(),
        "insumos": {"respuestas": Path(respuestas).as_posix(), "etiquetas": Path(etiquetas).as_posix(),
                    "muestra": Path(muestra).as_posix(), "protocolo": Path(protocolo).as_posix()},
        "sha256_de_los_insumos": {nombre: sha256_text(Path(ruta).read_text(encoding="utf-8"))
                                  for nombre, ruta in (("respuestas", respuestas), ("etiquetas", etiquetas),
                                                       ("muestra", muestra), ("protocolo", protocolo))},
        "protocolo": {"status": protocolo_datos.get("status"),
                      "congelado": protocolo_datos.get("congelado"), "k": k,
                      "criterios_adopcion": protocolo_datos.get("criterios_adopcion")},
        "conjunto_elegible": {
            "denominador_pares_total": poblacion["total_pares"],
            "pertinentes": poblacion["pertinentes"],
            "importantes_elegibles": [p["pair_id"] for p in poblacion["importantes"]],
            "brazos_en_registros": brazos,
        },
        "por_brazo": por_brazo,
        "criterios": criterios,
        "senales_mecanicas": [],
        "excluido_en_registros": sorted({f["brazo"] for f in filas
                                         if f.get("brazo")
                                         and str(f["brazo"]).lower()
                                         in str((protocolo_datos.get("modelos") or {})
                                                .get("excluido") or "").lower()}),
    }
    informe["senales_mecanicas"] = senales_mecanicas(informe)
    return informe


BRAZO_SUJETO = "jev"
BRAZO_COMPARADOR = "deepseek"


def evaluar_criterios(por_brazo: dict, poblacion: dict, protocolo: dict, brazos: list) -> dict:
    """Los cuatro criterios congelados, aplicados sin releerlos.

    Cada criterio publica umbral, medido, estado y motivo. `NO-EVALUABLE` es un estado, no un cero:
    es la unica forma de que `decide` sepa que NO le toca elegir (maestro :101, AC5).
    """
    criterios = protocolo.get("criterios_adopcion") or {}
    out: dict = {}

    umbral_cob = criterios.get("cobertura_min")
    medido_cob = {b: por_brazo[b]["recuperacion"].get("value") for b in brazos}
    valor_sujeto = medido_cob.get(BRAZO_SUJETO)
    out["cobertura_min"] = {
        "umbral": umbral_cob, "medido_por_brazo": medido_cob, "brazo_sujeto": BRAZO_SUJETO,
        "estado": ("NO-EVALUABLE" if valor_sujeto is None or umbral_cob is None
                   else "CUMPLE" if valor_sujeto >= umbral_cob else "NO CUMPLE"),
        "motivo": ("el brazo sujeto no tiene recuperacion medida" if valor_sujeto is None else ""),
    }

    suff = score(poblacion["pertinentes"], poblacion["total_pares"] or 0)
    umbral_suff = criterios.get("suficiencia_minima")
    out["suficiencia_minima"] = {
        "umbral": umbral_suff, "medido": suff,
        "lectura_congelada": f"{poblacion['pertinentes']} de {poblacion['total_pares']} "
                             "pares pertinentes",
        "estado": ("NO-EVALUABLE" if suff["value"] is None or umbral_suff is None
                   else "CUMPLE" if suff["value"] >= umbral_suff else "NO CUMPLE"),
    }

    umbral_margen = criterios.get("margen_vs_deepseek")
    e2e_sujeto = (por_brazo.get(BRAZO_SUJETO) or {}).get("extremo_a_extremo") or {}
    e2e_comparador = (por_brazo.get(BRAZO_COMPARADOR) or {}).get("extremo_a_extremo") or {}
    # Denominador efectivo: los pares donde LOS DOS brazos dejaron una eleccion utilizable. Es lo que
    # realmente compara el margen, y puede ser menor que el denominador del cociente (registro de C,
    # H6: con un par no hay diferencia que discriminar).
    eligibles_sujeto = {d["pair_id"] for d in (por_brazo.get(BRAZO_SUJETO) or {}).get("por_par", [])
                        if d["estado_propuesta"] == "eleccion"}
    eligibles_comparador = {d["pair_id"] for d in
                            (por_brazo.get(BRAZO_COMPARADOR) or {}).get("por_par", [])
                            if d["estado_propuesta"] == "eleccion"}
    denominador_efectivo = len(eligibles_sujeto & eligibles_comparador)
    margen = {
        "umbral": umbral_margen,
        "definicion_congelada": "diferencia absoluta del cociente extremo_a_extremo entre Jev y "
                                "DeepSeek",
        "medido_jev": e2e_sujeto.get("value"), "medido_deepseek": e2e_comparador.get("value"),
        "diferencia_calculada": None, "denominador_eval": None, "paso_de_resolucion": None,
        "denominador_efectivo_de_la_comparacion": denominador_efectivo,
        "estado": "NO-EVALUABLE", "motivo": "",
    }
    if e2e_sujeto.get("value") is None or e2e_comparador.get("value") is None:
        margen["motivo"] = ("alguna de las dos magnitudes extremo_a_extremo no esta medida: "
                            f"jev={e2e_sujeto.get('value')!r}, "
                            f"deepseek={e2e_comparador.get('value')!r}")
    else:
        diferencia = round(abs(e2e_sujeto["value"] - e2e_comparador["value"]), 4)
        margen["diferencia_calculada"] = diferencia
        denominador = e2e_sujeto.get("denominator")
        margen["denominador_eval"] = denominador
        margen["paso_de_resolucion"] = (round(1 / denominador, 4) if denominador else None)
        if umbral_margen is None:
            margen["motivo"] = "el margen congelado es null, no hay criterio que aplicar"
        else:
            fallos = (por_brazo[BRAZO_SUJETO]["contabilidad"]["fallos_operativos"]
                      + por_brazo[BRAZO_COMPARADOR]["contabilidad"]["fallos_operativos"])
            if fallos:
                margen["motivo"] = ("la diferencia esta calculada pero no gobierna: al menos un brazo "
                                    "perdio un par por un fallo del camino, y AC12 no permite medirle "
                                    "al modelo una indisponibilidad de la infraestructura")
                margen["estado"] = "NO-EVALUABLE"
            else:
                margen["estado"] = ("CUMPLE" if diferencia >= umbral_margen else "NO CUMPLE")
    out["margen_vs_deepseek"] = margen

    umbral_lat = criterios.get("latencia_max")
    latencias = {b: por_brazo[b]["latencia"]["max_latencia_ms"] for b in brazos
                 if por_brazo[b]["latencia"]["max_latencia_ms"] is not None}
    worst = max(latencias.values()) if latencias else None
    out["latencia_max"] = {
        "umbral_ms": umbral_lat, "medido_ms_por_brazo": latencias,
        "estado": ("NO-EVALUABLE" if worst is None or umbral_lat is None
                   else "CUMPLE" if worst <= umbral_lat else "NO CUMPLE"),
        "motivo": ("" if latencias else "ningun intento dejo una duracion de respuesta"),
        "nota": "solo intentos con resultado exito; la duracion de un fallo se publica en "
                "`latencia.duracion_ms_de_fallos`",
    }

    gastos = protocolo.get("limites_gasto") or {}
    out["coste_en_gobernanza"] = {
        "usd": gastos.get("usd"),
        "en_gobernanza": gastos.get("usd") is not None,
        "motivo": ("`usd` sigue null en el protocolo congelado, fuera de gobernanza por decision del "
                   "operador: no hay decision de coste sin coste en gobernanza"
                   if gastos.get("usd") is None else ""),
    }
    return out


def estado_del_run(informe: dict, protocolo: dict) -> dict:
    """`run_status` con los cuatro literales del maestro (:101), como aserciones y no como prosa.

    El orden importa: la contabilidad rota se declara primero porque invalida el experimento entero,
    y un brazo con indisponibilidad NO se elimina --se marca incompleto-- (AC12).
    """
    filas_total = sum(b["contabilidad"]["filas"] for b in informe["por_brazo"].values())
    impedimentos, indisponibilidades = [], []
    for brazo, datos in informe["por_brazo"].items():
        for fallo in datos["contabilidad"]["fallos_operativos"]:
            clase = fallo.get("error_kind")
            fila = {"brazo": brazo, **fallo}
            if clase in ERRORES_DE_IMPEDIMENTO:
                impedimentos.append(fila)
            else:
                indisponibilidades.append(fila)
        if datos["contabilidad"]["fallos_de_contabilidad"]:
            impedimentos.append({"brazo": brazo,
                                 "motivos": datos["contabilidad"]["fallos_de_contabilidad"]})
    criterios = informe["criterios"]
    no_evaluables = [c for c, v in criterios.items()
                     if c != "coste_en_gobernanza" and v.get("estado") == "NO-EVALUABLE"]
    if filas_total == 0:
        return {"run_status": "NO-EJERCITADO", "impedimentos": [], "indisponibilidades": [],
                "criterios_no_evaluables": no_evaluables,
                "motivos": ["los registros no traen ninguna fila de ningun brazo"]}
    if impedimentos:
        return {"run_status": "FALLIDO", "impedimentos": impedimentos,
                "indisponibilidades": indisponibilidades,
                "criterios_no_evaluables": no_evaluables,
                "motivos": ["fallo de autenticacion, esquema, peticion o contabilidad: se corrige o "
                            "se declara impedimento operativo, nunca se usa para afirmar que Jev no "
                            "sirve (maestro :101)"]}
    if indisponibilidades or no_evaluables:
        motivos = []
        if indisponibilidades:
            motivos.append("un envio volvio con el camino caido: AC12 detiene o aplaza el brazo pero "
                           "no lo elimina, y la comparacion queda incompleta")
        if no_evaluables:
            motivos.append("criterios sin magnitud medible: " + ", ".join(no_evaluables))
        return {"run_status": "INCOMPLETO", "impedimentos": [], "indisponibilidades": indisponibilidades,
                "criterios_no_evaluables": no_evaluables, "motivos": motivos}
    return {"run_status": "COMPLETO", "impedimentos": [], "indisponibilidades": [],
            "criterios_no_evaluables": [], "motivos": []}


def regla_de_adopcion(informe: dict, protocolo: dict, estado_run: dict) -> dict:
    """La regla pre-registrada, aplicada sobre lo que `report` midio.

    `ACTIVAR` y `RECHAZAR` requieren los criterios pre-registrados evaluables (maestro :101): si
    falta la magnitud, el emisor NO elige y emite `decision=null` con las bases. El emisor propone;
    la adopcion la firma el operador (AC5).
    """
    criterios = informe["criterios"]
    sufragio = estado_run["run_status"] in ("COMPLETO", "INCOMPLETO")
    literales = {}
    cost = criterios["coste_en_gobernanza"]
    cob = criterios["cobertura_min"]
    suff = criterios["suficiencia_minima"]
    margen = criterios["margen_vs_deepseek"]
    lat = criterios["latencia_max"]

    decision, motivos_null = None, []
    if sufragio and estado_run["run_status"] == "INCOMPLETO" and estado_run["indisponibilidades"]:
        motivos_null.append("hubo un fallo operativo en la pata de inferencia: un fallo operativo "
                            "nunca es RECHAZAR (AC5)")
    if estado_run["run_status"] == "FALLIDO":
        motivos_null.append("run_status=FALLIDO por impedimento del camino o de la contabilidad; "
                            "la decision se declara null y el fallo se corrige, no se convierte en "
                            "un veredicto sobre el modelo")
    if estado_run["run_status"] == "NO-EJERCITADO":
        if cost["en_gobernanza"]:
            decision = "COSTE-NO-PAGADO"
            motivos_null.append("no hay envios y el coste esta en gobernanza: COSTE-NO-PAGADO "
                                "describe la decision de no ejecutar, no un rechazo del modelo")
        else:
            motivos_null.append("no hay envios y `usd` sigue fuera de gobernanza: COSTE-NO-PAGADO "
                                "queda bloqueado porque no hay coste que declarar pagado o no")
    if estado_run["run_status"] == "NO-EJERCITADO" and not cost["en_gobernanza"]:
        literales["COSTE-NO-PAGADO"] = {
            "estado": "BLOQUEADO", "base": "`usd` null en el protocolo congelado: no hay decision de "
                                           "coste sin coste en gobernanza"}
    elif decision == "COSTE-NO-PAGADO":
        literales["COSTE-NO-PAGADO"] = {"estado": "EMITIDA",
                                        "base": "run_status NO-EJERCITADO con coste en gobernanza"}
    else:
        literales["COSTE-NO-PAGADO"] = {
            "estado": "NO APLICA" if cost["en_gobernanza"] else "BLOQUEADO",
            "base": ("el run ejecuto envios: la decision de no gastar ya no describe esta corrida"
                     if cost["en_gobernanza"] else
                     "`usd` null en el protocolo congelado, fuera de gobernanza por decision del "
                     "operador: no hay decision de coste sin coste en gobernanza")}

    insuficiente = (suff["estado"] == "NO CUMPLE")
    if insuficiente:
        decision = "MUESTRA-INSUFICIENTE"
        literales["MUESTRA-INSUFICIENTE"] = {
            "estado": "EMITIDA",
            "base": f"suficiencia_minima {suff['umbral']} contra {suff['medido']['value']} medido "
                    f"({suff['medido']['numerator']}/{suff['medido']['denominator']})"}
    elif suff["estado"] == "CUMPLE":
        literales["MUESTRA-INSUFICIENTE"] = {
            "estado": "EXCLUIDA por la regla congelada; ponible por el operador",
            "base": f"suficiencia_minima se cumple ({suff['medido']['value']} >= {suff['umbral']}) "
                    f"en el denominador congelado, pero el denominador efectivo de la comparacion es "
                    f"{margen['denominador_efectivo_de_la_comparacion']} par(es) con eleccion "
                    "utilizable en los dos brazos",
            "nota": "si el operador la emite aun asi, la salida es muestra nueva y nunca re-etiquetar "
                    "la congelada"}
    else:
        literales["MUESTRA-INSUFICIENTE"] = {"estado": "NO-EVALUABLE",
                                             "base": suff["medido"]["motivo"] or "sin poblacion"}

    evaluables = all(criterios[c]["estado"] in ("CUMPLE", "NO CUMPLE")
                     for c in ("cobertura_min", "margen_vs_deepseek", "latencia_max"))
    if decision is None and not evaluables:
        faltan = [c for c in ("cobertura_min", "margen_vs_deepseek", "latencia_max")
                  if criterios[c]["estado"] == "NO-EVALUABLE"]
        motivos_null.append("criterios pre-registrados NO-EVALUABLE: " + ", ".join(faltan)
                            + "; ACTIVAR y RECHAZAR requieren magnitud medida, asi que el emisor no "
                            "elige y deja las bases para el operador")
    if cob["estado"] == "CUMPLE":
        literales["ACTIVAR"] = {"estado": "CUMPLE su condicion", "base": cob}
    elif cob["estado"] == "NO CUMPLE":
        literales["ACTIVAR"] = {
            "estado": "EXCLUIDA por medicion",
            "base": f"cobertura_min {cob['umbral']} contra {cob['medido_por_brazo'][BRAZO_SUJETO]} "
                    "medido en el brazo sujeto",
            "nota": "la condicion de adopcion que si se midio hasta el fondo; tampoco la arregla "
                    "cambiar de proveedor porque es una propiedad de la capa fria comun"}
    else:
        literales["ACTIVAR"] = {"estado": "NO-EVALUABLE", "base": cob["motivo"]}

    if decision is None and evaluables and not insuficiente:
        if (cob["estado"] == "CUMPLE" and margen["estado"] == "CUMPLE"
                and lat["estado"] == "CUMPLE"):
            decision = "ACTIVAR"
            literales["ACTIVAR"]["estado"] = "EMITIDA"
            literales["RECHAZAR"] = {"estado": "NO EMITIDA",
                                     "base": "los criterios congelados se cumplieron"}
        else:
            decision = "RECHAZAR"
            literales["RECHAZAR"] = {
                "estado": "EMITIDA",
                "base": f"comparacion valida con criterios evaluables y al menos uno NO CUMPLE: "
                        f"cobertura={cob['estado']}, margen={margen['estado']}, "
                        f"latencia={lat['estado']}"}
    elif decision is None:
        literales["RECHAZAR"] = {
            "estado": "NO EMITIDA",
            "base": "gobernaria el margen extremo_a_extremo, que es "
                    f"{margen['estado']}" + (", y la pata Jev tuvo un fallo operativo"
                                             if estado_run["indisponibilidades"] else "")}
    if decision is None:
        literales.setdefault("ACTIVAR", {"estado": "NO EMITIDA", "base": "decision=null"})
    return {"decision": decision,
            "motivo_decision_null": motivos_null,
            "literales_y_su_estado": literales,
            "requiere_revision_del_operador": True,
            "regla_aplicada": "criterios_adopcion del protocolo congelado, leidos y aplicados sin "
                              "re-interpretarse; el emisor propone y el operador adopta (AC5)"}


def decide(*, informe: dict, protocolo: dict, fecha: str = None) -> dict:
    """CR-2: emision mecanica de `decision.json` sobre lo que `report` calcula, sin red."""
    from datetime import date
    estado_run = estado_del_run(informe, protocolo)
    regla = regla_de_adopcion(informe, protocolo, estado_run)
    criterios = informe["criterios"]
    recomendacion = {
        "valor": (regla["decision"] if regla["decision"] else
                  "NO EMITIDA: el emisor no elige sin los criterios evaluables"),
        "base_medida": [
            f"run_status={estado_run['run_status']}",
            f"cobertura_min: {criterios['cobertura_min']['estado']} "
            f"(umbral {criterios['cobertura_min']['umbral']}, medido "
            f"{criterios['cobertura_min']['medido_por_brazo'].get(BRAZO_SUJETO)})",
            f"extremo_a_extremo jev={criterios['margen_vs_deepseek']['medido_jev']} vs "
            f"deepseek={criterios['margen_vs_deepseek']['medido_deepseek']}, margen "
            f"{criterios['margen_vs_deepseek']['estado']}",
            f"latencia_max: {criterios['latencia_max']['estado']} (umbral "
            f"{criterios['latencia_max']['umbral_ms']} ms)",
        ],
        "no_significa": ["no es un cambio de default: `modules/providers/llm_provider.py` no se toca",
                         "no es deuda cerrada de ningun plan",
                         "no es un veredicto de calidad si el brazo sujeto tiene fallos del camino"],
        "antecedente": "FASE-C emito una lectura de sesion ('NO ADOPTAR; MANTENER COMO BRAZO "
                       "MEDIBLE') que ningun instrumento produjo; este campo es la salida del emisor "
                       "y se revisa contra ese registro, no lo re-transcribe",
        "requiere_revision_del_operador": True,
    }
    d6 = {
        "valor": ("NO ELEGIBLE" if criterios["cobertura_min"]["estado"] != "CUMPLE"
                  else "PENDIENTE DE LA SEGUNDA PATA"),
        "disparador_del_plan": "D6 exige pertinencia aceptable y candidatos nuevos; no exige que gane "
                               "Jev",
        "por_cada_pata": {
            "pertinencia_aceptable": f"{criterios['cobertura_min']['estado']}: cobertura_min "
                                     f"{criterios['cobertura_min']['umbral']} contra "
                                     f"{criterios['cobertura_min']['medido_por_brazo'].get(BRAZO_SUJETO)}",
            "candidatos_nuevos": "NO la mide este instrumento: su fuente es el triaje versionado "
                                 "(`candidatos_de_pertinencia`), citado en el registro de la fase",
        },
        "independencia": "la pata que falla es una propiedad de la capa fria, comun a los tres brazos",
    }
    decision = {
        "schema": DECISION_SCHEMA,
        "plan": "EVALUACION-JEV-TYPESAFE-2026-09-21",
        "fecha": fecha or date.today().isoformat(),
        "instrumento_de_emision": "scripts/evaluate_jev_pilot.py decide, sobre el informe de "
                                  "scripts/evaluate_jev_pilot.py report",
        "run_status": estado_run["run_status"],
        "decision": regla["decision"],
        "motivo_decision_null": regla["motivo_decision_null"],
        "estado_del_run": {"impedimentos": estado_run["impedimentos"],
                           "indisponibilidades": estado_run["indisponibilidades"],
                           "criterios_no_evaluables": estado_run["criterios_no_evaluables"],
                           "motivos": estado_run["motivos"]},
        "criterios_congelados": criterios,
        "literales_y_su_estado": regla["literales_y_su_estado"],
        "jev_recommendation": recomendacion,
        "d6_eligibility": d6,
        "transfer_status": "PENDIENTE",
        "motivo_transferencia": "la deuda del hermano solo se mueve con instruccion literal del "
                                "operador que nombre archivos y alcance, tras re-leer su estado; no "
                                "existe un flag que la simule",
        "requiere_revision_del_operador": True,
        "revision_humana_del_protocolo": (protocolo.get("criterios_adopcion") or {})
                                          .get("revision_humana"),
    }
    return decision


# Que celda del criterio es "lo medido", por nombre y no por una cadena de `or`: un 0.0 legitimo
# (una diferencia de margen que efectivamente es cero) es falso en Python y con `or` desaparecia de
# la tabla, que es la forma mas cara de perder un dato.
MEDIDO_DEL_CRITERIO = {"cobertura_min": "medido_por_brazo", "suficiencia_minima": "medido",
                       "margen_vs_deepseek": "diferencia_calculada",
                       "latencia_max": "medido_ms_por_brazo"}


def decision_markdown(decision: dict, informe: dict) -> str:
    """`decision.md` del mismo calculo: AC5 pide los dos artefactos, no un texto aparte."""
    lineas = [
        f"# Decision del piloto JEV - {decision['plan']}",
        "",
        f"- Emisor: {decision['instrumento_de_emision']}",
        f"- Fecha: {decision['fecha']}",
        f"- `run_status`: **{decision['run_status']}**",
        f"- `decision`: **{decision['decision'] if decision['decision'] else 'null'}**",
        "- Estado: propuesto por el runner, **pendiente de revision del operador** (AC5).",
        "",
        "## Criterios congelados, aplicados sin releerse",
        "",
        "| Criterio | Umbral | Medido | Estado |",
        "|---|---|---|---|",
    ]
    for clave in ("cobertura_min", "suficiencia_minima", "margen_vs_deepseek", "latencia_max"):
        criterio = decision["criterios_congelados"][clave]
        campo = MEDIDO_DEL_CRITERIO[clave]
        valor = criterio.get(campo)
        if isinstance(valor, dict):
            if "value" in valor:
                valor = f"{valor['value']} ({valor['numerator']}/{valor['denominator']})"
            else:
                valor = "; ".join(f"{k}={v}" for k, v in valor.items())
        elif valor is None:
            valor = f"no medido: {criterio.get('motivo') or criterio.get('medido', {}).get('motivo', '')}"
        umbral = (criterio.get("umbral") if criterio.get("umbral") is not None
                  else criterio.get("umbral_ms"))
        lineas.append(f"| {clave} | {umbral} | {valor} | {criterio['estado']} |")
    lineas += ["", "## Los cuatro literales", ""]
    for literal, estado in decision["literales_y_su_estado"].items():
        lineas.append(f"- **{literal}**: {estado['estado']} - {estado['base']}")
    if decision["motivo_decision_null"]:
        lineas += ["", "## Por que `decision = null`", ""]
        lineas += [f"- {motivo}" for motivo in decision["motivo_decision_null"]]
    lineas += [
        "", "## Cocientes por brazo (denominadores separados)", "",
        "| Brazo | " + " | ".join(COCIENTES_INFORME) + " |",
        "|---|" + "---|" * len(COCIENTES_INFORME),
    ]
    for brazo, datos in informe["por_brazo"].items():
        celdas = []
        for cociente in COCIENTES_INFORME:
            q = datos[cociente]
            celdas.append("NO-EVALUABLE" if q["value"] is None else
                          f"{q['value']} ({q['numerator']}/{q['denominator']})")
        lineas.append(f"| {brazo} | " + " | ".join(celdas) + " |")
    lineas += [
        "", "## Separacion de decisiones (AC7)", "",
        f"- `jev_recommendation`: {decision['jev_recommendation']['valor']}",
        f"- `d6_eligibility`: {decision['d6_eligibility']['valor']}",
        f"- `transfer_status`: {decision['transfer_status']} - {decision['motivo_transferencia']}",
        "",
    ]
    return "\n".join(lineas)


CREDENCIAL_DEL_SDK = "TYPESAFE_API_KEY"


def credencial_del_sdk(raiz: Path, *, nombre: str = CREDENCIAL_DEL_SDK) -> dict:
    """CR-3: la credencial llega por el camino del contrato, que es el entorno del SDK.

    `decision_client.cliente_jev` pasa `api_key=None` a proposito: el SDK resuelve la clave desde su
    propia variable de entorno. Este helper solo rellena esa variable cuando NO existe, leyendo
    `.env` por nombre --la misma via que usaron los arneses de la fase anterior--. No devuelve el
    valor ni su longitud: un estado. Imprimir la longitud ya es una fuga de la forma del secreto.
    """
    import os
    if os.environ.get(nombre):
        return {"nombre": nombre, "fuente": "entorno", "accion": "ninguna"}
    ruta_env = Path(raiz) / ".env"
    if not ruta_env.exists():
        return {"nombre": nombre, "fuente": "ausente", "accion": "env-no-encuentra-env"}
    try:
        from dotenv import dotenv_values
    except ImportError:
        return {"nombre": nombre, "fuente": "ausente", "accion": "dotenv-no-instalado"}
    valor = dotenv_values(ruta_env).get(nombre)
    if not valor:
        return {"nombre": nombre, "fuente": "ausente", "accion": "clave-no-esta-en-env"}
    os.environ[nombre] = valor
    return {"nombre": nombre, "fuente": "dotenv", "accion": "rellenada-desde-env"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="evaluate_jev_pilot.py",
        description="Instrumento offline del piloto Jev (prepare/check/metricas).")
    sub = parser.add_subparsers(dest="mode")

    p = sub.add_parser("prepare", help="prepara muestra y etiquetas desde candidatos (offline)")
    p.add_argument("--candidates", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--temporal-cut", default="2026-09-12")
    p.add_argument("--corpus-source", default="own:lecciones_index")

    c = sub.add_parser("check", help="verifica esquema/hashes/splits/etiquetas (offline)")
    c.add_argument("--muestra", required=True)
    c.add_argument("--etiquetas", required=True)
    c.add_argument("--out")

    r = sub.add_parser("run", help="corrida explicita por proveedor (FASE-B): exige preflight (AC12) "
                                   "y presupuesto (AC8) antes de construir nada")
    r.add_argument("--proveedor", help="jev | deepseek: explicito y sin default (L-ENT.9)")
    r.add_argument("--muestra")
    r.add_argument("--protocolo")
    r.add_argument("--indice", help=".opencode/lecciones_index.json: la poblacion de la capa fria")
    r.add_argument("--preflight")
    r.add_argument("--out-dir")
    r.add_argument("--k", type=int, default=8)
    r.add_argument("--splits", default="dev",
                   help="lista separada por comas; por defecto solo `dev`, porque el maestro reserva "
                        "`eval` para despues de congelar prompt y umbrales")
    r.add_argument("--autorizar-null",
                   help="motivo literal del operador que autoriza correr con tokens_in/tokens_out en null")
    r.add_argument("--etiquetas",
                   help="etiquetas.json del conjunto elegible: sin ella la recuperacion medida no "
                        "se publica (CR-3; el runner sigue sin leer etiquetas para elegir)")

    rp = sub.add_parser("report", help="reproduce la comparacion desde registros persistidos "
                                       "(offline: cero red, cero clientes, cero credenciales)")
    rp.add_argument("--respuestas", help="respuestas.jsonl: una fila por (par, brazo)")
    rp.add_argument("--etiquetas", help="etiquetas.json del conjunto elegible")
    rp.add_argument("--muestra", help="muestra.json congelada: la poblacion y los splits")
    rp.add_argument("--protocolo", help="protocolo.json: k y los criterios congelados")
    rp.add_argument("--out", help="ruta del informe; sin ella imprime y no escribe")
    rp.add_argument("--fecha", help="fecha del artefacto; por defecto la de hoy")

    dc = sub.add_parser("decide", help="aplica la regla pre-registrada del protocolo congelado "
                                       "sobre el informe del runner (offline)")
    dc.add_argument("--informe", help="informe_comparativa.json producido por `report`")
    dc.add_argument("--protocolo", help="protocolo.json con los criterios congelados")
    dc.add_argument("--out-dir", help="directorio donde se escriben decision.json y decision.md")
    dc.add_argument("--fecha", help="fecha del artefacto; por defecto la de hoy")

    pc = sub.add_parser("protocolo-check",
                        help="valida protocolo.json contra el schema, sus ocho umbrales y sus "
                             "null admitidos (sin red)")
    pc.add_argument("--protocolo", required=True)
    pc.add_argument("--out")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.mode == "prepare":
        candidates = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
        muestra, etiquetas = prepare(candidates, args.temporal_cut, args.corpus_source)
        out = Path(args.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "muestra.json").write_text(
            json.dumps(muestra, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / "etiquetas.json").write_text(
            json.dumps(etiquetas, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"prepare OK: {muestra['counts']} (status {muestra['status']})")
        return 0
    if args.mode == "check":
        result = check(Path(args.muestra), Path(args.etiquetas))
        if args.out:
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out).write_text(
                json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["check_status"] == "OK" else 1
    if args.mode == "protocolo-check":
        datos = _load_json(Path(args.protocolo))
        resultado = validar_protocolo(datos)
        if args.out:
            _persistir(Path(args.out).parent, Path(args.out).name, resultado)
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return 0 if resultado["check_status"] == "OK" else 1
    if args.mode == "run":
        # Sin alguno de los seis argumentos obligatorios no se construye nada y se sale 2: es el mismo
        # numero que la negacion historica de `run`, asi que el contrato offline del test de FASE-A
        # (`main(["run"]) == 2`) sigue siendo verdad con el modo ya implementado.
        faltan = [clave for clave, valor in (("proveedor", args.proveedor), ("muestra", args.muestra),
                                             ("protocolo", args.protocolo), ("indice", args.indice),
                                             ("preflight", args.preflight),
                                             ("out-dir", args.out_dir)) if not valor]
        if faltan:
            sys.stderr.write("run exige " + ", ".join(faltan) +
                             ": sin ellos no se instancia un cliente ni se gasta una llamada (AC8).\n")
            return 2
        resultado = run(
            muestra=Path(args.muestra), protocolo=Path(args.protocolo), indice=Path(args.indice),
            preflight=Path(args.preflight), out_dir=Path(args.out_dir), proveedor=args.proveedor,
            k=args.k, splits=args.splits,
            etiquetas=Path(args.etiquetas) if args.etiquetas else None,
            autorizacion_de_null={"declarada": True, "motivo": args.autorizar_null}
            if args.autorizar_null else {})
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return {"OK": 0, "NEGADO": 2}.get(resultado["status"], 1)
    if args.mode == "report":
        faltan = [clave for clave, valor in (("respuestas", args.respuestas), ("etiquetas", args.etiquetas),
                                             ("muestra", args.muestra), ("protocolo", args.protocolo))
                  if not valor]
        if faltan:
            return _refuse("report", faltan)
        ausentes = [ruta for ruta in (args.respuestas, args.etiquetas, args.muestra, args.protocolo)
                    if not Path(ruta).exists()]
        if ausentes:
            sys.stderr.write("report no encuentra insumos: " + ", ".join(ausentes) + "\n")
            return 1
        informe = report(respuestas=Path(args.respuestas), etiquetas=Path(args.etiquetas),
                         muestra=Path(args.muestra), protocolo=Path(args.protocolo), fecha=args.fecha)
        if args.out:
            _persistir(Path(args.out).parent, Path(args.out).name, informe)
        print(json.dumps(informe, ensure_ascii=False, indent=2))
        return 0
    if args.mode == "decide":
        faltan = [clave for clave, valor in (("informe", args.informe), ("protocolo", args.protocolo))
                  if not valor]
        if faltan:
            return _refuse("decide", faltan)
        if not Path(args.informe).exists():
            sys.stderr.write(f"decide no encuentra el informe: {args.informe}\n")
            return 1
        informe = _load_json(Path(args.informe))
        faltan_claves = [clave for clave in ("criterios", "por_brazo") if clave not in informe]
        if faltan_claves:
            sys.stderr.write(
                "decide espera un informe producido por `report`: le faltan "
                + ", ".join(faltan_claves)
                + ". Un informe escrito a mano no es un insumo de este emisor (AC10).\n")
            return 1
        decision = decide(informe=informe, protocolo=_load_json(Path(args.protocolo)),
                          fecha=args.fecha)
        if args.out_dir:
            _persistir(Path(args.out_dir), "decision.json", decision)
            _persistir(Path(args.out_dir), "decision.md", decision_markdown(decision, informe))
        print(json.dumps(decision, ensure_ascii=False, indent=2))
        return 0 if decision["decision"] else 3
    build_parser().print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
