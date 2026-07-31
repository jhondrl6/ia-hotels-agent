# FASE-RELEASE-4.57.0 — Cierre y Documentación Oficial

**ID**: ROICRIII-FASE-RELEASE-4.57.0
**Objetivo**: Documentación oficial, version bump 4.56.0 → 4.57.0, sync de versiones, validaciones finales.
**Dependencias**: TODAS las fases 1-6 ✅ completadas
**Complejidad**: 🟢 BAJA — Solo documentación y validaciones, NO modifica código fuente
**Skill**: `iah-cli-phased-execution`

---

## Contexto

Esta es la última fase del plan ROICRIII. Todas las correcciones de código fueron implementadas y verificadas en FASE-1 a FASE-6. Esta fase se encarga EXCLUSIVAMENTE de:
- Actualizar VERSION.yaml
- Sincronizar versiones en todos los archivos
- Generar CHANGELOG y GUIA_TECNICA oficiales
- Ejecutar validaciones finales

**Regla**: NO modifica ROADMAP.md, NO edita código fuente, NO ejecuta v4complete.

---

## Tareas

### E1. Diagnóstico Inicial

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/version_consistency_checker.py
./venv/Scripts/python.exe main.py --doctor
```

- [ ] version_consistency_checker.py pasa sin discrepancias
- [ ] doctor no reporta errores críticos

### E2. Version Bump

**Archivo**: `VERSION.yaml`

Actualizar:
```yaml
version: "4.57.0"
codename: "FINANCIAL-COHERENCE"
release_date: "YYYY-MM-DD"  # Fecha real del día
```

Luego sincronizar:
```bash
./venv/Scripts/python.exe scripts/sync_versions.py
```

**IMPORTANTE**: `sync_versions.py` NO acepta `--bump` ni `--release-name`. Editar VERSION.yaml manualmente, luego ejecutar sin args.

- [ ] VERSION.yaml actualizado a 4.57.0
- [ ] sync_versions.py ejecutado sin errores

### E3. CHANGELOG.md

Añadir entrada al inicio de CHANGELOG.md (después del header):

```markdown
## [4.57.0] - Financial Coherence & Asset Semantics Rescue — YYYY-MM-DD

### Objetivo
Resolver regresión crítica de v4.55.0: doble motor de cálculo financiero produciendo ROIs contradictorios, mapeos semánticos incorrectos, y assets deprecados en la propuesta comercial.

### Cambios Implementados
- **Motor Financiero Unificado**: `total_recovered` y `roi_6m` ahora usan `_maturity_result.total_recuperacion_6m` como única fuente de verdad (FASE-1)
- **Pain Ratio Corregido**: `pain_ratio_note` muestra % inversión/fuga real (10.7%) en lugar del `pain_ratio` interno (FASE-2)
- **Validator Semántico Integrado**: `asset_semantics_validator` activo en `_generate_dynamic_services_table` (FASE-3)
- **Assets Deprecados Filtrados**: 4 assets deprecados removidos de output y catálogo (FASE-4)
- **Piloto 30 Días**: Nueva sección de bajo riesgo para clientes sin presupuesto completo (FASE-5)
- **CAPEX Breakdown**: Desglose detallado de Setup Fee (FASE-5)
- **Garantía Día 55**: KPI concreto (+15% clics GSC) reemplaza texto genérico (FASE-5)

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_proposal_generator.py` | Unificación motor, validator, filtrado de deprecados, features |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Eliminar dualidad ROI, piloto, CAPEX, garantía |
| `modules/commercial_documents/service_catalog.py` | Remover `indirect_traffic_optimization` del catálogo |
| `config/commercial.yaml` | Añadir `pilot_options` |

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `tests/commercial_documents/test_financial_coherence.py` | Tests de coherencia financiera (5 tests) |
| `tests/quality/test_asset_semantics_integration.py` | Tests de integración del validator (5 tests) |

### Tests
- 10 tests nuevos en `test_financial_coherence.py` y `test_asset_semantics_integration.py`
- 0 regresiones en suite existente
```

- [ ] CHANGELOG.md tiene entrada [4.57.0] con todas las secciones

### E4. GUIA_TECNICA.md

Añadir sección "Notas de Cambios v4.57.0":

```markdown
## Notas de Cambios v4.57.0 — Financial Coherence & Asset Semantics Rescue

### Módulos Afectados
- `modules/commercial_documents/v4_proposal_generator.py`
- `modules/commercial_documents/service_catalog.py`
- `modules/commercial_documents/templates/propuesta_v6_template.md`
- `config/commercial.yaml`

### Problema
La v4.55.0 introdujo doble motor de cálculo en `_prepare_template_data()`:
1. `total_recovered` usaba `effective_monthly_gain * 6` (path del pain_ratio)
2. `_maturity_result.total_recuperacion_6m` usaba curva de maduración

Resultado: dos ROIs distintos (0.45X vs 2.10X) en el mismo documento → destrucción de confianza comercial.

### Solución
Unificar TODA la proyección financiera al motor de curva de maduración (`pillar_maturity_curve.py`).
El `effective_monthly_gain` se mantiene para otros cálculos internos pero NO para el total renderizado.

### Backwards Compatibility
- **Sin breaking changes**: La API pública no cambió
- `_prepare_template_data()` retorna el mismo dict con valores corregidos
- `asset_semantics_validator` es aditivo (solo filtra, no cambia firma)
- Template V6: `${pilot_section}` y `${trazabilidad_origen}` son nuevos placeholders (opcionales, retornan "" si no aplican)
```

- [ ] GUIA_TECNICA.md tiene nota técnica para v4.57.0

### E5. Regenerar SYSTEM_STATUS.md + DOMAIN_PRIMER

```bash
./venv/Scripts/python.exe scripts/doctor.py --status
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer
./venv/Scripts/python.exe scripts/doctor.py --context
```

- [ ] SYSTEM_STATUS.md regenerado
- [ ] DOMAIN_PRIMER.md regenerado con módulos actuales

### E6. Validación Final

```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/version_consistency_checker.py
git diff --stat
```

- [ ] run_all_validations.py --quick pasa sin errores
- [ ] version_consistency_checker.py pasa
- [ ] git diff muestra todos los archivos modificados del plan completo

### E7. Commit final

```bash
git add -A
git commit -m "release: v4.57.0 Financial Coherence & Asset Semantics Rescue (ROICRIII)"
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** — Marcar FASE-RELEASE como ✅ Completada. Actualizar tabla final.
2. **`06-checklist-implementacion.md`** — Marcar RELEASE como ✅
3. **log_phase_completion.py**:
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe" scripts/log_phase_completion.py --fase FASE-RELEASE-4.57.0 --desc "Release_4.57.0_Financial_Coherence_Rescue" --archivos-mod "VERSION.yaml,CHANGELOG.md,docs/GUIA_TECNICA.md" --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] VERSION.yaml = 4.57.0
- [ ] sync_versions.py ejecutado
- [ ] CHANGELOG.md con entrada [4.57.0] completa
- [ ] GUIA_TECNICA.md con nota técnica v4.57.0
- [ ] SYSTEM_STATUS.md + DOMAIN_PRIMER regenerados
- [ ] run_all_validations.py --quick pasa
- [ ] version_consistency_checker.py pasa
- [ ] git commit con mensaje de release
- [ ] Post-ejecución completada
- [ ] Todas las fases 1-6 en dependencias-fases.md = ✅

---

## Restricciones

- **NO modificar código fuente** (toda la lógica ya está en FASE-1 a FASE-5)
- NO ejecutar v4complete
- NO modificar ROADMAP.md
- `sync_versions.py` NO acepta --bump/--release-name: editar VERSION.yaml manualmente + ejecutar sin args
- `sync_versions.py` usa `datetime.now()` para fecha: la fecha en AGENTS.md será la del día de ejecución
- Límite: 60 iteraciones
