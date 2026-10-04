#!/usr/bin/env python3
"""Instrumento del piloto Jev (EVALUACION-JEV-TYPESAFE-2026-09-21).

`prepare` y `check` siguen siendo LOCALES y deterministas: NO importan clientes de inferencia, NO
abren red y NO leen credenciales, y esa regla la goberna `FORBIDDEN_MODULES` con su test. `run`
llego en FASE-B (2026-10-03) y no cambia el contrato offline: se construye solo con preflight de
AC12 y presupuesto de AC8 reservados, y el SDK lo carga la puerta (`scripts/decision_client.py`),
que es el unico sitio donde AC6 admite ese import. `decide` pertenece a FASE-C y aqui se niega sin
instanciar nada. Un par de triaje es (target_plan, lesson_id) con
una etiqueta humana {pertinente|no_pertinente|insuficiente} e importancia.
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
    for clave in ("tokens_in", "tokens_out"):
        if limites.get(clave) is None and not autorizacion.get("declarada"):
            motivos.append(f"techo_de_{clave}_sin_declarar")
    restantes = (llamadas - usadas) if (isinstance(llamadas, int)
                                         and isinstance(usadas, int)) else None
    return {"reservado": not motivos, "motivos": motivos, "llamadas_restantes": restantes}


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


def _refuse(name: str) -> int:
    sys.stderr.write(
        f"{name} corresponde a FASE-B/FASE-C: requiere preflight (AC8), "
        f"presupuesto y autorizacion literal, y no se instancia aqui. "
        f"El modo offline no construye clientes ni abre red.\n")
    return 2


# --- FASE-B, paso 1a (2026-10-03): el modo `run`, con preflight y presupuesto antes de enviar ---
# El runner NO importa el SDK: lo carga la puerta (`scripts/decision_client.py`), que es el unico
# sitio donde AC6 admite ese import. Aqui se goberna CUANDO se construye: sin preflight de AC12 y
# sin reserva de AC8 no hay ni un intento, y eso se publica con su causa en vez de callarse.

PREFLIGHT_SCHEMA = "jev-pilot-preflight/v1"
ESTADOS_PREFLIGHT_OBLIGATORIOS = {"habilitacion_declarada": True, "sdk_instalado": True,
                                  "autenticacion_real": "AUTENTICADA"}
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


def revisar_preflight(ruta_preflight: Path, proveedor: str) -> dict:
    """AC12 como precondicion de AC8: los cuatro estados por proveedor, y tres se exigen.

    `cuota_o_saldo` se **declara** pero no se exige: medido el 2026-10-03, `typesafe_sdk` 0.7.0 no
    expone superficie de saldo, asi que exigirla forzaria a fingirla. Lo que no esta se estampa con
    su motivo, no con un valor que parezca favorable.
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
    motivos = [f"preflight-{clave}={registro.get(clave)!r}"
               for clave, esperado in ESTADOS_PREFLIGHT_OBLIGATORIOS.items()
               if registro.get(clave) != esperado]
    return {"ok": not motivos, "motivos": motivos, "registro": registro,
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
    if enviar is None:
        # La construccion del cliente y el envio van juntos detras de la inyeccion: un test con
        # transporte falso tiene que poder ejercitar el guard, el ledger y la contabilidad sin
        # necesitar la credencial real que `TypeSafeClient` resuelve por entorno.
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
        cuenta["llamadas_usadas"] += 1
        cuenta["intentos"] += estado["attempts"]
        uso = estado["usage_normalized"]
        if uso.get("input_tokens") is not None:
            cuenta["tokens_in_max"] = max(cuenta.get("tokens_in_max") or 0, uso["input_tokens"])
        if uso.get("output_tokens") is not None:
            cuenta["tokens_out_max"] = max(cuenta.get("tokens_out_max") or 0, uso["output_tokens"])
        if uso.get("estado") not in ("observado",):
            cuenta.setdefault("usage_estados", []).append(uso.get("estado"))
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
                 "resolucion_sdk": resolucion_sdk, "recuperacion": recuperacion,
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

    pc = sub.add_parser("protocolo-check",
                        help="valida protocolo.json contra el schema, sus ocho umbrales y sus "
                             "null admitidos (sin red)")
    pc.add_argument("--protocolo", required=True)
    pc.add_argument("--out")

    sub.add_parser("decide", help="[FASE-C] no disponible en modo offline")
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
            autorizacion_de_null={"declarada": True, "motivo": args.autorizar_null}
            if args.autorizar_null else {})
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return {"OK": 0, "NEGADO": 2}.get(resultado["status"], 1)
    if args.mode == "decide":
        return _refuse("decide")
    build_parser().print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
