# FASE-0H: G8 Root-Cause Hardening — Asset Confidence desde Datos Derivables

> **Fase:** 0H
> **Tipo:** Código + tests
> **Comando largo:** No (verificación con fixture local)
> **Dependencias:** 0A-0G
> **Máximo iteraciones:** 60
> **Restricción:** NO ejecutar `v4complete`. Usar fixture de `audit_report_20260513_190808.json`.

---

## Contexto

Lee primero:
1. `.opencode/context/FASE-0H-G8-CORRECCION-CONTEXTO.md` — diagnóstico raíz completo
2. Este prompt

---

## Diagnóstico raíz (resumen)

G8 FAIL ocurre porque 8/12 assets tienen `confidence=0.5` debido a `WARNING` en `PreflightChecker`. El WARNING se produce porque su `required_field` no existe en `validated_data`.

**Causa raíz:** `validated_data` no contiene los campos porque:
- `v4_comprehensive.py` no los recolecta nominalmente, O
- `_extract_validated_fields()` no los deriva de subestructuras del `audit_report` donde SÍ existen.

**Consecuencia:** El scoring penaliza fallback controlado como si fuera genérico (`0.5/1 = 0.5`), haciendo que G8 falle para cualquier hotel que no tenga todos los datos perfectamente mapeados.

---

## Objetivo de esta fase

Transformar el sistema de confidence de un modelo binario (`campo existe / no existe`) a uno semántico que:
1. **Derive campos faltantes** del `audit_report` existente cuando sea posible (aplicable a cualquier hotel).
2. **Distinga `REQUIRED` vs `RECOMMENDED`** en el contrato de preflight (aplicable a cualquier asset futuro).
3. **No penalice fallback sobre `RECOMMENDED`** como genérico (aplicable a cualquier hotel sin esos datos).

Esto resuelve G8 desde causa raíz en lugar de aplicar `confidence bumps` por asset (half-measure).

---

## Principios de diseño (no negociables)

1. **Cero hardcode por asset.** No se permite `_FALLBACK_ASSET_MIN_CONFIDENCE = {"optimization_guide": 0.7, ...}`. La solución debe ser algorítmica.
2. **Cero dependencia de APIs nuevas.** No se agregan llamadas a GA4 API, Search Console, etc. Solo derivación de datos ya recolectados.
3. **Retrocompatible.** Los assets que hoy tienen `confidence=0.85` deben seguir teniéndolo.
4. **Testeable sin v4complete.** Toda la verificación se hace con fixture de `audit_report_20260513_190808.json` + tests unitarios.

---

## Tareas

### Tarea 1: Auditoría de derivación de datos

**Meta:** Determinar qué campos faltantes se pueden derivar del `audit_report` existente y cuáles requieren cambio de contrato (`REQUIRED` → `RECOMMENDED`).

Comandos de investigación:
```bash
# 1. ¿Qué campos extrae _extract_validated_fields() hoy?
grep -n "validated_data\[" modules/asset_generation/v4_asset_orchestrator.py

# 2. ¿Qué subestructuras del audit contienen datos similares?
python -c "
import json
d = json.load(open('output/v4_complete/hotelcastillareal/v4_audit/audit_report_20260513_190808.json'))
for k in ['schema', 'performance', 'validation', 'seo_elements', 'llm_report', 'gbp']:
    if k in d and isinstance(d[k], dict):
        print(f'{k}: {list(d[k].keys())}')
"

# 3. ¿Qué required_field declara cada asset?
grep -rn "required_field" modules/asset_generation/conditional_generator.py modules/asset_generation/asset_metadata.py
```

**Entregable:** Tabla con 4 columnas:
| required_field | ¿Derivable del audit? | Fuente en audit | Acción |

Acciones posibles: `DERIVAR`, `RECOMMENDED`, `REQUIRED_MANTENER`.

### Tarea 2: Implementar `DataDerivationLayer`

**Meta:** Crear módulo que derive campos faltantes del `audit_report` antes de que `_extract_validated_fields()` termine.

**Archivo nuevo:** `modules/asset_generation/data_derivation_layer.py`

**Responsabilidades:**
- Recibir `audit_report` (dict) completo.
- Derivar campos que hoy faltan en `validated_data`:
  - `og_tags_detected` → desde `seo_elements` / `llm_report` / raw HTML auditado.
  - `org_data` → desde `schema` (Organization schema si existe).
  - `ga4_available` → desde scripts/tracking detectados en audit.
  - `organic_traffic` → desde `performance` (estimación o indicador proxy); si no existe, derivar como `None` con flag `inferred=False`.
- Devolver dict con campos derivados + metadata (`inferred: bool`, `source: str`).

**Reglas:**
- Si el campo ya existe en `validated_data`, no sobrescribir (la fuente directa gana).
- Si no se puede derivar, omitir (no inventar datos).
- No requiere APIs externas.

### Tarea 3: Modificar `_extract_validated_fields()` para inyectar derivados

**Archivo:** `modules/asset_generation/v4_asset_orchestrator.py`

**Cambio:**
- Después de construir `validated_data` actual, llamar a `DataDerivationLayer.derive(audit_report)`.
- Fusionar campos derivados en `validated_data` con `DataPoint(source="derived", confidence=0.7, value=...)`.
- `confidence=0.7` para derivados porque son inferidos, no directos.

### Tarea 4: Refactorizar contrato de preflight (`REQUIRED` vs `RECOMMENDED`)

**Archivo:** `modules/asset_generation/conditional_generator.py` (o donde viva `PreflightChecker`)

**Cambio:**
- Extender `PreflightCheck` con campo `priority: Literal["REQUIRED", "RECOMMENDED"]`.
- `REQUIRED` (default): sin este campo el asset no puede generarse → BLOCKED si falta.
- `RECOMMENDED`: sin este campo el asset usa fallback → WARNING pero NO penaliza confidence a 0.5 si fallback está documentado.

**Assets a revisar:**
| Asset | required_field actual | Nueva prioridad | Justificación |
|-------|----------------------|-----------------|---------------|
| `optimization_guide` | `metadata` | REQUIRED | metadata es esencial para guía |
| `local_content_page` | `hotel_data` | REQUIRED | hotel_data siempre debe existir |
| `analytics_setup_guide` | `ga4_available` | RECOMMENDED | hotel puede no tener GA4; fallback aceptable |
| `indirect_traffic_optimization` | `organic_traffic` | RECOMMENDED | tráfico orgánico puede no estar disponible |
| `og_tags_guide` | `og_tags_detected` | RECOMMENDED | OG tags pueden no existir; guía de setup es válida |
| `open_graph` | `hotel_data` | REQUIRED | hotel_data debe existir |
| `org_schema` | `org_data` | RECOMMENDED | schema org puede no estar implementado; guía de setup es válida |
| `monthly_report` | `hotel_data` | REQUIRED | hotel_data debe existir |

### Tarea 5: Ajustar `_calculate_confidence_score()`

**Archivo:** `modules/asset_generation/conditional_generator.py`

**Cambio:**
```python
def _calculate_confidence_score(self, preflight_report: PreflightReport) -> float:
    if not preflight_report.checks:
        return 0.0
    
    total_score = 0.0
    for check in preflight_report.checks:
        if check.status == PreflightStatus.PASSED:
            total_score += 1.0
        elif check.status == PreflightStatus.WARNING:
            if check.priority == "RECOMMENDED" and check.fallback_action:
                total_score += 0.8  # fallback controlado sobre campo recomendado
            else:
                total_score += 0.5
        else:
            total_score += 0.0
    
    return total_score / len(preflight_report.checks)
```

**Regla:** `0.8` para RECOMMENDED+fallback porque el contenido sigue siendo útil (guía de implementación), no genérico.

### Tarea 6: Tests TDD

**Archivo nuevo:** `tests/asset_generation/test_data_derivation_layer.py`
**Archivo modificado:** `tests/asset_generation/test_conditional_generator.py` (agregar tests de scoring)

**Tests obligatorios:**
1. `test_derive_og_tags_from_seo_elements` — dado audit con `seo_elements.og_tags`, devuelve `og_tags_detected=True`.
2. `test_derive_org_data_from_schema` — dado audit con `schema.organization`, devuelve `org_data` dict.
3. `test_derive_ga4_from_scripts` — dado audit con script `gtag`, devuelve `ga4_available=True`.
4. `test_recommended_warning_scores_0_8` — preflight WARNING+RECOMMENDED+fallback → score 0.8.
5. `test_required_warning_scores_0_5` — preflight WARNING+REQUIRED → score 0.5 (sin cambio).
6. `test_hotelcastillareal_fixture_g8_pass` — cargar fixture real, ejecutar preflight, confirmar que los 8 assets afectados suben a ≥ 0.65.

**Fixture:**
```bash
mkdir -p tests/fixtures
cp output/v4_complete/hotelcastillareal/v4_audit/audit_report_20260513_190808.json tests/fixtures/audit_report_hotelcastillareal.json
```

### Tarea 7: Verificación local sin v4complete

**Meta:** Confirmar que G8 pasaría con los cambios usando solo el fixture.

```bash
pytest tests/asset_generation/test_data_derivation_layer.py -v
pytest tests/asset_generation/test_conditional_generator.py -v
pytest tests/quality_gates/test_delivery_quality_report.py -v
```

**Criterio PASS:**
- Todos los tests nuevos PASS.
- Ningún test de regresión FALLA.
- El fixture de hotelcastillareal produce ≥ 10/12 assets con confidence ≥ 0.65 (vs 4/12 actual).

---

## Criterios de Completitud

- [ ] Tabla de derivación completada (Tarea 1)
- [ ] `data_derivation_layer.py` implementado con ≥ 3 derivaciones (Tarea 2)
- [ ] `_extract_validated_fields()` inyecta derivados (Tarea 3)
- [ ] Contrato REQUIRED/RECOMMENDED aplicado a 8 assets (Tarea 4)
- [ ] `_calculate_confidence_score()` distingue prioridades (Tarea 5)
- [ ] Tests TDD: ≥ 6 tests, todos PASS (Tarea 6)
- [ ] Fixture copiado a `tests/fixtures/` (Tarea 6)
- [ ] Regresión: 0 tests rotos (Tarea 7)
- [ ] Fixture local demuestra ≥ 10/12 assets con confidence ≥ 0.65 (Tarea 7)

---

## Post-Ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-0H-G8 \
    --desc "Root-cause fix: data derivation + REQUIRED/RECOMMENDED preflight contract + confidence scoring refactor" \
    --tests "6+" \
    --check-manual-docs
```

Actualizar `06-checklist-implementacion.md`: marcar 0H-1..0H-7 como ✅.

---

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| Derivación incorrecta (falso positivo) | `confidence=0.7` para derivados; no sobrescribe datos directos. Tests con fixture real. |
| `org_data` no siempre es Organization schema | Manejar `LocalBusiness`, `Hotel`, `LodgingBusiness` como fuentes válidas. |
| Tests de regresión rotos | Ejecutar `pytest tests/ -x` antes de commit. |
| Alcance se extiende a detectores nuevos | Rechazar: si un campo NO es derivable del audit existente, su prioridad pasa a RECOMMENDED. No se toca `v4_comprehensive.py`. |
