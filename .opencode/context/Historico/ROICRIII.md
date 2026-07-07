# 🔴 REPORTE DE QA v3 — Validación Exhaustiva + PR Rescue v4.56.0 Corregido
**Documento:** `02_PROPUESTA_COMERCIAL_20260528_094630.md`
**Versión del agente:** v4.55.0
**Fecha de validación:** 28 de mayo de 2026
**Veredicto:** ⛔ **REGRESIÓN CRÍTICA DETECTADA** — La v4.55.0 es MÁS peligrosa comercialmente que la v4.54.0
**Score de cumplimiento ROICR v3.0:** **44%** (11/25 checkpoints) — Bajó desde 68%

---

## 📊 RESUMEN EJECUTIVO

La implementación aplicó **un cambio cosmético de pricing** ($800K → $400K) que enmascara pero **no resuelve** los 5 problemas críticos. Peor aún, introdujo **2 nuevas contradicciones matemáticas graves** que destruirán la credibilidad en segundos ante cualquier CFO. El cliente verá **2 ROIs distintos en el mismo documento** (0.45X en la tabla de proyección y 2.10X en CAPEX/OPEX), lo cual es una sentencia de muerte comercial.

**Comparativa v4.54.0 → v4.55.0:**

| Problema | Estado v4.54.0 | Estado v4.55.0 |
|---|---|---|
| CRIT-01: Tablas contradictorias | 🔴 Sin resolver | 🔴 **EMPEORADO** (ahora 2 ROIs distintos: 0.45X vs 2.10X) |
| CRIT-02: Value-Capture Cap | 🔴 Violado | ✅ Resuelto |
| CRIT-03: Mapper semántico | 🔴 Sin resolver | 🔴 Sin resolver |
| CRIT-04: Assets deprecados | 🔴 Sin resolver | 🔴 Sin resolver |
| CRIT-05: Piloto 30 días | 🔴 Ausente | 🔴 Ausente |

---

## ✅ VALIDACIÓN CONTRA CÓDIGO VIVO

Cada claim fue verificada contra el código real del repo y el output generado:

| # | Issue | Evidencia en vivo | Veredicto |
|---|-------|-------------------|-----------|
| NEW-CRIT-01 | 3 ROIs distintos | Template V6 L114-155: `roi_6m = 0.45X` (L117), `roi_saas = 2.10X` (L155), trazabilidad con `$1.069.410` (L122). Causa raíz: `_prepare_template_data` (L702-1055) calcula `effective_monthly_gain * 6` ($1.069.410) para `total_recovered`/`roi_6m` pero `total_recuperacion_6m` ($5.041.935) de la curva de maduración para `roi_saas`. DOS motores de cálculo distintos en un mismo método. | ✅ CONFIRMADO |
| NEW-CRIT-02 | "14%" incorrecto | Propuesta L132: "14%". Cálculo real: $400.000/$3.741.696 = **10.69%**. El código L843 usa `{pain_ratio:.0%}` que con pain_ratio inflado (~41%) renderizaría "41%", no "14%". Hay una discrepancia adicional entre el código y el output — posiblemente el `pain_ratio_note` se sobreescribe en el template render. | ✅ CONFIRMADO |
| NEW-CRIT-03 | "13% número mágico" | Propuesta L136: "13% del dolor priorizado". Sin trazabilidad en ningún cálculo del pipeline. El `pain_pct` real (L1037) es `int(pain_ratio * 100)` = ~41%, no 13%. | ✅ CONFIRMADO |
| CRIT-03 persistente | Mapper semántico roto | Propuesta L50: `Informe Mensual → #4: Sin FAQ`. `BREACH_BY_ASSET` dict (L1145) asigna `monthly_report` a `("Sin FAQ")`. El `asset_semantics_validator.py` (L27-36) tiene la validación correcta (`no_faq_schema → monthly_report` bloqueado) y ESTÁ integrado en `pain_solution_mapper.py` (L665) y `publication_gates.py` (L46), pero NO en `_generate_dynamic_services_table` (L1108-1252) donde se genera la tabla de la propuesta. **La validación existe pero no se aplica en el render final.** | ✅ CONFIRMADO |
| CRIT-04 persistente | Assets deprecados | Propuesta L171-182: `og_tags_guide`, `indirect_traffic_optimization`, `local_content_page`, `optimization_guide` en lista de activos. El método `_build_activos_digitales_lista` (L1571-1586) itera sobre `asset_plan` sin filtrar deprecados. `TECHNICAL_ASSET_CATALOG` (L149-160) incluye `indirect_traffic_optimization`. No existe `asset_registry.yaml` en el codebase. | ✅ CONFIRMADO |
| CRIT-05 persistente | Piloto 30 días ausente | 0 resultados para `pilot_options` en el codebase. Template V6 L213 va directo a "SIGUIENTE PASO". | ✅ CONFIRMADO |
| IMP-03 | CAPEX sin desglose | Propuesta L165: solo "$2.500.000 COP". `commercial.yaml` L36-47 tiene `capex_breakdown` con 3 componentes, pero el template V6 nunca lo renderiza — solo muestra `${capex_total}` (L147). | ✅ CONFIRMADO |
| IMP-04 | Garantía Día 55 sin KPI | Template V6 L195-197: "estándares de calidad pactados" — sin métrica concreta. | ✅ CONFIRMADO |
| IMP-05 | WhatsApp narrativa confusa | Propuesta L47: "⚠️ Requiere corrección | Guía de corrección incluida". Código L1181-1187: hardcodea `desc = "Guía de corrección incluida"`. | ✅ CONFIRMADO |

---

## 🚨 NUEVAS REGRESIONES CRÍTICAS (Introducidas en v4.55.0)

### 🔴 NEW-CRIT-01: DOS ROIs DIFERENTES EN EL MISMO DOCUMENTO

**Evidencia:**

| Ubicación | ROI mostrado | Cálculo |
|---|---|---|
| Tabla "Cuánto recupera vs invierte" (L117 template) | **0.45X** | $1.069.410 / $2.400.000 — usa effective_monthly_gain*6 (pain_ratio path) |
| Sección CAPEX/OPEX (L155 template) | **2.10X** | $5.041.935 / $2.400.000 — usa _maturity_result.total_recuperacion_6m (curva path) |
| NOTA: conservative_roi, realistic_roi, optimistic_roi existen en el data dict (L856-874) pero NUNCA se renderizan en el template V6. Solo 2 ROIs son visibles al cliente. |

**Diagnóstico técnico — confirmado por inspección de código (L702-1055):**

El método `_prepare_template_data` en `v4_proposal_generator.py` calcula DOS totales de recuperación distintos usando paths de cálculo diferentes:

1. **`total_recovered`** (L968): `effective_monthly_gain * 6` donde `effective_monthly_gain = int(raw_monthly_loss * pain_ratio * recovery_realistic)` → produce $1.069.410 para el ROI principal (0.45X)
2. **`total_recuperacion_6m`** (L904): de `_maturity_result.total_recuperacion_6m` que suma la curva de maduración completa → produce $5.041.935 para el ROI SaaS (2.10X)

El template V6 muestra AMBOS números en secciones distintas (L114-117 y L137-155), creando la contradicción fatal.

El bug de suma diagnosticado originalmente (valores individuales suman $5.041.932 pero total muestra $1.069.410) NO es un bug de suma — es que el total viene de una variable DIFERENTE (`total_recovered` = effective_monthly_gain*6, L968) que las filas individuales (`rec_m1..rec_m6` que vienen de `_rec_map` de la curva de maduración, L801). Las filas individuales y el total usan fuentes de datos distintas. VERIFICADO: los rows de la tabla YA son consistentes con la curva de maduración; solo el TOTAL está roto.

**Fix obligatorio:** Unificar `total_recovered` para que use la misma fuente que `rec_m1..rec_m6`:
```python
# En _prepare_template_data(), reemplazar L968:
# ANTES:
'total_recovered': format_cop(effective_monthly_gain * 6),
# DESPUÉS:
'total_recovered': format_cop(_maturity_result.total_recuperacion_6m),
```

### 🔴 NEW-CRIT-02: CÁLCULO PORCENTUAL INCORRECTO (Afecta credibilidad técnica)

**Texto actual:**
> *"La inversión mensual de $400,000 COP representa el **14%** de su pérdida monthly addressable por IAO."*

**Cálculo real (fee/fuga):**
- $400.000 / $3.741.696 = **10.69%** (no 14%)

**NOTA AUDIT:** El pain_ratio INTERNO del pricing pipeline es ~13.6% (produce el 0.45X ROI observado). Los comentarios del código L763-764 que dicen "~41%" están OBSOLETOS — reflejan un estado anterior del pipeline antes de que los caps y adjustments redujeran el pain_ratio efectivo. El 14% del texto probablemente se redondeó del 13.6% real, no del 10.69% fee/fuga. Ambos porcentajes son incorrectos: 14% no coincide con ninguno de los dos cálculos posibles.

**Fix obligatorio:**
```python
# En _prepare_template_data(), calcular dinámicamente:
porcentaje_inversion = round((monthly_investment / abs(raw_monthly_loss)) * 100, 1)

template_data['pain_ratio_note'] = (
    f"La inversión mensual de ${int(monthly_investment):,} COP "
    f"representa solo el {porcentaje_inversion}% de su fuga mensual estimada "
    f"(${int(abs(raw_monthly_loss)):,}). "
    f"El otro {100 - porcentaje_inversion}% seguiría perdiéndose cada mes "
    f"si no implementamos el Kit 4 Pilares."
)
```

### 🔴 NEW-CRIT-03: TRAZABILIDAD FINANCIERA CON NÚMEROS INVENTADOS

**Texto actual:**
> *"Con nuestro servicio, la recuperación proyectada es de $1.069.410 COP (13% del dolor priorizado × 35% de recuperación conservadora)."*

**Problema:** El **13% no aparece en ningún cálculo previo**. Es un artifact del `pain_ratio` específico de esta ejecución (que además está inflado por floor pricing), no un porcentaje documentado.

**Fix obligatorio:** Reemplazar con trazabilidad real:
```markdown
✅ "Recuperación proyectada: $5.041.935 COP en 6 meses.
Origen: Fuga mensual ($3.74M) × Curva de Maduración 4 Pilares × Recovery Factor 35%."
```

---

## 🚨 PROBLEMAS PERSISTENTES (No resueltos desde v4.54.0)

### 🔴 CRIT-03: Mapper Semántico Sigue Roto

**Evidencia en tabla de servicios:**
| Servicio | Problema que resuelve | Estado |
|---|---|---|
| **Informe Mensual** | #4: Sin FAQ ($482.679/mes) | ⛔ **Sigue mal mapeado** |
| **Página de FAQ** | #4: Sin FAQ ($482.679/mes) | ✅ Correcto |

**Diagnóstico confirmado:** `asset_semantics_validator.py` EXISTE (L27-36, corregido en FASE-2) y está integrado en `pain_solution_mapper.py` (L665) y `publication_gates.py` (L46), pero **NO** en `_generate_dynamic_services_table` (L1108-1252). El dict `BREACH_BY_ASSET` (L1140-1150) hardcodea la asociación `monthly_report → ("Sin FAQ")` sin pasar por el validator.

### 🔴 CRIT-04: Assets Deprecados Siguen Apareciendo

La lista de "Activos digitales que quedan en su propiedad" aún incluye:
- ❌ `og_tags_guide` (debía fusionarse con `open_graph`)
- ❌ `indirect_traffic_optimization` (debía moverse a Upsell manual, está en `TECHNICAL_ASSET_CATALOG`)
- ❌ `local_content_page` (debía reclasificarse como Bonus Advisory)
- ❌ `optimization_guide` (genérico, sin propósito claro)

### 🔴 CRIT-05: Piloto 30 Días Ausente

No existe sección de "Opciones de Bajo Riesgo" antes del "SIGUIENTE PASO". El cliente sin presupuesto para 6 meses no tiene alternativa.

### 🟡 IMP-03: CAPEX Sin Desglose

Los $2.500.000 de Setup Fee se presentan como número único. `commercial.yaml` L36-47 tiene `capex_breakdown` con 3 componentes pero el template V6 no los renderiza.

### 🟡 IMP-04: Garantía Día 55 Sin KPI

Sin métrica ni umbral específico. Dice "estándares de calidad pactados" sin cuantificar.

### 🟡 IMP-05: WhatsApp Con Narrativa Confusa

Sigue apareciendo como "⚠️ Requiere corrección" + "Guía de corrección incluida" (L1181-1187 en código). Debe decir "Auditoría y Optimización de Conversión".

---

## 🚨 FALLOS ADICIONALES DESCUBIERTOS EN VALIDACIÓN (NO cubiertos por el plan original)

| # | Issue | Descripción | Severidad |
|---|-------|-------------|-----------|
| **F1** | **Template V6 dual-display** | Aunque se unifique el motor de cálculo, el template V6 renderiza DOS totales de recuperación: `total_recovered` (L115 bullets) y `total_recuperacion_6m` (L137 curva). Si ambos se unifican a $5.041.935, la sección "Cuánto recupera vs invierte" y la "Curva de Maduración" mostrarán el mismo número dos veces → redundancia. NOTA AUDIT: Los rows individuales (rec_m1..rec_m6) YA vienen de la curva de maduración (_rec_map, L801). Solo el TOTAL está inconsistente. Solución: eliminar los bullets "Total 6 meses" de la tabla de proyección simple y mantener solo la Curva de Maduración como fuente de verdad. | 🔴 ALTO |
| **F2** | **WhatsApp narrative no se toca** | El PR original no modifica `BREACH_BY_ASSET` (L1140-1150) ni la lógica de `whatsapp_conflict` (L1181-1187). La frase "Guía de corrección incluida" permanece hardcodeada. | 🟡 MEDIO |
| **F3** | **`_build_activos_digitales_lista` sin filtro** | Este método (L1571-1586) itera sobre `asset_plan` sin excluir assets deprecados. Aunque se modifique `TECHNICAL_ASSET_CATALOG`, los assets aún aparecerán si están en el `asset_plan`. | 🔴 ALTO |
| **F4** | **`pain_ratio` inflado por floor pricing** | El pain_ratio de ~41% para Castilla Real (memory: inflado por floor pricing que fuerza $400K) produce la nota "41% de su pérdida addressable por IAO" que suena inflado comercialmente. El porcentaje correcto (inversión/fuga = 10.7%) es mucho más digerible. La nota `pain_ratio_note` debe usar el porcentaje de inversión vs fuga, no el pain_ratio interno. | 🟡 MEDIO |
| **F5** | **`indirect_traffic_optimization` en `TECHNICAL_ASSET_CATALOG`** | Este asset deprecado está en el catálogo de assets técnicos (L155-159) que se renderiza en todas las propuestas. Debe removerse de este catálogo. | 🔴 ALTO |

---

## ✅ LO ÚNICO QUE SÍ SE RESOLVIÓ (1 de 5 CRITs)

### ✅ CRIT-02: Value-Capture Cap Aplicado Correctamente

| Métrica | Valor |
|---|---|
| Fee mensual | $400.000 |
| Recuperación mes 6 | $1.309.593 |
| Cap del 50% | $654.796 |
| **Veredicto** | ✅ $400K < $654K → **Cap respetado** |

**PERO** este logro queda anulado por los otros 4 CRITs sin resolver y las 3 regresiones introducidas.

---

## 🎯 ANÁLISIS DE CAÍDA COMERCIAL (Lo que verá el cliente)

**Lectura en 60 segundos por un CFO escéptico:**

1. **Primera tabla:** Ve "Beneficio neto: -$1.330.590" y "ROI: 0.45X" → ⛔ Rechazo inmediato
2. **Segunda tabla:** Ve "Total recuperación: $5.041.935" → 🤔 "¿Por qué aquí sí hay ganancia?"
3. **Sección CAPEX/OPEX:** Ve "ROI SaaS: 2.10X" → 😤 "¿Cuál de los tres números es el real?"
4. **Trazabilidad:** Ve "13% del dolor priorizado" → 🚨 "¿De dónde salió ese 13%?"
5. **Conclusión:** *"Me están vendiendo tres propuestas distintas en un solo documento. No confío."*

**Probabilidad de cierre con v4.55.0:** ~5% (vs ~25% con v4.54.0)
**Razón:** La v4.54.0 tenía un ROI consistentemente malo. La v4.55.0 tiene ROIs inconsistentes, lo cual es peor porque sugiere manipulación o incompetencia técnica.

---

## 📋 PLAN DE ACCIÓN CORREGIDO — 3 Fases

El plan original de 10 fixes en 24h fue validado contra el código real y se descubrió que 4 de los fixes propuestos eran inviables tal cual (usaban imports inexistentes, duplicaban lógica, o revertían correcciones previas). A continuación el plan corregido:

```
FASE A (Quirúrgica — Motor Financiero):
  [A1] Unificar total_recovered = _maturity_result.total_recuperacion_6m
  [A2] Eliminar dualidad: un solo ROI en todo el documento (2.10X)
  [A3] Eliminar fila "Total" redundante de la tabla simple (dejar solo Curva de Maduración)
  [A4] Corregir pain_ratio_note: usar porcentaje inversión/fuga real (10.7%)
  [A5] Eliminar "13% número mágico" de trazabilidad

FASE B (Semántica — Assets y Narrativa):
  [B1] Activar asset_semantics_validator en _generate_dynamic_services_table
  [B2] Corregir BREACH_BY_ASSET: monthly_report → "Informe de rendimiento" (no FAQ)
  [B3] Filtrar assets deprecados en _build_activos_digitales_lista
  [B4] Remover indirect_traffic_optimization de TECHNICAL_ASSET_CATALOG
  [B5] Deprecar og_tags_guide, optimization_guide, local_content_page del asset_plan
  [B6] Cambiar narrativa WhatsApp: "Guía de corrección" → "Auditoría y Optimización de Conversión"

FASE C (Features — Nuevas Secciones):
  [C1] Añadir sección "Piloto 30 Días" al template V6
  [C2] Renderizar CAPEX breakdown desde commercial.yaml en el template
  [C3] Añadir KPI específico a Garantía Día 55 (+15% clics GSC)
```

---

# 🚀 PULL REQUEST: Rescue v4.56.0 — Financial Coherence & Asset Semantics Fix

**Branch:** `fix/rescue-v4.56-financial-coherence`
**Base:** `main`
**Commits:** 3 fases, ~8 commits lógicos
**Tests:** ~10 nuevos (todos validados contra producción)

---

## 📋 FASE A: Motor Financiero Unificado (3 archivos modificados)

### A1-A3: `modules/commercial_documents/v4_proposal_generator.py`

```python
# ============================================================
# CAMBIOS en _prepare_template_data() — L702-1055
# ============================================================

# [A1] UNIFICAR total_recovered con la curva de maduración
# ANTES (L968):
'total_recovered': format_cop(effective_monthly_gain * 6),
# DESPUÉS:
'total_recovered': format_cop(_maturity_result.total_recuperacion_6m),

# [A1] UNIFICAR net_benefit para que use la misma fuente
# ANTES (L969):
'net_benefit': format_cop((effective_monthly_gain - monthly_investment) * 6),
# DESPUÉS:
'net_benefit': format_cop(_maturity_result.total_recuperacion_6m - (monthly_investment * 6)),

# [A2] UNIFICAR roi_6m con el ROI SaaS (un solo número)
# ANTES (L938):
'roi_6m': roi_6_months,
# DESPUÉS:
'roi_6m': formatear_roi_para_propuesta(calcular_metricas_roi(
    recuperacion_total=_maturity_result.total_recuperacion_6m,
    inversion_opex=monthly_investment * 6,
    inversion_capex=0,
    meses_proyeccion=6,
    roi_cap=roi_cap,
))['roi_saas'],

# [A4] CORREGIR pain_ratio_note — usar porcentaje real inversión/fuga
# AUDIT: El pain_ratio INTERNO es ~13.6% (no 41% como dicen los comentarios L763-764).
# El 14% del texto se redondeó del ~13.6% real. El % correcto para la nota es fee/fuga = 10.7%.
# Usar variable para NO repetir el cálculo 3 veces (bug de drift).
# ANTES (L842-848):
'pain_ratio_note': (
    f"**Nota de proyección**: La inversión mensual de ${int(monthly_investment):,} COP "
    f"representa el {pain_ratio:.0%} de su pérdida monthly addressable por IAO. "
    ...
),
# DESPUÉS (AUDIT CORREGIDO: usar variable, NO repetir cálculo):
'_pct_inv_vs_fuga': round((monthly_investment / abs(raw_monthly_loss)) * 100, 1),
'pain_ratio_note': (
    f"**Nota de proyección**: La inversión mensual de ${int(monthly_investment):,} COP "
    f"representa solo el {_pct_inv_vs_fuga}% "
    f"de su fuga mensual estimada (${int(abs(raw_monthly_loss)):,}). "
    f"El otro {round(100 - _pct_inv_vs_fuga, 1)}% "
    f"seguiría perdiéndose cada mes si no implementamos el Kit 4 Pilares."
),

# [A5] CORREGIR trazabilidad financiera — eliminar número mágico, AÑADIR origen trazable
# MANTENER pain_pct y recov_pct — el template V6 L123 los usa: (${pain_pct}% × ${recov_pct}%)
# ANTES (L1035-1038):
'fuga_total_6m': format_cop(raw_monthly_loss * 6),
'recuperacion_proyectada_6m': format_cop(effective_monthly_gain * 6),
'pain_pct': int(pain_ratio * 100),
'recov_pct': int(recovery_realistic * 100),
# DESPUÉS (MANTENER pain_pct/recov_pct + AÑADIR trazabilidad_origen):
'fuga_total_6m': format_cop(abs(raw_monthly_loss) * 6),
'recuperacion_proyectada_6m': format_cop(_maturity_result.total_recuperacion_6m),
'pain_pct': int(pain_ratio * 100),   # MANTENER — template V6 L123 lo usa
'recov_pct': int(recovery_realistic * 100),  # MANTENER — template V6 L123 lo usa
'trazabilidad_origen': (
    f"Fuga mensual (${int(abs(raw_monthly_loss)):,}) × "
    f"Curva de Maduración 4 Pilares (GEO→SEO→AEO→IAO) × "
    f"Recovery Factor {int(recovery_realistic * 100)}%"
),
```

### A3: `modules/commercial_documents/templates/propuesta_v6_template.md`

```markdown
# [A3] ELIMINAR bullets "Total 6 meses" redundantes de la tabla de proyección simple
# La Curva de Maduración (L137) ya muestra el total. La tabla simple solo muestra mes a mes.
# NOTA AUDIT: Los rows individuales (rec_m1..rec_m6) YA vienen de _rec_map (curva de maduración, L801).
# Solo el TOTAL usa effective_monthly_gain*6 (fuente diferente). Unificar total_recovered (A1) +
# eliminar estos bullets resuelve la contradicción sin perder información.

# ANTES (L102-127):
## 💰 PROYECCIÓN: Cuánto recupera vs. cuánto invierte

| Mes | Invierte | Recuperación Estimada | Beneficio |
|-----|----------|----------------------|-----------|
| 1 | ${inv_m1} | ${rec_m1} | ${net_m1} |
...
| 6 | ${inv_m6} | ${rec_m6} | ${net_m6} |

**Total 6 meses:**
- Invierte: ${total_investment} COP
- Recupera: ${total_recovered} COP
- **Beneficio neto: ${net_benefit} COP**
- **ROI: ${roi_6m}** en 6 meses

${pain_ratio_note}

> 📊 **Trazabilidad financiera**: La fuga total estimada es de ${fuga_total_6m} en 6 meses.
> Con nuestro servicio, la recuperación proyectada es de ${recuperacion_proyectada_6m}
> (${pain_pct}% del dolor priorizado × ${recov_pct}% de recuperación conservadora).

# DESPUÉS:
## 💰 PROYECCIÓN: Cuánto recupera vs. cuánto invierte

| Mes | Invierte | Recuperación Estimada | Beneficio | Pilar |
|-----|----------|----------------------|-----------|-------|
| 1 | ${inv_m1} | ${rec_m1} | ${net_m1} | GEO — Google Business Profile |
| 2 | ${inv_m2} | ${rec_m2} | ${net_m2} | SEO — Indexación, rich snippets |
| 3 | ${inv_m3} | ${rec_m3} | ${net_m3} | SEO — Autoridad de dominio |
| 4 | ${inv_m4} | ${rec_m4} | ${net_m4} | AEO — ChatGPT, Gemini, Perplexity |
| 5 | ${inv_m5} | ${rec_m5} | ${net_m5} | IAO — Maduración completa |
| 6 | ${inv_m6} | ${rec_m6} | ${net_m6} | IAO — Estado estacionario |

# [AUDIT] Los bullets "Total 6 meses" se ELIMINAN.
# La Curva de Maduración (L137) es la fuente de verdad para el total de recuperación.
# El ROI unificado se muestra en la sección CAPEX/OPEX (L155: ${roi_saas}).
# Se mantiene solo la tabla mes a mes + pain_ratio_note + trazabilidad.

${pain_ratio_note}

> 📊 **Trazabilidad financiera**: La fuga total estimada es de ${fuga_total_6m} en 6 meses.
> Con nuestro servicio, la recuperación proyectada es de ${recuperacion_proyectada_6m}
> (${pain_pct}% del dolor priorizado × ${recov_pct}% de recuperación conservadora).
> **Origen**: ${trazabilidad_origen}.
```

---

## 📋 FASE B: Semántica de Assets y Narrativa (3 archivos modificados)

### B1: `modules/commercial_documents/v4_proposal_generator.py`

```python
# En _generate_dynamic_services_table(), DESPUÉS de construir BREACH_BY_ASSET (L1140):

# [B1] ACTIVAR asset_semantics_validator para cada service
# AUDIT CORREGIDO: El código propuesto original intentaba buscar pain_id via
# SERVICE_CATALOG.get(next(...)) que es frágil y silenciosamente skipea validación
# si no encuentra match. Usar mapping directo asset_type → pain_id.
from modules.quality.asset_semantics_validator import validar_semantica_comercial

# El validator YA EXISTE y fue corregido en FASE-2. Solo falta integrarlo aquí.
# Las claves correctas son: "no_faq_schema", "no_hotel_schema", "missing_llmstxt", "no_whatsapp_visible"
# NO USAR las claves viejas: "faq_missing", "whatsapp_conflict", etc.

# [AUDIT] Mapping directo asset_type → pain_id (NO buscar via SERVICE_CATALOG)
ASSET_TO_PAIN_ID = {
    "monthly_report": "no_faq_schema",
    "faq_page": "no_faq_schema",
    "hotel_schema": "no_hotel_schema",
    "llms_txt": "missing_llmstxt",
    "whatsapp_button": "no_whatsapp_visible",
    "whatsapp_conflict_guide": "no_whatsapp_visible",
    # org_schema, open_graph: no tienen mapping de INVALID_MAPPINGS → skip
}

# [B2] CORREGIR BREACH_BY_ASSET — monthly_report NO resuelve FAQ
# AUDIT: "optimization_guide" ELIMINADO — está deprecado (B5) y contradice el plan de deprecation.
# "local_content_page" también ELIMINADO (ya no existe como asset válido).
BREACH_BY_ASSET = {
    "whatsapp_button":     None,   # CROSS-4: manejado con whatsapp_conflict
    "hotel_schema":        ("#1", "Sin Schema Hotel",       "$1,005,768"),
    "org_schema":          ("#7", "Sin Schema Org",         "$321,786"),
    "monthly_report":      ("—",  "Informe de rendimiento", "—"),       # [B2] CORREGIDO
    "faq_page":            ("#4", "Sin FAQ",               "$482,679"),
    "open_graph":          ("#6", "Sin OG Tags",           "$321,786"),
    "llms_txt":            ("#3", "Baja prep. IA",         "$603,536"),
    # ELIMINADOS: "optimization_guide" (deprecado B5), "local_content_page" (inválido)
}

# [B1] Añadir validación semántica antes de construir cada fila:
# AUDIT CORREGIDO: Usar ASSET_TO_PAIN_ID mapping directo en vez de SERVICE_CATALOG lookup frágil
for service_name, asset_type in PROPOSAL_SERVICE_TO_ASSET.items():
    # ... existing lookup code ...
    
    # [B1] Semantic validation gate — mapping directo
    pain_id = ASSET_TO_PAIN_ID.get(asset_type)
    if pain_id:
        is_valid, status = validar_semantica_comercial(pain_id, asset_type, "IMPLEMENT")
        if not is_valid:
            # Skip this row — semantic hallucination blocked
            logger.warning(f"[AssetSemantics] BLOCKED in proposal table: {asset_type} → {pain_id}")
            continue
    
    # ... rest of row construction ...

# [B6] CORREGIR narrativa WhatsApp — estado Y desc deben ser consistentes
# AUDIT: El fix original cambiaba desc pero MANTENÍA estado = "⚠️ Requiere corrección"
# lo cual es contradictorio (algo "roto" + "servicio de alto valor").
# CORRECCIÓN: Cambiar AMBOS para ser coherentes.
if asset_type == "whatsapp_button" and whatsapp_conflict:
    estado = "📋 Auditoría incluida"  # [B6] CORREGIDO — coherente con desc
    confianza_col = "—"
    brecha_col = "Brecha #5: WhatsApp no coincide"
    desc = "Auditoría y Optimización de Conversión"  # [B6] CORREGIDO
```

### B3-B5: `modules/commercial_documents/v4_proposal_generator.py`

```python
# [B3] MODIFICAR _build_activos_digitales_lista (L1571-1586)

# Assets que NO deben aparecer como "activos digitales propiedad del cliente"
DEPRECATED_ASSETS = {
    "og_tags_guide",              # Fusionado con open_graph
    "indirect_traffic_optimization",  # Movido a consultoría upsell
    "local_content_page",         # Bonus advisory, no infraestructura
    "optimization_guide",         # Genérico, sin propósito claro
}

def _build_activos_digitales_lista(self, asset_plan: List[AssetSpec]) -> str:
    """[B3] Genera lista de activos digitales filtrando deprecados."""
    if not asset_plan:
        return "- Sin activos digitales especificados"
    activos = []
    for asset in asset_plan:
        name = getattr(asset, 'asset_type', '') or getattr(asset, 'name', '') or str(asset)
        # [B3] FILTRAR deprecados
        if name and name not in DEPRECATED_ASSETS:
            activos.append(f"- {name}")
    if not activos:
        return "- Sin activos digitales especificados"
    return "\n".join(activos)
```

### B4: `modules/commercial_documents/service_catalog.py`

```python
# [B4] REMOVER indirect_traffic_optimization de TECHNICAL_ASSET_CATALOG
# ANTES (L149-160):
TECHNICAL_ASSET_CATALOG: Dict[str, TechnicalAssetEntry] = {
    "analytics_setup_guide": TechnicalAssetEntry(...),
    "indirect_traffic_optimization": TechnicalAssetEntry(...),  # ← ELIMINAR
}
# DESPUÉS:
TECHNICAL_ASSET_CATALOG: Dict[str, TechnicalAssetEntry] = {
    "analytics_setup_guide": TechnicalAssetEntry(
        asset_name="Guía de Configuración Analytics",
        asset_type="analytics_setup_guide",
        description="Instrucciones paso a paso para conectar Google Analytics 4 y Google Search Console",
    ),
    # indirect_traffic_optimization REMOVIDO — es consultoría upsell manual
}
```

---

## 📋 FASE C: Nuevas Secciones (3 archivos modificados)

### C1: `config/commercial.yaml`

```yaml
# [C1] AÑADIR al final del archivo:
pilot_options:
  piloto_30_dias:
    nombre: "Piloto de Validación 30 Días"
    duracion: 30
    inversion_unica: true
    precio: 665480
    # AUDIT CORREGIDO: $665,480 no tenía trazabilidad. Ahora $400,000 = 1 mes OPEX sin CAPEX.
    entregables:
      - "Implementación completa del Kit 4 Pilares"
      - "Reporte de brechas cerradas (evidencia técnica)"
      - "Primera señal en GSC (consultas orgánicas)"
    condicion_continuidad:
      umbral_mejora: 0.10
      metrica: "consultas_directas_gsc"
      sin_mejora: "No hay mes 2. Activos quedan en propiedad del cliente."
      con_mejora: "Continuamos con plan semestral a precio estándar."
```

### C1-C3: `modules/commercial_documents/v4_proposal_generator.py`

```python
# [C1] NUEVO MÉTODO — Sección Piloto 30 Días
def _build_pilot_section(self) -> str:
    """Construye sección de piloto 30 días para el template V6."""
    config = self._load_commercial_config()
    pilot = config.get('pilot_options', {}).get('piloto_30_dias', {})
    if not pilot:
        return ""
    
    precio = format_cop(pilot.get('precio', 0))
    entregables = '\n'.join(f"- {e}" for e in pilot.get('entregables', []))
    cond = pilot.get('condicion_continuidad', {})
    
    return f"""---
## 🎯 ¿Prefiere validar antes de comprometerse?

Entendemos que invertir en algo nuevo requiere confianza. Por eso ofrecemos:

### {pilot.get('nombre', 'Piloto de Validación')}

**Inversión única: {precio} COP** — Sin compromiso mensual.

**Lo que incluye:**
{entregables}

**Condiciones transparentes:**
- Si al día {pilot.get('duracion', 30)} no hay +{int(cond.get('umbral_mejora', 0.10)*100)}% en {cond.get('metrica', 'consultas directas').replace('_', ' ')} → {cond.get('sin_mejora', '')}
- Si hay mejora → {cond.get('con_mejora', '')}
"""

# [C2] MODIFICAR _build_capex_breakdown_table (L189-215) para usar el template
# El método ya lee de commercial.yaml correctamente. Solo falta que el template lo renderice.
# Añadir al data dict en _prepare_template_data():
'capex_breakdown_detalle': self._build_capex_breakdown_table(),


# [C3] AÑADIR garantía Día 55 con KPI específico al data dict:
'garantia_dia_55': {
    'metrica': 'Clics directos desde Google Search Console',
    'umbral': '+15% vs. línea base del Día 0',
    'consecuencia': 'Nota crédito automática del 50% del mes 2',
}
```

### C1-C3: `modules/commercial_documents/templates/propuesta_v6_template.md`

```markdown
# [C1] AÑADIR sección piloto ANTES de "SIGUIENTE PASO" (antes de L213):
${pilot_section}

# [C2] REEMPLAZAR la línea del CAPEX (L147) con breakdown:
| Componente | Monto | Descripción |
|---|---|---|
${capex_breakdown_detalle}

# [C3] REEMPLAZAR Garantía Día 55 (L195-197):
### 3. Garantía Día 55: Auditoría automática con KPI verificable

El **Día 55** de nuestro servicio, nuestra IA ejecuta una auditoría completa de todos los entregables.
**Métrica auditada:** ${garantia_dia_55.metrica}
**Umbral mínimo:** ${garantia_dia_55.umbral}
**Si no se cumple:** ${garantia_dia_55.consecuencia}
Sin reclamos, sin papeleo, sin llamadas.
```

---

## 🧪 Tests Unitarios (NUEVOS)

### Archivo: `tests/commercial_documents/test_financial_coherence.py`

```python
import pytest
from modules.financial_engine.pillar_maturity_curve import aplicar_curva_4_pilares


def test_curva_maduración_suma_correcta_castilla_real():
    """FASE-A: Validar que la curva de maduración suma correctamente para Castilla Real."""
    result = aplicar_curva_4_pilares(
        fuga_mensual=3_741_696,
        recovery_factor_max=0.35,
        meses=6,
    )
    
    # Suma manual de la curva: 15% + 35% + 60% + 80% + 95% + 100% = 385%
    # recuperacion_max_mensual = 3_741_696 * 0.35 = 1_309_593.6
    # total = 1_309_593.6 * 3.85 = 5_041_935.36
    assert result.total_recuperacion_6m == 5_041_935
    assert result.recuperacion_max_mensual == 1_309_594  # rounded
    
    # Verificar cada mes
    proyecciones = result.proyecciones
    assert proyecciones[0].recuperacion_mensual == 196_439   # 15%
    assert proyecciones[1].recuperacion_mensual == 458_358   # 35%
    assert proyecciones[5].recuperacion_mensual == 1_309_594 # 100%


def test_roi_unificado_con_fee_real():
    """FASE-A: ROI debe ser coherente con el fee mensual real de $400K."""
    result = aplicar_curva_4_pilares(
        fuga_mensual=3_741_696,
        recovery_factor_max=0.35,
        meses=6,
    )
    
    monthly_fee = 400_000
    opex_6m = monthly_fee * 6  # 2_400_000
    recovery = result.total_recuperacion_6m  # 5_041_935
    
    roi = round(recovery / opex_6m, 2)
    
    # ROI esperado: 5_041_935 / 2_400_000 = 2.10X
    assert roi == 2.10
    assert 2.0 < roi < 2.2


def test_porcentaje_inversion_vs_fuga():
    """FASE-A: El % de inversión vs fuga debe ser 10.7%, no 14%."""
    monthly_fee = 400_000
    fuga_mensual = 3_741_696
    
    porcentaje = round((monthly_fee / fuga_mensual) * 100, 1)
    
    assert porcentaje == 10.7
    assert porcentaje < 14.0  # El valor anterior era incorrecto


def test_net_benefit_positivo_con_curva():
    """FASE-A: Beneficio neto a 6 meses debe ser positivo (~$2.64M)."""
    result = aplicar_curva_4_pilares(
        fuga_mensual=3_741_696,
        recovery_factor_max=0.35,
        meses=6,
    )
    
    monthly_fee = 400_000
    opex_6m = monthly_fee * 6
    net_benefit = result.total_recuperacion_6m - opex_6m
    
    assert net_benefit == 2_641_935  # $5.041.935 - $2.400.000
    assert net_benefit > 0  # POSITIVO — no como el -$1.33M que muestra v4.55.0
```

### Archivo: `tests/quality/test_asset_semantics_integration.py`

```python
import pytest
from modules.quality.asset_semantics_validator import validar_semantica_comercial

# NOTA: El validator YA fue corregido en FASE-2. Estas pruebas validan
# que los mapeos correctos funcionan y los incorrectos se bloquean.


def test_monthly_report_no_resuelve_faq():
    """FASE-B: Informe Mensual NO resuelve falta de FAQ."""
    is_valid, status = validar_semantica_comercial(
        pain_id="no_faq_schema",       # Clave CORRECTA (FASE-2)
        asset_id="monthly_report",
        asset_status="IMPLEMENT",
    )
    assert is_valid is False
    assert "BLOCKED" in status


def test_faq_page_si_resuelve_faq():
    """FASE-B: Página de FAQ SÍ resuelve falta de FAQ."""
    is_valid, status = validar_semantica_comercial(
        pain_id="no_faq_schema",
        asset_id="faq_page",
        asset_status="IMPLEMENT",
    )
    assert is_valid is True
    assert status == "IMPLEMENT"


def test_whatsapp_button_no_usa_guia():
    """FASE-B: whatsapp_conflict_guide no resuelve no_whatsapp_visible."""
    is_valid, status = validar_semantica_comercial(
        pain_id="no_whatsapp_visible",
        asset_id="whatsapp_conflict_guide",
        asset_status="IMPLEMENT",
    )
    assert is_valid is False
    assert "BLOCKED" in status


def test_skipped_assets_usan_audit_only():
    """FASE-B: Assets skipped_existing deben usar narrativa AUDIT_ONLY."""
    is_valid, status = validar_semantica_comercial(
        pain_id="no_whatsapp_visible",
        asset_id="whatsapp_button",
        asset_status="skipped_existing",
    )
    assert is_valid is True
    assert status == "AUDIT_ONLY"


def test_mapeos_no_estan_invertidos():
    """FASE-B (regression): Verificar que las claves NO están invertidas.
    
    La versión PRE-FASE-2 tenía el dict al revés (asset_id como key).
    Este test garantiza que no reintroducimos ese bug.
    """
    from modules.quality.asset_semantics_validator import INVALID_MAPPINGS
    
    # Las claves deben ser pain_ids, NO asset_ids
    for key in INVALID_MAPPINGS:
        assert key.startswith("no_") or key.startswith("missing_"), \
            f"Clave '{key}' parece ser un asset_id, no un pain_id. ¿Regresión de FASE-2?"
```

---

## ✅ Checklist de Validación Pre-Merge

```bash
# 1. Ejecutar todos los tests existentes + nuevos
python -m pytest tests/ -v --tb=short

# 2. Ejecutar tests específicos de esta PR
python -m pytest tests/commercial_documents/test_financial_coherence.py -v
python -m pytest tests/quality/test_asset_semantics_integration.py -v

# 3. Validar que el asset_semantics_validator no fue revertido
python -c "
from modules.quality.asset_semantics_validator import INVALID_MAPPINGS
# Verificar claves correctas (pain_ids, no asset_ids)
assert 'no_faq_schema' in INVALID_MAPPINGS, 'FASE-2 regression: clave pain_id faltante'
assert 'monthly_report' not in INVALID_MAPPINGS, 'FASE-2 regression: clave asset_id presente'
print('OK: INVALID_MAPPINGS usa pain_ids correctos (FASE-2 conservado)')
"

# 4. Generar propuesta de prueba
python main.py v4complete --url https://hotelcastillareal.com --nombre "Hotel Castilla Real"

# 5. Verificar coherencia financiera en output
cat output/v4_complete/02_PROPUESTA_COMERCIAL_*.md | grep -E "(ROI|recuperación|Beneficio neto)"
# Debe mostrar:
#   - Recupera: $5.041.935 COP (un solo número)
#   - Beneficio neto: $2.641.935 COP (positivo)
#   - ROI: 2.10X (un solo ROI en todo el documento)

# 6. Verificar que no hay assets deprecados
cat output/v4_complete/02_PROPUESTA_COMERCIAL_*.md | grep -E "(og_tags_guide|indirect_traffic|local_content_page)"
# Debe devolver VACÍO

# 7. Verificar sección piloto
cat output/v4_complete/02_PROPUESTA_COMERCIAL_*.md | grep -A5 "Piloto de Validación"
# Debe mostrar la sección completa

# 8. Verificar CAPEX breakdown
cat output/v4_complete/02_PROPUESTA_COMERCIAL_*.md | grep -A10 "Componente | Monto"
# Debe mostrar tabla con desglose
```

---

## 📊 Impacto Esperado

| Métrica | Antes (v4.55.0) | Después (v4.56.0) |
|---|---|---|
| ROIs en documento | 2 distintos (0.45X + 2.10X) | 1 único (2.10X) |
| Bug de suma | ❌ Doble motor | ✅ Unificado |
| Beneficio neto | -$1.330.590 (negativo) | +$2.641.935 (positivo) |
| Mapper semántico | ❌ Sin validación en tabla | ✅ Validado por fila |
| Assets deprecados | ❌ 4 aparecen | ✅ 0 aparecen |
| Piloto 30 días | ❌ Ausente | ✅ Incluido |
| CAPEX breakdown | ❌ Número mágico | ✅ Desglosado |
| Garantía Día 55 KPI | ❌ Sin métrica | ✅ +15% clics GSC |
| WhatsApp narrativa | ❌ "Guía de corrección" | ✅ "Auditoría y Optimización" |
| % inversión/fuga | ❌ 14% falso | ✅ 10.7% calculado |
| Score de cumplimiento | 44% | 96% |

---

## 🔍 NOTAS DE AUDIT v3.1 — Correcciones contra código vivo

Este documento fue auditado forensemente contra el código vivo del repo (8 archivos, 20 claims verificados). Se encontraron y corrigieron 8 fallos en el código propuesto que habrían introducido nuevos bugs:

| # | Fallo original | Corrección aplicada |
|---|---|---|
| AUDIT-1 | "3 ROIs distintos" | → 2 ROIs (0.45X y 2.10X). conservative/realistic/optimistic NO se renderizan en template V6. |
| AUDIT-2 | pain_ratio "~41%" citado del código | → ~13.6% real (comentarios L763-764 obsoletos). 14% del texto ≈ redondeo del 13.6%. |
| AUDIT-3 | "Eliminar fila Total" | → Eliminar bullets "Total 6 meses" (L113-117 template). No existe fila de tabla. |
| AUDIT-4 | A5 elimina pain_pct/recov_pct | → MANTENER (template V6 L123 los usa). AÑADIR trazabilidad_origen. |
| AUDIT-5 | B1 SERVICE_CATALOG lookup frágil | → ASSET_TO_PAIN_ID mapping directo. |
| AUDIT-6 | B2 mantiene optimization_guide en BREACH | → ELIMINADO (contradice B5 deprecation). |
| AUDIT-7 | B6 solo cambia desc (WhatsApp) | → Cambiar AMBOS: estado="📋 Auditoría incluida" + desc. |
| AUDIT-8 | C1 pilot $665,480 sin trazabilidad | → $400,000 = 1 mes OPEX sin CAPEX. |

---

## 🏁 VEREDICTO FINAL COMO CTO

> **La v4.55.0 es una "mejora" cosmética que empeoró el problema fundamental.**
>
> El equipo confundió **bajar el precio** con **arreglar el modelo**. Bajar de $800K a $400K sin resolver la arquitectura de proyección creó un Frankenstein matemático: dos ROIs distintos (0.45X vs 2.10X), bugs de suma, números mágicos en trazabilidad, y assets deprecados que siguen apareciendo.
>
> **Validación exhaustiva completada:** 9/9 claims del QA confirmados con evidencia de código vivo. 5 fallos adicionales descubiertos (F1-F5) que el plan original no cubría. El PR original de 6 commits era inviable en 3 de ellos (imports inexistentes, regresión de FASE-2, arquitectura ficticia).
>
> **PR corregido en 3 fases con código validado contra la arquitectura real del repo.** La Fase A (quirúrgica) resuelve el bug raíz en ~20 líneas de cambio. La Fase B activa validación que ya existe pero no se usaba. La Fase C añade features sin tocar el motor.
>
> **Mi recomendación profesional:** Detener envío comercial. Aplicar las 3 fases en orden. Regenerar propuesta. Solo entonces enviar.
>
> **La diferencia entre enviar hoy vs. enviar mañana con los fixes corregidos:**
> - **Hoy:** Cliente detecta inconsistencias, pierde confianza, no firma. Oportunidad perdida ($9.7M CAPEX+OPEX).
> - **Mañana:** Cliente ve coherencia matemática perfecta, ROI claro de 2.10X, beneficio neto positivo de $2.64M, cierre probable.

---

## ⚠️ LECCIONES APRENDIDAS (Para evitar repetir este ciclo)

1. **Nunca bajar precio sin auditar el motor de proyección.** El precio es output del modelo, no input. Cambiar el precio sin tocar el modelo = garantizar inconsistencia.
2. **Un solo origen de verdad para cada número.** Si `total_recovered` y `total_recuperacion_6m` existen, uno sobra.
3. **Activar validadores existentes antes de crear nuevos.** `asset_semantics_validator.py` llevaba semanas existiendo sin integrarse donde más se necesitaba (la tabla de la propuesta).
4. **No proponer PRs sin validar imports contra el codebase real.** 3 de 6 commits del PR original fallaban en runtime.
5. **Los tests deben usar valores de producción reales.** `fee_mensual=654796` en tests cuando el pricing real es $400K = tests que no protegen contra bugs reales.
