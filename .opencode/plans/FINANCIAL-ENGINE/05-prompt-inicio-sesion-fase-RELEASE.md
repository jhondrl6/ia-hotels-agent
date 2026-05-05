# 05-prompt-inicio-sesion-fase-RELEASE

**Fase**: RELEASE — Documentación + Version Bump + Validaciones Finales  
**Plan**: Financial Evidence Engine v1.1.0  
**Sesión**: Nueva (fresh)  
**Iteraciones máx**: 60  
**Depende de**: FIN-1A ✅, FIN-1B ✅, FIN-2A ✅, FIN-2B ✅, FIN-3 ✅, CHAN-1 ✅, CHAN-2 ✅, FIN-4 ✅  
**Bloquea a**: Ninguna (última fase)  

---

## Objetivo

Cerrar el proyecto con documentación oficial, version bump, sincronización y validaciones finales. **NO se modifica código fuente** — solo documentación.

---

## Tareas

### T1: Registrar TODAS las fases en REGISTRY.md

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# 8 fases de implementación + validación
for fase in \
    "FIN-1A:Financial Evidence dataclass + epistemic metadata propagation:modules/financial_engine/financial_evidence.py,tests/financial_engine/test_financial_evidence.py:modules/financial_engine/scenario_calculator.py,modules/financial_engine/calculator_v2.py:8" \
    "FIN-1B:NoDefaultsValidator ampliado + precision tier:modules/financial_engine/precision_validator.py,tests/financial_engine/test_no_defaults_precision.py:modules/financial_engine/no_defaults_validator.py:8" \
    "FIN-2A:Regional benchmark 2026 structured data:data/benchmarks/regional_adr_2026.json,tests/financial_engine/test_regional_adr_2026.py:modules/financial_engine/regional_adr_resolver.py:8" \
    "FIN-2B:Feature flags Caribe + ADR fallback chain honesto:tests/financial_engine/test_fallback_chain_honesto.py:modules/financial_engine/feature_flags.py,modules/financial_engine/adr_resolution_wrapper.py:8" \
    "FIN-3:Rendering financiero: rangos, advertencias y CTA:tests/commercial_documents/test_precision_rendering.py:modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/templates/:6" \
    "CHAN-1:Channel Evidence Resolver:modules/financial_engine/channel_evidence_resolver.py,tests/financial_engine/test_channel_evidence_resolver.py::8" \
    "CHAN-2:OpportunityScorer con channel_context:tests/financial_engine/test_opportunity_scorer_channels.py:modules/financial_engine/opportunity_scorer.py,modules/commercial_documents/v4_diagnostic_generator.py:8" \
    "FIN-4:E2E combinado financiero + comercial — Hotel Castilla Real:evidence/FIN-4/::0"; do
    
    IFS=':' read -r fase_name desc archivos_nuevos archivos_mod tests <<< "$fase"
    ./venv/Scripts/python.exe scripts/log_phase_completion.py \
        --fase "$fase_name" \
        --desc "$desc" \
        ${archivos_nuevos:+--archivos-nuevos "$archivos_nuevos"} \
        ${archivos_mod:+--archivos-mod "$archivos_mod"} \
        --tests "$tests" \
        --check-manual-docs
done
```

### T2: Version bump + sync

```bash
# Actualizar versión en VERSION.yaml: 4.39.0 → 4.40.0
# (editar manualmente o usar script)

# Sincronizar VERSION.yaml → 6 archivos
./venv/Scripts/python.exe scripts/sync_versions.py

# Verificar consistencia
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

### T3: Actualizar CHANGELOG.md

Agregar entrada v4.40.0 con formato CONTRIBUTING.md:

```markdown
## [4.40.0] - 2026-05-XX

### Objetivo
Eliminar falsa precisión financiera ($2.610.000 COP/mes desde defaults) implementando 
Financial Evidence Engine + Regional Benchmark Fallback + Evidence-Based Channel Prioritization.
Validado E2E sobre Hotel Castilla Real (hotelcastillareal.com) en 1 sola ejecución v4complete.

### Cambios Implementados
- Modelo de metadata epistémica (FinancialEvidence, EpistemicStatus, PrecisionTier)
- NoDefaultsValidator ampliado con clasificación de fuentes granular (SOURCE_EPISTEMIC_MAP)
- Fuente estructurada regional_adr_2026.json con benchmarks 2026 (3 regiones + default)
- ADRResolutionWrapper con propagación de epistemic_status y can_show_exact
- Caribe agregado a validated_regions en feature_flags.py
- Rendering condicional: rangos + advertencias + CTA para Tier B/C
- Channel Evidence Resolver (inferencia sin hardcodear WhatsApp)
- OpportunityScorer con channel_context opcional y multiplicadores trazables

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| modules/financial_engine/financial_evidence.py | Dataclasses epistémicas |
| modules/financial_engine/precision_validator.py | Validador de precisión financiera |
| modules/financial_engine/channel_evidence_resolver.py | Inferencia de canal por evidencia |
| data/benchmarks/regional_adr_2026.json | Benchmarks 2026 estructurados |
| tests/financial_engine/test_financial_evidence.py | 8 tests |
| tests/financial_engine/test_no_defaults_precision.py | 8 tests |
| tests/financial_engine/test_regional_adr_2026.py | 8 tests |
| tests/financial_engine/test_fallback_chain_honesto.py | 8 tests |
| tests/commercial_documents/test_precision_rendering.py | 6 tests |
| tests/financial_engine/test_channel_evidence_resolver.py | 8 tests |
| tests/financial_engine/test_opportunity_scorer_channels.py | 8 tests |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| modules/financial_engine/scenario_calculator.py | FinancialEvidence en FinancialScenario |
| modules/financial_engine/no_defaults_validator.py | SOURCE_EPISTEMIC_MAP + precision tier |
| modules/financial_engine/regional_adr_resolver.py | Metadata epistémica en resultados |
| modules/financial_engine/feature_flags.py | Caribe en validated_regions |
| modules/financial_engine/adr_resolution_wrapper.py | epistemic_status + can_show_exact |
| modules/financial_engine/opportunity_scorer.py | channel_context + multiplicadores |
| modules/commercial_documents/v4_diagnostic_generator.py | Render rangos + channel_context |

### Tests
- 54 tests nuevos, 0 regresiones
- Validación E2E: Hotel Castilla Real (hotelcastillareal.com)
```

### T4: Actualizar GUIA_TECNICA.md

Agregar notas técnicas por fase. Mínimo requerido:

```markdown
### Notas de Cambios v4.40.0 — Financial Evidence Engine

#### FIN-1A: Epistemic Metadata Model
- Módulos: financial_evidence.py (NUEVO), scenario_calculator.py
- Problema: Sistema no distinguía fuentes de datos
- Solución: FinancialEvidence dataclass con EpistemicStatus, PrecisionTier
- Backwards compatible: Sí (FinancialScenario.financial_evidence opcional)
- Tests: 8

#### FIN-1B: NoDefaultsValidator Ampliado
- Módulos: precision_validator.py (NUEVO), no_defaults_validator.py
- Solución: SOURCE_EPISTEMIC_MAP granular + PrecisionValidator
- Backwards compatible: Sí (SUSPECT_SOURCES se mantiene)
- Tests: 8

#### FIN-2A: Regional Benchmark 2026
- Módulos: regional_adr_2026.json (NUEVO), regional_adr_resolver.py
- Solución: Datos 2026 del Benchmarking.md a JSON operativo con metadata
- Tests: 8

#### FIN-2B: Feature Flags + Fallback Chain
- Módulos: feature_flags.py, adr_resolution_wrapper.py
- Solución: Caribe validado, epistemic_status en toda la cadena ADR
- Tests: 8

#### FIN-3: Rendering Condicional
- Módulos: v4_diagnostic_generator.py, templates
- Solución: Rangos + advertencias + CTA según precision tier
- Tests: 6

#### CHAN-1: Channel Evidence Resolver
- Módulos: channel_evidence_resolver.py (NUEVO)
- Solución: Inferencia de canal sin hardcodear WhatsApp
- Tests: 8

#### CHAN-2: OpportunityScorer + Channel Weights
- Módulos: opportunity_scorer.py, v4_diagnostic_generator.py
- Solución: channel_context opcional con multiplicadores trazables
- Tests: 8

#### FIN-4: E2E Combinado
- Hotel: Castilla Real (hotelcastillareal.com)
- Resultado: [completar con veredicto de FIN-4]
```

### T5: Validaciones finales

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Validación completa
./venv/Scripts/python.exe scripts/run_all_validations.py --quick

# Estado del sistema
./venv/Scripts/python.exe scripts/doctor.py --status

# Todos los tests nuevos
./venv/Scripts/python.exe -m pytest \
    tests/financial_engine/test_financial_evidence.py \
    tests/financial_engine/test_no_defaults_precision.py \
    tests/financial_engine/test_regional_adr_2026.py \
    tests/financial_engine/test_fallback_chain_honesto.py \
    tests/commercial_documents/test_precision_rendering.py \
    tests/financial_engine/test_channel_evidence_resolver.py \
    tests/financial_engine/test_opportunity_scorer_channels.py \
    -v --tb=short

# No-regresión en módulos financieros
./venv/Scripts/python.exe -m pytest tests/financial_engine/ -v --tb=short
```

---

## Criterios de Completitud

- [ ] `log_phase_completion.py` ejecutado para las 8 fases
- [ ] REGISTRY.md actualizado con todas las fases
- [ ] `sync_versions.py` ejecutado → 6 archivos sincronizados
- [ ] `version_consistency_checker.py` pasa
- [ ] CHANGELOG.md con entrada v4.40.0 y formato correcto
- [ ] GUIA_TECNICA.md con notas técnicas por fase
- [ ] `run_all_validations.py --quick` pasa (4/4)
- [ ] `doctor.py --status` sin errores
- [ ] 54 tests pasan, 0 regresiones

---

## Restricciones

- **Modo de Ejecución**: DIRECTO con agente principal. Fase de documentación pura (5 tareas, 0 comandos largos) — aplica Regla código+tests del workflow v2.10.0 §Decisión. NO usar subagente. Budget: ~20 iteraciones para T1-T3 + ~15 para T4-T5 + ~25 para validaciones/docs.
- Máximo 60 iteraciones
- **NO modificar código fuente** — solo documentación
- **NO ejecutar v4complete** (ya ejecutado en FIN-4)
- Seguir flujo documental obligatorio (§4.5 del workflow v2.10.0)

---

## Post-Ejecución

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

echo "=== VERIFICACIONES FINALES ==="
grep "## FASE-" docs/contributing/REGISTRY.md | tail -8
./venv/Scripts/python.exe scripts/sync_versions.py
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/doctor.py --status

echo ""
echo "✅ RELEASE v4.40.0 COMPLETADO"
echo "Hotel validado: Hotel Castilla Real (hotelcastillareal.com)"
echo "Ejecuciones v4complete: 1"
```
