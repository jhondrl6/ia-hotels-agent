# Dependencias entre Fases — DT-4 Residual Fixes

> **Plan**: DT4-RESIDUAL-FIXES
> **Target**: v4.66.0

## Diagrama de Dependencias

```
FASE-1 (Contract) ───────────────────────────────────────────┐
  └── Independiente                                           │
                                                              │
FASE-2 (SitePresence) ────────────────────────────────────────┤
  └── Independiente (pero FASE-3 la requiere)                 │
         │                                                    │
         ▼                                                    │
FASE-3 (Coherence Unify)                                      │
  └── Requiere FASE-2 (site_presence_report propagado)       │
                                                              │
FASE-4 (Alignment Unify) ─────────────────────────────────────┤
  └── Independiente                                           │
                                                              │
FASE-5 (Gate Idempotency) ────────────────────────────────────┤
  └── Depende de FASE-2 (pub_gates.py sin mutaciones)          │
                                                              │
         Todos convergen ─────────────────────────────────────┤
                                                              │
                                                              ▼
                                                    FASE-6 (E2E Zione)
                                                    └── Requiere FASE-1,2,3,4,5
                                                              │
                                                              ▼
                                                    FASE-RELEASE-v4.66.0
                                                    └── Requiere FASE-6
```

## Tabla de Dependencias

| Fase | Depende de | Bloquea a | Archivos que modifica |
|------|-----------|-----------|----------------------|
| FASE-1 | — | FASE-6 | `assessment_builder.py`, `main.py`, `v4_asset_orchestrator.py` |
| FASE-2 | — | FASE-3, FASE-6 | `site_presence_checker.py`, `coherence_validator.py`, `v4_asset_orchestrator.py`, `main.py`, `publication_gates.py` |
| FASE-3 | FASE-2 | FASE-6 | `v4_asset_orchestrator.py`, `assessment_builder.py`, `main.py` |
| FASE-4 | — | FASE-6 | `publication_gates.py`, `modules/quality_gates/delivery_quality_report.py` |
| FASE-5 | FASE-2 (logicamente) | FASE-6 | `publication_gates.py`, `main.py` |
| FASE-6 | FASE-1,2,3,4,5 | FASE-RELEASE | Ninguno (solo ejecución v4complete) |
| RELEASE | FASE-6 | — | `VERSION.yaml`, `CHANGELOG.md`, `GUIA_TECNICA.md`, `REGISTRY.md`, `DOMAIN_PRIMER.md` |

## Tabla de Conflictos Potenciales

| Archivo | Modificado por | Riesgo de conflicto |
|---------|---------------|---------------------|
| `assessment_builder.py` | FASE-1, FASE-3 | ⚠️ MEDIO — FASE-1 agrega campo, FASE-3 cambia `with_coherence()` |
| `main.py` | FASE-1, FASE-2, FASE-3, FASE-5 | ⚠️ ALTO — 4 fases tocan el mismo archivo (146KB) |
| `v4_asset_orchestrator.py` | FASE-1, FASE-2, FASE-3 | ⚠️ MEDIO — FASE-1 expone resultado, FASE-2 pasa site_presence, FASE-3 agrega final_coherence |
| `publication_gates.py` | FASE-2, FASE-4, FASE-5 | ⚠️ MEDIO — Eliminar mutaciones (FASE-5) + eliminar reconstrucción fake (FASE-2) |
| `coherence_validator.py` | FASE-2 | ✅ BAJO — solo agrega llamadas con `site_presence_report` |

### Estrategia de mitigación para `main.py`

Las 4 fases que tocan `main.py` deben modificar **secciones diferentes**:
- FASE-1: carga de `pain_ledger_resolved` + inyección en builder (zona de carga de datos, ~L2670-2770)
- FASE-2: una llamada a `SitePresenceChecker` + propagación (zona de pre-diagnóstico, ~L2395 + ~L2673)
- FASE-3: consumo de `final_coherence_report` (zona de assessment, ~L2764)
- FASE-5: eliminar doble ejecución de gates (zona de gates, ~L2775)

Cada fase debe usar `patch()` con contexto suficiente para no colisionar.

## Orden de Ejecución Recomendado

```
Sesión 1: FASE-1 (Contract)
Sesión 2: FASE-2 (SitePresence) ← MAYOR COMPLEJIDAD
Sesión 3: FASE-3 (Coherence)
Sesión 4: FASE-4 (Alignment)
Sesión 5: FASE-5 (Gate Idempotency)
Sesión 6: FASE-6 (E2E Zione)
Sesión 7: FASE-RELEASE
```

Las fases independientes (FASE-1, FASE-2, FASE-4) pueden ejecutarse en cualquier orden. FASE-3 debe ir después de FASE-2. FASE-5 debe ir después de FASE-2 (ambas modifican `publication_gates.py`).
