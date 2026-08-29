# Greps residuales — FASE-SR-VERIFY (2026-08-28, L2/L16)

> Criterio: 0 residuos reales. Los matches que persisten son por diseño (glosario/comentarios/display de reporte) — justificados abajo.

| # | Patrón | Alcance | Matches | Veredicto |
|---|--------|---------|---------|-----------|
| 1 | `_normalize_url_for_matching` (nombre erróneo del contexto original; el helper real es `_normalize_url`) | `**/*.py` | **0** | ✅ 0 residuos |
| 2 | `sin costo \(fallback\)` | `modules/**/*.py` | 4 | ✅ Por diseño: `tech_jargon_glossary.py:38,52,86` = el glosario único contiene el término PROHIBIDO para detectarlo/traducirlo (fuente única SR-G, 14 tests de cobertura); `commercial_gate.py:817` = comentario del guardia. **Texto renderizado = 0** (ver fila 3) |
| 3 | `sin costo \(fallback\)` | `evidence/FASE-SR-H2/final/**/*.md` (texto publicado al cliente) | **0** | ✅ El texto publicado usa "disponibles sin compromiso (fuera del coverage)" y "incluido sin costo adicional" (mapeo del glosario) |
| 4 | `len\(report\.missing\)` (criterio duplicado de unresolved) | `modules/**/*.py` | 1 | ✅ Por diseño: `proposal_asset_alignment.py:376` es mensaje de DISPLAY del reporte formateado ("Missing: N"), NO un criterio de conteo. El criterio canónico único es `AlignmentResult.compute_unresolved` (alignment_result.py:174) |
| 5 | `TECH_JARGON_TERMS` (strings de jerga duplicados) | `**/*.py` | Solo glosario + import único en `commercial_gate.py:18` + tests de identidad (`assert gate_module.TECH_JARGON_TERMS is TECH_JARGON_TERMS`) | ✅ Fuente única sin duplicación (matches en `evidence/FASE-SR-G/` son copias de evidencia, no código) |
| 6 | `def _extract_text_tier` (extractor de tier duplicado) | `modules/**/*.py` | 1 (`v4_diagnostic_generator.py:797`) | ✅ Implementación única |
| 7 | `logger\.` | `main.py` | **0** | ✅ AC13 (guardián AST 3/3 PASSED) |

## Conclusión

**0 residuos reales.** Todos los patrones que debían desaparecer del código activo y del texto publicado desaparecieron; los matches restantes son la fuente única por diseño (glosario), comentarios explicativos o display de reporte — no criterios paralelos de conteo ni strings duplicados (L-NC10 respetada).
