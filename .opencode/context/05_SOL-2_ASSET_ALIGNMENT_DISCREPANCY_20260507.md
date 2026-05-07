---
generated_at: 2026-05-07 10:40
updated_at: 2026-05-07 15:46
version: 3.0.0
document_type: CONTEXT_KNOWN_ISSUE
related_plan: PROP-PATCH (FASE-PATCH-C) + SOL-2 (FASE-SOL2-D)
validation_type: E2E verification of v4complete for Termales Santa Rosa de Cabal
evidence_files:
  - evidence/FASE-PATCH-C/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260507_093302.md
  - evidence/FASE-PATCH-C/02_PROPUESTA_COMERCIAL_20260507_093310.md
  - evidence/FASE-PATCH-C/gate_report_20260507_093317.json
  - evidence/FASE-PATCH-C/coherence_validation.json
  - evidence/FASE-PATCH-C/asset_generation_report.json
trigger: FASE-PATCH-C E2E verification (v4complete Termales, 2026-05-07)
update_note: "v3.0 — 2026-05-07 15:46 — SOL2-D: GAP-G resuelta (falso positivo), GAP-D documentada, line range corregido a 755-865"
---

# CONTEXTO: Discrepancia SOL-2 — Proposal Asset Alignment

## RESUMEN EJECUTIVO

Durante la verificacion E2E de PATCH-C (v4complete para Termales Santa Rosa de Cabal), se observo que dos componentes de validacion reportan resultados distintos para la misma verificación de alineación propuesta-activos:

- **`coherence_validator._check_promised_assets_exist()`**: score=1.0, mensaje "Todos los assets prometidos están implementados"
- **`proposal_asset_alignment_gate`** (publication_gates.py): missing_count=3, status=WARNING

**Esta discrepancia NO es un bug.** Es una diferencia de enfoque entre dos validadores con bases de comparación distintas. Sin embargo, representa una brecha en la consistencia del sistema de validacion que debe documentarse y potencialmente resolverse.

---

## Hallazgos Detallados

### Componente 1: coherence_validator (score=1.0 PASS)

**Archivo**: `modules/commercial_documents/coherence_validator.py` (lineas 494-526)

**Logica**: `_check_promised_assets_exist()` verifica que los assets en la lista `assets` (AssetSpec) están en ASSET_CATALOG con status=IMPLEMENTED.

```python
promised_types = {a.asset_type for a in assets}
missing_types = [
    t for t in promised_types
    if not is_asset_implemented(t)
]
# Si no hay missing_types -> score=1.0, passed=True
```

**Resultado**: Los 6 assets generados (hotel_schema, faq_page, monthly_report, analytics_setup_guide, indirect_traffic_optimization, llms_txt) estan todos en ASSET_CATALOG como IMPLEMENTED -> 6/6 OK.

**Limitation**: Solo verifica si los assets generados estan en el catalogo, no si los servicios prometidos en la propuesta tienen assets correspondientes.

---

### Componente 2: proposal_asset_alignment_gate (missing_count=3, WARNING)

**Archivo**: `modules/quality_gates/publication_gates.py` (lineas 755-865)

**Logica**: `verify_proposal_asset_alignment()` compara `PROPOSAL_SERVICE_TO_ASSET` (contrato estático de 6 servicios) contra los assets generados y la verificacion de presencia en el sitio.

```python
# PROPOSAL_SERVICE_TO_ASSET (estatico, 6 servicios)
PROPOSAL_SERVICE_TO_ASSET = {
    "SEO Local": "optimization_guide",
    "Botón de WhatsApp": "whatsapp_button",
    "Datos Estructurados": "hotel_schema",
    "Informe Mensual": "monthly_report",
    "Página de FAQ": "faq_page",
    "Meta Tags Sociales (Open Graph)": "open_graph",
}
```

**Resultado**:
- aligned_count: 2 (hotel_schema, faq_page)
- missing_count: 3 (optimization_guide/SEO Local, whatsapp_button/Botón de WhatsApp, open_graph/Meta Tags Sociales)
- low_quality_count: 1 (monthly_report, confianza 0.5)

**Nota**: El gate verifica presencia en sitio via `SitePresenceChecker` para los missing. Para WhatsApp button: `presence_verified: true, presence_status: "not_exists"`.

---

## Servicios Filtrados en la Propuesta

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py` (lineas 839-908)

El generador de propuesta usa `_generate_dynamic_services_table(assets_generated=...)` que filtra por assets realmente generados:

```python
if assets_generated:
    generated_asset_types = {a.get("asset_type", "") for a in assets_generated}
    services = [entry for entry in SERVICE_CATALOG.values()
                if entry.asset_type in generated_asset_types]
```

**Resultado para Termales**: Solo 4 servicios filtrados (los que tienen assets generados):
1. Datos Estructurados (hotel_schema)
2. Página de FAQ (faq_page)
3. Informe Mensual (monthly_report)
4. Optimización para IA Generativa (conditional, score_aeo < 20)

Los servicios SEO Local, Botón de WhatsApp, y Meta Tags Sociales **NO aparecen** en la propuesta porque sus assets no se generaron. La propuesta NO promete lo que no puede entregar.

---

## Root Cause de la Discrepancia

**No es un bug — es un desacoplamiento intencional pero inconsistente:**

| Aspecto | coherence_validator | proposal_asset_alignment_gate |
|---------|---------------------|------------------------------|
| **Qué verifica** | Assets generados vs ASSET_CATALOG (status IMPLEMENTED) | Servicios prometidos en propuesta vs assets generados + presencia en sitio |
| **Baseline** | ASSET_CATALOG (6 implementados) | PROPOSAL_SERVICE_TO_ASSET (contrato estatico de 6 servicios) |
| **Pregunta** | "¿Los assets generados existen en el catalogo?" | "¿Los servicios prometidos tienen assets?" |
| **Resultado para Termales** | 6/6 OK | 2/6 aligned, 3/6 missing |

El coherence_validator responde: "¿Podemos generar lo que prometemos?" (respuesta: sí, el generador sabe generar esos 6).
El gate responde: "¿Lo que prometemos realmente existe?" (respuesta: no, 3 assets no existen en el sitio y no se generaron).

---

## Estado del Sistema

- **gate status**: WARNING (no bloqueante) — el sistema permite publicacion
- **Propuesta**: Correcta — solo promete 4 servicios con assets generados
- **Discrepancia**: Visible en los JSONs de validacion (inconsistencia para el operador/auditor)
- **Documentación**: Existe nota en `_proposal_asset_alignment_gate` docstring (linea 763-771) explicando el mismatch

---

## Gap Analysis

|| Gap | Descripcion | Impacto | Prioridad |
|-----|-------------|---------|-----------|
| **G1** | Los 3 assets faltantes (optimization_guide, whatsapp_button, open_graph) no se generaron para Termales | El kit de servicios esta incompleto vs el contrato de 6 servicios | Media |
| **G2** | ASSET_CATALOG los marca como IMPLEMENTED pero no se generaron | Contradiccion en catalogo vs realidad | Alta |
| **G3** | coherence_validator y gate muestran resultados inconsistentes para el mismo check | Confusion para operadores/auditores | Media |
| **G4** | No hay ticket/plan para resolver la brecha de los 3 assets faltantes | El issue queda abierto sin seguimiento | Alta |
| **G5** | Site verification/deployment no realizado — archivos solo en output/ | Pipeline no modifica sitio real del cliente | **Alta** |

---

## Opciones de Solucion

### Opcion A: Generar los 3 assets faltantes
**Descripcion**: Implementar la generacion de optimization_guide (SEO Local), whatsapp_button, y open_graph para que el catalogo de 6 servicios sea completo.

**Pros**:
- Cierra la brecha completamente
- Mantiene el contrato de 6 servicios

**Cons**:
- Requiere desarrollo nuevo (impacto desconocido)
- Puede requerir APIs externas o cambios en el pipeline de generacion

**Verificar**: ¿Estos assets están en el roadmap? ¿Son técnicamente viables para el alcance actual?

---

### Opcion B: Reducir el catálogo de servicios prometidos a 3-4
**Descripcion**: Actualizar `PROPOSAL_SERVICE_TO_ASSET` y `SERVICE_CATALOG` para que solo incluyan los servicios cuyos assets se generan actualmente (hotel_schema, faq_page, monthly_report + conditional AEO).

**Pros**:
- Elimina la discrepancia contrato-realidad
- No requiere desarrollo nuevo

**Cons**:
- Reduce el alcance del kit comercial
- Cambia el producto ofrecido

**Impacto en propuesta**: Menos servicios en el kit = menos valor percibido? Evaluar con equipo comercial.

---

### Opcion C: Unificar la validacion (discrepancia de reporting)
**Descripcion**: Hacer que coherence_validator y proposal_asset_alignment_gate usen la misma lógica de verificacion, o eliminar la verificacion duplicada.

**Pros**:
- Consistencia en reportes
- No cambia el producto

**Cons**:
- Requiere analisis profundo de ambos validadores
- Puede requerir reescribir uno de los dos

---

### Opcion D: Pipeline de Deployment (GAP-5)
**Descripcion**: Implementar flujo de deployment que suba los archivos generados al sitio real del cliente, cerrando el loop diagnostico → propuesta → implementacion.

**Pros**:
- Cierra el loop completo del servicio
- Diferenciador comercial significativo

**Cons**:
- Requiere integracion con múltiples hosting providers (WordPress, cPanel, Plesk, Managed WP)
- Alto esfuerzo de desarrollo

**Verificar**: ¿Existe skill de deployment_assistant? ¿Es reutilizable?

---

## GAP-5 — Site Verification / Deployment (Prioridad Alta)

### Estado Actual

El pipeline v4complete genera archivos en `output/v4_complete/` y empaqueta un ZIP en `deliveries/`, pero **no modifica el sitio real del cliente**:

```json
{
  "site_verification_applied": false,
  "delivery_ready_percentage": 67.0
}
```

### Evidencia (v4complete Termales, 2026-05-07)

- **Delivery ZIP**: `output/v4_complete/deliveries/termales_20260507.zip`
- **Contenido verificado**: diagnostico, propuesta, 6 assets, research data, v4_audit
- **Assets faltantes en ZIP**: `whatsapp_button/`, `open_graph/`, `optimization_guide/` — no existen en el paquete
- **Sitio real**: NO fue modificado (no hay script de deployment)

### Causa Raiz

El pipeline actual es un **generador de entregables**, no un sistema de deployment. El flujo ends en:
1. Generar documentos + assets
2. Empaquetar en ZIP
3. Entregar al cliente

No existe paso 4: **Implementar en el sitio del cliente**.

### Impacto Comercial

- El cliente recibe archivos pero no ve mejoras en su sitio web
- El "gancho comercial" (Tier C CTA pidiendo datos reales) no se traduce en implementacion
- Competidores que ofrecen deployment automatico tienen ventaja

### Opciones de Solucion

| Opcion | Descripcion | Esfuerzo |
|--------|-------------|----------|
| **D1** | Skill `deployment_assistant.md` existente — evaluar reutilizacion | Bajo |
| **D2** | WP REST API connector — subir archivos via API | Medio |
| **D3** | Delivery package con instrucciones paso-a-paso para implementacion manual | Bajo |
| **D4** | Integracion con cPanel/Plesk file manager via SSH | Alto |

### Recomendacion D

**D1+D3**: Evaluar si `deployment_assistant.md` es reutilizable para este caso. Si no, crear un "Deployment Guide" generico que accompanies el ZIP como solucion de bajo esfuerzo.

---

## Validacion del Harness (2026-05-07 12:27)

Ejecutado: `./venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co/`

### Resultados sin Errores

|| Componente | Resultado |
|-----------|-----------|
| `coherence_validation.json` | ✅ `is_coherent: true`, `score: 0.89`, errors: `[]` |
| `gate_report` | ✅ 6/8 PASSED, 2 WARNING (financial Tier C, asset_confidence) |
| `price_matches_pain` | ✅ `score: 0.8`, `passed: true` (era 0.0 pre-PATCH) |
| Pipeline exit | ✅ Exit 0, "Flujo v4.0 completado exitosamente" |
| Shadow logs | ✅ 0 errores capturados |
| Doctor --status | ✅ PASS |

### Verificacion de Assets en Delivery

```
ASSETS/analytics_setup_guide/
ASSETS/faq_page/
ASSETS/geo_enriched/
ASSETS/hotel_schema/
ASSETS/indirect_traffic_optimization/
ASSETS/llms_txt/
ASSETS/monthly_report/
ASSETS/v4_audit/
```

**3 assets NO generados** (confirmado en delivery y en gate_report):
- `whatsapp_button/`
- `open_graph/`
- `optimization_guide/`

### Conclusion

**El harness opera correctamente post-PATCH.** Los gaps restantes (G1-G5) son decisiones de producto, no bugs del sistema.

---

## Recomendacion General

**Prioridad Alta**: GAP-5 (Deployment) — el unico gap que impide cerrar el loop comercial.

**Fase 1 (Quick Win)**: Documentar GAP-5 en ROADMAP.md y crear ticket con opciones D1-D4.

**Fase 2 (Si D1)**: Evaluar `deployment_assistant.md` para复用 en contexto hotelero.

**Fase 3 (Si D2/D4)**: Crear nuevo plan `DEPLOYMENT-FLOW` con FASE-A (conector) + FASE-B (integracion) + FASE-C (testing).

**Gap G1-G4 (Discrepancia assets)**: Depende de decision comercial — reducir catalogo de servicios o invertir en generar los 3 faltantes.

---

## Archivos Relevantes

### Codigo
- `modules/commercial_documents/coherence_validator.py` — `_check_promised_assets_exist()` (lineas 494-526)
- `modules/quality_gates/publication_gates.py` — `_proposal_asset_alignment_gate()` (lineas 755-865)
- `modules/asset_generation/proposal_asset_alignment.py` — `verify_proposal_asset_alignment()`, `PROPOSAL_SERVICE_TO_ASSET` (lineas 20-27)
- `modules/commercial_documents/v4_proposal_generator.py` — `_generate_dynamic_services_table()` (lineas 839-908)
- `modules/asset_generation/asset_catalog.py` — `is_asset_implemented()`, `ASSET_CATALOG`

### Evidencia E2E
- `evidence/FASE-PATCH-C/gate_report_20260507_093317.json` — gate proposal_asset_alignment: missing_count=3
- `evidence/FASE-PATCH-C/coherence_validation.json` — coherence check: promised_assets_exist score=1.0
- `evidence/FASE-PATCH-C/02_PROPUESTA_COMERCIAL_20260507_093310.md` — propuesta solo lista 4 servicios
- `evidence/FASE-PATCH-C/asset_generation_report.json` — 6 assets generados

### Documentacion
- `docs/contributing/REGISTRY.md` — FASE-PATCH-C registrada
- `.opencode/plans/PROP-PATCH/09-documentacion-post-proyecto.md` — Nota 7 documenta la discrepancia
- `.opencode/plans/PROP-PATCH/06-checklist-implementacion.md` — PATCH-C completada

---

## Contexto Adicional

**Lecciones de PROP-PATCH** (relevantes para disenar el nuevo plan):

1. **Pain IDs vs Asset Types**: `SERVICE_CATALOG` mapea cada servicio a UN pain_id, pero `ASSET_CATALOG` usa `promised_by` con MULTIPLES pain_ids. Desacoplamiento conocido.

2. **Nombres de archivo**: Los planes referencing `proposal_generator.py` y `proposal_asset_alignment_gate.py` no coinciden con los archivos reales (`v4_proposal_generator.py`, `publication_gates.py`). Verificar con `search_files` antes de modificar.

3. **Tests no detectaron la brecha**: Los tests unitarios no捕捉 esta discrepancia. Verificación E2E con hotel real es obligatoria.

4. **Discrepancia documentada pero no resuelta**: La nota en `_proposal_asset_alignment_gate` docstring reconoce el mismatch pero no lo resuelve.

---

---

## Validacion contra Codigo Vivo (2026-05-07 12:47)

**Metodo**: Lectura directa de archivos fuente + busqueda en codebase completo.
**Skills aplicados**: `iah-cli-cross-document-audit`, `iah-cli-phase-implementation-verification`.

### Claims Verificados: 12

| # | Claim | Veredicto | Evidencia |
|---|-------|-----------|-----------|
| 1 | `coherence_validator._check_promised_assets_exist()` lineas 494-526 | ✅ CONFIRMADO | Lineas exactas, logica matchea |
| 2 | Usa `promised_types = {a.asset_type for a in assets}` + `is_asset_implemented(t)` | ✅ CONFIRMADO | Lineas 502-506 exactas |
| 3 | Retorna score=1.0 si no missing_types | ✅ CONFIRMADO | Lineas 508-515, coherence_validation.json linea 43 |
| 4 | `proposal_asset_alignment_gate` lineas 755-865 | ✅ CONFIRMADO | Corregido de 755-850 a 755-865 (SOL2-D) |
| 5 | `PROPOSAL_SERVICE_TO_ASSET` 6 entradas estaticas | ✅ CONFIRMADO | proposal_asset_alignment.py lineas 20-27 |
| 6 | `verify_proposal_asset_alignment()` existe | ✅ CONFIRMADO | Linea 129-253 |
| 7 | `_generate_dynamic_services_table()` filtra por assets_generated | ✅ CONFIRMADO | Lineas 839-908 exactas |
| 8 | ASSET_CATALOG marca 3 assets IMPLEMENTED sin generar para Termales | ✅ CONFIRMADO | optimization_guide(L184), whatsapp_button(L62), open_graph(L333) |
| 9 | Root cause: dos validadores con baselines distintas | ✅ CONFIRMADO | coherence=capability, gate=delivery |
| 10 | Gate status WARNING (no bloqueante) | ✅ CONFIRMADO | Linea 855: `passed=True  # WARNING, not blocking` |
| 11 | whatsapp_button: "always" eliminado en FASE-5 | ✅ CONFIRMADO | Linea 63: `FASE-5: "always" ELIMINADO - bug sistemico` |
| 12 | SitePresenceChecker usado por el gate para WhatsApp | ❌ FALSO | Ver GAP-A abajo |

**Resultado**: 10/12 confirmados, 1 parcial, 1 falso.

---

### Nuevos Gaps Encontrados (ampliacion del alcance)

#### GAP-A [ALTA]: SitePresenceChecker NO EXISTE en el codebase

**Hallazgo**: El documento asume que `SitePresenceChecker` opera y reporta `presence_verified: true, presence_status: "not_exists"` para WhatsApp. En realidad:

- `publication_gates.py` linea 798 intenta: `from modules.asset_generation.site_presence_checker import SitePresenceChecker`
- **Ese modulo NO EXISTE** (0 archivos encontrados en todo el codebase)
- El `try/except` en lineas 811-813 captura el ImportError silenciosamente: `site_presence_report = None`
- El gate_report JSON muestra `present_in_production: []` (vacio) a pesar de que WhatsApp tiene `presence_verified: true`

**Impacto**: El feature "check site presence for missing assets" esta **completamente deshabilitado**. El gate funciona sin el (degrada gracefully), pero pierde la capacidad de detectar assets que YA existen en el sitio del cliente. La evidencia de `presence_verified: true` para WhatsApp probablemente vino de una version anterior donde el modulo existia, o fue hardcodeada en la generacion del reporte.

**Solucion**: Crear `modules/asset_generation/site_presence_checker.py` con la clase `SitePresenceChecker` y metodo `check_site(url, asset_types)`. La infraestructura en el gate ya esta lista (lineas 793-813). Alternativamente, eliminar la referencia y simplificar el gate.

---

#### GAP-B [ALTA]: `deployment_assistant.md` NO EXISTE

**Hallazgo**: AGENTS.md (linea 52) e INDICE_DOCUMENTACION.md (linea 210) referencian `.agents/workflows/deployment_assistant.md`. El archivo **NO EXISTE** en `.agents/workflows/` (0 matches).

**Impacto directo en este documento**: La opcion D1 del documento dice:

> "Skill deployment_assistant.md existente — evaluar reutilizacion | Bajo esfuerzo"

Esto es **IMPOSIBLE**. El workflow de deployment nunca fue creado o fue eliminado sin actualizar las referencias. La opcion D1 debe descartarse o reemplazarse.

**Solucion**: Eliminar la referencia fantasma de AGENTS.md e INDICE_DOCUMENTACION.md, o crear el workflow si se decide que es necesario.

---

#### GAP-C [MEDIA]: 7mo servicio excluido del gate

**Hallazgo**: `SERVICE_CATALOG` tiene 7 entradas (6 base + 1 condicional AEO):

```python
# service_catalog.py - entrada condicional
"Optimización para IA Generativa" -> asset_type="llms_txt"
# Se agrega cuando score_aeo < 20
```

`PROPOSAL_SERVICE_TO_ASSET` (usado por el gate via `ALL_PROMISED_SERVICES`) solo tiene 6. El 7mo servicio (AEO/llms_txt) **escapa a la verificacion del gate**.

**Impacto**: Si un hotel califica para AEO y llms_txt NO se genera, el gate no lo detecta. El documento dice "4 servicios filtrados" para Termales pero no explica que el 4to (AEO condicional) no esta cubierto por el gate.

**Solucion**: Agregar `"Optimización para IA Generativa": "llms_txt"` a `PROPOSAL_SERVICE_TO_ASSET`, o hacer que el gate consulte `SERVICE_CATALOG` directamente en vez del dict estatico.

---

#### GAP-D [MEDIA → DOCUMENTADA]: Coherence score inconsistente entre fuentes

**Hallazgo**:

| Fuente | Score | Contexto |
|--------|-------|----------|
| `coherence_validation.json` | 0.89 | overall_score (promedio ponderado de 6 checks) |
| `gate_report.json` | 0.891 | coherence gate value (mismo dato, menos redondeo) |
| AGENTS.md | 0.84 | Diferente run |

**Verificacion SOL2-D (2026-05-07)**: Ambas fuentes usan el **mismo cálculo**. `publication_gates.py` extrae el score del assessment dict (que viene de `CoherenceValidator.validate()`). La diferencia 0.89 vs 0.891 es solo redondeo:
- `coherence_validation.json`: `round(overall_score, 4)` → 0.89
- `gate_report.json`: extrae el float raw → 0.891111...

**Resolución**: La fuente única de verdad es `CoherenceValidator.validate()`. AGENTS.md ya usa notación de rango (`≥0.8`). Documentado en docstrings de `publication_gates.py` (SOL2-D).

---

#### GAP-E [BAJA]: Line range del gate subestimado

**Hallazgo**: Documento dice "lineas 755-850". El metodo termina en linea 865 (el `return PublicationGateResult` del caso WARNING). Diferencia: ~15 lineas.

---

#### GAP-F [MEDIA]: `promised_by=["always"]` en monthly_report no documentado

**Hallazgo**: El documento documenta que whatsapp_button tuvo `"always"` eliminado en FASE-5 (linea 63), pero **NO menciona** que `monthly_report` **TIENE** `"always"` en `promised_by` (linea 322):

```python
promised_by=["always"]  # SIEMPRE generar - la propuesta SIEMPRE lo promete
```

**Impacto**: monthly_report se genera SIEMPRE, incluso si el hotel no tiene brechas relacionadas. Esto es intencional pero crea una cadena de causalidad no documentada:

1. `promised_by=["always"]` → se genera siempre
2. Se genera con confidence baja (0.5) porque no hay datos especificos
3. El gate `asset_confidence` lo reporta como low_quality (0.5 < 0.7)
4. El documento lo menciona como `low_quality_count: 1` pero no conecta esto con el patron `"always"`

---

#### GAP-G [ALTA → RESUELTA]: `delivery_ready_percentage` y `site_verification_applied` — campos VALIDADOS

**Hallazgo original**: El documento citaba estos campos como "no existen en codigo".

**Verificacion SOL2-D (2026-05-07)**: Ambos campos **SÍ existen** y son calculados dinámicamente en `modules/asset_generation/v4_asset_orchestrator.py` (lineas 144-145):

```python
"delivery_ready_percentage": round(delivery_ready_pct, 2),
"site_verification_applied": len(self.skipped_assets) > 0  # FASE-CAUSAL-01
```

- `delivery_ready_pct` se calcula como `(can_use_count / total_assets) * 100`
- `site_verification_applied` es `True` si hay assets skipeados

**Veredicto**: NO son campos fantasma. El GAP-G original fue un falso positivo causado por busqueda incompleta del codebase. Los campos son validos y dinamicos.

---

### Resumen de Verificacion

```
Claims del documento:      12
Confirmados:               11  (92%)
Precision parcial:           0  (corregido en SOL2-D)
Falsos/omitidos:             1  (SitePresenceChecker)

Gaps nuevos encontrados:     7  (A a G)
Severidad ALTA:              2  (SitePresenceChecker, deployment_assistant)
Severidad MEDIA:             3  (7mo servicio, coherence score, "always")
Severidad BAJA:              1  (line range - corregido en SOL2-D)
Severidad RESUELTA:          1  (GAP-G: campos fantasma eran falsos positivos)
```

### Impacto en Opciones de Solucion del Documento

| Opcion | Estado post-validacion | Observacion |
|--------|----------------------|-------------|
| **A** (generar 3 assets) | FACTIBLE | Los 3 estan IMPLEMENTED en catalogo. Verificar si `detect_pains()` detecta sus pain_ids. Si no, problema es de thresholds, no capability. |
| **B** (reducir catalogo) | FACTIBLE | Bajo esfuerzo, alto impacto comercial negativo. Evaluar con equipo. |
| **C** (unificar validacion) | FACTIBLE | Ambos validadores responden preguntas distintas (capability vs delivery). Hacer que coherence_validator tambien verifique delivery. |
| **D** (deployment) | **D1 IMPOSIBLE** | `deployment_assistant.md` NO EXISTE. D3 (package con instrucciones) es quick win. D2/D4 requieren desarrollo nuevo. |
| **E** (NUEVA: restaurar SitePresenceChecker) | FACTIBLE | Critico. El modulo fue eliminado/referenciado sin existir. Infraestructura del gate lista. |
| **F** (NUEVA: limpiar refs muertas) | FACTIBLE | Bajo esfuerzo. Eliminar refs a deployment_assistant, limpiar/crear site_presence_checker. |

### Recomendacion Actualizada

**Prioridad 1 (bloqueante)**: GAP-A + GAP-B — Componentes que el sistema asume funcionales NO EXISTEN. Antes de cualquier plan de mejora, decidir: crear los modulos faltantes O eliminar las referencias.

**Prioridad 2 (discrepancia)**: Opcion C — Unificar la validacion de coherence_validator y gate para que ambos verifiquen capability + delivery.

**Prioridad 3 (comercial)**: Opcion A o B — Decision de producto: generar los 3 assets faltantes o reducir el catalogo.

**Prioridad 4 (cierre del loop)**: Opcion D3 — Deployment guide como companion del ZIP (bajo esfuerzo, alto valor percibido).

---

*Contexto generado automaticamente por Hermes Agent durante FASE-PATCH-C*
*Para disenar nuevo plan: cargar este archivo y crear .opencode/plans/NEW-PLAN/ basandose en las opciones de solucion*

*Validacion contra codigo vivo: 2026-05-07 12:47 — 11/12 claims confirmados, 7 gaps (2 ALTA, 3 MEDIA, 1 BAJA, 1 RESUELTA). Actualizado por SOL2-D: GAP-G resuelta (falso positivo), line range corregido.*
