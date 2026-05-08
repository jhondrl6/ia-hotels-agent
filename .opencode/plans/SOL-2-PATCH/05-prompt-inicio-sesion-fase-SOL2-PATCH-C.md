---
description: Prompt de inicio de fase SOL2-PATCH-C — Investigacion skipped_assets + v4complete baseline
version: 1.0.0
---

# FASE-SOL2-PATCH-C: Investigacion skipped_assets + v4complete baseline

**ID**: SOL2-PATCH-C
**Objetivo**: Investigar por que `skipped_assets` nunca se popula y verificar comportamiento con v4complete real
**Dependencias**: SOL2-PATCH-A (recomendado, no bloqueante)
**Duracion estimada**: 45-60 minutos
**Skill**: `phased_project_executor.md` v2.10.0
**Modo Ejecucion**: DIRECTO + v4complete (1 comando largo permitido)

## Contexto

El contexto 07 identifico que `v4_asset_orchestrator.skipped_assets` (dataclass field L90) nunca se popula en el flujo normal. Esto significa que `site_verification_applied` (L145) siempre es `False`, haciendo el flag cosmetico.

**Pregunta clave**: Existe logica que llama a SitePresenceChecker ANTES de generar assets y popule `skipped_assets`? Si no, el campo es dead code.

Esta fase incluye:
1. Investigacion de codigo (tracing completo de skipped_assets)
2. Ejecucion de v4complete para hotel de prueba (Termales Santa Rosa de Cabal)
3. Verificacion de si site_verification_applied se activa en output
4. Decision documentada: fix, doc, o ninguno

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| SOL-2-REFACTOR (A-D + RELEASE) | ✅ Completada |
| SOL2-PATCH-A | ✅/⏳ (recomendado completar antes) |
| SOL2-PATCH-C | ⏳ En progreso |

### Base Tecnica Disponible
- `modules/asset_generation/v4_asset_orchestrator.py` — L90 (`skipped_assets`), L145 (`site_verification_applied`)
- `modules/asset_generation/site_presence_checker.py` — 601 lineas
- `modules/quality_gates/publication_gates.py` — L803 (import SitePresenceChecker), L816 (try/except)
- `modules/asset_generation/asset_catalog.py` — definicion de assets
- Evidencia previa: `evidence/SOL2-PATCH-C/` (si v4complete ya fue ejecutado en sesion de preparacion)

## Tareas

### T1: Investigar poblacion de skipped_assets
**Objetivo**: Trazar todo el flujo donde `skipped_assets` deberia poblarse.

**Archivos a investigar**:
- `modules/asset_generation/v4_asset_orchestrator.py`: buscar `skipped_assets`, `append`, `extend`, `skip`
- `modules/asset_generation/site_presence_checker.py`: buscar retorno que indique "ya existe"
- `modules/quality_gates/publication_gates.py`: buscar donde se usa `site_presence_report`
- `main.py` o `v4complete` flujo: buscar donde se instancia orchestrator y si se pasan skipped_assets

**Criterios de aceptacion**:
- [ ] Mapa completo de donde skipped_assets SE DEFINIO vs donde SE POBLA
- [ ] Veredicto: dead code, gap de integracion, o feature no implementada

### T2: Ejecutar v4complete baseline
**Objetivo**: Usar el output YA EXISTENTE de la preparacion para verificar comportamiento de site_verification_applied.

**Evidencia disponible** (ya copiada en preparacion):
- `evidence/SOL2-PATCH-C/01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md`
- `evidence/SOL2-PATCH-C/02_PROPUESTA_COMERCIAL_*.md`
- `evidence/SOL2-PATCH-C/v4_audit/*.json`

**Nota**: NO ejecutar v4complete nuevamente. El baseline ya fue generado durante la sesion de preparacion del plan.

**Criterios de aceptacion**:
- [ ] Confirmar que los archivos JSON de evidencia estan presentes
- [ ] Verificar que asset_generation_report.json tiene `site_verification_applied: false`

### T3: Verificar site_verification_applied en output
**Objetivo**: Inspeccionar archivos JSON de salida para confirmar si el flag se activa.

**Archivos a inspeccionar**:
- `output/v4_complete/{hotel_id}/v4_audit/coherence_validation.json`
- `output/v4_complete/{hotel_id}/v4_audit/gate_report_*.json`
- `output/v4_complete/{hotel_id}/v4_audit/generation_report.json`

**Probe sugerido**:
```bash
./venv/Scripts/python.exe -c "
import json, glob
for f in glob.glob('output/v4_complete/*/v4_audit/*.json'):
    d = json.load(open(f))
    if 'site_verification' in str(d).lower() or 'skipped' in str(d).lower():
        print(f, '->', [k for k in d.keys() if 'site' in k.lower() or 'skip' in k.lower()])
"
```

**Criterios de aceptacion**:
- [ ] Confirmacion documentada de si site_verification_applied aparece en output
- [ ] Si aparece: en que archivo y con que valor
- [ ] Si no aparece: documentar como "confirmado cosmetico"

### T4: Documentar hallazgos y decision
**Objetivo**: Actualizar o confirmar `evidence/SOL2-PATCH-C/analisis_ejecucion.md` con la investigacion T1.

**Contenido requerido**:
1. Mapa completo de donde skipped_assets SE DEFINIO vs donde SE POBLA (de T1)
2. Resultados del baseline YA EXISTENTE (asset_generation_report.json, gate_report.json)
3. Decision con justificacion:
   - **OPCION A**: Implementar poblacion de skipped_assets (si es gap de integracion)
   - **OPCION B**: Documentar como comportamiento conocido (si es intencional)
   - **OPCION C**: Deprecar campo (si es dead code)
4. Recomendacion y proximos pasos

**Criterios de aceptacion**:
- [ ] Archivo `evidence/SOL2-PATCH-C/analisis_ejecucion.md` existe y refleja los hallazgos de T1
- [ ] Decision justificada con evidencia

## Tests Obligatorios

Esta fase es principalmente investigacion — no requiere tests nuevos de pytest.

| Verificacion | Metodo | Criterio de Exito |
|--------------|--------|-------------------|
| v4complete completo | Inspeccion output | Diagnostico + propuesta + assets generados |
| Coherence score | `coherence_validation.json` | >= 0.80 |
| Evidence guardada | `ls evidence/SOL2-PATCH-C/` | Archivos copiados |

## Post-Ejecucion (OBLIGATORIO)

1. **Guardar evidencia inmediatamente**:
   ```bash
   mkdir -p evidence/SOL2-PATCH-C
   cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/SOL2-PATCH-C/
   cp output/v4_complete/02_PROPUESTA_*.md evidence/SOL2-PATCH-C/
   cp output/v4_complete/*/v4_audit/*.json evidence/SOL2-PATCH-C/
   ```

2. **Actualizar `dependencias-fases.md`**:
   - Marcar PATCH-C como ✅ Completada

3. **Actualizar `06-checklist-implementacion.md`**:
   - Marcar tareas de PATCH-C como completadas

4. **Actualizar `09-documentacion-post-proyecto.md`**:
   - Seccion D: metricas de v4complete (coherence score, assets generados)

## Criterios de Completitud (CHECKLIST)

- [x] T1: Investigacion de skipped_assets completada con veredicto
- [x] T2: Baseline v4complete verificado (evidencia ya existente)
- [x] T3: site_verification_applied verificado en output JSON existente
- [x] T4: Analisis actualizado en `evidence/SOL2-PATCH-C/analisis_ejecucion.md` con trazado completo 5-capas
- [x] `dependencias-fases.md` actualizado
- [x] `06-checklist-implementacion.md` actualizado

## Restricciones

- **NO modificar codigo** en esta fase (a menos que la decision T4 indique fix simple de 1-2 lineas)
- **NO ejecutar v4complete** — el baseline ya fue ejecutado durante la preparacion del plan
- **NO modificar ROADMAP.md**
- Maximo 60 iteraciones
- Si se agota antes de T4, guardar evidencia y marcar como ⏳ INCOMPLETA

## Prompt de Ejecucion

```
Actua como agente de investigacion.

OBJETIVO: Investigar skipped_assets y consolidar hallazgos usando evidencia existente.

CONTEXTO:
- v4_asset_orchestrator.skipped_assets existe como dataclass field pero nunca se popula
- site_verification_applied siempre es False
- Baseline v4complete YA EJECUTADO durante preparacion del plan
- Evidencia disponible: evidence/SOL2-PATCH-C/v4_audit/*.json
- Hotel de prueba: Termales Santa Rosa de Cabal

TAREAS:
1. Trazar todo el flujo de skipped_assets (definicion, poblacion, uso)
2. Verificar en evidence existente que site_verification_applied = false
3. Actualizar analisis con veredicto (fix/doc/deprecar)

CRITERIOS:
- Investigacion completa con veredicto documentado
- Analisis actualizado en evidence/SOL2-PATCH-C/analisis_ejecucion.md

RESTRICCIONES:
- NO ejecutar v4complete nuevamente
```
