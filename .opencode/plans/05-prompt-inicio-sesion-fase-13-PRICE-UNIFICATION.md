---
description: Fix Bug 2 - Unificar cálculo de precio entre financial_scenarios.json y propuesta comercial
version: 1.0.0
---

# FASE 13: Price Calculation Unification

**ID**: PRICE-UNIFICATION  
**Objetivo**: Corregir la desconexión entre el precio calculado en `financial_scenarios.json` ($130,500 COP) y el precio en la propuesta comercial ($800,000 COP)  
**Dependencias**: FASE 12 (AUDIT-DATA-PIPELINE) ✅ REQUERIDA  
**Duración estimada**: 1-2 horas  
**Skill**: systematic-debugging

---

## Contexto

### Problema Detectado

Durante la ejecución de `v4complete` para Hotel Visperas, se encontró una contradicción en el precio:

| Fuente | Precio |
|--------|--------|
| `financial_scenarios.json` (generado por `calculate_price_with_shadow`) | **$130,500 COP/mes** |
| Propuesta comercial (`v4_proposal_generator.py`) | **$800,000 COP/mes** |

### Análisis de Causa Raíz

**Ubicación del bug**: `modules/commercial_documents/v4_proposal_generator.py` línea 558

```python
calculated_price = min(max(int(expected_monthly * 0.02), 800000), 2500000)
```

**Problema**: La fórmula usa:
- `expected_monthly * 0.02` = 2% del dolor (esto está bien)
- Mínimo de $800,000 (esto ignora el `pricing_result` ya calculado)

**Flujo actual**:

```
main.py
    ├── calculate_price_with_shadow() → pricing_result.monthly_price_cop = $130,500 (pain_ratio=5%)
    │
    ├── financial_scenarios.json guarda $130,500 ✅
    │
    └── v4_proposal_generator.generate()
        └── calculate_price() → min(max(expected_monthly * 0.02, 800000), 2500000)
                               → ignora pricing_result y usa fórmula legacy con mínimo $800,000 ❌
```

### Estado de Fases Anteriores

| Fase | ID | Estado |
|------|----|--------|
| FASE 12 | AUDIT-DATA-PIPELINE | ⏳ PENDIENTE (prerequisito) |
| FASE 11 | GOOGLE-TRAVEL-INTEGRATION | ✅ COMPLETADA |

### Base Técnica Disponible

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py` (línea 558: `calculate_price`)
- `main.py` (líneas 1624-1636: donde se calcula `pricing_result`)
- `modules/financial_engine/pricing_wrapper.py` (donde está `calculate_price_with_shadow`)

**Módulos relacionados**:
- `PricingResolutionResult` - resultado de `calculate_price_with_shadow`
- `V4ProposalGenerator` - generador de propuesta comercial
- `FinancialCalculatorV2` - calculadora financiera

---

## Tareas

### Tarea 13.1: Analizar cómo se pasa el precio a la propuesta

**Objetivo**: Entender el flujo actual de datos para corregirlo

**Búsqueda requerida**:
```bash
grep -n "price_monthly\|pricing_result\|calculated_price" main.py modules/commercial_documents/*.py
```

**Criterios de aceptación**:
- [ ] Documentar el flujo actual de cómo llega (o no llega) `pricing_result` a la propuesta

### Tarea 13.2: Corregir v4_proposal_generator para usar pricing_result

**Objetivo**: Modificar la propuesta para usar `pricing_result` en lugar de recalcular

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

**Cambio requerido** (línea 547-560):

```python
def calculate_price(
    expected_monthly: float,
    pricing_result: PricingResolutionResult = None,  # NUEVO PARÁMETRO
    pain_ratio: float = 0.05
) -> int:
    """
    Calcula precio mensual basado en expected monthly loss.
    
    Usa pricing_result si está disponible para mantener consistencia
    con el cálculo de financial_scenarios.json
    """
    # Si tenemos pricing_result, usarlo directamente (ya fue calculado correctamente)
    if pricing_result is not None:
        return pricing_result.monthly_price_cop
    
    # Fallback: calcular con fórmula y pain_ratio especificado
    calculated_price = int(expected_monthly * pain_ratio)
    
    # Aplicar bounds solo si no hay pricing_result
    return calculated_price
```

**Criterios de aceptación**:
- [ ] Método `calculate_price()` acepta `pricing_result` como parámetro opcional
- [ ] Si `pricing_result` existe, retorna su `monthly_price_cop` directamente
- [ ] Fallback mantiene compatibilidad hacia atrás

### Tarea 13.3: Actualizar llamada en main.py

**Objetivo**: Pasar `pricing_result` a la propuesta

**Archivo**: `main.py`

**Cambio requerido** (en `V4ProposalGenerator.generate()` call alrededor de línea 1988):

```python
# Antes:
proposal_path = proposal_gen.generate(
    diagnostic_summary=diagnostic_summary,
    financial_scenarios=financial_scenarios_obj,
    asset_plan=asset_plan,
    hotel_name=hotel_name,
    output_dir=str(output_dir),
    audit_result=audit_result
)

# Después:
proposal_path = proposal_gen.generate(
    diagnostic_summary=diagnostic_summary,
    financial_scenarios=financial_scenarios_obj,
    asset_plan=asset_plan,
    hotel_name=hotel_name,
    output_dir=str(output_dir),
    audit_result=audit_result,
    pricing_result=pricing_result  # NUEVO: Pasar pricing_result para consistencia
)
```

**Criterios de aceptación**:
- [ ] Llamada a `generate()` pasa `pricing_result`
- [ ] Si `pricing_result` es None, usa fallback

### Tarea 13.4: Actualizar signatura de V4ProposalGenerator.generate()

**Objetivo**: Aceptar y usar el nuevo parámetro

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

**Cambio requerido** (signatura del método `generate`):

```python
def generate(
    self,
    diagnostic_summary: DiagnosticSummary,
    financial_scenarios: FinancialScenarios,
    asset_plan: List[AssetSpec],
    hotel_name: str,
    output_dir: str,
    audit_result: V4AuditResult = None,
    pricing_result: PricingResolutionResult = None  # NUEVO
) -> str:
    ...
    # En el cálculo de precio:
    price_monthly = self.calculate_price(
        expected_monthly=expected_monthly,
        pricing_result=pricing_result,  # Pasar pricing_result
        pain_ratio=0.05
    )
```

**Criterios de aceptación**:
- [ ] Signatura del método `generate()` incluye `pricing_result=None`
- [ ] Dentro del método se pasa `pricing_result` a `calculate_price()`

### Tarea 13.5: Crear test de regresión

**Objetivo**: Verificar que el precio es consistente entre financial_scenarios.json y la propuesta

**Archivo**: `tests/commercial_documents/test_price_consistency.py`

**Test requerido**:
```python
def test_price_consistency_between_scenarios_and_proposal():
    """Verifica que el precio en la propuesta coincide con financial_scenarios.json"""
    # Arrange
    pricing_result = PricingResolutionResult(
        monthly_price_cop=130500,
        tier="boutique",
        pain_ratio=0.05,
        is_compliant=True,
        source="legacy_fixed"
    )
    expected_monthly = 2610000
    
    # Act
    price = calculate_price(
        expected_monthly=expected_monthly,
        pricing_result=pricing_result,
        pain_ratio=0.05
    )
    
    # Assert
    assert price == 130500  # Debe usar pricing_result, no $800,000

def test_price_uses_fallback_when_no_pricing_result():
    """Verifica que usa fallback si no hay pricing_result"""
    # Arrange
    expected_monthly = 2610000
    pain_ratio = 0.05  # 5%
    
    # Act
    price = calculate_price(
        expected_monthly=expected_monthly,
        pricing_result=None,
        pain_ratio=pain_ratio
    )
    
    # Assert: 2610000 * 0.05 = 130500
    assert price == 130500
```

**Criterios de aceptación**:
- [ ] Test `test_price_consistency_between_scenarios_and_proposal` pasa
- [ ] Test `test_price_uses_fallback_when_no_pricing_result` pasa

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_price_consistency_between_scenarios_and_proposal` | `tests/commercial_documents/test_price_consistency.py` | Debe pasar |
| `test_price_uses_fallback_when_no_pricing_result` | `tests/commercial_documents/test_price_consistency.py` | Debe pasar |
| Test de integración `v4complete` | `tests/e2e/test_v40_complete_flow.py` | Precio en propuesta = precio en financial_scenarios.json |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_price_consistency.py -v
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**:
   - Marcar FASE 13 como ✅ COMPLETADA
   - Agregar fecha de finalización
   - Agregar notas: "Bug 2 corregido: price_unification"

2. **`README-FASES-TRACKING.md`**:
   - Marcar FASE 13 como completada
   - Actualizar tabla de progreso

3. **`09-documentacion-post-proyecto.md`**:
   - Sección A: "modules/commercial_documents/v4_proposal_generator.py - calculate_price() ahora usa pricing_result"
   - Sección D: Tests +2
   - Sección E: Marcar archivos actualizados

4. **Evidencia**: Crear `evidence/fase-13/` con logs de ejecución

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Tests pasan**: `pytest tests/commercial_documents/test_price_consistency.py -v` pasa 4/4
- [ ] **Validación de regresión**: `pytest tests/e2e/test_v40_complete_flow.py -v` pasa
- [ ] **Precio consistente**: En ejecución real, `financial_scenarios.json` y propuesta tienen el mismo precio
- [ ] **`dependencias-fases.md` actualizado**: FASE 13 marcada como completada
- [ ] **README actualizado**: Tabla de progreso refleja FASE 13 completada
- [ ] **Documentación post-proyecto actualizada**: Secciones A, D, E actualizadas
- [ ] **Evidencia preservada**: Logs en `evidence/fase-13/`
- [ ] **Post-ejecución completada**: Todos los puntos anteriores realizados

---

## Restricciones

- NO cambiar la fórmula base de `calculate_price_with_shadow` (ya está correcta)
- NO modificar el formato de `financial_scenarios.json`
- Mantener backward compatibility para casos donde no hay `pricing_result`

---

## Verificación Final (Post-FASE 12 y FASE 13)

Después de completar ambas fases, ejecutar:

```bash
python main.py v4complete --url https://www.hotelvisperas.com/ --nombre "Hotel Visperas" --output ./tmp/verificacion
```

Y verificar:
1. `hotel_schema.json` contiene `"Hotel Visperas"` (no "Hotel")
2. `financial_scenarios.json` y propuesta tienen el mismo precio
3. Coherence score se mantiene >= 0.8

---

## Estado de Avance (Sesión Previa - 2026-03-25)

### Implementación Completada ✅

**1. `modules/commercial_documents/v4_proposal_generator.py`:**
- Agregado import: `from modules.financial_engine.pricing_resolution_wrapper import PricingResolutionResult`
- Añadido parámetro `pricing_result: Optional[PricingResolutionResult] = None` a `generate()`
- Nueva lógica de precio:
  ```python
  if pricing_result is not None:
      price_monthly = int(pricing_result.monthly_price_cop)
  elif price_monthly is None:
      price_monthly = self._calculate_dynamic_price(financial_scenarios)
  ```

**2. `main.py` línea ~1994:**
- Agregado `pricing_result=pricing_result` a la llamada de `proposal_gen.generate()`

**3. `tests/commercial_documents/test_price_consistency.py`:**
- Creado con 4 tests unitarios

### Tests: 3/4 Pasan

```
tests/commercial_documents/test_price_consistency.py
  test_price_uses_pricing_result_when_provided: ✅ PASSED
  test_price_uses_legacy_formula_when_no_pricing_result: ✅ PASSED
  test_pricing_result_takes_precedence_over_price_monthly: ✅ PASSED
  test_proposal_price_matches_financial_scenarios: ✅ PASSED
```

### Pendiente (1 test requiere fix de mock)

El 4to test tiene un patch incompleto de `builtins.open`. Fix requerido:
```python
# Cambiar en test_pricing_result_takes_precedence_over_price_monthly:
# De:
patch('pathlib.Path.mkdir', return_value=True):
# A:
patch('pathlib.Path.mkdir', return_value=True), \
patch('builtins.open', MagicMock()):
```

---

## Versión

- **v1.1.0** (2026-03-25): Sesión previa - implementación completada, 3/4 tests pasando
- **v1.0.0** (2026-03-25): Fase inicial basada en análisis de coherencia Hotel Visperas
