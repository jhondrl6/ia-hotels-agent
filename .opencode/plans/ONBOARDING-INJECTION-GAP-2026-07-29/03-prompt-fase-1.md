# FASE-1: Alineación Taxonómica ADRSource↔EvidenceTier + Fix Mensaje Deprecado

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: SUBAGENTE (✅ VIABLE — 2 one-liners, sin imports del proyecto, sin dependencia de FASE-0)
> **Complejidad**: BAJA
> **Plan**: `ONBOARDING-INJECTION-GAP-2026-07-29/01-plan-maestro.md`

## Contexto previo

**FASE-0 completada**: El loader ahora busca por URL normalizada en vez de slug, `onboard` persiste `hotel.url`, y la ventana de frescura es configurable. Quedan 2 hallazgos independientes por resolver:

1. **§10a**: `"user_provided"` (fuente de ADR de máxima confianza) es invisible para `_determine_evidence_tier()`. No bloquea Tier A porque occupancy y channel sí están marcados como `"onboarding"`, pero es una inconsistencia taxonómica.
2. **§10b**: El mensaje de `onboard` al finalizar sugiere ejecutar `audit` (deprecado) en vez de `v4complete`.

## Objetivo de esta fase

Dos one-liners independientes: alinear la taxonomía de fuentes y actualizar el mensaje de next-steps.

### Tareas

- [ ] **T1 — Fix 4**: Agregar `"user_provided"` a `verified_sources` en `_determine_evidence_tier()`
- [ ] **T2 — Fix 5**: Actualizar mensaje de onboard: `audit` → `v4complete`

### Detalle T1 — Fix 4

**Archivo**: `modules/financial_engine/scenario_calculator.py` (línea 493-494)

```python
# ANTES (L493-494):
verified_sources = [s for s in [adr_src, occ_src, ch_src]
                  if s in ('onboarding', 'verified', 'industry_standard_15pct')]

# DESPUÉS:
verified_sources = [s for s in [adr_src, occ_src, ch_src]
                  if s in ('onboarding', 'verified', 'industry_standard_15pct', 'user_provided')]
```

**Justificación**: `ADRSource.USER_PROVIDED = "user_provided"` es el dato de mayor calidad epistémica posible (`epistemic_status="measured"`). Debe ser tratado como fuente verificada. En la práctica, si solo se onboardea ADR (sin occupancy ni channel), tener `user_provided` en verified_sources permite que un solo campo verificado + sin low_quality → Tier A (se necesita len(verified_sources) >= 2, así que ADR solo no basta — se necesitan al menos 2 fuentes verificadas).

### Detalle T2 — Fix 5

**Archivo**: `main.py` (línea 1118)

```python
# ANTES (L1118):
print(f"   2. Ejecuta: python main.py audit --url {url_hint} --input-data {output_path}")

# DESPUÉS:
print(f"   2. Ejecuta: python main.py v4complete --url {url_hint}")
```

También actualizar línea 1113 si aplica (mensaje alternativo cuando `--run-audit` sin `--url`):
```python
# ANTES (L1113):
print(f"   Ejecuta: python main.py audit --url <URL> --input-data {output_path}")

# DESPUÉS:
print(f"   Ejecuta: python main.py v4complete --url <URL>")
```

**Justificación**: `audit` está deprecado (marcado `⚠️ DEPRECADO` en `run_audit_mode`, L1122-1127). El flujo correcto post-onboarding es `v4complete`.

### Restricciones

- ❌ NO modificar la lógica de tiering más allá de agregar el string
- ❌ NO tocar `run_audit_mode()` — solo el mensaje en `run_onboard_mode()`
- ✅ Ambos cambios son ortogonales — si uno falla, el otro no se afecta

### Criterios de completitud

- [ ] `"user_provided"` aparece en la tupla de `verified_sources` (L494)
- [ ] El mensaje de onboard L1118 sugiere `v4complete`, no `audit`
- [ ] El mensaje de onboard L1113 sugiere `v4complete`, no `audit` (si existe)

### delegate_task Prompt (para subagente)

```
GOAL: Apply two independent one-line fixes to iah-cli codebase.

FIX 1 (modules/financial_engine/scenario_calculator.py, line ~493):
Add 'user_provided' to the verified_sources tuple in _determine_evidence_tier().
Current: if s in ('onboarding', 'verified', 'industry_standard_15pct')
New:      if s in ('onboarding', 'verified', 'industry_standard_15pct', 'user_provided')

FIX 2 (main.py, line ~1118):
Change the onboard completion message from suggesting 'audit' (deprecated) to 'v4complete'.
Current: print(f"   2. Ejecuta: python main.py audit --url {url_hint} --input-data {output_path}")
New:      print(f"   2. Ejecuta: python main.py v4complete --url {url_hint}")

Also check if line ~1113 has a similar message and update it too.

CONTEXT: These are independent one-liners. No imports needed. No tests to run. Just patch.
```

### Próxima sesión

**FASE-2**: Integración de `observations.json` como fuente de fallback en `_load_latest_onboarding_data()`. MEDIA complejidad. ❌ NO VIABLE delegate_task (modifica función reescrita en FASE-0).

Carga: `04-prompt-fase-2.md`
