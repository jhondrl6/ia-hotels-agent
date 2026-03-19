---
description: Generate assets conditionally based on preflight checks and confidence gates.
---

# Skill: V4 Conditional Asset Generator

> [!NOTE]
> **Trigger**: Execute ONLY after coherence validation passes and confidence gates are met.

## Pre-requisitos (Contexto)
- [ ] Coherence validation PASSED (score >= 0.8)
- [ ] Cross-validation data (WhatsApp, ADR) con confidence >= 0.9
- [ ] Financial scenarios calculated
- [ ] Package selected and validated

## Fronteras (Scope)
- **Hará**: Generar assets solo si pasan gates de calidad. Aplicar nomenclatura según confidence.
- **NO Hará**: No generar assets con datos CONFLICT. No bypass preflight checks.

## Pasos de Ejecución

### 1. Run Preflight Checks
// turbo
python -c "
import json

# Define preflight gates
preflight_gates = {
    'whatsapp': {
        'required_confidence': 0.9,
        'current_confidence': {{whatsapp_confidence}},
        'status': '{{whatsapp_status}}',
        'value': '{{whatsapp_value}}'
    },
    'faq_page': {
        'required_confidence': 0.7,
        'current_confidence': {{faq_confidence}},
        'status': '{{faq_status}}'
    },
    'hotel_schema': {
        'required_confidence': 0.8,
        'current_confidence': {{schema_confidence}},
        'status': '{{schema_status}}'
    },
    'coherence': {
        'required_confidence': 0.8,
        'current_confidence': {{coherence_score}},
        'status': '{{coherence_status}}'
    }
}

# Check each gate
gate_results = {}
all_passed = True

for gate_name, gate_config in preflight_gates.items():
    passed = gate_config['current_confidence'] >= gate_config['required_confidence']
    gate_results[gate_name] = {
        'passed': passed,
        'confidence': gate_config['current_confidence'],
        'required': gate_config['required_confidence'],
        'status': 'PASS' if passed else 'BLOCK'
    }
    if not passed:
        all_passed = False

result = {
    'all_passed': all_passed,
    'gates': gate_results,
    'generation_allowed': all_passed
}

print(json.dumps(result, indent=2, ensure_ascii=False))
"

*Validación*: Todos los preflight gates evaluados.

### 2. Determine Nomenclature
// turbo
python -c "
import json

preflight = json.loads('''{{preflight_result}}''')
gates = preflight['gates']

# Determine nomenclature based on lowest confidence
confidences = [g['confidence'] for g in gates.values()]
min_confidence = min(confidences)

if min_confidence >= 0.9:
    nomenclature = 'PASSED'
    filename_prefix = ''
elif min_confidence >= 0.7:
    nomenclature = 'WARNING'
    filename_prefix = 'ESTIMATED_'
else:
    nomenclature = 'BLOCKED'
    filename_prefix = 'BLOCKED_'

result = {
    'nomenclature': nomenclature,
    'filename_prefix': filename_prefix,
    'min_confidence': min_confidence,
    'generation_allowed': nomenclature != 'BLOCKED'
}

print(json.dumps(result, indent=2))
"

*Validación*: Nomenclatura determinada según confidence mínima.

### 3. Generate WhatsApp Button (Conditional)
// turbo
python -c "
whatsapp_confidence = {{whatsapp_confidence}}
whatsapp_value = '{{whatsapp_value}}'
hotel_name = '{{hotel_name}}'
filename_prefix = '{{filename_prefix}}'

if whatsapp_confidence >= 0.9 and whatsapp_value:
    # Generate WhatsApp button HTML
    whatsapp_button_html = f'''<!-- WhatsApp Button for {hotel_name} -->
<!-- Confidence: {whatsapp_confidence} | Status: VERIFIED -->
<a href=\"https://wa.me/{whatsapp_value.replace('+', '')}\" 
   class=\"whatsapp-button\" 
   target=\"_blank\"
   rel=\"noopener noreferrer\">
   <img src=\"/icons/whatsapp.svg\" alt=\"WhatsApp\" />
   <span>Chatea con nosotros</span>
</a>

<style>
.whatsapp-button {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 12px 20px;
    background: #25D366;
    color: white;
    text-decoration: none;
    border-radius: 24px;
    font-family: system-ui, sans-serif;
}}
.whatsapp-button img {{
    width: 20px;
    height: 20px;
}}
</style>'''

    filename = f'{filename_prefix}boton_whatsapp.html'
    
    with open('{{output_dir}}/' + filename, 'w', encoding='utf-8') as f:
        f.write(whatsapp_button_html)
    
    print(f'✅ Generated: {filename} (confidence: {whatsapp_confidence})')
else:
    print(f'⛔ Skipped: boton_whatsapp.html (confidence {whatsapp_confidence} < 0.9)')
"

*Validación*: WhatsApp button generado solo si confidence >= 0.9.

### 4. Generate FAQ Schema (Conditional)
// turbo
python -c "
import json

faq_confidence = {{faq_confidence}}
filename_prefix = '{{filename_prefix}}'

if faq_confidence >= 0.7:
    # Generate FAQ Schema.org markup
    faq_schema = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {
                '@type': 'Question',
                'name': f'¿Dónde está ubicado {{hotel_name}}?',
                'acceptedAnswer': {
                    '@type': 'Answer',
                    'text': f'{{hotel_name}} está ubicado en {{ubicacion}}.'
                }
            },
            {
                '@type': 'Question',
                'name': f'¿Cómo puedo contactar a {{hotel_name}}?',
                'acceptedAnswer': {
                    '@type': 'Answer',
                    'text': f'Puedes contactarnos vía WhatsApp al {{whatsapp_value}} o a través de nuestro sitio web.'
                }
            }
        ]
    }
    
    filename = f'{filename_prefix}faq_schema.json'
    with open('{{output_dir}}/' + filename, 'w', encoding='utf-8') as f:
        json.dump(faq_schema, f, indent=2, ensure_ascii=False)
    
    print(f'✅ Generated: {filename} (confidence: {faq_confidence})')
else:
    print(f'⛔ Skipped: faq_schema.json (confidence {faq_confidence} < 0.7)')
"

*Validación*: FAQ Schema generado solo si confidence >= 0.7.

### 5. Generate Hotel Schema (Conditional)
// turbo
python -c "
import json

schema_confidence = {{schema_confidence}}
filename_prefix = '{{filename_prefix}}'

if schema_confidence >= 0.8:
    # Generate Hotel Schema.org markup
    hotel_schema = {
        '@context': 'https://schema.org',
        '@type': 'Hotel',
        'name': '{{hotel_name}}',
        'url': '{{url}}',
        'telephone': '{{whatsapp_value}}',
        'address': {
            '@type': 'PostalAddress',
            'addressLocality': '{{ubicacion}}',
            'addressCountry': 'CO'
        }
    }
    
    filename = f'{filename_prefix}hotel_schema.json'
    with open('{{output_dir}}/' + filename, 'w', encoding='utf-8') as f:
        json.dump(hotel_schema, f, indent=2, ensure_ascii=False)
    
    print(f'✅ Generated: {filename} (confidence: {schema_confidence})')
else:
    print(f'⛔ Skipped: hotel_schema.json (confidence {schema_confidence} < 0.8)')
"

*Validación*: Hotel Schema generado solo si confidence >= 0.8.

### 6. Generate Proposal Document (Always)
python -c "
import json
from datetime import datetime
from pathlib import Path

output_dir = Path('{{output_dir}}')
output_dir.mkdir(parents=True, exist_ok=True)

# Generate proposal with confidence annotations
proposal_content = f'''# Propuesta Comercial - {{hotel_name}}

**Fecha:** {datetime.now().strftime('%Y-%m-%d')}  
**URL:** {{url}}  
**Paquete Recomendado:** {{paquete_recomendado}}

---

## Diagnóstico

{{hotel_name}} presenta oportunidades de mejora en su presencia digital que representan una pérdida estimada de:

- **Escenario Conservador:** ${{conservative_monthly:,.0f}} COP/mes
- **Escenario Realista:** ${{realistic_monthly:,.0f}} COP/mes  
- **Escenario Optimista:** ${{optimistic_monthly:,.0f}} COP/mes

> ⚠️ **Nota:** Estas cifras son estimaciones basadas en benchmarks de la región. Los resultados reales pueden variar.

## Solución Propuesta

**Paquete:** {{paquete_recomendado}}  
**Inversión:** ${{precio:,.0f}} COP  
**ROI Esperado:** {{roi_meses}} meses

## Nivel de Confianza

| Dato | Confianza | Status |
|------|-----------|--------|
| WhatsApp | {whatsapp_confidence*100:.0f}% | {{whatsapp_status}} |
| FAQ Schema | {faq_confidence*100:.0f}% | {{faq_status}} |
| Hotel Schema | {schema_confidence*100:.0f}% | {{schema_status}} |

---

*Generado por IA Hoteles Agent v4.0*
'''

filename = f'{filename_prefix}propuesta.md'
with open(output_dir / filename, 'w', encoding='utf-8') as f:
    f.write(proposal_content)

print(f'✅ Generated: {filename}')
"

*Validación*: Propuesta generada con anotaciones de confianza.

### 7. Generate Asset Generation Report
python -c "
import json
from datetime import datetime
from pathlib import Path

output_dir = Path('{{output_dir}}')

report = {
    'generated_at': datetime.utcnow().isoformat(),
    'hotel': '{{hotel_name}}',
    'hotel_id': '{{hotel_id}}',
    'preflight_results': json.loads('''{{preflight_result}}'''),
    'nomenclature': '{{nomenclature}}',
    'files_generated': [
        '{{filename_prefix}}boton_whatsapp.html' if {{whatsapp_confidence}} >= 0.9 else None,
        '{{filename_prefix}}faq_schema.json' if {{faq_confidence}} >= 0.7 else None,
        '{{filename_prefix}}hotel_schema.json' if {{schema_confidence}} >= 0.8 else None,
        '{{filename_prefix}}propuesta.md'
    ],
    'files_skipped': [
        'boton_whatsapp.html' if {{whatsapp_confidence}} < 0.9 else None,
        'faq_schema.json' if {{faq_confidence}} < 0.7 else None,
        'hotel_schema.json' if {{schema_confidence}} < 0.8 else None
    ],
    'overall_status': 'SUCCESS' if '{{nomenclature}}' != 'BLOCKED' else 'BLOCKED'
}

# Remove None values
report['files_generated'] = [f for f in report['files_generated'] if f]
report['files_skipped'] = [f for f in report['files_skipped'] if f]

with open(output_dir / 'asset_generation_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print('📊 Asset generation report saved')
print(f'Overall Status: {report[\"overall_status\"]}')
"

*Validación*: Reporte de generación de assets guardado.

## Criterios de Éxito
- [ ] Preflight checks ejecutados.
- [ ] Nomenclatura determinada (PASSED/WARNING/BLOCKED).
- [ ] Assets generados según gates de confianza.
- [ ] Propuesta generada con anotaciones de confianza.
- [ ] Reporte de generación guardado.

## Plan de Recuperación (Fallback)
- Si nomenclatura es BLOCKED, generar solo reporte de diagnóstico sin assets.
- Si un asset específico falla, continuar con los demás y documentar en el reporte.

## Nomenclatura de Archivos

| Status | Prefix | Ejemplo |
|--------|--------|---------|
| PASSED (confidence >= 0.9) | (ninguno) | `boton_whatsapp.html` |
| WARNING (confidence 0.7-0.9) | `ESTIMATED_` | `ESTIMATED_boton_whatsapp.html` |
| BLOCKED (confidence < 0.7) | No generar | - |