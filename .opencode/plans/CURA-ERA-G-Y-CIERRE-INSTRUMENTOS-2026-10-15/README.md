# CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15

> Cierra en un solo ciclo los dos cabos que dejó la tanda de instrumentos del 2026-10-15: el **cierre documental** (las 4 rutas del registro `D-QW-1`/`D-QW-2` sin commitear, los crudos en `temp/`, ninguna acta) y la **deuda era-G** que mantiene el modo completo en rojo (`[DUPLICADO-VIGENTE]` sobre 5 fuentes de 2 planes + 5 huéspedes sin contabilidad). Versión objetivo: **4.81.1**, una sola unidad que cubre las tres curas (DEC-1).

## Estado

| Fase | Estado |
|------|--------|
| Preparación (Paso 0 + maestro + prompts) | ✅ 2026-10-15 |
| FASE-A — Cierre documental (commits `D-QW` + crudos + acta) | ✅ 2026-10-21 — crudos `15-`…`26-` en `77dea21` (12 rutas, hook 8/8); registro `D-QW` ya en `85ab952`; acta y post-ejecución en el commit `docs(plan)` de la sesión. Sin push (Operador) |
| FASE-B — Censo era-G + decisión por fuente | ✅ 2026-10-22 — censo + decisiones en `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-B/censo-era-g.md` (5 fuentes censadas, cruce de poblaciones 5/5 idéntico, decisión (a) «marcar como reemplazada» del Operador en las 5; métricas y crudos por referencia al censo). Sin commit (Operador) |
| FASE-C — Cura era-G | ⬜ Pendiente |
| FASE-RELEASE-4.81.1 — Cierre + write-back + archivado | ⬜ Pendiente |

## Cabos que este plan cierra

1. **El registro `D-QW` está sin commitear** (contexto raíz + crudo `14-` + par del índice regenerado) y los crudos de la tanda viven en `temp/` (gitignored). → FASE-A. **Vencido en su primera mitad el 2026-10-15**: el registro quedó versionado en `85ab952`. **Cerrado del todo el 2026-10-21**: los 12 crudos de `temp/` quedaron versionados en `77dea21`, con sus shas de blob y disco en el acta (métricas por referencia: `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-A/acta-cierre-documental.md`).
2. **La deuda era-G no tiene censo ni decisiones**: 5 fuentes publicadas antes de que existiera la marca de reemplazo, y 5 huéspedes sin contabilidad. Resolverlo exige la decisión escrita del Operador por fuente (borrar es irreversible). → FASE-B + FASE-C. **Censada y decidida el 2026-10-22** (FASE-B): el censo mide cruce 5/5 (el rojo `[DUPLICADO-VIGENTE]` y el contador de huéspedes son la misma población) y el Operador decidió (a) «marcar como reemplazada» para las 5 — métricas por referencia al censo (§2 y §5 de `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-B/censo-era-g.md`); la cura queda para FASE-C.
3. **No hay entrada de versión** para la tanda ya empujada (`2e048e6`, `1f95e84`): el CHANGELOG la publica junto a era-G en 4.81.1. → FASE-RELEASE.

## Referencias

- Maestro: `01-plan-maestro.md` (§1 AC1..AC7, §4 decisiones DEC-1..DEC-5, §5 deudas diferidas).
- Paso 0: `00-lecciones-capitalizadas.md` (§1 consultas re-ejecutables, §2 lecciones, §3 descartes).
- Prompts: `05-prompt-inicio-sesion-fase-A.md`, `-fase-B.md`, `-fase-C.md`, `-fase-RELEASE.md`.
- Contexto del hallazgo de origen: `.opencode/context/CONTEXT-DEUDAS-WRITER-QMIND-2026-10-15.md` (define `D-QW-1`/`D-QW-2`) y `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-RELEASE/13-segunda-via-ciega.txt` (la segunda vía, ya curada).
- Evidencia del plan: `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/`.
- Acta del cierre documental (FASE-A): `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-A/acta-cierre-documental.md` (shas de blob y disco, verdes re-ejecutados, frontera con FASE-B).

## Cómo se ejecuta

Una fase por sesión (R1): abrir sesión nueva con el prompt de la fase (`05-prompt-inicio-sesion-fase-*.md`), que declara sus tareas, tests, post-ejecución y restricciones. Ningún prompt autoriza commit por sí mismo: cada commit/push requiere la autorización escrita del Operador en la sesión.
