# Plan: Propuesta Dinámica desde Pain Detection

> **Versión**: 1.0.2  
> **Fecha**: 2026-04-23  
> **Estado**: 🔄 En ejecución (FASE-RELEASE pendiente)  

---

## Resumen

Este plan resuelve la causa raíz arquitectónica identificada tras FASE-RELEASE-4.34.0: la propuesta comercial genera servicios desde un diccionario estático (`PROPOSAL_SERVICE_TO_ASSET`) en vez de iterar sobre los pains detectados dinámicamente por `pain_solution_mapper.detect_pains()`.

### Problema Inmediato (Síntoma)
v4.34.0 agregó FAQ y Open Graph al diccionario estático. Pero si un hotel tiene 12 pains detectados y el diccionario solo tiene 7 servicios, la propuesta seguirá desalineada.

### Análisis de Causa Raíz
3 capas desvincadas:

1. **Capa de detección** (`pain_solution_mapper.detect_pains()`): Detecta ~20 pains dinámicamente.
2. **Capa de promesa** (`PROPOSAL_SERVICE_TO_ASSET`): Diccionario estático de 7 servicios. No reacciona a los pains detectados.
3. **Capa de presentación** (`propuesta_v6_template.md`): Tabla principal hardcodeada (fija) + tabla secundaria (`${asset_quality_table}`) generada iterando sobre el diccionario estático.

**Consecuencia**: La propuesta siempre muestra los mismos 7 servicios, independientemente de qué pains se detectaron.

### Solución Elegida: Opción C — Desacoplar Template de Diccionario

1. Crear `SERVICE_CATALOG` — catálogo independiente de servicios vendibles con metadatos (descripción, categoría, asset relacionado, pain relacionado).
2. Refactorizar `v4_proposal_generator` para consultar `pain_solution_mapper.detect_pains()` y luego mapear cada pain a servicios del catálogo.
3. La tabla de servicios se genera dinámicamente: solo los servicios cuyos pains fueron detectados.
4. Mantener `PROPOSAL_SERVICE_TO_ASSET` como backwards-compatible para el gate de alineación (verificación post-generación).

### Alcance de este plan
- **Este plan resuelve**: Que la propuesta refleje exactamente los servicios basados en los pains detectados.
- **Este plan NO resuelve**: El modelo de monetización (qué servicios son "core" vs "add-on").

---

## Fases del Plan

| # | Fase | Objetivo | Estado | Dependencias |
|---|------|----------|--------|--------------|
| 1 | FASE-CAUSAL-DIAG | Diagnosticar mapeo pain→servicio y arquitectura actual | ⏳ Pendiente | Ninguna |
| 2 | FASE-CAUSAL-REFACTOR | Refactorizar generador para usar pain detection como fuente | ⏳ Pendiente | DIAG |
| 3 | FASE-CAUSAL-VALIDATE | Verificar refactor mediante tests unitarios, inspección de código y test dinámico nuevo | ✅ Completada | REFACTOR |
| 4 | FASE-RELEASE-X.Y.Z | Documentación y release | ⏳ Pendiente | VALIDATE |

---

## Estructura de Archivos

```
.opencode/plans/PROPOSAL-DYNAMICA/
├── README.md                          ← Este archivo
├── context/
│   └── CAUSA-RAIZ-ARQUITECTONICA.md  ← Contexto completo del problema
├── dependencias-fases.md              ← Dependencias y conflictos
├── 06-checklist-implementacion.md    ← Checklist maestro
├── 09-documentacion-post-proyecto.md  ← Plantilla de documentación
├── 05-prompt-inicio-sesion-fase-causal-diag.md
├── 05-prompt-inicio-sesion-fase-causal-refactor.md
├── 05-prompt-inicio-sesion-fase-causal-validate.md
└── 05-prompt-inicio-sesion-fase-release-X.Y.Z.md
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
3. CHANGELOG.md con entrada [X.Y.Z]
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
- Contexto previo: `.opencode/plans/PROPOSAL-DYNAMICA/context/CAUSA-RAIZ-ARQUITECTONICA.md`

---

## Changelog del Plan

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0.0 | 2026-04-23 | Creación del plan |
| 1.0.1 | 2026-04-23 | Revisión pre-ejecución: corregido título VALIDATE (no es E2E), agregado test_proposal_dynamic.py, corregida contradicción en Opcion C (PROPOSAL_SERVICE_TO_ASSET se mantiene), corregidas descripciones de dependencias |
| 1.0.2 | 2026-04-23 | FASE-CAUSAL-VALIDATE completada: 14/14 tests PASS en test_proposal_dynamic.py, 13/13 alignment PASS, 4/4 validations PASS. Documentación actualizada. |
