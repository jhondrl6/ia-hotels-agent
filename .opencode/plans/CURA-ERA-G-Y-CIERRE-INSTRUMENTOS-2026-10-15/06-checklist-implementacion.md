# Checklist de Implementación — CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15

> Regla R1 del executor: **una fase por sesión, sin excepciones.** `FASE-RELEASE-4.81.1` requiere TODAS las previas en ✅.

| # | Fase | Tipo | Complejidad | Modo de ejecución | Dependencias | Estado |
|---|------|------|-------------|-------------------|--------------|--------|
| 0 | Preparación (Paso 0 + maestro + prompts) | Orquestación | Media | DIRECTO (sesión del 2026-10-15) | — | ✅ Completada 2026-10-15 |
| 1 | FASE-A — Cierre documental de la tanda (commits `D-QW` + crudos + acta) | Cierre documental | Baja | DIRECTO | Preparación | ✅ Completada 2026-10-21 (crudos `77dea21`, hook 8/8; ver acta FASE-A) |
| 2 | FASE-B — Censo era-G + decisión por fuente (Operador en el bucle) | Investigación | Media | DIRECTO | FASE-A ✅ | ⬜ Pendiente |
| 3 | FASE-C — Cura era-G (mecanismo decidido; única fase que puede tocar código) | Implementación | Media | DIRECTO | FASE-B ✅ | ⬜ Pendiente |
| 4 | FASE-RELEASE-4.81.1 — Cierre + write-back + archivado | Cierre | Baja | DIRECTO | FASE-C ✅ | ⬜ Pendiente |

## Notas de dependencia

- FASE-B **no cura**: su producto es el censo y la tabla de decisión del Operador. FASE-C no arranca sin esa tabla (si falta una decisión por fuente, FASE-B cierra `⏳ INCOMPLETA` con checkpoint).
- El redondeo de versión es **uno solo** (4.81.1) y cubre las tres curas (DEC-1): el CHANGELOG no publica la segunda vía por separado, aunque sus commits (`2e048e6`, `1f95e84`) ya estén empujados.
- FASE-VERIFY **no aplica** (criterios §4.6 evaluados en el maestro §3): sin E2E y con una sola fase que puede tocar código.
- El `10-analisis` de CURA está congelado (DEC-2) y los dos CONTEXT publicados también (DEC-3): ninguna fase los edita.

## Recuperación

- Fase agotada → `⏳ INCOMPLETA` con checkpoint en esta tabla y en `dependencias-fases.md`; evidencia parcial en `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-*/`; la sesión nueva retoma desde el checkpoint sin re-ejecutar lo ya correcto.
- El crudo del rojo-antes de FASE-B es insumo de AC5: si se pierde, se re-corre el writer antes de curar (el rojo tiene que estar capturado ANTES del cambio, R2.8).
