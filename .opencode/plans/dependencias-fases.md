# Dependencias entre Fases — Gap Arquitectónico Brechas V6

**Proyecto**: Brecha Architectural Fix — propuesta_v6 no consume brechas reales
**Version Base**: v4.25.3
**Version Target**: v4.26.0 (FASE-RELEASE-4.26.0)
**Creado**: 2026-04-10

---

## Diagrama de Dependencias

```
FASE-F ─── Phantom Cost Fix + Dead Code Removal ✅ COMPLETADA (2026-04-10)
  │           (propuesta: líneas 539-546, template V4)
  │
  ▼
FASE-G ─── Dual Source Conflict Resolution ✅ COMPLETADA (2026-04-10)
  │           (diagnostic: _inject_brecha_scores vs _get_brecha_*)
  │
  ▼
FASE-H ─── Performance Cache + Cleanup ✅ COMPLETADA (2026-04-10)
  │           (_identify_brechas 9x → 1x, pain_to_type cleanup, loop normalization)
  │
  ▼
FASE-I ─── data_structures.py Deduplication
  │           (Scenario duplicado, funciones duplicadas)
  │
  ▼
FASE-J ─── E2E Validation + Release
              (v4complete amaziliahotel.com + FASE-RELEASE-4.26.0)
```

**Todas las fases son secuenciales** — cada una depende de la anterior.
No hay paralelismo posible porque todas tocan los mismos archivos o dependencias encadenadas.

---

## Tabla de Conflictos Potenciales

| Archivo | Fases que lo modifican | Tipo de Conflicto |
|---------|----------------------|-------------------|
| `v4_proposal_generator.py` | FASE-F | Exclusivo — solo esta fase lo toca |
| `v4_diagnostic_generator.py` | FASE-G, FASE-H | **COMPARTIDO** — G modifica _inject_brecha_scores, H agrega caché |
| `data_structures.py` | FASE-I | Exclusivo |
| `propuesta_v4_template.md` | FASE-F | Exclusivo (si necesita ajuste) |
| `tests/commercial_documents/test_diagnostic_brechas.py` | FASE-G, FASE-H | **COMPARTIDO** — ambos agregan/actualizan tests |
| `tests/test_proposal_alignment.py` | FASE-F | Exclusivo |

### Riesgos

| Riesgo | Mitigación |
|--------|-----------|
| FASE-G y FASE-H ambas tocan diagnostic_generator.py | G modifica lógica de scores, H agrega caché. Sectores distintos, bajo riesgo de merge conflict |
| Tests compartidos entre G y H | Cada fase agrega sus propios tests, no modifica los del otro |
| FASE-J depende de que F,G,H,I estén 100% completas | Checklist obligatorio antes de ejecutar J |

---

## Archivos Involucrados por Fase

### FASE-F (Phantom Cost Fix) ✅ COMPLETADA
- `modules/commercial_documents/v4_proposal_generator.py` — distribución fija 40/30/20/10 reemplazada por `_build_brecha_data()` dinámico
- `tests/test_proposal_alignment.py` — 5 tests nuevos (phantom costs), 0 regresiones
- Template V4: funciona correctamente con variables dinámicas

### FASE-G (Dual Source Conflict)
- `modules/commercial_documents/v4_diagnostic_generator.py` (líneas 510-521 vs 586, 1976-2024)
- `tests/commercial_documents/test_diagnostic_brechas.py` (tests nuevos)

### FASE-H (Performance Cache + Cleanup)
- `modules/commercial_documents/v4_diagnostic_generator.py` (líneas 1539-1923, pain_to_type 1931)
- `tests/commercial_documents/test_diagnostic_brechas.py` (tests nuevos)

### FASE-I (data_structures Dedup)
- `modules/commercial_documents/data_structures.py` (líneas 83-114 duplicadas, 320/419, 362/461)
- Tests existentes deben seguir pasando sin cambios

### FASE-J (E2E Validation + Release)
- `main.py` (ejecutar v4complete, sin modificar)
- `scripts/log_phase_completion.py` (registro)
- Documentación: CHANGELOG.md, GUIA_TECNICA.md, VERSION.yaml

---

## Orden de Ejecución Obligatorio

```
Sesión 1 → FASE-F  (Phantom Cost Fix)
Sesión 2 → FASE-G  (Dual Source Conflict)
Sesión 3 → FASE-H  (Cache + Cleanup)
Sesión 4 → FASE-I  (Deduplication)
Sesión 5 → FASE-J  (E2E + Release)
```

**Regla**: 1 fase por sesión. Sin excepciones.
