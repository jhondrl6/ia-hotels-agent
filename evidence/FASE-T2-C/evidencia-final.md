# Evidencia Final — FASE-T2-C

**Commit**: `45335f6`
**Fecha**: 2026-09-10
**Plan**: TRIBUNAL-OFFLINE-2026-09-09
**Residuos cerrados**: S-E2 (NameError latente + código muerto), S9 (INVALID_MAPPINGS + fósil V3)

---

## Resumen de cambios

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| `main.py` | fix (S-E2) | Hoist de `site_presence_report = site_presence_snapshot` fuera del bloque `if generate_proposal:` — elimina NameError latente cuando `generate_proposal=False` |
| `modules/commercial_documents/v4_proposal_generator.py` | fix (S-E2) | 3 bloques `presence_lookup` corregidos: `hasattr(site_presence_report, 'results')` (siempre False contra dict) → cascade `isinstance(dict)` + `hasattr(dataclass)` que maneja ambos formatos |
| `modules/asset_generation/v4_asset_orchestrator.py` | cleanup (S-E2) | Import + instanciación de `SitePresenceChecker` retirados — `self.site_checker` nunca se llamaba |
| `tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py` | test nuevo | 7 tests: 5 de presencia canónica (dict/None/empty) + 2 de verificación del hoist en `main.py` |

---

## Diff de código

### `main.py` — Hoist de `site_presence_report`

```diff
+    # FASE-T2-C (S-E2): hoisted outside `if generate_proposal` — consumers at
+    # FASE 4.5 and delivery_quality_report need it regardless of proposal regime.
+    site_presence_report = site_presence_snapshot
+
     # PIPELINE-FIX: Initialize pain_ledger for assessment scope
     pain_ledger_entries = []
     pain_ledger_resolved_entries = None
     ...
     if generate_proposal:
         ...
-        # FASE-2 (DT4-R2): SitePresenceSnapshot computed upfront — reuse it.
-        site_presence_report = site_presence_snapshot
-
         # RC1 (FASE-B): opportunity_scores del pipeline
```

**Por qué**: `site_presence_report` se asignaba SOLO dentro de `if generate_proposal:` pero se consumía en FASE 4.5 (`builder.with_site_presence()`) y `delivery_quality_report.generate()` — ambos fuera del bloque. Con `generate_proposal=False` → `NameError` enmascarado por `except Exception` amplio.

### `v4_proposal_generator.py` — Fix de `presence_lookup` (×3 bloques)

```diff
         presence_lookup = {}
-        if site_presence_report and hasattr(site_presence_report, 'results'):
-            for asset_type, result in site_presence_report.results.items():
+        if site_presence_report:
+            if isinstance(site_presence_report, dict):
+                _results = site_presence_report.get("results", {})
+            elif hasattr(site_presence_report, "results"):
+                _results = getattr(site_presence_report, "results", {})
+            else:
+                _results = {}
+            for asset_type, result in _results.items():
+                status = result.get("status", "") if isinstance(result, dict) else getattr(result, "status", "")
                 presence_lookup[asset_type] = {
-                    'present_in_production': is_present_in_production(result.status),
+                    'present_in_production': is_present_in_production(status),
                     'presence_verified': True,
                 }
```

**Por qué**: `normalize_site_presence()` retorna un **dict** con clave `"results"`, no un objeto con atributo `.results`. El guard `hasattr(site_presence_report, 'results')` era siempre `False` contra dicts → `presence_lookup` siempre vacío → las tablas de servicios nunca mostraban "Presente en sitio". El fix maneja ambos formatos (dict canónico + dataclass `SitePresenceReport` que algunos tests pasan directo).

### `v4_asset_orchestrator.py` — Retiro de código muerto

```diff
-from .site_presence_checker import SitePresenceChecker  # FASE-CAUSAL-01
 ...
-        self.site_checker = SitePresenceChecker()  # FASE-CAUSAL-01
```

**Por qué**: `self.site_checker` se instanciaba pero nunca se llamaba en ningún método de `V4AssetOrchestrator`. Confirmado con `grep self.site_checker` → solo 1 hit (la asignación).

---

## S9 — Cierre sin cambios de código

| Item | Evidencia |
|------|-----------|
| Fósil V3 (`ASSET_TO_PAIN_ID["monthly_report"] = "no_faq_schema"`) | Solo existe como docstring en `service_identity.py:10`. `grep` confirma 0 hits en código vivo. FASE-A ya derivó `ASSET_TO_PAIN_ID` del canónico (`SERVICE_IDENTITIES`). |
| Test de contrato `INVALID_MAPPINGS` | `test_invalid_mappings_valida_contra_capa1` en `test_service_identity_registry.py:672` ya verifica: keys ⊆ `PAIN_SOLUTION_MAP`, values ⊆ `ASSET_CATALOG`. 4 tests adicionales en `TestInvalidMappingsComplete`. Todos verdes. |

---

## Métricas

| Métrica | Pre | Post | Delta |
|---------|-----|------|-------|
| Tests colectados | 3,983 | 3,990 | +7 |
| Tests tribunal acumulados | 39 | 46 | +7 |
| Módulos afectados (no-regresión) | — | 997 passed | 0 failed |
| `run_all_validations.py --quick` | — | 8/8 PASS | — |
| Pre-commit hooks | — | 5/5 PASS | — |

---

## Criterios de aceptación

| AC | Criterio | Estado | Artefacto |
|----|----------|--------|-----------|
| AC15 | S-E2: `generate_proposal=False` sin NameError | ✅ | `test_site_presence_snapshot_initialized_before_proposal_gate` |
| AC16 | S9: `INVALID_MAPPINGS` pasa contrato | ✅ | `test_invalid_mappings_valida_contra_capa1` (preexistente, verde) |
| NR1 | `passed_post = passed_pre + tests nuevos` | ✅ | 3983 + 7 = 3990 |
| NR3 | `run_all_validations.py --quick` TOTAL PASS | ✅ | 8/8 |
| NR4 | No reimplementa gates | ✅ | Solo limpieza + fix de formato en `presence_lookup` |

---

## Lecciones aprendidas

| # | Lección |
|---|---------|
| L-T2C.1 | `hasattr(obj, 'results')` como guard de tipo es frágil cuando el consumidor canónico es un dict. El fix dual (dict + dataclass) cubre ambos formatos sin romper tests existentes. |
| L-T2C.2 | Un `NameError` latente puede sobrevivir meses si el consumidor está bajo un `except Exception` amplio. Los `except` amplios son máscaras de NameErrors. |
| L-T2C.3 | Antes de escribir tests nuevos, verificar si el contrato ya está fijado por tests existentes en otros directorios. S9 ya estaba certificado. |
