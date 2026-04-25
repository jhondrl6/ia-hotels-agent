# FASE-A: Alineacion Test Drift + Catalogos de Servicios

**ID**: FASE-A
**Objetivo**: Eliminar el test drift activo en commercial_documents y alinear SERVICE_CATALOG con PROPOSAL_SERVICE_TO_ASSET para garantizar determinismo en _generate_asset_quality_table.
**Dependencias**: Ninguna (primera fase de intervencion)
**Duracion estimada**: 1.5 - 2 horas
**Skill**: test-driven-development, systematic-debugging

---

## Contexto

La intervencion parte de un estado donde 1 test falla en commercial_documents y hay dos catalogos de servicios desalineados. Esta fase NO consume APIs externas (solo codigo y tests locales), por lo que es segura para ejecutar sin costos.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-RELEASE-4.35.0 | Completada |
| FASE-CAUSAL-REFACTOR | Parcial (service_catalog.py creado pero desalineado) |

### Base Tecnica Disponible
- Archivos existentes: `modules/commercial_documents/v4_proposal_generator.py`, `modules/commercial_documents/service_catalog.py`, `modules/asset_generation/proposal_asset_alignment.py`, `tests/commercial_documents/test_proposal_confidence_disclosure.py`, `tests/commercial_documents/test_proposal_dynamic.py`
- Tests base: 118 passed, 1 failed en tests/commercial_documents/
- Modulos disponibles: V4ProposalGenerator, SERVICE_CATALOG, PROPOSAL_SERVICE_TO_ASSET

---

## Tareas

### Tarea 1: Fix test drift en test_proposal_confidence_disclosure.py
**Objetivo**: Actualizar el test para reflejar los 7 servicios actuales de PROPOSAL_SERVICE_TO_ASSET.

**Archivos afectados**:
- `tests/commercial_documents/test_proposal_confidence_disclosure.py`

**Criterios de aceptacion**:
- [ ] Eliminar "Visibilidad en ChatGPT" de expected_services (servicio eliminado historicamente)
- [ ] Agregar "Pagina de FAQ" y "Meta Tags Sociales (Open Graph)" a expected_services
- [ ] Ajustar comentario "6 services" -> "7 services"
- [ ] Verificar que los demas tests del archivo siguen pasando (mapping de assets, confidence levels)
- [ ] Ejecutar `pytest tests/commercial_documents/test_proposal_confidence_disclosure.py -v` -> 5/5 PASS

### Tarea 2: Alinear SERVICE_CATALOG con PROPOSAL_SERVICE_TO_ASSET
**Objetivo**: Garantizar que ambas fuentes de verdad tengan los mismos 7 servicios con nombres identicos.

**Archivos afectados**:
- `modules/commercial_documents/service_catalog.py`
- `modules/asset_generation/proposal_asset_alignment.py` (posible ajuste de tilde)

**Criterios de aceptacion**:
- [ ] SERVICE_CATALOG incluye "Informe Mensual" (monthly_report, pain_id="no_monthly_report" o similar) en lugar de "Barra de Reserva Movil"
- [ ] Nombres de servicio son IDENTICOS en ambos catalogos (resolver "Boton/Boton" de WhatsApp)
- [ ] SERVICE_TO_ASSET_LOOKUP generado dinamicamente desde SERVICE_CATALOG sigue siendo valido
- [ ] `pytest tests/commercial_documents/test_proposal_dynamic.py -v` -> 14/14 PASS (regresion cero)

### Tarea 3: Verificar determinismo de _generate_asset_quality_table
**Objetivo**: Confirmar que modo dinamico (con detected_pain_ids) y estatico (sin ellos) producen tablas coherentes.

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py`

**Criterios de aceptacion**:
- [ ] Cuando detected_pain_ids incluye TODOS los pains, la tabla dinamica tiene los mismos 7 servicios que la estatica
- [ ] Cuando detected_pain_ids es None, usa PROPOSAL_SERVICE_TO_ASSET (backward compat)
- [ ] Ningun servicio aparece duplicado ni faltante

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| TestAssetQualityTable | `tests/commercial_documents/test_proposal_confidence_disclosure.py` | 5/5 PASS |
| TestProposalDynamicFiltering | `tests/commercial_documents/test_proposal_dynamic.py` | 14/14 PASS |
| TestServiceCatalogConsistency | `tests/commercial_documents/test_proposal_dynamic.py` | 7 entries validas |

**Comando de validacion**:
```bash
venv/Scripts/python.exe -m pytest tests/commercial_documents/test_proposal_confidence_disclosure.py tests/commercial_documents/test_proposal_dynamic.py -v
venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE (antes de cerrar la sesion):

1. **`.opencode/plans/06-checklist-implementacion.md`**
   - Marcar FASE-A como Completada
   - Agregar fecha de finalizacion

2. **`09-documentacion-post-proyecto.md`**
   - Seccion A: Archivos modificados (service_catalog.py, proposal_asset_alignment.py, test_proposal_confidence_disclosure.py)
   - Seccion D: Metricas (tests commercial_documents: 119/119 PASS)

3. **REGISTRY.md via log_phase_completion.py**:
```bash
venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-A --desc "Fix test drift proposal_confidence_disclosure + alineacion SERVICE_CATALOG con PROPOSAL_SERVICE_TO_ASSET" --archivos-mod "modules/commercial_documents/service_catalog.py,modules/asset_generation/proposal_asset_alignment.py,tests/commercial_documents/test_proposal_confidence_disclosure.py" --tests "5" --check-manual-docs
```

**NO esperar a la siguiente sesion para documentar.**

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como COMPLETADA** ⚠️

- [ ] Tests nuevos pasan: Todos los tests de commercial_documents ejecutan exitosamente (0 fallos)
- [ ] Validaciones del proyecto: `scripts/run_all_validations.py --quick` pasa 4/4
- [ ] `06-checklist-implementacion.md` actualizado: Estado de FASE-A marcado
- [ ] Metricas consistentes: Conteo de tests coincide (119 passed commercial_documents)
- [ ] Documentacion afiliada: REGISTRY.md actualizado via log_phase_completion.py
- [ ] Post-ejecucion completada: Todos los puntos de la seccion anterior realizados

**NO marcar la fase como completada si algun criterio falla.**

---

## Restricciones

- NO modificar logica de V4ProposalGenerator mas alla de verificar determinismo
- NO agregar nuevos servicios al catalogo (solo alinear los existentes)
- NO ejecutar v4complete en esta fase (optimizacion de costos API)
- Windows/WSL: usar `venv/Scripts/python.exe` (NO .venv, NO system python3)
