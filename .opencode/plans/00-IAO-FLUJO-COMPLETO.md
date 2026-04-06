# IAO FLUJO COMPLETO: Auditoría → Diagnóstico → Propuesta → Assets
## Sin Desconexiones — Todo Enfocado en IAO (Intelligence Augmentation Optimization)

**Versión**: 1.0
**Fecha**: 2026-03-31
**Estado**: Plan unificado para implementación

---

## DEFINICIÓN: IAO (IA Optimization)

**IAO** = Optimización para que hoteles boutique sean **citables y visibles** para LLMs (ChatGPT, Gemini, Perplexity) y asistentes de voz (Alexa, Siri, Google Assistant).

A diferecia del SEO clásico, IAO mide:
- ¿Puede un LLM **extraer** información del sitio?
- ¿Puede un LLM **citarla** correctamente?
- ¿Aparece el hotel en **respuestas de IA**?

---

## FLUJO COMPLETO (4-etapas)

```
ETAPA 1: AUDITORÍA              ETAPA 2: DIAGNÓSTICO
─────────────────────           ───────────────────
v4_comprehensive.py    ──────►   v4_diagnostic_generator.py
     │                             │
     ▼                             ▼
V4AuditResult                    DiagnosticSummary
  ├─ schema.*                       ├─ score_tecnico (KB)
  ├─ performance.*                  ├─ score_ia
  ├─ validation.*                   ├─ paquete
  ├─ citability.*                   ├─ faltantes[] (12 elem KB)
  └─ (NUEVO) seo_elements.*        └─ pain_ids[] (solo con asset)
          │                                  │
          ▼                                  ▼
     ETAPA 3: PROPUESTA              ETAPA 4: ASSETS
     ─────────────────               ─────────────
     v4_proposal_generator.py       conditional_generator.py
              │                              │
              ▼                              ▼
     Propuesta comercial          Assets generados
     (paquete + precio)          (por pain_id)
```

---

## CHECKLIST_IAO: Los 12 Elementos KB

Estos son los elementos que el sistema debe detectar, diagnosticar y resolver:

| # | Elemento KB | Impacto IAO | Asset que lo resuelve | Status |
|---|-------------|-------------|---------------------|--------|
| 1 | `ssl` | Seguridad/HTTPS obligatorio | `ssl_guide` | ❌ MISSING |
| 2 | `schema_hotel` | LLM puede leer hotel | `hotel_schema` | ✅ IMPLEMENTED |
| 3 | `schema_reviews` | AggregateRating markup | `hotel_schema` | ✅ IMPLEMENTED |
| 4 | `LCP_ok` | Performance mínimo | `performance_audit` | ✅ IMPLEMENTED |
| 5 | `CLS_ok` | UX estable | `optimization_guide` | ✅ IMPLEMENTED |
| 6 | `contenido_extenso` | Citabilidad LLM | `optimization_guide` | ⚠️ CitabilityScorer existe |
| 7 | `open_graph` | Social sharing | `og_tags_guide` | ❌ MISSING |
| 8 | `schema_faq` | FAQ en IA responses | `faq_page` | ✅ IMPLEMENTED |
| 9 | `nap_consistente` | Confianza local | `whatsapp_button` | ⚠️ Solo WhatsApp |
| 10 | `imagenes_alt` | Accesibilidad IA | `alt_text_guide` | ❌ MISSING |
| 11 | `blog_activo` | Autoridad/contenido | `blog_strategy_guide` | ❌ MISSING |
| 12 | `redes_activas` | Señales E-E-A-T | `social_strategy_guide` | ❌ MISSING |

---

## ELEMENTO_KB_TO_PAIN_ID: Fuente de Verdad

**AL IMPLEMENTAR**: Esta constante debe existir en `v4_diagnostic_generator.py`

```python
# ============================================================
# ELEMENTO_KB_TO_PAIN_ID — ÚNICA FUENTE DE VERDAD
# Conecta elementos CHECKLIST_IAO → pain_id → asset
# ============================================================
ELEMENTO_KB_TO_PAIN_ID: Dict[str, tuple] = {
    # Elemento KB: (pain_id, asset_principal, asset_secundario)
    # CORREGIDO v3: schema_reviews → no_schema_reviews (no missing_reviews)
    "ssl":                ("no_ssl",              "ssl_guide",           None),
    "schema_hotel":      ("no_hotel_schema",     "hotel_schema",        None),
    "schema_reviews":     ("no_schema_reviews",   "hotel_schema",        None),  # ANTES: missing_reviews
    "LCP_ok":             ("poor_performance",    "performance_audit",   "optimization_guide"),
    "CLS_ok":             ("poor_performance",    "optimization_guide",  None),
    "contenido_extenso":  ("low_citability",      "optimization_guide",  None),
    "open_graph":         ("no_og_tags",          "og_tags_guide",       None),
    "schema_faq":         ("no_faq_schema",       "faq_page",            None),
    "nap_consistente":    ("whatsapp_conflict",   "whatsapp_button",     None),
    "imagenes_alt":       ("missing_alt_text",    "alt_text_guide",      None),
    "blog_activo":        ("no_blog_content",     "blog_strategy_guide", None),
    "redes_activas":      ("no_social_links",     "social_strategy_guide", None),
}

# Elementos cuyo asset principal está IMPLEMENTED
ELEMENTOS_MONETIZABLES: set = {
    elem for elem, (_, asset, _) in ELEMENTO_KB_TO_PAIN_ID.items()
    if asset and is_asset_implemented(asset)
}

# Elementos cuyo asset está MISSING (visibles en scoring, no en monetización)
ELEMENTOS_NO_MONETIZABLES: set = {
    elem for elem, (_, asset, _) in ELEMENTO_KB_TO_PAIN_ID.items()
    if asset and not is_asset_implemented(asset)
}
```

---

## PESO KB: Score Técnico (0-100)

```python
PESOS_KB = {
    "ssl":               10,  # Básico pero necesario
    "schema_hotel":      15,  # Crítico para IA
    "schema_reviews":    15,  # Crítico para IA
    "LCP_ok":            10,  # Umbral técnico
    "CLS_ok":             5,  # UX
    "contenido_extenso": 10,  # Citabilidad
    "open_graph":         5,  # Social
    "schema_faq":         8,  # FAQ en IA
    "nap_consistente":    7,  # Confianza local
    "imagenes_alt":       5,  # Accesibilidad
    "blog_activo":        5,  # Autoridad
    "redes_activas":      5,  # E-E-A-T
}
# Total: 100 puntos
```

---

## ETAPA 1: AUDITORÍA — Datos que Produce

### V4AuditResult (actual vs objetivo)

| Campo | Actual | Objetivo | Desconexión |
|-------|--------|----------|-------------|
| `schema.hotel_schema_detected` | ✅ | ✅ | No |
| `schema.faq_schema_detected` | ✅ | ✅ | No |
| `performance.lcp` | ✅ | ✅ | No |
| `performance.cls` | ✅ | ✅ | No |
| `validation.whatsapp_status` | ✅ | ✅ | No |
| `validation.address_status` | ❌ | ✅ | **SÍ** — falta |
| `validation.email_status` | ❌ | ✅ | **SÍ** — falta |
| `citability.overall_score` | ✅ | ✅ | No |
| `ssl` | ❌ | ✅ | **SÍ** — no existe |
| `seo_elements.open_graph` | ❌ | ✅ | **SÍ** — no existe |
| `seo_elements.imagenes_alt` | ❌ | ✅ | **SÍ** — no existe |
| `seo_elements.redes_activas` | ❌ | ✅ | **SÍ** — no existe |

### Detalle de Desconexiones en Auditoría

#### D1: `ssl` no existe en V4AuditResult
**Problema**: No hay campo `ssl` en el resultado
**Solución**: Extraer de `url.startswith("https")` — trivial

#### D2: `validation.address_status` no existe
**Problema**: CrossValidator solo valida WhatsApp
**Solución**: Extender CrossValidator con `validate_address()`

#### D3: `validation.email_status` no existe
**Problema**: No hay validación de email
**Solución**: Extender CrossValidator con `validate_email()`

#### D4-D6: SEO Elements no existen
**Problema**: No hay detectores para open_graph, imagenes_alt, redes_activas
**Solución**: Crear SEOElementsDetector con stubs

---

## ETAPA 2: DIAGNÓSTICO — Datos que Consume

### DiagnosticSummary (actual vs objetivo)

| Campo | Tipo | Origen | Status |
|-------|------|--------|--------|
| `score_tecnico` | `int` | `calcular_cumplimiento(elementos)` | ❌ No existe |
| `score_ia` | `Optional[int]` | IATester (-1=error, None=sin datos) | ⚠️ Existe pero no se usa |
| `paquete` | `str` | `sugerir_paquete(score_tecnico)` | ❌ No existe |
| `faltantes` | `List[str]` | Elementos KB que fallan | ❌ No existe |
| `pain_ids` | `List[str]` | Solo con asset IMPLEMENTED | ❌ No existe |

### Detalle de Desconexiones en Diagnóstico

#### D7: `calcular_cumplimiento()` no existe
**Problema**: No hay función para calcular score KB
**Solución**: Implementar con PESOS_KB

#### D8: `sugerir_paquete()` no existe
**Problema**: No hay función para sugerir paquete
**Solución**: 
```python
if score < 40: "basico"
elif score < 70: "avanzado"  
else: "premium"
```

#### D9: `_extraer_elementos_de_audit()` no existe
**Problema**: No hay función para mapear V4AuditResult → 12 elementos KB
**Solución**: Implementar función + ELEMENTO_KB_TO_PAIN_ID

#### D10: `_asset_para_pain()` no existe
**Problema**: No hay filtro para pain_ids con asset MISSING
**Solución**: Implementar + usar en generate()

---

## ETAPA 3: PROPUESTA — Datos que Consume

### Flujo Actual vs Propuesto

```
ACTUAL (genérico):
v4_proposal_generator.py → usa datos hardcodeados

PROPUESTO (IAO):
v4_proposal_generator.py → recibe DiagnosticSummary
    ├─ score_tecnico → determina nivel de urgencia
    ├─ pain_ids[] → para cada pain_id, buscar en PAIN_SOLUTION_MAP
    └─ faltantes[] → listar en propuesta
```

### PAIN_SOLUTION_MAP — Actualización Requerida

**PROBLEMA**: Los siguientes pain_ids NO están en el mapa actual:
- `no_ssl`
- `no_og_tags`
- `missing_alt_text`
- `no_blog_content`
- `no_social_links`

**PROBLEMA**: Los siguientes assets NO están en ASSET_CATALOG:
- `ssl_guide`
- `og_tags_guide`
- `alt_text_guide`
- `blog_strategy_guide`
- `social_strategy_guide`

---

## ETAPA 4: ASSETS — Datos que Consume

### Flujo actual

```
pain_id → PainSolutionMapper → asset_type → ASSET_CATALOG → conditional_generator
```

### Mapeo Completo IAO

| Pain ID | asset_type | ASSET_CATALOG Status | promised_by |
|---------|-----------|---------------------|-------------|
| `no_ssl` | `ssl_guide` | ❌ MISSING | `no_ssl` |
| `no_hotel_schema` | `hotel_schema` | ✅ IMPLEMENTED | `no_hotel_schema` |
| `no_schema_reviews` | `hotel_schema` | ✅ IMPLEMENTED | `no_schema_reviews` |
| `missing_reviews` | `review_plan` | ✅ IMPLEMENTED | `missing_reviews` |
| `poor_performance` | `performance_audit` | ✅ IMPLEMENTED | `poor_performance` |
| `poor_performance` | `optimization_guide` | ✅ IMPLEMENTED | `poor_performance` |
| `low_citability` | `optimization_guide` | ✅ IMPLEMENTED | `low_citability` |
| `no_og_tags` | `og_tags_guide` | ❌ MISSING | `no_og_tags` |
| `no_faq_schema` | `faq_page` | ✅ IMPLEMENTED | `no_faq_schema` |
| `whatsapp_conflict` | `whatsapp_button` | ✅ IMPLEMENTED | `whatsapp_conflict` |
| `missing_alt_text` | `alt_text_guide` | ❌ MISSING | `missing_alt_text` |
| `no_blog_content` | `blog_strategy_guide` | ❌ MISSING | `no_blog_content` |
| `no_social_links` | `social_strategy_guide` | ❌ MISSING | `no_social_links` |

### Assets MISSING: Plan de Implementación

| Asset | Prioridad | Dependencias | Notas |
|-------|----------|--------------|-------|
| `ssl_guide` | BAJA | Ninguna | Guía trivial, no requiere código |
| `og_tags_guide` | BAJA | Ninguna | Guía trivial |
| `alt_text_guide` | MEDIA | beautifulsoup4 | Requiere parsing HTML |
| `blog_strategy_guide` | BAJA | Ninguna | Estrategia sin código |
| `social_strategy_guide` | BAJA | Ninguna | Estrategia sin código |

---

## ARQUITECTURA COMPLETA SIN DESCONEXIONES

```
╔══════════════════════════════════════════════════════════════╗
║                    KB: CHECKLIST_IAO                          ║
║          12 elementos con pesos (total = 100 pts)               ║
╚══════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════╗
║  AUDITORÍA: v4_comprehensive.py                                ║
║                                                               ║
║  V4AuditResult:                                                ║
║  ├─ schema.* ✅                                                ║
║  ├─ performance.* ✅                                           ║
║  ├─ validation.* ✅ (solo WhatsApp) ⚠️                        ║
║  ├─ citability.* ✅                                            ║
║  └─ NUEVO:                                                     ║
║      ├─ ssl: bool (de url)                                     ║
║      ├─ validation.address_status: str                         ║
║      ├─ validation.email_status: str                           ║
║      └─ seo_elements: SEOElementsResult                        ║
║          ├─ open_graph: bool                                   ║
║          ├─ imagenes_alt: bool                                 ║
║          └─ redes_activas: bool                               ║
╚══════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════╗
║  DIAGNÓSTICO: v4_diagnostic_generator.py                       ║
║                                                               ║
║  ELEMENTO_KB_TO_PAIN_ID ✅ (CONSTANTE NUEVA)                   ║
║                                                               ║
║  _extraer_elementos_de_audit(audit_result) → 12 elementos     ║
║  calcular_cumplimiento(elementos) → score_tecnico             ║
║  sugerir_paquete(score_tecnico) → "basico|avanzado|premium"   ║
║                                                               ║
║  DiagnosticSummary:                                            ║
║  ├─ score_tecnico: int                                        ║
║  ├─ score_ia: Optional[int]                                    ║
║  ├─ paquete: str                                               ║
║  ├─ faltantes: List[str] (TODOS los 12)                        ║
║  └─ pain_ids: List[str] (SOLO con asset IMPLEMENTED)           ║
╚══════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════╗
║  PROPUESTA: v4_proposal_generator.py                           ║
║                                                               ║
║  Recibe DiagnosticSummary                                      ║
║  Para cadapain_id en pain_ids:                                 ║
║      → PAIN_SOLUTION_MAP[pain_id] → asset(s)                  ║
║      → Monetizar impacto                                      ║
║  Para cadapain_id con asset MISSING:                           ║
║      → Mostrar en "Requiere atención manual"                   ║
╚══════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════╗
║  ASSETS: conditional_generator.py                              ║
║                                                               ║
║  PAIN_SOLUTION_MAP (ACTUALIZADO):                              ║
║  ├─ 5 pain_ids nuevos agregados ✅                             ║
║  └─ 5 assets MISSING en ASSET_CATALOG ✅                      ║
║                                                               ║
║  Para cadapain_id con asset IMPLEMENTED:                        ║
║      → conditional_generator.generate(asset_type)              ║
║  Para cadapain_id con asset MISSING:                            ║
║      → Saltar (ya filtrado en DiagnosticSummary)               ║
╚══════════════════════════════════════════════════════════════╝
```

---

## IMPLEMENTACIÓN: 3 FASES

### FASE 1: GAP-IAO-01-02 (KB/Pain ID Alignment)
**Objetivo**: Cerrar desconexiones D7-D10 + PAIN_SOLUTION_MAP + ASSET_CATALOG

| # | Tarea | Archivo | Status |
|---|-------|---------|--------|
| 1 | Crear `ELEMENTO_KB_TO_PAIN_ID` | v4_diagnostic_generator.py | ⏳ |
| 2 | Implementar `calcular_cumplimiento()` | v4_diagnostic_generator.py | ⏳ |
| 3 | Implementar `sugerir_paquete()` | v4_diagnostic_generator.py | ⏳ |
| 4 | Implementar `_extraer_elementos_de_audit()` | v4_diagnostic_generator.py | ⏳ |
| 5 | Implementar `_asset_para_pain()` | v4_diagnostic_generator.py | ⏳ |
| 6 | Agregar 5 pain_ids a `PAIN_SOLUTION_MAP` | pain_solution_mapper.py | ⏳ |
| 7 | Agregar 5 assets a `ASSET_CATALOG` (MISSING) | asset_catalog.py | ⏳ |
| 8 | Agregar campos a `DiagnosticSummary` | data_structures.py | ⏳ |
| 9 | Modificar `generate()` para filtrar pain_ids | v4_diagnostic_generator.py | ⏳ |

### FASE 2: GAP-IAO-01-02-B (Integración de 6 Elementos)
**Objetivo**: Cerrar desconexiones D1-D6 en auditoría

| # | Tarea | Archivo | Status |
|---|-------|---------|--------|
| B1 | `_check_ssl()` | v4_comprehensive.py | ⏳ |
| B2 | Mapear `citability.overall_score` | v4_diagnostic_generator.py | ⏳ |
| B3 | Extender CrossValidator (address/email) | cross_validator.py | ⏳ |
| B4 | Crear `SEOElementsDetector` | seo_elements_detector.py (NUEVO) | ⏳ |
| B5 | Extender `V4AuditResult` | v4_comprehensive.py | ⏳ |
| B6 | Mapear elementos SEO en `_extraer_elementos_de_audit()` | v4_diagnostic_generator.py | ⏳ |

### FASE 3: GAP-IAO-01-02-C (Assets IAO Completos)
**Objetivo**: Implementar los 5 assets MISSING para IAO

| # | Tarea | Asset | Prioridad |
|---|-------|-------|----------|
| C1 | Implementar `ssl_guide` | `ssl_guide` | BAJA |
| C2 | Implementar `og_tags_guide` | `og_tags_guide` | BAJA |
| C3 | Implementar `alt_text_guide` | `alt_text_guide` | MEDIA |
| C4 | Implementar `blog_strategy_guide` | `blog_strategy_guide` | BAJA |
| C5 | Implementar `social_strategy_guide` | `social_strategy_guide` | BAJA |

---

## VERIFICACIÓN DE FLUJO

### Test de Integración Completa

```python
def test_iao_flujo_completo():
    """
    Verifica que el flujo IAO no tiene desconexiones.
    """
    # 1. AUDITORÍA → produce V4AuditResult con 12 elementos
    audit_result = auditor.audit("https://hotelvisperas.com")
    
    # 2. DIAGNÓSTICO → extrae elementos KB
    generator = V4DiagnosticGenerator()
    elementos = generator._extraer_elementos_de_audit(audit_result)
    
    assert len(elementos) == 12, "Deben ser 12 elementos KB"
    for elem in ELEMENTO_KB_TO_PAIN_ID.keys():
        assert elem in elementos, f"Falta elemento: {elem}"
    
    # 3. Score técnico calculado correctamente
    score = calcular_cumplimiento(elementos)
    assert 0 <= score <= 100
    
    # 4. Paquete sugerido según score
    paquete = sugerir_paquete(score)
    assert paquete in ["basico", "avanzado", "premium"]
    
    # 5. DiagnosticSummary creado
    summary = generator.generate(audit_result, ...)
    
    # 6. faltantes = elementos que fallan
    for f in summary.faltantes:
        assert f in ELEMENTO_KB_TO_PAIN_ID
    
    # 7. pain_ids = solo con asset IMPLEMENTED
    for pid in summary.pain_ids:
        asset = PainSolutionMapper.PAIN_SOLUTION_MAP[pid]["assets"][0]
        assert is_asset_implemented(asset), f"Asset {asset} no implementado para {pid}"
    
    # 8. PROPUESTA → monetiza pain_ids
    proposal = proposal_generator.generate(summary, ...)
    for pid in summary.pain_ids:
        assert pid in proposal.monetized_pains
    
    # 9. ASSETS → genera para pain_ids con asset
    for pid in summary.pain_ids:
        asset = PainSolutionMapper.PAIN_SOLUTION_MAP[pid]["assets"][0]
        if is_asset_implemented(asset):
            asset_result = conditional_generator.generate(asset, ...)
            assert asset_result is not None
```

---

## RESUMEN DE DESCONEXIONES

| ID | Etapa | Desconexión | Solución | Status |
|----|-------|-------------|----------|--------|
| D1 | Auditoría | ssl no existe | `_check_ssl()` | ⏳ |
| D2 | Auditoría | address_status no existe | `validate_address()` | ⏳ |
| D3 | Auditoría | email_status no existe | `validate_email()` | ⏳ |
| D4 | Auditoría | seo_elements no existe | `SEOElementsDetector` | ⏳ |
| D5 | Auditoría | open_graph no existe | `SEOElementsDetector.detect()` | ⏳ |
| D6 | Auditoría | imagenes_alt no existe | `SEOElementsDetector.detect()` | ⏳ |
| D7 | Diagnóstico | calcular_cumplimiento() no existe | Implementar | ⏳ |
| D8 | Diagnóstico | sugerir_paquete() no existe | Implementar | ⏳ |
| D9 | Diagnóstico | _extraer_elementos_de_audit() no existe | Implementar | ⏳ |
| D10 | Diagnóstico | _asset_para_pain() no existe | Implementar | ⏳ |
| D11 | Diagnóstico | schema_reviews → pain_id incorrecto | Crear no_schema_reviews | ✅ CORREGIDO v3 |
| D12 | Propuesta | faltantes incluye assets MISSING | Separar faltantes_monetizables | ✅ CORREGIDO v3 |

**Total: 12 desconexiones (D11-D12 corregidas en v3)**

---

## PRÓXIMOS PASOS

1. **Ejecutar FASE 1** (GAP-IAO-01-02 original)
   - Crear ELEMENTO_KB_TO_PAIN_ID
   - Implementar funciones de scoring
   - Actualizar PAIN_SOLUTION_MAP y ASSET_CATALOG

2. **Ejecutar FASE 2** (GAP-IAO-01-02-B)
   - Integrar 6 elementos en auditoría
   - Verificar flujo completo

3. **Ejecutar FASE 3** (GAP-IAO-01-02-C)
   - Implementar 5 assets MISSING

---

**Documento creado**: 2026-03-31
**Última actualización**: 2026-03-31
**Estado**: Listo para implementación
