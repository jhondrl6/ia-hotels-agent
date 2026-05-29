# Dependencias de Fases — REFACTOR-PENDIENTE-V4.58.0

## Diagrama ASCII

```
┌─────────────────────────────────────────────────────────────────┐
│  FASE-0: Verificación y Preparación                             │
│  [grep verification + baseline capture]                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  FASE-1A: IMP-03 (CAPEX) + F7 (Gate)                            │
│  [template fix + gate unification]                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  FASE-1B: F5 (ADR checklist bug)                                │
│  [quick bug fix]                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  FASE-2: MIN-02 (ADR evidenciado)  *** MÁS COMPLEJA ***          │
│  [YAML + código + template — NO DELEGAR]                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  FASE-3: MIN-01 (Status Quo)                                    │
│  [nueva función + template]                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  FASE-4: MIN-03 (Closing pitch)                                 │
│  [nueva función + template]                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  FASE-5: Limpieza dead code                                     │
│  [eliminar template embebido muerto]                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  FASE-6: v4complete Hotel Castilla Real (E2E)                   │
│  [ejecución única + post-análisis de fixes]                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  FASE-RELEASE: Docs cascade                                     │
│  [REGISTRY + CHANGELOG + GUIA_TECNICA + sync_versions]          │
└─────────────────────────────────────────────────────────────────┘
```

## Tabla de Conflictos Potenciales

| Fase | Archivos Modificados | Conflictos con otras fases |
|------|---------------------|----------------------------|
| FASE-0 | Todos (lectura) | Ninguno |
| FASE-1A | `propuesta_v6_template.md`, `publication_gates.py` | Ninguno |
| FASE-1B | `v4_proposal_generator.py` L1934 | Ninguno (cambio localizado) |
| FASE-2 | `regional_benchmarks.yaml`, `v4_proposal_generator.py`, `v4_diagnostic_generator.py`, `propuesta_v6_template.md` | **ALTO** — mismo archivo que 1B, 3, 4, 5 |
| FASE-3 | `v4_proposal_generator.py`, `propuesta_v6_template.md` | MEDIO — mismo archivo que 2, 4, 5 |
| FASE-4 | `v4_proposal_generator.py`, `propuesta_v6_template.md` | MEDIO — mismo archivo que 2, 3, 5 |
| FASE-5 | `v4_proposal_generator.py` | BAJO — solo elimina líneas L575-605 |
| FASE-6 | Output en `output/v4_complete/` + `evidence/` | Ninguno |
| RELEASE | Documentación (`CHANGELOG.md`, `GUIA_TECNICA.md`, `REGISTRY.md`) | Ninguno |

## Mitigación de Conflictos

- **FASE-2 va antes de 3, 4, 5** porque modifica los mismos archivos que ellas
- Cada fase de código (2, 3, 4) añade funciones/places nuevos, no sobreescribe
- FASE-5 (cleanup) va al final porque elimina código muerto
- Cada fase debe ejecutar tests después de sus cambios para detectar regresiones

## Evaluación R3 por Fase

| Fase | Tareas | Comandos Largos | Dentro de R3? |
|------|--------|-----------------|---------------|
| FASE-0 | 4 | 0 | ✅ Sí |
| FASE-1A | 4 | 0 | ✅ Sí |
| FASE-1B | 3 | 0 | ✅ Sí |
| FASE-2 | 4 | 0 | ✅ Sí |
| FASE-3 | 4 | 0 | ✅ Sí |
| FASE-4 | 4 | 0 | ✅ Sí |
| FASE-5 | 3 | 0 | ✅ Sí |
| FASE-6 | 4 | 1 (v4complete 900s) | ✅ Sí (3 tareas + 1 largo) |
| RELEASE | 4 | 0 | ✅ Sí |

## Presupuesto de Iteraciones

| Fase | Fijas | Específicas | Total Est. |
|------|-------|-------------|------------|
| FASE-0 | ~26 | ~10 | ~36 |
| FASE-1A | ~26 | ~12 | ~38 |
| FASE-1B | ~26 | ~8 | ~34 |
| FASE-2 | ~26 | ~20 | ~46 |
| FASE-3 | ~26 | ~14 | ~40 |
| FASE-4 | ~26 | ~14 | ~40 |
| FASE-5 | ~26 | ~8 | ~34 |
| FASE-6 | ~26 | ~12 | ~38 |
| RELEASE | ~26 | ~12 | ~38 |

## Orden de Ejecución Recomendado

1. **FASE-0** → verificación + preparación
2. **FASE-1A** → IMP-03 (CAPEX breakdown) + F7 (gate discrepancy)
3. **FASE-1B** → F5 (ADR checklist bug)
4. **FASE-2** → MIN-02 (ADR evidenciado) — **MÁS COMPLEJA, NO DELEGAR**
5. **FASE-3** → MIN-01 (Status Quo table)
6. **FASE-4** → MIN-03 (Closing pitch)
7. **FASE-5** → Limpieza dead code
8. **FASE-6** → v4complete Hotel Castilla Real (E2E)
9. **RELEASE** → docs cascade

## Reglas de Delegación

| Fase | Delegate | Razón |
|------|----------|-------|
| 0, 1A, 1B, 3, 4, 5, 6 | ✅ Sí | Tareas mecánicas + tests, bajo riesgo |
| 2 | ❌ No | Triple capa YAML+código+template, alto riesgo de regresión |
| RELEASE | ❌ No | Scripts interactivos (log_phase, sync_versions) |
