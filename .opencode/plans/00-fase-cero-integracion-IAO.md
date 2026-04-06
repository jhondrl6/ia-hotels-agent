# FASE 0: Reglas de Integración — GAP-IAO-01

**Propósito**: Definir cómo conectar los componentes existentes del codebase para monetizar las debilidades de la KB en el pipeline Diagnóstico → Propuesta → Assets.

**Fecha**: 2026-03-30
**Estado**: ✅ Revisada (enfoque minimalista)
**Cambio vs versión anterior**: Eliminada sobreingeniería. Se usa lo que existe.

---

## 1. Arquitectura de Score Unificado

### Problema
La KB define `calcular_cumplimiento()` (score técnico 0-100). El sistema tiene `AEOKPIs.calculate_composite_score()` (score IA 0-100). Pero el diagnóstico usa un cálculo inventado.

### Solución: Usar lo que ya existe

```
COMPONENTE EXISTENTE                          FUNCIÓN
─────────────────────────────────────────────────────────────────
AEOKPIs.calculate_composite_score() (línea 98)  Score IA real (IATester + BingProxy)
V4AuditResult (dataclass)                      Contiene datos de auditoría
PainSolutionMapper (línea 44)                   Mapea problemas → assets
conditional_generator                           Genera assets por tipo
```

### Flujo de score

```
INPUT: elementos detectados en auditoría
  │
  ▼
calcular_cumplimiento(elementos) → score_tecnico (0-100)  ← USA KB LÍNEAS 717-751
  │
  ▼
IATester.test_hotel(hotel_data) → ia_result
BingProxyTester.test_visibility(url) → share_of_voice
  │
  ▼
AEOKPIs(
    ai_visibility_score=ia_result.score,      # 0-100
    share_of_voice=share_of_voice,           # 0-100
    citation_rate=ia_result.citation_rate,   # 0-100
) → calculate_composite_score() → score_ia  ← USA MÉTODOS EXISTENTES
  │
  ▼
score_final = (score_tecnico * 0.70) + (score_ia * 0.30)
```

### Reglas de fallback

| Escenario | score_tecnico | score_ia | score_final |
|-----------|---------------|----------|-------------|
| Todo funciona | ✓ (KB算法) | ✓ (AEOKPIs) | Promedio ponderado 70/30 |
| IATester falla | ✓ (KB算法) | Usar BingProxy | 85/15 |
| BingProxy también falla | ✓ (KB算法) | 0 | Técnico puro |
| APIs IA caídas | ✓ (KB算法) | N/A | score_tecnico |

**NOTA**: Los pesos 70/30 son ajustables. Si el usuario tiene más confianza en datos técnicos, cambiar a 80/20.

---

## 2. Mapeo de Debilidades KB → Monetización → Assets

### Problema
La KB lista debilidades en `CHECKLIST_IAO` (líneas 678-710) pero no conecta explícitamente a monetización ni a assets.

### Solución: Tabla de conexión cerrada

| # | Debilidad KB (CHECKLIST) | Detecta en | Score (KB算法) | Monetiza en | Asset que resuelve |
|---|--------------------------|------------|----------------|------------|-------------------|
| 1 | Sin Schema Hotel | Scraping sitio | -15 pts | Propuesta: sin cita IA | `hotel_schema` |
| 2 | Sin aggregateRating | Scraping sitio | -15 pts | Propuesta: sin estrellas | `hotel_schema` (con rating) |
| 3 | SSL/HTTPS incompleto | Scraping sitio | -10 pts | Propuesta: riesgo | Guía SSL |
| 4 | LCP > 2500ms | PageSpeed API | -10 pts | Propuesta: % abandono | Guía optimización LCP |
| 5 | CLS > 0.1 | PageSpeed API | -5 pts | Propuesta: UX | Guía CLS |
| 6 | Contenido < 300 palabras | Word count | -10 pts | Propuesta: SEO bajo | Recomendación contenido |
| 7 | Sin Open Graph | Scraping meta | -5 pts | Propuesta: sin social | Asset meta tags |
| 8 | Sin FAQPage Schema | Scraping sitio | -8 pts | Propuesta: sin rich snippets | `faq_page` |
| 9 | NAP inconsistente | Cross-validation | -7 pts | Propuesta: desconfianza | Guía consistencia NAP |
| 10 | Imágenes sin alt | Scraping img | 0 pts* | Propuesta: IA suboptimal | Asset optimización |
| 11 | Blog inactivo | Scraping | -5 pts | Propuesta: autoridad baja | Estrategia contenido |
| 12 | Sin sameAs | Scraping Schema | 0 pts* | Propuesta: sin KGO | Recomendación sameAs |

*Estos no restan puntos pero afectan el score IA.

### Implementación

```python
# En v4_diagnostic_generator.py
from data_models.aeo_kpis import AEOKPIs
from modules.analyzers.ia_tester import IATester
from modules.analyzers.bing_proxy_tester import BingProxyTester

def calcular_score_completo(audit_result: V4AuditResult, hotel_data: dict) -> dict:
    """
    Calcula score técnico (KB) + score IA (AEOKPIs).
    Retorna dict con score_final y metodología.
    """
    
    # Score técnico: USAR KB ALGORITMO (líneas 717-751 de KB)
    elementos = _extraer_elementos_de_audit(audit_result)  # NEEDS IMPLEMENTATION
    score_tecnico = calcular_cumplimiento(elementos)
    
    # Score IA: USAR AEOKPIs con datos reales
    ia_score = None
    data_source = "N/A"
    
    ia_tester = IATester()
    ia_result = ia_tester.test_hotel(hotel_data)
    if ia_result:
        bing_proxy = BingProxyTester()
        share = bing_proxy.test_visibility(audit_result.url)
        
        kpis = AEOKPIs(
            hotel_name=hotel_data.get("name", ""),
            url=audit_result.url,
            ai_visibility_score=ia_result.score,
            share_of_voice=share,
            citation_rate=ia_result.citation_rate,
        )
        ia_score = kpis.calculate_composite_score()
        data_source = "IATester+BingProxy"
    
    # Si falla, intentar con lo que hay
    if ia_score is None or ia_score < 0:
        # Solo técnico
        score_final = score_tecnico
        confianza = "SIN DATOS IA"
    else:
        score_final = (score_tecnico * 0.70) + (ia_score * 0.30)
        confianza = "ALTA" if ia_score > 60 else "MEDIA"
    
    return {
        "score_tecnico": score_tecnico,
        "score_ia": ia_score,
        "score_final": score_final,
        "confianza": confianza,
        "data_source": data_source,
        "faltantes": _identificar_faltantes(elementos),  # NEEDS IMPLEMENTATION
    }
```

---

## 3. KB `calcular_cumplimiento()` — Debe Implementarse

### Problema
La KB define el algoritmo exacto (líneas 717-751) pero NO está implementado en el diagnóstico.

### Algoritmo KB (copiado de la KB)

```python
def calcular_cumplimiento(elementos: dict) -> int:
    """
    Pesos por elemento. Total máximo = 100.
    DE LA KB: [SECTION:SCORING_ALGORITHM]
    """
    pesos = {
        "ssl":               10,
        "schema_hotel":      15,
        "schema_reviews":    15,  # AggregateRating
        "LCP_ok":            10,  # LCP <= 2500ms
        "CLS_ok":             5,  # CLS <= 0.1
        "contenido_extenso": 10,
        "open_graph":         5,
        "schema_faq":         8,
        "nap_consistente":    7,
        "imagenes_alt":       5,
        "blog_activo":        5,
        "redes_activas":      5,
    }
    score = 0
    score += pesos["ssl"] if elementos.get("ssl") else 0
    score += pesos["schema_hotel"] if elementos.get("schema_hotel") else 0
    score += pesos["schema_reviews"] if elementos.get("schema_reviews") else 0
    lcp = elementos.get("LCP_ms")
    score += pesos["LCP_ok"] if lcp and lcp <= 2500 else 0
    cls = elementos.get("CLS")
    score += pesos["CLS_ok"] if cls is not None and cls <= 0.1 else 0
    score += pesos["contenido_extenso"] if elementos.get("contenido_extenso") else 0
    score += pesos["open_graph"] if elementos.get("open_graph") else 0
    score += pesos["schema_faq"] if elementos.get("schema_faq") else 0
    score += pesos["nap_consistente"] if elementos.get("nap_consistente") else 0
    score += pesos["imagenes_alt"] if elementos.get("imagenes_alt") else 0
    score += pesos["blog_activo"] if elementos.get("blog_activo") else 0
    score += pesos["redes_activas"] if elementos.get("redes_activas") else 0
    return min(score, 100)
```

### Reglas de paquete (KB líneas 753-756)

```python
def sugerir_paquete(score: int) -> str:
    """DE LA KB: [SECTION:SCORING_ALGORITHM]"""
    if score < 40:
        return "basico"
    elif score < 70:
        return "avanzado"
    return "premium"
```

---

## 4. PRIORITY_MATRIX — KB vs Implementación

### Problema
La KB tiene `PRIORITY_MATRIX` (líneas 506-525) pero no está implementada en PainSolutionMapper.

### Mapeo actual vs faltante

| Elemento KB | Impacto IA | Prioridad KB | Pain ID en Mapper | Asset |
|-------------|------------|--------------|-------------------|-------|
| Schema `aggregateRating` | Alto | 🔴 ALTA | `no_schema_rating` | `hotel_schema` |
| SSL/HTTPS | Medio | 🔴 ALTA | `no_ssl` | Guía SSL |
| Optimizar LCP | Alto | 🔴 ALTA | `low_lcp` | Guía LCP |
| Contenido >300 palabras | Alto | 🔴 ALTA | `low_content` | Estrategia |
| Schema `Hotel` básico | Alto | 🔴 ALTA | `no_hotel_schema` | `hotel_schema` |
| Open Graph | Medio | 🟡 MEDIA | `no_og_tags` | Asset meta |
| NAP consistente | Medio | 🟡 MEDIA | `nap_conflict` | Guía NAP |
| Schema `FAQPage` | Medio | 🟡 MEDIA | `no_faq_schema` | `faq_page` |
| Reviews visibles | Medio | 🟡 MEDIA | `low_reviews` | `review_plan` |

**ACCIÓN REQUERIDA**: Verificar que todos los Pain IDs de la KB existan en `pain_solution_mapper.py`. Agregar los que faltan.

---

## 5. Dependencias y orden de implementación

```
┌─────────────────────────────────────────────────────────────────┐
│                    FASE 0 (ESTE DOCUMENTO)                       │
│  Define: qué existe, qué falta, cómo conectar                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              GAP-IAO-01-01: Auditoría de conexiones              │
│  Objetivo: Mapear exactamente qué se usa vs qué se ignora       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              GAP-IAO-01-02: Diagnóstico con KB                   │
│  Objetivo: Implementar calcular_cumplimiento() + IATester       │
│  Archivos: v4_diagnostic_generator.py                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              GAP-IAO-01-03: Propuesta con monetización           │
│  Objetivo: Score real + faltantes → recomendaciones monetizadas │
│  Archivos: v4_proposal_generator.py                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              GAP-IAO-01-04: Assets con PainSolutionMapper        │
│  Objetivo: Conectar recommendations → conditional_generator     │
│  Archivos: conditional_generator.py                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              GAP-IAO-01-05: GA4 (post-mínimo viable)             │
│  Objetivo: Agregar tráfico indirecto si es necesario            │
│  Nota: GA4 puede omitirse si el pipeline básico funciona        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Eliminaciones vs plan anterior

| Concepto eliminado | Razón |
|-------------------|-------|
| `IAOCompositeScore` (nueva clase) | `AEOKPIs.calculate_composite_score()` ya existe y hace lo mismo |
| STAGE 4.5 (pipeline) | No es necesario crear un stage nuevo. Se modifica `_calculate_iao_score()` |
| 7 campos nuevos en V4AuditResult | No necesarios si se usa AEOKPIs como está |
| Pesos 70/30 hardcodeados | Ajustables por configuración, no parte del plan |
| GA4 como requerimiento | Útil pero no bloqueante para MVP |

---

## 7. Checklist de coherencia

Después de cada fase, verificar:

- [ ] KB `calcular_cumplimiento()` produce el mismo resultado que el diagnóstico actual (backwards compatible)
- [ ] Score IA usa `AEOKPIs.calculate_composite_score()`, no cálculo inventado
- [ ] `sugerir_paquete()` usa umbrales KB: <40 basico, <70 avanzado, ≥70 premium
- [ ] PainSolutionMapper tiene un Pain ID por cada elemento del CHECKLIST_IAO
- [ ] conditional_generator recibe recommendations del diagnóstico, no las inventa

---

*FIN DE FASE 0 — PREREQUISITO para GAP-IAO-01*
