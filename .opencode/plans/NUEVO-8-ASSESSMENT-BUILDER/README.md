# NUEVO-8: AssessmentBuilder — Plan de Refactorización

> **Origen:** `.opencode/context/NUEVO-8-ASSESSMENT-DICT-CONTEXT.md`
> **Severidad:** 🟡 Media — riesgo de regresión acumulativo
> **Objetivo:** Centralizar la construcción del assessment dict en una clase tipada con esquema validable, simplificar extractores multi-path, eliminar campos muertos/zombie.
> **v4complete E2E:** Hotel Castilla Real (`https://www.hotelcastillareal.com/`)
> **Versión target:** v4.50.0

---

## Problema

El diccionario `assessment` que alimenta los 11 publication gates se construye manualmente en `main.py:2663-2754` (~87 líneas) sin estructura tipada, en 3 etapas separadas, con campos duplicados, hardcodeados, zombie, y sin validación. Los gates implementan ~129 líneas de extractores multi-path (4-6 fallbacks por campo) como defensa contra la ausencia de schema.

## Solución

`AssessmentBuilder`: clase centralizada con dataclass `AssessmentPayload` tipado, construcción declarativa fluida, validación pre-gates, y simplificación de extractores a acceso directo.

## Plan-vs-Reality (discrepancias corregidas)

| Claim del contexto | Verificación | Corrección |
|---|---|---|
| `audit_schema` zombie (0 consumidores vía dict) | ❌ SÍ consumido en L868 | Se mantiene en el schema |
| `consistency_report` dead key (0 consumidores) | ❌ SÍ consumido en L1236-1238 por extractor | Se mantiene como campo opcional |
| ROADMAP.md L369 referencia NUEVO-8 | ❌ No existe | Referencia eliminada del contexto |
| `coherence_checks/errors/warnings` no consumidos | ✅ 0 consumidores | Se eliminan del schema |
| `quality_gate_*` ×3 zombie | ✅ 0 consumidores | Se eliminan |
| `critical_issues_detected` duplicado tautológico | ✅ Mismo array | Se elimina |
| `evidence_coverage: 0.95` hardcodeado | ✅ | Se mantiene con TODO |
| `site_presence_report` no inyectado en assessment | ✅ Se calcula pero no llega | Se agrega al schema |
| `proposal_services` fantasma | ✅ Nunca inyectado, gate usa default | Se agrega al schema |
| `hotel_url` fantasma | ✅ No existe como clave independiente | Se agrega como alias |
| Total extractor lines: 129 (context decía 135) | ⚠️ 129 líneas reales | Ajustado |
| `metrics` solo tiene `coherence_score` | ✅ Extractores buscan 3 claves | **Eliminado** — 0 consumidores, el dict entero es dead code |
| `coherence_report` en dict | ✅ Consumido por extractor L1236 | **Eliminado** — 0 consumidores post-simplificación |
| `hotel_url or url` fallback | ✅ Gate L836 usa doble get | **Simplificado** — builder garantiza el campo |

---

## Decisiones Arquitectónicas

| # | Decisión | Respuesta |
|---|---------|-----------|
| 1 | ¿Dataclass o Pydantic? | **Dataclass** — sin dependencia externa, suficiente para validación en tiempo de construcción |
| 2 | ¿Ubicación del nuevo módulo? | **`modules/assessment_builder.py`** — junto a los módulos que lo consumen |
| 3 | ¿Migración progresiva o big-bang? | **Big-bang controlado** — el builder reemplaza las ~87 líneas en una sola fase; los extractores se simplifican en otra |
| 4 | ¿Eliminar `consistency_report` del dict? | **Mantener** — es consumido por `_extract_coherence_score` (L1236-1238) |
| 5 | ¿Eliminar `audit_schema` del dict? | **Mantener** — es consumido por `_proposal_asset_alignment_gate` (L868) |
| 6 | ¿Eliminar `coherence_checks/errors/warnings`? | **Eliminar** — 0 consumidores en gates. Coherence score viene de `coherence_report` |
| 7 | ¿Eliminar `quality_gate_issues/blockers/warnings`? | **Eliminar** — 0 consumidores, patrón `locals().get()` frágil |
| 8 | ¿`evidence_coverage: 0.95` hardcodeado? | **Dejar con TODO** — requiere métrica real de otro hallazgo, fuera de scope |
| 9 | ¿Builder pattern: fluid vs constructor? | **Fluid** (`.with_X()`) — legible, cada método encapsula una etapa, compatible con el código existente |
| 10 | ¿Activación: default o feature flag? | **Directa** — reemplaza el código actual, no es feature opcional |

---

## Fases

| Fase | Descripción | Tareas | v4complete | Tipo |
|------|-------------|--------|------------|------|
| N8-A | Auditoría final + Diseño AssessmentPayload + Tests dataclass | 4 | No | DIRECTA |
| N8-B | AssessmentBuilder + Migración main.py + Tests | 4 | No | DIRECTA |
| N8-C | Simplificar extractores + Eliminar campos muertos + Tests | 4 | No | DIRECTA |
| N8-D | E2E v4complete Hotel Castilla Real + Verificación | 3 + 1LC | **Sí** | SUBAGENTE |
| N8-RELEASE | CHANGELOG + GUIA_TECNICA + sync + validación | 4 | No | DIRECTA |

**Total: 5 fases (4 implementación + 1 RELEASE)**

---

## Arquitectura Target

```
main.py                                  publication_gates.py
┌──────────────────────┐                ┌────────────────────────────┐
│ builder = Assessment │                │ def _proposal_asset_gate(  │
│   Builder()          │                │   assessment):             │
│   .with_core(url, n) │  assessment    │   # Acceso directo — NO    │
│   .with_validation() │  dict          │   # extractores multi-path │
│   .with_financial()  │──────────────▶ │   score = assessment[      │
│   .with_coherence()  │                │     "evidence_coverage"]   │
│   .with_pain_ledger()│                │   ...                      │
│   .with_audit()      │                └────────────────────────────┘
│   .with_documents()  │
│   .with_assets()     │
│   .with_site_presence│
│   .build()  ← valida │
└──────────────────────┘
```

---

## Riesgos

- **Regresión silenciosa en gates:** si un campo cambia de nombre, el gate puede fallar. Mitigación: tests de integración + v4complete E2E.
- **SitePresenceChecker duplicado:** actualmente se ejecuta 2 veces. El builder lo ejecuta 1 vez e inyecta el resultado. Si el builder no se llama, el gate tiene el fallback de re-ejecución.
- **Compatibilidad hacia atrás:** el builder produce un `Dict[str, Any]` idéntico al que esperan los gates actuales. No se rompe el contrato.

---

## Referencias

- Contexto: `.opencode/context/NUEVO-8-ASSESSMENT-DICT-CONTEXT.md`
- Código: `main.py:2663-2754`, `modules/quality_gates/publication_gates.py:1138-1272`
- ROADMAP: sin referencia explícita (verificado 2026-05-30)
- Baseline v4complete: Hotel Castilla Real, coherence 0.83, 9/11 gates
