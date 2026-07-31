# Plan Maestro: EVIDENCE-TIER-FALSE-CONFIDENCE-IAO — Refactorizacion Evidence Tier + Gate + Honestidad IAO

> **Origen**: CONTEXT-EVIDENCE-TIER-FALSE-CONFIDENCE-IAO-2026-07-30.md (validado contra codigo vivo)
> **Version objetivo**: v4.68.0
> **Version actual**: v4.67.0 (ONBOARDING-INJECTION-GAP completado 2026-07-29)
> **Hotel de referencia**: Zi One Luxury (https://zione.co/)
> **Sesiones estimadas**: 6 fases (5 implementacion + 1 RELEASE)
> **Estimacion total**: ~10-12h (corregida de 8-10h tras hallazgos NP1-NP8)
> **Auditoria**: Validado contra codigo vivo 2026-07-31. 12/12 hallazgos del plan confirmados. 8 hallazgos nuevos (NP1-NP8) detectados y agregados al alcance. Ver §15 ampliada.

---

## Resumen Ejecutivo

El documento v4complete del 07-30 para Zi One Luxury tiene una **contradiccion interna**: el CTA honesto (linea 84) dice "conecte GA4", pero el disclaimer de tier (linea 215) afirma "Basado en Google Analytics y Search Console verificados". La misma pagina del documento dice 3 cosas contradictorias sobre GA4.

**Causa raiz**: Dos rutas de codigo que no comparten fuente de verdad:
- Ruta A (CTA honesto): consulta `analytics_data.use_ga4` → False → SABE que GA4 no esta conectado
- Ruta B (Tier falso): `_determine_evidence_tier()` asigna Tier A con >=2 fuentes verificadas, **NUNCA verifica GA4/GSC**

**Evidencia en codigo vivo** (verificado 2026-07-31):
- `scenario_calculator.py:480-504`: `_determine_evidence_tier()` asigna Tier A sin check de `ga4_enabled`
- `data_structures.py:135`: `EvidenceTier.A.disclaimer` hardcodea "GA4 + Search Console verificados"
- `main.py:2099`: relationship text hardcodeado "evidence_tier B" (siempre, sin importar el tier real)
- `v4_proposal_generator.py:944`: `has_onboarding='False'` hardcodeado, nadie lo sobreescribe
- `v4_proposal_generator.py:586`: `getattr(pricing_result, 'is_onboarding', False)` — fallback silencioso a False porque `PricingResolutionResult` NO tiene el atributo (`pricing_resolution_wrapper.py:31-41`)
- **`commercial_gate.py:80,601-639`**: `CG-TIER-CONSISTENCY` YA EXISTE pero solo compara frontmatter vs texto. NO verifica GA4/GSC. Esta en WARNING (no bloquea).
- **MANIFEST** se genera en `modules/delivery/delivery_packager.py:145` (NO `main.py:3038` como decia el plan original)

---

## Bugs y Hallazgos (del Contexto + Live Code Verification)

### Hallazgos originales del plan (12/12 confirmados contra codigo vivo)

| ID | Severidad | Descripcion | Archivos | Fase |
|----|-----------|-------------|----------|------|
| **H1** | **CRITICA** | `_determine_evidence_tier()` asigna Tier A sin verificar GA4/GSC | `scenario_calculator.py`, `data_structures.py` | **FASE-1** |
| **H2** | **ALTA** | `EvidenceTier.A.disclaimer` miente: "GA4+GSC verificados" sin verificacion real | `data_structures.py:135` | **FASE-1** |
| **H3** | **ALTA** | `has_onboarding='False'` hardcodeado en propuesta, 0 overrides en codebase | `v4_proposal_generator.py:944`, `main.py` | **FASE-2** |
| **H4** | **ALTA** | Propuesta dice 3 tiers diferentes (A, B, C) en 3 lineas consecutivas | `v4_proposal_generator.py` disclaimer | **FASE-2** |
| **H5** | **MEDIA** | `main.py:2099` relationship text hardcodeado "evidence_tier B" | `main.py` | **FASE-2** |
| **H6** | **MEDIA** | `precision_tier` en JSON pero NO visible en template | `v4_diagnostic_generator.py`, template | **FASE-2** |
| **H7** | **MEDIA** | Template Tiers legend no incluye B+ y es hardcodeado | `diagnostico_v6_template.md:161-163` | **FASE-2** |
| **H8** | **ALTA** | Sin gate que detecte Tier A + GA4 no configurado (CG-TIER-CONSISTENCY existente no cubre esto) | `commercial_gate.py`, `delivery_quality.py` | **FASE-3** |
| **H9** | **MEDIA** | MANIFEST.json sin metadata de calidad (evidence_tier, precision_tier, ga4_available) | `modules/delivery/delivery_packager.py:145` (NO main.py:3038) | **FASE-3** |
| **H10** | **MEDIA** | Tres sistemas de precision_tier no unificados (enum, string, validator) | `financial_evidence.py`, `no_defaults_validator.py`, `main.py` | **DEUDA (documentada, no implementa)** |
| **H11** | **BAJA** | `_get_adr_from_benchmarks()` parcialmente obsoleto (H1-FIX ya aplicado) | `v4_proposal_generator.py:1907` | **NO ACCION (ya fixed)** |
| **H12** | **INFRA** | Service account Google Cloud no creada → CTA "conecte GA4" no accionable | Google Cloud Console | **OUT OF PLAN (user action)** |

### Hallazgos nuevos NP1-NP8 detectados en auditoria 2026-07-31

| ID | Severidad | Descripcion | Archivos | Fase |
|----|-----------|-------------|----------|------|
| **NP1** | **CRITICA** | `hook_pdf_generator.py:509` `valid_tiers = {"A", "B", "C"}` — B_PLUS sera rechazado y forzado a B con WARN | `modules/commercial_documents/hook_pdf_generator.py:509` | **FASE-1 (T0)** |
| **NP2** | **ALTA** | `publication_gates.py:399` `tier_message` logica condicional rota — else branch siempre dice "Tier C evidence" independientemente del tier real | `modules/quality_gates/publication_gates.py:399` | **FASE-1 (T0)** |
| **NP3** | **ALTA** | `tests/test_financial_breakdown.py:107-116` assertions asumen solo A/B/C — romperan con B_PLUS | `tests/test_financial_breakdown.py` | **FASE-1 (T0b) + FASE-4** |
| **NP4** | **ALTA** | `v4_diagnostic_generator.py:1043` `evidence_tier: str = "A"` default — bug latente: si `financial_breakdown` is None, default a A (el bug que estamos corrigiendo) | `modules/commercial_documents/v4_diagnostic_generator.py:1043` | **FASE-1 (T0b)** |
| **NP5** | **MEDIA** | `v4_proposal_generator.py:586` `getattr(pricing_result, 'is_onboarding', False)` — fallback silencioso a False porque `PricingResolutionResult` NO tiene atributo `is_onboarding` | `v4_proposal_generator.py:586`, `pricing_resolution_wrapper.py:31-41` | **FASE-2 (T0)** |
| **NP6** | **MEDIA** | Plan original indica `main.py:3038` para MANIFEST pero la realidad es `modules/delivery/delivery_packager.py:145` | Documentacion del plan | **CORREGIDO en este plan** |
| **NP7** | **ALTA** | Plan FASE-3 T1 propone gate con `os.getenv('GA4_PROPERTY_ID')` — global, NO respeta arquitectura per-hotel actual (`main.py:2304` `ga4_hotel_property_id` per-hotel via CLI flag) | `modules/quality_gates/commercial_gate.py` | **FASE-3 (T1 rediseñado)** |
| **NP8** | **MEDIA** | Plan no incluye corrida de control para hoteles SIN onboarding tras el fix — riesgo de regresion no testeado (leccion previa §6 "Regresion en hoteles sin onboarding" no verificada) | Test strategy | **FASE-5 (T0 nueva)** |

---

## Fases del Plan

| Fase | Titulo | Complejidad | Tareas | Ejecucion | delegate_task |
|------|--------|-------------|--------|-----------|---------------|
| **FASE-1** | Root Cause: Evidence Tier Honesto + B_PLUS + Downstream Consumers | **ALTA** ⚠️ | 6 (4 + T0 + T0b) | DIRECTA | ❌ WSL import cascade |
| **FASE-2** | Proposal + Template Honesty + PricingResolution.is_onboarding | MEDIA | 5 (4 + T0 fix NP5) | DIRECTA | ❌ WSL import cascade |
| **FASE-3** | Quality Gate (per-hotel) + Delivery Enrichment | MEDIA | 3 | ✅ COMPLETADA | ❌ WSL import cascade |
| **FASE-4** | Tests + Regression + Update Existing Tests | MEDIA | 4 (3 + T0 NP3) | ✅ COMPLETADA | ❌ WSL import cascade |
| **FASE-5** | v4complete Zi One + Control Sin Onboarding + Post-Implementation | MEDIA | 5 (1+3 + T0 control) | MIXTO | ✅ v4complete subagent |
| **FASE-RELEASE** | Version v4.68.0 + Docs Cascade | BAJA | 4 | SUBAGENTE | ✅ Solo YAML/MD |

### delegate_task Viability Matrix

| Fase | Viable? | Razon |
|------|---------|-------|
| FASE-1 | ❌ NO | Edita 6+ archivos con imports de modulo → WSL import cascade. DIRECTA requerido. |
| FASE-2 | ❌ NO | Edita generators + templates + PricingResolutionResult → necesita imports. DIRECTA requerido. |
| FASE-3 | ❌ NO | Edita quality_gates + delivery_packager.py → imports. DIRECTA requerido. |
| FASE-4 | ❌ NO | pytest desde venv Windows → subagent en WSL no puede importar. DIRECTA requerido. |
| FASE-5 | ✅ MIXTO | v4complete → delegate_task (timeout=900). Analisis post → main agent (necesita contexto completo). |
| FASE-RELEASE | ✅ YES | Solo edita YAML/MD + scripts. Sin imports de modulo. 18 tool calls, ~4 min tipico. |

---

## Fase de Mayor Complejidad Tecnica: FASE-1

**Razon**: Cambia la logica CORE de tiering que afecta a TODOS los hoteles. Modifica 6 archivos interconectados (enum + dataclass + calculator + orchestrator + 3 consumers downstream). Cualquier error rompe el tiering para hoteles CON GA4 real O introduce regression en hotels sin onboarding.

**Factores de riesgo**:
1. **Cross-module signature change**: `_determine_evidence_tier()` cambia firma → TODOS los callers deben actualizarse
2. **Regression risk**: Hoteles con GA4 real deben seguir recibiendo Tier A
3. **Nuevo enum value**: `B_PLUS` debe propagarse a TODOS los consumers downstream (NP1, NP2, NP3 son los bloqueadores)
4. **Dataclass extension**: `HotelFinancialData` +2 campos → impacto en serializacion/JSON
5. **Default conservador vs. liberal**: NP4 detecta default "A" en `_build_financial_placeholders` — debe cambiar a "C"

**Mitigaciones**:
- Pre-patch grep exhaustivo de TODOS los consumers de `_determine_evidence_tier`, `EvidenceTier`, `hotel_data.evidence_tier`
- T0 (fix NP1, NP2, NP4) ANTES de T1-T4 — limpiar consumers antes de introducir B_PLUS
- T0b (update test_financial_breakdown.py) — necesario porque tests existentes rompen con B_PLUS
- Test regression suite ANTES de empezar (baseline de tests pasando)
- Fix en orden: enum → consumers downstream → dataclass → calculator → orchestrator

---

## Dependencias entre Fases

```
FASE-1 (Root Cause + Downstream Consumers — 6 archivos)
  └─► FASE-2 (Requiere B_PLUS enum + downstream limpio)
       └─► FASE-3 (Requiere tier corregido para disenar gate)
            └─► FASE-4 (Requiere codigo estable para escribir/actualizar tests)
                 └─► FASE-5 (Requiere todos los fixes + tests pasando + control sin onboarding)
                      └─► FASE-RELEASE
```

---

## Archivos Afectados (17 archivos, ordenados por fase)

### FASE-1 (6 archivos — incluye T0/T0b de NP1-NP4)

| # | Archivo | Cambio |
|---|---------|--------|
| 1 | `modules/commercial_documents/data_structures.py` | Agregar `B_PLUS` al enum `EvidenceTier` + nuevo disclaimer |
| 2 | `modules/commercial_documents/hook_pdf_generator.py` | **T0 NP1**: `valid_tiers = {"A", "B+", "B", "C"}` |
| 3 | `modules/quality_gates/publication_gates.py` | **T0 NP2**: `tier_message` logica dinamica para todos los tiers |
| 4 | `modules/commercial_documents/v4_diagnostic_generator.py` | **T0b NP4**: `evidence_tier: str = "C"` default (no "A") |
| 5 | `tests/test_financial_breakdown.py` | **T0b NP3**: agregar assertions para B_PLUS.disclaimer |
| 6 | `modules/financial_engine/scenario_calculator.py` | `HotelFinancialData` + `ga4_enabled`/`gsc_enabled`. `_determine_evidence_tier()` recibe y usa estos flags |
| 7 | `main.py` | Construccion de `HotelFinancialData`: pasar `ga4_enabled=ga4_available`, `gsc_enabled=gsc_available` |

### FASE-2 (5 archivos — incluye T0 de NP5)

| # | Archivo | Cambio |
|---|---------|--------|
| 8 | `modules/commercial_documents/v4_proposal_generator.py` | `has_onboarding` dinamico (no hardcodeado). Disclaimer condicional al tier |
| 9 | `modules/commercial_documents/v4_proposal_generator.py` | **T0 NP5**: Eliminar fallback silencioso `getattr(pricing_result, 'is_onboarding', False)` — agregar parametro `has_onboarding` a `generate()` |
| 10 | `main.py` | Pasar `has_onboarding = str(onboarding_data is not None)` al proposal generator. Fix relationship text en :2099 |
| 11 | `modules/commercial_documents/v4_diagnostic_generator.py` | Exponer `precision_tier` en placeholders |
| 12 | `modules/commercial_documents/templates/diagnostico_v6_template.md` | Agregar `${precision_tier}`, actualizar legend con B+ |

### FASE-3 (3 archivos — corregido por NP6 y NP7)

| # | Archivo | Cambio |
|---|---------|--------|
| 13 | `modules/quality_gates/commercial_gate.py` | Nuevo gate `CG-EVIDENCE-TIER-CONSISTENCY` — **recibe `ga4_available`/`gsc_available` como parametros** (NO `os.getenv`) |
| 14 | `modules/quality_gates/delivery_quality.py` | Agregar a checklist pre-delivery |
| 15 | `modules/delivery/delivery_packager.py` | **CORREGIDO**: enriquecer MANIFEST con `quality_metadata` (en este archivo, NO main.py) |

### FASE-4 (1+ directorio)

| # | Directorio | Cambio |
|---|-----------|--------|
| 16 | `tests/` | Tests para evidence_tier, proposal honesty, gate consistency, regression |

### FASE-5 (no archivos de codigo — incluye T0 control)

| # | Accion | Descripcion |
|---|--------|-------------|
| 17 | T0 **NUEVA** | v4complete para hotel_test_001 (sin onboarding) — verificar que NO hay regresion a Tier C default |
| 18 | v4complete Zi One | Ejecutar para Zi One Luxury (https://zione.co/) |
| 19 | Analisis | Verificar matriz de 12 hallazgos originales + 8 hallazgos nuevos NP1-NP8 + generar lecciones aprendidas |

---

## Condiciones para el Fix (del Contexto §5)

1. **Fuente de verdad unificada** (FASE-1): `_determine_evidence_tier()` debe consultar `ga4_enabled`/`gsc_enabled`
2. **Tier honesto** (FASE-1): Tier A solo con GA4+GSC real. Sin ellos → max B+
3. **Consumers downstream limpios** (FASE-1 T0/T0b): NP1-NP4 deben corregirse ANTES de introducir B_PLUS para evitar regression silenciosa
4. **Default conservador** (FASE-1 T0b NP4): Cuando no hay financial_breakdown, default a C (no A)
5. **Gate de validacion** (FASE-3): Bloquear delivery si Tier A + GA4 no configurado — **con params per-hotel** (no env vars globales)

---

## Restriccion Arquitectonica (Contexto §4)

**El hotel DEBE suministrar credenciales GA4/GSC.** El sistema NO puede acceder autonomamente:
- `GA4_PROPERTY_ID` (per-hotel via CLI flag `--ga4-property-id`, NO global)
- `GSC_SITE_URL` (per-hotel)
- Service account → debe ser agregada como usuario en GA4 y verificada en GSC

Esto es inherente al modelo de seguridad de Google. Tier A real es cliente-gateado. **El gate FASE-3 debe respetar arquitectura per-hotel (NP7)**.

---

## DoD Global (Definition of Done)

- [ ] FASE-1: `_determine_evidence_tier()` nunca devuelve A sin GA4+GSC. B+ existe con disclaimer honesto. Consumers downstream (hook_pdf_generator, publication_gates, v4_diagnostic_generator default) NO rompen con B+. Tests pre-existentes (test_financial_breakdown.py) actualizados.
- [ ] FASE-2: Propuesta no miente sobre tiers. `has_onboarding` refleja realidad (param pasado correctamente, no fallback silencioso). `precision_tier` visible.
- [ ] FASE-3: `CG-EVIDENCE-TIER-CONSISTENCY` recibe `ga4_available`/`gsc_available` como params (per-hotel) y bloquea delivery si Tier A + !GA4. MANIFEST enriquecido en `delivery_packager.py` (NO main.py).
- [ ] FASE-4: Tests unitarios + integracion + gate + actualizacion de tests pre-existentes. Regression suite verde.
- [ ] FASE-5: v4complete Zi One genera Tier B+ (no A). v4complete hotel_test_001 (sin onboarding) genera Tier C sin regresion. 20/20 hallazgos verificados (12 originales + 8 nuevos NP1-NP8). Analisis completado.
- [ ] FASE-RELEASE: v4.68.0 tagged. CHANGELOG consolidado. Docs sincronizados.

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Fix rompe tiering para hoteles con GA4 real | BAJA | ALTO | Test con `ga4_enabled=True + gsc_enabled=True` debe devolver A |
| B_PLUS no propagado a consumers downstream | ALTA | CRITICO | T0/T0b de FASE-1 limpian NP1-NP4 ANTES de introducir B_PLUS |
| CG-EVIDENCE-TIER-CONSISTENCY usa env vars globales | MEDIA | ALTO | T1 rediseñado: recibe params per-hotel (NP7) |
| MANIFEST no se enriquece (ubicacion incorrecta) | BAJA | MEDIO | NP6 corregido: enrichment en `delivery_packager.py`, NO main.py |
| Test pre-existentes rompen con B_PLUS | ALTA | ALTO | T0b NP3 actualiza `tests/test_financial_breakdown.py` |
| Default "A" en diagnostic generator (NP4) | MEDIA | ALTO | T0b NP4 cambia default a "C" (conservador) |
| has_onboarding fallback silencioso (NP5) | ALTA | ALTO | T0 NP5 elimina fallback, agrega param |
| Regresion en hoteles sin onboarding | ALTA | MEDIO | T0 FASE-5: v4complete hotel_test_001 verifica no-regresion |
| Service account GCP no existe → CTA no accionable | ALTA | MEDIO | Documentado como OUT OF PLAN. User debe crear service account. |
| v4complete Zi One timeout (900s) | MEDIA | BAJO | delegate_task con timeout=900 + recovery pattern documentado |

---

## Notas de Implementacion

1. **No tocar formulas financieras** — los valores son correctos. El bug es de labeling, no de math.
2. **CG-TIER-CONSISTENCY existente NO se modifica** — sigue en WARNING para su proposito original (frontmatter vs texto). El nuevo gate es independiente.
3. **precision_tier ya existe en JSON** — solo hay que exponerlo en el template (~5 lineas).
4. **ia_readiness_calculator.py ya esta listo** para recibir `ga4_indirect_score`. Sin cambios.
5. **Orden estricto**: FASE-1 → FASE-2 → FASE-3 → FASE-4 → FASE-5 → RELEASE. No paralelizar.
6. **T0/T0b en FASE-1 son pre-requisito** para T1-T4. Sin limpieza de consumers downstream, introducir B_PLUS causa regression silenciosa en PDFs (NP1) y publication gates (NP2).
7. **H10 (3 sistemas precision_tier) es DEUDA TECNICA documentada** — no se implementa en este plan. Requiere refactorizacion independiente.
8. **H12 (service account GCP) es OUT OF PLAN** — accion manual del usuario en Google Cloud Console.
9. **Arquitectura per-hotel respetada** (NP7): GA4/GSC son per-hotel via CLI flag, NO env vars globales. Gate y MANIFEST enrichment deben pasar params.
10. **T0 control en FASE-5** (NP8): sin el control de hotel_test_001, no se verifica que el fix no rompe el caso default Tier C (hotel sin onboarding). Leccion previa §6 aplicada.
