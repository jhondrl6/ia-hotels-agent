# Checklist de Implementación — CURA-COSTURA-TRIBUNAL-2026-10-11

> Regla R1 del executor: **una fase por sesión, sin excepciones.** `FASE-RELEASE-4.81.0` requiere TODAS las previas en ✅.

| # | Fase | Tipo | Complejidad | Modo de ejecución | Dependencias | Estado |
|---|------|------|-------------|-------------------|--------------|--------|
| 0 | Preparación (Paso 0 + maestro + prompts) | Orquestación | Media | DIRECTO (esta sesión) | — | ✅ Completada 2026-10-11 |
| 0b | Preparación-2 — auditoría del plan aplicada sobre el código vivo y los artefactos reales (sin código) | Orquestación | Media | DIRECTO | Preparación | ✅ Completada 2026-10-11 — 6 bloqueantes + 9 de diseño; rename `JEV-`→`CURA-`, AC13 partida con `S-CST-1`, ACs 1/4/5/10/11/13/14 re-enunciadas, AC17 y AC18 nuevas, FASE-B reordenada, T0 de E2E por YAML derivado, L-T4A.2 capitalizada |
| 1 | FASE-A — Contrato 4 estados + cache versionada + recibo | Implementación | Alta | DIRECTO (no delegable: decisión arquitectónica DEC-A1) | Preparación | ✅ Completada 2026-10-11 **sin commit** — AC2..7 legibles en `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-A/` (mutation check AC2 con par rojo/verde, +46 funciones de test, quick 13/13). **AC1 se certifica en FASE-B junto con AC15** (DEC-A1 deja el wrapper mapeando no-OK → `[]`). DEC-A5 nueva (techo `max_tokens` 2000→4000) y `L-CST-1`/`L-CST-2` en `10-analisis`. Presupuesto excedido: ~62 tool calls contra ~55 |
| 2 | FASE-B — Bot 2/Bot 4 + N5 + N7 + wrapper fuera; **orden interno T3→T2→T1→T4** | Implementación | Alta | DIRECTO | FASE-A ✅ (desbloqueada) | ⬜ Pendiente |
| 3 | FASE-C — Juez/tier + P6.2 + N8 (cuatro sitios del motor) | Implementación | Media-Alta | DIRECTO | FASE-B (comparte honesty_reviewer.py) | ⬜ Pendiente |
| 4 | FASE-E2E — Run único v4complete Don Alfonso (onboarding por YAML derivado) | Ejecución E2E | Media | **Subagente** para el run (delegate_task, timeout 900); parent para pre-vuelo/evidencia/docs | FASE-A, FASE-B, FASE-C | ⬜ Pendiente |
| 5 | FASE-VERIFY — Certificación AC1..18 contra output E2E | Verificación | Media | DIRECTO (no delegable §4.6; sin código, sin v4complete) | Todas las anteriores | ⬜ Pendiente |
| 6 | FASE-RELEASE-4.81.0 — Cierre + write-back + archivado | Cierre | Baja | Delegable a subagente (TIP del executor) | FASE-VERIFY ✅ | ⬜ Pendiente |

## Notas de dependencia

- La secuencia A→B→C es obligatoria: `honesty_reviewer.py` se edita en B (estados, N5, N7, AC18) y en C (N6).
- Dentro de FASE-B el orden de ejecución es **T3→T2→T1→T4** (las tareas no se renumeran): ajustar el patrón de CRITICAL antes de encender el texto completo evita un hallazgo espurio que suprimiría el ZIP de la corrida única.
- El run único de v4complete ocurre SOLO en FASE-E2E (mandato del operador); VERIFY no ejecuta comandos largos.
- FASE-VERIFY incluida por criterios de activación §4.6 (4 fases impl + E2E + ACs cross-fase AC1..18).

## Recuperación

- Fase agotada → `⏳ INCOMPLETA` con checkpoint en esta tabla y en `dependencias-fases.md`; evidencia parcial en `evidence/FASE-*/`; sesión nueva retoma desde el checkpoint sin re-ejecutar lo ya correcto.
- El run de FASE-E2E es único: si un escenario exige una segunda corrida, parar y consultar al operador.
