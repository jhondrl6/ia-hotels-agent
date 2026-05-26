# FASE-D: Credibilidad — Labels (V-2) + Jerga (V-3) + Onboarding (A-1) + Confidence (CROSS-5)

**ID**: FASE-D
**Objetivo**: Eliminar 4 degradadores de credibilidad: unificar labels de estado, expandir el gate anti-jerga, eliminar fallback frágil de onboarding, y vincular confidence scores a servicios.
**Dependencias**: FASE-C (tabla de servicios ya tiene mapping de brechas)
**Duración estimada**: 2-3 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

La auditoría identificó 4 problemas que, aunque no bloquean, degradan la credibilidad profesional:

- **V-2**: 4 instancias de "⚠️ En preparación" — 3 con tilde, 1 sin tilde. Suena a que el servicio no está listo.
- **V-3**: El gate CG-TECH-JARGON solo detecta 9 términos. NO detecta OpenRouter, Perplexity, Gemini, GA4_PROPERTY_ID, GSC_SITE_URL, UTM, iah-cli, iahotels.co. Además, la tabla de costos IAO expone nombres de providers al dueño.
- **A-1**: `has_onboarding` tiene un fallback de búsqueda de string que activa incorrectamente el perdón de ROI negativo si el template menciona "onboarding" en cualquier contexto.
- **CROSS-5**: La propuesta marca 5 de 10 entregables como "⚠️ En preparación" pero el asset `optimization_guide` tiene confidence=0.5 — muy por debajo del umbral 0.65.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada (asumido) |
| FASE-B | ✅ Completada (asumido) |
| FASE-C | ✅ Completada (asumido) |

---

## Tareas

### Tarea 1: Unificar labels "⚠️ En preparación" (V-2)

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

**Cambio**: Las 4 instancias deben unificarse. Opción recomendada: cambiar a "En proceso de activación — Semana 2" para comunicar progreso en lugar de indefinición.

```python
# L1019, L1047, L1104 — cambiar tilde + texto
estado = "En proceso de activación — Semana 2"

# L1297 — corregir tilde + unificar
return ("En proceso de activación — Semana 2", "Datos pendientes del cliente")
```

**Criterios de aceptación**:
- [ ] 4 instancias unificadas al mismo string
- [ ] Sin "⚠️ En preparación" ni "⚠️ En preparacion" residual
- [ ] El nuevo texto no rompe anchos de columna en la tabla

### Tarea 2: Expandir CG-TECH-JARGON + Mover tabla IAO (V-3)

**Archivos**:
- `modules/quality_gates/commercial_gate.py` L85-88 — `TECH_JARGON_TERMS`
- `modules/commercial_documents/templates/propuesta_v6_template.md` L149-158

**Cambio A — Agregar 8 términos al gate**:
```python
TECH_JARGON_TERMS = [
    "Schema", "AEO", "IAO", "Open Graph", "NAP", "Rich Snippets",
    "schema.org", "JSON-LD", "markup estructurado",
    # PROPUESTA-COMERCIAL FASE-D: términos adicionales
    "OpenRouter", "Perplexity", "Gemini", "GA4_PROPERTY_ID",
    "GSC_SITE_URL", "UTM", "iah-cli", "iahotels.co",
]
```

**Cambio B — Mover tabla IAO a anexo técnico**:
La tabla de costos IAO (L149-158 del template) expone nombres de providers y costos por queries al dueño. Mover esta tabla a una nueva sección "Anexo Técnico: Infraestructura IAO" al final del documento.

**Criterios de aceptación**:
- [ ] Gate detecta los 8 nuevos términos
- [ ] Tabla IAO movida fuera de la vista gerencia (secciones 1-6)
- [ ] Referencia desde la sección original al anexo ("ver Anexo Técnico")

### Tarea 3: Eliminar fallback de búsqueda de string en has_onboarding (A-1)

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py` L355-359

**Cambio**:
```python
# ANTES
has_onboarding = False
if pricing_result is not None:
    has_onboarding = getattr(pricing_result, 'is_onboarding', False)
if not has_onboarding:
    has_onboarding = 'onboarding' in document_content.lower()  # ELIMINAR

# DESPUÉS
has_onboarding = False
if pricing_result is not None:
    has_onboarding = getattr(pricing_result, 'is_onboarding', False)
```

**Criterios de aceptación**:
- [ ] Sin búsqueda de string residual
- [ ] `has_onboarding` solo depende de `pricing_result.is_onboarding`
- [ ] Gate CG-ROI-NEGATIVE no se activa falsamente

### Tarea 4: Vincular confidence score a servicios (CROSS-5)

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py` — `_generate_dynamic_services_table()`

**Objetivo**: Agregar columna "Confianza" con el confidence score del asset asociado a cada servicio. Si confidence < 0.65, marcar con ⚠️.

**Datos disponibles**: Los assets tienen `confidence` en el `asset_plan` que ya se pasa a la tabla de servicios. Verificar acceso.

**Criterios de aceptación**:
- [ ] Cada servicio muestra su confidence score (o "—" si no aplica)
- [ ] Scores < 0.65 marcados con ⚠️
- [ ] `optimization_guide` (0.5) visiblemente advertido

---

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Gate jargon | `pytest tests/quality_gates/ -v -k "jargon or tech" --timeout=60` | Detecta nuevos términos |
| Tests de propuesta | `pytest tests/commercial_documents/ -v -k "proposal" --timeout=60` | Sin regresiones |
| Validación rápida | `python scripts/run_all_validations.py --quick` | 4/4+ checks |

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-D como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items D1-D5 como ✅
3. **`09-documentacion-post-proyecto.md`**: Agregar cambios
4. Ejecutar:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-D \
    --desc "V-2: labels unificados + V-3: gate jargon expandido + A-1: sin fallback string + CROSS-5: confidence en servicios" \
    --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/quality_gates/commercial_gate.py,modules/commercial_documents/templates/propuesta_v6_template.md" \
    --tests "0" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] V-2: 4 labels unificados a "En proceso de activación — Semana 2"
- [ ] V-3: 8 términos nuevos en TECH_JARGON_TERMS
- [ ] V-3: Tabla IAO movida a anexo técnico
- [ ] A-1: Sin fallback de búsqueda de string en has_onboarding
- [ ] CROSS-5: Confidence score visible en tabla de servicios
- [ ] `run_all_validations.py --quick` pasa
- [ ] `dependencias-fases.md` actualizado
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- NO modificar `scenario_calculator.py`
- NO ejecutar v4complete
- NO eliminar la tabla IAO — solo moverla de sección
- Máximo 60 iteraciones de agente
