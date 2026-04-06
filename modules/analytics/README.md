# Analytics Module — iah-cli

Modulo de integracion con fuentes de datos analiticas externas para el diagnostico de hoteles.

## Providers Configurados

| Provider | Client | Variable de Entorno | Estado | Documentacion |
|----------|--------|---------------------|--------|---------------|
| **Google Analytics 4** | `GoogleAnalyticsClient` | `GA4_PROPERTY_ID` + Google Cloud credentials (service account JSON) | ✅ IMPLEMENTADO | [GoogleAnalyticsClient](google_analytics_client.py) |
| **Profound AI** | `ProfoundClient` | `PROFOUND_API_KEY` | ⚠️ STUB/MOCK | [ProfoundClient](profound_client.py) |
| **Semrush** | `SemrushClient` | `SEMRUSH_API_KEY` | ⚠️ STUB/MOCK | [SemrushClient](semrush_client.py) |

## Configuracion de GA4 (Implementado)

1. Crear proyecto en [Google Cloud Console](https://console.cloud.google.com/)
2. Habilitar API: "Google Analytics Data API"
3. Crear Service Account y descargar JSON de credenciales
4. Exportar credenciales:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/ruta/a/credentials.json"
   export GA4_PROPERTY_ID="properties/XXXXXXXXX"  # El ID numerico de tu propiedad
   ```
5. Verificar:
   ```python
   from modules.analytics.google_analytics_client import GoogleAnalyticsClient
   client = GoogleAnalyticsClient()
   print(f"Configured: {client.is_configured}")
   ```

## Configuracion de Profound AI (Stub)

1. Crear cuenta en https://www.profound.com/
2. Obtener API key desde el dashboard
3. Exportar variable:
   ```bash
   export PROFOUND_API_KEY="tu-api-key-aqui"
   ```
4. Implementar las llamadas reales en `profound_client.py` (actualmente `NotImplementedError`)

**Endpoints de la API de Profound:**
- `GET /v1/ai-visibility?domain={domain}` — AI Visibility Score
- `GET /v1/share-of-voice?domain={domain}&competitors={list}` — Share of Voice
- `GET /v1/citation-rate?domain={domain}` — Tasa de citacion con enlace

**Fallback a mock:** Cuando no hay API key, retorna `None` en todas las metricas sin errores.

## Configuracion de Semrush (Stub)

1. Crear cuenta en https://www.semrush.com/ con acceso a API
2. Obtener API key desde el dashboard (My Reports -> API)
3. Exportar variable:
   ```bash
   export SEMRUSH_API_KEY="tu-api-key-aqui"
   ```
4. Implementar las llamadas reales en `semrush_client.py` (actualmente `NotImplementedError`)

**Endpoints de la API de Semrush:**
- `POST /v2/reports` (tipo `domain_organic`) — Trafico organico
- `GET /v1/domain_analytics/organic_research/{domain}` — Investigacion organica
- Keywords difficulty — Dificultad de palabras clave

**Fallback a mock:** Cuando no hay API key, retorna `None` en todas las metricas sin errores.

## Fallback Graceful

El sistema esta diseñado para funcionar sin ninguna fuente de analytics externa:

- **Sin GA4:** Flujo cualitativo con datos del hotel y scraping
- **Sin Profound:** Sin datos de AI Visibility (no bloqueante)
- **Sin Semrush:** Sin datos de SEO competitivo (no bloqueante)
- **Todos configurados:** Diagnostico completo con datos cuantitativos reales

Cada cliente expone `is_mock` o `is_configured` para que el orquestador detecte que fuentes estan activas y documente cuales faltan en el reporte final (ver FASE-IAO-06: Analytics Transparency Loop).

## Estructura del Modulo

```
modules/analytics/
  __init__.py                # exports publicos
  google_analytics_client.py # GA4 Data API (IMPLEMENTADO)
  profound_client.py         # Profound AI API (STUB)
  semrush_client.py          # Semrush API (STUB)
  README.md                  # Este archivo
```

## Historial de Versiones

| Fase | Descripcion | Estado |
|------|-------------|--------|
| GAP-IAO-01-05 | GA4 Integration | ✅ COMPLETADA |
| FASE-IAO-06 | Analytics Transparency Loop | ✅ COMPLETADA |
| ANALYTICS-03 | Documentacion de stubs | ✅ COMPLETADA |
