# SKILL: Diagnostico Completo Hotel Visperas
# Ejecuta un analisis completo del Hotel Visperas mediante AgentHarness
# Actualizado: 21-Feb-2026
# Mejoras: v3.3.3 Deep Agentic Core, soporte bypass-harness, extraccion dinamica

[CmdletBinding()]
param(
    [switch]$ShowDetails,
    [switch]$OpenReports,
    [switch]$StagesOnly,        # Usa stage en vez de audit (más rápido)
    [switch]$UpdateCaseStudy,    # Actualiza CASO_ESTUDIO_VISPERAS.md con métricas
    [switch]$DebugMode,         # Activa modo debug en Python
    [switch]$BypassHarness      # Ejecuta en modo legacy (sin AgentHarness)
)

$projectRoot = "C:\Users\Jhond\Github\iah-cli"
$outputDir = ".\output\clientes"
$caseStudyPath = "$projectRoot\output\clientes_no_borrar\hotel_visperas\CASO_ESTUDIO.md"

# Forzar codificación UTF-8 para evitar errores con caracteres especiales en Windows
$env:PYTHONIOENCODING='utf-8'
[System.Environment]::SetEnvironmentVariable('PYTHONIOENCODING','utf-8','Process')

function Write-Header {
    param([string]$Title)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Write-Section {
    param([string]$Title, [string]$Color = "Yellow")
    Write-Host "`n$Title" -ForegroundColor $Color
    Write-Host ("-" * $Title.Length) -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Alert {
    param([string]$Message)
    Write-Host "[ALERT] $Message" -ForegroundColor Red
}

function Update-CaseStudy {
    param(
        [string]$JsonPath,
        [string]$OutputPath
    )
    
    Write-Section "Actualizando Caso de Estudio" "Cyan"
    
    if (-not (Test-Path $JsonPath)) {
        Write-Alert "No se encontró JSON de análisis en: $JsonPath"
        return $false
    }
    
    try {
        $data = Get-Content $JsonPath -Raw | ConvertFrom-Json
        $today = Get-Date -Format "dd-MMM-yyyy"
        
        # Extraer métricas del JSON
        $geoScore = if ($data.gbp_data.score) { $data.gbp_data.score } else { "N/A" }
        $aeoScore = if ($data.schema_data.score_schema -ne $null) { $data.schema_data.score_schema } else { 0 }
        $iaoScore = if ($data.ia_test.perplexity.menciones -ne $null) { $data.ia_test.perplexity.menciones } else { 0 }
        $seoScore = if ($data.seo_data.score) { $data.seo_data.score } else { "N/A" }
        $perdida = if ($data.llm_analysis.perdida_mensual_total) { $data.llm_analysis.perdida_mensual_total } else { "N/A" }
        $reviews = if ($data.gbp_data.reviews) { $data.gbp_data.reviews } else { "N/A" }
        
        Write-Host "  Fecha: $today" -ForegroundColor Gray
        Write-Host "  GEO: $geoScore | AEO: $aeoScore | IAO: $iaoScore | SEO: $seoScore" -ForegroundColor Gray
        Write-Host "  Pérdida mensual: $perdida" -ForegroundColor Gray
        
        # Leer caso de estudio actual
        $content = Get-Content $caseStudyPath -Raw -Encoding UTF8
        
        # Actualizar fecha de última actualización
        $content = $content -replace "(\*\*Última actualización:\*\*) \d+-\w+-\d+", "`$1 $today"
        
        # Añadir nueva fila a tabla de evolución histórica
        $newRow = "| $today | `$$perdida | $($geoScore)/100 | $($aeoScore)/100 | $($iaoScore)/100 | $($seoScore)/100 | Actualización dinámica v3.3.2 |"
        
        if ($content -match "(\| \d+-\w+-\d+ \|[^\r\n]+)") {
            $lastRow = $Matches[1]
            $content = $content -replace [regex]::Escape($lastRow), "$lastRow`n$newRow"
            Write-Success "Tabla de evolución actualizada"
        }
        
        # Guardar cambios
        $content | Set-Content $caseStudyPath -Encoding UTF8
        Write-Success "Caso de estudio actualizado: $caseStudyPath"
        return $true
        
    } catch {
        Write-Alert "Error actualizando caso de estudio: $_"
        return $false
    }
}

# Inicio
Write-Header "SKILL: DIAGNOSTICO COMPLETO HOTEL VISPERAS"

Write-Host "Iniciando secuencia de diagnostico..." -ForegroundColor White
Write-Host "Fecha: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')" -ForegroundColor Gray
Write-Host "Proyecto: IA Hoteles Agent CLI`n" -ForegroundColor Gray

Set-Location $projectRoot

# FASE 1: Ejecución
Write-Header "EJECUTANDO ANALISIS MOTOR PYTHON"

if ($StagesOnly) {
    Write-Host "Modo: STAGE (geo + ia + seo)" -ForegroundColor Yellow
    python main.py stage --url "https://hotelvisperas.com" --stages geo ia seo --output "./output/clientes"
} else {
    $debugFlag = if ($DebugMode) { "--debug" } else { "" }
    $bypassFlag = if ($BypassHarness) { "--bypass-harness" } else { "" }
    python main.py audit --url "https://hotelvisperas.com" --output "./output/clientes" $debugFlag $bypassFlag
}

$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    Write-Alert "El análisis de Python falló con código: $exitCode"
    exit $exitCode
}

# Capturar directorio generado
$reportDir = Get-ChildItem -Path $outputDir -Directory | Where-Object {$_.Name -match "hotel_visperas"} | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# FASE 2: Análisis Dinámico de Resultados
Write-Header "HALLAZGOS REALES DETECTADOS"

$jsonPath = ""
if ($reportDir) {
    $jsonPath = Join-Path $reportDir.FullName "evidencias\raw_data\analisis_completo.json"
    if (-not (Test-Path $jsonPath)) {
        $jsonPath = Join-Path $reportDir.FullName "analisis_completo.json"
    }
}

if ($jsonPath -and (Test-Path $jsonPath)) {
    try {
        $data = Get-Content $jsonPath -Raw | ConvertFrom-Json
        
        Write-Section "Información General" "Cyan"
        Write-Host "Nombre: $($data.hotel_data.nombre)" -ForegroundColor White
        Write-Host "Ubicación: $($data.hotel_data.ubicacion)" -ForegroundColor White
        Write-Host "Habitaciones: $($data.hotel_data.habitaciones)" -ForegroundColor White
        $precioFormat = if ($data.hotel_data.precio_promedio) { "$($data.hotel_data.precio_promedio.ToString('N0')) COP" } else { "N/D" }
        Write-Host "Precio Promedio: $precioFormat" -ForegroundColor White
        Write-Host "Rating GBP: $($data.gbp_data.rating)/5.0" -ForegroundColor Green
        Write-Host "Reviews: $($data.gbp_data.reviews)" -ForegroundColor White
        Write-Host "Confianza de Datos: $($data.hotel_data.confidence.ToUpper())" -ForegroundColor Cyan

        Write-Header "MÉTRICAS Y BRECHAS"
        
        Write-Section "Brecha Financiera" "Red"
        $perdidaMensual = if ($data.llm_analysis.perdida_mensual_total) { $data.llm_analysis.perdida_mensual_total } else { 0 }
        Write-Host "Pérdida Mensual Estimada: " -ForegroundColor White -NoNewline
        Write-Host "$($perdidaMensual.ToString('N0')) COP" -ForegroundColor Red
        
        Write-Section "Scores por Pilar" "Yellow"
        Write-Host "GEO (Google Maps): $($data.gbp_data.score)/100" -ForegroundColor Gray
        Write-Host "AEO (Schema IA): $($data.schema_data.score_schema)/100" -ForegroundColor Red
        $webColor = if ($data.seo_data.score -ge 70) {"Green"} else {"Red"}
        Write-Host "Web Credibility: $($data.seo_data.score)/100" -ForegroundColor $webColor

        Write-Section "Top Brechas Detectadas" "Red"
        foreach ($brecha in $data.llm_analysis.brechas_criticas) {
            Write-Host "- $($brecha.nombre)" -ForegroundColor Red
            Write-Host "  $($brecha.descripcion)" -ForegroundColor Gray
        }

        Write-Header "PROPUESTA Y ROI"
        Write-Section "Paquete Recomendado: $($data.llm_analysis.paquete_recomendado)" "Cyan"
        Write-Host "Razón: $($data.llm_analysis.justificacion_paquete)" -ForegroundColor Gray
        $invMensual = if ($data.roi_data.inversion_mensual) { $data.roi_data.inversion_mensual } else { 0 }
        Write-Host "Inversión Mensual: $($invMensual.ToString('N0')) COP" -ForegroundColor Yellow
        Write-Host "ROI Proyectado: $($data.roi_data.totales_6_meses.roas)X en 6 meses" -ForegroundColor Green
        Write-Host "Recuperación de Inversión: $($data.roi_data.mes_recuperacion)`n" -ForegroundColor Green

    } catch {
        Write-Alert "Error parseando datos dinámicos: $_"
    }
} else {
    Write-Alert "No se pudieron cargar datos reales para el resumen final."
}

# FASE 4: Reportes
Write-Header "REPORTES GENERADOS"

if ($reportDir) {
    $reportPath = $reportDir.FullName
    Write-Section "Ubicación: $reportPath" "Green"
    
    Get-ChildItem -Path $reportPath -Filter "*.md" | ForEach-Object {
        Write-Success "$($_.Name) ($($_.Length) bytes)"
    }
}

# FASE 7: Finalización
Write-Header "DIAGNOSTICO FINALIZADO EXITOSAMENTE"
Write-Host "Fecha: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')" -ForegroundColor Gray
Write-Host "Generado por: IA Hoteles Agent - v3.3.3 (Agentic) `n" -ForegroundColor Gray

if ($OpenReports -and $reportDir) {
    Invoke-Item $reportDir.FullName
}

if ($UpdateCaseStudy -and $reportDir) {
    $jsonPath = Join-Path $reportDir.FullName "evidencias\raw_data\analisis_completo.json"
    if (-not (Test-Path $jsonPath)) { $jsonPath = Join-Path $reportDir.FullName "analisis_completo.json" }
    $relativePath = $reportDir.FullName -replace [regex]::Escape($projectRoot), "."
    Update-CaseStudy -JsonPath $jsonPath -OutputPath $relativePath
}
