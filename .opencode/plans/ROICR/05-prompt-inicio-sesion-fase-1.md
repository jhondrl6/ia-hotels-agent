# FASE-1: Semántica de Activos — AssetSemanticsValidator + Migration Targets

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (código + tests)
> **Plan**: ROICR
> **Prerrequisito**: Ninguno

## Contexto previo

Esta es la primera fase del plan ROICR. El plan ROI-REFACTOR (completado) corrigió problemas de presentación. Ahora atacamos la capa estructural: el `PainSolutionMapper` produce "alucinaciones semánticas" — une brechas a activos que no las resuelven (ej: Monthly Report → FAQ missing). Además, deprecar assets sin `migration_target` rompe el mapper con `UnmappedPainError`.

## Objetivo de esta fase

Eliminar las alucinaciones semánticas del PainSolutionMapper y establecer la base de deprecación segura con `migration_target`.

### Tareas

- [ ] **1A**: Crear `modules/quality/asset_semantics_validator.py`
  - Implementar `INVALID_MAPPINGS` dict:
    ```python
    INVALID_MAPPINGS = {
        'monthly_report': ['faq_missing', 'schema_missing', 'llms_missing'],
        'whatsapp_conflict_guide': ['whatsapp_missing']
    }
    ```
  - Implementar `validar_semantica_comercial(pain_id, asset_id, asset_status) -> tuple[bool, str]`
  - Retorna `(False, "BLOCKED: ...")` si el mapping es ilógico
  - Retorna `(True, "AUDIT_ONLY")` si `asset_status == 'skipped_existing'`
  - Retorna `(True, "IMPLEMENT")` en caso normal

- [ ] **1B**: Actualizar `config/asset_registry.yaml`
  - Assets DEPRECATED deben tener `migration_target` explícito
  - `og_tags_guide` → `migration_target: open_graph_html`
  - `indirect_traffic_optimization` → `migration_target: null` (consultoría manual)
  - `local_content_page` → `confidence_score: 0.60`, presentar como "Bonus"

- [ ] **1C**: Integrar validator en `PainSolutionMapper`
  - Buscar dónde el mapper une pain_points con assets
  - Antes de asignar un asset a un pain, llamar `validar_semantica_comercial()`
  - Si retorna `BLOCKED`: buscar `migration_target` del asset deprecado
  - Si `migration_target` es null: marcar como `UNRESOLVED` con justificación
  - Si retorna `AUDIT_ONLY`: cambiar verbo de "Implementar" a "Auditar/Optimizar"

- [ ] **1D**: Implementar narrativas dinámicas en propuesta
  - En `v4_proposal_generator.py`: si el asset tiene narrativa `AUDIT_ONLY`, usar "Auditar y Optimizar" en vez de "Implementar"
  - Verificar con grep que no queden "Implementar" para assets skipped

- [ ] **1E**: Crear tests `tests/test_asset_semantics_validator.py`
  - Test mapping ilógico → BLOCKED
  - Test skipped_existing → AUDIT_ONLY
  - Test normal → IMPLEMENT
  - Test migration_target redirect
  - Test migration_target null → UNRESOLVED

### Restricciones

- NO cambiar la fórmula del pricing (eso es FASE-3)
- NO tocar publication_gates.py (eso es FASE-2)
- Preservar todos los fixes del plan ROI-REFACTOR
- Si `asset_registry.yaml` tiene formato diferente al del ROICR.md, adaptar al formato real

### Criterios de completitud

- [ ] `asset_semantics_validator.py` existe y es importable
- [ ] `grep migration_target config/asset_registry.yaml` retorna matches
- [ ] Mapper no produce uniones ilógicas (verificar con grep en propuesta output)
- [ ] `pytest tests/test_asset_semantics_validator.py -v` pasa
- [ ] Documentar resultado en `09-documentacion-post-proyecto.md` §FASE-1

### Próxima sesión

FASE-2: Gate Hardening — elevar `proposal_asset_alignment` a BLOCKING para dolores P1, usando el validator de esta fase.
