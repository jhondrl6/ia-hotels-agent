# FASE-A — Retiro de `spark` y guardián por existencia (`N1` + `N7` + `R4`)

**ID**: FASE-A · **Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22`
**Objetivo**: retirar la ruta `spark` (deprecada y rota por `FinancialFactors.SUPERPOSITION_FACTOR`), corregir el lector latente de `gap_analyzer`, extender el guardián a existencia de atributo y cerrar el barrido de lectores huérfanos del refactor `1501dd8`.
**Dependencias**: ninguna (primera fase).
**Complejidad técnica**: MEDIA-ALTA · **Duración estimada**: 2-3 horas
**Modo de ejecución**: **DIRECTO** (imports del proyecto; regla código+tests del executor). El barrido `R4(c)` es delegable a un subagente con `Agent` (grep/AST puro, sin imports).

## Contexto

`FinancialFactors.SUPERPOSITION_FACTOR` ya no existe: el refactor lo convirtió en `get_superposition_factor()`. `main.py` lo referencia en `_map_audit_to_spark_data`, que solo usan las dos ramas de `spark`; `run_spark_mode` traga la excepción y hace `sys.exit(1)`. La ruta está deprecada en `AGENTS.md` y el producto usa `v4complete`. **Decisión del Operador en esta corrección: se retira, no se repara.** `D19` se cierra por retiro, no por una promesa de número. `gap_analyzer` conserva un lector latente del mismo atributo; se corrige como higiene de contrato.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| Preparación + corrección | ✅ |

### Base Técnica Disponible
- `main.py` (`_map_audit_to_spark_data`, `_spark_handler`, `run_spark_mode`, `_run_spark_legacy`, registro del subcomando `spark`)
- `modules/analyzers/gap_analyzer.py` (`GapAnalyzer._basic_analysis` → `modelo_perdidas.factor_superposicion`)
- `modules/utils/financial_factors.py` (`get_superposition_factor()`, devuelve 0.7)
- `tests/test_main_static_guards.py` (3 passed sobre el defecto)
- `AGENTS.md` (§Comandos CLI: `spark` deprecado)

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-SR1 | Las ramas no ejercitadas acumulan defectos latentes | El retiro no cierra sin un test que ejecute la ruta retirada y afirme que no revienta |
| L-V2 | Quien cambia un contrato barre sus consumidores en TODO el repo | Tarea 4 barre los demás contratos atributo→método del refactor `1501dd8` |
| L-CIM.12 | Un control verde puede no medir la propiedad que nombra | Tarea 3 convierte el guardián en comprobación de existencia, con mutante en rojo |
| D-PF5 | El guardián estático es una lista de nombres sobre AST, extensible | Tarea 3 lo extiende a la clase importada o a una superficie pública equivalente |
| L-R.4 | Una regla sin verificador se publica solo si lo declara | El par rojo/verde se declara en el cierre |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | El test del retiro afirma exit y mensaje, no solo “no lanzó” |

## Tareas

### Tarea 1: Retirar `spark` de la CLI
**Objetivo**: el comando `spark` deja de ejecutar la estimación rota y sale con un mensaje de retiro; no queda ningún lector ejecutable de `SUPERPOSITION_FACTOR` en esa ruta.
**Archivos afectados**: `main.py` (registro del subcomando, `_spark_handler`, `_run_spark_legacy`, `run_spark_mode`, `_map_audit_to_spark_data` y tests asociados).
**Criterios de aceptación**:
- [x] `python main.py spark --url <fixture>` sale con código 0 y un mensaje que declara el retiro; no aparece `AttributeError`
- [x] `_map_audit_to_spark_data` desaparece o deja de calcular la pérdida; no hay lectura ejecutable de `FinancialFactors.SUPERPOSITION_FACTOR`
- [x] `D19` se declara cerrada por retiro en `10-analisis` §Seguimientos; no se promete una cifra nueva

### Tarea 2: Corregir el lector latente de `gap_analyzer`
**Objetivo**: `GapAnalyzer._basic_analysis` deja de referenciar el atributo inexistente; si la rama es código muerto, se retira o se marca con dueño, no se deja “por si acaso”.
**Archivos afectados**: `modules/analyzers/gap_analyzer.py`.
**Criterios de aceptación**:
- [x] Importar y recorrer la rama no produce `AttributeError`
- [x] La decisión (reparar o retirar) queda escrita en `10-analisis` §Decisiones; no se cambia el alcance de `D19`

### Tarea 3: Guardián por existencia (`N7`)
**Objetivo**: el guardián detecta un atributo inexistente sobre la clase importada, no solo nombres prohibidos.
**Archivos afectados**: `tests/test_main_static_guards.py` (o test de superficie pública nuevo).
**Criterios de aceptación**:
- [x] Mutante con atributo inventado → rojo; árbol actual → verde; par en `evidence/…/FASE-A/`
- [x] El docstring de `analyze_with_claude` deja de afirmar un consumidor (`main.py`) que no existe
- [x] La comprobación es AST/import, no un grep de menciones

### Tarea 4: Barrido de lectores huérfanos (`R4c`)
**Objetivo**: barrer los demás contratos que el mismo refactor tocó (atributo→método) en TODO el repo.
**Criterios de aceptación**:
- [x] Crudo del barrido en evidencia (`git log -S`/AST), con la lista de superficies revisadas
- [x] Huérfanos adicionales → `10-analisis` §Seguimientos con dueño; **no** se expande alcance sin decisión

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| retiro de `spark` | `tests/` (nuevo) | Exit 0, mensaje de retiro, sin `AttributeError`; rojo si se reintroduce el lector roto |
| guardián de existencia | `tests/test_main_static_guards.py` | Verde en el árbol; rojo con atributo inventado |
| lector de `gap_analyzer` | `tests/` (nuevo o extensión) | La rama no revienta; rojo con el contrato roto |

**Comando de validación**: `./venv/Scripts/python.exe -m pytest tests/test_main_static_guards.py <tests-nuevos> -q` + `./venv/Scripts/python.exe main.py spark --url <fixture>; echo EXIT=$?` + `run_all_validations.py --quick`. Baseline de conteo: `grep -rE "^\s*def test_" tests --include=*.py | wc -l` (par pre/post, R2.3).

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: marcar FASE-A ✅ con fecha y notas.
2. `README.md`: progreso por referencia a `09` §D.
3. `09-documentacion-post-proyecto.md`: completar B/D/E de esta fase.
4. `10-analisis-post-implementacion.md`: fila de resumen, lecciones, seguimientos (incluido el cierre de `D19` por retiro) y métricas por referencia.
5. `00-lecciones-capitalizadas.md`: anotar qué pasó con las lecciones citadas.
6. `evidence/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22/FASE-A/`: crudos, pares rojo/verde, `baseline_pre.txt`/`baseline_post.txt` y `baseline-pre-post.md` con la resta (R2.7).

Registro:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-A --fecha <fecha-de-cierre-de-esta-fase> \
    --desc "Retiro de spark (N1/D19), lector latente de gap_analyzer corregido y guardián por existencia (N7/R4, AC5)" \
    --archivos-mod "<rutas>" --tests "N" --check-manual-docs
```

## Criterios de Completitud (CHECKLIST)

- [x] `spark` retirado con test de la ruta; sin `AttributeError`; `D19` cerrada por retiro
- [x] `gap_analyzer` sin lector roto; decisión escrita
- [x] Guardián con mutante rojo y árbol verde; par en evidencia
- [x] Barrido `R4c` publicado; huérfanos con dueño
- [x] `--quick` verde; cinco cortes sin commit; lecciones registradas
- [x] `dependencias-fases.md` actualizado; métricas consistentes con `09` §D

## Restricciones

- Presupuesto: tope **60 tool-use**; corte «listo para revisión». El instrumento `evidence/FASE-D/measure_iterations.py` es legado: si el transcript del runtime no es compatible, auto-reporte `tool_use` marcado **no comparable**.
- **No** se repara `D19`; no se ejecuta `v4complete`; no se toca `S-CST-1` (`publication_gates.py`), ni `judge.py`/`acta_writer.py` (FASE-C), ni las plantillas (FASE-B).
- No acuñar alias de IDs. Citas por símbolos, nunca `archivo:línea` (R2.2).

## Prompt de Ejecución

```bash
Actúa como especialista en el repo iah-cli. Ejecuta únicamente FASE-A del plan .opencode/plans/Archives/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22.
Lee 05-prompt-inicio-sesion-fase-A.md, 01-plan-maestro.md §1, §2, §4 y §5, 00-lecciones-capitalizadas.md §2, dependencias-fases.md y workflow canónico.
OBJETIVO: retirar spark (no repararlo), corregir el lector latente de gap_analyzer, extender el guardián a existencia y barrer lectores huérfanos.
TAREAS: 1 retiro de spark, 2 lector de gap_analyzer, 3 guardián por existencia, 4 barrido R4c.
CRITERIOS: AC5 (spark sin AttributeError, guardián con mutante rojo, D19 cerrada por retiro); par rojo/verde en evidence.
VALIDACIONES: pytest; main.py spark con exit 0; --quick; log_phase_completion.py al cierre.
```
