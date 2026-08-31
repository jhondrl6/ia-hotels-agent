# Checklist de Implementación — VALIDADOR-URL-PROPIA-2026-08-30

| # | Fase | Sesión | Estado | Fecha | delegate_task | Notas |
|---|------|--------|--------|-------|---------------|-------|
| 0 | Preparación | 2026-08-30 | ✅ Completada | 2026-08-30 | No | Plan + 6 prompts + docs base; Paso 0 (memoria + QMind) ejecutado |
| 1 | FASE-A — Núcleo del guard (TDD) | 2026-08-30 | ✅ Completada | 2026-08-30 | No (DIRECTO) | Contratos rojos→verdes 45/45; 28/28 canonicalización; baseline 14 fallos preexistentes (sin nuevos); validaciones 7/7; smoke CLI exit 2 |
| 2 | FASE-B — Superficies secundarias | 2026-08-31 | ✅ Completada | 2026-08-31 | Sí (2 subagentes) | AC6 last_url (rechazo precede a save_state, sin repersistencia) + AC7 hook-pdf + capa datos (scraper/auditor); +35 def test_ / 47 casos; 120 passed contratos integrados; 3 smokes CLI (hook-pdf exit 0 real / exit 2 OTA / v4complete exit 2); D-VUP-B1 resuelve el conflicto --force |
| 3 | FASE-C — Verificación empírica Don Julio | 2026-08-31 | ✅ Completada | 2026-08-31 | Sí | 11/11 probes PASS; regresión 101 passed 0 failed; P6 corregido (--output-dir); P5 comportamiento correcto (no re-persiste) |
| 4 | FASE-D — E2E v4complete Salento Real | 2026-08-31 | ✅ Completada | 2026-08-31 | Mixto (comando delegado) | EXIT_CODE=0 (~3 min pared); "Using defaults" (equivalencia F5); 0 interferencias guard; 7/7 checks vs baseline H2 (`verificar_no_regresion.py`): coherence 0.88=, READY_FOR_PUBLICATION, 13/13 gates sin regresión, plan assets/pains/financieros byte-equal; anomalías = infra preexistente (gemini 403, PageSpeed key) |
| 5 | FASE-VERIFY — Certificación AC1-AC8 | nueva | ⏳ Pendiente | — | No (DIRECTO §4.6) | Baja-Media; sin código, sin v4complete |
| 6 | FASE-RELEASE-4.74.0 | nueva | ⏳ Pendiente | — | Sí (delegable) | Baja; docs oficiales + validaciones |

## Reglas de paso

- Cada fase abre SESIÓN NUEVA (R1) y lee su `05-prompt-inicio-sesion-fase-*.md`.
- FASE-VERIFY exige A+B+C+D ✅; FASE-RELEASE exige VERIFY ✅.
- Fase agotada (60 iteraciones) → ⏳ INCOMPLETA con checkpoint en `dependencias-fases.md`; se retoma en sesión fresca sin re-ejecutar lo completado.

## Estado del proyecto: ⏳ EN EJECUCIÓN — FASE-A ✅, FASE-B ✅, FASE-C ✅, FASE-D ✅ 2026-08-31; siguiente: FASE-VERIFY
