# 🔍 Evaluación de la Propuesta Comercial v4.0 (2026-05-25) — AUDITORÍA VIVA (v3)

> **Auditoría**: 2026-05-26 vs código vivo (`v4_proposal_generator.py`, `modules/quality_gates/commercial_gate.py`, `propuesta_v6_template.md`)
> **Verificación cross-documento**: `01_DIAGNOSTICO`, `02_PROPUESTA`, `v4_complete_report.json`, 12 assets
> **Estado**: ❌ 5 BLOQUEANTES, 4 ALTOS, 7 MEDIOS, 3 BAJOS — NO enviar al dueño aún
> **Hallazgos totales**: 19 (6 cross-documento + 8 código + 3 template + 2 cosméticos)

---

# 🔴 NIVEL 1 — BLOQUEANTES: Desconexiones cross-documento (el cliente ve esto)

---

## 🔗 TRAZA COMPLETA: DIAGNÓSTICO → PROPUESTA → ASSETS (Hotel Castillo Real, 2026-05-25)

**Archivos verificados**: `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260525_200650.md`, `02_PROPUESTA_COMERCIAL_20260525_200700.md`, `v4_complete_report.json`, 12 assets en `hotelcastillareal/`

**Severidad general**: 🔴 6 DESCONEXIONES entre los 3 documentos que el cliente recibe

---

### CROSS-1 🔴 CRÍTICA: Sin puente dual entre fuga bruta ($22.4M) y recuperación efectiva ($1.8M)

**Evidencia en el output real**:

| Documento | Línea | Qué dice | Cálculo real |
|-----------|-------|----------|--------------|
| Diagnóstico | L218 | "Proyección 6 meses: **$22.450.176 COP**" | `raw_loss × 6 = $22,450,176` (sin pain_ratio ni recovery) |
| Propuesta | L128 | "Recupera: **$1.832.832 COP**" | `effective_monthly_gain × 6 = $305,472 × 6` |
| Propuesta | L132 | "41% × 20% = ~$305,472/mes" (nota pequeña) | `raw × 0.41 × 0.20 = $305,472` |

**El gap**: $22,450,176 ÷ $1,832,832 = **12.2:1**. El cliente lee el diagnóstico y espera recuperar $22M. Recibe una propuesta que ofrece $1.8M. La única explicación es una nota de 2 líneas en la propuesta (L132). El diagnóstico NUNCA menciona pain_ratio ni recovery_factor.

**Causa raíz**: `_prepare_template_data()` del diagnóstico genera `proyeccion_6_meses = raw_monthly_loss × 6` (sin ajustes). El generador de propuesta usa `effective_monthly_gain = raw × pain_ratio × recovery`. Son dos generadores distintos que no comparten la misma filosofía financiera.

**Ruta recomendada — puente dual obligatorio (Opción C)**: diagnóstico y propuesta deben mostrar SIEMPRE dos cifras coordinadas: **Fuga total estimada** (`raw_loss × 6`) y **Recuperación proyectada con servicio** (`raw_loss × pain_ratio × recovery_factor × 6`). La nota `41% × 20%` debe pasar de nota menor en la propuesta a explicación visible en el diagnóstico, y repetirse en propuesta como puente de trazabilidad.

**Por qué esta ruta**: preserva el impacto comercial de la fuga bruta ($22.4M), pero evita que el cliente sienta que se infló el problema para vender una recuperación de solo $1.8M. La venta queda anclada en transparencia: "esto es lo que se está fugando; esto es lo razonablemente recuperable con el alcance contratado".

---

### CROSS-2 🔴 CRÍTICA: 7 brechas → 8 servicios → sin mapping verificable

El diagnóstico identifica 7 brechas con costos específicos pero la propuesta lista 8 servicios sin indicar cuál resuelve cuál:

| Brecha (Diagnóstico) | Costo/mes | ¿Servicio en Propuesta? | Asset generado | Confidence |
|---------------------|-----------|------------------------|----------------|------------|
| 1. Sin Schema Hotel | $1,005,768 | Schema Hotel ✅ | hotel_schema | 1.0 |
| 2. Metadatos CMS | $402,232 | ¿SEO Local? ❓ | optimization_guide | **0.5** ⚠️ |
| 3. Baja preparación IA | $603,536 | ¿Optimización IA? ❓ | llms_txt + local_content_page | 1.0 + 1.0 |
| 4. Sin FAQ | $482,679 | Página FAQ ✅ | faq_page | 0.85 |
| 5. IA sin guía | $603,536 | Optimización IA Gen ✅ | og_tags_guide + open_graph | 0.8 + 1.0 |
| 6. Sin OG Tags | $321,786 | Meta Tags Sociales ✅ | open_graph | 1.0 |
| 7. Sin Schema Org | $321,786 | Schema Organization ✅ | org_schema | 0.8 |

Las brechas 2 y 3 son AMBIGUAS — el cliente no puede verificar que su problema será resuelto. Peor aún: el asset `optimization_guide` tiene **confidence=0.5** (el más bajo de los 12). La brecha más ambigua tiene el asset más débil.

**Fix**: Cada servicio en la propuesta debe indicar qué brecha(s) del diagnóstico resuelve, con su costo asociado. Tabla de 2 columnas: "Su problema" → "Nuestra solución".

---

### CROSS-3 🟠 ALTA: Escenario "optimista" en financial_data es NEGATIVO

**Diagnóstico** (L215-217):
```
Mínimo garantizable:  $2,993,356 COP/mes (70%)
Más probable:         $3,741,696 COP/mes (20%)
Máximo alcanzable:    $4,490,035 COP/mes (10%)
```

**`v4_complete_report.json` financial_data.scenarios**:
```json
"conservative": 7276953.6,
"realistic":    3741696.0,
"optimistic":  -270950.4    ← NEGATIVO
```

El escenario "optimista" real es **-$270,950** — el hotel PIERDE dinero incluso en el mejor caso. Pero el diagnóstico presenta "Máximo alcanzable: $4,490,035" — que es el límite superior del RANGO de fuga bruta, no un escenario de recuperación. Son dos conceptos distintos bajo el mismo encabezado "Escenarios de Recuperación".

**Fix**: Los "Escenarios de Recuperación" del diagnóstico deben mostrar recuperación neta proyectada (con pain_ratio + recovery), no rango de fuga bruta.

---

### CROSS-4 🟡 MEDIA: "Botón de WhatsApp | Presente en sitio" contradice la alerta del diagnóstico

**Propuesta** L47: `Botón de WhatsApp | ℹ️ Presente en sitio` — implica que todo está bien.
**Diagnóstico** L36-37: `🚨 ALERTA — Conflicto de WhatsApp detectado` — números no coinciden.

**Fix**: La propuesta debe reflejar el conflicto: "Botón de WhatsApp | ⚠️ Requiere corrección (guía incluida)".

---

### CROSS-5 🟡 MEDIA: "⚠️ En preparación" sin vincular a confidence real

La propuesta marca 5 de 10 entregables como "⚠️ En preparación". Pero el asset `optimization_guide` (detrás de "SEO Local") tiene **confidence=0.5** — muy por debajo del umbral 0.65. El diagnóstico advierte 1 asset con confianza baja pero la propuesta no vincula el warning al servicio específico.

**Fix**: La tabla de servicios debe mostrar confidence score junto al estado.

---

### CROSS-6 🟢 BAJA: Publication gates NOT_READY pero documentos se generaron igual

`v4_complete_report.json` → `phases.phase_4_publication_gates.status: "NOT_READY"`. Ambos documentos se generaron completos pese a los warnings. El sistema no bloquea output con bugs conocidos.

---

### IMPACTO ACUMULADO — lo que experimenta el dueño de Hotel Castillo Real

1. **Lee el diagnóstico**: "Fuga total estimada: $22M en 6 meses; recuperación proyectada con el servicio: $1.8M." → Entiende magnitud y alcance.
2. **Lee la propuesta**: ve las mismas dos cifras y la explicación `41% × 20%`. → Hay continuidad entre documentos.
3. **Compara ambas cifras**: entiende que no se promete recuperar toda la fuga bruta, sino la parte priorizada y razonablemente recuperable. → Baja fricción comercial.
4. **Mira los servicios**: si además se agrega mapping brecha→servicio, puede verificar qué problema resuelve cada entregable. → Trazabilidad.
5. **Ve el WhatsApp**: debe reflejar el conflicto detectado, no marcarlo como resuelto. → Coherencia operativa.
6. **Resultado esperado con la ruta recomendada**: la propuesta deja de parecer inflada; el paquete vende urgencia con transparencia y una promesa de recuperación acotada.

---

# 🔴 NIVEL 2 — CRÍTICOS: Bugs de código que producen números contradictorios

---

## CODE-1 🔴 CRÍTICO: `recovered_6m` vs `total_recovered` — dos definiciones de "recuperación semestral"

**Archivo**: `v4_proposal_generator.py` L.796 vs L.824

```python
# L.796 — optimista (sin recovery_factor)
'recovered_6m': format_cop(projected_monthly_gain * 6)
  → $3,741,696 × pain_ratio × 6 = número grande

# L.824 — conservador (con recovery_factor)
'total_recovered': format_cop(effective_monthly_gain * 6)
  → $3,741,696 × pain_ratio × recovery × 6 = número chico
```

**Causa raíz**: `projected_monthly_gain = raw × pain_ratio` (L681), `effective_monthly_gain = raw × pain_ratio × recovery` (L691). Dos variables distintas para el mismo concepto.

**Fix**: Unificar a `effective_monthly_gain` en L796.

---

## CODE-2 🔴 CRÍTICO: Gate CG-ROI-NEGATIVE y tabla ROI — bases distintas

**Archivos**: `v4_proposal_generator.py` L.339-352; `modules/quality_gates/commercial_gate.py` L.419-448

**Cadena del gate** (L345): `monthly_gain = getattr(realistic, 'monthly_loss_central', None)` → raw loss, sin pain_ratio. Si loss > investment, gate PASA ✅ aunque la tabla muestre pérdida ❌.

**Cadena del template** (L691-825): usa `effective_monthly_gain = raw × pain_ratio × recovery` → el número que VE el cliente. Muestra pérdida pero el gate no la detecta.

**Fix**: El gate debe recibir `net_benefit_6m` calculado con `effective_monthly_gain`, igual que la tabla.

---

## CODE-3 🔴 CRÍTICO: `recovered_6m` contradice a `roi_6m` en la MISMA tabla

**Archivo**: `v4_proposal_generator.py` L.794 vs L.796

```python
L794: 'roi_6m': roi_6_months,    # _calculate_roi(projected_monthly_gain, recovery=0.20)
L796: 'recovered_6m': format_cop(projected_monthly_gain * 6),  # SIN recovery_factor
```

Con pain_ratio=0.20:
- `roi_6m` = 0.1X → "pierdes el 90%"
- `recovered_6m` = $4.5M → "recuperas más de lo que inviertes"

Ambos números en la misma página. No cuadran entre sí.

**Fix**: Si `roi_6m` incluye recovery_factor, `recovered_6m` también debe incluirlo.

---

## CODE-4 🔴 CRÍTICO: `net_benefit_6m` usa la base optimista, minimizando la pérdida real en 2.3×

**Archivo**: `v4_proposal_generator.py` L.797

```python
'net_benefit_6m': format_cop((projected_monthly_gain - monthly_investment) * 6),
```

| Base | net_benefit_6m | Multiplicador |
|------|---------------|---------------|
| `projected_monthly_gain` (actual) | -$2,709,966 | 1× |
| `effective_monthly_gain` (correcto) | -$6,301,992 | **2.3× peor** |

**Fix**: Cambiar `projected_monthly_gain` → `effective_monthly_gain` en L797.

---

## V-1 🔴 CRÍTICO (CORREGIDO): El modelo financiero interno del template — 3 filosofías para el mismo concepto

**Archivo**: `v4_proposal_generator.py` L.681-825

**Lo que el documento original decía (y era falso)**: "recovery_factor se aplica dos veces en cascada (×0.20×0.20×0.20 = 0.8%)".

**Lo que realmente pasa**: `_calculate_roi()` (L1367) recibe `projected_monthly_gain` (SIN recovery) y aplica recovery UNA SOLA VEZ. `effective_monthly_gain` (L691) aplica recovery UNA SOLA VEZ. Son DOS caminos INDEPENDIENTES, no una cascada. Pero producen 3 filosofías distintas:

| Variable | Línea | Base | Filosofía |
|----------|-------|------|-----------|
| `recovered_6m` | L796 | `projected_monthly_gain` | Optimista (sin recovery) |
| `net_benefit_6m` | L797 | `projected_monthly_gain` | Optimista (sin recovery) |
| `roi_6m` | L794 | `projected_monthly_gain` + recovery en `_calculate_roi()` | Intermedio |
| `total_recovered` | L824 | `effective_monthly_gain` | Conservador (con recovery) |

Las 3 conviven en el mismo template. La solución es unificar a UNA base.

**Fix consolidado para CODE-1, CODE-3, CODE-4**: Todas las variables financieras del template deben usar `effective_monthly_gain` como base única.

---

# 🟠 NIVEL 3 — ALTOS: Bugs que degradan credibilidad

---

## A-1 🟠 ALTO: `has_onboarding` con fallback frágil de búsqueda de string

**Archivo**: `v4_proposal_generator.py` L.355-359

```python
has_onboarding = False
if pricing_result is not None:
    has_onboarding = getattr(pricing_result, 'is_onboarding', False)  # PRIMARY
if not has_onboarding:
    has_onboarding = 'onboarding' in document_content.lower()          # FALLBACK
```

El string search es FALLBACK, no primary. Pero si el template menciona "onboarding" en cualquier contexto futuro, el fallback se activa incorrectamente y el gate `CG-ROI-NEGATIVE` perdona ROI negativo.

**Fix**: Eliminar el fallback de búsqueda de string. Usar solo `pricing_result.is_onboarding`.

---

## V-2 🟠 ALTO: "⚠️ En preparación" en entregables — inconsistencia + typo

**Archivo**: `v4_proposal_generator.py` L.1019, 1047, 1104, 1297

```python
L.1019: estado = "⚠️ En preparación"    # _generate_dynamic_services_table
L.1047: estado = "⚠️ En preparación"    # same
L.1104: estado = "⚠️ En preparación"    # _generate_technical_assets_table
L.1297: return ("⚠️ En preparacion", ...)  # SIN TILDE: _confidence_to_nivel_significado
```

3 instancias con tilde, 1 sin tilde. Mismo archivo, misma semántica. Suena a que el servicio no está listo cuando realmente está "pendiente de datos del cliente".

**Fix**: Cambiar a "En proceso de activación — Semana 2" o vincular al confidence score.

---

## V-3 🟠 ALTO: Jerga técnica filtrada — Gate incompleto + Tabla IAO expuesta al cliente

**Archivos**: `modules/quality_gates/commercial_gate.py` L.85-88; `propuesta_v6_template.md` L.60, 149-158

**Gate `CG-TECH-JARGON`** solo detecta 8 términos: Schema, AEO, IAO, Open Graph, NAP, Rich Snippets, schema.org, JSON-LD, markup estructurado.

**NO detecta**: OpenRouter, Perplexity, Gemini, GA4_PROPERTY_ID, GSC_SITE_URL, UTM, iah-cli, iahotels.co — todos presentes en el documento cliente.

**Tabla de costos IAO** (L.149-158 del template) expone al dueño: nombres de providers, modelo de costos por queries, stubs "—". Detalle de implementación innecesario.

**Fix**: Agregar términos al gate. Mover tabla IAO a anexo técnico.

---

# 🟡 NIVEL 4 — MEDIOS: Issues que completan el paquete comercial

---

## V-4 🟡 MEDIO: "Cupo limitado" sin justificación

**Archivo**: `propuesta_v6_template.md` L.14

```markdown
**Válido por 15 días** (cupo limitado)
```

Copy estático. Sin lógica que controle, justifique o cuantifique el cupo.

**Fix**: Justificar con número ("2 cupos para junio") o eliminar.

---

## V-5 🟡 MEDIO: Garantía no medible sin GA4

**Archivo**: `propuesta_v6_template.md` L.162-163

La promesa de "10% más consultas directas" no tiene mecanismo de medición si el cliente no tiene GA4.

**Fix**: Reformular hacia tracking propio instalado en Día 7.

---

## V-6 🟡 MEDIO: Sin prueba social

No existe sección de testimonios/casos en el template.

**Fix**: Agregar placeholder.

---

## A-2 🟡 MEDIO: Umbral AEO contradictorio (20 vs 30)

**Archivo**: `v4_proposal_generator.py` L.1035 vs L.1235

```python
L.1035: if score_aeo < 20:  # dynamic_services_table
L.1235: if score_aeo < 30:  # asset_quality_table
```

Hotel con score_aeo=25: ve fila AEO en una tabla pero no en la otra. Comportamiento contradictorio.

**Fix**: Unificar a 30 en ambas.

---

# 🟢 NIVEL 5 — BAJOS: Pulido final

---

## A-3 🟢 BAJO: Typo "SIGUIENTE PASSO"

**Archivo**: `propuesta_v6_template.md` L.173

```markdown
## 🚀 SIGUIENTE PASSO: Empezar es simple
```

**Fix**: "PASSO" → "PASO".

---

## B-1 🟢 BAJO: Double pipe `||` en tablas del diagnóstico — columna fantasma

**Archivo**: `v4_diagnostic_generator.py` L.1779

```python
table = """
|| Métrica | Score | Detalle | Estado ||
|---------|-------|---------|--------|
"""
```

El `||` inicial crea columna vacía en render HTML (GitHub, Notion, frontend). No afecta lectura en terminal.

**Fix**: Eliminar pipes extras. Usar `join()` para construir tablas.

---

## OMISIÓN-3 🟢 BAJO (META): Documento original usaba ruta incorrecta para `commercial_gate.py`

El documento referenciaba `commercial_gate.py` sin path. La ruta real es `modules/quality_gates/commercial_gate.py`. Corregido en esta versión.

---

# ✅ LO QUE SÍ ESTÁ BIEN

✅ **CG-ROI-NEGATIVE gate existe** (`modules/quality_gates/commercial_gate.py` L.413-443) — solo hay que sincronizarle los datos de entrada.

✅ **El modelo de 3 escenarios** (conservative 70% / realistic 20% / optimistic 10%) en `config/scenarios.yaml` es internamente consistente.

✅ **La narrativa de pain_ratio + recovery_factor** está bien pensada. El problema no es el modelo — es que diagnóstico y propuesta no comparten la misma filosofía. Diagnóstico muestra fuga bruta, propuesta muestra recuperación efectiva. El gap 12:1 entre ambas es el bug #1.

✅ **El plan 7/30/60/90 días** está bien estructurado y es dinámico por asset_plan.

✅ **Las garantías** (mes a mes, satisfacción, transparencia) son un buen trío reductor de fricción.

✅ **La sección de fotos** es clara y gestiona expectativas.

✅ **Descuentos por pago anticipado** (10% trimestral / 18% semestral) aceleran la decisión.

---

# 📋 CHECKLIST DE EJECUCIÓN (ordenado por prioridad)

## 🔴 Fase 1 — Bloqueantes (el documento NO sale sin esto)

- [ ] **CROSS-1**: Unificar filosofía financiera diagnóstico↔propuesta. Hoy el diagnóstico comunica **fuga bruta** ($22.4M/6m) y la propuesta vende **recuperación efectiva** ($1.8M/6m), generando un gap 12:1 sin puente narrativo.
  - **Decisión requerida de producto**: elegir UNA base financiera principal para todo el paquete comercial antes de tocar código/templates.
  - **Opción A — Diagnóstico orientado a recuperación efectiva**: mantener la fuga bruta como contexto, pero mostrar como cifra principal la recuperación realista recuperable: `raw_loss × pain_ratio × recovery_factor`. Ventaja: alinea expectativa con propuesta y ROI. Riesgo: reduce impacto inicial si no se explica bien la fuga total.
  - **Opción B — Diagnóstico mantiene fuga bruta con advertencia explícita**: conservar "$22.4M de fuga estimada" como headline, pero agregar inmediatamente: "esta es la fuga total; la recuperación contratada proyectada es parcial y depende de prioridad de dolor (41%) y factor de recuperación (20%)". Ventaja: conserva urgencia comercial. Riesgo: requiere copy muy claro para no parecer inflado.
  - **Opción C — Puente dual obligatorio en ambos documentos**: diagnóstico y propuesta muestran siempre dos columnas: "Fuga total estimada" y "Recuperación proyectada con servicio". Mover la nota `41% × 20%` al diagnóstico y repetirla en propuesta como explicación, no como nota menor. Ventaja: máxima transparencia y trazabilidad. Riesgo: más complejidad visual.
  - **Implementación mínima aceptable**: usar Opción C si se quiere preservar impacto comercial sin sacrificar confianza; actualizar diagnóstico, propuesta, escenarios y gate ROI para que todos calculen sobre la misma base.
- [ ] **CROSS-2**: Agregar mapping brecha→servicio en propuesta. Cada servicio indica qué brecha resuelve + costo.
- [ ] **CODE-1/3/4 (unificado)**: Cambiar `recovered_6m` (L796), `net_benefit_6m` (L797) de `projected_monthly_gain` → `effective_monthly_gain`. Así `roi_6m`, `recovered_6m`, `net_benefit_6m` y `total_recovered` quedan en UNA sola base.
- [ ] **CODE-2**: Sincronizar gate `CG-ROI-NEGATIVE` (L345) — pasar `net_benefit_6m` calculado con `effective_monthly_gain`.

## 🟠 Fase 2 — Altos (degradan credibilidad)

- [ ] **CROSS-3**: Corregir escenarios del diagnóstico. Mostrar recuperación neta proyectada, no rango de fuga bruta.
- [ ] **CROSS-4**: Corregir "Botón de WhatsApp | Presente en sitio" → reflejar conflicto + guía incluida.
- [ ] **A-1**: Eliminar fallback de búsqueda de string en `has_onboarding` (L359).
- [ ] **V-2**: Cambiar "⚠️ En preparación" → "En proceso de activación — Semana 2" + unificar tilde.
- [ ] **V-3**: Agregar 8 términos al gate `CG-TECH-JARGON` + mover tabla IAO a anexo técnico.

## 🟡 Fase 3 — Importantes (completan el paquete)

- [ ] **CROSS-5**: Vincular confidence score a cada servicio en tabla de propuesta.
- [ ] **V-4**: Justificar "cupo limitado" o eliminar.
- [ ] **V-5**: Reformular garantía hacia tracking propio (Día 7).
- [ ] **V-6**: Agregar sección de prueba social (placeholder).
- [ ] **A-2**: Unificar umbral AEO a 30 en ambas tablas.

## 🟢 Fase 4 — Pulido (no bloquea envío pero suma)

- [ ] **A-3**: Corregir "PASSO" → "PASO".
- [ ] **B-1**: Eliminar double pipe `||` en `_build_geo_problems_table()`.
- [ ] **CROSS-6**: Hacer que gates NOT_READY bloqueen generación de documentos.

---

# VEREDICTO FINAL

**¿Se puede enviar al dueño de Hotel Castillo Real hoy?**
❌ **NO.** El gap 12:1 entre diagnóstico y propuesta es un destructor de confianza mientras no exista puente dual. El dueño lee que pierde $22M y recibe una oferta para recuperar $1.8M — sin una explicación visible de fuga bruta vs recuperación efectiva. La ruta recomendada es mostrar ambas cifras en diagnóstico y propuesta, con `41% × 20%` como explicación central, no como nota menor. Si a eso se suman 7 brechas sin mapping a servicios, escenarios falsos y contradicciones internas, el paquete sigue siendo comercialmente inviable.

**¿Está cerca de estar lista?**
✅ **SÍ, al 55%.** La estructura de documentos es sólida (plan, garantías, fotos, descuentos). Los bugs de código son puntuales: 4 líneas a cambiar en `v4_proposal_generator.py` + 1 ajuste en el gate. La parte difícil es la **decisión de producto** (CROSS-1): adoptar la ruta recomendada de puente dual — fuga bruta + recuperación efectiva — y hacer que diagnóstico, propuesta, escenarios y gates hablen el mismo idioma financiero.

**Estrategia de ejecución en 3 capas**:

1. **Capa de Producto** (1 decisión): adoptar puente dual obligatorio — **fuga bruta + recuperación efectiva** en ambos documentos. → Define la narrativa recomendada.
2. **Capa de Código** (5 líneas): Unificar 4 variables del template + 1 gate sobre la base de recuperación efectiva, manteniendo fuga bruta como contexto explícito.
3. **Capa de Template** (8 cambios): Agregar bloque comparativo de ambas cifras, mapping brecha→servicio, estados de assets, warnings linkeados y jerga a anexos.

---

*Auditoría: 2026-05-26 (3 iteraciones) | Archivos verificados: 8 código + 2 output + 1 JSON + 12 assets | Hallazgos: 19 total (6 cross-doc, 8 code, 3 template, 2 cosmetic) | 0 paths falsos*
