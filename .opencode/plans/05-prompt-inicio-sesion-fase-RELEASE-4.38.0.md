# FASE-RELEASE-4.38.0: Documentación Oficial + Release

**Plan:** FEATURE-CONFIG-EXTRACTION v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.9.0, §7 FASE-RELEASE
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~38 iteraciones
**Dependencias:** TODAS las fases (CONFIG-1 a CONFIG-8) DEBEN estar ✅ COMPLETADAS
**Versión target:** 4.38.0
**Codename:** "Config Extraction — Hardcodes to YAML"

---

## Contexto

**Fuente:** `docs/CONTRIBUTING.md` §55-163

Esta fase NO modifica código fuente. Solo ejecuta documentación oficial y validaciones finales siguiendo el protocolo E1-E8 de `phased_project_executor.md` §7.

**Pre-requisito:** Verificar que TODAS las fases están completadas:
```bash
grep -E "FASE-CONFIG-[1-8]|FASE-RELEASE" .opencode/plans/06-checklist-implementacion.md | grep "✅"
```
Deben aparecer 8 fases CONFIG + ésta = 9 fases completadas.

---

## Tareas — Protocolo E1-E8

### Tarea 1: E1 Diagnóstico Inicial + E2 Sync
```bash
# E1: Diagnóstico
venv/Scripts/python.exe scripts/version_consistency_checker.py
venv/Scripts/python.exe main.py --doctor

# E2: Sincronización automática (AHORA CORREGIDA por FASE-CONFIG-1)
# Primero actualizar VERSION.yaml → 4.38.0
# Luego ejecutar sync CORREGIDO:
venv/Scripts/python.exe scripts/sync_versions.py
```
- [ ] version_consistency_checker.py pasa sin discrepancias
- [ ] doctor.py no reporta errores críticos
- [ ] sync_versions.py propaga 4.38.0 a 6 archivos (AHORA SÍ funciona)
- [ ] sync_versions.py --check reporta "All files in sync" (REAL, no falso positivo)

### Tarea 2: E3 CHANGELOG.md + E4 GUIA_TECNICA.md
**E3 — CHANGELOG.md (formato CONTRIBUTING.md):**
```markdown
## [4.38.0] - FEATURE-CONFIG-EXTRACTION (2026-05-XX)

### Objetivo
Corrección del bug sync_versions + migración de 31 hardcodes a archivos YAML con schema validado.
Resolución de 7 causas raíz identificadas en auditoría forense v2.

### Cambios Implementados
- CR-1/CR-2/CR-3: Corrección bug sync_versions (doble escape YAML + validación post-reemplazo + consistencia "v")
- CR-3: Fallbacks migrados a config/fallbacks.yaml con flag "estimated" visible
- CR-4: Parámetros financieros migrados a config/pricing.yaml, config/scenarios.yaml, config/financial_defaults.yaml
- CR-5: Duplicación de garantías eliminada — unificado en template + commercial.yaml
- CR-6: Reconexión config/código — settings.yaml depurado de duplicados
- CR-7: Narrativas de impacto + umbrales migrados a config/regional_benchmarks.yaml
- 31 hardcodes extraídos a 6 archivos YAML con schema validado

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| config/pricing.yaml | TIER_CONFIG, GATE ratios, floor_price unificado (1.2M) |
| config/scenarios.yaml | Recovery factors, scenario weights, degradation, OTA shifts, ia_boost, pain_ratio |
| config/financial_defaults.yaml | DEFAULTS financieros (12 valores) |
| config/fallbacks.yaml | Fallbacks de scores con flags estimated |
| config/commercial.yaml | ROI cap, break_even, descuentos, garantías, planes |
| config/regional_benchmarks.yaml | Pain narratives (14) + umbrales de scoring multi-región |
| tests/config/test_config_*.py | 8 archivos de tests de migración y regresión |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| scripts/sync_config.yaml | CR-1: Corrección doble escape en 2 patterns + consistencia "v" |
| scripts/sync_versions.py | CR-2: Validación post-reemplazo |
| modules/financial_engine/pricing_calculator.py | CR-4: TIER_CONFIG + GATE ratios → YAML |
| modules/financial_engine/scenario_calculator.py | CR-4: OTA shifts + ia_boost → YAML |
| modules/financial_engine/loss_projector.py | CR-4: degradation_rate → YAML |
| modules/utils/financial_factors.py | CR-4: DEFAULTS + SUPERPOSITION_FACTOR → YAML |
| modules/commercial_documents/v4_proposal_generator.py | CR-3/4/5: fallbacks + recovery_factors + weights + garantías + comerciales → YAML |
| modules/commercial_documents/v4_diagnostic_generator.py | CR-3/7: voice_readiness + pain narratives + umbrales → YAML |
| modules/commercial_documents/templates/propuesta_v6_template.md | CR-5: Garantías unificadas, variables comerciales |
| config/settings.yaml | CR-6: Depurado de duplicados, marcado como legacy |
| scripts/doctor.py | Verificación de integridad de config files |

### Tests
- 30+ tests nuevos en tests/config/ (migración, fallback, schema, integración)
- 0 regresiones en tests existentes
- v4complete Amazilia Hotel: coherence >= 0.80, publication READY_FOR_PUBLICATION
```

**E4 — GUIA_TECNICA.md:**
Agregar sección "Notas de Cambios v4.38.0" con:
- **Módulos afectados:** pricing_calculator, scenario_calculator, loss_projector, financial_factors, v4_proposal_generator, v4_diagnostic_generator, sync_versions, sync_config
- **Problema:** 31 hardcodes + bug sync_versions causaban datos falsos y versiones stale
- **Solución:** Extracción a 6 archivos YAML con schema validado + fallback a defaults para backwards compatibility
- **Backwards compatibility:** Sin YAML, usa defaults documentados. Con YAML, todos los valores son configurables sin tocar código.
- **Tests:** 30+ tests de migración y schema

### Tarea 3: E5 Skills/Workflows + E6 SYSTEM_STATUS + E7 DOMAIN_PRIMER
```bash
# E5: Verificar skills/workflows
ls -la .agents/workflows/*.md

# E6: Regenerar SYSTEM_STATUS
venv/Scripts/python.exe scripts/doctor.py --status

# E7: Verificar DOMAIN_PRIMER
venv/Scripts/python.exe scripts/doctor.py --context
```
- [ ] Todos los .md en .agents/workflows/ listados en README.md
- [ ] SYSTEM_STATUS.md regenerado con v4.38.0
- [ ] DOMAIN_PRIMER.md verificado

### Tarea 4: E8 Symlink + Validación Final + Commit
```bash
# Verificar symlink
ls -la .agent/workflows

# Validación final
venv/Scripts/python.exe scripts/run_all_validations.py --quick
venv/Scripts/python.exe scripts/sync_versions.py --check

# Verificar cambios
git diff --stat

# Commit
git add -A
git commit -m "RELEASE 4.38.0: FEATURE-CONFIG-EXTRACTION — 31 hardcodes → 6 YAML + sync fix + v4complete validado"
```
- [ ] Symlink .agent/workflows → .agents/workflows intacto
- [ ] run_all_validations.py --quick: 4/4
- [ ] sync_versions.py --check: All files in sync (REAL)
- [ ] git diff --stat muestra todos los archivos modificados
- [ ] Commit realizado

---

## Archivos Involucrados

| Archivo | Tipo | Acción |
|---------|------|--------|
| `VERSION.yaml` | MODIFICAR | 4.37.0 → 4.38.0, codename actualizado |
| `CHANGELOG.md` | MODIFICAR | Nueva entrada [4.38.0] |
| `docs/GUIA_TECNICA.md` | MODIFICAR | Nota técnica v4.38.0 |
| `AGENTS.md` | AUTO (sync) | Version header actualizado |
| `README.md` | AUTO (sync) | Version header actualizado |
| `.cursorrules` | AUTO (sync) | Version header actualizado |
| `docs/CONTRIBUTING.md` | AUTO (sync) | Version header actualizado |
| `docs/contributing/REGISTRY.md` | AUTO (sync) | Version header actualizado |
| `.agent/SYSTEM_STATUS.md` | AUTO (doctor) | Regenerado |

---

## Criterios de Completitud

- [ ] VERSION.yaml: 4.38.0 + codename "Config Extraction — Hardcodes to YAML"
- [ ] sync_versions.py CORREGIDO propaga a 6 archivos (verificar con --check)
- [ ] CHANGELOG.md: entrada [4.38.0] con formato CONTRIBUTING.md completo
- [ ] GUIA_TECNICA.md: nota técnica v4.38.0 con módulos, problema, solución, backwards compatibility
- [ ] SYSTEM_STATUS.md regenerado
- [ ] DOMAIN_PRIMER.md verificado
- [ ] run_all_validations.py --quick: 4/4
- [ ] git commit realizado
- [ ] NO se modificó código fuente

---

## Restricciones

- **NO modificar** código fuente (solo documentación + version bump)
- **NO ejecutar** v4complete o v4audit
- **NO modificar** ROADMAP.md
- **NO crear** nuevos archivos de código
- **Máximo 60 iteraciones** (R2)

---

## Post-Ejecución (CIERRE DEL PROYECTO)

```bash
venv/Scripts/python.exe scripts/log_phase_completion.py     --fase FASE-RELEASE-4.38.0     --desc "Release 4.38.0: FEATURE-CONFIG-EXTRACTION. 31 hardcodes → 6 YAML + sync fix + v4complete Amazilia validado. 7 causas raíz corregidas."     --archivos-mod "VERSION.yaml,CHANGELOG.md,docs/GUIA_TECNICA.md"     --tests "30+"     --coherence [COMPLETAR_CON_VALOR_DE_CONFIG-7]     --check-manual-docs
```

**PROYECTO COMPLETADO.** Verificar:
- [ ] 10/10 fases completadas en `06-checklist-implementacion.md`
- [ ] `dependencias-fases.md` refleja estados finales
- [ ] Todos los GAPs documentados en `ANALISIS_HALLAZGOS.md`
