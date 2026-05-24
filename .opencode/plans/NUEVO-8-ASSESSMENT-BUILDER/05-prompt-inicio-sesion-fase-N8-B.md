# 05-prompt-inicio-sesion-fase-N8-B

**Fase:** N8-B — AssessmentBuilder + Migración main.py + Tests
**Plan:** NUEVO-8-ASSESSMENT-BUILDER
**Sesión:** Nueva (fresh)
**Iteraciones máx:** 60
**Depende de:** N8-A ✅ (AssessmentPayload dataclass creado en `modules/assessment_builder.py`)
**Bloquea a:** N8-C
**Tipo:** DIRECTA (código + tests, sin comandos largos)

---

## Objetivo

Implementar la clase `AssessmentBuilder` con API fluida, migrar el bloque de construcción del assessment dict en `main.py:2663-2754` (~87 líneas en 3 etapas) al builder, y escribir tests unitarios.

## Contexto de Fases Anteriores

**N8-A completada:** `modules/assessment_builder.py` ya contiene el dataclass `AssessmentPayload` con todos los campos tipados. `tests/test_assessment_builder.py` tiene 12+ tests del dataclass que pasan.

## Tareas

### T1: Implementar `AssessmentBuilder` class
- Archivo: `modules/assessment_builder.py` (EXTENDER — ya tiene AssessmentPayload)
- Agregar la clase `AssessmentBuilder` con:
  - `__init__`: crea `AssessmentPayload()` vacío
  - Métodos fluid (cada uno retorna `self`):
    - `with_core(url, hotel_name)` — setea url, hotel_name, hotel_url=url
    - `with_validation(validation_summary, whatsapp_validation)` — validation_summary dict con whatsapp_status, overall_confidence, conflicts
    - `with_financial(rooms, adr_cop, occupancy_rate, direct_channel_pct, financial_sources, financial_breakdown)` — financial_data + financial_sources + financial_evidence_tier
    - `with_coherence(pre_coherence_report, asset_result)` — coherence_score desde asset_result.coherence_report.overall_score
    - `with_pain_ledger(entries, diagnostic_summary, asset_plan)` — pain_ledger, diagnostic_pain_ids, proposal_pain_ids
    - `with_audit(audit_result)` — audit_schema + critical_issues
    - `with_documents(diagnostic_path, proposal_path)` — lee archivos y setea diagnostico_text, propuesta_text
    - `with_assets(asset_result)` — generated_assets + evidence_coverage
    - `with_site_presence(site_presence_report)` — inyecta el report para evitar recálculo
    - `with_hotel_data(region)` — hotel_data con region
  - `build()` → `Dict[str, Any]`: valida y convierte a dict
  - `_validate()`: verifica que url y hotel_name no estén vacíos
  - `_to_dict()`: convierte el dataclass a dict (usar `dataclasses.asdict`)

**Detalles de implementación:**
- `with_coherence`: `self._payload.coherence_score = asset_result.coherence_report.overall_score` si asset_result existe, sino 0.0. **NO** setear `coherence_report` en el payload (0 consumidores post-simplificación de extractores).
- `with_pain_ledger`: convertir entries con `e.to_dict() if hasattr(e, 'to_dict') else e`
- `with_audit`: extraer `audit_result.schema.hotel_schema_detected`, etc. (6 sub-campos como en L2689-2696)
- `with_documents`: leer archivos con try/except (como L2723-2734)
- `with_assets`: generated_assets como en L2739-2748, evidence_coverage=0.95. **NO** setear `metrics` (0 consumidores — dict con campos que nunca existieron).
- `_validate()`: lanzar `ValueError` si url vacío o hotel_name vacío
- `_to_dict()`: usar `dataclasses.asdict(self._payload)` y asegurar que es `Dict[str, Any]`

### T2: Migrar `main.py:2663-2754` al builder
- Archivo: `main.py` (MODIFICAR — solo el bloque L2663-2754)
- Reemplazar las ~87 líneas de construcción del assessment dict por:
```python
# Build assessment via AssessmentBuilder (NUEVO-8)
from modules.assessment_builder import AssessmentBuilder

builder = AssessmentBuilder()
builder.with_core(args.url, hotel_name)
builder.with_validation(validation_summary, whatsapp_validation)
builder.with_financial(rooms, adr_cop, occupancy_rate, direct_channel_pct, financial_sources, financial_breakdown)
builder.with_coherence(pre_coherence_report, asset_result)
builder.with_pain_ledger(pain_ledger_entries, diagnostic_summary, asset_plan)
builder.with_audit(audit_result)
builder.with_documents(diagnostic_path, proposal_path)
builder.with_assets(asset_result)
builder.with_site_presence(site_presence_report)
builder.with_hotel_data(region)

assessment = builder.build()
```
- **NO eliminar** las líneas que calculan `site_presence_report` (L2597-2607) — esas se mantienen
- **NO eliminar** `assessment['consistency_report'] = consistency_report.to_dict()` (L2838) — se mantiene por ahora
- Verificar que `main.py` compila: `./venv/Scripts/python.exe -c "import main"` (puede fallar por dependencias, verificar al menos que no hay SyntaxError)

### T3: Escribir tests unitarios para AssessmentBuilder
- Archivo: `tests/test_assessment_builder.py` (EXTENDER)
- Mínimo 17 tests adicionales (29 total con los de N8-A):
  1. `test_builder_with_core` — url + hotel_name + hotel_url alias
  2. `test_builder_with_validation` — validation_summary con todos los campos
  3. `test_builder_with_financial` — financial_data + sources + evidence_tier
  4. `test_builder_with_coherence` — coherence_score desde asset_result
  5. `test_builder_with_coherence_no_asset_result` — defaults a 0.0
  6. `test_builder_with_pain_ledger` — entries con to_dict()
  7. `test_builder_with_pain_ledger_no_diagnostic` — defaults a listas vacías
  8. `test_builder_with_audit` — audit_schema con 6 sub-campos
  9. `test_builder_with_audit_none` — audit_result=None → dict vacío
  10. `test_builder_with_documents` — lee archivos reales (crear temp files)
  11. `test_builder_with_documents_missing` — archivos no existen → strings vacíos
  12. `test_builder_with_assets` — generated_assets con campos correctos
  13. `test_builder_with_site_presence` — site_presence_report inyectado
  14. `test_builder_with_hotel_data` — hotel_data con region
  15. `test_builder_build_valid` — build() retorna dict con todas las keys
  16. `test_builder_build_missing_url` — build() sin url lanza ValueError
  17. `test_builder_build_missing_hotel_name` — build() sin hotel_name lanza ValueError
  18. `test_builder_full_pipeline` — integración: todos los with_* → build() → dict completo

### T4: Ejecutar tests + log_phase
- Ejecutar: `./venv/Scripts/python.exe -m pytest tests/test_assessment_builder.py -v`
- Esperado: 29+ passed (12 de N8-A + 17 nuevos), 0 failed
- Si hay fallos, corregir antes de log_phase

## Criterios de Completitud
- [ ] T1: `AssessmentBuilder` class implementada con todos los métodos fluid + build()
- [ ] T2: `main.py` migrado (L2663-2754 reemplazado por ~15 líneas de builder)
- [ ] T3: 17+ tests nuevos para AssessmentBuilder
- [ ] T4: 29+ tests totales pasan + main.py sin SyntaxError + log_phase

## Restricciones
- Máximo 60 iteraciones
- **NO modificar publication_gates.py** (se modifica en N8-C)
- **NO eliminar `assessment['consistency_report']` en L2838** (se maneja en N8-C)
- **NO ejecutar v4complete**
- Python path: `./venv/Scripts/python.exe`
- Working directory: `/mnt/c/Users/Jhond/Github/iah-cli`

## Post-Ejecución (OBLIGATORIO)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli && \
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase N8-B \
    --desc "AssessmentBuilder class + migracion main.py + tests — NUEVO-8" \
    --archivos-nuevos "" \
    --archivos-mod "main.py,modules/assessment_builder.py,tests/test_assessment_builder.py" \
    --tests "17" \
    --check-manual-docs
```

## Próxima sesión
N8-C: Simplificar extractores + Eliminar campos muertos + Tests
