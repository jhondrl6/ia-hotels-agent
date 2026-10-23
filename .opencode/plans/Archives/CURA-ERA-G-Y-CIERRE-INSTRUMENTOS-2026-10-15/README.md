# CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15

> Cierra en un solo ciclo los dos cabos que dejó la tanda de instrumentos del 2026-10-15: el **cierre documental** (las 4 rutas del registro `D-QW-1`/`D-QW-2` sin commitear, los crudos en `temp/`, ninguna acta) y la **deuda era-G** que mantiene el modo completo en rojo (`[DUPLICADO-VIGENTE]` sobre 5 fuentes de 2 planes + 5 huéspedes sin contabilidad). Versión objetivo: **4.81.1**, una sola unidad que cubre las tres curas (DEC-1).

## Estado

| Fase | Estado |
|------|--------|
| Preparación (Paso 0 + maestro + prompts) | ✅ 2026-10-15 |
| FASE-A — Cierre documental (commits `D-QW` + crudos + acta) | ✅ 2026-10-21 — crudos `15-`…`26-` en `77dea21` (12 rutas, hook 8/8); registro `D-QW` ya en `85ab952`; acta y post-ejecución en el commit `docs(plan)` de la sesión. Sin push (Operador) |
| FASE-B — Censo era-G + decisión por fuente | ✅ 2026-10-22 — censo + decisiones en `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-B/censo-era-g.md` (5 fuentes censadas, cruce de poblaciones 5/5 idéntico, decisión (a) «marcar como reemplazada» del Operador en las 5; métricas y crudos por referencia al censo). Sin commit (Operador) |
| FASE-C — Cura era-G | ✅ 2026-10-22 — mecanismo (a) ejecutado: primitivo `registrar_historica()` + `--mark-historic` con 4 dientes (rojo-antes, verde, mutante del guard, delta 63→67); las 5 fuentes marcadas `reemplazada` **por el writer** (registro 9→14, 8 vigentes intactas); AC5 en la corrida real: 0 `[DUPLICADO-VIGENTE]`, `0 fuente(s) huesped(s)` sobre 8/8 (racha dirigida de 3 intentos); `S-SEC-1` definida en §5 (T4); quick 13/13. Métricas por referencia: `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-C/`. Sin commit (Operador) |
| FASE-RELEASE-4.81.1 — Cierre + write-back + archivado | ✅ 2026-10-22 — **plan CERRADO** (4.81.1 publicado en `CHANGELOG`, nota de ronda +13, write-back `[FRESCO]` y plan bajo `Archives/`; sin commit, a la espera de la letra del Operador) |

## Cabos que este plan cierra

1. **El registro `D-QW` está sin commitear** (contexto raíz + crudo `14-` + par del índice regenerado) y los crudos de la tanda viven en `temp/` (gitignored). → FASE-A. **Vencido en su primera mitad el 2026-10-15**: el registro quedó versionado en `85ab952`. **Cerrado del todo el 2026-10-21**: los 12 crudos de `temp/` quedaron versionados en `77dea21`, con sus shas de blob y disco en el acta (métricas por referencia: `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-A/acta-cierre-documental.md`).
2. **La deuda era-G no tiene censo ni decisiones**: 5 fuentes publicadas antes de que existiera la marca de reemplazo, y 5 huéspedes sin contabilidad. Resolverlo exige la decisión escrita del Operador por fuente (borrar es irreversible). → FASE-B + FASE-C. **Censada y decidida el 2026-10-22** (FASE-B): el censo mide cruce 5/5 (el rojo `[DUPLICADO-VIGENTE]` y el contador de huéspedes son la misma población) y el Operador decidió (a) «marcar como reemplazada» para las 5 — métricas por referencia al censo (§2 y §5 de `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-B/censo-era-g.md`). **Curada el 2026-10-22** (FASE-C): las 5 marcas `reemplazada` escritas por el writer con su primitivo nuevo y sus dientes; la corrida real sale sin `[DUPLICADO-VIGENTE]` y con `0 fuente(s) huesped(s)` (par rojo/verde en evidence).
3. **No hay entrada de versión** para la tanda ya empujada (`2e048e6`, `1f95e84`): el CHANGELOG la publica junto a era-G en 4.81.1. → FASE-RELEASE. **Cerrado el 2026-10-22**: la entrada `## [4.81.1]` del `CHANGELOG.md` publica las tres curas y nombra esos dos shas; `VERSION.yaml` queda en 4.81.1 y el sync estampa la versión en los seis encabezados gobernados.

## Referencias

- Maestro: `01-plan-maestro.md` (§1 AC1..AC7, §4 decisiones DEC-1..DEC-5, §5 deudas diferidas).
- Paso 0: `00-lecciones-capitalizadas.md` (§1 consultas re-ejecutables, §2 lecciones, §3 descartes).
- Prompts: `05-prompt-inicio-sesion-fase-A.md`, `-fase-B.md`, `-fase-C.md`, `-fase-RELEASE.md`.
- Contexto del hallazgo de origen: `.opencode/context/CONTEXT-DEUDAS-WRITER-QMIND-2026-10-15.md` (define `D-QW-1`/`D-QW-2`) y `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-RELEASE/13-segunda-via-ciega.txt` (la segunda vía, ya curada).
- Evidencia del plan: `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/`.
- Acta del cierre documental (FASE-A): `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-A/acta-cierre-documental.md` (shas de blob y disco, verdes re-ejecutados, frontera con FASE-B).

## Cómo se ejecuta

Una fase por sesión (R1): abrir sesión nueva con el prompt de la fase (`05-prompt-inicio-sesion-fase-*.md`), que declara sus tareas, tests, post-ejecución y restricciones. Ningún prompt autoriza commit por sí mismo: cada commit/push requiere la autorización escrita del Operador en la sesión.

## Sello de la tanda de publicación (2026-10-22)

**Fuente única del sello.** Las celdas de las tablas de arriba y de `dependencias-fases.md` y `06-checklist-implementacion.md` que decían «sin commit» **no se re-escriben**: registran el corte declarado al cerrar cada fase. Lo que mide `git log` se estampa aquí, en tiempo pasado, y los otros dos documentos apuntan a esta sección.

- El cierre del plan quedó commiteado en `651efd2` (padre `2e4ba97`): **51 rutas** — 38 contadas por `git diff --name-only --no-renames HEAD~1 HEAD`, con los 11 renombres del archivado en sus dos mitades, más 13 entradas nuevas (12 crudos `01-`…`11-` y la instantánea del write-back) —, 898 inserciones / 109 borrados.
- Ese commit se empujó después de una revisión de seguridad profunda con `findings_count: 0` (corrida directa antes del push, rango medido `2e4ba97..651efd2` = 1 commit). Fast-forward, paridad `0 0` y puntero remoto `651efd286cfd51a20d0ba0c8f60e50d9c2171f9e` casando con el local.
- El primer intento de ese commit (`ab95b78`) quedó fuera de la rama: su pathspec nombró la mitad **nueva** de los renombres y no la vieja, así que el árbol commiteado duplicaba el plan y dejaba 11 borrados colgando del índice. Como no estaba publicado, se rehizo con `git reset --soft` y un solo commit con **ambas** mitades, por decisión escrita del Operador en la sesión.
- El push de `651efd2` publicó de paso un rojo de instrumento, nacido del propio archivado: al mover este plan a `Archives/`, sus citas con prefijo al contexto de las deudas del writer metieron a ese contexto en la población **gobernada** por la segunda vía (`declara_durable()` = False, o sea que lo gobierna la cita, no la declaración), y el contexto nunca se publicó en el notebook → `[VENCIDO]` con `[FAIL] … 1 fresco(s), 4 problema(s)` y `EXIT 1`. El `--quick` no lo mira: cortaba en modo completo.
- Se cerró el mismo día en `32cd77c` (padre `651efd2`, **2 rutas**): el contexto pasó a `Historico/` con `git mv` de bytes intactos (`R100`; sha256 `864e1c623f43…` igual antes y después) y las 5 roturas absorbidas en `.opencode/refs_baseline.txt` — **4 entradas agregadas / 0 borradas**, porque la clave es el par `archivo|referencia` — escritas con `--write-baseline` y **nunca `--fix`** (el hook lo corre solo y habría reescrito documentos archivados). Tras la mudanza la corrida dicta `1 gobernado(s) … 1 fresco(s), 0 problema(s)`; el `EXIT 2` que queda es la abstención de siempre por descarga flaqueante, con dueño y racha declarados. Su push también fue posterior a una revisión sin hallazgos: fast-forward `651efd2..32cd77c`, paridad `0 0`, remoto `32cd77c8108e483005aa0584889a3067c6bed504`.
- No se abre un sello para anotar que este sello fue revisado (corta-bucles): la cobertura de cada revisión se enuncia en la tanda, y el puntero publicado es el que imprime `git ls-remote` al leer esto.
- Lo normativo no cambia: ningún prompt de este plan autoriza commit por sí mismo, la letra del Operador manda y el pathspec es obligatorio. Quedan **diferidas con dueño Operador**: las dos deudas del writer (definidas ahora bajo `Historico/`, con sus citas del plan archivado apuntando a la ruta vieja por baseline y la caída de la segunda vía en silencio), la deuda del gate de secretos (fix fail-closed en fase propia) y la de la invocación sin `--strict`.
