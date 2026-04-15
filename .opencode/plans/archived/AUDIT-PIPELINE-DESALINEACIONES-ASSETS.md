# Contexto: Auditoría Pipeline — Desalineaciones Assets vs Diagnóstico/Propuesta

**Fecha original:** 2026-04-12
**Fecha actualización:** 2026-04-12 22:00
**Origen:** Auditoría exhaustiva post-ejecución v4complete para amaziliahotel.com + validación cruzada agente + validación de planificación
**Sesión anterior:** Ejecución 09-documentacion-post-proyecto.md + auditoría cross-document + validación planificación
**Estado:** Planificación completada (8 fases) — Listo para implementación por fases

---

## 1. QUÉ SE AUDITÓ

Se ejecutó `v4complete --url https://amaziliahotel.com/` y se cruzaron exhaustivamente:
- Diagnóstico: `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260412_203924.md`
- Propuesta: `output/v4_complete/02_PROPUESTA_COMERCIAL_20260412_203924.md`
- Assets: 10 generados en `output/v4_complete/amaziliahotel/`
- Código: `v4_diagnostic_generator.py`, `v4_proposal_generator.py`, template V6, template embebido
- Datos fuente: `financial_scenarios.json`, `audit_report.json`, `v4_complete_report.json`

---

## 2. QUÉ ESTÁ BIEN (NO TOCAR)

### Cadena financiera íntegra ✅
- Diagnóstico, propuesta y financial_scenarios.json muestran mismos valores
- Pérdida mensual: $2,610,000 COP (consistente en los 3 documentos)
- Escenarios conservador/realista/optimista: $5,076,000 / $2,610,000 / -$189,000
- Precio: $130,500/mes (tier=boutique, rooms=10, pain_ratio=5%)
- ROI: 20.0x (cálculo correcto: 2,610,000 / 130,500)
- Suma brechas ($2,610,261) ≈ pérdida esperada ($2,610,000) — diferencia $261 por redondeo

### 4 Pilares alineados ✅
- Diagnóstico muestra exactamente 4 filas: SEO Local, Google Maps, AEO, IAO
- Fila "Visibilidad Digital (Global)" eliminada correctamente (FASE-1 efectiva)
- Benchmarks regionales consistentes con defaults del código (línea 1391 de v4_diagnostic_generator.py)
- Template V6 (`diagnostico_v6_template.md` líneas 52-55) usa las mismas 4 variables

### Brechas soportadas por audit ✅
- Las 6 brechas del diagnóstico mapean a datos reales del audit_report.json
- Cada brecha tiene costo COP calculado proporcionalmente

### Publication Gates ✅
- 7/7 gates pasaron (hard_contradictions, evidence_coverage, financial_validity, coherence 0.89, critical_recall 100%, ethics, content_quality)
- READY_FOR_PUBLICATION

### Content Scrubber ✅
- 10 fixes diagnóstico, 9 fixes propuesta (moneda, idioma, genericidad)
- 3 warnings menores (self-replacement) — no bloqueantes

### Coherence Score ✅
- Score: 0.89 (umbral: 0.8) — PASA gate

---

## 3. DESCONEXIONES ENCONTRADAS

### D2: hotel_schema vacío — IMPACTO ALTO ⚠️
**Problema:** El asset entregado al cliente (`hotel_schema/ESTIMATED_hotel_schema_*.json`) contiene datos genéricos:
```json
{
  "@type": "LodgingBusiness",
  "name": "Hotel",
  "description": "",
  "url": "",
  "telephone": "",
  "address": {"streetAddress": "", "addressLocality": "...", "addressCountry": "CO"}
}
```
**Pero** existe `geo_enriched/hotel_schema_rich.json` con datos REALES:
```json
{
  "@type": "Hotel",
  "name": "Amaziliahotel",
  "url": "https://amaziliahotel.com/",
  "geo": {"latitude": "40.7128", "longitude": "-74.0060"},
  "amenityFeature": ["WiFi gratuito", "Recepción 24 horas", ...],
  "starRating": "4",
  "numberOfRooms": "10",
  "checkinTime": "15:00",
  "checkoutTime": "12:00"
}
```
**Raíz:** El generador de hotel_schema crea un schema desde audit data limitada (sin onboarding). El geo_enriched se genera por un pipeline diferente (GEO enrichment) pero NO se empaqueta como asset principal.
**Archivo relevante:** `modules/asset_generation/` — generador de hotel_schema asset

### D3: llms.txt con placeholders vacíos — IMPACTO ALTO ⚠️
**Problema:** El archivo `llms_txt/ESTIMATED_llms_*.txt` generado contiene:
```
# Hotel  (debería ser "Amaziliahotel")

> Hotel es un hotel boutique en , Eje Cafetero, Colombia.
  (nombre vacío antes de la coma)

- [Homepage](): Main hotel website  (URL vacía)
- Phone: N/A, Email: N/A, Address: N/A
```
**Pero** existe `geo_enriched/llms.txt` con datos reales:
```
# Amaziliahotel
**URL:** https://amaziliahotel.com/
**Servicios:** Hospedaje, restaurante, WiFi, recepción 24 horas.
```
**Raíz:** El generador de llms.txt no tiene acceso a datos de onboarding (nombre real, URLs de páginas, contacto). Usa defaults/genéricos cuando no hay datos.
**Archivo relevante:** Módulo que genera llms.txt asset

### D4: Propuesta promete 7 servicios pero 3 no generan asset — IMPACTO ALTO ⚠️ **CORREGIDO**
**Problema (evidencia real de amaziliahotel.com):**

| Servicio prometido | Asset esperado | Generado? | Directorio en disco? |
|---|---|---|---|
| Google Maps Optimizado (GEO) | geo_playbook | SI ✅ | SI |
| Visibilidad en ChatGPT (IAO) | indirect_traffic_optimization | SI ✅ | SI |
| Búsqueda por Voz (AEO) | voice_assistant_guide | NO ❌ | NO |
| SEO Local (SEO) | optimization_guide | SI ✅ | SI |
| Botón de WhatsApp | whatsapp_button | NO ❌ | NO |
| Datos Estructurados | hotel_schema | SI ⚠️ | SI (placeholder) |
| Informe Mensual | (no existe en catálogo) | NO ❌ | NO |

**3 de 7 servicios (43%) prometidos con ✅ NO generan asset entregable.**

**Raíz arquitectural (descubierta durante validación de planificación):**
La propuesta template (`propuesta_v6_template.md`) hardcodea los 7 servicios con `✅`. Pero la generación de assets es **pain-driven** (`v4_asset_orchestrator.py` línea 220-224): solo genera assets si `pain detection` detecta un problema específico.

- `voice_assistant_guide`: Existe en catálogo como IMPLEMENTED pero ningún pain lo dispara (`promised_by=[]`)
- `whatsapp_button`: Está en `_fast_assets` pero no aparece en los 10 assets generados — preflight o conditional logic lo filtra
- `monthly_report`: No existe en catálogo ni en ningún módulo

**Si no entregamos lo que prometemos, no captamos clientes y no crecemos.**

**Archivos relevantes:**
- `modules/asset_generation/asset_catalog.py` — catálogo central
- `modules/asset_generation/conditional_generator.py` — PAIN_TO_ASSET mapping (línea 201)
- `modules/asset_generation/v4_asset_orchestrator.py` — flujo pain-driven (línea 220)
- `modules/commercial_documents/templates/propuesta_v6_template.md` — servicios hardcodeados

### D5: Template embebido vs V6 desalineados — IMPACTO BAJO (deuda técnica)
**Problema:** `v4_diagnostic_generator.py` tiene DOS templates:
1. **Embebido** (líneas ~390-460): Tiene 4 filas con nombres diferentes (GEO, Competitive, SEO, AEO) — NO tiene IAO
2. **V6** (`diagnostico_v6_template.md`): Tiene 4 filas (SEO Local, Google Maps, AEO, IAO) — SÍ tiene IAO

El V6 se carga primero (línea 263). El embebido es fallback. Si el V6 se elimina o el path cambia, el output perdería el pilar IAO.

### D6: `package_name` dead code — IMPACTO BAJO
**Problema:** Código línea 532: `'package_name': "Kit Hospitalidad 4.0"`. Template V6 hardcodea "Kit Hospitalidad Digital" en línea 39 y NO usa `${package_name}`. Variable es dead code en contexto V6.

### D7: SEO score 10 con datos nulos — IMPACTO BAJO (comportamiento intencional, no bug)
**Problema documentado:** `_calculate_web_score()` muestra 10/100 cuando se esperaría 0.
**Re-evaluación del agente:** El comportamiento NO es bug. Mirando el código (línea 1507-1527):
- `whatsapp_status = "unknown"` → NO es `"conflict"` → suma 10 puntos
- Performance: null → 0 puntos
- Schema: no detectado → 0 puntos
- FAQ: no detectado → 0 puntos
- Total: 10 puntos

**Veredicto:** La lógica es intencional. `unknown` no es `conflict`, por tanto suma. Esto NO es un bug pero la documentación del código no explica POR QUÉ unknown suma 10.
**Clasificación correcta:** IMPACTO BAJO — deuda de documentación, no de código.

### D1: Template propuesta tiene typo "debeproveer" — IMPACTO BAJO
**Problema:** Línea 61 de propuesta: "lo que debeproveer" (falta espacio: "debe prover"). El content scrubber no lo detecta porque no es un error de idioma sino de espaciado.
**Confirmado:** Template `propuesta_v6_template.md` línea 61 contiene `debeproveer`.

### D8: TODOS los assets con confidence 0.50 pero marcados READY_FOR_PUBLICATION — IMPACTO ALTO ⚠️ **NUEVO**
**Problema:** Los 10 assets generados tienen:
```json
"preflight_status": "WARNING",
"confidence_score": 0.5
```
Sin embargo, `phase_4_publication_gates.status = "READY_FOR_PUBLICATION"` con 7/7 gates pasando.
**El cliente recibe assets de baja calidad sin saberlo.**
**Raíz:** El gate `content_quality` pasa con 0.95 aunque haya WARNING en preflight. No hay gate que evalúe `confidence_score` de assets.
**Archivos relevantes:**
- `modules/quality_gates/publication_gates.py`
- `modules/asset_generation/asset_catalog.py` (is_asset_implemented)

---

## 4. RECOMENDACIONES (PRIORIZADAS) — REVISADAS

### PRIORIDAD ALTA (afectan calidad del deliverable al cliente)

**R1: geo_enriched → delivery package (CRÍTICO)**
- `geo_enriched/` contiene: `faq_schema.json`, `hotel_schema_rich.json`, `llms.txt`, `seo_fix_kit.md`, `geo_checklist_min.md`, `geo_dashboard.md`
- Estos assets tienen datos REALES que NO llegan al cliente
- Incluir `geo_enriched/` en zip de delivery o fusionar datos con assets principales
- **Razón: D2 y D3 se resuelven aquí — geo_enriched tiene los datos que faltan**

**R2: Assets con confidence < 0.7 NO deben marcarse READY_FOR_PUBLICATION**
- Crear gate adicional: `asset_confidence_gate` que falla si algún asset `confidence_score < 0.7`
- O marcar `READY_FOR_PUBLICATION_WITH_WARNINGS` si se quiere entregar con alerta
- **Resuelve D8**

**R3: No generar llms.txt si datos insuficientes**
- Si nombre="Hotel", URL="", contacto=N/A → marcar como "PENDIENTE_ONBOARDING"
- Agregar disclaimer visible o no incluirlo en delivery
- Alternativa: usar datos de `geo_enriched/llms.txt` directamente (ya tiene datos reales)

**R4: package_name vs template inconsistencia**
- Código línea 532: `"Kit Hospitalidad 4.0"`
- Template línea 39: `"Kit Hospitalidad Digital"`
- Elegir uno y estandarizar

### PRIORIDAD MEDIA (deuda técnica / robustez)

**R5: Eliminar o sincronizar template embebido**
- Mantener dos templates (embebido + V6) es fuente de bugs
- Opción A: Eliminar template embebido, exigir que V6 exista
- Opción B: Sincronizar embebido con V6 (agregar IAO, quitar competitive)
- Archivo: `v4_diagnostic_generator.py` líneas ~390-460

**R6: Content scrubber — evitar self-replacement warnings**
- "reserva" → "reserva" y "proxima" → "proxima" generan warnings innecesarios
- Agregar check: si old == new, skip

**R7: Content scrubber — detectar errores de espaciado**
- "debeproveer" no es error de idioma → content scrubber no lo detecta
- Agregar regex para palabras pegadas (ej: `debeproveer` → `debe prover`)

### PRIORIDAD BAJA (mejora continua)

**R8: Documentar racional de `_calculate_web_score`**
- El score 10 con `whatsapp_status=unknown` es intencional pero confuso
- Agregar docstring que explique por qué unknown suma 10 puntos

**R9: Disclaimer de confianza en propuesta — IMPACTO ALTO ⚠️ **REEVALUADO****
- La propuesta no menciona que los 10 assets tienen WARNING + confidence 0.50
- El cliente recibe assets marcados como "listos para usar" pero con calidad incierta
- Si el cliente implementa un asset con confidence 0.5 y no funciona (ej: hotel_schema con name="Hotel"), pierde confianza en TODO el servicio
- No renueva, no refiere, no crecemos
- Agregar sección "Estado de los Entregables" con nivel de cada asset (Completo / Requiere datos / En desarrollo)
- Tabla generada dinámicamente desde confidence scores reales

---

## 5. HALLAZGO ADICIONAL — GEO_ENRICHED COMO FUENTE DE VERDAD

**Descubierto durante validación del agente:**
- `geo_enriched/` se genera en una fase separada del pipeline principal de assets
- Contiene TODOS los datos reales que faltan en los assets entregados:
  - Nombre real del hotel ("Amaziliahotel" vs "Hotel")
  - URL completa
  - Amenities reales (WiFi, Recepción 24h, etc.)
  - Coordenadas geográficas
  - starRating, numberOfRooms, horarios de check-in/checkout
  - Contenido de contacto real
- Pero NUNCA se usa para alimentar los assets del delivery package

**El problema no es que falten datos — los datos EXISTEN en geo_enriched. El problema es que el pipeline de delivery no los consume.**

---

## 6. ARCHIVOS RELEVANTES PARA PLANIFICACIÓN

### Código fuente (correcciones prioritarias)
| Archivo | Desconexiones | Prioridad |
|---------|--------------|-----------|
| `modules/asset_generation/asset_catalog.py` | R2, D8 | ALTA |
| `modules/asset_generation/` (generadores) | D2, D3, R1 | ALTA |
| `modules/quality_gates/publication_gates.py` | D8, R2 | ALTA |
| `modules/commercial_documents/v4_diagnostic_generator.py` | D5, D7, R5 | MEDIA |
| `modules/commercial_documents/v4_proposal_generator.py` | D6, R4 | MEDIA |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | D1, R7 | BAJA |

### Pipeline de delivery (geo_enriched → assets)
- `modules/orchestration_v4/` — flujo dos fases Hook → Validación
- Buscar donde se "empaquetan" assets para delivery (FASE 7 del v4complete)
- `geo_enriched/` se genera en fase GEO pero se ignora en fase de packaging

### Datos de referencia (no modificar, solo lectura)
- `output/v4_complete/audit_report.json` — datos audit raw
- `output/v4_complete/financial_scenarios.json` — datos financieros
- `output/v4_complete/v4_complete_report.json` — assets_generated con confidence_score
- `output/v4_complete/amaziliahotel/geo_enriched/` — assets que SÍ tienen datos pero no se entregan
- `output/v4_complete/amaziliahotel/hotel_schema/ESTIMATED_hotel_schema_20260412_203926.json` — PLACEHOLDER
- `output/v4_complete/amaziliahotel/llms_txt/ESTIMATED_llms_20260412_203926.txt` — PLACEHOLDER

### Skills relacionadas
- `iah-cli-cross-document-audit` — CV4: Assets Promised vs Assets Generated (ya documenta el problema)
- `iah-cli-output-forensics` — para tracear problemas individuales
- `iah-cli-v4complete-flow-validation` — validar flujo completo post-corrección

---

## 7. CONSTRAINTS PARA LA SIGUIENTE SESIÓN

1. **No romper la cadena financiera** — cualquier cambio a assets o templates NO debe alterar los cálculos financieros que ya están validados
2. **No tocar el template V6 de diagnóstico** — los 4 pilares están correctos, solo ajustar si es estrictamente necesario
3. **Mantener backward compat** — si se elimina template embebido, asegurar que V6 siempre exista
4. **Testing** — verificar que los 385+ tests sigan pasando después de cambios
5. **Trazabilidad** — cualquier fase nueva requiere log_phase_completion.py + actualización de REGISTRY.md
6. **Costo API** — sensible a costos; no ejecutar v4complete innecesariamente para testing
7. **Una fase por sesión** — no implementar todas las correcciones de una vez; priorizar

---

## 8. AGENDA — PLANIFICACIÓN COMPLETADA (8 FASES)

**Estado:** Planificación completada en `.opencode/plans/` (v2 — ampliado)

### Fases implementadas:

| # | Fase | Resuelve | Prioridad |
|---|------|----------|-----------|
| 1 | FASE-GEO-BRIDGE | geo_enriched → delivery (D2, D3, R1) | ALTA |
| 2 | FASE-CONF-GATE | Confidence gate en publication (D8, R2) | ALTA |
| 3 | FASE-LLMSTXT-FIX | Fix llms.txt con fallback (D3, R3) | ALTA |
| 4 | FASE-ASSETS-VALIDACION | 7/7 servicios con asset (D4 corregido) | ALTA |
| 5 | FASE-CONFIDENCE-DISCLOSURE | Transparencia calidad en propuesta (R9 reevaluado) | MEDIA |
| 6 | FASE-TEMPLATE-DEBT | Sincronizar templates + typo (D5, D1, D6, R4, R5) | MEDIA |
| 7 | FASE-CONTENT-SCRUBBER | Fix self-replacement + spacing (R6, R7) | MEDIA |
| 8 | FASE-RELEASE | v4.29.0 + validación 3D (presencia + efectividad + calidad) | ALTA |

### Cobertura:
- **D1-D3, D5-D6, D8:** Cubiertos ✅
- **D4:** Cubierto (corregido con evidencia real, impacto ALTO) ✅
- **D7:** Fuera de scope (deuda documentación, IMPACTO BAJO) ⚪
- **R1-R7:** Cubiertos ✅
- **R9:** Cubierto (reevaluado a IMPACTO ALTO) ✅
- **R8:** Fuera de scope (deuda documentación) ⚪

### Validación final (FASE-RELEASE):
Ejecutar `v4complete --url https://amaziliahotel.com/` y verificar 3 dimensiones:
1. **Presencia:** 13+ tipos de asset, 7/7 servicios con asset
2. **Efectividad:** hotel_schema con nombre real, llms.txt con URL, voice_guide con checklists
3. **Calidad:** confidence >= 0.7, tabla disclosure en propuesta, 9 publication gates

---

*Documento validado y enriquecido por agente — 2026-04-12*
