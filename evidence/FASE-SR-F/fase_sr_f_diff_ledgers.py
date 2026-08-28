"""FASE-SR-F T1 — Diff forense de pain_ledgers y asset_generation_reports entre corridas A y C.

Solo lectura. Salida redirigida a archivo por el caller (evidencia de la fase).
"""
import json
from pathlib import Path

ROOT = Path(r"C:\Users\Jhond\Github\iah-cli")
RUN_A = ROOT / "output" / "v4_complete" / "hotelsalentoreal" / "v4_audit"
RUN_C = ROOT / "output" / "test_salentoreal_v4c" / "v4_complete" / "hotelsalentoreal" / "v4_audit"

OUT = ROOT / "temp" / "fase_sr_f_ledger_diff.txt"


def load(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def pain_ids(ledger: dict):
    return [e["pain_id"] for e in ledger.get("entries", [])]


def asset_ids(report: dict):
    """Extrae ids de assets de asset_generation_report.json (estructura tolerante)."""
    if isinstance(report, dict):
        for key in ("assets", "generated_assets", "entries"):
            if key in report:
                items = report[key]
                out = []
                for it in items:
                    if isinstance(it, dict):
                        out.append(it.get("asset_id") or it.get("id") or it.get("name") or json.dumps(it)[:80])
                    else:
                        out.append(str(it))
                return out
        return [f"<top-level keys: {list(report.keys())}>"]
    return [str(report)]


def main():
    lines = []
    add = lines.append

    # ---- pain_ledger.json ----
    la = load(RUN_A / "pain_ledger.json")
    lc = load(RUN_C / "pain_ledger.json")
    ida, idc = pain_ids(la), pain_ids(lc)
    add("=" * 70)
    add("pain_ledger.json — pain_ids POR CORRIDA (en orden de ingesta)")
    add("=" * 70)
    add(f"RUN A ({RUN_A}): {len(ida)} pains")
    for i, p in enumerate(ida):
        add(f"  [{i}] {p}")
    add(f"RUN C ({RUN_C}): {len(idc)} pains")
    for i, p in enumerate(idc):
        add(f"  [{i}] {p}")
    add("")
    add(f"Solo en A: {sorted(set(ida) - set(idc))}")
    add(f"Solo en C: {sorted(set(idc) - set(ida))}")
    add(f"Comunes:   {sorted(set(ida) & set(idc))}")

    # Detalle de entradas exclusivas de A (severity/confidence/source)
    add("")
    add("Detalle entradas solo en A (pain_ledger):")
    for e in la.get("entries", []):
        if e["pain_id"] not in set(idc):
            add(f"  - {e['pain_id']}: severity={e.get('severity')} confidence={e.get('confidence')} "
                f"source_file={e.get('source_file')} source_module={e.get('source_module')} status={e.get('status')}")
    add("Detalle entradas solo en C (pain_ledger):")
    for e in lc.get("entries", []):
        if e["pain_id"] not in set(ida):
            add(f"  - {e['pain_id']}: severity={e.get('severity')} confidence={e.get('confidence')} "
                f"source_file={e.get('source_file')} source_module={e.get('source_module')} status={e.get('status')}")

    # ---- pain_ledger_resolved.json ----
    try:
        ra = load(RUN_A / "pain_ledger_resolved.json")
        rc = load(RUN_C / "pain_ledger_resolved.json")
        rid_a, rid_c = pain_ids(ra), pain_ids(rc)
        add("")
        add("=" * 70)
        add("pain_ledger_resolved.json — pain_ids POR CORRIDA")
        add("=" * 70)
        add(f"RUN A: {len(rid_a)} -> {rid_a}")
        add(f"RUN C: {len(rid_c)} -> {rid_c}")
        add(f"Solo en A (resolved): {sorted(set(rid_a) - set(rid_c))}")
        add(f"Solo en C (resolved): {sorted(set(rid_c) - set(rid_a))}")
        # status por pain
        add("")
        add("Status por pain (resolved) — A vs C:")
        sta = {e["pain_id"]: e.get("status") for e in ra.get("entries", [])}
        stc = {e["pain_id"]: e.get("status") for e in rc.get("entries", [])}
        for p in sorted(set(sta) | set(stc)):
            add(f"  {p}: A={sta.get(p, '<ausente>')} | C={stc.get(p, '<ausente>')}")
    except Exception as exc:  # noqa: BLE001
        add(f"[WARN] resolved: {exc}")

    # ---- asset_generation_report.json ----
    try:
        ga = load(RUN_A / "asset_generation_report.json")
        gc = load(RUN_C / "asset_generation_report.json")
        aid, cid = asset_ids(ga), asset_ids(gc)
        add("")
        add("=" * 70)
        add("asset_generation_report.json — assets POR CORRIDA")
        add("=" * 70)
        add(f"RUN A: {len(aid)}")
        for i, a in enumerate(aid):
            add(f"  [{i}] {a}")
        add(f"RUN C: {len(cid)}")
        for i, a in enumerate(cid):
            add(f"  [{i}] {a}")
    except Exception as exc:  # noqa: BLE001
        add(f"[WARN] asset report: {exc}")

    # ---- audit_report: scores de ia_readiness / robots en ambas corridas ----
    add("")
    add("=" * 70)
    add("audit_report: campos relevantes para la hipótesis (ia_readiness, robots, caches)")
    add("=" * 70)
    for tag, run in (("A", RUN_A), ("C", RUN_C)):
        audits = sorted(run.glob("audit_report_*.json"))
        add(f"RUN {tag}: {[p.name for p in audits]}")
        for ap in audits:
            rep = load(ap)
            keys = list(rep.keys()) if isinstance(rep, dict) else []
            add(f"  {ap.name}: top-keys={keys[:20]}")
            # busquedas puntuales
            def walk(obj, path=""):
                hits = []
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        kl = str(k).lower()
                        if any(s in kl for s in ("ia_readiness", "readiness_score", "robots", "ai_crawler")):
                            if not isinstance(v, (dict, list)):
                                hits.append(f"{path}.{k} = {v}")
                            else:
                                hits.append(f"{path}.{k} = <{type(v).__name__}>")
                        hits.extend(walk(v, f"{path}.{k}"))
                elif isinstance(obj, list):
                    for i, v in enumerate(obj[:5]):
                        hits.extend(walk(v, f"{path}[{i}]"))
                return hits
            for h in walk(rep):
                add(f"    {h}")

    text = "\n".join(lines)
    print(text)


if __name__ == "__main__":
    main()
