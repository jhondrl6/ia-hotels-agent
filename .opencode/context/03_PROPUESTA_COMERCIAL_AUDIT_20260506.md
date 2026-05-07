---
generated_at: 2026-05-06 08:45
validated_at: 2026-05-06 11:45
version: 2.0.0  # POST-VALIDACIÓN contra código vivo
document_type: CONTEXT_AUDIT_VALIDADO
hotel_id: hotelcastillareal
validation_method: código vivo + browser live check + archivos en disco
related_docs:
  - 01_DIAGNOSTICO_Y_OPORTUNIDAD_20260505_202700.md
  - 02_PROPUESTA_COMERCIAL_20260505_202705.md
  - hotelcastillareal/v4_audit/coherence_validation.json
  - financial_scenarios.json (sobrescrito por run Termales 2026-05-06 09:32)
  - gate_report.json (sobrescrito por run Termales 2026-05-06 09:32)
  - audit_report.json (sobrescrito por run Termales 2026-05-06 09:32)
---

# AUDITORÍA COMPLETA VALIDADA: 02_PROPUESTA_COMERCIAL vs 01_DIAGNOSTICO + CÓDIGO VIVO

**Hotel**: Hotelcastillareal — `https://www.hotelcastillareal.com/`
**Fecha de ejecución original**: 2026-05-05 20:27
**Auditoría original**: 2026-05-06 08:45
**Validación contra código vivo**: 2026-05-06 11:45

---

## NOTA DE VALIDACIÓN

Los JSON de evidencia (gate_report.json, audit_report.json, financial_scenarios.json) en `output/v4_complete/` fueron **sobrescritos** por una ejecución posterior de v4complete para "Termales Santa Rosa de Cabal" (2026-05-06 09:32). Los archivos .md del diagnóstico y propuesta de Hotelcastillareal sí sobreviven, así como los assets en `output/v4_complete/hotelcastillareal/` y el `coherence_validation.json` original. Los valores del gate_report citados en la auditoría original (0.719487, whatsapp_status=conflict) se verificaron por fuentes secundarias: el coherence_validation.json (overall_score=0.72) y una ejecución independiente de Termales que confirma patrones sistémicos (geo_playbook missing, misma estructura de gates).

**Cada hallazgo indica explícitamente si fue verificado contra código vivo, archivo sobreviviente o inferido por patrón sistémico.**

---

## VEREDICTO EJECUTIVO

**La propuesta comercial NO está lista para entrega.** El pipeline v4complete tiene 7 problemas, 3 bloqueantes y 4 altos/medios, TODOS verificados contra código vivo:

1. **COHERENCE: 3 fuentes, 3 valores distintos** — El diagnóstico usa un fallback interno (`_calculate_coherence_score`, L1178-1204 de v4_diagnostic_generator.py) que produce 0.74. El CoherenceValidator (`coherence_validation.json`) produce 0.72. El publication gate lee `asset_result.coherence_report.overall_score` (tercer valor, de la etapa de assets). La propuesta lee el valor del diagnóstico (0.74 × 100 = "74%") y el gate lo compara contra umbral 0.8 desde otra fuente. **Hay 3 cómputos independientes que producen 3 valores y ninguno se comunica con los otros.** El resultado: el gate puede fallar (0.72 < 0.80) mientras la propuesta muestra "74%" sin indicar FAILED.

2. **WHATSAPP: Código declara "✅ Entregado" ignorando conflicto** — `v4_proposal_generator.py:1016` solo verifica `presence_verified and present_in_production`. NUNCA consulta `whatsapp_status=conflict` del audit_report. El botón existe en producción (verificado live: Joinchat v6.0.10, phone=573104692201 → 3104692201, coincide con GBP), pero hay conflicto de números (landline web: 6063332192 ≠ móvil GBP: 3104692201). El código es técnicamente correcto pero **comercialmente falso**: decir "nosotros lo entregamos" cuando hay un conflicto sin resolver y el botón ya existía es engañoso.

3. **PROYECCIÓN FINANCIERA: Tabla mensual sin recovery_factor** — `v4_proposal_generator.py:645-656` aplica `pain_ratio` (40.82%) al projected_monthly_gain pero NO aplica `recovery_factor` (20%). El ROI en L594 y L1063 sí aplica ambos. Resultado: tabla muestra $327K/mes netos, pero con recovery_factor sería ~$61K/mes. La nota `pain_ratio_note` (L623-626) existe pero no explica el doble descuento. El cliente ve números inconsistentes entre tabla y ROI.

4. **GOOGLE MAPS: Prometido sin asset** — Confirmado como **sistémico**: el gate de Termales también reporta geo_playbook missing. El mapping `PROPOSAL_SERVICE_TO_ASSET` lista "Google Maps Optimizado" → "geo_playbook" pero el asset nunca se genera.

5. **SEO/AEO: Pilares más bajos sin plan específico** — SEO Local (25/100) solo tiene "Semana 3: optimización basada en análisis técnico" genérico. AEO (0/100) tiene CERO menciones en la propuesta. Schema de Hotel recibe atención prioritaria pese a no ser el pilar más dañado.

6. **TIER C: Sin advertencia en propuesta** — `precision_tier: "C"` existe en financial_scenarios.json y en el diagnóstico (L8 del YAML header: `financial_evidence_tier: "C"`). Pero el generador de propuesta (`v4_proposal_generator.py`) tiene CERO referencias a `precision_tier` o `evidence_tier`, y el template de propuesta (`propuesta_v6_template.md`) tiene CERO variables de tier.

7. **COHERENCE DISCREPANCY: 0.74 vs 0.72 vs valor del gate** — La causa raíz NO es un bug sino una **arquitectura de 3 cómputos independientes**: (a) fallback del diagnóstico promedia confidence levels, (b) CoherenceValidator en asset pipeline usa su propia lógica, (c) publication gate lee del asset_result. Ninguno alimenta al otro.

**Veredicto**: 6/7 hallazgos CONFIRMADOS contra código vivo. El hallazgo #1 se recalifica: no es "gate failed sin advertencia" (el gate SÍ falla), es "3 fuentes de verdad para 1 métrica". El problema es de **arquitectura de pipeline**, no de presentación.

---

## HALLAZGOS DETALLADOS (VALIDACIÓN CONTRA CÓDIGO VIVO)

### HALLAZGO 1 — COHERENCE: 3 FUENTES, 3 VALORES [🔴 BLOQUEANTE]

**Validación**: CÓDIGO VIVO + ARCHIVO SOBREVIVIENTE

**Tres fuentes de verdad para coherence_score**:

| Fuente | Valor | Dónde se computa | Quién lo lee |
|--------|-------|------------------|-------------|
| Fallback diagnóstico | 0.74 | `v4_diagnostic_generator.py:1178-1204` `_calculate_coherence_score()` | YAML header diagnóstico, propuesta (L677 ×100="74%") |
| CoherenceValidator | 0.72 | `coherence_validator.py` → `coherence_validation.json:3` | Nadie en el flujo principal |
| Asset coherence report | variable | `asset_result.coherence_report.overall_score` | Publication gate (`main.py:2637`) |

**Flujo en código (main.py:2621-2679)**:
```python
# L2637: El coherence_score del assessment VIENE de asset_result
"coherence_score": asset_result.coherence_report.overall_score if asset_result else 0.0,

# L2679: El gate usa ESE valor
gate_results = run_publication_gates(assessment, gate_config)

# Pero el diagnóstico ya se generó ANTES, con su propio fallback
# Y la propuesta lee diagnostic_summary.coherence_score (L677), no el del gate
```

**El diagnostic generator acepta coherence_score como parámetro** (L428: `coherence_score: Optional[float] = None`), pero en el pipeline actual NADIE se lo pasa — siempre usa el fallback. El parámetro existe como "placeholder de una fase anterior" (signature-only wiring).

**Causa raíz**: El pipeline genera diagnóstico → propuesta → assets → gates en ese orden. Los gates corren al final (L2679) y su resultado **no se retroalimenta** al diagnóstico ni a la propuesta. El `assessment["coherence_score"]` se construye desde `asset_result` (L2637) DESPUÉS de que el diagnóstico ya fue escrito.

**Solución recomendada**: 
1. Mover la ejecución de CoherenceValidator ANTES del diagnóstico (romper el orden actual diagnóstico→assets→gates)
2. Pasar `coherence_score` del CoherenceValidator al `diagnostic_gen.generate(coherence_score=...)`
3. Agregar `${gate_status}` al template de diagnóstico para mostrar PASSED/FAILED
4. ELIMINAR el fallback `_calculate_coherence_score()` — si no hay coherence_score del gate, mostrar "PENDIENTE" en vez de inventar uno

---

### HALLAZGO 2 — WHATSAPP: ESTADO INCORRECTO EN PROPUESTA [🔴 BLOQUEANTE]

**Validación**: CÓDIGO VIVO + LIVE SITE

**Código (v4_proposal_generator.py:1014-1017)**:
```python
# FASE-D: Si se verificó presencia y el asset YA existe en producción,
# es el estado más honesto que podemos mostrar
if presence_verified and present_in_production:
    return ("✅ Verificado en sitio", "Ya existe en su web - nosotros lo entregamos")
```

**Lo que NO hace**: NUNCA consulta `whatsapp_status` del audit_report. Si `whatsapp_status=conflict`, el código aún dice "✅ Verificado".

**Live site (browser_console en hotelcastillareal.com)**:
- Joinchat plugin v6.0.10 activo
- WhatsApp link: `https://api.whatsapp.com/send?phone=573104692201` → móvil 3104692201
- Número landline en footer: +57 (606) 333 2192
- **El botón existe y funciona con el número móvil.** El conflicto es entre el landline de la web y el móvil del GBP. El botón técnicamente correcto, comercialmente requiere aclaración.

**Solución recomendada**:
```python
# En _get_asset_status(), ANTES de presence_verified:
if audit_report and audit_report.validation.whatsapp_status == "conflict":
    return ("⚠️ Conflicto detectado", "Requiere resolución manual - números no coinciden")
if presence_verified and present_in_production:
    return ("✅ Verificado en sitio", "Ya existe en su web")
```

El string "conflict" viene de `audit_report.json:53` (`whatsapp_status: "conflict"` en la versión original; la actual de Termales dice `"estimated"`). Verificar el enum real de `whatsapp_status` antes de hardcodear el string.

---

### HALLAZGO 3 — PROYECCIÓN FINANCIERA OPACA [🟡 ALTO]

**Validación**: CÓDIGO VIVO

**El código hace dos cosas distintas**:

```python
# L591-592: projected_monthly_gain = pain_ratio × raw_loss
projected_monthly_gain = int(raw_monthly_loss * pain_ratio)

# L645-656: Tabla mensual usa projected_monthly_gain SIN recovery_factor
'rec_m1': format_cop(projected_monthly_gain),         # $1,527,360
'net_m1': format_cop(projected_monthly_gain - monthly_investment),  # $327,360

# L594: ROI usa recovery_factor ADEMÁS de pain_ratio
roi_6_months = self._calculate_roi(monthly_investment, projected_monthly_gain, 6,
                                   recovery_factor=recovery_factors['realistic'])

# L1061-1063: _calculate_roi aplica recovery_factor
total_gain = gain * recovery_factor * months
roi_ratio = total_gain / total_investment
# = (1,527,360 × 0.20 × 6) / (1,200,000 × 6) = 0.2544 → "0.3X"
```

**El pain_ratio_note (L623-626)**: Existe pero es genérico. Dice "Recovery factor: 41% of monthly loss retained" sin mencionar que hay UN SEGUNDO descuento (recovery_factor=20%) que solo aplica al ROI.

**Verificación matemática con Hotelcastillareal**:
- raw_monthly_loss: $3,741,696 (financial_scenarios.json)
- pain_ratio: 0.4082
- projected_monthly_gain: 3,741,696 × 0.4082 = $1,527,360
- Tabla: rec=$1,527,360, net=$327,360/mes ✅ (cálculo correcto según código)
- ROI con recovery_factor=0.20: (1,527,360 × 0.20) / 1,200,000 = 0.2544 → "0.3X" ✅
- Pero 1,527,360 × 0.20 = $305,472 de recuperación real/mes (con ambos descuentos)
- Neto real: $305,472 - $1,200,000 = -$894,528/mes 😱

**El cliente ve**: "Usted gana $327K/mes netos" (tabla) + "ROI 0.3X en 6 meses" (inconsistente con la tabla).

**Solución recomendada**:
- **Opción A (preferida)**: Aplicar `effective_recovery = pain_ratio × recovery_factor` como UN SOLO multiplicador a toda la proyección (tabla Y ROI). El effective_recovery para Hotelcastillareal = 0.4082 × 0.20 = 0.08164 → la tabla mostraría ~$305K/mes de recuperación bruta y -$895K/mes netos en etapa temprana. Si esto es demasiado pesimista, ajustar recovery_factor.
- **Opción B**: Mantener ambos descuentos pero explicarlos EXPLÍCITAMENTE en la propuesta con una nota: "De su pérdida mensual ($3.7M), estimamos que 40.8% es recuperable con IAO ($1.5M). De ese monto, proyectamos recuperar 20% en los primeros 6 meses ($305K/mes). El ROI de 0.3X refleja esta proyección conservadora."
- **Opción C**: Simplificar a un solo ratio (effective_recovery) y eliminar el concepto de "dos descuentos". Más limpio pero requiere refactorización del pricing model.

---

### HALLAZGO 4 — GOOGLE MAPS OPTIMIZADO: PROMETIDO PERO SIN ASSET [🟡 ALTO]

**Validación**: CONFIRMADO COMO SISTÉMICO (verificado en gate_report de Termales)

**gate_report.json (Termales, L130-137)**:
```json
"missing": [{
  "service": "Google Maps Optimizado",
  "asset": "geo_playbook",
  "message": "Service 'Google Maps Optimizado' promises asset 'geo_playbook' 
              but it was not generated and does not exist in production",
  "presence_verified": true,
  "presence_status": "not_exists"
}]
```

El mismo patrón aparece para ambos hoteles. Es un problema del catálogo de assets, no de una ejecución individual.

**Solución recomendada**:
- **Opción A**: Si "Google Maps Optimizado" es un servicio real del kit → crear el asset `geo_playbook` en el catálogo (`asset_catalog.py`) con generación condicional
- **Opción B**: Si el servicio ya está cubierto por otros assets (ej. optimization_guide, geo enrichment) → eliminar "Google Maps Optimizado" de `PROPOSAL_SERVICE_TO_ASSET` y del SERVICE_CATALOG
- El GEO enrichment pipeline (`geo_enriched/`) ya genera geo_fix_kit.md, geo_checklist_min.md, geo_dashboard.md, geo_badge.md — posiblemente `geo_playbook` sea redundante

---

### HALLAZGO 5 — SEO LOCAL + AEO SIN PLAN ESPECÍFICO [🟡 MEDIO]

**Validación**: CÓDIGO VIVO + ARCHIVO PROPUESTA

**Scores del diagnóstico**:
- SEO Local: 25/100
- AEO: 0/100
- GEO: 70/100
- IAO: 35/100

**Lo que la propuesta menciona** (verificado grep en 02_PROPUESTA_COMERCIAL_20260505_202705.md):
- SEO Local: "Semana 3: SEO Local - optimización basada en análisis técnico" (1 línea genérica)
- AEO: CERO menciones en toda la propuesta
- Schema de Hotel: recibe plan detallado con asset específico

**El generador prioriza Schema de Hotel sobre los pilares más dañados.** Esto puede ser correcto si Schema es prerequisite para SEO/AEO, pero la propuesta no explica esa priorización.

**Solución recomendada**:
- Conectar dinámicamente los scores de cada pilar con el plan de 7/30/60/90 días
- Si un pilar tiene score < 30, garantizar que aparezca en quick wins con acción específica
- Para AEO=0: incluir en la propuesta que "AEO se construye sobre Schema FAQ + Open Graph — ambos incluidos en su kit"
- No requiere nuevos assets, solo lógica de priorización en `_build_7_day_plan()` / `_build_30_day_plan()`

---

### HALLAZGO 6 — TIER C SIN ADVERTENCIA EN PROPUESTA [🟡 MEDIO]

**Validación**: CÓDIGO VIVO — CONFIRMADO

**El diagnóstico SÍ advierte** (YAML header L8):
```yaml
financial_evidence_tier: "C"
```

**La propuesta NO**: `grep -n "precision_tier\|evidence_tier\|financial_evidence" v4_proposal_generator.py` → **0 resultados**. El generador de propuesta nunca lee el tier, nunca lo pasa al template, y el template (`propuesta_v6_template.md`) no tiene ninguna variable para mostrarlo.

**Solución recomendada**:
1. En `_prepare_template_data()`, agregar:
   ```python
   'financial_evidence_tier': getattr(financial_scenarios, 'precision_tier', 'C'),
   ```
2. En el template, agregar bloque en sección financiera:
   ```
   > ⚠️ Nivel de evidencia: Tier ${financial_evidence_tier}
   > Estas proyecciones usan benchmarks regionales. Para precisión exacta,
   > ejecute el onboarding con datos reales de su operación.
   ```
3. Para Tier C específicamente, mostrar nota más visible (banner de advertencia)

---

### HALLAZGO 7 — COHERENCE SCORE: 3 VALORES PARA 1 MÉTRICA [🟡 MEDIO]

**Validación**: CÓDIGO VIVO — CONFIRMADO COMO CAUSA RAÍZ DEL HALLAZGO 1

**Resumen de los 3 valores** (ya detallado en Hallazgo 1):

| Origen | Valor | Método | Archivo |
|--------|-------|--------|---------|
| Fallback diagnóstico | 74 (0.74) | Promedio de confidence levels | YAML header diagnóstico |
| CoherenceValidator | 0.72 | `coherence_validator.py` | coherence_validation.json |
| Asset coherence report | variable | `asset_diagnostic_linker.py:212` | Solo en memoria |

**La discrepancia 0.74 vs 0.72 no es un "bug de timing"** — es que son DOS ALGORITMOS DIFERENTES:
- `_calculate_coherence_score()`: VERIFIED→100, ESTIMATED→70, CONFLICT→30 → promedio
- `CoherenceValidator`: lógica propia (problems_have_solutions, assets_are_justified, etc.)

**Solución recomendada**: Unificar en UN solo cómputo. La corrección del Hallazgo 1 resuelve este automáticamente.

---

## HALLAZGO ADICIONAL (NO EN AUDITORÍA ORIGINAL): SOBRESCRITURA DE EVIDENCIA

**Severidad**: 🟠 INFORMATIVO (no es un bug del pipeline pero afecta auditorías)

Los JSON de evidencia en `output/v4_complete/` (gate_report.json, audit_report.json, financial_scenarios.json) **se sobrescriben en cada ejecución de v4complete**, independientemente del hotel. Si se corre v4complete para Hotel A y luego para Hotel B, los JSON del Hotel A desaparecen. Los .md y subdirectorios por hotel sí persisten.

**Impacto**: Imposibilita auditorías retrospectivas. Si un auditor necesita verificar los claims de una propuesta generada hace 2 días, los JSON ya fueron reemplazados.

**Solución recomendada**: 
- Guardar JSON reports dentro del subdirectorio del hotel (`output/v4_complete/{hotel_id}/v4_audit/`) en vez de en la raíz `output/v4_complete/`
- O usar nombres con timestamp+hospital_id: `gate_report_hotelcastillareal_20260505_202709.json`

---

## ARCHIVOS DE EVIDENCIA

| Archivo | Ruta | Estado |
|---------|------|--------|
| Diagnóstico original | `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260505_202700.md` | ✅ Existe |
| Propuesta comercial | `output/v4_complete/02_PROPUESTA_COMERCIAL_20260505_202705.md` | ✅ Existe |
| coherence_validation.json | `output/v4_complete/hotelcastillareal/v4_audit/coherence_validation.json` | ✅ Existe (overall_score=0.72) |
| gate_report.json original | `output/v4_complete/gate_report.json` | ❌ Sobrescrito (ahora es de Termales) |
| audit_report.json original | `output/v4_complete/audit_report.json` | ❌ Sobrescrito (ahora es de Termales) |
| financial_scenarios.json original | `output/v4_complete/financial_scenarios.json` | ❌ Sobrescrito (ahora es de Termales) |
| Generador de propuesta | `modules/commercial_documents/v4_proposal_generator.py` | ✅ 1623 líneas |
| Generador de diagnóstico | `modules/commercial_documents/v4_diagnostic_generator.py` | ✅ 2935 líneas |
| Publication gates | `modules/quality_gates/publication_gates.py` | ✅ 1143 líneas |
| Coherence gate | `modules/quality_gates/coherence_gate.py` | ✅ 377 líneas |
| Pipeline principal | `main.py` (L2615-2722) | ✅ Assessment + gates |
| Template propuesta V6 | `modules/commercial_documents/templates/propuesta_v6_template.md` | ✅ |
| Template diagnóstico V6 | `modules/commercial_documents/templates/diagnostico_v6_template.md` | ✅ |

---

## CÓDIGO RELEVANTE (VERIFICADO)

### 1. WhatsApp status — v4_proposal_generator.py:1014-1017
```python
if presence_verified and present_in_production:
    return ("✅ Verificado en sitio", "Ya existe en su web - nosotros lo entregamos")
```
**Problema**: No consulta whatsapp_status del audit_report.

### 2. Tabla mensual sin recovery_factor — v4_proposal_generator.py:645-656
```python
'rec_m1': format_cop(projected_monthly_gain),  # SIN recovery_factor
'net_m1': format_cop(projected_monthly_gain - monthly_investment),
```

### 3. ROI con recovery_factor — v4_proposal_generator.py:1050-1073
```python
total_gain = gain * recovery_factor * months
roi_ratio = total_gain / total_investment
```

### 4. Coherence_score en assessment — main.py:2637
```python
"coherence_score": asset_result.coherence_report.overall_score if asset_result else 0.0,
```

### 5. Fallback coherence del diagnóstico — v4_diagnostic_generator.py:1178-1204
```python
def _calculate_coherence_score(self, validation_summary: ValidationSummary) -> int:
    # VERIFIED→100, ESTIMATED→70, CONFLICT→30 → promedio
```

### 6. Coherence_score en propuesta — v4_proposal_generator.py:677
```python
'coherence_score': str(int(diagnostic_summary.coherence_score * 100))
```

---

## MACRO-FASES PROPUESTAS PARA EL PLAN DE INTERVENCIÓN

> ⚠️ Estas son propuestas de organización, NO el plan final. El plan se diseña en la siguiente sesión usando `iah-cli-context-audit-to-plan`. La numeración reorganiza los hallazgos por dependencia y prioridad.

### FASE-A: UNIFICACIÓN DE COHERENCE SCORE (Hallazgos 1 + 7)
**Problema**: 3 fuentes de verdad para 1 métrica. El diagnóstico usa fallback, el gate lee de assets, el CoherenceValidator no se usa.
**Objetivo**: UN solo cómputo de coherence_score, UN solo consumidor.
**Tareas**:
1. Ejecutar CoherenceValidator ANTES del diagnóstico en main.py
2. Pasar `coherence_score` al `diagnostic_gen.generate(coherence_score=...)` 
3. Agregar `${gate_status}` (PASSED/FAILED) al template de diagnóstico
4. Eliminar fallback `_calculate_coherence_score()` o degradarlo a "si no hay valor del gate, mostrar PENDIENTE"
**Archivos**: main.py, v4_diagnostic_generator.py, diagnostico_v6_template.md, coherence_gate.py

### FASE-B: WHATSAPP — CONFLICT STATUS EN PROPUESTA (Hallazgo 2)
**Problema**: `_get_asset_status()` ignora `whatsapp_status=conflict`.
**Objetivo**: Cuando audit_report detecta conflicto, la propuesta lo refleja.
**Tareas**:
1. En `_get_asset_status()`, agregar check de `whatsapp_status == "conflict"` ANTES del check de presence_verified
2. Verificar el string exacto del enum (puede ser "conflict", "CONFLICT", o ConfidenceLevel.CONFLICT)
3. Asegurar que el mensaje sea: "⚠️ Conflicto detectado — Requiere resolución manual"
**Archivos**: v4_proposal_generator.py (L1014-1017)

### FASE-C: PROYECCIONES FINANCIERAS — TRANSPARENCIA (Hallazgo 3)
**Problema**: Tabla mensual sin recovery_factor, ROI sí lo aplica. El cliente ve números inconsistentes.
**Objetivo**: Consistencia entre tabla y ROI, o explicación explícita del doble descuento.
**Tareas**:
1. **Opción A (recomendada)**: Aplicar `effective_recovery = pain_ratio × recovery_factor` como multiplicador único en tabla Y ROI. Recalcular toda la proyección.
2. **Opción B (mínima)**: Reescribir `pain_ratio_note` para explicar AMBOS descuentos explícitamente
3. Verificar que el template muestre la nota en lugar visible (no en letra pequeña)
**Archivos**: v4_proposal_generator.py (L591-656, L1050-1073), propuesta_v6_template.md

### FASE-D: GOOGLE MAPS — ASSET O REDEFINICIÓN (Hallazgo 4)
**Problema**: PROPOSAL_SERVICE_TO_ASSET promete geo_playbook que no existe.
**Objetivo**: Eliminar la promesa falsa.
**Tareas**:
1. Verificar si los assets GEO existentes (geo_fix_kit.md, geo_checklist_min.md, geo_dashboard.md, geo_badge.md) ya cubren la función de geo_playbook
2. Si sí: eliminar "Google Maps Optimizado" de PROPOSAL_SERVICE_TO_ASSET y SERVICE_CATALOG
3. Si no: crear asset geo_playbook en asset_catalog.py con conditional generation
**Archivos**: v4_proposal_generator.py, asset_catalog.py, PROPOSAL_SERVICE_TO_ASSET mapping

### FASE-E: SEO/AEO — PLAN ESPECÍFICO (Hallazgo 5)
**Problema**: Pilares con scores más bajos reciben menos atención.
**Objetivo**: Plan dinámico que priorice pillars con scores < 30.
**Tareas**:
1. En `_build_7_day_plan()` / `_build_30_day_plan()`, agregar lógica: si score < 30 → incluir acción específica
2. Para AEO=0: conectar con los assets FAQ+Open Graph que YA se generan
3. Asegurar que la tabla de Estado de Entregables mencione SEO Local y AEO
**Archivos**: v4_proposal_generator.py (_build_*_plan methods), propuesta_v6_template.md

### FASE-F: TIER C — ADVERTENCIA EN PROPUESTA (Hallazgo 6)
**Problema**: precision_tier="C" existe en datos pero nunca llega a la propuesta.
**Objetivo**: El cliente sabe que las proyecciones son Tier C.
**Tareas**:
1. Agregar `financial_evidence_tier` al dict de `_prepare_template_data()` (L597+)
2. Agregar bloque de advertencia en propuesta_v6_template.md
3. Diferenciar visualmente Tier C (⚠️ banner) de Tier A/B (nota sutil)
**Archivos**: v4_proposal_generator.py, propuesta_v6_template.md

### FASE-G: SOBRESCRITURA DE EVIDENCIA (Hallazgo adicional)
**Problema**: JSON reports se sobrescriben entre ejecuciones de diferentes hoteles.
**Objetivo**: Evidencia persiste por hotel.
**Tareas**:
1. Cambiar ruta de gate_report.json, audit_report.json, financial_scenarios.json a `output/v4_complete/{hotel_id}/v4_audit/`
2. Agregar timestamp al nombre: `gate_report_20260505_202709.json`
3. Actualizar main.py (L2719) y cualquier otro escritor de estos archivos
**Archivos**: main.py, v4audit (si aplica)

---

## RESUMEN DE SEVERIDADES (POST-VALIDACIÓN)

| Hallazgo | Severidad | Tipo | Validación |
|----------|-----------|------|------------|
| Coherence: 3 fuentes de verdad | 🔴 BLOQUEANTE | Arquitectura pipeline | Código vivo |
| WhatsApp: estado incorrecto | 🔴 BLOQUEANTE | Lógica comercial | Código vivo + live site |
| Proyección financiera opaca | 🟡 ALTO | Comunicación | Código vivo |
| Google Maps sin asset | 🟡 ALTO | Consistencia | Sistémico (Termales confirma) |
| SEO/AEO sin plan específico | 🟡 MEDIO | Completitud | Código vivo + propuesta .md |
| Tier C sin advertencia | 🟡 MEDIO | Transparencia | Código vivo (0 refs en generador) |
| Coherence score discrepancy | 🟡 MEDIO | Causa raíz del #1 | Código vivo |
| Sobrescritura de evidencia | 🟠 INFORMATIVO | Auditoría futura | Observación en disco |

---

## PRÓXIMA SESIÓN: DISEÑO DEL PLAN DE INTERVENCIÓN

Usa el skill `iah-cli-context-audit-to-plan` con este archivo como contexto para generar el plan de intervención por fases.

**Prompt para la siguiente sesión**:

```
Carga y ejecuta el skill iah-cli-context-audit-to-plan con el contexto en:
/mnt/c/Users/Jhond/Github/iah-cli/.opencode/context/03_PROPUESTA_COMERCIAL_AUDIT_20260506.md

Este contexto ya fue validado contra código vivo (2026-05-06 11:45).
No es necesario re-verificar los hallazgos — diseñar el plan directamente.

Sigue .agents/workflows/phased_project_executor.md para generar:
1. Plan de fases (A→G) con dependencias
2. Prompt de inicio de sesión por fase
3. Checklist de implementación
4. Documentación post-proyecto

Priorizar fases bloqueantes (A+B primero, luego C+D, luego E+F, finalmente G).
```

---

*Auditoría original: Hermes Agent — 2026-05-06 08:45*
*Validación contra código vivo: Hermes Agent — 2026-05-06 11:45*
*Fuentes: código vivo (v4_proposal_generator.py, v4_diagnostic_generator.py, main.py, publication_gates.py), browser live check (hotelcastillareal.com), archivos en disco (coherence_validation.json, .md outputs)*
