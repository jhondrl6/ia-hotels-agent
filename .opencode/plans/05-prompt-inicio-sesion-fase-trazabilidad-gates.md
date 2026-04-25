# Prompt de Inicio de Sesión: FASE-TRAZABILIDAD-GATES

**Proyecto**: Corrección Trazabilidad "Calidad Garantizada"  
**Fase**: 2 de 3 — Cableado de Publication Gates + Trazabilidad en Output  
**Sesión**: Nueva (1 fase por sesión)  
**Dependencia**: FASE-TRAZABILIDAD-DOCS completada (documentos ya reflejan 9 gates)

---

## Contexto

### Problema Raíz
`PublicationGatesOrchestrator` (1062 líneas, 9 gates, `modules/quality_gates/publication_gates.py`) está implementado pero **NUNCA se invoca** desde el flujo `v4complete`. El comando `main.py v4complete` ejecuta `CoherenceValidator` (1 solo gate) pero ignora los otros 8 gates. Resultado: 1062 líneas de código muerto y cero trazabilidad de calidad en los documentos generados.

### Evidencia
- `search_files` confirma: 0 imports de `publication_gates` fuera de `modules/quality_gates/`
- `main.py` L2157-2189: solo llama a `CoherenceValidator`, no a `PublicationGatesOrchestrator`
- El output `01_DIAGNOSTICO_Y_OPORTUNIDAD` muestra `coherence_score: 0.89` pero sin evidencia de gates ejecutados
- CERO tests para `PublicationGatesOrchestrator` (1062 líneas sin cobertura)

### Lo que YA funciona
- `CoherenceValidator` SÍ se ejecuta y su score (0.89) se pasa al generador de diagnóstico → NO TOCAR
- `v4complete` flow: FASE 1 (Hook) → FASE 2 (Validación) → FASE 3 (Financieros) → FASE 4 (Coherence Gate) → Diagnóstico → Assets → Propuesta

### API de PublicationGatesOrchestrator
```python
from modules.quality_gates.publication_gates import PublicationGatesOrchestrator, PublicationGateConfig

config = PublicationGateConfig()  # Usa defaults
orchestrator = PublicationGatesOrchestrator(config)

# run_all() requiere un assessment dict con estructura específica
results = orchestrator.run_all(assessment)  # → List[PublicationGateResult]
ready = orchestrator.is_ready_for_publication(results)  # → bool
blocking = orchestrator.get_blocking_gates(results)  # → List[PublicationGateResult]
```

### PublicationGateResult (dataclass)
```python
gate_name: str        # "hard_contradictions", "evidence_coverage", etc.
passed: bool          # True/False
status: GateStatus    # PASSED/FAILED/BLOCKED/WARNING
message: str          # Descripción humana
value: Any            # Valor verificado (ej: 0.89, 0.95, count)
suggestion: str       # Acción sugerida si falló
details: Dict[str, Any]
```

## Tareas Específicas

### T1: Construir `assessment` dict para PublicationGatesOrchestrator.run_all()

Examinar qué espera cada gate:

**Gate 1 - hard_contradictions**: busca `assessment["validation_summary"]` (dict o ValidationSummary) con campo `hard_contradictions_count`. También busca `assessment["conflicts"]` como lista de dicts con `severity="HARD"`.

**Gate 2 - evidence_coverage**: busca `assessment.get("evidence_coverage", 0)` o `assessment["validation_summary"].get("evidence_coverage", 0)`. Threshold: 95%.

**Gate 3 - financial_validity**: instancia `NoDefaultsValidator` internamente. Busca `assessment["financial_data"]` con keys como `adr_cop`, `rooms`, `occupancy_rate`, etc.

**Gate 4 - coherence**: busca `assessment.get("coherence_score", 0)`. Threshold: 0.8.

**Gate 5 - critical_recall**: busca `assessment["validation"].get("critical_recall_score", 0)` y `assessment["validation"].get("critical_recall_items", 0)`.

**Gate 6 - ethics**: instancia `EthicsGate` internamente. Busca `assessment["commercial_documents"]`.

**Gate 7 - content_quality**: instancia `DocumentQualityGate` internamente.

**Gate 8 - asset_confidence**: busca `assessment["asset_plan"]` con confianza de assets.

**Gate 9 - proposal_asset_alignment**: busca assets en proposal vs plan.

**Tarea T1**: Leer CADA método `_*_gate()` en `publication_gates.py` (líneas 202-900+) y documentar exactamente qué keys necesita cada uno en el `assessment` dict. Luego construir el dict en main.py ensamblando los datos disponibles en el contexto de v4complete.

### T2: Insertar llamada a PublicationGatesOrchestrator en main.py

Ubicación: Después de FASE 4 (Coherence Gate, ~L2190) y ANTES de regenerar el diagnóstico (~L2221).

```python
# FASE 4.5: Publication Gates (9 gates)
from modules.quality_gates.publication_gates import PublicationGatesOrchestrator, PublicationGateConfig

gate_config = PublicationGateConfig()
gate_orchestrator = PublicationGatesOrchestrator(gate_config)

# Construir assessment dict (según lo documentado en T1)
assessment = {
    "validation_summary": validation_summary,
    "coherence_score": pre_coherence_score,
    "financial_data": {...},
    "conflicts": [...],
    "asset_plan": asset_plan,
    ...
}

gate_results = gate_orchestrator.run_all(assessment)
gate_ready = gate_orchestrator.is_ready_for_publication(gate_results)

# Guardar gate report
gate_report_path = output_dir / "gate_report.json"
with open(gate_report_path, 'w') as f:
    json.dump([r.to_dict() for r in gate_results], f, indent=2)

print(f"🔒 Publication Gates: {sum(1 for r in gate_results if r.passed)}/{len(gate_results)} passed")
if not gate_ready:
    blocking = gate_orchestrator.get_blocking_gates(gate_results)
    for b in blocking:
        print(f"   ❌ {b.gate_name}: {b.message}")
```

### T3: Agregar sección de trazabilidad al documento de diagnóstico

Modificar `_prepare_template_data()` en `v4_diagnostic_generator.py` para aceptar `gate_results: Optional[List[Dict]] = None`.

Agregar template variable `${GATE_VALIDATION_SECTION}` que inserte al final del documento:

```markdown
## 🔒 Validación de Calidad (Publication Gates)

| Gate | Estado | Valor | Umbral |
|------|--------|-------|--------|
| hard_contradictions | ✅ PASSED | 0 conflictos | 0 max |
| evidence_coverage | ✅ PASSED | 97% | 95% min |
| financial_validity | ✅ PASSED | No defaults | required |
| coherence | ✅ PASSED | 0.89 | 0.80 min |
| critical_recall | ⚠️ WARNING | 85% | 90% min |
| ethics | ✅ PASSED | compliant | required |
| content_quality | ✅ PASSED | 92/100 | 80 min |
| asset_confidence | ⚠️ WARNING | 0.72 | 0.80 min |
| proposal_asset_alignment | ✅ PASSED | 7/7 | all |

*Gates ejecutados: 2026-04-24 19:08:26 | Orchestrator: PublicationGatesOrchestrator v1.0*
```

Pasar `gate_results` desde main.py en la llamada a `diagnostic_gen.generate()`.

### T4: Crear tests para PublicationGatesOrchestrator

Crear `tests/quality_gates/test_publication_gates.py`:

Tests mínimos (8-10 tests):
1. `test_orchestrator_initialization` — verifica 9 gates registrados
2. `test_run_all_returns_9_results` — verifica que run_all() retorna 9 resultados
3. `test_hard_contradictions_gate_pass` — sin conflictos → PASSED
4. `test_hard_contradictions_gate_block` — con HARD conflicts → BLOCKED
5. `test_coherence_gate_pass` — score 0.85 → PASSED
6. `test_coherence_gate_fail` — score 0.70 → FAILED
7. `test_is_ready_for_publication_all_pass` — todos PASSED → True
8. `test_is_ready_for_publication_one_fail` — un FAILED → False
9. `test_get_blocking_gates` — filtra correctamente
10. `test_gate_result_to_dict` — serialización correcta

### T5: Actualizar CHANGELOG.md

Agregar entrada para esta fase.

## Criterios de Completitud

- [ ] `PublicationGatesOrchestrator` importado y llamado en `main.py` v4complete
- [ ] `gate_report.json` se genera junto al diagnóstico
- [ ] Documento de diagnóstico incluye sección "Validación de Calidad" con tabla de gates
- [ ] 8-10 tests para PublicationGatesOrchestrator (todos pasan)
- [ ] CHANGELOG.md actualizado con entrada de esta fase

## Post-Ejecución

```bash
# 1. Ejecutar tests
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_publication_gates.py -v

# 2. Registrar fase
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-TRAZABILIDAD-GATES \
    --desc "Cableado PublicationGatesOrchestrator (9 gates) en v4complete + trazabilidad en output + tests" \
    --archivos-nuevos "tests/quality_gates/test_publication_gates.py" \
    --archivos-mod "main.py,modules/commercial_documents/v4_diagnostic_generator.py,CHANGELOG.md" \
    --tests "10" \
    --check-manual-docs

# 3. Commit
git add -A && git commit -m "FASE-TRAZABILIDAD-GATES: Wire 9 publication gates into v4complete + traceability + tests"
```

## Archivos Involucrados

| Archivo | Tipo | Cambio |
|---------|------|--------|
| `main.py` (~L2190) | Modificar | Insertar llamada a PublicationGatesOrchestrator |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Modificar | Agregar gate_results param + template section |
| `tests/quality_gates/test_publication_gates.py` | Nuevo | 8-10 tests |
| `CHANGELOG.md` | Modificar | Nueva entrada |
