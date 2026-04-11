# Diagnóstico $3,132,000 COP — Investigación Completa
## Amaziliahotel | 2026-04-10 | Actualizado con auditoría de código

---

## 1. Resumen Ejecutivo

El documento diagnóstico generado para Amaziliahotel muestra "$3,132,000 COP" como pérdida mensual.
El motor financiero calcula correctamente $2,610,000 (escenario realista).
La diferencia ($522,000 / 20%) proviene de un diseño de rangos en `main.py:1884` que infla el valor,
sumado a que el generador consume el TECHO del rango como cifra principal.

**Veredicto: El método actual NO es sustentable.** Requiere rediseño.

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

## 8. Datos del Caso de Prueba (Amaziliahotel)

```
hotel: Amaziliahotel
url: https://amaziliahotel.com
region: eje_cafetero
rooms: 10
adr_cop: 300,000
occupancy_rate: 0.5
direct_channel_percentage: 0.2

Escenarios (financial_scenarios.json):
  conservative: $5,076,000
  realistic:    $2,610,000  ← Valor calculado correcto
  optimistic:   -$189,000

Valor mostrado en documento: $3,132,000  ← Techo del rango (x1.2)
Diferencia: $522,000 (20% inflado)

Brechas detectadas: 4
  Schema Hotel  → 25% → $783,000
  FAQ Schema    → 12% → $375,840
  Metadata      → 10% → $313,200
  Open Graph    →  8% → $250,560
  Suma: 55% → $1,722,600
  Sin explicar: 45% → $1,409,400

coherence_score: 0.9177
generated: 2026-04-10 11:38:31
output_dir: output/v4_complete/
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

## 14. GAPs para la sesión de planificación — Lo que FALTA

### 14.1 GAP A: La variable `hotel_data` (scraping) NO está disponible en el bloque financiero

El scraper ejecuta en `main.py:507-508` (fase inicial) y guarda `hotel_data` como dict local.
Pero el bloque financiero ejecuta ~1000 líneas después (`main.py:1500+`) y solo consulta:
- `onboarding_data` → `datos_operativos.get('valor_reserva_cop')`
- Nunca accede a `hotel_data['precio_promedio']`

**Problema**: `hotel_data` es variable local del bloque `v4complete`. El plan necesita saber
cómo pasar `hotel_data` al bloque financiero. Posibles opciones:
- Variable global del scope (ya es local compartido si está en la misma función)
- Guardar en `args` o dict de contexto
- Cargar desde archivo intermedio

**Verificar en la sesión de plan**: inspeccionar el scope de `hotel_data` vs el bloque financiero en `main.py`. Ambos están dentro de la función `cmd_v4complete()` así que probablemente ya es accesible. Confirmar.

### 14.2 GAP B: `v4_proposal_generator.py` consume `monthly_loss_max` 22 veces

El generador de propuestas (`v4_proposal_generator.py`) usa `monthly_loss_max` en:

- Línea 457: `projected_monthly_gain = main_scenario.monthly_loss_max`
- Líneas 489-494: gains y ROI para los 3 escenarios
- Líneas 503-514: recuperación mensual M1-M6 y neto M1-M6
- Todas usan `monthly_loss_max` como valor de "ganancia" del escenario

**Si se cambia `monthly_loss_max`**, el proposal también se rompe.
El plan DEBE incluir `v4_proposal_generator.py` en el scope de cambios.
No está en la Sección 7 actual.

### 14.3 GAP C: `Scenario.format_loss_cop()` y `is_equilibrium_or_gain()` también usan max

`data_structures.py` líneas 93-102:

```python
def format_loss_cop(self) -> str:
    amount = self.monthly_loss_max  # ← usa max
    ...

def is_equilibrium_or_gain(self) -> bool:
    return self.monthly_loss_max <= 0  # ← usa max
```

Ambos métodos usan `monthly_loss_max`. Si se agrega un campo `monthly_loss_central`
o se cambia la semántica de `max`, estos métodos deben actualizarse.
Están en la Sección 7 pero sin detalle de qué cambiar.

### 14.4 GAP D: Template diagnostico_v6_template.md — estructura exacta

El template actual (115 líneas) tiene estos placeholders financieros:

```
Línea 60: **Pérdida estimada mensual: ${monthly_loss} COP**
Línea 62: Texto fijo: "Esta cifra representa reservas directas..."
Línea 68: ${brechas_section}
Línea 82: **Pérdida acumulada:** ${loss_6_months} COP
```

Si el modelo cambia a "Comisión OTA" + rangos, el template necesita:
- Reemplazar `${monthly_loss}` por desglose (comisión OTA + fuente)
- Agregar placeholder para evidence tier disclaimer
- Cambiar narrativa de "Pérdida" a "Comisión OTA verificable"
- Agregar sección de escenarios de recuperación con disclaimer

### 14.5 GAP E: No hay decisión tomada sobre scope (fix mínimo vs rediseño)

El archivo documenta 3 capas de problema (Sección 12) y una propuesta completa (Sección 11),
pero NO tiene una decisión sobre cuál implementar. La sesión nueva necesita saber:

**Opción A — Fix mínimo (capa presentación)**:
- Cambiar `monthly_loss_max` → valor central
- Normalizar pesos de brechas
- No tocar ScenarioCalculator ni agregar FinancialBreakdown
- Archivos: ~5

**Opción B — Fix medio (A + conectar scraper)**:
- Lo anterior + conectar `precio_promedio` del scraper al ADR
- Agregar `web_scraping` a ADRSource
- Archivos: ~8

**Opción C — Rediseño completo (3 capas)**:
- FinancialBreakdown como nuevo dataclass
- Reformulación narrativa (comisión OTA → escenarios de mejora)
- Nuevo template de diagnóstico
- Conexión scraper → ADR
- Cambios en proposal_generator, coherence_validator, asset_linker
- Archivos: ~13+

**DECISIÓN TOMADA: Opción C — Rediseño completo (3 capas).**

Justificación del usuario: "Las soluciones a medias no son soluciones, es aplazar el problema."

Además, el README.md línea 63 define la promesa del producto:
> "asigna un costo en COP a cada brecha detectada, y genera un paquete de
> assets técnicos listos para deploy con validación cruzada de coherencia"

El modelo actual NO cumple esa promesa:
- "asigna un costo en COP" → el costo viene de supuestos inventados, no de datos
- "validación cruzada de coherencia" → no hay validación cruzada del valor financiero

El rediseño DEBE alinearse con esa definición. El costo en COP de cada brecha debe ser:
1. Rastreable a una fuente (onboarding, scraping, benchmark)
2. Proporcional (pesos normalizados que sumen 100%)
3. Honestamente etiquetado (VERIFIED vs ESTIMATED, como ya hace con assets)
4. Basado en un hecho verificable (comisión OTA real) cuando sea posible

**Scope completo Opción C:**
- [ ] FinancialBreakdown como nuevo dataclass (Sección 11.3)
- [ ] Reformulación narrativa: "Comisión OTA verificable" → escenarios de mejora
- [ ] Nuevo template de diagnóstico con desglose por fuente
- [ ] Normalización de pesos de brechas (suma siempre = 100%)
- [ ] Conexión scraper → ADR (web_scraping como fuente)
- [ ] Evidence tier en YAML header (A/B/C)
- [ ] Actualización de v4_proposal_generator.py (22 puntos de consumo)
- [ ] Actualización de coherence_validator.py
- [ ] Actualización de asset_diagnostic_linker.py
- [ ] Actualización de data_structures.py (Scenario + FinancialBreakdown)
- [ ] Tests de regresión completos

---

## 15. Estructuras de Datos Actuales (referencia rápida)

### Scenario (data_structures.py:83-102)
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

## 16. Consumidores de monthly_loss_max — Mapa Completo

| Archivo | Línea | Uso | Impacto del cambio |
|---------|-------|-----|-------------------|
| `data_structures.py` | 95 | `format_loss_cop()` → display | Cambiar a central |
| `data_structures.py` | 102 | `is_equilibrium_or_gain()` | Cambiar a central |
| `data_structures.py` | 118 | `format_range_cop()` → conservative.min | No cambia (usa min) |
| `data_structures.py` | 119 | `format_range_cop()` → optimistic.max | No cambia |
| `v4_diagnostic_generator.py` | 471 | `main_scenario_amount` (título) | Cambiar a central |
| `v4_diagnostic_generator.py` | 442 | `loss_6_months_value` (×6) | Cambiar a central |
| `v4_diagnostic_generator.py` | 551 | `monthly_loss` (template V6) | Cambiar a central |
| `v4_diagnostic_generator.py` | 897 | `empathy_message` | Cambiar a central |
| `v4_diagnostic_generator.py` | 1554 | `costo = max * proportion` (brechas) | Cambiar a central |
| `v4_diagnostic_generator.py` | 1588 | `recuperacion = max * proportion` | Cambiar a central |
| `v4_proposal_generator.py` | 457 | `projected_monthly_gain` | Cambiar a central |
| `v4_proposal_generator.py` | 489 | `conservative_gain` | Cambiar a central |
| `v4_proposal_generator.py` | 490 | `conservative_roi` | Cambiar a central |
| `v4_proposal_generator.py` | 491 | `realistic_gain` | Cambiar a central |
| `v4_proposal_generator.py` | 492 | `realistic_roi` | Cambiar a central |
| `v4_proposal_generator.py` | 493 | `optimistic_gain` | Cambiar a central |
| `v4_proposal_generator.py` | 494 | `optimistic_roi` | Cambiar a central |
| `v4_proposal_generator.py` | 503-508 | `rec_m1` a `rec_m6` | Cambiar a central |
| `v4_proposal_generator.py` | 509-514 | `net_m1` a `net_m6` | Cambiar a central |
| `coherence_validator.py` | 433 | `pain = .monthly_loss_max` | Cambiar a central |
| `asset_diagnostic_linker.py` | 498 | `monthly_loss_max` en impacto | Cambiar a central |
| `asset_diagnostic_linker.py` | 504 | `impact_cop = max * weight` | Cambiar a central |
| `asset_diagnostic_linker.py` | 507 | `impact_cop = max * 0.25` fallback | Cambiar a central |
| `main.py` | 1877-1878 | `conservative.monthly_loss_max` | Mantener como techo (rango) |
| `main.py` | 1884 | `realistic.monthly_loss_max` | Mantener como techo, agregar central |
| `main.py` | 1890 | `optimistic.monthly_loss_max` | Mantener (caso especial) |

**Total: 22 puntos de consumo.** De estos, ~20 deben cambiar de `max` a `central`.
Los 3 de `main.py` (construcción) se mantienen como techo del rango.

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
