import sys, os
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    try: sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except: pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_agents_md import check_3_gate_count, check_2_test_count
from pathlib import Path
import tempfile, shutil

BASE = Path(__file__).resolve().parent.parent
results = []

# Test 1: gate_count drift detection
real_agents = BASE / "AGENTS.md"
tmpdir = Path(tempfile.mkdtemp())
tmp_agents = tmpdir / "AGENTS.md"
shutil.copy(real_agents, tmp_agents)

import validate_agents_md as vam
orig_agents = vam.AGENTS_MD
vam.AGENTS_MD = tmp_agents

orig_content = tmp_agents.read_text(encoding="utf-8")
result_correct = check_3_gate_count()

wrong_content = orig_content.replace("11 publication gates", "9 publication gates")
tmp_agents.write_text(wrong_content, encoding="utf-8")
result_wrong = check_3_gate_count()

vam.AGENTS_MD = orig_agents
shutil.rmtree(tmpdir)

test1_pass = result_correct.get("status") == "PASS" and result_wrong.get("status") == "FAIL"
results.append(("gate_drift_detection", test1_pass,
    "correct=%s, wrong=%s" % (result_correct.get("status"), result_wrong.get("status"))))

# Test 2: test_count tolerance with real data
result_real = check_2_test_count()
pct = result_real.get("pct_diff", 999)
test2_pass = result_real.get("status") == "PASS" and pct <= 5.0
results.append(("test_count_tolerance", test2_pass,
    "pct_diff=%s%%, count=%s, status=%s" % (pct, result_real.get("pytest_count"), result_real.get("status"))))

# Test 3: boundary math
pct_2600 = abs(2743-2600)/2743*100
pct_2610 = abs(2743-2610)/2743*100
test3_pass = (pct_2600 > 5.0) and (pct_2610 <= 5.0)
results.append(("tolerance_boundary_math", test3_pass,
    "2600->%.1f%% (expect >5%%), 2610->%.1f%% (expect <=5%%)" % (pct_2600, pct_2610)))

for name, passed, detail in results:
    print("%s: %s -- %s" % ("PASS" if passed else "FAIL", name, detail))

all_pass = all(r[1] for r in results)
print("\n%s/%s internal checks passed" % (sum(1 for r in results if r[1]), len(results)))
sys.exit(0 if all_pass else 1)
