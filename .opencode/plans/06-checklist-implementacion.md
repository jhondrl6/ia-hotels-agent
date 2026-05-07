# Checklist de Implementación

> Plan: PROPOSAL-COMERCIAL-FIX v1.0.0

## FASE-PROP-A: Unificación de Coherence Score

### Tareas
- [x] Pipeline reordenado: CoherenceValidator/resultado disponible antes del diagnóstico
- [x] Diagnóstico usa valor real: no inventa coherence_score
- [x] Template muestra gate_status: PASSED/FAILED/PENDIENTE visible
- [x] Fallback degradado: `_calculate_coherence_score()` no produce valores ficticios automáticamente
- [x] Tests pasan: 7/7 tests nuevos pasan
- [x] Validaciones del proyecto: `run_all_validations.py --quick` pasa 4/4
- [x] Documentación afiliada: cambios reflejados en notas de fase

### Archivos Modificados
| Archivo | Tipo de Cambio |
|---------|---------------|
| `main.py` | Modificación — pasa `gate_status` a `diagnostic_gen.generate()` |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Modificación — acepta `gate_status`, lógica `coherence_score` unificada, fallback deprecado |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Modificación — agrega `gate_status` al YAML header |

### Archivos Nuevos
|| Archivo | Descripción |
|---------|-------------|
|| `tests/commercial_documents/test_diagnostic_generator.py` | 7 tests para FASE-PROP-A |

## FASE-PROP-B: WhatsApp Conflict Status en Propuesta

### Tareas
- [x] WhatsApp conflict detection en `_confidence_to_nivel_significado()`
- [x] Tabla de calidad muestra conflicto cuando `whatsapp_status='conflict'`
- [x] Test coverage para casos: conflict, verified, no-audit
- [x] Validaciones del proyecto: `run_all_validations.py --quick` pasa 4/4

### Archivos Modificados
|| Archivo | Tipo de Cambio |
|---------|---------------|
|| `v4_proposal_generator.py` | Modificación — conflicto WhatsApp en asset_quality_table |

### Archivos Nuevos
|| Archivo | Descripción |
|---------|-------------|
|| `tests/commercial_documents/test_proposal_generator.py` | Tests para FASE-PROP-B |

## FASE-PROP-C: Proyecciones Financieras Transparentes

### Tareas
- [x] Reescribir `pain_ratio_note` para explicar pain_ratio y recovery_factor
- [x] Añadir `${pain_ratio_note}` al template propuesta_v6_template.md
- [x] Documentar Opción A como deuda técnica (comentario en código)
- [x] Tests nuevos: 2 tests para verificar nota con pain_ratio y recovery_factor
- [x] Validaciones del proyecto: `run_all_validations.py --quick` pasa 4/4

### Archivos Modificados
|| Archivo | Tipo de Cambio |
|---------|---------------|
|| `modules/commercial_documents/v4_proposal_generator.py` | Modificación — pain_ratio_note reescrito |
|| `modules/commercial_documents/templates/propuesta_v6_template.md` | Modificación — nota visible cerca de tabla |

### Archivos Nuevos
|| Archivo | Descripción |
|---------|-------------|
|| `tests/commercial_documents/test_proposal_generator.py` | Tests para FASE-PROP-C |

## Estado: Fases Completadas

- [x] FASE-PROP-A: ✅ Completada
- [x] FASE-PROP-B: ✅ Completada
- [x] FASE-PROP-C: ✅ Completada
- [x] FASE-PROP-D: ✅ Completada
- [x] FASE-PROP-E: ✅ Completada
- [x] FASE-PROP-F: ✅ Completada
- [x] FASE-RELEASE-4.41.0: ✅ Completada

---

## FASE-PROP-D: Google Maps — Asset o Redefinición

### Tareas
- [x] Verificar que assets GEO existentes cubren la función de geo_playbook
- [x] Decisión documentada: ELIMINAR — geo_playbook es redundante con delivery GEO
- [x] Implementar: geo_playbook DEPRECATED en asset_catalog.py
- [x] Implementar: eliminar geo_playbook de pain_solution_mapper.py (low_gbp_score → solo review_plan)
- [x] Implementar: eliminar geo_playbook de conditional_generator.py
- [x] Implementar: eliminar geo_playbook de asset_diagnostic_linker.py
- [x] Implementar: eliminar geo_playbook de site_presence_checker.py
- [x] Tests pasan: 10 nuevos (5 asset_catalog + 5 proposal_generator)
- [x] Tests existentes: 21+15 = 36/36 PASS
- [x] Validaciones del proyecto: `run_all_validations.py --quick` pasa 4/4
- [x] Documentación afiliada: GUIA_TECNICA.md actualizado
- [x] log_phase_completion.py ejecutado

### Archivos Modificados
||| Archivo | Tipo de Cambio |
|---------|---------------|
||| `modules/asset_generation/asset_catalog.py` | Modificación — geo_playbook status DEPRECATED, promised_by=[] |
||| `modules/commercial_documents/pain_solution_mapper.py` | Modificación — low_gbp_score solo review_plan, ASSET_NAMES sin geo_playbook |
||| `modules/asset_generation/conditional_generator.py` | Modificación — eliminado de _standard_assets y handler elif |
||| `modules/asset_generation/asset_diagnostic_linker.py` | Modificación — eliminado de justifications, impact_map, metadata |
||| `modules/asset_generation/site_presence_checker.py` | Modificación — eliminada entrada geo_playbook |
||| `docs/GUIA_TECNICA.md` | Modificación — nota técnica FASE-PROP-D agregada |

### Archivos Nuevos
||| Archivo | Descripción |
|---------|-------------|
||| Ninguno — solo modificaciones y tests nuevos en archivos existentes |

## FASE-PROP-E: SEO/AEO Plan Específico por Score

### Tareas
- [x] Plan 7 días incluye acción SEO cuando score < 30
- [x] Plan 7 días incluye Schema FAQ/AEO cuando score_aeo < 30
- [x] Plan 30 días incluye acciones específicas por score bajo
- [x] Tabla de calidad incluye AEO cuando score_aeo < 30
- [x] Tests pasan: 6 tests nuevos
- [x] Validaciones del proyecto: `run_all_validations.py --quick` pasa 4/4

### Archivos Modificados
|| Archivo | Tipo de Cambio |
|---------|---------------|
|| `modules/commercial_documents/v4_proposal_generator.py` | Modificación — _build_7_day_plan y _build_30_day_plan con score-based prioritization |

### Archivos Nuevos
|| Archivo | Descripción |
|---------|-------------|
|| `tests/commercial_documents/test_proposal_generator.py` | Tests para FASE-PROP-E |

## FASE-PROP-F: Tier C — Advertencia en Propuesta

### Tareas
- [x] `_prepare_template_data()` incluye `financial_evidence_tier` extraído de `financial_breakdown.evidence_tier` (fallback: "C")
- [x] Banner condicional `{{if financial_evidence_tier == "C"}}` visible en propuesta_v6_template.md
- [x] Nota sutil para Tier A/B en sección financiera
- [x] Tests pasan: 4 tests nuevos
- [x] Validaciones del proyecto: `run_all_validations.py --quick` pasa 4/4
- [x] log_phase_completion.py ejecutado

### Archivos Modificados
||| Archivo | Tipo de Cambio |
||---------|---------------|
||| `modules/commercial_documents/v4_proposal_generator.py` | Modificación — `_prepare_template_data()` agrega `financial_evidence_tier` desde `financial_breakdown.evidence_tier` |
||| `modules/commercial_documents/templates/propuesta_v6_template.md` | Modificación — bloque condicional Tier C con banner ⚠️ y nota sutil para A/B |

### Archivos Nuevos
||| Archivo | Descripción |
||---------|-------------|
||| `tests/commercial_documents/test_proposal_generator.py` | Tests para FASE-PROP-F (4 tests: Tier C, default C, Tier A, template conditional) |

## FASE-PROP-G: Sobrescritura de Evidencia — Rutas Persistentes

### Tareas
- [x] Identificar TODOS los lugares en main.py donde se escriben `gate_report.json`, `audit_report.json`, `financial_scenarios.json`
- [x] Cambiar la ruta para que incluya `hotel_id` (variable disponible en el pipeline)
- [x] Crear el subdirectorio si no existe (`os.makedirs(..., exist_ok=True)`)
- [x] Nombre resultante incluye timestamp en formato `%Y%m%d_%H%M%S`
- [x] Los archivos .md en la raíz se mantienen con nombre actual (no se cambian)
- [x] Lectores de JSONs verificados: no hay lectores automáticos (solo auditorías humanas)
- [x] Tests pasan: 8 tests nuevos pasan
- [x] Validaciones del proyecto: `run_all_validations.py --quick` pasa 4/4
- [x] Documentación afiliada: dependencias-fases.md + checklist actualizados
- [x] log_phase_completion.py ejecutado

### Archivos Modificados
||| Archivo | Tipo de Cambio |
||---------|---------------|
||| `main.py` | Modificación — 3 escritores de JSON ahora usan `_make_evidence_path()` con `hotel_id/v4_audit/` + timestamp; `hotel_id` derivado arriba para consistencia; resumen final actualizado |

### Archivos Nuevos
||| Archivo | Descripción |
||---------|-------------|
||| `tests/test_evidence_paths.py` | 8 tests para FASE-PROP-G: ruta correcta, creación de dirs, timestamp default, rutas distintas por timestamp, coexistencia de múltiples basenames, persistencia entre runs |

## Próxima Fase

- [ ] FASE-RELEASE-4.41.0: Pendiente
