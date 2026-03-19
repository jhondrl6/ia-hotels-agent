---
description: Validar y certificar la veracidad de los datos financieros de un hotel antes de emitir un diagnóstico.
---

# Skill: Protocolo de Verdad 4.0 (Truth Protocol)

> [!NOTE]
> **Trigger**: Usar SIEMPRE que se inicie una auditoría (`audit`), o cuando el usuario pida "evalúa este hotel", "valida estos números" o "revisa este diagnóstico".

## Pre-requisitos (Contexto)
- [ ] Nombre y/o URL del hotel (`{{url}}`).
- [ ] Región del hotel para Benchmarks.

## Fronteras (Scope)
- **Hará**: Triangulación de datos crudos contra Benchmarks Nacionales 2026. Emisión de dictamen de Veracidad. Registro en log forense.
- **NO Hará**: No genera activos ni contacta al cliente.

## Pasos de Ejecución

### 1. Extracción de Datos Crudos
// turbo
geo_stage --url {{url}}

*Validación*: Datos base (habitaciones, ubicación, scores) disponibles en memoria.

### 2. Triangulación de Contexto (Autoridad AI)
// turbo
ia_stage --url {{url}}

*Validación*: Identificar asimetría entre realidad operativa y huella digital.

### 3. Coherencia Financiera (Benchmark 2026)
Validar cálculos de pérdida mensual contra umbrales de sensibilidad 2026.

*Validación*: Datos financieros realistas (no exceden 50% de ingresos estimados).

### 4. Registro de Arbitraje
Documentar ajustes en `evidencias/arbitraje_de_verdad.json`.

*Validación*: El log forense refleja los ajustes aplicados.

## Criterios de Éxito
- [ ] Diagnóstico respaldado por Benchmarks 2026.
- [ ] Discrepancias justificadas.
- [ ] Sin falsos positivos de pérdida inflada.

## Plan de Recuperación (Fallback)
- Usar `DEFAULT_DATA` del Benchmark Nacional si faltan datos base.
- Si el plan maestro no carga, abortar.
