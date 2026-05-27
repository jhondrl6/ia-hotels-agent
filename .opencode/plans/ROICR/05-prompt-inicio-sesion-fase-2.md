# FASE-2: Gate Hardening — proposal_asset_alignment BLOCKING para P1

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (código + tests)
> **Plan**: ROICR
> **Prerrequisito**: FASE-1 completada (AssetSemanticsValidator existe)
> **Estado**: ✅ COMPLETADA — 2026-05-27

## Contexto previo

FASE-1 creó el `AssetSemanticsValidator` con `INVALID_MAPPINGS` y narrativas dinámicas (IMPLEMENT vs AUDIT_ONLY). Los assets DEPRECATED ahora tienen `migration_target` en `asset_registry.yaml`.

Sin embargo, el sistema técnico puede decir `NOT_READY` (ej: botón WhatsApp, Tier C) mientras `v4_proposal_generator.py` ignora esto y genera el PDF de todos modos porque el Coherence Score general ≥ 0.8. Esto permite promesas falsas al cliente.

## Objetivo de esta fase

Hacer que `proposal_asset_alignment` sea un gate **BLOCKING** cuando un asset asociado a un dolor P1 está en estado NOT_READY o BLOCKED.

### Tareas

- [ ] **2A**: Modificar `modules/quality/publication_gates.py`
  - Localizar la función `gate_proposal_asset_alignment()` (o equivalente)
  - Agregar lógica: si el asset resuelve un `pain_point` de prioridad P1 Y su status es NOT_READY o BLOCKED → retornar `GateResult(passed=False, gate_type='BLOCKING')`
  - Excepción: si el asset tiene status `skipped_existing` → pasar PERO forzar narrativa AUDIT_ONLY (usar validator de FASE-1)
  - **IMPORTANTE**: G8 (asset_confidence) sigue siendo ADVISORY, no bloqueante. Solo G1 (proposal_asset_alignment) cambia a BLOCKING para P1.

- [ ] **2B**: Integrar con AssetSemanticsValidator de FASE-1
  - Importar `validar_semantica_comercial` en el gate
  - Si retorna `AUDIT_ONLY`: gate pasa pero propuesta debe usar narrativa "Auditar"
  - Si retorna `BLOCKED`: gate falla

- [ ] **2C**: Crear tests `tests/test_proposal_asset_alignment.py`
  - Test: P1 pain con asset NOT_READY → BLOCKING
  - Test: P1 pain con asset IMPLEMENT → PASS
  - Test: P2 pain con asset NOT_READY → ADVISORY (no bloquea)
  - Test: skipped_existing con P1 → PASS + AUDIT_ONLY
  - Test: asset DEPRECATED con migration_target válido → redirigir

### Restricciones

- NO tocar el pipeline de pricing (FASE-3)
- NO cambiar G8 a blocking — sigue ADVISORY
- Preservar comportamiento existente para P2/P3
- El pattern de gate-blocking post-generación (delete documents si blocked) NO se aplica aquí — el gate debe correr ANTES de generar

### Criterios de completitud

- [ ] `publication_gates.py` tiene lógica BLOCKING para P1
- [ ] `grep "BLOCKING" modules/quality/publication_gates.py` muestra la nueva lógica
- [ ] `pytest tests/test_proposal_asset_alignment.py -v` pasa
- [ ] Documentar resultado en `09-documentacion-post-proyecto.md` §FASE-2

### Próxima sesión

FASE-3: Pipeline unificado de pricing (3 pasos) + CAPEX/OPEX desacoplado + curva de maduración 4 pilares.
