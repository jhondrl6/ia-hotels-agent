# Checklist de Implementación — VALIDADOR-URL-PROPIA-2026-08-30

| # | Fase | Sesión | Estado | Fecha | delegate_task | Notas |
|---|------|--------|--------|-------|---------------|-------|
| 0 | Preparación | 2026-08-30 | ✅ Completada | 2026-08-30 | No | Plan + 6 prompts + docs base; Paso 0 (memoria + QMind) ejecutado |
| 1 | FASE-A — Núcleo del guard (TDD) | 2026-08-30 | ✅ Completada | 2026-08-30 | No (DIRECTO) | Contratos rojos→verdes 45/45; 28/28 canonicalización; baseline 14 fallos preexistentes (sin nuevos); validaciones 7/7; smoke CLI exit 2 |
| 2 | FASE-B — Superficies secundarias | nueva | ⏳ Pendiente | — | Sí (2 subagentes) | Baja-Media; modos + last_url + hook-pdf + capa datos |
| 3 | FASE-C — Verificación empírica Don Julio | nueva | ⏳ Pendiente | — | Sí | Baja; probes P1-P11 + regresión |
| 4 | FASE-D — E2E v4complete Salento Real | nueva | ⏳ Pendiente | — | Mixto (comando delegado) | Baja; única corrida del plan; evidencia-first |
| 5 | FASE-VERIFY — Certificación AC1-AC8 | nueva | ⏳ Pendiente | — | No (DIRECTO §4.6) | Baja-Media; sin código, sin v4complete |
| 6 | FASE-RELEASE-4.74.0 | nueva | ⏳ Pendiente | — | Sí (delegable) | Baja; docs oficiales + validaciones |

## Reglas de paso

- Cada fase abre SESIÓN NUEVA (R1) y lee su `05-prompt-inicio-sesion-fase-*.md`.
- FASE-VERIFY exige A+B+C+D ✅; FASE-RELEASE exige VERIFY ✅.
- Fase agotada (60 iteraciones) → ⏳ INCOMPLETA con checkpoint en `dependencias-fases.md`; se retoma en sesión fresca sin re-ejecutar lo completado.

## Estado del proyecto: ⏳ EN EJECUCIÓN — FASE-A ✅ 2026-08-30; siguiente: FASE-B
