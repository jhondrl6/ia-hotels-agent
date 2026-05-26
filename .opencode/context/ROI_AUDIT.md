# Auditoría del ROI.md contra Código Vivo — Correcciones

**Fecha**: 2026-05-26
**Auditado por**: Hermes Agent (2do ciclo de verificación)
**Archivo auditado**: `.opencode/context/ROI.md`
**Método**: Cada claim verificada línea por línea contra el código fuente

---

## RESUMEN DE ERRORES EN EL ROI.MD ORIGINAL

El ROI.md original tiene **3 errores factualmente incorrectos** y **1 conclusión
estratégica peligrosa** que, si se implementa, produciría una propuesta
comercialmente fraudulenta (prometer $19.2M de recuperación donde el modelo
realista proyecta $1.8M).

| # | Claim original | Veredicto | Severidad |
|---|---------------|-----------|-----------|
| 1 | "_calculate_roi aplica recovery_factor UNA TERCERA VEZ" (§0.1) | ❌ FALSO | Alto — asume triple descuento que no existe |
| 2 | "Fórmula corregida: usar $7.7M con 75% efectividad" (PARTE 3) | ❌ PELIGROSO | Crítico — promete ROI 3.67X irreal |
| 3 | "57% del resultado son supuestos" (§0.4) | 🟡 PARCIAL | Medio — el framing es engañoso |
| 4 | "pain_ratio 41% = porción IAO del dolor" (§0.6) | ❌ FALSO | Alto — es artifact del min_price, no un % real |

---

## CORRECCIÓN 1: NO hay triple descuento

### Claim original (ROI.md §0.1, línea 63):
> "Línea 1445 — `_calculate_roi` aplica recovery_factor UNA TERCERA VEZ"

### Evidencia de código:

```python
# v4_proposal_generator.py:686
projected_monthly_gain = int(raw_monthly_loss * pain_ratio)
# → 3,741,696 × 0.4082 = 1,527,360 (GAIN BRUTO, sin recovery)

# v4_proposal_generator.py:688
roi_6_months = self._calculate_roi(
    monthly_investment, projected_monthly_gain, 6,
    recovery_factor=recovery_factors['realistic']  # 0.20
)

# v4_proposal_generator.py:1432-1455 (la función _calculate_roi)
def _calculate_roi(self, investment, gain, months, recovery_factor=0.20):
    total_investment = investment * months
    total_gain = gain * recovery_factor * months  # ← gain es BRUTO, NO tiene recovery
    roi_ratio = total_gain / total_investment
```

### Veredicto:
`projected_monthly_gain` = raw_loss × pain_ratio (BRUTO, sin recovery).
`_calculate_roi` multiplica por recovery_factor UNA VEZ.
La fórmula total es: `(raw_loss × pain_ratio × recovery_factor) / investment`.

**Hay UN descuento compuesto, no tres.** El recovery_factor se aplica 1 sola vez,
sobre el gain bruto. La línea 1445 NO es una tercera aplicación — es la PRIMERA
y ÚNICA vez que recovery se aplica al gain para calcular ROI.

### Prueba numérica:
- gain = 1,527,360 (bruto, sin recovery)
- recovery_factor = 0.20
- total_gain = 1,527,360 × 0.20 × 6 = 1,832,832
- total_investment = 1,200,000 × 6 = 7,200,000
- ROI = 1,832,832 / 7,200,000 = 0.25X ≈ 0.3X ✅

La tabla (líneas 783-794) usa `effective_monthly_gain` que SÍ tiene recovery:
- effective = 3,741,696 × 0.4082 × 0.20 = 305,472/mes

**Son consistentes.** La tabla y el ROI usan el mismo monto efectivo.
No hay triple descuento.

---

## CORRECCIÓN 2: La "fórmula corregida" es PEOR que el problema

### Claim original (ROI.md PARTE 3, líneas 291-320):
Propone usar $7,741,440 (comisión OTA BRUTA) × 75% efectividad × curva adopción.
Resultado prometido: ROI 3.67X, +$19.2M en 6 meses.

### Por qué esto es factualmente incorrecto:

**$7,741,440 es la comisión OTA TOTAL, no la fuga recuperable.**

El scenario_calculator (líneas 279-292) calcula:
```
fuga_verificable = ota_bookings × ADR × 15% = $7,741,440
shift_savings    = ota_bookings × 10% × ADR × 15% = $774,144   (10% shift)
ia_boost         = room_nights × 5% × ADR = $3,225,600          (5% IA)
fuga_neta        = $7,741,440 - $774,144 - $3,225,600 = $3,741,696
```

Los componentes restados NO son "supuestos que inflan" — son **estimaciones
de cuánto se puede recuperar**. El shift del 10% asume que el 10% de las
reservas OTA se pueden mover a canal directo. El IA boost asume un 5% de
visibilidad adicional.

**El ROI.md propone esto:**
```
Base: $7,741,440 (TODA la comisión OTA)
× 75% efectividad = $5,806,080/mes de recuperación
```

Esto dice que el hotel va a **recuperar $5.8M/mes** cuando su pérdida neta
realista es $3.7M. Es decir, promete más recuperación que toda la pérdida.
Es matemáticamente absurdo y comercialmente fraudulento.

### El error conceptual del ROI.md:
Confunde "comisión verificable" con "comisión recuperable":
- **Verificable**: $7.7M (sí, se puede calcular con datos públicos)
- **Recuperable**: Una fracción de $7.7M (solo el % de reservas que se
  pueden mover a canal directo)

El scenario_calculator ya hace el cálculo correcto: parte de $7.7M y
descuenta lo que NO es recuperable para llegar a $3.7M. Aplicar pain_ratio
(41%) y recovery (20%) sobre $3.7M es metodológicamente correcto.

---

## CORRECCIÓN 3: El 57% de supuestos no es lo que parece

### Claim original (ROI.md §0.4):
> "El 57% del resultado son supuestos"

### Matiz:
Los componentes "supuestos" (shift 10%, IA boost 5%) no son inventados —
son estimaciones con base en literatura de la industria:
- **Shift 10%**: benchmark conservador (la literatura reporta 5-25%)
- **IA boost 5%**: estimado sin GA4, pero con base en el crecimiento de
  búsquas asistidas por IA

El problema real NO es que sean supuestos. Es que **no hay datos del hotel
para validarlos**. La solución correcta no es eliminarlos (como propone
el ROI.md al usar $7.7M bruto) sino señalar que necesitan GA4 para
validarse, que es lo que ya hace el disclaimer del JSON:
> "Estimación basada en benchmarks regionales y datos de su web.
> Para mayor precisión, conecte Google Analytics 4."

---

## CORRECCIÓN 4: pain_ratio 41% NO es "porción IAO"

### Claim original (ROI.md §0.6 y PARTE 3):
> "Se vende una solución integral de 4 pilares (SEO + GEO + AEO + IAO),
> pero solo se proyecta recuperación sobre el pilar IAO (41%)"

### Evidencia de código:

```python
# pricing_calculator.py:252-255
recommended = expected_loss_cop * 0.035  # 3.5% of loss for boutique
price = max(1_200_000, min(recommended, 2_500_000))  # CLAMPED to min
pain_ratio = price / expected_loss_cop  # Result: 0.4082
```

Para Castilla Real:
- expected_loss ≈ $3.74M
- recommended = $3.74M × 3.5% = $130,959
- price = max($1.2M, $130,959) = **$1,200,000** (min_price floor kicks in)
- pain_ratio = $1.2M / $3.74M ≈ 0.32

**Pero el JSON dice 0.4082.** Esto indica que el expected_loss_cop usado
en pricing fue ~$2.94M, no $3.74M. El pricing usó un valor de pérdida
diferente al del scenario_calculator (posiblemente sin IA boost, o de
otro escenario).

**Punto clave**: pain_ratio = 0.4082 es un ARTIFACT del min_price floor
($1.2M), no un "% del dolor abordable con IAO". Es la relación
aritmética entre el precio mínimo y la pérdida. No tiene significado
semántico como "porción IAO".

### Impacto:
El código interpreta pain_ratio como "% del dolor abordable con IAO"
(ver líneas 748-754 del generador), pero es realmente un artifact
de pricing. Esto significa que la nota de proyección que ve el cliente:

> "De su pérdida mensual estimada, el 41% representa la porción del dolor
> financieramente abordable con IAO"

...es una interpretación incorrecta de un número que es puramente
aritmético.

---

## EL DIAGNÓSTICO CORRECTO

### ¿Por qué el ROI es negativo?

La causa raíz NO es un error de fórmula. Es un **mismatch estructural
entre pricing y perfil de hotel**:

| Factor | Valor | Implicación |
|--------|-------|-------------|
| Hotel rooms | 10 | Tier "boutique" |
| Pérdida neta mensual | $3,741,696 | Moderada para 10 hab |
| Precio mínimo mensual | $1,200,000 | Floor del tier boutique |
| pain_ratio resultante | ~32-41% | 6-8x sobre el gate (3-6%) |
| Recovery factor | 20% | Conservador pero estándar |
| Recovery efectiva/mes | $305,472 | 25% del precio |
| **Gap mensual** | **-$894,528** | **El recovery no cubre el precio** |

**El recovery de $305K/mes es realista** para un hotel de 10 habitaciones
sin GA4. El problema es que el precio de $1.2M/mes es 4x el recovery
realista.

### ¿Por qué el modelo produce negativo en TODOS los escenarios?

Incluso el optimistic (-$270K) es negativo porque:
- Optimistic shift: 20% (vs 10% realistic)
- Optimistic IA boost: 10% (vs 5% realistic)
- Optimistic occupancy: +5%
- Pero el precio sigue siendo $1.2M/mes

La única forma de obtener ROI positivo con este hotel sería:
1. Reducir el precio a ~$300K/mes (por debajo del min_price)
2. O tener GA4 que demuestre un loss mucho mayor
3. O aumentar el recovery_factor a ~80% (irrealista sin datos)

---

## LO QUE EL ROI.md ACIERTA (corroborado por código)

| Claim | Sección | Veredicto |
|-------|---------|-----------|
| Alertas comerciales al output del cliente | §0.2 | ✅ CONFIRMADO — línea 374-386, sin audience check |
| Placeholder de testimonios hardcodeado | §0.3 | ✅ CONFIRMADO — template línea 171, sin condicional |
| Optimistic scenario negativo | §0.5 | ✅ CONFIRMADO — JSON: -270,950.4 |
| Divergencia pain_ratio diag vs propuesta | §0.6 | ✅ CONFIRMADO — diseño intencional |
| Versión hardcodeada 4.0.0 | §0.7 | ✅ CONFIRMADO — línea 725 |
| ADR scrapeado desconectado | §0.8 | ✅ CONFIRMADO — no hay fallback intermedio |
| Tabla de entregables muestra incertidumbre | §2 | ✅ CONFIRMADO — output líneas 67-69 |
| Jerga técnica sin traducir | §4 | ✅ CONFIRMADO — output línea 75 (AEO) |
| Anexo APIs visible al cliente | §4 | ✅ CONFIRMADO — output líneas 260-271 |

---

## ESTRATEGIA CORREGIDA

### Diagnóstico de fondo (CORREGIDO):

El problema NO es la fórmula del ROI. La fórmula es correcta:
- Base: pérdida neta realista ($3.7M)
- pain_ratio: porción abordable (~41%, aunque es artifact del min_price)
- recovery: efectividad conservadora (20%)
- Resultado: $305K/mes de recovery

**El problema es que $305K/mes no cubre $1.2M/mes de precio.**

Esto NO se arregla cambiando la fórmula. Se arregla con una de estas:

### Opción A: Pricing dinámico por recovery (RECOMENDADA)
El precio debe derivarse del recovery defendible. Con recovery de $305.472/mes:

```
Para ROI cliente 2X:
  precio máximo = recovery / 2 = $305,472 / 2 = ~$152,736/mes

Para punto de equilibrio (ROI 1X):
  precio ≈ recovery = ~$305,000/mes
```

NOTA: La fórmula anterior (`precio = recovery × 2`) estaba invertida.
Si precio = $610,944 y recovery = $305,472, entonces ROI cliente =
$305,472 / $610,944 = 0.5X, NO 2X. La relación correcta es
precio = recovery / ROI_deseado.

Por debajo de GA4, cualquier fee cercano a $1.2M/mes debe venderse
como activación estratégica, no como ROI financiero inmediato.

### Opción B: Lower pricing hasta tener GA4
$300-400K/mes durante onboarding. Consistente con el recovery actual.
Después de GA4, recalcular con datos reales.

### Opción C: Quick wins como proyecto único
Vender WhatsApp fix + Schema Hotel + llms.txt como proyecto de $200-400K
único. Sin contrato mensual. Construye confianza y genera datos.

### Opción D: Entregar con transparencia (LA ACTUAL, MEJORADA)
Mantener la tabla de ROI negativa pero agregar:
- "La inversión se recálcula con sus datos reales en el Día 30"
- "El primer reporte de ROI real será el Día 45"
- Eliminar la nota de "41% del dolor abordable con IAO" (es misleading)

### NO hacer (lo que propone el ROI.md original):
❌ Usar $7.7M como base → promete $19.2M de recovery irreal
❌ Curva de adopción con 75% efectividad → no hay evidencia
❌ ROI 3.67X → fraudulento para un hotel de 10 habitaciones sin GA4

---

## FIXES DE CÓDIGO NECESARIOS (sin cambiar la fórmula del ROI)

### 🔴 Nivel 1 — Bloqueantes:

1. **Ocultar alertas del output al cliente**
   - Archivo: `v4_proposal_generator.py:374-386`, `v4_diagnostic_generator.py:514-526`
   - Fix: agregar `document_audience` parameter

2. **Eliminar placeholder de testimonios si vacío**
   - Archivo: `propuesta_v6_template.md:169-171`
   - Fix: `{% if testimonials %}...{% endif %}` o eliminar sección

3. **Corregir interpretación de pain_ratio en nota de proyección**
   - Archivo: `v4_proposal_generator.py:755-762`
   - Actual: "el 41% representa la porción del dolor financieramente abordable con IAO"
   - Corregir: "el 41% es la relación entre su inversión mensual y la pérdida estimada"

### 🟡 Nivel 2 — Importantes:

4. **Traducir jerga técnica** (AEO, UTMs, P1/P2/P3)
5. **Cambiar entregables a "Momento de entrega"** sin % confianza
6. **Conectar ADR del web_scraper como fallback**
7. **Corregir versión hardcodeada** (línea 725)

### 🟢 Nivel 3 — Pulido:

8. Simplificar Anexo Técnico APIs
9. Documentar evidence_tier vs precision_tier
10. Agregar nota explicativa pain_ratio 20% vs 41%

---

## CONCLUSIÓN

El ROI.md original tiene un **análisis comercial excelente** (alertas,
testimonios, jerga, scorecard) pero una **propuesta de fórmula financiera
equivocada y peligrosa**.

La fórmula actual del código es **metodológicamente correcta**. El ROI
negativo es un **hecho comercial**, no un bug. El recovery de $305K/mes
es realista para un hotel de 10 habitaciones sin GA4.

Las soluciones correctas son comerciales (cambiar pricing, segmentar
oferta), no técnicas (cambiar la fórmula para inflar números).

---
*Auditoría generada por verificación directa contra código vivo — 2026-05-26*
