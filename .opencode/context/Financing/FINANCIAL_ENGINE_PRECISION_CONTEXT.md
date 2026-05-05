# CONTEXTO REVISADO: Financial Engine — Falsa Precisión, Fallback Regional Honesto y Priorización por Canal Basada en Evidencia

**Archivo fuente:** `C:\Users\Jhond\Github\iah-cli\.opencode\context\Financing\FINANCIAL_ENGINE_PRECISION_CONTEXT.md`  
**Guardado el:** 2026-05-03  
**Versión repo verificada:** v4.39.0  
**Estado:** contexto listo para que en una nueva sesión se diseñe un plan de intervención por fases.  
**Corrección clave de esta revisión:** la Alternativa G no debe diseñarse para Amazilia ni asumir WhatsApp como canal dominante. Debe resolver cualquier hotel boutique, con foco inicial Eje Cafetero Colombia, mediante inferencia de canal basada en evidencia.

---

## 1. VEREDICTO EJECUTIVO

La solución más adecuada NO es escoger una única alternativa aislada.

La ruta recomendada es una solución compuesta:

> **Financial Evidence Engine + Regional Benchmark Fallback + Evidence-Based Channel Prioritization**

En términos de las opciones existentes:

1. **Base inmediata:** E + F + A + B.
   - E: etiquetas epistémicas / metadata de confianza.
   - F: activar fallback regional, pero como benchmark inferido, no como dato exacto.
   - A/B: rangos y advertencias visibles según calidad de evidencia.

2. **Gobernanza de exactitud:** D modificada.
   - No debe bloquear todo cálculo financiero.
   - Debe bloquear solamente el lenguaje de “cifra exacta” cuando no existan datos medidos del hotel.

3. **Fase posterior:** G rediseñada.
   - No “WhatsApp-first”.
   - Sí “Channel Evidence Weighted Prioritization”.
   - Debe funcionar para cualquier hotel boutique, no para un caso particular.

4. **Complemento posterior:** H.
   - Filtro por ejecutabilidad real del owner-operador.

5. **Posponer:** I y J.
   - I: pricing condicionado por evidencia, después de estabilizar tiers.
   - J: solo tomar una versión liviana como tabla de sensibilidad, no como módulo grande.

### Criterio rector de diseño

> Nunca mostrar dinero con más precisión que la evidencia que lo soporta; y nunca priorizar brechas por un canal que no fue inferido o confirmado con evidencia.

---

## 2. PROBLEMA A RESOLVER

### 2.1 Síntoma visible

El sistema genera una cifra como **$2.610.000 COP/mes** para hoteles sin onboarding y la presenta con desglose aparentemente preciso:

- $530.613
- $212.193
- etc.

El problema no es solo el número, sino la **autoridad visual** con la que se presenta una estimación basada en defaults.

### 2.2 Causa inmediata técnica

El sistema sí tiene datos regionales y un resolver implementado, pero el uso operativo está apagado por feature flags.

Evidencia verificada en código:

`modules/financial_engine/feature_flags.py`

```python
regional_adr_enabled: bool = False
regional_adr_mode: RolloutMode = RolloutMode.SHADOW
validated_regions: tuple = ("eje_cafetero", "antioquia")
```

`FinancialFeatureFlags.from_env()` también usa defaults apagados:

```python
regional_adr_enabled=_env_bool("FINANCIAL_REGIONAL_ADR_ENABLED", False)
regional_adr_mode=RolloutMode(os.getenv("FINANCIAL_REGIONAL_ADR_MODE", "shadow"))
validated_regions=("eje_cafetero", "antioquia")
```

### 2.3 Cadena real de fallback ADR

Verificada en `modules/financial_engine/adr_resolution_wrapper.py`:

```python
1. user_provided_adr       -> ADRSource.USER_PROVIDED
2. web_scraping_adr        -> ADRSource.WEB_SCRAPING
3. regional benchmark      -> ADRSource.REGIONAL_V410
4. hardcode $300K          -> ADRSource.LEGACY_HARDCODE
```

Pero como `regional_adr_enabled=False`, en práctica se cae en legacy cuando no hay onboarding ni scraping útil.

Constante actual:

```python
LEGACY_DEFAULT_ADR = 300000.0
```

### 2.4 Causa profunda de diseño

El motor no distingue suficientemente entre:

- dato medido,
- dato observado por scraping,
- benchmark regional,
- default global,
- simulación,
- conflicto entre fuentes.

Por eso puede presentar con la misma autoridad una cifra proveniente de onboarding real y una cifra proveniente de un hardcode global.

Esto rompe el contrato de confianza comercial.

---

## 3. REALIDAD DEL CÓDIGO VERIFICADA

### 3.1 Feature flags regionales

Archivo: `modules/financial_engine/feature_flags.py`

Hallazgos:

- `regional_adr_enabled` está en `False` por defecto.
- `regional_adr_mode` está en `SHADOW` por defecto.
- `validated_regions` excluye `caribe`.
- `should_use_regional_for(region)` retorna `False` si el flag está apagado.

Conclusión:

> El resolver regional existe, pero producción cae a legacy salvo que el entorno active explícitamente los flags.

### 3.2 ADRResolutionWrapper

Archivo: `modules/financial_engine/adr_resolution_wrapper.py`

Hallazgos:

- Prioriza onboarding.
- Luego web scraping.
- Luego regional si flags lo permiten.
- Luego hardcode $300K.
- En `ACTIVE`, si la región no está validada, retorna legacy.
- En `SHADOW`, calcula comparación pero retorna legacy.

Conclusión:

> El documento original acierta: el hardcode no es un bug accidental; es el resultado esperado del modo actual.

### 3.3 RegionalADRResolver

Archivo: `modules/financial_engine/regional_adr_resolver.py`

Hallazgos:

- Carga `data/benchmarks/plan_maestro_data.json`.
- Lee `v25_config.regiones`.
- Soporta segmentos:
  - `boutique_10_25`
  - `standard_26_60`
- Si no hay segmento, usa `adr_cop` o `precio_promedio`.
- Si no hay región, cae a default.
- `resolve_occupancy(region)` ya puede leer ocupación regional.

Conclusión:

> La infraestructura regional existe y es reutilizable, pero debe usarse como benchmark inferido, no como dato real del hotel.

### 3.4 plan_maestro_data.json

Archivo: `data/benchmarks/plan_maestro_data.json`

Valores actuales:

| Región | precio_promedio | ocupación | habitaciones_promedio |
|---|---:|---:|---:|
| default | $280.000 | 60% | 15 |
| antioquia | $280.000 | 60% | 18 |
| eje_cafetero | $330.000 | 52% | 12 |
| caribe | $410.000 | 66% | 25 |

Problema adicional:

El archivo todavía contiene nota histórica indicando:

> “No en uso operativo desde la transición a v4.0.0+”

Si vuelve a usarse como fuente operativa, esa nota debe actualizarse para no inducir a error.

### 3.5 Benchmarking.md

Archivo: `data/benchmarks/Benchmarking.md`

Valores 2026:

| Región | Segmento | Habitaciones | ADR estimado |
|---|---|---:|---:|
| Eje Cafetero | Boutique | 10-25 | $420.000 |
| Eje Cafetero | Estándar | 26-60 | $350.000 |
| Caribe | Boutique | 10-25 | $950.000 |
| Caribe | Estándar | 26-60 | $750.000 |
| Antioquia | Boutique | 10-25 | $620.000 |
| Antioquia | Estándar | 26-60 | $480.000 |

Advertencia crítica del propio archivo:

```markdown
USO INCORRECTO (PROHIBIDO v4.0):
- Input primario para calculos financieros especificos
- Fuente de datos para estimar perdidas de un hotel particular
- Sustituto de datos reales del hotel
```

Conclusión:

> Benchmarking.md puede alimentar benchmarks regionales estructurados, pero esos valores no deben renderizarse como “dato exacto del hotel”. Deben etiquetarse como `regional_benchmark` y mostrarse como rango/estimación preliminar.

### 3.6 NoDefaultsValidator

Archivo: `modules/financial_engine/no_defaults_validator.py`

Hallazgos:

- Bloquea `None`, `0` o missing en campos críticos.
- Detecta fuentes sospechosas, pero no bloquea por fuente.
- `SUSPECT_SOURCES` incluye:

```python
{"legacy_hardcode", "default", "unknown", "hardcoded", "estimated"}
```

Limitación:

- No diferencia todavía entre `regional_benchmark`, `observed`, `measured`, `simulated`, `conflict`.
- La confiabilidad se reduce a `verified` / `unverified`.

Conclusión:

> Existe una base útil, pero debe ampliarse hacia metadata epistémica por campo.

### 3.7 OpportunityScorer

Archivo: `modules/financial_engine/opportunity_scorer.py`

Hallazgos:

- Ya existe scoring por 3 factores:
  - severidad 0-40,
  - esfuerzo 0-30,
  - impacto 0-30.
- Incluye brechas WhatsApp, GBP, schema, performance, reviews, OG tags, citability, etc.
- No hay módulo actual de channel weighting.
- No hay inferencia explícita de canal dominante.

Conclusión:

> G no debe crear un pipeline paralelo completo. Debe extender el scoring existente con un multiplicador por canal, basado en evidencia.

### 3.8 Integración con diagnóstico comercial

Archivo: `modules/commercial_documents/v4_diagnostic_generator.py`

Hallazgos:

- `_compute_opportunity_scores()` usa `OpportunityScorer`.
- Mapea pain_ids a tipos de brecha.
- El scoring actual alimenta variables de template.
- Comentario existente advierte sobre conflicto de doble fuente en brechas.

Conclusión:

> La intervención de G debe ser cuidadosa para no crear otro “dual-source conflict”. El canal debe entrar como metadata/multiplicador trazable dentro del scorer, no como lista paralela de brechas.

---

## 4. CÁLCULO BASE DEL $2.610.000

La cifra sale de la fórmula realista en `scenario_calculator.py`:

```python
occupied_room_nights = rooms * 30 * occupancy_rate
ota_percentage = 1.0 - direct_channel_percentage
ota_bookings = occupied_room_nights * ota_percentage
current_ota_commission_loss = ota_bookings * adr_cop * ota_commission_rate
potential_shift = ota_bookings * moderate_shift
savings = potential_shift * adr_cop * ota_commission_rate
ia_visibility_boost = occupied_room_nights * 0.05 * adr_cop
monthly_loss = current_ota_commission_loss - savings - ia_visibility_boost
```

Con defaults:

```text
rooms = 10
adr_cop = 300.000
occupancy_rate = 0.50
direct_channel_percentage = 0.20
ota_commission_rate = 0.15
moderate_shift = 0.10
ia_visibility_boost = 0.05
```

Resultado:

```text
occupied_room_nights = 10 * 30 * 0.50 = 150
ota_bookings = 150 * 0.80 = 120
current_ota_commission_loss = 120 * 300.000 * 0.15 = 5.400.000
savings = 120 * 0.10 * 300.000 * 0.15 = 540.000
ia_visibility_boost = 150 * 0.05 * 300.000 = 2.250.000
monthly_loss = 5.400.000 - 540.000 - 2.250.000 = 2.610.000
```

Esto confirma:

> $2.610.000 no es un bug aritmético. Es el output esperado de defaults convergentes.

---

## 5. IMPACTO DE ACTIVAR BENCHMARKS REGIONALES

Usando la misma fórmula actual del repo, para 10 habitaciones y directo 20%:

| Caso | ADR | Ocupación | Resultado realista aprox. |
|---|---:|---:|---:|
| Legacy actual | $300.000 | 50,0% | $2.610.000 |
| Eje Cafetero plan_maestro actual | $330.000 | 52,0% | $2.985.840 |
| Eje Cafetero boutique 2026 | $420.000 | 51,2% | $3.741.696 |
| Caribe boutique 2026 | $950.000 | 68,5% | $11.323.050 |
| Antioquia boutique 2026 | $620.000 | 64,2% | $6.925.896 |

Conclusión:

> F sí elimina la convergencia a $2.610.000. Pero si se muestra como cifra exacta, solo cambia una falsa precisión global por una falsa precisión regional.

Por eso F debe combinarse con E + A/B.

---

## 6. EVALUACIÓN REVISADA DE OPCIONES

| Opción | Veredicto revisado | Motivo |
|---|---|---|
| A — Rangos Tier C | Mantener | Corrige falsa precisión visual, pero no basta sola. |
| B — Advertencia output | Mantener | Protege confianza comercial, pero no cambia cálculo. |
| C — Captura datos reales | Mantener como prioridad funcional | Onboarding/web scraping deben ser fuente superior, pero no requisito para salida preliminar. |
| D — Validación mínimos | Modificar | No bloquear todo cálculo; bloquear exactitud/promesas cuando faltan datos medidos. |
| E — Etiquetas epistémicas | Prioridad inmediata | Es la pieza arquitectónica central. |
| F — ADN Regional | Prioridad inmediata ajustada | Activar como benchmark inferido con rango, no como dato exacto. |
| G — Channel-First | Rediseñar y postergar | Debe ser evidence-first y genérica para hoteles boutique. |
| H — Filtro owner | Recomendada posterior | Mejora utilidad comercial del plan de acción. |
| I — Precio condicionado | Posponer | Requiere estabilidad previa en tiers de evidencia. |
| J — Documento vivo | No priorizar como módulo | Tomar solo tabla liviana de sensibilidad para Tier B/C. |

---

## 7. SOLUCIÓN RECOMENDADA: FINANCIAL EVIDENCE ENGINE

### 7.1 Objetivo

Eliminar la falsa precisión financiera sin perder utilidad comercial.

El sistema debe poder producir una estimación preliminar cuando faltan datos reales, pero debe comunicar claramente la calidad de evidencia.

### 7.2 Jerarquía de fuentes para ADR

Orden recomendado:

```text
1. onboarding.valor_reserva_cop
   status: measured
   render: cifra puntual

2. web_scraping.precio_promedio
   status: observed
   render: aproximado con fuente

3. benchmark regional por región + segmento
   status: regional_benchmark
   render: rango regional / estimación preliminar

4. default nacional
   status: defaulted
   render: rango amplio + advertencia fuerte
```

### 7.3 Metadata epistémica por campo

Agregar o propagar metadata por variable financiera crítica:

```json
{
  "financial_evidence": {
    "adr_cop": {
      "value": 420000,
      "source": "benchmarking_2026:eje_cafetero:boutique_10_25",
      "epistemic_status": "regional_benchmark",
      "precision": "range",
      "can_show_exact": false
    },
    "occupancy_rate": {
      "value": 0.512,
      "source": "benchmarking_2026:eje_cafetero",
      "epistemic_status": "regional_benchmark",
      "precision": "range",
      "can_show_exact": false
    },
    "direct_channel_percentage": {
      "value": 0.20,
      "source": "system_default",
      "epistemic_status": "defaulted",
      "precision": "range",
      "can_show_exact": false
    }
  },
  "financial_precision_tier": "C",
  "can_show_exact_money": false
}
```

### 7.4 Estados epistémicos recomendados

| Estado | Significado | Render recomendado |
|---|---|---|
| `measured` | Dato entregado por owner/onboarding o API real confiable | Cifra puntual |
| `observed` | Extraído del sitio web o evidencia directa, pero no confirmado por owner | Cifra aproximada |
| `regional_benchmark` | Inferido por región + segmento | Rango regional |
| `defaulted` | Valor genérico de sistema | Rango amplio + advertencia |
| `simulated` | Supuesto de modelo sin evidencia directa | Proyección hipotética |
| `conflict` | Fuentes contradictorias | Solicitar validación, no prometer exactitud |

### 7.5 Regla para mostrar dinero

```python
can_show_exact_money = all(
    field.epistemic_status in {"measured", "observed"}
    for field in [adr_cop, occupancy_rate, direct_channel_percentage]
)
```

Si `can_show_exact_money=False`:

- no mostrar centavos,
- no mostrar desglose con precisión falsa,
- usar rango,
- mostrar fuente,
- incluir CTA para completar datos.

### 7.6 Ejemplo de render correcto Tier C

En vez de:

```markdown
Pérdida estimada: $2.610.000 COP/mes
```

Usar:

```markdown
Pérdida estimada preliminar: ~$3.4M–$4.1M COP/mes

Base de cálculo:
- ADR: benchmark regional Eje Cafetero boutique 2026, no dato confirmado del hotel.
- Ocupación: benchmark regional 2026.
- Canal directo: default del sistema.

Para convertir esta estimación en proyección exacta, confirme:
1. tarifa promedio real,
2. ocupación mensual,
3. porcentaje de reservas directas vs OTA.
```

### 7.7 Regla para defaults globales

Si la fuente cae en `LEGACY_HARDCODE`:

- mantener cálculo solo como fallback técnico,
- marcar `epistemic_status=defaulted`,
- mostrar advertencia fuerte,
- no mostrar cifra exacta,
- considerar deprecación gradual de `LEGACY_DEFAULT_ADR = 300000.0`.

---

## 8. SOLUCIÓN RECOMENDADA PARA F: REGIONAL BENCHMARK FALLBACK HONESTO

### 8.1 Qué hacer

No basta con cambiar tres líneas en `feature_flags.py`.

El cambio correcto es:

1. Habilitar resolución regional bajo control.
2. Agregar `caribe` a regiones validadas.
3. Migrar datos 2026 estructurados desde `Benchmarking.md` a JSON/YAML operativo.
4. Marcar la fuente como `regional_benchmark`.
5. Renderizar rango, no cifra exacta.
6. Actualizar nota histórica de `plan_maestro_data.json` si vuelve a ser operativo.
7. Mantener trazabilidad de fuente y fecha.

### 8.2 Riesgo a evitar

No convertir esto:

```text
ADR = $300.000 hardcode exacto falso
```

en esto:

```text
ADR = $420.000 benchmark regional exacto falso
```

La salida correcta es:

```text
ADR inferido desde benchmark regional boutique Eje Cafetero 2026.
Rango financiero preliminar, no cifra exacta del hotel.
```

### 8.3 Fuente estructurada recomendada

Crear o actualizar fuente estructurada, por ejemplo:

`data/benchmarks/regional_adr_2026.json`

o extender `plan_maestro_data.json` con metadata clara:

```json
{
  "region": "eje_cafetero",
  "segment": "boutique_10_25",
  "adr_cop": 420000,
  "occupancy_rate": 0.512,
  "source": "Benchmarking.md 2026",
  "source_role": "regional_benchmark_not_hotel_specific",
  "epistemic_status": "regional_benchmark",
  "valid_for_exact_projection": false
}
```

### 8.4 Validación esperada

Después de la intervención:

- Hotel sin onboarding en Eje Cafetero no debe caer a $300K si se detecta región.
- Hotel sin onboarding en Caribe no debe caer a $300K si se detecta región.
- Ningún benchmark regional debe presentarse como cifra exacta.
- `financial_scenarios.json` debe indicar fuente y status.
- Documentos comerciales deben mostrar rango y advertencia para Tier C/B regional.

---

## 9. SOLUCIÓN RECOMENDADA PARA G: CHANNEL EVIDENCE WEIGHTED PRIORITIZATION

### 9.1 Corrección conceptual

La Alternativa G original usaba un ejemplo real de Amazilia:

```text
WhatsApp verificado, 60-70% reservas último minuto
```

Ese supuesto NO es válido como regla general.

La solución no se construye para Amazilia. Debe resolver cualquier hotel boutique, con foco inicial en Eje Cafetero Colombia.

Por tanto, G debe reformularse así:

> No “Channel-First basado en WhatsApp”. Sí “priorización de oportunidades ponderada por canal dominante inferido con evidencia”.

### 9.2 Objetivo de G rediseñada

Evitar que el sistema detecte señales de canal importantes y aun así entregue un plan genérico SEO/IA.

Pero sin asumir canal dominante cuando no hay evidencia suficiente.

### 9.3 Nuevo módulo sugerido

Nombre recomendado:

```text
modules/financial_engine/channel_evidence_resolver.py
```

o, si se decide ubicar fuera de financial_engine:

```text
modules/opportunity/channel_evidence_resolver.py
```

### 9.4 Inputs posibles

Desde onboarding:

- `canal_directo_pct`
- porcentaje OTA
- reservas por WhatsApp
- reservas por motor directo
- reservas por llamada
- reservas por redes sociales

Desde web scraping/auditoría:

- WhatsApp visible o ausente
- conflictos WhatsApp web vs GBP
- booking engine detectado
- presencia de OTAs
- CTA principal
- formularios de contacto
- velocidad mobile

Desde GBP:

- cantidad de reviews
- score GBP
- teléfono validado
- website link
- categoría/local intent
- fotos/actividad

Desde diagnóstico existente:

- `no_whatsapp_visible`
- `whatsapp_conflict`
- `low_gbp_score`
- `gbp_incomplete`
- `poor_performance`
- `no_hotel_schema`
- `faq_schema_missing`
- `low_citability`

### 9.5 Output esperado

```json
{
  "dominant_channel": "gbp",
  "confidence": "medium",
  "evidence": [
    "GBP tiene alto volumen de reviews",
    "web tiene WhatsApp visible pero sin evidencia de reservas por WhatsApp",
    "no hay onboarding de canal"
  ],
  "channel_weights": {
    "gbp_local": 1.25,
    "direct_conversion": 1.10,
    "whatsapp": 1.00,
    "seo": 0.95,
    "iao_schema": 0.95,
    "performance": 1.05
  },
  "assumptions": [
    "No se asume WhatsApp como canal dominante sin datos de reservas."
  ]
}
```

### 9.6 Canales recomendados

| Canal | Cuándo inferirlo | Brechas que suben |
|---|---|---|
| `whatsapp` | onboarding lo confirma o WhatsApp es CTA dominante con evidencia | WhatsApp visible, conflicto, velocidad respuesta, tracking, templates |
| `gbp` | alto peso de Google Maps/reviews/local intent | GBP incompleta, reviews, fotos, consistencia NAP |
| `booking_engine` | motor directo detectado o CTA fuerte a reservar | performance, tracking, motor reservas, schema Offer |
| `ota_dependent` | presencia OTA fuerte y bajo canal directo | estrategia directa, motor, WhatsApp, contenido de confianza |
| `seo_content` | tráfico orgánico/contenido como principal evidencia | headings, metadata, contenido local, FAQ |
| `unknown` | evidencia insuficiente | pesos boutique neutrales, no asumir canal |

### 9.7 Pesos boutique neutrales iniciales

Cuando no hay evidencia suficiente de canal dominante, usar pesos base para hotel boutique Eje Cafetero:

```json
{
  "gbp_local": 1.15,
  "direct_conversion": 1.10,
  "performance_mobile": 1.05,
  "whatsapp": 1.00,
  "seo_content": 0.95,
  "iao_schema": 0.95
}
```

Justificación:

- En hoteles boutique, Google Maps/local y conversión directa suelen ser críticos.
- WhatsApp es importante, pero no debe asumirse dominante sin evidencia.
- SEO/IAO siguen siendo relevantes, pero no deben aplastar canales transaccionales cuando hay señales fuertes.

### 9.8 Integración con OpportunityScorer

No crear otro ranking paralelo.

Modificar `OpportunityScorer` para aceptar metadata opcional:

```python
score_brechas(
    brechas,
    assessment=None,
    competitor_data=None,
    total_monthly_loss=None,
    channel_context=None,
)
```

Aplicar multiplicador trazable:

```python
adjusted_total_score = base_total_score * channel_multiplier
```

Y devolver metadata:

```json
{
  "base_total_score": 82,
  "channel_multiplier": 1.25,
  "adjusted_total_score": 102.5,
  "channel_reason": "GBP inferred as dominant channel with medium confidence"
}
```

### 9.9 Regla anti-Amazilia-hardcode

Prohibido codificar supuestos como:

```python
if region == "eje_cafetero":
    whatsapp_weight = 1.4
```

o:

```python
# boutique hotels use whatsapp as main channel
```

Correcto:

```python
if evidence.onboarding.whatsapp_share >= threshold:
    whatsapp_weight = 1.4
elif evidence.web.whatsapp_visible and no_other_channel_evidence:
    whatsapp_weight = 1.05
else:
    whatsapp_weight = neutral
```

---

## 10. VALIDACIÓN DE ÉXITO ESPERADA

### 10.1 Para el problema financiero

Un plan de intervención debe lograr:

- [ ] Hoteles sin onboarding ya no convergen automáticamente a $2.610.000 cuando hay región detectada.
- [ ] Regional benchmarks se usan solo como `regional_benchmark`.
- [ ] Benchmarks no se muestran como cifras exactas.
- [ ] `financial_scenarios.json` incluye fuente y status epistémico por campo.
- [ ] Documentos comerciales muestran rango cuando `can_show_exact_money=false`.
- [ ] Se muestra advertencia visible cuando haya fuentes `defaulted`, `simulated` o `regional_benchmark`.
- [ ] Onboarding real sigue teniendo prioridad máxima.
- [ ] Web scraping real sigue teniendo prioridad sobre benchmark regional.
- [ ] Legacy hardcode queda deprecado o aislado como fallback de último recurso.

### 10.2 Para G rediseñada

Un plan de intervención debe lograr:

- [ ] No asumir WhatsApp como canal dominante por región o tipo de hotel.
- [ ] Inferir canal dominante solo con evidencia.
- [ ] Si no hay evidencia, usar pesos boutique neutrales.
- [ ] Integrar pesos al `OpportunityScorer`, no crear ranking paralelo.
- [ ] Mostrar razón trazable del ajuste de prioridad.
- [ ] Mantener ranking base si `channel_context.confidence=low`.
- [ ] Validar al menos tres casos:
  - hotel con WhatsApp dominante confirmado,
  - hotel con GBP/local dominante,
  - hotel sin canal dominante claro.

---

## 11. ARCHIVOS CLAVE PARA EL PLAN DE INTERVENCIÓN

### 11.1 Financial Evidence Engine / Regional Fallback

| Archivo | Cambio probable |
|---|---|
| `modules/financial_engine/feature_flags.py` | Revisar defaults, regiones validadas, modo de rollout. |
| `modules/financial_engine/adr_resolution_wrapper.py` | Propagar fuente, status epistémico, fallback regional honesto. |
| `modules/financial_engine/regional_adr_resolver.py` | Agregar metadata de fuente, versión, segmento, valid_for_exact_projection. |
| `modules/financial_engine/calculator_v2.py` | Incluir metadata en `FinancialCalculationResult.to_dict()`. |
| `modules/financial_engine/no_defaults_validator.py` | Ampliar confiabilidad de fuentes más allá de verified/unverified. |
| `modules/financial_engine/scenario_calculator.py` | Mantener fórmula, pero asegurar trazabilidad/rangos en capa superior. |
| `main.py` | Propagar `financial_sources`, evidence tier y metadata al output final. |
| `data/benchmarks/plan_maestro_data.json` | Actualizar datos o nota operativa si vuelve a ser fuente. |
| `data/benchmarks/Benchmarking.md` | Mantener como referencia humana; evitar dualidad con JSON. |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Render financiero según precisión/evidencia. |
| templates de diagnóstico/propuesta | Rangos, advertencias, CTA de onboarding. |

### 11.2 Channel Evidence Weighted Prioritization

| Archivo | Cambio probable |
|---|---|
| `modules/financial_engine/opportunity_scorer.py` | Aceptar `channel_context`, multiplicadores, metadata trazable. |
| `modules/financial_engine/channel_evidence_resolver.py` | Nuevo módulo sugerido. |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Pasar channel_context al scorer. |
| tests de `opportunity_scorer` | Validar multiplicadores y fallback neutral. |
| nuevos tests `test_channel_evidence_resolver.py` | Validar inferencia de canal por evidencia. |

---

## 12. PROPUESTA DE FASES PARA DISEÑAR EN LA SIGUIENTE SESIÓN

Este contexto NO es aún el plan final. La siguiente sesión debe diseñar el plan de intervención siguiendo `.agents/workflows/phased_project_executor.md`, una fase por sesión.

Sugerencia de macrofases a convertir en prompts:

### FASE FIN-1 — Financial Evidence Metadata

Objetivo:
Agregar modelo de metadata epistémica por campo financiero y propagarlo hasta `financial_scenarios.json`.

Incluye:

- Definir estados epistémicos.
- Extender resultados ADR/financial calculator.
- Ampliar `NoDefaultsValidator` o crear helper de precision tier.
- Tests unitarios.

### FASE FIN-2 — Regional Benchmark Fallback Honesto

Objetivo:
Activar/usar regional resolver como benchmark inferido con trazabilidad.

Incluye:

- Actualizar fuente estructurada regional.
- Agregar Caribe a regiones validadas si procede.
- Evitar presentación exacta.
- Actualizar nota histórica de datos si aplica.
- Tests para Eje Cafetero, Caribe, Antioquia y default.

### FASE FIN-3 — Rendering: Rangos, Advertencias y CTA de Datos

Objetivo:
Cambiar documentos comerciales para que la presentación dependa de `can_show_exact_money`.

Incluye:

- Rangos para `regional_benchmark`, `defaulted`, `simulated`.
- Advertencias visibles.
- CTA para onboarding.
- No mostrar desglose arbitrario con falsa precisión.

### FASE FIN-4 — Validación E2E Financiera

Objetivo:
Probar que el sistema ya no converge a $2.610.000 y que no promete exactitud sin datos.

Incluye:

- Casos sin onboarding por región.
- Caso con onboarding.
- Caso con web scraping ADR.
- Verificar outputs JSON y MD.

### FASE CHAN-1 — Channel Evidence Resolver

Objetivo:
Crear inferencia de canal dominante basada en evidencia.

Incluye:

- Resolver inputs de onboarding/web/GBP/audit.
- No asumir WhatsApp.
- Pesos boutique neutrales para unknown.
- Tests unitarios.

### FASE CHAN-2 — Integración con OpportunityScorer

Objetivo:
Integrar multiplicadores de canal al scorer sin ranking paralelo.

Incluye:

- `channel_context` opcional.
- `base_total_score`, `channel_multiplier`, `adjusted_total_score`.
- Justificación trazable.
- Tests de no-regresión.

### FASE CHAN-3 — Validación Comercial de Prioridades

Objetivo:
Verificar que planes de acción cambian correctamente según canal inferido.

Casos mínimos:

- WhatsApp dominante confirmado.
- GBP/local dominante.
- Canal desconocido.
- Hotel boutique Eje Cafetero sin evidencia suficiente.

---

## 13. DECISIONES QUE EL PLAN DEBE TOMAR EXPLÍCITAMENTE

La siguiente sesión de planificación debe decidir:

1. Si los datos 2026 se migran a `plan_maestro_data.json` o a un nuevo `regional_adr_2026.json`.
2. Si `regional_adr_enabled` queda activo por defecto o se activa vía env/canary primero.
3. Cómo calcular rangos:
   - porcentaje fijo por status,
   - intervalo por benchmark,
   - escenarios conservador/realista/optimista.
4. Cómo definir `financial_precision_tier`:
   - por peor fuente,
   - por combinación ponderada,
   - por reglas explícitas.
5. Si `LEGACY_DEFAULT_ADR` se depreca o se conserva solo como fallback técnico invisible.
6. En qué capa se renderiza la advertencia:
   - generator,
   - template,
   - data structure.
7. Dónde ubicar `channel_evidence_resolver.py`:
   - financial_engine,
   - opportunity,
   - commercial_documents.
8. Qué señales mínimas permiten inferir WhatsApp como canal dominante.
9. Cómo evitar dual-source conflicts entre brechas detectadas, scores y templates.

---

## 14. COMANDO SUGERIDO PARA INICIAR LA NUEVA SESIÓN

Copiar y pegar en la próxima sesión:

```text
Carga y valida el contexto .opencode/context/Financing/FINANCIAL_ENGINE_PRECISION_CONTEXT.md contra el código vivo. Luego diseña un plan de intervención por fases siguiendo .agents/workflows/phased_project_executor.md para implementar la solución recomendada: Financial Evidence Engine + Regional Benchmark Fallback + Evidence-Based Channel Prioritization. Respeta 1 fase por sesión y R3 Scope.
```

---

## 15. REFERENCIAS PRINCIPALES

- `modules/financial_engine/feature_flags.py`
- `modules/financial_engine/adr_resolution_wrapper.py`
- `modules/financial_engine/regional_adr_resolver.py`
- `modules/financial_engine/calculator_v2.py`
- `modules/financial_engine/no_defaults_validator.py`
- `modules/financial_engine/scenario_calculator.py`
- `modules/financial_engine/opportunity_scorer.py`
- `modules/commercial_documents/v4_diagnostic_generator.py`
- `data/benchmarks/plan_maestro_data.json`
- `data/benchmarks/Benchmarking.md`
- `main.py`
- `.agents/workflows/phased_project_executor.md`
