# ROICRIII — FASE-6 Resultado y Faltantes

**Fecha**: 2026-05-28
**Estado**: ⏳ INCOMPLETA — Publication readiness: NOT_READY

---

## Resumen Ejecutivo

v4complete para Hotel Castilla Real se ejecutó exitosamente con coherencia 0.83 (≥ 0.80 threshold). Se generaron los 5 niveles de verificación y la mayoría pasaron. Sin embargo, **publication readiness está bloqueado** por un gate de alineación de assets y persisten 2 issues menores.

---

## Lo que PASÓ bien

| Aspecto | Resultado |
|---------|-----------|
| Coherence score | ✅ 0.83 (pre), 0.81 (post) — ambas ≥ 0.80 |
| ROI único | ✅ 2.10X en documento (sin dualidad 0.45X/2.10X) |
| Beneficio neto | ✅ +$5.04M COP positivo |
| % inversión/fuga | ✅ 10.7% (no 14% ni 41%) |
| Trazabilidad origen | ✅ Fuga × Curva × Recovery Factor presente |
| Assets deprecados | ✅ 0 (og_tags_guide, indirect_traffic, local_content_page, optimization_guide ausentes) |
| Piloto 30 días | ✅ Secciones "Quick Wins" + "Piloto de Validación" presentes |
| CAPEX breakdown | ✅ Setup fee $2.5M COP (suyo) + OPEX $400K/mes |
| Garantía KPI | ✅ Día 55: +15% clics directos vs línea base GSC |
| WhatsApp narrativa | ✅ "Auditoría y Optimización de Conversión" (no "Guía de corrección") |
| Mapeo semántico | ✅ "Informe Mensual" ya no fuerza "→ FAQ" como equivalencia |
| Gates pasados | ✅ 9/10 |

---

## Lo que FALTA (Issues Abiertos)

### Issue 1 — BLOQUEANTE: proposal_asset_alignment < 80% (62%)

**Gate**: `proposal_asset_alignment`
**Estado**: ❌ BLOCKED
**Valor**: 62% (threshold: 80%)

**Detalle**:
- Service `Botón de WhatsApp` promete asset `whatsapp_button` — **NO fue generado**
- 5 services alineados (Schema Hotel, Schema Organization, Informe Mensual, Meta Tags OG, Optimización IA)
- 2 services baja calidad (SEO Local → `optimization_guide` 0.5, Página FAQ → `faq_page` 0.5)
- 1 service faltante (Botón de WhatsApp → `whatsapp_button`)

**Impacto**: Publication readiness = NOT_READY. El documento no puede publicarse sin resolver esto.

**Causa raíz probable**: El pipeline de generación de assets no produce `whatsapp_button` cuando el diagnóstico detecta "WhatsApp no coincide". La narrativa de la propuesta menciona "Auditoría y Optimización de Conversión" pero no genera el asset físico.

---

### Issue 2 — SEMÁNTICO: "13% del dolor" persiste en fórmula

**Ubicación**: Línea 128 de `02_PROPUESTA_COMERCIAL_*.md`
```
(13% del dolor priorizado × 35% de recuperación conservadora)
```

**Estado**: ⚠️ Mejorado vs baseline (ya no es línea independiente con "% de IAO-addressable pain"), pero sigue siendo un "número mágico" que necesita explicación adicional.

**Contexto**: Antes aparecía como porcentaje aislacionista. Ahora está embebido en la fórmula de cálculo de recuperación. La trazabilidad origen (línea 129) menciona "Fuga × Curva × Recovery Factor" pero no reconecta con el 13%.

---

### Issue 3 — WARNING: asset_confidence bajo threshold

**Assets bajo 0.7**:
- `faq_page`: 0.5
- `optimization_guide`: 0.5

**Detalle del gate_report**:
```
"2 asset(s) below confidence threshold (0.7)"
"services: SEO Local (optimization_guide), Página de FAQ (faq_page)"
```

**Impacto**: Warning, no bloqueante. Afecta calidad del documento pero no previene publicación.

---

## Métricas Comparativas

| Métrica | Baseline (v4.56.0) | Post-Fix (v4.57.0) | Delta |
|---------|-------------------|---------------------|-------|
| Coherence | 0.83 | 0.83 | → |
| ROI en doc | Dual (0.45X + 2.10X) | Único (2.10X) | ✅ Fix |
| % fuga | 14% (wrong) | 10.7% (correct) | ✅ Fix |
| Assets deprecados | 4 | 0 | ✅ Fix |
| "13% número mágico" | Sí (aislado) | En fórmula (parcial) | ⚠️ Partial |
| Piloto/CAPEX/Garantía | No | Sí | ✅ Fix |
| Publication ready | Unknown | NOT_READY | ❌ Bloqueado |

---

## Acción Requerida

Para completar FASE-6 se necesita:

1. **Resolver `whatsapp_button`**: El pipeline de assets no genera el botón de WhatsApp cuando se detecta la brecha. Requiere fix en `asset_generator.py` o en la lógica de `proposal_generator.py` para generar el asset físico cuando el service lo promete.

2. **Opcional — mejorar "13%"**: Añadir explicación contextual sobre el origen del 13% (subset del dolor IAO-addressable) para eliminar el último número mágico.

3. **Opcional — mejorar confidence de faq_page y optimization_guide**: Enriquecer los assets detectados con más datos del sitio.

---

## Archivos de Evidencia

- `/mnt/c/Users/Jhond/Github/iah-cli/evidence/roicriii-fase-6/`
  - `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260528_151028.md`
  - `02_PROPUESTA_COMERCIAL_20260528_151039.md`
  - `gate_report_20260528_151039.json`
  - `coherence_validation.json` (pre: 0.83)
  - `coherence_validation_post_gen.json` (post: 0.81)
  - `audit_report_20260528_151025.json`
  - `financial_scenarios_20260528_151025.json`
  - `pain_ledger.json`
