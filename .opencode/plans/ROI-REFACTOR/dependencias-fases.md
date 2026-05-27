# Dependencias entre Fases — ROI-REFACTOR

```
┌─────────────────────────────────────────────────────────────┐
│                     ROI-REFACTOR                             │
│                  Dependency Diagram                          │
└─────────────────────────────────────────────────────────────┘

FASE-0 (Decisión Comercial)
  │  Evaluar opciones comerciales A/B/C/D + B+C + opción E
  │  Decisión operativa: Opción E (piloto $250K + crédito a retainer + success fee capped)
  │  Sin dependencias — fase inicial
  │  Pre-requisito: todas las demás fases
  ▼
FASE-1 (Bloqueantes de output) [ex-FASE-A]
  │  Fix 1: document_audience switch en proposal + diagnostic generators
  │  Fix 2: {% if testimonials %} condicional en propuesta_v6_template.md
  │  Fix 3: Corregir nota semántica de pain_ratio
  │  Sin dependencias — fase inicial (post FASE-0)
  │
  ▼
FASE-2 (Jerga + Entregables) [ex-FASE-B]
  │  Fix 4: Traducir AEO, UTMs, P1/P2/P3
  │  Fix 5: Tabla entregables → "Momento de entrega"
  │  ⚠️ Puede ejecutarse en paralelo con FASE-1
  │     (archivos distintos: template entregables vs document_audience en generators)
  │
  ▼
FASE-3 (ADR scraper + Versión) [ex-FASE-C]
  │  Fix 6: Conectar ADR del web_scraper como fallback en scenario_calculator
  │  Fix 7: Dynamic version en v4_proposal_generator.py:725
  │  Depende de: FASE-1 y FASE-2 completadas
  │     (trabaja en generators ya modificados por 1 + 2)
  │
  ▼
FASE-4 (Pulido final) [ex-FASE-D]
  │  Fix 8: Simplificar Anexo Técnico APIs
  │  Fix 9: Documentar evidence_tier vs precision_tier
  │  Fix 10: Nota explicativa pain_ratio 20% vs 41%
  │  Depende de: FASE-3 (usa el ADR scraper conectado + versión dinámica)
  │
  ▼
FASE-5 (v4complete + Análisis) [ex-FASE-E]
     v4complete Hotel Castilla Real
     Análisis post-implementación por niveles
     Depende de: TODAS las fases anteriores (FASE-0 a FASE-4)
```

---

## Tabla de Conflictos

| Par de Fases | ¿Conflicto? | Razón |
|-------------|-------------|-------|
| 0 ↔ 1 | ✅ Ninguno | Fases distintas (decisión vs implementación) |
| 1 ↔ 2 | ⚠️ Bajo | Archivos distintos (generators vs template entregables) |
| 1 ↔ 3 | ❌ Secuencial | 3 modifica generators que 1 ya modificó |
| 2 ↔ 3 | ✅ Ninguno | Archivos completamente distintos |
| 3 ↔ 4 | ⚠️ Bajo | Distintas secciones del código/template |
| 4 ↔ 5 | ❌ Secuencial | 5 requiere todos los fixes aplicados |

---

## Orden de Ejecución Recomendado

```
Sesión 1  → FASE-0 (Decisión comercial — exploración + decisión Jhond)
Sesión 2  → FASE-1 (Código+Tmpl — bloqueantes de output)
Sesión 3  → FASE-2 (Código+Tmpl — jerga + entregables)
Sesión 4  → FASE-3 (Código — ADR scraper + versión)
Sesión 5  → FASE-4 (Código+Tmpl — pulido final)
Sesión 6  → FASE-5 (Ejecución — v4complete + análisis)
```

---

## Estado de Fases

| Fase | Estado | Fecha | Evidencia |
|------|--------|-------|-----------|
| FASE-0 | ✅ COMPLETADA | 2026-05-26 | 09-documentacion-post-proyecto.md §F |
| FASE-1 | ✅ COMPLETADA | 2026-05-26 | 4 files modified (proposal/diagnostic generators + template) |
| FASE-2 | ✅ COMPLETADA | 2026-05-26 | propuesta_v6_template.md + v4_proposal_generator.py |
| FASE-3 | ✅ COMPLETADA | 2026-05-26 | main.py (adr_source en financial_scenarios.json), v4_proposal_generator.py, v4_diagnostic_generator.py (PIPELINE_VERSION) |
| FASE-4 | ✅ COMPLETADA | 2026-05-26 | propuesta_v6_template.md (Anexo APIs → párrafo transparencia), v4_proposal_generator.py (stubs IAO removidos), main.py (tier_explanation en JSON), v4_diagnostic_generator.py (pain_ratio_note + tier_explanation en JSON), diagnostico_v6_template.md (${pain_ratio_note}) |
|| FASE-5 | ✅ COMPLETADA | 2026-05-26 | `evidence/ROI-REFACTOR/analisis_post_implementacion.md` |"