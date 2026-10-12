# T0 — Pre-imagen y blast radius (FASE-C2, 2026-10-12)

Medido **antes** de editar. Sin subagente (decisión declarada en el prompt de la fase).

## Árbol de apertura

```
TIP=cea999ac01fff1e6d9be9b25a7d2fec61d4dd490
ORIGIN=cea999ac01fff1e6d9be9b25a7d2fec61d4dd490
SUCIOS=0
PARIDAD_ADELANTE_AS=[0	0]
```

Comando: `git rev-parse HEAD` · `git rev-parse origin/master` · `git status --porcelain | wc -l` · `git rev-list --left-right --count origin/master...HEAD`.

**Hallazgo declarado (no bloqueante)**: la línea de dependencias del prompt fija el tip de apertura en
`6494939`; el tip medido es `cea999a` — un commit **posterior de docs** (`docs(plan): la línea de FASE-C2
que abría sobre un árbol que ya no existe, corregida con sus shas`), que es justamente la corrección del
propio prompt. El árbol sigue **limpio y en paridad**, y `cea999a` no toca código del tribunal:
`git diff --name-only 6494939..HEAD` lista solo documentos del plan. Ninguna ruta sucia, así que no hay
trabajo ajeno que excluir del commit de esta fase.

## Blast radius de los tres predicados (re-contado, L-CST-3)

Comando: `grep -rn "verified_critical\|verified_block\|verified_return_for_tests" tests/ --include=*.py`

| Archivo | Línea | Qué es |
|---------|-------|--------|
| `tests/quality_gates/tribunal/test_fase_b_consumidores_contrato.py` | 473 | aserción `assert bot4.verified_critical` (status `OK_WITH_FINDINGS`) |
| `tests/test_fase_0_ac20_evidencia_veredicto.py` | 269 | prosa del docstring, no aserción |
| `tests/test_fase_0_ac20_evidencia_veredicto.py` | 277 | aserción `con_hallazgos.verified_critical is vacio.verified_critical is True` |
| `tests/test_fase_0_ac20_evidencia_veredicto.py` | 278 | aserción `con_hallazgos.verified_block is vacio.verified_block is True` |

**3 líneas con aserción en 2 archivos** (la base técnica del prompt decía «4 líneas de 2 archivos»: el
cuarto hit es un docstring). Cifra confirmada con `grep -rc` por archivo: 1 y 3.

`INPUT_NOT_EVALUABLE` en tests: **4 líneas de un solo archivo** (`test_fase_b_consumidores_contrato.py`
:438 :439 :488 :489) — coincide con la base técnica. Su diferencial (`:441 assert acta["verdict"] !=
VERDICT_APPROVED`) sobrevive a la cura: con Bot 4 en `INPUT_NOT_EVALUABLE` el diferencial de ese test es
Bot 2 **sin hallazgos**, así que el veredicto sigue sin ser `APROBADO-PARA-ENTREGA` por la fila 4.

## Re-anclaje esperado: **0 aserciones** (corregido desde «0–2»)

Medido, no heredado: las tres aserciones construyen el report con estado de la familia `OK_*`
(`test_fase_0_ac20:216` → `_report(..., status=ReviewerStatus.OK_WITH_FINDINGS)` por defecto;
`test_fase_b:472` → `assert bot4.status is ReviewerStatus.OK_WITH_FINDINGS` justo antes). Retirar la
exigencia `is_ok` de `verified_critical`/`verified_block` es **aditivo** para estados `OK_*`: el
predicado sigue siendo `True`. No hay aserción que re-anclar.

## Baseline pre-edición de la selección que se va a correr

```
$ PYTHONUTF8=1 ./venv/Scripts/python.exe -m pytest \
    tests/quality_gates/tribunal/test_fase_b_consumidores_contrato.py \
    tests/test_fase_0_ac20_evidencia_veredicto.py -q
47 passed, 8 warnings in 1.50s
```

Selección de validación de la fase: `tests/quality_gates/tribunal/` (incluye el archivo nuevo
`test_fase_c2_ac19_critical_bloquea_sin_is_ok.py`) + `./venv/Scripts/python.exe -m pytest
tests/test_fase_0_ac20_evidencia_veredicto.py` + `scripts/run_all_validations.py --quick`.
