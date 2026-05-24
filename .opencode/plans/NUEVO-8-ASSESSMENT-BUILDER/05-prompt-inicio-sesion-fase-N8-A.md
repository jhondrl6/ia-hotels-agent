# 05-prompt-inicio-sesion-fase-N8-A

**Fase:** N8-A — Auditoría final + Diseño AssessmentPayload + Tests
**Plan:** NUEVO-8-ASSESSMENT-BUILDER
**Sesión:** Nueva (fresh)
**Iteraciones máx:** 60
**Depende de:** —
**Bloquea a:** N8-B
**Tipo:** DIRECTA (código + tests, sin comandos largos)

---

## Objetivo

Verificar los claims del contexto NUEVO-8 contra código vivo, diseñar el dataclass `AssessmentPayload` con el esquema tipado final, y escribir tests unitarios.

## Contexto de Fases Anteriores

Ninguna — esta es la primera fase. El contexto completo está en `.opencode/context/NUEVO-8-ASSESSMENT-DICT-CONTEXT.md`. El problema: el assessment dict en `main.py:2663-2754` se construye manualmente sin tipado, y los gates implementan ~129 líneas de extractores multi-path como defensa.

**Discrepancias ya detectadas (no re-verificar):**
- `audit_schema` SÍ es consumido (L868 `_proposal_asset_alignment_gate`) → NO es zombie
- `consistency_report` SÍ es consumido (L1236-1238 `_extract_coherence_score`) → NO es dead key
- ROADMAP.md no tiene referencia NUEVO-8
- `coherence_checks/errors/warnings` tienen 0 consumidores → SÍ son dead fields

## Tareas

### T1: Verificar claims pendientes del contexto contra código vivo
- Archivos: `main.py`, `modules/quality_gates/publication_gates.py`
- Claims a verificar (solo los NO marcados como verificados en README.md):
  - ¿`coherence_report` se inyecta en el assessment y es consumido? (verificado: SÍ, L2838 + L1236)
  - ¿`SitePresenceChecker` se ejecuta 2 veces? (verificar main.py L2600-2607 y publication_gates.py L839-851)
  - ¿`proposal_services` se busca en el assessment dict? ¿Dónde está el default ALL_PROMISED_SERVICES?
  - ¿El cálculo de `critical_recall` en L1267-1270 usa `critical_issues` y `critical_issues_detected` que son el mismo array?
- Output: tabla de verificación en el log de la fase

### T2: Diseñar `AssessmentPayload` dataclass
- Archivo: `modules/assessment_builder.py` (CREAR)
- El dataclass DEBE incluir todos los campos que los gates consumen (verificado en T1)
- Campos REQUERIDOS (sin default): `url`, `hotel_name`
- Campos OPCIONALES (con default): validation_summary, financial_data, financial_sources, financial_evidence_tier, coherence_score, pain_ledger, diagnostic_pain_ids, proposal_pain_ids, audit_schema, critical_issues, proposal_services, diagnostico_text, propuesta_text, generated_assets, evidence_coverage, site_presence_report, hotel_data, hotel_url
- Campos ELIMINADOS (NO incluir): quality_gate_issues, quality_gate_blockers, quality_gate_warnings, coherence_checks, coherence_errors, coherence_warnings, critical_issues_detected, metrics (0 consumidores post-simplificación), coherence_report (0 consumidores post-simplificación)
- `hotel_url` es alias de `url` (default="" — el builder lo setea a `url`)
- `evidence_coverage` default=0.95 con comentario `# TODO: calcular en vez de hardcodear`
- `financial_evidence_tier` default="C"
- Usar `from dataclasses import dataclass, field` y `from typing import Any, Dict, List, Optional`

```python
# Estructura esperada (completar en la fase):
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class AssessmentPayload:
    """Contrato tipado entre main.py y publication_gates.
    
    Todos los campos que los 11 gates consumen, verificados contra código vivo.
    """
    # Core
    url: str
    hotel_name: str
    hotel_url: str = ""  # alias de url
    
    # Validation
    validation_summary: Dict[str, Any] = field(default_factory=dict)
    
    # Financial
    financial_data: Dict[str, Any] = field(default_factory=dict)
    financial_sources: Dict[str, Any] = field(default_factory=dict)
    financial_evidence_tier: str = "C"
    
    # Coherence
    coherence_score: float = 0.0
    
    # Pain Ledger / FASE-0
    pain_ledger: List[Dict] = field(default_factory=list)
    diagnostic_pain_ids: List[str] = field(default_factory=list)
    proposal_pain_ids: List[str] = field(default_factory=list)
    
    # Audit
    audit_schema: Dict[str, Any] = field(default_factory=dict)
    critical_issues: List[str] = field(default_factory=list)
    
    # Proposal
    proposal_services: List[str] = field(default_factory=list)
    
    # Documents
    diagnostico_text: str = ""
    propuesta_text: str = ""
    
    # Assets
    generated_assets: List[Dict] = field(default_factory=list)
    evidence_coverage: float = 0.95  # TODO: calcular
    
    # Site presence (evita duplicación)
    site_presence_report: Optional[Dict[str, Any]] = None
    
    # Hotel data
    hotel_data: Dict[str, str] = field(default_factory=dict)
```

### T3: Escribir tests unitarios para AssessmentPayload
- Archivo: `tests/test_assessment_builder.py` (CREAR)
- Mínimo 12 tests:
  1. `test_payload_creation_defaults` — crear con solo url+hotel_name, verificar defaults
  2. `test_payload_hotel_url_alias` — hotel_url default es "" (no url), verificar
  3. `test_payload_validation_summary` — dict anidado correcto
  4. `test_payload_financial_data` — financial_data + financial_evidence_tier
  5. `test_payload_coherence` — coherence_score float
  6. `test_payload_pain_ledger` — pain_ledger lista de dicts
  7. `test_payload_audit` — audit_schema + critical_issues
  8. `test_payload_documents` — diagnostico_text + propuesta_text strings
  9. `test_payload_assets` — generated_assets + evidence_coverage
  10. `test_payload_site_presence` — site_presence_report opcional (None default)
  11. `test_payload_no_zombie_fields` — verificar que NO existen quality_gate_*, coherence_checks, coherence_errors, coherence_warnings, critical_issues_detected, metrics, coherence_report
  12. `test_payload_serialization` — dataclasses.asdict() produce dict esperado
- Usar pytest. Python path: `./venv/Scripts/python.exe -m pytest`

### T4: Ejecutar tests + log_phase
- Ejecutar: `./venv/Scripts/python.exe -m pytest tests/test_assessment_builder.py -v`
- Esperado: 12+ passed, 0 failed
- Ejecutar log_phase_completion.py

## Criterios de Completitud
- [ ] T1: Tabla de verificación generada con todos los claims
- [ ] T2: `modules/assessment_builder.py` creado con AssessmentPayload dataclass
- [ ] T3: `tests/test_assessment_builder.py` con 12+ tests
- [ ] T4: Todos los tests pasan + log_phase ejecutado

## Restricciones
- Máximo 60 iteraciones
- **NO modificar main.py** (se modifica en N8-B)
- **NO modificar publication_gates.py** (se modifica en N8-C)
- **NO ejecutar v4complete**
- Python path: `./venv/Scripts/python.exe`
- Working directory: `/mnt/c/Users/Jhond/Github/iah-cli`

## Post-Ejecución (OBLIGATORIO)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli && \
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase N8-A \
    --desc "AssessmentPayload dataclass + tests unitarios — NUEVO-8 AssessmentBuilder" \
    --archivos-nuevos "modules/assessment_builder.py,tests/test_assessment_builder.py" \
    --archivos-mod "" \
    --tests "12" \
    --check-manual-docs
```

## Próxima sesión
N8-B: Implementar AssessmentBuilder + Migrar main.py + Tests
