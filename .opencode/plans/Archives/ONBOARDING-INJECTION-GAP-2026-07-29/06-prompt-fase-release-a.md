# FASE-RELEASE-A: v4complete Zi One Luxury + Verificacion de 8 Hallazgos

> **REGLA**: Una fase = una sesion. No ejecutar multiples fases aqui.
> **Tipo de ejecucion**: MIXTO ⚠️ — v4complete → SUBAGENTE (timeout=900s), verificacion → DIRECTO
> **Complejidad**: MEDIA
> **R3**: 2 tareas + 1 comando largo (v4complete) ✅ dentro del limite
> **Plan**: `ONBOARDING-INJECTION-GAP-2026-07-29/01-plan-maestro.md`

## Contexto previo

**FASE-0-A**: `_load_latest_onboarding_data()` reescrita con matching por URL + `_normalize_url()` + frescura configurable.
**FASE-0-B**: `onboard` persiste `hotel.url`, `v4complete` pasa `output_dir`, template tiene `url`.
**FASE-1**: `user_provided` en verified_sources + mensaje onboard actualizado.
**FASE-2**: Fallback a `observations.json` + `_observation_to_onboarding_format()`.
**FASE-3**: Tests de regresion completos.

El pipeline de inyeccion esta completo. Esta fase verifica E2E con datos reales.

## Objetivo de esta fase

Ejecutar v4complete para Zi One Luxury (https://zione.co/) y verificar los 8 hallazgos contra output real.

### Tareas

- [ ] **T1**: Ejecutar v4complete para Zi One Luxury (SUBAGENTE — timeout=900s)
- [ ] **T2**: Verificar inyeccion de datos Tier A contra matriz de 8 hallazgos (DIRECTO)

---

### T1 — v4complete Zi One Luxury (SUBAGENTE)

**Comando exacto** (WSL path, venv Windows):
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli && ./venv/Scripts/python.exe main.py v4complete --url https://zione.co/ --force-new
```

**Timeout**: 900s (v4complete tipicamente 5-10 minutos de wall-clock).

**IMPORTANTE**: El proyecto tiene venv Windows (`venv/Scripts/python.exe`). El subagente se ejecuta en WSL Linux.

**Verificacion PRE-v4complete** (leccion DT4 #3 — ejecutar ANTES de lanzar v4complete):
```bash
# Verificar que el loader puede encontrar datos para Zi One
grep -c "def _load_latest_onboarding_data" main.py
# Debe mostrar 1

# Verificar que el YAML de onboarding existe (si se hizo onboard previamente)
ls -la output/clientes/*_onboarding.yaml 2>/dev/null || echo "No YAML files yet"

# Verificar que observations.json tiene website para Zi One
grep -A1 "Zi One Luxury" data/hotel_observations/observations.json | grep website || echo "WARNING: Zi One no tiene website en observations.json"
```

**Delegate task prompt** (autocontenido para subagente):

```
GOAL: Execute v4complete for Zi One Luxury hotel and capture output evidence.

STEPS:
1. Run this exact command (Windows venv via WSL):
   cd /mnt/c/Users/Jhond/Github/iah-cli && ./venv/Scripts/python.exe main.py v4complete --url https://zione.co/ --force-new

   Use terminal with background=true, timeout=900, notify_on_complete=true.

2. After completion, capture evidence:
   - List files in output/v4_complete/ modified in the last 10 minutes: ls -lt output/v4_complete/ | head -20
   - Check if 01_DIAGNOSTICO_*.md EXISTS (not just "was generated"): ls -la output/v4_complete/01_DIAGNOSTICO_*.md
   - Check if 02_PROPUESTA_COMERCIAL_*.md EXISTS: ls -la output/v4_complete/02_PROPUESTA_COMERCIAL_*.md
   - Read financial_scenarios.json to verify rooms, adr, occupancy, direct_channel
   - Read the first 50 lines of the latest 01_DIAGNOSTICO_*.md (if it exists)
   - Check for evidence_tier in the diagnostic

3. Report:
   - Whether onboarding data was loaded (look for "Onboarding data loaded" in stdout)
   - rooms value (should be 34, not 10)
   - adr_cop value (should be ~290000, not 420000)
   - occupancy_rate (should be ~0.784, not 0.512)
   - direct_channel_percentage (should be ~0.4, not 0.2)
   - evidence_tier (should be A, not B)
   - Paths to generated files

CRITICAL: Use the Windows Python executable at ./venv/Scripts/python.exe, not system python.
CRITICAL: Verify file existence with ls -la, do NOT infer from logs (DT4 lesson #6).
```

---

### T2 — Verificacion de Hallazgos (DIRECTO)

**Matriz de verificacion de 8 hallazgos**:

| # | Hallazgo | Fix | Que verificar en output | PASS/FAIL |
|---|----------|-----|------------------------|-----------|
| B1 | Slug mismatch | CAMBIO A+C | v4complete log muestra "Onboarding data loaded: N campos confirmados" | |
| B2 | Frescura 24h | Fix 3 | Datos con fecha 2026-07-23 (5 dias) NO rechazados | |
| N3 | hotel_url ignorado | CAMBIO C | `_load_latest_onboarding_data` usa `hotel_url` para matching | |
| N4 | output_dir hardcodeado | CAMBIO B | Loader recibe `output_dir` desde `args.output` | |
| N5 | Sin identity resolver | CAMBIO A+C | URL es clave canonica — matching funciona sin importar el nombre | |
| S10a | user_provided invisible | Fix 4 | `adr_source: "user_provided"` → tier A | |
| S10b | audit deprecado | Fix 5 | Mensaje onboard sugiere `v4complete` en vez de `audit` | |
| S10c | observations.json | Fix 6 | Si YAML no existe, fallback a observations.json funciona | |

**Procedimiento de verificacion**:

```bash
# B1 + B2 + N3 + N4 + N5 (paquete FASE-0):
grep "Onboarding data loaded" <stdout_del_subagente>
grep -o '"rooms": [0-9]*' output/v4_complete/zione/v4_audit/financial_scenarios_*.json | tail -1
grep -o '"adr_cop": [0-9]*' output/v4_complete/zione/v4_audit/financial_scenarios_*.json | tail -1
grep -o '"occupancy_rate": [0-9.]*' output/v4_complete/zione/v4_audit/financial_scenarios_*.json | tail -1

# S10a (FASE-1):
grep "evidence_tier\|financial_evidence_tier" output/v4_complete/01_DIAGNOSTICO_*.md | head -5

# S10b (FASE-1):
./venv/Scripts/python.exe main.py onboard --url https://zione.co/ --hotel-name "Zi One Luxury" 2>&1 | grep "v4complete"
```

**Criterios de exito**:
- rooms=34 (no 10)
- adr_cop=290000 (no 420000)
- occupancy_rate=0.784 (no 0.512)
- evidence_tier="A" (no "B")

### Restricciones

- ❌ NO ejecutar version bump ni CHANGELOG — eso es FASE-RELEASE-B
- ✅ Si v4complete falla o timeout, documentar en el analisis como riesgo
- ✅ Verificar EXISTENCIA de archivos con `ls -la`, no inferir de logs (DT4 lesson #6)

### Criterios de completitud

- [ ] v4complete Zi One Luxury ejecutado y output capturado
- [ ] rooms=34, adr_cop=290000, occupancy_rate=0.784 en financial_scenarios.json
- [ ] evidence_tier="A" en diagnostico
- [ ] Matriz de 8 hallazgos verificada (PASS/FAIL documentado para cada uno)

### Proxima sesion

**FASE-RELEASE-B**: Version bump v4.67.0 + CHANGELOG + AGENTS.md + GUIA_TECNICA.md. 3 tareas. MEDIA complejidad.

Carga: `07-prompt-fase-release-b.md`
