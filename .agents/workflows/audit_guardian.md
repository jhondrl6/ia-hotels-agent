---
description: Orquestador raíz para auditoría de hoteles. Coordina geo, seo, ia y entregables.
---

# Skill: Audit Guardian (Orquestador Raíz)

> [!NOTE]
> **Trigger**: Tarea raíz para iniciar el diagnóstico completo de un hotel.

## Pre-requisitos (Contexto)
- [ ] URL del hotel (`{{url}}`).
- [ ] Opciones de ejecución (opcional).

## Fronteras (Scope)
- **Hará**: Ejecutar secuencialmente las etapas de auditoría: Scraping GBP (geo), Auditoría Web (seo), Inteligencia Artificial (ia) y Generación de Entregables (outputs).
- **NO Hará**: No implementa lógica de negocio directamente, delega en las subtareas granulares.

## Pasos de Ejecución

### 1. Validación de Identidad y Verdad
// turbo
truth_protocol --url {{url}}

*Validación*: El hotel ha sido validado contra Benchmarks 2026.

### 2-4. Ejecución Paralela de Etapas Independientes
// turbo parallel
geo_stage --url {{url}}

// turbo parallel  
seo_stage --url {{url}}

// turbo parallel
ia_stage --url {{url}}

*Validación*: Se han obtenido datos de GBP, web_score y análisis IA en paralelo.

### 5. Generación de Entregables
// turbo
outputs_stage --url {{url}}

*Validación*: Los reportes, propuestas y kits de contacto están listos en el directorio de salida.

## Criterios de Éxito
- [ ] Todas las etapas se ejecutaron sin errores críticos.
- [ ] Se inyectó el contexto de memoria entre etapas.
- [ ] El kit de entrega final está completo y validado.

## Plan de Recuperación (Fallback)
- Si una etapa falla, el Harness intentará auto-sanación.
- Si la falla persiste, documentar en el log de sesión y notificar al usuario.
