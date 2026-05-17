# Contexto Validado: IA-Readiness Score — ¿Advisory o Bloqueante?

**Archivo:** `.opencode/context/ia-readiness-advisory-vs-blocking.md`  
**Fecha original:** 2026-05-16  
**Actualización:** 2026-05-16  
**Trigger:** Evaluación de coherencia vs. guía Google AI Optimization + revisión de código vivo.  
**Dictamen:** Sí amerita intervención, pero como **WARNING advisory visible y persistente**, no como bloqueo duro de entrega.

---

## 1. Resumen ejecutivo

La tesis del contexto original es estratégicamente válida: si iah-cli vende una promesa de valor asociada a que el hotel sea **citado/recomendado por IAs**, un `IA-Readiness` en estado `Critical` no debe quedar reducido a un icono genérico o a un print de consola.

Sin embargo, el contexto original estaba parcialmente desactualizado y sobredimensionaba la solución recomendada:

- Ya existe `delivery_quality_report.json` como gate pre-ZIP en el pipeline.
- Ya existe un sistema de gates con distinción `PASS` / `WARNING` / `FAIL`.
- `IA-Readiness` está correctamente modelado como `ADVISORY`; convertirlo en bloqueo duro mezclaría riesgo comercial con fallas estructurales de entrega.
- La intervención pertinente no es abortar ZIP ni contaminar `overall_confidence`, sino hacer explícito el riesgo comercial cuando el score sea crítico.

**Decisión recomendada:** implementar una alerta advisory no bloqueante cuando `ia_readiness.status == "Critical"` o `overall_score < 50`, surfaced en el diagnóstico y persistida en el reporte de calidad/gates.

---

## 2. Estado real verificado en código

### 2.1 IA-Readiness Calculator

Archivo:

`modules/auditors/ia_readiness_calculator.py`

El módulo `IAReadinessCalculator` produce tres estados:

| Status | Score | Lógica |
|--------|-------|--------|
| `Ready` | `>= 70` | Preparación adecuada |
| `Needs Work` | `50–69` | Requiere mejoras |
| `Critical` | `< 50` | Riesgo fuerte para discoverability/citación IA |

Evidencia:

```python
if overall >= 70:
    status = "Ready"
elif overall >= 50:
    status = "Needs Work"
else:
    status = "Critical"
```

El score se compone de:

| Componente | Peso |
|-----------|------|
| `schema_quality` | 22% |
| `crawler_access` | 22% |
| `citability` | 23% |
| `llms_txt` | 9% |
| `brand_signals` | 14% |
| `ga4_indirect` | 10% |

Cuando GA4 no está disponible, el peso se redistribuye entre los demás componentes.

---

### 2.2 IA-Readiness en V4AuditResult

Archivo:

`modules/auditors/v4_comprehensive.py`

`IA-Readiness` está modelado explícitamente como campo opcional/advisory:

```python
# IA Readiness (optional, advisory)
ia_readiness: Optional[IAReadinessReport] = None
```

También se serializa en `to_dict()`:

```python
if self.ia_readiness:
    result["ia_readiness"] = {
        "overall_score": self.ia_readiness.overall_score,
        "components": self.ia_readiness.components,
        "status": self.ia_readiness.status,
        "actionable_items": self.ia_readiness.actionable_items,
    }
```

---

### 2.3 IA-Readiness NO afecta `overall_confidence`

Archivo:

`modules/auditors/v4_comprehensive.py`

`_calculate_overall_confidence()` usa solamente:

- `schema`
- `gbp`
- `validation`

No consume `ia_readiness`.

Esto es correcto arquitectónicamente: `overall_confidence` debe medir confiabilidad de datos/base auditada, no probabilidad comercial de ser citado por IA.

---

### 2.4 IA-Readiness NO entra en `critical_issues`

Archivo:

`modules/auditors/v4_comprehensive.py`

`_identify_critical_issues()` detecta:

- ausencia de Hotel schema,
- schema inválido,
- conflicto de WhatsApp,
- GBP geo_score bajo,
- performance móvil pobre.

No considera `ia_readiness`.

Esto evita que métricas advisory contaminen la lista de issues críticos estructurales.

---

### 2.5 Diagnóstico actual sí muestra IA-Readiness, pero sin alerta semántica pesada

Archivo:

`modules/commercial_documents/v4_diagnostic_generator.py`

En `_build_geo_problems_table()` se renderiza la fila:

```python
rows.append(f"| IA-Readiness | {score:.1f}/100 | {status_text} | {status_icon} |")
```

La tabla aparece bajo la sección del template:

`modules/commercial_documents/templates/diagnostico_v6_template.md`

```md
### Métricas de Acceso para IA

${ia_metrics_table}
```

Limitación actual:

- Un score `33/100` con status `Critical` se muestra como fila de tabla.
- No traduce el riesgo al lenguaje comercial: “el objetivo de ser citado/recomendado por IA está comprometido hasta implementar correcciones”.
- El hotelero puede no entender que este es el problema central respecto a la promesa IAO/AEO.

---

### 2.6 El contexto original estaba desactualizado sobre delivery_quality_report

El contexto original decía:

> No hay `delivery_quality_report.json` en el pipeline; no hay gate de calidad.

Eso ya no es correcto.

Evidencia real:

Archivo:

`main.py`

```python
# FASE-0E: Delivery Quality Report — bloqueante pre-ZIP
quality_report_path = v4_audit_dir / "delivery_quality_report.json"
delivery_quality_report = quality_generator.generate(hotel_id, v4_audit_dir)
quality_generator.save(delivery_quality_report, quality_report_path)
```

Si el reporte queda en `FAIL`, se aborta ZIP:

```python
if delivery_quality_report and delivery_quality_report.status == "FAIL":
    print("ZIP ABORTED: Delivery quality report status is FAIL.")
    delivery_zip_path = None
```

Archivo:

`modules/quality_gates/delivery_quality_report.py`

El reporte define:

- `PASS`
- `WARNING`
- `FAIL`
- `blocking: bool`
- `human_review_items`
- gates G6/G7/G8/EVIDENCE

Reglas actuales:

| Status | Efecto |
|--------|--------|
| `FAIL` | bloquea ZIP/publicación |
| `WARNING` | visible, no bloqueante |
| `PASS` | entrega continúa |

Por tanto, ya existe el lugar natural para persistir un advisory warning sin romper arquitectura.

---

## 3. Qué dice la guía Google AI Optimization

La guía de Google AI Optimization es coherente con el enfoque actual del proyecto:

- Las mejores prácticas SEO siguen siendo relevantes.
- La calidad y utilidad para visitantes reales siguen siendo centrales.
- No se requiere “chunking” especial para IA.
- No se requieren archivos propietarios de IA.
- No se deben fabricar menciones.
- Los crawlers como `Google-Extended` deben tratarse correctamente si el sitio quiere exposición en features IA.
- El contenido citable, factual y estructurado sigue siendo la base.

Conclusión: no hay contradicción estructural entre iah-cli y la guía.

El problema no es de alineación con Google, sino de **transparencia comercial del output**: si el score crítico contradice la promesa central, el usuario debe verlo con claridad.

---

## 4. Análisis estratégico profundizado

### 4.1 La promesa comercial cambia la severidad percibida

En un auditor SEO genérico, `IA-Readiness Critical` podría ser solo una métrica más.

En iah-cli, el objetivo comercial incluye que el hotel mejore su capacidad de ser:

- citado por motores de IA,
- recomendado por asistentes,
- entendido por buscadores generativos,
- descubierto como entidad confiable.

Por eso, un score crítico no es un simple dato técnico: es una señal de que el objetivo de valor está en riesgo.

Esto no significa que deba bloquear la entrega. Significa que debe ser visible, persistente y semánticamente explícito.

---

### 4.2 Advisory no significa oculto

La categoría `ADVISORY` debe interpretarse así:

- No bloquea el cálculo de `overall_confidence`.
- No invalida el diagnóstico.
- No impide generar assets.
- No aborta ZIP.
- Sí debe informar riesgo comercial cuando contradice la tesis del producto.

Por tanto, “advisory” y “warning pesado” no son categorías excluyentes.

La distinción correcta es:

| Concepto | Debe aplicar a IA-Readiness Critical? |
|---------|----------------------------------------|
| Bloquear ZIP | No |
| Bajar `overall_confidence` | No |
| Agregar a `critical_issues` estructurales | No recomendado |
| Mostrar alerta clara en diagnóstico | Sí |
| Persistir warning en reporte de calidad/gates | Sí |
| Incluir en checklist humano si aplica | Sí, opcional |

---

### 4.3 Riesgo de meterlo en `critical_issues`

La Opción C original proponía usar `critical_issues`.

Eso tiene una ventaja: ya hay infraestructura para mostrar esos issues en stdout y en algunos outputs.

Pero tiene riesgos:

1. `critical_issues` se usa aguas abajo como señal de problemas críticos del audit.
2. Puede afectar conteos como `critical_problems_count`.
3. Puede cambiar `top_problems` y narrativa comercial.
4. Puede mezclar fallas estructurales verificables con riesgo estratégico/advisory.
5. Puede generar la impresión de que la entrega está defectuosa aunque los assets estén correctamente generados.

Dictamen técnico: no usar `critical_issues` salvo que se renombre o se cree una categoría separada como `advisory_warnings`.

---

### 4.4 Lugar natural para la intervención

El lugar más correcto no es `overall_confidence`, ni `critical_issues`, ni un bloqueo ZIP.

El lugar más correcto es doble:

1. **Diagnóstico visible para el hotelero**  
   `modules/commercial_documents/v4_diagnostic_generator.py`  
   Sección: `### Métricas de Acceso para IA`

2. **Reporte persistente de calidad/gates**  
   `modules/quality_gates/delivery_quality_report.py` o `gate_report.json` generado en `main.py`

Esto mantiene la separación:

- Documento comercial: explica impacto.
- Reporte de calidad: preserva trazabilidad.
- Gates bloqueantes: siguen enfocados en coherencia/cobertura/evidencia.

---

## 5. Evaluación de opciones

### Opción A — WARNING liviano en DIAGNOSTICO.md

**Pertinencia:** Alta.  
**Riesgo:** Bajo.  
**Invasión:** Mínima.  
**Recomendada:** Sí.

Descripción:

Agregar una alerta debajo de la tabla de métricas IA cuando `IA-Readiness` sea crítico.

Mensaje sugerido:

```md
> ⚠️ **Alerta IA-Readiness Critical**: este score no bloquea la entrega, pero indica que el objetivo comercial de ser citado/recomendado por IA está en riesgo hasta implementar las correcciones propuestas.
```

Ventaja:

- Lo ve el hotelero.
- No cambia arquitectura.
- No afecta confidence.
- No bloquea ZIP.

Limitación:

- Si solo queda en el diagnóstico, no queda como señal machine-readable para gates/reportes.

---

### Opción B — WARNING persistente en reporte/manifest

**Pertinencia:** Alta.  
**Riesgo:** Bajo-medio.  
**Invasión:** Baja.  
**Recomendada:** Sí, pero preferiblemente en `delivery_quality_report.json` o `gate_report.json`, no en `MANIFEST.json`.

El contexto original proponía `MANIFEST.json`. Sin embargo, hoy `MANIFEST.json` representa metadata de archivos del ZIP. El contrato de salud de entrega ya vive en:

- `delivery_quality_report.json`
- `gate_report.json`
- `human_checklist.md`

Mejor ubicación:

```json
"advisory_warnings": [
  {
    "code": "IA_READINESS_CRITICAL",
    "severity": "WARNING",
    "blocking": false,
    "message": "IA-Readiness Critical: objetivo de citación/recomendación por IA en riesgo sin acción correctiva"
  }
]
```

Ventaja:

- Persistente.
- Machine-readable.
- Compatible con `WARNING` no bloqueante.
- Puede alimentar checklist humano.

Limitación:

- Requiere que `main.py` inyecte `ia_readiness` en el `assessment` o que el generator pueda leerlo desde algún JSON de audit.

---

### Opción C — Gate WARNING pesado vía `critical_issues`

**Pertinencia:** Parcial.  
**Riesgo:** Medio.  
**Invasión real:** Mayor de lo que indica el contexto original.  
**Recomendada:** No como está escrita.

Problemas:

- El contexto original decía que cuesta “~5 líneas”, pero no es tan simple si se hace bien.
- `ia_readiness_result` se calcula después de `_identify_critical_issues()`, por lo que habría que reordenar lógica o pasar el resultado a la función.
- `critical_issues` tiene consumidores downstream.
- Puede contaminar métricas de severidad y narrativa de problemas críticos.

Reformulación aceptable:

- Crear `advisory_warnings`, no usar `critical_issues`.
- Mantener `blocking=False`.
- Persistirlo como warning comercial, no como fallo estructural.

---

## 6. Dictamen final

### ¿Es pertinente intervenir?

Sí.

### ¿Debe bloquear entrega?

No.

### ¿Debe afectar `overall_confidence`?

No.

### ¿Debe entrar en `critical_issues`?

No recomendado.

### ¿Debe quedar visible para usuario/hotelero?

Sí.

### ¿Debe quedar persistido en artefactos de QA?

Sí.

### Severidad

Media-alta por transparencia comercial, no por bug técnico estructural.

### Tipo de intervención

Quirúrgica, advisory, visible y persistente.

### Recomendación concreta

Implementar combinación de:

- **Opción A:** alerta clara en diagnóstico.
- **Opción B reformulada:** warning no bloqueante en `delivery_quality_report.json` o `gate_report.json`.

Rechazar por ahora:

- bloqueo ZIP,
- modificación de `overall_confidence`,
- uso directo de `critical_issues`,
- tratar `IA-Readiness Critical` como `FAIL`.

---

## 7. Propuesta de implementación recomendada

### 7.1 Cambio 1 — alerta en diagnóstico

Archivo objetivo:

`modules/commercial_documents/v4_diagnostic_generator.py`

Función:

`_build_geo_problems_table()`

Lógica sugerida:

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

Luego agregar `ia_critical_warning` al final de la tabla.

Tests requeridos:

- Si `status=Critical` y `score < 50`, la alerta aparece.
- Si `status=Ready`, la alerta no aparece.
- Si `status=Needs Work`, la alerta no aparece.

---

### 7.2 Cambio 2 — warning persistente en gate/report

Opción preferida:

1. En `main.py`, incluir `ia_readiness` dentro de `assessment`:

```python
"ia_readiness": {
    "overall_score": audit_result.ia_readiness.overall_score,
    "status": audit_result.ia_readiness.status,
    "components": audit_result.ia_readiness.components,
    "actionable_items": audit_result.ia_readiness.actionable_items,
} if audit_result and audit_result.ia_readiness else None,
```

2. En `gate_report.json`, agregar advisory warning si aplica:

```python
advisory_warnings = []
ia_readiness = assessment.get("ia_readiness")
if ia_readiness and (
    ia_readiness.get("status", "").lower() == "critical"
    or ia_readiness.get("overall_score", 100) < 50
):
    advisory_warnings.append({
        "code": "IA_READINESS_CRITICAL",
        "severity": "WARNING",
        "blocking": False,
        "message": "IA-Readiness Critical: objetivo de citación/recomendación por IA en riesgo sin acción correctiva",
    })
```

3. Incluir en el JSON:

```python
"advisory_warnings": advisory_warnings,
```

Alternativa:

Agregar soporte formal a `DeliveryQualityReport`:

- nuevo campo `advisory_warnings: List[dict]`
- incluir en `to_dict()`
- mantener `status=WARNING` pero `blocking=False` cuando solo existan advisory warnings.

Esta alternativa es más limpia a largo plazo, pero toca más tests.

---

### 7.3 Cambio 3 — human checklist opcional

Si se actualiza `delivery_quality_report`, `HumanChecklistGenerator` podría incluir un ítem no bloqueante:

```md
- [ ] Revisar IA-Readiness Critical: explicar al cliente que la entrega incluye assets correctivos, pero el impacto depende de implementación.
```

Esto debe contar dentro del límite actual de checklist humano (`<= 10 items`).

---

## 8. Tests recomendados

### Diagnóstico

Agregar o extender tests en:

`tests/quality_gates/test_publication_gates.py`

o crear test específico para `V4DiagnosticGenerator`.

Casos:

1. `IA-Readiness Critical` muestra alerta.
2. `IA-Readiness Ready` no muestra alerta.
3. `IA-Readiness Needs Work` no muestra alerta pesada.
4. Tabla sigue incluyendo `Accesibilidad IA`, `Citabilidad`, `IA-Readiness`.

### Reporte/gate

Agregar tests en:

`tests/quality_gates/test_delivery_quality_report.py`

o tests para `gate_report` si se implementa allí.

Casos:

1. `IA-Readiness Critical` genera `advisory_warnings`.
2. `advisory_warnings` no bloquea ZIP.
3. `status` queda `WARNING` si no hay fallas bloqueantes y existe warning advisory.
4. `FAIL` por G6/G7/EVIDENCE sigue bloqueando como antes.

---

## 9. Verificación ejecutada durante este análisis

Comando ejecutado:

```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_delivery_quality_report.py tests/auditors/test_ia_readiness_calculator.py -q
```

Resultado:

```text
25 passed, 8 warnings in 0.72s
```

Observación:

- `pytest` global no estaba disponible en WSL.
- El proyecto usa el Python del venv Windows:

```bash
./venv/Scripts/python.exe -m pytest ...
```

---

## 10. Hallazgos corregidos respecto al contexto original

| Claim original | Estado validado | Ajuste |
|---------------|-----------------|--------|
| No hay `delivery_quality_report.json` en pipeline | Incorrecto / desactualizado | Sí existe en `main.py` y `modules/quality_gates/delivery_quality_report.py` |
| No hay gate de calidad | Incorrecto / desactualizado | Hay gate pre-ZIP; `FAIL` aborta ZIP |
| Opción C cuesta ~5 líneas | Subestimado | Requiere reordenar cálculo o pasar `ia_readiness`, más revisión downstream |
| Mejor lugar para warning: `critical_issues` | Riesgoso | Mejor `advisory_warnings` o warning en reportes |
| Render principal de IA-Readiness en propuesta | Parcial / incompleto | El diagnóstico actual usa `v4_diagnostic_generator.py` y es el lugar prioritario |
| IA-Readiness Critical no aparece en documento hotelero | Parcialmente incorrecto | Sí aparece como fila/status, pero no con alerta semántica suficiente |

---

## 11. Metadata de decisión

```yaml
scorecard_actual:
  ia_readiness_critical:
    visible_en_diagnostico: true
    alerta_semantica_comercial: false
    persistido_como_warning_qa: false
    bloquea_zip: false
    afecta_overall_confidence: false

dictamen:
  intervencion_pertinente: true
  urgencia: media_alta
  tipo: advisory_warning_visible_y_persistente
  bloquear_entrega: false
  afectar_overall_confidence: false
  usar_critical_issues: false

implementacion_recomendada:
  - diagnostico_warning
  - advisory_warnings_en_gate_report_o_delivery_quality_report
  - tests_no_bloqueo_zip

no_hacer:
  - abortar_zip_por_ia_readiness_critical
  - bajar_overall_confidence
  - tratar_critical_como_fail
  - mezclar_con_critical_issues_estructurales

archivos_relevantes:
  - modules/auditors/ia_readiness_calculator.py
  - modules/auditors/v4_comprehensive.py
  - modules/commercial_documents/v4_diagnostic_generator.py
  - modules/commercial_documents/templates/diagnostico_v6_template.md
  - modules/quality_gates/delivery_quality_report.py
  - main.py
  - tests/auditors/test_ia_readiness_calculator.py
  - tests/quality_gates/test_delivery_quality_report.py
```

---

## 12. Conclusión final

`IA-Readiness Critical` debe seguir siendo advisory en términos de arquitectura, pero no puede ser silencioso en términos comerciales.

La intervención pertinente es convertirlo en una advertencia explícita, persistente y no bloqueante:

- visible en `DIAGNOSTICO.md`,
- rastreable en reportes de calidad/gates,
- sin contaminar `overall_confidence`,
- sin abortar ZIP,
- sin degradar la entrega si los assets correctivos fueron generados correctamente.

Esta solución preserva la arquitectura agent-first actual y mejora la transparencia comercial del pipeline.