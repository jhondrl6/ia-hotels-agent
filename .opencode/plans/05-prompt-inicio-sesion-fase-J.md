# FASE-J: NoDefaultsValidator Source-Aware + Template Honesto

## Contexto

El `NoDefaultsValidator` solo detecta valores ausentes (0, None, ""). No detecta valores fallback disfrazados como datos reales ($300K de legacy_hardcode, 0.50 de default). Ademas, el template de diagnostico dice "Comision OTA Actual (verificable)" cuando la fuente es "benchmark" — que NO es verificacion.

Esta fase INDEPENDIENTE de FASE-I (no comparten archivos). Puede ejecutarse en paralelo.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A..H | ✅ Completadas |
| FASE-I | ⬜/✅ (puede estar en progreso, es independiente) |

### Base Tecnica
- `modules/financial_engine/no_defaults_validator.py` — validador actual (solo detecta 0/None/"")
- `modules/financial_engine/calculator_v2.py` — orquesta validacion + calculo
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — template con "(verificable)"
- `modules/commercial_documents/v4_diagnostic_generator.py` — llena el template

---

## Tareas

### Tarea 1: Extender NoDefaultsValidator con deteccion de fuentes sospechosas

**Archivo**: `modules/financial_engine/no_defaults_validator.py`

Agregar concepto de "fuente sospechosa" (warning, no block):

```python
# Nuevos constantes de clase
SUSPECT_SOURCES = {"legacy_hardcode", "default", "unknown", "hardcoded", "estimated"}

@dataclass
class ValidationWarning:
    """Warning sobre fuente de datos sospechosa."""
    field: str
    value: Any
    source: str
    message: str
```

Modificar `validate()` para aceptar sources:
```python
def validate(self, data: Dict[str, Any], sources: Optional[Dict[str, str]] = None) -> NoDefaultsValidationResult:
    # ... validacion existente (bloquea 0/None/"") ...
    
    # NUEVO: detectar fuentes sospechosas (warnings, no blocks)
    warnings = []
    if sources:
        for field_name, source in sources.items():
            if source in self.SUSPECT_SOURCES:
                warnings.append(
                    f"'{field_name}' usa fuente '{source}' — dato no verificado"
                )
    
    return NoDefaultsValidationResult(
        can_calculate=can_calculate,
        blocks=self.blocks,
        warnings=warnings,
    )
```

Agregar propiedad al resultado:
```python
@dataclass
class NoDefaultsValidationResult:
    can_calculate: bool
    blocks: List[ValidationBlock] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    has_suspect_sources: bool = False  # NUEVO
    suspect_fields: List[str] = field(default_factory=list)  # NUEVO
```

Agregar metodo de conveniencia:
```python
@property
def source_reliability(self) -> str:
    """Retorna 'verified', 'estimated' o 'unverified'."""
    if self.has_suspect_sources:
        return "unverified"
    if self.can_calculate:
        return "verified"
    return "unverified"
```

### Tarea 2: Actualizar FinancialCalculatorV2 para pasar sources

**Archivo**: `modules/financial_engine/calculator_v2.py`

En `calculate()` (linea ~205):
```python
def calculate(self, financial_data: Dict[str, Any], 
              opportunity_scores: Optional[List[Any]] = None,
              data_sources: Optional[Dict[str, str]] = None) -> FinancialCalculationResult:
    # ...
    validation_result = self.validator.validate(financial_data, sources=data_sources)
    # ...
    # En metadata del resultado exitoso:
    metadata["source_reliability"] = validation_result.source_reliability
    metadata["suspect_fields"] = validation_result.suspect_fields
```

### Tarea 3: Cambiar titulo del template de "(verificable)" a condicional

**Archivo**: `modules/commercial_documents/templates/diagnostico_v6_template.md`

Buscar la seccion "Comision OTA Actual (verificable)" (~linea 70-72):
```markdown
### Comision OTA Actual (verificable)
```

Cambiar a:
```markdown
### ${financial_title_label}
```

Donde `financial_title_label` se resuelve dinamicamente:
- Si source_reliability == "verified" → "Comision OTA Actual (verificable)"
- Si source_reliability == "unverified" → "Comision OTA Estimada"
- Si source_reliability == "estimated" → "Comision OTA Estimada (benchmarks regionales)"

### Tarea 4: Actualizar generador para poblar el label condicional

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`

Buscar donde se llena el placeholder del titulo financiero y agregar logica:

```python
def _build_financial_title_label(self, source_reliability: str) -> str:
    """Retorna el label del titulo financiero segun confiabilidad de datos."""
    labels = {
        "verified": "Comision OTA Actual (verificable)",
        "estimated": "Comision OTA Estimada (benchmarks regionales)",
        "unverified": "Comision OTA Estimada",
    }
    return labels.get(source_reliability, "Comision OTA Estimada")
```

Buscar donde se preparan los placeholders del template y agregar:
```python
source_reliability = getattr(calc_result, 'metadata', {}).get('source_reliability', 'unverified')
placeholders['financial_title_label'] = self._build_financial_title_label(source_reliability)
```

### Tarea 5: Agregar asterisco de estimacion al monto principal

En el template, el monto principal muestra:
```
**$2.610.000 COP/mes**
```

Cambiar a:
```markdown
**${ota_commission_formatted} COP/mes**${estimate_asterisk}
```

Donde `estimate_asterisk` es:
- "" si source_reliability == "verified"
- "*" si source_reliability != "verified"

Y al final del bloque financiero, agregar nota condicional:
```markdown
${estimate_note}
```

Donde `estimate_note` es:
- "" si verified
- "\\n* Dato basado en estimaciones. Conecte GA4 para mayor precision." si unverified

### Tarea 6: Tests

```python
# test_no_defaults_validator_sources.py

def test_suspect_source_generates_warning():
    validator = NoDefaultsValidator()
    result = validator.validate(
        {"adr_cop": 300000, "occupancy_rate": 0.50, "direct_channel_percentage": 0.20},
        sources={"adr": "legacy_hardcode", "occupancy": "default"}
    )
    assert result.can_calculate == True  # No bloquea
    assert len(result.warnings) == 2
    assert "legacy_hardcode" in result.warnings[0]
    assert result.source_reliability == "unverified"

def test_verified_sources_no_warnings():
    validator = NoDefaultsValidator()
    result = validator.validate(
        {"adr_cop": 300000, "occupancy_rate": 0.50, "direct_channel_percentage": 0.20},
        sources={"adr": "onboarding", "occupancy": "onboarding", "direct_channel": "onboarding"}
    )
    assert result.can_calculate == True
    assert len(result.warnings) == 0
    assert result.source_reliability == "verified"

def test_mixed_sources_partial_warning():
    validator = NoDefaultsValidator()
    result = validator.validate(
        {"adr_cop": 300000, "occupancy_rate": 0.50, "direct_channel_percentage": 0.20},
        sources={"adr": "regional_v410_estimated", "occupancy": "default", "direct_channel": "onboarding"}
    )
    assert len(result.warnings) == 1  # Solo occupancy
    assert "occupancy" in result.warnings[0]

def test_no_sources_param_no_warning():
    """Backward compat: si no se pasa sources, no hay warnings."""
    validator = NoDefaultsValidator()
    result = validator.validate(
        {"adr_cop": 300000, "occupancy_rate": 0.50, "direct_channel_percentage": 0.20}
    )
    assert len(result.warnings) == 0

def test_financial_title_label_verified():
    gen = V4DiagnosticGenerator(...)
    label = gen._build_financial_title_label("verified")
    assert "verificable" in label.lower()

def test_financial_title_label_unverified():
    gen = V4DiagnosticGenerator(...)
    label = gen._build_financial_title_label("unverified")
    assert "Estimada" in label
    assert "verificable" not in label
```

---

## Criterios de Aceptacion

| # | Criterio | Verificacion |
|---|----------|-------------|
| 1 | Sources sospechosos generan warnings (no blocks) | test_suspect_source_generates_warning |
| 2 | source_reliability = "unverified" cuando hay fuentes sospechosas | test |
| 3 | Template muestra "Estimada" cuando datos son unverified | E2E output |
| 4 | Template muestra "verificable" cuando datos son verified | test unitario |
| 5 | Backward compatible (sin sources param = sin warnings) | test_no_sources_param_no_warning |
| 6 | 7 tests nuevos pasan | pytest |
| 7 | Suite regresion pasa | pytest tests/ |

---

## Restricciones

- NO tocar `feature_flags.py` ni `harness_handlers.py` — eso es FASE-I
- NO tocar `main.py` lineas 1720-1733 — eso es FASE-K
- NO tocar `scenario_calculator.py` — eso es FASE-K
- Los warnings NO bloquean el calculo — solo documentan la naturaleza del dato
- El campo `can_calculate` sigue funcionando igual (bloquea solo 0/None/"")

---

## Post-Ejecucion (OBLIGATORIO)

1. `dependencias-fases.md` — Marcar FASE-J como ✅ Completada
2. `06-checklist-implementacion.md` — Marcar FASE-J
3. Ejecutar:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-J \
    --desc "NoDefaultsValidator source-aware + template honesto (Estimada vs verificable)" \
    --archivos-mod "modules/financial_engine/no_defaults_validator.py,modules/financial_engine/calculator_v2.py,modules/commercial_documents/templates/diagnostico_v6_template.md,modules/commercial_documents/v4_diagnostic_generator.py" \
    --tests "7"
```
