# FASE-PF-1: Fix Assessment Dict — Cargar e Inyectar Artefactos Huérfanos

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (código + tests, sin comandos largos)
> **Presupuesto**: ~40 iteraciones (4 tareas + tests + validación)

## Contexto previo

**Plan:** PIPELINE-FIX (`.opencode/plans/PIPELINE-FIX-PLAN.md`)
**Contexto de auditoría:** `.opencode/context/auditoria-hotelcastillareal-fase0-pipeline-fixes.md`

La auditoría forense (2026-05-22) identificó que `main.py:2652-2694` construye el `assessment` dict manualmente SIN incluir 4 campos que los gates de publicación necesitan. Estos datos YA existen en disco o memoria, pero quedan huérfanos:

- `pain_ledger` → existe en `output_dir/v4_audit/pain_ledger.json` (11 entries)
- `diagnostic_pain_ids` → existe en `diagnostic_summary.pain_ids`
- `proposal_pain_ids` → existe en `asset_plan[].pain_ids`
- `financial_evidence_tier` → existe en `financial_breakdown.evidence_tier`

**Consecuencia:** `_coverage_gate()` retorna BLOCKED, `_tier_c_onboarding_gate()` SIEMPRE hace default a "C" → BLOCKED, `ProposalAssetMatrix.save()` nunca se invoca.

## Objetivo de esta fase

Resolver la causa raíz del pipeline: inyectar los 4 artefactos huérfanos al assessment dict y pasar pain_ledger a proposal_gen.generate().

### Hallazgos que resuelve
- **CRÍTICO-1**: PainLedger no llega al CoverageGate
- **NUEVO-5**: financial_evidence_tier nunca llega al assessment
- **NUEVO-6**: diagnostic_pain_ids y proposal_pain_ids ausentes
- **ALTO-4**: proposal_asset_matrix.json no se serializa

### Tareas

#### T1: Cargar pain_ledger.json antes del assessment builder

- **Dónde:** `main.py`, ANTES de línea 2652 (antes de `# Build assessment dict`)
- **Qué:** Agregar bloque de carga:
```python
# PIPELINE-FIX: Load pain_ledger for assessment injection
from modules.asset_generation.pain_ledger import PainLedger
pain_ledger_path = output_dir / "v4_audit" / "pain_ledger.json"
if pain_ledger_path.exists():
    pain_ledger_entries = PainLedger().load(pain_ledger_path)
else:
    pain_ledger_entries = []
```
- **Verificar:** Import correcto, path handling robusto (Path vs str), fallback a lista vacía

#### T2: Inyectar 4 campos al assessment dict

- **Dónde:** `main.py:2652-2694` (dentro del dict `assessment = {...}`)
- **Qué:** Agregar al dict:
```python
# PIPELINE-FIX: Inject orphaned artifacts into assessment
"pain_ledger": [
    e.__dict__ if hasattr(e, '__dict__') else e 
    for e in pain_ledger_entries
],
"diagnostic_pain_ids": list(
    getattr(diagnostic_summary, 'pain_ids', []) or []
) if diagnostic_summary else [],
"proposal_pain_ids": list(set(
    pid for asset in (asset_plan or []) 
    for pid in (getattr(asset, 'pain_ids', None) or [])
)),
"financial_evidence_tier": (
    getattr(financial_breakdown, 'evidence_tier', 'C') 
    if financial_breakdown else 'C'
),
```
- **Verificar:** Campos existen en assessment dict post-construcción, tipos correctos

#### T3: Pasar pain_ledger a proposal_gen.generate()

- **Dónde:** `main.py:2601-2614` (llamada a `proposal_gen.generate()`)
- **Qué:** Agregar parámetro:
```python
proposal_path = proposal_gen.generate(
    # ... parámetros existentes ...
    pain_ledger=pain_ledger_entries,  # PIPELINE-FIX: enable ProposalAssetMatrix.save()
)
```
- **Nota:** `pain_ledger_entries` se carga en T1 (antes de esta llamada). Verificar que la variable está en scope.
- **IMPORTANTE:** Si `pain_ledger_entries` se carga DESPUÉS de la llamada a generate() (porque la carga está antes de línea 2652 pero generate() está en línea 2601), entonces MOVER la carga de pain_ledger ANTES de línea 2601.
- **Verificar:** `proposal_asset_matrix.json` se genera en `output_dir/v4_audit/`

#### T4: Tests unitarios

- **Qué:** Crear o extender tests que verifiquen:
  1. `assessment["pain_ledger"]` contiene entries cuando pain_ledger.json existe
  2. `assessment["pain_ledger"]` es [] cuando no existe
  3. `assessment["diagnostic_pain_ids"]` contiene IDs del diagnostic_summary
  4. `assessment["proposal_pain_ids"]` contiene IDs del asset_plan
  5. `assessment["financial_evidence_tier"]` refleja el valor real (no default "C")
  6. `proposal_gen.generate()` recibe pain_ledger correctamente
- **Dónde:** `tests/` — buscar test existente del assessment builder o crear `tests/test_pipeline_fix_assessment.py`
- **Ejecutar:** `./venv/Scripts/python.exe -m pytest tests/test_pipeline_fix_assessment.py -v`

### Restricciones

- NO modificar `publication_gates.py` — los gates están bien, solo falta data
- NO modificar `pain_ledger.py` — ya genera correctamente
- NO modificar `v4_proposal_generator.py` — ya tiene la lógica de save()
- NO ejecutar v4complete en esta fase (eso es FASE-PF-3)
- Verificar números de línea ANTES de editar (pueden haber cambiado desde la auditoría)
- Si `financial_breakdown` no tiene atributo `evidence_tier`, usar `'C'` como fallback seguro

### Criterios de completitud

- [x] T1: `pain_ledger_entries` cargado correctamente desde disco
- [x] T2: Los 4 campos nuevos están en el assessment dict
- [x] T3: `proposal_gen.generate()` recibe `pain_ledger=pain_ledger_entries`
- [x] T4: Tests pasan (13 tests cubriendo los campos inyectados)
- [x] `python scripts/run_all_validations.py --quick` → sin nuevos errores (3/5 pass, 2 fallas preexistentes)
- [x] No se introducen regresiones en tests existentes (63/64 pass, 1 falla preexistente)

**Estado: ✅ COMPLETADA — 2026-05-23 17:00**
**Sesión:** FASE-PF-1 ejecutada en ~35 iteraciones
**Archivo nuevo:** `tests/test_pipeline_fix_assessment.py` (13 tests)
**Archivo modificado:** `main.py` (3 bloques: init scope + load + assessment injection)

### Próxima sesión

**FASE-PF-2**: Fix delivery_ready_percentage en `v4_asset_orchestrator.py:125-132` — cambiar fórmula de `preflight_status` a `confidence_score >= 0.65`.
