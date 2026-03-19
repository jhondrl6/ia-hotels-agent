---
description: Escáner de vigilancia ligera y alertas de anomalías.
---

# Skill: Watchdog Check (Vigilancia Ligera)

> [!NOTE]
> **Trigger**: "escáner ligero", "vigila este perfil", "chequeo rápido".

## Pre-requisitos (Contexto)
- [ ] Nombre y ubicación del hotel.
- [ ] URL del hotel (`{{url}}`).

## Fronteras (Scope)
- **Hará**: Chequeo de visibilidad rápida en Google Maps y asistentes IA. Alerta de inconsistencias graves.
- **NO Hará**: No ejecuta el pipeline completo ni genera reportes detallados.

## Pasos de Ejecución

### 1. Escaneo de Vigilancia Ligera
// turbo
geo_stage --url {{url}} --skip-competitors --skip-posts

*Validación*: Se obtienen métricas básicas de GBP y visibilidad.

### 2. Detección de Anomalías
Comparar el `gbp_score` actual con los benchmarks mínimos históricos.

*Validación*: Si el score cae de 60, disparar alerta crítica.

### 3. Registro de Estado
Actualizar el Knowledge Graph con el estado de vigilancia actual.

*Validación*: Snapshot guardado para seguimiento temporal.

## Criterios de Éxito
- [ ] Escaneo completado en menos de 2 minutos.
- [ ] Alertas enviadas si se detectan fallos.
- [ ] Datos persistidos para el histórico.

## Plan de Recuperación (Fallback)
- Si el scraping falla, usar la Search API para validar existencia del negocio.
- Si no hay acceso a benchmarks, usar el umbral genérico de 50/100.
