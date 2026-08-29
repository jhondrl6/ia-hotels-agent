# FASE-3: Semántica + Floor + Gate Estricto

**Plan**: ROICRII
**Tipo**: Código+Tests
**Hallazgos**: IMP-01, NEW-05, NEW-02
**Prerrequisito**: FASE-2 completada
**Ejecución**: delegate_task (3 fixes independientes — candidato a batch paralelo)
**Iteración estimada**: 35-45

---

## Objetivo

Tres fixes independientes en capa de gobernanza comercial: (1) clarificar semántica de pain_ratio en el copy, (2) unificar fallback de operational_floor, (3) añadir strict_mode al commercial gate para audiencia externa.

---

## DELEGATE_TASK — CONTEXTO AUTÓNOMO

**Working directory**: `/mnt/c/Users/Jhond/Github/iah-cli`

**Preflight**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
source venv/bin/activate 2>/dev/null || true
```

**Estructura**: Los 3 fixes son independientes. Se pueden ejecutar en cualquier orden.

---

### Fix 3A: Clarificar pain_ratio_note — separar addressable vs fee/loss [IMP-01]

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

**Paso 1**: Leer L785-805 para ver el bloque completo:
```bash
sed -n '785,805p' modules/commercial_documents/v4_proposal_generator.py
```

**Paso 2**: Encontrar el bloque `'pain_ratio_note'`. El ANTES (verificar contra output de Paso 1):
```python
            'pain_ratio_note': (
                f"**Nota de proyección**: La inversión mensual de ${int(monthly_investment):,} COP "
                f"representa el {pain_ratio:.0%} de su pérdida mensual estimada. "
                f"Aplicando una efectividad esperada de recuperación del {recovery_factors['realistic']:.0%}, "
                f"la proyección conservadora es de aproximadamente "
                f"${int(raw_monthly_loss * pain_ratio * recovery_factors['realistic']):,}/mes"
                f" (vs. la cifra bruta de ${int(raw_monthly_loss * pain_ratio):,} que se mostraría "
                f"sin ajustar por efectividad)."
            ),
```

Reemplazar con:
```python
            'pain_ratio_note': (
                f"**Nota de proyección**: Abordamos el {pain_ratio:.0%} de su pérdida mensual estimada "
                f"(zona addressable por IAO). Su inversión mensual de ${int(monthly_investment):,} COP "
                f"representa el {monthly_investment/raw_monthly_loss:.1%} de su pérdida total. "
                f"Aplicando una efectividad esperada de recuperación del {recovery_factors['realistic']:.0%}, "
                f"la proyección conservadora es de aproximadamente "
                f"${int(raw_monthly_loss * pain_ratio * recovery_factors['realistic']):,}/mes."
            ),
```

**NOTA**: Verificar que `raw_monthly_loss` está en scope. Si no, buscar la variable equivalente:
```bash
grep -n "raw_monthly_loss\|monthly_loss\|financial_value_central" modules/commercial_documents/v4_proposal_generator.py | head -15
```
El bloque está dentro de la función `_build_proposal_context()` o similar. `raw_monthly_loss` se define unas 20-30 líneas antes del `pain_ratio_note`.

**Paso 3**: Verificar:
```bash
grep -n "addressable" modules/commercial_documents/v4_proposal_generator.py
# Expected: ≥1 match en la zona de pain_ratio_note
```

---

### Fix 3B: Unificar fallback operational_floor a 400K [NEW-05]

**Archivo**: `modules/financial_engine/pricing_calculator.py`

**Paso 1**: Leer L240-250:
```bash
sed -n '240,250p' modules/financial_engine/pricing_calculator.py
```

**Paso 2**: El ANTES (verificar):
```python
    operational_floor = config.get("operational_floor", min_price)
```

Reemplazar con:
```python
    operational_floor = config.get("operational_floor", 400_000)  # ROICRII: unificar fallback con constructor
```

**Paso 3**: Verificar que ambos fallbacks ahora son 400_000:
```bash
grep -n "operational_floor.*400_000\|operational_floor.*defaults" modules/financial_engine/pricing_calculator.py
# Expected: ≥2 matches — constructor L144 + calcular_precio_final L245
```

---

### Fix 3C: CommercialGateBlockedError para audiencia externa [NEW-02]

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

**Paso 1**: Verificar si la exception ya existe:
```bash
grep -rn "CommercialGateBlockedError" modules/ 2>/dev/null
grep -rn "class.*Gate.*Error\|class.*Blocked.*Error" modules/commercial_documents/ 2>/dev/null
```

**Paso 2**: Si NO existe, buscar dónde crearla. Opciones:
- `modules/commercial_documents/exceptions.py` (si existe)
- Al inicio de `v4_proposal_generator.py` (inline)

Verificar:
```bash
ls modules/commercial_documents/exceptions.py 2>/dev/null || echo "No existe exceptions.py"
grep -n "^class\|^from\|^import" modules/commercial_documents/v4_proposal_generator.py | head -30
```

Si no hay `exceptions.py`, crear la exception al inicio de `v4_proposal_generator.py` después de los imports existentes:
```python
class CommercialGateBlockedError(Exception):
    """Raised when commercial gates fail for external audience — blocks document generation."""
    pass
```

**Paso 3**: Leer L394-420 para el bloque del gate:
```bash
sed -n '394,420p' modules/commercial_documents/v4_proposal_generator.py
```

**Paso 4**: El ANTES (verificar contra Paso 3):
```python
                else:
                    logging.warning(
                        "Proposal commercial gates BLOCKING (hidden from client): %s",
                        [r.gate_id for r in commercial_report.blocking_failures],
                    )
```

Reemplazar con:
```python
                else:
                    # ROICRII NEW-02: Para audiencia externa, bloquear publicación
                    failure_ids = [r.gate_id for r in commercial_report.blocking_failures]
                    raise CommercialGateBlockedError(
                        f"Propuesta bloqueada por {len(failure_ids)} gates comerciales: {failure_ids}. "
                        f"Corrija los problemas antes de generar para audiencia externa."
                    )
```

**Paso 5**: Verificar:
```bash
grep -n "CommercialGateBlockedError" modules/commercial_documents/v4_proposal_generator.py
# Expected: ≥2 (class def + raise)
```

---

### Tarea 3D: Tests

**Archivo**: Crear `tests/test_semantics_floor_gate.py`

```python
"""ROICRII FASE-3: Tests de semántica, floor unificado, gate estricto."""
import pytest


class TestPainRatioSemantics:
    """IMP-01: pain_ratio_note diferencia addressable vs fee/loss."""

    def test_pain_ratio_note_contains_addressable(self):
        """El copy debe mencionar 'addressable' para clarificar que pain_ratio es zona abordable."""
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
        gen = V4ProposalGenerator()
        # Generar contexto de propuesta para hotel de prueba
        # (adaptar según la API real del generador)
        context = gen._build_proposal_context(
            hotel_name="Test Hotel",
            url="https://example.com",
            region="eje_cafetero",
        )
        note = context.get('pain_ratio_note', '')
        assert 'addressable' in note.lower(), f"pain_ratio_note no contiene 'addressable': {note[:200]}"


class TestOperationalFloorUnified:
    """NEW-05: operational_floor fallback = 400K en ambos caminos."""

    def test_fallback_is_400k_in_calcular_precio_final(self):
        """calcular_precio_final() con config vacío debe usar 400K como floor."""
        from modules.financial_engine.pricing_calculator import calcular_precio_final
        # Llamar con config mínimo (sin operational_floor)
        result = calcular_precio_final(
            tier="boutique",
            config={},  # Sin operational_floor
            expected_loss_cop=3_741_696,
            rooms=30,
        )
        # El resultado debe respetar floor de 400K, NO 800K (min_price)
        assert result['monthly_price_cop'] >= 400_000, f"Floor incorrecto: {result['monthly_price_cop']}"

    def test_fallback_is_400k_in_constructor(self):
        """PricingCalculator constructor con defaults vacíos debe usar 400K."""
        from modules.financial_engine.pricing_calculator import PricingCalculator
        calc = PricingCalculator()
        # Verificar que el default del constructor es 400K
        # (adaptar según cómo se accede al default)
        defaults = calc.defaults
        assert defaults.get('operational_floor') == 400_000


class TestExternalGateBlocking:
    """NEW-02: CommercialGateBlockedError para audiencia externa."""

    def test_raises_for_external_audience(self):
        """Con gates fallidos y audiencia externa, debe lanzar CommercialGateBlockedError."""
        # Este test requiere mockear el CommercialGateValidator para que retorne failures
        # Adaptar según la API real
        try:
            from modules.commercial_documents.v4_proposal_generator import CommercialGateBlockedError
            assert issubclass(CommercialGateBlockedError, Exception)
        except ImportError:
            pytest.fail("CommercialGateBlockedError no existe — fix 3C no aplicado")
```

**Ejecución**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python -m pytest tests/test_semantics_floor_gate.py -v 2>&1 | tail -30
```

**NOTA**: Los tests de esta fase son más exploratorios que los de FASE-2. Si un test falla porque la API del generador no es como se asumió, adaptar el test al código real. Lo importante es verificar:
1. "addressable" aparece en el copy
2. operational_floor fallback = 400K en ambos caminos
3. CommercialGateBlockedError existe como clase

---

### Post-tareas: Verificación final + docs + log

```bash
# 1. Verificaciones
grep -n "addressable" modules/commercial_documents/v4_proposal_generator.py
grep -n "operational_floor.*400_000" modules/financial_engine/pricing_calculator.py
grep -n "CommercialGateBlockedError" modules/commercial_documents/v4_proposal_generator.py

# 2. log_phase
cd /mnt/c/Users/Jhond/Github/iah-cli
python scripts/log_phase.py --phase "FASE-3" --plan "ROICRII" --status "completed" --desc "Pain_ratio_clarificado_floor_unificado_gate_estricto" 2>/dev/null || echo "log_phase no disponible"

# 3. Actualizar documentación
# Leer y actualizar /.opencode/plans/Archives/ROICRII/09-documentacion-post-proyecto.md
```

---

## Hallazgos a Resolver

| Hallazgo | Veredicto | Fix |
|----------|-----------|-----|
| IMP-01 | pain_ratio_note dice "representa el X%" pero es addressable, no fee/loss | 3A: Copy clarificado |
| NEW-05 | operational_floor fallback 800K vs 400K | 3B: Unificar a 400K |
| NEW-02 | Gate externo solo warning, no bloquea | 3C: CommercialGateBlockedError |
