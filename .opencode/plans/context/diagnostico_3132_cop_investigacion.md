# Diagnóstico $3,132,000 COP — Investigación Completa
## Amaziliahotel | 2026-04-10 | Actualizado post-FASE-G (2026-04-11)

---

## 0. Estado Post-FASE-G (RESUMEN DE AVANCE)

### Fases ejecutadas (Opción C — Rediseño completo)

| Fase | Estado | Qué hizo | Fecha |
|------|--------|----------|-------|
| FASE-A | ✅ | `FinancialBreakdown` dataclass + `EvidenceTier` enum + `Scenario.monthly_loss_central` | 2026-04-10 |
| FASE-B | ✅ | `ScenarioCalculator.calculate_breakdown()` por capas | 2026-04-11 |
| FASE-C | ✅ | Pesos normalizados (suma=100%) + `DynamicImpactCalculator` | 2026-04-11 |
| FASE-D | ✅ | Scraper→ADR con `WEB_SCRAPING` como fuente | 2026-04-11 |
| FASE-E | ✅ | 22 consumidores actualizados de `max` a `central` | 2026-04-11 |
| FASE-F | ✅ | Template narrativa Comisión OTA + evidence tiers | 2026-04-11 |
| FASE-G | ✅ | Integración `main.py` + validación E2E | 2026-04-11 |
| FASE-H | ✅ | `RegionalADRResolver` activado SHADOW + parcheo `precio_promedio` + occupancy regional | 2026-04-11 |

### Verificación E2E (Amaziliahotel, 2026-04-11)

- Exit code: 0
- Valor central: $2,610,000 COP (realistic, no inflado x1.2)
- Comisión OTA visible: $5,400,000 (en breakdown)
- Evidence tier: "C" con disclaimer completo
- Breakdown con 7 data_sources rastreables
- 453 tests pasados, 0 failures
- Commit: `5171ce4`

### HALLAZGO NUEVO: $300.000 ADR es HARDCODE, no usa benchmarks regionales

El ADR de Amaziliahotel ($300.000) NO viene de benchmarks ni scraping.
Viene de `LEGACY_DEFAULT_ADR = 300000.0` en `adr_resolution_wrapper.py:45`.

El archivo `data/benchmarks/plan_maestro_data.json` SÍ tiene ADR por región:
- eje_cafetero: $330.000
- antioquia: $280.000
- caribe: $410.000

Pero `RegionalADRResolver` está **desactivado** por feature flag:
```python
# feature_flags.py:30
regional_adr_enabled: bool = False  ← APAGADO
```

**Consecuencia**: De 4 datos de entrada, solo rooms=10 es real. ADR ($300K), occupancy (50%), y direct_channel (20%) son defaults.
El $2.610.000 es correcto aritméticamente pero construido sobre datos genéricos, no datos del hotel.

### GAPs residuales post-FASE-H

| # | GAP | Severidad | Estado |
|---|-----|-----------|--------|
| G1 | ADR regional activado en SHADOW | ALTA | ✅ RESUELTO — resolver parcheado, lee `precio_promedio` de `v25_config.regiones` |
| G2 | Occupancy regional disponible vía `resolve_occupancy()` | ALTA | ✅ RESUELTO — método añadido a `RegionalADRResolver` |
| G3 | Supuestos de mejora (10% shift, 5% IA boost) hardcodeados sin evidencia | MEDIA | Sin cambios — Evidence tier C lo reconoce |
| G4 | Promoción a ACTIVE pendiente | ALTA | ⚠️ PENDIENTE — Caribe muestra 36.7% diff (mercado real, no error). Activar vía `.env`: `FINANCIAL_REGIONAL_ADR_ENABLED=True` + `FINANCIAL_REGIONAL_ADR_MODE=active` |
| G5 | Generadores aceptan `financial_breakdown` pero no lo consumen internamente aún | BAJA | Sin cambios |
| G6 | Integración occupancy regional en `main.py` fallback path | MEDIA | GAP MENOR — resolver tiene el método, integración en flujo pendiente |

---

## 2. Cadena Completa del Flujo (de cálculo a presentación)

### PASO 1 — Cálculo original (CORRECTO)
- Archivo: `modules/financial_engine/scenario_calculator.py` línea 222
- Fórmula: `monthly_loss = current_ota_commission_loss - savings - ia_visibility_boost`
- Resultado: `monthly_loss_cop = 2,610,000`

### PASO 2 — Guardado en JSON (CORRECTO)
- Archivo: `main.py` línea 1664 → `expected_monthly = calc_result.get_realistic_loss()` → 2,610,000
- Archivo: `main.py` línea 1715 → se guarda como `expected_monthly_cop: 2610000.0` en `financial_scenarios.json`
- Verificado: `output/v4_complete/financial_scenarios.json` contiene `"realistic": 2610000.0`

### PASO 3 — Construcción del Scenario dataclass (DONDE SE INFLA x1.2)
- Archivo: `main.py` líneas 1875-1894
- Código exacto:
```python
financial_scenarios_obj = FinancialScenarios(
    conservative=Scenario(
        monthly_loss_min=conservative_value,
        monthly_loss_max=int(conservative_value * 1.2),  # techo conservador
        probability=0.70,
        description="Peor caso plausible",
        monthly_opportunity_cop=0),
    realistic=Scenario(
        monthly_loss_min=int(realistic_value * 0.8),     # 2,088,000 (piso)
        monthly_loss_max=int(realistic_value * 1.2),     # 3,132,000 (techo) ← BUG CONSUMO
        probability=0.20,
        description="Meta esperada",
        monthly_opportunity_cop=0),
    optimistic=Scenario(
        monthly_loss_min=int(optimistic_value * 0.8) if optimistic_value > 0 else int(optimistic_value * 1.2),
        monthly_loss_max=optimistic_value,
        probability=0.10,
        description="Mejor caso",
        monthly_opportunity_cop=optimistic_opportunity)
)
```
- El spread +/-20% es razonable como rango. El problema es el consumo del techo.

### PASO 4 — Consumo en el diagnóstico (USA TECHO COMO PRINCIPAL)
- Archivo: `modules/commercial_documents/v4_diagnostic_generator.py`
- Líneas exactas donde se consume `monthly_loss_max`:

| Línea | Variable | Contexto |
|-------|----------|----------|
| 471 | `main_scenario_amount` | Título del impacto financiero |
| 442 | `loss_6_months_value = main.monthly_loss_max * 6` | Proyección 6 meses (también inflada) |
| 551 | `monthly_loss` | Template V6: "Pérdida estimada mensual: $3.132.000 COP" |
| 897 | `empathy_message` | Mensaje de empatía comercial |

### PASO 5 — Costo por brecha (TAMBIÉN usa techo)
- Archivo: `v4_diagnostic_generator.py` líneas 1547-1556
```python
def _get_brecha_costo(self, audit_result, financial_scenarios, index):
    brechas = self._identify_brechas(audit_result)
    if index < len(brechas):
        main = financial_scenarios.get_main_scenario()
        proportion = brechas[index].get('impacto', 0.25)
        costo = main.monthly_loss_max * proportion  # ← techo x peso = costo inflado
        return format_cop(costo)
    return format_cop(0)
```

### PASO 6 — Recuperación por brecha (TAMBIÉN usa techo)
- Mismo patrón en `_get_brecha_recuperacion` línea 1582-1590

---

## 3. Pesos de Brechas: Hardcoded y No Normalizados

### Origen: `_identify_brechas()` líneas 1770-1910

| # | Brecha | Peso hardcoded | Condición de detección |
|---|--------|---------------|------------------------|
| 1 | Visibilidad GBP/GEO | 30% | `gbp.geo_score < 60` |
| 2 | Sin Schema Hotel | 25% | `not schema.hotel_schema_detected` |
| 3 | Sin WhatsApp | 20% | `not phone_web and not whatsapp_html` |
| 4 | Web Lenta | 15% | `mobile_score < 70` |
| 5 | Conflictos Datos | 10% | `whatsapp_status == CONFLICT` |
| 6 | Metadata Defaults | 10% | `metadata.has_issues` |
| 7 | Falta Reviews | 10% | `gbp.reviews < 10` |
| 8 | Sin FAQ Schema | 12% | `not schema.faq_schema_detected` |
| 9 | Sin Open Graph | 8% | `not seo_elements.open_graph` |
| 10 | Contenido no citable | 10% | `citability.overall_score < 30` |

### Problemas:
- **Suma máxima posible: 150%** (todas las condiciones pueden cumplirse simultáneamente)
- **Ningún peso se deriva de datos reales** (GSC, GA4, benchmarks)
- **No hay normalización** — si detectan 4 brechas con pesos [25,12,10,8]=55%, el 45% queda sin asignar
- **El ordenamiento es por peso** (línea 1908: `brechas.sort(key=lambda x: x.get('impacto', 0), reverse=True)`) pero los pesos son arbitrarios

### En el caso Amaziliahotel:
Se detectaron 4 brechas: Schema Hotel (25%), FAQ (12%), Metadata (10%), Open Graph (8%)
- Suma: 55%
- $3,132,000 × 0.55 = $1,722,600 explicados
- $3,132,000 × 0.45 = $1,409,400 SIN EXPLICAR en el documento

---

## 4. Módulo Existente NO Utilizado: DynamicImpactCalculator

### Archivo: `modules/utils/dynamic_impact.py` (307 líneas)

Este módulo YA TIENE la lógica correcta para impacto dinámico:

- **Datos que usa**: reservas_mes, valor_reserva, canal_directo, revpar_regional
- **Fuentes**: hotel_data (input) → benchmarks regionales → defaults
- **Factores por issue type**: PERFIL_NO_RECLAMADO=1.0, FOTOS_INSUFICIENTES=0.35, etc.
- **Cálculo real**: `base_loss = factor * indirect_channel_share * reservas_mes * valor_reserva`
- **ConfidenceTracker**: tracking de fuente de cada dato (HOTEL_INPUT vs PLAN_MAESTRO_JSON)

**Pero el generador de diagnóstico NO lo usa.** Sigue consumiendo `_identify_brechas()` hardcoded.

---

## 5. Fallas Estructurales (Resumen)

| # | Falla | Severidad | Impacto en el cliente |
|---|-------|-----------|----------------------|
| F1 | Inflación 20% sistemática | ALTA | Cifra engañosa, pierde credibilidad si el hotelero verifica |
| F2 | Pesos sin base empírica | ALTA | Atribución incorrecta de prioridades |
| F3 | Suma puede superar 100% | MEDIA | Inconsistencia matemática visible |
| F4 | 45% de pérdida sin explicar | ALTA | El cliente pregunta "¿y el resto?" y no hay respuesta |
| F5 | DynamicImpactCalculator ignorado | MEDIA | Solución parcial ya existe pero no está conectada |
| F6 | Sin trazabilidad del cálculo | ALTA | Imposible auditar el número ante un tercero |

---

## 6. Propuesta: Método de Impacto Proporcional con Evidence Tiers

### Principio 1 — Valor central, no techo
```
monthly_loss = realistic_value  (sin x1.2)
monthly_loss_range = [realistic * 0.8, realistic * 1.2]  (solo para escenarios)
```

### Principio 2 — Pesos normalizados al 100%
```
peso_bruto = brecha.impacto  (de _identify_brechas o DynamicImpactCalculator)
suma_brutos = sum(peso_bruto for brecha in brechas_detectadas)
peso_normalizado = peso_bruto / suma_brutos  # garantiza suma = 100%
costo_brecha = monthly_loss * peso_normalizado
```

### Principio 3 — Evidence Tiers en YAML header
```yaml
financial_evidence_tier: A|B|C  # A=GA4+GSC, B=benchmarks, C=solo scraping
financial_source: financial_scenarios.json#realistic
financial_value_central: 2610000
financial_value_range: [2088000, 3132000]
financial_method: proportional_normalized
```

### Principio 4 — Conectar DynamicImpactCalculator
- Si hay hotel_data o benchmarks → usar DynamicImpactCalculator para pesos
- Si no → fallback a _identify_brechas() pesos hardcoded pero normalizados
- Escalera: hotel_data > benchmarks > hardcoded

### Principio 5 — Sección de brecha no atribuida eliminada
- Con pesos normalizados, la suma siempre es 100%
- Ya no hay porción "sin explicar"

---

## 7. Archivos a Modificar (mapa completo)

| Archivo | Cambio requerido | Prioridad |
|---------|-----------------|-----------|
| `main.py:1884` | Cambiar a `monthly_loss_max=realistic_value` (sin x1.2) o bien crear campo `monthly_loss_central` | P1 |
| `v4_diagnostic_generator.py:551` | Consumir valor central en vez de `monthly_loss_max` | P1 |
| `v4_diagnostic_generator.py:471` | Ídem | P1 |
| `v4_diagnostic_generator.py:442` | Ídem (proyección 6 meses) | P1 |
| `v4_diagnostic_generator.py:897` | Ídem (empathy message) | P1 |
| `v4_diagnostic_generator.py:1554` | Cambiar a valor central + peso normalizado | P1 |
| `v4_diagnostic_generator.py:1588` | Ídem (_get_brecha_recuperacion) | P1 |
| `v4_diagnostic_generator.py:1770-1910` | Normalizar pesos de _identify_brechas() | P1 |
| `data_structures.py` | Agregar campo `monthly_loss_central` a Scenario | P1 |
| `v4_diagnostic_generator.py` | Integrar DynamicImpactCalculator como fuente de pesos | P2 |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Agregar evidence tier disclaimer | P2 |
| `coherence_validator.py:433` | Ajustar validación si cambia estructura de Scenario | P2 |
| `asset_diagnostic_linker.py:498-504` | Ajustar cálculo de impacto por asset | P2 |

---

## 8. Datos del Caso de Prueba (Amaziliahotel) — ACTUALIZADO post-FASE-G

```
hotel: Amaziliahotel
url: https://amaziliahotel.com
region: eje_cafetero
rooms: 10           (fuente: hotel_data — DATO REAL)
adr_cop: 300,000    (fuente: legacy_hardcode — NO ES DATO DEL HOTEL)
                   (plan_maestro eje_cafetero = $330,000 — NO SE USA)
                   (RegionalADRResolver DESACTIVADO por feature flag)
occupancy_rate: 0.5 (fuente: default — NO ES DATO DEL HOTEL)
direct_channel: 0.2 (fuente: default — NO ES DATO DEL HOTEL)

Escenarios (financial_scenarios.json):
  conservative: $5,076,000
  realistic:    $2,610,000  ← Valor central (monthly_loss_central)
  optimistic:   -$189,000

Valor mostrado en documento: $2,610,000 (ANTES: $3,132,000 inflado x1.2)
Inflación x1.2: ELIMINADA (FASE-E cambió consumo de max a central)

Breakdown (NUEVO — FASE-G):
  ota_commission_cop: $5,400,000 (verificable: 120 noches × $300K × 15%)
  shift_savings_cop: $540,000 (10% OTA→directo, supuesto sin GA4)
  ia_revenue_cop: $2,250,000 (5% boost IA, supuesto sin GA4)
  evidence_tier: "C"
  data_sources: adr=legacy_hardcode, rooms=hotel_data, occupancy=default,
                direct_channel=default, shift=hardcoded, ia_boost=estimado

coherence_score: 0.91
commit: 5171ce4 (2026-04-11)
```

---

## 9. Notas para la sesión de planificación

1. **Prioridad comercial**: El cliente ve "$3,132,000" como cifra exacta. Si pregunta "¿cómo llegaron a ese número?", no hay respuesta rastreable. Esto afecta credibilidad del producto.

2. **El fix mínimo viable** es: cambiar `monthly_loss_max` por valor central + normalizar pesos. No requiere tocar el motor financiero.

3. **El fix completo** integra DynamicImpactCalculator. Eso ya existe, solo falta conectarlo.

4. **No romper tests**: Hay 1782 funciones de test. Los cambios en `data_structures.py` (agregar campo) y `main.py` (cálculo de Scenario) pueden impactar. Verificar con `python -m pytest` post-cambio.

5. **coherence_validator.py línea 433** valida precio vs pain usando `monthly_loss_max`. Si se cambia el campo, ajustar la validación.

6. **El template V6** tiene 4 slots fijos (`brecha_1` a `brecha_4`) pero también `brechas_section` dinámico. Ambos consumen el mismo `_get_brecha_costo`. El fix en la función centraliza el cambio.

7. **impacto_cop en coherence**: El coherence_validator usa `main.monthly_loss_max` para el ratio pain/precio. Cambiar a valor central afecta este ratio. Verificar que siga pasando el gate de 0.8.

---

## 10. Hallazgo Crítico: El Problema Conceptual de la Fórmula

### 10.1 La fórmula NO calcula "pérdida" — calcula "pérdida neta después de mejora hipotética"

El documento dice "Pérdida estimada mensual: $2,610,000 COP" (o $3,132,000 inflado).
Pero la fórmula real del ScenarioCalculator (`scenario_calculator.py` líneas 202-222) es:

```
Pérdida presentada = comisión_OTA_actual - ahorro_shift_OTA - boost_visibilidad_IA
```

Con los datos de Amaziliahotel:

```
$5,400,000   ← Comisión OTA actual (VERIFICABLE: 120 noches × $300K × 15%)
- $540,000   ← SUPUESTO: 10% de clientes OTA migra a directo
- $2,250,000 ← SUPUESTO: IA genera 5% más reservas directas
= $2,610,000 ← Se presenta como "pérdida estimada mensual"
```

### 10.2 Los dos supuestos son completamente inventados

| Supuesto | Valor en fórmula | Origen | Sensibilidad |
|----------|-----------------|--------|-------------|
| 10% shift OTA→directo | `moderate_shift = 0.10` (línea 215) | Hardcodeado sin evidencia | Si fuera 5%: resultado = $2,835,000 (+$225K) |
| 5% boost IA bookings | `ia_visibility_boost` (línea 220) | Hardcodeado sin evidencia | Si fuera 3%: resultado = $2,010,000 (-$600K) |

El boost IA ($2,250,000) representa el **43% del resultado final** y es el supuesto más débil.
No hay evidencia empírica de que mejorar Schema/FAQ genere 5% más reservas directas.

### 10.3 El número VERIFICABLE nunca aparece en el documento

La comisión OTA actual ($5,400,000/mes) es un dato verificable:
- Habitaciones: dato del hotelero
- ADR: dato del hotelero
- Ocupación: dato del hotelero
- % OTA vs directo: dato del hotelero
- Comisión OTA: 15% (estándar de industria, verificable en facturas Booking/Expedia)

Sin embargo, el documento nunca muestra este número. Solo muestra el resultado después de restarle dos supuestos hipotéticos.

### 10.4 ¿Qué preguntaría un hotelero con sentido comercial?

Si el dueño de Amazilia ve "$2,610,000 de pérdida":

1. "¿Pérdida de qué?" → Mezcla comisiones reales con oportunidades hipotéticas
2. "¿Cómo saben que el 10% migraría?" → No lo saben, es supuesto
3. "¿Y el 5% de la IA?" → Tampoco lo saben
4. "¿O sea que pago $5.4M en comisiones OTA?" → Sí, pero ese número nunca se le dice
5. "¿Entonces el número real verificable es $5.4M, no $2.6M?" → Correcto

### 10.5 Implicación: El modelo actual SUBESTIMA la pérdida real

El modelo toma una pérdida verificable ($5.4M) y la reduce con supuestos optimistas para producir un número más pequeño ($2.6M). El efecto es:

- El hotelero VE un número bajo que no puede verificar
- El hotelero NO VE el número alto que SÍ puede verificar
- Si alguien audita el cálculo, descubre que los supuestos no tienen base

Paradójicamente, el modelo sería más creíble mostrando la comisión OTA real ($5.4M) como "dinero que sale por OTAs" y presentando la mejora como un escenario separado.

---

## 11. Propuesta: Reformulación de la Narrativa Financiera

### 11.1 Principio: Separar hecho verificable de hipótesis

El documento debe presentar DOS capas claramente diferenciadas:

**CAPA 1 — Datos verificables (hechos)**
```
Su hotel vende 150 noches/mes a $300,000 COP promedio.
El 80% de sus reservas viene por OTAs (Booking, Expedia).
Las OTAs le cobran ~15% de comisión.
Comisión OTA mensual: $5,400,000 COP ← VERIFICABLE con sus facturas
```

**CAPA 2 — Escenarios de mejora (hipótesis, con disclaimer)**
```
Si mejora su presencia digital (Schema, FAQ, GBP):
  Escenario conservador: recupera 5% → ahorro $270,000/mes
  Escenario realista: recupera 10% → ahorro $540,000/mes
  Escenario optimista: recupera 20% → ahorro $1,080,000/mes

Adicionalmente, visibilidad en IA podría generar reservas nuevas:
  Estimado: 3%-7% más noches ocupadas ($450K - $1,050K/mes)
  *Este rango es estimativo, basado en benchmarks de industria, no en datos de su hotel.
```

### 11.2 Por qué esto es más sustentable

| Aspecto | Modelo actual | Propuesta |
|---------|--------------|-----------|
| Dato principal | "Pérdida: $2.6M" (mezcla hecho + supuesto) | "Comisión OTA: $5.4M" (verificable) |
| Supuestos de mejora | Ocultos en la fórmula | Explícitos como escenarios |
| Si el hotelero verifica | Descubre que el número no cuadra | Confirma que $5.4M en comisiones es real |
| Credibilidad | Frágil — un cuestionamiento derrumba todo | Robusta — el dato principal es verificable |
| Motivación de compra | "Pierde $2.6M" (abstracto) | "Paga $5.4M en comisiones" (concreto, verificable en su cuenta bancaria) |

### 11.3 Cambio en la estructura del ScenarioCalculator

El calculador actual produce UN número (monthly_loss_cop) que mezcla hechos y supuestos.
El nuevo modelo debería producir TRES componentes separados:

```python
@dataclass
class FinancialBreakdown:
    # CAPA 1: Verificable (hechos del hotel + comisión OTA estándar)
    monthly_ota_commission_cop: float    # $5,400,000
    ota_commission_basis: str            # "120 noches OTA × $300K ADR × 15% comisión"

    # CAPA 2A: Ahorro por migración OTA→directo (hipótesis)
    shift_savings_cop: float             # $540,000
    shift_percentage: float              # 0.10
    shift_source: str                    # "benchmark: hoteles con presencia digital mejorada"

    # CAPA 2B: Ingresos nuevos por visibilidad IA (hipótesis)
    ia_revenue_cop: float                # $2,250,000
    ia_boost_percentage: float           # 0.05
    ia_source: str                       # "estimado: sin datos GA4"

    # META
    evidence_tier: str                   # "A" | "B" | "C"
    disclaimer: str                      # Texto honesto sobre confianza
```

### 11.4 Cómo operaría sin GA4 (Tier C — 90% de clientes)

Sin GA4, los supuestos de mejora (10% shift, 5% IA boost) NO se pueden validar.
Pero la comisión OTA actual ($5.4M) SÍ es verificable con datos del hotelero.

El documento Tier C diría:
```
COMISIÓN OTA ACTUAL (verificable): $5,400,000 COP/mes

Potencial de recuperación con mejora digital:
  Rango estimado: $1,500,000 - $3,500,000 COP/mes
  *Estimación basada en benchmarks regionales.
   Para mayor precisión, conecte Google Analytics 4.
```

Esto es honesto: el dato duro es el centro, la estimación es un rango explícito con disclaimer.
El hotelero puede verificar el $5.4M con sus facturas de Booking/Expedia.
La estimación de recuperación es claramente un "podría ser", no un "es".

### 11.5 Cómo operaría con GA4 (Tier A)

Con GA4+GSC, los supuestos se reemplazan con datos:
- Traffic share real → peso de cada brecha proporcional a tráfico perdido
- CTR diferencial → cuántas visitas pierde vs competidores
- Conversion rate → cuántas visitas se convierten en reservas

El documento Tier A diría:
```
COMISIÓN OTA ACTUAL: $5,400,000 COP/mes
TRÁFICO PERDIDO VERIFICADO: 340 visitas/mes que van a competidores
CONVERSIÓN ESTIMADA: 2.1% (benchmark Eje Cafetero)

Pérdida por tráfico no capturado: $2,142,000 COP/mes
  (340 visitas × 2.1% conversión × $300,000 ADR)

Basado en: GA4 (configurado) + GSC (configurado) + benchmarks Eje Cafetero
```

---

## 12. Resumen del problema completo (3 capas)

| Capa | Problema | Dónde | Severidad |
|------|----------|-------|-----------|
| PRESENTACIÓN | Inflación x1.2 del valor (techo como principal) | `main.py:1884` + `v4_diagnostic_generator.py:551` | ALTA |
| PESOS | Brechas con porcentajes hardcoded, no normalizados | `v4_diagnostic_generator.py:1770-1910` | ALTA |
| CONCEPTUAL | Fórmula mezcla hechos verificables con supuestos inventados | `scenario_calculator.py:215,220` | CRÍTICA |

La capa CONCEPTUAL es la más grave y la que menos se nota: no es un bug de código,
es un problema de diseño del modelo financiero. El número que se presenta como
"pérdida" no es una pérdida — es una pérdida neta después de restar hipótesis
optimistas que no tienen evidencia.

**El fix completo requiere rediseñar `FinancialBreakdown` como entidad separada
(Sección 11.3), no solo ajustar valores de presentación.**

---

## 13. Hallazgo: El Scraper Extrae Precios pero el Motor Financiero No los Usa

### 13.1 El scraper YA tiene la capacidad

`modules/scrapers/web_scraper.py` (líneas 54-99, 1027-1091) extrae `precio_promedio` de:

| Fuente | Selector/Pattern | Confidence |
|--------|-----------------|------------|
| Schema JSON-LD | `data['priceRange']` | HIGH |
| Meta tags | `og:price:amount`, `product:price:amount` | MEDIA |
| CSS selectors | `.price`, `.precio`, `.tarifa`, `[itemprop="price"]` | MEDIA |
| Regex | `desde $XXX.XXX`, `precio $XXX.XXX COP` | MEDIUM |

También maneja rangos (ej: "$280K-$520K") tomando el promedio (`_parse_price` línea 1088).

### 13.2 El dato se pierde — desconexión scraping ↔ financiero

El flujo financiero (`main.py:1526`) obtiene ADR así:

```python
adr_from_onboarding = datos_operativos.get('valor_reserva_cop')
```

Solo busca en `datos_operativos` (onboarding form). **Nunca consulta `datos_scraping['precio_promedio']`**.

Si `adr_from_onboarding` es None, la resolución cae a:

```
ADRResolutionWrapper.resolve():
  mode=ACTIVE  → RegionalADRResolver → benchmark regional avg_adr
  mode=LEGACY  → LEGACY_DEFAULT_ADR = $300,000 fijo (hardcodeado línea 44)
```

### 13.3 Cadena de fallback actual (lo que usa el motor financiero)

```
1. Onboarding form (valor_reserva_cop)     → "Usted nos lo dijo"
2. Benchmark regional (avg_adr por región) → "Promedio Eje Cafetero"
3. Hardcode $300,000 (LEGACY_DEFAULT_ADR)  → "Valor por defecto"
```

### 13.4 Cadena de fallback propuesta (conectando el scraper)

```
1. Onboarding form (valor_reserva_cop)           → HECHO verificable
2. Scraping web (precio_promedio del HTML)       → HECHO verificable (si tiene Schema)
3. Benchmark regional (avg_adr por región)       → ESTIMADO benchmark
4. Hardcode $300,000                              → ÚLTIMO RECURSO
```

El paso 2 es clave: si el hotel tiene `priceRange` en su Schema (o incluso un "desde $X" en el HTML),
el ADR se puede derivar de su propia web. Eso le da al hotelero una respuesta verificable:
"Extraído de su página web, sección tarifas".

### 13.5 Impacto en el modelo propuesto

Para la narrativa de "hecho verificable" (Sección 11), el ADR scrapeado fortalece la Capa 1:

```
COMISIÓN OTA ACTUAL (verificable): $X COP/mes

Desglose:
  Habitaciones: 10 (fuente: onboarding)
  Tarifa por noche: $280,000 (fuente: su página web, schema priceRange)
  Ocupación: 50% (fuente: benchmark regional)
  Canal directo: 20% (fuente: onboarding)
  Comisión OTA: 15% (estándar industria)
```

Cada dato tiene fuente. El hotelero puede verificar: "¿Mi tarifa es $280K? Sí, eso dice mi web".

### 13.6 Limitaciones reales del scraping de precios

- Muchos hoteles pequeños NO publican precios en su web (solo "consulte disponibilidad")
- Los que usan Booking widget embebido tienen el precio en iframe (no scrapeable)
- priceRange en Schema es un rango ("$200K-$500K"), no un valor exacto
- Algunos muestran precios por temporada que no corresponden al ADR real

**Conclusión**: El scraping de precios es una fuente válida para el Tier C,
pero no está garantizado. Por eso el fallback a benchmarks es necesario.
Lo importante es INTENTAR el scraping primero y documentar la fuente del dato.

### 13.7 Archivo a modificar

| Archivo | Cambio |
|---------|--------|
| `main.py:1526` | Agregar fallback: si `adr_from_onboarding` es None, buscar `datos_scraping['precio_promedio']` antes de ir a benchmark |
| `adr_resolution_wrapper.py` | Agregar fuente `"web_scraping"` al enum ADRSource y manejarla en resolve() |
| `ADRResolutionResult.source` | Nuevo valor posible: `"web_scraping"` con confidence proporcional al método de extracción |

---

## 14. GAPs — Estado post-FASE-G (ORIGINALMENTE PRE-IMPLEMENTACIÓN)

### 14.1 GAP A: Variable `hotel_data` del scraper — RESUELTO (FASE-D)
- FASE-D conectó scraper → ADR resolution chain
- `adr_from_scraping` ahora es fuente #2 en la cadena de fallback
- `ADRSource.WEB_SCRAPING` existe en el enum

### 14.2 GAP B: `v4_proposal_generator.py` consume `monthly_loss_max` 22 veces — RESUELTO (FASE-E)
- Los 22 puntos cambiados a `monthly_loss_central`
- `format_loss_cop()` y `is_equilibrium_or_gain()` usan central

### 14.3 GAP C: `Scenario.format_loss_cop()` e `is_equilibrium_or_gain()` — RESUELTO (FASE-A + E)
- Ambos métodos ahora prefieren `monthly_loss_central` sobre `monthly_loss_max`

### 14.4 GAP D: Template diagnostico_v6_template.md — RESUELTO (FASE-F)
- Template actualizado con placeholders de evidence tier y breakdown

### 14.5 GAP E: Decisión de scope — RESUELTO
- **Opción C ejecutada completa** (7 fases, FASE-A a FASE-G)
- Commit: 5171ce4

**Scope Opción C — estado final:**
- [x] FinancialBreakdown como nuevo dataclass (FASE-A)
- [x] Reformulación narrativa: Comisión OTA verificable → escenarios de mejora (FASE-F)
- [x] Nuevo template de diagnóstico con desglose por fuente (FASE-F)
- [x] Normalización de pesos de brechas (suma siempre = 100%) (FASE-C)
- [x] Conexión scraper → ADR (web_scraping como fuente) (FASE-D)
- [x] Evidence tier en YAML header (A/B/C) (FASE-F)
- [x] Actualización de v4_proposal_generator.py (22 puntos de consumo) (FASE-E)
- [x] Actualización de coherence_validator.py (FASE-E)
- [x] Actualización de asset_diagnostic_linker.py (FASE-E)
- [x] Actualización de data_structures.py (Scenario + FinancialBreakdown) (FASE-A)
- [x] Tests de regresión completos (453 passed) (FASE-G)
- [x] Integración main.py + E2E validación (FASE-G)

### 14.6 GAPs NUEVOS descubiertos durante FASE-G (noexistentes pre-implementación)

| GAP | Descripción | Acción requerida |
|-----|-------------|-----------------|
| G1 | `regional_adr_enabled=False` — RegionalADRResolver existe pero no se invoca | Activar flag en .env o config |
| G2 | `LEGACY_DEFAULT_ADR=300000` ignora `plan_maestro_data.json` regiones | Activar G1 elimina este problema |
| G3 | Occupancy y direct_channel son defaults sin fuente cuando no hay onboarding | Requiere onboarding o benchmark lookup |
| G4 | Supuestos 10% shift / 5% IA boost hardcodeados en `scenario_calculator.py` | Con GA4 real se reemplazan con datos |
| G5 | Generadores aceptan `financial_breakdown` pero no lo consumen en templates | Conectar en siguiente iteración |

---

## 15. Estructuras de Datos Actuales (referencia rápida) — ACTUALIZADO post-FASE-A

### Scenario (data_structures.py:83-102) — CON monthly_loss_central
```python
@dataclass
class Scenario:
    monthly_loss_min: int
    monthly_loss_max: int
    probability: float
    description: str
    assumptions: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    monthly_opportunity_cop: int = 0
    monthly_loss_central: Optional[int] = None  # FASE-A: valor central de presentación

    def format_loss_cop(self) -> str:
        # FASE-A: usa central si disponible, sino max
        amount = self.monthly_loss_central if self.monthly_loss_central is not None else self.monthly_loss_max
```

### FinancialBreakdown (data_structures.py:142-165) — NUEVO FASE-A
```python
@dataclass
class FinancialBreakdown:
    monthly_ota_commission_cop: float      # CAPA 1: verificable
    ota_commission_basis: str              # "120 noches OTA × $300K ADR × 15%"
    ota_commission_source: str             # "onboarding" | "scraping" | "benchmark"
    shift_savings_cop: float               # CAPA 2A: hipótesis
    shift_percentage: float                # 0.10
    shift_source: str                      # "benchmark: ..."
    ia_revenue_cop: float                  # CAPA 2B: hipótesis
    ia_boost_percentage: float             # 0.05
    ia_source: str                         # "estimado: sin GA4"
    evidence_tier: str                     # "A" | "B" | "C"
    disclaimer: str                        # Texto honesto sobre confianza
    hotel_data_sources: Dict[str, str] = field(default_factory=dict)
```

### EvidenceTier (data_structures.py:126-139) — NUEVO FASE-A
```python
class EvidenceTier(Enum):
    A = "A"  # GA4 + GSC conectados
    B = "B"  # Benchmarks regionales + scraping
    C = "C"  # Solo scraping básico
```

### FinancialScenarios (data_structures.py:105-120)
```python
@dataclass
class FinancialScenarios:
    conservative: Scenario  # 70%
    realistic: Scenario     # 20% - MAIN
    optimistic: Scenario    # 10%

    def get_main_scenario(self) -> Scenario:
        return self.realistic

    def format_range_cop(self) -> str:
        # usa conservative.min y optimistic.max
```

### ADRSource (adr_resolution_wrapper.py:23-27)
```python
class ADRSource(Enum):
    REGIONAL_V410 = "regional_v410"
    LEGACY_HARDCODE = "legacy_hardcode"
    USER_PROVIDED = "user_provided"
    # FALTA: WEB_SCRAPING = "web_scraping"
```

### ADRResolutionResult (adr_resolution_wrapper.py:30-38)
```python
@dataclass
class ADRResolutionResult:
    adr_cop: float
    source: str  # "regional_v410", "legacy_hardcode", "user_provided"
    confidence: str
    used_new_calculation: bool
    shadow_comparison: Optional[ShadowComparison] = None
    metadata: Optional[Dict[str, Any]] = None
```

### RolloutMode (feature_flags.py:13-20)
```python
class RolloutMode(Enum):
    FORCE_LEGACY = "force_legacy"
    SHADOW = "shadow"
    CANARY = "canary"
    ACTIVE = "active"
```

---

## 16. Consumidores de monthly_loss_max — Mapa Completo (ACTUALIZADO post-FASE-E)

**FASE-E actualizó ~20 puntos de `max` a `central`.** Los marcados con ✅ ya usan `monthly_loss_central`.

| Archivo | Línea | Uso | Estado FASE-E |
|---------|-------|-----|---------------|
| `data_structures.py` | 95 | `format_loss_cop()` | ✅ central |
| `data_structures.py` | 102 | `is_equilibrium_or_gain()` | ✅ central |
| `data_structures.py` | 118 | `format_range_cop()` → min | No cambia |
| `data_structures.py` | 119 | `format_range_cop()` → optimistic.max | No cambia |
| `v4_diagnostic_generator.py` | 471 | `main_scenario_amount` (título) | ✅ central |
| `v4_diagnostic_generator.py` | 442 | `loss_6_months_value` (×6) | ✅ central |
| `v4_diagnostic_generator.py` | 551 | `monthly_loss` (template V6) | ✅ central |
| `v4_diagnostic_generator.py` | 897 | `empathy_message` | ✅ central |
| `v4_diagnostic_generator.py` | 1554 | `costo = max * proportion` (brechas) | ✅ central |
| `v4_diagnostic_generator.py` | 1588 | `recuperacion = max * proportion` | ✅ central |
| `v4_proposal_generator.py` | 457 | `projected_monthly_gain` | ✅ central |
| `v4_proposal_generator.py` | 489-494 | gains y ROI 3 escenarios | ✅ central |
| `v4_proposal_generator.py` | 503-514 | recuperación M1-M6, neto M1-M6 | ✅ central |
| `coherence_validator.py` | 433 | `pain = .monthly_loss_max` | ✅ central |
| `asset_diagnostic_linker.py` | 498, 504, 507 | impacto por asset | ✅ central |
| `main.py` | construcción escenarios | `monthly_loss_max` como TECHO | ✅ central añadido |

---

## 17. Tests Relevantes

Tests que probablemente toquen estas estructuras (buscar con grep en tests/):

```
test_data_structures.py      → Scenario, FinancialScenarios
test_financial_*.py          → ScenarioCalculator, FinancialCalculatorV2
test_diagnostic_generator.py → v4_diagnostic_generator
test_proposal_generator.py   → v4_proposal_generator
test_coherence_validator.py  → coherence_validator
test_loss_projector.py       → loss_projector
test_adr_resolution*.py      → ADRResolutionWrapper
```

Comando de verificación post-cambio:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python -m pytest tests/ -x -q 2>&1 | tail -20
```
