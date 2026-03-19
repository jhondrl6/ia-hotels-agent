---
description: Validador de calidad y coherencia de los entregables generados.
---

# Skill: QA Guardian (Control de Calidad)

> [!NOTE]
> **Trigger**: "valida los entregables", "QA post-venta", "revisar diagnóstico".

## Pre-requisitos (Contexto)
- [ ] Directorio de salida con archivos generados.
- [ ] Datos originales del hotel.

## Fronteras (Scope)
- **Hará**: Verificación de placeholders en Markdown/PDF, alineación de ROI en todos los documentos, cumplimiento de directrices de marca.
- **NO Hará**: No corrige errores automáticamente, solo genera un reporte de inconsistencias.

## Pasos de Ejecución

### 1. Escaneo de Placeholders
Buscar cualquier texto en formato `{{...}}` o `[N/D]` en los archivos del directorio de salida.

*Validación*: Todos los campos están poblados correctamente.

### 2. Triangulación de ROI
Confirmar que la "pérdida mensual" y el "paquete recomendado" coincidan en el Diagnóstico Ejecutivo y la Propuesta PDF.

*Validación*: Datos financieros coherentes en todo el kit de entrega.

### 3. Certificación de Calidad
Generar un sello de calidad "QA Passed" si el kit cumple todos los requisitos.

*Validación*: El consultor recibe el OK para proceder con el cliente.

## Criterios de Éxito
- [ ] Kit de entrega 100% coherente.
- [ ] Sin placeholders visibles.
- [ ] Cálculos financieros validados doblemente.

## Plan de Recuperación (Fallback)
- Si hay inconsistencias, indicar al consultor qué campos requieren edición manual.
- Si el QA detecta un error de lógica mayor, recomendar reiniciar la etapa de IA.
