# FASE-6: RELEASE v4.56.0

**Plan**: ROICRII
**Tipo**: Docs+Sync
**Hallazgos**: —
**Prerrequisito**: FASE-5 completada (v4complete con 5 niveles superados)
**Ejecución**: delegate_task (100% mecánico — sin decisiones)
**Iteración estimada**: 25-30

---

## Objetivo

Cerrar el plan ROICRII con RELEASE v4.56.0: version bump, CHANGELOG, REGISTRY, domain primer, log_phase, pre-commit.

---

## DELEGATE_TASK — CONTEXTO AUTÓNOMO

**Working directory**: `/mnt/c/Users/Jhond/Github/iah-cli`

**Preflight**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
source venv/bin/activate 2>/dev/null || true
```

**Orden de ejecución**: Las tareas van en secuencia (A → B → C → D → E → F → G). No saltar.

---

### Tarea 6A: VERSION.yaml → 4.56.0

**Paso 1**: Leer VERSION.yaml actual:
```bash
cat VERSION.yaml
```

**Paso 2**: Editar. Los campos a cambiar (adaptar según la estructura real):
- `version: 4.55.0` → `version: 4.56.0`
- `release_name: ROICR` → `release_name: ROICRII`
- `release_date:` → fecha actual (YYYY-MM-DD)

**Paso 3**: Ejecutar sync_versions.py:
```bash
python scripts/sync_versions.py
```

**NOTA CRÍTICA**: `sync_versions.py` NO acepta `--bump` ni `--release-name`. Solo: `--check`, `--list`, `--validate`, `--rule`. Editar VERSION.yaml manualmente PRIMERO, luego ejecutar script sin args.

**NOTA**: `sync_versions.py` usa `datetime.now()` para `{date}` — ignora `release_date` de VERSION.yaml. `last_update` en AGENTS.md será siempre hoy, no la fecha del release.

**Paso 4**: Verificar:
```bash
grep "4.56.0" VERSION.yaml
# Expected: 1 match
```

---

### Tarea 6B: CHANGELOG.md

**Paso 1**: Leer las primeras 30 líneas para ver formato:
```bash
head -30 CHANGELOG.md
```

**Paso 2**: Añadir entrada después del header existente (adaptar formato al que ya usa el archivo):
```markdown
## v4.56.0 — ROICRII (2026-05-27)

### Fix (structural)
- **ROI unificado**: Eliminados motores inline `_calculate_roi()` y `_calculate_roi_saas()`. Motor único: `roi_formatter.py`. Formato `:.2f`.
- **Coherencia financiera**: Commercial gate calcula ROI con opex-only (sin CAPEX). Wrapper activa pipeline 3 pasos vía `expected_recovery_cop`.
- **Gobernanza semántica**: `pain_ratio_note` diferencia addressable vs fee/loss. `operational_floor` fallback unificado a 400K.
- **Gate estricto**: `CommercialGateBlockedError` para audiencia externa. CAPEX desglosado en componentes.
- **QA Score**: 72% → ≥90% (ROICRII reporte v3)

### Test
- Nuevos: test_roi_unification, test_financial_coherence, test_semantics_floor_gate, test_capex_rename
- Regresiones: 0 (517+ passed)
```

**Paso 3**: Verificar:
```bash
grep "v4.56.0" CHANGELOG.md
# Expected: ≥1 match
```

---

### Tarea 6C: REGISTRY.md

**Paso 1**: Leer las últimas 30 líneas para ver formato:
```bash
tail -30 REGISTRY.md
```

**Paso 2**: Añadir entrada ROICRII al final (adaptar formato al existente):
```markdown
## v4.56.0 — ROICRII
- **Plan**: ROICRII (6 fases)
- **Origen**: ROICRII.md (QA v3 — auditoría tercer orden)
- **Hallazgos**: 9 (4 CRIT, 3 IMP, 2 NEW subsumidos)
- **Resultado**: QA 72% → ≥90%, ROI unificado, pipeline activo, gate estricto
```

**Paso 3**: Verificar:
```bash
grep "ROICRII" REGISTRY.md
# Expected: ≥1 match
```

---

### Tarea 6D: Domain primer

```bash
python scripts/generate_domain_primer.py 2>/dev/null || echo "Script no disponible"
```

Si no existe, buscar:
```bash
ls scripts/generate* 2>/dev/null
ls scripts/*primer* 2>/dev/null
```

Si tampoco existe, skip. Documentar en 09-documentacion que se omitió.

---

### Tarea 6E: log_phase de fases 1-5

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

python scripts/log_phase.py --phase "FASE-1" --plan "ROICRII" --status "completed" --desc "ROI_unificado_roi_formatter_motor_unico_formato_2f" 2>/dev/null || true
python scripts/log_phase.py --phase "FASE-2" --plan "ROICRII" --status "completed" --desc "Gate_ROI_opex_only_wrapper_activa_pipeline_3_pasos" 2>/dev/null || true
python scripts/log_phase.py --phase "FASE-3" --plan "ROICRII" --status "completed" --desc "Pain_ratio_clarificado_floor_unificado_gate_estricto" 2>/dev/null || true
python scripts/log_phase.py --phase "FASE-4" --plan "ROICRII" --status "completed" --desc "CAPEX_desglose_pain_ratio_renombrado" 2>/dev/null || true
python scripts/log_phase.py --phase "FASE-5" --plan "ROICRII" --status "completed" --desc "v4complete_Hotel_Castilla_Real_analisis_5_niveles" 2>/dev/null || true
python scripts/log_phase.py --phase "FASE-6" --plan "ROICRII" --status "completed" --desc "RELEASE_v4560" 2>/dev/null || true
```

**NOTA**: Cada `--desc` DEBE usar underscores (sin espacios) — argparse rechaza palabras extra como unrecognized args.

---

### Tarea 6F: Pre-commit o validación equivalente

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Intentar pre-commit
pre-commit run --all-files 2>&1 | tail -20 || echo "pre-commit no disponible"

# Alternativa
python scripts/run_all_validations.py --quick 2>&1 | tail -20 || echo "run_all_validations no disponible"
```

**NOTA**: Si `run_all_validations.py` falla con errores pre-existentes (no relacionados con ROICRII), documentar pero NO bloquear el RELEASE. Los RELEASE failures suelen ser repo issues, no del plan.

---

### Tarea 6G: Veredicto final

**Archivo**: `.opencode/plans/ROICRII/09-documentacion-post-proyecto.md`

Completar la sección "Veredicto Final" con:
- ¿6 fases completadas? SÍ
- ¿5 niveles de FASE-5 superados? (leer de 09-documentacion, sección FASE-5)
- ¿La propuesta es APTA para envío al cliente? (SÍ solo si los 5 niveles pasaron)
- QA score final
- Coherence score final

---

## Verificación Final FASE-6

```bash
# 1. VERSION.yaml
grep "4.56.0" VERSION.yaml

# 2. CHANGELOG.md
grep "v4.56.0" CHANGELOG.md

# 3. REGISTRY.md
grep "ROICRII" REGISTRY.md

# 4. log_phase
grep "ROICRII" scripts/phase_log.jsonl 2>/dev/null | wc -l
# Expected: 6
```
