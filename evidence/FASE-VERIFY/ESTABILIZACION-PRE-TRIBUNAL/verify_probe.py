import json, os, zipfile, sys

BASE = "evidence/FASE-I/corrida"
AUD = os.path.join(BASE, "hotelsalentoreal", "v4_audit")
out = []

def j(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def show(title, obj):
    out.append("== " + title + " ==")
    out.append(json.dumps(obj, ensure_ascii=False, indent=1)[:4000])

# 1. matriz de propuesta (AC5)
m = j(os.path.join(AUD, "proposal_asset_matrix.json"))
statuses = {}
for e in m.get("entries", m.get("matrix", [])):
    st = e.get("status") or e.get("alignment_status")
    statuses[st] = statuses.get(st, 0) + 1
show("MATRIZ keys", list(m.keys()))
show("MATRIZ statuses", statuses)
show("MATRIZ summary", m.get("summary"))
show("MATRIZ coverage_ratio", m.get("coverage_ratio"))
out.append("NO_BREACH count = %d" % statuses.get("NO_BREACH", 0))

# 2. coherencia (AC6)
for fn in ("coherence_validation.json", "coherence_validation_post_gen.json", "asset_generation_report.json"):
    c = j(os.path.join(AUD, fn))
    keys = {k: c[k] for k in c if "coher" in k.lower() or k in ("overall_score", "coverage_ratio", "unresolved")}
    show("COHER " + fn, keys)
    checks = c.get("checks") or c.get("validation_checks") or {}
    if isinstance(checks, dict) and "assets_are_justified" in checks:
        show("  assets_are_justified " + fn, checks["assets_are_justified"])
    for k in ("details", "results"):
        v = c.get(k)
        if isinstance(v, dict) and "assets_are_justified" in v:
            show("  assets_are_justified(" + k + ") " + fn, v["assets_are_justified"])

# 3. gate report (AC7 / NR9 / NR2 / NR1 / AC10)
gr = [f for f in os.listdir(AUD) if f.startswith("gate_report_")]
g = j(os.path.join(AUD, gr[0]))
res = g.get("gate_results") or g.get("gates") or []
out.append("== GATE REPORT %s: %d results ==" % (gr[0], len(res)))
for r in res:
    out.append("  %-32s passed=%-5s status=%-14s value=%s details_keys=%s" % (
        r.get("gate_name"), r.get("passed"), r.get("status"), r.get("value"),
        sorted((r.get("details") or {}).keys())))
out.append("  severity key present in any gate: %s" % any("severity" in r for r in res))
out.append("  blocking key present in any gate: %s" % any("blocking" in r for r in res))
show("GATE summary", g.get("summary"))
show("GATE top-level keys", list(g.keys()))
for r in res:
    if r.get("gate_name") in ("proposal_asset_alignment", "critical_recall", "doc_audit_consistency", "coverage_no_silent_drop", "coherence"):
        show("GATE " + r["gate_name"], r)

# 4. delivery quality report (AC11 / AC9-A6)
d = j(os.path.join(AUD, "delivery_quality_report.json"))
show("DELIVERY summary", d.get("summary"))
dq = json.dumps(d, ensure_ascii=False)
out.append("NOT_EVALUATED occurrences in delivery report: %d" % dq.count("NOT_EVALUATED"))
out.append("asset_path occurrences / non-null: %d / %d" % (dq.count('"asset_path"'), dq.count('"asset_path": null') * 0 + dq.count('"asset_path"')))
ap = []
def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("asset_path", "path"):
                ap.append((path + "/" + k, v))
            walk(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + "/%d" % i)
walk(d)
show("DELIVERY asset_path/path", ap[:30])

# 5. snapshot A2 (AC9)
sp = os.path.join(AUD, "site_presence_snapshot.json")
out.append("== snapshot exists=%s size=%d ==" % (os.path.exists(sp), os.path.getsize(sp) if os.path.exists(sp) else -1))
if os.path.exists(sp):
    s = j(sp)
    show("SNAPSHOT keys", list(s.keys()))
    inner = s.get("snapshot", {})
    show("SNAPSHOT summary", {k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in inner.items()})

# 6. human_checklist (AC8)
hc = open(os.path.join(AUD, "human_checklist.md"), encoding="utf-8").read()
out.append("== HUMAN CHECKLIST (%d chars) ==" % len(hc))
out.append(hc)

# 7. ledger (AC4/AC5 contexto)
pl = j(os.path.join(AUD, "pain_ledger.json"))
plr = j(os.path.join(AUD, "pain_ledger_resolved.json"))
def ids(o):
    if isinstance(o, dict):
        for k in ("pains", "entries", "items"):
            if k in o and isinstance(o[k], list):
                return [e.get("pain_id") or e.get("id") for e in o[k]]
    return None
show("LEDGER ids", {"raw": ids(pl), "resolved": ids(plr)})
show("LEDGER resolved summary", plr.get("summary") if isinstance(plr, dict) else None)

# 8. ZIP (NR10/AC12)
z = os.path.join(BASE, "deliveries", "hotelsalentoreal_20260904.zip")
zf = zipfile.ZipFile(z)
names = zf.namelist()
out.append("== ZIP %d files, size %d ==" % (len(names), os.path.getsize(z)))
out.append("  snapshot in zip: %s" % [n for n in names if "site_presence" in n])
cohs = []
for n in names:
    if n.endswith(".json"):
        try:
            dd = json.loads(zf.read(n).decode("utf-8"))
        except Exception:
            continue
        s = json.dumps(dd)
        if '"is_coherent"' in s:
            import re
            cohs.append((n, sorted(set(re.findall(r'"is_coherent":\s*(true|false|null)', s)))))
show("ZIP is_coherent", cohs)

# 9. v4_complete_report
v = j(os.path.join(BASE, "v4_complete_report.json"))
show("V4REPORT keys", list(v.keys()))
ag = v.get("assets_generated") or []
show("V4REPORT assets path keys", [{k: a.get(k) for k in ("asset_type", "path", "filename", "asset_path")} for a in ag])
for k in ("publication_state", "ready_for_publication", "coherence", "gates"):
    if k in v:
        show("V4REPORT " + k, v[k])

# 10. copias is_coherent en disco (fuera del zip)
import re
disc = []
for root, dirs, files in os.walk(BASE):
    for f in files:
        if f.endswith(".json"):
            p = os.path.join(root, f)
            txt = open(p, encoding="utf-8").read()
            if '"is_coherent"' in txt:
                disc.append((p.replace("\\", "/"), sorted(set(re.findall(r'"is_coherent":\s*(true|false|null)', txt)))))
show("DISK is_coherent", disc)

sys.stdout.reconfigure(encoding="utf-8")
print("\n".join(out))
