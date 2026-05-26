# Análisis Integral — Propuesta Comercial Castilla Real (FASE-F)

> **⚠️ CORREGIDO 2026-05-26**: Este documento fue auditado por ROI_AUDIT.md.
> Tres claims originales son INCORRECTOS: (1) no hay triple descuento,
> (2) la "fórmula corregida" con $7.7M × 75% es fraudulenta, (3) pain_ratio
> NO es "% del dolor abordable con IAO". Los hallazgos comerciales (alertas,
> testimonios, jerga, anexo APIs) SÍ son válidos. Ver secciones marcadas con
> TESIS CORRECTA y ~~tachado~~.

**Fecha**: 2026-05-26
**Validación contra código**: 2026-05-26 (v4_proposal_generator.py, commercial_gate.py, scenario_calculator.py, templates, financial_scenarios.json)
**Propuesta analizada**: `output/Castilla Real/v4_complete/02_PROPUESTA_COMERCIAL_20260526_131333.md`
**Hotel**: https://www.hotelcastillareal.com/
**Versión pipeline**: v4.53.0 (NOTA: el frontmatter del output dice `version: 4.0.0` — hardcodeado en v4_proposal_generator.py:725, NO actualizado)

---

## Resumen Ejecutivo

| Dimensión | Estado | Detalle |
|-----------|--------|---------|
| Técnica (pipeline) | ✅ 4.5/5 | Paquete funcional — niveles superados |
| Comercial (documento) | ⚠️ 55% | Scorecard 3/9 — 3 bloqueantes críticos |
| Financiera (ROI) | 🔴 NEGATIVO | -$5.367.168 COP en 6 meses, ROI 0.3X |
| Decisión requerida | 🚨 SÍ | Antes de entregar al cliente |

**Veredicto**: ❌ NO se puede enviar al dueño del hotel hoy. Tres razones independientes y cada una fatal:

1. La tabla de ROI le dice que va a **perder $5.3 millones** contratando el servicio
2. El bloque "⚠️ Alertas Comerciales" visible **delata que el propio sistema desconfía de la propuesta**
3. El placeholder `[Espacio para casos de éxito...]` muestra que es una **plantilla genérica sin respaldo**

---

## PARTE 0: VALIDACIÓN CONTRA CÓDIGO VIVO

Cada hallazgo fue rastreado hasta su archivo y línea exacta en el código. Marcado como:

- ✅ **CONFIRMADO**: el claim del análisis original es correcto
- 🔴 **NUEVO**: hallazgo no documentado previamente
- 🟡 **PARCIAL**: requiere matiz

---

### 0.1 Fórmula del ROI — ✅ CONFIRMADO con trace completo

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

**Línea 685** — pain_ratio:
```python
pain_ratio = getattr(self, '_current_pain_ratio', scenario_config.get('pain_ratio_default', 0.20))
```
`_current_pain_ratio` viene del pricing engine → **0.4082** para Castilla Real (confirmado en `financial_scenarios.json:41`).

**Línea 696** — effective_monthly_gain (descuento compuesto):
```python
effective_monthly_gain = int(raw_monthly_loss * pain_ratio * recovery_realistic)
```
Donde `recovery_realistic = 0.20` (`_load_scenario_config()` línea 137 del fallback).

**Resultado**: 3,741,696 × 0.4082 × 0.20 = 305,472 COP/mes ✅

**Líneas 783-794** — Tabla mensual PLANA (sin curva de maduración):
```python
'rec_m1': format_cop(effective_monthly_gain),  # ← IDÉNTICO
'rec_m2': format_cop(effective_monthly_gain),  # ← IDÉNTICO
# ... los 6 meses proyectan exactamente la misma recuperación
```

**Línea 1445** — `_calculate_roi` aplica recovery_factor UNA VEZ sobre el gain bruto (NO es un tercer descuento — ver ROI_AUDIT.md):
```python
total_gain = gain * recovery_factor * months  # gain YA es bruto, OK
```

---

### 0.2 "⚠️ Alertas Comerciales" — ✅ CONFIRMADO como fuga al output del cliente

**Dos puntos de inyección**:

1. `v4_proposal_generator.py:374-386` — propuesta:
```python
if not commercial_report.blocking_passed:
    alert_section = "\n---\n## ⚠️ Alertas Comerciales\n\n"
    alert_section += "Las siguientes alertas de copywriting fueron detectadas ..."
    document_content += alert_section  # ← APPEND DIRECTO AL DOCUMENTO FINAL
```

2. `v4_diagnostic_generator.py:514-526` — diagnóstico (mismo patrón)

**Gate raíz**: `modules/quality_gates/commercial_gate.py:422-455` — `_check_roi_negative()`

**NO EXISTE** ningún `if document_audience == "internal"` en ninguna de las dos ubicaciones. El bloque se apendea incondicionalmente.

**Bypass existente** (línea 362-364): si `pricing_result.is_onboarding == True`, el gate pasa incluso con ROI negativo. Para Castilla Real (`tier: boutique`), `is_onboarding = False` → el gate se dispara.

**Archivos involucrados**:
- `modules/quality_gates/commercial_gate.py` — define 5 BLOCKING + 4 WARNING gates
- `v4_proposal_generator.py:335-398` — inyecta en propuesta
- `v4_diagnostic_generator.py:505-540` — inyecta en diagnóstico
- `tests/quality_gates/test_commercial_gate.py` — tests existentes

---

### 0.3 Placeholder testimonios — ✅ CONFIRMADO

**Archivo**: `modules/commercial_documents/templates/propuesta_v6_template.md:171`
```
> *[Espacio para casos de éxito — hoteles del Eje Cafetero con resultados medibles]*
```

**NO es condicional**: sin `{% if testimonials %}`, sin flag, sin variable. El texto está hardcodeado en el template y se renderiza siempre que se usa propuesta_v6_template.md.

---

### 0.4 Scenario Calculator: fórmula mezcla hechos con hipótesis — 🔴 NUEVO

**Archivo**: `modules/financial_engine/scenario_calculator.py:279-292`

```python
current_ota_commission_loss = ota_bookings × adr × 15%    # VERIFICABLE
potential_shift = ota_bookings × 0.10                       # SUPUESTO (10% shift)
savings = potential_shift × adr × 15%                       # DERIVADO
ia_visibility_boost = occupied_room_nights × 0.05 × adr    # SUPUESTO (5% IA)
monthly_loss = current_ota_commission_loss - savings - ia_visibility_boost
```

**Evidencia en JSON** (`financial_scenarios_20260526_131321.json`):
| Componente | Valor | Tipo | Source |
|-----------|-------|------|--------|
| ota_commission_cop | $7,741,440 | VERIFICABLE | industry_standard_15pct |
| shift_savings_cop | $774,144 | SUPUESTO | "hardcoded: sin GA4" |
| ia_revenue_cop | $3,225,600 | SUPUESTO | "estimado: sin datos GA4" |
| **Neto** | **$3,741,696** | **57% SUPUESTOS** | |

El número verificable ($7.7M de comisión OTA bruta) **NUNCA se muestra al cliente**. La "pérdida" de $3.7M ya descuenta beneficios hipotéticos.

---

### 0.5 Optimistic scenario negativo — 🔴 NUEVO (falla estructural)

`financial_scenarios.json:13`: `"optimistic": -270950.4`

Los 3 escenarios:
- Conservative: $7,276,954
- Realistic: $3,741,696
- Optimistic: **-$270,950**

El orden es correcto (optimistic < realistic → mejor), pero incluso el MEJOR escenario es negativo. Con `direct_channel_percentage = 0.2` y `evidence_tier = B`, el modelo financiero completo produce pérdida en todos los escenarios. No es un bug de código — es una **restricción estructural del modelo** que hace inviable la venta del paquete completo a este perfil de hotel.

---

### 0.6 Pain_ratio divergente diagnóstico vs propuesta — ✅ CONFIRMADO como diseño

**Código**:
- Diagnóstico: `pain_ratio_default = 0.20` (`_load_scenario_config()` línea 139)
- Propuesta: `_current_pain_ratio` del pricing engine (~0.41)

**Comentario en código** (líneas 748-754): *"FASE-B: pain_ratio real del pricing (~41% Castilla Real) + recovery_factor real (20%). Esto diferencia la propuesta del diagnóstico que usa defaults conservadores (20%/20%)."*

**Amplificación**: No es un bug, pero es frágil. Si el pricing engine no está disponible, el fallback es 0.20 para AMBOS documentos → propuesta y diagnóstico mostrarían la misma proyección, eliminando la diferenciación comercial.

---

### 0.7 Versión hardcodeada — 🔴 NUEVO

`v4_proposal_generator.py:725`: `'version': '4.0.0'`

El frontmatter del output siempre dice `version: 4.0.0` sin importar la versión real del pipeline. Esto no es un bug funcional pero elimina trazabilidad.

---

### 0.8 ADR del scraping desconectado del financial engine — 🔴 NUEVO

`web_scraper.py` extrae `precio_promedio` del sitio web (4 métodos: Schema JSON-LD, meta tags, CSS selectors, regex). Pero `scenario_calculator.py` toma el ADR solo de `datos_operativos.get('valor_reserva_cop')` → si no hay onboarding → benchmark regional → hardcode $300K. El precio scrapeado del sitio web **nunca se consulta** como fallback intermedio.

---

### 0.9 Precision tier inconsistente — 🔴 NUEVO

`financial_scenarios.json`:
- Línea 26: `"evidence_tier": "B"`
- Línea 45: `"precision_tier": "C"`
- Línea 46: `"can_show_exact_money": false`

Dos sistemas de tier diferentes en el mismo JSON sin documentación que explique la relación. `precision_tier = C` significa "no mostrar dinero exacto" pero el output muestra "$3.741.696 COP" con precisión de peso. Inconsistencia no detectada por los quality gates actuales.

---

## PARTE 1: HALLAZGOS COMERCIALES (Deuda FASE-F)

### Hallazgo 1: Inconsistencia pain_ratio — 20% vs 40% ✅

El puente dual (CROSS-1, FASE-B) está correctamente implementado, pero los valores divergen:

| Documento | pain_ratio usado | Recuperación proyectada 6m |
|-----------|-----------------|---------------------------|
| Diagnóstico | 20% × 20% = 4% | ~$898.002 COP |
| Propuesta | ~41% × 20% = 8.2% | $1.832.832 COP |

**Es intencional, no bug:**
- **Diagnóstico**: usa defaults conservadores (20%) para causar impacto sin conocer el perfil real
- **Propuesta**: usa el `pain_ratio` real del pricing engine (~41%) porque ya tiene datos del hotel

**Riesgo identificado en validación**: Si el pricing engine falla o no está disponible, el fallback es 0.20 para ambos documentos → la diferenciación comercial colapsa.

**Acción**: No requiere fase. Si se quiere, agregar nota explicativa de 3 líneas en el template del diagnóstico: *"El 20% del diagnóstico es una estimación regional conservadora; su perfil de canal directo (20%) ajusta esto al 41% en la propuesta."*

### Hallazgo 2: ROI proyectado negativo — Escenarios Base ✅

```
Inversión mensual:        $1.200.000 COP
Recuperación estimada:     $305.472 COP/mes  (41% × 20% × $3.741.696)
Resultado neto/mes:          -$894.528 COP
Resultado neto/6m:        -$5.367.168 COP
ROI a 6 meses:                 0.3X
```

El escenario `optimistic` en `financial_scenarios.json` también es **negativo** (-$270.950/mes).

**Causa raíz (validada en código):**
- `direct_channel_percentage: 0.2` (80% de reservas por OTA → comisión alta)
- `evidence_tier: B` (sin GA4, sin datos reales de tráfico)
- Pricing actual: $1.200.000 COP/mes fijo — `modules/financial_engine/pricing_resolution_wrapper.py`
- El modelo asume recuperación vía canal directo, pero el hotel no tiene infraestructura para capturarla aún
- **NUEVO**: El scenario_calculator descuenta $3,999,744 en ahorros hipotéticos (shift 10% + IA boost 5%) del número verificable ($7.7M). El 57% del resultado son supuestos.

**No se resuelve con código** — requiere rediseño del modelo comercial o ajuste de pricing.

---

## PARTE 2: VALIDACIÓN TÉCNICA DEL DOCUMENTO (Scorecard)

### Scorecard de Cumplimiento: 3/9 (33%)

| # | Recomendación | Estado | Observación | Trace |
|---|---------------|--------|-------------|-------|
| 1 | 🚨 Rehacer tabla ROI con curva progresiva y ROI positivo | ❌ NO HECHO | Sigue mostrando pérdida de $5.3M y ROI 0.3X | `v4_proposal_generator.py:783-794` — tabla plana |
| 2 | 🚨 Eliminar "En preparación" de entregables | 🟡 PARCIAL | Cambió a "En proceso de activación — Semana 2" con ⚠️ 50% | Output líneas 46, 67-69 |
| 3 | 🚨 Agregar Resumen Ejecutivo de 30 segundos | ❌ NO HECHO | El doc arranca directo con "El problema" | Template V6 línea 18 |
| 4 | 🚨 Quitar tabla de costos de APIs | 🟡 PARCIAL | Movida al Anexo Técnico, pero sigue visible | Template V6 líneas 218-229, output líneas 260-271 |
| 5 | Reemplazar tabla "Problema/Impacto" por "Antes/Después" | ❌ NO HECHO | Tabla redundante intacta | Template V6 líneas 24-28 |
| 6 | Traducir jerga técnica (AEO, UTMs, P1/P2/P3) | 🟡 PARCIAL | Aún aparecen AEO, UTMs, P1/P2/P3 | Output líneas 75, 162 |
| 7 | Agregar prueba social / testimonios | ⚠️ PEOR | Placeholder visible `[Espacio para casos de éxito...]` | `propuesta_v6_template.md:171` hardcodeado |
| 8 | Justificar "cupo limitado" | ✅ HECHO | "2 cupos disponibles para julio 2026" | Output línea 14 |
| 9 | Garantía medible sin GA4 del cliente | ✅ HECHO | "Instalamos tracking propio en el Día 7" | Output línea 203 |

---

## PARTE 3: ALERTAS CRÍTICAS

### 🚨 ALERTA ROJA: Fuga de información interna al cliente

**Código**: `v4_proposal_generator.py:374-386` y `v4_diagnostic_generator.py:514-526`

Al final del documento aparece:

```
⚠️ Alertas Comerciales
Las siguientes alertas de copywriting fueron detectadas y deben
revisarse antes de entregar al cliente:

ROI negativo como argumento de cierre (CG-ROI-NEGATIVE)
Beneficio neto 6m negativo ($-5,367,168 COP) y ROI 0.19X sin plan
de onboarding alternativo. Una propuesta que dice 'págueme para
perder dinero' no cierra.
```

Esto es un bloque de validación de `CommercialGateValidator` (`modules/quality_gates/commercial_gate.py`) que se inyecta directamente al `document_content` sin verificar audiencia. El validador fue diseñado para alertar al **operador**, pero se implementó como apéndice al **documento del cliente**.

**Fix en código**: 
1. Agregar parámetro `document_audience: str = "client"` en `generate()` de ambos generadores
2. Condicional: `if document_audience == "internal": document_content += alert_section`
3. Opcional: generar dos archivos — `02_PROPUESTA_COMERCIAL.md` (cliente) y `02_PROPUESTA_COMERCIAL_INTERNAL.md` (operador)

**Archivos a modificar**:
- `v4_proposal_generator.py:335-398` (inyección de alerts)
- `v4_diagnostic_generator.py:505-540` (inyección de alerts)
- `modules/quality_gates/commercial_gate.py` (no requiere cambios — el validador funciona bien, es el caller quien decide si renderizar)

### 🔴 El ROI negativo: problema comercial, NO de fórmula

> **TESIS CORRECTA (2026-05-26):** El ROI negativo NO se debe a una fórmula
> rota. Se debe a un mismatch comercial entre el precio mínimo ($1.200.000/mes)
> y el recovery realista que el modelo puede defender (~$305.472/mes sin GA4).
>
> La fórmula del código es metodológicamente correcta. NO hay triple descuento.
> Ver ROI_AUDIT.md para la auditoría detallada contra código vivo.

**Matemática verificada:**
```
raw_monthly_loss         = $3.741.696
pain_ratio               = 0.4082 (artifact del min_price, NO "% IAO")
recovery_factor           = 0.20
effective_monthly_gain    = $3.741.696 × 0.4082 × 0.20 = $305.472/mes
recuperación 6m           = $305.472 × 6 = $1.832.832
inversión 6m              = $1.200.000 × 6 = $7.200.000
neto 6m                   = -$5.367.168
ROI                       = 0.25X ≈ 0.3X
```

**NOTA sobre pain_ratio (0.4082):** En pricing_calculator.py:252-255,
pain_ratio = price / expected_loss. Para Castilla Real, el min_price floor
de $1.2M clampa el precio, produciendo 0.4082. NO significa "41% del dolor
abordable con IAO" — es un artifact aritmético del pricing floor.

**~~Tesis incorrecta descartada~~** (PARTE 3 original):
~~Reescribir fórmula usando $7.7M comisión OTA bruta × 75% efectividad ×
curva de maduración → ROI 3.67X / +$19.2M.~~ Esto promete más recuperación
que toda la pérdida neta. Es comercialmente fraudulento y no está respaldado
por el modelo.

---

## PARTE 4: PROBLEMAS PERSISTENTES

### 1. Placeholder de prueba social — peor que no tenerlo
```
[Espacio para casos de éxito — hoteles del Eje Cafetero
con resultados medibles]
```
El cliente ve los corchetes y entiende que es una plantilla vacía.
**Fix**: `{% if testimonials|length > 0 %}...{% endif %}` — no renderizar si array vacío. O simplemente eliminar la sección completa del template hasta que haya testimonios reales.

**Archivo**: `modules/commercial_documents/templates/propuesta_v6_template.md:169-171`

### 2. Tabla de entregables muestra incertidumbre
```
| Schema Hotel | ⚠️ Listo para implementar | Requiere confirmacion post-firma |
| Página FAQ   | En proceso de activación  | Datos pendientes del cliente     |
```

**Fix**: Cambiar "Estado" por "Momento de entrega", eliminar porcentajes de confianza:

| Entregable | Cuándo lo recibe |
|------------|-----------------|
| Schema Hotel | Día 4 (Activación inicial) |
| Schema Organization | Día 45 (Consolidación) |
| Página de FAQ | Semana 3 (con sus respuestas) |
| Meta Tags Sociales | Día 7 (Activación completa) |

**Archivo**: `v4_proposal_generator.py:_generate_asset_quality_table()`

### 3. Jerga técnica sin traducir
- **"Nota sobre AEO: AEO (Answer Engine Optimization)..."** → Eliminar o traducir a: *"La optimización para asistentes de voz como Siri ya está incluida en su FAQ y redes sociales."*
- **"UTMs, conversiones"** → *"Sistema de rastreo para medir de dónde viene cada reserva"*
- **"P1 / P2 / P3"** → Nombrar por beneficio: *"Fase inicial: WhatsApp y datos para IA"*, *"Fase de contenido: Preguntas frecuentes y guías locales"*

**Gate existente**: `CG-TECH-JARGON` en `commercial_gate.py:84-91` — ya detecta estos términos como WARNING pero no bloquea.

### 4. Anexo Técnico de APIs — ruido para el cliente
Aunque movido al final, el dueño ve "OpenRouter, Gemini, Perplexity" y costos en USD.
**Fix**: Reemplazar por párrafo de transparencia:
> *"Nuestro análisis utiliza tecnología de punta (múltiples modelos de IA) para evaluar cómo lo ven ChatGPT, Gemini y Perplexity. El costo de estas consultas lo absorbemos nosotros como parte del servicio — usted no paga nada adicional."*

**Archivo**: `propuesta_v6_template.md:218-229`

---

## PARTE 5: LO QUE SÍ QUEDÓ IMPECABLE (Conservar)

1. **"2 cupos disponibles para julio 2026"** — Específico, creíble, urgente
2. **"Instalamos tracking propio en el Día 7 — sin necesidad de que tengas GA4"** — Resuelve objeción de medición
3. **Sección de Fotos con specs técnicas** — Gestiona expectativas perfectamente
4. **Plan 7/30/60/90 días** — Certeza operativa (quitar P1/P2/P3)
5. **Formas de pago + descuentos por anticipado** — Estructura comercial sólida

---

## PARTE 6: OPCIONES COMERCIALES

### Opción A: Lower pricing hasta tener GA4
$300-400k/mes durante 1-2 meses de onboarding mientras se conecta GA4, luego re-calcular con datos reales.

| Mes | Inversión | Recuperación real (est.) | Resultado |
|-----|-----------|--------------------------|-----------|
| 1 | $300.000 | $305.472 | +$5.472 |
| 2 | $300.000 | $305.472 | +$5.472 |
| 3+ | $1.200.000 | [datos GA4] | Por definir |

### Opción B: Quick wins primero — fase de activación
Vender quick wins de alto dolor (WhatsApp conflict, Schema Hotel, llms.txt) como proyecto único de bajo costo. La fase mensual completa se vende después con datos reales.

- **Activación**: $0-$200.000 (proyecto puntual, ~1 semana)
- **Incluye**: WhatsApp conflict guide, Schema Hotel, llms.txt, diagnóstico completo
- **Upsell**: Contrato mensual después de ver resultados medidos

### Opción C: Cobrar % del recovery real
En vez de fee fijo, cobrar un % del monto recuperado. Elimina el riesgo del cliente y alinea incentivos.

```
Propuesta: 15% del recovery mensual
Si recovery real = $305.472/mes → fee = $45.821/mes ✅
Si recovery real = $1.005.768/mes (con GA4) → fee = $150.865/mes ✅
```

### Opción D: Entregar como está con transparencia
Documentar que sin GA4 no hay ROI verificable. Incluir en la propuesta: *"Esta proyección se recalculará con sus datos de Google Analytics 4 en el Día 30. El primer reporte de ROI real será el Día 45."*

---

## PARTE 7: RECOMENDACIÓN ESTRATÉGICA

**Opción D (temporal) + Opción B (estratégica):**

1. **Opción D (ahora)**: Entregar la propuesta con el ROI actual y la garantía de tracking en Día 7. El cliente ve que no hay magia — hay medición real desde el día 1. Si cierra así, fine. Si no, pasar a B.

2. **Opción B (si no cierra con D)**: Vender fase de activación como proyecto separado. Riesgo casi cero para el cliente. Construye confianza y datos reales.

**Diagnóstico de fondo**: El diagnóstico (`01_DIAGNOSTICO`) está al **98% de madurez** — herramienta comercial excelente. La propuesta (`02_PROPUESTA`) está al **55%** porque tiene fugas de información interna al output, jerga técnica, y un ROI negativo que no puede venderse como retainer estándar.

**Recomendación técnica**: La fórmula del ROI es correcta. NO tocarla para inflar números. En cambio, priorizar: (1) ocultar alertas internas del output cliente, (2) eliminar placeholder testimonios, (3) corregir la nota semántica de pain_ratio, y (4) reestructurar oferta/precio para Castilla Real según las opciones de PARTE 6.

---

## PARTE 8: PLAN DE ACCIÓN PRIORIZADO

### 🔴 Nivel 1 — Bloqueantes (ANTES de enviar a cualquier prospecto)

- [x] ~~**Reescribir fórmula del ROI**~~ **DESCARTADO** — La fórmula es correcta. Ver ROI_AUDIT.md. El problema es comercial (precio vs recovery), no técnico.
  - ~~Archivos: `v4_proposal_generator.py:686,696,783-794`, `scenario_calculator.py:279-292`~~
- [ ] **Ocultar bloque "⚠️ Alertas Comerciales"** del output al cliente — agregar `document_audience` switch
  - Archivos: `v4_proposal_generator.py:335-398`, `v4_diagnostic_generator.py:505-540`
- [ ] **Eliminar placeholder de testimonios** si el array está vacío (condicional en template)
  - Archivo: `propuesta_v6_template.md:169-171`
- [ ] **Decidir opción comercial** a presentar (Jhond)

### 🟡 Nivel 2 — Importantes (siguiente sprint)

- [ ] Agregar **Resumen Ejecutivo de 30 segundos** al inicio
- [ ] Cambiar tabla de entregables a **"Momento de entrega"** sin porcentajes de confianza
- [ ] Reemplazar tabla "Problema/Impacto" por comparativa **"Si sigue como está / Si implementa el Kit"**
- [ ] Traducir AEO, UTMs, P1/P2/P3 a lenguaje de negocio
- [ ] Si Opción B: definir precio de fase activación y quick wins (Jhond)
- [ ] Si Opción D: redactar nota de transparencia sobre GA4 (Agente)
- [ ] Conectar ADR del web_scraper como fallback intermedio en la cadena de resolución de ADR
  - Archivo: `scenario_calculator.py` — insertar entre onboarding y benchmark regional

### 🟢 Nivel 3 — Pulido (v5.0)

- [ ] Simplificar Anexo Técnico de APIs a un párrafo de transparencia
- [ ] Conseguir 1-2 testimonios reales (aunque sea de pilotos beta)
- [ ] Nota explicativa pain_ratio 20% vs 40% (opcional, copywriting)
- [ ] Actualizar `version` en el generador para que refleje la versión real del pipeline
  - Archivo: `v4_proposal_generator.py:725`
- [ ] Documentar relación `evidence_tier` vs `precision_tier` en financial_scenarios.json

---

## PARTE 9: CONTEXTO PARA CONVERSACIÓN CON CLIENTE

**Lo que NO deben decir:**
- "El ROI es negativo" (cierra el diálogo)
- "No tenemos datos suficientes"
- "El modelo no funciona" (sí funciona — necesita GA4)

**Lo que SÍ deben decir:**
- "Instalamos medición real desde el Día 1 — usted va a ver exactamente cuánto se recupera"
- "La primera proyección se recalcula con sus datos reales en el Día 30"
- "El quick win de WhatsApp solo ya justifica la inversión" (si se vende fase activación)

---

## Archivos de Referencia

| Archivo | Ubicación |
|---------|-----------|
| Propuesta analizada | `output/Castilla Real/v4_complete/02_PROPUESTA_COMERCIAL_20260526_131333.md` |
| Diagnóstico generado | `evidence/FASE-F/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260526_131324.md` |
| Análisis post-implementación | `evidence/FASE-F/analisis_post_implementacion.md` |
| Financial scenarios | `evidence/FASE-F/v4_audit/financial_scenarios_20260526_131321.json` |
| Pain ledger | `evidence/FASE-F/v4_audit/pain_ledger.json` |

### Archivos de código validados

| Archivo | Líneas clave | Rol |
|---------|-------------|-----|
| `modules/commercial_documents/v4_proposal_generator.py` | 127-140, 335-398, 642-934, 1432-1455 | Generador de propuestas, ROI, alertas |
| `modules/commercial_documents/v4_diagnostic_generator.py` | 505-540 | Generador de diagnóstico, alertas |
| `modules/quality_gates/commercial_gate.py` | 69-91, 98-113, 200-249, 416-455 | Validación comercial, CG-ROI-NEGATIVE |
| `modules/financial_engine/scenario_calculator.py` | 260-307 | Fórmula de escenarios (OTA + shift + IA boost) |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | 169-171, 218-229 | Template con placeholder y anexo APIs |
| `evidence/FASE-F/v4_audit/financial_scenarios_20260526_131321.json` | 1-46 | Datos financieros de Castilla Real |

---

*Documento unificado de `deuda-comercial-fase-f.md` + `ROI.md` + validación contra código vivo — 2026-05-26*
