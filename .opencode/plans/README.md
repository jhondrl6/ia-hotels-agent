# Plan: FASE-CAUSAL Alignment Fix

> **Versión**: 1.0.0  
> **Fecha**: 2026-04-22  
> **Estado**: ✅ Preparación Completa  

---

## Resumen

Este plan corrige el desalineamiento entre el diagnóstico de brechas y la propuesta comercial en iah-cli v4.33.0.

### Problema Inmediato (Síntoma)
La propuesta comercial lista 5 servicios fijos, pero el sistema detecta brechas reales (incluyendo FAQ y Open Graph) que nunca se ofrecen al cliente. El cliente paga para solucionar problemas que la propuesta ni siquiera menciona.

### Análisis de Causa Raíz Real
La causa raíz NO es solo "faltan 2 entradas en un diccionario". Es arquitectónica:

1. **Capa de detección** (`pain_solution_mapper`): Detecta ~20 pains dinámicamente (FAQ, OG, SSL, performance, etc.).
2. **Capa de promesa** (`PROPOSAL_SERVICE_TO_ASSET`): Diccionario ESTÁTICO de 5 servicios. No reacciona a los pains detectados.
3. **Capa de presentación** (`propuesta_v6_template.md`): Tiene DOS tablas:
   - Tabla principal (líneas 44-50): **hardcodeada en markdown** — 5 filas fijas de texto plano.
   - Tabla secundaria (`${asset_quality_table}`): generada dinámicamente desde `PROPOSAL_SERVICE_TO_ASSET`.

**Consecuencia**: Incluso si agregamos FAQ/OG al diccionario, la tabla principal del template seguirá mostrando solo 5 servicios porque es texto estático. Y si un hotel NO tiene brecha de OG, igual se le ofrecería porque el diccionario es estático.

### Alcance de este plan
- **Este plan resuelve**: Que FAQ y Open Graph aparezcan en la propuesta para hoteles que SÍ los necesitan (corrección sintomática).
- **Este plan NO resuelve**: Que la propuesta se genere dinámicamente desde los pains detectados (causa raíz sistémica). Eso requiere refactor del generador de propuestas para iterar sobre `pain_solution_mapper` en vez de `PROPOSAL_SERVICE_TO_ASSET`.

### Solución Inmediata (este plan)
1. Actualizar `PROPOSAL_SERVICE_TO_ASSET` para incluir FAQ y Open Graph
2. Actualizar `ASSET_NAMES` en `pain_solution_mapper` (falta `open_graph`)
3. Hacer dinámica la tabla principal del template (no solo `${asset_quality_table}`)
4. ~~Verificación E2E con Amaziliahotel~~ → **REUBICADA**: La prueba E2E con `https://amaziliahotel.com/` se ejecuta UNA SOLA VEZ en FASE-RELEASE-4.34.0 (post-implementación), no en FASE-CAUSAL-TEST, para minimizar costos API.

### Solución Sistémica (futura FASE)
- Refactorizar `v4_proposal_generator` para generar servicios desde `pain_solution_mapper.detect_pains()` en vez de `PROPOSAL_SERVICE_TO_ASSET`.
- Eliminar o deprecar `PROPOSAL_SERVICE_TO_ASSET` como fuente de verdad.

---

## Fases del Plan

| # | Fase | Objetivo | Estado | Dependencias |
|---|------|----------|--------|--------------|
| 1 | FASE-CAUSAL-DIAG | Diagnosticar causa raíz | ⏳ Pendiente | Ninguna |
| 2 | FASE-CAUSAL-FIX | Corregir mapeo y plantilla | ⏳ Pendiente | DIAG |
| 3 | FASE-CAUSAL-TEST | Verificación E2E | ⏳ Pendiente | FIX |
| 4 | FASE-RELEASE-4.34.0 | Documentación y release | ⏳ Pendiente | TEST |

---

## Estructura de Archivos

```
.opencode/plans/
├── README.md                          ← Este archivo
├── context/
│   └── context.md                     ← Contexto completo del problema
├── dependencias-fases.md              ← Dependencias y conflictos
├── 06-checklist-implementacion.md     ← Checklist maestro
├── 09-documentacion-post-proyecto.md  ← Plantilla de documentación
├── 05-prompt-inicio-sesion-fase-causal-diag.md
├── 05-prompt-inicio-sesion-fase-causal-fix.md
├── 05-prompt-inicio-sesion-fase-causal-test.md
└── 05-prompt-inicio-sesion-fase-release-4.34.0.md
```

---

## Quick Start

### Para ejecutar una fase:

1. Leer el prompt de la fase en `05-prompt-inicio-sesion-fase-{NOMBRE}.md`
2. Seguir las tareas y criterios de aceptación
3. Actualizar `dependencias-fases.md` y `06-checklist-implementacion.md`
4. Marcar fase como completada

### Comandos de validación (al final de cada fase):

```bash
# Tests específicos
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_proposal_alignment.py -v

# Validaciones completas
./venv/Scripts/python.exe scripts/run_all_validations.py --quick

# Doctor status
./venv/Scripts/python.exe scripts/doctor.py --status
```

---

## Documentación Post-Proyecto

Después de completar todas las fases, seguir el flujo §4.5 documentado en `09-documentacion-post-proyecto.md`.

**Resumen de pasos**:
1. `log_phase_completion.py` para cada fase
2. `sync_versions.py`
3. CHANGELOG.md con entrada [4.34.0]
4. GUIA_TECNICA.md con nota técnica
5. `run_all_validations.py --quick`
6. Commit y tag

---

## Referencias

- Workflow: `.agents/workflows/phased_project_executor.md` v2.4.0
- Template fase: `.agents/workflows/templates/prompt-fase-template.md` v1.3.0
- Skills relacionadas:
  - `iah-cli-plan-vs-reality-check`
  - `iah-cli-post-implementation-e2e-verification`
- Contributing: `docs/CONTRIBUTING.md`

---

## Changelog del Plan

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0.0 | 2026-04-22 | Creación del plan |
