import json, os, re, sys

sys.path.insert(0, os.getcwd())
out = []
def p(*a):
    out.append(" ".join(str(x) for x in a))

from modules.common.service_identity import SERVICE_IDENTITIES
from modules.quality_gates import publication_gates as pg
from modules.quality_gates.coherence_gate import coherence_verdict_passes
from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper
from modules.quality_gates.delivery_quality_report import DeliveryQualityReportGenerator

p("AC1 SERVICE_IDENTITIES =", len(SERVICE_IDENTITIES),
  "| pain_ids:", sorted({i.pain_id for i in SERVICE_IDENTITIES}))
p("AC3 monthly_report -> pain_id canónico:",
  [i.pain_id for i in SERVICE_IDENTITIES if i.asset_type == "monthly_report"])
p("AC4 Capa1 pain_ids =", len(PainSolutionMapper.PAIN_SOLUTION_MAP))

phantom = ["no_speakable", "no_llms_txt", "ia_crawler_blocked", "weak_brand_signals", "no_entity_schema", "no_factual_data"]
for d in ("modules/commercial_documents", "modules/asset_generation"):
    for pid in phantom:
        hits = []
        for root, dirs, files in os.walk(d):
            for f in files:
                if f.endswith(".py"):
                    fp = os.path.join(root, f)
                    t = open(fp, encoding="utf-8", errors="replace").read()
                    for m in re.finditer(r'["\']%s["\']' % re.escape(pid), t):
                        hits.append("%s:%d" % (fp, t[:m.start()].count("\n") + 1))
        p("AC1 ghost %-22s %-30s -> %d %s" % (pid, d, len(hits), hits[:4]))

pat = re.compile(r"\b\d+\s+servic", re.IGNORECASE)
for root, dirs, files in os.walk("modules"):
    for f in sorted(files):
        if f.endswith(".py"):
            fp = os.path.join(root, f).replace("\\", "/")
            t = open(fp, encoding="utf-8", errors="replace").read()
            hits = [(i + 1, l.strip()[:110]) for i, l in enumerate(t.splitlines()) if pat.search(l)]
            if hits:
                p("AC2 numeral-servicios %s -> %d :: %s" % (fp, len(hits), hits[:5]))

p("AC7 BLOCKING =", len(pg.BLOCKING_GATE_NAMES), "ADVISORY =", len(pg.ADVISORY_GATE_NAMES), sorted(pg.ADVISORY_GATE_NAMES))
p("AC7 asset_confidence blocking:", "asset_confidence" in pg.BLOCKING_GATE_NAMES,
  "| disjuntas:", not (set(pg.BLOCKING_GATE_NAMES) & set(pg.ADVISORY_GATE_NAMES)),
  "| suma:", len(pg.BLOCKING_GATE_NAMES) + len(pg.ADVISORY_GATE_NAMES))
src = open("modules/quality_gates/publication_gates.py", encoding="utf-8").read().splitlines()
for i, l in enumerate(src, 1):
    if re.search(r"(10|11|13)\s*(blocking|gates)|\d+\s*advisory", l, re.I):
        p("AC7/AC8 cite :%d %s" % (i, l.strip()[:170]))
o = pg.PublicationGatesOrchestrator.__new__(pg.PublicationGatesOrchestrator)
class R:
    def __init__(self, n, passed, status):
        self.gate_name, self.passed, self.status = n, bool(passed), status
        self.details = {}
        self.message = ""
        self.value = None
        self.status = status
res = [R(n, True, "PASSED") for n in pg.BLOCKING_GATE_NAMES] + [R(n, False, "FAILED") for n in pg.ADVISORY_GATE_NAMES]
p("AC7 get_blocking_gates() ->", len(o.get_blocking_gates(res)), sorted(g.gate_name for g in o.get_blocking_gates(res)))
ag = open("AGENTS.md", encoding="utf-8").read()
p("AC8 AGENTS.md 'blocking (11)':", "blocking (11)" in ag, "| 'advisory (2)':", "advisory (2)" in ag,
  "| '10 blocking':", "10 blocking" in ag, "| '3 advisory':", "3 advisory" in ag)

p("AC12 verdict(0.88/0.8/False):", coherence_verdict_passes(0.88, 0.8, False),
  "(True):", coherence_verdict_passes(0.88, 0.8, True), "(None):", coherence_verdict_passes(0.88, 0.8, None))
p("AC12/F publicacion_state existe:", os.path.exists("modules/quality_gates/publication_state.py"))

v4 = "evidence/FASE-I/corrida/hotelsalentoreal/v4_audit"
m = json.load(open(os.path.join(v4, "proposal_asset_matrix.json"), encoding="utf-8"))
for e in m["entries"]:
    p("AC9 entry %-32s %-22s asset_path=%r" % (e.get("service"), e.get("status") or e.get("alignment_status"), e.get("asset_path")))
p("AC9 not_promised:", m.get("not_promised"), "| unknown:", m.get("unknown_services"))
d = json.load(open(os.path.join(v4, "delivery_quality_report.json"), encoding="utf-8"))
p("AC11 delivery keys:", list(d.keys()))
p("AC11 delivery gates:", json.dumps(d.get("gates", d.get("gate_results")), ensure_ascii=False)[:1200])
p("AC11 human_review_items:", d.get("human_review_items"))
p("AC11 readiness:", json.dumps(d.get("readiness"), ensure_ascii=False)[:400])

g = json.load(open(os.path.join(v4, [f for f in os.listdir(v4) if f.startswith("gate_report_")][0]), encoding="utf-8"))
p("NR9 readiness del gate_report:", json.dumps(g.get("readiness"), ensure_ascii=False)[:900])
p("NR2 audit critical_issues:", json.dumps(json.load(open(os.path.join(v4, [f for f in os.listdir(v4) if f.startswith("audit_report_")][0]), encoding="utf-8")).get("overall", {}).get("critical_issues"), ensure_ascii=False)[:800])

# AC11 conductual: G9 sin matriz (estado post-F) — reproduce el caso del test rojo de tests/delivery
import tempfile, pathlib
tmp = pathlib.Path(tempfile.mkdtemp()) / "v4_audit"
tmp.mkdir()
(tmp / "coherence_validation.json").write_text(json.dumps({"overall_score": 0.85}), encoding="utf-8")
(tmp / "asset_generation_report.json").write_text(json.dumps({"total_assets": 2, "preflight_results": []}), encoding="utf-8")
rep = DeliveryQualityReportGenerator().generate("probe", tmp)
p("AC11 G9 sin matriz ->", json.dumps(rep.proposal_asset_gate, ensure_ascii=False))
p("AC11 summary ->", json.dumps(rep.summary if isinstance(rep.summary, dict) else rep.summary.__dict__, ensure_ascii=False, default=str)[:600])

sys.stdout.reconfigure(encoding="utf-8")
print("\n".join(out))
