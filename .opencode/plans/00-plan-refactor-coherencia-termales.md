# Plan Maestro: Refactorización Coherencia Diagnóstico vs Propuesta — Termales

> **Proyecto**: iah-cli — Coherencia Diagnóstico/Propuesta post-FASE-RELEASE  
> **Versión objetivo**: 4.44.0  
> **Hotel de verificación**: Termales Santa Rosa de Cabal — http://www.termales.com.co/  
> **Fecha de plan**: 2026-05-09  
> **Contexto base**: `.opencode/context/AUDITORIA_DIAG_PROP_COHERENCIA_TERMALES_20260509.md`

---

## Resumen Ejecutivo

Este plan resuelve **8 hallazgos** de coherencia entre diagnóstico y propuesta comercial, descubiertos en la auditoría post-FASE-RELEASE para Termales. Los hallazgos van desde un **defecto arquitectónico crítico** (H6: coherence se valida ANTES de generar assets) hasta **errores financieros menores** (H3/H4).

**Reglas de ejecución** (phased_project_executor.md v2.10.0):
- **R1**: Una fase por sesión. Sin excepciones.
- **R3**: Máximo 4 tareas de investigación/fix + 0 comandos largos, O 3 tareas + 1 comando largo.
- **R9**: Código puro/tests → ejecución DIRECTA. Comandos externos (v4complete) → protocolo de presupuesto.

---

## Tabla de Fases

| Fase | ID | Hallazgos | Tipo | Modo | Tareas | Estado |
|------|----|-----------|------|------|--------|--------|
| 1 | FASE-1 | H6 (CRÍTICO) | Root Cause — Coherence post-generación | DIRECTO | 3 | ⬜ Pendiente |
| 2 | FASE-2 | H1, H5, H8 (ALTO) | Propuesta completa + Gate robusto | DIRECTO | 3 | ⬜ Pendiente |
| 3 | FASE-3 | H7 (ALTO) | Monthly report fail-safe | DIRECTO | 3 | ⬜ Pendiente |
| 4 | FASE-4 | H3, H4 (MEDIO) | Corrección financiera | DIRECTO | 2 | ⬜ Pendiente |
| 5 | FASE-5 | — | Verificación E2E — v4complete Termales | DIRECTO* | 2 | ⬜ Pendiente |
| 6 | FASE-RELEASE | — | Documentación oficial + version bump | DIRECTO | 4 | ⬜ Pendiente |

\* FASE-5 incluye 1 comando largo (v4complete, ~5-10 min). Presupuesto de iteraciones: ~26 fijos + ~10 trabajo + ~10 docs = dentro de límite 60.

---

## Dependencias entre Fases

```
FASE-1 (H6: Coherence post-gen)
    │
    ▼
FASE-2 (H1/H5/H8: Propuesta + Gate)
    │
    ▼
FASE-3 (H7: Monthly report fail-safe)
    │
    ▼
FASE-4 (H3/H4: Financiero)
    │
    ▼
FASE-5 (v4complete E2E Termales)
    │
    ▼
FASE-RELEASE (Docs + version bump)
```

**Regla**: FASE-RELEASE solo ejecuta cuando FASE-1 a FASE-5 están ✅ en `dependencias-fases.md`.

---

## Hallazgos vs Fases

| Hallazgo | Severidad | Fase | Descripción breve |
|----------|-----------|------|-------------------|
| H6 | CRÍTICO | FASE-1 | CoherenceValidator no se ejecuta post-generación |
| H1 | CRÍTICO | FASE-2 | Propuesta muestra solo 3/8 servicios |
| H2 | CRÍTICO | FASE-1 | Contradicción coherence vs gate (resuelto por H6) |
| H5 | MENOR | FASE-2 | Assets técnicos no aparecen en propuesta |
| H8 | ALTO | FASE-2 | Gate 9 no bloquea con alignment 50% |
| H7 | ALTO | FASE-3 | monthly_report falla silenciosamente |
| H3 | MENOR | FASE-4 | Error de redondeo en distribución de brechas |
| H4 | MENOR | FASE-4 | Confusión pain_ratio vs recovery_factor |

---

## Conflictos de Archivos por Fase

| Archivo | FASE-1 | FASE-2 | FASE-3 | FASE-4 |
|---------|--------|--------|--------|--------|
| `modules/asset_generation/v4_asset_orchestrator.py` | ✅ Modifica | — | — | — |
| `main.py` | ✅ Modifica | — | — | — |
| `modules/commercial_documents/v4_proposal_generator.py` | — | ✅ Modifica | ✅ Modifica | ✅ Modifica |
| `modules/asset_generation/proposal_asset_alignment.py` | — | ✅ Modifica | — | — |
| `modules/quality_gates/publication_gates.py` | — | ✅ Modifica | — | — |
| `modules/commercial_documents/service_catalog.py` | — | ✅ Modifica | — | — |
| `modules/asset_generation/conditional_generator.py` | — | — | ✅ Modifica | — |
| `modules/asset_generation/monthly_report_generator.py` | — | — | ✅ Modifica | — |
| `modules/commercial_documents/coherence_validator.py` | ✅ Modifica | — | — | — |

**Nota**: No hay conflictos de archivo entre fases (cada archivo se toca en una sola fase, excepto v4_proposal_generator.py que se toca en FASE-2, FASE-3 y FASE-4 secuencialmente).

---

## Diagrama de Flujo Corregido (Post-Implementación)

```
Orquestación actual (defectuosa):
  Audit → Pre-coherence (sin assets) → Generar assets → Gate 9 → Propuesta
              ↑
     coherence_validator.validate() con generated_assets=None ✗

Orquestación corregida:
  Audit → Pre-coherence (screening rápido, sin bloqueo)
            ↓
     2. Generar assets (con condicionales + SitePresenceChecker)
            ↓
     3. Coherence post-generación ← NUEVO (FASE-1, H6)
            ↓
     4. Gate 9 (con datos reales) ──→ Si alignment < 0.8: BLOCKED (FASE-2, H8)
            ↓
     5. Propuesta completa con 8 servicios + assets técnicos (FASE-2, H1/H5)
            ↓
     6. monthly_report con fail-safe + nota (FASE-3, H7)
            ↓
     7. Financiero normalizado (FASE-4, H3/H4)
            ↓
     8. Publicación / Revisión manual
```

---

## Entregables del Plan

1. ✅ Arquitectura del flujo corregido (diagrama ASCII arriba)
2. ✅ Cambios específicos por archivo con líneas aproximadas
3. 🔄 Tests para cada fix (en prompts de fase)
4. 🔄 Documentación de la cascada de cambios (en FASE-RELEASE)

---

## Reglas Especiales de este Plan

1. **NO tocar FASE-12A/B/C**: Ya implementado y validado (commits `eb748fe`, `c26b2d2`).
2. **NO ejecutar v4complete hasta FASE-5**: La ejecución E2E es única y al término.
3. **Cada fase incluye tests**: Mínimo 3 tests nuevos por fase de código.
4. **Evidencia proactiva**: En FASE-5, inmediatamente después de v4complete, copiar output a `evidence/FASE-5/`.
5. **Version bump**: FASE-RELEASE sube VERSION.yaml 4.43.0 → 4.44.0.
