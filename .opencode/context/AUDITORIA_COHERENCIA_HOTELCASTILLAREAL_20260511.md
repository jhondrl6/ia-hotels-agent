---
created_at: 2026-05-11 19:05
updated_at: 2026-05-11 20:15
validated_by: hermes — auditoría exhaustiva contra código vivo
hotel: Hotel Castilla Real
hotel_url: https://www.hotelcastillareal.com/
hotel_id: hotelcastillareal
region: eje_cafetero
delivery_zip: /mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/deliveries/hotelcastillareal_20260511.zip
v4complete_run_timestamp: 2026-05-11 18:50
document_type: AUDITORIA_COHERENCIA_V4COMPLETE_VALIDADA
status: PLAN-READY — validado contra código vivo, listo para diseñar plan de intervención
purpose: Fuente de verdad validada para diseñar plan de refactorización por fases
---

# AUDITORÍA DE COHERENCIA — Hotel Castilla Real
## v4complete 2026-05-11 18:50 — VALIDADO CONTRA CÓDIGO VIVO

---

## 1. RESUMEN EJECUTIVO

**Veredicto: SISTEMA DESCONECTADO — 5 fuentes de coherence_score para el mismo delivery.**

El pipeline produce 5 valores distintos de coherence_score porque el gate NUNCA consume al validator, el validator corre 2× con datos distintos (pre/post generación), y `v4_complete_report.json` introduce 2 scores adicionales. El H10 FIX que debía unificar validator↔gate existe como código muerto: `CoherenceGate._validator` está instanciado pero jamás llamado en `execute()`.

Además, `open_graph_generator.py` tiene **hardcoded defaults de otro hotel** (`'Amazilia Hotel Campestre'`) en 3 lugares distintos (L87, L94, L107) — no es LLM hallucination, es código Python determinístico que contamina entregas cross-hotel.

Todos los 7 assets generados tienen confidence=0.5 (100% ESTIMATED). El delivery es funcionalmente un placeholder hasta que el cliente complete onboarding.

---

## 2. DATOS DEL DELIVERY

| Campo | Valor |
|-------|-------|
| Diagnóstico | `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260511_185023.md` (12,272 bytes) |
| Propuesta | `02_PROPUESTA_COMERCIAL_20260511_185033.md` (9,714 bytes) |
| coherence_validation.json | `hotelcastillareal/v4_audit/coherence_validation.json` |
| gate_report | `hotelcastillareal/v4_audit/gate_report_20260511_185038.json` |
| asset_generation_report | `hotelcastillareal/v4_audit/asset_generation_report.json` |
| v4_complete_report | `output/v4_complete/v4_complete_report.json` (≠ hotel-specific) |
| geo_flow_result | `hotelcastillareal/v4_audit/geo_flow_result.json` |
| ZIP | `deliveries/hotelcastillareal_20260511.zip` (45 archivos, válido) |
| Modelo | DeepSeek (provider: deepseek) |
| Región | Eje Cafetero |
| Tier | C (sin onboarding — datos estimados/benchmark) |
| Assets planificados | 12 |
| Assets generados | 12 (100% ESTIMATED, confidence=0.5) |
| Assets skipped | 1 (whatsapp_button — ya existe en sitio) |

---

## 3. DIVERGENCIA DE COHERENCE SCORE (5 FUENTES)

### Los 5 scores — MISMO delivery, MISMO hotel

| # | Fuente | Score raw | Score display | is_coherent | Errores |
|---|--------|-----------|---------------|-------------|---------|
| 1 | `coherence_validation.json` (validator pre-gen) | ~0.8053 | 0.81 | **false** | 2 |
| 2 | `asset_generation_report.coherence_report` (orchestrator pre-gen) | 0.8261... | 0.83 | false | 1 |
| 3 | `gate_report coherence.value` (post-gen, via assessment) | 0.8261... | 0.83 | **PASSED** | 0 |
| 4 | `v4_complete_report.coherence_score` | 0.8466... | 0.85 | — | — |
| 5 | `v4_complete_report.coherence_score_post` | 0.8056... | 0.81 | — | — |

### Trazado de cada score en el código

```
main.py L2228: CoherenceValidator.validate() → pre_coherence_report (0.8053)
                  ↓ se guarda en coherence_validation.json como 0.81
                  
main.py L2414: orchestrator.generate_assets() → asset_result.coherence_report (0.8261)
                  ↓ se guarda en asset_generation_report.json como 0.83
                  
main.py L2448: diagnostic_gen.generate(coherence_score=asset_result.coherence_report.overall_score)
                  ↓ diagnostic YAML header: 0.8261

main.py L2653: assessment["coherence_score"] = asset_result.coherence_report.overall_score
                  ↓ gate_report coherence.value: 0.8261

main.py L2955: 'coherence_score': pre_coherence_score  ← 0.8053 esperado, JSON muestra 0.8467 ⚠️
main.py L2956: 'coherence_score_post': asset_result.post_coherence_score  ← 0.8056
```

### Anomalía detectada

`v4_complete_report.coherence_score` (0.8467) **no coincide con `pre_coherence_score`** (0.8053). `pre_coherence_score` se asigna en L2236 y NUNCA se reasigna hasta L2955. El valor 0.8467 no es trazable a ningún cálculo conocido en el pipeline. Posible corrupción por escritura concurrente o valor residual de ejecución anterior — requiere investigación en FASE de implementación.

---

## 4. CONTAMINACIÓN DE TEMPLATES (Cross-bleed)

### open_graph.html — HOTEL ERRADO (CAUSA RAÍZ PRECISA)

```html
<!-- Open Graph Meta Tags for Amazilia Hotel Campestre -->
```

**NO es LLM hallucination.** Es código Python determinístico:

```python
# open_graph_generator.py:87 — DEFAULT ES OTRO HOTEL
hotel_name = hotel_data.get('hotel_name', 'Amazilia Hotel Campestre')

# open_graph_generator.py:107 — DEFAULT URL ES OTRO HOTEL
website_url = hotel_data.get('website_url', hotel_data.get('website', 'https://amaziliahotel.com/'))

# open_graph_generator.py:93-94 — DEFAULTS DE OTRO HOTEL
rating = hotel_data.get('rating', 4.5)
review_count = hotel_data.get('review_count', hotel_data.get('reviews', 202))
```

Cuando el pipeline pasa `hotel_data` con key `'name'` en vez de `'hotel_name'`, el `.get('hotel_name', ...)` no encuentra la key y usa el fallback: **literalmente otro hotel**. Tres lugares con defaults cross-hotel en un solo archivo.

### local_content_page.md — contenido genérico (CAUSA RAÍZ PRECISA)

```markdown
# Hotel en  - Lo que debes saber (2026)
# Hotel Boutique  Colombia: Todo lo que necesitas saber
```

El `LocalContentGenerator` (609 líneas) es un generador basado en LLM. Recibe `hotel_data` sin campo `city` poblado → el LLM no tiene ubicación para interpolar → título con location vacío. No hay validación pre-LLM del campo `city`.

---

## 5. CAMPOS VACÍOS EN ASSETS CRÍTICOS

### hotel_schema.json (confidence 0.5, can_use: false)

```json
{
  "@type": "LodgingBusiness",
  "name": "Hotel Castilla Real",
  "description": "",        ← VACÍO
  "addressLocality": "",    ← VACÍO
  "addressRegion": "",      ← VACÍO
  "amenityFeature": [],     ← VACÍO
  "image": [],              ← VACÍO
  "url": "https://www.hotelcastillareal.com/",  ← CORRECTO
  "telephone": "+57 310 4692201",               ← CORRECTO
  "geo": { "latitude": "4.8095346", "longitude": "-75.69123259999999" }  ← CORRECTO
}
```

**No es bug del generador.** Es limitación del input (Tier C sin onboarding). El generador produce el schema correcto con los datos disponibles. La causa raíz es el pipeline de datos, no el generador. Campos con datos reales (url, telephone, geo) sí se pueblan correctamente — demostrando que el generador funciona cuando recibe datos.

### org_schema.json (confidence 0.5, can_use: false)

```json
{
  "@type": "Organization",
  "name": "Hotelcastillareal"
}
```

Solo 2 campos. Sin url, address, contactInfo. Mismo root cause que hotel_schema: input insuficiente. El name "Hotelcastillareal" (sin espacios) sugiere que el campo viene de `hotel_id` en vez de `hotel_name`.

---

## 6. CONTRADICCIÓN EN proposal_asset_alignment GATE

```json
{
  "alignment_percentage": 0.0,
  "all_aligned": true,        ← NO es contradicción — son métricas ortogonales
  "aligned_count": 0,
  "missing_count": 0,
  "low_quality_count": 7,
  "present_in_production": 1
}
```

**Explicación validada contra código** (`proposal_asset_alignment.py:76-85`):

- `all_aligned` = `len(self.missing) == 0` → mide **cobertura** (¿falta algo?)
- `alignment_percentage` = `len(self.aligned) / self.total_services` → mide **calidad** (¿cuántos pasan el threshold de confidence?)
- `present_in_production` se excluye de ambas métricas

En este delivery: WhatsApp existe en producción (→ present_in_production, no missing), los otros 7 se generaron pero con confidence 0.5 < 0.7 (→ low_quality, no aligned). Resultado: 0 missing → all_aligned=true; 0 aligned → alignment=0.0%.

**No es un bug lógico, es naming confuso.** `all_aligned` debería llamarse `all_covered`. La semántica es correcta pero el nombre induce a error.

### Estado final del gate

```
readiness.status: NOT_READY
blocking_issues: 1 (tier_c_onboarding_required)
warnings: 2 (financial_validity, asset_confidence)
```

El único bloqueo es tier_c. Los 7 assets low_quality + alignment 0% solo generan WARNING.

---

## 7. WHATSAPP: CONFLICTO SIN RESOLUCIÓN

| Fuente | Resultado |
|--------|-----------|
| coherence_validator.whatsapp_verified | **FAILED** (score 0.30, threshold 0.90) |
| whatsapp_button asset | **SKIPPED** — "ya implementado en sitio" |
| whatsapp_conflict_guide | Generado con confidence 0.5 (WARNING), formato .md informativo |
| audit_report whatsapp_status | **CONFLICT** |
| gate present_in_production | **exists** |
| ZIP delivery | `whatsapp_conflict_guide/` incluido (45 archivos total) |

El `whatsapp_conflict_guide` es intencionalmente informativo (.md), no un asset desplegable. El GAP-4 persiste: `site_verification_applied: true` pero sin pipeline de despliegue real. El conflicto de números (web: 6063332192 vs GBP: 3104692201) queda documentado pero no resuelto operativamente.

---

## 8. DIVERGENCIA GEO SCORE: 70/100 vs 23/100

| Fuente | Score | Sistema |
|--------|-------|---------|
| Diagnóstico (tabla principal) | 70/100 | `_calculate_geo_score()` — basado en GBP |
| geo_flow_result.json | 23/100 (band: critical) | Checklist interno iah-cli |

**No es un bug.** Son dos sistemas de scoring independientes con dominios distintos. El diagnóstico incluye una nota aclaratoria. La divergencia es intencional pero confusa para el lector no técnico. La nota debería ser más prominente.

---

## 9. COHERENCE VALIDATOR vs GATE COHERENCE (CAUSA RAÍZ PRECISA)

```python
# coherence_gate.py:158 — EL VALIDATOR SE INSTANCIA
self._validator = CoherenceValidator()

# coherence_gate.py:160-203 — PERO NUNCA SE LLAMA EN execute()
def execute(self, coherence_score, assessment_data=None):
    passed = coherence_score >= self.threshold  # ← Solo compara contra umbral
    # self._validator.validate() NUNCA ES INVOCADO
```

**El H10 FIX es un facade.** La docstring dice "H10 FIX: Unificado con CoherenceValidator como fuente única de verdad" pero la unificación nunca se implementó. El `_validator` existe como atributo (L158) pero tiene **cero usos** en `execute()`. El gate recibe `coherence_score` como parámetro externo y solo verifica `score >= 0.8`.

### Flujo real (desconectado)

```
CoherenceValidator.validate() → coherence_validation.json
    is_coherent: false
    errors: [whatsapp_verified, promised_assets_exist]
    
CoherenceGate.execute(score_externo=0.8261) → gate_report
    passed: true   ← IGNORA los 2 errores del validator
    status: PASSED
```

### Por qué diagnostic YAML y gate COINCIDEN (0.8261)

Ambos leen de la misma fuente: `asset_result.coherence_report.overall_score`:
- Diagnostic YAML ← L2448: `coherence_score=asset_result.coherence_report.overall_score`
- Gate assessment ← L2653: `"coherence_score": asset_result.coherence_report.overall_score`

Coinciden porque usan el mismo valor. Pero ese valor NO es el del validator — es el del orchestrator interno, que corre con datos post-generación.

---

## 10. ALIGNMENT: coherence_validator vs proposal_asset_alignment

```
coherence_validator._check_promised_assets_exist:
  score: 0.92 (1.0 si no hubiera whatsapp_button missing)
  passed: false
  errors: ["Assets no implementados: whatsapp_button"]

proposal_asset_alignment gate:
  alignment_percentage: 0.0%
  all_aligned: true
  low_quality_count: 7
  missing_count: 0
```

**No es contradicción — son fuentes de datos distintas:**
- Validator verifica `is_asset_implemented()` contra `asset_catalog.py` (catálogo estático)
- Gate verifica `generated_assets` reales contra `PROPOSAL_SERVICE_TO_ASSET` (contrato de servicios)

El validator no encuentra `whatsapp_button` como IMPLEMENTED → error. El gate encuentra `whatsapp_button` como `present_in_production` (ya existe en sitio) → no missing.

PROPOSAL_SERVICE_TO_ASSET tiene 8 entradas (verificado en código L20-29):
1. SEO Local → optimization_guide
2. Botón de WhatsApp → whatsapp_button
3. Schema Hotel → hotel_schema
4. Schema Organization → org_schema
5. Informe Mensual → monthly_report
6. Página de FAQ → faq_page
7. Meta Tags Sociales (Open Graph) → open_graph
8. Optimización para IA Generativa → llms_txt

---

## 11. NUEVOS HALLAZGOS (no en documento original)

### H1 [CRÍTICA] — H10 FIX es un facade

`CoherenceGate._validator` instanciado (L158) pero jamás llamado en `execute()` (L160-203). La docstring y los comentarios afirman unificación que nunca ocurrió. Patrón "signature-only wiring".

**Archivo**: `modules/quality_gates/coherence_gate.py:158`

### H2 [CRÍTICA] — OpenGraphGenerator hardcodea defaults de otro hotel en 3 lugares

`open_graph_generator.py:87,94,107` usan `.get('key', 'Amazilia Hotel Campestre')` como fallback. No es LLM hallucination — es código determinístico. Cuando el `hotel_data` recibido usa key `'name'` en vez de `'hotel_name'`, el fallback es literalmente otro hotel.

**Archivo**: `modules/asset_generation/open_graph_generator.py:87,94,107`

### H3 [ALTA] — 100% de assets con confidence=0.5

Los 7 assets del PROPOSAL_SERVICE_TO_ASSET (excluyendo whatsapp_button que fue skipped) tienen confidence=0.5. El gate `asset_confidence` emite WARNING pero no bloquea. El delivery es funcionalmente un placeholder.

### H4 [MEDIA] — evidence_tier B≠C entre financial_scenarios.json y diagnóstico

`financial_scenarios.json`: `evidence_tier: "B"`. Diagnóstico YAML: `financial_evidence_tier: "C"`. El tier real (adr=handler, occupancy=regional, direct_channel=default) es C. El JSON está inflado.

### H5 [MEDIA] — v4_complete_report.coherence_score (0.8467) no es trazable

`main.py:2955` asigna `pre_coherence_score` (~0.8053) pero el JSON muestra 0.8467. `pre_coherence_score` no se reasigna entre L2236 y L2955. El origen de 0.8467 es desconocido — posible corrupción por escritura concurrente o valor residual.

### H6 [BAJA] — conditional_generator llama métodos privados de OpenGraphGenerator

`conditional_generator.py:523` llama `generator._generate_html(generator._extract_og_data(...))` — métodos privados directamente en vez de `generator.generate()`. By-passes la lógica de escritura a archivo del generator público.

---

## 12. MATRIZ COMPLETA DE CAUSAS RAÍZ

| # | Issue | Causa raíz precisa | Archivo:Línea | Tipo |
|---|-------|-------------------|---------------|------|
| R1 | 5 coherence scores | `CoherenceGate.execute()` ignora `_validator`. Validator corre 2× (pre/post). v4_complete_report introduce 2 scores más | `coherence_gate.py:160`, `main.py:2228,2414,2955` | BUG |
| R2 | open_graph cross-hotel | `.get('hotel_name', 'Amazilia Hotel Campestre')` — default es otro hotel | `open_graph_generator.py:87` | BUG |
| R3 | open_graph URL cross-hotel | `.get('website', 'https://amaziliahotel.com/')` — default es otro hotel | `open_graph_generator.py:107` | BUG |
| R4 | local_content sin location | `hotel_data.get("city")` vacío, sin validación pre-interpolación | `local_content_generator.py` (vía LLM prompt) | BUG |
| R5 | all_aligned vs alignment% | `all_aligned = len(missing)==0` (cobertura), `alignment% = aligned/total` (calidad). Naming confuso, no bug lógico | `proposal_asset_alignment.py:76-85` | DESIGN |
| R6 | hotel_schema/org_schema vacíos | Input Tier C sin onboarding. No es bug del generador | Pipeline de datos | DATA |
| R7 | WhatsApp conflict no resuelto | `whatsapp_conflict_guide` es .md informativo, no desplegable. Sin pipeline de deploy | GAP-4 | GAP |
| R8 | GEO score divergencia | Dos sistemas independientes: GBP-based vs checklist interno. Intencional pero confuso | `v4_diagnostic_generator.py`, `geo_flow` | DESIGN |
| R9 | evidence_tier B≠C | Dos fuentes calculan tier con lógica diferente o en momentos distintos | `financial_scenarios.json` vs diagnostic YAML | BUG |
| R10 | CoherenceValidator vs alignment gate | Validator usa catálogo estático (`is_asset_implemented()`), gate usa `generated_assets` reales | `coherence_validator.py:517` vs `proposal_asset_alignment.py:149` | DESIGN |

---

## 13. SOLUCIONES MEJORADAS (NO implementar — para diseño de plan)

### S1 [P0] — Integrar realmente CoherenceValidator en CoherenceGate

```python
# coherence_gate.py — NUEVO método que SÍ usa el validator:
def execute_from_validator(self, diagnostic, proposal, assets,
                            validation_summary, generated_assets=None):
    report = self._validator.validate(
        diagnostic, proposal, assets, validation_summary,
        generated_assets=generated_assets
    )
    return CoherenceGateResult(
        coherence_score=report.overall_score,
        passed=report.is_coherent,  # ← del validator, no solo threshold
        errors=report.errors,
        checks=report.checks,
    )
```

**Cambios requeridos**:
1. `coherence_gate.py`: Nuevo método `execute_from_validator()` o modificar `execute()` para aceptar datos del validator
2. `main.py`: Pasar datos completos al gate en vez de solo `coherence_score` float
3. `main.py`: Eliminar `asset_result.coherence_report.overall_score` como fuente del gate — usar solo el validator
4. `v4_complete_report.json`: Unificar `coherence_score` y `coherence_score_post` en un solo campo del validator

**Garantía post-fix**: `coherence_validation.json.overall_score == gate_report.coherence.value == diagnostic_YAML.coherence_score`

### S2 [P0] — Eliminar defaults hardcodeados cross-hotel en OpenGraphGenerator

```python
# open_graph_generator.py:87 — REEMPLAZAR default 'Amazilia Hotel Campestre'
hotel_name = hotel_data.get('hotel_name') or hotel_data.get('name', '')
if not hotel_name or hotel_name.strip() == '':
    raise ValueError(
        f"open_graph_generator requiere hotel_name válido. "
        f"Keys recibidas: {list(hotel_data.keys())}"
    )

# Mismo patrón para L94, L107
rating = hotel_data.get('rating')
review_count = hotel_data.get('review_count') or hotel_data.get('reviews')
website_url = hotel_data.get('website_url') or hotel_data.get('website') or hotel_data.get('url', '')
```

**Cambios requeridos**:
1. `open_graph_generator.py:87`: Eliminar default 'Amazilia Hotel Campestre', validar explícitamente
2. `open_graph_generator.py:94`: Eliminar defaults 4.5 y 202
3. `open_graph_generator.py:107`: Eliminar default 'https://amaziliahotel.com/'
4. `conditional_generator.py:523`: Usar `generator.generate()` en vez de métodos privados

**Garantía post-fix**: `grep -c "Amazilia" output/*/open_graph/*.html` → 0

### S3 [P1] — Validación de location en LocalContentGenerator

```python
# Antes de pasar datos al LLM, validar location:
location = (hotel_data.get("city") or hotel_data.get("state") 
            or hotel_data.get("region") or "")
if not location or location.strip() == "":
    location = "Colombia"  # fallback genérico pero informativo
```

**Garantía post-fix**: `grep "Hotel en  -" output/*/local_content_page/*.md` → 0 matches

### S4 [P2] — Renombrar all_aligned → all_covered

```python
# proposal_asset_alignment.py:76
@property
def all_covered(self) -> bool:
    """True si todos los servicios están cubiertos (generado o en producción)."""
    return len(self.missing) == 0
```

Mantener `all_aligned` como alias deprecado para backward compatibility.

### S5 [P2] — Unificar evidence_tier en todo el delivery

El tier debe computarse UNA vez (basado en `financial_sources`) y propagarse a:
- `financial_scenarios.json.breakdown.evidence_tier`
- Diagnóstico YAML `financial_evidence_tier`
- Propuesta YAML (si aplica)

### S6 [P3] — Gate asset_confidence: BLOCKED cuando 100% assets son ESTIMATED

Si `asset_generation_report` muestra que TODOS los assets tienen confidence < 0.7, el gate debe emitir BLOCKED (no WARNING). Actualmente solo `tier_c_onboarding_required` bloquea, y es fácil de bypass.

---

## 14. MATRIZ DE PRIORIDAD (actualizada)

| Prioridad | Issue | Impacto | Archivos |
|-----------|-------|---------|----------|
| **P0** | Gate ↔ Validator desconectados (H10 FIX facade) | 5 scores contradictorios en cada delivery | `coherence_gate.py`, `main.py` |
| **P0** | Hardcoded defaults open_graph (3 lugares) | Contaminación cross-hotel en producción | `open_graph_generator.py` |
| **P1** | Location validation local_content | Contenido SEO inútil ("Hotel en  -") | `local_content_generator.py` |
| **P1** | evidence_tier B≠C | Inconsistencia documental ante el cliente | `financial_scenarios.json`, diagnostic generator |
| **P2** | all_aligned naming confuso | Reportes confunden al usuario | `proposal_asset_alignment.py` |
| **P2** | WhatsApp conflict sin deploy | Conflicto documentado pero no resuelto | Pipeline de deployment |
| **P3** | Gate asset_confidence muy permisivo | Delivery 100% placeholder pasa como WARNING | `publication_gates.py` |
| **P3** | conditional_generator usa métodos privados | By-passes file-writing del generator | `conditional_generator.py:523` |

---

## 15. GARANTÍA POST-FIX (10 verificaciones)

| Gate | Verificación | Estado actual | Target post-fix |
|------|-------------|---------------|-----------------|
| G1 | `coherence_validation.overall_score == gate.coherence.value` | ❌ 0.81 ≠ 0.8261 | ✅ Iguales |
| G2 | `diagnostic_YAML.coherence_score == gate.coherence.value` | ✅ 0.8261 = 0.8261 | ✅ Mantener |
| G3 | `v4_complete_report` sin scores duplicados ni inexplicables | ❌ 2 scores, 0.8467 no trazable | ✅ 1 score, trazable |
| G4 | `open_graph_meta.html` sin "Amazilia" | ❌ 1 match | ✅ 0 matches |
| G5 | `local_content_*.md` sin "Hotel en  -" | ❌ Match | ✅ 0 matches |
| G6 | `hotel_schema.json` con campos poblados | ❌ description y locality vacíos | ✅ Poblados (requiere onboarding) |
| G7 | `whatsapp_conflict_guide` con confidence ≥ 0.7 | ❌ 0.5 | ✅ ≥ 0.7 |
| G8 | `financial_scenarios.evidence_tier == diagnostic.financial_evidence_tier` | ❌ B ≠ C | ✅ Iguales |
| G9 | `CoherenceGate.execute()` llama a `_validator.validate()` | ❌ 0 llamadas | ✅ ≥ 1 llamada |
| G10 | Ningún generator con defaults hardcodeados de otro hotel | ❌ open_graph | ✅ 0 defaults cross-hotel |

---

## 16. MACRO-FASES PROPUESTAS (para sesión de diseño de plan)

### FASE-COH: Unificar CoherenceValidator ↔ CoherenceGate
- Eliminar facade H10 FIX, integrar validator en gate
- Unificar fuente de coherence_score en main.py
- Limpiar v4_complete_report.json (un solo score)
- **Archivos**: `coherence_gate.py`, `main.py` L2225-2250, L2653, L2955-2960
- **R3**: 3 tareas + 1 v4complete (3+1)

### FASE-DEFAULT: Eliminar hardcoded defaults cross-hotel
- open_graph_generator.py: eliminar 3 defaults 'Amazilia Hotel Campestre'
- conditional_generator.py: usar generate() público, no métodos privados
- Auditoría rápida: ¿hay otros generators con defaults de hotel específico?
- **Archivos**: `open_graph_generator.py`, `conditional_generator.py`
- **R3**: 3 tareas (3+0)

### FASE-CONTENT: Fix local_content + evidence_tier + all_aligned
- local_content: validación de location pre-LLM
- evidence_tier: unificar fuente de verdad
- all_aligned → all_covered (renombrar con alias deprecado)
- **Archivos**: `local_content_generator.py`, `financial_scenarios.json` writer, `proposal_asset_alignment.py`
- **R3**: 3 tareas (3+0)

### FASE-VERIFY: v4complete verification + asset_confidence gate hardening
- Ejecutar v4complete para Hotel Castilla Real
- Verificar G1-G10
- Hardening de gate asset_confidence (BLOCKED si 100% ESTIMATED)
- **R3**: 1 v4complete + 2 tareas (2+1)

---

## 17. PROMPT PARA SESIÓN DE DISEÑO DE PLAN

```
Carga el contexto validado en:
  .opencode/context/AUDITORIA_COHERENCIA_HOTELCASTILLAREAL_20260511.md

Diseña un plan de intervención por fases siguiendo phased_project_executor.md.
Usa las macro-fases de la Sección 16 como punto de partida.
Verifica R3 (máx 4 tareas o 3+1 comando largo por fase).
Incluye verificación post-fix con los 10 gates G1-G10 de la Sección 15.

No implementar — solo diseñar el plan en .opencode/plans/
```

---

## 18. PATHS RELEVANTES

| Recurso | Path |
|---------|------|
| Repo | `/mnt/c/Users/Jhond/Github/iah-cli` |
| Output delivery | `/mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/` |
| Diagnostic | `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260511_185023.md` |
| Proposal | `output/v4_complete/02_PROPUESTA_COMERCIAL_20260511_185033.md` |
| ZIP | `output/v4_complete/deliveries/hotelcastillareal_20260511.zip` |
| Validator | `modules/commercial_documents/coherence_validator.py` |
| CoherenceGate | `modules/quality_gates/coherence_gate.py` |
| OpenGraph generator | `modules/asset_generation/open_graph_generator.py` |
| Alignment | `modules/asset_generation/proposal_asset_alignment.py` |
| Main pipeline | `main.py` |

---

*Generado: 2026-05-11 19:05*
*Validado contra código vivo: 2026-05-11 20:15*
*Agent: Hermes — auditoría exhaustiva con trazado de código*
*Repo auditado: /mnt/c/Users/Jhond/Github/iah-cli*
*Estado: PLAN-READY — todas las claims verificadas, soluciones mejoradas, macro-fases propuestas*
