# Cierre de FASE-V3 — orden R2.10 medido (2026-09-13)

Todo lo de abajo se **ejecutó** en este orden y se pega con su salida literal. La sesión se
reanudó el 2026-09-13; V1 y V2 cerraron el 2026-09-12 (commits `42b12a1` y `e02a688`).

## 0. Estado de partida: `--quick` daba 8/9 sin que nadie tocara nada

`[3/9] Version Sync` en rojo al reanudar la sesión:

```
Source: ...\VERSION.yaml  version: 4.76.0  date: 2026-09-13
FAIL: AGENTS.md (agents_version_comment) - needs update
FAIL: .cursorrules (cursorrules_header) - needs update
FAIL: docs/GUIA_TECNICA.md (guia_tecnica_header) - needs update
FAIL: docs/contributing/REGISTRY.md (registry_last_update) - needs update
```

Causa leída en el código: `VERSION.yaml` no define la clave `date`, así que `sync_versions.py`
la inyecta con `datetime.now().strftime("%Y-%m-%d")`; las cuatro cabeceras llevaban `2026-09-12`.
El delta era exclusivamente el calendario. Registrado como **D-V3.1** (y como lección **L-V3.2**).

Arreglo: se corrió el escritor canónico, no se editaron cabeceras a mano.

```
python scripts/sync_versions.py
OK: AGENTS.md (agents_version_comment) - updated
OK: .cursorrules (cursorrules_header) - updated
OK: docs/GUIA_TECNICA.md (guia_tecnica_header) - updated
Result: All files in sync
```

`git diff` de esos tres archivos: **solo** la fecha (`2026-09-12` → `2026-09-13`) más la línea de
`AGENTS.md` que esta fase debía tocar (`(4/4 checks)` → `(9/9 checks en modo rápido; 13 en el
completo)`). `VERSION.yaml` con diff vacío (**AC-A5**, sin bump, decisión Q5).

## 1. Registro de fase

```
python scripts/log_phase_completion.py --fase FASE-V3 --desc "PASO0-VERIFICADOR: cierre documental
  sin bump - template v1.1.0 y executor v2.24.0 nombran al verificador, deuda (i) del predecesor
  cerrada, validation.md y AGENTS.md con el conteo de checks" --archivos-mod ... --tests 0
(R) Fase registrada exitosamente
```

Sin `--release`. Después de esto `registry_last_update` ya quedó en sync.

## 2. Write-back **antes** de archivar (R2.10)

```
python scripts/validate_qmind_writeback.py --upload PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12
[UP] 10-analisis: PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12 (lecciones aprendidas y decisiones)
[OK] Subido: 10-analisis-post-implementacion
[RESUMEN] upload=1 skip=0 fail=0
```

El argumento es **stem del plan**, no ruta: con `--upload .opencode/plans/<PLAN>` el script
concatena y responde `[FAIL] Upload: el directorio no existe: ...\.opencode\plans\.opencode\plans\...`.

## 3. Índice → archivar → índice (paso 3b de R2.10)

```
python scripts/build_lesson_index.py     # antes del git mv
[OK] 254 IDs definidos + 38 sin definición (12 análisis, 354 .md citados)

git mv .opencode/plans/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12 \
       .opencode/plans/Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12

python scripts/build_lesson_index.py     # después
[OK] 254 IDs definidos + 38 sin definición (12 análisis, 354 .md citados)

python scripts/build_lesson_index.py     # tercera corrida, tras escribirse L-V3.3 en el §2 del análisis
[OK] 255 IDs definidos + 38 sin definición (12 análisis, 354 .md citados)
```

252 → **254** → **255** por `L-V3.1`, `L-V3.2` y `L-V3.3`, las tres lecciones nuevas del cierre. Las
dos primeras corridas dan la misma cifra porque el índice cubre también `Archives/`: archivar no
saca un análisis del corpus, solo le cambia la ruta.

## 4. Referencias y validaciones

```
python scripts/validate_opencode_refs.py --fix
[PASS] OpenCode References: todas las referencias existen     ← sin diff que revisar a mano

python scripts/run_all_validations.py --quick
  TOTAL: 9/9 validations passed    (pre-archivado y post-archivado)
```

Salida del verificador del Paso 0 **después** de archivar:

```
cobertura: 0 plan(es) en alcance (—) | 26 archivados excluidos | 1 exentos por fecha anterior a 2026-09-12 | 0 exentos SIN FECHA PARSEABLE (—)
[OK] Capitalización del Paso 0: forma y trazabilidad verificadas | NO verifica pertinencia (...)
exit=0
```

Verde con denominador **0**: desde este cierre el gate no tiene población que evaluar hasta el
próximo plan creado bajo v2.24.0. La línea `cobertura:` lo dice en cada corrida (AC-B5, L-R.3);
el ✅ no significa «los planes capitalizan», significa «no hay nada todavía que capitalizar».

## 5. Dos rojos que produjo el propio cierre (y su arreglo)

Ninguno era un defecto del artefacto evaluado; los dos eran aserciones ancladas a una variable que
el cierre mutaba.

| Test | Rojo | Causa | Qué se hizo |
|------|------|-------|-------------|
| `test_el_unico_artefacto_real_del_repo_pasa_todos_los_checks` | `assert pobo["alcance"]` → `[]` | Exigía que el corpus tuviera un plan **en alcance**; el `git mv` de R2.5 sacó al único que había. El artefacto no cambió, el verde se fue solo | Reescrito como `test_los_artefactos_reales_del_repo_pasan_todos_los_checks_aunque_esten_archivados`: recorre con `rglob` todo `00-lecciones-capitalizadas.md` del repo, vivo o archivado, y su no-vacuidad la da el conteo de testigos, no la clasificación de alcance |
| `test_medido_contra_el_predecesor_la_unica_violacion_es_su_limite_no_actualizado` | `assert {C6} == set()` → `[]` | Pineaba una medición que esta fase invalidó: corrigió el §4 del predecesor, que seguía declarando «ese verificador falta» —frase que además era falsa en dos puntos, porque **C4 sí** comprueba que el «qué cambia» nombre un AC existente | §4 del predecesor actualizado (2026-09-13, con el límite real intacto: la pertinencia). El test pasa a `test_medido_contra_el_predecesor_entra_en_alcance_y_su_forma_es_conforme`, exige que el plan esté **en la población** antes de celebrar el verde, y deja escrita la historia del rojo en el docstring |

`29 passed` en `tests/test_validate_lesson_capitalization.py`.

## 6. Recertificación NR7 en el corte de cierre

```
python evidence/FASE-V2/run_nr7_capitalizacion.py
  OK  C1a: rojo=1 verde=0 ... OK C8: rojo=1 verde=0
[OK] NR7 (R2.8): 13 detecciones revertidas sobre el archivo versionado, todas con rojo y verde en FASE-V2/
```

13/13 otra vez sobre el script vigente. El runner reescribió sus 24 salidas de `evidence/FASE-V2/`
y el `git diff` resultante era **solo** la ruta temporal de `tmp_path` de pytest
(`pytest-322` → `pytest-354`), sin información nueva: se revirtió con `git restore evidence/FASE-V2/`
para no firmar como evidencia de V3 una diferencia de calendario de ficheros temporales. Antes de
revertir se midió que ningún otro archivo bajo `evidence/` estaba modificado (0).

## 7. Conteos de cierre

- Tests canónicos: **4.108** funciones en **295** archivos (método canónico `grep -rE "^\s*def test_" tests --include=*.py`).
- Publicación en `AGENTS.md`: **4.063**, 7 menciones vivas. No se parchea a mano (**S-V2.1**).
- Funciones de test nuevas en FASE-V3: **0** (los dos tests reescritos son de V2; el conteo no se mueve).
- Cambios de código de producción: **0**.

## 8. Suite completa en el corte de cierre

```
python -m pytest tests/ -q -p no:randomly
3 failed, 4071 passed, 31 skipped, 4 xfailed, 218 warnings in 174.73s (0:02:54)
```

Salida cruda: `pytest-cierre.txt` (tail). Los **3** rojos son exactamente los publicados y ajenos a
este plan: `test_function_default_flags` (flaky por orden de recolección),
`test_barreda_un_solo_emisor_de_la_clave` (deuda propia del tribunal, routed a **D-V.1**) y
`test_diagnostic_includes_geo_metrics` (cabecera `_build_geo_problems_table`). **0 regresiones**
atribuibles a este plan, cuyo único cambio de código son los dos tests reescritos del §5.
