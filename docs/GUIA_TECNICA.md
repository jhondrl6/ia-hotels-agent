# Guía Técnica IA Hoteles Agent CLI

**Ultima actualizacion:** 8 Abril 2026
**Version:** 4.25.3 (Fix AEO Score - Pendiente de datos eliminado)
**Audiencia:** Desarrolladores, DevOps, Contribuidores

## Notas de Cambios v4.25.3 - Fix AEO Score "Pendiente de datos"

**Fecha:** 8 Abril 2026

### Resumen

El score AEO del diagnostico v4complete mostraba "0 (Pendiente de datos)" en todos los hoteles porque `_calculate_aeo_score()` solo usaba PageSpeed API. Se implemento scoring completo de 4 componentes y deteccion real de Open Graph. FASE-C verifico la integracion end-to-end sin regresiones.

### Modulos Afectados

#### 1. seo_elements_detector.py (FASE-A)
- Stub reemplazado con implementacion real BeautifulSoup
- `_detect_open_graph()`: detecta `<meta property="og:*">`, requiere og:title + og:description
- `_detect_images_alt()`: cuenta imagenes sin atributo alt, pasa si <20%
- `_detect_social_links()`: detecta 8 dominios sociales

#### 2. v4_diagnostic_generator.py (FASE-B)
- `_calculate_aeo_score()` reescrito (lineas 1324-1378):
  - **ANTES**: solo verificaba `performance.mobile_score` → "0 (Pendiente de datos)" si PageSpeed fallaba
  - **AHORA**: scoring de 4 componentes x 25pts = 100pts:
    - Schema Hotel valido → +25pts (detectado no valido → +10pts)
    - FAQ Schema valido → +25pts (detectado no valido → +10pts)
    - Open Graph detectado → +25pts (via `hasattr` para compatibilidad)
    - Citabilidad tiers → 70→+25, 40→+15, >0→+5, None→0pts
  - Retorna string numerico ("0", "25", "50", etc.) compatible con `_get_score_status()`
  - Usa `hasattr()` para `seo_elements` y `citability` (campos opcionales en V4AuditResult)

#### 3. Templates (FASE-C verificado, sin cambios)
- v6 linea 49: `${aeo_score}/100` → renderiza numero (ej: "50/100")
- v4 linea 40: `${schema_infra_score}` → mapeado a `_calculate_aeo_score()` (L514)

### Backwards Compatibility
- Interfaz de `SEOElementsResult` sin cambios (mismos campos, mismos tipos)
- `_calculate_aeo_score()` retorna string numerico compatible con `_get_score_status()`
- Templates no requieren cambios (`${aeo_score}` renderiza numero como antes)
- Benchmark regional `aeo_score_ref` (default 20) sigue siendo coherente

### Tests
- 24 tests nuevos (9 FASE-A + 15 FASE-B)
- 0 regresiones
- `run_all_validations.py --quick` 4/4 pasan

### FASE-D: 5 Bugs Medios + seo_elements Serialization

**Resumen**: Corrección de 5 bugs medios (dead code, claves duplicadas, inconsistencia de confidence, pipe markdown, sufijo /100) + serialización faltante de `seo_elements` en `V4AuditResult.to_dict()`.

**Modulos afectados**:

#### 3a. v4_diagnostic_generator.py (FASE-D)
- **MED-1**: Eliminación de 148 líneas dead code — dos definiciones de `_compute_opportunity_scores` e `_inject_brecha_scores`. La segunda definición (FASE-C) es la productiva; la primera (FASE-B legacy) silenciaba a la segunda por shadowing.
- **MED-2**: Eliminadas 4 claves `*_regional_avg` duplicadas en dict de template data. Python usaba la última silenciosamente.
- **MED-3**: `confidence.value` → `confidence.value.upper()` en WhatsApp. Otros campos ya usaban 'ESTIMATED'/'VERIFIED' en mayúsculas.
- **MED-4**: Tabla markdown scorecard — filas tenían `||` o `|||` al inicio en vez de `|`, rompiendo alineación.
- **MED-5**: AEO score en template ahora incluye `/100` para consistencia visual.

#### 3b. v4_comprehensive.py (FASE-D)
- **SER-1**: `V4AuditResult.to_dict()` ahora serializa campo `seo_elements` completo (8 campos: open_graph, imagenes_alt, redes_activas, confidence, notes, open_graph_tags, images_without_alt, social_links_found). Sin este fix, `audit_report.json` perdía datos OG, imágenes sin alt y enlaces sociales.
- **SER-1**: `"seo_elements_detection"` agregado a `executed_validators` en la auditoría.

**Arquitectura**: `to_dict()` es el serializador usado por `main.py` para persistir `audit_report.json`. Antes de SER-1, el detector `SEOElementsDetector` ejecutaba y asignaba resultado a `V4AuditResult.seo_elements`, pero el JSON persistido no contenía esos datos. El pipeline de datos fluye: Detector → V4AuditResult.seo_elements → to_dict() → audit_report.json. SER-1 cierra la brecha de persistencia.

**Backwards Compatibility**: Totalmente backwards compatible. `seo_elements` es campo opcional (`Optional[SEOElementsResult]`). El bloque `if self.seo_elements:` solo agrega al dict si existe. Eliminación de dead code no afecta comportamiento (métodos eliminados nunca se ejecutaban).

---

## Notas de Cambios v4.21.0 - Consolidacion AEO/IAO

**Fecha:** 6 Abril 2026
**Version:** 4.25.0 (FASE-E: Micro-Content Local Generator)

## Notas de Cambios v4.25.0 - Micro-Content Local Generator

**Fecha:** 6 Abril 2026
**Version:** 4.25.0 (FASE-E: Micro-Content Local Generator)

### Resumen

Generador de 3-5 paginas de contenido local orientadas a keywords long-tail para hoteles boutique del Eje Cafetero. Add-on comercial vendible ($50K COP por 3 paginas) al Kit Hospitalidad Digital. Cada pagina tiene keyword target, 800-1200 palabras, schema Article JSON-LD, y link a reservas directas.

### Modulos Afectados

#### 1. modules/asset_generation/local_content_generator.py (NUEVO)
- Dataclasses: LocalContentPage (keyword_target, title, slug, content_md, schema_article, internal_links, meta_description, word_count), LocalContentSet (hotel_name, location, pages, total_word_count)
- LocalContentGenerator.generate_content_set(): genera 3-5 paginas segun tipo de hotel
- KEYWORD_TEMPLATES por tipo: termales (5), parque_natural (5), pueblo_patrimonio (5), cafe (5), boutique (5), general (5)
- KEYWORD_PRIORITY: heuristica de volumen estimado para ordenar keywords
- Contenido expandible: 6-8 secciones por pagina (intro, contexto, informacion, practica, cultura, recomendaciones, datos_utiles, conclusion)
- Schema Article JSON-LD con @context, @type, headline, description, author, publisher, keywords, inLanguage
- Meta description 150-160 chars
- Internal links: home del hotel + link a reservas WhatsApp
- content_passes_scrubber(): metodo estatico que detecta frases AI genericas
- Compatible con ContentScrubber de FASE-B

#### 2. modules/asset_generation/templates/local_content/page_template.md (NUEVO)
- Template de prompt para generacion LLM
- Reglas: 800-1200 palabras, 4-5 secciones H2, tono informativo no vendedor

#### 3. modules/asset_generation/templates/local_content/keyword_selection.md (NUEVO)
- Guia para seleccionar keywords por tipo de hotel con priorizacion

#### 4. modules/asset_generation/asset_catalog.py (MODIFICADO)
- Entrada local_content_page registrada con status IMPLEMENTED

### Tests
15 tests nuevos en test_local_content_generator.py. 0 regresiones.

**Version:** 4.23.0 (FASE-D: Google Search Console Integration)

### Resumen

Integracion de Google Search Console como fuente de datos para el diagnostico, pasando de estimaciones cualitativas ("0% confianza") a datos reales de keywords, posiciones y CTR del hotel. GSC es 100% opcional -- el flujo v4complete funciona completamente sin GSC.

### Modulos Afectados

#### 1. modules/analytics/google_search_console_client.py (NUEVO)
- Cliente GSC usando webmasters v3 API con service account
- Dataclasses: GSCQueryData, GSCPageData, GSCReport
- Metodos: is_configured(), get_search_analytics(), get_top_opportunities()
- Graceful fallback: retorna GSCReport con is_available=False sin credenciales
- Reutiliza las mismas credenciales de GA4 (config/google-analytics-key.json)
- Scope: https://www.googleapis.com/auth/webmasters.readonly
- Costo API: GRATIS

#### 2. modules/analytics/data_aggregator.py (NUEVO)
- Unifica datos GA4 + GSC en UnifiedAnalyticsData
- Confidence level: LOW (0 fuentes), MEDIUM (1 fuente), HIGH (2 fuentes)
- Metricas derivadas: estimated_ia_visibility, organic_health_score
- Graceful degradation: funciona sin GSC, sin GA4, o sin ambos

#### 3. modules/onboarding/add_gsc_step.py (NUEVO)
- Paso GSC opcional en onboarding del hotel
- ask_gsc_during_onboarding(): pregunta si tiene GSC, pide site_url
- apply_gsc_config(): guarda configuracion GSC en config del hotel

#### 4. modules/commercial_documents/v4_diagnostic_generator.py (MODIFICADO)
- Integration GSC en seccion "Fuentes de Datos" del diagnostico
- Con GSC: muestra impresiones, posiciones, CTR reales
- Sin GSC: fallback honesto con instruccion de activacion

#### 5. data_models/analytics_status.py (MODIFICADO)
- Agregados campos: gsc_available, gsc_error, gsc_status_text
- Nueva funcion: gsc_status_for_template()

### Tests

33 tests nuevos: 14 en test_google_search_console_client.py + 19 en test_data_aggregator.py.

## Notas de Cambios v4.21.0 - Consolidacion AEO/IAO

**Fecha:** 4 Abril 2026

### Resumen

Eliminacion de redundancia entre scores AEO e IAO (ambos median infraestructura de datos estructurados) y score de Voice Readiness (hardcodeado "--"). Se unifico todo bajo un unico score AEO. Adicionalmente, gap_analyzer se reestructuro de 3 a 2 pilares.

### Modulos Afectados

#### 1. v4_diagnostic_generator.py
**Problema**: 3 metodos redundantes o dead code: `_calculate_iao_score()` (fallback a `_calculate_schema_infra_score()`), `_calculate_score_ia()` (duplicado), `_calculate_voice_readiness_score()` (retornaba "--" hardcodeado).
**Solucion**:
- Eliminados `_calculate_iao_score()`, `_calculate_score_ia()`, `_calculate_voice_readiness_score()`
- Renombrado `_calculate_schema_infra_score()` -> `_calculate_aeo_score()`
- Template v6: scorecard de 5 filas a 4 filas (GEO, GBP, AEO, SEO)
- Variables de template eliminadas: `iao_score`, `iao_status`, `voice_readiness_score`, `voice_readiness_status`

#### 2. gap_analyzer.py
**Problema**: Modelo de 3 pilares incluia "Momentum IA" (basado en IAO, score redundante).
**Solucion**:
- Eliminada referencia a "Momentum IA" / 3 pilares
- Redistribuido a 2 pilares: Pilar 1 (GBP & Voz Cercana) + Pilar 2 (Datos JSON-LD para IA / AEO)
- Prompt del LLM actualizado al modelo 2-Pilares

#### 3. report_builder.py
**Problema**: Metodo `_calculate_iao_score()` duplicado + referencias a IAO en scorecards.
**Solucion**:
- Eliminado `_calculate_iao_score()` y todas las referencias a IAO
- Scorecard V6 simplificado: eliminada fila "Score IA Avanzado (IAO)"

### Backwards Compatibility

- Variables de template eliminadas (iao_score, iao_status, voice_readiness_score, voice_readiness_status): si algun template personalizado las referencia, fallara con KeyError en Template.safe_substitute()
- Metodos eliminados son internos, no son API publica del modulo
- El score AEO (_calculate_aeo_score) fue reescrito en v4.25.3: scoring de 4 componentes x 25pts (Schema valido + FAQ valido + OG detectado + Citabilidad). Ya NO mantiene la logica del anterior schema_infra_score
- aeo_metrics_gen.py se mantiene como modulo tecnico interno

## Notas de Cambios v4.20.0 - Agent Harness v3.2.0 Refactor

**Fecha:** 3 Abril 2026

### Resumen

Refactor arquitectonico completo del modulo `agent_harness`. Se corrigio un syntax error critico en core.py linea 65 que impedia la delegacion recursiva de tareas, y se agregaron mejoras de fondo en thread safety, timeout protection, background task lifecycle, validacion per-task, y error learning. Version del harness: 0.3.0 -> 3.2.0.

### Modulos Afectados

#### 1. agent_harness/core.py (Orchestrator)
**Problema**: Linea 65 tenia codigo corrupto (`tokens=shlex....cmd)`) que causaba SyntaxError al intentar delegacion recursiva. Ademas, sin timeout, sin background tracking, sin validacion por tipo.
**Solucion**: 
- Fix sintaxis: `tokens = shlex.split(command)`
- `_execute_with_timeout()` con threading.Timer y configurable `default_task_timeout`
- BackgroundTaskInfo lifecycle con poll automatico
- `register_validator(task_name, fn)` para validacion per-task
- Graceful fallback de UIColors si el modulo no existe

#### 2. agent_harness/memory.py (Memory Manager)
**Problema**: Race conditions en append_log() concurrente, scan lineal O(N) de todas las sesiones por cada lookup.
**Solucion**:
- Thread safety con threading.Lock por archivo de sesion
- Escritura atomica con .tmp + rename
- Indice invertido `target_index.json` para lookup O(1) de target_id a sesiones relevantes
- `rebuild_index()` para reconstruccion en caso de corrupcion

#### 3. agent_harness/skill_router.py (Skill Router)
**Problema**: Paths relativos al CWD que fallan si se ejecuta desde otro directorio.
**Solucion**: PROJECT_ROOT resuelto como `Path(__file__).resolve().parent.parent`, todos los paths absolutos.

#### 4. agent_harness/skill_executor.py (Skill Executor)
**Problema**: dry_run=True como default (footgun), sin metricas de uso de skills.
**Solucion**: dry_run=False como default, SkillMetricsCollector persistido en CSV con stats de invocaciones, tasa de exito y duracion promedio.

#### 5. agent_harness/self_healer.py (Self Healer)
**Problema**: PlanValidator import hard al inicio, errores desconocidos se perdian sin tracking.
**Solucion**: Lazy import de PlanValidator con graceful fallback, ErrorLearner que captura y sugiere entradas al catalogo de errores.

#### 6. agent_harness/mcp_client.py (MCP Client)
**Problema**: asyncio.run() falla si hay event loop corriendo (nested loop error).
**Solucion**: Deteccion de loop + threading fallback + soporte para nest_asyncio.

#### 7. agent_harness/types.py (Type Definitions)
**Nuevo**: BackgroundTaskInfo, TaskValidator Protocol, SkillMetrics dataclass con properties success_rate y avg_duration.

## Notas de Cambios v4.19.0 - Agent Ecosystem Integration

**Fecha:** 3 Abril 2026

### Resumen

Integracion del ecosistema de agentes (.agent/, .agents/workflows/) al flujo de desarrollo diario con validacion automatica pre-commit. DOMAIN_PRIMER.md deja de ser una isla de documentacion stale y ahora tiene ciclo de vida semi-automatico con regeneracion via Doctor CLI.

### Modulos de Documentacion Afectados

#### 1. DOMAIN_PRIMER.md (v4.0.0 -> v4.19.0)

**Problema**: El archivo llevaba 5 versiones y ~5 semanas desactualizado. Modulos como analytics, geo_enrichment, quality_gates, auditors no estaban documentados. Conteo de tests falso (decia 338, directorio vacio).

**Solucion**: Regeneracion completa con escaneo en vivo de 19 modulos, 138 archivos Python, 248 clases.

#### 2. CONTRIBUTING.md

**Cambio**: Agregado DOMAIN_PRIMER.md a tablas de actualizacion manual y seccion Regenerable. Nuevo Paso 5b para verificacion post-documentacion.

#### 3. procedures.md §4

**Cambio**: Renombrado "Modificar Decision Engine" -> "Modificar Financial Engine o agregar modulos nuevos". Eliminada referencia a script fantasma `generate_domain_primer.py`.

#### 4. scripts/validate_context_integrity.py

**Cambio**: Agregados 7 modulos nuevos al mapa de validacion: analytics, geo_enrichment, quality_gates, auditors, commercial_documents, delivery, providers. Removido modulo muerto decision_engine.

#### 5. scripts/doctor.py

**Nuevo flag**: `--regenerate-domain-primer` - escanea modulos en vivo y regenera DOMAIN_PRIMER.md automaticamente.

### Scripts Afectados

| Script | Cambio |
|--------|--------|
| `doctor.py` | Nuevo flag `--regenerate-domain-primer` |
| `log_phase_completion.py` | Nuevo flag `--check-domain-primer`, DOMAIN_PRIMER en MANUAL_DOCS |
| `validate_context_integrity.py` | Modulos nuevos en module_files map |

### Backwards Compatibility

Sin cambios breaking. Solo documentacion y nuevo flag en doctor.py.

---

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

## Notas de Cambios BRECHAS-DINAMICAS (v4.25.3)

### Problema
El pipeline mostraba máximo 4 brechas en el diagnóstico debido a hardcode en 3 capas:
1. **Templates**: 4 ranuras hardcodeadas (`${brecha_1_detalle}`, etc.)
2. **Generator**: `min(..., 4)` truncaba a 4 brechas
3. **Scorer**: Solo 7 tipos mapeados en SEVERITY/EFFORT/IMPACT_MAP

### Solución
- Templates: ranuras hardcode → `${brechas_section}` dinámica
- Generator: métodos `_build_brechas_section()` y `_build_brechas_resumen_section()` generan N secciones
- Scorer: 5 nuevos tipos mapeados (total: 12 tipos)
- Mapper: fix duplicate `low_ia_readiness`, fix `optimization_guide.promised_by`

### Módulos Afectados
| Módulo | Cambio | Fase |
|--------|--------|------|
| `v4_diagnostic_generator.py` | `_build_brechas_section()`, `_build_brechas_resumen_section()`, `_inject_brecha_scores()` truncation fix | A+B |
| `templates/diagnostico_v6_template.md` | `${brechas_section}` placeholder | A |
| `templates/diagnostico_v4_template.md` | `${brechas_section}` placeholder | A |
| `opportunity_scorer.py` | 5 nuevos tipos en maps | C |
| `pain_solution_mapper.py` | Duplicate fix | D |
| `asset_catalog.py` | `promised_by` fix | D |

### Backward Compatibility
- Diagnóstico con ≤4 brechas: formato idéntico al anterior
- Diagnóstico con >4 brechas: secciones adicionales, tabla resumen expandida
- Coherence score: unaffected (0.84 en validación E2E)
- Tests existentes: 0 regresiones
