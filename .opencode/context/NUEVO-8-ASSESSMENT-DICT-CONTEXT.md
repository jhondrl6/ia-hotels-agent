# Contexto: NUEVO-8 — Assessment Dict Frágil y Manual

**Creado:** 2026-05-26
**Origen:** PIPELINE-FIX-PLAN.md L41 + ROADMAP.md L369
**Proyecto:** iah-cli
**Versión actual:** v4.49.0 (AGENTSMD-DRIFT)
**Severidad:** 🟡 Media — no bloquea el pipeline, pero cada nueva fase que toca el assessment dict genera riesgo de regresión

---

## Resumen ejecutivo

El diccionario `assessment` que alimenta los 11 publication gates se construye manualmente en `main.py:2663-2754` (~90 líneas) sin estructura tipada, sin validación de esquema, y en 3 etapas separadas. PIPELINE-FIX (v4.48.0) tuvo que inyectar 4 campos huérfanos quirúrgicamente porque el dict no los incluía. Cada nueva feature que necesita datos en los gates obliga a editar este bloque manual, con riesgo de olvidar campos, romper contratos implícitos, o desalinear nombres de keys.

**La solución propuesta es `AssessmentBuilder`:** una clase centralizada que construya el assessment dict de forma declarativa, con esquema validable, y que los gates consuman sin conocer los detalles de construcción.

**Este hallazgo está explícitamente fuera de scope de PIPELINE-FIX y de AGENTSMD-DRIFT.** ROADMAP.md L369 lo marca como "sesión futura dedicada".

---

## Evidencia del problema

### 1. Construcción en 3 etapas (main.py)

**Etapa 1 — Construcción inicial (L2663-2720):** ~60 líneas de dict literal con ~20 campos anidados.

```python
assessment = {
    "url": args.url,
    "hotel_name": hotel_name,
    "validation_summary": { ... },
    "financial_data": { ... },
    "financial_sources": financial_sources,
    "coherence_score": ...,
    "coherence_checks": [ ... ],
    "coherence_errors": ...,
    "coherence_warnings": ...,
    "critical_issues": ...,
    "critical_issues_detected": ...,  # duplicado de arriba
    "audit_schema": { ... },
    # PIPELINE-FIX: Inject orphaned artifacts
    "pain_ledger": [ ... ],
    "diagnostic_pain_ids": [ ... ],
    "proposal_pain_ids": [ ... ],
    "financial_evidence_tier": ...,
    "evidence_coverage": 0.95,  # hardcodeado
    "metrics": { ... },
    "quality_gate_issues": ...,
    "quality_gate_blockers": ...,
    "quality_gate_warnings": ...,
}
```

**Etapa 2 — Enriquecimiento post-construcción (L2722-2748):** ~25 líneas que agregan campos después del dict literal:

```python
assessment["diagnostico_text"] = f.read()        # L2726
assessment["propuesta_text"] = f.read()           # L2732
assessment["hotel_data"] = { ... }                # L2735
assessment["generated_assets"] = [ ... ]          # L2739
```

**Etapa 3 — Enriquecimiento tardío (L2838):** ~80 líneas después, en otro contexto:

```python
assessment['consistency_report'] = consistency_report.to_dict()  # L2838
```

### 2. Sin tipado — Dict[str, Any]

Los consumers (`run_publication_gates`, `check_publication_readiness`) reciben `Dict[str, Any]`. No hay contrato explícito de qué campos deben existir. Cada gate accede a `assessment["lo_que_sea"]` con fe ciega.

### 3. Campos duplicados y hardcodeados

- `"critical_issues"` y `"critical_issues_detected"` son el mismo dato con dos nombres (L2687-2688)
- `"evidence_coverage": 0.95` está hardcodeado sin justificación (L2713)
- `"quality_gate_issues"`, `"quality_gate_blockers"`, `"quality_gate_warnings"` usan `locals().get()` — patrón frágil (L2717-2719)

### 4. PIPELINE-FIX fue sintomático

La FASE-PF-1 de v4.48.0 tuvo que agregar 4 campos al assessment dict porque no existían. El comentario `# PIPELINE-FIX: Inject orphaned artifacts` en L2697 es literalmente una admisión de que el dict no estaba completo. Si hubiera existido un `AssessmentBuilder` con esquema validado, esos campos se habrían detectado como faltantes en tiempo de desarrollo, no en producción.

---

## Consumidores del assessment dict

| Consumidor | Archivo | Qué espera |
|-----------|---------|------------|
| 11 publication gates | `modules/quality_gates/publication_gates.py:157-169` | Cada gate accede a subsets distintos del dict |
| `run_publication_gates()` | `publication_gates.py:1277` | `Dict[str, Any]` sin validación |
| `check_publication_readiness()` | `publication_gates.py:1304` | `Dict[str, Any]` sin validación |

---

## Implicaciones

1. **Cada nueva feature que requiere datos en los gates** obliga a editar `main.py:2663-2754` manualmente.
2. **No hay validación de esquema:** si un campo falta, el gate falla en runtime con KeyError.
3. **No hay documentación del contrato:** para saber qué espera cada gate, hay que leer el código de los 11 gates uno por uno.
4. **Riesgo de regresión:** modificar el orden o nombre de un campo puede romper gates silenciosamente (pasan de FAIL a PASS o viceversa sin que nadie lo note).
5. **Deuda acumulativa:** cada fase que agrega campos al dict aumenta la fragilidad.

---

## Propuesta: AssessmentBuilder

### Objetivo

Centralizar la construcción del assessment dict en una clase `AssessmentBuilder` con:

- **Esquema tipado** (dataclass o Pydantic) que declare todos los campos requeridos y opcionales
- **Construcción declarativa:** el builder recibe los artefactos disponibles y los ensambla
- **Validación pre-gates:** antes de pasar a `run_publication_gates()`, validar que el esquema está completo
- **Contracto documentado:** cada gate declara qué campos necesita del assessment

### Diseño tentativo

```python
# modules/assessment_builder.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class AssessmentPayload:
    """Contrato tipado entre main.py y publication_gates."""
    # Core
    url: str
    hotel_name: str
    
    # Validation
    validation_summary: Dict[str, Any]
    
    # Financial
    financial_data: Dict[str, Any]
    financial_sources: Dict[str, Any]
    financial_evidence_tier: str = "C"
    
    # Coherence
    coherence_score: float = 0.0
    coherence_checks: List[Dict] = field(default_factory=list)
    coherence_errors: List[str] = field(default_factory=list)
    coherence_warnings: List[str] = field(default_factory=list)
    
    # Pain ledger (FASE-0)
    pain_ledger: List[Dict] = field(default_factory=list)
    diagnostic_pain_ids: List[str] = field(default_factory=list)
    proposal_pain_ids: List[str] = field(default_factory=list)
    
    # Audit
    audit_schema: Dict[str, Any] = field(default_factory=dict)
    critical_issues: List[str] = field(default_factory=list)
    
    # Documents (post-generation)
    diagnostico_text: str = ""
    propuesta_text: str = ""
    
    # Assets
    generated_assets: List[Dict] = field(default_factory=list)
    evidence_coverage: float = 0.95
    
    # Quality gates
    quality_gate_issues: List[str] = field(default_factory=list)
    quality_gate_blockers: List[str] = field(default_factory=list)
    quality_gate_warnings: List[str] = field(default_factory=list)
    
    # Regional
    hotel_data: Dict[str, str] = field(default_factory=dict)
    
    # Consistency
    consistency_report: Optional[Dict[str, Any]] = None
    
    # Metrics
    metrics: Dict[str, Any] = field(default_factory=dict)


class AssessmentBuilder:
    """Centralized, validated assessment dict construction."""
    
    def __init__(self):
        self._payload = AssessmentPayload()
    
    def with_core(self, url: str, hotel_name: str) -> 'AssessmentBuilder':
        ...
    
    def with_validation(self, validation_summary, whatsapp_validation) -> 'AssessmentBuilder':
        ...
    
    def with_financial(self, rooms, adr_cop, occupancy_rate, ...) -> 'AssessmentBuilder':
        ...
    
    def with_coherence(self, pre_coherence_report, asset_result) -> 'AssessmentBuilder':
        ...
    
    def with_pain_ledger(self, entries, diagnostic_summary, asset_plan) -> 'AssessmentBuilder':
        ...
    
    def with_audit(self, audit_result) -> 'AssessmentBuilder':
        ...
    
    def with_documents(self, diagnostic_path, proposal_path) -> 'AssessmentBuilder':
        ...
    
    def with_assets(self, asset_result) -> 'AssessmentBuilder':
        ...
    
    def with_consistency(self, consistency_report) -> 'AssessmentBuilder':
        ...
    
    def build(self) -> Dict[str, Any]:
        """Validate and return the assessment dict."""
        self._validate()
        return self._to_dict()
    
    def _validate(self):
        """Ensure all required fields are present and non-empty."""
        ...
    
    def _to_dict(self) -> Dict[str, Any]:
        """Convert to the dict format expected by publication_gates."""
        ...
```

### Uso en main.py (target)

```python
# Antes (actual, ~90 líneas):
assessment = {
    "url": args.url,
    "hotel_name": hotel_name,
    "validation_summary": { ... },
    # ... 80+ líneas más
}
assessment["diagnostico_text"] = f.read()
assessment["propuesta_text"] = f.read()
# ... etc

# Después (target, ~15 líneas):
builder = AssessmentBuilder()
builder.with_core(args.url, hotel_name)
builder.with_validation(validation_summary, whatsapp_validation)
builder.with_financial(rooms, adr_cop, occupancy_rate, direct_channel_pct, financial_sources, financial_breakdown)
builder.with_coherence(pre_coherence_report, asset_result)
builder.with_pain_ledger(pain_ledger_entries, diagnostic_summary, asset_plan)
builder.with_audit(audit_result)
builder.with_documents(diagnostic_path, proposal_path)
builder.with_assets(asset_result)
# ... post-generation
builder.with_consistency(consistency_report)

assessment = builder.build()
```

---

## Esfuerzo estimado

| Actividad | Horas |
|-----------|-------|
| Auditar qué campos consume cada uno de los 11 gates | 1.5h |
| Diseñar `AssessmentPayload` dataclass con todos los campos | 1h |
| Implementar `AssessmentBuilder` con métodos fluid | 3h |
| Migrar `main.py:2663-2754` al builder | 1.5h |
| Tests (validación de esquema + integración) | 2h |
| Verificación E2E con v4complete | 1h |
| **Total** | **~10h** |

---

## Relación con otros hallazgos

| Hallazgo | Relación |
|----------|----------|
| PIPELINE-FIX (v4.48.0) | Parchó 4 campos huérfanos. NUEVO-8 es la causa raíz estructural. |
| AGENTSMD-DRIFT (v4.49.0) | Sin relación directa. AGENTSMD-DRIFT corrige documentación, no código. |
| ROADMAP FASE A-01 | AGENTS.md auditado — no toca assessment dict. |
| ROADMAP FASE B/C (futuro) | Posible ubicación para NUEVO-8. |

---

## Decisión pendiente

¿En qué fase del ROADMAP se asigna NUEVO-8? Opciones:

1. **FASE A-04** (extender FASE A: "Baseline de robustez agente") — si se considera deuda estructural que debe resolverse antes de nuevas features
2. **FASE B** (nuevas capacidades) — si se espera a que una nueva feature fuerce el refactor
3. **FASE independiente (NUEVO-8)** — sesión dedicada como sugiere ROADMAP L369

---

## Referencias cruzadas

| Archivo | Sección/Línea | Dato clave |
|---------|--------------|------------|
| `main.py` | L2663-2754 | Construcción manual del assessment dict (~90 líneas) |
| `main.py` | L2697-2712 | PIPELINE-FIX: 4 campos huérfanos inyectados |
| `main.py` | L2687-2688 | `critical_issues` duplicado con `critical_issues_detected` |
| `main.py` | L2713 | `evidence_coverage: 0.95` hardcodeado |
| `main.py` | L2838 | `consistency_report` agregado 80 líneas después |
| `modules/quality_gates/publication_gates.py` | L157-169 | 11 gates, cada uno accede subsets del dict |
| `modules/quality_gates/publication_gates.py` | L1277 | `run_publication_gates(assessment: Dict[str, Any])` |
| `.opencode/plans/PIPELINE-FIX-PLAN.md` | L41 | NUEVO-8: "Assessment dict frágil y manual — FUERA DE SCOPE" |
| `ROADMAP.md` | L369 | "AssessmentBuilder centralizado — sesión futura dedicada" |

---

## Prompt para diseñar el plan (sesión futura)

```
Carga .opencode/context/NUEVO-8-ASSESSMENT-DICT-CONTEXT.md.
También carga ROADMAP.md para contexto de fases.
Diseña un plan de implementación por fases siguiendo phased_project_executor.md.
Alcance: AssessmentBuilder + migración de main.py + tests + v4complete E2E.
NO implementar aún — solo diseñar fases con R3 scope.
```
