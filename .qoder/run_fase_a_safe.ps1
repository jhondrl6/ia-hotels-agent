# Runner seguro de regresion para FASE-A (y reutilizable en futuras fases).
# Cada chunk corre como UN proceso pytest hijo, monitoreado por un vigilante:
#   - Si el proceso supera RamLimitMB  -> se mata y se registra KILLED_RAM.
#   - Si supera TimeoutSec             -> se mata y se registra KILLED_TIMEOUT.
# Asi ningun test con fuga de memoria o cuelgue puede bloquear el equipo.
param(
    [int]$RamLimitMB = 1500,
    [int]$TimeoutSec = 240
)

$ErrorActionPreference = 'Continue'
$root  = Split-Path -Parent $PSScriptRoot          # .../iah-cli
$py    = Join-Path $root "venv\Scripts\python.exe"
$sumLog = Join-Path $PSScriptRoot "fase_a_safe_summary.txt"
Remove-Item $sumLog -ErrorAction SilentlyContinue
$workDir = Join-Path $PSScriptRoot "chunk_out"
New-Item -ItemType Directory -Force -Path $workDir | Out-Null

# Chunks del modulo afectado (commercial_documents), EXCLUYENDO test_proposal_generator.py
# (fuga de RAM preexistente, se aisla aparte). Se añade data_validation como chunk final.
$chunks = @(
  @{ id="CHUNK2"; files=@("tests/commercial_documents/test_pain_solution_mapper.py","tests/commercial_documents/test_proposal_confidence_disclosure.py","tests/commercial_documents/test_price_consistency.py") },
  @{ id="CHUNK3"; files=@("tests/commercial_documents/test_proposal_dynamic.py","tests/commercial_documents/test_aeo_score.py","tests/commercial_documents/test_iao_score.py","tests/commercial_documents/test_proposal_generator_dict.py") },
  @{ id="CHUNK4"; files=@("tests/commercial_documents/test_diagnostic_generator.py","tests/commercial_documents/test_hook_pdf_generator.py","tests/commercial_documents/test_coherence_generated_assets.py","tests/commercial_documents/test_proposal_fase4_h3_h4.py") },
  @{ id="CHUNK5"; files=@("tests/commercial_documents/test_precision_rendering.py","tests/commercial_documents/test_financial_coherence.py","tests/commercial_documents/test_fase_f_financial_placeholders.py") },
  @{ id="CHUNK6_DATAVAL"; files=@("tests/data_validation") }
)

function Run-ChunkWatched {
    param([string]$id, [string[]]$files)
    $outFile = Join-Path $workDir "$id.out"
    $errFile = Join-Path $workDir "$id.err"
    $argList = @("-m","pytest") + $files + @("-q","-p","no:cacheprovider","--tb=line")
    $proc = Start-Process -FilePath $py -ArgumentList $argList -WorkingDirectory $root `
            -PassThru -NoNewWindow -RedirectStandardOutput $outFile -RedirectStandardError $errFile
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $killReason = $null
    while (-not $proc.HasExited) {
        Start-Sleep -Seconds 2
        try { $proc.Refresh() } catch {}
        $ramMB = [int]($proc.WorkingSet64 / 1MB)
        if ($ramMB -gt $RamLimitMB) { $killReason = "KILLED_RAM(${ramMB}MB > ${RamLimitMB}MB)"; break }
        if ($sw.Elapsed.TotalSeconds -gt $TimeoutSec) { $killReason = "KILLED_TIMEOUT(${TimeoutSec}s)"; break }
    }
    if ($killReason) {
        try { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue } catch {}
        Add-Content $sumLog "$id : $killReason"
        return $killReason
    } else {
        $proc.WaitForExit()
        $tail = (Get-Content $outFile -Tail 1 -ErrorAction SilentlyContinue)
        Add-Content $sumLog "$id : exit=$($proc.ExitCode) | $tail"
        return "OK"
    }
}

foreach ($c in $chunks) {
    Run-ChunkWatched -id $c.id -files $c.files | Out-Null
}
Add-Content $sumLog "ALL_CHUNKS_DONE"
