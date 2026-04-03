---
description: Validador integral de calidad del flujo v4. Fase A (pre-generación): coherencia estructural. Fase B (post-entrega): QA de entregables.
version: 1.0.0
---

# Skill: V4 Quality Validator

> [!NOTE]
> **Fase A (antes de assets)**: "Validar coherencia", "Verificar antes de generar"
> **Fase B (después de delivery)**: "valida los entregables", "QA post-venta", "revisar diagnóstico"

## Arquitectura de Dos Fases

| Fase | Cuándo | Qué valida | Output |
|------|--------|-----------|--------|
| **A: Coherencia Pre-generación** | Después de proposal, antes de assets | Alineación paquete-diagnóstico, ROI, WhatsApp, ADR | `coherence_report.json` |
| **B: QA Post-entrega** | Después de generar el kit de entrega | Placeholders vacíos, consistencia documental, sello QA | `qa_report.json` |

---

## FASE A: Coherencia Pre-Generación

### Pre-requisitos
- [ ] Diagnosis data (brechas, fugas, scores)
- [ ] Proposal data (paquete recomendado, ROI, precio)
- [ ] Hotel metadata (nombre, URL, validación cruzada)
- [ ] **Configuración cargada desde `.conductor/guidelines.yaml`**

### A1. Extract Diagnosis Summary
```python
import json

diagnosis = json.loads('''{{diagnosis_json}}''')
proposal = json.loads('''{{proposal_json}}''')

coherence_checks = {
    'diagnosis_brechas_count': len(diagnosis.get('brechas_criticas', [])),
    'diagnosis_fugas_count': len(diagnosis.get('fugas_gbp', [])),
    'diagnosis_perdida': diagnosis.get('perdida_mensual', 0),
    'proposal_paquete': proposal.get('paquete_recomendado', ''),
    'proposal_precio': proposal.get('precio', 0),
    'proposal_roi': proposal.get('roi_meses', 0)
}
print(json.dumps(coherence_checks, indent=2))
```

### A2. Validate Package-Diagnosis Alignment
```python
import json

paquete = '{{proposal_paquete}}'.lower()
brechas = json.loads('''{{brechas_json}}''')

package_capabilities = {
    'starter geo': ['geo_basico', 'seo_local'],
    'pro aeo': ['geo_basico', 'seo_local', 'ia_basics', 'automation_light'],
    'pro aeo plus': ['geo_basico', 'seo_local', 'ia_basics', 'automation_light', 'schema_advanced'],
    'elite': ['geo_avanzado', 'seo_tecnico', 'ia_completa', 'automation_full', 'revpar_optimization'],
    'elite plus': ['todo', 'priority_support', 'dedicated_manager']
}

capabilities = package_capabilities.get(paquete, [])
inconsistencias = []

for brecha in brechas:
    tipo = brecha.get('tipo', '').lower()
    if tipo in ['revpar', 'adr_optimization', 'pricing_strategy'] and 'revpar_optimization' not in capabilities:
        if 'elite' not in paquete:
            inconsistencias.append(f'Brecha tipo {tipo} requiere Elite/Elite PLUS')

print(json.dumps({
    'coherent': len(inconsistencias) == 0,
    'inconsistencias': inconsistencias,
    'paquete_capabilities': capabilities
}, indent=2, ensure_ascii=False))
```

### A3. Validate ROI Credibility
```python
import json, yaml

with open('.conductor/guidelines.yaml', 'r') as f:
    config = yaml.safe_load(f)

price_config = config.get('price_validation', {})
min_ratio = price_config.get('min_ratio', 3.0)
max_ratio = price_config.get('max_ratio', 6.0)
ideal_ratio = price_config.get('ideal_ratio', 4.5)

perdida = {{diagnosis_perdida}}
precio = {{proposal_precio}}
roi_meses = {{proposal_roi}}

if perdida > 0 and precio > 0:
    expected_roi = precio / (perdida * 0.3)
    roi_credible = abs(roi_meses - expected_roi) <= 2
else:
    roi_credible = False

if perdida > 0:
    investment_ratio = precio / perdida
    ratio_valid = min_ratio <= investment_ratio <= max_ratio
    ratio_deviation = abs(investment_ratio - ideal_ratio)
    max_deviation = max(max_ratio - ideal_ratio, ideal_ratio - min_ratio)
    ratio_score = max(0.0, 1.0 - (ratio_deviation / max_deviation)) if max_deviation > 0 else 1.0
else:
    ratio_valid = False
    investment_ratio = 0
    ratio_score = 0.0

print(json.dumps({
    'roi_credible': roi_credible,
    'investment_ratio_valid': ratio_valid,
    'investment_ratio': round(investment_ratio, 2),
    'ratio_score': round(ratio_score, 2),
    'ratio_range': f'{min_ratio}x-{max_ratio}x',
    'recommendation': 'APPROVED' if (roi_credible and ratio_valid) else 'REVIEW'
}, indent=2))
```

### A4. Validate Cross-Reference Consistency
```python
import json, yaml

with open('.conductor/guidelines.yaml', 'r') as f:
    config = yaml.safe_load(f)

coherence_config = config.get('v4_coherence_rules', {})
whatsapp_config = coherence_config.get('whatsapp_verified', {})
whatsapp_threshold = whatsapp_config.get('confidence_threshold', 0.9)
financial_config = coherence_config.get('financial_data_validated', {})
financial_threshold = financial_config.get('confidence_threshold', 0.7)

# WhatsApp triangulation
whatsapp_web = '{{whatsapp_web}}'
whatsapp_gbp = '{{whatsapp_gbp}}'
whatsapp_input = '{{whatsapp_input}}'
fuentes_whatsapp = [w for w in [whatsapp_web, whatsapp_gbp, whatsapp_input] if w]

if len(fuentes_whatsapp) >= 2:
    matches = sum(1 for i in range(len(fuentes_whatsapp)) for j in range(i+1, len(fuentes_whatsapp)) if fuentes_whatsapp[i] == fuentes_whatsapp[j])
    total_comparisons = len(fuentes_whatsapp) * (len(fuentes_whatsapp) - 1) / 2
    match_pct = matches / total_comparisons if total_comparisons > 0 else 0
    whatsapp_confidence = match_pct
    whatsapp_verified = match_pct >= whatsapp_threshold
else:
    whatsapp_confidence = 0.5 if len(fuentes_whatsapp) == 1 else 0.0
    whatsapp_verified = False

conflictos = []
if not whatsapp_verified and len(fuentes_whatsapp) > 0:
    conflictos.append(f'WhatsApp no verificado: confidence={whatsapp_confidence:.2f}, threshold={whatsapp_threshold}')
if whatsapp_web and whatsapp_gbp and whatsapp_web != whatsapp_gbp:
    conflictos.append(f'WhatsApp diferente: web={whatsapp_web}, gbp={whatsapp_gbp}')

# ADR consistency
adr_benchmark = {{adr_benchmark}}
adr_input = {{adr_input}}
if adr_input > 0 and adr_benchmark > 0:
    adr_diff = abs(adr_input - adr_benchmark) / adr_benchmark
    adr_confidence = max(0.0, 1.0 - adr_diff)
    if adr_confidence < 0.5:
        conflictos.append(f'ADR conflicto: confidence={adr_confidence:.2f}')
    elif adr_confidence < financial_threshold:
        conflictos.append(f'ADR baja confianza: confidence={adr_confidence:.2f}')

if len(conflictos) == 0:
    confidence_level = 'VERIFIED'
elif whatsapp_confidence < 0.5 or (adr_input > 0 and adr_benchmark > 0 and adr_confidence < 0.5):
    confidence_level = 'CONFLICT'
else:
    confidence_level = 'ESTIMATED'

print(json.dumps({
    'cross_reference_valid': len(conflictos) == 0,
    'conflictos': conflictos,
    'whatsapp_confidence': round(whatsapp_confidence, 2),
    'confidence_level': confidence_level
}, indent=2, ensure_ascii=False))
```

### A5. Generate Coherence Report
```python
import json
from datetime import datetime

report = {
    'timestamp': datetime.utcnow().isoformat(),
    'hotel': '{{hotel_name}}',
    'url': '{{url}}',
    'phase': 'A',
    'coherence_score': {{coherence_score}},
    'checks': {
        'package_alignment': {{package_alignment_result}},
        'roi_credibility': {{roi_credibility_result}},
        'cross_reference': {{cross_reference_result}}
    },
    'overall_status': '{{overall_status}}',
    'recommendation': '{{recommendation}}'
}

with open('{{output_dir}}/coherence_report.json', 'w') as f:
    json.dump(report, f, indent=2)
print('✅ Coherence report generated')
```

### Criterios Éxito Fase A
- [ ] Score de coherencia >= 0.8
- [ ] Price/Loss ratio entre 3x-6x
- [ ] WhatsApp verificado con confidence >= 0.9
- [ ] Sin conflictos de validación cruzada críticos
- [ ] Reporte generado

---

## FASE B: QA Post-Entrega

### Pre-requisitos
- [ ] Directorio de salida con archivos generados
- [ ] Datos originales del hotel

### B1. Escaneo de Placeholders
Buscar cualquier texto en formato `{{...}}` o `[N/D]` en los archivos del directorio de salida.

```bash
grep -rn '{{\|\\[N/D\\]' output/{{hotel_id}}/
```

### B2. Triangulación de ROI
Confirmar que la "pérdida mensual" y el "paquete recomendado" coincidan en el Diagnóstico Ejecutivo y la Propuesta.

*Validación*: Datos financieros coherentes en todo el kit de entrega.

### B3. Generar Sello de Calidad
```python
import json
from datetime import datetime

qa_report = {
    'timestamp': datetime.utcnow().isoformat(),
    'hotel': '{{hotel_name}}',
    'phase': 'B',
    'checks': {
        'no_placeholders': {{placeholder_check_passed}},
        'roi_consistent': {{roi_consistent}},
        'financial_validated': {{financial_double_check}}
    },
    'overall': 'QA_PASSED' if all_checks_pass else 'NEEDS_REVIEW',
    'recommendation': 'El consultor puede proceder con el cliente.' if all_checks_pass else 'Revisar campos indicados antes de entregar.'
}

with open('{{output_dir}}/qa_report.json', 'w') as f:
    json.dump(qa_report, f, indent=2)
```

### Criterios Éxito Fase B
- [ ] Kit de entrega 100% coherente
- [ ] Sin placeholders visibles
- [ ] Cálculos financieros validados doblemente

---

## Plan de Recuperación (Fases A y B)

**Fase A (coherencia):**
- Si score < 0.8: revisión manual antes de generar assets
- Si hay conflictos de validación cruzada: bloquear y reportar

**Fase B (QA):**
- Si hay inconsistencias: indicar campos que requieren edición manual
- Si error de lógica mayor: recomendar reiniciar etapa de IA

## Criterios de Selección

| Trigger | Fase Ejecutada |
|---------|---------------|
| "Validar coherencia", "Verificar antes de generar" | Fase A |
| "valida los entregables", "QA post-venta", "revisar diagnóstico" | Fase B |
| "Validar v4complete post-cambios" | Fase A + Fase B |

