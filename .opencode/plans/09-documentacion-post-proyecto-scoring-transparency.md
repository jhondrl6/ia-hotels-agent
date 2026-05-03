# 09-documentacion-post-proyecto-scoring-transparency.md

> **Proyecto:** Scoring Transparency — GEO/AEO Scoring Methodology
> **Versión target:** 4.39.0
> **Estado:** En preparación

---

## A. Módulos Nuevos

*(Llenar después de implementar)*

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| — | — | — |

---

## D. Métricas Acumulativas

*(Llenar después de implementar)*

| Métrica | Antes | Después |
|---------|-------|--------|
| Transparencia del scoring | Score opaco | Breakdown visible + "NO mide" |
| Consistencia matemática GEO | Score GBP sin relación con checklist | Score checklist auto-calculado en breakdown, nota de divergencia explicativa |

### Nota arquitectónica — Dual-score GEO

iah-cli calcula DOS scores GEO que pueden diferir:
1. **GBP raw** (`_calculate_geo_score`) → mostrado en tabla principal → algoritmo de Google
2. **Checklist** (`calcular_score_geo`) → mostrado en breakdown → 6 factores con pesos fijos

El plan SCORING-TRANSPARENCY garantiza que el breakdown SIEMPRE muestre el score checklist (consistencia matemática). La nota de divergencia en el template explica que ambos scores son complementarios, no redundantes.

---

## E. Archivos Afiliados Actualizados

*(Llenar después de implementar)*

### Documentos actualizados

| Documento | Cambio |
|-----------|--------|
| `docs/scoring_methodology.md` | **NUEVO** — metodología completa de scoring |
| `CHANGELOG.md` | Entrada [4.39.0] |
| `GUIA_TECNICA.md` | Nota técnica v4.39.0 |
| `AGENTS.md` | Version bump 4.39.0 |

### Tests

| Suite | Tests | Resultado |
|-------|-------|-----------|
| `tests/commercial_documents/` | N | Pasan sin regresiones |

---

## Flujo de Documentación (ejecutar al final)

```
1. log_phase_completion.py --fase FASE-SCORING-1 --desc "..." --check-manual-docs
2. log_phase_completion.py --fase FASE-SCORING-2 --desc "..." --check-manual-docs
3. log_phase_completion.py --fase FASE-SCORING-3 --desc "..." --check-manual-docs
4. sync_versions.py
5. Verificar CHANGELOG.md
6. Verificar GUIA_TECNICA.md
7. run_all_validations.py --quick
```
