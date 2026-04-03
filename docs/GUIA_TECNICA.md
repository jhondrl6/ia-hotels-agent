# Guía Técnica IA Hoteles Agent CLI

**Última actualización:** 2 Abril 2026
**Versión:** 4.18.0 (GA4 Multi-Hotel Architecture)
**Audiencia:** Desarrolladores, DevOps, Contribuidores

## Notas de Cambios v4.12.0 - GA4 Integration

**Fecha:** 1 Abril 2026

### Resumen

Integracion de Google Analytics 4 como metodo #5 de medicion de trafico indirecto post-consulta IA. Implementacion completa con cliente real, consolidacion de modelos de datos, y wiring en pipeline de diagnostico.

### Modulos Principales

#### 1. GoogleAnalyticsClient

**Proposito**: Cliente para GA4 Data API que mide trafico indirecto (sesiones que sugieren consulta previa en IA).

**Ubicacion**: `modules/analytics/google_analytics_client.py`

**Caracteristicas**:
- Lazy initialization con caching
- Graceful fallback cuando GA4 no esta configurado
- Soporte para date_range: last_30_days, last_90_days
- Retorna estructura: sessions_indirect, sessions_direct, sessions_referral, top_sources, data_source, date_range, note

**Metodos principales**:
- `is_available()` - Verifica si GA4 esta configurado y disponible
- `get_indirect_traffic(date_range)` - Obtiene metricas de trafico indirecto

**Variables de entorno requeridas**:
- `GA4_PROPERTY_ID`: ID de propiedad GA4
- `GA4_CREDENTIALS_PATH`: Ruta al archivo JSON de service account

**Dependencia externa**: `google-analytics-data` (pip install)

#### 2. IndirectTrafficMetrics (Consolidado)

**Proposito**: Dataclass para almacenar metricas de trafico indirecto de GA4.

**Ubicacion**: `data_models/aeo_kpis.py` (linea 70)

**Campos**:
| Campo | Tipo | Default | Descripcion |
|-------|------|---------|-------------|
| sessions_indirect | int | 0 | Sesiones de trafico indirecto |
| sessions_direct | int | 0 | Sesiones de trafico directo |
| sessions_referral | int | 0 | Sesiones de trafico referral |
| data_source | str | N/A | Fuente de datos (GA4 o N/A) |
| top_sources | list | [] | Lista de fuentes principales |
| date_range | Optional[str] | None | Rango de fechas consultado |
| note | Optional[str] | None | Nota adicional o error |

**Metodos**:
- `to_dict()` - Serializa a diccionario
- `from_ga4_response(response)` - Factory method desde respuesta de GA4

#### 3. IA Readiness Calculator (GA4 Weight)

**Proposito**: Score compuesto IA-readiness con componente GA4.

**Ubicacion**: `modules/auditors/ia_readiness_calculator.py`

**Weights actualizados**:
| Componente | Peso |
|------------|------|
| schema_quality | 0.22 |
| crawler_access | 0.22 |
| citability | 0.23 |
| llms_txt | 0.09 |
| brand_signals | 0.14 |
| ga4_indirect | 0.10 |

**Redistribucion**: Cuando GA4 no disponible (ga4_indirect_score=None), el peso de 0.10 se redistribuye proporcionalmente entre los componentes disponibles.

#### 4. Diagnostic Generator (GA4 Wiring)

**Proposito**: Integracion de GA4 en calculo de score IAO.

**Ubicacion**: `modules/commercial_documents/v4_diagnostic_generator.py`

**Flujo en `_calculate_score_ia()`**:
1. Intentar IATester (existente)
2. Intentar GA4 para trafico indirecto (opcional, non-blocking)
3. Si GA4 disponible: construir AEOKPIs con IATester + GA4 datos, calcular composite_score
4. Fallback: retornar score de IATester directamente

**Fix en `_calculate_iao_score()`**: Ahora tiene fallback explicito a `_calculate_schema_infra_score()` cuando IATester retorna None o -1.

### Arquitectura de Integracion

    AUDITORIA (V4ComprehensiveAuditor)
        |
        v
    _calculate_iao_score(audit_result, hotel_data)
        |
        +-- IATester.test_hotel(hotel_data)
        |       |
        |       v
        |   ia_score (0-100)
        |
        +-- GoogleAnalyticsClient.get_indirect_traffic()
        |       |
        |       v
        |   IndirectTrafficMetrics
        |
        +-- AEOKPIs(ia_visibility=ia_score, indirect_traffic=ga4_metrics)
                |
                v
            calculate_composite_score()
                |
                v
            score_ia (0-100)

### Backwards Compatibility

- GA4 es completamente opcional
- Todos los paths de GA4 estan envueltos en try/except
- Sin GA4: pipeline funciona con IATester + BingProxy solamente
- Sin GA4: IA readiness redistribuye peso proporcionalmente

---

## Notas de Cambios v4.18.0 - GA4 Multi-Hotel Architecture

**Fecha:** 2 Abril 2026
**FASE:** ANALYTICS-E2E-CERT-01

### Resumen

Evolucion de la integracion GA4 a arquitectura multi-hotel. El `property_id` se pasa por hotel via flag CLI en vez de variable global. Se implementa deteccion fallback automatica de `low_organic_visibility` en el mapper de pain-points. Certificacion E2E completada con 12/12 items PASADOS.

### Certificacion E2E

| Item | Estado |
|------|--------|
| 1-12 | PASADOS (12/12) |

**Resultado:** CERTIFICADO - Todos los escenarios verificados.

### GA4 Multi-Hotel: property_id por Hotel

El `property_id` ya no se lee desde `.env` como valor global. Ahora se pasa explicitamente por hotel mediante el flag CLI:

```
--ga4-property-id <PROPERTY_ID>
```

**Rationale:** Cada hotel tiene su propia propiedad GA4. Un valor global en `.env` limita la operacion a un solo hotel por ejecucion.

**Service account (global, compartido):**
```
config@dian-467401.iam.gserviceaccount.com
```

### Escenarios Probados

#### Escenario 1: Sin GA4
- Pipeline funciona normalmente con IATester + BingProxy
- Sin errores ni warnings de GA4
- IA readiness redistribuye peso proporcionalmente

#### Escenario 2: Con GA4 sin acceso
- Service account configurada pero sin permisos sobre la propiedad
- GoogleAnalyticsClient retorna metrics con `data_source=error`
- Pipeline continua sin interrupcion
- Warning logueado en output

#### Escenario 3: Con GA4 con acceso
- Service account con permisos otorgados
- Metricas reales de trafico indirecto obtenidas
- `data_source=GA4` en IndirectTrafficMetrics
- Composite score incluye componente ga4_indirect (peso 0.10)

### Archivos Modificados

#### 1. main.py
**Cambio:** Nuevo flag `--ga4-property-id` en CLI args.
- Se pasa como parametro al inicializar `GoogleAnalyticsClient`
- Valor por defecto: `None` (sin GA4)

#### 2. v4_diagnostic_generator.py
**Cambio:** 4 metodos actualizados para aceptar y propagar `property_id`.
- Metodos afectados reciben `ga4_property_id` como parametro
- `GoogleAnalyticsClient` se instancia con `property_id` explicito
- Flujo de GA4 completamente condicional al valor de `property_id`

#### 3. pain_solution_mapper.py
**Cambio:** Deteccion fallback automatica de `low_organic_visibility`.
- **FASE ANALYTICS-E2E-CERT-01:** Si el pain-point `low_organic_visibility` no se detecta por IA Tester, se evalua con fallback heuristico basado en metricas GA4 disponibles
- Integracion transparente: el mapper no requiere cambios en su API publica

### GoogleAnalyticsClient - Cambios de API

**Antes (v4.12.0):**
```python
client = GoogleAnalyticsClient()  # Lee GA4_PROPERTY_ID de .env
```

**Ahora (v4.18.0):**
```python
client = GoogleAnalyticsClient(property_id="123456789")  # Parametro explicito
```

El constructor ahora recibe `property_id` como parametro obligatorio (opcional con default `None`). Ya no lee de `.env`.

### Configuracion .env

```env
# GA4_PROPERTY_ID=123456789          # COMENTADO - ya no se usa globalmente
GA4_CREDENTIALS_PATH=/path/to/credentials.json  # ACTIVO - ruta global al JSON de service account
```

- `GA4_PROPERTY_ID`: **Comentado**. Reemplazado por `--ga4-property-id` en CLI.
- `GA4_CREDENTIALS_PATH`: **Activo**. La ruta al JSON de service account sigue siendo global (compartida entre hoteles).

### Dependencia

```
google-analytics-data  # Instalada como dependencia del proyecto
```

### Backwards Compatibility

- Sin `--ga4-property-id`: comportamiento identico a versiones sin GA4
- `.env` con `GA4_PROPERTY_ID` activo: sera ignorado por el nuevo constructor (warning en log)
- Todos los paths GA4 envueltos en try/except
- Pipeline funciona completamente offline sin GA4

---
