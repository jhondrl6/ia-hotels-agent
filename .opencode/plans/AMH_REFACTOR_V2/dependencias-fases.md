# Dependencias de Fases — Amaziliahotel Refactor v2
**Corregido post-rediagnóstico: persistencias de timing/API/serialización**

## Diagrama de Dependencias

```
FASE-1 a FASE-8 (Completadas ✅)
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│              REDIAGNOSTICO                           │
│  ROOT_CAUSE_ANALYSIS.md: 3 causas raíz confirmadas  │
└─────────────────────┬───────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
    FASE-PATCH-1  FASE-PATCH-2  FASE-PATCH-3
    [Places API   [Scrubber     [Region
     FieldMask     timing fix    serialization
     + lat/lng]    re-scrub]     fix]
          │           │           │
          └───────────┼───────────┘
                      ▼
              FASE-RELEASE ⏳
         [E2E real validation
          post-patches + release]
```

## Matriz de Conflictos de Archivos

| Fase | Archivos Modificados | Riesgo Conflicto |
|------|---------------------|------------------|
| FASE-PATCH-1 | `modules/auditors/v4_comprehensive.py`, `modules/asset_generation/conditional_generator.py` | Bajo |
| FASE-PATCH-2 | `main.py` (~10 líneas, post-L2476) | Medio |
| FASE-PATCH-3 | `main.py` (3 líneas, ~L2289/2538/2738) | Medio |
| FASE-RELEASE | Scripts de validación, docs | N/A |

**Conflicto PATCH-2 + PATCH-3**: Ambos tocan `main.py` pero en líneas distintas (PATCH-2 ~L2476, PATCH-3 ~L2289/2538/2738). Sin conflicto directo, pero ejecutar SECUENCIALMENTE (no paralelo) para evitar merge issues.

## Dependencias

| Fase | Depende de | Por qué |
|------|-----------|---------|
| FASE-PATCH-1 | FASE-1 a FASE-8 | Fix de persistencia en API layer |
| FASE-PATCH-2 | FASE-1 a FASE-8 | Fix de timing en main.py |
| FASE-PATCH-3 | FASE-1 a FASE-8 | Fix de serialización en main.py |
| FASE-RELEASE | PATCH-1 + PATCH-2 + PATCH-3 | Validación E2E requiere todos los fixes |

**Paralelizables**: PATCH-1 es independiente de PATCH-2/3 (archivos distintos). PATCH-2 y PATCH-3 NO son paralelizables (ambos tocan main.py).

**Secuencia recomendada**: PATCH-1 → PATCH-2 → PATCH-3 → FASE-RELEASE

## Criterios de Avance

| Fase | Criterio de éxito |
|------|-------------------|
| FASE-PATCH-1 | FieldMask incluye places.location, PlaceData usa coords del API, _is_valid rechaza (0,0) |
| FASE-PATCH-2 | ✅ `grep 'Re-scrub proposal' main.py` = 1 match; `postscrubber` en scope post-L2476 |
| FASE-PATCH-3 | 3 puntos de serialización usan .title(), interna sigue lowercase |
| FASE-RELEASE | COP COP=0, coords!=0.0, region=Title Case, publication_ready=true |
