"""Smoke test for ROICRIII FASE-1 — imports + template verification."""
import sys
sys.path.insert(0, r'C:\Users\Jhond\Github\iah-cli')

from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
print('v4_proposal_generator.py: OK')

from modules.financial_engine.pillar_maturity_curve import aplicar_curva_4_pilares, PillarMaturityResult
print('pillar_maturity_curve.py: OK')

import pathlib
template_path = pathlib.Path(r'C:\Users\Jhond\Github\iah-cli\modules\commercial_documents\templates\propuesta_v6_template.md')
content = template_path.read_text(encoding='utf-8')

assert 'Total 6 meses' not in content, 'FAIL: "Total 6 meses" still in template!'
assert '${total_recovered}' not in content, 'FAIL: ${total_recovered} still in template!'
assert '${roi_6m}' not in content, 'FAIL: ${roi_6m} still in template!'
print('propuesta_v6_template.md: OK (no redundant bullets)')

print('ALL SMOKE TESTS PASSED')
