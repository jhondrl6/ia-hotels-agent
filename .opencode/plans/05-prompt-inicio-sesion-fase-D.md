# FASE-D: Conexión Scraper→ADR — Precio Web como Fuente de ADR

**ID**: FASE-D
**Objetivo**: Conectar el precio extraído por el scraper web (`precio_promedio`) como fuente intermedia de ADR, entre onboarding y benchmark regional. Agregar `WEB_SCRAPING` como valor al enum `ADRSource`.
**Dependencias**: FASE-A (data structures base)
**Duración estimada**: 1.5-2 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

El motor financiero obtiene el ADR (tarifa promedio diaria) de:
1. Onboarding form (`valor_reserva_cop`) — verificable
2. Benchmark regional (`avg_adr`) — estimado
3. Hardcode $300,000 (`LEGACY_DEFAULT_ADR`) — último recurso

El scraper YA extrae `precio_promedio` del HTML de la web del hotel (Schema priceRange, meta tags, regex). Pero el motor financiero NUNCA consulta este dato.

Para la narrativa de "hecho verificable", el ADR scrapeado fortalece la Capa 1:
> "Tarifa por noche: $280,000 (fuente: su página web, schema priceRange)"

### GAP A del archivo de investigación (Sección 14.1):
`hotel_data` es variable local en `cmd_v4complete()`. El bloque financiero ejecuta ~1000 líneas después pero AMBOS están en la misma función, así que `hotel_data` ya es accesible. **Confirmar en la implementación.**

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |
| FASE-B | ⬜ Pendiente (puede ejecutarse en paralelo) |
| FASE-C | ⬜ Pendiente (puede ejecutarse en paralelo) |

### Base Técnica Disponible
- `modules/scrapers/web_scraper.py` — extrae `precio_promedio` (líneas 54-99, 1027-1091)
- `modules/financial_engine/adr_resolution_wrapper.py` (279 líneas)
  - `ADRSource(Enum)` — REGIONAL_V410, LEGACY_HARDCODE, USER_PROVIDED
  - `ADRResolutionResult(dataclass)` — adr_cop, source, confidence, used_new_calculation, shadow_comparison, metadata
  - `ADRResolutionWrapper` — resolve() con RolloutMode
- `main.py:1526` — bloque donde se obtiene ADR para el motor financiero

---

## Tareas

### Tarea 1: Agregar `WEB_SCRAPING` a `ADRSource`

**Objetivo**: Extender el enum para incluir la nueva fuente.

**Archivo afectado**: `modules/financial_engine/adr_resolution_wrapper.py`

**Cambios**:
```python
class ADRSource(Enum):
    REGIONAL_V410 = "regional_v410"
    LEGACY_HARDCODE = "legacy_hardcode"
    USER_PROVIDED = "user_provided"
    WEB_SCRAPING = "web_scraping"      # NUEVO — precio extraído de la web del hotel
```

**Criterios de aceptación**:
- [ ] `ADRSource.WEB_SCRAPING` existe
- [ ] Tests existentes de ADR no se rompen

### Tarea 2: Modificar `ADRResolutionWrapper.resolve()` para aceptar web_scraping_adr

**Objetivo**: Agregar parámetro opcional y lógica de fallback.

**Archivo afectado**: `modules/financial_engine/adr_resolution_wrapper.py`

**Cambios en firma y lógica**:
```python
def resolve(self, region: str, rooms: int = None, user_provided_adr: float = None,
            hotel_id: str = None, hotel_name: str = None,
            web_scraping_adr: float = None) -> ADRResolutionResult:  # NUEVO parámetro
    """
    Cadena de fallback del ADR:
    1. user_provided_adr (onboarding) → ADRSource.USER_PROVIDED
    2. web_scraping_adr (scraper)     → ADRSource.WEB_SCRAPING  [NUEVO]
    3. regional benchmark             → ADRSource.REGIONAL_V410
    4. hardcode $300K                 → ADRSource.LEGACY_HARDCODE
    """
    # 1. User-provided (onboarding) — prioridad máxima
    if user_provided_adr and user_provided_adr > 0:
        return ADRResolutionResult(
            adr_cop=user_provided_adr,
            source=ADRSource.USER_PROVIDED.value,
            confidence="high",
            used_new_calculation=True,
            metadata={'fallback_chain': 'user_provided'}
        )
    
    # 2. Web scraping — NUEVO
    if web_scraping_adr and web_scraping_adr > 0:
        return ADRResolutionResult(
            adr_cop=web_scraping_adr,
            source=ADRSource.WEB_SCRAPING.value,
            confidence="medium",  # Medium porque es scraping, no dato declarado
            used_new_calculation=True,
            metadata={
                'fallback_chain': 'web_scraping',
                'note': 'Precio extraído de la página web del hotel'
            }
        )
    
    # 3-4. Existing logic (regional benchmark / legacy hardcode)
    # ... (código existente sin cambios)
```

**Criterios de aceptación**:
- [ ] `resolve()` acepta `web_scraping_adr` como parámetro opcional
- [ ] Si `user_provided_adr` existe, se usa ese (prioridad)
- [ ] Si no, y `web_scraping_adr` existe, se usa ese con confidence="medium"
- [ ] Si no, fallback a regional/legacy como antes
- [ ] `ADRResolutionResult.source` puede ser "web_scraping"

### Tarea 3: Conectar `hotel_data['precio_promedio']` en main.py

**Objetivo**: En el bloque financiero de `main.py`, pasar el precio scrapeado al resolver de ADR.

**Archivo afectado**: `main.py` (~línea 1526)

**Cambios**:
```python
# ANTES (línea ~1526):
adr_from_onboarding = datos_operativos.get('valor_reserva_cop')

# DESPUÉS:
adr_from_onboarding = datos_operativos.get('valor_reserva_cop')

# Extraer precio del scraping si está disponible
adr_from_scraping = None
if hotel_data and isinstance(hotel_data, dict):
    scraped_price = hotel_data.get('precio_promedio')
    if scraped_price and scraped_price > 0:
        adr_from_scraping = float(scraped_price)

# Pasar al resolver
adr_result = adr_wrapper.resolve(
    region=region,
    rooms=rooms,
    user_provided_adr=adr_from_onboarding,
    web_scraping_adr=adr_from_scraping,  # NUEVO
    hotel_id=hotel_id,
    hotel_name=hotel_name
)
```

**NOTA**: Verificar que `hotel_data` está en scope en el bloque financiero (ambos están dentro de `cmd_v4complete()`).

**Criterios de aceptación**:
- [ ] `hotel_data['precio_promedio']` se pasa al resolver
- [ ] El fallback chain funciona: onboarding > scraping > benchmark > hardcode
- [ ] Si `hotel_data` es None o no tiene precio, el código no crashea

### Tarea 4: Tests

**Archivo afectado**: `tests/financial_engine/test_adr_resolution_wrapper.py`

**Tests requeridos**:
```python
# 1. WEB_SCRAPING como fuente cuando no hay user_provided
def test_web_scraping_as_source():
    wrapper = ADRResolutionWrapper()
    result = wrapper.resolve(region="eje_cafetero", web_scraping_adr=280000)
    assert result.source == "web_scraping"
    assert result.confidence == "medium"

# 2. User-provided tiene prioridad sobre scraping
def test_user_provided_priority_over_scraping():
    wrapper = ADRResolutionWrapper()
    result = wrapper.resolve(region="eje_cafetero", 
                             user_provided_adr=300000, 
                             web_scraping_adr=280000)
    assert result.source == "user_provided"
    assert result.adr_cop == 300000

# 3. Fallback chain completa
def test_full_fallback_chain():
    wrapper = ADRResolutionWrapper()
    # Sin user_provided ni scraping → va a regional
    result = wrapper.resolve(region="eje_cafetero")
    assert result.source in ("regional_v410", "legacy_hardcode")

# 4. Scraping None no crashea
def test_scraping_none_no_crash():
    wrapper = ADRResolutionWrapper()
    result = wrapper.resolve(region="eje_cafetero", web_scraping_adr=None)
    # Debe caer a regional/legacy sin error
    assert result.adr_cop > 0

# 5. Scraping 0 no se usa
def test_scraping_zero_ignored():
    wrapper = ADRResolutionWrapper()
    result = wrapper.resolve(region="eje_cafetero", web_scraping_adr=0)
    assert result.source != "web_scraping"
```

**Criterios de aceptación**:
- [ ] 5 tests nuevos pasan
- [ ] Tests existentes de ADR pasan

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| test_web_scraping_as_source | `tests/financial_engine/test_adr_resolution_wrapper.py` | source = "web_scraping" |
| test_user_provided_priority_over_scraping | idem | source = "user_provided" |
| test_full_fallback_chain | idem | Funciona sin scraping ni user |
| test_scraping_none_no_crash | idem | No crashea |
| test_scraping_zero_ignored | idem | No usa scraping=0 |
| Suite completa | `tests/` | 0 failures |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/financial_engine/test_adr_resolution_wrapper.py -v
./venv/Scripts/python.exe -m pytest tests/ -x -q 2>&1 | tail -20
```

---

## Restricciones

- NO modificar ScenarioCalculator — eso es FASE-B
- NO modificar v4_diagnostic_generator — eso es FASE-C/F
- El parámetro `web_scraping_adr` es completamente opcional (default None)
- ADRResolutionResult.source existente ("regional_v410", "legacy_hardcode", "user_provided") no cambia
- Confidence de web_scraping es "medium" (no es dato declarado por el hotelero)

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** — Marcar FASE-D como ✅ Completada
2. **`06-checklist-implementacion.md`** — Marcar FASE-D
3. **`09-documentacion-post-proyecto.md`** — Sección A: ADRSource.WEB_SCRAPING
4. **Ejecutar**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-D \
    --desc "Scraper→ADR: precio web como fuente intermedia de ADR" \
    --archivos-mod "modules/financial_engine/adr_resolution_wrapper.py,main.py" \
    --tests "5"
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] `ADRSource.WEB_SCRAPING` existe en el enum
- [ ] `resolve()` acepta `web_scraping_adr` y lo prioriza correctamente
- [ ] `main.py` pasa `hotel_data['precio_promedio']` al resolver
- [ ] Fallback chain: onboarding > scraping > benchmark > hardcode
- [ ] 5 tests nuevos pasan
- [ ] Suite completa pasa
- [ ] `log_phase_completion.py` ejecutado
