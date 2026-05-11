# FASE-1: Coherence Post-Generación (H6 — CRÍTICO)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.  
> **Tipo de ejecución**: DIRECTA (código puro, sin comandos largos)  
> **Límite de iteraciones**: Máximo 60. Budget estimado: ~35 trabajo + ~15 docs = ~50.

## Contexto previo

Este es el inicio del plan de refactorización para resolver la desconexión entre diagnóstico y propuesta comercial en iah-cli. El contexto completo está en `.opencode/context/AUDITORIA_DIAG_PROP_COHERENCIA_TERMALES_20260509.md`.

**Hallazgo H6 (CRÍTICO)**: El `CoherenceValidator` se ejecuta ANTES de generar assets, con `generated_assets=None`. El score 0.89 es un falso positivo que no refleja la realidad post-generación.

## Objetivo de esta fase

Implementar re-validación de coherencia DESPUÉS de la generación de assets, usando los `generated_assets` reales. El score post-generación debe reemplazar al pre-generación en el reporte final.

### Tareas

- [ ] **T1: Implementar `_validate_post_generation()` en `v4_asset_orchestrator.py`**
  - Ubicación: después del bucle de generación de assets (actual L296-360)
  - Re-ejecutar `self.coherence_validator.validate()` pasando los assets generados reales
  - El resultado debe almacenarse en un nuevo campo del reporte del orquestador
  - Referencia: `modules/asset_generation/v4_asset_orchestrator.py`, método `generate_assets()`

- [ ] **T2: Actualizar `main.py` para consumir post_coherence_score**
  - Línea ~2526: `DiagnosticSummary.coherence_score` debe usar el score post-generación cuando exista
  - Línea ~2228: el pre-coherence sigue existiendo como screening rápido, pero NO es el score final
  - Asegurar que `v4_complete_report.json` guarde AMBOS scores: `coherence_score_pre` y `coherence_score_post`

- [ ] **T3: Tests — verificar detección de missing assets post-generación**
  - Crear test que simule generación parcial (solo 3 de 8 assets) y verifique que `coherence_score_post` refleja los missing
  - Crear test que verifique que `coherence_score_post < coherence_score_pre` cuando hay assets fallidos
  - Crear test de regresión: cuando todos los assets se generan, `coherence_score_post >= 0.8`
  - Ubicación sugerida: `tests/asset_generation/test_v4_asset_orchestrator.py` o archivo nuevo

- [ ] **T4: Validaciones locales**
  - Ejecutar: `./venv/Scripts/python.exe scripts/run_all_validations.py --quick`
  - Verificar 4/4 checks pasan
  - Si hay fallos, corregir antes de cerrar la sesión

### Restricciones

- **NO** modificar `CoherenceValidator.validate()` ni su lógica interna — solo cambiar CUÁNDO y CON QUÉ se llama
- **NO** eliminar el pre-coherence en `main.py` — convertirlo en screening, no bloqueante
- **NO** tocar `proposal_asset_alignment.py` ni `publication_gates.py` (van en FASE-2)
- **NO** ejecutar `v4complete` en esta fase

### Criterios de completitud

- [x] `_validate_post_generation()` existe y se ejecuta después del bucle de generación
- [x] `v4_complete_report.json` contiene tanto `coherence_score_pre` como `coherence_score_post`
- [x] Tests nuevos pasan (mínimo 3) ✅ 8/8
- [x] Tests existentes no tienen regresiones ✅ 70+ passed
- [x] `run_all_validations.py --quick` pasa 4/4 ✅ 5/5

### Cerrada
2026-05-09 22:00 — Implementación completa, todos los criterios marcados.

### Próxima sesión

FASE-2: Propuesta completa + Gate robusto (H1, H5, H8). Se modificarán `v4_proposal_generator.py`, `service_catalog.py` y `publication_gates.py`.
