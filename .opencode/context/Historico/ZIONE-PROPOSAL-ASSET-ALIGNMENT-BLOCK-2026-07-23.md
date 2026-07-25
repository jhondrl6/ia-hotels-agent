# Contexto: Bloqueo proposal_asset_alignment — Ejecución Zi One Luxury (2026-07-23)

> **Propósito**: Documentar el hallazgo del gate `proposal_asset_alignment` (Gate 9)
> durante la ejecución v4complete para zione.co (Zi One Luxury), con toda la
> trazabilidad necesaria para diseñar un plan de refactorización en nueva sesión.

> **Última actualización**: 2026-07-23 — Auditoría exhaustiva contra código vivo.
> Ver secciones 9-12 para hallazgos ampliados de causa raíz sistémica (3 capas
> de control bypassed: publication gates → delivery_quality_report → ZIP).

---

## 1. Resumen del Hallazgo

La ejecución v4complete para Zi One Luxury (zione.co) completó 11/11 publication
gates evaluados. Sin embargo, **proposal_asset_alignment** (Gate 9) marcó
**BLOCKED** porque 2 servicios prometidos en la propuesta comercial no tienen
assets generados correspondientes.

| Métrica | Valor |
|---------|-------|
| Alineación | 66.7% (4/6 servicios sin contar present_in_production) |
| Alineación efectiva (gate) | 75% (4/6 + 2 present_in_production = 6/8 = 75%) |
| Umbral requerido | 80% |
| Servicios alineados | 4 |
| Servicios faltantes | 2 (SEO Local, Meta Tags Sociales) |
| Servicios en producción | 2 (Botón de WhatsApp, Schema Organization) |
| **Gate 9 status** | **BLOCKED** (passed=false, status=BLOCKED, value=0.75) |

**CORRECCIÓN del documento original**: El gate report NUNCA dice "NOT_READY" para
el gate individual. El campo `status` del gate 9 es `BLOCKED`. El `readiness.status`
general sí es `NOT_READY`, pero eso es un campo distinto.

---

## 2. Servicios Prometidos vs Assets Generados

Fuente de verdad: `PROPOSAL_SERVICE_TO_ASSET` en
`modules/asset_generation/proposal_asset_alignment.py` (línea 22-31)

```
PROPOSAL_SERVICE_TO_ASSET = {
    "SEO Local":                        "optimization_guide",
    "Botón de WhatsApp":                "whatsapp_button",
    "Schema Hotel":                     "hotel_schema",
    "Schema Organization":              "org_schema",
    "Informe Mensual":                  "monthly_report",
    "Página de FAQ":                    "faq_page",
    "Meta Tags Sociales (Open Graph)":  "open_graph",
    "Optimización para IA Generativa":  "llms_txt",
}
```

### Estado en esta ejecución (verificado contra asset_generation_report.json + ZIP):

| Servicio | Asset esperado | ¿Generado? | ¿En ZIP? | Confianza |
|----------|---------------|-----------|----------|-----------|
| Schema Hotel | `hotel_schema` | ✅ | ✅ | 1.0 |
| Schema Organization | `org_schema` | — (present_in_production) | ❌ | — |
| Página de FAQ | `faq_page` | ✅ | ✅ | 0.8 |
| Optimización para IA | `llms_txt` | ✅ | ✅ | 1.0 |
| Informe Mensual | `monthly_report` | ✅ | ✅ | 1.0 |
| Botón de WhatsApp | `whatsapp_button` | ❌ (skipped — "ya existe en sitio") | ❌ | — |
| **SEO Local** | `optimization_guide` | **❌ NO GENERADO** | **❌** | — |
| **Meta Tags Sociales** | `open_graph` | **❌ NO GENERADO** | **❌** | — |

**NUEVO**: 4 de 8 servicios prometidos NO tienen su asset en el ZIP de delivery.
Solo 2 están justificados como present_in_production. Los otros 2 son promesas
vacías.

---

## 3. Causa Raíz: Disconexión Pain→Asset

Ambos assets (`optimization_guide` y `open_graph`) **SÍ existen** en el catálogo
y **SÍ tienen generadores**. El problema es que el **PainSolutionMapper no los
planifica** porque ningún "pain" detectado los mapea.

### 3.1 optimization_guide

**Ubicación del generador**: `modules/asset_generation/conditional_generator.py:450`
```python
elif asset_type == "optimization_guide":
    from .optimization_guide_generator import OptimizationGuideGenerator
```

**Entradas en asset_catalog** (`asset_catalog.py:183`):
```python
"optimization_guide": AssetCatalogEntry(
    asset_type="optimization_guide",
    template="optimization_guide_template.md",
    status=AssetStatus.IMPLEMENTED,
    promised_by=["metadata_defaults", "poor_performance", "low_citability", "low_content_length"],
    ...
)
```

**Mapeos en PainSolutionMapper** (`pain_solution_mapper.py:60+`):
- `poor_performance` → assets: ["performance_audit", "optimization_guide"]
  - Requiere: `core_web_vitals`, `mobile_score`
  - En esta ejecución: performance API devolvió ERROR (API key inválida, audit_report.json: `mobile_score: null, status: "ERROR"`)
- `metadata_defaults` → assets: ["optimization_guide"]
  - Requiere: `default_title`, `default_description`
  - En esta ejecución: `default_title: False, default_description: False, has_issues: False` → NO se detectó
- `low_citability` → assets: ["optimization_guide"]
  - Requiere: `citability_score` < 50
  - En esta ejecución: citability = 56.13/100 (> 50) → NO se detectó
- `low_content_length` → mapea a optimization_guide en asset_catalog pero NO se evaluó en esta ejecución

**Diagnóstico**: Ningún pain relacionado con SEO Local dispara `optimization_guide`.
El pain `metadata_defaults` es el más cercano, pero el hotel no tiene metadatos
por defecto (WordPress, títulos personalizados). El pain `poor_performance` no se
pudo evaluar por falta de API key de PageSpeed.

**Score SEO Local del hotel**: 25/100 (promedio regional: 59/100) — el diagnóstico
SÍ detecta que está bajo, pero no hay un pain type `low_seo_score` en
PainSolutionMapper.

### 3.2 open_graph

**❌ CORRECCIÓN del documento original**: La afirmación "No hay entrada `no_og_tags` en
`PAIN_SOLUTION_MAP`" es INCORRECTA. La entrada SÍ existe:

```python
# pain_solution_mapper.py:245-253
"no_og_tags": {
    "assets": ["og_tags_guide", "open_graph"],  # FASE-4: Added open_graph asset
    "confidence_required": 0.0,
    "priority": 2,
    "validation_fields": ["og_tags_detected"],
    "estimated_impact": "medium",
    "name": "Sin Open Graph Tags",
    "description": "Faltan meta tags de Open Graph para redes sociales"
},
```

**La causa raíz real es distinta**: El pain `no_og_tags` NO se activó porque
`detect_pains()` (pain_solution_mapper.py:523-533) solo lo hace cuando
`seo_elements.open_graph == False`. En esta ejecución, el audit report muestra
`seo_elements.open_graph: true` (el sitio ya tiene 8 OG tags: og:locale, og:type,
og:title, og:description, og:url, og:site_name, og:image). Al ser True, el pain
nunca entra al ledger, y `open_graph` nunca se planifica.

Esto es una inconsistencia de diseño: la propuesta SIEMPRE promete "Meta Tags
Sociales (Open Graph)" como servicio, pero el pipeline solo lo genera cuando NO
hay OG tags. Si el sitio YA tiene OG tags, el servicio se promete igual pero no
se genera. El texto "Sus fotos brillan cuando alguien comparte su link en redes"
implica optimización, no creación desde cero — el pipeline necesitaría un modo
"enhance_existing" para OG tags.

**Ubicación del generador**: `modules/asset_generation/conditional_generator.py:528`
```python
elif asset_type == "open_graph":
    from .open_graph_generator import OpenGraphGenerator
```

**Entradas en asset_catalog** (`asset_catalog.py:349`):
```python
"open_graph": AssetCatalogEntry(
    asset_type="open_graph",
    template="open_graph_template.html",
    output_name="{prefix}open_graph_meta{suffix}.html",
    status=AssetStatus.IMPLEMENTED,
    promised_by=["no_og_tags"],
    ...
)
```

---

## 4. Arquitectura del Problema (Tres Capas Desconectadas)

```
CAPA 1: Propuesta Comercial (v4_proposal_generator.py)
  → Usa PROPOSAL_SERVICE_TO_ASSET para listar servicios
  → Promete 8 servicios (incluyendo SEO Local y Open Graph)
  → NO verifica si el pipeline GENERÓ el asset antes de prometerlo
  → _generate_dynamic_services_table() itera TODOS los 8 servicios siempre

CAPA 2: Publication Gates (publication_gates.py)
  → Gate 9: proposal_asset_alignment
  → Cruza servicios prometidos vs assets realmente generados
  → FALLA cuando un servicio prometido no tiene asset (BLOCKED, 75%)

CAPA 3: Pain→Asset Pipeline (PainSolutionMapper → conditional_generator)
  → Detecta pains → planifica assets → genera
  → NO tiene mapping para "SEO Local" como pain específico
  → TIENE mapping para open_graph (pain `no_og_tags`), pero el pain no se activa
    porque el sitio YA tiene OG tags
  → Resultado: nunca planifica ni genera estos 2 assets
```

La desconexión es entre CAPA 1 (promete) y CAPA 3 (genera). El Gate 9 (CAPA 2)
es el sintomizador, no la causa.

**⚠️ NUEVO — CAPA 0 adicional**: Hay una cuarta capa (CAPA 0) que debería
bloquear la entrega pero está bypassed:
- `main.py:2814`: `GATE_BLOCKING_ENABLED` = False por default → nunca bloquea
- `delivery_quality_report.py:238`: hardcodea `proposal_asset_gate.passed=True`
  ignorando el resultado real del Gate 9
- `delivery_quality_report.py:203-205`: los únicos gates considerados blocking
  son `coherence`, `coverage`, `evidence` — proposal_asset_alignment NUNCA bloquea

---

## 5. Evidencia de la Ejecución

### 5.1 Datos del Hotel (observaciones.json — Tier A)
```json
{
  "hotel_name": "Zi One Luxury",
  "rooms": 34,
  "monthly_reservations": 800,
  "adr_cop": 290000,
  "direct_channel_percentage": 40.0,
  "occupancy_rate": 0.7843,
  "region": "eje_cafetero",
  "category": "standard_26_60",
  "is_transit_hotel": false,
  "confidence": 0.95
}
```

### 5.2 Onboarding YAML creado
Ruta: `output/clientes/zi-one-luxury_onboarding.yaml`
```yaml
hotel:
  nombre: Zi One Luxury
  ubicacion: Pereira, Eje Cafetero
datos_operativos:
  habitaciones: 34
  reservas_mes: 800
  valor_reserva_cop: 290000
  canal_directo_pct: 40.0
metadatos:
  fuente: observations_tier_a
  fecha_captura: '2026-07-23T10:00:00+00:00'
  campos_confirmados: [habitaciones, reservas_mes, valor_reserva_cop, canal_directo_pct]
```

### 5.3 Scores del Diagnóstico
| Score | Valor | Regional | Estado |
|-------|-------|----------|--------|
| SEO Local | 25/100 | 59/100 | ❌ Bajo |
| GEO | 78/100 | 77/100 | ⚠️ Promedio |
| AEO | 15/100 | 44/100 | ❌ Bajo |
| IAO | 50/100 | 20/100 | ✅ Superior |

**Nota**: El desglose del diagnóstico muestra que SEO Local = `ssl(15%) + schema_reviews(10%) = 25/100`.
No incluye contenido optimizado, meta descriptions, ni estructura H1/H2.

### 5.4 Financial Scenarios (con trazabilidad de fuentes)
- Conservador: $19,627,200 COP/mes
- Realista: $7,192,000 COP/mes
- Optimista: -$6,820,800 COP/mes (equilibrio)
- **Comisión OTA real**: $20,880,000 COP/mes (480 noches OTA × $290,000 ADR × 15%)
- **Evidence tier**: B (datos fuente)
- **Precision tier**: C (cálculos derivados — supuestos de shift 10% y boost IA 5% no validados con GA4)
- **⚠️ La propuesta muestra $7,192,000 con etiqueta "Fuga mensual por comisiones OTA"**, pero ese valor ya descuenta $2,088,000 de shift_savings (10% hardcodeado) y $11,600,000 de ia_revenue_cop (5% boost IA hardcodeado). El número verificable ($20,880,000) nunca aparece.

### 5.5 Publication Gates (completo)
| Gate | Status | Valor |
|------|--------|-------|
| hard_contradictions | ✅ PASSED | 0 |
| evidence_coverage | ✅ PASSED | 95.0% |
| financial_validity | ✅ PASSED | true |
| coherence | ✅ PASSED | 0.88 |
| critical_recall | ✅ PASSED | 100% |
| ethics | ✅ PASSED | — |
| content_quality | ✅ PASSED | 1.0 |
| asset_confidence | ✅ PASSED | 7/7 above threshold |
| **proposal_asset_alignment** | **❌ BLOCKED** | **0.75 (efectivo), 0.667 (alignment_percentage)** |
| tier_c_onboarding_required | ✅ PASSED | Tier B |
| coverage | ✅ PASSED | 1.0 |

**⚠️ El gate report tiene una inconsistencia interna**: `value: 0.75` (efectivo
contando present_in_production) pero `alignment_percentage: 0.6667` (sin contar
present_in_production). Ambas métricas aparecen en el mismo JSON.

### 5.6 Coherence Report (detallado)
```
problems_have_solutions:  ✅ 1.00
assets_are_justified:     ❌ 0.75 (Solo 75% de assets tienen justificación)
financial_data_validated: ✅ 0.95
whatsapp_verified:        ❌ 0.30 (confidence insuficiente)
price_matches_pain:       ⚠️ 0.80 (límite superior 7.0x)
promised_assets_exist:    ✅ 1.00 (PRE-GENERACIÓN — 8 servicios verificados via PROPOSAL_SERVICE_TO_ASSET)
```

**⚠️ El coherence pre-generación dice `promised_assets_exist: 1.00`** ("Todos los assets
prometidos están implementados (8 servicios verificados via PROPOSAL_SERVICE_TO_ASSET)").
Pero el coherence post-generación (`coherence_validation_post_gen.json`) lo corrige:
`promised_assets_exist: ❌ 0.91` ("Assets no implementados: whatsapp_button").

### 5.7 Archivos Generados
```
output/v4_complete/
├── 01_DIAGNOSTICO_Y_OPORTUNIDAD_20260723_131456.md
├── 02_PROPUESTA_COMERCIAL_20260723_131506.md
├── v4_complete_report.json
├── deliveries/
│   ├── zi_one_luxury_20260723.zip  (40 archivos reales, MANIFEST declara 38)
│   └── README_DELIVERY.md
├── health_dashboard/
│   ├── health_dashboard.html
│   └── health_dashboard_summary.json
├── v4_audit/
│   └── proposal_asset_matrix.json
└── zi_one_luxury/
    ├── v4_audit/
    │   ├── audit_report_20260723_131452.json
    │   ├── gate_report_20260723_131507.json
    │   ├── asset_generation_report.json
    │   ├── coherence_validation.json
    │   ├── coherence_validation_post_gen.json
    │   ├── delivery_quality_report.json
    │   ├── geo_flow_result.json
    │   ├── pain_ledger.json
    │   ├── financial_scenarios_20260723_131452.json
    │   └── human_checklist.md
    ├── geo_enriched/ (7 archivos: seo_fix_kit, robots_fix, llms.txt, etc.)
    ├── whatsapp_conflict_guide/
    ├── hotel_schema/
    ├── faq_page/
    ├── analytics_setup_guide/
    ├── indirect_traffic_optimization/
    ├── llms_txt/
    └── monthly_report/
```

---

## 6. Archivos Clave para el Plan de Refactorización

| Archivo | Relevancia |
|---------|-----------|
| `modules/asset_generation/proposal_asset_alignment.py` | Gate 9 + PROPOSAL_SERVICE_TO_ASSET (source of truth) |
| `modules/commercial_documents/pain_solution_mapper.py` | PAIN_SOLUTION_MAP (donde faltan los mappings — CORRECCIÓN: no_og_tags SÍ existe) |
| `modules/asset_generation/asset_catalog.py` | Catálogo de assets (optimization_guide:183, open_graph:349) |
| `modules/asset_generation/conditional_generator.py` | Generadores (optimization_guide:450, open_graph:528) + PAIN_TO_ASSET (clave duplicada L250-251) |
| `modules/quality_gates/publication_gates.py` | Gate 9 implementation (línea 803+) + _proposal_asset_alignment_gate |
| `modules/quality_gates/delivery_quality_report.py` | ⚠️ BUG: proposal_asset_gate hardcodeado L238 |
| `modules/commercial_documents/v4_proposal_generator.py` | Genera la propuesta (promete servicios) + _generate_dynamic_services_table L1110 |
| `modules/commercial_documents/service_catalog.py` | SERVICE_CATALOG (7+1 entradas, divergente de PROPOSAL_SERVICE_TO_ASSET) |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Template con "Tier C" hardcodeado L102 |
| `modules/quality_gates/delivery_quality_report.py` | ⚠️ Evalúa G6/G7/G8 independientemente de los publication gates reales |
| `modules/delivery/delivery_packager.py` | Crea ZIP sin verificar Gate 9 |
| `main.py:2814` | GATE_BLOCKING_ENABLED (False por default) |

---

## 7. Opciones de Solución (para evaluar en nueva sesión)

### Opción A: Agregar pain mappings al PainSolutionMapper
- Agregar pain `low_seo_score` → assets: ["optimization_guide"]
  - Trigger: `seo_local_score < 40` (o configurable)
  - En esta ejecución: SEO Local = 25/100 → SÍ se activaría
- Modificar lógica de `no_og_tags`: activar también cuando OG tags existen pero
  son mejorables (modo "enhance_existing"), no solo cuando están ausentes

### Opción B: Agregar `promised_by: "always"` al asset_catalog
- Para assets que la propuesta SIEMPRE promete, generarlos sin depender de un pain
- Patrón ya usado para `monthly_report` (promised_by=["always"])

### Opción C: Hacer la propuesta condicional
- Que v4_proposal_generator SOLO prometa servicios para los cuales SÍ se generó
  un asset (excluyendo los "⏳ Pendiente" de la tabla)
- Más honesto comercialmente, pero reduce el valor percibido del paquete

### Opción D: Gate 9 como WARNING en vez de BLOCKING
- Cambiar el gate de BLOCKING a WARNING para que no impida publication
- Riesgo: el cliente recibiría una propuesta con servicios que no tiene

### Opción E (NUEVA): Reparar delivery_quality_report para consumir Gate 9 real
- `delivery_quality_report.py:238`: leer resultado real de proposal_asset_alignment
  desde gate_report.json en vez de hardcodear `passed=True`
- Añadir `proposal_asset_alignment` a la lista de blocking_gates

### Opción F (NUEVA): Activar GATE_BLOCKING_ENABLED por default
- Cambiar `main.py:2814` para que el default sea True o eliminar la variable
  y usar delivery_quality_report como único blocker

### Híbrida recomendada (opciones A + C + E + F):
1. Agregar pain `low_seo_score` + mejorar detección de `no_og_tags` (Opción A)
2. Hacer la propuesta condicional como safety net (Opción C)
3. Reparar delivery_quality_report para que consuma el resultado real del Gate 9 (Opción E)
4. Activar GATE_BLOCKING_ENABLED por default (Opción F)

---

## 8. Notas Adicionales

### Sobre la propuesta prometiendo Open Graph cuando ya existe
El diagnóstico detecta `seo_elements.open_graph: True` (8 OG tags), lo que significa
que el sitio YA tiene OG tags. Sin embargo, la propuesta promete "Meta Tags Sociales
(Open Graph)" como servicio pendiente. La propuesta muestra el servicio como
"⏳ Pendiente" con la brecha "#6: Sin OG Tags ($321,786/mes)".

Posible explicación: la propuesta promete "optimización" de OG tags, no
"implementación desde cero". El generador `open_graph` podría generar tags
más completos. Pero el pipeline actual solo activa `no_og_tags` cuando NO hay
OG tags — no tiene modo "enhance_existing".

### Sobre el escenario "optimista" negativo
El escenario optimista (-$6,820,800 COP/mes) representa equilibrio/ganancia
cuando el % de canal directo compensa las comisiones OTA. Con 78.43% de
ocupación (muy por encima del benchmark de ~51%), el hotel ya captura bien
la demanda. La brecha real está en visibilidad digital (SEO, IA, schema),
no en demanda no activada.

### Sobre el score SEO Local = 25/100
El componente `seo_elements` del diagnóstico detecta:
- SSL: ✅ (15 pts)
- Schema reviews: ✅ (10 pts)
- Total visible: 25/100
- Faltan: contenido optimizado, meta descriptions, estructura H1/H2, etc.

---

## 9. HALLAZGOS AMPLIADOS — Auditoría Código Vivo (2026-07-23)

### 9.1 🔴 CRÍTICO — delivery_quality_report ignora el resultado real de Gate 9

**Evidencia**:
- `delivery_quality_report.json`: `status: "PASS"`, `blocking: false`, `proposal_asset_gate: {"passed": true, "gate": "G9"}`
- `gate_report.json` (Gate 9 real): `passed: false`, `status: "BLOCKED"`, `value: 0.75`

**Causa raíz**: `delivery_quality_report.py:238`:
```python
proposal_asset_gate=gate_results.get("proposal_asset", {"passed": True, "gate": "G9"}),
```
El código busca una key `"proposal_asset"` que NUNCA se inserta en `gate_results`.
El gate real se llama `"proposal_asset_alignment"`. Al no encontrarlo, usa el
default `{"passed": True, ...}`.

**Además**: `_evaluate_asset_specificity` (L324-382) evalúa G8 con sus propios
thresholds independientes, sin consumir el resultado del gate `asset_confidence`
de publication_gates. El quality report tiene lógica duplicada e independiente.

**Consecuencia**: El ZIP se generó a pesar de que el sistema SABÍA que 2 servicios
prometidos no tenían assets.

### 9.2 🔴 CRÍTICO — GATE_BLOCKING_ENABLED desactivado por default

`main.py:2814`:
```python
_gate_blocking_enabled = os.getenv("GATE_BLOCKING_ENABLED", "").lower() in ("1", "true", "yes")
```

Default = `False`. Los documentos cliente se generan siempre, sin importar el
resultado de los gates. La única barrera real es `delivery_quality_report.status == "FAIL"`
→ no genera ZIP — pero ese report está roto (ver 9.1).

### 9.3 🔴 CRÍTICO — 4 de 8 servicios prometidos NO están en el ZIP de delivery

Matriz factual ZIP vs Propuesta:

| Servicio | Asset | ¿En ZIP? |
|----------|-------|----------|
| SEO Local | optimization_guide | ❌ |
| Meta Tags Sociales | open_graph | ❌ |
| Botón de WhatsApp | whatsapp_button | ❌ (skipped) |
| Schema Organization | org_schema | ❌ (present_in_production) |
| Schema Hotel | hotel_schema | ✅ |
| Página de FAQ | faq_page | ✅ |
| Optimización IA | llms_txt | ✅ |
| Informe Mensual | monthly_report | ✅ |

### 9.4 🔴 CRÍTICO — Contradicción financial_evidence_tier

- Diagnóstico (frontmatter YAML): `financial_evidence_tier: "B"`
- Propuesta (template warn): `> ⚠️ Advertencia: Nivel de evidencia: Tier C`
- financial_scenarios.json: `evidence_tier: "B"`, `precision_tier: "C"`
- Gate tier_c_onboarding_required: PASSA (porque recibe tier "B")

El texto "Tier C" en la propuesta viene del template `propuesta_v6_template.md:102`
que es texto fijo, NO una variable. La variable `financial_evidence_tier` se inyecta
como "B" (v4_proposal_generator.py:919), pero el warning del template es estático.

### 9.5 🟠 ALTO — Clave duplicada en PAIN_TO_ASSET (sobrescritura silenciosa)

`conditional_generator.py:250-251`:
```python
"whatsapp_conflict": "whatsapp_button",                        # L250 — SOBREESCRITO
"whatsapp_conflict": ["whatsapp_button", "whatsapp_conflict_guide"],  # L251 — sobrevive
```
Solo la segunda entrada sobrevive. No rompe la generación actual (la rama
`generate_for_faltantes` maneja listas), pero cualquier consumidor que espere
un string para `whatsapp_conflict` recibirá una lista.

### 9.6 🟠 ALTO — Tres fuentes de verdad divergentes para servicios

1. `proposal_asset_alignment.py:PROPOSAL_SERVICE_TO_ASSET` — 8 entradas (source of truth para Gate 9)
2. `service_catalog.py:SERVICE_CATALOG` — 7+1 entradas (más FASE-D dinámica)
3. `service_catalog.py:SERVICE_TO_ASSET_LOOKUP` — derivado de SERVICE_CATALOG

`_generate_dynamic_services_table()` itera sobre PROPOSAL_SERVICE_TO_ASSET (8 servicios).
`_generate_asset_quality_table()` itera sobre SERVICE_CATALOG filtrado por detected_pain_ids.
Resultado: "Informe Mensual" aparece en asset_quality_table pero NO en la tabla
principal de servicios.

### 9.7 🟡 MEDIO — proposal_asset_matrix.json muestra todo como NO_BREACH

Las 8 entradas de `proposal_asset_matrix.json` tienen `pain_ids: [], confidence: 0.0,
status: "NO_BREACH"`. La matriz no encontró correspondencia entre los pain_ids del
ledger y los asset_types de PROPOSAL_SERVICE_TO_ASSET.

Causa probable: `ProposalAssetMatrix.build()` recibe `pain_ledger` como lista de
PainLedgerEntry (objetos con `.pain_id`), pero `assessment_builder.py:154` los
serializa a dicts con `.to_dict()`. Si `pain_ledger` llega como dicts, el acceso
`e.pain_id` en L497 falla silenciosamente.

### 9.8 🟡 MEDIO — MANIFEST y README desincronizados del ZIP real

- ZIP real: 40 archivos
- MANIFEST.json: 38 archivos declarados
- README_DELIVERY.md: "38 files (104.0 KB)"

### 9.9 🟡 MEDIO — README_DELIVERY.md referencia archivos que no existen

El README menciona `boton_whatsapp.html` (línea 54-57) pero el ZIP no contiene
ese archivo (whatsapp_button fue skipped). El README es genérico, no refleja el
contenido real del paquete.

### 9.10 🟡 MEDIO — $7,192,000 etiquetado "Fuga mensual por comisiones OTA" es engañoso

La comisión OTA verificable es $20,880,000 (480 noches × $290K × 15%). El $7,192,000
es el resultado NETO después de restar $2,088,000 de shift_savings (10% hardcodeado,
fuente: "sin GA4") y $11,600,000 de ia_revenue_cop (5% boost IA hardcodeado, fuente:
"estimado: sin datos GA4"). El número verificable nunca aparece en la propuesta.

### 9.11 🟢 BAJO — Test roto por path hardcodeado

`tests/quality_gates/test_publication_gates.py:1191` — `test_asset_generation_report_exists`
falla porque apunta a `output/v4_complete/amaziliahotel/v4_audit/asset_generation_report.json`
que no existe. 85/86 tests pasan, 1 falla (pre-existente, no relacionado con esta ejecución).

---

## 10. CADENA DE BYPASS COMPLETA (3 capas rotas)

```
CAPA A: Publication Gates (11 gates — source of truth canónica)
   ↓ Gate 9 detecta BLOCKED (alignment 66.7%, efectivo 75%)
   ↓ PERO: GATE_BLOCKING_ENABLED=False → no bloquea documentos
   ↓ PERO: delivery_quality_report IGNORA el resultado real de Gate 9
   
CAPA B: Delivery Quality Report (evalúa G6/G7/G8 independientemente)
   ↓ delivery_quality_report.py:238 hardcodea proposal_asset_gate.passed=True
   ↓ No consume los resultados reales de los publication gates
   ↓ Siempre reporta PASS cuando coherence+coverage+evidence pasan
   
CAPA C: Delivery Packaging (main.py:2948-2990)
   ↓ Solo bloquea ZIP si delivery_quality_report.status == "FAIL"
   ↓ Como el quality report siempre dice PASS, NUNCA bloquea
   ↓ El ZIP se genera con servicios faltantes
```

---

## 11. VERIFICACIONES REPRODUCIBLES

### Tests ejecutados
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_proposal_asset_alignment.py -q    # 24 passed
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_proposal_asset_matrix.py -q    # incluidos
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_delivery_quality_report.py -q     # 27 passed
./venv/Scripts/python.exe -m pytest tests/delivery/test_delivery_packager.py -q                # incluidos
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_publication_gates.py -q           # 85 passed, 1 FAILED
```

### Verificación del bypass delivery_quality_report
```bash
# Gate 9 REAL — BLOCKED
jq '.gate_results[] | select(.gate_name=="proposal_asset_alignment") | {passed,status,value}' \
  output/v4_complete/zi_one_luxury/v4_audit/gate_report_20260723_131507.json

# Quality report — siempre PASS (BUG)
jq '{status,blocking,proposal_asset_gate}' \
  output/v4_complete/zi_one_luxury/v4_audit/delivery_quality_report.json
```

### Verificación ZIP vs Promesas
```bash
python3 -c "
import zipfile
with zipfile.ZipFile('output/v4_complete/deliveries/zi_one_luxury_20260723.zip') as z:
    names = [n.replace('\\\\','/') for n in z.namelist()]
    for asset in ['optimization_guide','open_graph','whatsapp_button','org_schema',
                  'hotel_schema','faq_page','llms_txt','monthly_report']:
        print(asset, any(asset in n.lower() for n in names))
"
```

---

## 12. PLAN DE ATAQUE RECOMENDADO (nueva sesión)

### Fase 1 — Reparar el bypass de seguridad (CRÍTICO)
1. **delivery_quality_report.py:238**: Leer resultado real de `proposal_asset_alignment`
   desde gate_report.json. Añadir a lista de blocking_gates.
2. **main.py:2814**: Activar GATE_BLOCKING_ENABLED por default.

### Fase 2 — Cerrar gaps Pain→Asset (ALTO)
1. **pain_solution_mapper.py**: Agregar `low_seo_score` → optimization_guide.
2. **pain_solution_mapper.py**: Modificar detección de `no_og_tags` para activar
   también en modo "enhance_existing" (OG tags presentes pero mejorables).
3. **conditional_generator.py:250-251**: Eliminar clave duplicada.

### Fase 3 — Hacer la propuesta condicional (MEDIO)
1. **_generate_dynamic_services_table()**: Excluir servicios sin asset generado
   y sin presencia en producción.

### Fase 4 — Unificar fuentes de verdad (MEDIO)
1. Derivar SERVICE_TO_ASSET_LOOKUP de PROPOSAL_SERVICE_TO_ASSET.
2. Sincronizar SERVICE_CATALOG con PROPOSAL_SERVICE_TO_ASSET.

### Fase 5 — Correcciones de presentación (BAJO)
1. Template "Tier C" → variable `${financial_evidence_tier}`.
2. README_DELIVERY dinámico basado en assets reales del ZIP.

---

*Documento original: 2026-07-23*
*Última actualización: 2026-07-23 (auditoría exhaustiva contra código vivo)*
*Ejecución: v4complete v4.62.0 para https://zione.co/*
*Hotel: Zi One Luxury, Pereira, Eje Cafetero*
*Datos: observations.json (Tier A, confidence 0.95)*
*Tests: 136 relevantes ejecutados, 1 pre-existing failure*
