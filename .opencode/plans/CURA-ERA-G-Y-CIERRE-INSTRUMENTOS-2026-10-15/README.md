# CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15

> Cierra en un solo ciclo los dos cabos que dejó la tanda de instrumentos del 2026-10-15: el **cierre documental** (las 4 rutas del registro `D-QW-1`/`D-QW-2` sin commitear, los crudos en `temp/`, ninguna acta) y la **deuda era-G** que mantiene el modo completo en rojo (`[DUPLICADO-VIGENTE]` sobre 5 fuentes de 2 planes + 5 huéspedes sin contabilidad). Versión objetivo: **4.81.1**, una sola unidad que cubre las tres curas (DEC-1).

## Estado

| Fase | Estado |
|------|--------|
| Preparación (Paso 0 + maestro + prompts) | ✅ 2026-10-15 |
| FASE-A — Cierre documental (commits `D-QW` + crudos + acta) | ⬜ Pendiente |
| FASE-B — Censo era-G + decisión por fuente | ⬜ Pendiente |
| FASE-C — Cura era-G | ⬜ Pendiente |
| FASE-RELEASE-4.81.1 — Cierre + write-back + archivado | ⬜ Pendiente |

## Cabos que este plan cierra

1. **El registro `D-QW` está sin commitear** (contexto raíz + crudo `14-` + par del índice regenerado) y los crudos de la tanda viven en `temp/` (gitignored). → FASE-A. **Vencido en su primera mitad el 2026-10-15**: el registro quedó versionado en `85ab952`; los crudos de `temp/` siguen sin persistir, así que el cabo lo conserva FASE-A.
2. **La deuda era-G no tiene censo ni decisiones**: 5 fuentes publicadas antes de que existiera la marca de reemplazo, y 5 huéspedes sin contabilidad. Resolverlo exige la decisión escrita del Operador por fuente (borrar es irreversible). → FASE-B + FASE-C.
3. **No hay entrada de versión** para la tanda ya empujada (`2e048e6`, `1f95e84`): el CHANGELOG la publica junto a era-G en 4.81.1. → FASE-RELEASE.

## Referencias

- Maestro: `01-plan-maestro.md` (§1 AC1..AC7, §4 decisiones DEC-1..DEC-5, §5 deudas diferidas).
- Paso 0: `00-lecciones-capitalizadas.md` (§1 consultas re-ejecutables, §2 lecciones, §3 descartes).
- Prompts: `05-prompt-inicio-sesion-fase-A.md`, `-fase-B.md`, `-fase-C.md`, `-fase-RELEASE.md`.
- Contexto del hallazgo de origen: `.opencode/context/CONTEXT-DEUDAS-WRITER-QMIND-2026-10-15.md` (define `D-QW-1`/`D-QW-2`) y `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-RELEASE/13-segunda-via-ciega.txt` (la segunda vía, ya curada).
- Evidencia del plan: `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/`.

## Cómo se ejecuta

Una fase por sesión (R1): abrir sesión nueva con el prompt de la fase (`05-prompt-inicio-sesion-fase-*.md`), que declara sus tareas, tests, post-ejecución y restricciones. Ningún prompt autoriza commit por sí mismo: cada commit/push requiere la autorización escrita del Operador en la sesión.
