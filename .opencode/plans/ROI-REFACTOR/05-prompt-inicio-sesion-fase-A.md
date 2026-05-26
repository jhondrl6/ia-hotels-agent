# FASE-A: Bloqueantes de output al cliente

**ID**: FASE-A
**Objetivo**: Corregir 3 fugas críticas de información interna/placeholder que dañan la credibilidad comercial del output al cliente.
**Dependencias**: Ninguna (fase inicial)
**Duración estimada**: 1-2 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

El ROI_AUDIT.md (2026-05-26) identificó 3 problemas bloqueantes que hacen que el documento NO sea enviable al dueño del hotel:

1. **"⚠️ Alertas Comerciales" visibles al cliente**: El bloque de validación de `CommercialGateValidator` se inyecta directamente al `document_content` sin verificar audiencia (L374-386 en proposal, L514-526 en diagnostic). El validador fue diseñado para alertar al **operador**, pero se implementó como apéndice al **documento del cliente**.

2. **Placeholder de testimonios vacío**: `propuesta_v6_template.md:171` tiene hardcodeado `[Espacio para casos de éxito...]` sin `{% if testimonials %}`. El cliente ve corchetes literales.

3. **Nota de pain_ratio engañosa**: L755-762 dice "el 41% representa la porción del dolor financieramente abordable con IAO" cuando en realidad pain_ratio = price / expected_loss es un artifact del min_price floor, no un % semántico.

### Evidencia verificada en código vivo

```python
# v4_proposal_generator.py:374-386 — alertas inyectadas sin audience check
if not commercial_report.blocking_passed:
    alert_section = "\n---\n## ⚠️ Alertas Comerciales\n\n"
    # ... blocking_failures ...
    document_content += alert_section  # ← INCONDICIONAL, sin document_audience

# v4_proposal_generator.py:755-762 — nota de pain_ratio engañosa
'pain_ratio_note': (
    f"De su pérdida mensual estimada, el {pain_ratio:.0%} "
    f"representa la porción del dolor financieramente abordable con IAO. "
    # ↑ FALSO: pain_ratio es price/expected_loss, no "% IAO"
)
```

### Estado de Fases Anteriores

|| Fase | Estado | Nota ||
|------|--------|-------|------|
| PROPUESTA-COMERCIAL FASE-A a RELEASE | ✅ COMPLETADAS (v4.53.0) | — |
| **ROI-REFACTOR FASE-0** | ✅ COMPLETADA (2026-05-26) | **Decisión: Opción E** — piloto $250K + crédito a retainer + success fee capped. Pricing de activación documentado en `09-documentacion-post-proyecto.md` §F. Esta fase ejecuta fixes técnicos sin tocar estructura comercial. |

---

## Tareas

### Tarea 1: Agregar `document_audience` switch en proposal generator

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

**Paso 1.1**: Agregar parámetro `document_audience: str = "client"` a `generate()` (L260-277)

**Paso 1.2**: Condicionar inyección de alertas (L374-386):
```python
# ANTES
if not commercial_report.blocking_passed:
    alert_section = ...
    document_content += alert_section

# DESPUÉS
if not commercial_report.blocking_passed:
    if document_audience == "internal":
        alert_section = ...
        document_content += alert_section
    else:
        logging.warning("Commercial gates BLOCKING (hidden from client): %s", ...)
```

**Paso 1.3**: Opcional — generar archivo `_INTERNAL.md` cuando `document_audience == "internal"` (o mantener solo logging para el caso "client")

**Archivos a modificar**: `v4_proposal_generator.py` (L260-277 signature, L374-386 conditional)

**Criterios de aceptación**:
- [ ] Con `document_audience="client"` (default), NO se inyectan alertas
- [ ] Con `document_audience="internal"`, SÍ se inyectan alertas
- [ ] El warning se loguea en ambos casos
- [ ] Sin cambios en el resto del flujo

### Tarea 2: Agregar `document_audience` switch en diagnostic generator

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`

**Paso 2.1**: Agregar parámetro `document_audience: str = "client"` a `generate()`

**Paso 2.2**: Condicionar inyección de alertas (L514-526) igual que Tarea 1

**Criterios de aceptación**:
- [ ] Mismo comportamiento que proposal generator
- [ ] Sin regresiones en diagnóstico

### Tarea 3: Eliminar placeholder de testimonios si está vacío

**Archivo**: `modules/commercial_documents/templates/propuesta_v6_template.md` L169-171

**Cambio**:
```markdown
<!-- ANTES -->
### 🏨 Hoteles que ya confiaron en nosotros

> *[Espacio para casos de éxito — hoteles del Eje Cafetero con resultados medibles]*

<!-- DESPUÉS -->
{% if testimonials %}
### 🏨 Hoteles que ya confiaron en nosotros

{% for t in testimonials %}
> *{{ t.quote }}*
> — {{ t.hotel_name }}, {{ t.result }}
{% endfor %}
{% endif %}
```

**NOTA**: Si el sistema no tiene testimonios todavía, la sección completa se omite. Esto es mejor que mostrar un placeholder vacío que grita "plantilla genérica".

**Paso 3.1**: Agregar `'testimonials': testimonials if testimonials else []` al diccionario de datos en el generator (cerca de L722-730)

**Criterios de aceptación**:
- [ ] Sin testimonios → sección NO renderizada
- [ ] Con testimonios → sección renderizada con datos reales
- [ ] Sin placeholder `[Espacio para...]` en el output

### Tarea 4: Corregir nota semántica de pain_ratio

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py` L755-762

**Cambio**:
```python
# ANTES
'pain_ratio_note': (
    f"**Nota de proyección**: De su pérdida mensual estimada, el {pain_ratio:.0%} "
    f"representa la porción del dolor financieramente abordable con IAO. "
    # ...
),

# DESPUÉS
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

**Criterios de aceptación**:
- [ ] Ya NO dice "porción del dolor financieramente abordable con IAO"
- [ ] Dice "relación entre inversión y pérdida mensual estimada"
- [ ] Resto del texto (efectividad, proyección conservadora) se preserva

---

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Validación rápida | `python3 scripts/run_all_validations.py --quick` | 3/5+ checks pass |
| Import test proposal | `python3 -c "from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator; print('OK')"` | OK |
| Import test diagnostic | `python3 -c "from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator; print('OK')"` | OK |
| Smoke test generate | `python3 -c "from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator; g = V4ProposalGenerator(); print('init OK')"` | OK |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: Marcar FASE-A como ✅ Completada con fecha y evidencia
2. **`06-checklist-implementacion.md`**: Marcar items A1-A4 como ✅
3. **`09-documentacion-post-proyecto.md`**: Agregar módulos en Sección A, funcionalidades en B
4. Ejecutar:
```bash
cmd.exe /c "venv\Scripts\python.exe scripts\log_phase_completion.py \
    --fase FASE-A \
    --desc \"ROI-REFACTOR: document_audience switch + eliminar placeholder testimonios + corregir nota pain_ratio\" \
    --archivos-mod \"modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/templates/propuesta_v6_template.md\" \
    --tests 0 \
    --check-manual-docs"
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] `document_audience` parameter en `generate()` de proposal generator
- [ ] `document_audience` parameter en `generate()` de diagnostic generator
- [ ] Alertas condicionadas a `document_audience == "internal"`
- [ ] Placeholder testimonios eliminado del template
- [ ] Condicional `{% if testimonials %}` en template
- [ ] Nota de pain_ratio corregida semánticamente
- [ ] `run_all_validations.py --quick` pasa
- [ ] Import tests OK
- [ ] `dependencias-fases.md` actualizado
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- NO modificar `commercial_gate.py` (el validador funciona bien)
- NO ejecutar v4complete
- NO modificar `scenario_calculator.py`
- NO cambiar la fórmula del ROI
- NO modificar `pricing_calculator.py`
- Máximo 60 iteraciones de agente
