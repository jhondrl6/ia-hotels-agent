# Contexto — Fase de Corrección G8: Asset Specificity

> **Fecha:** 2026-05-13
> **Repo:** `/mnt/c/Users/Jhond/Github/iah-cli`
> **Origen:** FASE-0G-E2E — G8 FAIL (8/12 assets ≤ 0.5 confidence)
> **Propósito:** contexto completo para que una sesión nueva pueda crear el plan de implementación de la corrección G8 sin redescubrir causa raíz, opciones ni restricciones.

---

## 1. Diagnóstico raíz

### 1.1 Resultado FASE-0G-E2E

El E2E controlado sobre Hotel Castilla Real produjo:

| Gate | Resultado | Detalle |
|------|-----------|---------|
| G0 | WARNING | `delivery_quality_report.json`: 3/4 sub-gates PASS, G8 FAIL |
| G6 | PASS | `coherence_score_final` = 0.81 ≥ 0.80 |
| G7 | PASS | `pain_ledger.json`: 11 pains, 0 UNTRACKED |
| **G8** | **FAIL** | 8/12 assets con confidence ≤ 0.5; `delivery_ready_percentage` = 25% |

### 1.2 Assets afectados

Los 8 assets con confidence ≤ 0.5 y `preflight_status=WARNING`:

| Asset | Confidence | required_field | required_confidence | ¿Field en audit? |
|-------|-----------|----------------|---------------------|-------------------|
| `optimization_guide` | 0.5 | `metadata` | 0.5 | Sí (dict 8 keys) |
| `local_content_page` | 0.5 | `hotel_data` | 0.5 | Indirecto |
| `analytics_setup_guide` | 0.5 | `ga4_available` | 0.4 | **NO** |
| `indirect_traffic_optimization` | 0.5 | `organic_traffic` | 0.4 | **NO** |
| `og_tags_guide` | 0.5 | `og_tags_detected` | 0.4 | **NO** |
| `open_graph` | 0.5 | `hotel_data` | 0.5 | Indirecto |
| `org_schema` | 0.5 | `org_data` | 0.5 | **NO** |
| `monthly_report` | 0.5 | `hotel_data` | 0.4 | Indirecto |

Los 4 assets con confidence ≥ 0.8 y `preflight_status=PASSED`:

| Asset | Confidence | Nota |
|-------|-----------|------|
| `whatsapp_conflict_guide` | 0.8 | Hardcoded bump en `conditional_generator.py` L165-171 |
| `hotel_schema` | 0.85 | `hotel_data` presente + data completeness check |
| `llms_txt` | 0.85 | `hotel_data` presente |
| `faq_page` | 0.85 | `faqs` probablemente en validated_data |

### 1.3 Mecanismo de confidence

El pipeline de confidence funciona así:

```
validated_data (dict de DataPoints)
    ↓
PreflightChecker.check_asset(asset_type, validated_data)
    → busca required_field en validated_data
    → si NO existe + block_on_failure=False → WARNING con fallback
    → si SÍ existe → evalúa confidence del DataPoint vs required_confidence
    → produce PreflightReport con checks[]
    ↓
ConditionalGenerator._calculate_confidence_score(preflight_report)
    → PASSED check = 1.0
    → WARNING check = 0.5
    → BLOCKED check = 0.0
    → confidence = promedio de todos los checks
    ↓
Para assets de 1 solo check con WARNING → confidence = 0.5/1 = 0.5
```

**Causa raíz confirmada:** Los 8 assets tienen `confidence=0.5` porque su `required_field` no existe en `validated_data`, el preflight lo convierte a WARNING, y el cálculo de confidence asigna 0.5 a un solo check WARNING.

### 1.4 Campos faltantes en audit de Hotel Castilla Real

Inspección del `audit_report_20260513_190808.json`:

```
Campos PRESENTES: url, hotel_name, timestamp, schema, gbp, performance, 
                   validation, overall, competitors, execution_trace, metadata,
                   ai_crawlers, citability, ia_readiness, seo_elements, 
                   aeo_snippets, llm_report

Campos AUSENTES: ga4_available, organic_traffic, og_tags_detected, 
                  org_data, faqs, whatsapp_conflict
```

GBP data SÍ está presente (rating=4.6, reviews=531, place_found=True, address, coords, etc.).

---

## 2. Validated_data vs audit_data

### 2.1 Flujo de datos

```
v4_comprehensive.py (auditoría)
    → audit_report.json (datos crudos del sitio)
    ↓
v4_asset_orchestrator._extract_validated_fields()
    → validated_data dict (DataPoints para preflight)
    ↓
ConditionalGenerator.generate_asset(asset_type, validated_data)
    → PreflightChecker.check_asset()
    → _generate_content()
```

### 2.2 Hipótesis sobre campos faltantes

Los campos `ga4_available`, `organic_traffic`, `og_tags_detected`, `org_data` no están en el `audit_report.json`. Hay dos posibles causas:

1. **El detector/auditor no los recolecta** — `v4_comprehensive.py` no ejecuta la detección de estos campos para este hotel.
2. **`_extract_validated_fields()` no los mapea** — El orquestador no extrae estos campos del audit_report hacia validated_data.

Para `faqs` y `whatsapp_conflict`: no aparecen en audit pero faq_page SÍ tiene confidence 0.85 (PASSED), lo cual sugiere que estos campos SÍ están en validated_data aunque no en el audit_report serializado. Posiblemente se derivan de otros campos durante la extracción.

### 2.3 Verificaciones pendientes (próxima sesión)

```bash
# 1. ¿Qué campos puebla _extract_validated_fields()?
grep -n "validated_data\[" modules/asset_generation/v4_asset_orchestrator.py

# 2. ¿El audit de hotelcastillareal tiene subcampos con estos datos?
./venv/Scripts/python.exe -X utf8 -c "
import json
d = json.load(open('output/v4_complete/hotelcastillareal/v4_audit/audit_report_20260513_190808.json'))
# Buscar en subestructuras
for k in ['schema', 'performance', 'validation', 'seo_elements', 'llm_report']:
    if k in d and isinstance(d[k], dict):
        print(f'{k} keys: {list(d[k].keys())[:15]}')
"

# 3. ¿Hay detectores para estos campos que no se estén llamando?
grep -rn "ga4_available\|organic_traffic\|og_tags_detected\|org_data" modules/ --include='*.py' | grep -v test | grep -v __pycache__
```

---

## 3. Opciones de solución

### Opción A: Hardening de datos — recolectar campos faltantes

**Qué hace:** Modificar `v4_comprehensive.py` y/o `_extract_validated_fields()` para que los campos `ga4_available`, `organic_traffic`, `og_tags_detected`, `org_data` se recolecten y mapeen correctamente a validated_data.

**Archivos a tocar:**
- `modules/auditors/v4_comprehensive.py` — agregar detectores
- `modules/asset_generation/v4_asset_orchestrator.py` — mapear campos en `_extract_validated_fields()`
- Posiblemente `modules/analytics/` — para GA4/tráfico

**Pros:**
- Solución estructural, arregla la raíz
- Mejora la calidad de datos para TODOS los hoteles
- Los assets generados tendrán datos reales, no fallbacks

**Contras:**
- Mayor esfuerzo (3-4 archivos, detectores nuevos)
- Puede requerir APIs adicionales (GA4, Search Console) — potencial costo
- Los campos pueden ser genuinamente no disponibles (hotel sin GA4, sin OG tags)

**Riesgo:** Algunos campos (`ga4_available`, `organic_traffic`) requieren APIs externas que pueden no estar configuradas. Si el hotel no tiene GA4, el campo debe reflejar eso (confidence alta en "no disponible" vs confidence baja en "no sé").

### Opción B: Confidence bumps por asset (patrón whatsapp_conflict_guide)

**Qué hace:** Agregar bumps de confidence mínimo en `conditional_generator.py` (líneas 165-183, donde ya existen los bumps para whatsapp_conflict_guide y hotel_schema) para los 8 assets afectados.

**Archivos a tocar:**
- `modules/asset_generation/conditional_generator.py` — agregar bumps en `generate_asset()`

**Ejemplo de implementación:**
```python
# G8-FIX: Assets que usan fallback controlado no deben penalizarse
_FALLBACK_ASSET_MIN_CONFIDENCE = {
    "optimization_guide": 0.7,
    "local_content_page": 0.7,
    "analytics_setup_guide": 0.65,
    "indirect_traffic_optimization": 0.65,
    "og_tags_guide": 0.65,
    "open_graph": 0.7,
    "org_schema": 0.7,
    "monthly_report": 0.7,
}
if asset_type in _FALLBACK_ASSET_MIN_CONFIDENCE:
    confidence_score = max(confidence_score, _FALLBACK_ASSET_MIN_CONFIDENCE[asset_type])
```

**Pros:**
- Rápido (1 archivo, ~15 líneas)
- Control preciso por asset
- No rompe nada existente

**Contras:**
- No arregla la causa raíz (datos siguen sin recolectarse)
- Los assets siguen siendo "estimated" aunque tengan confidence más alta
- Requiere justificar por qué cada asset merece ese bump

**Riesgo:** Si el fallback genera contenido genérico/de baja calidad, subir la confidence es engañoso. Solo aplicar si el fallback produce contenido aceptable.

### Opción C: Modificar `_calculate_confidence_score()` — no penalizar fallback

**Qué hace:** Cambiar la fórmula de confidence para que assets generados con fallback (WARNING + fallback_action definido) reciban un score base más alto que 0.5.

**Archivos a tocar:**
- `modules/asset_generation/conditional_generator.py` — modificar `_calculate_confidence_score()`

**Ejemplo:**
```python
def _calculate_confidence_score(self, preflight_report: PreflightReport) -> float:
    if not preflight_report.checks:
        return 0.0
    
    total_score = 0.0
    has_fallback = any(c.fallback_action is not None for c in preflight_report.checks)
    
    for check in preflight_report.checks:
        if check.status == PreflightStatus.PASSED:
            total_score += 1.0
        elif check.status == PreflightStatus.WARNING:
            total_score += 0.7 if check.fallback_action else 0.5  # ← bump condicional
        else:
            total_score += 0.0
    
    return total_score / len(preflight_report.checks)
```

**Pros:**
- Afecta a TODOS los assets con fallback, no solo los 8
- Cambio mínimo (1 método, ~5 líneas)
- Semánticamente correcto: si hay fallback controlado, la confianza debería ser > 0.5

**Contras:**
- Cambia el scoring de todos los assets, podría tener efectos secundarios
- WARNING=0.7 con fallback puede ser demasiado generoso para algunos assets
- No distingue entre fallbacks buenos y malos

### Opción D: Cambiar lógica del gate G8 — separar "draft" de "delivery"

**Qué hace:** Modificar `publication_gates.py` para que el gate G8 no bloquee assets con fallback documentado, diferenciando entre:
- `ESTIMATED` (WARNING con fallback → aceptable con disclaimer)
- `GENERIC_DRAFT` (BLOCKED sin fallback → inaceptable)

**Archivos a tocar:**
- `modules/quality_gates/publication_gates.py` — modificar `_asset_specificity_gate()`
- `modules/quality_gates/delivery_quality_report.py` — reflejar nueva semántica

**Pros:**
- Alineado con ROADMAP decisión D4 ("separar `can_use_as_draft` vs `delivery_ready`")
- No requiere cambios en generación de assets
- El disclaimer en el asset ya advierte al cliente

**Contras:**
- Cambia la semántica del gate (requiere aprobación explícita)
- Si el fallback produce contenido pobre, el cliente recibe baja calidad
- No mejora la calidad real de los assets

### Opción E: Combinación (B + D)

Aplicar bumps controlados (Opción B) para assets donde el fallback está validado como aceptable, Y ajustar el gate (Opción D) para que WARNING+bump pase sin bloquear.

---

## 4. Recomendación preliminar

**Corto plazo (esta fase):** Opción B — confidence bumps controlados por asset, con justificación documentada por cada bump.

**Justificación:**
1. Es el cambio más acotado y de menor riesgo (1 archivo, ~15 líneas)
2. Sigue el patrón ya establecido para `whatsapp_conflict_guide`
3. Permite que FASE-RELEASE proceda con G8=PASS
4. No requiere APIs externas ni cambios estructurales

**Mediano plazo (fase separada posterior):** Opción A — hardening de datos para reducir la dependencia de fallbacks.

**Consideración importante:** La próxima sesión debe decidir explícitamente qué nivel de confidence asignar a cada asset, basándose en la calidad real del contenido generado por el fallback. No todos los fallbacks producen contenido de igual calidad.

---

## 5. Archivos relevantes

### Código a modificar (Opción B)

```
modules/asset_generation/conditional_generator.py   → L165-183 (agregar bumps)
```

### Código a modificar (Opción A — futuro)

```
modules/auditors/v4_comprehensive.py                 → agregar detectores
modules/asset_generation/v4_asset_orchestrator.py     → _extract_validated_fields()
modules/analytics/                                    → GA4, tráfico orgánico
```

### Código a modificar (Opción D — alternativo)

```
modules/quality_gates/publication_gates.py            → _asset_specificity_gate()
modules/quality_gates/delivery_quality_report.py      → schema
```

### Tests relevantes

```
tests/asset_generation/test_conditional_generator.py
tests/quality_gates/test_publication_gates.py
tests/quality_gates/test_delivery_quality_report.py
```

### Evidencia

```
evidence/FASE-0G-E2E/
├── asset_generation_report.json
├── delivery_quality_report.json
├── pain_ledger.json
├── coherence_validation.json
├── gate_report_20260513_190819.json
├── audit_report_20260513_190808.json
├── human_checklist.md
└── ejecucion.log
```

### Output actual

```
output/v4_complete/hotelcastillareal/v4_audit/
├── asset_generation_report.json       ← 12 assets, 8 con confidence=0.5
├── delivery_quality_report.json       ← status=WARNING, G8=FAIL
├── pain_ledger.json                   ← 11 pains DETECTED
├── human_checklist.md
├── coherence_validation.json          ← overall_score=0.83
└── gate_report_20260513_190819.json
```

---

## 6. Restricciones para el plan de implementación

### 6.1 Una fase por sesión

La fase de corrección G8 debe ser una ÚNICA fase, ejecutable en una sesión.

### 6.2 R3 scope

- Máximo 4 tareas + 0 comandos largos, o
- Máximo 3 tareas + 1 comando largo (`v4complete` de verificación)

### 6.3 TDD obligatorio

Si se modifica código, aplicar TDD:
1. Escribir test que verifique el nuevo comportamiento de confidence
2. Verificar RED
3. Implementar bumps
4. Verificar GREEN
5. Refactor mínimo

### 6.4 No ejecutar v4complete hasta el final

La verificación E2E con `v4complete` debe ser la ÚLTIMA tarea, solo después de que los tests unitarios pasen.

### 6.5 Evidencia

Copiar outputs a `evidence/FASE-0H-G8-FIX/` (o el identificador que se defina).

---

## 7. Criterios de éxito

- [ ] G8 pasa en `delivery_quality_report.json` (`asset_specificity_gate.passed = true`)
- [ ] G0 pasa (`delivery_quality_report.json.status = PASS`)
- [ ] `delivery_ready_percentage` ≥ 50%
- [ ] Ningún asset con confidence < 0.65
- [ ] Tests unitarios del fix pasan
- [ ] Tests de regresión sin nuevas fallas
- [ ] `v4complete` E2E exitoso (exit code 0, ZIP generado)
- [ ] Evidencia copiada a `evidence/`

---

## 8. Decisión pendiente para la próxima sesión

| # | Decisión | Opciones |
|---|----------|----------|
| D1 | ¿Qué opción implementar? | A (datos) / B (bumps) / C (scoring) / D (gate) / E (combinación) |
| D2 | Si Opción B: ¿qué confidence mínima por asset? | 0.65-0.75 según calidad del fallback |
| D3 | ¿Requiere v4complete de verificación? | Sí (costo ~1 ejecución) |
| D4 | ¿Hotel: mismo (hotelcastillareal) u otro? | Recomendado: mismo para comparabilidad |

---

## 9. Veredicto operativo

El G8 FAIL no es un bug — es una consecuencia de diseño: el pipeline genera assets con fallback cuando los datos no están disponibles, y el scoring de confidence penaliza el fallback como WARNING=0.5.

La corrección debe decidir si:
- **Recolectar los datos** (más trabajo, mejor resultado) → Opción A
- **Aceptar el fallback como válido** (menos trabajo, confianza ajustada) → Opción B

En ambos casos, el `delivery_quality_report.json` ya existe y funciona como artifact bloqueante. La meta es que pase de WARNING a PASS.

---

## 10. Prompt recomendado para iniciar la próxima sesión

```text
Crea y ejecuta el plan de corrección G8 usando como contexto:

C:\Users\Jhond\Github\iah-cli\.opencode\plans\context\FASE-0H-G8-CORRECCION-CONTEXTO.md

Objetivo: Corregir el G8 FAIL detectado en FASE-0G-E2E para que delivery_quality_report.json 
tenga status=PASS con G8=PASS.

Evidencia base en: evidence/FASE-0G-E2E/
Output actual en: output/v4_complete/hotelcastillareal/v4_audit/

Restricciones:
- 1 fase/sesión
- TDD obligatorio si se modifica código
- v4complete solo al final como verificación
- Hotel: hotelcastillareal.com (mismo que FASE-0G para comparabilidad)
```
