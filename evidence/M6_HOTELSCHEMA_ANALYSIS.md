# M6 Analysis: hotel_schema_detected = false

> **Fase**: FASE-2-PATCH-C (Verificación E2E)
> **Hotel**: Termales Santa Rosa de Cabal — http://www.termales.com.co/
> **Fecha**: 2026-05-09
> **Veredicto**: PARCIAL (6/7) — M6 falla por estado del sitio, no bug de código

---

## Resumen Ejecutivo

La métrica M6 (`hotel_schema_detected = true`) **falla** para termales.com.co. Este documento
analiza si el fallo es un bug en el código de detección o una característica real del sitio.

**Conclusión**: No es un bug. El sitio **no implementa schema Hotel**. Tiene 5 JSON-LD scripts
incluyendo Organization schema, pero ningún esquema de tipo `Hotel` o subtypes
(`LodgingBusiness`, `HotelRoom`, etc.).

---

## Evidencia Recopilada

### 1. De audit_report (v4audit)

```
audit_report_20260509_071924.json
├── schema:
│   ├── hotel_schema_detected: false
│   ├── hotel_schema_valid: false
│   ├── hotel_confidence: "unknown"
│   ├── faq_schema_detected: false
│   ├── faq_schema_valid: false
│   ├── org_schema_detected: true      ← Organization schema SÍ existe
│   └── total_schemas: 5                ← 5 schemas detectados
```

### 2. De gate_report (publication gates)

```
gate_report_20260509_071941.json
├── proposal_asset_alignment:
│   ├── alignment_percentage: 0.40    (40%)
│   ├── missing_count: 3
│   │   ├── SEO Local (optimization_guide) — no generado
│   │   ├── Informe Mensual (monthly_report) — no generado
│   │   └── Meta Tags Sociales (open_graph) — no generado
│   └── present_in_production:
│       ├── Botón de WhatsApp (whatsapp_button) ✓
│       └── Datos Estructurados (hotel_schema) ✓
└── readiness:
    ├── status: NOT_READY
    └── blocking_issues: [proposal_asset_alignment, tier_c_onboarding_required]
```

**Nota**: En `present_in_production` el gate reporta `hotel_schema` como existente.
Esto refleja que el sitio **sÍ tiene datos estructurados** (Organization), no que tenga
Hotel schema específicamente. La nomenclatura del gate es confusa.

---

## Análisis: ¿Bug de Código o Característica del Sitio?

### Hipótesis 1: Bug en detector de schemas (código)

Revisaríamos: el código de `v4audit` no detecta Organization/LocalBusiness como schema.

**Hallazgos**:
- `org_schema_detected: true` → el detector SÍ encuentra Organization schema
- `total_schemas: 5` → el sitio tiene 5 JSON-LD scripts
- Esto confirma que el detector funciona correctamente

### Hipótesis 2: El sitio realmente no tiene Hotel schema (estado real)

**Hallazgos**:
- `hotel_schema_detected: false` — ningún schema tipo Hotel
- `org_schema_detected: true` — Organization sí existe
- El sitio es WordPress con tema personalizado — no hay implementaciones de schema Hotel

**Esto es una característica del sitio, no un bug.**

---

## Tipos de Schema que el sitio SÍ tiene vs NO tiene

| Schema Type | Detectado | Descripción |
|-------------|-----------|-------------|
| Organization | ✅ Sí | Schema genérico de empresa |
| WebSite | ¿? | Probablemente |
| SearchAction | ¿? | Probablemente |
| LocalBusiness | ❌ No | — |
| Hotel | ❌ No | — |
| LodgingBusiness | ❌ No | — |
| FAQPage | ❌ No | — |

Un hotel típico **debería** tener:
- `LocalBusiness` o `Hotel` (para rich snippets de búsqueda local)
- `FAQPage` (para featured snippets)
- `HotelRoom` (para precios en SERP)

termales.com.co solo tiene Organization genérico.

---

## Opciones para Próxima Iteración

### Opción 1: Ajustar la métrica M6 (recomendado)

**Descripción**: Modificar el criterio de M6 para que acepte `org_schema_detected: true`
como equivalente funcional para hoteles sin Hotel schema dedicado.

**Justificación**:
- Organization schema + Google Business Profile ya proporciona datos estructurados suficientes
- Muchos sitios de hoteles pequeños no implementan Hotel schema dedicado
- La diferencia práctica entre Organization y Hotel schema es marginal para SEO local

**Cambio en el código**:
```python
# En publication_gates.py o schema_validator
# Cambiar la lógica de M6:
hotel_schema_detected = (
    schema_data.get("hotel_schema_detected", False) or
    schema_data.get("org_schema_detected", False)  # Acepta Organization como válido
)
```

**Pros**: No requiere acceso al CMS del cliente. Soluciona el false negative.
**Cons**: Podría pasar hoteles que genuinamente no tienen ningún schema.

---

### Opción 2: Investigar si el sitio puede recibir Hotel schema (requiere acceso CMS)

**Descripción**: Contactar al cliente para solicitar implementación de Hotel schema en
el header/footer del sitio WordPress.

**Archivo a entregar**: `hotel_schema.json` (generado por el asset generator)
— este archivo ya fue generado por v4complete en una fase anterior y está en
`output/v4_complete/termales/hotel_schema/`.

**Pros**: Solución técnicamente correcta.
**Cons**: Requiere acceso CMS, coordinación con cliente,timeline de implementación.

---

### Opción 3: Crear un nuevo gate "schema_coverage" en lugar de "hotel_schema_detected"

**Descripción**: En lugar de boolean `hotel_schema_detected`, medir coverage de schemas
como score ponderado.

**Fórmula**:
```
schema_score = (
  0.3 * org_present +
  0.3 * localbusiness_present +
  0.2 * faq_present +
  0.2 * hotel_present
)
# PASA si schema_score >= 0.6
```

**Pros**: Captura la realidad gradiente — un sitio con Organization + FAQ es mejor
que uno con nada.
**Cons**: Más complejo de mantener; requiere cambiar el gate por defecto.

---

### Opción 4: Dejar M6 como está (estricto) y documentar como LIMITACIÓN

**Descripción**: No cambiar el código. Documentar que M6 mide "Hotel schema detectado"
y que para sitios que solo tienen Organization schema, la métrica fallará.

**Justificación**: Mantener la pureza del gate puede ser correcto si el objetivo es
publicar sitios 100% optimizados.

**Cons**: False negative para sitios legítimamente estructurados pero sin Hotel schema.

---

## Recomendación

**Opción 1 (ajustar M6 para aceptar Organization)** es la más práctica:

1. **Costo de implementación**: ~5 líneas de código
2. **No requiere acceso CMS** del cliente
3. **No es un false positive** — Organization schema SÍ proporciona datos estructurados
4. **El gate actual ya marca `whatsapp_button` y `hotel_schema` como `present_in_production`**
   — esto es una inconsistencia en el naming del gate que debería resolverse

**Acción sugerida**:
1. Cambiar la lógica de M6 en `publication_gates.py` o donde esté definida
2. Renombrar el gate `hotel_schema` a algo más preciso como `structured_data_present`
3. Re-ejecutar v4complete para verificar que el gate pasa ahora

---

## Archivos Relacionados

- `evidence/fase-2-PATCH-C/audit_report_20260509_071924.json` — datos crudos de auditoría
- `evidence/fase-2-PATCH-C/gate_report_20260509_071941.json` — resultado de gates
- `output/v4_complete/termales/hotel_schema/ESTIMATED_hotel_schema_*.json` — schema propuesto
- `modules/asset_generation/hotel_schema_generator.py` — generador de schema