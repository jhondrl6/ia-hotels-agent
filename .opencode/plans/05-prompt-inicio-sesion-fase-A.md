# FASE-A: Implementar IA-Readiness Advisory Warnings

**ID**: FASE-A
**Objetivo**: Implementar alerta advisory en diagnóstico + warning persistente en delivery_quality_report cuando IA-Readiness sea Critical
**Dependencias**: Ninguna (primera fase)
**Duración estimada**: 2-3 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

El archivo `.opencode/context/ia-readiness-advisory-vs-blocking.md` (cargado al inicio de esta sesión) documenta que:
- `IA-Readiness` Critical (score < 50) actualmente aparece como una fila más en la tabla de diagnóstico
- El hotelero no entiende que el objetivo comercial de ser citado/recomendado por IA está en riesgo
- No debe bloquear ZIP ni afectar `overall_confidence`
- Sí debe ser visible y persistente como WARNING advisory

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| — | Primera fase del plan |

### Base Técnica Disponible
- Archivos existentes:
  - `modules/auditors/ia_readiness_calculator.py` — calcula score con estados Ready/Needs Work/Critical
  - `modules/auditors/v4_comprehensive.py` — `ia_readiness` es campo opcional/advisory
  - `modules/commercial_documents/v4_diagnostic_generator.py` — genera tabla de métricas IA
  - `modules/commercial_documents/templates/diagnostico_v6_template.md` — template del diagnóstico
  - `modules/quality_gates/delivery_quality_report.py` — reporte de calidad con PASS/WARNING/FAIL
  - `main.py` — pipeline principal, genera delivery_quality_report.json
- Tests base: ~2491 funciones, 192 archivos

---

## Tareas

### T1: Investigar código existente
**Objetivo**: Confirmar los puntos de inserción exactos en los archivos destino

**Archivos a leer**:
- `modules/commercial_documents/v4_diagnostic_generator.py` — función `_build_geo_problems_table()`, buscar dónde se construye la tabla IA y dónde insertar el warning
- `modules/quality_gates/delivery_quality_report.py` — campos actuales de `DeliveryQualityReport`, método `generate()`, `to_dict()`
- `main.py` — dónde se pasa `assessment` al quality generator, cómo se construye el dict

**Criterios de aceptación**:
- [ ] Identificado el lugar exacto en `_build_geo_problems_table()` para insertar `ia_critical_warning`
- [ ] Identificado si `DeliveryQualityReport` soporta un nuevo campo `advisory_warnings`
- [ ] Identificado cómo `main.py` pasa `ia_readiness` al `assessment` (o si hay que agregarlo)
- [ ] Confirmado que el template `diagnostico_v6_template.md` tiene la variable `${ia_metrics_table}` o equivalente

---

### T2: Implementar Cambio 1 — Alerta en diagnóstico
**Objetivo**: Agregar bloquequote de advertencia en DIAGNOSTICO.md cuando IA-Readiness sea Critical

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py`
- `modules/commercial_documents/templates/diagnostico_v6_template.md` (posible, si se necesita nueva variable)

**Lógica**:
```python
ia_critical_warning = ""

if has_ia_readiness:
    ia = audit_result.ia_readiness
    score = getattr(ia, 'overall_score', 0) or 0
    status_text = getattr(ia, 'status', 'Unknown') or 'Unknown'

    if status_text.lower() == "critical" or score < 50:
        ia_critical_warning = (
            "\n> ⚠️ **Alerta IA-Readiness Critical**: este score no bloquea la entrega, "
            "pero indica que el objetivo comercial de ser citado/recomendado por IA "
            "está en riesgo hasta implementar las correcciones propuestas.\n"
        )
```

**Criterios de aceptación**:
- [ ] Si `status=Critical` y `score < 50`, la alerta aparece
- [ ] Si `status=Ready`, la alerta NO aparece
- [ ] Si `status=Needs Work`, la alerta NO aparece
- [ ] La alerta aparece debajo de la tabla de métricas IA
- [ ] La alerta usa formato blockquote markdown (`> ⚠️`)

---

### T3: Implementar Cambio 2 — Advisory warning en delivery_quality_report
**Objetivo**: Agregar campo `advisory_warnings` al `DeliveryQualityReport` y poblarlo cuando IA-Readiness sea Critical

**Archivos afectados**:
- `modules/quality_gates/delivery_quality_report.py`
- `main.py` (posible, para pasar `ia_readiness` al assessment)

**Lógica**:
1. Agregar campo `advisory_warnings: List[dict]` a `DeliveryQualityReport`
2. En `to_dict()`, serializar `advisory_warnings`
3. En `generate()` o en `main.py`, detectar `ia_readiness.status == "critical"` o `overall_score < 50`
4. Agregar entry:
```python
{
    "code": "IA_READINESS_CRITICAL",
    "severity": "WARNING",
    "blocking": False,
    "message": "IA-Readiness Critical: objetivo de citación/recomendación por IA en riesgo sin acción correctiva"
}
```

**Criterios de aceptación**:
- [ ] `DeliveryQualityReport` tiene campo `advisory_warnings: List[dict]`
- [ ] `to_dict()` incluye `advisory_warnings`
- [ ] Cuando `ia_readiness` es Critical, se genera `IA_READINESS_CRITICAL` warning
- [ ] `advisory_warnings` NO bloquea ZIP (status sigue pudiendo ser PASS)
- [ ] Si no hay advisory warnings, el campo es lista vacía `[]`
- [ ] `delivery_quality_report.json` resultante contiene el campo

---

### T4: Tests
**Objetivo**: Agregar tests para ambas funcionalidades

**Archivos de test**:
- `tests/commercial_documents/test_v4_diagnostic_generator.py` (crear o extender)
- `tests/quality_gates/test_delivery_quality_report.py` (extender)

**Casos de test**:

Test 1 (diagnóstico):
- [ ] `IA-Readiness Critical` muestra alerta
- [ ] `IA-Readiness Ready` no muestra alerta
- [ ] `IA-Readiness Needs Work` no muestra alerta pesada
- [ ] Tabla sigue incluyendo filas de Accesibilidad IA, Citabilidad, IA-Readiness

Test 2 (gate/reporte):
- [ ] `IA-Readiness Critical` genera `advisory_warnings` con entry `IA_READINESS_CRITICAL`
- [ ] `advisory_warnings` no bloquea ZIP
- [ ] `status` queda `PASS` si no hay fallas bloqueantes (aunque existan advisory warnings)
- [ ] `FAIL` por G6/G7/EVIDENCE sigue bloqueando como antes (no se degrada)
- [ ] `DeliveryQualityReport.to_dict()` incluye `advisory_warnings`

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_ia_critical_shows_alert` | `tests/commercial_documents/test_v4_diagnostic_generator.py` | Alerta presente cuando status=Critical |
| `test_ia_ready_no_alert` | `tests/commercial_documents/test_v4_diagnostic_generator.py` | Sin alerta cuando status=Ready |
| `test_ia_needs_work_no_alert` | `tests/commercial_documents/test_v4_diagnostic_generator.py` | Sin alerta cuando status=Needs Work |
| `test_advisory_warning_generated` | `tests/quality_gates/test_delivery_quality_report.py` | advisory_warnings contiene IA_READINESS_CRITICAL |
| `test_advisory_warning_non_blocking` | `tests/quality_gates/test_delivery_quality_report.py` | blocking=False, ZIP no aborta |
| `test_fail_still_blocks` | `tests/quality_gates/test_delivery_quality_report.py` | FAIL por G6/G7 sigue bloqueando |

**Comandos de validación**:
```bash
# Python en WSL
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_v4_diagnostic_generator.py tests/quality_gates/test_delivery_quality_report.py -v

# Validación rápida del proyecto
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, ejecutar INMEDIATAMENTE:

```bash
# 1. Registrar en REGISTRY.md
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-A \
    --desc "IA-Readiness Advisory Warnings: alerta en diagnóstico + advisory_warnings en delivery_quality_report" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/quality_gates/delivery_quality_report.py,modules/commercial_documents/templates/diagnostico_v6_template.md" \
    --tests "6" \
    --check-manual-docs

# 2. Regenerar DOMAIN_PRIMER
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer

# 3. Actualizar 09-documentacion-post-proyecto.md (Secciones A, B, D, E)
# 4. Actualizar dependencias-fases.md (marcar FASE-A como ✅)
# 5. Actualizar 06-checklist-implementacion.md
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] T1: Código investigado, puntos de inserción confirmados
- [ ] T2: Alerta en diagnóstico implementada (3 casos: Critical/Ready/Needs Work)
- [ ] T3: Advisory warning en delivery_quality_report implementado
- [ ] T4: 6 tests nuevos pasan
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `dependencias-fases.md` actualizado (FASE-A → ✅)
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado
- [ ] Evidencia preservada en `evidence/fase-A/` si aplica

---

## Restricciones

- **NO modificar** `modules/auditors/ia_readiness_calculator.py` (score ya es correcto)
- **NO modificar** `modules/auditors/v4_comprehensive.py` (arquitectura advisory ya es correcta)
- **NO usar `critical_issues`** para advisory warnings (rechazado por dictamen)
- **NO modificar `overall_confidence`** (solo mide datos, no riesgo comercial)
- **NO hacer que advisory warnings bloqueen ZIP** (blocking=False siempre)
- **NO ejecutar v4complete** en esta fase (se ejecuta en FASE-B)
- **Máximo 60 iteraciones del agente**
