
# PLAN CONSOLIDACION: AEO/IAO Redundance Elimination
**Version**: v1.0
**Fecha**: 2026-04-03
**Tipo**: Refactor tecnico + limpieza de scorecard

## Resumen Ejecutivo

El sistema genera scores redundantes AEO e IAO que miden esencialmente lo mismo (infraestructura de datos estructurados). IAO solo se diferencia cuando hay GA4 + IATester funcionando con datos reales, pero en la practica actual su fallback es `_calculate_schema_infra_score()`, o sea, **IAO = AEO + fallback = IAO mal nombrado**.

El diagnostico presenta estos scores redundantes al hotelero, quien no puede distinguirlos y percibe el sistema como inconsistente. Ademas, se incluye "Busqueda por voz" como score separado cuando se resuelve con el mismo trabajo AEO.

**Regla de oro**: Si el diagnostico no tiene un Asset para resolver el dolor, no va en el scorecard. Si no puede medirlo con datos del audit, no genera score.

## Fases del Proyecto

| Fase | ID | Descripcion | Sesion | Archivos |
|------|-----|-------------|--------|----------|
| 1 | `FASE-CAUSAL-01` | Eliminar IAO/score redundante del scorecard (template + generator) | Nueva | 3 archivos |
| 2 | `FASE-CAUSAL-02` | Reestructurar gap_analyzer: 3 pilares -> 2 pilares (GBP + AEO) | Nueva | 2 archivos |
| 3 | `FASE-CAUSAL-03` | Eliminar IAO/report_builder.py y dead code voice_readiness | Nueva | 3 archivos |
| 4 | `FASE-RELEASE-4.21.0` | Documentation sync, registry, changelog | Nueva | 4 archivos |

## Diagrama de Dependencias

```
FASE-CAUSAL-01 (scorecard + generator)
    |
    ├── afecta: v4_diagnostic_generator.py, diagnostico_v6_template.md, v4_diagnostic_generator.py templates
    |
    v
FASE-CAUSAL-02 (gap_analyzer)
    |
    ├── necesita: Fase 1 completada (AEO score unico confirmado)
    ├── afecta: gap_analyzer.py, tests relacionados
    |
    v
FASE-CAUSAL-03 (report_builder + cleanup)
    |
    ├── necesita: Fase 1 y 2 completadas
    ├── afecta: report_builder.py, aeo_metrics_gen.py (opcional), dead code
    |
    v
FASE-RELEASE-4.21.0
    |
    ├── necesita: Todas las fases completadas
    └── Cambios: CHANGELOG.md, REGISTRY.md, version update
```

## Conflicto de Archivos

| Archivo | Fases que lo tocan | Riesgo | Mitigacion |
|---------|-------------------|--------|------------|
| `v4_diagnostic_generator.py` | Fase 1 | Solo esta fase lo toca | No hay conflicto |
| `diagnostico_v6_template.md` | Fase 1 | Solo esta fase lo toca | No hay conflicto |
| `gap_analyzer.py` | Fase 2 | Solo esta fase lo toca | No hay conflicto |
| `report_builder.py` | Fase 3 | Solo esta fase lo toca | No hay conflicto |

## Criterios de Exito Global

1. [ ] Scorecard del diagnostico tiene UN solo score AEO (antes tenia AEO + IAO + voice)
2. [ ] GAP analyzer distribuye perdida en 2 pilares (antes 3)
3. [ ] Metodos `_calculate_iao_score()` eliminados de todos los modulos
4. [ ] Metodos `_calculate_voice_readiness_score()` eliminados
5. [ ] CHANGELOG actualizado
6. [ ] REGISTRY actualizado
7. [ ] v4complete genera diagnostico sin `--` ni scores fantasmas
