# Checklist de Implementación — CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15

> Regla R1 del executor: **una fase por sesión, sin excepciones.** `FASE-RELEASE-4.81.1` requiere TODAS las previas en ✅.

| # | Fase | Tipo | Complejidad | Modo de ejecución | Dependencias | Estado |
|---|------|------|-------------|-------------------|--------------|--------|
| 0 | Preparación (Paso 0 + maestro + prompts) | Orquestación | Media | DIRECTO (sesión del 2026-10-15) | — | ✅ Completada 2026-10-15 |
| 1 | FASE-A — Cierre documental de la tanda (commits `D-QW` + crudos + acta) | Cierre documental | Baja | DIRECTO | Preparación | ✅ Completada 2026-10-21 (crudos `77dea21`, hook 8/8; ver acta FASE-A) |
| 2 | FASE-B — Censo era-G + decisión por fuente (Operador en el bucle) | Investigación | Media | DIRECTO | FASE-A ✅ | ✅ Completada 2026-10-22 (censo + decisiones en `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-B/censo-era-g.md`; decisión (a) en las 5 fuentes) |
| 3 | FASE-C — Cura era-G (mecanismo decidido; única fase que puede tocar código) | Implementación | Media | DIRECTO | FASE-B ✅ | ✅ Completada 2026-10-22 (`registrar_historica()` + `--mark-historic`, 4 dientes con rojo-antes y mutante, delta 63→67; 5 marcas por el writer; AC5 0/0 en la corrida real; `S-SEC-1` definida en §5 del maestro; quick 13/13) |
| 4 | FASE-RELEASE-4.81.1 — Cierre + write-back + archivado | Cierre | Baja | DIRECTO | FASE-C ✅ | ✅ Completada 2026-10-22 (bump 4.81.1 sincronizado; CHANGELOG con las tres curas y los shas `2e048e6`/`1f95e84`; nota de ronda +13 atribuida contra revisiones fijas (5.321 → 5.330 → 5.334) con cabecera y fila de `AGENTS.md` movidas; GUIA_TECNICA; SYSTEM_STATUS y DOMAIN_PRIMER regenerado por el bump (crudo `03-`: sin eso el quick cae 12/13) y verificado con `--context`; quick 13/13 y modo completo 16/18 con `PYTHONUTF8=1` con sus dos rojos dueñados; cierre R2.5/R2.10 en orden: write-back (`--strict` `[FRESCO]`, 0 huéspedes sobre 9/9) → índice → `git mv` a `Archives/` (11 renombres) → índice → refs `--fix` → citas `--update-baseline` → quick. **Plan CERRADO**, sin commit (letra del Operador) |

## Notas de dependencia

- FASE-B **no cura**: su producto es el censo y la tabla de decisión del Operador. FASE-C no arranca sin esa tabla (si falta una decisión por fuente, FASE-B cierra `⏳ INCOMPLETA` con checkpoint).
- El redondeo de versión es **uno solo** (4.81.1) y cubre las tres curas (DEC-1): el CHANGELOG no publica la segunda vía por separado, aunque sus commits (`2e048e6`, `1f95e84`) ya estén empujados.
- FASE-VERIFY **no aplica** (criterios §4.6 evaluados en el maestro §3): sin E2E y con una sola fase que puede tocar código.
- El `10-analisis` de CURA está congelado (DEC-2) y los dos CONTEXT publicados también (DEC-3): ninguna fase los edita.

## Recuperación

- Fase agotada → `⏳ INCOMPLETA` con checkpoint en esta tabla y en `dependencias-fases.md`; evidencia parcial en `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-*/`; la sesión nueva retoma desde el checkpoint sin re-ejecutar lo ya correcto.
- El crudo del rojo-antes de FASE-B es insumo de AC5: si se pierde, se re-corre el writer antes de curar (el rojo tiene que estar capturado ANTES del cambio, R2.8).
