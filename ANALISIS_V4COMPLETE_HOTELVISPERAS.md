# ANÁLISIS V4COMPLETE - HOTEL VÍSPERAS
## Proyecto: iah-cli | URL: https://www.hotelvisperas.com/es
## Fecha: 2026-03-26

---

## RESUMEN EJECUTIVO

El flujo V4COMPLETE de iah-cli se estructura en 5 fases documentadas, pero se encontraron **5 desconexiones críticas** entre lo que el sistema promete, lo que valida, y lo que finalmente entrega.

**Coherence Score Global: 0.86** ( umbral: 0.8 ) - PASA con ADVERTENCIAS

---

## 1. PUNTO DE ENTRADA: main.py

**Ubicación**: `main.py:1314-1317`

```python
if args.command == "v4complete":
    maybe_run_config_check(args)
    run_v4_complete_mode(args)
    sys.exit(0)
```

**Función principal**: `run_v4_complete_mode()` (líneas 1324-2429)

### Flujo de datos en run_v4_complete_mode():

```
L1324: run_v4_complete_mode(args)
  L1356: AgentHarness() - memoria y routing
  L1377: OnboardingController() - HOOK automático
  L1403: FASE 2: CrossValidator() - VALIDACIÓN CRUZADA
  L1417: V4ComprehensiveAuditor() - аудит
  L1445: validator.validate_whatsapp() - validación WhatsApp
  L1451: FASE 3: Escenarios Financieros
  L1463: _load_latest_onboarding_data() - datos operativos
  L1563: resolve_adr_with_shadow() - ADR resolution
  L1584: FinancialCalculatorV2() - cálculos financieros
  L1847: PainSolutionMapper() - MAPEO P→S
  L1890: FASE 4: CoherenceValidator() - GATE COHERENCIA
  L1953: V4DiagnosticGenerator() - genera DIAGNÓSTICO
  L1996: V4ProposalGenerator() - genera PROPUESTA (si coherence ≥ 0.8)
  L2034: V4AssetOrchestrator() - genera ASSETS
```

---

## 2. ANÁLISIS FASE POR FASE

### FASE 1: HOOK AUTOMÁTICO

**Módulo**: `modules/orchestration_v4/onboarding_controller.py`

**Función**: `start_onboarding()` (línea 1388-1398)

```python
state = controller.start_onboarding(
    hotel_url=args.url,
    hotel_name=hotel_name,
    region=region
)
```

**Datos de salida**: 
- `state.hotel_id`
- `state.phase_1_result.hook_message`
- `state.progress_percentage`

**OBSERVACIÓN**: El Hook se genera pero no se valida contra datos reales. Solo usa la URL para detectar región.

---

### FASE 2: VALIDACIÓN APIs CRUZADA

**Módulo**: `modules/data_validation/cross_validator.py`

**Función**: `validate_whatsapp()` (línea 1445)

```python
whatsapp_validation = validator.validate_whatsapp(whatsapp_web, whatsapp_gbp)
```

**Datos de entrada**:
- `whatsapp_web` = `audit_result.validation.phone_web`
- `whatsapp_gbp` = `audit_result.validation.phone_gbp`

**OBSERVACIÓN CRÍTICA**: 
El `audit_result` de `V4ComprehensiveAuditor()` contiene los teléfonos, pero en el MANIFEST (línea 89 del DIAGNÓSTICO) se ve:
```
| 🟡 whatsapp_number | ['+57 3113973744', '+57 3168245636'] | ESTIMATED | Web |
```

Esto indica que se detectó un **CONFLICTO** (dos números diferentes), pero el validation summary lo marca como **ESTIMATED** en lugar de **CONFLICT**. Esto es una **desconexión**.

---

### FASE 3: MAPEO P→S (PainSolutionMapper)

**Módulo**: `modules/commercial_documents/pain_solution_mapper.py`

**Función**: `detect_pains()` (línea 215-402)

```python
detected_pains = pain_mapper.detect_pains(audit_result, validation_summary)
```

**Problemas detectados** (según `pain_solution_mapper.py`):

| Pain ID | Severity | Descripción |
|---------|----------|-------------|
| no_whatsapp_visible | high | No hay WhatsApp visible |
| whatsapp_conflict | high | Números diferentes entre web y GBP |
| no_faq_schema | medium | Sin FAQ Schema |
| low_gbp_score | high | GBP score < 70 |
| no_hotel_schema | high | Sin Hotel Schema |
| no_org_schema | low | Sin Organization Schema |
| metadata_defaults | high | Metadatos por defecto del CMS |
| ai_crawler_blocked | medium | IA crawlers bloqueados |
| low_citability | medium | Contenido poco citable |
| low_ia_readiness | high | Baja preparación IA |

**Assets generados según MANIFEST**:
- `hotel_schema`
- `llms_txt`
- `org_schema`

**ASSET FALLIDO**: `optimization_guide` - Falló por content validation con placeholders.

---

### FASE 4: GATE COHERENCIA

**Módulo**: `modules/commercial_documents/coherence_validator.py`

**Función**: `validate()` (línea 113-171)

```python
pre_coherence_report = coherence_validator.validate(
    temp_diagnostic,
    temp_proposal,
    asset_plan,
    validation_summary
)
pre_coherence_score = pre_coherence_report.overall_score
```

**Checks realizados**:

| Check | Score | Passed | Severity | Observación |
|-------|-------|--------|----------|-------------|
| problems_have_solutions | 0.60 | ✅ | warning | Solo 60% (3/5) soluciones |
| assets_are_justified | 1.00 | ✅ | info | 100% justificados |
| financial_data_validated | 0.70 | ✅ | info | Confidence promedio 0.70 |
| whatsapp_verified | 1.00 | ✅ | info | "No hay asset de WhatsApp button" |
| price_matches_pain | 1.00 | ✅ | info | Precio 4.2x en rango ideal |
| promised_assets_exist | 1.00 | ✅ | info | Assets implementados |

---

## 3. DESCONEXIONES IDENTIFICADAS

### 🔴 DESCONEXIÓN 1: WhatsApp - Prometido vs Validado

**Ubicación**: `coherence_validation.json` línea 30

```
"name": "whatsapp_verified"
"message": "No hay asset de WhatsApp button"
```

**PERO** en `MANIFEST.json` línea 387-396:
```json
{
  "name": "ASSETS/whatsapp_button\\ESTIMATED_boton_whatsapp_20260323_155957.html",
  "size_bytes": 2018,
  "type": "code"
}
```

**CONTRADICCIÓN**: El coherence validator dice "No hay WhatsApp button" pero el archivo EXISTE en el delivery.

**Causa probable**: 
- El `whatsapp_button` fue marcado como SKIPPED o WARNING durante generation
- O el orden de ejecución causa que el asset se genere después de la validación de coherencia
- El mensaje "No hay asset de WhatsApp button" significa que el check `whatsapp_verified` no encontró el asset en la lista `asset_plan` que se pasó al validator

**Impacto**: El diagnóstico menciona "WhatsApp diferente en web vs Google" (línea 49 DIAGNÓSTICO) con impacto $1.252.800 COP, pero NO se generó el asset para resolverlo.

---

### 🔴 DESCONEXIÓN 2: optimization_guide - Prometido vs Entregado

**Ubicación**: `asset_generation_report.json` líneas 55-63

```json
"failed_assets": [
  {
    "asset_type": "optimization_guide",
    "reason": "Content validation failed: placeholder: Placeholder detected: \\.\\.\\.; generic_phrase: Generic phrase detected: 'no configurado'",
    "pain_ids_affected": ["metadata_defaults"],
    "preflight_status": "BLOCKED"
  }
]
```

**PERO** en `PROPUESTA_COMERCIAL.md` línea 62:
```
| Metadatos por Defecto | Título y descripción usando valores por defecto del CMS | optimization_guide | 🔴 P1 |
```

**CONTRADICCIÓN**: El asset `optimization_guide` se prometió como solución P1 para "Metadatos por Defecto", pero FALLÓ en content validation.

**Causa**: El generador de optimization_guide usó placeholders genéricos ("..." y "no configurado") en lugar de datos reales del hotel.

**Impacto**: La propuesta comercial promete un asset que NO se puede entregar.

---

### 🟡 DESCONEXIÓN 3: Timestamps Múltiples en Assets

**Ubicación**: MANIFEST.json y archivos físicos

Se observan timestamps diferentes para el mismo tipo de asset:

| Asset Type | Timestamps |
|------------|------------|
| hotel_schema | 155211, 155957, 164630, 164914, 165337, 170649, 171200 |
| llms_txt | 155211, 155957, 164630, 164914, 165337, 170649, 171200 |
| geo_playbook | 155211, 155957, 164630, 164914, 165337 |
| review_plan | 155211, 155957, 164630, 164914, 165337 |
| review_widget | 155211, 155957, 164630, 164914 |

**Causa probable**: 
- Múltiples ejuciones del flujo
- Regeneración selectiva de assets
- FASE-CAUSAL-01 (SitePresenceChecker) causando regeneraciones

**Impacto**: Inconsistencia en versionamiento. El MANIFEST muestra 78 archivos totales, muchos de ellos son redundantes.

---

### 🟡 DESCONEXIÓN 4: Confidence Score en DIAGNÓSTICO vs Validación

**Ubicación DIAGNÓSTICO.md** línea 108:
```
### Coherence Score: 0.8599999999999999%
```

**Ubicación coherence_validation.json** línea 3:
```json
"overall_score": 0.86
```

**Diferencia**: 0.86 vs 0.8599999999999999 - Son numéricamente equivalentes pero el diagnóstico muestra más decimales, sugiriendo que se calculó independientemente.

**Causa**: El `coherence_score` en el diagnóstico viene de `V4DiagnosticGenerator()` línea 1953-1961:
```python
diagnostic_path = diagnostic_gen.generate(
    ...
    coherence_score=pre_coherence_score,
)
```

El valor `pre_coherence_score` se calcula en línea 1921 como:
```python
pre_coherence_score = pre_coherence_report.overall_score
```

**Observación**: El redondeo difiere, pero el valor es coherente.

---

### 🟡 DESCONEXIÓN 5: delivery_ready_percentage = 0.0

**Ubicación**: `asset_generation_report.json` línea 12

```json
"delivery_ready_percentage": 0.0
```

**PERO** `can_use: 3` (línea 10) - 3 assets tienen `can_use: true`.

**Causa**: El cálculo en `v4_asset_orchestrator.py` línea 87-91:
```python
delivery_ready_pct = (
    ((generated_count - estimated_count) / generated_count) * 100
    if generated_count > 0
    else 0.0
)
```

Como `estimated_count = 3` y `generated_count = 3`, el resultado es 0%.

**Significado**: El sistema considera que los 3 assets generados tienen calidad "ESTIMATED" (WARNING), no "VERIFIED" (PASSED), por lo tanto `delivery_ready_percentage` es 0%.

**Impacto**: A pesar de que `can_use = true` para todos los assets, ninguno se considera "delivery ready" porque todos tienen preflight_status = WARNING.

---

## 4. FLUJO DE DATOS COMPLETO

```
INPUT: --url https://www.hotelvisperas.com/es
           │
           ▼
    ┌─────────────────┐
    │ OnboardingCtrl  │ → hotel_id, region
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │V4Comprehensive  │ → audit_result
    │   Auditor       │   (schema, gbp, performance,
    └────────┬────────┘    validation, metadata)
             │
             ▼
    ┌─────────────────┐
    │ CrossValidator  │ → validation_summary
    │ (WhatsApp ADR)  │   (validated_fields)
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ PainSolutionMap │ → detected_pains
    │ .detect_pains() │   (12 pain types)
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │PainSolutionMap  │ → asset_plan
    │.generate_asset_ │   (4 assets planned)
    │     plan()      │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ CoherenceValid  │ → pre_coherence_score: 0.86
    │ .validate()     │   ⚠️ Solo 3/5 problems solved
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ V4DiagnosticGen │ → DIAGNOSTICO.md
    │ .generate()     │   (5 problemas listados)
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ V4ProposalGen   │ → PROPUESTA_COMERCIAL.md
    │  .generate()    │   (4 assets prometidos)
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │V4AssetOrchestr.│ → ASSETS/
    │.generate_assets │   - hotel_schema ✅ WARNING
    │                 │   - llms_txt ✅ WARNING
    │                 │   - org_schema ✅ WARNING
    │                 │   - optimization_guide ❌ BLOCKED
    └─────────────────┘
```

---

## 5. VALIDACIÓN CRUZADA: DIAGNÓSTICO vs PROPUESTA vs ASSETS

| Aspecto | Diagnóstico | Propuesta | Assets | ¿Coherente? |
|---------|------------|-----------|--------|--------------|
| Pérdida mensual | $3.132.000 COP | $3.132.000 COP | N/A | ✅ |
| Precio | N/A | $800.000 COP/mes | N/A | ✅ |
| ROI | N/A | 292X (6 meses) | N/A | ⚠️ (cálculo suspect) |
| WhatsApp conflict | Mencionado | Mencionado | NO GENERADO | ❌ |
| Metadata defaults | Mencionado | Mencionado | OPTIMIZATION_GUIDE FALLÓ | ❌ |
| IA Readiness (30/100) | Mencionado | Mencionado | hotel_schema, llms_txt | ✅ |
| Org Schema | Mencionado | Mencionado | org_schema generado | ✅ |

---

## 6. ANOMALÍAS CÓDIGO

### ANOMALÍA 1: Duplicación de código en main.py

**Ubicación**: `main.py:204-277` (4 definiciones idénticas de `_audit_handler`)

```python
def _audit_handler(payload: dict, context) -> dict:
    """Harness-compatible handler for audit command (DEPRECATED - use v4complete instead)."""
    if not ORCHESTRATOR_AVAILABLE:
        return {"status": "error", "message": "Comando audit deprecado. Use v4complete en su lugar."}
    # Import movido al principio del archivo con manejo condicional
def _audit_handler(payload: dict, context) -> dict:
    """Harness-compatible handler for audit command (DEPRECATED - use v4complete instead)."""
    ...
```

La misma función está definida 4 veces seguidas. Esto sugiere un problema de merge o edición.

---

### ANOMALÍA 2: Línea 102-103 duplicada en data_structures.py

```python
monthly_opportunity_cop: int = 0  # Valor absoluto cuando loss <= 0 (ganancia/equilibrio)
    
    def format_loss_cop(self) -> str:
        """Format loss amount with semantic handling for negative values."""
```

El atributo `monthly_opportunity_cop` aparece dos veces en la misma clase `Scenario` (líneas 91 y 103).

---

### ANOMALÍA 3: Cálculo de ROI en Propuesta

**Ubicación**: `PROPUESTA_COMERCIAL.md` línea 36

```
ROI Proyectado: 292X en 6 meses
```

**Cálculo esperado**:
- Inversión total: $800.000 × 6 = $4.800.000
- Ingreso recuperado: $3.132.000 × 6 = $18.792.000
- ROI = $18.792.000 / $4.800.000 = 3.91X

**PERO** dice 292X. Esto es claramente un error de formato o cálculo (probablemente multiplicó por 100 o mostró el valor en porcentaje).

---

## 7. CONCLUSIONES

### Estado General: FUNCIONAL con ADVERTENCIAS

El flujo V4COMPLETE está correctamente estructurado con 5 fases bien definidas:
1. ✅ Hook automático
2. ✅ Validación cruzada
3. ✅ Mapeo P→S
4. ✅ Gate de coherencia (score 0.86 ≥ 0.8)
5. ⚠️ Assets (3/4 generados, 1 fallido)

### Desconexiones Críticas:

1. **WhatsApp**: Diagnosticado pero no generado como asset
2. **optimization_guide**: Prometido pero falló en validación de contenido

### Recomendaciones:

1. **Prioridad Alta**: Arreglar el generador de `optimization_guide` para que no use placeholders
2. **Prioridad Media**: Investigar por qué `whatsapp_button` no se incluyó en `asset_plan`
3. **Prioridad Baja**: Limpiar archivos de ejecuciones anteriores (timestamps múltiples)
4. **Bug Fix**: El cálculo de ROI muestra 292X en lugar de 3.9X

---

## 8. ARCHIVOS ANALIZADOS

| Archivo | Última modificación | Tamaño |
|---------|---------------------|--------|
| main.py | 2026-03-25 | 103,071 bytes |
| pain_solution_mapper.py | 2026-03-23 | 29,935 bytes |
| coherence_validator.py | 2026-03-23 | 20,000 bytes |
| v4_asset_orchestrator.py | 2026-03-25 | 21,104 bytes |
| data_structures.py | 2026-03-23 | 14,695 bytes |
| v4_diagnostic_generator.py | 2026-03-23 | 41,445 bytes |
| DIAGNOSTICO.md | 2026-03-23 | 3,350 bytes |
| PROPUESTA_COMERCIAL.md | 2026-03-23 | 5,546 bytes |
| coherence_validation.json | 2026-03-23 | 1,310 bytes |
| asset_generation_report.json | 2026-03-23 | 4,081 bytes |
| MANIFEST.json | 2026-03-23 | 11,693 bytes |

---

*Reporte generado: 2026-03-26*
*Proyecto: iah-cli | Hotel Vísperas*
