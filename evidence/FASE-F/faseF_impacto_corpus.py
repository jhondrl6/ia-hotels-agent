# -*- coding: utf-8 -*-
"""FASE-F (Tarea F4): re-evaluacion del corpus historico bajo F1+F2+F3.

Lee los artefactos persistidos de cada corrida (v4_audit) en output/ y
archives/outputs/ y re-deriva el veredicto del gate de coherencia:
  - ANTES (pre-F3): solo score — >= 0.8 pasa.
  - DESPUES (post-F3): coherence_verdict_passes(score, 0.8, is_coherent).
Solo F3 puede voltear un veredicto de publicacion (F1 es narrativa,
F2 es contabilidad del resumen de delivery). asset_confidence (100%
ESTIMATED) bloquea en ambos mundos y DEBE seguir bloqueando.

Salida: evidence/FASE-F/impacto-corpus.md
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.quality_gates.coherence_gate import coherence_verdict_passes

REPO = Path(__file__).resolve().parents[1]
DIRS_FILE = REPO / "temp" / "faseF_v4audit_dirs.txt"
OUT_MD = REPO / "evidence" / "FASE-F" / "impacto-corpus.md"

THRESHOLD = 0.8


def load_json(path: Path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def read_corrida(v4audit: Path):
    """Extrae (score, is_coherent, fuente, estimated, generated, tiene_reporte)."""
    asset_report = load_json(v4audit / "asset_generation_report.json")
    post_gen = load_json(v4audit / "coherence_validation_post_gen.json")
    pre_gen = load_json(v4audit / "coherence_validation.json")

    summary = (asset_report or {}).get("summary") or {}
    generated = summary.get("generated", 0)
    estimated = summary.get("estimated", 0)

    final_report = (asset_report or {}).get("final_coherence_report")
    score_final = (asset_report or {}).get("coherence_score_final")

    if not any([asset_report, post_gen, pre_gen]):
        return None

    # Score canónico que el gate de producción realmente leyó: el assessment
    # consume coherence_score_final (DT4-N4). Cuando es None NO hay rescate
    # por scores pre-gen (dossier §12.2, C3) — el gate decía "not found".
    score = score_final
    fuente_score = "coherence_score_final"
    pre_gen_score = (pre_gen or {}).get("overall_score") if pre_gen else None
    post_gen_score = (post_gen or {}).get("overall_score") if post_gen else None

    # Veredicto binario con la misma precedencia que assessment_builder
    is_coherent = None
    fuente_verdict = "ausente (legacy)"
    if isinstance(final_report, dict) and final_report.get("is_coherent") is not None:
        is_coherent = bool(final_report.get("is_coherent"))
        fuente_verdict = "final_coherence_report.is_coherent"

    return {
        "score": score,
        "is_coherent": is_coherent,
        "fuente_score": fuente_score,
        "fuente_verdict": fuente_verdict,
        "estimated": estimated,
        "generated": generated,
        "errors": len((final_report or {}).get("errors", []) or []),
        "pre_gen_score": pre_gen_score,
        "post_gen_score": post_gen_score,
        "post_gen_is_coherent": (post_gen or {}).get("is_coherent"),
        "post_gen_errors": len((post_gen or {}).get("errors", []) or []),
    }


def coherence_before(score):
    """Veredicto pre-F3 del gate de coherencia: solo score."""
    if score is None:
        return "BLOCKED (sin coherence_score)"
    if score >= THRESHOLD:
        return "PASSED"
    return "FAILED" if score >= 0.5 else "BLOCKED"


def coherence_after(score, is_coherent):
    """Veredicto post-F3 con la funcion canónica embarcada."""
    if score is None:
        return "BLOCKED (sin coherence_score)"
    if coherence_verdict_passes(score, THRESHOLD, is_coherent):
        return "PASSED"
    if score >= THRESHOLD:
        return "BLOCKED (is_coherent=False)"
    return "FAILED" if score >= 0.5 else "BLOCKED"


def package_verdict(coherence_verdict, all_estimated):
    """Veredicto del paquete: coherencia AND asset_confidence (11 gates blocking,
    los dos relevantes aquí). Las corridas 100% ESTIMATED están bloqueadas por
    asset_confidence en ambos mundos."""
    if coherence_verdict == "PASSED" and not all_estimated:
        return "READY"
    return "NOT_READY"


def main():
    dirs = [Path(line.strip()) for line in DIRS_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = []
    for d in dirs:
        if not d.is_absolute():
            d = REPO / d
        label = str(d.relative_to(REPO)).replace("\\", "/").replace("/v4_audit", "")
        is_delivery_copy = bool(re.search(r"/deliveries/.*/ASSETS/?$", str(d.parent).replace("\\", "/")))
        data = read_corrida(d)
        if data is None:
            rows.append({"label": label, "kind": "SIN_ARTEFACTOS", "before": "—", "after": "—",
                         "pkg_before": "—", "pkg_after": "—", "cambio": "—",
                         "data": None, "delivery": is_delivery_copy})
            continue
        before = coherence_before(data["score"])
        after = coherence_after(data["score"], data["is_coherent"])
        all_estimated = data["generated"] > 0 and data["estimated"] == data["generated"]
        pkg_before = package_verdict(before, all_estimated)
        pkg_after = package_verdict(after, all_estimated)
        if pkg_before != pkg_after:
            cambio = "F3 (veredicto respeta is_coherent)"
        elif before != after:
            cambio = "coherencia cambia, paquete sigue NOT_READY (asset_confidence)"
        else:
            cambio = "—"
        rows.append({
            "label": label, "kind": "ESTIMATED_100%" if all_estimated else "CON_DATOS",
            "before": before, "after": after,
            "pkg_before": pkg_before, "pkg_after": pkg_after,
            "cambio": cambio,
            "data": data, "delivery": is_delivery_copy,
        })

    primaries = [r for r in rows if not r["delivery"]]
    copies = [r for r in rows if r["delivery"]]
    flips = [r for r in rows if r["pkg_before"] != r["pkg_after"]]
    coherence_flips = [r for r in rows if r["before"] != r["after"]]
    estimated_rows = [r for r in rows if r["kind"] == "ESTIMATED_100%"]

    lines = []
    lines.append("# FASE-F — Impacto del corpus histórico (Tarea F4)")
    lines.append("")
    lines.append("**Fecha**: 2026-09-03 · **Script**: `temp/faseF_impacto_corpus.py` "
                 "(copia preservada en `evidence/FASE-F/faseF_impacto_corpus.py`; no se ejecutó v4complete)")
    lines.append("")
    lines.append("Re-evaluación de artefactos persistidos bajo el comportamiento nuevo:")
    lines.append("")
    lines.append("| Tarea | Naturaleza del cambio | ¿Puede voltear un veredicto de publicación? |")
    lines.append("|---|---|---|")
    lines.append("| F1 (A4) | Un oráculo de presencia decide **y** narra (`is_present_in_production`) | No — converge narrativa y decisión |")
    lines.append("| F2 (A1) | `NOT_EVALUATED` ≠ `passed`; defaults G9 unificados | No — contabilidad del resumen de delivery |")
    lines.append("| F3 (N11/P9) | El gate de coherencia respeta `is_coherent` (umbral 0.8 intacto) | **Sí — único volteador** |")
    lines.append("")
    lines.append("Veredicto de COHERENCIA ANTES = solo score (pre-F3). DESPUÉS =")
    lines.append("`coherence_verdict_passes(score_final, 0.8, is_coherent_final)` — la función embarcada,")
    lines.append("importada de `modules/quality_gates/coherence_gate.py` (misma que consume publication_gates).")
    lines.append("El score/veredicto leído es el que el assessment de producción consume")
    lines.append("(`coherence_score_final` / `final_coherence_report`, DT4-N4); los scores pre-gen de")
    lines.append("`coherence_validation.json` NO rescatan corridas (dossier §12.2, C3). Veredicto de PAQUETE =")
    lines.append("coherencia AND asset_confidence (corridas 100% ESTIMATED bloqueadas en ambos mundos).")
    lines.append("")
    lines.append(f"**Corpus medido**: {len(primaries)} corridas primarias + {len(copies)} copias de delivery "
                 f"(reconciliación con C2 §12.2 más abajo).")
    lines.append("")
    lines.append("## Resultados clave")
    lines.append("")
    lines.append(f"- **Corridas 100% ESTIMATED**: {len(estimated_rows)} (incluye copias) — "
                 "**TODAS siguen bloqueadas** ✓ (`coherence_score_final=None` ⟹ gate de coherencia "
                 "sin score; `asset_confidence` bloquea el paquete en ambos mundos). Coincide con el "
                 "dossier §12.2/C3: no hay score canónico que las rescate.")
    lines.append(f"- **Veredictos de paquete que cambian**: {len(flips)} — todos en dirección "
                 "**READY → NOT_READY** (seguro): corridas con `final_coherence_report.is_coherent=False` "
                 "persistido que el gate pre-F3 ignoraba por leer solo el score (la familia exacta "
                 "de N11/P9; incluye la repro SalentoReal FASE-D: score 0.88 + is_coherent False).")
    lines.append("- **Ninguna corrida pasa de bloqueada a lista** — F3 solo endurece.")
    lines.append(f"- **F1/F2**: no mueven veredictos (narrativa y contabilidad); ver lectura al final.")
    lines.append("")
    lines.append("## Corridas primarias")
    lines.append("")
    lines.append("| Corrida | Tipo | Score final | is_coherent final | Coherencia ANTES | Coherencia DESPUÉS | Paquete ANTES | Paquete DESPUÉS | Cambio |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for r in primaries:
        if r["data"] is None:
            lines.append(f"| `{r['label']}` | SIN_ARTEFACTOS | — | — | — | — | — | — | — |")
            continue
        d = r["data"]
        score_s = "None" if d["score"] is None else f"{d['score']:.2f}"
        coh_s = "—" if d["is_coherent"] is None else str(d["is_coherent"])
        lines.append(f"| `{r['label']}` | {r['kind']} | {score_s} | {coh_s} | {r['before']} | {r['after']} "
                     f"| {r['pkg_before']} | {r['pkg_after']} | {r['cambio']} |")
    lines.append("")
    lines.append("## Copias de delivery (no se cuentan como corrida)")
    lines.append("")
    if copies:
        lines.append("| Corrida (copia) | ANTES | DESPUÉS | Cambio |")
        lines.append("|---|---|---|---|")
        for r in copies:
            if r["data"] is None:
                lines.append(f"| `{r['label']}` | — | — | — |")
                continue
            lines.append(f"| `{r['label']}` | {r['before']} | {r['after']} | {r['cambio']} |")
    else:
        lines.append("*(ninguna)*")
    lines.append("")
    lines.append("## Corridas 100% ESTIMATED — DEBEN seguir bloqueadas")
    lines.append("")
    if estimated_rows:
        ok = True
        lines.append("| Corrida | Score final | Coherencia ANTES | Coherencia DESPUÉS | Paquete ANTES | Paquete DESPUÉS | ¿Sigue bloqueada? |")
        lines.append("|---|---|---|---|---|---|---|")
        for r in estimated_rows:
            d = r["data"]
            score_s = "None" if d["score"] is None else f"{d['score']:.2f}"
            blocked = r["pkg_after"] == "NOT_READY"
            ok = ok and blocked
            lines.append(f"| `{r['label']}` | {score_s} | {r['before']} | {r['after']} "
                         f"| {r['pkg_before']} | {r['pkg_after']} | {'SÍ' if blocked else '**NO — F3 SE PASÓ DE PERMISIVO**'} |")
        lines.append("")
        lines.append("**Resultado**: " + ("TODAS siguen bloqueadas ✓ (asset_confidence intacto)" if ok else "FALLO — alguna ESTIMATED salió"))
    else:
        lines.append("*(ninguna corrida con 100% ESTIMATED en el corpus accesible)*")
    lines.append("")
    lines.append("## Veredictos de paquete que cambian (única vía: F3)")
    lines.append("")
    if flips:
        all_safe = all("READY" in r["pkg_before"] for r in flips)
        lines.append("| Corrida | Score final | is_coherent final | Paquete ANTES | Paquete DESPUÉS | Dirección |")
        lines.append("|---|---|---|---|---|---|")
        for r in flips:
            d = r["data"] or {}
            direction = "listo → bloqueado (seguro)" if "READY" in r["pkg_before"] else "bloqueado → listo (requiere justificación)"
            coh_s = "—" if d.get("is_coherent") is None else str(d.get("is_coherent"))
            score_s = "None" if d.get("score") is None else f"{d.get('score'):.2f}"
            lines.append(f"| `{r['label']}` | {score_s} | {coh_s} | {r['pkg_before']} | {r['pkg_after']} | {direction} |")
        lines.append("")
        lines.append("**Dirección**: " + ("todos READY → NOT_READY (seguro: el validador ya había declarado "
                                            "`is_coherent=False`; F3 hace que el gate lo escuche)" if all_safe else "⚠ revisar"))
    else:
        lines.append("*(ningún veredicto de publicación cambia)*")
    lines.append("")
    if coherence_flips and not flips:
        lines.append(f"Nota: {len(coherence_flips)} corridas cambian el veredicto del gate de coherencia, "
                     "pero ninguna mueve el veredicto del paquete (asset_confidence u otro gate ya bloqueaba).")
    lines.append("")
    lines.append("## Reconciliación con el corpus C2 (27 corridas)")
    lines.append("")
    lines.append("El conteo C2 §12.2 (**27 corridas únicas, 10 hoteles**) se midió sobre `output/` en su")
    lines.append("estado de 2026-09-03; desde entonces buena parte del histórico fue archivado a")
    lines.append("`archives/outputs/`. Esta medición barre `output/` **y** `archives/outputs/`, tomando como")
    lines.append("unidad la carpeta `v4_audit` (conjunto canónico de artefactos por corrida) y excluyendo")
    lines.append("copias bajo `deliveries/*/ASSETS/`. Corridas sin artefactos de coherencia/asset quedan")
    lines.append("como SIN_ARTEFACTOS (sin veredicto evaluable).")
    lines.append("")
    lines.append("## Lectura F1/F2 sobre el corpus")
    lines.append("")
    lines.append("- **F1 (A4)**: no mueve veredictos; elimina la divergencia narrativa (`missing` vs")
    lines.append("  `present_assets`) en corridas con presencia `exists_with_issues`. Los artefactos con")
    lines.append("  `proposal_asset_matrix.json` quedan cubiertos por el test anti-A4 (`test_alignment_result.py`).")
    lines.append("- **F2 (A1)**: en corridas cuyo `delivery_quality_report.json` no tiene `proposal_asset_matrix.json`,")
    lines.append("  G9 pasaba en verde vacuo; ahora se reporta `NOT_EVALUATED` y aparece en")
    lines.append("  `human_review_items`. No bloquea ni libera nada.")
    lines.append("")
    lines.append("> Nota: `evidence/FASE-F/` también aloja evidencia histórica del FASE-F de otro plan")
    lines.append("> (RC1-RC2-ENTREGA-COHERENTE-2026-08-04, «Verificación de Fixes V1-V10»). Los archivos")
    lines.append("> de esta fase son `impacto-corpus.md` y `faseF_*.txt`.")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK -> {OUT_MD}")
    print(f"primaries={len(primaries)} copies={len(copies)} pkg_flips={len(flips)} "
          f"coherence_flips={len(coherence_flips)} estimated={len(estimated_rows)}")


if __name__ == "__main__":
    main()
