# Dependencias de Fases — HOTFIX v4.25.0 (2026-04-06)

> **SUPERADO — 2026-04-06** — Todos los bugs fueron resueltos.
> Ver `.opencode/plans/dependencias-fases.md` (v3) para el plan unificado vigente.
> Este archivo se archivó porque su contenido fue implementado completamente.

## Origen

Ejecucion v4complete --url https://www.hotelvisperas.com/es revelo 3 bugs criticos y 2 desconexiones
que invalidan la calidad del output entregado al cliente. El flujo principal funciona pero
FASE 3.6 (Scrubber) y FASE 4.5+ (Gates, Delivery, Health) no se ejecutan por Path type mismatch.

## Diagrama de Dependencias

```
FASE-HOTFIX-1 (Path Fix + Region Fix + Scrubber Desbloqueo)
   │
   ▼
FASE-HOTFIX-2 (OpportunityScorer en template + COP COP raiz)
   │
   ▼
FASE-HOTFIX-3 (Re-ejecucion v4complete + Validacion 100% + LocalContent conexion)
```

## Tabla de Fases

| # | ID | Descripcion | Depende de | Prioridad | Archivos |
|---|-----|-------------|-----------|-----------|----------|
| 1 | FASE-HOTFIX-1 | Fix Path mismatch + Region "default" + Desbloquear Scrubber/Gates | Ninguna | CRITICA | main.py, v4_diagnostic_generator.py |
| 2 | FASE-HOTFIX-2 | OpportunityScorer no se refleja + COP COP raiz en templates | HOTFIX-1 | ALTA | v4_diagnostic_generator.py, templates/ |
| 3 | FASE-HOTFIX-3 | Re-ejecucion v4complete hotelvisperas + Validacion + LocalContent conexion | HOTFIX-2 | ALTA | main.py, pain_solution_mapper.py, asset_catalog.py |

## Conflictos Potenciales

| Archivo | Fases que lo tocan | Resolucion |
|---------|-------------------|------------|
| `main.py` | HOTFIX-1 (Path fix), HOTFIX-3 (LocalContent) | Secciones distintas, sin conflicto |
| `v4_diagnostic_generator.py` | HOTFIX-1 (region), HOTFIX-2 (scores, COP COP) | HOTFIX-2 va despues de HOTFIX-1 |
| `templates/` | HOTFIX-2 (COP COP en templates) | Solo HOTFIX-2 |

## Bugs a Resolver

### BUG-1 (CRITICO): Path type mismatch
- **Sintoma**: AttributeError: 'str' object has no attribute 'exists'
- **Lineas**: main.py 2120, 2141, 2266, 2272
- **Causa**: V4DiagnosticGenerator.generate() retorna str, no Path
- **Fix**: Wrappear con Path() en las 4 ubicaciones
- **Impacto**: Desbloquea FASE 3.6, 4.5, 4.6, 7, 10

### BUG-2 (CRITICO): Region "default" propagation
- **Sintoma**: Documentos dicen "en default", "region de default"
- **Causa**: _extract_region_from_audit() retorna None cuando GBP no tiene region explicita
- **Fix**: Fallback a ciudad del GBP/direccion del hotel
- **Impacto**: Documentos cliente profesional sin placeholders

### BUG-3 (CRITICO): Content Scrubber nunca se ejecuta (consecuencia de BUG-1)
- **Sintoma**: "COP COP" x6, "en default" x4 en diagnostico y propuesta
- **Causa**: BUG-1 causa crash en FASE 3.6, el try/except engulle el error
- **Fix**: Se resuelve con FIX-1 (Path fix). Ademas verificar que los templates no generen "COP COP"
- **Impacto**: Documentos limpios para entrega al cliente

### DESCONEXION-1: OpportunityScorer no se refleja en diagnostico
- **Sintoma**: Brechas muestran % estatico, no scores ponderados
- **Causa**: _inject_brecha_scores() no reemplaza los placeholders del template
- **Fix**: Verificar mapeo de variables y corregir inyeccion

### DESCONEXION-2: LocalContentGenerator no conectado al flujo
- **Sintoma**: asset_catalog tiene local_content_page pero V4AssetOrchestrator nunca lo genera
- **Causa**: PainSolutionMapper no mapea ningun pain a local_content_page
- **Fix**: Agregar deteccion de oportunidad de contenido local

## Validacion Final (FASE-HOTFIX-3)

Despues de todos los fixes, re-ejecutar:
```bash
venv/Scripts/python.exe main.py v4complete --url https://www.hotelvisperas.com/es
```

Verificar en output:
- 0 ocurrencias de "COP COP"
- 0 ocurrencias de "en default" / "de default"
- FASE 3.6 ejecuta sin errores
- FASE 4.5 Publication Gates pasa
- FASE 4.6 Consistency Checker ejecuta
- FASE 7 Delivery Packaging ejecuta
- FASE 10 Health Dashboard ejecuta
- Opportunity scores visibles en brechas del diagnostico
