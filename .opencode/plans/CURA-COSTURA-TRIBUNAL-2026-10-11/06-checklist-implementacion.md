# Checklist de Implementación — CURA-COSTURA-TRIBUNAL-2026-10-11

> Regla R1 del executor: **una fase por sesión, sin excepciones.** `FASE-RELEASE-4.81.0` requiere TODAS las previas en ✅.

| # | Fase | Tipo | Complejidad | Modo de ejecución | Dependencias | Estado |
|---|------|------|-------------|-------------------|--------------|--------|
| 0 | Preparación (Paso 0 + maestro + prompts) | Orquestación | Media | DIRECTO (esta sesión) | — | ✅ Completada 2026-10-11 |
| 0b | Preparación-2 — auditoría del plan aplicada sobre el código vivo y los artefactos reales (sin código) | Orquestación | Media | DIRECTO | Preparación | ✅ Completada 2026-10-11 — 6 bloqueantes + 9 de diseño; rename `JEV-`→`CURA-`, AC13 partida con `S-CST-1`, ACs 1/4/5/10/11/13/14 re-enunciadas, AC17 y AC18 nuevas, FASE-B reordenada, T0 de E2E por YAML derivado, L-T4A.2 capitalizada |
| 1 | FASE-A — Contrato 4 estados + cache versionada + recibo | Implementación | Alta | DIRECTO (no delegable: decisión arquitectónica DEC-A1) | Preparación | ✅ Completada 2026-10-11 **sin commit** — AC2..7 legibles en `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-A/` (mutation check AC2 con par rojo/verde, +46 funciones de test, quick 13/13). **AC1 se certifica en FASE-B junto con AC15** (DEC-A1 deja el wrapper mapeando no-OK → `[]`). DEC-A5 nueva (techo `max_tokens` 2000→4000) y `L-CST-1`/`L-CST-2` en `10-analisis`. Presupuesto excedido: ~62 tool calls contra ~55 |
| 2 | FASE-B — Bot 2/Bot 4 + N5 + N7 + wrapper fuera; **orden interno T3→T2→T1→T4** | Implementación | Alta | DIRECTO | FASE-A ✅ | ✅ Completada 2026-10-11 **sin commit** — orden ejecutado tal cual (T3→T2→T1→T4). AC8/9/10/15/17/18 legibles en `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-B/`; **AC1 se cierra aquí con AC15**. Delta R2.3 +27 (5253→5280); tribunal 277 passed / 9 skipped; quick 13/13. Presupuesto EXCEDIDO: ~80 tool calls contra ~55 (≈45 %; unidad auto-reportada, sin instrumento que la mida) |
| 3 | FASE-C — Juez/tier + P6.2 + N8 (cuatro sitios del motor) | Implementación | Media-Alta | DIRECTO | FASE-B ✅ (comparte honesty_reviewer.py) | ✅ Completada 2026-10-12 **sin commit** — AC11/12/13 legibles en `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-C/` (módulo nuevo `evidence_tier.py`, tres mutantes con par rojo/verde, delta R2.3 **+29** con cero re-anclajes, quick 13/13). Quedan escaladas al Operador: la regla «`INPUT_NOT_EVALUABLE` no suprime el ZIP» (sin AC en este plan) y `_extract_precision_tier` (fuera de AC11). Presupuesto EXCEDIDO: ~52 tool calls contra ~45 |
| 3b | FASE-C2 — AC19: el CRITICAL verificado bloquea aunque el insumo sea no-OK (**fase nueva por decisión del Operador 2026-10-12**) | Implementación | Media | DIRECTO (**sin subagente**: costura compartida entre veredicto y acciones correctivas; evaluado y descartado en su prompt) | FASE-C ✅ (misma costura, `outcome.py`/`judge.py`) | ⬜ Pendiente — corre en sesión nueva **antes de FASE-E2E** |
| 4 | FASE-E2E — Run único v4complete Don Alfonso (onboarding por YAML derivado) | Ejecución E2E | Media | **Subagente** para el run (delegate_task, timeout 900); parent para pre-vuelo/evidencia/docs | FASE-A, FASE-B, FASE-C | ⬜ Pendiente |
| 5 | FASE-VERIFY — Certificación AC1..18 contra output E2E | Verificación | Media | DIRECTO (no delegable §4.6; sin código, sin v4complete) | Todas las anteriores | ⬜ Pendiente |
| 6 | FASE-RELEASE-4.81.0 — Cierre + write-back + archivado | Cierre | Baja | Delegable a subagente (TIP del executor) | FASE-VERIFY ✅ | ⬜ Pendiente |

**Sello de publicación (2026-10-12)**: las celdas «**sin commit**» de las filas 1-3 registran el corte declarado al cerrar cada fase, no el estado del árbol. Estado medido con `git log`: FASE-A `5ed960a`+`af508cd` (empujada), FASE-B `bf5ab2e`+`4df81d3` (empujada), **FASE-C `079f475`**. FASE-C2 sigue pendiente de ejecución.

**Sello de la segunda tanda (2026-10-12)**: la última frase de arriba quedó **vencida por la propia ejecución**. FASE-C2 se ejecutó ese mismo día y se commiteó en `fa4c93e` (28 archivos, hook 8/8 verde, `git grep -c -E "^\s*def test_" HEAD -- tests` = 5321 reproducido en el árbol del commit). El tip publicado es el que imprime `git ls-remote` al leer esta línea, no el que ella estampa.

## Notas de dependencia

- La secuencia A→B→C es obligatoria: `honesty_reviewer.py` se edita en B (estados, N5, N7, AC18) y en C (N6).
- Dentro de FASE-B el orden de ejecución es **T3→T2→T1→T4** (las tareas no se renumeran): ajustar el patrón de CRITICAL antes de encender el texto completo evita un hallazgo espurio que suprimiría el ZIP de la corrida única.
- El run único de v4complete ocurre SOLO en FASE-E2E (mandato del operador); VERIFY no ejecuta comandos largos.
- FASE-VERIFY incluida por criterios de activación §4.6 (4 fases impl + E2E + ACs cross-fase AC1..18).

## Recuperación

- Fase agotada → `⏳ INCOMPLETA` con checkpoint en esta tabla y en `dependencias-fases.md`; evidencia parcial en `evidence/FASE-*/`; sesión nueva retoma desde el checkpoint sin re-ejecutar lo ya correcto.
- El run de FASE-E2E es único: si un escenario exige una segunda corrida, parar y consultar al operador.
