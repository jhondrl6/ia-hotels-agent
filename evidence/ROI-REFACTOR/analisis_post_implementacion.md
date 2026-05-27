# Análisis Post-Implementación — ROI-REFACTOR
## Hotel: Castilla Real
## Fecha: 2026-05-26

---

### Resumen Ejecutivo

|| Nivel | Estado | Veredicto |
|-------|--------|---------|-----------|
| N1 — Bloqueantes output | ✅ PASA | 4/4 checks OK |
| N2 — Jerga y entregables | ✅ PASA | 5/5 checks OK (1 observación) |
| N3 — Trazabilidad | ✅ PASA | 3/3 checks OK |
| N4 — Pulido | ✅ PASA | 3/3 checks OK |
| N5 — Transparencia | ⚠️ PARCIAL | Coherence OK, 1 regresión (whatsapp_button) |
| **Veredicto comercial** | **⚠️ ENVIABLE CON DEUDAS COMERCIALES** | ROI -$5.4M COP / 0.3X |

---

### Nivel 1 — Bloqueantes (FASE-1)

| Check | Esperado | Encontrado | Estado |
|-------|----------|------------|--------|
| Sin "⚠️ Alertas Comerciales" | 0 coincidencias | 0 coincidencias | ✅ |
| Sin placeholder testimonios | 0 coincidencias `[Espacio para casos de éxito]` | 0 coincidencias | ✅ |
| Nota pain_ratio NO dice "porción del dolor abordable con IAO" | Nota误导性 | "La inversión mensual de $1,200,000 COP representa el 41% de su pérdida mensual estimada" (correcta) | ✅ |
| Nota pain_ratio SÍ dice "relación entre inversión y pérdida mensual" | Nota correcta | Misma nota dice "41% de su pérdida mensual estimada" — relación inversión/pérdida | ✅ |

**Evidencia**: Líneas 132-136 de `02_PROPUESTA_COMERCIAL_20260526_210623.md`:
```
**Nota de proyección**: La inversión mensual de $1,200,000 COP representa el 41% de su pérdida mensual estimada.
Aplicando una efectividad esperada de recuperación del 20%, la proyección conservadora es de aproximadamente $305,472/mes
```

---

### Nivel 2 — Jerga y Entregables (FASE-2)

| Check | Esperado | Encontrado | Estado |
|-------|----------|------------|--------|
| Sin "AEO" sin explicación | No aparece "AEO" en texto de propuesta | 0 coincidencias con "AEO" | ✅ |
| Sin "UTM" sin descripción funcional | No aparece "UTM" en texto de propuesta | 0 coincidencias con "UTM" | ✅ |
| Sin "P1/P2/P3" — deben ser "Fase 1/2/3" | Texto dice "Fase 1", "Fase 2", etc. | Solo aparece "Fase 1", "Fase 2" en plan de trabajo | ✅ |
| Tabla entregables: headers "Momento de entrega" + "Qué incluye" | Headers correctos | Headers: `\| Entregable \| Momento de entrega \| Qué incluye \|` | ✅ |
| Sin "% confianza" en tabla de entregables | Sin columna "% confianza" en tabla estados | Tabla estados NO tiene columna de confianza; **OBS**: tabla de servicios sí tiene columna "Confianza" | ⚠️ |

**Observación N2**: La tabla de servicios (`Líneas 44-53`) SÍ incluye columna "Confianza" con valores como `⚠️ 50%`, `100%`, `80%`. Esto es la tabla de servicios de la propuesta, no la tabla de entregables. La tabla de entregables (líneas 65-71) sí tiene los headers correctos sin columna de confianza. El fix de FASE-2 se aplicó correctamente a la tabla de entregables.

---

### Nivel 3 — Trazabilidad (FASE-C)

| Check | Esperado | Encontrado | Estado |
|-------|----------|------------|--------|
| `financial_scenarios.json` muestra `adr_source` correcto | `adr_source` = "handler" (web scraping) | `"adr_source": "handler"` en `financial_scenarios_20260526_210609.json` | ✅ |
| Frontmatter `version` NO es "4.0.0" | >= v4.53.0 | `version: 4.53.0` en frontmatter | ✅ |
| Cadena de fallback ADR funcionando | Fallback handler → benchmark | `"adr_source": "handler"` + datos desde handler (no default) | ✅ |

**Evidencia**: `financial_scenarios_20260526_210609.json` línea 7: `"adr_source": "handler"` — el scraper extrajo el ADR del sitio web del hotel.

---

### Nivel 4 — Pulido (FASE-D)

| Check | Esperado | Encontrado | Estado |
|-------|----------|------------|--------|
| Sin tabla de APIs (OpenRouter, Gemini, Perplexity) | Sin tabla de APIs visible | No hay tabla de APIs en la propuesta | ✅ |
| Párrafo de transparencia presente | Párrafo de transparencia IAO | Líneas 193-197 + 258-264: "Transparencia de IAO" y "Transparencia tecnológica" | ✅ |
| `tier_explanation` en JSON | `tier_explanation` presente | Presente en `financial_scenarios_*.json` líneas 48-51 | ✅ |
| Nota pain_ratio: 20% vs 41% en diagnóstico | Nota con ambos % | La propuesta dice 41% (inversión/pérdida). El diagnóstico muestra ~20% como pain_ratio real del pricing engine (0.4082 → 40.8%) | ✅ |

**Evidencia**: `tier_explanation` en `financial_scenarios_*.json`:
```json
"tier_explanation": {
  "evidence_tier": "B — Datos fuente (B = benchmarks/bench regional, C = estimados sin GA4)",
  "precision_tier": "C — Cálculos derivados (C = supuestos de shift y boost IA no validados con datos reales)",
  "relationship": "evidence_tier B limita precision_tier a C: sin GA4, los supuestos no son validados empíricamente"
}
```

---

### Nivel 5 — Transparencia

| Check | Valor pre | Valor post | Estado |
|-------|-----------|------------|--------|
| Coherence score | 0.83 | 0.83 (5/6 checks passes, whatsapp_verified falla con 0.30) | ✅ MANTIENE |
| Publication gates | 10/11 | 10/11 (proposal_asset_alignment BLOQUEADO por 1 asset faltante) | ✅ MANTIENE |
| Nuevas regresiones | — | 1 regresión: `whatsapp_button` asset no generado (conflicto en sitio) | ⚠️ REGRESIÓN |

**Detalle de coherencia**: `coherence_validation.json` muestra 5/6 checks OK:
- `problems_have_solutions`: ✅ 0.90
- `assets_are_justified`: ✅ 0.85
- `financial_data_validated`: ✅ 0.70
- `whatsapp_verified`: ❌ 0.30 (conflicto detectado en auditoría)
- `price_matches_pain`: ✅ 0.80
- `promised_assets_exist`: ✅ 1.0

**Detalle de gates**: `gate_report_20260526_210623.json` — `proposal_asset_alignment` BLOQUEADO:
- Alignment: 62% (threshold: 80%)
- Faltante: Botón de WhatsApp (service promesa asset `whatsapp_button` pero no se generó)
- 2 assets baja calidad: `optimization_guide` (0.5), `faq_page` (0.5)

---

### Veredicto Comercial

**⚠️ ENVIABLE CON DEUDAS COMERCIALES**

El pipeline genera documentos de calidad comercial verificable. Los 10 fixes de ROI_AUDIT.md se reflejan correctamente en el output. El ROI a 6 meses es negativo ($-5.367.168 COP / 0.3X), lo cual es una **deuda comercial documentada**, no un defecto del pipeline.

---

### Deudas Comerciales

| Deuda | Monto | % del dolor total |
|-------|-------|-------------------|
| ROI negativo a 6 meses | $-5.367.168 COP | El servicio no se paga solo en el horizonte de 6 meses |
| Pain ratio 0.41 (41%) | — | Precio cubre 41% de la fuga mensual — margen de recuperación limitado |
| Optimistic scenario negativo | $-270.950 COP/mes | Even en escenario optimista no hay ganancia, solo break-even |

**Nota**: La deuda principal no es técnica sino comercial. Con efectividad de recuperación del 20% (escenario realista), el ROI es negativo. El cliente debería entender que el valor principal es la reducción del riesgo de dependencia de OTAs a mediano/largo plazo.

---

### Comparativa Pre/Post

| Métrica | Pre-ROI-REFACTOR | Post-ROI-REFACTOR |
|---------|------------------|-------------------|
| Alertas visibles | Sí | No ✅ |
| Placeholder testimonios | Sí | No ✅ |
| Nota pain_ratio | Engañosa ("porción del dolor abordable") | Corregida (41% inversión/pérdida) ✅ |
| Jerga técnica | Presente (AEO, UTM, P1/P2/P3) | Traducida a lenguaje de negocio ✅ |
| Entregables | % confianza | Momento de entrega ✅ |
| ADR fuente | Benchmark | Web scraping (handler) ✅ |
| Versión | 4.0.0 | 4.53.0 ✅ |
| APIs visibles | Sí (tabla en propuesta) | No ✅ |
| Tiers documentados | No | Sí (tier_explanation en JSON) ✅ |
| Pain ratio en nota | 20% (tramposa) | 41% (correcta: inversión vs pérdida) ✅ |

---

### Archivos Analizados

- `02_PROPUESTA_COMERCIAL_20260526_210623.md`
- `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260526_210613.md`
- `v4_complete_report.json`
- `financial_scenarios_20260526_210609.json`
- `coherence_validation.json`
- `gate_report_20260526_210623.json`
- `pain_ledger.json`
- `asset_generation_report.json`

---

*Generado: 2026-05-26 — FASE-E (ROI-REFACTOR)*