# CONTEXT VALIDADO: DT-4 Residual Fixes — Post-Release v4.65.0

> **Documento actualizado**: 2026-07-27
> **Fuente original**: FASE-RELEASE DT-4-ROOT-CAUSE-2026-07-25
> **Repositorio auditado**: `/mnt/c/Users/Jhond/Github/iah-cli`
> **Versión auditada**: v4.65.0
> **HEAD auditado**: `0181b54` — `docs: context for DT-4 residual fixes (DT4-R1 MAPPED_TO_SERVICE gap + DT4-R2 SitePresence boost)`
> **Hotel de evidencia**: Zi One Luxury / Zione — `https://zione.co/`
> **Modo**: Contexto validado y ampliado. NO implementar todavía.

---

## 0. Veredicto ejecutivo

El contexto original identificó correctamente que el run de Zi One terminó sin documentos comerciales entregables y que existía una desconexión entre la reconciliación post-orchestrator y los gates de publicación.

Sin embargo, su diagnóstico de DT4-R1 es incorrecto y su propuesta de solución de una línea no debe ejecutarse:

- `MAPPED_TO_SERVICE` **ya existe** en `_JUSTIFIED_STATUSES`.
- El reconciliador **sí genera** `pain_ledger_resolved.json` con `MAPPED_TO_SERVICE`.
- El coverage gate **sí sabe interpretar** `MAPPED_TO_SERVICE`.
- El fallo real es que `pain_ledger_resolved` **no se inyecta en el assessment** que recibe el gate.
- Por eso el gate vuelve al `pain_ledger.json` original y observa `no_whatsapp_visible` como no justificado.

DT4-R2 también es real, pero el problema no se limita a “pasar un parámetro desde un archivo al validator”. Hay varias ejecuciones de `CoherenceValidator`, varias rutas de `SitePresenceChecker` y formas incompatibles de representar el reporte.

### Veredicto consolidado

| Elemento | Estado factual | Clasificación |
|---|---|---|
| Zi One ejecutó v4complete y terminó con exit 0 | Confirmado por evidencia preservada | CONFIRMADO |
| Los documentos comerciales fueron eliminados/no quedaron entregables | Confirmado; no existen en el output auditado | CONFIRMADO |
| El reconciliador produjo `MAPPED_TO_SERVICE` | Confirmado | CONFIRMADO |
| `MAPPED_TO_SERVICE` falta en `_JUSTIFIED_STATUSES` | El código vivo lo contradice | REFUTADO |
| El coverage gate recibe `pain_ledger_resolved` | No; el assessment no tiene ese campo | REFUTADO / CAUSA REAL IDENTIFICADA |
| El boost de SitePresence existe en `_check_whatsapp_verified()` | Confirmado | CONFIRMADO |
| El boost llega a las validaciones de coherencia del flujo principal | No en las llamadas pre/post del orchestrator | REFUTADO COMO “RESUELTO”; DEFECTO CONFIRMADO |
| El score de WhatsApp quedó en 0.30 | Confirmado en evidencia | CONFIRMADO |
| Agregar una línea al set resuelve el problema | No-op; la línea ya existe | REFUTADO |
| El fix es estrictamente de una línea | Incorrecto; requiere corrección de contrato de datos | REFUTADO |
| Los commercial gates seguirían pudiendo bloquear el delivery | Confirmado | CONFIRMADO |

---

## 1. Estado de validación ejecutada

### Pruebas ejecutadas

Comando usado:

```bash
./venv/Scripts/python.exe -m pytest \
  tests/quality_gates/test_coverage_gate.py \
  tests/test_post_orchestrator_reconciler.py \
  tests/quality_gates/test_gate_presence.py \
  tests/commercial_documents/test_financial_coherence.py -q
```

Resultado real:

```text
35 passed, 8 warnings in 3.47s
```

Los warnings corresponden a deprecaciones de Pydantic v2; no fueron introducidos por esta auditoría.

También se ejecutó compilación sintáctica sobre:

- `modules/quality_gates/publication_gates.py`
- `modules/commercial_documents/coherence_validator.py`
- `modules/asset_generation/v4_asset_orchestrator.py`
- `main.py`

Resultado:

- Compilación exitosa.
- Existe un `SyntaxWarning` preexistente en `v4_asset_orchestrator.py:101` por una secuencia de escape `\\)` dentro de texto.

### Limitación importante de los tests

Los tests unitarios pasan porque verifican por separado:

1. que el reconciliador puede producir `MAPPED_TO_SERVICE`;
2. que el coverage gate acepta ese status si se le entrega directamente;
3. que SitePresence puede marcar un asset como existente.

No existe un test de integración que pruebe el recorrido defectuoso completo:

```text
PostOrchestratorReconciler
    → AssetGenerationResult / main.py
    → AssessmentBuilder
    → assessment["pain_ledger_resolved"]
    → publication_gates._coverage_gate()
```

Tampoco existe una prueba integrada que demuestre que el `SitePresenceReport` real llegue a las validaciones pre y post de `CoherenceValidator` dentro del orchestrator.

---

## 2. DT4-R1 — Diagnóstico original refutado

### Claim original

El contexto original afirmaba que `MAPPED_TO_SERVICE` no estaba en:

```text
modules/quality_gates/publication_gates.py::_JUSTIFIED_STATUSES
```

y proponía agregarlo junto a `ASSET_GENERATED`.

### Código vivo

`modules/quality_gates/publication_gates.py:1184-1188`:

```python
# Acceptable justification statuses — pain_ids with these statuses do NOT
# need to appear in diagnostic or proposal.
_JUSTIFIED_STATUSES: Set[str] = {
    "JUSTIFIED_SKIP", "BLOCKED", "MAPPED_TO_SERVICE", "ASSET_GENERATED"
}
```

El gate usa realmente el set en `publication_gates.py:1278-1288`:

```python
is_justified = entry.status in self._JUSTIFIED_STATUSES

if is_justified:
    justified_count += 1
elif in_diagnostic or in_proposal:
    covered += 1
else:
    uncovered.append(entry.pain_id)
```

### Evidencia histórica

`git blame` muestra que estos estados fueron incorporados por el commit:

```text
73c0765 feat(FASE-0): post-orchestrator reconciler — causa raíz transversal DT-4
```

El contexto residual fue creado después, en `0181b54`.

Además, el test específico ya existe:

`tests/quality_gates/test_coverage_gate.py:133-145`:

```python
def test_passes_when_pain_has_status_mapped_to_service(self, orchestrator):
    assessment = make_assessment(
        pain_ledger=[{"pain_id": "low_ota_divergence", "status": "MAPPED_TO_SERVICE"}],
        diagnostic_pain_ids=[],
        proposal_pain_ids=[],
    )

    result = orchestrator._coverage_gate(assessment)

    assert result.passed is True
    assert result.details["justified"] == 1
```

### Veredicto DT4-R1

**REFUTADO.**

El cambio propuesto en el contexto sería un no-op y no debe implementarse.

---

## 3. Causa raíz real del coverage failure

### Evidencia del reconciliador

El archivo preservado demuestra que la reconciliación sí funcionó:

`.opencode/plans/DT-4-ROOT-CAUSE-2026-07-25/evidence/pain_ledger_resolved.json`:

```json
{
  "pain_id": "no_whatsapp_visible",
  "status": "MAPPED_TO_SERVICE"
}
```

Su resumen es:

```json
{
  "total": 9,
  "asset_generated": 8,
  "mapped_to_service": 1,
  "justified_skip": 0
}
```

El reconciliador se ejecuta en:

`modules/asset_generation/v4_asset_orchestrator.py:521-533`:

```python
reconciler = PostOrchestratorReconciler()
...
reconciler.reconcile(
    asset_generation_report_path=asset_gen_report_path,
    pain_ledger_path=pain_ledger_path,
    output_path=pain_ledger_resolved_path,
)
```

El método incluso retorna el resultado reconciliado, pero el caller no conserva ese valor en el objeto de resultado que luego usa `main.py`.

### Evidencia del gate

El gate report del mismo run dice:

`gate_report_20260727_140459.json:160-173`:

```json
{
  "gate_name": "coverage_no_silent_drop",
  "passed": false,
  "status": "FAILED",
  "message": "Brecha(s) sin cobertura ni justificacion: no_whatsapp_visible",
  "value": 0.8888888888888888,
  "details": {
    "total_detected": 9,
    "covered": 8,
    "justified": 0,
    "uncovered": ["no_whatsapp_visible"]
  }
}
```

La combinación de ambas evidencias prueba que el gate no consumió el ledger reconciliado.

### El fallback existe, pero nunca se activa

`publication_gates.py:1232-1238`:

```python
# Try pain_ledger_resolved first (post-orchestrator reconciliation),
# fallback to pain_ledger if not available.
raw = assessment.get("pain_ledger_resolved")
if raw and isinstance(raw, dict):
    pain_ledger_raw = raw.get("entries", raw)
else:
    pain_ledger_raw = raw or assessment.get("pain_ledger")
```

El problema es que el campo esperado no existe en el assessment.

`modules/assessment_builder.py:61-64` solo declara:

```python
pain_ledger: List[Dict] = field(default_factory=list)
diagnostic_pain_ids: List[str] = field(default_factory=list)
proposal_pain_ids: List[str] = field(default_factory=list)
```

No existe `pain_ledger_resolved`.

`AssessmentBuilder.with_pain_ledger()` (`assessment_builder.py:148-167`) solo setea `pain_ledger`, `diagnostic_pain_ids` y `proposal_pain_ids`.

En `main.py:2657-2661`, se carga únicamente el ledger original:

```python
pain_ledger_path = _get_pipeline_path(output_dir, hotel_id, "pain_ledger.json")
if pain_ledger_path.exists():
    pain_ledger_entries = PainLedger().load(pain_ledger_path)
```

Y en `main.py:2764`:

```python
builder.with_pain_ledger(pain_ledger_entries, diagnostic_summary, asset_plan)
```

No hay carga ni inyección de `pain_ledger_resolved.json`.

### Flujo real

```text
PostOrchestratorReconciler
    │
    ├── escribe pain_ledger_resolved.json correctamente
    │
    └── el resultado no se conserva en AssetGenerationResult/main.py
                │
                ▼
main.py carga pain_ledger.json original
                │
                ▼
AssessmentBuilder solo crea assessment["pain_ledger"]
                │
                ▼
assessment.get("pain_ledger_resolved") → None
                │
                ▼
coverage gate hace fallback al ledger original
                │
                ▼
no_whatsapp_visible permanece DETECTED
                │
                ▼
coverage_no_silent_drop = FAILED
```

### Veredicto de causa raíz

**CRÍTICO — contrato productor-consumidor incompleto.**

La reconciliación no está integrada en el objeto de assessment que consumen los gates.

---

## 4. DT4-R2 — Boost de SitePresence no cableado a CoherenceValidator

### Lo que sí existe

`modules/commercial_documents/coherence_validator.py:357-379` acepta:

```python
def _check_whatsapp_verified(
    self,
    assets: List[AssetSpec],
    validation_summary: ValidationSummary,
    whatsapp_html_detected: bool = False,
    site_presence_report: Optional[Dict[str, Any]] = None,
):
```

Y el boost está implementado en `coherence_validator.py:420-424`:

```python
confidence_score = self._confidence_level_to_score(whatsapp_field.confidence)

if site_whatsapp_exists:
    confidence_score = max(confidence_score, 0.95)
```

### Evidencia de que el boost no se aplicó

`coherence_validation.json:27-31`:

```json
{
  "name": "whatsapp_verified",
  "passed": false,
  "score": 0.3,
  "message": "WhatsApp con confidence insuficiente (0.30) - requiere >= 0.9",
  "severity": "error"
}
```

El `asset_generation_report.json` confirma simultáneamente:

```json
{
  "asset_type": "whatsapp_button",
  "presence_status": "exists",
  "site_verified": true,
  "pain_ids_affected": ["no_whatsapp_visible"]
}
```

### Las llamadas que omiten SitePresence

#### Validación pre-assets en main.py

`main.py:2395-2402` llama:

```python
pre_coherence_report = coherence_validator.validate(
    temp_diagnostic,
    temp_proposal,
    asset_plan,
    validation_summary,
    whatsapp_html_detected=...,
    generated_assets=None
)
```

No pasa `site_presence_report`.

#### Validación pre-generación en el orchestrator

`modules/asset_generation/v4_asset_orchestrator.py:282-285`:

```python
coherence = self.coherence_validator.validate(
    diagnostic_doc, proposal_doc, asset_specs, validation_summary
)
```

No pasa `site_presence_report`.

#### Validación post-generación en el orchestrator

`v4_asset_orchestrator.py:419-423`:

```python
post_coherence_report = self.coherence_validator.validate(
    diagnostic_doc, proposal_doc, asset_specs, validation_summary,
    generated_assets=generated_assets_dict
)
```

Tampoco pasa `site_presence_report`, aunque a esa altura `skipped_assets` ya contiene la evidencia de que WhatsApp existe.

### Veredicto DT4-R2

**CONFIRMADO Y AMPLIADO.**

Se debe corregir el flujo completo, no solamente agregar texto a una llamada aislada.

Severidad recomendada: **ALTA**, no MEDIA, porque el error produce una señal de coherencia falsa y puede participar en decisiones de bloqueo.

---

## 5. Hallazgo DT4-N1 — Shapes incompatibles de SitePresenceReport

`CoherenceValidator` tipa el parámetro como `Optional[Dict[str, Any]]` y busca:

```python
site_presence_report.get("whatsapp_button", {})
```

Pero `SitePresenceChecker` produce la dataclass:

`modules/asset_generation/site_presence_checker.py:96-103`:

```python
@dataclass
class SitePresenceReport:
    site_url: str
    checked_at: datetime
    results: Dict[str, PresenceCheckResult]
```

La estructura real es conceptualmente:

```python
report.results["whatsapp_button"].status
```

no:

```python
report["whatsapp_button"]["presence_status"]
```

Además, `AssessmentBuilder._to_dict()` usa `dataclasses.asdict()` (`assessment_builder.py:261-264`), lo cual convierte recursivamente la dataclass en dict y elimina identidad/atributos de objeto.

Esto puede causar tres fallos distintos:

1. `AttributeError` si se pasa la dataclass directamente y el consumer intenta `.get()`.
2. WhatsApp no detectado si llega serializado dentro de `results` y el validator busca en la raíz.
3. Comparación fallida entre `PresenceStatus.EXISTS` y la cadena `"exists"`.

### Solución raíz recomendada

Definir una representación canónica de presencia, por ejemplo:

```python
{
    "site_url": "...",
    "checked_at": "...",
    "results": {
        "whatsapp_button": {
            "status": "exists",
            "site_verified": True,
            "confidence": 1.0
        }
    }
}
```

Y centralizar un adaptador que acepte únicamente en el borde:

- `SitePresenceReport` dataclass;
- dict serializado;
- evidencia de `skipped_assets`.

Los consumidores no deben volver a implementar su propio shape resolution.

---

## 6. Hallazgo DT4-N2 — SitePresence se calcula/reconstruye varias veces

El pipeline conoce la presencia del sitio por varias rutas:

1. `ConditionalGenerator`, por asset, dentro de `V4AssetOrchestrator`.
2. `main.py:2673-2680`, que vuelve a ejecutar `SitePresenceChecker` antes de generar la propuesta.
3. `publication_gates.py:861-890`, que puede reconstruir un reporte fake a partir de `skipped_assets`.
4. `publication_gates.py:895-919`, que puede ejecutar otro `SitePresenceChecker` si el reporte no existe.

Esto crea:

- llamadas de red duplicadas;
- riesgo de resultados distintos en momentos distintos;
- objetos dataclass, dict y `SimpleNamespace` para el mismo concepto;
- lógica de fallback distribuida entre productores y consumidores;
- dificultad para saber qué evidencia es canónica.

### Solución raíz

Calcular SitePresence una vez por ejecución y propagar el snapshot normalizado a todos los consumidores. Los gates deben validar; no deben descubrir ni reconstruir la evidencia primaria.

---

## 7. Hallazgo DT4-N3 — Los gates mutan el assessment y se ejecutan dos veces

`publication_gates.py:861-890` puede hacer:

```python
assessment["site_presence_report"] = SimpleNamespace(...)
```

El gate deja de ser una función pura y muta el input.

Además, `main.py:2775-2776` ejecuta:

```python
gate_results = run_publication_gates(assessment, gate_config)
readiness_report = check_publication_readiness(assessment)
```

`check_publication_readiness()` vuelve a llamar internamente a `run_publication_gates()`.

Consecuencias:

- el resultado depende del orden de `self.gates`;
- la segunda ejecución puede observar un assessment diferente al primero;
- los reportes pueden variar aunque no haya cambiado ningún input externo;
- un gate puede preparar datos para otro gate por efecto lateral.

### Solución raíz

- Crear el assessment completo antes de ejecutar gates.
- Ejecutar los gates una sola vez.
- Derivar readiness desde los resultados ya calculados.
- Eliminar mutaciones de `assessment` dentro de gates.

---

## 8. Hallazgo DT4-N4 — Coherence score pre/post no tiene fuente única

El orchestrator ejecuta coherencia antes y después de generar assets:

- pre-gen: `v4_asset_orchestrator.py:282-285`;
- post-gen: `v4_asset_orchestrator.py:419-424`.

Sin embargo, `AssetGenerationResult` conserva:

- `coherence_report` como reporte pre-gen;
- `post_coherence_score` como número separado;
- no conserva el `post_coherence_report` como reporte final principal.

`AssessmentBuilder.with_coherence()` usa:

`modules/assessment_builder.py:137-146`:

```python
self._payload.coherence_score = (
    asset_result.coherence_report.overall_score
    if asset_result
    else 0.0
)
```

Esto usa el reporte pre-gen, no el score post-gen.

La evidencia del asset report muestra:

```json
{
  "coherence_score_pre": 0.84,
  "coherence_score_post": 0.82,
  "coherence_score_final": 0.82
}
```

Mientras el gate report registra:

```json
"coherence": {
  "value": 0.8424242424242424
}
```

Hay más de una fuente de score para la misma ejecución.

### Solución raíz

Definir `final_coherence_report` como única fuente canónica cuando exista validación post-gen. Conservar pre/post únicamente como trazabilidad, no como inputs competidores.

---

## 9. Hallazgo DT4-N5 — Publication y delivery reports usan alignment distinto

`delivery_quality_report.json` de la evidencia dice:

```json
{
  "status": "FAIL",
  "proposal_asset_gate": {
    "passed": false,
    "aligned": 5,
    "total": 7
  }
}
```

Pero `gate_report_20260727_140459.json` dice:

```json
{
  "gate_name": "proposal_asset_alignment",
  "passed": true,
  "message": "All 7 promised services have assets (7/7 aligned, 2 already in production)",
  "details": {
    "total_services": 5,
    "aligned_count": 5,
    "present_in_production": ["Botón de WhatsApp", "Schema Organization"]
  }
}
```

La diferencia puede explicarse parcialmente por que un reporte excluye los assets existentes del denominador y el otro no, pero el sistema no expone una semántica única y verificable.

### Hallazgo adicional

El mensaje comunica 7/7, mientras `details.total_services` es 5. Esto es ambiguo para consumidores automáticos.

### Solución raíz

Usar un resultado común con campos explícitos:

```json
{
  "promised_services_total": 7,
  "generated_aligned": 5,
  "present_in_production": 2,
  "unresolved": 0,
  "coverage_ratio": 1.0
}
```

El publication gate y delivery quality report deben serializar el mismo objeto.

---

## 10. Hallazgo DT4-N6 — El bloqueo comercial es independiente de coverage

La evidencia de `commercial_gates_report.json` muestra:

```text
CG-ROI-NEGATIVE: BLOCKING
Beneficio neto 6m negativo ($-1,330,590 COP) y ROI 0.45X
```

También existe `CG-TECH-JARGON` como warning.

`BLOCKED_BY_GATES.md` indica que se deben resolver los commercial gates bloqueantes y los publication gates antes de reejecutar.

Por tanto, incluso si coverage pasa después de integrar `pain_ledger_resolved`, la existencia de documentos cliente no queda garantizada. La corrección técnica del ledger no resuelve la viabilidad comercial de Zi One.

El contexto original sí advertía que CG-ROI-NEGATIVE podía seguir bloqueando, pero su criterio de éxito —documentos presentes inmediatamente después de corregir coverage— es demasiado fuerte y debe dividirse:

1. coverage gate corregido;
2. coherencia corregida;
3. commercial viability decision tomada;
4. delivery final verificado.

---

## 11. Hallazgo DT4-N7 — Estado documental y drifts adyacentes

Estos hallazgos no son la causa del fallo DT4, pero afectan la confiabilidad del contexto y deben quedar registrados:

### REGISTRY.md

`docs/contributing/REGISTRY.md:4` contiene:

```text
Version actual: v4.58.0
```

Mientras `VERSION.yaml` y el contexto auditado indican v4.65.0.

Esto es drift documental confirmado.

### DOMAIN_PRIMER.md

`.agent/knowledge/DOMAIN_PRIMER.md:6` contiene mojibake:

```text
Root cause reconciliation â€” Post-orchestrator reconciler
```

La línea debería conservar un em dash correctamente codificado. El archivo también usa CRLF.

Estos archivos aparecen modificados en el working tree al momento de la auditoría:

```text
M .agent/knowledge/DOMAIN_PRIMER.md
M docs/contributing/REGISTRY.md
```

No se modificaron durante esta auditoría.

---

## 12. Recomendación de solución raíz — sin implementar

No ejecutar el plan original de dos pasos. La secuencia recomendada para una futura sesión de implementación es:

### Macro-fase A — Integrar el ledger reconciliado

1. Agregar `pain_ledger_resolved` al contrato `AssessmentPayload`.
2. Exponer el resultado reconciliado desde `AssetGenerationResult` o cargarlo explícitamente en `main.py`.
3. Crear `AssessmentBuilder.with_resolved_pain_ledger(...)`.
4. Inyectarlo antes de `run_publication_gates()`.
5. Hacer que la ausencia del ledger reconciliado sea `BLOCKED` cuando la reconciliación era esperada, en vez de hacer fallback silencioso.
6. Añadir test integrado:

```text
reconciler → builder → assessment → coverage gate
```

### Macro-fase B — Normalizar SitePresence

1. Elegir una estructura canónica serializable.
2. Crear un adaptador único para dataclass/dict/status enum.
3. Calcular SitePresence una sola vez.
4. Propagarlo al orchestrator y a `CoherenceValidator` pre/post según timing.
5. Eliminar reconstrucciones fake y rechecks redundantes.
6. Añadir tests para:
   - `SitePresenceReport` real;
   - dict producido por `asdict()`;
   - `PresenceStatus.EXISTS` y `"exists"`;
   - `whatsapp_button` existente;
   - error de verificación.

### Macro-fase C — Unificar CoherenceValidator

1. Conservar `pre_coherence_report` y `post_coherence_report` como trazabilidad.
2. Definir `final_coherence_report` como fuente única.
3. Hacer que AssessmentBuilder, gate report y v4complete report consuman el mismo score final.
4. Verificar la fórmula ponderada manualmente.
5. Eliminar consumidores que mezclen score pre-gen y post-gen.

### Macro-fase D — Unificar alignment

1. Extraer un DTO/resultado canónico de alignment.
2. Hacer que publication gates y delivery quality report consuman el mismo resultado.
3. Separar explícitamente generated/present/missing/redundant/indeterminate.
4. Añadir una prueba de igualdad semántica entre ambos reportes.

### Macro-fase E — Decisión comercial y E2E

Esta fase debe venir después de las pruebas locales y requiere una decisión explícita sobre `CG-ROI-NEGATIVE`:

1. No ocultar ni relajar el gate comercial.
2. Decidir si Zi One requiere:
   - precio menor;
   - fase de activación/onboarding;
   - modelo ligado a recuperación;
   - transparencia con propuesta preliminar.
3. Ejecutar un único `v4complete` después de que A-D pasen.
4. Verificar separadamente:
   - coverage;
   - coherence;
   - commercial gates;
   - existencia de documentos;
   - contenido final y trazabilidad.

---

## 13. No objetivos de esta actualización

Esta actualización NO implementa:

- cambios en `_JUSTIFIED_STATUSES`;
- cambios en `publication_gates.py`;
- cambios en `AssessmentBuilder`;
- cambios en `CoherenceValidator`;
- cambios en `v4_asset_orchestrator.py`;
- reejecución de v4complete;
- modificación de `PAIN_SOLUTION_MAP`;
- modificación de `scenario_calculator.py`;
- version bump.

---

## 14. Criterios para declarar la futura solución completa

No declarar DT4 resuelto hasta verificar todos estos puntos:

- [ ] `pain_ledger_resolved` existe en el contrato de assessment.
- [ ] El assessment usado por publication gates contiene el ledger reconciliado.
- [ ] `coverage_no_silent_drop` cuenta `no_whatsapp_visible` como justificado.
- [ ] El gate report muestra `justified >= 1` y `uncovered = []` para este caso.
- [ ] El boost SitePresence se ejecuta en CoherenceValidator con el reporte real.
- [ ] `whatsapp_verified.score` deja de ser 0.30 cuando SitePresence confirma `exists`.
- [ ] Dataclass, dict serializado y enum/string tienen una única normalización.
- [ ] No hay reejecuciones redundantes de SitePresence sin justificación.
- [ ] Publication y delivery alignment reportan el mismo contrato y totales.
- [ ] El score final de coherencia es único y trazable.
- [ ] Se ejecutan tests de integración, no solo tests unitarios aislados.
- [ ] Se valida nuevamente Zi One después de A-D.
- [ ] Se toma una decisión explícita sobre CG-ROI-NEGATIVE.
- [ ] Se verifica si los documentos existen y si no fueron eliminados por otro gate.

---

## 15. Prompt para la siguiente sesión

Usar este prompt en una NUEVA sesión. No implementar en la sesión de actualización del contexto:

```text
Carga y ejecuta una auditoría de implementación sobre:
/mnt/c/Users/Jhond/Github/iah-cli/.opencode/context/CONTEXT-DT4-RESIDUAL-FIXES.md

El contexto ya fue validado contra el código vivo. NO asumas que DT4-R1 consiste en agregar MAPPED_TO_SERVICE: ese status ya existe en publication_gates.py.

Objetivo de la siguiente sesión:
1. Diseñar un plan phased_project_executor para integrar pain_ledger_resolved al AssessmentBuilder y al coverage gate.
2. Diseñar la normalización canónica de SitePresenceReport y su propagación a las validaciones pre/post de CoherenceValidator.
3. Diseñar la fuente única de final_coherence_report.
4. Diseñar la unificación de proposal_asset_alignment entre publication_gates y delivery_quality_report.
5. Mantener CG-ROI-NEGATIVE como decisión comercial separada; no relajarlo ni ocultarlo.
6. Incluir tests de integración antes de cualquier v4complete.
7. No implementar todavía. Primero producir el plan completo, verificar scope R3 y registrar dependencias.

Usa como hechos confirmados:
- publication_gates.py:1186-1188 ya contiene MAPPED_TO_SERVICE.
- publication_gates.py:1232-1238 espera pain_ledger_resolved, pero AssessmentBuilder/main.py nunca lo inyectan.
- v4_asset_orchestrator.py:521-533 genera el resolved ledger y descarta el resultado.
- coherence_validator.py:420-424 contiene el boost SitePresence.
- v4_asset_orchestrator.py:282-285 y 419-423 no pasan site_presence_report al validator.
- Zi One produjo score whatsapp_verified=0.30 y coverage_no_silent_drop FAILED por no_whatsapp_visible.
- Tests relevantes actuales: 35 passed, pero no existe test integrado del puente reconciler→assessment→gate.

NO ejecutes v4complete hasta que el plan sea validado y las fases locales de contrato y tests estén completadas.
```

---

## 16. Estado final del documento

Este archivo queda como contexto validado y plan-ready, no como autorización de implementación.

La causa raíz vigente es:

```text
La reconciliación post-orchestrator produce el estado correcto,
pero el contrato de datos no lo propaga al assessment consumidor;
además, SitePresence y coherence tienen múltiples rutas y shapes
sin una fuente canónica única.
```
