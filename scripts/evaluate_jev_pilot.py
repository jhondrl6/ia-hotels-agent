#!/usr/bin/env python3
"""Instrumento offline del piloto Jev (EVALUACION-JEV-TYPESAFE-2026-09-21).

FASE-A entrega solo los modos LOCALES y deterministas: `prepare` y `check`,
mas las funciones de metricas. NO importa clientes de inferencia, NO abre red
y NO lee credenciales. `run` y `decide` pertenecen a FASE-B/FASE-C y aqui se
niegan sin instanciar nada. Un par de triaje es (target_plan, lesson_id) con
una etiqueta humana {pertinente|no_pertinente|insuficiente} e importancia.
"""
from __future__ import annotations

import argparse
import hashlib
import json
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
    """
    def _entero(valor):
        return valor if isinstance(valor, int) and not isinstance(valor, bool) else None

    if usage is None:
        return {"input_tokens": None, "output_tokens": None, "total": None,
                "estado": "sin_usage", "libera_reserva_como_cero": False}
    entrada = _entero(getattr(usage, "input_tokens", None))
    salida = _entero(getattr(usage, "output_tokens", None))
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

    sub.add_parser("run", help="[FASE-B/C] no disponible en modo offline")
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
    if args.mode == "run":
        return _refuse("run")
    if args.mode == "decide":
        return _refuse("decide")
    build_parser().print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
