# FASE-A — par pre/post del conteo (AC5 y AC16)

Plan: `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` · Medido el **2026-09-21** sobre HEAD `2deddee`
(árbol limpio al abrir, paridad `0/0` con `origin/master`).

**Comando idéntico en los dos lados** (R2.3/R2.7 — la resta solo vale si el instrumento es el
mismo):

```bash
grep -nE '^\s*(def _check|print\(f?"\[[0-9]+/[0-9]+\])' scripts/run_all_validations.py
grep -nE '^#   \[[0-9]+/[0-9]+\]' scripts/git_hooks/pre-commit
grep -rhoE '\[[0-9]+/11\]|11 checks?' tests/ --include=*.py | sort | uniq -c
grep -rhoE '\[[0-9]+/7\]|7 pasos' tests/ --include=*.py | sort | uniq -c
grep -rE '^\s*def test_' tests/quality_gates/governance_numbers --include=*.py | wc -l
grep -rE '^\s*def test_' tests --include=*.py | wc -l
grep -rhoE '\[[0-9]+/[0-9]+\]' .agents/workflows/phased_project_executor.md \
  .agents/workflows/templates/lecciones-capitalizadas-template.md | wc -l
```

Archivos crudos: `faseA_baseline_pre.txt` · `faseA_baseline_post.txt` ·
`faseA_quick_pre.txt` · `faseA_quick_post.txt`.

## La resta, por unidad

| Unidad (medida con el mismo comando en los dos lados) | PRE | POST | Resta | Esperado | Estado |
|---|---|---|---|---|---|
| Checks del `--quick` (`[N/11]` impresas) | 11 | 11 | **0** | 0 (AC5, AC16) | ✅ |
| Total del modo completo (`[N/15]`) | 4 | 4 | **0** | 0 | ✅ |
| Pasos del hook versionado | 7 | 7 | **0** | 0 (AC16) | ✅ |
| Composición del `--quick` (`TOTAL: n/n`) | 11/11 verde | 11/11 verde | 0 | verde sin tocar composición | ✅ |
| Población A8 de los documentos de gobierno: instancias `[N/M]` | 22 | 22 | **0** | 0 (no se editó `.agents/`) | ✅ |
| Población A8: líneas con instancia | 17 | 17 | **0** | 0 | ✅ |
| Población A8: formas «check N» | 2 | 2 | **0** | 0 | ✅ |
| **Selección de tests de la fase** (`tests/quality_gates/governance_numbers`) | 0 funciones | 23 funciones / 28 casos | **+23** | distinto de 0: la fase agrega tests | ✅ declarado |
| Funciones de test canónicas del repo (método grep) | 4.307 | 4.330 | **+23** | coherente con la fila anterior | ✅ |
| Pins de `[N/11]` en `tests/` (familia iii de AC2) | 0 | **4** | **+4** | — | ⚠️ creado por esta fase, con dueño |

**AC5 no pide una resta 0 en los tests: pide una resta 0 en los CONTEOS DE CHECKS** (11 y 7) y
prohíbe cerrar con «delta 0» sobre una métrica que sí se movió. Por eso las dos últimas filas se
publican aparte: pretender 0 en la selección de tests con 21 funciones nuevas escritas aquí sería
un baseline contaminado (L-D3).

## Quién afirma el 11 y el 7 (barrido de `tests/`, L-V2.3)

| Fuente | Qué afirma | Medido |
|---|---|---|
| `tests/test_validate_plan_closure.py` | `[5/7]` dentro del hook (contract test del paso 5) | 1 coincidencia, PRE y POST |
| `tests/quality_gates/governance_numbers/test_governance_numbers_reproduce_A1_A4.py` | `observed == "[9/11]"` y `"[10/11]"` (el contrato AC1 escrito como literal) | **4 coincidencias, todas de esta fase** |
| `tests/` antes de la fase | nada sobre el denominador 11 | 0 coincidencias con `\[[0-9]+/11\]\|11 checks?` |
| `AGENTS.md` | «10/10 checks en modo rápido; 14 en el completo» | vencido (mide 11 y 15); **no lo toca este plan** — familia (ii) de AC2 |
| Cuatro documentos de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` | «El quick son 11 checks» y su par | re-medidos y confirmados: `README.md`, `06-`, `09-`, `10-` de ese plan |
| Dos documentos de `Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` | la misma cifra, archivada | presente, fuera de alcance |

**Consecuencia declarada**: FASE-A **añadió** pins del denominador 11 en `tests/`. No es una
violación de AC16 (AC16 gobierna la *composición* del quick y del hook, que sigue en 11 y 7), pero
sí agranda la familia (iii) que AC2 declara no cubierta, y es deuda que alguien pagará al renumerar:
dueño **D1/D2** (la corrección de `.agents/` y la promoción del verificador a check 12 obligan a
re-anclar este test con su nota datada). Se dejó la aserción literal — es la que prueba AC1 — y se
publicó el pin, en lugar de debilitar el test para que la resta quedara limpia.

## Rojos preexistentes ajenos, declarados

* Ninguno en la selección de esta fase (`26 passed`).
* **Rojo ajeno reproducido y medido, no arrastrado**: al correr la selección de esta fase junto a
  sus vecinas, falla
  `tests/test_validate_lesson_capitalization.py::test_medido_contra_el_predecesor_entra_en_alcance_y_su_forma_es_conforme[2026-09-11-TRIBUNAL-ENFORCEMENT-OBS-2026-09-11]`.
  **Causa medida**: el test afirma que `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` está en el *alcance* del
  verificador de capitalización, pero ese plan fue archivado en `RELEASE-4.77.0` (`git log --
  .opencode/plans/Archives/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` → `3d25778`, `e8010ce`) y el alcance
  excluye `Archives/` por diseño. **No lo abrió FASE-A**: la prueba no mira los archivos de esta fase
  y el `[10/11]` del quick está verde. **Dueño**: `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` (última sesión
  que tocó el test, `66e17bd`) — re-anclar el caso a un plan que siga en alcance, sin borrarlo.
* `run_all_validations.py --quick`: verde en los dos lados (11/11). **Con un rojo propio
  intermedio, declarado y resuelto con su writer**: al re-escribir los `.md` del plan, el registro de
  `log_phase_completion.py` dejó vencida la fecha de `REGISTRY.md` y el check `[3/11]`
  (`sync_versions.py --check`) puso la corrida en 10/11. No se editó `REGISTRY.md` a mano: se corrió
  `python scripts/sync_versions.py --rule registry_last_update` y la corrida volvió a 11/11
  (`faseA_quick_post.txt`). Lección de proceso: los dos escritores de esa fecha siguen sin
  reconciliar, y esta fase lo reprodujo.
* Cifra canónica del repo en `AGENTS.md` (4.246 funciones) contra disk (4.330 al cerrar): vencida por
  tráfico ajeno a este plan (el piloto `EVALUACION-JEV` sumó funciones antes de esta sesión). No se
  corrige aquí: `AGENTS.md` es configuración central y su edición pide instrucción literal.
