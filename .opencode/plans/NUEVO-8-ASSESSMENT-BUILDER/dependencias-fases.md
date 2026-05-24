# Dependencias entre Fases — NUEVO-8 AssessmentBuilder

## Diagrama de Dependencias

```
N8-A (Auditoría + Diseño + Tests dataclass)
  │
  ├──▶ N8-B (AssessmentBuilder + Migración main.py + Tests)
  │      │
  │      ├──▶ N8-C (Simplificar extractores + Eliminar muertos + Tests)
  │      │      │
  │      │      └──▶ N8-D (E2E v4complete Hotel Castilla Real)
  │      │             │
  │      │             └──▶ N8-RELEASE (CHANGELOG + sync + validación)
  │      │
  │      └──▶ (N8-C también consume AssessmentPayload definido en N8-A)
  │
  └──▶ (Todas las fases consumen AssessmentPayload de N8-A)
```

## Tabla de Conflictos de Archivos

| Archivo | N8-A | N8-B | N8-C | N8-D | N8-RELEASE | Riesgo |
|---------|------|------|------|------|------------|--------|
| `main.py` | — | **MOD** (L2663-2754 → builder) | — | — | — | Bajo — solo bloque assessment |
| `modules/assessment_builder.py` | **NEW** | **MOD** | — | — | — | Bajo — N8-A crea dataclass, N8-B agrega builder |
| `modules/quality_gates/publication_gates.py` | — | — | **MOD** (extractores) | — | — | Medio — simplifica ~129 líneas |
| `tests/test_assessment_builder.py` | **NEW** | **MOD** | **MOD** | — | — | Bajo — acumulativo |
| `tests/quality_gates/test_publication_gates.py` | — | — | **MOD** | — | — | Bajo |
| `CHANGELOG.md` | — | — | — | — | **MOD** | Bajo |
| `docs/GUIA_TECNICA.md` | — | — | — | — | **MOD** | Bajo |
| `VERSION.yaml` | — | — | — | — | **MOD** | Bajo |

## Orden de Ejecución

1. **N8-A** (sin dependencias) — crea `AssessmentPayload` dataclass + tests
2. **N8-B** (depende de N8-A) — implementa `AssessmentBuilder` + migra main.py
3. **N8-C** (depende de N8-B) — simplifica extractores + elimina campos muertos
4. **N8-D** (depende de N8-C) — E2E v4complete para verificar que todo funciona
5. **N8-RELEASE** (depende de N8-D) — documentación final

## Notas

- **N8-A y N8-B** no pueden fusionarse: R3 — sumarían 8 tareas
- **N8-C** requiere que el assessment dict del builder ya esté en producción (N8-B completado) para poder simplificar extractores
- **N8-D** solo se ejecuta si N8-C completó — es la verificación E2E
- **N8-RELEASE** es siempre la última fase
