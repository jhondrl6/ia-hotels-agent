# Plan: Superar Desconexiones Restantes en Flujo Analytics E2E
## ID: ANALYTICS-E2E-BRIDGE
## Version: 1.0 — 2026-04-02
## Base: v4.13.0 (Analytics Transparency Loop)

---

## DIAGNOSTICO DEL ESTADO ACTUAL (verificado en codigo)

### Flujo analytics ACTUAL (lo que YA funciona):
```
main.py L1953-1979 → AnalyticsStatus construido
    ↓
main.py L1984-1994 → analytics_data pasado a V4DiagnosticGenerator.generate()
    ↓
V4DiagnosticGenerator._inject_analytics() → seccion transparencia en diagnostico
    ↓
NO pasa a V4ProposalGenerator
NO pasa a V4AssetOrchestrator
NO se persiste en v4_complete_report.json
```

### Las 4 Desconexiones (CONFIRMADAS):

| # | Desconexion | Evidencia en Codigo | Severidad |
|---|-------------|---------------------|-----------|
| D1 | V4ProposalGenerator no recibe analytics_data | `generate()` en L140-152 NO tiene parametro analytics_data | ALTA |
| D2 | ProfoundClient y SemrushClient son 100% stubs | analytics_status L1967-1970: hardcoded `available=False` | BAJA* |
| D3 | Analytics → Asset bridge no existe | pain_solution_mapper.py tiene 0 refs a "analytics" | MEDIA |
| D4 | analytics_data no se persiste al v4_complete_report.json | report dict L2313-2379 NO incluye seccion analytics | ALTA |

*D2 es baja porque es un design decision documentado, no un bug. Los stubs existen para cuando haya credenciales.

---

## PLAN POR FASES (siguiendo phased_project_executor.md)

### FASE-ANALYTICS-01: Persistir analytics_status en v4_complete_report.json
**Complejidad**: BAJA | **Archivos**: 1 | **Prioridad**: INMEDIATA

**Objetivo**: Agregar seccion `analytics` al JSON report para trazabilidad.

**Tareas**:
1. En `main.py` ~L2378 (antes de cerrar el dict `report`), agregar:
```python
'analytics': {
    'ga4_available': analytics_status.ga4_available,
    'ga4_status': analytics_status.ga4_status_for_template(),
    'profound_available': analytics_status.profound_available,
    'profound_status': analytics_status.profound_status_for_template(),
    'semrush_available': analytics_status.semrush_available,
    'semrush_status': analytics_status.semrush_status_for_template(),
    'is_complete': analytics_status.is_complete(),
    'missing_credentials': analytics_status.missing_credentials(),
    'timestamp': analytics_status.timestamp.isoformat(),
}
```
2. Verificar que `analytics_status` esta en scope (esta declarado en L1959, el report se construye en L2313 — mismo scope `v4complete`).

**Criterios de Aceptacion**:
- [ ] `v4_complete_report.json` incluye seccion `analytics` con todos los campos
- [ ] Cuando GA4 no configurado: `ga4_available=False`, `ga4_status` muestra texto descriptivo
- [ ] `missing_credentials` lista las variables de entorno faltantes
- [ ] Backwards compatible: report existente funciona sin cambios adicionales

**Archivos a modificar**:
- `main.py` (1 insertion ~L2378)

---

### FASE-ANALYTICS-02: V4ProposalGenerator recibe analytics_data
**Complejidad**: MEDIA | **Archivos**: 2-3 | **Dependencia**: FASE-ANALYTICS-01

**Objetivo**: El generador de propuesta puede incluir metricas de trafico indirecto cuando estan disponibles.

**Tareas**:
1. Modificar firma de `V4ProposalGenerator.generate()` (L140-152) para aceptar parametro opcional:
```python
def generate(
    self,
    diagnostic_summary: DiagnosticSummary,
    financial_scenarios: FinancialScenarios,
    asset_plan: List[AssetSpec],
    hotel_name: str,
    output_dir: str,
    price_monthly: Optional[int] = None,
    setup_fee: Optional[int] = None,
    audit_result: Optional[Any] = None,
    pricing_result: Optional[PricingResolutionResult] = None,
    region: Optional[str] = None,
    analytics_data: Optional[Dict] = None,  # NUEVO
) -> str:
```

2. En main.py L2030-2039, pasar `analytics_data=analytics_data` en la llamada.

3. En `V4ProposalGenerator._prepare_template_data()` (~L439+), si `analytics_data` no es None y tiene datos reales, agregar al template context:
```python
if analytics_data and analytics_data.get('use_ga4'):
    template_vars['analytics_metrics'] = 'Si — datos GA4 incluidos'
    template_vars['indirect_traffic_note'] = 'Metricas de trafico indirecto disponibles'
else:
    template_vars['analytics_metrics'] = 'No disponible (configurar GA4)'
    template_vars['indirect_traffic_note'] = ''
```

4. En `propuesta_v6_template.md` (si existe), agregar placeholder `${indirect_traffic_note}` en seccion de contexto del hotel (opcional, solo si el template lo soporta).

**Criterios de Aceptacion**:
- [ ] `V4ProposalGenerator.generate()` acepta `analytics_data` sin romper llamadas existentes
- [ ] main.py pasa `analytics_data` al proposal generator
- [ ] Cuando GA4 esta disponible, la propuesta menciona metricas de analytics
- [ ] Cuando GA4 no esta disponible, la propuesta no muestra seccion de analytics (sin placeholders)
- [ ] Backwards compatible: funciona sin `analytics_data` (default None)

**Archivos a modificar**:
- `modules/commercial_documents/v4_proposal_generator.py` (firma + preparacion template)
- `main.py` (L2030-2039: pasar analytics_data)
- `modules/commercial_documents/templates/propuesta_v6_template.md` (placeholder opcional)

---

### FASE-ANALYTICS-03: Documentar stubs de Profound y Semrush
**Complejidad**: BAJA | **Archivos**: 2-3 | **Independiente** (puede ejecutarse en paralelo con FASE-01)

**Objetivo**: Documentar claramente que se necesita para activar las integraciones reales.

**Tareas**:
1. En `modules/analytics/profound_client.py`, agregar docstring con:
   - Variables de entorno requeridas: `PROFOUND_API_KEY`
   - Formato esperado de la API
   - Estado actual: STUB (retorna None)
   - Como activar: setear variable + cambiar flag en __init__

2. En `modules/analytics/semrush_client.py`, mismo patron:
   - Variables: `SEMRUSH_API_KEY`
   - Estado: STUB
   - Instrucciones de activacion

3. En `docs/` o `README.md`, agregar seccion "Fuentes de Datos Analytics" con tabla:
```
| Fuente | Variable | Estado | Activacion |
|--------|----------|--------|------------|
| GA4 | GA4_PROPERTY_ID + credentials | ✅ Implementado | Setear vars |
| Profound AI | PROFOUND_API_KEY | ⚠️ Stub | Pendiente API key |
| Semrush | SEMRUSH_API_KEY | ⚠️ Stub | Pendiente API key |
```

**Criterios de Aceptacion**:
- [ ] Ambos clientes tienen docstrings completos con instrucciones de activacion
- [ ] README o docs incluyen tabla de configuracion de analytics
- [ ] El fallback a mock esta documentado y es graceful

**Archivos a modificar**:
- `modules/analytics/profound_client.py`
- `modules/analytics/semrush_client.py`
- `README.md` o `docs/` (seccion nueva)

---

### FASE-ANALYTICS-04: Analytics → Asset bridge
**Complejidad**: ALTA | **Archivos**: 3-4 | **Dependencia**: FASE-ANALYTICS-02

**Objetivo**: Cuando analytics detecta problemas de visibilidad, se generan assets especificos (ej: guia GA4, recomendaciones Schema).

**Tareas**:
1. En `modules/commercial_documents/pain_solution_mapper.py`, agregar pain types relacionados con analytics:
```python
# Analytics-related pain types
"no_analytics_configured": {
    "pain_type": "no_analytics_configured",
    "solution": "Configurar Google Analytics 4 para medicion de trafigo indirecto",
    "asset_types": ["analytics_setup_guide"],
    "severity": "medium",
    "confidence": 0.7,
},
"low_indirect_traffic": {
    "pain_type": "low_indirect_traffic",
    "solution": "Optimizar presencia digital para aumentar trafico indirecto",
    "asset_types": ["indirect_traffic_optimization"],
    "severity": "medium",
    "confidence": 0.6,
},
```

2. Crear asset templates en `modules/asset_generation/templates/`:
   - `analytics_setup_guide.md` — Guia paso a paso para configurar GA4
   - `indirect_traffic_optimization.md` — Recomendaciones para mejorar visibilidad

3. En `pain_mapper.detect_pains()` (o equivalente), agregar deteccion:
   - Si `analytics_status.ga4_available == False` → detectar pain `no_analytics_configured`
   - Si `analytics_data` disponible y `indirect_traffic < threshold` → `low_indirect_traffic`

4. En main.py, pasar `analytics_data` al pain detection flow (si no llega ya por audit_result).

**Criterios de Aceptacion**:
- [ ] PainSolutionMapper incluye al menos 2 pain types de analytics
- [ ] Cuando GA4 no configurado, se detecta pain `no_analytics_configured`
- [ ] Assets de guia GA4 se generan cuando se detecta el pain
- [ ] El bridge es opcional: si no hay analytics_data, el flujo funciona igual
- [ ] Tests unitarios para nuevos pain types

**Archivos a modificar**:
- `modules/commercial_documents/pain_solution_mapper.py`
- `modules/asset_generation/asset_catalog.py` (registrar nuevos assets)
- `modules/asset_generation/conditional_generator.py` (si necesita dispatch)
- Nuevos templates en `modules/asset_generation/templates/`

---

## DIAGRAMA DE DEPENDENCIAS

```
FASE-ANALYTICS-01 (persistir JSON)  ←── INDEPENDIENTE (iniciar aqui)
FASE-ANALYTICS-03 (doc stubs)       ←── INDEPENDIENTE (paralelo)
        │
        ▼
FASE-ANALYTICS-02 (proposal recibe analytics)
        │
        ▼
FASE-ANALYTICS-04 (analytics → asset bridge)
```

## TABLA DE CONFLICTOS DE ARCHIVOS

| Fase | Archivos | Conflicto con |
|------|----------|---------------|
| ANALYTICS-01 | main.py L2378 | Ninguno (insertion point unico) |
| ANALYTICS-02 | main.py L2030-2039, v4_proposal_generator.py L140-152 | ANALYTICS-01 (mismo archivo, distinta zona) |
| ANALYTICS-03 | profound_client.py, semrush_client.py | Ninguno |
| ANALYTICS-04 | pain_solution_mapper.py, asset_catalog.py | ANALYTICS-02 (ambos leen analytics_data) |

## RIESGOS Y MITIGACIONES

| Riesgo | Mitigacion |
|--------|------------|
| main.py tiene 2612 lineas — cambios en zonas distintas pueden causar merge conflicts | Ejecutar fases secuenciales, commit despues de cada una |
| V4ProposalTemplate puede no soportar nuevos placeholders | Hacer insercion condicional: solo mostrar si datos existen |
| Asset bridge requiere design decision sobre que constituye un "analytics pain" | Empezar con 2 pain types claros, expandir despues |
| GA4 client esta implementado pero no testeado con credenciales reales | El flujo funciona sin GA4 (fallback cualitativo) |

## ORDEN DE EJECUCION RECOMENDADO

1. **Sesion 1**: FASE-ANALYTICS-01 (persistir JSON) — 15 min, 1 archivo
2. **Sesion 2**: FASE-ANALYTICS-03 (doc stubs) — 20 min, 3 archivos
3. **Sesion 3**: FASE-ANALYTICS-02 (proposal recibe analytics) — 30 min, 2-3 archivos
4. **Sesion 4**: FASE-ANALYTICS-04 (asset bridge) — 45 min, 4+ archivos

**POST-EJECUCION (obligatorio por phased_project_executor.md L109-135)**:
Despues de cada fase completada:
```bash
python scripts/log_phase_completion.py \
    --fase FASE-ANALYTICS-01 \
    --desc "Persistir analytics_status en v4_complete_report.json" \
    --archivos-mod "main.py" \
    --check-manual-docs
```

## METRICAS DE EXITO (verificables via v4complete)

1. `v4_complete_report.json` tiene seccion `analytics` con todos los campos de AnalyticsStatus
2. `02_PROPUESTA_COMERCIAL.md` muestra nota de analytics cuando GA4 disponible (sin crash cuando no)
3. `profound_client.py` y `semrush_client.py` tienen docstrings completos
4. PainSolutionMapper detecta `no_analytics_configured` cuando GA4 no esta configurado
5. Al menos 1 asset de analytics (guia GA4) se genera en el run de v4complete
6. Todos los tests existentes siguen pasando (0 regresiones)
