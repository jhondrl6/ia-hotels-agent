# FASE 0.5: Auditoría Runtime — Verificar Componentes Huerfanos

**ID**: GAP-IAO-01-00  
**Objetivo**: Verificar que los componentes "existen pero no se usan" realmente funcionan, antes de asumir que se pueden integrar  
**Dependencias**: GAP-IAO-01-01 (auditoría de datos - completada)  
**Duración estimada**: 1-2 horas  
**Skill**: systematic-debugging

---

## Contexto

### Problema Descubierto

GAP-IAO-01-01 reveló que **8 de los 12 elementos KB NO existen en V4AuditResult**. Esto质疑 la asumisión de FASE-0 de que "IATester, BingProxy, AEOKPIs ya existen y solo hay que conectarlos".

### Lo que FASE-0 asumió

```
AEOKPIs.calculate_composite_score() → YA EXISTE → usar
IATester.test_hotel() → YA EXISTE → usar
BingProxyTester.test_visibility() → YA EXISTE → usar
```

### Lo que GAP-IAO-01-01 reveló

- V4AuditResult tiene: schema, gbp, performance, validation
- **8 elementos KB faltantes**: ssl, schema_reviews (real), contenido_extenso, open_graph, imagenes_alt, blog_activo, redes_activas
- **NAP parcial**: solo WhatsApp, no dirección ni email
- **Pain IDs inconsistentes**: 2 gaps en _identify_brechas() vs PainSolutionMapper

### Lo que NO sabemos (por eso esta fase)

1. **IATester.test_hotel()** — ¿Funciona o es stub que siempre retorna 0/error?
2. **BingProxyTester.test_visibility()** — ¿Está implementado o es placeholder?
3. **AEOKPIs.calculate_composite_score()** — ¿Da scores útiles (>0) o siempre 0?
4. **¿Cuántos elementos del CHECKLIST_IAO se pueden detectar REALMENTE con el audit actual?**

---

## Tareas

### Tarea 1: Verificar IATester.test_hotel()

**Archivo a investigar**: `modules/analyzers/ia_tester.py`

```bash
# Buscar implementación real vs stub
grep -n "def test_hotel" modules/analyzers/ia_tester.py
grep -n "return {" modules/analyzers/ia_tester.py | head -20
```

**Preguntas**:
- ¿Retorna datos reales o siempre `{'success': False, 'score': 0}`?
- ¿Hace llamadas a APIs reales o es un mock?
- ¿Qué datos necesita como input?

### Tarea 2: Verificar BingProxyTester.test_visibility()

**Archivo a investigar**: `modules/analyzers/bing_proxy_tester.py`

**Preguntas**:
- ¿Está implementado o es un placeholder?
- ¿Hace scraping real o usa datos mock?
- ¿Qué retorna cuando funciona?

### Tarea 3: Verificar AEOKPIs.calculate_composite_score()

**Archivo a investigar**: `data_models/aeo_kpis.py`

**Preguntas**:
- ¿El método existe y está implementado?
- ¿Qué pasa cuando le pasas datos reales vs vacíos?
- ¿Retorna scores distintos de 0 o siempre 0?

### Tarea 4: Crear tabla de elementos detectables

**Basado en V4AuditResult y lo que se puede extraer**:

| Elemento KB | Detector existente | Score KB | Observaciones |
|-------------|-------------------|----------|---------------|
| ssl | ❌ No existe | 10 | Requiere detector nuevo |
| schema_hotel | ✅ audit_result.schema.hotel_schema_detected | 15 | Bool directo |
| schema_reviews | ⚠️ Proxy: gbp.rating | 15 | No valida AggregateRating real |
| LCP_ok | ✅ audit_result.performance.lcp | 10 | Float, comparar <= 2500 |
| CLS_ok | ✅ audit_result.performance.cls | 5 | Float, comparar <= 0.1 |
| contenido_extenso | ❌ No existe | 10 | Requiere content_length |
| open_graph | ❌ No existe | 5 | Requiere og_tags detection |
| schema_faq | ✅ audit_result.schema.faq_schema_detected | 8 | Bool directo |
| nap_consistente | ⚠️ Solo WhatsApp | 7 | Solo phone_web vs phone_gbp |
| imagenes_alt | ❌ No existe | 5 | Requiere img parsing |
| blog_activo | ❌ No existe | 5 | Requiere blog detection |
| redes_activas | ❌ No existe | 5 | Requiere social links detection |

**Elementos que se pueden detectar HOY con el audit existente**: 5 de 12
**Elementos que requieren detectores nuevos**: 7 de 12

### Tarea 5: Decision Tree — ¿Qué hacer con elementos faltantes?

**Opciones para elementos que no se detectan**:

| Opción | Impacto | Trabajo | Resultado |
|--------|---------|---------|-----------|
| A) Crear detectores para todos | Alto | 3-4 semanas | 12/12 elementos |
| B) Crear solo detectores críticos | Medio | 1 semana | 8/12 elementos (ssl, reviews, contenido, og, alt) |
| C) Ignorar elementos faltantes | Bajo | 0 | 5/12 elementos (score incompleto) |
| D) Usar Proxies/Estimaciones | Medio-bajo | 1-2 días | 5/12 + 4 con estimate |

**Recomendación basada en ROI**:
- Opción D: Para elementos faltantes, usar valores por defecto "negativos" (asumir que fallan) hasta que haya detectores reales
- Esto permite que el scoring funcione con 5 elementos reales + 7 "asumidos fallidos"

---

## Entregable: Tabla de Viabilidad de Implementación

```
## VIABILIDAD GAP-IAO-01-02

### Elementos KB detectables con audit actual:
| # | Elemento | Detector | Peso KB | Implementable? |
|---|----------|----------|---------|----------------|
| 1 | ssl | NUEVO (1 línea: url.startswith('https')) | 10 | ✅ Easy |
| 2 | schema_hotel | ✅ schema.hotel_schema_detected | 15 | ✅ Listo |
| 3 | schema_reviews | ⚠️ gbp.rating como proxy | 15 | ✅ Proxy OK |
| 4 | LCP_ok | ✅ performance.lcp | 10 | ✅ Listo |
| 5 | CLS_ok | ✅ performance.cls | 5 | ✅ Listo |
| 6 | contenido_extenso | ❌ Requiere new detector | 10 | ⚠️ Post-GAP |
| 7 | open_graph | ❌ Requiere new detector | 5 | ⚠️ Post-GAP |
| 8 | schema_faq | ✅ schema.faq_schema_detected | 8 | ✅ Listo |
| 9 | nap_consistente | ⚠️ Solo WhatsApp | 7 | ⚠️ Parcial |
|10 | imagenes_alt | ❌ Requiere new detector | 5 | ⚠️ Post-GAP |
|11 | blog_activo | ❌ Requiere new detector | 5 | ⚠️ Post-GAP |
|12 | redes_activas | ❌ Requiere new detector | 5 | ⚠️ Post-GAP |

### Componentes "ya existen":
| Componente | ¿Funciona? | Status |
|------------|-----------|--------|
| IATester.test_hotel() | ❓ No verificado | HUERFANO SOSPECHOSO |
| BingProxy.test_visibility() | ❓ No verificado | HUERFANO SOSPECHOSO |
| AEOKPIs.calculate_composite_score() | ❓ No verificado | HUERFANO SOSPECHOSO |

### DECISIÓN para GAP-IAO-01-02:
- Implementar con 5-6 elementos que YA existen
- Para los demás: usar默认值 (asumir fallido) hasta crear detectores
- NO depender de IATester/BingProxy hasta verificar que funcionan
```

---

## Criterios de Completitud

- [ ] IATester.test_hotel() verificado: ¿funciona o es stub?
- [ ] BingProxy.test_visibility() verificado: ¿funciona o es stub?
- [ ] AEOKPIs.calculate_composite_score() verificado: ¿da scores reales?
- [ ] Tabla de elementos detectables creada
- [ ] Decisión documentada: ¿qué elementos se implementan en 01-02 vs post?
- [ ] Plan de detectores nuevos priorizado

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar GAP-IAO-01-00 como completada
2. **`06-checklist-implementacion.md`**: Agregar fase 0.5
3. **`README.md`**: Actualizar índice con nueva fase
4. **Ejecutar**:
```bash
python scripts/log_phase_completion.py \
    --fase GAP-IAO-01-00 \
    --desc "Auditoría runtime: IATester/BingProxy/AEOKPIs huérfanos, 7/12 elementos requieren detectores nuevos" \
    --check-manual-docs
```
