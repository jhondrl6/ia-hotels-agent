# FASE-T2-A: Revisor de Diagnóstico Interno (Bot 1)

**ID**: TRIBUNAL-OFFLINE-2026-09-09 / FASE-T2-A
**Objetivo**: Implementar `tribunal/diagnosis_reviewer.py` — revisor determinista que verifica trazabilidad brecha→pain_id, fuente declarada, y respeto a `is_coherent`. Produce `revision_diagnostico.json` que alimenta el acta del Juez.
**Dependencias**: FASE-T1 ✅ (contrato de acta estable; D-T1.3 resuelta — primer piso → `first_floor_rule`, P6.5 liberada para Bot 4)
**Complejidad técnica**: **MEDIA** — módulo determinista, lecturas de artefactos JSON, sin LLM
**Modo de ejecución**: **DIRECTO** (agente principal). NO delegable: la fase crea un módulo **y corre tests que importan el proyecto**; el venv es Windows accedido desde WSL ⟹ ejecutor v2.20.0, branch «imports del proyecto + venv Windows → DIRECTA… NO delegar a subagentes» (lección FASE-4 BUGS-ONBOARDING-ADR: ~40 iteraciones perdidas).
**Skill**: `phased_project_executor.md` v2.20.0

---

## Contexto

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-T1 | ✅ Completada (contrato de acta definido) |
| FASE-T2-A | ← ESTA FASE |

### Base Técnica Disponible

- **Contrato de acta** (definido en T1): `modules/quality_gates/tribunal/judge.py` — el Juez agrega reportes de revisores
- **Artefactos que Bot 1 lee**:
  - `01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md` (diagnóstico generado)
  - `coherence_validation.json` (veredicto de coherencia)
  - `pain_ledger.json` (brechas detectadas)
  - `pain_ledger_resolved.json` (brechas con assets mapeados)
  - `gate_report_*.json` (resultado de publication gates)
- **Módulos de referencia** (NO reimplementar):
  - `modules/data_validation/cross_validator.py`
  - `modules/asset_generation/pain_ledger.py`

### Lecciones aplicables

| Lección | Aplicación |
|---------|-----------|
| R2.4: AC legible en artefacto | Test de serialización que lee el JSON del writer real |
| S-I1: `critical_recall = 1.0` con `details: {}` | Bot 1 distingue recall fundado de vacuo. **Nota (auditoría 2026-09-09)**: el gate YA serializa `details.critical_issues_count` + `recall_basis` en código v4.75.0 — en la corrida E2E NO dispara; AC6 es test-level con fixture. Los `gate_report_*.json` retro (FASE-D/FASE-I) tampoco traen `severity` por gate: tratarla como opcional |
| Tribunal NO reimplementa gates | Bot 1 LEE `coherence_validation.json`, no re-ejecuta el gate |
| N11/P9 cerrado (v4.75.0) | `is_coherent` ya se respeta en el pipeline; Bot 1 verifica que el artefacto lo refleja |

---

## Tareas

### Tarea 1: Implementar `diagnosis_reviewer.py`

**Objetivo**: Clase `DiagnosisReviewer` con método `review() → DiagnosisFindings`.

**Archivo a crear**:
- `modules/quality_gates/tribunal/diagnosis_reviewer.py`

**Responsabilidades del Bot 1** (§5 del CONTEXT):
1. Brechas diagnosticadas aparecen en `pain_ledger` con `pain_id` trazable
2. Cada brecha tiene fuente declarada (no inferida silenciosamente)
3. Cifras de fuga calculadas desde inputs declarados (no defaults)
4. Diagnóstico no afirma cosas que gates no pudieron validar
5. Brechas críticas con prioridad correcta
6. **S-I1**: `critical_recall` con `details: {}` es vacuo, no fundado

**Salida**: `revision_diagnostico.json`
```json
{
    "reviewer": "diagnosis_reviewer",
    "clause": "P6.1",
    "findings": [
        {
            "severity": "CRITICAL" | "WARNING" | "INFO",
            "clause": "P6.1",
            "finding_type": "UNTRACEABLE_PAIN" | "UNDECLARED_SOURCE" | "VACUOUS_RECALL" | "UNSUPPORTED_CLAIM",
            "source_artifact": "pain_ledger.json",
            "description": "...",
            "pain_id": "..." 
        }
    ],
    "summary": {"total_findings": N, "critical": N, "warning": N},
    "verdict_recommendation": "APROBADO" | "DEVOLVER-PRUEBAS" | "BLOQUEAR"
}
```

**Criterios de aceptación**:
- [ ] Clase `DiagnosisReviewer` con método `review(v4_audit_dir) → dict`
- [ ] Lee los 5 artefactos listados (resuelve timestamped por glob)
- [ ] Detecta recall vacuo (S-I1): `details` sin `critical_issues_count` → finding `VACUOUS_RECALL`
- [ ] NO importa internals de gates (solo lee sus JSONs de output)

### Tarea 2: Tests

**Archivo a crear**:
- `tests/quality_gates/tribunal/test_diagnosis_reviewer.py`

**Tests obligatorios**:
| Test | Criterio |
|------|----------|
| `test_review_produces_findings_list` | Salida tiene clave `findings` como lista |
| `test_vacuous_recall_detected` | Fixture con `critical_recall: 1.0, details: {}` → finding `VACUOUS_RECALL` |
| `test_founded_recall_not_flagged` | Fixture con `details.critical_issues_count: 3` → sin finding de recall |
| `test_untraceable_pain_detected` | Brecha en diagnóstico sin `pain_id` en ledger → finding |
| `test_serialization_to_disk` | Escribe JSON real, lo re-lee, verifica claves (R2.4) |
| `test_resolves_timestamped_gate_report` | Glob resuelve `gate_report_*.json` |
| `test_does_not_import_gate_internals` | Grep: no importa `publication_gates` |

**Nota (auditoría 2026-09-09)**: AC6 se certifica con fixture (`critical_recall: 1.0, details: {}` → `VACUOUS_RECALL`). En la corrida E2E el gate ya declara `details.critical_issues_count`, así que el finding no aparecerá — VERIFY ya trae el caveat "si aplica en esta corrida" para AC6.

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/tribunal/test_diagnosis_reviewer.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

### Tarea 3: Docs + Post-ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-T2-A \
    --desc "Bot 1: revisor de diagnóstico interno (trazabilidad pain_id, fuente declarada, recall vacuo S-I1)" \
    --archivos-nuevos "modules/quality_gates/tribunal/diagnosis_reviewer.py,tests/quality_gates/tribunal/test_diagnosis_reviewer.py" \
    --tests "7" \
    --check-manual-docs
```

Actualizar: `09-documentacion-post-proyecto.md` (Secciones A, B, D) + `10-analisis-post-implementacion.md` (Resumen + Lecciones).

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: marcar FASE-T2-A ✅
2. **`README.md` del plan**: actualizar progreso
3. **`09-documentacion-post-proyecto.md`**: Secciones A, B, D
4. **`10-analisis-post-implementacion.md`**: fila T2-A + lecciones (mínimo 3)
5. **`evidence/FASE-T2-A/`**: baseline pre/post
6. **`06-checklist-implementacion.md`**: marcar items T2-A

---

## Criterios de Completitud (CHECKLIST)

- [ ] **AC5**: `revision_diagnostico.json` con `findings[]` (test de serialización verde)
- [ ] **AC6**: Recall vacuo marcado como `VACUOUS_RECALL` (test verde)
- [ ] **NR1**: `passed_post = passed_pre + tests nuevos` (baseline pre/post)
- [ ] **NR3**: `run_all_validations.py --quick` TOTAL PASS
- [ ] **NR4**: No reimplementa gates (test verde)
- [ ] **Post-ejecución completada**

---

## Restricciones

- **Presupuesto**: 35 iteraciones, corte en commit de código (R2.1)
- **NO ejecutar v4complete**
- **NO modificar ROADMAP.md ni `main.py`**
- **NO modificar `judge.py`** (el contrato de T1 es estable; si necesita cambio, documentar en seguimientos)
- **NO usar números de línea** (R2.2)
- **DIRECTO (no delegable)**: los tests importan el proyecto y el venv es Windows/WSL. Si excepcionalmente se demuestra que los tests son stdlib-only, la delegación requeriría que el parent ejecute los tests (el subagente no corre el venv Windows).
