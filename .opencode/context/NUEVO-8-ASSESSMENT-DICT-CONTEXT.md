# Contexto: NUEVO-8 — Assessment Dict Frágil y Manual

**Creado:** 2026-05-26
**Validado exhaustivamente:** 2026-05-27 (verificación live-code de todos los claims)
**Re-auditado:** 2026-05-30 (forensic audit contra código vivo — 18/23 claims confirmados, 4 nuevos hallazgos)
**Origen:** ROADMAP.md L369
**Proyecto:** iah-cli
**Versión actual:** v4.49.0 (AGENTSMD-DRIFT)
**Severidad:** 🟡 Media — no bloquea el pipeline, pero cada nueva fase que toca el assessment dict genera riesgo de regresión

---

## Resumen ejecutivo

El diccionario `assessment` que alimenta los 11 publication gates se construye manualmente en `main.py:2663-2754` (~87 líneas) sin estructura tipada, sin validación de esquema, y en 3 etapas separadas. PIPELINE-FIX (v4.48.0) tuvo que inyectar 4 campos huérfanos quirúrgicamente porque el dict no los incluía. Cada nueva feature que necesita datos en los gates obliga a editar este bloque manual, con riesgo de olvidar campos, romper contratos implícitos, o desalinear nombres de keys.

**Validación live-code (2026-05-27) amplió el diagnóstico:** la verdadera deuda no son solo las ~87 líneas en main.py, sino **~135 líneas de extractores multi-path** en `publication_gates.py` que existen precisamente porque no hay schema. Cada gate implementa su propia resolución de datos con 4-6 fallbacks por campo. Además, se detectaron **5 campos zombie** (quality_gate_×3 vía `locals().get()`, consistency_report vía dict, audit_schema — 0 consumidores vía assessment dict), **1 duplicación de cómputo** (SitePresenceChecker ejecutado 2 veces), y **~15 líneas de dead code** en paths de extractores nunca activados.

**Re-auditoría forense (2026-05-30):** Verificación exhaustiva contra código vivo (main.py L2663-2720, publication_gates.py L157-169, L1138-1272). 18/23 claims confirmados, 3 parciales, 4 nuevos hallazgos. Las cifras de extractores se corrigieron a la baja (135 líneas reales, no 300).

**La solución propuesta es `AssessmentBuilder`:** una clase centralizada que construya el assessment dict de forma declarativa, con esquema validable, y que permita simplificar los extractores multi-path a acceso directo. El dataclass propuesto en la versión original de este contexto fue corregido: se agregaron campos omitidos que los gates sí consumen y se marcaron los campos muertos para eliminación.

**Este hallazgo está explícitamente fuera de scope de PIPELINE-FIX y de AGENTSMD-DRIFT.** ROADMAP.md L369 lo marca como "sesión futura dedicada".

---

## Evidencia del problema

### 1. Construcción en 3 etapas (main.py)

**Etapa 1 — Construcción inicial (L2663-2720):** ~57 líneas de dict literal con ~20 campos anidados.

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

**Etapa 2 — Enriquecimiento post-construcción (L2722-2748):** ~26 líneas que agregan campos después del dict literal:

```python
assessment["diagnostico_text"] = f.read()        # L2726
assessment["propuesta_text"] = f.read()           # L2732
assessment["hotel_data"] = { ... }                # L2735
assessment["generated_assets"] = [ ... ]          # L2739
```

**Etapa 3 — Enriquecimiento tardío (L2838):** ~83 líneas después, en otro contexto:

```python
assessment['consistency_report'] = consistency_report.to_dict()  # L2838
```

### 2. Sin tipado — Dict[str, Any]

Los consumers (`run_publication_gates`, `check_publication_readiness`) reciben `Dict[str, Any]`. No hay contrato explícito de qué campos deben existir.

**CORRECCIÓN (2026-05-27):** Contrario a lo que indicaba la versión original de este contexto ("cada gate accede a assessment['lo_que_sea'] con fe ciega"), los gates NO acceden directamente. Implementan una **capa de extractores multi-path** que intentan 4-6 ubicaciones diferentes por cada campo. Esta capa existe precisamente porque no hay schema — es un síntoma, no negligencia:

| Extractor | Paths intentados | Líneas |
|-----------|-----------------|--------|
| `_extract_coherence_score()` | 4 (coherence_score, metrics.coherence_score, coherence_report.overall_score, quality_metrics.coherence_score) | L1211-1242 |
| `_extract_evidence_coverage()` | 6 (evidence_coverage, metrics.evidence_coverage, quality_metrics.evidence_coverage, claims, diagnostic.claims, cálculo) | L1151-1183 |
| `_extract_conflicts()` | 4 (conflicts, validation.conflicts, cross_validation.conflicts, validation_summary.conflicts) | L1138-1149 |
| `_extract_critical_recall()` | 5 (critical_recall, metrics.critical_recall, quality_metrics.critical_recall, audit_results.critical_recall, calculado de critical_issues) | L1246-1272 |
| `_extract_financial_data()` | 4 (financial_data, hotel_data, validation_summary.fields, onboarding_data) | L1185-1209 |

**Total: ~135 líneas de código defensivo** (medición real: 5 extractores × ~27 líneas c/u) cuya única razón de existir es la ausencia de schema tipado. De estas, ~15 líneas son dead code (paths 3-6 de fallback nunca activados porque los paths 1-2 siempre resuelven). Con AssessmentBuilder + schema validado, los extractores se pueden reducir a acceso directo con type check, ahorrando ~100 líneas.

### 3. Campos duplicados y hardcodeados

- `"critical_issues"` y `"critical_issues_detected"` son el mismo dato con dos nombres (L2687-2688). Ambos asignados a `audit_result.critical_issues`. El extractor `_extract_critical_recall` (L1267-1270) calcula `len(detected)/len(critical_issues)` — como son el mismo array, siempre da 1.0. **Cálculo tautológico.**
- `"evidence_coverage": 0.95` está hardcodeado con comentario "# Default assumption" (L2713). Sin justificación ni trazabilidad.
- `"quality_gate_issues"`, `"quality_gate_blockers"`, `"quality_gate_warnings"` usan `locals().get()` — patrón frágil (L2717-2719). Si las variables se renombran en el scope anterior, el fallo es silencioso (`.get()` retorna `[]`). **Validación 2026-05-27: 0 consumidores en todo el codebase. Son campos zombie.**

### 4. PIPELINE-FIX fue sintomático

La FASE-PF-1 de v4.48.0 tuvo que agregar 4 campos al assessment dict porque no existían. El comentario `# PIPELINE-FIX: Inject orphaned artifacts` en L2697 es literalmente una admisión de que el dict no estaba completo. Si hubiera existido un `AssessmentBuilder` con esquema validado, esos campos se habrían detectado como faltantes en tiempo de desarrollo, no en producción.

**Los 4 campos sí son consumidos:** `pain_ledger`, `diagnostic_pain_ids`, y `proposal_pain_ids` son leídos por el gate `coverage` (L1034-1060). `financial_evidence_tier` es leído por el gate `tier_c_onboarding_required`. La inyección fue correcta y necesaria: sin ella, 2 gates habrían fallado.

### 5. Campos muertos y zombie (NUEVO — no en diagnóstico original)

**5a. `consistency_report` — CLAVE MUERTA EN EL DICT.** Construido e inyectado en L2838: `assessment['consistency_report'] = consistency_report.to_dict()`. Búsqueda exhaustiva en todo el codebase: **0 lectores de `assessment['consistency_report']`**. Ningún gate, módulo ni script lee esta clave del dict. NOTA: la variable `consistency_report` SÍ se consume directamente en el summary JSON (L3043-3047), pero los datos fluyen por canal paralelo — nunca pasan por el assessment dict. La inyección en L2838 es código muerto genuino.

**5b. `quality_gate_issues/blockers/warnings` — CAMPOS ZOMBIE.** Construidos en L2717-2719 con `locals().get()`. **0 consumidores en todo el codebase.** Agregados "por si acaso" y nunca utilizados.

**5c. `audit_schema` — CAMPO ZOMBIE EN EL DICT.** Inyectado en L2689-2696 con 6 sub-campos (hotel_schema_detected, hotel_schema_valid, hotel_confidence, faq_schema_detected, faq_schema_valid, faq_confidence). **0 consumidores vía assessment dict.** El objeto `audit_result` original sí se usa como argumento de función en L2622, pero los 6 sub-campos en el dict nunca son leídos por ningún gate.

**5d. `assessment["metrics"]` solo tiene `coherence_score`.** L2715-2717 construye `metrics` con un solo campo. Pero los extractores buscan `metrics.evidence_coverage` y `metrics.critical_recall` — que no existen. Los fallbacks salvan, pero el contrato implícito de `metrics` está roto: los consumidores asumen un diccionario rico cuando solo tiene una clave.

**5e. `proposal_services` — CLAVE FANTASMA.** El gate `proposal_asset_alignment` en L832 hace `assessment.get("proposal_services", ALL_PROMISED_SERVICES)`. La clave `proposal_services` NUNCA se inyecta en el assessment dict. El gate siempre usa el default. No es un bug funcional (el default es correcto), pero es ruido: el AssessmentBuilder debería incluir este campo explícitamente.

**5f. `hotel_url` — CLAVE FANTASMA.** El gate en L836 busca `assessment.get("hotel_url")`. Esta clave NO existe en el assessment dict. El fallback `assessment.get("url")` funciona, pero `hotel_url` como clave independiente es otro campo fantasma.

### 6. site_presence_report: duplicación de cómputo (NUEVO)

`main.py:2597-2622` ejecuta `SitePresenceChecker.check_site()` y pasa el resultado a `verify_proposal_asset_alignment()` como argumento directo. Pero el assessment dict **nunca recibe** este campo. El gate `proposal_asset_alignment` en L835 intenta `assessment.get("site_presence_report")` → siempre None → **vuelve a ejecutar** `SitePresenceChecker` (L839-851), duplicando el trabajo y el costo de red.

**Causa raíz:** sin contrato tipado, los datos fluyen por canales separados (argumentos de función vs dict). El dato se calcula una vez pero nunca llega al lugar donde se necesita.

---

## Consumidores del assessment dict

| Consumidor | Archivo | Qué espera | Nota |
|-----------|---------|------------|------|
| 11 publication gates | `modules/quality_gates/publication_gates.py:157-169` | Cada gate accede subsets vía extractores multi-path (4-6 fallbacks) | **~135 líneas de extractores** |
| `run_publication_gates()` | `publication_gates.py:1277` | `Dict[str, Any]` sin validación | |
| `check_publication_readiness()` | `publication_gates.py:1304` | `Dict[str, Any]` sin validación | |

### Mapa gate → keys consumidas (trazado completo)

| Gate | Keys directas | Extractores llamados | Total paths |
|------|--------------|---------------------|-------------|
| hard_contradictions | validation_summary | _extract_conflicts | 5 |
| evidence_coverage | — | _extract_evidence_coverage | 6 |
| financial_validity | financial_data, financial_sources, financial_evidence_tier | _extract_financial_data | 5 |
| coherence | — | _extract_coherence_score | 4 |
| critical_recall | — | _extract_critical_recall | 5 |
| ethics | diagnostico_text, propuesta_text | — | 2 |
| content_quality | diagnostico_text, propuesta_text, hotel_data | — | 3 |
| asset_confidence | generated_assets | — | 1 |
| proposal_asset_alignment | generated_assets, proposal_services, site_presence_report, hotel_url, url, audit_schema | SitePresenceChecker (re-ejecutado) | 7 |
| tier_c_onboarding_required | financial_evidence_tier, hotel_data | — | 2 |
| coverage | pain_ledger, diagnostic_pain_ids, proposal_pain_ids | — | 3 |

---

## Implicaciones

1. **Cada nueva feature que requiere datos en los gates** obliga a editar `main.py:2663-2754` manualmente.
2. **No hay validación de esquema:** si un campo falta, el gate puede fallar en runtime con KeyError (aunque los extractores con `.get()` mitigan esto parcialmente).
3. **No hay documentación del contrato:** para saber qué espera cada gate, hay que leer ~135 líneas de extractores multi-path.
4. **Riesgo de regresión:** modificar el orden o nombre de un campo puede romper gates silenciosamente (pasan de FAIL a PASS o viceversa sin que nadie lo note).
5. **Deuda acumulativa:** cada fase que agrega campos al dict aumenta la fragilidad.
6. **Campos muertos/zombie** acumulan ruido: consistency_report, quality_gate_* (3), audit_schema, proposal_services (fantasma), hotel_url (fantasma), metrics vacío.
7. **Duplicación de cómputo:** SitePresenceChecker ejecutado 2 veces por falta de contrato.
8. **Cálculo tautológico:** `critical_recall` siempre da 1.0 porque `critical_issues == critical_issues_detected`.
9. **Campos fantasma:** proposal_services y hotel_url son buscados por los gates pero nunca inyectados — los defaults salvan, pero el AssessmentBuilder debe incluirlos explícitamente.

---

## Propuesta: AssessmentBuilder

### Objetivo

Centralizar la construcción del assessment dict en una clase `AssessmentBuilder` con:

- **Esquema tipado** (dataclass o Pydantic) que declare todos los campos requeridos y opcionales
- **Construcción declarativa:** el builder recibe los artefactos disponibles y los ensambla
- **Validación pre-gates:** antes de pasar a `run_publication_gates()`, validar que el esquema está completo
- **Contracto documentado:** cada gate declara qué campos necesita del assessment
- **Simplificación de extractores:** con schema validado, los extractores multi-path se reducen a acceso directo (ahorro: ~100 líneas, elimina ~15 líneas de dead code)

### Diseño tentativo (CORREGIDO con hallazgos 2026-05-27)

```python
# modules/assessment_builder.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class AssessmentPayload:
    """Contrato tipado entre main.py y publication_gates.
    
    CORREGIDO (2026-05-27): Campos agregados que los gates SÍ consumen
    y removidos los que NO consumen.
    RE-AUDITADO (2026-05-30): Agregados proposal_services, coherence_report.
    Confirmado audit_schema como zombie (0 consumidores vía dict).
    """
    # Core (consumido por proposal_asset_alignment, financial_validity)
    url: str
    hotel_name: str
    hotel_url: str = ""  # alias de url para extractors que buscan 'hotel_url'
    
    # Validation (consumido por hard_contradictions, evidence_coverage)
    validation_summary: Dict[str, Any] = field(default_factory=dict)
    
    # Financial (consumido por financial_validity, tier_c_onboarding)
    financial_data: Dict[str, Any] = field(default_factory=dict)
    financial_sources: Dict[str, Any] = field(default_factory=dict)
    financial_evidence_tier: str = "C"
    
    # Coherence (consumido por coherence gate)
    coherence_score: float = 0.0
    
    # Pain ledger / FASE-0 (consumido por coverage gate)
    pain_ledger: List[Dict] = field(default_factory=list)
    diagnostic_pain_ids: List[str] = field(default_factory=list)
    proposal_pain_ids: List[str] = field(default_factory=list)
    
    # Audit (consumido por critical_recall, proposal_asset_alignment)
    # NOTA: audit_schema es zombie en el dict (0 consumidores) — los datos fluyen
    # vía audit_result como argumento de función. Mantener por compatibilidad.
    audit_schema: Dict[str, Any] = field(default_factory=dict)
    critical_issues: List[str] = field(default_factory=list)
    # NOTA: critical_issues_detected ELIMINADO — es duplicado tautológico

    # Proposal services (consumido por proposal_asset_alignment)
    # NUEVO (2026-05-30): el gate lo busca pero nunca se inyecta; usa default ALL_PROMISED_SERVICES
    proposal_services: List[str] = field(default_factory=list)

    # Coherence report (consumido por extractor como fallback path 3)
    # NUEVO (2026-05-30): los extractores buscan coherence_report.overall_score
    coherence_report: Optional[Dict[str, Any]] = None
    
    # Documents / post-generation (consumido por ethics, content_quality)
    diagnostico_text: str = ""
    propuesta_text: str = ""
    
    # Assets (consumido por asset_confidence, proposal_asset_alignment)
    generated_assets: List[Dict] = field(default_factory=list)
    evidence_coverage: float = 0.95  # TODO: calcular en vez de hardcodear
    
    # Site presence (consumido por proposal_asset_alignment)
    # NUEVO: evita duplicación de SitePresenceChecker
    site_presence_report: Optional[Dict[str, Any]] = None
    
    # Regional (consumido por content_quality, tier_c_onboarding)
    hotel_data: Dict[str, str] = field(default_factory=dict)
    
    # Metrics (consumido por coherence, evidence_coverage, critical_recall)
    # CORREGIDO: asegurar que metrics tenga todas las claves que los extractores buscan
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    # ELIMINADOS (campos muertos/zombie — 0 consumidores vía assessment dict):
    # - consistency_report: DEAD KEY, construido en L2838, nunca leído del dict
    #   (NOTA: variable consistency_report sí se consume directamente en summary JSON L3043-3047)
    # - quality_gate_issues: ZOMBIE, locals().get(), 0 consumers
    # - quality_gate_blockers: ZOMBIE, locals().get(), 0 consumers
    # - quality_gate_warnings: ZOMBIE, locals().get(), 0 consumers
    # - audit_schema: ZOMBIE en dict, 0 consumidores (objeto audit_result sí usado como arg)
    # - coherence_checks: NO consumido por gates (solo leen coherence_score)
    # - coherence_errors: NO consumido por gates
    # - coherence_warnings: NO consumido por gates


class AssessmentBuilder:
    """Centralized, validated assessment dict construction."""
    
    def __init__(self):
        self._payload = AssessmentPayload()
    
    def with_core(self, url: str, hotel_name: str) -> 'AssessmentBuilder':
        self._payload.url = url
        self._payload.hotel_name = hotel_name
        self._payload.hotel_url = url  # alias
        return self
    
    def with_validation(self, validation_summary, whatsapp_validation) -> 'AssessmentBuilder':
        ...
    
    def with_financial(self, rooms, adr_cop, occupancy_rate, direct_channel_pct,
                       financial_sources, financial_breakdown) -> 'AssessmentBuilder':
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
    
    def with_site_presence(self, site_presence_report) -> 'AssessmentBuilder':
        """NUEVO: inyecta site_presence_report para evitar recálculo en el gate."""
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
# Antes (actual, ~87 líneas en 3 etapas):
assessment = {
    "url": args.url,
    "hotel_name": hotel_name,
    # ... 80+ líneas más
}
assessment["diagnostico_text"] = f.read()
assessment["propuesta_text"] = f.read()
assessment['consistency_report'] = consistency_report.to_dict()
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
builder.with_site_presence(site_presence_report)  # NUEVO: evita duplicación

assessment = builder.build()
```

### Simplificación de extractores (ahorro estimado: ~100 líneas, elimina ~15 dead code)

Con schema validado, los extractores multi-path se reducen a acceso directo:

```python
# Antes (_extract_evidence_coverage, 33 líneas, 6 paths):
def _extract_evidence_coverage(self, assessment):
    if "evidence_coverage" in assessment:
        return float(assessment["evidence_coverage"])
    if "metrics" in assessment and isinstance(assessment["metrics"], dict):
        coverage = assessment["metrics"].get("evidence_coverage")
        if coverage is not None:
            return float(coverage)
    if "quality_metrics" in assessment:
        coverage = assessment["quality_metrics"].get("evidence_coverage")
        if coverage is not None:
            return float(coverage)
    if "claims" in assessment:
        claims = assessment["claims"]
        ...
    if "diagnostic" in assessment:
        ...
    return 0.0

# Después (3 líneas, 1 path validado):
def _extract_evidence_coverage(self, assessment):
    return float(assessment["evidence_coverage"])
```

---

## Esfuerzo estimado (REVISADO con hallazgos 2026-05-27)

| Actividad | Original | Revisado | Delta |
|-----------|----------|----------|-------|
| Auditar qué campos consume cada uno de los 11 gates | 1.5h | 2.5h | +1h (los extractores multi-path requieren tracing) |
| Diseñar `AssessmentPayload` dataclass con todos los campos | 1h | 1.5h | +0.5h (incluir campos omitidos, eliminar muertos) |
| Implementar `AssessmentBuilder` con métodos fluid | 3h | 3h | Sin cambio |
| Migrar `main.py:2663-2754` al builder | 1.5h | 2h | +0.5h (3 etapas + site_presence_report injection) |
| Simplificar extractores en publication_gates.py | — | 1.5h | **NUEVO** (eliminar ~100 líneas redundantes + ~15 dead code) |
| Eliminar campos muertos/zombie/fantasma | — | 1h | **NUEVO** (5 zombie + 2 fantasma) |
| Tests (validación de esquema + integración) | 2h | 2.5h | +0.5h (validar extractores simplificados) |
| Verificación E2E con v4complete | 1h | 1h | Sin cambio |
| **Total** | **~10h** | **~13.5h** | **+3.5h** |

---

## Relación con otros hallazgos

| Hallazgo | Relación |
|----------|----------|
| PIPELINE-FIX (v4.48.0) | Parchó 4 campos huérfanos. NUEVO-8 es la causa raíz estructural. Los 4 campos sí son consumidos (coverage gate + tier_c gate). |
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

## Referencias cruzadas (CORREGIDAS)

| Archivo | Sección/Línea | Dato clave | Estado |
|---------|--------------|------------|--------|
| `main.py` | L2663-2754 | Construcción manual del assessment dict (~87 líneas, 3 etapas) | ✅ Verificado |
| `main.py` | L2697-2712 | PIPELINE-FIX: 4 campos huérfanos inyectados (pain_ledger, diagnostic_pain_ids, proposal_pain_ids, financial_evidence_tier) | ✅ Verificado |
| `main.py` | L2687-2688 | `critical_issues` duplicado con `critical_issues_detected` | ✅ Verificado |
| `main.py` | L2713 | `evidence_coverage: 0.95` hardcodeado con "# Default assumption" | ✅ Verificado |
| `main.py` | L2717-2719 | `quality_gate_issues/blockers/warnings` vía `locals().get()` — **0 consumidores** | ✅ Verificado |
| `main.py` | L2838 | `consistency_report` inyectado en assessment dict — **0 consumidores vía dict** (variable sí usada en summary JSON L3043-3047) | ✅ Verificado |
| `main.py` | L2714-2716 | `metrics` solo contiene `coherence_score` — extractores buscan 3 claves | ✅ Verificado |
| `main.py` | L2597-2622 | `site_presence_report` calculado pero NO inyectado en assessment → recalculado en gate | ✅ Verificado |
| `modules/quality_gates/publication_gates.py` | L157-169 | 11 gates, cada uno accede subsets del dict vía extractores multi-path | ✅ Verificado |
| `modules/quality_gates/publication_gates.py` | L1138-1272 | **~135 líneas de extractores defensivos** (5 extractores, 4-6 paths c/u, ~15 líneas dead code) | ✅ Verificado |
| `modules/quality_gates/publication_gates.py` | L1277 | `run_publication_gates(assessment: Dict[str, Any])` | ✅ Verificado |
| `modules/quality_gates/publication_gates.py` | L1304 | `check_publication_readiness(assessment: Dict[str, Any])` | ✅ Verificado |
| `modules/quality_gates/publication_gates.py` | L835-851 | `proposal_asset_alignment` gate re-ejecuta SitePresenceChecker (ya ejecutado en main.py) | ✅ Verificado |
| `modules/quality_gates/publication_gates.py` | L1267-1270 | `critical_recall` = `len(detected)/len(critical_issues)` — como son el mismo array, siempre 1.0 | ✅ Verificado |
| ~~`.opencode/plans/PIPELINE-FIX-PLAN.md`~~ | ~~L41~~ | ❌ **ARCHIVO NO EXISTE** — referencia eliminada | ❌ Refutado |
| `ROADMAP.md` | L369 | "AssessmentBuilder centralizado — sesión futura dedicada" | ✅ Verificado |

### NUEVOS hallazgos (re-auditoría 2026-05-30)

| Archivo | Sección/Línea | Dato clave | Estado |
|---------|--------------|------------|--------|
| `main.py` | L2689-2696 | `audit_schema` inyectado con 6 sub-campos — **0 consumidores vía dict** | ✅ NUEVO |
| `modules/quality_gates/publication_gates.py` | L832 | `proposal_services` buscado por gate pero **nunca inyectado** — gate usa default | ✅ NUEVO |
| `modules/quality_gates/publication_gates.py` | L836 | `hotel_url` buscado por gate pero **no existe como clave independiente** — fallback a `url` | ✅ NUEVO |
| `modules/quality_gates/publication_gates.py` | L1211-1242 | `_extract_coherence_score` paths 3-4 (coherence_report, quality_metrics) — dead code | ✅ NUEVO |
| `modules/quality_gates/publication_gates.py` | L1151-1183 | `_extract_evidence_coverage` paths 3-6 (quality_metrics, claims, diagnostic) — dead code | ✅ NUEVO |

---

## Prompt para diseñar el plan (sesión futura)

```
Carga .opencode/context/NUEVO-8-ASSESSMENT-DICT-CONTEXT.md.
También carga ROADMAP.md para contexto de fases.
Diseña un plan de implementación por fases siguiendo phased_project_executor.md.
Alcance: AssessmentBuilder + migración de main.py + simplificación de extractores
         en publication_gates.py + eliminación de campos muertos + tests + v4complete E2E.
NO implementar aún — solo diseñar fases con R3 scope.
```
