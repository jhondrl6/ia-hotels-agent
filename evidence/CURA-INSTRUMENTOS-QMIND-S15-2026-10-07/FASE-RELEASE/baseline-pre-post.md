# PRE / POST de la selección literal — FASE-RELEASE

Unidad e intérprete idénticos en los dos cortes: `./venv/Scripts/python.exe` (CPython 3.13 del venv) con
`PYTHONUTF8=1` declarado (S-CIM-10), corrida **sin tubería** y el `EXIT` leído del proceso.

Selección literal (las dos familias que el plan gobierna):

```
tests/test_validate_qmind_writeback_escritura.py
tests/test_build_lesson_index_s15_fecha_versionada.py
```

| Corte | Árbol | Resultado | EXIT | Crudo |
|---|---|---|---|---|
| PRE | `0f50ea4` (HEAD == `git ls-remote origin refs/heads/master`, medido al abrir) | **65 passed** (57 del write-back + 8 del control S15) | 0 | `00-pre_seleccion_apertura.txt` |
| POST | árbol de trabajo de esta sesión, **sin commit** (no hubo instrucción literal) | **65 passed** | 0 | `06b-post_seleccion.txt` |

## Resta comprobada (R2.7)

`suma_post − suma_pre = 65 − 65 = 0`, y la fase **no declara tests nuevos**: es una fase documental que no
tocó código. El caso que R2.7 prohíbe es la resta 0 **con** dientes declarados (baseline contaminado); aquí la
resta 0 es el resultado esperado y se publica con su motivo.

Ninguna aserción existente se re-bajó: `git diff` sobre los dos archivos de tests está vacío en esta sesión
(medido: 0 líneas modificadas en `tests/`).

## Consecuencia de la ausencia de commit (L-VCF-15)

El POST corrió en el **árbol de trabajo**. Como el operador no autorizó el commit, la verificación repetida
sobre el **árbol del commit** no existe en esta sesión y queda declarada como deber de la sesión que commitee:
ese verde no se puede dar por hecho.
