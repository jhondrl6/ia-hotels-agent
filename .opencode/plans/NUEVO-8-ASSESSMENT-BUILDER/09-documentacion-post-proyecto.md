# Documentación Post-Proyecto — NUEVO-8 AssessmentBuilder

> **Plan:** NUEVO-8-ASSESSMENT-BUILDER
> **Inicio:** 2026-05-30
> **Versión target:** v4.50.0

---

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| AssessmentBuilder | `modules/assessment_builder.py` | Clase centralizada para construir el assessment dict con esquema tipado | N8-B |
| AssessmentPayload | `modules/assessment_builder.py` | Dataclass con todos los campos requeridos/opcionales del assessment dict | N8-A |

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| AssessmentBuilder fluid API | `modules/assessment_builder.py` | `.with_core().with_validation().with_financial()...build()` | N8-B |
| Validación pre-gates | `modules/assessment_builder.py` | `_validate()` asegura schema completo antes de pasar a gates | N8-B |
| Extractores simplificados | `publication_gates.py` | Acceso directo en vez de 4-6 fallbacks (ahorro ~100 líneas) | N8-C |
| site_presence_report injection | `main.py`, `assessment_builder.py` | Evita re-ejecución de SitePresenceChecker en el gate | N8-B |
| hotel_url or url simplificado | `publication_gates.py` | Fallback muerto eliminado — builder garantiza el campo | N8-C |

## Sección C: Bugs Corregidos

| Bug | Descripción | Fase |
|-----|-------------|------|
| critical_issues duplicado | `critical_issues_detected` era idéntico a `critical_issues` → cálculo tautológico de critical_recall | N8-C |
| quality_gate_* zombie | 3 campos con `locals().get()` — 0 consumidores | N8-C |
| coherence_checks/errors/warnings dead | 3 campos en assessment dict — 0 consumidores | N8-A |
| metrics dict dead | Dict con solo coherence_score duplicado — 0 consumidores | N8-A/N8-C |
| coherence_report dead weight | Campo en assessment dict — 0 consumidores post-simplificación extractores | N8-A/N8-C |
| site_presence_report ausente | SitePresenceChecker ejecutado 2 veces (main.py + gate) por falta de contrato | N8-B |
| proposal_services fantasma | Gate lo buscaba pero nunca se inyectaba → siempre usaba default | N8-A |
| hotel_url fantasma | Gate buscaba clave independiente que no existía → fallback or url | N8-A |
| hotel_url or url dead branch | Fallback `or assessment.get("url")` nunca se ejecuta post-builder | N8-C |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests nuevos | ~29 (12 + 17) | N8-A, N8-B |
| Líneas eliminadas (dead code) | ~130 (extractores + campos zombie + metrics + coherence_report + hotel_url fallback) | N8-C |
| Líneas agregadas | ~230 (AssessmentBuilder + dataclass + tests) | N8-A, N8-B |
| v4complete coherence | ≥ 0.80 esperado | N8-D |
| v4complete gates | 9+/11 esperado | N8-D |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `main.py` | L2663-2754 reemplazado por builder (~87 → ~15 líneas) | N8-B |
| `modules/assessment_builder.py` | Nuevo módulo | N8-A, N8-B |
| `modules/quality_gates/publication_gates.py` | Extractores simplificados (~129 → ~30 líneas) | N8-C |
| `tests/test_assessment_builder.py` | Tests unitarios + integración | N8-A, N8-B, N8-C |
| `CHANGELOG.md` | Entrada v4.50.0 | N8-RELEASE |
| `docs/GUIA_TECNICA.md` | Nota técnica AssessmentBuilder | N8-RELEASE |
| `VERSION.yaml` | Bump a 4.50.0 | N8-RELEASE |
