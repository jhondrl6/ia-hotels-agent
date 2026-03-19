---
assessment_id: $assessment_id
generated_at: $generated_at
version: 2.0.0
document_type: DIAGNOSTICO_V2
publication_status: $publication_status
coherence_score: $coherence_score
evidence_coverage: $evidence_coverage
---

# 📊 DIAGNÓSTICO Y OPORTUNIDAD
## $hotel_name

**URL:** $hotel_url  
**ID de Análisis:** $assessment_id  
**Fecha:** $generated_at  
**Coherence Score:** $coherence_score%  
**Cobertura de Evidencia:** $evidence_coverage%

---

## ⚠️ DISCLAIMERS

$disclaimers

---

## 🔍 ANÁLISIS POR CATEGORÍA

### Metadatos del Sitio

$metadata_claims

### Schema.org

$schema_claims

### Performance Web

| Métrica | Valor | Severidad |
|---------|-------|-----------|
| Performance Score | $performance_score | $performance_severity |
| Schema Coverage | $schema_coverage% | - |

$performance_claims

### Google Business Profile

$gbp_claims

---

## 📋 RESUMEN EJECUTIVO

- **Total Claims:** $total_claims
- **Críticos:** $critical_count
- **Altos:** $high_count
- **Medios:** $medium_count
- **Bajos:** $low_count
- **Verificados:** $verified_count
- **Bloqueos de Publicación:** $blockers_count

---

*Documento generado desde CanonicalAssessment*  
*Cada claim incluye evidence_excerpt trazable*
