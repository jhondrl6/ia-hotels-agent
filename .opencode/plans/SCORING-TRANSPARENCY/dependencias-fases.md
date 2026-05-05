# dependencias-fases.md — SCORING-TRANSPARENCY

**Plan:** SCORING-TRANSPARENCY v1.0.0
**Creado:** 2026-05-05

---

## Diagrama de Dependencias

```
SCORING-A ──────────▶ SCORING-B ──────────▶ SCORING-C
(Fix filtrado)       (4 pilares)           (Docs cascade)

Dependencia lineal estricta:
  - SCORING-B requiere que SCORING-A esté completado
    (el fix del filtrado condiciona cómo se presentan los 4 pilares)
  - SCORING-C requiere SCORING-A y SCORING-B completados
    (la documentación refleja el estado final del código)

Sin bifurcaciones. Sin trabajo paralelo posible (dependencia secuencial).
```

---

## Tabla de Conflictos de Archivos

| Archivo | SCORING-A | SCORING-B | SCORING-C | ¿Conflicto? |
|---------|-----------|-----------|-----------|-------------|
| `v4_diagnostic_generator.py` | L276-285 | L697-700 | — | NO (líneas distintas) |
| `diagnostico_v6_template.md` | — | L60+ (nuevos) | — | NO |
| `CHANGELOG.md` | — | — | MOD | NO |
| `GUIA_TECNICA.md` | — | — | MOD | NO |
| `REGISTRY.md` | — | — | MOD (auto) | NO |

**Conclusión:** Cero conflictos de archivos entre fases. La dependencia es lógica (B necesita el fix de A funcionando), no técnica.

---

## Archivos Involucrados por Fase

### SCORING-A: Fix del filtrado

| Archivo | Tipo | Líneas | Cambio |
|---------|------|--------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | MOD | 276-285 | Reemplazar filtro `is True` por iteración completa con marcadores ✅/~~tachado~~ |

### SCORING-B: Extensión a 4 pilares

| Archivo | Tipo | Líneas | Cambio |
|---------|------|--------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | MOD | ~697-700 | Agregar 3 asignaciones: `seo_score_breakdown`, `aeo_score_breakdown`, `iao_score_breakdown` |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | MOD | ~60+ | Agregar 3 placeholders: `${seo_score_breakdown}`, `${aeo_score_breakdown}`, `${iao_score_breakdown}` |

### SCORING-C: Documentación cascade

| Archivo | Tipo | Cambio |
|---------|------|--------|
| `docs/CHANGELOG.md` | MOD | Entrada v4.40.1 |
| `docs/GUIA_TECNICA.md` | MOD | Nota técnica de scoring transparency |
| `docs/contributing/REGISTRY.md` | MOD | Automático via `log_phase_completion.py` |
| `VERSION.yaml` | MOD | bump v4.40.0 → v4.40.1 |

---

## Non-Goals por Fase

### SCORING-A
- NO modificar los checklists ni los pesos
- NO modificar `calcular_score_*()` ni `_extraer_elementos_*()`
- NO modificar `scoring_methodology.md`

### SCORING-B
- NO modificar `_build_scoring_breakdown()` (ya corregido en A)
- NO modificar los checklists
- NO agregar nuevos pilares (solo los 4 existentes)

### SCORING-C
- NO modificar código fuente
- NO modificar ROADMAP.md
- NO ejecutar `v4complete`

---

## Estados de Fases

| Fase | Estado | Fecha inicio | Fecha fin | Sesión ID | Iteraciones |
|------|--------|-------------|-----------|-----------|-------------|
| SCORING-A | ✅ Completada | 2026-05-05 | 2026-05-05 | 20260505_1527 | 24 |
| SCORING-B | ✅ Completada | 2026-05-05 | 2026-05-05 | 20260505_1545 | 35 |
| SCORING-C | ✅ Completada | 2026-05-05 | 2026-05-05 | 20260505_1549 | 42 |
