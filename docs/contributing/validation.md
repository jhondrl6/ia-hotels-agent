# Sistema de Validacion

> Este documento contiene el sistema de validacion segun CONTRIBUTING.md §6, §10, §11, §12.

---

## 6. Sistema de Validacion (v3.8.0)

El sistema utiliza pre-commit hooks + Validation Engine nativo.

### Instalacion (una vez)

```bash
pip install pre-commit
pre-commit install
```

### Antes de cada commit

```bash
# Validacion rapida (recomendado)
python scripts/run_all_validations.py --quick

# Validacion completa
python scripts/run_all_validations.py

# Validacion post-cambios v4complete
python .agents/workflows/v4_regression_guardian.py --quick
```

### Validaciones Disponibles

| Comando | Descripcion |
|---------|-------------|
| `python scripts/run_all_validations.py` | Todas las validaciones (7 checks) |
| `python scripts/run_all_validations.py --quick` | Validaciones esenciales (4 checks) |
| `python scripts/validate.py --plan` | Validar coherencia Plan Maestro |
| `python scripts/validate.py --security` | Detectar secrets hardcoded |
| `python scripts/validate.py --content <file>` | Validar contenido de archivo |
| `pre-commit run --all-files` | Ejecutar todos los hooks manualmente |

Si alguna validacion falla, corregir antes de hacer commit.

---

## 10. Solucion de Problemas

### Error: "pre-commit not found"
```bash
pip install pre-commit
```

### Error: "pytest failed"
```bash
# Ver detalles de tests fallidos
pytest tests/ -v --tb=short
```

### Saltar validaciones (NO recomendado)
```bash
git commit -m "mensaje" --no-verify
```

### Error: "version out of sync"
```bash
python scripts/sync_versions.py
```

---

## 11. Controles de Coherencia v4.0

Al agregar nuevos checks de coherencia o modificar los existentes:

### 11.1 Definir en `.conductor/guidelines.yaml`

```yaml
v4_coherence_rules:
  nuevo_check:
    confidence_threshold: 0.8
    blocking: true|false
    description: "Descripcion clara del check"
```

### 11.2 Implementar en `modules/commercial_documents/coherence_validator.py`

```python
def _check_nuevo_check(self, ...) -> CoherenceCheck:
    """Descripcion del check."""
    threshold = self.config.get_threshold('nuevo_check')
    is_blocking = self.config.is_blocking('nuevo_check')
    
    passed = ...  # Logica de validacion
    score = ...   # Score entre 0.0 y 1.0
    
    return CoherenceCheck(
        name='nuevo_check',
        passed=passed,
        score=score,
        message='...',
        severity='error' if is_blocking and not passed else 'warning'
    )
```

### 11.3 Agregar al metodo `validate()`

```python
def validate(self, ...):
    checks = [
        self._check_problems_have_solutions(...),
        self._check_assets_are_justified(...),
        # ... checks existentes
        self._check_nuevo_check(...),
    ]
```

### 11.4 Documentar en `DOMAIN_PRIMER.md`

```markdown
### Nuevo Check
**Definicion**: Descripcion del check
**Mapeo**: `coherence_validator._check_nuevo_check()`
**Umbrales**: confidence >= 0.8
**Casos de borde**: 
- Caso X: Comportamiento Y
```

### 11.5 Sincronizar con Workflow

Actualizar `.agents/workflows/v4_coherence_validator.md`:
- Agregar paso de ejecucion si aplica
- Actualizar criterios de exito
- Documentar umbral configurable

### 11.6 Tests Obligatorios

Crear tests en `tests/test_coherence_validator.py`:
```python
def test_nuevo_check_passed(self):
    """Test cuando el check pasa."""
    ...

def test_nuevo_check_failed(self):
    """Test cuando el check falla."""
    ...

def test_nuevo_check_blocking(self):
    """Test comportamiento blocking."""
    ...
```

### 11.7 Validacion Pre-Commit

```bash
# 1. Regla en YAML
python -c "from modules.commercial_documents import CoherenceConfig; c = CoherenceConfig(); print(c.get_rule('nuevo_check'))"

# 2. Check implementado
python -c "from modules.commercial_documents import CoherenceValidator; v = CoherenceValidator(); assert hasattr(v, '_check_nuevo_check')"

# 3. Tests pasan
pytest tests/test_coherence_validator.py::TestNuevoCheck -v

# 4. Validaciones del proyecto
python scripts/run_all_validaciones.py
```

---

## 12. Sistema de Regresion v4.2.0

### 12.1 Dos Modos de Validacion

| Modo | Requisitos | Uso |
|------|-----------|-----|
| `url-only` | Assets >=3/5, Performance presente, GBP diagnosticado | Analisis rapido sin datos operativos |
| `with-onboarding` | Coherence >=0.8, Datos financieros VERIFIED | Analisis completo con onboarding |

### 12.2 Script de Regresion

```bash
# Modo URL-only (default)
python .opencode/plans/v4_repair_plan/scripts/regression_test.py \
    --new output/v4_complete/ \
    --mode url-only

# Modo with-onboarding
python .opencode/plans/v4_repair_plan/scripts/regression_test.py \
    --new output/v4_complete/ \
    --mode with-onboarding
```

### 12.3 Checks de Regresion

| # | Check | Validacion |
|---|-------|------------|
| 1 | Assets Generated | >=3/5 assets generados |
| 2 | Coherence Score | Estructura valida (url-only) o >=0.8 (with-onboarding) |
| 3 | Performance Detected | Score presente (0-100) |
| 4 | Performance Status | "VERIFIED" o "LAB_DATA_ONLY" |
| 5 | GBP Diagnostics | `error_type` poblado si `place_found=false` |
| 6 | Diagnostic Structure | 4 secciones obligatorias |
| 7 | Proposal Structure | 5 secciones obligatorias |

### 12.4 Nuevos Assets Generables

| Asset | Tipo | Requiere | Fallback |
|-------|------|----------|----------|
| `geo_playbook` | Markdown | gbp_data | Si (con warning) |
| `review_plan` | Markdown | gbp_reviews | Si (con warning) |
| `review_widget` | HTML | review_data | Si (con warning) |
| `org_schema` | JSON-LD | org_data | Si (con warning) |

### 12.5 Tests Obligatorios para Nuevos Assets

1. **Agregar generador** en `modules/asset_generation/conditional_generator.py`
2. **Agregar test** en `tests/asset_generation/test_conditional_new_assets.py`
3. **Validar preflight** permite fallback con `block_on_failure=False`
4. **Ejecutar regresion** para validar E2E

### 12.6 Checklist Pre-Release

```bash
# 1. Tests unitarios
python -m pytest tests/ -x --tb=short -q

# 2. Regresion url-only
python .opencode/plans/v4_repair_plan/scripts/regression_test.py \
    --new output/test_validation/v4_complete/ \
    --mode url-only

# 3. Validaciones del proyecto
python scripts/run_all_validations.py

# 4. Verificar coherencia documentacion
git diff --stat
```

### 12.7 v4_regression_guardian

Valida que cambios en codigo no introduzcan regresiones en el flujo v4complete.

```bash
# Validacion rapida (recomendado)
python .agents/workflows/v4_regression_guardian.py --quick

# Validacion completa
python .agents/workflows/v4_regression_guardian.py --full

# Modo CI
python .agents/workflows/v4_regression_guardian.py --quiet

# Directorio alternativo
python .agents/workflows/v4_regression_guardian.py --workdir /ruta/al/proyecto

# Re-ejecutar tests fallidos
python .agents/workflows/v4_regression_guardian.py --retry-failed
```

**Diferencia con regression_test.py:**
- `regression_test.py`: Valida outputs de un analisis v4complete especifico
- `v4_regression_guardian`: Valida que cambios en codigo no hayan roto pruebas

**Ejecutar despues de modificar:**
- orchestration_v4/
- data_validation/
- financial_engine/
- asset_generation/
- commercial_documents/
- modules/quality_gates/

---

## 15. Taxonomia de Confianza

| Nivel | Confidence | Criterio | Uso en Assets |
|-------|------------|----------|---------------|
| 🟢 VERIFIED | >= 0.9 | 2+ fuentes coinciden | Directo |
| 🟡 ESTIMATED | 0.5-0.9 | 1 fuente o benchmark | Con disclaimer |
| 🔴 CONFLICT | < 0.5 | Fuentes contradicen | Bloqueado |

### 15.1 Gates de Assets

| Asset | Threshold | Comportamiento |
|-------|-----------|----------------|
| WhatsApp | >= 0.9 | PASSED |
| WhatsApp | 0.5-0.9 | ESTIMATED con disclaimer |
| WhatsApp | < 0.5 | BLOCKED |
| FAQ Page | >= 0.7 | PASSED |
| FAQ Page | < 0.7 | ESTIMATED/BLOCKED |
| Hotel Schema | >= 0.8 | PASSED |
| Hotel Schema | < 0.8 | ESTIMATED/BLOCKED |

---

## 16. Quality Gates de Publicacion

Antes de marcar un analisis como `READY_FOR_CLIENT`:

| Gate | Umbral | Severidad |
|------|--------|-----------|
| hard_contradictions | = 0 | CRITICAL |
| evidence_coverage | >= 95% | HIGH |
| financial_validity | sin defaults | CRITICAL |
| coherence | >= 0.8 | CRITICAL |
| critical_recall | >= 90% | HIGH |

### 16.1 Estados de Publicacion

| Estado | Descripcion |
|--------|-------------|
| `DRAFT_INTERNAL` | Analisis en progreso |
| `REQUIRES_REVIEW` | Gate fallido, requiere correccion |
| `READY_FOR_CLIENT` | Todos los gates pasados |
