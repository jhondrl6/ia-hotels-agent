# FASE-2: Proposal + Template Honesty — Fix has_onboarding, Disclaimer Condicional, precision_tier

> **REGLA**: Una fase = una sesion. No ejecutar multiples fases aqui.
> **Tipo de ejecucion**: DIRECTA (WSL import cascade impide delegate_task)
> **Complejidad**: MEDIA
> **Depende de**: FASE-1 completada (B_PLUS enum + disclaimer honesto + consumers downstream limpios)
> **Auditoria 2026-07-31**: Ampliada con T0 para corregir NP5 (fallback silencioso `getattr(pricing_result, 'is_onboarding', False)`).

## Contexto previo

FASE-1 (completada): EvidenceTier ahora incluye B_PLUS. `_determine_evidence_tier()` ya consulta `ga4_enabled`/`gsc_enabled`. Sin GA4+GSC → max B+. Consumers downstream (hook_pdf_generator, publication_gates, v4_diagnostic_generator default) limpios.

**Estado post-FASE-1**: El diagnostic ya es honesto. Pero la propuesta comercial tiene bugs independientes que deben corregirse.

**Bug NP5 detectado**: `v4_proposal_generator.py:586` tiene `has_onboarding = getattr(pricing_result, 'is_onboarding', False)` — fallback silencioso a False porque `PricingResolutionResult` NO tiene atributo `is_onboarding`. El plan original sugería pasar `has_onboarding` desde main.py, pero el generador YA calcula `has_onboarding` internamente con un fallback roto. Hay que elegir: o eliminar el cálculo interno y depender 100% del param, o arreglar el wiring. Recomendado: eliminar el cálculo interno.

## Objetivo de esta fase

Eliminar 3 fuentes de falsedad en la propuesta comercial, exponer `precision_tier` en el diagnostic, y arreglar el wiring roto de `has_onboarding` (NP5).

### Tareas

#### Pre-requisito (T0): Eliminar fallback silencioso de has_onboarding (NP5)

- [ ] **T0.1 — NP5**: En `v4_proposal_generator.py:583-586`, eliminar el calculo interno de `has_onboarding` que depende de `getattr(pricing_result, 'is_onboarding', False)`:
  ```python
  # ANTES (lineas 583-586):
  # Check for onboarding plan in pricing_result
  has_onboarding = False
  if pricing_result is not None:
      has_onboarding = getattr(pricing_result, 'is_onboarding', False)
  
  # DESPUES: aceptar has_onboarding como parametro de generate()
  ```
- [ ] **T0.2 — NP5**: Agregar parametro `has_onboarding: bool = False` a la firma de `generate()` en `v4_proposal_generator.py:475-494`. Usar este param en lugar del calculo interno.
- [ ] **T0.3 — NP5**: En `main.py:2712-2727`, pasar `has_onboarding=onboarding_data is not None` al `proposal_gen.generate()`. **Esto es el ÚNICO punto de entrada para has_onboarding** (elimina el fallback silencioso).
- [ ] **T0.4 — NP5**: Verificar que NO se usa `pricing_result.is_onboarding` en ningun otro lugar del codebase. Si existe, deprecate con warning.

#### Tareas principales (T1-T4)

- [ ] **T1 — Fix `has_onboarding` wiring en dict de template**: Cambiar `'has_onboarding': 'False'` hardcodeado en `v4_proposal_generator.py:944` por valor dinamico desde el param `has_onboarding`:
  ```python
  # ANTES:
  'has_onboarding': 'False',  # Conservative default; caller can override with actual value
  # DESPUES:
  'has_onboarding': str(self._current_has_onboarding) if hasattr(self, '_current_has_onboarding') else 'False',
  ```
  Guardar `self._current_has_onboarding = has_onboarding` al inicio de `generate()`.

- [ ] **T2 — Disclaimer condicional en propuesta**: El disclaimer fijo "usan benchmarks regionales" (linea 119 del output) debe adaptarse al tier real. Si tier es B+, decir "Datos operativos verificados". Si tier es B, mantener mensaje actual.
  ```python
  # En v4_proposal_generator.py, donde se construye el disclaimer:
  financial_evidence_tier = getattr(financial_breakdown, 'evidence_tier', 'C') if financial_breakdown else 'C'
  if financial_evidence_tier in ('B_PLUS', 'B+'):
      disclaimer = "Datos operativos verificados. Proyecciones con supuestos conservadores."
  elif financial_evidence_tier == 'A':
      disclaimer = "Basado en Google Analytics 4 y Search Console verificados."
  else:
      disclaimer = "Estimacion basada en benchmarks regionales."
  ```

- [ ] **T3 — Fix relationship text hardcodeado**: `main.py:2099` tiene string fijo "evidence_tier B limita precision_tier a C". Cambiar por f-string que use el tier real:
  ```python
  # ANTES:
  'relationship': 'evidence_tier B limita precision_tier a C: sin GA4, los supuestos no son validados empiricamente'
  # DESPUES:
  _evidence = _breakdown_dict.get('evidence_tier', 'C')
  _precision = _precision_tier if _precision_tier else 'C'
  'relationship': f'evidence_tier {_evidence} limita precision_tier a {_precision}: sin GA4, los supuestos no son validados empiricamente'
  ```

- [ ] **T4 — Exponer `precision_tier` en diagnostic + actualizar legend**: 
  1. Agregar `${precision_tier}` al template `diagnostico_v6_template.md` cerca de `${financial_evidence_tier}` (~linea 158).
  2. Actualizar la legenda de Tiers (lineas ~161-163) para incluir B+:
  ```markdown
  > - Tier A: Basado en Google Analytics + Search Console
  > - Tier B+: Datos operativos verificados, proyecciones con supuestos conservadores
  > - Tier B: Basado en benchmarks regionales + datos web
  > - Tier C: Basado en datos limitados de su web
  ```

### Restricciones

- **EJECUTAR T0 ANTES de T1.** Sin eliminar el fallback silencioso, T1 (cambiar hardcoded 'False') no tiene efecto: el param nunca se usa porque `has_onboarding` se calcula internamente.
- **NO modificar la logica de calculo financiero.** Solo labeling y templates.
- **NO crear nuevos placeholders sin verificar que el generator los pasa.** Grepear el dict de placeholders antes de agregar `${precision_tier}` al template.
- **NO tocar `_get_adr_from_benchmarks()`** — H1-FIX ya aplicado, parcialmente obsoleto.
- **Mantener backward compat**: Si `has_onboarding` no se pasa explicitamente, el default debe ser False (conservative).
- **T0.4 verificar `pricing_result.is_onboarding` no se usa en otros lugares** — si existe, migrar al nuevo param.

### Criterios de completitud

- [ ] T0.1: Calculo interno `getattr(pricing_result, 'is_onboarding', False)` eliminado
- [ ] T0.2: `generate()` acepta `has_onboarding: bool = False` como param
- [ ] T0.3: `main.py` pasa `has_onboarding=onboarding_data is not None` a `proposal_gen.generate()`
- [ ] T0.4: NO hay otros usos de `pricing_result.is_onboarding` en el codebase
- [ ] T1: `has_onboarding` en propuesta refleja el param pasado por main.py
- [ ] T2: El disclaimer de la propuesta NO dice "benchmarks regionales" cuando el tier es B+
- [ ] T2: El disclaimer de la propuesta NO dice "Tier C" cuando los datos son de onboarding
- [ ] T3: `relationship` en `tier_explanation` usa el tier real (f-string, no hardcodeado)
- [ ] T4: `${precision_tier}` aparece en el template del diagnostic
- [ ] T4: La legenda de Tiers en el template incluye B+
- [ ] Los tests existentes siguen pasando

### Detalle de cambios

**T0.2 — Firma de generate() con nuevo param (v4_proposal_generator.py:475-494)**:
```python
def generate(
    self,
    diagnostic_summary: DiagnosticSummary,
    financial_scenarios: FinancialScenarios,
    asset_plan: List[AssetSpec],
    hotel_name: str,
    output_dir: str,
    price_monthly: Optional[int] = None,
    setup_fee: Optional[int] = None,
    audit_result: Optional[Any] = None,
    pricing_result: Optional[PricingResolutionResult] = None,
    region: Optional[str] = None,
    analytics_data: Optional[Dict[str, Any]] = None,
    financial_breakdown: Optional[Any] = None,
    assets_generated: Optional[List[Dict[str, Any]]] = None,
    site_presence_report: Optional[Any] = None,
    pain_ledger: Optional[List[Any]] = None,
    document_audience: str = "client",
    user_provided_adr: Optional[float] = None,
    has_onboarding: bool = False,  # NUEVO FASE-2 T0 (reemplaza calculo interno)
) -> str:
    self._current_has_onboarding = has_onboarding  # Guardar para uso en dict de template
    ...
```

**T0.3 — Wire en main.py (linea ~2712-2727)**:
```python
proposal_path = proposal_gen.generate(
    diagnostic_summary=diagnostic_summary,
    financial_scenarios=financial_scenarios_obj,
    asset_plan=asset_plan,
    hotel_name=hotel_name,
    output_dir=str(output_dir),
    audit_result=audit_result,
    pricing_result=pricing_result,
    region=region,
    analytics_data=analytics_data,
    financial_breakdown=financial_breakdown,
    assets_generated=assets_for_quality,
    site_presence_report=site_presence_report,
    pain_ledger=pain_ledger_entries,
    user_provided_adr=adr_from_onboarding,
    has_onboarding=onboarding_data is not None,  # NUEVO FASE-2 T0
)
```

**T1 — Dict de template usa param (v4_proposal_generator.py:943-944)**:
```python
# ANTES:
# BUG-2-FIX: has_onboarding flag for centralized CTA conditionals in template
'has_onboarding': 'False',  # Conservative default; caller can override with actual value

# DESPUES:
# FASE-2: has_onboarding flag passed via generate() param, no fallback silencioso
'has_onboarding': str(self._current_has_onboarding),
```

### Verificacion pre-patch (ANTES de empezar)

```bash
# 1. Verificar estado actual de has_onboarding y fallback silencioso
grep -n "has_onboarding" modules/commercial_documents/v4_proposal_generator.py
grep -rn "pricing_result.is_onboarding\|getattr(pricing_result, 'is_onboarding'" --include="*.py" /mnt/c/Users/Jhond/Github/iah-cli/

# 2. Verificar donde main.py llama al proposal generator
grep -n "proposal_gen.generate\|proposal_generator.generate" main.py

# 3. Verificar el template actual de la propuesta
grep -n "has_onboarding\|benchmarks regionales\|Tier" modules/commercial_documents/templates/propuesta_v6_template.md

# 4. Verificar el template del diagnostic
grep -n "precision_tier\|evidence_tier\|Tier A\|Tier B" modules/commercial_documents/templates/diagnostico_v6_template.md

# 5. Verificar line 2099 en main.py
sed -n '2095,2110p' main.py

# 6. Verificar que onboarding_data existe en scope de main.py:2712
grep -n "onboarding_data" main.py | head -10
```

### Verificacion post-implementacion

```bash
# 1. Fallback silencioso eliminado
grep "getattr(pricing_result, 'is_onboarding'" modules/commercial_documents/v4_proposal_generator.py
# Debe retornar 0 (no debe existir)

# 2. Param has_onboarding en generate()
grep "has_onboarding: bool" modules/commercial_documents/v4_proposal_generator.py

# 3. main.py pasa has_onboarding
grep "has_onboarding=" main.py

# 4. has_onboarding ya no es hardcodeado 'False'
grep "has_onboarding.*False.*Conservative default" modules/commercial_documents/v4_proposal_generator.py
# Debe retornar 0

# 5. relationship text usa f-string
grep "evidence_tier.*limita precision_tier" main.py
# Debe mostrar f-string con tier dinamico

# 6. Template incluye precision_tier
grep "precision_tier" modules/commercial_documents/templates/diagnostico_v6_template.md

# 7. Template incluye B+ en legenda
grep "B+" modules/commercial_documents/templates/diagnostico_v6_template.md

# 8. Tests
./venv/Scripts/python.exe -m pytest tests/ -x -q 2>&1 | tail -20
```

### Proxima sesion

**FASE-3**: Quality Gate + Delivery Enrichment — Nuevo gate `CG-EVIDENCE-TIER-CONSISTENCY` (con params per-hotel, NO env vars globales — NP7). MANIFEST enriquecido en `modules/delivery/delivery_packager.py:145` (NO main.py:3038 — NP6).
