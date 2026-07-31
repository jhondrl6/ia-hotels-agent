# FASE-3: Quality Gate (per-hotel) + Delivery Enrichment — CG-EVIDENCE-TIER-CONSISTENCY

> **REGLA**: Una fase = una sesion. No ejecutar multiples fases aqui.
> **Tipo de ejecucion**: DIRECTA (WSL import cascade impide delegate_task)
> **Complejidad**: MEDIA
> **Depende de**: FASE-2 completada (tier honesto + disclaimer condicional + has_onboarding wiring arreglado)
> **Auditoria 2026-07-31**: Redisenado para corregir NP6 (MANIFEST en `delivery_packager.py`, NO main.py) y NP7 (gate con params per-hotel, NO `os.getenv`).

## Contexto previo

FASE-1 (completada): Evidence tier ahora es honesto. Sin GA4+GSC → max B+. B_PLUS existe. Consumers downstream limpios.
FASE-2 (completada): Propuesta no miente sobre tiers. `has_onboarding` dinamico (sin fallback silencioso). `precision_tier` visible.

Sin embargo, **no existe un gate que bloquee la entrega** si por alguna razon el tier es A pero GA4/GSC no estan configurados. El gate existente `CG-TIER-CONSISTENCY` (commercial_gate.py:601-639) solo compara frontmatter vs texto — no verifica conectividad GA4/GSC.

**Correccion arquitectonica importante (NP7)**: El sistema actual usa `ga4_property_id` PER-HOTEL via CLI flag (`main.py:2304`), NO env vars globales. El gate debe recibir los flags per-hotel como parametros, NO leer `os.getenv('GA4_PROPERTY_ID')`. El diseño del plan original era global — eso no respeta la arquitectura real.

**Correccion de ubicacion (NP6)**: El MANIFEST se genera en `modules/delivery/delivery_packager.py:145`, NO en `main.py:3038` como decia el plan original. El enrichment debe hacerse en el package method, no en main.py.

## Objetivo de esta fase

Crear un gate de coherencia interna que detecte "Tier A + GA4 no configurado" y **bloquee la entrega**. Enriquecer el MANIFEST.json con metadatos de calidad para trazabilidad post-mortem.

### Tareas

- [ ] **T1 — Nuevo gate `CG-EVIDENCE-TIER-CONSISTENCY` (PER-HOTEL)**: Agregar metodo `_check_evidence_tier_consistency()` en `commercial_gate.py` que:
  1. Recibe `financial_json: Optional[Dict[str, Any]]`, `ga4_available: bool`, `gsc_available: bool` como parametros (NO `os.getenv`)
  2. Extraiga `evidence_tier` del financial_json
  3. Si `evidence_tier == "A"` Y (`!ga4_available` O `!gsc_available`) → **BLOCKING**
  4. Mensaje: "El documento afirma Tier A (GA4+GSC verificados) pero GA4/GSC no estan disponibles para este hotel."
  
  ```python
  # Agregar a BLOCKING_GATE_IDS (linea ~69):
  BLOCKING_GATE_IDS = [
      "CG-SCENARIO-ORDER",
      "CG-SCENARIO-NEGATIVE",
      "CG-IA-BLOCKED-CLAIM",
      "CG-ROI-NEGATIVE",
      "CG-CLAIM-VS-EVIDENCE",
      "CG-EVIDENCE-TIER-CONSISTENCY",  # NUEVO FASE-3
  ]
  
  # Nuevo metodo en CommercialGateValidator:
  def _check_evidence_tier_consistency(
      self,
      financial_json: Optional[Dict[str, Any]],
      ga4_available: bool = False,
      gsc_available: bool = False,
  ) -> CommercialGateResult:
      """CG-EVIDENCE-TIER-CONSISTENCY: Tier A sin GA4/GSC reales (per-hotel)."""
      if financial_json is None:
          return CommercialGateResult(
              gate_id="CG-EVIDENCE-TIER-CONSISTENCY",
              name="Evidencia Tier vs GA4/GSC",
              passed=True,
              severity="INFO",
              message="Sin datos financieros para verificar.",
              suggestion="",
          )
      
      breakdown = financial_json.get('breakdown', {})
      evidence_tier = breakdown.get('evidence_tier', 'C')
      
      # Solo aplica a Tier A (los demas tiers no requieren GA4/GSC)
      if evidence_tier != 'A':
          return CommercialGateResult(
              gate_id="CG-EVIDENCE-TIER-CONSISTENCY",
              name="Evidencia Tier vs GA4/GSC",
              passed=True,
              severity="INFO",
              message=f"Tier {evidence_tier} no requiere verificacion GA4/GSC.",
              suggestion="",
          )
      
      # Verificar conectividad real (PER-HOTEL via params, NO os.getenv)
      if ga4_available and gsc_available:
          return CommercialGateResult(
              gate_id="CG-EVIDENCE-TIER-CONSISTENCY",
              name="Evidencia Tier vs GA4/GSC",
              passed=True,
              severity="INFO",
              message="Tier A verificado: GA4 y GSC disponibles para este hotel.",
              suggestion="",
          )
      
      missing = []
      if not ga4_available:
          missing.append("GA4")
      if not gsc_available:
          missing.append("GSC")
      
      return CommercialGateResult(
          gate_id="CG-EVIDENCE-TIER-CONSISTENCY",
          name="Evidencia Tier vs GA4/GSC",
          passed=False,
          severity="BLOCKING",
          message=f"CONTRADICCION: El documento afirma Tier A (GA4+GSC verificados) "
                  f"pero {', '.join(missing)} no esta(n) disponible(s) para este hotel.",
          suggestion="Reducir evidence_tier a B+ o configurar GA4/GSC para este hotel.",
      )
  ```
  
  **IMPORTANTE**: Este cambio de firma (agregar params per-hotel) requiere actualizar el caller en `validate_diagnostic()`. El caller debe pasar `ga4_available` y `gsc_available` desde main.py (NO leer env vars).

- [ ] **T2 — Integrar en delivery_quality.py**: Agregar `CG-EVIDENCE-TIER-CONSISTENCY` al checklist de gates pre-delivery. El `validate_proposal()` y/o `validate_diagnostic()` ahora reciben `ga4_available`/`gsc_available` desde main.py.

- [ ] **T3 — Enriquecer MANIFEST.json en delivery_packager.py**: Modificar `modules/delivery/delivery_packager.py` (NO main.py) para agregar bloque `quality_metadata` al MANIFEST:
  ```python
  # En delivery_packager.py, despues de construir el manifest (linea ~179):
  manifest = self.create_manifest(hotel_id, files_for_manifest)
  
  # NUEVO FASE-3 T3: quality_metadata
  manifest["quality_metadata"] = {
      "evidence_tier": getattr(self, '_current_evidence_tier', 'C'),
      "precision_tier": getattr(self, '_current_precision_tier', 'C'),
      "ga4_configured": getattr(self, '_current_ga4_available', False),
      "gsc_configured": getattr(self, '_current_gsc_available', False),
      "onboarding_used": getattr(self, '_current_onboarding_used', False),
      "coherence_score": getattr(self, '_current_coherence_score', None),
      "contradictions_detected": getattr(self, '_current_contradictions', []),
  }
  
  with open(manifest_path, 'w', encoding='utf-8') as f:
      json.dump(manifest, f, indent=2, ensure_ascii=False)
  ```
  
  **Cambio de signature**: `package()` debe aceptar params `evidence_tier`, `precision_tier`, `ga4_available`, `gsc_available`, `onboarding_used`, `coherence_score`, `contradictions` (o usar atributos internos seteados desde main.py antes de llamar a package).

### Restricciones

- **NO modificar el gate `CG-TIER-CONSISTENCY` existente.** Sigue en WARNING para su proposito original (comparar frontmatter vs texto).
- **El nuevo gate debe ser BLOCKING** (agregar a `BLOCKING_GATE_IDS` en commercial_gate.py).
- **NO hardcodear credenciales globales.** Recibir `ga4_available`/`gsc_available` como parametros per-hotel (NP7 — corregir diseño original que usaba `os.getenv`).
- **El gate debe ser tolerante a ausencia de datos**: si no puede verificar (params no pasados), debe hacer fallback conservador (passed=True, severity=INFO).
- **MANIFEST.json debe mantener backward compat**: agregar `quality_metadata` como bloque opcional. NO remover campos existentes.
- **El caller en main.py debe pasar los flags reales**: `ga4_available` se calcula en main.py:2306 (`ga4_client.is_available()`). NO leer de env vars.

### Criterios de completitud

- [ ] T1: `CG-EVIDENCE-TIER-CONSISTENCY` existe en `commercial_gate.py` con firma per-hotel (`ga4_available`, `gsc_available` como params)
- [ ] T1: El gate esta en `BLOCKING_GATE_IDS` (no en WARNING)
- [ ] T1: NO usa `os.getenv` en el codigo del gate
- [ ] T1: Si `evidence_tier == "A"` y `!ga4_available` → `passed=False, severity=BLOCKING`
- [ ] T1: Si `evidence_tier == "B+"` o `"B"` o `"C"` → `passed=True`
- [ ] T2: `delivery_quality.py` incluye el gate en su checklist pre-delivery
- [ ] T2: El caller en main.py pasa `ga4_available` y `gsc_available` reales al gate
- [ ] T3: MANIFEST.json incluye bloque `quality_metadata`
- [ ] T3: El enrichment se hace en `modules/delivery/delivery_packager.py` (NO main.py)
- [ ] T3: `delivery_packager.package()` acepta los nuevos params (o atributos internos)
- [ ] Los tests existentes siguen pasando
- [ ] Las pruebas manuales confirman que Tier A + !GA4 → BLOCKING

### Detalle de cambios en el caller (main.py)

El caller de `validate_diagnostic()` / `validate_proposal()` debe pasar los flags per-hotel:

```python
# En main.py, donde se invoca el validator (buscar con grep):
validator = CommercialGateValidator()
report = validator.validate_diagnostic(
    diagnostic_text=doc,
    scenarios=scenarios,
    ai_crawlers_data=audit_result.ai_crawlers,
    place_found=audit_result.gbp_place_found,
    gbp_rating=audit_result.gbp_rating,
    # NUEVO FASE-3 T1 — per-hotel flags
    ga4_available=ga4_available,  # ya calculado en main.py:2306
    gsc_available=gsc_available,  # similar a ga4_available
)
```

Y donde se llama a `delivery_packager.package()`:

```python
# En main.py (~linea 3048):
delivery_zip_path = packager.package(
    hotel_id=hotel_id,
    # ... existing args ...
    # NUEVO FASE-3 T3 — quality metadata
    evidence_tier=_breakdown_dict.get('evidence_tier', 'C'),
    precision_tier=_precision_tier,
    ga4_available=ga4_available,
    gsc_available=gsc_available,
    onboarding_used=onboarding_data is not None,
    coherence_score=coherence_score,
    contradictions=contradictions,
)
```

**Alternativa si cambiar signature es problematico**: Setear atributos en `packager` antes de llamar:
```python
packager._current_evidence_tier = ...
packager._current_ga4_available = ga4_available
# ... luego llamar package() sin los nuevos params
delivery_zip_path = packager.package(hotel_id=hotel_id, ...)
```

### Verificacion pre-patch

```bash
# 1. Verificar BLOCKING_GATE_IDS actual
grep -A10 "BLOCKING_GATE_IDS" modules/quality_gates/commercial_gate.py

# 2. Verificar donde se construye el MANIFEST (CORREGIDO NP6)
grep -n "MANIFEST\|manifest" modules/delivery/delivery_packager.py
grep -n "package(" modules/delivery/delivery_packager.py

# 3. Verificar donde se invoca el CommercialGateValidator
grep -n "validate_diagnostic\|validate_proposal" main.py
grep -n "validate_diagnostic\|validate_proposal" modules/quality_gates/delivery_quality.py

# 4. Verificar delivery_quality.py estructura
grep -n "def\|gate" modules/quality_gates/delivery_quality.py | head -30

# 5. Verificar que ga4_available y gsc_available existen en scope de main.py
grep -n "ga4_available\|gsc_available" main.py | head -10

# 6. Buscar usos de os.getenv para GA4/GSC (NP7 — debe retornar pocos resultados)
grep -rn "os.getenv.*GA4\|os.getenv.*GSC" --include="*.py" /mnt/c/Users/Jhond/Github/iah-cli/ | grep -v ".venv"
```

### Verificacion post-implementacion

```bash
# 1. Nuevo gate en BLOCKING_GATE_IDS
grep "CG-EVIDENCE-TIER-CONSISTENCY" modules/quality_gates/commercial_gate.py
grep -A12 "BLOCKING_GATE_IDS" modules/quality_gates/commercial_gate.py | grep "EVIDENCE"

# 2. Gate NO usa os.getenv (NP7 verificado)
grep "os.getenv.*GA4\|os.getenv.*GSC" modules/quality_gates/commercial_gate.py
# Debe retornar 0

# 3. Gate recibe params per-hotel (NP7 verificado)
grep "def _check_evidence_tier_consistency" modules/quality_gates/commercial_gate.py
grep "ga4_available.*bool\|gsc_available.*bool" modules/quality_gates/commercial_gate.py

# 4. MANIFEST incluye quality_metadata (CORREGIDO NP6)
grep "quality_metadata" modules/delivery/delivery_packager.py
grep "quality_metadata" main.py
# El primero debe retornar 1 (definicion), el segundo debe retornar 0 (NO en main.py)

# 5. delivery_quality incluye el gate
grep "CG-EVIDENCE-TIER-CONSISTENCY" modules/quality_gates/delivery_quality.py

# 6. Caller en main.py pasa flags per-hotel
grep "ga4_available=" main.py
grep "gsc_available=" main.py

# 7. Tests
./venv/Scripts/python.exe -m pytest tests/ -x -q 2>&1 | tail -20
```

### Proxima sesion

**FASE-4**: Tests — Unit tests para `_determine_evidence_tier`, integration test para tier piping, gate test para `CG-EVIDENCE-TIER-CONSISTENCY` (con mocks de `ga4_available`/`gsc_available`), regression suite. **ADEMAS**: actualizar tests pre-existentes que rompen con B_PLUS (NP3 — `test_financial_breakdown.py`).
