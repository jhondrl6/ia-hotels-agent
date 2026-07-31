# Dependencias entre Fases — DT-3

> **Plan**: DT-3-TECH-DEBT-2026-07-25
> **Target**: v4.64.0

---

## Grafo de Dependencias

```
FASE-0 (BUG-1: Fix rutas flat)
  │
  ├──▶ FASE-1 (BUG-2 + BUG-3: Fix G9)
  │      │
  │      ├──▶ FASE-2 (BUG-4/P-04: Unificación)
  │             │
  │             ├──▶ FASE-3 (v4complete Zi One + verificación)
  │                    │
  │                    └──▶ FASE-RELEASE (Docs + version bump)
```

---

## Tabla de Dependencias

| Fase | Depende de | Bloquea a | Justificación |
|------|-----------|-----------|---------------|
| FASE-0 | — (root cause) | FASE-1, FASE-2, FASE-3 | BUG-1 es causa raíz: sin pain_ledger real, FASE-1 no tiene datos para validar G9, FASE-2 unificaría sobre datos incorrectos |
| FASE-1 | FASE-0 | FASE-2, FASE-3 | BUG-2 y BUG-3 son pre-requisitos: FASE-2 debe unificar sobre un G9 ya corregido para no propagar bugs |
| FASE-2 | FASE-0, FASE-1 | FASE-3 | La unificación es el cambio más grande; FASE-3 verifica que todo el pipeline funcione post-unificación |
| FASE-3 | FASE-0, FASE-1, FASE-2 | FASE-RELEASE | v4complete verifica E2E; RELEASE solo procede con verificación verde |
| FASE-RELEASE | FASE-3 | — (final) | Docs cascade requiere que todo esté implementado y verificado |

---

## Matriz de Conflictos de Archivos

| Archivo | FASE-0 | FASE-1 | FASE-2 | FASE-3 | RELEASE | ¿Conflicto? |
|---------|--------|--------|--------|--------|---------|-------------|
| main.py | ✅ MODIFICA (3 líneas + helper) | — | ✅ MODIFICA (imports) | — | — | ⚠️ Orden estricto: FASE-0 primero, FASE-2 después |
| modules/quality_gates/delivery_quality_report.py | — | ✅ MODIFICA (L201-258) | ✅ MODIFICA (G9 → contrato unificado) | — | — | ⚠️ Orden estricto: FASE-1 primero, FASE-2 después |
| modules/asset_generation/proposal_asset_alignment.py | — | — | ✅ MODIFICA (unificación) | — | — | Sin conflicto |
| modules/delivery/delivery_context.py | — | — | ✅ POSIBLE EXTENSIÓN | — | — | Sin conflicto |
| tests/delivery/test_delivery_contract.py | — | — | ✅ MODIFICA (nuevos tests) | — | — | Sin conflicto |
| VERSION.yaml | — | — | — | — | ✅ MODIFICA | Sin conflicto |
| CHANGELOG.md | — | — | — | — | ✅ MODIFICA | Sin conflicto |

**Regla**: FASE-2 toca archivos que también modifica FASE-1 (delivery_quality_report.py). El orden FASE-1 → FASE-2 es obligatorio.

---

## Orden de Ejecución Recomendado

1. **FASE-0** — Nueva sesión. Fix causa raíz. Sin dependencias previas.
2. **FASE-1** — Nueva sesión. Fixes pequeños sobre G9 ya funcional. Depende de FASE-0.
3. **FASE-2** — Nueva sesión. Unificación arquitectónica. **MAYOR COMPLEJIDAD**. Depende de FASE-0 + FASE-1.
4. **FASE-3** — Nueva sesión. v4complete + verificación E2E. Depende de FASE-0 + FASE-1 + FASE-2.
5. **FASE-RELEASE** — Nueva sesión. Docs cascade. Depende de FASE-3.
