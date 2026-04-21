# Checklist de Implementacion — AMH_REFACTOR_V3_ALT

## Estado General

| Fase | ID | Estado | Fecha | Notas |
|------|----|--------|-------|-------|
| FASE-1 | DATASOURCE-GAP | Completada | 2026-04-21 | 13 tests, phone_web fallback fix |
| FASE-2 | BRIDGE-QUALITY-GUARD | Completada | 2026-04-21 | 5 tests, quality gate implementado |
| FASE-3 | MINIMUM-DATA-GUARANTEE | Pendiente | — | Garantia de datos minimos |
| FASE-RELEASE | RELEASE-4.33.0 | Pendiente | — | E2E + release |

## FASE-1: DATASOURCE-GAP
- [x] T0: Pre-validar fuentes de fallback (curl amaziliahotel.com para schema, telefono, direccion)
- [x] T1: Rastrear data flow GBP API → v4_comprehensive → audit_result.gbp
- [x] T2: Verificar si gbp.lat/lng/phone son None cuando Places API falla
- [x] T3: Verificar si schema.properties esta vacio cuando no hay schema en HTML
- [x] T4: Agregar logging de diagnostico en _extract_validated_fields()
- [x] T5: Fix fallbacks completos: telephone (cross_validation), geo (schema.geo), address (gbp.formatted_address), rating (gbp.rating), review_count (gbp.user_ratings_total)
- [x] T6: Tests 13 nuevos (casos: gbp vacio, schema vacio, ambos vacios, gbp parcial, gbp completo, address fallback, rating fallback, review_count fallback, all critical fields)
- [x] Syntax check pasa
- [x] log_phase_completion.py ejecutado
- [x] REGISTRY.md actualizado

## FASE-2: BRIDGE-QUALITY-GUARD
- [x] T1: Definir funcion _is_better_schema() que compara schemas campo por campo
- [x] T2: Implementar quality check en try_enrich_from_geo_enriched() antes de reemplazar
- [x] T3: Agregar verificacion: si reemplazo tiene MENOS campos que original → NO reemplazar
- [x] T4: Agregar verificacion: si reemplazo tiene @type diferente → advertir en log
- [x] T5: Tests >= 5 nuevos (reemplazo mejor, reemplazo peor, reemplazo igual, tipo diferente, confidence edge cases)
- [x] Syntax check pasa
- [x] log_phase_completion.py ejecutado
- [x] REGISTRY.md actualizado

## FASE-3: MINIMUM-DATA-GUARANTEE
- [x] T1: CRITICAL_FIELDS definido (mandatory, important, nice_to_have)
- [x] T2: _validate_hotel_data_completeness() implementada (scoring 0.0-1.0)
- [x] T3: Garantia de datos minimos en _generate_hotel_schema() + Data Rescue flag
- [x] T4: Penalizacion confidence: data_rescue=0.3, completeness<0.3→0.5, <0.6→0.7
- [x] T5: Fallback pais Colombia "CO" en _extract_validated_fields()
- [x] T6: Tests 5 nuevos pasando (28/28 total)
- [x] Syntax check pasa
- [x] log_phase_completion.py ejecutado
- [x] REGISTRY.md actualizado

## FASE-RELEASE: 4.33.0
- [ ] T1: Syntax check y tests de regresion pasan
- [ ] T2: v4complete E2E ejecutado
- [ ] T3: hotel_schema validado: telephone, address, geo presentes; confidence >= 0.7; fallbacks activados
- [ ] T4: GEO-BRIDGE quality gate validado
- [ ] T5: Publication gates pasan
- [ ] T6: Documentacion actualizada (VERSION, CHANGELOG, GUIA_TECNICA, REGISTRY)
- [ ] T7: Plan de contingencia NO se activo (o se ejecuto si schema vacio)
- [ ] T8: git commit + tag v4.33.0 (solo si exito)
- [ ] log_phase_completion.py ejecutado con --release
