# FASE-1: Root Cause — Evidence Tier Honesto + B_PLUS + Downstream Consumers Limpios

> **REGLA**: Una fase = una sesion. No ejecutar multiples fases aqui.
> **Tipo de ejecucion**: DIRECTA (WSL import cascade impide delegate_task)
> **Complejidad**: ALTA ⚠️ (mayor complejidad tecnica del plan)
> **Auditoria 2026-07-31**: Ampliada con T0/T0b para corregir NP1-NP4 (consumers downstream). Sin esto, B_PLUS causa regression silenciosa en PDFs y publication gates.

## Contexto previo

Plan `EVIDENCE-TIER-FALSE-CONFIDENCE-IAO-2026-07-31`. Version actual v4.67.0.

El documento v4complete 07-30 para Zi One Luxury tiene una contradiccion interna:
- Linea 84 (CTA): "conecte GA4 y Search Console" (honesto: sabe que GA4 no esta conectado)
- Linea 215 (disclaimer): "Basado en Google Analytics y Search Console verificados" (falso: GA4 no esta conectado)
- Linea 276 (Fuentes): "GA4: No configurado" (confirma la falsedad)

**Causa raiz**: `_determine_evidence_tier()` en `scenario_calculator.py:480-504` asigna Tier A basado en >=2 fuentes de datos operativos verificados. **NUNCA verifica si GA4 o GSC estan realmente conectados.**

## Objetivo de esta fase

Hacer que `_determine_evidence_tier()` consulte `ga4_enabled`/`gsc_enabled` como fuente de verdad. Sin GA4+GSC conectados, NUNCA devolver Tier A. Introducir nuevo tier `B_PLUS` para onboarding verificado sin GA4.

**CRITICO**: Antes de introducir `B_PLUS`, limpiar los consumers downstream (T0/T0b) que actualmente asumen solo A/B/C. Sin esto, los PDFs y publication gates rompen silenciosamente.

### Tareas

#### Pre-requisito (T0): Limpiar consumers downstream (NP1, NP2, NP4)

- [ ] **T0.1 — NP1**: Actualizar `modules/commercial_documents/hook_pdf_generator.py:509`:
  ```python
  # ANTES:
  valid_tiers = {"A", "B", "C"}
  # DESPUES:
  valid_tiers = {"A", "B+", "B", "C"}
  ```
  Sin esto, B_PLUS sera rechazado y forzado a B con WARN. El deliverable principal (PDF) degradara el tier honesto.

- [ ] **T0.2 — NP2**: Refactorizar `modules/quality_gates/publication_gates.py:399`:
  ```python
  # ANTES (roto):
  tier_message = f"Tier {formal_tier} evidence" if formal_tier == "C" else "Tier C evidence"
  # DESPUES (dinamico):
  tier_message = f"Tier {formal_tier} evidence"  # ya es dinamico — quitar el condicional
  ```
  El condicional `if formal_tier == "C" else "Tier C evidence"` es bug: si tier es "A", "B", o "B+", siempre dice "Tier C evidence". Remover la condicion falsa.

- [ ] **T0.3 — NP4**: Cambiar default en `modules/commercial_documents/v4_diagnostic_generator.py:1043`:
  ```python
  # ANTES:
  def _build_financial_placeholders(
      self,
      ...
      evidence_tier: str = "A",  # BUG: default optimista cuando deberia ser conservador
  )
  # DESPUES:
  evidence_tier: str = "C",  # Conservador: sin evidencia asuma C, no A
  ```
  Sin este fix, el bug que estamos corrigiendo se reproduce en el path "no financial_breakdown".

#### Pre-requisito (T0b): Actualizar tests pre-existentes (NP3)

- [ ] **T0b.1 — NP3**: Extender `tests/test_financial_breakdown.py:107-116`:
  ```python
  # Agregar assertions para B_PLUS:
  assert "operativos" in EvidenceTier.B_PLUS.disclaimer or "onboarding" in EvidenceTier.B_PLUS.disclaimer
  assert EvidenceTier.B_PLUS.value == "B+"
  ```
  Tambien extender `test_evidence_tier_values()` para incluir B_PLUS.

#### Tareas principales (T1-T4)

- [ ] **T1**: Agregar `B_PLUS = "B+"` al enum `EvidenceTier` en `data_structures.py:126-139`. Agregar disclaimer honesto para B+ (ver §8 del contexto).
- [ ] **T2**: Agregar campos `ga4_enabled: bool = False` y `gsc_enabled: bool = False` al dataclass `HotelFinancialData` en `scenario_calculator.py`.
- [ ] **T3**: Refactorizar `_determine_evidence_tier()` para recibir y usar `ga4_enabled`/`gsc_enabled`. Sin GA4+GSC → max B+. Actualizar `calculate_breakdown()` para pasar estos flags desde `hotel_data`.
- [ ] **T4**: En `main.py`, construir `HotelFinancialData` pasando `ga4_enabled=ga4_available`, `gsc_enabled=gsc_available` (usando los flags ya calculados en main.py:2306).

### Restricciones

- **EJECUTAR T0/T0b ANTES de T1-T4.** Sin limpieza de consumers downstream, B_PLUS introduce regression silenciosa.
- **NO modificar `_determine_evidence_tier()` sin antes grepear TODOS sus callers.** La firma cambia → todos deben actualizarse.
- **NO modificar formulas financieras.** Los valores son correctos. El bug es de labeling.
- **NO tocar `ia_readiness_calculator.py`.** Ya acepta `ga4_indirect_score` como param opcional.
- **NO usar delegate_task.** WSL import cascade: subagent en Linux no puede importar modulos del venv Windows.
- **Preservar Tier A real**: Hoteles con GA4+GSC conectados DEBEN seguir recibiendo Tier A.
- **B_PLUS debe propagarse**: Grepear `EvidenceTier` en todo el codebase para asegurar que el nuevo valor no rompe ningun consumer.

### Criterios de completitud

- [ ] T0.1: `valid_tiers = {"A", "B+", "B", "C"}` en `hook_pdf_generator.py:509`
- [ ] T0.2: `tier_message` en `publication_gates.py:399` es dinamico (sin condicional falso)
- [ ] T0.3: `evidence_tier: str = "C"` default en `v4_diagnostic_generator.py:1043`
- [ ] T0b.1: `test_financial_breakdown.py` incluye assertions para `EvidenceTier.B_PLUS`
- [ ] T1: `EvidenceTier.B_PLUS` existe con `value = "B+"` y disclaimer honesto
- [ ] T2: `HotelFinancialData` tiene campos `ga4_enabled` y `gsc_enabled`
- [ ] T3: `_determine_evidence_tier()` con `ga4_enabled=False` NUNCA devuelve `EvidenceTier.A`
- [ ] T3: `_determine_evidence_tier()` con `ga4_enabled=True AND gsc_enabled=True` + >=2 fuentes verificadas → `EvidenceTier.A`
- [ ] T3: `_determine_evidence_tier()` con onboarding pero sin GA4 → `EvidenceTier.B_PLUS`
- [ ] T4: `main.py` pasa `ga4_available` y `gsc_available` a `HotelFinancialData`
- [ ] Grep de `EvidenceTier` en todo el codebase no revela consumers rotos por el nuevo valor B_PLUS
- [ ] Tests existentes (incluyendo test_financial_breakdown.py actualizado) siguen pasando

### Secuencia de implementacion (orden critico)

```
Pre-requisito:
1. T0.1: hook_pdf_generator.py — valid_tiers incluye B+
2. T0.2: publication_gates.py — tier_message dinamico
3. T0.3: v4_diagnostic_generator.py — default evidence_tier "C"
4. T0b.1: test_financial_breakdown.py — assertions para B_PLUS

Despues de T0/T0b:
5. data_structures.py: Agregar B_PLUS al enum + disclaimer
6. scenario_calculator.py: Agregar ga4_enabled/gsc_enabled a HotelFinancialData
7. scenario_calculator.py: Refactorizar _determine_evidence_tier() + calculate_breakdown()
8. main.py: Pasar ga4_enabled/gsc_enabled a HotelFinancialData
```

### Codigo de referencia

**Nuevo EvidenceTier (data_structures.py:126-139)**:
```python
class EvidenceTier(Enum):
    """Clasificacion de calidad de evidencia financiera."""
    A = "A"      # GA4 + GSC conectados — datos verificables
    B_PLUS = "B+"  # NUEVO: onboarding verificado sin GA4/GSC
    B = "B"      # Benchmarks regionales + scraping — estimado con base
    C = "C"      # Solo scraping basico — estimado con baja confianza

    @property
    def disclaimer(self) -> str:
        if self == EvidenceTier.A:
            return "Basado en datos de Google Analytics y Search Console verificados."
        elif self == EvidenceTier.B_PLUS:  # NUEVO
            return ("Datos operativos verificados de su hotel (habitaciones, ADR, ocupacion, "
                    "canal directo). Las proyecciones usan supuestos conservadores "
                    "(shift 10%, IA boost 5%) no validados con trafico real. "
                    "Conecte Google Analytics 4 y Search Console para cifras exactas al peso.")
        elif self == EvidenceTier.B:
            return "Estimacion basada en benchmarks regionales y datos de su web. Para mayor precision, conecte Google Analytics 4."
        else:
            return "Estimacion basada en datos limitados de su web. Conecte Google Analytics 4 para un diagnostico mas preciso."
```

**Nuevo _determine_evidence_tier (scenario_calculator.py:480-504)**:
```python
def _determine_evidence_tier(self, hotel_data: HotelFinancialData) -> EvidenceTier:
    """Determina tier basado en disponibilidad de datos.
    
    FASE-1: Sin GA4+GSC conectados, NUNCA devuelve A.
    """
    sources = self._trace_data_sources(hotel_data)
    adr_src = sources.get('adr', '')
    occ_src = sources.get('occupancy', '')
    ch_src = sources.get('direct_channel', '')
    
    # Flags GA4/GSC (NUEVO en FASE-1)
    ga4_enabled = getattr(hotel_data, 'ga4_enabled', False)
    gsc_enabled = getattr(hotel_data, 'gsc_enabled', False)
    
    # Fuentes verificadas (onboarding/user_provided)
    has_verified_data = any(s in ('onboarding', 'user_provided')
                            for s in [adr_src, ch_src])
    low_quality = [s for s in [adr_src, occ_src, ch_src]
                   if s in ('scraping', 'default', 'unknown', 'legacy_hardcode')]
    
    # GA4+GSC real → A (con datos verificados)
    if ga4_enabled and gsc_enabled and has_verified_data:
        return EvidenceTier.A
    
    # Onboarding verificado sin GA4 → B+ (NUEVO)
    if has_verified_data and not (ga4_enabled and gsc_enabled):
        return EvidenceTier.B_PLUS
    
    # Baja calidad → C
    if len(low_quality) >= 2:
        return EvidenceTier.C
    
    # Default → B
    return EvidenceTier.B
```

**Nuevo HotelFinancialData (scenario_calculator.py:77-102)**:
```python
@dataclass
class HotelFinancialData:
    rooms: int
    adr_cop: float
    occupancy_rate: float
    ota_commission_rate: float = 0.15
    direct_channel_percentage: float = 0.0
    ota_presence: List[str] = field(default_factory=lambda: ["booking", "expedia"])
    # Trazabilidad
    adr_source: str = "unknown"
    occupancy_source: str = "unknown"
    channel_source: str = "unknown"
    # NUEVO FASE-1 — conectividad real GA4/GSC
    ga4_enabled: bool = False
    gsc_enabled: bool = False
```

### Verificacion pre-patch (ANTES de empezar)

```bash
# 1. Consumers actuales de EvidenceTier (baseline)
grep -rn "EvidenceTier\." --include="*.py" /mnt/c/Users/Jhond/Github/iah-cli/ | grep -v ".venv"

# 2. Baseline tests (debe pasar ANTES del patch)
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/test_financial_breakdown.py -v
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_fase_f_financial_placeholders.py -v

# 3. Verificar lineas exactas de los consumers downstream a limpiar
grep -n "valid_tiers" modules/commercial_documents/hook_pdf_generator.py
grep -n "tier_message" modules/quality_gates/publication_gates.py
grep -n "evidence_tier: str =" modules/commercial_documents/v4_diagnostic_generator.py

# 4. Verificar que main.py tiene ga4_available ya calculado
grep -n "ga4_available\|ga4_hotel_property_id" main.py
```

### Verificacion post-implementacion

```bash
# 1. B_PLUS existe en enum
grep -n "B_PLUS" modules/commercial_documents/data_structures.py

# 2. HotelFinancialData tiene ga4_enabled/gsc_enabled
grep -n "ga4_enabled\|gsc_enabled" modules/financial_engine/scenario_calculator.py

# 3. main.py pasa flags
grep -n "ga4_enabled=" main.py

# 4. Consumers downstream limpios (NP1-NP4)
grep "valid_tiers" modules/commercial_documents/hook_pdf_generator.py
grep "tier_message" modules/quality_gates/publication_gates.py
grep "evidence_tier: str =" modules/commercial_documents/v4_diagnostic_generator.py

# 5. Tests existentes + nuevos pasan
./venv/Scripts/python.exe -m pytest tests/test_financial_breakdown.py -v
./venv/Scripts/python.exe -m pytest tests/commercial_documents/ -v

# 6. Suite de regresion
./venv/Scripts/python.exe -m pytest tests/ -x -q 2>&1 | tail -10
```

### Proxima sesion

**FASE-2**: Proposal + Template Honesty — Fix `has_onboarding` wiring (incluyendo NP5: eliminar fallback silencioso `getattr(pricing_result, 'is_onboarding', False)`), disclaimer condicional al tier, precision_tier visible, relationship text dinamico.
