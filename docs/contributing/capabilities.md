# Sistema de Capability Contracts

> Este documento contiene el sistema de capability contracts segun CONTRIBUTING.md §13.

---

## 13. Sistema de Capability Contracts (v4.4.0)

### 13.1 Proposito

Detectar y prevenir "capacidades desconectadas" - modulos que existen en codigo pero no se invocan en runtime ni producen output observable.

### 13.2 Definicion de Capability Contract

| Campo | Descripcion |
|-------|-------------|
| Capability | Nombre del modulo/validador |
| Estado | conectada/desconectada/huerfana |
| Punto de Invocacion | Donde se ejecuta (archivo:metodo) |
| Evidencia en Output | Artefacto donde se serializa |

### 13.3 Checklist de Verificacion

Cuando integres una nueva capacidad:

- [ ] **Existe en codigo**: Archivo con clase/funcion
- [ ] **Se invoca**: No solo se importa, se ejecuta en flujo
- [ ] **Produce output**: Serializa en to_dict/export/report
- [ ] **Documentada**: Punto de invocacion registrado
- [ ] **Testeada**: Tests cubriendo caso normal y edge

### 13.4 Patron de Verificacion

```bash
# 1. Listar capabilities del contrato
grep -rn "class.*Validator\|class.*Checker" modules/ data_validation/

# 2. Verificar invocacion en flujo principal
grep -rn "Validator()\|Checker()" main.py modules/

# 3. Verificar output en serializacion
grep -rn "to_dict\|export\|report" main.py | grep -i "validator"
```

### 13.5 Matriz de Capacidades

La matriz de capacidades documenta el estado de cada capability en el sistema.

| Capability | Estado | Punto Invocacion | Output | Severidad |
|------------|--------|-----------------|--------|-----------|
| MetadataValidator | conectada | v4_comprehensive.py:_audit_metadata() | audit_result.metadata | HIGH |
| PublicationGates | conectada | main.py:FASE 4.5 | gate_results | CRITICAL |
| ConsistencyChecker | conectada | main.py:FASE 4.6 | consistency_report | HIGH |
| FinancialCalculatorV2 | conectada | main.py:FASE 3 | scenarios | CRITICAL |
| EvidenceLedger | conectada | v4complete:FASE 2 | evidence_ledger | HIGH |
| ContradictionEngine | conectada | v4complete:FASE 2 | contradiction_report | CRITICAL |
| CoherenceValidator | conectada | commercial_documents/ | coherence_score | CRITICAL |
| NoDefaultsValidator | conectada | financial_engine/ | validation_result | CRITICAL |
| AICrawlerAuditor | conectada | v4audit/ | crawler_audit | MEDIUM |
| CitabilityScorer | conectada | v4audit/ | citability_score | MEDIUM |
| IAReadinessCalculator | conectada | v4audit/ | ia_readiness_score | MEDIUM |
| Dashboard | conectada | observability/ | metrics_report | LOW |
| Calibration | conectada | observability/ | calibration_result | LOW |
|| SitePresenceChecker | conectada | asset_generation/ | presence_status | HIGH |
|| AutonomousResearcher | conectada | v4_asset_orchestrator.py | research_result | HIGH |
|| geo_flow | conectada | v4_asset_orchestrator.py:339 | geo_flow_result | HIGH |
|| GEOEnrichmentLayer | conectada | geo_flow.py | enrichment_layer | HIGH |
|| SyncContractAnalyzer | conectada | geo_flow.py | sync_results | HIGH |
| AssetResponsibilityContract | conectada | delivery_packager.py:124 | implementation_order | MEDIUM |
| SSLGuideGenerator | conectada | conditional_generator.py | ssl_guide content | LOW |
| OGTagsGuideGenerator | conectada | conditional_generator.py | og_tags_guide content | LOW |
| AltTextGuideGenerator | conectada | conditional_generator.py | alt_text_guide content | LOW |
| BlogStrategyGuideGenerator | conectada | conditional_generator.py | blog_strategy_guide content | LOW |
| GoogleAnalyticsClient | conectada | v4_diagnostic_generator.py:_check_analytics_status() | analytics_transparency_section, indirect_traffic | HIGH |
| ProfoundClient | conectada (stub) | v4_diagnostic_generator.py:_check_analytics_status() | profound_status_text en diagnostico | MEDIUM |
| SemrushClient | conectada (stub) | v4_diagnostic_generator.py:_check_analytics_status() | semrush_status_text en diagnostico | MEDIUM |
| AnalyticsStatus | conectada | v4_diagnostic_generator.py:_prepare_template_data() | status_text, missing_credentials, transparency_section | HIGH |
| SocialStrategyGuideGenerator | conectada | conditional_generator.py | social_strategy_guide content | LOW |

### 13.6 Gate de Cierre

Antes de marcar fase como completada:

- [ ] 0 capacidades sin invocacion en runtime
- [ ] 0 capacidades sin output observable
- [ ] Matriz de capacidades actualizada

### 13.7 Casos de Uso

| Situacion | Accion |
|-----------|--------|
| Nuevo validador/validator | Agregar a matriz de capacidades |
| Nueva capability en orchestrator | Documentar punto de invocacion |
| Capacidad sin output | INVESTIGAR - puede ser huerfana |
| Modulo existente sin uso | Crear capacidad o archivar |

### 13.8 Relacion con phased_project_executor

El sistema de Capability Contracts se integra con `.agents/workflows/phased_project_executor.md`:

**Paso 6 (Documentacion Post-Fase) incluye:**
- Verificacion de capabilities segun esta matriz
- Confirmacion de que nuevas capacidades tienen punto de invocacion
- Validacion de output serializable

**Capacidades a verificar en cada fase:**
1. Capabilities existentes en codigo
2. Capabilities con punto de invocacion identificado
3. Capabilities con output verificable
4. Capabilities huérfanas (sin uso)

---

## 14. Sistema de Evidence Ledger (v4.3.0)

### 14.1 Proposito

El Evidence Ledger es el almacen centralizado de evidencia que alimenta todo el sistema de validacion cruzada.

### 14.2 Estructura

```
evidence/
├── ledger.json          # Registro central
├── claims/              # Claims por hotel
│   └── {hotel_url}/
│       └── claim_{id}.json
└── evidence/            # Evidencias raw
    └── {hotel_url}/
        ├── web_{timestamp}.json
        ├── gbp_{timestamp}.json
        └── input_{timestamp}.json
```

### 14.3 Integracion

Cuando agregues nueva evidencia:

1. **Web scraping**: Guardar en `evidence/evidence/{hotel}/web_{ts}.json`
2. **GBP API**: Guardar en `evidence/evidence/{hotel}/gbp_{ts}.json`
3. **User input**: Guardar en `evidence/evidence/{hotel}/input_{ts}.json`
4. **Ledger**: Agregar entrada en `evidence/ledger.json`

### 14.4 Scripts Relacionados

| Script | Uso |
|--------|-----|
| `scripts/cleanup_sessions.py` | Limpia sesiones antiguas |
| `scripts/normalize_cache_filenames.py` | Normaliza nombres de cache |

---

## 17. FASE-CAUSAL-01: SitePresenceChecker

### 17.1 Problema que Resuelve

**Desconexion critica**: El sistema generaba assets sin verificar si el sitio de produccion ya tenla la funcionalidad implementada.

**Sintomas observados:**
- FAQ schema detectado como "ausente" pero ya existia en WordPress
- Assets regenerados 7+ veces sin cambios (hotel_schema, org_schema)
- `delivery_ready_percentage: 0%` pese a multiples assets generados
- Reportes desincronizados con realidad del sitio

### 17.2 Estados de Presencia

| Estado | Significado | Accion |
|--------|-------------|--------|
| `EXISTS` | Asset ya implementado en sitio | SKIP - No regenerar |
| `EXISTS_WITH_ISSUES` | Existe pero con problemas | SKIP - Recomendar fix |
| `NOT_EXISTS` | No existe | Generar asset |
| `REDUNDANT` | Existe + ya fue entregado | SKIP definitivo |
| `VERIFICATION_FAILED` | No se pudo verificar | Warning + generar con disclaimers |

### 17.3 Genericidad del Sistema

**IMPORTANTE**: El sistema NO esta atado a ningun hotel especifico.

| Componente | Hotel Visperas | Otro Hotel |
|------------|---------------|------------|
| SitePresenceChecker | `site_url` param | `site_url` param |
| ASSET_TO_SCHEMA_MAP | Generico | Generico |
| SchemaFinder | Analiza cualquier URL | Analiza cualquier URL |

Visperas es un **laboratorio de pruebas**, no el destino final.

### 17.4 Checklist de Verificacion

- [ ] SitePresenceChecker verificado con sitio real
- [ ] Assets skippeados correctamente cuando ya existen
- [ ] Reporte refleja skipped_assets con razones
- [ ] delivery_ready_percentage calculado correctamente
- [ ] Sistema funciona con hotel generico (no hardcodeado)
