# 🔴 REPORTE DE QA — BLOQUEANTE PARA ENVÍO COMERCIAL (v3 — Auditoría de Tercer Orden vs Código Vivo)

**Documento revisado:** `02_PROPUESTA_COMERCIAL_20260527_155211.md`
**Versión del agente:** v4.54.0
**Fecha de revisión:** 27 de mayo de 2026
**Fecha de auditoría contra código vivo:** 27 de mayo de 2026
**Veredicto:** ⛔ **NO APTO PARA ENVÍO AL CLIENTE** — Requiere 4 fixes críticos + 4 importantes
**Score de cumplimiento vs. ROICR v3.0:** **72%** (18/25 checkpoints)

---

## 📊 RESUMEN EJECUTIVO

La implementación aplicó correctamente la **capa cosmética** del refactor (separación CAPEX/OPEX, curva de maduración, garantía Día 55 hardcodeada), pero **falló en la capa estructural** (coherencia financiera entre tablas, unificación de motores ROI, ausencia de validador de garantía real). El documento contiene **una contradicción matemática bloqueante** que cualquier Director Financiero detectará en menos de 60 segundos de lectura.

**Nota metodológica v3:** Esta versión fue verificada exhaustivamente contra código vivo. Los archivos que la v2 decía que existían (`asset_semantics_validator.py`, `asset_catalog.py`, `guarantee_validator.py`) **NO EXISTEN en el repositorio.** Fueron claims inventados por la auditoría anterior, el mismo error que se le criticaba al ROICR original. Solo se incluyen hallazgos verificables.

---

## 🚨 HALLAZGOS CRÍTICOS (Bloqueantes — Fix en 24h)

### 🔴 CRIT-01: TRES SISTEMAS DE ROI PARALELOS — SOLO UNO DEBE QUEDAR
**Veredicto:** ✅ CONFIRMADO contra código vivo

**Evidencia en `v4_proposal_generator.py`:**
1. `_calculate_roi()` (línea 1492): `(gain * recovery_factor) / investment` → genera `roi_6_months` con formato `:.1fX`
2. `_calculate_roi_saas()` (línea 1534): `total_recuperacion / inversion_opex` → genera `roi_saas` con formato `:.1fX`
3. `roi_formatter.py` (importado línea 25): `calcular_metricas_roi()` + `formatear_roi_para_propuesta()` — **importado pero NUNCA invocado** (0 calls en todo el generador)

**La contradicción real:** Son TRES sistemas paralelos. El inline `_calculate_roi()` (legacy FASE-B) genera `roi_6_months`="0.4X", el inline `_calculate_roi_saas()` (FASE-3) genera `roi_saas`="1.1X", y `roi_formatter.py` (el motor correcto) no se usa.

**El problema del formato `:.1f`:** `roi_formatter.py:81` usa `f"{metrics.roi_saas:.1f}X"` — si roi_saas=1.05, el display es "1.1X". Mismo bug en `_calculate_roi_saas():1554` y `_calculate_roi():1515`.

**Fix obligatorio (unificado CRIT-01 + IMP-02 + NEW-01):**
```python
# modules/commercial_documents/v4_proposal_generator.py
# ELIMINAR _calculate_roi() (L1492-1515) y _calculate_roi_saas() (L1534-1554)
# USAR EXCLUSIVAMENTE roi_formatter.py como motor único:
from modules.financial_engine.roi_formatter import calcular_metricas_roi, formatear_roi_para_propuesta

# Y CAMBIAR en roi_formatter.py L81:
# "roi_saas": f"{metrics.roi_saas:.1f}X"  →  "roi_saas": f"{metrics.roi_saas:.2f}X"
```

---

### 🔴 NEW-03: ROI INCONSISTENTE ENTRE COMMERCIAL GATE Y DOCUMENTO
**Veredicto:** ✅ CONFIRMADO contra código vivo

**Evidencia:**
- Commercial gate (L377-379 del generador):
  ```python
  total_investment = price_monthly * 6 + setup_fee  # ← INCLUYE CAPEX
  total_recovery = monthly_gain * 6
  roi = total_recovery / total_investment  # ← ROI sobre OPEX+CAPEX
  ```
- `_calculate_roi_saas()` (L1550): `total_recuperacion / inversion_opex` ← **SIN CAPEX**

**Impacto:** El commercial gate calcula ROI=(gain×6)/(price×6+setup_fee) mientras el documento muestra ROI=gain×6/(price×6). Si setup_fee=$2.5M, la diferencia es sustancial.

**Fix obligatorio:**
```python
# L377-379: usar inversion_opex, NO total_investment
total_investment_opex = price_monthly * 6  # ← SIN setup_fee
roi = total_recovery / total_investment_opex
```

---

### 🔴 CRIT-02: VALUE-CAPTURE CAP — EL PIPELINE EXISTE PERO EL WRAPPER NO LO ACTIVA
**Veredicto:** ⚠️ DIAGNÓSTICO CORREGIDO

**El pipeline de 3 pasos SÍ existe** en `pricing_calculator.py` (función `calcular_precio_final()`, L211-287):
```
Paso 1: base_price = max(min_price, min(recommended, max_price))
Paso 2: adjusted_price (si pain_ratio > gate_max_ratio * 2.0)
Paso 3: ethical_cap = expected_recovery * value_capture_cap
        capped_price = min(adjusted_price, ethical_cap)  ← CAP APLICA
Floor:  final_price = max(capped_price, operational_floor)
```

**PERO** el `PricingResolutionWrapper._new_resolution()` (L143 de `pricing_resolution_wrapper.py`) llama a `calculator.calculate(rooms, expected_loss_cop, segment)` **SIN pasar `expected_recovery_cop`**. Sin ese parámetro, `calculate()` (L363) NO activa el pipeline de 3 pasos — cae al cálculo simple (L368-390).

**Consecuencia:** Aunque el ethical cap está implementado, nunca se ejecuta desde el flujo normal. Solo funcionaría si alguien llama `calculate()` directamente con `expected_recovery_cop`.

**Fix obligatorio:**
```python
# pricing_resolution_wrapper.py L143:
pricing_result = calculator.calculate(
    rooms, expected_loss_cop, segment,
    expected_recovery_cop=expected_loss_cop * 0.20  # ← PASAR ESTE PARÁMETRO
)
```

---

## 🟡 HALLAZGOS IMPORTANTES (Fix en 72h)

### 🟡 IMP-01: ERROR DE PORCENTAJE — pain_ratio ≠ fee/loss
**Veredicto:** ⚠️ CONFIRMADO — error semántico

**Evidencia (L790-801 del generador):**
```python
'pain_ratio_note': (
    f"La inversión mensual de ${int(monthly_investment):,} COP "
    f"representa el {pain_ratio:.0%} de su pérdida mensual estimada."
)
```
`pain_ratio` aquí es `addressable_pain_ratio` (porción del dolor que IAO puede abordar, default 0.20). Pero el copy dice "representa el X% de su pérdida", lo cual es semánticamente `fee/loss`, no `addressable_pain_ratio`. Para Castilla Real: fee=$800K, loss=$3.74M → fee/loss=21.4%, pero el template muestra 20% (pain_ratio).

**Fix:**
```python
'pain_ratio_note': f"Abordamos el {pain_ratio:.0%} de su pérdida estimada (zona addressable por IAO).",
'fee_to_loss_note': f"Su inversión representa el {monthly_investment/monthly_loss:.1%} de su pérdida mensual.",
```

---

### 🟡 NEW-02: COMMERCIAL GATE NO PREVIENE PUBLICACIÓN PARA AUDIENCIA EXTERNA
**Veredicto:** ✅ CONFIRMADO

**Evidencia (L394-420 del generador):**
- Si `document_audience == "internal"` y `blocking_passed=False`: añade alertas al documento
- Si `document_audience != "internal"`: solo `logging.warning` y el documento se guarda igual (L427)

**Fix:** Añadir `strict_mode=True` que lance `CommercialGateBlockedError` para audiencia externa:
```python
if not commercial_report.blocking_passed and document_audience != "internal":
    raise CommercialGateBlockedError(
        f"Propuesta bloqueada por {len(commercial_report.blocking_failures)} gates: "
        f"{[r.gate_id for r in commercial_report.blocking_failures]}"
    )
```

---

### 🟡 NEW-05: operational_floor CON DOS FALLBACKS DISTINTOS
**Veredicto:** ⚠️ CONFIRMADO — inconsistencia entre dos lugares

**Evidencia:**
- `calcular_precio_final()` L245: `operational_floor = config.get("operational_floor", min_price)` → fallback = min_price (800K para boutique)
- `PricingCalculator.__init__()` L329: `defaults.get("operational_floor", 400_000)` → fallback = 400K

Si el YAML no tiene `operational_floor`, el comportamiento depende de POR DÓNDE entra la llamada. El wrapper usa el constructor → 400K. Pero una llamada directa a `calcular_precio_final()` con config mínimo → 800K.

**Fix:** Unificar fallback a 400K en ambos lugares:
```python
# L245: operational_floor = config.get("operational_floor", 400_000)
```

---

### 🟡 IMP-03: SETUP FEE SIN DESGLOSE
**Veredicto:** ✅ CONFIRMADO

- Template muestra `| Cuota de Activación | ${setup_fee} | Única vez |`
- `SETUP_FEE = 2_500_000` hardcodeado (L126 del generador)
- No hay desglose de componentes (auditoría, implementación, configuración)

**Fix:** Crear dataclass `CAPEXBreakdown` en `data_structures.py`, definir componentes en `config/commercial.yaml`, añadir tabla de desglose al template.

---

### 🟡 NEW-04: pain_ratio CONCEPTO SOBRECARGADO
**Veredicto:** ✅ CONFIRMADO

Se usa para 3 cosas distintas en el código:
1. `addressable_pain_ratio`: porción del dolor que IAO puede abordar (L707, default 0.20)
2. `fee_to_loss_ratio`: se describe como tal en el copy (L795) pero no se calcula
3. `pain_ratio_gate_max`: umbral de gate en pricing.yaml (0.32) — cargado en L246 pero NUNCA comparado; el pipeline usa `gate_max_ratio * 2.0` (L256)

**Fix:** Renombrar variables para claridad semántica.

---

## 📊 HALLAZGOS QUE NO EXISTEN (CORREGIDOS DE v2)

Estos hallazgos de la versión anterior del ROICRII resultaron ser **falsos** tras verificación contra código vivo:

| Hallazgo v2 | Qué decía | Realidad |
|---|---|---|
| CRIT-03: AssetSemanticsValidator | "SÍ EXISTE (64 líneas) con INVALID_MAPPINGS" | **NO EXISTE.** 0 archivos `*semantics*` en el repo. No hay `INVALID_MAPPINGS` en `pain_solution_mapper.py` |
| CRIT-04: asset_catalog.py | Citaba líneas 240, 299, 313 con status IMPLEMENTED | **NO EXISTE.** El catálogo real es `service_catalog.py` (171 líneas) con `SERVICE_CATALOG` dict |
| IMP-04: guarantee_validator.py | "SÍ EXISTE (441 líneas) con KPIs, umbral 10%, CREDIT_NOTE.md" | **NO EXISTE.** La garantía Día 55 es texto hardcodeado en `propuesta_v6_template.md` L195-197. No hay validador automático |
| IMP-05: WhatsApp validation | "INVALID_MAPPINGS bloquea no_whatsapp_visible→whatsapp_conflict_guide" | **FALSO.** `INVALID_MAPPINGS` no existe. WhatsApp se maneja vía flag `whatsapp_conflict` (L738-742 del generador) |

---

## ℹ️ HALLAZGOS INFORMATIVOS

### ℹ️ CRIT-05: SIN PILOTO 30 DÍAS
**Veredicto:** ✅ CONFIRMADO — 0 resultados de "piloto"/"pilot" en todo el codebase

**Fix (baja prioridad):** Crear dataclass `PilotOption`, template section "Opciones de Bajo Riesgo", config en `commercial.yaml`.

### ℹ️ NEW-06: run_all_validations.py SIN COHERENCIA CROSS-TABLE
**Veredicto:** ✅ CONFIRMADO — el script existe (`scripts/run_all_validations.py`, 416 líneas) con 8 pasos pero ninguno valida coherencia financiera entre tablas (roi_6_months vs roi_saas vs maturity_curve total).

### ℹ️ Garantía Día 55: TEXTO ESTÁTICO, SIN BACKEND
La garantía es texto hardcodeado en el template (L195-197). No existe `guarantee_validator.py`, no hay KPIs reales, no hay nota crédito automática. Si se ofrece esta garantía, DEBE implementarse el backend antes del envío a cliente.

---

## 📊 TABLA DE VERIFICACIÓN CRUZADA (v3 — contra código vivo)

| Hallazgo | Veredicto | Evidencia en código |
|---|---|---|
| CRIT-01: 3 sistemas ROI | ✅ CONFIRMADO | L1492, L1534, L25 (0 calls) |
| NEW-03: ROI inconsistente gate | ✅ CONFIRMADO | L377 vs L1550 |
| CRIT-02: Ethical cap wrapper | ⚠️ CORREGIDO | Pipeline existe (L248-269) pero wrapper no pasa expected_recovery_cop (L143) |
| IMP-01: pain_ratio confusion | ✅ CONFIRMADO | L790-801 |
| IMP-02: ROI format :.1f | ✅ CONFIRMADO | L1515, L1554, roi_formatter.py:81 |
| IMP-03: SETUP_FEE hardcodeado | ✅ CONFIRMADO | L126 |
| NEW-02: Gate no bloquea externo | ✅ CONFIRMADO | L394-412 |
| NEW-04: pain_ratio sobrecargado | ✅ CONFIRMADO | L707, L795, pricing.yaml |
| NEW-05: operational_floor dual | ⚠️ CONFIRMADO | L245 vs L329 |
| NEW-06: run_all_validations | ✅ CONFIRMADO | scripts/run_all_validations.py:416 líneas |
| CRIT-05: Sin piloto | ✅ CONFIRMADO | 0 resultados en codebase |
| CRIT-03: Semantics validator | ❌ NO EXISTE | 0 archivos `*semantics*` |
| CRIT-04: asset_catalog.py | ❌ NO EXISTE | Existe service_catalog.py (171 líneas) |
| IMP-04: guarantee_validator | ❌ NO EXISTE | Garantía es texto hardcodeado en template |
| IMP-05: INVALID_MAPPINGS | ❌ NO EXISTE | WhatsApp se maneja vía flag conflict |

---

## 🎯 PLAN DE ACCIÓN (Prioridad real — código vivo)

### CRÍTICOS (24h):
```
[ ] CRIT-01: Unificar ROI: eliminar _calculate_roi() y _calculate_roi_saas() inline,
             usar roi_formatter.py como motor único. Cambiar :.1f → :.2f en 3 sitios.
[ ] NEW-03: Corregir commercial gate L377-379: usar inversion_opex, NO total_investment
[ ] NEW-02: Añadir strict_mode al commercial gate para audiencia externa
[ ] IMP-02: Cambiar formato ROI de :.1f a :.2f (absorbido en CRIT-01)
```

### IMPORTANTES (72h):
```
[ ] CRIT-02: Pasar expected_recovery_cop en PricingResolutionWrapper._new_resolution()
[ ] NEW-05: Unificar fallback operational_floor a 400K
[ ] IMP-01: Separar pain_ratio (addressable) de fee_to_loss_ratio en el copy
[ ] IMP-03: Desglose de CAPEX en componentes
```

### NICE-TO-HAVE (semana):
```
[ ] CRIT-05: Implementar Piloto 30 días
[ ] NEW-04: Renombrar pain_ratio a nombres semánticos distintos
[ ] NEW-06: Añadir cross-table coherence a run_all_validations.py
[ ] Garantía Día 55: Implementar guarantee_validator.py real (KPIs, umbrales, nota crédito)
[ ] AssetSemanticsValidator: Crear de cero si se necesita (no existe actualmente)
```

**Post-fix:** Ejecutar `python scripts/run_all_validations.py` + regenerar propuesta con `iah-cli v4complete hotelcastillareal`.

---

## ✅ LO QUE SÍ SE IMPLEMENTÓ CORRECTAMENTE

| Check | Implementación |
|---|---|
| ✅ Separación CAPEX/OPEX | Tabla clara, Setup Fee como activo propio |
| ✅ Curva de Maduración 4 Pilares | GEO→SEO→AEO→IAO con `aplicar_curva_4_pilares()` |
| ✅ Plan 7/30/60/90 días | Estructurado y accionable |
| ✅ Value-Capture Cap (narrativa) | Copy honesto en el template |
| ✅ Transparencia IAO | Anexo técnico en template |
| ✅ Notas de confianza (50%, 80%, 100%) | Implementado |
| ✅ Fotos: especificación técnica | Clara y accionable |
| ✅ Service Catalog (`service_catalog.py`) | Mapeo pains→servicios funcional |
| ✅ `roi_formatter.py` | Implementado (89 líneas) — solo falta usarlo |
| ✅ `calcular_precio_final()` pipeline 3 pasos | Implementado — solo falta activarlo desde el wrapper |
| ✅ `run_all_validations.py` | 416 líneas, 8 pasos de validación |

---

## 📋 VEREDICTO FINAL

> **La propuesta tiene los huesos correctos pero la matemática está rota.** Tres motores de ROI producen números distintos, el commercial gate usa una fórmula inconsistente con el documento, y el ethical cap existe en código pero nunca se activa desde el flujo normal.
>
> **Corrección a la auditoría v2:** La versión anterior del ROICRII cometió el mismo error que criticaba — inventó archivos (`asset_semantics_validator.py`, `asset_catalog.py`, `guarantee_validator.py`) y claims sobre ellos que no existen en el repositorio. Esta v3 solo contiene hallazgos verificables contra código vivo.
>
> **Recomendación:** NO enviar. Ejecutar los 3 fixes críticos (CRIT-01 unificado, NEW-03, NEW-02) en ~2 horas. Regenerar la propuesta. Luego validar coherencia financiera entre todas las tablas del documento generado. Solo entonces enviar.

---

## 🔧 NOTA METODOLÓGICA (LECCIÓN APRENDIDA — DOBLE)

El ROICR original referenció archivos inexistentes. El ROICRII (v2) criticó esto pero luego cometió el MISMO error: afirmó que `asset_semantics_validator.py` (64 líneas), `asset_catalog.py` (líneas 240/299/313), y `guarantee_validator.py` (441 líneas) existían y tenían contenido específico. **Ninguno existe.**

**Lección:** Toda auditoría de código DEBE verificar existencia de archivos con `search_files`/`grep` antes de referenciarlos — incluso las meta-auditorías. Esta v3 fue verificada con `search_files(target='files')` para cada archivo mencionado.
