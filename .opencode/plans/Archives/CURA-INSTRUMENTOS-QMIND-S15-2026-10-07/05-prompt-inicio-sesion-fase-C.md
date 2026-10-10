# FASE-C — Cura en el generador, si y solo si AC7 la exige (AC9, condicional)

**ID:** CURA-INSTRUMENTOS-QMIND-S15 / FASE-C
**Objetivo:** si —y solo si— el diagnóstico de FASE-B concluye que la divergencia no se gobierna desde el test,
cambiar `scripts/build_lesson_index.py` como **código de producto**, con su AC, su mutación y sus baterías.
**Dependencias:** FASE-B cerrada con AC7 publicado y con la fila «la cura está en el generador» escrita en
`dependencias-fases.md`. **Si B no abrió esta fase, C no se ejecuta y se declara en el checklist** —no es una fase
de relleno.
**Complejidad:** ALTA. El generador alimenta `[6/8]` del hook (cada commit), el corpus consultable por el Paso 0 de
todos los planes futuros y la línea `[fechas]` que es la prueba de la cura de 2026-09-26.
**Skill:** `.agents/workflows/phased_project_executor.md`.
**Modo:** DIRECTO. **R3:** 4 tareas, 0 comandos largos.

## Contexto

El estado vigente del generador, recuperado del corpus y re-validado por símbolo en la preparación: `_plan_date`
resuelve en cascada `nombre` (fecha en el nombre del plan) → `commit` (fecha `%aI` del último commit que tocó el
documento, recortada a 10 caracteres) → `SIN-FUENTE` (`0000-00-00`), y `build()` ordena a los dueños por
`(fuente, fecha, plan)`. `mtime` fue **retirado** de la lista de fuentes admitidas, no rebajado. Dos límites
declarados entonces y **no curados** son los que esta fase puede tocar: el desempate por nombre si un `git mv`
masivo de `Historico/` colapsa las fechas del tier `commit`, y el hecho de que «el último commit que tocó un
archivo» **no** es la fecha en que se escribió.

**Nada de esto es premisa de la fase:** FASE-B trae la medición; C ejecuta la consecuencia. Si C descubre que B
se equivocó de corte, se vuelve a B con la medición delante y se declara la reversión del diagnóstico, no se
ajusta la aserción.

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-VCF-15 | Un verde del árbol de trabajo no sustituye la prueba en el árbol del commit | Toda verificación de la cura se repite sobre el árbol del commit (`git archive`/clon fiel), no solo sobre el worktree |
| L-T4A.5 | Un verde puede no alcanzar la rama | El mutante es sobre la rama real de `_plan_date` (o de `build()`), según dónde caiu la cura, nunca sobre un duplicado en el test |
| L-PF10 | Una lista vacía válida no equivale a falta de fuente | `SIN-FUENTE` es un **estado publicado** con fecha `0000-00-00`, no una aproximación; ningún corte nuevo lo colapsa con `commit` |
| L-ENT.12 | El verde del verificador no probaba su propia cobertura | La cobertura `fechas_por_fuente` y la línea `[fechas]` siguen imprimiéndose en verde y en rojo, con cada tier teniendo su diente |
| L-G3 | Cambiar un contrato reescribe sus tests y su prosa en el mismo commit | Si cambia la cascada, cambian en el mismo commit `tests/test_build_lesson_index.py`, la cabecera autodescriptiva del índice generado y la fila S15 del `10-analisis` del plan que la definió (**solo** la fila de este plan; la del padre archivado no se toca) |

## Tareas

1. **PRE y lectura del corte.** Re-medir HEAD/status/quick; PRE de la familia completa (`s15` 4 + `build_lesson_index`
   16 + `verify_qmind_context_freshness` 36, selección literal publicada). Leer la fila de B que abre la fase y el
   mutante que B dejó documentado.
2. **AC9: la cura en el generador** con su decisión escrita (qué corte gobierna, qué alternativas se rechazaron y
   por qué — el precedente medido del 2026-09-26 es que la alternativa del commit de creación `--diff-filter=A`
   **empeoraba** el criterio). Sin nuevos tiers sin diente.
3. **Dientes y mutantes:** apagar la rama curada devuelve el rojo; los tres tiers de `[fechas]` tienen cada uno su
   afirmación; la no-regresión del corte positivo (dos checkouts del mismo commit publican bytes idénticos) sigue
   verde sin tocar su aserción. Restauración por sha256.
4. **Cierre con hermanas y derivados:** las tres baterías re-corridas con par pre/post y resta comprobada;
   `build_lesson_index.py` regenerado **después** de la cura y su `--check` en verde; quick; modo completo si la fase
   tocó la capa de contenido; post-ejecución del contrato paso 1 al 8.

## Criterios de Completitud (CHECKLIST)

- [ ] La fase está autorizada por la medición de B (fila en `dependencias-fases.md`), no por conveniencia
- [ ] AC9 con mutante rojo y verde archivados y restauración verificada por sha256
- [ ] `[fechas]` imprime los tres tiers con su conteo y cada tier tiene su diente; ningún tier nuevo sin diente
- [ ] 4 + 16 + 36 funciones verdes, delta explicado solo por adiciones de ESTA fase
- [ ] El par del índice regenerado viaja con la cura en el mismo commit (R2.10, `[6/8]`)
- [ ] Post-ejecución completo; quick verde; CHANGELOG y GUIA_TECNICA con la nota de fase bajo `## [Sin publicar]`

## Restricciones

- No tocar `scripts/validate_qmind_writeback.py` ni su familia (pertenece a A1-A3, ya cerradas).
- No re-ancorar el control de B; no tocar `AGENTS.md`, `.cursorrules`, `VERSION.yaml`; no liberar versión.
- No iniciar FASE-RELEASE. Presupuesto **90 `tool_use`** al corte autorizado — igual que A2/A3/B, por decisión del
  operador del 2026-10-08 sobre la medición de A1 (ALTA, ≈70) más las 4 + 16 + 36 funciones hermanas que C re-ejecuta;
  la referencia y su base viven en `04-contrato-ejecucion.md` §R2. Auto-reporte con unidad declarada.

## Prompt de ejecución

```
Actua como ejecutor de fases del repo C:\Users\Jhond\Github\iah-cli (rama master), en espanol y sin acentos en
el mensaje de commit.

Lee 01-plan-maestro.md §1 y §4, 04-contrato-ejecucion.md, 00-lecciones-capitalizadas.md §2 y §4, dependencias-fases.md, 05-prompt-inicio-sesion-fase-C.md y el workflow canónico.

Ejecuta SOLO FASE-C del plan .opencode/plans/Archives/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07, y solo si FASE-B abrio esta
fase con su medicion; si no se abrio, cierra la sesion declarando que la fase no aplica.

OBJETIVO: curar la clasificacion en scripts/build_lesson_index.py como codigo de producto, con su AC, su mutacion
y sus baterias.

TAREAS: 1) PRE y lectura del corte que B decidio. 2) AC9 cura con decision escrita y alternativas rechazadas.
3) dientes por tier con restauracion por sha. 4) cierre con las hermanas de 16 y 36 funciones y el indice
regenerado.

CRITERIOS: apagar la rama curada devuelve el rojo, los tres tiers de la linea de fechas tienen su diente y el par
regenerado viaja en el mismo commit.

RESTRICCIONES: sin tocar el verificador de write-back, sin re-ancorar el control de B, sin AGENTS ni VERSION, sin
commit salvo instruccion literal, sin iniciar RELEASE.

```
