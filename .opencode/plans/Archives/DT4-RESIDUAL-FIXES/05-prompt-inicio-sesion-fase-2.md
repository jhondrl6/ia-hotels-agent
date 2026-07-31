# FASE-2: DT4-R2-SITE-PRESENCE — SitePresence Normalization + Wiring ★

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (decisión arquitectónica cross-module NO delegable)
> **Iteraciones máx**: 60
> **Depende de**: —
> **Bloquea a**: FASE-3 (Coherence), FASE-6 (E2E)
> **⚠️ COMPLEJIDAD: ALTA** — Esta es la fase de mayor complejidad técnica del plan

## ⚠️ Hechos Confirmados (NO re-verificar)

- `coherence_validator.py:357-379` YA acepta `site_presence_report: Optional[Dict[str, Any]] = None`
- `coherence_validator.py:420-424` YA tiene el boost: `if site_whatsapp_exists: confidence_score = max(confidence_score, 0.95)`
- PERO 3 call sites NO pasan `site_presence_report`:
  - `main.py:2395-2402` — validación pre-assets
  - `v4_asset_orchestrator.py:282-285` — validación pre-generación
  - `v4_asset_orchestrator.py:419-423` — validación post-generación
- `SitePresenceChecker` produce dataclass `SitePresenceReport` (con `.results` dict), pero `CoherenceValidator` espera `Dict[str, Any]` con acceso `.get("whatsapp_button", {})`
- SitePresence se calcula/reconstruye 4+ veces en el pipeline — hallazgo DT4-N2

## Objetivo

1. Diseñar una estructura canónica serializable para SitePresence
2. Crear un adaptador único dataclass↔dict↔enum
3. Calcular SitePresence UNA sola vez por ejecución y propagar el snapshot
4. Eliminar reconstrucciones fake y rechecks redundantes

## Tareas

### T1: Diseñar estructura canónica + adapter

- **Archivo NUEVO recomendado**: `modules/asset_generation/site_presence_adapter.py`
  O alternativamente agregar método a `SitePresenceReport`.

- **Estructura canónica** (dict):
  ```python
  {
      "site_url": "https://zione.co/",
      "checked_at": "2026-07-27T14:04:48",
      "results": {
          "whatsapp_button": {
              "status": "exists",        # "exists" | "not_found" | "error" | "not_checked"
              "site_verified": True,
              "confidence": 1.0
          },
          # ... otros assets
      }
  }
  ```

- **Adapter** (`normalize_site_presence`):
  ```python
  def normalize_site_presence(report) -> dict:
      """
      Acepta: SitePresenceReport | dict | None
      Retorna: dict canónico (estructura de arriba)
      """
      if report is None:
          return {"results": {}}
      if isinstance(report, dict):
          # Ya es dict — verificar que tenga 'results', si no, puede ser output de asdict()
          if "results" in report:
              return report
          # Podría ser el dict de asdict(SitePresenceReport) que tiene results como subcampo
          # Normalizar status enum → string si es necesario
          return _normalize_dict(report)
      if hasattr(report, 'results'):
          # Es SitePresenceReport dataclass
          return _from_dataclass(report)
      raise TypeError(f"Unsupported type: {type(report)}")
  ```

- **Verificación**: El adapter debe manejar:
  - `SitePresenceReport` dataclass (con `.results[asset_type].status` como enum)
  - `dataclasses.asdict(SitePresenceReport)` → dict con `results` conteniendo enum values
  - `None` → dict vacío con `results: {}`

### T2: Computar SitePresence una vez, propagar snapshot, eliminar redundancias ⚠️ EJECUTAR ANTES DE T3

> **⚠️ ORDEN CRÍTICO**: T2 debe ejecutarse ANTES de T3. El cómputo de `site_presence_snapshot` debe existir antes de que T3 intente pasarlo a los 3 call sites de CoherenceValidator. Si se ejecuta T3 primero, los call sites recibirán `None` porque la variable aún no existe.

- **Archivo**: `main.py`
  - Mover la llamada a `SitePresenceChecker` (~L2673-2680) a ANTES del flujo de diagnóstico/propuesta, específicamente ANTES de L2395 donde se llama a `coherence_validator.validate()`.
  - Guardar el resultado normalizado en una variable `site_presence_snapshot`
  - El `site_presence_snapshot` debe estar disponible para TODOS los consumidores: CoherenceValidator pre (L2395), orchestrator, CoherenceValidator post, y el builder (L2768)

- **Archivo**: `modules/asset_generation/v4_asset_orchestrator.py`
  - Aceptar `site_presence_report` como parámetro en el constructor o en `generate_assets()`
  - Pasarlo a `ConditionalGenerator` si es necesario
  - NO re-ejecutar `SitePresenceChecker` internamente

- **Archivo**: `modules/quality_gates/publication_gates.py`
  - **L861-890**: Eliminar reconstrucción fake de `SitePresenceReport` desde `skipped_assets`
  - **L895-919**: Eliminar re-ejecución de `SitePresenceChecker` si el reporte no existe
  - En su lugar: recibir `site_presence_report` normalizado desde el assessment
  - `AssessmentPayload` ya tiene el campo `site_presence_report` en L82-83

- **Verificación**: `grep -rn "SitePresenceChecker" main.py modules/` debe mostrar ≤2 ocurrencias (1 en main.py, 1 en import)

### T3: Wire site_presence_report a 3 call sites de CoherenceValidator ⚠️ DEPENDE DE T2

> **⚠️ PRECONDICIÓN**: T2 debe estar completado. `site_presence_snapshot` debe existir en `main.py` antes de L2395.

- **`main.py:2395-2402`** — validación pre-assets:
  - Pasar `site_presence_report=normalize_site_presence(site_presence_snapshot)` a `coherence_validator.validate()`
  - La variable `site_presence_snapshot` ya fue computada en T2

- **`v4_asset_orchestrator.py:283-285`** — validación pre-generación:
  - El orchestrator recibe `site_presence_report` (inyectado en T2)
  - Normalizar y pasar a `self.coherence_validator.validate(site_presence_report=...)`

- **`v4_asset_orchestrator.py:419-423`** — validación post-generación:
  - Usar el mismo snapshot normalizado
  - Pasar `site_presence_report=...` (mismo snapshot)

- **Actualizar docstring**: `CoherenceValidator.validate()` L136-147 no documenta el parámetro `site_presence_report`. Agregar al docstring.

### T4: Tests — 5 escenarios de cobertura

- **Archivo**: `tests/asset_generation/test_site_presence_adapter.py` (nuevo)
  1. `test_normalize_from_dataclass` — `SitePresenceReport` → dict canónico
  2. `test_normalize_from_asdict` — `dataclasses.asdict(report)` → dict canónico
  3. `test_normalize_from_none` — `None` → `{"results": {}}`
  4. `test_normalize_status_enum_to_string` — `PresenceStatus.EXISTS` → `"exists"`
  5. `test_whatsapp_exists_boost` — verificar que con site_presence normalizado, `_check_whatsapp_verified` recibe `site_whatsapp_exists=True`

- **Archivo**: `tests/commercial_documents/test_financial_coherence.py` (extender)
  - Agregar test que verifica `whatsapp_verified.score > 0.30` cuando `site_presence_report` tiene `whatsapp_button: exists`

## Criterios de Completitud

- [ ] Adapter `normalize_site_presence()` existe y maneja 3 tipos de input
- [ ] SitePresenceChecker se ejecuta ≤1 vez en todo el pipeline (T2 completado)
- [ ] `publication_gates.py` NO reconstruye SitePresence fake ni re-ejecuta checker (T2 completado)
- [ ] `site_presence_snapshot` computado antes de L2395 en `main.py` (T2 completado)
- [ ] 3 call sites de CoherenceValidator reciben `site_presence_report` normalizado (T3 completado)
- [ ] Docstring de `CoherenceValidator.validate()` actualizado con parámetro `site_presence_report`
- [ ] 5+ tests nuevos pasan
- [ ] Tests existentes no rompen: `./venv/Scripts/python.exe -m pytest tests/commercial_documents/ tests/asset_generation/ tests/quality_gates/test_gate_presence.py -q`
- [ ] `log_phase_completion.py` ejecutado

## Restricciones

- **NO modificar `_check_whatsapp_verified()`** — el boost ya funciona
- **NO modificar la firma de `validate()` a menos que sea estrictamente necesario** — agregar `site_presence_report` como keyword argument con default `None`
- **NO eliminar `SitePresenceReport` dataclass** — otros consumidores pueden depender de ella
- **NO ejecutar v4complete**
- Máximo 60 iteraciones
- Si se alcanza el límite: marcar INCOMPLETA, documentar checkpoint, guardar evidencia

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-2 \
    --desc "DT4-R2-SITE-PRESENCE: canonical SitePresence adapter + wiring to 3 CoherenceValidator call sites + single computation" \
    --archivos-nuevos "modules/asset_generation/site_presence_adapter.py,tests/asset_generation/test_site_presence_adapter.py" \
    --archivos-mod "modules/commercial_documents/coherence_validator.py,modules/asset_generation/v4_asset_orchestrator.py,modules/quality_gates/publication_gates.py,main.py,modules/assessment_builder.py" \
    --tests "5" \
    --check-manual-docs
```

## Próxima Sesión

FASE-3: DT4-N4-COHERENCE — Unify coherence score source (requiere SitePresence propagado de FASE-2)
