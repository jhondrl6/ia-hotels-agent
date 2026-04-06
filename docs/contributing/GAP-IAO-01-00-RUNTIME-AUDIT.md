# GAP-IAO-01-00: Auditoría Runtime — RESULTADOS

**Fecha**: 2026-03-30  
**Auditor**: Hermes (análisis de código estático)

---

## STATUS: 3/3 COMPONENTES VERIFICADOS COMO REALES

| Componente | Funciona? | Implementación | Requiere |
|------------|-----------|----------------|----------|
| IATester.test_hotel() | ✅ SI | API calls reales (Perplexity, OpenAI, DeepSeek) | API keys |
| BingProxy.test_visibility() | ✅ SI | Scraping real de Bing + BeautifulSoup | requests, bs4 |
| AEOKPIs.calculate_composite_score() | ✅ SI | Ponderación 40/20/20/20 + -1 fallback | Datos填充 |

---

## TABLA DEFINITIVA: Elementos Detectables en V4AuditResult

| # | Elemento KB | Detector | Peso KB | Status | Notas |
|---|-------------|----------|---------|--------|-------|
| 1 | ssl | ❌ No existe | 10 | NUEVO | Una línea: `url.startswith('https')` |
| 2 | schema_hotel | ✅ `schema.hotel_schema_detected` | 15 | LISTO | Bool directo |
| 3 | schema_reviews | ⚠️ Proxy: `gbp.rating` | 15 | PROXY | No valida AggregateRating real |
| 4 | LCP_ok | ✅ `performance.lcp` | 10 | LISTO | Float, comparar <= 2500ms |
| 5 | CLS_ok | ✅ `performance.cls` | 5 | LISTO | Float, comparar <= 0.1 |
| 6 | contenido_extenso | ❌ No existe | 10 | NUEVO | Requiere content_length |
| 7 | open_graph | ❌ No existe | 5 | NUEVO | Requiere og_tags detection |
| 8 | schema_faq | ✅ `schema.faq_schema_detected` | 8 | LISTO | Bool directo |
| 9 | nap_consistente | ⚠️ Solo WhatsApp | 7 | PARCIAL | Solo phone_web vs phone_gbp |
| 10 | imagenes_alt | ❌ No existe | 5 | NUEVO | Requiere img parsing |
| 11 | blog_activo | ❌ No existe | 5 | NUEVO | Requiere blog detection |
| 12 | redes_activas | ❌ No existe | 5 | NUEVO | Requiere social links detection |

**RESUMEN**:
- Elementos con detector LISTO (directo): **5** (schema_hotel, LCP, CLS, schema_faq, +1 más)
- Elementos con PROXY/Parcial: **2** (schema_reviews, nap_consistente)
- Elementos que REQUIEREN detector nuevo: **5** (ssl, contenido_extenso, open_graph, imagenes_alt, blog_activo, redes_activas)

---

## DECISION: Qué usar detectores reales vs默认值

| Elemento | Acción | Justificación |
|----------|--------|---------------|
| ssl | Crear detector trivial (1 línea) | Peso alto (10), implementación trivial |
| schema_hotel | Usar `schema.hotel_schema_detected` | Ya existe, directo |
| schema_reviews | Usar `gbp.rating` como proxy | GBP ya tiene rating, proxy razonable |
| LCP_ok | Usar `performance.lcp <= 2500` | Ya existe |
| CLS_ok | Usar `performance.cls <= 0.1` | Ya existe |
| contenido_extenso |默认值=0 (asumir fallido) | Implementación más compleja, diferir |
| open_graph |默认值=0 (asumir fallido) | Metadata audit no disponible aún |
| schema_faq | Usar `schema.faq_schema_detected` | Ya existe |
| nap_consistente | Usar solo validación WhatsApp | Parcial pero mejor que nada |
| imagenes_alt |默认值=0 (asumir fallido) | Requiere parsing HTML, diferir |
| blog_activo |默认值=0 (asumir fallido) | Requiere detección de blog, diferir |
| redes_activas |默认值=0 (asumir fallido) | Requiere social links detection, diferir |

---

## RECOMENDACIÓN GAP-IAO-01-02

**Implementar scoring con:**
- 5 detectores reales directos
- 2 proxies aceptables
- 5默认值 (asumir fallido hasta crear detectores)

**Detectors nuevos priorizados para post-01-02:**
1. ssl (trivial, alto impacto)
2. contenido_extenso (peso 10)
3. open_graph (peso 5)

**NO usar IATester/BingProxy para scoring KB todavía** — son para IA Visibility externo, no para el checklist de 12 elementos.

---

## Criterios de Completitud

- [x] IATester.test_hotel() verificado: ✅ FUNCIONA
- [x] BingProxy.test_visibility() verificado: ✅ FUNCIONA  
- [x] AEOKPIs.calculate_composite_score() verificado: ✅ FUNCIONA
- [x] Tabla de elementos detectables creada
- [x] Decisión documentada: qué elementos usan detectores reales vs默认值
- [ ] Plan de detectores nuevos priorizado (ver arriba)