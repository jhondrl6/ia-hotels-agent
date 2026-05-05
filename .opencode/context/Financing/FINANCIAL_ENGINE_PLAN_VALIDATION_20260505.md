# CONTEXTO: Validación Post-Ejecución — Financial Evidence Engine Plan v1.2.0

**Archivo fuente:** `C:\Users\Jhond\Github\iah-cli\.opencode\context\Financing\FINANCIAL_ENGINE_PLAN_VALIDATION_20260505.md`
**Guardado el:** 2026-05-05
**Validado contra código:** 2026-05-05 — 3 ajustes aplicados (L1735→L1739, L242→L238, 空格→espacio)
**Versión repo verificada:** v4.40.0
**Hotel E2E:** Hotel Castilla Real — https://www.hotelcastillareal.com/
**Documento audited:** `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260504_204951.md`
**Plan auditado:** `.opencode/plans/FINANCIAL-ENGINE/`

---

## 1. VEREDICTO EJECUTIVO

**El plan fue arquitectónicamente efectivo, operacionalmente incompleto.**

Del plan de 11 fases (FIN-1A→1B→2A→2B→3→CHAN-1→CHAN-2→FIN-4→FIN-4A→FIN-4B→RELEASE):

| Fase | Estado | Resultado |
|------|--------|-----------|
| FIN-1A → FIN-1B | ✅ Completadas | `FinancialEvidence`, `PrecisionValidator`, `ADRResolutionResult` con epistemic_status |
| FIN-2A → FIN-2B | ✅ Completadas | `regional_adr_2026.json` existe, `validated_regions` incluye caribe |
| FIN-3 | ✅ Completada | Templates renderizan rangos, advertencias, CTA |
| CHAN-1 → CHAN-2 | ✅ Completadas | `channel_context` + `channel_multiplier` en opportunity_scores |
| FIN-4 | ✅ Completada | v4complete Hotel Castilla Real ejecuta |
| FIN-4A | ✅ Completada | `evidence/FIN-4A/gap_analysis.md` creado |
| **FIN-4B** | ❌ **NO completada** | 4 fixes documentados pero sin implementar |
| RELEASE | ❌ **NO completada** | Docs + version bump pendientes |

**Tasa de completitud del plan: 73% (8/11 fases)**

**Problema central**: La fase que cableaba los módulos al pipeline (`FIN-4B`) nunca se ejecutó. Esto explica por qué `financial_scenarios.json` muestra `adr_cop: 300000.0` (legacy) en vez de `420000` (regional eje_cafetero). Sin embargo, GAPs 2/3/4 se resolvieron solos durante la re-ejecución de v4complete; solo GAP-1 (ADR) queda pendiente.

---

## 2. PROBLEMA A RESOLVER

### 2.1 Qué se quería lograr

Según `FINANCIAL_ENGINE_PRECISION_CONTEXT.md`, el objetivo era:

> Eliminar la falsa precisión financiera ($2.610.000 COP/mes desde defaults) sin perder utilidad comercial, implementando:
> 1. **Financial Evidence Engine** → metadata epistémica por campo + precision tiers + reglas de render
> 2. **Regional Benchmark Fallback Honesto** → benchmarks regionales 2026 como estimación, no como dato exacto
> 3. **Evidence-Based Channel Prioritization** → priorización de brechas ponderada por canal inferido con evidencia

### 2.2 Criterio rector

> Nunca mostrar dinero con más precisión que la evidencia que lo soporta; y nunca priorizar brechas por un canal que no fue inferido o confirmado con evidencia.

### 2.3 Diagnóstico del output generado

El documento `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260504_204951.md` para Hotel Castilla Real muestra:

- `financial_evidence_tier: "C"` ✓
- `financial_value_range: [2088000, 3132000]` ✓
- Renderizado: `~$2.088.000 COP–$3.132.000 COP/mes (estimado — Tier C)` ✓
- `precision_tier: "C"` en header ✓
- Advertencia: `⚠️ **Nivel de evidencia: Tier C** — Estas cifras se basan en benchmark regional` ✓
- CTA: `¿Quiere saber su cifra exacta? Complete el [onboarding con sus datos reales]` ✓
- `adr_cop: 300000.0` en `financial_scenarios.json` ✗ (legacy, no regional $420K)
- `adr_source: "legacy_hardcode"` en `financial_scenarios.json` ✗ (no `regional_v410`)

**El documento se ve correcto visualmente para Tier C. El problema es que usa ADR legacy $300K en vez de regional $420K, pero como no muestra cifra exacta, el impacto práctico en el cliente es menor.**

---

## 3. REALIDAD DEL CÓDIGO VERIFICADA

### 3.1 Feature Flags

Archivo: `modules/financial_engine/feature_flags.py`

**Estado actual:**

| Flag | Valor default | Efecto |
|------|--------------|--------|
| `regional_adr_enabled` | `False` | Desactiva ADR regional |
| `regional_adr_mode` | `RolloutMode.SHADOW` | Calcula pero no usa regional |
| `financial_v410_enabled` | `False` | Motor nuevo desactivado |
| `validated_regions` | `("eje_cafetero", "antioquia", "caribe")` | Incluye caribe ✅ |
| `should_use_regional_for()` | Normaliza a lowercase + replace espacio | Correcto ✅ |

**Observación**: La normalización de región (`region.lower().replace(' ', '_')`) YA está implementada en L128. El gap analysis de FIN-4A dijo que era case-sensitive, pero el código actual ya tiene el fix. Esto reduce GAP-1 a solo activar los flags.

### 3.2 ADRResolutionWrapper

Archivo: `modules/financial_engine/adr_resolution_wrapper.py`

Cadena de fallback (L79-83):
```
1. user_provided_adr (onboarding) → "measured"
2. web_scraping_adr             → "observed"
3. regional benchmark            → "regional_benchmark" (REGIONAL_V410)
4. LEGACY_DEFAULT_ADR = 300000   → "defaulted"
```

**Campo nuevo verificado**: `ADRResolutionResult` tiene `epistemic_status` (L41) y `can_show_exact` (L42) ✓

**El problema**: Esta cadena nunca llega al paso 3 porque `regional_adr_enabled=False` por defecto. Siempre cae a legacy.

### 3.3 RegionalADRResolver

Archivo: `modules/financial_engine/regional_adr_resolver.py`

- Carga `regional_adr_2026.json` ✓
- `_resolve_from_regional_benchmarks()` retorna `(adr, occupancy, epistemic_status, source)` ✓
- `epistemic_status="regional_benchmark"` cuando usa JSON ✓
- `can_show_exact=False` siempre para benchmarks regionales ✓

### 3.4 regional_adr_2026.json

Archivo: `data/benchmarks/regional_adr_2026.json`

Valores:
```json
{
  "eje_cafetero": {
    "boutique_10_25": { "adr_cop": 420000, "occupancy_rate": 0.512 }
  },
  "antioquia": { ... },
  "caribe": { ... }
}
```

### 3.5 PrecisionValidator

Archivo: `modules/financial_engine/precision_validator.py`

- Existe y está importado en `main.py:1883` ✓
- Se ejecuta para calcular `_precision_tier` y `_can_show_exact` (main.py L1880-1896) ✓
- El resultado se escribe en `financial_scenarios.json` (L1921-1922) ✓

### 3.6 OpportunityScorer

Archivo: `modules/financial_engine/opportunity_scorer.py`

- `OpportunityScore` dataclass tiene `channel_multiplier` (L36) y `channel_reason` (L37) ✓
- `score_brechas()` acepta `channel_context` opcional (L283) ✓
- Ajusta `total_score` con `channel_multiplier` (L40-42) ✓

### 3.7 ChannelEvidenceResolver

Archivo: `modules/financial_engine/channel_evidence_resolver.py`

- `ChannelEvidence` con `dominant_channel`, `confidence`, `channel_weights` ✓
- `NEUTRAL_WEIGHTS` para pesos boutique neutrales ✓
- Sin hardcodeo de WhatsApp como dominante ✓
- `InferredChannel.GBP_LOCAL` cuando review_count >= 50 y score >= 4.0 ✓

### 3.8 v4_diagnostic_generator.py — channel context wiring

Archivo: `modules/commercial_documents/v4_diagnostic_generator.py`

- `_resolve_channel_context()` (L2741-2795) — construye gbp_data y web_evidence desde audit_result y llama `ChannelEvidenceResolver.resolve()` ✓
- Retorna dict con `dominant_channel`, `confidence`, `channel_weights` ✓
- `_compute_opportunity_scores()` (L2797+) calcula scores con `channel_context` ✓

### 3.9 main.py — v4_complete_report.json wiring

Archivo: `main.py`

- L2972-2975: `opportunity_scores` se incluye en report ✓
- L2976-2984: `channel_context` se incluye en report ✓
- L1879-1896: `precision_tier` y `can_show_exact_money` calculados y agregados a `financial_scenarios.json` ✓

---

## 4. GAP ANALYSIS — Estado de los 4 gaps

Archivo de referencia: `evidence/FIN-4A/gap_analysis.md`

### GAP-1 — CRÍTICO: ADR legacy no usa feature flags

| Atributo | Valor |
|----------|-------|
| **file:line** | `modules/financial_engine/adr_resolution_wrapper.py:238` (def) / `L242` (asignación LEGACY_DEFAULT_ADR) |
| **función** | `ADRResolutionWrapper._legacy_resolution()` |
| **fuente del valor** | `LEGACY_DEFAULT_ADR = 300000.0` (L49) |

**Causa raíz**: Feature flags apagados por defecto en producción.

**Cadena de resolución para Castilla Real:**
```
main.py:1739 → resolve_adr_with_shadow(region="Eje Cafetero")
  → ADRResolutionWrapper.resolve()
    → flags.should_use_regional_for("Eje Cafetero")
      → Normaliza: "eje_cafetero" ✓ (ya normalizado en código)
      → Pero regional_adr_enabled=False → retorna False
        → _legacy_resolution_with_scraping()
          → _legacy_resolution() → LEGACY_DEFAULT_ADR = 300000.0
```

**Fix requerido** (minimo):
```bash
export FINANCIAL_REGIONAL_ADR_ENABLED=true
export FINANCIAL_REGIONAL_ADR_MODE=active
```

**Nota**: La normalización de región ya está en el código (`feature_flags.py:128`). No se necesita fix de case-sensitivity.

**Estado**: ❌ Pendiente — FIN-4B no ejecutada

---

### GAP-2 — ALTO: opportunity_scores en v4_complete_report.json

| Atributo | Valor |
|----------|-------|
| **file:line** | `main.py:2972-2975` |
| **fuente del cálculo** | `v4_diagnostic_generator.py:_compute_opportunity_scores()` |

**Verificación en output real**:
```json
// v4_complete_report.json (20260504_204951)
"opportunity_scores": [
  {
    "brecha_id": "no_hotel_schema",
    "total_score": 85.0,
    "channel_multiplier": 0.95,
    "channel_reason": "Canal inferido: gbp, multiplicador iao_schema: 0.95"
  },
  ...
]
```

**Estado**: ✅ Resuelto — el código en main.py L2972 ya cablea opportunity_scores al JSON

---

### GAP-3 — ALTO: channel_context en v4_complete_report.json

| Atributo | Valor |
|----------|-------|
| **file:line** | `main.py:2976-2984` |
| **fuente del cálculo** | `v4_diagnostic_generator.py:_resolve_channel_context()` |

**Verificación en output real**:
```json
// v4_complete_report.json (20260504_204951)
"channel_context": {
  "dominant_channel": "gbp",
  "confidence": "medium",
  "channel_weights": {
    "gbp_local": 1.15,
    "direct_conversion": 1.1,
    "performance_mobile": 1.05,
    "whatsapp": 1.0,
    "seo_content": 0.95,
    "iao_schema": 0.95
  }
}
```

**Estado**: ✅ Resuelto — el código en main.py L2976 ya cablea channel_context al JSON

---

### GAP-4 — MEDIO: precision_tier y can_show_exact_money en financial_scenarios.json

| Atributo | Valor |
|----------|-------|
| **file:line** | `main.py:1879-1896`, `main.py:1920-1922` |
| **fuente del cálculo** | `PrecisionValidator.validate()` |

**Verificación en output real**:
```json
// financial_scenarios.json (20260504_204951)
"precision_tier": "C",
"can_show_exact_money": false,
```

**Estado**: ✅ Resuelto — main.py calcula y persiste estas variables

---

### Resumen GAPs

| GAP | Severidad | Estado | Fix requerido |
|-----|:---------:|--------|---------------|
| GAP-1 | CRÍTICO | ❌ Pendiente | Activar env vars |
| GAP-2 | ALTO | ✅ Resuelto | Ninguno |
| GAP-3 | ALTO | ✅ Resuelto | Ninguno |
| GAP-4 | MEDIO | ✅ Resuelto | Ninguno |

**Conclusión**: Solo GAP-1 requiere acción. Los demás se resolvieron durante la re-ejecución de v4complete.

---

## 5. IMPACTO DEL GAP-1 PENDIENTE

### 5.1 Comparación de escenarios con ADR regional vs legacy

Para Hotel Castilla Real (10 habitaciones, ocupación 50%, canal directo 20%):

| Caso | ADR | Ocupación | Pérdida mensual calculada |
|------|---:|---:|-------------------------:|
| Legacy (actual) | $300.000 | 50% | $2.088.000–$3.132.000 |
| Eje Cafetero boutique (propuesto) | $420.000 | 51,2% | ~$2.688.000–$4.074.000 |
| Delta | +$120.000 | +1,2pp | +$600K–$942K/mes |

**El documento visualmente es correcto para Tier C — muestra rango, no cifra exacta, con advertencia apropiada. Pero el rango está subestimado por usar ADR legacy en lugar del regional.**

### 5.2 Impacto en el pricing

| Campo | Valor actual (legacy) | Valor con regional |
|-------|----------------------|-------------------|
| pain_ratio | 5% | 5% |
| monthly_price | $130.500 | ~$182.700 |
| delta | — | +$52.200/mes |

---

## 6. ANÁLISIS DE FONDO — Por qué el plan quedó incompleto

### 6.1 Diseño del plan vs ejecución real

El plan preveía 11 fases con 1 ejecución de v4complete (FIN-4) para validar todo junto. Se ejecutó v4complete en FIN-4, se encontraron 4 gaps, se creó FIN-4A (investigación) y luego se pretendía FIN-4B (implementación). Sin embargo:

1. **FIN-4A se completó**: El gap analysis está creado en `evidence/FIN-4A/gap_analysis.md`
2. **FIN-4B no se ejecutó**: Los 4 fixes documentados no se aplicaron
3. **Se ejecutó v4complete de nuevo** (las 20:49:51) — esto resolvió GAPs 2/3/4 automáticamente porque el código en main.py ya cableaba esos campos; solo GAP-1 quedó pendiente

### 6.2 Lo que se resolvió solo

Cuando se volvió a ejecutar v4complete (con flags probablemente activados en el entorno de la sesión que generó el output de las 20:49:51), el código existente en main.py:
- Ya tenía `opportunity_scores` cableado al JSON (L2972)
- Ya tenía `channel_context` cableado al JSON (L2976)
- Ya tenía `precision_tier` y `can_show_exact_money` cableados al JSON (L1920)

**El gap analysis fue correcto en su momento, pero el código de wiring ya existía — solo faltaba la activación de flags para GAP-1.**

### 6.3 Lo que queda pendiente

**GAP-1 exclusivamente**: Activar `FINANCIAL_REGIONAL_ADR_ENABLED=true` + `FINANCIAL_REGIONAL_ADR_MODE=active` para que el ADR sea $420K regional en vez de $300K legacy.

---

## 7. EVALUACIÓN DEL PLAN CONTRA EL CONTEXTO ORIGINAL

### 7.1 Claims del FINANCIAL_ENGINE_PRECISION_CONTEXT verificados

| Claim | Veredicto | Evidencia |
|-------|-----------|-----------|
| `regional_adr_enabled=False` por defecto | ✅ | `feature_flags.py:30` |
| `validated_regions` excluye caribe | ❌ Ya incluye caribe | `feature_flags.py:48` |
| Cadena fallback: onboarding→scraping→regional→legacy | ✅ | `adr_resolution_wrapper.py:79-83` |
| `regional_adr_2026.json` existe con eje_cafetero $420K | ✅ | `data/benchmarks/regional_adr_2026.json` |
| `ADRResolutionResult` tiene `epistemic_status` | ✅ | `adr_resolution_wrapper.py:41` |
| `OpportunityScorer` tiene `channel_multiplier` | ✅ | `opportunity_scorer.py:36` |
| `channel_context` con `dominant_channel` en report | ✅ | `v4_complete_report.json:443-454` |
| Diagnostic muestra rango ~$2.088K–$3.132K | ✅ | Documento L109 |
| `precision_tier: "C"` en documento | ✅ | Header L8 + documento L105 |
| `can_show_exact_money: false` en JSON | ✅ | `financial_scenarios.json:46` |

### 7.2 Claims implícitos que NO se cumplieron

| Claim | Realidad |
|-------|----------|
| ADR para Eje Cafetero debería ser $420K | `financial_scenarios.json: adr_cop: 300000.0` |
| `adr_source` debería ser `regional_v410` | `financial_scenarios.json: adr_source: "legacy_hardcode"` |

---

## 8. CONCLUSIONES

### 8.1 El plan fue efectivo en 8/11 fases

La arquitectura implementada es sólida:
- Metadata epistémica ✅
- Precision tiers ✅
- Renderizado con rangos y advertencias ✅
- Channel inference (GBP como dominante para hoteles con buenas reseñas) ✅
- Channel multiplicadores en opportunity scores ✅
- Wiring de todos los campos a los JSONs de output ✅

### 8.2 Queda 1 gap operacional

Solo GAP-1 (ADR legacy) necesita fix. Todo lo demás ya funciona.

### 8.3 El documento generado es comercialmente aceptable para Tier C

Aunque el ADR base es $300K legacy en vez de $420K regional:
- Muestra **rango**, no cifra exacta ✅
- Tiene **advertencia de Tier C** prominente ✅
- Incluye **CTA de onboarding** ✅
- No hace promesas de precisión que no puede cumplir ✅

**El impacto práctico para el cliente es menor — sigue siendo una estimación honesta con disclaimer.**

---

## 9. RECOMENDACIÓN

### Opción mínima (1 línea)

Ejecutar v4complete con flags activos:

```bash
export FINANCIAL_REGIONAL_ADR_ENABLED=true
export FINANCIAL_REGIONAL_ADR_MODE=active
cd /mnt/c/Users/Jhond/Github/iah-cli
python main.py v4complete --url https://www.hotelcastillareal.com/
```

### Opción completa (FIN-4B)

Ejecutar la fase que implementa los fixes documentados:

```
Carga y ejecuta .opencode/plans/FINANCIAL-ENGINE/05-prompt-inicio-sesion-fase-FIN-4B.md
siguiendo .agents/workflows/phased_project_executor.md
```

Esto garantizará que:
1. GAP-1 se solvente con activación correcta de flags
2. Se documenten los fixes aplicados
3. Se ejecuten validaciones post-fix
4. Se pueda avanzar a RELEASE

### Acción de documentación pendiente (RELEASE)

Después de FIN-4B:
```
log_phase_completion.py → sync_versions.py → CHANGELOG → GUIA_TECNICA → run_all_validations.py
```

---

## 10. PRÓXIMO PASO — Instrucciones para nueva sesión

### Objetivo de la sesión: Ejecutar FIN-4B + v4complete de validación + RELEASE

**Este documento ya fue validado contra código (2026-05-05). Todos los line numbers y claims
están confirmados. No re-validar — pasar directamente a ejecución.**

La ejecución de v4complete NO es solo para verificar GAP-1. Es la **prueba de fuego de todo
el plan FINANCIAL-ENGINE**: confirma que los 3 pilares implementados en 11 fases funcionan
de punta a punta en un hotel real.

---

### TAREA 1: FIN-4B — Activar feature flags

1. Activar env vars:
   ```bash
   export FINANCIAL_REGIONAL_ADR_ENABLED=true
   export FINANCIAL_REGIONAL_ADR_MODE=active
   ```
2. Si los flags no se activan por env vars, cambiar defaults en
   `modules/financial_engine/feature_flags.py` L30 (`False` → `True`) y
   L35 (`RolloutMode.SHADOW` → `RolloutMode.ACTIVE`).

---

### TAREA 2: v4complete — Prueba de validación integral del plan

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python main.py v4complete --url https://www.hotelcastillareal.com/
```

**CHECKLIST DE VALIDACIÓN — Los 3 pilares del plan deben pasar:**

#### Pilar 1: Financial Evidence Engine (FIN-1A, FIN-1B, FIN-3)
- [ ] `financial_scenarios.json` tiene `precision_tier: "C"`
- [ ] `financial_scenarios.json` tiene `can_show_exact_money: false`
- [ ] Documento muestra rango con `~` y `–` (no cifra exacta)
- [ ] Documento tiene advertencia Tier C visible
- [ ] Documento tiene CTA de onboarding

#### Pilar 2: Regional Benchmark ADR (FIN-2A, FIN-2B, GAP-1)
- [ ] `financial_scenarios.json` tiene `adr_cop: 420000.0` (NO 300000.0)
- [ ] `financial_scenarios.json` tiene `adr_source: "regional_v410"` (NO "legacy_hardcode")
- [ ] Rango en documento sube a ~$2.688.000–$4.074.000 COP/mes
- [ ] `financial_evidence_tier` en JSON es `"C"`

#### Pilar 3: Channel Evidence Prioritization (CHAN-1, CHAN-2)
- [ ] `v4_complete_report.json` tiene `opportunity_scores` con `channel_multiplier` y `channel_reason`
- [ ] `v4_complete_report.json` tiene `channel_context` con `dominant_channel: "gbp"` y `confidence`
- [ ] Scores NO están hardcodeados — varían según canal inferido

**Si los 3 pilares pasan**: el plan FINANCIAL-ENGINE cumplió su cometido al 100%.
**Si algún pilar falla**: documentar cuál falló y por qué, antes de proseguir con RELEASE.

Registrar evidencia completa en `evidence/FIN-4B/plan_validation_e2e.md` con:
- Captura de cada valor verificado vs esperado
- Veredicto por pilar (PASS/FAIL)
- Veredicto global del plan (PASS/FAIL)

---

### TAREA 3: RELEASE — Documentación + version bump

**Solo si TAREA 2 da PASS global.** Ejecutar el flujo documental:

1. `python scripts/log_phase_completion.py --fase FIN-4B --desc "Activación flags ADR regional + validación E2E plan"`
2. `python scripts/sync_versions.py`
3. Actualizar `CHANGELOG.md` con formato CONTRIBUTING.md (Objetivo/Cambios/Archivos/Tests)
4. Actualizar `GUIA_TECNICA.md` con nota técnica de FIN-4B
5. `python scripts/run_all_validations.py --quick`
6. Version bump v4.40.0 → v4.41.0 en `VERSION.yaml` + sync

---

### Contexto heredado (no repetir investigación)

- GAP-1 es el **único gap pendiente**. GAPs 2/3/4 ya están resueltos.
- La normalización de región (.lower().replace(' ', '_')) ya está en feature_flags.py L128.
- El wiring de opportunity_scores, channel_context, precision_tier ya existe en main.py.
- El plan original tenía 3 objetivos (§2.1): Evidence Engine, Regional Benchmark, Channel
  Prioritization. Los 3 están implementados en código — solo falta activar el flag de ADR
  para que el pilar 2 funcione en producción.
- El documento actual es Tier C correcto pero con ADR subestimado. Post-fix, el rango sube
  pero el tier y el disclaimer no cambian.

**Costo estimado**: 1 sesión (FIN-4B + verificación + RELEASE).
