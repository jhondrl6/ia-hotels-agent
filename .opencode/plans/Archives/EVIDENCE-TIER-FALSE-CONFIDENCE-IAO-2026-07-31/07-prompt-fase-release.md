# FASE-RELEASE: Version v4.68.0 + Docs Cascade

> **REGLA**: Una fase = una sesion. No ejecutar multiples fases aqui.
> **Tipo de ejecucion**: **SUBAGENTE** (delegate_task viable: solo YAML/MD, sin imports de modulo)
> **Complejidad**: BAJA
> **Depende de**: FASE-5 completada (v4complete Zi One + control sin onboarding verificados + analisis)
> **Auditoria 2026-07-31**: Plan corregido. CHANGELOG debe incluir hallazgos NP1-NP8 ademas de los 12 originales.

## Contexto previo

FASE-1 a FASE-5 completadas. Todos los fixes implementados y verificados con v4complete real:
- Zi One Luxury: Tier B+ (no A) — fixes #1-#12 + #13-#19 verificados
- hotel_test_001 (control sin onboarding): Tier C (no regresion) — fix #20 (NP8) verificado
- Tests verdes (incluyendo tests pre-existentes actualizados por NP3)
- El plan esta listo para release.

## Objetivo de esta fase

Bump de version a v4.68.0, consolidar CHANGELOG (incluyendo hallazgos NP1-NP8), sincronizar docs (AGENTS.md, GUIA_TECNICA.md, README.md), ejecutar pre-commit, log_phase, y tag.

### Tareas

- [ ] **T1 — Version bump**: Editar VERSION.yaml: `version: "4.68.0"`, codename descriptivo, release_date actual.
- [ ] **T2 — CHANGELOG**: Agregar entrada `[4.68.0]` consolidando cambios de FASE-1 a FASE-5. **NO multi-phase sub-secciones — una entrada unificada.** **Debe listar los 20 hallazgos resueltos** (12 originales + 8 nuevos NP1-NP8).
- [ ] **T3 — Docs cascade**: Actualizar AGENTS.md (header dispatcher), GUIA_TECNICA.md (nueva seccion v4.68.0), README.md (numeros: tests, modulos, gates).
- [ ] **T4 — Pre-commit + sync + tag**: Ejecutar pre-commit, `sync_versions.py`, `log_phase_completion.py --fase RELEASE --desc "Evidence_Tier_False_Confidence_Fix" --tests N --release "4.68.0"`, git tag v4.68.0.

### Restricciones

- **NO modificar codigo de produccion.** RELEASE solo toca YAML/MD.
- **NO usar `--bump` en sync_versions.py.** El script solo acepta `--check`, `--list`, `--validate`, `--rule`. Editar VERSION.yaml manualmente.
- **NO usar `→` (unicode) en codename.** Usar `->`. Crash en Windows CP1252.
- **CHANGELOG entry UNIFICADA** — no sub-secciones por fase.
- **Tag ANTES del commit de REGISTRY.** Annotated tag debe apuntar al ultimo commit de codigo.
- **Verificar README.md numeros post-sync** — `sync_versions.py` no actualiza conteos.
- **CHANGELOG debe mencionar explicitamente los hallazgos NP1-NP8** ademas de los 12 originales.

### Criterios de completitud

- [ ] VERSION.yaml: `4.68.0` con codename ASCII y fecha actual
- [ ] CHANGELOG.md: entrada `[4.68.0]` consolidada con cambios, archivos, y tests
- [ ] CHANGELOG.md: menciona los 8 hallazgos nuevos NP1-NP8 (ademas de los 12 originales)
- [ ] AGENTS.md: header dispatcher actualizado (proxima fase)
- [ ] GUIA_TECNICA.md: nueva seccion v4.68.0
- [ ] README.md: conteos verificados (tests, modulos, gates, skills)
- [ ] pre-commit pasa
- [ ] `sync_versions.py` ejecutado sin errores
- [ ] `log_phase_completion.py` ejecutado
- [ ] git tag `v4.68.0` annotated
- [ ] REGISTRY.md actualizado

### Contenido sugerido para CHANGELOG (entrada [4.68.0])

```markdown
## [4.68.0] - 2026-07-31 — Evidence Tier Honesty + B_PLUS + GA4/GSC Gate

### Hallazgos Resueltos (20 totales: 12 originales + 8 nuevos NP1-NP8)

**Originales (12):**
1. H1: `_determine_evidence_tier()` ahora consulta `ga4_enabled`/`gsc_enabled`
2. H2: `EvidenceTier.A.disclaimer` ahora solo aplica con GA4+GSC real
3. H3: `has_onboarding` dinamico (sin fallback silencioso a False)
4. H4: Propuesta no dice 3 tiers diferentes
5. H5: `main.py:2099` relationship text dinamico
6. H6: `precision_tier` visible en template diagnostic
7. H7: Template Tiers legend incluye B+
8. H8: Nuevo gate `CG-EVIDENCE-TIER-CONSISTENCY` (BLOCKING)
9. H9: MANIFEST.json enriquecido con quality_metadata
10. H10: 3 sistemas precision_tier documentados como deuda (no implementado)
11. H11: H1-FIX ya aplicado (no requiere accion)
12. H12: Service account GCP documentado como OUT OF PLAN (user action)

**Nuevos NP1-NP8 (auditoria 2026-07-31):**
13. NP1: hook_pdf_generator acepta B+ (valid_tiers actualizado)
14. NP2: publication_gates tier_message logica dinamica corregida
15. NP3: tests pre-existentes compatibles con B_PLUS (test_financial_breakdown.py actualizado)
16. NP4: v4_diagnostic_generator default evidence_tier "C" (no "A")
17. NP5: PricingResolutionResult.is_onboarding fallback silencioso eliminado
18. NP6: MANIFEST enrichment en delivery_packager.py (corregido de main.py)
19. NP7: Gate con params per-hotel (NO env vars globales)
20. NP8: Control sin onboarding (hotel_test_001) verifica Tier C sin regresion

### Archivos Modificados (17 archivos)
... (listar)
```

### delegate_task prompt (embebido)

```
GOAL: Execute RELEASE phase for iah-cli v4.68.0 — Evidence Tier False Confidence Fix.

Working directory: /mnt/c/Users/Jhond/Github/iah-cli

CONTEXT:
This is the RELEASE phase of plan EVIDENCE-TIER-FALSE-CONFIDENCE-IAO-2026-07-31 (CORREGIDO tras auditoria 2026-07-31).
FASE-1 through FASE-5 are complete. All code changes, tests, and v4complete verification done (Zi One: Tier B+, control hotel_test_001: Tier C).

The plan targeted 20 hallazgos (12 originales + 8 nuevos NP1-NP8):
- FASE-1: EvidenceTier.B_PLUS added, _determine_evidence_tier() checks ga4_enabled/gsc_enabled, consumers downstream limpios (NP1-NP4)
- FASE-2: has_onboarding dynamic (sin fallback silencioso NP5), proposal disclaimer conditional, precision_tier exposed
- FASE-3: CG-EVIDENCE-TIER-CONSISTENCY gate (BLOCKING, per-hotel params NP7), MANIFEST enriched en delivery_packager.py (NP6)
- FASE-4: Tests for all tier combinations + gate + regression + actualizacion tests pre-existentes (NP3)
- FASE-5: v4complete Zi One Luxury (Tier B+) + control hotel_test_001 (Tier C, NP8) verificados

TASKS (in order):

1. VERSION BUMP:
   - Edit VERSION.yaml: version: "4.68.0", codename: "Evidence Tier Honesty - B_PLUS + GA4/GSC gate + proposal truthfulness"
   - Set release_date to today (2026-07-31)
   - Use ASCII only (no unicode arrows)

2. CHANGELOG:
   - Add [4.68.0] entry under [Unreleased]
   - Consolidate ALL changes into ONE entry (not per-phase sub-sections)
   - Include: Cambios Implementados, Archivos Modificados, Tests
   - **CRITICAL**: Mencionar los 20 hallazgos (12 originales H1-H12 + 8 nuevos NP1-NP8)
   - Key changes to list: EvidenceTier.B_PLUS, _determine_evidence_tier GA4/GSC check, has_onboarding dynamic (NP5), precision_tier visible, CG-EVIDENCE-TIER-CONSISTENCY gate per-hotel (NP7), MANIFEST quality_metadata en delivery_packager.py (NP6), relationship text dynamic, hook_pdf_generator valid_tiers actualizado (NP1), publication_gates tier_message dinamico (NP2), default evidence_tier "C" (NP4), control sin onboarding Tier C verificado (NP8)

3. DOCS CASCADE:
   - AGENTS.md: update header dispatcher (line ~1-10) with plan status
   - GUIA_TECNICA.md: add v4.68.0 section referencing this plan
   - README.md: verify and update counts (tests, modules, gates, skills)

4. VALIDATION + TAG:
   - Run: ./venv/Scripts/python.exe scripts/sync_versions.py
   - Run: ./venv/Scripts/python.exe -m pytest tests/ -x -q (verify tests still pass)
   - Run pre-commit: git add -A && pre-commit run
   - Run log_phase: cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py --fase RELEASE --desc Evidence_Tier_False_Confidence_Fix --tests N --release 4.68.0"
     (Replace N with actual test count)
   - Git tag: git tag -a v4.68.0 -m "v4.68.0: Evidence Tier Honesty - B_PLUS + GA4/GSC gate + proposal truthfulness"
   - Update REGISTRY.md

CRITICAL PITFALLS:
- sync_versions.py does NOT accept --bump flag. Edit VERSION.yaml manually then run with no args.
- Do NOT use unicode arrows (→) in codename — use ASCII (->)
- Tag BEFORE REGISTRY commit: annotated tag must point to last code commit
- README.md counts are NOT auto-updated by sync_versions.py — verify manually
- Use cmd.exe /c with FULL Windows path for log_phase (WSL quoting trap)
- --desc must use underscores (no spaces)
- CHANGELOG entry must be CONSOLIDATED (one section), not per-phase sub-sections
- CHANGELOG must list ALL 20 hallazgos (12 originales + 8 nuevos NP1-NP8)
```

### Verificacion post-RELEASE

```bash
# 1. Version correcta
grep "version:" VERSION.yaml

# 2. CHANGELOG tiene entrada 4.68.0 con los 20 hallazgos
grep -A50 "\[4.68.0\]" CHANGELOG.md | grep -E "H[0-9]+|NP[0-9]+" | head -25

# 3. Tag existe
git tag -l "v4.68.0"

# 4. Tag apunta al commit correcto
git log --oneline v4.68.0 -1

# 5. Tests pasan
./venv/Scripts/python.exe -m pytest tests/ -x -q

# 6. README counts
grep -E "tests|modules|gates|skills" README.md | head -10
```

### Fin del plan

Esta es la ultima fase del plan EVIDENCE-TIER-FALSE-CONFIDENCE-IAO-2026-07-31 (CORREGIDO). Despues de RELEASE:
- El plan se mueve a Archives/
- El contexto se marca como IMPLEMENTADO
- La deuda tecnica documentada (H10: 3 sistemas precision_tier) queda para plan futuro
- Los 20 hallazgos (12 originales + 8 nuevos NP1-NP8) quedan cerrados
