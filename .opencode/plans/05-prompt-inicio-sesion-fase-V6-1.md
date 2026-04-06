---
description: FASE V6-1 - Crear templates V6 para documentos comerciales
version: 1.0.0
fase: V6-1
 Objetivo: Crear templates diagnostico_v6_template.md y propuesta_v6_template.md
---

# FASE V6-1: Templates V6 para Documentos Comerciales

## Contexto

Esta fase es parte del proyecto V6 Commercial Documents que busca alinear el formato de los documentos comerciales con la propuesta de valor para el cliente.

**Fases anteriores:** Ninguna (FASE V6-1 es la primera del proyecto V6)

## Tareas de la Fase

### Tarea 1: Analizar V6 existente

Localizar y leer los archivos V6 en `/output/v6/`:
- `01_DIAGNOSTICO_Y_OPORTUNIDAD.md`
- `02_PROPUESTA_COMERCIAL.md`

Estos son el FORMATO OBJETIVO que debe replicarse en los templates del sistema.

### Tarea 2: Crear `diagnostico_v6_template.md`

Ubicación: `modules/commercial_documents/templates/diagnostico_v6_template.md`

Basarse en la estructura de V6 del output, pero con variables template `${}` para:
- `${hotel_name}`
- `${generated_at}`
- `${loss_amount}` (pérdida mensual en COP)
- `${brecha_1_nombre}`, `${brecha_1_costo}`, etc. (4 brechas)
- `${quick_wins}` (lista de wins)
- `${regional_scores}` (tabla de scores)

**IMPORTANTE:** El template debe mantener el frontmatter YAML con:
- `generated_at`
- `version`
- `hotel_id`
- `coherence_score`
- `document_type: DIAGNOSTICO_V6`
- `generator: IA_Hoteles_v4`

### Tarea 3: Crear `propuesta_v6_template.md`

Ubicación: `modules/commercial_documents/templates/propuesta_v6_template.md`

Basarse en la estructura de V6 del output, con variables para:
- `${hotel_name}`
- `${problem_summary}` (resumen del problema)
- `${monthly_loss}` (pérdida mensual)
- `${monthly_investment}` (precio del paquete)
- `${roi_6m}` (ROI a 6 meses)
- `${investment_table}` (tabla mes a mes)
- `${kit_services}` (tabla de servicios del Kit)
- `${plan_7_days}`, `${plan_30_days}`, etc. (plan 7/30/60/90)
- `${payment_options}` (opciones de pago)

### Tarea 4: Agregar lógica de fallback en generadores

Modificar `v4_diagnostic_generator.py` y `v4_proposal_generator.py` para buscar primero `*_v6_*` template antes del default V4.

```python
# En v4_diagnostic_generator.py __init__:
self.template_path = self.template_dir / "diagnostico_v6_template.md"
if not self.template_path.exists():
    self.template_path = self.template_dir / "diagnostico_v4_template.md"
```

## Criterios de Completitud

- [ ] `diagnostico_v6_template.md` existe en `modules/commercial_documents/templates/`
- [ ] `propuesta_v6_template.md` existe en `modules/commercial_documents/templates/`
- [ ] Ambos templates usan frontmatter YAML con campos requeridos
- [ ] Generadores buscan V6 antes de V4
- [ ] Los templates de V6 siguen la estructura comercial de V6 (sin jerga técnica excesiva)

## Post-Ejecución

1. Marcar checklist como completado
2. Actualizar estado en `06-checklist-implementacion.md`
3. NO ejecutar `log_phase_completion.py` aún - esperar a FASE V6-5 (E2E)

## Archivos a Modificar/Crear

| Archivo | Acción |
|---------|--------|
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | CREAR |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | CREAR |
| `modules/commercial_documents/v4_diagnostic_generator.py` | MODIFICAR |
| `modules/commercial_documents/v4_proposal_generator.py` | MODIFICAR |
