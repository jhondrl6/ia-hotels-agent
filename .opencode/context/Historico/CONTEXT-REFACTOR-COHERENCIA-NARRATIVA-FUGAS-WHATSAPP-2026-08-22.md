# CONTEXT — Refactorización de Coherencia Narrativa en Documentos Comerciales (FUGAS-WHATSAPP-2026-08-22)

> **Fecha**: 2026-08-22
> **Alcance**: Refactorización de la capa narrativa de documentos comerciales generados por `v4_diagnostic_generator.py` para eliminar incoherencias entre datos técnicos verificados y texto hardcoded en templates y métodos de generación narrativa.
> **Origen**: Anomalía detectada en output E2E de Zione (v4.72.0) — la Sección 4 del diagnóstico reporta "Fuga 1 — Contacto perdido por WhatsApp incorrecto" cuando los datos técnicos confirman WhatsApp verificado y funcional.
> **Método**: Análisis de propagación cross-documento, rastreo de causa raíz en código generador, cruce con lecciones aprendidas del plan CREDIBILIDAD-NUMERICA-2026-08-20, y **validación exhaustiva contra código vivo** (2026-08-22).
> **Versión actual del sistema**: v4.72.0
> **Estado de validación**: ✅ Todos los hallazgos confirmados factualmente contra código vivo + 4 manifestaciones adicionales identificadas

---

## Veredicto Ejecutivo

La anomalía es de **capa narrativa**, no de capa de datos. Los datos técnicos (pain_ledger, proposal_asset_matrix, v4_complete_report, delivery_quality_report) son **coherentes y correctos**: WhatsApp aparece como VERIFIED, sin pain_id asociado, y status NO_BREACH en el asset matrix.

**Validación factual (2026-08-22)**: Se validó exhaustivamente cada hallazgo contra el código vivo y el output E2E de Zione. Resultado: **3 bugs originales confirmados 100% + 4 manifestaciones adicionales** de la misma causa raíz identificadas.

El problema abarca **7 manifestaciones** de una única causa raíz (**fosilización narrativa en templates**):

1. **Template hardcoded (Sección 4)**: "LAS 3 FUGAS PRINCIPALES" con 3 fugas estáticas que siempre mencionan WhatsApp, independiente de los datos del audit.
2. **Quick Wins copy-paste bug**: `_build_quick_wins()` muestra "Corregir el número de WhatsApp en Google Maps" cuando la condición real es `not hotel_schema_detected`.
3. **Título Sección 1 genérico**: Texto hardcoded "WHATSAPP, GOOGLE MAPS E IA" y "número de WhatsApp no responde" sin corresponder a los datos.
4. **[NUEVO] Título "3" hardcoded**: Sección 4 dice "LAS 3 FUGAS" cuando el número real de fugas es dinámico (7 para Zione).
5. **[NUEVO] Sección 6 "3 fugas digitales"**: Texto hardcoded "Detecta las 3 fugas digitales" cuando el sistema detecta N.
6. **[NUEVO] Proposal plan 30 días**: `_build_30_day_plan()` hardcodea "(WhatsApp + datos para IA)" sin verificar si WhatsApp es un problema.
7. **[NUEVO] Proposal servicios adicionales**: Muestra "Botón de WhatsApp" como servicio adicional cuando no es brecha detectada.

**Impacto comercial**: Un cliente que lea el diagnóstico ve una contradicción directa: la Sección 4 dice que WhatsApp es la fuga #1, pero la Sección 2 (anexo técnico) dice "✅ WhatsApp verificado — Canal directo funcional". Esto erosiona la credibilidad del documento completo.

---

## 1. Análisis de Propagación

### 1.1 Mapa de artefactos afectados

```
                    ┌─────────────────────────┐
                    │  FUENTE DE VERDAD        │
                    │  v4_complete_report.json  │
                    │  whatsapp: VERIFIED ✅    │
                    └────────┬────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌────────────┐  ┌─────────────┐  ┌──────────────────┐
     │pain_ledger │  │proposal_    │  │delivery_quality  │
     │7 pains     │  │asset_matrix │  │_report.json      │
     │NO WhatsApp │  │NO_BREACH ✅ │  │WhatsApp present ✅│
     │✅ COHERENTE│  │✅ COHERENTE │  │✅ COHERENTE      │
     └────────────┘  └─────────────┘  └──────────────────┘
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌─────────────────┐
                    │ 02_PROPUESTA    │
                    │ WhatsApp =      │
                    │ "adicional"     │
                    │ ⚠️ INCONSISTENTE│
                    │ (no replica     │
                    │  Fuga 1)        │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ 01_DIAGNOSTICO  │
                    │ "Fuga 1 =       │
                    │  WhatsApp       │
                    │  incorrecto" ❌  │
                    │ ANOMALÍA ORIGEN │
                    └─────────────────┘
```

### 1.2 Estado por artefacto

| Artefacto | ¿Tiene anomalía? | Ubicación | Severidad |
|-----------|-----------------|-----------|-----------|
| `01_DIAGNOSTICO.md` Sección 4 (L65-77 template) | **SÍ — Origen** | Template hardcoded | Alta |
| `01_DIAGNOSTICO.md` Sección 5 (Quick Wins L81-83) | **SÍ — Replica** | Quick Win #1 incorrecto | Alta |
| `01_DIAGNOSTICO.md` Sección 8 (Quick Wins duplicado L187-189) | **SÍ — Re-replica** | Mismo contenido duplicado | Alta |
| `01_DIAGNOSTICO.md` Sección 1 (L29, L37, L39) | **Parcial** | Título y nota introductoria mencionan WhatsApp genérico | Media |
| `02_PROPUESTA_COMERCIAL.md` | **Parcial** | L60: WhatsApp como "servicio adicional"; L203: mezcla WhatsApp con Hotel Schema | Media |
| `deliveries/` (ZIP interno) | **NO** | Datos técnicos coherentes | — |
| `pain_ledger.json` | **NO** | Sin pain_id de WhatsApp | — |
| `proposal_asset_matrix.json` | **NO** | `whatsapp_button: NO_BREACH` | — |
| `v4_complete_report.json` | **NO** | `whatsapp_status: VERIFIED` | — |
| `01_DIAGNOSTICO.md` Sección 4 título (L65 template) | **SÍ — [NUEVO]** | "LAS 3 FUGAS" con número hardcoded | Media |
| `01_DIAGNOSTICO.md` Sección 6 (L89 template) | **SÍ — [NUEVO]** | "Detecta las 3 fugas digitales" hardcoded | Media |
| `02_PROPUESTA` plan 30 días (L2195 generator) | **SÍ — [NUEVO]** | "(WhatsApp + datos para IA)" hardcoded | Media |
| `02_PROPUESTA` servicios adicionales (L1455 generator) | **Parcial — [NUEVO]** | WhatsApp como "adicional" cuando no es brecha | Baja |

---

## 2. Causas Raíz Identificadas

### Bug 1: Sección 4 hardcoded en template

**Archivo**: `modules/commercial_documents/templates/diagnostico_v6_template.md` (líneas 65-77)

```markdown
## 4. 🔍 LAS 3 FUGAS PRINCIPALES

De las ${brechas_total_count} brechas técnicas detectadas, estas ${brechas_destacadas_count} son las que más dinero le están costando HOY.
Las otras ${brechas_restantes_count} se resuelven en el plan completo de la Fase 2.

### Fuga 1 — Contacto perdido por WhatsApp incorrecto
Cuando un huésped quiere reservar directo, busca el WhatsApp del hotel. Si el número en Google Maps es diferente al de su web, pierde la reserva.

### Fuga 2 — Visibilidad insuficiente en Google Maps
Cuando alguien busca "hotel boutique cerca de ${hotel_landmark}", su hotel aparece más abajo que la competencia. Pocos llegan a su web.

### Fuga 3 — Las IA no recomiendan su hotel
Cuando alguien le pregunta a ChatGPT o Google AI "hotel boutique en ${hotel_region}", si su web no tiene los datos correctos, no aparece en la respuesta.
```

**Problema**: Las 3 fugas son texto estático. Solo `${brechas_total_count}`, `${brechas_destacadas_count}`, `${brechas_restantes_count}`, `${hotel_landmark}` y `${hotel_region}` son variables. El contenido de cada fuga NO se deriva de las brechas detectadas.

**Consumidor**: `v4_diagnostic_generator.py` línea 499 carga el template y línea 749 lo renderiza con `string.Template.substitute()`.

### Bug 2: Quick Win #1 con texto incorrecto (copy-paste)

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py` (líneas 1883-1888)

```python
if audit_result.schema and not audit_result.schema.hotel_schema_detected:
    wins.append(
        f"{win_number}. **HOY (5 minutos): Corregir el número de WhatsApp en Google Maps.** "
        f"→ Usted mismo puede hacerlo desde su celular."
    )
    win_number += 1
```

**Problema**: La condición es `not hotel_schema_detected` (no se detectó Schema Hotel), pero el texto dice "Corregir el número de WhatsApp en Google Maps". El texto no corresponde a la condición que lo dispara.

**Evidencia de que es copy-paste**: El Quick Win #1 original debería decir algo como "Instalar los datos estructurados de su hotel en Google" para corresponder a la condición `hotel_schema_detected`.

### Bug 3 (cosmético, seguimiento de V6): Título Sección 1 genérico

**Archivo**: `modules/commercial_documents/templates/diagnostico_v6_template.md` (líneas 29, 37, 39)

- Línea 29: `## 1. 🚨 HOY HAY RESERVAS ESCAPÁNDOSE POR WHATSAPP, GOOGLE MAPS E IA` — menciona WhatsApp como si siempre fuera un canal de fuga.
- Línea 37: `${whatsapp_conflict_business_note}` — esta variable SÍ es dinámica (el método `_build_whatsapp_conflict_note` retorna "" si no hay conflicto). Correcto.
- Línea 39: Texto hardcoded "...o el número de WhatsApp no responde" — asume problema de WhatsApp genérico.

**Nota**: El método `_build_whatsapp_conflict_note()` (líneas 2635-2675) es correcto: solo retorna contenido cuando hay un conflicto real de WhatsApp (números diferentes entre web y GBP). Pero el texto hardcoded de la línea 39 no se condiciona a esta verificación.

### Bug 4 [NUEVO]: Título "LAS 3 FUGAS PRINCIPALES" con número hardcoded

**Archivo**: `modules/commercial_documents/templates/diagnostico_v6_template.md` (línea 65)

```markdown
## 4. 🔍 LAS 3 FUGAS PRINCIPALES
```

**Problema**: El título hardcodea "3" cuando el sistema detecta N brechas dinámicamente (7 para Zione). Los contadores en L67-68 son dinámicos y correctos ("estas 7 son...", "Las otras 0..."), pero el título permanece fijo en "3", creando contradicción interna.

**Evidencia en output Zione**: El título dice "LAS **3** FUGAS PRINCIPALES" pero los contadores dicen "De las **7** brechas técnicas detectadas, estas **7** son las que más dinero le están costando HOY."

### Bug 5 [NUEVO]: "Detecta las 3 fugas digitales" en Sección 6

**Archivo**: `modules/commercial_documents/templates/diagnostico_v6_template.md` (línea 89)

```markdown
IA Hoteles Agent es el sistema que acaba de analizar su hotel. Detecta las 3 fugas digitales, calcula la fuga financiera aproximada y genera un plan de recuperación personalizado.
```

**Problema**: Hardcoded "3 fugas digitales" cuando el sistema detecta N fugas dinámicamente. Debería usar `${brechas_total_count}` o un contador dinámico.

### Bug 6 [NUEVO]: "(WhatsApp + datos para IA)" en plan de 30 días

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py` (línea 2195)

```python
items.append(f"- [ ] **Semana 2**: Implementación Fase 1 (WhatsApp + datos para IA): {', '.join(asset_names)}")
```

**Problema**: La mención "(WhatsApp + datos para IA)" está hardcoded en el método `_build_30_day_plan()`. Cuando WhatsApp NO es un problema detectado (como Zione), esta mención es incorrecta y confusa para el cliente.

**Evidencia en output Zione** ([02_PROPUESTA L203](file:///c:/Users/Jhond/Github/iah-cli/output/v4_complete/02_PROPUESTA_COMERCIAL_20260821_175706.md)):
> "Semana 2: Implementación Fase 1 (WhatsApp + datos para IA): Hotel Schema"

### Bug 7 [NUEVO]: "Servicios adicionales disponibles: Botón de WhatsApp"

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py` (líneas 1455-1457)

```python
if excluded_services:
    excluded_names = ", ".join(excluded_services)
    rows.append(f"\n> **Servicios adicionales disponibles:** {excluded_names}")
```

**Problema**: Cuando `whatsapp_button` no tiene asset generado ni está en producción, se agrega a `excluded_services` y se muestra como "Servicios adicionales disponibles". Para Zione ([output L60](file:///c:/Users/Jhond/Github/iah-cli/output/v4_complete/02_PROPUESTA_COMERCIAL_20260821_175706.md)): "Servicios adicionales disponibles: Botón de WhatsApp, Schema Organization". Técnicamente correcto (el botón existe en el sitio), pero narrativamente confuso cuando el diagnóstico dice "Fuga 1 = WhatsApp incorrecto".

**Nota**: Se resuelve automáticamente al corregir Bug 1 (si el diagnóstico ya no menciona WhatsApp como fuga, la propuesta no contradice).

### Causa Raíz Unificada: Fosilización Narrativa en Templates

El template `diagnostico_v6_template.md` fue diseñado como prototipo estático con un caso de ejemplo específico (hotel con conflicto de WhatsApp). La capa de datos fue evolucionando hacia un modelo completamente dinámico (`PainSolutionMapper.detect_pains()` → `_identify_brechas()` → `_get_brecha_pesos()` → `brechas_section`), pero **la capa narrativa del template nunca fue refactorizada** para consumir esos datos dinámicos.

**Tabla de manifestaciones** (7 bugs, 1 causa raíz):

| Bug | Manifestación | Ubicación | Tipo |
|-----|--------------|-----------|------|
| B1 | 3 fugas hardcoded (WhatsApp, Maps, IA) | Template L70-77 | Texto estático |
| B2 | Quick Win "WhatsApp" para condición Schema | Generator L1885 | Copy-paste |
| B3 | Título "WHATSAPP..." + "no responde" | Template L29, L39 | Texto estático |
| B4 | "LAS 3 FUGAS" número fijo | Template L65 | Contador hardcoded |
| B5 | "3 fugas digitales" | Template L89 | Contador hardcoded |
| B6 | "(WhatsApp + datos para IA)" | Proposal Generator L2195 | Texto estático |
| B7 | WhatsApp como "adicional" | Proposal Generator L1455 | Narrativa inconsistente |

**Patrón arquitectónico roto**: El sistema tiene una **fuente de verdad limpia** (`pain_ledger` → `brechas_pesos`) pero el template tiene **texto estático que la ignora**, creando una doble narrativa: los datos dicen X, el texto dice Y.

---

## 3. Lecciones Aprendidas Aplicables (de CREDIBILIDAD-NUMERICA-2026-08-20)

| Lección | ID original | Aplicación en esta refactorización |
|---------|-------------|-------------------------------------|
| Tras parametrizar constantes, verificar TAMBIÉN los strings de display/basis que citan el valor, no solo la lógica de cálculo | L30 | Tras hacer dinámica la Sección 4, verificar que los Quick Wins, el título de Sección 1 y cualquier narrativa que mencione WhatsApp sean coherentes con los datos |
| Docs comerciales SIEMPRE deben citar la fuente de verdad en vez de hardcodear valores | L27 | Las fugas narrativas deben derivarse del pain_ledger (fuente de verdad de brechas), no de texto estático en templates |
| Nunca declarar bug sin leer el archivo completo | CONTEXT §1.3 | Antes de modificar el template, verificar todas las secciones que mencionan WhatsApp para no dejar residuos |
| Para nuevos estados de verdad, preferir extensión de taxonomía + whitelist sobre lógica paralela | L21 | Si se agrega condición para mostrar/ocultar "Fuga WhatsApp", extender la lógica existente de `_build_whatsapp_conflict_note` en vez de crear un nuevo mecanismo |
| Antes de modificar un constructor/consumidor, verificar si el parámetro ya existe y el gap está en el caller | L16 | Antes de agregar variables nuevas al template, verificar si las variables existentes (`brechas_section`, `brechas_destacadas_count`) ya pueden alimentar una sección dinámica |
| Al agregar un gate/feature nuevo, verificar con grep que no queden referencias residuales | L2 | Tras refactor de la Sección 4, grep global por "Fuga 1", "WhatsApp incorrecto", "Contacto perdido" para confirmar 0 residuos |
| Tests de contrato deben comparar contra fuente dinámica, no valores fijos | L3 | Los tests de coherencia narrativa deben verificar que las fugas mencionadas correspondan a pain_ids reales del audit, no hardcodear expectativas de texto |
| Para contratos de código transversales, usar AST en vez de regex/grep | L7 | Considerar un test estático que verifique que todo texto hardcoded en templates que mencione un canal (WhatsApp, Maps, IA) tenga una condición de activación |

---

## 4. Propuesta de Corrección

### 4.1 Fix Bug 1: Sección 4 dinámica

**Objetivo**: Que las "Fugas Principales" se generen a partir de las brechas reales detectadas (pain_ledger), no de texto hardcoded.

**Enfoque propuesto**:
1. Crear nuevo método `_build_fugas_principales_section(audit_result, brechas)` en `v4_diagnostic_generator.py`.
2. El método selecciona las top-N brechas por impacto económico (ya calculado en `brechas_pesos`) y genera narrativa coherente con cada pain_id.
3. Mapeo pain_id → narrativa de fuga (tabla de correspondencia):

| pain_id | Narrativa de fuga |
|---------|-------------------|
| `no_hotel_schema` | "Datos del hotel invisibles para Google e IA" |
| `low_seo_score` | "Visibilidad insuficiente en Google Maps" |
| `no_faq_schema` | "Preguntas frecuentes no aparecen en búsquedas" |
| `no_analytics_configured` | "Sin medición de tráfico — decisiones a ciegas" |
| `low_organic_visibility` | "Tráfico orgánico no medido ni optimizado" |
| `ai_crawler_blocked` | "Las IA no recomiendan su hotel" |
| `no_og_tags` | "Compartir en redes sociales sin presentación" |
| `whatsapp_conflict` (si existiera) | "Contacto perdido por WhatsApp incorrecto" |

4. Reemplazar líneas 65-77 del template con `${fugas_principales_section}`.
5. Si NO hay conflicto de WhatsApp real, la fuga de WhatsApp NO aparece.

**Variable a inyectar en template** (dict de renderizado, ~línea 920):
```python
'fugas_principales_section': self._build_fugas_principales_section(audit_result, brechas_pesos),
```

### 4.2 Fix Bug 2: Quick Win #1 texto correcto

**Archivo**: `v4_diagnostic_generator.py` línea 1885

**Cambio**:
```python
# Antes (incorrecto):
"Corregir el número de WhatsApp en Google Maps."

# Después (correcto — corresponde a not hotel_schema_detected):
"Instalar los datos de su hotel en Google (Schema markup). → Nosotros nos encargamos en 24h."
```

**Verificación**: Grep posterior por "Corregir el número de WhatsApp" en `modules/` debe retornar 0 resultados (a menos que haya un conflicto real de WhatsApp detectado).

### 4.3 Fix Bug 3 (cosmético): Título Sección 1 condicional

**Opción A (mínima)**: Reemplazar "WHATSAPP, GOOGLE MAPS E IA" por "GOOGLE MAPS, REDES E IA" en el template hardcoded. El `${whatsapp_conflict_business_note}` dinámico ya maneja el caso WhatsApp cuando aplica.

**Opción B (completa)**: Convertir el título de Sección 1 en variable dinámica `${seccion_1_titulo}` con lógica:
- Si hay conflicto WhatsApp: "HOY HAY RESERVAS ESCAPÁNDOSE POR WHATSAPP, GOOGLE MAPS E IA"
- Si no hay conflicto: "HOY HAY RESERVAS ESCAPÁNDOSE POR GOOGLE MAPS E IA"

Análogo para el texto de línea 39.

### 4.4 Limpieza de `02_PROPUESTA_COMERCIAL.md`

**Línea 203**: `"Semana 2: Implementación Fase 1 (WhatsApp + datos para IA): Hotel Schema"` — la mención "(WhatsApp + datos para IA)" es confusa cuando WhatsApp no es un problema detectado. Corregir a:
```
"Semana 2: Implementación Fase 1 (datos para IA): Hotel Schema"
```

**Verificación**: El template de propuesta (`propuesta_v6_template.md`) NO contiene esta referencia — el texto se genera en código (`_build_30_day_plan`). Corregir directamente en `v4_proposal_generator.py`.

### 4.5 Fix Bug 4+5: Contadores dinámicos en template

**Archivo**: `diagnostico_v6_template.md`

**Cambios**:
- L65: Reemplazar `## 4. 🔍 LAS 3 FUGAS PRINCIPALES` por `## 4. 🔍 LAS ${fugas_count_display} FUGAS PRINCIPALES`
- L89: Reemplazar "Detecta las 3 fugas digitales" por "Detecta las ${brechas_total_count} fugas digitales"

**Variable a inyectar** (dict de renderizado, ~línea 920):
```python
'fugas_count_display': str(min(3, len(brechas_pesos))),  # top-N mostradas en título
```

### 4.6 Fix Bug 6: Plan 30 días condicional

**Archivo**: `v4_proposal_generator.py` línea 2195

**Cambio**:
```python
# Antes (hardcoded):
items.append(f"- [ ] **Semana 2**: Implementación Fase 1 (WhatsApp + datos para IA): {', '.join(asset_names)}")

# Después (condicional):
whatsapp_mention = "WhatsApp + " if whatsapp_conflict else ""
items.append(f"- [ ] **Semana 2**: Implementación Fase 1 ({whatsapp_mention}datos para IA): {', '.join(asset_names)}")
```

**Nota**: El parámetro `whatsapp_conflict` ya se extrae en L792-798 del mismo generador pero NO se pasa a `_build_30_day_plan`. Se debe agregar como parámetro.

### 4.7 Fix Bug 7: Narrativa de servicios adicionales

**Opción A (mínima)**: No requerido — se resuelve indirectamente al corregir Bug 1 (el diagnóstico ya no menciona WhatsApp como fuga, eliminando la contradicción).

**Opción B (robusta)**: Cuando `whatsapp_button` está en `excluded_services` Y `whatsapp_conflict=False`, reemplazar texto por "Ya presente en su sitio" en vez de "Servicios adicionales disponibles".

---

## 5. Archivos Involucrados

### 5.1 Archivos a modificar (código)

| Archivo | Cambio | Complejidad |
|---------|--------|-------------|
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Reemplazar Sección 4 hardcoded por variable dinámica; opcionalmente Sección 1 | Baja |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Nuevo método `_build_fugas_principales_section`; fix `_build_quick_wins` L1885; inyectar variable en dict de renderizado | Media |
| `modules/commercial_documents/v4_proposal_generator.py` | Fix `_build_30_day_plan` L2195 (WhatsApp condicional); opcional fix servicios adicionales | Media |

### 5.2 Archivos a verificar (solo lectura, grep de residuos)

| Archivo | Qué buscar |
|---------|------------|
| Todo `modules/commercial_documents/` | "Fuga 1", "Contacto perdido", "WhatsApp incorrecto" |
| Todo `modules/asset_generation/` | Referencias a WhatsApp como fuga sin condición |
| `templates/` | Templates legacy que puedan contener texto similar |

### 5.3 Tests a crear/modificar

| Test | Propósito | Tipo |
|------|-----------|------|
| `test_fugas_principales_sin_whatsapp_conflict` | Verificar que las fugas NO mencionan WhatsApp cuando `whatsapp_status=VERIFIED` | Nuevo |
| `test_fugas_principales_con_whatsapp_conflict` | Verificar que las fugas SÍ mencionan WhatsApp cuando hay conflicto real | Nuevo |
| `test_quick_wins_schema_text` | Verificar que Quick Win para `not hotel_schema_detected` menciona Schema, no WhatsApp | Nuevo |
| `test_template_no_hardcoded_fugas` | Test estático (AST o regex) que verifique ausencia de texto hardcoded de fugas en el template | Nuevo |
| `test_fugas_count_matches_brechas` | Verificar que el número en el título coincide con `len(brechas_pesos)` | Nuevo |
| `test_proposal_plan_sin_whatsapp` | Verificar que plan 30 días NO menciona WhatsApp cuando `whatsapp_conflict=False` | Nuevo |
| Tests existentes de `v4_diagnostic_generator` | Verificar que no se rompan por el cambio de template variable | Modificar si es necesario |

---

## 6. Restricciones y Guardas

### 6.1 No-regresión de gates

- El cambio es puramente narrativo. NO debe afectar:
  - Publication gates (13 gates, todos deben seguir PASSED)
  - Coherence score (debe mantenerse ≥ 0.8)
  - Pain ledger (no se altera la detección de pains)
  - Proposal asset matrix (no se altera la alineación)

### 6.2 Compatibilidad backwards

- El template `diagnostico_v6_template.md` es la plantilla oficial desde v4.72.0.
- Si se reemplaza `${brechas_destacadas_count}` y `${brechas_restantes_count}` por una sección dinámica, estos variables pueden mantenerse como fallback o eliminarse con deprecación explícita.
- Outputs históricos en `output/` y `evidence/` NO se modifican (son registro de lo que el sistema produjo en su momento).

### 6.3 Coherencia con FASE-P1-D (VERIFIED_IN_SITE)

- La FASE-P1-D del plan CREDIBILIDAD-NUMERICA implementó el filtrado de brechas verificadas en sitio vivo (D8). El nuevo método `_build_fugas_principales_section` debe respetar este filtrado: si una brecha tiene status `VERIFIED_IN_SITE` en el pain_ledger, NO debe aparecer como fuga.
- El filtrado ya existe en `_get_brechas()` (línea 3043: `pains = [p for p in pains if p.id not in verified_ids]`). El nuevo método debe consumir la lista YA filtrada.

### 6.4 Principio de fuente única

- Las fugas narrativas deben derivarse del pain_ledger (fuente de verdad), no de lógica independiente. Esto es análogo a la decisión D6 (pricing.yaml como fuente única de pricing).

---

## 7. Plan de Ejecución Sugerido

| Fase | Contenido | Estimación |
|------|-----------|------------|
| **FASE-R0-A** | Fix Bug 2 (Quick Wins texto): cambio de 1 línea en `_build_quick_wins`. Test nuevo. Grep de residuos. | ~10 min |
| **FASE-R0-B** | Fix Bug 1 (Sección 4 dinámica): crear `_build_fugas_principales_section`, reemplazar template, inyectar variable. Tests nuevos (con/sin conflicto WhatsApp). | ~30 min |
| **FASE-R0-C** | Fix Bug 3 (Sección 1 condicional): evaluar Opción A vs B. Implementar. Test nuevo. | ~15 min |
| **FASE-R0-D** | Limpieza propuesta comercial: fix Bug 6 (plan 30 días WhatsApp condicional en `v4_proposal_generator.py` L2195) + fix Bug 4+5 (contadores dinámicos en template L65, L89). | ~20 min |
| **FASE-R0-E** | E2E: regenerar output Zione con `python main.py v4complete --url https://zione.co/` y verificar coherencia cross-documento. | ~5 min + tiempo de corrida |
| **FASE-R0-F** | Documentación: CHANGELOG, GUIA_TECNICA nota técnica, VERSION si aplica. | ~15 min |

---

## 8. Criterios de Aceptación

| # | Criterio | Verificación |
|---|----------|--------------|
| AC1 | `01_DIAGNOSTICO.md` NO menciona "Fuga 1 — Contacto perdido por WhatsApp incorrecto" cuando `whatsapp_status=VERIFIED` | Grep + lectura del output |
| AC2 | Quick Win #1 menciona Schema markup (no WhatsApp) cuando la condición es `not hotel_schema_detected` | Lectura del output + test unitario |
| AC3 | Las fugas listadas en Sección 4 corresponden 1:1 con pain_ids del pain_ledger (sin inventos) | Test de integración |
| AC4 | Si hay conflicto real de WhatsApp (phone_web ≠ phone_gbp), la fuga de WhatsApp SÍ aparece | Test con datos simulados de conflicto |
| AC5 | 0 regresiones en gates de publicación (13/13 PASSED) | `run_all_validations.py --quick` |
| AC6 | Coherence score ≥ 0.8 | Gate report del E2E |
| AC7 | Grep "WhatsApp incorrecto" en `modules/` retorna 0 resultados | Grep global |
| AC8 | Pain_ledger no alterado (mismos 7 pain_ids para Zione) | Comparación JSON pre/post |
| AC9 | Título Sección 4 muestra número dinámico coincidente con `len(brechas_pesos)` | Lectura del output |
| AC10 | Sección 6 muestra "Detecta las N fugas" con N = brechas reales | Lectura del output |
| AC11 | Plan 30 días NO menciona WhatsApp cuando `whatsapp_conflict=False` | Grep + lectura del output propuesta |
| AC12 | Grep "Corregir el número de WhatsApp" en `modules/` retorna 0 resultados | Grep global |

---

## 9. Datos de Contexto del Sistema

| Métrica | Valor |
|---------|-------|
| Versión actual | v4.72.0 |
| Tests totales | 3,360 funciones / 261 archivos |
| Gates de publicación | 13 (12 PASSED + 1 WARNING pricing_compliance) |
| Coherence score Zione | 0.9485 |
| Pain IDs detectados Zione | 7 (schema, seo, faq, analytics, visibility, crawlers, og) |
| WhatsApp status Zione | VERIFIED (+573103724544) |
| Template activo | `diagnostico_v6_template.md` (234 líneas) |
| Generador diagnóstico | `v4_diagnostic_generator.py` (3,544 líneas) |
| Generador propuesta | `v4_proposal_generator.py` (2,411 líneas) |
| Bugs documentados originalmente | 2 (+ 1 cosmético) |
| Bugs confirmados tras validación factual | 3 confirmados + 4 adicionales = **7 total** |
| Tests existentes afectados | `tests/commercial_documents/test_diagnostic_generator.py` (D8 tests) |
| Tests existentes NO afectados | `tests/test_top_problems_consistency.py` (usa `calculate_quick_wins`, función distinta) |

---

## 10. Referencias Cruzadas

| Documento | Relación |
|-----------|----------|
| `CREDIBILIDAD-NUMERICA-2026-08-20/10-analisis-post-implementacion.md` | Lecciones aprendidas L1-L32 aplicadas |
| `CONTEXT-VALIDACION-COMERCIAL-CODIGO-VIVO-2026-08-19.md` | Contexto original de fallos F1-F10 |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Template a refactorizar |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Generador a modificar |
| `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260821_175706.md` | Output con anomalía (evidencia) |
| `output/v4_complete/02_PROPUESTA_COMERCIAL_20260821_175706.md` | Output con propagación parcial |
| `output/v4_complete/v4_complete_report.json` | Fuente de verdad (whatsapp: VERIFIED) |
| `modules/commercial_documents/v4_proposal_generator.py` | Generador de propuesta a modificar (Bug 6, Bug 7) |

---

## 11. Resultados de Validación Factual (2026-08-22)

### 11.1 Resumen de validación cruzada

| Categoría | Resultado |
|-----------|----------|
| Bugs del documento original confirmados | **3/3 (100%)** |
| Bugs nuevos identificados | **4** (B4-B7) |
| Capa de datos (pain_ledger, asset_matrix, report) | **100% coherente** |
| Anomalía de capa narrativa | **Confirmada con evidencia en output** |
| Causa raíz | **Fosilización Narrativa**: template estático que ignora datos dinámicos |
| Archivos a modificar | 2 código (.py) + 1 template (.md) = **3 total** |
| Tests nuevos necesarios | **6 mínimo** |
| Riesgo de regresión | **Bajo** — cambio puramente narrativo, sin tocar lógica de datos ni gates |

### 11.2 Evidencia factual por bug

| Bug | Archivo verificado | Línea(s) | Output verificado | Veredicto |
|-----|-------------------|----------|-------------------|----------|
| B1 | `diagnostico_v6_template.md` | L70-77 | 01_DIAGNOSTICO L110-117 | ✅ CONFIRMADO |
| B2 | `v4_diagnostic_generator.py` | L1883-1888 | 01_DIAGNOSTICO L123, L260 | ✅ CONFIRMADO |
| B3 | `diagnostico_v6_template.md` | L29, L39 | 01_DIAGNOSTICO L29, L39 | ✅ CONFIRMADO |
| B4 | `diagnostico_v6_template.md` | L65 | 01_DIAGNOSTICO L105 ("3" vs "7") | ✅ CONFIRMADO |
| B5 | `diagnostico_v6_template.md` | L89 | 01_DIAGNOSTICO L130 | ✅ CONFIRMADO |
| B6 | `v4_proposal_generator.py` | L2195 | 02_PROPUESTA L203 | ✅ CONFIRMADO |
| B7 | `v4_proposal_generator.py` | L1455-1457 | 02_PROPUESTA L60 | ✅ CONFIRMADO (parcial — auto-resuelto con B1) |

### 11.3 Verificación de datos técnicos (capa de verdad)

| Dato verificado | Fuente | Valor | Estado |
|-----------------|--------|-------|-------|
| `whatsapp_status` | `v4_complete_report.json` L13 | `"VERIFIED"` | ✅ Correcto |
| WhatsApp en pain_ledger | `detect_pains()` output | Sin pain_id WhatsApp | ✅ Correcto |
| WhatsApp en asset_matrix | `proposal_asset_matrix` | `NO_BREACH` | ✅ Correcto |
| Contadores brechas | `_get_brecha_pesos()` | 7 brechas para Zione | ✅ Correcto |
| Filtro VERIFIED_IN_SITE | `_identify_brechas()` L3043 | Activo y funcional | ✅ Correcto |
| `_build_whatsapp_conflict_note` | L2635-2675 | Retorna "" sin conflicto | ✅ Correcto |

### 11.4 Conclusión

El documento de contexto original es **factualmente correcto en sus hallazgos centrales** pero **incompleto en su alcance**: dejaba fuera 4 manifestaciones adicionales de la misma causa raíz (fosilización narrativa). La solución propuesta (sección 4) es adecuada en dirección pero debía ampliarse para cubrir:
- `_build_30_day_plan` en `v4_proposal_generator.py` (Bug 6)
- Contadores hardcoded "3" en Secciones 4 y 6 del template (Bugs 4+5)
- Narrativa de servicios adicionales en proposal (Bug 7, auto-resuelto con B1)

La implementación puede proceder con confianza: todos los supuestos del documento han sido verificados contra código vivo.
