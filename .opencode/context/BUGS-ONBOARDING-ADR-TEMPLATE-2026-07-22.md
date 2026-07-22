# CONTEXTO: Bugs en Inyección de Datos de Onboarding al v4complete

> **Fecha original**: 2026-07-22
> **Auditado y amplificado**: 2026-07-22 (sesión de validación forense contra código vivo)
> **Sesión origen**: v4complete Don Alfonso Hotel (doble ejecución comparativa)
> **Propósito**: Habilitar formulación de plan de refactorización en nueva sesión
> **Hotel de prueba**: Hotel Don Alfonso (Pereira, Eje Cafetero)
> **Estado del código auditado**: 700 tests pasan, 55 fallan (fallos preexistentes no relacionados)

---

## 1. Resumen Ejecutivo

Se ejecutó v4complete **dos veces** para el mismo hotel: la primera con datos estimados (defaults) y la segunda con datos reales de `data/hotel_observations/observations.json` inyectados vía YAML de onboarding. La comparación reveló **3 bugs + 4 hallazgos sistémicos amplificados** que degradan la precisión financiera y la experiencia del documento final.

### Bugs del documento original (recalificados tras auditoría)

| Bug | Severidad Original | Severidad Real | Impacto |
|-----|-------------------|----------------|---------|
| BUG-1: ADR de onboarding ignorado | ALTA | **CRÍTICA** | Cifras financieras incorrectas (+27.3% sobredimensionado). Afecta 3 superficies (diagnóstico, propuesta, JSON). **El occupancy también se ignora** en el harness (ver NEW-1). |
| BUG-2: Template "Complete onboarding" siempre visible | MEDIA | **ALTA** | 7 mensajes redundantes en 3 documentos distintos pidiendo datos que ya se tienen. El flag `has_onboarding` existe pero nunca llega al generador. |
| BUG-3: Escenario optimista negativo | BAJA | **BAJA (diseño, no bug)** | Decisión intencional con 6 artefactos de soporte: `is_net_gain`, `display_label`, `hook_range` con `abs()`, log `[INFO]`, 5 tests `TestOptimistaFix`, y gate `CG-SCENARIO-NEGATIVE`. |

### Hallazgos sistémicos amplificados (no en el documento original)

| ID | Hallazgo | Severidad |
|----|----------|-----------|
| NEW-1 | **Occupancy_rate del onboarding también ignorado en el harness** — `harness_handlers.py:91-99` SIEMPRE sobrescribe con regional si `should_use_regional_for(region)=True`. El JSON Run 2 muestra `realistic=3,157,862.40` que coincide con `occ=0.512` (regional), NO con `0.4242` (onboarding). | **CRÍTICA** |
| H1 | **Consumidor paralelo divergente en proposal generator** — `v4_proposal_generator.py:1859-1873` tiene su propio `RegionalADRResolver` con `user_provided_adr=None`. La propuesta SIEMPRE muestra $420K aunque se arregle el harness. | **ALTA** |
| H2 | **Divergencia de taxonomía de fuentes: 3 vocabularios incompatibles** — `ADRSource` enum (snake_case) vs `ValidationSummary.sources` (PascalCase) vs `JSON input_data.adr_source` (mixto). El discriminador `v4_diagnostic_generator.py:1244` nunca matchea → `adr_source_label` siempre es "estimado". | **ALTA** |
| H3 | **Falsa confianza + falsa procedencia en ValidationSummary** — `confidence=VERIFIED` y `sources=["Onboarding"]` se derivan de la mera existencia del flag `adr_from_onboarding_verified`, no de si el valor final (`adr_cop`) realmente provino de ahí. Patrón repetido en rooms, occupancy_rate, y direct_channel_percentage. | **ALTA** |
| H4 | **Sin tests end-to-end onboarding → harness → JSON** — 92 tests de unidad pasan pero ninguno cierra el pipeline completo. El placeholder `"adr_source": "handler"` en el JSON nunca es detectado. | **MEDIA** |

### Hallazgos financieros adicionales

| ID | Hallazgo |
|----|----------|
| F1 | **§9 ROI del contexto es matemáticamente incorrecto** — dice "ROI ≈ 12.1x" usando `comision_ota / precio_mensual`, pero el código real usa `(loss × pain_ratio × recovery × 6) / (price × 6)`. Con ADR=$330K el ROI real sería ~0.20x, no 12.1x. |
| F2 | **gate_report muestra tier="B" pero el template propuesta usa condicionales Tier C** — Con evidence_tier=B, los bloques `{{if financial_evidence_tier == "C"}}` no se renderizan. Correcto para Don Alfonso, pero la divergencia tier entre gate y template es frágil. |
| F3 | **`adr_source="handler"` en JSON es un placeholder muerto** — `main.py:1861` hace `result_data.get("adr_source", "handler")` pero el handler NUNCA retorna clave top-level `"adr_source"` (solo `"adr_resolution": {"source": ...}`). El fallback siempre se activa. |

---

## 2. Datos de Prueba (observations.json → Hotel Don Alfonso)

```json
{
  "hotel_name": "Hotel Don Alfonso",
  "rooms": 11,
  "monthly_reservations": 140,
  "avg_reservation_cop": 330000,
  "direct_channel_percentage": 30.0,
  "occupancy_rate": 0.4242,
  "adr_cop": 330000,
  "is_transit_hotel": false,
  "ota_percentage": 70.0,
  "region": "eje_cafetero",
  "confidence": 0.95,
  "epistemic_status": "verified",
  "source": "contacto_directo"
}
```

Archivo de onboarding creado para la segunda ejecución:
`output/clientes/donalfonsohotel_onboarding.yaml`

**Nota de auditoría**: El YAML tiene `valor_reserva_cop: 330000` y `adr_cop: 330000`. El código solo lee `valor_reserva_cop` (main.py:1765) e ignora la clave `adr_cop`. Para hoteles con reservas multi-noche, `valor_reserva_cop ≠ adr_cop` — este mapeo semántico es incorrecto en el caso general.

---

## 3. BUG-1: ADR de Onboarding Ignorado (CRÍTICA)

### Síntoma
El ADR real del hotel es **$330,000 COP** (contacto directo, confidence 0.95).
El sistema usa **$420,000 COP** (benchmark regional Eje Cafetero).
El ValidationSummary marca `adr_cop: 420000 (verified)` — **valor incorrecto con etiqueta "verified"**.
El JSON muestra `"adr_source": "handler"` — **placeholder muerto que nunca se actualiza**.

### Evidencia en outputs reales

- **Log**: `ejecucion-con-datos-reales.log:159` — `✅ Onboarding data loaded: 6 campos confirmados`
- **Log**: `ejecucion-con-datos-reales.log:180` — `[OK] adr_cop: 420000 (verified)` ← **falsa confianza**
- **JSON**: `financial_scenarios_20260722_162455.json:6-7` — `"adr_cop": 420000, "adr_source": "handler"`
- **Diagnóstico**: `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260722_162501.md:88` — CTA "Complete el onboarding"
- **Propuesta**: `02_PROPUESTA_COMERCIAL_20260722_162515.md:36` — `ADR regional promedio | $420,000 COP` (consumidor paralelo H1)

### Cadena Causal (5 pasos)

**Paso 1** — `main.py:1765` — Extracción correcta del onboarding:
```python
adr_from_onboarding = datos_operativos.get('valor_reserva_cop')  # → 330000 ✓
```

**Paso 2** — `main.py:1797-1806` — Payload del harness NO incluye el ADR:
```python
financial_task = AgentTask(
    payload={
        "rooms": rooms,                          # 11 ✓
        "region": region,                        # "eje_cafetero" ✓
        "occupancy_rate": occupancy_rate,        # 0.4242 ✓
        "direct_channel_percentage": direct_channel_pct,  # 0.3 ✓
        "hotel_id": args.url,
        "hotel_name": hotel_name
        # ❌ FALTA: "user_provided_adr": adr_from_onboarding
    }
)
```

**Paso 3** — `harness_handlers.py:49` — Handler recibe None:
```python
user_provided_adr = payload.get("user_provided_adr")  # → None
```

**Paso 4** — `harness_handlers.py:65-71` — Resolver usa benchmark regional:
```python
adr_result = resolve_adr_with_shadow(
    region=region,               # "eje_cafetero"
    rooms=rooms,                 # 11
    user_provided_adr=None,      # ← NULL, cae al benchmark
)
# → adr_cop = 420000 (benchmark regional)
```

**Paso 5** — `main.py:2160-2170` — ValidationSummary marca como "verified" con valor incorrecto:
```python
# adr_from_onboarding_verified = True (porque adr_from_onboarding=330000 existe)
# PERO adr_cop = 420000 (del harness, NO del onboarding)
confidence = ConfidenceLevel.VERIFIED if adr_from_onboarding_verified else ConfidenceLevel.ESTIMATED
sources = ["Onboarding"] if adr_from_onboarding_verified else ["Benchmark"]
validated_fields.append(ValidatedField(
    field_name="adr_cop",
    value=adr_cop,  # ← 420000 (INCORRECTO, debería ser 330000)
    confidence=confidence,  # ← VERIFIED (falso — el valor no es del onboarding)
    sources=sources,  # ← ["Onboarding"] (falso — el valor vino del benchmark)
))
```

### Prueba de fuego (handler ejecutado con fix simulado)

Handler ejecutado con `user_provided_adr=330000` en el payload → retorna correctamente:
```json
{
  "adr_cop": 330000,
  "adr_resolution": {"source": "user_provided", "confidence": "ESTIMATED"},
  "pricing": {"monthly_price_cop": 400000, "pain_ratio": 0.1574},
  "scenarios": {"conservative": 5503196.16, "realistic": 2481177.6, "optimistic": -936714.24}
}
```
El resolver funciona correctamente cuando recibe el dato. El problema es upstream: el payload no lo transporta.

### Impacto Cuantificado

| Métrica | Con ADR real ($330K) | Con ADR actual ($420K) | Δ |
|---------|---------------------|----------------------|---|
| Comisión OTA | $4,851,000/mes | $6,174,000/mes | +$1,323,000 (+27.3%) |
| Realistic | ~$2,481,000/mes | $3,157,862/mes | +$676,862 (+21.4%) |
| Conservador | ~$5,503,000/mes | $7,004,068/mes | +$1,501,068 (+27.3%) |

**Nota sobre ROI**: El contexto original §9 calcula "ROI ≈ 12.1x" usando `comision_ota / precio_mensual`, lo cual es incorrecto. El ROI real en el código usa `(raw_loss × pain_ratio × recovery_factor × 6) / (price × 6)`. Con ADR=$330K, pain_ratio=0.1574, recovery=0.20: `ROI = (2,541,000 × 0.1574 × 0.20) / 400,000 = 0.20x`. El ROI mostrado de 7.9x con ADR=$420K está igualmente sobredimensionado.

### NEW-1: Occupancy_rate también ignorado en el harness (CRÍTICA)

**Ubicación**: `harness_handlers.py:91-99`
```python
# Override occupancy with regional data if available and validated
from modules.financial_engine.feature_flags import get_flags
flags = get_flags()
if flags.should_use_regional_for(region):
    from modules.financial_engine import RegionalADRResolver
    resolver = RegionalADRResolver()
    regional_occupancy = resolver.resolve_occupancy(region)
    if regional_occupancy is not None:
        occupancy_rate = regional_occupancy  # ← SOBRESCRIBE el onboarding
```

El JSON Run 2 (`financial_scenarios_20260722_162455.json`) muestra `realistic=3,157,862.40` que coincide EXACTAMENTE con `occupancy=0.512` (benchmark regional), NO con `0.4242` del onboarding. Reproducido algebraicamente: `ota - shift - ia` con `occ=0.512` → 3,157,862.40.

**Causa raíz**: `get_flags()` está cacheado a nivel módulo y se llama DESDE el handler (no recibe los flags que main.py ya computó como `feature_flags`). Si `.env` tiene `FINANCIAL_REGIONAL_ADR_ENABLED=true`, el handler ve los flags activos y sobrescribe.

**Fix**: El handler debe respetar `occupancy_rate` si viene del payload con fuente "onboarding", o recibir un flag explícito `occupancy_source` que indique que ya fue validado.

---

## 4. H1-H4: Hallazgos Sistémicos Amplificados

### H1 — Consumidor paralelo divergente en proposal generator (ALTA)

**Ubicación**: `modules/commercial_documents/v4_proposal_generator.py:1859-1873` y uso en L760.

El método `_get_adr_from_benchmarks()` instancia su propio `RegionalADRResolver` con `rooms=0` y `user_provided_adr=None`. Ignora completamente el onboarding.

**Impacto**: El ADR en la propuesta comercial SIEMPRE es el benchmark regional ($420K para eje_cafetero). El fix del harness payload NO afecta este path. Después del fix, la propuesta y el diagnóstico mostrarán ADRs diferentes al mismo hotel.

**Evidencia en output**: `02_PROPUESTA_COMERCIAL_20260722_162515.md:36` — `| ADR regional promedio | $420,000 COP |`

### H2 — Divergencia de taxonomía de fuentes: 3 vocabularios incompatibles (ALTA)

Tres vocabularios distintos para "fuente del ADR":

| Vocabulario | Valores | Ubicación |
|-------------|---------|-----------|
| **A — `ADRSource` enum** | `"user_provided"`, `"regional_v410"`, `"legacy_hardcode"`, `"web_scraping"` | `modules/financial_engine/adr_resolution_wrapper.py:23-28` |
| **B — ValidationSummary.sources** | `["Onboarding"]`, `["Benchmark"]`, `["Default"]`, `["Audit"]` | `main.py:2151, 2163, 2175, 2187` |
| **C — JSON `input_data.adr_source`** | `"handler"`, `"onboarding"`, `"regional"` | `main.py:1861, 1899-1907` |

**Bug activo en discriminador del diagnóstico**:
`v4_diagnostic_generator.py:1244`:
```python
if adr_source in ("user_provided", "web_scraping"):  # Vocabulario A (snake_case)
    adr_source_label = "datos del hotel"
```
Pero `sources = field_map['adr_cop'].sources` (L1207) trae `["Onboarding"]` (Vocabulario B, PascalCase). **Nunca matchea** → `adr_source_label` siempre cae a `"estimado"`. La etiqueta "datos del hotel" es **código muerto**.

### H3 — Falsa confianza + falsa procedencia en ValidationSummary (ALTA)

**Ubicación**: `main.py:2160-2170`. Mismo patrón en rooms (L2150), occupancy_rate (L2174), y direct_channel_percentage (L2186).

El bloque:
```python
confidence = ConfidenceLevel.VERIFIED if adr_from_onboarding_verified else ConfidenceLevel.ESTIMATED
sources = ["Onboarding"] if adr_from_onboarding_verified else ["Benchmark"]
```

**Acoplamiento incorrecto**: `confidence` y `sources` se derivan de `adr_from_onboarding_verified` (flag booleano que solo verifica existencia del valor en el YAML), pero `value` viene de `adr_cop` (que puede ser regional si el harness ignoró el onboarding). **No hay invariante que ligue `value` con `sources`**.

### H4 — Sin tests end-to-end onboarding → harness → JSON (MEDIA)

**Tests existentes** (todos aislados, 92 pasan):
- `tests/financial_engine/test_adr_resolution_wrapper.py` — prueba el wrapper con `user_provided_adr` directo ✅
- `tests/financial_engine/test_fallback_chain_honesto.py` — prueba la cascada de fallback ✅
- `tests/test_onboarding.py` — prueba el loader de YAML ✅

**Tests faltantes** (gap):
- ❌ Ningún test asserta que el `payload` del `AgentTask` incluya `user_provided_adr` cuando hay YAML
- ❌ Ningún test asserta que `financial_scenarios.json:input_data.adr_cop` refleje el valor del YAML
- ❌ Ningún test asserta que `financial_scenarios.json:input_data.adr_source` NO sea `"handler"`
- ❌ Ningún test asserta que `ValidationSummary` no tenga `confidence=VERIFIED` cuando el `value` no vino del onboarding

---

## 5. BUG-2: Template "Complete Onboarding" Siempre Visible (ALTA)

### Síntoma
El bloque de línea 88 en el diagnóstico siempre dice:
```
> ¿Quiere saber su cifra exacta? Complete el onboarding con sus datos reales:
> número de habitaciones, reservas mensuales promedio, valor promedio de
> reserva (COP) y porcentaje de canal directo.
```
**Incluso cuando** el log muestra `✅ Onboarding data loaded: 6 campos confirmados`.

Confirmado en output real: `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260722_162501.md:88`.

### Cadena Causal

**Ubicación**: `modules/commercial_documents/v4_diagnostic_generator.py:1259-1267`
```python
if not can_show_exact:  # can_show_exact = False cuando precision_tier != "A"
    show_onboarding_cta = (
        "\n> **¿Quiere saber su cifra exacta?** "
        "Complete el onboarding con sus datos reales: "
        "número de habitaciones, reservas mensuales promedio, "
        "valor promedio de reserva (COP) y porcentaje de canal directo. "
        "Así podrá ver el cálculo preciso de su pérdida mensual.\n"
    )
else:
    show_onboarding_cta = ""
```

**Causa raíz**: `can_show_exact` depende de `precision_tier`. El flag `has_onboarding` **existe** en `main.py:2106` (`has_onboarding = onboarding_data is not None`) pero **nunca se pasa** a `diagnostic_gen.generate()` (L2496). La firma `generate()` (L441-455) no recibe este parámetro. No existe lógica para distinguir:
- "No tengo onboarding → necesito pedir datos" (caso original)
- "Tengo onboarding pero el tier sigue siendo B/C → los datos ya están, solo falta GA4" (caso real)

### Amplificación: 7 mensajes de onboarding en 3 superficies

1. **Diagnóstico** — CTA hardcodeado (L1259-1267)
2. **Diagnóstico** — Nota assets baja confianza: "Ejecute onboarding con datos reales" (L2493-2496)
3. **Diagnóstico** — Banner Tier C: "ejecute onboarding con datos reales" (L1084-1088)
4. **Propuesta** — `propuesta_v6_template.md:102`: "ejecute el onboarding con datos reales" (condicional Tier C)
5. **Propuesta** — `propuesta_v6_template.md:104`: "completar el proceso de onboarding" (condicional Tier C)
6. **Propuesta** — `propuesta_v6_template.md:126`: "complete el proceso de onboarding (15 minutos)" (condicional Tier C)
7. **Log final** — `main.py:3281`: "Para precisar las cifras, ejecute con datos operativos: python main.py onboard"

**Interacción con BUG-1**: Si BUG-1 se corrige (ADR pasa a `user_provided`) y el occupancy deja de ser sobrescrito por regional, `can_show_exact_money` podría pasar a `True` → el CTA del diagnóstico se silencia automáticamente. Pero la propuesta sigue teniendo sus propios condicionales Tier C.

### Fix Propuesto

Agregar condición de onboarding:
```python
if not can_show_exact and not has_onboarding:
    show_onboarding_cta = "Complete el onboarding..."
elif not can_show_exact and has_onboarding:
    show_onboarding_cta = (
        "\n> ✅ **Datos operativos verificados.** "
        "Para obtener la cifra exacta al peso, conecte Google Analytics 4 "
        "y confirme las comisiones reales de OTAs.\n"
    )
else:
    show_onboarding_cta = ""
```

**Propagación** (dos opciones, ordenadas por menor invasividad):
- **Opción B (recomendada)**: Inferir `has_onboarding` de `validation_summary.fields[i].sources` — si algún campo tiene `sources=["Onboarding"]`, onboarding está cargado. No requiere cambio de firma del generador.
- **Opción A**: Pasar `onboarding_loaded: bool` como parámetro adicional a `generate()`.

### Archivos Afectados
- `modules/commercial_documents/v4_diagnostic_generator.py` — L1259-1270 (template CTA)
- `modules/commercial_documents/v4_diagnostic_generator.py` — L2493-2496 (nota assets confianza)
- `modules/commercial_documents/v4_diagnostic_generator.py` — L1084-1088 (banner Tier C)
- `modules/commercial_documents/templates/propuesta_v6_template.md` — L102, L104, L126 (condicionales Tier C)

---

## 6. BUG-3: Escenario Optimista Negativo (BAJA — diseño, no bug)

### Síntoma
El escenario "optimista" produce valores negativos:
- Run 1: -$270,950 COP/mes
- Run 2: -$1,192,181 COP/mes

### Veredicto de auditoría: **NO es un bug. Es una decisión de diseño.**

6 artefactos en el código tratan el escenario negativo como intencional:

1. `scenario_calculator.py:62-64` — `is_net_gain = monthly_loss_cop < 0`
2. `scenario_calculator.py:67-73` — `display_label` muestra "Ganancia neta" cuando negativo
3. `scenario_calculator.py:384-386` — `get_hook_range` usa `abs()` para mostrar como ahorro
4. `main.py:2220-2221` — log `[INFO] Escenario 'optimista' negativo: representa EQUILIBRIO/GANANCIA`
5. `tests/financial_engine/test_scenario_calculator.py:625-698` — clase `TestOptimistaFix` con 5 tests
6. `modules/quality_gates/commercial_gate.py:328-362` — `CG-SCENARIO-NEGATIVE` bloquea propuestas con optimista negativo

### Fix (no recomendado "clamp a 0")
El fix de "clamp a max(0, valor)" destruiría la semántica correcta de "ganancia neta". Si se desea cambiar, la opción correcta es **renombrar** la etiqueta a "Equilibrio / Sin pérdida neta" o "Break-even" sin modificar el valor numérico. Pero esto requiere revisar el gate `CG-SCENARIO-NEGATIVE` que actualmente bloquea propuestas con optimista negativo (porque no puede mostrarse como "recuperación").

---

## 7. Evidencia Comparativa

### Tabla de Diferencias (Run 1 defaults vs Run 2 "onboarding")

| Campo | Run 1 (default) | Run 2 ("real") | Δ | Source Run 2 | Nota de auditoría |
|-------|-----------------|----------------|---|-------------|-------------------|
| rooms | 10 | 11 | +1 | onboarding ✅ | |
| occupancy_rate | 0.512 | 0.4242 | -17.1% | onboarding ✅ | **PERO el harness lo sobrescribe a 0.512** (ver NEW-1) |
| direct_channel | 0.20 | 0.30 | +50% | onboarding ✅ | |
| adr_cop | $420,000 | $420,000 | 0 | **handler ❌** | Debería ser $330,000. El harness ignora el onboarding. |
| noches OTA | 122 | 98 | -19.7% | derivado | |
| OTA commission | $7,741,440 | $6,174,000 | -20.2% | derivado | Usa ADR=$420K, occ=0.512 (AMBOS ignoran onboarding) |
| Conservative | $7,276,954 | $7,004,068 | -3.7% | derivado | Usa ADR=$420K, occ=0.512 |
| Realistic | $3,741,696 | $3,157,862 | -15.6% | derivado | 3,157,862 = fórmula con occ=0.512 (NO 0.4242) |
| Optimistic | -$270,950 | -$1,192,182 | -340% | derivado | |
| Coherence Score | 0.897 | 0.947 | +5.6% | gates ✅ | |
| financial_data_validated | 0.700 | 0.950 | +35.7% | gates ✅ | |
| financial_validity gate | "Tier C defaults" | "All validated" | ✅ | gates ✅ | |
| pain_ratio | 13.61% | 12.37% | -9.1% | derivado | |
| ROI | 9.3x | 7.9x | -15.1% | derivado | Ambos sobredimensionados (ver F1) |

### Archivos Generados en Cada Run

| Archivo | Run 1 | Run 2 |
|---------|-------|-------|
| Diagnóstico | `01_..._20260722_155824.md` | `01_..._20260722_162501.md` |
| Propuesta | `02_..._20260722_155838.md` | `02_..._20260722_162515.md` |
| Financial scenarios | `financial_scenarios_20260722_155818.json` | `financial_scenarios_20260722_162455.json` |
| Gate report | `gate_report_20260722_155838.json` | `gate_report_20260722_162515.json` |
| Log | `ejecucion.log` | `ejecucion-con-datos-reales.log` |

---

## 8. Datos del Onboarding YAML

Archivo: `output/clientes/donalfonsohotel_onboarding.yaml`

```yaml
hotel:
  nombre: "Hotel Don Alfonso"
  ubicacion: "Carrera 13 #12-37 Av Alfonso Jaramillo, Pereira, Risaralda"
datos_operativos:
  habitaciones: 11
  reservas_mes: 140
  valor_reserva_cop: 330000
  canal_directo_pct: 30.0
  adr_cop: 330000
  occupancy_rate: 0.4242
  is_transit_hotel: false
  ota_percentage: 70.0
metadatos:
  fuente: "contacto_directo_observations_json"
  fecha_captura: "2026-07-22T16:00:00+00:00"
  campos_confirmados:
    - habitaciones
    - reservas_mes
    - valor_reserva_cop
    - canal_directo_pct
    - adr_cop
    - occupancy_rate
  confidence: 0.95
  epistemic_status: "verified"
```

---

## 9. Ruta de Código Relevante

### Flujo de carga de onboarding
```
main.py:1641  → hotel_name = _extract_hotel_name_from_url(args.url)
main.py:1739  → onboarding_data = _load_latest_onboarding_data(args.url, hotel_name)
                → busca: output/clientes/{generate_slug(hotel_name)}_onboarding.yaml
                → frescura: < 24h desde fecha_captura
main.py:1746  → datos_operativos = onboarding_data.get('datos_operativos', {})
main.py:1747  → rooms = datos_operativos.get('habitaciones', 10)
main.py:1749  → occupancy_rate = reservas_mes / (rooms * 30)
main.py:1761  → canal_directo = datos_operativos.get('canal_directo_pct', 20.0)
main.py:1765  → adr_from_onboarding = datos_operativos.get('valor_reserva_cop')  ← 330000
```

### Flujo financiero (donde se pierde el ADR y el occupancy)
```
main.py:1797  → financial_task = AgentTask(payload={rooms, region, occupancy, direct_channel, ...})
                ❌ NO incluye user_provided_adr
main.py:1810  → financial_result = harness.run_task(financial_task)
                → harness_handlers.py:49 → user_provided_adr = None
                → harness_handlers.py:65 → resolve_adr_with_shadow(user_provided_adr=None)
                → harness_handlers.py:91-99 → occupancy_rate = regional (SOBRESCRITO)
                → adr_cop = 420000, occupancy_rate = 0.512 (AMBOS ignoran onboarding)
main.py:1814  → adr_cop = result_data["adr_cop"]  ← 420000 (equivocado)
main.py:1861  → adr_source = result_data.get("adr_source", "handler")  ← placeholder muerto
```

### Construcción de ValidationSummary
```
main.py:2107  → adr_from_onboarding_verified = (adr_from_onboarding is not None and > 0)  ← True
main.py:2162  → confidence = VERIFIED (porque adr_from_onboarding_verified=True)
main.py:2166  → value=adr_cop  ← 420000 (INCORRECTO — el flag dice verified pero el valor es del benchmark)
```

### Template de diagnóstico
```
v4_diagnostic_generator.py:1259  → if not can_show_exact:
v4_diagnostic_generator.py:1262  →   show_onboarding_cta = "Complete el onboarding..."
                                     ← NO verifica si onboarding ya fue cargado
```

### Consumidor paralelo en propuesta (H1)
```
v4_proposal_generator.py:760   → _adr_value = self._get_adr_from_benchmarks(region)
v4_proposal_generator.py:1869  → resolver.resolve(region, rooms=0, user_provided_adr=None)
                                   ← SIEMPRE retorna benchmark regional, ignora onboarding
```

---

## 10. Causa Raíz

El defecto NO es "olvidé pasar `user_provided_adr`". Es un **patrón arquitectónico** con 3 fallas:

1. **El orquestador no propaga metadata de provenance al harness** — el payload transporta valores numéricos (rooms, occupancy, direct_channel) pero no su fuente. El handler recibe datos sin contexto.
2. **Cuando el orquestador reconstruye la metadata (ValidationSummary), asume que los valores finales reflejan las fuentes originales** — asunción que el path del harness viola sistemáticamente.
3. **Existen 3 vocabularios incompatibles para "fuente del ADR"** (`ADRSource` enum, `ValidationSummary.sources`, `JSON input_data.adr_source`) que deberían ser una sola taxonomía.

---

## 11. Soluciones Propuestas (ordenadas por costo/beneficio)

### Para BUG-1 + NEW-1 (ADR + occupancy)

| Opción | Alcance | Costo | Cubre |
|--------|---------|-------|-------|
| **A (mínima)** | Agregar `user_provided_adr` al payload del harness (main.py:1806). Agregar flag `occupancy_source` para que el handler no sobrescriba si viene de onboarding. | Bajo — 2 archivos, ~5 líneas | Solo el síntoma de BUG-1 + NEW-1 |
| **B (mínima + H1)** | Opción A + reemplazar `_get_adr_from_benchmarks` en proposal generator para recibir `adr_from_onboarding` del orquestador. | Medio — 3 archivos | BUG-1 + NEW-1 + inconsistencia diagnóstico/propuesta |
| **C (robusta, RECOMENDADA)** | Opción B + unificar taxonomía de fuentes a `ADRSource.value` en las 3 capas + cambiar `confidence`/`sources` en ValidationSummary para reflejar fuente real + arreglar `main.py:1861` para leer `result_data["adr_resolution"]["source"]` + 3-4 tests e2e. | Alto — 5+ archivos, nuevos tests | BUG-1 + NEW-1 + H1 + H2 + H3 + H4 |
| **D (refactor mayor)** | Opción C + extraer `build_validated_field(name, value, source)` centralizado + eliminar duplicación de vocabularios + migrar a contrato de tipos para payload del harness. | Muy alto — cambio arquitectónico | Todo + deuda técnica estructural |

### Para BUG-2 (CTA redundante)

| Opción | Alcance |
|--------|---------|
| **A** | Pasar `onboarding_loaded: bool` como parámetro a `generate()`. |
| **B (RECOMENDADA)** | Inferir `has_onboarding` de `validation_summary.fields[i].sources` — si algún campo tiene `sources=["Onboarding"]`, onboarding está cargado. No requiere cambio de firma. |
| **C** | Opción B + unificar los 7 CTAs en una función `_build_onboarding_cta(has_onboarding, precision_tier)` que decida el mensaje correcto según contexto real. |

---

## 12. Checklist para Plan de Refactorización

### BUG-1 + NEW-1 (ADR + occupancy)
- [ ] Agregar `user_provided_adr` al payload del harness (1 línea en main.py:1806)
- [ ] Agregar flag `occupancy_source` al payload para que el handler no sobrescriba (`harness_handlers.py:91-99`)
- [ ] Reemplazar `_get_adr_from_benchmarks` en proposal generator (H1 — `v4_proposal_generator.py:1859-1873`)
- [ ] Arreglar `main.py:1861` para leer `result_data["adr_resolution"]["source"]` en lugar del placeholder `"handler"`
- [ ] Unificar taxonomía de fuentes: cambiar `ValidationSummary.sources` para derivar de `ADRSource.value` (H2)
- [ ] Cambiar lógica de `confidence`/`sources` en ValidationSummary para reflejar fuente REAL del valor (H3)
- [ ] Test: verificar `adr_cop` en `financial_scenarios.json = 330000` post-fix
- [ ] Test: verificar `adr_source != "handler"` en `financial_scenarios.json`
- [ ] Test: verificar que `ValidationSummary` no tiene `confidence=VERIFIED` cuando `value` no vino del onboarding
- [ ] Test e2e: YAML → harness → JSON → documento

### BUG-2 (CTA redundante)
- [ ] Propagar flag `has_onboarding` al generador (inferir de `validation_summary.sources`, Opción B)
- [ ] Modificar CTA del diagnóstico para distinguir "sin onboarding" vs "con onboarding sin GA4"
- [ ] Revisar los 7 CTAs en diagnóstico, propuesta y log final para consistencia
- [ ] Test: verificar que el CTA NO aparece cuando hay onboarding cargado

### BUG-3 (opcional)
- [ ] Renombrar etiqueta de "Optimista" a "Equilibrio / Sin pérdida neta" si se desea cambiar UX
- [ ] Revisar interacción con `CG-SCENARIO-NEGATIVE` si se renombra

### Regresión y E2E
- [ ] `python -m pytest tests/financial_engine tests/commercial_documents -v`
- [ ] Re-ejecutar v4complete con onboarding y comparar cifras esperadas vs reales
- [ ] Verificar consistencia ADR entre diagnóstico y propuesta (mismo valor en ambos documentos)
