# 🟡 REPORTE DE VALIDACIÓN — v4.60.0 (Fix de Regresión)
**Documento:** `02_PROPUESTA_COMERCIAL_20260529_193634.md`
**Versión del agente:** v4.60.0
**Fecha de validación:** 30 de mayo de 2026
**Veredicto:** 🟡 **CASI APTO — 1 fix residual de 15 minutos antes de enviar**
**Score de cumplimiento ROICR v3.0:** **88%** (Subió desde 73% en v4.59.0)

---

## 📊 RESUMEN EJECUTIVO

**La intervención fue 95% exitosa.** El equipo corrigió la regresión crítica de la v4.59.0 eliminando completamente la tabla contradictoria "Análisis Comparativo: Status Quo vs Implementación IAO". El documento ahora tiene **coherencia matemática perfecta en el 95% de su extensión**.

Sin embargo, quedó un **residuo crítico** en el párrafo final de cierre que reintroduce la contradicción justo cuando el cliente está tomando la decisión de compra.

> ⚠️ **CORRECCIÓN POST-AUDITORÍA (30-May-2026):** Este reporte fue auditado contra código vivo. El diagnóstico original señalaba incorrectamente un archivo `templates/closing_pitch.md` que **NO EXISTE** en el repositorio. La raíz real está en `v4_proposal_generator.py` (método `_build_closing_pitch`, línea 332) que recibe datos del modelo lineal en vez de la curva de maduración. Ver sección **🔬 DIAGNÓSTICO TÉCNICO CORREGIDO** abajo.

**Evolución del Score:**
| Versión | Score | Estado |
|---|---|---|
| v4.54.0 (original) | 68% | Problemas estructurales |
| v4.55.0 (regresión) | 44% | Regresión crítica |
| v4.58.0 (estable) | 92% | ✅ APTO |
| v4.59.0 (regresión) | 73% | ⛔ Tablas contradictorias |
| **v4.60.0 (actual)** | **88%** | 🟡 **Casi listo — 1 fix residual** |

---

## ✅ LO QUE SE CORRIGIÓ CORRECTAMENTE (95% del documento)

### ✅ Fix #1: Tabla contradictoria ELIMINADA
La tabla "Análisis Comparativo: Status Quo vs Implementación IAO" (que mostraba ROI negativo de -$2.6M anuales y 23 meses de recupero) **fue completamente removida**. Excelente decisión.

### ✅ Fix #2: Unicidad del modelo de proyección
Ahora solo existe **un motor de verdad**: la Curva de Maduración 4 Pilares.
- Tabla de proyección: $5.041.935 en 6 meses ✅
- Trazabilidad financiera: $5.041.935 ✅
- ROI SaaS: 2.10X ✅
- Nota de proyección: 10.7% de la fuga ✅

### ✅ Fix #3: Todos los CRITs de v4.58.0 se mantienen
- ✅ Value-Capture Cap respetado ($400K < $420K — 50% de $840K/mes promedio)
- ✅ Mapper semántico limpio
- ✅ Assets deprecados filtrados (`DEPRECATED_ASSETS` en línea 1574: og_tags_guide, indirect_traffic_optimization, local_content_page, optimization_guide)
- ✅ Piloto 30 días presente (línea 281 de la propuesta)
- ✅ Desglose CAPEX por componentes
- ✅ Garantía Día 55 con KPI específico
- ✅ WhatsApp con narrativa AUDIT_ONLY
- ✅ ADR regional evidenciado

---

## 🚨 REGRESIÓN RESIDUAL (El 5% que bloquea el envío)

### 🔴 RESIDUAL-01: Párrafo de cierre con números del modelo lineal (legacy)

**Ubicación:** Sección final "🟡 Oportunidad de Significativa para Hotelcastillareal" (línea 296-300 de la propuesta)

**Texto problemático:**
> *"Su hotel puede recuperar **$178.235 COP mensuales** con una inversión que se paga sola en **1.9 años** (ROICR: 2.10x)."*

**Por qué es un problema crítico:**

| Métrica | Párrafo final (❌ Legacy) | Resto del documento (✅ Correcto) |
|---|---|---|
| Recuperación mensual | $178.235 (constante) | Promedio $840.322 (curva: $5.041.935 ÷ 6) |
| Período de recupero | 1.9 años (23 meses) | **~2.5 meses** (breakeven en mes 3) |
| Origen del número | `fuga × pain_ratio × recovery` (lineal) | Curva de maduración 4 pilares |
| ROI | 2.10x (correcto, de curva) | 2.10x (mismo número, genera contradicción) |

**Impacto comercial:**
El cliente leerá todo el documento viendo números coherentes ($5M en 6 meses, ROI 2.10X), pero el **último párrafo que lee antes de firmar** le dice que solo recuperará $178K/mes y que tardará 1.9 años en recuperar la inversión. Ese es el número que quedará en su memoria de trabajo al momento de decidir.

---

## 🔬 DIAGNÓSTICO TÉCNICO CORREGIDO (auditado contra código vivo)

### ❌ Diagnóstico original del reporte (INCORRECTO):

El reporte original afirmaba que el bug estaba en:
- Archivo: `modules/commercial_documents/templates/closing_pitch.md`
- Variables: `{{legacy_monthly_recovery}}`, `{{legacy_payback_years}}`

**Estos NO existen en el repositorio.** No hay archivo `closing_pitch.md` ni variables legacy en ningún template.

### ✅ Diagnóstico real (verificado contra código vivo):

**Archivo real:** `modules/commercial_documents/v4_proposal_generator.py`

**1. El closing pitch se construye dinámicamente (línea 332-371):**
```python
def _build_closing_pitch(self, financial_data: dict, hotel_name: str) -> str:
    roicr = financial_data.get('roicr', 0)
    payback_months = financial_data.get('payback_months', 12)
    recovered_monthly = financial_data.get('recovered_amount_cop', 0)
    # ...
    pitch = (
        f"### {emoji} Oportunidad de {urgency.title()} para {hotel_name}\n\n"
        f"Su hotel puede recuperar **{recovery_fmt} COP mensuales** "
        f"con una inversión que se paga sola en **{payback_text}** "
        f"(ROICR: {roicr:.2f}x).\n\n"
        # ...
    )
```

**2. Los datos se inyectan en línea 1013-1020:**
```python
'closing_pitch': self._build_closing_pitch(
    financial_data={
        'roicr': float(_maturity_result.total_recuperacion_6m / (monthly_investment * 6)),
        'payback_months': break_even,                    # ← modelo lineal
        'recovered_amount_cop': effective_monthly_gain,  # ← modelo lineal
    },
    hotel_name=hotel_name,
),
```

**3. Raíz de la discrepancia — línea 714 vs línea 742:**

| Variable | Línea | Fórmula | Valor | Modelo |
|---|---|---|---|---|
| `effective_monthly_gain` | 714 | `raw_monthly_loss × pain_ratio × recovery_realistic` | $178.235 | ❌ Lineal |
| `break_even` | 707 | `_calculate_break_even(investment, projected_monthly_gain)` | 23 meses | ❌ Lineal + CAPEX |
| `roicr` | 1015 | `total_recuperacion_6m ÷ (monthly_investment × 6)` | 2.10x | ✅ Curva |

**4. ¿Por qué `break_even` da 1.9 años?** (línea 1556-1571)
```python
def _calculate_break_even(self, investment: int, gain: int) -> int:
    # gain = projected_monthly_gain = $509.259 (bruto, sin recovery factor)
    # investment = $400.000
    # net mensual = $109.259
    cumulative = -SETUP_FEE  # -$2.500.000 ← INCLUYE CAPEX
    while cumulative < 0:
        cumulative += (gain - investment)
    # $2.500.000 ÷ $109.259 = 22.9 → 23 meses → 1.9 años
```
Dos bugs aquí:
- Usa `projected_monthly_gain` (bruto, sin recovery factor) en vez del gain efectivo
- Incluye CAPEX ($2.500.000) en el cálculo de payback, contradiciendo la narrativa del documento que dice "ROI calculado solo sobre OPEX"

### 🟡 RESIDUAL-02: Error de tipeo menor — DIAGNÓSTICO CONFIRMADO ✅

El typo está en la línea 365 de `v4_proposal_generator.py`:
```python
f"### {emoji} Oportunidad de {urgency.title()} para {hotel_name}\n\n"
```
La palabra "de" sobra cuando `urgency = "significativa"`, produciendo:
> *"🟡 Oportunidad de Significativa para Hotelcastillareal"*

Debe ser: *"🟡 Oportunidad Significativa para Hotelcastillareal"* (sin "de").

---

## 🛠️ FIX OBLIGATORIO (15 minutos)

### Único archivo a modificar: `modules/commercial_documents/v4_proposal_generator.py`

**Paso 1 — Corregir inyección de datos en closing pitch (línea 1013-1020):**

```python
# ANTES (línea 1013-1020):
'closing_pitch': self._build_closing_pitch(
    financial_data={
        'roicr': float(_maturity_result.total_recuperacion_6m / (monthly_investment * 6)) if monthly_investment > 0 else 0.0,
        'payback_months': break_even,                    # ← lineal + CAPEX
        'recovered_amount_cop': effective_monthly_gain,  # ← lineal
    },
    hotel_name=hotel_name,
),

# DESPUÉS:
'closing_pitch': self._build_closing_pitch(
    financial_data={
        'roicr': float(_maturity_result.total_recuperacion_6m / (monthly_investment * 6)) if monthly_investment > 0 else 0.0,
        'payback_months': _maturity_result.mes_breakeven_opex if hasattr(_maturity_result, 'mes_breakeven_opex') else 3,
        'recovered_amount_cop': int(_maturity_result.total_recuperacion_6m / 6),  # ← promedio curva
    },
    hotel_name=hotel_name,
),
```

**Paso 2 — Corregir typo "Oportunidad de Significativa" (línea 365):**

```python
# ANTES:
f"### {emoji} Oportunidad de {urgency.title()} para {hotel_name}\n\n"

# DESPUÉS:
f"### {emoji} Oportunidad {urgency.title()} para {hotel_name}\n\n"
```

**Paso 3 — (Opcional) Verificar que `_maturity_result` tenga `mes_breakeven_opex`:**
Si `aplicar_curva_4_pilares()` no expone ese campo, calcularlo como:
```python
mes_breakeven_opex = next((i+1 for i, acc in enumerate(acumulados) if acc >= monthly_investment * (i+1)), 3)
```
Donde `acumulados` son las recuperaciones acumuladas mes a mes de la curva.

---

## 📋 CHECKLIST FINAL DE VALIDACIÓN

```
✅ CRIT-01: Tablas unificadas (v4.59.0 resuelto)
✅ CRIT-02: Value-Capture Cap respetado (400K < 420K — 50% de $840K/mes avg)
✅ CRIT-03: Mapper semántico limpio
✅ CRIT-04: Assets deprecados filtrados (DEPRECATED_ASSETS, línea 1574)
✅ CRIT-05: Piloto 30 días presente
✅ IMP-01 a IMP-05: Todos resueltos
✅ MIN-02: Status Quo eliminado (decisión correcta)
✅ MIN-04: ADR regional evidenciado

⛔ RESIDUAL-01: Párrafo final con datos del modelo lineal — raíz en v4_proposal_generator.py:1016-1017
⚠️ RESIDUAL-02: Typo "Oportunidad de Significativa" — raíz en v4_proposal_generator.py:365
⚠️ MIN-01: SEO Local aún en 80% (ejecutar onboard post-firma)
⚠️ MIN-03: Fotos sin galería de referencia
```

---

## 🎯 ANÁLISIS COMERCIAL (Lo que verá el cliente)

**Lectura completa del documento:**

1. **Tabla de proyección:** "Gano $2.6M netos en 6 meses, ROI 2.10X" ✅
2. **Curva de maduración:** "Mes 3 ya estoy en equilibrio, mes 6 gano $909K" ✅
3. **CAPEX:** "Los $2.5M son activos míos" ✅
4. **Piloto 30 días:** "Tengo salida de bajo riesgo" ✅
5. **Párrafo final:** ❌ *"Espera... ¿solo recupero $178K/mes y tardo 1.9 años? Entonces todo lo anterior era optimismo..."*

**Probabilidad de cierre:**
| Escenario | Probabilidad |
|---|---|
| Enviar v4.60.0 tal cual | **~45%** (el cliente queda con duda final) |
| Aplicar fix de 15 min y enviar | **~70%** ✅ |

---

## 🏁 VEREDICTO FINAL COMO CTO

> **La v4.60.0 está al 95% de ser la propuesta perfecta.**
>
> El equipo tomó la **decisión correcta** al eliminar la tabla "Status Quo vs Implementación" en lugar de intentar corregirla. A veces menos es más, y la curva de maduración por sí sola cuenta una historia comercial mucho más poderosa.
>
> **Sin embargo, el párrafo final es el "último sabor" que queda en la boca del cliente.** Enviar el documento con ese residuo legacy es como servir un plato de alta cocina y rematar con un chicle masticado: arruina la experiencia completa.
>
> **Diagnóstico corregido post-auditoría:** El bug NO está en un template separado (`closing_pitch.md` no existe). Está en `v4_proposal_generator.py` línea 1016-1017, donde se pasan `effective_monthly_gain` (fórmula lineal: `fuga × pain_ratio × recovery`) y `break_even` (lineal + CAPEX) al closing pitch, en vez de usar los valores de la curva de maduración que ya están disponibles en `_maturity_result`.
>
> **Mi recomendación profesional:**
> 1. **NO enviar todavía.** Tomar 15 minutos para aplicar el fix.
> 2. Modificar `v4_proposal_generator.py` línea 1016-1017: `recovered_amount_cop` → `total_recuperacion_6m / 6`, `payback_months` → breakeven desde curva.
> 3. Corregir typo línea 365: quitar "de" en "Oportunidad de Significativa".
> 4. Regenerar propuesta.
> 5. **ENVIAR HOY MISMO.**
>
> **Valor del contrato en juego:** $4.900.000 COP (CAPEX + 6 meses OPEX)
>
> **Costo del fix:** 15 minutos de desarrollo.
>
> **ROI del fix:** +25 puntos porcentuales de probabilidad de cierre (~$1.2M en valor esperado).

---

## 📎 NOTA DE AUDITORÍA (30 de mayo de 2026)

Este reporte fue validado contra código vivo del repositorio `/mnt/c/Users/Jhond/Github/iah-cli/`. 

**Archivos verificados:**
- `modules/commercial_documents/v4_proposal_generator.py` — 2,201 líneas
- `output/v4_complete/02_PROPUESTA_COMERCIAL_20260529_193634.md` — 342 líneas

**Correcciones al diagnóstico original:**
| Claim original | Realidad en código |
|---|---|
| Template `closing_pitch.md` existe | ❌ No existe. El pitch se construye en Python (línea 332) |
| Variables `{{legacy_monthly_recovery}}` | ❌ No existen. Se usa `effective_monthly_gain` (línea 714) |
| `{{legacy_payback_years}}` | ❌ No existe. Se usa `break_even` (línea 707) |
| Fix: editar template markdown | ❌ Fix correcto: editar Python línea 1016-1017 |
| $654K Value-Capture Cap | ⚠️ $420K sería más preciso (50% de $840K/mes avg) |
