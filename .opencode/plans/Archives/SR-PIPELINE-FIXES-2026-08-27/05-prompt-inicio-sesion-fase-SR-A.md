# FASE-SR-A — Helper único `compute_unresolved()` + Guardián Estático L-SR1

**ID**: FASE-SR-A
**Objetivo**: Eliminar la divergencia N1 (gate_report `unresolved=4` vs delivery_quality_report `unresolved=1` en el MISMO run) unificando el conteo en UN helper `AlignmentResult.compute_unresolved()` consumido por ambos reportes; y crear el test estático AST guardián L-SR1 contra símbolos no definidos en ramas no ejercitadas de `main.py`.
**Dependencias**: Ninguna (primera fase del plan SR-PIPELINE-FIXES-2026-08-27).
**Complejidad**: Media · **Delegación**: ❌ DIRECTO (código+tests con venv; §Regla-de-Decisión-código+tests del executor)
**Duración estimada**: 45-60 min · **Presupuesto**: ~15-20 iteraciones de trabajo + ~15 de verificación/docs (R2: máx. 60)

## Reglas de Sesión (MANDATORIO)

- R1: Una fase por sesión. No iniciar otra fase.
- R2: Máximo 60 iteraciones. Si se alcanza, marcar `⏳ INCOMPLETA` con checkpoint en `dependencias-fases.md` §2 y cerrar sesión (evidencia primero).
- R3: Esta fase = 4 tareas + 0 comandos largos. NO ejecutar v4complete/v4audit.
- Python: `./venv/Scripts/python.exe` SIEMPRE.

## Contexto

**Lectura previa obligatoria**: `/.opencode/context/Historico/CONTEXT-SALENTOREAL-V4COMPLETE-EJECUCION-2026-08-27.md` (§4.3, §9 #9, §9.5.2 N1) + `01-plan-maestro.md` de este plan (§8 Restricciones) + `10-analisis-post-implementacion.md` (lecciones capitalizadas).

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| Preparación | ✅ Completada (2026-08-27) |

### Base Técnica Disponible (hallazgo N1 verificado contra código vivo)
- `modules/quality_gates/alignment_result.py` — `class AlignmentResult` (L22): **DOS caminos** computan `unresolved`:
  - Camino 1: `from_alignment_report()` (L86): `unresolved_count = len(report.missing)` — usado por `publication_gates.py:862-903` (`verify_proposal_asset_alignment` + inyección de `asset_status_map`).
  - Camino 2: constructor desde matriz + SitePresence (L134/L139): `unresolved_count = sum(...)` — usado por `delivery_quality_report.py:~235` (reconstruye desde `proposal_asset_matrix.json` + SitePresence).
- Evidencia corrida C: `gate_report` dice "4 sin cubrir"; `delivery_quality_report` dice "1 sin cubrir"; `coverage_ratio` idéntico (0.4286). El mensaje interno de G9 está desalineado con sus propios datos.
- Fix H1 (logger) YA comiteado en d8e509d: `grep "logger\." main.py` = 0. Esta fase lo vuelve permanente (D-PF5).

## Tareas

### T1: Investigar los dos caminos de conteo
**Objetivo**: Confirmar el contrato de cada camino y cuál es el semánticamente correcto.
**Archivos**: `modules/quality_gates/alignment_result.py`, `modules/quality_gates/publication_gates.py` (L862-903), `modules/quality_gates/delivery_quality_report.py` (L~235), `modules/asset_generation/proposal_asset_alignment.py` (L783-789 concepto `actionable`).
**Criterios**:
- [ ] Documentar (en notas de sesión) qué cuenta cada camino y por qué difieren (4 vs 1)
- [ ] Identificar el path correcto según matriz + SitePresence (el que excluye NO_BREACH/present_in_production de "sin cubrir")

### T2: Implementar helper único
**Objetivo**: `AlignmentResult.compute_unresolved()` (o refactor a UN único path interno) consumido por AMBOS reportes. NO parchear solo el texto del mensaje (CONTEXT §9.5.2 N1).
**Archivos**: `modules/quality_gates/alignment_result.py`, `modules/quality_gates/publication_gates.py`, `modules/quality_gates/delivery_quality_report.py`.
**Criterios**:
- [ ] Un único lugar del código calcula `unresolved`
- [ ] Ambos reportes invocan el mismo helper
- [ ] El mensaje de G9 se deriva del helper (coherente con `unresolved` y `coverage_ratio`)

### T3: Test estático AST guardián L-SR1
**Objetivo**: Prevención permanente de la clase "símbolo no definido en rama no ejercitada" (H1/L-NC8/L-NC9). Decisión D-PF5.
**Archivos**: `tests/test_main_static_guards.py` (nuevo).
**Criterios**:
- [ ] `py_compile` de `main.py` OK
- [ ] AST de `main.py` no contiene atributos/referencias a `logger` (lista extensible `FORBIDDEN_SYMBOLS` en el test)
- [ ] Test documentado como guardián de la clase de bug H1

### T4: Tests + greps + docs
**Criterios**:
- [ ] Tests unitarios: `from_alignment_report` y el path de matriz+SitePresence producen el MISMO `unresolved` para el escenario corrida C (7 servicios: 2 LINKED, 1 present_in_production, 1 MISSING con pain, 3 NO_BREACH → mismo número esperado)
- [ ] Grep residuos: `grep "len(report.missing)"` y `grep "unresolved_count = sum"` solo dentro del helper único (0 conteos paralelos)
- [ ] `grep "logger\." main.py` = 0 (AC13)

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| helper unificado | `tests/quality_gates/test_alignment_result.py` (o archivo existente del módulo) | Ambos paths → mismo unresolved |
| guardián estático | `tests/test_main_static_guards.py` | Pasa; extensión AST |

**Comando de validación** (procesos aislados, salida a archivo — NUNCA suite completa):
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_alignment_result.py tests/test_main_static_guards.py -v > temp/fase_sr_a_tests.txt 2>&1
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO — antes de cerrar la sesión)

1. **`dependencias-fases.md`** §2: FASE-SR-A → ✅ con sesión/fecha/checkpoint.
2. **`README.md`** del plan: fila de progreso ✅.
3. **`06-checklist-implementacion.md`**: criterios de SR-A marcados.
4. **`09-documentacion-post-proyecto.md`**: Secciones B/D/E + Notas de la fase.
5. **`10-analisis-post-implementacion.md`**: fila Resumen de Ejecución + lecciones L-PF1 (mín. 1) + seguimientos.
6. **`evidence/FASE-SR-A/`**: diff de los 3 archivos + salida de tests.
7. **Registro de fase** (SIN `--release`):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-SR-A --desc "Helper AlignmentResult.compute_unresolved unificado + test estatico guardiano L-SR1" --archivos-mod "modules/quality_gates/alignment_result.py,modules/quality_gates/publication_gates.py,modules/quality_gates/delivery_quality_report.py" --archivos-nuevos "tests/test_main_static_guards.py" --tests "<N reales>" --check-manual-docs
```
8. **DOMAIN_PRIMER**: `./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer`

## Criterios de Completitud (CHECKLIST)

- [ ] Tests nuevos pasan (archivo de salida en temp/, no pipes)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Greps de residuos = 0
- [ ] `dependencias-fases.md` + README + checklist actualizados
- [ ] 09 + 10 actualizados (lecciones, métricas)
- [ ] Evidencia en `evidence/FASE-SR-A/`
- [ ] log_phase_completion ejecutado SIN --release

## Restricciones

- Máximo 60 iteraciones; NO ejecutar v4complete/v4audit.
- NO modificar `modules/financial_engine/` (capa financiera intacta).
- NO tocar `output/` ni `evidence/` históricos.
- NO usar `--release` en log_phase_completion (check "Prompts No Release").
- NO delegar a subagente (código+tests con venv → directo).
- Si surge un hallazgo fuera de alcance → registrarlo en Seguimientos de `10-analisis`, no expandir la fase.
