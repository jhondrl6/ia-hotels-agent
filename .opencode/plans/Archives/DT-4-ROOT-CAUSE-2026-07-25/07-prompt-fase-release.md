# Prompt de Inicio de Sesión: FASE-RELEASE — v4complete Zi One + Version Bump + Análisis

**Fase**: FASE-RELEASE — v4complete verificación + version bump + análisis post-implementación
**Plan**: DT-4-ROOT-CAUSE-2026-07-25
**Sesión**: Nueva (fresh)
**Iteraciones máx**: 60
**Complejidad**: MEDIA (análisis) + BAJA (docs)
**Ejecución**: **MIXTO** ⚠️ — v4complete delegado, análisis DIRECTO
**⚠️ CONTIENE COMANDO LARGO**: v4complete (timeout 900s, ~5-10 min)
**Depende de**: FASE-0 ✅, FASE-1 ✅, FASE-2 ✅, FASE-3 ✅, FASE-4 ✅
**Bloquea a**: — (final)

---

## Objetivo

Ejecutar v4complete fresco para Zi One Luxury (https://zione.co/) y verificar que los 5 fixes (FIX-PRIORITY-1 a 5) superaron los bugs detectados en CONTEXT-DT-4. Luego ejecutar version bump a v4.65.0 con documentación completa y análisis post-implementación.

---

## Contexto de Fases Anteriores

Las 5 fases implementaron:
- **FASE-0**: Reconciliador post-orchestrator → resuelve BUG-6 + BUG-9 + N2 + N3 + N4
- **FASE-1**: BUG-8 → optimista negativo es WARNING, no BLOCKING
- **FASE-2**: BUG-7 → commercial_gates_report.json + BLOCKED_BY_GATES ampliado
- **FASE-3**: BUG-10 → monthly_report excluido de alignment
- **FASE-4**: N1 → gates coverage renombrados (coverage_no_silent_drop + coverage_failure_rate)

---

## Ejecución

### Paso 1: v4complete Zi One Luxury (DELEGAR — MIXTO)

Lanzar v4complete vía delegate_task (comando largo, ~5-10 min):

```
delegate_task(
    goal="Execute v4complete for Zi One Luxury (https://zione.co/) to verify DT-4 fixes",
    context="""
Project: iah-cli at /mnt/c/Users/Jhond/Github/iah-cli
Command: cd /mnt/c/Users/Jhond/Github/iah-cli && ./venv/Scripts/python.exe main.py v4complete --url https://zione.co/ --output output/clientes
Timeout: 900s
Expected output: ~24 files in output/clientes/v4_complete/
Key evidence files to check exist after completion:
  - output/clientes/v4_complete/zione/v4_audit/pain_ledger_resolved.json (NEW — reconciler output)
  - output/clientes/v4_complete/zione/v4_audit/commercial_gates_report.json (NEW — commercial gates persisted)
  - output/clientes/v4_complete/zione/v4_audit/gate_report_*.json
  - output/clientes/v4_complete/v4_complete_report.json
  - output/clientes/v4_complete/BLOCKED_BY_GATES.md

WARNING: This is a LONG command (~5-10 min). Be patient. Do NOT try to re-run if it times out — just report what files were generated.
""",
    timeout=900,
    notify_on_complete=True,
    toolsets=["terminal"]
)
```

### Paso 2: Análisis post-implementación (DIRECTO — agente principal)

Después de recibir el resultado del v4complete, el agente principal ejecuta el análisis:

#### 2.1 Copiar evidencia

```bash
# Guardar evidencia de la ejecución post-fix
cp output/clientes/v4_complete/v4_complete_report.json \
   /.opencode/plans/Archives/DT-4-ROOT-CAUSE-2026-07-25/evidence/v4complete_report_post_fix.json
cp output/clientes/v4_complete/zione/v4_audit/gate_report_*.json \
   /.opencode/plans/Archives/DT-4-ROOT-CAUSE-2026-07-25/evidence/
```

#### 2.2 Verificar matriz de fixes

Verificar cada fix contra la evidencia en disco:

| Fix | Verificación | Archivo de evidencia | ¿Superado? |
|-----|-------------|---------------------|------------|
| FIX-1 (reconciliador) | pain_ledger_resolved.json existe con ASSET_GENERATED/MAPPED_TO_SERVICE | `pain_ledger_resolved.json` | |
| FIX-1 (coverage gate) | Coverage gate PASS (ya no falso positivo no_whatsapp_visible) | `gate_report_*.json §coverage_no_silent_drop` | |
| FIX-1 (coherence) | whatsapp_verified confidence ≥ 0.9 | `coherence_validation.json` | |
| FIX-2 (BUG-7) | commercial_gates_report.json existe | `commercial_gates_report.json` | |
| FIX-2 (BUG-7 N5) | BLOCKED_BY_GATES.md menciona commercial gates | `BLOCKED_BY_GATES.md` | |
| FIX-3 (BUG-8) | Optimista negativo → WARNING o PASS | `commercial_gates_report.json §CG-SCENARIO-NEGATIVE` | |
| FIX-4 (BUG-10) | monthly_report excluido de alignment counts | `proposal_asset_matrix.json §entries` | |
| FIX-5 (N1) | Gate report usa nuevos nombres | `gate_report_*.json §gate_name` | |

#### 2.3 Completar `09-analisis-post-implementacion.md`

Rellenar la plantilla con:
- Resumen de ejecución (fase, sesión, iteraciones, delegate_task usado)
- Análisis de fase de mayor complejidad (FASE-0)
- delegate_task viability real vs planificado
- Lecciones aprendidas

### Paso 3: Version bump + documentación

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# 1. Bump version: v4.64.0 → v4.65.0
#    Editar VERSION.yaml: version: "4.65.0", release_date: "2026-07-25"

# 2. Sync versions
./venv/Scripts/python.exe scripts/sync_versions.py

# 3. Actualizar CHANGELOG.md (consolidar las 5 fases bajo [4.65.0])
#    Template:
#    ## [4.65.0] — 2026-07-25
#    ### Cambios Implementados (DT-4)
#    - FIX-PRIORITY-1: Post-orchestrator reconciler — unified pain resolution across 3 data sources
#    - FIX-PRIORITY-2: Persist commercial gates report + expanded BLOCKED_BY_GATES.md
#    - FIX-PRIORITY-3: Reinterpret optimistic scenario negative as WARNING not BLOCKING
#    - FIX-PRIORITY-4: Exclude monthly_report from proposal service alignment counts
#    - FIX-PRIORITY-5: Rename duplicate coverage gates (coverage_no_silent_drop / coverage_failure_rate)
#    ### Archivos Modificados
#    - Nuevo: modules/orchestration/post_orchestrator_reconciler.py
#    - modules/asset_generation/v4_asset_orchestrator.py
#    - modules/quality_gates/publication_gates.py
#    - modules/quality_gates/commercial_gate.py
#    - modules/quality_gates/delivery_quality_report.py
#    - modules/quality_gates/coherence_validator.py
#    - modules/asset_generation/proposal_asset_alignment.py
#    - modules/commercial_documents/v4_proposal_generator.py
#    - main.py
#    ### Tests
#    - N tests nuevos (contar con pytest --collect-only)

# 4. Pre-commit check
./venv/Scripts/python.exe scripts/version_consistency_checker.py --verbose

# 5. git tag + commit
git add -A
git commit -m "release: v4.65.0 — DT-4 root cause reconciliation + 5 fixes"
git tag -a v4.65.0 -m "v4.65.0: Post-orchestrator reconciler + 5 bug fixes (DT-4)"
```

---

## Criterios de Completitud

- [ ] v4complete Zi One ejecutado exitosamente
- [ ] `pain_ledger_resolved.json` existe en v4_audit
- [ ] `commercial_gates_report.json` existe en v4_audit
- [ ] `BLOCKED_BY_GATES.md` incluye sección de commercial gates (si aplica)
- [ ] Coverage gate PASS (ya no falso positivo no_whatsapp_visible)
- [ ] Matriz de verificación completada en `09-analisis-post-implementacion.md`
- [ ] VERSION.yaml: 4.65.0
- [ ] CHANGELOG.md: entrada [4.65.0] consolidada
- [ ] Pre-commit: version_consistency_checker.py PASS
- [ ] git tag v4.65.0 creado
- [ ] `pytest --collect-only -q | tail -1` para conteo real de tests
- [ ] README.md test count actualizado

---

## Restricciones

- **NO modificar código** en esta fase — solo verificación + docs
- **NO re-ejecutar v4complete** si ya generó archivos — usar la primera ejecución
- v4complete usa `--output output/clientes` (path con datos reales, consistente con CONTEXT-DT-4)
- El análisis post-implementación es DIRECTO — requiere el agente principal con contexto completo

---

## Post-Ejecución (OBLIGATORIO)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-RELEASE --desc "DT-4_v4complete_Zi_One_version_bump_v4_65_0" --check-manual-docs --force-skip-docs --skip-reason "GUIA_TECNICA_actualizada_manualmente_en_FASE-RELEASE"
```
