
# Checklist de Implementacion: Consolidacion AEO/IAO

**Proyecto**: iah-cli - Eliminacion de redundancia AEO/IAO en scorecards
**Version target**: 4.21.0
**Fecha inicio**: 2026-04-03

---

## Estado de Fases

| # | Fase | ID | Estado | Sesion | Fecha |
|---|------|-----|--------|--------|-------|
| 1 | Scorecard + Generator | `FASE-CAUSAL-01` | completado | sesion-actual | 2026-04-04 |
| 2 | GAP Analyzer | `FASE-CAUSAL-02` | pendiente | nueva | - |
| 3 | Report Builder + Cleanup | `FASE-CAUSAL-03` | pendiente | nueva | - |
| 4 | Release Docs | `FASE-RELEASE-4.21.0` | pendiente | nueva | - |

---

## Checklist Detallado por Fase

### FASE CAUSAL-01: Scorecard + Generator
- [ ] `_calculate_iao_score()` eliminado de v4_diagnostic_generator.py
- [ ] `_calculate_score_ia()` eliminado de v4_diagnostic_generator.py
- [ ] `_calculate_voice_readiness_score()` eliminado de v4_diagnostic_generator.py
- [ ] `_calculate_schema_infra_score()` renombrado a `_calculate_aeo_score()`
- [ ] Variables `iao_score/iao_status/voice_readiness` eliminadas de `_prepare_template_data()`
- [ ] Referencias a `iao_score` eliminadas de `_inject_analytics()`
- [ ] diagnostico_v6_template.md: fila "Optimizacion ChatGPT" eliminada
- [ ] diagnostico_v6_template.md: fila "Visibilidad en IA (AEO)" eliminada
- [ ] diagnostico_v6_template.md: nueva fila "AEO - Infraestructura para IAs" con `${aeo_score}/100`
- [ ] Scorecard final tiene 4 filas (GEO, GBP, AEO, SEO)
- [ ] Python syntax valida en todos los archivos
- [ ] `log_phase_completion.py --fase FASE-CAUSAL-01` ejecutado

### FASE CAUSAL-02: GAP Analyzer
- [ ] `iao_benchmark` eliminado de gap_analyzer.py
- [ ] `iao_score` eliminado de gap_analyzer.py
- [ ] `gap_iao` eliminado de gap_analyzer.py
- [ ] `suma_gaps = gap_geo + gap_aeo` (solo 2 pilares)
- [ ] Bloque "Pilar 3: Momentum IA" eliminado
- [ ] `_calculate_iao_score()` de gap_analyzer eliminado si existe
- [ ] Perdida distribuida correctamente entre 2 pilares
- [ ] Python syntax valida
- [ ] `log_phase_completion.py --fase FASE-CAUSAL-02` ejecutado

### FASE CAUSAL-03: Report Builder + Cleanup
- [ ] `_calculate_iao_score()` eliminado de report_builder.py
- [ ] Variables `iao_score/iao_ref/iao_diff` eliminadas de report_builder.py
- [ ] Filas IAO eliminadas de scorecards generados por report_builder.py
- [ ] aeo_metrics_gen.py verificado sin errores de import
- [ ] data_models/aeo_kpis.py verificado importable
- [ ] Python syntax valida
- [ ] `log_phase_completion.py --fase FASE-CAUSAL-03` ejecutado

### FASE RELEASE-4.21.0: Documentacion
- [ ] CHANGELOG.md con entrada 4.21.0
- [ ] REGISTRY.md actualizado (automatico via log_phase_completion)
- [ ] Version Sync Gate paso sin errores
- [ ] Modulos importan sin errores
- [ ] v4complete de prueba exitoso (opcional)
- [ ] `log_phase_completion.py --fase FASE-RELEASE-4.21.0` ejecutado
- [ ] `git add -A && git commit` realizado

---

## Metricas del Proyecto

| Metrica | Valor Inicial | Valor Final |
|---------|--------------|-------------|
| Scores en scorecard V6 | 5 | 4 |
| Scores fantasmas (--) | 1 (AEO/Voice) | 0 |
| Scores redundantes (IAO=AEO) | 1 | 0 |
| Modulos que usan IAO | 3 | 0 |
| Lineas de dead code | ~100 | 0 |
| Version del proyecto | 4.20.0 | 4.21.0 |
