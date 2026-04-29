# Dependencias y Conflictos entre Fases

**Proyecto**: PATCH-AUDITORIA-FORENSE-AMAZILIA-v2
**Versión**: 4.36.1 → 4.37.0
**Fecha**: 2026-04-29

---

## Diagrama de Dependencias

```
FASE-PATCH-A (Critical Bugs + Stubs + Unicode)
    │
    ├── v4_proposal_generator.py: fix BUG-1 (ROI X) + BUG-2 (pain_ratio)
    ├── v4_diagnostic_generator.py: fix H-3/H-4/H-5 (blog/speakable/ga4 stubs)
    └── scripts/version_consistency_checker.py: fix unicode crash
    │
    ▼
FASE-PATCH-B (Placeholders + Evidence Integrity)
    │
    ├── v4_proposal_generator.py: fix H-1 (web_score "85")
    ├── two_phase_flow.py: fix H-2 (phone placeholder)
    └── scenario_calculator.py: fix H-6 (Evidence Tier "C")
    │
    ▼
FASE-PATCH-C (v4complete Verification)
    │
    ├── Ejecutar v4complete --url https://amaziliahotel.com/
    ├── Guardar evidencia proactiva en evidence/fase-patch-auditoria-v2/
    └── Verificar todos los fixes reflejados en output
    │
    ▼
FASE-PATCH-D (Docs + Version Sync + Deuda Técnica)
    │
    ├── scripts/derive_version_from_changelog.py ✅ (NUEVO)
    ├── VERSION.yaml 4.36.1 ✅ + sync_versions ✅
    ├── AGENTS.md: H-7 (test count) + H-8 (gates) ✅
    └── docs/technical_debt/hardcodes_audit_2026-04-29.md ✅
    │
    ▼
FASE-RELEASE-4.37.0 (Cierre Oficial)
    │
    ├── sync_versions.py
    ├── CHANGELOG.md [4.37.0]
    ├── GUIA_TECNICA.md nota técnica
    └── run_all_validations.py --quick
```

---

## Tabla de Conflictos de Archivos

| Archivo | PATCH-A | PATCH-B | PATCH-C | PATCH-D | RELEASE | Conflicto |
|---------|---------|---------|---------|---------|---------|-----------|
| `v4_proposal_generator.py` | ESCRIBE | ESCRIBE | LEE | - | - | ⚠️ MISMO ARCHIVO (secuencial) |
| `v4_diagnostic_generator.py` | ESCRIBE | - | LEE | - | - | Ninguno |
| `version_consistency_checker.py` | ESCRIBE | - | - | - | EJECUTA | Ninguno |
| `two_phase_flow.py` | - | ESCRIBE | - | - | - | Ninguno |
| `scenario_calculator.py` | - | ESCRIBE | - | - | - | Ninguno |
| `derive_version_from_changelog.py` | - | - | - | CREA | - | Ninguno |
| `VERSION.yaml` | - | - | - | ESCRIBE | ESCRIBE | Ninguno (secuencial) |
| `AGENTS.md` | - | - | - | ESCRIBE | ESCRIBE | Ninguno (secuencial) |
| `output/v4_complete/` | - | - | GENERA | LEE | - | Ninguno |
| `CHANGELOG.md` | - | - | - | - | ESCRIBE | Ninguno |
| `GUIA_TECNICA.md` | - | - | - | - | ESCRIBE | Ninguno |

**⚠️ Alerta**: `v4_proposal_generator.py` es modificado por PATCH-A y PATCH-B. Son secuenciales (sin conflicto real), pero PATCH-B debe aplicar sus cambios SOBRE el código ya modificado por PATCH-A. El prompt de PATCH-B incluye esta advertencia.

---

## Evaluación de Scope (R3)

### FASE-PATCH-A: Critical Bugs + Diagnostic Stubs + Unicode Fix

```
TAREAS DE LA FASE:
  [ ] T1: Investigar BUG-1 (ROI .replace), BUG-2 (pain_ratio), stubs H-3/H-4/H-5
  [ ] T2: Fix BUG-1 + BUG-2 en v4_proposal_generator.py
  [ ] T3: Fix H-3/H-4/H-5 (blog/speakable/ga4) + fix unicode en version_consistency_checker.py
  [ ] T4: Ejecutar tests + documentación de fase

CONTADOR:
  - T1 = 1 tarea (investigación)
  - T2 = 1 tarea (fix proposal generator)
  - T3 = 1 tarea (fix diagnostic + unicode)
  - T4 = 1 tarea (verificación + docs)
  - Total: 4 tareas + 0 comandos largos = DENTRO DEL LÍMITE R3
```

### FASE-PATCH-B: Placeholders + Evidence Integrity

```
TAREAS DE LA FASE:
  [x] T1: Investigar H-1 (web_score), H-2 (phone), H-6 (Evidence Tier)
  [x] T2: Fix H-1 en v4_proposal_generator.py
  [x] T3: Fix H-6 en scenario_calculator.py + Fix H-2 en two_phase_flow.py
  [x] T4: Tests + documentación de fase

CONTADOR:
  - T1 = 1 tarea (investigación)
  - T2 = 1 tarea (fix web_score)
  - T3 = 1 tarea (fix evidence tier + phone)
  - T4 = 1 tarea (verificación + docs)
  - Total: 4 tareas + 0 comandos largos = DENTRO DEL LÍMITE R3
```

### FASE-PATCH-C: v4complete Verification

```
TAREAS DE LA FASE:
  [x] T1: Ejecutar v4complete --url https://amaziliahotel.com/ (COMANDO LARGO)
  [x] T2: Guardar evidencia proactiva en evidence/fase-patch-auditoria-v2/
  [x] T3: Verificar output contra criterios de aceptación

CONTADOR:
  - T1 = 1 tarea + 1 comando largo
  - T2 = 1 tarea
  - T3 = 1 tarea
  - Total: 3 tareas + 1 comando largo = DENTRO DEL LÍMITE R3
```

### FASE-PATCH-D: Docs + Version Sync + Deuda Técnica

```
TAREAS DE LA FASE:
  [x] T1: Crear derive_version_from_changelog.py + resolver drift + sync_versions
  [x] T2: Fix AGENTS.md: H-7 (test count) + H-8 (gates count)
  [x] T3: Crear docs/technical_debt/hardcodes_audit_2026-04-29.md (H-9→H-27)
  [x] T4: Docs cascade: log_phase para PATCH-A, B, C + run_all_validations

CONTADOR:
  - T1 = 1 tarea (script nuevo + drift)
  - T2 = 1 tarea (fix docs)
  - T3 = 1 tarea (deuda técnica)
  - T4 = 1 tarea (docs cascade)
  - Total: 4 tareas + 0 comandos largos = DENTRO DEL LÍMITE R3
```

---

## Presupuesto de Iteraciones

| Fase | Fijo (~26-36) | Específico | Total estimado |
|------|---------------|------------|----------------|
| PATCH-A | 26 | 15-20 (2 bugs + 3 stubs + unicode) | ~41-46 |
| PATCH-B | 26 | 12-18 (3 fixes cross-module) | ~38-44 |
| PATCH-C | 26 | 8-10 (v4complete + verify) | ~34-36 |
| PATCH-D | 26 | 15-20 (script nuevo + docs + deuda) | ~41-46 |
| RELEASE | 26 | 8-12 (docs cascade) | ~34-38 |

Todas dentro del límite de 60 iteraciones.

---

## Versiones

- **v1.0.0** (2026-04-29): Plan inicial basado en ContextMv2.md + ContextMM.md
