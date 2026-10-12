# Nota de cierre — FASE-C (CURA-COSTURA-TRIBUNAL-2026-10-11)

**Fecha**: 2026-10-12 · **Sesión**: FASE-C (una fase por sesión, R1) · **Base**: `4df81d3` (0 rutas sucias al abrir)
**Árbol al cerrar**: 3 archivos modificados (`judge.py`, `honesty_reviewer.py`, `contradiction_engine.py`), 4 nuevos (`evidence_tier.py` + 3 archivos de tests), 1 republicado (`.opencode/wiring_report.json`).

## Lo que se certificó y dónde se lee

| AC | Artefacto |
|----|-----------|
| AC11 | `modules/quality_gates/tribunal/evidence_tier.py` (el símbolo) + `tests/quality_gates/tribunal/test_evidence_tier_precedencia_unica_ac11.py` (12 funciones) + mutantes `M1-*` y `M2-*` en este directorio |
| AC12 | `tests/quality_gates/tribunal/test_acta_p6_2_no_niega_al_revisor_ac12.py` (4 funciones, sobre un acta generada con `ActaWriter`) + decisión diferida con dueño en `10-analisis` §Seguimientos |
| AC13 | `data_validation/contradiction_engine.py` (tri-estado + cuatro sitios) + `tests/test_contradiction_engine_reglas_no_callan_ac13.py` (13 funciones) + mutante `M3-*` |
| AC16 | `tests_baseline_pre.txt` (5280) y `tests_baseline_post.txt` (5309): delta **+29** verificado restando, igual a 12+4+13 |

Corridas: `pytest tests/quality_gates/tribunal/ tests/data_validation/ -q` → **460 passed / 9 skipped / 0 failed** (`pytest-seleccion-del-plan.txt`); selección del motor
(`tests/test_contradiction_engine_reglas_no_callan_ac13.py`, `tests/test_contradiction_engine.py`, `tests/test_consistency_checker.py`,
`tests/regression/test_hotel_visperas_conflicts.py`) → **55 passed / 0 failed** (`pytest-seleccion-motor.txt`); `run_all_validations.py --quick` → **13/13** tras republicar `wiring_report.json` (719 → 723: un módulo nuevo + tres archivos de tests).

## Declaración exigida por AC13: el verde del gate NO es evidencia de esta cura

`S-CST-1` (maestro §5, dueño **Operador**) sigue abierta: el gate blocking `hard_contradictions` cuenta
`assessment["validation_summary"]["conflicts"]`, y ese `ValidationSummary` se construye en `main.py` con `conflicts=[]`
**hardcoded**; el dataclass `Conflict` no tiene `severity` ni `type`; la clave alternativa `hard_contradictions_count` no tiene productor.
Consecuencia medida y declarada: **el motor ahora publica `LECTOR_FALLIDO`, pero ningún lector en producción lo consulta todavía**, así que
una regla que revienta deja el gate en verde igual que antes. Esta fase cura el silencio del motor (sus cuatro sitios de captura), no el
cableado. Quien lea `hard_contradictions: PASS` debe seguir sin poder afirmar que el motor operó.

## Mutantes: qué cayó y qué NO discrimina

| Clave | Ataque | Rojos | Lo que esto dice |
|-------|--------|-------|------------------|
| `M1-inversion-precedencia` | `MANIFEST` primero dentro del símbolo compartido | 2 | **La rama «coinciden» no discrimina la precedencia**: con las dos fuentes declarando el mismo valor, invertir el orden da el mismo tier. Lo que la discrimina es la **etiqueta de la fuente** (`test_falta_la_fuente_de_escenarios_y_aporta_el_manifest`) y la rama manifest-sola (`test_el_manifest_puede_declarar_solo_y_ambos_lo_leen`). Por eso los tests afirman `fuente`/`descripcion_fuente`, no solo el tier |
| `M2-silencio-sobre-presentacion` | `return []` bajo tier no declarado | 1 | El diente está en el hallazgo publicado, no en la ausencia de hallazgos |
| `M3-engine-sin-registrar` | tragar la excepción sin registrar el `RuleFailure` | 9 | Cae por la causa nombrada en los cuatro sitios. **No** lo detecta `test_el_motor_ya_no_imprime_por_stdout`: ese diente certifica la ausencia del `print` (que M3 no re-introduce), no el registro del estado; queda declarado para que nadie lo lea como cobertura del mutante |

M1 y M2 se aplicaron sobre el símbolo compartido: **no reproducen la divergencia original de N6** (dos precedencias en dos archivos), porque
desde esta fase ya no hay dos precedencias que diverjan. La divergencia histórica queda certificada por los dos tests cruzados
(`test_juez_y_bot4_coinciden_*`), que bajo el código viejo habrían dado `C` en el Juez y `UNKNOWN` en Bot 4.

## Rama no certificable, declarada

«MANIFEST y escenarios en desacuerdo» **no** se certifica con fixture (AC11). Medido el 2026-10-12: `build_dir` de
`test_honesty_reviewer_fidelidad_salida.py` acepta `breakdown=` pero ningún test lo pasa; el baseline SalentoReal
(`output/FASE-D_salentoreal_post_guard/`) no existe en este árbol, y en régimen ZIP-only nunca se descomprime
`deliveries/<hotel>/MANIFEST.json` (L-E2E.1). Forzarla con un fixture sintético certificaría una rama que producción no genera.

## Dos hallazgos de la fase, declarados

1. **El prompt de FASE-C ubicaba los tests del motor en `tests/data_validation/` y ahí no hay ninguno.** Medido:
   `ls tests/data_validation/` no trae tests del engine; los 16 existentes viven en `tests/test_contradiction_engine.py`, con
   `tests/test_consistency_checker.py` y `tests/regression/test_hotel_visperas_conflicts.py` como consumidores. La batería nueva
   (`test_contradiction_engine_reglas_no_callan_ac13.py`) se escribió **junto a los tests del engine** (raíz de `tests/`), y el comando de
   validación del prompt (`pytest tests/quality_gates/tribunal/ tests/data_validation/`) no recorre ni uno solo de los 13 dientes de AC13:
   se publicó su corrida aparte en `pytest-seleccion-motor.txt`.
2. **`_extract_precision_tier` conserva su propia precedencia (MANIFEST → escenarios → `UNKNOWN`).** No cae bajo AC11, que nombra
   `evidence_tier`, y unificarlo habría ampliado la fase sin AC que lo cubra. Queda como deuda visible: el mismo archivo lee ahora un tier
   por el símbolo compartido y el precision tier con una regla local de dos vías.

## Presupuesto (R2.1, unidad `tool calls`, auto-reportada)

~52 llamadas contra un presupuesto de ~45: **EXCEDIDO en ~7 (≈15 %)**. Lo consumió la medición del blast radius del cambio de precedencia
(checar fixture por fixture si algún arnés dependía del orden MANIFEST-primero, y verificar que la rama de desacuerdo no era producible), más
la depuración de un arnés propio que escribía el MANIFEST en el directorio equivocado y daba un falso rojo en la rama del fallback.
La unidad no la mide ningún instrumento de la casa.

## Cinco cortes, sin commit

Implementación terminada → verificación terminada → cierre documental → **listo para revisión** → espera de autorización.
Ningún `git commit` se ejecutó ni se ejecutará sin autorización explícita del Operador con pathspec.
