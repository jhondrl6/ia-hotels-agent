# FASE-RELEASE-4.37.0: Cierre Oficial

**ID**: FASE-RELEASE-4.37.0
**Objetivo**: Documentación oficial, version bump a 4.37.0, CHANGELOG, GUIA_TECNICA, validaciones finales. NO modifica código fuente.
**Dependencias**: FASE-PATCH-A ✅ + FASE-PATCH-B ✅ + FASE-PATCH-C ✅ + FASE-PATCH-D ✅
**Duración estimada**: ~30-40 min
**Skill**: iah-cli-phased-execution
**⚠️ ÚLTIMA FASE DEL PROYECTO**

---

## Contexto

El PATCH-Auditoría-Forense-Amazilia-v2 corrigió 9 hallazgos (BUG-1, BUG-2, H-1→H-6, unicode crash) y resolvió 2 pendientes de infraestructura (version drift, derive_version_from_changelog.py). Otros 19 hardcodes (H-9→H-27) quedaron documentados como deuda técnica.

Esta fase empaqueta todo en una release formal siguiendo el protocolo E1-E8 de `phased_project_executor.md` §7 y `CONTRIBUTING.md`.

### Cambios acumulados del proyecto

**PATCH-A**: `v4_proposal_generator.py`, `v4_diagnostic_generator.py`, `version_consistency_checker.py`
**PATCH-B**: `v4_proposal_generator.py`, `two_phase_flow.py`, `scenario_calculator.py`
**PATCH-C**: verificación (sin cambios de código)
**PATCH-D**: `derive_version_from_changelog.py` (NUEVO), `AGENTS.md`, `VERSION.yaml`, `docs/technical_debt/`

---

## Tareas

### E1. Diagnóstico Inicial

```bash
./venv/Scripts/python.exe scripts/version_consistency_checker.py
./venv/Scripts/python.exe main.py --doctor
```

- [ ] version_consistency_checker.py pasa sin discrepancias (ya con unicode fix)
- [ ] doctor no reporta errores críticos

### E2. Sincronización Automática

```bash
./venv/Scripts/python.exe scripts/sync_versions.py
```

- [ ] sync_versions.py ejecutado sin errores

### E3. Actualizar VERSION.yaml → 4.37.0

Editar `VERSION.yaml`:
```yaml
version: "4.37.0"
codename: "PATCH Forense AmaziliaHotel v2"
release_date: "2026-04-29"
```

Luego re-ejecutar sync_versions.py para propagar.

- [ ] VERSION.yaml: 4.37.0
- [ ] sync_versions.py re-ejecutado

### E4. CHANGELOG.md entrada [4.37.0]

Agregar al inicio de CHANGELOG.md (después de `# Changelog`, antes de `## [4.36.1]`):

```markdown
## [4.37.0] - 2026-04-29

### Objetivo

Corrección de hallazgos críticos de auditoría forense AmaziliaHotel: bugs de credibilidad comercial (ROI, pain_ratio), stubs diagnósticos (blog/speakable/ga4), placeholders hardcodeados (web_score, teléfono, Evidence Tier), crash Unicode en version_consistency_checker.py, y version drift 4.36.0→4.36.1. 19 hardcodes de pricing catalogados como deuda técnica.

### Cambios Implementados

#### FASE-PATCH-A: Critical Bugs + Diagnostic Stubs + Unicode Fix
- `modules/commercial_documents/v4_proposal_generator.py`: Eliminado `.replace("X","")` en L556 que mutilaba el formato ROI. Agregada explicación de pain_ratio en sección de proyección.
- `modules/commercial_documents/v4_diagnostic_generator.py`: Reemplazados stubs `blog_activo=False`, `speakable_schema=False`, `ga4_indirect=False` por detección real o marcado explícito "No evaluado".
- `scripts/version_consistency_checker.py`: Agregado `sys.stdout.reconfigure(encoding="utf-8")` para evitar UnicodeEncodeError en Windows cp1252.

#### FASE-PATCH-B: Hardcoded Placeholders + Evidence Integrity
- `modules/commercial_documents/v4_proposal_generator.py`: web_score ahora usa audit_result real o muestra "No disponible" (antes: "85" hardcodeado).
- `modules/orchestration_v4/two_phase_flow.py`: Teléfono placeholder "+57 300 123 4567" reemplazado por valor real o marcador honesto.
- `modules/financial_engine/scenario_calculator.py`: Evidence Tier ahora condicionado a presencia real de GA4 (antes: siempre "C").

#### FASE-PATCH-D: Infraestructura + Documentación
- `scripts/derive_version_from_changelog.py`: Creado. Deriva VERSION.yaml desde CHANGELOG.md.
- `AGENTS.md`: Test count unificado. Gates documentados: 9 (6 blocking + 3 advisory).
- `docs/technical_debt/hardcodes_audit_2026-04-29.md`: 19 hardcodes H-9→H-27 catalogados con severidad y recomendación.

### Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `scripts/derive_version_from_changelog.py` | Deriva VERSION.yaml desde CHANGELOG.md |
| `docs/technical_debt/hardcodes_audit_2026-04-29.md` | Catálogo de 19 hardcodes como deuda técnica |

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_proposal_generator.py` | BUG-1 (ROI X) + BUG-2 (pain_ratio) + H-1 (web_score) |
| `modules/commercial_documents/v4_diagnostic_generator.py` | H-3/H-4/H-5 (stubs blog/speakable/ga4) |
| `modules/orchestration_v4/two_phase_flow.py` | H-2 (teléfono placeholder) |
| `modules/financial_engine/scenario_calculator.py` | H-6 (Evidence Tier) |
| `scripts/version_consistency_checker.py` | Unicode fix (cp1252) |
| `AGENTS.md` | H-7 (test count) + H-8 (gates count) |
| `VERSION.yaml` | 4.36.0 → 4.37.0 |
| `.opencode/plans/` | Planes PATCH-A/B/C/D + checklist + dependencias |

### Tests

- Sin regresiones. Tests existentes (~2363) pasan.
- v4complete verificado: coherence >= 0.80, gates ready=true.
```

- [ ] CHANGELOG.md tiene entrada `[4.37.0]` con formato correcto
- [ ] Secciones requeridas: Objetivo, Cambios Implementados, Archivos Nuevos, Archivos Modificados, Tests
- [ ] No hay entradas duplicadas

### E5. GUIA_TECNICA.md nota técnica

Agregar sección antes de la última nota:

```markdown
## Notas de Cambios v4.37.0

**Módulos afectados**: `v4_proposal_generator`, `v4_diagnostic_generator`, `two_phase_flow`, `scenario_calculator`, `version_consistency_checker`

**Problema**: Auditoría forense (ContextMv2.md) reveló 2 bugs de credibilidad comercial y 6 hardcodes/stubs que producían datos falsos en la propuesta. version_consistency_checker.py crasheaba en Windows cp1252. VERSION.yaml desincronizado de CHANGELOG.

**Solución**:
- BUG-1/2: Corrección de formato ROI y explicación de pain_ratio en proyección financiera
- H-1→H-6: Eliminación de placeholders y stubs silenciosos; datos ahora provienen de fuentes reales o se marcan explícitamente como no disponibles
- Unicode fix: sys.stdout.reconfigure(encoding="utf-8") siguiendo patrón de log_phase_completion.py
- derive_version_from_changelog.py: Nuevo script para derivar VERSION.yaml desde CHANGELOG

**Backwards compatibility**: Total. Los fixes son incrementales. Templates existentes siguen funcionando. Los stubs que antes retornaban False ahora retornan estado real o marcador textual.

**Deuda técnica documentada**: 19 hardcodes (H-9→H-27) en pricing, escenarios y fallbacks catalogados en docs/technical_debt/ para proyecto futuro de extracción de configuración.

**Tests**: ~2363 tests sin regresiones. v4complete verificado con coherence >= 0.80.
```

- [ ] GUIA_TECNICA.md tiene nota técnica v4.37.0
- [ ] Incluye: módulos afectados, problema, solución, backwards compatibility
- [ ] Menciona deuda técnica documentada

### E6. Validación Final

```bash
# Regenerar SYSTEM_STATUS.md
./venv/Scripts/python.exe scripts/doctor.py --status

# Validación completa
./venv/Scripts/python.exe scripts/run_all_validations.py --quick

# Verificar consistencia final
./venv/Scripts/python.exe scripts/version_consistency_checker.py

# Verificar symlink
ls -la .agent/workflows

# Ver qué archivos cambiaron
git diff --stat
```

- [ ] run_all_validations.py --quick: 4/4
- [ ] version_consistency_checker.py: SINCRONIZADO
- [ ] doctor.py --status sin errores
- [ ] Symlink .agent/workflows → .agents/workflows intacto

### E7. Commit Final

```bash
git add -A
git status
git commit -m "RELEASE v4.37.0: PATCH Forense AmaziliaHotel v2

- BUG-1/2: ROI format + pain_ratio explanation (v4_proposal_generator.py)
- H-3/4/5: Diagnostic stubs replaced with real detection (v4_diagnostic_generator.py)
- H-1: web_score uses audit_result (v4_proposal_generator.py)
- H-2: Phone placeholder removed (two_phase_flow.py)
- H-6: Evidence Tier conditioned on real data (scenario_calculator.py)
- Unicode fix: version_consistency_checker.py (cp1252)
- New: derive_version_from_changelog.py
- Docs: AGENTS.md unified test count + 9 gates
- Technical debt: 19 hardcodes cataloged in docs/technical_debt/
- Version: 4.36.1 → 4.37.0"
```

- [ ] Commit realizado
- [ ] Mensaje describe todos los cambios

---

## Criterios de Completitud (CHECKLIST)

- [ ] VERSION.yaml = 4.37.0, codename actualizado
- [ ] sync_versions.py ejecutado (2 veces: pre y post version bump)
- [ ] CHANGELOG.md entrada [4.37.0] con formato CONTRIBUTING.md
- [ ] GUIA_TECNICA.md nota técnica v4.37.0
- [ ] version_consistency_checker.py: SINCRONIZADO
- [ ] run_all_validations.py --quick: 4/4
- [ ] doctor.py --status sin errores críticos
- [ ] SYSTEM_STATUS.md regenerado
- [ ] Evidencia en evidence/fase-patch-auditoria-v2/ preservada
- [ ] Commit final con mensaje descriptivo

---

## Restricciones

- **NO modificar código fuente** de producción
- **NO ejecutar v4complete**
- **NO modificar ROADMAP.md**
- **NO modificar DOMAIN_PRIMER.md** (no hubo cambios arquitectónicos)
- Usar `--force-skip-docs --skip-reason "no-aplica"` solo si algún check manual no aplica
