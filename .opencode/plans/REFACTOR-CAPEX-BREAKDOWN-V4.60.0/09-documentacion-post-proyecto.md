# Documentación Post-Proyecto — REFACTOR-CAPEX-BREAKDOWN v4.60.0

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| (ninguno) | — | Solo modificaciones, no módulos nuevos | — |

---

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Test integridad pipes | `tests/test_capex_rename.py` | Verifica estructura markdown de tabla CAPEX renderizada | FASE-1 |
| CAPEX desglose como sección | `propuesta_v6_template.md` | Desglose en sección independiente (no anidado en celda) | FASE-1 |

---

## Sección C: Fixes Aplicados

| Fix ID | Descripción | Archivo | Fase |
|--------|-------------|---------|------|
| F1 | Tabla CAPEX corrupta por tabla markdown anidada en celda | `propuesta_v6_template.md` | FASE-1 |
| F6 | Coherence Checklist invisible (placeholder inexistente) | `v4_proposal_generator.py` | FASE-3 |
| F7 | 9 keys huérfanas eliminadas del template data dict | `v4_proposal_generator.py` | FASE-2 |
| F8 | Fallback de `_build_capex_breakdown_table()` sin header | `v4_proposal_generator.py` | FASE-2 |

---

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests nuevos | 1 (integridad pipes) | FASE-1 |
| Regresiones | 0 | FASE-1, FASE-2, FASE-3 |
| Keys huérfanas eliminadas | 9 | FASE-2 |
| Complejidad máxima | FASE-1 (template fix + test) | FASE-1 |
| v4complete coherence | (pendiente FASE-4) | FASE-4 |
| v4complete gates | (pendiente FASE-4) | FASE-4 |

---

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `modules/commercial_documents/templates/propuesta_v6_template.md` | CAPEX desglose a sección propia | FASE-1 |
| `tests/test_capex_rename.py` | Test de integridad de pipes | FASE-1 |
| `modules/commercial_documents/v4_proposal_generator.py` | Keys huérfanas + fallback + coherence | FASE-2, FASE-3 |
| `VERSION.yaml` | Bump a 4.60.0 | RELEASE |

---

## Sección F: Lecciones Aprendidas

| Lección | Origen | Acción Preventiva |
|---------|--------|-------------------|
| Markdown no soporta tablas anidadas | F1 (bug de tablas) | Nunca embeber `${var}` que contenga tabla markdown dentro de celda de otra tabla |
| Tests deben verificar estructura, no solo contenido | F1 (regresión silenciosa) | Agregar test de integridad de pipes para cada tabla crítica en templates |
| Código generador puede tener keys huérfanas tras refactors | F7 (9 keys muertas) | Auditar periódicamente template data dict vs placeholders de templates activos |
