# Checklist Maestro de Implementación — DIAGNOSTIC-ALIGNMENT

> Actualizar después de cada fase. NO marcar ✅ sin verificación.

## FASE-A: Fix E1 (Escenarios) + E2 (Antes/Ahora)

|| ID | Tarea | Estado | Evidencia |
||----|-------|--------|-----------|
|| A1 | Investigar `_build_scenario_table_rows` y cadena de datos | ✅ | — |
|| A2 | Implementar fix E1 (financial_value_range, eliminar clamp) | ✅ | `v4_diagnostic_generator.py` L934-979 |
|| A3 | Insertar tabla Antes/Ahora en template v6 Sección 1 | ✅ | `diagnostico_v6_template.md` L28-32 |
|| A4 | Verificar con tests existentes | ✅ | `run_all_validations.py --quick` 5/5 ✅ |

**Resultado FASE-A**: ✅ COMPLETADA 2026-05-25

---

## FASE-B: Fix F1 (Quick Wins) + F2 (Disclaimer→Gancho)

| ID | Tarea | Estado | Evidencia |
|----|-------|--------|-----------|
| B1 | Investigar `_build_quick_wins` y `_prepare_financial_template_vars` | ✅ | `_build_quick_wins` L1595, `_build_precision_warning` L1241 |
| B2 | Reformular Quick Wins en lenguaje de dueño | ✅ | `v4_diagnostic_generator.py` L1595-1651 |
| B3 | Convertir disclaimer Tier C en Oportunidad de Auditoría | ✅ | `v4_diagnostic_generator.py` L1241-1269 |
| B4 | Verificar con tests existentes | ✅ | `test_precision_rendering.py` 12/12 ✅ |
| B5 | Tests de Quick Wins (`_build_quick_wins_content`) | ✅ | Sin regresiones |

**Resultado FASE-B**: ✅ COMPLETADA 2026-05-25

---

## FASE-C: Fix F3 (Puente) + F4 (Encabezado)

| ID | Tarea | Estado | Evidencia |
|----|-------|--------|-----------|
| C1 | Localizar puntos de inserción | ✅ | `diagnostico_v6_template.md` L64-74, `v4_diagnostic_generator.py` L2294-2307 |
| C2 | Agregar texto puente 7 brechas → 3 fugas | ✅ | `diagnostico_v6_template.md` L66-67 |
| C3 | Cambiar "+$" → "Fuga mensual estimada" | ✅ | `v4_diagnostic_generator.py` L2306 |
| C4 | Verificar | ✅ | `run_all_validations.py --quick` 5/5 ✅ |

**Resultado FASE-C**: ✅ COMPLETADA 2026-05-25

---

## FASE-D: v4complete + Verificación

| ID | Tarea | Estado | Evidencia |
|----|-------|--------|-----------|
| D1 | Pre-vuelo: verificar fixes en su lugar | ⬜ | — |
| D2 | Ejecutar v4complete Hotel Castilla Real | ⬜ | `output/v4_complete/` |
| D3 | Verificar 6 criterios Prospección.md | ⬜ | `evidence/fase-D/` |

**Criterios de verificación**:

| # | Criterio | Estado |
|---|----------|--------|
| E1 | Conservador ($2.99M) < Realista ($3.74M) < Optimista ($4.49M) | ⬜ |
| E2 | Tabla "Antes vs Ahora" en Sección 1 | ⬜ |
| F1 | Quick Wins: "HOY", "ESTA SEMANA", "DELEGAR" | ⬜ |
| F2 | "OPORTUNIDAD DE AUDITORÍA PROFUNDA" en Sección 3 | ⬜ |
| F3 | "De las 7 brechas..." en Sección 4 | ⬜ |
| F4 | "Fuga mensual estimada" en tabla resumen | ⬜ |

**Resultado FASE-D**: ⬜ PENDIENTE

---

## FASE-RELEASE: Documentación Oficial

| ID | Tarea | Estado | Evidencia |
|----|-------|--------|-----------|
| R1 | Version bump VERSION.yaml → 4.52.0 | ⬜ | `VERSION.yaml` |
| R2 | sync_versions.py + version_consistency_checker.py | ⬜ | Output de comandos |
| R3 | CHANGELOG.md entrada [4.52.0] | ⬜ | `CHANGELOG.md` |
| R4 | GUIA_TECNICA.md + validaciones finales | ⬜ | `run_all_validations.py --quick` 4/4 |

**Resultado FASE-RELEASE**: ⬜ PENDIENTE

---

## Resumen Global

| Fase | Estado | Fecha |
|------|--------|-------|
| FASE-A | ✅ COMPLETADA | 2026-05-25 |
| FASE-B | ✅ COMPLETADA | 2026-05-25 |
| FASE-C | ✅ COMPLETADA | 2026-05-25 |
| FASE-D | ⬜ PENDIENTE | — |
| FASE-RELEASE | ⬜ PENDIENTE | — |

**Progreso**: 3/5 fases completadas
