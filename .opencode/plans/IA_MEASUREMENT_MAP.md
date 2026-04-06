# IA_MEASUREMENT_MAP.md

**Proyecto**: GAP-IAO-01 — Auditoría de IAO para iah-cli  
**Fase**: GAP-IAO-01-01  
**Fecha**: 2026-03-30  
**Objetivo**: Mapear realidad de datos entre AUDITORÍA → DIAGNÓSTICO → PROPUESTA → ASSETS

---

## 1. Flujo de Datos Completo

```
[AUDITORÍA]
    │
    ▼
    V4AuditResult (datos crudos: schema, gbp, performance, validation)
    │
    ▼
[DIAGNÓSTICO]
    │  V4DiagnosticGenerator.generate() → DiagnosticSummary
    │  Fields: hotel_name, critical_problems_count, quick_wins_count,
    │          overall_confidence, top_problems[], validated_data_summary{},
    │          coherence_score
    ▼
    PainSolutionMapper.detect_pains() → Pain[]
    │
    ▼
[PROPUESTA]
    │  V4ProposalGenerator.generate(diagnostic_summary, financial_scenarios, asset_plan)
    │  Recibe: DiagnosticSummary + FinancialScenarios + List[AssetSpec]
    ▼
    recommendations / Pain IDs → AssetSpecs
    │
    ▼
[ASSETS]
       ConditionalGenerator.generate(asset_type, validated_data, hotel_name, hotel_id)
       Recibe: validated_data (Dict), NO recibe "faltantes" directamente
```

---

## 2. Elementos CHECKLIST_IAO — Estado Real

> Basado en los 12 elementos que debe detectar el sistema según KB (FASE-0: usar AEOKPIs existente)

| # | Elemento KB | Detectado por | Existe en V4AuditResult? | Data Real? | Bloqueante? |
|---|-------------|--------------|--------------------------|------------|-------------|
| 1 | ssl | ¿Campo `ssl` o `https`? | ❌ NO | — | No (no es 12 KB original) |
| 2 | schema_hotel | `schema.hotel_schema_detected` | ✅ YES | ✅ Bool | No |
| 3 | schema_reviews | `gbp.rating` es proxy, no Schema.org `AggregateRating` | ❌ NO tiene `has_aggregate_rating` | ⚠️ Solo rating numérico | No (proxy existe) |
| 4 | LCP_ok | `performance.lcp` | ✅ YES | ✅ Float | No |
| 5 | CLS_ok | `performance.cls` | ✅ YES | ✅ Float | No |
| 6 | contenido_extenso | ¿Campo `content_length`? | ❌ NO encontrado | — | No |
| 7 | open_graph | ¿Campo `has_og_tags`? | ❌ NO encontrado | — | No |
| 8 | schema_faq | `schema.faq_schema_detected` | ✅ YES | ✅ Bool | No |
| 9 | nap_consistente | `validation.whatsapp_status` | ⚠️ Solo WhatsApp | ⚠️ Solo teléfono | No |
| 10 | imagenes_alt | ¿Campo `images_without_alt`? | ❌ NO encontrado | — | No |
| 11 | blog_activo | ¿Campo `has_blog`? | ❌ NO encontrado | — | No |
| 12 | redes_activas | ¿Campo `social_links`? | ❌ NO encontrado | — | No |

### Detalle de Elementos:

**ssl**: No existe campo `ssl` o `https_detected` en ningún auditor. El `v4_comprehensive.py` usa PageSpeed API pero no extrae si el sitio tiene HTTPS.

**schema_reviews**: V4AuditResult tiene `gbp.rating` (float) pero NO tiene campo `has_aggregate_rating` en SchemaValidation. El sistema usa `gbp.rating` como proxy pero no valida Schema.org AggregateRating.

**contenido_extenso**: No hay campo `content_length`, `word_count` o similar en V4AuditResult ni en data_structures.py.

**open_graph**: No existe campo `has_og_tags`, `og_image`, etc. en ningún dataclass del audit.

**nap_consistente**: Solo valida `whatsapp_status` en CrossValidationResult. No hay validación de dirección (`address_web` vs `address_gbp`) ni email.

**imagenes_alt**: No existe `images_without_alt` en PerformanceData ni en ningún auditor.

**blog_activo**: No hay `has_blog` en ningún campo de V4AuditResult.

**redes_activas**: No hay `social_links` en ningún campo.

---

## 3. Gaps de Datos Identificados

### Gap 1: SSL no detectado
- **Descripción**: No existe campo ssl o https en V4AuditResult
- **Impacto**: No se puede verificar si el sitio tiene HTTPS activo
- **Solución sugerida**: Usar AEOKPIs existente. PageSpeed API ya requiere HTTPS para funcionar. Se puede inferir del status de PageSpeed o agregar un campo simple `has_https: bool = url.startswith('https')`

### Gap 2: Schema Reviews (AggregateRating) no verificado
- **Descripción**: `gbp.rating` es proxy pero no valida Schema.org `AggregateRating`
- **Impacto**: El诊断 no puede distinguir si hay markup de reviews vs solo mostrar rating de GBP
- **Solución sugerida**: Agregar `schema.has_aggregate_rating: bool` a SchemaValidation dataclass. Requiere agregar detección en `v4_comprehensive.py`

### Gap 3: Open Graph no detectado
- **Descripción**: No existe campo `has_og_tags` en ningún auditor
- **Impacto**: No se puede incluir Open Graph en el diagnóstico de IAO
- **Solución sugerida**: No es bloqueante para GAP-01-02. Se puede inferir de `metadata` si existe o agregar post-audit

### Gap 4: Imágenes sin ALT no detectadas
- **Descripción**: No existe campo `images_without_alt` 
- **Impacto**: No se puede generar asset de accesibilidad
- **Solución sugerida**: No es bloqueante. Fase posterior si hay demanda

### Gap 5: Blog y Redes no detectados
- **Descripción**: `has_blog` y `social_links` no existen
- **Impacto**: No se incluyen en diagnóstico
- **Solución sugerida**: No es bloqueante. Se pueden agregar post-audit

### Gap 6: NAP parcialmente validado (solo WhatsApp)
- **Descripción**: Solo `whatsapp_status` en CrossValidationResult, no dirección ni email
- **Impacto**: Validación de NAP incompleta
- **Solución sugerida**: Agregar `address_web`, `address_gbp` y validar match. Por ahora solo WhatsApp es el pain point principal

### Gap 7: Contenido extenso no medido
- **Descripción**: No hay `content_length` o `word_count`
- **Impacto**: No se puede detectar si contenido es demasiado corto para citación IA
- **Solución sugerida**: `citability` scorer (líneas 375-385 en pain_solution_mapper.py) ya tiene `low_citability` pain. El citability score se calcula desde `audit_result.citability.overall_score`

---

## 4. Inconsistencias de Pain IDs

### _identify_brechas() vs PainSolutionMapper

| Brecha en _identify_brechas() | Pain ID usado | En PainSolutionMapper? | Asset(s) | Consistencia |
|--------------------------------|--------------|------------------------|----------|--------------|
| "Visibilidad Local (Google Maps)" | (ninguno - solo impacto 0.30) | ❌ NO | — | ❌ Gap |
| "Sin Schema de Hotel" | Implied `no_hotel_schema` | ✅ YES | hotel_schema | ✅ |
| "Canal Directo Cerrado (Sin WhatsApp)" | Implied `no_whatsapp_visible` | ✅ YES | whatsapp_button | ✅ |
| "Web Lenta (Abandono Móvil)" | Implied `poor_performance` | ✅ YES | performance_audit, optimization_guide | ✅ |
| "Datos Inconsistentes" | Implied `whatsapp_conflict` | ✅ YES | whatsapp_button | ✅ |
| "Oportunidad FAQ/Rich Snippets" | Implied `no_faq_schema` | ✅ YES | faq_page | ✅ |
| "Optimización GBP Incompleta" | Implied `low_gbp_score` | ✅ YES | geo_playbook, review_plan | ✅ |
| "Sin Datos de Campo" | (ninguno) | ❌ NO | — | ❌ Gap |
| "Presencia IA No Optimizada" | Implied `low_ia_readiness` | ✅ YES | hotel_schema, llms_txt | ✅ |

### Pain IDs huérfanos en PainSolutionMapper (existen pero no se generan desde _identify_brechas):

| Pain ID | Assets | Detección en _identify_brechas? |
|---------|--------|--------------------------------|
| `no_motor_reservas` | barra_reserva_movil | ❌ NO |
| `no_org_schema` | org_schema | ❌ NO |
| `low_ota_divergence` | direct_booking_campaign | ❌ NO |
| `metadata_defaults` | optimization_guide | ❌ NO |
| `missing_llmstxt` | llms_txt | ❌ NO |
| `ai_crawler_blocked` | llms_txt | ❌ NO |
| `low_citability` | optimization_guide | ⚠️ Indirecta |
| `low_ia_readiness` | hotel_schema, llms_txt | ⚠️ Indirecta |

### Observación sobre Pain IDs:
- `_identify_brechas()` NO usa Pain IDs para sus internas. Solo retorna `nombre`, `impacto`, `detalle`
- `PainSolutionMapper.detect_pains()` tiene su propia lógica de detección basada en V4AuditResult
- Ambos sistemas pueden estar fuera de sincronía si el audit cambia

---

## 5. Flujo Diagnóstico → Propuesta

### DiagnosticSummary (data_structures.py líneas 247-256)

| Campo | Tipo | Existe? | Usado en propuesta? | Cómo se usa |
|-------|------|---------|-------------------|-------------|
| hotel_name | str | ✅ | ✅ | Encabezado |
| critical_problems_count | int | ✅ | ✅ | Resumen |
| quick_wins_count | int | ✅ | ✅ | Resumen |
| overall_confidence | ConfidenceLevel | ✅ | ✅ | Nivel confianza |
| top_problems | List[str] | ✅ | ✅ | Lista de problemas |
| validated_data_summary | Dict[str, Any] | ✅ | ✅ | Datos cruzados |
| coherence_score | Optional[float] | ✅ | ✅ | Score coherencia |
| **score_tecnico** | — | ❌ | ❌ | No existe |
| **score_ia** | — | ❌ | ❌ | No existe |
| **faltantes** | — | ❌ | ❌ | No existe |
| **paquete** | — | ❌ | ❌ | No existe |

### Backwards Compatibility:
- DiagnosticSummary NO tiene `score_tecnico`, `score_ia`, `faltantes`, ni `paquete`
- El template de propuesta puede estar esperando estos campos pero recibe valores None o falla silenciosamente
- **No hay backwards compatibility layer** para campos faltantes

---

## 6. Flujo Propuesta → Assets

### V4ProposalGenerator.generate() (líneas 68-101)

```python
def generate(
    self,
    diagnostic_summary: DiagnosticSummary,  # ✅ Existe
    financial_scenarios: FinancialScenarios,  # ✅ Existe
    asset_plan: List[AssetSpec],  # ✅ Existe
    hotel_name: str,  # ✅ Existe
    output_dir: str,  # ✅ Existe
    price_monthly: Optional[int] = None,
    setup_fee: Optional[int] = None,
    audit_result: Optional[Any] = None,  # ⚠️ Optional, no se usa para assets
    pricing_result: Optional[PricingResolutionResult] = None,  # ⚠️ Optional
) -> str
```

### ConditionalGenerator.generate() (líneas 62-95)

```python
def generate(
    self,
    asset_type: str,  # ✅
    validated_data: Dict,  # ✅
    hotel_name: str,  # ✅
    hotel_id: str,  # ✅
    hotel_context: Optional[Dict[str, Any]] = None,  # ⚠️ Optional
    site_url: Optional[str] = None  # ⚠️ Optional
) -> Dict[str, Any]
```

### Gap: La propuesta NO pasa `faltantes` a assets directamente

- La propuesta recibe `asset_plan: List[AssetSpec]`
- `AssetSpec` tiene `pain_ids: List[str]` (línea 220)
- El flujo es: Pain → Solution → AssetSpec.pain_ids
- NO hay un campo `faltantes` que se pase como lista separada

---

## 7. Recomendación de Implementación (GAP-IAO-01-02)

### Prioridad 1: Bloqueantes para el flujo básico

- [x] SSL — No es bloqueante (proxy: PageSpeed requiere HTTPS)
- [x] schema_hotel — ✅ Existe
- [x] schema_faq — ✅ Existe
- [x] LCP_ok — ✅ Existe  
- [x] CLS_ok — ✅ Existe
- [x] WhatsApp — ✅ Existe (partial NAP)

### Prioridad 2: Elementos que existen como Pain ID pero no como dato auditado

- [ ] `no_motor_reservas` — Pain existe, detección NO existe en audit
- [ ] `no_org_schema` — Pain existe, detección existe en schema.org_schema_detected
- [ ] `metadata_defaults` — Pain existe, requiere `audit_result.metadata.has_issues`

### Prioridad 3: Elementos faltantes en V4AuditResult (no bloqueantes para GAP-01-02)

- [ ] SSL detection (has_https)
- [ ] Open Graph (has_og_tags)
- [ ] Contenido extenso (content_length)
- [ ] Imágenes sin ALT (images_without_alt)
- [ ] Blog activo (has_blog)
- [ ] Redes activas (social_links)

### Acciones para GAP-IAO-01-02:

1. **Usar AEOKPIs existente** — No crear clases nuevas. Extender dataclasses existentes si es necesario
2. **Normalizar Pain IDs** — `_identify_brechas()` debe usar Pain IDs oficiales del PainSolutionMapper
3. **Completar NAP** — Agregar `address_web` y `address_gbp` en CrossValidationResult
4. **Schema Reviews** — Agregar `schema.has_aggregate_rating: bool` si es necesario
5. **NO agregar campos que no se usarán** — Los elementos faltantes (Gap 3-5) pueden esperar

---

## 8. Resumen de Hallazgos

| Área | Estado | Notas |
|------|--------|-------|
| V4AuditResult → KB | ⚠️ 5/12 elementos reales | 7 usan默认值 (False) hasta detectores nuevos |
| _identify_brechas() vs PainMapper | ❌ DESCONEXIÓN CRÍTICA | No retornaba pain_id — GAP-IAO-01-02 lo corrige |
| DiagnosticSummary → Propuesta | ❌ INCOMPLETO | Faltaban 5 campos KB — GAP-IAO-01-02 los agrega |
| Propuesta → Assets | ✅ Flujo existe | pero requiere pain_ids desde brecha |
| Backwards Compatibility | ⚠️ Parcial | GAP-IAO-01-02 agrega campos con defaults None |

---

## 9. Actualización GAP-IAO-01-00 (2026-03-31)

### Componentes huérfanos — VERIFICADOS

| Componente | Status | Implementación |
|------------|--------|----------------|
| IATester.test_hotel() | ✅ FUNCIONA | APIs reales (Perplexity, OpenAI, ProviderAdapter) |
| BingProxyTester.test_visibility() | ✅ FUNCIONA | Scraping Bing con BeautifulSoup |
| AEOKPIs.calculate_composite_score() | ✅ FUNCIONA | Retorna -1 si sin datos |

### Desconexión crítica descubierta

`_identify_brechas()` (v4_diagnostic_generator.py línea 930) retornaba brechas por **nombre**, no por `pain_id`. Esto rompía la cadena:

```
_identify_brechas() → Pain ID NO传到→ PainSolutionMapper → Assets
```

**Solución en GAP-IAO-01-02**: `_identify_brechas()` ahora retorna `pain_id` para cada brecha.

### Elementos detectables ACTUALIZADOS (5/12)

| # | Elemento | Detector | Peso | Status |
|---|----------|---------|------|--------|
| 1 | ssl | `url.startswith('https')` | 10 | ✅ Trivial |
| 2 | schema_hotel | `schema.hotel_schema_detected` | 15 | ✅ Real |
| 3 | schema_reviews | `bool(gbp.rating)` | 15 | ✅ Proxy |
| 4 | LCP_ok | `lcp <= 2.5` | 10 | ✅ Real |
| 5 | CLS_ok | `cls <= 0.1` | 5 | ✅ Real |
| 6 | contenido_extenso |默认值 False | 10 | ❌ Sin detector |
| 7 | open_graph |默认值 False | 5 | ❌ Sin detector |
| 8 | schema_faq | `schema.faq_schema_detected` | 8 | ✅ Real |
| 9 | nap_consistente | Solo WhatsApp | 7 | ⚠️ Parcial |
| 10 | imagenes_alt |默认值 False | 5 | ❌ Sin detector |
| 11 | blog_activo |默认值 False | 5 | ❌ Sin detector |
| 12 | redes_activas |默认值 False | 5 | ❌ Sin detector |

---

**Documento creado**: 2026-03-30
**Actualización GAP-IAO-01-00**: 2026-03-31
**Auditor**: Hermes CLI
**Estado**: ✅ Activo — GAP-IAO-01-02 en progreso
