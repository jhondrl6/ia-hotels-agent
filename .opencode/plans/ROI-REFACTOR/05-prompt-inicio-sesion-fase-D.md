# FASE-D: Pulido final (Anexo APIs + Tiers + Nota pain_ratio)

**ID**: FASE-D
**Objetivo**: Simplificar Anexo Técnico APIs a párrafo de transparencia + documentar evidence_tier vs precision_tier + agregar nota explicativa pain_ratio 20% vs 41%.
**Dependencias**: FASE-3 completada (ADR scraper conectado, versión dinámica). **FASE-0 completada (Opción E)** — decisión comercial en `09-documentacion-post-proyecto.md` §F.
**Duración estimada**: 1-2 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

Los 3 fixes restantes del ROI_AUDIT.md son de pulido — no bloquean la entrega pero mejoran la transparencia y trazabilidad:

1. **Anexo Técnico APIs visible (Fix 8, §4)**: `propuesta_v6_template.md:218-229` muestra "OpenRouter, Gemini, Perplexity" con costos en USD. El dueño del hotel no necesita ver esto — es ruido técnico. Reemplazar por párrafo de transparencia.

2. **evidence_tier vs precision_tier sin documentar (Fix 9, §0.9)**: `financial_scenarios.json` tiene `"evidence_tier": "B"` y `"precision_tier": "C"` sin explicación de la relación entre ambos. La inconsistencia (precision_tier=C dice "no mostrar dinero exacto" pero el output muestra "$3.741.696 COP") no es detectada por quality gates.

3. **Sin nota explicativa pain_ratio 20% vs 41% (Fix 10, §0.6)**: El diagnóstico usa pain_ratio=20% (default conservador) mientras la propuesta usa ~41% (del pricing engine). La divergencia es intencional pero no está explicada en el output. Agregar nota en el diagnóstico.

### Evidencia en código

```markdown
<!-- propuesta_v6_template.md:218-229 — Anexo APIs visible -->
## 📋 Anexo Técnico: Infraestructura IAO
| API | Propósito | Costo estimado/mes |
|-----|-----------|-------------------|
| OpenRouter | ... | $5-15 USD |
| Gemini | ... | $0 USD |
| Perplexity | ... | $20 USD |
```

```json
// financial_scenarios.json
"evidence_tier": "B",
"precision_tier": "C",
"can_show_exact_money": false
// ↑ inconsistencia: precision_tier=C pero el output muestra COP exactos
```

---

## Tareas

### Tarea 1: Simplificar Anexo Técnico APIs

**Archivo**: `modules/commercial_documents/templates/propuesta_v6_template.md` L218-229

**Cambio**: Reemplazar tabla de APIs por párrafo de transparencia:

```markdown
<!-- ANTES -->
## 📋 Anexo Técnico: Infraestructura IAO
| API | Propósito | Costo estimado/mes |
|-----|-----------|-------------------|
| OpenRouter | Consultas LLM | $5-15 USD |
...

<!-- DESPUÉS -->
## 📋 Transparencia tecnológica

Nuestro análisis utiliza múltiples modelos de inteligencia artificial
(ChatGPT, Gemini, Perplexity) para evaluar cómo los motores de búsqueda
y asistentes de IA ven su hotel en internet. El costo de estas consultas
lo absorbemos nosotros como parte del servicio — usted no paga nada adicional.
```

**Paso 1.1**: Si la tabla de APIs se genera dinámicamente en el generator (no solo en el template), modificar también `v4_proposal_generator.py`

**Criterios de aceptación**:
- [ ] Sin tabla de "API | Propósito | Costo" en el output
- [ ] Párrafo de transparencia en lenguaje de negocio
- [ ] Sin menciones a "OpenRouter", "Gemini", "Perplexity" en el output al cliente

### Tarea 2: Documentar relación evidence_tier vs precision_tier

**Archivo**: El JSON se genera en `main.py` ≈L1866-1898 (GAP-4). Documentar en código y/o en el JSON.

**Paso 2.1**: Agregar comentario/documentación en `main.py` donde se establecen ambos tiers:
```python
# evidence_tier (A-E): calidad de los datos fuente (A = GA4 real, B = benchmarks, C = estimados)
# precision_tier (A-C): precisión de los cálculos derivados (A = datos reales, C = estimados)
# Relación: evidence_tier es upstream (datos), precision_tier es downstream (cálculos)
# Un evidence_tier B puede producir precision_tier C si los cálculos usan supuestos
```

**Paso 2.2**: Agregar un campo `tier_explanation` al `financial_scenarios.json`:
```json
"tier_explanation": {
  "evidence_tier": "B — Basado en benchmarks regionales y datos públicos del sitio web, sin GA4",
  "precision_tier": "C — Los cálculos usan supuestos de shift (10%) e IA boost (5%) no validados con datos reales",
  "relationship": "evidence_tier B limita precision_tier a C porque sin GA4 los supuestos no son validables"
}
```

**Paso 2.3**: Verificar si `precision_tier = C` + `can_show_exact_money = false` debería redondear los COP en el output (ej: "$3.7M COP" en vez de "$3.741.696 COP"). Si aplica, implementar en el generator.

**Criterios de aceptación**:
- [ ] Documentación clara de qué mide cada tier
- [ ] Relación entre tiers explicada
- [ ] `tier_explanation` en el JSON (o documentación equivalente)

### Tarea 3: Agregar nota explicativa pain_ratio 20% vs 41%

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py` ≈L1077 (donde se usa `pain_ratio_default`)

**Paso 3.1**: Agregar placeholder en el template del diagnóstico explicando la divergencia:
```markdown
**Nota sobre la proyección**: El 20% utilizado en este diagnóstico es una estimación
regional conservadora. En la propuesta personalizada, este porcentaje se ajusta según
el perfil específico de su hotel (canal directo, ocupación, tarifas).
```

**Paso 3.2**: Agregar la nota al diccionario de placeholders del diagnostic generator (cerca de L1077)

**Criterios de aceptación**:
- [ ] Diagnóstico explica que el 20% es conservador y preliminar
- [ ] Referencia a que la propuesta usará el % real del hotel
- [ ] Sin confundir al cliente con dos números diferentes sin explicación

---

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Validación rápida | `python3 scripts/run_all_validations.py --quick` | 3/5+ checks pass |
| Import tests | `python3 -c "from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator; from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator; print('OK')"` | OK |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: Marcar FASE-D como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items D1-D3 como ✅
3. **`09-documentacion-post-proyecto.md`**: Agregar cambios
4. Ejecutar:
```bash
cmd.exe /c "venv\Scripts\python.exe scripts\log_phase_completion.py \
    --fase FASE-D \
    --desc \"ROI-REFACTOR: Simplificar Anexo APIs + documentar evidence/precision tiers + nota pain_ratio 20vs41\" \
    --archivos-mod \"modules/commercial_documents/templates/propuesta_v6_template.md,modules/commercial_documents/v4_diagnostic_generator.py,main.py\" \
    --tests 0 \
    --check-manual-docs"
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] Anexo APIs reemplazado por párrafo de transparencia
- [ ] Sin nombres de APIs visibles al cliente
- [ ] evidence_tier vs precision_tier documentados
- [ ] `tier_explanation` o equivalente en JSON
- [ ] Nota pain_ratio 20% vs 41% en diagnóstico
- [ ] `run_all_validations.py --quick` pasa
- [ ] `dependencias-fases.md` actualizado
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- NO modificar `commercial_gate.py`
- NO ejecutar v4complete (eso es FASE-E)
- NO cambiar la fórmula del ROI
- NO modificar `scenario_calculator.py`
- El párrafo de transparencia debe ser 3-5 líneas máximo
- Máximo 60 iteraciones de agente
