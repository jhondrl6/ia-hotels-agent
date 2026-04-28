# Contexto: Post-VALIDATE-v2 — Hallazgos Verificados y Corregidos

> Generado: 2026-04-27 | Corregido: 2026-04-27 | Version base: v4.36.0
> Sesion origen: FASE-TRAZABILIDAD-VALIDATE-v2
> Revision forense contra codigo Y outputs reales (2da pasada)

## Propósito

Este contexto alimenta el diseño de un **nuevo plan de correccion** en una sesion futura. Contiene los hallazgos VERIFICADOS contra el codigo real y los archivos JSON de output, con correcciones a errores factuales del documento original.

**CORRECCIONES APLICADAS (2da pasada 2026-04-27):**
- N2: hotel_id es "amazilia_hotel" (CON guion bajo), NO "amaziliahotel"
- N5: TODOS los assets tienen confidence 0.5, NO existen valores de 0.85
- M1: hotel_name es "Amazilia Hotel" (CON espacio), NO "Amaziliahotel"
- H2: Archivos de diagnostico y propuesta SI existen (no estaban en el path original)
- Entregables: 0/7 completos (NO 2/7 como decia el contexto original)

---

## Sitio de Prueba

- **Hotel**: Amazilia Hotel
- **URL**: https://amaziliahotel.com/
- **hotel_id**: amazilia_hotel (CON guion bajo — verificado en directorio Y en JSON)
- **Region**: Eje Cafetero, Pereira, Risaralda, Colombia
- **Version**: v4.36.0 (PATCH Forense AmaziliaHotel)
- **Directorio output**: `output/v4_complete/amazilia_hotel/`

---

## Cadena de Fases Completadas

| Fase | Version | Estado | Fecha |
|------|---------|--------|-------|
| FASE-TRAZABILIDAD-DOCS | v4.35.1 | OK | 2026-04-25 |
| FASE-TRAZABILIDAD-RAIZ | v4.35.1 | OK | 2026-04-25 |
| FASE-TRAZABILIDAD-VALIDATE | v4.35.1 | OK | 2026-04-25 |
| FASE-TRAZABILIDAD-PATCH+SEO | v4.35.1 | OK | 2026-04-25 |
| FASE-TRAZABILIDAD-REFINEMENT | v4.35.1 | OK | 2026-04-25 |
| PATCH Forense FASE-A/B/C/D | v4.36.0 | OK | 2026-04-26 |
| FASE-TRAZABILIDAD-VALIDATE-v2 | v4.36.0 | OK | 2026-04-27 |

---

## Resultado de VALIDATE-v2 (Validado contra outputs reales)

- **Veredicto**: SUPERADO (14/15, 1 parcial)
- **Coherence**: 0.893 (diagnostico YAML L5) / 0.88 (coherence_validation.json)
- **Publication**: READY_FOR_PUBLICATION
- **Gates**: 9/9 ejecutados (NO verificable — gate_report.json NO existe en disco)
- **Commit**: f2575e5 (confirmado en git log)

---

## HALLAZGO PARCIAL: T4 — "Salud Técnica GEO" no aparece en primera corrida

### Estado: CONFIRMADO (validado contra código Y output)

### Descripcion

La row "Salud Técnica GEO" NO aparece en la tabla `ia_metrics_table` del diagnostico markdown cuando se hace una corrida fresca, a pesar de que el codigo en `v4_diagnostic_generator.py` L1287-1300 SI tiene la logica para generarla.

### Causa Raiz — Timing del Pipeline (CONFIRMADO)

```
main.py L2232: Diagnostico generado (FASE 3.5)
    └── v4_diagnostic_generator.py L1290: busca geo_flow_result.json
        └── NO LO ENCUENTRA (aun no existe)
    └── ia_metrics_table se genera SIN "Salud Técnica GEO"

main.py L2410: Assets generados (FASE 4)
    └── v4_asset_orchestrator.py L435: geo_flow_result.json SE CREA aqui
    └── Pero el diagnostico ya fue generado en FASE 3.5
```

### Evidencia en Output Real

Diagnostico `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260427_185630.md` L66-76:
```
### Métricas de Acceso para IA

## [NEW] Métricas de Optimización para IA

| Métrica | Score | Detalle | Estado |
|---------|-------|---------|--------|
| Accesibilidad IA | 0.50/1.00 | 14 bloqueados | 🟡 |
| Citabilidad | 51.7/100 | 3 bloques | 🟢 |
| IA-Readiness | 33.2/100 | Critical | 🟡 |
```

**Observacion**: NO aparece "Salud Técnica GEO" — CONFIRMADO que el timing impide su inclusion.

### Codigo Afectado

```python
# v4_diagnostic_generator.py L1287-1300 — busca geo_flow_result.json
# v4_asset_orchestrator.py L435 — crea geo_flow_result.json
# main.py L2232 vs L2410 — orden FASE 3.5 vs FASE 4
```

### Posibles Soluciones

1. Regenerar diagnostico post-assets
2. Pre-generar geo_flow antes de FASE 3.5
3. Segunda pasada: regenerar solo ia_metrics_table

### Impacto: Menor — la info GEO principal SI aparece (62/100 en tabla de Scores)

---

## HALLAZGOS VERIFICADOS (5 originales + 4 nuevos)

### N1: Header `[NEW]` hardcodeado en generator — CONFIRMADO

- **Ubicacion**: `v4_diagnostic_generator.py` L1308
- **Problema**: Generator inyecta `## [NEW] Métricas de Optimización para IA` pero el template `diagnostico_v6_template.md` L61 tiene `### Métricas de Acceso para IA`. Dos fuentes de verdad.
- **Evidencia**: Diagnostico real L66-69 muestra AMBOS headers (template + generator)
- **Severidad**: Baja — cosmético, no funcional

### N2: hotel_id — CORREGIDO (2da pasada)

- **Contexto original decia**: "amaziliahotel" (sin guion bajo)
- **REALIDAD VERIFICADA**: hotel_id es `amazilia_hotel` (CON guion bajo)
- **Evidencia**:
  - Directorio: `output/v4_complete/amazilia_hotel/` (existe)
  - asset_generation_report.json L2: `"hotel_id": "amazilia_hotel"`
  - diagnostico YAML L4: `hotel_id: amazilia_hotel`
  - propuesta YAML L4: `hotel_id: amazilia_hotel`
- **Causa**: `_sanitize_hotel_id()` en v4_asset_orchestrator.py L449-451 reemplaza espacios con guiones bajos
- **Severidad**: Baja — consistente en todos los archivos

### N3: PageSpeed API key — NO VERIFICABLE

- **Claim original**: API key puede estar expirada/invalida
- **Problema**: `pagespeed_client.py` NO fue encontrado en el código (búsqueda retornó 0)
- **Severidad**: Desconocida — requiere localizar el archivo en sesion futura

### N4: LLM queries fallidas — NO VERIFICABLE

- **Claim original**: Google API usa `gemini-2.0-flash` sin `-001` (L268)
- **Problema**: `llm_mention_checker.py` NO fue encontrado en el código (búsqueda retornó 0)
- **Severidad**: Desconocida — requiere localizar el archivo en sesion futura

### N5: Assets confidence — CORREGIDO (2da pasada)

**Contexto original decia**: hotel_schema, faq_page, llms_txt tienen confidence 0.85; otros tienen 0.50

**REALIDAD VERIFICADA** (asset_generation_report.json):

| Asset | confidence_score | preflight_status | can_use (report) |
|-------|-----------------|------------------|------------------|
| hotel_schema | **0.50** | WARNING | true |
| optimization_guide | **0.50** | WARNING | true |
| llms_txt | **0.50** | WARNING | true |
| faq_page | **0.50** | WARNING | true |
| geo_playbook | **0.50** | WARNING | true |
| review_plan | **0.50** | WARNING | true |
| analytics_setup_guide | **0.50** | WARNING | true |
| indirect_traffic_optimization | **0.50** | WARNING | true |
| og_tags_guide | **0.50** | WARNING | true |
| open_graph | **0.50** | WARNING | true |
| org_schema | **0.50** | WARNING | true |
| monthly_report | **0.50** | WARNING | true |

**Total**: 12/12 assets con confidence 0.50, 12/12 con WARNING. NO existen valores de 0.85 ni status PASSED.

- **Severidad**: Media — la diferencia entre 0.50 y 0.85 es significativa para gates

---

## NUEVOS HALLAZGOS (4 identificados en 1ra pasada)

### M1: hotel_name — CORREGIDO (2da pasada)

- **Contexto original decia**: "Amaziliahotel" (sin espacio)
- **REALIDAD VERIFICADA**: asset_generation_report.json L3: `"hotel_name": "Amazilia Hotel"` (CON espacio)
- **Conclusion**: El espacio se preserva en hotel_name. Solo hotel_id se sanitiza (con guion bajo).
- **Severidad**: Nula — no es un bug

### M2: Assets duplicados por doble corrida sin limpieza

- **Evidencia**: No se verificó en 2da pasada (requeriría comparar timestamps)
- **Severidad**: Baja — asumido correcto del contexto original

### M3: can_use inconsistente entre metadata y report — CONFIRMADO

- **Evidencia**:
  - Metadata hotel_schema L12: `"can_use": false`
  - Metadata faq_page L12: `"can_use": false`
  - asset_generation_report.json L28: `"can_use": true`
- **Causa raiz**: Dos lógicas diferentes:
  - `v4_asset_orchestrator.py` L868-870: `can_use = preflight_status == "PASSED" or (preflight_status == "WARNING" and asset_spec.confidence_level != "CONFLICT")`
  - `asset_metadata.py` L151-173: `_calculate_can_use()` rechaza si confidence_score < 0.5
- **Impacto**: Confusion sobre si un asset es usable. El report dice "si", la metadata dice "no".
- **Severidad**: Media — afecta confianza en el sistema de gates

### M4: Paths Windows (backslashes) en outputs generados — CONFIRMADO

- **Evidencia**: Todos los JSON usan `output\\v4_complete\\amazilia_hotel`
- **Ejemplo**: asset_generation_report.json L5: `"output_dir": "output\\v4_complete\\amazilia_hotel"`
- **Causa**: Python en Windows genera backslashes con `str(path)` sin normalizar
- **Severidad**: Baja — legibilidad, posible problema en scripts que parsean paths

---

## NUEVO HALLAZGO (2da pasada)

### H1: Asset fallido no reportado

- **Tipo**: local_content_page
- **Razon**: "Generation failed: Unknown asset type: local_content_page"
- **Preflight**: BLOCKED
- **Evidencia**: asset_generation_report.json L172-180
- **Impacto**: 1 de 13 assets falló completamente. El contexto original decia "12/12 generados" — FALSO, son 12/13.
- **Severidad**: Media — el asset no se genera, pain "low_ia_readiness" queda sin resolver

---

## Entregables Comerciales — CORREGIDO (2da pasada)

> Fuente: `output/v4_complete/02_PROPUESTA_COMERCIAL_20260427_185633.md` L61-73

### Contexto original decia: "2 de 7 completos"

### REALIDAD VERIFICADA: 0 de 7 completos

| Entregable | Nivel | Estado |
|------------|-------|--------|
| Google Maps Optimizado | ⚠️ En preparacion | Datos pendientes del cliente |
| SEO Local | ⚠️ En preparacion | Datos pendientes del cliente |
| Botón de WhatsApp | ⏳ Incluido en su kit | Preparacion posterior a la firma |
| Datos Estructurados | ⚠️ En preparacion | Datos pendientes del cliente |
| Informe Mensual | ⚠️ En preparacion | Datos pendientes del cliente |
| Página de FAQ | ⚠️ En preparacion | Datos pendientes del cliente |
| Meta Tags Sociales (Open Graph) | ⚠️ En preparacion | Datos pendientes del cliente |

**Ningun entregable esta marcado como "Completo"** en la propuesta real.

---

## Datos Financieros — VERIFICADOS

> Fuente: diagnostico YAML + propuesta MD

| Concepto | Valor | Fuente |
|----------|-------|--------|
| Pérdida mensual estimada | $2.610.000 COP | diagnostico YAML L13 |
| Comisión OTA real | $5.400.000 COP/mes | diagnostico YAML L14 |
| Inversión mensual | $130.500 COP/mes | propuesta L40 |
| Total 6 meses | $783.000 COP | propuesta L112 |
| Beneficio neto | $0 COP | propuesta L114 |
| ROI | 0.2 | propuesta L115 |
| Evidence tier | C | diagnostico YAML L8 |
| Proyección 6 meses | $15.660.000 COP | diagnostico L169 |

---

## Scores de Visibilidad — VERIFICADOS

> Fuente: diagnostico L52-57

| Indicador | Su Negocio | Promedio Regional | Estado |
|-----------|------------|------------------|--------|
| SEO Local | 25/100 | 59/100 | ❌ Bajo |
| GEO | 62/100 | 89/100 | ❌ Bajo |
| AEO | 0/100 | 44/100 | ❌ Bajo |
| IAO | 33/100 | 20/100 | ✅ Superior |

---

## Datos del Hotel — VERIFICADOS

> Fuente: diagnostico L82-85

- **WhatsApp**: +57 3104019049 (verificado)
- **GBP**: 202 reviews, 4.5/5 rating
- **HTTPS**: Activo
- **Redes sociales**: Facebook, Instagram, YouTube activas

---

## Brechas Identificadas — VERIFICADAS

> Fuente: diagnostico L119-158

| # | Brecha | Impacto | Costo/mes |
|---|--------|---------|-----------|
| 1 | Sin Schema de Hotel | 20% | $530.613 COP |
| 2 | Metadatos por Defecto CMS | 8% | $212.193 COP |
| 3 | Baja Preparación para IA | 12% | $318.420 COP |
| 4 | Sin FAQ para Rich Snippets | 9% | $254.736 COP |
| 5 | Visibilidad Local (Maps) | 24% | $636.579 COP |
| 6 | IA Bloqueada (ChatGPT) | 12% | $318.420 COP |
| 7 | Sin Meta Tags OG | 6% | $169.650 COP |
| 8 | Sin Schema Organization | 6% | $169.650 COP |

**Total brechas**: 8 (88% del impacto total estimado)

---

## Defecciones Pendientes (3 de 18 hallazgos originales)

| ID | Descripcion | Razon de deferral |
|----|-------------|-------------------|
| C10 | Benchmarks sin trace de fuente | Requiere diseno de trazabilidad para benchmarks regionales |
| D16 | Contexto regional hardcoded | Requiere diseno de dynamic regional context |
| D17 | Competidores stub (sin datos reales) | Requiere API de competidores |

## Decision Diferida

| Decision | Descripcion | Estado |
|----------|-------------|--------|
| D1 | WARNING gates deberian cambiar readiness a REQUIRES_REVIEW? | Diferida a sesion dedicada |

---

## Archivos de Referencia — Estado Real (2da pasada)

| Archivo | Estado | Path Real | Nota |
|---------|--------|-----------|------|
| Diagnóstico | **EXISTE** | `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260427_185630.md` | NO en subdirectorio amazilia_hotel |
| Propuesta Comercial | **EXISTE** | `output/v4_complete/02_PROPUESTA_COMERCIAL_20260427_185633.md` | NO en subdirectorio amazilia_hotel |
| asset_generation_report.json | **EXISTE** | `output/v4_complete/amazilia_hotel/v4_audit/asset_generation_report.json` | 12/13 assets, 1 fallido |
| coherence_validation.json | **EXISTE** | `output/v4_complete/amazilia_hotel/v4_audit/coherence_validation.json` | Score 0.88, 6/6 checks |
| geo_flow_result.json | **EXISTE** | `output/v4_complete/amazilia_hotel/v4_audit/geo_flow_result.json` | Score 23/100, band critical |
| gate_report.json | **NO EXISTE** | — | No encontrado en output/ |
| VALIDATION_RESULTS.md | **NO EXISTE** | — | Referenciado originalmente pero no encontrado |
| 06-checklist-implementacion.md | **NO EXISTE** | — | Referenciado originalmente pero no encontrado |
| dependencias-fases.md | **NO EXISTE** | — | Referenciado originalmente pero no encontrado |
| v4_complete_report.json | **NO EXISTE** | — | Solo en archives/ |

### Contenido verificado — Propuesta L61-73

La propuesta comercial en L61 (`### 📋 Estado de los Entregables`) muestra:

```markdown
| Entregable | Nivel | Que significa |
|------------|-------|---------------|
| Google Maps Optimizado | ⚠️ En preparacion | Datos pendientes del cliente |
| SEO Local | ⚠️ En preparacion | Datos pendientes del cliente |
| Botón de WhatsApp | ⏳ Incluido en su kit | Preparacion posterior a la firma |
| Datos Estructurados | ⚠️ En preparacion | Datos pendientes del cliente |
| Informe Mensual | ⚠️ En preparacion | Datos pendientes del cliente |
| Página de FAQ | ⚠️ En preparacion | Datos pendientes del cliente |
| Meta Tags Sociales (Open Graph) | ⚠️ En preparacion | Datos pendientes del cliente |
```

**Veredicto**: 0/7 entregables marcados como "Completo". Todos en estado "En preparacion" o "Incluido en su kit".

---

## Resumen Ejecutivo para el Proximo Plan

### Que requiere intervención (verificado contra código Y outputs):

1. **T4 (timing pipeline)** — "Salud Técnica GEO" no aparece en primera corrida — CONFIRMADO
2. **N1 (header dual)** — Template L61 + Generator L1308 crean dos headers — CONFIRMADO
3. **M3 (can_use inconsistente)** — Metadata=false, Report=true — CONFIRMADO
4. **H1 (asset fallido)** — local_content_page no se genera — CONFIRMADO
5. **M4 (backslashes)** — Paths Windows en JSON — CONFIRMADO

### Que requiere verificación adicional:

6. **N3 (PageSpeed key)** — Archivo no localizado
7. **N4 (Gemini model)** — Archivo no localizado

### Que ya funciona (confirmado contra outputs):

- Coherence 0.893 (diagnostico) / 0.88 (validation) — ✅
- 12/13 assets generados (1 fallido: local_content_page) — ⚠️
- Scores: SEO 25, GEO 62, AEO 0, IAO 33 — ✅
- 8 brechas identificadas con costos — ✅
- Propuesta comercial generada — ✅
- Datos financieros consistentes — ✅

### Prioridad sugerida para el plan:

1. **Alta**: T4 (timing) + M3 (can_use) + H1 (asset fallido)
2. **Media**: N1 (header) + M4 (paths)
3. **Pendiente verificación**: N3 (PageSpeed) + N4 (Gemini)
4. **Diferida**: C10, D16, D17, D1

---

## Precision del Contexto Original

| Metrica | Valor |
|---------|-------|
| Claims verificados | 9 |
| Claims correctos | 4 (T4, N1, M3, M4) |
| Claims corregidos | 3 (N2, N5, M1) |
| Claims no verificables | 2 (N3, N4) |
| Hallazgos nuevos añadidos | 1 (H1) |
| **Precisión global** | **44% (4/9)** |
