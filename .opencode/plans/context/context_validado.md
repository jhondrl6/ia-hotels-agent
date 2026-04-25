# Contexto Validado: Propuesta Comercial Amazilia Hotel — Intervencion iah-cli v4.35.0
# Fecha validacion: 2026-04-23
# Validador: auditoria cruzada codigo + tests + output real

## Referencia Cruzada

- **Documento auditado:** `output/v4_complete/02_PROPUESTA_COMERCIAL_20260423_145443.md`
- **Datos financieros:** `output/v4_complete/financial_scenarios.json`
- **Hotel (Google Maps name):** Amazilia Hotel
- **URL:** https://amaziliahotel.com/
- **Version iah-cli:** 4.35.0

---

## Estado de Tests (REALIDAD OPERACIONAL)

- **Validaciones quick:** 4/4 PASS
- **Tests commercial_documents:** 118 passed, 1 FAILED
- **Tests totales proyecto:** 2224 funciones, 140 archivos
- **Fallo activo:** `TestAssetQualityTable.test_proposal_includes_quality_table` — ver BUG-10

---

## Arquitectura del Generador (archivos clave)

| Archivo | Rol |
|---------|-----|
| `modules/commercial_documents/v4_proposal_generator.py` | Generador principal (1151 lineas). Clase `V4ProposalGenerator`. Busca template V6, cae a V4 embebido. |
| `modules/commercial_documents/service_catalog.py` | `SERVICE_CATALOG` (7 entries): mapea pain_id -> servicio vendible. Creado en FASE-CAUSAL-REFACTOR. |
| `modules/asset_generation/proposal_asset_alignment.py` | `PROPOSAL_SERVICE_TO_ASSET` (7 servicios): mapea nombre servicio -> asset_type. Fuente de verdad para modo estatico. |
| `modules/commercial_documents/templates/` | Solo existe `diagnostico_v4_template.md`. **NO existe `propuesta_v6_template.md`**. |
| `modules/financial_engine/calculator_v2.py` | Calculo de escenarios financieros. Orden de escenarios invertido detectado. |
| `modules/financial_engine/pricing_resolution_wrapper.py` | `PricingResolutionResult` con `monthly_price_cop`. |

---

## BUGS VALIDADOS Y AMPLIADOS

### BUG-1 (CRITICO): Seccion "Esto es lo que hacemos por usted" VACIA

**Confirmado:** `_generate_dynamic_services_table()` retorna `""` cuando `detected_pain_ids` es None/empty.
**Impacto:** La propuesta generada tiene una seccion vacia entre titulo y cierre.

### BUG-2 (CRITICO): Escenarios financieros INVERTIDOS

**Confirmado:** `financial_scenarios.json` muestra conservative > realistic > optimistic (negativo).
**Causa:** `_get_main_value()` usa `monthly_loss_central` o `monthly_loss_max` pero el ordenamiento de escenarios esta roto.

### BUG-3 (CRITICO): ROI de 20.0X irreal

**Confirmado:** `_calculate_roi()` usa recuperacion 100% sin recovery_factor. Pain_ratio 5% nunca se aplica a la proyeccion.

### BUG-4 (ALTO): Tabla de entregables muestra errores al cliente

**Confirmado:** 5 de 7 items dicen "Requiere datos" o "No generado". La propuesta se genera ANTES de los assets.

### BUG-5 (ALTO): No existe template V6

**Confirmado:** El generador cae a `_get_default_template()` (linea 234). La seccion "Asi funciona" proviene de un tercer template embebido o residual.

### BUG-6 (ALTO): Planes 7/30/60/90 dias hardcoded

**Confirmado:** `_build_7_day_plan()`, `_build_30_day_plan()`, etc. retornan strings fijos, ignoran `asset_plan`.

### BUG-7 (MEDIO): Disclaimer financiero no aparece en propuesta

**Confirmado:** `financial_scenarios.json` tiene disclaimer pero no se inyecta en template cuando evidence_tier es "C".

### BUG-8 (BAJO): Ortografia en template embebido

**Confirmado:** Errores en `_get_default_template()`: "hotels" -> "hoteles", "brillen" -> "brille", "prover" -> "proveer", etc.

### BUG-9 (BAJO): Secciones vacias y placeholder telefonico

**Confirmado:** Metricas de visibilidad sin contenido, telefono "+57 300 000 0000".

### BUG-10 (CRITICO — NUEVO, no estaba en context.md original): Test drift en proposal_confidence_disclosure

**Hallazgo:** `tests/commercial_documents/test_proposal_confidence_disclosure.py` FALLA.
**Error:** `AssertionError: Servicio faltante en tabla: Visibilidad en ChatGPT`
**Analisis:**
- El test espera 6 servicios: [Google Maps Optimizado, Visibilidad en ChatGPT, SEO Local, Boton de WhatsApp, Datos Estructurados, Informe Mensual]
- **"Visibilidad en ChatGPT" fue eliminado/renombrado** en versiones recientes pero el test no se actualizo.
- El test **NO incluye** los 2 servicios agregados en v4.34.0: "Pagina de FAQ" y "Meta Tags Sociales (Open Graph)".
- El comentario del test dice "6 services" pero PROPOSAL_SERVICE_TO_ASSET tiene 7.

**Fix requerido:** Actualizar test para reflejar los 7 servicios actuales de PROPOSAL_SERVICE_TO_ASSET.

### BUG-11 (ALTO — NUEVO): Desalineacion SERVICE_CATALOG vs PROPOSAL_SERVICE_TO_ASSET

**Hallazgo:** Las dos fuentes de verdad para `_generate_asset_quality_table()` tienen 7 entradas cada una pero **diferentes**.

| PROPOSAL_SERVICE_TO_ASSET (modo estatico) | SERVICE_CATALOG (modo dinamico) |
|-------------------------------------------|--------------------------------|
| Google Maps Optimizado | Google Maps Optimizado |
| SEO Local | SEO Local |
| Boton de WhatsApp (sin tilde) | Boton de WhatsApp (CON tilde) |
| Datos Estructurados | Datos Estructurados |
| Informe Mensual | **Barra de Reserva Movil** (NO Informe Mensual) |
| Pagina de FAQ | Pagina de FAQ |
| Meta Tags Sociales (Open Graph) | Meta Tags Sociales (Open Graph) |

**Impacto:** `_generate_asset_quality_table()` produce tablas DIFERENTES dependiendo de si `detected_pain_ids` esta presente:
- Con pains: 7 servicios de SERVICE_CATALOG (incluye Barra de Reserva Movil, omite Informe Mensual)
- Sin pains: 7 servicios de PROPOSAL_SERVICE_TO_ASSET (incluye Informe Mensual, omite Barra de Reserva Movil)

**Fix requerido:** Definir fuente de verdad unica. SERVICE_CATALOG debe tener los mismos 7 servicios que PROPOSAL_SERVICE_TO_ASSET.

---

## DESALINEACIONES DIAGNOSTICO <-> PROPUESTA (D-1 a D-8)

Todas confirmadas y validadas contra codigo fuente:

| ID | Severidad | Estado | Descripcion |
|----|-----------|--------|-------------|
| D-1 | CRITICA | PENDIENTE | AEO score 0/100 sin plan de recuperacion en propuesta |
| D-2 | CRITICA | PENDIENTE | Pain_ratio 5% vs recuperacion 100% en ROI — triangulo imposible |
| D-3 | CRITICA | PENDIENTE | ADR hardcodeado $300K — proyeccion financiera es ficcion |
| D-4 | ALTA | PENDIENTE | Quick wins = 30 dias en diagnostico, promesa = 7 dias en propuesta |
| D-5 | ALTA | PENDIENTE | WhatsApp presentado como brecha sin ser pain detectado ni cuantificado |
| D-6 | ALTA | PENDIENTE | GA4 prometido sin plan de implementacion ni costo de setup |
| D-7 | ALTA | PENDIENTE | 6 de 7 entregables bloqueados/"Requiere datos" antes de firma |
| D-8 | MEDIA | PENDIENTE | Sin competidores identificados en propuesta |

---

## AJUSTES AL CONTEXT ORIGINAL

1. **Conteo de tests:** El contexto original dice "385 tests pasando". Realidad: 1 test fallando en commercial_documents. Corregido arriba.
2. **FASE-CAUSAL:** El parche estatico SI creo `service_catalog.py`, pero la propagacion de `detected_pain_ids` al generador sigue rota (viene None). Esto significa el modo dinamico nunca se activa en produccion.
3. **Template V6:** La no-existencia del template V6 es un blocker para BUG-1 (fallback de servicios dinamicos) y para corregir BUG-8 (ortografia).

---

## RESTRICCIONES DE LA INTERVENCION

- **Una fase por sesion** (regla absoluta phased_project_executor)
- **Optimizacion de costos API:** Solo UNA ejecucion v4complete (FASE-VALIDATE)
- **Hotel de prueba:** "Amazilia Hotel" (nombre exacto Google Maps), URL https://amaziliahotel.com/
- **Prioridad:** Corregir bugs de codigo/test primero (sin costo API), luego validar con v4complete
