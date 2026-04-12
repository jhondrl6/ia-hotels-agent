# Dependencias entre Fases — Refactor 4 Pilares SEO/GEO/AEO/IAO

**Proyecto**: AEO-IAO-PROGRESSION-REFACTOR
**Fecha creación**: 2026-04-12
**Total fases**: 6 (FASE-A a FASE-F)

---

## Diagrama de Dependencias

```
FASE-A (Score Redistribution)     ← FUNDACIÓN, sin dependencias
  │
  ├──→ FASE-B (AEO Real + SerpAPI)
  │       │
  │       └──→ FASE-C (IAO Restoration + LLM Checker)
  │               │
  │               └──→ FASE-D (Package & Template Alignment)
  │                       │
  │                       └──→ FASE-E (Voice Readiness Proxy)
  │                               │
  │                               └──→ FASE-F (Documentation & Validation)
  │
  └──→ FASE-E puede iniciarse después de FASE-A (no requiere B/C/D)
```

## Orden de Ejecución Obligatorio

| Orden | Fase | Depende de | Razón |
|-------|------|-----------|-------|
| 1 | FASE-A | — | Base: redistribuye CHECKLIST_IAO a 4 pilares |
| 2 | FASE-B | FASE-A | Requiere estructura 4 pilares para inyectar SerpAPI |
| 3 | FASE-C | FASE-B | Requiere AEO score correcto antes de añadir IAO |
| 4 | FASE-D | FASE-C | Requiere 4 scores funcionales para alinear paquetes |
| 5 | FASE-E | FASE-A | Solo requiere estructura base (independiente de B/C/D) |
| 6 | FASE-F | TODAS | Cierra ciclo: documenta todo |

---

## Tabla de Conflictos de Archivos

Cada celda indica si la fase MODIFICA (M), LEE (L), o CREA (C) el archivo.

| Archivo | FASE-A | FASE-B | FASE-C | FASE-D | FASE-E | FASE-F |
|---------|--------|--------|--------|--------|--------|--------|
| `v4_diagnostic_generator.py` | **M** (L75-129, L504-570, L1401-1455, L1801-1860) | **M** (_calculate_aeo_score) | **M** (restaurar _calculate_iao_score) | L | L | L |
| `data_structures.py` | **M** (L280-308 DiagnosticSummary) | L | **M** (añadir iao fields) | L | L | L |
| `aeo_kpis.py` | **M** (reasignar campos) | L | **C** (IAO models) | L | L | L |
| `gap_analyzer.py` | L | L | L | **M** (gap_aeo → 4 gaps) | L | L |
| `report_builder.py` | — | — | — | **M** (DEPRECATED + 4-pilar, legado spark) | — | — |
| `pain_solution_mapper.py` | L | L | L | **M** (pain→package mapping) | L | L |
| `opportunity_scorer.py` | L | L | L | **M** (brechas 4 pilares) | L | L |
| `benchmarks.py` | L | L | L | **M** (3→4 benchmarks) | L | L |
| `package_recommender.py` | L | L | L | **M** (inputs 4 pilares) | L | L |
| `update_benchmarks.py` | L | L | L | **M** (3→4 scores) | L | L |
| `diagnostico_v6_template.md` | L | L | L | **M** (añadir IAO row) | L | L |
| `propuesta_v6_template.md` | L | L | L | L (ya correcto) | L | L |
| `llm_mention_checker.py` | — | — | **C** (nuevo) | L | L | L |
| `aeo_snippet_tracker.py` | — | **C** (nuevo) | L | L | L | L |
| `voice_readiness_proxy.py` | — | — | — | — | **C** (nuevo) | L |
| `test_aeo_score.py` | **M** | **M** | L | L | L | L |
| `test_aeo_kpis.py` | **M** | L | **M** | L | L | L |
| `test_fase_b_aeo_voice.py` | **M** | **M** | L | L | **M** | L |
| `test_audit_alignment.py` | L | L | L | **M** | L | L |
| `test_iao_score.py` | — | — | **C** (nuevo) | L | L | L |
| `CHANGELOG.md` | L | L | L | L | L | **M** |
| `GUIA_TECNICA.md` | L | L | L | L | L | **M** |
| `REGISTRY.md` | L | L | L | L | L | **M** |

### Conflictos potenciales (archivos compartidos)

| Archivo | Fases que lo modifican | Riesgo | Mitigación |
|---------|----------------------|--------|------------|
| `v4_diagnostic_generator.py` | A, B, C | **ALTO**: 3 fases tocan el mismo archivo de 2239 líneas | Cada fase toca funciones distintas: A→calcular_cumplimiento, B→_calculate_aeo_score, C→_calculate_iao_score |
| `data_structures.py` | A, C | **MEDIO**: 2 fases tocan DiagnosticSummary | A→renombrar campos, C→añadir campos IAO nuevos |
| `aeo_kpis.py` | A, C | **MEDIO**: A reasigna, C crea modelos nuevos | A no elimina campos, solo reasigna significado |
| `test_aeo_score.py` | A, B | **BAJO**: A cambia estructura, B cambia lógica AEO | A prepara tests para 4 componentes, B añade SerpAPI |

---

## Justificación del Orden

1. **FASE-A primero**: Es la base. Sin redistribuir CHECKLIST_IAO a 4 pilares, ninguna otra fase tiene dónde inyectar sus scores.
2. **FASE-B antes que C**: AEO (posición cero) es prerequisito conceptual de IAO (recomendación IA). Necesitamos AEO correcto antes de medir IAO.
3. **FASE-C antes que D**: Los paquetes comerciales dependen de los 4 scores funcionando. No podemos alinear paquetes hasta que IAO exista.
4. **FASE-E es flexible**: Voice Readiness Proxy solo requiere la estructura de FASE-A. Puede ejecutarse en paralelo lógico con B/C/D.
5. **FASE-F siempre al final**: Documenta todo lo implementado.

---

## Estado de Fases

| Fase | Estado | Fecha Inicio | Fecha Fin | Notas |
|------|--------|-------------|-----------|-------|
| FASE-A | ✅ Completada | 2026-04-12 | 2026-04-12 | Score Redistribution: 4 pilares, 101 tests, 0 regresiones |
| FASE-B | ✅ Completada | 2026-04-08 | 2026-04-08 | AEO Scoring Rewrite (4 componentes × 25pts) |
| FASE-C | ✅ Completada | 2026-04-12 | 2026-04-12 | IAO Restoration + LLM Mention Checker: 42 tests, 0 regresiones |
| FASE-D | ⏳ Pendiente | — | — | Package & Template Alignment |
| FASE-E | ⏳ Pendiente | — | — | Voice Readiness Proxy |
| FASE-F | ✅ Completada | 2026-04-12 | 2026-04-12 | Documentation & Validation: CHANGELOG, GUIA_TECNICA, REGISTRY, version sync, E2E pass |
