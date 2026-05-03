# Checklist: Scoring Transparency — FASE-SCORING

## Resumen del Proyecto

**Problema:** El scoring GEO/AEO/SEO/IAO no es transparente sobre qué factores mide y cuáles excluye. Un hotel con 203 reviews y respuesta <24h puede bajar su score por fotos faltantes — el owner no sabe por qué.

**Solución:** Agregar breakdown visible, sección "Este score NO mide" y documento `scoring_methodology.md` linkado.

**Archivos a modificar:**
- `modules/commercial_documents/v4_diagnostic_generator.py`
- `modules/commercial_documents/templates/diagnostico_v6_template.md`
- `docs/scoring_methodology.md` (NUEVO)

---

## Estados

| Fase | Nombre | Estado | Iteraciones |
|------|--------|--------|-------------|
| FASE-SCORING-1 | Python functions: breakdown + excluded | ⏳ Pendiente | — |
| FASE-SCORING-2 | Template vars + scoring_methodology.md | ⏳ Pendiente | — |
| FASE-SCORING-3 | Verificación + v4complete + docs | ⏳ Pendiente | — |
| FASE-RELEASE-4.39.0 | Release 4.39.0 | ⏳ Pendiente | — |

---

## Dependencias

```
FASE-SCORING-1 (Python)
    └── FASE-SCORING-2 (Template + Docs)
            └── FASE-SCORING-3 (Verificación)
                    └── FASE-RELEASE-4.39.0
```

---

## Criterios de Éxito Globales

1. Output del diagnóstico muestra breakdown: "GEO XX/100 = Fotos(15%) + NAP(15%) + ..." (score auto-calculado del checklist, consistencia matemática garantizada)
2. Sección "Este score NO mide" visible debajo de la tabla de scores
3. Nueva sección "Metodología de Scoring" al final del documento, con nota de divergencia GEO (checklist vs GBP score)
4. Link a `scoring_methodology.md` en frontmatter del output
5. Pregunta del owner ("¿El score considera la calidad de respuestas a reseñas?") respondida implícitamente por el documento
6. **NUEVO (Finding #1)**: Consistencia matemática en el breakdown GEO — score = suma exacta de pesos de items True del CHECKLIST_GEO
