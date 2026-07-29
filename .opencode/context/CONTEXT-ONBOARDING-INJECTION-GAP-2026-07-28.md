# Contexto: Gap de Inyección Onboarding → v4complete — Flujo Bimodal Tier B → Tier A

> **Origen**: Validación de ejecución v4complete para Zione.co (2026-07-28) contra datos reales de onboarding
> **Versión actual**: v4.65.0
> **Hotel de referencia**: Zi One Luxury (https://zione.co/)
> **Severidad**: ALTA — las 2 ejecuciones de v4complete producen documentos Tier B idénticos ignorando datos Tier A verificados
> **Fecha del contexto**: 2026-07-28
> **Output de referencia**: `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260728_122913.md`, `output/v4_complete/02_PROPUESTA_COMERCIAL_20260728_122913.md`
> **ESTADO**: Verificado contra código vivo — se identificaron 2 bugs en `_load_latest_onboarding_data()` que bloquean la inyección de datos reales

---

## 1. Archivos fuente de esta validación

| Archivo | Rol |
|---------|-----|
| `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260728_122913.md` | Diagnóstico generado (Tier B) |
| `output/v4_complete/02_PROPUESTA_COMERCIAL_20260728_122913.md` | Propuesta generada (Tier B) |
| `output/v4_complete/zione/v4_audit/financial_scenarios_20260728_122901.json` | Escenarios financieros usados (Tier B) |
| `output/v4_complete/zione/v4_audit/financial_scenarios_20260728_180531.json` | Escenarios 2a ejecución (idénticos, Tier B) |
| `output/clientes/zi-one-luxury_onboarding.yaml` | Datos reales Tier A (ignorados por el pipeline) |
| `data/hotel_observations/observations.json` | Observaciones verificadas (Zi One Luxury: confidence 0.95, Tier A) |

---

## 2. El flujo bimodal (arquitectura intencionada)

El pipeline está diseñado para dos pasadas:

```
PASADA 1 (Tier B) — WhatsApp inicial
  v4complete --url https://zione.co/
  → Usa benchmarks regionales
  → Genera 01_DIAGNOSTICO + 02_PROPUESTA con cifras estimadas
  → El hotel recibe el hook, se interesa, responde con sus datos reales

PASADA 2 (Tier A) — Con datos reales del hotel
  onboard --url https://zione.co/ --hotel-name "Zi One Luxury"
  → Captura datos operativos (habitaciones, reservas, ADR, canal directo)
  → Guarda en output/clientes/{slug}_onboarding.yaml

  v4complete --url https://zione.co/ --force-new
  → _load_latest_onboarding_data() carga el .yaml
  → Inyecta rooms, occupancy_rate, direct_channel_pct, user_provided_adr
  → ADR resolver da prioridad máxima a user_provided_adr
  → Genera 01_DIAGNOSTICO + 02_PROPUESTA con cifras EXACTAS (Tier A)
```

## 3. El punto de inyección (main.py)

La función `_load_latest_onboarding_data()` en `main.py:3396-3445` es el único punto donde v4complete intenta cargar datos de onboarding:

```python
# main.py:1739
onboarding_data = _load_latest_onboarding_data(args.url, hotel_name)
```

Cuando encuentra datos, los usa para poblar (líneas 1745-1788):

```python
rooms = datos_operativos.get('habitaciones', 10)           # ← real: 34
occupancy_rate = reservas_mes / (rooms * 30)               # ← real: 78.4%
direct_channel_pct = canal_directo / 100                   # ← real: 40%
adr_from_onboarding = datos_operativos.get('valor_reserva_cop')  # ← real: $290K
```

Y el ADR resolver (línea 1894) da prioridad máxima a `user_provided_adr`:

```python
# modules/financial_engine/adr_resolution_wrapper.py:173
if user_provided_adr is not None:
    # User measured value takes precedence
    return ADRResolutionResult(..., epistemic_status="measured", can_show_exact=True)
```

**La arquitectura ES correcta. El problema está en `_load_latest_onboarding_data()` que nunca retorna datos para Zi One Luxury.**

---

## 4. BUG 1 — Slug mismatch (bloqueante)

**Archivo**: `main.py:3414`

```python
hotel_slug = generate_slug(hotel_name)         # "Zione" → "zione"
onboarding_file = output_dir / f"{hotel_slug}_onboarding.yaml"  # busca: zione_onboarding.yaml
```

El archivo real en disco es `zi-one-luxury_onboarding.yaml` (guardado por el comando `onboard` que usa `generate_slug("Zi One Luxury")` → `"zi-one-luxury"`).

| Variable | Valor |
|---|---|
| `hotel_name` desde URL `zione.co` | `"Zione"` |
| `generate_slug("Zione")` | `"zione"` |
| Archivo buscado | `output/clientes/zione_onboarding.yaml` |
| Archivo real | `output/clientes/zi-one-luxury_onboarding.yaml` |
| **Match** | **NO** |

**Causa raíz**: `onboard` usa `--hotel-name "Zi One Luxury"` para derivar el slug, pero `v4complete` deriva `hotel_name` de la URL (`zione.co` → `"Zione"`). Los slugs nunca coinciden para hoteles cuyo nombre difiere de su dominio.

---

## 5. BUG 2 — Ventana de frescura de 24h (bloqueante)

**Archivo**: `main.py:3438`

```python
if diferencia > timedelta(hours=24):
    return None
```

Los datos de Zi One Luxury tienen `fecha_captura: 2026-07-23T10:00:00+00:00`. Al ejecutar v4complete el 2026-07-28, la diferencia es de ~5 días → la función retorna `None`.

**Impacto**: Incluso si se corrige el BUG 1 (slug), los datos son rechazados por "stale". En la práctica, el flujo real es:
1. Se envía WhatsApp con Tier B (día 0)
2. El hotel tarda 2-7 días en responder con sus datos
3. Cuando se ejecuta v4complete de nuevo, los datos ya tienen >24h → ignorados

**La ventana de 24h es inconsistente con el ciclo real de ventas.**

---

## 6. Evidencia: 2 ejecuciones produjeron resultados idénticos

Se ejecutó v4complete 2 veces (122913 y 180531). Ambas produjeron `financial_scenarios.json` idénticos:

```json
{
  "input_data": {
    "rooms": 10,
    "adr_cop": 420000,
    "adr_source": "regional_v410",
    "occupancy_rate": 0.512,
    "direct_channel_percentage": 0.2
  },
  "scenarios": {
    "conservative": 7276953.6,
    "realistic": 3741696.0,
    "optimistic": -270950.4
  }
}
```

En ambas ejecuciones, el log muestra: `"Using defaults (no fresh onboarding data found)"`.

---

## 7. Impacto financiero del gap

### Datos de entrada

| Parámetro | Real (Tier A) | Usado (Tier B) | Desviación |
|---|---|---|---|
| Habitaciones | **34** | 10 | -71% |
| ADR | **$290,000** | $420,000 | +45% |
| Ocupación | **78.4%** | 51.2% | -35% |
| Canal directo | **40%** | 20% | -50% |

### Escenarios financieros

| Métrica | Tier B (actual) | Tier A (real) | Delta |
|---|---|---|---|
| Comisión OTA/mes | $7,741,440 | $20,879,634 | **+$13.1M (2.7x)** |
| Fuga realista/mes | $3,741,696 | $7,191,874 | **+$3.4M (1.9x)** |
| Fuga 6 meses | $22,450,176 | $43,151,244 | +$20.7M |
| Recovery 6m | $1,571,512 | $3,020,587 | +$1.4M |
| ROICR | 0.7x | **1.3x** | +86% |
| Pain ratio | 5.2% | **1.9%** | fee 2.7x menos doloroso |

### Impacto en la propuesta comercial

- El fee de $400K/mes es solo **1.9%** de la fuga real (vs 5.2% actual) → propuesta más irresistible
- **ROICR pasa de 0.7x a 1.3x** → de "apenas se paga" a "retorno claro"
- La fuga real es **casi el doble** → urgencia mucho mayor para el hotel
- El escenario optimista da **ganancia neta real de $6.8M/mes** (vs $271K actual)

---

## 8. Código involucrado

| Módulo | Función/Clase | Línea | Rol |
|--------|--------------|-------|-----|
| `main.py` | `_load_latest_onboarding_data()` | 3396-3445 | Carga datos de onboarding — **BUG 1 y 2 aquí** |
| `main.py` | `run_v4_complete_mode()` | 1739-1788 | Usa onboarding_data para poblar financial inputs |
| `main.py` | `run_v4_complete_mode()` | 1891-1899 | Pasa `user_provided_adr` al ADR resolver |
| `main.py` | `run_onboard_mode()` | 1041-1119 | Guarda datos como `{slug}_onboarding.yaml` |
| `modules/onboarding/data_loader.py` | `generate_slug()` | 125-143 | Derivación de slug — usada por ambos, pero con inputs distintos |
| `modules/financial_engine/adr_resolution_wrapper.py` | `ADRResolutionWrapper.resolve()` | 68-134 | Cadena de fallback: user_provided > web_scraping > regional > legacy |
| `modules/financial_engine/scenario_calculator.py` | `ScenarioCalculator` | 105-535 | Cálculo de escenarios con HotelFinancialData |

---

## 9. Fixes recomendados

### Fix 1 — BUG 1: Búsqueda de onboarding por glob, no por slug derivado

```python
# En _load_latest_onboarding_data(), reemplazar:
hotel_slug = generate_slug(hotel_name)
onboarding_file = output_dir / f"{hotel_slug}_onboarding.yaml"

# Por búsqueda por glob de todos los *_onboarding.yaml y matching por nombre de hotel:
for f in output_dir.glob("*_onboarding.yaml"):
    data = yaml.safe_load(f.read_text(encoding='utf-8'))
    if data.get('hotel', {}).get('nombre', '').lower() == hotel_name.lower():
        # ... validar frescura y retornar
```

### Fix 2 — BUG 2: Ventana de frescura configurable o eliminada

```python
# Opción A: Eliminar el check de frescura (el dato operativo no se vuelve obsoleto)
# Opción B: Hacerla configurable (7 días por defecto):
FRESHNESS_HOURS = int(os.getenv("ONBOARDING_FRESHNESS_HOURS", "168"))  # 7 días
if diferencia > timedelta(hours=FRESHNESS_HOURS):
    return None
```

### Fix 3 — Consistencia de slug entre onboard y v4complete

```python
# En run_onboard_mode(), guardar también con el slug derivado de URL:
url_slug = generate_slug(_extract_hotel_name_from_url(args.url))
# Guardar ambos: {hotel_slug}_onboarding.yaml Y {url_slug}_onboarding.yaml (symlink o copia)
```

---

## 10. Verificación post-fix

Para validar que los fixes funcionan:

```bash
# 1. Asegurar que el archivo de onboarding existe con el slug correcto
cp output/clientes/zi-one-luxury_onboarding.yaml output/clientes/zione_onboarding.yaml

# 2. Actualizar fecha_captura para que pase el check de frescura
#    (o aplicar Fix 2 primero)

# 3. Re-ejecutar v4complete
python main.py v4complete --url https://zione.co/ --force-new

# 4. Verificar que financial_scenarios.json ahora tiene:
#    rooms=34, adr_cop=290000, occupancy_rate=0.7843, direct_channel_percentage=0.4

# 5. Verificar que 01_DIAGNOSTICO muestra cifras Tier A (~$20.8M comisión OTA)
```

---

## 11. Notas adicionales

- **El comando `audit` está deprecado** (main.py:1126). La migración a v4complete es completa. El mensaje `"python main.py audit --url <URL> --input-data {output_path}"` que sugiere `run_onboard_mode()` (línea 1118) apunta a un comando legacy que no debe usarse.
- **El comando `execute` con `--input-data`** no regenera diagnóstico ni propuesta — solo ejecuta delivery de assets. Es un flujo distinto.
- **`_determine_evidence_tier()` en `scenario_calculator.py:480`** no reconoce `'onboarding_confirmado'` como fuente verificada (solo acepta `'onboarding'`, `'verified'`, `'industry_standard_15pct'`). Esto es un bug menor: incluso con datos reales inyectados, el tier se queda en B. Debería agregarse `'onboarding_confirmado'` a la lista de `verified_sources`.
- **El `observations.json` en `data/hotel_observations/`** contiene datos Tier A verificados (confidence 0.95) para 6 hoteles, incluyendo Zi One Luxury. Actualmente NO es consultado por v4complete — solo lo usa el `onboarding_controller` para cross-validation. Podría ser una fuente adicional de datos reales.

---

*Contexto generado por validación de ejecución v4complete 2026-07-28.*
*Para reanudar: cargar este contexto + `iah-cli-execution-conventions` + `iah-cli-v4complete-workflows`.*
