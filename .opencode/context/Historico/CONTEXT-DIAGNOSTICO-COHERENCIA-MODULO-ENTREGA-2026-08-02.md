# Contexto: Diagnóstico V6 — Desconexiones Módulo ↔ Entrega (Zione 2026-08-01)

> **Origen**: Validación de coherencia módulo-vs-entrega solicitada por usuario (2026-08-02) sobre `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260801_170539.md`
> **Versión actual**: v4.68.0 (frontmatter del diagnóstico) · v4.69.0 en RELEASE (plan DELIVERY-ZIP-SINGLE-WRITE)
> **Hotel de referencia**: Zione / Zi One Luxury (https://zione.co/) — Pereira, Eje Cafetero
> **Severidad**: ALTA — 2 desconexiones críticas (D1 contenido falso para el cliente; D2 conteos de brechas incoherentes) + 9 adicionales. El pipeline publica gates PASSED con un documento que contradice su propia evidencia.
> **Fecha del contexto**: 2026-08-02
> **Outputs de referencia**:
>   - `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260801_170539.md` (301 líneas, 14.2KB)
>   - `output/v4_complete/v4_complete_report.json` (opportunity_scores, pricing — SIN key "gates"; los gates viven en gate_report_*.json) [R1]
>   - `output/v4_complete/zione/v4_audit/audit_report_20260801_170528.json`
>   - `output/v4_complete/zione/v4_audit/financial_scenarios_20260801_170528.json`
>   - `output/v4_complete/zione/v4_audit/pain_ledger.json` + `pain_ledger_resolved.json`
>   - `output/v4_complete/zione/v4_audit/gate_report_20260801_170540.json`
>   - `output/v4_complete/zione/v4_audit/geo_flow_result.json` + `ia_readiness_report.json`
>   - `output/v4_complete/zione/v4_audit/commercial_gates_report.json` (STALE — 2026-07-30)
>   - `output/clientes/zi-one-luxury_onboarding.yaml` (Tier A: 34 hab, 800 res/mes, ADR 290K, canal 40%)
> **ESTADO**: Validado EXHAUSTIVAMENTE contra código vivo + filesystem (2026-08-02). 12 hallazgos (D1-D12) confirmados con evidencia dura (rutas + líneas + matemática de pesos). Listo para plan de implementación en NUEVA sesión.
> **RE-AUDITORÍA (2026-08-03, Hermes Agent)**: Verificación independiente de TODOS los hallazgos contra código vivo + outputs + ZIP de entrega. Resultado: **12/12 CONFIRMADOS** (matemática recalculada al peso, líneas verificadas) + **9 ampliaciones nuevas (N1-N9**, 2 de severidad ALTA) + **4 inexactitudes menores del propio documento corregidas (R1-R4)**. Ver §3.4 (N1-N9), §4.1, §7 y §8.
> **Validación**: Trazado de cada cifra del documento → módulo productor (audit/financial/pain_ledger/gates) → código (v4_diagnostic_generator.py, pain_solution_mapper.py, google_places_client.py, scenario_calculator.py, opportunity_scorer.py, pillar_maturity_curve.py, publication_gates.py, main.py, template V6). No se re-ejecutó v4complete (solo inspección de outputs del run 2026-08-01 17:05:39 + lectura de código).

---

## 1. RESUMEN EJECUTIVO

El diagnóstico del 2026-08-01 fue publicado con `gate_status: PASSED` y `coherence_score: 0.9168`, pero la validación módulo↔entrega encontró **12 desconexiones (D1-D12)**, ampliadas a **21 hallazgos con la re-auditoría del 2026-08-03 (N1-N9)**. La mayoría de las cifras financieras y de audit son correctas y trazables (tier B+, $7.192.000/mes, OTA real $20.880.000, conflicto WhatsApp, scores GEO/SEO/AEO/IAO, métricas IA). Los problemas están en la **capa de traducción a documento** y en **sistemas paralelos de detección, costo y recuperación** — no dos, sino TRES capas de dinero independientes (brechas, opportunity_scores y recuperación proyectada: D2/D3/N1):

- **D1 (CRÍTICO)**: El doc vende "Sin Meta Tags Sociales (Open Graph)" con costo $958.694/mes cuando el propio audit detecta 8 tags OG completos con imagen real. El mismo doc, en el breakdown AEO, acredita "✅ open_graph(15%)". Mismo dato, dos conclusiones opuestas en el mismo documento.
- **D2 (CRÍTICO)**: Tres conteos de brechas en el mismo run: 9 en pain_ledger.json, 4 mostradas con costo en el doc, "7 brechas técnicas detectadas" (texto hardcodeado en el template). Causa raíz: doble invocación de `detect_pains()` con inputs distintos.
- **D3**: opportunity_scores del JSON report ($3.667.920…) ≠ costos del doc ($2.996.906…) para la misma brecha — dos sistemas de costo paralelos.
- **D4**: Los escenarios reales del módulo (conservative=19.6M, optimistic=-6.8M) nunca aparecen; el doc usa un rango sintético ±20%. El techo del rango (8.63M) es menor que el peor caso del módulo (19.6M).
- **D5**: El gate `coverage_no_silent_drop` pasó con `covered=0` — no puede detectar drops silenciosos.
- **D6**: "Sin Datos de Campo — el sitio puede ser nuevo o tener tráfico bajo" enmascara la causa real: API key de PageSpeed inválida.
- **D7**: "un hotel con 203 reseñas" (texto estático) vs 966 reviews reales en el mismo doc.
- **D8**: GEO 78 atribuido a "algoritmo de Google" — es fórmula local de iah-cli.
- **D9**: Target de fotos del doc (20) ≠ target del auditor (40+).
- **D10**: "Instagram, Instagram, Facebook" — sin dedup, omite TikTok/YouTube.
- **D11**: commercial_gates_report.json stale (07-30) con CG-ROI-NEGATIVE BLOCKING viaja DENTRO del ZIP del 08-01.
- **D12**: occupancy_rate etiquetado "regional" pero calculado de onboarding (800/1020=0.7843).

---

## 2. METODOLOGÍA DE VALIDACIÓN

1. Leer el documento entregado y extraer TODAS las cifras/afirmaciones.
2. Leer los outputs crudos del mismo run (timestamp 1705x): audit_report, financial_scenarios, pain_ledger(+resolved), gate_report, geo_flow_result, ia_readiness_report, v4_complete_report.json.
3. Para cada cifra, rastrear el método productor en código (grep + lectura de secciones exactas).
4. Recalcular matemáticamente los pesos (suma 0.60 → 4 brechas) y los escenarios.
5. Verificar el estado de cada gate y su semántica real en publication_gates.py.
6. Comparar con convenciones de skills previos (iah-cli-output-forensics, iah-cli-data-provenance-forensics, iah-cli-audit-diagnostic-scorecard).

---

## 3. HALLAZGOS DETALLADOS

| ID | Severidad | Hallazgo | Evidencia (ruta:línea) | Causa raíz |
|----|-----------|----------|------------------------|------------|
| D1 | CRÍTICA | Brecha "Sin OG" falsa + contradicción con breakdown AEO | audit_report:305-319 (open_graph=true, 8 tags, og:image real) · pain_solution_mapper.py:543-555 (rama enhance_existing) · doc líneas 61-64 vs 137 | `_pain_to_brecha` (v4_diagnostic_generator.py:2944-2947) ignora pain.name del mapper y usa narrativa estática "Sin" |
| D2 | CRÍTICA | 9 vs 4 vs "7" brechas | pain_ledger.json (9) · v4_diagnostic_generator.py:2853-2864 (fake ValidationSummary en _identify_brechas) · template diagnostico_v6_template.md:66 (hardcode "7") · pesos doc suman 0.60 | Doble invocación de detect_pains con inputs distintos (generator vs orquestador) |
| D3 | ALTA | Costos de brechas duplicados y divergentes | v4_complete_report.json:320-377 (3.667.920/3.667.920/2.373.360/2.373.360) vs doc (2.996.906/1.438.400/1.798.000/958.694) · v4_diagnostic_generator.py:3217-3230 vs 2397-2407 | P1 parallel consumers: OpportunityScorer vs pesos normalizados |
| D4 | ALTA | Escenarios reales ocultados; rango no contiene peor caso | financial_scenarios.json:11-15 (19.6M/7.2M/-6.8M) · doc:195-197 (±20% sintético) · v4_diagnostic_generator.py:1063-1079 (workaround FASE-A E1) · scenario_calculator.py:245/300/358 (prob 0.70/0.20/0.10) | Escenarios del módulo invertidos en semántica; generator los enmascara |
| D5 | ALTA | Gate cobertura con covered=0 | gate_report:169-181 · publication_gates.py:1263-1276 (status justificado tiene prioridad sobre covered) | _JUSTIFIED_STATUSES exime a ASSET_GENERATED de aparecer en el doc |
| D6 | ALTA | Falsa explicación Core Web Vitals | audit_report:43-51 (status ERROR, "API key not valid") · doc:188 · v4_diagnostic_generator.py:1741 (hardcode "puede ser nuevo o tener tráfico bajo") | Texto estático no lee performance.status/message |
| D7 | MEDIA | "203 reseñas" estático vs 966 reales | v4_diagnostic_generator.py:316 (hardcode) · doc:148 vs 172 (audit gbp.reviews=966) | Texto de ejemplo nunca parametrizado |
| D8 | MEDIA | Atribución falsa "algoritmo de Google" | doc:140,299 · google_places_client.py:177-193 (fórmula local: rating/5×30 + reviews/100×2 + fotos×0.5 + 10 + 10, /90×100) | Texto del template no describe la fuente real |
| D9 | BAJA | Target fotos 20 vs 40+ | v4_diagnostic_generator.py:1737 (`20 - photos`) · audit_report:101 ("target: 40+") | Constante local duplicada |
| D10 | BAJA | "Instagram, Instagram, Facebook" | v4_diagnostic_generator.py:1854-1862 (`social[:3]` sin dedup) · audit_report:321-328 (6 links: 2 IG, 2 FB, TikTok, YouTube) | Sin deduplicación + tope 3 antes de dedup |
| D11 | BAJA→MEDIA | commercial_gates_report.json stale (07-30) dentro del ZIP del 08-01 | ls: ambos archivos 07-30 14:37 (zione/v4_audit/ y deliveries/zione_20260801/ASSETS/v4_audit/) · main.py:2898 lee la ruta stale · v4_proposal_generator.py:629 escribe | El run 08-01 no regeneró el reporte de gates comerciales; el packager copió el archivo stale al ZIP |
| D12 | MEDIA | occupancy etiquetada "regional" pero derivada de onboarding | main.py:1763 (`reservas_mes/(rooms*30)` = 800/1020 = 0.78431 EXACTO) · main.py:1878/1937 (label por feature flag, no por origen real) · financial_scenarios.json:32 | Label de procedencia calculado desde config preference, no desde el origen del valor (P3) |

### 3.1 Matemática que prueba D2 (pesos)

Doc: Schema 41.67%, FAQ 20%, IA Bloqueada 25%, OG 13.33% → costos = 7.192.000 × peso.
Pesos YAML (config/regional_benchmarks.yaml pain_narratives): no_hotel_schema 0.25, no_faq_schema 0.12, ai_crawler_blocked 0.15, no_og_tags 0.08 → **suma 0.60**.
0.25/0.60 = 41.67% ✓ · 0.12/0.60 = 20% ✓ · 0.15/0.60 = 25% ✓ · 0.08/0.60 = 13.33% ✓.
`_normalize_weights` (v4_diagnostic_generator.py:3013-3028) normaliza sobre la lista COMPLETA recibida → la lista tenía EXACTAMENTE esos 4. Si hubiera tenido los 9 del ledger (suma ~1.20+), Schema habría sido ~20%. Conclusión: `_identify_brechas` del generator devolvió 4; el orquestador registró 9.

### 3.2 Detecciones paralelas divergentes (raíz de D2)

| Pain | Ledger (orquestador) | Doc (generator) |
|------|---------------------|-----------------|
| no_hotel_schema, no_faq_schema, ai_crawler_blocked, no_og_tags | ✓ | ✓ (4 brechas con costo) |
| whatsapp_conflict | ✓ | solo alerta en sección 1, no brecha |
| no_whatsapp_visible, low_seo_score, no_analytics_configured, low_organic_visibility | ✓ | ✗ ausentes |
| low_gbp_score | ✗ (GEO 78 ≥ 70) | ✗ (correcto) |

`_identify_brechas` (v4_diagnostic_generator.py:2823-2864) construye un `ValidationSummary(fields=[], overall_confidence=UNKNOWN)` sintético y pasa `whatsapp_html_detected` desde un getattr — inputs ≠ a los del orquestador → conjuntos distintos. El orquestador detecta con inputs reales en main.py:2333-2336; el generator se invoca desde 4 puntos (main.py:2638, main.py:3290, generator:3069 `_get_brecha_pesos`, generator:3173 `_compute_opportunity_scores`) pero el caché (L2839-2840) congela la detección sintética para todos. [R3 — el original decía "2 invocaciones"; son 2 sistemas (orquestador vs generator) con 4 consumidores del generator]

### 3.3 Lo que SÍ es coherente (no tocar)

- $7.192.000 central y $20.880.000 OTA (financial_scenarios) ✓
- Tier B+ con disclaimers honestos (GA4/GSC no configurados declarados) ✓
- Conflicto WhatsApp (web 3103724544 vs GBP 3116079036) ✓
- GEO 78 (fórmula local) y promedio regional 77 (mean competidores 81/80/79/77/72 = 77.8 — el doc trunca a 77; redondeando sería 78) [R4]
- SEO 25, AEO 15, IAO 50 con breakdowns matemáticamente consistentes ✓
- IA-Readiness 117.5, Citabilidad 56.1/24 bloques, Accesibilidad 0.50/14 bloqueados, Salud Técnica GEO 23 ✓
- "IA Bloqueada" soportada por evidencia (14 crawlers bloqueados) ✓
- Fuga 6m $43.152.000, brechas suman 7.192.000 ✓
- 10 assets ≥ 0.7 confidence, 7/7 servicios alineados ✓

### 3.4 Ampliaciones de la re-auditoría 2026-08-03 (N1-N9)

Hallazgos NUEVOS no cubiertos por el documento original, todos verificados contra código vivo con matemática recalculada.

| ID | Severidad | Hallazgo | Evidencia (ruta:línea) | Causa raíz |
|----|-----------|----------|------------------------|------------|
| N1 | ALTA | TERCER sistema de dinero: "recuperación proyectada 6m" diverge 3.2× entre artefactos del MISMO run: diagnóstico $3.020.634 (43.152.000 × 20% × 35%, doc:203-204) vs propuesta $9.691.220 (7.192.000 × 0.35 × 3.85 = curva de maduración) vs pain_ratio 0.0724 (financial_scenarios pricing) | pillar_maturity_curve.py:22 (CURVA_4_PILARES=[0.15,0.35,0.60,0.80,0.95,1.00]) · v4_proposal_generator.py:1062 (`recuperacion_proyectada_6m`) · financial_scenarios.json pricing.pain_ratio=0.0724 | 3 módulos de dinero independientes (diagnóstico, propuesta, pricing) sin fuente única de recovery |
| N2 | ALTA | Gate `hard_contradictions` PASÓ con count=0 pese a contradicción directa doc↔audit (OG: "Sin Meta Tags" vs 8 tags). Solo inspecciona conflicts/validation_summary del assessment, NUNCA el documento generado vs audit | publication_gates.py:240-270 (`_hard_contradictions_gate` lee assessment, no el doc) · gate_report: "No hard contradictions detected (count: 0)" | Misma clase de bug que D5: gates validan INPUTS, no el artefacto que publican |
| N3 | MEDIA | El doc 01-08 es BYTE-IDÉNTICO al 31-07 salvo 3 líneas (generated_at, version 4.67→4.68, reviews 965→966). La "nueva versión" es copia del run anterior con hardcodes intactos | diff binario de `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260731_164842.md` vs `..._20260801_170539.md` (ambos 14.219 bytes, 13 líneas de diff) | Textos estáticos nunca parametrizados (prueba estructural, no run puntual) |
| N4 | MEDIA | D11 es SISTÉMICO: además de commercial_gates_report.json, el ZIP del 08-01 contiene 7 gate reports HISTÓRICOS (4× 28-07, 30-07, 31-07) | unzip: ASSETS/v4_audit/gate_report_20260728_*.json (4), ..._20260730_, ..._20260731_ + commercial_gates_report.json (07-30) | El packager copia el directorio v4_audit COMPLETO sin filtrar por run_id |
| N5 | BAJA | "La cifra acima es nuestra mejor estimación" — PORTUGUÉS en plantilla española | diagnostico_v6_template.md:57 (doc:81) | Plantilla heredada no revisada |
| N6 | BAJA | "Por que importa" sin acento | v4_diagnostic_generator.py:2458 (doc:48) | Texto de generador sin revisión ortográfica |
| N7 | BAJA | Tabla RESUMEN trunca descripciones a 80 chars a mitad de palabra ("Pérdida absoluta de rese...") | v4_diagnostic_generator.py:2471 (`detalle_corto = b.get('detalle','Sin resumen')[:80]`) · doc:251-254 | Slice crudo sin corte por palabra |
| N8 | BAJA | doc:231 dice "Esta estimación está con 70% de confianza" para $7.192.000 cuando el 70% es la probabilidad del escenario conservative (19.6M) — confianza mal atribuida | doc:231 vs scenario_calculator.py:245 (prob 0.70 del conservative) | Extensión de D4: probabilidades y labels cruzados |
| N9 | INFO | execution_trace.skipped=["pagespeed_api"] + performance.status="ERROR" — dos señales para el mismo fallo de API key | audit_report_20260801_170528.json execution_trace.skipped · performance.status | Refuerza D6: el estado real del fallo se registra pero el doc lo enmascara |

**Matemática N1 (recalculada)**:
- Diagnóstico: $43.152.000 × 0.20 × 0.35 = $3.020.640 (doc muestra 3.020.634 — redondeo de 6 COP).
- Propuesta: $7.192.000 × 0.35 × (0.15+0.35+0.60+0.80+0.95+1.00 = 3.85) = $9.691.220 EXACTO.
- Módulo: pain_ratio = 0.0724 (pricing hybrid_v410) — tercer valor para "cuánto de la fuga se recupera".
- Conclusión: el MISMO concepto ("recuperación proyectada 6m") tiene 3 implementaciones; doc y propuesta del mismo run divergen 3.2×.

**Matemática N2 (contexto del bug)**: el validation_summary del assessment solo contiene el conflicto WhatsApp (severity no-HARD) → hard_count=0 → PASSED. La contradicción OG es ENTRE el texto del doc y el audit, no dentro del validation_summary; ningún gate lee el documento generado.

**Matemática N3 (prueba)**: `cmp -s` de los dos docs → difieren SOLO en generated_at, version y reviews (965→966). Los hardcodes (203 reseñas, 7 brechas, 20 fotos, ±20%, Instagram×2, "algoritmo de Google") persisten idénticos entre runs.

---

## 4. MAPEO DE ARCHIVOS AFECTADOS

### 4.1 Archivos a MODIFICAR

| Archivo | Hallazgo | Cambio | Prioridad |
|---------|----------|--------|-----------|
| `modules/commercial_documents/pain_solution_mapper.py` | D1 | Ya distingue missing vs incomplete en pain.name ("Sin Open Graph Tags" vs "Open Graph Tags Incompletos") — mantener esa info | P0 |
| `modules/commercial_documents/v4_diagnostic_generator.py` | D1, D2, D3, D4, D6, D7, D9, D10 | `_pain_to_brecha` usa pain.name/description en vez de narrativa estática; `_identify_brechas` recibe VS real (firma); costo único (D3); escenarios honestos (D4); textos dinámicos (D6/D7/D9/D10) | P0-P2 |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | D2, D8 | Conteo de brechas dinámico ("De las N brechas…"); corregir atribución GEO ("algoritmo de Google" → "algoritmo propio de iah-cli sobre datos de Google Places") | P1 |
| `modules/quality_gates/publication_gates.py` | D5 | `_coverage_gate`: covered debe contar pains que aparecen en docs ANTES de eximir por status justificado; o fallar si covered=0 y hay pains sin assets | P1 |
| `main.py` | D2, D12 | Pasar validation_summary/analytics_data reales a `_identify_brechas` (una sola fuente de detección); label occupancy desde origen real del valor (1763 vs 1878/1937) | P1 |
| `modules/financial_engine/scenario_calculator.py` | D4 | Decidir semántica: conservative=peor caso con label honesto, o conservative=límite inferior; probabilidades coherentes con labels | P1 |
| `modules/commercial_documents/v4_proposal_generator.py` | D11, N1 | Escribir commercial_gates_report.json SIEMPRE en cada generación de propuesta (ruta canónica output_dir/hotel_id/v4_audit/); `recuperacion_proyectada_6m` (L1062) debe salir de la MISMA fórmula que el diagnóstico | P2 |
| `modules/financial_engine/pillar_maturity_curve.py` | N1 | Unificar fórmula de recuperación proyectada 6m: decidir entre pain_ratio×recovery (diagnóstico) o curva de maduración (propuesta); documentar la relación | P1 |
| `modules/financial_engine/opportunity_scorer.py` | N1, D3 | `estimated_monthly_cop` (L566: total_loss × score/100 / n × 2) debe salir de la MISMA fuente que `_get_brecha_costo` (pesos normalizados) — hoy usa monthly_loss_max del rango sintético | P1 |
| `modules/quality_gates/publication_gates.py` | N2 | `_hard_contradictions_gate` (L240-270) debe leer el DOC generado vs audit (pares clave: OG tags, reviews, fotos, performance.status), no solo el assessment | P1 |
| `modules/delivery/delivery_packager.py` | N4 | (opcional, NO bloquear v4.69.0 — respetar CONTEXT-DELIVERY-ZIP-PACKAGING-BROKEN) filtrar v4_audit por run_id o emitir warning por artefactos con timestamp anterior al run | P2 |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | N5 | "La cifra acima" (portugués, L57) → "La cifra arriba" | P2 |
| `modules/commercial_documents/v4_diagnostic_generator.py` | N6, N7, N8 | "Por que importa" → "Por qué importa" (L2458); truncamiento `[:80]` a corte por palabra (L2471); corregir "70% de confianza" mal atribuido (doc:231, ver D4/N8) | P2 |
| `modules/commercial_documents/data_structures.py` | D4 | (opcional) Scenario.monthly_loss_min/central/max: documentar relación con conservative/optimistic | P2 |

### 4.2 Archivos que se MANTIENEN (con razón)

| Archivo | Razón |
|---------|-------|
| `modules/financial_engine/scenario_calculator.py` (cálculos de pérdida) | Los valores centrales son correctos ($7.19M verificado contra onboarding 800×290K×15% = $20.88M OTA; realistic = OTA − shift − IA boost). NO tocar fórmulas hasta decidir D4 semántica |
| `modules/scrapers/google_places_client.py:177-193` | Fórmula geo_score correcta y consistente (78 = 70.72/90×100). El problema es la ATRIBUCIÓN en el template, no la fórmula |
| `modules/financial_engine/feature_flags.py` | La etiqueta "regional" en occupancy viene de `should_use_regional_for` — el FIX es en main.py (etiquetar por origen real), no cambiar flags |
| `modules/asset_generation/*`, `delivery_packager.py` | Fuera de alcance (assets OK; ZIP single-write ya resuelto en v4.69.0) |
| `data/benchmarks/plan_maestro_data.json`, `config/regional_benchmarks.yaml` | Valores de referencia OK (aeo 44, seo 59, iao 20, pain_narratives). El problema es quién los consume |

### 4.3 Dead code / texto muerto adicional

| Elemento | Ubicación | Motivo |
|----------|-----------|--------|
| Texto "un hotel con 203 reseñas" | v4_diagnostic_generator.py:316 | Ejemplo estático que contradice datos reales → parametrizar o eliminar |
| "El sitio puede ser nuevo o tener tráfico bajo" | v4_diagnostic_generator.py:1741 | Enmascara errores reales de API → leer performance.status |
| "Mínimo garantizable/Más probable/Máximo alcanzable" con probabilidades 70/20/10 | v4_diagnostic_generator.py:1087-1099 | Semántica invertida (el "más probable" tiene 20%) |
| `financial_method: "proportional_normalized"` | v4_diagnostic_generator.py:1240 | Label hardcodeado que no describe cálculo real → derivar de la fuente usada |

---

## 5. DETALLE DE CAMBIOS PROPUESTOS (por hallazgo)

> Regla de oro: una fuente de verdad por concepto. Detección (1), costos (1), labels de origen (1).

### FASE-1 (P0 — contenido veraz): D1 + D2

**D1 — `_pain_to_brecha` (v4_diagnostic_generator.py:2886-3006):**
```python
# ANTES: narrative = narratives[pain.id]; nombre/detalle SIEMPRE de la narrativa estática
# DESPUÉS: preferir pain.name / pain.description (el mapper ya distingue
#   "Sin Open Graph Tags" vs "Open Graph Tags Incompletos")
nombre = pain.name or narrative['nombre']
detalle = pain.description or narrative['detalle']
```
- Mantener el special-case de `ai_crawler_blocked` (2983-2998) — ese ya es correcto.
- Impacto: la brecha 4 pasará a decir "Open Graph Tags Incompletos — Se detectaron 8 OG tags pero faltan tags importantes" — veraz y vendible (mejora, no mentira).
- Verificación: `_og_tags_incomplete` ya distingue (pain_solution_mapper.py:633-644, umbral <10).

**D2 — Unificar detección:**
1. Cambiar firma: `_identify_brechas(self, audit_result, validation_summary=None, analytics_data=None, whatsapp_html_detected=None)`.
2. En el cuerpo (2853-2864): usar los parámetros reales; SOLO construir el VS sintético si `validation_summary is None` (fallback).
3. En main.py:2638: `diagnostic_gen._identify_brechas(audit_result, validation_summary=validation_summary, analytics_data=analytics_data, whatsapp_html_detected=...)` — mismo input que el orquestador.
4. El ledger del orquestador debe construirse DESDE la misma lista (main.py ya tiene `brechas_reales` en 2638) — eliminar la segunda invocación.
5. Template diagnostico_v6_template.md:66-67: reemplazar "De las 7 brechas técnicas detectadas" por variable dinámica `${brechas_total_count}` y "Las otras 4" por `${brechas_restantes_count}`.
- Impacto: doc y ledger convergen a N real (9 para Zione); el conteo nunca más queda hardcodeado.
- Verificación: tras el fix, `_get_brecha_pesos` normalizará sobre 9 → Schema ~20.8% (0.25/1.2). Los costos cambiarán; documentar que es el comportamiento correcto.

### FASE-2 (P1 — finanzas honestas): D3 + D4

**D3 — Una sola fuente de costos:**
- Opción A (recomendada): `_compute_opportunity_scores` (3217-3230) recibe los pesos normalizados de `_get_brecha_pesos` y los usa como `estimated_monthly_cop` → el JSON report queda idéntico al doc.
- Opción B: el doc consume `estimated_monthly_cop` del scorer (con channel multipliers) — requiere renormalizar a la suma total.
- Decidir en plan; NO dejar dos números para el mismo concepto.

**D4 — Escenarios honestos:**
- Opción A: el doc muestra los 3 escenarios reales del módulo con labels semánticos correctos: "Peor caso (conservador) 19.6M — 70%", "Más probable 7.19M — 20%", "Mejor caso (optimista) −6.8M (ganancia) — 10%". Nota: −6.8M es GANANCIA neta proyectada (recuperación), debe explicarse.
- Opción B: corregir semántica en scenario_calculator (conservative = límite inferior de pérdida, no peor caso) y recalcular 19.6M.
- Requisito transversal: ejecutar el gate CG-SCENARIO-ORDER (commercial_gate.py:70 ID · implementación `_check_scenario_order` L297-348) DENTRO del pipeline v4 (hoy no corre en el run de diagnóstico) para validar ordenamiento antes de publicar. [R2]
- El `financial_value_range` [5.75M, 8.63M] debe contener el peor caso o renombrarse ("rango ±20% del escenario más probable").

**N1 — Una sola fórmula de recuperación proyectada 6m (ampliación re-auditoría 2026-08-03):**
- Hoy: diagnóstico $3.020.634 = fuga 6m × 20% × 35% (doc:203-204) ≠ propuesta $9.691.220 = fuga mensual × 0.35 × Σ(curva 3.85) (pillar_maturity_curve.py:22, v4_proposal_generator.py:1062) ≠ pain_ratio 0.0724 (financial_scenarios pricing).
- Decisión requerida en plan: (A) la curva de maduración ES la fórmula correcta (más honesta: recuperación crece mes a mes) y el diagnóstico debe usarla también; o (B) mantener pain_ratio×recovery en ambos y eliminar la curva del cálculo de la propuesta. El pain_ratio 0.0724 del módulo pricing debe reconciliarse o documentarse como métrica distinta (relación precio/fuga).
- Verificación: `grep -rn "recuperacion_proyectada_6m\|total_recuperacion_6m" modules/` → debe apuntar a UNA función compartida.

### FASE-3 (P1 — gates y textos): D5 + D6 + D7 + D8

**D5 — `_coverage_gate` (publication_gates.py:1263-1276):**
- Cambiar prioridad: `covered` (aparece en doc) debe contar ANTES; `is_justified` exime solo si el pain además está explicado por un asset. Si `covered=0` y `justified>0`, emitir WARNING en el mensaje ("0 pains aparecen en el documento").
- Ideal: el gate lee los pain_ids REALES del doc generado (diagnostic_pain_ids debe poblarse desde el doc parseado o desde brechas_reales — main.py:2638-2639 ya lo hace).

**N2 — `_hard_contradictions_gate` debe validar el DOCUMENTO, no solo el assessment (ampliación re-auditoría 2026-08-03):**
- El gate (publication_gates.py:240-270) cuenta HARD conflicts del validation_summary/assessment. No puede detectar contradicciones doc↔audit: en el run 08-01 pasó con count=0 mientras el doc decía "Sin Meta Tags Sociales" contra 8 tags OG del audit.
- Propuesta: añadir checks de pares doc↔audit al gate (o a un gate nuevo `doc_audit_consistency`): (a) si audit.seo_elements.open_graph=true → el doc NO puede decir "Sin ... Open Graph"; (b) reviews del doc vs gbp.reviews; (c) fotos target vs photos; (d) performance.status ERROR → el doc no puede decir "sitio nuevo o tráfico bajo". FAILED con mensaje que cite la línea del doc.
- Implementación mínima viable: el generador emite un `evidence_used.json` (o reutiliza diagnostic_pain_ids) con los valores del audit que alimentaron cada sección; el gate compara doc parseado vs evidence_used.

**D6 — v4_diagnostic_generator.py:1741:**
```python
# ANTES: rows.append("| Sin Datos de Campo (Core Web Vitals) | 🟡 Media | El sitio puede ser nuevo o tener tráfico bajo |")
# DESPUÉS: leer audit_result.performance.status/.message
#   status == "ERROR" → "API de PageSpeed no disponible (verificar clave)" — naranja/rojo
#   status OK sin field data → "El sitio puede ser nuevo o tener tráfico bajo" — amarillo
```

**D7 — v4_diagnostic_generator.py:316:** parametrizar con `audit_result.gbp.reviews` o eliminar el ejemplo numérico.

**D8 — template:** "algoritmo propio de Google Business Profile" → "algoritmo propio de IA Hoteles Agent sobre datos de Google Places (rating, reseñas, fotos, horario, web)". Ajustar ambas notas (líneas 140 y 299 del doc = template).

### FASE-4 (P2 — pulido): D9 + D10 + D11 + D12

**D9**: constante compartida `TARGET_GBP_PHOTOS = 40` (v4_diagnostic_generator.py:1737 y auditor/recomendaciones).
**D10**: en 1854-1862: dedupe con `seen` set ANTES de aplicar tope; iterar TODA la lista, no `social[:3]`.
**D11**: (a) v4_proposal_generator.py:629: escribir SIEMPRE commercial_gates_report.json en cada generación de propuesta (ruta canónica `output_dir/hotel_id/v4_audit/`); (b) el packager debe excluir artefactos stale (o regenerarlos); (c) main.py:2898: si el archivo es más viejo que la propuesta, warning "reporte stale".

**N4 — Freshness de evidencia en el ZIP (ampliación re-auditoría 2026-08-03):** el packager copia v4_audit COMPLETO: el ZIP del 08-01 contiene 7 gate reports históricos (4× 28-07, 30-07, 31-07) + commercial_gates_report.json (07-30). El fix de D11 (b) debe cubrir TODO el directorio: filtrar por run_id (timestamp del run) o mover históricos a un subdirectorio `historico/`. NO tocar la arquitectura single-write del packager (v4.69.0); solo el criterio de selección de archivos.

**N3 — Los docs son copias entre runs (ampliación re-auditoría 2026-08-03):** doc 31-07 y 01-08 byte-idénticos salvo timestamp/version/reviews. Refuerza que TODOS los fixes de texto estático (D6/D7/D8/D9/D10, N5-N8) son la prioridad real: mientras existan hardcodes, cada run propaga la misma mentira. Checklist: tras FASE-3, `diff` de dos runs consecutivos debe mostrar cambios > 3 líneas.

**N5-N8 — Pulido de texto:** N5 "acima"→"arriba" (template:57); N6 "Por que importa"→"Por qué importa" (generator:2458); N7 truncamiento `[:80]` a corte por palabra (generator:2471); N8 corregir "70% de confianza" mal atribuido en doc:231 (ver D4).
**D12**: main.py:1878/1937: label occupancy desde el ORIGEN real: si `reservas_mes` existe → "onboarding"; solo "regional" cuando vino de `resolver.resolve_occupancy`.

---

## 6. VERIFICACIÓN POST-IMPLEMENTACIÓN

### Comandos
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
# 1. Tests específicos
venv/Scripts/python.exe -m pytest tests/ -k "pain_solution_mapper or diagnostic_generator or coverage_gate or publication_gates" -x -q
# 2. Baseline E2E (fase 1 y 2): re-ejecutar el run
venv/Scripts/python.exe main.py v4complete --url https://zione.co/ --output output/verify_<id>
# 3. Verificaciones estáticas post-fix
grep -rn "203 reseñas" modules/            # → 0 hits
grep -rn "7 brechas técnicas" modules/     # → 0 hits
grep -rn "algoritmo propio de Google" modules/  # → 0 hits
grep -rn "El sitio puede ser nuevo o tener tráfico bajo" modules/  # → 0 hits (o solo rama correcta)
grep -rn "acima" modules/  # → 0 hits (N5)
grep -rn "Por que importa" modules/  # → 0 hits (N6)
grep -rn "recuperacion_proyectada_6m\|total_recuperacion_6m" modules/  # → UNA definición compartida (N1)
```

### Checklist por hallazgo (comparar contra baseline auditado 2026-08-01)

| Hallazgo | Check |
|----------|-------|
| D1 | Doc muestra "Open Graph Tags Incompletos (8 tags detectados)", no "Sin Meta Tags". Breakdown AEO y brecha 4 ya no se contradicen |
| D2 | pain_ledger.json == brechas del doc (mismo N); template usa conteo dinámico; pesos normalizan sobre N real |
| D3 | `jq '.opportunity_scores[].estimated_monthly_cop' v4_complete_report.json` == costos del doc |
| D4 | Doc muestra escenarios reales del módulo O rango renombrado; gate CG-SCENARIO-ORDER en gate_report del run |
| D5 | gate_report: `covered` > 0 o mensaje honesto; nunca "Coverage completo" con covered=0 |
| D6 | Doc refleja "API key inválida" o el estado real de performance |
| D7 | Sin "203 reseñas" |
| D8 | Atribución GEO correcta en template y doc |
| D9 | "Subir al menos 30 fotos adicionales" (target 40) |
| D10 | "Instagram, Facebook" o similar sin duplicados; TikTok/YouTube si aplican |
| D11 | commercial_gates_report.json fresco (timestamp == run) en zione/v4_audit/ y en el ZIP |
| D12 | financial_scenarios.json: `occupancy: "onboarding"` (o "regional" solo si realmente vino de benchmark) |
| N1 | Diagnóstico y propuesta muestran la MISMA recuperación proyectada 6m (misma fórmula); pain_ratio reconciliado o documentado | 
| N2 | gate_report: hard_contradictions detecta la contradicción OG (o un gate `doc_audit_consistency` la reporta); nunca "No hard contradictions" con doc auto-contradictorio |
| N3 | `diff` entre dos runs consecutivos muestra más de 3 líneas de diferencia (evidencia de parametrización real) |
| N4 | ZIP del run contiene SOLO artefactos v4_audit del run actual (0 archivos con timestamp anterior) |

### Suite completa (delegada a RELEASE)
`venv/Scripts/python.exe -m pytest tests/ -q` — 3,164+ tests (FASE-RELEASE, puede dar timeout; usar `--timeout` o dividir por módulo).

---

## 7. CONTEXTO ARQUITECTÓNICO

### Skills aplicables (cargar en la sesión de plan)
- `iah-cli-output-forensics` — patrones P1 (parallel consumers), template slots fijos, x1.2 inflation, gate discrepancy, subdirectory path mismatch (D11 es exactamente este patrón)
- `iah-cli-data-provenance-forensics` — P3 (false confidence por existencia), P6/P7 (wiring roto), P8 (evidence tier), 3-vocabulario de fuentes ADR
- `iah-cli-audit-diagnostic-scorecard` — scorecards con métricas no accionables; IAO vs AEO (aquí IAO 50 vs AEO 15 son métricas distintas, OK)

### Contextos previos relacionados (en .opencode/context/)
- `CONTEXT-EVIDENCE-TIER-FALSE-CONFIDENCE-IAO-2026-07-30.md` — el fix de tier B+ (sin mentir con A) YA está aplicado y verificado en este run. NO reabrir.
- `CONTEXT-ONBOARDING-INJECTION-GAP-2026-07-28.md` — onboarding como fuente de verdad (relacionado con D12 y origen de datos).
- `CONTEXT-DT4-RESIDUAL-FIXES.md` — patrones P6/P7 del gate coverage (wiring pain_ledger) — base de D5.
- `CONTEXT-DELIVERY-ZIP-PACKAGING-BROKEN-2026-08-01.md` — delivery packager (v4.69.0): NO tocar; D11 solo toca el reporte de gates, no el packager.

### Patrones estructurales identificados (para el plan)
1. **Doble detección de pains** (generator con VS sintético + caché vs orquestador con inputs reales; 4 puntos de invocación: main.py:2638, 3290, generator:3069, 3173) — unificar en una sola llamada con inputs reales (D2).
2. **TRIPLE capa de dinero paralela**: costos de brechas (scorer vs pesos normalizados, D3) Y recuperación proyectada (diagnóstico vs curva de maduración vs pain_ratio, N1) — una sola fuente por concepto.
3. **Labels de procedencia derivados de config, no de origen** (D12, y P2/P3 del skill de provenance).
4. **Texto estático que miente** (D6/D7/D8, N3, N5-N8) — todo texto numérico en templates/generators debe ser parametrizado o eliminado; los docs entre runs son copias byte-idénticas (N3) — prueba estructural.
5. **Gates con semántica débil** (D5 coverage, N2 hard_contradictions) — los gates validan INPUTS (assessment/status), no el ARTEFACTO (documento generado); el pipeline declara PASSED con un doc auto-contradictorio.
6. **Ausencia de freshness en evidencia** (D11, N4) — el packager copia v4_audit completo con históricos; ningún check de edad de artefacto.

---

## 8. RIESGOS

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Unificar detección (D2) cambia los costos de brechas de TODOS los hoteles (pesos sobre N real) | Alta | Medio | Documentar el cambio como corrección de verdad; comparar baseline pre/post; actualizar fixtures de tests |
| Unificar recuperación (N1) cambia la cifra de recuperación de la propuesta vs históricos de ventas (9.69M vs 3.02M) | Alta | Medio | Decidir la fórmula ANTES de implementar; comparar baseline pre/post; actualizar pitch de cierre (ROI) y tests de golden files |
| El gate sobre el documento (N2) empieza a fallar runs existentes con contradicciones hoy invisibles (OG, reviews) | Media | Alto | WARNING primero (no blocking) en un release, BLOCKING después; catalogar contradicciones conocidas antes de activar |
| Filtrar v4_audit por run (N4) puede romper referencias a históricos en MANIFEST.json | Media | Bajo | Mover históricos a `historico/` en vez de borrarlos; verificar MANIFEST.json post-fix |
| D4 (mostrar −6.8M "ganancia") puede confundir al cliente si no se explica | Media | Medio | Label explícito: "escenario optimista = recuperación proyectada (ganancia)"; test de lectura |
| Cambiar `_pain_to_brecha` a pain.name afecta otras narrativas (no solo OG) | Media | Medio | Mapear TODOS los pain.name del mapper vs narrativas del generator; mantener fallback a narrativa |
| El gate coverage (D5) empieza a fallar runs existentes | Media | Alto | Hacerlo WARNING primero (no blocking) en un release, BLOCKING después |
| Tests de golden files (fixtures) se rompen por cambios de texto | Alta | Bajo | Regenerar fixtures con `--rewrite-expected` si existe; revisar tests de delivery/diagnóstico |
| Suite completa 3,164+ da timeout en WSL | Alta | Bajo | Ejecutar por módulo; skip conocido (lección 5 del plan ZIP) |

---

## 9. VALIDACIÓN DE PERTINENCIA — LECCIONES DE `DELIVERY-ZIP-SINGLE-WRITE-2026-08-01/09-documentacion-post-proyecto.md`

**Veredicto: INCLUIR 2 de 5 lecciones, con adaptación; EXCLUIR 3 con razón documentada.**

### INCLUIDAS (pertinentes para este contexto)

1. **Lección 4 — "Onboarding es fuente de verdad"** ✅ INCLUIDA.
   - Pertinencia directa: `output/clientes/zi-one-luxury_onboarding.yaml` (34 hab, 800 res/mes, valor_reserva_cop 290.000, canal 40%) es la fuente de TODOS los valores financieros del run auditado: ADR 290.000 (user_provided ✓), occupancy 0.7843 = 800/(34×30) (main.py:1763), canal 0.4.
   - Uso en este contexto: (a) evidencia de que tier B+ y "$20.880.000 OTA = 480 noches × 290K × 15%" son correctos; (b) sustenta D12 (occupancy etiquetada "regional" pero derivada de onboarding — la nota del YAML dice "Occupancy 78.43%" explícitamente); (c) confirma el patrón P5 conocido: `valor_reserva_cop` se usa como ADR (main.py:1765) — para reservas multi-noche sobreestima; el YAML no tiene campo `adr_cop`.
   - Nota de precisión: la lección llama al YAML "Tier A", pero el evidence_tier del run es B+ (correcto, GA4/GSC no conectados) — el fix P8 ya aplicado no debe revertirse.

2. **Lección 3 — "Evidencia proactiva es crítica"** ✅ INCLUIDA (parcial, como mejora de proceso).
   - Pertinencia: conecta directamente con D11 — el run del 08-01 no dejó evidencia fresca del estado de gates comerciales (commercial_gates_report.json stale 07-30 viajó al ZIP). Un protocolo automático de evidencia post-v4complete (evidence/<run-id>/ con timestamp por artefacto) habría detectado el artefacto stale.
   - Uso: recomendación transversal en el plan (FASE-4), NO bloqueante de los fixes.

### EXCLUIDAS (no pertinentes para ESTE contexto)

3. **Lecciones 1, 2, 5** (single-write architecture, fixed-point iteration, suite 816 tests) ❌ EXCLUIDAS.
   - Razón: pertenecen al subsistema `modules/delivery/` (packager ZIP), ya cubierto por `CONTEXT-DELIVERY-ZIP-PACKAGING-BROKEN-2026-08-01.md` y resuelto en v4.69.0. Este contexto es de coherencia diagnóstico ↔ módulos comerciales; mezclar ambos diluye el alcance de la nueva sesión (una fase = una sesión).
   - La lección 5 (timeout de suite completa → delegar a FASE-RELEASE) se incorpora SOLO como riesgo operativo en §8, no como contenido del plan.

### Dato corroborativo (usar como trazabilidad)
El §Sección F del 09-documentación confirma el mismo E2E que audité: run 2026-08-01 sobre zione.co, "10 gates PASSED, coherence 0.92, realistic $7.19M COP/mes, 10 assets". Coincide 1:1 con los outputs del run — refuerza que la auditoría se hizo sobre el run canónico y que el ZIP de entrega existe (zione_20260801.zip, 194 archivos).

---

## 10. PRÓXIMOS PASOS PARA LA NUEVA SESIÓN

1. **NO ejecutar fixes en esta sesión.** El plan se escribe en `.opencode/plans/` con fases P0→P2 (sugeridas tras re-auditoría 2026-08-03: FASE-1 D1+D2, FASE-2 D3+D4+N1, FASE-3 D5-D8+N2, FASE-4 D9-D12+N3-N8, FASE-5 RELEASE). Los hallazgos N1 (recuperación) y N2 (gate sobre el doc) se incorporan a FASE-2/FASE-3 porque comparten causa raíz con D3/D5; N4 (freshness ZIP) entra en FASE-4 junto a D11; N5-N8 son pulido de texto en FASE-3/FASE-4.
2. Cada fase = una sesión. Al cerrar: checklist de §6 + evidencia + `log_phase_completion.py`:
   ```
   venv/Scripts/python.exe scripts/log_phase_completion.py --fase <N> --desc "<desc>" --tests <N> --archivos-mod <paths> --coherence <0-1> --release 4.70.0
   ```
   (Sin `--status`; `--release` sin prefijo "v"; Version Sync Gate compara CHANGELOG.md [X.Y.Z].)
3. Antes de FASE-1: re-ejecutar baseline `v4complete --url https://zione.co/ --output output/baseline_d1d2` y guardar análisis en `.opencode/plans/context/` (o `Historico/`).
4. Cargar skills: `iah-cli-output-forensics`, `iah-cli-data-provenance-forensics`, `iah-cli-code-modification`, `iah-cli-execution-conventions`.
5. Bloqueo externo conocido: en WSL, `rm`/`shutil.copy`/heredocs pueden ser bloqueados por el safety guard — usar write_file para inputs y rutas explícitas (ver skill `wsl-safety-guard-bypass`).
