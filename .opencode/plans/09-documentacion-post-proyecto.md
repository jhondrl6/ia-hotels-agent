# Documentación Post-Proyecto: FASE-CAUSAL Alignment Fix

> **Proyecto**: Corregir desalineamiento diagnóstico-propuesta  
> **Versión objetivo**: 4.34.0  
> **Estado**: En progreso

---

## Objetivo del Proyecto

Corregir la causa raíz por la cual la propuesta comercial no lista todos los servicios correspondientes a las brechas detectadas en el diagnóstico. Específicamente: FAQ y Open Graph.

---

## A. Módulos Nuevos (si aplica)

> Esta fase no crea módulos nuevos, solo modifica existentes.

| Módulo | Descripción | Estado |
|--------|-------------|--------|
| N/A | No hay módulos nuevos | - |

---

## B. Módulos Modificados

| Módulo | Cambio Realizado |
|--------|------------------|
| `modules/asset_generation/proposal_asset_alignment.py` | Agregadas 2 entradas a PROPOSAL_SERVICE_TO_ASSET: "Pagina de FAQ" → faq_page, "Meta Tags Sociales (Open Graph)" → open_graph. Comentado "5" → "7". |
| `modules/commercial_documents/pain_solution_mapper.py` | Agregadas 2 entradas a ASSET_NAMES: open_graph y og_tags_guide |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Agregadas 2 filas a tabla principal hardcodeada (líneas 44-50): Página de FAQ y Meta Tags Sociales (Open Graph) |
| `tests/asset_generation/test_proposal_alignment.py` | Actualizados hardcoded 5 → 7 en 8 tests (tests de conteo y de assets) |

---

## C. Tests Nuevos

| Test | Archivo | Cobertura |
|------|---------|-----------|
| Tests existentes de proposal_alignment | `tests/asset_generation/test_proposal_alignment.py` | Verificados con 7 servicios |

---

## D. Métricas Acumulativas

| Métrica | Antes | Después |
|---------|-------|---------|
| Servicios en PROPOSAL_SERVICE_TO_ASSET | 5 | 7 |
| Coherence Score | 0.84 | 0.84 (sin cambio) |
| Tests totales | ~2224 | ~2224 (sin cambio) |

---

## E. Archivos Afiliados Actualizados (checklist)

### Paso 4.5: Flujo Documental Obligatorio

| Verificación | Comando | Estado | Notas |
|-------------|---------|--------|-------|
| FASE-CAUSAL-DIAG registrada | `log_phase_completion.py --fase FASE-CAUSAL-DIAG` | ⏳ Pendiente | - |
| FASE-CAUSAL-FIX registrada | `log_phase_completion.py --fase FASE-CAUSAL-FIX` | ⏳ Pendiente | - |
| FASE-CAUSAL-TEST registrada | `log_phase_completion.py --fase FASE-CAUSAL-TEST` | ⏳ Pendiente | - |
| FASE-RELEASE-4.34.0 registrada | `log_phase_completion.py --fase FASE-RELEASE-4.34.0` | ⏳ Pendiente | - |
| Versiones sincronizadas | `sync_versions.py` | ⏳ Pendiente | - |
| CHANGELOG formato | Manual | ⏳ Pendiente | Sección ### requerida |
| GUIA_TECNICA nota | Manual | ⏳ Pendiente | Nota técnica por fase |
| Validaciones pasan | `run_all_validations.py --quick` | ⏳ Pendiente | - |
| Doctor sin errores | `doctor.py --status` | ⏳ Pendiente | - |

---

## F. Detalle de Fases Completadas

### FASE-CAUSAL-DIAG
- **Fecha**: 2026-04-23
- **Estado**: ✅ Completada
- **Entregable**: Causa raíz documentada (doble tabla, hardcoding)

### FASE-CAUSAL-FIX
- **Fecha**: 2026-04-23
- **Estado**: ✅ Completada
- **Entregable**: Código corregido (7 servicios en PROPOSAL_SERVICE_TO_ASSET, ASSET_NAMES, template)

### FASE-CAUSAL-TEST
- **Fecha**: [por definir]
- **Estado**: ⏳ Pendiente
- **Entregable**: Verificación E2E exitosa

### FASE-RELEASE-4.34.0
- **Fecha**: [por definir]
- **Estado**: ⏳ Pendiente
- **Entregable**: Release completo con docs

---

## Notas de Implementación

### Causa Raíz
- Plantilla `propuesta_v6_template.md` hardcodea 5 servicios
- `PROPOSAL_SERVICE_TO_ASSET` no incluye FAQ ni Open Graph
- Los mapeos existen en `pain_solution_mapper.py` pero no se usaban

### Solución Aplicada
- Agregar entradas faltantes a `PROPOSAL_SERVICE_TO_ASSET`
- Hacer dinámica la generación de servicios en la propuesta

---

## Checklist de Cierre

- [ ] Todas las fases completadas
- [ ] REGISTRY.md actualizado
- [ ] CHANGELOG.md con entrada [4.34.0]
- [ ] GUIA_TECNICA.md con nota técnica
- [ ] VERSION.yaml sincronizado
- [ ] Validaciones pasan 4/4
- [ ] Commit y tag creado
