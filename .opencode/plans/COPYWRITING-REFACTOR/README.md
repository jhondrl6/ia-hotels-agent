# COPYWRITING REFACTOR — Plan Maestro

> **Origen**: `.opencode/context/Copywriting.jsonl` (validado 2026-05-25)
> **Objetivo**: Refactorizar templates y generadores de documentos comerciales (01_DIAGNOSTICO, 02_PROPUESTA) para maximizar conversión en hoteles boutique/negocios locales colombianos.
> **Alcance**: Solo copywriting + presentación. Cero cambios en lógica de auditoría, scoring, o APIs externas.
> **Principio rector**: "No aumentar API spend para resolver copy; usar datos ya generados y reglas determinísticas."

---

## Resumen Ejecutivo

El diagnóstico y propuesta actuales son técnicamente correctos pero comercialmente débiles:
- Hablan a un auditor técnico, no a un dueño/gerente hotelero
- Muestran escenario optimista negativo (-$270K COP/mes) 
- Presentan ROI negativo como argumento de venta (0.3X)
- Dicen "IA Bloqueada" cuando el audit muestra 0 crawlers bloqueados
- Ignoran el dolor OTA (Booking/Expedia, comisiones, dependencia)
- El gancho WhatsApp no lidera la narrativa

**La solución**: Reordenar templates (vista gerencia primero, anexo técnico después), corregir lógica financiera (clamp de escenarios, consistencia de tiers), y agregar gates comerciales (no publicar propuesta con ROI negativo como argumento principal).

---

## Decisiones Arquitectónicas

| # | Decisión | Respuesta |
|---|---------|-----------|
| D1 | ¿Dónde va la vista gerencia? | Template V6 reordenado: dueño primero (líneas 1-80), anexo técnico después (líneas 81+) |
| D2 | ¿Nuevo template V7 o modificar V6? | **Modificar V6** — es evolución del mismo template, no un nuevo formato |
| D3 | ¿Dónde clamp de escenarios? | En `v4_diagnostic_generator._build_scenario_table_rows()` — validación + label condicional |
| D4 | ¿Nuevo módulo de gates comerciales? | **Sí** — `modules/quality_gates/commercial_gate.py` junto a los gates técnicos existentes (junto a `publication_gates.py`, `coherence_gate.py`, etc.) |
| D5 | ¿Cómo se corrige "IA Bloqueada"? | Condicional en fuente de datos (`_pain_to_brecha()` L2625): si `pain.id == 'ai_crawler_blocked'` Y `blocked_crawlers == []`, cambiar label a "IA sin guía" |
| D6 | ¿La propuesta sigue mostrando ROI/beneficio neto? | Sí, pero con gate: si `net_benefit_6m < 0`, no mostrar tabla como argumento de cierre; mostrar plan de onboarding/activación de bajo riesgo |
| D7 | ¿Se toca la lógica de pricing? | **No** — el pricing ($1.2M/mes boutique) es decisión de negocio. Solo se corrige la presentación. |
| D8 | ¿Cambios en financial_scenarios.json? | **No** — los valores son correctos. Solo se corrige cómo se muestran (rango, no número exacto cuando Tier < A). |
| D9 | ¿Se modifica la estructura del v4_complete_report.json? | **No** — es output del LLM en el pipeline. Se agrega post-procesamiento en el generator. |
| D10 | ¿Qué hacemos con el whatsapp_button deprecado? | Ya está documentado en `phased-project-executor` §G1 como pre-existing gap. No se toca en este plan. |

---

## Arquitectura del Cambio

```
modules/commercial_documents/
├── templates/
│   ├── diagnostico_v6_template.md   ← MODIFICADO: Vista Gerencia primero, anexo técnico
│   └── propuesta_v6_template.md     ← MODIFICADO: Finanzas honestas, OTA narrative
├── v4_diagnostic_generator.py       ← MODIFICADO: _build_scenario_table_rows, financial labels
├── v4_proposal_generator.py         ← MODIFICADO: ROI/beneficio neto gate, pricing honesty
├── service_catalog.py               ← SIN CAMBIOS (datos correctos)
├── pain_solution_mapper.py          ← SIN CAMBIOS (detección correcta)
└── coherence_validator.py           ← SIN CAMBIOS (validación correcta)

modules/quality_gates/
└── commercial_gate.py               ← NUEVO: Gates comerciales (bloqueantes + advisory)
```

---

## Fases del Plan

| Fase | Descripción | Tareas | Comando Largo | R3 |
|------|------------|--------|---------------|-----|
| **COPY-A** | Template Restructuring + Generator Fixes | 4 | 0 | ✅ |
| **COPY-B** | Commercial Gates + Content Validation Rules | 3 | 0 | ✅ |
| **COPY-C** | E2E v4complete Validation (Hotel Castilla Real) | 2 | 1 (v4complete) | ✅ |
| **COPY-RELEASE** | Documentación y cierre | 4 | 0 | ✅ |

### Dependencias

```
COPY-A ──► COPY-B ──► COPY-C ──► COPY-RELEASE
```

---

## Hallazgos Validados (Plan vs Reality)

| # | Claim del Copywriting.jsonl | Archivo | Verificación |
|---|---------------------------|---------|-------------|
| F01 | "Copywriting.jsonl no era JSONL válido" | context/Copywriting.jsonl | ⚠️ Ya corregido — ahora es JSONL válido (20 líneas parseables) |
| F02 | "Diagnóstico conserva demasiada jerga técnica" | diagnostico_v6_template.md | ✅ Confirmado — SEO/AEO/IAO/Schema upfront (líneas 52-66) |
| F03 | "WhatsApp es el gancho emocional más fuerte" | audit + output | ✅ Confirmado — conflicto detectado pero no lidera narrativa |
| F04 | "Disclaimers contradictorios (Tier B vs C)" | v4_diagnostic_generator.py:942-961 | ✅ Confirmado — financial_breakdown.evidence_tier puede divergir del tier del template frontmatter |
| F05 | "Escenario optimista negativo" | diagnostic_generator.py:888-901 | ✅ Confirmado — `_build_scenario_table_rows` no clamp negative values |
| F06 | "Propuesta muestra ROI 0.3X con beneficio neto negativo" | Output 02_PROPUESTA:115-131 | ✅ Confirmado — $-5.367.168 COP beneficio neto |
| F07 | "Promete 'no hay botón WhatsApp' pero datos no soportan" | Output 02_PROPUESTA:24-30 | ✅ Confirmado parcial — el texto es fuerte pero no totalmente falso |
| F08 | "No se habla de OTAs/comisiones" | Templates + output | ✅ Confirmado — 0 menciones de Booking/Expedia/comisiones |
| F09 | "IA Bloqueada' cuando blocked_crawlers=[]" | Output 01_DIAGNOSTICO:165-168 | ✅ Confirmado — label incorrecto, viene de LLM en v4_complete_report |
| F10 | "Documento no está listo para venta sin revisión humana" | gate_report | ✅ Confirmado — NOT_READY, G8 advisory, G1 missing whatsapp_button |
| F11 | "Quick wins son tareas técnicas, no acciones de dueño" | Output diag:216-220 | ✅ Confirmado — falta priorizar acciones verificables por el dueño |
| F12 | "Contexto regional necesita aterrizarse más" | Output diag:28-49 | ⚠️ Parcial — funciona pero falta presión competitiva concreta |

---

## Dead Code Audit (Post-Design)

Tras este refactor, verificar que no quede código muerto:
- Ningún campo nuevo se introduce — solo se reordenan templates
- Los placeholders del template que se mueven de posición NO deben eliminarse del generator (solo cambia su ubicación en el output)
- `_build_scenario_table_rows` modificado: el parámetro `monthly_loss_max` sin `monthly_loss_central` sigue siendo necesario como fallback

---

## Presupuesto de Iteraciones por Fase

| Fase | Trabajo específico | Gastos fijos | Total estimado |
|------|-------------------|--------------|----------------|
| COPY-A | ~25 iters (template + generator edits) | ~26 iters | ~51 iters |
| COPY-B | ~20 iters (nuevo módulo + integración) | ~26 iters | ~46 iters |
| COPY-C | ~10 iters (preparación + verificación) + 1 v4complete | ~20 iters | ~30 iters + v4complete |
| COPY-RELEASE | ~20 iters (docs cascade) | ~15 iters | ~35 iters |

---

## Evidencia E2E Esperada

Tras FASE-COPY-C, se espera para Hotel Castilla Real (https://www.hotelcastillareal.com/):
- Coherence score: ≥ 0.80
- Sin escenario optimista negativo
- Sin "IA Bloqueada" si blocked_crawlers está vacío
- Propuesta con narrativa OTA (Booking/Expedia) presente
- WhatsApp como gancho #1 en diagnóstico
- Disclosure honesto de tier de evidencia financiera
