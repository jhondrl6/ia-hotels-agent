---
description: Validate structural coherence between diagnosis, proposal, and generated assets.
---

# Skill: V4 Coherence Validator

> [!NOTE]
> **Trigger**: Execute AFTER proposal generation and BEFORE asset generation to ensure alignment.

## Pre-requisitos (Contexto)
- [ ] Diagnosis data (brechas, fugas, scores)
- [ ] Proposal data (paquete recomendado, ROI, precio)
- [ ] Hotel metadata (nombre, URL, validación cruzada)
- [ ] **Configuración cargada desde `.conductor/guidelines.yaml`**

## Fronteras (Scope)
- **Hará**: Validar coherencia estructural entre diagnóstico, propuesta y assets planificados. Detectar inconsistencias críticas.
- **NO Hará**: No modifica datos, solo emite dictamen de coherencia.

## Pasos de Ejecución

### 1. Extract Diagnosis Summary
// turbo
python -c "
import json
import sys

# Load diagnosis from context
diagnosis = json.loads('''{{diagnosis_json}}''')
proposal = json.loads('''{{proposal_json}}''')

# Extract key metrics
brechas = diagnosis.get('brechas_criticas', [])
fugas = diagnosis.get('fugas_gbp', [])
perdida_mensual = diagnosis.get('perdida_mensual', 0)

coherence_checks = {
    'diagnosis_brechas_count': len(brechas),
    'diagnosis_fugas_count': len(fugas),
    'diagnosis_perdida': perdida_mensual,
    'proposal_paquete': proposal.get('paquete_recomendado', ''),
    'proposal_precio': proposal.get('precio', 0),
    'proposal_roi': proposal.get('roi_meses', 0)
}

print(json.dumps(coherence_checks, indent=2))
"

*Validación*: Diagnosis y proposal cargados correctamente.

### 2. Validate Package-Diagnosis Alignment
// turbo
python -c "
import json

paquete = '{{proposal_paquete}}'.lower()
brechas = json.loads('''{{brechas_json}}''')

# Define package capabilities
package_capabilities = {
    'starter geo': ['geo_basico', 'seo_local'],
    'pro aeo': ['geo_basico', 'seo_local', 'ia_basics', 'automation_light'],
    'pro aeo plus': ['geo_basico', 'seo_local', 'ia_basics', 'automation_light', 'schema_advanced'],
    'elite': ['geo_avanzado', 'seo_tecnico', 'ia_completa', 'automation_full', 'revpar_optimization'],
    'elite plus': ['todo', 'priority_support', 'dedicated_manager']
}

capabilities = package_capabilities.get(paquete, [])
inconsistencies = []

for brecha in brechas:
    tipo = brecha.get('tipo', '').lower()
    # Check if package can address this gap type
    if tipo in ['revpar', 'adr_optimization', 'pricing_strategy'] and 'revpar_optimization' not in capabilities:
        if 'elite' not in paquete:
            inconsistencias.append(f'Brecha tipo {tipo} requiere Elite/Elite PLUS')

result = {
    'coherent': len(inconsistencias) == 0,
    'inconsistencias': inconsistencias,
    'paquete_capabilities': capabilities
}

print(json.dumps(result, indent=2, ensure_ascii=False))
"

*Validación*: Paquete puede abordar las brechas identificadas.

### 3. Validate ROI Credibility
// turbo
python -c "
import json
import yaml

# Cargar config desde .conductor/guidelines.yaml
with open('.conductor/guidelines.yaml', 'r') as f:
    config = yaml.safe_load(f)

price_config = config.get('price_validation', {})
min_ratio = price_config.get('min_ratio', 3.0)
max_ratio = price_config.get('max_ratio', 6.0)
ideal_ratio = price_config.get('ideal_ratio', 4.5)

perdida = {{diagnosis_perdida}}
precio = {{proposal_precio}}
roi_meses = {{proposal_roi}}

# Validate ROI calculation
if perdida > 0 and precio > 0:
    expected_roi = precio / (perdida * 0.3)  # Assuming 30% capture
    roi_credible = abs(roi_meses - expected_roi) <= 2  # Within 2 months
else:
    roi_credible = False

# Validate investment vs loss ratio - NUEVO (alineado con CoherenceConfig)
if perdida > 0:
    investment_ratio = precio / perdida
    ratio_valid = min_ratio <= investment_ratio <= max_ratio
    # Calculate score based on proximity to ideal ratio
    ratio_deviation = abs(investment_ratio - ideal_ratio)
    max_deviation = max(max_ratio - ideal_ratio, ideal_ratio - min_ratio)
    ratio_score = max(0.0, 1.0 - (ratio_deviation / max_deviation)) if max_deviation > 0 else 1.0
else:
    ratio_valid = False
    investment_ratio = 0
    ratio_score = 0.0

result = {
    'roi_credible': roi_credible,
    'investment_ratio_valid': ratio_valid,
    'investment_ratio': round(investment_ratio, 2) if perdida > 0 else 0,
    'ratio_score': round(ratio_score, 2),
    'ratio_range': f'{min_ratio}x-{max_ratio}x',
    'recommendation': 'APPROVED' if (roi_credible and ratio_valid) else 'REVIEW'
}

print(json.dumps(result, indent=2))
"

*Validación*: ROI es coherente con la pérdida estimada.

### 4. Validate Cross-Reference Consistency
// turbo
python -c "
import json
import yaml

# Cargar config desde .conductor/guidelines.yaml
with open('.conductor/guidelines.yaml', 'r') as f:
    config = yaml.safe_load(f)

coherence_config = config.get('v4_coherence_rules', {})

# WhatsApp validation con umbral desde config
whatsapp_config = coherence_config.get('whatsapp_verified', {})
whatsapp_threshold = whatsapp_config.get('confidence_threshold', 0.9)

# Check if WhatsApp is consistent across all sources
whatsapp_web = '{{whatsapp_web}}'
whatsapp_gbp = '{{whatsapp_gbp}}'
whatsapp_input = '{{whatsapp_input}}'

fuentes_whatsapp = [w for w in [whatsapp_web, whatsapp_gbp, whatsapp_input] if w]

# Calcular confidence basado en coincidencias
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

# Check ADR consistency (usando confidence threshold en lugar de diferencia fija)
adr_benchmark = {{adr_benchmark}}
adr_input = {{adr_input}}

if adr_input > 0 and adr_benchmark > 0:
    adr_diff = abs(adr_input - adr_benchmark) / adr_benchmark
    # Usar mismo threshold de confianza que otros validadores
    adr_confidence = max(0.0, 1.0 - adr_diff)
    financial_config = coherence_config.get('financial_data_validated', {})
    financial_threshold = financial_config.get('confidence_threshold', 0.7)
    
    if adr_confidence < 0.5:  # CONFLICT level
        conflictos.append(f'ADR conflicto: confidence={adr_confidence:.2f}, benchmark={adr_benchmark}, input={adr_input}')
    elif adr_confidence < financial_threshold:
        conflictos.append(f'ADR baja confianza: confidence={adr_confidence:.2f} < threshold={financial_threshold}')

# Determinar nivel de confianza
if len(conflictos) == 0:
    confidence_level = 'VERIFIED'
elif whatsapp_confidence < 0.5 or (adr_input > 0 and adr_benchmark > 0 and adr_confidence < 0.5):
    confidence_level = 'CONFLICT'
else:
    confidence_level = 'ESTIMATED'

result = {
    'cross_reference_valid': len(conflictos) == 0,
    'conflictos': conflictos,
    'whatsapp_confidence': round(whatsapp_confidence, 2),
    'whatsapp_verified': whatsapp_verified,
    'whatsapp_threshold': whatsapp_threshold,
    'confidence_level': confidence_level
}

print(json.dumps(result, indent=2, ensure_ascii=False))
"

*Validación*: Datos cruzados son consistentes.

### 5. Generate Coherence Report
python -c "
import json
from datetime import datetime

report = {
    'timestamp': datetime.utcnow().isoformat(),
    'hotel': '{{hotel_name}}',
    'url': '{{url}}',
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
"

*Validación*: Reporte de coherencia guardado en output directory.

## Criterios de Éxito
- [ ] Todos los checks de coherencia pasaron.
- [ ] Score de coherencia >= 0.8 (configurable en `.conductor/guidelines.yaml`)
- [ ] Price/Loss ratio entre 3x-6x (configurable en `.conductor/guidelines.yaml`)
- [ ] WhatsApp verificado con confidence >= 0.9 (configurable)
- [ ] Sin conflictos de validación cruzada críticos.
- [ ] Reporte generado y guardado.

## Plan de Recuperación (Fallback)
- Si coherence_score < 0.8, requiere revisión manual antes de generar assets.
- Si hay conflictos de validación cruzada, bloquear generación y reportar al usuario.

## Output
```json
{
  "coherence_score": 0.92,
  "overall_status": "APPROVED",
  "recommendation": "PROCEED_TO_ASSET_GENERATION"
}
```