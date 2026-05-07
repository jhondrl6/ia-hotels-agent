---
description: FASE-SOL2-C v4complete E2E Verification para Termales Santa Rosa de Cabal
version: 1.0.0
skill: phased_project_executor
---

# FASE-SOL2-C: v4complete E2E Verification (Termales)

**ID**: FASE-SOL2-C  
**Objetivo**: Ejecutar v4complete para Termales Santa Rosa de Cabal y verificar que los fixes de FASE-SOL2-A y SOL2-B mejoran los reportes de validación.  
**Dependencias**: FASE-SOL2-A y FASE-SOL2-B completadas.  
**Duración estimada**: 2-3 horas (incluye 10-15 min de v4complete + análisis)  
**Skill**: phased_project_executor, iah-cli-v4complete-delivery-validation  

## Contexto

Esta fase ejecuta el análisis completo E2E para el hotel Termales Santa Rosa de Cabal (http://www.termales.com.co/) como baseline post-fix. Se compara contra los hallazgos documentados en `05_SOL-2_ASSET_ALIGNMENT_DISCREPANCY_20260507.md`.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-SOL2-A | ✅ Completada |
| FASE-SOL2-B | ✅ Completada |
| PROP-PATCH-C | ✅ Completada (baseline pre-fix) |

### Base Técnica Disponible
- Comando: `./venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co/`
- Output esperado en: `output/v4_complete/termales/`
- Hotel ID derivado: `termales`
- Baseline pre-fix documentado en contexto SOL-2

## Tareas

### Tarea 1: Ejecutar v4complete
**Objetivo**: Generar diagnóstico, propuesta, assets y reportes para Termales.

**Comando exacto**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli && ./venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co/
```

**Criterios de aceptación**:
- [ ] Comando ejecuta con exit 0
- [ ] Se generan archivos en `output/v4_complete/termales/`
- [ ] Diagnóstico generado: `01_DIAGNOSTICO_*.md`
- [ ] Propuesta generada: `02_PROPUESTA_*.md`
- [ ] Assets generados en `output/v4_complete/termales/ASSETS/`
- [ ] Coherence score ≥ 0.80

**Protocolo de Ejecución**:
- Usar `terminal(timeout=600)` o spawn subagente con `delegate_task(timeout=900, notify_on_complete=True)`
- Si se usa subagente: el parent agent solo verifica output
- Si se ejecuta directo: usar `notify_on_complete=True` para no bloquear

### Tarea 2: Preservar Evidencia (OBLIGATORIO - inmediatamente post-ejecución)
**Objetivo**: Guardar output crítico antes de cualquier análisis.

```bash
mkdir -p evidence/FASE-SOL2-C
mkdir -p evidence/FASE-SOL2-C/v4_audit
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/FASE-SOL2-C/
cp output/v4_complete/02_PROPUESTA_*.md evidence/FASE-SOL2-C/
cp output/v4_complete/termales/v4_audit/*.json evidence/FASE-SOL2-C/v4_audit/ 2>/dev/null || true
cp output/v4_complete/termales/coherence_validation.json evidence/FASE-SOL2-C/ 2>/dev/null || true
cp output/v4_complete/termales/gate_report_*.json evidence/FASE-SOL2-C/ 2>/dev/null || true
```

**Criterios de aceptación**:
- [ ] Evidencia copiada a `evidence/FASE-SOL2-C/`
- [ ] Al menos 5 archivos JSON/Markdown en evidencia
- [ ] Si el agente se agota después, la evidencia ya está a salvo

### Tarea 3: Análisis de Ejecución
**Objetivo**: Comparar resultados contra baseline pre-fix (documentado en SOL-2 context).

**Análisis obligatorio**:
- [ ] **Coherence Validation**: ¿score ≥ 0.80? ¿`is_coherent: true`?
- [ ] **Gate Report**: ¿Cuántos PASSED vs WARNING vs FAILED?
- [ ] **Proposal Asset Alignment**: ¿missing_count sigue siendo 3 o bajó?
- [ ] **Assets Generados**: ¿Lista de assets coincide con los 6 esperados? ¿Aparece llms_txt?
- [ ] **SitePresence**: Si FASE-SOL2-A creó SitePresenceChecker, ¿log muestra `presence_verified` real?
- [ ] **Servicios en Propuesta**: ¿Cuántos servicios lista la propuesta? (baseline era 4)

**Reporte de análisis**:
Crear `evidence/FASE-SOL2-C/analisis_ejecucion.md` con:
```markdown
# Análisis v4complete Termales - Post SOL-2 Fixes

## Baseline vs Actual
| Métrica | Pre-fix (2026-05-07) | Post-fix (esta ejecución) | Δ |
|---------|----------------------|---------------------------|-----|
| Coherence score | 0.89 | {actual} | |
| Gate PASSED | 6/8 | {actual} | |
| Gate WARNING | 2/8 | {actual} | |
| missing_count | 3 | {actual} | |
| Assets generados | 6 | {actual} | |
| Servicios propuesta | 4 | {actual} | |

## Hallazgos
...

## Recomendaciones
...
```

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Validación E2E | Manual: analisis_ejecucion.md | Comparativa documentada |
| Coherence Gate | coherence_validation.json | score ≥ 0.80, is_coherent=true |
| Publication Gate | gate_report_*.json | PASSED ≥ 6/8, no FAILED bloqueantes |

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-SOL2-C ✅, fecha {timestamp}
2. **`06-checklist-implementacion.md`**: Estado ✅, iteraciones usadas
3. **`09-documentacion-post-proyecto.md`**:
   - Sección D: métricas E2E post-fix
   - Sección E: evidencia FASE-SOL2-C vinculada
4. **Evidencia**: Asegurar que `evidence/FASE-SOL2-C/` tiene todos los archivos

## Criterios de Completitud (CHECKLIST)

- [ ] v4complete ejecutado con éxito (exit 0)
- [ ] Coherence score ≥ 0.80
- [ ] Gate report generado y analizado
- [ ] Evidencia copiada a evidence/FASE-SOL2-C/ ANTES de análisis
- [ ] Análisis comparativo creado en analisis_ejecucion.md
- [ ] dependencias-fases.md actualizado
- [ ] Máximo 60 iteraciones (v4complete = ~1 tool call con timeout largo)

## Restricciones

- **NO modificar código fuente** en esta fase (solo lectura y análisis)
- **NO ejecutar fixes** si se encuentran nuevos gaps: documentarlos y reportar
- **NO olvidar copiar evidencia** inmediatamente después de v4complete
- Si v4complete falla, guardar logs de error y reportar en analisis_ejecucion.md
- Si el presupuesto de iteraciones es < 30 al iniciar, usar subagente para v4complete

## Prompt de Ejecución

```
Actúa como QA engineer ejecutando validación E2E.

OBJETIVO: Ejecutar v4complete para Termales y comparar contra baseline.

CONTEXTO:
- Fixes de FASE-SOL2-A (SitePresence) y SOL2-B (Gate unification) ya aplicados
- Baseline pre-fix: coherence=0.89, 6/8 PASSED, missing_count=3, 6 assets
- URL: http://www.termales.com.co/

TAREAS:
1. Ejecutar v4complete (directo o subagente con notify_on_complete)
2. INMEDIATAMENTE copiar output a evidence/FASE-SOL2-C/
3. Analizar coherence_validation.json y gate_report.json
4. Comparar contra baseline y crear analisis_ejecucion.md

CRITERIOS:
- Coherence ≥ 0.80
- Exit 0
- Evidencia preservada

VALIDACIONES:
- Análisis documentado en analisis_ejecucion.md
- Checklist de completitud verificado
```
