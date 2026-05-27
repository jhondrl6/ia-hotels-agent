# Documentación Post-Proyecto — ROI-REFACTOR

**Plan**: ROI-REFACTOR
**Target**: v4.54.0
**Iniciado**: 2026-05-26
**Actualizado**: 2026-05-26 (FASE-C completada)

---

## A. Módulos Modificados

||| Fase | Módulo | Archivo | Cambio |
|------|--------|---------|--------|
| FASE-1 | commercial_documents | `v4_proposal_generator.py` | `document_audience` param en `generate()` + alertas condicionadas a `internal` |
| FASE-1 | commercial_documents | `v4_diagnostic_generator.py` | `document_audience` param en `generate()` + alertas condicionadas a `internal` |
| FASE-1 | commercial_documents | `propuesta_v6_template.md` | Eliminado placeholder testimonios, agregado `{{if testimonials_present == "true"}}...{{endif}}` |
| FASE-2 | commercial_documents | `v4_proposal_generator.py` | Tabla entregables: "Nivel"→"Momento de entrega" + "Qué significa"→"Qué incluye"; estados mapeados a fechas concretas (Día 1, Semana 1, Semana 2); P1/P2/P3→Fase 1/2/3 con descripciones |
| FASE-2 | commercial_documents | `propuesta_v6_template.md` | Nota AEO→"Optimización para Asistentes de Voz (Siri, Alexa, Google)"; leyenda P1/P2/P3→Fase 1/2/3 |
| FASE-3 | main | `main.py` | `adr_source` agregado a `financial_scenarios.json` (input_data) para trazabilidad de fuente de ADR |
| FASE-3 | commercial_documents | `v4_proposal_generator.py` | `_get_pipeline_version()` + `PIPELINE_VERSION` desde `VERSION.yaml`; reemplazado hardcode `'4.0.0'` en frontmatter |
| FASE-3 | commercial_documents | `v4_diagnostic_generator.py` | `_get_pipeline_version()` + `PIPELINE_VERSION` desde `VERSION.yaml`; reemplazado hardcode `'4.0.0'` en frontmatter |

---

## B. Funcionalidades Agregadas/Modificadas

||| Fase | Funcionalidad | Descripción |
|------|--------------|-------------|
| FASE-1 | Hidden commercial alerts | El bloque `⚠️ Alertas Comerciales` se inyecta solo cuando `document_audience="internal"`; con `document_audience="client"` (default) se omite del documento |
| FASE-1 | Testimonials conditional | La sección "Hoteles que ya confiaron en nosotros" se renderiza solo si `testimonials_present="true"`, caso contrario se omite completamente |
| FASE-1 | pain_ratio note semántica | La nota de proyección ahora dice "La inversión mensual representa el X% de su pérdida mensual" en vez del incorrecto "el X% representa la porción del dolor financieramente abordable con IAO" |
| FASE-2 | Lenguaje de negocio en propuesta | "AEO"→"Optimización para Asistentes de Voz (Siri, Alexa, Google)"; "UTMs"→"sistema de rastreo para medir de dónde viene cada reserva"; "P1/P2/P3"→"Fase 1/2/3" con descripciones (WhatsApp+datos IA, Contenido+FAQs, Guías locales) |
| FASE-2 | Tabla de entregables con fechas concretas | Columnas "Nivel"→"Momento de entrega" y "Qué significa"→"Qué incluye"; estados reemplazados por fechas (Día 1, Semana 1, Semana 2); sin % confianza |
| FASE-3 | ADR source en financial_scenarios.json | `adr_source` expuesto explícitamente en `input_data` del JSON para trazabilidad (antes solo implícito vía precision_tier) |
| FASE-3 | Versión dinámica en frontmatter | `PIPELINE_VERSION` lee `VERSION.yaml` (v4.53.0) — antes hardcodeado `4.0.0` en proposal y diagnostic generators |

---

## C. Decisiones de Diseño

|| ID | Decisión | Justificación |
|----|----------|--------------|
| D01 | `document_audience` default = "client" | Seguridad: si no se especifica, el output es seguro para el cliente |
| D02 | Placeholder testimonios: condicional `{% if %}` | Mejor omitir sección que mostrar placeholder vacío |
| D03 | pain_ratio note: "relación inversión/pérdida" | Corrección semántica: pain_ratio = price/expected_loss, no "% IAO" |
| D04 | ADR fallback order: user → web_scraping → benchmark → hardcode | El precio del sitio web es más específico que el benchmark regional |
| D05 | Versión: importar de fuente canónica, fallback "4.0.0" | Trazabilidad sin riesgo de crash |
| D06 | Anexo APIs → párrafo transparencia | El dueño no necesita ver costos de infraestructura |
| D07 | No modificar commercial_gate.py | El validador funciona bien; es el caller quien decide renderizar |
| D08 | FASE-0 como prerrequisito | Decisión comercial antes de inversión técnica — evita implementar código para propuesta invendible |

---

## D. Deudas Técnicas Conocidas

|| ID | Deuda | Severidad | Plan |
|----|-------|-----------|------|
| DT01 | ROI negativo para hoteles boutique sin GA4 | Comercial | Solucionado por decisión FASE-0 (opciones A/B/C/D + B+C) |
| DT02 | pain_ratio 20% (diag) vs 41% (prop) es divergencia intencional | Baja | Documentado en nota de diagnóstico (FASE-4) |
| DT03 | evidence_tier B + precision_tier C con COP exactos | Media | Documentado en FASE-4; redondeo pendiente |
| DT04 | precision_tier=C + can_show_exact_money=false → sin redondeo implementado | Media | Gap conocido — no bloquea entrega |

---

## E. Archivos del Plan

|| Archivo | Estado |
|---------|--------|
| `README.md` | ✅ Actualizado v1.1.0 (con FASE-0) |
| `dependencias-fases.md` | ✅ Actualizado (FASE-0 a FASE-5, numeración corregida) |
| `05-prompt-inicio-sesion-fase-0.md` | ✅ Creado |
| `05-prompt-inicio-sesion-fase-A.md` | ✅ Existente (reenumerate a FASE-1) |
| `05-prompt-inicio-sesion-fase-B.md` | ✅ Existente (reenumerate a FASE-2) |
| `05-prompt-inicio-sesion-fase-C.md` | ✅ Existente (reenumerate a FASE-3) |
| `05-prompt-inicio-sesion-fase-D.md` | ✅ Existente (reenumerate a FASE-4) |
| `05-prompt-inicio-sesion-fase-E.md` | ✅ Existente (reenumerate a FASE-5) |
| `06-checklist-implementacion.md` | ✅ Actualizado (con FASE-0) |
| `09-documentacion-post-proyecto.md` | ✅ Este archivo |

---

## F. Registro de Ejecución

### FASE-0 — Decisión Comercial

**Fecha**: 2026-05-26

| Opción evaluada | Análisis | Decisión |
|----------------|----------|----------|
| A — Lower pricing | Viable si se baja el fee a $300-400K/mes: el recovery realista (~$305K/mes) deja de destruir ROI. El problema es que reduce 4x el revenue frente al pricing boutique actual y puede anclar el servicio como barato. | ❌ No elegida como modelo principal |
| B — Quick wins | Proyecto único de bajo riesgo para resolver WhatsApp conflict guide, Schema Hotel y llms.txt. Cierra mejor para hotel boutique sin GA4 porque evita vender un retainer que el modelo financiero no soporta todavía. | ✅ Base de entrada |
| C — % recovery | Alinea incentivos, pero no puede arrancar sin medición confiable. Con el recovery estimado actual, 15% equivale a ~$45K/mes: demasiado bajo como única monetización. | ✅ Usar solo como Fase 2 post-tracking |
| D — Transparencia total | Éticamente defendible, pero comercialmente débil: mantener $1.2M/mes mientras el ROI proyectado es negativo obliga a vender una pérdida esperada. | ❌ Rechazada para Castilla Real |
| **B+C combinada** | Activación pagada de $250K → instalación de tracking → upsell a % recovery real. Reduce fricción, genera evidencia y evita prometer ROI financiero no demostrado. | ✅ Recomendada |
| **E — Piloto con crédito a retainer + success fee capped** | Variante fuera de las 4 opciones: cobrar una activación/piloto de $250K, acreditar ese valor contra un retainer futuro si el hotel continúa, y convertir el success fee en un porcentaje con techo mensual. Mejora B+C porque elimina la objeción de "pago doble" y conserva upside si el recovery real supera el estimado. | ✅ **Opción preferida para pitch comercial** |

**Decisión operativa registrada**: avanzar con **Opción E** como recomendación comercial para Hotel Castilla Real. E conserva la entrada de bajo riesgo de B, usa C solo después de tracking real, y agrega crédito a retainer para hacer más fácil el cierre.

**Pricing Preliminar — Fase 1 Activación / Piloto**:

| componente | precio |
|------------|--------|
| WhatsApp conflict guide | Incluido |
| Schema Hotel instalación | Incluido |
| llms.txt | Incluido |
| Diagnóstico completo | Incluido |
| Instalación/revisión de tracking mínimo para medir baseline | Incluido |
| Crédito aplicable a retainer futuro si continúa antes de 30 días | $250,000 COP |
| **Total proyecto único** | **$250,000 COP** |
| Duración estimada | 1-2 semanas |

**Fase 2 sugerida post-piloto**:

| componente | regla comercial |
|------------|-----------------|
| Trigger | Día 30-45, solo con baseline/tracking operativo |
| Modelo | 15% del recovery mensual real atribuible |
| Techo sugerido | Hasta $1,200,000 COP/mes mientras se valida escala |
| Protección cliente | Si no hay recovery medible, no se activa success fee |
| Protección proveedor | Si hay señales fuertes, el crédito del piloto facilita transición a retainer |

**Conclusión FASE-0**: no continuar vendiendo Castilla Real con retainer fijo de $1.2M/mes desde el día 1. La vía comercial defendible es piloto pagado + medición + monetización variable/capped con crédito a retainer.

---

### FASE-1 a FASE-5

|| Fase | Fecha | Resultado | Evidencia |
|------|-------|---------|-----------|
| FASE-1 | 2026-05-26 | ✅ 4/4 fixes aplicados | `v4_proposal_generator.py`, `v4_diagnostic_generator.py`, `propuesta_v6_template.md` |
| FASE-2 | 2026-05-26 | ✅ 2/2 fixes aplicados | `propuesta_v6_template.md`, `v4_proposal_generator.py` |
| FASE-3 | 2026-05-26 | ✅ Verificación + 2 fixes | ADR ya conectado (verificado); adr_source agregado a JSON; PIPELINE_VERSION en ambos generators |
| FASE-4 | — | — | — |
| FASE-5 | — | — | — |
