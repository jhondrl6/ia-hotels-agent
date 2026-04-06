# Plan de Corrección - GAPS V4COMPLETE
## Fases H-06, H-07, H-08

## Proyecto: iah-cli | hotelvisperas.com
## Fecha: 2026-03-26
## Estado: PENDIENTE

---

## Análisis de FASE-H-05 (E2E Certification - FALLIDA)

La certificación E2E falló por 2 problemas que NO fueron resueltos por H-02 ni H-04:

| Problema | Causa | H-02/H-04 lo resolvieron? |
|----------|-------|---------------------------|
| whatsapp_button BLOCKED | Regex `\+57\d{10}` rechaza números reales | NO - H-02 solo arregló el nombre del campo |
| ROI = "24.0XX" | Cálculo/formato incorrecto | NO - H-04 solo cambió "Ejemplo:" por "Referencia:" |

---

## Nuevas Fases Requeridas

### FASE-H-06: Fix AssetContentValidator - WhatsApp Phone Numbers
**Problema**: El regex `\+57\d{10}` detecta números reales de Colombia (ej: `+573005551234`) como placeholders.

**Solución**: Modificar `modules/asset_generation/asset_content_validator.py` para excluir números de WhatsApp válidos del check de placeholders, o cambiar el regex para solo detectar formatos placeholder obvios.

### FASE-H-07: Fix ROI Calculator
**Problema**: El ROI muestra "24.0XX" en vez del ratio correcto (~2.6X).

**Solución**: Revisar `modules/commercial_documents/v4_proposal_generator.py` y el template `propuesta_v4_template.md` para corregir el cálculo.

### FASE-H-08: Re-Certificación E2E
**Problema**: Necesitamos verificar que H-06 y H-07 resuelven los problemas antes de aceptar la implementación.

---

## Dependencias

```
FASE-H-05 (FALLIDA)
        │
        ▼
FASE-H-06 ──→ FASE-H-07 ──→ FASE-H-08
    │              │              │
    └──────────────┴──────────────┘
              (todas deben pasar)
```

---

## Criterios de Aceptación

Para que el proyecto sea aceptado, FASE-H-08 debe pasar:

- [ ] Coherence Score ≥ 0.8
- [ ] whatsapp_button generado (no BLOCKED)
- [ ] optimization_guide pasa validación (no WARNING)
- [ ] ROI muestra ratio correcto (~2.6X, no "24.0XX")
- [ ] 0 desconnetions en coherence_validator
- [ ] Status: READY_FOR_PUBLICATION

---

## Templates de FASE-H-06, H-07, H-08

### FASE-H-06: Fix AssetContentValidator

```markdown
# Prompt: FASE-H-06 - Fix WhatsApp Phone Validation

## Pre-requisito
FASE-H-05 debe estar ejecutada y documentada.

## Contexto
El validador `AssetContentValidator` tiene un regex `\+57\d{10}` que detecta 
números de teléfono reales de Colombia como placeholders. Esto causa que 
whatsapp_button sea bloqueado aunque el número sea válido.

## Tareas

1. Analizar el regex en `asset_content_validator.py` línea 51
2. Modificar para que NO rechace números de WhatsApp reales
3. Verificar que placeholders obvios siguen siendo detectados
4. Ejecutar pytest para regresión
5. Documentar el fix

## Criterio de completitud
El whatsapp_button pasa validación y se incluye en el delivery.
```

### FASE-H-07: Fix ROI Calculator

```markdown
# Prompt: FASE-H-07 - Fix ROI Calculation

## Pre-requisito
FASE-H-06 debe estar completada.

## Contexto
El ROI en la propuesta comercial muestra "24.0XX" en vez del ratio correcto (~2.6X).

## Tareas

1. Localizar el cálculo del ROI en `v4_proposal_generator.py`
2. Verificar la fórmula: (ganancia_total / inversión_total)
3. Corregir el formato en el template `propuesta_v4_template.md`
4. Ejecutar pytest para regresión
5. Documentar el fix

## Criterio de completitud
El ROI muestra "~2.6X" (ratio) en la propuesta comercial.
```

### FASE-H-08: Re-Certificación E2E

```markdown
# Prompt: FASE-H-08 - Re-Certificación E2E

## Pre-requisito
FASE-H-06 y FASE-H-07 deben estar completadas.

## Contexto
Después de aplicar los fixes de H-06 y H-07, debemos verificar que el 
flujo completo V4COMPLETE funciona sin desconexiones.

## Tareas

1. Ejecutar v4complete E2E
2. Verificar Coherence Score ≥ 0.8
3. Verificar whatsapp_button se genera (no BLOCKED)
4. Verificar optimization_guide pasa validación (no WARNING)
5. Verificar ROI corregido (~2.6X)
6. Actualizar REGISTRY.md

## Criterio de completitud
v4complete pasa E2E con 0 desconexiones.
```

---

*Creado: 2026-03-26*
*Reemplaza: Estado FALLIDO de FASE-H-05*
