# Diagrama de Dependencias — ROICRII

```
FASE-1 ─────────────┐ ✅ COMPLETED
(Root Cause ROI)     │ 2026-05-27
Sin prerrequisitos   │ Tests: 11/11 passed
CRIT-01 + IMP-02     │ Evidencia: grep 0 inline, 6 calls
                     ▼
FASE-2 ─────────────┐
(Coherencia)         │
Depende: FASE-1      │
NEW-03 + CRIT-02     │
                     ▼
FASE-3 ─────────────┐
(Semántica+Gate)     │
Depende: FASE-2      │
IMP-01 + NEW-05      │
+ NEW-02             │
                     ▼
FASE-4 ─────────────┐
(CAPEX+Rename)       │
Depende: FASE-3      │
IMP-03 + NEW-04      │
                     ▼
FASE-5 ─────────────┐
(v4complete)         │
Depende: FASE-4      │
Ejecución única      │
                     ▼
FASE-6
(RELEASE)
Depende: FASE-5
Docs+Sync
```

## Reglas de Dependencia

| Si FASE-X falla | Impacto |
|-----------------|---------|
| FASE-1 | FASE-2, 3, 4, 5, 6 bloqueadas |
| FASE-2 | FASE-3, 4, 5, 6 bloqueadas |
| FASE-3 | FASE-4, 5, 6 bloqueadas |
| FASE-4 | FASE-5, 6 bloqueadas |
| FASE-5 | FASE-6 bloqueada |
| FASE-6 | No bloquea nada (es la última fase) |

## Notas

- FASE-1 a FASE-4: Código+Tests (máx 4 tasks o 3 tasks + 1 long command)
- FASE-5: Ejecución (1 long command + 1 task de análisis)
- FASE-6: Docs+Sync (version bump, CHANGELOG, REGISTRY, pre-commit)
- No hay fases paralelas — todo es secuencial
- 1 sesión = 1 fase (regla R1)
- RELEASE es MANDATORIO — nunca omitir
