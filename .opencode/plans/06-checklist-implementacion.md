# Checklist de Implementacion - PATCH Forense AmaziliaHotel

## Progreso General

| Fase | Descripcion | Estado | Tests | Fecha |
|------|-------------|--------|-------|-------|
| FASE-A | hotel_schema dual (rico vs vacio) | Pendiente | - | - |
| FASE-B | Comision OTA label incorrecto | Pendiente | - | - |
| FASE-C | open_graph template + pain_id | Pendiente | - | - |
| FASE-D | gate_report presence check | Pendiente | - | - |
| FASE-RELEASE-4.36.0 | Cierre + documentacion | Pendiente | - | - |

## Dependencias

```
FASE-A ──┐
FASE-B ──┤
FASE-C ──┼──→ FASE-RELEASE-4.36.0
FASE-D ──┘
```

FASE-A, B, C, D son funcionalmente independientes.
Conflicto bajo A vs C en conditional_generator.py (ramas distintas).
FASE-RELEASE depende de TODAS completadas.

## Checklist por Fase

### FASE-A: hotel_schema dual
- [ ] Schema rico se prefiere sobre basico en conditional_generator
- [ ] Bridge siempre aplica en v4_asset_orchestrator
- [ ] Tests nuevos agregados (>= 3)
- [ ] Tests existentes sin regresion
- [ ] run_all_validations.py --quick pasa
- [ ] dependencias-fases.md actualizado
- [ ] Post-ejecucion completada

### FASE-B: Comision OTA label
- [ ] Labels corregidos en _build_financial_title_label()
- [ ] Valores correctos en _build_financial_placeholders()
- [ ] Template actualizado si aplica
- [ ] Tests nuevos agregados (>= 2)
- [ ] Tests existentes sin regresion
- [ ] run_all_validations.py --quick pasa
- [ ] dependencias-fases.md actualizado
- [ ] Post-ejecucion completada

### FASE-C: open_graph asset
- [ ] Template open_graph_template.html creado
- [ ] Pain_id no_og_tags cableado desde audit_report
- [ ] Generacion end-to-end funciona
- [ ] Tests nuevos agregados (>= 4)
- [ ] Tests existentes sin regresion
- [ ] run_all_validations.py --quick pasa
- [ ] dependencias-fases.md actualizado
- [ ] Post-ejecucion completada

### FASE-D: gate_report presence
- [ ] gate_report no marca "missing" assets existentes en sitio
- [ ] presence_verified por asset en output
- [ ] alignment_percentage recalculado
- [ ] 4 categorias de assets en reporte
- [ ] Tests nuevos agregados (>= 4)
- [ ] Tests existentes sin regresion
- [ ] run_all_validations.py --quick pasa
- [ ] dependencias-fases.md actualizado
- [ ] Post-ejecucion completada

### FASE-RELEASE-4.36.0: Cierre
- [ ] VERSION.yaml bumped a 4.36.0
- [ ] sync_versions.py ejecutado (6 archivos)
- [ ] version_consistency_checker.py pasa
- [ ] log_phase_completion.py para FASE-A
- [ ] log_phase_completion.py para FASE-B
- [ ] log_phase_completion.py para FASE-C
- [ ] log_phase_completion.py para FASE-D
- [ ] CHANGELOG.md entrada 4.36.0 (formato CONTRIBUTING)
- [ ] GUIA_TECNICA.md notas v4.36.0
- [ ] run_all_validations.py --quick 4/4
- [ ] doctor.py --status sin errores
- [ ] log_phase_completion.py para FASE-RELEASE
- [ ] Git commit

## Metricas Acumulativas

| Metrica | Valor Inicial | Post-A | Post-B | Post-C | Post-D | Post-RELEASE |
|---------|---------------|--------|--------|--------|--------|--------------|
| Tests totales | 2224 | | | | | |
| Regresiones | 0 | | | | | |
| Validaciones | 4/4 | | | | | |
