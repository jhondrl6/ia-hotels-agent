# Checklist de Implementación — VALIDADOR-URL-PROPIA-2026-08-30

| # | Fase | Sesión | Estado | Fecha | delegate_task | Notas |
|---|------|--------|--------|-------|---------------|-------|
| 0 | Preparación | 2026-08-30 | ✅ Completada | 2026-08-30 | No | Plan + 6 prompts + docs base; Paso 0 (memoria + QMind) ejecutado |
| 1 | FASE-A — Núcleo del guard (TDD) | nueva | ⏳ Pendiente | — | No (DIRECTO) | Media; contratos antes del fix; 28 canonicalización verdes |
| 2 | FASE-B — Superficies secundarias | nueva | ⏳ Pendiente | — | Sí (2 subagentes) | Baja-Media; modos + last_url + hook-pdf + capa datos |
| 3 | FASE-C — Verificación empírica Don Julio | nueva | ⏳ Pendiente | — | Sí | Baja; probes P1-P11 + regresión |
| 4 | FASE-D — E2E v4complete Salento Real | nueva | ⏳ Pendiente | — | Mixto (comando delegado) | Baja; única corrida del plan; evidencia-first |
| 5 | FASE-VERIFY — Certificación AC1-AC8 | nueva | ⏳ Pendiente | — | No (DIRECTO §4.6) | Baja-Media; sin código, sin v4complete |
| 6 | FASE-RELEASE-4.74.0 | nueva | ⏳ Pendiente | — | Sí (delegable) | Baja; docs oficiales + validaciones |

## Reglas de paso

- Cada fase abre SESIÓN NUEVA (R1) y lee su `05-prompt-inicio-sesion-fase-*.md`.
- FASE-VERIFY exige A+B+C+D ✅; FASE-RELEASE exige VERIFY ✅.
- Fase agotada (60 iteraciones) → ⏳ INCOMPLETA con checkpoint en `dependencias-fases.md`; se retoma en sesión fresca sin re-ejecutar lo completado.

## Estado del proyecto: ⏳ EN EJECUCIÓN — siguiente: FASE-A
