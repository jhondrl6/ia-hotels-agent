# FASE-A — criterios de completitud, uno por uno, con su medición

Cerrada el **2026-09-21** sobre HEAD `2deddee`. Cada fila cita el artefacto donde un humano lo vería
sin abrir el código (R2.4). Techo alcanzable: `VERIFICADO OFFLINE` con mutation check en disco.

| Criterio del prompt de fase | Estado | Dónde se lee / comando |
|---|---|---|
| «Los cuatro tests pasan y **ninguno** cubre dos estados» | ✅ con rectificación de forma: son **cinco** archivos los que lista la tabla de tests obligatorios del propio prompt (y seis escritos, counting el de mutantes): 23 funciones / **28 casos**, todos verdes. Ninguno cubre dos estados: `…sin_hallazgos.py`, `…ausente.py`, `…lector_fallido.py` comparan **la primera línea** de la salida y cada uno exige además que las otras dos marcas **no** aparezcan | `python -m pytest tests/quality_gates/governance_numbers -q` |
| `mutation/` con el rojo y el verde (AC4) | ✅ **sin** quedar ⚠️: `verde_baseline.txt` + seis rojos (`M-A1`, `M-A2`, `M-A3`, `M-A4`, `M-POBLACION`, `M-SUJETO`), cada uno con el símbolo real apagado, las aserciones perdidas/ganadas y su `reasons` | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/mutation/` |
| `baseline-pre-post.md` muestra la resta y delta 0 (AC5) | ✅ quick 11→11, hook 7→7, población A8 22/17/2→22/17/2 (restas 0) y la métrica que **sí** se movió publicada aparte (tests +23) | `baseline-pre-post.md`, crudos en `faseA_baseline_pre.txt` / `…_post.txt` |
| `informe.json` con `coverage_basis` legible sin abrir el código (AC2) | ✅ población por clase, fuentes con sus 15 registros, regla de población con sus dos rutas y su frase de amparo, cuatro familias medidas y exenciones | `informe.json` → `coverage_basis` |
| `run_all_validations.py --quick` verde **sin** haber tocado su composición (AC16) | ✅ 11/11, `grep -c '/11]'` idéntico en los dos lados, `run_all_validations.py` y el hook sin diff. Incluye un rojo **propio** intermedio (fecha de `REGISTRY.md`) resuelto con su writer, no a mano | `faseA_quick_pre.txt` / `faseA_quick_post.txt`, `git diff --stat scripts/run_all_validations.py scripts/git_hooks/pre-commit` (vacío) |
| Ninguna aserción de `.agents/` fue editada (AC17) | ✅ `git status --porcelain .agents/` → **vacío**; los dos documentos conservan 98.694 y 6.123 bytes. A1–A4 siguen vencidas a propósito: corregirlas es **D1** | `ac17-y-presupuesto.md` §AC17 |
| Rojos preexistentes ajenos declarados con dueño y causa | ✅ un rojo ajeno reproducido (`test_validate_lesson_capitalization.py`, caso del plan archivado en `RELEASE-4.77.0`) con causa medida y dueño: `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` | `baseline-pre-post.md` §Rojos preexistentes |
| Post-ejecución completa, incluidos `log_phase_completion.py` y el índice | ✅ seis archivos del plan re-escritos (`dependencias-fases.md`, `README.md`, `06-`, `09-`, `10-`, `00-`), fase registrada en `REGISTRY.md` por el script, índice regenerado y fresco (`[OK] Índice de lecciones fresco (325 IDs)`), citas y capitalización y refs verdes | `git status --porcelain`, salidas de los tres verificadores |

## Lo que la fase **no** cerró (para que el siguiente no lo lea como cerrado)

- **Commit**: **hecho el 2026-09-21 en `a7564ae`** (34 archivos, +2.981/-142) con instrucción literal del operador, y llevó **dentro** el par `.opencode/LECCIONES-INDEX.md` +
  `.opencode/lecciones_index.json`, que es lo que corta `[6/7]` del hook. Dos rutas ajenas quedaron **excluidas a propósito** y siguen en el árbol de trabajo:
  `.opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/dependencias-fases.md` (modificado por otra sesión antes de abrir esta) y `.opencode/context/Refuerzo.md`
  (sin trackear, apareció durante la sesión). El push **no** estaba autorizado y no se hizo.

  *Nota de auto-aplicación (medición A6 del maestro, reproducida por esta fase): el párrafo decía «Commit: no hecho» y lo invalidó el propio commit que
  lo registró. Es el defecto que este plan caza, esta vez dentro de su propia fase — de ahí que la higiene se commitee aparte.*
- **D1** (corregir `.agents/`): sigue debida, con su disparador **re-formulado** porque estaba
  redactado en círculo (L-VCF-4).
- **D2** (promover el verificador al `--quick`): sigue debida. El script corre suelto y su salida 1
  con A1–A4 presentes es el comportamiento esperado, no un gate.
- Los estados `AUSENTE` y `LECTOR-FALLIDO` del **árbol real** no se ejercitaron (allí las cuatro
  rutas existen y se leen): se ejercitaron sobre fixtures en `tmp_path`, y así queda declarado —
  un verde de fixture no prueba el camino en producción, pero es el único camino reproducible sin
  romper `.agents/`.
