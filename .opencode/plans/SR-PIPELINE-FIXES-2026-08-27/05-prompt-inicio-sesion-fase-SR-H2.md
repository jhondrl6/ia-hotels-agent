# FASE-SR-H2 — Hotfix gate `critical_recall` + Verificación E2E (DELEGABLE corrida)

**ID**: FASE-SR-H2
**Objetivo**: Corregir el bug latente expuesto por la corrida E2E de FASE-SR-H: `_extract_critical_recall` colapsa "lista crítica vacía" (resultado favorable) con "dato ausente" → BLOCKED espurio ("metric not found") que impidió READY_FOR_PUBLICATION (AC11). Fix mínimo + tests de contrato + UNA corrida de verificación única (desviación pre-registrada D-PF7 al §9 del plan maestro) con smoke 7 checks → evidencia para que FASE-SR-VERIFY certifique AC11/AC12.
**Dependencias**: FASE-SR-H ✅ (corrida ejecutada, post-mortem en `10-analisis` §Resumen E2E).
**Complejidad**: Baja-Media · **Delegación**: fix DIRECTO · corrida de verificación ✅ DELEGABLE (Protocolo de Subagente §Paso-6)
**Duración estimada**: 30-40 min · **Presupuesto**: 3 tareas + 1 comando largo (la corrida de verificación ES el comando largo)

## Reglas de Sesión (MANDATORIO)

- R1: Una fase por sesión. R2: máx. 60 iteraciones. R3: **3 tareas + 1 comando largo**.
- Python: `./venv/Scripts/python.exe`. Suites pytest: NUNCA la suite completa en un proceso (memoria `test_proposal_generator.py` ~8GB); solo archivos específicos con salida redirigida a archivo.
- **DELEGACIÓN de la corrida**: `delegate_task(timeout=900, notify_on_complete=True, toolsets=["terminal"])` — el prompt del subagente debe ser COMPLETO e incondicional (comando exacto, cwd, qué capturar si falla). Smoke y evidencia: del orquestador, síncronos.

## Contexto

**Lectura previa obligatoria**: `10-analisis` §Resumen E2E (post-mortem completo) + lección **L-PF10**.

### Diagnóstico (verificado contra evidencia, NO re-investigar)

- Cadena causal: SR-E corrigió el falso negativo de schema → `critical_issues = []` (resultado bueno) → [`_extract_critical_recall`](file:///c:/Users/Jhond/Github/iah-cli/modules/quality_gates/publication_gates.py) (L1850-1862) retorna `None` para lista vacía → `_critical_recall_gate` BLOCKED "metric not found" → GATE BLOCKING ACTIVE eliminó docs 01/02 y generó BLOCKED_BY_GATES.md → NOT_READY (smoke SR-H: 5/7).
- El comentario existente del código ("All critical issues were detected (builder guarantees completeness)", L1861) ya establece la semántica correcta para lista NO vacía → 1.0; la lista vacía merece el MISMO tratamiento cuando el audit sí se ejecutó.

### Criterio técnico pre-decidido (el builder ya provee la distinción)

`AssessmentBuilder` (`modules/assessment_builder.py` ~L200-213): con `audit_result=None` → `audit_schema={}` Y `critical_issues=[]`; con audit presente → `audit_schema` NO vacío y `critical_issues = audit_result.critical_issues or []`. Por tanto:

| Estado del assessment | `_extract_critical_recall` | Gate |
|---|---|---|
| `critical_recall` directo (numérico convertible) | ese valor | umbral 0.90 (hoy) |
| `critical_recall` inválido + `critical_issues` no vacío | 1.0 | PASSED (hoy) |
| `critical_issues == []` y `audit_schema` NO vacío | **1.0** + traza en details | **PASSED** (fix) |
| `critical_issues == []` y `audit_schema == {}` (audit ausente) | `None` | **BLOCKED real** (dato ausente — L-SR5: ciclar o escalar, nunca silenciar) |
| Ambas keys ausentes (`{}`) | `None` | BLOCKED (hoy, test existente) |

Trazabilidad: el branch PASSED del gate debe incluir `details={"critical_issues_count": 0, "recall_basis": "audit_present_no_critical_issues"}` (solo en el camino nuevo; el JSON de gate_report ya lleva `details` — sin consumidores estrictos, riesgo 0).

### Alcance EXACTO (solo estos archivos)

- `modules/quality_gates/publication_gates.py` — solo `_extract_critical_recall` + `details` en `_critical_recall_gate`.
- `tests/quality_gates/test_extractors_simplified.py` — ACTUALIZAR `test_extract_critical_recall_empty_critical_issues` (L167-171: asume contrato viejo → lista vacía+audit → ahora 1.0) y cubrir los 2 caminos nuevos.
- `tests/quality_gates/test_publication_gates.py` — tests de gate para los 2 caminos nuevos.

**Prohibido**: tocar `main.py`, `assessment_builder.py`, cualquier otro gate, la capa financiera, `agent_harness/`, config. Versión: el fix va dentro de la release 4.73.0 ya prevista (sin bump aparte).

## Tareas

### T1: TDD rojo — tests de contrato (ANTES del fix)
**Criterios**:
- [ ] En `test_extractors_simplified.py` (`TestExtractCriticalRecall`): reemplazar `test_extract_critical_recall_empty_critical_issues` por `test_extract_critical_recall_empty_with_audit_present` (espera 1.0) + `test_extract_critical_recall_empty_without_audit` (espera None). Ejecutar → ambos ROJOS contra código actual.
- [ ] En `test_publication_gates.py`: `test_empty_critical_issues_with_audit_passes` (gate → PASSED, value 1.0) + `test_empty_critical_issues_without_audit_blocks` (gate → BLOCKED, "not found"). Ejecutar → ROJOS.

### T2: Fix mínimo + greens + regresión
**Criterios**:
- [ ] Implementar el criterio de la tabla de Contexto en `_extract_critical_recall` (máx ~10 líneas; mantener el docstring, actualizar la semántica de lista vacía en él).
- [ ] `details` con traza en el branch PASSED de `_critical_recall_gate` (camino lista vacía).
- [ ] Los 4 tests nuevos VERDES; suites de regresión aisladas con salida a archivo: `tests/quality_gates/test_publication_gates.py` + `tests/quality_gates/test_extractors_simplified.py` + `tests/test_publication_gates_presence.py` + `tests/quality_gates/test_gate_presence.py` → 0 fallos nuevos (fallos preexistentes: certificar contra HEAD con `git stash` NO permitido; usar `git show HEAD:archivo` para contrastar si aparece alguno).
- [ ] Grep residual: `_extract_critical_recall` no tiene otros consumidores fuera de `publication_gates.py` (verificar, documentar).

### T3: Corrida de verificación única (comando largo — DELEGAR)
**Criterios**:
- [ ] **Desviación pre-registrada D-PF7** al §9 del plan maestro (una corrida ADICIONAL post-hotfix): solo si T2 está verde. Output NUEVO para no pisar evidencia: `output/salentoreal_final_v4c_h2`.
- [ ] Ejecutar (delegado, en el repo): `./venv/Scripts/python.exe main.py v4complete --url "https://www.hotelsalentoreal.com/" --output output/salentoreal_final_v4c_h2` — URL canónica EXACTA (L-SR2).
- [ ] 1 corrida; si falla: NO reintentar → `evidence/FASE-SR-H2/failure.log` + escalar a decisión.
- [ ] Copiar INMEDIATAMENTE el output → `evidence/FASE-SR-H2/final/` + log → `evidence/FASE-SR-H2/corrida.log` (Protocolo de Evidencia Proactiva).
- [ ] Re-ejecutar smoke: `./venv/Scripts/python.exe temp/fase_sr_h_smoke.py evidence/FASE-SR-H2/final/v4_complete` → expectativa **7/7** (veredicto READY, docs 01/02 presentes, financiera idéntica al baseline). Guardar → `evidence/FASE-SR-H2/smoke_result_h2.json`. Si ≠ 7/7: documentar con causa y fase responsable, NO re-correr.

## Tests Obligatorios

| Test | Artefacto | Criterio de Éxito |
|------|-----------|-------------------|
| 4 tests de contrato (T1) | `tests/quality_gates/` | Rojos → verdes tras fix; regresión aislada 0 fallos nuevos |
| Smoke 7 checks (T3) | `evidence/FASE-SR-H2/final/` | 7/7 contra baseline (o fallas documentadas con causa) |

## Post-Ejecución (OBLIGATORIO — antes de cerrar la sesión)

1. `dependencias-fases.md` §2 → ✅ H2 (y §4: VERIFY depende de H2). 2. `README.md` → ✅ H2. 3. `06-checklist` → H2. 4. `09-documentacion` → B/D/E + Notas. 5. `10-analisis` → seguimiento `critical_recall` → ✅ RESUELTO (H2) + L-PF10 anotada "fix confirmado en corrida H2" + **D-PF7** en §Decisiones (desviación §9: corrida de verificación post-hotfix) + Métricas: readiness de corrida H2. 6. Registro (SIN `--release`):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-SR-H2 --desc "Hotfix _extract_critical_recall (lista vacia + audit presente = recall 1.0 con traza; audit ausente = BLOCKED real) + corrida de verificacion unica (D-PF7) + smoke 7/7" --archivos-mod "modules/quality_gates/publication_gates.py; tests/quality_gates/test_extractors_simplified.py; tests/quality_gates/test_publication_gates.py" --tests "4 contrato nuevos + regresion aislada + smoke 7 checks" --check-manual-docs
```
7. NO regenerar DOMAIN_PRIMER (es del RELEASE).

## Criterios de Completitud (CHECKLIST)

- [ ] Fix implementado SOLO en los 3 archivos del alcance; TDD rojo→verde documentado
- [ ] Regresión aislada 0 fallos nuevos
- [ ] Corrida de verificación exactamente 1 vez; evidencia copiada ANTES de cerrar la sesión
- [ ] Smoke 7/7 (o fallas documentadas con causa y fase responsable)
- [ ] Docs post-fase completos (1-7), D-PF7 registrada

## Restricciones

- NO re-ejecutar `v4complete` salvo la corrida de verificación única de T3 (D-PF7). Prohibido v4audit, scrapers sueltos.
- URL EXACTA: `https://www.hotelsalentoreal.com/` (L-SR2).
- Capa financiera INTACTA ($6.57M/$4.04M/$1.26M = referencia).
- NO usar `--release` en log_phase_completion.
- La evidencia de SR-H (`evidence/FASE-SR-H/final/`) NO se modifica: es el registro del estado pre-fix.
- Si el smoke H2 revela cualquier bloqueo NUEVO distinto de critical_recall: documentar y escalar a decisión (post-mortem en `10-analisis`); NO ampliar esta fase.
