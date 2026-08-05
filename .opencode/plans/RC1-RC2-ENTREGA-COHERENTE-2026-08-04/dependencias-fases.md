# Dependencias de Fases — RC1-RC2-ENTREGA-COHERENTE-2026-08-04

> Actualizado: 2026-08-04 (Etapa 1 — Preparación)

## Diagrama de Dependencias

```
FASE-A (triage tests patológicos)
   │  PREREQUISITO de B (los tests del área propuesta son los patológicos)
   ▼
FASE-B (RC1 — parametrización propuesta) ◄── MAYOR COMPLEJIDAD
   │
   ▼
FASE-C (RC2-a — gates N11/N15)
   │  (C no depende de B a nivel código, pero B primero por severidad ALTA
   │   y porque el run E2E verifica ambos)
   ▼
FASE-D (RC2-b — ZIP/S7/S5)  ←── tracks independientes internas (delegate_task)
   │
   ▼
FASE-E (RC3 — higiene documental)  ←── independiente de B/C/D a nivel código;
   │                                    va después para reflejar estado final
   ▼
FASE-F (E2E v4complete Zione + análisis post-implementación)
   │  requiere: A ✅ B ✅ C ✅ D ✅ (E puede estar en progreso,
   │  pero los fixes de código deben estar cerrados)
   ▼
FASE-RELEASE-4.71.0 (requiere A-F ✅)
```

## Tabla de Conflictos de Archivos

| Archivo | Fases que lo tocan | Conflicto |
|---------|--------------------|-----------|
| `modules/commercial_documents/v4_proposal_generator.py` | FASE-B | Ninguno (solo B) |
| `modules/commercial_documents/pain_solution_mapper.py` | FASE-B (lectura para mapa inverso) | Ninguno (solo lectura) |
| `modules/quality_gates/commercial_gate.py` | FASE-C | Ninguno (solo C) |
| `modules/commercial_documents/v4_diagnostic_generator.py` | FASE-C | Ninguno (solo C — cableado tier) |
| `modules/delivery/delivery_packager.py` | FASE-D | Ninguno (solo D) |
| `main.py` (loader onboarding) | FASE-D (S7) | Ninguno |
| `modules/financial_engine/harness_handlers.py` L118 (occupancy label) | FASE-D (S5) | Ninguno |
| `pytest.ini` / `tests/_archived_broken_tests/` | FASE-A | Ninguno |
| `.opencode/plans/COHERENCIA-MODULO-ENTREGA-2026-08-03/*` | FASE-E | Ninguno (solo MD) |
| `scripts/run_all_validations.py` | FASE-E (nuevo check `_check_prompts_no_release`) | Ninguno (solo E; stdlib-only, sin imports del proyecto) |
| CHANGELOG / VERSION / GUIA_TECNICA / AGENTS | FASE-RELEASE | Ninguno (solo RELEASE edita versión) |
| `tests/commercial_documents/test_*propuesta*` | FASE-B (nuevos), FASE-A (triage) | A aisla patológicos ANTES de que B agregue tests → sin conflicto por orden |

**Conclusión**: sin conflictos de archivos entre fases gracias al orden A→B→C→D→E→F.
No hay dos fases tocando el mismo archivo.

## Estados

| Fase | Estado | Fecha | Notas |
|------|--------|-------|-------|
| FASE-A | ⬜ Pendiente | — | Prerrequisito crítico |
| FASE-B | ⬜ Pendiente | — | Mayor complejidad técnica |
| FASE-C | ⬜ Pendiente | — | |
| FASE-D | ⬜ Pendiente | — | Delegable (3 tracks) |
| FASE-E | ⬜ Pendiente | — | Delegable (solo docs) |
| FASE-F | ⬜ Pendiente | — | 1 solo v4complete (Zi One Luxury) |
| FASE-RELEASE-4.71.0 | ⬜ Pendiente | — | Delegable |

## Notas de Recuperación

- Si una fase queda ⏳ INCOMPLETA: registrar aquí checkpoint + qué falta + timestamp.
- La sesión siguiente lee esta tabla y continúa desde el checkpoint (no re-ejecuta lo ya hecho).
