# Regresión FASE-A por chunks acotados (secuenciales, un proceso por lote).
# Cada pytest es un proceso chico que libera memoria al terminar → no satura la máquina.
$ErrorActionPreference = 'Continue'
$log = ".qoder/fase_a_chunks_result.txt"
$py  = "./venv/Scripts/python.exe"
Remove-Item $log -ErrorAction SilentlyContinue

$chunks = @(
  @{ id = "CHUNK1"; files = "tests/commercial_documents/test_diagnostic_brechas.py tests/commercial_documents/test_data_structures.py tests/commercial_documents/test_template_conditionals.py" },
  @{ id = "CHUNK2"; files = "tests/commercial_documents/test_proposal_generator.py tests/commercial_documents/test_pain_solution_mapper.py tests/commercial_documents/test_proposal_confidence_disclosure.py tests/commercial_documents/test_price_consistency.py" },
  @{ id = "CHUNK3"; files = "tests/commercial_documents/test_proposal_dynamic.py tests/commercial_documents/test_aeo_score.py tests/commercial_documents/test_iao_score.py tests/commercial_documents/test_proposal_generator_dict.py" },
  @{ id = "CHUNK4"; files = "tests/commercial_documents/test_diagnostic_generator.py tests/commercial_documents/test_hook_pdf_generator.py tests/commercial_documents/test_coherence_generated_assets.py tests/commercial_documents/test_proposal_fase4_h3_h4.py" },
  @{ id = "CHUNK5"; files = "tests/commercial_documents/test_precision_rendering.py tests/commercial_documents/test_financial_coherence.py tests/commercial_documents/test_fase_f_financial_placeholders.py" }
)

foreach ($c in $chunks) {
  Add-Content $log "===== $($c.id) START ====="
  $argList = "-m pytest " + $c.files + " -q -p no:cacheprovider --tb=line"
  & $py -m pytest @($c.files.Split(' ')) -q -p no:cacheprovider --tb=line 2>&1 | Add-Content $log
  Add-Content $log "===== $($c.id) END (exit=$LASTEXITCODE) ====="
}
Add-Content $log "ALL_CHUNKS_DONE"
