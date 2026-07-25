# FASE-RELEASE — v4.63.2 (Delivery Contract Residual Fixes)

> **Plan**: DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24
> **Fase**: RELEASE (fase final)
> **Versión objetivo**: v4.63.2
> **Ejecución**: SUBAGENTE (delegate_task — solo YAML/MD + scripts)
> **Dependencias**: FASE-A, B, C, D, E, F completadas
> **Próxima fase**: Ninguna (cierre del plan)

---

## Contexto

Todas las fases de código (A-D), tests (E) y verificación E2E (F) están completas.
Esta fase formaliza el release: version bump, CHANGELOG, docs cascade, pre-commit.

**Cambios de la versión v4.63.2**:
- P-01: README Overview conteo post-manifest (recalcular después de Pass 3)
- P-02: Exclusión mutua advisory assets en secciones state-based
- P-03: delivery_quality_report usa coherence score post-generación
- P-04: proposal_asset_matrix path alignment con DeliveryContext
- P-05: G9 proposal_asset_alignment gate implementado (o eliminado con deuda documentada)
- P-06: proposal_asset_matrix.json empaquetado en ZIP de entrega
- P-07: Comparación string-vs-enum unificada a enum en delivery_packager.py
- 7+ tests nuevos de contrato en test_delivery_contract.py

---

## Tareas

### Tarea R-1: Version bump en VERSION.yaml

**Archivo**: `VERSION.yaml`

```yaml
version: "4.63.2"
codename: "Delivery-Contract-Residual"
release_date: "2026-07-24"  # o fecha actual
```

**NOTA**: Si el codename contiene caracteres Unicode (→, em-dash), reemplazar
con ASCII (->) para evitar UnicodeEncodeError en sync_versions.py (CP1252).

### Tarea R-2: CHANGELOG.md consolidado

**Archivo**: `CHANGELOG.md`

Agregar entrada bajo `## [4.63.2]`:

```markdown
## [4.63.2] - 2026-07-24

### Cambios Implementados (DT-2: Delivery Contract Residual Fixes)
- P-01: README Overview ahora muestra conteo de archivos y tamaño que coinciden con MANIFEST.json
- P-02: Assets advisory ya no aparecen simultáneamente en secciones state-based y Advisory Guides
- P-03: delivery_quality_report refleja score de coherencia post-generación (con fallback a pre-gen)
- P-04: proposal_asset_matrix path alineado con DeliveryContext
- P-05: G9 proposal_asset_alignment gate evaluado realmente (no default hardcodeado)
- P-06: proposal_asset_matrix.json ahora se empaqueta en el ZIP de entrega
- P-07: Comparación string-vs-enum unificada a enum (DeliveryAssetState.DELIVERED)

### Archivos Modificados
- modules/delivery/delivery_packager.py (P-01, P-07, P-02, P-06)
- modules/delivery/delivery_context.py (P-02)
- modules/quality_gates/delivery_quality_report.py (P-03, P-05)
- modules/asset_generation/proposal_asset_alignment.py (P-04)
- modules/commercial_documents/v4_proposal_generator.py (P-04, P-06)
- tests/delivery/test_delivery_contract.py (7+ tests nuevos)

### Tests
- 28 tests existentes + 7+ nuevos = 35+ tests de contrato
- v4complete Zi One Luxury: verificación E2E de 7 fixes (S-1 a S-9)
```

**Si ya existen entradas parciales de DT-2 bajo [4.63.2]**: consolidar en una
sola entrada unificada (no agregar nueva encima).

### Tarea R-3: Docs cascade + sync_versions + pre-commit

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# 1. Actualizar headers de versión en docs
./venv/Scripts/python.exe scripts/sync_versions.py

# 2. Actualizar GUIA_TECNICA.md con nota de v4.63.2
#    (agregar entrada breve en la sección de cambios recientes)

# 3. Pre-commit validation
git add -A
git commit -m "release: v4.63.2 Delivery-Contract-Residual

DT-2: 7 fixes residuales post-DT-1
- P-01: README conteo post-manifest
- P-02: Advisory exclusión mutua
- P-03: Post-gen coherence score
- P-04: Matrix path alignment
- P-05: G9 gate implemented
- P-06: Matrix empaquetado en ZIP
- P-07: Enum comparison unified

7+ tests nuevos, 35+ total contract tests
v4complete Zi One Luxury: S-1 to S-9 verified"

# 4. Git tag (ANTES del REGISTRY bookkeeping commit)
git tag -a v4.63.2 -m "v4.63.2 Delivery-Contract-Residual"
```

**NOTA sync_versions.py**: Solo acepta `--check`, `--list`, `--validate`, `--rule`.
No acepta `--bump` ni `--release-name`. Editar VERSION.yaml manualmente, luego
correr `sync_versions.py` sin args para propagar.

**NOTA log_phase quoting**: `cmd.exe /c` con paths relativos falla en WSL.
Usar path completo de Windows: `cmd.exe /c "C:\Users\Jhond\...\venv\Scripts\python.exe ..."`
y `--desc` con underscores (no espacios).

---

## Criterios de Completitud

- [ ] VERSION.yaml actualizado a 4.63.2
- [ ] CHANGELOG.md tiene entrada consolidada [4.63.2]
- [ ] sync_versions.py ejecutado sin errores
- [ ] GUIA_TECNICA.md actualizado con nota de v4.63.2
- [ ] Pre-commit hook pasa (version_consistency + sync_versions)
- [ ] Git tag v4.63.2 creado (annotated, apunta al commit de código)
- [ ] log_phase_completion.py ejecutado para FASE-RELEASE-DT2

---

## Post-Ejecución

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-RELEASE-DT2 --desc "v4.63.2_Delivery_Contract_Residual_released"
```

---

## Prompt para delegate_task (SUBAGENTE)

```
Goal: Execute RELEASE phase for iah-cli v4.63.2 (Delivery Contract Residual Fixes)

Context:
- Repo path: /mnt/c/Users/Jhond/Github/iah-cli
- Current version: 4.63.1
- Target version: 4.63.2
- Codename: "Delivery-Contract-Residual" (ASCII only, no Unicode arrows)

Steps:
1. Edit VERSION.yaml: change version to "4.63.2", codename to "Delivery-Contract-Residual",
   release_date to today's date (YYYY-MM-DD)
2. Read CHANGELOG.md — check if [4.63.2] entry already exists (from per-phase commits).
   If yes: consolidate all sub-sections into one unified entry.
   If no: add new [4.63.2] entry with the 7 fixes (P-01 to P-07), files modified, and tests.
3. Run: ./venv/Scripts/python.exe scripts/sync_versions.py
   (This updates version headers in AGENTS.md, .cursorrules, docs/GUIA_TECNICA.md,
   docs/contributing/REGISTRY.md. WARN lines are expected and harmless.)
4. Update GUIA_TECNICA.md: add a brief note under the latest version section
   documenting the 7 fixes from DT-2.
5. git add -A
6. git commit -m "release: v4.63.2 Delivery-Contract-Residual"
7. git tag -a v4.63.2 -m "v4.63.2 Delivery-Contract-Residual"
8. Run: ./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-RELEASE-DT2 --desc "v4.63.2_released"

IMPORTANT:
- sync_versions.py does NOT accept --bump or --release-name. Edit VERSION.yaml manually first.
- If codename has Unicode chars (arrows, em-dashes), replace with ASCII to avoid cp1252 crash.
- Pre-commit hook runs version_consistency_checker.py (BLOCKS) and sync_versions.py --check (advisory).
- sync_versions.py --check WARN lines do NOT block the commit. Don't re-run the commit for WARNs.
- Git tag must be created BEFORE any REGISTRY bookkeeping commit.
```

---

## Cierre del Plan

Al completar FASE-RELEASE, el plan DT-2 está cerrado. Actualizar:

1. **Plan README.md**: marcar todas las fases como ✅ COMPLETADA
2. **09-checklist-implementacion.md**: marcar todos los items como `[x]`
3. **10-analisis-post-implementacion.md**: completar lecciones aprendidas (si no se hizo en FASE-F)

**Plan completado**: 7 fases × 7 sesiones × 7 fixes → v4.63.2
