# Dependencias: Scoring Transparency

## Diagrama de Dependencias

```
FASE-SCORING-1 (Python)
    │
    └── FASE-SCORING-2 (Template + Docs)
            │
            └── FASE-SCORING-3 (Verificación)
                    │
                    └── FASE-RELEASE-4.39.0
```

## Conflictos de Archivos

| Archivo | Modificado en | Conflicto potencial |
|---------|--------------|---------------------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | SCORING-1 | **Ninguno** (solo esta fase lo toca) |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | SCORING-2 | **Ninguno** (solo esta fase lo toca) |
| `docs/scoring_methodology.md` | SCORING-2 (crea) | **Ninguno** (no existía antes) |

## Tabla de Fases

| Fase | Sesiones | Archivos | Depende de | Bloquea |
|------|----------|----------|------------|---------|
| FASE-SCORING-1 | 1 | `v4_diagnostic_generator.py` | — | SCORING-2 |
| FASE-SCORING-2 | 1 | `diagnostico_v6_template.md`, `scoring_methodology.md` | SCORING-1 | SCORING-3 |
| FASE-SCORING-3 | 1 | (verificación) | SCORING-2 | RELEASE |
| FASE-RELEASE-4.39.0 | 1 | CHANGELOG, GUIA_TECNICA, etc. | SCORING-3 | — |

## Regla de Bloqueo

FASE-SCORING-N no inicia hasta que FASE-SCORING-(N-1) muestre ✅ en todos los criterios de completitud del checklist.
