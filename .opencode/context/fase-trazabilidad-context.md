# FASE-TRAZABILIDAD: Contexto Consolidado — Items Pendientes y Decisiones

**Creado**: 2026-04-25
**Origen**: Consolidación de `d1-warning-readiness-context.md` + `fase-trazabilidad-pendientes-context.md`
**Estado**: Post-commit `16fa26b`
**Próxima sesión sugerida**: FASE-TRAZABILIDAD-REFINEMENT

---

## Résumen de lo completado en FASE-TRAZABILIDAD-PATCH

La fase anterior implementó 5 fixes verificados en 1 ejecución v4complete (Amazilia Hotel):

| Fix | Resultado |
|-----|-----------|
| T1: BUG-02 financial_validity WARNING | ✅ Gate reporta WARNING con default_sources en details |
| T2A: Header "## 🔍 Trazabilidad" | ✅ Visible en L112 del diagnóstico |
| T2B: Sección "## ✅ Validación de Calidad" | ✅ Visible en L104 del diagnóstico |
| T3: seo_score persiste en JSON | ✅ v4_complete_report.json tiene seo_score: 25 |
| T4: geo_flow_result timing | ✅ Archivo existe en amazilia_hotel/v4_audit/ |

**Cambio fundamental**: El sistema dejó de ocultar → ahora transparenta. Pero la credibilidad sigue limitada por datos de entrada (onboarding no ejecutado), no por código.

---

## Items Pendientes

### ITEM 1: D1 — WARNING en Publication Readiness

**Estado**: PENDIENTE — requiere decisión

**Descripción**: El fix BUG-02 hace que `financial_validity` retorne `WARNING` con `passed=True`. Pero `check_publication_readiness()` en `publication_gates.py` L979-982 usa solo `passed` (bool), así que el readiness sigue siendo `READY_FOR_PUBLICATION` aunque haya warnings.

**Código actual** (`modules/quality_gates/publication_gates.py` L979-982):
```python
results = run_publication_gates(assessment)
blocking_gates = [r for r in results if not r.passed]
ready = len(blocking_gates) == 0
```

**Opciones**:

**Opción A — WARNING = REQUIRES_REVIEW (conservador)**:
```python
blocking_gates = [
    r for r in results
    if not r.passed or r.status == GateStatus.WARNING
]
ready = len([r for r in results if not r.passed]) == 0
status = "READY_FOR_PUBLICATION" if ready else "REQUIRES_REVIEW"
```
- Efecto: Si cualquier gate tiene WARNING, el diagnóstico muestra "REQUIRES_REVIEW"
- Implicación: Mayor rigor, más fricción para publicación

**Opción B — WARNING visible pero no bloqueante (actual)**:
El gate WARNING ya mejora el mensaje individual en `gate_report.json`. El readiness sigue `READY_FOR_PUBLICATION`. No se requiere cambio de código.

**Opción C — WARNING en summary pero no en readiness status**:
Mantener `ready=True` pero incluir los warnings en el JSON del readiness report para que el diagnóstico los mencione.

**Criterios de decisión**:
1. ¿Qué nivel de rigor quieres para publicación?
2. ¿Quieres que el cliente vea "REQUIRES_REVIEW" por defaults financieros (Tier C)?
3. ¿Un warning sobre Tier C justifica bloquear/marcar publicación?

**Archivo a modificar**: `modules/quality_gates/publication_gates.py` — método `check_publication_readiness()`

---

### ITEM 2: D2 — Visibilidad del Tier C en cuerpo del documento

**Estado**: PENDIENTE — requiere decisión de contenido

**Problema**: El diagnóstico muestra el Tier C en frontmatter + blockquote, pero NO lo hace visible en el encabezado de pérdida financiera:

```
### Comisión OTA Actual (verificable)
**$2.610.000 COP/mes**           ← Sin indicador de Tier
Desglose:
- Estimación basada en escenario meta esperada
- Fuente del dato: benchmark
```

Un cliente que lee "$2.6M/mes de pérdida" sin contexto puede inferir datos reales cuando son benchmark regional.

**Opciones**:

**Opción A — Disclaimer mínimo en encabezado**:
Modificar template para que cuando `financial_evidence_tier == "C"`:
```markdown
**$2.610.000 COP/mes** *(estimado — Tier C: basado en benchmark regional)*
```

**Opción B — Banner dedicado sobre la tabla de escenarios (más visible)**:
```markdown
> ⚠️ **Nivel de evidencia: Tier C**
> Estas cifras se basan en benchmark regional + datos limitados de la web.
> Para precisión, ejecute onboarding con datos operativos reales.
```
Insertar después de `## 💰 Impacto Financiero` y antes de `### Comisión OTA Actual`.

**Opción C — Sin cambios**:
Mantener el disclaimer en footer/blockquote como está. El código ya transparenta Tier en metadata. La decisión de enfatizar más es comercial.

**Criterios de decisión**:
- ¿Qué nivel de visibilidad quiere para Tier C en el cuerpo?
- ¿Debe decir explícitamente "cifras estimadas" o "basado en benchmark"?
- ¿Cambiar "Comisión OTA Actual" → "Pérdida Estimada por OTA"?

**Archivo a modificar**: `modules/commercial_documents/templates/diagnostico_v6_template.md`

---

### ITEM 3: D3 — geo_score = 0/100 — ¿Timing, bug o dato real?

**Estado**: PENDIENTE — requiere investigación

**Problema**: El diagnóstico muestra:
```
| Salud Técnica GEO | 0/100 | unknown | 🔴 |
```

El archivo `geo_flow_result.json` existe pero el score es `0/100` con `unknown`.

**Hipótesis**:
1. **Timing**: El diagnóstico se generó ANTES de que `v4_asset_orchestrator` calculara el geo_flow real
2. **Dato real**: El sitio realmente tiene 0 SEO GEO detectable
3. **Bug**: El parser en `v4_diagnostic_generator.py` no lee correctamente el archivo

**Verificación sugerida**:
```bash
# Ver contenido del geo_flow_result
cat output/v4_complete/amazilia_hotel/v4_audit/geo_flow_result.json

# Comparar con lo que muestra el diagnóstico
grep -A5 "Salud Técnica GEO" output/v4_complete/01_DIAGNOSTICO_*.md
```

**Decisiones según resultado**:
- Si timing: ¿reordenar pipeline para que geo_score se calcule antes del diagnóstico?
- Si dato real (0 real): cambiar "unknown" → "0/100 — Sin datos GEO detectados"
- Si bug: revisar parser en `v4_diagnostic_generator.py`

**Archivos a investigar**:
- `output/v4_complete/amazilia_hotel/v4_audit/geo_flow_result.json`
- `modules/commercial_documents/v4_diagnostic_generator.py`

---

### ITEM 4: D4 — Gap entre coherence_score (0.89) y asset_confidence (8 below threshold)

**Estado**: PENDIENTE — requiere decisión de display

**Problema**:
```
🔒 Gate de Coherencia:
   Score calculado: 0.89 (umbral: 0.8)
   Checks: 6/6 pasados
   [OK] Coherencia aceptable — Generando propuesta completa

🔒 Publication Gates:
   ✅ asset_confidence: 8 asset(s) below confidence threshold (0.7)
```

El diagnóstico muestra coherence_score = 0.89 y dice "Coherencia aceptable". Pero 8/10 assets están below threshold. Puede dar impresión falsa de que los assets son confiables.

**Opciones**:

**Opción A — No cambiar (decisión de negocio)**:
El coherence gate pasa (0.89 > 0.8). Los assets con WARNING se entregan con disclaimer.

**Opción B — Nota en diagnóstico**:
Cuando `asset_confidence < threshold`, agregar línea:
```
⚠️ 8 assets con confianza baja (0.7) — Incluidos con disclaimer en paquete
```

**Opción C — Gate más riguroso**:
Cambiar `asset_confidence` de WARNING a BLOCKED si más de N assets están below threshold.

**Criterios de decisión**:
- ¿Debe el diagnóstico transparentar que los assets tienen baja confianza?
- ¿Quieres que `asset_confidence` bloquee si demasiados assets están below threshold?

**Archivo a modificar**: `modules/quality_gates/publication_gates.py` (para Opción C) + `modules/commercial_documents/v4_diagnostic_generator.py` (para Opción B)

---

## Resumen de Decisiones

| # | Item | Tipo | ¿Código o decisión? |
|---|------|------|---------------------|
| D1 | WARNING en readiness | Operativo | Código + decisión negocio |
| D2 | Tier C en cuerpo | Comercial | Decisión contenido |
| D3 | geo_score = 0 | Técnico | Investigación → decisión |
| D4 | coherence vs asset_confidence | Comercial | Decisión display |

---

## Flujo Recomendado para Próxima Sesión

1. **D1** (código, ~30 min) — resolver el if/warning en readiness
2. **D2** (contenido, ~20 min) — decidir nivel de visibilidad Tier C
3. **D3** (investigación, ~20 min) — verificar geo_flow_result.json y determinar si es timing/bug/dato real
4. **D4** (display, ~15 min) — decidir cómo mostrar gap coherence/asset_confidence

D2 y D4 son mejoras de **credibilidad comercial**. D1 es mejora de **rigor operativo**. D3 es **investigación**.

---

## Archivos Relevantes

```
modules/quality_gates/publication_gates.py     # D1, D4
modules/commercial_documents/templates/diagnostico_v6_template.md  # D2
modules/commercial_documents/v4_diagnostic_generator.py  # D3, D4
output/v4_complete/amazilia_hotel/v4_audit/geo_flow_result.json  # D3
```
