# CONTEXT: DT-4 Residual Fixes — Post-Release v4.65.0

> **Origen**: FASE-RELEASE DT-4-ROOT-CAUSE-2026-07-25 (completada 2026-07-27)
> **Versión actual**: v4.65.0 (tagged, pushed)
> **Objetivo**: Corregir 2 hallazgos residuales que impiden la generación de documentos comerciales
> **Hotel de prueba**: Zi One Luxury (https://zione.co/)
> **Sesión**: NUEVA (fresh) — NO continuar en la sesión del release

---

## Problema

El v4complete para Zi One Luxury ejecutó exitosamente (exit 0, 73 archivos), pero
**los documentos comerciales (01_DIAGNOSTICO, 02_PROPUESTA) NO se generaron**
porque el coverage gate bloqueó la publicación y los eliminó.

Causa raíz: el reconciliador post-orchestrator (FASE-0) funciona correctamente y
marca `no_whatsapp_visible` como `MAPPED_TO_SERVICE` (el botón de WhatsApp ya existe
en el sitio), pero el coverage gate **no reconoce `MAPPED_TO_SERVICE` como status
justificado** — solo reconoce `ASSET_GENERATED`.

---

## Hallazgos a Corregir

### DT4-R1 (CRÍTICO — Bloquea delivery)

**Archivo**: `modules/quality_gates/publication_gates.py`
**Ubicación**: Constante `_JUSTIFIED_STATUSES` (buscar con grep)
**Problema**: `MAPPED_TO_SERVICE` no está en la lista de status justificados
**Fix**: Agregar `"MAPPED_TO_SERVICE"` a `_JUSTIFIED_STATUSES`

**Ejemplo del cambio esperado**:
```python
# ANTES (aproximadamente línea ~1186):
_JUSTIFIED_STATUSES = {"ASSET_GENERATED"}

# DESPUÉS:
_JUSTIFIED_STATUSES = {"ASSET_GENERATED", "MAPPED_TO_SERVICE"}
```

**Verificación esperada post-fix**:
- v4complete Zi One: coverage_no_silent_drop debe pasar de FAIL a PASS
- `gate_report_*.json` → `coverage_no_silent_drop.status = "PASSED"`
- `v4_documentos/` debe existir con 01_DIAGNOSTICO y 02_PROPUESTA
- Tests existentes deben seguir PASS (sin regresiones)

---

### DT4-R2 (MEDIO — No bloquea delivery pero reduce calidad)

**Archivo**: `modules/quality_gates/coherence_validator.py`
**Ubicación**: Método `_check_whatsapp_verified()` (FASE-0 T4)
**Problema**: El boost de confidence vía `site_presence_report` no se activó.
Score quedó en 0.30 (debajo del threshold 0.9).
**Causa probable**: El parámetro `site_presence_report` no está siendo pasado
desde `v4_asset_orchestrator.py` al coherence_validator.

**Diagnóstico**:
```bash
# Verificar si el orchestrator pasa site_presence_report al validator
grep -n "coherence_validator\|site_presence_report\|_check_whatsapp_verified" \
  modules/asset_generation/v4_asset_orchestrator.py

# Verificar el signature actual del método
grep -n "def _check_whatsapp_verified" \
  modules/quality_gates/coherence_validator.py
```

**Fix esperado**: Cablear `site_presence_report` desde el orchestrator al
coherence_validator. El código del boost ya existe en `_check_whatsapp_verified()`
(acepta `site_presence_report` como parámetro opcional), solo falta pasar el dato.

**Verificación esperada post-fix**:
- `coherence_validation.json` → `whatsapp_verified.score ≥ 0.9`

---

## Evidencia en Disco

Todos los archivos de la ejecución fallida están preservados:

```
.opencode/plans/DT-4-ROOT-CAUSE-2026-07-25/evidence/
├── BLOCKED_BY_GATES.md           ← Confirma: coverage_no_silent_drop FAIL
├── coherence_validation.json     ← whatsapp_verified: score=0.30
├── commercial_gates_report.json  ← CG-ROI-NEGATIVE BLOCKING
├── delivery_quality_report.json  ← G7 coverage_failure_rate PASS, G9 FAIL
├── gate_report_20260727_140459.json ← coverage_no_silent_drop: FAILED
├── pain_ledger_resolved.json     ← no_whatsapp_visible: MAPPED_TO_SERVICE
├── proposal_asset_matrix.json    ← 7 entries, sin monthly_report
└── v4complete_report_post_fix.json
```

También disponibles en el output original:
```
output/clientes/v4_complete/zione/v4_audit/
├── pain_ledger_resolved.json     ← 9 entries (8 ASSET_GENERATED + 1 MAPPED_TO_SERVICE)
├── commercial_gates_report.json
├── gate_report_20260727_140459.json
├── coherence_validation.json
├── delivery_quality_report.json
├── proposal_asset_matrix.json
└── asset_generation_report.json
```

---

## Plan de Ejecución (2 pasos)

### Paso 1: Fix DT4-R1 — coverage gate

1. `grep -n "_JUSTIFIED_STATUSES" modules/quality_gates/publication_gates.py`
2. Agregar `"MAPPED_TO_SERVICE"` al set
3. Verificar syntax: `python -m py_compile modules/quality_gates/publication_gates.py`
4. Correr tests del módulo:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   ./venv/Scripts/python.exe -m pytest tests/quality_gates/test_coverage_gate.py -v
   ```
5. Commit con mensaje descriptivo

### Paso 2: Re-ejecutar v4complete para verificar

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete --url https://zione.co/ --output output/clientes
```

Verificar post-ejecución:
- [ ] `coverage_no_silent_drop` = PASSED en `gate_report_*.json`
- [ ] `v4_documentos/01_DIAGNOSTICO*` existe
- [ ] `v4_documentos/02_PROPUESTA*` existe
- [ ] `BLOCKED_BY_GATES.md` NO contiene coverage_no_silent_drop (o está vacío si no hay otros blockers)

### Paso 3 (opcional): Fix DT4-R2 si hay tiempo

Verificar y cablear `site_presence_report` en el coherence_validator.

---

## Comandos Útiles

```bash
# Working directory
cd /mnt/c/Users/Jhond/Github/iah-cli

# Python (Windows venv desde WSL)
./venv/Scripts/python.exe ...

# Tests
./venv/Scripts/python.exe -m pytest tests/quality_gates/ -q
./venv/Scripts/python.exe -m pytest --collect-only -q | tail -1

# v4complete
./venv/Scripts/python.exe main.py v4complete --url https://zione.co/ --output output/clientes

# Git
git log --oneline -5
git tag -l 'v4.65*'
```

---

## Restricciones

- NO modificar `PAIN_SOLUTION_MAP` ni `scenario_calculator.py`
- NO hacer version bump (ya estamos en v4.65.0)
- El fix es mínimo: 1 línea en `_JUSTIFIED_STATUSES`
- Tests existentes deben seguir PASS
- Si el fix de cobertura funciona pero CG-ROI-NEGATIVE sigue bloqueando,
  eso es ESPERADO (es un commercial gate legítimo para Zi One)
