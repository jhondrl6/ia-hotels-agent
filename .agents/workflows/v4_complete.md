---
description: Complete v4.0 workflow - Two-phase onboarding with validation, scenarios, and conditional asset generation.
---

# Skill: V4 Complete Orchestrator

> [!NOTE]
> **Trigger**: Main entry point for v4.0 comprehensive analysis. Replaces legacy `audit` command.

## Pre-requisitos (Contexto)
- [ ] URL del hotel
- [ ] Nombre del hotel (opcional)
- [ ] Región del hotel (para benchmarks)

## Fronteras (Scope)
- **Hará**: Ejecutar flujo completo v4.0 de dos fases con validación cruzada y generación condicional.
- **NO Hará**: No usa benchmarks como input directo. No genera assets con datos CONFLICT.

## Pasos de Ejecución

### 1. Phase 1: Hook Generation (Automated)
// turbo
geo_stage --url {{url}}

*Validación*: Datos básicos extraídos (nombre, ubicación, schema).

### 2. Phase 1: Calculate Initial Hook Range
// turbo
v4_financial_scenarios --url {{url}} --phase 1

*Validación*: Rango estimado calculado con benchmarks regionales como contexto.

### 3. Phase 1: Display Hook to User
El sistema muestra el hook generado:

```
{{hotel_name}} podría estar dejando de capturar entre $X y $Y COP mensuales.

¿Quiere precisar esta cifra? (Requiere 5 datos de operación)
```

*Validación*: Hook presentado con disclaimer de estimación. Progreso: 30%

### 4. Phase 2: Collect Operational Data (Manual)
> [!NOTE]
> Este paso requiere interacción del usuario.

Solicitar datos mínimos:
- [ ] Número de habitaciones: `{{rooms}}`
- [ ] Tarifa promedio real (ADR) en COP: `{{adr_cop}}`
- [ ] % Ocupación promedio: `{{occupancy_rate}}`
- [ ] Presencia en OTAs: `{{ota_presence}}`
- [ ] % Canal Directo: `{{direct_channel_percentage}}`
- [ ] Número de WhatsApp: `{{whatsapp_input}}`

*Validación*: Datos operativos completos recibidos.

### 5. Phase 2: Cross-Validation
// turbo
truth_protocol --url {{url}} --validate-cross

*Validación*: WhatsApp, ADR, y datos operativos validados entre fuentes.

### 6. Phase 2: Recalculate Financial Scenarios
// turbo
v4_financial_scenarios --url {{url}} --phase 2 --with-inputs

*Validación*: Escenarios recalculados con datos validados.

### 7. Check for Conflicts
// turbo
python -c "
conflicts_detected = {{has_conflicts}}

if conflicts_detected:
    print('⚠️  CONFLICTOS DETECTADOS:')
    print('{{conflicts_report}}')
    print('\\nRequiere revisión manual antes de continuar.')
    exit(1)
else:
    print('✅ Sin conflictos - datos validados')
"

*Validación*: Sin conflictos críticos de validación cruzada.

### 8. Generate Diagnosis and Proposal
// turbo
ia_stage --url {{url}}
outputs_stage --url {{url}}

*Validación*: Diagnóstico y propuesta generados.

### 9. Validate Coherence
// turbo
v4_coherence_validator --url {{url}}

*Validación*: Coherencia entre diagnosis, proposal y assets validada.

### 10. Generate Assets Conditionally
// turbo
v4_asset_conditional --url {{url}}

*Validación*: Assets generados según gates de calidad.

## Criterios de Éxito
- [ ] Fase 1 completada: Hook generado (30%).
- [ ] Fase 2 completada: Datos validados (60%).
- [ ] Sin conflictos de validación cruzada.
- [ ] Coherence validation PASSED (score >= 0.8).
- [ ] Assets generados condicionalmente.
- [ ] Reporte final guardado en output directory.

## Plan de Recuperación (Fallback)

### Si hay conflictos en validación cruzada:
1. Generar reporte detallado de conflictos.
2. Bloquear generación de assets.
3. Solicitar revisión manual.

### Si coherence score < 0.8:
1. Documentar inconsistencias.
2. Requerir revisión antes de generar assets.

### Si faltan datos operativos:
1. Continuar con estimaciones (WARNING).
2. Aplicar nomenclatura ESTIMATED_ a assets.

## Output Final

```
output/{{hotel_slug}}/
├── v4_complete_report.json          # Reporte completo del análisis
├── phase_1/
│   ├── hook_message.txt             # Hook inicial
│   └── estimated_scenarios.json     # Escenarios estimados
├── phase_2/
│   ├── validated_data.json          # Datos validados
│   ├── cross_validation_report.json # Reporte de validación cruzada
│   └── financial_scenarios.json     # Escenarios financieros
├── diagnosis/
│   ├── diagnosis.json               # Diagnóstico completo
│   └── proposal.md                  # Propuesta comercial
├── assets/
│   ├── [ESTIMATED_]boton_whatsapp.html
│   ├── [ESTIMATED_]faq_schema.json
│   ├── [ESTIMATED_]hotel_schema.json
│   └── asset_generation_report.json
└── coherence/
    └── coherence_report.json        # Validación de coherencia
```

## Estado del Onboarding

| Estado | Progreso | Descripción |
|--------|----------|-------------|
| INIT | 0% | Inicialización |
| PHASE_1_HOOK | 30% | Hook generado con benchmark |
| PHASE_2_INPUT | 60% | Esperando datos del usuario |
| VALIDATION | 75% | Validando datos cruzados |
| CALCULATION | 90% | Calculando escenarios |
| COMPLETE | 100% | Listo para assets |