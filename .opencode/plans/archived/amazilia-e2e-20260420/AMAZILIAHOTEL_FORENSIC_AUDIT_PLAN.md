# PLAN: Validación E2E v4complete — Amaziliahotel Post-Refactor

**Proyecto**: AMAZILIAHOTEL_REFACTOR (FASE-1 a FASE-6 completadas)
**Fecha plan**: 2026-04-20
**Objetivo**: Ejecutar v4complete y validar si las fases resolvieron los GAPs pre-existentes **Y detectar GAPs nuevos** introducidos por el proceso de refactorización (FASE-1 a FASE-6) o por la nueva ejecución v4complete, incluyendo desconexiones entre diagnóstico ↔ propuesta ↔ assets y brechas de coherencia no documentadas previamente.
**Score objetivo**: >= 80/100 (desde 16/100 pre-refactor)
**Commit base**: `cdd9991` (docs(AMAZILIAHOTEL): completar checklist E1-E8 post-proyecto)

---

## CONTEXTO: Qué se ejecutó y qué GAPs existían

### Fases completadas (06-checklist-implementacion.md)

| # | Fase | Estado | Resultado esperado |
|---|------|--------|-------------------|
| 1 | FASE-1: BookingScraper Real | ✅ | Scraping real + fallback GBP |
| 2 | FASE-2A: hotel_schema real | ✅ | Schema con datos reales GBP |
| 2 | FASE-2B: monthly_report real | ✅ | Reporte con datos reales |
| 2 | FASE-2C: optimization_guide | ✅ | Sin contradicciones title tag |
| 3 | FASE-3: Bugs generadores | ✅ | H3/H4/H10/H12 corregidos |
| 4 | FASE-4: Open Graph | ✅ | B4 cerrado ($379K/mes) |
| 5 | FASE-5: Decisiones + Gates | ✅ | WhatsApp/Voice eliminados |
| 6 | FASE-6: Docs comerciales | ✅ | ROI 3X Tier C, 105/105 tests |

### GAPs pre-existentes (del plan original v1)

| # | Gap | Severidad | Corrección aplicada |
|---|-----|-----------|---------------------|
| G1 | research.json VACIO (confidence 0.0) | CRITICO | BookingScraper real (FASE-1) |
| G2 | hotel_schema GENERICO (sin datos reales) | CRITICO | Regenerado con GBP (FASE-2A) |
| G3 | B4 Open Graph NO existía | CRITICO | open_graph_generator.py (FASE-4) |
| G4 | faq_page extensión .csv (era JSON-LD) | ALTO | Bug H3 corregido (FASE-3) |
| G5 | llms.txt DUPLICADO en 2 carpetas | ALTO | Consolidado en geo_enriched/ (FASE-3) |
| G6 | optimization_guide contradicción title tag | ALTO | H12 corregido (FASE-2C) |
| G7 | monthly_report PLANTILLA VACIA | ALTO | Regenerado con datos reales (FASE-2B) |
| G8 | WhatsApp NO tiene brecha (promised_by=always) | ALTO | ELIMINADO en FASE-5 |
| G9 | Voice NO tiene brecha (promised_by=always_aeo) | ALTO | ELIMINADO pipeline en FASE-5 |
| G10 | ROI 20X inflado (Tier C) | ALTO | ROI 3X Tier C en FASE-6 |
| G11 | Coherence duplicada (0.89 vs 0.86) | MEDIO | Unificado en FASE-3 (H10) |
| G12 | Paths Windows en reports | MEDIO | H12 corregido (FASE-3) |
| G13 | "eje_cafetero" variable sin interpolar | MEDIO | Corregido en docs (FASE-6) |
| G14 | "COP COP" duplicado | MEDIO | Corregido en docs (FASE-6) |

### Documentación de soporte

- `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260415_113914.md` (pre-refactor)
- `output/v4_complete/02_PROPUESTA_COMERCIAL_20260415_113915.md` (post-FASE-6, corregido)
- `output/v4_complete/amaziliahotel/` (assets generados pre-refactor)
- `docs/GUIA_TECNICA.md` (notas FASE-3 a FASE-6)
- `CHANGELOG.md` (entradas AMAZILIAHOTEL-REFACTOR)

---

## FASE 0: Precondiciones (sin costo API)

### 0.1 Validación de sintaxis módulos modificados

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

./venv/Scripts/python.exe -m py_compile modules/scrapers/booking_scraper.py
./venv/Scripts/python.exe -m py_compile modules/asset_generation/open_graph_generator.py
./venv/Scripts/python.exe -m py_compile modules/asset_generation/asset_catalog.py
./venv/Scripts/python.exe -m py_compile modules/asset_generation/conditional_generator.py
./venv/Scripts/python.exe -m py_compile modules/asset_generation/faq_generator.py
./venv/Scripts/python.exe -m py_compile modules/asset_generation/llmstxt_generator.py
./venv/Scripts/python.exe -m py_compile modules/financial_engine/calculator_v2.py
./venv/Scripts/python.exe -m py_compile modules/orchestration_v4/two_phase_orchestrator.py

# Esperado: 0 errores para todos
```

### 0.2 Tests de regresión

```bash
# Suite completa — 0 fallos requeridos
./venv/Scripts/python.exe -m pytest tests/ -x -q 2>&1 | tail -5

# Suite específica AMAZILIAHOTEL (FASE-3 a FASE-6)
./venv/Scripts/python.exe -m pytest tests/ -k "amazilia or faq or coherence or open_graph" -v 2>&1 | tail -10
```

### 0.3 Validaciones globales

```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/doctor.py --status
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

### 0.4 Sincronizacion AGENTS.md

```bash
# Verificar que AGENTS.md refleja la realidad del codebase
TEST_COUNT=$(./venv/Scripts/python.exe -m pytest tests/ --co -q 2>&1 | tail -1 | grep -oE '[0-9]+')
AGENTS_COUNT=$(grep -oE '[0-9]+ tests' AGENTS.md | head -1 | grep -oE '[0-9]+')
echo "Tests reales: $TEST_COUNT | AGENTS.md dice: $AGENTS_COUNT"

if [ "$TEST_COUNT" != "$AGENTS_COUNT" ]; then
    echo "ADVERTENCIA: AGENTS.md desactualizado. Actualizar antes de ejecutar."
fi
```

### Criterio de avance: 0 errores en FASE-0 → Proceder a FASE-1

---

## FASE 1: Ejecución controlada v4complete (UNICA, costo API)

**RESTRICCIÓN**: Esta es la UNICA ejecución de v4complete en el plan.
No ejecutar v4complete en ninguna otra fase.

### 1.1 Setup de evidencia

```bash
mkdir -p evidence/amazilia-e2e-20260420
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
```

### 1.2 Ejecución v4complete

```bash
./venv/Scripts/python.exe main.py v4complete \
    --url https://amaziliahotel.com/ \
    --debug \
    2>&1 | tee evidence/amazilia-e2e-20260420/ejecucion_${TIMESTAMP}.log

EXIT_CODE=$?
echo "Exit code: $EXIT_CODE" >> evidence/amazilia-e2e-20260420/ejecucion_${TIMESTAMP}.log
```

### 1.3 Captura de output

```bash
# Identificar archivos generados
ls -lt output/v4_complete/*.md output/v4_complete/amaziliahotel/ 2>/dev/null

# Listar diagnostico y propuesta generados
DIAGNOSTICO=$(ls -t output/v4_complete/01_DIAGNOSTICO*.md 2>/dev/null | head -1)
PROPUESTA=$(ls -t output/v4_complete/02_PROPUESTA*.md 2>/dev/null | head -1)

echo "Diagnostico: $DIAGNOSTICO"
echo "Propuesta: $PROPUESTA"
```

### Criterio de avance: v4complete termina con exit code 0 → Proceder a FASE-2

---

## FASE 2: Análisis de Coherencia Diagnóstico ↔ Propuesta ↔ Assets

### 2.1 Tri-Play: Diagnóstico → Propuesta → Assets

**Regla**: `VALIDO = (Brecha en Diagnostico) AND (Servicio en Propuesta) AND (Asset con datos reales) AND (Promesa medible)`

#### 2.1.1 Validar brechas del diagnóstico vs servicios de la propuesta

```bash
# Extraer brechas del diagnostico generado
grep -E "BRECHA|\[BRECHA" "$DIAGNOSTICO" | head -10

# Extraer servicios de la propuesta
grep -E "Servicio|Google Maps|ChatGPT|SEO|Datos Estructurados|Informe" "$PROPUESTA" | head -20
```

**Checklist** (cada brecha debe tener servicio, cada servicio debe tener brecha):

| Brecha en Diagnóstico | Servicio en Propuesta | Estado |
|----------------------|----------------------|--------|
| B1: Sin Schema Hotel | Datos Estructurados | ? |
| B2: Sin FAQ Rich Snippets | Datos Estructurados | ? |
| B3: Metadatos por Defecto | SEO Local | ? |
| B4: Sin Open Graph | Open Graph / meta tags | ? |

#### 2.1.2 Validar coherencia financiera

```bash
# Extraer Tier del diagnostico
grep -E "Tier|financial_evidence_tier" "$DIAGNOSTICO"

# Extraer ROI de la propuesta
grep -E "ROI|3X|20X|Tier C" "$PROPUESTA"

# Validar: ROI 3X para Tier C, 20X SOLO con GA4 mencionado
```

**Checks requeridos**:
- [ ] Propuesta menciona "Tier C" o "datos limitados"
- [ ] ROI base es 3X (no 20X)
- [ ] 20X aparece SOLO como potencial con GA4
- [ ] Escenario optimista (-$189K) no aparece como garantizado

#### 2.1.3 Validar servicios ELIMINADOS (FASE-5)

```bash
# WhatsApp NO debe aparecer como servicio vendible
grep -i "whatsapp" "$PROPUESTA" | grep -v "contacto\|WhatsApp:"
# Esperado: 0 matches o solo en sección contacto

# Voice NO debe aparecer como servicio
grep -i "voz\|voice\|alexa\|google assistant" "$PROPUESTA" | grep -v "IAO\|Inteligencia"
# Esperado: 0 matches como servicio

# Informe Mensual DEBE aparecer como "Incluido" (no fix de brecha)
grep -i "informe mensual" "$PROPUESTA"
# Esperado: en sección "Servicios Incluidos"
```

### 2.2 Matriz de Fidelidad Diagnóstico → Propuesta

| Afirmación en Propuesta | Dato en Diagnóstico | Veredicto |
|------------------------|---------------------|-----------|
| "$2.610.000 COP/mes" | financial_value_central: 2.610.000 | ? |
| "No aparece en ChatGPT" | AEO 0/100 | ? |
| "Aparece último en Maps" | GBP 62/100 vs 89/100 regional | ? |
| ROI 3X (Tier C) | Tier C, GA4 no configurado | ? |
| Servicios alineados B1-B4 | 4 brechas cuantificadas | ? |

### Criterio de avance: <= 1 inconsistencia tolerable → Proceder a FASE-3

---

## FASE 3: Auditoría de Assets Post-Ejecución

### 3.1 Assets generados — verificar estado (ESTIMATED vs REAL)

```bash
# Listar todos los assets
find output/v4_complete/amaziliahotel -maxdepth 2 -type f \( -name "*.json" -o -name "*.md" -o -name "*.html" -o -name "*.txt" \) | sort

# Clasificar por prefijo
echo "=== ASSETS ESTIMATED ==="
find output/v4_complete/amaziliahotel -name "ESTIMATED_*" | wc -l

echo "=== ASSETS REAL/VERIFIED ==="
find output/v4_complete/amaziliahotel -name "REAL_*" -o -name "VERIFIED_*" | wc -l

echo "=== ASSETS TOTAL ==="
find output/v4_complete/amaziliahotel -type f \( -name "*.json" -o -name "*.md" -o -name "*.html" -o -name "*.txt" \) ! -path "*/v4_audit/*" ! -path "*/metadata.json" | wc -l
```

### 3.2 Validación de GAPs corregidos

#### G1: research.json (confidence 0.0 → ?)

```bash
RESEARCH=$(ls -t output/v4_complete/amaziliahotel/research*.json 2>/dev/null | head -1)
echo "Research: $RESEARCH"
cat "$RESEARCH"

# Criterio: confidence > 0.5 Y sources_checked NO vacío
```

#### G2: hotel_schema (generico → ?)

```bash
SCHEMA=$(ls -t output/v4_complete/amaziliahotel/hotel_schema/*.json 2>/dev/null | grep -v metadata | head -1)
echo "Schema: $SCHEMA"
cat "$SCHEMA" | python -c "import json,sys; d=json.load(sys.stdin); print('address:', d.get('address',{})); print('telephone:', d.get('telephone',{})); print('geo:', d.get('geo',{})); print('starRating:', d.get('starRating',{}))"

# Criterio: address, telephone, geo.latitude/longitude NO vacíos
```

#### G3: Open Graph (B4 — antes NO existía → ?)

```bash
OG_FOLDER="output/v4_complete/amaziliahotel/open_graph_meta"
if [ -d "$OG_FOLDER" ]; then
    echo "✅ B4: open_graph_meta/ EXISTE"
    ls -la "$OG_FOLDER"
    cat "$OG_FOLDER"/*.html 2>/dev/null | head -20
else
    echo "❌ B4: open_graph_meta/ NO EXISTE"
fi

# Criterio: carpeta existe con contenido OG tags reales
```

#### G4: faq_page extensión (.csv → .json)

```bash
FAQ_FOLDER="output/v4_complete/amaziliahotel/faq_page"
ls -la "$FAQ_FOLDER"

# Verificar extensión correcta
echo "=== Extensiones en faq_page ==="
find "$FAQ_FOLDER" -type f ! -name "*metadata.json" | while read f; do
    echo "$f: $(echo $f | grep -oE '\.(csv|json|html|md)$')"
done

# Criterio: extensión .json o .html (no .csv)
```

#### G5: llms.txt duplicado

```bash
echo "=== llms.txt en geo_enriched/ ==="
cat output/v4_complete/amaziliahotel/geo_enriched/llms.txt 2>/dev/null | head -5

echo "=== llms.txt en llms_txt/ ==="
cat output/v4_complete/amaziliahotel/llms_txt/*.txt 2>/dev/null | head -5

# Criterio: geo_enriched/llms.txt = DEPRECATED o solo 1 versión existe
```

#### G6: optimization_guide contradicción title tag

```bash
OPT=$(ls -t output/v4_complete/amaziliahotel/optimization_guide/*.md 2>/dev/null | grep -v metadata | head -1)
echo "=== optimization_guide ==="
grep -i "title tag" "$OPT" | head -5

# Criterio: NO debe haber contradicción ("detectado" y "no detectado" en mismo archivo)
```

#### G7: monthly_report (plantilla vacia → ?)

```bash
REPORT=$(ls -t output/v4_complete/amaziliahotel/monthly_report/*.md 2>/dev/null | grep -v metadata | head -1)
echo "=== monthly_report ==="
grep -c "_____\|\" por confi" "$REPORT"
# Criterio: 0 matches de "_____" o "Por configurar"
```

#### G8-G9: WhatsApp y Voice ELIMINADOS del output

```bash
echo "=== whatsapp_button ==="
if [ -d "output/v4_complete/amaziliahotel/whatsapp_button" ]; then
    echo "❌ whatsapp_button/ AÚN EXISTE (debe tener _DEPRECATED_)"
    ls output/v4_complete/amaziliahotel/whatsapp_button/
else
    echo "✅ whatsapp_button/ ELIMINADO"
fi

echo "=== voice_assistant_guide ==="
if [ -d "output/v4_complete/amaziliahotel/voice_assistant_guide" ]; then
    echo "❌ voice_assistant_guide/ AÚN EXISTE (debe tener _DEPRECATED_)"
    ls output/v4_complete/amaziliahotel/voice_assistant_guide/
else
    echo "✅ voice_assistant_guide/ ELIMINADO"
fi
```

### 3.3 Verificación de coherencia interna de assets

#### 3.3.1 Datos del hotel consistentes entre assets

```bash
# Dirección debe ser consistente
echo "=== Dirección en assets ==="
grep -r "Via Pereira\|CERRITOS\|Cafelia" output/v4_complete/amaziliahotel/ --include="*.json" --include="*.md" --include="*.html" 2>/dev/null | grep -v "metadata" | head -5

# Teléfono debe ser consistente
echo "=== Teléfono en assets ==="
grep -r "310 4019049\|573104019049" output/v4_complete/amaziliahotel/ --include="*.json" --include="*.md" --include="*.html" 2>/dev/null | grep -v "metadata" | head -5

# Rating debe ser consistente
echo "=== Rating en assets ==="
grep -r "4\.5\|rating" output/v4_complete/amaziliahotel/ --include="*.json" --include="*.md" --include="*.html" 2>/dev/null | grep -v "metadata" | head -5
```

#### 3.3.2 Coherence validation post-ejecución

```bash
COH_VAL=$(cat output/v4_complete/amaziliahotel/v4_audit/coherence_validation.json 2>/dev/null)
echo "=== Coherence Validation ==="
echo "$COH_VAL" | python -c "import json,sys; d=json.load(sys.stdin); print('is_coherent:', d.get('is_coherent')); print('overall_score:', d.get('overall_score'))"

# Criterio: is_coherent: true Y overall_score >= 0.80
```

---

## FASE 4: Validación de Coherencia Tri-Play (GAPs vs Assets vs Propuesta)

### 4.1 Tabla de cobertura GAP → Asset → Servicio

| GAP | Antes (pre-refactor) | Después (post-refactor) | Asset que lo resuelve | Servicio en propuesta |
|-----|---------------------|------------------------|---------------------|----------------------|
| G1: research.json vacio | confidence 0.0 | ? | (datos via booking_scraper) | N/A (dato interno) |
| G2: hotel_schema generico | sin address/telephone | ? | hotel_schema/ | Datos Estructurados |
| G3: B4 Open Graph faltante | NO existia | ? | open_graph_meta/ | Open Graph / Meta Tags |
| G4: faq_page extension .csv | .csv (bug) | ? | faq_page/ | Datos Estructurados |
| G5: llms.txt duplicado | 2 versiones | ? | geo_enriched/llms.txt | IAO |
| G6: optimization_guide contradiccion | title tag contradictoria | ? | optimization_guide/ | SEO Local |
| G7: monthly_report vacio | _____ everywhere | ? | monthly_report/ | Informe Mensual |
| G8: WhatsApp sin brecha | promised_by=always | DEPRECATED (_DEPRECATED_NO_BRECHA.txt) | N/A | N/A |
| G9: Voice sin brecha | promised_by=always_aeo | DEPRECATED (_DEPRECATED_NO_BRECHA.txt) | N/A | N/A |
| G10: ROI 20X inflado | 20X directo | ROI 3X | N/A (es documento) | Precio/ROI |
| G11: coherence duplicada | 0.89 vs 0.86 | unificado | N/A | N/A |
| G12: paths Windows | C:\... | relativos | N/A | N/A |
| G13: "eje_cafetero" sin tilde | "eje_cafetero" | "Eje Cafetero" | N/A | N/A |
| G14: "COP COP" | doble moneda | corregido | N/A | N/A |

### 4.2 Score Forense Recalculado

```bash
# Ejecutar scoring manual
echo "=== SCORE FORENSO POST-REFACTOR ==="

# Dimension 1: Cobertura de brechas (4 brechas B1-B4) - Peso 25%
BRECHAS_CUBIERTAS=4  # B1-B4 todas con servicio
BRECHAS_TOTALES=4
SCORE_BRECHAS=$((BRECHAS_CUBIERTAS * 100 / BRECHAS_TOTALES))
echo "Cobertura brechas: $SCORE_BRECHAS% ($BRECHAS_CUBIERTAS/$BRECHAS_TOTALES) [peso 25%]"

# Dimension 2: Assets con datos reales (confidence > 0.5) - Peso 25%
# Contar manual: hotel_schema, open_graph, monthly_report, optimization_guide
ASSETS_CON_DATOS=4
ASSETS_TOTALES=12
SCORE_DATOS=$((ASSETS_CON_DATOS * 100 / ASSETS_TOTALES))
echo "Assets con datos reales: $SCORE_DATOS% ($ASSETS_CON_DATOS/$ASSETS_TOTALES) [peso 25%]"

# Dimension 3: Assets justificados (pain_ids_resolved) - Peso 15%
# NOTA: pain_ids_resolved es casi siempre MISSING en metadata.json
JUSTIFICADOS=0
JUSTIFICADOS_TOTAL=$ASSETS_TOTALES
SCORE_JUSTIFICADOS=$((JUSTIFICADOS * 100 / JUSTIFICADOS_TOTAL))
echo "Assets justificados (pain_ids): $SCORE_JUSTIFICADOS% ($JUSTIFICADOS/$JUSTIFICADOS_TOTAL) [peso 15%]"

# Dimension 4: Assets sin duplicacion - Peso 10%
DUPLICADOS=0  # Antes: hotel_schema (2), llms.txt (2) → ahora 0
SCORE_DUP=$(( (ASSETS_TOTALES - DUPLICADOS) * 100 / ASSETS_TOTALES))
echo "Sin duplicados: $SCORE_DUP% [peso 10%]"

# Dimension 5: Assets entregables (no DEPRECATED, no ESTIMATED) - Peso 25%
ENTREGABLES=8  # Estimado post-FASE-5 (sin WhatsApp, sin Voice)
ENTREGABLES_TOTAL=$((ASSETS_TOTALES - 2))  # menos WhatsApp y Voice
SCORE_ENTREGABLES=$((ENTREGABLES * 100 / ENTREGABLES_TOTAL))
echo "Entregables: $SCORE_ENTREGABLES% ($ENTREGABLES/$ENTREGABLES_TOTAL) [peso 25%]"

# SCORE GLOBAL (5 dimensiones, pesos: 25+25+15+10+25=100)
echo ""
echo "=== SCORE FORENSO ESTIMADO ==="
echo "Formula: (BRECHAS*25 + DATOS*25 + JUSTIFICADOS*15 + SINDUP*10 + ENTREGABLES*25) / 100"
SCORE_FORENSO=$(( (SCORE_BRECHAS * 25 + SCORE_DATOS * 25 + SCORE_JUSTIFICADOS * 15 + SCORE_DUP * 10 + SCORE_ENTREGABLES * 25) / 100 ))
echo "Score estimado: $SCORE_FORENSO/100"
```

### 4.3 Veredicto de GAPs

| GAP | Estado post-ejecución | Veredicto |
|-----|----------------------|-----------|
| G1-G14 | Validación manual requerida | ? |

---

## FASE 5: Análisis de NUEVOS GAPs (no existentes en plan original)

### 5.1 Verificar si existen nuevos problemas

```bash
# Nuevos archivos o carpetas inesperada
echo "=== Assets inesperado (nuevos) ==="
find output/v4_complete/amaziliahotel -maxdepth 2 -type d ! -name "v4_audit" ! -name "geo_enriched" ! -name "review_widget" ! -name "review_plan" ! -name "org_schema" | sort

# Verificar si hay archivos sin prefijo ESTIMATED/VERIFIED/REAL
find output/v4_complete/amaziliahotel -type f \( -name "*.json" -o -name "*.md" -o -name "*.html" -o -name "*.txt" \) ! -name "*metadata.json" ! -path "*/v4_audit/*" ! -path "*/geo_enriched/*" | while read f; do
    BASENAME=$(basename "$f")
    if ! echo "$BASENAME" | grep -qE "^(ESTIMATED_|VERIFIED_|REAL_|DEPRECATED_)"; then
        echo "⚠️ Archivo sin prefijo estándar: $f"
    fi
done

# Verificar coherence_score del diagnóstico vs coherence_validation.json
DIAG_SCORE=$(grep "coherence_score:" "$DIAGNOSTICO" | head -1)
echo "Diagnostico coherence_score: $DIAG_SCORE"

VAL_SCORE=$(cat output/v4_complete/amaziliahotel/v4_audit/coherence_validation.json 2>/dev/null | grep -o '"overall_score": [0-9.]*' | head -1)
echo "Coherence validation overall_score: $VAL_SCORE"
```

### 5.2 Verificar alineación Diagnóstico ↔ Propuesta ↔ Assets (nuevas desconexiones)

```bash
# 1) El diagnóstico menciona B4 (Open Graph)?
grep -c "Open Graph\|OpenGraph\|meta tag\|social" "$DIAGNOSTICO"

# 2) La propuesta menciona Open Graph?
grep -c "Open Graph\|social\|meta tag" "$PROPUESTA"

# 3) El asset Open Graph existe?
[ -d "output/v4_complete/amaziliahotel/open_graph_meta" ] && echo "✅" || echo "❌"

# Si diagnostico dice B4 Y propuesta NO lo menciona → NUEVO GAP
```

### 5.3 Checklist de nuevos GAPs potenciales

| Check | Archivo/Dato | Esperado | Actual | ¿Nuevo GAP? |
|-------|-------------|----------|--------|-------------|
| faq_page extension | faq_page/* | .json/.html | ? | ? |
| open_graph_meta existe | carpeta | existe | ? | ? |
| whatsapp_button DEPRECATED | carpeta | _DEPRECATED_ | ? | ? |
| voice_assistant_guide DEPRECATED | carpeta | _DEPRECATED_ | ? | ? |
| monthly_report sin ____ | monthly_report/*.md | 0 blanks | ? | ? |
| research.json confidence | research/*.json | > 0.5 | ? | ? |
| hotel_schema con datos | hotel_schema/*.json | address+telf+geo | ? | ? |
| ROI 3X no 20X | PROPUESTA | 3X base | ? | ? |

---

## FASE 6: Veredicto Final y Recomendación

### 6.1 Criterios de aprobación

| Criterio | Umbral | Ponderación |
|----------|--------|-------------|
| Score forense (GAPs pre-existentes) | >= 80/100 | 40% |
| Coherence validation | is_coherent: true | 20% |
| GAPs pre-existentes resueltos | >= 11/14 (80%) | 20% |
| **GAPs nuevos detectados** | **<= 2 tolerable** | **10%** |
| Tests pasando | 100% | 10% |

### 6.2 Clasificación de nuevos GAPs por severidad

| Severidad | Significado | Acción |
|-----------|-------------|--------|
| CRITICO | Bloquea entrega al cliente | Corregir antes de veredicto APROBADO |
| ALTO | Degrada valor percibido | Corregir en plan de seguimiento |
| MEDIO | Inconsistencia menor | Documentar y monitorizar |
| BAJO | Cosmético | Ignorar |

### 6.3 Veredicto

| Condición | Veredicto |
|-----------|-----------|
| Score >= 80 AND coherence=true AND GAPs>=11/14 AND tests=100% | **APROBADO** ✅ |
| Score 60-79 OR coherence=false OR GAPs 8-10/14 OR nuevos GAPs <= 2 | **APROBADO CON CORRECCIONES** ⚠️ |
| Score < 60 OR coherence=false OR GAPs < 8/14 OR nuevos GAPs > 2 | **RECHAZADO** ❌ |

### 6.4 Acciones post-veredicto

**Si APROBADO:**
- Generar reporte final en `evidence/amazilia-e2e-20260420/VERedicto_Final.md`
- Commit: `git add . && git commit -m "docs(amazilia): validacion E2E APROBADA - score X/100"`

**Si APROBADO CON CORRECCIONES:**
- Listar GAPs restantes con severidad
- Crear plan de corrección en `evidence/amazilia-e2e-20260420/GAPs_Remaining.md`

**Si RECHAZADO:**
- No proceder a entrega
- Regenerar v4complete SOLO si GAPs son críticos y corregibles
- Documentar en `evidence/amazilia-e2e-20260420/VERedicto_Final.md`

---

## RESUMEN DE VALIDACIONES (Checklist E2E)

**Dos objetivos paralelos:**
1. **GAPs pre-existentes**: ¿Las 14 correcciones de FASE-1 a FASE-6 funcionaron?
2. **GAPs nuevos**: ¿La ejecución v4complete o el refactor introdujeron nuevos problemas?

### Pre-ejecución (FASE-0)
- [ ] py_compile: 0 errores en módulos modificados
- [ ] pytest: 0 fallos en suite completa
- [ ] run_all_validations.py: 4/4 passed
- [ ] doctor.py --status: sin bloqueantes

### Ejecución (FASE-1)
- [ ] v4complete exit code: 0
- [ ] Archivos generados: diagnostico + propuesta + assets

### Coherencia (FASE-2)
- [ ] Diagnóstico → Propuesta: 4 brechas con 4+ servicios
- [ ] Propuesta → Diagnóstico: sin invenciones (WhatsApp/Voice eliminados)
- [ ] ROI: 3X Tier C (no 20X directo)
- [ ] Tier C mencionado en propuesta

### Assets (FASE-3)
- [ ] G1: research.json confidence > 0.5
- [ ] G2: hotel_schema con address + telephone + geo
- [ ] G3: open_graph_meta/ existe con datos reales
- [ ] G4: faq_page extensión .json/.html (no .csv)
- [ ] G5: llms.txt sin duplicado
- [ ] G6: optimization_guide sin contradicción title tag
- [ ] G7: monthly_report sin blanks "_____"
- [ ] G8: whatsapp_button DEPRECATED o eliminado
- [ ] G9: voice_assistant_guide DEPRECATED o eliminado
- [ ] G10: ROI 3X en propuesta
- [ ] G11-G14: coherencia interna (paths, texto, moneda)

### Tri-Play (FASE-4)
- [ ] Score forense >= 80/100
- [ ] is_coherent: true en coherence_validation.json
- [ ] 0 nuevas desconexiones Diagnóstico ↔ Propuesta ↔ Assets

### GAPs nuevos (FASE-5)
- [ ] Detección de archivos/carpetas inesperadas en output
- [ ] Verificación de extensiones correctas en faq_page
- [ ] Verificación de DEPRECATED marks en WhatsApp y Voice
- [ ] Consistencia de datos (dirección, teléfono, rating) entre assets
- [ ] Coherence score vs coherence validation (nueva inconsistencia)
- [ ] B4 Open Graph en diagnóstico Y en propuesta Y asset existe

### Final (FASE-6)
- [ ] Veredicto: APROBADO / APROBADO CON CORRECCIONES / RECHAZADO
- [ ] GAPs nuevos clasificados por severidad (CRITICO/ALTO/MEDIO/BAJO)
- [ ] Reporte generado en evidence/amazilia-e2e-20260420/

---

*Plan creado: 2026-04-20*
*Reemplaza: .opencode/plans/context/AMAZILIAHOTEL_FORENSIC_AUDIT_PLAN.md (v1)*
*Workflow: .agents/workflows/phased_project_executor.md v2.4.0 §4.5*
