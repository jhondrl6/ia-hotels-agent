# FASE-6: E2E-ZIONE — v4complete Zi One + Verification + Post-Implementation Analysis

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: MIXTA — v4complete vía subagente, verificación y análisis vía agente principal
> **Iteraciones máx**: 60
> **⚠️ CONTIENE COMANDO LARGO**: v4complete (5-10 min)
> **Depende de**: FASE-1 ✅, FASE-2 ✅, FASE-3 ✅, FASE-4 ✅, FASE-5 ✅
> **Bloquea a**: FASE-RELEASE

## Contexto de Fases Anteriores

Todas las fases de implementación están completadas:
- **FASE-1**: `pain_ledger_resolved` ahora se inyecta en el assessment → coverage gate recibe datos reconciliados
- **FASE-2**: SitePresence normalizado, adapter canónico, propagado a 3 call sites de CoherenceValidator
- **FASE-3**: `final_coherence_report` como fuente única de score
- **FASE-4**: `AlignmentResult` DTO canónico compartido entre publication gates y delivery report
- **FASE-5**: Gates se ejecutan una sola vez, sin mutaciones al assessment

## Datos Reales para Verificación

Los datos de referencia (pre-fix) están en `output/clientes/v4_complete/zione/v4_audit/`:
- `pain_ledger_resolved.json` — 9 entries, 1 mapped_to_service (no_whatsapp_visible)
- `gate_report_20260727_140459.json` — coverage FAILED, justified=0, uncovered=["no_whatsapp_visible"]
- `coherence_validation.json` — whatsapp_verified.score=0.30 (boost no aplicado)
- `asset_generation_report.json` — whatsapp_button site_verified=true, presence_status=exists
- `commercial_gates_report.json` — CG-ROI-NEGATIVE BLOCKING

## Objetivo

1. Ejecutar v4complete para Zi One Luxury (https://zione.co/)
2. Verificar los 14 criterios de éxito contra el output generado
3. Generar el análisis post-implementación con lecciones aprendidas

### T1: Ejecutar v4complete vía delegate_task [COMANDO LARGO]

Usar `delegate_task` para ejecutar v4complete en background:

```
delegate_task(
    goal="Ejecutar v4complete para Zi One Luxury (https://zione.co/) y verificar que el output se generó correctamente.",

    context="""Project: iah-cli at /mnt/c/Users/Jhond/Github/iah-cli

Run the following command exactly:
  ./venv/Scripts/python.exe main.py v4complete --url https://zione.co/

Timeout: 900 seconds. The command takes 5-10 minutes.

After completion, verify these output files exist:
- output/v4_complete/01_DIAGNOSTICO_*.md
- output/v4_complete/02_PROPUESTA_*.md
- output/v4_complete/zione/v4_audit/gate_report_*.json
- output/v4_complete/zione/v4_audit/coherence_validation.json
- output/v4_complete/zione/v4_audit/coherence_validation_post_gen.json
- output/v4_complete/zione/v4_audit/asset_generation_report.json
- output/v4_complete/zione/v4_audit/pain_ledger_resolved.json
- output/v4_complete/zione/v4_audit/commercial_gates_report.json
- output/v4_complete/zione/v4_audit/delivery_quality_report.json

Return the paths to all generated files and the exit code of v4complete.""",

    timeout=900,
    notify_on_complete=True,
    toolsets=["terminal"]
)
```

### T2: Guardar evidencia + verificar 14 criterios

**2a. Guardar evidencia** (inmediatamente después de que el subagente complete):

```bash
mkdir -p /mnt/c/Users/Jhond/Github/iah-cli/.opencode/plans/DT4-RESIDUAL-FIXES/evidence/FASE-6
cp output/v4_complete/01_DIAGNOSTICO_*.md .opencode/plans/DT4-RESIDUAL-FIXES/evidence/FASE-6/
cp output/v4_complete/02_PROPUESTA_*.md .opencode/plans/DT4-RESIDUAL-FIXES/evidence/FASE-6/
cp output/v4_complete/zione/v4_audit/*.json .opencode/plans/DT4-RESIDUAL-FIXES/evidence/FASE-6/
```

**2b. Verificar 14 criterios** contra el output generado:

Para cada criterio del contexto §14, verificar contra el output generado:

### Verification Matrix

| # | Criterio | Archivo a verificar | Campo/Path esperado | ¿Pre-fix? |
|---|---------|---------------------|---------------------|-----------|
| C1 | pain_ledger_resolved en contrato assessment | Código (ya verificado en FASE-1) | `AssessmentPayload.pain_ledger_resolved` | ❌ No existía |
| C2 | Assessment usado por gates contiene ledger reconciliado | `gate_report_*.json` | `coverage_no_silent_drop.details.justified >= 1` | Era 0 |
| C3 | coverage_no_silent_drop cuenta no_whatsapp_visible como justificado | `gate_report_*.json` | `coverage_no_silent_drop.details.uncovered` NO contiene `no_whatsapp_visible` | Sí contenía |
| C4 | Gate report muestra justified >= 1 y uncovered = [] | `gate_report_*.json` | `coverage_no_silent_drop.passed == true` | Era false |
| C5 | Boost SitePresence ejecutado en CoherenceValidator | `coherence_validation.json` | `whatsapp_verified.score > 0.30` | Era 0.30 |
| C6 | whatsapp_verified.score deja de ser 0.30 cuando site verified | `coherence_validation.json` | `whatsapp_verified.score >= 0.9` o `whatsapp_verified.passed == true` | Era false, score=0.30 |
| C7 | Única normalización dataclass/dict/enum | Código (ya verificado en FASE-2) | `normalize_site_presence()` existe | No existía |
| C8 | Sin reejecuciones redundantes de SitePresence | `grep -rn "SitePresenceChecker" main.py modules/` | ≤2 ocurrencias | 4+ ocurrencias |
| C9 | Publication y delivery alignment reportan mismo contrato | `gate_report_*.json` vs `delivery_quality_report.json` | Ambos muestran mismos totales | 5/7 vs 7/7 |
| C10 | Score final de coherencia único y trazable | `coherence_validation_post_gen.json` | `overall_score` == score en gate_report | Distintos (0.84 vs 0.8424) |
| C11 | Tests de integración existen | `./venv/Scripts/python.exe -m pytest --collect-only -q` | Tests de integración listados | Solo unitarios |
| C12 | Zi One validado post-fixes | Output files existen | Diagnóstico + Propuesta + Assets | Sin docs comerciales |
| C13 | Decisión explícita sobre CG-ROI-NEGATIVE | `commercial_gates_report.json` | Documentar en análisis | BLOCKING |
| C14 | Documentos existen (no eliminados por otro gate) | `output/v4_complete/` | `01_DIAGNOSTICO_*.md` y `02_PROPUESTA_*.md` existen | No existían |

### Script de verificación programática

```python
import json, os, glob

base = "/mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/zione/v4_audit"
results = []

# C2-C4: Coverage gate
gate_files = glob.glob(f"{base}/gate_report_*.json")
if gate_files:
    latest_gate = max(gate_files, key=os.path.getmtime)
    with open(latest_gate) as f:
        gates = json.load(f)
    coverage = next((g for g in gates if g.get("gate_name") == "coverage_no_silent_drop"), None)
    if coverage:
        results.append(("C2", "justified >= 1", coverage.get("details", {}).get("justified", 0) >= 1))
        results.append(("C3", "no_whatsapp_visible not in uncovered", "no_whatsapp_visible" not in coverage.get("details", {}).get("uncovered", [])))
        results.append(("C4", "coverage passed", coverage.get("passed", False)))

# C5-C6: WhatsApp boost
coh_files = glob.glob(f"{base}/coherence_validation.json")
if coh_files:
    with open(coh_files[0]) as f:
        coh = json.load(f)
    whatsapp = next((c for c in coh if c.get("name") == "whatsapp_verified"), None)
    if whatsapp:
        results.append(("C5", "whatsapp score > 0.30", whatsapp.get("score", 0) > 0.30))
        results.append(("C6", "whatsapp passed or score >= 0.9", whatsapp.get("passed", False) or whatsapp.get("score", 0) >= 0.9))

# C9: Alignment consistency
with open(f"{base}/delivery_quality_report.json") as f:
    dq = json.load(f)
pa = dq.get("proposal_asset_gate", {})
results.append(("C9", "alignment totals consistent", pa.get("total", 0) == pa.get("aligned", 0) + pa.get("present_in_production", 0)))

# C10: Coherence score único
coh_post_files = glob.glob(f"{base}/coherence_validation_post_gen.json")
if coh_post_files:
    with open(coh_post_files[0]) as f:
        coh_post = json.load(f)
    results.append(("C10", "post_gen coherence exists", coh_post.get("overall_score", 0) > 0))

# C14: Docs existen
diag = glob.glob("/mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/01_DIAGNOSTICO_*.md")
prop = glob.glob("/mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/02_PROPUESTA_*.md")
results.append(("C14", "docs exist", len(diag) > 0 and len(prop) > 0))

print("\n".join(f"{'✅' if r[2] else '❌'} {r[0]}: {r[1]}" for r in results))
```

### T3: Generar análisis post-implementación

Crear archivo `.opencode/plans/DT4-RESIDUAL-FIXES/08-analisis-post-implementacion.md` con:

### 1. Execution Summary Table

| Fase | Sesión | Iteraciones | Status | delegate_task |
|------|--------|-------------|--------|---------------|
| FASE-1 | — | — | ✅/❌ | No (DIRECTA) |
| FASE-2 | — | — | ✅/❌ | No (DIRECTA) |
| FASE-3 | — | — | ✅/❌ | No (DIRECTA) |
| FASE-4 | — | — | ✅/❌ | No (DIRECTA) |
| FASE-5 | — | — | ✅/❌ | No (DIRECTA) |
| FASE-6 | — | — | ✅/❌ | Sí (v4complete subagente) |
| RELEASE | — | — | ✅/❌ | Sí (SUBAGENTE) |

### 2. Findings Verification Matrix

Completar con los resultados del script de verificación (✅/❌ por criterio).

### 3. delegate_task Viability Assessment

| Fase | ¿Viable? | ¿Usado? | Outcome |
|------|---------|---------|---------|
| FASE-1 | ❌ WSL venv | No | DIRECTA — N iteraciones |
| FASE-2 | ❌ Decisión cross-module | No | DIRECTA — N iteraciones |
| FASE-3 | ❌ WSL venv | No | DIRECTA — N iteraciones |
| FASE-4 | ❌ WSL venv | No | DIRECTA — N iteraciones |
| FASE-5 | ❌ WSL venv | No | DIRECTA — N iteraciones |
| FASE-6 | ✅ v4complete | Sí | Subagente — N iteraciones |
| RELEASE | ✅ YAML/MD only | Sí | Subagente — N iteraciones |

### 4. Lessons Learned

Documentar:
- Qué funcionó bien del plan
- Qué no funcionó (desviaciones del plan original)
- Problemas encontrados en cada fase y cómo se resolvieron
- Lecciones para futuros planes similares
- Si CG-ROI-NEGATIVE sigue bloqueando y qué implica para Zi One

### 5. Risk Table

| Riesgo | Probabilidad | Impacto | Mitigación | ¿Ocurrió? |
|--------|-------------|---------|------------|-----------|
| Regresión en consumers de AssessmentPayload | Media | Alto | Tests exhaustivos | — |
| Shape resolution incorrecto en adapter | Alta | Medio | 5 tests de cobertura | — |
| Score drift pre/post coherence | Baja | Medio | final_coherence_report | — |
| CG-ROI-NEGATIVE sigue bloqueando | Alta | Alto | Documentar, no relajar | — |
| v4complete timeout subagente | Media | Alto | timeout=900, notify_on_complete | — |

## Criterios de Completitud

- [ ] v4complete ejecutado exitosamente para https://zione.co/
- [ ] Evidencia copiada a `evidence/FASE-6/`
- [ ] Verification matrix completada (✅/❌ para C2-C14)
- [ ] `08-analisis-post-implementacion.md` creado con todas las secciones
- [ ] Lecciones aprendidas documentadas
- [ ] `log_phase_completion.py` ejecutado

## Restricciones

- **NO modificar código fuente** — solo verificación y análisis
- **NO relajar CG-ROI-NEGATIVE** — documentar la decisión comercial pendiente
- Máximo 60 iteraciones
- Si v4complete timeout: verificar archivos generados, si existen continuar con verificación

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-6 \
    --desc "E2E-ZIONE: v4complete Zi One Luxury + verification 14 criterios + post-implementation analysis" \
    --archivos-nuevos ".opencode/plans/DT4-RESIDUAL-FIXES/08-analisis-post-implementacion.md" \
    --tests "N" \
    --check-manual-docs
```

## Próxima Sesión

FASE-RELEASE-v4.66.0 — Documentación oficial, version bump, CHANGELOG, GUIA_TECNICA, validaciones finales
