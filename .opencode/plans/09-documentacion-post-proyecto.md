# Documentación Post-Proyecto — ADVISORY-WARNINGS

**Plan:** IA-Readiness Advisory Warnings
**Versión objetivo:** 4.47.0
**Creado:** 2026-05-16

> Este archivo es la fuente de datos acumulativa para FASE-RELEASE al generar CHANGELOG y GUIA_TECNICA.
> Cada fase de implementación agrega sus datos aquí al completar.

---

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| — | — | No se crean módulos nuevos en este proyecto | — |

---

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Alerta IA-Readiness Critical en diagnóstico | `v4_diagnostic_generator.py` | Blockquote advisory cuando IA-Readiness score < 50 en DIAGNOSTICO.md | FASE-A |
| Advisory warnings en delivery quality report | `delivery_quality_report.py` | Nuevo campo `advisory_warnings: List[dict]` con entry `IA_READINESS_CRITICAL` | FASE-A |
| Verificación e2e con caso real | — | v4complete para Hotel Castilla Real validando que los warnings aparecen correctamente | FASE-B |

---

## Sección C: Correcciones de Bugs

| Bug | Módulo | Descripción | Fase |
|-----|--------|-------------|------|
| — | — | No se corrigen bugs en este proyecto | — |

---

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests nuevos | 6 | FASE-A |
| Tests totales post-proyecto | ~2497 | FASE-A |
| Regresiones | 0 | FASE-A |
| Coherence score (Hotel Castilla Real) | — | FASE-B |
| IA-Readiness score (Hotel Castilla Real) | — | FASE-B |

---

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | Agregada lógica de alerta advisory en `_build_geo_problems_table()` | FASE-A |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Agregada variable `${ia_critical_warning}` (si aplica) | FASE-A |
| `modules/quality_gates/delivery_quality_report.py` | Nuevo campo `advisory_warnings: List[dict]` + `to_dict()` | FASE-A |
| `tests/commercial_documents/test_v4_diagnostic_generator.py` | Tests de alerta advisory (3 casos) | FASE-A |
| `tests/quality_gates/test_delivery_quality_report.py` | Tests de advisory_warnings (3 casos) | FASE-A |
| `CHANGELOG.md` | Entrada [4.47.0] | FASE-RELEASE |
| `GUIA_TECNICA.md` | Nota técnica v4.47.0 | FASE-RELEASE |
| `VERSION.yaml` | Bump a 4.47.0 | FASE-RELEASE |

---

## Sección F: Decisiones de Diseño

| Decisión | Justificación | Fase |
|----------|---------------|------|
| Advisory, no bloqueante | IA-Readiness mide riesgo comercial, no calidad estructural de datos | FASE-A |
| No usar `critical_issues` | `critical_issues` tiene consumidores downstream que asumen fallas estructurales | FASE-A |
| No afectar `overall_confidence` | `overall_confidence` mide confiabilidad de datos, no probabilidad de citación IA | FASE-A |
| WARNING visible + persistente | Combinación de diagnóstico (visible al hotelero) + delivery_quality_report (machine-readable) | FASE-A |

---

## Historial de Actualizaciones

| Fecha | Fase | Actualización |
|-------|------|---------------|
| 2026-05-16 | — | Estructura base creada |
