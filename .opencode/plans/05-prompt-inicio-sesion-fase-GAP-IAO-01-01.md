# GAP-IAO-01-01: Auditoría de Conexiones y Datos

**ID**: GAP-IAO-01-01
**Objetivo**: Mapear la realidad de datos entre auditoría → diagnóstico → propuesta → assets, identificando缺口 (gaps) de datos que causarían desconexiones
**Dependencias**: Ninguna (FASE-0 yadefine arquitectura)
**Duración estimada**: 1-2 horas
**Skill**: systematic-debugging

---

## Contexto

### Por qué esta fase es crítica

El plan GAP-IAO-01 asume que ciertos datos existen en el pipeline pero NO LOS VERIFICÓ contra el codebase real. Esta fase responde:

- ¿Qué datos REALMENTE produce la auditoría?
- ¿Qué datos necesita el diagnóstico según KB?
- ¿Qué datos recibe la propuesta?
- ¿Qué datos necesita conditional_generator?

**Sin esta validación, GAP-IAO-01-02 puede implementar código que no conecta con datos reales.**

### Lo que esta fase NO hace

No implementa nada. Solo documenta la realidad de los datos.

---

## Tareas

### Tarea 1: Mapear V4AuditResult → Elementos KB

**Archivos a investigar**:
- `modules/commercial_documents/data_structures.py` (líneas 136-207: V4AuditResult)
- `modules/auditors/v4_comprehensive.py` (cómo se construye V4AuditResult)
- `modules/auditors/pagespeed_auditor_v2.py` (datos de PageSpeed)
- `modules/auditors/ai_crawler_auditor.py` (datos de IA crawlers)

**Formato de documento**:

```markdown
## A.1: V4AuditResult — Campos existentes

| Campo en V4AuditResult | Tipo Python | ¿Existe? | Mapea a KB CHECKLIST_IAO |
|------------------------|-------------|----------|--------------------------|
| schema.hotel_schema_detected | bool | ✅ | schema_hotel |
| schema.hotel_schema_valid | bool | ✅ | (sub-elemento) |
| schema.faq_schema_detected | bool | ✅ | schema_faq |
| schema.total_schemas | int | ✅ | (conteo) |
| performance.lcp | float | ✅ | LCP_ok |
| performance.cls | float | ✅ | CLS_ok |
| performance.mobile_score | int | ✅ | (proxy) |
| gbp.place_found | bool | ✅ | (existencia) |
| gbp.rating | float | ✅ | schema_reviews (proxy) |
| gbp.reviews | int | ✅ | (proxy) |
| gbp.photos | int | ✅ | (proxy) |
| validation.whatsapp_status | str | ✅ | nap_consistente |
| validation.phone_web | str | ⚠️ | (parcial) |
| validation.phone_gbp | str | ⚠️ | (parcial) |
| ... | ... | ... | ... |
```

### Tarea 2: Verificar Elementos KB que FALTAN en V4AuditResult

**Los 12 elementos del CHECKLIST_IAO**:

| # | Elemento KB | ¿Cómo se detecta? | ¿Existe en V4AuditResult? |
|---|-------------|-------------------|---------------------------|
| 1 | ssl | ¿Campo `ssl` o `https`? | ❓ |
| 2 | schema_hotel | ✅ `schema.hotel_schema_detected` | ✅ |
| 3 | schema_reviews | ⚠️ `gbp.rating` es proxy, no Schema | ❌ No hay `has_aggregate_rating` |
| 4 | LCP_ok | ✅ `performance.lcp` | ✅ |
| 5 | CLS_ok | ✅ `performance.cls` | ✅ |
| 6 | contenido_extenso | ¿Hay campo `content_length` o similar? | ❓ |
| 7 | open_graph | ¿Hay campo `has_og_tags`? | ❌ No encontrado |
| 8 | schema_faq | ✅ `schema.faq_schema_detected` | ✅ |
| 9 | nap_consistente | ✅ `validation.whatsapp_status` | ⚠️ Solo WhatsApp |
| 10 | imagenes_alt | ¿Hay `images_without_alt`? | ❌ No encontrado |
| 11 | blog_activo | ¿Hay `has_blog`? | ❌ No encontrado |
| 12 | redes_activas | ¿Hay `social_links`? | ❌ No encontrado |

**ACCIÓN**: Documentar CADA elemento con:
- ¿Existe el dato en el audit actual?
- Si no existe, ¿de dónde debería venir?
- ¿Es bloqueante para GAP-IAO-01-02?

### Tarea 3: Mapear `_identify_brechas()` vs `PainSolutionMapper`

**Archivos**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (líneas 930-985: `_identify_brechas()`)
- `modules/commercial_documents/pain_solution_mapper.py` (líneas 52+: `PAIN_SOLUTION_MAP`)

**Comparar**:

```markdown
## A.3: Pain IDs — Consistencia entre funciones

| Problema detectado por _identify_brechas() | Pain ID | Existe en PainSolutionMapper? | Asset(s) | Consistencia |
|-------------------------------------------|---------|------------------------------|----------|--------------|
| "Visibilidad Local (Google Maps)" | (ninguno) | ❌ No existe | - | ❌ |
| "Sin Schema Hotel" | `no_hotel_schema` | ✅ | hotel_schema | ✅ |
| "WhatsApp No Configurado" | `no_whatsapp_visible` | ✅ | whatsapp_button | ✅ |
| "Web Lenta" | `low_lcp` | ❌ No existe | - | ❌ |
| "FAQPage" | `no_faq_schema` | ✅ | faq_page | ✅ |
| ... | ... | ... | ... | ... |
```

**ACCIÓN**: Documentar:
- Qué brechas de `_identify_brechas()` NO tienen Pain ID
- Qué Pain IDs de PainSolutionMapper NO se usan en `_identify_brechas()`
- ¿Son los mismos nombres? ¿Case-sensitive?

### Tarea 4: Mapear Diagnóstico → Propuesta

**Archivos**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (cómo construye DiagnosticSummary)
- `modules/commercial_documents/v4_proposal_generator.py` (qué recibe y usa)

**Preguntas**:
- ¿DiagnosticSummary tiene `score_final`, `score_tecnico`, `score_ia`?
- ¿La propuesta recibe `faltantes` como lista?
- ¿La propuesta sabe qué score mostrar?
- ¿Hay backwards compatibility si faltan campos nuevos?

```markdown
## A.4: Flujo Diagnóstico → Propuesta

| Campo en DiagnosticSummary | ¿Existe? | Usado en propuesta? | Cómo se usa |
|---------------------------|----------|---------------------|-------------|
| hotel_name | ✅ | ✅ | Encabezado |
| critical_problems_count | ✅ | ✅ | Resumen |
| quick_wins_count | ✅ | ✅ | Resumen |
| overall_confidence | ✅ | ✅ | Nivel confianza |
| coherence_score | ✅ | ✅ | Score coherencia |
| score_tecnico | ❌ | ❌ | - (no existe) |
| score_ia | ❌ | ❌ | - (no existe) |
| faltantes | ❌ | ❌ | - (no existe) |
| paquete | ❌ | ❌ | - (no existe) |
```

### Tarea 5: Mapear Propuesta → Assets

**Archivos**:
- `modules/commercial_documents/v4_proposal_generator.py` (qué pasa a assets)
- `modules/asset_generation/conditional_generator.py` (qué recibe generate())

**Preguntas**:
- ¿La propuesta llama a conditional_generator?
- ¿Le pasa `faltantes` o solo `validated_data`?
- ¿Hay mapeo de `recommendations` → `asset_type`?

### Tarea 6: Crear documento IA_MEASUREMENT_MAP.md

**Archivo de salida**: `.opencode/plans/IA_MEASUREMENT_MAP.md`

**Contenido obligatorio**:

```markdown
# IA_MEASUREMENT_MAP.md

## 1. Flujo de datos completo

```
[AUDITORÍA] 
    ↓
    V4AuditResult (datos crudos)
    ↓
[DIAGNÓSTICO]
    ↓
    DiagnosticSummary (datos procesados)
    ↓
[PROPUESTA]
    ↓
    recommendations / faltantes
    ↓
[ASSETS]
```

## 2. Elementos CHECKLIST_IAO — Estado real

| Elemento | Detectado por | Existe en audit | ¿Data real? | Bloqueante? |
|----------|--------------|-----------------|-------------|-------------|
| ssl | ? | ? | ? | ? |
| schema_hotel | Scraping | ✅ | ✅ | No |
| ... | ... | ... | ... | ... |

## 3. Gaps de datos identificados

### Gap 1: [NOMBRE]
**Descripción**: [Qué dato falta]
**Impacto**: [Cómo afecta al pipeline]
**Solución sugerida**: [Cómo resolver sin romper backwards]

### Gap 2: [NOMBRE]
...

## 4. Inconsistencias de Pain IDs

| _identify_brechas() | PainSolutionMapper | Consistencia |
|---------------------|-------------------|--------------|
| ... | ... | ... |

## 5. Recomendación de implementación

- [ ] Implementar GAP-IAO-01-02 usando AEOKPIs existente
- [ ] Para elementos KB faltantes: usar默认值 y documentar
- [ ] Normalizar Pain IDs entre funciones
- [ ] Primero implementar en auditoría, luego en diagnóstico, luego en propuesta
```

---

## Entregable

**Archivo**: `IA_MEASUREMENT_MAP.md` en `.opencode/plans/`

Este documento es la** un source of truth** para lo que realmente existe vs lo que假设 existe.

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**
   - Marcar GAP-IAO-01-01 como ✅ Completada

2. **`06-checklist-implementacion.md`**
   - Marcar fase como completada

3. **`09-documentacion-post-proyecto.md`**
   - Sección A: N/A (auditoría nomás)
   - Sección D: N/A
   - Sección E: N/A

4. **Ejecutar**:
```bash
python scripts/log_phase_completion.py \
    --fase GAP-IAO-01-01 \
    --desc "Auditoría de datos: 12 elementos KB vs realidad V4AuditResult, Pain IDs inconsistentes" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] `IA_MEASUREMENT_MAP.md` creado con TODAS las tablas
- [ ] Los 12 elementos del CHECKLIST_IAO verificados contra V4AuditResult
- [ ] Tabla de gaps: elementos que faltan vs cómo obtenerlos
- [ ] `_identify_brechas()` vs PainSolutionMapper: tabla de consistencia
- [ ] Flujo Diagnóstico → Propuesta: campos existentes vs faltantes
- [ ] Recomendación: qué resolver primero (bloqueantes vs no bloqueantes)
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- **Solo auditoría**: No implementar nada, solo documentar
- **Enfoque en datos**: No basta verificar código, hay que verificar si los datos existen
- **Ser exhaustivo**: Cada "no sé" es un gap potencial

---

## Prompt de Ejecución para Nueva Sesión

```
Actúa como auditor técnico y de datos.

OBJETIVO: Documentar la realidad del flujo de datos en el pipeline Diagnóstico → Propuesta → Assets para GAP-IAO-01.

CONTEXTO:
- FASE-0 yadefine arquitectura: usar AEOKPIs existente, no crear clases nuevas
- Los 12 elementos del KB CHECKLIST_IAO deben extraerse desde V4AuditResult
- GAP-01-01 es auditoría pura, NO implementación
- El objetivo es identificar缺口 (gaps) que causarían desconexiones

TAREAS OBLIGATORIAS:

1. MAPEAR V4AuditResult vs KB
   - Leer data_structures.py:V4AuditResult (líneas ~136-207)
   - Leer modules/auditors/v4_comprehensive.py (cómo se construye)
   - Crear tabla: campo V4AuditResult → elemento KB CHECKLIST_IAO
   - Marcar cada elemento como: ✅ Existe, ❌ No existe, ⚠️ Parcial

2. VERIFICAR LOS 12 ELEMENTOS KB
   Para cada elemento del CHECKLIST_IAO:
   - ssl: ¿existe campo ssl o https en algún auditor?
   - schema_reviews: ¿hay campo has_aggregate_rating en schema?
   - contenido_extenso: ¿hay campo content_length o similar?
   - open_graph: ¿hay campo has_og_tags?
   - nap_consistente: ¿solo WhatsApp o también dirección/email?
   - imagenes_alt: ¿hay campo images_without_alt?
   - blog_activo: ¿hay campo has_blog?
   - redes_activas: ¿hay campo social_links?
   Documentar qué elementos FALTAN y de dónde vendrían

3. COMPARAR _identify_brechas() vs PainSolutionMapper
   - Leer v4_diagnostic_generator.py:líneas 930-985 (_identify_brechas)
   - Leer pain_solution_mapper.py:PAIN_SOLUTION_MAP
   - Crear tabla de consistencia: problema → Pain ID → existe → asset
   - Identificar pain IDs huérfanos (existen en uno pero no en otro)

4. FLUJO DIAGNÓSTICO → PROPUESTA
   - Leer v4_proposal_generator.py (qué recibe en generate())
   - Verificar si DiagnosticSummary tiene campos para score_tecnico, score_ia, faltantes
   - Documentar backwards compatibility

5. CREAR IA_MEASUREMENT_MAP.md
   Documento en .opencode/plans/IA_MEASUREMENT_MAP.md con:
   - Diagrama de flujo de datos
   - Tabla completa de elementos KB vs realidad
   - Lista de gaps con solución sugerida
   - Recomendación: qué fases pueden proceder vs qué está bloqueado

OUTPUT:
- Archivo: .opencode/plans/IA_MEASUREMENT_MAP.md
- Criterio de éxito: El documento permite a GAP-01-02 saber exactamente qué datos existen y cuáles necesitan implementarse
```
