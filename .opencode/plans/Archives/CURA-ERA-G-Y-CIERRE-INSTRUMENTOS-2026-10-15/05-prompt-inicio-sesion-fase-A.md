# FASE-A — Cierre documental de la tanda de instrumentos

**ID**: FASE-A (plan CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15)
**Objetivo**: cerrar el documental de la tanda ya empujada (`2e048e6` + `1f95e84`): commitear las 4 rutas del registro `D-QW-1`/`D-QW-2`, persistir los crudos de la sesión bajo evidencia versionada, dejar el acta del cierre con los shas, y verificar el árbol del commit. **No toca código de producción. No ejecuta el modo completo sin `PYTHONUTF8=1`.**
**Dependencias**: ninguna (primera fase; el árbol trae los 4 archivos sin commitear). **Sello 2026-10-15**: esas cuatro rutas y los 11 archivos del plan quedaron versionados en `85ab952`; la frase de arriba describe el árbol al concebir la fase y no se re-escribe — abrir re-midiendo.
**Duración estimada**: 1 sesión corta.
**Complejidad**: BAJA — comandos ya corridos y verdes; el único paso con puerta es el commit, que **requiere autorización escrita del Operador en la sesión**.
**Skill**: `.agents/workflows/phased_project_executor.md` (workflow canónico).

## Contexto

La sesión del 2026-10-15 curó la segunda vía de gobernación y el reemplazo por documento, publicó los dos CONTEXT que la población nueva exigía, y empujó dos commits (`2e048e6` cierre documental 4.81.0 + archivado; `1f95e84` las dos curas con sus 9 dientes). De esa sesión quedaron tres cabos que esta fase cierra: (1) las 4 rutas del registro `D-QW-1`/`D-QW-2` —el contexto raíz, el crudo `14-` y el par del índice regenerado— siguen **sin commitear**; (2) los crudos de las corridas viven en `temp/` (gitignored) y se pierden con el scratch; (3) ninguna acta reúne los shas de esos crudos ni la frontera de lo que quedó fuera.

La deuda era-G (el rojo `[DUPLICADO-VIGENTE]` del writer) es de FASE-B/C y **no se toca aquí**; esta fase solo cierra lo ya hecho: nada de este prompt re-mide el write-back ni sube nada al notebook.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| Preparación (Paso 0 + maestro + prompts) | ✅ Completada (2026-10-15) |

### Base Técnica Disponible

- Rutas del registro `D-QW` (sin commitear): `.opencode/context/CONTEXT-DEUDAS-WRITER-QMIND-2026-10-15.md` (nuevo), `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-RELEASE/14-deuda-writer-context-sin-registro.txt` (nuevo), `.opencode/LECCIONES-INDEX.md` y `.opencode/lecciones_index.json` (modificados; el par ya está regenerado y `--check` verde). **Vencido el 2026-10-15**: las cuatro rutas quedaron versionadas en `85ab952` con `git add` previo y pathspec explícito.
- Crudos en `temp/` (gitignored): `14-frescura-post-cura.txt`, `15-frescura-segunda-corrida.txt`, `16-indice-antes.txt`, `17-opencode-refs.txt`, `18-quick-post-cura.txt`, `19-writeback-post-cura.txt`, `20-commit2-hook.txt`, `21-quick-tras-deuda.txt`, `msg-c1.txt`, `msg-c2.txt`, `l3-out.json`.
- Instrumentos: `scripts/build_lesson_index.py` (`--check`), `scripts/validate_opencode_refs.py`, `scripts/run_all_validations.py --quick`, `scripts/log_phase_completion.py`.
- Commits de la tanda: `2e048e6` (44 rutas) y `1f95e84` (8 rutas, hook 8/8 impreso). L3 sobre `5341e15..1f95e84` = 2 commits, 0 hallazgos. Paridad con `origin/master` 0/0 al cerrar la sesión.

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-SECF.2 | `git commit -- <ruta>` ignora untracked y una salida filtrada borra el fallo del radar | T2: `git add` explícito por ruta, conteo de lo stageado contra el listado esperado y `git status` del árbol después; prohibido `git add <directorio padre>` y prohibido leer el resultado por un `grep` filtrado |
| L-V.2 | Las notas de fase pueden ser inexactas: se certifica re-leyendo artefactos | T3: la verificación del cierre corre sobre los **crudos re-ejecutados en esta sesión** y sobre el árbol del commit; ninguno de los shas del acta se hereda de la sesión de preparación |
| D-V2.1 | El instrumento canónico de R2.1 no alcanza el transcript: presupuesto auto-reportado | Restricciones: el presupuesto de esta fase se declara como auto-reporte en `tool calls`, no como medido |

## Tareas

### Tarea 1 — Persistir los crudos (AC2)

**Objetivo**: que la evidencia de la tanda viva versionada y con shas auditables, no en `temp/`.

**Archivos afectados**:
- `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-RELEASE/` (crudos nuevos, numeración sin colisión con `14-deuda-writer-context-sin-registro.txt`)

**Criterios de aceptación**:
- [ ] Los crudos relevantes se copian con **nombres descriptivos o numeración desde `15-`** (`14-` está tomado). Mínimo: frescura post-cura, segunda corrida de frescura, quick post-cura, write-back post-cura, hook del commit 2, quick tras la deuda, el recorrido de L3 y los dos mensajes de commit. `16-indice-antes.txt` y `17-opencode-refs.txt` pueden viajar como parte del acta si se citan; decidirlo y declararlo, no mezclarlo.
- [ ] Cada crudo copiado conserva sus bytes: la copia se verifica por `sha256sum` de origen y destino **antes** de borrar nada de `temp/`. No se borra `temp/` en esta fase salvo que el Operador lo pida.
- [ ] El acta publica el sha256 del **blob versionado** (el que Git guarda, que con `core.autocrlf=input` puede diferir del disco para un crudo CRLF): el acta declara ambas identidades cuando difieran, o solo la del blob y lo dice. Nunca dos promesas de sha contradictorias.

### Tarea 2 — Commit de las rutas del registro (AC1) — **requiere autorización escrita**

**Objetivo**: las 4 rutas de `D-QW-1`/`D-QW-2` quedan versionadas (y empujadas si el Operador lo autoriza en la sesión).

**Archivos afectados**:
- `.opencode/context/CONTEXT-DEUDAS-WRITER-QMIND-2026-10-15.md`
- `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-RELEASE/14-deuda-writer-context-sin-registro.txt`
- `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` (viajan **en el mismo commit** que el `.md` de `context/`: el hook `[6/8]` corta sin el par)
- los crudos de T1

**Criterios de aceptación**:
- [ ] Antes del commit: `git status --porcelain` listado, `git add` **por ruta explícita**, y `git diff --cached --name-only | wc -l` contrastado contra el listado esperado (L-SECF.2). Prohibido `git add` de directorio padre.
- [ ] El hook pre-commit corre **sus 8 checks, ninguno saltado**; su salida se guarda como crudo.
- [ ] Mensaje propuesto (ajustable por el Operador): `docs(qmind): D-QW-1 y D-QW-2, la rama que sube CONTEXT sin registrar` con el cuerpo que declare la autoría de la sesión anterior.
- [ ] Si el Operador autoriza además el push: la **L3 va entre el último commit y el push**; si el clasificador la niega, se para antes del push y se pide el literal con las tres opciones en texto plano.
- [ ] El commit **no** incluye nada fuera de T1+T2: `git status` posterior demuestra que no quedan restos.

### Tarea 3 — Verificación del cierre (AC1, AC2, AC6)

**Objetivo**: el árbol del commit queda con los verdes re-ejecutados en esta sesión.

**Criterios de aceptación**:
- [ ] `python scripts/build_lesson_index.py --check` → OK y el conteo de IDs lo imprime la corrida.
- [ ] `python scripts/validate_opencode_refs.py` → PASS.
- [ ] `python scripts/run_all_validations.py --quick` → verde (el número lo imprime la corrida).
- [ ] Opcional y preferido: reproducir la población gobernada **en el árbol del commit** con `git archive` a un temporal y `poblacion_del_context` de `scripts/verify_qmind_context_freshness.py`: debe dar **2 gobernados** (los dos CONTEXT publicados). Si se corre, su crudo va a evidence.

### Tarea 4 — Acta y documentación de fase

**Objetivo**: el cierre documental existe como artefacto con shas, no como relato.

**Criterios de aceptación**:
- [ ] `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-A/acta-cierre-documental.md`: qué viajó (rutas + shas de blob), qué quedó fuera y por qué, el árbol del commit verificado, y la frontera con FASE-B (la deuda era-G intacta).
- [ ] Post-Ejecución 1-6 completa (README, `06-checklist`, `dependencias-fases.md`, `09` §D, `10-analisis`, `00-` §2).
- [ ] `python scripts/log_phase_completion.py --fase FASE-A --fecha <FECHA_DE_CIERRE_DE_ESTA_FASE> --desc "Cierre documental de la tanda de instrumentos (D-QW-1/2, crudos, acta)" --archivos-mod "<rutas reales del commit>" --tests 0 --check-manual-docs`
- [ ] `DOMAIN_PRIMER` **no** se regenera en esta fase (no es fase de implementación; se regenera en FASE-C y se verifica en RELEASE).
- [ ] Pregunta de aporte durable para cualquier `CONTEXT-*.md` tocado (aquí no se escribe ninguno nuevo).

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| (sin tests nuevos) | — | Esta fase no toca código; su verificación son las tres corridas de T3 y el hook del commit |

**Comando de validación**:
```bash
python scripts/build_lesson_index.py --check
python scripts/validate_opencode_refs.py
python scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** — ver template §5. Al cerrar:

1. `dependencias-fases.md`: marcar FASE-A ✅ con fecha, shas del commit y notas.
2. README del plan: tabla de progreso; métricas por **referencia** al acta.
3. `09-documentacion-post-proyecto.md`: secciones A/B/D/E con lo de esta fase (aquí vive el número).
4. `10-analisis-post-implementacion.md`: fila de Resumen de Ejecución + lecciones (o «sin lecciones nuevas») + seguimientos.
5. `00-lecciones-capitalizadas.md` §2: anotar qué pasó realmente en la columna «Qué cambia».
6. `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-A/`: acta + crudos + shas.
7. Registro de fase (la fase se registra a sí misma, §2.5 del executor): comando de T4.

## Criterios de Completitud (CHECKLIST)

- [ ] AC1 y AC2 legibles en sus artefactos; AC6 con la corrida del quick re-ejecutada
- [ ] Commit con pathspec, índice contrastado por conteo y hook 8/8 impreso (o la sesión termina en «listo para revisión» si el Operador no autoriza el commit — es un corte válido)
- [ ] `build_lesson_index.py --check` y `validate_opencode_refs.py` verdes **en esta sesión**
- [ ] `log_phase_completion.py` ejecutado con `--tests 0`
- [ ] Cinco cortes declarados; sin push sin L3 y sin autorización
- [ ] Post-ejecución 1-7 completa

## Restricciones

- **Presupuesto (R2.1)**: ~30 tool calls; unidad: auto-reporte en `tool calls` (D-V2.1: no hay instrumento que lo mida); corte: **hasta listo para revisión** — este prompt **no** autoriza commit ni push por sí mismo.
- **No tocar**: el `10-analisis` de CURA (congelado, DEC-2), los dos CONTEXT publicados (congelados, DEC-3), ningún archivo de código, el notebook (ninguna subida en esta fase), y `temp/` (no borrar hasta que T1 esté verificado).
- Citas por símbolo, nunca `archivo:línea` (R2.2).
- El commit, si se autoriza, es **uno** y con las 4+ rutas del registro y sus derivados; los crudos de T1 pueden ir en el mismo commit o en uno propio, declarándolo.

## Prompt de Ejecución

```
Actúa como agente de cierre documental del plan CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15.

Ejecuta únicamente FASE-A del plan .opencode/plans/Archives/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/
Lee 01-plan-maestro.md (§4 y §5), 00-lecciones-capitalizadas.md (§2 y §4), dependencias-fases.md y el workflow canónico.

OBJETIVO: cerrar el documental de la tanda empujada: persistir los crudos bajo evidencia con sus shas, commitear las rutas del registro D-QW-1/D-QW-2 con pathspec y autorización, y verificar el árbol del commit.

CONTEXTO:
- Fases previas: Preparación ✅ (esta fase no toca código ni el notebook)
- El árbol trae sin commitear: CONTEXT-DEUDAS-WRITER-QMIND-2026-10-15.md, 14-deuda-writer-context-sin-registro.txt y el par del índice
  (vencido 2026-10-15: esas rutas y la carpeta del plan están en 85ab952; re-medir el árbol en T0 antes de fiar esta línea)
- Commits de la tanda: 2e048e6 y 1f95e84 (empujados; paridad 0/0 medida al cerrar la sesión previa)
- El commit y el push requieren autorización escrita del Operador EN ESTA SESIÓN, y siempre con pathspec

TAREAS:
1. T1 Persistir los crudos en evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-RELEASE/ (numeración desde 15-), con sha256 de origen==destino verificado antes de tocar temp/
2. T2 Commit de las 4 rutas del registro + crudos: add explícito por ruta, conteo del índice, hook 8/8, mensaje propuesto; push solo si el Operador lo autoriza, con L3 entre el último commit y el push
3. T3 Verificación: build_lesson_index.py --check, validate_opencode_refs.py, run_all_validations.py --quick y (preferido) población 2 en el árbol del commit vía git archive
4. T4 Acta del cierre documental con shas de blob + post-ejecución + log_phase_completion --fase FASE-A --tests 0

CRITERIOS:
- AC1/AC2 legibles en el acta y en el `git show` del commit; AC6 con el quick re-ejecutado
- Sin tocar el 10-analisis de CURA ni los dos CONTEXT publicados

VALIDACIONES:
- python scripts/build_lesson_index.py --check
- python scripts/validate_opencode_refs.py
- python scripts/run_all_validations.py --quick
- python scripts/log_phase_completion.py --fase FASE-A --fecha <FECHA_DE_CIERRE_DE_ESTA_FASE> (la fase se registra a sí misma)
```
