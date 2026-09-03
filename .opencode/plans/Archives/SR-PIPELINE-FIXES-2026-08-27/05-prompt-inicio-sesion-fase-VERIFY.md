# FASE-VERIFY — Certificación de ACs contra Evidencia E2E (DIRECTO)

**ID**: FASE-VERIFY
**Objetivo**: Certificar AC1-AC13 contra el output E2E de FASE-SR-H (verificación cruzada sobre artefactos reales, no sobre lo que dice el código ni sobre tests unitarios). Incluye diff antes/después vs baseline (L-NC12), greps residuales (L2, L16) y captura de ≥3 lecciones nuevas (L-NC11: E2E > unit tests). Produce el veredicto global "fixes superados SÍ/NO" que habilita el RELEASE.
**Dependencias**: FASE-SR-H ✅ (output completo en `evidence/FASE-SR-H/final/`).
**Complejidad**: Media · **Delegación**: ❌ DIRECTO — NO delegable (§4.6 del executor: ≥3 fases de implementación + E2E + ACs cross-fase; el juicio de certificación es del orquestador)
**Duración estimada**: 60-75 min · **Presupuesto**: 4 tareas + 0 comandos largos (R3)

## Reglas de Sesión (MANDATORIO)

- R1: Una fase por sesión. R2: máx. 60 iteraciones. R3: 4 tareas + 0 comandos largos.
- Python: `./venv/Scripts/python.exe`.

## Contexto

**Lectura previa obligatoria**: executor §4.6 (FASE-VERIFY condicional) + plan maestro §7 (AC1-AC13) + `10-analisis` §Matriz AC (Expected pre-cargado).

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-SR-A…SR-H | ✅ Completadas |

### Entrada de la Fase
- Output E2E: `evidence/FASE-SR-H/final/` (copia íntegra de `output/salentoreal_final_v4c/`)
- Baseline: `evidence/FASE-SR-H/baseline/` (corrida C pre-fix: NOT_READY)
- Matriz AC pre-cargada en `10-analisis` (columna Expected por AC1-AC13)

## Tareas

### T1: Certificación AC1-AC13 (Expected → Observed → Verdict)
**Criterios**:
- [ ] Por cada AC: evidencia citada (archivo + campo/valor) desde el output E2E — nunca desde código ni tests
- [ ] AC1 gate no bloquea por NO_BREACH · AC2 promesa pain_ledger+presence · AC3 unresolved idéntico · AC4 claims ciclan (reporte gates) · AC5 target_id canónico · AC6 detección schema correcta (audit ≥ 1 Hotel, incl. array JSON-LD; sin pain falso; exists_with_issues = presencia) · AC7 promised_assets_exist limpio + ausencia genuina vía fallback · AC8 varianza explicada · AC9 display sincronizado · AC10 financiera $6.57M/$4.04M/$1.26M · AC11 READY_FOR_PUBLICATION · AC12 01/02+ZIP sin BLOCKED_BY_GATES · AC13 guardián estático
- [ ] Veredicto por AC: SUPERADO / NO SUPERADO (con causa y fase responsable si falla)

### T2: Diff antes/después vs baseline (L-NC12)
**Criterios**:
- [ ] Tabla comparativa baseline C vs final: gates, coherencia, alignment, unresolved, assets, financiera
- [ ] Verificar que los fixes de SR-A…SR-G se reflejan en el E2E real, no solo en tests unitarios
- [ ] Cualquier regresión (algo que empeoró vs baseline) documentada con causa y fase

### T3: Greps residuales + guardián + regresión (L2, L16, AC13)
**Criterios**:
- [ ] Greps de residuos = 0: `_normalize_url_for_matching` (nombre erróneo del contexto original), "sin costo (fallback)", display strings de tier duplicados, criterios duplicados de unresolved
- [ ] Guardián estático AC13 pasa: `tests/test_main_static_guards.py`
- [ ] Suite de regresión 26/26: `tests/regression/`

### T4: Lecciones nuevas + cierre del análisis
**Criterios**:
- [ ] ≥3 lecciones nuevas (L-PF1+, formato qué pasó/por qué/qué lo previene) extraídas del E2E real
- [ ] `10-analisis` completo: matriz AC con Observed/Verdict, veredicto global, seguimientos actualizados
- [ ] `06-checklist` y `README.md` del plan → VERIFY ✅

## Tests Obligatorios

| Test | Comando | Criterio de Éxito |
|------|---------|-------------------|
| Guardián estático | `./venv/Scripts/python.exe -m pytest tests/test_main_static_guards.py -v > temp/fase_verify_tests1.txt 2>&1` | PASS (AC13) |
| Regresión permanente | `./venv/Scripts/python.exe -m pytest tests/regression/ -v > temp/fase_verify_tests2.txt 2>&1` | 26/26 |
| Validaciones | `./venv/Scripts/python.exe scripts/run_all_validations.py --quick` | TOTAL PASS |

## Post-Ejecución (OBLIGATORIO — antes de cerrar la sesión)

1. `dependencias-fases.md` §2 → ✅. 2. `README.md` → ✅. 3. `06-checklist` → VERIFY. 4. `09-documentacion` → B/E + Notas. 5. `10-analisis` → matriz AC final + veredicto global. 6. `evidence/FASE-VERIFY/` → matriz AC final + diffs + salidas de greps/tests. 7. Registro (SIN `--release`):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-VERIFY --desc "Certificacion AC1-AC13 contra E2E Salento Real; veredicto fixes superados; >=3 lecciones nuevas" --archivos-mod "(ninguno - fase de verificacion)" --tests "<N reales>" --check-manual-docs
```
8. NO regenerar DOMAIN_PRIMER aquí (es del RELEASE).

## Criterios de Completitud (CHECKLIST)

- [ ] Matriz AC completa (13/13 con evidencia citada)
- [ ] Diff antes/después sin regresiones ocultas
- [ ] Greps residuales = 0
- [ ] ≥3 lecciones nuevas capturadas
- [ ] Veredicto global registrado en `10-analisis`

## Restricciones

- **NO modificar código** (cualquier hallazgo → seguimiento documentado o fase de contingencia; NO hotfix aquí).
- **NO ejecutar v4complete/v4audit** (la única corrida del plan ya ocurrió en SR-H).
- Verificación sobre evidencia E2E real, no sobre outputs de tests unitarios.
- NO delegar a subagente (§4.6 del executor); NO usar `--release` en log_phase_completion.
- AC10: si la financiera diverge del baseline → veredicto NO SUPERADO con causa (bloquea RELEASE).
