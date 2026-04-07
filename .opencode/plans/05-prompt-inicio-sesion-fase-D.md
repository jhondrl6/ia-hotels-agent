# FASE-D: Google Search Console Integration

**ID**: FASE-D  
**Objetivo**: Integrar Google Search Console como fuente de datos para el diagnostico, pasando de estimaciones cualitativas ("0% confianza") a datos reales de keywords, posiciones y CTR del hotel.  
**Dependencias**: FASE-A ✅ (provider_registry + canonical_metrics), FASE-A ✅ (opportunity_scorer se alimenta con datos GSC)  
**Duracion estimada**: 3-4 horas  
**Skill**: `phased_project_executor` v2.3.0

---

## Contexto

### Por que esta fase es necesaria

El diagnostico actual dice:

```
Fuentes de Datos:
- Google Analytics 4: No configurado
- Profound AI Visibility: No disponible  
- Semrush SEO: No disponible
- Audit Web: ✅ Disponible

"Con 0% de confianza en el analisis..."
```

Sin GSC, iah-cli NO puede reportar:
- Que keywords realmente traen impresiones al hotel
- En que posicion aparece para cada query
- CTR real por keyword
- Paginas con impresiones pero sin clicks (oportunidades directas)

**PERO la realidad operativa**: Hoteles boutique pequenos probablemente NO tienen GSC configurado. La solucion es un enfoque de 2 etapas:

```
ETAPA 1 (esta fase): Infraestructura tecnica
  - Cliente GSC funcional
  - Paso en onboarding para conectar GSC
  - Fallback honesto cuando no hay datos

ETAPA 2 (mes 2+ del cliente): Datos reales
  - El hotelero ya verifico dominio en GSC durante onboarding
  - Segundo diagnostico ya tiene datos reales
  - De "0% confianza" a "340 impresiones/mes, posicion 8.2 promedio"
```

Esto TAMBIEN es una razon de retencion: el cliente se queda porque el mes 2 ve datos reales.

### Inspiracion

Patron de seomachine:
- `google_search_console.py` — Keywords, rankings, impressions, CTR via service account
- `data_aggregator.py` — Unifica GA4 + GSC + otros

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |
| FASE-B | ✅ Completada |
| FASE-A | ✅ Completada (provider_registry disponible) |
| FASE-B | ✅ Completada |
| FASE-A | ✅ Completada |

### Base Tecnica Disponible

- `modules/analytics/google_analytics_client.py` — Patron GA4 con service account (REPlicar para GSC)
- `modules/utils/provider_registry.py` (FASE-A) — Registro de proveedores
- `modules/utils/canonical_metrics.py` (FASE-A) — Normalizacion de metricas
- `modules/financial_engine/opportunity_scorer.py` (FASE-A) — Se alimenta con datos GSC
- `config/google-analytics-key.json` — Service account existente para GA4
- Service account: `config@dian-467401.iam.gserviceaccount.com`
- Patron GA4: credentials globales, property ID por hotel (via flag)
- Tests base: 1782 + 22 (D) + 14 (E)

---

## Tareas

### Tarea 1: Crear Google Search Console Client

**Objetivo**: Cliente GSC que obtiene keywords, posiciones, impresiones y CTR.

**Archivos afectados**:
- `modules/analytics/google_search_console_client.py` (NUEVO)

**Estructura**:

```python
# modules/analytics/google_search_console_client.py

@dataclass
class GSCQueryData:
    query: str                    # "hotel santa rosa de cabal"
    impressions: int              # 340
    clicks: int                   # 12
    position: float               # 8.2
    ctr: float                    # 0.035
    
@dataclass
class GSCPageData:
    page_url: str
    impressions: int
    clicks: int
    position: float
    ctr: float
    top_queries: List[str]

@dataclass  
class GSCReport:
    site_url: str
    date_range: tuple             # (start_date, end_date)
    total_impressions: int
    total_clicks: int
    avg_position: float
    avg_ctr: float
    top_queries: List[GSCQueryData]      # Top 20 by impressions
    top_pages: List[GSCPageData]         # Top 10 by clicks
    opportunity_queries: List[GSCQueryData]  # Impresiones altas + CTR bajo
    is_available: bool = True
    error_message: str = ""

class GoogleSearchConsoleClient:
    """Client for Google Search Console API."""
    
    SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
    
    def __init__(self, credentials_path: str = None, site_url: str = None):
        # Patron identico a google_analytics_client.py
        self.credentials_path = credentials_path or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self.site_url = site_url
    
    def get_search_analytics(self, start_date: str, end_date: str, 
                              dimensions: list = None) -> GSCReport:
        """Get search analytics data from GSC.
        
        Args:
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD  
            dimensions: ['query'], ['page'], ['query', 'page']
        
        Returns:
            GSCReport with all data
        """
        # 1. Autenticar con service account (patron GA4)
        # 2. Llamar searchanalytics.query
        # 3. Parsear response
        # 4. Calcular opportunity_queries (impresiones > 10 + CTR < avg)
        # 5. Retornar GSCReport
    
    def is_configured(self) -> bool:
        """Check if GSC is properly configured."""
        # credentials_path existe + site_url proporcionado
    
    def get_top_opportunities(self, report: GSCReport) -> List[dict]:
        """Identify keywords with high impressions but low CTR.
        
        These are the highest-value opportunities:
        - Google shows the hotel (impressions exist)
        - But travelers don't click (CTR is low)
        - Fix: improve title, meta description, rich snippets
        
        Returns list of {query, impressions, position, ctr, estimated_gain}
        """
        # Filtrar: impressions > 10 AND ctr < report.avg_ctr
        # estimated_gain = (target_ctr - current_ctr) * impressions * avg_booking_value
```

**Criterios de aceptacion**:
- [ ] Autenticacion via service account (mismo patron GA4)
- [ ] Obtiene top queries con impresiones, clicks, posicion, CTR
- [ ] Identifica opportunity queries (alta impresion + bajo CTR)
- [ ] `is_configured()` retorna False gracefully cuando no hay credenciales
- [ ] Errores de API no crashean el flujo (try/except con fallback)
- [ ] Testeable sin API real (mock responses)

### Tarea 2: Crear Data Aggregator

**Objetivo**: Modulo que unifica datos de GA4 + GSC + otros para inyectar en diagnostico.

**Archivos afectados**:
- `modules/analytics/data_aggregator.py` (NUEVO)

**Estructura**:

```python
# modules/analytics/data_aggregator.py

@dataclass
class UnifiedAnalyticsData:
    """Unified view from all analytics sources."""
    # GSC data
    gsc_available: bool
    gsc_report: Optional[GSCReport]
    # GA4 data  
    ga4_available: bool
    ga4_data: Optional[dict]  # Existing GA4 data
    # Derived insights
    total_organic_impressions: int = 0
    total_organic_clicks: int = 0
    avg_serps_position: float = 0.0
    top_keyword_opportunities: List[dict] = field(default_factory=list)
    confidence_level: str = "LOW"  # LOW, MEDIUM, HIGH
    
class DataAggregator:
    """Aggregates data from multiple analytics sources."""
    
    def __init__(self, gsc_client=None, ga4_client=None):
        self.gsc = gsc_client
        self.ga4 = ga4_client
    
    def aggregate(self, site_url: str, days: int = 30) -> UnifiedAnalyticsData:
        """Pull and unify data from all available sources."""
        gsc_report = None
        ga4_data = None
        
        # Try GSC (graceful fallback)
        if self.gsc and self.gsc.is_configured():
            try:
                gsc_report = self.gsc.get_search_analytics(...)
            except Exception:
                pass
        
        # Try GA4 (existing pattern)
        if self.ga4:
            ga4_data = ...  # existing GA4 fetch
        
        # Calculate confidence
        sources = sum([gsc_report is not None, ga4_data is not None])
        confidence = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}[sources]
        
        return UnifiedAnalyticsData(
            gsc_available=gsc_report is not None,
            gsc_report=gsc_report,
            ga4_available=ga4_data is not None,
            ga4_data=ga4_data,
            confidence_level=confidence,
            ...
        )
```

**Criterios de aceptacion**:
- [ ] Unifica GA4 + GSC en un solo objeto
- [ ] Graceful degradation: sin GSC funciona, sin GA4 funciona, sin ambos funciona
- [ ] Calcula nivel de confianza basado en fuentes disponibles
- [ ] Identifica keyword opportunities desde GSC

### Tarea 3: Integrar en Onboarding

**Objetivo**: Agregar paso de verificacion GSC en el flujo de onboarding del hotel.

**Archivos afectados**:
- `modules/onboarding/onboarding_flow.py` (MODIFICAR)

**Cambios**: Agregar paso opcional que:
1. Pregunta si el hotel ya tiene Google Search Console
2. Si si: pedir URL del sitio verificada y dar acceso al service account
3. Si no: guiar verificacion rapida (1 paso si ya tienen GA4)
4. Guardar `gsc_site_url` en config del hotel

**Criterios de aceptacion**:
- [ ] Paso GSC es OPCIONAL (no bloquea onboarding)
- [ ] Si el hotelero no tiene GSC, el flujo continua normalmente
- [ ] Si lo tiene, se guarda site_url para uso futuro

### Tarea 4: Integrar en Composer

**Objetivo**: El diagnostico usa datos GSC reales cuando estan disponibles.

**Archivos afectados**:
- `modules/commercial_documents/composer.py` (MODIFICAR)

**Cambios en el diagnostico**:

```
SIN GSC (actual):
  "Con 0% de confianza en el analisis..."
  "Pérdida estimada mensual: $3.132.000 COP"

CON GSC (nuevo):
  "Datos de Google: 340 personas buscan 'hotel santa rosa de cabal' al mes.
   Su hotel aparece en posición 8.2 promedio.
   Solo 12 hacen clic (CTR 3.5%).
   
   Si sube a posición 3 (donde estan los competidores),
   estimación conservadora: +17 clics/mes.
   A $150.000 COP/reserva promedio = $2.550.000 COP/mes adicional.
   
   Confianza: ALTA (datos Google Search Console reales)"
```

**Criterios de aceptacion**:
- [ ] Con GSC: muestra keywords, posiciones, CTR reales
- [ ] Sin GSC: fallback honesto con instruccion de activacion
- [ ] El opportunity_scorer (FASE-A) se alimenta con datos GSC cuando disponible
- [ ] No rompe generacion sin GSC

### Tarea 5: Registrar en Provider Registry

**Objetivo**: GSC como proveedor registrado en el sistema.

**Archivos afectados**:
- `config/provider_registry.yaml` (MODIFICAR)

**Cambios**: Agregar entrada:
```yaml
gsc:
  type: "analytics"
  auth_method: "service_account"
  env_vars:
    - "GOOGLE_APPLICATION_CREDENTIALS"
  required_config:
    - "site_url"
  cost_per_run: 0.0  # GSC API es gratis
  rate_limit: "100 requests/min"
  retry_max: 3
  timeout: 30
  optional: true  # No bloquea el flujo
```

**Criterios de aceptacion**:
- [ ] GSC aparece en provider_registry
- [ ] `is_configured()` del provider_registry retorna estado correcto

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| Test GSC client mock | `tests/analytics/test_google_search_console_client.py` | Parsea response mock correctamente |
| Test GSC top queries | `tests/analytics/test_google_search_console_client.py` | Retorna top 20 queries ordenadas |
| Test GSC opportunities | `tests/analytics/test_google_search_console_client.py` | Identifica queries con CTR bajo |
| Test GSC not configured | `tests/analytics/test_google_search_console_client.py` | is_configured() = False sin credenciales |
| Test GSC API error | `tests/analytics/test_google_search_console_client.py` | No crashea, retorna error gracefully |
| Test GSC empty data | `tests/analytics/test_google_search_console_client.py` | Maneja site sin datos |
| Test aggregator with GSC+GA4 | `tests/analytics/test_data_aggregator.py` | Confidence = HIGH |
| Test aggregator GSC only | `tests/analytics/test_data_aggregator.py` | Confidence = MEDIUM |
| Test aggregator no sources | `tests/analytics/test_data_aggregator.py` | Confidence = LOW |
| Test aggregator GA4 only | `tests/analytics/test_data_aggregator.py` | Confidence = MEDIUM |
| Test composer with GSC | `tests/analytics/test_data_aggregator.py` | Diagnostico muestra keywords reales |
| Test composer without GSC | `tests/analytics/test_data_aggregator.py` | Fallback honesto |
| Test onboarding GSC step | `tests/analytics/test_data_aggregator.py` | Paso opcional funciona |
| Test provider registry GSC | `tests/analytics/test_data_aggregator.py` | GSC en registry |
| Test E2E GSC flow | `tests/analytics/test_data_aggregator.py` | GSC → aggregator → composer → diagnostico |
| Test E2E no GSC | `tests/analytics/test_data_aggregator.py` | Sin GSC = flujo actual funciona |

**Comando de validacion**:
```bash
python -m pytest tests/analytics/ -v
python scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`** — Marcar FASE-B como ✅ Completada
2. **`06-checklist-implementacion.md`** — Marcar todos los items de FASE-B como ✅
3. **`09-documentacion-post-proyecto.md`** — Secciones A, B, D, E
4. **Ejecutar**: `python scripts/log_phase_completion.py --fase FASE-B --desc "Google Search Console Integration" --archivos-nuevos "modules/analytics/google_search_console_client.py,modules/analytics/data_aggregator.py,tests/analytics/test_google_search_console_client.py,tests/analytics/test_data_aggregator.py" --archivos-mod "modules/onboarding/onboarding_flow.py,modules/commercial_documents/composer.py,config/provider_registry.yaml" --tests "18" --check-manual-docs`

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Tests nuevos pasan**: 16+ tests en tests/analytics/
- [ ] **Validaciones del proyecto**: `python scripts/run_all_validations.py --quick` pasa
- [ ] **Sin regresiones**: Tests existentes siguen pasando
- [ ] **Prueba sin GSC**: v4complete funciona normalmente sin GSC configurado
- [ ] **Prueba con GSC mock**: Diagnostico muestra keywords, posiciones, CTR
- [ ] **Confidence level**: LOW sin fuentes, MEDIUM con 1, HIGH con 2+
- [ ] **dependencias-fases.md actualizado**
- [ ] **Documentacion afiliada**: CHANGELOG.md, AGENTS.md (GSC en analytics)
- [ ] **Post-ejecucion completada**: log_phase_completion.py ejecutado

---

## Restricciones

- GSC es OPCIONAL: el flujo v4complete debe funcionar completamente sin GSC
- NO requiere que el hotelero tenga GSC para usar iah-cli
- NO agregar dependencias nuevas (google-api-python-client ya esta para GA4)
- Service account mismo que GA4: `config@dian-467401.iam.gserviceaccount.com`
- El patron de credentials es IDENTICO a GA4: global credentials, site_url por hotel
- Costo API: GSC es GRATIS (no afecta costo por ejecucion)

---

## Prompt de Ejecucion

```
Actua como desarrollador Python senior especializado en integracion de APIs Google.

OBJETIVO: Implementar FASE-B — Google Search Console Integration para iah-cli.

CONTEXTO:
- Proyecto: iah-cli v4.22.0+ (FASE-A, D, E completadas)
- Patron existente: google_analytics_client.py usa service account
- Service account: config@dian-467401.iam.gserviceaccount.com
- GSC API: gratis, mismo SDK que GA4
- Problema: diagnostico tiene "0% confianza" sin datos reales
- Solucion: GSC provee keywords, posiciones, CTR reales

TAREAS:
1. Crear modules/analytics/google_search_console_client.py (patron GA4)
2. Crear modules/analytics/data_aggregator.py (unifica GA4 + GSC)
3. Modificar modules/onboarding/onboarding_flow.py (paso GSC opcional)
4. Modificar modules/commercial_documents/composer.py (datos GSC en diagnostico)
5. Modificar config/provider_registry.yaml (entrada gsc)
6. Crear 16+ tests con mock responses

CRITERIOS:
- Funciona sin GSC (graceful degradation)
- Con GSC muestra keywords reales + posiciones + CTR
- Confidence level: LOW/MEDIUM/HIGH segun fuentes disponibles
- Patron identico a GA4 (credentials globales, config por hotel)

VALIDACIONES:
- pytest tests/analytics/ -v (16+ passing)
- python scripts/run_all_validations.py --quick
- v4complete sin GSC = flujo normal
- v4complete con GSC mock = datos reales en diagnostico
```
