# Contexto: Gap de Inyección Onboarding → v4complete — Flujo Bimodal Tier B → Tier A

> **Origen**: Validación de ejecución v4complete para Zione.co (2026-07-28) contra datos reales de onboarding
> **Versión actual**: v4.65.0
> **Hotel de referencia**: Zi One Luxury (https://zione.co/)
> **Severidad**: ALTA — las 2 ejecuciones de v4complete producen documentos Tier B idénticos ignorando datos Tier A verificados
> **Fecha del contexto**: 2026-07-28
> **Output de referencia**: `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260728_122913.md`, `output/v4_complete/02_PROPUESTA_COMERCIAL_20260728_122913.md`
> **ESTADO**: Verificado contra código vivo + amplificado + rediseñado. Se confirmaron 2 bugs bloqueantes y se descubrieron 3 adicionales (N3-N5). La nota §11 sobre `_determine_evidence_tier()` fue corregida: el impacto real no es "tier B" sino `user_provided` invisible al tiering. Los fixes 1+2+5 originales fueron reemplazados por un diseño integrado basado en URL como clave canónica de matching tras auditoría de la brecha de fuzzy matching.

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
# modules/financial_engine/adr_resolution_wrapper.py:173-200
if user_provided_adr is not None:
    # User measured value takes precedence
    return ADRResolutionResult(..., epistemic_status="measured", can_show_exact=True)
```

**La arquitectura ES correcta. El problema está en `_load_latest_onboarding_data()` que nunca retorna datos para Zi One Luxury.**

---

## 4. BUG 1 — Slug mismatch (bloqueante) ✅ CONFIRMADO

**Archivo**: `main.py:3414`

```python
hotel_slug = generate_slug(hotel_name)         # "Zione" → "zione"
onboarding_file = output_dir / f"{hotel_slug}_onboarding.yaml"  # busca: zione_onboarding.yaml
```

El archivo real en disco es `zi-one-luxury_onboarding.yaml` (guardado por el comando `onboard` que usa `generate_slug("Zi One Luxury")` → `"zi-one-luxury"`).

| Variable | Valor |
|---|---|
| `hotel_name` desde URL `zione.co` | `"Zione"` (main.py:1641 → `_extract_hotel_name_from_url()`) |
| `generate_slug("Zione")` | `"zione"` |
| Archivo buscado | `output/clientes/zione_onboarding.yaml` |
| Archivo real | `output/clientes/zi-one-luxury_onboarding.yaml` |
| **Match** | **NO** |

**Causa raíz**: `onboard` usa `--hotel-name "Zi One Luxury"` para derivar el slug, pero `v4complete` deriva `hotel_name` de la URL (`zione.co` → `"Zione"`). Los slugs nunca coinciden para hoteles cuyo nombre difiere de su dominio. No existe un identificador canónico de hotel compartido entre ambos comandos. La función `generate_slug()` es determinista pero recibe inputs distintos en cada flujo.

### Evidencia de código vivo

- `_extract_hotel_name_from_url()` (main.py:3448-3452): `domain = urlparse(url).netloc.replace('www.', '').split('.')[0]; return domain.replace('-', ' ').replace('_', ' ').title()`
- `run_onboard_mode()` (main.py:1053-1057): `hotel_nombre = args.hotel_name or args.nombre or ""; if not hotel_nombre and args.url: ...hotel_nombre = domain.replace('-', ' ').replace('_', ' ').title()`
- `generate_slug()` (modules/onboarding/data_loader.py:125-143): transforma minúsculas, reemplaza espacios/underscores por guiones.
- Archivo YAML real: `output/clientes/zi-one-luxury_onboarding.yaml` — 19 líneas, `hotel.nombre: Zi One Luxury`, `datos_operativos.habitaciones: 34`, `valor_reserva_cop: 290000`.

---

## 5. BUG 2 — Ventana de frescura de 24h (bloqueante) ✅ CONFIRMADO

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

### Evidencia de código vivo

- `main.py:3431-3439`: `fecha_captura = datetime.fromisoformat(fecha_captura_str.replace('Z', '+00:00')); ahora = datetime.now(timezone.utc); diferencia = ahora - fecha_captura; if diferencia > timedelta(hours=24): return None`
- YAML línea 11: `fecha_captura: '2026-07-23T10:00:00+00:00'`
- Diferencia al 2026-07-28: ~120 horas >> 24 horas.

**Causa raíz**: La ventana de frescura asume un flujo de trabajo interactivo en sesión única que no refleja la realidad del ciclo de ventas (time-to-response del hotel: 2-7 días). El dato operativo (habitaciones, ADR, canal) no se vuelve obsoleto en 24h — es información estructural del hotel.

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

En ambas ejecuciones, el log muestra: `"Using defaults (no fresh onboarding data found)"` (main.py:1769).

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
| `main.py` | `_load_latest_onboarding_data()` | 3396-3445 | Carga datos de onboarding — **BUG 1, 2, N3, N4 aquí** |
| `main.py` | `run_v4_complete_mode()` | 1577-2100 | Orquestador v4complete — llama a `_load_latest_onboarding_data()` en 1739 |
| `main.py` | `run_v4_complete_mode()` | 1739 | Pasa `args.url` y `hotel_name`; NO pasa `output_dir` (N4) |
| `main.py` | `run_v4_complete_mode()` | 1745-1788 | Usa onboarding_data para poblar financial inputs |
| `main.py` | `run_v4_complete_mode()` | 1641 | Deriva `hotel_name` de URL o `--nombre` |
| `main.py` | `run_v4_complete_mode()` | 1996-2004 | Construye `HotelFinancialData` con `occupancy_source='onboarding'` / `channel_source='onboarding'` |
| `main.py` | `run_v4_complete_mode()` | 1891-1899 | Pasa `user_provided_adr` al ADR resolver |
| `main.py` | `run_onboard_mode()` | 1041-1119 | Guarda datos como `{slug}_onboarding.yaml` — NO escribe `hotel.url` |
| `main.py` | `run_onboard_mode()` | 1068 | `output_dir = Path(args.output) / "clientes"` (configurable) |
| `main.py` | `_extract_hotel_name_from_url()` | 3448-3452 | Derivación de nombre desde URL — usada por v4complete |
| `modules/onboarding/data_loader.py` | `generate_slug()` | 125-143 | Derivación de slug — usada por ambos, pero con inputs distintos |
| `modules/onboarding/data_loader.py` | `_merge_onboarding_data()` | 70-96 | Marca campos con fuente `"onboarding_confirmado"` |
| `modules/financial_engine/adr_resolution_wrapper.py` | `ADRResolutionWrapper._new_resolution_with_scraping()` | 161-203 | user_provided_adr gana (source=`"user_provided"`, epistemic_status=measured) |
| `modules/financial_engine/adr_resolution_wrapper.py` | `ADRSource` enum | 23-28 | `USER_PROVIDED = "user_provided"` |
| `modules/financial_engine/scenario_calculator.py` | `ScenarioCalculator._determine_evidence_tier()` | 480-504 | Tiering — **BUG §11a aquí: `"user_provided"` invisible** |
| `modules/financial_engine/scenario_calculator.py` | `ScenarioCalculator._trace_data_sources()` | 524-534 | Trazabilidad de fuentes para tiering |
| `data/hotel_observations/observations.json` | — | 114-133 | Datos Zi One Luxury Tier A (confidence 0.95) — **NO integrado en v4complete** |

---

## 9. BUGS ADICIONALES DESCUBIERTOS (no en el contexto original)

### NUEVO BUG N3 — `hotel_url` aceptado pero ignorado en `_load_latest_onboarding_data()`

**Archivo**: `main.py:3396`

```python
def _load_latest_onboarding_data(hotel_url: str, hotel_name: str) -> Dict[str, Any] | None:
```

El parámetro `hotel_url` es aceptado en la firma pero NUNCA se usa en el cuerpo de la función (3396-3445). Es un parámetro vestigial.

**Causa raíz**: Parámetro agregado por forward-compat pero nunca implementado. Contribuye a que la función dependa ÚNICAMENTE del nombre derivado de URL sin poder usar la URL como clave secundaria de matching.

**Severidad**: MEDIA (contribuye y amplifica BUG 1).

---

### NUEVO BUG N4 — `output_dir` hardcodeado en lectura vs configurable en escritura

- `_load_latest_onboarding_data()` (main.py:3410): `output_dir = Path("output/clientes")` — **hardcodeado**
- `run_onboard_mode()` (main.py:1068): `output_dir = Path(args.output) / "clientes"` — **configurable** (default `"./output"`)

Si un usuario ejecuta `onboard --output ./custom_output`, el YAML se guarda en `./custom_output/clientes/` pero `_load_latest_onboarding_data()` busca en `./output/clientes/`.

**Causa raíz**: Divergencia de paths entre escritura (configurable vía `--output`) y lectura (hardcodeada). La función de carga debería aceptar `output_dir` como parámetro o usar el mismo default configurable que el resto del sistema.

**Severidad**: BAJA (condicional — solo afecta cuando `--output` no es `./output`).

---

### NUEVO BUG N5 — Sin estrategia de resolución de identidad del hotel

El sistema actual resuelve `hotel_name` exclusivamente del dominio de la URL (main.py:1641). No hay ningún fallback:

1. No busca en los YAMLs de onboarding por matching de dominio
2. No consulta `observations.json` para obtener el nombre canónico
3. No unifica la identidad entre comandos (`onboard` vs `v4complete`)

**Causa raíz**: No existe un identificador canónico compartido entre comandos. Cada comando (`onboard`, `v4complete`, `execute`) resuelve la identidad del hotel de forma independiente con estrategias potencialmente diferentes. Esto es el problema arquitectónico subyacente del BUG 1.

**Severidad**: MEDIA (causa estructural del BUG 1).

---

## 10. NOTAS CORREGIDAS Y VALIDADAS (§11 del contexto original)

### §10a — `_determine_evidence_tier()` y `onboarding_confirmado` ⚠️ CORREGIDO

**Claim original**: *"incluso con datos reales inyectados, el tier se queda en B"*. **Esto es INCORRECTO.**

El flujo real de v4complete cuando onboarding_data SÍ se carga (main.py:2002-2004):

```python
adr_source=adr_source,                              # → "user_provided" (ADRSource.USER_PROVIDED)
occupancy_source='onboarding',                      # → "onboarding" ✓
channel_source='onboarding',                        # → "onboarding" ✓
```

`_determine_evidence_tier()` (scenario_calculator.py:493-504):

```python
verified_sources = [s for s in [adr_src, occ_src, ch_src]
                  if s in ('onboarding', 'verified', 'industry_standard_15pct')]
# Resultado: verified_sources = ['onboarding', 'onboarding'] → len=2
# low_quality = [] (ni "user_provided" ni "onboarding" están en la lista de baja calidad)
# → len(verified_sources) >= 2 and len(low_quality) == 0 → EvidenceTier.A ✅
```

**El tier SÍ sería A cuando los datos de onboarding se cargan correctamente.**

**El gap real es distinto**: `adr_source = "user_provided"` (la fuente de ADR más confiable posible) NO está en la lista `verified_sources` ni en `low_quality`. Es invisible para el tiering. Esto significa que:

- Si solo el ADR fuera `"user_provided"` (sin otros datos onboardeados), el tiering no lo reconocería como evidencia verificada
- `"user_provided"` debería ser tratado como `epistemic_status="measured"` → equivalente a verificado

**Causa raíz corregida**: La taxonomía de fuentes de ADR (`ADRSource`: `"user_provided"`) y la taxonomía de tier de evidencia (`EvidenceTier`: `'onboarding'`, `'verified'`) NO están alineadas. `"user_provided"` es el dato de mayor calidad epistémica posible pero el tiering no lo reconoce.

**Severidad real**: MEDIA. En la práctica no bloquea Tier A porque occupancy y channel sí están marcados como `"onboarding"`, pero es una inconsistencia taxonómica que podría causar falsos Tier B si solo se onboardea ADR.

### §10b — Comando `audit` deprecado sugerido por onboard ✅ CONFIRMADO

- `run_onboard_mode()` (main.py:1118): `print(f"   2. Ejecuta: python main.py audit --url {url_hint} --input-data {output_path}")`
- `run_audit_mode()` (main.py:1125-1127): marcado `⚠️ DEPRECADO`.
- Mensaje de "próximos pasos" no se actualizó cuando `audit` fue deprecado. Debería sugerir `v4complete`.

### §10c — `observations.json` no consultado por v4complete ✅ CONFIRMADO

- `data/hotel_observations/observations.json` contiene 6 hoteles con datos Tier A (confidence 0.95), incluyendo Zi One Luxury (líneas 114-133, rooms=34, ADR=$290K, occupancy=78.4%).
- `grep -rn "observations.json" --include="*.py"` solo encuentra referencias en `scripts/add_observation.py` y `scripts/validate.py` — scripts de mantenimiento, NO en el pipeline v4complete.
- `_load_latest_onboarding_data()` solo lee de `output/clientes/*_onboarding.yaml`. No hay integración con `observations.json`.
- **Causa raíz**: `observations.json` fue diseñado como warehouse de datos verificados pero nunca se creó un punto de inyección en el pipeline v4complete. El único puente es el YAML de onboarding.

### §10d — `execute` no regenera diagnóstico ni propuesta ✅ CONFIRMADO

- `run_execution_mode()` (main.py:704): usa `DeliveryManager` para entrega de assets. No llama a `ScenarioCalculator`, `FinancialCalculatorV2`, ni generadores de documentos. Es un comando de delivery, no de re-análisis.

---

## 11. TABLA RESUMEN DE SEVERIDAD

| # | Bug | Severidad | Bloquea Tier A? | Causa raíz |
|---|-----|-----------|-----------------|------------|
| B1 | Slug mismatch onboard↔v4complete | **CRÍTICA** | **SÍ** | Doble fuente de identidad (--hotel-name vs URL) sin canonicalización |
| B2 | Ventana frescura 24h hardcodeada | **CRÍTICA** | **SÍ** | Time-to-response real (2-7 días) >> 24h; dato operativo no caduca |
| N3 | `hotel_url` ignorado en loader | MEDIA | Contribuye a B1 | Parámetro forward-compat nunca implementado |
| N4 | `output_dir` hardcodeado en lectura | BAJA | Condicional | Divergencia write-path configurable vs read-path hardcodeado |
| N5 | Sin identity resolver centralizado | MEDIA | Causa B1 | Arquitectura sin canonicalización de identidad entre comandos |
| §10a | `user_provided` invisible al tiering | MEDIA | No (occupancy+channel compensan) | Taxonomías ADRSource y EvidenceTier desalineadas |
| §10b | `audit` deprecado sugerido por onboard | BAJA | No | Mensaje de onboard no actualizado post-deprecación |
| §10c | `observations.json` no integrado | MEDIA | No (usa YAML alternativo) | Sin punto de inyección del warehouse en el pipeline |

---

## 12. DISEÑO DE SOLUCIÓN (enfocado en causa raíz)

### Principio rector

El flujo bimodal prometido en el diagnóstico (línea 84: "Complete el onboarding con sus datos reales... Así podrá ver el cálculo preciso") debe funcionar **para cualquier hotel, con cualquier nombre, desde cualquier `--output`**.

La URL es el único dato que **siempre está presente en ambos comandos** y es **idéntico** en ambos. Por tanto, debe ser la clave canónica de matching.

### Diseño integrado: 3 cambios atómicos que resuelven B1 + N3 + N4 + N5

---

#### CAMBIO A — `onboard` persiste `hotel.url` en el YAML

**Archivo**: `main.py:1074` (dentro de `run_onboard_mode`)

**Qué cambia**: Al guardar el YAML, escribir también la URL del hotel para que `v4complete` pueda encontrarlo después sin depender de slugs ni nombres.

**Formato YAML resultante**:

```yaml
hotel:
  nombre: Zi One Luxury
  url: https://zione.co/          # ← NUEVO: clave canónica de matching
  ubicacion: Pereira, Eje Cafetero
datos_operativos:
  habitaciones: 34
  reservas_mes: 800
  valor_reserva_cop: 290000
  canal_directo_pct: 40.0
metadatos:
  fuente: observations_tier_a
  fecha_captura: '2026-07-23T10:00:00+00:00'
  ...
```

**Implementación** (en `run_onboard_mode()`, antes de `form.save_yaml()`):

```python
# Asegurar que la URL quede persistida en el YAML como clave canónica
if args.url:
    data = form.to_dict()
    data.setdefault('hotel', {})['url'] = args.url.rstrip('/')
    # form.save_yaml() ya escribe data — o se pasa la URL al método save
```

**Por qué funciona para cualquier hotel**: `args.url` siempre está disponible en `onboard`. Zi One Luxury, Hotel Luxor, cualquier hotel — la URL se guarda sin ambigüedad.

---

#### CAMBIO B — `v4complete` pasa `output_dir` configurable al loader

**Archivo**: `main.py:1739` (dentro de `run_v4_complete_mode`)

**Qué cambia**: Dejar de hardcodear `output_dir` en el loader; en su lugar, pasar el directorio configurable desde el caller.

```python
# Antes (línea 1739):
onboarding_data = _load_latest_onboarding_data(args.url, hotel_name)

# Después:
clientes_dir = Path(args.output) / "clientes"
onboarding_data = _load_latest_onboarding_data(
    hotel_url=args.url,
    hotel_name=hotel_name,
    output_dir=clientes_dir,
)
```

**Firma actualizada de `_load_latest_onboarding_data`**:

```python
def _load_latest_onboarding_data(
    hotel_url: str,
    hotel_name: str,
    output_dir: Path | None = None,
) -> Dict[str, Any] | None:
```

**Por qué funciona con `--output` variable**:

| Comando | `--output` | `output_dir` pasado |
|---|---|---|
| `onboard --output ./prod` | `./prod` | Guarda en `./prod/clientes/` |
| `v4complete --output ./prod` | `./prod` | Busca en `./prod/clientes/` |
| `v4complete` (default) | `./output` | Busca en `./output/clientes/` |

---

#### CAMBIO C — `_load_latest_onboarding_data` busca por URL normalizada

**Archivo**: `main.py:3396-3445`

**Qué cambia**: Reemplazar la búsqueda por slug derivado con iteración por glob + matching determinístico de URL normalizada.

```python
def _load_latest_onboarding_data(
    hotel_url: str,
    hotel_name: str,
    output_dir: Path | None = None,
) -> Dict[str, Any] | None:
    """Carga datos de onboarding más recientes del hotel si existen.

    Matching determinístico por URL — sin depender de slugs, nombres ni fuzzy matching.
    """
    import yaml
    from datetime import datetime, timezone, timedelta

    output_dir = output_dir or Path("output/clientes")
    if not output_dir.exists():
        return None

    normalized_url = _normalize_url(hotel_url)

    for f in output_dir.glob("*_onboarding.yaml"):
        try:
            data = yaml.safe_load(f.read_text(encoding='utf-8'))
        except Exception:
            continue

        if not data or 'metadatos' not in data:
            continue

        # Matching canónico: URL normalizada
        yaml_url = (data.get('hotel', {}) or {}).get('url', '')
        if yaml_url and _normalize_url(yaml_url) == normalized_url:
            # URL coincide → validar frescura
            fecha_captura_str = data.get('metadatos', {}).get('fecha_captura')
            if not fecha_captura_str:
                continue

            fecha_captura = datetime.fromisoformat(fecha_captura_str.replace('Z', '+00:00'))
            if fecha_captura.tzinfo is None:
                fecha_captura = fecha_captura.replace(tzinfo=timezone.utc)

            # Fix 3 (BUG 2): ventana de frescura eliminada o configurable
            # El dato operativo no caduca — omitir check o usar env var
            return data

    return None


def _normalize_url(url: str) -> str:
    """Reduce https://www.zione.co/ → zione.co.

    Ignora protocolo, www, trailing slash, path y query string.
    """
    from urllib.parse import urlparse
    p = urlparse(url.rstrip('/'))
    return p.netloc.replace('www.', '').lower()
```

**Matriz de matching — garantizado para cualquier hotel**:

| Hotel | URL onboard | URL v4complete | `_normalize_url` | Match? |
|---|---|---|---|---|
| Zi One Luxury | `https://zione.co/` | `https://zione.co/` | `zione.co == zione.co` | ✅ |
| Con www | `https://www.hotel.com` | `https://hotel.com` | `hotel.com == hotel.com` | ✅ |
| Con path | `https://hotel.com/es` | `https://hotel.com/` | `hotel.com == hotel.com` | ✅ |
| Con query | `https://hotel.co?lang=es` | `https://hotel.co` | `hotel.co == hotel.co` | ✅ |
| HTTP | `http://simple-hotel.co` | `https://simple-hotel.co` | `simple-hotel.co == simple-hotel.co` | ✅ |
| Cualquier hotel | `https://{dominio}` | `https://{dominio}` | `{dominio} == {dominio}` | ✅ |

**No depende de**: nombre del hotel, slug derivado, dominio extraído, fuzzy matching, ni proximity string comparison.

---

### Fix 3 (independiente) — BUG 2: Eliminar ventana de frescura

```python
# Opción A (recomendada): Eliminar el check de frescura
# El dato operativo (habitaciones, ADR, canal) no se vuelve obsoleto.
# Si el hotel cambia de estructura, se re-onboardea y el nuevo archivo reemplaza al viejo.

# Opción B: Ventana amplia y configurable
FRESHNESS_HOURS = int(os.getenv("ONBOARDING_FRESHNESS_HOURS", "168"))  # 7 días
```

### Fix 4 (independiente) — §10a: Alinear ADRSource con EvidenceTier

```python
# En _determine_evidence_tier(), agregar "user_provided" a verified_sources:
verified_sources = [s for s in [adr_src, occ_src, ch_src]
                  if s in ('onboarding', 'verified', 'industry_standard_15pct', 'user_provided')]
```

### Fix 5 (independiente) — §10b: Actualizar mensaje de onboard

```python
# En run_onboard_mode(), reemplazar línea 1118:
print(f"   2. Ejecuta: python main.py v4complete --url {url_hint}")
```

### Fix 6 (independiente) — §10c: Integrar observations.json como fuente alternativa

```python
# En _load_latest_onboarding_data(), fallback a observations.json
# usando _normalize_url() como clave de matching:
obs_path = Path("data/hotel_observations/observations.json")
if obs_path.exists():
    obs_data = json.loads(obs_path.read_text(encoding='utf-8'))
    for obs in obs_data.get('observations', []):
        # Matching por URL si el observation tiene 'website' o campo similar
        obs_url = obs.get('website', '')
        if obs_url and _normalize_url(obs_url) == normalized_url:
            return _observation_to_onboarding_format(obs)
```

### Mapa de cobertura

| Bug | Resuelto por | Mecanismo |
|-----|-------------|-----------|
| B1 (slug mismatch) | Cambio A + C | URL como clave canónica; matching determinístico |
| B2 (24h freshness) | Fix 3 | Eliminar check o hacer configurable |
| N3 (hotel_url ignorado) | Cambio C | `hotel_url` se usa como clave primaria de matching |
| N4 (output_dir hardcodeado) | Cambio B | `output_dir` pasado como parámetro desde el caller |
| N5 (sin identity resolver) | Cambio A + C | URL es el identificador canónico; no se necesita resolver nombre |
| §10a (user_provided invisible) | Fix 4 | Agregar a `verified_sources` |
| §10b (audit deprecado sugerido) | Fix 5 | Actualizar mensaje a `v4complete` |
| §10c (observations.json no integrado) | Fix 6 | Fallback en `_load_latest_onboarding_data` |

---

## 13. Verificación post-implementación

Para validar que el diseño integrado funciona:

```bash
# 1. Verificar que onboard escribe hotel.url en el YAML
python main.py onboard --url https://zione.co/ --hotel-name "Zi One Luxury"
grep "url:" output/clientes/zi-one-luxury_onboarding.yaml
# Debe mostrar: url: https://zione.co

# 2. Verificar que v4complete encuentra el archivo por URL (no por slug)
python main.py v4complete --url https://zione.co/ --force-new

# 3. Verificar que financial_scenarios.json ahora tiene:
#    rooms=34, adr_cop=290000, occupancy_rate=0.7843, direct_channel_percentage=0.4

# 4. Verificar que 01_DIAGNOSTICO muestra:
#    financial_evidence_tier: "A"
#    financial_value_range incluye ~$7.1M-$20.8M (cifras Tier A)

# 5. Verificar con --output personalizado
python main.py onboard --url https://zione.co/ --output ./custom
python main.py v4complete --url https://zione.co/ --output ./custom --force-new
# Debe encontrar el YAML en ./custom/clientes/, no en ./output/clientes/

# 6. Verificar que el mensaje de onboard ya no sugiere "audit"
python main.py onboard --url https://zione.co/
# Debe sugerir: "python main.py v4complete --url https://zione.co/"
```

---

*Contexto original generado por validación de ejecución v4complete 2026-07-28.*
*Actualizado 2026-07-28 v2: validación exhaustiva contra código vivo. Corrección de §11. Adición de bugs N3, N4, N5. Auditoría de brecha de fuzzy matching en Fix 1+2 original.*
*Actualizado 2026-07-28 v3: rediseño integrado. Fix 1+2+5 originales reemplazados por diseño de 3 cambios atómicos (A: onboard escribe hotel.url, B: output_dir parametrizado, C: matching por URL normalizada). La URL es la clave canónica universal — sin slugs, sin nombres, sin fuzzy matching.*
*Para reanudar: cargar este contexto + `iah-cli-execution-conventions` + `iah-cli-v4complete-workflows`.*
