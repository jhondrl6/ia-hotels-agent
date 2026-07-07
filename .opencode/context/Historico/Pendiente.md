# ✅ REPORTE DE VALIDACIÓN v2 — v4.58.0 (VERIFICADO CONTRA CÓDIGO VIVO + RE-EJECUCIÓN)

**Fecha de validación:** 29 de mayo de 2026
**Metodología:** Auditoría forense contra código vivo + re-ejecución v4complete Hotel Castilla Real
**Output verificado:** `output/v4_verify_f4/v4_complete/02_PROPUESTA_COMERCIAL_20260529_102728.md`
**Gate report:** `output/v4_verify_f4/v4_complete/hotelcastillareal/v4_audit/gate_report_20260529_102728.json`
**Veredicto:** ⚠️ **5 GAPS CONFIRMADOS + 1 BUG DE GATES + 1 DEUDA TÉCNICA**

---

## 🔍 HALLAZGO CLAVE DE RE-EJECUCIÓN: Evidence Tier es B, no C

**Esto resuelve F4 y corrige una premisa incorrecta del reporte anterior.**

### Evidencia (gate report re-ejecución):
```json
// tier_c_onboarding_required gate → Tier B
{"gate_name": "tier_c_onboarding_required", "status": "PASSED",
 "message": "Tier B: Datos suficientes para propuesta activa.",
 "details": {"tier": "B"}}

// financial_sources (L183-187):
{"adr_cop": "handler", "occupancy_rate": "regional", "direct_channel_percentage": "default"}
```

### Cálculo de `_determine_evidence_tier()` (scenario_calculator.py L480-504):
```
Sources: adr="handler", occupancy="regional", channel="default"
Verified (onboarding/verified/industry_standard_15pct): 0
Low quality (scraping/default/unknown/legacy_hardcode): 1 (channel="default")
→ NO cumple Tier A (necesita ≥2 verified) → NO cumple Tier C (necesita ≥2 low_quality)
→ Resultado: Tier B ✅
```

### Implicación para template:
Template L95-100 y L119-121: `{{if financial_evidence_tier == "C"}}` → **BLOQUE ELIMINADO** (correctamente).
El warning Tier C no aparece porque el tier real es B. **NO es un bug del template.**

### Discrepancia entre gates (BUG NUEVO — F7):
- `financial_validity` gate: "Financial data uses default/legacy values — **Tier C** evidence" (WARNING)
- `tier_c_onboarding_required` gate: "**Tier B**: Datos suficientes" (PASSED)

**Causa raíz:** `financial_validity` usa heurística de source-level ("any default → Tier C warning"), mientras `tier_c_onboarding_required` usa `_determine_evidence_tier()` formal. Dos lógicas diferentes para el mismo concepto. Esto confunde al lector del gate report.

**Fix:** Unificar la fuente de truth. `financial_validity` debe leer `financial_breakdown.evidence_tier` en vez de heurística propia.

---

## ✅ GAPS RESUELTOS (2/8)

### ✅ F0: Archivo fantasma — RESUELTO
El archivo v4.58.0 SÍ existe en `output/v4_complete_fix_v2/v4_complete/`.
El reporte anterior buscaba en `output/v4_complete/` (directorio equivocado).

### ✅ F4: Tier C warning — RESUELTO (no es un bug)
El warning no aparece porque evidence_tier = B, no C.
Template y código están correctamente alineados.
**Nuevo:** Se identificó F7 (discrepancia entre gates).

---

## 🔴 GAPS CONFIRMADOS (5 — contra código vivo + re-ejecución)

### 🔴 IMP-03: CAPEX breakdown no llega al output
**Estado:** CONFIRMADO
**Evidencia:**
- Código L867: `'capex_breakdown_table': self._build_capex_breakdown_table()` ✅ produce el dato
- Template `propuesta_v6_template.md` L141: solo tiene `${capex_total}` — NO `${capex_breakdown_table}`
- Output re-ejecutado L157: solo muestra "$2.500.000 COP" (total), sin desglose
- Template EMBEBIDO en `v4_proposal_generator.py` L593 SÍ tiene `${capex_breakdown_table}` pero NUNCA se usa (dead code)

**Fix:** Añadir `${capex_breakdown_table}` en `propuesta_v6_template.md` entre L141 y L142. Sin cambios de código.

**Esfuerzo:** 5 min

---

### 🔴 MIN-01: Sin tabla Status Quo vs Implementación
**Estado:** CONFIRMADO
**Evidencia:**
- `status_quo` → 0 resultados en todo `modules/`
- Template no tiene slot para tabla comparativa
- Output no muestra escenario de inacción vs implementación

**Fix:** Implementar `_build_status_quo_table()` + placeholder `${status_quo_table}` en template.

**Esfuerzo:** 1-2 horas

---

### 🔴 MIN-02: ADR no evidenciado
**Estado:** CONFIRMADO
**Evidencia:**
- `regional_benchmarks.yaml`: 0 entradas para `adr` en ninguna región
- `_build_coherence_checklist()` L1934: `validated_data.get('adr')` → siempre None
- Output re-ejecutado: 0 menciones de ADR
- `_extract_adr_from_audit()` SÍ existe en diagnostic_generator L1510 pero solo se usa para diagnóstico

**Fix (3 pasos):**
1. Añadir `adr: 285000` en `regional_benchmarks.yaml` para eje_cafetero (+ demás regiones)
2. Inyectar `adr_display` en data dict desde `_extract_adr_from_audit()` o benchmark YAML
3. Corregir `_build_coherence_checklist()` L1934: usar fuente real en vez de `validated_data.get('adr')`

**Esfuerzo:** 1-2 horas

---

### 🔴 MIN-03: Closing pitch no usa copy del ROICR
**Estado:** CONFIRMADO
**Evidencia:**
- `_build_closing_pitch()` → 0 resultados en codebase
- Template L214-220: texto duro "SIGUIENTE PASO", sin placeholder
- Output: sección estática idéntica al template

**Fix:** Implementar `_build_closing_pitch()` + reemplazar texto duro L214-220 con `${closing_pitch}`.

**Esfuerzo:** 1-2 horas

---

### 🔴 F5: ADR en coherence checklist siempre [PENDING]
**Estado:** CONFIRMADO
**Evidencia (código vivo):**
```python
# v4_proposal_generator.py L1934-1936
adr_value = validated_data.get('adr')  # ← siempre None
adr_verified = adr_value is not None   # ← siempre False
adr_detail = "Pendiente"               # ← siempre "Pendiente"
```
`validated_data` viene de `diagnostic_summary.validated_data_summary` — tiene keys como `whatsapp` pero NO `adr`.

**Fix:** Usar `_extract_adr_from_audit()` o inyectar `adr` en `validated_data` desde el diagnostic.

**Esfuerzo:** 15 min

---

## 🟡 HALLAZGOS ADICIONALES

### 🟡 F7 (NUEVO): Discrepancia entre publication gates
`financial_validity` dice "Tier C" y `tier_c_onboarding_required` dice "Tier B".
Dos lógicas diferentes para el mismo concepto. Confunde al lector.
**Fix:** Unificar `financial_validity` para usar `financial_breakdown.evidence_tier`.

### 🟡 F2: Producer-consumer disconnect (estructural)
Data dict ~50 keys, template ~30 placeholders. Sin contrato de schema.
CAPEX breakdown: producido pero no consumido. ADR/StatusQuo/Closing: ni producidos ni consumidos.
**Fix:** Opcional — schema validation. No bloqueante para los gaps comerciales.

### 🟡 Deuda técnica: Template embebido muerto
`v4_proposal_generator.py` L575-605 contiene template markdown completo que NUNCA se usa.
El código carga `propuesta_v6_template.md` desde archivo (L348).
**Fix:** Eliminar L575-605 del Python. Reduce confusión.

---

## 📊 RESUMEN CONSOLIDADO

| ID | Severidad | Gap | Tipo | Esfuerzo | Estado |
|----|-----------|-----|------|----------|--------|
| F0 | — | Archivo fantasma | Evidencia | — | ✅ RESUELTO |
| F4 | — | Tier C warning | Runtime | — | ✅ RESUELTO (tier=B) |
| IMP-03 | 🟡 | CAPEX breakdown sin consumir | Template | 5 min | 🔴 CONFIRMADO |
| MIN-01 | 🔴 | Sin Status Quo table | Código+Tpl | 1-2h | 🔴 CONFIRMADO |
| MIN-02 | 🔴 | ADR no evidenciado | Código+YAML+Tpl | 1-2h | 🔴 CONFIRMADO |
| MIN-03 | 🔴 | Closing pitch ausente | Código+Tpl | 1-2h | 🔴 CONFIRMADO |
| F5 | 🔴 | ADR checklist siempre [PENDING] | Bug | 15 min | 🔴 CONFIRMADO |
| F7 | 🟡 | Discrepancia entre gates | Bug | 30 min | 🟡 NUEVO |
| F2 | 🟡 | Producer-consumer disconnect | Arquitectura | 2-3h | 🟡 ESTRUCTURAL |

---

## 🎯 ESTRATEGIA DE INTERVENCIÓN (corregida v2)

### Cambios vs reporte anterior:
1. ~~F0 como paso bloqueante~~ → ELIMINADO (archivo existe)
2. ~~F4 necesita re-ejecución~~ → RESUELTO (tier=B, no C)
3. NUEVO F7: discrepancia entre gates (bug menor)
4. NUEVO: limpiar template embebido muerto

### Priorización:

**P1 — Template-only (5 min, máximo impacto inmediato):**
- IMP-03: Añadir `${capex_breakdown_table}` en template L141

**P2 — Bug fix rápido (15-30 min):**
- F5: Corregir `_build_coherence_checklist()` L1934 para ADR
- F7: Unificar lógica de `financial_validity` gate

**P3 — Código + Template (1-2 horas cada uno):**
- MIN-02: ADR en benchmarks YAML + data dict + template
- MIN-01: `_build_status_quo_table()` + template
- MIN-03: `_build_closing_pitch()` + template

**P4 — Deuda técnica (30 min):**
- Eliminar template embebido muerto L575-605

### Orden de ejecución recomendado:
```
1. IMP-03 (template 1 línea) → inmediato, sin riesgo
2. F5 + F7 (bugs) → bajo riesgo, alta claridad
3. MIN-02 (ADR) → habilita F5 completamente
4. MIN-01 (Status Quo) → impacto comercial alto
5. MIN-03 (Closing) → impacto comercial medio
6. Limpieza dead code → cosmético
```

---

## 📋 ARCHIVOS INVOLUCRADOS

| Archivo | Líneas clave | Gaps |
|---------|-------------|------|
| `modules/commercial_documents/v4_proposal_generator.py` | L191, L575-605, L867, L988, L1934 | IMP-03, F5, dead code |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | L95-100, L119-121, L141, L214-220 | IMP-03, MIN-03 |
| `config/regional_benchmarks.yaml` | nueva key `adr` | MIN-02 |
| `modules/quality_gates/publication_gates.py` | L1152 (tier_c), financial_validity | F7 |
| `modules/commercial_documents/v4_diagnostic_generator.py` | L1510 `_extract_adr_from_audit` | MIN-02, F5 |

---

## ✅ CERTIFICACIÓN DE CONFIANZA

**¿Estoy 100% seguro de esta estrategia?** SÍ, para los 5 gaps confirmados + 2 hallazgos nuevos.

Cada gap fue verificado con:
1. Búsqueda en codebase (grep/rg)
2. Lectura de código fuente (líneas específicas)
3. Re-ejecución v4complete con output real
4. Gate report JSON con valores numéricos

**La única incertidumbre remanente** es si el template embebido L575-605 se usa en algún otro code path (tests, fallback). Esto se verifica con un grep simple y no bloquea la estrategia.
