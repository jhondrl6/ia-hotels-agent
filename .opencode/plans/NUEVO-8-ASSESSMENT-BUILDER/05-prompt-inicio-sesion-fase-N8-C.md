# 05-prompt-inicio-sesion-fase-N8-C

**Fase:** N8-C — Simplificar extractores + Eliminar campos muertos + Tests
**Plan:** NUEVO-8-ASSESSMENT-BUILDER
**Sesión:** Nueva (fresh)
**Iteraciones máx:** 60
**Depende de:** N8-B ✅ (AssessmentBuilder implementado, main.py migrado)
**Bloquea a:** N8-D
**Tipo:** DIRECTA (código + tests, sin comandos largos)

---

## Objetivo

Simplificar los 5 extractores multi-path en `publication_gates.py` a acceso directo (aprovechando que el assessment dict ahora tiene schema validado), eliminar campos muertos/zombie/fantasma, y actualizar tests.

## Contexto de Fases Anteriores

**N8-A:** `AssessmentPayload` dataclass creado con schema tipado.
**N8-B:** `AssessmentBuilder` implementado con API fluida. `main.py:2663-2754` migrado al builder. El assessment dict que reciben los gates ahora tiene TODOS los campos en ubicaciones predecibles (ya no hay 3 etapas de construcción dispersas).

**Cambio clave:** Con el builder, los extractores ya no necesitan 4-6 fallbacks. Cada campo está donde el builder lo pone. Ejemplo: `evidence_coverage` siempre está en `assessment["evidence_coverage"]`, no en 6 ubicaciones diferentes.

## Tareas

### T1: Simplificar 5 extractores multi-path a acceso directo
- Archivo: `modules/quality_gates/publication_gates.py` (MODIFICAR ~129 líneas → ~30 líneas)
- Reemplazar cada extractor con acceso directo + type check:

**1. `_extract_conflicts` (L1138-1149, ~12 líneas → ~5):**
```python
def _extract_conflicts(self, assessment: Dict[str, Any]) -> List[Dict]:
    """Extract conflicts from validated assessment."""
    vs = assessment.get("validation_summary", {})
    return vs.get("conflicts", []) if isinstance(vs, dict) else []
```

**2. `_extract_evidence_coverage` (L1151-1183, ~33 líneas → ~5):**
```python
def _extract_evidence_coverage(self, assessment: Dict[str, Any]) -> float:
    """Extract evidence coverage from validated assessment."""
    try:
        return float(assessment.get("evidence_coverage", 0.0))
    except (TypeError, ValueError):
        return 0.0
```

**3. `_extract_financial_data` (L1185-1209, ~25 líneas → ~5):**
```python
def _extract_financial_data(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
    """Extract financial data from validated assessment."""
    fd = assessment.get("financial_data", {})
    return fd if isinstance(fd, dict) else {}
```

**4. `_extract_coherence_score` (L1211-1242, ~32 líneas → ~5):**
```python
def _extract_coherence_score(self, assessment: Dict[str, Any]) -> float:
    """Extract coherence score from validated assessment."""
    try:
        return float(assessment.get("coherence_score", 0.0))
    except (TypeError, ValueError):
        return 0.0
```

**5. `_extract_critical_recall` (L1246-1272, ~27 líneas → ~8):**
```python
def _extract_critical_recall(self, assessment: Dict[str, Any]) -> Optional[float]:
    """Extract critical recall from validated assessment."""
    # Direct field (preferred)
    if "critical_recall" in assessment:
        try:
            return float(assessment["critical_recall"])
        except (TypeError, ValueError):
            pass
    # Calculate from critical issues
    critical_issues = assessment.get("critical_issues", [])
    if critical_issues:
        return 1.0  # All critical issues were detected (builder guarantees completeness)
    return None
```

**IMPORTANTE:** El cálculo `len(detected)/len(critical_issues)` anterior (L1267-1270) era tautológico porque `critical_issues_detected` y `critical_issues` eran el mismo array. Como N8-A/N8-B eliminaron `critical_issues_detected`, el nuevo cálculo es: si hay critical_issues, recall = 1.0 (el builder garantiza que todos los critical_issues están detectados). Si no hay, return None.

### T2: Eliminar campos muertos/zombie/fantasma + limpiezas post-refactor
- Archivos: `main.py`, `modules/quality_gates/publication_gates.py`, `modules/assessment_builder.py`

**2a. Eliminar `consistency_report` del assessment dict (L2838):**
- `main.py L2838`: eliminar la línea `assessment['consistency_report'] = consistency_report.to_dict()`
- **Verificación previa:** `consistency_report` SÍ era consumido por `_extract_coherence_score` (L1236-1238). PERO con la simplificación de T1, el extractor ya no busca en `coherence_report` — solo usa `assessment["coherence_score"]`. Por lo tanto, la inyección en L2838 es ahora genuinamente dead code.
- **CUIDADO:** La variable `consistency_report` sí se usa directamente en el summary JSON (L3043-3047) — NO eliminar ese uso. Solo eliminar la línea que la inyecta en el assessment dict.

**2b. Eliminar campos zombie del builder (ya eliminados en N8-A):**
- Verificar que `quality_gate_issues`, `quality_gate_blockers`, `quality_gate_warnings` NO están en `AssessmentPayload`
- Verificar que `coherence_checks`, `coherence_errors`, `coherence_warnings` NO están en `AssessmentPayload`
- Verificar que `critical_issues_detected` NO está en `AssessmentPayload`
- Verificar que `metrics` NO está en `AssessmentPayload` (0 consumidores post-simplificación)
- Verificar que `coherence_report` NO está en `AssessmentPayload` (0 consumidores post-simplificación)

**2c. Agregar campos fantasma al builder (ya en N8-A):**
- Verificar que `proposal_services` y `hotel_url` SÍ están en `AssessmentPayload`
- Verificar que `site_presence_report` SÍ se inyecta vía `builder.with_site_presence()`

**2d. Simplificar `hotel_url or url` en el gate (L836):**
- Archivo: `modules/quality_gates/publication_gates.py`
- L836 actual: `hotel_url = assessment.get("hotel_url") or assessment.get("url")`
- Después del builder, `hotel_url` **siempre** existe en el dict (el builder lo setea en `with_core()`). El fallback `or assessment.get("url")` es código muerto.
- Cambiar a: `hotel_url = assessment.get("hotel_url") or assessment.get("url", "")` (mantener defensivo pero simplificado)
- O más directo: `hotel_url = assessment.get("hotel_url", "")` ya que el builder garantiza el campo

**2e. (VERIFICACIÓN) Sin `metrics` ni `coherence_report` en `_to_dict()`:**
- Revisar `modules/assessment_builder.py` — `_to_dict()` usa `dataclasses.asdict()` que solo serializa los campos del dataclass. Como `metrics` y `coherence_report` no están en `AssessmentPayload`, no aparecen en el dict de salida.

### T3: Actualizar tests de integración para extractores simplificados
- Archivo: `tests/quality_gates/test_publication_gates.py` (MODIFICAR si existe, o crear tests inline)
- Si no existe archivo de tests para publication_gates, buscar tests existentes con:
  ```bash
  grep -r "extract_conflicts\|extract_evidence_coverage\|extract_financial_data\|extract_coherence_score\|extract_critical_recall" tests/
  ```
- Si existen tests: actualizarlos para que usen el assessment dict del builder (con campos en ubicaciones canónicas)
- Si NO existen tests: crear `tests/quality_gates/test_extractors_simplified.py` con al menos 5 tests:
  1. `test_extract_conflicts_direct` — verifica acceso directo a validation_summary.conflicts
  2. `test_extract_evidence_coverage_direct` — verifica acceso directo a evidence_coverage
  3. `test_extract_financial_data_direct` — verifica acceso directo a financial_data
  4. `test_extract_coherence_score_direct` — verifica acceso directo a coherence_score
  5. `test_extract_critical_recall_direct` — verifica cálculo con critical_issues

### T4: Ejecutar test suite completa + log_phase
- Ejecutar tests del assessment builder: `./venv/Scripts/python.exe -m pytest tests/test_assessment_builder.py -v`
- Ejecutar tests de extractores: `./venv/Scripts/python.exe -m pytest tests/quality_gates/ -v`
- Ejecutar test suite completa: `./venv/Scripts/python.exe -m pytest tests/ -x --timeout=120` (fail fast)
- Esperado: 0 regresiones. Si hay fallos en otros tests, analizar y corregir.
- Si hay fallos en tests que dependen de campos zombie eliminados → actualizar esos tests

## Criterios de Completitud
- [ ] T1: 5 extractores simplificados (~129 → ~30 líneas) — acceso directo
- [ ] T2: Campos muertos/zombie eliminados; consistency_report L2838 eliminado; hotel_url or url simplificado; verificado que metrics y coherence_report no están en el dict
- [ ] T3: Tests de extractores actualizados/creados (5+ tests)
- [ ] T4: Test suite completa 0 regresiones + log_phase

## Restricciones
- Máximo 60 iteraciones
- **NO modificar la lógica de los gates** — solo los extractores
- **NO ejecutar v4complete**
- **NO modificar AGENTS.md, ROADMAP.md, CHANGELOG.md** (eso es N8-RELEASE)
- Python path: `./venv/Scripts/python.exe`
- Working directory: `/mnt/c/Users/Jhond/Github/iah-cli`

## Post-Ejecución (OBLIGATORIO)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli && \
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase N8-C \
    --desc "Extractores simplificados + campos muertos eliminados — NUEVO-8" \
    --archivos-nuevos "tests/quality_gates/test_extractors_simplified.py" \
    --archivos-mod "modules/quality_gates/publication_gates.py,main.py,modules/assessment_builder.py" \
    --tests "5" \
    --check-manual-docs
```

## Próxima sesión
N8-D: E2E v4complete Hotel Castilla Real + Verificación
