---
description: Generar el kit de entrega completo para el hotel.
---

# Skill: Delivery Wizard (Generador de Entregables)

> [!NOTE]
> **Trigger**: "materializa la propuesta", "genera entregables", "finaliza auditoría".

## Pre-requisitos (Contexto)
- [ ] Datos de las etapas previas (geo, seo, ia).
- [ ] Directorio de salida configurado.

## Fronteras (Scope)
- **Hará**: Generación de Diagnóstico Ejecutivo, Propuesta PDF, Kits de Contacto (WhatsApp, Email) y Certificados (Badge Reserva Directa).
- **NO Hará**: No genera el análisis, solo procesa los datos existentes para crear los activos.

## Pasos de Ejecución

### 1. Generación de Kit de Salida
// turbo
outputs_stage --url {{url}}

*Validación*: Directorio de salida (`output/hotel_name_timestamp/`) poblado con los archivos.

### 2. Validación de Coherencia de Salida
// turbo
qa_guardian --url {{url}}

*Validación*: Los documentos generados no contienen placeholders vacíos y los cálculos de ROI coinciden entre sí.

### 3. Notificación de Entrega
Resumir la ubicación de los archivos y los próximos pasos para el consultor.

*Validación*: El consultor tiene el "kit de combate" listo para enviar.

## Criterios de Éxito
- [ ] Propuesta PDF generada y validada.
- [ ] Toolkit de consultor completo.
- [ ] Certificados generados si el paquete califica.

## Plan de Recuperación (Fallback)
- Si el generador de PDF falla, proveer la propuesta en formato Markdown optimizado.
- Si los certificados fallan, marcarlos como "pendientes de validación manual".
