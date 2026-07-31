# FASE-4: Tests — Unit + Integration + Gate + Regression + Update Existing Tests

> **REGLA**: Una fase = una sesion. No ejecutar multiples fases aqui.
> **Tipo de ejecucion**: DIRECTA (WSL import cascade impide delegate_task)
> **Complejidad**: MEDIA
> **Depende de**: FASE-3 completada (gate + MANIFEST enriquecido)
> **Auditoria 2026-07-31**: Ampliada con T0 para corregir NP3 (tests pre-existentes que rompen con B_PLUS). FASE-1 ya actualizo `test_financial_breakdown.py` para B_PLUS, pero FASE-4 debe validar suite completa.

## Contexto previo

FASE-1 (completada): Evidence tier honesto. B_PLUS existe. `_determine_evidence_tier()` consulta GA4/GSC. Consumers downstream limpios.
FASE-2 (completada): Propuesta honesta. `has_onboarding` dinamico (sin fallback silencioso). `precision_tier` visible.
FASE-3 (completada): `CG-EVIDENCE-TIER-CONSISTENCY` recibe `ga4_available`/`gsc_available` per-hotel y bloquea delivery si Tier A + !GA4. MANIFEST enriquecido en `delivery_packager.py`.

**TODO el codigo de produccion esta implementado.** Solo faltan tests (incluyendo actualizacion de tests pre-existentes).

## Objetivo de esta fase

Crear tests unitarios, de integracion, de gate, verificar que la suite de regresion completa sigue verde, y validar que tests pre-existentes que asumen A/B/C ahora soportan B_PLUS.

### Tareas

#### Pre-requisito (T0): Validar tests pre-existentes compatibles con B_PLUS (NP3)

- [ ] **T0.1 — NP3 validation**: Ejecutar suite de tests pre-existentes que asumen A/B/C:
  ```bash
  ./venv/Scripts/python.exe -m pytest tests/test_financial_breakdown.py -v
  ./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_fase_f_financial_placeholders.py -v
  ./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_hook_pdf_generator.py -v
  ./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_proposal_generator.py -v
  ./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_template_conditionals.py -v
  ```
  Verificar que ninguno falla por la introduccion de B_PLUS. FASE-1 T0b ya actualizo `test_financial_breakdown.py`, pero estos otros tests pueden necesitar ajustes:
  - `test_fase_f_financial_placeholders.py:88-107` (default tier "C" test) — validar que sigue pasando o ajustar
  - `test_hook_pdf_generator.py:279-280` (tier invalido "X" test) — no afectado, "X" sigue invalido
  - `test_proposal_generator.py:422-475` (template data tests) — verificar que B_PLUS fluye correctamente

- [ ] **T0.2 — NP3 fixes**: Si T0.1 detecta failures, aplicar fixes minimos:
  - Para `test_fase_f_financial_placeholders.py`: ajustar assertions si la logica cambio (ej. tier default ya no es "C" sino "B+" cuando hay onboarding)
  - Para `test_proposal_generator.py`: agregar test para `has_onboarding=True` (param nuevo de FASE-2)
  - Para `test_template_conditionals.py`: verificar que `{{if financial_evidence_tier == "B+"}}` se rendere correctamente

- [ ] **T0.3 — NP3 documentation**: Documentar cualquier test pre-existente que sigue pasando pero ahora tiene semantica cambiada (ej. tier default cambio de "C" a "B+" con onboarding).

#### Tareas principales (T1-T4)

- [ ] **T1 — Unit tests para `_determine_evidence_tier()`**: Probar todas las combinaciones de tier:
  - `ga4_enabled=True + gsc_enabled=True + has_verified_data` → `EvidenceTier.A`
  - `ga4_enabled=True + gsc_enabled=False + has_verified_data` → `EvidenceTier.B_PLUS` (NUEVO)
  - `ga4_enabled=False + gsc_enabled=True + has_verified_data` → `EvidenceTier.B_PLUS` (NUEVO)
  - `ga4_enabled=False + has_verified_data` → `EvidenceTier.B_PLUS` (NUEVO)
  - `ga4_enabled=False + low_quality >= 2` → `EvidenceTier.C`
  - Default → `EvidenceTier.B`

- [ ] **T2 — Integration test para tier piping**: Verificar que el pipeline completo (onboarding → HotelFinancialData → calculate_breakdown → evidence_tier) produce B+ cuando hay onboarding pero no GA4.

- [ ] **T3 — Gate test para `CG-EVIDENCE-TIER-CONSISTENCY`**:
  - `evidence_tier="A" + ga4_available=False` → `passed=False, severity=BLOCKING` (param per-hotel, NO env var)
  - `evidence_tier="B+"` → `passed=True` (no aplica)
  - `evidence_tier="A" + ga4_available=True + gsc_available=True` → `passed=True`
  - `evidence_tier="A" + ga4_available=True + gsc_available=False` → `passed=False, severity=BLOCKING`

- [ ] **T4 — Regression**: Ejecutar suite completa de tests. Verificar que no hay regresiones. Si hay failures pre-existentes, documentarlos.

### Restricciones

- **NO usar delegate_task.** Tests necesitan el venv Windows. Subagent en WSL Linux no puede importar modulos.
- **NO modificar codigo de produccion** a menos que un test revele un bug real.
- **Usar `./venv/Scripts/python.exe -m pytest`** para ejecutar tests (venv Windows).
- **Tests deben ser independientes**: no depender de estado global ni de credenciales reales.
- **Mock `ga4_available`/`gsc_available` como parametros** para gate tests (NO monkeypatch `os.getenv`).
- **T0.1 primero**: validar tests pre-existentes ANTES de agregar tests nuevos. Si fallan, T0.2 los arregla. Sin esto, FASE-5 puede enmascarar regressions con resultados ruidosos.

### Criterios de completitud

- [ ] T0.1: 5+ tests pre-existentes ejecutados, resultados documentados
- [ ] T0.2: Tests pre-existentes que fallan por B_PLUS arreglados
- [ ] T0.3: Cambios de semantica en tests pre-existentes documentados
- [ ] T1: Al menos 6 test cases para `_determine_evidence_tier()` cubriendo todas las combinaciones
- [ ] T2: Al menos 1 integration test que verifica el pipeline completo con onboarding YAML
- [ ] T3: Al menos 4 test cases para `CG-EVIDENCE-TIER-CONSISTENCY` (cubriendo per-hotel params)
- [ ] T4: Suite de regresion completa pasa (o se documentan failures pre-existentes)
- [ ] `pytest --collect-only` muestra los nuevos tests

### Estructura de tests

```python
# tests/test_evidence_tier.py (NUEVO)

class TestDetermineEvidenceTier:
    """Tests para _determine_evidence_tier() con ga4_enabled/gsc_enabled."""
    
    def test_tier_a_with_ga4_and_gsc(self):
        """GA4+GSC conectados + has_verified_data → Tier A."""
        ...
    
    def test_tier_b_plus_with_onboarding_no_ga4(self):
        """Onboarding verificado sin GA4 → B+."""
        ...
    
    def test_tier_b_plus_with_ga4_but_no_gsc(self):
        """GA4 conectado pero GSC no → B+ (se requieren AMBOS)."""
        ...
    
    def test_tier_b_plus_with_gsc_but_no_ga4(self):
        """GSC conectado pero GA4 no → B+ (se requieren AMBOS)."""
        ...
    
    def test_tier_c_with_low_quality(self):
        """Fuentes de baja calidad → C."""
        ...
    
    def test_tier_b_default(self):
        """Caso default → B."""
        ...


class TestEvidenceTierConsistencyGate:
    """Tests para CG-EVIDENCE-TIER-CONSISTENCY (per-hotel params)."""
    
    def test_blocks_when_tier_a_without_ga4(self):
        """Tier A sin ga4_available → BLOCKING (param=False)."""
        # NO usar monkeypatch os.getenv
        # Pasar ga4_available=False, gsc_available=False directamente
        ...
    
    def test_passes_when_tier_b_plus(self):
        """Tier B+ no requiere verificacion GA4/GSC."""
        ...
    
    def test_passes_when_tier_a_with_ga4_and_gsc(self):
        """Tier A con ga4_available=True + gsc_available=True → pasa."""
        # Pasar ga4_available=True, gsc_available=True directamente
        ...
    
    def test_blocks_when_tier_a_with_only_ga4(self):
        """Tier A con solo GA4 (no GSC) → BLOCKING (se requieren AMBOS)."""
        ...


class TestEvidenceTierIntegration:
    """Integration test: pipeline completo con onboarding."""
    
    def test_onboarding_without_ga4_produces_b_plus(self):
        """v4complete con onboarding YAML pero sin GA4 → Tier B+."""
        ...
```

### Verificacion pre-patch

```bash
# 1. Baseline de tests actuales (debe pasar ANTES)
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/ --collect-only -q 2>&1 | tail -5

# 2. Verificar que modulo de tests existe
ls tests/test_evidence*.py 2>/dev/null || echo "No existe aun (esperado)"

# 3. Verificar imports necesarios
grep "from.*scenario_calculator import\|from.*commercial_gate import" tests/ --include="*.py" -l

# 4. Verificar tests pre-existentes que pueden estar afectados por B_PLUS
grep -rln "EvidenceTier\|evidence_tier" tests/ --include="*.py" | grep -v ".venv"
```

### Verificacion post-implementacion

```bash
# 1. Tests pre-existentes (T0)
./venv/Scripts/python.exe -m pytest tests/test_financial_breakdown.py -v
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_fase_f_financial_placeholders.py -v
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_hook_pdf_generator.py -v
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_proposal_generator.py -v

# 2. Nuevos tests collectados
./venv/Scripts/python.exe -m pytest tests/test_evidence_tier.py --collect-only -q

# 3. Unit tests pasan
./venv/Scripts/python.exe -m pytest tests/test_evidence_tier.py -v

# 4. Gate tests pasan
./venv/Scripts/python.exe -m pytest tests/test_evidence_tier.py -v -k "gate"

# 5. Integration test pasa
./venv/Scripts/python.exe -m pytest tests/test_evidence_tier.py -v -k "integration"

# 6. Regression suite completa
./venv/Scripts/python.exe -m pytest tests/ -x -q 2>&1 | tail -20
```

### Proxima sesion

**FASE-5**: v4complete Zi One Luxury (Tier B+ esperado) + v4complete hotel_test_001 (sin onboarding, Tier C esperado — control de regresion NP8) + Post-Implementation Analysis. Verificar matriz de 20 hallazgos (12 originales + 8 nuevos NP1-NP8).
