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
FORBIDDEN_MODULES = {"typesafe", "httpx", "httpx2", "httpcore", "httpcore2",
                     "tenacity", "anthropic", "openai", "requests", "urllib.request"}


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
